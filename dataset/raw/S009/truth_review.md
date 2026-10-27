# 真值审核卡

> 本卡仅在组内保存，不发送给 LLM。真值未审核前不得填写 `dataset/manifest.json` 的 `ground_truth`。

sample_id：S009
family_id：SQL05
代码来源、提交号与文件哈希：自建（lab_people 数据与 mysqli 连接约定取自 D 手册）；源码提交号 7e50925（c/samples，try/catch 修复）；case_code_sha256 = 2b5e2f2506eef63fb39a2f5e00cdedfcaa3453a05c294f1b03b3d8af08deb0f2
入口URL、参数、登录状态：GET `?ids=`（逗号分隔 ID 列表）；登录状态：无（D 证据直接 200 返回业务结果，无需会话）
目标漏洞类型：SQLi
构造目标：vulnerable（设计目标，非真实标签）
普通业务参考请求及结果：`ids=1,2` → id=1 Alice、id=2 Bob 两条；`ids=3` → id=3 Carol 一条
参考测试请求及结果：
  - `ids=1 OR 1=1` → 仅 id=1（Alice）一条（`IN (1 OR 1=1)` 求值为 `IN (1)`，非全表）
  - `ids=1) OR 1=1 #` → 全部 3 条（闭合右括号并以 `#` 注释尾随，WHERE 语义被改写）
  - `ids=1) OR 1=1 -- `（尾随空格）→ 空结果（语法错误，现被 try/catch 捕获，不得记作成功）
源头代码位置：`dataset/raw/S009/index.php:8`（入口取值）、`:13`（危险拼接）、`:15`（执行）
调用链：`index.php:8` `$_GET['ids']` → `:13` 字符串拼入 `IN ($idsRaw)` → `:15` `$db->query($sql)`
危险操作或浏览器输出位置：`index.php:13` `IN ($idsRaw)` 直接拼接；`:15` `$db->query($sql)`
沿途安全措施及其适用范围：无任何校验/绑定/转义（`trim()` 不构成 SQL 防护）
是否需要额外文件或模板：共享 `bootstrap.php`（提供 `$db`）
结论（true、false或待判定）：true（有漏洞）
置信度：高
结论解释（附文件与行号）：SQLi 四项检查——①输入来源：满足（`index.php:8` `$_GET['ids']`）；②影响语法结构：满足（`index.php:13` `IN ($idsRaw)` 拼入语句结构）；③可达且执行：满足（`index.php:15` `$db->query`）；④无有效约束：满足（未见绑定/白名单/转义）。四项全满足 → 有漏洞。
证据文件相对路径：evidence/truth/S009/http_reference.json（D 于 origin/d/environment-reference）
异常是否回显页面：否（try/catch 捕获，D 证据 php_fatal_error_visible=false）
初审人及日期：C，2026-10-15
复核人及日期：A，2026-10-17；已核对证据提交 `8da63f7` 与当前 `index.php` 字节一致。
争议与解决记录：无。语法错误尝试真值记录：`ids=1) OR 1=1 -- `（尾随空格）经 `trim()` 去尾随空格后 `--` 失效引发语法错误；try/catch 修复后页面显示“未找到匹配记录”（空结果），不回显 Fatal error，且不得把 HTTP 200 当作注入成功。
