import pytest

from farz.extract import extract


@pytest.mark.parametrize("text, amount", [
    ("دزيت 580 ألف لأخوي", 580_000),
    ("حولت ١٢٥ الف وما وصلت", 125_000),
    ("انخصم 1,525,000 من رصيدي", 1_525_000),
    ("sent 455k yesterday", 455_000),
    ("deducted 940,000 IQD", 940_000),
    ("دفعت 75 ألف، وانخصمت مرتين", 75_000),
    ("حولت مليون ونص لأهلي", 1_500_000),
    ("دزيت نص مليون", 500_000),
    ("ربع مليون راحت", 250_000),
    ("2 مليون ونص للأردن", 2_500_000),
    ("انخصم 290000 دينار", 290_000),
    ("dazet 12 alf", 12_000),
    ("صارلي 3 ايام انتظر", None),
])
def test_amounts(text, amount):
    assert extract(text)["amount"] == amount


@pytest.mark.parametrize("text, phone", [
    ("للرقم 07805579410 بالغلط", "07805579410"),
    ("to 0780 056 9588", "07800569588"),
    ("+964 788 010 5164", "07880105164"),
    ("9647849209270", "07849209270"),
    ("على ٠٧٨٧٥٠١٧٥٣٧", "07875017537"),
])
def test_phones(text, phone):
    assert extract(text)["phone"] == phone


def test_phone_digits_are_not_an_amount():
    e = extract("حولت 600 ألف للرقم 9647849209270")
    assert e == {"amount": 600_000, "phone": "07849209270", "reference": None}


@pytest.mark.parametrize("text", ["رقم العملية ZC-39894376", "zc39894376", "the reference is 39894376"])
def test_references(text):
    assert extract(text)["reference"] == "ZC-39894376"


def test_comma_amount_is_not_a_reference():
    assert extract("انخصم 1,020,000")["reference"] is None
