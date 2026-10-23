# Farz: one-page update

Shakir Mahmood, ZainCash Agentic AI Hackathon. 23 Oct 2026, for the MVP review on 8 Nov. Code: github.com/drengir1/farz

Farz reads a ZainCash support ticket written in Iraqi Arabic, Arabizi or English, decides what it is about and how urgent it is, checks any amount, phone number and reference against the wallet's transactions, and drafts a reply. A support agent approves the draft, edits it, or takes the ticket over. Nothing is ever sent by Farz on its own, and every ticket that is unsure, a possible scam, or has a ledger problem goes to a person. All data in this project is made up; no real customer data was used.

## What works

- **Sorting.** On 75 tickets kept aside and scored once, Jev picked the right category for 71 and the right urgency for 65. Our own model, which runs on a laptop with no network and no cost, got 67 and 61.
- **Safe routing.** 45 of the 75 went straight to the right team's queue with Jev, and 43 of those were fully right. The two that were not were harmless: one wrong team, one marked more urgent than it was. Every scam, every message trying to trick the AI, and every ticket that must see a person reached a person, 14 of 14, with both models.
- **Scams.** Across all three test sets, no scam ticket ever went to the queue. Jev named every one as a scam.
- **Reading the details.** The amount, phone and reference were read right, and checked right against the ledger, in 75 of 75 tickets.
- **Reply drafts.** GPT-6 Astra wrote a draft for all 175 practice tickets in Iraqi Arabic, or in English when the customer wrote English. A check throws out any draft that promises a refund or a time, asks for a PIN or code, quotes a number we did not give it, or uses a word from our banned list; a fixed template takes its place. On the latest run all 175 drafts came from Astra and none failed the check. Two faults found by reading them are fixed: a customer who lost a card is no longer asked for a transaction number, and Arabizi like "3laykum" is no longer mistaken for an amount.
- **The agent screen.** A dashboard in Iraqi Arabic, in Nurunim's colours, light or dark, on a laptop or a phone. The overview shows the day's tickets, how many went to a person and why. The messages page shows the queue, the message, what Farz found and why it reached a person, the matching wallet transactions, and the draft, with one key to approve. Every choice is logged.
- **Drafts rated by a person.** Shakir worked the queue in the screen and rated the drafts: 3 of the first 4 were sent as is, none needed edits, and 1 was rewritten. That is a first sample, too small to give a reliable share, but the rating and its count run end to end.
- **Confidence that means something.** When Jev says 90% sure, it is right about 90% of the time (off by 3 points on average). Our model was far too modest, off by 27 points; a correction learned from practice tickets only brings that down to 3 points, though the routing keeps the uncorrected scores because they let more tickets through at the same safety.
- **Cost and speed.** Jev cost $0.0029 for all 75 tickets, about a quarter of a second each.

## What does not work yet

- **Too few rated drafts.** The check proves a draft is not dangerous, and 3 of 4 rated drafts went out untouched, but 4 is not enough to say how often an agent can send a draft without changes.
- **Tickets from real people.** All test tickets were written by people on our side or by AI models. The 63 tickets Shakir wrote by hand are the fairest test we have, and Jev is clearly ahead of our model on them. Tickets from real ZainCash customers would be the true test.
- **Our own model needs more data.** It is a safe fallback, but it sends fewer tickets to the queue than Jev because it is less sure. More hand-written training tickets are what it needs.
- **No live connection.** Farz reads a file of tickets and a made-up ledger. It is not connected to a real ticket system or wallet, by design for the hackathon.

## What comes next

1. Rate a larger sample of drafts, by more than one agent, and report the share sent untouched.
2. Collect more hand-written tickets and retrain our model.
3. With ZainCash: try Farz on a copy of real, anonymised tickets, with agents using the screen, before anything touches a customer.
