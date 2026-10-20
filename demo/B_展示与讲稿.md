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

## 两分钟个人讲稿（2026-10-20 证据版）

“我负责给同一个模型设计 SQL 注入和 XSS 的三版审计任务，并记录它在相同代码输入上的差异。每份 Prompt 是完整的四段文本：角色、目标、漏洞专属判定、JSON 与 POC 契约。V0 已经能定位行号、讲清证据并限制本地验证；V1 候选要求把入口到危险操作的可达链条和有效防护写实；V2 候选进一步要求普通请求与测试请求对照，区分脚本可运行和漏洞实际触发。代码中的注释只是审计数据，不是模型命令，这一边界从 V0 就存在。

这里展示 S013 的三轮同包原始观察，全部 36 条开发回答均已归档。正式 36 条也已由 A 集成复核，每版的六个有漏洞与六个安全样本标签均判对，没有观察到 V1/V2 提高标签准确率。V1 补充部分执行点和跨请求证据，V2 的 POC 说明更具体，但我的九条正式记录仍未执行模型 POC；因此报告把预测、代码证据和实际触发分开。原文与哈希使每项结论都能追溯。

注释干扰的固定句式批次现有十六条真实原文，八对预测都未改变；V0 本来已有不可信代码边界，不能把结果解释为 V2 独有防护。输入只追加合法注释的差异已核对，语法与业务等价动态补证仍待做。我还复核了 C 的九条，发现一个 POC 的注释空格会被 trim 删除，另外两个普通对照会跳去外站。标签判对并不保证验证方案可靠，这正是需要人工复核的原因。”

## 证据索引与复现

Prompt：`prompts/{SQLi,XSS}_V{0,1,2}.txt`。输入和原文：`runs/{run_id}/{input.txt,raw_output.txt,metadata.json,normalized.json}`。静态复算：`python tools/b_final_evidence_audit.py --out <全新JSON路径>`，该命令不执行 POC。机器证据：`results/B_evidence_audit_2026-10-20.json`；注入：`results/B_injection.md`；复核：`results/B_review_C.md`；正式统计：`results/formal_eval_2026-10-19-v2/summary.md`。B 自己九条 POC 仍为 not_run，全组两条触发见各自运行证据，不能移作 B 的结果。
