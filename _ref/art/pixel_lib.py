# -*- coding: utf-8 -*-
"""32px 像素画基础库（美术资产执行线专用）。

口径：1 格 = 32×32 px（TILE=32，见 scripts/house_shape.gd:13）。
风格：星露谷式暖色调乡村；左上来光；只用色阶分层，不画细碎纹理（2× 缩放下会糊成噪点）。

本文件只提供绘图基元与调色板；具体资产在 _gen_shells.py / _gen_props.py / _gen_scene.py。
"""
from PIL import Image, ImageDraw

TILE = 32

# ---------------------------------------------------------------- 调色板
# 每个色组是 (亮, 主, 暗, 更暗) 四档，越靠前越亮。
PAL = {
    # 木材
    "wood":   ("#c89a5e", "#a2763f", "#7a5429", "#4e341a"),
    "wood_d": ("#a07a4c", "#836038", "#5f4423", "#3d2b14"),
    "wood_l": ("#e0b878", "#c39a5c", "#9c7539", "#6f5222"),
    # 墙面（泥墙 / 白灰 / 青砖）
    "plaster": ("#e8d7b8", "#d0b892", "#a68f6c", "#7b6647"),
    "mud":    ("#c9a87e", "#ac8b61", "#866a45", "#5d492d"),
    "brick":  ("#b9a894", "#9c8b78", "#7a6b5a", "#57493c"),
    "stone":  ("#c4c0b4", "#a5a196", "#827e73", "#5d5a52"),
    # 屋顶
    "thatch": ("#e0bd76", "#c39a52", "#9c7836", "#6d5322"),
    "tile_r": ("#b8634a", "#9a4c39", "#78382a", "#51251c"),
    "tile_g": ("#6f7a5c", "#57603f", "#40472d", "#2a2f1c"),
    # 地面
    "floor_w": ("#c8a578", "#a8875a", "#7f6640", "#54432a"),
    "yard":   ("#8a8a5c", "#6f7449", "#555937", "#3a3c26"),
    "grass":  ("#8fa055", "#74843f", "#58682c", "#3b451c"),
    "dirt":   ("#b09066", "#8e7148", "#6c5433", "#493820"),
    "soil":   ("#8a6a45", "#6d5334", "#513d25", "#342715"),
    "earth":  ("#a3865c", "#876c47", "#665031", "#44351e"),
    # 布 / 纸
    "cloth_r": ("#cf7a63", "#b35f4a", "#8d4636", "#5e2e24"),
    "cloth_b": ("#6f8ba8", "#57708a", "#40566c", "#293a4a"),
    "paper":  ("#f0e6c8", "#dbceaa", "#b7aa86", "#8b8064"),
    # 金属
    "metal":  ("#b8bcc0", "#909498", "#6b6f73", "#484b4e"),
    "iron":   ("#7d8186", "#5e6266", "#45484b", "#2e3033"),
    "brass":  ("#e0bd6a", "#c39a45", "#96742d", "#68501b"),
    # 水 / 植物
    "water":  ("#6f9ab0", "#4f7e95", "#38607a", "#24455b"),
    "leaf":   ("#7ea04a", "#618135", "#476025", "#2e3f17"),
    "leaf_d": ("#6b8c3f", "#526d2d", "#3c5120", "#263514"),
    # 陶 / 瓷
    "pot":    ("#b8734c", "#96593a", "#6f4028", "#4a2b19"),
    "porc":   ("#eef2f0", "#cfd8d5", "#a7b2ae", "#7a8481"),
    #  misc
    "ink":    ("#3a2f26", "#2b221b", "#1c1611", "#100c09"),
    "white":  ("#ffffff", "#f0ece0", "#d6d0c0", "#a9a494"),
    "fire":   ("#ffd36a", "#f0913a", "#c35d24", "#8a3c16"),
    "glass":  ("#cfe0e4", "#a9c4cc", "#7d9ba6", "#55707c"),
    # 天空 / 远景（场景层用）
    "sky":    ("#cfe3ef", "#a9cfe4", "#7fb2cd", "#5a93b0"),
    "sand":   ("#e2d2a8", "#c9b787", "#a89565", "#847249"),
    "rock":   ("#9aa0a2", "#7b8184", "#5d6366", "#42484a"),
}


def shade(name, level):
    """取调色板某色组的第 level 档（0 最亮 → 3 最暗）。"""
    return PAL[name][max(0, min(3, level))]


def hexc(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def mix(c1, c2, t):
    a = hexc(c1) if isinstance(c1, str) else c1
    b = hexc(c2) if isinstance(c2, str) else c2
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))


# ---------------------------------------------------------------- 画布
class Canvas:
    """像素画布。

    默认 ss=1（1 目标像素 = 1 真实像素，硬边，像素画标准）。
    需要斜面/圆形抗锯齿时用 ss=2，画完自动降采样。

    坐标一律用**目标像素**坐标，内部自动乘 ss。
    """

    def __init__(self, w, h, bg=None, ss=1):
        self.w = w
        self.h = h
        self.ss = ss
        self.im = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0) if bg is None else hexc(bg))
        self.d = ImageDraw.Draw(self.im)

    def _s(self, box):
        k = self.ss
        return [box[0] * k, box[1] * k, box[2] * k, box[3] * k]

    def rect(self, x0, y0, x1, y1, color):
        self.d.rectangle(self._s((x0, y0, x1, y1)), fill=hexc(color) if isinstance(color, str) else color)

    def box(self, x0, y0, x1, y1, color, width=1):
        self.d.rectangle(self._s((x0, y0, x1, y1)),
                         outline=hexc(color) if isinstance(color, str) else color,
                         width=max(1, int(width * self.ss)))

    def line(self, x0, y0, x1, y1, color, width=1):
        self.d.line(self._s((x0, y0, x1, y1)),
                    fill=hexc(color) if isinstance(color, str) else color,
                    width=max(1, int(width * self.ss)))

    def poly(self, pts, color):
        k = self.ss
        self.d.polygon([(x * k, y * k) for x, y in pts],
                       fill=hexc(color) if isinstance(color, str) else color)

    def ellipse(self, x0, y0, x1, y1, color):
        self.d.ellipse(self._s((x0, y0, x1, y1)),
                       fill=hexc(color) if isinstance(color, str) else color)

    def px(self, x, y, color):
        self.d.rectangle(self._s((x, y, x + 1, y + 1)),
                         fill=hexc(color) if isinstance(color, str) else color)

    # -- 常用构件 --
    def vgrad(self, x0, y0, x1, y1, c_top, c_bot):
        """竖直渐变（按目标像素逐行插值），像素风里当柔和过渡用。"""
        h = max(1, int(y1 - y0))
        for i in range(h):
            t = i / max(1, h - 1)
            self.line(x0, y0 + i, x1, y0 + i, mix(c_top, c_bot, t), 1)

    def hgrad(self, x0, y0, x1, y1, c_left, c_right):
        w = max(1, int(x1 - x0))
        for i in range(w):
            t = i / max(1, w - 1)
            self.line(x0 + i, y0, x0 + i, y1, mix(c_left, c_right, t), 1)

    def noise_dots(self, x0, y0, x1, y1, color, seed=0, density=0.10, size=1):
        """稀疏噪点（固定 seed，可复现）。用 xorshift 散布，避免出现规则网格。"""
        h = int(y1 - y0)
        w = int(x1 - x0)
        if h <= 0 or w <= 0:
            return
        n = int(w * h * density)
        s = (seed * 2654435761 + 12345) & 0xFFFFFFFF
        for _ in range(n):
            s ^= (s << 13) & 0xFFFFFFFF
            s ^= s >> 17
            s ^= (s << 5) & 0xFFFFFFFF
            px = x0 + (s % w)
            s ^= (s << 13) & 0xFFFFFFFF
            s ^= s >> 17
            s ^= (s << 5) & 0xFFFFFFFF
            py = y0 + (s % h)
            for oy in range(size):
                for ox in range(size):
                    if px + ox < x1 and py + oy < y1:
                        self.px(px + ox, py + oy, color)

    def speckle(self, x0, y0, x1, y1, color, seed=0, density=0.02, size=2):
        """成簇的小斑点（2×2），比单像素噪点更像材质颗粒。"""
        h = int(y1 - y0)
        w = int(x1 - x0)
        if h <= 2 or w <= 2:
            return
        n = max(1, int(w * h * density / 4))
        s = (seed * 40503 + 7) & 0xFFFFFFFF
        for _ in range(n):
            s = (s * 1103515245 + 12345) & 0x7FFFFFFF
            px = x0 + (s % w)
            s = (s * 1103515245 + 12345) & 0x7FFFFFFF
            py = y0 + (s % h)
            if px + size >= x1 or py + size >= y1:
                continue
            self.rect(px, py, px + size, py + size, color)

    def outline(self, color, alpha=200, ofs=0):
        """给不透明像素加一圈描边（避免深色物件糊在深色背景里）。"""
        px = self.im.load()
        w, h = self.im.size
        solid = set()
        for y in range(h):
            for x in range(w):
                if px[x, y][3] > 40:
                    solid.add((x, y))
        edge = set()
        for (x, y) in solid:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q not in solid:
                    edge.add(q)
        for (x, y) in edge:
            if 0 <= x < w and 0 <= y < h:
                r, g, b, _ = px[x, y]
                px[x, y] = (r, g, b, alpha)

    def shadow_ellipse(self, cx, cy, rx, ry, color=None, alpha=90):
        """物件脚下的椭圆投影（半透明）。"""
        c = hexc(color) if color else (20, 18, 14, alpha)
        k = self.ss
        layer = Image.new("RGBA", (self.w * k, self.h * k), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.ellipse([(cx - rx) * k, (cy - ry) * k, (cx + rx) * k, (cy + ry) * k], fill=c)
        self.im.alpha_composite(layer)

    def save(self, path):
        out = self.im if self.ss == 1 else self.im.resize((self.w, self.h), Image.LANCZOS)
        out.save(path, "PNG")
        return path


# ---------------------------------------------------------------- 调色板便捷
def P(name, lv):
    return shade(name, lv)
