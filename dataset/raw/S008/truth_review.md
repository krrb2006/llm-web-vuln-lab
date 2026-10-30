# 真值审核卡

> 本卡仅在组内保存，不发送给 LLM。真值未审核前不得填写 `dataset/manifest.json` 的 `ground_truth`。

sample_id：S008
family_id：SQL04
代码来源、提交号与文件哈希：自建；sha256 见 source_note.md；当前源码提交号 `6b522ea`（严格异常处理修订）
入口URL、参数、登录状态：GET `?name=`；登录状态：无（D 证据直接 200 返回业务结果，无需会话）
目标漏洞类型：SQLi
构造目标：fixed（设计目标，非真实标签）

## 分析思路（A 撰写）

- 输入来源在入口 `index.php:8`（`$_GET['name']`），查询在 `repository.php:7-10`，
  中间跨一层函数调用 `find_people_by_name()`（`index.php:11`）。
- `repository.php:7` 用 `prepare` + 占位符，`:8` `bind_param('s', $name)` 绑定，
  `name` 无法改写语法结构。
- 判定依据仍按 `docs/judgment_criteria.md` 的 SQLi 四项检查逐条落地，结论只取「满足/不满足/未知」。

## 待验证步骤（A 撰写，C 复核结果见下）

1. 普通业务：`name=Alice` 返回 id=1 行，`name=ZZZ` 返回空。**D 证据已验**。
2. 受控真假条件（引号闭合 + 布尔恒真/恒假）：应被作为字面值绑定，不改变结果集逻辑（预期空）。**D 证据已验**。
3. 防护覆盖范围：确认 repository 层不存在其他把 `name` 重新拼入 SQL 的分支。**已复核，未见其他分支**。

普通业务参考请求及结果：`name=Alice` → id=1（Alice）；`name=ZZZ` → 空
参考测试请求及结果：`name=x' OR '1'='1` → 空；`name=x' AND '1'='2` → 空（注入输入被作为字面值绑定，不改变结果集）
源头代码位置：`dataset/raw/S008/repository.php:7/8`（prepare/bind_param）
调用链：`index.php:8` `$_GET['name']` → `index.php:11` `find_people_by_name()` → `repository.php:6` 函数 → `:7` prepare → `:8` bind_param → `:9` execute
危险操作或浏览器输出位置：`repository.php:7/9`（查询以绑定值方式执行）
沿途安全措施及其适用范围：预处理 + 绑定参数（C 复核确认覆盖危险点）
是否需要额外文件或模板：`../common/db_connect.php`、`repository.php`
初步判断（仅代码分析，待 D 参考验证）：安全（repository 层 `prepare` + `bind_param` 绑定）
结论（true、false或待判定）：false（安全，不构成 SQLi）
结论解释（附文件与行号）：SQLi 四项检查——①输入来源：满足（`index.php:8` `$_GET['name']`）；②影响语法结构：不满足（`repository.php:7/8` prepare + bind_param，`name` 仅作绑定值）；③可达且执行：满足（`index.php:11` 调用 → `repository.php:9` execute，跨函数可达）；④无有效约束：不满足（绑定覆盖，未见其他拼接分支）。检查②、④不满足 → 不构成 SQLi（false）。已追踪到 repository.php。
证据文件相对路径：evidence/truth/S008/http_reference.json
异常是否回显页面：提交 `6b522ea` 在入口 `index.php:10-18` 捕获 repository 的 prepare/bind/execute/get_result 及取数异常，异常只写日志并显示普通提示；待 D 容器回归。
初审人及日期：A，2026-10-14（已按新源码复核）
复核人及日期：C，2026-10-13（结论针对旧基线 `d498903`；第④项由 A 整合时按判定标准纠正，新提交待 C 确认）
争议与解决记录：无（同意 A 初步判断，代码与 D 证据一致；已追踪到 repository.php）
