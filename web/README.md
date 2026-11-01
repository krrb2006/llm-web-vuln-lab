# VulnLab · 智能代码审计（LLM Web Vuln Lab Web）

用大模型辅助开源仓库代码审计的可自托管 Web 应用：上传仓库压缩包 → 静态规则定位可疑数据流 → 用**使用者自己的模型 API Key** 逐条复核 → 输出带文件/行号、代码片段、分析依据和修复建议的报告。

> 与仓库根目录的实验数据集同源：判定口径、证据分层（模型预测 / 代码定位 / POC 执行 / 实际触发）沿用 `docs/` 中的实验约定，本应用只把"静态规则 + LLM 复核"这一层做成可用产品。

## 界面

| 登录 | 工作台 |
|---|---|
| ![登录](docs/screenshots/login.png) | ![工作台](docs/screenshots/dashboard.png) |

![发现详情](docs/screenshots/job-detail.png)

## 架构

```
浏览器 ──► nginx 网关 :8080 ──┬── /            前端静态资源（React + Vite 构建产物）
                             └── /api/*       反向代理 ──► FastAPI :8000 ──► MySQL :3306
                                                              └── 解压 / 静态扫描 / 调模型
```

| 层 | 技术 | 说明 |
|---|---|---|
| 前端 | React 18 + TypeScript + Vite | SPA，无 UI 框架依赖，深色安全台风格 |
| 后端 | FastAPI + SQLAlchemy 2 | JWT 登录、任务队列（BackgroundTasks）、报告导出 |
| 数据库 | MySQL 8.4 | 用户、任务、发现三张表；utf8mb4 |
| 网关 | nginx 1.27 | 静态托管、SPA 回退、`/api` 代理、25 MB 上传、安全响应头 |
| 编排 | Docker Compose | 一条命令起全栈，MySQL 不暴露到宿主机 |

## 功能

- **上传即分析**：支持 `.zip` / `.tar.gz` / `.tgz` 或单个源码文件；自动跳过 `.git`、`node_modules`、`dist` 等目录，只读取代码，**永不执行上传代码**。
- **静态规则**：SQLi（字符串拼接 / 请求参数进查询）、XSS（反射输出、DOM 写入）、命令注入、路径穿越 / LFI、代码执行、反序列化、SSRF、硬编码密钥、弱哈希、关闭 TLS 校验、调试输出。
- **LLM 复核（可选）**：填入任意 OpenAI 兼容服务的 Key（OpenAI / DeepSeek / Moonshot / 通义千问 / 自建网关），对优先级最高的若干条候选逐条复核，返回结论、严重度、置信度、分析与修复建议。
- **证据可复核**：每条发现都包含 `文件:行号`、上下文代码片段、类别、来源（静态 / LLM）、置信度。
- **报告导出**：一键导出 Markdown 报告（含汇总表与逐条详情）。
- **示例仓库**：内置一个故意包含 SQLi / XSS / 命令注入 / 硬编码密钥的小样本，登录后点"用示例仓库试一下"即可看到完整效果，无需准备代码。

## 快速开始（Docker）

```bash
cd web
cp .env.example .env          # 至少改掉 JWT_SECRET、MYSQL_PASSWORD、MYSQL_ROOT_PASSWORD
docker compose up -d --build
# 浏览器打开 http://localhost:8080
```

默认演示账号：`demo@vulnlab.local` / `demo-vulnlab-2026`（可用 `SEED_DEMO=false` 关闭，或在 `.env` 里改）。

停止：

```bash
docker compose down            # 保留数据卷
docker compose down -v         # 连数据一起删除
```

## 本地开发

后端：

```bash
cd web/backend
python -m venv .venv && . .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL="mysql+pymysql://vulnlab:vulnlab@127.0.0.1:3306/vulnlab?charset=utf8mb4"
uvicorn app.main:app --reload --port 8000
```

前端（Vite 已把 `/api` 代理到 `127.0.0.1:8000`）：

```bash
cd web/frontend
npm install
npm run dev        # http://localhost:5173
npm run typecheck
npm run build
```

## 配置项

| 变量 | 默认值 | 说明 |
|---|---|---|
| `HTTP_PORT` | `8080` | 宿主机映射端口 |
| `JWT_SECRET` | 占位值 | **必须修改**，用于签发登录令牌 |
| `MYSQL_*` | `vulnlab` | 数据库名/账号/密码/root 密码 |
| `MAX_UPLOAD_MB` | `20` | 单次上传上限 |
| `MAX_FILES` | `3000` | 单次分析文件数上限 |
| `MAX_CANDIDATES` | `40` | 保留的静态候选上限 |
| `MAX_LLM_FINDINGS` | `8` | 交给模型复核的条数上限（控制费用） |
| `DAILY_JOB_LIMIT` | `10` | 每账号每日任务上限 |
| `SEED_DEMO` / `DEMO_EMAIL` / `DEMO_PASSWORD` | `true` / 见上 | 演示账号 |
| `ALLOW_REGISTER` | `true` | 是否开放在线注册 |
| `CORS_ORIGINS` | `http://localhost:5173` | 开发期跨域白名单 |

## 安全设计

- **不执行用户代码**：只做解压、文本读取与正则/数据流启发式匹配；不调用 `php`、`node`、`python` 执行上传内容。
- **解压防护**：路径穿越校验、拒绝符号链接、跳过依赖目录、单文件与总文件数上限、只保留白名单扩展名。
- **API Key 不落库**：Key 只存在使用者浏览器 `localStorage`，随任务请求发送，在进程内存中用完即释放，不写数据库、不写日志。
- **最小暴露面**：MySQL 与 FastAPI 只在内网 `internal` 网络中，宿主机只暴露 nginx；上传大小在 nginx 与 FastAPI 双侧限制。
- **账号隔离**：任务与发现按用户隔离，接口全部走 JWT 鉴权；每日限额防滥用。
- **已知限制**：静态规则是启发式，LLM 结论也可能出错；报告用于辅助人工复核，不作为漏洞成立的单独证据。

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/auth/register` | 注册（返回 JWT） |
| POST | `/api/auth/login` | 登录 |
| GET | `/api/auth/me` | 当前用户 |
| POST | `/api/jobs` | multipart：`file` + 可选 `api_key`/`provider`/`base_url`/`model` |
| POST | `/api/jobs/demo` | 用内置示例仓库创建任务 |
| GET | `/api/jobs` | 任务列表 |
| GET | `/api/jobs/{id}` | 任务详情 + 全部发现 |
| GET | `/api/jobs/{id}/export` | 导出 Markdown 报告 |
| DELETE | `/api/jobs/{id}` | 删除任务 |
| GET | `/api/health` | 健康检查 |
| GET | `/api/docs` | OpenAPI 文档 |

## 部署说明

- **GitHub Pages 只能托管静态文件**，跑不了 FastAPI 和 MySQL。所以本应用的代码放在 GitHub，运行时需要一个能跑 Docker 的地方（云主机 / 群晖 / 家里的小主机都行）：`git clone` → `cd web` → `cp .env.example .env` → 改密钥 → `docker compose up -d --build`。
- 如需公网访问，建议在 nginx 前再挂一层 HTTPS（Caddy / Traefik / 云厂商 LB），并打开 `ALLOW_REGISTER=false`、提高 `DAILY_JOB_LIMIT` 前先评估费用。
- 想接自己的域名：把 `HTTP_PORT` 反代到 443，或在 `nginx/default.conf` 里加证书。

## 目录

```
web/
├── docker-compose.yml
├── .env.example
├── nginx/
│   ├── Dockerfile          # 多阶段：构建前端 → nginx 静态托管
│   └── default.conf        # 网关配置（SPA 回退 + /api 代理）
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py         # FastAPI 入口、建表、演示账号
│       ├── config.py       # 环境变量
│       ├── db.py / models.py / schemas.py / security.py / deps.py
│       ├── routers/        # auth / jobs / health
│       ├── services/       # archive 解压、scan 规则、llm 复核、pipeline 编排
│       └── samples/        # 内置演示样本（故意含漏洞）
└── frontend/
    ├── vite.config.ts
    └── src/
        ├── pages/          # Login / Dashboard / JobDetail / Settings
        ├── components/     # Layout / UploadCard / Toast / Icons
        ├── api.ts / auth.tsx / types.ts / styles.css
```
