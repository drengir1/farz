"""Turn an agent's choices on the screen into the draft score: send as is, edit, or rewrite.

    python -m farz.screen --actions runs/rating-dev.jsonl     # a person works the queue
    python eval/rate.py runs/rating-dev.jsonl                 # then count what they did

On the screen, approving a draft is "send as is", approving after an edit is "edit", and taking
the ticket over is "rewrite". An edit that changed nothing counts as send as is. For edits, the
share of the draft that was kept shows how big the change was. Only the last choice per ticket
counts. Writes eval/results/rating-<file name>.json next to the other results.
"""

from __future__ import annotations

import argparse
import collections
import difflib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "eval" / "results"
VERDICT = {"approve": "send", "edit": "edit", "take_over": "rewrite"}


def verdict(action: dict) -> str:
    if action["choice"] == "edit" and not action.get("changed"):
        return "send"
    return VERDICT[action["choice"]]


def kept(action: dict) -> float | None:
    """How much of the draft survived an edit, 0 to 1."""
    if verdict(action) != "edit":
        return None
    return round(difflib.SequenceMatcher(None, action.get("draft") or "", action.get("sent_text") or "").ratio(), 3)


def summarise(actions: list[dict]) -> dict:
    last = {}
    for a in actions:
        last[a["id"]] = a
    rows = list(last.values())

    def counts(group: list[dict]) -> dict:
        c = collections.Counter(verdict(a) for a in group)
        n = len(group)
        return {"tickets": n, **{v: c.get(v, 0) for v in ("send", "edit", "rewrite")},
                "send_share": round(c.get("send", 0) / n, 4) if n else None}

    edits = [k for k in map(kept, rows) if k is not None]
    by = lambda key: {k: counts([a for a in rows if a.get(key) == k])
                      for k in sorted({a.get(key) for a in rows}, key=str)}
    return {"all": counts(rows), "kept_in_edits_median": sorted(edits)[len(edits) // 2] if edits else None,
            "by_writer": by("draft_writer"), "by_route": by("route"), "by_category": by("category")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("actions", help="the screen's actions file")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    path = Path(args.actions)
    actions = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    summary = {"from": path.name, **summarise(actions)}
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / f"rating-{path.stem}.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1),
                                                      encoding="utf-8", newline="\n")
    a = summary["all"]
    print(f"{a['tickets']} drafts: {a['send']} send as is, {a['edit']} edited, {a['rewrite']} rewritten "
          f"({a['send_share']:.0%} sent untouched)" if a["tickets"] else "no choices yet")
    if summary["kept_in_edits_median"] is not None:
        print(f"edits kept {summary['kept_in_edits_median']:.0%} of the draft (median)")
    for name in ("by_writer", "by_route"):
        for k, c in summary[name].items():
            print(f"  {name[3:]} {k}: {c['send']}/{c['tickets']} send, {c['edit']} edit, {c['rewrite']} rewrite")


if __name__ == "__main__":
    main()
