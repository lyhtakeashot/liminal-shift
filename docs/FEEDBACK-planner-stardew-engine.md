# 反馈文档 · 星露谷视觉机制执行线（引擎）致「项目总策划」会话

> 提交方：星露谷视觉机制执行线（引擎线，2026-11-22 16:10 交付）
> 接收方：项目总策划会话（负责统筹并行、划边界、验收、提交）
> 依据：`docs/PROMPT-stardew-engine-exec.md`（73 行）+ `docs/DECIDE-stardew-visual.md`（110 行）
> **本线已 commit**：`b6024dd feat: 星露谷视觉机制 - y-sort 遮挡 + 南墙半高（DECIDE D3/D4）`
> （6 files changed, 766 insertions(+), 120 deletions(-)）
> ⚠️ 例外说明：执行提示词 §4 写「本线不写文档」，本文件是用户 2026-11-22 16:09 追加要求
> 「写份反馈文档，我提交给项目总策划检查验收」才写的，**不在本线原定交付范围**，未 commit。

---

## 0. 一句话现状

**D8 顺序里的 ①② 两条（y-sort 遮挡 + 南墙半高）已全部做完并通过像素级验收**，
12 栋（A1–A3）全部生效，碰撞与数据层零改动；下一步 ③ 美术接入的**引擎侧消费点已就位**，
`_house_tex()` 接口原样保留、缺图降级仍可用。

---

## 1. 已交付（逐条对照 PROMPT §2）

### 1.1 八条画面/逻辑检查项 —— 全部通过（像素级实测，非目视估计）

| # | 检查项 | 结果 | 实测证据 |
|---|---|---|---|
| 1 | 玩家站房北 → 被房子/屋顶遮住（`z_index=10` 已删） | ✅ | 玩家置于 lu_house 北侧 y=750，采样点非玩家本体色 → 被屋顶盖住 |
| 2 | 玩家站房南 → 玩家挡住房子南立面 | ✅ | 玩家 y=1130（体 1116..1144）压住南墙立面 1104..1120，采样点 = 玩家本体色 |
| 3 | 家具后被家具挡 / 家具前挡住家具 | ✅ | 八仙桌北侧 y=900 → 采样点非本体色（被挡）；南侧 y=940 → 本体色（盖住桌） |
| 4 | 东/南墙半高 16px，北/西墙全高 32px | ✅ | 竖列像素探测（world_x=2464）：北墙顶面起 **736**（地面 768 − 32 = 全高）；南墙立面仅 **1088..1120**（16px = 半高） |
| 5 | 进屋 → 屋顶整块消失，无渐变 | ✅ | 屋内像素 ≠ roof 贴图 texel；屋外像素**完全等于** roof 贴图 texel(296,94)=`#af8a49` → 屋顶 1:1 贴图画在 (2304,736) |
| 6 | 时间轴推一年 → 整帧干净切换 | ✅ | root 子节点数 before=1 / after=1；无残影、无重复节点、无「房子呼吸」 |
| 7 | 缺美术图 → `_house_tex()` 静默回色块，游戏可跑 | ✅ | `_house_tex("zzz_no_such_house")` → `{base:null, roof:null}`，不抛错不刷 ERROR |
| 8 | 内外 1:1 与 AABB 碰撞未变，四套回归关键字全绿 | ✅ | `solid_rects()` 仍返回纯整格 `Rect2`；五套回归全绿（见 §3） |

**第 4 条的原始探测输出**（玩家在室内、屋顶已消失，竖列逐段取色）：

```
  world y  700..736  #6e7a4c   草地
  world y  736..928  #c9a878   墙顶 (WALL_TOP)      ← 北墙顶面从 736 起，高 32
  world y  928..960  #8c6b4a   墙南立面 (WALL_COLOR)
  world y  960..1088 #c9a878
  world y 1088..1120 #8c6b4a                        ← 南墙立面只有 16px
  world y 1120..1160 #3b3a2e   院子
```

### 1.2 改动清单（只动了 4 个 .gd + 1 个新测试）

| 文件 | 改动 | 关键位置 |
|---|---|---|
| `scripts/house_shape.gd` | 新增**渲染专用**墙向分类器 | `WALL_FULL/WALL_HALF`（:21-22）、`wall_render_cells()`（:221）、`_classify_walls()`（:245）、`_wall_class_direct()`（:301）、`_wall_class_inherit()`（:310） |
| `scripts/world_view.gd` | 单 `_draw()` 拆两层 + 排序循环 | `set_player_state()`（:105）、`set_player_ref()`（:124）、`_draw_back()`（:182）、`_draw_front()`（:238）、`_collect_front()`（:275）、`_roof_sort_y()`（:357）、`_draw_walls_row()`（:492）、`_draw_roof()`（:540） |
| `scripts/player.gd` | 删 `z_index=10`，绘制抽成 `draw_self()` | `draw_target`（:28）、`_draw()` 清空（:33）、`draw_self()`（:40） |
| `scripts/main.gd` | 把玩家状态喂给 world_view | `world.set_player_ref(player)`（:63）、`world.set_player_state(...)`（:115、:230） |
| `_mdtest/sort_check.gd`（新，264 行） | 本线自检 | 分类器 12 栋逐格 + 整格 AABB + y-sort 不变量 + `player.z_index==0` |

### 1.3 实现要点（供后续线参考，细节看代码注释）

**排序键 = 精灵底边（脚那条线），不是中心**（DECIDE D4 / house-spec §4.8.2）：

| 精灵 | sort_y |
|---|---|
| 玩家 | `position.y + RADIUS * 0.7`（RADIUS=14） |
| 树 / 井 | `center.y + radius * 0.7` |
| 家具 | 占地 `rect.end.y` |
| 墙（按行） | `hpos.y + (行号 + 1) * TILE` |
| 屋顶 | wings 南沿 `_roof_sort_y()` |

**墙必须按行拆开排序**（这条是本线实测踩出来的，PROMPT 里没写）：
一栋房子如果只当一个整体条目（sort_y = 屋体南沿），那么「玩家站在隔断南边」时，
整栋（含隔断）都排在玩家**后面** → 隔断错误地盖住明明站在它前面的玩家。
拆成「一行墙 = 一个条目」之后，玩家能和每一行墙各自比深度。
→ **文件头 `scripts/world_view.gd:27-31` 写了这段解释，避免后来人改回整栋排序。**

**墙向分类器判据**（观察者在东南方向）：
墙的**室内侧**朝南/朝东 → 内侧面朝向观察者 → 看得见 → 画全高（32px）；
墙的室内侧朝北/朝西 → 只看得到墙顶 → 画矮墙（16px）。
即 **北墙/西墙全高，东墙/南墙半高**。
- 墙角格（四邻都不是室内）→ 继承邻格，**「有全高就全高」**（隔断南端头朝着观察者 → 全高），最多 6 轮传播。
- `demolished` 拆墙表里的格 → 强制半高（数据说墙已拆，只剩墙根）。
- 仍判不出的 → 按全高（保守，不会把墙画成半高导致穿帮）。
- ⚠️ **只影响「画多高」，绝不影响碰撞**：`solid_rects()`（`house_shape.gd:185`）返回结构与内容一字未改，碰撞恒为整格 AABB。
- 分类器不假设矩形：任意 wings 形状、任意 `partitions`、`demolished` 都吃得住。

---

## 2. 与其他线的边界自查

### 2.1 我没碰的（承诺过不碰，实测没碰）

| 约束 | 自查结果 |
|---|---|
| 不写 `_ref/houses/houses_data.json` | ✅ 未改（`git show --stat HEAD` 里没有它） |
| 不写 `data/frames.json` | ✅ 未改 |
| `EXTRUDE := 32.0` 写死 | ✅ 仍在 `scripts/world_view.gd:42`，未进任何数据文件 |
| 不做 α 0.4、不做屋顶渐变 | ✅ 未实现，屋顶仍是「进屋整块消失」硬切换 |
| 保留 `_house_tex()` 缺图回色块 | ✅ 原样保留（`scripts/world_view.gd:378`），并在 `:377` 加了「永久保留」标注 |
| 保留 `_player_inside()` 进屋不画屋顶 | ✅ 原样保留（`scripts/world_view.gd:472`），逻辑未改，只是加了「先判进屋再画屋顶」的调用位置 |
| `solid_rects()` 返回结构不变 | ✅ 未改（`house_shape.gd:185-199`） |
| 只做 A1–A3 的 12 栋，A4/A5 冻结 | ✅ 分类器对 A4/A5 房子同样生效（是通用算法），但本线**未验证 A4/A5**，未改 A4/A5 数据与贴图 |
| 本线只写 4 个 .gd | ✅ 实际改了 4 个 + 新增 1 个测试文件，无其他 |

### 2.2 关于 §2.1 最后一行 —— A4/A5 的一个已知副作用（请总策划知悉）

分类器是**通用算法**，所以 A4/A5 的房子（如 `school`、`zheng_a4`）在运行时**也会走新的半高墙渲染**。
本线按 PROMPT 冻结 A4/A5，**没有验证也没有截图 A4/A5 的观感**。
如果 A4/A5 的房子有大面积朝南的墙需要全高（例如学校操场边的高墙），现在会变成半高。
→ **这不是 bug，但需要场景设计线 / 总策划确认 A4/A5 是否接受这个观感**，
或由我单独跑一遍 A4/A5 的墙向统计后再定（数据侧我没动，改起来成本很低）。

### 2.3 commit 卫生

- 只 `git add` 了 6 个文件：`scripts/world_view.gd`、`scripts/house_shape.gd`、`scripts/player.gd`、`scripts/main.gd`、`_mdtest/sort_check.gd`(+`.uid`)。
- 工作区里**同时存在的他人未提交改动全部原封未动**：美术资产线（`assets/village/_classmate/`、`_ref/art/gen/`、`docs/ART-MAPPING-classmate.md` 等）、
  A4 场景线（`_ref/houses/_redo_school.py`、`_ref/houses/gen_all_houses.py`、`_ref/houses/houses_data.json`、`docs/HANDOFF-VILLAGE.md`）、大量 `lab/_*` 中间产物。
- 本线**产生的临时文件已全部删除**（`_mdtest/_probe_walls.gd`、`_mdtest/_ysort_shot.gd`、`_mdtest/_ysort_verify.gd`、`_mdtest/ysort/`、`lab/_*_out.log`/`_*_err.log`）。
  → 像素级验收脚本属临时工具（PROMPT 只允许 `_mdtest/*_sort_check.gd`），**已删**；如总策划希望长期保留，可另立一条 PR。

---

## 3. 回归结果（判 green 看关键字，不看退出码 —— 沙箱噪声 `Failed to read the root certificate store.` 是基线固有）

```
sort_check.gd        SORT_CHECK_DONE fails=0
greybox_check.gd     WORLD_OK=true / START_OK=true / HOTSPOTS_OK=true
                     WALL_BLOCKED=true / UNEXPLAINED_BLOCKS=0 / REACH_OK=true
camera_check.gd      CAMERA_CHECK_DONE fails=0
display_check.gd     exit=0，无 SCRIPT ERROR
                     CONTENT_SCALE_MODE=1 / CONTENT_SCALE_ASPECT=1
                     CONTENT_SCALE_SIZE=(1280,720) / 默认纹理过滤=0 / STRETCH_SCALE_MODE=0
hud_layout_check.gd  HUD_CHECK_DONE fails=0
```

五套全部 exit=0，无 SCRIPT ERROR / Parse Error。
**提交后又在他人新 commit（`631afa9 feat(school): v5 ...`）之上复跑过 sort_check + greybox_check，仍全绿。**

---

## 4. 请总策划决策的三件事

### ① 消费点接入线（`PROMPT-asset-consumption-exec.md`）——**现在可以开工了，但有一个文件级冲突要先解**

美术线的反馈文档里写了「消费点接入线与视觉机制线同写 `scripts/*.gd`，必须串行」。
**本线已收工并 commit，`scripts/world_view.gd` 现在没有未提交改动 → 撞车窗口已解除。**

但还有一个残留冲突需要总策划指定顺序：
消费点接入线要新建 `scripts/asset_draw.gd`，而本线刚把**房子/墙/家具/树/井/玩家**的绘制
全部收进了 `scripts/world_view.gd` 的 `_draw_back()` / `_draw_front()` 两层里。
- 若接入线新建独立 `asset_draw.gd` 画 props → 需要 world_view 把它当一个可排序条目接进 `_collect_front()`；
- 或直接扩 `_draw_front()` 里的 `"furniture"` / `"prop"` 分支。
→ **两条路都能走，但选哪条由总策划定**，避免两条线同时改 `_collect_front()`。

另：美术线反馈里提的「`houses_data.json` 家具没有 `id` 键」，
本线实测**确认属实**（`solid_rects()`/`furniture_rects()` 读的都是 `name`/`short`/`rect`/`clue`/`zone`）。
本线**没有动数据**，这一条仍留给接入线 + 总策划决策。

### ② A4/A5 的半高墙观感（见 §2.2）

通用算法已作用到 A4/A5，本线未验证。请总策划决定：
- 接受（则本线收工）；或
- 派一条小任务给本线跑 A4/A5 墙向统计（只读，不改数据）。

### ③ D8 ③「美术按 D6 规格重画并接入」的下一步归属

引擎侧消费点（`_house_tex()`）已就位且接口冻结。房屋 `_base.png` / `_roof.png`
**美术线已交付并在本机实际画出来过**（本线像素验收第 5 条读到了 roof 贴图 texel）。
→ 是否现在就推进「按 D6 重画房屋贴图 + 接入」，还是等 props 消费点一起做，请总策划排期。

---

## 5. 遗留问题 / 已知不足

1. **墙体本体仍是色块**，不是贴图。墙现在是「顶面 + 南立面」两段式像素渲染（顶面 `#c9a878`、立面 `#8c6b4a`），
   房子 `_base.png` 目前只画在屋顶层。美术线若要替换墙体，需要新开贴图规格（DECIDE D6 目前只冻了 base/roof 尺寸）。
2. **A4/A5 未验证**（见 §2.2）。
3. **像素验收脚本已删除**（PROMPT 只允许 `_mdtest/*_sort_check.gd`）。
   若总策划想要一个长期可跑的「画面级」回归（不只是逻辑断言），需要放开文件名约定，
   我可以补一条 `_mdtest/ysort_pixels_check.gd`（需**去掉 `--headless`** 才能取到像素）。
4. **`set_player_pos()` 保留未删**（`world_view.gd:96`），main.gd 已改调 `set_player_state()`，
   但旧函数留在那儿以免破坏潜在调用方；总策划若认为该清，可让我删。

---

## 6. 给后续线的一条沙箱经验（本线踩了 5 次，建议写进 HANDOFF）

1. **Godot `--headless` 是 dummy 渲染器 → 拿不到像素**：`root.get_texture().get_image()` 返回 null，
   报 `ERROR: Parameter "t" is null`。要截图/像素级验收**必须去掉 `--headless`**（真实 OpenGL 上下文）。
2. **headless 下也不能用管道捕获 stdout**（EPERM）→ 必须
   `Start-Process ... -RedirectStandardOutput <file> -RedirectStandardError <file>` 再读文件；
   直接 `& godot ... 2>&1 | Select-Object` 会挂死。
3. **PowerShell 的 `Get-Content`/`Set-Content` 往返会损坏 UTF-8 中文文件**（中文变乱码 + 吃掉行尾 → GDScript Parse Error）。
   → **改文件一律用 edit/write 工具，绝不用 pwsh 做文本替换。**
4. 镜头是 lerp 跟随（`scripts/camera_rig.gd`），等 60 帧也可能没收敛 →
   像素验收要**直接钉死** `camera_rig.set("offset", want)` + `camera_rig.call("_apply")`。
5. 玩家脚下有地面影子（`scripts/player.gd:72-73`）→ 判「玩家本体色」要**采样圆心上方 6px**，不能取圆心。
   中文 print 在 GBK 控制台是乱码 → **只看 PASS/FAIL 关键字**。

---

## 7. 自查签字

- [x] 只改 4 个 .gd（+1 新测试），未越界
- [x] 未写 `houses_data.json` / `frames.json`
- [x] `EXTRUDE` 仍写死在代码里
- [x] 未实现 α 0.4 / 屋顶渐变
- [x] `_house_tex()` 降级路径原样保留
- [x] `_player_inside()` 逻辑未改
- [x] `solid_rects()` 返回结构未改，碰撞恒为整格 AABB
- [x] 8 条检查项全绿（像素级）
- [x] 五套回归全绿
- [x] 临时文件已清理
- [x] commit 信息与 PROMPT §3 一致，只 add 允许的文件
- [x] 未触碰 A4 精调线 / 美术资产线的任何未提交改动
