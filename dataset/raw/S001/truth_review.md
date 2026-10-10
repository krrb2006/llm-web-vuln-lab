# 真值审核卡（空白，待填写）

> 本卡仅在组内保存，不发送给 LLM。真值未审核前不得填写 `dataset/manifest.json` 的 `ground_truth`。

sample_id：S001
family_id：SQL01
代码来源、提交号与文件哈希：自建；sha256 见 source_note.md；提交号待首次提交后补
入口URL、参数、登录状态：GET `?name=`；登录状态待 D 确认；**未验证**
目标漏洞类型：SQLi
构造目标：vulnerable（设计目标，非真实标签）
普通业务参考请求及结果：**未验证**
参考测试请求及结果：**未验证**
源头代码位置：`dataset/raw/S001/index.php:9-10`（拼接与执行）
调用链：`index.php:7` `$_GET['name']` → `:9` 字符串拼接 → `:10` `$db->query($sql)`
危险操作或浏览器输出位置：`index.php:10` `$db->query($sql)`
沿途安全措施及其适用范围：未观察到绑定/转义（**待人工复核确认**）
是否需要额外文件或模板：`../common/db_connect.php`（共享 bootstrap）
结论（true、false或待判定）：**待判定（未验证）**
结论解释（附文件与行号）：**未验证**
证据文件相对路径：（无）
初审人及日期：A，未进行
复核人及日期：（C 复核，未进行）
争议与解决记录：（无）
