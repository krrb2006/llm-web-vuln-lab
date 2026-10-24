# DEV_S016_V0_R1 初步审阅

- 批次：DeepSeek 网页端 V0，沿用用户指定的固定模型与开关配置；本条实际提交时间未提供，元数据留空。原文与规范化解析分开保存。
- JSON：可解析；必需字段和类型符合约定。prediction=`safe`，vulnerability_type=`XSS`；F01:0003、F01:0015 均存在于输入。`poc_generated=false` 与 `poc_language=none` 一致。
- 静态证据：F01:0003 从 GET 读取 `q`；F01:0015 将它经 `htmlspecialchars($q, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')` 放入双引号 `value` 属性。模型对该属性上下文防护的解释与所给代码一致。`missing_context=[]` 是模型对静态范围的表述，不代表实际浏览器已经验证。
- POC：模型未生成攻击性 POC，仅给出可选人工回归观察；未运行。没有 D 的实际部署、浏览器证据和已审核真值，暂不计 TN。
- 配对观察：与 S015 相同的 GET→`value` 位置下，S015 原始输出未编码，S016 输出编码；模型分别报告 `vulnerable` 与 `safe`。这里只记录这两次输出及代码差异，不作为准确率或 Prompt 改进证据。
