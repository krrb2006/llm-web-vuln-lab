# D：默认模式模型标识抓包核对（2026-10-26）

目的：核对“DeepSeek 默认/快速模式 = DeepSeek-V4.1-Flash-1017”这个说法。
方法：在 D 账号的调试 Edge 中用 CDP 抓取一次最小会话（只发“只回复OK”）的 API 响应；不涉及 S001，不改仓库记录。

## 抓到的关键字段

### 1. 创建会话

```json
"chat_session": {
  "id": "...",
  "model_type": "default"
}
```

### 2. completion 的 ready 事件

```text
event: ready
data: {"request_message_id":1,"response_message_id":2,"model_type":"default"}
```

### 3. assistant 消息

```json
{
  "model": "",
  "role": "ASSISTANT",
  "thinking_enabled": true,
  "search_enabled": false,
  "conversation_mode": "DEFAULT"
}
```

### 4. 设置

- `thinking_enabled: true`
- `search_enabled: false`

## 结论

1. 当前网页/API 明确把这次会话标为 **`model_type: default`**；
2. assistant 消息的 `model` 字段是**空字符串**；
3. 整个响应里**没有** `V4.1`、`Flash` 或 `1017`；
4. 因此，**“默认模式 = V4.1-Flash-1017”目前无法从接口证明**，只能是一个平台内部映射的猜测；
5. 历史 36 条/旧 S001 会话也没有 HAR/API 响应，不能用这个抓包反推它们当时的具体模型。

## 如果平台文档/公告确实写了这个映射

那也只能写成：

> DeepSeek 网页默认模式；据平台说明/公告，该模式对应 V4.1-Flash-1017；但每条运行未捕获模型版本字段。

不能写成“每条运行都证明了 V4.1-Flash-1017”。

## 边界

- 本次抓包是一次新的最小会话，不是 S001；
- 没有保存/上传账号 token、cookie 或完整会话内容；
- 不改 `runs/formal.json`、旧 raw/normalized、bonus plan。

D（linan / linan-prog，2986713478@qq.com）　2026-10-26 21:05（UTC+8）
