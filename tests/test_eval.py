import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from run import pick_threshold  # noqa: E402


def _row(cat, conf):
    return {"category": cat, "priority": "high", "category_confidence": conf, "priority_confidence": conf}


def _ticket(cat):
    return {"gold": {"category": cat, "priority": "high"}}


def test_picks_the_lowest_threshold_that_is_right_often_enough():
    # 10 sure and right at 0.8, 5 unsure and wrong at 0.5.
    tickets = [_ticket("card_issue")] * 15
    routed = [_row("card_issue", 0.8)] * 10 + [_row("bill_payment", 0.5)] * 5
    assert pick_threshold(tickets, routed) == 0.55


def test_picks_nothing_when_too_few_are_sure():
    tickets = [_ticket("card_issue")] * 9
    routed = [_row("card_issue", 0.99)] * 9
    assert pick_threshold(tickets, routed) is None
