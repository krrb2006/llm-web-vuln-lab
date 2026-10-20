# D 预审：ADV_SECOND_SQLI / ADV_IDOR 目前不能直接运行（2026-10-20）

预审人：D（advanced_case 的 reviewer）
对象：`experiments/advanced_cases/SECOND_SQLI_01`、`IDOR_01`，对应 bonus plan 的 4 条 `ADV_*`（operator=A，reviewer=D）
基线：`a/criteria-and-sql01@3c5adda`

## 一、结论

4 条 advanced case 目前 **不具备“复制到靶场就能跑”的条件**。不是模型或 POC 的问题，是运行环境/代码接线问题。建议先不要把这 4 条标成 `executed`，否则会产生无法复现的记录。

## 二、具体阻塞项

### 1. 数据库变量名不一致（全部 6 个 PHP 文件）

`dataset/raw/common/db_connect.php` 只建立：

```php
$db = new mysqli(...);
```

而 advanced cases 全部使用 `$conn`：

- `SECOND_SQLI_01/vulnerable/save_profile.php`、`lookup_profile.php`
- `SECOND_SQLI_01/fixed/save_profile.php`、`lookup_profile.php`
- `IDOR_01/vulnerable/invoice.php`、`fixed/invoice.php`

在当前环境直接访问会因 `$conn` 未定义而 fatal（即使 catch 也只有 `$db` 的连接错误处理）。

### 2. 缺少 `profiles` / `invoices` 表与种子数据

`environment/init_lab_db.py` 目前只创建：

- `lab_people`
- `lab_guestbook`
- `lab_preview_drafts`

没有 `profiles`、`invoices`，也没有用户 A/B 与发票种子数据。advanced cases 即使连上数据库也查不到业务记录；IDOR 的“越权读取 B 的发票”无法构造。

### 3. advanced cases 没有被挂载进 DVWA

`environment/build_lab_cases.py` 只组装 S001–S024 到 `local/lab_cases`，没有 advanced 目录；`local/lab_cases` 只读挂载到容器 `/var/www/html/lab_cases`。因此：

- `http://127.0.0.1:4280/experiments/advanced_cases/...` 不存在；
- 直接 `require __DIR__ . '/../../../../dataset/raw/common/db_connect.php'` 在容器内也找不到对应文件。

需要单独的 `build_advanced_cases.py`（或扩展 build 脚本）把它们复制到 `local/lab_cases/advanced/`，并修正 require 路径。

### 4. IDOR 没有会话/用户初始化

`IDOR_01/fixed/invoice.php` 依赖 `$_SESSION['user_id']`，但仓库没有登录流程或 session 初始化脚本。当前：

- `user_id` 默认 0，修复版会返回空；
- 漏洞版不校验 `owner_id`，任何 `id` 都能读出 `owner_id` 和 `total`，但无法证明“A 读到了 B 的发票”，因为 A/B 用户与发票不存在。

需要：用户 A/B、各自发票、设置 `$_SESSION['user_id']=A` 的测试入口（或 test harness），以及越权前后对照。

### 5. SECOND_SQLI 的二次注入链缺少正常回归数据

- 写入阶段 `save_profile.php` 用 prepared statement，本身安全；
- 读取阶段 `lookup_profile.php` 把已存 `nickname` 拼进 SQL，构成二次注入；
- 但没有 `profiles` 表、没有“正常昵称”和“恶意昵称”的成对种子，无法展示“写入安全、二次读取不安全”的跨请求数据流。

## 三、建议的修复顺序（由 A/D 确认是否纳入本轮）

1. D 增加 `environment/init_advanced_db.py`：创建 `profiles`、`invoices`，写入用户 A/B、各自发票、正常/恶意昵称；提供按 case 重置。
2. D 增加 `environment/build_advanced_cases.py`：复制 6 个 PHP 到 `local/lab_cases/advanced/`，把 `$conn` 统一改为 `$db`（或在该目录的 bootstrap 里提供 `$conn = $db` 别名），修正 require 路径。
3. A 为 IDOR 补 session 初始化/测试入口，明确 A/B 用户与发票 id。
4. D 跑通 `vulnerable` 与 `fixed` 的正常业务回归，再交给 A 做模型记录；A 的 4 条仍为 `planned`，D 复核后再改 `executed/reviewed`。

## 四、边界

- 本记录只是预审，不改 `experiments/advanced_cases` 代码、不改 `runs/formal.json`、不改 bonus plan 状态。
- 如果本轮时间不够，建议把 4 条 ADV 明确标为“未完成/不计分”，不要用占位记录充数；主实验 36 条不受影响。

## 五、签字

D（linan / linan-prog，2986713478@qq.com）　2026-10-20 21:30（UTC+8）
