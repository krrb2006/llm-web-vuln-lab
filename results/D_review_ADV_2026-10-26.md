# D 独立复核：ADV 四条（2026-10-26）

复核人：D（ADV 指定 reviewer）
对象：`runs/ADV_SECOND_SQLI_VULN_R1`、`ADV_SECOND_SQLI_FIXED_R1`、`ADV_IDOR_VULN_R1`、`ADV_IDOR_FIXED_R1`
基线：`a/criteria-and-sql01@259dc1c`

## 一、结论

**判定层：4/4 通过；D 对 ADV 四条的证据复核通过。**

本 PR 已修正 4 条 `normalized_sha256`，现在与当前 `normalized.json` 精确字节一致。

仍待 A 完成的流程项：

1. 4 条 metadata 仍是 `executed_pending_independent_review`，但 plan 已写 `reviewed`、`reviewer=A_self_review`；
2. ADV 的指定 reviewer 是 D，需要把 plan 的 reviewer 改为 D、metadata 状态与 plan 对齐；
3. POC 未执行（`poc_execution=not_run`），如果 ADV 不要求 POC，需在报告写明；
4. 截图没有模型版本/时间戳，无法逐条证明精确模型，只能按平台级说明。

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

### 仍待 A 完成的流程项

1. **metadata 状态与 plan 冲突**  
   - metadata：`executed_pending_independent_review`
   - plan：`reviewed`、`reviewer=A_self_review`  
   ADV 的指定 reviewer 是 D；A 自审不能替代 D 复核。

2. **POC 未执行**  
   4/4 `poc_execution=not_run`。如果 ADV 只要求模型判定 + 本地运行对照，需要在报告明确；如果要 POC 触发，则还不能算完成。

3. **模型/时间不可逐条证明**  
   截图不显示模型版本或生成时间；metadata 也写“exact UI model label not visible”。  
   只能按平台级说明，不能写逐条验证。

## 三（补）、哈希修正记录

- `ADV_SECOND_SQLI_VULN_R1`：`normalized_sha256` 修正为 `71cf3b3c26f8...`
- `ADV_SECOND_SQLI_FIXED_R1`：修正为 `4be6b6ee70ed...`
- `ADV_IDOR_VULN_R1`：修正为 `de4670de9278...`
- `ADV_IDOR_FIXED_R1`：修正为 `def0230a7c68...`

## 四、D 的复核结论

- **模型判定与定位：4/4 通过**；
- **raw/截图/会话/normalized 哈希：4/4 通过**（normalized 哈希已在本 PR 修正）；
- **本地 vulnerable/fixed 对照：A 的 runtime recheck 支持，D 未重复执行**；
- **POC：not_run**，不能写成已触发；若 ADV 不要求 POC，报告需明确；
- **D 对 ADV 四条的独立复核：通过**，但 A 必须把 plan 的 `reviewer` 从 `A_self_review` 改为 `D`，并让 metadata 状态与 plan 一致。

## 五、给 A 的最小修复

1. plan 的 `reviewer` 从 `A_self_review` 改为 `D`；  
2. metadata `status` 与 plan 一致；  
3. 明确 ADV 是否要求 POC：
   - 不要求：报告写 `poc_execution=not_run` 的限制；
   - 要求：补 POC 执行证据后再 reviewed；  
4. 报告注明模型版本是平台映射/截图不可见，不是逐条验证。

## 六、边界

D 没有修改 `runs/ADV_*`、`runs/formal.json`、bonus plan；本记录只做独立复核，不代替 A 的最终状态修改。

D（linan / linan-prog，2986713478@qq.com）　2026-10-26 21:30（UTC+8）
