# POC及人工验证记录

run_id：F_S010_V1_R1
sample_id、版本、操作者、复核人：S010 / V1 / D / C
审计代码哈希／运行代码哈希：bffb5fc5bf93deac2ea04397af540daa0847678386318a9ccaec6fae2bd6ad2d / 同一哈希（runtime_check 37/37）
正常业务请求与结果：GET ids=1,2 返回 Alice/Bob，GET ids=3 返回 Carol；受控与非法输入均无 Fatal；见 evidence/truth/S010/http_reference.json。
模型原文相对路径：runs/F_S010_V1_R1/raw_output.txt
模型原始结论及引用行号：safe；未发现 ids 进入 SQL 结构，F01:0016 过滤、F01:0027 占位符、F01:0030-0031 绑定。
模型POC原文路径（若没有则写无）：无。
执行前人工审核（目标、依赖、文件／网络动作）：仅访问 127.0.0.1:4280；无外部主机、无写文件、无删除、无 Cookie 外发。
原脚本直接运行命令、输出、退出码：无 POC，未执行。
有无环境适配及diff路径：无。
适配后执行命令和结果：无。
有无改变请求／测试输入／成功判断逻辑及diff路径：无。
漏洞触发需要的登录、数据、浏览器状态：无。
普通输入和测试输入的受控差异：无。
实际观测（数据库／浏览器／请求响应）：仅完成参考业务检查；模型未给出可执行 POC。
verification取值：not_run
失败归因和下一步：模型未生成 POC，未执行攻击性脚本；保持 not_run。
全部证据相对路径：见 runs/formal.json 的 evidence_paths；截图 runs/F_S010_V1_R1/screenshot_*.png，POC pocs/F_S010_V1_R1/，日志 evidence/F_S010_V1_R1/。
执行人签名和日期：D（linan）2026-10-19 19:00（UTC+8）
复核人签名和日期：
