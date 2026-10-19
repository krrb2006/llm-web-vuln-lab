# A 冻结前复核与签字记录（2026-10-19）

复核人：A（经项目负责人本人授权提交）
复核时间：2026-10-19 17:06:45（UTC+8）
复核范围：六份候选 Prompt、24 个正式输入包、24 条真值、36 条正式计划、B 的 9 条正式记录及冻结检查结果。

## 复核结论

- 六份 Prompt 文件与 `environment/prompt_hashes.txt` 的 UTF-8/LF SHA-256 全部一致：SQLi V0/V1/V2、XSS V0/V1/V2 各 1 份。
- 24 个正式输入包、24 个源码/行号映射、24 条真值记录和 36 条正式计划均通过自动一致性检查；归档的 S009–S012 v1 未进入正式包索引。
- 当前模型条件为 `DeepSeek-V4.1-Flash`、深度思考开启、联网搜索关闭。
- B 的 9 条记录（S008、S019、S024 各 V0/V1/V2）已完成 A 审核；prediction 与真值一致，证据路径可追溯，模型位置引用在合法行号范围内。
- S019 的模型输出虽包含静态 POC 方案，但目标仅为本地地址且未执行；S008/S024 未生成 POC。9 条记录的 `verification` 均保持 `not_run`，未伪造触发证据。
- `python tools/check_freeze.py --report-only`：`READY`，自动阻塞项为 0。
- `python tools/freeze_plan.py --model-display-name "DeepSeek-V4.1-Flash" --model-settings "深度思考=开；联网搜索=关"`：`DRY RUN READY: 36 records`。
- 自动化测试：21/21 通过。

## A 签字声明

A 确认上述冻结前技术复核结果，并同意在 D 完成真实环境、参考验证和安全条件复核且四人签字完成后，由 A 执行：

```text
python tools/freeze_plan.py --write
python tools/check_freeze.py
```

在此之前不生成新的 `F_` 正式结果，不执行 POC，不改变 Prompt、输入包和模型条件。

签字：A
日期时间：2026-10-19 17:06:45（UTC+8）
