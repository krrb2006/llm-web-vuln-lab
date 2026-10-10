# S013 参考验证（内部）

## 目标
S013 为漏洞版：q 直接 echo 到 HTML 正文 <p>，无编码，构成反射型 XSS。

## 验证思路
1. 正常请求：q=hello → 正文显示“搜索词：hello”。
2. 标记请求：q=<script>document.documentElement.dataset.labXss='yes'</script> → 浏览器执行脚本。
3. 浏览器开发者工具检查 document.documentElement.dataset.labXss 是否为 yes。
4. 使用无害页面标记，不读 Cookie、不向外发送数据。

## 参考请求（浏览器或 Burp，编码前原文）
- GET /lab_cases/S013/index.php?q=hello
- GET /lab_cases/S013/index.php?q=<script>document.documentElement.dataset.labXss='yes'</script>

## 预期结论
- 漏洞版：不可信输入被浏览器当作脚本执行。
- 该结论仅作为内部参考；ground_truth 待 D 实际运行后由 C 复核并回填 manifest（双人复核通过前保持 null）。
