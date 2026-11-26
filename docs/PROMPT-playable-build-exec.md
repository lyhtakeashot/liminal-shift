# L21 · 可玩构建线（Windows 包 → 字体 → Web）

> 立线理由（2026-11-26 实测，不是猜的）：
> 1. 仓库**从来没有导出过**：`export_presets.cfg` 不存在；`%APPDATA%\Godot\export_templates` **不存在**。
>    比赛要的是「能点开就玩」的构建，这是唯一的硬门槛，而且全队没一个人走过这条路。
> 2. **默认字体没有中文字形**：`ThemeDB.fallback_font` = `FontFile "Open Sans SemiBold"`，
>    `has_char("沈") = false`、`has_char("「") = false`，靠 `allow_system_fallback=true` 在桌面
>    从系统字体抓字形。**Web 导出没有系统字体** ⇒ 整屏中文变豆腐块。这条今天必须解决，
>    否则 Web 版上线当天才发现，就来不及了。
>
> 结论：**先出 Windows 包（保底可玩，绕开字体问题），再做字体，最后 Web（体验最好但有新风险）**。
> 顺序不许调换 —— 先拿到「能玩的东西」，再追「更好玩的方式」。

---

## 0. 你是哪条线、不能碰什么

| | |
|---|---|
| **可以写** | `export_presets.cfg`、`tools/build_*.ps1`、`assets/fonts/**`、`docs/BUILD.md`、`_mdtest/build_check.gd`、`project.godot` 里**只** `gui/theme/*` 与 `application/config/name` 两处 |
| **绝对不能碰** | `scripts/**`、`data/**`、`scenes/**`、`_ref/**`、`assets/village/**`、`assets/audio/**`、`docs/` 下除 `BUILD.md` 以外的任何文件 |
| **不能并行** | 任何同时在改 `project.godot` 的线（本线独占 `project.godot`）|
| **不改** | 不新增依赖、不改渲染后端（`gl_compatibility` 是 Web 唯一正确选择，别改成 forward_plus）|

---

## 1. Stage A · Windows 可执行包（先做这个，今天必须出）

### A1. 装导出模板（**需要联网，用户做**）

Godot 4.7.2.stable（steam 版）。模板必须**版本号完全一致**，否则导出报
`No export template found`。

两条路任选：
- 编辑器里：`编辑器 → 管理导出模板 → 下载并安装`（最省事）
- 手动：`https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_export_templates.tpz`
  解压后整目录放到 `%APPDATA%\Godot\export_templates\4.7.2.stable\`

**验证**（必须看到 `4.7.2.stable` 目录里有 `windows_release_x86_64.exe`）：
```powershell
Get-ChildItem "$env:APPDATA\Godot\export_templates" -Recurse -Filter "windows_release_x86_64.exe"
```

### A2. 建 Windows 预设

`export_presets.cfg` 是本线的产物，手写即可（不要用编辑器 GUI 点，那样没法 review）。
最小可用内容：`platform="Windows Desktop"`、`export_path="build/windows/shift.exe"`、
`runnable=true`、`embed_pck=true`（单文件，发给评委不用带一堆东西）、
`binary_format/embed_pck=true`、`application/product_name="SHIFT"`。

### A3. 出包 + 自证能跑

```powershell
git rev-parse --short HEAD                      # 先记下这个 hash，反馈里要写
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . --export-release "Windows Desktop" "build/windows/shift.exe"
```

导出后**必须做三件自证**（写进反馈，缺一条算没做完）：

1. **文件存在且像样**：`shift.exe` ≥ 40MB（`embed_pck=true` 时 pck 在里面）。
2. **真的能跑起来**：`& .\build\windows\shift.exe --quit-after 240` 不让它崩，
   stderr 里除了
   - `Failed to read the root certificate store.`
   - `user://logs` / `Failed to open log file`
   这两类**环境噪音**之外，不许出现任何 `SCRIPT ERROR` / `Invalid` / `Cannot`。
3. **黑盒截图**：跑 `_mdtest/greybox_shot.gd` 那套之前先不要求 —— 但**必须**让
   **用户双击 `build/windows/shift.exe` 玩一次**，因为本机沙箱能跑 ≠ 别的机器能跑。
   反馈里写明「已请用户真机双击」。

### A4. 一键重建脚本

`tools/build_windows.ps1`：读 HEAD hash → 清 `build/windows/` → 导出 → 三件自证 →
把 hash 与文件大小打印出来。做到「任何人一条命令复现这个包」。

---

## 2. Stage B · 字体（**Web 的前置，桌面观感必须零变化**）

### 为什么要做

见文首第 2 条。桌面上中文是从系统字体抓的，**换一台没有该字体的机器、或者上 Web，就是豆腐块**。
另外比赛评委可能用 Linux/Mac，这些机器上的中文字体未必是黑体。

### 怎么做（关键：用 fallback 链，不改任何现有字号/排版）

1. 下载 **Noto Sans SC**（OFL 许可，可随游戏分发）：
   `https://github.com/notofonts/noto-cjk/releases` 或 Google Fonts 的 `NotoSansSC`。
   **不许用微软雅黑/宋体**（Windows 系统字体，不能随包分发）。
   放到 `assets/fonts/NotoSansSC-Regular.otf`（+ `-Bold.otf`）。
2. 做**子集**（可选但强烈建议）：全量 Noto Sans SC 约 10MB，Web 首屏要下这个很痛。
   游戏用到的汉字是有限的（`data/frames.json` + `scripts/*.gd` + `docs/npc.md` 台词里的字），
   用 `fonttools` 收一遍，通常能压到 300KB 以内。
   ```powershell
   pip install fonttools
   pyftsubset assets/fonts/NotoSansSC-Regular.otf --text-file=build/_used_chars.txt --output-file=assets/fonts/NotoSansSC-subset.otf
   ```
   收集用字的脚本自己写（扫 `data/**`、`scripts/**`、`docs/npc.md`，把全部非 ASCII 字符去重）。
   **注意**：字表必须包含归档表/结局界面用到的字，跑完用 `_mdtest/build_check.gd` 全量扫一遍再说。
3. 在 `project.godot` 里建 fallback 链（**唯一允许改的 project.godot 位置**）：
   ```ini
   [gui]
   theme/custom_font="res://assets/fonts/font_chain.tres"
   ```
   `font_chain.tres` 是一个 `FontVariation` 或 `SystemFont`？——
   **正确做法**：建 `assets/fonts/font_chain.tres`，类型 `FontFile` 指向 Open Sans
   （把引擎默认字体导出一份），`fallbacks` 数组里塞 Noto Sans SC 子集。
   这样：拉丁字符走 Open Sans（**和现在一模一样**），中文落到 Noto。
4. 验收（B 的硬项）：
   - **B1** 桌面窗口截图与改动前**逐像素不可区分**（同帧同位置，用 python 比对，容差 0；
     若真有差，必须能一句话解释哪几个字变了、为什么）。
   - **B2** `has_char("沈")` 由 false 变 true，且 `get_string_size` 与改动前**同一字号下差 <1px**。
   - **B3** 用一张**没有系统中文**的证明：临时把 `assets/fonts/` 之外的系统字体路径屏蔽不可行，
     改为断言之：`_mdtest/build_check.gd` 里断言「渲染中文时用到的是我们嵌的字形」
     （用 `Font.has_char` + 子集字表比对，可证）。

---

## 3. Stage C · Web 导出（**有余量才做，做了就比 Windows 包强一档**）

先决条件：A 与 B 都过。Web 特有的四个坑，逐条验：

- **C1 音频要用户手势**：浏览器不允许自动播音频。`Aud` 初始化必须在第一次点击/按键之后，
  否则 `AudioServer` 静默失败。验：导出后在浏览器里先点一下画面，再走动，能听见脚步。
- **C2 `user://` 存到 IndexedDB**：`evidence_archive.json` 能存能读（关卡刷新后证物还在）。
  验：收一个证物 → F5 刷新 → 还在。
- **C3 字体**：整屏中文无豆腐块（B 的成果）。
- **C4 性能**：`Props` 那层 1583 个节点 + `_draw()` 现画，Web 上帧率可能垮。
  验：浏览器里走动不卡（体感），且 `Engine.get_frames_per_second()` ≥ 30（打印一次）。
  宁可降分辨率也不要卡：`window/stretch/mode="canvas_items"` 已经是正确设置，别动。
- **C5 导出体积**：`build/web/index.wasm` + `index.pck` 合计目标 < 80MB（itch 单文件上限 1GB，
  但评委下载耐心有限）。

导出命令：
```powershell
& $godot --headless --path . --export-release "Web" "build/web/index.html"
```
本地起服务验证（**必须 http，不能 file://**）：
```powershell
python -m http.server 8080 --directory build/web
```

---

## 4. 验收总表

| 编号 | 项 | 判据 |
|---|---|---|
| **A1** | 导出模板 | `4.7.2.stable/windows_release_x86_64.exe` 存在 |
| **A2** | Windows 包 | `build/windows/shift.exe` 存在且 ≥40MB |
| **A3** | 能跑 | `--quit-after 240` 零 `SCRIPT ERROR` |
| **A4** | 用户真机双击 | 反馈里写明结果 |
| **A5** | 一键重建 | `tools/build_windows.ps1` 一条命令复现 |
| **B1** | 桌面观感零变化 | 截图像素比对容差 0 |
| **B2** | 中文字形自带 | `has_char("沈")=true` |
| **B3** | 子集覆盖 | 全项目用字 100% 命中 |
| **C1** | Web 音频 | 点击后能听见 |
| **C2** | Web 存档 | 刷新后证物还在 |
| **C3** | Web 中文 | 无豆腐块 |
| **C4** | Web 性能 | ≥30fps |
| **C5** | 体积 | wasm+pck < 80MB |

**不做**：Linux/Mac 包（评委多数 Windows，且 Mac 包要签名，成本高收益低）、Steam/itch 上传
（那是发布线，另立）、自动更新、图标美化（`application/config/icon` 现在是空的话随手加一个也行，不是验收项）。

---

## 5. 反馈格式

写 `docs/FEEDBACK-playable-build-exec.md`，必须含：

1. HEAD hash（开工时与交付时各一个）。
2. A1–A5 / B1–B3 / C1–C5 逐条「实测输出」（贴关键行，不要写「已验证」四个字）。
3. **明确写出哪几条没做、为什么**（例：C 段没做因为模板下载失败）。
4. 任何一条「我以为是好的但其实没验」的地方，必须标出来 —— 这条线最怕的就是
   「导出成功」四个字背后的静默失败。

---

## 6. 环境与坑（照抄，别自创）

```powershell
$godot = "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe"
$py    = "C:\Users\lyh\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
```

- 统计行数别用 `(Get-Content).Count`（UTF-8 文件会少算），用 python。
- 别用 `python -` 走 stdin 传中文脚本（GBK 解码会崩），先写成 `.py` 再跑。
- `git add` 只加本线白名单里的文件，**绝不 `git add -A`**（工作区里有别人 900+ 个未跟踪文件）。
- **不要 push**（push 由用户定时做）。
- 导出产物 `build/**` 要不要入库？**不入库** —— 在仓库根 `.gitignore` 里忽略 `build/`，
  反馈里写清「体积大、可复现、不入库」。