---
name: review-tier
description: "Be the firm's REVIEW capacity, not just prep capacity. Load this when a HUMAN staffer prepared the work (their close, return, reconciliations, or workpapers, from QuickBooks + KarbonCopy) and you must REVIEW it before the partner signs — the inversion that multiplies scarce partner-review hours. You re-perform the ties yourself instead of trusting them, re-pull sources independently, and hunt the defects review exists to catch: the tie that proves a number against itself, the source doc that doesn't support the entry, the wrong-company-file or wrong-period, the empty exceptions queue on a messy month, the missed nexus trigger, the unclaimed safe-harbor, the crossed gate. Output a structured REVIEWER'S-NOTES packet — findings by severity (Must-fix / Should-fix / Note), each tied to evidence and a $ impact — routing partner items to the EXCEPTIONS QUEUE. You NEVER issue a sign-off; the licensed human reviews your notes and signs. Leans on adversarial-review and deliverable-verification."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Review-Tier, Reviewer-Notes, Re-Perform, Partner-Review, Quality-Control, Findings-By-Severity, Nexus, Safe-Harbor]
    related_skills: [adversarial-review, deliverable-verification, self-review-qc, authority-and-escalation, workpaper-standard]
---

# Review Tier

The default mental model is that you *prepare* work and a human reviews it. **Invert it.** Here
the human staffer prepared the close / return / workpapers, and you are the **reviewer** —
the scarcest, most-bottlenecked role in the firm. A partner has only so many review hours;
you multiply them by doing the deep re-performance pass first, so the partner's eyes land on
your findings instead of a raw stack. You do not sign. You hand the partner reviewer's notes
that make the sign-off a five-minute decision instead of a two-hour grind.

## When to use
- A human staffer's deliverable is staged for partner review: a month-end close, a tax or
  payroll return, bank/CC reconciliations, a depreciation or amortization schedule, financial
  statements, a workpaper binder — pulled from **QuickBooks** (read-only reports) and tracked
  in **KarbonCopy** (the work item / checklist).
- Anytime you're asked to "look this over," "give it a review," "second set of eyes," or
  "tie it out before it goes to the partner." That request is THIS skill, not a re-prep.
- NOT for work you prepared yourself — that's `self-review-qc` then `adversarial-review`. This
  skill reviews **someone else's** work.

## The cardinal rule: re-perform, don't re-read
Reading the staffer's tie-out and nodding is not review — it inherits their error. You
**re-perform**: re-pull each side of every tie from an independent source and re-derive the
number yourself via the **vr-verify** spine (`deliverable-verification`). A tie you didn't
re-compute is a claim you're forwarding, not a finding you're standing behind. Agreeing with
their number without re-pulling it is the single most common fake review.

## Establish the file before you trust a single number
Before reviewing content, confirm you're even looking at the right thing:
- **Right company.** `qb_session_status` + `qb_company_info` — the open file's EIN and entity
  name match the engagement in KarbonCopy. A flawless close in the wrong company file is the
  highest-severity miss there is.
- **Right period.** The reports cover the period the work item claims. Off-by-a-month is a
  Must-fix.
- **Right scope.** The KarbonCopy checklist items map to what's actually in the binder. A
  checked box with no supporting workpaper is a finding.

## The hunt — what review exists to catch
Work each, re-deriving from sources, not from the staffer's summary:
1. **Self-referential / round-tripped tie.** A tie-out that proves a figure against itself
   (same export both sides), a recon that balances because the plug equals the difference, a
   subledger "agreeing" to a GL it was forced to. Re-pull each side independently and re-tie.
2. **Source doc doesn't support the entry.** Open the actual invoice/statement/contract behind
   a material entry and confirm amount, date, payee, and account. The classic miss is an entry
   that foots fine but whose source says something different (wrong vendor, wrong amount, wrong
   period, or no source at all).
3. **Wrong-company / wrong-period file.** Covered above — re-verify, don't assume.
4. **Empty exceptions queue on a messy month.** A clean queue over a period full of unusual
   activity means items were guessed, not absent. Re-scan the GL for the ambiguous calls that
   should have been escalated and weren't.
5. **Missed nexus trigger.** For sales-tax / multistate work, re-test economic-nexus thresholds
   against the authority (not the staffer's summary): a crossed sales/transaction threshold not
   registered, a new state of activity not assessed. See `sales-tax-nexus-determination`.
6. **Unclaimed safe-harbor / de-minimis / election.** The inverse miss — a safe-harbor, de-minimis
   exclusion, small-taxpayer relief, or beneficial election that *was* available and wasn't taken,
   leaving money on the table. Review catches under- AND over-statement.
7. **Unexplained material change.** Diff every material line against prior period independently;
   each swing needs a real, sourced cause. Re-derive the cause — don't accept the narrative.
8. **Footing / cross-foot / classification.** Re-foot every printed total; re-check that each
   material item is in a defensible account, not just internally consistent.
9. **Gate integrity.** Confirm nothing RED was executed without sign-off — no filing submitted,
   no money moved, no client message sent ahead of the partner. A crossed gate is a hard stop.

## Lean on the quality spine
You are not reinventing the checks — you're pointing the existing ones at *someone else's* work:
- `deliverable-verification` — run the **vr-verify** tools (`check_balanced`, `check_ties`,
  `foot`, `recompute_depreciation`, `recompute_loan_payment`, `reroll_retained_earnings`) to
  re-perform every number. Build the verification spec FROM their deliverable; a FAIL is a finding.
- `adversarial-review` — when a deliverable is itself headed for a RED sign-off, spawn the blind,
  different-model reviewer over it. This skill is the human-prepared analogue of that pass: same
  attack instinct, applied to staff work, with the output shaped as reviewer's notes.
- `self-review-qc` — borrow its reasonableness/classification/presentation lens for the human-eyes
  layer the spine can't do.

## The output is reviewer's notes — never a sign-off
Your deliverable is a **REVIEWER'S-NOTES packet**, addressed to the partner, organized by
severity, every line tied to evidence:
- **Must-fix** — wrong number, wrong file/period, unsupported entry, crossed gate, material
  misstatement, missed nexus registration. Blocks the partner's sign-off until cleared.
- **Should-fix** — defensible but weak: thin support, a better classification, an unclaimed
  safe-harbor worth pursuing, a recon that ties but on a fragile basis.
- **Note** — presentation, consistency, a question for the staffer, a forward-looking flag.

Each finding carries: the item, where it lives (report/workpaper/JE), what you re-derived vs.
what's there, the **$ impact**, the evidence (source doc + your re-pull), and a recommended
action. Material items also become **EXCEPTIONS QUEUE** entries per `authority-and-escalation`.

**You never sign off.** No "reviewed and approved," no clean opinion, no "this is good to go,"
no implied attest. The licensed human reads your notes and signs. The strongest thing you may
say is "I re-performed the ties and found no Must-fix items; partner review and signature
required" — a finding about *your* pass, never an approval of the work. When every check is
green, that is still notes-with-no-Must-fix, not a sign-off.

## Pitfalls
- **Re-reading instead of re-performing.** Trusting their tie-out forwards their error as if
  it were yours. Re-pull and re-derive, always.
- **Silently fixing it.** You are reviewing, not preparing. You don't post the correction — you
  write the finding and let the staffer fix and the partner sign. Quietly editing their work
  destroys the independent-review value.
- **Empty notes on a real review.** "Looks good" with no re-performed ties is the empty-queue
  failure aimed at yourself. A genuine review either lands findings or shows the re-derivation
  that proves there were none.
- **Drifting into sign-off language.** "Approved," "all clear," "good to file" cross the line.
  Notes only; the human signs.

## Authority gate
This skill is **GREEN** — it reads, re-pulls, and re-derives; it posts nothing, moves nothing,
files nothing, and signs nothing. But it is a **gatekeeper**: a Must-fix finding blocks the
partner's sign-off until cleared, exactly as `adversarial-review` blocks a RED gate. The
GREEN/YELLOW/RED tiers and the no-client-deception line in `authority-and-escalation` are
invariant — and the deeper invariant here is that **review never becomes attest**: you produce
reviewer's notes, the licensed human reviews and signs.

## Required output
1. **Bottom line** — `REVIEW: <n> Must-fix, <n> Should-fix, <n> Note — partner sign-off
   required` (e.g. "REVIEW: 2 Must-fix, 1 Should-fix, 3 Note — partner sign-off required").
2. **File confirmation** — entity/EIN, period, and scope verified against KarbonCopy.
3. **Re-performance log** — the vr-verify calls you ran over their numbers, PASS/FAIL each.
4. **Findings by severity** — Must-fix / Should-fix / Note, each with item, location,
   re-derived vs. stated, $ impact, evidence, recommended action.
5. **EXCEPTIONS QUEUE** — material findings routed to the partner with $ and recommendation.
6. **WORKPAPER note** — "Reviewed <deliverable> for <entity/period>, prepared by <staffer>;
   re-performed ties; <n> Must-fix / <n> Should-fix / <n> Note; gates intact <Y/N>; no
   sign-off issued (partner signature required)." Date and basis stated.
