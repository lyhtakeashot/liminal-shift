# -*- coding: utf-8 -*-
"""只读：查 school 的墙格分布，确认界碑所在格 (0,18) 是不是墙。"""
import json, io
d = json.load(io.open("_ref/houses/houses_data.json", encoding="utf-8"))
sch = [h for h in d if h["id"] == "school"][0]
print("lot:", sch["lot"])
print("wings:", sch["wings"])
print("doors:", sch["doors"])
print("gate:", sch["gate"])
print("partitions count:", len(sch["partitions"]))
for p in sch["partitions"][:40]:
    print("   ", p)

# 复刻 house_shape.gd 的 grid_of 判定：G > D > partitions > is_wall
W = 38
H = 30
grid = [[". " for _ in range(W)] for _ in range(H)]
for g in sch["gate"]:
    grid[g[1]][g[0]] = "G"
for dd in sch["doors"]:
    grid[dd[1]][dd[0]] = "D"
for p in sch["partitions"]:
    for x in range(p[0], p[2] + 1):
        for y in range(p[1], p[3] + 1):
            if grid[y][x] == ". ":
                grid[y][x] = "#"
for row in grid:
    print("".join(row))
print("cell (0,18) =", repr(grid[18][0]))
print("row 18 =", "".join(grid[18]))
