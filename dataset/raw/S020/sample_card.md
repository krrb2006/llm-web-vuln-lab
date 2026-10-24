# 样本卡 S020

- 家族：XSS04；集合：正式测试；构造人：D；执行人：A；内部构造目标：fixed。
- 入口：`http://127.0.0.1:4280/lab_cases/S020/index.php`。`GET` 显示空表单；`POST` 字段 `content` 后在同一响应中显示预览。无需登录。
- 正常业务：提交普通文字（如 `Hello`）后，输入框与预览区均显示该文字；不保存到数据库。
- 数据依赖：无数据库、Cookie 或会话依赖。入口 `index.php` 将文字交给 `templates/preview.php` 渲染；两个文件都必须包含在运行目录和模型输入中。
- 目标显示位置：独立模板的 HTML 正文预览区。表单中的 `textarea` 始终进行 HTML 编码；配对差异仅为预览正文输出时的编码。
- 浏览器动作：使用与 S019 完全相同的普通文字和无害页面属性标记，保存请求和页面，在本机检查浏览器 DOM；保留预览区的正常显示能力。
- 重置：无持久化；新建 `GET` 或刷新干净 URL 后可重新开始。
- 语法与哈希：`index.php` 和 `templates/preview.php` 都需要容器内 `php -l` 和宿主机／容器 SHA-256 核对。
- 状态：D 的本机观察见 `evidence/truth/S020`；`ground_truth=null`，待 A 独立复核。`reference_check.md` 保留原验证计划，实际结果以证据 JSON 为准。
