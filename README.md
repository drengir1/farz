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
   -> Jev: category, priority, team, with a confidence for each
   -> rules: amount, phone, reference pulled from the ticket text
   -> mock ledger: do those values match a real transaction?
   -> LLM: reply drafted in the customer's dialect
   -> confidence gate
        sure       -> team queue, agent approves the draft
        not sure   -> a person, with Jev's split shown
        scam words -> always a person, urgent
```

## What is here now

- `probe/` the first test, run 23 Sep 2026 before the build stage. 63 Iraqi-dialect tickets, run once with no tuning.
  - Category right on 61 of 63 (96.8%). Priority right on 54 of 63 (85.7%).
  - Every ticket above 0.90 confidence was right (57 of 57). Both mistakes were below it.
  - Median 463 ms per ticket from Baghdad. $0.0023 for all 63.
  - Small and written by the same person who wrote the categories, so it is optimistic. The build stage measures again on a held-out set.
  - `probe.py` uses a Jev client from another project of ours. The build stage replaces it with a client in this repo.
- `docs/` the design brief (`ShakirMahmood_SupportPipelineAutomation.pdf`, built from `brief.html`).

## Build plan

| Week | Goal |
| --- | --- |
| 1 | 300 tickets: 250 synthetic in dialect, English and Arabizi (75 of them held out and never tuned on) plus 50 written by real Iraqis. 40-wallet mock ledger. |
| 2 | Jev client in this repo, batch intake, category, priority and team routing, confidence gate. First score on the held-out set. |
| 3 | Rules for amount, phone and reference. Ledger matching. Scam words force a person. |
| 4 | Reply drafts in dialect. Agent screen to approve, edit or take over. 50 drafts rated send, edit or rewrite. |
| 5 | Full held-out run, calibration check, fraud recall on its own, demo. |

If time runs short we cut multi-channel intake, then drafts for low-priority tickets, then ledger matching. We never cut the held-out set, the escalation gate, or a person approving every reply.

## AI tools used

- **Jev** (TypeSafe AI) makes every routing decision.
- **GPT-6 Astra** drafts replies only. It never decides where a ticket goes.
- **Claude** and **Codex** help write code and documents. Every change is reviewed by us.
- Synthetic tickets are generated with an LLM and checked by hand. The 50 human-written tickets are not.
