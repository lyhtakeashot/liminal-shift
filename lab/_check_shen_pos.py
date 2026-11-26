import math

TILE = 32
MILL_X0, MILL_X1 = 38, 55

def river_depth(x):
    """权威公式：逐字照抄 _ref/houses/_design_v5.py:59-74"""
    base = (5.5
            + 1.5 * math.sin(x / 13.0 + 0.6)
            + 0.8 * math.sin(x / 5.3 + 2.1))
    center = (MILL_X0 + MILL_X1) * 0.5
    sigma = 16.0
    bay = math.exp(-((x - center) / sigma) ** 2)
    base += bay * 8.0
    return int(round(max(4, min(15, base))))

RY = [(river_depth(x) + 1) * TILE for x in range(150)]

def river_max_y(x0, x1):
    """某 x 区间的河下沿（最大 y）。口径：该区间内 RIVER_Y 的最大值。"""
    return max(RY[x] for x in range(x0 // TILE, x1 // TILE + 1))

LOT = 1152            # shen_a4 lot 36x36 格
HOUSE_X = 64
HOUSE_X1 = HOUSE_X + LOT
ROAD_N = 1600         # A5 主路带北沿

print("=== 沈家四合院 (lot 1152x1152) 的合法 y ===")
for pos_y in (352, 416, 448):
    top, bot = pos_y, pos_y + LOT
    rm = river_max_y(HOUSE_X, HOUSE_X1)
    ok_river = top >= rm + TILE
    ok_road = (ROAD_N - bot) >= TILE
    print(f"pos=({HOUSE_X},{pos_y}) rect=({HOUSE_X},{top})-({HOUSE_X1},{bot})")
    print(f"   河下沿(格 2..37 最大) = {rm}  需 top >= {rm+TILE}  ⇒ {'✅' if ok_river else f'❌ 压河 {rm+TILE-top}px'}")
    print(f"   距主路北沿 {ROAD_N}      = {ROAD_N-bot}   需 >= 32  ⇒ {'✅' if ok_road else '❌ 压路'}")

rm = river_max_y(HOUSE_X, HOUSE_X1)
print()
print("权威公式下：河下沿(沈家 x 区间) =", rm)
print("不压河的最小 pos_y =", rm + 32)
print("M15 锚点 [64,352] 压河深度 =", rm + 32 - 352, "px")
print("v5fix 用的 (64,416) 压河深度 =", max(0, rm + 32 - 416), "px")
print()
print("RIVER_Y[2..38] =", RY[2:39])
print("全河 max =", max(RY[:100]), "argmax(格) =", RY[:100].index(max(RY[:100])))
