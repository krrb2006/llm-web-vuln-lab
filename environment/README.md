# 本地 DVWA 教学环境

这套配置把经审阅的 A、C、D 样本 PHP 文件部署到本机 DVWA，供 D 做正常业务请求、受控输入和源码哈希核对。所有命令从本仓库根目录执行。靶场仅绑定 `127.0.0.1:4280`，不要将端口转发到公网。

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

`build_lab_cases.py` 不传 `--d-ref` 时只读取 A、C 分支，组装 S001–S016；传入 `--d-ref` 后，还从该 Git 提交组装 D 的 S017–S024。分支可能继续变化，运行前应审阅提交中的 PHP 代码及样本清单，并记录采用的完整提交号。正式参考验证使用固定提交号，不依赖可移动的分支名。若 `git fetch origin` 因网络问题失败，先检查下列固定提交是否已在本地；不存在时不要改用未经审阅的版本。

## 2. 生成样本并初始化教学数据库

下面是本轮已核对的 A、C、D 源提交；换用后续提交前须重新审阅、重建并重做哈希与行为核对。按顺序运行：

```powershell
$aRef = 'd498903da01d89a695fa49d5392d3776eb901e2f'
$cRef = '8da63f7b8e169e5037626b0362d005ba7ba5ede0'
$dRef = 'a296e4b527ebdaf41ca04c2bbc5627b1a89efc06'
git cat-file -t $aRef
git cat-file -t $cRef
git cat-file -t $dRef
python environment/build_lab_cases.py --a-ref $aRef --c-ref $cRef --d-ref $dRef
python environment/init_lab_db.py
```

三个 `git cat-file -t` 应分别显示 `commit`。第一个 Python 脚本从选定的 Git 提交提取运行所需的 PHP 文件，生成受 Git 忽略的 `local/lab_cases`，并逐文件核对 SHA-256。传入 D 提交时共 37 个样本 PHP 文件；省略 `--d-ref` 时为 A/C 的 23 个。它会为 C 的 S009–S012 生成适配 A 公共数据库连接的 `bootstrap.php`。脚本只复制 PHP 运行文件，不复制样本卡、人工真值和内部复核笔记。脚本不会自动删除目录中原有的文件；挂载前要核对目录内容，移出旧版本文件及任何非 PHP 文件：

```powershell
Get-ChildItem local/lab_cases -Recurse -File | Select-Object FullName
```

脚本还从固定版本的官方 `config.inc.php.dist` 生成受 Git 忽略的 `local/dvwa_config.inc.php`。它只将官方配置读取的 `DB_USER/DB_PASSWORD` 环境变量名改为 `DVWA_DB_USER/DVWA_DB_PASSWORD`，保留官方 DVWA 账户默认值；教学样本仍按 A 的原始连接文件读取 `DB_*` 和最小权限的 `lab_user`。Compose 将这个独立配置只读挂载到 DVWA 主站。这样主站登录与教学表使用各自的数据库账户，且不改动任何 A/C/D 样本源码。不要手工编辑生成文件；再次构建会核对其来源和哈希。

第二个脚本启动 MariaDB，创建独立的 `teaching_lab.lab_people`、`lab_guestbook` 和 `lab_preview_drafts` 教学表，并写入 Alice、Bob、Carol 三条虚构记录。S017/S018 使用留言表，S021/S022 使用草稿表；各样本的记录由 `sample_id` 隔离。它首次运行时随机生成数据库密码，保存在受 Git 忽略的 `local/lab.env`；后续运行复用该密码。不要提交、截图或粘贴此文件内容。脚本只处理 `teaching_lab`，不会重置 DVWA 自己的数据库。`--reset-data` 只清空并重建 `lab_people` 的三条教学数据；存储型样本应使用按样本重置选项：

```powershell
python environment/init_lab_db.py --reset-sample S017
python environment/init_lab_db.py --reset-sample S018
python environment/init_lab_db.py --reset-sample S021
python environment/init_lab_db.py --reset-sample S022
```

每次运行只删除对应样本在相应表中的记录；可重复传入 `--reset-sample` 清理多个样本。执行前保存需要留存的请求和观察证据，记录清理时间与样本编号。

## 3. 启动并检查服务

官方 `third_party/DVWA/compose.yml` 是第一份 Compose 文件；`environment/compose.lab.yml` 覆盖镜像和教学样本挂载。下列命令通过 `local/lab.env` 提供教学数据库密码：

```powershell
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml up -d
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml ps
```

浏览器访问 <http://127.0.0.1:4280/>。全新 DVWA 数据卷首次启动时，按页面提示在 Setup DVWA 中创建 DVWA 数据库，然后返回登录页。HTTP 检查可在 PowerShell 中运行：

```powershell
$loginResponse = Invoke-WebRequest http://127.0.0.1:4280/login.php -UseBasicParsing
if ($loginResponse.StatusCode -ne 200 -or $loginResponse.Content -notmatch '<form' -or $loginResponse.Content -match 'Fatal error|Access denied') { throw 'DVWA 登录页异常' }
'DVWA 登录页正常'
```

预期为 `200`，且响应正文必须包含登录表单，不能有 `Fatal error` 或 `Access denied`。曾发现数据库权限错误也会返回 HTTP 200，因此只看状态码会误判；`capture_environment.py` 现在会检查正文。若页面异常，检查 Compose 日志和独立 DVWA 配置文件，不要运行会重建数据库的 Setup。核对后的 PHP 目录以只读方式挂载到 `/var/www/html/lab_cases`；不要将样本卡或真值资料放入该目录。

```powershell
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml exec -T dvwa php -l /var/www/html/lab_cases/S001/index.php
Get-FileHash local/lab_cases/S001/index.php -Algorithm SHA256
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml exec -T dvwa sha256sum /var/www/html/lab_cases/S001/index.php
```

语法检查应显示 `No syntax errors detected`，两处 SHA-256 应相同。随后按各样本卡检查正常请求、数据库返回和受控输入；语法通过或 HTTP 200 均不能单独证明案例真值。S001–S024 的所有运行 PHP 文件都须核对哈希，包括生成的 `bootstrap.php`、共用 `db_connect.php`、S019/S020 的模板及 S021/S022 的三个页面。`check_runtime.py` 还单独核对生成的 DVWA 主站配置在本地与容器内的哈希及 PHP 语法。

本次 D 的可重复检查可依次运行：

```powershell
python environment/check_runtime.py --a-ref $aRef --c-ref $cRef --d-ref $dRef
python environment/check_sql_http.py
# 单例复核时限定样本，避免覆盖其它样本的参考记录
python environment/check_sql_http.py --sample S009 --sample S010
python environment/check_xss_browser.py
python environment/check_d_business.py
node environment/check_d_browser.mjs
python environment/capture_environment.py
```

它们分别生成 `environment/runtime_check.json`、`evidence/truth/S001` 至 `S012` 的 HTTP 参考记录（默认覆盖全部 S001–S012；使用 `--sample` 可只更新指定样本）、`S013` 至 `S016` 的浏览器 DOM 参考记录、`S017` 至 `S024` 的普通业务 HTTP 与浏览器 DOM 参考记录，以及脱敏的环境配置与版本文件。`check_xss_browser.py` 需要本机 Chrome 或 Edge；当前 `check_d_browser.mjs` 在 Windows 使用 Chrome 与 Node.js 24。两个 D 脚本会按样本清理 S017/S018/S021/S022 的教学行；需要保留此前插入的本地数据时先不要重跑。参考记录只是 D 的现场观察，真值字段仍须由规定的同学独立复核后填写。发现某次输入失败时，保留首次失败记录并写明后续调整。

本地覆盖文件使用固定的 DVWA 与 MariaDB 镜像摘要，避免 `latest` 或标签更新造成运行差异。记录 `git -C third_party/DVWA rev-parse HEAD`、`docker image inspect` 的镜像 ID、`docker compose ... ps`、PHP/MariaDB 版本、A/C/D 完整提交号和浏览器版本，供第二台电脑复现。`docker compose config` 会展开数据库密码；保存配置证据前必须脱敏，不要把原样输出提交到 Git。

## 4. D 样本的正常业务检查

以下请求仅使用普通文字和教学数据。`curl.exe` 明确调用 Windows 的 curl 程序，避免 PowerShell 的别名差异。S017/S018 先按样本清理，再分别 POST 留言并 GET 列表；POST 应返回 `303`，列表应显示刚写入的文字。重复实验时使用新的普通文字，或再次按样本清理。

```powershell
python environment/init_lab_db.py --reset-sample S017 --reset-sample S018
curl.exe -sS -i --data-urlencode "body=D-normal-017" http://127.0.0.1:4280/lab_cases/S017/index.php
curl.exe -sS http://127.0.0.1:4280/lab_cases/S017/index.php
curl.exe -sS -i --data-urlencode "body=D-normal-018" http://127.0.0.1:4280/lab_cases/S018/index.php
curl.exe -sS http://127.0.0.1:4280/lab_cases/S018/index.php
```

S019/S020 不使用数据库。对每个 `index.php` 提交普通 `content` 后，检查输入框与预览正文均显示同样的文字；同时保存请求方式、状态和响应，不能仅凭状态码判断业务通过。

```powershell
curl.exe -sS -i --data-urlencode "content=D-normal-019" http://127.0.0.1:4280/lab_cases/S019/index.php
curl.exe -sS -i --data-urlencode "content=D-normal-020" http://127.0.0.1:4280/lab_cases/S020/index.php
```

S021/S022 先按样本清理，再提交普通标题与正文。POST 的 `Location` 指向新草稿的 `preview.php?id=...`；`-L` 会跟随 303 到预览页。另行 GET `list.php`，确认能打开同一编号的草稿。记录该编号，避免把旧数据当成本次结果。

```powershell
python environment/init_lab_db.py --reset-sample S021 --reset-sample S022
curl.exe -sS -i -L --data-urlencode "title=D-normal-021" --data-urlencode "body=Hello-021" http://127.0.0.1:4280/lab_cases/S021/submit.php
curl.exe -sS http://127.0.0.1:4280/lab_cases/S021/list.php
curl.exe -sS -i -L --data-urlencode "title=D-normal-022" --data-urlencode "body=Hello-022" http://127.0.0.1:4280/lab_cases/S022/submit.php
curl.exe -sS http://127.0.0.1:4280/lab_cases/S022/list.php
```

S023/S024 的正常路径只生成本页链接预览，不需要请求外部网站。核对两个版本的输入框值和预览链接 `href` 与普通 HTTP/HTTPS 地址一致；浏览器点击和协议边界测试应另行保存现场证据。

```powershell
curl.exe -sS -i -G --data-urlencode "url=https://example.org/" http://127.0.0.1:4280/lab_cases/S023/index.php
curl.exe -sS -i -G --data-urlencode "url=https://example.org/" http://127.0.0.1:4280/lab_cases/S024/index.php
```

四组样本的源码结构、运行入口、交叉复核责任见 `docs/D_第二轮样本交接.md`。受控输入须按各样本卡在本机浏览器完成，并将“实际观察”与“构造目标”分开记录；无害标记、HTTP 200 或源码推断都不代替 A 的独立复核。

## 5. 停止服务

```powershell
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml down
```

日常停止只用 `down`，不要使用 `down -v`；后者会删除包含 DVWA 初始化数据的数据库卷。再次启动时重复第 3 步的 `up -d`。
