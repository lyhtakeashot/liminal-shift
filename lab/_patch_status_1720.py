import io

def read(p):
    with io.open(p, encoding='utf-8') as f:
        return f.read().split('\n')

def write(p, lines):
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))

# ---------- 1) docs/待解决事项.md 状态行（第 6 行） ----------
p = 'docs/待解决事项.md'
lines = read(p)
assert lines[5].startswith('> **当前状态**'), lines[5][:60]
lines[5] = (
    '> **当前状态**：2026-11-25 17:20 · 仓库 HEAD `9f89c86`（本地；远端仍 `b0798da`，按用户定时指令推）· '
    '🔴 **最新快照＝`docs/RESUME-2026-11-25-1720.md`**（旧快照 `docs/RESUME-2026-11-25.md` 已标过期）｜'
    '**L9 已交卷**（`014a18c`，只改 `scripts/world_view.gd` +69/−4，反馈 `docs/FEEDBACK-render-bug-exec.md` 117 行，**总策划尚未独立复核**）'
    '⇒ **L11 的 `world_view.gd` 阻塞解除**｜'
    '🔴 **A5 帧布局已定稿为 v4**（`lab/_a5_draft.py` 自检 errors=0，产出 `lab/_a5_draft.json`，预览 `lab/_a5_preview.png`，均已入库 commit `bdfbdf2`）：'
    '环心=树心=路口中心=(2048,1456)、环岛内圈 R176＋环道 128＋外缘 R304、两条引道在环岛外圆处断开、井 (2048,832) r48、'
    '四角＝小学/超市/玩具店/停车场、界碑 (480,864) 嵌小学西墙实墙格、红绿灯 (2112,816)｜'
    '🔴 **A5 v4 推翻 `lab/_l11_final.json`（v3）**：v3 环心在 (2048,1696)、A5 竖路三段 polygon、界碑 [736,512] ⇒ **L11 任务书基准需换，且照 v3 跑会得到「路口不在环岛里」的破几何**｜'
    '🔴 **装饰房引擎穿帮（本轮新挖）**：14 栋 decor 复用 `lu_house`/`zhou_house` id ⇒ `world_view.gd:668` `FAMILY` 命中 A1 陆家底图 + '
    '`frame_data.gd:66` 自动生成 14 份 A1 线索热点 ⇒ **建议采方案乙（引擎加 decor 分支）**｜'
    '🔴 **主题句从项目第一天就写偏**（`story.md:988` 与 `HANDOFF.md:833` 同句「唯一没移动过的东西，是那块地砖」；`git log -S` 只有初始化提交）'
    '⇒ 用户已给中文新句「时过境迁，沧海桑田，我仍在此处看云卷云舒。」（不加老槐、不用全称断言），英文版待写｜'
    '🔴 **`story.md:433`/`:700`「十字路口中央」与新几何冲突**（井在车道正中、距路口中心 624px）⇒ 建议改「车道正中」｜'
    'L2/L3/L4/L5/L6/L12/L13 七条已交付并验收通过｜L8 资产接线任务书未写｜实机 Shift+E 最终验收未做'
)
write(p, lines)
print('OK 待解决事项.md 状态行已更新（行 6）')

# ---------- 2) docs/PROMPT-overseer.md ----------
p = 'docs/PROMPT-overseer.md'
lines = read(p)

# 2a) L9 行 (§十 表格里那一行)
hit = 0
for i, l in enumerate(lines):
    if l.startswith('| L9 渲染缺陷调查'):
        lines[i] = (
            '| L9 渲染缺陷调查（人站在墙上 / 门可穿 / A4 门口色块乱） | ✅ **已交卷**（commit `014a18c`，只改 `scripts/world_view.gd` +69/−4，反馈 `docs/FEEDBACK-render-bug-exec.md` 117 行）| '
            '**实测推翻任务书 §2.1 的定位**：A4/A5 色块路径排序无错位（python 逐格复刻全 0 例），真因在 A1–A3 美术路径（base 图整张画在背景层、前景 walls 分支有图就 `return`）'
            '⇒ 新增 `_draw_art_wall_strips()` 把墙行横条按同落点公式贴回前景层（补贴带固定 64px 高，只在 `alpha_mul==1.0` 主通道贴）＋门 `sort_y` 改行北沿（58/58 门格中心被盖→0）。'
            '碰撞未动 ⇒ DOOR_PASSABLE／WALL_STOP_Y(816)／A1_WELL_FREE 不变。**⇒ L11 的 `world_view.gd` 阻塞解除。**'
            '🟡 **总策划尚未独立复核**（待办）。'
        )
        hit += 1
assert hit == 1, hit

# 2b) 在 §十一 末尾追加 17:20 更新段（插在 "### ✅ 现在就能开" 之前）
anchor = '### ✅ 现在就能开'
idx = lines.index(anchor)
seg = [
    '**2026-11-25 17:20 更新（A5 v4 定稿 + 转接文档）**：**A5 帧布局已定稿为 v4**（`lab/_a5_draft.py` 自检 errors=0 → `lab/_a5_draft.json` ＋预览 `lab/_a5_preview.png`，'
    '已 commit `bdfbdf2` 入库）。🔴 **它推翻 `lab/_l11_final.json`（子代理 v3）**：v4 的环心/树心/路口中心统一在 (2048,1456)、内圈 R176＋环道 128＋外缘 R304、'
    '两条引道在环岛外圆处断开（v3 是主路直穿环岛内岛 ⇒ 路口根本不在环岛里）；井 (2048,832) r48、界碑 (480,864) 嵌小学西墙实墙格、红绿灯 (2112,816)、'
    '四角＝小学(448,288)/超市(2128,225)/玩具店(2128,1856)/停车场(1440,1792)。'
    '⇒ **L11 任务书基准必须换**，且 **A1–A4 的新布局尚未定**（用户 2026-11-25 m07696 提过「从 A4/A5 反推 A1–A3」，还没做）。'
    '🔴 **本轮新挖两个装饰房引擎穿帮**：①`world_view.gd:668` `FAMILY["lu_house"]=["lu","a1"]` ⇒ A5「空白房子」会贴 A1 陆家底图；'
    '②`frame_data.gd:66` 对每栋 house 都调 `HouseShape.hotspots()` ⇒ 14 栋装饰房各带「旧木箱」/「小桌」热点 ⇒ A5 冒出 14 份 A1 线索（`lu::旧木箱`/`zhou::小桌` 键被灌）；'
    '且门洞不碰撞 ⇒ 玩家能走进装饰房，「不可探索」没实现。**建议方案乙＝引擎加 decor 分支**（`world_view.gd` 画纯色块墙+屋顶不贴图、`frame_data.gd` 对 decor 房跳过 hotspots、整栋 lot 进碰撞；'
    '改动面正好在 L11 白名单里）。🔴 **主题句从项目第一天就写偏**（`story.md:988` 与 `HANDOFF.md:833` 同句「唯一没移动过的东西，是那块地砖」；`git log -S "那块地砖"` 只有初始化提交）'
    '⇒ 用户已给中文新句「时过境迁，沧海桑田，我仍在此处看云卷云舒。」（不加老槐、不用全称断言），英文版适配 itch 介绍页待写；**两处必须同步改**。'
    '🔴 **`story.md:433`/`:700`「十字路口中央」与新几何冲突**（井在车道正中、距路口中心 624px）⇒ 建议改「车道正中」（A5 热点文案已是「铺在车道正中」）。'
    '📌 **转接快照＝`docs/RESUME-2026-11-25-1720.md`**（旧 `docs/RESUME-2026-11-25.md` 已标过期）。',
    '',
]
lines = lines[:idx] + seg + lines[idx:]
write(p, lines)
print('OK PROMPT-overseer.md 已更新（L9 行 + 17:20 更新段，插入行号 %d）' % idx)
