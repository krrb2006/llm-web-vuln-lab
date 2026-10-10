# 真值审核卡（空白，待填写）

> 本卡仅在组内保存，不发送给 LLM。真值未审核前不得填写 `dataset/manifest.json` 的 `ground_truth`。

sample_id：S008
family_id：SQL04
代码来源、提交号与文件哈希：自建；sha256 见 source_note.md；提交号待首次提交后补
入口URL、参数、登录状态：GET `?name=`；登录状态待 D 确认；**未验证**
目标漏洞类型：SQLi
构造目标：fixed（设计目标，非真实标签）

## 分析思路（待验证，非结论）

- 输入来源在入口 `index.php:8`（`$_GET['name']`），查询在 `repository.php:7/11-12`，
  中间跨一层函数调用 `find_people_by_name()`（`index.php:10`）。
- `repository.php:7` 用 `prepare` + 占位符，`:11` `bind_param('s', $name)` 绑定，
  `name` 无法改写语法结构。
- 判定依据仍按 `docs/judgment_criteria.md` 的 SQLi 四项检查逐条落地，结论只取「满足/不满足/未知」。

## 待验证步骤

1. 普通业务：`name=Alice` 返回 id=1 行，`name=ZZZ` 返回空。**未验证**。
2. 受控真假条件（引号闭合 + 布尔恒真/恒假）：应被作为字面值绑定，不改变结果集逻辑（预期空）。**未验证**。
3. 防护覆盖范围：确认 repository 层不存在其他把 `name` 重新拼入 SQL 的分支。**未验证**。

普通业务参考请求及结果：**未验证**
参考测试请求及结果：**未验证**
源头代码位置：`dataset/raw/S008/repository.php:7/11`（prepare/bind_param）
调用链：`index.php:8` `$_GET['name']` → `index.php:10` `find_people_by_name()` → `repository.php:6` 函数 → `:7` prepare → `:11` bind_param → `:12` execute
危险操作或浏览器输出位置：`repository.php:7/12`（查询以绑定值方式执行）
沿途安全措施及其适用范围：预处理 + 绑定参数（**待人工复核确认覆盖范围**）
是否需要额外文件或模板：`../common/db_connect.php`、`repository.php`
初步判断（仅代码分析，待 D 参考验证）：安全（repository 层 `prepare` + `bind_param` 绑定）
结论（true、false或待判定）：**待判定（未验证）**
结论解释（附文件与行号）：**未验证**
证据文件相对路径：（无）
初审人及日期：A，未进行
复核人及日期：（C 复核，未进行）
争议与解决记录：（无）
