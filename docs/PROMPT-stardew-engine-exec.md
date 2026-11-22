# 新会话提示词：星露谷视觉机制执行线（引擎）

> 整段复制给新会话作为第一条消息。本线只做代码，不写美术资产、不改数据、不回写文档。

你是《shift》Godot 4.7 像素游戏的**视觉机制执行人**。

用户原话（2026-11-22）：「A1–A3 是可以参与改造的」——本线所有改动与验收**只在 A1–A3 的 12 栋上做**，A4/A5 冻结。

## 0. 开工前（必做）

```
项目：D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift
Godot：D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe
```

- 所有 pwsh 调用带 `sandbox_permissions: "danger-full-access"`。
- `git log --oneline -3` 确认 HEAD ≥ `eb6c7fa`（星露谷裁决 `docs/DECIDE-stardew-visual.md` 已提交）。
- `git status --short`：**工作区有另一条 A4 精调线的未提交改动**（`_ref/houses/houses_data.json`、`_ref/houses/_redo_*.py`、`_ref/art/A4_2001/*.png`、`docs/HANDOFF-VILLAGE.md`、`docs/PROMPT-house-size.md`、`docs/PROMPT-a4-houses-exec.md`）。这些文件**只读、绝不写入、绝不 `git add`**。
- 先读 `docs/DECIDE-stardew-visual.md` 全文（110 行），那是本线的需求来源；D2/D5 已裁决「不做 α 0.4 / 不做屋顶渐变」，**不许复活**。

## 1. 你的独占写入文件（只有这 4 个 .gd）

| 文件 | 任务 |
|---|---|
| `scripts/world_view.gd` | ① 实现 y-sort：收集 houses / trees / furniture / player → 按 `sort_y`（精灵底边，不是中心）排序 → 顺序 `draw_*`。② `_draw_walls_lifted()`（`:281-321`）按朝向画墙：**北/西全高 = TILE 32px，东/南半高 = TILE/2 = 16px**。③ 保留 `_house_tex()`（`:188-200`）缺图回色块的降级路径，永久不删。④ 保留进屋不画屋顶 `_player_inside()`（`:259-274`），已真机验收，不许改。 |
| `scripts/house_shape.gd` | 新增**渲染专用**墙向分类器：基于 `grid_of()`（`:109-171`）相邻格判断每格墙的朝向（北/西/东/南），供 world_view 用。⚠️ **`solid_rects()`（`:176-190`）返回结构不许改**，碰撞恒为整格 AABB。分类器要容忍任意 `wings` 形状与 `demolished` 拆墙表，别假设矩形。 |
| `scripts/player.gd` | 把 `_draw()`（`:26-52`）的绘制逻辑抽成 `func draw_self(offset := Vector2.ZERO)` 供 world_view 排序循环调用；**删除 `:23` 的 `z_index = 10`**；保留 `walking` / `facing` / `bump_kick` / 残影等状态。 |
| `scripts/main.gd` | 扩展已有的玩家状态通路（`:111`/`:224` 的 `world.set_player_pos`），把排序需要的玩家状态（pos / facing / walking / walk_phase / bump_kick / time_mode）喂给 world_view。`player.position = tl.char_pos`（`:54`/`:107`）保持。 |

### 实现要点（DECIDE D4 方案 B）

- 选 B：**保留单 `_draw()`，收集 → 排序 → 绘制**。理由：切帧天然干净（`show_frame()` 换帧整帧重绘，无节点增删、无残影）。
- 排序键：`sort_y` = 精灵底边（脚那条线）。玩家 = `position.y + RADIUS * 0.7`（`player.gd:12 RADIUS=14`）；树 = 中心 y + radius×0.7；家具 = 占地 `rect` 底边；房子 = lot 底边。
- `docs/PROMPT-pseudo3d.md:76` 那句「单 `_draw()` 做不到」已判作废——`world_view.gd:335-336` 已有 `_draw()` 内 `sort_custom` 的反证。
- 场景树 `scenes/main.tscn:22-30`：WorldView(Control) 与 Player(Node2D) 是 CameraRig 下兄弟节点，**不要靠节点 z_index 做遮挡**（插不进 `_draw()` 内部顺序）。Player 节点可以留着只存状态，绘制交给 world_view。

### 硬约束（不许拿来交换）

1. 内外严格 1:1；碰撞纯数据 AABB（`scripts/frame_data.gd:is_free()` 不引物理引擎）。
2. **不写** `_ref/houses/houses_data.json`、**不写** `data/frames.json`。
3. 高度不进逐帧数据；`EXTRUDE := 32.0`（`world_view.gd:21`）保持写死。
4. 不做 α 0.4、不做屋顶渐变（D2/D5 已裁决）。

## 2. 验收（全部只用 A1–A3）

A1–A3 的 12 栋：`lu_house/shen_a1/mill_a1/zhou_house`（A1）、`lu_a2/shen_a2/mill_a2/zhou_a2`（A2）、`lu_a3/shen_a3/mill_a3/zhou_a3`（A3）——与 `world_view.gd:178-183` 的 `FAMILY` 表一致。

跑 Godot 用 `--headless --path . -s res://_mdtest/<脚本>.gd`。**沙箱噪声 `Failed to read the root certificate store.` / `[exit code: 1]` 是基线固有，判 green 看关键字不看退出码**：`WORLD_OK` / `START_OK` / `WALL_BLOCKED` / `REACH_OK` / `UNEXPLAINED_BLOCKS=0` / `HOTSPOTS_OK`。

四套必跑：`_mdtest/{greybox,camera,display,hud_layout}_check.gd`。

画面/逻辑检查项（DECIDE §5，逐条自查并在报告里打勾）：

- [ ] 玩家站房北 → 被房子/屋顶遮住（y-sort 生效，`z_index=10` 已删）
- [ ] 玩家站房南 → 玩家挡住房子南立面
- [ ] 玩家绕到家具后 → 被家具挡住；绕到前 → 挡住家具
- [ ] 玩家在房外南侧 → 东/南墙只画半高 16px，室内家具可见；北/西墙全高 32px
- [ ] 玩家进屋（wings 内）→ 屋顶整块消失，无渐变
- [ ] 时间轴推一年 → 整帧干净切换，无残影、无重复节点、无「房子呼吸」
- [ ] 缺美术图时 `_house_tex()` 静默回色块，游戏可跑
- [ ] 内外 1:1 与 AABB 碰撞未变，四套回归关键字全绿

## 3. 收工

- 只 `git add` 上述 4 个 .gd 和你新增的测试文件（如需新增 `_mdtest/*_sort_check.gd` 可加）。**不要 add 任何其他文件**。
- commit 信息写 `feat: 星露谷视觉机制 - y-sort 遮挡 + 南墙半高（DECIDE D3/D4）`。
- 报告里写清：改了哪些行、四套回归关键字结果、8 条检查项的通过情况、有没有遗留问题。

## 4. 边界提醒

- 美术资产（另一条线）正在按 +32/base+roof 规格画 A1–A3 贴图，走的就是你保留的 `_house_tex()` 路径——**不要改这个接口**。
- 文档回写（第三条线）负责 `house-spec.md` 等；**本线不写文档**。
- 场景设计线（已在跑）改 A4/A5 房屋与 `houses_data.json`；**本线只读那部分**。
