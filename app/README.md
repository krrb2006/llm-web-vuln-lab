# TraceGuard 全栈动态版

`app/` 是独立于原有实验文件和静态 `web/` 的全栈部署版本：

- `frontend/`：React + Vite，浏览器内解压 ZIP、筛选源码、交互式 AI 审计、人工复核和 Markdown 导出；
- `backend/`：FastAPI + SQLAlchemy 2 async + MySQL asyncmy，负责模型代理、审计会话和对话记录；
- `nginx/`：同域反向代理，`/` 转发前端，`/api/` 转发 FastAPI；
- `docker-compose.yml`：MySQL、FastAPI、React 静态服务和 Nginx 一键编排。

原仓库的实验数据、`web/` 静态版本和旧的 TraceGuard Site 源码均保留，不被本目录覆盖。

## 本地启动

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

访问 `http://localhost`。关闭服务：

```powershell
docker compose down
```

## GitHub + 服务器部署

1. 将本仓库推送到你的 GitHub 仓库。
2. 在自己的 Linux 服务器安装 Docker、Docker Compose，并克隆仓库。
3. 在 `app/.env` 设置随机的 MySQL 密码，并将 `CORS_ORIGINS` 改成你的域名，例如 `https://audit.example.com`。
4. 运行 `docker compose -f app/docker-compose.yml up -d --build`。
5. 将域名 DNS 指向服务器，在服务器层为 Nginx 配置 HTTPS（建议使用 Caddy 或 Certbot）。

模型 API Key 由用户在页面输入，FastAPI 只在单次请求中使用，不写入 MySQL。MySQL 保存项目元信息、审计结论和对话记录，不保存上传的源码正文。

生产环境请把 Nginx 放在 HTTPS 终止层、配置防火墙，只开放 80/443，并将 `MYSQL_ROOT_PASSWORD` 与 `MYSQL_PASSWORD` 换成随机长密码。
