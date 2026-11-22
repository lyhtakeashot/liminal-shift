# -*- coding: utf-8 -*-
"""美术同学资产 → 游戏可用资产：A 档（单件家具）适配生成。

规格依据 DECIDE D6：
  - 交付画布 = 占地宽×32 × (占地高×32 + 32)
  - 内容贴底对齐，顶部留透明（多出的一格做立面区）
  - 同学源图上下都有透明留白，先裁透明边再贴底

产出：
  assets/village/_classmate/props/<id>.png          主图（每个 id 一张）
  assets/village/_classmate/props/_variants/...      同 id 的其余变体（不覆盖主图）
  lab/_cls_map_a.json                              映射数据（供文档生成）
"""
import json
import os

from PIL import Image

ROOT = r"D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift"
SRC = os.path.join(ROOT, "美术资产", "家具")
OUT = os.path.join(ROOT, "assets", "village", "_classmate", "props")
VAR = os.path.join(OUT, "_variants")
TILE = 32

# (源相对路径, manifest id, 宽格, 高格, 置信度, 备注)
# 同 id 多张源图：第一张 = 主图，其余进 _variants
MAP = [
    ("柴缸灶/Sprite-水缸1.png",  "shuigang_1x1",     1, 1, "高", "陶水缸，院内蓄水"),
    ("柴缸灶/Sprite-柴火灶.png", "chaihuozao_1x1",   1, 1, "高", "柴火灶，一口锅"),
    ("柴缸灶/Sprite-柴堆.png",  "chaidui_1x1",      1, 1, "高", "柴堆"),
    ("柴缸灶/Sprite-茅坑.png",  "maokeng_1x1",      1, 1, "高", "茅坑（坑口）"),
    ("床/Sprite-床1.png",       "danrenchuang_1x2", 1, 2, "高", "红被单床"),
    ("床/Sprite-床2.png",       "danrenchuang_1x2", 1, 2, "高", "米色被褥床（变体）"),
    ("床/Sprite-床3.png",       "danrenchuang_1x2", 1, 2, "高", "蓝被床（变体）"),
    ("床/Sprite-大床1.png",     "shuangrenchuang_2x2", 2, 2, "高", "双人大床（米色）"),
    ("床/Sprite-大床2.png",     "shuangrenchuang_2x2", 2, 2, "高", "双人大床（蓝被，变体）"),
    ("柜子/Sprite-柜子1.png",   "gui_1x2",          1, 2, "中", "四层抽屉竖柜"),
    ("柜子/Sprite-柜子2.png",   "gui_1x1",          1, 1, "高", "两层抽屉矮柜（NEW id）"),
    ("箱子/Sprite-箱子1.png",   "muxiang_1x1",      1, 1, "高", "木箱"),
    ("箱子/Sprite-箱子2.png",   "luokuang_1x1",     1, 1, "中", "竹编扁箩筐（变体）"),
    ("箱子/Sprite-箱子3.png",   "luokuang_1x1",     1, 1, "中", "竹编圆箩筐（主图）"),
    ("椅子/Sprite-短椅1.png",   "yi_1x1",           1, 1, "高", "带靠背木椅"),
    ("椅子/Sprite-短椅2.png",   "deng_1x1",         1, 1, "中", "圆草墩（当凳）"),
    ("桌子/Sprite-短桌1.png",   "xiaozhuo_1x1",     1, 1, "高", "素木小方桌（NEW id）"),
    ("桌子/Sprite-短桌2.png",   "hongzhuo_1x1",     1, 1, "高", "铺红绸方桌/喜桌（NEW id）"),
    ("桌子/Sprite-短桌3.png",   "shuzhuo_1x1_top",  1, 1, "中", "俯视书桌，桌上摊纸笔（NEW id）"),
    ("桌子/Sprite-短桌4.png",   "baizhuo_1x1",      1, 1, "高", "铺白桌布方桌/供桌（NEW id）"),
    ("桌子/Sprite-书桌1.png",   "shuzhuo_1x1",      1, 1, "高", "带抽屉书桌，摊开书册"),
    ("桌子/Sprite-长桌1.png",   "changzhuo_2x1",    2, 1, "高", "长条木桌 2 格（NEW id）"),
    ("桌子/Sprite-餐桌1.png",   "cantang_3x1",      3, 1, "高", "整套餐桌：长桌+两小凳（NEW id）"),
]

# manifest 里需要新增的 id（用户拍板：加新 id）
NEW_IDS = {
    "xiaozhuo_1x1":    ("小方桌", "素木小方桌，无装饰"),
    "hongzhuo_1x1":    ("红绸桌", "铺红绸的方桌（喜桌/祭桌）"),
    "baizhuo_1x1":     ("白布桌", "铺白桌布的方桌（供桌）"),
    "shuzhuo_1x1_top": ("书桌(俯视)", "俯视角度的书桌，桌上摊纸笔"),
    "gui_1x1":         ("矮柜", "两层抽屉矮柜，1×1 占地"),
    "changzhuo_2x1":   ("长桌", "长条木桌，2×1 占地"),
    "cantang_3x1":     ("餐桌", "长桌+两侧小凳的整套餐桌，3×1 占地"),
}


def adapt(src_rel, pid, gw, gh):
    """裁透明边 → 贴底 → 输出 (w*32) × (h*32+32) 画布。返回 (im, 统计)。"""
    sp = os.path.join(SRC, src_rel.replace("/", os.sep))
    im = Image.open(sp).convert("RGBA")
    ow, oh = gw * TILE, gh * TILE + TILE
    bbox = im.getbbox()
    if bbox is None:
        raise ValueError("empty: %s" % src_rel)
    cut = im.crop(bbox)
    cw, ch = cut.size
    if cw > ow or ch > oh:
        raise ValueError("oversize %s %dx%d > %dx%d" % (src_rel, cw, ch, ow, oh))
    canvas = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    x = (ow - cw) // 2
    canvas.alpha_composite(cut, (x, oh - ch))
    return canvas, {"src_size": list(im.size), "content": [cw, ch],
                    "out_size": [ow, oh], "left_gap": x, "right_gap": ow - x - cw}


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(VAR, exist_ok=True)
    seen = {}
    rows = []
    for src_rel, pid, gw, gh, conf, note in MAP:
        im, st = adapt(src_rel, pid, gw, gh)
        if pid in seen:
            # 同 id 的第二张起 → 变体
            stem = os.path.splitext(os.path.basename(src_rel))[0]
            vp = os.path.join(VAR, "%s__%s.png" % (pid, stem))
            im.save(vp)
            role = "变体"
            outp = os.path.relpath(vp, ROOT).replace(os.sep, "/")
        else:
            seen[pid] = True
            op = os.path.join(OUT, "%s.png" % pid)
            im.save(op)
            role = "主图"
            outp = os.path.relpath(op, ROOT).replace(os.sep, "/")
        rows.append({"src": "美术资产/家具/" + src_rel, "id": pid, "gw": gw, "gh": gh,
                     "conf": conf, "note": note, "role": role, "out": outp, **st})
        print("%-6s %-18s %-22s %s" % (role, pid, outp, st["out_size"]))

    with open(os.path.join(ROOT, "lab", "_cls_map_a.json"), "w", encoding="utf-8") as f:
        json.dump({"rows": rows, "new_ids": NEW_IDS}, f, ensure_ascii=False, indent=1)
    print("\n主图 %d / 变体 %d / 新 id %d" % (
        sum(1 for r in rows if r["role"] == "主图"),
        sum(1 for r in rows if r["role"] == "变体"), len(NEW_IDS)))


if __name__ == "__main__":
    main()
