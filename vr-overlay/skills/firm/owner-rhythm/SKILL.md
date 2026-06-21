---
name: owner-rhythm
description: "A private, behavioral model of the OWNER (Valentino) as a decision-maker — distinct from client-context, which holds entity facts. Captures what he always approves vs always pushes back on, his revealed risk tolerance from past sign-offs, the questions he reliably asks before each quarter-end/close, and his preferred defaults. Load it at the start of any owner-facing decision, approval, or quarter-end prep so you ANTICIPATE: pre-answer the predictable question and pre-pick the default he'd choose, instead of asking what is already predictable. Update it after every interaction via self-improvement. Stored at home/memories/owner-rhythm.md."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Owner-Rhythm, Decision-Model, Anticipation, Defaults, Risk-Tolerance, Approvals, Continuity, Behavioral]
    related_skills: [colleague, client-context, self-improvement, authority-and-escalation, communication-cadence]
---

# Owner Rhythm

You work for one principal — Valentino. After a few months a sharp human hire stops
asking him things he answers the same way every time. This skill is how you build and use
that model: a private, behavioral read of *how he decides*, so you ANTICIPATE the
predictable instead of re-asking it.

This is **not** `client-context`. That holds entity facts (EIN, FY, coding precedents per
client). This holds *Valentino-the-decision-maker*: his patterns, his tolerances, his
defaults — firm-wide, across every client. Two different memories; never merge them.

## Where the model lives
- One private file: `home/memories/owner-rhythm.md` (alongside USER.md / MEMORY.md).
- Internal only. It models a person's preferences — it is **never** quoted to a client and
  never leaves the internal relationship. Treat it like USER.md.
- It records **revealed** preference (what he actually did), not flattery. Every entry is
  dated and tied to the decision it came from, so the model is auditable, not vibes.

## Model schema (sections, in order)
1. **Always-approves** — classes of action he green-lights without fuss every time
   (e.g. "reclass to suspense pending docs," "expense under the $2,500 de-minimis line,"
   "send the routine 941 reminder draft"). These become *defaults you just pick*.
2. **Always-pushes-back** — patterns he reliably rejects or rewrites (e.g. "don't capitalize
   the borderline asset, he expenses when defensible," "hates hedged language to clients,"
   "no accrual he can't tie to a document"). These you *pre-correct before showing him*.
3. **Revealed risk tolerance** — calibrated from past sign-offs, not asserted: where he is
   aggressive (e.g. takes defensible deductions, S-corp reasonable-comp on the lower end of
   range) vs conservative (e.g. won't file without reconciled cash, wants nexus confirmed
   before collecting tax). Note the *boundary*: the case where aggressive flips to cautious.
4. **Quarter-end / close questions he always asks** — the recurring set he opens with before
   each quarter-end, month-end, or filing ("are we current through the month?", "any vendor in
   suspense?", "what's the estimated-tax number and is it covered?", "anything that slips the
   deadline?"). Pre-answer these in the prep packet so the meeting starts solved.
5. **Preferred defaults** — his standing choices when you'd otherwise ask: report format,
   rounding, materiality threshold, which client gets touched first, delivery channel, how
   much detail in a status. Pull format/cadence prefs that overlap into `communication-cadence`.
6. **Decision log (revealed)** — dated one-liners: *situation → what he chose → the rule it
   implies*. This is the evidence base; sections 1-5 are the distilled summary of it.

## Procedure — LOAD (run before any owner-facing decision or quarter-end prep)
1. Read `home/memories/owner-rhythm.md`. If absent, create it from the schema above (empty
   sections are fine — the model grows by observation, not by interviewing him cold).
2. **Anticipate, don't ask.** For the decision in front of you:
   - If it matches an **always-approves** pattern → pick that default and proceed (within the
     authority gate; see below). Note in the workpaper *why* (which pattern), don't ask.
   - If it matches an **always-pushes-back** pattern → fix it *before* he sees it, then show
     the corrected version with a one-line "did X your usual way."
   - For quarter-end/close → walk his standing question set and **pre-answer every one** in the
     packet, so he reads answers, not questions.
   - Only surface what is genuinely *new* or *outside the model* — the actual decision he
     hasn't made before. That is the signal you protect by removing the noise.
3. **Confidence, honestly.** A pattern needs a few consistent observations before you act on it
   silently. Thin evidence → still anticipate, but show your pick as a proposal he can veto in
   one word ("defaulting to expense per your usual — say the word to capitalize"), not a fait
   accompli. Never invent a preference you can't point to in the decision log.

## Procedure — UPDATE (run after every owner interaction, via self-improvement)
1. After he approves, edits, or overrides, append a dated line to the **decision log**:
   situation → his choice → the rule it implies.
2. If it confirms an existing pattern, strengthen it (note the added observation). If it
   *contradicts* one, don't silently flip — log the exception; a pattern only changes after the
   new behavior repeats. People have off-days; don't overfit to one.
3. Promote stabilized patterns up into sections 1-5 so LOAD gets faster over time. Route the
   capture through `self-improvement` (it decides skill vs MEMORY vs this file) — and do it
   **silently**: never narrate "I saved that to your rhythm file."
4. Decay: if a default stops holding (his business changed, new partner, new software), retire
   the stale entry rather than fighting his current behavior with last year's model.

## What this buys him
The tell of a great hire is the meeting that's already half-answered. He opens
quarter-end and the four questions he always asks are sitting there answered; the approval
he'd have rubber-stamped is already done with a one-line note; the only thing on his plate is
the genuinely new call. You earned that by *watching*, not by asking him to repeat himself.

## Edge cases a seasoned hire knows
- **Predictable ≠ authorized.** Anticipating his default never upgrades the authority gate. A
  RED action (post a material JE, send client comms, move money, submit a filing) is still
  prepared-then-sign-off even if you're 100% sure what he'd pick — see `authority-and-escalation`.
  You pre-fill his likely answer; he still pulls the trigger.
- **Don't anticipate a client into a corner.** This models *him*, not the client. Never let a
  modeled owner-preference override a client fact, a regulation, or the no-client-deception line.
- **One off-day isn't a pattern.** Single override = log it, don't rewrite the model.
- **Stale model is worse than none.** A confidently-wrong "he always wants X" erodes trust fast;
  date everything and decay aggressively.
- **Privacy.** This file profiles a person. It stays internal, never surfaces in client-facing
  output, and holds no secrets — pointers and patterns only.

## Authority gates
- **GREEN (autonomous):** read/build/update the model; pick an always-approves default within
  an already-GREEN action; pre-answer quarter-end questions; pre-correct an always-pushes-back
  draft before showing it.
- **YELLOW (proceed, flag):** act on a thinly-evidenced pattern, but show it as a one-word-veto
  proposal, not a silent fait accompli.
- **RED (prepare, then human sign-off):** anything the model predicts that is itself a gated
  mutation. The model informs the prep; it never authorizes the submit.

## Required output
1. **Bottom line** (one line): "Anticipated 4 of 5 — pre-answered your quarter-end set,
   defaulted reclass-to-suspense per usual; one genuinely new call for you below."
2. **NEW / OUTSIDE-MODEL** — the short list of things the model couldn't pre-decide: the real
   asks that need him.
3. **WORKPAPER note** — which patterns drove which defaults (with dates from the decision log),
   what was logged back this session, and the model's new "Last updated" date.
