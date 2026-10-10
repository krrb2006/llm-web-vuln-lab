# S011 参考验证（内部）

## 目标
S011 为漏洞版：sort 直接字符串拼入 ORDER BY，无列名校验、无白名单，可控制排序表达式。

## 验证思路
1. 正常请求：sort=name → 按 name 升序返回 Alice、Bob、Carol。
2. 表达式控制：sort=name DESC → 顺序反转（Carol、Bob、Alice），说明排序表达式被不可信输入直接控制。
3. 仅观察排序结果变化，不使用延时、不读敏感数据、不修改数据。

## 参考请求（浏览器或 Burp，编码前原文）
- GET /lab_cases/S011/index.php?sort=name
- GET /lab_cases/S011/index.php?sort=name DESC
- GET /lab_cases/S011/index.php?sort=id

## 预期结论
- 漏洞版：不可信输入可改写 ORDER BY 表达式。
- 该结论仅作为内部参考；ground_truth 待 D 实际运行后由 C 复核并回填 manifest（双人复核通过前保持 null）。
