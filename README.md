# Farz

Support pipeline automation for an Iraqi mobile wallet. Agentic AI Challenge Iraq (ZainCash), Topic 06.

Farz reads the support queue in batches, works out what each ticket is about, how urgent it is and which team owns it, pulls out the amount, phone number and reference, checks them against the ledger, and drafts a reply in the customer's own dialect. A support agent approves, edits or takes over every reply. Anything Farz is unsure about goes straight to a person.

**Jev decides. An LLM writes. A person sends.**

## Team

- Shakir Mahmood
- Taha Samer Saif Al-Din

## How it works

```
tickets in (batch)
   -> decider: category and priority, with a confidence for each
        Jev (TypeSafe AI), or our own local model running next to it for comparison
   -> rules: amount, phone, reference pulled from the ticket text
   -> mock ledger: do those values match a transaction on the customer's wallet?
   -> confidence gate
        sure and clean                 -> team queue, agent approves the draft
        not sure                       -> a person, with the decider's split shown
        scam, injection, ledger problem -> always a person
   -> reply draft in Iraqi Arabic (also for Arabizi), or English if the customer wrote English
        GPT-6 Astra writes it from the facts above; a check throws out any draft that
        promises money back or a time, asks for a code or PIN, quotes a number we did not
        give it, or uses a word from our banned list. A fixed template takes its place.
   -> agent screen in Iraqi Arabic: approve, edit and approve, or take over
        nothing is sent by Farz; every choice is logged
```

Try it with the saved dev results, no network needed:

```
python -m farz.screen          # then open http://localhost:8008
```

## What is here now

- `farz/` the pipeline: ticket reading (`extract.py`), the ledger check (`ledger.py`), the safety gate (`gate.py`), the two deciders (`deciders.py`, `jev.py`), reply drafts and their check (`drafts.py`, `words.py`), `pipeline.py` that joins them, and the agent screen (`screen.py`, `screen.html`).
- `data/` a 40-wallet mock ledger and 250 synthetic tickets, 175 to work with and 75 held out. All invented. `data/README.md` says how they were made and what their limits are.
- `eval/` the scorer and the results of every run. `eval/README.md` lists the local models we tried.
- `tests/` 47 tests for the reading rules, the ledger check, the gate, threshold picking, the confidence correction, the drafts, their check, the rating count and the mistake count.
- `probe/` the first test, run 23 Sep 2026: 63 Iraqi-dialect tickets written by a person, first scored with Jev only, later with both deciders, never tuned on.
- `docs/` the design brief.

## Results so far

Each decider was scored once on the 75 held-out tickets, on 23 Oct, after the file's hash was checked. The confidence threshold for the gate was picked on the 175 dev tickets only (Jev 0.85, local 0.50; the two models' confidences are on different scales).

| Held-out, 75 tickets | Jev | Our local model |
| --- | --- | --- |
| Category right | 71 (94.7%) | 67 (89.3%) |
| Priority right | 65 (86.7%) | 61 (81.3%) |
| Both right | 63 (84.0%) | 56 (74.7%) |
| Sent to the team queue | 45 (60%) | 31 (41%) |
| Of those, both right | 43 of 45 | 29 of 31 |
| Scam, injection and must-see-a-person tickets sent to a person | 14 of 14 | 14 of 14 |
| Amount, phone, reference read right; ledger check right | 75 of 75 | 75 of 75 |
| Cost for all 75 | $0.0029 | nothing |
| Time per ticket | 226 ms median, over the network | about 550 ms on a laptop CPU, counting the model load |

None of the four tickets wrongly sent to the queue was dangerous: three went to the wrong team and one was marked more urgent than it was.

On the 63 probe tickets, written by a person rather than a model, Jev got category 61 and priority 53 right and the local model 58 and 47. The local model was trained on tickets from the same two writers that wrote the held-out set, which flatters it there; the probe is the fairer comparison, and Jev is ahead on it. On the 175 dev tickets (local scored by 5-fold cross-validation) Jev got 150 fully right and the local model 111.

What this means for now: Jev stays the decider for the MVP. The local model is a working fallback that needs no network and no payment, and every ticket it is unsure about goes to a person, so it is safe if slower to save work. More training tickets, especially human-written ones, are what it needs.

### Does the confidence mean what it says?

When a decider says it is 90% sure, it should be right about 90% of the time; the gate trusts that number. The gap below is how far, on average, the stated confidence sits from how often it was actually right (0 is perfect). `python eval/calibration.py` recomputes it from the saved runs.

| Category gap | Dev | Probe | Held-out |
| --- | --- | --- | --- |
| Jev | 0.035 | 0.037 | 0.027 |
| Local, raw | 0.267 | 0.371 | 0.354 |
| Local, corrected | 0.026 | 0.136 | not run |

Jev's confidence can be taken at its word. The local model was far too modest: it said 36% where it was right 57% of the time, which is why its dev-picked threshold was only 0.50 and it sent fewer tickets to the queue. It now learns one correction for each question from its own cross-validation (dev only). This changes no answer, only how sure each answer claims to be, and it closes most of the gap.

It did not help the gate, though. On dev, the raw scores let 66 tickets through at 95% right; with the correction the best was 41 at the same 95%, because the two questions are corrected by different amounts and that reorders which tickets clear the bar. So routing keeps the raw scores, picked on dev, and the correction is an option (`--calibrated`) for when the number itself is shown or used. On probe, routing was the same either way.

### Scams on their own

Every scam ticket must reach a person, whatever the decider calls it. It did: no scam ticket was ever sent to the team queue, on any set, by either decider, because the scam words and the gate catch it even when the category is wrong. Jev also named every scam as a scam (all three sets). The local model named 21 of 24 on dev, 6 of 7 on probe and 10 of 10 on held-out; the four it missed it filed as a bill, a login, a transfer and an account problem, and the gate still sent all four to a person.

### Where it goes wrong

`eval/failures.py` counts the mistakes on dev and probe; held-out is left out so nobody tunes on its mistakes.

- **Mistakes that get past the gate are rare.** On dev, 1 Jev ticket and 2 local tickets went to a team queue with a wrong answer: two had the priority one step too high, one was a transfer filed as a wrong recipient. On the 63 hand-written tickets, none.
- **Jev errs on the careful side.** Of its 20 wrong priorities on dev, 19 were too high. Its few category slips were bills read as transfers and account checks read as general questions.
- **Our model's priority misses go both ways.** On dev, 19 too low and 18 too high, including 7 urgent tickets marked high and 1 marked low. Its category mix-ups are between close neighbours: wrong recipient and failed transfer, account checks and general questions, login and account.
- **On the hand-written tickets our model over-calls scams.** Three non-scam tickets were named scams. That costs a person's time, not safety, since scams go to a person anyway.

Drafts rated by a person: a first sample of 4 in the agent screen, 3 sent as is, 0 edited, 1 rewritten (saved in `eval/results/rating-dev.jsonl`; `python eval/rate.py eval/results/rating-dev.jsonl`). Too few for a share. Not measured yet: anything on real traffic. The held-out local numbers above were taken before the confidence correction and are left as they are; scoring it again would need a recorded second run.

## Build plan

The MVP is due 8 Nov 2026. The core has to work end to end on sample tickets by then.

| Dates | Goal |
| --- | --- |
| 23 to 29 Oct | Done: 250 synthetic tickets in dialect, English and Arabizi (75 of them held out and never tuned on), plus the 63 written by hand as the human test set (see below). 40-wallet mock ledger. Jev client in this repo, batch intake, category, priority and team routing, confidence gate. First score on the held-out set. |
| 30 Oct to 5 Nov | Done early: rules for amount, phone and reference, ledger matching, scam words force a person, reply drafts with their check, the agent screen in Iraqi Arabic, the calibration check and scam recall on their own. |
| 6 to 8 Nov | Done early: the agent screen as a dashboard, a first sample of drafts rated, the one-page update ([docs/update.md](docs/update.md)). Submit the MVP. |

After the MVP: rate more drafts as send, edit or rewrite, test on new inputs, document failure modes, and polish the demo for the progress review.

If time runs short we cut multi-channel intake, then drafts for low-priority tickets, then ledger matching. We never cut the held-out set, the escalation gate, or a person approving every reply.

### The human test set

The design brief promised 50 tickets written by Iraqi volunteers. We dropped that and use the 63 probe tickets Shakir wrote by hand on 23 Sep instead: more tickets, written by a person, and in hand already. Nothing was trained or tuned on them, and they are scored on their own. They are not as blind as a stranger's tickets would be, since the same person later helped design the categories, and they carry category and priority only, no ledger details.

## AI tools used

- **Jev** (TypeSafe AI) makes every routing decision in the MVP.
- **Our local model** is built from two open multilingual sentence encoders, `intfloat/multilingual-e5-base` (MIT) and `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (Apache 2.0), plus scikit-learn. It is trained only on our dev tickets and runs offline. It is scored next to Jev, it does not route anything live.
- **GPT-6 Astra** drafts replies only, from the facts the pipeline hands it, with every tool switched off. It never decides where a ticket goes, and a draft that fails our check is replaced by a fixed template.
- **Claude** and **Codex** help write code and documents. Every change is reviewed by us.
- Synthetic tickets were written by two LLMs from outlines we wrote (GPT-6 Astra 156, Claude 94) and checked by a script for required details and our Iraqi word list. The 63 human-written probe tickets were written by Shakir by hand on 23 Sep, before any of the pipeline existed, and are not taken from real customers. No real personal or customer data is used anywhere.
