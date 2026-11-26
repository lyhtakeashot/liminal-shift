# -*- coding: utf-8 -*-
import io

p = 'docs/待解决事项.md'
s = io.open(p, encoding='utf-8').read()
BT = chr(96)

lines = s.split('\n')

# locate the Q9 row and the table end
q9_idx = None
for i, l in enumerate(lines):
    if l.startswith('| **Q9**'):
        q9_idx = i
        break
if q9_idx is None:
    raise SystemExit('Q9 row not found')

# find end of table: first empty line after q9_idx
end = q9_idx + 1
while end < len(lines) and lines[end].strip() != '':
    end += 1

q10 = (
    '| **Q10**<br>✅已定 | **已定（2026-11-26）：「地图不是几何，是贴图」＝ 硬约束 C1–C5**（用户原话：「为什么环岛、公路、树都退化成了几何图形？不是一直在强调最小单位是 32px 的方格吗」）'
    '**（原问题：地图线的验收要不要验贴图？）** | '
    '**C1** 最小单位 = 32×32 单方格可平铺｜**C2** 数据只圈方格区域不写造型｜**C3** 贴图与地图尺寸解耦（放大不得重画）｜**C4** 缺图降级是容错不是验收通过｜**C5** 每个 shape 都要能说出铺什么贴图。'
    '权威＝' + BT + 'docs/地图视觉口径.md' + BT + '；执行＝L8 任务书 ' + BT + 'docs/PROMPT-asset-tile-wire-exec.md' + BT + '（410 行）。'
    '**从现在起「几何就绪」≠「视觉交付」** | 全部地图线（L1/A4/A1–A3 重排线）＋ 验收意见（A4 重排线结论＝「几何通过 / 视觉未交付」）'
)

q11 = (
    '| **Q11**<br>🔴待派线 | **起始帧改 A5**（`scripts/timeline.gd:58` 至今 `index = 0` ⇒ 进游戏站 1926；`docs/house-spec.md:461-464` 2026-11-19 用户拍板「起始帧 = A5 往过去挖」，`:500` 坑表第一条）'
    '**（原问题：进游戏从哪个时代开始？）** | **改成读配置、默认最后一帧（a5_2026）**；建议加 `data/frames.json` 的 `start_frame` 字段而不是写死 | '
    '只改 `scripts/timeline.gd` ＋ `data/frames.json` ＋ `docs/house-spec.md` 状态回写；**这条 2026-11-19 就该写进任务书，是我的漏项**；与 L15 归档表「玩家在 A5 站在超市里」的设计直接相关（`docs/story.md:631`）'
)

lines[end:end] = [q10, q11]

s = '\n'.join(lines)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ufffd', s.count('\ufffd'), 'lines', s.count(chr(10)) + 1)
