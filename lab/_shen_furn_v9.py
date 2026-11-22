"""shen_a4 v9 家具权威脚本（家具自检 + 出带家具图）。

【数据源】houses_data.json 里 shen_a4 的 v9 定稿家具（76 件，2026-11-22 用户确认落地）。
本脚本只读 JSON、不写 JSON——houses_data.json 是唯一数据源。
家具口径：12 功能房生活合理化、衣柜/柜/单人床/书架长边贴墙、储物间箱坛货架沿墙成排、
门厅鞋架衣帽架；3 件 clue 叙事保全（蜂窝煤炉 1976 / 账桌「地下有暗河」/ 保险柜「改稿底本」）。

用法：
  python lab/_shen_furn_v9.py             # 家具自检
  python lab/_shen_furn_v9.py --preview   # 另出带家具图 lab/shen_a4_with_furniture.png
"""
import sys
sys.path.insert(0, '_ref/houses')
import gen_all_houses as g

HOUSE_ID = 'shen_a4'
# clue 三件：名称 + 文案必须出现的关键词
CLUE_KEEP = {
    '蜂窝煤炉': '蜂窝煤',
    '账桌': '地下有暗河',
    '保险柜': '改稿底本',
}


def load():
    return next(h for h in g.HOUSES if h['id'] == HOUSE_ID)


def selfcheck(h=None):
    h = h or load()
    X0, Y0, X1, Y1 = h['lot']
    grid = g.build_grid(h)
    F = h['furniture']

    # gen_all_houses.check_all 的家具全规则（复用它，覆盖越界/重叠/压门/净空/房间不压墙）
    g.HOUSES = [h]  # 临时只校验本栋——注意是模块级替换，脚本结束即弃
    g.check_all()

    # clue 三件叙事保全
    for name, kw in CLUE_KEEP.items():
        hits = [f for f in F if f['name'] == name and f.get('clue')]
        assert hits, f'clue 家具缺失: {name}'
        assert any(kw in f['note'] for f in hits), f'clue「{name}」文案丢了「{kw}」'

    # 长边贴墙：1×2 竖柜/书架/衣柜类须贴东西墙，2×1 横床/桌须贴南北墙
    # 墙格判定用真实 grid（# 墙 / D 门 / G 院门 都算边界）
    def wall(px, py):
        if px < X0 or px > X1 or py < Y0 or py > Y1:
            return True  # 越过 lot 边界也是墙
        return grid[py - Y0][px - X0] in '#DG'

    # 用户原话「衣柜、柜、单人床、书架长边贴墙」——屏风/酒坛是短边贴墙，不在其列
    tall_key = ('衣柜', '大衣柜', '大柜', '储物柜', '书架', '货架')
    wide_key = ('单人床',)
    for f in F:
        x, y, w, hh = f['rect']
        nm = f['name']
        if w == 1 and hh == 2 and any(k in nm for k in tall_key):
            # 长边沿 y：西邻或东邻须是墙
            assert all(wall(x - 1, yy) or wall(x + 1, yy) for yy in (y, y + 1)), \
                f'{nm}@({x},{y}) 竖柜未贴东西墙'
        if w == 2 and hh == 1 and any(k in nm for k in wide_key):
            # 长边沿 x：北邻或南邻须是墙
            assert all(wall(xx, y - 1) or wall(xx, y + 1) for xx in (x, x + 1)), \
                f'{nm}@({x},{y}) 横床未贴南北墙'

    print(f'SHEN V9 FURNITURE PASS | 共 {len(F)} 件（住宅 '
          f'{sum(1 for f in F if f["zone"] == "house")} + 庭院 '
          f'{sum(1 for f in F if f["zone"] == "yard")}）| clue 三件文案保全 | 长边贴墙全过')
    return True


def preview():
    h = load()
    img = g.render(h)
    p = 'lab/shen_a4_with_furniture.png'
    img.save(p)
    print('saved', p, img.size)


if __name__ == '__main__':
    selfcheck()
    if '--preview' in sys.argv:
        preview()
