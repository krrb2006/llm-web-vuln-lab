# 真值审核卡

> 本卡仅在组内保存，不发送给 LLM。真值未审核前不得填写 `dataset/manifest.json` 的 `ground_truth`。

sample_id：S010
family_id：SQL05
代码来源、提交号与文件哈希：自建（lab_people 数据与 mysqli 连接约定取自 D 手册）；源码提交号 7e50925（c/samples，try/catch 修复）；case_code_sha256 = bffb5fc5bf93deac2ea04397af540daa0847678386318a9ccaec6fae2bd6ad2d
入口URL、参数、登录状态：GET `?ids=`（逗号分隔 ID 列表）；登录状态：无（D 证据直接 200 返回业务结果，无需会话）
目标漏洞类型：SQLi
构造目标：fixed（设计目标，非真实标签）
普通业务参考请求及结果：`ids=1,2` → id=1 Alice、id=2 Bob 两条；`ids=3` → id=3 Carol 一条（与 S009 正常行为一致）
参考测试请求及结果：
  - `ids=1 OR 1=1` → 空（非整数项被忽略，未改写 WHERE）
  - `ids=1) OR 1=1 #`、`ids=1) OR 1=1 -- ` → 均空（逐项校验拒绝非整数）
  - `ids=1,abc` → 仅 id=1（Alice）（`abc` 被忽略，`1` 保留）
源头代码位置：`dataset/raw/S010/index.php:8`（入口取值）、`:11-21`（逐项校验）、`:26-32`（占位符与绑定）
调用链：`index.php:8` `$_GET['ids']` → `:11-21` explode/trim/ctype_digit/(int) 强转 → `:26` 生成占位符 → `:27` `IN ($placeholders)` → `:31` bind_param → `:32` execute
危险操作或浏览器输出位置：`index.php:27` 查询语句（仅含占位符，不可信值经绑定进入）
沿途安全措施及其适用范围：`:16` ctype_digit 拒绝非整数 + `:20` (int) 强转 + `:26` 占位符 + `:31` bind_param('i', ...) 覆盖危险点
是否需要额外文件或模板：共享 `bootstrap.php`（提供 `$db`）
结论（true、false或待判定）：false（安全）
置信度：高
结论解释（附文件与行号）：SQLi 四项检查——①输入来源：满足（`index.php:8` `$_GET['ids']`）；②影响语法结构：不满足（不可信值未拼入结构，`index.php:27` 仅含 `?` 占位符，值经 `:31` bind_param 作绑定值进入）；③可达且执行：满足（`:32` execute）；④有效约束：满足（`:16` ctype_digit 校验 + `:31` 绑定覆盖危险点）。②不满足 → 安全。
证据文件相对路径：evidence/truth/S010/http_reference.json（D 于 origin/d/environment-reference）
异常是否回显页面：否（try/catch 捕获；本样本注入输入不产生 SQL 异常）
初审人及日期：C，2026-10-15
复核人及日期：A，2026-10-17；已核对证据提交 `8da63f7` 与当前 `index.php` 字节一致。
争议与解决记录：无。S009 的有效条件与失败尝试在本样本均无结果，逐项 ctype_digit 校验拒绝非整数，符合预期。
