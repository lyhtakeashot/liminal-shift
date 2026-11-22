# 裁决：星露谷美术与视觉效果（2026-11-22）

> 本文件是 `docs/PROMPT-stardew-visual-decision.md` 的产出。
> 目的：把历史上互相矛盾的说法一次性裁掉，给美术线和引擎线各一份可开工的唯一答案。
> 所有 file:line 与「现状」均为 2026-11-22 现场实测；本会话**不改业务代码与数据**，只列回写清单。
> 开工前 `git status` 已核对：A4 精调线的改动（`_ref/houses/*`、`docs/HANDOFF-VILLAGE.md` 等）全程只读、未写入、未提交。

---

## 0. 一句话总纲

星露谷效果 = **P0 补齐 y-sort 遮挡 + 南墙半高**，**美术按冻结的「base/roof 两张、画布 `lot_h + 32`、底部中心锚点」规格开工**；
**整栋 α 0.4 不做**（已否决）、**屋顶渐变不做**（已验收）、**内外 1:1 / 纯 AABB 碰撞不动**（硬约束）。
引擎线先做机制（用现有色块降级验证，不等美术），美术线按冻结规格并行重画。

---

## 1. 裁决表 D1–D8

| 问题 | 结论（唯一答案） | 依据（file:line） | 影响文件 |
|---|---|---|---|
| **D1** 目标拆解 | **P0：A 建筑立面/屋顶立体观感（已部分实现，补齐即可）+ B y-sort 遮挡（核心缺口）**；**P1：C 南墙半高 + E 家具多格分级/源图多画一格**；**P2：D 整栋 α 半透（本轮不做）**；**F 32px 重画全部素材**是美术线开工前提，不进引擎优先级（引擎用色块降级不阻塞）；G：树抬升（`world_view.gd:138-149`）保持，不做真透视/等距 | A 已实现见 `world_view.gd:21,281-321`；B 缺口见 `world_view.gd:116-173`、`player.gd:23`；硬约束见 `house-spec.md §0.1/§3` | `scripts/world_view.gd`、`scripts/player.gd`、`scripts/house_shape.gd`、美术交付包 |
| **D2** C1（α 0.4）怎么裁 | **① 删掉 §4.8.3，正式标「已否决 / SUPERSEDED」**。不恢复、不做条件触发 | `world_view.gd:264` 注释「不做 alpha 渐变 —— 用户 2026-11-21 拍板」与 `house-spec.md:582-600` §4.8.4 一致；§4.8.3（`:560-580`）是残留；硬约束 #6 | `docs/house-spec.md §4.8.3` 标 SUPERSEDED；`docs/REPORT-house-height.md:37-38,66` 销账 |
| **D3** C3（南墙半高） | **改半高**：北/西墙全高（= TILE 32px）、**东/南墙半高 = TILE/2 = 16px**（可见是墙但不挡家具）。**不改 `solid_rects()` 的返回结构**——碰撞恒为整格 AABB；在 `house_shape.gd` 新增一个**渲染专用**的墙向分类器（基于 `grid_of()` 的相邻格判断朝向），供 `world_view.gd` 用 | `house-spec.md:256-264` §4.5.2 是正解、`:729` 坑表；代码现状 `world_view.gd:281-321` 四面画满；`solid_rects()` 在 `house_shape.gd:176-190` 返回纯 `Rect2` | `scripts/house_shape.gd`（新增分类器）、`scripts/world_view.gd:_draw_walls_lifted()` |
| **D4** C4/C5 架构 | **选 B：保留单 `_draw()`，收集可排序对象 → 排序 → 绘制**。切帧天然干净（`show_frame()` 换 frame 即整帧重绘，无节点增删、无残影）；`player.gd:23 z_index=10` **删除**（玩家不再独立叠在最上，绘制并入排序循环）；**C5 的「做不到」（`PROMPT-pseudo3d.md:76`）判为作废**，采用同文件 `:81` 方案 B | `world_view.gd:335-336` 已在 `_draw()` 内对 wings `sort_custom`——证明单 `_draw()` 内排序可行；`house-spec.md:532-558` 五层桶 + `sort_y`；场景树 `scenes/main.tscn:22-30` WorldView(Control) 与 Player(Node2D) 是兄弟节点，独立 z_index 无法插入 `_draw()` 内部顺序 | `scripts/world_view.gd`（排序循环 + 吸收玩家绘制）、`scripts/player.gd`（绘制抽成 `draw_self()`、删 z_index）、`scripts/main.gd`（把玩家状态喂给 world_view） |
| **D5** 屋顶规则 | **维持「进屋不画屋顶」**（用户 2026-11-21 拍板、已真机验收）。不改 §4.8.4、不做渐变。要改必须先写「推翻已验收项」理由请用户再拍 | `world_view.gd:259-274`、`house-spec.md:582-600` §4.8.4、硬约束 #6 | 无（维持现状） |
| **D6** C6 美术规格 | **冻结**：`base` + `roof` **两张都要**（废墟 `lu_a3` 只有 base）；`props` 家具是**独立数据对象**（有 pos/size/reach，贴图只是其外观）；画布高 = `lot_h + 32`（TILE 已 32）；**锚点底部中心**；**采纳家具源图多画一格**（画布 = 占地高 + 32，多出的一格在顶部做立面，但占地/碰撞读数据不读 PNG）；**`PROMPT-art-canvas-h16.md` 标 SUPERSEDED**（+16 是 16px 时代产物） | `house-spec.md:602-622` §4.8.5、`:677-692` §5；`art-assets-a1a3.md:298`、`HANDOFF-VILLAGE.md:178`；`PROMPT-tile-32px.md:143` 撞车说明 | 美术交付包 23 张 P0 外观 + 家具；`docs/PROMPT-art-canvas-h16.md` 标 SUPERSEDED |
| **D7** C2 分辨率 | **正式定案 1280×720 + `canvas_items` / `scale_mode=0`**（1080p=1.5×、1440p=2×、4K=3×）。`HANDOFF.md §5.1` 的「640×360 不能改」**标 SUPERSEDED**（「定案后不再改」的原则保留，但值换成 1280×720） | `project.godot:20-25`、`docs/VERIFY-scale.md` 用户已真机验收、`REPORT-house-height.md:19`；残留 `display_manager.gd:6-8`、`PROMPT-overseer.md:46-56` | `docs/HANDOFF.md:396-405`、`scripts/display_manager.gd:6-8`、`docs/PROMPT-overseer.md:46-56` 列入回写清单 |
| **D8** 顺序 | **机制先行**：① y-sort 遮挡 → ② 南墙半高 → ③ 美术按 D6 规格重画并接入 → ④ 家具多格分级等 P1。**降级**：`_house_tex()`（`world_view.gd:188-200`）的「缺图静默回色块」**永久保留**，作为优雅降级与分批交付保障。美术线不必等引擎，按 D6 冻结规格即可开工 | `world_view.gd:188-200`、`house-spec.md:691`「缺文件退回纯色占位块」；美术资产现状 `assets/village/houses/` 0 张 | 执行顺序见 §4 |

---

## 2. 矛盾销账表 C1–C7

| 矛盾 | 保留哪个说法 | 另一个怎么处理 | 状态 |
|---|---|---|---|
| **C1** 整栋 α 0.4 | **保留「不做 α 渐变」**：`house-spec.md §4.8.4`（`:582-600`）+ `world_view.gd:264` + 用户 2026-11-21 拍板 | `house-spec.md §4.8.3`（`:560-580`）整段**标 SUPERSEDED（已否决）**；`REPORT-house-height.md:37-38,66` 销账为「已裁决：否决」 | ✅ 销账 |
| **C2** 视口能否改 | **保留现值**：`project.godot:20-25` 1280×720 + scale_mode=0 + 用户真机验收 | `HANDOFF.md:396-405 §5.1`「640×360 不能改」标 SUPERSEDED、`display_manager.gd:6-8` 与 `PROMPT-overseer.md:46-56` 旧值**改写**（见 §3） | ✅ 销账 |
| **C3** 南墙半高/四面画满 | **保留半高**：`house-spec.md §4.5.2`（`:256-264`）+ `:729` 坑表 | `world_view.gd:281-321` 四面画满的实现**改写**为按朝向区分；§4.5.2 `:264` 那句「四面全高技术上也能做」**标 SUPERSEDED**（本裁决排除） | ✅ 销账 |
| **C4** 深度排序 | **保留「必须做」**：`house-spec.md §4.8.2`（`:532-558`）+ `:666` 坑表 | `player.gd:23 z_index=10` 删除；按 D4 方案 B 实现 | ✅ 销账 |
| **C5** 单 `_draw()` 能否 y-sort | **保留 `:81` 方案 B「做得到」** | `PROMPT-pseudo3d.md:76`「做不到」**判为作废（SUPERSEDED）**——已有 `world_view.gd:335-336` 反证 | ✅ 销账 |
| **C6** 美术 +32 还是 +16 | **保留 +32**：`house-spec.md §4.8.5`（`:602-622`）+ §5（`:677-692`）+ `PROMPT-tile-32px.md:143` | `PROMPT-art-canvas-h16.md` 整份**标 SUPERSEDED**；家具「多画一格」按 D6 正式采纳（读数据不读 PNG） | ✅ 销账 |
| **C7** 老提示词现状过期 | **保留实测现状**（本文件 §0/§1） | `PROMPT-pseudo3d.md:34-55` 的「纯 2D 无伪 3D / 16×16 墙 / 1600×900」现状章节**标 SUPERSEDED**；`house-spec.md:709`「模型看不到图片」标为历史环境注记（非项目事实） | ✅ 销账 |

> 附带：`REPORT-house-height.md` 是待裁决单，其 P1③（`:37-38`）与回填框（`:66`）在本裁决后**销账为「否决 α 0.4」**；P0① frames.json 落地仍冻结（等 A4 精调完成），与本裁决无关。

---

## 3. 作废与回写清单（本会话只列清单，不改这些文件）

### 3.1 标 `SUPERSEDED`（保留原文、加作废标记）

| 位置 | 处理 |
|---|---|
| `docs/house-spec.md:560-580` §4.8.3 | 顶部加 `> SUPERSEDED（2026-11-22 裁决：已否决，见 DECIDE-stardew-visual.md D2）` |
| `docs/house-spec.md:264` §4.5.2 末句「四面全高技术上也能做」 | 加 SUPERSEDED 注记 |
| `docs/house-spec.md:709-711` 「当前模型看不到图片」 | 标为历史环境注记（2026-11-19 状态），非项目事实 |
| `docs/PROMPT-art-canvas-h16.md`（整份） | 标题下加 `> SUPERSEDED：画布高应为 lot_h + 32（TILE 已 16→32），见 DECIDE D6` |
| `docs/PROMPT-pseudo3d.md:34-55` 现状章节 | 加 `> SUPERSEDED：现状已实现 EXTRUDE=32/墙立面/树抬升/进屋不画屋顶，勿照抄` |
| `docs/PROMPT-pseudo3d.md:76`「做不到」 | 加 `> SUPERSEDED：方案 B（:81）成立，见 DECIDE D4/C5` |
| `docs/HANDOFF.md:396-405` §5.1 旧分辨率 | 标 SUPERSEDED，保留「定案后不再改」原则、换成新值 |

### 3.2 改数字的旧行（带 file:line）

| 位置 | 旧值 → 新值 |
|---|---|
| `scripts/display_manager.gd:5-8` 注释 | `scale_mode=1 / 640×360 / 2x` → `scale_mode=0 / 1280×720 / 1.5×~3× fractional` |
| `docs/PROMPT-overseer.md:46` | `TILE := 16.0` → `TILE := 32.0`（`house_shape.gd:13`） |
| `docs/PROMPT-overseer.md:47-49` | `640×360 / scale_mode=1` → `1280×720 / canvas_items + scale_mode=0` |
| `docs/PROMPT-overseer.md:50` | 世界 `1600×900` → `3200×1800` |
| `docs/PROMPT-overseer.md:52-55` | 主角/半径/`EXTRUDE:=16` → 按 32px 口径重填（`EXTRUDE:=32`，`world_view.gd:21`） |
| `docs/house-spec.md:524` | `EXTRUDE := 16.0` → `32.0`（代码已是 32，文档同步） |
| `docs/REPORT-house-height.md:37-38,66` | P1③ 标记「已裁决：否决 α 0.4，见 DECIDE D2」 |

> `docs/HANDOFF.md §5.1`、`docs/PROMPT-overseer.md` 等由总策划指定唯一写入者在后续会话统一回写；本会话**不碰**。

---

## 4. 执行顺序与验收点（D8 展开）

| 步 | 内容 | 谁 | 验收点 |
|---|---|---|---|
| 1 | **y-sort 遮挡**（方案 B）：`world_view.gd` 收集 houses/trees/furniture/player → 按 `sort_y`（底边）排 → 顺序 `draw_*`；`player.gd` 绘制抽成 `draw_self()`、删 `z_index=10`；`main.gd` 把玩家状态喂进 world_view | 引擎线 | 玩家站房北→被房挡；站房南→挡住房；切帧无残影；四套回归关键字全绿 |
| 2 | **南墙半高**：`house_shape.gd` 新增渲染专用墙向分类器；`_draw_walls_lifted()` 按朝向画 32/16px | 引擎线 | 站房外南侧→看到半截墙 + 家具可见；碰撞不变（推时间不卡墙） |
| 3 | **美术重画 + 接入**：按 D6 冻结规格出 23 张 P0 外观（+32/底部中心/base+roof），走现有 `_house_tex()` 接入 | 美术线（并行） | 贴图加载不报错；进屋屋顶整块消失不渐变；base/roof 切换无跳变；缺图自动回色块 |
| 4 | **P1 收尾**：家具多格分级 + 源图多画一格接入；`PROMPT-art-canvas-h16.md` 等作废标记回写 | 引擎 + 美术 | 家具绕后遮挡成立；文档引用检查无残留旧值 |

**降级策略**：第 1–2 步全程用现有色块（无美术资产）验证；`_house_tex()` 的 `ResourceLoader.exists()` 缺图回色块**永久保留**，美术分批交付期间游戏始终可跑。

---

## 5. 验收标准（可勾选，下一会话照此判通过）

- [ ] 玩家站房子北侧 → 玩家被房子/屋顶遮住（y-sort 生效，`z_index=10` 已删）
- [ ] 玩家站房子南侧 → 玩家挡住房子南立面
- [ ] 玩家绕到家具后方 → 被家具挡住；绕到前方 → 挡住家具
- [ ] 玩家在房外南侧 → 东/南墙只画半高（16px），室内家具可见；北/西墙全高（32px）
- [ ] 玩家进屋（wings 内）→ 屋顶**整块消失**，无 α 渐变、无半透明糊叠
- [ ] 时间轴推一年 → 整帧干净切换，无残影、无重复节点、无「房子呼吸」
- [ ] 缺美术图时 `_house_tex()` 静默回色块，游戏可跑；有图时正常加载
- [ ] 美术交付图：base/roof 同宽同高同锚点，画布高 = `lot_h + 32`，锚点底部中心
- [ ] 内外 1:1 与 AABB 碰撞未变，`_mdtest/{greybox,camera,display,hud_layout}_check.gd` 关键字全绿（`WORLD_OK / START_OK / WALL_BLOCKED / REACH_OK / UNEXPLAINED_BLOCKS=0 / HOTSPOTS_OK`）

---

## 6. 结尾（一句话）

**做**星露谷效果，但只做「y-sort 遮挡 + 南墙半高 + 冻结美术规格」这三件；**引擎线先做机制**（色块降级验收），**美术线按 +32/base+roof 规格并行重画**，整栋 α 0.4 与屋顶渐变**不做**。

> 需用户本人拍板的事项：本裁决**无需新增拍板**（未推翻任何已验收项）。若日后想恢复 α 0.4 或改屋顶规则，须按硬约束 #6 另写「推翻已验收项」理由重新拍板，不得复活已 SUPERSEDED 的 §4.8.3。
