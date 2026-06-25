"""
Glassbox provenance report renderer for the AI accounting employee.

Reads a vr-provenance dossier (home/provenance/dossiers/<client>-<period>.json),
the hash-chained ledger (home/provenance/ledger.jsonl), and the content-addressed
evidence bundles (home/provenance/evidence/), and renders a single SELF-CONTAINED
HTML provenance report to home/provenance/reports/<client>-<period>.html.

The report is a "glass box": every ledger event is shown in chain order with its
hash and prev_hash, the chain link is re-verified, every evidence bundle is listed
with its source + sha256, and each event carries an explicit
AI-prepared-vs-human-authorized column so a reviewer can see exactly what the
agent did autonomously versus what a human signed off on.

Pure stdlib. Usage:
    python glassbox_report.py --client acme --period 2026-Q2
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("HERMES_HOME") or (Path(__file__).resolve().parents[1] / "home")) / "provenance"
EVIDENCE_DIR = ROOT / "evidence"
DOSSIER_DIR = ROOT / "dossiers"
REPORT_DIR = ROOT / "reports"
LEDGER_PATH = ROOT / "ledger.jsonl"
GENESIS = "0" * 64


def _canonical(obj) -> str:
    """Deterministic JSON matching the vr-provenance server's link hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _link_hash(prev_hash: str, event) -> str:
    return _sha256(prev_hash + _canonical(event))


def _read_ledger() -> list[dict]:
    if not LEDGER_PATH.exists():
        return []
    out = []
    for raw in LEDGER_PATH.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if raw:
            out.append(json.loads(raw))
    return out


def _read_evidence_dir() -> dict[str, dict]:
    """Map sha256 -> bundle for every evidence file on disk."""
    out: dict[str, dict] = {}
    if EVIDENCE_DIR.exists():
        for f in sorted(EVIDENCE_DIR.glob("*.json")):
            try:
                bundle = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            sha = bundle.get("sha256") or f.stem
            out[sha] = bundle
    return out


def _load_dossier(client: str, period: str) -> dict:
    path = DOSSIER_DIR / f"{client}-{period}.json"
    if not path.exists():
        raise FileNotFoundError(f"dossier not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


# ---- authorization classification ------------------------------------------

_AUTH_KEYS = ("authorized_by", "approved_by", "signed_off_by", "human")
_PREP_KEYS = ("prepared_by", "agent", "actor", "by")


def _first(event: dict, keys) -> str:
    for k in keys:
        v = event.get(k)
        if v:
            return str(v)
    return ""


def _classify(event: dict) -> tuple[str, str]:
    """Return (prepared_by, authorized_by) display strings for an event."""
    prepared = _first(event, _PREP_KEYS) or "AI (RealDeal CPA)"
    authorized = _first(event, _AUTH_KEYS)
    if not authorized:
        gate = str(event.get("gate", "")).upper()
        if gate == "GREEN":
            authorized = "Auto (GREEN authority)"
        elif gate in ("YELLOW", "RED"):
            authorized = "PENDING HUMAN"
        else:
            authorized = "(unauthorized / AI-prepared)"
    return prepared, authorized


def _esc(v) -> str:
    return html.escape("" if v is None else str(v))


def _mono(v) -> str:
    return f'<span class="mono">{_esc(v)}</span>'


# ---- HTML rendering --------------------------------------------------------

def _render_events_rows(chain: list[dict]) -> tuple[str, bool]:
    rows = []
    prev_hash = GENESIS
    chain_ok = True
    for entry in chain:
        seq = entry.get("seq")
        stored_prev = entry.get("prev_hash")
        stored_hash = entry.get("hash")
        event = entry.get("event", {})
        recomputed = _link_hash(prev_hash, event)
        link_ok = (stored_prev == prev_hash) and (recomputed == stored_hash)
        if not link_ok:
            chain_ok = False
        prepared, authorized = _classify(event if isinstance(event, dict) else {})
        action = event.get("action", "") if isinstance(event, dict) else ""
        ts = event.get("ts", "") if isinstance(event, dict) else ""
        auth_class = "auth-human"
        low = authorized.lower()
        if "pending" in low or "unauthorized" in low:
            auth_class = "auth-pending"
        elif "auto" in low:
            auth_class = "auth-auto"
        badge = "ok" if link_ok else "bad"
        badge_txt = "linked" if link_ok else "BROKEN"
        rows.append(
            f"<tr>"
            f"<td>{_esc(seq)}</td>"
            f"<td>{_esc(action)}</td>"
            f"<td>{_esc(ts)}</td>"
            f'<td><details><summary>event</summary>'
            f'<pre>{_esc(json.dumps(event, indent=2, sort_keys=True, default=str))}</pre>'
            f"</details></td>"
            f"<td>{_mono(prepared)}</td>"
            f'<td class="{auth_class}">{_esc(authorized)}</td>'
            f"<td>{_mono(stored_prev)}</td>"
            f"<td>{_mono(stored_hash)}</td>"
            f'<td><span class="badge {badge}">{badge_txt}</span></td>'
            f"</tr>"
        )
        prev_hash = stored_hash if stored_hash else recomputed
    return "\n".join(rows), chain_ok


def _render_evidence_rows(evidence: list[dict], on_disk: dict[str, dict]) -> str:
    rows = []
    seen = set()
    for b in evidence:
        sha = b.get("sha256", "")
        seen.add(sha)
        disk = on_disk.get(sha)
        present = "yes" if disk is not None else "MISSING"
        present_class = "ok" if disk is not None else "bad"
        rows.append(
            f"<tr>"
            f"<td>{_esc(b.get('source'))}</td>"
            f"<td>{_mono(sha)}</td>"
            f"<td>{_esc(b.get('length'))}</td>"
            f'<td><span class="badge {present_class}">{present}</span></td>'
            f"</tr>"
        )
    # evidence on disk but not referenced by the dossier
    for sha, disk in on_disk.items():
        if sha in seen:
            continue
        rows.append(
            f"<tr>"
            f"<td>{_esc(disk.get('source'))} <em>(on disk, not in dossier)</em></td>"
            f"<td>{_mono(sha)}</td>"
            f"<td>{_esc(disk.get('length'))}</td>"
            f'<td><span class="badge warn">extra</span></td>'
            f"</tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="4"><em>no evidence bundles</em></td></tr>')
    return "\n".join(rows)


CSS = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
       margin: 0; padding: 2rem; background: #0f1115; color: #e7e9ee; }
h1 { margin: 0 0 .25rem; font-size: 1.5rem; }
h2 { margin: 2rem 0 .5rem; font-size: 1.15rem; border-bottom: 1px solid #2a2f3a; padding-bottom: .25rem; }
.sub { color: #9aa3b2; margin: 0 0 1rem; }
table { width: 100%; border-collapse: collapse; font-size: .82rem; }
th, td { text-align: left; padding: .45rem .55rem; border-bottom: 1px solid #232733; vertical-align: top; }
th { color: #b9c2d0; font-weight: 600; position: sticky; top: 0; background: #161a22; }
.mono { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: .72rem; word-break: break-all; color: #c7d0de; }
pre { margin: .25rem 0 0; font-size: .72rem; white-space: pre-wrap; word-break: break-word; color: #c7d0de; }
details summary { cursor: pointer; color: #7aa2ff; }
.badge { display: inline-block; padding: .1rem .5rem; border-radius: 999px; font-size: .68rem; font-weight: 700; }
.badge.ok { background: #143d2a; color: #5ee29b; }
.badge.bad { background: #4a1620; color: #ff8a9c; }
.badge.warn { background: #4a3a14; color: #ffd166; }
.auth-human { color: #5ee29b; font-weight: 600; }
.auth-auto { color: #ffd166; }
.auth-pending { color: #ff8a9c; font-weight: 700; }
.banner { padding: .75rem 1rem; border-radius: 8px; margin: 1rem 0; font-weight: 600; }
.banner.ok { background: #143d2a; color: #5ee29b; }
.banner.bad { background: #4a1620; color: #ff8a9c; }
.meta { display: flex; gap: 2rem; flex-wrap: wrap; color: #9aa3b2; font-size: .85rem; }
footer { margin-top: 2rem; color: #6b7280; font-size: .75rem; }
"""


def render_html(dossier: dict, on_disk: dict[str, dict]) -> str:
    client = dossier.get("client", "")
    period = dossier.get("period", "")
    chain = dossier.get("ledger", []) or []
    evidence = dossier.get("evidence", []) or []

    event_rows, chain_ok = _render_events_rows(chain)
    evidence_rows = _render_evidence_rows(evidence, on_disk)

    banner = (
        '<div class="banner ok">Hash chain VERIFIED: all event links recompute and match stored hashes.</div>'
        if chain_ok else
        '<div class="banner bad">Hash chain BROKEN: one or more event links do not recompute. See the per-event status column.</div>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Glassbox provenance report - {_esc(client)} {_esc(period)}</title>
<style>{CSS}</style>
</head>
<body>
<h1>Glassbox provenance report</h1>
<p class="sub">Tamper-evident audit trail for the AI accounting employee. Every action is recorded; nothing is hidden.</p>
<div class="meta">
  <div><strong>Client:</strong> {_esc(client)}</div>
  <div><strong>Period:</strong> {_esc(period)}</div>
  <div><strong>Ledger events:</strong> {len(chain)}</div>
  <div><strong>Evidence bundles:</strong> {len(evidence)}</div>
</div>
{banner}

<h2>Ledger chain (chain order)</h2>
<table>
<thead><tr>
  <th>seq</th><th>action</th><th>ts</th><th>event</th>
  <th>AI prepared</th><th>Human authorized</th>
  <th>prev_hash</th><th>hash</th><th>link</th>
</tr></thead>
<tbody>
{event_rows or '<tr><td colspan="9"><em>empty ledger</em></td></tr>'}
</tbody>
</table>

<h2>Evidence bundles</h2>
<table>
<thead><tr><th>source</th><th>sha256</th><th>length</th><th>on disk</th></tr></thead>
<tbody>
{evidence_rows}
</tbody>
</table>

<footer>
Generated by glassbox_report.py from the vr-provenance dossier, ledger.jsonl, and evidence/.
Authority gates GREEN/YELLOW/RED are invariant; "PENDING HUMAN" rows must not be presented to a
client as authorized work. This report is self-contained and offline-renderable.
</footer>
</body>
</html>
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Render a glassbox provenance HTML report.")
    ap.add_argument("--client", required=True)
    ap.add_argument("--period", required=True)
    args = ap.parse_args(argv)

    os.makedirs(REPORT_DIR, exist_ok=True)
    dossier = _load_dossier(args.client, args.period)
    on_disk = _read_evidence_dir()
    htmltext = render_html(dossier, on_disk)

    out = REPORT_DIR / f"{args.client}-{args.period}.html"
    out.write_text(htmltext, encoding="utf-8")
    print(json.dumps({
        "report": str(out),
        "events": len(dossier.get("ledger", []) or []),
        "evidence": len(dossier.get("evidence", []) or []),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
