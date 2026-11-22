# 美术资产消费点接入线 · 进度存档

> 存档时间：2026-11-22 17:05（首次）／**2026-11-22 19:35（视觉验收后修订）**
> 任务文档：`docs/PROMPT-asset-consumption-exec.md`
> 状态：**代码已全部写完、回归全绿、截图已验证、视觉验收通过；尚未 commit（按约定由总策划统一提交）**

---

## 〇、2026-11-22 19:35 修订：修掉「双份墙」

### 症状
房子截图里墙是**两层**：base 图里画好的墙顶面/南立面，被引擎画的墙色块盖住，
视觉上像「墙被画成另一种颜色」。像素级比对定位：
`a1_shen_house.png` vs `assets/village/houses/shen/a1_base.png`
（shen_a1 world pos=(128,640)，base 画布左上 = 世界 (128,608)）

| 采样 | base 图 | 截图 | 判定 |
|---|---|---|---|
| 地面/院子/田块 cy=64,128,160 | (196,179,146) | (196,179,146) | ✅ 一致 → 锚点公式没错 |
| 墙顶面 cy=0 | (232,215,184) | (201,168,120) | ❌ 被引擎 `WALL_TOP #c9a878` 覆盖 |
| 南立面 cy=32 | (208,184,146) | (140,107,74) | ❌ 被引擎 `WALL_COLOR #8c6b4a` 覆盖 |

⇒ 结论：**base 图锚点/位置公式正确**，是引擎多画了一层墙。

### 根因
`_ref/art/gen/_gen_shells.py` 的 `paint_base()` 里，base 图**已经画好了**：
墙顶面（`draw_cap`）、南立面（`draw_facade`）、门窗（`draw_window`）、房门（`draw_door`）、
院门（`draw_gate`）。而 `world_view.gd` 的 `_draw_walls_row()` 与 "door" 分支
**又用色块画了一遍**墙顶面/南立面/门 → 双份墙。

（`_draw_walls_row()` 的 `with_body` 参数原来只控制「墙格本体」，
墙顶面和南立面是**无条件**画的 —— 这是 bug 根源。）

### 修法
`scripts/world_view.gd`：
- 新增 `static func _art_walls(sid: String) -> bool` —— 该栋是否由美术 base 图接管墙。
- "walls" 分支：有 base 图 → `continue`（不画色块）；无图 → 原样画引擎色块。
- "door" 分支：同上（门/院门也在 base 图里）。
- `_collect_front()` 的 **door 条目补了 `"sid"` 字段**（原来没有，门条目不知道属于哪栋房子）。
  ⚠️ 这只加了字段，**没动 sort_y / seq / 条目数量** → 排序不变式守住。

**关键**：`walls`/`door` **条目仍然留在排序链里**（A1 前景层 39 行墙 + 13 个门），
只是「不画」而不是「不收集」。这样美术图接管后，玩家的遮挡关系仍由数据决定。

### 验证
- 截图对比：双份墙消失，墙顶/立面/门窗/院门全部还原成美术原图。
- 六套回归全绿（见下）。
- `asset_draw_check` 新增 4 条断言（`_check_art_walls()`）：
  墙归属与 base 图存在性一致（不符 0 栋）、12 栋全部由美术图接管墙、
  前景层仍有墙条目 39 行、仍有门条目 13 个（排序链没被删）。

### 顺带发现（不改，只记录）
`lu_a3` 是废墟（`ruin:true`），base 图由 `paint_ruin()` 画 —— 只有**矮墙基**，没有墙顶面+立面。
所以「有 base 图就不画引擎墙」对废墟也成立（废墟没有高墙），截图 `a3_lu_ruin.png` 正常。

---

## 一、这一线干了什么

让美术同学的 PNG **真的在游戏里画出来**。之前美术资产交付了 126 张 PNG + 91 条 manifest，
但引擎里一个消费点都没有 —— 全是色块占位。

架构按用户 2026-11-22 拍板的 **A 方案**：
贴图绘制**接进视觉机制线已交付的 `world_view.gd` 现有绘制循环**，
**不新建绘制节点、不设 z_index、不动排序不变式**。

---

## 二、改了哪些文件（全部未 commit）

| 文件 | 状态 | 改了什么 |
|---|---|---|
| `scripts/asset_draw.gd` | **新建** | 纯静态工具：贴图加载 / manifest 索引 / 家具匹配 / 锚点计算 / 场景图索引 |
| `scripts/world_view.gd` | 改 | 4 处消费点接进现有分支 + 墙/门改由美术 base 图接管（详见下） |
| `scripts/player.gd` | 改 | 主角精灵表接入（`draw_self()` 内） |
| `_mdtest/asset_draw_check.gd` | **新建** | 专项自检，**65 条断言**（含墙归属 4 条） |
| `_mdtest/asset_shot.gd` | **新建** | 定点截图器（不带 `--headless` 才有像素），11 处定点 |
| `_mdtest/assets/*.png` | **新建** | **11 张**验证截图 |

**没动**：`scripts/house_shape.gd`、`data/frames.json`、`_ref/houses/houses_data.json`、
manifest、任何 PNG、任何美术资产。

---

## 三、world_view.gd 的 4 个消费点

### 1. 房子 base 图 → `_draw_house_base()`
- 有 base 图：贴 `Rect2(hpos.x, hpos.y − EXTRUDE, lot.w, lot.h + EXTRUDE)`（左上角锚点）
  —— 顶部多出的一格就是墙立起来的高度，与 `_gen_shells.py` 文件头冻结的约定一致。
- **有图时替代**原来的第 1 层 lot 底色 + 第 2 层房间色块；无图原样保留（缺图降级永久保留）。
- 墙（`_draw_walls_row`）**整条改由美术图接管**（见第〇节）：`_art_walls(sid)` 为真时引擎不画墙色块，
  因为 base 图里已经画好墙顶面 + 南立面 + 门窗 + 院门。

### 2. 家具 props 图 → `_draw_furniture()`
- 按 `f["name"]`（= short）查 manifest，`AssetDraw.prop_draw()` 一次算好贴图 + 落点。
- **落地按 houses_data 的 rect**，不按 manifest 的 w/h（美术只是外观，占地/碰撞仍读数据）。
- D6 底部中心锚点：贴图底边 = 占地底边，多出的那格在顶部。
- 线索家具仍画橙框；匹配不到（学校施工类词）→ 回色块，不报错。

### 3. 场景大图 → `_draw_back()`
- **路**：整张 `road_curved_tiles.png` / `road_straight_a3.png` 按**整帧路面 bbox** 贴一次。
- **田**：整张田图按**整帧田块 bbox** 贴一次。
- **河**：整张 `river_*.png` 贴到 `Rect2((0,0), (3200,416))` —— 与 frames.json 的河 polygon 同几何。
- **坝**：一张图对一个 rect。
- ⚠️ 路/田/河的大图上非目标区域是透明的，**必须按整帧 bbox 一次性贴**，逐格贴会丢路缘/田埂。
- 口径与 `_gen_scene.py` 对齐：`field_rects()` = 跳过 `road:true` 和 `label` 非空的 rect；
  `road_cells()` = road rect 逐 32px 格展开。

### 4. 场景小件 → `_draw_prop()`
- circle：label 含「槐」→ tree 图；含「井」→ well 图。
- rect：label 含「碑」→ stele 图。
- 贴图按半径居中、**底边对齐圆的底边**（占位大小不变），缺图回原色块。

---

## 四、player.gd 主角精灵

- 精灵表：`res://美术资产/主角/Sprite-主角-Sheet.png`（1152×32 = 36 帧，32×32 一格）。
- **方向分组是推出来的**（美术同学没给标记）：

| 方向 | 行走帧 | 站立帧 |
|---|---|---|
| down | 0,1,2,3 | 16,17,18,19,20 |
| left | 4,5,6,7 | 21,22,23,24,25 |
| right | 8,9,10,11 | 26,27,28,29,30 |
| up（背面） | 12,13,14,15 | 31,32,33,34,35 |

  判据：按「脸部皮肤像素的左右分布」分类（背面帧只见金色头发，skin 像素极少）。
  验证脚本：`lab/_hero_all.png`（36 帧 3 倍对照图）。
- 贴图落点：脚底对齐 `position.y + RADIUS`，走路时按 `walk_phase` 在 4 帧里循环。
- 缺图 → 回退原来的「圆 + 朝向三角」灰盒画法（`_draw_fallback`）。

---

## 五、回归结果（全绿）

```
greybox_check     WORLD_OK=true  START_OK=true  HOTSPOTS_OK=true  REACH_OK=true
sort_check        SORT_CHECK_DONE fails=0
camera_check      CAMERA_CHECK_DONE fails=0
display_check     CONTENT_SCALE_MODE=1 / ASPECT=1 / SIZE=(1280,720) / 纹理过滤=0(Nearest) / STRETCH_SCALE_MODE=0
hud_layout_check  HUD_CHECK_DONE fails=0
asset_draw_check  ASSET_DRAW_CHECK_DONE fails=0     ← 新增，65 条断言（60 PASS 计数见下）
```

> `asset_draw_check` 的 PASS 行数是 60（35 个 `_ok()` 调用点，其中 4 个在循环里，
> 循环展开后实际打印 60 行 PASS）；fails=0。

沙箱固有噪声（基线就有，与本线无关）：`Failed to open 'user://logs/...'`、
`Failed to read the root certificate store.`、pwsh 控制台中文乱码。

---

## 六、哪些图真能看到 / 哪些看不到

### ✅ 看得到（已截图验证）
| 类别 | 内容 | 验证截图 |
|---|---|---|
| base | 12 栋房子的院子/地板/门窗底图 | `a1_shen_house.png`、`a1_lu_house.png`、`a3_mill.png` |
| roof | 茅草顶/瓦顶（玩家在屋外才看得到） | `a1_mill_outside.png` |
| props | 床/桌/椅/柜/书架/牌位/水缸/花盆/灯笼等 | `a1_shen_house.png`（书架、牌位、水缸） |
| scene 大图 | 主路、田、河、坝 | `a1_mill_road.png`（河+坝）、`a3_field_road.png`（田+路） |
| scene 小件 | 老井、老槐、界碑 | `a1_well_tree.png` |
| 主角 | 36 帧精灵（4 方向） | 所有截图里的主角 |
| 废墟 | `lu_a3` 残墙基 + 杂草（`paint_ruin`） | `a3_lu_ruin.png` |

### ❌ 看不到（原因明确）
| 内容 | 原因 |
|---|---|
| 学校施工类家具（跑道×56、课桌×48、未拆封货架×18 等） | **manifest 里没有这些 id**（`_ref/art/_assets_a1a3/_a1a3_assets.json` 只有 91 条 props）→ 回色块。需美术补图或补 manifest。 |
| A4/A5 的 6 栋房子（shen_a4/market/school/toyshop/zhou_a4/zheng_a4）的家具 | A4/A5 的帧 `a4_2001`/`a5_2026` 的 `shapes` 是**空数组** → 画不到任何东西（不是贴图问题，是帧数据还没搭）。 |
| A4/A5 的场景图 | 同上，没有帧 → `AssetDraw.scene_tex()` 回 null → 色块降级。 |
| `lu_a3` 的屋顶 | 废墟（ruin），manifest 里**只有 base 没有 roof** → 回色块屋顶。 |
| 7 条同 short 多义家具（凳/粮囤/书架/单人床/双人床/木箱/长凳/八仙桌/柜/灶台/账桌/书桌/牌位/石磨/藤椅/灯笼/盆景 共 18 个 short） | manifest 一 short 多 id → 用 **short + 占地尺寸** 一起匹配（完全一致优先，否则 |Δw|+|Δh| 最小）。A1–A3 的 247 条命中里 footprint 全一致。 |

### ⚠️ 还没做（待拍板）
- **同学资产替换**：manifest 里 7 条 props 指向 `assets/village/_classmate/props/`（39 主图 + 45 变体），
  但只有 7 条被 manifest 引用，其余 32 张同学图**零消费点**。
  `docs/FEEDBACK-planner-art-import.md` 的阻塞③「替换（31 张尺寸一致）待拍板」**还没做**。
  建议：等这批贴图在游戏里跑通、视觉确认后再一次性全换。
- **主角朝向**：目前 up = 背面帧（帧 12–15/31–35），left/right 是侧脸帧。
  美术同学若补了真正的「向上」帧，换分组表即可。

---

## 七、接着做什么

1. ~~**看截图做视觉验收**~~ ✅ 已完成（2026-11-22 19:35）。
   验收中查出并修掉了「双份墙」（见第〇节）；其余 11 张截图全部确认：
   - 房子底图和墙的衔接没有错位（base 图顶部那格 = 墙高）
   - 家具贴图底边对齐占地底边
   - 河/路/田的整帧 bbox 贴法没有漏边
   - 废墟态（`lu_a3`）正常
2. **决定阻塞③**：同学生产图（39 张）要不要替换 manifest 里那 7 条 + 补 32 条新 id。
3. **决定 A4/A5**：帧数据还没搭，贴图接好了但没内容可显示。
4. ~~**写结束报告**~~ ✅ 已写（见回复正文）。
5. **不 commit**（按约定由总策划统一提交）。

### 重跑命令（Windows）

```powershell
$godot = 'D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe'
# 回归（headless，看关键字不看退出码）
foreach ($s in @('sort_check','greybox_check','camera_check','display_check','hud_layout_check','asset_draw_check')) {
  & cmd /c "`"$godot`" --headless --path . --script _mdtest/$s.gd > lab\_$s.txt 2>&1"
  Get-Content "lab\_$s.txt" | Select-String -Pattern "DONE|OK=|FAIL"
}
# 截图（**不能**加 --headless，否则拿不到像素）
& cmd /c "`"$godot`" --path . --script _mdtest/asset_shot.gd > lab\_shot.txt 2>&1"
```

---

## 八、踩坑记录

- **`houses_data.json` 的 `lot` 是闭区间 `[x0,y0,x1,y1]`**，不是宽高。`lot_rect()` 才做 +1。
  写断言时直接拿 `lot[2]` 当宽度会全部算错（第一次自检就是这里挂的，23 张不符）。
- **GDScript 里 `var x := JSON.parse_string(...)` 会报 "inferred from a Variant value"**（warning 当 error），
  必须显式写 `var x: Dictionary = JSON.parse_string(...)`。
- **headless 模式下不能管道捕获 stdout**（EPERM），用 `cmd /c "godot ... > out.txt 2>&1"`。
- **截图必须去掉 `--headless`**，否则画面是空的。
- **镜头 lerp 要钉死**：`camera.set("offset", want)` + `camera.call("_apply")`，否则拍到镜头半路。
- 玩家站在 wings 里时屋顶整块消失（既定机制，不是 bug）→ 想拍屋顶要把玩家放到屋外。
- `_mdtest/sort_check.gd` 会 `WorldView.new()` 并调 `_collect_front()` / `_player_inside()`
  → 新加的静态/实例方法名不能跟这些撞。
- **美术 base 图里已经画好墙顶面/南立面/门窗/院门**（`_gen_shells.py` 的
  `draw_cap`/`draw_facade`/`draw_window`/`draw_door`/`draw_gate`）——
  引擎再画一遍就是「双份墙」。这是本线最容易漏的一条：
  只把 base 图「贴上去」不够，还得**关掉引擎的墙/门色块**。
- 查「双份墙」的最快办法：**像素级比对 base 图与截图**。
  先比地面（对得上 → 锚点公式正确），再比墙行（对不上 → 是引擎多画了一层，不是错位）。
  锚点换算：base 画布左上 = 世界 (lot_x, lot_y − 32)；截图 screen = world − 相机 offset。
