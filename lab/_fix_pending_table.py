# -*- coding: utf-8 -*-
"""修两处：Q3 行列数超了；§4 表新增行插到了空行之后（表格被断开）。"""
import io
p = 'docs/待解决事项.md'
t = io.open(p, encoding='utf-8').read().split('\n')

# --- 1. Q3 行：重建为 4 列 ---
for i, l in enumerate(t):
    if l.startswith('| **Q3**'):
        t[i] = ('| **Q3**<br>✅已办 | **已办（2026-11-26）：L14 执行线已写完并落地** —— 老槐五帧新文案全部换掉'
                '（统一「朝西北歪」，不再说「朝井那侧」；a5 删掉已作废的「拱裂地砖」；a5 结尾改为'
                '「环岛修起来的时候，把它圈在了正当中，树冠正好顶满内圈」）**（原问题：老槐五帧新文案谁写？）** | '
                '**L14 执行线写**（它已经是 `data/frames.json` 的唯一写者，顺手闭环；别的线写会撞写者锁） | '
                '低。已写进 L14 任务书 §3.4，落地于 L14 `e086c83` |')
        print('fixed Q3 at', i + 1)
        break
else:
    raise SystemExit('Q3 row not found')

# --- 2. §4 表：把新增的 6 行移到空行之前 ---
new_rows = [l for l in t if l.startswith('| **L14 A5 落地** | ✅ 已交付并验收（`0989e87`')
             or l.startswith('| **A4 重排线**（新，P0）')
             or l.startswith('| **A1–A3 重排线**（新）')
             or l.startswith('| **L15 归档表 + 结局变体**（新）')
             or l.startswith('| **L16 双日记渲染**（新）')
             or l.startswith('| **L17 phasing/虚化**（新）')]
assert len(new_rows) == 6, len(new_rows)
# 移除原位置
t = [l for l in t if l not in new_rows]
# 找 L6 行，其后一格是空行 → 插到空行之前
idx = None
for i, l in enumerate(t):
    if l.startswith('| L6 文档回写 v2 |'):
        idx = i
        break
assert idx is not None
assert t[idx + 1].strip() == '', repr(t[idx + 1])
t[idx + 1:idx + 1] = new_rows

io.open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(t))
print('OK fixed; lines =', len(t))
