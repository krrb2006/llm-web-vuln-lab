# B 开发集 DeepSeek 网页端提交清单

本批只提交 V0。用户指定的计划配置为 **DeepSeek-V4.1-Flash；深度思考=开；联网搜索=关**。每条必须在 DeepSeek 网页端新建独立会话，核对这三个设置；逐条记录页面显示的模型名称、可见设置、实际提交时间及其时区。界面不提供的参数如实写“界面不提供”，不得猜测。复制 `input.txt` **全文**作为一次用户消息，不附内部 line_map、真值或其他版本回答。首轮回答要完整原样保存；若回答中途截断，先保留该首轮原文，续写或重试另编号。

|顺序|run_id|复制全文的文件|建议原文文件名|
|---|---|---|---|
|1|DEV_S013_V0_R2|`runs/DEV_S013_V0_R2/input.txt`|`DEV_S013_V0_R2_raw_output.txt`|
|2|DEV_S014_V0_R1|`runs/DEV_S014_V0_R1/input.txt`|`DEV_S014_V0_R1_raw_output.txt`|
|3|DEV_S015_V0_R1|`runs/DEV_S015_V0_R1/input.txt`|`DEV_S015_V0_R1_raw_output.txt`|
|4|DEV_S016_V0_R1|`runs/DEV_S016_V0_R1/input.txt`|`DEV_S016_V0_R1_raw_output.txt`|

S013 使用 R2 是因为 R1 属于先前 ChatGPT GPT-6 的独立试跑，已明确排除在 DeepSeek 主对照之外；它不是为了挑选更好的回答。四条代码包仍与 C 的同一标准输入 SHA256 对齐。收到原文后由 B 运行 `tools/b_runs.py record`，保留原文并单独标记 JSON、行号及 POC 问题。POC 不经人工安全审阅不执行。

请回传每条原文文件、实际提交时间（例如 `2026-10-12T14:30+08:00`）、页面显示的模型标签、可见设置以及是否有追加消息。若时间或标签未记录，直接说明未知，B 会标记元数据缺失，不补造。

S001—S006、S017—S018 的 V0 草稿位于 `results/B_proposed_packets/`，仍待 C 核对，不在本批提交。V1/V2 不在 V0 全 12 条分析前提交。
