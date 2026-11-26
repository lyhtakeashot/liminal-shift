import json, sys
p = "data/frames.json"
d = json.load(open(p, encoding="utf-8"))
print("world", d["world"], "start", d["start_pos"], "safe", d["safe_top"], d["safe_bottom"])
for fr in d["frames"]:
    if fr["id"] not in ("a4_2001", "a5_2026"):
        continue
    print("=" * 60)
    print(fr["id"], "year", fr["year"], "ground", fr.get("ground"))
    print("-- shapes", len(fr["shapes"]))
    for i, s in enumerate(fr["shapes"]):
        t = s.get("type")
        if t == "rect":
            print(i, "rect", s.get("rect"), "label=", repr(s.get("label", "")), "road=", s.get("road"), "solid=", s.get("solid"), s.get("color"))
        elif t == "circle":
            print(i, "circle", s.get("center"), "r=", s.get("radius"), "label=", repr(s.get("label", "")), "solid=", s.get("solid"))
        elif t == "polygon":
            pts = s.get("points", [])
            xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
            print(i, "polygon", "N=", len(pts), "bbox=", (min(xs), min(ys), max(xs), max(ys)), "label=", repr(s.get("label", "")), "solid=", s.get("solid"))
        elif t == "house":
            print(i, "house", s.get("id"), "pos=", s.get("pos"), "solid=", s.get("solid"), "decor=", s.get("decor"))
        else:
            print(i, t, s)
    print("-- hotspots", len(fr["hotspots"]))
    for h in fr["hotspots"]:
        print("   ", h.get("pos"), repr(h.get("title")), "reach=", h.get("reach"))
        print("      text:", (h.get("text") or "")[:60])
