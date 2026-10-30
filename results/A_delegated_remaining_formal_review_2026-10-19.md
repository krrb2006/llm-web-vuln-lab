# A delegated technical review of remaining formal records

日期：2026-10-19（Asia/Shanghai）
复核执行：A（按用户授权代行技术复核）

## 范围

本记录覆盖本轮已由 DeepSeek Web 独立会话生成并归档的 8 条正式回答：

- A operator 分组：S007 V0/V1/V2、S020 V0/V1/V2、S021 V0/V1

每条记录均保留原始输出、规范化结果、输入包哈希与原文哈希。`runs/formal.json` 中的 reviewer 字段仍保留冻结计划规定的责任人；本文件只说明 A 的代行技术检查，不构成对 B 或 D 的冒名签字。

## 检查项

1. `normalized.json` 的回答格式和必需字段通过校验。
2. vulnerable 回答的代码定位属于对应正式输入包，safe 回答不要求定位正确布尔值。
3. POC 仅检查生成格式；本轮没有执行模型生成的 POC，因此 `raw_execution_ok=false`、`environment_execution_ok=false`、`verification=not_run`。
4. 预测值按模型原文登记，不因奇偶真值基线而改写模型输出。

## 结果摘要

|样本|V0|V1|V2|POC执行|
|---|---|---|---|---|
|S007|vulnerable|vulnerable|vulnerable|均未执行|
|S020|safe|safe|safe|均未执行|
|S021|vulnerable|vulnerable|待运行|V0/V1未执行|

S021 V2 因上传失败尚未产生模型回答，仍保持 `planned`，不在本次登记范围内。

## 签字边界

本文件不是 B/C/D 的冻结签字，也不替代责任人对其分配条目的最终确认；它只为当前工作流提供可审计的 A 代技术复核记录。
