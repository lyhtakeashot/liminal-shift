# L12 · 界面与手感执行任务书（小地图 + 提速 + 走路动画频率）

> 这份是**执行线**的任务书。执行的人（新会话）不需要读我（总策划）的对话历史，照本文件做即可。
> 本文件里每一条数字要么来自实测，要么来自用户 2026-11-25 的逐条拍板。**没有依据的数字不要自己编。**
>
> **本线只碰界面与手感三个脚本 + 一个测试文件，文件域与 L11（数据与地图引擎）、L13（叙事文本）零重叠，可同时开。**
>
> - **L11 世界重排**（`docs/PROMPT-l11-world-rebuild-exec.md`）＝ 改 `data/frames.json` ＋ `scripts/world_view.gd` ＋ `scripts/frame_data.gd`。
> - **L13 树井文案与倾斜叙事删除**（`docs/PROMPT-l11c-text-exec.md`）＝ 只碰 `docs/story.md`／`docs/npc.md`／`docs/HANDOFF.md`。
>
> ⚠️ 但 **L11 会把世界从 3200×2400 放大到 4800×3600**，本线的「小地图要显示世界缩略图」必须按 **4800×3600** 写死（或从数据读），不要按旧的 3200×2400 写。

---

## §0 开工前

### 0.1 基线与依赖

| 项 | 值 |
| --- | --- |
| 开工要求的 HEAD | `92078cb`（或其后；2026-11-25 11:05 的进度快照提交） |
| 反馈文档（必须写） | `docs/FEEDBACK-l11b-ui-exec.md`，≤100 行 |
| 依赖 | **不依赖 L11 的代码**。但世界尺寸按 **4800×3600** 写（用户 M7 已拍板，L11 正在改 `data/frames.json`）。若 L11 尚未落地，你的小地图仍可用旧世界尺寸跑，**但要按 4800×3600 写死常量并注释说明**。 |

**开工前必须先读**：
1. 本任务书全文。
2. `docs/待解决事项.md` §1.3（M6：提速 + 小地图）与 §1.2 M7（世界放大按甲方案）。
3. `scripts/hud.gd`（195 行，全文很短，**先读完再动手**）。
4. `scripts/main.gd` 的 `:96-190`（`_process`）、`:322-337`（`_refresh_all`）。
5. `scripts/player.gd` 的 `:1-100`。
6. `_mdtest/hud_layout_check.gd`（89 行，全文）。

### 0.2 能改 / 不能碰

**能改（白名单）**：

| 文件 | 改什么 |
| --- | --- |
| `scripts/hud.gd` | ①加小地图的绘制与状态 ②新增 `sync_player(pos)` 之类的接口 |
| `scripts/main.gd` | ①每帧把玩家坐标喂给 HUD ②`PLAYER_SPEED` 120→180 |
| `scripts/player.gd` | 走路动画频率 9.0→6.0 |
| `_mdtest/hud_layout_check.gd` | **只许加**小地图自己的断言（既有断言一条都不许改） |

**不能碰（一律不许改）**：

- `data/frames.json`（**归 L11**：世界尺寸、五帧数据、热点文案）
- `scripts/world_view.gd`（**归 L11**：地图绘制、平铺贴图、decor 房子）
- `scripts/frame_data.gd`（**归 L11**：碰撞与热点生成）
- `scripts/house_shape.gd`（证物文案与家具热点）
- `scripts/evidence_store.gd`／`scripts/evidence_archive.gd`（证物模型）
- `scripts/timeline.gd`／`scripts/camera_rig.gd`／`scripts/asset_draw.gd`／`scripts/display_manager.gd`
- `docs/story.md`／`docs/npc.md`／`docs/HANDOFF.md`（**归 L13**）
- `_mdtest/**` 里除 `hud_layout_check.gd` 之外的任何文件
- `_mdtest/hud_layout_check.gd` 的**既有断言**（`:38` 字号、`:53/:54/:55` 顶条三段、`:58` 顶条高、`:64/:67/:68` 底条、`:74` 提示字宽、`:85/:86` 检视卡）
- `assets/**`、`_ref/**`、`_ref/houses/**`

**不要动别人的工作区**：仓库里有美术线未提交的 PNG（`_ref/art/A1..A3/*.png`）、用户自己删掉的 `美术资产/` 一批文件、大批未跟踪的 `lab/_*`。**只用精确 `git add <文件>`，绝不用 `git add -A`。**

### 0.3 跑 Godot 的正确姿势（Windows + 沙箱）

```powershell
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . -s res://_mdtest/hud_layout_check.gd 2>&1 | Select-Object -Last 45
```

- **看关键字，不看退出码**。沙箱固有噪声：`Failed to read the root certificate store.`、`Failed to open 'user://logs/godot...log'`。成功标志是脚本自己打的 `HUD_CHECK_DONE fails=0`。
- `cmd /c "..."` 会被路径里的空格截断；`> out.txt` 在本机会产出 0 字节文件 ⇒ **一律用内联管道**。
- 本线至少要跑这一套：`hud_layout_check`。**建议顺手跑全套**（七套，见 §4.3），因为提速会动到 `main.gd` 的 `PLAYER_SPEED`，而 `greybox_check` 里有一堆依赖坐标的断言。

### 0.4 四个坑（踩过就别再踩）

1. **HUD 三块已被测试钉死**：`scripts/hud.gd` 的顶条（36px，`:88-108`）、底条（60px，`:110-139`）、检视卡（宽 1200、`x=40`、`y=size.y-34*UI-h`，`:141-163`）三块都有断言。**小地图不许压到这三块**，也不许改它们的尺寸。
2. **`hud.gd` 的 `sync()` 现在没有玩家坐标**：`:38` `func sync(is_time: bool, i: int, fmax: int, f: FrameData) -> void`。`_mdtest/hud_layout_check.gd:34` 正是这样调它的 ⇒ **你不能改 `sync()` 的参数列表**（会打破既有测试），要**另加一个方法**。
3. **`main.gd` 的 `hud.sync(...)` 只在 `_refresh_all()` 里调**（`:336`），而 `_refresh_all()` 只在**切帧/切轴**时调（`:304-311`）⇒ **玩家每帧移动时 HUD 拿不到新坐标**。所以小地图要每帧更新，必须在 `main.gd:_process` 里另加一次调用（或者让 HUD 自己每帧从别处拿）。注意 `main.gd:_process` 里有两处提前 return（`:98` tl 为空、`:143-147` 档案开着）⇒ **档案开着的时候小地图可以不更新**（符合「开档时世界停」的语义）。
4. **走路动画频率是同一个常量写了两处**：`scripts/player.gd:73` `bob = absf(sin(walk_phase * 9.0)) * 3.2`（上下浮动）与 `:96` `idx = int(walk_phase * 9.0) % frames.size()`（帧索引）。**两处都要改**，只改一处会出现「身体上下抖得慢、腿脚还在快走」的抽搐。

---

## §1 背景与用户裁定

用户 2026-11-25 09:19 逐条拍板（原文见 `docs/待解决事项.md` §1.3）：

- **M6**：「世界尺寸需要放大，且**角色的移动速度要放大**，现在走得太慢了，而且我想**加一个小地图的功能**，方便检视现在所处的位置。」
- **M7**：世界放大按**甲方案**（地图变大，TILE 仍 32）⇒ **世界从 3200×2400 变成 4800×3600**（150×112 格）。

本线就干 M6 里的两件事：**提速** ＋ **小地图**（外加走路动画频率必须同步降，否则提速后人物像滑冰）。

---

## §2 事实底账（照抄，不要重新推导）

### 2.1 `scripts/hud.gd`（195 行，全文已读）

- `:11-15` 布局常量：`const DESIGN_W := 640.0`／`const UI := 2.0`／`const FONT := int(10*UI)`=20／`const FONT_BIG := int(13*UI)`=26。
  **UI 的定义是「视口宽 / DESIGN_W」＝ 1280/640 = 2.0** ⇒ **小地图的所有尺寸也要乘 `UI`**（比如 100×75 的设计尺寸 ⇒ 200×150 实际像素）。
- `:19` `var font: Font = ThemeDB.fallback_font`。
- `:21-31` 状态字段：`time_mode`／`index`／`frame_max`／`year`／`frame_id`／`hotspot_title`／`hotspot_text`／`hotspot_visible`／`bump_flash`／`axis_flash`。
- `:33-35` `_ready()`：`set_anchors_preset(Control.PRESET_FULL_RECT)`、`mouse_filter = Control.MOUSE_FILTER_IGNORE`。
- `:38-44` `func sync(is_time: bool, i: int, fmax: int, f: FrameData) -> void` — 复制 `time_mode/index/frame_max/year/frame_id` 后 `queue_redraw()`。**没有玩家坐标参数**（坑 2）。
- `:47-57` `show_hotspot(h: Dictionary)`。
- `:59-67` `flash_bump()`／`flash_axis()`。
- `:69-79` `_process(delta)`：只处理闪烁衰减。
- `:81-86` `_draw()`：依次调 `_draw_top_bar()`／`_draw_timeline()`／`_draw_hotspot()`／`_draw_hint()` ⇒ **小地图要在这里加一次调用**。
- `:88-108` `_draw_top_bar()`：条高 `18.0*UI`=36px，基线 `ty = 13.0*UI`；左段「%d · %s」／中段轴名（按字宽居中）／右段「F11 全屏/小窗」。
- `:110-139` `_draw_timeline()`：条高 `30.0*UI`=60px，`y := size.y - bar_h`，刻度点 `dot_y = y + 13.0*UI`，5 档刻度点 + 竖线（`y+5*UI`→`y+21*UI`）。
- `:141-163` `_draw_hotspot()`：卡宽 `w := size.x - 40.0*UI`=1200、`x := 20.0*UI`=40、`y := size.y - 34.0*UI - h`；`pad=8*UI`、`line_h=13*UI`。
- `:166-178` `_draw_hint()`：`hotspot_visible` 时不画；提示字贴 `size.y - 2.0*UI`。
- `:182-195` `_wrap(text, max_w)` 按字符宽度硬折行。

### 2.2 `scripts/main.gd`（342 行）

- `:12` `const PLAYER_SPEED := 120.0`。
- `:96-98` `_process(delta)` 开头：`if tl == null: return`。
- `:140-147` 档案开着时：`player.walking = false`＋`_set_hud_hidden(true)`＋**`return`** ⇒ 这一段不会走到后面的玩家位置同步。
- `:158-169` 走/时间轴分支；`:163` `player.position = tl.char_pos`；`:168-169` `world.set_player_state(tl.char_pos, ...)`。
- `:172-190` `_process_space(delta)`：`:182` `tl.move_space(dir * PLAYER_SPEED * delta)`；`:184` `player.walk_phase += delta`。
- `:322-337` `_refresh_all()`：`:336` `hud.sync(is_time, tl.index, tl.frame_max(), f)` —— **只在切帧/切轴时调**（`:304-311`）。
- `:90` `_set_hud_hidden(hidden)` 会设 `hud.visible`。

### 2.3 `scripts/player.gd`（165 行）

- `:17` `const RADIUS := 14.0`（**碰撞半径，别动**）。
- `:26` `const HERO_FRAME := 32`（**精灵尺寸，别动**）。
- `:73` `bob = absf(sin(walk_phase * 9.0)) * 3.2`。
- `:96` `idx = int(walk_phase * 9.0) % frames.size()`。
- 对照：`scripts/frame_data.gd:14` `const CHAR_RADIUS := 14.0`（碰撞探针，与 `RADIUS` 一致 ⇒ **提速不许改这两个**）。

### 2.4 `_mdtest/hud_layout_check.gd`（89 行，全文已读）

既有断言清单（**一条都不许改**）：

| 行 | 断言 |
| --- | --- |
| `:38` | 字号 20 / 26 |
| `:53` | 左段不压中段 |
| `:54` | 中段不压右段 |
| `:55` | 右段不出屏 |
| `:58` | 顶条高 36 装得下 20px 字 |
| `:64` | 底条不遮住整个屏（y=660） |
| `:67` | 第一个刻度点不越左边界 |
| `:68` | 最后一个刻度点不越右边界 |
| `:74` | 底部提示字宽 < 1280 |
| `:85` | 检视卡不超屏宽 |
| `:86` | 检视卡不压住底部时间轴条（`hy > bar_h + 20`） |

⚠️ 该脚本 `:26` 设 `hud.size = Vector2(1280, 720)`、`:27-31` 直接写 `hud.frame_max/index/year/frame_id/time_mode`、`:33-34` `var f = FrameData.new(); hud.sync(false, 0, 4, f)`（**空 FrameData**，`f.id` 是空串）。你的小地图实现**不能假设 `sync()` 传进来的 frame 有内容**，也不能因为小地图而改动 `sync()` 的签名（坑 2）。

---

## §3 要做的三件事

### 3.1 提速（`scripts/main.gd`）

- `:12` `const PLAYER_SPEED := 120.0` → **`180.0`**（×1.5；世界也放大 1.5 倍 ⇒ 屏幕上观感速度不变，但用户明确要「速度放大」）。
- **不许改** `scripts/player.gd:17` `RADIUS`、`:26` `HERO_FRAME`、`scripts/frame_data.gd:14` `CHAR_RADIUS`。
- 提速会不会让玩家「穿墙」？不会：`scripts/timeline.gd:105-121` `move_space()` 是分轴推进的（撞墙沿墙滑），与速度无关。但**单帧位移变大 ⇒ 可能一步跨过 32px 的墙格**？`CHAR_RADIUS=14` 的方形探针每帧位移 180×dt（60fps 下 3px）⇒ 远小于一格，**不会穿墙**。若你在 30fps 的机器上测出穿墙，**不要改碰撞半径**，改用「单帧位移上限」（clamp 位移到 ≤8px）。

### 3.2 走路动画频率（`scripts/player.gd`）

- `:73` 与 `:96` 两处的 **`9.0` 都要改成 `6.0`**（×1.5 提速 ⇒ 动画频率按同倍降，否则腿脚比身体快，看着像滑冰）。
- 建议把 `9.0` 提成一个常量（例如 `const WALK_FREQ := 6.0`）再在两处引用 —— **但如果你担心别的脚本引用了 `9.0`，就不要重构**（grep `walk_phase` 确认只有 `player.gd` 与 `main.gd` 用到）。

### 3.3 小地图（`scripts/hud.gd` ＋ `scripts/main.gd`）

**落位**：**右上角，顶条以下、检视卡以上**。

- 视口 1280×720；顶条高 36；底条高 60（`y=660`）；检视卡在下方居中、宽 1200（`x=40`）、顶边随内容高度浮动（`y = size.y - 68 - h`）。
- 建议尺寸：**200×150 实际像素**（＝设计值 100×75，乘 `UI=2`）。落位：右边缘留 `8*UI`=16px 边距 ⇒ `x = size.x - 16 - 200`；顶边 `y = 36 + 8*UI` = **52**（顶条下沿 36 + 16 间隙）。
- **不许压到**：顶条（y<36）、底条（y>660）、检视卡（x=40…1240 且在屏幕下部）。你的小地图 x=1064…1264、y=52…202 ⇒ 与检视卡**可能同时出现**（检视卡顶边 `720-68-h`，h 最小约 62 ⇒ 顶边 ≈590）⇒ **不重叠**。但要在断言里验这一条。

**内容**（一张世界缩略图 + 三个点）：

1. **世界底板**：`world` 是 4800×3600 ⇒ 缩略图 200×150 正好是 **4800:3600 = 4:3** ⇒ **1 世界像素 = 1/24 缩略图像素**（4800/200=24，3600/150=24，比例一致 ⇒ 不用留白或拉伸）。
   - 底板画法：深色半透明底 + 一条淡边框（例如 `Color(0.06,0.05,0.04,0.62)` 底 ＋ `Color(0.55,0.48,0.38,0.55)` 1px 边）。
   - **不要**把五帧的 houses/roads 画成缩略图（那是额外工作量，且 HUD 不该读 `data/frames.json`）⇒ **只画世界框 + 玩家点 + 关键地标点**。
2. **玩家点**：世界坐标 → 缩略图坐标：`p = (world_pos.x / 24.0, world_pos.y / 24.0)`（相对缩略图左上角）。画一个亮色小圆点（半径 3px，`Color(0.95,0.85,0.60)`）。
3. **关键地标点**：井／老槐／界碑／界碑？—— **本轮只画「井」和「超市/小学」不好做**（HUD 拿不到世界数据）⇒ **本轮只画玩家点 + 一个可选的世界框**，地标点留成下一轮（或者你愿意读 `data/frames.json` 也可以，但那样 HUD 与数据耦合、且 L11 正在改数据文件 ⇒ **不要读**）。

**接口设计**（两个方案，任选，但**不许改 `sync()` 的签名**）：

- 方案 A（推荐）：`hud.gd` 加
  ```gdscript
  var player_pos := Vector2.ZERO
  var world_extent := Vector2(4800, 3600)   # 4800×3600（M7 已拍板）

  func sync_player(pos: Vector2) -> void:
      player_pos = pos
      queue_redraw()
  ```
  由 `scripts/main.gd:_process` 里每帧调用（放在 `:163` `player.position = tl.char_pos` 之后）。**注意**：档案开着时 `_process` 在 `:143-147` 提前 return ⇒ 那一段不会调用，**符合语义，不用特殊处理**。
- 方案 B：把玩家坐标塞进 `sync()` 的参数 —— **❌ 会打破 `_mdtest/hud_layout_check.gd:34` 的既有调用**（它只传 4 个参数）⇒ **不许做**。

**绘制**：在 `_draw()` 里加 `_draw_minimap()`（放在 `_draw_top_bar()` 之后、`_draw_timeline()` 之前都可以；建议放最后 `_draw_hint()` 之后，这样检视卡压在小地图上面更保险 —— 其实不重叠，随便）。

⚠️ `hud.gd` 是 `Control` 子类，`_draw()` 里用 `draw_rect`／`draw_circle`／`draw_string` 都可以。

### 3.4 顺便考虑：要不要在时间轴模式也显示小地图？

建议**一直显示**（小地图是空间定位工具，与轴无关）。但**时间轴模式下 alpha 降一档**（底板 alpha 从 0.62 降到 0.45），与 `scripts/hud.gd:110-139` 时间轴的收起风格一致。**这一条可选，你自己定，在反馈文档里写明。**

---

## §4 测试

### 4.1 只能加的断言（在 `_mdtest/hud_layout_check.gd`）

在既有断言**之后**追加（不许改动既有行）：

1. **小地图矩形不越屏**：`x + w <= 1280`、`y >= 36`（顶条下沿）、`y + h <= 660`（底条上沿）。
2. **小地图不压顶条/底条/检视卡**：
   - 与顶条（`Rect2(0,0,1280,36)`）不相交；
   - 与底条（`Rect2(0,660,1280,60)`）不相交；
   - 与检视卡（`Rect2(40, 720-68-h, 1200, h)`）不相交（h 用 `:82` 那个算法算出来的）。
3. **玩家点落在小地图内**：把 `hud.sync_player(Vector2(2400, 1800))` 调进去，然后断言玩家点在 `[x, x+w]×[y, y+h]` 内。
4. **世界坐标 → 缩略图坐标的映射正确**：如果你把映射写成了可测的函数（如 `_minimap_point(world_pos) -> Vector2`），就断言 `hud._minimap_point(Vector2(0,0)) == 小地图左上角`、`hud._minimap_point(Vector2(4800,3600)) == 右下角`。
5. **帧切换后小地图仍在**：调两次 `sync()`（不同 frame）后小地图矩形不变。

**写法提示**：小地图矩形最好做成 HUD 的一个**可测的方法**（如 `func minimap_rect() -> Rect2`），这样断言和绘制共用同一份几何，不会写着写着两处不一致。

### 4.2 既有断言一条都不许动

`_mdtest/hud_layout_check.gd:38/:53/:54/:55/:58/:64/:67/:68/:74/:85/:86` —— **不许改、不许删、不许改期望值**。如果你发现既有断言因为你改了什么而变红，**先想清楚是不是你改错了**。

### 4.3 回归要跑全的套

`hud_layout_check`（必须）＋ 建议顺手跑全套：`greybox_check`／`camera_check`／`asset_draw_check`／`sort_check`／`display_check`／`evidence_archive_check`（七套）。

**注意**：如果你在 L11 之前跑 `greybox_check`，它会因为 `data/frames.json` 还没放大而**绿**；如果你在 L11 之后跑，它会因为 L11 改了期望值而绿或红 —— **红了不要自己去改 `_mdtest/greybox_check.gd`（那是 L11 的文件域）**，把关键字记下来写进反馈文档，交给总策划裁决。

---

## §5 白名单与纪律

1. **只精确 `git add <文件>`，绝不用 `git add -A`。**
2. commit message 用中文，建议：`feat(ui): 加小地图 + 速度 ×1.5 + 走路动画频率同步降档`。
3. 提交前 `git diff --stat` 自检，确认只包含 `scripts/hud.gd`／`scripts/main.gd`／`scripts/player.gd`／`_mdtest/hud_layout_check.gd` 这四个文件。
4. **不要 push**（GitHub 推送由项目总策划按用户定时指令统一做）。
5. 反馈文档 `docs/FEEDBACK-l11b-ui-exec.md` ≤100 行，必须包含：
   - 改了哪些文件、各改了什么（列出具体行号）；
   - 小地图的落位与尺寸、画了什么、没画什么；
   - 玩家点坐标映射公式；
   - 提速与动画频率的改动值；
   - 新增断言清单与七套回归的实际输出关键字；
   - **未解决/做不到的地方**（例如「地标点没做，因为 HUD 不读数据」）；
   - 你有没有碰 L11/L13 的文件（**应该没有**）。

---

## §6 验收清单（自检打勾）

- [ ] `scripts/main.gd:12` `PLAYER_SPEED` = 180.0。
- [ ] `scripts/player.gd:73` 与 `:96` 的 `9.0` 都改成 `6.0`（两处都要改）。
- [ ] `scripts/hud.gd` 有 `sync_player(pos)`（或等价接口），`sync()` 签名**没变**。
- [ ] 小地图落在右上角（x ≈ 1064、y ≈ 52、200×150），不压顶条/底条/检视卡。
- [ ] 玩家点位置随 `sync_player()` 更新，且坐标映射是 `world/24`。
- [ ] `scripts/main.gd:_process` 每帧喂坐标（档案开着时停更，符合语义）。
- [ ] `_mdtest/hud_layout_check.gd` **只加了**断言，既有 11 条断言一字未改。
- [ ] `hud_layout_check` 打 `HUD_CHECK_DONE fails=0`。
- [ ] 七套回归无新增红（若红在 L11 的地盘，写进反馈文档交总策划）。
- [ ] **没有碰** `data/frames.json`／`scripts/world_view.gd`／`scripts/frame_data.gd`／`docs/story.md`／`docs/npc.md`／`docs/HANDOFF.md`。

---

## §7 不要自作主张的事

1. **不要改 `scripts/hud.gd` 的 `sync()` 参数列表**（会打破既有测试）。
2. **不要改顶条/底条/检视卡的尺寸与位置**。
3. **不要在 HUD 里读 `data/frames.json`**（数据文件是 L11 的单写者域，且会耦合）。
4. **不要改碰撞半径**（`RADIUS`/`HERO_FRAME`/`CHAR_RADIUS`）。
5. **不要动 `_mdtest/` 里除 `hud_layout_check.gd` 之外的任何文件**。
6. **不要做地标小地图点**（本轮不做；地标数据在 frames.json，L11 正在改）。
7. **不要 push。**
8. **不要改 `docs/story.md`／`docs/npc.md`／`docs/HANDOFF.md`**（归 L13）。

---

## §8 收工

1. 跑 `hud_layout_check`（＋建议全套），把关键字贴进反馈文档。
2. `git add` 精确那四个文件 → `git status` 自检 → commit。
3. 写 `docs/FEEDBACK-l11b-ui-exec.md`（≤100 行）。
4. 交回总策划验收。
