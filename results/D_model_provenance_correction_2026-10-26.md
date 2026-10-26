# D：模型口径核对与更正（2026-10-26，官方资料补充版）

核对人：D
适用范围：本仓库所有 DeepSeek 网页端运行记录，包括 36 条正式记录、加分实验和 S001 重跑。

## 一、官方资料

DeepSeek 官方 API 文档有两条直接相关的公告：

1. **2026-10-17：DeepSeek V4.1 Flash 新版本**
   - 标题：DeepSeek V4.1 Flash 新版本：许愿式编程一键成真
   - 原文：**“DeepSeek V4.1 Flash 现已更新至 V4.1-Flash-1017 版本，官方网页端、APP 与 API 模型已同步变更为新模型。”**
   - https://api-docs.deepseek.com/zh-cn/news/news261017/

2. **2026-09-10：DeepSeek V4.1 Flash 发布**
   - API 模型名为 `deepseek-flash`；V4.1 Flash 上线 API。
   - https://api-docs.deepseek.com/zh-cn/news/news260910/

## 二、这些资料能证明什么

### 能证明

- 2026-10-17 起，**DeepSeek 官方网页端**模型已同步为 `V4.1-Flash-1017`；
- 本仓库的正式运行发生在 **2026-10-19/20**，在这条公告之后；
- 因此，**平台层面**上，当时网页端默认/快速模式对应 `V4.1-Flash-1017` 是官方公告支持的。

### 不能证明

- 每条运行**实际返回的模型字段**：当前 API 抓包只返回：
  - `model_type: "default"`
  - assistant `model: ""`
  - 没有 `V4.1`/`Flash`/`1017` 字段；
- 仓库里没有当时的 HAR/API 响应/模型选择器截图；
- `runs/formal.json` 的 36 条 `model_snapshot` 仍全部为 `None`；
- 只有 D 的 9 条 metadata 写了 `V4.1-Flash-1017`，来源是页面横幅文字记录，没有截图/HAR。

## 三、正确口径

建议写成两层：

```text
平台口径：DeepSeek 网页默认/快速模式；据官方 2026-10-17 公告，网页端已同步为 V4.1-Flash-1017。
单次运行：未捕获模型版本字段，model_version_proven=false。
```

不再写：

```text
36 条每条都独立验证了 V4.1-Flash-1017
```

也不必写：

```text
明确不是 V4.1-Flash
```

因为官方公告支持平台映射，只是缺少逐次运行字段。

## 四、影响

1. **36 条正式实验**：可以继续写“DeepSeek V4.1 Flash / 网页默认模式”，但必须在报告中注明“平台映射，非逐次字段验证”。
2. **S001 官方 8 条**：原会话不可访问；原证据仍缺逐次模型字段，不能把“POC 跑通”当成模型版本证明。
3. **S001 D 默认模式 8 条**：运行在 2026-10-26，官方公告之后；平台层面同样是 V4.1-Flash-1017，但仍是 `exploratory_only=true` 的新会话，不能冒充 B 原 8 条。
4. **加分统计**：14/26 不因口径修正自动变化；A/C 决定是否把 S001 D 8 条计入。

## 五、建议 A/C 的动作

1. A 在最终报告写：
   - 模型家族：DeepSeek V4.1 Flash；
   - 网页入口：默认/快速模式；
   - 平台映射：官方 2026-10-17 公告，网页端同步 `V4.1-Flash-1017`；
   - 逐次证据：未捕获 model 字段，`model_version_proven=false`（如按严格口径）。
2. C 复核时注明：官方映射是平台级证据，不等于每条会话的接口字段。
3. 如果课程要求“逐条运行都能证明模型版本”，当前证据仍不足，只能如实说明；不能伪造 HAR。

## 六、引用

- https://api-docs.deepseek.com/zh-cn/news/news261017/
- https://api-docs.deepseek.com/zh-cn/news/news260910/

D（linan / linan-prog，2986713478@qq.com）　2026-10-26 21:15（UTC+8）
