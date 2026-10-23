# A 加分实验与正式九条交接裁定

日期：2026-10-20（Asia/Shanghai）

## A 对 C 的裁定

C 可以按 `experiments/bonus_runs.plan.json` 继续执行名下 8 条正式 XSS Prompt Injection 记录：

- `INJ_XSS_IGNORE_BASE` / `INJ_XSS_IGNORE_DEF`
- `INJ_XSS_SAFE_BASE` / `INJ_XSS_SAFE_DEF`
- `INJ_XSS_LEAK_BASE` / `INJ_XSS_LEAK_DEF`
- `INJ_XSS_DIVERT_BASE` / `INJ_XSS_DIVERT_DEF`

这 8 条必须使用计划中对应的 S013、XSS_V0/XSS_V2、四类正式攻击文本和独立会话，保存完整输入、模型原文、规范化结果、metadata、模型设置截图及必要的语法/正常业务证据。完成后交 B 独立复核；执行阶段不得把状态提前改为 `reviewed`。

A 已完成的 16 条固定注释句式批次继续单独保留在 `runs/INJ_*_R1/`，报告为探索性对照，不替代官方四类攻击矩阵，也不进入官方 16 条计划的完成统计。

## B 的 9 条正式记录

当前 `runs/formal.json` 中 S008、S019、S024 的 9 条均为 `reviewed`，reviewer 为 A，模型回答和结构化证据已完成技术复核。

S019 的 `evidence/truth/S019/browser_reference.json` 是样本级浏览器参考观察，内容可证明受控 XSS marker 在浏览器 DOM 中出现；但该文件没有绑定到 `F_S019_V0_R1` 或 `F_S019_V2_R1` 的 run_id，且两条正式记录的 `verification` 仍为 `not_run`。在完成逐条 run 绑定、原始 POC、命令/日志和截图交叉核对前，不把它改写为正式记录的 `triggered`。

因此当前正式口径保持：S019 V0/V2 的 POC 执行证据待补强；S019 V0 截图缺失问题待解决；S008、S024 没有模型 POC，不补造 POC。

## CTX

S007 SQLi_V2 修正重跑和四条 CTX 的 A 技术复核已经完成。CTX 不进入 36 条主实验统计，也不反向修改已冻结 Prompt。

## 下一次收口条件

1. C 完成上述 8 条正式 XSS Prompt Injection 运行并交 B 复核。
2. B/C 补齐注入版语法与正常业务等价证据。
3. S019 V0/V2 的浏览器/POC 证据按具体 run_id 绑定；未绑定前保持 `verification=not_run`。
4. 重新运行 `audit_submission.py`、测试和最终报告生成工具。

