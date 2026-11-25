import io

p = 'docs/PROMPT-overseer.md'
with io.open(p, encoding='utf-8') as f:
    lines = f.read().split('\n')

hit = 0
for i, l in enumerate(lines):
    if l.startswith('| **L9 渲染缺陷调查**（新） |'):
        lines[i] = (
            '| **L9 渲染缺陷调查** | ✅ **已交卷**（`014a18c`，只改 `scripts/world_view.gd` +69/−4，反馈 `docs/FEEDBACK-render-bug-exec.md` 117 行）'
            '→ **不要再开重复的**；🟡 总策划尚未独立复核（待办）。**L11 的 `world_view.gd` 阻塞已解除。**'
        )
        hit += 1
assert hit == 1, hit

with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines))
print('OK overseer §十一 L9 行已更新')
