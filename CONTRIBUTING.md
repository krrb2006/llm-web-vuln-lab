# 四人协作规范

## 工作分支

从最新 main 建立分支，例如 `a/criteria`、`b/prompt-v0`、`c/sample-s001`、`d/local-environment`。每项工作单独提交 PR，至少一名其他成员复核后合并。

```bash
git switch main
git pull --ff-only
git switch -c a/criteria
# 完成修改后，只暂存本次相关文件
git add docs/
git commit -m "docs: add vulnerability judgment criteria"
git push -u origin a/criteria
```

示例分支和暂存路径请按本人工作替换。每人使用自己的 Git 身份；不共用账号。组长在仓库创建后邀请其余三人的 GitHub 账号。

## 修改边界

A 维护判定标准、真值审核、汇总和报告；B 维护 prompts；C 维护样本及追溯；D 维护环境说明和验证规范。每个人都需提交自己的实验原文、验证记录、证据和报告章节。

多人修改 `runs/formal.json` 时，仅修改本人负责的记录，由 A 顺序合并并处理冲突。交叉复核：A 的记录由 D 复核；B 由 A；C 由 B；D 由 C。不能自行签署复核。

## 实验记录

保留原始输出；原始 POC、环境适配、逻辑修改分别记录。不能把“脚本执行成功”当作“漏洞触发成功”。正式测试前冻结样本与 Prompt；测试结果不能再用于修改本轮 Prompt。

提交前检查 `git diff --cached`：不得含真实密码、Cookie、令牌、数据库目录或其他项目文件。`.gitignore` 只提供常见排除项，不能代替人工检查。

## 完成标准

PR 写明目的、操作步骤、证据路径、实际验证结果和待解决问题。计划、预期、实测结果明确区分。每人保留自己的提交记录，以支持课堂贡献说明。
