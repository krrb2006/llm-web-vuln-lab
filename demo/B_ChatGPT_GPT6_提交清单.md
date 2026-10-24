# B 开发集 ChatGPT 网页版 GPT-6 提交清单

**已停止使用：主实验界面改为 DeepSeek 网页端。请使用 `demo/B_DeepSeek_提交清单.md`。本文件仅保留历史交接记录。**

## 本批可直接提交：S013—S016 的 V0

|顺序|复制全文的文件|回答原文建议文件名|
|---|---|---|
|1|`runs/DEV_S013_V0_R1/input.txt`|`DEV_S013_V0_R1_raw_output.txt`|
|2|`runs/DEV_S014_V0_R1/input.txt`|`DEV_S014_V0_R1_raw_output.txt`|
|3|`runs/DEV_S015_V0_R1/input.txt`|`DEV_S015_V0_R1_raw_output.txt`|
|4|`runs/DEV_S016_V0_R1/input.txt`|`DEV_S016_V0_R1_raw_output.txt`|

每条在 ChatGPT 网页版**新建独立会话**，确认界面显示 GPT-6，复制对应 `input.txt` 全文作为一次用户消息提交。不附内部 `line_map.json`、manifest、参考答案或其他版本输出。不追加纠正消息替换首轮回答。完整复制模型首轮回答（包括 JSON、代码块和其他文本）到各自原文文件，不自行修复格式。记录每条实际提交时间及其时区、界面所显示的模型名称、可见设置；界面不提供的参数写“界面不提供”，不猜测值。若模型显示名称或版本变化，标记批次并暂停跨版本比较。

把四份原文文件和上述时间/模型/设置记录交回 B 后，逐条运行：

```powershell
python tools/b_runs.py record --run-id DEV_S013_V0_R1 --raw-output <S013原文文件> --model "GPT-6" --settings "界面不提供" --submitted-at 2026-10-12T14:30:00+08:00
```

示例时间必须替换为**该条实际提交时间**，模型与设置也以界面实际显示为准。工具保留原文，另存 JSON 格式与行号校验结果。后续 S014—S016 仅替换 run_id、原文路径与该条时间。

## 暂不提交的八份草稿

`results/B_proposed_packets/S001—S006、S017—S018` 下有基于 A/D 源码生成的 `v0_input_DRAFT.txt`，仅供 C 核对标准化输入。其来源、行号与哈希可检查，但**尚未经 C 确认**，且 D 的 PHP 语法及真实运行验证尚待完成。C 确认或提供正式 `code_input.txt` 后，B 再用 `tools/b_runs.py prepare` 生成正式 DEV 输入；如 C 的包与草稿不同，以 C 审核包为准。

本批只产生 V0 原文。收齐 12 个开发样本的 V0 输出并归因后才决定 V1 的实验性修订，再按相同固定代码包复测；V2 同理。不要将 ChatGPT 网页版以外的模型或 Codex 回答混入主对照。
