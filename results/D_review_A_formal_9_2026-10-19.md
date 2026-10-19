# D 独立复核：A 的正式九条（2026-10-19）

复核人：D（linan）　复核对象：A 的 S007、S020、S021 各 V0/V1/V2
复核基线：`a/criteria-and-sql01@0c994ed`（提交信息 `record complete formal experiment results`）
说明：本记录是 D 作为 A 的 primary reviewer 的独立复核，不改真值、不改别人的记录。

## 一、通过项

- 9/9 的 `input.txt`、`raw_output.txt`、`normalized.json`、`metadata.json` 存在且可追溯。
- 9/9 `format_valid=true`；`sample_id`、`prompt_version` 与 run_id 一致。
- 9/9 的 prediction 与 `dataset/manifest.json` 真值一致：
  - S007 三条 `vulnerable`（真值 true）；
  - S020 三条 `safe`（真值 false）；
  - S021 三条 `vulnerable`（真值 true）。
- 9/9 的 locations 均落在对应 packet 的 `line_map` 合法行范围内；S007 覆盖 F01/F02，S021 覆盖三页路径。
- 模型显示名为 `DeepSeek-V4.1-Flash`，`model_settings` 为“深度思考=开；联网搜索=关”。
- S007/S021 的 raw 中各含 1 个 Python POC 代码块，目标均为 `127.0.0.1:4280`，未见外部主机。

## 二、未通过 / 待补项

### 1. 九条都没有设置/回答截图

`runs/F_S007_*`、`F_S020_*`、`F_S021_*` 的目录里只有 `input.txt`、`raw_output.txt`、`normalized.json`、`metadata.json`，没有 `screenshot_settings.png`/`screenshot_answer_*.png`。`evidence_paths` 也只有 raw 和 normalized 两条。

手册要求保存模型名/设置截图与回答截图；这 9 条目前无法从截图核实模型设置和界面状态。

### 2. S007/S021 六条 POC 原文没有归档

- `F_S007_V0/V1/V2`、`F_S021_V0/V1/V2` 的 `poc_generated=true`，但 `pocs/F_S007_*`、`pocs/F_S021_*` 均不存在。
- raw 中已有完整 Python 代码块，说明不是“没有 POC”，而是没有提取到 `pocs/<run_id>/original.py`。
- `evidence_paths` 未包含 POC 原文；`verification=not_run`，也没有执行日志或“未执行原因”的证据文件。

这使“POC 可执行性/触发”这一维度无法复核。

### 3. metadata 与 formal.json 状态不一致

- `metadata.json` 的 `status` 仍是 `raw_recorded`；
- `runs/formal.json` 已是 `reviewed`；
- `metadata.json` 没有 `model_snapshot`（页面提示 `V4.1-Flash-1017`），也没有 `executed_by`。

### 4. 状态先于复核

`runs/formal.json` 已把这 9 条置为 `reviewed`，但 D 的独立复核此前未发生。`tools/check_freeze.py` 只接受 `planned/reviewed`，不支持 `executed_pending_review`，因此不要求把已完成的 36 条降级；但报告/附录必须如实说明“reviewed 时 D 的独立复核尚未完成，证据待补”。

## 三、复核结论

- **判定与定位：通过。** 9/9 prediction 与真值一致，行号引用合法，S007/S021 的漏洞判断与代码路径一致。
- **证据完整性：未通过。** 缺 9 条截图；S007/S021 六条缺 POC 原文与执行/未执行证据；metadata 未记录模型快照。
- 因此本次结论为 **有条件通过**：A 补齐上述 1–3 后，D 再签“完整复核”；在补齐前，这 9 条不能作为“POC 已验证”的材料引用。

## 四、A 需要补的最小集

1. 从 raw 提取并保存：
   - `pocs/F_S007_V0_R1/original.py`、`V1`、`V2`；
   - `pocs/F_S021_V0_R1/original.py`、`V1`、`V2`；
   - 把 POC 路径加入对应 `evidence_paths`。
2. 补 9 条的 `screenshot_settings.png` 与 `screenshot_answer_1/2.png`；无法补的，写明原因并在 `error_reason` 记录。
3. 在 9 条 `metadata.json` 补 `model_snapshot: "V4.1-Flash-1017"`，并把 `status` 与 formal.json 对齐；如需保留 `raw_recorded`，在复核记录里说明。
4. S007/S021 的 POC 若要计入“可执行/触发”，按 `templates/verification.md` 执行并保存 stdout/exit code；不执行则明确写“未执行及原因”，不要只留 `not_run`。

## 五、签字

D（linan / linan-prog，2986713478@qq.com）　2026-10-19 22:50（UTC+8）

结论：判定/定位通过；证据完整性待补。补齐后由 D 追加最终签字。
