# -*- coding: utf-8 -*-
"""TILE32 fractional 缩放数学验算（纯标准库，不依赖 Godot / PIL）。

背景：视口 1280×720 + scale_mode=0(fractional) + Nearest 过滤 + aspect=keep。
问题：非整数倍缩放时，逻辑像素列映射到物理像素的宽度不等 → 滚动时格线「忽粗忽细」。

本脚本精确算出每档分辨率下每条逻辑像素/行占多少物理像素，量化脉动幅度与周期。

跑法：python lab/verify_scale.py
"""
from collections import Counter
from fractions import Fraction

VIEW_W, VIEW_H = 1280, 720

# 常见全屏分辨率。16:9 三档 + 一个 16:10 作对照。
TARGETS = [
    ("窗口默认", 1280, 720),
    ("1080p",   1920, 1080),
    ("1440p",   2560, 1440),
    ("4K UHD",  3840, 2160),
    ("16:10 对照(1920x1200)", 1920, 1200),
]


def nearest_scale(screen_w, screen_h):
    """aspect=keep：取较小的缩放比，多余部分留黑边。用 Fraction 保持精确。"""
    return min(Fraction(screen_w, VIEW_W), Fraction(screen_h, VIEW_H))


def physical_widths(scale, view_len):
    """返回每个逻辑像素列(行)占的物理像素数。

    物理像素 p 采样逻辑坐标 p/scale，Nearest 取四舍五入（half-up）。
    源逻辑列 i 占的物理像素集合 = {p : round(p/scale) == i}。
    标准最近邻：src = floor((p + 0.5)/scale) = floor((2p+1)·den/(2·num))，
    全程整数运算，避免浮点在 2.0/3.0 处的误差。
    """
    num, den = scale.numerator, scale.denominator
    n_phys = (view_len * num) // den
    counts = [0] * view_len
    for p in range(n_phys):
        src = (2 * p * den + den) // (2 * num)   # floor((p+0.5)/scale)
        if src < view_len:
            counts[src] += 1
    return counts


def min_period(seq):
    """序列最小周期；无周期返回 len(seq)。"""
    n = len(seq)
    for T in range(1, n + 1):
        if all(seq[i] == seq[i % T] for i in range(n)):
            return T
    return n


def analyse(name, w, h):
    s = nearest_scale(w, h)
    cw = physical_widths(s, VIEW_W)
    ch = physical_widths(s, VIEW_H)
    vals_w = sorted(set(cw))
    vals_h = sorted(set(ch))
    amp_w = max(cw) - min(cw)
    amp_h = max(ch) - min(ch)
    period_w = min_period(cw)
    letterbox_x = (w - VIEW_W * s) / 2
    letterbox_y = (h - VIEW_H * s) / 2

    print("=" * 66)
    print("%-22s  %dx%d" % (name, w, h))
    is_int = (s.denominator == 1)
    print("  scale          = %.4f %s" % (
        float(s), "(整数倍 ✓ 无脉动)" if is_int else "(非整数 ⚠ 有脉动)"))
    print("  内容区         = %dx%d 物理像素" % (
        (VIEW_W * s.numerator) // s.denominator,
        (VIEW_H * s.numerator) // s.denominator))
    print("  黑边           = 左右 %.0f / 上下 %.0f 物理像素" % (
        letterbox_x, letterbox_y))
    print("  横向逻辑列宽   = %s  取值集合%s" % (
        "周期 %d: %s" % (period_w, cw[:period_w]) if period_w <= 8
        else "见下", vals_w))
    print("  纵向逻辑行高   = 取值集合%s" % vals_h)
    print("  脉动幅度       = 横 %d px / 纵 %d px" % (amp_w, amp_h))
    if is_int:
        print("  判定           = 整数倍，格线等宽，无脉动。")
    else:
        print("  判定           = 相邻逻辑线物理宽度差 %dpx；滚动时格线粗细交替 = 脉动(数学必然)。" % amp_w)
        print("                   一格=32逻辑像素 = %d 个宽度周期。" % (32 // period_w))
    return s, amp_w, amp_h


def main():
    print("视口 %dx%d / scale_mode=0(fractional) / Nearest / aspect=keep" % (
        VIEW_W, VIEW_H))
    print("=" * 66)
    for name, w, h in TARGETS:
        analyse(name, w, h)
    print("=" * 66)
    print("结论：只有缩放比为整数(1/2/3)时格线严格等宽；1.5× 下宽度序列 1,2,1,2…")
    print("      这是 Nearest 采样的数学结果，换线性过滤能消脉动但像素画会糊，故保留。")


if __name__ == "__main__":
    main()
