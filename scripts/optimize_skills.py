#!/usr/bin/env python
"""
Optimize RealDeal CPA for the chosen LLM.

Reads vr-overlay/config/model-profiles.yaml, matches the active model to a tier,
and (with --apply) tunes config.yaml.tmpl (reasoning_effort, max_turns, optionally
model.default) and writes a tier "skill-style" directive that sync-overlay appends to
the agent's persona so every skill is delivered in the right style for that model.

Offer-only by default — nothing changes without --apply. Reversible with --revert.

Usage (normally via scripts/optimize-skills.ps1):
  python optimize_skills.py                  # offer for the current model
  python optimize_skills.py --model <name>   # offer for a specific model
  python optimize_skills.py --apply [--model <name>]
  python optimize_skills.py --revert
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TMPL = ROOT / "vr-overlay" / "config" / "config.yaml.tmpl"
PROFILES = ROOT / "vr-overlay" / "config" / "model-profiles.yaml"
STYLE_OUT = ROOT / "vr-overlay" / "config" / "model-style.md"


def load_profiles():
    import yaml
    return yaml.safe_load(PROFILES.read_text(encoding="utf-8"))


def active_model() -> str:
    m = re.search(r'^\s*default:\s*"([^"]+)"', TMPL.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else "(unknown)"


def match_tier(model: str, profiles: dict) -> str:
    ml = model.lower()
    for tier, cfg in profiles["tiers"].items():
        for pat in cfg.get("match", []):
            if str(pat).lower() in ml:
                return tier
    return profiles.get("default_tier", "strong")


def set_yaml_scalar(text: str, key: str, value, section: str | None = None) -> str:
    """Replace `  key: ...` (optionally within a top-level `section:`) with the new value."""
    quoted = f'"{value}"' if isinstance(value, str) else str(value)
    pat = re.compile(rf'^(\s*){re.escape(key)}:\s*.*$', re.M)
    repl_done = {"n": 0}

    def repl(m):
        repl_done["n"] += 1
        return f'{m.group(1)}{key}: {quoted}'

    if section:
        # operate only within the section block
        sm = re.search(rf'^{re.escape(section)}:\s*$', text, re.M)
        if sm:
            start = sm.end()
            nxt = re.search(r'^\S', text[start:], re.M)
            end = start + (nxt.start() if nxt else len(text) - start)
            block = pat.sub(repl, text[start:end], count=1)
            return text[:start] + block + text[end:]
    return pat.sub(repl, text, count=1)


STYLE_HEADER = "## Active-model skill style (managed by optimize-skills)"


def write_style(profiles: dict, model: str, tier: str):
    style = profiles["tiers"][tier]["skill_style"]
    guidance = profiles["skill_styles"][style]
    STYLE_OUT.write_text(
        f"{STYLE_HEADER}\n"
        f"You are currently running on **{model}** (tier: **{tier}**, style: **{style}**).\n"
        f"Apply every skill in this style: {guidance}\n"
        f"This shapes *delivery only* -- never relax the authority gates or accounting correctness.\n",
        encoding="utf-8",
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--revert", action="store_true")
    a = ap.parse_args()

    profiles = load_profiles()

    if a.revert:
        if STYLE_OUT.exists():
            STYLE_OUT.unlink()
            print("reverted: removed model-style directive. Re-run sync-overlay.ps1.")
        else:
            print("nothing to revert (no model-style directive).")
        return

    model = a.model or active_model()
    tier = match_tier(model, profiles)
    t = profiles["tiers"][tier]
    print(f"Active model : {model}")
    print(f"Matched tier : {tier}  ({t['note']})")
    print(f"  reasoning_effort -> {t['reasoning_effort']}")
    print(f"  max_turns        -> {t['max_turns']}")
    print(f"  skill style      -> {t['skill_style']}")

    if not a.apply:
        print("\n(offer only) Re-run with -Apply to apply these settings.")
        return

    text = TMPL.read_text(encoding="utf-8")
    text = set_yaml_scalar(text, "reasoning_effort", t["reasoning_effort"], section="agent")
    text = set_yaml_scalar(text, "max_turns", t["max_turns"], section="agent")
    if a.model:
        text = set_yaml_scalar(text, "default", a.model, section="model")
    TMPL.write_text(text, encoding="utf-8")
    write_style(profiles, model, tier)
    print(f"\nAPPLIED to config.yaml.tmpl (+ model-style.md for tier '{tier}').")
    print("Run sync-overlay.ps1 to render it into home/.")


if __name__ == "__main__":
    main()
