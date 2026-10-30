# 真值审核卡

> 本卡仅在组内保存，不发送给 LLM。真值未审核前不得填写 `dataset/manifest.json` 的 `ground_truth`。

sample_id：S015
family_id：XSS02
代码来源、提交号与文件哈希：自建；源码提交号 d4f7147（c/samples）；case_code_sha256 = 1270539fa9afa232e32a272568c2198f0a3bfd819de8a7765535e215fdab2d46
入口URL、参数、登录状态：GET `?q=`（留言内容）；登录状态：无（反射型，无需会话）
目标漏洞类型：XSS（带引号普通属性反射）
构造目标：vulnerable（设计目标，非真实标签）
普通业务参考请求及结果：`q=hello` → 输入框 `value="hello"`，无脚本元素
参考测试请求及结果：`q="><script>document.documentElement.dataset.labXss='yes'</script>` → 引号闭合 value 属性后脚本执行（D 证据 html_data_lab_xss=yes，script_element_count=1）
源头代码位置：`dataset/raw/S015/index.php:3`（入口取值）、`:15`（危险输出）
调用链：`index.php:3` `$_GET['q']` → `:15` 直接拼入 `<input ... value="<?php echo $q; ?>">`
危险操作或浏览器输出位置：`index.php:15` `value="<?php echo $q; ?>"`（带双引号属性，无属性编码）
沿途安全措施及其适用范围：无任何编码/净化（属性引号可被输入中的 `"` 逃逸）
是否需要额外文件或模板：无（单文件）
结论（true、false或待判定）：true（有漏洞）
置信度：高
结论解释（附文件与行号）：XSS 五项检查——①输入来源：满足（`index.php:3` `$_GET['q']`）；②存储或传递路径：满足（反射型，`:3` 直达 `:15` 输出）；③最终输出位置：满足（`:15` 带双引号的普通属性 value）；④上下文适配的编码或净化：缺失（直接 `echo $q`，属性上下文未做引号/HTML 编码）；⑤浏览器执行可能性：满足（D 证据 marker 执行，data-lab-xss=yes）。编码缺失且实测执行 → 有漏洞。
证据文件相对路径：evidence/truth/S015/browser_reference.json（D 于 origin/d/environment-reference）
异常是否回显页面：不适用（无数据库查询）
初审人及日期：C，2026-10-15
复核人及日期：A，2026-10-17；浏览器证据中的 source/local/container SHA-256 与当前 `index.php` 完全一致。
争议与解决记录：无。
