# 每日实验日志（A）

日期、成员、工作时长：2026-10-10，A，约 6 小时（累计）

今天完成的可打开文件和版本：
- `docs/judgment_criteria.md`、`docs/metrics_protocol.md`（判定规则 + 指标口径）
- `dataset/raw/S001`–`S008`（8 个 SQLi 配对样本代码草稿，各含 index.php、sample_card.md、source_note.md、truth_review.md；S007/S008 另含 repository.php）
- `docs/A_给D_验证任务清单.md`、`docs/A_给C_真值复核清单.md`、`docs/A_给B_提示词交接说明.md`
- `docs/A_报告与PPT框架初稿.md`
- 本机安装 PHP 8.3.33（CLI）用于语法检查

运行的样本编号或 run_id：无（尚未运行；本机无 Docker 运行环境）

命令与运行结果摘要：
- `php -l`：S001–S008 全部 PHP 文件 + 共享 db_connect.php 均通过（本机 PHP 8.3.33）。
- `prepare_input.py` 中性检查：8 例审计输入均无「漏洞/修复」标签泄露；修复了 S001–S006 代码注释的中性化问题并同步行号/哈希。
- `evaluate.py` 合成数据自检：TP/FP/TN/FN/待判定/精确率/召回率/误报率计算与手工期望一致。

今天发现的阻塞及证据：
- 本机无 Docker / PHP 运行环境（已装 PHP CLI，仅能语法检查，不能运行验证）；DVWA 靶场待 D 搭建。
- 真值（ground_truth）无法脱离参考验证填写，全部保持 null。

与哪位成员交接，交付了什么：
- D：S001–S008 容器验证任务清单（语法检查、哈希核对、普通业务、受控输入）。
- C：S001–S008 真值复核清单。
- B：Prompt 与输出字段交接说明。

下一工作日具体操作：待 D 环境就绪后做参考验证并填真值；待 C 复核；待 B 产出 6 份 Prompt。

本人成果提交记录或截图路径：分支 `a/criteria-and-sql01`，PR #1。

遇到失败保留原始日志，不用「解决了」替代根因和复测结果。
