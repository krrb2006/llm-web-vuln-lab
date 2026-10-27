# A 对 ADV 复核与哈希记录的收口说明（2026-10-26）

## 结论

D 已对 ADV 四条的模型判定、定位、原文、会话截图和本地漏洞版/修复版对照完成独立复核，结论为通过。D 复核后在 `9e36c49` 上按仓库 blob 的精确字节重算，发现原表值来自旧文件/格式化前版本；下表已按实际 blob 修正。

`D_review_ADV_2026-10-26.md` 中列出的四个值经复核为当前 blob 的实际 SHA-256；原表值不再使用。该修正不改变任何模型原文、`normalized.json` 内容、预测或动态验证结论。

## 当前状态

| run_id | metadata SHA-256 | 当前 `normalized.json` SHA-256 | 结果 |
|---|---|---|---|
| ADV_SECOND_SQLI_VULN | `71cf3b3c26f805671cc041cbfa41bf244efdf05024ca782b40b3de5dd5f2d3f0` | 相同 | 通过 |
| ADV_SECOND_SQLI_FIXED | `4be6b6ee70edc0eb66de02402813c3bfec3c7cdb50bc74120cc4f70f1836f278` | 相同 | 通过 |
| ADV_IDOR_VULN | `de4670de92788b616434636e850b3165fd4ef687685b978bb6b0b9ddf3ca585b` | 相同 | 通过 |
| ADV_IDOR_FIXED | `def0230a7c68bc2c6881a7263e9a58f8a4911acd8dfa6f0450b931e91ee20681` | 相同 | 通过 |

## 复核与执行边界

- bonus plan 的 ADV 四条 reviewer 已从 `A_self_review` 对齐为 `D`；四份 metadata 状态均为 `reviewed`。
- 四条 `poc_execution` 均为 `not_run`。本地 `ADV_runtime_recheck` 是代码路径的漏洞版/修复版对照，不能表述为模型原始 POC 已执行或已触发。
- 单条截图不显示精确模型版本或生成时间；版本口径仅按平台级说明记录，见 `A_model_provenance_update_2026-10-26.md`。

## D 复核补正（2026-10-26）

上述四个值已由 D 在 `9e36c49` 上按 `normalized.json` 精确字节复核；A 原表中的 `35ee.../b6df.../835d.../bf13...` 不匹配当前 blob，已由本表替换。ADV 状态仍为 D 复核、reviewed、POC `not_run`。
