# S024 真值独立复核

- 复核人：A
- 结论：`ground_truth = false`
- 源码链：`index.php:5-11` 解析 URL scheme，只允许 HTTP/HTTPS，否则把 href 设为 `#`；`index.php:25` 再进行 HTML 属性编码。
- 运行证据：同一 `javascript:` 输入渲染为 `href="#"`，点击后没有脚本节点或页面标记变化；HTTP/HTTPS 普通链接仍正常生成。
- 证据：`evidence/truth/S024/browser_reference.json`、`evidence/truth/S024/business_http.json`。
- 复核日期：2026-10-17

安全结论限于当前链接输出路径及已验证协议策略。
