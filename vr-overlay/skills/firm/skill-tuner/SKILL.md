---
name: skill-tuner
description: "Optimize RealDeal CPA for the LLM in use. When the partner switches models (or asks to 'tune/optimize for <model>', 'I'm using a smaller/local model', 'make it work better on X'), match the model to a tier and apply the right reasoning effort, autonomy budget, and skill style — config-only by default, with an optional deep re-tune of the skill text. Fully reversible."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Optimization, Models, Tuning, Reasoning-Effort, Skills, Config]
    related_skills: [self-improvement]
---

# Skill Tuner — optimize for the chosen LLM

Different models need different handling. A frontier reasoner does best with lean,
principle-first skills and long autonomy; a small or local model needs explicit
micro-steps, tighter loops, and lower reasoning effort. This skill offers that as an
**option** — it never changes anything until asked.

## When to use
- The partner switched the model (`vragent.ps1 model`) or said which model they're running.
- They ask to "optimize/tune for <model>", "I'm on a smaller/local model", or "why is it slow/over-thinking".

## The tool
`scripts/optimize-skills.ps1` reads `vr-overlay/config/model-profiles.yaml`, matches the
active model to a **tier** (frontier / strong / mid / small), and applies that tier's
settings. Run it from the repo root.

| Invocation | Effect |
|---|---|
| `.\scripts\optimize-skills.ps1` | **Offer only** — prints the active model, its tier, and the exact changes it *would* make. No change. |
| `.\scripts\optimize-skills.ps1 -Model <name>` | Offer for a specific model (e.g. before you switch). |
| `.\scripts\optimize-skills.ps1 -Apply` | Apply the config tuning: set `model.default`, `agent.reasoning_effort`, `agent.max_turns` for the tier, then re-sync. |
| `.\scripts\optimize-skills.ps1 -Apply -Deep` | Also fan out a re-tune of the skill *text* to the tier's style (lean / scaffolded / explicit). Writes reversible overrides to `home/skills/` (delete them to revert). |
| `.\scripts\optimize-skills.ps1 -Revert` | Remove any deep-tune overrides and restore the canonical skills. |

## What each tier changes (config)
- **reasoning_effort** — high for frontier/strong, medium for mid, low for small.
- **max_turns** — longer autonomy for stronger models, tighter loops for smaller ones.
- **skill_style** (deep mode) — lean / scaffolded / explicit guidance density.

## How to run it as the agent
1. Get the active model: read `model.default` in the config (or what the partner names).
2. Run the **offer** first (no `-Apply`) and show the partner what it would change.
3. If they approve, run with `-Apply` (add `-Deep` only if they want the skill text re-tuned
   for a notably weaker/smaller model).
4. Confirm with `vragent.ps1 doctor` and a quick `skills list`.

## Guardrails
- Default is **offer-only**; never apply tuning without the partner's go-ahead or an explicit `-Apply`.
- The deep re-tune writes *overrides*, never touching the tracked canonical skills — `-Revert` undoes it.
- Tuning changes *how* skills are delivered, never the **authority gates** or the accounting correctness.
