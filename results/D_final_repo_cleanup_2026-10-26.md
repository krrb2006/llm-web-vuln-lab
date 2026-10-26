# D 仓库最终整理记录（2026-10-26）

> C 收口修订说明（2026-10-26）：D 的修正事项与署名保持不变；C 仅根据团队最终决定更新后续流程状态和模型版本证据口径。

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
   - 平台公告推定版本统一为 `DeepSeek-V4.1-Flash-1017`；
   - `exploratory_only=false`；
   - 保留 `model_display_name=null`、`model_version_proven=false`、`per_run_model_field_captured=false`，不把公告推定写成逐会话直接证明。

3. **A 的 ADV 哈希说明**
   - `A_ADV_review_reconciliation_2026-10-26.md` 中四个旧哈希替换为实际 blob SHA-256；
   - 增加 D 复核补正说明。

4. **D 文档**
   - 更新 `D_S001_default_8_2026-10-26.md` 为 1017 平台公告推定口径，并如实记录 A 项目内自审；
   - 更新 `D_review_ADV_2026-10-26.md`：ADV 4/4 通过，reviewer/status 已对齐，POC `not_run` 作为限制。

## 二、没有改的内容

- `runs/formal.json` 未改；
- ADV/S001 的 raw、normalized、截图、POC 未改；
- bonus plan 的状态/reviewer 未改（ADV 已是 D，S001 仍是 `A_self_review`）；
- 没有伪造 C 的复核签字。

## 三、最终流程口径

**S001 8 条无需等待 C 签字才能提交。**

- plan 里 S001 reviewer 仍是 `A_self_review`；
- D 是这 8 条的 operator，A 已完成项目内自审；
- 最终报告必须明确写成“A 对 D 运行证据完成项目内自审”，不得写成 C 独立复核通过；
- C 或外部复核可增强可信度，但不是当前提交阻塞项。

## 四、当前状态

- 36/36 正式记录：reviewed；
- 26/26 加分状态：reviewed；
- ADV 4 条：D 复核通过，reviewer=D，POC `not_run` 已记录；
- S001 8 条：数据/POC/证据完成，由 A 对 D 运行证据完成项目内自审；
- 模型：按官方 2026-10-17 网页端同步公告推定为 `DeepSeek-V4.1-Flash-1017`；逐条 API 字段未捕获，不表述为逐会话直接证明。

D（linan / linan-prog，2986713478@qq.com）　2026-10-26 22:15（UTC+8）
