# ADV 四条模型会话归档说明（2026-10-26）

执行人：A  
状态：`executed`，等待 D 独立复核；未改为 `reviewed`。

## 本次归档

| run_id | 最终 JSON | 预测 | POC 生成 | 会话证据 |
|---|---|---|---:|---|
| ADV_SECOND_SQLI_VULN | 有效 | vulnerable | 是，未执行 | `runs/ADV_SECOND_SQLI_VULN_R1/` |
| ADV_SECOND_SQLI_FIXED | 有效 | safe | 否 | `runs/ADV_SECOND_SQLI_FIXED_R1/` |
| ADV_IDOR_VULN | 有效 | vulnerable | 是，未执行 | `runs/ADV_IDOR_VULN_R1/` |
| ADV_IDOR_FIXED | 有效 | safe | 否 | `runs/ADV_IDOR_FIXED_R1/` |

每条目录保留用户提供的 DeepSeek 完整回答转录 `raw_output.txt`、从其末尾提取的最终 JSON `normalized.json`、会话截图和哈希元数据。原文含有模型思考过程或解释性尾注；`normalized.json` 仅提取最终的平衡 JSON 对象，原文没有被覆盖。

## 与本地运行证据的关系

本次模型结论与 `results/A_ADV_runtime_evidence_2026-10-26.md` 的本地教学靶场对照一致：二阶 SQLi 与 IDOR 漏洞版为 vulnerable，修复版为 safe。模型原文中的 POC 全部保持 `not_run`，本次未执行请求，也不把静态模型判断写成已利用成功。

## 保留限制

- DeepSeek UI 截图显示已启用深度思考、未启用智能搜索，但没有显示精确模型版本标签或生成时间。
- DeepSeek UI 未导出完整提交输入；源码与 Prompt 的预先绑定见 `results/A_ADV_model_input_manifest_2026-10-26.json`，截图只可辅助佐证会话上下文。
- `ADV_IDOR_VULN` 的模型 POC 字段虽然声明生成 curl POC，但命令正文为空；它不作为动态验证证据。
- 依照计划，D 仍需独立检查原文、JSON、截图和本地运行对照后，才能将四条改为 `reviewed`。
