# S001 官方注入证据对账（A，2026-10-23）

本记录只说明 A 对 B 修正版的技术核对，不替代 C 的独立复核，也不改变 `experiments/bonus_runs.plan.json` 中 8 条记录的 `planned` 状态。

## 已由 B 修正版解决

- `INJ_SQLI_*` 8 条均已有完整 `runs/<run_id>/input.txt`。
- 8 条 `input.txt` 的 SHA-256 均与对应 `metadata.json.input_sha256` 一致。
- 8 条原始回答哈希均与 `metadata.json.raw_output_sha256` 一致。
- `INJ_SQLI_SAFE_BASE/normalized.json` 已改为 `format_valid=false`，并列出缺失的 `prerequisites`、`missing_context`、`poc_generated`、`poc_language`、`poc_instructions` 五个字段。
- 原始模型回答未被改写，POC 仍未执行。

## 仍需 C 独立确认的限制

- 设置截图为共享证据，不能单独证明每条会话的页面模型名称；metadata 的模型名称限制仍应保留。
- `SAFE_BASE` 原文格式不完整，但其漏洞判断和定位内容仍需按 C 的复核规则单独裁定。
- 其他 7 条的格式、输入包内容、Prompt 哈希、正常业务回归和证据路径仍由 C 在 PR #23 中重新确认。

## A 当前裁定

在 C 更新 PR #23 并明确接受/拒绝上述限制前，不把 8 条从 `planned` 改为 `reviewed`，也不把加分统计从 `14/26` 提前改写。
