# RealDeal CPA — Claude Code Build (design docs)

This folder is a **self-contained design package** for re-platforming the RealDeal CPA
agent off the Hermes framework and onto **Claude Code** as its runtime — so it can be
powered by a **Claude Max subscription** instead of a metered Anthropic API key.

These are **planning documents for a future build**, not code. Nothing here changes the
current (Hermes-based) project. Move this folder wherever you want to start the new build.

## Why this exists
The current agent runs on NousResearch's Hermes framework, which calls the Anthropic
**API** (API key, pay-per-token). A Claude subscription **cannot** legitimately power Hermes
(that's a ToS violation). The *only* sanctioned way to run a custom agent on your
subscription is to build it on **Claude Code** itself. This package specs that rebuild.

## What's the punchline
Most of the value **ports cleanly**: the 9 MCP tool servers move 1:1 (standard MCP), and
the 47 custom skills move with light frontmatter edits. The authority gates actually get
*stronger* (deterministic hooks instead of prompt instructions). The main rebuild is the
**Command Center** UI (its canvas is reusable; its backend is rewritten). You trade
per-token API billing for subscription **usage limits**.

## Read in this order
1. **[PRD.md](./PRD.md)** — what we're building and why (product vision, users, goals,
   non-goals, success criteria, the subscription-vs-API decision).
2. **[INVENTORY-AND-PORT-MAP.md](./INVENTORY-AND-PORT-MAP.md)** — exactly what exists today
   and where each piece lands (ports clean / rebuilt / dropped), with effort estimates.
3. **[BUILD-SPEC.md](./BUILD-SPEC.md)** — the technical architecture + a phased build plan,
   with the exact Claude Code config formats (MCP, skills, subagents, hooks, headless,
   plugin packaging).
4. **[COMPLIANCE.md](./COMPLIANCE.md)** — the legal/usage basis for running this on a Max
   subscription, the boundary you must not cross, and the sources.

## Status & provenance
- Authored 2026-06-23 against Claude Code's then-current extension model (docs linked in
  BUILD-SPEC and COMPLIANCE). **Verify the specifics against the live docs before building**
  — Claude Code evolves; a few details (plugin versioning, tool-search defaults) were noted
  as in-flux at authoring time.
- The source of truth for *what the agent does* is the current Hermes build in the parent
  project (`vr-overlay/`). This package describes how to reproduce that behavior on Claude
  Code — same capabilities, new runtime.

## One-line vision
> A senior-accountant AI teammate ("Remy") for one CPA firm's internal use — accounting,
> tax, bookkeeping, advisory, marketing — that sees and drives the desktop, browses the web,
> proves its math deterministically, keeps a tamper-evident audit trail, and runs on a Claude
> Max subscription.
