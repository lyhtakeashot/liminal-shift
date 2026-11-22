# 开新会话用的提示词：星露谷美术与视觉效果 —— 裁决会话

> 复制「你是」开始的整段到**新会话**第一条消息。
> 这份提示词的目的不是再讨论一轮，而是**把历史上互相矛盾的说法一次性裁掉，产出可执行结论**。
> 所有 file:line 与「现状」均为 2026-11-22 现场 grep / 读文件实测，不要再重新考据。

---

你是《shift》这个 Godot 4.7 像素游戏的**视觉方案裁决人**。

用户开这个会话的原话（2026-11-22）：**「我想做出星露谷的美术和视觉效果，这点通过这几个会话聊下来，好像还是没法解决，或者说说法有矛盾，你写份新的提示词吧，我再开个新会话再尝试一次讨论出结果」**。

所以你的任务**不是再列一遍选项**，而是：
1. 承认并逐条消掉下面第 3 节的矛盾（每处都有 file:line 和原文）；
2. 基于第 2 节的实测现状（这些是事实，不许重新争论）做取舍；
3. **对每个问题给出唯一答案**，产出一份可执行的裁决文档，让美术和引擎线能各自开工。

**你本会话不改任何业务代码和数据，只写一份 `docs/DECIDE-stardew-visual.md`。**

## 1. 项目位置与边界

```
D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift
```

- git 已初始化，`main` 分支，当前 HEAD `a0827df`。**所有 pwsh 调用带 `sandbox_permissions: "danger-full-access"`**（工作区缺 ACL「更改权限」）。
- Godot 不在 PATH，路径：`D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`。
- ⚠️ **有另一条线正在改 A4 精调**（工作区未提交：`_ref/houses/houses_data.json`、`_ref/houses/_redo_shen_a4.py`、`_redo_zheng_a4.py`、`_ref/art/A4_2001/*.png`、`docs/HANDOFF-VILLAGE.md`、`docs/PROMPT-house-size.md`、`docs/PROMPT-a4-houses-exec.md`）。这些文件**只读，绝不写入、绝不提交**。
- 开工前 `git status`，收工只 `git add docs/DECIDE-stardew-visual.md` 再 commit。

## 2. 实测现状（2026-11-22，别再重新讨论这些）

### 已经做了的（伪 3D 的「形」）

| 项 | 位置 | 值 |
|---|---|---|
| 一格 | `scripts/house_shape.gd:13` | `const TILE := 32.0`（唯一定义点） |
| 伪 3D 抬升 | `scripts/world_view.gd:21` | `const EXTRUDE := 32.0`（= 一整格） |
| 墙立面 | `scripts/world_view.gd:281-321` `_draw_walls_lifted()` | 逐格「先南立面、后墙顶面」，同行连续格合并矩形；**四面墙同一画法、整格画满** |
| 进屋不画屋顶 | `scripts/world_view.gd:259-274` `_player_inside()` | 玩家在 `wings` 内整块屋顶消失（娃娃屋剖视），用户 2026-11-21 拍板、已真机验收 |
| 玩家位置通路 | `scripts/main.gd` 两处 `world.set_player_pos(tl.char_pos)` | 每帧 + 换帧各一处 |
| 树抬升 | `scripts/world_view.gd:138-149` | 树干 + 树冠上移 `rad*0.7` |
| 贴图接口 | `scripts/world_view.gd:188-200` `_house_tex()` | 按 `assets/village/houses/<族>/<帧>_{base,roof}.png` 加载，`ResourceLoader.exists()` 缺图静默回落色块 |
| 分辨率 | `project.godot:20-25` | viewport 1280×720、`canvas_items` + `scale_mode=0`（fractional）；1080p=1.5×/1440p=2×/4K=3× |
| 回归 | `_mdtest/{greybox,camera,display,hud_layout}_check.gd` | 四套全绿 |

### 明确没做的（伪 3D 的「遮挡关系」）

| 项 | 证据 |
|---|---|
| 深度排序 | `scripts/world_view.gd:116-173` `_draw_shapes()` 按 `frame.shapes` **数组顺序**画；全项目 grep 无 `sort_y` / `hide_zone` 实现 |
| 玩家参与排序 | `scripts/player.gd:23` 仍 `z_index = 10`，玩家是独立 Node，**永远盖在最上面**，绕到房后不被挡 |
| 南墙半高 | 没有按朝向区分，`_draw_walls_lifted()` 四面一样 |
| 整栋 α 0.4 | 没有实现 |
| 美术资产 | `assets/village/houses/` **0 张**；props 17 张是旧 16px 时代；scene 只有 `tree_old_4x5.png`。`world_view.gd` 只有 houses 的加载代码，props/tree 的接入逻辑还没写 |

### 回归判定口径

沙箱里 `Failed to read the root certificate store.` / `[exit code: 1]` 是固有噪声，判 green 看关键字：`WORLD_OK` / `START_OK` / `WALL_BLOCKED` / `REACH_OK` / `UNEXPLAINED_BLOCKS=0` / `HOTSPOTS_OK`。

## 3. 🔴 七处矛盾 —— 这是本次会话要消掉的核心

> 每一处都有两个（或多个）互相冲突的权威说法。**你的产出必须让每一处只剩一个有效说法**，并写明另一个怎么办（删除 / 标作废 / 改写）。

### C1 — 整栋 α 0.4：必做 vs 已否决

| 说法 | 出处（原文） |
|---|---|
| 必做 | `docs/house-spec.md:560-580` §4.8.3 标题「遮挡：整栋房子降 α 到 0.4（照抄星露谷）」，`:579` 原文「这个机制不是可选项：沈家 A3 被完全遮住的区域 448×316 px……硬挡 5 秒是不可接受的」 |
| 已否决 | `docs/house-spec.md:582-600` §4.8.4「**不做 α 渐变**」；`scripts/world_view.gd:264` 注释「不做 alpha 渐变 —— 用户 2026-11-21 拍板」 |
| 第三方 | `docs/REPORT-house-height.md`（待裁决单）P1③ 把 α 0.4 列为「用户已拍方向但未执行」 |

**事实**：没实现；`world_view.gd:264` 与 §4.8.4 一致，§4.8.3 是残留。

### C2 — 视口「不能改」vs 已经改了

| 说法 | 出处（原文） |
|---|---|
| 不能改 | `docs/HANDOFF.md:396-405` §5.1：内部分辨率 **640×360**、整数倍 3x，`:405` 原文「**这个数一旦定了就不能改**，改了所有素材重画」 |
| 已经改了 | `project.godot:20-25` 现为 1280×720 + `scale_mode=0`；`docs/VERIFY-scale.md` 用户已真机验收接受 1.5×；`docs/REPORT-house-height.md` 已把方案 D 标为完成 |

**残留**：`scripts/display_manager.gd:6` 注释仍写「640×360 / scale_mode=1」；`docs/PROMPT-overseer.md:46-56` 核心数值表全是旧的（TILE 16、世界 1600×900、EXTRUDE 16 等）。

### C3 — 南墙半高 vs 四面画满（**这就是用户说的「能看到部分墙壁」没做到的直接原因**）

| 说法 | 出处（原文） |
|---|---|
| 半高 | `docs/house-spec.md:256-264` §4.5.2「北墙、西墙画全高内侧面；**东墙、南墙只画矮内侧面**（能看出是墙，但不挡住家具和玩家）」；`:729` 坑表「四面墙都画全高 → 南墙挡住整个室内，家具看不见」 |
| 全高 | `docs/PROMPT-pseudo3d.md:52-55` 承认「这只是文档里的设计，代码没实现」；实际 `world_view.gd:281-321` 四面整格画满 |

### C4 — 深度排序：必须做 vs 现状完全没有

| 说法 | 出处（原文） |
|---|---|
| 必须做 | `docs/house-spec.md:532-558` §4.8.2 五层桶 + `sort_y`，`:557`「**`player.gd` 的 `z_index = 10` 会变成废字段**」；`:666` 坑表「玩家留在 `z_index = 10` → 绕到房子后面仍画在屋顶上，伪 3D 直接失效」 |
| 现状 | `scripts/player.gd:23` 仍 `z_index = 10`；`world_view.gd:116-173` 顺序绘制 |

### C5 — 同一份文档内部打架：`_draw()` 里到底能不能 y-sort

| 说法 | 出处（原文） |
|---|---|
| 做不到 | `docs/PROMPT-pseudo3d.md:76`「伪 3D 需要逐对象排序，这**在单 `_draw()` 里做不到**」 |
| 做得到 | 同一文件 `:81` 方案 B「**保留单 `_draw()`，自己排序**：先收集所有可排序对象，按 `sort_key` 排好，再顺序 `draw_*`」 |

**提示**：技术上「先收集 → 排序 → 再 draw」是可行的，`:76` 的结论可能是早期判断，需要你明确裁定哪个有效。

### C6 — 美术规格：+32 还是 +16

| 说法 | 出处（原文） |
|---|---|
| +32 / 两图 | `docs/house-spec.md:602-605` §4.8.5 外观层拆 `base` + `roof`，画布高 = 占地高 + 32；`:677-692` §5 三层 `base`/`roof`/`props`、锚点底部中心 |
| +16 | `docs/PROMPT-art-canvas-h16.md` 标题「任务书：外观画布高度 **+16px**」；`docs/PROMPT-tile-32px.md:143` 自己承认「这条线定的是 +16，格子从 16 改 32，+16 也要变成 +32，**两条线会撞车**」 |
| 家具多画一格 | `docs/art-assets-a1a3.md:298`、`docs/HANDOFF-VILLAGE.md:178`：家具源图高度常比占地多一格，占地看数据不看 PNG |

**事实**：美术资产还是空的，规格没冻结就让美术开画必返工。

### C7 — 老提示词的「现状」已过期

`docs/PROMPT-pseudo3d.md:34-55` 写「游戏是纯 2D 俯视，**没有任何伪 3D**」「墙是平铺的 16×16 方块」，但实测 `EXTRUDE=32`、墙立面、树抬升、进屋不画屋顶都已实现。**不要照抄这份文档的现状章节。**

> 附带过期信息：`docs/house-spec.md:709` 写「当前模型看不到图片（`read_image` 返回 image omitted）」——那是当时的环境状态，不是项目事实。参考图在 `_ref/stardew/`，`contact_sheet.jpg` 是入口。

## 4. 不可让步的硬约束（不许拿来交换）

1. **内外严格 1:1**：外观占地必须精确等于内部可行走区 + 墙厚（`docs/house-spec.md` §0.1 / §4.5.1）。差一格，推时间就卡墙里。**不学星露谷「内部比外部大」**（`PROMPT-house-size.md:67` / `house-spec.md:36`）。
2. **碰撞纯数据 AABB**：`scripts/frame_data.gd:is_free()` 不引 `CollisionShape2D` / 物理引擎（`docs/HANDOFF.md` §3.3/§3.4）。视觉高度不影响碰撞。
3. **不改 `_ref/houses/houses_data.json`**：A4 精调线正在写，只读。
4. **不碰 `data/frames.json`**：用户 2026-11-22 明确撤回「落地到 frames.json」；A4/A5 空帧冻结等精调。
5. **高度不进逐帧数据**：`EXTRUDE` 写死在代码里，不给 `frames.json` 加 `roof_height`（`house-spec.md:524-530`、`:665`，否则「房子在呼吸」）。
6. **不做屋顶 α 渐变**：§4.8.4 已定「进屋直接不画屋顶」，用户已真机验收。若你要推翻，必须明确写一个「推翻已验收项」的理由让用户再拍一次。

## 5. 必须给出唯一答案的问题（共 8 个，禁止「都可以」）

### D1 — 目标拆解：你要的「星露谷效果」到底包含哪些？

从下面勾选并排 P0/P1/P2，**不许写「全都要」**：

- A 建筑立面 + 屋顶的立体观感（已部分实现）
- B y-sort 遮挡（玩家绕到房后被房子挡、绕到家具后被家具挡）
- C 南墙半高（能看见部分室内）
- D 整栋 α 半透（被挡时看穿）
- E 家具多格分级 + 源图多画一格（美术规格）
- F 32px 重画全部素材（资产量）
- G 其他（写明）

### D2 — C1 怎么裁？（三选一，必须指定回写哪几行）

`① 删掉 §4.8.3，正式标记「已否决」` / `② 恢复 α 0.4 机制` / `③ 改成条件触发（写清触发条件）`

### D3 — C3 怎么裁？

南墙画全高还是半高？若半高，矮到多少（占 `TILE` 的 1/2 还是 1/3）？这个数直接决定「玩家能看到部分墙壁」成不成立。同时回答：按朝向区分需要改 `HouseShape.solid_rects()` 的返回结构吗？

### D4 — C4/C5 架构选型（A/B/C 三选一）

- A 全改 `Node2D` 子节点 + `y_sort_enabled`
- B 保留单 `_draw()`，收集可排序对象 → 排序 → 绘制
- C 混合：场景层留在 `_draw()`，立体对象独立 Node2D

必须写清：理由、切帧（时间轴推一年）怎么处理、`player.gd:23 z_index=10` 改成什么、C5 那句「做不到」是否判为作废。

### D5 — 屋顶规则是否维持现状？

维持「进屋不画屋顶」（用户已验收）还是改别的？若改，说明和 §4.8.4、和已验收的关系。

### D6 — C6 美术规格冻结成哪一套？

明确答案：`base`/`roof` 是否需要、`props` 独立对象还是贴图、画布高 = `lot_h + 32`、锚点底部中心、家具源图多画一格是否采纳、`PROMPT-art-canvas-h16.md` 是否标作废。**这条冻结后美术才能开画。**

### D7 — C2 分辨率是否正式定案？

1280×720 + `scale_mode=0` 是否最终值？`HANDOFF.md §5.1` 的「不能改」是否标注作废？`scripts/display_manager.gd:6`、`docs/PROMPT-overseer.md:46-56` 的旧值要不要列入回写清单？

### D8 — 顺序：机制先行还是美术先行？

给出可执行顺序 + 每步验收点。必须回答：**美术资产一张都没有的当下，用什么降级**（现有 `_house_tex()` 色块 fallback 是否保留）。

## 6. 输出要求（落盘 `docs/DECIDE-stardew-visual.md`）

1. **裁决表**：D1–D8 每项一行——结论一句话 + 依据（file:line）+ 影响哪些文件。
2. **矛盾销账表**：C1–C7 每项写明「保留哪个说法 / 另一个怎么处理（删除 / 标 SUPERSEDED / 改写）」，不许留「待定」。
3. **作废与回写清单**：明确列出需要标 `SUPERSEDED` 的段落（如 `house-spec.md §4.8.3`、`PROMPT-art-canvas-h16.md`、`PROMPT-pseudo3d.md §现状`）和需要改数字的旧行（带 file:line）。本会话**只列清单不改那些文件**。
4. **验收标准**：写 6–10 条可勾选的画面检查项（例：「玩家站房北→被房挡住」「站房南→挡住房」「南墙只挡半截能看见家具」），让下一会话能照着判通过。
5. **结尾一句话**：我们到底做不做 X、谁来做、先做哪个。
6. 如果读完觉得某个问题必须用户本人拍板，**最多精简成 3 个问题直接问**，不要罗列 20 个问号就结束——这次会话的目的是收敛。

## 7. 纪律

- **本会话只写 `docs/DECIDE-stardew-visual.md`**，不写业务代码、不写 `houses_data.json`、不写 `frames.json`。
- 先读文档再下结论；不要读 `docs/story.md` 全文（与渲染无关）。
- 拿不准的地方标「需用户拍板」，**不要猜着写进结论**。
- 要跑验证时用四套 `_mdtest/*_check.gd`，判关键字不判退出码。
- 时间背景：`docs/house-spec.md:767-771` 原写截止 2026-12-02 05:37（北京时间），那是 11-19 的记录，现只剩约 10 天——所以这次必须收敛，不能再开一轮「再讨论讨论」。
