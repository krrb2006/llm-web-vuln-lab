# A 代 D 二次技术复核：B 正式九条（2026-10-19）

复核执行：A（根据项目授权代 D 完成二次技术复核；不代签 D）
复核对象：B 运行的 S008、S019、S024 各 V0/V1/V2，共 9 条。

## 复核结论

- 9/9 原文、规范化 JSON、metadata 和 evidence_paths 存在且可追溯；raw、input、Prompt、packet 哈希与正式计划一致。
- 9/9 `format_valid=true`，模型预测与真值一致：S008 safe、S019 vulnerable、S024 safe。
- S019 三条位置引用均落在合法行号范围，且覆盖输入流、输出/模板 sink；`location_correct=true`。
- S008、S024 为 safe，位置字段保持 `null`。
- 9 条记录的模型显示名、模型设置、Prompt 版本和输入包均与冻结计划一致；没有跨样本混包。

## POC 与验证边界

- S008、S024 未生成 POC，保持 `verification=not_run`。
- S019 的输出包含静态 POC 方案，但没有执行脚本；目标约束为本地实验地址，正式记录保持 `verification=not_run`、`raw_execution_ok=false`、`environment_execution_ok=false`。
- 本次二次复核没有执行任何模型 POC，也没有把静态 POC 方案或既有参考证据改写为正式触发证据。

## 状态记录

9 条原记录已经由 A 完成主审核并为 `reviewed`；本报告记录 D 角色的独立二次技术复核结果，不改正式计划指定的 primary reviewer，也不填写或伪造 D 的人工签名。
