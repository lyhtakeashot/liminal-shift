import io, os, json, re

BASE = r"D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift"

def rd(p):
    with io.open(os.path.join(BASE, p), encoding="utf-8") as f:
        return f.read()

print("=" * 74)
print("H. A4/A5 的环岛几何是否存在（§7.3 说「2001 年十字路口修起环岛」）")
print("=" * 74)
d = json.loads(rd("lab/_l11_final.json"))
for fr in d["frames"]:
    polys = [s for s in fr["shapes"] if s.get("type") == "polygon"]
    circ = [s for s in fr["shapes"] if s.get("type") == "circle"]
    print("  %s : shapes=%d polygon=%d circle=%d" % (fr["id"], len(fr["shapes"]), len(polys), len(circ)))
    for s in polys:
        pts = s.get("points", [])
        bb = None
        if pts:
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            bb = (min(xs), min(ys), max(xs), max(ys))
        print("     polygon label=%r n=%d bbox=%s" % (s.get("label"), len(pts), bb))
    for s in circ:
        print("     circle  label=%r center=%s r=%s" % (s.get("label"), s.get("center"), s.get("radius")))

print()
print("=" * 74)
print("I. L13 反馈文档 §5 D2 清单逐条核对（该文档说的 file:line 与实际是否对得上）")
print("=" * 74)
CHECKS = [
    ("docs/待解决事项.md", 36), ("docs/待解决事项.md", 39), ("docs/待解决事项.md", 40),
    ("docs/待解决事项.md", 85), ("docs/待解决事项.md", 89), ("docs/待解决事项.md", 90),
    ("docs/待解决事项.md", 111), ("docs/待解决事项.md", 210), ("docs/待解决事项.md", 211),
    ("docs/待解决事项.md", 328), ("docs/待解决事项.md", 329), ("docs/待解决事项.md", 330),
    ("docs/待解决事项.md", 333), ("docs/待解决事项.md", 337), ("docs/待解决事项.md", 344),
    ("docs/待解决事项.md", 352), ("docs/待解决事项.md", 361), ("docs/待解决事项.md", 363),
    ("docs/待解决事项.md", 364), ("docs/待解决事项.md", 365), ("docs/待解决事项.md", 366),
    ("docs/BUILD-A1.md", 42), ("docs/BUILD-A1.md", 80),
    ("docs/PROMPT-a5-map-build-exec.md", 80), ("docs/PROMPT-a5-map-build-exec.md", 88),
    ("docs/PROMPT-evidence-model-exec.md", 39), ("docs/PROMPT-evidence-model-exec.md", 54),
    ("docs/PROMPT-evidence-model-exec.md", 55),
    ("docs/PROMPT-art-asset-gap-exec.md", 144),
    ("docs/art-assets-a1a3.md", 350),
    ("docs/DECIDE-a4-a5-layout.md", 80),
    ("docs/PROMPT-overseer.md", 79),
    ("docs/ART-HANDOFF-a4a5.md", 79),
    ("docs/ART-GAP-A4A5.md", 492),
]
for p, n in CHECKS:
    path = os.path.join(BASE, p.replace("/", os.sep))
    if not os.path.exists(path):
        print("  %-38s :%-4d  ❌ 文件不存在" % (p, n))
        continue
    L = rd(p).split("\n")
    if n > len(L):
        print("  %-38s :%-4d  ❌ 行号越界（文件只有 %d 行）" % (p, n, len(L)))
        continue
    print("  %-38s :%-4d  %s" % (p, n, L[n - 1].strip()[:118]))

print()
print("=" * 74)
print("J. D2 清单里被点名的文件是否真的是「现行活文档」还是「历史存档/任务书」")
print("=" * 74)
CATS = [
    ("docs/待解决事项.md", u"活文档·总策划维护"),
    ("docs/BUILD-A1.md", u"活文档·设定"),
    ("docs/PROMPT-a5-map-build-exec.md", u"旧任务书（已作废？）"),
    ("docs/PROMPT-evidence-model-exec.md", u"旧任务书（已交付）"),
    ("docs/PROMPT-art-asset-gap-exec.md", u"旧任务书（已交付）"),
    ("docs/art-assets-a1a3.md", u"活文档·设定"),
    ("docs/DECIDE-a4-a5-layout.md", u"活文档·决策备忘"),
    ("docs/PROMPT-overseer.md", u"活文档·调度"),
    ("docs/ART-HANDOFF-a4a5.md", u"活文档·给美术同学"),
    ("docs/ART-GAP-A4A5.md", u"活文档·给美术同学（已转发）"),
]
for p, cat in CATS:
    path = os.path.join(BASE, p.replace("/", os.sep))
    if not os.path.exists(path):
        print("  %-38s %s" % (p, u"❌ 不存在"))
        continue
    txt = rd(path)
    mark = u"作废" if (u"已作废" in txt or u"SUPERSEDED" in txt) else u"现行"
    print("  %-38s 自带「已作废/SUPERSEDED」标记？ %s  ｜ %s" % (p, mark, cat))
