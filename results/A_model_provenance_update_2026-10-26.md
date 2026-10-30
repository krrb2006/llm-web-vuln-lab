# DeepSeek 网页默认模式与版本口径更新（2026-10-26）

## 结论

本仓库中于 2026-10-19 及之后以 DeepSeek 网页默认/快速模式完成的记录，统一表述为：

> DeepSeek 网页默认/快速模式（官方版本映射：DeepSeek-V4.1-Flash-1017）；深度思考开启，智能搜索关闭。

DeepSeek 官方于 2026-10-17 公告 V4.1 Flash 升级为 `DeepSeek-V4.1-Flash-1017`，并说明官方网页端和 App 同步更新。官方来源：

- <https://api-docs.deepseek.com/updates/>
- <https://api-docs.deepseek.com/news/news261017/>

## 适用证据链

1. `runs/formal.json` 的 36 条记录均为 2026-10-19 的网页端运行；历史 UI 口径为默认/快速模式。
2. `evidence/S001_D_default_2026-10-26/` 的八条记录保存了 UI `default/快速模式` 通道、深度思考开启、智能搜索关闭和会话截图。
3. 上述日期均晚于官方网页端更新日，故将原先笼统的 `DeepSeek-V4.1-Flash` 更正为精确版本 `DeepSeek-V4.1-Flash-1017`。

## 保留限制

没有 API/HAR 的逐请求 `model` 字段，也没有在每张历史截图中直接显示后端版本号。版本判断来自“会话默认/快速模式证据 + 官方网页端版本更新公告”的组合，而非伪造的接口快照。原始模型回答、Prompt、输入包和运行结果均未改写。
