# 真值审核卡

> 本卡仅在组内保存，不发送给 LLM。真值未审核前不得填写 `dataset/manifest.json` 的 `ground_truth`。

sample_id：S011
family_id：SQL06
代码来源、提交号与文件哈希：自建（lab_people 数据与 mysqli 连接约定取自 D 手册）；源码提交号 9d5a234（c/samples，本次 try/catch 对齐）；case_code_sha256 = 3028eb9cd8c08e3678f586cdb417c22957fd156c5f757f8ad9b3aee2c97b6ecb
入口URL、参数、登录状态：GET `?sort=`（排序字段）；登录状态：无（D 证据直接 200 返回业务结果，无需会话）
目标漏洞类型：SQLi
构造目标：vulnerable（设计目标，非真实标签）
普通业务参考请求及结果：`sort=id`、`sort=name` → 均返回 id=1/2/3（Alice、Bob、Carol）升序
参考测试请求及结果：`sort=name DESC` → 顺序反转（Carol、Bob、Alice），说明排序表达式被不可信输入直接控制
源头代码位置：`dataset/raw/S011/index.php:8`（入口取值）、`:13`（危险拼接）、`:15`（执行）
调用链：`index.php:8` `$_GET['sort']` → `:13` 字符串拼入 `ORDER BY $sort` → `:15` `$db->query($sql)`
危险操作或浏览器输出位置：`index.php:13` `ORDER BY $sort` 直接拼接；`:15` `$db->query($sql)`
沿途安全措施及其适用范围：无列名白名单、无校验（`trim()` 与空值默认 `id` 不构成对排序表达式的约束）
是否需要额外文件或模板：共享 `bootstrap.php`（提供 `$db`）
结论（true、false或待判定）：true（有漏洞）
置信度：高
结论解释（附文件与行号）：SQLi 四项检查——①输入来源：满足（`index.php:8` `$_GET['sort']`）；②影响语法结构：满足（`index.php:13` `ORDER BY $sort` 拼入排序表达式，非绑定值）；③可达且执行：满足（`index.php:15` `$db->query`）；④无有效约束：满足（无白名单映射，`$sort` 原样进入）。四项全满足 → 有漏洞。
证据文件相对路径：evidence/truth/S011/http_reference.json（D 于 origin/d/environment-reference）
异常是否回显页面：否（try/catch 捕获；本样本证据请求不产生 SQL 异常）
初审人及日期：C，2026-10-15
复核人及日期：A，2026-10-17。
争议与解决记录：D 的运行证据基于 `a04a832`；A 对照当前源码确认差异仅把查询错误处理改为 `try/catch(Throwable)`，`$sort` 拼接、查询执行和正常/受控排序数据流未变，详见 `evidence/truth/S011/current_source_review.json`。当前机器未安装 Docker Desktop，因此不把该差异审计称为新一轮容器复跑。
