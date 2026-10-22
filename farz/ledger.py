"""Check what the customer says against the mock ledger.

Outcomes:
  match       a transaction on the customer's wallet fits what they said
  mismatch    a transaction fits the reference or phone they gave, but not the amount
  not_found   they gave details and nothing on their wallet fits
  no_details  they gave no amount, phone or reference, so there is nothing to check

mismatch and not_found always send the ticket to a person: either the customer remembers it
wrong, or something happened that the ledger does not show (a cash deposit an agent never made).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def _twin(a: dict, b: dict) -> bool:
    """Same charge twice: same type, amount and counterparty within ten minutes."""
    if (a["type"], a["amount"], a["counterparty"]) != (b["type"], b["amount"], b["counterparty"]):
        return False
    gap = abs(datetime.fromisoformat(a["time"]) - datetime.fromisoformat(b["time"]))
    return gap.total_seconds() <= 600


class Ledger:
    def __init__(self, wallets: list[dict]):
        self.by_phone = {w["phone"]: w for w in wallets}

    @classmethod
    def load(cls, path: Path) -> "Ledger":
        return cls(json.loads(Path(path).read_text(encoding="utf-8"))["wallets"])

    def check(self, wallet_phone: str, amount: int | None, phone: str | None, reference: str | None) -> dict:
        wallet = self.by_phone.get(wallet_phone)
        if wallet is None:
            return {"outcome": "not_found", "txns": [], "why": "no wallet for this customer"}
        if amount is None and phone is None and reference is None:
            return {"outcome": "no_details", "txns": [], "why": "no amount, phone or reference in the ticket"}
        txns = wallet["transactions"]

        if reference:
            hit = [t for t in txns if t["ref"][-8:] == reference[-8:]]
            if not hit:
                return {"outcome": "not_found", "txns": [], "why": f"reference {reference} is not on this wallet"}
            t = hit[0]
            if amount is not None and t["amount"] != amount:
                return {"outcome": "mismatch", "txns": [t["ref"]],
                        "why": f"{t['ref']} is {t['amount']:,} IQD, customer says {amount:,}"}
            twins = [u["ref"] for u in txns if u is not t and _twin(u, t)]
            why = f"{t['ref']} {t['type']} {t['status']}" + (f", charged again as {', '.join(twins)}" if twins else "")
            return {"outcome": "match", "txns": [t["ref"], *twins], "why": why}

        if phone:
            to_phone = [t for t in txns if t["counterparty"] == phone]
            if amount is None:
                if to_phone:
                    return {"outcome": "match", "txns": [t["ref"] for t in to_phone], "why": f"transactions with {phone}"}
                return {"outcome": "not_found", "txns": [], "why": f"nothing with {phone} on this wallet"}
            exact = [t for t in to_phone if t["amount"] == amount]
            if exact:
                return {"outcome": "match", "txns": [t["ref"] for t in exact], "why": f"{amount:,} IQD with {phone}"}
            if to_phone:
                t = to_phone[-1]
                return {"outcome": "mismatch", "txns": [t["ref"]],
                        "why": f"{t['ref']} with {phone} is {t['amount']:,} IQD, customer says {amount:,}"}

        exact = [t for t in txns if t["amount"] == amount]
        if exact:
            return {"outcome": "match", "txns": [t["ref"] for t in exact], "why": f"{amount:,} IQD on this wallet"}
        if amount is None:
            return {"outcome": "not_found", "txns": [], "why": "nothing on this wallet fits"}
        why = f"no transaction of {amount:,} IQD on this wallet"
        # A hint for the agent, not an answer: the customer may remember the amount wrong.
        near = min(txns, key=lambda t: abs(t["amount"] - amount), default=None)
        if near and abs(near["amount"] - amount) <= 0.25 * amount:
            why += f"; closest is {near['ref']} {near['type']} {near['amount']:,} IQD"
        return {"outcome": "not_found", "txns": [], "why": why}
