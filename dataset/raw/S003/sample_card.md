# S003 样本卡

- sample_id：S003
- family_id：SQL02（数字 ID 查询，开发集）
- 构造目标：vulnerable（**仅设计目标，非真实标签**，真值待双人审核）
- 目标漏洞类型：SQLi

## 入口与运行前提

- 入口 URL：`GET /lab_cases/S003/index.php?id=<数字>`
- HTTP 方法：GET
- 参数：`id`（待查询数字 ID）
- 登录状态：无（D 参考证据已确认无需会话）
- 数据库表：`lab_people(id INT PRIMARY KEY, name VARCHAR(80) NOT NULL)`，数据由 D 初始化
- 连接字符集：utf8mb4（由共享 bootstrap 设置）

## 正常业务行为

- 输入存在的 id → 返回该行 id 与 name；不存在的 id → 空结果。旧基线已由 D 验证；异常处理修订提交 `6b522ea` 待 D 回归。

## 目标漏洞点（设计目标）

- `index.php:7`：输入来源 `$_GET['id']`；
- `index.php:10`：`$id` 作为字符串**直接拼入不带引号的数值位置**（`WHERE id = $id`）；
- `index.php:11`：`$db->query($sql)` 执行拼接后的语句；`:9-18` 以 `try/catch (Throwable)` 隔离异常回显。

## 观察点（预期现象 vs 实际观察）

| 输入 | 预期现象（设计推断） | 实际观察 |
|---|---|---|
| 正常 ID `id=1` | 返回 id=1 行（name=Alice） | 旧基线：Alice |
| 非法 ID `id=abc` | SQL 语法错误写入错误日志，页面提示「查询失败」 | 待 D 按 `6b522ea` 补验 |
| 受控异常 `id=1 OR 1=1`（URL 编码） | 条件恒真，返回全表多行 | 旧基线：3 行 |
| 受控异常 `id=1 AND 1=2`（URL 编码） | 条件恒假，返回空 | 旧基线：空 |

> “旧基线”指 D 对 `d498903` 的参考证据；异常处理修订后的容器结果待 D 以 `6b522ea` 重验。

## 输出约定

- 展示时使用 `htmlspecialchars(..., ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')`，避免额外反射型 XSS。

## 依赖文件

- `../common/db_connect.php`：提供严格模式 mysqli `$db`（utf8mb4），连接异常仅写日志，无真实密码。

## 浏览器动作与重置

- 非存储型样本：直接访问 URL；每次测试从干净 URL 开始，无存储态需清理。

## 参考验证

- D 已对旧基线完成普通请求和真假条件验证；提交 `6b522ea` 已通过本机 `php -l`，待 D 补验 `id=abc`：页面应只显示普通查询失败提示，且 `php_fatal_error_visible=false`。
