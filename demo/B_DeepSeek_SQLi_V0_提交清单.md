# B 下一批：DeepSeek SQLi 开发集 V0（S001—S006）

这六份输入已从 A 独立验收的 C 标准包重新生成，`input.txt` 与 A 分支所准备的完整 V0 输入逐字节 SHA-256 一致。S005/S006 使用 C 补充 LIKE 中性说明后的新包；旧草稿哈希作废。D 对 A 当前源码的运行重验仍待完成，因此这批可用于保留**模型 V0 原文**，但不得在重验与真值审核前判定 TP/FP/TN/FN；若最终源码或标准包再变，三版均须改用同一最终包重跑。

被测界面继续固定为 DeepSeek 网页端 `DeepSeek-V4.1-Flash`；深度思考开启、联网搜索关闭。每条新开独立会话，复制对应 `input.txt` **全文**作为唯一首轮用户消息；不要附 `line_map.json`、manifest、真值或其他样本答案。保存完整首轮回答，不修复模型格式。实际提交时记下时间与时区，以及页面显示的模型和开关；缺失时如实说明。

|顺序|run_id|复制的完整输入|
|---|---|---|
|1|DEV_S001_V0_R1|`runs/DEV_S001_V0_R1/input.txt`|
|2|DEV_S002_V0_R1|`runs/DEV_S002_V0_R1/input.txt`|
|3|DEV_S003_V0_R1|`runs/DEV_S003_V0_R1/input.txt`|
|4|DEV_S004_V0_R1|`runs/DEV_S004_V0_R1/input.txt`|
|5|DEV_S005_V0_R1|`runs/DEV_S005_V0_R1/input.txt`|
|6|DEV_S006_V0_R1|`runs/DEV_S006_V0_R1/input.txt`|

建议按 run_id 保存原文为 `<run_id>_raw_output.txt`，逐条回传给 B。B 用 `tools/b_runs.py record` 原样归档、校验 JSON 和原始行号，再根据 D/C/A 的源码与参考证据分类错误。V1/V2 不在 V0 全 12 条归档和分析前提交；正式测试仍暂停。
