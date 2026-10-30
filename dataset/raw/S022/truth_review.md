# S022 真值独立复核

- 复核人：A
- 结论：`ground_truth = false`
- 第二条读取路径裁定：与 S021 相同，`submit.php`、`list.php`、`preview.php` 构成写入—列表—独立预览流程，符合 XSS05 蓝图。
- 数据流：`submit.php:8-22` 接收并存储正文；`preview.php:7-21` 按编号读取；最终 `preview.php:39` 使用 `htmlspecialchars(..., ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')` 编码 HTML 正文。
- 运行证据：D 的浏览器证据显示列表页和单独预览页均没有脚本节点，DOM 标记保持空值；普通写入、列表和预览均可用。
- 当前源码适用性：证据提交 `a90708b` 到当前源码提交 `f82ddc2` 只新增数据库异常捕获和日志；三页面路由、存储/读取字段及最终编码行未改变，详见 `current_source_review.json`。
- 复核日期：2026-10-17

当前机器没有 Docker Desktop，因此没有把源码差异审计表述为一次新的容器复跑。
