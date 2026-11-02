import { useMemo, useRef, useState } from "react";
import { api, loadLlmConfig, saveLlmConfig } from "../api";
import type { Job, LlmConfig } from "../types";
import { PROVIDERS } from "../types";
import { IconKey, IconPlay, IconSpark, IconUpload, IconX } from "./Icons";
import { useToast } from "./Toast";

interface Props {
  onCreated: (job: Job) => void;
}

function humanSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KiB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MiB`;
}

export function UploadCard({ onCreated }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [showKey, setShowKey] = useState(false);
  const [config, setConfig] = useState<LlmConfig>(() => loadLlmConfig());
  const inputRef = useRef<HTMLInputElement>(null);
  const { push } = useToast();

  const provider = useMemo(
    () => PROVIDERS.find((item) => item.id === config.provider) ?? PROVIDERS[0],
    [config.provider],
  );

  function update(next: Partial<LlmConfig>) {
    const merged = { ...config, ...next };
    setConfig(merged);
    saveLlmConfig(merged);
  }

  function pick(next: File | null) {
    if (!next) return;
    const limit = 20 * 1024 * 1024;
    if (next.size > limit) {
      push("文件超过 20 MiB 限制", "error");
      return;
    }
    setFile(next);
  }

  async function submit() {
    if (!file) {
      push("请先选择要分析的代码包", "error");
      return;
    }
    setBusy(true);
    try {
      const job = await api.createJob(file, config.apiKey ? config : null);
      push(job.llm_enabled ? "任务已创建，正在用你的 Key 分析" : "任务已创建（未填 Key，仅静态扫描）", "success");
      setFile(null);
      onCreated(job);
    } catch (error) {
      push(error instanceof Error ? error.message : "创建任务失败", "error");
    } finally {
      setBusy(false);
    }
  }

  async function runDemo() {
    setBusy(true);
    try {
      const job = await api.demoJob(config.apiKey ? config : null);
      push(job.llm_enabled ? "已创建示例任务，正在调用你的模型" : "已创建示例分析任务（仅静态扫描）", "success");
      onCreated(job);
    } catch (error) {
      push(error instanceof Error ? error.message : "创建示例任务失败", "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel panel-pad">
      <h3 className="panel-title">
        <IconUpload size={17} /> 新建分析
      </h3>
      <p className="panel-hint">上传开源仓库的压缩包或单个源码文件；代码只在服务端本地解压，不会被执行。</p>

      <div
        className={`dropzone ${dragging ? "drag" : ""}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragging(false);
          pick(event.dataTransfer.files?.[0] ?? null);
        }}
      >
        <div className="dz-icon">
          <IconUpload size={26} />
        </div>
        <div className="dz-title">拖拽代码包到这里，或点击选择</div>
        <div className="dz-sub">支持 .zip / .tar.gz / .tgz，或单个 .php / .js / .ts / .py 等源码，最大 20 MiB</div>
        <input
          ref={inputRef}
          type="file"
          hidden
          accept=".zip,.tar.gz,.tgz,.tar.bz2,.tar.xz,.php,.js,.jsx,.ts,.tsx,.py,.java,.go,.rb,.html,.vue,.svelte"
          onChange={(event) => pick(event.target.files?.[0] ?? null)}
        />
      </div>

      {file && (
        <div className="file-chip">
          <IconSpark size={15} style={{ color: "var(--accent)" }} />
          <span className="name">{file.name}</span>
          <span className="size">{humanSize(file.size)}</span>
          <button type="button" onClick={() => setFile(null)} title="移除">
            <IconX size={15} />
          </button>
        </div>
      )}

      <div style={{ marginTop: 18 }}>
        <div className="panel-title" style={{ fontSize: 14 }}>
          <IconKey size={16} /> 模型 API Key（可选）
        </div>
        <p className="panel-hint" style={{ marginBottom: 12 }}>
          填入后只会对静态扫描命中的前若干条候选做模型复核；如果静态扫描没有候选，本次不会产生模型请求。不填则只跑静态规则。Key 仅存本机浏览器，随本次请求发送，不写入数据库。
        </p>

        <div className="row">
          <div className="field">
            <label>服务商</label>
            <select
              className="select"
              value={config.provider}
              onChange={(event) => {
                const next = PROVIDERS.find((item) => item.id === event.target.value)!;
                update({ provider: next.id, baseUrl: next.baseUrl, model: next.models[0] });
              }}
            >
              {PROVIDERS.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.label}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>模型</label>
            <input
              className="input"
              list="model-options"
              value={config.model}
              onChange={(event) => update({ model: event.target.value })}
              placeholder="deepseek-flash"
            />
            <datalist id="model-options">
              {provider.models.map((model) => (
                <option key={model} value={model} />
              ))}
            </datalist>
          </div>
        </div>

        <div className="field">
          <label>Base URL（OpenAI 兼容）</label>
          <input
            className="input"
            value={config.baseUrl}
            onChange={(event) => update({ baseUrl: event.target.value })}
            placeholder="https://api.deepseek.com"
          />
        </div>

        <div className="field">
          <label>API Key</label>
          <div className="inline">
            <input
              className="input"
              type={showKey ? "text" : "password"}
              value={config.apiKey}
              onChange={(event) => update({ apiKey: event.target.value })}
              placeholder="sk-..."
              autoComplete="off"
            />
            <button className="btn ghost small" type="button" onClick={() => setShowKey((value) => !value)}>
              {showKey ? "隐藏" : "显示"}
            </button>
          </div>
        </div>
      </div>

      <div className="inline" style={{ marginTop: 8 }}>
        <button className="btn primary" onClick={submit} disabled={busy || !file} type="button">
          {busy ? <span className="spinner" /> : <IconPlay size={15} />} 开始分析
        </button>
        <button className="btn ghost" onClick={runDemo} disabled={busy} type="button">
          用示例仓库试一下
        </button>
      </div>
    </div>
  );
}
