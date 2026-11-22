# 反馈文档 · 美术资产消费点接入线（致「项目总策划」会话）

> 提交方：美术资产消费点接入线（本线，2026-11-22 19:35 交付）
> 接收方：项目总策划会话（负责统筹并行、划边界、验收、提交）
> 目的：汇报本线已交付内容 + **实测数据** + **边界自查** + **仍需总策划拍板的两项**。
> 本线**未 commit**，全部产物在隔离路径内，等总策划统一提交。
> 上游：`docs/PROMPT-asset-consumption-exec.md`（本线任务书，A 方案已由用户 2026-11-22 拍板）

---

## 0. 一句话现状

**美术贴图已经全部画进游戏里了** —— 房子底图、屋顶、家具、主路/田/河/坝、老井/老槐/界碑、主角 36 帧精灵，
六套回归全绿；并且在视觉验收中查出并修掉了一个真 bug（「双份墙」）。
剩余两件事需要总策划拍板：**同学那 32 张零消费点的生产图要不要一次性全换**、**A4/A5 帧数据谁来搭**。

---

## 1. 本线已交付（已实测通过，可直接验收）

| 产物 | 位置 | 规模 | 校验 |
|---|---|---|---|
| 贴图工具模块 | `scripts/asset_draw.gd` | **新建** 171 行 | 纯静态函数，无 `_draw` 入口 |
| 引擎消费点 | `scripts/world_view.gd` | 改 **+206 / −18** | 4 处消费点 + 墙/门改由美术图接管 |
| 主角精灵接入 | `scripts/player.gd` | 改 **+104** | 36 帧 / 4 方向 |
| 专项自检 | `_mdtest/asset_draw_check.gd` | **新建**，65 条断言 | `ASSET_DRAW_CHECK_DONE fails=0`（打印 60 行 PASS） |
| 定点截图器 | `_mdtest/asset_shot.gd` | **新建**，11 处定点 | 截图 **11 张** |
| 验证截图 | `_mdtest/assets/*.png` | 11 张 1280×720 | 全部目视核对过 |
| 存档 | `docs/HANDOFF-asset-consumption.md` | 约 200 行 | 含第〇节「修掉双份墙」根因复盘 |

合计两个已有文件 **+283 / −27**，外加 5 个新增路径。

### 1.1 四类贴图各接在哪（架构：接进既有分支，**不新建绘制节点、不新起 `_draw` 入口**）

| 类别 | 消费点 | 实现要点 |
|---|---|---|
| **base**（12 栋底图） | `world_view.gd` `_draw_house_base()` | 贴 `Rect2(lot_x, lot_y − EXTRUDE, lot_w, lot_h + EXTRUDE)`（D6：顶部多一格 = 墙高），**替代**原第 1/2 层色块；无图回色块 |
| **roof** | `_draw_roof()` 末尾 | 沿用既有 `draw_texture_rect` 公式（本就存在），无需改 |
| **props**（家具） | `_draw_furniture()` | 按 `short` 匹配 manifest id，**按 houses_data 的 rect 尺寸**贴（D6：底边对齐占地底边 + 顶部一格）；线索家具仍画橙框 |
| **scene 大图**（路/田/河/坝） | `_draw_back()` | 河贴整张 river 图到 `(0,0)-(3200,416)`；路/田按**整帧几何 bbox**（`_scene_bboxes()`）各贴一次 |
| **scene 小件**（老井/老槐/界碑） | `_draw_prop()` | circle/rect 分支先试小件图，底边对齐；无图走原色块 |
| **主角**（36 帧） | `player.gd` `draw_self()` | `draw_texture_rect_region` + 4 方向分组；无图回原「圆+朝向三角」画法 |

### 1.2 家具匹配的精度（本线实测修正了上游的一处错误口径）

上游 `PROMPT-asset-consumption-exec.md` §3.2 写的是「从 `f["id"]` 取」——
但 `houses_data.json` 的家具条目**没有 `id` 键**（只有 `name`/`short`/`rect`/`clue`/`zone`），照抄会取到空值。
本线改用 **`short` + 占地尺寸** 双键匹配：footprint 完全一致优先，否则取 |Δw|+|Δh| 最小。
（manifest 里 **18 个 short 对应多个 id**：凳→1×1/1×3、八仙桌→2×2/2×3、灶台→3 个 id……，单靠名字一定会串。）

实测（2026-11-22 19:59 重算，houses_data 已被其它线扩容过）：

```
全部 18 栋：total 583 / short 命中 247 / footprint 完全一致 227 / 近似 20 / 未命中 336
A1–A3 12 栋：total 178 / 命中 176 / **footprint 完全一致 176 / 近似 0** / 未命中 2（都是「大床」）
可达 manifest id：85 / 91
```

⇒ **玩家实际能看到的 A1–A3 场景里，家具贴图 100% 精确对齐**（176/176）；
未命中的 336 条全部集中在 A4/A5 的学校施工类词（跑道×56、课桌×48、货架×18、未拆封货架×18、茶几×5…）。

### 1.3 主角精灵方向分组（美术没给标记，本线按像素实测推出）

`美术资产/主角/Sprite-主角-Sheet.png` = 1152×32 = 36 帧（32×32 一格），**无方向分组标记**。
本线按「脸部皮肤像素左右分布」分类得出：

| 方向 | 行走帧 | 站立帧 |
|---|---|---|
| 正面 down | 0–3 | 16–20 |
| 左 left | 4–7 | 21–25 |
| 右 right | 8–11 | 26–30 |
| 背面 up（只见金发无脸） | 12–15 | 31–35 |

精灵 alpha bbox ≈ (6,0)-(26,32)，底边 = 帧底边（脚底对齐）。

### 1.4 回归结果（六套全绿）

```
greybox_check     WORLD_OK=true  START_OK=true  HOTSPOTS_OK=true  REACH_OK=true
sort_check        SORT_CHECK_DONE fails=0
camera_check      CAMERA_CHECK_DONE fails=0
display_check     CONTENT_SCALE_MODE=1 / ASPECT=1 / SIZE=(1280,720) / 纹理过滤=0(Nearest) / STRETCH_SCALE_MODE=0
hud_layout_check  HUD_CHECK_DONE fails=0
asset_draw_check  ASSET_DRAW_CHECK_DONE fails=0     ← 新增，65 条断言
```

沙箱基线噪声（非本线引入）：`Failed to open 'user://logs/godot...log'`、
`Failed to read the root certificate store.`、pwsh 控制台中文乱码。

---

## 2. 视觉验收：查出并修掉「双份墙」（本线最值得记的一条）

**症状**：房子截图里墙像被画成了另一种颜色。

**像素级定位**（`a1_shen_house.png` vs `assets/village/houses/shen/a1_base.png`；
shen_a1 world pos=(128,640)，base 画布左上 = 世界 (128,608)，screen = world − 相机 offset）：

| 采样行 | base 图 | 截图 | 判定 |
|---|---|---|---|
| 地面/院子/田块 | (196,179,146) | (196,179,146) | ✅ 完全一致 → **锚点公式正确，不是错位** |
| 墙顶面行 | (232,215,184) | (201,168,120) | ❌ 被引擎 `WALL_TOP #c9a878` 覆盖 |
| 南立面行 | (208,184,146) | (140,107,74) | ❌ 被引擎 `WALL_COLOR #8c6b4a` 覆盖 |

**根因**：`_ref/art/gen/_gen_shells.py` 的 `paint_base()` 里 base 图**已经画好**墙顶面(`draw_cap`) /
南立面(`draw_facade`) / 窗(`draw_window`) / 门(`draw_door`) / 院门(`draw_gate`)；
而 `world_view.gd` 的 `_draw_walls_row()` + "door" 分支**又用色块画了一遍**。
（`_draw_walls_row` 的 `with_body` 只控制「墙格本体」，**墙顶面和南立面是无条件画的** —— 这就是 bug 根源。）

**修法**：
- `world_view.gd` 新增 `static func _art_walls(sid) -> bool`（= `_house_tex(sid)["base"] != null`）；
  "walls" / "door" 分支在它为真时 `continue`（不画引擎色块）。
- `_collect_front()` 的 door 条目补了 `"sid"` 字段（原来门条目不知道属于哪栋），
  **只加字段，未动 sort_y / seq / 条目数量** ⇒ 排序不变式守住。
- walls/door **条目仍留在排序链里**（A1 = 39 行墙 + 13 个门），只是「不画」不是「不收集」。
- 顺带确认：`lu_a3` 是废墟（`ruin:true`，`paint_ruin()` 只画矮墙基），「有 base 就不画引擎墙」对废墟同样成立，
  截图 `a3_lu_ruin.png` 正常。

**教训（对后续所有美术接入线都适用）**：
> 把美术图「贴上去」**不等于**接完了 —— 美术图已画的内容，引擎必须让位，否则就是双份。
> 查这类问题最快的方法是**像素级比对 base 图与截图**：先比地面（对得上 ⇒ 锚点对），
> 再比出问题的行（对不上 ⇒ 是引擎多画了一层，不是错位）。

---

## 3. 结束报告（任务书 §6 要求的四条）

### ① 哪些图真能看到

| 类别 | 内容 | 验收截图 |
|---|---|---|
| base | 12 栋房子的院子/地板/门窗底图 | `a1_shen_house.png`、`a1_lu_house.png`、`a3_mill.png` |
| roof | 茅草顶/瓦顶（玩家在屋外才显示，屋内消失是既定机制不是 bug） | `a1_mill_outside.png` |
| props | 床/桌/椅/柜/书架/牌位/水缸/花盆/灯笼等 | `a1_shen_house.png` |
| scene 大图 | 主路、田、河、坝 | `a1_mill_road.png`（河+坝）、`a3_field_road.png`（田+路） |
| scene 小件 | 老井、老槐、界碑 | `a1_well_tree.png` |
| 主角 | 36 帧精灵（4 方向） | 各截图中的主角 |
| 废墟 | `lu_a3` 残墙基 + 杂草 | `a3_lu_ruin.png` |

### ② 哪些看不到 + 原因

| 内容 | 数量 | 原因 | 性质 |
|---|---|---|---|
| 学校施工类家具 | 跑道×56、课桌×48、货架×18、未拆封货架×18… | manifest 里**没有这些 id** → 回色块 | **预期行为**（缺图优雅降级，D8 永久保留） |
| A4/A5 的 6 栋房子及场景 | shen_a4 / market / school / toyshop / zhou_a4 / zheng_a4 | `data/frames.json` 的 `a4_2001` / `a5_2026` **shapes 是空数组** → 场景里没有这些房子 | **上游数据缺口**，见 §4 |
| `lu_a3` 屋顶 | 1 | 废墟，manifest 只有 base 没有 roof | 预期 |
| 同学生产图 | 39 主图里 **32 张零消费点** | manifest 只引用了 7 条（`xiaozhuo_1x1`/`hongzhuo_1x1`/`baizhuo_1x1`/`shuzhuo_1x1_top`/`gui_1x1`/`changzhuo_2x1`/`cantang_3x1`） | **阻塞③**，见 §4 |

### ③ 回归结果
六套全绿（见 §1.4）。

### ④ 边界确认（已用 `git diff` 逐条核实）
- ✅ **没改** `scripts/house_shape.gd`（diff 空）
- ✅ **没改** `data/frames.json` / `_ref/houses/houses_data.json` / manifest / 任何 PNG
- ✅ **没动排序不变式**：sort_y + seq 稳定序原封不动，只给 door 条目多加了 `sid` 字段
- ✅ 碰撞/内外 1:1 未动（`EXTRUDE := 32.0` 写死未改；碰撞仍纯 AABB 读 houses_data）
- ✅ **没推翻**「玩家在 wings 内不画屋顶」
- ✅ **不新建绘制节点 / 不新起 `_draw` 入口**（A 方案）
- ✅ **未 commit**

---

## 4. 仍需总策划拍板的两项

### 拍板 A：同学生产图 32 张零消费点 —— 现在换，还是等？

现状：`assets/village/_classmate/props/` 实有 **39 张主图**（+45 变体），
manifest 只引用了 **7 条**。本线已把这 7 条接进消费点，**所以这 7 条现在真的画出来了**；
剩下 32 张没有任何 id 指向它们。

上游 `docs/FEEDBACK-planner-art-import.md` §2 阻塞③ 已算清替换可行性：
**尺寸一致 31 张**（换文件即可）、**AI 侧无此图 7 张**（属纯补位）。
风格差距是硬伤：同学图是带描边、高光阴影的精细像素画、多为正面/3/4 视角；AI 图是平涂色块、俯视视角
⇒ **建议一次性全换**而不是挑几张换。

> **本线补充的实测信息**（供决策）：
> ① 消费点已就绪 ⇒ **现在换就是「看得见的替换」**，不再是上游文档建议的「先别换」那种看不见的替换；
> ② 但**视角差异是已知的风格断层**，若只换一部分会出现同屏不协调；
> ③ 替换会动 manifest 引用的 PNG 文件，**与本线「不动任何 PNG」的边界不同**，需总策划单独授权。

**请总策划回复**：全换 / 只换那 31 张尺寸一致的 / 暂不换（继续走 AI 图风格）？

### 拍板 B：A4/A5 帧数据谁来搭？

`data/frames.json` 的 `a4_2001`（2001 年）和 `a5_2026`（2026 年）**shapes 是空数组**。
本线的贴图消费点对 A4/A5 的 6 栋房子**已经就绪**（base/roof 都在 manifest 里），
但帧里没有这些房子的 scene 摆放 → 玩家在 2001/2026 年**看不到那 6 栋房子**。

本线**没有搭帧数据**（超出本线边界：不动 `data/frames.json`）。

> **请总策划回复**：A4/A5 帧数据是**新开一条线**、还是**并进本线**？
> 若并进，本线需要额外授权「可改 `data/frames.json`」—— 因为这会同时影响
> `greybox_check` 的 HOUSE_MAP 期望值（那里写死了 A1–A3 的房子 pos/size）。

---

## 5. 本线的写入边界（已自查，未越界）

**本线只动过**：
- 新增 `scripts/asset_draw.gd`
- 新增 `_mdtest/asset_draw_check.gd`
- 新增 `_mdtest/asset_shot.gd`
- 新增 `_mdtest/assets/`（11 张 PNG）
- 新增 `docs/HANDOFF-asset-consumption.md`
- 改 `scripts/world_view.gd`（+206/−18）
- 改 `scripts/player.gd`（+104）

**本线没碰**：`scripts/house_shape.gd`、`scripts/main.gd`、`scripts/frame_data.gd`、`scripts/hud.gd`、
`scripts/camera_rig.gd`、`scripts/display_manager.gd`、`scripts/timeline.gd`、
`data/frames.json`、`_ref/houses/houses_data.json`、`_ref/art/_assets_a1a3/_a1a3_assets.json`、
`assets/village/**`、任何 PNG、`美术资产/` 源目录。

**未 commit**（按约定由总策划统一提交）。
工作区里 `houses_data.json` 的改动、toyshop/school 线的新文件等**来自其它并发线**，不是本线产出。
总策划 `git add` 时请**按路径精确挑选**，建议提交信息：

### 5.1 ⚠️ 一个提交时的依赖（必须和本线一起进版本库）

`scripts/player.gd` 里的主角精灵指向 `res://美术资产/主角/Sprite-主角-Sheet.png`，
但这个目录**目前整个是未跟踪状态**（`git ls-files 美术资产/主角/` 为空）。
另外 `美术资产/` 下原有的 `Sprite-*.png`（主角/房屋/家具/树/地皮若干）在工作区里显示为 **已删除**，
那是**美术资产线**把散图整理进分类目录造成的，**不是本线删的**。

⇒ 若只提交本线 7 个文件而不带上 `美术资产/主角/`，主角会走**降级路径**（画圆，不报错、功能不崩），
但精灵就没了。**请总策划提交时把 `美术资产/主角/` 一并纳入**（含 `.import`）。

### 5.2 一并建议纳入的其它线产物（供总策划参考，非本线产出）

`_ref/art/gen/`、`_ref/art/pixel_lib.py`（本线的 manifest/贴图规格来自这一套生成器）、
`assets/village/props/_legacy_16px/*.import`。

```
feat(render): 美术资产消费点接入线（base/roof/props/scene/主角 四类贴图消费点 + 双份墙修复）
```

---

## 6. 请总策划回复的三件事

1. **同学那 32 张零消费点的生产图**：全换 / 只换 31 张尺寸一致的 / 暂不换？
   （若换，请明确授权「本线或美术线可改 manifest 引用的 PNG」—— 这超出本线当前边界。）
2. **A4/A5 帧数据**：新开一条线，还是并进本线？若并进，请授权本线改 `data/frames.json`
   （会牵动 `greybox_check` 的 HOUSE_MAP 期望值）。
3. **本线是否可以提交**：六套回归全绿、`git diff` 边界自查已过，是否按上面的提交信息合入？
   （注意 §5.1：`美术资产/主角/` 目录目前未跟踪，主角精灵依赖它，请一并纳入。）

---

## 附：本线沉淀的两条通用经验

1. **贴图接完 ≠ 接对了**：美术图里已经画好的内容（墙、门窗、院门），引擎必须让位，
   否则叠成「双份」。查法 = 像素级比对 base 图与截图（先比地面定位锚点，再比问题行定位覆盖源）。
2. **贴图只是外观，占地/碰撞仍读数据**：manifest 的 `w/h` 与 houses_data 的 `rect` 在 A4/A5 有 22 条不一致，
   本线的做法是**按 houses_data 的 rect 贴图**，manifest 只用来选图 —— 与 D6「占地/碰撞读数据不读 PNG」一致。

---

*本反馈的事实全部经过实测（2026-11-22 19:35）。数值可复算：
`_mdtest/asset_draw_check.gd`（65 断言 / fails=0）、五套既有回归（fails=0）、
`git diff --stat`（两文件 +283/−27）、家具匹配复算脚本（583/247/227/20/336，A1–A3 178/176/176/0/2）。*
