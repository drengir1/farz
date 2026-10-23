from eval.failures import failures


def _r(id, cat, pri, route="team_queue"):
    return {"id": id, "category": cat, "priority": pri, "route": route}


def test_counts_mix_ups_priority_direction_and_wrong_answers_that_reached_a_queue():
    gold = [{"category": "failed_transfer", "priority": "urgent"},
            {"category": "bill_payment", "priority": "normal"},
            {"category": "login_access", "priority": "normal"}]
    routed = [_r("a", "failed_transfer", "high", route="person"),
              _r("b", "failed_transfer", "normal"),
              _r("c", "login_access", "normal")]
    f = failures(routed, gold)
    assert f["category_wrong"] == 1 and f["confused"][0] == {"is": "bill_payment", "said": "failed_transfer", "tickets": 1}
    assert f["priority_too_low"] == 1 and f["priority_too_high"] == 0 and f["too_low"] == {"urgent as high": 1}
    assert [q["id"] for q in f["queued_but_wrong"]] == ["b"]
