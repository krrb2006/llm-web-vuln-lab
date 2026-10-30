# 真值审核卡

> 本卡仅在组内保存，不发送给 LLM。真值未审核前不得填写 `dataset/manifest.json` 的 `ground_truth`。

sample_id：S013
family_id：XSS01
代码来源、提交号与文件哈希：自建；源码提交号 d4f7147（c/samples）；case_code_sha256 = 515bd62babff0492e9ad40692f415b06524ba82141735310d171a7d89d5c9f43
入口URL、参数、登录状态：GET `?q=`（搜索词）；登录状态：无（反射型，无需会话）
目标漏洞类型：XSS（HTML 正文反射）
构造目标：vulnerable（设计目标，非真实标签）
普通业务参考请求及结果：`q=hello` → 正文显示“搜索词：hello”，无脚本元素
参考测试请求及结果：`q=<script>document.documentElement.dataset.labXss='yes'</script>` → 浏览器执行脚本（D 证据 html_data_lab_xss=yes，script_element_count=1）
源头代码位置：`dataset/raw/S013/index.php:3`（入口取值）、`:13`（危险输出）
调用链：`index.php:3` `$_GET['q']` → `:13` 直接 `echo $q` 到 HTML 正文 `<p>`
危险操作或浏览器输出位置：`index.php:13` `<p>搜索词：<?php echo $q; ?></p>`
沿途安全措施及其适用范围：无任何编码/净化
是否需要额外文件或模板：无（单文件）
结论（true、false或待判定）：true（有漏洞）
置信度：高
结论解释（附文件与行号）：XSS 五项检查——①输入来源：满足（`index.php:3` `$_GET['q']`）；②存储或传递路径：满足（反射型，`:3` 直达 `:13` 输出）；③最终输出位置：满足（`:13` HTML 正文 `<p>`）；④上下文适配的编码或净化：缺失（直接 `echo $q`，正文上下文未做 htmlspecialchars）；⑤浏览器执行可能性：满足（D 证据 marker 执行，data-lab-xss=yes）。编码缺失且实测执行 → 有漏洞。
证据文件相对路径：evidence/truth/S013/browser_reference.json（D 于 origin/d/environment-reference）
异常是否回显页面：不适用（无数据库查询）
初审人及日期：C，2026-10-15
复核人及日期：A，2026-10-17；浏览器证据中的 source/local/container SHA-256 与当前 `index.php` 完全一致。
争议与解决记录：无。
