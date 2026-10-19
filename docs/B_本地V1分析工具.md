# B 本地 V1 原文分析工具

用途：原始回答在本地保存后，检查 JSON 契约、原始行号、V0/V1 输入哈希与同包条件，生成对照分析表。仅用 Python 标准库；建议 Python 3.10 或更新版本。没有联网、模型调用或 POC 执行，也不自动修改 `runs/`、原始回答或实验完成状态。

独立交付包已包含工具所需的 V0 基线、V1 准备记录和空收件箱；解压后直接把回答保存到 `local/b_v1_inbox/对应run_id/raw_output.txt`，再双击分析脚本。工具包不包含任何真实 V1 原文。V0 原文只供本地对照，不要随 V1 输入一起交给被测模型。

## 最短操作

在仓库根目录执行一次：

```powershell
python tools/b_local_analysis.py init
```

收件箱位于 `local/b_v1_inbox/`。每个 V1 run_id 有一个文件夹和待填写的 `session.json`。把对应**完整首轮回答**保存为 UTF-8 的 `raw_output.txt`，例如：

```text
local/b_v1_inbox/DEV_S001_V1_R1/raw_output.txt
local/b_v1_inbox/DEV_S001_V1_R1/session.json
```

不要修改模型 JSON、删除解释、修补代码或补写被截断部分。`session.json` 上半部分填实际界面名称、设置、提交时间、新会话与追加消息数，未知留 `null`。下半部分的 `planned_*` 是计划值，不是实际观察。示例时间：`2026-10-19T15:30+08:00`；实际模型设置按固定批次填写 `深度思考=开；联网搜索=关`。分析程序只读取这些自报字段，不会从模型自述推断 UI 或时间。

保存一条或多条回答后执行：

```powershell
python tools/b_local_analysis.py analyze
```

也可以双击仓库根目录 `B_本地V1_初始化.cmd` 和 `B_本地V1_分析.cmd`。需要本机可运行 Python；初始化收件箱已存在时程序会拒绝覆盖，直接继续保存回答和执行分析即可。

每次分析创建独立的 `local/b_v1_reports/时间编号/`，打印报告路径。可以只分析部分样本，或指定其他收件箱/全新输出目录：

```powershell
python tools/b_local_analysis.py analyze --samples S001 S002
python tools/b_local_analysis.py analyze --inbox D:/my-v1-answers --out D:/my-v1-report-01
```

也支持平铺原文名 `DEV_S001_V1_R1_raw_output.txt` 或 `DEV_S001_V1_R1.txt`；其会话文件分别为同名 `.session.json`（将 `.txt` 替换为 `.session.json`）。同一样本同时存在多个支持的原文路径时，程序报冲突，不挑选或覆盖。未识别的 `.txt` 文件名列在报告摘要中。

## 报告内容

|文件|用途|
|---|---|
|`analysis.html`|双击浏览的本地分析表、每例字段差异与问题详情；模型文本全部转义，报告不加载外部资源|
|`analysis.csv`|中文表头，可用 Excel 查看；对潜在公式起始字符作显示转义，原文不变|
|`analysis.json`|机器可读的解析、对照和原文 SHA-256；含模型字段文本，按本地实验材料保管|
|`human_review.md`|人工复核表：预测正确性、行号相关性、证据充分性、POC 安全、触发、总体改善均为“待复核”|
|`raw_snapshots/`|本次读取的 V1 原文字节副本，哈希与原文件一致；分析末尾重新检查源文件未变化|

自动检查：严格 JSON 解析（重复键、非标准 NaN/Infinity、多个 JSON 结论块均拒绝自动选择）、字段类型与枚举、sample_id、Fxx 行号是否在实际输入内、evidence 中不存在的行号提示、Python POC 语法、V0/V1 输入与包哈希、预测/行号/证据字段/POC 字段的字面差异。没有 json 代码围栏但全文是有效 JSON 时可解析，同时保留格式提示；不会修复损坏 JSON。

V0 基线按 V1 元数据的 `v0_reference_run_id` 选取，S013 使用 DeepSeek R2，不选早先 GPT 试跑。程序读取 V0 原始文本重新解析，并核对其哈希；不把规范化文件中已有结论当新模型输出。

自动结果的限制：

- 行号存在不代表引用正确，文字变化不代表证据改善；预测是否正确需人工对照 A 的已审核真值。
- Python 可解析不代表能安全运行、只访问本地或成功触发；手工 POC 无可自动验证的执行结论。
- 模型与设置的 session 字段匹配只表示用户填写与计划一致，需要原始界面/操作记录支撑；时间未知会明确报告。
- 缺少回答会显示“待保存原文”，不算一次观察；报错或拒绝原文按实保存，不改成 safe。
- 报告不生成 TP/FP/TN/FN、准确率或“V1 提升”结论，不写入正式实验、归档记录或冻结哈希。

`local/` 已被 `.gitignore` 忽略；原始回答、报告和 session 不会被普通 `git add` 自动提交。所有处理在本地完成。后续需要正式归档时，再由 B 根据实际元数据用已有 `b_runs.py record` 审核并操作；本工具不会代签人工复核。

## 软件验证

```powershell
python -m unittest discover -s tests -p test_b_local_analysis.py -v
```

测试使用合成回答和临时目录，覆盖原文/仓库不变、重复键和多结论拒绝、无效行号、损坏/拒绝文本、输入篡改、多文件冲突、HTML 转义、CSV 公式处理、POC 不执行、输出拒绝覆盖、会话缺项与 S013 类试跑隔离。合成测试不进入课程模型实验数据。
