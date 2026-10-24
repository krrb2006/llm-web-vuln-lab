# POC及人工验证记录

run_id：F_S011_V1_R1
sample_id、版本、操作者、复核人：S011 / V1 / D / C
审计代码哈希／运行代码哈希：3028eb9cd8c08e3678f586cdb417c22957fd156c5f757f8ad9b3aee2c97b6ecb / 同一哈希（runtime_check 37/37）
正常业务请求与结果：GET sort=id、sort=name、sort=name DESC 均返回 3 条（1 Alice, 2 Bob, 3 Carol），无 Fatal；见 evidence/truth/S011/http_reference.json。
模型原文相对路径：runs/F_S011_V1_R1/raw_output.txt
模型原始结论及引用行号：vulnerable；F01:0008 读取 sort，F01:0013 拼入 ORDER BY，F01:0015 执行。
模型POC原文路径：pocs/F_S011_V1_R1/original.py；适配版 pocs/F_S011_V1_R1/adapted.py。
执行前人工审核（目标、依赖、文件／网络动作）：仅访问 127.0.0.1:4280；无外部主机、无写文件、无删除、无 Cookie 外发。
原脚本直接运行命令、输出、退出码：python pocs/F_S011_V1_R1/original.py → exit 1；根路径解析为空，见 stdout_original.txt / stderr_original.txt / exit_code_original.txt。
有无环境适配及diff路径：仅将 BASE_URL 改为 /lab_cases/S011/index.php；evidence/F_S011_V1_R1/adapted.diff。
适配后执行命令和结果：python pocs/F_S011_V1_R1/adapted.py → exit 0；normal [(1,Alice),(2,Bob),(3,Carol)]，test [(2,Bob),(1,Alice),(3,Carol)]。
有无改变请求／测试输入／成功判断逻辑及diff路径：无；请求仍为 GET sort，断言仍为行序比较。
漏洞触发需要的登录、数据、浏览器状态：无需登录；lab_people 三条种子数据。
普通输入和测试输入的受控差异：sort=id vs sort=(id=2) DESC, id ASC。
实际观测（数据库／浏览器／请求响应）：行序由 1,2,3 变为 2,1,3，ORDER BY 表达式被外部输入改变；数据未修改。
verification取值：triggered
失败归因和下一步：无；POC 已在本地教学数据上触发并观察到排序变化。
全部证据相对路径：见 runs/formal.json 的 evidence_paths；截图 runs/F_S011_V1_R1/screenshot_*.png，POC pocs/F_S011_V1_R1/，日志 evidence/F_S011_V1_R1/。
执行人签名和日期：D（linan）2026-10-19 19:00（UTC+8）
复核人签名和日期：C（Chang_jia_jia，1715172213@qq.com）2026-10-20（UTC+8），见 results/C_review_D_formal_9_2026-10-20.md
