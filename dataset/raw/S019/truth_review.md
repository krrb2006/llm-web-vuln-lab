# S019 真值独立复核

- 复核人：A
- 结论：`ground_truth = true`
- 源码链：`index.php:5-8` 接收 POST `content` 并传给模板；`templates/preview.php:16` 在 HTML 正文直接输出 `$content`。
- 运行证据：浏览器提交受控脚本后出现一个 script 节点，`document.documentElement.dataset.labXss` 从空值变为 `yes`；普通文本预览保持可用。
- 证据：`evidence/truth/S019/browser_reference.json`、`evidence/truth/S019/business_http.json`。
- 复核日期：2026-10-17

该结论只针对本地教学样本的反射型 XSS，不由被评估模型输出决定。
