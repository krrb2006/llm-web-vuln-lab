# S001 原始模型 POC 执行记录

2026-10-26，按用户最新授权逐条执行八条原始模型脚本。脚本直接从 evidence/S001_message_bound_2026-10-26 各自 raw 的 Python 代码块提取，未修改代码。scripts.json 记录源 raw、脚本哈希与语法检查。

八条均已实际启动 Python 进程，stdout.txt、stderr.txt、execution.json 分别保留完整输出及退出码。全部在本地请求阶段失败，未获得可判定的业务记录，不能认定漏洞触发。错误包含 WinError 10061 连接被拒绝，以及本机代理返回 HTTP 502。并非运行一次通用 payload 后复制到八条。

环境排查：127.0.0.1:4280 无监听；Docker Linux API 初始报 dockerDesktopLinuxEngine 管道不存在。尝试启动 Docker Desktop 及 docker desktop start，相关进程出现，但引擎检查尚未返回就绪。未重置数据库或修改系统安全设置。

这些是新的执行尝试证据；此前“不执行POC”的记录描述其当时状态，保留历史。当前执行不会填充正式36条实验，也不会使加分 planned 自动成为 reviewed。

完整验收仍缺：靶场恢复后八条脚本的业务结果；已有DeepSeek会话内完整输入和回答导出；模型与生成设置来源的最终裁定。当前不声称完整验收通过。
