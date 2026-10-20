# D 的 PPT 两页（文字稿）

> 对应 A 的框架：D 负责“本地 POC 复现 + 修复版本复测”两页。可直接交给 A 统一排版。

## 第 1 页：环境与证据链

**标题：从源码到可复现靶场**

- Windows + Docker Desktop / WSL，DVWA 仅绑定 `127.0.0.1:4280`；DVWA/MariaDB 镜像固定摘要。
- 37 个 PHP 文件：Git 源 = 本地运行目录 = 容器内文件，SHA-256 逐一核对；`php -l` 仅作前提。
- 主站与教学样本数据库账户隔离；登录页 200 之外还检查正文，避免“200 但权限错误”。
- 证据路径：`environment/runtime_check.json`（37/37）、`version.txt`、`services.txt`。

**一句话**：先证明“审计的源码就是运行的源码”，再谈模型结论。

## 第 2 页：动态复现与修复对照

**标题：POC 分层执行，修复版复测**

- 模型 POC 分三层：`original` → `adapted`（只改地址/路径）→ `logic_fixed`（改逻辑，成功不归原 POC）。
- S011 V1：原 POC 根路径 exit 1；仅改入口为 `/lab_cases/S011/index.php` 后 exit 0，排序 `1,2,3 → 2,1,3`。
- S011 V2：原脚本未改，仅设 `ENTRY_PATH`；排序 `1,2,3 → 3,2,1`。
- XSS 对照：S021 预览执行 marker（`data-lab-xss=yes`）；S022 修复版转义、无该属性。
- Burp：S009 受控 1→3 行、S010 配对 0 行；S021/S022 浏览器 DOM 对照。
- 结论边界：HTTP 200 不等于触发；`verification` 只认真实影响。

**现场演示**：跑一个本地 POC，再切到修复版用同一方法复测，展示“行序/ marker 变化”，而不是只看状态码。
