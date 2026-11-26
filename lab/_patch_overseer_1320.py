# -*- coding: utf-8 -*-
import io

p = 'docs/PROMPT-overseer.md'
s = io.open(p, encoding='utf-8').read()

BT = chr(96)


def rep(old, new, tag):
    global s
    assert s.count(old) == 1, (tag, s.count(old))
    s = s.replace(old, new)
    print('ok', tag)


rep('| **A4 重排线**（P0） | ✅ **任务书已按新口径改写，可派**（' + BT + 'docs/PROMPT-a4-rebuild-exec.md' + BT + '，464 行） |',
    '| **A4 重排线**（P0） | ✅ **已交付并验收**（' + BT + '9ec040a' + BT + '，反馈 ' + BT + 'docs/FEEDBACK-a4-rebuild-exec.md' + BT + '＋总策划验收）—— **几何通过 / 视觉未交付**（画面是色块，根因在引擎与缺 L8） |',
    'A4 todo row')

rep('| **L15 归档表 + 结局变体** | ✅ **任务书已写，可派**（' + BT + 'docs/PROMPT-ending-form-exec.md' + BT + '） |',
    '| **L15 归档表 + 结局变体** | ✅ **代码层已交付并验收**（' + BT + '6141ff8' + BT + '＋' + BT + '45c5f72' + BT + '，' + BT + 'ENDING_CHECK_DONE fails=0' + BT + '）｜接线待 L17 |',
    'L15 todo row')

rep('| **L16 双日记渲染** | ✅ **任务书已写，可派**（' + BT + 'docs/PROMPT-diary-render-exec.md' + BT + '） |',
    '| **L16 双日记渲染** | ✅ **已交付并验收**（' + BT + '082f0c5' + BT + '→' + BT + '8a9f0d2' + BT + '→' + BT + '01c3921' + BT + '，' + BT + 'DIARY_RENDER_CHECK_DONE fails=0' + BT + '，删除线自绘达标）｜🔴 ' + BT + 'J' + BT + ' 临时调试键待删、书热点数据未落地 |',
    'L16 todo row')

rep('| **界碑删除线**（新） | ✅ **任务书已写，可派**（' + BT + 'docs/PROMPT-stele-removal-exec.md' + BT + '） |',
    '| **界碑删除线**（新） | ✅ **任务书已写，可派**（' + BT + 'docs/PROMPT-stele-removal-exec.md' + BT + '）｜🔴 与 L8／L17 争 ' + BT + 'world_view.gd' + BT + ' ⇒ 三选一 |',
    'stele todo row')

anchor = '**2026-11-26 10:10 更新（用户拍板「顶住了作废、只做虚化」＋四份新任务书已写）**：'
assert s.count(anchor) == 1

new_block = (
    '**2026-11-26 13:20 更新（三份反馈验收 ＋ 地图事故定性 ＋ L8 补救任务书已写）**：\n'
    '\n'
    '1. 🔴 **三份反馈验收完毕**：**A4 重排线**（' + BT + '9ec040a' + BT + '）＝ **几何通过 / 视觉未交付**；**L15 归档表**（' + BT + '6141ff8' + BT + '＋' + BT + '45c5f72' + BT + '）＝ **代码层通过，接线待 L17**；**L16 双日记**（' + BT + '082f0c5' + BT + '→' + BT + '8a9f0d2' + BT + '→' + BT + '01c3921' + BT + '）＝ **代码层通过**（' + BT + 'J' + BT + ' 临时键待删、书热点数据未落地、举证系统需单独立项）。\n'
    '2. 🔴 **用户 2026-11-26 指出地图事故**：「产出提示词后交给会话构造的地图连游戏地图的核心都丢失了……为什么环岛、公路、树都退化成了几何图形？」⇒ **根因在我，不在执行线**，四层：①任务书层（A5 v5／A4 重排两份任务书里「贴图/平铺/32×32/美术」**零命中**，验收项只验几何）②引擎层（' + BT + 'world_view.gd' + BT + ' polygon 分支**只认河**，无平铺通路）③资产层（美术 autotile 已交付未入库未接线）④**纪律层**（M16/M14 早在 2026-11-25 就写进 ' + BT + '待解决事项.md' + BT + '，**从未转成任务书** —— 规则不落任务书＝不存在）。\n'
    '3. ✅ **新立 ' + BT + 'docs/地图视觉口径.md' + BT + '**（硬约束 C1–C5 ＋ shape→贴图对应表 ＋ 引擎缺口表 ＋ 交付必查清单）＋ **新立 L8 任务书 ' + BT + 'docs/PROMPT-asset-tile-wire-exec.md' + BT + '**（410 行）：**从现在起「几何就绪」≠「视觉交付」**。\n'
    '4. 🔴 **另挖到两个现存缺陷**：**D1 河跨帧宽度不一致**（a1–a3 河 103 点 x 只到 3200，a4/a5 152 点铺到 4800 ⇒ **A1–A3 的河在 x=3200 断掉**；' + BT + 'world_view.gd:264' + BT + ' 画布写死 ' + BT + '3200×416' + BT + '）；**D2 起始帧反了**（' + BT + 'scripts/timeline.gd:58' + BT + ' 至今 ' + BT + 'index = 0' + BT + ' ⇒ 进游戏站 1926，而 ' + BT + 'docs/house-spec.md:461-464' + BT + '（2026-11-19 用户拍板）要求「起始帧 = A5 往过去挖」、' + BT + ':500' + BT + ' 坑表第一条）⇒ 两条都需另派小线。\n'
    '\n'
)

s = s.replace(anchor, new_block + anchor)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ufffd', s.count('\ufffd'), 'lines', s.count(chr(10)) + 1)
