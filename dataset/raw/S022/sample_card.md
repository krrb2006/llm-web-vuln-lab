# 样本卡 S022

- 家族：XSS05；集合：正式测试；构造人及执行人：D；内部构造目标：fixed。
- 写入入口：`http://127.0.0.1:4280/lab_cases/S022/submit.php`，`POST` 字段 `title` 和 `body`；成功后以 303 跳转到 `preview.php?id=...`。无需登录。
- 读取入口：`GET list.php` 列出本样本草稿标题；`GET preview.php?id=...` 按数字编号读取并显示指定草稿的标题和正文。不存在的编号返回 404。
- 正常业务：提交普通标题和正文后，预览页显示两者；列表可打开同一草稿。标题不超过 120 字节，正文不超过 2000 字节。
- 数据：独立教学表 `lab_preview_drafts(id, sample_id, title, body, created_at)`。`sample_id` 由目录名取得，并在写入、列表和预览查询中使用；S021 与 S022 记录隔离。所有 SQL 都使用 mysqli 绑定参数。
- 公共依赖：`../common/db_connect.php` 提供 mysqli `$db`、`utf8mb4` 和 `DB_*` 环境变量；D 的数据库初始化脚本建立表。
- 目标读取点：`preview.php` 的正文区域在读取后做 HTML 正文编码。`list.php` 标题及 `preview.php` 标题均做 HTML 编码，列表链接只使用整数 ID。
- 清理：仅清理本样本数据：`DELETE FROM lab_preview_drafts WHERE sample_id = 'S022';`。测试前后记录清理时间和行数。
- 浏览器动作：提交草稿后保存写入和 303 跳转证据，再单独访问列表与预览页；在预览页观察无害页面属性标记的执行状态。列表标题出现文字或 HTTP 200 不能证明目标影响。
- 语法检查：容器内分别对 `submit.php`、`list.php`、`preview.php` 运行 `php -l`；逐文件核对宿主机与容器内 SHA-256。
- 状态：D 的本机观察见 `evidence/truth/S022`；`ground_truth=null`，待 A 独立复核后填写。`reference_check.md` 保留原验证计划，实际结果以证据 JSON 为准。
