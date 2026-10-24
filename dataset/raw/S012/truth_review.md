# 真值审核卡

> 本卡仅在组内保存，不发送给 LLM。真值未审核前不得填写 `dataset/manifest.json` 的 `ground_truth`。

sample_id：S012
family_id：SQL06
代码来源、提交号与文件哈希：自建（lab_people 数据与 mysqli 连接约定取自 D 手册）；源码提交号 9d5a234（c/samples，本次 try/catch 对齐）；case_code_sha256 = 08a09dccfdf19f49f072ca960013703c729f89a49782e8acaab56da6430c1c4f
入口URL、参数、登录状态：GET `?sort=`（排序字段）；登录状态：无（D 证据直接 200 返回业务结果，无需会话）
目标漏洞类型：SQLi
构造目标：fixed（设计目标，非真实标签）
普通业务参考请求及结果：`sort=id`、`sort=name` → 均返回 id=1/2/3（Alice、Bob、Carol）升序（与 S011 正常行为一致）
参考测试请求及结果：`sort=name DESC` → 顺序不变（仍为 1/2/3 升序），非法值回退默认列 id，排序表达式未被改写
源头代码位置：`dataset/raw/S012/index.php:8`（入口取值）、`:9-13`（白名单映射）、`:15`（查询）、`:17`（执行）
调用链：`index.php:8` `$_GET['sort']` → `:9-13` 白名单映射为 `$column`（非法值回退 `id`）→ `:15` `ORDER BY $column` → `:17` `$db->query($sql)`
危险操作或浏览器输出位置：`index.php:15` `ORDER BY $column`（仅白名单常量，排序字段不使用问号占位符）
沿途安全措施及其适用范围：`:9-13` 固定列名白名单映射覆盖排序字段；非法值回退默认列，不可信值未进入语法结构
是否需要额外文件或模板：共享 `bootstrap.php`（提供 `$db`）
结论（true、false或待判定）：false（安全）
置信度：高
结论解释（附文件与行号）：SQLi 四项检查——①输入来源：满足（`index.php:8` `$_GET['sort']`）；②影响语法结构：不满足（不可信值未拼入结构，`index.php:13` 白名单映射后仅 `id`/`name` 常量经 `:15` 进入 `ORDER BY $column`，非法值回退 `id`）；③可达且执行：满足（`:17` query）；④有效约束：满足（白名单覆盖排序字段）。②不满足 → 安全。
证据文件相对路径：evidence/truth/S012/http_reference.json（D 于 origin/d/environment-reference）
异常是否回显页面：否（try/catch 捕获；本样本证据请求不产生 SQL 异常）
初审人及日期：C，2026-10-15
复核人及日期：A，2026-10-17。
争议与解决记录：D 的运行证据基于 `a04a832`；A 对照当前源码确认差异仅把查询错误处理改为 `try/catch(Throwable)`，排序字段白名单、查询执行和输出数据流未变，详见 `evidence/truth/S012/current_source_review.json`。当前机器未安装 Docker Desktop，因此不把该差异审计称为新一轮容器复跑。
