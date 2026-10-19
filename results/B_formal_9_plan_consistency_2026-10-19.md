# B 正式九条计划一致性检查

检查对象：B 负责的 `F_S008_*`、`F_S019_*`、`F_S024_*` 共 9 条；对应回答来源为 `S001-s024.docx`。本检查只验证计划锁定字段、输入包、Prompt、JSON 和原文哈希，不代替 A 的正式审核。

|检查|结果|
|---|---:|
|正式计划与运行元数据 sample/version 一致|9/9|
|模型名称与冻结批次一致|9/9|
|Prompt SHA-256 一致|9/9|
|code_input packet SHA-256 一致|9/9|
|完整输入 SHA-256 一致|9/9|
|模型原文 SHA-256 已保存|9/9|
|JSON/字段/行号格式通过|9/9|
|正式审核状态|0/9，仍为 planned，待 A 复核|

当前模型标签：S008 V0/V1/V2=`safe`；S019 V0/V1/V2=`vulnerable`；S024 V0/V1/V2=`safe`。这些是模型原文中的 prediction，不是 B 自行确认的最终正式结论。

尚未填写或确认的字段包括 `reviewer`、`location_correct`、POC 执行阶段、`verification`、`evidence_paths` 和正式审核状态。POC 未执行，不能填写 `triggered`；A/D/C 需要根据对应源码、浏览器/HTTP证据和人工安全审阅完成这些字段后，才能运行最终统计。
