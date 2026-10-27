# A 侧 S013 Prompt Injection 输入包技术复核

日期：2026-10-20（Asia/Shanghai）

范围：`experiments/prompt_injection/official_packets/S013/` 四个候选攻击包。

## 结果

|攻击类别|manifest 哈希|行数一致|差异行数|差异位置|技术结论|
|---|---|---|---|---|---|
|`ignore_task`|通过|通过|1|F01:0002 注释|通过|
|`force_safe_verdict`|通过|通过|1|F01:0002 注释|通过|
|`request_hidden_rules`|通过|通过|1|F01:0002 注释|通过|
|`divert_output`|通过|通过|1|F01:0002 注释|通过|

四个候选包均保留 `<sample_id>`、`runtime_context`、`<untrusted_code>` 和所有 F 行；差异只发生在原有 PHP 注释行，未改变可执行 PHP 代码。S013 源码 LF SHA-256 为：

`154456e20c0d4adc6febf6945c6d14c2b97722a38746a4c7ae1fa87a24a6cb4f`

## 边界

- 这是一份 A 侧技术复核，不是 B 对攻击语义的独立复核。
- 尚未调用模型、尚未产生 raw output、尚未执行 POC。
- `bonus_runs.plan.json` 中 S013 的 8 条仍全部为 `planned`。
- B 需要确认四条文本是否准确覆盖 `ignore_task`、`force_safe_verdict`、`request_hidden_rules`、`divert_output`，确认后 C 才开始 8 条正式运行。

