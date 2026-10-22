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
    """Character n-gram TF-IDF and logistic regression, one model per question.

    Character n-grams cope with the three scripts we see (Arabic, Latin Arabizi, English),
    with typos, and with Iraqi spellings, without a tokenizer or any download.
    """

    name = "local"

    def __init__(self, models: dict | None = None):
        self.models = models or {}

    @staticmethod
    def _pipeline():
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        return make_pipeline(
            TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1, sublinear_tf=True, max_features=60000),
            LogisticRegression(C=8.0, max_iter=3000, class_weight="balanced"),
        )

    def fit(self, texts: list[str], labels: dict[str, list[str]]) -> "LocalDecider":
        from .normalize import normalize
        clean = [normalize(t) for t in texts]
        for q, y in labels.items():
            self.models[q] = self._pipeline().fit(clean, y)
        return self

    def decide(self, texts: list[str]) -> list[dict]:
        from .normalize import normalize
        clean = [normalize(t) for t in texts]
        per_q = {}
        for q, model in self.models.items():
            classes = list(model.classes_)
            per_q[q] = [dict(zip(classes, map(float, row))) for row in model.predict_proba(clean)]
        options = {"category": CATEGORIES, "priority": PRIORITIES}
        out = []
        for i in range(len(texts)):
            row = {}
            for q, probs_list in per_q.items():
                probs = {o: probs_list[i].get(o, 0.0) for o in options[q]}
                row[q] = decision(probs)
            out.append(row)
        return out

    def save(self, path: Path):
        path.write_bytes(pickle.dumps(self.models))

    @classmethod
    def load(cls, path: Path) -> "LocalDecider":
        return cls(pickle.loads(path.read_bytes()))
