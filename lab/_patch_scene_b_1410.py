import io, sys

OV = 'docs/PROMPT-overseer.md'
PD = 'docs/待解决事项.md'

def read(p):
    return io.open(p, encoding='utf-8').read().split('\n')

def write(p, lines):
    io.open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))

def find(lines, needle, start=0):
    hits = [i for i, l in enumerate(lines) if needle in l]
    if len(hits) != 1:
        print('FIND_FAIL', needle[:40], 'hits=', len(hits))
        sys.exit(1)
    return hits[0]

def insert_after(lines, idx, row):
    cols = len([c for c in row.strip().split('|')[1:-1]])
    lines.insert(idx + 1, row)
    return cols

# ---------------- overseer ----------------
ov = read(OV)

# 1) §三 工作线表（5 列）—— 在「界碑删除线」行后插入「地图场景化」行
i = find(ov, '| **界碑删除线**（新） | **撤掉周界石碑与其全部配套**')
row = ('| **地图场景化（方案 B）Stage 1** | **把地图烘焙成真正的 Godot 场景节点**'
       '（TileMapLayer 地面/路/田 ＋ Polygon2D 任意形状 ＋ Sprite2D 前景 y_sort），'
       '让总策划能在编辑器 2D 视图里看见并手摆 | 新建 `tools/bake_world_scene.gd` ＋ '
       '`tools/world_scene_spec.gd` ＋ `scenes/world/**`（5 个 `.tscn` ＋ 5 个 `.tres`）＋ '
       '`_mdtest/scene_bake_check.gd`（**只读** `data/frames.json`，**不碰任何运行时文件**） | '
       '🟢 | ✅ **任务书已写**（`docs/PROMPT-scene-tilemap-exec.md`，437 行）→ **可派**；'
       '🔴 **用户 2026-11-26 拍板「走方案 B」**；⚠️ **Stage 1 只烘焙场景、不改运行时**；'
       'Stage 2（运行时从 `_draw()` 切到场景节点）**另派线**；🟢 与所有线**零文件冲突**'
       '（只读 frames.json） |')
insert_after(ov, i, row)

# 2) §三 索引表（3 列）
i = find(ov, '| `docs/PROMPT-stele-removal-exec.md` | **界碑删除线**')
row = ('| `docs/PROMPT-scene-tilemap-exec.md` | **地图场景化 Stage 1**'
       '（从 `frames.json` 烘焙五帧 Godot 场景：TileMapLayer ＋ Polygon2D ＋ Sprite2D） | '
       '✅ **2026-11-26 新写，可派**（437 行）；🔴 三个引擎坑已实测写死（`create_tile` 必须在 '
       '`add_source` 后经 `get_source()` 调用｜`PackedScene.pack()` 必须给子节点设 `owner=root`｜'
       '`TileMapLayer` 无碰撞 API ⇒ 墙的碰撞仍走 `frame_data.gd`）；'
       '⚠️ `.tscn` 是**产物不是源**（手改会被烘焙器覆盖） |')
insert_after(ov, i, row)

# 3) §十 待办表（3 列）
i = find(ov, '| **界碑删除线**（新） | ✅ **任务书已写，可派**（`docs/PROMPT-stele-removal-exec.md`）')
row = ('| **地图场景化（方案 B）Stage 1**（用户 2026-11-26 拍板「走方案 B」） | '
       '✅ **任务书已写，可派**（`docs/PROMPT-scene-tilemap-exec.md`，437 行） | '
       '目标＝**地图从「数据＋画笔」变成「Godot 场景里的节点」**，总策划能在编辑器 2D 视图里看见并手摆。'
       'Stage 1＝写烘焙器 `tools/bake_world_scene.gd`，从 `data/frames.json` ＋ `asset_draw.gd` 的贴图表'
       '生成 `scenes/world/world_*.tscn` ＋ `tileset_*.tres`（五帧各一），**运行时完全不动**；'
       '🟢 **只读 frames.json、不碰 `scripts/**` ⇒ 与所有线零冲突**；'
       '⚠️ **Stage 2（运行时切场景）不属本线**，等总策划在编辑器里确认后再派 |')
insert_after(ov, i, row)

# 4) §十一「现在就能开」表（3 列）
i = find(ov, '| **界碑删除线** | `data/frames.json`（只删界碑条目）')
row = ('| **地图场景化（方案 B）Stage 1** | 新建 `tools/bake_world_scene.gd` ＋ '
       '`tools/world_scene_spec.gd` ＋ `scenes/world/**` ＋ `_mdtest/scene_bake_check.gd` | '
       '✅ **任务书已写，可派**（`docs/PROMPT-scene-tilemap-exec.md`）；🟢 **只读 `data/frames.json`、'
       '不碰 `scripts/**` ⇒ 可与任何线同时跑**（含 L17／界碑删除线／A1–A3 重排线）；'
       '⚠️ Stage 2 另派 |')
insert_after(ov, i, row)

# 5) §十一 更新段（插在「### ✅ 现在就能开」之前）
i = find(ov, '### ✅ 现在就能开')
seg = ('**2026-11-26 14:10 更新（方案 B 拍板 ＋ 地图场景化任务书已写）**：'
       '用户 m10231 拍板「**1.走方案 B　2.（小地图）这点应该要往后放，因为地图的原因**」⇒ 两条决定：'
       '① **地图要落成真正的 Godot 2D 场景节点**（TileMapLayer ＋ Polygon2D ＋ Sprite2D），'
       '让总策划能在编辑器 2D 视图里看见并手摆；② **小地图改造往后放**'
       '（理由＝小地图要画的内容取决于地图最终形态）。'
       '🔴 **为什么编辑器里现在是空的**（实测）：`scenes/main.tscn` 只有 5 个节点、**没有任何 '
       'TileMap/Sprite2D**（grep 零命中），地图是 `scripts/world_view.gd` 在 `_draw()` 里按 shape 逐个画的'
       '（`:3` 原话「没有图片资源、没有场景继承 —— 全是数据」），且**全仓没有一个 `@tool`** ⇒ '
       '脚本不在编辑器里执行 ⇒ 编辑器 2D 视图里**什么都看不到**。'
       '✅ **新任务书 `docs/PROMPT-scene-tilemap-exec.md`（437 行）已写**：Stage 1＝写烘焙器，'
       '从 `frames.json` ＋ `asset_draw.gd` 的贴图表生成五帧 `.tscn`/`.tres` 入库，'
       '**运行时完全不动**（游戏画面仍是 L8 的平铺管线）；🟢 因只读 frames.json ⇒ **零文件冲突、可与任何线并行**；'
       '🔴 **Stage 2（运行时从 `_draw()` 切到场景节点）不属本线**，等总策划在编辑器里确认后再派。'
       '📌 **三个引擎坑已用探针实测并写进任务书**（`lab/_probe_tilemap*.gd` 六支，未入库）：'
       '`create_tile()` 必须在 `add_source()` 之后**经 `get_source()` 取回引用**再调（用原引用调会得 0 tiles）｜'
       '`PackedScene.pack()` **必须给每个子节点设 `owner = root`**（不设则读回 children=0，设了 children=2）｜'
       '`TileMapLayer` **没有物理碰撞 API**（`add_collision_polygon()` 不存在）⇒ 墙的碰撞仍走 '
       '`scripts/frame_data.gd` 的 `solid_rects`。'
       '📌 **沙箱限制备注**：实机截图抓不到游戏画面（桌面处于锁屏态，`CopyFromScreen` 只拿到壁纸＋锁屏时钟）'
       '⇒ 实机观感验证只能靠总策划那边看，或用 headless/窗口模式渲染＋像素采样替代。\n\n')
ov.insert(i, seg)

write(OV, ov)
print('overseer lines:', len(ov))

# ---------------- 待解决事项 ----------------
pd = read(PD)

# 1) 状态行
i = find(pd, '> **当前状态**：')
pd[i] = ('> **当前状态**：2026-11-26 14:10 · 仓库 HEAD `b928b4c`（本地；远端仍 `b0798da`，'
         '按用户定时指令推）· ✅ **L8 资产接线已交付**（32px 逐格平铺管线打通，窗口模式 39 条像素断言全绿）'
         '· 🟢 **方案 B 拍板**：用户 2026-11-26「**走方案 B**」＝ **地图要落成真正的 Godot 2D 场景节点**'
         '（TileMapLayer ＋ Polygon2D ＋ Sprite2D），让总策划能在**编辑器 2D 视图里看见并手摆**；'
         '✅ 新任务书 `docs/PROMPT-scene-tilemap-exec.md`（437 行，Stage 1＝烘焙器，**不改运行时**）'
         '· 🔴 **小地图改造往后放**（用户原话「这点应该要往后放，因为地图的原因」）'
         '· 🔴 **两个现存缺陷待修**：**D1 河跨帧宽度不一致**（a1–a3 河 x 只到 3200 ⇒ 在 x=3200 断掉）｜'
         '**D2 起始帧反了**（`timeline.gd:58` 是 `index = 0` ⇒ 进游戏站 1926，'
         '而 `house-spec.md:461-464` 已拍板「起始帧 = A5 往过去挖」）')

# 2) §1.6 加 Q12
i = find(pd, '| **Q11**<br>🔴待派线')
q12 = ('| **Q12**<br>✅已拍板 | **已拍板（2026-11-26）：地图落成真正的 Godot 2D 场景节点＝「方案 B」**'
       '（用户原话：「1.走方案 B」）**（原问题：为什么不能在 Godot 的 2D 场景里直接制作、只能给我看渲染图？）** | '
       '**Stage 1（本条已写任务书）**＝写烘焙器 `tools/bake_world_scene.gd`，从 `data/frames.json` ＋ '
       '`scripts/asset_draw.gd` 的贴图表生成 `scenes/world/world_*.tscn` ＋ `tileset_*.tres`（五帧各一）入库 ⇒ '
       '**编辑器 2D 视图里能看见格子、能手摆**；**运行时完全不动**（游戏画面仍是 L8 的平铺管线）；'
       '🟢 **只读 frames.json、不碰 `scripts/**` ⇒ 与所有线零冲突、可并行**；'
       '⚠️ **Stage 2（运行时从 `_draw()` 切到场景节点）另派线**（等总策划在编辑器里确认）'
       '｜🔴 **`.tscn` 是产物不是源**（手改会被烘焙器覆盖；改地图要改 frames.json 再重跑烘焙器）'
       '｜**实测根因**（为什么编辑器里是空的）：`scenes/main.tscn` 只有 5 个节点、无任何 TileMap/Sprite2D，'
       '且全仓无 `@tool` ⇒ 脚本不在编辑器里执行 | '
       '**小地图改造同批往后放**（用户原话「2.这点应该要往后放，因为地图的原因」）—— 理由＝小地图要画的'
       '内容取决于地图最终形态；且现有 `scripts/hud.gd` 的小地图只画「世界框＋玩家点」零场景内容，'
       '技术方案已备（用 `sync()` 收到的 `FrameData.shapes` 降采样，不读 frames.json），但**等地图定稿再开** |')
pd.insert(i + 1, q12)

# 3) §4 表加一行（先看表头列数）
i = find(pd, '| **界碑删除线**')
row = ('| **地图场景化（方案 B）Stage 1** | ✅ **任务书已写，可派**（`docs/PROMPT-scene-tilemap-exec.md`，437 行）'
       '｜🟢 只读 `data/frames.json`、不碰 `scripts/**` ⇒ 零冲突可并行 | '
       '新建 `tools/bake_world_scene.gd` ＋ `tools/world_scene_spec.gd` ＋ `scenes/world/**`（5 `.tscn` ＋ 5 `.tres`）'
       '＋ `_mdtest/scene_bake_check.gd`；**只读** `data/frames.json`；**不碰** `scripts/**`／`assets/**` |')
pd.insert(i + 1, row)

write(PD, pd)
print('pending lines:', len(pd))

# 校验 U+FFFD
for p in (OV, PD):
    s = io.open(p, encoding='utf-8').read()
    print(p, 'FFFD=', s.count('\ufffd'))
