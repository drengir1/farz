"""Where the deciders go wrong, from the saved runs on dev and probe.

    python eval/failures.py

Counts which category gets mistaken for which, whether wrong priorities are too low or too
high, and lists the tickets that reached a team queue with a wrong answer: those are the
mistakes a person would not catch at the gate. Held-out is left out on purpose so nobody
studies its mistakes and tunes on them. Writes eval/results/failures.json.
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.run import RESULTS, load_set  # noqa: E402

LEVEL = {"low": 0, "normal": 1, "high": 2, "urgent": 3}


def failures(routed: list[dict], gold: list[dict], top: int = 6) -> dict:
    confused = collections.Counter()
    too_low = collections.Counter()
    too_high = collections.Counter()
    slipped = []
    for r, g in zip(routed, gold):
        cat_ok = r["category"] == g["category"]
        pri_ok = r["priority"] == g["priority"]
        if not cat_ok:
            confused[(g["category"], r["category"])] += 1
        if not pri_ok:
            (too_low if LEVEL[r["priority"]] < LEVEL[g["priority"]] else too_high)[g["priority"] + " as " + r["priority"]] += 1
        if r["route"] == "team_queue" and not (cat_ok and pri_ok):
            slipped.append({"id": r["id"], "right": [g["category"], g["priority"]],
                            "said": [r["category"], r["priority"]]})
    return {"tickets": len(routed),
            "category_wrong": sum(confused.values()),
            "confused": [{"is": a, "said": b, "tickets": n} for (a, b), n in confused.most_common(top)],
            "priority_too_low": sum(too_low.values()), "priority_too_high": sum(too_high.values()),
            "too_low": dict(too_low.most_common(top)),
            "queued_but_wrong": slipped}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = {}
    for s in ("dev", "probe"):
        gold = [t["gold"] for t in load_set(s)]
        for decider in ("jev", "local"):
            path = RESULTS / f"{s}-{decider}.json"
            if not path.exists():
                continue
            f = failures(json.loads(path.read_text(encoding="utf-8"))["routed"], gold)
            out[f"{s}-{decider}"] = f
            print(f"\n{s}-{decider}: {f['category_wrong']}/{f['tickets']} category wrong, priority "
                  f"{f['priority_too_low']} too low and {f['priority_too_high']} too high, "
                  f"{len(f['queued_but_wrong'])} wrong but sent to a team queue")
            for c in f["confused"]:
                print(f"   {c['is']} taken as {c['said']}: {c['tickets']}")
            for k, n in f["too_low"].items():
                print(f"   priority {k}: {n}")
            for q in f["queued_but_wrong"]:
                print(f"   queued wrong {q['id']}: is {'/'.join(q['right'])}, said {'/'.join(q['said'])}")
    (RESULTS / "failures.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
