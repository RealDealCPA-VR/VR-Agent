---
name: cohort-benchmarking
description: "Benchmark a client privately against the firm's OWN book of business. At each close or review, compute the client's operating metrics (gross margin, payroll-%-of-revenue, DSO, rent-%, owner-comp ratio), feed each one DE-IDENTIFIED into the vr-cohort MCP under its NAICS peer group keyed by a one-way HASH of the client id, then score the client against that cohort and flag outliers in plain English ('payroll is 3.2 sigma above your 14 retail clients'). Builds a proprietary peer dataset no public benchmark matches, behind a hard PRIVACY WALL: only the abstracted statistical signal crosses clients, never a client's confidential figures. Use during month-end-close, financial-statement-prep, or QBR prep, or when asked 'how does this client compare', 'is X normal for this industry', or 'flag anything off'. Reads metrics from quickbooks/vr-ledger; observations and scoring are GREEN; any peer comparison reaching a client deliverable is RED until reviewed."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Benchmarking, Cohort, Peer-Analysis, NAICS, Outlier-Detection, Privacy-Wall, De-Identification, Advisory]
    related_skills: [month-end-close, financial-statement-prep, client-context, consulting]
---

# Cohort Benchmarking

Every close, every client teaches the firm something — *if* you capture it. This skill turns the
book of business into a private benchmark: each client's operating metrics feed an anonymized
peer pool keyed by industry, and each client gets scored against that pool. The firm's edge is a
dataset built from its own clients that no purchased benchmark can match — and a privacy wall
that keeps it ethical.

## The privacy wall (read first, never cross)
Only the **abstracted statistical signal** crosses clients — a metric value attached to a NAICS
code and a hashed id. **No client's confidential data ever lands in another client's workspace.**
- **Never** pass a client *name*, EIN, account number, or any identifier to `vr-cohort`. The id
  is always a one-way hash: `client_hash = sha256(firm_salt + client_id)[:16]`. Keep `firm_salt`
  in `home/cohort/salt` (created once, never committed, never logged).
- The cohort store holds only `(naics, metric, value, client_hash, period)` — numbers, not books.
- A score you read back is a *position* ("3.2 sigma high"), not another client's figure. When you
  report it, describe the cohort in aggregate ("your 14 retail clients"), never name a peer.
- With fewer than the minimum cohort size, **do not score** — report "insufficient peers (n=4)"
  rather than a number that could fingerprint one client. Treat n<8 as not-yet-benchmarkable.

## The metrics (compute these five each cycle)
Pull real numbers from `quickbooks` (`qb_pnl_report`, `qb_ar_aging`, `qb_balance_sheet_report`)
or `vr-ledger` (`income_statement`, `balance_sheet`) — tools first, memory never. Use `Decimal`,
not floats.
- **gross_margin** = (revenue - COGS) / revenue
- **payroll_pct** = total payroll / revenue
- **dso** = (accounts receivable / revenue) * days-in-period
- **rent_pct** = rent expense / revenue
- **owner_comp_ratio** = owner compensation / revenue
Express ratios as decimals (0.0–1.0) consistently so cohorts stay comparable. Record the period
and the source report in a workpaper note for each figure (see QC below).

## The vr-cohort MCP (only these three tools for this server)
1. **`add_observation(naics, metric, value, client_hash)`** — record one metric for one client
   into its NAICS peer pool. Call it once per metric per close. Re-feeding the same client/metric
   updates that client's contribution (idempotent on `client_hash`), so re-running a close does
   not double-count.
2. **`cohort_stats(naics, metric)`** — return the peer-pool summary for a metric (n, mean, stdev,
   median, quartiles). Use it to confirm the cohort is large enough and to describe the peer set.
3. **`score(naics, metric, value)`** — position one client's value in its cohort: z-score / sigma,
   percentile, and the in/out-of-band call. This is what flags outliers.

Argument shape: tools take JSON-string args (e.g. `add_observation('{"naics":"448140",
"metric":"payroll_pct","value":0.41,"client_hash":"a3f9c1d20b8e4f56"}')`) and return concise JSON.

## The loop (run at each close / review)
1. **Resolve NAICS** for the client from `client-context`; default to the 6-digit code, fall back
   to the 4- or 3-digit parent if the 6-digit cohort is too thin.
2. **Compute** the five metrics from the tools. Sanity-check (margins in [-1,1], no divide-by-zero
   revenue) before you trust them.
3. **Hash** the client id with the firm salt.
4. **`add_observation`** each metric — this client now contributes to the pool.
5. **`cohort_stats`** each metric. If n is below the floor, mark "insufficient peers" and skip
   scoring for that metric.
6. **`score`** each metric for this client's value. Anything beyond +/-2 sigma (or outside the
   inter-quartile band by a wide margin) is an **outlier** — flag it.
7. **Narrate** the outliers for the advisory write-up: direction, magnitude in sigma/percentile,
   and the cohort in aggregate. "Owner comp is 0.9 sigma — normal. Payroll is 3.2 sigma above your
   14 retail clients; worth a labor-efficiency look."

## Reading the signal (judgment, not just z-scores)
- High sigma is a **question, not a verdict** — a 3-sigma DSO might be a genuine collections
  problem or a one-off large receivable. Look before you conclude.
- Direction matters: high margin is usually good, high payroll-% usually isn't; say which.
- A *cluster* of mild outliers (margin low + payroll high + owner-comp high) tells a story a single
  metric won't. Read them together.
- Cohorts drift — a metric that was 2 sigma last year may be the new normal as the pool grows.
  Re-score against the current pool, not a remembered number.

## Authority & deception
- Computing metrics, feeding the cohort, and reading scores back **internally** are **GREEN**.
- Any peer comparison that reaches a **client deliverable** (deck, memo, QBR) is **RED** — route
  through `self-review-qc` and Valentino's review/name before it goes out. Never present a
  benchmark as audited or as a public industry standard when it's the firm's internal pool; label
  it "firm peer set (n=__)". The no-client-deception line is invariant.
- If a YELLOW judgment call arises (NAICS ambiguous, cohort borderline-thin, a metric that looks
  wrong), surface it rather than guessing.

## Workpaper & QC
For every cycle, leave a note under `home/cohort/`: per metric, the value, the source tool +
report + period, the NAICS used, the cohort n, and the score. Record the salt's existence (never
its value). On re-runs, confirm observations are idempotent (no double-count) and that no client
identifier ever appears in the cohort store or logs. Cross-link: the numbers → `financial-statement-prep`
and `month-end-close`; the client/industry facts → `client-context`; turning a flag into advice →
`consulting`.
