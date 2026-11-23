# PROMPT · 证物存档 UI 线（逆转裁判式证据档案）

**任务**：给游戏实现「证物存档 / 证据档案界面」，采用**逆转裁判的证物清单方案**。
玩家用 E 检视热点时，不仅弹出文字，还把该证物**收集入档**；按一个键打开档案界面，
随时查看已收集的证物（名称 + 描述 + 来源），跨时间轴、跨移动都持久保留。

**项目路径**：`D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift`
**开工基准**：HEAD `f6b3e9e`（`feat: 补齐 A4/A5 六栋证物检视文案（CLUE_TEXTS）`）。开工前先 `git status` 确认 `scripts/*.gd` 无他人改动；若 HEAD 不是 `f6b3e9e`，先向总策划确认。
**Godot 可执行**：`D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`
**运行**：`godot.windows.opt.tools.64.exe --path . scenes/main.tscn`（**必须去掉 `--headless`**，否则看不到界面）。

---

## §0 先读这段：现状与边界（已实测，别凭印象改）

### 0.1 E 键与检视现已存在，不用重做
- `scripts/main.gd:102-103` 绑定 `inspect` 动作；`_do_inspect()` 在 `scripts/main.gd:187-195`，调 `tl.current().hotspot_at(tl.char_pos)`，命中后 `_last_hotspot = h` + `hud.show_hotspot(h)`。
- `scripts/hud.gd:47-55` `show_hotspot()` 存 title/text，`:141-167` `_draw_hotspot()` 把文本画在屏幕上——**当前只是一次性弹文字，无持久化**。
- `scripts/house_shape.gd:378-406` `hotspots()` 从 `houses_data.json` 的家具 `clue:true` 生成检视点，**文本取 `CLUE_TEXTS[house_id][furniture_name]`**，缺省退回「「X」立在这里。」。
- **结论**：E 键是既有功能。本线做的是「**检视时入档 + 打开档案界面**」，不改 E 键的检视逻辑本身，只给它**加一个收集动作**。

### 0.2 证物文案线已完成，文本直接可用
- `scripts/house_shape.gd:46-109` `CLUE_TEXTS` 已覆盖 A1–A5 全部 18 栋的 clue 家具文案（A4/A5 刚在 `f6b3e9e` 补齐）。**本线只读取 `CLUE_TEXTS`，禁止改写文案内容**。

### 0.3 证物来源分两类
1. **房屋家具证物**：`house_shape.gd:hotspots()` 生成的热点，键 = 房子 `id` + 家具 `name`，文本 = `CLUE_TEXTS` 对应条目。来源标签 = 房子名 + 时代。
2. **世界地标证物**：`data/frames.json` 各帧手写的 `hotspots`（如老井、老槐、界碑），文本 = 热点的 `text` 字段，标题 = 热点的 `title`。来源标签 = 时代 + 地名。

两类都入档。地标热点结构见 frames.json 的 `{"pos":[..],"title":"..","reach":..,"text":".."}`。

---

## §1 设计（逆转裁判式）

### 1.1 档案界面（证物清单）
- 按 **I 键**（或 Ctrl+I，二选一，见 §3）打开；再按关闭。打开时**暂停游戏逻辑**（不响应行走 / 时间轴），只响应档案界面自身的按键。
- 界面风格对齐现有 `scripts/hud.gd`：像素 UI、`UI` 缩放变量、`draw_rect` 底框 + 边框、`draw_string` 文字，1280×720 视口。
- 布局：
  - 顶部标题栏「证物档案 · 证据清单」+ 已收集数量。
  - 中间是**条目列表**，每条一张卡：
    - **名称**（证物名，如「账簿」/「石磨」/「老井」）
    - **来源**（如「磨坊 · 1926」）
    - **描述摘要**（`CLUE_TEXTS` / 地标 `text` 的前若干字，超长截断，详情页看全文）
  - 选中条目高亮；Enter 或点击进入**详情页**（名称 + 完整描述 + 来源，可翻页/滚动）。
  - 列表按**收集先后**排序（先收集的在前），新证据加在末尾并有视觉提示。
  - 未收集的证物**不显示**（逆转裁判是收集后才可见，不要提前剧透）。

### 1.2 收集触发
- E 检视命中热点时：
  - 先保留现有「弹文字」行为不变（`hud.show_hotspot`）。
  - **首次**收集该证物：写入档案（条目 + 来源 + 文本），界面给一次「已收集」提示（如底部闪一行字，不打断检视文字）。
  - **再次**检视：只弹文字，**不重复入档**（去重）。
- 收集是**会话内持久**的：走路、切时间轴、切时代都不丢。

### 1.3 持久化（推荐，Game Off 范围内尽量做）
- 运行时状态存内存（单例）。
- 额外用 `DirectoryAccess` 把档案 JSON 存到 `UserDir`（`get_user_data_dir()`），启动时读回；保存时机 = 收集时或切时间轴时。文件名如 `evidence_archive.json`。**若为了省事只做内存持久也可接受，但必须在交付说明里写明「未做跨启动存档」。**

---

## §2 实现方案（文件与改动）

### 2.1 新增文件（优先做，避免动别人代码）
- **`scripts/evidence_store.gd`**：证物存档管理（推荐做成 `static class` 或 `autoload` 单例）。职责：
  - 条目数据：`{key, name, source, text, order}`；`key` 唯一（房屋家具用 `house_id::furniture_name`，地标用 `title`）。
  - `try_collect(key, name, source, text)`：去重收集，返回是否新收集。
  - `get_entries()`：按收集顺序返回列表。
  - `is_collected(key)`、`clear()`（测试用）。
  - `save()` / `load()`：JSON 读写（若做持久化）。
- **`scripts/evidence_archive.gd`**：档案界面节点（`CanvasLayer` 或挂 UI 层）。职责：
  - `show()` / `hide()` / `toggle()`，`visible` 控制开合。
  - 列表与详情两态渲染，处理 `I`/ESC/方向键/Enter。
  - 打开时暂停主循环输入（通过给 main 或本节点设标志，见 §3）。
- **`_mdtest/evidence_archive_check.gd`**：新自测（见 §5）。

### 2.2 修改文件（改动要小、要克制）
- **`scripts/main.gd`**：
  - 在 `_process()` 里加一个 `I`（或选定键）的边沿检测 → 调 `evidence_archive.toggle()`。
  - 在 `_do_inspect()`（`main.gd:187-195`）命中热点后，调 `evidence_store.try_collect(...)` 入档。**保留原 `hud.show_hotspot` 逻辑不动**，只在其后追加收集调用。
  - 档案界面打开期间，暂停行走/时间轴处理（可在 `_process_space/_process_time` 开头加 `if evidence_archive.is_open(): return`，或用一个 `paused` 标志）。
- **`project.godot`**：**仅当选择用输入映射时**，在 `[input]` 段加一个 `archive` 动作（绑定 I 或 Ctrl+I）。这是本线对 `project.godot` 的唯一改动，只新增不改删。**若用 `Input.is_key_just_pressed(KEY_I)` 原始键检测，则完全不动 `project.godot`。**

### 2.3 不要碰
- `houses_data.json`、`data/frames.json`（只读）。
- `scripts/house_shape.gd` 的 `CLUE_TEXTS` 文案（只读，刚由证物文案线交付）。
- `assets/`、`_ref/`、`scenes/main.tscn` 的结构。
- 视觉机制线已交付的排序 / 南墙半高逻辑，不动。

---

## §3 键位与输入处理（二选一，建议第一种）
1. **推荐**：新增输入动作 `archive`，绑定 `I` 键。开档案界面时主循环暂停输入。
2. **省事**：`Input.is_key_just_pressed(KEY_I)` 原始键检测，不开新动作。
两种都写清楚选了哪个。**不要和现有 `inspect`(E)、`move_*`(WASD/方向)、时间轴冲突。**

---

## §4 验收

1. **开档**：按 I → 档案界面打开，初始为空列表（0 件），标题显示数量。
2. **收集**：走到磨坊 A1（`mill_a1`）账桌旁，按 E → 弹出文案，且档案里出现「账簿」条目（来源「磨坊 · 1926」）。
3. **持久**：走开、按 SHIFT 切时间轴再切回、切时代，档案条目仍在；再按 E 检视同一证物，**不新增重复条目**。
4. **详情**：列表选中条目按 Enter → 显示完整描述与来源。
5. **关闭**：按 I 关闭，恢复游戏输入。
6. **回归**：跑 `_mdtest/` 现有套件（greybox / camera / display / hud_layout / asset_draw）+ 新 `evidence_archive_check.gd`，看关键字（`EVIDENCE_OK` / `COLLECTED` / `NO_DUP`），**不看退出码**（沙箱固有 `Failed to read the root certificate store.` / `[exit code:1]` 是噪声）。
7. **截图**：交付前用非 headless 运行，截 1 张「档案界面打开、有 2 条以上条目」的图，与一张「E 检视刚收集」的图，`present` 给用户确认。

## §5 新测试 `_mdtest/evidence_archive_check.gd`
- 直接调 `EvidenceStore`（或等价入口），断言：空档案 → `try_collect` 返回 true 且条目数 1 → 同 key 再 collect 返回 false 且条目数不变 → `get_entries()` 顺序 = 收集顺序 → `save/load` 往返后条目一致（若做持久化）。
- 末行打印 `EVIDENCE_OK`，结束时自检 `fails == 0`。

## §6 提交纪律
- 只 `git add` 自己新增/修改的这几个文件：`scripts/evidence_store.gd`、`scripts/evidence_archive.gd`、`scripts/main.gd`、`_mdtest/evidence_archive_check.gd`、（若加动作）`project.godot`。
- **严禁 `git add -A`**：工作区有别的线的产物（`_ref/art/*` 的 M、用户删的 `美术资产/` 旧图 D 等），一个都不要带。
- 提交信息：`feat(evidence): 逆转裁判式证物存档界面与收集逻辑`。

## §7 交付前自述
- 说明选了哪种键位、是否做了跨启动存档、收集触发是否保留原检视弹字、回归关键字全绿、截图 2 张路径。
- 如有取舍（如未做跨启动存档），如实说明，不要隐瞒。
