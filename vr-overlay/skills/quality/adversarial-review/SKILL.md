---
name: adversarial-review
description: "Independent adversarial review before any RED sign-off. Run AFTER self-review-qc passes and BEFORE you stage a RED gate (material/unusual JE, client comm, money movement, any tax/payroll filing). Spawn a SEPARATE reviewer via your delegation/subagent toolset — a DIFFERENT model (the multi-provider brain; delegation.model can override), BLIND to your prep reasoning (it gets ONLY the deliverable plus evidence/source docs, never your chain-of-thought), whose sole mandate is to BREAK the conclusion: re-pull the sources itself and hunt the split-to-dodge-materiality, the round-tripped or self-referential tie, the wrong-company-file/EIN, the empty exceptions queue on a messy month, the missed nexus trigger or safe-harbor. Same-model self-grading is theater — this must be genuinely independent. Any disagreement becomes an EXCEPTIONS QUEUE item for the partner; every break it lands is a self-improvement lesson. Use whenever a deliverable is about to feed a RED gate or sign-off request."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Adversarial-Review, Red-Team, Independent-Reviewer, Blind-Review, Approval-Gate, Quality-Control, Materiality, Self-Improvement]
    related_skills: [self-review-qc, authority-and-escalation, deliverable-verification, provenance-and-evidence]
---

# Adversarial Review

Self-review-qc is you grading your own work — necessary, but you are the same mind that
made the error, so you share its blind spots. Before anything RED goes up for sign-off,
a **second, independent reviewer** tries to tear the conclusion apart. This is not a
politeness pass. Its only job is to make you wrong. What survives an honest attempt to
break it is what you hand the partner.

## When to run
AFTER `self-review-qc` returns PASS / PASS-WITH-NOTES, and BEFORE you stage a RED gate or
emit an approval request (per `authority-and-escalation`): a material or unusual JE, any
client/external communication, any money movement, any tax or payroll filing or election.
GREEN/YELLOW work does not require it; a RED deliverable does. If self-review-qc FAILed,
fix that first — do not adversarially review broken work.

## Genuinely independent — or it's theater
The reviewer must be **different from the preparer in the ways that matter**:
1. **Different model.** Spawn it through your delegation/subagent toolset and route it to a
   DIFFERENT model than the one that prepared the work — the multi-provider brain makes this
   possible; set `delegation.model` to override the default so preparer and reviewer are not
   the same weights. One model grading its own output reproduces its own mistakes and rubber-
   stamps them with false confidence. Same-model self-grading is theater. Do not fake it.
2. **Blind to your reasoning.** The reviewer receives ONLY (a) the finished deliverable and
   (b) the evidence / source documents. It does NOT receive your prep chain-of-thought, your
   narration, your "why I think this is right," or your tier classification. If you hand it
   your reasoning, it anchors to your story and confirms it instead of testing it.
3. **Adversarial mandate, in writing.** Its instruction is a single sentence: *re-derive the
   answer from the source documents and find every way this conclusion is wrong.* Not "check
   my work" — break it.

## What you hand the reviewer
- The deliverable exactly as it would go to the partner: the entries/recon/return/statement,
  the EXCEPTIONS QUEUE, the workpaper, and the recorded RED tier.
- The raw evidence: source docs, the QB company identity (`qb_session_status` +
  `qb_company_info`), the read-only reports it will need to re-pull (Trial Balance, GL,
  AR/AP aging, sales-tax liability) or the `vr-ledger` validate/statement outputs.
- NOT your reasoning, your draft notes, or your conclusion-defense. Evidence and result only.

## The attack checklist — the reviewer re-derives, then hunts
The reviewer works the sources itself; agreeing with your number without re-pulling it is
not a review. It specifically hunts:
1. **Split-to-dodge-materiality.** Two $4k entries for one $8k event; a payment or write-off
   sliced under threshold; a pattern of immaterial items that aggregates material. Re-sum the
   whole event and re-classify — does the real size make this RED?
2. **Round-tripped / self-referential tie.** A "tie-out" that proves a figure against itself
   (the same export on both sides), a reconciliation that matches because the plug equals the
   difference, a subledger agreeing to a GL that was forced to it. Re-pull each side from an
   independent source and tie again.
3. **Wrong company / wrong period.** Confirm the open file's EIN and entity name and the
   period independently — a perfect close in the wrong company file is still wrong. Any
   mismatch is an immediate exception.
4. **Empty exceptions queue on a messy month.** A clean queue over a period full of unusual
   activity usually means items were guessed, not absent. The reviewer re-scans for the
   ambiguous calls that should have been escalated and weren't.
5. **Missed nexus trigger or safe-harbor.** For sales-tax / multistate / filing-threshold
   work: a crossed economic-nexus threshold not flagged, a safe-harbor or de-minimis
   exclusion not applied, a stale rate or sourcing rule. Re-test the thresholds against the
   authority, not against your summary of it.
6. **Unexplained material change.** Diff against prior independently; every material swing
   needs a real cause. The reviewer does not accept your explanation — it re-derives one.
7. **Gate integrity.** Confirm no RED action was actually executed: everything is
   prepared-pending-approval, nothing posted/sent/filed/moved. A crossed gate is a hard stop.

## What comes out
- **AGREE** — the reviewer independently re-derived the same conclusion from the sources and
  found no break. Proceed to stage the RED gate / approval request.
- **DISAGREE / BREAK FOUND** — the reviewer landed a hit (wrong number, wrong file, dodged
  materiality, missed trigger, crossed gate, guessed exception). This does **not** become a
  quiet fix-and-move-on. Every disagreement is logged as an **EXCEPTIONS QUEUE** item for the
  partner — what the reviewer found, the evidence, the $ impact, both positions, your
  recommendation. You never overrule the adversarial reviewer silently to push your own
  conclusion through; the partner adjudicates a genuine split.

## Every break is a lesson
A break the reviewer finds is not just a defect to patch — it is a hole in how you prepared.
Capture it via `self-improvement` (silently): the class of error, the tell you missed, the
check that would have caught it earlier. The point of the adversary is to make the *next*
deliverable harder to break, not only this one.

## Pitfalls
- **Faking independence.** Re-running the same model on its own output and calling it
  "review." It will agree with itself. Different model, or it doesn't count.
- **Leaking your reasoning.** Pasting your prep notes "for context" turns the adversary into
  a confirmer. Evidence and result only.
- **Treating AGREE as proof.** Independent agreement raises confidence; it is not a
  certificate. A material call still routes to the partner per `authority-and-escalation`.
- **Burying a break.** Overruling the reviewer to hit a deadline is the exact failure this
  skill exists to prevent. Time pressure is not authority — the split goes to the partner.
- **Reviewing broken work.** Adversarial review is not a substitute for self-review-qc; run
  QC first, fix FAILs, then red-team what passed.

## Authority gate
This skill is **GREEN** — it reads, re-derives, and reviews; it posts nothing and presses no
submit. But like `self-review-qc` it is a gatekeeper: a DISAGREE/BREAK blocks the RED gate
until the EXCEPTIONS QUEUE item is cleared by the partner. The no-client-deception line and
the GREEN/YELLOW/RED tiers in `authority-and-escalation` are invariant — adversarial review
strengthens the gate, it never relaxes it.

## Required output
1. **Bottom line** — `ADVERSARIAL REVIEW: AGREE` or `DISAGREE — <one-line break>` (e.g.
   "DISAGREE — $8.2k write-off split into two $4.1k entries; real size is RED, not YELLOW").
2. **Reviewer setup** — model used (and that it differs from the preparer), what evidence it
   received, confirmation it was blind to prep reasoning.
3. **Attack findings table** — each of the 7 hunts: Check | Re-derived result | Break? | evidence/$.
4. **EXCEPTIONS QUEUE** — every disagreement routed to the partner with both positions, $,
   and your recommendation; nothing material resolved by overruling the adversary.
5. **WORKPAPER note** — "Adversarial review of <deliverable> for <entity/period> by
   <reviewer model>, blind to prep; verdict <AGREE/DISAGREE>; breaks <n>; gates intact <Y/N>;
   lessons captured <Y/N>." Date and basis stated.
