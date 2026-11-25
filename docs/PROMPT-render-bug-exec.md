# 新会话提示词：渲染缺陷调查与修复执行人 ——「人站在墙上 / 门能穿 / A4 门口色块乱」
> 线索号 **L9**。上一条同族线是 `docs/PROMPT-render-fix-exec.md`（L2，已交付验收）——**它不适用**，请以本文件为准。
> 本线是**调查 + 修复**，不是重新设计。你要先拿出证据、再动代码；能不改数据就不改数据。

---

## §0 开工前（照做，别跳）

| 项 | 值 |
|---|---|
| 仓库根 | `D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift` |
| Godot | `D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`（不在 PATH） |
| HEAD 要求 | ≥ `92078cb`（`git log -1` 确认，2026-11-25 11:05 的进度快照提交）。若更低，先 `git status` 看现场再定要不要 pull |
| 你能改的文件 | `scripts/world_view.gd`、`scripts/house_shape.gd`、`scripts/frame_data.gd`（三者都在白名单内，见 §1.1） |
| 你**不能**碰 | `data/frames.json`（L1 独占）、`_ref/houses/houses_data.json`（L3 单写者）、`scripts/main.gd`、`scripts/evidence_*.gd`、`scripts/asset_draw.gd`（L8 独占）、`assets/**`、`_ref/art/**`、`_mdtest/**`（**测试文件一律不要改**）、`docs/PROMPT-overseer.md` |
| pwsh | 本机 `pwsh` 调「写文件」类命令要带 `sandbox_permissions: "danger-full-access"`（工作区 ACL），否则会报 `windows-acl workspace grant failed: Win32Error 5` |

### §0.0.5 这条线现在的状态（总策划 2026-11-25 复核）

- 🔴 **本线从未真正开工**：`docs/FEEDBACK-render-bug-exec.md` 不存在；`scripts/world_view.gd` 自 `cc19b4c`（2026-11-24 17:26）起没动过 ⇒ **工作区没有任何在途改动**，你是这条线的第一个执行者。
- ✅ **任务书里的行号引用已由总策划逐条复核过（2026-11-25 11:10）**，全部仍然准确：
  - `scripts/world_view.gd:455-467`＝排序键约定段（「玩家 position.y + RADIUS * 0.7」／「墙 该行格子的南沿」都在里面）；
  - `:537`＝玩家 `sort_y: player_pos.y + 14.0 * 0.7`；`:492`＝墙 `sort_y: hpos.y + (row+1) * HouseShape.TILE`；
  - `:847-848`＝墙顶面抬高 `hh` 的 `draw_rect`；`:805`＝「北/西墙 h=TILE（32px 全高），东/南墙 h=TILE/2（16px 半高）」；
  - `:426-427`＝有 base 图就 `return`（引擎不画墙）；`:431-435`＝门分支同理；
  - `:604-608`＝`FAMILY` 映射（**只到 a1–a3 的 12 栋** ⇒ A4/A5 六栋查不到屋体图）；
  - `scripts/house_shape.gd:157-219`＝`grid_of()`；`:368-369`＝「solid_rects() 只返回墙 → 碰撞用；door_rects() 只画颜色、不参与碰撞」；
  - `scripts/player.gd:17`＝`const RADIUS := 14.0`；`:103-106`＝`_draw_hero` 脚底对齐 `base.y + RADIUS - HERO_FRAME - bob`。
- ⚠️ **§1.3 表格里 `WALL_STOP_Y` / `DOOR_PASSABLE` 的行号写法有误**（真值在 `greybox_check.gd` 里）：

| 断言 | 任务书原写法 | 实际位置 | 内容 |
|---|---|---|---|
| `DOOR_PASSABLE` | `greybox_check.gd:189` | **`greybox_check.gd:182-189`**（用例块 `:182`，断言在 `:189`） | 4 个院门点必须可站：`(1456,784)` / `(336,976)` / `(1872,1456)` / `(2512,1104)` |
| `WALL_STOP_Y` | `greybox_check.gd:208-209` | **`greybox_check.gd:202-209`**（用例块 `:202`，断言在 `:208-209`） | 期望 **800~816**（撞磨坊南墙，从 `(1248,904)` 上撞） |
| `TIME_FWD_REACHED` | `greybox_check.gd:218` | `:211-218` | 期望 `[1,2,3,4]`（起点 `(1400,1120)`） |
| `A1_WELL_FREE` | `greybox_check.gd:233` | `:226-233`（断言在 `:233`） | 期望 **false**（`(1360,860)`） |
| `A3_OLD_WELL_UNDER_MILL` | `greybox_check.gd:170` | `:170` | 期望 `true` |
| `UNEXPLAINED_BLOCKS=0` | `greybox_check.gd:255` | `:251-261`（断言在 `:255`） | — |

  ⇒ 定位时按「用例块起始行 → 断言行」两处一起看，别只按断言行号跳。
- ⚠️ **`scripts/world_view.gd` 最近一次改动是 `cc19b4c`（L2 交付）**，所以 §2 里所有「总策划初步定位」都是在那个版本上做的；若你改到 `world_view.gd` 的别处，**别回退 L2 的成果**（色块树冠不上抬／圆深度键分立着-贴地／井恒可见的补画方案，见 §4 末尾）。

### §0.1 跑回归的正确姿势（照抄，别自己发挥）

```powershell
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . -s res://_mdtest/sort_check.gd 2>&1 | Select-Object -Last 45
```

- ❌ `cmd /c "D:\steam\...\godot..."` —— 路径有空格会被截断，报 `'D:\steam\steamapps\common\Godot' is not recognized`。
- ❌ `> out.txt` 重定向 —— 会产出 0 字节文件。
- ✅ 上面这种**内联管道**写法。
- **看关键字，不看退出码**。沙箱固有噪声：`ERROR: Failed to open 'user://logs/...'`、`Failed to open log file for writing: user://logs/godot.log`、`Failed to read the root certificate store.`、`[exit code: 1]`。
- 七套脚本：`greybox_check` / `camera_check` / `display_check` / `hud_layout_check` / `asset_draw_check` / `sort_check` / `evidence_archive_check`。

### §0.2 六个必须知道的坑

1. **`scripts/world_view.gd:455-467` 有一段明文约定**：排序键统一＝「精灵底边（脚那条线）」，玩家 `position.y + RADIUS*0.7`、墙＝该行格子的南沿、屋顶＝wings 南沿、家具＝占地 rect 底边。同一段写着 **⚠ 排序链「只加不减」** —— L2 的「井恒可见 + 不挡玩家」是用**补画**实现的，**故意没动 sort_y**，因为一改排序键 `_mdtest/sort_check.gd:250` 和 `_mdtest/asset_draw_check.gd:287` 的「sort_y 单调」断言就会红。你改排序键前必须先想清楚这两条断言。
2. **A1–A3 有美术 base 图，A4/A5 没有**。`assets/village/houses/` 实际只有 lu(5)/mill(6)/shen(6)/zhou(6) 四族 PNG，全是 A1/A2/A3 的 base/roof（`scripts/world_view.gd:604-608` 的 `FAMILY` 映射只列了 12 栋）。`scripts/world_view.gd:426-427` 的 `"walls"` 分支：有 base 图就**引擎不再画墙**；`:431-435` 的 `"door"` 分支：有图就不画门色块。⇒ **A4/A5 六栋走的是引擎色块墙/门画法，A1–A3 走美术图**。这解释了为什么玩家只在 A4/A5 看到「门口色块乱」——同一个渲染 bug 在 A1–A3 被美术图遮住了，不是 A1–A3 没有 bug。
3. **`scripts/house_shape.gd:368-369` 的注释是故意写的**：「a) `solid_rects()` 只返回墙（'#'）→ 碰撞用；b) `door_rects()` 返回门洞格（'D'/'G'）→ **只画颜色、不参与碰撞**」。所以「人能穿门」不是漏写一行，是**当初的设计选择**。你可以改这个选择，但要在报告里说清为什么改、代价是什么。
4. **门洞色块与同排墙的 `sort_y` 完全相同**（都是 `hpos.y + (row+1)*TILE`），同深度靠 `seq` 决定先后：墙条目先 append（`scripts/world_view.gd:491`），门条目后 append（`:498`）⇒ **门色块画在墙之上**，观感像「门压在墙顶面上」。
5. **`grid_of()` 的判定顺序是 `G(院门) > D(房门) > partitions/is_wall('#') > interior('.') > ' '`**（`scripts/house_shape.gd:157-219`）。**门格优先于隔断** ⇒ 门开在隔断上时，那一格的隔断被门替换 ⇒ **隔断在这一格被从两侧切断**。
6. **headless 截图这条路上「实例化 main.tscn + 相机」会卡死**。总策划已经踩过：仿 `lab/_render_fix_shot.gd` 写了个 `lab/_render_bug_shot.gd`，`godot --headless --path . -s res://lab/_render_bug_shot.gd` 后台跑 12 分钟零输出（连第一行 print 都没有），进程 PID 37040 卡住，只能强杀。⇒ **取证优先走几何/网格/python 复刻**（§2 的做法就是这条路）；截图是加分项，不是必需项。若一定要截，先写一个**不实例化主场景**的最小脚本试水，并把超时设为 3 分钟，超时就放弃截图、继续用几何证据。

---

## §1 背景与白名单

### §1.1 你能改什么

| 文件 | 你能做什么 |
|---|---|
| `scripts/world_view.gd` | 排序键、墙体/门的绘制、伪 3D 高度、补画逻辑 |
| `scripts/house_shape.gd` | 网格生成（`grid_of`）、碰撞矩形（`solid_rects`）、门矩形（`door_rects`）、墙高分类（`_classify_walls`） |
| `scripts/frame_data.gd` | `is_free()` 的占位判定、house 的 solid/hotspot 装配 |

### §1.2 你不能改什么（越界＝任务失败）

- **`data/frames.json`** —— L1 独占。任何「A4 的门数据不对」类修改都**只能报告、不能改**。
- **`_ref/houses/houses_data.json`** —— L3 单写者文件。本线若证明数据必须改，**写进报告交总策划**，不要自己动。
- **`_mdtest/**`** —— 测试文件是公共依赖，**任何情况下都不许改**。需要新断言就在报告里写「建议新增断言：……」，由总策划决定另开一条线。
- `scripts/main.gd`、`scripts/evidence_*.gd`、`scripts/asset_draw.gd`、`assets/**`、`_ref/art/**`、`docs/PROMPT-overseer.md`。

### §1.3 现有断言（**这些是基线，不是目标**；改坏任何一条＝任务失败）

| 断言 | 位置 | 内容 |
|---|---|---|
| 排序结果按 sort_y 递增 | `_mdtest/sort_check.gd:250`（用例区 `:242-250`） | 只覆盖 A1–A3 的房子 |
| 玩家在家具南 → 玩家后画（挡住家具） | `_mdtest/sort_check.gd:240` | |
| 墙按行拆开（N 行） | `_mdtest/sort_check.gd:261` | |
| 前景层 sort_y 单调不减 | `_mdtest/asset_draw_check.gd:287` | |
| 玩家在 lu_house wings 内 | `_mdtest/asset_draw_check.gd:289-290`（`_player_inside`） | |
| `DOOR_PASSABLE` | `_mdtest/greybox_check.gd:189` | **4 个院门点必须可站**：`Vector2(1456,784)` / `(336,976)` / `(1872,1456)` / `(2512,1104)` |
| `WALL_STOP_Y` | `_mdtest/greybox_check.gd:208-209` | 期望 **800~816**（撞磨坊南墙） |
| `TIME_FWD_REACHED=[1,2,3,4]` | `_mdtest/greybox_check.gd:218` | |
| `A1_WELL_FREE` | `_mdtest/greybox_check.gd:233` | 期望 **false** |
| `UNEXPLAINED_BLOCKS=0` | `_mdtest/greybox_check.gd:255` | |
| `A3_OLD_WELL_UNDER_MILL=true` | `_mdtest/greybox_check.gd:170` | |

> 🔴 `DOOR_PASSABLE` 与 §2 的问题 3 **直接冲突**：如果门洞变成可碰撞的墙格，那 4 个院门点就必须仍然可站；如果你把「门洞＝可通行的洞」改成「门洞＝墙上画个门但仍然挡人」，那玩家就永远进不了屋。**这两条必须同时成立**，想清楚再动。

---

## §2 三条问题的已知线索（这是总策划已经查到的**初步定位**，你要复核 + 补完）

> 总策划的取证方式：**python 复刻 `grid_of()`** 把每栋房子的网格打印出来 + 读源码。**你必须自己复核**，别直接抄结论。

### §2.1 问题 1：人站在墙的北面，却画在墙上面

**玩家实机原话**：「明明人是站在墙的北面（应该被墙挡住的），但出现了人站在墙上的情况」。

**已知机制**：
- 玩家的排序键 = `player_pos.y + 14.0 * 0.7`（`scripts/world_view.gd:537`）。14 是 `scripts/player.gd:17` 的 `RADIUS`；0.7 是历史遗留下来的一把尺子 ⇒ **脚线被放在身体中心偏下 9.8px 的位置**。
- 墙的排序键 = **墙格整行的南沿** = `hpos.y + (row+1) * TILE`（`scripts/world_view.gd:492`）⇒ 比该行墙格的**顶沿低了一整格（32px）**。
- ⇒ 玩家站在墙**北侧**（y 更小）时，只要 `player_pos.y + 9.8` 仍大于墙行南沿，排序上玩家就排在墙之后 ⇒ **画在墙之上**。
- 视觉上墙的顶面被**抬高 h**（`scripts/world_view.gd:847-848`，`draw_rect(bx, by-hh, ...)`），北/西墙 h=32 全高、东/南墙 h=16 半高（`:805`）⇒ 墙比碰撞盒高一截，**放大**了错位观感。
- 玩家的身体框是 32×32、脚底对齐 `position.y + RADIUS`（`scripts/player.gd:103-106` 的 `_draw_hero`：`base.y + RADIUS - HERO_FRAME`）。

**你要回答的问题**：
1. 这个错位在 **A1–A3（美术图路径）** 里为什么**看不见**？是 base 图把墙画得低、还是碰撞盒与美术图根本对不齐？给出证据。
2. **修法候选**（你可以提别的，但必须评估这两条断言）：
   - ① 玩家键改用真脚底 `position.y + RADIUS`（`scripts/player.gd` 已有 `RADIUS = 14`）。语义最对，但**会改动 sort_y 数值** ⇒ 两处单调断言是否还成立？
   - ② 墙键从「行南沿」改成「行顶沿」`hpos.y + row*TILE`。视觉上更早被遮挡，但会改变墙/家具/玩家的相对前后关系。
   - ③ 几何判定：玩家在墙北侧时强制被墙遮挡（按玩家 x 是否落在墙格 x 范围内判断），不动通用排序键。
   - ④ 不改排序，只调视觉：墙顶面不抬高 / 加投影 / 加轮廓。
3. **每条候选都要给出**：会不会破坏 `sort_check.gd:250`、`asset_draw_check.gd:287`、`greybox_check.gd:208-209`（`WALL_STOP_Y` 800~816）、`:189`（`DOOR_PASSABLE`）、`:240`（玩家挡家具）。**逐条实测，不要推测。**

### §2.2 问题 2：沈家 A4 进门处的色块渲染不对

**已知机制（数据层面）**：
- `shen_a4` 的 12 扇门**全部落在内部隔断（partitions）上**，不是外墙：
  - `(14,10)` / `(22,10)` 在 partition `[11,10,25,10]` 上；
  - `(10,12)` / `(10,16)` / `(10,20)` / `(10,24)` 在 partition `[10,3,10,32]` 上；
  - `(26,*)` 在 partition `[26,3,26,32]` 上；
  - `(14,26)` / `(22,26)` 在 partition `[11,26,25,26]` 上。
- 因为 `grid_of()` 的判定顺序里 **D 优先于 partitions**（`scripts/house_shape.gd:157-219`），这些格子被渲染成 `'D'` ⇒ **隔断在这一格被门替换 ⇒ 隔断从两侧都被切断**。
- 实测网格行（python 复刻）：
  ```
  y=10  #.......####D#######D####......#
  y=12  #.......D...............D......#
  y=16  #.......D...#       #...D......#
  y=20  #.......D...#       #...D......#
  y=24  #.......D...............D......#
  y=26  #.......####D#######D####......#
  y=33  ##########################G###
  ```
  ⇒ 门格两侧是墙（`'#'`），门格本身是通道；一扇门把一整段隔断切成两截。

**🔴 但这不是 A4 的数据错误 —— 这是全项目通例**（总策划逐门实测）：
| 房子 | 门在隔断上的比例 |
|---|---|
| `shen_a1` | 3/3 |
| `market` | 3/3 |
| `shen_a2` | 5/6（只有 `(9,13)` 在外墙） |
| `shen_a3` | 7/10（`(3,11)`/`(19,11)`/`(13,11)` 在外墙） |
| `shen_a4` | **12/12（门最多 ⇒ 观感最乱）** |

**⇒ 你的定位方向不是「A4 数据写错了」，而是**：
1. **语义问题**：门应该开在**外墙**上（通向屋外的开口），而现在开在**内部隔断**上（通向屋内的开口）。隔断（partitions）是「屋里的隔墙」，在它上面开门洞，语义是「隔墙上有个洞」，但渲染出来的是「墙被切了一格、门色块浮在切口上」。
2. **渲染问题**：门色块是画在**地面层**的（`scripts/world_view.gd:496-504` 的 `sort_y` ＝ 同行南沿，与墙同深度），但墙顶面抬高 32/16px ⇒ 门色块永远落在墙的**脚下**，看着像「门被墙压住」或「门贴在地上的色块」。
3. **另外注意 `shen_a3` 的院门**：`gate (13,23)` 邻接**全是空格**（两侧没墙）⇒ 院门开在空地上，这也是渲染/数据语义的边角情况，可以一并报告。

**你要回答的问题**：
1. 「门开在隔断上」到底是**数据语义错**（改 `houses_data.json`，属 L3 文件域，**你只能报告**），还是**渲染错**（改 `house_shape.gd` / `world_view.gd`，**你可以改**）？给出你的判断和理由。
2. 门色块应该画在**哪一层**？地面层（同现在）、墙顶面高度、还是墙的南立面上？画在墙顶高度上会不会引入新的遮挡问题（门在前面的墙会不会被后面的门盖住）？
3. `grid_of()` 的判定顺序（`G > D > partitions > is_wall`）能不能调？调了会破坏什么？（提示：把 `partitions` 提到 `D` 前面 ⇒ 门格被隔断覆盖 ⇒ 门洞消失 ⇒ 那扇门就没有视觉了。）

### §2.3 问题 3：门可以站在门下面 / 人可以穿门

**玩家实机原话**：「门的色块的渲染逻辑也有问题，人可以出现在门下面，这点是不符合实际的」。

**已知机制（两条独立的事）**：
- **(a) 门洞完全不参与碰撞**：`scripts/house_shape.gd:224-238` 的 `solid_rects()` **只返回 `'#'` 格**；门洞是 `'D'`/`'G'`，**不在里面** ⇒ 玩家可以从门洞穿墙进屋。注释 `:368-369` 明写这是当年的设计选择（「只画颜色、不参与碰撞」）。
  - 碰撞判定链：`scripts/frame_data.gd:124-131` 的 `is_free(at)` 用玩家占位 `Rect2(at.x-CHAR_RADIUS, at.y-CHAR_RADIUS, 2R, 2R)`（**28×28 方块**）与所有 solid rect 求交；house 的 solid rect 由 `scripts/frame_data.gd:65` 调 `HouseShape.solid_rects(hdata, hpos)` 得到；`scripts/timeline.gd:97-101` 的 `is_walkable` ＝ 不越界 + `is_free`；`:105-119` 的 `move_space` 分轴推进（撞墙可以沿墙滑）。
  - ⇒ 「人出现在门下面」＝ 玩家占位方块与门洞格相交，但门洞不在 solid 里 ⇒ 判定为可站。
- **(b) 门色块与同排墙同深度、靠 `seq` 排在后面** ⇒ 门画在墙之上（见 §0.2 坑 4）。

**你要回答的问题**：
1. **门洞到底该不该挡人？** 三种可能，各给代价：
   - ① **门洞永远挡人**（门＝画在墙上的装饰，墙不开口）⇒ 玩家永远进不了屋 ⇒ 需确认游戏是否需要「进屋」（看 `docs/story.md` 与现有房间设计），且 `DOOR_PASSABLE`（`greybox_check.gd:189`）那 4 个院门点会怎样？
   - ② **门洞可通行，但通行口要在门的正下方**（即门洞格的**下半部分**是通道、上半部分是门扇；玩家能站在门口但不能站在门扇上）⇒ 需要玩家占位方块和门格做更细的判定。
   - ③ **门洞可通行，且视觉上画成「门框 + 门洞地面」**（不再用一块实心色块糊上去）⇒ 玩家可以走进去，但视觉上不像「站在门上」。
   - **你也可以提出第四种**，但必须回答「玩家站到门那个位置时，看到的是什么」。
2. 「人出现在门下面」的观感问题，**是碰撞问题还是绘制问题**？玩家说「不符合实际」——他期望的是「门洞那儿应该有一扇门，人不能站在门扇上，但可以站在门口」？还是「门应该只画门框，地是空的」？**从玩家的原话推断意图，别自作主张。**
3. 改完之后，`greybox_check.gd:189` 的 `DOOR_PASSABLE`（4 个院门点必须可站）、`:208-209` 的 `WALL_STOP_Y`（800~816）还成立吗？**实测给结论。**

---

## §3 调查与修复流程（照这个顺序走）

### §3.1 先复现（不许跳过）

1. 起一个**只读**的调查脚本（放 `lab/` 下，**不要放 `_mdtest/`**），用 python 或 GDScript 把每栋房子的 `grid_of()` 等价网格打印出来，把门格与 partition 格标出来，统计「门在隔断上」的比例。**你要自己跑一遍，确认 §2.2 的表**。
2. 用 python 复刻排序链：对每个「玩家站在墙北侧」的位置，算 `player_sort_y` 与墙的 `sort_y`，列出「会画在墙上」的具体位置清单（至少给出 A1 `shen_a1` 与 A4 `shen_a4` 各一组坐标）。
3. 算门洞与玩家占位方块（28×28）的相交情况，列出「人站在门上」的具体位置。

> 这些脚本可以留在 `lab/`（该目录未被 git 跟踪），**不要提交**。

### §3.2 再定方案，再动代码

- 每条改动都要在报告里写：**根因 → 改法 → 影响面 → 回归结果**。
- **优先顺序**：① 不改数据、不改排序键的视觉/几何修法 → ② 只改 `house_shape.gd` 的网格/碰撞生成 → ③ 改排序键（最后考虑，因为它牵着两条断言）。
- 任何需要改 `data/frames.json` 或 `_ref/houses/houses_data.json` 的方案，**不要动手**，写进报告的「建议交办」段。

### §3.3 验收口径（交卷时必须全绿）

- 七套回归全绿：`greybox` / `camera` / `display` / `hud_layout` / `asset_draw` / `sort` / `evidence_archive`，**每套都要贴出关键行**（例如 `SORT_CHECK_DONE fails=0`、`WORLD_OK/HOTSPOTS_OK/REACH_OK=true`、`EVIDENCE_OK`）。**看关键字不看退出码**（§0.1）。
- §1.3 的**每一条断言**都要单独确认它仍然成立（在报告里逐条打勾，不许写「应该没问题」）。
- 玩家三条原话逐条给「修前现象 → 修后现象」的**对照描述**（不需要截图；能截图更好，但按 §0.2 坑 6，超时就放弃截图、别卡死）。
- `_mdtest/**` **零改动**（`git diff --stat -- _mdtest` 必须为空）。
- `git diff --stat` 只应出现 §1.1 的三个文件（若你确实没改别的）。

### §3.4 收工

1. 精确 `git add`（**只 add 你改的那几个文件**，**绝不 `git add -A`** —— 工作区长期有别的线的东西：`_ref/art/A1..A4/*.png` 12 张美术线的改动、`美术资产/` 一批用户自己删的文件、若干未跟踪的 `docs/FEEDBACK-*`）。
2. commit 建议信息：`fix(render): 修复「人站在墙上 / 门可穿 / 门口色块错位」三条渲染缺陷`
3. 写 `docs/FEEDBACK-render-bug-exec.md`（**≤120 行**），结构：
   - §1 复现证据（表格：位置 → 现象 → 根因）
   - §2 改动清单（文件:行 → 改了什么 → 为什么）
   - §3 回归结果（七套的关键行 + §1.3 断言逐条打勾）
   - §4 建议交办（需要改 `data/frames.json` / `houses_data.json` 的部分，或建议新增的 `_mdtest` 断言）
   - §5 没做到的 / 取舍说明（尤其：截图为什么没交）
4. 把反馈文档的路径告诉我（总策划要审）。

---

## §4 边界与提醒

- **只改 §1.1 的三个文件**。任何时候想动第五个文件，先停下来写进报告。
- **不要为了让断言变绿而改断言。** 断言红了说明你的改动破坏了不变量 —— 回头改实现，不是改测试。
- **不要引入新依赖**，不要改 `project.godot`。
- 报告里要**明确区分**「我实测出来的」和「我推测的」。推测要标出来。
- 如果你发现 §2 的某条线索是**错的**，直接推翻它并给出新证据 —— 总策划的初步定位也可能错（L2 那次「地标文案 30 条 vs 28 条」就是总策划口径错、执行方对）。
- 遇到和 L2（`docs/PROMPT-render-fix-exec.md`）冲突的地方：**L2 已交付并验收**（commit `cc19b4c`），它的成果（色块树冠不上抬、圆深度键分立着/贴地、井恒可见的补画方案）**不要回退**。特别是 `:455-467` 那段「排序链只加不减」的约定 —— 它是为了保住两条断言而写的，你要改排序键就得同时说明怎么保住那两条断言。
