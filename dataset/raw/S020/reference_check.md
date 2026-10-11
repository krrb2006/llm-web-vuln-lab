# S020 参考验证计划（内部，尚未执行）

1. 记录 `index.php` 与 `templates/preview.php` 的本地／容器 SHA-256，运行两处 `php -l`，确认实际 URL 为本机 `/lab_cases/S020/index.php`。
2. `GET` 打开空表单；`POST content=Hello`，保存请求和响应，确认表单及预览区均显示 `Hello`。
3. 新建干净请求，使用与 S019 相同的无害页面属性标记作为 POST `content`；在浏览器开发者工具检查 `document.documentElement.dataset.labXss`。标记不得读取 Cookie 或发起外部请求。
4. 设计预期是预览区作为文本显示输入，页面属性标记不执行；以实际 DOM 为准，不能只凭 HTML 源码或 HTTP 200 判定。
5. 对比 S019 和 S020 的控制器及模板差异，确认仅预览正文编码变化；保存正常与受控输入的证据，由 A 独立复核后才决定真值。
