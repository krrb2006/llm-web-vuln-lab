# S015 参考验证（内部）

## 目标
S015 为漏洞版：q 直接拼接进带双引号的 value 属性且不做属性编码，输入中的引号可逃逸属性。

## 验证思路
1. 正常请求：q=hello → 输入框 value 显示 hello。
2. 逃逸请求：q="><script>document.documentElement.dataset.labXss='yes'</script> → 引号闭合 value 属性，脚本执行。
3. 浏览器开发者工具检查 document.documentElement.dataset.labXss 是否为 yes。
4. 使用无害页面标记，不读 Cookie、不向外发送数据。

## 参考请求（浏览器或 Burp，编码前原文）
- GET /lab_cases/S015/index.php?q=hello
- GET /lab_cases/S015/index.php?q="><script>document.documentElement.dataset.labXss='yes'</script>

## 预期结论
- 漏洞版：不可信输入逃逸 value 属性并被当作脚本执行。
- 该结论仅作为内部参考；ground_truth 待 D 实际运行后由 C 复核并回填 manifest（双人复核通过前保持 null）。
