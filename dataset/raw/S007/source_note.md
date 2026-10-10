# S007 来源说明

- 代码来源：自建教学样本，未复制第三方代码。
- 参考依据：C 手册「二 样本构造」SQL04 蓝图（入口到 repository 函数的查询，辅助函数内部拼接）
  与 D 手册「三 教学数据」的 `lab_people` 表结构。
- 改动说明：将查询拆为入口 `index.php` 与数据访问层 `repository.php` 两个文件，
  保留完整调用链；代码注释保持中性，不含「漏洞/修复」等标签。
- 许可：自建，无第三方许可约束。
- case_code_sha256（当前文件；冻结前需与容器内运行文件两端一致）：
  - `index.php`：`ef9f569558f6fb59842c87f48987dfd8829fcf0f2cc709facb4de3c0eb9809e8`
  - `repository.php`：`50956c0086d652fff94ce4bc82710dd804c6429be74a272fb320c8c53021f739`
- source_url / source_commit：自建样本，暂为空。
