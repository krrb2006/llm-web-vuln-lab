# 本地 DVWA 教学环境

这套配置把经审阅的 A、C 样本 PHP 文件部署到本机 DVWA，供 D 做正常业务请求、受控输入和源码哈希核对。所有命令从本仓库根目录执行。靶场仅绑定 `127.0.0.1:4280`，不要将端口转发到公网。

## 1. 准备 Docker、Python 与源码

确认 Docker Desktop 已启动，Docker Compose、Git 和 Python 可用。Windows PowerShell 用 `python` 执行下列脚本；在 WSL 中可改用 `python3`。宿主机不需要安装 PHP，语法检查在 DVWA 容器内执行。

```powershell
docker version
docker compose version
git --version
python --version
```

官方 DVWA 必须位于本仓库的 `third_party/DVWA`。该第三方工作副本受 `.gitignore` 排除，不作为本组源码提交。若目录尚不存在，执行：

```powershell
git clone https://github.com/digininja/DVWA.git third_party/DVWA
```

已有目录时不要重新克隆；先记录实际提交，再核对它与本组约定的版本是否一致：

```powershell
git -C third_party/DVWA rev-parse HEAD
git fetch origin
git rev-parse origin/a/criteria-and-sql01
git rev-parse origin/c/samples
```

`build_lab_cases.py` 默认读取上述 A、C 远程分支。分支可能继续变化，运行前应审阅两份提交的 PHP 代码及样本清单，并记录本次采用的完整提交号。正式参考验证应使用审阅后固定的提交号，而非让可移动的分支名决定运行内容；需要固定时传入 `--a-ref <完整提交号> --c-ref <完整提交号>`。当前脚本仅组装 A 的 S001–S008 与 C 的 S009–S016，之后的版本和 S017–S024 要另行审阅、更新。

## 2. 生成样本并初始化教学数据库

按顺序运行：

```powershell
python environment/build_lab_cases.py
python environment/init_lab_db.py
```

第一个脚本从选定的 Git 提交提取运行所需的 PHP 文件，生成受 Git 忽略的 `local/lab_cases`，并逐文件核对 SHA-256。它会为 C 的 S009–S012 生成适配 A 公共数据库连接的 `bootstrap.php`。脚本只复制 PHP 运行文件，不复制样本卡、人工真值和内部复核笔记。脚本不会自动删除目录中原有的文件；挂载前要核对目录内容，移出旧版本文件及任何非 PHP 文件：

```powershell
Get-ChildItem local/lab_cases -Recurse -File | Select-Object FullName
```

第二个脚本启动 MariaDB，创建独立的 `teaching_lab.lab_people` 教学表，并写入 Alice、Bob、Carol 三条虚构记录。它首次运行时随机生成数据库密码，保存在受 Git 忽略的 `local/lab.env`；后续运行复用该密码。不要提交、截图或粘贴此文件内容。脚本只处理 `teaching_lab`，不会重置 DVWA 自己的数据库；需要恢复三条教学数据时才运行 `python environment/init_lab_db.py --reset-data`。

## 3. 启动并检查服务

官方 `third_party/DVWA/compose.yml` 是第一份 Compose 文件；`environment/compose.lab.yml` 覆盖镜像和教学样本挂载。下列命令通过 `local/lab.env` 提供教学数据库密码：

```powershell
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml up -d
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml ps
```

浏览器访问 <http://127.0.0.1:4280/>。全新 DVWA 数据卷首次启动时，按页面提示在 Setup DVWA 中创建 DVWA 数据库，然后返回登录页。HTTP 检查可在 PowerShell 中运行：

```powershell
(Invoke-WebRequest http://127.0.0.1:4280/login.php -UseBasicParsing).StatusCode
```

预期为 `200`。如果容器或页面未就绪，检查 Compose 日志；不要把单纯的 `Up` 状态当作样本验证成功。核对后的 PHP 目录以只读方式挂载到 `/var/www/html/lab_cases`；不要将样本卡或真值资料放入该目录。

```powershell
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml exec -T dvwa php -l /var/www/html/lab_cases/S001/index.php
Get-FileHash local/lab_cases/S001/index.php -Algorithm SHA256
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml exec -T dvwa sha256sum /var/www/html/lab_cases/S001/index.php
```

语法检查应显示 `No syntax errors detected`，两处 SHA-256 应相同。随后按各样本卡检查正常请求、数据库返回和受控输入；语法通过或 HTTP 200 均不能单独证明案例真值。验证 S001–S016 前还应检查对应文件的哈希，尤其是生成的 `bootstrap.php` 和共用 `db_connect.php`。

本次 D 的可重复检查可依次运行：

```powershell
python environment/check_runtime.py
python environment/check_sql_http.py
python environment/check_xss_browser.py
python environment/capture_environment.py
```

它们分别生成 `environment/runtime_check.json`、`evidence/truth/S001` 至 `S012` 的 HTTP 参考记录、`S013` 至 `S016` 的浏览器 DOM 参考记录，以及脱敏的环境配置与版本文件。浏览器脚本需要本机 Chrome 或 Edge。参考记录只是 D 的现场观察，真值字段仍须由规定的同学独立复核后填写。发现某次输入失败时，保留首次失败记录并写明后续调整。

本地覆盖文件使用固定的 DVWA 与 MariaDB 镜像摘要，避免 `latest` 或标签更新造成运行差异。记录 `git -C third_party/DVWA rev-parse HEAD`、`docker image inspect` 的镜像 ID、`docker compose ... ps`、PHP/MariaDB 版本、A/C 完整提交号和浏览器版本，供第二台电脑复现。`docker compose config` 会展开数据库密码；保存配置证据前必须脱敏，不要把原样输出提交到 Git。

## 4. 停止服务

```powershell
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml down
```

日常停止只用 `down`，不要使用 `down -v`；后者会删除包含 DVWA 初始化数据的数据库卷。再次启动时重复第 3 步的 `up -d`。
