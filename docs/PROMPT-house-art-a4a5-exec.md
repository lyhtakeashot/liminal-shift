# 执行任务书 · 线 C：A4/A5 七栋房屋贴图（把色块换成真房子）

> 总策划下达 2026-11-26。**本线零代码改动** —— 引擎通路早就接好了，缺的只是美术 PNG 文件。

---

## §0 一句话

A4/A5 的 7 栋房（超市 / 沈家 / 周家 / 郑家 / 玩具店 / 小学）现在在画面上是**院子底色 + 房间色块 + 引擎补的墙和屋顶色块**。
`scripts/world_view.gd` 里 `FAMILY` 表**已经登记好**了这 7 栋的族名与帧号，`_house_tex()` 只去找
`assets/village/houses/<族>/<帧>_base.png` 和 `_roof.png` —— **PNG 一落进对应目录就自动接管**，引擎一个字都不用改。

---

## §1 文件白名单

| 路径 | 允许 |
|---|---|
| `assets/village/houses/market/a4_{base,roof}.png` | 新建 |
| `assets/village/houses/shen/a4_{base,roof}.png` | 新建 |
| `assets/village/houses/zhou/a4_{base,roof}.png` | 新建 |
| `assets/village/houses/zheng/a4_{base,roof}.png` | **新建目录 + 两个文件** |
| `assets/village/houses/shen/a5_{base,roof}.png` | 新建 |
| `assets/village/houses/toyshop/a5_{base,roof}.png` | **新建目录 + 两个文件** |
| `assets/village/houses/school/a5_{base,roof}.png` | **新建目录 + 两个文件** |
| `assets/village/houses/lu/a3_roof.png` | 补既有缺口（`a3_base` 有、`a3_roof` 缺） |
| `_mdtest/house_art_check.gd` | 新建校验脚本 |

🔴 **不许改**：`scripts/**`（一行都不许）、`data/**`、`scenes/**`、`docs/**`、`_ref/houses/houses_data.json`（19 栋的几何数据已经齐了，改它会把整张地图弄歪 —— 历史上翻倍过一次）。

⚠️ 工作区现在的未提交改动里有 `_ref/art/**` 的一批 `M` 和 `美术资产/**` 的一批 `D`，**那不是你的，别提交、别删、别恢复**。

---

## §2 硬规格（照抄，不许自己发挥）

出自 `docs/house-spec.md` §4.8.5 与 `_ref/art/gen/_gen_shells.py` 的文件头注释：

- **画布**：`cw = (lot宽格) × 32`，`ch = (lot高格 + 1) × 32`
  （多出来的那 32px 在**顶部** = 墙/屋顶立起来的高度）
- **锚点**：画布**左上角**贴到世界 `(lot_x, lot_y − 32)`，尺寸 `lot_w×32 × (lot_h+1)×32`
- **透明底**（RGBA，顶部那 32px 里没东西的部分必须真透明）
- **base 里画**：院子地面 + 房间地板 + 墙顶面 + 南立面 + 门窗 + 院门
- **roof 单独一层**：wing 屋顶（南翼压北翼，按 `wy` 升序）
- 一层 32px，像素风，配色跟 `_ref/art/gen/pixel_lib.py` 的 `PAL` 走，别引入新色板

**各栋 lot 尺寸**（`_ref/houses/houses_data.json`，`[x0,y0,x1,y1]`，含边界）：
`shen_a4/shen_a5 = [0,0,35,35]`、`market = [0,0,41,27]`、`school = [0,0,37,29]`、`toyshop = [0,0,20,19]`、`zhou_a4` / `zheng_a4` 自己读、`lu_a3` 有 `ruin` 标记（废墟态）。

---

## §3 怎么做（**优先跑生成器，不要手搓**）

`_ref/art/gen/` 里有现成工具链：

| 脚本 | 用途 |
|---|---|
| `_gen_shells.py` | 从 `houses_data.json` 生成 base/roof（文件头写明「生成 A1–A3 12 栋」，先读它的帧列表/循环条件，看能不能直接跑全 19 栋） |
| `_check_sizes.py` | 验尺寸公式 |
| `_preview_base.py` / `_preview.py` | 出预览图 |
| `pixel_lib.py` | `Canvas` / `TILE=32` / `PAL` / `shade` / `mix` / `hexc` |

python：`C:\Users\lyh\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe`（含 Pillow 12.3.0）

步骤：
1. 读 `_gen_shells.py`，确认它是不是按帧名白名单只跑 a1–a3；是就把帧列表扩到 a4/a5 需要的 id（**只改这个本地生成脚本能接受的范围；改 `_ref/art/gen/*.py` 是允许的，它不在禁止清单里，但改完要在反馈里写清楚**）。
2. 跑到 `assets/village/houses/<族>/` 下。
3. `_check_sizes.py` 验尺寸。
4. 出预览图，肉眼过一遍（对不齐就是坐标映射错了，见 `_gen_shells.py` 文件头的「画布坐标映射」注释）。

⚠️ **不要拿 `_ref/art/A4_2001/`、`_ref/art/A5_2026/` 里那 6 张参考图去切** —— 2026-11-26 实测：它们**全不透明、无 alpha、逐行 100% 填充**（尺寸 1090×1300 ~ 1970×1922），而入库要求透明底 + 独立 roof 层。切了也接不上（历史结论，别再试一遍）。

---

## §4 验收

| # | 断言 |
|---|---|
| C1 | 15 个 PNG 全部存在（含补的 `lu/a3_roof.png`） |
| C2 | 每张尺寸严格等于 `((lot_x1−lot_x0+1)×32, (lot_y1−lot_y0+2)×32)` |
| C3 | 每张都有 alpha 通道，且**透明像素占比 > 0**（全不透明＝把参考图直接塞进来的嫌疑） |
| C4 | `_mdtest/asset_draw_check.gd` 仍 `fails=0` |
| C5 | 窗口模式跑游戏 5 帧截图，**不出现**「双份墙」（base 图 + 引擎色块叠在一起） |
| C6 | `_mdtest/greybox_check.gd` 的 `solids` 仍是 **238/299/379/812/897**（本线不该动量数据） |

`_mdtest/house_art_check.gd`（新建）至少覆盖 C1–C3，**关键词判定，不许只在文档里写**。

---

## §5 已知限制（报告里必须写，不许偷偷绕过）

1. ⚠️ **`market` 在 A4/A5 共用同一个 id** ⇒ `world_view.gd:650` 只能登记一套 `["market","a4"]` ⇒ **A5 的超市会复用 A4 的图**。
   要区分得在数据侧拆 id（`data/frames.json` + `houses_data.json` 一起动）—— **不在本线范围**，报告里写一句即可。
2. 山体、内岛、老槐、老井仍是平色占位（属另一条线，不是本线）。
3. 本线只解决「不再是色块」，不解决「比得上手绘美术」。

---

## §6 交付物

1. 15 个 PNG（按 §1 路径）
2. `_mdtest/house_art_check.gd`
3. 预览图若干（放 `_mdtest/house_art_preview/`）
4. `docs/FEEDBACK-house-art-a4a5-exec.md`：生成了哪些、尺寸核对表、C1–C6 结果、`market` id 冲突、还剩什么

---

## §7 纪律

- `git add` 只加 §1 白名单里的文件；**绝不 `git add -A`**；**不 push**
- 比赛截止 2026-12-02 05:37（北京）。**这条线是「有余量才做」的 P1**：如果只剩 2 天，宁可交色块也别为了贴图把仓库弄脏。