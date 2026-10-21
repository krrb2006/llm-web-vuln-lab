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

S021/S022 留证用的临时草稿已在截图完成后重置；临时标题为 `Second-PC-S021-20261021` 和 `Second-PC-S022-20261021`，不保留为正式数据。

## 边界与后续

- 本轮只形成浏览器视觉证据，未声称完成 60–90 秒录屏。
- 本轮未生成新的模型运行或正式 POC 触发结论。
- 若课程要求完整“第二台电脑复现”包，仍需在独立机器上补齐 `version.txt`、`services.txt`、`runtime_check.json`、Docker 服务截图和录屏，并记录机器/时间/提交号。
