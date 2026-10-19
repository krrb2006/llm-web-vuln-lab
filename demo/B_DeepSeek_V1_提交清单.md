# B 第一轮迭代：DeepSeek V1 开发集 12 条

V0 的 12 条原始回答已归档，V0 问题与修改依据见 `results/B_DEV_V0_baseline_2026-10-19.md`、SQLi/XSS 迭代日志。V1 只强化证据要求：SQLi 报告须引用实际 `query()/execute()` 行；存储型 XSS 须区分写入与随后独立读取/渲染。V1 的效果尚未实测，不要把这些预期写成已提升。

模型与设置继续固定为 DeepSeek 网页端 `DeepSeek-V4.1-Flash`、深度思考开启、联网搜索关闭。每条**新开独立会话**，仅提交对应 `input.txt` 全文，不附 V0 答案、manifest、line_map 或真实标签。完整原样保存首轮回答；若回答截断，保留该原文，重试另编号。请在提交时记录真实时间（含时区）与页面模型/开关，缺失如实说明。下表只是交接顺序，**不控制模型随机性**。

|顺序|run_id|完整输入|
|---|---|---|
|1|DEV_S001_V1_R1|`runs/DEV_S001_V1_R1/input.txt`|
|2|DEV_S002_V1_R1|`runs/DEV_S002_V1_R1/input.txt`|
|3|DEV_S003_V1_R1|`runs/DEV_S003_V1_R1/input.txt`|
|4|DEV_S004_V1_R1|`runs/DEV_S004_V1_R1/input.txt`|
|5|DEV_S005_V1_R1|`runs/DEV_S005_V1_R1/input.txt`|
|6|DEV_S006_V1_R1|`runs/DEV_S006_V1_R1/input.txt`|
|7|DEV_S013_V1_R1|`runs/DEV_S013_V1_R1/input.txt`|
|8|DEV_S014_V1_R1|`runs/DEV_S014_V1_R1/input.txt`|
|9|DEV_S015_V1_R1|`runs/DEV_S015_V1_R1/input.txt`|
|10|DEV_S016_V1_R1|`runs/DEV_S016_V1_R1/input.txt`|
|11|DEV_S017_V1_R1|`runs/DEV_S017_V1_R1/input.txt`|
|12|DEV_S018_V1_R1|`runs/DEV_S018_V1_R1/input.txt`|

每条 V1 的 `code_input` SHA-256 与对应 V0 完全相同，只有 Prompt 文本变化；完整输入 SHA-256 因 Prompt 改变而不同。SQLi V1 候选 Prompt SHA-256：`76727ec101cac6793e108061511ba7ec1029f27d654aa8b1c499f5dd18cb3c84`；XSS V1 候选：`44476daa06bfbebf6d83fc85649f1d1a9332b17ecec23eeb1241534f2860533c`。十二条原文归档与对照分析完成前，不开始 V2 或正式实验。
