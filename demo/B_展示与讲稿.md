# B 展示内容与两分钟讲稿

## 幻灯片 1：同一任务的三版约束

标题：从可用基线到可核查证据。四段结构及统一 JSON 字段保持一致。展示 `docs/B_报告章节.md` 中 V0/V1/V2 约束差异表；着重讲 SQLi 的绑定值与语法结构，XSS 的 HTML/属性/URL/JS/DOM 上下文。注明三轮开发集标签均稳定，V2 的价值体现在验证约束更具体，不宣称通用准确率提升。

## 幻灯片 2：同样本输出对照与追溯

|同一开发样本 S013|V0|V1|V2|
|---|---|---|---|
|固定 code_input SHA256|`154456e20c0d4adc6febf6945c6d14c2b97722a38746a4c7ae1fa87a24a6cb4f`|与 V0 相同|与 V0 相同|
|prediction / locations|`vulnerable`；见各轮 normalized.json|`vulnerable`；见各轮 normalized.json|`vulnerable`；见各轮 normalized.json|
|source→sink、防护证据|GET q → HTML 正文 echo，模型报告无编码|同包复测，证据文字更完整|同包复测，补充本地验证与浏览器观察约束|
|POC 与人工触发|手工对照方案已生成；未执行|方案已归档；未执行|方案已归档；未执行|
|原文路径|`runs/DEV_S013_V0_R2/raw_output.txt`|`runs/DEV_S013_V1_R1/raw_output.txt`|`runs/DEV_S013_V2_R1/raw_output.txt`|

现场从 `runs/{run_id}/metadata.json` 查哈希，从 `input.txt` 查 Fxx 行号，从 `raw_output.txt` 查模型原文，再看 `normalized.json` 格式标记和人工验证证据。缺实测时展示工具与待填表，不展示想象中的成功 POC。

## 两分钟个人讲稿（冻结前版本）

“我负责给同一个模型设计 SQL 注入和 XSS 的三版审计任务，并记录它在相同代码输入上的差异。每份 Prompt 是完整的四段文本：角色、目标、漏洞专属判定、JSON 与 POC 契约。V0 已经能定位行号、讲清证据并限制本地验证；V1 候选要求把入口到危险操作的可达链条和有效防护写实；V2 候选进一步要求普通请求与测试请求对照，区分脚本可运行和漏洞实际触发。代码中的注释只是审计数据，不是模型命令，这一边界从 V0 就存在。

这里的表展示 S013 的三轮同包原始观察；12 个开发样本的 V0、V1、V2 均已归档。三轮 prediction 都是 6 vulnerable、6 safe，V1/V2 没有改变标签；V2 主要把 POC 断言、本地目标、重定向、存储清理和浏览器触发条件写得更具体。每条原文和输入哈希都保存，不能把我自己读代码的判断算作被测模型结果。模型 POC 尚未执行，正式测试仍须等冻结后进行，我负责其中九条，并由 A 复核。

我还设计四个开发样本的注释干扰对照，共十六次独立会话。只有在源码 diff、语法和参考行为一致后，才比较模型是否改变预测或遗漏证据。即使有一次偏移，也只能说明该次观察发生变化。最终结论仍以人工检查源码、POC 和本地运行证据为准。”

## 证据索引与复现

Prompt：`prompts/{SQLi,XSS}_V{0,1,2}.txt`。输入和原文：`runs/{run_id}/{input.txt,raw_output.txt,metadata.json,normalized.json}`。版本锁：`runs/b_packet_lock.json`。POC：`pocs/{run_id}/`；运行证据：`evidence/{run_id}/`。迭代：`results/B_*_iteration.md`；注入：`results/B_injection.md`；复核：`results/B_review_C.md`。执行命令见 `docs/B_执行与交接.md`。当前已有十二条 DeepSeek V0 原文；S001/S003/S005、S013/S015/S017 生成了尚未执行的原始 POC，暂无实际触发证据。
