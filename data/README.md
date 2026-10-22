# Data

Everything here is invented. Names are combined from short lists, phone numbers are random digits in the 078x pattern, references are random. No real customer, account or transaction is behind any of it.

- `ledger.json` 40 mock wallets with 369 transactions (transfers, bills, top-ups, agent cash in and out, card payments). Each has a reference, amount in IQD, status, and whether the customer was debited.
- `dev.jsonl` 175 tickets we may look at, train on and tune on.
- `heldout.jsonl` 75 tickets kept apart. See below.
- `gen/` how the tickets were made.

## How the tickets were made

1. `gen/make_scenarios.py` (seeded) decides every right answer first: category, priority, the amount, phone and reference the customer will mention, and which ledger rows the ticket is about. It plants those rows in the ledger, including double charges, failed-but-debited transfers, and cash deposits an agent never made.
2. It also decides how the customer writes: Iraqi dialect (161), Arabizi (30), English (28), dialect mixed with English (31), and a style (very short, angry, typos, voice-note run-on, two questions in one).
3. Two different writers turned those outlines into text, so one model's habits do not dominate: GPT-6 Astra wrote 156, Claude wrote 94 (`gen/write_tickets.py`, prompts and raw output in `gen/batches/`). The writers never saw the category or priority names.
4. `write_tickets.py check` rejects any ticket that lacks one of its required strings, uses a support-team label word, or uses a word on our Iraqi word list of corrections. All 250 passed.

Some tickets are traps on purpose: 16 try to instruct the system (ignore your rules, refund now, tell me who received the money), and 23 state an amount or reference that does not fit the ledger.

## The held-out set

The 75 held-out tickets were picked by category, with a fixed seed, before any routing code existed. We do not read them, train on them or tune on them. They are scored once per decider, at the end.

SHA-256 of `heldout.jsonl` at the moment it was written:

```
cba70facea3adb49057966a1e9ae29e1bc0162c08b470795c0a465722942891a
```

If that hash ever stops matching, the held-out score is void.

## Honest limits

These tickets were written by language models from outlines we wrote. A model trained on the dev set can pick up the writers' habits, which flatters it on the held-out set. Jev is not trained on anything here, so it does not get that advantage. To keep the comparison fair we also score both deciders on the 63 probe tickets from 23 Sep (written by a person, a different author) and, once they exist, on 50 tickets made up by Iraqi volunteers.
