# D 最终复核签字：A 的 9 条（含证据限制）与第二台电脑决定

复核人：D（linan）　日期：2026-10-20（UTC+8）
基线：`a/criteria-and-sql01@34b36ad`（A 已合并 D 的 #10/#11/#12/#13/#15/#16）

## 一、A 的 9 条：最终复核通过（带已记录的证据限制）

对象：`F_S007_V0/V1/V2`、`F_S020_V0/V1/V2`、`F_S021_V0/V1/V2`，operator=A，reviewer=D。

### 通过项

1. **判定与定位**：9/9 prediction 与 `dataset/manifest.json` 真值一致（S007 vulnerable、S020 safe、S021 vulnerable）；9/9 JSON 有效，locations 落在 `line_map` 合法行范围。
2. **POC 原文已归档**：A 已补 `pocs/F_S007_{V0,V1,V2}_R1/original.py`、`pocs/F_S021_{V0,V1,V2}_R1/original.py`，`runs/formal.json` 的 evidence_paths 已指向对应 POC。
3. **POC 目标与安全边界**：S007 POC 仅访问 `127.0.0.1:4280/lab_cases/S007/index.php`；S021 POC 仅访问 `127.0.0.1:4280`，未读 Cookie、未外发、未写文件。D 已在冻结源码上执行 S007 三条（V0/V1/V2），均 exit 0 并观察到条件/行集变化；S021 三条仅做静态安全审阅，未执行。
4. **哈希与格式**：input/raw/prompt/packet 哈希与 metadata/冻结计划一致；9/9 `format_valid=true`。

### 已记录的限制（不伪造为已完成）

1. **无 run-specific 截图**：A 的 9 条运行目录只有 input/raw/normalized/metadata，没有 settings/answer 截图；A 在 `results/A_formal_9_poc_completion_2026-10-20.md` 中明确说明未补。D 接受该限制为“已在报告中披露的证据缺口”，但它意味着无法从截图独立核对界面设置。
2. **S021 POC 未执行**：S021 三条 POC 未做浏览器 marker 观察，`verification` 保持 `not_run`；不得把 S021 的 POC 统计成“已触发”。
3. **metadata 状态未对齐**：A 的 9 条 metadata 仍为 `status=raw_recorded`，且缺 `model_snapshot`/`executed_by`；`runs/formal.json` 已是 `reviewed`。D 不要求降级（`check_freeze.py` 只接受 planned/reviewed），但报告附录应注明 metadata 与 formal 状态的口径差异。
4. **截图缺口不影响 prediction/location/POC 原文的复核**，但影响“界面设置可独立核验”的证据强度；报告中必须披露，不能写成“全部证据完整”。

### 结论

**A 的 9 条最终复核通过，附上述已记录限制。** 9/9 判定与真值一致，POC 原文、目标与安全边界可追溯；截图与 S021 执行证据缺失按限制披露，不冒充触发证据。

D（linan / linan-prog，2986713478@qq.com）　2026-10-20 21:45（UTC+8）

## 二、第二台电脑复现：本轮决定不做

- D 单人只有当前一台机器，无法满足“另一名成员电脑”的复现要求；
- `environment/reproduce_second_pc.md`（PR #13 已合入）已给出固定提交、镜像、build/compose/check 和两代表样本的完整步骤，可在后续由另一名成员执行；
- 本轮不伪造“第二台电脑已复现”的结论，报告中按“未完成/环境限制”记录；
- 若后续有人提供第二台电脑，按该文档执行即可，预计 30–45 分钟。

D（linan / linan-prog，2986713478@qq.com）　2026-10-20 21:45（UTC+8）

## 三、对最终报告的建议

- 主实验 36 条按“全部 reviewed”统计，但附录注明：A 的 9 条无 run-specific 截图、S021 POC 未执行、metadata 状态与 formal 不一致；
- D 的 9 条有 27 张截图与 C 的复核签字；
- 第二台电脑复现列为未完成的环境限制，不写成已验证；
- 加分实验当前 6/26（CTX 4 + Burp 2），其余按 planned/未完成处理。
