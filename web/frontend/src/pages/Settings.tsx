import { useState } from "react";
import { loadLlmConfig, saveLlmConfig } from "../api";
import { useAuth } from "../auth";
import { IconCheck, IconKey, IconShield } from "../components/Icons";
import { useToast } from "../components/Toast";
import { PROVIDERS } from "../types";
import type { LlmConfig } from "../types";

export function Settings() {
  const { user } = useAuth();
  const { push } = useToast();
  const [config, setConfig] = useState<LlmConfig>(() => loadLlmConfig());

  function update(next: Partial<LlmConfig>) {
    const merged = { ...config, ...next };
    setConfig(merged);
    saveLlmConfig(merged);
  }

  return (
    <div className="container">
      <div className="page-head">
        <div>
          <div className="eyebrow">Settings</div>
          <h1>设置</h1>
          <p className="subtitle">模型 Key 只保存在这台设备的浏览器里；后端只在分析请求期间使用，不写入数据库。</p>
        </div>
      </div>

      <div className="split">
        <div className="panel panel-pad">
          <h3 className="panel-title">
            <IconKey size={17} /> 模型接入
          </h3>
          <p className="panel-hint">任何 OpenAI 兼容接口都可用：OpenAI、DeepSeek、Moonshot、通义千问或自建网关。</p>

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
            <label>Base URL</label>
            <input
              className="input"
              value={config.baseUrl}
              onChange={(event) => update({ baseUrl: event.target.value })}
              placeholder="https://api.deepseek.com/v1"
            />
          </div>

          <div className="field">
            <label>模型名</label>
            <input
              className="input"
              value={config.model}
              onChange={(event) => update({ model: event.target.value })}
              placeholder="deepseek-chat"
            />
          </div>

          <div className="field">
            <label>API Key</label>
            <input
              className="input"
              type="password"
              value={config.apiKey}
              onChange={(event) => update({ apiKey: event.target.value })}
              placeholder="sk-..."
              autoComplete="off"
            />
          </div>

          <div className="inline">
            <button
              className="btn primary"
              type="button"
              onClick={() => {
                saveLlmConfig(config);
                push("已保存到本机浏览器", "success");
              }}
            >
              <IconCheck size={15} /> 保存
            </button>
            <button
              className="btn ghost"
              type="button"
              onClick={() => {
                const cleared = { ...config, apiKey: "" };
                setConfig(cleared);
                saveLlmConfig(cleared);
                push("已清除本机保存的 Key", "success");
              }}
            >
              清除 Key
            </button>
          </div>
        </div>

        <div>
          <div className="panel panel-pad">
            <h3 className="panel-title">
              <IconShield size={17} /> 账号
            </h3>
            <dl className="kv">
              <dt>邮箱</dt>
              <dd>{user?.email}</dd>
              <dt>昵称</dt>
              <dd>{user?.display_name || "—"}</dd>
              <dt>注册时间</dt>
              <dd>{user ? new Date(`${user.created_at}Z`).toLocaleString() : "—"}</dd>
            </dl>
          </div>

          <div className="panel panel-pad section-gap">
            <h3 className="panel-title">安全与限额</h3>
            <ul className="hint" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.9 }}>
              <li>上传的代码只在服务端本地解压与读取，永远不会执行。</li>
              <li>压缩包会做路径穿越校验，跳过 node_modules、.git 等目录，单文件与总量都有上限。</li>
              <li>API Key 不落库、不写日志；分析结束即从内存释放。</li>
              <li>每个账号每天有分析次数上限，避免被当成免费代理滥用。</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
