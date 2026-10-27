# S019 参考验证计划（内部；已执行，证据待复核）

1. 记录 `index.php` 与 `templates/preview.php` 的本地／容器 SHA-256，运行两处 `php -l`，确认实际 URL 为本机 `/lab_cases/S019/index.php`。
2. `GET` 打开空表单；`POST content=Hello`，保存请求和响应，确认表单及预览区均显示 `Hello`。
3. 新建干净请求，以 `<script>document.documentElement.dataset.labXss='yes'</script>` 作为 POST `content`；该标记只修改当前页面属性，不读取 Cookie、不发出网络请求。在浏览器开发者工具检查 `document.documentElement.dataset.labXss`，并保存页面和 DOM 证据。
4. 设计预期是模板预览区将该输入解释为脚本；以实际浏览器观察为准，不能以 HTTP 200 或响应含有脚本文字替代执行证据。
5. 按相同输入复测 S020，确认正常业务一致，记录配对差异与任何失败；由 A 独立复核后才决定真值。
