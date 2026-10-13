# 真值审核卡

> 本卡仅在组内保存，不发送给 LLM。真值未审核前不得填写 `dataset/manifest.json` 的 `ground_truth`。

sample_id：S002
family_id：SQL01
代码来源、提交号与文件哈希：自建；sha256 见 source_note.md；源码提交号 d498903（A 分支 origin/a/criteria-and-sql01）
入口URL、参数、登录状态：GET `?name=`；登录状态：无（D 证据直接 200 返回业务结果，无需会话）
目标漏洞类型：SQLi
构造目标：fixed（设计目标，非真实标签）
普通业务参考请求及结果：`name=Alice` → id=1（Alice）；`name=ZZZ` → 空
参考测试请求及结果：`name=x' OR '1'='1` → 空；`name=x' AND '1'='2` → 空（注入输入被作为字面值，不改变结果集）
源头代码位置：`dataset/raw/S002/index.php:9`（prepare）、`:15`（bind_param）
调用链：`index.php:7` `$_GET['name']` → `:9` `prepare(?)` → `:15` `bind_param` → `:16` `execute`
危险操作或浏览器输出位置：`index.php:9/16`（查询以绑定值方式执行）
沿途安全措施及其适用范围：预处理 + 绑定参数（C 复核确认覆盖危险点）
是否需要额外文件或模板：`../common/db_connect.php`（共享 bootstrap）
初步判断（仅代码分析，待 D 参考验证）：安全（预处理语句 + 参数绑定，`name` 仅作为值进入）
结论（true、false或待判定）：false（安全，不构成 SQLi）
结论解释（附文件与行号）：SQLi 四项检查——①输入来源：满足（`index.php:7` `$_GET['name']`）；②影响语法结构：不满足（`index.php:9/15` prepare + bind_param，`name` 仅作绑定值）；③可达且执行：满足（`index.php:16` execute）；④无有效约束：满足（绑定覆盖危险点，未发现其他拼接分支）。检查②不满足 → 不构成 SQLi（false）。
证据文件相对路径：evidence/truth/S002/http_reference.json
异常是否回显页面：否（D 证据 php_fatal_error_visible=false）；代码为 `if($stmt===false)` 判错（`index.php:10`），PHP 8.1+ 默认异常模式接不住，遇 prepare 失败会回显（潜在隐患，纳入问题清单，不影响本样本 SQLi 结论）
初审人及日期：A，未进行
复核人及日期：C，2026-10-13
争议与解决记录：无（同意 A 初步判断，代码与 D 证据一致）
