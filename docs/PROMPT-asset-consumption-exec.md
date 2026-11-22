# 新会话提示词：美术资产消费点接入线（让贴图真的画出来）

> 整段复制给新会话作为第一条消息。本线只改 GDScript 与配套自测，**不改资产文件、不改数据、不改 manifest**。

你是《shift》Godot 4.7 像素游戏的**渲染接入人**。用户明确：「这点需要单开一条线」。

## 0. 开工前（必做）

```
项目：D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift
Godot：D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe
```

- 所有 pwsh 调用带 `sandbox_permissions: "danger-full-access"`。
- `git log --oneline -3` 确认 HEAD ≥ `6674bea`。
- `git status --short`：工作区有其他线的未提交改动——`scripts/house_shape.gd` / `scripts/player.gd`（视觉机制线正在写）、`_ref/houses/_redo_school.py`（场景设计4）、`data/frames.json`（场景搭建2，若已在写）、`_ref/art/A4_2001/*.png`、`美术资产/`（删除/新增未提交）、`assets/village/`（美术线）。
  - **本线与视觉机制线同写 `scripts/*.gd`，是最严重的撞车风险**。开工第一件事：问本人「视觉机制线（PROMPT-stardew-engine-exec.md）是否已结束并提交？」——**未结束就不动 `world_view.gd` / `player.gd` / `house_shape.gd`**，先只做 §3 中互不冲突的部分（`scripts/` 下**新建文件** + 新自测文件），或在本人明确排期后等待。
- 先读 `docs/DECIDE-stardew-visual.md`（D6 冻结规格、D4 方案 B）、`docs/art-assets-a1a3.md`、`docs/HANDOFF-ART-A1A3.md`、`_ref/art/_assets_a1a3/_a1a3_assets.json`。

## 1. 这条线要解决什么（用户 1.C 的原话背景）

现在游戏里**只有屋顶贴图会画**（`scripts/world_view.gd:366` 的 `draw_texture_rect(tex_roof, ...)`）。美术同学和 AI 程序化出的其它图，游戏根本不读：

| 图 | 现状 | 消费点位置 |
|---|---|---|
| `assets/village/houses/<族>/*_base.png`（23 张） | `:239` 只判断 `tex_base == null` 决定墙画满格还是半格，**图本身从不贴** | `world_view.gd:217-239` |
| `assets/village/props/*.png`（84 张） | `scripts/` 全目录零引用；家具现在是纯色矩形 + 名字（`world_view.gd:248-256`） | `world_view.gd:248-256` |
| `assets/village/scene/*.png`（20 张：河/路/田/井/树/地面） | 零引用；现在靠 `frames.json` 的 polygon/rect 画色块 | `world_view.gd` 的 `_draw_shapes()` 附近 |
| `Sprite-主角-Sheet.png`（同学图，36 帧） | 主角纯代码画圆（`player.gd:40 draw_self()`） | `player.gd:40-73` |

**目标**：把这些图接进绘制流程，让画面真的出现美术资产；缺口图走现有降级（色块），分批交付不崩。

## 2. 硬约束（不可违反）

1. 内外 1:1：屋里屋外坐标一致，**碰撞仍是纯 AABB**（`HouseShape.solid_rects()` 一字不动）。
2. `EXTRUDE := 32.0` 写死；不做整栋 α 0.4、不做屋顶渐变（DECIDE 已裁决）。
3. 不改 `houses_data.json` / `data/frames.json` / manifest / 任何 PNG。
4. 不推翻已验收的「玩家在 wings 内不画屋顶」（`world_view.gd:258-260`）。
5. 美术资产**只是外观**：家具的占地/线索/碰撞仍读 `houses_data.json`，贴图不决定尺寸。
6. 缺图必须优雅降级：`_house_tex()`（`world_view.gd:188-200`）的 `ResourceLoader.exists()` 回 `null` 逻辑保留。

## 3. 实施顺序（建议）

### 3.1 先建独立新文件（无撞车风险，先做）

新建 `scripts/asset_draw.gd`（纯逻辑/静态函数，可单测，不依赖其他线）：

- `static func load_asset(path: String) -> Texture2D`：封装 `ResourceLoader.exists()` + `load()`，缺图返回 `null`，不报错。
- `static func anchor_bottom_center(tex: Texture2D, rect: Rect2) -> Vector2`：按 D6「底部中心锚点」算贴图左上角位置；支持贴图比占地高 32px（顶部立面）。
- `static func tile_variant(path_template: String, kind: String) -> String`：瓦片集变体路径拼装（给 scene 用）。

### 3.2 等视觉线结束后接 base / props

- **base**：`world_view.gd:221-249`，在第 1 层之后、第 3 层墙之前插入 base 贴图绘制（若有图，用底部中心锚点画；墙仍按 base 存在与否画半格/满格）。注意别让贴图盖住墙体立体部分。
- **props**：`world_view.gd:248-256`，把每个家具的色块替换成 `assets/village/props/<id>.png`（从 `f["id"]` 取），缺图保留色块；名字标签可保留但缩小。
- **主角**：`player.gd:40-73`，`draw_self()` 里若有 `Sprite-主角-Sheet.png` 的导入图则画对应帧，否则保留代码画圆。**注意这要等导入线把图放进 `assets/village/`**。

### 3.3 scene 接入（最后做，最复杂）

- `frames.json` 的 river polygon / dam rect / field rect / well circle / tree circle 对应 `assets/village/scene/*.png`。
- 河/路/田这类大面积图可能需瓦片平铺（`draw_texture_rect` + 32px 网格循环）；先做井/碑/树等小件，验证锚点正确后再铺大件。
- 注意 `frames.json` 的 `a4_2001` 正被场景搭建2 写，**本线只读**。

### 3.4 自测

- 新自测文件 `_mdtest/asset_draw_check.gd`（独立，不碰现有四套回归的断言）。
- 断言：缺图返回 `null` 不报错；锚点计算对 1×1/1×2/3×3 家具正确；base/props 接入后 `greybox_check.gd` 的 `WORLD_OK` / `WALL_BLOCKED` / `REACH_OK` / `UNEXPLAINED_BLOCKS=0` 仍全绿（碰撞没被贴图影响）。
- 四套回归看关键字，不看退出码（沙箱 `Failed to read the root certificate store.` + `[exit code:1]` 是基线固有）。

## 4. 交付与边界

- 只改：`scripts/asset_draw.gd`（新建）、`scripts/world_view.gd`、`scripts/player.gd`、`_mdtest/asset_draw_check.gd`（新建）。
- 不动：`scripts/house_shape.gd`（视觉线在读，若需要它加接口，**发消息给本人协调，别自己改**）、`house_shape.gd` 以外的其他线文件、任何资产/数据/文档。
- 不 commit（由总策划统一提交）；结束时报告改了哪些文件、四套回归关键字结果、还有什么没接。
- `present` 一张游戏截图（若能在沙箱跑 Godot）或列明如何本地验证。

## 5. 输出要求

结束时回答：① 哪些图真的能看到了（按 base/props/scene/主角分类）；② 哪些还看不到及原因；③ 四套回归结果；④ 与视觉机制线的边界是否守住（确认没改 `house_shape.gd`）。
