import io, sys

PD = 'docs/待解决事项.md'

def read(p):
    return io.open(p, encoding='utf-8').read().split('\n')

def write(p, lines):
    io.open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))

def find(lines, needle, start=0):
    hits = [i for i, l in enumerate(lines) if needle in l]
    if len(hits) != 1:
        print('FIND_FAIL', needle[:40], 'hits=', len(hits), [lines[h][:60] for h in hits])
        sys.exit(1)
    return hits[0]

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

# 2) §1.6 加 Q12（在 Q11 行之后）
i = find(pd, '| **Q11**<br>')
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

# 3) §4 表加一行（用表头定位 §4）
i4 = find(pd, '## §4 已在跑 / 已交付')
hits = [k for k in range(i4, len(pd)) if pd[k].startswith('| **界碑删除线**')]
print('sec4 hits:', len(hits))
if len(hits) != 1:
    print([pd[h][:80] for h in hits]); sys.exit(1)
row = ('| **地图场景化（方案 B）Stage 1** | ✅ **任务书已写，可派**（`docs/PROMPT-scene-tilemap-exec.md`，437 行）'
       '｜🟢 只读 `data/frames.json`、不碰 `scripts/**` ⇒ 零冲突可并行 | '
       '新建 `tools/bake_world_scene.gd` ＋ `tools/world_scene_spec.gd` ＋ `scenes/world/**`（5 `.tscn` ＋ 5 `.tres`）'
       '＋ `_mdtest/scene_bake_check.gd`；**只读** `data/frames.json`；**不碰** `scripts/**`／`assets/**` |')
pd.insert(hits[0] + 1, row)

write(PD, pd)
print('pending lines:', len(pd))
s = io.open(PD, encoding='utf-8').read()
print('FFFD=', s.count('\ufffd'))
