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
   -> LLM: reply drafted in the customer's dialect (not built yet)
   -> confidence gate
        sure and clean                 -> team queue, agent approves the draft
        not sure                       -> a person, with the decider's split shown
        scam, injection, ledger problem -> always a person
```

## What is here now

- `farz/` the pipeline: ticket reading (`extract.py`), the ledger check (`ledger.py`), the safety gate (`gate.py`), the two deciders (`deciders.py`, `jev.py`) and `pipeline.py` that joins them.
- `data/` a 40-wallet mock ledger and 250 synthetic tickets, 175 to work with and 75 held out. All invented. `data/README.md` says how they were made and what their limits are.
- `eval/` the scorer and the results of every run. `eval/README.md` lists the local models we tried.
- `tests/` 35 tests for the reading rules, the ledger check, the gate and threshold picking.
- `probe/` the first test, run 23 Sep 2026: 63 Iraqi-dialect tickets written by a person, Jev only, no tuning.
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

What has not been measured yet: the 50 volunteer-written tickets, the reply drafts, and anything on real traffic.

## Build plan

The MVP is due 8 Nov 2026. The core has to work end to end on sample tickets by then.

| Dates | Goal |
| --- | --- |
| 23 to 29 Oct | Done except the volunteer tickets: 300 tickets: 250 synthetic in dialect, English and Arabizi (75 of them held out and never tuned on) plus 50 made up by Iraqi volunteers. 40-wallet mock ledger. Jev client in this repo, batch intake, category, priority and team routing, confidence gate. First score on the held-out set. |
| 30 Oct to 5 Nov | Done early: rules for amount, phone and reference, ledger matching, scam words force a person. Left: reply drafts in dialect. A simple agent screen in Iraqi Arabic to approve, edit or take over. |
| 6 to 8 Nov | Full run on the held-out set, calibration check, fraud recall on its own. One-page update: what works, what does not yet, what comes next. Submit the MVP. |

After the MVP: rate 50 drafts as send, edit or rewrite, test on new inputs, document failure modes, and polish the demo for the progress review.

If time runs short we cut multi-channel intake, then drafts for low-priority tickets, then ledger matching. We never cut the held-out set, the escalation gate, or a person approving every reply.

## AI tools used

- **Jev** (TypeSafe AI) makes every routing decision in the MVP.
- **Our local model** is built from two open multilingual sentence encoders, `intfloat/multilingual-e5-base` (MIT) and `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (Apache 2.0), plus scikit-learn. It is trained only on our dev tickets and runs offline. It is scored next to Jev, it does not route anything live.
- **GPT-6 Astra** drafts replies only. It never decides where a ticket goes.
- **Claude** and **Codex** help write code and documents. Every change is reviewed by us.
- Synthetic tickets were written by two LLMs from outlines we wrote (GPT-6 Astra 156, Claude 94) and checked by a script for required details and our Iraqi word list. The 50 human-written tickets are invented by Iraqi volunteers, not taken from real customers. No real personal or customer data is used anywhere.
