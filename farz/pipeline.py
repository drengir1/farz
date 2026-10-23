"""Run a batch of tickets through Farz: decide, extract, check the ledger, gate, draft a reply.

  python -m farz.pipeline tickets.jsonl --decider local     # or --decider jev
  python -m farz.pipeline tickets.jsonl --decider jev --drafts astra --out routed.jsonl
  python -m farz.screen routed.jsonl                         # work the result on the agent screen

Each input line needs "id", "text" and "wallet_phone" (the logged-in customer's number).
Drafts default to the template writer; --drafts astra rewrites them with GPT-6 Astra, --drafts none skips them.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .extract import extract
from .gate import THRESHOLD, assess
from .ledger import Ledger
from .schema import MONEY_CATEGORIES, TEAMS

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "ledger.json"
LOCAL_MODEL = ROOT / "models" / "local.pkl"


def make_decider(name: str):
    from .deciders import JevDecider, LocalDecider
    if name == "jev":
        return JevDecider()
    if name == "local":
        return LocalDecider.load(LOCAL_MODEL)
    raise SystemExit(f"unknown decider {name}")


def route(tickets: list[dict], decider, ledger: Ledger, threshold: float = THRESHOLD) -> list[dict]:
    decisions = decider.decide([t["text"] for t in tickets])
    out = []
    for t, d in zip(tickets, decisions):
        entities = extract(t["text"])
        checked = None
        if d["category"]["choice"] in MONEY_CATEGORIES or any(entities.values()):
            checked = ledger.check(t.get("wallet_phone", ""), entities["amount"], entities["phone"], entities["reference"])
        gate = assess(t["text"], d, checked, threshold)
        out.append({
            "id": t["id"],
            "category": d["category"]["choice"], "category_confidence": round(d["category"]["confidence"], 4),
            "priority": d["priority"]["choice"], "priority_confidence": round(d["priority"]["confidence"], 4),
            "team": TEAMS.get(d["category"]["choice"]),
            "entities": entities, "ledger": checked,
            "route": "person" if gate["to_person"] else "team_queue", "reasons": gate["reasons"],
            "probabilities": {"category": d["category"]["probabilities"], "priority": d["priority"]["probabilities"]},
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tickets")
    ap.add_argument("--decider", default="local", choices=["local", "jev"])
    ap.add_argument("--threshold", type=float, default=THRESHOLD)
    ap.add_argument("--drafts", default="template", choices=["template", "astra", "none"])
    ap.add_argument("--out")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    tickets = [json.loads(line) for line in Path(args.tickets).read_text(encoding="utf-8").splitlines() if line.strip()]
    ledger = Ledger.load(LEDGER)
    rows = route(tickets, make_decider(args.decider), ledger, args.threshold)
    if args.drafts != "none":
        from .drafts import draft_all
        rows = draft_all(rows, tickets, ledger, args.drafts)
    # Keep the message and wallet beside each result so the agent screen can show them.
    rows = [{**r, "text": t["text"], "wallet_phone": t.get("wallet_phone", "")} for r, t in zip(rows, tickets)]
    text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
