# D 仓库最终整理记录（2026-10-26）

整理人：D　基线：`a/criteria-and-sql01@9e36c49`

## 一、这次直接修正的内容

1. **ADV 4 条 metadata**
   - `normalized_sha256` 按当前 `normalized.json` 精确字节重算：
     - `ADV_SECOND_SQLI_VULN_R1`：`71cf3b3c26f805671cc041cbfa41bf244efdf05024ca782b40b3de5dd5f2d3f0`
     - `ADV_SECOND_SQLI_FIXED_R1`：`4be6b6ee70edc0eb66de02402813c3bfec3c7cdb50bc74120cc4f70f1836f278`
     - `ADV_IDOR_VULN_R1`：`de4670de92788b616434636e850b3165fd4ef687685b978bb6b0b9ddf3ca585b`
     - `ADV_IDOR_FIXED_R1`：`def0230a7c68bc2c6881a7263e9a58f8a4911acd8dfa6f0450b931e91ee20681`
   - 模型字段统一为 `DeepSeek-V4.1-Flash-1017`，并注明平台公告依据、逐条 UI 标签不可见。

2. **S001 8 条 metadata**
   - 模型统一为 `DeepSeek-V4.1-Flash-1017`；
   - `exploratory_only=false`；
   - 保留 `per_run_model_field_captured=false` 的技术备注。

3. **A 的 ADV 哈希说明**
   - `A_ADV_review_reconciliation_2026-10-26.md` 中四个旧哈希替换为实际 blob SHA-256；
   - 增加 D 复核补正说明。

4. **D 文档**
   - 更新 `D_S001_default_8_2026-10-26.md` 为 1017 口径、A 已接受、C 复核待完成；
   - 更新 `D_review_ADV_2026-10-26.md`：ADV 4/4 通过，reviewer/status 已对齐，POC `not_run` 作为限制。

## 二、没有改的内容

- `runs/formal.json` 未改；
- ADV/S001 的 raw、normalized、截图、POC 未改；
- bonus plan 的状态/reviewer 未改（ADV 已是 D，S001 仍是 `A_self_review`）；
- 没有伪造 C 的复核签字。

## 三、剩余唯一流程缺口

**S001 8 条仍缺 C 的独立复核。**

- plan 里 S001 reviewer 仍是 `A_self_review`；
- D 是这 8 条的 operator，不能自审；
- C 需要实际核对 8 个 session、input/raw 哈希、JSON、POC stdout/exit、截图和设置；
- C 签字后，A 才能把 reviewer 改为 C。

## 四、当前状态

- 36/36 正式记录：reviewed；
- 26/26 加分状态：reviewed；
- ADV 4 条：D 复核通过，reviewer=D，POC `not_run` 已记录；
- S001 8 条：数据/POC/证据完成，C 复核待完成；
- 模型：`DeepSeek-V4.1-Flash-1017`（官方 2026-10-17 网页端同步公告；逐条 API 字段未捕获）。

D（linan / linan-prog，2986713478@qq.com）　2026-10-26 22:15（UTC+8）
