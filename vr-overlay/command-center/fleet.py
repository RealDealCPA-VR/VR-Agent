"""
RealDeal CPA Command Center — agent-fleet data layer (framework-agnostic).

Loads/persists the fleet (agents + work-flow edges + live work items), and exposes
the operations the Command Center tab needs: add an agent, change an agent's model,
remove an agent, and list the available models/skills/tools for the add-agent form.

The backend web route is a thin layer over these functions. Runtime state lives at
$HERMES_HOME/command-center/fleet.json, seeded from fleet.seed.json on first use.
The running agent updates the live `work`/`status` fields at runtime; until then the
seed provides an illustrative populated canvas.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

_THIS = Path(__file__).resolve()
# HERMES_HOME is authoritative (the dashboard always sets it). Fall back to the
# repo-local home when running this module directly from vr-overlay/command-center.
HOME = Path(os.environ.get("HERMES_HOME") or (_THIS.parents[2] / "home"))
ROOT = HOME.parent                               # .../VRAGENT (holds vr-overlay/)
SEED = _THIS.parent / "fleet.seed.json"          # ships next to this module
STATE_DIR = HOME / "command-center"
STATE = STATE_DIR / "fleet.json"

_SLUG = re.compile(r"[^a-z0-9]+")
_STATUSES = ("idle", "queued", "running", "blocked", "review", "done")

# Curated default models offered in the add-agent / change-model picker. The live
# config model + anything already on an agent are merged in by available_models().
_DEFAULT_MODELS = [
    "anthropic/claude-opus-4.5",
    "anthropic/claude-sonnet-4.6",
    "anthropic/claude-haiku-4.5",
    "openai/gpt-5",
    "google/gemini-3-pro",
    "google/gemini-3-flash",
    "deepseek/deepseek-r1",
    "x-ai/grok-4",
]


def _read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def load() -> dict:
    """Return the live fleet, seeding from fleet.seed.json on first use."""
    if STATE.exists():
        return _read_json(STATE)
    fleet = _read_json(SEED)
    save(fleet)
    return fleet


def save(fleet: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(fleet, indent=2), encoding="utf-8")


def _slug(name: str, existing: set) -> str:
    base = _SLUG.sub("-", name.strip().lower()).strip("-") or "agent"
    s, i = base, 2
    while s in existing:
        s, i = f"{base}-{i}", i + 1
    return s


def add_agent(name: str, role: str = "", model: str = "", skills=None, tools=None) -> dict:
    """Create a new specialized agent node and persist it."""
    fleet = load()
    ids = {a["id"] for a in fleet["agents"]}
    aid = _slug(name, ids)
    # lay it out below the existing left column so it's visible immediately
    ys = [a.get("y", 0) for a in fleet["agents"] if a.get("x", 0) < 300]
    agent = {
        "id": aid, "name": name.strip() or aid, "role": role.strip(), "kind": "agent",
        "model": model or "", "status": "idle", "task": None,
        "skills": list(skills or []), "tools": list(tools or []),
        "x": 120, "y": (max(ys) + 180) if ys else 60,
    }
    fleet["agents"].append(agent)
    fleet.setdefault("edges", []).append({"from": aid, "to": "remy", "label": "prepared work"})
    save(fleet)
    return agent


def update_agent(agent_id: str, **changes) -> dict | None:
    """Patch an agent (e.g. model, status, task, skills, tools, x, y, name, role)."""
    fleet = load()
    allowed = {"name", "role", "model", "status", "task", "skills", "tools", "x", "y"}
    for a in fleet["agents"]:
        if a["id"] == agent_id:
            for k, v in changes.items():
                if k in allowed:
                    a[k] = v
            save(fleet)
            return a
    return None


def remove_agent(agent_id: str) -> bool:
    if agent_id in ("remy", "partner"):
        return False  # the lead + the human partner are not removable
    fleet = load()
    before = len(fleet["agents"])
    fleet["agents"] = [a for a in fleet["agents"] if a["id"] != agent_id]
    fleet["edges"] = [e for e in fleet.get("edges", [])
                      if e["from"] != agent_id and e["to"] != agent_id]
    fleet["work"] = [w for w in fleet.get("work", []) if w.get("agent") != agent_id]
    if len(fleet["agents"]) != before:
        save(fleet)
        return True
    return False


def reset() -> dict:
    """Re-seed from the default fleet (discards UI changes)."""
    fleet = _read_json(SEED)
    save(fleet)
    return fleet


# ---- options for the add-agent / change-model form (real data) -------------
def available_skills() -> list[str]:
    base = ROOT / "vr-overlay" / "skills"
    out = set()
    if base.exists():
        for sk in base.rglob("SKILL.md"):
            out.add(sk.parent.name)
    return sorted(out)


def available_tools() -> list[str]:
    """MCP servers from config + the headline built-in toolsets."""
    tools = ["browser", "web_search", "desktop", "terminal", "code_execution"]
    tmpl = ROOT / "vr-overlay" / "config" / "config.yaml.tmpl"
    if tmpl.exists():
        txt = tmpl.read_text(encoding="utf-8")
        m = re.search(r"^mcp_servers:\s*$(.*?)^\S", txt, re.S | re.M)
        block = m.group(1) if m else txt
        for name in re.findall(r"^\s{2}([a-z][a-z0-9-]+):\s*$", block, re.M):
            if name not in tools:
                tools.append(name)
    return tools


def available_models() -> list[str]:
    models = list(_DEFAULT_MODELS)
    # merge the configured default + any model already assigned to an agent
    tmpl = ROOT / "vr-overlay" / "config" / "config.yaml.tmpl"
    if tmpl.exists():
        m = re.search(r'^\s*default:\s*"([^"]+)"', tmpl.read_text(encoding="utf-8"), re.M)
        if m and m.group(1) not in models:
            models.insert(0, m.group(1))
    try:
        for a in load().get("agents", []):
            if a.get("model") and a["model"] not in models:
                models.append(a["model"])
    except Exception:
        pass
    return models


def options() -> dict:
    return {"models": available_models(), "skills": available_skills(),
            "tools": available_tools(), "statuses": list(_STATUSES)}


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "load"
    if cmd == "options":
        print(json.dumps(options(), indent=2))
    else:
        print(json.dumps(load(), indent=2))
