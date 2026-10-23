import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from rate import summarise  # noqa: E402


def _a(id, choice, changed=False, draft="هلا بيك، وصلتنا رسالتك.", sent=None, writer="astra"):
    return {"id": id, "choice": choice, "changed": changed, "draft": draft, "sent_text": sent,
            "draft_writer": writer, "route": "person", "category": "card_issue"}


def test_choices_become_send_edit_rewrite_and_the_last_choice_counts():
    s = summarise([
        _a("t1", "take_over"), _a("t1", "approve"),                            # changed mind: send
        _a("t2", "edit", changed=False, sent="هلا بيك، وصلتنا رسالتك."),      # no real change: send
        _a("t3", "edit", changed=True, sent="هلا بيك، وصلتنا رسالتك ونعتذر."),
        _a("t4", "take_over", writer="template"),
    ])
    assert s["all"] == {"tickets": 4, "send": 2, "edit": 1, "rewrite": 1, "send_share": 0.5}
    assert 0.5 < s["kept_in_edits_median"] < 1
    assert s["by_writer"]["template"]["rewrite"] == 1
