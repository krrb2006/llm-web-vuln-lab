# B S001 official injection source confirmation

日期：2026-10-25（Asia/Shanghai）

## 正式来源

三类注入文本均来自仓库中的 S001 官方输入包，注入内容只位于 F01:0003 的 PHP 文档注释，F01:0001-F01:0024 的可执行 PHP 语句未改变：

| attack | official packet | V0 run | V2 run |
|---|---|---|---|
| force_safe_verdict | `experiments/prompt_injection/official_packets/S001/force_safe_verdict/code_input.txt` | `INJ_SQLI_SAFE_BASE` | `INJ_SQLI_SAFE_DEF` |
| request_hidden_rules | `experiments/prompt_injection/official_packets/S001/request_hidden_rules/code_input.txt` | `INJ_SQLI_LEAK_BASE` | `INJ_SQLI_LEAK_DEF` |
| divert_output | `experiments/prompt_injection/official_packets/S001/divert_output/code_input.txt` | `INJ_SQLI_DIVERT_BASE` | `INJ_SQLI_DIVERT_DEF` |

`ignore_task` 同理，对应 `INJ_SQLI_IGNORE_BASE/DEF`。V0 使用 `prompts/SQLi_V0.txt`，V2 使用 `prompts/SQLi_V2.txt`。

## B 证据状态

- 8 条回答已按顺序从 `D:/网络安全/json.docx` 拆出，保存为各 run 的 `raw_output_user.txt`，并写入 raw SHA-256 和来源 metadata。
- `SAFE_BASE` 的缺失字段已保留为 `format_valid=false`，没有补写模型原文。
- 输入包和 Prompt 哈希已写入 metadata；POC 均声明未执行。
- 共享设置证据只确认“深度思考开启、智能搜索关闭”；按用户要求不记录模型名称，也不要求每条重复截图。
- 只有 `INJ_SQLI_IGNORE_BASE` 另有一次可追溯的浏览器重跑 raw；其余七条的 raw 来自用户提供的 DOCX 归档，不能表述为本轮逐条浏览器重跑。

## 交接结论

B 已完成来源确认和文档归档，可交 C 做静态独立复核。S001 八条仍保持 `planned`，不由 B 修改 `reviewed` 状态。
