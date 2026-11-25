import io, os, re

BASE = r"D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift"

def rd(p):
    with io.open(os.path.join(BASE, p), encoding="utf-8") as f:
        return f.read()

def ls(p):
    return rd(p).split("\n")

print("=" * 74)
print("A. 六条 grep 独立复核（L13 任务书 §6.1 要求）")
print("=" * 74)
story = ls("docs/story.md")
npc = ls("docs/npc.md")
hand = ls("docs/HANDOFF.md")

def hits(lines, pat, label):
    out = []
    for i, l in enumerate(lines, 1):
        if re.search(pat, l):
            out.append((i, l.strip()))
    print("  [%s] %d 命中" % (label, len(out)))
    for i, l in out[:8]:
        print("      %d: %s" % (i, l[:110]))
    return out

hits(story, u"倾斜", "story.md 倾斜 (期望 0)")
hits(story, u"私生子", "story.md 私生子 (期望只命中 :964 右列)")
hits(npc, u"老槐", "npc.md 老槐 (期望 0)")
hits(npc, u"这树", "npc.md 这树 (期望 0)")
hits(story, u"拱裂", "story.md 拱裂 (期望 0)")
hits(npc, u"拱裂", "npc.md 拱裂 (期望 0)")
hits(hand, u"拱裂", "HANDOFF.md 拱裂 (期望 0)")
hits(hand, u"树倾斜", "HANDOFF.md 树倾斜 (期望 0)")

print()
print("  附: story.md 树|槐 命中位置 ——")
for i, l in enumerate(story, 1):
    if re.search(u"树|槐", l):
        print("      %d: %s" % (i, l.strip()[:100]))

print()
print("=" * 74)
print("B. story.md §7.3 现状逐字（期望：标题保留 + 三段 + 全节无「井」字）")
print("=" * 74)
for i in range(444, 458):
    if i <= len(story):
        print("  story.md:%d  %s" % (i, story[i - 1]))
sec = "\n".join(story[446:455])
print("  => §7.3 整节含「井」字？", u"井" in sec)

print()
print("=" * 74)
print("C. story.md 纪律③ 表现状")
print("=" * 74)
for i in range(956, 968):
    if i <= len(story):
        print("  story.md:%d  %s" % (i, story[i - 1]))

print()
print("=" * 74)
print("D. npc.md 关键行现状")
print("=" * 74)
for n in (167, 211, 221, 230, 232, 298, 329, 335, 336, 337, 338, 340, 341, 357, 381):
    if n <= len(npc):
        print("  npc.md:%d  %s" % (n, npc[n - 1][:130]))

print()
print("=" * 74)
print("E. HANDOFF.md :378 与 :453")
print("=" * 74)
for n in (378, 453):
    if n <= len(hand):
        print("  HANDOFF.md:%d  %s" % (n, hand[n - 1][:130]))

print()
print("=" * 74)
print("F. 与 A17 口径交叉：story §7.3 vs frames.json 待同步四句")
print("=" * 74)
for pat in (u"2001 年十字路口修起环岛", u"2026 年树冠正好顶满环岛中间", u"1951 年树干抱得过来", u"1976 年树冠压到路边"):
    print("  story §7.3 含「%s」？" % pat, (pat in "\n".join(story[446:455])))

print()
print("=" * 74)
print("G. 全仓残留：现行文档里还在讲「树倾斜/井边树/拱裂」的地方")
print("=" * 74)
KEY = [u"树倾斜", u"井边种的", u"拱裂", u"朝远离井", u"朝西北歪"]
for p in sorted(os.listdir(os.path.join(BASE, "docs"))):
    if not p.endswith(".md"):
        continue
    if p.startswith("_backup") or p.startswith("FEEDBACK") or p.startswith("HANDOVER"):
        continue
    path = os.path.join(BASE, "docs", p)
    try:
        L = io.open(path, encoding="utf-8").read().split("\n")
    except Exception:
        continue
    for k in KEY:
        for i, l in enumerate(L, 1):
            if k in l:
                print("  docs/%s:%d  [%s] %s" % (p, i, k, l.strip()[:95]))
