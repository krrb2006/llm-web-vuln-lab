# A 对 CTX 四条记录的最终技术复核

日期：2026-10-20（Asia/Shanghai）

A 已对 `CTX_S007_ENTRY`、`CTX_S007_FULL`、`CTX_S020_ENTRY`、`CTX_S020_FULL` 的输入、metadata、模型原文、规范化 JSON、Prompt 类型和 SHA-256 进行程序化核验。

复核结论：四条证据完整，格式有效，样本类型与 Prompt 一致，输入哈希和原文哈希均一致，计划状态更新为 `reviewed`。

|记录|Prompt/类型|预测|格式|POC执行|
|---|---|---|---|---|
|CTX_S007_ENTRY|SQLi_V2 / SQL注入|uncertain|有效|未执行|
|CTX_S007_FULL|SQLi_V2 / SQL注入|vulnerable|有效|未执行|
|CTX_S020_ENTRY|XSS_V2 / XSS|uncertain|有效|未执行|
|CTX_S020_FULL|XSS_V2 / XSS|safe|有效|未执行|

S007 的旧 XSS_V2 错配记录仍保留在 `experiments/context_ablation/runs/CTX_S007_*`，不作为本次有效对照证据。修正后的 S007 证据位于 `experiments/context_ablation/prepared_sqliv2_rerun/`。

本次 `reviewed` 只表示证据与输出的独立技术复核完成，不表示 POC 已触发；四条 `normalized.json` 的 `human_verification` 仍为 `pending`。CTX 仍不纳入 36 条正式统计。
