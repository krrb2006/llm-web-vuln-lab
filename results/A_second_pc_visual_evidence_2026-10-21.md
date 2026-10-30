# A 第二台电脑视觉留证（2026-10-21）

## 范围

本记录由 A 在当前复现机完成，用于补充 D 要求的第二台电脑环境可移植性证据。浏览器访问范围固定为 `http://127.0.0.1:4280`；本轮不运行模型、不运行正式 POC、不修改 `runs/formal.json`，也不把本轮观察写入正式真值。

本轮通过可控浏览器页面保存了 SQLi、排序和 XSS 配对页面截图。截图证明页面可见结果和 DOM marker；它们不替代 Docker `compose ps`、完整 `runtime_check.json` 或 60–90 秒录屏。

## 截图清单

| 文件 | 页面与操作 | 可见观察 |
|---|---|---|
| `environment/second_pc/screenshots/S009_normal_ids1.png` | S009 `index.php?ids=1` | 正常请求显示 1 行 Alice |
| `environment/second_pc/screenshots/S009_controlled_3rows.png` | S009 `index.php?ids=1%29%20OR%201%3D1%20%23` | 受控请求显示 Alice、Bob、Carol 共 3 行 |
| `environment/second_pc/screenshots/S011_normal_id.png` | S011 `index.php?sort=id` | 正常排序页面 |
| `environment/second_pc/screenshots/S011_controlled_name_desc.png` | S011 `index.php?sort=name%20DESC` | 受控排序页面，顺序发生变化 |
| `environment/second_pc/screenshots/S021_preview_marker_yes.png` | S021 提交 marker 后的独立 `preview.php` | 页面 DOM `document.documentElement.dataset.labXss` 实测为 `yes` |
| `environment/second_pc/screenshots/S022_preview_marker_absent.png` | S022 提交同一 marker 后的独立 `preview.php` | 页面 DOM 未出现 `data-lab-xss` 属性，正文显示为编码文本 |

S021/S022 留证用的临时草稿已在截图和 DOM 读取完成后重置；临时标题为 `Second-PC-S021-20261021`、`Second-PC-S022-20261021` 及 console 复核标题，不保留为正式数据。

## DevTools 无桌面替代证据

当前 Codex 可控浏览器没有可绑定的原生 DevTools 桌面窗口，因此没有伪造 Console 截图。按 D 指南中的无桌面替代方案，保存了真实 DOM 读取结果：

- `environment/second_pc/screenshots/S021_console_dom.json`：表达式 `document.documentElement.dataset.labXss`，值为 `yes`。
- `environment/second_pc/screenshots/S022_console_dom.json`：同一表达式，值为字符串记录的 `undefined`，类型为 `undefined`。

这两个 JSON 是 headless 浏览器实际执行表达式后的结果，不是模型输出，也不是人工填写的结论。

## 边界与后续

- 本轮形成浏览器视觉证据及 DevTools Console 的无桌面替代 DOM JSON，未声称完成 60–90 秒录屏。
- 本轮未生成新的模型运行或正式 POC 触发结论。
- 若课程要求完整“第二台电脑复现”包，仍需在独立机器上补齐 `version.txt`、`services.txt`、`runtime_check.json`、Docker 服务截图和录屏，并记录机器/时间/提交号。
