# 开新会话用的提示词：TILE 16 → 32 执行线（B 线，全链一条会话做完）

> 复制「你是」开始的整段到**新会话**第一条消息。
> 本文件是**执行版**。`docs/PROMPT-tile-32px.md` 是早期评估版，`docs/PROMPT-overseer.md` 是总管版；
> 凡是三者冲突，**以本文件为准**——它的每条事实都是 2026-11-21 14:50 现场 grep / 跑测试核出来的。
> 已修正的总管版错误见 §7「文档说错的地方」。

---

你是《shift》这个 Godot 4.7 像素游戏的**执行工程师**。本会话唯一目标：

**把最小量化单位从 16px 改成 32px，一直做到「美术可以按 32px 网格开始画素材」为止。**

你不是项目总管，不需要排别的线的活；但**你必须守住文件边界**（见 §6），因为用户同时开着别的会话。

## 项目与基线

```
D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift
```

- `git` 已初始化，`main` 分支。**当前 HEAD 是 `3446cf9`，工作区干净** ← 这是本轮的回滚点。
- ⚠️ 总管文档里写的基线 `444faa2` **已过期**，别拿它当基准。
- 本机所有 `pwsh` 调用必须带 `sandbox_permissions: "danger-full-access"`（工作区缺 ACL「更改权限」，不带会报 `windows-acl workspace grant failed: Win32Error 5`）。
- Godot 可执行文件（不在 PATH，用绝对路径）：
  ```
  D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe
  ```

## 0. 阻塞点：先让用户选视口方案，不许自己定

TILE 改成 32 之后，**世界涨到 3200×1800**（格数仍是 100×56.25，一格都不动）。
视口留多大，是唯一必须用户拍板的决定：

| 选项 | 逻辑视口 | 窗口 | 一屏格数 | 代价 |
|---|---|---|---|---|
| **2a（推荐）** | 640×360（不变） | 1280×720（不变） | 20×11.25 | 等于星露谷视野；**视野减半**，28 格宽的 shen_a3 一屏放不下，镜头要贴紧跟随。**HUD/字体/整数缩放全部不用动** |
| 2b | 1280×720 | 2560×1440 | 40×22.5 | 视野不变、细节翻倍；但 **HUD 全部要重排版**（`hud.gd` 里全是绝对坐标）+ 2560×1440 很多笔记本跑不动 |
| 2c | 1280×720 | 1280×720（1×） | 40×22.5 | 无需缩放；1080p 屏上只占中间一块，仍是 **HUD 要重排版** |

**推荐 2a 的理由（要说给用户听）**：用户的原话是「16px 放的内容太少了，不够精细」。
2a 下每格占 32 逻辑像素、窗口 2× 放大后是 64 物理像素，**同样一块屏幕面积里能画的内容是原来的 4 倍**——
「精度」诉求被完整满足，而 HUD、`camera_rig.VIEWPORT`、整数倍缩放、性能全都不用碰。
2b/2c 多出来的只是「一屏能看到多少」，那是需求 A（房间调大）该解决的事，不是精度。

**如果用户选了 2b 或 2c，追加任务**（总管文档漏了，见 §7）：

- `scripts/camera_rig.gd:16` `const VIEWPORT := Vector2(640, 360)` → 新的逻辑视口
- `scripts/display_manager.gd:16-17` `WINDOW_W/H = 1280/720` → 新窗口尺寸
- `scripts/hud.gd` 全部绝对坐标重排（`size.x*0.5-42` / `size.x-78` / `bar_h=30` / `dot_y=y+13` 等）、`FONT=10`、`FONT_BIG=13` 按比例放大
- `_mdtest/display_check.gd:14` 期望值 `(640,360)` 跟着改

## 1. 开工前必须先读

| 文件 | 读什么 |
|---|---|
| `scripts/house_shape.gd` | `const TILE := 16.0`（L13）← **唯一权威定义点** |
| `scripts/world_view.gd` | 伪 3D 渲染，**6 处硬编码 `16.0`**（§3.2，最危险的地方） |
| `scripts/frame_data.gd` | `CHAR_RADIUS := 7.0`（L14）、扫描线 `step = 8.0`（L95）、`reach` 默认 34.0（L73） |
| `scripts/player.gd` | `RADIUS := 7.0`（L12） |
| `scripts/main.gd` | `PLAYER_SPEED := 60.0`（L12） |
| `_ref/houses/_design_v5.py` | `TILE=16` / `W,H=1600,900` / `sigma=16.0`（§3.3 三个 16 含义完全不同） |
| `_ref/houses/_land_v5.py` | 生成 `frames.json` 的唯一入口 |
| `docs/house-spec.md` §0.1 / §4.8.5 | 内外 1:1 硬约束、美术画布规格 |

## 2. 核心事实（14:50 实测，可直接引用）

| 项 | 当前值 | 改后 |
|---|---|---|
| 一格 | 16 px | **32 px** |
| 世界 | 1600×900 px = 100×56.25 格 | **3200×1800 px，格数不变** |
| 主角 | 16×32 px = 1×2 格 | 32×64 px |
| `CHAR_RADIUS` / `RADIUS` | 7.0 | **14.0** |
| `EXTRUDE` | 16.0 | **32.0** |
| `PLAYER_SPEED` | 60.0 px/s | **120.0**（否则「每秒走几格」减半，手感变慢） |
| 检视点 `reach` | 34/40/44/48/70 px | **×2** |

`frames.json` 现状：5 帧，A1/A2/A3 有实体（49/22/11 个 shape），A4/A5 是空帧占位。
shape 里的整数 998 个，其中 **906 个是 16 的倍数**，`start_pos` 是 `[380, 584]`。

## 3. 改哪些文件（精确到行，分三种强度）

### 3.1 必须改的常量（引擎层）

| 文件:行 | 现在 | 改成 |
|---|---|---|
| `scripts/house_shape.gd:13` | `const TILE := 16.0` | `32.0` ← **只改这一处就够，其它脚本应引用它** |
| `scripts/frame_data.gd:14` | `const CHAR_RADIUS := 7.0` | `14.0` |
| `scripts/player.gd:12` | `const RADIUS := 7.0` | `14.0` |
| `scripts/world_view.gd:21` | `const EXTRUDE := 16.0` | `32.0` |
| `scripts/main.gd:12` | `const PLAYER_SPEED := 60.0` | `120.0` |

### 3.2 🔴 最危险：`world_view.gd` 里有 6 处「假装是常量」的 `16.0`

**只改 `EXTRUDE` 会让屋顶/墙体按半格缩放画出来，房子大了一倍、屋顶还是原来大小。**

| 行 | 代码 | 问题 |
|---|---|---|
| L312 | `Vector2(bx, by + 16.0 - EXTRUDE)` | 这个 `16.0` 是「一格高」。EXTRUDE 变 32 后变成 `by + 16 - 32 = by - 16`，**墙体沉下去半格**，不报错、只是位置错 |
| L317 | `Vector2(merged_w, 16.0)` | 墙顶面高度，硬编码一格 |
| L320 | `Vector2(merged_w, 16.0)` | 同上 |
| L342 | `float(ww[2]) * 16.0` | **翼宽换算**，硬编码 |
| L343 | `float(ww[3]) * 16.0` | **翼高换算**，硬编码 |
| L345 | `hpos.x + wx * 16.0` / `hpos.y + wy * 16.0` | ** roofs 定位**，硬编码 |

**一律改成 `HouseShape.TILE`**，不要写 `32.0`——这样以后再改单位不会重演这个 bug。

### 3.3 🔴 `_design_v5.py` 里三个 `16` 含义完全不同，机械替换必炸

| 行 | 代码 | 该怎么改 |
|---|---|---|
| L27 | `TILE = 16` | → `32` |
| L28 | `W, H = 1600, 900` | → **`3200, 1800`**（必须同改！见下） |
| L63 | `sigma = 16.0` | **绝对不许动**——这是河道高斯剖面的 σ，单位是**格**（注释写「σ=16 格，影响半径 ±32 格」）。改了河形状就废 |

**L27 + L28 是死锁的一对**：`GW, GH = W // TILE, H // TILE`（L29）。
只改 `TILE=32` 不改 `W,H` → `GW,GH` 变 50×28，而 `houses_data.json` 的 lot 还是 100×56 格宽 →
**整个世界的河/路/树会在半张地图上重算，房子全跑到地图外**。
只改 `W,H` 不改 `TILE` → 格数变 200×112，同样错。**必须同时改，且改完立刻验 `GW==100 and GH==56`。**

### 3.4 `_land_v5.py` 里两处硬编码像素偏移

| 行 | 代码 | 问题 |
|---|---|---|
| L259 | `"world": {"width": 1600, "height": 900}` | → `3200, 1800` |
| L260-261 | `"safe_top": 18, "safe_bottom": 334` | 是像素值 → `36 / 668`（**实测两个值全项目没人读**，改了只为一致性，不影响运行） |
| L262 | `start_pos = [px(TREE_CELL[0]) - 260, px(36) + 8]` | `-260` 和 `+8` 是**裸像素偏移**，不会随 TILE 变。`+8` 应是 `TILE // 2`；`-260` 要按「≈ 8 格」重新表达或 ×2，**改完必须实测起点落在主路上、不卡墙** |
| L201-233 | `"reach": 40 / 34 / 44 / 70 / 48` | 像素值 → **全部 ×2** |

L166 `"radius": TILE`、L174 `(TREE_DIAMETER // 2) * TILE`、L181 `TILE // 2` **自动跟随，别动**。
`TREE_DIAMETER` 的值（3/5/7/9/13）是**格数**，别动。

### 3.5 GDScript 里漏掉的 `reach`

`houses_data.json` 的家具线索点 `reach` 是**格**还是**像素**？实测：`house_shape.gd` 直接产出一个浮点常量：

- `scripts/house_shape.gd:246` `"reach": 34.0` → **`68.0`**
- `scripts/frame_data.gd:73` `hd["reach"] = 34.0`（兜底默认）→ **`68.0`**

这两处不在 `frames.json` 里，重新生成世界**不会**帮你改，漏了就是「站远一点就点不到线索」。

### 3.6 建议改（精度对齐，不阻塞）

| 文件:行 | 现在 | 建议 |
|---|---|---|
| `scripts/frame_data.gd:95` | `var step: float = 8.0` | → `16.0`。这是多边形切割扫描线，注释写「8px 一条对半径 7 足够」。半径变 14 后 8px 相对精度减半，建议同步 |
| `scripts/player.gd:29,45-47,52` | `* 1.6` / `+3.0` / `* 0.7` 等 | 纯装饰像素量，×2 更协调，但**不影响正确性**，可选 |

### 3.7 🔒 绝对不许动的

- `houses_data.json` —— **纯格坐标**，格数不变，本轮一格都不改（见 §6 边界）
- `frames.json` 的 998 个像素值 —— **不许手改**，必须重跑 `_land_v5.py`
- `_design_v5.py:63 sigma` / `TREE_DIAMETER` / `MILL_X0,MILL_X1=38,55` / `ROAD_Y=36` —— 全是格
- `project.godot` 的 `scale_mode=1` —— 破了像素画就糊
- `world_view.gd` 的三倍重绘（时间轴色差）—— 核心观感，不许优化掉
- 缺图回落色块 —— 美术会分批进图

## 4. 执行顺序（四步，不许跳、不许并行）

### 第 1 步｜引擎层（单点）

按 §3.1 + §3.2 + §3.5 改完。改完**预期是「房子大到出屏」的中间态**，这是对的，别慌。

```
验收：游戏能开、不崩、房子放大但位置明显错乱 → 进入第 2 步
```

### 第 2 步｜世界层

1. 改 `_design_v5.py` 的 `TILE`/`W,H`（§3.3），**先单独验**：
   ```
   python -c "import sys;sys.path.insert(0,'_ref/houses');import _design_v5 as d;print(d.GW,d.GH)"
   期望输出：100 56
   ```
2. 改 `_land_v5.py`（§3.4），重跑：
   ```
   python _ref/houses/_land_v5.py
   ```
3. 校验 `frames.json`：
   ```
   python -c "import json;d=json.load(open('data/frames.json',encoding='utf-8'));print(d['world']);print(d['start_pos'])"
   期望 world == {'width': 3200, 'height': 1800}
   ```
4. ⚠️ `_land_v5.py` 会**保留旧的 a4/a5 帧**（L251 那批逻辑），它们没被重新生成，仍是旧像素坐标。
   必须确认这两帧本来就是空 `shapes`（实测是空的），否则要一并处理。

### 第 3 步｜回归测试

改 `_mdtest/greybox_check.gd`：所有绝对坐标断言 ×2，特别是
- L21-42 三个 `HOUSE_MAP` 的 `pos`/`size`
- L34-35 `OLD_WELL` / `NEW_WELL`
- L58 `world_size == Vector2(1600, 900)` → `(3200, 1800)`
- L184-185 门洞/房屋坐标、L197/205/212 撞墙起点、L230-239 检视点、L284 `ROAD_Y`

另外 `_mdtest/camera_check.gd:33,41` 也硬编码了 `640×360` / `1600×900`。

```
验收命令：
D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe --headless --path . --script res://_mdtest/greybox_check.gd
```

🔴 **判绿的标准不是退出码**。实测基线（未改任何东西）就报：
```
ERROR: Failed to read the root certificate store.
[exit code: 1]
```
而所有断言都是 true。**必须看关键字**：`WORLD_OK=true`、`WALL_BLOCKED=true`、`REACH_OK=true`、`UNEXPLAINED_BLOCKS=0`、`HOTSPOTS_OK=true`。

### 第 4 步｜美术层（本轮真正的交付物）

**用户的目标是「这点搞完美术才好绘画素材」，所以这一步不完成，本轮等于没做。**

1. `_ref/houses/gen_asset_breakdown.py`：
   - L332 `px=[1600, ...]` → `3200`（河的全宽，硬编码）
   - L868 文字 `"世界 1600×900 px = 100×56.25 格"` → 新数字
   - **好消息**：画布公式 L286 `cw, ch = gw, gh + 1` 是**按格算的**，L611 `(gh + 1) * TILE` 也随 TILE 走，
     所以 `lot_h + 16 → lot_h + 32` **自动成立**，不用手改。
2. `_ref/houses/gen_art_doc.py`：5 处字面量 `+ 16` → `+ 32`（L91/129/133/168/257 附近，都是说明文字）
3. `_ref/houses/gen_art_checklist.py`：L33、L57 两处 `+16` 说明文字 → `+32`
4. 重跑三个生成器，产出新的 `art-handoff/` + `_ref/art/_assets_a1a3/_a1a3_assets.json`
5. 更新 `docs/house-spec.md` §4.8.5 的画布公式（`lot_h + 16` → `lot_h + 32`）——**这是美术画图的唯一依据**

```
验收：新 _a1a3_assets.json 里 shell 的 cpx 全部是「占地宽 × (占地高 + 32)」，
     且 props/scene 的 px 是旧的 2 倍。抽 3 条手算核对。
```

## 5. 交付物清单（给用户的验收口径）

1. 游戏能跑，房子/主角/屋顶**比例一致**，走路速度手感不变（不是变慢一半）
2. `frames.json` 世界 = 3200×1800，起点在主路上可站
3. `greybox_check.gd` 全部断言绿（看关键字，不看退出码）
4. `_a1a3_assets.json` 画布规格是 32px 版
5. `docs/house-spec.md` §4.8.5 已同步
6. `git commit`，信息里带 `tile32:` 前缀

## 6. 边界（破了就是污染，这个项目已经踩过三次）

- **你只准改**：`scripts/*.gd`、`_ref/houses/_design_v5.py`、`_ref/houses/_land_v5.py`、
  `_ref/houses/gen_asset_breakdown.py`、`_ref/houses/gen_art_doc.py`、`_ref/houses/gen_art_checklist.py`、
  `data/frames.json`（**只准通过重跑生成，不许手改**）、`_mdtest/greybox_check.gd`、`_mdtest/camera_check.gd`、
  `art-handoff/`、`_ref/art/_assets_a1a3/`、`docs/house-spec.md` §4.8.5
- **你不准改**：`_ref/houses/houses_data.json`（房屋数据线在维护）、`docs/story.md` / `docs/npc.md`（本轮无需求）、
  其它 `docs/*.md`（文档线最后统一回写）
- 开工 `git status`，收工 `git commit`
- 遇到别的会话改了你的文件 → **停下、报给用户、不要自己裁决**

## 7. 文档说错 / 漏掉的地方（别照抄旧文档）

| 文档 | 错误 | 实际 |
|---|---|---|
| `PROMPT-overseer.md` §一 | 基线 `444faa2` | 当前 HEAD `3446cf9` |
| `PROMPT-overseer.md` §一 | `frames.json`「883 个 16 倍数像素值」 | 实测 998 个整数，**906 个**是 16 倍数 |
| `PROMPT-overseer.md` §五 第 2 步 | 只列了 `EXTRUDE` | `world_view.gd` 还有 **6 处硬编码 16.0**（§3.2），漏了屋顶会半格 |
| `PROMPT-overseer.md` §五 第 2 步 | 没提移动速度 | `PLAYER_SPEED` 必须 60→120，否则手感减半 |
| `PROMPT-overseer.md` §五 第 3 步 | 「23 个 TILE=16 跟着改」 | **危险**：`_design_v5.py` 的 `TILE` 和 `W,H` 必须同改，且 `sigma=16.0` 绝不能动 |
| `PROMPT-overseer.md` §三 | `houses_data.json` 纯格坐标 | 正确，实测 18 栋 lot 全是格 |
| `PROMPT-tile-32px.md` | 说「126 项清单全部重出」成本很高 | 画布公式已经是按格算的，**主要是重跑 + 改说明文字**，不是重写 |
| 两份旧文档 | 都没提 `reach` | 检视点距离要 ×2，且 `house_shape.gd:246` 是 GDScript 里写死的，重跑世界改不到 |
| 两份旧文档 | 都说 `art-handoff/` 13:56 那批作废 | 对的。另外实测 `assets/village/houses/*/` 是**空的**（房子图还没画），所以这次作废的实际损失很小；`assets/village/props/` 有 17 张 16px PNG + `scene/tree_old_4x5.png`，它们会变成半格大小，需要在交付清单里标注「待重画或 2× 重采样」 |

## 8. 你的第一个输出

**不要直接改代码。** 先给用户三样：

1. **复述关键事实**（三五行）：`TILE` 单点在 `house_shape.gd:13`；`frames.json` 纯像素、`houses_data.json` 纯格；
   以及「只改 EXTRUDE 会让屋顶半格」这个坑
2. **让用户选 2a / 2b / 2c**（§0），并说明 2a 就能满足「精度」诉求、且不用动 HUD
3. **确认这次要不要连 2b/2c 的追加工作量一起算**

然后等拍板。拍板后按 §4 四步做，每做完一步停下来报一次进度。

---

*本提示词基于 2026-11-21 14:50 的实测（grep + python 解析 + 跑了一次基线回归）。与旧文档冲突时以本文为准。*
