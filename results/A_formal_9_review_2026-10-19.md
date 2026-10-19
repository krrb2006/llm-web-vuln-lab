# A 对 B 正式九条记录的审核（2026-10-19）

审核对象：`S008`、`S019`、`S024` 各 V0/V1/V2，共 9 条。

## 结论

- 原文、规范化 JSON 和元数据可互相追溯，9/9 通过。
- 输入包、Prompt、原文 SHA-256 核对通过，9/9 通过。
- JSON 格式和 POC 格式校验通过，9/9 通过。
- prediction 与当前 A 真值基线一致，9/9 通过：S008 safe、S019 vulnerable、S024 safe。
- 所有模型位置引用均落在对应 `line_map.json` 的合法范围内。
- S019 三条 vulnerable 记录的 `location_correct` 记为 `true`；S008、S024 为 safe，位置字段保持 `null`。
- 9 条状态更新为 `reviewed`，审核人为 A；证据路径指向各自的 `raw_output.txt` 和 `normalized.json`。

## POC 与验证边界

- S008、S024 的模型输出未生成 POC。
- S019 的三条模型输出生成了 Python POC 方案；静态检查确认目标仅为 `127.0.0.1:4280`，没有执行脚本。
- 所有 9 条 `verification` 继续保持 `not_run`。
- `raw_execution_ok`、`environment_execution_ok` 保持 `false`；本记录不把 HTTP 回显或静态 POC 方案写成触发证据。

## 修正记录

B 的 `c01e1c8` 曾将这 9 条 `model_display_name` 清空。A 已按前置冻结计划恢复为 `DeepSeek-V4.1-Flash`；Prompt、输入包和原文哈希未改动。

正式统计仍需遵守 `verification=not_run` 的边界。若团队决定执行 S019 的 POC，必须另存执行证据并经安全复核后再更新 verification；本次审核没有执行任何 POC。
