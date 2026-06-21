---
name: glassbox
description: "Radical traceability for every client-facing figure: one click takes a reviewer from the number on the deliverable, through the workpaper index, to the exact tool calls that produced it, to the source document, down to the bank line it came from. Backed by the vr-provenance hash-chained ledger and content-addressed evidence bundles, rendered into a single self-contained traceable HTML dossier by scripts/glassbox-report.ps1. Treats AI-vs-human provenance as a FEATURE shown on the report's face (who ACTED = agent, who AUTHORIZED = named human), never as a footnote to bury. Load this when assembling a support package, a partner/peer-review/exam request, or any client deliverable that must be defensible line by line. The rendered report is an AI-prepared DRAFT that stays under human review and is labeled as such before any client-facing release — the hard guardrail, by construction."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Glassbox, Traceability, Provenance, Evidence, Hash-Chain, Disclosure, One-Click-Trace, Quality-Control]
    related_skills: [provenance-and-evidence, workpaper-standard, communication-cadence, authority-and-escalation]
---

# Glassbox

A black box asks the client to *trust* the number. A glass box lets them *check* it.
Every figure a client sees should trace — in one click — from the deliverable, through
the workpaper that supports it, to the tool calls that produced it, to the source
document, all the way down to the bank line. That unbroken chain is the product. When a
partner, a peer reviewer, or an IRS examiner points at a number and asks "where did this
come from?", the answer is a link, not a meeting.

This skill is the *assembly and presentation* layer on top of `provenance-and-evidence`.
That skill records the evidence (`record_read`, `append_event`, `verify_chain`,
`build_dossier`). This skill turns the dossier into a human- and exam-readable artifact
and holds the line on disclosure and human review.

## The trace, end to end
The click-path you are building and proving:

1. **Figure** on the client deliverable (a P&L line, a recon balance, a tax number).
2. **Workpaper index** that supports it (`A-1`, `PR-3`, …) per `workpaper-standard`.
3. **Tool calls** that produced it — the `append_event` records in the hash-chained
   ledger (e.g. `qb_journal_entry_create`, `qb_general_ledger`, a `validate`/`balance_of`).
4. **Source document** — the `record_read` evidence bundle (statement, invoice #, report
   run + parameters, screenshot path), content-addressed by sha256.
5. **Bank line** — the literal transaction the source resolves to.

If any link is missing, the figure is *unsupported* and does not go to the client until it
is sourced. "I looked at QB" is not a link; the read + its parameters + the value taken is.

## When to use
- You are assembling a **support package** for a client/period (close binder, recon pack,
  tax workpapers) and want every number defensible to its source.
- A **partner, peer reviewer, or regulator/exam** asks for the trail behind a deliverable.
- Before any **client-facing release** that presents firm-prepared figures — to verify the
  chain is intact and the disclosure labeling is correct first.
- During the **close wrap / standup sweep**, to re-verify integrity on cadence.

## Build the dossier, then render it
1. Confirm the evidence exists. Per `provenance-and-evidence`: every input was
   `record_read`, every consequential action `append_event`'d, in order.
2. **`verify_chain` FIRST.** A report over an unverified chain is false comfort. A *failing*
   verify is a stop-the-line RED escalation to the human partner — never "repair" history to
   make it re-verify.
3. **`build_dossier(client, period)`** to assemble the chain + evidence index into
   `home/provenance/dossiers/<client>-<period>.json`.
4. **Render** with `scripts/glassbox-report.ps1 -Client <c> -Period <p>`. It reads the
   dossier, the ledger, and the evidence bundles, **independently re-links the hash chain on
   render** (it does not take the dossier's word for integrity), and writes a single
   self-contained, offline-renderable HTML to `home/provenance/reports/<client>-<period>.html`.
   No external assets — it survives being emailed or printed to PDF.
5. **Cross-reference** the rendered report back to the workpaper indexes so the narrative
   (`workpaper-standard`) and the evidence line up — the report supports the workpaper, it
   does not replace it.

## Disclosure is a feature, on the report's face (the hard guardrail, by construction)
The no-client-deception line is INVARIANT and the report *shows* it rather than asserting it.
Each event renders two columns:
- **AI prepared** — who ACTED. The agent. Always.
- **Human authorized** — who AUTHORIZED. For a GREEN autonomous action, "Auto (GREEN
  authority)". For a RED money/filing/material action, the **named human partner** who signed
  off. A YELLOW or unsigned consequential item renders as **"PENDING HUMAN"** in alarm color.

That separation is the selling point to an exam or peer-review team, not a liability. A row
that reads "PENDING HUMAN" must never be presented to a client as authorized firm work. You
never relabel an agent-performed step to look human-performed, and you never backdate or
reword an event to clean up the picture — that defeats the entire chain and is the cardinal
sin here.

## The report is a DRAFT under human review
The rendered HTML is watermarked **"DRAFT — AI-prepared — pending human review & sign-off."**
It is internal support and a partner deliverable by default. It goes to a **client** only
after the human partner has reviewed and signed off, and then only labeled per firm policy
(`communication-cadence`). When unsure whether an artifact is client-facing, treat it as
client-facing. The traceability is what *earns* the client's trust honestly — do not trade
that away by implying a licensed human did what the agent did.

## Procedure
1. Scope the request: which client, which period, which deliverable's figures.
2. Per `provenance-and-evidence`, ensure reads + events are complete and in order.
3. `verify_chain` — pass before proceeding; fail = RED stop-the-line to the partner.
4. `build_dossier(client, period)`.
5. `scripts/glassbox-report.ps1 -Client <c> -Period <p>` → self-contained HTML.
6. Spot-check the click-path on 2–3 hero figures: figure → workpaper → event → read → line.
7. Confirm every consequential row is correctly attributed (agent acted / human authorized);
   resolve any "PENDING HUMAN" before client release.
8. Route to the partner for review; release to client only post-sign-off and labeled.

## Edge cases / pitfalls a 15-year CPA knows cold
- **Integrity != accuracy.** A green chain proves the record wasn't *altered*; it does not
  prove the number is *right*. The workpaper tie-outs carry accuracy; this carries provenance.
  Never let a clean chain banner substitute for a real review.
- **An action without its source read** is an unsupportable event — the reviewer can't re-pull
  the number. Read-first, always; fix the gap before rendering, don't paper over it.
- **A stale read** (parameters that don't match the period) is a silent error. Re-run and
  re-record; don't reuse.
- **Rendering before verifying** ships a dossier whose integrity is unconfirmed. `verify_chain`
  immediately before `build_dossier`, every time.
- **"PENDING HUMAN" left in a client copy** is a disclosure failure. Clear it (get the sign-off)
  or pull the figure; never ship it as authorized.
- The report is **discoverable evidence**: write only supportable, professional event text
  (Circular 230 conduct), the same standard as a workpaper.
- This machine may lack ffmpeg/extra tooling, but the report is **pure stdlib HTML** — it
  renders and prints anywhere, with no external dependency.

## Required output
- **Trace note** — client + period, that `verify_chain` passed first, the report path, and the
  workpaper indexes it cross-references.
- **Provenance summary** — count of events and evidence bundles, and that each consequential
  row is correctly attributed (agent prepared / human authorized).
- **EXCEPTIONS QUEUE** — any broken chain, missing source, or unresolved "PENDING HUMAN" as a
  RED item for the partner; state "none" explicitly if clean.

## Approval gate
GREEN (autonomous): building dossiers, rendering reports, re-verifying the chain, cross-
referencing workpapers — making the work traceable is always free to do, relentlessly. RED:
the underlying actions the report *documents* (posting material/unusual JEs, moving money,
filing) still need the human partner's authorization, and **any client-facing release of the
report** is gated on the partner's review and sign-off. A failed `verify_chain` is a stop-the-
line RED escalation. Never weaken the disclosure labeling to make a client copy read cleaner.
