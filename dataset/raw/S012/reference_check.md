# S012 参考验证（内部）

## 目标
S012 为修复版：sort 经固定列名白名单映射为 id/name，非法值回退默认列 id，排序表达式不可被输入改写。

## 验证思路
1. 正常请求：sort=name → 按 name 升序返回 Alice、Bob、Carol（与 S011 正常行为一致）。
2. 控制尝试：sort=name DESC → 非法值回退默认列 id，顺序不变（不反转）。
3. 仅观察排序结果变化，不使用延时、不读敏感数据、不修改数据。

## 参考请求（浏览器或 Burp，编码前原文）
- GET /lab_cases/S012/index.php?sort=name
- GET /lab_cases/S012/index.php?sort=name DESC
- GET /lab_cases/S012/index.php?sort=id

## 预期结论
- 修复版：非法排序输入回退默认列，排序表达式不可控。
- 该结论仅作为内部参考；ground_truth 待 D 实际运行后由 C 复核并回填 manifest（双人复核通过前保持 null）。
