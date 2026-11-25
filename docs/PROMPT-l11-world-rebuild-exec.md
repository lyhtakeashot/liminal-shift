# L11 · 世界重排执行任务书（4800×3600 + 五帧重排 + decor 边缘房子 + 平铺贴图）

> 这份是**执行线**的任务书。执行的人（新会话）不需要读我（总策划）的对话历史，照本文件做即可。
> 本文件里每一条数字要么来自实测，要么来自用户 2026-11-25 的逐条拍板。**没有依据的数字不要自己编。**
> 凡本文件写「待定 / 待用户点头」的，执行时**先按 §0.3 的默认值做**，并在反馈文档里注明「我用的是默认值，若用户改口径则需要二次调整」。
>
> **本线只做「数据 + 地图引擎」。** 同一批的另两条线（文件域零重叠，可同时开）：
> - **L12 界面与手感**（`docs/PROMPT-l11b-ui-exec.md`）＝ 小地图 + 提速 + 走路动画频率 ⇒ 只碰 `scripts/hud.gd`／`scripts/main.gd`／`scripts/player.gd`／`_mdtest/hud_layout_check.gd`。
> - **L13 树井文案与倾斜叙事删除**（`docs/PROMPT-l11c-text-exec.md`）＝ 只碰 `docs/story.md`／`docs/npc.md`／`docs/HANDOFF.md` 等**纯文档**。
>
> ⚠️ 但 `data/frames.json` 里**老槐四帧的 `text`** 属于本线（数据文件），**与 L13 的正文改口必须同批落地**（否则会出现「地图文案已改、设定文档还没改」的中间态）⇒ 两条线要**挨着交付**，不要隔几天。

---

## §0 开工前

### 0.1 基线与依赖

| 项 | 值 |
| --- | --- |
| 开工要求的 HEAD | `92078cb`（或其后；2026-11-25 11:05 的进度快照提交） |
| 本线产出 | `docs/PROMPT-l11-world-rebuild-exec.md` 之外的**代码与数据**，本文件不产生新文档 |
| 反馈文档（必须写） | `docs/FEEDBACK-l11-world-rebuild-exec.md`，≤120 行（⚠️ `docs/FEEDBACK-world-rebuild-exec.md` 是旧世界重构线的存档，**不许覆盖**） |
| 布局基准文件（**只读，不要改**） | **`lab/_l11_final.json`**（子代理 v3 冻结版：含 world/road/roundabout/well/tree/stele/field/hills/signs/edge_houses/parking/river/houses + 五帧 shapes）、`lab/_l11_final_report.txt`（自检报告，241 行，红灯 0 项） |

**开工前必须先读**：
1. **`lab/_l11_final.json`** —— 这是五帧布局的**唯一权威**（v3 冻结版，2026-11-25 10:39 写入）。任何坐标以它为准；它的顶层除了 `frames` 还有 `world/road/roundabout/well/tree/stele/field/hills/signs/edge_houses/parking/river/houses/selfcheck_red` 十三张参数表，可直接对照抄。
2. `lab/_l11_final_report.txt` —— 子代理的自检报告（241 行，红灯 0 项），里面有逐帧自检、可达性实测、环岛余量表、磨坊 grid 展开。
3. `docs/待解决事项.md` §1.3（M7–M16）—— 用户的八条裁定原文。
4. 本任务书 §2.5 —— 总策划对 v3 的独立复核结果（含你必须照抄的实测表与一个已知取舍）。

⚠️ **不要自己重新设计地图布局。** 你只负责把 `lab/_l11_final.json` 的内容**正确落进 `data/frames.json`**，并把该落地的引擎改造做掉。

🔶 **`lab/_l11_final.json` 已存在（v3 冻结版），直接用它。** 若它损坏或读不出来，才按下面退：

1. 用 `lab/_l11_candidate_frames.json`（v2 候选）作底 —— 参数与 v3 **不同**（v2：起点 [1472,1696]、井 [2048,1376]、环岛内圈 R192、槐 A1–A3 [1888,1536]、mill [1920,1056]、market [2112,512]、toyshop [2400,1792]、界碑 A1–A3 [1664,1600]），**只作兜底，不优先**。
2. v2 也缺三样：**每帧 `ground`**（§3.2 第 1 条）、**每帧 `hotspots`**（§3.3）、**a4 的 `_note`**（§3.2 第 2 条）。
3. v2 自带的 11 栋 decor 有 4 处冲突（1 栋出界、3 处互压）⇒ **不要用**；`lab/_l11_edge.json` 的 14 栋是按 v2 布局算的，在 v3 布局下**有 8 栋会与主屋/道路冲突**（总策划已实测）⇒ **也不要用**。边缘 decor 房子一律以 `lab/_l11_final.json` 的 `edge_houses`（12 栋）为准，再按 §3.4 处理那 1 处压路。
4. 用了 v2 就要在反馈文档里写明「用了 v2 候选 + 补 ground/hotspots/_note + 边缘 decor 自算」。
5. **无论用哪版，都必须按 §3.4 重新跑一次冲突校验**，不能直接抄。

### 0.2 能改 / 不能碰

**能改（白名单）**：

| 文件 | 改什么 |
| --- | --- |
| `data/frames.json` | 五帧世界数据：世界尺寸、起点、五帧 shapes/hotspots、decor 标记、新增 rect 类别字段 |
| `scripts/world_view.gd` | ①decor 房子的绘制 ②平铺贴图（河/路/田/山丘） ③新 rect 类别（surface / prop） ④一切与「放大后贴图尺寸写死」有关的硬编码 |
| `scripts/frame_data.gd` | ①decor 房子的碰撞与热点 ②新 rect 类别字段的读取 |
| `docs/PROMPT-l11c-text-exec.md` 涉及的三份文档 | **本线不碰**（归 L13）—— 但本线负责 `data/frames.json` 里老槐四帧 `text` 的改口，与 L13 同批 |
| `_mdtest/greybox_check.gd` | 仅限 §6 列出的**必红那几处**（需授权） |
| `_mdtest/camera_check.gd` | 仅限 §6 列出的**必红那几处**（需授权） |

**不能碰（一律不许改）**：

- `_ref/houses/houses_data.json`（房屋几何与家具是另一个文件域）
- `_ref/houses/*.py`（生成器）
- `assets/**`（美术资产由美术同学出，不是本线）
- `_ref/art/**`
- `scripts/house_shape.gd`（CLUE_TEXTS 与家具热点逻辑；本线不改线索文案）
- `scripts/hud.gd`／`scripts/main.gd`／`scripts/player.gd`（**归 L12**：小地图、提速、走路动画频率）
- `docs/story.md`／`docs/npc.md`／`docs/HANDOFF.md`（**归 L13**：树井文案改口、倾斜叙事删除）
- `_mdtest/hud_layout_check.gd`（**归 L12**）
- `scripts/evidence_store.gd`、`scripts/evidence_archive.gd`（证物模型本线不动）
- `scripts/timeline.gd`、`scripts/camera_rig.gd`、`scripts/player.gd` 以外的脚本随意禁止改
- `docs/_backup/**`、`docs/FEEDBACK-*`、`docs/HANDOVER-*`（历史留档）
- `_mdtest/**` 里除 §6 明确列出之外的任何断言

**不要动别人的工作区**：仓库里有美术线未提交的 PNG（`_ref/art/A1..A3/*.png`）、用户自己删掉的 `美术资产/` 一批文件、大批未跟踪的 `lab/_*`。**只用精确 `git add <文件>`，绝不用 `git add -A`。**

### 0.3 五个待用户点头的数 —— 本轮先用这些默认值

| 议题 | 默认值（本轮按此执行） | 备注 |
| --- | --- | --- |
| 世界放大倍率 | **1.5 倍 ＝ 4800 × 3600 px ＝ 150 × 112 格**（TILE 仍 32） | 用户已拍板「按甲方案走」＝地图变大、TILE 不变 |
| 环岛规格 | 圆心 **[2048,1696]**；**内圈 R=160（5 格）＋环道宽 64（2 格）＝外缘 R=224（7 格，外径 14 格）**；环岛 polygon ＝ `label:"路"` 48 点，bbox (1824,1472)–(2272,1920) | 用户已拍板「A4 树比环岛小、A5 树与环岛一样大」——**A5 老槐 r=160 正好等于内圈 R=160（顶满，余量 0）**，A4 老槐 r=96 ≤ 160（余量 64） |
| 「不可探索版空白房子」怎么表示 | house shape 加 **`"decor": true`**：只画底色/轮廓，**不进碰撞里的门洞逻辑、不生成任何热点**、**整栋 lot 作为一块实体挡住玩家** | 用户 M9：「村庄的边缘可以加点陆家周家的空白房子（不可探索版）作为空间约束」 |
| `docs/story.md:965` 线索表换成什么物证 | 左列换成「**磨盘上凿的那一行字**」（实物已有：上磨盘「沈氏丰源·一九五七」，`docs/story.md:441` §7.2 第 6 条已列） | 右列「第二个「私生子」」**必须保留**（那是「不能用第二次」的禁止项，删掉整行会把纪律删了） |
| 测试改写授权 | **已授权**改 §6 列出的 5 处（`greybox_check.gd:57-58`/`:291`/`:372`、`camera_check.gd:44`/`:51-52`）及随之必须同步的 HOUSE_MAP / 院门点 / 边界探测点 | 这几处是「世界尺寸写死」导致的必红，改的是**期望值**，不是删断言 |

另有两项用户明确**延后**，本轮**不要动**：
- **路宽**：A1/A2 弯路带宽度、A3–A5 直路宽度维持现状（弯路由 32px 小段拼、主路 64px），等世界放大后用户再定。
- **老槐半径刻度**：维持 32/64/96/96/160 不变（用户 M10「先把世界放大后再决定要不要改树的数据」）。**不改成 2/3/4/5/6 格。**

### 0.4 跑 Godot 的正确姿势（Windows + 沙箱）

```powershell
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . -s res://_mdtest/greybox_check.gd 2>&1 | Select-Object -Last 45
```

- **看关键字，不看退出码**。沙箱固有噪声：`Failed to read the root certificate store.`、`Failed to open 'user://logs/godot...log'`。成功标志是脚本自己打的 `..._CHECK_DONE fails=0`。
- `cmd /c "..."` 会被路径里的空格截断；`> out.txt` 在本机会产出 0 字节文件 ⇒ **一律用内联管道**。
- 需要 `$env:PYTHONIOENCODING='utf-8'` 才能用 python 读中文 JSON。
- `pwsh` 的 `ConvertFrom-Json` 读 `data/frames.json` 会报「传入的对象无效」⇒ **用 python 读**。

### 0.5 五个坑（踩过就别再踩）

1. **排序链只加不减**：`scripts/world_view.gd` 的 `_collect_front()` 收集的条目按 `sort_y` 升序排（`sort_custom`，同值按 `seq` 保全序）。`_mdtest/sort_check.gd:250` 与 `_mdtest/asset_draw_check.gd:287` 断言 `sort_y` 单调 ⇒ **新增前景元素时只能追加到链上，不能改别人的 sort_y 计算方式**。
2. **贴图画布尺寸写死**：`scripts/world_view.gd:263` 河贴图画布写死 `Vector2(3200, 416)`；`_scene_bboxes()`（`:276-304`）把同帧所有 `road:true` 的 rect 用 `Rect2.merge` 合成**一个外包矩形**再贴一次整张路图 ⇒ **世界放大到 4800 后河与路都会画错**。本线必须改成平铺/逐 rect 贴。
3. **每帧只能一个无 label 的 rect**：`label == ""` 的 rect 会被合成一个 field bbox；`label == "坝"`/`"碑"` 的 rect 被跳过；**竖路不能写 `road:true`**（否则整帧路 bbox 会把空地刷成柏油）。
4. **门洞不碰撞是故意设计**：`scripts/house_shape.gd:222-238` `solid_rects()` 只收 `'#'`，`'D'/'G'` 门洞完全不碰撞（`:368-369` 有注释说明）。不要顺手改。
5. **headless 实例化主场景截图会卡死**（跑 12 分钟零输出）。要截图就跑真实窗口，别在 headless 里实例化 `main.tscn`。

---

## §1 背景与用户裁定（本轮为什么做这些）

用户 2026-11-25 09:19 逐条拍板（原话见 `docs/待解决事项.md` §1.3 M7–M16）：

| 编号 | 裁定 | 本轮的落法 |
| --- | --- | --- |
| M7 | 世界放大按**甲方案**（地图变大，TILE 仍 32） | `data/frames.json` `world` ＝ 4800×3600；⚠️ 美术口径已同步改成「32×32 单方格瓦可平铺」（`docs/ART-GAP-A4A5.md`），所以引擎侧要改成平铺而不是拉伸整帧大图 |
| M8 | **先放大，后重新安排** | 一次做完：先改 world 尺寸，再按 `lab/_l11_final.json` 重排五帧 |
| M9 | 村庄边缘加**陆家/周家的空白房子（不可探索版）**作空间约束 | 边缘 **12 栋**（`lab/_l11_final.json` 的 `edge_houses`），house shape 加 `"decor": true` |
| M10 | 树的数据这轮**不改** | 老槐 radius 维持 32/64/96/96/160 |
| M11 | **树和井的文案都要改口，不保留同源关系** | `docs/story.md:447-455` 整节重写；`docs/npc.md:230` 换行；`data/frames.json` 老槐四帧 `text` 改口（老井五帧不动） |
| M12 | **倾斜叙事整组删** | 删 `story.md:451/453/454`、`:965` 换物证、`HANDOFF.md:378` 删三字、`npc.md` 六处 |
| M13 | 路宽**等放大后再定** | 本轮不动路宽 |
| M14 | 新元素**只需要把区域圈定好（方格）**，用贴图 | 用 rect 表达，**不新增 shape 类型**；引擎加 `surface`/`prop` 两个可选字段来区分 |
| M15 | 房屋布局：**陆家/周家放路南**；**沈家全帧定在同一位置且变大**；界碑跟着学校；起点重设 | 落进 `data/frames.json` |
| M16 | 美术重点是**复用**不是多设计 | 引擎改平铺；不要求新的整帧大图 |

---

## §2 事实底账（照抄，不要重新推导）

### 2.1 `data/frames.json` 现有 schema

顶层：`world {width,height}` / `safe_top` / `safe_bottom` / `start_pos [x,y]` / `frames`（**list**）。
每个 frame：`id` / `year` / `ground`（底色 hex）/ `shapes`（list）/ `hotspots`（list）。

shape 字段：

| type | 字段 |
| --- | --- |
| `polygon` | `points`（二维数组）/ `color` / `label` / `solid` |
| `rect` | `rect`（4 数 `[x,y,w,h]`）/ `color` / `label` / `road`(可选) / `solid`(可选) |
| `circle` | `center [x,y]` / `radius`（**半径，像素**）/ `color` / `label` / `solid`(可选) |
| `house` | `id`（houses_data.json 里的 id）/ `pos [x,y]`（**世界像素原点**＝lot 原点）/ `solid` |

hotspot 字段：`pos [x,y]` / `title` / `reach`（缺省 68.0）/ `text`。

> ⚠️ **坐标坑**：house 的 `pos` 是**世界像素原点**；`houses_data.json` 里的 `lot`/`wings`/`doors`/`partitions` 是**格坐标**。世界矩形 ＝ `pos + 格 × TILE`（TILE=32）。

### 2.2 引擎硬约束清单（改动前必须知道）

- `scripts/frame_data.gd`（143 行）
  - `:14` `const CHAR_RADIUS := 14.0`；`is_free()` 用方形探针与所有 solid_rects 求交。
  - `:38` `if not bool(sd.get("solid", false)): continue` ⇒ **`solid:false` 的 shape 完全不进碰撞**。
  - `:41-67` 按 type 分派；`house` → `HouseShape.solid_rects(hdata, hpos)` ＋ `HouseShape.hotspots(hdata, hpos, year)`（`:66` 是全仓唯一传 year 的地方）。
  - `:68-75` 手写 hotspots 缺 `reach` 时补 68.0。
- `scripts/world_view.gd`（928 行）
  - `:164` 草地是**引擎纯色**（`draw_rect` 全屏 + `frame.ground`），从不贴地面贴图。
  - `:196-199` `_draw_back` 开头取 `_scene_bboxes()`，有 `drew_road`/`drew_field` 两个「只贴一次」开关。
  - `:200-270` 分派：house→`_draw_house_base`；circle→**pass（走前景层）**；rect→`_is_standing_rect` 为真则 pass，否则按 `road:true` / `label=="坝"` / `label!=""` / `label==""` 四分支；path→polyline；polygon→河。
  - `:263` 河贴图画布**写死** `Rect2(Vector2.ZERO + offset, Vector2(3200, 416))`。
  - `:276-304` `_scene_bboxes()`：road rect 合成一个外包矩形；`label==""` 的 rect 合成一个 field bbox；`label=="坝"/"碑"` 跳过。
  - `:315-324` `_is_standing_rect()`：`road:true`→false；`solid:false`→false；**宽≤TILE 且 高≤2*TILE** 才算「立着」。
  - `:468-546` `_collect_front()` 收 walls / door / roof / furniture / prop 五类；玩家 `sort_y = player_pos.y + 14.0*0.7`。
  - `:577-579` `_is_standing_tree(label, rad)`＝`label.find("槐") >= 0 and rad >= 12.0`。
  - `:583-584` `_is_ground_landmark(label)`＝label 含「井」。
  - `:601-608` **`const FAMILY` 只到 a1–a3 的 12 栋** ⇒ A4/A5 六栋查不到屋体图（美术线的事，本线不管）。
  - `:642-662` `_draw_house_base()`：有 base 图时贴到 `Rect2(hpos.x, hpos.y - EXTRUDE, lot.size.x, lot.size.y + EXTRUDE)`（EXTRUDE=32）；**没有 decor 分支**。
- `scripts/house_shape.gd`（498 行）：`:13` `const TILE := 32.0`；`:157-219` `grid_of()` 判定顺序 `G > D > partitions > is_wall`；`:222-238` `solid_rects()` 只收 `'#'`；`:399-432` `hotspots()` 只对 `clue:true` 且**整个家具落在 lot 内**的家具生成；家具名「老井」会加「· 院里」后缀。
- `scripts/hud.gd`（195 行）：`:11-15` `DESIGN_W:=640.0`/`UI:=2.0`/`FONT:=20`/`FONT_BIG:=26`；`:38` `sync(is_time,i,fmax,f)`（**没有玩家坐标参数**）；`:88-108` 顶条 36px；`:110-139` 底条 60px；`:141-163` 检视卡宽 1200、`x=40`、`y=size.y-34*UI-h`；`:182-195` `_wrap()` 硬折行。
- `scripts/main.gd`（342 行）：`:12` `const PLAYER_SPEED := 120.0`；`:182` `tl.move_space(dir * PLAYER_SPEED * delta)`；`:184` `player.walk_phase += delta`；`:140-147` 档案开着时游戏停；`:149-156` SHIFT/E 在档案判断**之后**；`:336` `hud.sync(...)`。
- `scripts/player.gd`（165 行）：`:17` `const RADIUS := 14.0`；`:26` `const HERO_FRAME := 32`；`:73` `bob = absf(sin(walk_phase * 9.0)) * 3.2`；`:96` `idx = int(walk_phase * 9.0) % frames.size()`。
- `scripts/camera_rig.gd`（66 行）：`:16` `const VIEWPORT := Vector2(1280,720)`；`:57` `max_off := (world_size - VIEWPORT).max(Vector2.ZERO)` ⇒ 4800×3600 后 clamp 上限是 **(3520, 2880)**。
- `scripts/timeline.gd`（121 行）：`:44` `world_size` 从 frames.json 读；`:56-57` `start_pos` → `char_pos`；`:97-101` `is_walkable()` 用 world_size 做边界。
- `scripts/asset_draw.gd`（171 行）：`:18-40` `SCENE_FILES` **只含 a1/a2/a3**（每帧 road/field/river/well/tree）；`:43-46` `SHARED_SCENE` ＝ dam/stele；`:146-161` `prop_draw()` 底部中心锚点；`:165-171` `scene_tex()` 先查 `SHARED_SCENE` 再查每帧。

### 2.3 老槐 / 老井热点改口（**只改 text，其余一律不动**）

三条硬约束（违反会坏功能）：

1. 老槐 hotspot 的 **`title` 必须保持「老槐」**、`label` 必须含「槐」——`scripts/world_view.gd:579` 的 `_is_standing_tree()` 与 `:735`/`:767` 的贴图查找都靠「槐」这个字；`:766-774` `_prop_tex()` 按 label 找贴图。
2. 证物归一键 ＝ `scripts/evidence_store.gd:74-78` `landmark_key(title)` 取 title 第一个「·」之前的主体名 ⇒ **改 title 会把老槐拆成多张卡**。
3. 半径刻度不动（M10）。

**老槐五帧的新 text**（年龄说法全部保留；A1 帧原文不动）：

| 帧 | 新的 text |
| --- | --- |
| A1 | （保留）老槐树，今年刚栽下。树干还细，根边堆着新土。 |
| A2 | 老槐树，二十五岁。树干已经抱得过来，树冠铺开一小片。 |
| A3 | 老槐树，四十九岁。树干粗过水桶，树冠压到路边，过路的人要低头。 |
| A4 | 老槐树，七十五岁。树冠盖住了半个路口，路口新修的环岛把它围在当中。 |
| A5 | 老槐树，一百岁。树干要三个人才围得住，树冠正好顶满环岛中间，车从四周绕过去。 |

**老井五帧的 text 一律不动**（原文一句都没提树，本来就干净）。

### 2.4 叙事文本要改的每一处（逐字）

**（以下 §2.4 归 L13 执行，本线只做 `data/frames.json` 里老槐四帧的 `text`；文字照抄 L13 的任务书即可）**

**`docs/story.md`**

- `:447` 标题「### 7.3 老槐树」**保留**（可选改成「### 7.3 老槐树（唯一跟着时间长的东西）」）。
- `:449`、`:451`、`:453`、`:454` 四句 → 整节替换为三句：

  > 1926 年栽在路边，是树苗。
  >
  > 它在村里站了一百年，五个时代，五个样子：1926 年是树苗，1951 年树干抱得过来，1976 年树冠压到路边，2001 年十字路口修起环岛，把它围在当中，2026 年树冠正好顶满环岛中间。
  >
  > **它不替任何人作证。** 它只说明时间：村子改过好几轮，它一直在那儿长。

  （改完后**全节不许出现「井」字**。）
- `:960-966` 附三纪律③ 表：`:965` 那一行「| 老槐树倾斜的方向 | 第二个「私生子」 |」→ 改为「| 磨盘上凿的那一行字 | 第二个「私生子」 |」。**右列必须保留**（禁止项）。表内其它行不动。

**`docs/npc.md`**

- `:211` 第 4 项：「旁听 · 主线（老槐树，五帧）」→「旁听 · 主线（老井，五帧）」。
- `:230` 旁听素材表末行「| **老槐树** | 「井边种的，图个荫凉」 | … |」→ 换成老井行：

  ```
  | **老井** | **（当场）**「井里有水，绳子在井沿上磨出一道沟」 | 「老井填了，新井挪路那头了」 | 「填的时候没人敢往下挖」 | 「超市西墙外那片土是新的，没人多看」 | 「早先这底下就有口井吧，塌了好几回」 |
  ```

  （若你选择「只删行不新增」，则 `:211` 的第 4 项删掉，并把 `:221` 的「旁听 21 条」改成「旁听 16 条」。**二选一，在反馈文档里写明选了哪个。**）
- `:298` 刘桂芳「知道」栏：删掉「老槐树"不能动"」，换成「这路口"老塌"」。
- `:329` 对话②标题：「（方向：老井、老槐树）」→「（方向：老井、路口）」。
- `:335-336`：删掉主角「这树，有啥说法？」与刘桂芳「不能动。（朝院外那棵老槐树努努嘴）…」这一问一答，**保留 `:337-338` 的固定收尾**（记一下／咦，我刚跟谁说话来着？）。若你不想直接删，可改成「老树了。…说是清朝种的。」——**不得提井**。
- `:342`「玩家该听出」：去掉「老槐树不能动、动了出事」。
- `:343`「不该得出」：去掉「树为什么不能动」。
- `:359` 总结句：去掉「老槐树」。
- `:383`：去掉「这树，有啥说法？」。
- `:167` 场景「A1 · 井边 · 两名农妇」**保留不改**（指井边有人说话，不是说树在井边）。

**`docs/HANDOFF.md`**

- `:378`「其余必须是物理证据（补丁、排水管、树倾斜、界碑）」→「（补丁、排水管、界碑）」（只删「、树倾斜」三个字）。
- `:453` 老槐 4 态表**保留不改**（其中「树桩」态正文已无对应 ⇒ 在反馈文档里注明美术不要画树桩态）。

**D2 同步清单（本线可以顺手改，也可以只在反馈文档里列出）**：
`docs/待解决事项.md:37-38/41/86-92/112/194-195/308-350`、`docs/BUILD-A1.md:42`（「老槐在井边」→「老槐在路边（与井无关）」）与 `:80`、`docs/PROMPT-a5-map-build-exec.md:80/:88`、`docs/PROMPT-evidence-model-exec.md:39/52-57`、`docs/PROMPT-art-asset-gap-exec.md:144`、`docs/art-assets-a1a3.md:316-350`、`docs/DECIDE-a4-a5-layout.md:80`、`docs/PROMPT-overseer.md:79`（「A2 突然变大是剧情」→「＝时间刻度，不再承担叙事暗示」）。
—— **这些是「记录裁定本身」的历史文档，改不改都行**；改了要在反馈文档里逐条列出。

### 2.5 总策划对 v3（`lab/_l11_final.json`）的独立复核 —— 照抄这一份

**总策划已用 python 独立算过一遍（脚本 `lab/_l11_verify_road.py`、`lab/_l11_edge_vs_v3.py`），下面每一行都是实测值。**

**世界**：4800×3600 px ＝ 150×112 格，TILE=32，`safe_top=36`、`safe_bottom=3440`、`start_pos=[1024,1680]`。

**五帧主屋落位（`pos` 是世界像素原点＝lot 原点）**：

| 帧 | 四栋主屋 |
| --- | --- |
| a1_1926 | `shen_a1 [64,352]`（640×416）／`mill_a1 [1632,448]`（576×544）／`zhou_house [3008,1856]`（384×224）／`lu_house [1248,1856]`（640×416） |
| a2_1951 | 同上，`shen_a2` 736×544／`mill_a2` |
| a3_1976 | 同上，`shen_a3` 896×768／`mill_a3` |
| a4_2001 | `shen_a4 [64,352]`（1152×1152）／`market [2112,544]`（1344×896）／`zhou_a4 [640,1792]`（704×352）／`zheng_a4 [2432,2144]`（640×416） |
| a5_2026 | `school [704,512]`（1216×960）／`market [2112,544]`（1344×896）／`toyshop [2304,1728]`（672×640）／`zhou_a4 [640,1792]`（704×352） |

⇒ **沈家四代同址 `[64,352]` 且屋体逐代严格变大**（640×416 → 736×544 → 896×768 → 1152×1152，已实算 True）；**陆家/周家全在路南**（北沿 1856 > 路南沿 1728）；**A4 与 A5 的 market 同址** `[2112,544]`；**A4/A5 每帧都是「主路南北各 2 栋」**（北侧 shen/market/school，南侧 zhou/lu/toyshop/zheng）。

**地标**：井 `[2048,848]`，r=32/32/32/32/48（A1 `solid:true`，A2–A5 `solid:false`）；老槐 A1–A3 `[2048,1536]` r=32/64/96、A4/A5 `[2048,1696]` r=96/160（**A4/A5 树心 ＝ 环岛圆心，差 0px**）；界碑 A1–A3 `[1856,1376]`、A4 `[3520,1152]`、A5 `[736,512]`（**在 school lot 内，相对格 (1,0)，且压在围墙墙上**）；坝 `[384,96,256,128]`；河 polygon 153 点、bbox (0,0)–(4800,416)、`solid:true`；主路 A3/A4/A5＝单块 `[0,1664,4800,64] road:true`；A5 竖路＝三段 polygon `label:"路"`（环岛 48 点 bbox (1824,1472)–(2272,1920)／北段 (2016,416)–(2080,1472)／南段 (2016,1920)–(2080,3600)），车道中轴 x=2048；A5 停车场 polygon (1408,1728)–(1792,1984)＋车位 ×3＋红绿灯 rect `[2032,1440,16,16] solid:true`；A1 碎田 35 块、A2+ 整块田 `[3456,352,1088,384]`；山 4 块 polygon；路标 4 块 rect 16×32。

**四组叙事硬约束在 v3 全部成立（已实算）**：①A3 `mill_a3` lot `[1632,448,576,544]` 含井心（井在磨坊院里，井盘到最近墙 16px）；②A4 井东缘 2080 → 超市西墙 2112 ＝ **32px（一道墙）**；③A5 井心 x=2048 落在车道 x2016–2080 内（且井心到环岛圆心 848px，井在环岛以北）；④A5 界碑在 school lot 内。

**环岛余量表（外缘 R=224 对各楼 lot 最近点）**：market 264px（余量 +40）／toyshop 258（+34）／school 258（+34）／lu_house 226（+2）／zhou_house 973／shen_a4 854／zheng_a4 590／zhou_a4 711 ⇒ **全部不压**（余量最小的是 `lu_house` +2px，很紧 ⇒ **执行线不要改 `lu_house [1248,1856]` 的位置**，也别把 A1/A2 的 lu 往前挪）。

**可达性（子代理 BFS 实测）**：五帧所有地标、院门、车位、红绿灯、环岛中心的最近可站距离都 ≤25px，**超 reach(120px) 或不可达的地标数 = 0**；各帧可站格 14498/14438/14317/14047/14132（总 16800）。

**shape 统计**：a1 93（polygon 5／rect 70／house 16／circle 2）／a2 59／a3 31／a4 32／a5 39。**每帧 house ＝ 16 栋（4 主屋 + 12 装饰空房）**。

**🟡 一个已知取舍，必须照办**：A1/A2 的弯路是 **29 块 32px 厚的 rect**（`lab/_l11_final.json` 的 `road.a12_rects_px`），块与块之间**只在对角相接** —— 总策划实测：**4 邻接下 29 块是 29 个互不连通的连通块**（8 邻接下才是 1 个）。像素上路面是连续的斜阶梯，但玩家探针是 14px 方形，**沿弯路走到块与块的接缝时可能被卡住**。本轮请照这个顺序处理：**先按 v3 原样落地 → 用 §6.4 新增断言实测「A1 弯路能不能从西端一路走到东端」（沿路逐格推进，走不过去就报出卡住的那一格）→ 若走不通，在相邻两块之间补一块 32×32 的 road rect 把它变成 4 邻接连通**（补的块不得压主屋/河/界碑）。把结果写进反馈文档。

---

## §3 数据改造：`data/frames.json`

### 3.1 顶层

```
world:      { "width": 4800, "height": 3600 }
safe_top:   36
safe_bottom: 3440
start_pos:  **[1024, 1680]**（`lab/_l11_final.json` 的值，在主路上；注意不是 v2 的 [1472,1696]）
```

### 3.2 五帧 shapes

**做法**：以 **`lab/_l11_final.json`** 为准，逐帧把 `frames[i].shapes` 抄进 `data/frames.json`（每帧 93/59/31/32/39 条，一条约 20 个字段，量大 ⇒ 建议写 python 脚本做转换，不要手抄）。抄的时候：

1. **补齐 `ground`**（候选文件里漏了）：a1 `#6e7a4c`、a2 `#68744a`、a3 `#6a6a44`、a4 `#6f6a52`、a5 `#7a7a76`。
2. **保留 a4 的 `_note`**：「老井 solid 仅 A1=true……这是 v5 设计口径，不是 bug，别改。」
3. **每个 house shape 补 `"decor": true`（仅边缘空白房子）**，主屋不加。
4. **山丘 rect 补 `"surface": "hill"`**；**路标 rect 补 `"prop": true`**（见 §4.3 的引擎字段约定）。
5. **田地 rect 补 `"surface": "field"`**（让每块田各自平铺，不再被合成一个巨大 field bbox）。
6. **河 polygon 保留**（shape 的 `points`/`label`/`color`/`solid` 照抄），贴图怎么画见 §4.2。
7. **老槐 circle 的 radius 一律不动**（32/64/96/96/160）。
8. **老井 circle 的 `solid` 口径不动**：A1 `solid:true`、A2–A5 不写 `solid`。
9. 界碑 rect 保持 16×32（`label` 必须含「碑」——`_prop_tex()` 靠这个字找界碑贴图）。

### 3.3 五帧热点（hotspots）

候选文件里 hotspots 是空数组 —— **必须补回来**。规则：

- 每个地标都要有热点，**`pos` 跟着新坐标走**：`title`/`reach`/`text` 从旧 `data/frames.json` 搬过来（老井 reach=80；其余缺省 68.0）。
- 五个时代的地标清单（旧值，作为对照）：
  - A1：老井 / 老槐 / 界碑 / 坝 / 田（5 条）
  - A2：老井 · 石板 / 老槐 / 界碑 / 坝 / 田（5 条）
  - A3：老井 · 三层水泥 / 老槐 / 界碑 / 坝 / 田（5 条）
  - A4：老井 · 沥青补丁 / 老槐 / 界碑 / 坝 / 田 / 超市工地 · 南大门（6 条）
  - A5：老井 · 沥青补丁 / 老槐 / 界碑 / 坝 / 田 / 路口 · 红绿灯基座 / 停车场（7 条）
- **老槐四帧的 text 按 §2.3 换成新句子**；老井五帧的 text 一字不动。
- `title` 一律不动（改了会拆证物卡，见 §2.3 硬约束 2）。
- 证物基数校验：五帧热点补齐后，**证物卡数应仍是 27 张卡 / 58 条观察**（家具 19＋地标 8）。补热点时**不要新增也不要漏**。

### 3.4 边缘空白房子（decor）

- 位置以 **`lab/_l11_final.json` 的 `edge_houses`（12 栋）** 为准。12 栋清单（id / pos）：

  | # | id | pos | # | id | pos |
  | --- | --- | --- | --- | --- | --- |
  | 1 | lu_house | [64, 3168] | 7 | lu_house | [32, 2400] |
  | 2 | lu_house | [1024, 3168] | 8 | zhou_house | [32, 2816] |
  | 3 | zhou_house | **[1984, 3328]** 🔴 | 9 | zhou_house | [4416, 1856] |
  | 4 | zhou_house | [2560, 3328] | 10 | lu_house | [4160, 2656] |
  | 5 | lu_house | [3136, 3168] | 11 | zhou_house | [4416, 800] |
  | 6 | zhou_house | [3968, 3328] | 12 | zhou_house | [4416, 1120] |

  - 🔴 **第 3 栋（`zhou_house [1984,3328]`，384×224 ⇒ 占 1984–2368 × 3328–3552）压在 A5 的竖路车道南段（polygon x2016–2080、y1920–3600）上** —— 总策划已实测确认（其余 11 栋零冲突、零出界、零压河）。**必须把它挪到 `[2080, 3328]`**（占 2080–2464 × 3328–3552：右边界 2464 < 竖路 2080 之东端不冲突 ⇒ 已避开车道；与第 4 栋 zhou[2560,3328] 留 96px；与第 2 栋 lu[1024,3168] 留 416px；与山 polygon（4416–4800）无冲突）。
  - 挪完之后**必须用最终 frames 重跑一次冲突校验**：与同帧所有其它实体（主屋、circle 地标、坝、碑、红绿灯、山 polygon、路标、road rect、河/路/停车场/车位 polygon、其它 decor 房子）**不重叠**；**不压河、不压主路、不压竖路车道**；**不出世界边界**（4800×3600）；decor 房子两两之间留 ≥96px 间隙。
  - 若还有别的冲突，**只挪 decor 房子**（保持 12 栋、保持「在离世界边界 ≤512px 的外圈带」这个原则），并在反馈文档里逐栋列出挪动。**不要动主屋、不要动路。**
- `decor` 的语义：**只画底色/轮廓，整栋 lot 挡路，不生成任何热点、不画墙/门/家具/屋顶**。

### 3.5 叙事硬约束（改数据时不能破坏）

| 约束 | 来自 |
| --- | --- |
| 磨坊一直盖在井上（A3 井在 mill_a3 的 lot 内） | `docs/story.md:415` §7.1 |
| A4「井口就在超市西墙外，只隔一道墙」（井东缘 → 超市西墙 ≈ 32px） | `docs/story.md:416`/`:425` |
| A5「井现在在车道正下方」（井心落在竖路车道内） | `docs/story.md:426` |
| A1–A2 路绕开井和磨坊，A3 开始取直 | `docs/story.md:423-424`、`:428`「路不会自己变直。」 |
| 界碑 A5 砌进小学围墙内壁 | 用户 M15「界碑跟着学校走」 |
| 沈家四代同址且逐代变大；陆家/周家全在路南 | 用户 M15 |
| A4 与 A5 的 market 同址（位置不变是核心玩法） | 用户 M1、既有裁定 |
| A5 十字路口＝环岛，树在环岛中心，停车场三车位 | 用户 M3、既有裁定 |

---

## §4 引擎改造

### 4.1 decor 房子（`scripts/frame_data.gd` ＋ `scripts/world_view.gd`）

**`scripts/frame_data.gd`**：house shape 遇到 `"decor": true` 时：
- 碰撞：**用 `HouseShape.lot_rect(hdata, hpos)` 整块作为碰撞体**（一整块实心，不留门洞）⇒ 这就是「空间约束」。
- 热点：**不调用** `HouseShape.hotspots(hdata, hpos, year)`（否则同一个 id 出现十几次会生成十几次家具热点，证物卡数会炸）。

**`scripts/world_view.gd`** `_draw_house_base()`：house shape 是 decor 时：
- 只画一层底色（或 base 图当剪影），**不画墙、不画门、不画屋顶、不画家具**。
- 不进 `_collect_front()` 的 walls/door/roof/furniture 四类（否则会画出内部结构）。
- 建议实现方式：给 decor 房子一个统一的低调配色（深灰褐 `#4a4740` 之类），让玩家一眼看出「这是背景房子，进不去」。

### 4.2 平铺贴图（河 / 路 / 田 / 山丘）—— 世界放大后必须改

现状三处硬编码都会在 4800 宽的世界下画错：

1. `scripts/world_view.gd:263` 河贴图画布写死 `Vector2(3200, 416)`。
2. `_scene_bboxes()` 把 road rect 合成一个外包矩形贴整张路图（3200 宽的图贴到 4800 宽 ⇒ 拉伸）。
3. `label==""` 的 rect 合成一个 field bbox。

**做法（按优先级）**：

- **路**：改为**逐个 road rect 平铺**（32×32 瓦，`assets/village/scene/road_a4_tiles.png` / `road_a5_tiles.png` 等，美术侧按「单方格复用」出）。颜色口径不变：A1–A4 土黄 `#8a7a5a`、A5 柏油 `#56564f`。贴图缺失时回落到原来的 `draw_rect` 纯色 ⇒ **本线不依赖美术到位也能跑**。
- **田**：每个田 rect 各自平铺（`field_a*_tiles.png`），不再合成一个 field bbox。
- **山丘**：每个山 rect 平铺 `hill_tiles.png`（美术若还没出，回落纯色块 `#4a5a3a`）。
- **河**：河是 polygon，平铺需要 `draw_polygon(points, colors, uvs, texture)` ＋ UV ＝ point/32，并在节点上开 `texture_repeat`。**如果实现有困难，允许本轮先保留纯色 `draw_colored_polygon` 兜底**，把贴图平铺标为「美术到位后再接」，并在反馈文档里写明。

**通用做法建议**：给 rect/polygon 增加一个可选字段 `surface`（值如 `"road"`/`"field"`/`"hill"`/`"river"`），引擎按它查平铺贴图；没有 `surface` 的 shape 行为完全不变（这样老数据不回归）。

### 4.3 新 rect 类别（`surface` / `prop`）—— 不新增 shape 类型

用户 M14：「只需要把区域圈定好（方格），到时候用贴图就行」⇒ **不新增 `type`**，只用 rect 的可选字段：

| 字段 | 含义 | 谁用 |
| --- | --- | --- |
| `"surface": "<贴图键>"` | 这个 rect 按该贴图键平铺（背景层） | 田地 `"field"`、道路 `"road"` |
| `"prop": true` | 这个 rect 当作前景小物件画（可带 `label` 找贴图），**不挡路** | 路标 `"路标"`、稻草人等 |

⚠️ **两处与 v3 数据不一致，以 v3 为准**：

- **山丘在 v3 里是 `polygon`（`label:"山"`，5 个点，四块），不是 rect**（bbox：(1408,2400)–(1856,2688)／(2080,2624)–(2528,2880)／(3072,2624)–(3520,2880)／(4416,3104)–(4800,3328)，均 `solid:true`）。`scripts/world_view.gd` 的 polygon 分支只认河（`scene_tex(frame.id,"river")`），拿不到河图就 `draw_colored_polygon` ⇒ **山会画成纯色多边形**。本轮**允许山保持纯色**（美术的 `hill_tiles.png` 还没出），但你**必须在反馈文档里写明「山为纯色 polygon，贴图接线留待美术到位」**。若你要顺手支持山贴图，可给 polygon 加 `"surface":"hill"` 并在 polygon 分支里加一个平铺分支——**但不许因此改动 river 的既有行为**。
- **路标在 v3 里是 `rect` 16×32 且 `solid:true`**（4 块：x=352/1024/2400/4128，y=1632）。这有两个问题：①`solid:true` ⇒ 它是一根 16×32 的实心柱，**会挡路**（玩家撞上）；②`_is_standing_rect()` 的判据是「宽≤32 且 高≤64 且 solid」⇒ 它会进前景层 y-sort，按 label 找贴图（`scripts/world_view.gd:766-774` `_prop_tex()`，没有路标贴图 ⇒ 画色块）。**本轮请把 4 块路标改成 `"prop": true` 且 `solid: false`**（不挡路、仍进前景层），并扩展 `_collect_front()` 收 `prop:true` 的 rect（`sort_y = rect.end.y`）。

引擎侧要点：
- `_is_standing_rect()` 现在的判据（宽≤TILE 且 高≤2*TILE 且 solid）会让「山丘 480×320」「路标 16×16 但 solid:false」都画不出来：
  - 山丘走 `surface` 分支（背景层平铺）⇒ 不进前景层。
  - 路标走 `prop: true` ⇒ **必须扩展 `_collect_front()`**，让它也收 `prop:true` 的 rect（`sort_y = rect.end.y`），否则路标会完全看不见。
- **排序链只加不减**：新增的 prop 条目只能追加，不得改动既有条目的 `sort_y` 计算（§0.5 坑 1）。

### 4.4 小地图（`scripts/hud.gd` ＋ `scripts/main.gd`）—— **本段归 L12 执行，本线不做**

用户 M6：加小地图方便检视位置。

- **落位**：右上角，**顶条以下、检视卡以上**。建议 200×150 px，底边距屏底 ~140px（避开底条 60px 与检视卡）。
- **数据**：`hud.gd` 加 `func sync_player(pos: Vector2) -> void`（或把玩家坐标塞进现有 `sync()` 的参数里），由 `scripts/main.gd:336` 附近每帧调用。
- **内容**：世界矩形 4800×3600 的缩略图 ＋ 玩家位置点 ＋ 关键地标点（井/槐/碑/超市/小学/玩具店，五个时代各一份，从 `frames.json` 的 shapes 里取 circle/house 的位置即可）。地标点在不同帧位置不同 ⇒ **每帧要跟着切时代换**。
- **不许碰**：顶条（36px）、底条（60px）、检视卡（宽 1200、`x=40`）。`_mdtest/hud_layout_check.gd` 的既有断言一条都不许改，只许**加**小地图自己的断言（见 §6）。
- 底色/边框要低调，不能抢戏。

### 4.5 提速（`scripts/main.gd` ＋ `scripts/player.gd`）—— **本段归 L12 执行，本线不做**

- `scripts/main.gd:12` `PLAYER_SPEED := 120.0` → **180.0**（×1.5，与世界放大 1.5 倍同倍 ⇒ 观感速度不变，但用户明确要「速度放大」）。
- `scripts/player.gd:73`/`:96` 走路动画频率 `walk_phase * 9.0` → **6.0**（不降频会变成滑冰）。
- `CHAR_RADIUS`/`RADIUS` 保持 14 不变。

---

## §5 数据与叙事的同批改（顺序很重要）

**文本与数据必须同批改**，否则中间态会出现「地图上树在井边、文案说树跟井无关」的矛盾：
1. 先改 `data/frames.json`（五帧 + 热点文案）。
2. **L13 改** `docs/story.md`、`docs/npc.md`、`docs/HANDOFF.md`（本线不碰；两条线挨着交付）。
3. 再改引擎（decor / 平铺）。**小地图与提速归 L12。**
4. 最后改测试期望值并跑全回归。

---

## §6 测试改造（**只有这几处允许改**）

### 6.1 必红、要改期望值的 5 处（已授权）

| 文件:行 | 现状 | 改成 |
| --- | --- | --- |
| `_mdtest/greybox_check.gd:57-58` | `world_size == Vector2(3200,2400)` | `Vector2(4800,3600)` |
| `_mdtest/greybox_check.gd:291`、`:372` | `range(240, 2400, 32)` | `range(240, 3440, 32)` |
| `_mdtest/camera_check.gd:44` | `big.setup_viewport(Vector2(3200, 2400))` | `Vector2(4800, 3600)` |
| `_mdtest/camera_check.gd:51-52` | clamp 上限 `(1920, 1680)` | `(3520, 2880)` |

### 6.2 随布局必然要同步的断言（同一文件内，期望值随新坐标改，**不许删**）

| 位置 | 断言 | 怎么改 |
| --- | --- | --- |
| `greybox_check.gd:20-25` / `:27-33` / `:37-42` | `HOUSE_MAP` / `HOUSE_MAP_A2` / `HOUSE_MAP_A3` 的 pos/size | 换成最终 frames 里对应房子的 pos 与 lot 尺寸 |
| `greybox_check.gd:59-60` | 起点可站 | 起点变了，期望不变（仍要可站） |
| `greybox_check.gd:62-73` | 四向边界探测（`y=260` 等） | 世界高 3600，探测点相应调整 |
| `greybox_check.gd:138-139` | `A2_MILL_SAME_SPOT`（磨坊三帧同址） | 改成新的三帧同址坐标 |
| `greybox_check.gd:182-189` | `DOOR_PASSABLE` 四个院门点 | 改成 v3 的实际院门点：**A1 = (1872,784) 磨坊／(272,688) 沈家／(3088,2032) 周家／(1456,2192) 陆家**；A4 = (2736,1424) market／(1008,1424) shen_a4／(1008,1808) zhou_a4／(2672,2480) zheng_a4；A5 = (1904,1264) school／(2736,1424) market／(2608,1872) toyshop／(1008,1808) zhou_a4（这些是子代理实测「院门可站」的点） |
| `greybox_check.gd:202-209` | `WALL_STOP_Y` 期望 800~816 | 改成新布局的期望区间 |
| `greybox_check.gd:251-261` | `REACH_MAP` / `UNEXPLAINED_BLOCKS=0` / `REACH_OK` | 数值会变，**断言结构不许删**；若 `UNEXPLAINED_BLOCKS` 不为 0，要查清是哪些格被挡并写进反馈 |
| `greybox_check.gd:192-194` | `HOTSPOTS >= 10` | 不变 |
| `greybox_check.gd:211-218` | `TIME_FWD_REACHED=[1,2,3,4]` | 不变（结构不许改） |
| `greybox_check.gd:229-233` | `A1_MILL_INTERIOR_FREE` / `A1_MILL_DOOR_FREE` / `A1_WELL_FREE=false` | 语义不变，坐标变 |
| `greybox_check.gd:284` | `const ROAD_Y := 1664` | **不变**（v3 主路仍是 `[0,1664,4800,64]`） |
| `greybox_check.gd:34` | `const OLD_WELL := Vector2(1360, 848)` | **改成 `Vector2(2048, 848)`**（v3 的井位；y 一样，x 变了） |
| `greybox_check.gd:202-209` | 撞墙测试起点 `(1248,904)`、期望 `WALL_STOP_Y` 800~816 | 起点要避开井（v3 井在 x2048，起点 x=1244 仍可用）；期望值按 v3 的 `mill_a1 [1632,448]` lot 南沿重算（lot 高 544 ⇒ 南沿 448+544=992 ⇒ 期望区间相应改成 976~992 附近），**自己算，别抄** |
| `greybox_check.gd:211-218` | `TIME_FWD_REACHED` 起点 `(1400,1120)` | 起点要落在**五帧都空地**的位置；v3 的 `(1400,1120)` 在 A1–A5 都在空地（子代理已实测可达），可以保留，但你要用新 frames 再验一次 |
| `greybox_check.gd:229-233` | 磨坊内部 `(1400,520)`／门洞 `(1456,784)`／老井 `(1360,860)` | 全部换成 v3 坐标：磨坊内部 `(1900,700)` 附近、门洞 `(1872,784)`、老井 `(2048,880)`（A1 井 r32 solid ⇒ 仍应不可站） |
| `greybox_check.gd:236-239` | 三个 HOTSPOT 断言的查询点 | 老井 → `(2048,848)`；老槐 → A1 `(2048,1536)`；A1 磨坊账桌 → 按 v3 `mill_a1 [1632,448]` 的家具相对格换算（家具坐标是 lot 原点 + 格×32） |

### 6.3 既有断言一条不许动（会红的自己想办法）

`_mdtest/sort_check.gd:240/:250/:261`、`_mdtest/asset_draw_check.gd:287/:289-290`、`_mdtest/greybox_check.gd:170`（`A3_OLD_WELL_UNDER_MILL`）、`:189`、`:208-209`、`:218`、`:233`、`:255`、`_mdtest/evidence_archive_check.gd`（证物 27 卡/58 观察）、`_mdtest/hud_layout_check.gd` 全部既有断言。

### 6.4 新增断言（只许加）

1. `_mdtest/greybox_check.gd`：**边缘 decor 房子不生成任何热点**（证物卡数仍是 27/58）。
2. `_mdtest/greybox_check.gd`：五帧各自 `house` 两两不重叠、不压主路、不压河、不出界。
3. （小地图断言归 L12 写在 `_mdtest/hud_layout_check.gd`，本线不碰该文件。）
4. `_mdtest/greybox_check.gd`：**界碑 A5 在 school 的 lot 内**；**A4 井与 market 西墙间距 ≈32px**；**A5 井心落在竖路车道内**（叙事硬约束的常驻断言）。
5. `_mdtest/greybox_check.gd`：**A1 弯路能连续走通** —— 沿 A1 的 29 块弯路 rect 从西端到东端逐格推进（用 `tl.move_space` 或直接 `is_free` 连通性检查），中途卡住就打印卡住的坐标。（这是 §2.5 那个已知取舍的守门断言。）
6. `_mdtest/greybox_check.gd`：**12 栋 decor 房子不压主路/竖路/河**且不出界。

### 6.5 回归要跑全的套（当前项目有 7 套）

`greybox_check` / `camera_check` / `hud_layout_check` / `asset_draw_check` / `sort_check` / `display_check` / `evidence_archive_check`。
每套都要打出 `..._CHECK_DONE fails=0`。**看关键字不看退出码。**

---

## §7 白名单与纪律

1. **只精确 `git add <文件>`，绝不用 `git add -A`。** 仓库里有美术线的未提交 PNG 和用户自己删的文件。
2. commit message 用中文，格式建议：`feat(world): 世界放大到 4800×3600 + 五帧重排 + decor 边缘房子 + 树井文案改口`。
3. 提交前 `git diff --stat` 自检，确认只包含自己那批文件。
4. **不要 push**（GitHub 推送由项目总策划按用户定时指令统一做）。
5. 反馈文档 **`docs/FEEDBACK-l11-world-rebuild-exec.md`** ≤120 行（**不要写 `docs/FEEDBACK-world-rebuild-exec.md`——那是旧世界重构线的存档**），必须包含：
   - 改了哪些文件、各改了什么；
   - `lab/_l11_final.json` → `data/frames.json` 的差异清单（**尤其是文件缺 `ground`/hotspots、你补了什么**）；
   - §2.5 那个「A1 弯路 4 邻接断裂」的实测结论与你的处理（补块还是不改）；
   - 装饰房子是否挪过位置、为什么；
   - §6 改了哪些断言、期望值从多少到多少；
   - 七套回归的实际输出关键字；
   - **未解决/做不到的地方**（例如河贴图平铺没做成、`:965` 换了别的物证）；
   - §2.4 D2 同步清单里你实际改了哪些、没改哪些。
6. 需要美术资产但还没有的（山丘瓦、路标、新的平铺瓦），**在反馈文档里列出来**，但**不要自己去画、不要改 `assets/**`**。

---

## §8 验收清单（自检打勾）

- [ ] `data/frames.json` 的 `world` ＝ 4800×3600，`start_pos` 可站且在主路上。
- [ ] 五帧 `ground` 都在（a1 `#6e7a4c`/a2 `#68744a`/a3 `#6a6a44`/a4 `#6f6a52`/a5 `#7a7a76`）。
- [ ] 五帧 `hotspots` 全部补齐（5/5/5/6/7 条），标题全对，老槐四帧新文案到位，老井文案一字未动。
- [ ] 边缘 **12** 栋 decor 房子（`lab/_l11_final.json` 的 `edge_houses`，含 §3.4 指定挪位的那一栋）：零重叠、零出界、零压路河；**不生成热点**。
- [ ] 磨坊盖井、A4 井在超市西墙外一道墙、A5 井在车道正下方、界碑在小学围墙内 —— 四条叙事硬约束由断言守住。
- [ ] 沈家四代同址且逐代变大；陆家/周家全在路南；A4/A5 的 market 同址。
- [ ] 老槐半径 32/64/96/96/160 未变；`title` 仍是「老槐」、`label` 仍含「槐」。
- [ ] `docs/story.md` §7.3 已重写（无「井」字）、`:965` 左列已换、右列保留。
- [ ] `docs/npc.md` 七处、`docs/HANDOFF.md:378` 已改。
- [ ] decor 房子在游戏里只显示为背景体，进不去，里面没有家具热点。
- [ ] 路/田/山丘在 4800 宽的世界下不再拉伸（逐 rect 平铺，缺贴图时回落纯色）。
- [ ] 七套回归全绿（`fails=0`）。
- [ ] 证物卡数仍是 27 张 / 58 条观察。

---

## §9 不要自作主张的事

1. **不要改 `_ref/houses/houses_data.json`**（房屋大小、家具、线索家具都不动）。「沈家逐代变大」靠的是既有 lot 尺寸，不是本线能改的。
2. **不要改路宽**（用户 M13 延后）。
3. **不要改树的半径刻度**（用户 M10 延后）。
3b. **不要做小地图、不要改速度、不要改走路动画频率**（归 L12，文件域不同）。**不要改 story/npc/HANDOFF**（归 L13）。
4. **不要新增 shape type**（用户 M14：只用方格圈区）。
5. **不要动 `assets/**`、`_ref/art/**`**。
6. **不要删任何既有测试断言**；要改的是**期望值**，不是断言本身。
6b. **不要挪动主屋**（v3 的 `lu_house [1248,1856]` 离环岛外缘只剩 2px 余量，挪了就压）。要挪只挪 decor 房子。
7. **不要改证物模型**（`scripts/evidence_store.gd`/`evidence_archive.gd` 不动）。
8. **不要 push**。
9. 不要把 `lab/_l11_*` 临时脚本当产物提交（除非里面有你想留下的基准文件，且要显式 add）。

---

## §10 收工

1. 七套回归跑一遍，把关键字贴进反馈文档。
2. `git add` 精确那批文件 → `git status` 自检 → commit。
3. 写 `docs/FEEDBACK-l11-world-rebuild-exec.md`（≤120 行）。
4. 交回总策划验收。
