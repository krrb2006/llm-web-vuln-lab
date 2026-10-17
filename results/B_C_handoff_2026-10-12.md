# B 接收 C 标准输入进度（2026-10-12）

来源：`origin/c/samples` 提交 `a04a832`。只读取 C 分支的标准包，没有改动 C 的样本、manifest 或 line_map。

|开发样本|C 标准包|B 的 V0 输入|状态|
|---|---|---|---|
|S001—S006|尚未从 C 分支获得|无|待 C 提供|
|S013|`dataset/packets/S013_v1/code_input.txt`|`runs/DEV_S013_V0_R1/input.txt`|已准备；未送模型|
|S014|`dataset/packets/S014_v1/code_input.txt`|`runs/DEV_S014_V0_R1/input.txt`|已准备；未送模型|
|S015|`dataset/packets/S015_v1/code_input.txt`|`runs/DEV_S015_V0_R1/input.txt`|已准备；未送模型|
|S016|`dataset/packets/S016_v1/code_input.txt`|`runs/DEV_S016_V0_R1/input.txt`|已准备；未送模型|
|S017—S018|尚未从 C 分支获得|无|待 C 提供|

四个输入已通过工具的 sample_id、代码边界、显式答案泄露检查；标准包 SHA256 保存在各 `metadata.json` 与 `runs/b_packet_lock.json`。准备时发现 Windows 检出将 LF 转为 CRLF，导致工作区字节哈希不同于 C 提交的标准包。模型提交前已按 C 的 Git blob 统一为 LF、逐行核对源码与内部映射，并在元数据保留修正前哈希；没有原始模型回答被覆盖。需要操作者在约定的同一个被测模型界面分别开新会话提交这四份 `input.txt`，保存完整原始回答与实际模型设置，再用 `tools/b_runs.py record` 归档。当前真实模型观察数仍为 0，不能据此修改 V1。

C 分支已有 S009—S012 标准包；S009、S012 是 C 的正式复核对象，必须等 Prompt 冻结及 C 的正式模型原文和验证证据后复核，不能提前将它们当开发集。
