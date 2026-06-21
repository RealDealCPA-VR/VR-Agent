---
name: continuous-close
description: "Invert month-end into an always-on close. Keep a PERSISTENT per-client close-state machine (what's tied / what's open / what's drifting) that NEVER resets, and run a frequent event-driven incremental pass over new QB activity so the books are reconciled-through-yesterday at all times and an 'audit-readiness %' asymptotes to 100% daily. Each pass reads only the delta since the last watermark, drafts (never posts) recon/categorize/accrual fixes, updates the close-state note, and verifies its own output. Trigger on 'continuous close', 'always-current books', 'daily/rolling close', 'keep [client] reconciled through yesterday', 'real-time close', or standing up a recurring incremental-close cadence for a QB-backed client."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Continuous-Close, Rolling-Close, Audit-Readiness, Reconciliation, Incremental, State-Machine, QuickBooks, Watermark, Drift]
    related_skills: [month-end-close, bank-reconciliation, transaction-categorization, proactive-routines]
---

# Continuous Close

Most firms close once a month and re-discover the same problems every time. You don't. You hold a
**persistent close-state machine per client** and run a **small incremental pass** on new activity
so the books are *reconciled-through-yesterday at all times*. The month-end "close" becomes a
five-minute confirmation, not a scramble. You **prepare/draft autonomously (GREEN)**; you **never
post** material/unusual entries and **never lock** a period without partner sign-off (**RED**).

## The mental model
Month-end close is a batch job that resets each period. Continuous close is a **streaming reducer**:
a long-lived state, plus an idempotent fold over each new chunk of QB activity. The state never
resets at month-end — it carries the watermark, the tie-outs, and the open items straight into the
next period. Your job each pass is to advance the watermark a little and shrink the open-items list.

## The persistent close-state note (NEVER resets)
Keep one note per client at `home/memories/clients/<slug>.md` under a `## CLOSE-STATE` section (or a
sibling `home/memories/clients/<slug>.close-state.md`). `os.makedirs(exist_ok=True)` the path. It is
the single source of truth across runs and survives every close. Maintain:
- **Watermark** — last processed transaction date/time (and last `qb_transaction_list` cursor/TxnID
  you reconciled through). Everything dated at/after the watermark is the *delta* this pass owns.
- **Tied accounts** — per cash/CC/loan/clearing account: last-reconciled date, GL balance at that
  date, and the support it ties to. "Tied through 6/19."
- **Open items** — the live EXCEPTIONS QUEUE: uncategorized txns, suspense / Ask-My-Accountant
  hits, unmatched deposits, stale outstanding checks, missing docs — each with age and owner.
- **Drift watch** — accounts trending wrong: a clearing account that isn't netting to zero,
  Undeposited Funds creeping up, AR/AP buckets aging, a recon variance reappearing.
- **Audit-readiness %** — your headline metric (formula below) plus the prior value, so the trend
  is visible. Date-stamp every update; never silently overwrite history you might need to recall.

## Audit-readiness % (the asymptote)
A weighted score of "how close-ready are these books *right now*", recomputed each pass:
- Bank/CC/loan accounts reconciled through yesterday (weight it heaviest).
- % of transactions categorized to a real account (not Uncategorized/suspense/Ask-My-Accountant).
- Undeposited Funds, suspense, and opening-balance-equity at/near zero.
- Scheduled accruals/prepaids/depreciation current for the elapsed period.
- Open-items count and age trending down.
New activity *lowers* it; each pass *raises* it back toward 100. It should **asymptote to 100 daily**
and only ever dip when fresh un-reconciled activity lands — a dip that doesn't recover is itself a
flag. Report the number and the delta every pass.

## The incremental pass (read-only / draft; NO posting)
1. **Open the file.** `qb_session_status` then `qb_company_info` — right company, live vs SIMULATION.
   Read the close-state note; load the watermark. (If no note, this is the **cold-start**: do a full
   `month-end-close` first to establish the baseline, then continuous from there.)
2. **Pull the delta only.** `qb_transaction_list` (or `qb_transaction_list_by_account`) for activity
   since the watermark. This is intentionally small — minutes, not hours. `qb_audit_log` catches
   back-dated edits to *already-closed* periods (a classic silent breaker of a prior tie-out).
3. **Incremental recon.** For each cash/CC account touched, advance the tie-out: match new cleared
   items, refresh `qb_uncleared_transactions`, run `qb_reconciliation_discrepancy`. Update each
   account's "tied through" date. A recon that "ties" only via an unexplained plug is **not tied** —
   it's an open item. (Mechanics: `bank-reconciliation`.)
4. **Incremental categorize.** New uncategorized/suspense/Ask-My-Accountant txns: apply the client's
   established coding rules and prior decisions from the close-state note. **Draft** the reclass; do
   not post. Anything genuinely ambiguous goes to **open items**, never guessed. (`transaction-categorization`.)
5. **Incremental accrual.** Only the marginal slice for elapsed days: recurring accruals coming due,
   the next month's prepaid amortization, depreciation for the elapsed period. Draft as JEs with
   Dr/Cr proving they balance; queue auto-reversals. Do not double-book what month-end will catch.
6. **Update drift watch.** Re-check the danger accounts (clearing nets to zero? Undeposited Funds
   flat? suspense empty? variance gone?). Worsening trend -> drift flag, even if not yet an error.
7. **Advance the watermark, recompute audit-readiness %, write the close-state note.** Date-stamp.
   Only advance past items you actually reconciled/categorized; leave open items behind the line.

## Verify before you trust the number (deliverable-verification)
The audit-readiness % is a deliverable — treat it like one. Per `deliverable-verification`: re-pull
the figure independently rather than trusting your own running tally (e.g. confirm "tied through
6/19" by re-reading the GL balance at that date, confirm the categorized-% against a fresh
`qb_transaction_list`), confirm the watermark didn't skip days, and confirm no closed-period edit
slipped past via `qb_audit_log`. A score you can't independently reproduce is not a score — flag it.

## Idempotency & safety (the things that break a streaming close)
- **Idempotent passes.** Re-running a pass must not double-count. Key off TxnID + the watermark;
  never re-accrue or re-categorize what's already behind the line.
- **Back-dated edits.** A transaction inserted *before* the watermark won't appear in a naive delta —
  `qb_audit_log` is how you catch it. Treat a closed-period edit as a RED-adjacent exception.
- **Clock/timezone.** "Through yesterday" is the client's books timezone; pin it so the watermark
  doesn't skip or repeat a day across runs.
- **Cold-start vs steady-state.** Don't run an incremental pass on books with no baseline tie-out —
  you'll asymptote to a confident-but-wrong number. Baseline via `month-end-close` first.
- **Month-end is now a confirmation.** At period boundary, you don't re-close — you verify the
  carried state, post the last scheduled JEs (immaterial via `dryRun` then real; material -> RED),
  and recommend the closing-date lock. The partner authorizes the lock; you never set it unasked.

## Cron — frequent incremental pass (read-only / draft; no posting)
Register once. Runs the delta pass every weekday morning so books stay current through yesterday:
```bash
hermes cron add "20 6 * * 1-5" \
  "Continuous-close incremental pass for each active QB client (READ-ONLY / DRAFT; NO posting, \
no sends). (1) qb_session_status + qb_company_info; read the close-state note and load the \
watermark. (2) qb_transaction_list since the watermark + qb_audit_log for back-dated edits to \
closed periods. (3) Incremental recon (qb_uncleared_transactions, qb_reconciliation_discrepancy), \
categorize, and the marginal accrual slice -- DRAFT only. (4) Recompute audit-readiness %, update \
drift watch, advance the watermark, and write home/memories/clients/<slug>.md. Verify the % is \
independently reproducible. Output: per-client bottom line (tied-through date + audit-readiness % \
and delta), the open-items EXCEPTIONS QUEUE, and any drift flags. No JEs posted, no closing-date \
changes." \
  --name continuous-close --deliver email \
  --skill continuous-close --skill bank-reconciliation \
  --skill transaction-categorization --skill deliverable-verification
```

## Required output (each pass)
1. **Bottom line** per client: tied-through date, audit-readiness % and its delta vs last pass, and
   open-items count. E.g. "Acme tied through 6/19; audit-readiness 97% (+2); 2 open items, 1 drift."
2. **Close-state diff** — what advanced (watermark, newly-tied accounts) and what's still open.
3. **Drafted fixes** — proposed categorizations/JEs with Dr/Cr proving balance; nothing posted.
4. **EXCEPTIONS QUEUE** — every uncategorized/ambiguous/back-dated item with age and the question.
5. **Drift flags** — accounts trending wrong, even if not yet broken.

## Approval gate
GREEN: read, pull deltas, reconcile incrementally, draft categorizations and scheduled JEs, update
the close-state note, compute and report audit-readiness %, verify your own number. RED (prepare,
then require partner sign-off): posting material/unusual JEs, any reclass into equity or a prior
period, recording a back-dated edit's correction, and setting/locking the closing date. Never
fabricate a "tied" status or an audit-readiness % you can't reproduce. The number is a promise.
