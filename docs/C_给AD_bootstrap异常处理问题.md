# 给 A/D：共享 bootstrap 的 mysqli 异常处理隐患（S001–S012）

> 本文是 C 的交接说明，供 A/D 决策。C 不改动任何公共文件（bootstrap.php 等）。

## 背景
PHP 8.1 起，mysqli 默认错误上报模式为 `MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT`，
查询 / 预处理失败时**抛出 `mysqli_sql_exception`**，而不是仅返回 `false`。

SQL 样本 S001–S012 的 index.php 均依赖共享 bootstrap.php 提供 `$db`，且普遍用
`if ($result === false)` / `if ($stmt === false)` 判断失败。在默认异常模式下，这种判断
接不住异常：`$db->query()` 一旦失败直接抛异常，未捕获时即 Fatal error，页面回显数据库
错误细节。D 已在 S009 容器内实测复现（PHP 8.5.11 + MariaDB 10.11）：
`mysqli_sql_exception ... near ')' at index.php:14` 直接回显到页面。

## 影响
- 违反《C 样本与预处理操作手册》"查询错误进日志"：错误细节回显页面而非写入日志。
- Fatal error 会成为模型可观察的页面内容，干扰误报 / 漏报判断。

## 已核实的范围
- C 名下 S009–S012 均已核实存在此模式：
  - S009/S010：原为 `if ($result === false)` / `if ($stmt === false)`，**本次已在样本内改为
    try/catch (Throwable)**（见下）。
  - S011/S012：仍为 `$db->query(...)` + `if ($result === false)`（S011 line 14–17、S012 line 16–18），
    属同一隐患，尚未处理，待统一口径后对齐。
- S001–S008 为 A 名下样本，C 未改动；请 A 自行确认是否同样使用 `if ($result === false)` 模式。

## S009/S010 已做的自包含修复（不改公共文件）
两版已在各自 index.php 内把查询块包进 `try { ... } catch (Throwable $e) { ... }`，catch 中：
- `error_log('lab_people query failed: ' . $e->getMessage())` 写日志；
- 页面保持普通业务输出（如空结果），不回显错误细节。

两版 catch 文本一致，配对唯一差异仍是 **IN 字符串拼接（S009）vs 占位符 + bind_param 绑定（S010）**。
修复后源码哈希已更新，需 D 按新哈希重跑 php -l 与参考验证。

## 建议（交 A/D 决定，二选一，避免样本内各改各的）
1. 在共享 bootstrap.php 显式 `mysqli_report(MYSQLI_REPORT_OFF)`，让所有样本继续沿用
   `if ($result === false)` 的返回式判错，错误经 `$db->error` + `error_log` 写日志；
   或
2. 保持默认异常模式，要求所有样本在查询处自包含 `try/catch (Throwable)`（S009/S010 已示范）。

无论选哪种，共同目标：**错误只进日志、不回显页面**。

## 后续
- 公共文件（bootstrap.php）的修改由 A/D 执行，C 不直接改动。
- 若采纳方案 1（统一 mysqli_report），S009/S010 的自包含 try/catch 可保留（无害）或按统一口径回退，
  请 A/D 给出结论后 C 再批量对齐 S011/S012。
