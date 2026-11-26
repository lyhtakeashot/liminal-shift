# -*- coding: utf-8 -*-
import io

p = 'docs/待解决事项.md'
s = io.open(p, encoding='utf-8').read()
BT = chr(96)


def rep(old, new, tag):
    global s
    assert s.count(old) == 1, (tag, s.count(old))
    s = s.replace(old, new)
    print('ok', tag)


# 1) 状态行整行重写
lines = s.split('\n')
for i, l in enumerate(lines):
    if l.startswith('> **当前状态**：'):
        lines[i] = (
            '> **当前状态**：2026-11-26 13:20 · 仓库 HEAD ' + BT + '7b410bd' + BT + '（本地；远端仍 ' + BT + 'b0798da' + BT + '，按用户定时指令推）· '
            '🔴 **2026-11-26 地图事故定性（用户指出的核心问题）**：「产出提示词后交给会话构造的地图连游戏地图的核心都丢失了……为什么环岛、公路、树都退化成了几何图形？」'
            '⇒ **根因在总策划的任务书与引擎缺位，不在执行线**；已立 ' + BT + 'docs/地图视觉口径.md' + BT + '（C1–C5 硬约束）＋ '
            + BT + 'docs/PROMPT-asset-tile-wire-exec.md' + BT + '（L8 补救任务书，410 行）· '
            '✅ **三份反馈验收完毕**：A4 重排线＝**几何通过 / 视觉未交付**；L15 归档表＝**代码层通过、接线待 L17**；L16 双日记＝**代码层通过** · '
            '🔴 **另挖到两个现存缺陷**：**D1 河跨帧宽度不一致**（a1–a3 河 x 只到 3200 ⇒ 在 x=3200 断掉）｜**D2 起始帧反了**（' + BT + 'timeline.gd:58' + BT + ' 是 ' + BT + 'index = 0' + BT + ' ⇒ 进游戏站 1926，'
            '而 ' + BT + 'house-spec.md:461-464' + BT + ' 2026-11-19 已拍板「起始帧 = A5 往过去挖」）'
        )
        print('ok status line', i + 1)
        break
else:
    raise SystemExit('status line not found')

s = '\n'.join(lines)

# 2) §0 速览表「已在跑的线」行
rep('| 已在跑的线 | 🔵 | **L9 渲染缺陷**（已派未交卷，' + BT + 'docs/FEEDBACK-render-bug-exec.md' + BT + ' 不存在）＝ **唯一阻塞 L11 的一条** ｜ **L12 界面手感** ✅ 已交付并验收通过 ｜ **L13 叙事文本** ✅ 已交付并验收通过（🔴 闭环项等 L11）',
    '| 已在跑的线 | 🔵 | **L8 资产接线（P0，新）** —— 任务书已写（' + BT + 'docs/PROMPT-asset-tile-wire-exec.md' + BT + '），**这是地图事故的真正补救线** ｜ **L17 phasing** 任务书已写待派 ｜ **界碑删除线** 任务书已写待派 ｜ **A1–A3 重排线** 待 A4 完成后写 ｜ 已结案：L12 界面手感 ✅｜L13 叙事文本 ✅｜L14 A5 落地 ✅｜L15 归档表 ✅（接线待 L17）｜L16 双日记 ✅｜A4 重排线 ✅（几何通过/视觉未交付）',
    'overview running row')

# 3) §4 表：L8 行
rep('| L8 资产接线 | ⚠️ 任务书**未写**，等 §2 裁完再写（树冠尺寸/井位置定了我才能写准） | — | ' + BT + 'scripts/asset_draw.gd' + BT + '、' + BT + 'scripts/world_view.gd' + BT + '（**与 L9 冲突 → L9 先**） |',
    '| **L8 资产接线**（🔴 P0） | ✅ **任务书已写**（2026-11-26 13:20，' + BT + 'docs/PROMPT-asset-tile-wire-exec.md' + BT + ' 410 行）—— 32px 平铺管线：地面铺装＋polygon 按 label 分派＋rect 逐类贴图；权威＝' + BT + 'docs/地图视觉口径.md' + BT + ' | 交付＝32px 贴图通路 ＋ 美术缺口表 ＋ ' + BT + 'docs/FEEDBACK-asset-tile-wire-exec.md' + BT + ' | ' + BT + 'scripts/world_view.gd' + BT + '、' + BT + 'scripts/asset_draw.gd' + BT + '、' + BT + 'assets/village/scene/' + BT + ' 新切片（**与 L17／界碑删除线三选一**） |',
    'sec4 L8 row')

# 4) §4 表：A4 重排线行 → 验收结论
rep('| **A4 重排线**（P0） | ✅ **已交付**（同批提交 ' + BT + 'feat(map): a4_2001 帧按 A5 v5 新世界重排' + BT + '，反馈 ' + BT + 'docs/FEEDBACK-a4-rebuild-exec.md' + BT + '，112 行）｜🟡 总策划尚未复核 —— ' + BT + 'a4_2001' + BT + ' 换成 26 shapes / 5 hotsp',
    '| **A4 重排线**（P0） | ✅ **已交付并验收**（' + BT + '9ec040a' + BT + '）—— 结论：**几何通过 / 视觉未交付**（画面是色块，根因在引擎缺 polygon 贴图通路 ＋ 缺 L8）；空气墙 cover 双向 100%／IoU 100%／双向触发 0 格；证物 25 卡 55 观察 | ' + BT + 'docs/FEEDBACK-a4-rebuild-exec.md' + BT + '（含总策划验收 §11） | ' + BT + 'data/frames.json' + BT + '（只改 ' + BT + 'a4_2001' + BT + ' 一帧） |',
    'sec4 A4 row')

# 5) §4 表：L15 / L16 行 → 已交付
rep('| **L15 归档表 + 结局变体** | ✅ **任务书已写，可派**（' + BT + 'docs/PROMPT-ending-form-exec.md' + BT + '）—— 真相全在 ' + BT + 'docs/story.md' + BT + ' §10.0–§10.5；⚠️ 接线段要等 L17 |',
    '| **L15 归档表 + 结局变体** | ✅ **代码层已交付并验收**（' + BT + '6141ff8' + BT + '＋' + BT + '45c5f72' + BT + '，' + BT + 'ENDING_CHECK_DONE fails=0' + BT + '）｜🔴 接线段要等 L17（' + BT + 'main.gd' + BT + ' 7 处补丁已备） |',
    'sec4 L15 row')

rep('| **L16 双日记渲染** | ✅ **任务书已写，可派**（' + BT + 'docs/PROMPT-diary-render-exec.md' + BT + '）—— 语法 ' + BT + 'docs/diary-markup.md' + BT + ' ＋ 原稿 ' + BT + 'docs/story.md' + BT + ' 附一；🔴 删除线必须自绘 |',
    '| **L16 双日记渲染** | ✅ **已交付并验收**（' + BT + '082f0c5' + BT + '→' + BT + '8a9f0d2' + BT + '→' + BT + '01c3921' + BT + '，' + BT + 'DIARY_RENDER_CHECK_DONE fails=0' + BT + '）｜🔴 ' + BT + 'J' + BT + ' 临时调试键待删、书热点数据未落地、举证/对质/呈上需单独立项 |',
    'sec4 L16 row')

# 6) §4 表后追加：另两个小线（L8 关联）
anchor = '**L9 的三条问题（已派，先记在这儿免得丢）**：'
assert s.count(anchor) == 1
extra = (
    '**另两个小线（2026-11-26 13:20 验收时挖出，尚未写任务书）**：\n'
    '\n'
    '- 🔴 **D1 · 河跨帧宽度不一致**：a1/a2/a3 的河 polygon 是 **103 点、x 只到 3200**，a4/a5 是 **152 点、铺到 4800** ⇒ **A1–A3 的河在 x=3200 处视觉断掉**；'
    '引擎侧 ' + BT + 'world_view.gd:264' + BT + ' 的河贴图画布写死 ' + BT + 'Vector2(3200, 416)' + BT + ' ⇒ 铺到 4800 也会被拉扁。'
    '**数据侧归 A1–A3 重排线，引擎侧归 L8。**\n'
    '- 🔴 **D2 · 起始帧反了**：' + BT + 'scripts/timeline.gd:58' + BT + ' 至今 ' + BT + 'index = 0' + BT + ' ⇒ 进游戏站 **1926**；'
    '而 ' + BT + 'docs/house-spec.md:461-464' + BT + '（2026-11-19 用户拍板）写明「起始帧 = A5，往过去挖」，' + BT + ':500' + BT + ' 把它列为**坑表第一条**，'
    + BT + ':780' + BT + ' 给的改法是「' + BT + 'index = 0' + BT + ' → 读配置（默认最后一帧 / a5）」。⇒ 需一条小线（只改 ' + BT + 'timeline.gd' + BT + ' ＋ ' + BT + 'frames.json' + BT + ' 加 ' + BT + 'start_frame' + BT + ' 字段）。'
    '**这条 2026-11-19 就该写进任务书，是我拖到现在。**\n'
    '\n'
)
s = s.replace(anchor, extra + anchor)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ufffd', s.count('\ufffd'), 'lines', s.count(chr(10)) + 1)
