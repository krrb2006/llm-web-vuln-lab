# D 报告章节初稿：环境、POC 验证与动态复现

> 供 A 整合进最终报告“模块详细设计”和“缺陷与优化”两章；数据来自 D 的 9 条正式记录、环境复跑和 Burp 加分实验。

## 4.x 本地验证环境与可复现性

实验统一使用 Windows 宿主机 + Docker Desktop（WSL 后端）运行 DVWA，服务只绑定 `127.0.0.1:4280`，不暴露公网。DVWA 与 MariaDB 镜像固定到摘要，避免 `latest` 漂移；样本 PHP 文件通过只读挂载进入容器，容器内不放入样本卡、真值或复核笔记。

为保证“审计源码 = 实际运行源码”，D 建立了三类检查：

1. **源码一致性**：从固定 Git 提交导出 37 个 PHP 运行文件，逐文件比较 Git 源、本地运行目录、容器内文件的 SHA-256；任何一端不一致即停止该样本的“源码—POC”配对结论。
2. **语法检查**：在容器内对 37 个文件执行 `php -l`，语法通过只作为可运行前提，不替代 HTTP、数据库或浏览器验证。
3. **环境健康**：DVWA 主站与教学样本使用独立数据库账户；登录页除 HTTP 200 外，还检查正文包含登录表单、且不出现 `Fatal error`/`Access denied`。曾出现“200 但正文是数据库权限错误”的误判，因此把正文断言写入 `capture_environment.py`。

最终记录：`runtime_check.json` 为 37/37，`source=local=container`，无多余运行文件，DVWA 独立配置哈希与语法检查通过；版本、镜像 ID、端口、PHP/MariaDB/浏览器版本保存在 `environment/version.txt`。

## 4.y POC 审核与执行分层

模型生成的 POC 不直接执行，而是按“原文—环境适配—逻辑修改”三层保存与判定：

- **original**：模型原文，原样保存；
- **adapted**：只改地址、Cookie、路径等环境参数，保存 diff；
- **logic_fixed**：改请求流程、测试输入或成功断言，成功不归给原 POC。

执行前逐项核对：目标是否为 `127.0.0.1:4280`、方法与参数是否匹配入口、是否含文件删除/外发/Shell、成功断言是否对应真实影响。`verification` 分 `triggered`、`not_triggered`、`execution_failed`、`not_run`、`not_applicable`，脚本可执行与漏洞触发分开记录。

D 的 9 条中，S011 V1 的原 POC 把入口写死为根路径，直接运行 exit 1；把 `BASE_URL` 改为 `/lab_cases/S011/index.php` 后 exit 0，排序由 `1,2,3` 变为 `2,1,3`，记为 `triggered`、`environment_execution_ok=true`、`raw_execution_ok=false`。S011 V2 原脚本未改，仅设置 `ENTRY_PATH`，排序变为 `3,2,1`，记为 `triggered`、`raw_execution_ok=true`。S010、S022 六条为修复样本，模型未生成 POC，保持 `not_run`。

## 4.z Burp 联动与动态复现

加分实验选 S009（SQLi）与 S021（XSS）各一例：先在 Burp Proxy 记录正常/受控请求，再发到 Repeater 手工重放，保存状态、正文差异与截图；XSS 另用浏览器 DOM 检查 `document.documentElement.dataset.labXss`，不把响应体出现 `<script>` 直接当作执行。

- SQLi：S009 正常 `ids=1` 返回 1 行，受控 `ids=1) OR 1=1 #` 返回 3 行；S010 配对控制同一 payload 返回 0 行。
- XSS：S021 marker 预览保留原始 `<script>`，浏览器 `data-lab-xss=yes`；S022 转义且无该属性。

Burp 抓包是 2026-10-13，早于正式 LLM 记录；D 在冻结源码 `6cd58b3` 上重放同一请求，行为不变，作为时间顺序的补充说明。SQLi 仅 S009 受控条件保存了完整 raw 请求/响应，其余三条为现场摘要 + 代理观察；XSS 执行证据来自浏览器 DOM/截图，不是 Burp 响应体。

## 5.x 环境与验证环节的缺陷及优化

| 现象 | 根因 | 优化 |
|---|---|---|
| DVWA 登录页 200 但正文是数据库权限错误 | 主站与样本共用同名数据库环境变量 | 生成独立 DVWA 配置，主站与教学账户隔离；HTTP 检查增加正文断言 |
| 容器哈希与正式包不一致 | 构建时把 S017–S024 从旧 D 提交取源 | 三个 ref 固定到冻结提交，`runtime_check` 逐文件比对源/本地/容器 |
| 只有 HTTP 200 就误判成功 | 状态码不反映业务影响 | SQLi 比较行集/条件变化，XSS 用浏览器 marker；`verification` 与状态码解耦 |
| 模型快照未记录 | 页面横幅显示 `V4.1-Flash-1017`，冻结单只写家族名 | 每条 metadata 记 `model_snapshot`；报告注明批次 |
| Burp 抓包早于正式运行 | 工具准备阶段先完成 | 冻结源码上重放并记录时间差，不把“先抓包”写成“先有 LLM 结论” |

## D 的 9 条结果（供 A 汇总）

| 样本 | V0 | V1 | V2 | 真值 | POC |
|---|---|---|---|---|---|
| S010（SQLi，fixed） | safe | safe | safe | safe | 无 |
| S011（SQLi，vulnerable） | vulnerable | vulnerable | vulnerable | vulnerable | V1/V2 triggered |
| S022（XSS，fixed） | safe | safe | safe | safe | 无 |

- 9/9 prediction 与真值一致；S011 V1/V2 的 POC 在本地触发，S010/S022 未生成 POC。
- 提交方式：D 授权，Chrome CDP 自动提交；原文由页面“复制”导出，截图与 metadata 在 `runs/F_*`。

## 边界

- 本组样本量小，结论只称“在本组受控样本集上的观察”，不宣称普遍识别率。
- 公开 DVWA 可能出现在模型训练材料中，独立测试不等于证明未知漏洞发现能力。
- 模型快照、自动化提交方式和 Burp 抓包时间差均需在报告附录如实说明。
