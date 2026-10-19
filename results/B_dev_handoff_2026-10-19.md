# B 开发集与扩展实验交接（2026-10-19）

## 当前锁定与原文

|范围|输入包状态|DeepSeek V0 原文|
|---|---|---:|
|S001—S006|A 已合入并验收 C 标准包；B 按同一字节准备、锁定六份 V0 输入|0/6|
|S013—S016|C/A 标准包哈希不变；B 已锁定|4/4|
|S017—S018|A 分支有旧版准备输入；D 的 try/catch 源码与新证据仍待提交，B **未锁定/未提交**|0/2|
|总开发集|固定模型：`DeepSeek-V4.1-Flash`，深度思考开、联网搜索关|**4/12**|

六份新 SQLi 包哈希已与 `origin/a/criteria-and-sql01@173b9af` 的 `dataset/packets`、`line_map.json`、`runs/DEV_*/input.txt` 交叉核验：

|样本|已锁定 code_input SHA-256|
|---|---|
|S001|`3a84669c84cee3841bf080bb546069a0367b152476cb163a47e533c6661437e1`|
|S002|`2a55ab105d2153549d248b39b40f22f7fdbbb3471133192ac46060a2ee1546a7`|
|S003|`965cfab7cf9654ff767f04f15a060994728d07226cf99346e1b64147d70a98ac`|
|S004|`9c6ca039383b371e799c7eaa34a2183d852c62bda00947e932c2392ef8032235`|
|S005|`b229827144f951e72a1f1851709487753473a0c92b34a85787db39a81bf48b5e`|
|S006|`86bbb4103876ae0b56ea28588ba7135eff8076028c87bf079b0455b6bab60bdb`|

旧 `results/B_proposed_packets_v2/S005`、`S006` 的 SHA 只代表当时草稿，**不再用于运行**。`runs/b_packet_lock.json` 现含 S001—S006、S013—S016 的 DEV Original 哈希。六份新输入的原文由用户在同一 DeepSeek 设置下提交，说明见 `demo/B_DeepSeek_SQLi_V0_提交清单.md`。D 对 A 当前源码的运行重验与独立真值复核仍是后续错误归因的必要证据，不把模型静态回答或旧版 D 证据当真值。

## CTX 口径

A 已裁定 CTX 是**主实验 36 条原始输出全部归档后**的独立附加实验：仅 S007 与 S020，各做 entry-only/full-context，共四条；不进入 36 条指标，不反馈修改已冻结 V2。C 生成 entry-only 变体，full-context 沿用正式包；B 在冻结 Prompt 和同一模型配置下按独立 `CTX_*` 编号保存四条原文。当前不生成 CTX 模型观察，也不读取测试集真值调整 Prompt。

## 冻结与正式测试

Prompt V0=4/12 已归档、V1=0/12、V2=0/12；六份仍是候选文本。S017/S018 最终包、D 重验、开发集两轮真实对照和用户确认尚未齐备，不能创建 `environment/prompt_hashes.txt`、宣称最终六哈希或启动正式 36 条。A 的 `check_freeze.py` 只有在其结果 READY 且四人签署后才能放行。B 的正式九条和 C 的九条复核仍待此关口。
