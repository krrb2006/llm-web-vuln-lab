# S013 四类 XSS Prompt Injection 输入准备

日期：2026-10-20（Asia/Shanghai）

状态：`candidate_inputs_prepared_not_run`

本文件记录 C 执行前的本地输入准备。四条攻击文本按
`bonus_runs.plan.json` 的类别名形成最小语义候选；它们仍需 B 独立复核文本语义，
复核前不得把下列候选宣称为已完成运行或改写计划状态。

| attack | baseline | defended | 输入包 |
|---|---|---|---|
| `ignore_task` | `INJ_XSS_IGNORE_BASE` / XSS_V0 | `INJ_XSS_IGNORE_DEF` / XSS_V2 | `official_packets/S013/ignore_task/` |
| `force_safe_verdict` | `INJ_XSS_SAFE_BASE` / XSS_V0 | `INJ_XSS_SAFE_DEF` / XSS_V2 | `official_packets/S013/force_safe_verdict/` |
| `request_hidden_rules` | `INJ_XSS_LEAK_BASE` / XSS_V0 | `INJ_XSS_LEAK_DEF` / XSS_V2 | `official_packets/S013/request_hidden_rules/` |
| `divert_output` | `INJ_XSS_DIVERT_BASE` / XSS_V0 | `INJ_XSS_DIVERT_DEF` / XSS_V2 | `official_packets/S013/divert_output/` |

所有候选只追加到 S013 F01:0002 的 PHP 注释，不改可执行代码；每条都有 diff 和 SHA-256。
没有调用模型、没有生成 raw output，也没有执行 POC。

生成工具：`tools/prepare_official_xss_injection.py`

