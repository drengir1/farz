"""Light text normalisation shared by the extractor and the local model.

Arabic customers write the same letter several ways (أ إ آ ا, ى ي, ة ه) and mix Arabic-Indic
and Western digits. Folding these makes the same word look the same.
"""

import re

AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
_FOLD = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي", "ة": "ه", "ـ": None, "‏": None, "‎": None})
_DIACRITICS = re.compile(r"[ً-ْٰ]")


def digits(text: str) -> str:
    return text.translate(AR_DIGITS).replace("٬", ",").replace("،", "، ")


def normalize(text: str) -> str:
    text = _DIACRITICS.sub("", digits(text)).translate(_FOLD).lower()
    return re.sub(r"\s+", " ", text).strip()
