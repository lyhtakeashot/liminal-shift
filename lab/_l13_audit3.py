import io, os, json, re

BASE = r"D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift"

def rd(p):
    with io.open(os.path.join(BASE, p.replace("/", os.sep)), encoding="utf-8") as f:
        return f.read()

def ls(p):
    return rd(p).split("\n")

story = ls("docs/story.md")

print("=" * 74)
print("K. story.md 全文「环岛」出现位置（新 §7.3 断言 A4 有环岛）")
print("=" * 74)
for i, l in enumerate(story, 1):
    if u"环岛" in l:
        print("  story.md:%d  %s" % (i, l.strip()[:130]))

print()
print("=" * 74)
print("L. story.md 「唯一没有移动过」相关句（与树位移冲突？）")
print("=" * 74)
for i, l in enumerate(story, 1):
    if re.search(u"唯一.*(没|未).*移动|地砖", l):
        print("  story.md:%d  %s" % (i, l.strip()[:150]))

print()
print("=" * 74)
print("M. 当前 data/frames.json（未落 L11）里 A4/A5 有没有环岛/竖路")
print("=" * 74)
cur = json.loads(rd("data/frames.json"))
print("  world =", cur["world"])
for fr in cur["frames"]:
    road_polys = [s for s in fr["shapes"] if s.get("type") == "polygon" and s.get("label") == u"路"]
    print("  %-9s polygon数=%d  其中label「路」=%d" % (fr["id"], len([s for s in fr["shapes"] if s.get("type")=="polygon"]), len(road_polys)))
    for s in road_polys:
        pts = s.get("points", [])
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        print("       路 polygon bbox=(%d,%d,%d,%d)" % (min(xs), min(ys), max(xs), max(ys)))
    for s in fr["shapes"]:
        if s.get("type") == "circle" and u"槐" in str(s.get("label","")):
            print("       老槐 center=%s r=%s" % (s.get("center"), s.get("radius")))

print()
print("=" * 74)
print("N. v3 规划里 老槐 A1-A3 → A4/A5 的位移")
print("=" * 74)
v3 = json.loads(rd("lab/_l11_final.json"))
pos = {}
for fr in v3["frames"]:
    for s in fr["shapes"]:
        if s.get("type") == "circle" and u"槐" in str(s.get("label","")):
            pos[fr["id"]] = (s.get("center"), s.get("radius"))
for k, v in pos.items():
    print("  %-9s 老槐 center=%s r=%s" % (k, v[0], v[1]))
if "a1_1926" in pos and "a4_2001" in pos:
    dx = pos["a4_2001"][0][0] - pos["a1_1926"][0][0]
    dy = pos["a4_2001"][0][1] - pos["a1_1926"][0][1]
    print("  => A1→A4 老槐位移 = (%d, %d)  = %d 格" % (dx, dy, max(abs(dx), abs(dy)) // 32))

print()
print("=" * 74)
print("O. 老井 A1 hotspot 文案 vs npc.md 新老井 A1 旁听句（是否重复）")
print("=" * 74)
for fr in cur["frames"]:
    if fr["id"] == "a1_1926":
        for h in fr["hotspots"]:
            if u"井" in str(h.get("title","")):
                print("  frames.json a1 老井 hotspot: title=%r text=%r" % (h.get("title"), h.get("text")))
npc = ls("docs/npc.md")
print("  npc.md:230 老井 A1 旁听 =", npc[229].strip()[:150])
