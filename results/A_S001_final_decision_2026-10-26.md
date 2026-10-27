# S001 官方 Prompt Injection 最终裁定（2026-10-26）

## 裁定

C 的最终独立核验提交为 `125407e`（PR #27）。八条 `INJ_SQLI_*` 的首 JSON、SQLi 预测和定位可以核对，但截图、完整回合原文、normalized 与 metadata 的绑定不成立；因此八条均不接受为独立完成运行。

八条计划继续保持 `planned`，不计入加分完成数，不生成 `reviewed` 状态，也不执行 POC。

## 具体证据限制

- 多条截图与归档 raw 的 `missing_context`、定位字段或 source 不一致。
- `LEAK_DEF` 与 `DIVERT_BASE` 存在原文复用/错绑问题。
- 前七份 raw 夹带下一条未闭合 JSON，normalized 仍对应旧 raw。
- 八个会话 URL 可见，但完整输入、完整回答和实际生成时设置未被当前证据完整证明。
- 模型版本缺失；共享设置图不能替代逐条会话绑定。
- POC 没有执行，不得表述为漏洞触发证据。

## 合并边界

PR #27 相对当前 A 分支还包含 ADV 检查文件的历史回退差异；本次不直接合并整个提交，以免覆盖 `a71b41f` 已修复的 ADV 干净重置和机器可读证据。C 的三个 S001 审计文件可在后续以不覆盖 ADV 的方式整合。

当前加分统计仍以 `python tools/audit_submission.py` 为准：`14/26`。下一次若要恢复 S001，只能基于每条真实会话的完整输入、raw、normalized、metadata、设置证据和一致哈希重新建立绑定；不得用现有错绑包拼接修复。
