import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useToast } from "../components/Toast";
import { UploadCard } from "../components/UploadCard";
import { IconAlert, IconClock, IconFile, IconSpark } from "../components/Icons";
import type { Job } from "../types";

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

function timeAgo(iso: string) {
  const date = new Date(iso.endsWith("Z") ? iso : `${iso}Z`);
  const diff = Date.now() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "刚刚";
  if (minutes < 60) return `${minutes} 分钟前`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} 小时前`;
  return `${Math.floor(hours / 24)} 天前`;
}

export function Dashboard() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { push } = useToast();

  const load = useCallback(async () => {
    try {
      const result = await api.jobs(30);
      setJobs(result.items);
    } catch (error) {
      push(error instanceof Error ? error.message : "加载任务失败", "error");
    } finally {
      setLoading(false);
    }
  }, [push]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setJobs((current) => {
        if (current.some((job) => job.status === "queued" || job.status === "running")) void load();
        return current;
      });
    }, 2500);
    return () => window.clearInterval(timer);
  }, [load]);

  const stats = useMemo(() => {
    const totalFindings = jobs.reduce((sum, job) => sum + job.findings_count, 0);
    const critical = jobs.reduce((sum, job) => sum + (job.severity_counts?.critical ?? 0), 0);
    const high = jobs.reduce((sum, job) => sum + (job.severity_counts?.high ?? 0), 0);
    return { totalFindings, critical, high };
  }, [jobs]);

  return (
    <div className="container">
      <div className="page-head">
        <div>
          <div className="eyebrow">Workspace</div>
          <h1>代码审计工作台</h1>
          <p className="subtitle">
            上传仓库代码，先由静态规则定位可疑数据流，再用你自己的模型 Key 逐条复核；结论以文件和行号为准，可导出报告。
          </p>
        </div>
      </div>

      <div className="stats">
        <div className="panel stat">
          <div className="label">
            <IconFile size={14} /> 分析任务
          </div>
          <div className="value">
            {jobs.length}
            <small>次</small>
          </div>
        </div>
        <div className="panel stat accent">
          <div className="label">
            <IconSpark size={14} /> 累计发现
          </div>
          <div className="value">
            {stats.totalFindings}
            <small>条</small>
          </div>
        </div>
        <div className="panel stat danger">
          <div className="label">
            <IconAlert size={14} /> 严重 / 高危
          </div>
          <div className="value">
            {stats.critical}
            <small>/ {stats.high}</small>
          </div>
        </div>
        <div className="panel stat warn">
          <div className="label">
            <IconClock size={14} /> 进行中
          </div>
          <div className="value">
            {jobs.filter((job) => job.status === "queued" || job.status === "running").length}
            <small>个任务</small>
          </div>
        </div>
      </div>

      <div className="split">
        <UploadCard
          onCreated={(job) => {
            setJobs((current) => [job, ...current]);
            navigate(`/jobs/${job.id}`);
          }}
        />

        <div className="panel panel-pad">
          <h3 className="panel-title">
            <IconClock size={17} /> 最近任务
          </h3>
          <p className="panel-hint">点击任意任务查看逐条发现与导出报告。</p>

          {loading ? (
            <div style={{ display: "grid", gap: 10 }}>
              {[0, 1, 2].map((index) => (
                <div key={index} className="skeleton" style={{ height: 64 }} />
              ))}
            </div>
          ) : jobs.length === 0 ? (
            <div className="empty">
              还没有任务。
              <br />
              左侧上传一个仓库包，或点“用示例仓库试一下”。
            </div>
          ) : (
            <div className="jobs">
              {jobs.map((job) => (
                <Link key={job.id} to={`/jobs/${job.id}`} className="job-row">
                  <div className="job-main">
                    <div className="job-title">
                      <span className="name">{job.filename}</span>
                      <span className={`badge ${job.status}`}>{STATUS_TEXT[job.status] ?? job.status}</span>
                    </div>
                    <div className="job-meta">
                      <span>{timeAgo(job.created_at)}</span>
                      <span>{job.file_count} 个文件</span>
                      {job.llm_enabled && <span className="badge llm">LLM · {job.model}</span>}
                      {!job.llm_enabled && <span className="badge static">仅静态</span>}
                    </div>
                    {job.status === "running" && (
                      <div className="progress" style={{ marginTop: 8 }}>
                        <span style={{ width: `${job.progress}%` }} />
                      </div>
                    )}
                  </div>
                  <div className="job-side">
                    <span className="count">{job.findings_count} 条</span>
                    <span className="badge">{STAGE_TEXT[job.stage] ?? job.stage}</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
