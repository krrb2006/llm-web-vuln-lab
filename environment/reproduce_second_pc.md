# 第二台电脑复现包（D）

目标：在另一名成员的电脑上，用同一提交、同一镜像和同一教学数据复现两个代表样本（S009 SQLi、S021 XSS），并留下 60–90 秒录屏与哈希对照。本文是操作清单，不是“已复现”结论。

## 一、固定版本

- 仓库提交：以复现当天的 `a/criteria-and-sql01` 为准，记录完整 SHA；本包编写时为 `e69e93f`。
- DVWA 镜像：`ghcr.io/digininja/dvwa@sha256:1af2cedda761…`。
- MariaDB 镜像：`ghcr.io/mariadb/mariadb@sha256:9d7f7220a4d9…`。
- 端口：仅 `127.0.0.1:4280`；不要映射到公网。
- 环境：Docker Desktop + WSL（或等价 Linux Docker）；Python 3.12；Node 22（仅 `check_d_browser.mjs` 需要）；Chrome/Edge 155。

## 二、步骤

```powershell
git clone https://github.com/krrb2006/llm-web-vuln-lab.git
cd llm-web-vuln-lab
git switch a/criteria-and-sql01
git rev-parse HEAD > environment/second_pc_commit.txt

docker version
docker compose version
python --version
```

构建运行树（不复制别人的 `local/`）：

```powershell
python environment/build_lab_cases.py --a-ref HEAD --c-ref HEAD --d-ref HEAD
python environment/init_lab_db.py
```

启动：

```powershell
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml up -d
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml ps
```

检查：

```powershell
python environment/check_runtime.py --a-ref HEAD --c-ref HEAD --d-ref HEAD
python environment/check_sql_http.py --sample S009 --sample S011
python environment/check_d_business.py
node environment/check_d_browser.mjs
python environment/capture_environment.py
```

预期：

- `check_runtime`：37/37，`source=local=container`，无意外文件，DVWA 配置通过；
- S009：正常 1 行、受控 3 行；S011：正常/受控排序变化；
- S017–S024 业务请求无 Fatal；S021 marker 执行、S022 不执行；
- `version.txt` 的镜像 ID、PHP/MariaDB、浏览器版本与本机一致。

## 三、两个代表样本

### S009（SQLi）

```powershell
curl.exe -sS "http://127.0.0.1:4280/lab_cases/S009/index.php?ids=1"
curl.exe -sS "http://127.0.0.1:4280/lab_cases/S009/index.php?ids=1%29+OR+1%3D1+%23"
```

观察：第一条 1 行（Alice）；第二条 3 行（Alice/Bob/Carol）。不要只看 HTTP 200。

### S021（XSS）

1. 浏览器打开 `http://127.0.0.1:4280/lab_cases/S021/submit.php`；
2. 标题填唯一值，正文填 `<script>document.documentElement.dataset.labXss='yes'</script>`；
3. 提交后进入 list，再打开新草稿的 preview；
4. DevTools 执行 `document.documentElement.dataset.labXss`，应为 `"yes"`；
5. 对 S022 重复，应为 `undefined`/无属性；结束后按唯一标题清理。

## 四、留证

- `environment/second_pc_commit.txt`、`version.txt`、`services.txt`；
- 两样本的普通/测试请求与响应截图；
- 60–90 秒录屏：从启动容器到 S009 行数变化、S021 marker 出现；
- 与本机 `environment/runtime_check.json` 的 37/37 对照；
- 在 `results/` 写一页 `D_second_pc_repro_YYYYMMDD.md`，记录实际版本、差异和失败点。

## 五、常见问题

| 现象 | 处理 |
|---|---|
| `docker version` 连接失败 | 先确认 Docker Desktop 运行、WSL 集成开启 |
| 4280 被占用 | 停掉本机其他 DVWA，不要改端口后不记录 |
| 镜像拉取失败 | 检查网络；记录实际镜像 ID，不要用未记录的新 tag |
| 页面 200 但正文是权限错误 | 检查 `local/dvwa_config.inc.php` 是否由 `build_lab_cases.py` 生成 |
| 哈希不一致 | 不要继续“源码—POC”配对；重建运行树并记录差异 |
| 浏览器 marker 不执行 | 检查是否打开 preview 而不是 list；确认没有额外转义 |

## 六、边界

- 第二台电脑复现是环境与参考验证，不是第二次模型运行；不产生新的 36 条记录。
- 不把 `local/lab.env`、数据库密码、Cookie 提交到 Git。
- 若第二台电脑的浏览器/镜像补丁号不同，记录差异，不强行写成完全一致。
