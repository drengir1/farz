"""Shakir's Iraqi Arabic word list, the corrections a native speaker made to our copy.

Every Iraqi Arabic line Farz writes is checked against it, the same way the synthetic tickets were.
The master list lives with the rest of his copy rules; this is the part that applies to support replies.
"""

from __future__ import annotations

import re

# wrong -> right
WORD_FIXES = {"مسدود": "معزل", "مسدودين": "معزلين", "فاتحين": "مفتحين", "ورينا": "شوفنا", "ورّينا": "شوفنا",
              "نوريك": "نشوفك", "نورّيك": "نشوفك", "زباين": "زبائن", "ينبلغ": "يتبلغ"}
# Not words: the line has to be rewritten.
BANNED = ["حچاك", "حجاك"]


def word_problems(text: str) -> list[str]:
    problems = []
    for wrong in list(WORD_FIXES) + BANNED:
        if re.search(rf"(?<![؀-ۿ]){wrong}(?![؀-ۿ])", text):
            fix = WORD_FIXES.get(wrong)
            problems.append(f"word {wrong}" + (f", write {fix}" if fix else ", rewrite the line"))
    if re.search(r"شكد(?!\s*سعر)", text):
        problems.append("شكد without سعر")
    return problems
