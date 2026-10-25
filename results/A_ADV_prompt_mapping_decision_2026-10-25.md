# ADV Prompt 映射裁定（2026-10-25）

## 已确认

- `SECOND_SQLI_01` 的目标是二次 SQL 注入，正式模型记录可以使用已冻结的 `SQLi_V2`，但仍须生成独立输入、原文、规范化结果、metadata 和设置证据。
- `IDOR_01` 的目标是对象所有权/授权逻辑缺陷，不是 SQL 注入。现有冻结 Prompt 集合只有 SQLi 与 XSS，没有合法的 IDOR/授权专项 Prompt。

## 当前决定

- 不把 `SQLi_V2` 冒充为 IDOR 专项 Prompt。
- 不为 IDOR 伪造模型输出、运行记录或 reviewed 状态。
- 四条 `ADV_*` 在取得合法 Prompt 映射、模型会话和 D 独立复核前继续保持 `planned`。
- 本机 Docker 运行证据单独保存为 `results/A_ADV_runtime_evidence_2026-10-25.json`，它证明业务对照，不替代模型证据。

## 可继续的最短路径

1. 若课程允许沿用统一安全审计 Prompt，由 A 明确批准一个 IDOR/授权逻辑 Prompt，并记录新 Prompt 文本、SHA-256 与变更理由。
2. 先运行 `SECOND_SQLI_01` 的 vulnerable/fixed 两条模型记录，再由 D 独立复核。
3. Prompt 冻结后再运行 IDOR 两条；不得把环境测试结果直接填入正式 `runs`。
