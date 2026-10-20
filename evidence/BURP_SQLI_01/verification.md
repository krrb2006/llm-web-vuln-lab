# 加分实验验证记录：BURP_SQLI_01

run_id：BURP_SQLI_01
category：burp_linkage
sample_id 与 condition：S009（vulnerable，Repeater 真条件）+ S010（paired control，同一 payload）
执行人、复核人：D / A
模型或工具完整版本：Burp Suite Community Edition v2026.9.2；Chrome 155.0.8059.84（历史截图）；本地 MariaDB 10.11
开始时间与结束时间：2026-10-13 12:14–13:00（UTC）；冻结源码复跑 2026-10-19 22:57（UTC+8）
输入包、Prompt、目标源码 SHA-256：S009 `2b5e2f2506eef63fb39a2f5e00cdedfcaa3453a05c294f1b03b3d8af08deb0f2`；S010 `bffb5fc5bf93deac2ea04397af540daa0847678386318a9ccaec6fae2bd6ad2`；冻结提交 `6cd58b3`
完整输入或 Burp 请求路径：`S009_request.raw.txt` / `S009_response.raw.txt`（S009 受控条件完整 raw）；其余三条见 `burp_repeater_observation.json` 与 `burp_proxy_observation.json`
模型原文、Burp 响应或运行日志路径：见全部证据路径；LLM 结论对应 `runs/F_S009_V2_R1`（C，reviewed，prediction=vulnerable）
与对照组唯一变化：`ids=1` vs `ids=1) OR 1=1 #`；S010 使用同一受控条件作配对
人工安全检查：仅 GET `127.0.0.1:4280`；无 Cookie、无写操作、无外部主机、无删除
执行命令或操作步骤：Burp Proxy 记录正常/受控请求 → Send to Repeater → 手工 Send；2026-10-19 用 Python urllib 在冻结源码上重放同一请求
实际观察：S009 正常 1 行（Alice），受控 3 行（Alice/Bob/Carol）；S010 正常 2 行，受控 0 行；均 HTTP 200，无 Fatal；Repeater 与 frozen_recheck 结果一致
主结论：Burp 重放能稳定复现 S009 的条件变化、S010 无变化；支持 F_S009_V2 的 vulnerable 结论，HTTP 200 未被当作成功条件
替代解释与排除依据：历史 Burp 抓包早于正式 LLM 结论；已在冻结源码上重放确认行为未变，差异仅来自输入条件
是否影响主实验：否；只作为独立加分实验
全部证据相对路径：`evidence/BURP_SQLI_01/` 下 verification、观察 JSON、S009 raw、frozen_recheck、screenshots/
执行人签名与日期：D（linan）2026-10-19 23:00（UTC+8）
复核人签名与日期：
