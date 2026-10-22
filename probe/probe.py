"""One-shot probe: can Jev classify Iraqi-dialect wallet support tickets, and does its confidence mean anything?

Questions are written once and not tuned on these tickets. Reuses the Jev client from the
sudoshaker reel 06 assistant (kept-open connection; the key is loaded there and never printed).
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "D:/sudoshaker/reels/06-jev/assistant")
from jev_assistant.jev import Jev, cost  # noqa: E402

HERE = Path(__file__).parent

CONTEXT = (
    "A customer of an Iraqi mobile wallet (like ZainCash) sent this support ticket. "
    "Tickets are usually in Iraqi Arabic dialect, sometimes English or Arabic written in Latin letters. "
    "Ticket: "
)

CATEGORIES = {
    "failed_transfer": "A wallet-to-wallet or international transfer failed, is stuck pending, was deducted but not received, or was deducted twice.",
    "wrong_recipient": "The customer sent money to the wrong number or wrong person by mistake and wants it back.",
    "login_access": "Cannot log in: OTP code not arriving, forgotten PIN, locked after attempts, new phone, lost SIM, app stuck at login.",
    "agent_dispute": "A problem with a cash-in/cash-out agent (وكيل): extra fees, cash deposit not credited, short cash-out, agent refused or did not do what was paid for.",
    "card_issue": "A problem with the wallet's payment card (Mastercard, virtual card): declined, not delivered, lost, expired, ATM, double card charge.",
    "bill_payment": "A bill, top-up, subscription, installment or purchase paid through the app that was not applied, or a question about where to pay a bill.",
    "fraud_scam": "Scam, social engineering, hacked account, unauthorized transactions, suspicious OTP codes or messages, being cheated by a seller.",
    "account_kyc": "Account verification, limits, updating ID, correcting the name, suspended account, closing the account, opening a merchant account.",
    "general_inquiry": "A general question about fees, services, branches or opening hours, app performance, unexplained small charges, or thanks and feedback.",
}

PRIORITIES = {
    "urgent": "Money is actively at risk right now: account compromised, money stolen by a scammer, lost card that must be blocked immediately.",
    "high": "The customer has lost money or money is stuck or missing, but there is no ongoing attack.",
    "normal": "A service is not working for the customer, but no money is lost or stuck.",
    "low": "A question, a request for information, a routine account change, or feedback.",
}

QUESTIONS = {
    "category": {
        "type": "choice",
        "instructions": "Which support category does this ticket belong to?",
        "criteria": CATEGORIES,
    },
    "priority": {
        "type": "choice",
        "instructions": "How urgently should the support team handle this ticket?",
        "criteria": PRIORITIES,
    },
}


def main():
    tickets = json.loads((HERE / "tickets.json").read_text(encoding="utf-8"))
    jev = Jev()
    warm_ms = jev.warm()
    rows = []
    started = time.perf_counter()
    for t in tickets:
        response, ms = jev.ask(CONTEXT + t["text"], QUESTIONS)
        answers = response.get("answers") or {}
        tokens, usd = cost(response)
        row = {"id": t["id"], "ms": round(ms), "tokens": tokens, "usd": usd}
        for q in ("category", "priority"):
            a = answers.get(q) or {}
            row[q] = {"gold": t[q], "pred": a.get("choice"), "conf": a.get("confidence"),
                      "probs": a.get("probabilities")}
        rows.append(row)
    wall = time.perf_counter() - started
    jev.stop()
    (HERE / "results.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")

    n = len(rows)
    print(f"tickets {n} | warm {warm_ms:.0f} ms | wall {wall:.1f} s | "
          f"median {sorted(r['ms'] for r in rows)[n // 2]} ms | "
          f"tokens/ticket {sum(r['tokens'] for r in rows) / n:.0f} | "
          f"total ${sum(r['usd'] for r in rows):.5f}")
    for q in ("category", "priority"):
        right = [r[q]["pred"] == r[q]["gold"] for r in rows]
        print(f"\n== {q}: {sum(right)}/{n} = {sum(right) / n:.1%}")
        bins = defaultdict(lambda: [0, 0])
        for r, ok in zip(rows, right):
            c = r[q]["conf"] or 0.0
            b = "0.95+" if c >= 0.95 else "0.80-0.95" if c >= 0.8 else "0.60-0.80" if c >= 0.6 else "<0.60"
            bins[b][0] += ok
            bins[b][1] += 1
        for b in ("0.95+", "0.80-0.95", "0.60-0.80", "<0.60"):
            if bins[b][1]:
                print(f"  conf {b:>9}: {bins[b][0]}/{bins[b][1]} right")
        for th in (0.6, 0.8, 0.9):
            kept = [(r, ok) for r, ok in zip(rows, right) if (r[q]["conf"] or 0) >= th]
            if kept:
                acc = sum(ok for _, ok in kept) / len(kept)
                print(f"  auto-route at conf>={th}: {len(kept)}/{n} kept, {acc:.1%} right, {n - len(kept)} escalated")
        errors = Counter((r[q]["gold"], r[q]["pred"]) for r, ok in zip(rows, right) if not ok)
        for (g, p), k in errors.most_common():
            print(f"  miss x{k}: gold {g} -> pred {p}")
        for r, ok in zip(rows, right):
            if not ok:
                print(f"    {r['id']}: {r[q]['pred']} @ {r[q]['conf']}")


if __name__ == "__main__":
    main()
