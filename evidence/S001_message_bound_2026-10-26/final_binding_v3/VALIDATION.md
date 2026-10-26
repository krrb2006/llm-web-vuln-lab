# 最终补充绑定自检

2026-10-26，候选补充位于本目录。每条 source_binding.json 导出仅对应的源用户消息，记录原消息 ID、源日志名和行号、消息文本提取起止下标、去除的用户编号后缀、源导出哈希。可由导出逐字恢复对应 raw；没有冒充 DeepSeek 会话日志。

本轮检查：

- tools/verify_s001_final_binding.py：8 条消息边界、源导出哈希、工作树字节/LF/Git哈希、执行状态通过。
- tools/check_s001_message_archive.py：8 条严格 JSON、raw/normalized、Prompt/input/packet 一致，且仅 PHP 注释有差异；通过。
- verify_s001_poc_results.py：8 条原始模型代码与保存脚本相等，5 类辅助 HTTP 响应业务记录相符；通过。该检查不启动 Docker，不重写历史证据。
- python -m pytest -q：23 passed, 3 subtests passed。
- tools/audit_submission.py：基础可提交，B 分支加分计数12/26。B旧计划两条Burp仍planned，项目整体14/26以A整合分支为准。
- tools/check_freeze.py --report-only：READY。

source_export_unavailable 对 DeepSeek 原始会话仍为 true。完整实际输入的来源依据为用户明确确认；精确模型版本、生成时设置仍未独立证明。POC 是历史实操结果，未补造完整命令、解释器路径、工作目录、结束时间和逐条完整抓包。捕获哈希已记录但原捕获字节未独立保存时，明确标为未保存，不从规范文本推造原字节。

两个旧验证脚本现为只读检查，防止自检把 poc_executed 重写回 false 或将缺失Docker输出写进历史日志。旧 raw、截图、normalized 和执行日志保留。

交C的一次性候选：本补充目录 + 上级8条原文/输入/截图 + evidence/S001_poc_verified_2026-10-26。保持 planned、不计入S001完成数；无需用户重跑模型或重复发材料。独立模型会话证据限制由C/A最终裁定。
