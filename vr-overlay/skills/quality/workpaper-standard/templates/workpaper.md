# Workpaper <Index> — <Title>

| Field | Value |
|---|---|
| **Index** | <e.g. A-1> |
| **Purpose** | <one sentence: what this workpaper proves> |
| **Client** | <Legal name> — KarbonCopy id: <KC-#####> |
| **Period** | <e.g. FYE 12/31/2025> — Basis: <cash / accrual> |
| **Preparer** | RealDeal CPA (agent) |
| **Date prepared** | <YYYY-MM-DD> |
| **Reviewer** | _(blank — partner sign-off required, RED gate)_ |
| **Review date** | |

## 1. Source documents
List every input. A reviewer must be able to re-pull each.

- QB company file: <name> (confirmed via `qb_session_status` + `qb_company_info` on <date>)
- QB report(s): <e.g. `qb_trial_balance_export`> — date range <…>, basis <…>, run <YYYY-MM-DD>
- Statement(s): <bank/CC name>, statement date <…>, ending balance <$…>
- Documents: <invoice #, bill #, W-9, contract, file path>
- Portal/screenshot: <portal, file path, date> (`desktop`/`browser`)

## 2. Procedures performed
Steps in order, with the exact tools/parameters used.

1. <step> — tool: <`qb_…` / vr-ledger `…`> — params: <…>
2. <step> …
3. …

## 3. Tie-outs / ticks
Tick legend: TB=agreed to TB/GL · B=agreed to statement · F=footed · PY=prior year · R=recomputed · CF=cross-ref · X=exception.

| Item | Amount (A) | Tied to | Amount (B) | Difference | Tick |
|---|---:|---|---:|---:|:--:|
| <e.g. Cash per GL> | 0.00 | <bank statement> | 0.00 | 0.00 | B |
| <…> | | | | | |

_Footing:_ <columns/rows re-added — F> · _Recomputations:_ <estimate recomputed — R>

## 4. Conclusion
<Bottom line. Claim only what the ties support.>

## 5. Exceptions / open items
Route material, unusual, or ambiguous items here (and to the EXCEPTIONS QUEUE). Do not resolve by assumption.

- [ ] <X> <description> — amount <$…> — proposed treatment / question for partner — CF <WP index>
- _(or: None.)_

## 6. References / cross-references
- This WP index: <A-1>
- Related WPs: <CF: …>
- Prior-period WP: <PY: path/index>
- Authority: <IRC §…, Treas. Reg. §…, ASC …, Form …> — or "verify current-year"
