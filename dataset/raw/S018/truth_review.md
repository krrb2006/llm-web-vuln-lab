# S018 真值独立复核

- 复核人：A
- 结论：`ground_truth = false`
- 数据流：`index.php:8` 接收留言，`:15-18` 写入，`:30-34` 读取；最终 `:53` 使用 `htmlspecialchars(..., ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')` 编码 HTML 正文。
- 运行证据：D 的独立浏览器 GET 在写入后及再次读取时均未出现脚本节点，DOM 标记保持空值；普通留言业务可用。
- 当前源码适用性：证据提交 `a90708b` 到当前源码提交 `f82ddc2` 只新增数据库异常捕获和日志；存储/读取链和最终编码行未改变，详见 `current_source_review.json`。
- 复核日期：2026-10-17

结论仅针对本地教学样本中的该 HTML 正文输出路径。当前机器没有 Docker Desktop，因此没有把源码差异审计表述为一次新的容器复跑。
