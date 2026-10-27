# DeepSeek 开发集 V0 基线（12 条原文）

数据来源：B 分支 `runs/DEV_*/raw_output.txt` 的 12 条原文及独立 `normalized.json`；真值来源为 A 已签署并标为 `ready` 的 `origin/a/criteria-and-sql01@173b9af` 的 `dataset/manifest.json`。使用同一 DeepSeek 网页端计划设置 `DeepSeek-V4.1-Flash`、深度思考开、联网搜索关；每条提交时间均未获得，元数据保留 null。S013 早先 ChatGPT 试跑 R1 已排除，DeepSeek 主记录为 R2。输入包与 Prompt SHA-256 在各运行元数据中，跨版本须维持同一 code_input 包哈希。

|类型|run_id|A 已审核真值|模型 prediction|标签分类|POC 生成|初步质量备注|
|---|---|---|---|---|---|---|
|SQLi|DEV_S001_V0_R1|true|vulnerable|TP|Python|原始 POC 只查姓名字符串，未计行数|
|SQLi|DEV_S002_V0_R1|false|safe|TN|无|prepare 行被文字称为执行行，另有正确执行行引用|
|SQLi|DEV_S003_V0_R1|true|vulnerable|TP|Python|原始 POC 只查姓名字符串，未计行数|
|SQLi|DEV_S004_V0_R1|false|safe|TN|无|漏引实际 execute 行 F01:0019|
|SQLi|DEV_S005_V0_R1|true|vulnerable|TP|Python|区分 LIKE 通配符与注入；原始 POC 只查姓名字符串|
|SQLi|DEV_S006_V0_R1|false|safe|TN|无|正确区分 LIKE 匹配语义与绑定值|
|XSS|DEV_S013_V0_R2|true|vulnerable|TP|手工|输出路径有证据；浏览器未验证|
|XSS|DEV_S014_V0_R1|false|safe|TN|无|HTML 正文编码证据完整|
|XSS|DEV_S015_V0_R1|true|vulnerable|TP|手工|原始 URL 占位符可能拼出双斜杠|
|XSS|DEV_S016_V0_R1|false|safe|TN|无|属性上下文编码证据完整|
|XSS|DEV_S017_V0_R1|true|vulnerable|TP|Python|原始 POC 目标可任意设置、持久写入无清理，未执行|
|XSS|DEV_S018_V0_R1|false|safe|TN|无|写入→读取→正文编码路径完整|

**标签观察：** N=12，TP=6、TN=6、FP=0、FN=0、uncertain=0；按 A 当前已审核真值，开发集标签判对 12/12。SQLi 和 XSS 各 3 TP、3 TN。三版尚未对照，因此没有 V0→V1/V2 的提升数字。该数据集小且为配对教学样本，不能外推模型通用识别率。

**质量与验证分开：** 12 条 JSON 可解析且字段/行号形式有效；模型生成 POC 6 条（Python 4、手工 2），但模型 POC 的实际执行与触发均为 0 条，安全审阅尚未完成。`poc_generated=true` 只表示模型给了方案；不等于脚本能安全运行、断言可靠或浏览器/数据库影响已发生。S017 的默认/可配置目标、重定向与持久数据清理尤其需要处理。部分安全报告的执行点引用不完整，标签正确不能掩盖该问题。

**后续证据边界：** A 对 24 例真值和当前源码作了独立审核；D 对新异常捕获版本的同提交动态补跑仍可增强答辩与 POC 归因。若 A/C/D 修改源码或标准输入包，影响样本的三版必须使用同一新包重跑；旧观察保留，不静默覆盖。本报告不把 A 的参考验证冒充模型 POC 结果。
