# S004 样本卡

- sample_id：S004
- family_id：SQL02（数字 ID 查询，开发集）
- 构造目标：fixed（**仅设计目标，非真实标签**，真值待双人审核）
- 目标漏洞类型：SQLi

## 入口与运行前提

- 入口 URL：`GET /lab_cases/S004/index.php?id=<数字>`（实际路径待 D 统一外壳确认）
- HTTP 方法：GET
- 参数：`id`（待查询数字 ID）
- 登录状态：无（待 D 确认外壳是否强制会话）
- 数据库表：`lab_people(id INT PRIMARY KEY, name VARCHAR(80) NOT NULL)`，数据由 D 初始化
- 连接字符集：utf8mb4（由共享 bootstrap 设置）

## 正常业务行为

- 输入存在的 id → 返回该行 id 与 name；不存在的 id → 空结果。**未验证**。

## 目标漏洞点 / 修复方式（设计目标）

- `index.php:7`：输入来源 `$_GET['id']`；
- `index.php:9`：`ctype_digit` 严格校验（仅接受十进制数字串，否则拒绝）；
- `index.php:14`：`(int)` 转换后；
- `index.php:16`：`$db->prepare('... WHERE id = ?')` 使用占位符；
- `index.php:22-23`：`bind_param('i', $id)` + `execute`。
- `id` 仅作为绑定值进入查询，不参与 SQL 语法结构。

## 观察点（预期现象 vs 实际观察）

| 输入 | 预期现象（设计推断） | 实际观察 |
|---|---|---|
| 正常 ID `id=1` | 返回 id=1 行（name=Alice） | **未验证** |
| 非法 ID `id=abc` | 被 `ctype_digit` 拦截，返回「非法的 ID 参数」，不执行查询 | **未验证** |
| 受控异常 `id=1 OR 1=1`（URL 编码） | 含空格/非数字，被拦截，返回「非法的 ID 参数」 | **未验证** |
| 受控异常 `id=1 AND 1=2`（URL 编码） | 同上，被拦截 | **未验证** |

> 预期现象仅为设计推断；安全标签不能只凭一次 POC 失败，还需结合代码路径与异常输入回归
> （见 `docs/judgment_criteria.md`）。真值由 D 的参考验证实测后确认。

## 输出约定

- 展示时使用 `htmlspecialchars(..., ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')`，避免额外反射型 XSS。

## 依赖文件

- `../common/db_connect.php`：提供 `$db`（mysqli，utf8mb4），无真实密码，待 D 集成统一外壳。

## 浏览器动作与重置

- 反射型样本：直接访问 URL；每次测试从干净 URL 开始，无存储态需清理。**未验证**。

## 参考验证

- **未验证**：普通业务必须正常（不能通过破坏功能制造「安全」），异常输入回归未在本机执行
  （本机 Docker/PHP 未安装）。
