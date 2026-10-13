# 真值审核卡

> 本卡仅在组内保存，不发送给 LLM。真值未审核前不得填写 `dataset/manifest.json` 的 `ground_truth`。

sample_id：S004
family_id：SQL02
代码来源、提交号与文件哈希：自建；sha256 见 source_note.md；源码提交号 d498903（A 分支 origin/a/criteria-and-sql01）
入口URL、参数、登录状态：GET `?id=`；登录状态：无（D 证据直接 200 返回业务结果，无需会话）
目标漏洞类型：SQLi
构造目标：fixed（设计目标，非真实标签）

## 分析思路（A 撰写）

- 输入来源 `index.php:7`（`$_GET['id']`）为外部可控字符串。
- `index.php:9` 以 `ctype_digit` 严格校验，非数字直接拒绝，查询不执行。
- `index.php:14` 转整数后经 `prepare`（`:16`）+ `bind_param('i', ...)`（`:22`）作为绑定值进入。
- 判定依据仍按 `docs/judgment_criteria.md` 的 SQLi 四项检查逐条落地，结论只取「满足/不满足/未知」。

## 待验证步骤（A 撰写，C 复核结果见下）

1. 普通业务：`id=1` 返回 id=1 行，`id=999`（不存在）返回空。**D 证据已验**。
2. 非法输入：`id=abc` 被拦截，返回「非法的 ID 参数」，查询不执行。**D 证据以 `id=1 OR 1=1` 等非数字值验证，同为拦截路径**。
3. 受控异常输入：`id=1 OR 1=1` 等含空格/非数字值被拦截，返回「非法的 ID 参数」，不改变结果集。**D 证据已验**。
4. 防护覆盖范围：确认不存在其他把 `id` 重新拼入 SQL 的分支。**已复核，未见其他分支**。

普通业务参考请求及结果：`id=1` → id=1（Alice）；`id=999` → 空
参考测试请求及结果：`id=1 OR 1=1` → 「非法的 ID 参数。」；`id=1 AND 1=2` → 「非法的 ID 参数。」（查询前拒绝，未执行）
源头代码位置：`dataset/raw/S004/index.php:16/22`（prepare/bind_param）
调用链：`index.php:7` `$_GET['id']` → `:9` `ctype_digit` → `:14` `(int)` → `:16` `prepare` → `:22` `bind_param` → `:23` `execute`
危险操作或浏览器输出位置：`index.php:16/23`（查询以绑定值方式执行）
沿途安全措施及其适用范围：严格数字校验 + 绑定参数（C 复核确认覆盖危险点）
是否需要额外文件或模板：`../common/db_connect.php`（共享 bootstrap）
初步判断（仅代码分析，待 D 参考验证）：安全（`ctype_digit` 严格校验 + 参数绑定）
结论（true、false或待判定）：false（安全，不构成 SQLi）
结论解释（附文件与行号）：SQLi 四项检查——①输入来源：满足（`index.php:7` `$_GET['id']`）；②影响语法结构：不满足（`index.php:9` ctype_digit 拒绝非数字、`:16/:22` prepare + bind_param，`id` 仅作绑定值）；③可达且执行：满足（正常数字路径执行，非法路径 `:9-13` 提前 exit）；④无有效约束：满足（校验 + 绑定覆盖，未见其他拼接分支）。检查②不满足 → 不构成 SQLi（false）。特别核查：S004 确在查询前（`index.php:9`）拒绝非数字。
证据文件相对路径：evidence/truth/S004/http_reference.json
异常是否回显页面：否（D 证据 php_fatal_error_visible=false）；非法输入在 `index.php:9` 查询前被拒，不触发查询异常；但 `if($stmt===false)` 判错（`index.php:17`）仍是同一潜在隐患（纳入问题清单，不影响本样本 SQLi 结论）
初审人及日期：A，未进行
复核人及日期：C，2026-10-13
争议与解决记录：无（同意 A 初步判断，代码与 D 证据一致）
