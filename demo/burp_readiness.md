# Burp 本机代理准备与联动观察（2026-10-13）

这是 D 对工具和环境的准备及本机代理观察记录，不计入正式模型运行。SQLi/XSS 的代理请求、响应和页面效果已有证据；两组 Burp Repeater 原生重放均已完成。

- 工具：已安装并启动 Burp Suite Community Edition v2026.9.2，临时项目。
- 范围：仅本机 `127.0.0.1:4280` 的 DVWA 教学容器；Burp Proxy 监听 `127.0.0.1:8080`，Intercept 保持关闭。
- 普通请求：`GET /login.php?d_burp_ready=20261011 HTTP/1.1`，`Host: 127.0.0.1:4280`，无请求 Cookie。
- Proxy HTTP history：该请求的 Host 为 `http://127.0.0.1:4280`，状态 200，HTML 标题为 `Login :: Damn Vulnerable Web Application (DVWA)`。
- Repeater：从对应历史行选择 **Send to Repeater**，点击 **Send**，再次得到 `HTTP/1.1 200 OK` 和登录页 HTML。独立正文健康检查确认 `<form` 存在，且无 `Fatal error` 或 `Access denied`。
- Burp 响应头包含临时 PHP 会话标识，因此不将原始响应或未遮盖的界面截图提交到 Git。上述记录只保存路径、状态和页面标识。

此前同一路径虽然返回 HTTP 200，正文却是数据库权限错误。D 已将 DVWA 主站与教学样本的数据库配置隔离，并在 `environment/capture_environment.py` 增加正文健康断言。`environment/runtime_check.json` 单独核对生成配置的来源、本地与容器哈希和 PHP 语法。

本轮 SQLi 与 XSS 代理请求和页面观察分别保存在 `demo/burp_sqli_proxy_observation.json`、`demo/burp_xss_proxy_observation.json`。XSS 浏览器截图也一并保存。Burp 原生窗口已完成 XSS 的两条 Repeater 重放，以及下方记录的四条 SQLi Repeater 请求。SQLi Repeater 观察摘要见 `demo/burp_sqli_repeater_observation.json`；S010 控制条件界面截图以及 S009 配对截图已保存。10 月 13 日新发送的 S009 受控条件请求与完整响应正文已另存到 `demo/S009_request.raw.txt` 和 `demo/S009_response.raw.txt`，SHA-256 见 Repeater 观察 JSON；其余三条 SQLi Repeater 消息的 raw 文件尚未保存。

## Listener 状态与启动方法（2026-10-13）

本轮初检时 Burp 进程仍在，但 `127.0.0.1:8080` 没有监听。用户随后打开 Burp 自带浏览器；之后系统检查确认该地址已由 BurpSuite.exe（PID 52292）监听。D 经 listener 完成 S009/S010 四条只读 GET 对照；首轮 XSS 的 POST、列表与预览 GET 经 listener 完成，记录分别见两个代理观察 JSON。后来清理导致旧草稿编号失效，见下方 Repeater 复核记录。

如果 listener 后续停止，在 Burp 打开 Settings（齿轮）→ Tools → Proxy，在 Proxy listeners 中确认 `127.0.0.1:8080` 的 Running 已勾选；若没有活动 listener，在该面板使用 **Restore defaults**。监听地址保持 `127.0.0.1`。

Burp 自带浏览器会自动使用当前 Burp listener。访问教学靶场时只打开 `http://127.0.0.1:4280/`。官方步骤见 [检查 Burp Proxy listener](https://portswigger.net/burp/documentation/desktop/external-browser-config/check-listener) 和 [Burp 自带浏览器](https://portswigger.net/burp/documentation/desktop/tools/burps-browser)。

## Repeater 404 与重试准备（2026-10-13）

用户提供的 Repeater 截图显示 `GET /lab_cases/S022/preview.php?id=14` 返回 `404 Not Found`。这是此前演示清理后重放旧草稿编号的结果：`preview.php` 在该编号不存在时返回 404 和“草稿不存在。”；请求已到达本机 PHP 服务，不能据此判断 Burp listener 或路径失效。

为便于重放，通过本机测试客户端重新提交了两条同一无外联 marker 草稿；这次提交未出现在 Burp Proxy HTTP history，因此不计作经 Proxy 的提交证据。POST 均为 303，随后预览 GET 均为 200：S021 新编号为 `id=15`，S022 新编号为 `id=16`。唯一标题分别为 `BurpD_RepeaterRetry_20261013T114737Z_S021`、`BurpD_RepeaterRetry_20261013T114737Z_S022`。

已在 Burp 原生窗口以 `http://127.0.0.1:4280` 为 target 手工重放：Repeater 标签 3 的 S021 `id=15` 返回 HTTP 200，响应正文保留原始 `<script>`；标签 2 的 S022 `id=16` 返回 HTTP 200，响应正文将 `<script>` 和单引号转义。两条测试记录仍暂时保留，供现场复核；完成证据留存后按唯一标题清理。

## SQLi Repeater 现场结果（2026-10-13）

Burp 原生 Repeater 标签 1 对本机 DVWA 发出四条无 Cookie 的只读 GET，均返回 HTTP 200：S009 `ids=1` 返回 Alice，`ids=1) OR 1=1 #` 返回 Alice、Bob、Carol；S010 `ids=1,2` 返回 Alice、Bob，同一受控条件无结果。页面均未显示 PHP Fatal error。请求行、响应时间、Content-Length 和观察行数见 `demo/burp_sqli_repeater_observation.json`。该 JSON 是 GUI 现场摘要，不包含 raw 全文；S009 最新受控条件请求/响应已另存到 `demo/S009_request.raw.txt`、`demo/S009_response.raw.txt`。另有一次手工输入缺少请求头终止空行，Burp 警告后 Apache 返回 408；此项是请求录入失败，不计作样本观察。S010 控制条件的 Repeater 截图已保存，S009 配对截图也已保存。其余三条 SQLi Repeater 消息的 raw 文件尚未保存。

## 两例演示的 Repeater 请求草稿

以下是复现实验时可用的请求草稿；它们对应的代理观察已保存，SQLi Repeater 的实际请求与结果见 `demo/burp_sqli_repeater_observation.json`。XSS 页面效果已由临时 Chrome 配置 Burp 代理后记录，说明见代理观察 JSON。

### SQLi：S009 与 S010 对照

先在 Burp 浏览器访问 S009 普通路径并从 Proxy history 发送到 Repeater。然后分别重放 S009 测试请求和 S010 对照请求。`%23` 是 URL 编码后的 `#`，避免它被浏览器当作片段标记。

**正常请求：**

```http
GET /lab_cases/S009/index.php?ids=1 HTTP/1.1
Host: 127.0.0.1:4280
```

**S009 测试请求：**

```http
GET /lab_cases/S009/index.php?ids=1%29%20OR%201%3D1%20%23 HTTP/1.1
Host: 127.0.0.1:4280
```

**S010 对照请求：**

```http
GET /lab_cases/S010/index.php?ids=1%29%20OR%201%3D1%20%23 HTTP/1.1
Host: 127.0.0.1:4280
```

实际观察：S009 普通输入和卡片输入 `1 OR 1=1` 均返回 Alice 一行，受控条件返回三行；同一受控条件在 S010 无结果。响应状态码本身不作为结论。代理链路实测与完整正文见 `demo/burp_sqli_proxy_observation.json`。S009 最新一次受控条件 Repeater 的完整请求与响应另存于 `demo/S009_request.raw.txt`、`demo/S009_response.raw.txt`；其余三条 Repeater 消息仍只有结构化观察和已有截图。

### XSS：S021 与 S022 对照

分别向两个样本提交普通草稿和同一测试草稿。测试正文只设置当前文档的 `data-lab-xss` 属性，不读取浏览器数据，也不发起外部请求。

**正常请求（分别改路径发到 S021 和 S022）：**

```http
POST /lab_cases/S021/submit.php HTTP/1.1
Host: 127.0.0.1:4280
Content-Type: application/x-www-form-urlencoded

title=BurpDemo&body=Hello
```

**测试请求（分别改路径发到 S021 和 S022）：**

```http
POST /lab_cases/S021/submit.php HTTP/1.1
Host: 127.0.0.1:4280
Content-Type: application/x-www-form-urlencoded

title=BurpDemo&body=%3Cscript%3Edocument.documentElement.dataset.labXss%3D%27yes%27%3C%2Fscript%3E
```

实际观察：S021/S022 的普通与 marker POST 均返回 303，列表与预览 GET 均返回 200。S021 预览设置 `html[data-lab-xss="yes"]`；S022 将标记显示为转义文本且没有该属性。完整请求、响应、DOM、清理行数见 `demo/burp_xss_proxy_observation.json`，截图文件路径也记录在该 JSON 中。请求经 Burp listener；DOM 与截图来自临时 headless Chrome 代理观察，尚非 Burp 自带浏览器窗口截图。演示结束后只删除本轮唯一标题对应的行，S021/S022 行数已恢复到初始值。
