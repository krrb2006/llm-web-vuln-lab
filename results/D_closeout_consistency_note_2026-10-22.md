# D 收口一致性核对（2026-10-24 更新）

核对人：D　基线：`a/criteria-and-sql01@19dbf10`

## 一、计数

- 正式实验：`runs/formal.json` 36/36 `reviewed`；
- 加分实验：14/26 `reviewed`（S013 8 + Burp 2 + CTX 4）；
- 剩余 12 条：8 条 `INJ_SQLI_*` + 4 条 `ADV_*`，均 `planned`。

## 二、此前指出的表述问题已修正

D 在 2026-10-22 指出：`results/A_final_closeout_2026-10-21.md` 把“剩余 8 条”写成 S001/S004 固定格式探索，但 plan 里实际是 S001 官方 `INJ_SQLI_*` 8 条。

A 已在 `19dbf10` 修正 closeout：

- 剩余 8 条明确为 S001 官方 SQLi 注入；
- S001/S004 的 8 条 Original/Injected 固定格式探索单独列出，不计入 26 条计划；
- 14/26 的计数不变。

该问题已闭环，无需再改。

## 三、S001 的当前口径

A 的 `results/A_S001_final_decision_2026-10-24.md` 决定：S001 官方 8 条保持 `planned`，不转 `reviewed`，也不计入 14/26。原因是 C 的审计确认存在 `SAFE_BASE` 原文字段缺失、metadata 缺 `raw_output_sha256`、输入哈希与重建不绑定、会话模型/设置截图缺失等；POC 未执行。D 同意该口径，不把 S001 写成已完成加分。

## 四、D 的收口状态

- D 的 #20 已合并：6 张第二台电脑截图已是真正 PNG，`results/D_second_pc_visual_review_2026-10-21.md` 已在主分支；
- #19 操作指南已关闭，内容留在 PR 历史；
- D 的 9 条、A 的 9 条、C 对 D 的签字均未被改动；
- 第二台电脑仍无 60–90 秒录屏，A 的 closeout 已如实记录；
- ADV 4 条按 A/D 决定保持 `planned`，本轮不重新开启。

## 五、结论

主实验 36/36 和加分 14/26 可以提交；S001 官方 8 条保持 `planned` 是如实口径，不需要重跑或补写。D 不再有必须执行的正式任务。

D（linan / linan-prog，2986713478@qq.com）　2026-10-24 19:40（UTC+8）
