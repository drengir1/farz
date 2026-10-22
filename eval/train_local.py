"""Train our local decider on the dev tickets only and save it.

Before the final fit, a 5-fold cross-validation on dev shows how well it does on tickets it
has not seen from the same writers. The held-out file is never opened here.

    python eval/train_local.py            # cross-validate, fit on all of dev, save models/local.pkl
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from sklearn.model_selection import StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from farz.deciders import LocalDecider  # noqa: E402

MODEL = ROOT / "models" / "local.pkl"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def labels(rows: list[dict]) -> dict[str, list[str]]:
    return {"category": [r["gold"]["category"] for r in rows], "priority": [r["gold"]["priority"] for r in rows]}


def cross_validate(rows: list[dict], folds: int = 5, seed: int = 20261023) -> dict[str, float]:
    texts, y = [r["text"] for r in rows], labels(rows)
    right = {"category": 0, "priority": 0}
    split = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    for train, test in split.split(texts, y["category"]):
        model = LocalDecider().fit([texts[i] for i in train], {q: [v[i] for i in train] for q, v in y.items()})
        for i, d in zip(test, model.decide([texts[i] for i in test])):
            for q in right:
                right[q] += d[q]["choice"] == y[q][i]
    return {q: n / len(rows) for q, n in right.items()}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    dev = load_jsonl(ROOT / "data" / "dev.jsonl")
    cv = cross_validate(dev)
    print(f"5-fold on dev ({len(dev)}): category {cv['category']:.1%}, priority {cv['priority']:.1%}")
    model = LocalDecider().fit([r["text"] for r in dev], labels(dev))
    MODEL.parent.mkdir(exist_ok=True)
    model.save(MODEL)
    print(f"saved {MODEL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
