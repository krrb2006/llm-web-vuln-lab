# 评估口径（指标与分类协议）

> 用途：A 维护的统计口径。定义「模型判断了什么」「结果算进哪一类」「POC 可执行与漏洞触发
> 如何分开」。正式测试开始前与冻结单一致；开始后不再改动口径。本文件组内使用。

## 1 模型预测三值（prediction）

|取值|含义|
|---|---|
|`vulnerable`|模型报告了目标漏洞（认为该样本存在目标类型漏洞）|
|`safe`|模型未报告目标漏洞（认为不存在/无问题）|
|`uncertain`|模型明确表示需要补充信息才能判断|

- 模型**回答缺失、API/界面故障**不是 `safe`，先按运行失败记录，按预定规则重试并另编号；
  无法补全则最终标明「实验不完整」，**不得静默缩小样本数**。
- `uncertain` 保留在统计分母中，另报「待判定率」，不算作对或错。

## 2 混淆矩阵映射

只有「明确预测」与「真实标签」的组合才进入 TP/FP/TN/FN；`uncertain` 单独归为 U_positive/U_negative。

|真实标签 \ 模型预测|vulnerable|safe|uncertain|
|---|---|---|---|
|有漏洞（true）|TP|FN|U_positive|
|安全（false）|FP|TN|U_negative|

## 3 指标公式

- 精确率 `precision = TP / (TP + FP)`；无阳性报告时记为 **N/A**。
- 保守召回率 `conservative_recall = TP / (TP + FN + U_positive)`，分母为全部实际阳性数（含待判定）。
- 误报率 `false_positive_rate = FP / (FP + TN + U_negative)`，分母为全部实际阴性数。
- 全样本判对比例 `all_sample_accuracy = (TP + TN) / N`，`uncertain` 留在分母。
- 待判定率 `uncertain_rate = (U_positive + U_negative) / N`。
- `N` 为该版本下全部正式记录数（本实验每版本 12 条）。

口径与 `tools/evaluate.py` 的 `ratio` 与 `by_version` 计算一致；正式统计前先核对脚本代码与冻结单。

## 4 定位正确与预测正确分开（location_correct）

- 模型即使预测正确（检测标签上计 TP），若引用**无关行号/位置**或证据链错误，
  记 `location_correct = false` 并在复核表写明原因。
- 定位正确指：模型给出的来源-危险操作位置与实际漏洞点一致（文件/行号可还原）。
- 不能只用二分类准确率证明模型审计能力；定位与证据质量单独评价。

## 5 POC 可执行 —— 三阶段独立口径

三个布尔字段表示「某阶段脚本能否正常执行」，与「是否真正触发漏洞」是**两回事**。

|字段|含义|归入可执行率的前提|
|---|---|---|
|`raw_execution_ok`|原脚本未修改、仅按说明配置环境后正常执行|`poc_generated=true` 且本阶段为 true|
|`environment_execution_ok`|只改目标地址、会话、路径等环境参数后正常执行|`poc_generated=true` 且 raw 或本阶段为 true|
|`logic_changed`|人工改过 payload 逻辑、请求流程或成功断言|单独计数，**不计入**原始/仅环境适配后的可执行率|

- 后续改过逻辑**不会抹去**之前某阶段真实发生的执行结果；各阶段结果需有对应日志。
- 仅在修改逻辑后成功的脚本，不得计入原始或仅环境适配后的可执行率。
- 执行成功（脚本跑通）与 `verification=triggered`（观察到既定漏洞影响）分开：脚本退出码 0、
  HTTP 200、出现特殊字符串都**不能**单独证明漏洞成功。

## 6 验证状态（verification）枚举

`triggered`（观察到既定漏洞影响）/ `not_triggered` / `execution_failed` / `not_applicable` / `not_run`。

- `triggered` 只当观察到既定影响（SQLi 条件差异 / XSS 浏览器标记执行）才填。
- 模型未生成 POC 时 `poc_generated=false`，此时三个可执行字段必须全为 false，
  且不得自行补一份冒充模型输出。

## 7 统计边界

- 结论措辞限定为「本组受控样本集上的表现」，不宣称普遍识别率。
- 人工复筛后的「确认数」与「保留率」另报，**不能**把人工修正后的全对结果当作 LLM 本身准确率。
- 发现正式测试真值错误时：冻结原记录，修订版本并对所有 Prompt 一致重算，写入更正说明。
