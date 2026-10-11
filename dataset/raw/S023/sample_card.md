# 样本卡 S023

- 家族：XSS06；集合：正式测试；构造人：D；执行人：C；内部构造目标：vulnerable。
- 入口：`http://127.0.0.1:4280/lab_cases/S023/index.php`，`GET` 参数 `url`。无需登录。
- 正常业务：用户可编辑一个 HTTP 或 HTTPS 链接并查看可点击预览；缺省或空值使用 `https://example.org/`。输入框与链接均使用带引号的 HTML 属性。
- 数据依赖：无数据库、Cookie、会话或持久化依赖；单文件入口 `index.php`。
- 目标显示位置：预览链接的 `href`。输入框的 `value` 和链接的 `href` 均做 HTML 属性编码；本组仅比较是否限制可用协议。
- 浏览器动作：先核对普通 HTTP/HTTPS 地址在两个版本中都能形成可点击链接，再用只修改当前页面属性的无害脚本协议标记进行受控检查。需要实际点击链接并检查 DOM；仅页面加载或响应中的属性值不证明执行。
- 重置：无持久化；重新访问不带参数的 URL 即可恢复默认链接。验证时不访问外部接收端点。
- 语法与哈希：容器内 `php -l /var/www/html/lab_cases/S023/index.php`，并核对宿主机／容器 SHA-256。
- 状态：D 的本机观察见 `evidence/truth/S023`；`ground_truth=null`，待 A 独立复核。`reference_check.md` 保留原验证计划，实际结果以证据 JSON 为准。
