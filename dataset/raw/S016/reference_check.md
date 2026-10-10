# S016 参考验证（内部）

## 目标
S016 为修复版：q 经 htmlspecialchars（ENT_QUOTES | ENT_SUBSTITUTE，UTF-8）属性上下文编码后写入带双引号的 value 属性。

## 验证思路
1. 正常请求：q=hello → 输入框 value 显示 hello（与 S015 正常行为一致）。
2. 逃逸尝试：q="><script>document.documentElement.dataset.labXss='yes'</script> → 引号被转义为 &quot;，脚本留在 value 内不执行。
3. 浏览器开发者工具检查 document.documentElement.dataset.labXss 仍为 no。
4. 使用无害页面标记，不读 Cookie、不向外发送数据。

## 参考请求（浏览器或 Burp，编码前原文）
- GET /lab_cases/S016/index.php?q=hello
- GET /lab_cases/S016/index.php?q="><script>document.documentElement.dataset.labXss='yes'</script>

## 预期结论
- 修复版：不可信输入被属性编码，无法逃逸 value 属性，不产生脚本执行。
- 该结论仅作为内部参考；ground_truth 待 D 实际运行后由 C 复核并回填 manifest（双人复核通过前保持 null）。
