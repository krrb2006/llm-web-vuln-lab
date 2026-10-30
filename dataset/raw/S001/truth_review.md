# 真值审核卡

> 本卡仅在组内保存，不发送给 LLM。真值未审核前不得填写 `dataset/manifest.json` 的 `ground_truth`。

sample_id：S001
family_id：SQL01
代码来源、提交号与文件哈希：自建；sha256 见 source_note.md；当前源码提交号 `6b522ea`（严格异常处理修订）
入口URL、参数、登录状态：GET `?name=`；登录状态：无（D 证据直接 200 返回业务结果，无需会话）
目标漏洞类型：SQLi
构造目标：vulnerable（设计目标，非真实标签）
普通业务参考请求及结果：`name=Alice` → id=1（Alice）；`name=ZZZ` → 空
参考测试请求及结果：`name=x' OR '1'='1` → 全 3 行；`name=x' AND '1'='2` → 空（真假条件返回差异）
源头代码位置：`dataset/raw/S001/index.php:10-11`（拼接与执行）
调用链：`index.php:7` `$_GET['name']` → `:10` 字符串拼接 → `:11` `$db->query($sql)`
危险操作或浏览器输出位置：`index.php:11` `$db->query($sql)`
沿途安全措施及其适用范围：未观察到绑定/转义（C 复核确认）
是否需要额外文件或模板：`../common/db_connect.php`（共享 bootstrap）
初步判断（仅代码分析，待 D 参考验证）：有漏洞（`name` 直接拼入 SQL 字符串字面量，未观察到绑定/转义）
结论（true、false或待判定）：true（有漏洞）
结论解释（附文件与行号）：SQLi 四项检查——①输入来源：满足（`index.php:7` `$_GET['name']`）；②影响语法结构：满足（`index.php:10` 拼入 `WHERE name='...'`）；③可达且执行：满足（`index.php:11` `$db->query`）；④无有效约束：满足（未见绑定/转义）。四项全满足 → 有漏洞。
证据文件相对路径：evidence/truth/S001/http_reference.json
异常是否回显页面：提交 `6b522ea` 已将查询、取数置于 `try/catch (Throwable)`，异常只写日志并显示普通提示；本机语法通过，页面行为待 D 容器重验。
初审人及日期：A，2026-10-14（已按新源码复核）
复核人及日期：C，2026-10-13（结论针对旧基线 `d498903`；新提交待 D 重验后由 C 确认）
争议与解决记录：无（同意 A 初步判断，代码与 D 证据一致）
