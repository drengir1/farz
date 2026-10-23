"""Draft replies for a scored ticket set and count what the draft check finds.

    python eval/drafts.py --set dev --writer template
    python eval/drafts.py --set dev --writer astra            # one Codex call per 12 tickets

Reuses the routed rows from eval/results/<set>-jev.json, so Jev is not asked again. Writes
eval/results/drafts-<set>-<writer>.json. A machine check is not a quality score: the drafts still
need a person to rate them send, edit or rewrite (eval/rate.py).
Never run on the held-out set: its drafts are rated once, with everything else, at the end.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.run import RESULTS, load_set  # noqa: E402
from farz.drafts import draft_all  # noqa: E402
from farz.ledger import Ledger  # noqa: E402
from farz.pipeline import LEDGER  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="dev", choices=["dev"])
    ap.add_argument("--writer", default="template", choices=["template", "astra"])
    ap.add_argument("--decider", default="jev", choices=["jev", "local"])
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    tickets = load_set(args.set)
    routed = json.loads((RESULTS / f"{args.set}-{args.decider}.json").read_text(encoding="utf-8"))["routed"]
    started = time.perf_counter()
    rows = draft_all(routed, tickets, Ledger.load(LEDGER), args.writer)
    seconds = time.perf_counter() - started

    flagged = [r for r in rows if r["draft_problems"]]
    rejected = [r for r in rows if r.get("astra_rejected")]
    reasons = collections.Counter(p.split(" is not")[0].split(",")[0] if p.startswith("number") else p
                                  for r in rejected for p in r["astra_rejected"]["problems"])
    summary = {"set": args.set, "writer": args.writer, "decider": args.decider, "tickets": len(rows),
               "written_by": dict(collections.Counter(r["draft_writer"] for r in rows)),
               "drafts_flagged": len(flagged), "astra_drafts_rejected": len(rejected),
               "astra_rejection_reasons": dict(reasons), "seconds": round(seconds, 1),
               "date": time.strftime("%Y-%m-%d %H:%M")}
    keep = ("id", "category", "team", "route", "reply_language", "draft", "draft_writer", "draft_problems",
            "astra_rejected")
    out = RESULTS / f"drafts-{args.set}-{args.writer}.json"
    out.write_text(json.dumps({**summary, "drafts": [{k: r.get(k) for k in keep} for r in rows]},
                              ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
