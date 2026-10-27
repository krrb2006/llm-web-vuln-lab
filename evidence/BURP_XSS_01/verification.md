# 加分实验验证记录：BURP_XSS_01

run_id：BURP_XSS_01
category：burp_linkage
sample_id 与 condition：S021（vulnerable，marker POST + preview）+ S022（paired control）
执行人、复核人：D / A
模型或工具完整版本：Burp Suite Community Edition v2026.9.2；Edge/Chrome 155；本地 MariaDB 10.11
开始时间与结束时间：2026-10-13 11:27–11:47（UTC）；冻结源码复跑 2026-10-19 22:58（UTC+8）
输入包、Prompt、目标源码 SHA-256：S021 `25b8c4949b372a9beae8e4b2e7a44899318f745d4e97c99aeedd8fc4e7d734b6`；S022 `c80d5c884abbf698ab9621e8b85788e2f8bdaf8e83c666e15d92ba31a78dc943`；冻结提交 `6cd58b3`
完整输入或 Burp 请求路径：`burp_proxy_observation.json` 中 S021/S022 的 normal/marker submit、list、preview；浏览器 DOM 观察同文件 `browser_observations`
模型原文、Burp 响应或运行日志路径：LLM 结论对应 `runs/F_S021_V2_R1`（A，reviewed，prediction=vulnerable）；DOM/截图见下
与对照组唯一变化：普通正文 vs 只设置 `document.documentElement.dataset.labXss='yes'` 的 marker
人工安全检查：仅 POST/GET `127.0.0.1:4280`；marker 不读 Cookie、不发外部请求；演示后按唯一标题清理
执行命令或操作步骤：Burp Proxy 记录 normal/marker POST 与 list/preview GET → 对应请求 Send to Repeater → 浏览器经同一代理观察 DOM
实际观察：S021 marker preview 的 HTML 保留原始 `<script>`，浏览器 `html[data-lab-xss="yes"]`；S022 预览把 `<script>` 转义、无该属性；均无 Fatal
主结论：Burp 请求与浏览器 DOM 联动能区分 S021 执行与 S022 转义，支持 F_S021_V2 的 vulnerable 结论
替代解释与排除依据：历史 Burp 抓包早于正式 LLM 结论；冻结源码 frozen_recheck 显示 S021 仍输出原始 script、S022 仍转义
是否影响主实验：否；只作为独立加分实验
全部证据相对路径：`evidence/BURP_XSS_01/` 下 verification、burp_proxy_observation、frozen_recheck、screenshots/
执行人签名与日期：D（linan）2026-10-19 23:00（UTC+8）
复核人签名与日期：A（当前分支内容复核）2026-10-20
