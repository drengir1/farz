"""Two deciders behind one interface, so the pipeline and the scorer treat them the same.

A decider takes ticket texts and returns, for each ticket and each question (category, priority),
the chosen option, a confidence, and the probability of every option.

- JevDecider: TypeSafe's Jev, zero-shot, the same questions the 23 Sep probe used.
- LocalDecider: our own model, trained on the dev tickets only, runs on a laptop with no network.
"""

from __future__ import annotations

import pickle
from pathlib import Path

from .schema import CATEGORIES, CONTEXT, PRIORITIES

QUESTIONS = {
    "category": {"type": "choice", "instructions": "Which support category does this ticket belong to?",
                 "criteria": CATEGORIES},
    "priority": {"type": "choice", "instructions": "How urgently should the support team handle this ticket?",
                 "criteria": PRIORITIES},
}


def decision(probs: dict[str, float]) -> dict:
    choice = max(probs, key=probs.get)
    return {"choice": choice, "confidence": probs[choice], "probabilities": probs}


class JevDecider:
    name = "jev"

    def __init__(self, jev=None):
        from .jev import Jev
        self.jev = jev or Jev()
        self.jev.warm()
        self.last_meta: list[dict] = []

    def decide(self, texts: list[str]) -> list[dict]:
        from .jev import cost
        out, self.last_meta = [], []
        for text in texts:
            response, ms = self.jev.ask(CONTEXT + text, QUESTIONS)
            answers = response.get("answers") or {}
            row = {}
            for q, options in (("category", CATEGORIES), ("priority", PRIORITIES)):
                a = answers.get(q) or {}
                probs = {o: float((a.get("probabilities") or {}).get(o, 0.0)) for o in options}
                if a.get("choice") in options:
                    row[q] = {"choice": a["choice"], "confidence": float(a.get("confidence") or 0.0),
                              "probabilities": probs}
                else:
                    row[q] = {"choice": None, "confidence": 0.0, "probabilities": probs}
            tokens, usd = cost(response)
            self.last_meta.append({"ms": ms, "tokens": tokens, "usd": usd})
            out.append(row)
        return out


class LocalDecider:
    """Our own model: two open multilingual sentence encoders plus character and word patterns.

    For each question, the average of two probability guesses:
      - logistic regression on the sentences as vectors, from intfloat/multilingual-e5-base and
        sentence-transformers/paraphrase-multilingual-mpnet-base-v2 side by side (both open, MIT and
        Apache 2.0). They place tickets that mean the same thing near each other, whatever the wording.
      - a calibrated linear SVM on character 2-5 grams and word 1-2 grams, which copes with Arabic,
        Arabizi and English, typos and Iraqi spellings.
    The encoders are downloaded once (about 2 GB) and then run on the laptop's CPU with no network.
    Chosen by 5-fold cross-validation on dev only; eval/README.md lists what else was tried.
    """

    name = "local"
    ENCODERS = (("intfloat/multilingual-e5-base", "query: "),
                ("sentence-transformers/paraphrase-multilingual-mpnet-base-v2", ""))
    _encoders: dict = {}
    _vectors: dict = {}

    def __init__(self, models: dict | None = None):
        self.models = models or {}

    @classmethod
    def encode(cls, texts: list[str]):
        """Sentence vectors, kept in memory so cross-validation encodes each ticket once."""
        import numpy as np
        todo = [t for t in dict.fromkeys(texts) if t not in cls._vectors]
        if todo:
            parts = []
            for name, prefix in cls.ENCODERS:
                if name not in cls._encoders:
                    from sentence_transformers import SentenceTransformer
                    cls._encoders[name] = SentenceTransformer(name, device="cpu")
                parts.append(cls._encoders[name].encode([prefix + t for t in todo], normalize_embeddings=True,
                                                        batch_size=16))
            for t, v in zip(todo, np.hstack(parts)):
                cls._vectors[t] = v
        return np.vstack([cls._vectors[t] for t in texts])

    @staticmethod
    def _patterns():
        from sklearn.calibration import CalibratedClassifierCV
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.pipeline import make_pipeline, make_union
        from sklearn.svm import LinearSVC
        return make_pipeline(
            make_union(TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True),
                       TfidfVectorizer(analyzer="word", ngram_range=(1, 2), sublinear_tf=True)),
            CalibratedClassifierCV(LinearSVC(C=0.5, class_weight="balanced"), cv=3),
        )

    @staticmethod
    def _meaning():
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression(C=16.0, max_iter=5000, class_weight="balanced")

    def fit(self, texts: list[str], labels: dict[str, list[str]]) -> "LocalDecider":
        from .normalize import digits
        clean = [digits(t) for t in texts]
        vectors = self.encode(clean)
        for q, y in labels.items():
            self.models[q] = {"patterns": self._patterns().fit(clean, y), "meaning": self._meaning().fit(vectors, y)}
        return self

    def decide(self, texts: list[str]) -> list[dict]:
        from .normalize import digits
        clean = [digits(t) for t in texts]
        vectors = self.encode(clean)
        options = {"category": CATEGORIES, "priority": PRIORITIES}
        per_q = {}
        for q, m in self.models.items():
            a = [dict(zip(m["patterns"].classes_, map(float, r))) for r in m["patterns"].predict_proba(clean)]
            b = [dict(zip(m["meaning"].classes_, map(float, r))) for r in m["meaning"].predict_proba(vectors)]
            per_q[q] = [{o: (x.get(o, 0.0) + y.get(o, 0.0)) / 2 for o in options[q]} for x, y in zip(a, b)]
        return [{q: decision(per_q[q][i]) for q in per_q} for i in range(len(texts))]

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pickle.dumps(self.models))

    @classmethod
    def load(cls, path: Path) -> "LocalDecider":
        return cls(pickle.loads(path.read_bytes()))
