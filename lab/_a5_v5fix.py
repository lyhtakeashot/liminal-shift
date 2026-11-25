# -*- coding: utf-8 -*-
"""A5 v5 修正版最终帧生成器（总策划口径）+ 全量自检。
产出 lab/_a5_v5fix.json（可直接粘进 data/frames.json 的 a5_2026 帧）。
只写 lab/，不碰 data/ scripts/ docs/。

修正要点（相对 lab/_a5_v5.py 的旧输出）：
  1. 河用权威公式 _ref/houses/_design_v5.py:river_depth() 延伸到 150 格（4800px），
     而不是脚本自造的 river_surface()（实测两者逐点 0/103 相同）。
  2. OY=1664（沈家四合院 1152 高 + 不压河 + 距主路 ≥1 格，三条同时成立）。
  3. 删装饰房 14 栋 / 删红绿灯 rect+hotspot / 四合院改用新 id shen_a5。
  4. 起点 (1024,1696) 落在 A5 主路带上。
"""
import json, io, math, os

TILE = 32
W, H = 4800, 3600
GW = W // TILE

# ---------- 权威河 ----------
MILL_X0, MILL_X1 = 38, 55
def river_depth(x):
    base = (5.5 + 1.5*math.sin(x/13.0+0.6) + 0.8*math.sin(x/5.3+2.1))
    c = (MILL_X0+MILL_X1)*0.5
    base += math.exp(-((x-c)/16.0)**2) * 8.0
    return int(round(max(4, min(15, base))))
RIVER_Y = {x: (river_depth(x)+1)*TILE for x in range(GW)}
RIVER_PTS = [[x*TILE, RIVER_Y[x]] for x in range(GW)] + [[W,0],[0,0]]

# ---------- 房屋数据 ----------
HD = json.load(io.open("_ref/houses/houses_data.json", encoding="utf-8"))
LOT = {h["id"]: h["lot"] for h in HD}
def lot_rect(pid, pos):
    l = LOT[pid]
    return (pos[0], pos[1], pos[0]+(l[2]-l[0]+1)*TILE-1, pos[1]+(l[3]-l[1]+1)*TILE-1)
def rect(x,y,w,h): return (x,y,x+w-1,y+h-1)
def overlap(a,b):
    w=min(a[2],b[2])-max(a[0],b[0])+1; h=min(a[3],b[3])-max(a[1],b[1])+1
    return max(0,w)*max(0,h)
def gap(a,b):
    dx=max(a[0]-b[2],b[0]-a[2],0); dy=max(a[1]-b[3],b[1]-a[3],0)
    return math.hypot(dx,dy)
def cgap(b,c,rad):
    dx=max(b[0]-c[0],0,c[0]-b[2]); dy=max(b[1]-c[1],0,c[1]-b[3])
    return math.hypot(dx,dy)-rad
def river_max_y(r):
    return max(RIVER_Y[x] for x in range(r[0]//TILE, r[2]//TILE+1))

# ---------- 锚点 ----------
OX, OY = 2048, 1664
R_IN, ROAD_W, R_OUT = 176, 128, 304
ROAD_N, ROAD_S = OY - ROAD_W//2, OY + ROAD_W//2        # 1600 / 1728
LANE_X0, LANE_X1 = OX - ROAD_W//2, OX + ROAD_W//2      # 1984 / 2112
LANE_TOP = 288
LANE_N_BOT, LANE_S_TOP = OY - R_OUT, OY + R_OUT        # 1360 / 1968
WELL, WELL_R = (2048, 832), 48
TREE = (OX, OY)
START = (1024, 1696)

ROAD_RECTS = [rect(0, ROAD_N, OX-R_OUT, ROAD_W), rect(OX+R_OUT, ROAD_N, W-(OX+R_OUT), ROAD_W)]
ROADS = {"主路西": ROAD_RECTS[0], "主路东": ROAD_RECTS[1],
         "车道北": rect(LANE_X0, LANE_TOP, ROAD_W, LANE_N_BOT-LANE_TOP+1),
         "车道南": rect(LANE_X0, LANE_S_TOP, ROAD_W, H-LANE_S_TOP)}

FIELD = rect(3600, 320, 880, 384)
DAM = rect(384, 96, 256, 128)
HILLS = [(4288,2624,512,384), (64,2624,512,384), (4288,3040,384,288)]
SIGNS = [(800,1732),(1600,1732),(2600,1732),(3400,1732)]

POS = {"shen_a5": (64, 416), "market": (2144, 320), "toyshop": (2176, 1984), "school": (576, 1920)}
PID = {"shen_a5": "shen_a4", "market": "market", "toyshop": "toyshop", "school": "school"}
RECTS = {k: lot_rect(PID[k], v) for k, v in POS.items()}

def circle_poly(c, r, n=72):
    return [[int(round(c[0]+r*math.cos(2*math.pi*i/n))), int(round(c[1]+r*math.sin(2*math.pi*i/n)))] for i in range(n)]

# ---------- 组帧 ----------
shapes = [
    {"type":"polygon","points":RIVER_PTS,"color":"#4a6a60","label":"河","solid":True},
    {"type":"rect","rect":[DAM[0],DAM[1],256,128],"color":"#6a5648","label":"坝","solid":True},
    {"type":"rect","rect":[ROAD_RECTS[0][0],ROAD_RECTS[0][1],ROAD_RECTS[0][2]-ROAD_RECTS[0][0]+1,ROAD_W],
     "color":"#56564f","label":"路","road":True},
    {"type":"rect","rect":[ROAD_RECTS[1][0],ROAD_RECTS[1][1],ROAD_RECTS[1][2]-ROAD_RECTS[1][0]+1,ROAD_W],
     "color":"#56564f","label":"路","road":True},
    {"type":"polygon","points":[[LANE_X0,LANE_TOP],[LANE_X1,LANE_TOP],[LANE_X1,LANE_N_BOT],[LANE_X0,LANE_N_BOT]],
     "color":"#56564f","label":"路","solid":False},
    {"type":"polygon","points":[[LANE_X0,LANE_S_TOP],[LANE_X1,LANE_S_TOP],[LANE_X1,H],[LANE_X0,H]],
     "color":"#56564f","label":"路","solid":False},
    {"type":"polygon","points":circle_poly(TREE,R_OUT),"color":"#56564f","label":"路","solid":False},
    {"type":"polygon","points":circle_poly(TREE,R_IN),"color":"#6b7a4a","label":"岛","solid":False},
    {"type":"circle","center":list(WELL),"radius":WELL_R,"color":"#3a3a38","label":"老井 · 沥青补丁","solid":False},
    {"type":"circle","center":list(TREE),"radius":160,"color":"#3d5230","label":"老槐","solid":False},
    {"type":"rect","rect":[POS["school"][0]+1*TILE, POS["school"][1]+18*TILE, 16,32],
     "color":"#8a8278","label":"碑","solid":True},
    {"type":"rect","rect":[FIELD[0],FIELD[1],880,384],"color":"#6b6440","label":"","solid":False},
]
for (hx,hy,hw,hh) in HILLS:
    shapes.append({"type":"polygon","points":[[hx,hy+hh],[hx+hw//2,hy],[hx+hw,hy+hh]],"color":"#5a6a4a","label":"山","solid":True})
for (sx,sy) in SIGNS:
    shapes.append({"type":"rect","rect":[sx,sy,16,32],"color":"#7a6a52","label":"路标","solid":True})
for pid in ("shen_a5","market","toyshop","school"):
    shapes.append({"type":"house","id":pid,"pos":list(POS[pid]),"solid":True})

STELE = (POS["school"][0]+1*TILE, POS["school"][1]+18*TILE)
hotspots = [
    {"pos":[2048,832],"title":"老井 · 沥青补丁","reach":88},
    {"pos":[2048,1664],"title":"老槐","reach":100},
    {"pos":[512,160],"title":"坝","reach":140},
    {"pos":[4040,512],"title":"田","reach":96},
    {"pos":[STELE[0]+8,STELE[1]+16],"title":"界碑","reach":68},
]

frame = {"id":"a5_2026","year":2026,"ground":"#7a7a76","shapes":shapes,"hotspots":hotspots}
out = {"world":{"width":W,"height":H},"safe_top":36,"safe_bottom":3552,"start_pos":list(START),
       "frame":frame,"notes":{
           "OY":OY,"R_IN":R_IN,"ROAD_W":ROAD_W,"R_OUT":R_OUT,
           "road_band":[ROAD_N,ROAD_S],"lane_x":[LANE_X0,LANE_X1],
           "lane_n":[LANE_TOP,LANE_N_BOT],"lane_s":[LANE_S_TOP,H],
           "stele_cell_relative_to_school":[0,18],"stele_world":[STELE[0],STELE[1]],
           "houses":{k:list(v) for k,v in POS.items()},
           "house_rects":{k:list(v) for k,v in RECTS.items()},
           "hotspot_text_source":"沿用 data/frames.json 现行 a5_2026 的 5 条文案（老槐那条要改）"}}
io.open("lab/_a5_v5fix.json","w",encoding="utf-8").write(json.dumps(out,ensure_ascii=False,indent=1))

# ---------- 自检 ----------
errs = []
# 1. 房-房
names = list(RECTS)
for i in range(len(names)):
    for j in range(i+1, len(names)):
        ov = overlap(RECTS[names[i]], RECTS[names[j]])
        if ov > 0: errs.append("房-房重叠 %s/%s %dpx²" % (names[i], names[j], ov))
        elif gap(RECTS[names[i]], RECTS[names[j]]) < 48:
            errs.append("房-房太近 %s/%s %.0fpx" % (names[i], names[j], gap(RECTS[names[i]],RECTS[names[j]])))
# 2. 房-路 / 房-河 / 房-田 / 房-坝 / 房-山 / 房-环岛 / 房-树冠
for k, r in RECTS.items():
    for nm, rr in ROADS.items():
        g = gap(r, rr)
        if g < TILE: errs.append("%s 距%s %.0fpx < 1格" % (k, nm, g))
    rb = river_max_y(r)
    if r[1] < rb + TILE: errs.append("%s 压河（河下缘%d 房顶%d）" % (k, rb, r[1]))
    if overlap(r, FIELD) > 0: errs.append("%s 压田" % k)
    if overlap(r, DAM) > 0: errs.append("%s 压坝" % k)
    for i,h in enumerate(HILLS):
        if overlap(r, rect(*h)) > 0: errs.append("%s 压山%d" % (k, i+1))
    g = cgap(r, TREE, R_OUT)
    if g < TILE: errs.append("%s 距环岛外缘 %.0fpx < 1格" % (k, g))
    if cgap(r, TREE, 160) < 0: errs.append("%s 被树冠压" % k)
    if r[0] < 0 or r[1] < 0 or r[2] > W-1 or r[3] > H-1: errs.append("%s 出界" % k)
# 3. 环岛与路相切
if abs((OY-R_OUT) - LANE_N_BOT) > 0: errs.append("环岛外缘与车道北不相切")
if abs((OX-R_OUT) - ROAD_RECTS[0][2]) > 1: errs.append("环岛外缘与主路西不相切")
# 4. 树在环岛内圈
if 160 > R_IN - 16: errs.append("树冠 r160 顶满内岛，余量不足 16px")
# 5. 一帧只能一个无 label rect
nl = [s for s in shapes if s.get("type")=="rect" and s.get("label","")==""]
if len(nl) != 1: errs.append("无 label rect 数=%d（必须 1）" % len(nl))
# 6. 井在车道正中
if not (LANE_X0 <= WELL[0] <= LANE_X1): errs.append("井不在车道 x 内")
if not (LANE_TOP <= WELL[1] <= LANE_N_BOT): errs.append("井不在北车道 y 内")
# 7. 起点
if not (LANE_X0-800 <= START[0] <= LANE_X1+800): pass
print("=== 自检 ===")
print("  错误 %d 条" % len(errs))
for e in errs: print("    ❌", e)
if not errs: print("    ✅ 全部通过")
print()
print("=== 关键间距 ===")
for k, r in RECTS.items():
    print("  %-9s %-28s 离河下缘%5d  离环岛外缘%6.0f  离井%5.0f" % (
        k, str(r), river_max_y(r), cgap(r,TREE,R_OUT),
        gap(r, rect(WELL[0]-WELL_R, WELL[1]-WELL_R, WELL_R*2, WELL_R*2))))
print("  井东缘→超市西墙 = %d px" % (RECTS["market"][0] - (WELL[0]+WELL_R)))
print("  环岛外缘 R=%d，内岛 R=%d，树冠 r=160" % (R_OUT, R_IN))
print("  主路带 y=%d..%d（中心 %d）；车道北底=%d 车道南顶=%d" % (ROAD_N,ROAD_S,OY,LANE_N_BOT,LANE_S_TOP))
print("  起点 %s 在主路带内：%s" % (str(START), ROAD_N <= START[1] <= ROAD_S))
print("  shapes=%d hotspots=%d" % (len(shapes), len(hotspots)))
print("  产出 lab/_a5_v5fix.json")
