# S020 真值独立复核

- 复核人：A
- 结论：`ground_truth = false`
- 源码链：`index.php:5-8` 接收 POST `content` 并传给模板；`templates/preview.php:11,16` 的两个输出位置均使用 `htmlspecialchars(..., ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')`。
- 运行证据：同一受控脚本在 textarea 和预览正文均以文本显示，未生成 script 节点，页面标记保持空值；普通文本预览保持可用。
- 证据：`evidence/truth/S020/browser_reference.json`、`evidence/truth/S020/business_http.json`。
- 复核日期：2026-10-17

安全结论限于本样本给定的两个 HTML 输出上下文。
