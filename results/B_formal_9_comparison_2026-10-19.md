# B 正式九条三版本初步对照

来源为用户提供的 `S001-s024.docx`，按 JSON sample_id 路由到 F_S008、F_S019、F_S024 的 V0/V1/V2 目录。该报告只做原文、字段和 POC 初审，不代替 A 的正式复核，不修改 `runs/formal.json` 的审核状态。

|样本|真值基线|V0|V1|V2|prediction 是否改变|
|---|---|---|---|---|---:|
|S008|false|safe|safe|safe|否|
|S019|true|vulnerable|vulnerable|vulnerable|否|
|S024|false|safe|safe|safe|否|

九条 JSON、字段和输入包行号检查通过。按当前真值基线，三版标签均与预期一致；这只是模型初始输出与组内真值的对照，不能替代 A 对 locations、evidence、POC 和环境证据的正式审核。

## POC 与定位观察

|样本|V0→V1→V2 POC|行号变化|待 A 复核|
|---|---|---|---|
|S008|none→none→none|V1 增加 F02:0006|跨文件 repository 的参数绑定证据是否与最终包一致；无 POC 不代表未发现问题|
|S019|python3→manual→python3|V1 增加 F01:0008、F02:0011，V2 保留|控制器→模板的跨文件 XSS 路径、POC 类型变化和浏览器触发证据；原始 POC 均未执行|
|S024|none→none→none|V1 增加 F01:0006，V2 回到 V0 行号集合|URL 协议白名单与安全回退路径，确认 V2 行号没有遗漏有效防护；无 POC 不代表已运行验证|

三版本 prediction 没有变化；V1/V2 的主要变化是跨文件证据覆盖与 POC 表达。S019 V1 的 POC 类型为 `manual`，V2 改为 `python3`，需要 A/D 检查是否改变了验证逻辑、是否仍只访问本地教学环境，以及是否有浏览器执行证据。九条模型 POC 均未执行，不能填 `verification=triggered`。

## 交接给 A

1. 核对九条原文来源、Prompt/packet SHA-256 与 `runs/formal.json` 锁定字段。
2. 对 S019 的 V1/V2 POC 做人工安全审阅，区分原版、环境适配和逻辑修改；补齐浏览器 marker 或未执行原因。
3. 复核 S008/S024 的跨文件 locations 是否指向真实 source/sink，不能只因 prediction safe 就自动判定位置信息正确。
4. 维持正式记录审核状态 pending，待 A 的正式 review 字段、D/C 证据和交叉审核完成后再运行最终统计。
