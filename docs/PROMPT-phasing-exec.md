# L17 · 卡墙虚化（phasing）执行提示词

> 这条线把「推时间被墙顶住」换成「主角虚化穿过去」。
> 用户 2026-11-26 拍板：**顶住这点去掉，只做虚化。**「顶住了」是总策划自己补上的、用户没批准的内容，本线负责把它从代码里拿掉，并把 `docs/house-spec.md` §8.3 写的虚化机制真正做出来。
>
> 用户同一天补充了触发条件的口径（本线必须照此实现，**这是判断 phasing 做得对不对的标尺**）：
> 「我们只需要保证包围可探索建筑的房屋、山体的位置大致是不变的……只要包围的空气墙（实体房屋、山）的范围是一致的，这就不会有卡到山里，从而通过虚化卡到地图之外的现象。」
> 翻译成可执行口径：
> 1. **正常游玩不该触发 phasing。** 跨帧推时间的落点如果会「从空地突变实体」，那是**地图线的错**（A4 重排线在修），不是 phasing 该兜的底。
> 2. **phasing 只在「实体范围内」兜底**：玩家此刻已经站在实体里（墙里、山体里、或被未来的房子包住），需要一条不被 `is_free()` 拦死的出路。
> 3. **phasing 不能把人带出地图**：虚化位移必须始终留在世界的实体范围内，绝不出现「虚化到地图之外」。
> 4. **不做楼层。** 用户 2026-11-26：「不做楼层了，时间不够了。」本线只做 phasing，不做 §8.1 方案 C。

---

## §0 开工前

### §0.1 路径与工具

- 仓库根：`D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift`
- Godot 可执行：`D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`（**不在 PATH**，跑的时候写全路径）
- 跑回归（**看关键字不看退出码**；沙箱固有噪声 `Failed to read the root certificate store.`、`Failed to open 'user://logs/godot...log'` 属正常）：

```
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . -s res://_mdtest/xxx_check.gd 2>&1 | Select-Object -Last 45
```

- 七套回归全名：`_mdtest/greybox_check.gd`、`_mdtest/camera_check.gd`、`_mdtest/hud_layout_check.gd`、`_mdtest/asset_draw_check.gd`、`_mdtest/sort_check.gd`、`_mdtest/evidence_archive_check.gd`、`_mdtest/display_check.gd`

### §0.2 HEAD 下限与**版本自检**

- HEAD 必须 **≥ `4e10958`**（＝四份新任务书 L15/L16/L17/A4 重排线落盘那笔）。
- 🔴 **更要紧的是版本自检**：打开本文件确认 §2.3 里已经有「**正常游玩不该触发 phasing**」那一段、
  且 §3.8 第 1 条写的是「用户已确认不做楼层」。
  - 若本文件还是旧版（§2.3 只写「替代原来的 bump 拒绝」）⇒ **你拿到的是旧任务书，停下报告**，不要按旧口径开工。
  - 若 HEAD 早于 `4e10958` ⇒ 说明缺前置，**先停下报告**，不要在旧基线上改。

### §0.3 开工前必须先跑一遍基线（七套回归）

开工前把七套全跑一遍，把输出存进 `lab/_l17_baseline.txt`（新建目录）。
**如果基线本身就有红项，停下报告**，不要在红基线上开工。

### §0.4 脏工作区纪律（**本条最容易出事**）

工作区长期脏，且**有些是别的线/美术同学的**：

- `M _ref/art/A1_1926/*.png` 等 11 张 —— 美术线，**一个字都不许碰**
- `D 美术资产/**` 一批 —— 用户自己删的，**不许恢复**
- 大量未跟踪 `lab/_*`、`docs/FEEDBACK-*`、`.import`

规矩：
1. **只精确 `git add` 自己那批文件，绝不 `git add -A`、绝不 `git add .`**
2. 提交前用 `git diff --stat` 逐个确认自己那几个文件的改动量
3. **不许 `git checkout -- <file>`**（会被沙箱拦），要还原用 `git show HEAD:<path>` 按字节写回
4. 长文件（>200 行）不要用编辑工具改长行，容易失败；用 python 脚本按行号改，脚本放 `lab/`

### §0.5 本线要碰的文件（**允许改**）

| 文件 | 改什么 |
|---|---|
| `scripts/timeline.gd` | 删 bump 机制、加 phasing 状态与位移 |
| `scripts/main.gd` | 删 bump 接线、加 phasing 输入与绘制通路 |
| `scripts/player.gd` | 删 bump_kick、加虚化透明度 |
| `scripts/world_view.gd` | 删震屏、加 phasing 半透明绘制 |
| `scripts/hud.gd` | 删 bump 红环、换成 phasing 提示 |
| `scripts/frame_data.gd` | **只读不改**（除非要加一个查询方法，见 §3.4） |
| `project.godot` | 可选：新增 phasing 专用 action（**改了要重启编辑器才生效**，见 §3.3） |
| `_mdtest/greybox_check.gd` | 改时间轴断言（见 §3.6） |
| `_mdtest/greybox_shot.gd` | 删撞墙截图、改虚化截图（见 §3.6） |
| **新建** `_mdtest/phasing_check.gd` | 本线专属回归 |
| `docs/HANDOFF.md` | §3.4 口径改写、特性表改写 |
| `docs/house-spec.md` | §8.3 标为「已实现」、§8.4 排期更新 |
| `docs/story.md` | **本线不动**（叙事不涉及） |
| **新建** `docs/FEEDBACK-phasing-exec.md` | 反馈文档，≤120 行 |

### §0.6 本线**不许碰**的文件

- `data/frames.json`（L1 独占）
- `_ref/houses/houses_data.json`（房屋数据域）
- `scripts/house_shape.gd`（L4 独占）
- `scripts/evidence_store.gd`、`scripts/evidence_archive.gd`（证物域）
- `scripts/camera_rig.gd`、`scripts/asset_draw.gd`、`scripts/display_manager.gd`
- `assets/**`、`_ref/art/**`
- `_mdtest/` 里除上面点名的两套之外的其他五套 —— **它们的断言一条都不许改**

### §0.7 串行提醒（本线会撞人）

- `scripts/world_view.gd` 的归属写者锁在 `docs/PROMPT-overseer.md` §四（`:156`）＝ **L2 独占**。L2 已交付，但**L8 资产接线线还没开工，而它也要改 `world_view.gd`**。
  ⇒ **开工前先看 `docs/PROMPT-overseer.md` §十一「不能开」表，如果 L8 正在跑，本线必须等 L8 交付后再开**。
- 本线**不改** `data/frames.json`、**不改** `scripts/house_shape.gd`，所以跟 A4 重排线、地图线不冲突。

---

## §1 独占写入文件

本线**独占**（同一时间不许别的线碰）：

1. `scripts/timeline.gd`
2. `scripts/player.gd`
3. `scripts/hud.gd`
4. `_mdtest/phasing_check.gd`（新建）
5. `docs/FEEDBACK-phasing-exec.md`（新建）

本线**独占但别人也在改**（要串行）：`scripts/main.gd`、`scripts/world_view.gd`。

本线**可小改**：`scripts/frame_data.gd`、`project.godot`、`_mdtest/greybox_check.gd`、`_mdtest/greybox_shot.gd`、`docs/HANDOFF.md`、`docs/house-spec.md`。

> 提交纪律：三段 commit，见 §5。

---

## §2 数据基准

### §2.1 两条既有口径（必须先分清，这是本线的全部前提）

代码里现在跑的是**「顶住了」**，文档里另有一套**「卡墙虚化」**。二者不是同一场景，本线要删前者、实现后者。

但**还有一个更前置的问题**：用户 2026-11-26 指出，「推不过去」这件事本身不该由游戏机制来兜——
「我们只需要保证包围可探索建筑的房屋、山体的位置大致是不变……只要包围的空气墙（实体房屋、山）的范围是一致的，
这就不会有卡到山里，从而通过虚化卡到地图之外的现象」。
⇒ **空气墙一致性是地图线（A4 重排线 / A1–A3 重排线）的活，不是 phasing 的活**；
**phasing 是兜底，不是主力**。本线做的是「万一还是落进了实体里，玩家有一条不被拦死的出路」。

本线的验收标准因此分成两层：
- **功能层**：虚化能进、能出、不卡死、不出地图、看得懂（半透明 + 提示）。
- **口径层**：正常游玩（空气墙一致的帧之间）**不会**触发虚化。

**口径 A｜顶住了（要删）**

- `docs/HANDOFF.md:239-249` §3.4：「如果目标帧里，角色的碰撞盒和固体重叠 → 卡住，推不过去」
- 实现：`scripts/timeline.gd:78-92 step_time()` 里 `if not frames[target].is_free(char_pos): bump.emit(index); return false`
- 反馈：顿帧 / 震屏 / 红环 / 闷响
- 后果：**推不过去的那些点，玩家就永远过不去那一帧**

**口径 B｜卡墙虚化（本线要做的）**

- `docs/house-spec.md:757-771` §8.3「卡墙虚化 = 主题机制，不是穿帮」
- 用户 2026-11-19 m01214 原话：「主角是游离于世界之外的人，『被墙遗忘』合理」⇒ 会出现**建模与墙重合、主角虚化**的现象
- 触发：推时间时目标帧该坐标**落在墙体/建筑占地内** ⇒ **不 bump**，而是进入 **phasing（虚化）状态**
- 视觉：半透明（文档建议 alpha ≈ 0.4）＋轻微色差
- 移动：phasing 期间临时启用 A/D 做「往里走 / 往外走」
- ⚠️ **phasing 期间必须绕过 `is_free()`**（见 §3.2）

### §2.2 phasing 的完整生命周期（文档原文口径）

`docs/house-spec.md:765-769` 的实现约定，逐条照做：

1. **phasing 时 char_pos 正落在目标帧的 solid_rects 里** ⇒ `move_space()` → `is_walkable()` → `frames[i].is_free(at)` 恒 false，**一步都挪不动**。
2. 正确做法＝**phasing 走独立位移路径，直接改 char_pos，不查 `is_free()`**。
3. 每步结束检查 `if frames[index].is_free(char_pos): 退出 phasing`。
4. 「往里走」＝进一步进入建筑/墙体内部；「往外走」＝退到最近的自由表面（室外地面或室内地面）。
5. 正常时间轴手感（W/S 推年份）**不变**；A/D 在**非 phasing 状态**下仍然没有作用（原设计如此，见 `docs/house-spec.md:761`）。

### §2.3 触发条件要写成「可判定」的，不能靠感觉

判定用现成的 `FrameData.is_free(at)`：
- 推时间到目标帧 ⇒ 若 `frames[target].is_free(char_pos)` 为 **true** ⇒ 正常落在自由面，**不进 phasing**（现有行为不变）
- 为 **false** ⇒ 目标帧该位置被固体重叠 ⇒ **进入 phasing**（替代原来的 bump 拒绝）

「被固体重叠」包含两类，都算：
- 落在 `solid_rects` 里（墙、地块、坝、路标这类手写 solid 形状）
- 落在某栋 house 的 `lot` 占地内（房屋实体）

#### 🔴 「正常不该触发」是本线的第一验收项（用户 2026-11-26）

用户口径：「包围的空气墙（实体房屋、山）的范围是一致的，这就不会有卡到山里，从而通过虚化卡到地图之外的现象。」

拆成两条可测的规则：

1. **跨帧空气墙一致 ⇒ 落点不该从空地突变实体。**
   空气墙的口径＝**房屋 `lot` 外框 ∪ 山体多边形**（路/田/井/树/内岛/环道都是 `solid:false`，**不算**空气墙）。
   A4 重排线正在把 A4 的空气墙对齐到 A5（A5↔A4 的 IoU 目标 100%、触发格数 0）；
   A1–A3 之后也要按同一口径对齐（另派线）。
   ⇒ **在空气墙已对齐的相邻两帧之间，玩家站在可站点上推时间，**目标帧同一坐标**必须仍是可站点**，否则就是地图没对齐，**不是 phasing 该管的事**。
2. **万一还是落进实体（兜底）**：进入 phasing，并且**只能在实体范围内活动**——
   「往里走」不许越过空气墙外边界，「往外走」必须走到实体范围内的自由面。

> ⚠️ 因此本线**不要**用「越多地方能虚化越好」来自我验收；验收要看的是「空气墙一致时几乎不触发，
> 真触发了也能安全进出」。

> 实测参考（`lab/_probe_push_trap.gd` 等三个探针，已入库）：
> A1 可站点 15104 个；推到 A5 被挡 1399 个，其中 **81% 是 A5 新建四栋主宅的占地**、79% 是 A5 的山。
> ⇒ 这些「被挡」绝大多数是**地图没对齐**造成的（A4/A5 与 A1–A3 的空气墙差异大），
> 地图线修完它们会自然减少。**别把 phasing 当成解法。**

### §2.4 「往外走」的落点规则（本线自定，但要写清楚）

phasing 里往外走，落到哪儿？**按这个顺序找，找到第一个就停**：

1. 沿当前朝向的反方向直线回退，每 8px 测一次 `frames[index].is_free(候选点)`，第一个自由点即落点（最多回退 256px）
2. 回退 256px 还没找到 ⇒ 落回**推出前那个坐标所在帧**的自由点（用 `frames[index-1].is_free()` 找最近的）
3. 还找不到 ⇒ 保持当前点，**留在 phasing**（不要把玩家丢进虚空）

🔴 **两条硬约束（用户 2026-11-26）**：
- **不许虚化出地图**：任何落点必须留在世界矩形内（`[0,0]..[world_size]`），也不许离开实体空气墙的范围。
- **不许虚化进虚空**：往外走找不到自由面时留在原地（见上第 3 条），绝不能把玩家放到没有任何东西的地方。

「往里走」＝沿当前朝往前推 8px/步，最多 6 步（48px），进去后仍然是 phasing（因为里面还是墙/占地）。往里走到头（推不动）就停住。

> 这三条是本线自定的实现细节，**执行方可以在反馈文档里提出更好的方案**，但必须保证：**玩家永远不会因为 phasing 而卡死或丢失位置**。

### §2.5 phasing 状态的可见反馈（最小集）

必须让玩家知道「我现在在虚化」：
- 主角半透明（alpha ≈ 0.4）
- 轻微色差（文档建议；具体色值自定，但要和正常态可区分）
- HUD 时间轴上给一个提示（替换掉原来 bump 的红环）

---

## §3 必改清单（**七件，一件都不能漏**）

### §3.1 第一件：删掉「顶住了」的全部代码

**这是本线的第一优先。** 逐处删/改：

**`scripts/timeline.gd`**
- `:7` 文件头注释「2. 推时间不做『弹回去』，做『顶住了』…」⇒ 整条删掉或改写成 phasing 口径
- `:15` `signal bump(index: int)` ⇒ **删**
- `:78-92` `step_time()`：
  - `:80-82` 越界分支里的 `bump.emit(index)` ⇒ 改成发一个**越界**信号（名字自定，如 `signal out_of_range(index: int)`），或复用 phasing 机制里「没地方可去」的表现
  - `:84-88` 「目标帧该位置被固体重叠就推不过去」⇒ **改成：正常推进到目标帧 + 进入 phasing**（推进本身要成功）
  - `:90-92` 成功路径保留（`index = target; frame_changed.emit(index, current()); return true`）
- 建议新增：`var phasing := false`、`signal phasing_changed(on: bool)`、以及 `func enter_phasing()` / `func exit_phasing()`（名字自定）

**`scripts/main.gd`**
- `:56` `tl.bump.connect(_on_bump)` ⇒ 删；如需新信号在这里接
- `:317-322` `func _on_bump(_index: int)` ⇒ **整段删**（含 `hud.flash_bump()`、`world.kick_shake(2.2)`、`player.bump_kick = 4.8`）
- `:171-172` `world.set_player_state(..., player.bump_kick, ...)` ⇒ 去掉 bump_kick 参数
- `:333-334` `_refresh_all()` 里同理去掉

**`scripts/world_view.gd`**
- `:73` 注释「推不过去时的震动（§3.4 的『顶住了』反馈之一）」⇒ 删
- `:74-75` `var _shake` / `var _shake_dir` ⇒ 删（若确认无处使用）
- `:88` `var _p_bump := 0.0` ⇒ 删
- `:118-133` `set_player_state(...)` 的 `bump_kick` 参数 ⇒ 删（签名变了，`main.gd` 两处调用点都要跟着改）
- `:144-148` `func kick_shake(amount: float)` ⇒ 删
- `:151-155` `_process` 里 `_shake -= delta*22.0` ⇒ 删
- `:157-177` `_draw()` 里 `:161-163` `shake_off = _shake_dir * _shake` ⇒ 删
- **⚠️ `:167-169` 和 `:171-174` 是核心观感，一个字都不许动**：非时间轴模式的单遍绘制、时间轴模式的三遍色差绘制（红偏左/青偏右各 1px、alpha 0.45）

**`scripts/player.gd`**
- `:48` `var bump_kick := 0.0` ⇒ 删
- `:79` `var kick := facing * bump_kick * -1.0` ⇒ 删（连带 `:84` `_draw_hero(c, sheet, base + kick, bob)` 的 `kick` 参数）
- `:166-169` `_process` 里 `bump_kick = maxf(...)` ⇒ 删
- **新增**：虚化透明度字段（如 `var phasing := false`），在 `_draw_hero`（`:95-124`）与 `_draw_fallback`（`:128-146`）里把颜色 alpha 乘上去
- `:114-124` 时间轴残影那段（`draw_texture_rect_region(..., Color(1,1,1,a))`）是核心观感，**不许改**

**`scripts/hud.gd`**
- `:29` `var bump_flash := 0.0` ⇒ 删
- `:96-98` `func flash_bump()` ⇒ 删
- `:108-109` `_process` 里 `bump_flash` 衰减 ⇒ 删
- `:179-181` `_draw_timeline` 里那段 `draw_arc(... Color(0.95,0.45,0.35, bump_flash*0.8) ...)` ⇒ 删
- **替换**：加一个 phasing 提示（自定形式，比如时间轴刻度点变虚线/变色/加文字「虚化中 · A/D 内/外」）

### §3.2 第二件：实现 phasing 状态与独立位移

**核心：phasing 期间的位移路径必须绕过 `is_free()`。**

`scripts/timeline.gd` 里新增（名字可自定，但语义必须是这三步）：

```
# 正常走（现有 move_space 的逻辑）→ 不变
# phasing 走（新增）：直接改 char_pos，不查 is_free
func move_phasing(delta: Vector2) -> void:
    # 1. 沿 delta 方向按 8px 步进，逐段尝试
    # 2. 每步结束：if frames[index].is_free(char_pos): exit_phasing()
    # 3. 「往外走」按 §2.4 的三级规则找落点
```

**约束**：
- phasing 期间 `char_pos` **允许**落在 solid 里，`is_walkable()` 在 phasing 期间**必须**返回 true（否则玩家会被 `move_space` 弹回）
- `scripts/main.gd:175-192 _process_space()` 里要分派：phasing 中按 A/D 走 `move_phasing`，否则走 `move_space`
- **W/S 推时间在 phasing 期间仍可用**（文档说「不改正常时间轴 W/S 手感」）；但要注意推时间时若又落到新的固体重叠 ⇒ 保持在 phasing

### §3.3 第三件：phasing 的输入

**phasing 期间启用 A/D 做「往里走 / 往外走」。**

现状（已核）：`project.godot` 的 InputMap 里
- `move_up`＝W + 上箭头
- `move_down`＝S + 下箭头
- `move_left`＝A + 左箭头
- `move_right`＝D + 右箭头
- `shift_axis`＝Shift｜`inspect`＝E｜`toggle_fullscreen`＝F11｜`archive`＝I

⇒ **没有单独的 phasing 专用 action。** 两个方案：

**方案甲（推荐，不改 project.godot）**：在 phasing 状态下，把 `move_left`/`move_right` 解释成「往里走 / 往外走」。
- A（左）＝往里走（沿当前朝向的反方向深入）
- D（右）＝往外走
- 依据：`docs/house-spec.md:761` 原话「时间轴原本 A/D 无作用，仅在 phasing 状态下临时启用 A/D 做内/外位移」

**方案乙**：在 `project.godot` 新增 `phasing_in` / `phasing_out` 两个 action 绑定 A/D。
⚠️ **改 `project.godot` 要重启编辑器才生效**（`docs/PROMPT-overseer.md` §九 有这条纪律），对「拿任务书去新开会话跑」的用法不友好。
⇒ **默认用方案甲**；只有方案甲做不通才考虑方案乙，且必须在反馈文档里写明理由。

### §3.4 第四件：绘制通路（半透明 + 色差）

玩家绘制走这条路（已核）：
- `scripts/player.gd:68` `func draw_self(offset: Vector2 = Vector2.ZERO) -> void:`
- `scripts/world_view.gd:411-415` `func _draw_player(offset)` → `p.call("draw_self", offset)`
- `scripts/world_view.gd:454-457` `_draw_entry` 的 "player" 分支 → 同样 `p.call("draw_self", offset)`

⇒ **alpha 建议在 `player.gd` 内部处理**（改 `_draw_hero`/`_draw_fallback` 用的颜色 alpha），这样 `world_view.gd` 那边不用改绘制逻辑，只加一个「当前是否 phasing」的字段传递即可。

需要传的字段（照 `world_view.gd:118-133 set_player_state` 的现成通路扩一个参数即可）：
- `phasing: bool`

**色差**：文档建议「轻微色差」。最小实现＝虚化态整体偏冷或偏蓝一点、alpha 0.4。
**不许**改动 `world_view.gd:171-174` 的时间轴三遍色差绘制（那是另一个效果，会叠加成怪东西）。

### §3.5 第五件：`scripts/frame_data.gd`（**只读不改，除非确实需要**）

`scripts/frame_data.gd`（143 行）现有关键点：
- `:14` `const CHAR_RADIUS := 14.0`
- `:38` `if not bool(sd.get("solid", false)): continue` ⇒ **solid:false 的形状不进碰撞**
- `:124-131` `is_free(at)` 用 2*CHAR_RADIUS 的方形探针
- `:135-143` `hotspot_at(pos)`

**首选方案：不要改这个文件。** `is_free()` 已经够用了（判定 phasing 进出、找往外走的落点都用它）。

只有在下面这种情况才允许加一个**只读查询方法**（不许改 `is_free()` 的语义）：
- 需要区分「被手写 solid 形状挡住」和「被房子占地挡住」——例如想让虚化提示文案更精确。
⇒ 加的话只允许加 `func is_free_at_shape(at) -> bool` 这类**新方法**，不许动既有方法体。

### §3.6 第六件：测试改动

**`_mdtest/greybox_check.gd`（时间轴那一段，`:211-224`）**
- `:211` 注释「从 A1 一路推到 A5（起点在主路 (1400,1120)，A2-A5 该点为空地可站）」
- `:212-218` 起点 `(1400,1120)`、连推 10 次、期望 `TIME_FWD_REACHED=[1,2,3,4]`
- `:222` `TIME_BACK_FROM_A1`（期望 false）——这是**越界**，不是被顶住，**期望值不变**
- `:224` `TIME_FWD_FROM_A5`（期望 false）——同上，**期望值不变**

⇒ **关键**：`:222`/`:224` 测的是「越界推不动」，**跟 phasing 无关，期望值不许改**。
`:218` 的 `TIME_FWD_REACHED` 期望值 `[1,2,3,4]` —— 旧行为下这个起点是空地可站 ⇒ 行为不变，**期望值原则上也不该变**。
**但**：旧行为下「推不动」会 `return false`，新行为下「推得动但进 phasing」会 `return true`。所以 `reached` 数组内容可能变化。
⇒ **做法**：先跑一遍看新值是多少，再决定断言怎么写。**如果新值不是 `[1,2,3,4]`，不要硬改断言去凑**，而是：
1. 确认起点 `(1400,1120)` 在 A2–A5 各帧是否真的自由（用 `frames[i].is_free()` 打印）
2. 如果它其实在某帧被挡 ⇒ 把断言改成明确的语义（例如「推到 A5 后应处于 phasing 状态」），并在反馈文档里写清为什么改
3. **不许**为了让测试变绿而删掉断言

**`_mdtest/greybox_shot.gd:42-53`**（撞墙截图）
- `:46` `main._on_bump(0)` —— `_on_bump` 被删了 ⇒ 这行会崩
- `:52` 存 `bump.png`、`:53` `print("SHOT bump")`
⇒ **改成虚化截图**：构造一个 phasing 状态（把玩家挪到已知会被挡的坐标、推一帧），然后存 `phasing.png`，打印改成 `SHOT phasing`。

**新建 `_mdtest/phasing_check.gd`**（本线专属，必须写全）：
至少断言这几条（自己用 headless 跑，不要只在文档里写）：

| 编号 | 断言 |
|---|---|
| P1 | 正常位置推时间（该点自由）⇒ **不进 phasing**，`tl.phasing == false` |
| P2 | 已被固体重叠的位置推时间 ⇒ **进 phasing**，`tl.phasing == true`，且**时代确实前进了**（`tl.index` 变了） |
| P3 | phasing 状态下 `tl.is_walkable(tl.char_pos)` 为 **true**（不被弹回） |
| P4 | phasing 状态下调用 `move_phasing` 能改变 `char_pos`（不卡死） |
| P5 | 从 phasing 往外走到自由点后 ⇒ 自动退出 phasing，`tl.phasing == false` |
| P6 | phasing 状态下**不会**触发 bump（bump 信号已不存在；断言代码里不应再有 `tl.bump`） |
| P7 | 越界推时间（`index==0` 往后推、`index==max` 往前推）⇒ 仍然返回 false，**时代不变** |

### §3.7 第七件：文档改写

**`docs/HANDOFF.md`**
- `:40` 特性表那行「推不过去的『顶住了』（顿帧/震屏/红环，不弹回）」⇒ **删掉或改写成虚化口径**
- `:239-249` §3.4「如果目标帧里，角色的碰撞盒和固体重叠 → 卡住，推不过去」⇒ **整节改写**为虚化口径：
  - 推时间落进固体重叠 ⇒ 时代照常推进，主角进入虚化
  - 虚化期间 A/D 往里/往外走，走到自由面自动恢复
  - 引 `docs/house-spec.md` §8.3
- `:244`「已实现（scripts/timeline.gd:78 step_time() + main.gd:171 _on_bump()）」⇒ 改成新实现的行号
- `:249`「所以『在二楼推时间、回到只有一层的过去、人落到屋顶上』不会发生（会被顶住）」⇒ **改写**（这句话的前提是顶住；新机制下会进入虚化）
- `:760` 未做清单「主角虚化：与 NPC 重叠时半透明＋轻微色差（纯视觉，不影响任何判定）」—— **这条是另一回事**（NPC 重叠），**保留**，但可以补一句「卡墙虚化是另一套机制，见 §3.4」

**`docs/house-spec.md`**
- `:216` 表格「时间轴」行「目标帧的墙若压在玩家当前位置上，则推不过去（『顶住了』）」⇒ 改写为虚化口径
- `:230`（同一节附近）⇒ 同步
- `:741` §8 开头「代码现状仍是纯 2D……推时间会被目标帧 solid『顶住』」⇒ 改写
- `:757-771` §8.3「**卡墙虚化 = 主题机制，不是穿帮**」⇒ 标题后加一行「**2026-11-26 已实现（见 `scripts/timeline.gd` phasing 状态）**」
- `:770`「排期：跟 8.1 方案 C 同期实现，不要单独提前」⇒ 改成本线已单独实现 phasing 的说明
- `:776` §8.4 排序「放大地图 + 室内可见 → 楼层方案 C + phasing 虚化 → 日记渲染 → Web 导出」⇒ 更新为当前实际进度
- **⚠️ 不许改** `:743-749` §8.1 方案 C 本身（表面高度快照）—— 本线**不做**楼层

**`docs/PROMPT-overseer.md` 与 `docs/待解决事项.md`** —— **本线不要改**（由总策划回写）。

### §3.8 本线**明确不做**的事（写清楚，免得跑偏）

1. **不做楼层方案 C**（`docs/house-spec.md:743-749`）—— 那是 surface 高度数据，本线只做 phasing。
   🔴 用户 2026-11-26 已明确：「**不做楼层了，时间不够了。**」⇒ 不许在本线上"顺手做一点楼层"，
   也不许把 phasing 做成依赖 surface 高度的实现（phasing 只用现有 `is_free()` 的 2D 判定 + 独立位移路径）。
2. **不做二楼/屋顶线索**（`docs/house-spec.md:751` §8.2）—— 用户已定「排期待定，不一定有时间做」
3. **不改** `data/frames.json`（不新增任何 shape 类型、不加 surface 字段）
4. **不改** `scripts/house_shape.gd`、不碰证物系统
5. **不做** NPC 对白/旁白/双日记/归档表（那是 L15/L16 两条线）
6. **不碰** `scripts/world_view.gd:167-174` 的时间轴三遍色差绘制
7. **不删** `docs/HANDOFF.md:760` 那条 NPC 重叠虚化

---

## §4 验收

### §4.1 几何/行为自检（**在 `_mdtest/phasing_check.gd` 里断言，不许只在文档里写**）

- P1–P7 七条全过（见 §3.6 的表）
- 回归后 `_mdtest/greybox_check.gd` 的 `TIME_FWD_REACHED` 新值必须与反馈文档里写的一致
- `TIME_BACK_FROM_A1=false`、`TIME_FWD_FROM_A5=false`（越界语义不变）

### §4.2 七套回归

七套全跑，**全部绿**。把改动前后的关键输出对照写进反馈文档：
- `REACH_MAP`（`standable` / `to_a5` / `blocked_at_step` / `band_total` / `band_full` / `band_ratio` / `ratio`）
  - **改动前基线**：`{standable:15104, to_a5:12863, blocked_at_step:[144,191,722,1184], band_total:298, band_full:261, band_ratio:"88%", ratio:"85%"}`
  - ⚠️ **预期会变**：旧的 `blocked_at_step` 记的是「推不过去被顶住」的步数，新机制下推得动 ⇒ 这一项必然变化。**要报告变化并解释，不要为了对上基线而改逻辑。**
- `A1_WELL_FREE=false`（井仍挡路，这一项是**空间轴**的可站判定，不是时间轴，**不该变**）
- `WALL_BLOCKED=true`、`WALL_STOP_Y` 仍在 800~816（**空间轴**撞墙，不该变）
- `TIME_FWD_REACHED`（会变，见 §3.6）
- `UNEXPLAINED_BLOCKS=0`、`REACH_OK=true`（不变）
- 其余五套（camera/hud_layout/asset_draw/sort/evidence_archive/display）输出应**逐行不变**。变了要查清原因。

### §4.3 实机验证（**沙箱里做不了窗口，必须在真机做**）

沙箱跑 headless 出不了窗口 ⇒ 截图类验证要在真机跑。清单：

1. 启动游戏 → SHIFT 切到时间轴
2. 站在一个「推到下一帧会被房子占住」的点（`_mdtest/phasing_check.gd` 里能打印出这样的坐标）→ 推时间
   ⇒ 期望：**时代推进了**、主角变半透明、**没有**顿帧/震屏/红环、HUD 出现虚化提示
3. 按 D（往外走）⇒ 主角走出实体、**自动恢复不透明**
4. 再推一次到会挡住的位置 ⇒ 这次按 A（往里走）⇒ 能往建筑内部走一步
5. **走不出来也不会卡死**（回退规则生效）
6. 正常走路（空间轴）手感不受影响
7. 推时间时**越界**（A1 往后推 / A5 往前推）仍然推不动，且**不是**虚化（是越界提示）

### §4.4 交付物检查清单

- [ ] `scripts/timeline.gd` 里 grep `bump` **零命中**
- [ ] `scripts/main.gd` 里 grep `bump` **零命中**
- [ ] `scripts/player.gd` 里 grep `bump` **零命中**
- [ ] `scripts/hud.gd` 里 grep `bump` **零命中**
- [ ] `scripts/world_view.gd` 里 grep `bump`/`_shake`/`kick_shake` **零命中**
- [ ] `_mdtest/` 里 grep `bump` **零命中**
- [ ] `docs/HANDOFF.md` 与 `docs/house-spec.md` 里 grep `顶住` **零命中**（历史留档段落如注明「旧口径已作废」可保留，但正文口径必须改干净）
- [ ] `_mdtest/phasing_check.gd` 存在且七套回归全绿
- [ ] `docs/FEEDBACK-phasing-exec.md` ≤120 行

### §4.5 空气墙一致性核对（**用户 2026-11-26 口径的落地验收**）

本线**不负责**修地图，但**必须报告** phasing 触发面是不是被地图差异撑起来的。

口径（照抄 A4 重排线，别自己另编）：**空气墙 ＝ 房屋 `lot` 外框 ∪ 山体多边形**；
路/田/井/树/内岛/环道都是 `solid:false`，**不算**空气墙。

要求：

1. 在 `_mdtest/phasing_check.gd` 里加一条断言：**相邻两帧之间**，
   「上一帧可站 ∧ 目标帧同坐标是实体」的格子数 —— 报告这个数在 A1→A2 / A2→A3 / A3→A4 / A4→A5 各是多少。
2. 若 A4 重排线已落地（HEAD 里 `a4_2001` 的形状已是新布局），
   **A4→A5 的这个数必须接近 0**（A4 重排线目标：两个方向的触发格数都是 0，IoU 100%）。
   数字不为 0 ⇒ **写进反馈文档报告**，但**不要在本线改 `data/frames.json`**（那是地图线的事）。
3. 反馈文档里必须有一句结论：**「玩家在正常游玩（空气墙对齐的两帧之间）不会触发虚化」** 或
   「**仍有 N 格会触发，原因在 A1–A3 尚未重排（地图线待办）**」。不许含糊。

---

## §5 收工

### §5.1 精确 add（**绝不 `git add -A`**）

```
git add scripts/timeline.gd scripts/main.gd scripts/player.gd scripts/hud.gd scripts/world_view.gd
git add _mdtest/phasing_check.gd _mdtest/greybox_check.gd _mdtest/greybox_shot.gd
git add docs/HANDOFF.md docs/house-spec.md docs/FEEDBACK-phasing-exec.md
```

（`scripts/frame_data.gd`、`project.godot` **只在真改了**时才加。）

提交前 `git diff --stat` 逐个确认。

### §5.2 三段 commit

```
① git commit -m "feat(time): 推时间落进固体重叠时进入 phasing 虚化，删掉「顶住了」"
   （scripts/timeline.gd scripts/main.gd scripts/player.gd scripts/hud.gd scripts/world_view.gd
    + _mdtest/phasing_check.gd + _mdtest/greybox_check.gd + _mdtest/greybox_shot.gd）

② git commit -m "docs: 删掉「顶住了」口径，改写为卡墙虚化（house-spec §8.3 已实现）"
   （docs/HANDOFF.md docs/house-spec.md）

③ git commit -m "docs: phasing 执行反馈"
   （docs/FEEDBACK-phasing-exec.md）
```

### §5.3 反馈文档 `docs/FEEDBACK-phasing-exec.md`（≤120 行）必须包含

1. 一句话结论（做完了 / 做了一半 / 卡住了）
2. **§3.1 七件必改清单的逐条完成情况**（做了什么、改在哪些行）
3. phasing 的完整生命周期实现说明（触发条件、进入、往外走的落点规则、退出）
4. **实测数据**：
   - `_mdtest/phasing_check.gd` 的 P1–P7 逐条结果
   - 七套回归的输出对照（尤其 `REACH_MAP`、`TIME_FWD_REACHED` 的变化与解释）
   - 越界推时间的实测结果
5. **实机验证结果**（§4.3 七条逐条：做了 / 没做 / 为什么做不了）
6. **已知缺口与取舍**（尤其：phasing 没有楼层方案 C 的 surface 数据，所以「往外走」只能回到 2D 自由面）
7. **对 `docs/house-spec.md` §8.3/§8.4 的影响**（哪些行改了、为什么）
8. 如果用了 §3.3 方案乙（改 project.godot），说明为什么方案甲做不通

---

## §6 边界提醒

1. **只精确 add 自己的文件**；美术线那 11 张 `_ref/art/*.png` 和用户删的 `美术资产/**` 一个都不许碰
2. **不许改** `data/frames.json`、`_ref/houses/houses_data.json`、`scripts/house_shape.gd`、证物三件套（`evidence_store.gd`/`evidence_archive.gd`/`frame_data.gd` 的既有方法）
3. **不许改** `_mdtest/` 里除 `greybox_check.gd`、`greybox_shot.gd` 之外的五套断言
4. **不许改** `scripts/world_view.gd:167-174` 的时间轴三遍色差绘制、`:419-457` `_draw_entry` 的既有分支顺序
5. **不许改** `scripts/player.gd:114-124` 的时间轴残影绘制
6. **不许**为了让 `TIME_FWD_REACHED` 变绿而删断言或改基线值
7. 本线**不改**叙事文档（`docs/story.md`、`docs/npc.md`）
8. 本线**不碰** `docs/PROMPT-overseer.md`、`docs/待解决事项.md`（总策划回写）
9. 落盘后 python 扫一遍 `'\ufffd'`（中文乱码检查）—— patch 脚本写中文长串容易出替换字符
10. 改 `project.godot` 需重启编辑器才生效 ⇒ 默认别改

---

## §附 依据

| 文件 | 位置 | 作用 |
|---|---|---|
| `docs/house-spec.md` | `:739-784` §8 | 楼层与穿墙的设计决议 + 排期；§8.3 = 虚化的权威出处 |
| `docs/house-spec.md` | `:757-771` §8.3 | phasing 触发条件、视觉约定、⚠️「phasing 期间必须绕过 `is_free()`」 |
| `docs/house-spec.md` | `:765-769` | phasing 期间的正确位移做法 |
| `docs/house-spec.md` | `:770` | 排期说明（本线单独实现 phasing 的取舍依据） |
| `docs/house-spec.md` | `:776` §8.4 | 排序表（放大地图 → 楼层方案C+phasing → 日记渲染 → Web 导出） |
| `docs/HANDOFF.md` | `:233-251` §3.4 | 旧「顶住了」口径的权威出处（要改写） |
| `docs/HANDOFF.md` | `:760` | NPC 重叠虚化（另一回事，保留） |
| `docs/PROMPT-overseer.md` | `:156` | 写者锁：`scripts/world_view.gd` 归属 L2 ⇒ 与 L8 串行 |
| `docs/PROMPT-overseer.md` | `:237-252` | 任务书骨架 |
| `docs/PROMPT-overseer.md` | §九 | 跑回归姿势、改 project.godot 需重启编辑器 |
| `scripts/timeline.gd` | `:78-92` | 旧 bump 实现（要改） |
| `scripts/main.gd` | `:56`、`:171-172`、`:317-322`、`:333-334` | 旧 bump 接线（要改） |
| `scripts/player.gd` | `:48`、`:68-91`、`:79`、`:166-169` | 旧 bump_kick（要改） |
| `scripts/hud.gd` | `:29`、`:96-98`、`:108-109`、`:179-181` | 旧 bump 红环（要改） |
| `scripts/world_view.gd` | `:73-75`、`:88`、`:118-133`、`:144-155`、`:157-177` | 旧震屏（要改；`:167-174` 禁改） |
| `scripts/frame_data.gd` | `:14`、`:38`、`:124-131`、`:135-143` | `CHAR_RADIUS`、solid 语义、`is_free`、`hotspot_at` |
| `_mdtest/greybox_check.gd` | `:211-224` | 时间轴断言（要改） |
| `_mdtest/greybox_shot.gd` | `:42-53` | 撞墙截图（要改） |
| `lab/_probe_push_trap.gd` | — | 「推不动」的分布实测（15104 可站 / 1399 被挡） |
| `lab/_probe_step_block.gd` | — | 每对时代的顶住比例（a4→a5 最高 8%） |
| `lab/_probe_road_push.gd` | — | 主路往东连续可推 118 格 |
| `docs/PROMPT-overseer.md` §六 | — | 「顶住了」是总策划补的、用户未批准 —— 本线的授权依据 |
