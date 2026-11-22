# 新会话提示词：美术资产消费点接入线（让贴图真的画出来）

> 整段复制给新会话作为第一条消息。本线只改 GDScript 与配套自测，**不改资产文件、不改数据、不改 manifest**。
> **架构已定案（用户 2026-11-22 拍板 A 方案）**：贴图绘制接进视觉机制线已交付的 `world_view.gd` 现有
> `_draw_front()` 排序循环 / `_draw_house_base()` 背景层，**不另起绘制入口、不新建绘制节点**。
> 视觉机制线已 commit `b6024dd`，撞车窗口已解除，可以放心改这些 .gd。

你是《shift》Godot 4.7 像素游戏的**渲染接入人**。用户明确：「这点需要单开一条线」。

## 0. 开工前（必做）

```
项目：D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift
Godot：D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe
```

- 所有 pwsh 调用带 `sandbox_permissions: "danger-full-access"`。
- `git log --oneline -3` 确认 HEAD ≥ `b664a05`；确认 `b6024dd`（视觉机制线）已在历史里。
- `git status --short` 核对：视觉线 4 个 .gd 已全部提交、工作区无 `M scripts/*.gd`。
  若仍有别的会话在写这些 .gd，**停下问本人**，不要同时写。
- 先读：`docs/DECIDE-stardew-visual.md`（D6 冻结规格、D4 方案 B）、`docs/HANDOFF-ART-A1A3.md`、
  `docs/FEEDBACK-planner-stardew-engine.md`（视觉线交付，含 §6 沙箱经验）、
  `_ref/art/_assets_a1a3/_a1a3_assets.json`。
- 🔴 视觉线的 `world_view.gd` 已把「墙/门/屋顶/家具/树/井/碑/玩家」全部收进排序链，
  **代码行号已整体位移**，本提示词给的是交付后行号，动手前再 read 一遍确认。

## 1. 这条线要解决什么（用户 1.C 的原话背景）

现在游戏里**只有屋顶贴图会画**（`_draw_roof()` 里 `draw_texture_rect`）。其余图游戏根本不读：

| 图 | 现状 | 消费点（视觉线交付后行号） |
|---|---|---|
| `assets/village/houses/<族>/*_base.png` | `_house_tex()` 只把 base 传进墙体判定「画满格/半格」，**图本身从不贴** | `world_view.gd:394-417 _draw_house_base()` |
| `assets/village/props/*.png` + `_classmate/props/*.png` | 零引用；家具是纯色矩形 + 名字 | `world_view.gd:420-428 _draw_furniture()` |
| `assets/village/scene/*.png`（河/路/田/井/树） | 零引用；靠 frames.json polygon/rect 画色块 | `world_view.gd:182-221 _draw_back()` / `:432-466 _draw_prop()` |
| `Sprite-主角-Sheet.png`（同学图 36 帧） | 主角纯代码画圆 | `player.gd:40 draw_self()` |

**目标**：把这些图接进现有绘制流程，让画面真的出现美术资产；缺图走降级色块，分批交付不崩。

## 2. 硬约束（不可违反）

1. 内外 1:1：屋里屋外坐标一致，**碰撞仍是纯 AABB**（`HouseShape.solid_rects()` / `wall_render_cells()` 一字不动）。
2. `EXTRUDE := 32.0` 写死；不做整栋 α 0.4、不做屋顶渐变（DECIDE 已裁决）。
3. 不改 `houses_data.json` / `data/frames.json` / manifest / 任何 PNG。
4. 不推翻已验收的「玩家在 wings 内不画屋顶」（`_player_inside()`，`world_view.gd:472`）。
5. 美术资产**只是外观**：家具占地/线索/碰撞仍读 `houses_data.json`，贴图不决定尺寸。
6. 缺图优雅降级：`_house_tex()`（`:378-390`）的 `ResourceLoader.exists()` 回 `null` 逻辑保留。
7. **A 方案专属**：不新建绘制节点、不设 z_index、不动 `_collect_front()` 的排序不变式
   （底边 sort_y + seq 稳定序）；贴图只替换"怎么画"，不改变"画哪些条目、什么顺序"。

## 3. 实施（A 方案：接进现有循环）

### 3.1 工具函数（可选，先做）

可新建 `scripts/asset_draw.gd`，**只放静态工具函数、不放 _draw 入口**：
`load_asset(path)`（exists + load，缺图回 null）、`anchor_bottom_center(tex, rect)`（D6 底部中心锚点）、
`tile_variant(path_template, kind)`（scene 瓦片变体）。纯逻辑可单测。
若判定不需要独立文件，直接把这些函数写进 `world_view.gd` 也行——**但绘制调用必须落在下面的现有分支里**。

### 3.2 base / props（主战场，接进现有 match 分支）

- **base**：在 `_draw_house_base()`（`:394-417`）画。注意 D6 规格里 base 是整块 lot 的**俯视图**，
  按 `lot_rect()` 矩形贴（左上角锚点），**不是底部中心**——底部中心锚点只给家具/立着物件用。
  有图时用贴图替代第 1/2 层色块，无图保留现有色块；别让 base 盖住第 3 层墙。
- **props**：在 `_draw_furniture()`（`:420-428`）把色块换成 `assets/village/props/<id>.png`，
  缺图保留色块；名字标签缩小或保留。
  - 🔴 **id 取法（用户 2026-11-22 拍板：近似匹配过渡）**：`houses_data.json` 家具条目**没有 `id` 键**，
    只有 `name`/`short`/`rect`/`clue`/`zone`，**不要写 `f["id"]`（会取空值）**。
    正确做法：用 `short`（或 `name`）去 manifest 的 `props[].short` 查 `id`，再拼路径。
  - 实测覆盖（`docs/FEEDBACK-planner-art-import.md` §阻塞②）：551 家具 / short 命中 253 / 未命中 298 /
    可达 manifest id **85 of 91**。未命中的是学校施工类词（跑道×56、课桌×30…），manifest 无对应 id，
    **匹配不到就回色块，是预期行为，不要报错、不要硬造 id**。
  - 同学图适配产物 `assets/village/_classmate/props/`（84 张）与 manifest 新增 P85–P91 一并可查。
- **主角**：在 `player.gd:40 draw_self()` 里若有同学主角图则画对应帧，否则保留代码画圆。
  ⚠️ 主角图由 `world_view` 按 sort_y 调 `draw_self()`，`player.gd` 的 `_draw()` 是空的——别改回自己画。

### 3.3 scene 接入（最后做，最复杂）

- river polygon / dam rect / field rect / well circle / tree circle 对应 `assets/village/scene/*.png`。
- 大面积图（河/路/田）用 32px 网格 `draw_texture_rect` 平铺；先做井/碑/树小件验证锚点再铺大件。
- `frames.json` 的 `a4_2001` / `a5_2026` 正被场景搭建2 写，**本线只读，绝不写 frames.json**。

### 3.4 自测

- 新建 `_mdtest/asset_draw_check.gd`（独立，不碰现有回归断言）：
  缺图回 null 不报错；锚点对 1×1/1×2/3×3 正确；贴图接入后五套回归关键字仍全绿
  （碰撞没被贴图影响）。
- 五套回归看关键字不看退出码：`sort_check` / `greybox_check` / `camera_check` / `display_check` /
  `hud_layout_check`（沙箱 `Failed to read the root certificate store.` + `[exit code:1]` 是基线固有）。

## 4. 沙箱经验（视觉线反馈 §6，踩过 5 次，照做省时间）

1. Godot `--headless` 是 dummy 渲染器**拿不到像素**；像素/截图验收必须去掉 `--headless`（真实 OpenGL 上下文）。
2. headless 下不能用管道捕获 stdout（EPERM）→ 用 `Start-Process -RedirectStandardOutput/-RedirectStandardError` 再读文件；
   若 `Start-Process` 被沙箱拒，改 `cmd /c "godot ... > out.txt 2> err.txt"`。
3. **改 GDScript 一律用 edit/write 工具，绝不用 pwsh 做文本替换**（中文往返会损坏 UTF-8 + 吃行尾 → Parse Error）。
4. 镜头 lerp 跟随，像素验收要钉死 `camera_rig.set("offset", want)` + `call("_apply")`。
5. 玩家脚下有影子，判"本体色"采样**圆心上方 6px**；中文 print 在 GBK 控制台乱码 → 只看 PASS/FAIL 关键字。

## 5. 交付与边界

- 只改：`scripts/world_view.gd`、`scripts/player.gd`、`scripts/asset_draw.gd`（可选新建）、
  `_mdtest/asset_draw_check.gd`（新建）。
- 不动：`scripts/house_shape.gd`（视觉线已定案，若需加接口，发消息给本人协调，别自己改）、
  其它线文件、任何资产/数据/文档。
- 不 commit（由总策划统一提交）；结束报告改了哪些文件、五套回归关键字、还有什么没接。
- `present` 一张游戏截图（能跑真实 Godot 时）或列明本地验证方法。

## 6. 输出要求

结束时回答：① 哪些图真的能看到了（按 base/props/scene/主角分类）；② 哪些还看不到及原因；
③ 五套回归结果；④ 确认没改 `house_shape.gd`、没动排序不变式（A 方案边界守住）。
