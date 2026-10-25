# ADV 本地运行对照证据（2026-10-25）

## 环境

- 目标：`http://127.0.0.1:4280`
- Docker Server：29.8.2
- 数据库：`teaching_lab`
- 初始化：`python environment/init_lab_db.py --reset-advanced`
- 运行副本：由 `environment/build_advanced_cases.py` 生成，原始蓝图源码未改写
- POC 范围：仅本机教学环境；未向外部地址发送请求

## 语法检查

以下 6 个运行副本均通过 `php -l`：

- `SECOND_SQLI_01/vulnerable/save_profile.php`
- `SECOND_SQLI_01/vulnerable/lookup_profile.php`
- `SECOND_SQLI_01/fixed/save_profile.php`
- `SECOND_SQLI_01/fixed/lookup_profile.php`
- `IDOR_01/vulnerable/invoice.php`
- `IDOR_01/fixed/invoice.php`

## 二次 SQLi 对照

1. 通过漏洞版保存普通昵称，HTTP 200 且返回 `saved`。
2. 通过漏洞版保存受控昵称 `' OR 1=1 #`，HTTP 200 且返回 `saved`。
3. 使用同一 profile id 读取：漏洞版返回集合长度大于修复版。
4. 修复版第二次查询使用参数绑定，未出现同样的扩大结果集合。

结论：运行时观察到 `SECOND_SQLI_01` 漏洞版/修复版的二次使用差异。该记录只证明本地业务对照，不替代模型分析记录，也不宣称通用环境结果。

## IDOR 对照

数据库种子为用户 A=`101`、用户 B=`202`；发票 `1001` 属于 A，`1002` 属于 B。

1. 以 session user 101 访问自己的 `1001`：漏洞版和修复版均返回 A 的发票。
2. 以 session user 101 访问 B 的 `1002`：漏洞版返回 owner 202 的发票；修复版返回空结果。
3. HTTP 200 未作为成功条件，判断基于返回对象和修复版的所有权过滤。

结论：运行时观察到 `IDOR_01` 漏洞版存在越权读取，修复版执行服务端所有权约束。

## 状态边界

- 本次仅完成 ADV 环境、语法和本地业务对照；没有执行 DeepSeek 模型会话。
- 没有写入 `runs/formal.json`，没有修改 36 条主实验。
- 四条 `ADV_*` 计划仍为 `planned`，等待模型记录和 D 独立复核后再决定是否更新状态。
