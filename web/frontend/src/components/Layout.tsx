import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import { IconGithub, IconLogout, IconSettings, IconShield, IconSpark } from "./Icons";

export function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const workspaceActive = location.pathname === "/" || location.pathname.startsWith("/jobs");

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <NavLink to="/" className="brand" end>
            <span className="brand-mark">
              <IconShield size={20} />
            </span>
            <span className="brand-text">
              VulnLab<span className="brand-sub">智能代码审计</span>
            </span>
          </NavLink>

          <nav className="nav-links">
            <NavLink to="/" className={workspaceActive ? "active" : ""}>
              工作台
            </NavLink>
            <NavLink to="/settings" className={({ isActive }) => (isActive ? "active" : "")}>
              <IconSettings size={15} /> 设置
            </NavLink>
            <a
              className="ghost-link"
              href="https://github.com/krrb2006/llm-web-vuln-lab"
              target="_blank"
              rel="noreferrer"
            >
              <IconGithub size={15} /> 仓库
            </a>
          </nav>

          <div className="topbar-right">
            <span className="user-chip">
              <span className="avatar">{(user?.display_name || user?.email || "U").slice(0, 1).toUpperCase()}</span>
              <span className="user-name">{user?.display_name || user?.email}</span>
            </span>
            <button
              className="icon-button"
              title="退出登录"
              onClick={() => {
                logout();
                navigate("/login");
              }}
            >
              <IconLogout size={17} />
            </button>
          </div>
        </div>
      </header>

      <main className="page">
        <Outlet />
      </main>

      <footer className="footer">
        <div className="footer-inner">
          <span>
            <IconSpark size={14} /> 静态规则 + 你自己的模型 Key，结论需人工复核
          </span>
          <span>仅分析源码，不执行上传代码；API Key 不落库</span>
        </div>
      </footer>
    </div>
  );
}
