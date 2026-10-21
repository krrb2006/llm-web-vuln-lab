# 第二台电脑复现：截图与录屏操作指南（给 A）

适用：Windows 11 + Docker Desktop + Edge。目标是把第二台电脑复现的证据补齐为 **6 张截图 + 1 段 60–90 秒录屏**，不需要重跑模型或 POC。

## 一、需要交什么

| 编号 | 内容 | 证明什么 |
|---|---|---|
| 01 | Docker Desktop 容器页，或 `docker compose ps` | dvwa/db 在跑，端口 4280 |
| 02 | `check_runtime` 输出 37/37 | 源码/容器哈希一致 |
| 03 | S009 `ids=1`，页面只有 Alice 1 行 | 普通请求 |
| 04 | S009 受控 `ids=1) OR 1=1 #`，页面 3 行 | 条件变化 |
| 05 | S021 preview + DevTools Console 显示 `"yes"` | marker 执行 |
| 06 | S022 preview + Console 显示 `undefined` | 修复版不执行 |
| 视频 | 60–90 秒，串起 01→06 | 现场复现过程 |

不需要露账号、邮箱、聊天窗口；只需要本机 `127.0.0.1:4280`。

## 二、截图通用操作

### 方法 1：Win+Shift+S（推荐）

1. 把要截的窗口放在最前；
2. 按 `Win + Shift + S`；
3. 选“矩形”或“窗口”；
4. 截图进入剪贴板，右下角出现预览；
5. 点预览 → `Ctrl + S`；
6. 保存到：
   ```text
   environment/second_pc/screenshots/
   ```
7. 文件名：
   ```text
   01_docker_ps.png
   02_runtime_37.png
   03_s009_normal.png
   04_s009_controlled.png
   05_s021_marker.png
   06_s022_no_marker.png
   ```

### 方法 2：Win+PrtScn

全屏截图，自动保存到 `图片\屏幕截图`；之后裁剪掉不相关部分。

### 隐私检查

- 先关掉微信/QQ/邮箱/聊天窗口；
- 截图里不要出现用户名、邮箱、桌面文件名；
- 侧边栏有账号名时，用截图工具裁剪或打码；
- 只保留 `127.0.0.1:4280`、终端命令和结果。

## 三、逐张怎么截

### 01 Docker 容器

PowerShell：

```powershell
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml ps
```

截 PowerShell 窗口，确保能看到：

- `dvwa-dvwa-1` / `dvwa-db-1`
- `Up`
- `127.0.0.1:4280->80/tcp`

或者打开 Docker Desktop → Containers，截两个容器 Running 的页面。

### 02 runtime 37/37

```powershell
python environment/check_runtime.py --a-ref HEAD --c-ref HEAD --d-ref HEAD
```

截最后几行，确保能看到：

```text
Runtime check: 37/37 PHP files passed.
```

最好把上面的命令也截进去，证明不是旧输出。

### 03 S009 普通请求（1 行）

浏览器打开：

```text
http://127.0.0.1:4280/lab_cases/S009/index.php?ids=1
```

页面应只有：

```text
ID 1：Alice
```

截图保留地址栏（能看到 `127.0.0.1:4280` 和 `ids=1`）。

或者 PowerShell：

```powershell
curl.exe -sS "http://127.0.0.1:4280/lab_cases/S009/index.php?ids=1"
```

截终端输出。

### 04 S009 受控条件（3 行）

浏览器打开（`#` 编码为 `%23`）：

```text
http://127.0.0.1:4280/lab_cases/S009/index.php?ids=1%29+OR+1%3D1+%23
```

页面应出现：

```text
ID 1：Alice
ID 2：Bob
ID 3：Carol
```

截图保留地址栏和 3 行结果。

### 05 S021 marker=yes（关键）

1. 打开：
   ```text
   http://127.0.0.1:4280/lab_cases/S021/submit.php
   ```
2. 标题填唯一值，例如 `SecondPC_S021_20261021`；
3. 正文填：
   ```html
   <script>document.documentElement.dataset.labXss='yes'</script>
   ```
4. 提交 → 进入 list → 点开刚提交的草稿 preview；
5. 按 `F12` 打开 DevTools，切到 **Console**；
6. 输入并回车：
   ```js
   document.documentElement.dataset.labXss
   ```
   应返回 `"yes"`；
7. 截图时同时拍到：
   - 地址栏 `preview.php?id=...`
   - 页面标题/正文
   - Console 里的 `"yes"`

> 页面本身不一定有可见变化；**Console 输出才是 marker 执行的证据**，只截页面不够。

### 06 S022 marker 不执行（对照）

1. 打开：
   ```text
   http://127.0.0.1:4280/lab_cases/S022/submit.php
   ```
2. 同样提交 marker 正文；
3. 进入 preview；
4. Console 输入：
   ```js
   document.documentElement.dataset.labXss
   ```
   应返回 `undefined`；
5. 截图同时包含地址栏、转义后的页面和 Console 的 `undefined`。

### 可选：S011 排序

```text
http://127.0.0.1:4280/lab_cases/S011/index.php?sort=id
http://127.0.0.1:4280/lab_cases/S011/index.php?sort=%28id%3D2%29+DESC%2C+id+ASC
```

截正常顺序和测试顺序的对比。

## 四、60–90 秒录屏

### 方法 1：Xbox Game Bar

1. `Win + G`；
2. 点 **Capture** → **Start recording**；
3. 或 `Win + Alt + R` 开始/停止；
4. 录完在 `视频\Captures` 下找 `.mp4`；
5. 复制到：
   ```text
   environment/second_pc/second_pc_recording.mp4
   ```

### 方法 2：Windows 11 截图工具的视频录制

1. `Win + Shift + S`；
2. 工具栏切到“录制视频”（摄像机图标，若系统版本支持）；
3. 选区域 → 开始录制 → 保存 mp4。

### 方法 3：PowerPoint

新建 PPT → 插入 → 屏幕录制 → 选区域 → 录制 → 另存为 mp4。

### 90 秒脚本

| 时间 | 画面 |
|---|---|
| 0–10s | PowerShell：`docker compose ... ps`，两个容器 Up |
| 10–20s | `python environment/check_runtime.py ...`，滚动到 `37/37` |
| 20–35s | 浏览器 S009 `ids=1`，只有 Alice |
| 35–50s | 浏览器 S009 受控条件，出现 Alice/Bob/Carol 3 行 |
| 50–65s | S021 提交 marker → preview → F12 Console 显示 `"yes"` |
| 65–80s | S022 同样操作，Console 显示 `undefined` |
| 80–90s | `git rev-parse HEAD`，显示 `34b36ad…` |

不用配音；录屏前关掉聊天窗口，别露账号。

## 五、如果机器是远程/无桌面

- **截图**：终端输出可以直接保存文本（`... | Tee-Object`），比截图更稳；
- 页面可以用 headless Edge：
  ```powershell
  & "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
    --headless=new --disable-gpu --window-size=1400,900 `
    --screenshot="environment\second_pc\screenshots\s021_preview.png" `
    "http://127.0.0.1:4280/lab_cases/S021/preview.php?id=<id>"
  ```
  但 headless 截图看不到 Console；marker 证据用 `check_d_browser.mjs` 生成的 `browser_reference.json`（`html_data_lab_xss=yes/no`）替代，并在报告里说明；
- **录屏**：如果完全没有桌面/录制权限，就在报告里写“无法录屏，原因：远程无桌面/权限限制”，不要用 D 的旧视频冒充；这不是主实验阻塞项。

## 六、保存与提交

目录：

```text
environment/second_pc/
  screenshots/
    01_docker_ps.png
    02_runtime_37.png
    03_s009_normal.png
    04_s009_controlled.png
    05_s021_marker.png
    06_s022_no_marker.png
  second_pc_recording.mp4
  README.md
```

然后在 `results/A_second_pc_repro_2026-10-20.md` 补一行：

```text
补充证据：environment/second_pc/screenshots/01–06、second_pc_recording.mp4；
录屏时长 85 秒；截图未包含账号信息。
```

## 七、完成检查

- [ ] 6 张截图都能看清命令/URL/结果；
- [ ] S021 截图里有 Console 的 `"yes"`，S022 有 `undefined`；
- [ ] 录屏 60–90 秒，能看清 S009 1→3 行；
- [ ] 截图/录屏没有账号、邮箱、聊天窗口；
- [ ] 文件已放到 `environment/second_pc/`，报告已补路径。
