# 上下文消融加分实验记录

日期：2026-10-19（Asia/Shanghai）

## 实验设置

- 固定 Prompt：XSS_V2。
- 固定模型：DeepSeek-V4.1-Flash。
- 固定设置：深度思考开启、智能搜索关闭。
- 变量：同一样本的 entry-only 与 full-context。
- 范围：S007、S020，共 4 条；不并入主实验 36 条统计。
- POC：本轮只保存模型生成结果，未执行任何 POC。

## 原始结果

|run_id|样本|条件|模型预测|格式|观察|
|---|---|---|---|---|---|
|CTX_S007_ENTRY|S007|entry-only|safe|通过|仅入口片段时识别为 XSS safe，依赖缺失的 repository 代码被列为 missing_context|
|CTX_S007_FULL|S007|full-context|vulnerable|失败：`vulnerability_type` 输出为 SQL注入|补充 repository 后转向 SQLi，未按冻结 XSS 输出契约作答|
|CTX_S020_ENTRY|S020|entry-only|uncertain|通过|缺少 preview 模板，无法确认最终浏览器输出上下文|
|CTX_S020_FULL|S020|full-context|safe|通过|识别两个输出点均有 `htmlspecialchars` 转义|

## 初步解释

本组 2 个样本显示，额外上下文并非单向改善：S020 从 uncertain 变为 safe，说明完整模板有助于判断输出防护；S007 的 full-context 虽然暴露了跨文件 SQLi，但偏离了本实验固定的 XSS 类型，且输出契约校验失败。该结果只用于说明上下文对审计路径和格式稳定性的影响，不用于修改 V2，也不改变主实验统计。

## 审核边界

当前四条在 `experiments/bonus_runs.plan.json` 中标记为 `executed`，等待独立复核后才可改为 `reviewed`。原始输入、metadata、规范化结果和模型原文位于各自 `experiments/context_ablation/runs/` 目录。
