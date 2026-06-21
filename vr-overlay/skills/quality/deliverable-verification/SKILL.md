---
name: deliverable-verification
description: "Every number you assert in a deliverable must first be confirmed by the vr-verify spine — a number the spine did not re-derive is NOT done, it is a draft. Load this whenever you produce a numeric deliverable: journal entries, a trial balance or tie-out, a depreciation/amortization schedule, a loan amortization or payment, a retained-earnings roll-forward, a footing/cross-foot, or any worksheet whose totals you are about to state to the partner or a client. Defines the side-artifact 'verification spec' you emit alongside the deliverable (the entries, the tie-out table of {name,expected,actual}, and the recompute params) and mandates the exact vr-verify call sequence (check_balanced, check_ties, foot, recompute_depreciation, recompute_loan_payment, reroll_retained_earnings) that must pass before you write the number down. Pairs with workpaper-standard (where the number lives) and self-review-qc (the human-eyes pass on top)."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Verification, Tie-Out, Footing, Recompute, Deliverable, Quality, Numbers, Spine]
    related_skills: [workpaper-standard, self-review-qc, authority-and-escalation]
---

# Deliverable Verification

A number you typed is a *claim*. A number the **vr-verify** spine re-derived is a *fact*. You only
ship facts. Before you assert any figure in a deliverable, you run it back through the spine; if the
spine did not confirm it, it is not done — it is a draft you are not allowed to send yet.

This is not optional self-discipline you can skip when you're confident. Confidence is exactly when
errors ship. The rule is mechanical: **every asserted number gets a verify call, or it doesn't go out.**

## The verification spec (the side-artifact)

For any numeric deliverable, emit a small spec *alongside* the deliverable. It is the machine-checkable
shadow of what you're claiming. Three sections, only the ones that apply:

- **entries** — the journal entries you're posting, line by line with debits/credits, for `check_balanced`.
- **ties** — a tie-out table: a list of `{name, expected, actual}` rows, where `expected` is the
  independent source (prior workpaper, bank statement, fixed-asset register, GL balance) and `actual`
  is the number in your deliverable. Fed to `check_ties`. Also list any column/row that must `foot`.
- **recompute** — the parameters for anything you derived from a formula rather than read off a
  document: depreciation (cost, salvage, life, method, period), a loan payment (principal, rate, term),
  or a retained-earnings roll (beginning RE, net income, dividends/distributions, expected ending).

The spec is data, not prose. You hand each section to the matching tool and read back PASS/FAIL.

## The vr-verify tools (the only ones you call here)

Use **exactly** these six — never invent a verify tool that isn't on this list:

- `check_balanced` — debits == credits for an entry or batch. Run on every journal entry.
- `check_ties` — for each `{name, expected, actual}`, confirms `expected == actual` (within zero
  tolerance unless you state one). Run on every tie-out.
- `foot` — re-adds a column/list and cross-foots; confirms the stated total. Run on every total you print.
- `recompute_depreciation` — re-derives the period (and accumulated) depreciation from the asset params.
- `recompute_loan_payment` — re-derives the payment / interest / principal split from the loan params.
- `reroll_retained_earnings` — re-rolls beginning RE + net income − distributions to your ending RE.

If a number isn't covered by one of these, that's a signal to decompose it until it is (a P&L line is a
`foot` of its accounts; a schedule total is a `foot` of its rows; a computed value is a `recompute`).

## The discipline

1. Build the deliverable.
2. Build the verification spec from it.
3. Run the spine over the spec — one call per tool that applies.
4. **Any FAIL → stop.** Fix the deliverable (not the spec) and re-run from step 2. Never edit the
   `expected` to match a wrong `actual` — that's gaming the check, and it's the no-deception line.
5. All PASS → record the verify results in the workpaper per **workpaper-standard**, then hand off to
   **self-review-qc** for the human-eyes pass (reasonableness, classification, presentation) that the
   spine cannot do. Spine-green is necessary, never sufficient — both gates clear before it ships.

A number that never made it into the spec is the dangerous one: it looks asserted but was never checked.
When you review your own spec, ask "is every figure in the deliverable represented in a section here?"
If a figure has no row, it has no verification, and it is not done.

## Worked example — a fixed-asset purchase + tie-out

**Deliverable:** post a $24,000 machine bought 2025-01-01 (5-yr straight-line, $0 salvage), and tie the
FY2025 depreciation and ending accumulated depreciation to the fixed-asset register.

**Verification spec:**
```
entries:
  - JE-2025-014:
      DR  Machinery & Equipment   24000.00
      CR  Cash                     24000.00
recompute:
  - depreciation: {cost: 24000.00, salvage: 0.00, life_years: 5,
                   method: straight_line, period: FY2025}   # expect 4800.00
ties:
  - {name: "FY2025 depr exp",          expected: 4800.00,  actual: 4800.00}
  - {name: "Accum depr 12/31/25",      expected: 4800.00,  actual: 4800.00}
foot:
  - {name: "FA register dep column",   rows: [4800.00], total: 4800.00}
```

**Verify call sequence:**
```
check_balanced(JE-2025-014)                 -> PASS  (24000 == 24000)
recompute_depreciation(cost=24000, salvage=0, life_years=5,
                       method=straight_line, period=FY2025) -> 4800.00
check_ties([{FY2025 depr exp,4800,4800},
            {Accum depr 12/31/25,4800,4800}]) -> PASS
foot(rows=[4800.00], total=4800.00)          -> PASS
```

Four greens → the $4,800 is now a fact. Had `recompute_depreciation` returned `4800.00` but the
register's `expected` said `4000.00`, `check_ties` FAILs — you investigate the register/source, you do
**not** quietly overwrite expected. Only after all-PASS do you write "FY2025 depreciation $4,800" in the
deliverable and log the verify results to the workpaper.

## When the spine and a source disagree

A FAIL is information, not an obstacle. The recompute is arithmetic-correct by construction, so a tie
break usually means the source is stale, the params are wrong, or your `actual` was mistyped. Run it
down; if it's a real discrepancy in the client's records, that's an exception — escalate per
**authority-and-escalation**, don't paper over it to get to green.
