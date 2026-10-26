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
4. 因此，**接口本身不能证明“默认模式 = V4.1-Flash-1017”**；
5. 但 DeepSeek 官方 API 文档 2026-10-17 公告明确写：
   > “DeepSeek V4.1 Flash 现已更新至 V4.1-Flash-1017 版本，官方网页端、APP 与 API 模型已同步变更为新模型。”
   - https://api-docs.deepseek.com/zh-cn/news/news261017/
6. 本仓库正式运行在 2026-10-19/20，公告之后；所以**平台层面**可以支持“网页默认模式 = V4.1-Flash-1017”，但**逐次运行的 model 字段仍未捕获**；
7. 历史 36 条/旧 S001 会话也没有 HAR/API 响应，不能用这个抓包反推每条当时的具体模型。

## 官方公告后的正确写法

> DeepSeek 网页默认/快速模式；据官方 2026-10-17 公告，网页端已同步为 V4.1-Flash-1017；但每条运行未捕获模型版本字段，`model_version_proven=false`。

不能写成“每条运行都独立验证了 V4.1-Flash-1017”。

## 边界

- 本次抓包是一次新的最小会话，不是 S001；
- 没有保存/上传账号 token、cookie 或完整会话内容；
- 不改 `runs/formal.json`、旧 raw/normalized、bonus plan。

D（linan / linan-prog，2986713478@qq.com）　2026-10-26 21:05（UTC+8）
