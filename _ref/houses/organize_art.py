"""
一次性整理：把 _ref/houses/ 里的旧图片归档到 _ref/art/（用户 m01912）。
- 过程/探索图 -> _ref/art/_overview/
- 旧单栋拆解图（新版已在各帧文件夹生成）-> 删除，避免两份混淆
所有 move/delete 前都校验：源在预期目录内、目标父目录是预期目录、新版确实存在。
"""
import os
import shutil

HERE = os.path.abspath(os.path.dirname(__file__))               # .../_ref/houses
REF = os.path.dirname(HERE)                                      # .../_ref
ART = os.path.join(REF, "art")
OVERVIEW = os.path.join(ART, "_overview")

# 过程/探索图 -> _overview
PROCESS = ["v4_straight.png", "v4_L.png", "v4_wei.png", "v4_siheyuan.png",
           "v4_liangjin.png", "evolution_v4.png", "house_grid_chart.png",
           "straight_rooms.png"]

# 旧单栋图 -> (新目录, 新版文件名)  仅当新版存在才删旧图
OLD = {
    "lu_house.png": ("A1_1926", "lu_house.png"),
    "mill.png": ("A2_1951", "mill_a2.png"),
    "shen_a1.png": ("A1_1926", "shen_a1.png"),
    "shen_a2.png": ("A2_1951", "shen_a2.png"),
    "shen_a3.png": ("A3_1976", "shen_a3.png"),
    "shen_a4.png": ("A4_2001", "shen_a4.png"),
    "market.png": ("A4_2001", "market.png"),
    "zhou_house.png": ("A1_1926", "zhou_house.png"),
    "toyshop.png": ("A5_2026", "toyshop.png"),
    "school.png": ("A5_2026", "school.png"),
}


def assert_in(path, parent, label):
    real = os.path.realpath(path)
    rp = os.path.realpath(parent)
    assert os.path.commonpath([real, rp]) == rp, f"{label} 不在预期目录: {path}"


def main():
    os.makedirs(OVERVIEW, exist_ok=True)
    assert_in(OVERVIEW, ART, "_overview")

    moved = 0
    for name in PROCESS:
        src = os.path.join(HERE, name)
        if not os.path.isfile(src):
            print("skip (missing):", src)
            continue
        assert_in(src, HERE, "过程图源")
        dst = os.path.join(OVERVIEW, name)
        assert_in(dst, OVERVIEW, "过程图目标")
        if os.path.exists(dst):
            os.remove(src)
        else:
            shutil.move(src, dst)
        print("archived:", name, "-> _overview/")
        moved += 1

    removed = 0
    for name, (frame, newname) in OLD.items():
        src = os.path.join(HERE, name)
        if not os.path.isfile(src):
            print("skip (missing):", src)
            continue
        assert_in(src, HERE, "旧图源")
        newp = os.path.join(ART, frame, newname)
        assert_in(newp, ART, "新版路径")
        assert os.path.isfile(newp), f"新版不存在，拒绝删旧图: {newp}"
        os.remove(src)
        print("removed old duplicate:", name, f"(新版 {frame}/{newname})")
        removed += 1

    print(f"DONE - archived={moved} removed={removed}")


if __name__ == "__main__":
    main()
