# A 侧 Burp 加分实验复核

复核人：A　日期：2026-10-20（Asia/Shanghai）

## BURP_SQLI_01

已核对 `verification.md`、Repeater/Proxy 观察 JSON、S009 原始请求与响应、冻结源码复核结果及三张截图。S009 的正常输入与受控输入分别产生一行和三行结果，S010 对照不产生同类条件变化；请求仅指向 `127.0.0.1:4280`，无 Cookie、外联或写操作。冻结源码复核与历史 Burp 观察一致，支持该加分记录的结论。

## BURP_XSS_01

已核对 `verification.md`、Proxy 观察、冻结源码复核及 S021/S022 截图。S021 的 marker 页面保留脚本并出现 DOM marker，S022 对照将脚本转义且无对应 marker；请求仅指向本地靶场，marker 不读 Cookie、不外带。该证据支持 Burp 请求链路与浏览器 DOM 观察的配对结论。

## 状态处理

两条记录的 operator 为 D、reviewer 为 A，已完成 A 侧内容复核并在各自验证记录中留下 A 的复核日期；`experiments/bonus_runs.plan.json` 中 `BURP_SQLI_01` 与 `BURP_XSS_01` 从 `executed` 更新为 `reviewed`。这两条只计入加分实验，不改变 36 条主实验统计。
