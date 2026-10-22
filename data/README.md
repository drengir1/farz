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

SHA-256 of `heldout.jsonl`:

```
39de061d3e0be132730027fa5be38c79be07a6781a62305c767321d397ca9b38
```

If that hash ever stops matching, the held-out score is void.

One change was made before any decider was scored on it. On 23 Oct, reading Jev's priority mistakes on the dev set showed four of our situations broke our own written priority rules (`farz/schema.py`). They were fixed by the rule, for every ticket of that situation in both files: an agent's extra fee and a small unexplained deduction became high (money lost or missing), closing an account became low (a routine account change), a prize SMS where nothing was paid became low (a question). That moved 14 dev labels and 2 held-out labels. No text changed. The same day we found the first hash, `cba70fac…2891a`, had been taken on a copy with Windows line endings while git stored plain ones, so a fresh clone would have failed the check. The generator now always writes plain newlines and the hash above is of those bytes. Arguable cases, such as repeated unrequested codes (we say high, Jev often says urgent), were left as they were.

## Honest limits

These tickets were written by language models from outlines we wrote. A model trained on the dev set can pick up the writers' habits, which flatters it on the held-out set. Jev is not trained on anything here, so it does not get that advantage. To keep the comparison fair we also score both deciders on the 63 probe tickets from 23 Sep (written by a person, a different author) and, once they exist, on 50 tickets made up by Iraqi volunteers.
