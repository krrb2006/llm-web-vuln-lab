# 课程评分项证据就绪审计

结论：**可提交**

|评分层级|检查项|完成|目标|状态|
|---|---|---:|---:|---|
|基础|24例数据集计划|24|24|READY|
|基础|样本源码落库|24|24|READY|
|基础|标准输入包与行号映射|24|24|READY|
|基础|独立真值复核|24|24|READY|
|基础|六份Prompt文本|6|6|READY|
|基础|正式记录计划|36|36|READY|
|基础|正式记录完成且证据可读|36|36|READY|
|基础|统计产物|1|1|READY|
|基础|最终实验报告|1|1|READY|
|加分|加分实验计划结构|1|1|READY|
|加分|加分实验完成且证据可读|4|26|PARTIAL|
|加分|二次注入与逻辑漏洞代码蓝图|6|6|READY|
|工程|自动化测试工作流|1|1|READY|

## 加分实验计划

- `prompt_injection`：16/16
- `burp_linkage`：2/2
- `context_ablation`：4/4
- `advanced_case`：4/4

## 口径说明

- READY only means required files and review states are present; humans must still inspect evidence content.
- Planned bonus records never count as completed evidence.
