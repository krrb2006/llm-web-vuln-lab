# S002 样本卡

- sample_id：S002
- family_id：SQL01（姓名精确查询，开发集）
- 构造目标：fixed（**仅设计目标，非真实标签**，真值待双人审核）
- 目标漏洞类型：SQLi

## 入口与运行前提

- 入口 URL：`GET /lab_cases/S002/index.php?name=<姓名>`
- HTTP 方法：GET
- 参数：`name`（待查询姓名）
- 登录状态：无（D 参考证据已确认无需会话）
- 数据库表：`lab_people(id INT PRIMARY KEY, name VARCHAR(80) NOT NULL)`，数据由 D 初始化
  （参考 D 手册：Alice/Bob/Carol 等虚构人员）
- 连接字符集：utf8mb4（由共享 bootstrap 设置）

## 正常业务行为

- 输入已存在姓名 → 返回该行 id 与 name；输入不存在 → 返回空结果。旧基线已由 D 验证；异常处理修订提交 `6b522ea` 待 D 回归。

## 目标漏洞点 / 修复方式（设计目标）

- `index.php:7`：输入来源 `$_GET['name']`；
- `index.php:10`：`$db->prepare('... WHERE name = ?')` 使用占位符；
- `index.php:11`：`$stmt->bind_param('s', $name)` 绑定参数；
- `index.php:12`：`$stmt->execute()` 执行；`:9-21` 以 `try/catch (Throwable)` 隔离异常回显。
- `name` 仅作为绑定值进入查询，不参与 SQL 语法结构。

## 输出约定

- 展示时使用 `htmlspecialchars(..., ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')`，避免额外反射型 XSS。

## 依赖文件

- `../common/db_connect.php`：提供严格模式 mysqli `$db`（utf8mb4），连接异常仅写日志，无真实密码。

## 浏览器动作与重置

- 非存储型样本：直接访问 URL；每次测试从干净 URL 开始，无存储态需清理。

## 参考验证

- D 已对旧基线完成普通业务与注入输入回归；提交 `6b522ea` 已通过本机 `php -l`，待 D 在容器内重验源码哈希、正常请求和异常不回显。
