"""The fixed answer lists every decider chooses from, and the tables that follow from them.

The category and priority wording is the same text the 23 Sep probe used, so the probe's
63 tickets stay a fair out-of-sample check.
"""

CATEGORIES = {
    "failed_transfer": "A wallet-to-wallet or international transfer failed, is stuck pending, was deducted but not received, or was deducted twice.",
    "wrong_recipient": "The customer sent money to the wrong number or wrong person by mistake and wants it back.",
    "login_access": "Cannot log in: OTP code not arriving, forgotten PIN, locked after attempts, new phone, lost SIM, app stuck at login.",
    "agent_dispute": "A problem with a cash-in/cash-out agent (وكيل): extra fees, cash deposit not credited, short cash-out, agent refused or did not do what was paid for.",
    "card_issue": "A problem with the wallet's payment card (Mastercard, virtual card): declined, not delivered, lost, expired, ATM, double card charge.",
    "bill_payment": "A bill, top-up, subscription, installment or purchase paid through the app that was not applied, or a question about where to pay a bill.",
    "fraud_scam": "Scam, social engineering, hacked account, unauthorized transactions, suspicious OTP codes or messages, being cheated by a seller.",
    "account_kyc": "Account verification, limits, updating ID, correcting the name, suspended account, closing the account, opening a merchant account.",
    "general_inquiry": "A general question about fees, services, branches or opening hours, app performance, unexplained small charges, or thanks and feedback.",
}

PRIORITIES = {
    "urgent": "Money is actively at risk right now: account compromised, money stolen by a scammer, lost card that must be blocked immediately.",
    "high": "The customer has lost money or money is stuck or missing, but there is no ongoing attack.",
    "normal": "A service is not working for the customer, but no money is lost or stuck.",
    "low": "A question, a request for information, a routine account change, or feedback.",
}

# The team follows from the category. Keeping it a table, not a third model decision,
# means one less thing that can be wrong.
TEAMS = {
    "failed_transfer": "transfers",
    "wrong_recipient": "transfers",
    "login_access": "account_access",
    "agent_dispute": "agent_network",
    "card_issue": "cards",
    "bill_payment": "payments",
    "fraud_scam": "fraud",
    "account_kyc": "kyc",
    "general_inquiry": "general",
}

# Categories where a transaction usually sits behind the ticket, so the ledger is checked.
MONEY_CATEGORIES = {"failed_transfer", "wrong_recipient", "agent_dispute", "card_issue", "bill_payment", "fraud_scam"}

CONTEXT = (
    "A customer of an Iraqi mobile wallet (like ZainCash) sent this support ticket. "
    "Tickets are usually in Iraqi Arabic dialect, sometimes English or Arabic written in Latin letters. "
    "Ticket: "
)
