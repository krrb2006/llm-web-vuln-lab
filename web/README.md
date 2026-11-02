# VulnLab · 智能代码审计（LLM Web Vuln Lab Web）

用大模型辅助开源仓库代码审计的可自托管 Web 应用：上传仓库压缩包 → 静态规则定位可疑数据流 → 用**使用者自己的模型 API Key** 逐条复核 → 输出带文件/行号、代码片段、分析依据和修复建议的报告。

> 与仓库根目录的实验数据集同源：判定口径、证据分层（模型预测 / 代码定位 / POC 执行 / 实际触发）沿用 `docs/` 中的实验约定，本应用只把"静态规则 + LLM 复核"这一层做成可用产品。

## 新用户最快启动

如果你只是想把仓库跑起来，不需要先理解 Docker、Vite 或 FastAPI：

### Windows（推荐）

双击 `web/start-web.cmd`，或在仓库根目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File web/scripts/run-native.ps1
```

脚本会自动创建 `.venv-native`、安装 Python 依赖、初始化本地 SQLite，并启动前端和 API。看到启动地址后保持窗口开启，访问：

```text
http://127.0.0.1:8081
```

### Linux / macOS / WSL

```bash
bash web/scripts/quickstart.sh
```

访问同一个地址 `http://127.0.0.1:8081`。首次安装依赖需要网络，之后启动会快很多。

### Docker（MySQL + Nginx，全栈部署）

```bash
cd web
cp .env.example .env
# 修改 .env 中的 MYSQL_PASSWORD、MYSQL_ROOT_PASSWORD、JWT_SECRET
docker compose up -d --build
```

访问 `http://localhost:8080`。Docker 模式使用 MySQL，原生模式使用 SQLite；两种模式的数据不会自动互通。

### 第一次使用网页

1. 使用演示账号 `demo@vulnlab.local / demo-vulnlab-2026` 登录，或切换到“注册”。
2. 先点击“用示例仓库试一下”，确认分析、进度刷新、漏洞详情和报告导出正常；如果上传卡片已经填入 API Key，示例任务也会把 Key 传给模型做复核。
3. 上传自己有权审计的源码压缩包；支持 ZIP、tar.gz 和常见源码文件。
4. 不填写 API Key 时只做本地静态扫描；填写 OpenAI 兼容 Key 后会对候选问题进行 LLM 复核。
5. API Key 只保存在当前浏览器并随分析请求发送，不写入数据库；共享电脑使用后请点击“清除 Key”和退出登录。

前端的已知限制、适用边界和后续计划见：[前端限制说明](docs/FRONTEND_LIMITATIONS.md)。

### 常见启动问题

- **提示找不到 `scripts/run-native.ps1`**：你在 Windows CMD 中切换盘符时要使用 `cd /d "D:\\...\\web"`，或者直接使用上面的完整路径命令。
- **提示 `No module named uvicorn`**：不要手动运行半成品环境；重新执行 `run-native.ps1`，脚本会检查并修复依赖。若之前安装被强制中断，可删除 `web/.venv-native` 后重试。
- **浏览器显示 `ERR_CONNECTION_REFUSED`**：后端进程已经退出或终端窗口被关闭。重新启动后，先用 `curl http://127.0.0.1:8081/api/health` 检查；CMD 中使用 `curl.exe`，`Invoke-WebRequest` 只在 PowerShell 中可用。
- **局域网分享**：使用 `run-native.ps1 -Bind 0.0.0.0`，再运行 `scripts/show-url.ps1`；Windows 防火墙需要放行 8081 端口。

### 依赖安装失败：`pydantic-core` / `Failed building wheel`

如果日志中出现下面的错误：

```text
Failed building wheel for pydantic-core
failed-wheel-build-for-install
```

这通常不是业务代码问题，而是当前 Python 没有匹配的预编译 Wheel，`pip` 被迫尝试本地编译 Pydantic 的 Rust 扩展。组内复现时请统一使用 **64 位 Python 3.11 或 3.12**，不要使用 32 位 Python 或过新的 Python 版本。

检查版本和架构：

```cmd
python --version
python -c "import platform,struct; print(platform.machine()); print(struct.calcsize('P')*8)"
```

如果已经创建过失败的虚拟环境，先删除后用 Python 3.11 重建：

```cmd
cd /d "D:\\你的仓库路径\\llm-web-vuln-lab\\web"
rmdir /s /q .venv-native
py -3.11 -m venv .venv-native
.venv-native\Scripts\python.exe -m pip install --upgrade pip
.venv-native\Scripts\python.exe -m pip install -r backend\requirements.txt -i https://pypi.org/simple
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run-native.ps1 -NoBrowser
```

如果官方源访问慢，可以替换为清华镜像：

```cmd
.venv-native\Scripts\python.exe -m pip install -r backend\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

不要把“安装 Rust 编译器”作为第一解决方案；统一 Python 版本比本地编译更容易复现。若不想安装 Python 依赖，可改用 Docker 模式，但 Docker 仍需要能拉取镜像。

### 其他常见问题对照表

| 现象 | 原因 | 处理方式 |
|---|---|---|
| `-File scripts/run-native.ps1 不存在` | CMD 中只执行了 `cd D:`，没有切换盘符 | 使用 `cd /d "D:\\...\\web"`，或直接传脚本完整路径 |
| `No module named uvicorn` | 上次安装被中断，虚拟环境只创建了一半 | 重新运行启动脚本；仍失败就删除 `.venv-native` 后重试 |
| `ERR_CONNECTION_REFUSED` | 后端进程已退出或启动终端被关闭 | 保持终端开启，先执行 `curl.exe http://127.0.0.1:8081/api/health` |
| `Invoke-WebRequest 不是内部或外部命令` | 在 CMD 中执行了 PowerShell 命令 | CMD 用 `curl.exe`；PowerShell 才能用 `Invoke-WebRequest` |
| `端口已被占用` | 8081 或 8080 已有其他程序 | 原生模式加 `-Port 8082`；Docker 修改 `.env` 的 `HTTP_PORT` |
| Docker 拉取镜像超时 | Docker Hub、PyPI 或校园网限制 | 更换网络/镜像源，或先使用原生模式 |
| 页面能打开但 API 报 502/503 | FastAPI 或 MySQL 仍在启动 | 等待 `/api/health` 返回 `status=ok`，再刷新页面 |
| 别人访问不了局域网地址 | 只监听了 `127.0.0.1` 或防火墙拦截 | 使用 `-Bind 0.0.0.0`，放行 TCP 8081，并确保在同一网络 |
| API Key 无法调用模型 | Base URL、模型名、Key 或网络不正确 | 先用静态扫描验证网站，再核对 OpenAI 兼容接口地址和模型名 |
| GitHub Pages 打开但没有后端功能 | Pages 只能托管静态文件 | 使用本地原生模式或 Docker 服务器；Pages 不运行 FastAPI/MySQL |

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
- **静态数据流（主）**：轻量 tokenizer + 语句拆分 + 变量级污点传播，支持 PHP / JS / TS / Python，输出完整**污染路径**（源 → 中间变量 → 汇点）。
- **规则兜底（辅）**：硬编码密钥、弱哈希、关闭 TLS 校验、调试输出等无数据流语义的问题仍由正则规则覆盖。
- **清洗函数感知**：按汇点类型区分 html / sql / shell / path / url 清洗函数 —— `intval()` 后的 SQL 不误报，"HTML 转义后拼进 SQL" 仍报告并降低置信度。
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

### 原生模式（不依赖 Docker，最稳）

不想被 Docker 状态影响时，用同一套代码直接跑在 Python 上（SQLite 存数据，预构建前端由 FastAPI 托管）：

```powershell
# Windows
powershell -File scripts/run-native.ps1          # 默认 http://127.0.0.1:8081
```

```bash
# Linux / macOS / WSL
./scripts/run-native.sh                          # PORT=9000 ./scripts/run-native.sh 可换端口
```

- 首次运行自动建 `.venv-native` 并装依赖（1–2 分钟），之后秒开；
- 数据在 `web/data/vulnlab.db`（SQLite），JWT 密钥写在 `web/local-native.env`（自动生成、已被 git 忽略）；
- 前端用仓库里的 `web/static/` 预构建产物，**不需要 Node**；改了前端代码后跑一次 `powershell -File scripts/build-static.ps1` 刷新；
- 可以和 Docker 版同时跑（8080 / 8081），互不干扰。

### 分享给别人（局域网）

```powershell
powershell -File scripts/show-url.ps1     # 打印当前本机/局域网地址并检测在线状态
```

| 模式 | 本机 | 局域网 |
|---|---|---|
| Docker（推荐分享） | `http://localhost:8080` | `http://<本机IP>:8080` |
| 原生（无需 Docker） | `http://127.0.0.1:8081` | `http://<本机IP>:8081` |

注意：

- 局域网访问要求对方连同一个 Wi-Fi；校园网（如 `tjuwlan`）常开启客户端隔离，可能连不上，改用手机热点。
- 8080 由 Docker 的入站规则放行；**8081 需要管理员放行一次**：
  `netsh advfirewall firewall add rule name="VulnLab 8081" dir=in action=allow protocol=TCP localport=8081`
- 本机 IP 由 DHCP 分配，重连 Wi-Fi 会变化，分享前重跑 `show-url.ps1`；原生模式想让局域网访问需加 `-Bind 0.0.0.0`。

### 稳定性：自动启动与自愈

本应用依赖 Docker 运行。电脑休眠/重启后 Docker Desktop 不会自动恢复时，站点就会打不开。仓库里提供了两层保障：

| 机制 | 作用 | 安装 |
|---|---|---|
| `scripts/auto-start.ps1` + 启动文件夹快捷方式 | 登录时启动 Docker、拉起容器，并常驻看门狗 | `powershell -File scripts/install-autostart.ps1` |
| `scripts/watchdog.ps1 -Loop` | 每 5 分钟检查 `/api/health`，异常自动 `docker compose up -d` | 由 `auto-start.ps1` 自动拉起 |
| compose `restart: always` + 三个服务的 healthcheck | 容器崩溃/宿主机重启后自动重启，不健康即重启 | 无需操作 |

卸载自启：`powershell -File scripts/install-autostart.ps1 -Remove`。
日志：`web/scripts/watchdog.log`、`web/scripts/startup.log`。

手动检查一次：`powershell -File scripts/watchdog.ps1`（正常时静默退出，异常时自动修复）。

### 打不开 localhost:8080 时

应用跑在 Docker 里（nginx + FastAPI + MySQL）。**电脑重启后如果 Docker Desktop 没启动，8080 就没有进程监听**，浏览器会提示无法连接。三种处理方式：

1. 打开 Docker Desktop，等引擎就绪后容器会按 `restart: unless-stopped` 自动拉起；
2. 或执行一键脚本：`powershell -ExecutionPolicy Bypass -File scripts/start.ps1`（Linux/macOS 用 `bash scripts/start.sh`）；
3. 想彻底免维护：Docker Desktop → Settings → General 勾选 **Start Docker Desktop when you sign in**。

脚本会自己检查引擎、拉起容器并轮询 `/api/health`，就绪后打印访问地址。

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

## 生产部署（域名 + 自动 HTTPS）

```bash
cd web
cp .env.prod.example .env        # 填 DOMAIN / ACME_EMAIL / 强密码
docker compose --env-file .env   -f docker-compose.yml -f docker-compose.prod.yml   up -d --build
```

Caddy 负责申请与续期证书（80/443），反向代理到内部 nginx；nginx 继续托管前端并转发 `/api`。
上公网前建议：`ALLOW_REGISTER=false`、`SEED_DEMO=false`、给 `JWT_SECRET` 用 `openssl rand -hex 32`。

## 测试

```bash
cd web/backend
python -m unittest discover -s tests -v      # 12 条：数据流分析 + 解压安全
```

CI（`.github/workflows/web-ci.yml`）会跑：前端 `tsc --noEmit` + `vite build`、后端 `compileall` + 单元测试、两个镜像构建。

## 项目介绍页

`web/landing/` 是给 GitHub Pages 用的纯静态介绍页（架构图 / 截图 / 部署命令），由 `.github/workflows/pages.yml` 自动发布。

**首次启用（需要仓库管理员操作一次）**：Settings → Pages → Build and deployment → Source 选择 **GitHub Actions**，然后到 Actions 里重跑 `pages` workflow（或再推一次 `web/landing/` 的改动）。
发布地址：<https://krrb2006.github.io/llm-web-vuln-lab/>。

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
