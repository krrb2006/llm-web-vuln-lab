# A 对 S001 官方 SQLi Prompt Injection 的最终裁定（2026-10-24）

## 裁定

S001 官方 `INJ_SQLI_*` 八条继续保持 `planned`，不改为 `reviewed`，也不计入当前加分可读证据数量。

## 依据

- C 已独立确认八条首个 JSON 的 SQLi 预测和关键定位均通过，但综合结论为“有条件接受”。
- `INJ_SQLI_SAFE_BASE` 原文缺少 `prerequisites`、`missing_context`、`poc_generated`、`poc_language`、`poc_instructions` 五个字段，原文格式不通过；修正后的 `normalized.json` 已如实标记 `format_valid=false`，没有改写原文。
- 八条 `metadata.json` 均缺少 `raw_output_sha256`；raw 文件虽可读取，但未由 metadata 绑定。
- 八条 `input.txt` 属于事后重建，不能证明原会话逐字提交了同一输入；设置截图为共享截图，不能逐条证明会话模型名称和会话绑定。
- POC 均未执行，不能把静态判断表述为真实触发。

## 统计与后续

当前加分证据仍为 `14/26`。S001 如需转为 `reviewed`，至少需要解决上述证据限制并由 B/C 重新确认；在此之前保留原始记录、限制说明和 `planned` 状态。
