# B 开发输入包交接队列

## 已获 C 标准包，可人工提交 V0

S013—S016：DeepSeek 主实验使用 `DEV_S013_V0_R2`、`DEV_S014_V0_R1`、`DEV_S015_V0_R1`、`DEV_S016_V0_R1` 的 `input.txt`。来源最初为 `origin/c/samples@a04a832`；在 C 当前 `8da63f7` 中字节哈希仍一致。四条均已取得 DeepSeek V0 原文，但提交时间缺失，动态验证与真值审核未完成。操作见 `demo/B_DeepSeek_提交清单.md`。`DEV_S013_V0_R1` 是早先 ChatGPT GPT-6 试跑，已排除主对照。

## 待 C 核对的 B 草稿

|样本|源码来源|草稿位置|需 C 核对|
|---|---|---|---|
|S001—S006|A 的 `origin/a/criteria-and-sql01`|`results/B_proposed_packets/S001—S006/`|入口/调用链是否完整、运行上下文与标准包口径、原始行号|
|S017—S018|D 的 `origin/d/environment-reference`|`results/B_proposed_packets/S017—S018/`|写入与读取链、模板/浏览器上下文、数据库与路由前提|

每目录包含 `spec.json`、`code_input.txt`、内部 `line_map.internal.json`、`v0_input_DRAFT.txt`、来源与哈希。草稿均已通过源码逐行与 Git blob 哈希检查，以及明显答案字段扫描；这些是静态准备检查，不等于 C 的标准化审核、D 的 PHP 语法/真实运行验证或模型实验。C 若提供不同的标准包，使用 C 审核包重新生成正式 DEV 输入，并保留差异；不得把草稿与 C 的包混作同一固定输入对照。

待 C 确认的具体问题：A 的 S001—S006 公共连接文件只以 `$db` 接口约定写入上下文，是否需要纳入输入包；D 的 S017—S018 完整 `index.php` 是否足以覆盖存储写入和读取链；运行 URL、会话与教学数据库前提是否与 D 最终环境一致。以上问题不影响四份已获 C 标准包的 V0 人工提交。

2026-10-15 更新：S001—S006 的旧草稿对应 A 源 `d498903`，已由 `results/B_proposed_packets_v2/` 基于 A 当前 `26637fb` 重建；旧 D 参考运行针对旧源码，不能直接复用。v2 草稿仍待 C 标准化和 D 新版本重验。S017/S018 源码字节目前未变，但数据库异常口径可能改变其最终版本。详见 `results/B_freeze_readiness_2026-10-15.md`。

2026-10-19 更新：A 最新分支 `173b9af` 已合入并独立验收 S001—S006 的 C 正式包，B 已据此生成并锁定 `runs/DEV_S001_V0_R1` 至 `DEV_S006_V0_R1`；S005/S006 只用补足 LIKE 中性说明后的新哈希。S017/S018 虽在 A 分支有准备包，但 D 将修改数据库异常处理，B 暂不锁定或提交该两条。当前权威状态见 `results/B_dev_handoff_2026-10-19.md`。
