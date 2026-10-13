# C 给 A：S001–S008 真值复核结论与问题清单

> 复核人：C；复核日期：2026-10-13。
> 复核方式：只读分析（未改动任何 PHP / 未改动 manifest.json）+ 对照 D 参考验证证据
> （`evidence/truth/S001–S008/http_reference.json`）。依据 `docs/judgment_criteria.md` 的 SQLi 四项检查。
> 本表结论为 C 的复核意见，`ground_truth` 仍由 A 写入 `dataset/manifest.json`。

## 一、复核结论总表（8 例）

| 样本 | family | 构造目标 | ①输入来源 | ②影响语法结构 | ③可达执行 | ④无有效约束 | 结论 | 异常是否回显页面 |
|---|---|---|---|---|---|---|---|---|
| S001 | SQL01 | vulnerable | 满足 | 满足 | 满足 | 满足 | **true（有漏洞）** | 否（`===false` 判错，潜在隐患） |
| S002 | SQL01 | fixed | 满足 | 不满足 | 满足 | 满足 | **false（安全）** | 否（`===false` 判错，潜在隐患） |
| S003 | SQL02 | vulnerable | 满足 | 满足 | 满足 | 满足 | **true（有漏洞）** | 否（`===false` 判错；`id=abc` 未被证据覆盖） |
| S004 | SQL02 | fixed | 满足 | 不满足 | 满足 | 满足 | **false（安全）** | 否（非法输入在查询前被拒） |
| S005 | SQL03 | vulnerable | 满足 | 满足 | 满足 | 满足 | **true（有漏洞）** | 否（`===false` 判错，潜在隐患） |
| S006 | SQL03 | fixed | 满足 | 不满足 | 满足 | 满足 | **false（安全）** | 否（`===false` 判错，潜在隐患） |
| S007 | SQL04 | vulnerable | 满足 | 满足 | 满足 | 满足 | **true（有漏洞）** | 否（`===false` 判错，潜在隐患） |
| S008 | SQL04 | fixed | 满足 | 不满足 | 满足 | 满足 | **false（安全）** | 否（`===false` 判错，潜在隐患） |

要点：
- 8 例结论与 A 的「初步判断」**全部一致**，无争议，均同意。
- 每个 family 的 vuln/fixed 两例：入口/参数、返回字段（id、name）、输出编码
  （`htmlspecialchars(..., ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')`）一致，唯一差异为目标缺陷
  （字符串/数值/LIKE 拼接 vs 校验 + 绑定；SQL04 差异位于 repository 层）。
- 特别核查均通过：S004 在查询前（`index.php:9`）以 `ctype_digit` 拒绝非数字；S005/S006 的
  `%`/`_` 通配符返回全表属 LIKE 行为、非注入证据；S007/S008 已追踪到 `repository.php`。

## 二、给 A 的问题清单（不影响 ground_truth 结论，供后续处理）

### 问题 1（全局，重要）：共享 bootstrap 的 mysqli 异常回显隐患（S001–S012 共有）
- 现象：S001–S008 的 `index.php`/`repository.php` 均使用 `if($result === false)` /
  `if($stmt === false)`（或 `return false`）判错，无 try/catch。`common/db_connect.php` 未显式设置
  `mysqli_report`，在 PHP 8.1+ 默认 `MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT` 下，查询/prepare 失败
  抛 `mysqli_sql_exception`，`===false` 接不住 → 未捕获即 Fatal error 回显页面（与 S009 已复现现象同类）。
- D 当前证据（S001–S008）全部 `php_fatal_error_visible=false`，是因为受控输入均为语法合法
  （如 `x' OR '1'='1`）或查询前被拒（S004），**未触发**语法错误路径，故未观察到回显。
- 建议：由 A/D 在共享 `common/db_connect.php` 统一 `mysqli_report` 策略（二选一：显式 OFF 让
  `===false` 生效，或保持异常模式并统一 try/catch），不要各样本自改。C 名下 S009/S010 已示范
  自包含 try/catch（见 `docs/C_给AD_bootstrap异常处理问题.md`）。
- 定位：本问题不改变上述任何一条 ground_truth 结论（SQLi 判定只看四项检查）。

### 问题 2（证据补强）：D 参考验证未覆盖「会触发 SQL 语法错误」的输入
- 具体：S003 卡片写 `id=abc` → 「页面提示查询失败」，但 D 证据未实测 `id=abc`；在异常模式下该输入
  实为 Fatal 回显而非「查询失败」。同理 S001/S005/S007 的裸单引号等语法错误输入未覆盖。
- 建议：D 对各漏洞版补一个语法错误触发输入（如 `id=abc`、`name=x'`），作为问题 1 的回显对照，
  与 `http_reference.json` 的 `php_fatal_error_visible` 字段一起入库。

### 问题 3（卡片同步）：S003 sample_card 观察点表述与异常模式不一致
- `id=abc` 的「SQL 语法错误写入错误日志，页面提示查询失败」在 PHP 8.1+ 异常模式下不成立
  （错误不进 error_log、页面显示 Fatal）。属问题 1 的派生表述，待 bootstrap 口径确定后由 A 统一更正卡片。

### 问题 4（流程）：A 初审状态未标记
- 8 例 `truth_review.md` 的「初审人及日期」均为「A，未进行」。按 `docs/A_给C_真值复核清单.md`，
  C 复核前提是 A 已完成初审；请 A 补填初审状态。

### 问题 5（轻微）：登录状态与卡片不同步
- sample_card 写「登录状态待 D 确认」，D 证据已直接 200 返回业务结果（无需会话）。C 已在
  `truth_review.md` 记为「无登录」，请 A 同步 sample_card。

## 三、C 复核范围与限制

- 只读分析：未改动 `dataset/raw/S001–S008` 的任何 PHP、未改动 `dataset/manifest.json`。
- 仅签署 `truth_review.md`（复核人及日期 = C）；`ground_truth` 由 A 写入 manifest。
- 证据路径：`evidence/truth/S00X/http_reference.json`（来自 D 分支 origin/d/environment-reference，
  仅本地使用，未提交）。

## 四、待 A 后续动作

1. 依据本表在 `dataset/manifest.json` 写入 8 例 `ground_truth`（true/false，见上表）、
   `truth_reviewer = C`、`truth_evidence`，`status` 改 `ready`。
2. 处理问题 1（bootstrap 全局口径，与 D 商定）与问题 2/3/4/5（卡片同步、初审标记）。
