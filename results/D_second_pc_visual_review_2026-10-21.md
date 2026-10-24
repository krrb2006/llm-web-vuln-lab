# D 复核：A 的第二台电脑视觉证据（2026-10-21）

复核人：D　执行人：A　基线：`a/criteria-and-sql01@eb78bea`（A 最终收口）

## 一、A 补了什么

A 在 2026-10-21 新增：

- `environment/second_pc/screenshots/` 下 6 张页面截图：
  - `S009_normal_ids1.png`、`S009_controlled_3rows.png`
  - `S011_normal_id.png`、`S011_controlled_name_desc.png`
  - `S021_preview_marker_yes.png`、`S022_preview_marker_absent.png`
- `S021_console_dom.json`、`S022_console_dom.json`：headless 浏览器执行
  `document.documentElement.dataset.labXss` 的结果，分别为 `"yes"` 和 `"undefined"`。

A 的最终收口 `eb78bea` 记录加分证据 14/26：S013 8 条 `reviewed`、Burp 2、CTX 4；剩余 8 条 `planned` 是 `INJ_SQLI_*`（S001 的 SQL 注入计划），S001/S004 的 8 条 Original/Injected 是计划外探索，不计入 26 条计划。两者不要混写。

## 二、内容核对

- S009 受控截图显示 Alice/Bob/Carol 3 行；S009 普通截图显示 Alice 1 行。
- S011 两张截图显示行序 `1,2,3` 与 `3,2,1` 的差异，排序变化可见。
- S021/S022 截图是 preview 页面；页面本身不会显示 `data-lab-xss`，marker 证据以两份 DOM JSON 为准：S021=`"yes"`、S022=`"undefined"`，与报告一致。
- 6 张截图是 headless 页面渲染，**没有地址栏、没有 Docker/runtime 输出、没有 DevTools Console**；S009 受控与 S011 普通截图因渲染内容相同而字节相同，只能靠文件名和 A 的报告区分，不能仅凭截图判断是哪个样本。

## 三、发现的技术问题

1. **文件格式与扩展名不符**：6 个 `.png` 文件实际是 JPEG（`FF D8 FF E0 ... JFIF`），部分图片查看器/工具会拒绝读取。D 已在本 PR 中把它们**无损转成真正的 PNG**（仅格式转换，页面内容不变，路径不变）。
2. **仍缺 Docker/runtime 截图、DevTools Console 截图、60–90 秒录屏**。这些不是主实验阻塞项，但意味着“环境/录屏”证据仍不完整。
3. A 的 `results/A_second_pc_visual_evidence_2026-10-21.md` 对限制写得很清楚，没有把 DOM JSON 说成截图，也没有复用 D 的旧图。

## 四、结论

- **接受这批视觉证据为第二台电脑复现的补充材料**：页面输出、排序变化、S021/S022 的 DOM marker 都能对上；
- 仍然保留此前限制：无 Docker/runtime 截图、无 Console 截图、无 60–90 秒录屏；
- 如果课程要求更完整，建议 A 补 Docker/`runtime_check` 截图和一段 60–90 秒录屏；不补也不影响 36 条主实验；
- A 的 final closeout 已如实记录“第二台电脑材料采用 headless 截图/DOM JSON、未补 60–90 秒录屏”；本复核作为补充，不改变该限制。

## 五、签字

D（linan / linan-prog，2986713478@qq.com）　2026-10-21 11:10（UTC+8）
