# DEV_S018_V0_R1 初步审阅

- 批次：DeepSeek 网页端 V0，沿用用户固定模型与开关配置；实际提交时间未提供，元数据留空。
- JSON：可解析，必需字段/类型符合契约。prediction=`safe`、vulnerability_type=`XSS`；F01:0008、F01:0015、F01:0016、F01:0030、F01:0033、F01:0053 均在锁定输入包中。`poc_generated=false` 与 `poc_language=none` 一致。
- 静态证据：F01:0008 读取 POST `body`，F01:0015—0016 参数化写入，F01:0030—0033 另一次读取，F01:0053 通过 `htmlspecialchars(..., ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')` 输出到 HTML 正文。模型说明适用编码与上下文，且没有把 SQL 参数化误当 XSS 防护；与当前源码一致。A 已审核真值为 `false`，本条没有运行浏览器验证。
- POC：未生成攻击性 POC；可选手工文本回归只是建议，没有执行。安全标签基于所给路径的源码与已审核真值，不将“脚本未运行”当作安全证据。
- 配对观察：S017/S018 的写入和读取链相同，HTML 正文输出是否编码不同；两条 V0 原文分别给 `vulnerable` 与 `safe`。该观察不证明 V1/V2 相比 V0 有改进。
