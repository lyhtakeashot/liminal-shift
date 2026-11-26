# 反馈 · A4/A5 七栋房屋贴图（15 张 PNG）

> 执行线交付于 2026-11-26，任务书 `docs/PROMPT-house-art-a4a5-exec.md`。
> **结论：15 张 PNG 全部落地、尺寸/透明/内容逐项实测通过，C1–C6 全绿，零代码改动**（`world_view.gd` 的 `FAMILY` 早就登记好了，图一落引擎自动接管）。
> 需转达 3 项（`market` 共用 id / `lu_a3` 的 roof 是遮罩不是美术 / 没有视觉模型只能数值验收）、需人眼复核 1 项（C5 截图）。

---

## §1 交付清单与尺寸核对表（C1 + C2 + C3）

生成方式见 §3，15 张全部由 `_ref/art/gen/_gen_shells.py` 产出，**没有一张是手搓或从参考图切的**。

| 栋（family/frame） | 文件 | 画布 | 期望 `((x1−x0+1)×32, (y1−y0+2)×32)` | 透明像素占比 base / roof | 不透明颜色数 base / roof |
|---|---|---|---|---|---|
| `market/a4` | `assets/village/houses/market/a4_base.png` · `a4_roof.png` | 1344×928 | 1344×928 ✅ | 0.2% / 3.0% | 35 / 9 |
| `shen/a4` | `assets/village/houses/shen/a4_base.png` · `a4_roof.png` | 1152×1184 | 1152×1184 ✅ | 2.7% / 26.1% | 40 / 13 |
| `zhou/a4` | `assets/village/houses/zhou/a4_base.png` · `a4_roof.png` | 704×384 | 704×384 ✅ | 2.2% / 19.4% | 35 / 9 |
| `zheng/a4` | `assets/village/houses/zheng/a4_base.png` · `a4_roof.png` | 640×448 | 640×448 ✅ | 2.5% / 39.9% | 34 / 9 |
| `shen/a5` | `assets/village/houses/shen/a5_base.png` · `a5_roof.png` | 1152×1184 | 1152×1184 ✅ | 2.7% / 26.1% | 33 / 13 |
| `toyshop/a5` | `assets/village/houses/toyshop/a5_base.png` · `a5_roof.png` | 672×672 | 672×672 ✅ | 4.8% / 23.2% | 32 / 9 |
| `school/a5` | `assets/village/houses/school/a5_base.png` · `a5_roof.png` | 1216×992 | 1216×992 ✅ | 0.2% / 2.8% | 28 / 9 |
| `lu/a3`（补缺口） | `assets/village/houses/lu/a3_roof.png` | 640×448 | 640×448 ✅ | — / 46.4% | — / 12（⚠️ 遮罩，见 §6.4） |

- 尺寸同时被两条独立路径验过：`_mdtest/house_art_check.gd` 用 `ResourceLoader` 读运行时纹理量尺寸，另一个独立 PIL 脚本直接读文件字节量尺寸，两者逐张一致，且都与 `houses_data.json` 的 `lot` 反推值一致（交叉验算，不是自己比自己）。
- 新建目录：`assets/village/houses/{zheng,toyshop,school}/`（这三个族此前只有 a1–a3 之外的空缺，无目录）。
- **每张 PNG 都带同目录的 `.import` sidecar**（`compress/mode=0` 无损、`mipmaps/generate=false`、`vram_texture=false`）。这是本仓库既有约定：`assets/village/houses/**` 下 46 个已跟踪文件里 PNG 与 `.import` 成对出现。**少了 sidecar，引擎会按默认压缩重新导入，headless 校验里 `texture.get_image()` 会拿不到原始像素。**

---

## §2 C1–C6 验收结果

| # | 断言 | 实测 | 判定 |
|---|---|---|---|
| C1 | 15 个 PNG 全部存在 | 15/15（`ResourceLoader.exists` 全 true，含补的 `lu/a3_roof.png`） | ✅ |
| C2 | 尺寸严格等于 lot 公式 | 8 行全中（上表），无一例外 | ✅ |
| C3 | 有 alpha 且透明像素占比 > 0 | 全 `RGBA8`，`detect_alpha() != ALPHA_NONE`；透明占比最低 0.2%（market / school 的 base），最高 46.4% | ✅ |
| C4 | `_mdtest/asset_draw_check.gd` `fails=0` | `ASSET_DRAW_CHECK_DONE fails=0`（HEAD `82c4a31`）。⚠️ 需同步改一条旧断言，见 §7 | ✅ |
| C5 | 窗口模式 5 帧截图无双份墙 | `house_art_check` 窗口模式 `checks=122 fails=0`，11 张截图见 §4 | ✅（**无人眼复核**，见 §4 末） |
| C6 | `greybox_check` 的 `solids` 不变 | `238 / 299 / 379 / 812 / 897`（5 帧逐帧对齐基线），`REACH_OK=true`、`UNEXPLAINED_BLOCKS=0` | ✅ |

`_mdtest/house_art_check.gd`（431 行，新建）把 C1–C3 做成了**关键词判定**，不是文档里写一句：`EXPECT` 七行 + `RUIN_ROOF` 一行，`_ok()` 把 label 里的 `C1`/`C2`/`C3` 记进 `kw_seen`，结尾自检「三档关键词都至少出现过一次」，没覆盖就红。

它还多做了三条内容断言（防「塞色块」和「复制粘贴」）：

- **K1 不是色块**：base 不透明颜色数 ≥10（实测 28–40），roof ≥8（实测 9–13）。
- **K2 roof 不是 base 的整张复制**：同一栋 roof 与 base 在同位置采样差异 ≥20%（实测 95–100%）。
- **K3 废墟遮罩形态正确**：`lu/a3_roof.png` 在翼投影区 `[0,0,480,352]` 与 `a3_base` 逐像素一致（18880 个采样点 0 不一致），翼外 (560,400) 透明。

---

## §3 怎么生成的（跑生成器，没手搓）

### 3.1 `_gen_shells.py` 的改动（任务书 §3 第 1 步允许，此处逐条报备）

该文件原本只跑 `ORDER`（a1–a3 的 12 栋）。改动共 6 处，均为**加一层 A4/A5 批次**，没有改 A1–A3 的任何画法：

1. 文件头 docstring 补一段 A4/A5 批次说明 + `lu_a3` 的 roof 是遮罩的警示。
2. `import` 加 `from PIL import Image`（唯一新增依赖，用于 `crop`/`paste` 遮罩）。
3. `ROOM_TINT` / `ROOM_TEX` 补两个缺键：`bath`（`#9aa8a8` / `tile`）、`field`（`#9a9678` / `earth`）。原表没有这两个键，`zhou_a4` 的卫生间和 `school` 的操场会静默走 `plank` 地板兜底（看起来像室内木地板铺在操场上）。
4. 新增 `FAMILY_A45` / `ORDER_A45` / `STYLE_A45` / `RUIN_ROOF_IDS`，与原 `FAMILY`/`ORDER`/`STYLE` 并列。A4/A5 的材质选择：

   | 栋 | wall | roof | yard | 依据 |
   |---|---|---|---|---|
   | `market`(a4) | stone | tile_g | dirt | A4 是在建工地 ⇒ 毛坯砌体、无装饰 |
   | `shen_a4` | brick | tile_r | grass | 首富宅 ⇒ 红瓦、砖墙、有院子绿 |
   | `zhou_a4` | brick | tile_g | dirt | |
   | `zheng_a4` | plaster | tile_r | dirt | |
   | `shen_a5` | plaster | tile_g | grass | 祖宅 ⇒ 灰瓦灰抹灰（与 a4 明确区分） |
   | `toyshop`(a5) | brick | tile_r | dirt | |
   | `school`(a5) | brick | tile_g | dirt | |

5. 新增 `paint_ruin_roof_mask(hs, base_abs, out_abs)`：生成 `lu/a3_roof.png` 用的**无屋顶遮罩层**（沿 `draw_roof` 的 `x0/x1/y0/y1` 公式算翼投影区，把 base 那块原样 `paste` 进全透明画布，其余留透明）。注释里写清了为什么必须这么做。
6. `main()` 拆出 `gen_one(...)`，并让 `main(argv)` 支持命令行传 house id 只跑指定几栋；roof 画布尺寸改为「manifest 的 `cpx`（A1–A3）或 lot 推导（A4/A5）」。原版 roof 画布尺寸**硬依赖 manifest**，A4/A5 不在 manifest 里（manifest 只登记 A1–A3 的 23 条），不拆这条会直接 KeyError。

### 3.2 执行

```
python _ref\art\gen\_gen_shells.py market shen_a4 zhou_a4 zheng_a4 shen_a5 toyshop school lu_a3
→ generated 16 files
```

- 16 = 14（7 套 × base/roof）+ 1（`lu/a3_roof.png`）+ 1（顺带重写的 `lu/a3_base.png`）。重写的那张 `git status` 显示**无改动** ⇒ 生成确定性、字节一致，没有意外动到既有 A3 资产。
- 生成后跑过一次 `godot --headless --path . --import`，才会有 §1 那批 `.import` sidecar；不跑这一步 `ResourceLoader.exists()` 是 false，引擎仍走色块降级，看起来像「图没生效」。
- ⚠️ **`_ref/art/gen/` 整个目录目前未被 git 跟踪**（`git status` 里是 `?? _ref/art/gen/`）⇒ 上述生成器改动只存在于本机工作区，不会随本次提交走。若以后想复现，得先把这个目录纳入版本管理（不在本线范围）。

### 3.3 `_check_sizes.py` 的结果（任务书 §3 第 3 步）

```
尺寸完成: 131   缺失: 0   尺寸不符: 1
  [错] scene road_straight -> assets/village/scene/road_straight_a3.png  want 3200x96  got 3200x64
manifest 之外的 PNG: 29
```

- **那 1 条尺寸不符与本线无关**：`road_straight_a3.png` 是场景路面，`git log` 指向 2026-11-22 的「主路南移+世界放大」提交（`29a5e2f`），工作区未修改。属**既有** manifest 与产物的口径差，请总策划裁定是改 manifest 还是重出这张路面。
- 「manifest 之外的 PNG 29 个」里 **15 个是本线新图**（预期，manifest 只登记 A1–A3），另外 14 个是别的线（`props/*`、`scene/*_tiles_l8.png`、`scene/stele.png`）。**别把这条输出当失败看。**

### 3.4 预览图（任务书 §6.3）

`_mdtest/house_art_preview/`：

- 8 张单栋预览（棋盘底 + 32px 格线 + 角标「fam frame WxH」）：`shen_a4.png`、`shen_a5.png`、`market_a4.png`、`zhou_a4.png`、`zheng_a4.png`、`toyshop_a5.png`、`school_a5.png`、`lu_a3.png`
- `_ALL.png`：8 张竖排总览（584×3889，1.6 MB，只为一次看完）
- 11 张 C5 截图（见 §4）

---

## §4 C5 是怎么验的（无视觉模型 ⇒ 全部数值化）

⚠️ **本机没有任何视觉模型**：`read_image` 报 `model deepseek-v4.1-flash-1017 does not declare image input`，`modlens_read_image` 报 `No vision provider is set up on this machine`。所以 C5 **没有人眼复核**，全部改用像素数值判定 —— 这是本线最需要人补一眼的地方。

### 4.1 截图

`_mdtest/house_art_check.gd` 加了窗口模式段落（headless 时打印 `PIXEL_SKIP` 只跑逻辑断言）。做法仿 `_mdtest/asset_shot.gd`：实例化 `scenes/main.tscn` → 设 `tl.index`/`tl.char_pos`/`tl.axis=0` → `main._refresh_all()` → `CameraRig.set_target()` 对准目标房屋 → 40 帧 → `cam.set("offset", cam._clamp(cam_at - Vector2(640,360)))` → `cam._apply()` → 两次 `RenderingServer.frame_post_draw` → `root.get_texture().get_image()` 存 PNG。

11 张：`c5_a1_1926_lu_house.png`、`c5_a2_1951_lu_a2.png`、`c5_a3_1976_lu_a3.png`、`c5_a4_2001_{shen_a4,market,zhou_a4,zheng_a4}.png`、`c5_a5_2026_{shen_a5,market,toyshop,school}.png`。A1–A3 三张是**对照组**（老美术，本来就是好的）。

### 4.2 判定方法（为什么它能抓到「双份墙」）

取每栋**最南翼的南立面带**（贴图内坐标 `Rect2(wx*32, (wy+wh-1)*32+32, ww*32, 32)`，换算到屏幕后与视口求交，要求可见宽度 ≥256px），然后：

- 带内按 8×8 小块统计「颜色数 ≥2 的小块占比」≥60%（`C5_PATCH_MIN`）
- 整带颜色数 ≥5（`C5_COLORS_MIN`）

「双份墙」的形态是**美术立面上又压了一层平色块**：色块是单色矩形，压上去会把 8×8 小块的颜色数压成 1，占比与整带颜色数同时塌下来。实测：

| 房屋 | 小块多样性 | 颜色数 |
|---|---|---|
| `lu_house`（a1 对照） | 87% | 12 |
| `lu_a2`（a2 对照） | 92% | 12 |
| `lu_a3`（a3 对照） | 89% | 7 |
| `shen_a4` | 97% | 12 |
| `market`（a4） | 100% | 8 |
| `zhou_a4` | 99% | 14 |
| `zheng_a4` | 83% | 12 |
| `shen_a5` | 82% | 7 |
| `market`（a5） | 100% | 8 |
| `toyshop`（a5） | 99% | 12 |
| `school`（a5） | 86% | 88 |

A4/A5 七栋全部**不低于对照组**（最低 82% vs 对照组 87–92%，同一量级；`school` 的 88 色是因为院子里有田垄+树）。

### 4.3 交叉验证（证明采样真的落在美术上）

把截图里的立面带与 `a4_base.png`/`a5_base.png` 的同区域做逐像素比对（2px 邻域容差），命中率：

`lu_house` 99.6% · `lu_a2` 99.6% · `lu_a3` 100% · `shen_a4` 99.8% · `market`(a4) 92.7% · `zhou_a4` 94.7% · `zheng_a4` 99.6% · `shen_a5` 99.8% · `market`(a5) 92.7% · `toyshop` 99.7% · `school` 84.4%

⇒ 屏幕上那一带**就是**我们生成的立图像素（`school` 84.4% 偏低是因为院里有树/道具遮了一部分），即引擎 1:1 采样、没有额外压平层。

### 4.4 为什么不可能有双份墙（代码层面）

`scripts/world_view.gd:392-431` 的 `_draw_entry`：`"walls"` 分支 **有 base 图就直接 `return`**（不画色块墙），`"door"` 同理；`_art_walls(sid)` = base 图非空。L9 之后只把 base 的同一行「补贴回前景层换深度」，贴的是**同一张图的同一行**，像素相同，不构成双份。

### 4.5 请人补一眼

`_mdtest/house_art_preview/c5_*.png` 11 张已入库，建议有人扫一遍：重点看 `shen_a4`/`shen_a5` 的连锁院墙、`market` 的单一大矩形屋顶、`lu_a3` 的废墟（有没有残留一块突兀的色块屋顶）。

---

## §5 生成结果的内容层面（顺手记录，供美术复核）

- **`market` 单翼 42×28 一格都没有内部院墙** ⇒ base 是一整块连续屋面 + 南立面。A4 是「在建工地」语义，用 stone 毛坯砌体表现；A5 是「营业态」但**复用同一张图**（见 §6.1），所以 A5 超市看起来也是毛坯。这是共用 id 的直接后果，不是画错。
- **`shen_a5` 与 `shen_a4` 几何逐格相同**（`houses_data.json` 刻意如此：祖宅不变），靠材质区分：a4 = brick + 红瓦 + 院子草，a5 = plaster + 灰瓦 + 院子草。采样差异 34.8%，肉眼能分。A5 是「封门」态（`doors=0`、`gate=[]`、`demolished=32`）⇒ **图里没有门洞、没有院门**，这是对的。
- `school` 走 `brick + tile_g`，操场用新补的 `field` 材质（土 + 田垄），不再是木地板。
- `toyshop` 只有一翼 21×16，两个院门都在侧墙上。
- `lu_a3` 是废墟：`paint_ruin` 出夯土地基 + 8px 残墙基 + 杂草，**没有屋顶**。

---

## §6 已知限制（任务书 §5 原文 + 本线新增两条）

### 6.1 `market` 在 A4/A5 共用同一个 id（§5.1，原文转述）

`data/frames.json` 的 `a4_2001` 与 `a5_2026` 两帧都引用 house id `market`（世界坐标不同：a4 `[2144,320]`，a5 另有其位），而 `scripts/world_view.gd:650` 的 `FAMILY` 只能登记一套 `"market": ["market","a4"]` ⇒ **A5 的超市会复用 A4 的图**。要区分必须在数据侧拆 id（`data/frames.json` + `_ref/houses/houses_data.json` 一起动）—— **不在本线范围，本线一个字没动这两个文件。**

### 6.2 山体、内岛、老槐、老井仍是平色占位（§5.2）

属另一条线（L8 贴图平铺 + 场景化），不是本线。

### 6.3 本线只解决「不再是色块」（§5.3）

不解决「比得上手绘美术」。A4/A5 的观感 = 与 A1–A3 同一套程序化画法，够看、不耐细看。

### 6.4 ⚠️ 本线新增：`lu/a3_roof.png` 不是美术，是「压色块遮罩」

`scripts/world_view.gd:900-945` 的 `_draw_roof` **无条件先按 wings 画一层色块屋顶**（`:912-934`），再在 `:937-945` 把 `tex_roof` 叠上去。所以：

- 如果给废墟一张**全透明** roof 图，色块屋顶照样在下面 ⇒ 塌掉的房子头上顶着一块平色瓦，比没有 roof 图更糟（没有 roof 图时 `ResourceLoader.exists` 为 false，`_draw_roof` 的贴图那段跳过，但色块仍然画 —— **废墟在补齐前就一直在被画色块屋顶**）。
- 因此本线交的 `lu/a3_roof.png` 是「把 `a3_base` 在翼投影区原样复制过去、其余透明」的遮罩：它不改变任何像素，只负责用**同像素**盖住那块色块。**别把它当新美术去评审，也别在上面加瓦片。**
- **根治办法（本线零代码，没做）**：`_draw_roof` 在 `hs.get("ruin", false)` 时整体跳过色块那一段（或者在 `_draw_entry` 的 `"roof"` 分支对 ruin 直接 return）。那样这张遮罩图就可以删掉。建议下一轮交给能动 `scripts/**` 的线。

### 6.5 ⚠️ 本线新增：`shen_a4` / `shen_a5` 两套图故意几何相同

若只扫一眼缩略图会以为「生成器没换参数」。真相：`houses_data.json` 里两栋的 `lot/wings/partitions/rooms` 逐格相同（祖宅不变是设定），**唯一区分就是材质与 seed**。已在 §5 记录。

---

## §7 改动了一个既有测试（必须报备）

`_mdtest/asset_draw_check.gd`（+8 / −3，唯一被修改的已跟踪测试文件）：`_check_a4a5_wiring()` 里那条旧断言

```gdscript
# 原文自带注释：「哪天美术落地了这条会红，届时把断言改成『有图』」
_ok(not WorldView._art_walls("shen_a4"), "shen_a4 尚无 base 图 → 走引擎色块降级（美术到位后改断言）")
```

本线一落 `shen/a4_base.png`，它必然红（实测改前正好 `fails=1`，唯一红项就是它）。按文件自己写的约定翻面：

```gdscript
_ok(WorldView._art_walls("shen_a4"), "shen_a4 已有 base 图 → 走美术通路（不再是色块降级）")
var tex = WorldView._house_tex("shen_a4")   # 顺带验一张的尺寸，其余由 house_art_check 全量覆盖
_ok(sz == Vector2(1152, 1184), ...)
```

另外：`lab/_l9_verify.gd:85` 还有一句同样的 `_ok(not wv._art_walls("shen_a4"), ...)`。那是 L9 的一次性脚本（`lab/` 下未跟踪），**本线没动它** ⇒ 将来谁再跑它会看到 FAIL，属预期，不是新回归。

---

## §8 回归（不只 C4–C6，跑在 HEAD `82c4a31`）

| 脚本 | 结果 |
|---|---|
| `_mdtest/house_art_check.gd`（headless） | `checks=99 fails=0` + `PIXEL_SKIP` |
| `_mdtest/house_art_check.gd`（窗口） | `checks=122 fails=0` |
| `_mdtest/asset_draw_check.gd` | `fails=0`（C4） |
| `_mdtest/greybox_check.gd` | `solids=238/299/379/812/897`、`hotspots=10/11/13/12/8`、`REACH_OK=true`、`UNEXPLAINED_BLOCKS=0`（C6） |
| `_mdtest/scene_bake_check.gd` | `fails=0` checks=1868 |
| `_mdtest/sort_check.gd` | `fails=0` |
| `_mdtest/interior_check.gd` | `RESULT: ALL PASS`（WALLS=62 · INTERIOR_CELLS=43 · ROOF_ALPHA=0.0 · MAIN_SCENE_OK children=6） |
| `_mdtest/a4_rebuild_check.gd` | `fails=0` |
| `_mdtest/tile_wire_check.gd` | `fails=0` gaps=0 checks=16（headless 下 `PIXEL_SKIP` 正常） |
| `_mdtest/display_check.gd` | 设置项全对（CONTENT_SCALE_MODE=1 · SIZE=(1280,720) · 默认纹理过滤=0 · STRETCH=0）；尾部 stderr 只有 `ERROR: Failed to read the root certificate store.`，是环境噪音 |

---

## §9 提交范围（`git add` 只加白名单，未 push）

加进 index 的：

1. 15 张 PNG（§1 表）
2. 对应 15 个 `.import` sidecar（§1 已说明必要性）
3. `_mdtest/house_art_check.gd`（新建）
4. `_mdtest/house_art_preview/` 下 20 张 PNG（8 单栋预览 + `_ALL.png` + 11 张 C5 截图）
5. `docs/FEEDBACK-house-art-a4a5-exec.md`（本文件）
6. `_mdtest/asset_draw_check.gd`（§7 的断言翻面，**不加则 C4 必红**）

**没加、也没动**的：

- `_ref/art/gen/`（整目录未跟踪，生成器改动只在本机）
- `scripts/**`、`data/**`、`scenes/**`、`_ref/houses/houses_data.json` —— 一行未改
- 工作区原有别人的未提交改动：`_ref/art/A1_1926/` 等 12 个 PNG 的 `M`、`data/frames.json`、`scripts/frame_data.gd`、`scripts/timeline.gd`、`docs/HANDOFF.md`、`美术资产/**` 的 `D` —— 原样留在工作区
- 本线临时校验脚本（`lab/` 下生成的 `_inspect_art.py`/`_verify_a45.py`/`_qa_pixels.py`/`_make_preview.py`/`_band_stats.py`/`_verify_c5.py`/`_table_stats.py` 等）已删除；它们的结论全部写进本文件与 `house_art_check.gd`

---

## §10 还剩什么

1. **人眼看 C5 截图**（§4.5）—— 本线唯一没做到的验收形式。
2. **要不要拆 `market` 的 id**（§6.1）。要拆就是数据线任务：`data/frames.json` 两帧各自指向不同的 house id + `houses_data.json` 里加一条、生成器里加一组材质。
3. **废墟屋顶的根治**（§6.4）：`_draw_roof` 对 `ruin` 跳过色块，然后删掉 `lu/a3_roof.png`。
4. **`road_straight_a3.png` 的 manifest 口径差**（§3.3）：不是本线的，但 `_check_sizes.py` 会一直报这一条。
5. A4「在建工地」目前只靠 stone 毛坯暗示，**没有脚手架/铁皮围挡**。要真做就得引入新贴图族（`_ref/art/A4_2001` 那 6 张参考图无 alpha、接不上，别回头去切）。