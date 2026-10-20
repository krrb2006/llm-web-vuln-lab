# B 对 C 正式记录的复核

状态：9/9 已完成 B 的独立静态复核（2026-10-20）；模型 POC 动态执行尚未完成。基线为 A 集成提交 `45dddaf`。

## 2026-10-20 实际独立复核

B 逐条重新读取九条原文、实际输入与源码，并复算 Prompt、packet、input 和 raw 哈希。复算程序与机器结果：`tools/b_final_evidence_audit.py`、`results/B_evidence_audit_2026-10-20.json`。九条原文字节哈希及标准包映射全部通过，prediction 和 poc_generated 均与正式记录一致。A 原先已将记录标 reviewed，本次保留其历史字段，不伪造动态执行或截图。

|run_id|哈希/JSON/源码映射|原文 prediction|POC|实际意见|
|---|---|---|---|---|
|F_S009_V0_R1|通过|vulnerable|Python，未运行|默认根路径需与实际入口核对|
|F_S009_V1_R1|通过|vulnerable|明确未生成|因入口未知而不生成 POC，不能误填为 true|
|F_S009_V2_R1|通过|vulnerable|Python，未运行|`-- ` 尾空格会被源码 trim 去掉；原测试可能 SQL 语法失败|
|F_S012_V0_R1|通过|safe|无|固定 id/name 白名单覆盖 ORDER BY 的动态结构|
|F_S012_V1_R1|通过|safe|无|白名单传播和实际 query 执行点可追溯|
|F_S012_V2_R1|通过|safe|无|模型指出预置数据两种排序可能相同，不能以无差异作安全证明|
|F_S023_V0_R1|通过|vulnerable|手工，未运行|普通对照在本地，仍需实际点击后观察执行|
|F_S023_V1_R1|通过|vulnerable|手工，未运行|普通对照要求点击 example.org，超出本地验证约束|
|F_S023_V2_R1|通过|vulnerable|手工，未运行|同样含外部普通对照，需要本地适配和真实浏览器证据|

S009 的 source/构造/query 对应 F01:0008/0013/0015；S012 的固定映射在 F01:0009—0013、执行在 F01:0017；S023 的 source/href/sink 对应 F01:0005/0010/0025。九条 evidence 均与这些实际路径相符。S009 V2 的 `0) UNION SELECT ... -- ` 经 trim 后失去注释必需空白，属于 POC 问题，不据此反推误报；不能偷偷改原版 payload。S023 的属性编码不限制 URL 协议，执行必须以点击后的浏览器状态确认，原有参考浏览器记录不能冒充模型 POC 证据。

实际生成 POC 的是 5 条（S009 V0/V2、S023 三版），不是 6 条。九条均 `verification=not_run`，运行目录没有模型/设置截图；请执行侧补原有截图或说明当时未采集，不得事后伪造或静默重跑。B 本次完成九条静态复核；S009 V2、S023 V1/V2 的 POC 执行审阅暂不通过，任何后续环境适配或逻辑修改均需另存与保留 diff。
