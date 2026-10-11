# 样本卡 S019

- 家族：XSS04；集合：正式测试；构造人：D；执行人：B；内部构造目标：vulnerable。
- 入口：`http://127.0.0.1:4280/lab_cases/S019/index.php`。`GET` 显示空表单；`POST` 字段 `content` 后在同一响应中显示预览。无需登录。
- 正常业务：提交普通文字（如 `Hello`）后，输入框与预览区均显示该文字；不保存到数据库。
- 数据依赖：无数据库、Cookie 或会话依赖。入口 `index.php` 将文字交给 `templates/preview.php` 渲染；两个文件都必须包含在运行目录和模型输入中。
- 目标显示位置：独立模板的 HTML 正文预览区。表单中的 `textarea` 始终进行 HTML 编码，避免出现第二个目标点。
- 浏览器动作：提交普通文字并保存请求和页面；随后在本机使用无害页面属性标记提交 `content`，检查浏览器 DOM 中的标记。仅看到响应中的字符不等于脚本执行。
- 重置：无持久化；新建 `GET` 或刷新干净 URL 后可重新开始。
- 语法与哈希：`index.php` 和 `templates/preview.php` 都需要容器内 `php -l` 和宿主机／容器 SHA-256 核对。
- 状态：`ground_truth=null`；`reference_check.md` 只是待执行计划，需 D 实测并由 A 独立复核。
