# -*- coding: utf-8 -*-
"""B 档：按候选编号切图 → 目视确认 → 落盘。

流程：
  1. PICK 里声明 (图集名, 候选序号, 目标 manifest id)
  2. 从图集按候选框裁出 → 裁透明边 → 贴到底部（画布 = 占地宽×32 × (占地高×32+32)）
  3. 生成确认接触表 lab/_cls_pick_check.png（带 id 标签），供目视核对
  4. 目视通过后，主图落到 assets/village/_classmate/props/<id>.png，
     同 id 的其余切片落到 _variants/

PICK 里的候选序号来自 lab/_cls_atlas_cands.json（连通域+32 网格吸附）。
"""
import json
import os
import shutil
import sys

from PIL import Image, ImageDraw

ROOT = r"D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift"
SRC = os.path.join(ROOT, "美术资产", "家具")
LAB = os.path.join(ROOT, "lab")
OUT = os.path.join(ROOT, "assets", "village", "_classmate", "props")
VAR = os.path.join(OUT, "_variants")
TILE = 32

# (图集名, 候选序号, 目标 id, 备注)
# 候选序号来自 lab/_cls_atlas_cands.json（连通域 + 32 网格吸附），
# 每条都对照 lab/_sheet_<图集>_<页>.png 的编号与 @x,y 网格位置目视核对过。
PICK = [
    # ---- Interior.png：床/书架/桌椅，最干净的一批 ----
    ("Interior.png", 0,  "shuangrenchuang_2x2", "蓝被双人床 @0,1"),
    ("Interior.png", 2,  "shuangrenchuang_2x2", "粉被双人床 @3,1"),
    ("Interior.png", 4,  "shuangrenchuang_2x2", "米色双人床 @9,1"),
    ("Interior.png", 6,  "shujia_2x2",         "彩色大书架 @10,1"),
    ("Interior.png", 7,  "shujia_2x2",         "彩色宽书架 @12,1"),
    ("Interior.png", 9,  "yi_1x1",            "木椅 @16,2"),
    ("Interior.png", 10, "gui_1x2",           "高立柜 @0,3"),
    ("Interior.png", 11, "yigui_1x2",         "窄立柜/衣柜 @5,3"),
    ("Interior.png", 13, "shujia_1x2",         "窄书架 @10,3"),
    ("Interior.png", 16, "danrenchuang_2x1",   "白被单人床(横) @7,4"),
    ("Interior.png", 24, "xiaozhuo_2x1",      "长条木案 @7,9"),
    ("Interior.png", 25, "deng_1x1",          "小圆凳 @0,10"),
    ("Interior.png", 27, "baxianzhuo_2x2",    "大圆桌 @6,10"),
    ("Interior.png", 38, "zhenglong_1x1",     "叠碗蒸笼 @5,14"),
    # ---- 1_Generic：木箱四态 @4~7,50 ----
    ("1_Generic_32x32.png", 24, "muxiang_1x1", "木箱(浅) @4,50"),
    ("1_Generic_32x32.png", 25, "muxiang_1x1", "木箱(米) @5,50"),
    ("1_Generic_32x32.png", 26, "muxiang_1x1", "木箱(黄) @6,50"),
    ("1_Generic_32x32.png", 27, "muxiang_1x1", "木箱(白) @7,50"),
    # ---- 12_Kitchen：碗柜/抽屉柜/酒瓶/水盆/水槽 ----
    ("12_Kitchen_32x32.png", 9,  "wangui_1x2",  "高碗柜(红) @4,11"),
    ("12_Kitchen_32x32.png", 11, "wangui_1x2",  "高碗柜(浅) @6,11"),
    ("12_Kitchen_32x32.png", 18, "gui_1x1",     "抽屉柜(棕) @0,12"),
    ("12_Kitchen_32x32.png", 19, "gui_1x1",     "抽屉柜(红) @1,12"),
    ("12_Kitchen_32x32.png", 20, "gui_1x1",     "抽屉柜(棕2) @2,12"),
    ("12_Kitchen_32x32.png", 14, "jiutan_1x1",  "酒瓶(蓝) @10,11"),
    ("12_Kitchen_32x32.png", 22, "jiutan_1x1",  "酒瓶(绿) @10,12"),
    ("12_Kitchen_32x32.png", 34, "shuipen_1x1", "白瓷大盆 @2,19"),
    ("12_Kitchen_32x32.png", 38, "shuichi_1x1", "大水槽 @2,21"),
    # ---- 3_Bathroom：蹲便器三态 ----
    ("3_Bathroom_32x32.png", 19, "dunbianqi_1x2", "蹲便器(黄) @8,12"),
    ("3_Bathroom_32x32.png", 20, "dunbianqi_1x2", "蹲便器(蓝) @9,12"),
    ("3_Bathroom_32x32.png", 21, "dunbianqi_1x2", "蹲便器(灰) @10,12"),
    # ---- 2_LivingRoom：三只陶罐 @0~2,9 ----
    ("2_LivingRoom_32x32.png", 3, "shuigang_1x1", "陶罐(素) @0,9"),
    ("2_LivingRoom_32x32.png", 4, "shuigang_1x1", "陶罐(黄) @1,9"),
    ("2_LivingRoom_32x32.png", 5, "shuigang_1x1", "陶罐(蓝) @2,9"),
    # ---- 5_Classroom_and_library：书架/柜/讲台 ----
    ("5_Classroom_and_library_32x32.png", 0,  "shujia_2x2",  "彩色大书架 @1,0"),
    ("5_Classroom_and_library_32x32.png", 9,  "shujia_1x2",  "梯架书架(空) @0,4"),
    ("5_Classroom_and_library_32x32.png", 10, "shujia_1x2",  "梯架书架(书) @1,4"),
    ("5_Classroom_and_library_32x32.png", 11, "gui_1x2",     "书柜(绿格) @0,7"),
    ("5_Classroom_and_library_32x32.png", 14, "gui_1x2",     "叠层箱柜(黄) @12,10"),
    ("5_Classroom_and_library_32x32.png", 15, "shuzhuo_2x1", "横置木柜 @13,10"),
    # ---- 4_Bedroom：双格木柜三态 ----
    ("4_Bedroom_32x32.png", 24, "gui_2x1", "双格木柜(米) @0,31"),
    ("4_Bedroom_32x32.png", 26, "gui_2x1", "双格木柜(棕) @0,33"),
    ("4_Bedroom_32x32.png", 28, "gui_2x1", "双格木柜(浅) @0,35"),
    # ---- 7_Art：画凳三态 + 木台 ----
    ("7_Art_32x32.png", 10, "deng_1x1",  "画凳(米) @3,2"),
    ("7_Art_32x32.png", 11, "deng_1x1",  "画凳(橙) @5,2"),
    ("7_Art_32x32.png", 12, "deng_1x1",  "画凳(浅) @7,2"),
    ("7_Art_32x32.png", 16, "anban_2x1", "木台(浅) @3,4"),
    ("7_Art_32x32.png", 17, "anban_2x1", "木台(橙) @5,4"),
    # ---- 11_Halloween：蜡烛 + 挂画 ----
    ("11_Halloween_32x32.png", 17, "denglong_1x1", "烛台 @0,4"),
    ("11_Halloween_32x32.png", 19, "paiwei_1x1",   "挂画(竖) @11,4"),
    # ---- 10_Birthday_party：长条供桌 ----
    ("10_Birthday_party_32x32.png", 15, "xiaozhuo_2x1", "长条供桌 @3,2"),
    # ---- 9_Fishing / 12_Kitchen：灶台变体 ----
    ("9_Fishing_32x32.png", 25, "chaihuozao_1x1", "深灶 @8,9"),
    ("12_Kitchen_32x32.png", 30, "chaihuozao_1x1", "小灶 @2,16"),
    # ---- 第二批：Interiors / Classroom / Kitchen / Art / Birthday 里的确定件 ----
    ("5_Classroom_and_library_32x32.png", 1, "shujia_2x2", "大书架(带书) @3,0"),
    ("5_Classroom_and_library_32x32.png", 6, "gui_1x2",    "窄药柜 @5,2"),
    ("Interiors 13_768x768_TILESETS_B_C_D_E.png", 1, "shujia_2x2", "木架图书 @3,11"),
    ("Interiors 16_768x768_TILESETS_B_C_D_E.png", 7, "jiutan_1x1", "高瓶 @14,19"),
    ("12_Kitchen_32x32.png", 23, "anban_2x1", "长条案板 @0,13"),
    ("12_Kitchen_32x32.png", 31, "anban_2x1", "厨房长台 @0,17"),
    ("7_Art_32x32.png", 8,  "penjing_1x1", "盆景(绿叶) @0,2"),
    ("7_Art_32x32.png", 14, "penjing_1x1", "盆景(茂) @0,4"),
    ("10_Birthday_party_32x32.png", 12, "changdeng_1x2", "烛行长凳 @5,1"),
]


def load_cands():
    return json.load(open(os.path.join(LAB, "_cls_atlas_cands.json"), encoding="utf-8"))


def load_manifest_footprints():
    """manifest 里每个 props id 的权威占地（格）：w × h。"""
    man = json.load(open(os.path.join(ROOT, "_ref", "art", "_assets_a1a3",
                                     "_a1a3_assets.json"), encoding="utf-8"))
    out = {}
    for p in man["props"]:
        out[p["id"]] = (int(p["w"]), int(p["h"]))
    return out


def crop_candidate(src_im, c):
    """按候选框裁出，再取紧内容包围盒（去掉透明留白）。

    关键：32 网格吸附框会**放大**占地（小圆凳落在 1×2 框里，内容其实只占 1 格），
    所以真实占地一律以 manifest 为准，网格框只用来定位。
    """
    reg = src_im.crop((c["x0"], c["y0"], c["x1"], c["y1"]))
    bb = reg.getbbox()
    return reg.crop(bb) if bb else reg


def adapt(cut, gw, gh):
    """把紧内容贴进 manifest 权威画布：画布 = 占地宽×32 × (占地高×32+32)，内容居中且贴底。

    不做重采样 —— 与 A 档保持源像素 1:1（同学手绘多为原尺寸单件图，
    放大只会破坏像素边缘）。
    """
    ow, oh = gw * TILE, gh * TILE + TILE
    if cut.size[0] > ow or cut.size[1] > oh:
        raise ValueError("oversize content %dx%d > canvas %dx%d" % (cut.size[0], cut.size[1], ow, oh))
    canvas = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    x = (ow - cut.size[0]) // 2
    canvas.alpha_composite(cut, (x, oh - cut.size[1]))
    return canvas


def main():
    cands = load_cands()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(VAR, exist_ok=True)
    src_cache = {}
    rows = []
    used = {}

    # A 档已经产出过的主图 id —— B 档同 id 一律降级为变体，不覆盖 A 档成果
    a_map_path = os.path.join(LAB, "_cls_map_a.json")
    a_ids = set()
    if os.path.exists(a_map_path):
        a_map = json.load(open(a_map_path, encoding="utf-8"))
        for r in a_map["rows"]:
            if r["role"] == "主图":
                a_ids.add(r["id"])
    print("A 档已占主图的 id（%d）: %s" % (len(a_ids), ", ".join(sorted(a_ids))))
    fp = load_manifest_footprints()

    for atlas, idx, pid, note in PICK:
        lst = [c for c in cands[atlas] if c["gw"] <= 2 and c["gh"] <= 2]
        c = lst[idx]
        if atlas not in src_cache:
            src_cache[atlas] = Image.open(os.path.join(SRC, atlas)).convert("RGBA")
        cut = crop_candidate(src_cache[atlas], c)
        # 占地一律取 manifest 权威值；manifest 里没有的 id 跳过（需先加 id）
        if pid not in fp:
            print("  [跳过] %s#%d 目标 id %s 不在 manifest" % (atlas, idx, pid))
            continue
        gw, gh = fp[pid]
        if cut.size[0] > gw * TILE or cut.size[1] > gh * TILE + TILE:
            print("  [跳过] %s#%d 内容 %dx%d 超出 %s 画布 %dx%d" % (
                atlas, idx, cut.size[0], cut.size[1], pid, gw * TILE, gh * TILE + TILE))
            continue
        im = adapt(cut, gw, gh)
        n = used.get(pid, 0)
        used[pid] = n + 1
        if n == 0 and pid not in a_ids:
            path = os.path.join(OUT, "%s.png" % pid)
            role = "主图"
        else:
            path = os.path.join(VAR, "%s__%s_%d.png" % (pid, atlas.replace(".png", "").replace(" ", "_"), idx))
            role = "变体"
        im.save(path)
        rows.append({"atlas": atlas, "idx": idx, "id": pid, "note": note, "role": role,
                     "gw": gw, "gh": gh,
                     "out": os.path.relpath(path, ROOT).replace(os.sep, "/"),
                     "src_box": [c["x0"], c["y0"], c["x1"], c["y1"]]})

    with open(os.path.join(LAB, "_cls_map_b.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)

    # ---- 确认接触表 ----
    COLS, CELL, Z = 8, 170, 3
    rowsn = (len(rows) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * CELL, rowsn * CELL), (30, 30, 38))
    d = ImageDraw.Draw(sheet)
    for i, r in enumerate(rows):
        p = os.path.join(ROOT, r["out"].replace("/", os.sep))
        im = Image.open(p).convert("RGBA")
        S = max(1, min(Z, int((CELL - 46) / max(im.size))))
        im2 = im.resize((im.width * S, im.height * S), Image.NEAREST)
        bg = Image.new("RGBA", im2.size, (92, 92, 108, 255))
        bg.alpha_composite(im2)
        gx, gy = (i % COLS) * CELL, (i // COLS) * CELL
        sheet.paste(bg.convert("RGB"), (gx + (CELL - bg.width) // 2, gy + 32 + (CELL - 32 - bg.height) // 2))
        d.rectangle([gx + 2, gy + 2, gx + CELL - 3, gy + CELL - 3], outline=(70, 70, 86))
        d.text((gx + 5, gy + 5), "%s %dx%d" % (r["id"], r["gw"], r["gh"]), fill=(255, 225, 140))
        d.text((gx + 5, gy + 17), "%s#%d %s" % (r["atlas"][:12], r["idx"], r["role"]), fill=(150, 220, 255))
    sheet.save(os.path.join(LAB, "_cls_pick_check.png"))
    print("切出 %d 件，落盘主图 %d / 变体 %d" % (
        len(rows),
        sum(1 for r in rows if r["role"] == "主图"),
        sum(1 for r in rows if r["role"] == "变体")))
    for r in rows:
        print("  %-4s %-42s #%-3d -> %-20s %s" % (r["role"], r["atlas"], r["idx"], r["id"], r["out"]))


if __name__ == "__main__":
    main()
