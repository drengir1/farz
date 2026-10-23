from farz.drafts import check, draft_all, facts, reply_language, template
from farz.ledger import Ledger
from farz.words import word_problems

WALLET = {"wallet_id": "W01", "name": "test", "phone": "07800000001", "balance": 100_000, "transactions": [
    {"ref": "ZC-11111111", "type": "p2p_send", "amount": 50_000, "status": "failed", "debited": True,
     "counterparty": "07811111111", "time": "2026-10-15T10:00"},
    {"ref": "ZC-22222222", "type": "card_payment", "amount": 75_000, "status": "success", "debited": True,
     "counterparty": "07822222222", "time": "2026-10-16T12:00"},
    {"ref": "ZC-33333333", "type": "card_payment", "amount": 75_000, "status": "success", "debited": True,
     "counterparty": "07822222222", "time": "2026-10-16T12:02"},
]}
L = Ledger([WALLET])


def _row(category, team, route="team_queue", outcome=None, txns=(), reasons=()):
    ledger = {"outcome": outcome, "txns": list(txns), "why": ""} if outcome else None
    return {"id": "x1", "category": category, "team": team, "route": route, "ledger": ledger, "reasons": list(reasons)}


def _ticket(text):
    return {"id": "x1", "text": text, "wallet_phone": "07800000001"}


def test_reply_language():
    assert reply_language("حولت 50 ألف وما وصلت") == "arabic"
    assert reply_language("Salam, 7awalt 50 alf w ma wesal") == "arabic"
    assert reply_language("Hello, my transfer of 50,000 IQD failed") == "english"


def test_failed_and_debited_transfer_says_what_the_ledger_shows():
    t = _ticket("حولت 50 ألف وطلعت فاشلة بس انخصمت")
    f = facts(_row("failed_transfer", "transfers", outcome="match", txns=["ZC-11111111"]), t, L)
    d = template(f)
    assert "ZC-11111111" in d and "50,000" in d and "منخصم" in d and "فريق التحويلات" in d
    assert check(d, f, t["text"]) == []


def test_double_charge_names_both_rows():
    t = _ticket("انخصم مني 75 ألف مرتين بالكارت")
    f = facts(_row("card_issue", "cards", outcome="match", txns=["ZC-22222222", "ZC-33333333"]), t, L)
    d = template(f)
    assert f["twice"] and "ZC-22222222" in d and "ZC-33333333" in d


def test_ledger_rows_are_not_quoted_when_the_ledger_disagrees():
    t = _ticket("حولت 60 ألف رقم العملية ZC-11111111")
    f = facts(_row("failed_transfer", "transfers", route="person", outcome="mismatch", txns=["ZC-11111111"]), t, L)
    d = template(f)
    assert "50,000" not in d and "موظف مختص" in d


def test_scam_reply_carries_the_safety_line_in_english_too():
    t = _ticket("Someone called saying he is from the company and I gave him the code")
    f = facts(_row("fraud_scam", "fraud", route="person", reasons=["scam signs in the text"]), t, L)
    d = template(f)
    assert "never ask for your PIN" in d and check(d, f, t["text"]) == []


def test_check_flags_promises_secrets_numbers_language_and_words():
    t = _ticket("حولت 50 ألف وما وصلت")
    f = facts(_row("failed_transfer", "transfers"), t, L)
    assert "promises money back or a time" in check("هلا، راح نرجعلك المبلغ خلال 24 ساعة.", f, t["text"])
    assert "asks for a code, PIN or password" in check("هلا، دزلنا الكود اللي وصلك حتى نتأكد.", f, t["text"])
    assert check("هلا، احنا ما نطلب منك الكود أبداً.", f, t["text"]) == []
    assert any("number 999000" in p for p in check("هلا، شفنا مبلغ 999000 دينار.", f, t["text"]))
    assert "not written in arabic" in check("Hi, we got your message.", f, t["text"])
    assert word_problems("الحساب مسدود") and check("هلا، الحساب مسدود هسه.", f, t["text"])


def test_template_drafts_pass_their_own_check_on_every_route():
    rows, tickets = [], []
    for cat, team in (("login_access", "account_access"), ("general_inquiry", "general"), ("bill_payment", "payments")):
        for route in ("team_queue", "person"):
            rows.append(_row(cat, team, route=route))
            tickets.append(_ticket("ما اگدر أدفع الفاتورة من التطبيق"))
    for r in draft_all(rows, tickets, L):
        assert r["draft_writer"] == "template" and r["draft_problems"] == []


def test_lost_card_is_not_asked_for_a_transaction_number():
    lost = facts(_row("card_issue", "cards", route="person"), _ticket("ضاعت بطاقتي وأريد أوقفها"), L)
    charged = facts(_row("card_issue", "cards"), _ticket("انخصم مني مبلغ بالبطاقة وما اشتريت شي"), L)
    assert not lost["details_missing"] and "رقم العملية" not in template(lost)
    assert charged["details_missing"]
