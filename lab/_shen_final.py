"""shen_a4 v9 房型权威脚本（房型结构自检 + 出房型图）。

【数据源】houses_data.json 里 shen_a4 的 v9 定稿字段（2026-11-22 用户确认落地）。
本脚本只读 JSON、不写 JSON——彻底消除旧 _redo_shen_a4.py「跑一次覆盖回 28×31」的风险。
房型设计基准（考据）：32×32 方院居中进 36×36 lot（四周 2 格庭院）；口字连廊宽 3
方正闭合、贴 9×9 天井居中；12 间矩形房贴合连廊外侧、四角放大矩形大房；单墙分隔、
房门全直达连廊不穿房；东南巽位门庑式院门 + 门厅座山影壁（墙非门）。

用法：
  python lab/_shen_final.py             # 房型自检
  python lab/_shen_final.py --preview   # 另出无家具房型图 lab/shen_a4_layout_final.png
"""
import sys
sys.path.insert(0, '_ref/houses')
import gen_all_houses as g

HOUSE_ID = 'shen_a4'
EXPECTED_LOT = [0, 0, 35, 35]


def load():
    return next(h for h in g.HOUSES if h['id'] == HOUSE_ID)


def selfcheck(h=None):
    h = h or load()
    grid = g.build_grid(h)
    X0, Y0, X1, Y1 = h['lot']
    assert h['lot'] == EXPECTED_LOT, f"lot 变了: {h['lot']}（应为 36×36）"

    # 天井 9×9：中心区 (14..22, 14..22) 必须全是露空格
    ty = [i for i, r in enumerate(h['rooms']) if '天井' in r[4]]
    assert len(ty) == 1, '天井房间应恰好 1 个'
    tx0, ty0, tx1, ty1 = h['rooms'][ty[0]][:4]
    assert (tx1 - tx0 + 1, ty1 - ty0 + 1) == (9, 9), '天井应 9×9'
    for ry in range(ty0, ty1 + 1):
        for rx in range(tx0, tx1 + 1):
            assert grid[ry - Y0][rx - X0] == ' ', f'天井格 ({rx},{ry}) 非露天'

    # 连廊四段：名字含「连廊」的房间必须全为室内 '.'（不被墙截断）
    corridors = [r for r in h['rooms'] if '连廊' in r[4]]
    assert len(corridors) == 4, f'连廊应 4 段，实得 {len(corridors)}'
    cset = set()
    for cx0, cy0, cx1, cy1, _, _ in corridors:
        for ry in range(cy0, cy1 + 1):
            for rx in range(cx0, cx1 + 1):
                assert grid[ry - Y0][rx - X0] == '.', f'连廊格 ({rx},{ry}) 非室内'
                cset.add((rx, ry))

    # 房门直达连廊：每道门的四邻至少一格落连廊集合
    for dx, dy in h['doors']:
        assert any((dx + a, dy + b) in cset for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))), \
            f'房门 ({dx},{dy}) 未直达连廊'

    # 12 功能房（排除 4 连廊 + 天井 + 门厅前室）
    func = [r for r in h['rooms'] if '连廊' not in r[4] and '天井' not in r[4] and '前室' not in r[4]]
    assert len(func) == 12, f'功能房应 12，实得 {len(func)}'

    # 房间矩形不含墙格（与 gen_all_houses.check_all :705-712 同规则）
    for rx0, ry0, rx1, ry1, rn in [r[:5] for r in h['rooms']]:
        for ry in range(ry0, ry1 + 1):
            for rx in range(rx0, rx1 + 1):
                if X0 <= rx <= X1 and Y0 <= ry <= Y1:
                    assert grid[ry - Y0][rx - X0] != '#', f'房间「{rn}」压墙格 ({rx},{ry})'

    # 连通性 BFS：院门出发，走室内 '.' 与露空格（天井已拆墙），全可走格应可达
    gx, gy = h['gate'][0]
    passable = set()
    for ry in range(Y0, Y1 + 1):
        for rx in range(X0, X1 + 1):
            ch = grid[ry - Y0][rx - X0]
            if ch in ('.', ' ', 'G') and not g.occupied(h, rx, ry):
                passable.add((rx, ry))
    seen, stack = set(), [(gx, gy)]
    while stack:
        c = stack.pop()
        if c in seen or c not in passable:
            continue
        seen.add(c)
        stack.extend([(c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)])
    assert (gx, gy) in seen, '院门格不可走'
    print(f'SHEN V9 LAYOUT PASS | lot={h["lot"]} 天井9×9 连廊4段 功能房12 '
          f'房门全直达连廊 | 可达 {len(seen)}/{len(passable)}')
    return True


def preview():
    h = dict(load())
    h['furniture'] = []  # 房型图不带家具
    img = g.render(h)
    p = 'lab/shen_a4_layout_final.png'
    img.save(p)
    print('saved', p, img.size)


if __name__ == '__main__':
    selfcheck()
    if '--preview' in sys.argv:
        preview()
