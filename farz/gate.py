"""Decide whether a ticket can go to a team queue with a draft, or must go to a person first.

A ticket goes to a person when any of these hold:
- the decider is not sure of the category or the priority (below the threshold)
- the category is fraud_scam, or the priority is urgent
- the text has scam signs (codes given away, calls claiming to be the company, prizes, hacking)
- the text tries to instruct the system (ignore your rules, refund now, reveal who received)
- the ledger check found a mismatch, or nothing that fits

Each reason is kept, so the agent sees why the ticket reached them.
"""

from __future__ import annotations

import re

from .normalize import normalize

THRESHOLD = 0.90

# Written once from what scams look like, not tuned on the tickets. Matched on normalised text
# (alef, yaa and taa marbuta folded, lower case), so the Arabic is written in that folded form.
SCAM = re.compile("|".join([
    r"احتيال", r"نصب", r"نصاب", r"اخترق", r"مخترق", r"مهكر", r"هكر", r"انسرق", r"سرقو", r"سرقه",
    r"انطيته الكود", r"انطيته الرمز", r"عطيته الكود", r"اعطيته الكود", r"دزيتله الكود", r"گلتله الكود",
    r"(?:اتصل|اتصلو|خابرني|خابروني).{0,40}(?:زين ?كاش|الشركه|موظف)", r"(?:ربحت|فزت|جائزه|جايزه)",
    r"ما سويتها|مو انا|ما اعرف عنها|ما مسويها|بدون علمي",
    r"\bscam", r"\bfraud", r"\bhack", r"\bstole", r"\bprize\b", r"\bwon\b", r"gave (?:him|them|her) the (?:code|otp)",
    r"\bnot me\b", r"didn'?t make", r"did not make", r"blocked me",
    r"\bnasab", r"\bin9ara8", r"\bhacker", r"\bkhtra8", r"ma sawetha", r"mo ani",
]))

INJECTION = re.compile("|".join([
    r"ignore (?:your|all|the) (?:rules|instructions)", r"\bsystem\b.{0,30}(?:ignore|mark|refund|send|reveal|show)",
    r"supervisor", r"as (?:a|the) (?:zaincash|support) (?:manager|supervisor|admin)",
    r"تجاهل", r"قواعدك", r"يا نظام", r"نظام الدعم", r"(?:مشرف|مدير) (?:من|ب)?\s?زين ?كاش", r"بصفتي",
    r"(?:طلعلي|اعطيني|انطيني|گلي|كلي) (?:اسم|رقم) (?:الشخص|اللي|الي)",
    r"ya system", r"ya nitham", r"tajahal", r"ignore",
]))


def assess(text: str, decision: dict, ledger: dict | None, threshold: float = THRESHOLD) -> dict:
    t = normalize(text)
    reasons = []
    cat, pri = decision["category"], decision["priority"]
    if cat["choice"] is None or cat["confidence"] < threshold:
        reasons.append(f"not sure of category ({cat['choice']} {cat['confidence']:.2f})")
    if pri["choice"] is None or pri["confidence"] < threshold:
        reasons.append(f"not sure of priority ({pri['choice']} {pri['confidence']:.2f})")
    if cat["choice"] == "fraud_scam":
        reasons.append("fraud or scam")
    if pri["choice"] == "urgent":
        reasons.append("urgent")
    if SCAM.search(t):
        reasons.append("scam signs in the text")
    if INJECTION.search(t):
        reasons.append("text tries to instruct the system")
    if ledger and ledger["outcome"] in ("mismatch", "not_found"):
        reasons.append(f"ledger: {ledger['why']}")
    return {"to_person": bool(reasons), "reasons": reasons}
