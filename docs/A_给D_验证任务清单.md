# A 给 D：S001–S008 容器验证任务清单

> 用途：D 在本地 DVWA 容器内，对 A 构造的 8 个 SQLi 配对样本做参考验证，建立真实标签证据。
> 原则：语法检查通过 ≠ 验证通过；安全样本不能只凭一次测试失败下结论，需异常输入回归 + 代码路径确认。
> 证据单独标记 reference，存 `evidence/truth/S00X/`，不冒充被评估模型生成的 POC。

## 一、环境前提

- 统一外壳 + 共享连接：提供 `$db`（mysqli）+ utf8mb4 字符集 + `lab_people(id INT PRIMARY KEY, name VARCHAR(80) NOT NULL)` 表，初始化虚构数据（如 Alice/Bob/Carol）。
- 连接接口见 `dataset/raw/common/db_connect.php`（环境变量注入，源码无密码）；D 可用自己的实现替换，保持「$db + utf8mb4 + 表名」约定不变。
- 确认实际入口 URL（样本卡写的是 `/lab_cases/S00X/index.php`，以 D 实际挂载路径为准）与会话/登录要求。

## 二、容器内 PHP 语法检查

```bash
docker compose exec -T dvwa php -l /var/www/html/lab_cases/S001/index.php
# 依次 S001–S008 的 index.php；S007/S008 还要检查 repository.php
```

## 三、源码哈希两端核对（不一致则不得据本地行号解释现象）

```bash
sha256sum dataset/raw/S001/index.php
docker compose exec -T dvwa sha256sum /var/www/html/lab_cases/S001/index.php
# 逐例核对；S007/S008 另核对 repository.php
```

## 四、正常业务请求（先确认普通业务可用；vuln/fixed 应一致）

| 样本 | 参数 | 正常输入 | 预期 |
|---|---|---|---|
| S001/S002 | name | name=Alice | 返回 id=1 行 |
| S001/S002 | name | name=ZZZ | 空结果 |
| S003/S004 | id | id=1 | 返回 id=1 行 |
| S003/S004 | id | id=999 | 空结果 |
| S005/S006 | q | q=li | 返回含 "li" 的行 |
| S005/S006 | q | q=zz | 空结果 |
| S007/S008 | name | name=Alice | 返回 id=1 行 |
| S007/S008 | name | name=ZZZ | 空结果 |

## 五、受控异常输入（区分「通配符行为」与「注入」）

> 下表负载需 URL 编码（空格 `%20` 或 `+`，`#` 为 `%23`）。「预期」为设计推断，以实测为准。

| 样本 | 输入（示意） | 类型 | 应观察 |
|---|---|---|---|
| S001 | name=`x' OR '1'='1` | 注入·恒真 | 预期返回全部行 |
| S001 | name=`x' AND '1'='2` | 注入·恒假 | 预期返回空 |
| S002 | 同上两个输入 | 绑定字面值 | 预期仅当 name 含该字面串才匹配，通常空 |
| S003 | id=`1 OR 1=1` | 注入·恒真 | 预期返回全部行 |
| S003 | id=`1 AND 1=2` | 注入·恒假 | 预期返回空 |
| S004 | id=`1 OR 1=1` | 被校验拦截 | 预期「非法的 ID 参数」，查询不执行 |
| S005 | q=`x' OR 1=1 #` | 注入·恒真 | 预期返回全部行 |
| S005 | q=`x' AND 1=2 #` | 注入·恒假 | 预期返回空 |
| S005/S006 | q=`%`、q=`_` | LIKE 通配符 | 改变匹配范围（**非注入**，两例应一致） |
| S006 | q=`x' OR 1=1 #` | 绑定字面值 | 预期返回空 |
| S007 | name=`x' OR '1'='1` | 注入·恒真 | 预期返回全部行 |
| S007 | name=`x' AND '1'='2` | 注入·恒假 | 预期返回空 |
| S008 | 同上两个输入 | 绑定字面值 | 预期返回空 |

## 六、记录与回填

- 保存普通/异常请求、响应与数据库现象、关键源码截图、两端哈希。
- 把 `truth_review.md` 中「未验证」替换为实测结果，并回填「普通业务参考请求及结果」「参考测试请求及结果」。
- 参考验证单独标记 reference，存 `evidence/truth/S00X/`。

## 七、提醒

- 语法检查通过 ≠ HTTP/数据库/注入验证通过。
- SQLi 只观察教学数据（lab_people）的条件变化；输出已做 HTML 编码，避免混入 XSS 干扰标签。
