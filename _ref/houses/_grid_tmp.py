import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
import gen_all_houses as g
data = json.load(open(os.path.join(HERE, "houses_data.json"), encoding="utf-8"))
hs = [h for h in data if h["id"] == "shen_a3"][0]
print("    " + "".join(str(i % 10) for i in range(28)))
for n, r in enumerate(g.build_grid(hs)):
    print(f"{n:2d} {r}")
