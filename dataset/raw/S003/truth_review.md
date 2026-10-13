# 真值审核卡

> 本卡仅在组内保存，不发送给 LLM。真值未审核前不得填写 `dataset/manifest.json` 的 `ground_truth`。

sample_id：S003
family_id：SQL02
代码来源、提交号与文件哈希：自建；sha256 见 source_note.md；源码提交号 d498903（A 分支 origin/a/criteria-and-sql01）
入口URL、参数、登录状态：GET `?id=`；登录状态：无（D 证据直接 200 返回业务结果，无需会话）
目标漏洞类型：SQLi
构造目标：vulnerable（设计目标，非真实标签）

## 分析思路（A 撰写）

- 输入来源 `index.php:7`（`$_GET['id']`）为外部可控字符串。
- `index.php:9` 将其直接拼入 SQL 的数值位置；因数值位置不带引号，字符串可影响语法结构。
- `index.php:10` 执行该语句；未观察到数字校验或绑定。
- 判定依据仍按 `docs/judgment_criteria.md` 的 SQLi 四项检查逐条落地，结论只取「满足/不满足/未知」。

## 待验证步骤（A 撰写，C 复核结果见下）

1. 普通业务：`id=1` 返回 id=1 行，`id=999`（不存在）返回空。**D 证据已验**。
2. 非法输入：`id=abc` 触发 SQL 错误（进错误日志），页面提示「查询失败」。**D 证据未覆盖此输入**。
3. 受控真假条件：`id=1 OR 1=1`（恒真，预期多行）与 `id=1 AND 1=2`（恒假，预期空行）的
   返回差异，作为语法结构可控的证据。**D 证据已验**。

普通业务参考请求及结果：`id=1` → id=1（Alice）；`id=999` → 空
参考测试请求及结果：`id=1 OR 1=1` → 全 3 行；`id=1 AND 1=2` → 空（真假条件返回差异）
源头代码位置：`dataset/raw/S003/index.php:9-10`
调用链：`index.php:7` `$_GET['id']` → `:9` 字符串拼接 → `:10` `$db->query($sql)`
危险操作或浏览器输出位置：`index.php:10` `$db->query($sql)`
沿途安全措施及其适用范围：未观察到数字校验/绑定（C 复核确认）
是否需要额外文件或模板：`../common/db_connect.php`（共享 bootstrap）
初步判断（仅代码分析，待 D 参考验证）：有漏洞（`id` 直接拼入数值位置，未观察到数字校验/绑定）
结论（true、false或待判定）：true（有漏洞）
结论解释（附文件与行号）：SQLi 四项检查——①输入来源：满足（`index.php:7` `$_GET['id']`）；②影响语法结构：满足（`index.php:9` 拼入数值位置 `WHERE id = $id`）；③可达且执行：满足（`index.php:10` `$db->query`）；④无有效约束：满足（未见数字校验/绑定）。四项全满足 → 有漏洞。
证据文件相对路径：evidence/truth/S003/http_reference.json
异常是否回显页面：否（D 证据 php_fatal_error_visible=false）；代码为 `if($result===false)` 判错（`index.php:11`），PHP 8.1+ 默认异常模式接不住；注意 D 证据未覆盖 `id=abc` 这类会触发语法错误的输入，卡片所写「页面提示查询失败」在异常模式下实为 Fatal 回显（潜在隐患，纳入问题清单，不影响本样本 SQLi 结论）
初审人及日期：A，未进行
复核人及日期：C，2026-10-13
争议与解决记录：无（同意 A 初步判断，代码与 D 证据一致）
