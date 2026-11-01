import { useState } from "react";
import { Navigate } from "react-router-dom";
import { ApiError } from "../api";
import { useAuth } from "../auth";
import { IconShield, IconSpark } from "../components/Icons";

export function Login() {
  const { user, login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("demo@vulnlab.local");
  const [password, setPassword] = useState("demo-vulnlab-2026");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (mode === "login") await login(email.trim(), password);
      else await register(email.trim(), password, name.trim());
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "请求失败，请稍后再试");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-page">
      <aside className="auth-visual">
        <div className="eyebrow">LLM × Static Analysis</div>
        <h2>
          把仓库丢进来，
          <br />
          用你自己的模型 Key 找出可疑代码。
        </h2>
        <p>
          静态规则先圈出可疑数据流，再由你的大模型逐条复核，输出可复核的证据、位置与修复建议。
          代码只在服务端本地解压分析，不会被执行，API Key 不落库。
        </p>
        <div className="visual-list">
          <div className="visual-item">
            <span className="dot" />
            支持 zip / tar.gz 仓库包，自动跳过 node_modules 与二进制文件
          </div>
          <div className="visual-item">
            <span className="dot" />
            覆盖 SQLi、XSS、命令注入、路径穿越、反序列化、SSRF、硬编码密钥等类别
          </div>
          <div className="visual-item">
            <span className="dot" />
            每条结论都带文件:行号、代码片段、分析依据与修复建议
          </div>
        </div>
      </aside>

      <section className="auth-form-wrap">
        <div className="panel auth-card">
          <h1>
            <IconShield size={22} style={{ verticalAlign: "-4px", color: "var(--accent)" }} /> VulnLab
          </h1>
          <p className="subtitle">登录后开始扫描，或用演示账号一键进入。</p>

          <div className="tabs">
            <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")} type="button">
              登录
            </button>
            <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")} type="button">
              注册
            </button>
          </div>

          {error && <div className="alert error">{error}</div>}

          <form onSubmit={submit}>
            {mode === "register" && (
              <div className="field">
                <label>昵称</label>
                <input className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder="可选" />
              </div>
            )}
            <div className="field">
              <label>邮箱</label>
              <input
                className="input"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </div>
            <div className="field">
              <label>密码（至少 8 位）</label>
              <input
                className="input"
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
            </div>
            <button className="btn primary block" disabled={busy} type="submit">
              {busy ? <span className="spinner" /> : <IconSpark size={16} />}
              {mode === "login" ? "进入工作台" : "创建账号"}
            </button>
          </form>

          <p className="hint" style={{ marginTop: 14 }}>
            演示账号已预填：demo@vulnlab.local / demo-vulnlab-2026（可在部署时通过环境变量修改）
          </p>
        </div>
      </section>
    </div>
  );
}
