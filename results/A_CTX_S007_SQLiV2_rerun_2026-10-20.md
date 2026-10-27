# A 对 S007 SQLi_V2 CTX 修正重跑的复核记录

日期：2026-10-20（Asia/Shanghai）  
范围：C 准备的 `prepared_sqliv2_rerun/CTX_S007_ENTRY` 与 `CTX_S007_FULL`。旧的 XSS_V2 错配记录仍保留在 `experiments/context_ablation/runs/CTX_S007_*`，本记录不覆盖它们。

## 运行与完整性

两条新会话均使用 `SQLi_V2`，Prompt SHA-256 为 `8f2fcafb576e990d1ef27527ce558830558fb87ea189ab32d8c10514e9c620ca`，模型为 `DeepSeek-V4.1-Flash`，深度思考开启、联网搜索关闭。提交时间未由界面导出，metadata 使用明确的 time note，没有伪造时间戳。

|run_id|输入哈希|原文哈希|格式|预测|类型|POC|
|---|---|---|---|---|---|---|
|`CTX_S007_ENTRY`|一致|一致|`true`|`uncertain`|SQL注入|未生成|
|`CTX_S007_FULL`|一致|一致|`true`|`vulnerable`|SQL注入|仅生成，未执行|

两条记录均为 `executed_pending_review`，`human_verification` 保持 `pending`。FULL 的模型原文包含本地 POC 文本，但没有执行该 POC；不能把它写成漏洞已触发。

## 对照解释

ENTRY 只有入口文件，关键 `repository.php` 查询实现缺失，因此模型给出 `uncertain`；FULL 包含跨文件查询实现，模型识别到 `$name` 拼接进入 SQL，给出 `vulnerable`。这组差异现在是在同一 `SQLi_V2` 类型契约下产生的，可作为 CTX 的有效观察，但仍不进入 36 条正式统计。

## 复核边界

本记录完成 A 侧技术复核与证据完整性检查，不代替另一名成员对 CTX 的独立签字；计划状态仅为 `executed`，未改为 `reviewed`。生成的 POC 仍未执行，旧错配记录继续作为审计历史保留。
