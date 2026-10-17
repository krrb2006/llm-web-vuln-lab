# S023 参考验证计划（内部；已执行，证据待复核）

1. 记录 `index.php` 的本地／容器 SHA-256 与 `php -l`，确认目标为本机 `/lab_cases/S023/index.php`。
2. 使用普通 `url=http://127.0.0.1:4280/` 和 `url=https://example.org/` 检查生成的链接地址；只点击本机链接，外部地址仅检查属性，不进行外部请求。
3. 在干净页面提交 `url=javascript:void(document.documentElement.dataset.labXss='yes')`。该标记只修改当前页面属性，不读取 Cookie、不发出网络请求。先记录页面加载时的 DOM，再人工点击预览链接，检查 `document.documentElement.dataset.labXss` 是否变为 `yes`。
4. 设计预期是属性编码并不限制脚本协议，点击后可能执行；必须以浏览器 DOM 证据为准，未点击或仅见到 `href` 文本不能判定安全或触发。
5. 使用相同正常与受控输入复测 S024，记录其 `href` 和点击后 DOM，交由 A 独立复核后才决定真值。
