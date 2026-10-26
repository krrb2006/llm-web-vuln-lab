# ADV 本地运行对照证据（2026-10-26）

执行人：A（本机统一环境）  
目标：`http://127.0.0.1:4280`  仅限本地教学靶场  
运行结果：`results/ADV_runtime_check_2026-10-26.json`

## 环境与检查

- Docker Desktop Linux Engine 已启动。
- 由 `environment/build_advanced_cases.py --a-ref HEAD --c-ref HEAD --d-ref HEAD` 生成运行副本。
- 由 `environment/init_lab_db.py --reset-advanced` 初始化 ADV 数据。
- `check_advanced.py` 的 PHP 语法检查通过。

## SECOND_SQLI_01

- 漏洞版写入普通值和受控条件字符串均返回 HTTP 200。
- 漏洞版后续查询响应长度为 33，修复版为 15。
- 漏洞版和修复版响应哈希不同，检查结果为 `vulnerable_response_longer_than_fixed`。
- 这支持“写入阶段安全、后续读取阶段二次拼接”的对照结论。

## IDOR_01

- 当前会话用户为 101。
- 访问自己的对象：漏洞版和修复版均返回 HTTP 200。
- 访问其他用户对象：漏洞版仍返回对象内容，修复版响应为空。
- 检查结果为 `vulnerable_allows_other_owner_fixed_filters_owner`。

## 限制与状态

本文件只证明本机本地业务对照和环境可运行性，不包含 DeepSeek 模型原文、模型设置截图、模型生成 POC 或浏览器触发证据。因此四条 `ADV_*` 计划继续保持 `planned`，不能仅凭本文件改为 `reviewed`。

未执行外部目标、未访问非本地地址、未修改 36 条正式实验记录。
