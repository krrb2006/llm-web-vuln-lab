# S010 参考验证（内部）

## 目标
S010 为修复版：ids 逐项 ctype_digit 校验并强制转整型，按数量生成占位符，bind_param 逐项绑定（类型 'i'）。

## 验证思路
1. 正常请求：ids=1,2 → 返回 Alice、Bob 两条记录（与 S009 正常行为一致）。
2. 注入尝试：ids=1 OR 1=1 → 空格与非整数项被忽略，不返回全部记录，WHERE 语义未被改写。
3. 混合输入：ids=1,abc → 忽略 abc，仅返回 id=1。
4. 仅观察教学数据条件变化，不读敏感数据、不延时、不修改数据。

## 参考请求（浏览器或 Burp，编码前原文）
- GET /lab_cases/S010/index.php?ids=1,2
- GET /lab_cases/S010/index.php?ids=1 OR 1=1
- GET /lab_cases/S010/index.php?ids=1,abc

## 预期结论
- 修复版：注入输入被当作无效整数忽略，不改变查询逻辑。
- 该结论仅作为内部参考；ground_truth 待 D 实际运行后由 C 复核并回填 manifest（双人复核通过前保持 null）。
