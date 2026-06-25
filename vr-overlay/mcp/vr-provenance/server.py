"""
VRAGENT vr-provenance MCP server.

Tamper-evident provenance for the AI accounting employee: content-addressed
evidence bundles, a hash-chained append-only ledger, chain verification, and
per-client/period dossier assembly. Pure stdlib — no external service, no
wall-clock dependency (callers pass timestamps inside their event payloads).

Registered in config.yaml under mcp_servers.vr-provenance. Runs over stdio.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("vr-provenance")

ROOT = Path(os.environ.get("HERMES_HOME") or (Path(__file__).resolve().parents[3] / "home")) / "provenance"
EVIDENCE_DIR = ROOT / "evidence"
DOSSIER_DIR = ROOT / "dossiers"
LEDGER_PATH = ROOT / "ledger.jsonl"
GENESIS = "0" * 64


def _ensure_dirs() -> None:
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    os.makedirs(DOSSIER_DIR, exist_ok=True)


def _canonical(obj) -> str:
    """Deterministic JSON: sorted keys, no insignificant whitespace."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _link_hash(prev_hash: str, event) -> str:
    """Chain link: sha256(prev_hash + canonical_json(event))."""
    return _sha256(prev_hash + _canonical(event))


def _read_ledger() -> list[dict]:
    if not LEDGER_PATH.exists():
        return []
    lines = []
    for raw in LEDGER_PATH.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if raw:
            lines.append(json.loads(raw))
    return lines


def _ledger_head() -> tuple[str, int]:
    """Return (prev_hash, next_seq) from the last ledger line without re-parsing
    the whole chain. O(1)-ish: reads the file and json.loads only the last
    non-blank line. Genesis -> (GENESIS, 0). Preserves the exact hash-chain
    semantics verify_chain() recomputes."""
    if not LEDGER_PATH.exists():
        return GENESIS, 0
    text = LEDGER_PATH.read_text(encoding="utf-8")
    for raw in reversed(text.splitlines()):
        raw = raw.strip()
        if raw:
            last = json.loads(raw)
            return last["hash"], last["seq"] + 1
    return GENESIS, 0


def _json(obj) -> str:
    return json.dumps(obj, indent=2, default=str)


@mcp.tool()
def record_read(source: str, content: str) -> str:
    """Record that a source was read. SHA-256s the content and writes an evidence
    bundle (source, sha256, length) under home/provenance/evidence/<sha8>.json.

    source: human label / URL / path the content came from.
    content: the raw text that was read.
    Returns JSON with the full sha256 and the bundle path.
    """
    _ensure_dirs()
    digest = _sha256(content)
    bundle = {
        "source": source,
        "sha256": digest,
        "length": len(content),
    }
    path = EVIDENCE_DIR / f"{digest[:8]}.json"
    path.write_text(_canonical(bundle), encoding="utf-8")
    return _json({"sha256": digest, "path": str(path)})


@mcp.tool()
def append_event(event_json: str) -> str:
    """Append an event to the hash-chained, append-only ledger
    (home/provenance/ledger.jsonl). Each line is {seq, prev_hash, event, hash}
    where hash = sha256(prev_hash + canonical_json(event)); genesis prev_hash is
    sixty-four zeros.

    event_json: a JSON string describing the event (e.g. an action record).
    Returns JSON with the new seq and hash.
    """
    _ensure_dirs()
    event = json.loads(event_json)
    prev_hash, seq = _ledger_head()
    new_hash = _link_hash(prev_hash, event)
    entry = {"seq": seq, "prev_hash": prev_hash, "event": event, "hash": new_hash}
    with LEDGER_PATH.open("a", encoding="utf-8") as fh:
        fh.write(_canonical(entry) + "\n")
    return _json({"seq": seq, "hash": new_hash})


@mcp.tool()
def verify_chain() -> str:
    """Recompute the hash chain from genesis and check it against stored hashes.

    Returns JSON {ok: bool}. If broken, also includes broken_seq = the first seq
    whose stored hash (or prev_hash linkage) does not match the recomputation.
    """
    chain = _read_ledger()
    prev_hash = GENESIS
    for entry in chain:
        seq = entry.get("seq")
        if entry.get("prev_hash") != prev_hash:
            return _json({"ok": False, "broken_seq": seq})
        recomputed = _link_hash(prev_hash, entry.get("event"))
        if recomputed != entry.get("hash"):
            return _json({"ok": False, "broken_seq": seq})
        prev_hash = entry["hash"]
    return _json({"ok": True})


@mcp.tool()
def build_dossier(client: str, period: str) -> str:
    """Assemble a provenance dossier for a client/period: the full ledger chain
    plus an index of every evidence bundle. Written to
    home/provenance/dossiers/<client>-<period>.json.

    client: client identifier.
    period: reporting period label (e.g. 2026-Q1).
    Returns JSON with the dossier path and the ledger entry count.
    """
    _ensure_dirs()
    chain = _read_ledger()
    evidence = []
    if EVIDENCE_DIR.exists():
        for f in sorted(EVIDENCE_DIR.glob("*.json")):
            try:
                evidence.append(json.loads(f.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                continue
    dossier = {
        "client": client,
        "period": period,
        "ledger": chain,
        "evidence": evidence,
        "entry_count": len(chain),
    }
    path = DOSSIER_DIR / f"{client}-{period}.json"
    path.write_text(_json(dossier), encoding="utf-8")
    return _json({"path": str(path), "entry_count": len(chain)})


if __name__ == "__main__":
    mcp.run()
