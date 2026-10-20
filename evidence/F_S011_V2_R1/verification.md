# POC及人工验证记录

run_id：F_S011_V2_R1
sample_id、版本、操作者、复核人：S011 / V2 / D / C
审计代码哈希／运行代码哈希：3028eb9cd8c08e3678f586cdb417c22957fd156c5f757f8ad9b3aee2c97b6ecb / 同一哈希（runtime_check 37/37）
正常业务请求与结果：GET sort=id、sort=name、sort=name DESC 均返回 3 条（1 Alice, 2 Bob, 3 Carol），无 Fatal；见 evidence/truth/S011/http_reference.json。
模型原文相对路径：runs/F_S011_V2_R1/raw_output.txt
模型原始结论及引用行号：vulnerable；F01:0008 读取 sort，F01:0013 拼入 ORDER BY，F01:0015 执行。
模型POC原文路径：pocs/F_S011_V2_R1/original.py；未修改。
执行前人工审核（目标、依赖、文件／网络动作）：仅访问 127.0.0.1:4280；无外部主机、无写文件、无删除、无 Cookie 外发。
原脚本直接运行命令、输出、退出码：ENTRY_PATH=/lab_cases/S011/index.php python pocs/F_S011_V2_R1/original.py → exit 0（原脚本未改，仅用脚本自身要求的 ENTRY_PATH 环境变量）。
有无环境适配及diff路径：无代码修改，仅设置 ENTRY_PATH；证据 evidence/F_S011_V2_R1/。
适配后执行命令和结果：normal [(1,Alice),(2,Bob),(3,Carol)]，test [(3,Carol),(2,Bob),(1,Alice)]。
有无改变请求／测试输入／成功判断逻辑及diff路径：无；请求为 GET sort，断言为解析后的行序比较。
漏洞触发需要的登录、数据、浏览器状态：无需登录；lab_people 三条种子数据。
普通输入和测试输入的受控差异：sort=id vs sort=(CASE WHEN (SELECT COUNT(*) FROM lab_people)=3 THEN -id ELSE id END)。
实际观测（数据库／浏览器／请求响应）：行序变为 3,2,1，证明 sort 进入 ORDER BY；数据未修改。
verification取值：triggered
失败归因和下一步：无；POC 已在本地教学数据上触发并观察到排序变化。
全部证据相对路径：见 runs/formal.json 的 evidence_paths；截图 runs/F_S011_V2_R1/screenshot_*.png，POC pocs/F_S011_V2_R1/，日志 evidence/F_S011_V2_R1/。
执行人签名和日期：D（linan）2026-10-19 19:00（UTC+8）
复核人签名和日期：C（Chang_jia_jia，1715172213@qq.com）2026-10-20（UTC+8），见 results/C_review_D_formal_9_2026-10-20.md
