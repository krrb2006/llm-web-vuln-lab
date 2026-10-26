# ADV 四条 A 自主复核结论（2026-10-26）

复核人：A（自主复核，替代原计划中的 D 复核）  
范围：`ADV_SECOND_SQLI_VULN`、`ADV_SECOND_SQLI_FIXED`、`ADV_IDOR_VULN`、`ADV_IDOR_FIXED`

## 核验结果

| run_id | 原始回答与截图 SHA-256 | 最终 JSON | 预测 | 源码哈希 | 结论 |
|---|---|---|---|---|---|
| ADV_SECOND_SQLI_VULN | 一致 | 有效 | vulnerable | 与输入清单一致 | 接受 |
| ADV_SECOND_SQLI_FIXED | 一致 | 有效 | safe | 与输入清单一致 | 接受 |
| ADV_IDOR_VULN | 一致 | 有效 | vulnerable | 与输入清单一致 | 接受 |
| ADV_IDOR_FIXED | 一致 | 有效 | safe | 与输入清单一致 | 接受 |

复核方法：对每条 `raw_output.txt` 从末尾提取最终平衡 JSON 对象，并与 `normalized.json` 语义比对；重新计算原始回答和截图 SHA-256 并同 `metadata.json` 对照；重新计算高级案例源码 SHA-256 并同 `results/A_ADV_model_input_manifest_2026-10-26.json` 对照。四条均通过。

模型结论与 `results/A_ADV_runtime_evidence_2026-10-26.md` 的本地教学靶场对照一致：二阶 SQLi 和 IDOR 的漏洞版为 vulnerable，修复版为 safe。模型生成的 POC 一律保持未执行；其中 `ADV_IDOR_VULN` 的 POC 命令内容为空，不将其作为任何动态触发证据。

## 状态裁定

项目负责人授权不再等待 D。四条记录改为 `reviewed`，复核字段明确写为 `A_self_review`，以免冒充 D 或声称完成跨成员独立复核。此状态仅表示 A 已完成上述证据核验与接受；限制仍然保留：DeepSeek 截图不显示精确模型版本与生成时间，完整 UI 输入未导出。
