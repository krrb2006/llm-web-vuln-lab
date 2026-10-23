# ADV 加分实验本轮裁定

裁定人：A　日期：2026-10-20（Asia/Shanghai）

## 裁定

本轮放弃/延期 `ADV_SECOND_SQLI_VULN`、`ADV_SECOND_SQLI_FIXED`、`ADV_IDOR_VULN`、`ADV_IDOR_FIXED`，不运行、不计分、不宣称已完成。

## 依据

D 的预审报告 `results/D_review_advanced_cases_2026-10-20.md` 已确认：当前环境存在 `$conn`/`$db` 接线不一致，缺少 `profiles`/`invoices` 表和种子数据，advanced case 未挂载进靶场，IDOR 缺少 A/B 会话初始化，二次注入缺少成对回归数据。现阶段补跑会产生不可复现或无法完成对照的结果。

## 计划文件处理

`tools/audit_submission.py` 规定 bonus plan 状态只能是 `planned`、`executed`、`reviewed`，因此四条 ADV 保留为 `planned`，并以本裁定明确为“本轮未完成/不计分”，不另造非法的 `abandoned` 状态。若后续要救 ADV，应先由 D 补齐环境与第二台电脑复现，再单独新增真实运行记录。
