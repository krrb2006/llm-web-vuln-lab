# S001 八条模型 POC 实操验证

2026-10-26：八条原始模型 Python 代码均实际运行，退出码均为0。脚本逐条与对应 raw 代码块比对一致，未修补模型代码。目标为本地 127.0.0.1:4280。进程设置 NO_PROXY=127.0.0.1,localhost，以避免本机代理导致502；未改变模型脚本。

IGNORE_BASE 普通/真条件得到Alice，假条件为空；其余七条普通得到Alice，测试得到Alice/Bob/Carol。独立HTTP观察保存 normal/true/false/or/comment 请求及完整响应，记录解析与上述预期一致。不是仅依据HTTP200或退出码判定。

每条目录包含原始脚本、stdout、stderr；execution_summary.json 含运行时间、源raw及脚本哈希、退出码、日志哈希。运行源码哈希记录于 runtime_source_hash.txt。此前失败尝试仍在 S001_poc_actual_2026-10-26 中保留。

脚本均发出只读SELECT条件测试。未做执行前后数据库快照，故不以此声称独立验证数据库完全不变。当前实操验证针对S001源码；注入包仅注释差异的核验见文件层自检。

该实操结果补充漏洞验证，不证明DeepSeek模型版本或生成设置。正式36条和加分planned状态未修改，交C独立复核、A裁定。
