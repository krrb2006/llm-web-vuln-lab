import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import { IconAlert, IconChevron, IconDownload, IconFile, IconTrash } from "../components/Icons";
import { useToast } from "../components/Toast";
import type { Finding, JobDetail as JobDetailType, Severity } from "../types";

const STATUS_TEXT: Record<string, string> = {
  queued: "排队中",
  running: "分析中",
  succeeded: "已完成",
  failed: "失败",
};

const STAGE_TEXT: Record<string, string> = {
  queued: "排队",
  extracting: "解压与过滤",
  scanning: "静态扫描",
  analyzing: "模型复核",
  done: "完成",
  failed: "失败",
};

const SEVERITY_ORDER: Severity[] = ["critical", "high", "medium", "low", "info"];

const SOURCE_LABEL: Record<string, string> = {
  llm: "LLM 复核",
  dataflow: "数据流",
  static: "规则",
};

const SEVERITY_LABEL: Record<Severity, string> = {
  critical: "严重",
  high: "高危",
  medium: "中危",
  low: "低危",
  info: "提示",
};

function llmStatus(job: JobDetailType): string {
  if (!job.llm_enabled) return "未启用（仅静态规则）";
  if (job.llm_call_count > 0) return `已调用 ${job.llm_call_count} 次（候选 ${job.llm_candidate_count} 条）`;
  if (job.llm_candidate_count === 0) return "未调用：静态扫描没有候选问题";
  return "未完成调用：请查看下方错误信息";
}

export function JobDetail() {
  const { jobId } = useParams<{ jobId: string }>();
  const [job, setJob] = useState<JobDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<"all" | Severity | "llm">("all");
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [exporting, setExporting] = useState(false);
  const navigate = useNavigate();
  const { push } = useToast();

  const load = useCallback(async () => {
    if (!jobId) return;
    try {
      const detail = await api.job(jobId);
      setJob(detail);
      setError("");
      if (detail.findings.length > 0) {
        setExpanded((current) => (Object.keys(current).length ? current : { [detail.findings[0].id]: true }));
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "加载任务失败");
    } finally {
      setLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!job || (job.status !== "queued" && job.status !== "running")) return;
    const timer = window.setInterval(() => void load(), 1200);
    return () => window.clearInterval(timer);
  }, [job, load]);

  const findings = useMemo(() => {
    if (!job) return [] as Finding[];
    const list = [...job.findings];
    if (filter === "llm") return list.filter((item) => item.source === "llm");
    if (filter === "all") return list;
    return list.filter((item) => item.severity === filter);
  }, [job, filter]);

  async function remove() {
    if (!jobId) return;
    if (!window.confirm("删除这个任务及其全部发现？")) return;
    try {
      await api.deleteJob(jobId);
      push("任务已删除", "success");
      navigate("/");
    } catch (cause) {
      push(cause instanceof Error ? cause.message : "删除失败", "error");
    }
  }

  async function exportReport() {
    if (!jobId) return;
    setExporting(true);
    try {
      await api.exportJob(jobId);
      push("报告已下载", "success");
    } catch (cause) {
      push(cause instanceof Error ? cause.message : "导出失败", "error");
    } finally {
      setExporting(false);
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="skeleton" style={{ height: 120, marginBottom: 16 }} />
        <div className="skeleton" style={{ height: 260 }} />
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="container">
        <div className="panel panel-pad">
          <div className="alert error">{error || "任务不存在"}</div>
          <Link className="btn ghost" to="/">
            返回工作台
          </Link>
        </div>
      </div>
    );
  }

  const counts = job.severity_counts || {};
  const running = job.status === "queued" || job.status === "running";

  return (
    <div className="container">
      <div className="page-head">
        <div>
          <Link to="/" className="hint">
            ← 返回工作台
          </Link>
          <h1 style={{ fontSize: 26 }}>{job.filename}</h1>
          <p className="subtitle">
            {STATUS_TEXT[job.status] ?? job.status} · {STAGE_TEXT[job.stage] ?? job.stage} · {job.file_count} 个文件 ·{" "}
            {job.findings_count} 条发现
          </p>
        </div>
        <div className="inline">
          {job.status === "succeeded" && (
            <button className="btn ghost small" onClick={exportReport} disabled={exporting} type="button">
              {exporting ? <span className="spinner" /> : <IconDownload size={15} />} {exporting ? "准备下载…" : "导出报告"}
            </button>
          )}
          <button className="btn danger small" onClick={remove} type="button">
            <IconTrash size={15} /> 删除
          </button>
        </div>
      </div>

      <div className="panel panel-pad" style={{ marginBottom: 18 }}>
        <div className="inline" style={{ justifyContent: "space-between", marginBottom: 10 }}>
          <span className="badge running">{STATUS_TEXT[job.status] ?? job.status}</span>
          <span className="hint">{running ? `${job.progress}%` : job.finished_at ? "分析结束" : ""}</span>
        </div>
        <div className={`progress ${job.status === "failed" ? "fail" : job.status === "succeeded" ? "done" : ""}`}>
          <span style={{ width: `${job.progress}%` }} />
        </div>
        {job.error && (
          <div className="alert note" style={{ marginTop: 12 }}>
            <IconAlert size={14} style={{ verticalAlign: "-2px" }} /> {job.error}
          </div>
        )}
        <div className="inline" style={{ gap: 18, marginTop: 13, flexWrap: "wrap" }}>
          <span className="hint">
            <IconFile size={13} /> 语言：
            {Object.entries(job.languages || {})
              .map(([language, count]) => `${language} × ${count}`)
              .join("，") || "—"}
          </span>
          <span className="hint">模型：{job.llm_enabled ? `${job.provider} · ${job.model}` : "未启用（仅静态规则）"}</span>
          <span className="hint">调用状态：{llmStatus(job)}</span>
        </div>
      </div>

      <div className="stats" style={{ marginBottom: 18 }}>
        {SEVERITY_ORDER.map((severity) => (
          <div key={severity} className="panel stat">
            <div className="label">
              <span className={`badge ${severity}`}>{SEVERITY_LABEL[severity]}</span>
            </div>
            <div className="value" style={{ fontSize: 22 }}>
              {counts[severity] ?? 0}
            </div>
          </div>
        ))}
      </div>

      <div className="panel panel-pad">
        <h3 className="panel-title">
          <IconAlert size={17} /> 发现详情
        </h3>
        <p className="panel-hint">
          静态规则命中的是“候选问题”；带 LLM 标记的条目由你的模型逐条复核过。最终结论仍需人工确认。
        </p>

        <div className="filters">
          <button className={`filter ${filter === "all" ? "active" : ""}`} onClick={() => setFilter("all")} type="button">
            全部 {job.findings.length}
          </button>
          {SEVERITY_ORDER.map((severity) => (
            <button
              key={severity}
              className={`filter ${filter === severity ? "active" : ""}`}
              onClick={() => setFilter(severity)}
              type="button"
            >
              {SEVERITY_LABEL[severity]} {counts[severity] ?? 0}
            </button>
          ))}
          <button className={`filter ${filter === "llm" ? "active" : ""}`} onClick={() => setFilter("llm")} type="button">
            仅模型确认 {job.findings.filter((item) => item.source === "llm").length}
          </button>
        </div>

        {findings.length === 0 ? (
          <div className="empty">
            {running ? "正在分析，稍后自动刷新…" : "该筛选下没有发现，或本次扫描未命中规则。"}
          </div>
        ) : (
          <div>
            {findings.map((finding) => {
              const open = expanded[finding.id];
              const flow = finding.flow ?? [];
              return (
                <div className="finding" key={finding.id}>
                  <div
                    className="finding-head"
                    onClick={() => setExpanded((current) => ({ ...current, [finding.id]: !current[finding.id] }))}
                  >
                    <span className={`badge ${finding.severity}`}>{SEVERITY_LABEL[finding.severity]}</span>
                    <span className="title">{finding.title}</span>
                    <span className="loc">
                      {finding.file_path}:{finding.line}
                    </span>
                    <span className={`badge ${finding.source}`}>{SOURCE_LABEL[finding.source] ?? finding.source}</span>
                    <span style={{ transform: open ? "rotate(180deg)" : "none", transition: "0.2s" }}>
                      <IconChevron size={16} />
                    </span>
                  </div>
                  {open && (
                    <div className="finding-body">
                      <pre className="snippet">{finding.snippet}</pre>
                      <div className="meta">
                        <span>类别：{finding.category}</span>
                        <span>结论：{finding.verdict}</span>
                        <span>置信度：{finding.confidence}%</span>
                        <span>位置：{finding.file_path}:{finding.line}</span>
                      </div>
                      {flow.length > 0 && (
                        <>
                          <h4>数据流路径</h4>
                          <ol className="flow">
                            {flow.map((step, index) => (
                              <li key={`${step.line}-${index}`}>
                                <span className="flow-line">L{step.line}</span>
                                <span className="flow-note">{step.note}</span>
                                <code>{step.code}</code>
                              </li>
                            ))}
                          </ol>
                        </>
                      )}
                      <h4>分析</h4>
                      <p>{finding.explanation || "—"}</p>
                      <h4>修复建议</h4>
                      <p>{finding.remediation || "—"}</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
