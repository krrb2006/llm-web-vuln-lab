# ADV Prompt 映射裁定 2026 10 26

## 映射

- `ADV_SECOND_SQLI_VULN`、`ADV_SECOND_SQLI_FIXED`：使用冻结 `SQLi_V2`，因为两条记录属于二次 SQL 注入对照。
- `ADV_IDOR_VULN`、`ADV_IDOR_FIXED`：使用新增 `IDOR_V2`，因为两条记录的核心问题是对象级授权/越权，不是 SQL 注入。

`IDOR_V2` 是 ADV 专用 Prompt，不修改六份冻结 Prompt，不回写主实验计划。
SHA-256：`3819ae6180e4c264188d752a18a2a1d395c05c51e11e2bdd8830e72cd1479af0`。

## 状态边界

四条 ADV 在模型会话、POC、本地修复对照和独立复核完成前保持 `planned`。本地环境证据只能证明代码运行结果，不能替代模型记录。
