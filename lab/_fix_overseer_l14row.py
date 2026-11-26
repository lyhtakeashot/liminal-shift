# -*- coding: utf-8 -*-
"""修 overseer §十一 L14 行：原来 3 列表格被插成 4 列，合并回 3 列。"""
import io
p = 'docs/PROMPT-overseer.md'
t = io.open(p, encoding='utf-8').read().split('\n')
i = 333
old = t[i]
assert 'L14 A5 落地' in old, 'not the L14 row'
# 去掉原第三格「任务书已就绪…本线不碰」这段（它在最后一个 | 之后）
parts = old.split(' | ')
print('parts:', len(parts))
for j, x in enumerate(parts):
    print(j, '|', x[:90])
new = parts[0] + ' | ' + parts[1] + ' | ✅ **已交付并验收**（`e086c83`）→ **不要再开重复的**。🔴 尾账：R-L14-1 A4↔A5 同址（超市/井/槐）**已升 P0**、R-L14-2 M15 沈家同位只满足 A5、R-L14-4 A1–A3 仍是旧布局、R-L14-5 河贴图画布写死 3200×416（属 L8）、R-L14-6 实机肉眼验证未做 |'
t[i] = new
io.open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(t))
print('OK fixed')
