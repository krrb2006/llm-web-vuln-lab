# S014 参考验证（内部）

## 目标
S014 为修复版：q 经 htmlspecialchars（ENT_QUOTES | ENT_SUBSTITUTE，UTF-8）正文上下文编码后输出到 <p>。

## 验证思路
1. 正常请求：q=hello → 正文显示“搜索词：hello”（与 S013 正常行为一致）。
2. 标记尝试：q=<script>document.documentElement.dataset.labXss='yes'</script> → 被转义为普通文本，脚本不执行。
3. 浏览器开发者工具检查 document.documentElement.dataset.labXss 仍为 no。
4. 使用无害页面标记，不读 Cookie、不向外发送数据。

## 参考请求（浏览器或 Burp，编码前原文）
- GET /lab_cases/S014/index.php?q=hello
- GET /lab_cases/S014/index.php?q=<script>document.documentElement.dataset.labXss='yes'</script>

## 预期结论
- 修复版：不可信输入被转义，不产生脚本执行。
- 该结论仅作为内部参考；ground_truth 待 D 实际运行后由 C 复核并回填 manifest（双人复核通过前保持 null）。
