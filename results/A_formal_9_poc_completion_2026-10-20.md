# A 负责 9 条正式记录：POC 补齐与证据边界

复核人：A　日期：2026-10-20（Asia/Shanghai）

## 结论

- S007 V0/V1/V2 的 POC 原文已从 D 的独立复核材料逐字归档到 `pocs/F_S007_V*_R1/original.py`。D 已在冻结源码和本地环境执行，三条均 exit 0，并观察到预期 SQL 条件变化；对应执行日志仍保留在 `results/D_review_A_pocs/`。
- S021 V0/V1/V2 的 POC 原文已归档到 `pocs/F_S021_V*_R1/original.py`。脚本只访问 `127.0.0.1:4280`，不读取 Cookie、不向外部主机发送数据；D 已完成静态安全复核，但未执行浏览器 marker 观察，因此本记录不声称三条已触发 XSS。
- S020 V0/V1/V2 的模型结果为 safe，`poc_generated=false`，不补造 POC。
- `runs/formal.json` 的六条 vulnerable 记录已补入对应 POC 原文路径。`verification` 仍保持 `not_run`，因为 POC 执行证据与每条正式模型 run_id 尚未形成完整的一一绑定。

## 尚缺证据

本轮没有新增 A 的正式运行 settings/answer 截图，也没有新增 S021 三条浏览器 marker 截图。D 的 S007 执行日志、Burp/DOM 参考截图和其他样本证据不替代正式 run-specific 截图；因此不把这些材料改写成正式截图或 XSS 触发结论。

## 复核范围

本文件只记录 A 侧补齐和证据边界，不改变 36 条主实验的 prediction、ground truth、统计结果或已审核状态。
