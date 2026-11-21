"""A3 1976 陆家地基/废墟：从 lu_a2 派生，补陆家线 1951 空屋→1976 荒废的断档。

口径（用户 m01420 提问 + 选定「补 A3 陆家地基/废墟」）：
  陆家 1951 已空（lu_a2），陆敬之当年被推进井里；到 1976 房子彻底塌了，
  house-spec.md:28「1976 陆家只剩地基」，docs/HANDOFF.md:413「房子→废墟→空地」。
  这栋是不可进入的废墟态：只剩残墙基 + 夯土地基 + 荒草，作一条线索格。

实现：结构（lot/wings/partitions/doors/gate/rooms）照抄 lu_a2 让 check_all 照常全过；
  加 ruin=True，生成器据此把墙画成残墙基、地板画成夯土+荒草、门画缺口、不画房间名。
  「断井颓垣」＝demolished 白名单让部分墙格在网格数据里真正缺失（不是渲染做旧）：
  门格/院门格/角格不动，外墙缺失露成院口、内隔墙缺失露成夯土地面。
  家具几乎清空，只留堂屋中央一处「堂屋地基痕迹」线索格。
幂等：存在则替换，否则追加。
"""
import json
import os
from gen_all_houses import build_grid

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")

with open(DATA, encoding="utf-8") as f:
    houses = json.load(f)

src = next(h for h in houses if h["id"] == "lu_a2")

a3 = {
    "id": "lu_a3",
    "name": "陆家 · 地基废墟 · A3 1976 · 受害方（房已塌）",
    "ruin": True,
    "lot": list(src["lot"]),
    "wings": [list(w) for w in src["wings"]],
    "partitions": [list(p) for p in src["partitions"]],
    "doors": [list(d) for d in src["doors"]],
    "gate": [list(g) for g in src["gate"]],
    "rooms": [list(r) for r in src["rooms"]],  # 保留仅供校验；废墟态图上不画房间名
    # 断井颓垣：部分墙格在网格数据里真正缺失（非渲染做旧）。
    # 保留门(5,5)(10,2)(10,5)/院门(6,7)；其余墙格按坐标哈希挑约 45% 抹掉。
    "demolished": [],  # 下方按原始网格填充
    "furniture": [
        {"name": "堂屋地基痕迹", "short": "堂屋地基", "rect": [7, 2, 2, 2],
         "zone": "house", "clue": True,
         "note": "原堂屋 · 扒开荒草还能看出夯土地基的占地轮廓（非物件，时间长了自然留下）"},
        {"name": "倒塌的灶台残砖", "short": "灶台残砖", "rect": [13, 5, 1, 2],
         "zone": "house", "clue": False,
         "note": "砌死在墙里的灶台也塌成一堆残砖"},
    ],
    "clue": [
        "房子塌了 · 1951 年还有床架八仙桌的空屋，到 1976 只剩残墙基与夯土地基。",
        "堂屋位置只剩荒草 · 走的人把祖宗牌位带走了，二十五年过去没人回来。",
    ],
    "story": "陆文 1926 年溺亡后陆家败落，1951 年陆敬之回村查地、当夜被推进老井，房子从此彻底无人。到 1976 年 A3，这栋空屋已经塌成废墟——只剩地基和半截残墙，荒草长满堂屋。陆家这条线在村子里彻底断了，直到 2026 陆敬之的手记重见天日才被人记起。",
    "note": "屋本体 15×8、占地 19×9，与 A1/A2 陆家同址同尺寸——同一块地基。1976 年只剩地基废墟（house-spec：房子→废墟→空地），不可进入，图上以断砖残墙基/夯土地基/荒草表示，仅堂屋一处线索格。结构字段照抄 lu_a2 仅为校验布局合法，废墟态渲染由 ruin=true 驱动。",
}

for f in a3["furniture"]:
    f["yard_building"] = False

# 用未拆墙的原始网格挑出要抹掉的墙格——门/院门/家具格不拆。
_base_grid = build_grid({k: src[k] for k in ("lot", "wings", "partitions", "doors", "gate")})
_keep = {(x, y) for x, y in [tuple(d) for d in src["doors"]] + [tuple(g) for g in src["gate"]]}
_keep |= {(i, j) for f in a3["furniture"]
          for i in range(f["rect"][0], f["rect"][0] + f["rect"][2])
          for j in range(f["rect"][1], f["rect"][1] + f["rect"][3])}
a3["demolished"] = [
    [x, y]
    for y in range(src["lot"][1], src["lot"][3] + 1)
    for x in range(src["lot"][0], src["lot"][2] + 1)
    if (_base_grid[y - src["lot"][1]][x - src["lot"][0]] == "#"
        and (x, y) not in _keep
        and (x + y * 3) % 7 < 3)  # 约 3/7 ≈ 43% 的墙格塌掉
]

# 需要美术铺 16px 杂草素材的格子：图上只画绿框+"草"占位标注，不画程序化草叶。
# 候选＝最终网格里的夯土地基格 '.' / 露天院格 ' '（含拆墙后露出的格）；
# 排除门/院门格和家具（线索格/残砖）占格；按坐标哈希选约 43%，出图稳定。
_full_grid = build_grid(a3)
a3["grass"] = [
    [x, y]
    for y in range(src["lot"][1], src["lot"][3] + 1)
    for x in range(src["lot"][0], src["lot"][2] + 1)
    if (_full_grid[y - src["lot"][1]][x - src["lot"][0]] in (".", " ")
        and (x, y) not in _keep
        and (x * 5 + y * 3) % 7 < 3)
]

# 自检：家具不压墙/门/院门
grid = build_grid(a3)
for f in a3["furniture"]:
    x, y, w, h = f["rect"]
    for i in range(x, x + w):
        for j in range(y, y + h):
            assert grid[j][i] in (".", " "), f"家具压墙/门：{f['name']} ({i},{j}) = {grid[j][i]}"

for i, h in enumerate(houses):
    if h["id"] == "lu_a3":
        houses[i] = a3
        break
else:
    houses.append(a3)

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(houses, f, ensure_ascii=False, indent=2)

print(f"lu_a3 written: houses {len(houses)} lot {a3['lot']} ruin {a3['ruin']} furniture {len(a3['furniture'])}")
