# -*- coding: utf-8 -*-
"""生成 A1–A3 全部 84 件家具 props。

交付口径（docs/PROMPT-stardew-art-exec.md §2.2 + docs/DECIDE-stardew-visual.md D6）：
  画布 = 占地宽×32 宽 × (占地高×32 + 32) 高；多出的 32px 在**顶部**（物件立起来的高度）。
  锚点 = 底部中心；占地/碰撞读 _ref/houses/houses_data.json，**不看 PNG 像素**。

§5.5 五个坑（docs/art-assets-a1a3.md:296-302）：
  1. 高度可以多画一格 ✔（画布高 = 占地高 + 32）
  2. 多出来的一格往**上**长 ✔（所有坐标以「离地高度 d」推算，不往下溢出画布）
  3. 不画地板 / 墙体 ✔（本文件只画物件本身）
  4. 茅房与茅坑是两个文件 ✔（maofang_3x2 / maokeng_1x1 各画各的）
  5. 立面不画细节 ✔（只用色阶分层：顶部亮带 + 主色 + 底部暗带）

画法约定：3/4 俯视 —— 顶面是梯形，正面是矩形，右侧压暗。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pixel_lib import Canvas, TILE, PAL, mix  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
MANIFEST = os.path.join(ROOT, "_ref", "art", "_assets_a1a3", "_a1a3_assets.json")
OUT_DIR = os.path.join(ROOT, "assets", "village", "props")


# ------------------------------------------------------------------ 画法小工具
def R(cv, x0, y0, x1, y1, c):
    """矩形（左上右下，**右/下不含**）。"""
    if x1 > x0 and y1 > y0:
        cv.rect(x0, y0, x1 - 1, y1 - 1, c)


def B(cv, x0, y0, x1, y1, c, w=1):
    """描边矩形。"""
    if x1 > x0 and y1 > y0:
        cv.box(x0, y0, x1 - 1, y1 - 1, c, w)


def TR(cv, x0, y0, x1, y1, ins, c):
    """梯形顶面：上窄下宽。"""
    cv.poly([(x0 + ins, y0), (x1 - 1 - ins, y0), (x1 - 1, y1 - 1), (x0, y1 - 1)], c)


def EL(cv, x0, y0, x1, y1, c):
    cv.ellipse(x0, y0, x1 - 1, y1 - 1, c)


def sh(cv, cx, y, rx, alpha=80):
    """脚下投影。"""
    cv.shadow_ellipse(cx, y, max(3, rx), 3, alpha=alpha)


def band(cv, x0, y0, x1, y1, c):
    """立面分层：顶亮带 + 底暗带（不画细节）。"""
    R(cv, x0, y0, x1, y0 + 2, c[0])
    R(cv, x0, y1 - 3, x1, y1, c[3])
    R(cv, x0, y1 - 5, x1, y1 - 3, c[2])


def wood_of(pal, seed=0):
    return PAL[pal]


# ================================================================== 坐具
def p_stool(cv, W, H, n=1, pal="wood"):
    """圆凳（可多只沿纵深排开）。"""
    for k in range(n):
        d = k * 30
        w = 30 - k * 2
        x0 = (W - w) // 2
        yb = H - d
        R(cv, x0 + 3, yb - 26, x0 + w - 3, yb - 19, PAL[pal][2])          # 凳身侧
        EL(cv, x0, yb - 30, x0 + w, yb - 18, PAL[pal][1])                 # 座面
        EL(cv, x0 + 2, yb - 28, x0 + w - 2, yb - 21, PAL[pal][0])
        R(cv, x0 + 5, yb - 21, x0 + 10, yb, PAL[pal][3])                 # 左腿
        R(cv, x0 + w - 10, yb - 21, x0 + w - 5, yb, PAL[pal][3])         # 右腿
        R(cv, x0 + 5, yb - 13, x0 + w - 5, yb - 10, PAL[pal][2])         # 横枨
        sh(cv, x0 + w // 2, yb - 1, w // 2 - 1)


def p_bench(cv, W, H, n=1):
    """长条凳（平板面 + 两条腿）。"""
    for k in range(n):
        d = k * 30
        w = W - 6 - k * 2
        x0 = (W - w) // 2
        yb = H - d
        TR(cv, x0, yb - 24, x0 + w, yb - 18, 2, PAL["wood"][1])
        R(cv, x0, yb - 18, x0 + w, yb - 14, PAL["wood_d"][2])
        R(cv, x0 + 3, yb - 14, x0 + 8, yb, PAL["wood_d"][3])
        R(cv, x0 + w - 8, yb - 14, x0 + w - 3, yb, PAL["wood_d"][3])
        sh(cv, x0 + w // 2, yb - 1, w // 2 - 2)


def p_chair(cv, W, H, n=1):
    """椅：座板 + 高靠背（竖棂）。"""
    for k in range(n):
        d = k * 30
        w = 26 - k * 2
        x0 = (W - w) // 2
        yb = H - d
        R(cv, x0 + 2, yb - 56, x0 + w - 2, yb - 44, PAL["wood_d"][2])   # 靠背板
        R(cv, x0 + 4, yb - 52, x0 + w - 4, yb - 48, PAL["wood"][1])
        R(cv, x0 + 3, yb - 42, x0 + w - 3, yb - 38, PAL["wood_d"][3])   # 靠背立柱
        TR(cv, x0, yb - 38, x0 + w, yb - 32, 2, PAL["wood"][1])         # 座面
        R(cv, x0, yb - 32, x0 + w, yb - 28, PAL["wood_d"][2])
        R(cv, x0 + 3, yb - 28, x0 + 7, yb, PAL["wood_d"][3])
        R(cv, x0 + w - 7, yb - 28, x0 + w - 3, yb, PAL["wood_d"][3])
        sh(cv, x0 + w // 2, yb - 1, w // 2 - 1)


def p_rattan(cv, W, H, n=1):
    """藤椅：编织座 + 弯背（浅色）。"""
    for k in range(n):
        d = k * 30
        w = 28 - k * 2
        x0 = (W - w) // 2
        yb = H - d
        R(cv, x0 + 2, yb - 52, x0 + w - 2, yb - 40, PAL["thatch"][2])    # 靠背
        for i in range(4):
            R(cv, x0 + 4 + i * 6, yb - 50, x0 + 7 + i * 6, yb - 42, PAL["thatch"][0])
        TR(cv, x0, yb - 36, x0 + w, yb - 30, 2, PAL["thatch"][1])        # 座面
        for i in range(4):
            R(cv, x0 + 3 + i * 6, yb - 34, x0 + 4 + i * 6, yb - 31, PAL["thatch"][3])
        R(cv, x0, yb - 30, x0 + w, yb - 27, PAL["wood_d"][2])
        R(cv, x0 + 3, yb - 27, x0 + 7, yb, PAL["wood_d"][3])
        R(cv, x0 + w - 7, yb - 27, x0 + w - 3, yb, PAL["wood_d"][3])
        sh(cv, x0 + w // 2, yb - 1, w // 2 - 1)


# ================================================================== 桌案
def _table(cv, W, H, tw, top_h, face_h, leg_h, pal="wood", apron=True):
    """通用方桌：顶面梯形 + 围板 + 四腿。"""
    x0 = (W - tw) // 2
    yb = H
    TR(cv, x0, yb - top_h - face_h - leg_h, x0 + tw, yb - face_h - leg_h, 3, PAL[pal][1])
    R(cv, x0 + 3, yb - top_h - face_h - leg_h, x0 + tw - 3, yb - top_h - face_h - leg_h + 2,
      PAL[pal][0])                                                   # 顶面高光
    R(cv, x0, yb - face_h - leg_h, x0 + tw, yb - leg_h, PAL[pal][2])   # 围板/正面
    R(cv, x0, yb - face_h - leg_h, x0 + tw, yb - face_h - leg_h + 2, PAL[pal][0])
    R(cv, x0, yb - leg_h, x0 + tw, yb - leg_h + 3, PAL[pal][3])
    R(cv, x0 + 3, yb - leg_h, x0 + 8, yb, PAL[pal][3])
    R(cv, x0 + tw - 8, yb - leg_h, x0 + tw - 3, yb, PAL[pal][3])
    R(cv, x0 + 10, yb - leg_h, x0 + tw - 10, yb, PAL[pal][3])


def p_baxian_2x3(cv, W, H):
    """八仙桌（大，2×3 占地）：厚桌面 + 四腿 + 围板。"""
    _table(cv, W, H, W - 8, 16, 10, 26)
    R(cv, W // 2 - 6, H - 26 - 10 - 16, W // 2 + 6, H - 26 - 10 - 16 + 3, PAL["paper"][1])
    sh(cv, W // 2, H - 1, W // 2 - 4)


def p_baxian_2x2(cv, W, H):
    """八仙桌（2×2）。"""
    _table(cv, W, H, W - 10, 14, 9, 22)
    sh(cv, W // 2, H - 1, W // 2 - 4)


def p_xiaozhuo(cv, W, H):
    """小桌（2×1）：抽屉留一道缝，缝里露一角纸。"""
    x0, x1 = 4, W - 4
    yb = H
    TR(cv, x0, yb - 34, x1, yb - 26, 3, PAL["wood"][1])
    R(cv, x0 + 3, yb - 34, x1 - 3, yb - 32, PAL["wood"][0])
    R(cv, x0, yb - 26, x1, yb - 8, PAL["wood_d"][2])
    R(cv, x0 + 2, yb - 24, x1 - 2, yb - 12, PAL["wood"][1])          # 抽屉面
    R(cv, x0 + 2, yb - 14, x1 - 2, yb - 12, PAL["ink"][2])            # 抽屉缝
    R(cv, x0 + 2, yb - 14, x1 - 12, yb - 11, PAL["paper"][0])        # 露出的纸角
    R(cv, x1 - 16, yb - 18, x1 - 12, yb - 15, PAL["brass"][1])        # 抽屉拉手
    R(cv, x0 + 3, yb - 8, x0 + 7, yb, PAL["wood_d"][3])
    R(cv, x1 - 7, yb - 8, x1 - 3, yb, PAL["wood_d"][3])
    sh(cv, W // 2, yb - 1, W // 2 - 4)


def p_shuzhuo(cv, W, H, tall=False):
    """书桌：桌面 + 摊开的书 + 笔 + 砚台。"""
    x0, x1 = 3, W - 3
    yb = H
    top = 44 if tall else 36
    TR(cv, x0, yb - top, x1, yb - top + 9, 3, PAL["wood"][1])
    R(cv, x0 + 3, yb - top, x1 - 3, yb - top + 2, PAL["wood"][0])
    R(cv, x0, yb - top + 9, x1, yb - 10, PAL["wood_d"][2])
    R(cv, x0 + 3, yb - top + 11, x0 + 18, yb - top + 22, PAL["paper"][0])   # 摊开的书
    R(cv, x0 + 3, yb - top + 11, x0 + 18, yb - top + 13, PAL["paper"][2])
    R(cv, x0 + 21, yb - top + 12, x0 + 28, yb - top + 16, PAL["ink"][2])    # 砚台
    R(cv, x0 + 21, yb - top + 12, x0 + 25, yb - top + 14, PAL["ink"][1])
    R(cv, x1 - 10, yb - top + 13, x1 - 6, yb - top + 15, PAL["wood_l"][1])  # 笔
    R(cv, x0 + 3, yb - 10, x0 + 7, yb, PAL["wood_d"][3])
    R(cv, x1 - 7, yb - 10, x1 - 3, yb, PAL["wood_d"][3])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_zhangzhuo(cv, W, H, tall=False):
    """账桌：长条案 + 摊开的账簿 + 算盘（线索：假《水簿》）。"""
    x0, x1 = 2, W - 2
    yb = H
    top = 52 if tall else 38
    TR(cv, x0, yb - top, x1, yb - top + 10, 3, PAL["wood"][1])
    R(cv, x0 + 3, yb - top, x1 - 3, yb - top + 2, PAL["wood"][0])
    R(cv, x0, yb - top + 10, x1, yb - 8, PAL["wood_d"][2])
    R(cv, x0 + 2, yb - top + 12, x0 + 17, yb - top + 26, PAL["paper"][0])   # 账簿
    R(cv, x0 + 2, yb - top + 12, x0 + 17, yb - top + 14, PAL["paper"][2])
    for i in range(4):
        R(cv, x0 + 4, yb - top + 16 + i * 2, x0 + 15, yb - top + 17 + i * 2, PAL["paper"][2])
    R(cv, x0 + 20, yb - top + 13, x0 + 34, yb - top + 19, PAL["wood_l"][1])  # 算盘框
    R(cv, x0 + 21, yb - top + 14, x0 + 33, yb - top + 18, PAL["ink"][1])
    R(cv, x0 + 3, yb - 8, x0 + 7, yb, PAL["wood_d"][3])
    R(cv, x1 - 7, yb - 8, x1 - 3, yb, PAL["wood_d"][3])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_tiaoan(cv, W, H):
    """条案：竖向长条桌，摆瓶 + 座钟 + 镜。"""
    x0, x1 = 3, W - 3
    yb = H
    TR(cv, x0, yb - 56, x1, yb - 48, 2, PAL["wood"][1])
    R(cv, x0 + 2, yb - 56, x1 - 2, yb - 54, PAL["wood"][0])
    R(cv, x0, yb - 48, x1, yb - 12, PAL["wood_d"][2])
    R(cv, x0 + 1, yb - 46, x1 - 1, yb - 44, PAL["wood"][1])
    R(cv, x0 + 3, yb - 12, x0 + 7, yb, PAL["wood_d"][3])
    R(cv, x1 - 7, yb - 12, x1 - 3, yb, PAL["wood_d"][3])
    R(cv, x0 + 4, yb - 64, x0 + 12, yb - 56, PAL["porc"][1])         # 瓷瓶
    R(cv, x0 + 5, yb - 62, x0 + 11, yb - 58, PAL["porc"][0])
    R(cv, x1 - 14, yb - 66, x1 - 4, yb - 56, PAL["wood_d"][2])        # 座钟
    R(cv, x1 - 12, yb - 63, x1 - 6, yb - 58, PAL["paper"][1])
    R(cv, x0 + 14, yb - 62, x0 + 20, yb - 56, PAL["glass"][1])        # 镜
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_anban(cv, W, H):
    """案板：厚木板 + 插着的菜刀。"""
    x0, x1 = 2, W - 2
    yb = H
    TR(cv, x0, yb - 30, x1, yb - 22, 2, PAL["wood_l"][1])
    R(cv, x0, yb - 22, x1, yb - 12, PAL["wood_l"][2])
    R(cv, x0, yb - 22, x1, yb - 20, PAL["wood_l"][0])
    R(cv, x0 + 6, yb - 12, x0 + 11, yb, PAL["wood_d"][3])
    R(cv, x1 - 11, yb - 12, x1 - 6, yb, PAL["wood_d"][3])
    R(cv, x0 + 18, yb - 38, x0 + 34, yb - 30, PAL["metal"][1])        # 刀身
    R(cv, x0 + 18, yb - 38, x0 + 34, yb - 36, PAL["metal"][0])
    R(cv, x0 + 12, yb - 36, x0 + 19, yb - 31, PAL["wood_d"][2])       # 刀柄
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_shizhuo(cv, W, H):
    """石桌：圆桌面 + 石凳。"""
    yb = H
    EL(cv, 4, yb - 34, W - 4, yb - 20, PAL["stone"][1])
    EL(cv, 6, yb - 32, W - 6, yb - 22, PAL["stone"][0])
    R(cv, 6, yb - 24, W - 6, yb - 18, PAL["stone"][2])
    R(cv, W // 2 - 5, yb - 20, W // 2 + 5, yb, PAL["stone"][3])
    EL(cv, W - 20, yb - 16, W - 6, yb - 6, PAL["stone"][1])            # 石凳
    EL(cv, W - 18, yb - 15, W - 8, yb - 8, PAL["stone"][0])
    R(cv, W - 17, yb - 9, W - 15, yb, PAL["stone"][3])
    R(cv, W - 9, yb - 9, W - 7, yb, PAL["stone"][3])
    sh(cv, W // 2, yb - 1, W // 2 - 4)


def p_bianmin(cv, W, H):
    """便民服务台：长条台 + 凉茶桶 + 小牌。"""
    x0, x1 = 2, W - 2
    yb = H
    TR(cv, x0, yb - 40, x1, yb - 32, 3, PAL["wood"][1])
    R(cv, x0, yb - 32, x1, yb - 12, PAL["wood_d"][2])
    R(cv, x0 + 2, yb - 30, x1 - 2, yb - 26, PAL["cloth_r"][1])        # 红布
    R(cv, x0 + 3, yb - 12, x0 + 8, yb, PAL["wood_d"][3])
    R(cv, x1 - 8, yb - 12, x1 - 3, yb, PAL["wood_d"][3])
    R(cv, x0 + 5, yb - 50, x0 + 17, yb - 38, PAL["wood_l"][2])        # 茶桶
    EL(cv, x0 + 5, yb - 50, x0 + 17, yb - 44, PAL["wood_l"][1])
    R(cv, x0 + 16, yb - 58, x0 + 19, yb - 44, PAL["wood_d"][2])       # 瓢
    R(cv, x1 - 16, yb - 52, x1 - 5, yb - 40, PAL["paper"][1])        # 小牌
    R(cv, x1 - 16, yb - 52, x1 - 5, yb - 50, PAL["paper"][2])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_yanliangtai(cv, W, H):
    """验粮台：木台 + 粮袋 + 插着的取样铁管。"""
    x0, x1 = 2, W - 2
    yb = H
    TR(cv, x0, yb - 34, x1, yb - 26, 3, PAL["wood"][1])
    R(cv, x0, yb - 26, x1, yb - 10, PAL["wood_d"][2])
    R(cv, x0 + 3, yb - 10, x0 + 8, yb, PAL["wood_d"][3])
    R(cv, x1 - 8, yb - 10, x1 - 3, yb, PAL["wood_d"][3])
    EL(cv, x0 + 4, yb - 44, x0 + 22, yb - 32, PAL["paper"][2])        # 粮袋
    EL(cv, x0 + 6, yb - 42, x0 + 20, yb - 34, PAL["paper"][0])
    R(cv, x1 - 20, yb - 52, x1 - 16, yb - 34, PAL["metal"][1])        # 铁管
    R(cv, x1 - 20, yb - 52, x1 - 18, yb - 34, PAL["metal"][0])
    R(cv, x1 - 22, yb - 30, x1 - 14, yb - 26, PAL["metal"][2])       # 管口
    sh(cv, W // 2, yb - 1, W // 2 - 3)


# ================================================================== 柜架
def _cabinet(cv, W, H, body_h, tw, doors=2, pal="wood_d", open_shelf=False):
    x0 = (W - tw) // 2
    yb = H
    body_h = min(body_h, H - 6)          # 画布只有「占地高 + 1 格」，别画出去
    TR(cv, x0, yb - body_h, x0 + tw, yb - body_h + 6, 2, PAL[pal][1])
    R(cv, x0, yb - body_h + 6, x0 + tw, yb, PAL[pal][2])
    R(cv, x0, yb - body_h + 6, x0 + tw, yb - body_h + 8, PAL[pal][0])
    R(cv, x0, yb - 5, x0 + tw, yb, PAL[pal][3])
    if open_shelf:
        for r in range(3):
            yy = yb - body_h + 12 + r * 12
            R(cv, x0 + 3, yy, x0 + tw - 3, yy + 3, PAL["wood"][2])
            R(cv, x0 + 3, yy + 3, x0 + tw - 3, yy + 11, PAL["ink"][2])
            for i in range(3):
                cx = x0 + 5 + i * 8
                R(cv, cx, yy + 4, cx + 6, yy + 10, PAL["porc"][1])
                EL(cv, cx, yy + 3, cx + 6, yy + 6, PAL["porc"][0])
    else:
        if doors > 0:
            seg = max(4, (tw - 6) // doors)
            for i in range(doors):
                dx = x0 + 3 + i * seg
                R(cv, dx, yb - body_h + 10, dx + seg - 2, yb - 7, PAL[pal][1])
                B(cv, dx, yb - body_h + 10, dx + seg - 2, yb - 7, PAL[pal][3], 1)
                R(cv, dx + seg - 5, yb - body_h + 26, dx + seg - 3, yb - body_h + 30,
                  PAL["brass"][1])
    return x0, tw


def p_yigui(cv, W, H):
    """衣柜（高，双开门）。"""
    _cabinet(cv, W, H, 88, W - 4, doors=2, pal="wood_d")
    sh(cv, W // 2, H - 1, W // 2 - 3)


def p_xiao_yigui(cv, W, H):
    _cabinet(cv, W, H, 74, W - 6, doors=1, pal="wood_d")
    sh(cv, W // 2, H - 1, W // 2 - 3)


def p_gui(cv, W, H):
    _cabinet(cv, W, H, 66, W - 4, doors=1, pal="wood_d")
    sh(cv, W // 2, H - 1, W // 2 - 3)


def p_wangui(cv, W, H):
    """碗柜：上层敞格放碗。"""
    _cabinet(cv, W, H, 70, W - 4, doors=2, pal="wood_d", open_shelf=True)
    sh(cv, W // 2, H - 1, W // 2 - 3)


def p_danjuji(cv, W, H):
    """单据柜 + 柜面算盘。"""
    x0, tw = _cabinet(cv, W, H, 30, W - 4, doors=2, pal="wood_d")
    yb = H
    R(cv, x0 + 5, yb - 44, x0 + 26, yb - 36, PAL["wood_l"][1])        # 算盘
    R(cv, x0 + 6, yb - 43, x0 + 25, yb - 38, PAL["ink"][1])
    for i in range(8):
        R(cv, x0 + 7 + i * 2, yb - 43, x0 + 8 + i * 2, yb - 38, PAL["wood_l"][2])
    R(cv, x0 + 4, yb - 36, x0 + 27, yb - 34, PAL["wood_l"][2])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_shujia(cv, W, H):
    """书架：几层格 + 彩色书脊。"""
    x0, tw = _cabinet(cv, W, H, 78, W - 4, doors=0, pal="wood_d")
    yb = H
    books = [PAL["cloth_r"][1], PAL["cloth_b"][1], PAL["paper"][2], PAL["wood_l"][1],
             PAL["leaf"][1], PAL["brick"][1]]
    n_shelf = max(1, (yb - 12) // 18)
    for r in range(n_shelf):
        yy = yb - 12 - (r + 1) * 18
        if yy < yb - H + 4:
            break
        R(cv, x0 + 2, yy, x0 + tw - 2, yy + 3, PAL["wood"][2])
        x = x0 + 3
        i = 0
        while x < x0 + tw - 6:
            bw = 3 + (i * 7) % 4
            R(cv, x, yy - 14, x + bw, yy, books[(i + r) % len(books)])
            R(cv, x, yy - 14, x + bw, yy - 12, PAL["ink"][1])
            x += bw + 1
            i += 1
    sh(cv, W // 2, yb - 1, W // 2 - 3)


# ================================================================== 床
def _bed(cv, W, H, tw, td, quilt="cloth_r", straw=False):
    yb = H
    x0 = (W - tw) // 2
    td = min(td, H - 12)
    top = yb - td
    TR(cv, x0, top, x0 + tw, top + 14, 4, PAL["wood"][1])             # 床架顶
    R(cv, x0 + 3, top + 3, x0 + tw - 3, yb - 8, PAL["wood"][2])      # 床板
    if straw:
        R(cv, x0 + 3, top + 3, x0 + tw - 3, yb - 8, PAL["thatch"][2])
        for i in range(8):
            xx = x0 + 4 + i * 5
            R(cv, xx, top + 5, xx + 2, yb - 10, PAL["thatch"][1])
    else:
        R(cv, x0 + 4, top + 5, x0 + tw - 4, yb - 10, PAL[quilt][1])   # 被面
        R(cv, x0 + 4, top + 5, x0 + tw - 4, top + 12, PAL[quilt][0])
        R(cv, x0 + 4, yb - 18, x0 + tw - 4, yb - 10, PAL[quilt][2])
        R(cv, x0 + 6, top + 6, x0 + 18, top + 14, PAL["white"][0])    # 枕头
        R(cv, x0 + 6, top + 6, x0 + 18, top + 8, PAL["white"][2])
    R(cv, x0, yb - 8, x0 + tw, yb, PAL["wood_d"][3])                 # 床沿
    R(cv, x0 + 2, yb - 8, x0 + 5, yb, PAL["wood_d"][2])
    R(cv, x0 + tw - 5, yb - 8, x0 + tw - 2, yb, PAL["wood_d"][2])
    sh(cv, W // 2, yb - 1, W // 2 - 4)


def p_danren_2x1(cv, W, H):
    _bed(cv, W, H, W - 6, 34, quilt="cloth_b")


def p_danren_1x2(cv, W, H):
    _bed(cv, W, H, W - 6, 58, quilt="cloth_b")


def p_shuangren_3x3(cv, W, H):
    _bed(cv, W, H, W - 8, 78, quilt="cloth_r")


def p_shuangren_2x2(cv, W, H):
    _bed(cv, W, H, W - 8, 56, quilt="cloth_r")


def p_jiu_muchuang(cv, W, H):
    """旧木床：草席烂成一堆。"""
    _bed(cv, W, H, W - 6, 56, straw=True)
    for i in range(5):
        R(cv, 4 + i * 5, H - 34, 7 + i * 5, H - 28, PAL["leaf_d"][2])


# ================================================================== 灶与厨
def p_zaotai(cv, W, H, tall=False):
    """灶台：砖砌 + 灶膛口 + 灶口锅 + 烟囱 + 柴。"""
    yb = H
    body = min(104 if tall else 62, H - 6)
    x0, x1 = 1, W - 1
    R(cv, x0, yb - body, x1, yb, PAL["brick"][2])
    for r in range(0, body - 6, 6):
        yy = yb - body + r
        R(cv, x0, yy, x1, yy + 1, PAL["brick"][3])
        off = 0 if (r // 6) % 2 else 8
        xx = x0 + off
        while xx < x1:
            R(cv, xx, yy, xx + 1, min(yb, yy + 6), PAL["brick"][3])
            xx += 16
    R(cv, x0, yb - body, x1, yb - body + 3, PAL["brick"][0])          # 灶面亮带
    EL(cv, x0 + 2, yb - body - 2, x1 - 2, yb - body + 10, PAL["brick"][1])  # 锅口
    EL(cv, x0 + 5, yb - body, x1 - 5, yb - body + 7, PAL["ink"][2])
    EL(cv, x0 + 7, yb - body + 1, x1 - 7, yb - body + 5, PAL["iron"][1])
    R(cv, x0 + 4, yb - body + 24, x1 - 4, yb - body + 8, PAL["ink"][3])   # 灶膛
    R(cv, x0 + 5, yb - body + 23, x1 - 5, yb - body + 12, PAL["fire"][3])
    R(cv, x0 + 6, yb - body + 20, x1 - 6, yb - body + 14, PAL["fire"][1])
    R(cv, x0 + 3, yb - 16, x1 - 3, yb - 6, PAL["brick"][3])          # 灶台基
    R(cv, x0 + 3, yb - 8, x1 - 3, yb, PAL["brick"][3])
    if tall:
        R(cv, W // 2 - 5, yb - body - 22, W // 2 + 5, yb - body, PAL["brick"][1])  # 烟囱
        R(cv, W // 2 - 7, yb - body - 26, W // 2 + 7, yb - body - 22, PAL["brick"][3])
    sh(cv, W // 2, yb - 1, W // 2 - 2)


def p_tupi_zaotai(cv, W, H):
    """土坯灶台：泥砌 + 铁锅。"""
    yb = H
    R(cv, 2, yb - 44, W - 2, yb, PAL["mud"][2])
    for r in range(0, 40, 5):
        yy = yb - 44 + r
        R(cv, 2, yy, W - 2, yy + 1, PAL["mud"][3])
    R(cv, 2, yb - 44, W - 2, yb - 41, PAL["mud"][0])
    EL(cv, 4, yb - 50, W - 4, yb - 40, PAL["iron"][2])
    EL(cv, 6, yb - 48, W - 6, yb - 43, PAL["iron"][1])
    R(cv, 5, yb - 30, W - 5, yb - 16, PAL["ink"][3])
    R(cv, 7, yb - 27, W - 7, yb - 20, PAL["fire"][2])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_daota_zaotai(cv, W, H):
    """倒塌的灶台残砖：一堆歪砖 + 灰。"""
    yb = H
    seeds = [(4, 0, 9, 6), (12, 3, 7, 6), (3, 8, 8, 5), (14, 10, 9, 6),
             (6, 15, 7, 5), (16, 17, 6, 5), (2, 22, 9, 6), (13, 24, 8, 5)]
    for (x, y, w, h) in seeds:
        R(cv, x, yb - y - h, x + w, yb - y, PAL["brick"][2])
        R(cv, x, yb - y - h, x + w, yb - y - h + 1, PAL["brick"][0])
    R(cv, 2, yb - 8, W - 2, yb, PAL["earth"][3])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_chaihuozao(cv, W, H):
    """柴火灶：泥灶 + 一口锅 + 柴。"""
    yb = H
    R(cv, 3, yb - 34, W - 3, yb, PAL["mud"][2])
    R(cv, 3, yb - 34, W - 3, yb - 31, PAL["mud"][0])
    EL(cv, 4, yb - 42, W - 4, yb - 31, PAL["iron"][2])
    EL(cv, 6, yb - 40, W - 6, yb - 33, PAL["iron"][1])
    R(cv, 6, yb - 24, W - 6, yb - 14, PAL["ink"][3])
    R(cv, 8, yb - 22, W - 8, yb - 16, PAL["fire"][2])
    R(cv, 2, yb - 14, 8, yb - 8, PAL["wood_d"][2])                   # 柴
    R(cv, 2, yb - 12, 9, yb - 7, PAL["wood_d"][3])
    sh(cv, W // 2, yb - 1, W // 2 - 2)


def p_zhenglong(cv, W, H):
    """蒸笼：三层竹蒸笼叠起来。"""
    yb = H
    for k in range(3):
        yy = yb - 16 - k * 13
        R(cv, 4, yy, W - 4, yy + 10, PAL["thatch"][2])
        EL(cv, 4, yy - 4, W - 4, yy + 4, PAL["thatch"][1])
        EL(cv, 6, yy - 2, W - 6, yy + 2, PAL["thatch"][0])
        R(cv, 4, yy + 9, W - 4, yy + 11, PAL["thatch"][3])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_tieguo(cv, W, H):
    """铁锅：厚壁圆锅带耳。"""
    yb = H
    EL(cv, 3, yb - 26, W - 3, yb - 6, PAL["iron"][2])
    EL(cv, 5, yb - 24, W - 5, yb - 8, PAL["iron"][1])
    EL(cv, 8, yb - 20, W - 8, yb - 12, PAL["iron"][3])
    R(cv, 1, yb - 20, 4, yb - 17, PAL["iron"][3])
    R(cv, W - 4, yb - 20, W - 1, yb - 17, PAL["iron"][3])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_shuichi(cv, W, H):
    """自来水池：水泥池 + 水龙头。"""
    yb = H
    R(cv, 2, yb - 36, W - 2, yb, PAL["rock"][2])
    R(cv, 2, yb - 36, W - 2, yb - 33, PAL["rock"][0])
    R(cv, 5, yb - 30, W - 5, yb - 12, PAL["rock"][3])
    R(cv, 6, yb - 28, W - 6, yb - 14, PAL["water"][2])
    R(cv, 7, yb - 27, W - 7, yb - 22, PAL["water"][0])
    R(cv, W // 2 - 1, yb - 48, W // 2 + 1, yb - 36, PAL["metal"][1])  # 龙头
    R(cv, W // 2 - 1, yb - 48, W // 2 + 4, yb - 46, PAL["metal"][1])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def _basin(cv, W, H, rim="porc", body="porc"):
    yb = H
    EL(cv, 3, yb - 26, W - 3, yb - 6, PAL[body][2])
    EL(cv, 5, yb - 24, W - 5, yb - 8, PAL[body][1])
    EL(cv, 7, yb - 22, W - 7, yb - 10, PAL["water"][1])
    EL(cv, 3, yb - 27, W - 3, yb - 20, PAL[rim][1])                  # 盆沿
    EL(cv, 5, yb - 25, W - 5, yb - 21, PAL[rim][0])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_shuipen(cv, W, H):
    _basin(cv, W, H)


def p_xishoupen(cv, W, H):
    _basin(cv, W, H, rim="cloth_b", body="porc")


def p_tangcipen(cv, W, H):
    _basin(cv, W, H, rim="cloth_b", body="white")


def p_gongtong(cv, W, H):
    """恭桶：木桶 + 盖。"""
    yb = H
    R(cv, 6, yb - 30, W - 6, yb, PAL["wood_d"][2])
    R(cv, 8, yb - 28, W - 8, yb - 2, PAL["wood_d"][1])
    R(cv, 6, yb - 22, W - 6, yb - 19, PAL["iron"][2])
    R(cv, 6, yb - 11, W - 6, yb - 8, PAL["iron"][2])
    EL(cv, 5, yb - 34, W - 5, yb - 26, PAL["wood"][1])
    EL(cv, 7, yb - 32, W - 7, yb - 28, PAL["wood"][0])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_dunbianqi(cv, W, H):
    """水冲蹲便器：瓷砖台 + 高水箱。"""
    yb = H
    R(cv, 1, yb - 26, W - 1, yb, PAL["porc"][2])
    for r in range(0, 24, 6):
        R(cv, 1, yb - 26 + r, W - 1, yb - 26 + r + 1, PAL["porc"][3])
    R(cv, 1, yb - 26, W - 1, yb - 24, PAL["porc"][0])
    R(cv, 5, yb - 20, W - 5, yb - 10, PAL["ink"][2])                 # 蹲坑口
    R(cv, 7, yb - 18, W - 7, yb - 12, PAL["ink"][3])
    R(cv, 4, yb - 56, W - 4, yb - 26, PAL["porc"][2])                # 高水箱
    R(cv, 4, yb - 56, W - 4, yb - 53, PAL["porc"][0])
    R(cv, 6, yb - 50, W - 6, yb - 44, PAL["metal"][1])              # 冲水手柄
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_fengwomeilu(cv, W, H):
    """蜂窝煤炉：铁皮炉 + 烟囱 + 码好的蜂窝煤。"""
    yb = H
    R(cv, 5, yb - 34, W - 5, yb, PAL["iron"][2])
    R(cv, 5, yb - 34, W - 5, yb - 31, PAL["iron"][0])
    R(cv, 8, yb - 27, W - 8, yb - 16, PAL["ink"][3])                 # 炉口
    R(cv, 9, yb - 25, W - 9, yb - 19, PAL["fire"][2])
    R(cv, W // 2 - 3, yb - 96, W // 2 + 3, yb - 34, PAL["metal"][2])  # 烟囱
    R(cv, W // 2 - 3, yb - 96, W // 2 - 1, yb - 34, PAL["metal"][0])
    for r in range(5):                                               # 蜂窝煤垛
        yy = yb - 8 - r * 9
        R(cv, 8, yy - 8, 22, yy, PAL["ink"][2])
        for i in range(4):
            EL(cv, 9 + i * 3, yy - 7, 12 + i * 3, yy - 4, PAL["ink"][1])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


# ================================================================== 容器
def p_shuigang(cv, W, H):
    """水缸：大陶缸，缸沿豁了一块口。"""
    yb = H
    EL(cv, 2, yb - 34, W - 2, yb - 4, PAL["pot"][2])
    R(cv, 4, yb - 26, W - 4, yb - 12, PAL["pot"][1])
    EL(cv, 4, yb - 36, W - 4, yb - 24, PAL["pot"][1])                # 缸沿
    EL(cv, 7, yb - 34, W - 7, yb - 26, PAL["water"][2])             # 缸里的水
    EL(cv, 9, yb - 33, W - 12, yb - 29, PAL["water"][0])
    R(cv, W - 14, yb - 34, W - 11, yb - 29, PAL["pot"][3])           # 豁口
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_jiutan(cv, W, H):
    """酒坛：封口布 + 麻绳。"""
    yb = H
    EL(cv, 5, yb - 30, W - 5, yb - 2, PAL["pot"][2])
    R(cv, 7, yb - 24, W - 7, yb - 10, PAL["pot"][1])
    EL(cv, 6, yb - 34, W - 6, yb - 26, PAL["pot"][1])
    EL(cv, 9, yb - 33, W - 9, yb - 28, PAL["cloth_r"][1])           # 封口布
    R(cv, 8, yb - 26, W - 8, yb - 24, PAL["thatch"][2])             # 麻绳
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_liangdun_1x1(cv, W, H):
    """粮囤（小）：编织囤 + 草盖。"""
    yb = H
    EL(cv, 4, yb - 30, W - 4, yb - 2, PAL["thatch"][2])
    for i in range(5):
        yy = yb - 6 - i * 5
        R(cv, 5 + (4 - i), yy, W - 5 - (4 - i), yy + 2, PAL["thatch"][3])
    EL(cv, 3, yb - 36, W - 3, yb - 26, PAL["thatch"][1])
    EL(cv, 6, yb - 35, W - 6, yb - 29, PAL["thatch"][0])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_liangdun_2x2(cv, W, H):
    """粮囤（大）：高囤 + 竹箍。"""
    yb = H
    R(cv, 8, yb - 62, W - 8, yb, PAL["thatch"][2])
    for i in range(7):
        yy = yb - 8 - i * 8
        R(cv, 9, yy, W - 9, yy + 2, PAL["thatch"][3])
        R(cv, 9, yy - 1, W - 9, yy, PAL["thatch"][0])
    EL(cv, 6, yb - 70, W - 6, yb - 56, PAL["thatch"][1])            # 囤盖
    EL(cv, 10, yb - 68, W - 10, yb - 60, PAL["thatch"][0])
    sh(cv, W // 2, yb - 1, W // 2 - 5)


def p_tuyuancang(cv, W, H):
    """土圆仓（3×3）：草泥圆仓 + 锥形茅顶。"""
    yb = H
    R(cv, 12, yb - 76, W - 12, yb, PAL["earth"][2])
    R(cv, 14, yb - 74, W - 14, yb - 4, PAL["earth"][1])
    for r in range(0, 70, 7):
        R(cv, 12, yb - 76 + r, W - 12, yb - 76 + r + 1, PAL["earth"][3])
    cv.poly([(12, yb - 76), (W - 12, yb - 76), (W // 2, yb - 100)], PAL["thatch"][1])
    cv.poly([(14, yb - 78), (W - 14, yb - 78), (W // 2, yb - 97)], PAL["thatch"][0])
    R(cv, W // 2 - 7, yb - 40, W // 2 + 7, yb - 20, PAL["wood_d"][2])  # 仓门
    R(cv, W // 2 - 6, yb - 39, W // 2 + 6, yb - 21, PAL["wood"][1])
    sh(cv, W // 2, yb - 1, W // 2 - 12)


def p_muxiang(cv, W, H, old=False):
    """木箱：板条箱（旧木箱带铜包角）。"""
    yb = H
    R(cv, 3, yb - 30, W - 3, yb, PAL["wood"][2])
    R(cv, 4, yb - 29, W - 4, yb - 1, PAL["wood"][1])
    TR(cv, 3, yb - 34, W - 3, yb - 28, 2, PAL["wood"][0])
    R(cv, 3, yb - 30, W - 3, yb - 28, PAL["wood_d"][2])
    R(cv, 3, yb - 16, W - 3, yb - 14, PAL["wood_d"][2])
    R(cv, 4, yb - 26, W - 4, yb - 18, PAL["wood_d"][3])              # 斜撑
    if old:
        R(cv, 3, yb - 30, 7, yb, PAL["brass"][2])
        R(cv, W - 7, yb - 30, W - 3, yb, PAL["brass"][2])
        R(cv, 3, yb - 30, W - 3, yb - 27, PAL["brass"][1])
        R(cv, 4, yb - 28, W - 4, yb - 27, PAL["brass"][0])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_luokuang(cv, W, H):
    """箩筐：编织筐。"""
    yb = H
    EL(cv, 4, yb - 28, W - 4, yb - 2, PAL["thatch"][2])
    R(cv, 6, yb - 22, W - 6, yb - 8, PAL["thatch"][1])
    for i in range(4):
        R(cv, 6, yb - 22 + i * 4, W - 6, yb - 21 + i * 4, PAL["thatch"][3])
    EL(cv, 4, yb - 32, W - 4, yb - 24, PAL["thatch"][1])
    EL(cv, 7, yb - 30, W - 7, yb - 26, PAL["thatch"][3])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_madai(cv, W, H):
    """麻袋：扎口粮袋。"""
    yb = H
    EL(cv, 5, yb - 30, W - 5, yb - 2, PAL["paper"][2])
    R(cv, 7, yb - 24, W - 7, yb - 8, PAL["paper"][1])
    cv.poly([(10, yb - 28), (W - 10, yb - 28), (W // 2, yb - 40)], PAL["paper"][1])
    R(cv, W // 2 - 4, yb - 34, W // 2 + 4, yb - 28, PAL["thatch"][2])   # 扎口
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_chaidui(cv, W, H):
    """柴堆：码好的柴。"""
    yb = H
    rows = [(4, 6, 24, 6), (6, 13, 20, 6), (3, 20, 24, 6), (8, 27, 14, 5)]
    for (x, y, w, h) in rows:
        R(cv, x, yb - y - h, x + w, yb - y, PAL["wood_d"][2])
        R(cv, x, yb - y - h, x + w, yb - y - h + 2, PAL["wood"][1])
        for i in range(1, w // 5):
            R(cv, x + i * 5, yb - y - h, x + i * 5 + 1, yb - y, PAL["wood_d"][3])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_nongjujia(cv, W, H):
    """农具架：横杆上挂锄与镰。"""
    yb = H
    R(cv, 4, yb - 46, W - 4, yb - 42, PAL["wood_d"][2])          # 横杆
    R(cv, 6, yb - 46, 9, yb, PAL["wood_d"][3])                    # 立柱
    R(cv, W - 9, yb - 46, W - 6, yb, PAL["wood_d"][3])
    R(cv, 12, yb - 44, 15, yb - 12, PAL["wood"][2])               # 锄柄
    R(cv, 10, yb - 14, 18, yb - 10, PAL["metal"][1])              # 锄头
    R(cv, 22, yb - 44, 25, yb - 16, PAL["wood"][2])               # 镰柄
    R(cv, 22, yb - 20, 29, yb - 15, PAL["metal"][1])              # 镰刀
    sh(cv, W // 2, yb - 1, W // 2 - 4)


def p_jilong(cv, W, H):
    """鸡笼：竹笼 + 小门。"""
    yb = H
    R(cv, 3, yb - 34, W - 3, yb, PAL["thatch"][2])
    for i in range(6):
        xx = 3 + i * 9
        R(cv, xx, yb - 34, xx + 2, yb, PAL["thatch"][3])
    for r in range(0, 32, 6):
        R(cv, 3, yb - 34 + r, W - 3, yb - 34 + r + 2, PAL["thatch"][3])
    TR(cv, 3, yb - 38, W - 3, yb - 32, 2, PAL["thatch"][1])
    R(cv, 12, yb - 24, 22, yb - 14, PAL["ink"][2])                 # 笼门
    sh(cv, W // 2, yb - 1, W // 2 - 4)


def p_fengche(cv, W, H):
    """风车：手摇扬谷风车（圆鼓 + 摇柄）。"""
    yb = H
    R(cv, 8, yb - 46, W - 8, yb, PAL["wood_d"][2])
    EL(cv, 8, yb - 48, W - 8, yb - 24, PAL["wood"][1])
    EL(cv, 12, yb - 44, W - 12, yb - 28, PAL["wood_d"][3])
    for i in range(4):
        R(cv, W // 2 - 1, yb - 44 + i * 4, W // 2 + 1, yb - 40 + i * 4, PAL["wood_l"][2])
    R(cv, W - 4, yb - 38, W - 1, yb - 34, PAL["metal"][1])          # 摇柄
    R(cv, W - 1, yb - 44, W, yb - 36, PAL["wood_l"][2])
    sh(cv, W // 2, yb - 1, W // 2 - 4)


def p_bangcheng(cv, W, H):
    """磅秤：台面 + 大圆盘表。"""
    yb = H
    R(cv, 4, yb - 14, W - 4, yb, PAL["metal"][2])
    R(cv, 4, yb - 14, W - 4, yb - 12, PAL["metal"][0])
    R(cv, W // 2 - 2, yb - 26, W // 2 + 2, yb - 14, PAL["metal"][2])   # 表柱
    EL(cv, W // 2 - 13, yb - 44, W // 2 + 13, yb - 22, PAL["porc"][1])   # 圆盘表
    EL(cv, W // 2 - 11, yb - 42, W // 2 + 11, yb - 24, PAL["white"][0])
    R(cv, W // 2 - 1, yb - 40, W // 2 + 1, yb - 30, PAL["ink"][2])      # 指针
    R(cv, W // 2 - 6, yb - 34, W // 2 + 6, yb - 32, PAL["ink"][3])
    sh(cv, W // 2, yb - 1, W // 2 - 4)


def p_shaixi(cv, W, H):
    """晒席：席上摊开的谷子。"""
    yb = H
    TR(cv, 1, yb - 30, W - 1, yb - 4, 4, PAL["thatch"][1])
    for i in range(8):
        R(cv, 3 + i * 7, yb - 28, 4 + i * 7, yb - 6, PAL["thatch"][3])
    R(cv, 3, yb - 26, W - 3, yb - 8, PAL["paper"][2])
    cv.speckle(3, yb - 26, W - 3, yb - 8, PAL["paper"][0], seed=5, density=0.05)
    sh(cv, W // 2, yb - 1, W // 2 - 4)


def p_liushai(cv, W, H):
    """溜筛：圆筛盘 + 谷粒。"""
    yb = H
    EL(cv, 2, yb - 30, W - 2, yb - 4, PAL["thatch"][2])
    EL(cv, 4, yb - 28, W - 4, yb - 6, PAL["thatch"][1])
    EL(cv, 7, yb - 25, W - 7, yb - 9, PAL["paper"][2])
    cv.speckle(7, yb - 25, W - 7, yb - 9, PAL["paper"][0], seed=9, density=0.05)
    EL(cv, 2, yb - 31, W - 2, yb - 25, PAL["thatch"][3])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_yanliangqi(cv, W, H):
    """验粮器：扦样勺 + 小量杯。"""
    yb = H
    R(cv, 8, yb - 44, 11, yb - 14, PAL["metal"][1])
    R(cv, 8, yb - 44, 9, yb - 14, PAL["metal"][0])
    EL(cv, 3, yb - 18, 17, yb - 4, PAL["metal"][2])                  # 勺
    EL(cv, 5, yb - 16, 15, yb - 6, PAL["metal"][1])
    R(cv, 19, yb - 22, 29, yb - 4, PAL["metal"][2])                 # 量杯
    R(cv, 20, yb - 20, 28, yb - 6, PAL["paper"][1])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_jimapai(cv, W, H):
    """木跳板 + 记码牌：斜板 + 挂着的木牌。"""
    yb = H
    cv.poly([(2, yb - 4), (W - 12, yb - 30), (W - 8, yb - 34), (6, yb - 8)],
            PAL["wood"][1])
    cv.poly([(6, yb - 8), (W - 8, yb - 34), (W - 8, yb - 31), (7, yb - 5)],
            PAL["wood_d"][2])
    R(cv, W - 12, yb - 46, W - 2, yb - 24, PAL["wood_l"][1])        # 记码牌
    R(cv, W - 12, yb - 46, W - 2, yb - 44, PAL["wood_l"][0])
    R(cv, W - 10, yb - 42, W - 6, yb - 38, PAL["ink"][2])
    R(cv, W - 10, yb - 36, W - 4, yb - 33, PAL["ink"][2])
    R(cv, W - 7, yb - 46, W - 5, yb - 24, PAL["wood_d"][2])
    sh(cv, W // 2, yb - 1, W // 2 - 4)


def p_zhiwutai(cv, W, H):
    """置物台：小方台 + 菜板 + 菜刀。"""
    yb = H
    TR(cv, 3, yb - 32, W - 3, yb - 26, 2, PAL["wood"][1])
    R(cv, 3, yb - 26, W - 3, yb - 10, PAL["wood_d"][2])
    R(cv, 5, yb - 24, W - 5, yb - 12, PAL["wood"][1])
    R(cv, 4, yb - 10, 8, yb, PAL["wood_d"][3])
    R(cv, W - 8, yb - 10, W - 4, yb, PAL["wood_d"][3])
    R(cv, 6, yb - 38, 18, yb - 32, PAL["wood_l"][1])                # 菜板
    R(cv, 17, yb - 44, 22, yb - 36, PAL["metal"][1])                # 刀
    R(cv, 21, yb - 41, 26, yb - 38, PAL["wood_d"][2])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


# ================================================================== 磨坊与粮
def p_shimo(cv, W, H):
    """石磨：木架 + 上磨盘（盘沿一圈刻字）。"""
    yb = H
    R(cv, 6, yb - 30, W - 6, yb, PAL["wood_d"][2])                  # 底架
    R(cv, 8, yb - 28, W - 8, yb - 4, PAL["wood_d"][1])
    R(cv, 6, yb - 20, W - 6, yb - 16, PAL["wood_d"][3])
    EL(cv, 2, yb - 68, W - 2, yb - 26, PAL["stone"][1])             # 下磨盘
    EL(cv, 6, yb - 64, W - 6, yb - 32, PAL["stone"][2])
    EL(cv, 1, yb - 76, W - 1, yb - 34, PAL["stone"][0])             # 上磨盘
    EL(cv, 5, yb - 72, W - 5, yb - 40, PAL["stone"][1])
    EL(cv, W // 2 - 7, yb - 64, W // 2 + 7, yb - 50, PAL["stone"][2])   # 中心孔
    EL(cv, W // 2 - 5, yb - 62, W // 2 + 5, yb - 52, PAL["ink"][2])
    for i in range(7):                                              # 盘沿刻字
        a = -60 + i * 20
        R(cv, W // 2 - 20 + (a * 14) // 20, yb - 52, W // 2 - 18 + (a * 14) // 20,
          yb - 48, PAL["stone"][3])
    R(cv, W // 2 - 2, yb - 84, W // 2 + 2, yb - 74, PAL["wood_d"][2])   # 推杆
    sh(cv, W // 2, yb - 1, W // 2 - 6)


def p_qizhi_shimo(cv, W, H):
    """弃置石磨：卸下来的上磨盘斜靠在墙角。"""
    yb = H
    EL(cv, 2, yb - 44, W - 2, yb - 6, PAL["stone"][1])
    EL(cv, 6, yb - 40, W - 6, yb - 12, PAL["stone"][2])
    EL(cv, W // 2 - 8, yb - 34, W // 2 + 8, yb - 22, PAL["stone"][3])
    EL(cv, W // 2 - 6, yb - 32, W // 2 + 6, yb - 24, PAL["ink"][2])
    for i in range(6):
        R(cv, 8 + i * 7, yb - 22 - (i % 2) * 3, 10 + i * 7, yb - 19 - (i % 2) * 3,
          PAL["stone"][3])
    sh(cv, W // 2, yb - 1, W // 2 - 6)


def p_laojing(cv, W, H):
    """老井：石井圈 + 木架 + 吊桶。"""
    yb = H
    EL(cv, 2, yb - 22, W - 2, yb - 4, PAL["stone"][1])
    R(cv, 4, yb - 18, W - 4, yb - 4, PAL["stone"][2])
    EL(cv, 5, yb - 20, W - 5, yb - 8, PAL["ink"][2])
    EL(cv, 7, yb - 18, W - 7, yb - 10, PAL["water"][1])
    R(cv, 4, yb - 56, 7, yb - 18, PAL["wood_d"][2])                # 木架
    R(cv, W - 7, yb - 56, W - 4, yb - 18, PAL["wood_d"][2])
    R(cv, 3, yb - 58, W - 3, yb - 54, PAL["wood_d"][1])
    R(cv, W // 2 - 1, yb - 54, W // 2 + 1, yb - 30, PAL["thatch"][2])   # 绳
    R(cv, W // 2 - 5, yb - 30, W // 2 + 5, yb - 20, PAL["wood"][2])     # 吊桶
    R(cv, W // 2 - 4, yb - 29, W // 2 + 4, yb - 22, PAL["wood"][1])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_qiangji_ankan(cv, W, H):
    """墙基暗龛：砖墙基上一个方龛（里头有油布包）。"""
    yb = H
    R(cv, 0, yb - 74, W, yb, PAL["brick"][2])
    for r in range(0, 74, 6):
        yy = yb - 74 + r
        R(cv, 0, yy, W, yy + 1, PAL["brick"][3])
        off = 0 if (r // 6) % 2 else 8
        xx = off
        while xx < W:
            R(cv, xx, yy, xx + 1, min(yb, yy + 6), PAL["brick"][3])
            xx += 16
    R(cv, 0, yb - 74, W, yb - 71, PAL["brick"][0])
    R(cv, 4, yb - 46, W - 4, yb - 22, PAL["ink"][2])                # 龛口
    R(cv, 6, yb - 44, W - 6, yb - 24, PAL["ink"][3])
    R(cv, 8, yb - 34, W - 8, yb - 26, PAL["cloth_b"][1])            # 油布包
    R(cv, 8, yb - 34, W - 8, yb - 32, PAL["cloth_b"][0])
    B(cv, 4, yb - 46, W - 4, yb - 22, PAL["brick"][1], 1)


def p_tangwu_diji(cv, W, H):
    """堂屋地基：荒草里一圈夯土地基轮廓。"""
    yb = H
    TR(cv, 0, yb - 62, W, yb - 4, 6, PAL["grass"][1])
    cv.speckle(0, yb - 62, W, yb - 4, PAL["grass"][0], seed=3, density=0.03)
    cv.speckle(0, yb - 62, W, yb - 4, PAL["grass"][2], seed=8, density=0.04)
    R(cv, 4, yb - 58, W - 4, yb - 52, PAL["earth"][2])
    R(cv, 4, yb - 14, W - 4, yb - 8, PAL["earth"][2])
    R(cv, 4, yb - 58, 8, yb - 8, PAL["earth"][2])
    R(cv, W - 8, yb - 58, W - 4, yb - 8, PAL["earth"][2])
    R(cv, 4, yb - 58, W - 4, yb - 56, PAL["earth"][1])
    R(cv, 4, yb - 14, W - 4, yb - 12, PAL["earth"][1])


def p_shuini_fengceng(cv, W, H):
    """水泥封层：三层水泥 + 一道走向西南的缝。"""
    yb = H
    for k, c in enumerate(["rock", "rock", "rock"]):
        top = 30 - k * 9
        R(cv, 2 + k * 2, yb - top, W - 2 - k * 2, yb, PAL[c][2 - k % 2])
    R(cv, 2, yb - 30, W - 2, yb - 28, PAL["rock"][0])
    R(cv, 4, yb - 21, W - 4, yb - 19, PAL["rock"][0])
    R(cv, 6, yb - 12, W - 6, yb - 10, PAL["rock"][0])
    cv.poly([(6, yb - 28), (10, yb - 20), (14, yb - 12), (16, yb - 4)],
            PAL["ink"][3])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_pingfeng(cv, W, H):
    """屏风：三扇折屏挡视线。"""
    yb = H
    R(cv, 1, yb - 60, W - 1, yb - 6, PAL["cloth_r"][1])
    R(cv, 2, yb - 58, W - 2, yb - 8, PAL["cloth_r"][0])
    for i in range(1, 3):
        R(cv, 2 + i * 10, yb - 60, 3 + i * 10, yb - 6, PAL["wood_d"][2])
    R(cv, 1, yb - 60, W - 1, yb - 57, PAL["wood_d"][2])
    R(cv, 1, yb - 9, W - 1, yb - 6, PAL["wood_d"][2])
    R(cv, 2, yb - 46, W - 2, yb - 44, PAL["cloth_r"][2])
    sh(cv, W // 2, yb - 1, W // 2 - 2)


def p_paiwei(cv, W, H):
    """牌位：一块立着的木牌 + 小底座。"""
    yb = H
    R(cv, 8, yb - 38, W - 8, yb - 4, PAL["wood_d"][2])
    R(cv, 10, yb - 36, W - 10, yb - 6, PAL["wood_l"][1])
    R(cv, W // 2 - 1, yb - 32, W // 2 + 1, yb - 12, PAL["ink"][2])
    R(cv, 4, yb - 6, W - 4, yb, PAL["wood_d"][2])
    R(cv, 5, yb - 5, W - 5, yb - 3, PAL["wood_d"][1])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_zuzong_paiwei(cv, W, H):
    """祖宗牌位：长条供桌 + 一排牌位 + 红布。"""
    yb = H
    R(cv, 2, yb - 44, W - 2, yb - 20, PAL["wood_d"][2])
    R(cv, 3, yb - 42, W - 3, yb - 22, PAL["cloth_r"][1])
    R(cv, 3, yb - 42, W - 3, yb - 40, PAL["cloth_r"][0])
    R(cv, 4, yb - 20, 9, yb, PAL["wood_d"][3])
    R(cv, W - 9, yb - 20, W - 4, yb, PAL["wood_d"][3])
    n = 5
    for i in range(n):
        x = 5 + i * 10
        R(cv, x, yb - 68, x + 8, yb - 44, PAL["wood_d"][2])
        R(cv, x + 1, yb - 66, x + 7, yb - 46, PAL["wood_l"][1])
        R(cv, x + 3, yb - 62, x + 5, yb - 50, PAL["ink"][2])
    sh(cv, W // 2, yb - 1, W // 2 - 4)


def p_maofang(cv, W, H):
    """茅房（3×2）：草顶小屋 + 门。"""
    yb = H
    R(cv, 10, yb - 44, W - 10, yb, PAL["mud"][2])
    R(cv, 12, yb - 42, W - 12, yb - 2, PAL["mud"][1])
    R(cv, W // 2 - 8, yb - 34, W // 2 + 8, yb, PAL["wood_d"][2])   # 门
    R(cv, W // 2 - 6, yb - 32, W // 2 + 6, yb - 1, PAL["wood"][1])
    R(cv, W // 2 + 3, yb - 20, W // 2 + 5, yb - 18, PAL["brass"][1])
    cv.poly([(4, yb - 44), (W - 4, yb - 44), (W // 2, yb - 62)], PAL["thatch"][1])
    for i in range(7):
        R(cv, 6 + i * 12, yb - 46, 8 + i * 12, yb - 52, PAL["thatch"][3])
    cv.poly([(8, yb - 46), (W - 8, yb - 46), (W // 2, yb - 60)], PAL["thatch"][0])
    sh(cv, W // 2, yb - 1, W // 2 - 10)


def p_maokeng(cv, W, H):
    """茅坑：坑口 + 两块蹲板。"""
    yb = H
    EL(cv, 2, yb - 26, W - 2, yb - 4, PAL["earth"][3])
    EL(cv, 5, yb - 23, W - 5, yb - 7, PAL["ink"][3])
    R(cv, 3, yb - 26, 12, yb - 12, PAL["wood"][1])
    R(cv, W - 12, yb - 26, W - 3, yb - 12, PAL["wood"][1])
    R(cv, 3, yb - 26, 12, yb - 24, PAL["wood"][0])
    R(cv, W - 12, yb - 26, W - 3, yb - 24, PAL["wood"][0])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


# ================================================================== 植物与杂项
def p_huapen(cv, W, H):
    """花盆：陶盆 + 花。"""
    yb = H
    R(cv, 6, yb - 22, W - 6, yb, PAL["pot"][2])
    R(cv, 8, yb - 20, W - 8, yb - 2, PAL["pot"][1])
    R(cv, 5, yb - 24, W - 5, yb - 20, PAL["pot"][1])
    R(cv, 5, yb - 24, W - 5, yb - 22, PAL["pot"][0])
    EL(cv, 9, yb - 38, W - 9, yb - 22, PAL["leaf"][1])
    EL(cv, 11, yb - 35, W - 11, yb - 25, PAL["leaf"][0])
    R(cv, W // 2 - 3, yb - 44, W // 2 + 3, yb - 36, PAL["cloth_r"][1])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_penjing_1x1(cv, W, H):
    """盆景：浅盆 + 松桩。"""
    yb = H
    R(cv, 5, yb - 16, W - 5, yb, PAL["pot"][2])
    R(cv, 7, yb - 14, W - 7, yb - 1, PAL["pot"][1])
    R(cv, 4, yb - 18, W - 4, yb - 14, PAL["pot"][1])
    R(cv, W // 2 - 1, yb - 34, W // 2 + 1, yb - 16, PAL["wood_d"][2])
    EL(cv, 6, yb - 42, W - 6, yb - 30, PAL["leaf_d"][1])
    EL(cv, 9, yb - 39, W - 9, yb - 33, PAL["leaf"][1])
    sh(cv, W // 2, yb - 1, W // 2 - 3)


def p_penjing_1x4(cv, W, H):
    """盆景（1×4）：连廊一排松桩盆景。"""
    for k in range(4):
        d = k * 30
        w = 26 - k * 2
        x0 = (W - w) // 2
        yb = H - d
        R(cv, x0 + 3, yb - 14, x0 + w - 3, yb, PAL["pot"][2])
        R(cv, x0 + 2, yb - 16, x0 + w - 2, yb - 12, PAL["pot"][1])
        R(cv, x0 + w // 2 - 1, yb - 30, x0 + w // 2 + 1, yb - 14, PAL["wood_d"][2])
        EL(cv, x0 + 2, yb - 38, x0 + w - 2, yb - 28, PAL["leaf_d"][1])
        EL(cv, x0 + 5, yb - 35, x0 + w - 5, yb - 30, PAL["leaf"][1])


def p_tingshu(cv, W, H):
    """庭树（2×2）：石榴树。"""
    yb = H
    R(cv, W // 2 - 5, yb - 44, W // 2 + 5, yb, PAL["wood_d"][2])
    R(cv, W // 2 - 3, yb - 42, W // 2 + 1, yb - 4, PAL["wood_d"][1])
    R(cv, W // 2 - 12, yb - 40, W // 2 - 4, yb - 34, PAL["wood_d"][2])
    R(cv, W // 2 + 2, yb - 38, W // 2 + 10, yb - 32, PAL["wood_d"][2])
    EL(cv, 6, yb - 76, W - 6, yb - 34, PAL["leaf_d"][1])
    EL(cv, 10, yb - 72, W - 10, yb - 38, PAL["leaf"][1])
    EL(cv, 16, yb - 66, W - 16, yb - 46, PAL["leaf"][0])
    for (x, y) in [(20, 54), (30, 62), (40, 50), (26, 66)]:
        R(cv, x, yb - y, x + 3, yb - y + 3, PAL["cloth_r"][1])
    sh(cv, W // 2, yb - 1, W // 2 - 6)


def p_denglong_1x1(cv, W, H):
    """灯笼：红纸灯笼 + 穗子。"""
    yb = H
    R(cv, W // 2 - 1, yb - 52, W // 2 + 1, yb - 40, PAL["ink"][2])
    EL(cv, W // 2 - 11, yb - 42, W // 2 + 11, yb - 20, PAL["cloth_r"][1])
    EL(cv, W // 2 - 8, yb - 39, W // 2 + 8, yb - 23, PAL["cloth_r"][0])
    R(cv, W // 2 - 10, yb - 42, W // 2 + 10, yb - 39, PAL["wood_d"][2])
    R(cv, W // 2 - 10, yb - 24, W // 2 + 10, yb - 21, PAL["wood_d"][2])
    R(cv, W // 2 - 2, yb - 20, W // 2 + 2, yb - 10, PAL["cloth_r"][2])
    sh(cv, W // 2, yb - 1, 6)


def p_denglong_1x4(cv, W, H):
    """灯笼（1×4）：连廊下四盏灯（沿纵深排开）。"""
    for k in range(4):
        d = k * 30
        yb = H - d
        R(cv, W // 2 - 1, yb - 44, W // 2 + 1, yb - 34, PAL["ink"][2])
        EL(cv, W // 2 - 10, yb - 36, W // 2 + 10, yb - 18, PAL["cloth_r"][1])
        EL(cv, W // 2 - 7, yb - 33, W // 2 + 7, yb - 21, PAL["cloth_r"][0])
        R(cv, W // 2 - 9, yb - 36, W // 2 + 9, yb - 33, PAL["wood_d"][2])
        R(cv, W // 2 - 9, yb - 21, W // 2 + 9, yb - 18, PAL["wood_d"][2])


# ================================================================== 分派表
def _mk(f, *a, **kw):
    return lambda cv, W, H: f(cv, W, H, *a, **kw)


DRAW = {
    # 坐具
    "deng_1x1": _mk(p_stool, 1),
    "deng_1x3": _mk(p_stool, 3),
    "tiaodeng_1x1": _mk(p_bench, 1),
    "changdeng_1x2": _mk(p_bench, 2),
    "changdeng_2x1": _mk(p_bench, 1),
    "yi_1x1": _mk(p_chair, 1),
    "tengyi_1x1": _mk(p_rattan, 1),
    "tengyi_1x4": _mk(p_rattan, 4),
    # 桌案
    "baxianzhuo_2x3": p_baxian_2x3,
    "baxianzhuo_2x2": p_baxian_2x2,
    "xiaozhuo_2x1": p_xiaozhuo,
    "shuzhuo_1x1": _mk(p_shuzhuo, False),
    "shuzhuo_1x2": _mk(p_shuzhuo, True),
    "shuzhuo_2x1": _mk(p_shuzhuo, False),
    "zhangzhuo_1x4": _mk(p_zhangzhuo, True),
    "zhangzhuo_2x1": _mk(p_zhangzhuo, False),
    "tiaoan_1x3": p_tiaoan,
    "anban_2x1": p_anban,
    "shizhuo_2x1": p_shizhuo,
    "bianmin_tai_2x1": p_bianmin,
    "yanliangtai_2x1": p_yanliangtai,
    # 柜架
    "yigui_1x2": p_yigui,
    "xiao_yigui_1x2": p_xiao_yigui,
    "gui_1x2": p_gui,
    "gui_2x1": p_gui,
    "wangui_1x2": p_wangui,
    "danjuji_suanpan_2x1": p_danjuji,
    "shujia_1x2": p_shujia,
    "shujia_2x2": p_shujia,
    # 床
    "danrenchuang_2x1": p_danren_2x1,
    "danrenchuang_1x2": p_danren_1x2,
    "shuangrenchuang_3x3": p_shuangren_3x3,
    "shuangrenchuang_2x2": p_shuangren_2x2,
    "jiu_muchuang_1x2": p_jiu_muchuang,
    # 灶厨
    "zaotai_1x4": _mk(p_zaotai, True),
    "zaotai_1x2": _mk(p_zaotai, False),
    "tupi_zaotai_2x1": p_tupi_zaotai,
    "daota_zaotai_1x4": p_daota_zaotai,
    "chaihuozao_1x1": p_chaihuozao,
    "zhenglong_1x1": p_zhenglong,
    "tieguo_1x1": p_tieguo,
    "shuichi_1x1": p_shuichi,
    "shuipen_1x1": p_shuipen,
    "xishoupen_1x1": p_xishoupen,
    "tangcipen_1x1": p_tangcipen,
    "gongtong_1x1": p_gongtong,
    "dunbianqi_1x2": p_dunbianqi,
    "fengwomeilu_1x4": p_fengwomeilu,
    "zhiwutai_1x1": p_zhiwutai,
    # 容器
    "shuigang_1x1": p_shuigang,
    "jiutan_1x1": p_jiutan,
    "liangdun_1x1": p_liangdun_1x1,
    "liangdun_2x2": p_liangdun_2x2,
    "tuyuancang_3x3": p_tuyuancang,
    "muxiang_1x1": _mk(p_muxiang, False),
    "jiu_muxiang_1x1": _mk(p_muxiang, True),
    "luokuang_1x1": p_luokuang,
    "madai_1x1": p_madai,
    "chaidui_1x1": p_chaidui,
    "nongjujia_2x1": p_nongjujia,
    "jilong_2x1": p_jilong,
    # 磨坊与粮
    "fengche_2x1": p_fengche,
    "bangcheng_2x1": p_bangcheng,
    "shaixi_2x1": p_shaixi,
    "liushai_1x1": p_liushai,
    "yanliangqi_1x1": p_yanliangqi,
    "mutiaoban_jimapai_2x1": p_jimapai,
    "shimo_2x4": p_shimo,
    "qizhi_shimo_2x2": p_qizhi_shimo,
    "laojing_1x1": p_laojing,
    # 建筑残迹
    "maofang_3x2": p_maofang,
    "maokeng_1x1": p_maokeng,
    "pingfeng_1x2": p_pingfeng,
    "paiwei_1x1": p_paiwei,
    "zuzong_paiwei_2x3": p_zuzong_paiwei,
    "qiangji_ankan_1x4": p_qiangji_ankan,
    "tangwu_diji_2x3": p_tangwu_diji,
    "shuini_fengceng_1x1": p_shuini_fengceng,
    # 植物杂项
    "huapen_1x1": p_huapen,
    "penjing_1x1": p_penjing_1x1,
    "penjing_1x4": p_penjing_1x4,
    "tingshu_2x2": p_tingshu,
    "denglong_1x1": p_denglong_1x1,
    "denglong_1x4": p_denglong_1x4,
}


def main():
    with open(MANIFEST, "r", encoding="utf-8") as f:
        man = json.load(f)
    os.makedirs(OUT_DIR, exist_ok=True)
    made, missing, bad = [], [], []
    for p in man["props"]:
        pid = p["id"]
        w, h = p["w"], p["h"]
        cw, ch = w * TILE, h * TILE + TILE          # 顶部多一格立面
        if pid not in DRAW:
            missing.append(pid)
            continue
        cv = Canvas(cw, ch)
        DRAW[pid](cv, cw, ch)
        out = os.path.join(ROOT, p["path"].replace("/", os.sep))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        cv.save(out)
        made.append(pid)
    print("props generated %d, missing %d" % (len(made), len(missing)))
    if missing:
        print("MISSING:", ", ".join(missing))
    print("ids not in manifest:", ", ".join(sorted(set(DRAW) - {p["id"] for p in man["props"]})))


if __name__ == "__main__":
    main()
