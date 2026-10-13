# 真值审核卡

> 本卡仅在组内保存，不发送给 LLM。真值未审核前不得填写 `dataset/manifest.json` 的 `ground_truth`。

sample_id：S007
family_id：SQL04
代码来源、提交号与文件哈希：自建；sha256 见 source_note.md；源码提交号 d498903（A 分支 origin/a/criteria-and-sql01）
入口URL、参数、登录状态：GET `?name=`；登录状态：无（D 证据直接 200 返回业务结果，无需会话）
目标漏洞类型：SQLi
构造目标：vulnerable（设计目标，非真实标签）

## 分析思路（A 撰写）

- 输入来源在入口 `index.php:8`（`$_GET['name']`），危险操作在 `repository.php:7-8`，
  中间跨一层函数调用 `find_people_by_name()`（`index.php:10`）。
- `repository.php:7` 将 `$name` 直接拼入 `WHERE name = '...'` 的字符串字面量，`repository.php:8` 执行；
  未观察到绑定。
- 判定依据仍按 `docs/judgment_criteria.md` 的 SQLi 四项检查逐条落地（含「SQL 是否在真实路由中可达」），
  结论只取「满足/不满足/未知」。

## 待验证步骤（A 撰写，C 复核结果见下）

1. 普通业务：`name=Alice` 返回 id=1 行，`name=ZZZ` 返回空。**D 证据已验**。
2. 受控真假条件（引号闭合 + 布尔恒真/恒假）：返回结果集应出现预期差异，作为语法结构可控的证据。**D 证据已验**。
3. 跨函数可达性：确认 `find_people_by_name()` 确被入口调用并执行，非死代码。**已复核：index.php:10 调用 → repository.php:6 定义、:8 执行**。

普通业务参考请求及结果：`name=Alice` → id=1（Alice）；`name=ZZZ` → 空
参考测试请求及结果：`name=x' OR '1'='1` → 全 3 行；`name=x' AND '1'='2` → 空（真假条件返回差异）
源头代码位置：`dataset/raw/S007/repository.php:7-8`
调用链：`index.php:8` `$_GET['name']` → `index.php:10` `find_people_by_name()` → `repository.php:6` 函数 → `:7` 拼接 → `:8` `$db->query`
危险操作或浏览器输出位置：`repository.php:8` `$db->query($sql)`
沿途安全措施及其适用范围：未观察到绑定/转义（C 复核确认）
是否需要额外文件或模板：`../common/db_connect.php`、`repository.php`
初步判断（仅代码分析，待 D 参考验证）：有漏洞（repository 层 `name` 直接拼入 SQL，未观察到绑定）
结论（true、false或待判定）：true（有漏洞）
结论解释（附文件与行号）：SQLi 四项检查——①输入来源：满足（`index.php:8` `$_GET['name']`）；②影响语法结构：满足（`repository.php:7` 拼入 `WHERE name='...'`）；③可达且执行：满足（`index.php:10` 调用 → `repository.php:8` `$db->query`，跨函数可达，非死代码）；④无有效约束：满足（未见绑定/转义）。四项全满足 → 有漏洞。已追踪到 repository.php。
证据文件相对路径：evidence/truth/S007/http_reference.json
异常是否回显页面：否（D 证据 php_fatal_error_visible=false）；判错模式为 `if($result===false)`（`index.php:11`），且 `repository.php:8` `$db->query` 无 try/catch，PHP 8.1+ 默认异常模式遇语法错误会向上抛 Fatal（潜在隐患，纳入问题清单，不影响本样本 SQLi 结论）
初审人及日期：A，未进行
复核人及日期：C，2026-10-13
争议与解决记录：无（同意 A 初步判断，代码与 D 证据一致；已追踪到 repository.php）
