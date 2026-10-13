# D 当前完成情况（2026-10-13）

本页记录 D 在本机教学靶场已完成的工作与尚未完成的依赖。所有参考结果是现场观察，尚未经规定的独立真值复核，不能当作正式模型运行结果。

## 版本与提交状态

- 团队仓库分支：`d/environment-reference`。第一阶段提交为 `20bc12a`（环境与第一轮参考证据），D 样本源码提交为 `a296e4b`（S017–S024 与教学表）。本轮证据、脚本与交接文档在本文件所在的后续提交中；查分支最新 `git log` 获取完整提交号。
- 原有参考记录固定 A 源提交 `d498903da01d89a695fa49d5392d3776eb901e2f`、C 源提交 `a04a83218e7999acd03d8a20422cf4b405903479`、D 源提交 `a296e4b527ebdaf41ca04c2bbc5627b1a89efc06`。2026-10-13 的运行树哈希与语法检查已改用 C 源提交 `8da63f7b8e169e5037626b0362d005ba7ba5ede0`；S009/S010 新证据也固定到该提交。官方 DVWA 本地检出为 `068d974487a297c155c48722f9fcf7180a83adc4`。镜像摘要和工具版本见 `environment/version.txt`。
- `environment/runtime_check.json` 记录 37/37 个样本 PHP 运行文件通过容器语法检查，固定 Git 源、本地副本与容器内文件哈希一致，运行目录无多余文件；生成的 DVWA 主站配置另有来源/本地/容器哈希与 PHP 语法检查通过。服务仅绑定 `127.0.0.1:4280`。这项检查只覆盖源码一致性与语法。
- 第二轮普通业务与浏览器脚本、S017–S024 证据、更新后的环境记录和交接文档随本轮提交一并交付。复核前应记录实际审阅的分支提交号；若源码变化，重新生成运行目录并重做受影响验证。

## 本轮环境故障修复与 Burp 准备

- 复查发现 DVWA 登录页虽然返回 HTTP 200，正文实际为 `lab_user` 无权访问 `dvwa` 数据库的错误。根因是主站与教学样本读取了同名数据库环境变量。D 生成只读挂载的独立 DVWA 配置，让主站使用官方账户、样本继续使用仅有教学表权限的账户；A/C/D 样本源码未改动。修复后登录页有表单且无数据库错误，S001、S010、S017 的普通 GET 均无 PHP 致命错误。`capture_environment.py` 已增加正文健康断言，避免只凭 200 误报。
- 本机已安装 Burp Suite Community Edition v2026.9.2。10 月 13 日用户打开 Burp 自带浏览器后，D 确认 `127.0.0.1:8080` listener 已监听。首轮 S009/S010 的 SQL 对照和 S021/S022 的普通/marker 提交、列表与预览请求经 Burp 代理完成，证据分别见 `demo/burp_sqli_proxy_observation.json`、`demo/burp_xss_proxy_observation.json`。临时 Chrome 代理观察确认 S021 执行页面标记、S022 显示转义文本；首轮两张浏览器截图已保存且教学行已清理。之后 D 在 Burp Repeater 手工重放 S021 `id=15` 与 S022 `id=16`，以及 S009/S010 四条只读 SQL 对照请求；所有请求均返回 200，响应行数符合配对预期。SQLi Repeater 的可见观察摘要和 S010 控制条件截图在 `demo/burp_sqli_repeater_observation.json` 及对应 JPG；完整 raw Repeater 响应和 S009 配对截图尚未另存。另记录一条录入格式错误导致的 408，不计作样本结果。S021/S022 两条重试草稿暂留供复核。第二台电脑复现仍待完成。详见 `demo/burp_readiness.md`。

## 已保存的参考观察

| 范围 | 已保存的内容 | 证据位置与注意点 |
|---|---|---|
| S001–S012 | 正常请求与受控 SQL 条件的 HTTP 记录 | `evidence/truth/S001`–`S012/http_reference.json`；S009/S010 已按 C 的新提交重跑，修正后的观察见下文；其余样本保留原记录 |
| S013–S016 | 普通请求与无外发页面标记的浏览器 DOM 记录 | `evidence/truth/S013`–`S016/browser_reference.json`；S013/S015 出现页面属性标记，配对 S014/S016 未出现，待独立审核 |
| S017–S024 | 共 24 条普通业务请求；八例各有 HTTP 记录 | `evidence/truth/S017`–`S024/business_http.json`；请求数按样本为 3、3、2、2、4、4、3、3，覆盖写入/读取、模板预览、草稿列表与链接预览 |
| S017–S024 | 四组配对浏览器观察 | `evidence/truth/S017`–`S024/browser_reference.json`；S017 独立读取、S019 POST 预览、S021 独立草稿预览、S023 点击链接后出现本页属性标记；S018/S020/S022/S024 的对应观察未出现。S024 链接回退为 `#` |

S017–S024 的普通业务检查由 `environment/check_d_business.py` 生成；浏览器记录由 `environment/check_d_browser.mjs` 生成。首次浏览器脚本运行在 Windows 临时 Chrome 目录清理阶段报错，修正进程清理后完整重跑且退出码为 0；现存八份 JSON 为重跑结果。存储型样本按样本清理后，本机复查 `lab_guestbook` 与 `lab_preview_drafts` 中相关教学记录为 **0/0 行**。清理和首次失败都应随第二轮证据一并留痕，避免把首次运行写成成功。

## 尚未完成

1. `dataset/manifest.json` 的 24 个 `ground_truth` 目前全部为 `null`；A/C 的独立复核与签署尚未完成。D 样本的构造目标和本机观察不能直接变成真值。S021/S022 的跨页实现与 C 手册“第二条读取路径”的措辞差异，须由 C、A 确认是否符合蓝图，暂不改动已固定源码。
2. C 已修订 S009/S010 并推送 `c/samples`；D 已按新源码复核参考行为，但 S009 v2 输入包哈希与 B 通知的前缀不一致，暂停冻结，待 B/C 核对。D 已选择保留 mysqli 严格模式，并建议所有查询、预处理和执行流程使用 `try/catch (Throwable)`、错误仅写日志；该方案待 A 确认，随后由 A 补齐 S001–S008、C 对齐 S011/S012，D 再按新提交重建和复验。B 仍需完成六份 Prompt 的版本确认、输出字段核对、模型原文与冻结哈希。环境、样本、真值和 Prompt 未一起冻结前不开始正式测试。
3. `runs/formal.json` 现有 36 条均为 `planned`。D 负责 S010、S011、S022 各 V0/V1/V2 的 9 条正式记录，并复核 A 的 9 条；D 的 9 条由 C 复核。这些记录目前未执行。
4. SQLi/XSS 的请求、响应已有 Burp 代理观察；XSS 页面 DOM 对照、浏览器截图和两条 Repeater 手工重放已完成。SQLi 的四条只读 Repeater 请求也已完成并记录观察摘要；S010 控制条件的 Repeater 截图已保存。首轮演示写入已清理，重试的 S021/S022 草稿暂留供复核。完整 raw Repeater 输出、S009 配对截图尚未留存；第二台电脑按同一版本复现也未完成。

下一步先由 A/D 定统一 MySQLi 错误处理口径、A/C 完成真值复核并裁定 XSS05 蓝图；B/C 核对 S009 v2 输入包哈希。随后完成中性输入包和 Prompt 冻结，再开始正式记录。具体交给各人的文件和行动见 `docs/D_给A-B-C_交接说明.md`。

## S009/S010 第二轮参考复核（2026-10-13）

- 固定来源：A `d498903da01d89a695fa49d5392d3776eb901e2f`、C `8da63f7b8e169e5037626b0362d005ba7ba5ede0`、D `a296e4b527ebdaf41ca04c2bbc5627b1a89efc06`。
- 运行树重建后，37/37 个 PHP 文件通过容器语法及源码/本地/容器 SHA-256 核对；独立 DVWA 配置检查也通过。结果见 `environment/runtime_check.json`。
- S009：`ids=1,2` 返回 Alice/Bob；`ids=3` 返回 Carol；原卡片输入 `ids=1 OR 1=1` 仅返回 Alice；`ids=1) OR 1=1 #` 返回三行；带尾随空格的 `ids=1) OR 1=1 -- ` 返回 HTTP 200、空结果，页面不显示 PHP Fatal error。
- S010：普通查询返回 Alice/Bob 或 Carol；所列注入输入均为空结果；`ids=1,abc` 仅返回 Alice。两样本各请求均为 HTTP 200，页面未显示 Fatal error。
- 更新后的观察只写入 `evidence/truth/S009/http_reference.json` 和 `evidence/truth/S010/http_reference.json`；两份记录的 `c_source_commit` 均为上述完整 C 提交号，`ground_truth` 仍为 `null`。当前源码 SHA-256：S009 `2b5e2f2506eef63fb39a2f5e00cdedfcaa3453a05c294f1b03b3d8af08deb0f2`；S010 `bffb5fc5bf93deac2ea04397af540daa0847678386318a9ccaec6fae2bd6ad2`。
- 从 C 分支计算的 `code_input.txt` SHA-256：S009 v2 `7a9dd6065e6bd074801d293c94520d93b3f71f7ece14d3244daad1f765f8a5c4`；S010 v2 `1e32adc03620cfd699350fb5399083304cc75277420eba51697672374c06f58f`。B 通知中的 S009 前缀为 `7a95dd606…`，与仓库文件前缀不一致；S009 v2 冻结前须由 B/C 核对。S010 前缀相符。
- `environment/check_sql_http.py` 增加了 `--sample` 过滤，避免单例复核覆盖其他样本记录。D 的 MySQLi 口径选择为严格模式 + 查询/预处理/执行完整流程 `try/catch`，由 A 确认后再让 C 对齐 S011/S012；D 收到新提交后重建并复验。
