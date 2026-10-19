# R1 R12 文档原文归档说明

用户确认 `R1-R12.docx` 是真实模型回答来源，且这些回答属于 V1。B 已使用用户提供的顺序修正版文档提取 12 条 V1 原文，覆盖 S001—S006、S013—S018；S017/S018 的标题和 `sample_id` 已按正确顺序对应。此前仓库中已归档的 12 条 DeepSeek 回答继续作为 V0。

## 归档规则

- 文档区块被保存为各 `runs/DEV_*_V1_R1/raw_output.txt`，并在 `metadata.json` 写入 `raw_source=R1-R12.docx`、源文件路径和提取说明。
- 仓库原有的 V0 原文和规范化记录已从 `raw_previous_chat.txt`、`normalized_previous_chat.json` 恢复；没有删除历史证据。
- V1 的 `normalized.json` 已重新检查 JSON 字段、预测枚举、输入包中的 Fxx 行号和 POC 格式。
- 文档版 V1 结果 12/12 可解析，预测标签为 6 条 vulnerable、6 条 safe；POC 方案按原文状态保留，没有执行。
- 这次纠正只调整 V0/V1 的归属和来源元数据，不改变 Prompt 文本、输入包哈希或正式测试计划。

## 关键顺序核对

|文档标题|JSON sample_id|预测|
|---|---|---|
|S017|S017|vulnerable|
|S018|S018|safe|

S017/S018 的顺序错位已在交付文档副本中修正后再提取；仓库运行目录现在与该修正版一致。
