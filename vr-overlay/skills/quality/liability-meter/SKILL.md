---
name: liability-meter
description: "The firm's accumulated-exposure tracker: feed every consequential decision to the vr-risk MCP so individually-immaterial calls can't silently aggregate into a restatement or a penalty stack. log_decision(client, tier, area, dollars, penalty_exposure) for each GREEN/YELLOW/RED action; exposure_summary(client, period) to total the running risk a client carries; threshold_breached(client, limit) to surface ACCUMULATED exposure to the partner BEFORE it compounds. Load this whenever you classify a gate or take a consequential action — 200 below-materiality decisions can sum to a material misstatement, and one client's drip of small penalties can become a stacked assessment. This is the meter that makes aggregate risk visible while each decision still looks small."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Liability, Risk, Exposure, Accumulation, Materiality, Penalty, Threshold, Quality-Control]
    related_skills: [authority-and-escalation, self-review-qc, workpaper-standard, provenance-and-evidence]
---

# Liability Meter

Every decision looks small in the moment. The danger is the *sum*. Two hundred
individually-immaterial calls — each a defensible rounding, a reasonable estimate,
a minor reclass — can aggregate into a material misstatement that forces a
restatement. A client's drip of small late-deposit and information-return slips can
stack into a penalty assessment no single item would have triggered. The liability
meter exists so that aggregate exposure is **visible to the partner before it
compounds**, while each decision still passes its own gate. Use the `vr-risk` MCP.

The three tools, and nothing you have to fabricate:
- `log_decision(client, tier, area, dollars, penalty_exposure)` — record one consequential decision: its gate tier (GREEN/YELLOW/RED), the area it touches, the dollar magnitude in play, and the penalty exposure it creates.
- `exposure_summary(client, period)` — total the running exposure a client carries across all logged decisions for the period.
- `threshold_breached(client, limit)` — test the accumulated exposure against a limit and surface a breach to the partner.

## When to use
- You **classify a gate** (`authority-and-escalation`) or take any consequential action → `log_decision` it, every time, even GREEN.
- You finish a unit of work, run a standup sweep, or close a period → `exposure_summary(client, period)` to see the running total.
- Before a handoff, a filing, a sign-off, or on cadence → `threshold_breached(client, limit)` to catch an aggregate that crossed the line.

## log_decision — one row per consequential decision
A consequential decision is anything that touches a number, an estimate, a
classification, a filing, or a client's money — not just the RED ones. The whole
point is to capture the *small* calls, because those are the ones that hide.
- **client** — KarbonCopy legal name + id (from `list_clients`), so exposure rolls up per client.
- **tier** — the gate you assigned this decision: `GREEN`, `YELLOW`, or `RED`. The tier mix is itself a signal; a wall of GREENs that sum past materiality is exactly what the meter is for.
- **area** — `cash`, `ar`, `ap`, `payroll`, `tax`, `sales-tax`, `revenue`, `close`, `equity`, `recon` — so exposure concentrates visibly (e.g. all of it sitting in payroll).
- **dollars** — the magnitude actually in play for this decision (the reclass amount, the estimate's range, the transaction size). Use Decimal precision; do not round to "feel" immaterial.
- **penalty_exposure** — the *downstream* dollar risk this decision creates if it's wrong: the IRC penalty that could attach (late deposit, §6721/§6722 information-return, accuracy-related §6662), the interest, the restatement cost. Distinct from `dollars` — a $400 misclassified deposit can carry a $10,000 penalty exposure.
Log at the moment you decide, not in a batch. A decision you didn't log is exposure the partner can't see.

## exposure_summary — the running total that no single row shows
`exposure_summary(client, period)` is the answer to "how much risk is this client
actually carrying right now?" — the question no individual gate decision can answer.
- Run it at the end of any work session, on the daily standup, and at every close.
- Read it two ways: total **dollars** (could the sum be a material misstatement?) and total **penalty_exposure** (is a penalty stack forming?).
- Watch **concentration**: $9k spread across ten areas is different from $9k all in `payroll` one week before a 941. Concentration in one area or one tier is a louder signal than the headline number.
- The summary is an input to materiality judgment, not a substitute for it — materiality is still a CPA call (`self-review-qc`), but now it's made against the aggregate, not item-by-item.

## threshold_breached — surface it BEFORE it compounds
`threshold_breached(client, limit)` tests the accumulated exposure against a limit
and is the trigger that escalates. This is the heart of the skill: the partner
hears about the aggregate **before** it forces a restatement or a stacked penalty,
not after.
- Set the `limit` from the client's materiality (the planning/performance materiality on file, or a firm default if none) — for penalty exposure, a hard dollar limit the partner is willing to carry.
- A breach is **not** a GREEN you can clear yourself. A crossed aggregate threshold is a **RED escalation to the human partner** regardless of how green each underlying decision was — that is the inversion this meter introduces and it is invariant.
- Run it before any handoff, filing, or sign-off, and on cadence (standup, close). A breach mid-period is more useful than a breach discovered at year-end.
- When it breaches, name the **top contributors** (which areas/decisions drive the total) so the partner can act on the few that matter, not re-review everything.

## How it sits under the gates (the inversion)
`authority-and-escalation` classifies each decision in isolation. The liability
meter classifies the **portfolio**. A decision can be a legitimate GREEN on its own
and still be part of an aggregate that has gone RED. When `threshold_breached`
returns true, the aggregate RED overrides the per-item GREENs: you stop, summarize,
and escalate. You never let "but each one was immaterial" justify shipping past a
breached threshold — that reasoning is precisely the failure mode the meter catches.

## Procedure
1. **Decide → log.** As you classify any gate or take any consequential action, `log_decision(client, tier, area, dollars, penalty_exposure)` — Decimal magnitudes, real penalty exposure, never batched.
2. **Total → summarize.** At session end, standup, and close, `exposure_summary(client, period)`; read dollars, penalty_exposure, and concentration.
3. **Test → escalate.** `threshold_breached(client, limit)` before handoffs/filings/sign-offs and on cadence; a breach is a RED to the partner.
4. **Name contributors.** On any breach, surface the top areas/decisions driving the total so the partner targets the few that matter.
5. **Cross-reference.** Tie the logged decisions back to their workpaper indexes (`workpaper-standard`) and provenance events (`provenance-and-evidence`) so the exposure is supportable, not a bare number.
6. **Exceptions.** A breach, or a concentration that worries you below the limit, goes to the EXCEPTIONS QUEUE for the partner; never self-clear a breach.

## Edge cases / pitfalls a 15-year CPA knows cold
- **Aggregation is the whole point** — logging only RED decisions defeats it; the misstatement hides in the GREENs you didn't bother to log.
- `dollars` and `penalty_exposure` are **different axes** — a tiny dollar item can carry an enormous penalty (a single late payroll deposit, a missed 1099 batch). Log both honestly; don't collapse them.
- A **subtotal under the limit is not a pass** if it's concentrated or trending — a $9k aggregate climbing $2k/week toward a $12k materiality is a YELLOW heads-up to the partner now, not a RED surprise next Friday.
- **Penalty stacks compound non-linearly** — §6721/§6722 can apply per return *and* per payee, late-deposit penalties tier by days late; a naive sum understates them. When in doubt, log the higher tier and let the partner judge.
- Don't **net** exposures to look smaller (an overstatement here "offsetting" an understatement there) — misstatements aggregate by absolute value for materiality; netting hides risk.
- **Reset the meter by period**, not by mood — exposure is per-client, per-period; rolling a prior period's cleared items forward inflates the total and erodes the signal.
- The meter measures *exposure*, not *guilt* — a high reading isn't a failure, it's information; the failure is letting it cross a threshold silently.
- Never tune a `limit` upward just to avoid a breach — that is moving the goalposts and it defeats the partner's protection; the limit comes from materiality, not convenience.

## Required output
- **Exposure note** — for the client/period: total dollars, total penalty_exposure, the area/tier concentration, and whether `threshold_breached` returned true.
- **Top contributors** (on a breach or a near-breach) — the few decisions/areas driving the total, each cross-referenced to its workpaper index.
- **EXCEPTIONS QUEUE** — any breach or worrying concentration as a RED item for the partner; "none — exposure within limits" stated explicitly if clean.

## Approval gate
GREEN (autonomous): `log_decision`, `exposure_summary`, and `threshold_breached` —
metering exposure is always free to do, and you should do it relentlessly on every
consequential decision. RED: a **breached aggregate threshold** is a stop-the-line
escalation to the human partner even when every underlying decision was GREEN — the
aggregate RED overrides the per-item gates. The underlying actions the meter
measures (posting material JEs, moving money, filings, client comms) keep their own
RED gates. Never raise a `limit` to dodge a breach, and never net exposures to look
smaller — both defeat the partner's protection.
