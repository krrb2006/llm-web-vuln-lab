# 代码作者索引

## 出现错误时如何查找作者

老师如果在运行过程中看到错误路径，可以在仓库根目录执行：

```powershell
python tools/show_author.py path/to/failed_file.py
```

例如：

```powershell
python tools/show_author.py environment/check_runtime.py
```

脚本会输出该文件的作者、负责内容和对应说明文档。也可以直接根据下表按错误路径查找。

## 路径到作者的对应关系

| 代码或资料路径 | 作者 | 负责内容 |
|---|---|---|
| `tools/`、`tests/` | A 刘珂如 | 冻结检查、审计、指标评估、测试和最终整合 |
| `dataset/`、`submission_inputs/` | C 常佳佳 | 样本源码、预处理、输入包、行号映射和数据追溯 |
| `prompts/`、`B_*.cmd` | B 张思佳 | SQLi/XSS Prompt、版本迭代和模型输入 |
| `environment/` | D 李楠 | Docker/DVWA 环境、数据库初始化和运行检查 |
| `pocs/`、`demo/`、`evidence/` | D 李楠 | POC、Burp 联动、请求响应、截图和验证证据 |
| `docs/A_*`、`results/A_*` | A 刘珂如 | 判定、真值、复核、统计和阶段整合 |
| `docs/B_*`、`results/B_*` | B 张思佳 | Prompt 实验、模型记录和迭代分析 |
| `docs/C_*`、`results/C_*` | C 常佳佳 | 样本审核、输入包和独立复核 |
| `docs/D_*`、`results/D_*` | D 李楠 | 环境、POC、Burp 和运行复核 |
| `docs/最终*`、`docs/网络安全大作业实验报告*` | A 刘珂如 | 全组最终报告整合 |
| `experiments/`、`runs/`、`templates/` | 全组协作 | 加分实验、模型运行归档和共同模板；具体责任以文件元数据和阶段前缀为准 |

## 代码头部标注约定

新增或修改的可执行代码应在文件头部保留以下信息：

```text
作者：A 刘珂如 / B 张思佳 / C 常佳佳 / D 李楠
职责：该文件在实验流程中的具体用途
```

历史批量生成的样本、模型原文和证据文件不重复改写，以免改变哈希和实验可追溯性；这些文件通过本索引和 `tools/show_author.py` 归属作者。
