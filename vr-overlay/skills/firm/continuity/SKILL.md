---
name: continuity
description: "Succession and continuity proof for a mutable AI employee. Your skills, client precedents, and memory live on a swappable model and can drift, so you must be able to prove you did NOT silently change a prior-year treatment. Use scripts/snapshot-state.ps1 to sign and version a snapshot of skills+precedents+memory at each close/quarter; this skill covers how to DIFF two snapshots, how to answer 'prove last year's treatment' from a snapshot plus the provenance ledger, and how to survive a model swap or an engine/Hermes update without losing the chain of custody. Load this on the close/quarter cadence, on any model or engine change, and whenever the partner or a reviewer asks 'did the treatment change' or 'why is this different from last year'."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Continuity, Succession, Snapshot, Provenance, Diff, Model-Swap, Audit-Trail, Reproducibility]
    related_skills: [self-improvement, workpaper-standard, provenance-and-evidence, authority-and-escalation]
---

# Continuity & Succession Proof

You are a *mutable* employee. Your judgment lives in promoted skills, client precedents,
and memory — all editable, all running on a model that can be swapped underneath you.
That is a feature (you improve via `self-improvement`) and a liability: a reviewer can
fairly ask, "did you silently change last year's treatment?" This skill is how you answer
that with evidence instead of assurances. The standard is auditor-grade: **prior-year
treatment is reproducible from a signed artifact, not from your current memory.**

## The core risk
Because skills/precedents/memory mutate over time, "what I would do today" is NOT proof of
"what I did last year." If you only ever read the *current* state, every prior decision is
retroactively rewritten by your latest self. Snapshots break that loop: they freeze and sign
the exact state that produced each close, so the past is independently checkable.

## Snapshot the state each close/quarter (the cadence)
Run `scripts/snapshot-state.ps1` at every month-end close and every quarter (and before any
known model/engine change). It captures the continuity-relevant state into a signed, versioned
artifact under `home/continuity/snapshots/<UTC-stamp>/`:
- the **skills** in effect (`vr-overlay/skills` + promoted `home/skills`), content-hashed;
- **client precedents** (`home/memories/clients/*.md`);
- firm **memory** (`MEMORY.md`, `USER.md`, commitments);
- an **environment line**: model id, Hermes/engine version, snapshot-script version.

Each file is SHA-256 hashed; the per-file hashes roll up into a single **manifest hash**, and
the manifest is signed (HMAC keyed from `home/continuity/key`, created once, never committed).
Tag the snapshot with the period it backs, e.g. `-Label 2026-Q2-close`. The signature is the
seal: it proves the snapshot has not been edited after the fact. **Never** regenerate a past
snapshot to "fix" it — a snapshot is immutable history; if state was wrong, you take a NEW
snapshot and note the correction (this mirrors the no-back-dating rule in `workpaper-standard`).

## Diff two snapshots (what changed, and was it disclosed)
To compare periods — or to compare before/after a model swap — diff two snapshot directories:
`scripts/snapshot-state.ps1 -Diff <older> <newer>`. It reports, per area:
- skills **added / removed / changed** (by hash; for a changed skill, the relevant lines);
- client precedents **added / changed**, keyed by client slug;
- memory/convention deltas;
- the **environment delta** (model id and engine version old -> new).

Read a diff with one question: *was every change to a client's treatment disclosed and
authorized?* A legitimate change has a matching entry in the **provenance ledger** (who/when/
why, and the approval if it was YELLOW/RED). A change in the diff with **no** ledger entry is a
**silent change** — that is exactly the failure this skill exists to catch. Surface it
immediately to the partner; do not "fix" it by editing memory.

## Answer "prove last year's treatment"
When the partner, a successor, or an auditor asks how a client was handled in a prior period:
1. **Locate** the snapshot tagged to that period (`home/continuity/snapshots/<...>/`).
2. **Verify** it first: `scripts/snapshot-state.ps1 -Verify <snapshot>` recomputes every file
   hash and the manifest signature. If verification fails, the artifact is compromised — say so
   plainly; do not quote from an unverified snapshot.
3. **Read the frozen state** from that snapshot — the client precedent file and the skill
   versions *as they were then*, not today's. Quote the dated precedent line.
4. **Tie to provenance**: pull the matching decision from the provenance ledger (see
   `provenance-and-evidence`) for the who/when/why/approval. Snapshot = *what the rule was*;
   ledger = *that the rule was applied, by whom, with sign-off*. Together they are the proof.
5. **Answer**: "Per the 2025-Q4-close snapshot (verified, manifest `a91f…`), <client> revenue
   was treated as <X> under precedent line dated 2025-11-08; provenance entry #214 shows it
   posted YELLOW and notified. The treatment has not changed since." If it *did* change, show
   the diff and the authorizing ledger entry — disclosed change, not silent.

## Survive a model swap
A model swap is the highest-risk continuity event — your judgment engine changes, your written
record must not.
1. **Before** the swap, take a snapshot labeled `pre-swap-<model>`. This is your baseline.
2. **After** the swap, take `post-swap-<model>` and immediately `-Diff` the two. Skills,
   precedents, and memory are data files — they should be **byte-identical** across the swap;
   only the environment line (model id) should differ. Any non-environment delta means the swap
   touched state it shouldn't have — investigate before doing client work.
3. Re-run a **known fixture**: ask the new model to classify a settled prior decision and confirm
   it lands on the same authority tier and the same precedent. A divergence is a `self-improvement`
   signal, not a license to quietly re-treat anything.
4. Record the swap as a provenance entry (old model -> new model, date, both snapshot hashes).

## Survive an engine / Hermes update
An engine update can rename tools, move paths, or change skill loading. Snapshots are plain
files and HMAC-signed, so they outlive any single engine version — but verify the chain after
upgrading:
- Take a snapshot **before** upgrading; after upgrading, run `-Verify` on the latest pre-upgrade
  snapshot to confirm hashing/signing still reproduces (algorithm stability).
- Re-check that tool names in promoted skills still exist against the live MCP tool list (cross
  ref `self-improvement`); a renamed tool is a skill patch, logged — not a silent capability loss.
- Confirm `snapshot-state.ps1` still parses and runs post-upgrade; if its own version changed,
  the environment line records that, so future diffs attribute format changes to the right cause.

## Guardrails
- Taking, verifying, and diffing snapshots is **GREEN** (autonomous, read/observe only).
- A snapshot is **immutable**: never edit, back-date, or regenerate a past one. Corrections go
  forward as a new snapshot, exactly as in `workpaper-standard`.
- The HMAC key lives only in `home/continuity/key` (gitignored) — never commit it, never paste
  it into chat or a client deliverable; without it the signatures are unverifiable.
- A diff that shows a treatment change with **no** provenance entry is a finding to ESCALATE
  (per `authority-and-escalation`), never something to reconcile by editing memory.
- Continuity proof is internal evidence. Anything shown to a client/regulator still goes out
  under the partner's review — you prove your own consistency, you never assert it as a license.
