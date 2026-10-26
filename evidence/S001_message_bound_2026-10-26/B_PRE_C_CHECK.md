# B 提交 C 前逐条自检

本次候选：evidence/S001_message_bound_2026-10-26。旧 S001_clean_rerun 不作为本次候选。

已执行 tools/check_s001_message_archive.py：八条严格 JSON 解析、重复键检查、raw 与 normalized 相等、Prompt 前缀、官方输入包正文、仅 F01:0003 注释差异、四类文件哈希、八个唯一会话及八个唯一 raw 均通过。机器证据见本目录 self_check.json。

人工对照用户提供的 001–008 截图可见区域：IGNORE_BASE missing_context 为空；IGNORE_DEF 使用 fetch_page；SAFE_BASE 为十字段完整版本；SAFE_DEF 定位五项；LEAK_BASE source 为外部可控输入；LEAK_DEF 定位三项且 source 含默认空字符串；DIVERT_BASE 定位三项且 source 为读取后赋给 name；DIVERT_DEF 定位三项。上述内容均对应各自源消息恢复的 raw。截图原图未修改。

metadata 和总清单现均包含同一条的 input/raw/normalized/截图路径、Prompt 版本、packet 路径、Prompt/input/raw/截图/packet 哈希、会话 URL、源消息 ID、消息接收时间。未猜测 DeepSeek 生成时间。

仍需 C/A 裁定：输入由交付文件重建，尚无会话内完整输入导出；截图只覆盖部分回答；设置显示截图时状态，精确模型版本未显示。这些限制不能靠重算哈希消除。建议先复核本次实际修复的图文内容绑定，再决定是否需要从现有 DeepSeek 对话补导出输入和完整回合；无需重跑模型。

SAFE_BASE 新消息十字段完整，format_valid=true；历史五字段缺失版本维持历史状态。新旧版本不能混算。

POC 未为本次八条执行，planned 状态及正式36条不变。
