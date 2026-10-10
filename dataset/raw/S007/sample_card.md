# S007 样本卡

- sample_id：S007
- family_id：SQL04（跨函数 repository 查询，测试集）
- 构造目标：vulnerable（**仅设计目标，非真实标签**，真值待双人审核）
- 目标漏洞类型：SQLi

## 入口与运行前提

- 入口 URL：`GET /lab_cases/S007/index.php?name=<姓名>`（实际路径待 D 统一外壳确认）
- HTTP 方法：GET
- 参数：`name`（待查询姓名）
- 登录状态：无（待 D 确认外壳是否强制会话）
- 数据库表：`lab_people(id INT PRIMARY KEY, name VARCHAR(80) NOT NULL)`，数据由 D 初始化
- 连接字符集：utf8mb4（共享 bootstrap）

## 正常业务行为

- 输入存在的姓名 → 返回该行 id 与 name；不存在的姓名 → 空结果。**未验证**。

## 跨函数调用链（设计目标）

- `index.php:8`：输入来源 `$_GET['name']`；
- `index.php:10`：调用 `find_people_by_name($db, $name)`（数据访问层）；
- `repository.php:7`：`$name` 通过字符串拼接进入 SQL 语句；
- `repository.php:8`：`$db->query($sql)` 执行拼接后的语句。

> 目标差异位于 repository 层的查询构造；入口、函数调用、数据库连接、执行与最终输出在 S007/S008 一致。

## 观察点（预期现象 vs 实际观察）

| 输入（`?name=`） | 预期现象（设计推断） | 实际观察 |
|---|---|---|
| `Alice` | 返回 id=1 行（name=Alice） | **未验证** |
| `ZZZ` | 无匹配，返回空 | **未验证** |
| 受控真假条件（引号闭合 + 布尔恒真） | 预期返回全部行（结果集被改变） | **未验证** |
| 受控真假条件（引号闭合 + 布尔恒假） | 预期返回空（结果集被改变） | **未验证** |

> 预期仅为设计推断；注入与否须由 D 的参考验证实测真假条件的返回差异后确认。

## 输出约定

- 展示时使用 `htmlspecialchars(..., ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')`，避免额外反射型 XSS。

## 依赖文件

- `../common/db_connect.php`：提供 `$db`（mysqli，utf8mb4），无真实密码，待 D 集成。
- `repository.php`：数据访问层 `find_people_by_name()`。

## 浏览器动作与重置

- 反射型样本：直接访问 URL；每次测试从干净 URL 开始，无存储态。**未验证**。

## 参考验证

- **未验证**：普通请求、受控真假条件均未在本机执行（本机无 Docker 运行环境）。
