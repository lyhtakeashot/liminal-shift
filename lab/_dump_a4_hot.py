import json
d=json.load(open("data/frames.json",encoding="utf-8"))
for f in d["frames"]:
    if f["id"]!="a4_2001": continue
    print("== a4_2001 hotspots ==")
    for h in f["hotspots"]:
        print("-",h["title"],"|pos",h["pos"],"|reach",h.get("reach"))
        print("   ",h.get("text","")[:120])
