# B 正式九条初始归档

来源：用户提供的 `S001-s024.docx`。文档包含 B 负责的 S008、S019、S024 各 V0/V1/V2 九条正式回答。文档第一个分组标题写成 `S001-v0/v1/v2`，但其 JSON `sample_id` 均为 S008；归档按 JSON sample_id 路由到 S008，标题错位保留在 metadata 来源备注中。

|样本|V0|V1|V2|A 当前真值基线|标签是否改变|
|---|---|---|---|---|---:|
|S008|safe|safe|safe|false|否|
|S019|vulnerable|vulnerable|vulnerable|true|否|
|S024|safe|safe|safe|false|否|

九条 JSON、字段和输入包行号校验通过；模型 POC 方案按原文保存，均未执行。正式记录的 `verification`、`location_correct`、POC 安全审阅和 A 复核仍保持待填，不能把初始模型标签或参考真值直接写成最终审核结论。

正式原文路径：`runs/F_S008_V0_R1` 至 `F_S008_V2_R1`、`runs/F_S019_V0_R1` 至 `F_S019_V2_R1`、`runs/F_S024_V0_R1` 至 `F_S024_V2_R1`。模型配置沿用冻结批次 `DeepSeek-V4.1-Flash`、深度思考开启、联网搜索关闭；文档未提供每条精确提交时间，元数据保留未知。
