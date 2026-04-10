import { useState, useRef, useEffect, useCallback } from "react";

const SKILL_SYSTEM = `You are an experienced team dynamics coach with deep knowledge of psychological safety theory (Edmondson), team development models (Tuckman, Lencioni), and the relationship between delivery pressure and team culture. You take a longitudinal view — your job is to understand a team over time, not just in this moment.

IMPORTANT: The user may provide a team state document at the start of the conversation. If they do, read it silently and use it as your working context. Do not summarise it back unless asked.

If no state document is provided and this appears to be the first session, ask for the team's name/identifier, what they do, and how long they've been together.

SESSION MODES — identify which applies:
- Check-in: general update on how the team is doing
- Event debrief: specific incident, change, or milestone to process
- Safety assessment: explicit questions about trust, candour, conflict
- Advice: what to do about a dynamic or situation
- State review: reflect on the team's history

REASONING (do this silently before responding):
1. Trajectory: what does the observation log tell you about direction of travel?
2. Delta triggers: have recent events shifted your read?
3. Derived state: does your assessment match the stored estimate, or does new info update it?
4. Gaps: what don't you know that would matter? Ask one question if critical — only one.

RESPONDING:
- Check-in: honest read of team health, reference specific observations, offer one thing worth watching
- Event debrief: make sense of what happened, connect to patterns, avoid over-interpreting a single data point
- Safety assessment: structured view across Edmondson's four dimensions. Be specific, not generic.
- Advice: clear actionable recommendations, name tradeoffs, don't hedge everything
- State review: narrate the team's arc, note inflection points, don't read out log entries verbatim

TONE: Honest, direct, grounded. Not therapeutic, not corporate-wellness. You hold the team's long-term health as the priority. You will name uncomfortable patterns if evidence supports it. You do not offer platitudes. "Psychological safety takes time" is not an insight.

SECURITY: No names, no verbatim quotes, no PII in any recorded field. Describe team-level behaviour and patterns, not individuals.

AT THE END OF EVERY RESPONSE, output the updated state document in this exact format with no deviations:

---BEGIN TEAM STATE---
# Team State: [Team Name]

_Created: YYYY-MM-DD | Last updated: YYYY-MM-DD_

---

## Baseline

**Mandate:** ...
**Formed:** ...
**Size:** ...
**Composition:** ...
**Working agreements:** ...

---

## Trajectory

- **YYYY-MM-DD** \`[tags]\` — Observation. (append-only, never delete entries)

Available tags: safety conflict delivery-pressure change relationship energy inclusion failure-response

---

## Delta Triggers

- **YYYY-MM-DD** — Event. *Assessed impact: ...*

---

## Derived State

_Replaces previous assessment each session._

**As of:** YYYY-MM-DD
**Psychological safety estimate:** low | cautious | moderate | high
**Confidence:** low | medium | high

**Key risks:**
- ...

**Key strengths:**
- ...

**Watch list** _(to revisit next session)_:
- ...

**Coach notes:** ...
---END TEAM STATE---

Trajectory and Delta Triggers are APPEND-ONLY. Derived State is REPLACED each session.`;

const colors = {
  bg: "#141210",
  surface: "#1c1917",
  surface2: "#242018",
  border: "#2e2a24",
  border2: "#3a3530",
  text: "#e8e0d5",
  muted: "#8a8278",
  dim: "#5a554f",
  accent: "#c4873a",
  accentSoft: "#a06c28",
  accentDim: "#3d2d14",
  green: "#5a8a5a",
  greenDim: "#1e2e1e",
  red: "#8a4a4a",
  redDim: "#2e1e1e",
};

const s = {
  app: {
    fontFamily: "'DM Mono', 'Courier New', monospace",
    background: colors.bg,
    color: colors.text,
    height: "100vh",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
  },
  header: {
    padding: "14px 24px",
    borderBottom: `1px solid ${colors.border}`,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    background: colors.surface,
    flexShrink: 0,
  },
  h1: {
    fontFamily: "'Georgia', serif",
    fontSize: "17px",
    fontWeight: "700",
    letterSpacing: "0.02em",
    color: colors.text,
    margin: 0,
  },
  headerSub: {
    fontSize: "10px",
    color: colors.dim,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    marginLeft: "14px",
  },
  main: {
    display: "grid",
    gridTemplateColumns: "1fr 340px",
    flex: 1,
    overflow: "hidden",
  },
  chatPanel: {
    display: "flex",
    flexDirection: "column",
    borderRight: `1px solid ${colors.border}`,
    overflow: "hidden",
  },
  messages: {
    flex: 1,
    overflowY: "auto",
    padding: "24px",
    display: "flex",
    flexDirection: "column",
    gap: "20px",
  },
  emptyState: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "100%",
    gap: "12px",
    color: colors.dim,
    textAlign: "center",
    fontSize: "12px",
    lineHeight: "1.8",
    letterSpacing: "0.04em",
  },
  inputArea: {
    borderTop: `1px solid ${colors.border}`,
    padding: "16px 24px",
    display: "flex",
    flexDirection: "column",
    gap: "10px",
    background: colors.surface,
    flexShrink: 0,
  },
  statePanel: {
    display: "flex",
    flexDirection: "column",
    background: colors.surface,
    overflow: "hidden",
  },
  statePanelHeader: {
    padding: "14px 18px",
    borderBottom: `1px solid ${colors.border}`,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexShrink: 0,
  },
};

function Badge({ loaded }) {
  return (
    <span style={{
      fontSize: "10px",
      padding: "3px 8px",
      borderRadius: "2px",
      letterSpacing: "0.06em",
      textTransform: "uppercase",
      fontWeight: "500",
      background: loaded ? colors.greenDim : colors.surface2,
      color: loaded ? colors.green : colors.dim,
      border: `1px solid ${loaded ? "#2e4a2e" : colors.border}`,
    }}>
      {loaded ? "Team loaded" : "No team loaded"}
    </span>
  );
}

function Btn({ children, onClick, disabled, variant = "default", style = {} }) {
  const base = {
    fontFamily: "'DM Mono', 'Courier New', monospace",
    fontSize: "10px",
    letterSpacing: "0.06em",
    textTransform: "uppercase",
    padding: "5px 10px",
    borderRadius: "2px",
    cursor: disabled ? "not-allowed" : "pointer",
    border: "1px solid",
    transition: "all 0.15s",
    ...style,
  };
  const variants = {
    default: { background: "transparent", borderColor: colors.border2, color: colors.muted },
    accent: { background: colors.accent, borderColor: colors.accent, color: "#0a0a08", fontWeight: "500", fontSize: "11px", padding: "0 18px", height: "42px" },
    green: { background: "transparent", borderColor: disabled ? colors.border : colors.green, color: disabled ? colors.dim : colors.green },
    danger: { background: "transparent", borderColor: colors.border2, color: colors.dim },
  };
  return (
    <button onClick={onClick} disabled={disabled} style={{ ...base, ...variants[variant] }}>
      {children}
    </button>
  );
}

function ThinkingDots() {
  return (
    <div style={{
      display: "flex", gap: "5px", alignItems: "center",
      padding: "14px 16px",
      background: colors.surface,
      border: `1px solid ${colors.border}`,
      borderLeft: `3px solid ${colors.accentDim}`,
      borderRadius: "0 4px 4px 0",
    }}>
      {[0, 1, 2].map(i => (
        <div key={i} style={{
          width: "5px", height: "5px",
          background: colors.accent,
          borderRadius: "50%",
          opacity: 0.6,
          animation: `tdPulse 1.2s ease-in-out ${i * 0.2}s infinite`,
        }} />
      ))}
    </div>
  );
}

function Message({ role, text, stateExtracted }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "6px", animation: "tdFadeUp 0.25s ease" }}>
      <div style={{
        fontSize: "9px", letterSpacing: "0.1em", textTransform: "uppercase",
        color: role === "user" ? colors.accent : colors.dim,
      }}>
        {role === "user" ? "You" : "Coach"}
      </div>
      <div style={
        role === "assistant"
          ? { fontSize: "13px", lineHeight: "1.75", color: colors.text, whiteSpace: "pre-wrap", wordBreak: "break-word", background: colors.surface, border: `1px solid ${colors.border}`, borderLeft: `3px solid ${colors.border2}`, padding: "14px 16px", borderRadius: "0 4px 4px 0" }
          : { fontSize: "13px", lineHeight: "1.75", color: colors.muted, fontStyle: "italic", paddingLeft: "12px", borderLeft: `2px solid ${colors.accentSoft}`, whiteSpace: "pre-wrap", wordBreak: "break-word" }
      }>
        {text}
      </div>
      {stateExtracted && (
        <div style={{
          fontSize: "10px", color: colors.green,
          background: colors.greenDim,
          border: "1px solid #2e4a2e",
          padding: "6px 10px", borderRadius: "2px",
          letterSpacing: "0.04em", alignSelf: "flex-start",
        }}>
          ✓ Team state updated — save from panel →
        </div>
      )}
    </div>
  );
}

function renderMarkdownLine(line, i) {
  if (line.startsWith("# ")) {
    return <div key={i} style={{ fontFamily: "'Georgia', serif", fontSize: "15px", color: colors.text, marginBottom: "4px", fontWeight: "700" }}>{line.slice(2)}</div>;
  }
  if (line.startsWith("## ")) {
    return <div key={i} style={{ fontSize: "10px", letterSpacing: "0.1em", textTransform: "uppercase", color: colors.accent, margin: "16px 0 8px", paddingBottom: "4px", borderBottom: `1px solid ${colors.accentDim}` }}>{line.slice(3)}</div>;
  }
  if (line === "---") {
    return <hr key={i} style={{ border: "none", borderTop: `1px solid ${colors.border}`, margin: "10px 0" }} />;
  }

  const parts = [];
  let remaining = line;
  let idx = 0;

  const push = (text, style = {}) => {
    if (text) parts.push(<span key={idx++} style={style}>{text}</span>);
  };

  // Simple inline: **bold**, `tag`, _italic_
  const regex = /(\*\*(.+?)\*\*|`([^`]+)`|_(.+?)_)/g;
  let last = 0, m;
  while ((m = regex.exec(remaining)) !== null) {
    push(remaining.slice(last, m.index), { color: colors.muted, fontSize: "11.5px" });
    if (m[2]) push(m[2], { color: colors.text, fontWeight: "500", fontSize: "11.5px" });
    else if (m[3]) push(m[3], { fontSize: "9px", padding: "1px 5px", borderRadius: "2px", background: colors.accentDim, color: colors.accent, letterSpacing: "0.04em" });
    else if (m[4]) push(m[4], { color: colors.dim, fontStyle: "italic", fontSize: "11.5px" });
    last = m.index + m[0].length;
  }
  push(remaining.slice(last), { color: colors.muted, fontSize: "11.5px" });

  return <div key={i} style={{ lineHeight: "1.8", minHeight: "1.2em" }}>{parts.length ? parts : <span style={{ color: colors.muted, fontSize: "11.5px" }}>{line || "\u00a0"}</span>}</div>;
}

function StatePanel({ stateMarkdown, onDownload }) {
  return (
    <div style={s.statePanel}>
      <div style={s.statePanelHeader}>
        <span style={{ fontSize: "10px", letterSpacing: "0.1em", textTransform: "uppercase", color: colors.dim }}>Team State</span>
        <Btn variant="green" disabled={!stateMarkdown} onClick={onDownload}>↓ Save team-state.md</Btn>
      </div>
      <div style={{ flex: 1, overflowY: "auto", padding: "18px" }}>
        {stateMarkdown ? (
          <div>{stateMarkdown.split("\n").map((line, i) => renderMarkdownLine(line, i))}</div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", height: "100%", alignItems: "center", justifyContent: "center", color: colors.dim, fontSize: "11px", letterSpacing: "0.04em", textAlign: "center", lineHeight: "1.9", padding: "20px" }}>
            Updated team state will appear here after each session.<br /><br />
            Save it as <strong style={{ color: colors.muted }}>team-state.md</strong> and upload next time to continue.
          </div>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [apiHistory, setApiHistory] = useState([]);
  const [teamState, setTeamState] = useState(null);
  const [currentState, setCurrentState] = useState(null);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [uploadLabel, setUploadLabel] = useState("No file loaded");
  const messagesEndRef = useRef(null);
  const fileRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      setTeamState(ev.target.result);
      setCurrentState(ev.target.result);
      setUploadLabel(file.name);
    };
    reader.readAsText(file);
  };

  const extractState = (text) => {
    const start = text.indexOf("---BEGIN TEAM STATE---");
    const end = text.indexOf("---END TEAM STATE---");
    if (start !== -1 && end !== -1) {
      const extracted = text.slice(start + "---BEGIN TEAM STATE---".length, end).trim();
      const reply = text.slice(0, start).trim();
      return { reply, extracted };
    }
    return { reply: text, extracted: null };
  };

  const sendMessage = useCallback(async () => {
    if (loading || !input.trim()) return;
    const userText = input.trim();
    setInput("");
    setError("");

    setMessages(prev => [...prev, { role: "user", text: userText }]);

    // Build API messages
    let newApiHistory;
    if (teamState && apiHistory.length === 0) {
      newApiHistory = [{ role: "user", content: `Here is the current team state document:\n\n${teamState}\n\n---\n\n${userText}` }];
    } else {
      newApiHistory = [...apiHistory, { role: "user", content: userText }];
    }

    setLoading(true);

    try {
      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 2000,
          system: SKILL_SYSTEM,
          messages: newApiHistory,
        }),
      });

      const data = await res.json();
      if (data.error) { setError("API error: " + data.error.message); setLoading(false); return; }

      const fullText = data.content.map(b => b.text || "").join("");
      const { reply, extracted } = extractState(fullText);

      const assistantApiMsg = { role: "assistant", content: fullText };
      setApiHistory([...newApiHistory, assistantApiMsg]);

      setMessages(prev => [...prev, { role: "assistant", text: reply, stateExtracted: !!extracted }]);

      if (extracted) setCurrentState(extracted);

    } catch (err) {
      setError("Network error: " + err.message);
    }

    setLoading(false);
  }, [input, loading, teamState, apiHistory]);

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  const downloadState = () => {
    if (!currentState) return;
    const blob = new Blob([currentState], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "team-state.md"; a.click();
    URL.revokeObjectURL(url);
  };

  const clearSession = () => {
    setMessages([]); setApiHistory([]); setTeamState(null);
    setUploadLabel("No file loaded"); setError("");
    if (fileRef.current) fileRef.current.value = "";
  };

  const stateLoaded = !!teamState || !!currentState;

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&display=swap');
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #3a3530; border-radius: 2px; }
        @keyframes tdPulse { 0%,100%{opacity:0.3;transform:scale(0.9)} 50%{opacity:1;transform:scale(1.1)} }
        @keyframes tdFadeUp { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
      `}</style>

      <div style={s.app}>
        {/* Header */}
        <div style={s.header}>
          <div style={{ display: "flex", alignItems: "baseline" }}>
            <h1 style={s.h1}>Team Dynamics Coach</h1>
            <span style={s.headerSub}>Longitudinal · Structured · Private</span>
          </div>
          <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
            <Badge loaded={stateLoaded} />
            <Btn variant="danger" onClick={clearSession}>Clear session</Btn>
          </div>
        </div>

        {/* Main */}
        <div style={s.main}>
          {/* Chat */}
          <div style={s.chatPanel}>
            <div style={s.messages}>
              {messages.length === 0 ? (
                <div style={s.emptyState}>
                  <div style={{ fontSize: "28px", opacity: 0.3 }}>◈</div>
                  <p style={{ maxWidth: "280px", margin: 0 }}>Upload a team state file to continue a previous session, or start talking to create one.</p>
                </div>
              ) : (
                messages.map((m, i) => <Message key={i} {...m} />)
              )}
              {loading && (
                <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                  <div style={{ fontSize: "9px", letterSpacing: "0.1em", textTransform: "uppercase", color: colors.dim }}>Coach</div>
                  <ThinkingDots />
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div style={s.inputArea}>
              <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                <Btn onClick={() => fileRef.current?.click()}>↑ Load team-state.md</Btn>
                <span style={{ fontSize: "10px", color: colors.dim, letterSpacing: "0.04em" }}>{uploadLabel}</span>
                <input ref={fileRef} type="file" accept=".md,.txt" style={{ display: "none" }} onChange={handleFile} />
              </div>
              {error && (
                <div style={{ fontSize: "11px", color: colors.red, background: colors.redDim, border: "1px solid #3a2020", padding: "8px 12px", borderRadius: "2px" }}>
                  {error}
                </div>
              )}
              <div style={{ display: "flex", gap: "10px", alignItems: "flex-end" }}>
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={handleKey}
                  placeholder="How's the team doing? What happened in today's session?"
                  rows={1}
                  style={{
                    flex: 1,
                    fontFamily: "'DM Mono', 'Courier New', monospace",
                    fontSize: "13px",
                    background: colors.surface2,
                    border: `1px solid ${colors.border2}`,
                    color: colors.text,
                    padding: "10px 14px",
                    borderRadius: "3px",
                    resize: "none",
                    minHeight: "42px",
                    maxHeight: "120px",
                    lineHeight: "1.6",
                    outline: "none",
                  }}
                />
                <Btn variant="accent" onClick={sendMessage} disabled={loading || !input.trim()}>
                  Send
                </Btn>
              </div>
            </div>
          </div>

          {/* State Panel */}
          <StatePanel stateMarkdown={currentState} onDownload={downloadState} />
        </div>
      </div>
    </>
  );
}
