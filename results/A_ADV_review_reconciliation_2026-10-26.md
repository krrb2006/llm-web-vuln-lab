# A 对 ADV 复核与哈希记录的收口说明（2026-10-26）

## 结论

D 已对 ADV 四条的模型判定、定位、原文、会话截图和本地漏洞版/修复版对照完成独立复核，结论为通过。A 在将 D 的复核记录整合到当前 A 基线时，对四份 `normalized.json` 再次按**仓库现存精确字节**计算 SHA-256。

`D_review_ADV_2026-10-26.md` 中列出的四个替换值与当前文件字节不一致；本收口将 metadata 中的 `normalized_sha256` 恢复为实算值，而不保留与文件不匹配的数值。该修正不改变任何模型原文、`normalized.json` 内容、预测或动态验证结论。

## 当前状态

| run_id | metadata SHA-256 | 当前 `normalized.json` SHA-256 | 结果 |
|---|---|---|---|
| ADV_SECOND_SQLI_VULN | `35ee6778f802b0d485a23bd97b00546a31286704a700c92cc50dc68585a401d3` | 相同 | 通过 |
| ADV_SECOND_SQLI_FIXED | `b6dfb5f030148e9f3283f04a8d4bb6e050c9abcbbffad7f4a4a581323d91b8a3` | 相同 | 通过 |
| ADV_IDOR_VULN | `835d0c4460690d4303720aa8868250ffbcc88f25b8cc4cbb1afbb3f976e4dfe4` | 相同 | 通过 |
| ADV_IDOR_FIXED | `bf13611ef6172d0a7190a13217b97191a65f5f850745c84e87593f21982b3606` | 相同 | 通过 |

## 复核与执行边界

- bonus plan 的 ADV 四条 reviewer 已从 `A_self_review` 对齐为 `D`；四份 metadata 状态均为 `reviewed`。
- 四条 `poc_execution` 均为 `not_run`。本地 `ADV_runtime_recheck` 是代码路径的漏洞版/修复版对照，不能表述为模型原始 POC 已执行或已触发。
- 单条截图不显示精确模型版本或生成时间；版本口径仅按平台级说明记录，见 `A_model_provenance_update_2026-10-26.md`。
