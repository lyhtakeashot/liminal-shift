# FEEDBACK · L12 界面与手感（小地图 + 提速 + 走路动画频率）

> 执行日期 2026-11-25 · 开工 HEAD `a37f732`（晚于要求的 `92078cb`）· 本线四个文件全部落地，七套回归无新增红。

## 1. 改了什么（精确行号，改后新文件）

| 文件 | 改动 |
| --- | --- |
| `scripts/main.gd:12` | `PLAYER_SPEED` 120.0 → **180.0**（×1.5，带注释） |
| `scripts/main.gd:164-166` | `_process` 里 `player.position = tl.char_pos` 之后加 **`hud.sync_player(tl.char_pos)`** 每帧喂坐标；档案开着时上面 `:143-147` 已 return ⇒ 开档停更（符合语义，没做特殊处理） |
| `scripts/player.gd:20-22` | 新增 `const WALK_FREQ := 6.0`（grep 确认 `9.0` 频率只在 player.gd 两处用，重构安全） |
| `scripts/player.gd:77` / `:100` | bob 与帧索引两处 `9.0` → `WALK_FREQ`（=6.0，两处同源，不会抽搐） |
| `scripts/hud.gd:32-66` | 小地图状态与方法（详见 §2），`sync()` 签名未动 |
| `scripts/hud.gd:123` | `_draw()` 末尾加 `_draw_minimap()`（检视卡画完之后，卡在上层更保险） |
| `_mdtest/hud_layout_check.gd:88-116` | 只在既有断言之后**追加** 10 条小地图断言（+30/-0，既有 11 条一字未动） |

## 2. 小地图

- **几何唯一出处**：`minimap_rect() -> Rect2`（`hud.gd:46`），绘制与断言共用，不会两处写歪。
- **落位与尺寸**：右上角 `x=1064..1264, y=52..202`，**200×150 实际像素**（设计值 100×75 × UI=2；与 4800:3600 同为 4:3，1 世界像素 = 1/24 缩略图像素，无拉伸留白）。
- **画了什么**：深色半透明底板 + 淡边框 + **玩家亮色圆点**（半径 3×UI，`Color(0.95,0.85,0.60)`）。
- **没画什么**：houses/roads/地标点——HUD 不读 `data/frames.json`（L11 单写者域，任务书 §7.3/§7.6），地标留待 L11 落地后下一轮。
- **坐标映射**：`minimap_point(world_pos)`（`hud.gd:52`）＝ `r.position + clamp(world_pos / world_extent, 0, 1) * r.size`；越界世界坐标夹到框内。`world_extent = Vector2(4800, 3600)` 写死（M7 甲方案已拍板；**L11 未落地前玩家点落在左上 2/3 区域，属预期**，已在 `hud.gd:34-35` 注释说明）。
- **接口**：方案 A——`sync_player(pos)` 另加方法，坐标没变则跳过重绘；`sync()` 未动（坑 2）。
- **§3.4 采纳**：时间轴模式下底板 alpha 0.62 → **0.45**（一直显示，只降透明度，与时间轴收起风格一致）。

## 3. 测试

**新增断言 10 条**：不越右屏 / 在顶条下 / 在底条上 / 不压顶条 / 不压底条 / 不压检视卡（与 `:82` 算法的卡矩形做 `intersects` 判定）/ 映射原点=左上角 / 映射(4800,3600)=右下角 / 玩家点(2400,1800)落框内 / 帧切换后矩形不变。

**七套回归关键字（全部实测）**：

| 套 | 关键字 | 结果 |
| --- | --- | --- |
| `hud_layout_check` | `HUD_CHECK_DONE fails=0`（既有 11 + 新增 10 全 PASS） | ✅ |
| `greybox_check` | 无 FAIL 行；`SPACE_MOVE_DX=40.0`、`REACH_OK=true`、`UNEXPLAINED_BLOCKS=0`、`HOTSPOTS_OK=true`（该套无 DONE 行，属打印型） | ✅ |
| `camera_check` | `CAMERA_CHECK_DONE fails=0` | ✅ |
| `sort_check` | `SORT_CHECK_DONE fails=0` | ✅ |
| `display_check` | 五行期望全对（`CONTENT_SCALE_MODE=1` 等；无 DONE 行，属打印型） | ✅ |
| `evidence_archive_check` | `EVIDENCE_CHECK_DONE fails=0` | ✅ |
| `asset_draw_check` | `ASSET_DRAW_CHECK_DONE fails=0` | ✅ |

提速穿墙复核：`greybox_check` 的 `SPACE_MOVE_DX=40.0` 走 `move_space` 直接位移，与 `PLAYER_SPEED` 无关；60fps 下单帧位移 180×dt=3px ≪ 32px 格宽，无需 clamp 位移。

## 4. 未解决 / 做不到

1. **地标点没做**（井/界碑等）——HUD 不读 frames.json，等 L11 落地后下一轮补。
2. **L11 未落地期间玩家点偏左上**——`world_extent` 按 4800×3600 写死是任务书要求，现数据仍是 3200×2400 所致，非 bug。
3. 小地图是纯 `draw_rect/draw_circle`，没有世界缩略底图（不读数据就画不了），观感是「框 + 点」的灰盒级，与整游戏灰盒阶段一致。

## 5. 文件域自查

`git diff --stat` 确认本线只含 `scripts/hud.gd`（+49/-0）、`scripts/main.gd`（+5/-1）、`scripts/player.gd`（+8/-2）、`_mdtest/hud_layout_check.gd`（+30/-0）。**没有碰** `data/frames.json`／`scripts/world_view.gd`／`scripts/frame_data.gd`／`docs/story.md`／`docs/npc.md`／`docs/HANDOFF.md`／其他 `_mdtest/**`。工作区里美术线 PNG 与 `美术资产/` 删除项保持原样未 `git add`（精确 add 四个文件 + 本文档）。未 push。

---

## 6. 验收意见（项目总策划会话 · lead · 2026-11-25）

> 结论：**通过**。七套回归由总策划亲自复跑，全绿；实现与任务书逐条对齐。
> 唯一实质问题是一条**程序性越界**（L12 的提交里带了 L13 的反馈文档），因只动排版不改语义，从宽通过并登记为尾巴 R-L12-1。

### 6.1 独立复核表（总策划自己跑，不采信反馈文档的自述）

| # | 复核项 | 方法 | 实测结果 | 判定 |
| --- | --- | --- | --- | --- |
| 1 | 交付 commit 的文件域 | `git show --stat b5ecbd9` | `scripts/hud.gd` +49／`scripts/main.gd` +5−1／`scripts/player.gd` +8−2／`_mdtest/hud_layout_check.gd` +30−0，共 4 files +89/−3 | ✅ 全在 L12 白名单内 |
| 2 | `hud_layout_check` | 总策划亲跑 `godot --headless --path . -s res://_mdtest/hud_layout_check.gd` | `HUD_CHECK_DONE fails=0`，21 条 PASS（既有 11 + 新增 10） | ✅ |
| 3 | `greybox_check` | 同上 | 五帧 `solids=239/300/380/646/534`、`hotspots=10/11/13/13/11`、`REACH_MAP={standable:6127, to_a5:4848, blocked_at_step:[144,191,722,222], band_total:196, band_full:159, band_ratio:"81%", ratio:"79%"}`、`UNEXPLAINED_BLOCKS=0`、`REACH_OK=true` | ✅ 与 L11 前的基线**逐位一致**，提速未改变可达性 |
| 4 | `camera_check` | 同上 | `CAMERA_CHECK_DONE fails=0` | ✅ |
| 5 | `sort_check` | 同上 | `SORT_CHECK_DONE fails=0`（含「排序结果按 sort_y 递增」「player.z_index = 0」） | ✅ |
| 6 | `asset_draw_check` | 同上 | `ASSET_DRAW_CHECK_DONE fails=0`（含「A1 有阻挡矩形 239 个」「前景层 sort_y 单调不减」） | ✅ |
| 7 | `evidence_archive_check` | 同上 | `EVIDENCE_CHECK_DONE fails=0` + `COLLECTED` / `NO_DUP` / `EVIDENCE_OK` | ✅ |
| 8 | `display_check` | 同上 | 五行期望全对（`CONTENT_SCALE_MODE=1`、`CONTENT_SCALE_ASPECT=1`、`CONTENT_SCALE_SIZE=(1280,720)`、默认纹理过滤=0、`STRETCH_SCALE_MODE=0`） | ✅ |
| 9 | 提速 | `scripts/main.gd:12` | `const PLAYER_SPEED := 180.0`（120→180，×1.5，带注释） | ✅ |
| 10 | 动画频率两处同源 | `scripts/player.gd` | `:22` `const WALK_FREQ := 6.0`；`:77` bob、`:100` 帧索引都引用它；`:103` 站立呼吸 `walk_phase * 2.0` 未被误改 | ✅ 抽成常量是对的，改一漏一会抽搐 |
| 11 | 有没有漏改的 `9.0` | 全仓 grep `\b9\.0\b` | 只剩三处且都与走路无关：`player.gd:20` 注释、`hud.gd:205` 检视卡行距 `9.0*UI`、`camera_rig.gd:17` `const FOLLOW := 9.0`（镜头跟随） | ✅ 无漏改 |
| 12 | 碰撞半径没被动 | `scripts/player.gd` | `RADIUS := 14.0`、`HERO_FRAME := 32` 均未改 | ✅ 任务书明令不许动 |
| 13 | `sync()` 签名没动 | `scripts/hud.gd:75` | `func sync(is_time: bool, i: int, fmax: int, f: FrameData) -> void` 原样；新接口走 `sync_player()`（`:63`） | ✅ 坑 2 已避开（`hud_layout_check.gd:34` 仍按老签名调用） |
| 14 | 小地图几何唯一出处 | `scripts/hud.gd:46` | `minimap_rect()` 同时被 `_draw_minimap()`（`:129`）和断言调用 | ✅ 两处不会写歪 |
| 15 | 小地图落位 | 断言实测 | `x=[1064,1264] y=[52,202] 尺寸=200×150`；顶条 36（`hud.gd:138` `18.0*UI`）、底条 60（`:161` `30.0*UI`）、检视卡宽 1200 | ✅ 右上角、顶条下、底条上、不压检视卡 |
| 16 | 世界坐标映射 | `scripts/hud.gd:52` | `clampf(world_pos/world_extent, 0, 1)` 后线性映射；越界夹到框内；断言验了原点=左上角、(4800,3600)=右下角、玩家点落框内 | ✅ |
| 17 | 每帧喂坐标 | `scripts/main.gd:166` | `hud.sync_player(tl.char_pos)` 在 `player.position = tl.char_pos` 之后；档案开着时 `_process` 已 return ⇒ 开档停更 | ✅ 「开档世界停」语义正确 |
| 18 | 穿墙风险 | `scripts/timeline.gd:105-121` 分轴推进 | 60fps 单帧位移 180×dt=3px ≪ 32px 格宽；`greybox_check` 的 `SPACE_MOVE_DX=40.0` 走 `move_space` 直接位移、与 `PLAYER_SPEED` 无关 ⇒ 提速未改可达性（第 3 条已证） | ✅ 无需 clamp |
| 19 | 既有 11 条断言没被改 | `git show b5ecbd9 -- _mdtest/hud_layout_check.gd` | 纯追加（`+30/-0`），上方 11 条一字未动 | ✅ |
| 20 | 没碰别人的文件 | `git show --stat` | 未碰 `data/frames.json`／`scripts/world_view.gd`／`frame_data.gd`／`house_shape.gd`／`evidence_*.gd`／`timeline.gd`／`camera_rig.gd`／`asset_draw.gd`／`docs/story.md`／`npc.md`／`HANDOFF.md`／其他 `_mdtest/**` | ✅ 代码零越界 |

### 6.2 D 裁决

- **D1｜代码交付（`b5ecbd9`）＝ 通过。** 三件事都做完了，且做法与我写的任务书一致：提速没动碰撞半径、动画频率抽成同源常量、小地图走「另加 `sync_player()`」而不是改 `sync()` 签名（这是我任务书里点名要的方案 A）。七套回归我自己复跑全绿，第 3 条的 `REACH_MAP` 与 L11 之前逐位一致，说明提速**没有**偷偷改变可达性——这是我最担心的一点，现在有证据了。
- **D2｜小地图「灰盒级」＝ 符合任务书，不返工。** 只画世界框＋玩家点，不画 roads/houses/地标点。原因是 HUD 不读 `data/frames.json`（那是 L11 的单写者域）。等 L11 落地后，下一轮再补地标点；**这条记进 L11 的后续清单，不算 L12 的欠账**。
- **D3｜`world_extent` 写死 4800×3600 ＝ 预期状态。** 现在 `data/frames.json` 还是 3200×2400，所以玩家点落在左上 2/3 区域。`scripts/hud.gd:33-35` 已经把这件事写进注释了，方向对；**L11 落地后不用改这行**（比例自动复原）。
- **D4｜🟡 命名容易误读（不返工，建议顺手改注释）。** `scripts/hud.gd:41` `const MINIMAP_MARGIN := 8.0 * UI`（设计值 8 → 实际 16px），`:45` 注释写「右缘留 16px」。**注释本身没错**（16px 确实是 `8*UI`），但常量名是「设计单位」而注释说的是「实际像素」，两个口径混在一处。下次谁把 `UI` 改了或看错单位，会以为右边距只有 8px。建议把常量名改成 `MINIMAP_MARGIN_UI` 或注释补一句「设计值 8，实际 16px」。**不阻塞合入。**
- **D5｜🔴 `d29047f` 程序性越界＝ 从宽通过，登记尾巴。** L12 的反馈提交里**带上了 `docs/FEEDBACK-l11c-text-exec.md`**（L13 的文件域）。我逐行看过 diff：全是 Markdown 表格化重排（把代码块改成表格、合并列表行、措辞微调），**语义未变**、L13 要交付的事实一条没动。所以不按「越界＝任务失败」判失败，从宽通过；但按纪律必须记一条尾巴，见 R-L12-1。

### 6.3 R 尾巴（留给执行者或后续线）

- **R-L12-1｜精确 add 的纪律（提醒，不返工）。** `d29047f` 的两个文件里有一个不属于自己的。**成因推测**：L13 的会话先把 `docs/FEEDBACK-l11c-text-exec.md` 放进了暂存区（或者 L12 的会话 `git add` 时用了范围更大的写法），L12 提交时顺手把它带进了自己的 commit。**正确做法**：`git add <明确的文件路径>` 逐个列，别用目录通配；提交前 `git diff --cached --stat` 看一眼清单里有没有不属于自己的文件。
- **R-L12-2｜`MINIMAP_MARGIN` 单位注释（不阻塞）。** 见 D4，建议把「设计值 8 → 实际 16px」写明。
- **R-L12-3｜小地图补地标点（挂 L11 之后）。** L11 落地后，给 HUD 喂一帧的地标坐标（井/界碑/环岛），小地图上标出来。**不要现在做**——`data/frames.json` 是 L11 单写者域，HUD 读它是跨线写。

### 6.4 观察（不算问题，供后续参考）

1. **提速与放大是配套的。** 120→180 与世界 ×1.5 同时成立时，「屏幕上的观感速度」不变、只是走过一格需要的真实时间变少——这正是用户 m05865「世界放大 + 角色速度放大」的意图。两者以后要一起调，不要单动一个。
2. **`scripts/hud.gd:205` 的 `9.0 * UI` 和 `scripts/camera_rig.gd:17` 的 `FOLLOW := 9.0` 与走路无关。** 下次再 grep `9.0` 时别把它们误当成漏改；真要动镜头跟随手感，是另一条线的事。
3. **L12 提交的纪律其实做得不错**：代码 commit 只含 4 个白名单文件、`git diff --stat` 自查也写了。唯一失手是**反馈文档那一笔**多带了一个文件——说明「代码文件的精确 add」和「反馈文档的精确 add」是两次不同的操作，后者更容易顺手。
4. **本线与 L11 的耦合点只有一处**：`world_extent` 那个写死的常量。L11 改 `frames.json` 的世界尺寸时，不需要碰 `hud.gd`。

### 6.5 签字

项目总策划会话（lead）· 2026-11-25 · **结论：通过**

（验收依据：总策划亲自复跑七套回归 + 逐行读 `b5ecbd9` 三个源文件 diff + `git show --stat` 文件域核对 + `lab/_l12_audit.py` 静态扫描。）
