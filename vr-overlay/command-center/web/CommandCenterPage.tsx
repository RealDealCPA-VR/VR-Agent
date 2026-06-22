// RealDeal CPA — Command Center
// An n8n-style node canvas of the agent fleet: who is working on what, in which
// state, on which LLM. Click a node to inspect it, change any agent's model from
// the node, and add new specialized agents with a button. Themed via --color-* vars.
import { useCallback, useEffect, useMemo, useState } from "react";
import type { ReactNode, CSSProperties } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Handle,
  Position,
  ReactFlowProvider,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { fetchJSON } from "@/lib/api";

type Agent = {
  id: string; name: string; role: string; kind: "agent" | "human";
  model: string | null; status: string; task: string | null;
  skills: string[]; tools: string[]; x: number; y: number;
};
type Edge = { from: string; to: string; label?: string };
type Work = { id: string; title: string; agent: string; state: string; model?: string; client?: string; pct?: number };
type Fleet = { agents: Agent[]; edges: Edge[]; work: Work[] };
type Options = { models: string[]; skills: string[]; tools: string[]; statuses: string[] };

const STATUS_COLOR: Record<string, string> = {
  running: "#30D158", queued: "#FF9F0A", idle: "#8E8E93",
  blocked: "#FF3B30", review: "#0A84FF", done: "#34C759",
};
const shortModel = (m?: string | null) => (m ? m.split("/").pop()!.replace("claude-", "").replace("-preview", "") : "—");

const api = {
  state: () => fetchJSON<Fleet>("/api/command-center/state"),
  options: () => fetchJSON<Options>("/api/command-center/options"),
  patch: (id: string, body: Record<string, unknown>) =>
    fetchJSON(`/api/command-center/agents/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
  add: (body: Record<string, unknown>) =>
    fetchJSON("/api/command-center/agents", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
  remove: (id: string) => fetchJSON(`/api/command-center/agents/${id}`, { method: "DELETE" }),
};

// ---- custom node -----------------------------------------------------------
function AgentNode({ data }: { data: any }) {
  const a: Agent = data.agent;
  const human = a.kind === "human";
  const color = STATUS_COLOR[a.status] || "#8E8E93";
  return (
    <div
      onClick={() => data.onSelect(a.id)}
      style={{
        width: 230, borderRadius: 14, cursor: "pointer",
        background: "var(--color-card, #fff)", color: "var(--color-card-foreground, #1d1d1f)",
        border: `1px solid ${data.selected ? "var(--color-primary, #30D158)" : "var(--color-border, #e5e5ea)"}`,
        boxShadow: data.selected ? "0 0 0 2px var(--color-primary, #30D158)" : "0 1px 3px rgba(0,0,0,.08)",
        overflow: "hidden", fontFamily: "var(--font-sans, system-ui)",
      }}
    >
      {!human && <Handle type="target" position={Position.Left} style={{ background: color }} />}
      <Handle type="source" position={Position.Right} style={{ background: color }} />
      <div style={{ padding: "10px 12px 8px", borderBottom: "1px solid var(--color-border,#eee)", display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ width: 9, height: 9, borderRadius: 9, background: color, flex: "0 0 auto", boxShadow: a.status === "running" ? `0 0 6px ${color}` : "none" }} />
        <div style={{ minWidth: 0 }}>
          <div style={{ fontWeight: 700, fontSize: 14, lineHeight: 1.1, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{a.name}</div>
          <div style={{ fontSize: 11, opacity: 0.6, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{human ? "Partner" : a.role}</div>
        </div>
      </div>
      <div style={{ padding: "8px 12px 10px" }}>
        <div style={{ fontSize: 11.5, minHeight: 28, opacity: a.task ? 0.85 : 0.45, lineHeight: 1.25 }}>
          {a.task || (human ? "Reviews & authorizes" : "idle — no task")}
        </div>
        {!human && (
          <div style={{ marginTop: 8, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 6 }}>
            <span style={{ fontSize: 10, textTransform: "uppercase", letterSpacing: 0.4, color, fontWeight: 700 }}>{a.status}</span>
            <select
              value={a.model || ""}
              onClick={(e) => e.stopPropagation()}
              onChange={(e) => { e.stopPropagation(); data.onModel(a.id, e.target.value); }}
              title="LLM assigned to this agent"
              style={{ fontSize: 10.5, maxWidth: 120, border: "1px solid var(--color-border,#ddd)", borderRadius: 8, background: "var(--color-muted,#f5f5f7)", color: "inherit", padding: "2px 4px" }}
            >
              {(data.models as string[]).map((m) => <option key={m} value={m}>{shortModel(m)}</option>)}
            </select>
          </div>
        )}
        {human && <div style={{ marginTop: 6, fontSize: 10, fontWeight: 700, color: "#0A84FF", textTransform: "uppercase", letterSpacing: 0.4 }}>● sign-off gate</div>}
      </div>
    </div>
  );
}
const nodeTypes = { agent: AgentNode };

// ---- page ------------------------------------------------------------------
function CommandCenterInner() {
  const [fleet, setFleet] = useState<Fleet | null>(null);
  const [opts, setOpts] = useState<Options | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [showAdd, setShowAdd] = useState(false);

  const refresh = useCallback(async () => {
    try { setFleet(await api.state()); } catch { /* ignore poll error */ }
  }, []);
  useEffect(() => {
    api.options().then(setOpts).catch(() => {});
    refresh();
    const t = setInterval(refresh, 4000);
    return () => clearInterval(t);
  }, [refresh]);

  const onModel = useCallback(async (id: string, model: string) => {
    await api.patch(id, { model }); refresh();
  }, [refresh]);

  const nodes = useMemo(() => (fleet?.agents || []).map((a) => ({
    id: a.id, type: "agent", position: { x: a.x, y: a.y },
    data: { agent: a, selected: selected === a.id, onSelect: setSelected, onModel, models: opts?.models || [a.model || ""] },
  })), [fleet, selected, opts, onModel]);

  const edges = useMemo(() => (fleet?.edges || []).map((e, i) => ({
    id: `e${i}`, source: e.from, target: e.to, label: e.label, animated: true,
    style: { stroke: "var(--color-primary, #30D158)", strokeWidth: 1.5 },
    labelStyle: { fontSize: 10, fill: "var(--color-foreground, #1d1d1f)" },
    labelBgStyle: { fill: "var(--color-card, #fff)", fillOpacity: 0.85 },
  })), [fleet]);

  const sel = fleet?.agents.find((a) => a.id === selected) || null;
  const selWork = (fleet?.work || []).filter((w) => w.agent === selected);
  const counts = (fleet?.agents || []).reduce((m, a) => { m[a.status] = (m[a.status] || 0) + 1; return m; }, {} as Record<string, number>);

  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", background: "var(--color-background, #fff)" }}>
      {/* toolbar */}
      <div style={{ flex: "0 0 auto", display: "flex", alignItems: "center", gap: 14, padding: "12px 18px", borderBottom: "1px solid var(--color-border,#eee)" }}>
        <div style={{ fontWeight: 800, fontSize: 16 }}>Command Center</div>
        <div style={{ display: "flex", gap: 10, fontSize: 12, opacity: 0.75 }}>
          {Object.entries(counts).map(([s, n]) => (
            <span key={s} style={{ display: "inline-flex", alignItems: "center", gap: 5 }}>
              <span style={{ width: 8, height: 8, borderRadius: 8, background: STATUS_COLOR[s] || "#8E8E93" }} />{n} {s}
            </span>
          ))}
        </div>
        <div style={{ flex: 1 }} />
        <button onClick={() => setShowAdd(true)}
          style={{ background: "var(--color-primary, #30D158)", color: "#fff", border: "none", borderRadius: 10, padding: "8px 14px", fontWeight: 700, fontSize: 13, cursor: "pointer" }}>
          + Add Agent
        </button>
      </div>
      <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
        {/* canvas */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {fleet && (
            <ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} fitView
              proOptions={{ hideAttribution: true }} onPaneClick={() => setSelected(null)}>
              <Background color="var(--color-border,#e5e5ea)" gap={22} />
              <Controls showInteractive={false} />
              <MiniMap pannable zoomable nodeColor={(n: any) => STATUS_COLOR[n.data?.agent?.status] || "#8E8E93"} />
            </ReactFlow>
          )}
          {!fleet && <div style={{ padding: 40, opacity: 0.6 }}>Loading the fleet…</div>}
        </div>
        {/* detail panel */}
        {sel && (
          <div style={{ flex: "0 0 320px", borderLeft: "1px solid var(--color-border,#eee)", padding: 18, overflowY: "auto", background: "var(--color-card,#fff)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
              <div>
                <div style={{ fontWeight: 800, fontSize: 17 }}>{sel.name}</div>
                <div style={{ fontSize: 12, opacity: 0.6 }}>{sel.kind === "human" ? "Partner — sign-off" : sel.role}</div>
              </div>
              <button onClick={() => setSelected(null)} style={{ border: "none", background: "transparent", fontSize: 18, cursor: "pointer", opacity: 0.5 }}>×</button>
            </div>
            <Row label="Status"><span style={{ color: STATUS_COLOR[sel.status], fontWeight: 700, textTransform: "uppercase", fontSize: 12 }}>{sel.status}</span></Row>
            {sel.kind !== "human" && (
              <Row label="LLM">
                <select value={sel.model || ""} onChange={(e) => onModel(sel.id, e.target.value)}
                  style={{ width: "100%", padding: "6px 8px", borderRadius: 8, border: "1px solid var(--color-border,#ddd)", background: "var(--color-muted,#f5f5f7)", color: "inherit", fontSize: 12 }}>
                  {(opts?.models || []).map((m) => <option key={m} value={m}>{m}</option>)}
                </select>
              </Row>
            )}
            <Row label="Working on">{sel.task || <span style={{ opacity: 0.5 }}>nothing right now</span>}</Row>
            {!!sel.skills.length && <Row label="Skills"><Chips items={sel.skills} /></Row>}
            {!!sel.tools.length && <Row label="Tools"><Chips items={sel.tools} accent /></Row>}
            {!!selWork.length && (
              <Row label="Work items">
                {selWork.map((w) => (
                  <div key={w.id} style={{ fontSize: 12, marginBottom: 6 }}>
                    <div style={{ display: "flex", justifyContent: "space-between" }}><span>{w.title}</span><span style={{ color: STATUS_COLOR[w.state] }}>{w.state}</span></div>
                    <div style={{ height: 4, borderRadius: 4, background: "var(--color-muted,#eee)", marginTop: 3 }}>
                      <div style={{ width: `${w.pct || 0}%`, height: "100%", borderRadius: 4, background: "var(--color-primary,#30D158)" }} />
                    </div>
                  </div>
                ))}
              </Row>
            )}
            {sel.id !== "remy" && sel.id !== "partner" && (
              <button onClick={async () => { await api.remove(sel.id); setSelected(null); refresh(); }}
                style={{ marginTop: 18, width: "100%", border: "1px solid #FF3B30", color: "#FF3B30", background: "transparent", borderRadius: 9, padding: "8px", fontSize: 12, cursor: "pointer" }}>
                Remove agent
              </button>
            )}
          </div>
        )}
      </div>
      {showAdd && opts && <AddAgentModal opts={opts} onClose={() => setShowAdd(false)} onAdded={() => { setShowAdd(false); refresh(); }} />}
    </div>
  );
}

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div style={{ marginTop: 14 }}>
      <div style={{ fontSize: 10.5, textTransform: "uppercase", letterSpacing: 0.5, opacity: 0.5, marginBottom: 5 }}>{label}</div>
      <div style={{ fontSize: 13 }}>{children}</div>
    </div>
  );
}
function Chips({ items, accent }: { items: string[]; accent?: boolean }) {
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
      {items.map((t) => (
        <span key={t} style={{ fontSize: 11, padding: "2px 8px", borderRadius: 999, background: accent ? "var(--color-accent,#eaf9ef)" : "var(--color-muted,#f5f5f7)", border: "1px solid var(--color-border,#eee)" }}>{t}</span>
      ))}
    </div>
  );
}

function AddAgentModal({ opts, onClose, onAdded }: { opts: Options; onClose: () => void; onAdded: () => void }) {
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [model, setModel] = useState(opts.models[0] || "");
  const [skills, setSkills] = useState<string[]>([]);
  const [tools, setTools] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const toggle = (arr: string[], set: (v: string[]) => void, v: string) =>
    set(arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v]);
  const submit = async () => {
    if (!name.trim()) return;
    setBusy(true);
    try { await api.add({ name, role, model, skills, tools }); onAdded(); } finally { setBusy(false); }
  };
  return (
    <div onClick={onClose} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,.4)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 50 }}>
      <div onClick={(e) => e.stopPropagation()} style={{ width: 460, maxHeight: "85vh", overflowY: "auto", background: "var(--color-card,#fff)", color: "var(--color-card-foreground,#1d1d1f)", borderRadius: 16, padding: 22, boxShadow: "0 20px 60px rgba(0,0,0,.3)" }}>
        <div style={{ fontWeight: 800, fontSize: 18, marginBottom: 2 }}>Add an agent</div>
        <div style={{ fontSize: 12, opacity: 0.6, marginBottom: 14 }}>A new specialized worker on your fleet.</div>
        <Field label="Name"><input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Marketing Agent" style={inp} /></Field>
        <Field label="Role / what it owns"><input value={role} onChange={(e) => setRole(e.target.value)} placeholder="e.g. Campaigns & brand" style={inp} /></Field>
        <Field label="LLM">
          <select value={model} onChange={(e) => setModel(e.target.value)} style={inp}>
            {opts.models.map((m) => <option key={m} value={m}>{m}</option>)}
          </select>
        </Field>
        <Field label={`Skills (${skills.length})`}><Picker all={opts.skills} sel={skills} onToggle={(v) => toggle(skills, setSkills, v)} /></Field>
        <Field label={`Tools (${tools.length})`}><Picker all={opts.tools} sel={tools} onToggle={(v) => toggle(tools, setTools, v)} /></Field>
        <div style={{ display: "flex", gap: 10, marginTop: 18, justifyContent: "flex-end" }}>
          <button onClick={onClose} style={{ ...btn, background: "var(--color-muted,#f5f5f7)", color: "inherit" }}>Cancel</button>
          <button onClick={submit} disabled={busy || !name.trim()} style={{ ...btn, background: "var(--color-primary,#30D158)", color: "#fff", opacity: busy || !name.trim() ? 0.5 : 1 }}>{busy ? "Adding…" : "Add agent"}</button>
        </div>
      </div>
    </div>
  );
}
const inp: CSSProperties = { width: "100%", padding: "8px 10px", borderRadius: 9, border: "1px solid var(--color-border,#ddd)", background: "var(--color-background,#fff)", color: "inherit", fontSize: 13, boxSizing: "border-box" };
const btn: CSSProperties = { border: "none", borderRadius: 10, padding: "9px 16px", fontWeight: 700, fontSize: 13, cursor: "pointer" };
function Field({ label, children }: { label: string; children: ReactNode }) {
  return <div style={{ marginBottom: 12 }}><div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: 0.4, opacity: 0.55, marginBottom: 5 }}>{label}</div>{children}</div>;
}
function Picker({ all, sel, onToggle }: { all: string[]; sel: string[]; onToggle: (v: string) => void }) {
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 6, maxHeight: 130, overflowY: "auto", padding: 6, border: "1px solid var(--color-border,#eee)", borderRadius: 9 }}>
      {all.map((v) => {
        const on = sel.includes(v);
        return (
          <button key={v} onClick={() => onToggle(v)} style={{ fontSize: 11, padding: "3px 9px", borderRadius: 999, cursor: "pointer", border: `1px solid ${on ? "var(--color-primary,#30D158)" : "var(--color-border,#ddd)"}`, background: on ? "var(--color-primary,#30D158)" : "transparent", color: on ? "#fff" : "inherit" }}>{v}</button>
        );
      })}
    </div>
  );
}

export default function CommandCenterPage() {
  return <ReactFlowProvider><CommandCenterInner /></ReactFlowProvider>;
}
