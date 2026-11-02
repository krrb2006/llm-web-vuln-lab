import { useMemo, useRef, useState } from "react";
import JSZip from "jszip";

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) || "/api";
const EXT = /\.(js|mjs|cjs|ts|tsx|jsx|vue|py|php|java|go|rb|cs|rs|c|cpp|h|sql|html|css|json|yaml|yml|xml|sh)$/i;
const IGNORE = /(^|\/)(node_modules|vendor|dist|build|coverage|\.git|\.next|target|__pycache__|venv)(\/|$)|\.min\.(js|css)$/i;
const PROVIDERS = { openai: ["https://api.openai.com/v1/chat/completions", "gpt-4.1-mini"], deepseek: ["https://api.deepseek.com/chat/completions", "deepseek-chat"], custom: ["", ""] } as const;

type Provider = keyof typeof PROVIDERS;
type SourceFile = { path: string; content: string };
type Severity = "critical" | "high" | "medium" | "low";
type Finding = { severity: Severity; title: string; location: string; evidence: string; impact: string; recommendation: string; confidence: "high" | "medium" | "low" };
type Report = { summary: string; risk_level: Severity; findings: Finding[]; limitations: string[] };
type ChatMessage = { role: "user" | "assistant"; content: string };

function sourceBundle(files: SourceFile[]) {
  let total = 0;
  return files.map((file) => {
    const room = 90_000 - total;
    if (room < 500) return "";
    const content = file.content.slice(0, Math.min(18_000, room));
    total += content.length;
    return `--- FILE: ${file.path} ---\n${content}\n--- END FILE ---`;
  }).filter(Boolean).join("\n");
}

async function readSource(file: File): Promise<SourceFile[]> {
  if (file.size > 20 * 1024 * 1024) throw new Error("文件超过 20 MB 限制，请移除依赖目录后重试。");
  if (!file.name.toLowerCase().endsWith(".zip")) return [{ path: file.name, content: await file.text() }];
  const zip = await JSZip.loadAsync(file);
  const entries = Object.values(zip.files).filter((entry) => !entry.dir && EXT.test(entry.name) && !IGNORE.test(entry.name));
  return Promise.all(entries.slice(0, 100).map(async (entry) => ({ path: entry.name, content: await entry.async("text") })));
}

function downloadReport(report: Report, projectName: string) {
  const rows = report.findings.map((finding, index) => `## ${index + 1}. ${finding.title}\n\n- 严重性：${finding.severity}\n- 位置：${finding.location}\n- 置信度：${finding.confidence}\n- 证据：${finding.evidence}\n- 影响：${finding.impact}\n- 修复建议：${finding.recommendation}`).join("\n\n");
  const markdown = `# TraceGuard 审计报告\n\n> 项目：${projectName}\n> LLM 辅助结果，必须经过人工复核。\n\n${report.summary}\n\n${rows || "未发现具有充分证据的漏洞。"}\n\n## 局限\n\n${report.limitations.map((item) => `- ${item}`).join("\n")}`;
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([markdown], { type: "text/markdown;charset=utf-8" }));
  link.download = "traceguard-audit-report.md";
  link.click();
  URL.revokeObjectURL(link.href);
}

export default function App() {
  const [files, setFiles] = useState<SourceFile[]>([]);
  const [projectName, setProjectName] = useState("未命名仓库");
  const [provider, setProvider] = useState<Provider>("openai");
  const [model, setModel] = useState<string>(PROVIDERS.openai[1]);
  const [endpoint, setEndpoint] = useState<string>(PROVIDERS.openai[0]);
  const [apiKey, setApiKey] = useState("");
  const [authorized, setAuthorized] = useState(false);
  const [auditId, setAuditId] = useState<string | null>(null);
  const [report, setReport] = useState<Report | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [chatBusy, setChatBusy] = useState(false);
  const [error, setError] = useState("");
  const [reviewed, setReviewed] = useState<number[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const ready = files.length > 0 && model.trim() && endpoint.trim() && apiKey.trim() && authorized;
  const totalChars = useMemo(() => files.reduce((sum, file) => sum + file.content.length, 0), [files]);

  const pickProvider = (value: Provider) => {
    setProvider(value);
    setEndpoint(PROVIDERS[value][0]);
    setModel(PROVIDERS[value][1]);
  };

  const ingest = async (file?: File) => {
    if (!file) return;
    try {
      const next = (await readSource(file)).filter((item) => item.content.trim());
      if (!next.length) throw new Error("没有找到可审计的文本源码。");
      setFiles(next);
      setProjectName(file.name.replace(/\.zip$/i, ""));
      setReport(null); setAuditId(null); setMessages([]); setReviewed([]); setError("");
    } catch (err) { setError(err instanceof Error ? err.message : "无法读取文件。"); }
  };

  const runAudit = async () => {
    if (!ready || busy) return;
    setBusy(true); setError(""); setMessages([{ role: "assistant", content: "正在整理攻击面、入口和数据流证据…" }]);
    try {
      const response = await fetch(`${API_BASE}/audits`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ projectName, provider, model, endpoint, apiKey, source: sourceBundle(files), fileNames: files.map((file) => file.path) }) });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || "审计请求失败。");
      setAuditId(body.id); setReport(body.result); setMessages([{ role: "assistant", content: body.result.summary || "初步扫描完成。现在可以针对右侧风险继续追问。" }]);
    } catch (err) { setError(err instanceof Error ? err.message : "审计服务暂时不可用。"); setMessages([]); }
    finally { setBusy(false); }
  };

  const ask = async (value = question) => {
    const text = value.trim();
    if (!text || !auditId || chatBusy) return;
    setQuestion(""); setChatBusy(true); setError(""); setMessages((items) => [...items, { role: "user", content: text }]);
    try {
      const response = await fetch(`${API_BASE}/audits/${auditId}/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ model, endpoint, apiKey, source: sourceBundle(files), message: text }) });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || "追问请求失败。");
      setMessages((items) => [...items, body.message]);
    } catch (err) { setError(err instanceof Error ? err.message : "追问暂时不可用。"); }
    finally { setChatBusy(false); }
  };

  const askFinding = (finding: Finding) => ask(`请围绕“${finding.title}”继续分析。位置：${finding.location}。证据：${finding.evidence}。请说明判断依据、影响和不含攻击载荷的安全验证思路。`);
  const fileInput = <input ref={inputRef} type="file" accept=".zip,.txt,.js,.ts,.tsx,.jsx,.py,.php,.java,.go,.rb,.cs,.html,.vue" onChange={(event) => ingest(event.target.files?.[0])} />;

  return <div className="app-shell">
    <header className="topbar"><div className="brand"><span className="brand-mark">⌁</span>TRACE<span>GUARD</span></div><div className="top-status"><span className="pulse" /> SELF-HOSTED / HUMAN + AI REVIEW <a href="#privacy">安全边界</a></div></header>
    <main>
      <section className="hero"><div><div className="eyebrow">INTERACTIVE SECURITY WORKBENCH</div><h1>审计不是一次扫描，<em>而是一场对话。</em></h1><p>上传授权仓库，配置自己的模型 API。先看证据，再追问、标注与复核，让 AI 成为你的安全搭档，而不是黑盒按钮。</p></div><div className="hero-stat"><strong>{files.length || "—"}</strong><span>源码文件<br />已纳入上下文</span></div></section>
      <section className="workbench">
        <aside className="panel source-panel"><div className="panel-heading"><div><span className="kicker">01 / SOURCE</span><h2>项目上下文</h2></div><span className="tag">LOCAL PREP</span></div><label className="dropzone"><input {...fileInput.props} ref={inputRef} /><span className="upload-icon">↥</span><b>导入仓库 ZIP</b><small>也支持单个源码文件<br />最大 20 MB · 浏览器内解压</small><span className="choose">选择文件</span></label>{files.length > 0 && <div className="source-loaded"><div><b>{projectName}</b><small>{files.length} files · {(totalChars / 1024).toFixed(1)} KB</small></div><button onClick={() => { setFiles([]); setReport(null); setAuditId(null); setMessages([]); }}>×</button></div>}<div className="file-list">{files.slice(0, 8).map((file) => <div className="file-row" key={file.path}>· {file.path}</div>)}{files.length > 8 && <small>+ {files.length - 8} 个文件已纳入</small>}</div><p className="privacy-note">自动排除依赖、构建产物与二进制文件。代码不会写入 MySQL。</p><div className="settings"><span className="kicker">02 / MODEL BRIDGE</span><label>项目名称<input value={projectName} onChange={(event) => setProjectName(event.target.value)} /></label><label>服务商<select value={provider} onChange={(event) => pickProvider(event.target.value as Provider)}><option value="openai">OpenAI</option><option value="deepseek">DeepSeek</option><option value="custom">兼容 OpenAI</option></select></label><label>模型<input value={model} onChange={(event) => setModel(event.target.value)} /></label><label>Endpoint<input value={endpoint} onChange={(event) => setEndpoint(event.target.value)} /></label><label>API Key<input type="password" value={apiKey} onChange={(event) => setApiKey(event.target.value)} placeholder="仅本次请求使用" autoComplete="off" /></label><label className="check"><input type="checkbox" checked={authorized} onChange={(event) => setAuthorized(event.target.checked)} /> 我确认拥有该仓库的审计授权</label><button className="primary full" disabled={!ready || busy} onClick={runAudit}>{busy ? "扫描中…" : report ? "重新扫描" : "开始初步扫描"}<span>→</span></button></div></aside>
        <section className="panel conversation-panel"><div className="conversation-head"><div className="assistant-title"><span className="assistant-icon">✦</span><div><span className="kicker">03 / COPILOT</span><h2>审计对话</h2><small>{auditId ? "会话已连接 · 可以继续追问" : "等待初步扫描"}</small></div></div><span className="model-label">{model || "NO MODEL"}</span></div><div className="messages">{messages.length === 0 ? <div className="empty-state"><span>✦</span><b>AI SECURITY COPILOT</b><p>初步扫描后，这里会出现攻击面摘要。你可以问“这条 SQLi 的数据流是什么？”或“如何安全验证？”</p></div> : messages.map((message, index) => <div className={`message ${message.role}`} key={`${message.role}-${index}`}><small>{message.role === "assistant" ? "TRACEGUARD AI" : "YOU"}</small><p>{message.content}</p></div>)}</div><div className="quick-prompts">{["概括攻击面", "解释最高风险", "安全验证思路", "最小修复计划"].map((prompt) => <button key={prompt} disabled={!auditId || chatBusy} onClick={() => ask(prompt)}>{prompt}</button>)}</div><form className="composer" onSubmit={(event) => { event.preventDefault(); ask(); }}><textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder={auditId ? "继续追问：把一条发现带入对话…" : "完成初步扫描后即可追问"} disabled={!auditId || chatBusy} /><button className="send" type="submit" disabled={!auditId || chatBusy || !question.trim()}>↑</button></form></section>
        <aside className="panel findings-panel"><div className="panel-heading"><div><span className="kicker">04 / EVIDENCE</span><h2>风险清单</h2></div><button className="export" disabled={!report} onClick={() => report && downloadReport(report, projectName)}>导出 MD ↓</button></div>{report && <div className="metrics">{(["critical", "high", "medium", "low"] as Severity[]).map((level) => <div className={`metric ${level}`} key={level}><strong>{report.findings.filter((finding) => finding.severity === level).length}</strong><span>{level.toUpperCase()}</span></div>)}</div>}<div className="finding-list">{!report ? <div className="empty-findings">完成扫描后，风险卡片会在这里按严重性排列。<br /><br /><span>每条卡片都包含定位、证据、置信度和追问入口。</span></div> : report.findings.length === 0 ? <div className="empty-findings">未发现具有充分证据的漏洞。<br /><span>这不等于代码绝对安全，仍需人工复核。</span></div> : report.findings.map((finding, index) => <article className={`finding-card ${finding.severity} ${reviewed.includes(index) ? "reviewed" : ""}`} key={`${finding.title}-${index}`}><div className="finding-top"><span>{finding.severity.toUpperCase()}</span><small>{reviewed.includes(index) ? "已复核" : finding.confidence + " confidence"}</small></div><h3>{finding.title}</h3><p>{finding.evidence || finding.impact}</p><code>{finding.location}</code><div className="finding-actions"><button onClick={() => askFinding(finding)} disabled={!auditId || chatBusy}>继续追问</button><button onClick={() => setReviewed((items) => items.includes(index) ? items.filter((item) => item !== index) : [...items, index])}>{reviewed.includes(index) ? "取消复核" : "标为已复核"}</button></div></article>)}</div></aside>
      </section>
      {error && <div className="error-banner">{error}</div>}
      <section className="privacy-strip" id="privacy"><b>SELF-HOSTED GUARDRAILS</b><span>API Key 只由你的 FastAPI 服务在单次请求中转发，不写入 MySQL；数据库只保存项目元信息、审计结论和对话记录。请只审计获得授权的仓库，AI 结论必须人工复核。</span></section>
    </main><footer>TRACEGUARD / REACT · FASTAPI · MYSQL · NGINX</footer>
  </div>;
}
