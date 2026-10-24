# A 代 C 技术复核：D 正式九条（2026-10-19）

复核执行：A（根据项目授权代 C 完成技术复核；不代签 C）
复核对象：D 运行的 S010、S011、S022 各 V0/V1/V2，共 9 条。
来源提交：`d/formal-nine`，基于 A 已完成四人冻结签字的 `5a7b5cb`。

## 复核结论

- 9/9 原文、规范化 JSON、metadata 和证据路径存在且可追溯；raw、input、Prompt、packet 哈希与正式计划一致。
- 9/9 `format_valid=true`，模型预测与独立真值一致：S010 safe、S011 vulnerable、S022 safe。
- 三条 S011 的模型位置 `F01:0008/F01:0013/F01:0015` 均落在 S011 v2 的合法行号范围，并准确覆盖 `sort` 输入、ORDER BY 拼接和 query 执行路径，`location_correct=true`。
- S010、S022 为 safe，位置字段保持 `null`。
- 9 条模型快照均记录为 `V4.1-Flash-1017`，显示名和冻结模型条件仍为 `DeepSeek-V4.1-Flash`、深度思考开、联网搜索关。

## POC 与 verification

- S010、S022 六条没有生成 POC，保持 `verification=not_run`。
- S011 V0 没有生成 POC，保持 `verification=not_run`。
- S011 V1 的 POC 仅访问 `127.0.0.1:4280`；适配版只修改入口路径，diff 已归档，原脚本失败原因和适配后成功结果均有记录，`environment_execution_ok=true`、`raw_execution_ok=false`。
- S011 V2 的原脚本未修改，仅通过 `ENTRY_PATH` 指定冻结样本入口；只访问 loopback，`raw_execution_ok=true`、`environment_execution_ok=true`。
- S011 V1/V2 的 `verification=triggered` 与执行日志、退出码和结果一致；未发现外部主机、Cookie 外带、写文件或删除动作。

## 状态记录

上述 9 条已从 `executed_pending_review` 改为 `reviewed`。`runs/formal.json` 保留冻结计划指定的 `reviewer=C`，本报告单独记录本次由 A 代行的技术复核事实；没有填写或伪造 C 的人工签名。
