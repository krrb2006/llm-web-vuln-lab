# D 正式九条运行说明（2026-10-19）

## 一、范围与冻结条件

- 样本与版本：`S010`、`S011`、`S022` 各 V0/V1/V2，共 9 条 `F_*_R1`。
- 输入：`local/D_formal_kit/<run_id>/input.txt` = 冻结 Prompt + 空行 + `code_input.txt`；`prompt_sha256`、`packet_sha256` 与 `runs/formal.json` 计划一致。
- 模型显示名：`DeepSeek-V4.1-Flash`。运行时页面顶部提示“DeepSeek V4.1 Flash 现已更新至 V4.1-Flash-1017 版本”，`metadata.json` 另记 `model_snapshot=V4.1-Flash-1017`。
- 设置：深度思考 = 开，智能搜索 = 关；每条新开独立会话，未复用上下文。
- 提交方式：D 授权，使用 Chrome 155 + DevTools Protocol 自动提交；每条保存 `screenshot_settings.png`、`screenshot_answer_1.png`、`screenshot_answer_2.png`，原文由页面“复制”按钮原样导出。

## 二、结果

真值取自 `dataset/manifest.json`（S010 safe、S011 vulnerable、S022 safe）。

| run_id | sample | 版本 | prediction | 真值 | POC | verification |
|---|---|---|---|---|---|---|
| F_S010_V0_R1 | S010 | V0 | safe | safe | 无 | not_run |
| F_S010_V1_R1 | S010 | V1 | safe | safe | 无 | not_run |
| F_S010_V2_R1 | S010 | V2 | safe | safe | 无 | not_run |
| F_S011_V0_R1 | S011 | V0 | vulnerable | vulnerable | 无 | not_run |
| F_S011_V1_R1 | S011 | V1 | vulnerable | vulnerable | 有 | triggered |
| F_S011_V2_R1 | S011 | V2 | vulnerable | vulnerable | 有 | triggered |
| F_S022_V0_R1 | S022 | V0 | safe | safe | 无 | not_run |
| F_S022_V1_R1 | S022 | V1 | safe | safe | 无 | not_run |
| F_S022_V2_R1 | S022 | V2 | safe | safe | 无 | not_run |

- 9/9 的 `prediction` 与当前真值一致；`status` 均为 `executed_pending_review`，等待 C 复核。
- 只有 S011 V1/V2 生成了 POC。两条都为只读 GET，目标固定 `127.0.0.1:4280`，成功后断言“行序变化”，不修改数据。

## 三、POC 执行

### F_S011_V1_R1

- 原脚本：`pocs/F_S011_V1_R1/original.py`，入口写死为根路径 `/`；直接运行 exit 1，页面不返回教学列表（`stdout_original.txt`）。
- 环境适配：`adapted.py` 仅把 `BASE_URL` 改为 `http://127.0.0.1:4280/lab_cases/S011/index.php`，请求参数与成功断言未改；diff 见 `evidence/F_S011_V1_R1/adapted.diff`。
- 结果：exit 0；`sort=id` → (1,Alice)(2,Bob)(3,Carol)，`sort=(id=2) DESC, id ASC` → (2,Bob)(1,Alice)(3,Carol)，行序改变。

### F_S011_V2_R1

- 原脚本：`pocs/F_S011_V2_R1/original.py`，要求用 `ENTRY_PATH` 指定入口；未改代码，设置 `ENTRY_PATH=/lab_cases/S011/index.php` 后运行。
- 结果：exit 0；`sort=id` → 1,2,3，`sort=(CASE WHEN (SELECT COUNT(*) FROM lab_people)=3 THEN -id ELSE id END)` → 3,2,1，行序反转。
- 数据未修改；脚本拒绝非 loopback 主机和重定向。

其余 6 条模型未生成 POC，`verification=not_run`，未自行补写攻击脚本。

## 四、边界与待复核

1. **模型快照**：页面横幅显示 `V4.1-Flash-1017`，冻结单只写 `DeepSeek-V4.1-Flash`。需要 B 确认其 9 条是否也是 1017，并由 A 在冻结单/计划中补记快照；若批次不同，A/C 需裁定是否可比。
2. **提交方式**：本轮由 D 授权、通过浏览器自动化提交，原文和截图仍来自该账号会话；C 复核时如不认可这种来源，需要在记录中明确，不能当作纯手工会话。
3. **POC 适配**：S011 V1 只改入口路径，`raw_execution_ok=false`、`environment_execution_ok=true`；S011 V2 原脚本未改，`raw_execution_ok=true`、`environment_execution_ok=true`。
4. 未修改任何真值、Prompt 或输入包；`ground_truth` 仍以 `dataset/manifest.json` 为准。
5. 9 条记录等待 C 复核后将 `status` 改为 `reviewed`；D 不自行改状态。

## 五、证据入口

- 运行目录：`runs/F_S010_*`、`runs/F_S011_*`、`runs/F_S022_*`（`input/raw_output/normalized/metadata/screenshot_*`）。
- POC：`pocs/F_S011_V1_R1/`、`pocs/F_S011_V2_R1/`。
- 执行日志与验证单：`evidence/F_S010_*`、`evidence/F_S011_*`、`evidence/F_S022_*`。
- 汇总记录：`runs/formal.json` 中 `operator=D` 的 9 条。
