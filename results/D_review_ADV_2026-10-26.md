# D 独立复核：ADV 四条（2026-10-26）

复核人：D（ADV 指定 reviewer）
对象：`runs/ADV_SECOND_SQLI_VULN_R1`、`ADV_SECOND_SQLI_FIXED_R1`、`ADV_IDOR_VULN_R1`、`ADV_IDOR_FIXED_R1`
基线：`a/criteria-and-sql01@9e36c49`

## 一、结论

**判定层：4/4 通过；D 对 ADV 四条的证据复核通过。**

本 PR 已修正 4 条 `normalized_sha256`，现在与当前 `normalized.json` 精确字节一致。

A 已在 `9e36c49` 完成：

1. plan 的 ADV reviewer 已从 `A_self_review` 改为 `D`；
2. metadata 状态已改为 `reviewed`，与 plan 对齐。

仍需在报告中写明：

1. POC 未执行（`poc_execution=not_run`）；
2. 截图没有模型版本/时间戳，只能按平台级说明。

## 二、判定核对

| run | prediction | 期望 | 结论 |
|---|---|---|---|
| `ADV_SECOND_SQLI_VULN_R1` | vulnerable | vulnerable | 一致 |
| `ADV_SECOND_SQLI_FIXED_R1` | safe | safe | 一致 |
| `ADV_IDOR_VULN_R1` | vulnerable | vulnerable | 一致 |
| `ADV_IDOR_FIXED_R1` | safe | safe | 一致 |

4/4 判定方向正确。

## 三、证据核对

### 通过项

- 4/4 `raw_output.txt` 存在；
- 4/4 `raw_output_sha256` 与 raw 文件**精确字节**一致；
- 4/4 `session_screenshot.png` 存在，SHA-256 与 metadata 一致；
- 4/4 有 `session_url`；
- 截图可见：会话 URL、回答区域、深度思考开/智能搜索关；
- A 的 `ADV_runtime_recheck_2026-10-26.json` 本地运行对照支持：
  - SECOND_SQLI vulnerable/fixed 响应长度 33/15；
  - IDOR vulnerable 返回他人 owner 202，fixed 为空。

### 本 PR 已修复

1. **normalized 哈希 4/4 不一致** → 已按当前 `normalized.json` 精确字节重算并写入 metadata；现在 4/4 匹配。

### A 已完成的流程项

1. **metadata 状态与 plan 已对齐**：`reviewed`、`reviewer=D`。

### 仍需在报告中写明

1. **POC 未执行**  
   4/4 `poc_execution=not_run`。如果 ADV 只要求模型判定 + 本地运行对照，需要在报告明确；如果要 POC 触发，则还不能算完成。

2. **模型/时间不可逐条证明**  
   截图不显示模型版本或生成时间；metadata 已写平台映射说明。  
   只能按平台级说明，不能写逐条字段验证。

## 三（补）、哈希修正记录

- `ADV_SECOND_SQLI_VULN_R1`：`normalized_sha256` 修正为 `71cf3b3c26f805671cc041cbfa41bf244efdf05024ca782b40b3de5dd5f2d3f0`
- `ADV_SECOND_SQLI_FIXED_R1`：修正为 `4be6b6ee70edc0eb66de02402813c3bfec3c7cdb50bc74120cc4f70f1836f278`
- `ADV_IDOR_VULN_R1`：修正为 `de4670de92788b616434636e850b3165fd4ef687685b978bb6b0b9ddf3ca585b`
- `ADV_IDOR_FIXED_R1`：修正为 `def0230a7c68bc2c6881a7263e9a58f8a4911acd8dfa6f0450b931e91ee20681`

## 四、D 的复核结论

- **模型判定与定位：4/4 通过**；
- **raw/截图/会话/normalized 哈希：4/4 通过**（normalized 哈希已在本 PR 修正）；
- **本地 vulnerable/fixed 对照：A 的 runtime recheck 支持，D 未重复执行**；
- **POC：not_run**，不能写成已触发；若 ADV 不要求 POC，报告需明确；
- **D 对 ADV 四条的独立复核：通过**；A 已把 plan reviewer 改为 D、metadata 状态改为 reviewed。

## 五、仍建议 A 在报告中写明

1. ADV `poc_execution=not_run` 的限制；
2. 模型版本按 1017 平台映射，截图未显示逐条版本字段。

## 六、边界

D 修正了 4 条 ADV `metadata.json` 的 `normalized_sha256` 与模型映射字段；没有修改 raw/normalized、`runs/formal.json` 或 bonus plan。本记录只做独立复核，不代替 A 的最终状态修改。

D（linan / linan-prog，2986713478@qq.com）　2026-10-26 21:30（UTC+8）
