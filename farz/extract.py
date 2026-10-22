"""Pull the amount, phone number and transaction reference out of a ticket. Plain rules, no model.

Customers write amounts many ways: 580 ألف, 455k, 1,525,000, ٧٥ الف, مليون ونص, نص مليون,
290000 دينار, 12 alf. Phones come as 0780 056 9588, +964 788 010 5164, 9647880105164 or in
Arabic digits. References as ZC-12345678, zc12345678 or the bare 8 digits.

Phones and references are found first and cut out of the text, so their digits are never
read as an amount.
"""

from __future__ import annotations

import re

from .normalize import digits

_PHONE = re.compile(r"(?<!\d)(?:\+?\s?964[\s-]?|0)(7[3-9]\d)[\s-]?(\d{3})[\s-]?(\d{4})(?!\d)")
_REF = re.compile(r"(?i)(?<![a-z0-9])zc-?\s?(\d{8})(?!\d)|(?<![\d,.])(\d{8})(?![\d,.])")

_THOUSAND = r"(?:الف|ألف|آلاف|الاف|ألاف|alf|alaf|k|K|thousand|grand)"
_MILLION = r"(?:مليون|ملايين|million|malyoon|melyoon|milyon)"
_HALF = r"(?:\s*و\s*نص|\s*ونص|\s*and a half|\s*w ?nus|\s*w ?nu9)"
_NUM = r"(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)"

_RULES = [
    (re.compile(_NUM + r"\s*" + _MILLION + "(" + _HALF + ")?", re.I), 1_000_000),
    (re.compile(_NUM + r"\s*" + _THOUSAND + r"(?![a-zء-ي])", re.I), 1_000),
    (re.compile(_NUM + r"\s*(?:دينار|دنانير|IQD|dinars?|د\.ع)", re.I), 1),
    (re.compile(r"(?<![\d.])(\d{1,3}(?:,\d{3})+)(?![\d,])"), 1),
]

_WORDS = [
    (r"مليونين\s*و\s*نص|مليونين\s*ونص", 2_500_000),
    (r"مليونين", 2_000_000),
    (r"مليون\s*و\s*نص|مليون\s*ونص", 1_500_000),
    (r"ربع\s*مليون", 250_000),
    (r"نص\s*مليون|نصف\s*مليون", 500_000),
    (r"سبعمية\s*و\s*خمسين\s*(?:الف|ألف)|سبعمية\s*وخمسين\s*(?:الف|ألف)", 750_000),
    (r"(?<![؀-ۿ])مليون(?![؀-ۿ])", 1_000_000),
]


def _phone(text: str) -> tuple[str | None, str]:
    m = _PHONE.search(text)
    if not m:
        return None, text
    number = "0" + "".join(m.groups())
    return number, text[:m.start()] + " " + text[m.end():]


def _ref(text: str) -> tuple[str | None, str]:
    m = _REF.search(text)
    if not m:
        return None, text
    return "ZC-" + (m.group(1) or m.group(2)), text[:m.start()] + " " + text[m.end():]


def _amount(text: str) -> int | None:
    hits = []
    for rx, mult in _RULES:
        for m in rx.finditer(text):
            value = float(m.group(1).replace(",", "")) * mult
            if mult == 1_000_000 and m.lastindex and m.lastindex >= 2 and m.group(2):
                value += 500_000
            hits.append((m.start(), int(round(value)), m.end()))
    for pattern, value in _WORDS:
        for m in re.finditer(pattern, text):
            if not any(s <= m.start() < e for s, _, e in hits):
                hits.append((m.start(), value, m.end()))
    hits = [h for h in hits if h[1] >= 250]
    if not hits:
        return None
    # The first stated amount is the one the ticket is about; later ones are usually repeats.
    hits.sort()
    kept = []
    for h in hits:
        if not any(k[0] <= h[0] < k[2] for k in kept):
            kept.append(h)
    return kept[0][1]


def extract(text: str) -> dict:
    t = digits(text)
    phone, t = _phone(t)
    ref, t = _ref(t)
    return {"amount": _amount(t), "phone": phone, "reference": ref}
