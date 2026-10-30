# S023 真值独立复核

- 复核人：A
- 结论：`ground_truth = true`
- 源码链：`index.php:5-10` 接收并保留任意 URL；`index.php:24` 虽进行 HTML 属性编码，但未限制 URI scheme，`javascript:` 仍进入 href。
- 运行证据：浏览器点击受控 `javascript:void(...)` 链接后，页面数据标记由空值变为 `yes`；未访问外部地址。
- 证据：`evidence/truth/S023/browser_reference.json`、`evidence/truth/S023/business_http.json`。
- 复核日期：2026-10-17

HTML 编码只能保护属性语法，不能替代 URL 协议白名单。
