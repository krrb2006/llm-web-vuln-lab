# TraceGuard 静态前端

`web/` 是可直接部署到 GitHub Pages 的零后端代码审计前端。它在浏览器内解压 ZIP、筛选文本源码，并将审计请求**直接**发送至用户填写的 OpenAI Chat Completions 兼容 Endpoint。

## 本地预览

在仓库根目录运行：

```powershell
python -m http.server 8000 -d web
```

随后访问 `http://localhost:8000`。请不要用 `file://` 直接打开，以免浏览器阻止网络请求。

## GitHub Pages 部署

1. 将这些文件推送到 `main` 分支。
2. 在 GitHub 仓库 **Settings → Pages → Build and deployment** 中将 Source 设为 **GitHub Actions**。
3. 等待名为 **Deploy TraceGuard to GitHub Pages** 的工作流完成；页面地址通常为 `https://<用户名>.github.io/llm-web-vuln-lab/`。

## 安全边界

- API Key 只存在当前页面内存中，不会写入 LocalStorage、仓库或本项目服务器。
- 静态 GitHub Pages 不具备安全保管密钥或绕过跨域限制的能力。若模型服务未开放 CORS，请使用该服务官方网页端、允许浏览器直连的兼容 API，或部署你自己受控的最小代理。
- 仅导入你拥有或明确获准进行安全审计的代码。模型发现是辅助结论，必须由人工审核和授权验证确认。
