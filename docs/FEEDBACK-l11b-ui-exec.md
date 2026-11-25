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
