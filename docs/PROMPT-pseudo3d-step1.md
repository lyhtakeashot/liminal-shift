# 任务书：室外伪 3D —— 第 1 步（只改 `world_view.gd`）

> 目标会话：**场景 / 代码**那条线。美术那条线另有一份任务书，**两边不要互相等**：
> 美术只改画布尺寸，你这边用色块就能先把伪 3D 跑起来，图到了自动接管。

---

## 0. 你在哪、先读什么

- 项目根：`D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift`
- **必须先读**（顺序）：
  1. `docs/house-spec.md` **§4.8 室外伪 3D** —— 这次要实现的全部规格，已经定稿
  2. `docs/house-spec.md` §4.5.1（三层结构）、§0.1（内外严格 1:1，不能破）
  3. `docs/PROMPT-pseudo3d.md` —— 需求原文
  4. `scripts/world_view.gd` 全文（237 行，这次**只改这一个文件**）

## 1. 现状（三句话）

- `scripts/world_view.gd` 是**唯一一个 `_draw()` 平铺所有东西**：地面 → `frame.shapes` 逐个 match 类型画 → 暗角。
- 时间轴模式下**整个场景重复画三遍**（红偏左 1px、青偏右 1px、本体），做成色差。**这个三倍重绘必须保留**，它是本作时间轴的核心观感。
- 房子现在是四层纯色块（lot 底色 / 房间色 / 墙体逐格 / 家具块），**没有高度、没有屋顶、没有立面**。树（`circle` 类型）现在就是一个圆，没有树干。

## 2. 这次只做「立体感」，不做排序

**范围严格限定**，做完就能看出伪 3D：

| 做 | 不做（留给第 2 步） |
|---|---|
| ✅ `EXTRUDE` 常量 + 墙南立面 + 墙顶面 | ❌ 不拆 `_build_draw_list()`/`_render()` |
| ✅ 按 `wings` 画屋顶（翼组合、南翼压北翼） | ❌ 不加 `sort_y`、不加五层桶 |
| ✅ 树加树干（`circle` 分支） | ❌ 不碰 `scripts/player.gd`、不删 `z_index` |
| ✅ 修 `_house_tex()` 的路径（见 §5） | ❌ 不做屋顶隐藏（`in_building` 判定） |
| | ❌ 不做遮挡 α 0.4 |
| | ❌ **不碰碰撞**（`frame_data.gd` / `timeline.gd` / `houses_data.json` 一个字都不改） |

## 3. 常量

```gdscript
const EXTRUDE := 16.0   # 伪 3D 抬升高度 = 一整格（house-spec §4.8.1 已定）
```

**写死在代码里**，不要写进 `frames.json`，不要写进 `houses_data.json`。

理由（别自作聪明改）：1926→2026 是同几栋实体房子，高度**不随时间变**。一旦给了逐帧字段，
迟早有人微调成「推时间时房子在呼吸」，且违反 §7「base/roof 尺寸或锚点不同 → 进屋切屋顶时画面跳动」。

## 4. 要写的绘制（几何已验算，照做）

### 4.1 墙体：逐格「先立面、后顶面」

墙格 `Rect2(px, py, 16, 16)`（`HouseShape.solid_rects()` 已经给出）：

```gdscript
# 南立面：整个墙格本身向下延伸
draw_rect(Rect2(Vector2(px, py + 16 - EXTRUDE) + offset, Vector2(16, EXTRUDE)), WALL_COLOR)
# 墙顶面：抬高 EXTRUDE
draw_rect(Rect2(Vector2(px, py - EXTRUDE) + offset, Vector2(16, 16)), WALL_TOP)
```

`EXTRUDE = 16` 时南立面正好等于整个墙格（`py + 16 - 16 = py`），**这是有意的，不要写成特例**。

**顺序不能反**：南北相邻的两个墙格，南格的顶面正好盖住北格的立面。反了就会看见墙格之间的缝。
效果是所有格子一次性画完，整段连续墙**只露最南一格立面**，中间无缝。

⚠️ 性能：四栋房子的墙格约 480 个，× 时间轴三倍重绘 ≈ 1440 次 `draw_rect`/帧。
**必须把同一行 `y` 上连续的墙格合并成一个矩形**（`solid_rects` 已按行输出，约 8 行代码）。
这是 `gl_compatibility` + Web 导出的硬要求，别留到最后优化。

### 4.2 屋顶：按 `wings` 每翼一块

`HouseShape.house(sid)["wings"]` 是 `[[x, y, w, h], ...]`（**格坐标，不是像素**）。
`lot` 原点是 `hpos`，所以翼的世界坐标是 `hpos + Vector2(x, y) * 16`。

每翼一块矩形，绘制位置整体抬高 `EXTRUDE`：

```gdscript
for w in wings:
    var r := Rect2(hpos + Vector2(w[0], w[1]) * 16 + Vector2(-1, -1 - EXTRUDE) + offset,
                   Vector2(w[2] * 16 + 2, w[3] * 16 + 2))     # 外扩 1px 出檐
    draw_rect(r, ROOF_COLOR, true)
    # 屋脊 1px 线（沿长轴）+ 檐边 1px
```

- **翼必须按 `y` 从小到大画**（南翼压北翼檐，§0.2 已定）
- **禁渐变、禁粗黑边**（§7 明确列为坑）
- 屋脊颜色比屋面**亮一档**，檐边比屋面**暗一档**（`Color.darkened(0.25)` 级别就够）
- 颜色自选，别用 `WALL_COLOR`/`WALL_TOP` 直接顶（屋顶要能一眼区分是屋顶）

### 4.3 树：加树干

现在 `circle` 分支只有 `draw_circle`。凡是有 `label` 的树（`老槐`，`radius` 逐帧 16/32/48）
或按 `circle` 尺寸判断（`radius >= 12` 当树），在圆下面加树干：

```gdscript
var r := float(sd.get("radius", 4))
if r >= 12.0:
    draw_rect(Rect2(center + offset + Vector2(-2, r * 0.35), Vector2(4, r * 0.7)), TRUNK_COLOR)
    # 树冠上抬 r*0.7
```

**别给老井加树干**（它也是 `circle`，`label` 是 `老井·XX`）。用 `label` 判断最稳。

## 5. 顺手修一个现存 bug：`_house_tex()` 的路径是错的

```gdscript
# scripts/world_view.gd:143  现在的代码
var path := "res://assets/village/%s.png" % sid      # → assets/village/shen_a1.png
```

美术实际交付路径是 **`assets/village/houses/<族>/<帧>_base.png`**（`house-spec` §5 / §4.8.5），
两边**从来没对上过**，所以这段一直是死代码（`assets/` 目录本身也不存在）。

这次要改成读 **两张**，分别是 `_base` 和 `_roof`：

```gdscript
# assets/village/houses/<族>/<帧>_base.png
# assets/village/houses/<族>/<帧>_roof.png
```

族/帧映射见 `_ref/houses/gen_asset_breakdown.py:83-88`（`FAMILY` 表），例如
`shen_a1 → shen/a1_base.png`、`zhou_house → zhou/a1_base.png`。

**⚠️ 关键**：现在的代码是「有图就 `draw_texture_rect` 然后 `return`」，**跳过全部四层色块**。
加了屋顶之后这个 `return` 必须挪位——否则有图的房子**只有一张平铺图、没有屋顶**。
正确结构：`base` 图铺 lot → 墙/家具色块仅在缺图时画 → 屋顶**无论如何都画**（除非第 2 步的隐藏规则）。

**图现在还不存在**（美术在出），所以这段必须保留「拿不到图 → 走色块」的降级路径，
且**不能每帧 `load` 刷 ERROR**（现有 `_tex_cache` + `ResourceLoader.exists()` 的写法保留）。

## 6. 不改的东西（会被 `greybox_check` 抓到）

- `scripts/frame_data.gd`、`scripts/timeline.gd`、`scripts/house_shape.gd`、`scripts/player.gd`、`scripts/main.gd`
- `_ref/houses/houses_data.json`（**只读**）
- `data/frames.json`
- 时间轴三倍重绘结构（`_draw()` 里那三次 `_draw_shapes` 调用）

## 7. 验收

### 7.1 必须全绿（硬门禁）

```powershell
& 'D:\Steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe' --headless `
  --path "D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift" `
  --script "res://_mdtest/greybox_check.gd"
```

期望：`UNEXPLAINED_BLOCKS=0`，其余断言（`WORLD_OK`、四栋 lot 尺寸、`HOUSE_WALLS>0`、
`DOOR_PASSABLE`、`HOTSPOTS>=10`、`WALL_STOP_Y`、A1→A5 可达）全部通过。

> 它只测**碰撞 / 尺寸 / 可达性**，伪 3D 理论上不影响判定 → **它绿了不代表伪 3D 对了，但它红了说明你碰坏东西了**。

### 7.2 必须肉眼确认（数据断言测不出伪 3D）

`greybox_check` 测不出「屋顶画没画对」。用 `_mdtest/diary_test.gd` 那套
`await RenderingServer.frame_post_draw` + `get_viewport().get_texture().get_image().save_png()`
写一个临时截图脚本（**带窗口跑，不能 `--headless`**），把 A1 跑起来截一张图，然后逐条自查：

1. 四栋房子都有屋顶，屋顶盖在墙的上方、不是和墙顶齐平
2. 连续墙的立面**只有最南一格露出来**，墙格之间**没有缝**
3. 屋顶翼与翼的接缝处，**南翼压住北翼的檐**（沈家 A3 三块翼是唯一的检验点）
4. 老槐有树干，老井**没有**树干
5. 时间轴模式下（按 Shift）三倍重绘仍正常，**不闪、不糊**
6. 时间轴模式下伪 3D 的立体感**没有丢**（色差三遍都带高度）

截图存 `_mdtest/` 下，别提交进仓库。

## 8. 交付回报

1. 改了 `scripts/world_view.gd` 的哪几段（给行号）
2. `greybox_check` 的完整输出尾部（断言汇总）
3. 截图路径 + 上面 6 条自查的实际结果
4. **有没有发现规格里没写的坑**（有就写出来，别自己消化掉——第 2 步要用）
5. 一句结论：这一步能不能交给下一步（排序 + 玩家参与）

## 9. 下一步预告（这次别做）

第 2 步才是「玩家绕到房子后面被挡住」：拆 `_build_draw_list()`/`_render()`、五层桶、
`sort_y`、玩家搬进条目、屋顶隐藏（玩家在 `wings` 内就不画）、遮挡 α 0.4。
**所以这次写代码时，尽量让结构能撑住第 2 步**（比如墙/屋顶那些绘制别散在 `_draw_shapes` 的 match 里太碎），
但**不要提前实现**第 2 步。
