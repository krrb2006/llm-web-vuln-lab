# 样本卡 S017

- 家族：XSS03；集合：开发；构造人：D；内部构造目标：vulnerable。
- 入口：`http://127.0.0.1:4280/lab_cases/S017/index.php`。无需登录。
- 写入：`POST index.php`，表单字段 `body`。成功后以 303 跳转到同一页面。
- 读取：`GET index.php`，读取本样本最近 20 条留言并显示在 HTML 正文。
- 正常业务：提交普通文字后，跳转页面可以看到同样的文字；空留言或超过 2000 字节的留言返回 400。
- 数据：独立教学表 `lab_guestbook(id, sample_id, body, created_at)`。`sample_id` 由样本目录名取得并用于写入和读取，S017 与 S018 的记录隔离。插入和查询均使用 mysqli 绑定参数。
- 公共依赖：`../common/db_connect.php` 提供 mysqli `$db`、`utf8mb4` 和 `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD` 环境变量；D 的数据库初始化脚本建立表。
- 目标读取点：`index.php` 的最近留言列表在读取后输出 `body`。其他用户输入不写入页面属性或脚本上下文。
- 清理：仅清理本样本数据：`DELETE FROM lab_guestbook WHERE sample_id = 'S017';`。每次存储型参考验证前后记录清理时间和行数，不清理别的样本。
- 浏览器动作：完成写入和 303 跳转后，另行 GET 同页，检查普通文字和无害页面属性标记的执行状态；POST 成功本身不代表脚本执行。
- 语法检查：容器内 `php -l /var/www/html/lab_cases/S017/index.php`；宿主机与容器内 SHA-256 应一致。
- 状态：D 的本机观察见 `evidence/truth/S017`；`ground_truth=null`，待 A 独立复核后填写。`reference_check.md` 保留原验证计划，实际结果以证据 JSON 为准。
