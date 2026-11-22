# 美术同学资产导入适配线 · 映射表

> 生成脚本：`lab/_cls_doc.py`（可重跑）。数据源：`lab/_cls_map_a.json`、`lab/_cls_map_b.json`。
> 本表**不覆盖**已交付的 AI 程序化图：全部产物落在 `assets/village/_classmate/props/`，
> 替换与否由本人拍板。

## 0. 总览

| 档位 | 源文件数 | 已映射 | 未映射 | 落盘产物 |
|---|---|---|---|---|
| A 档 单件家具 | 23 | 23 | 0 | 19 主图 + 4 变体 |
| B 档 图集切片 | 32 | 13 张图集贡献 60 切片 | 19 张图集未取件 | 20 主图 + 41 变体 |
| C 档 房屋/地皮/树/主角 | 19 | 19（只出方案） | 0 | **0（按纪律不落盘）** |
| **合计** | **74** | **55** | **19** | **84 张 PNG（39 主图 + 45 变体）** |

规格口径（D6）：交付画布 = 占地宽×32 × (占地高×32 + 32)，透明补在**顶部**，内容**贴底**。
校验脚本 `lab/_cls_check.py`：84 张全部尺寸符合 manifest 且内容贴底，**0 问题**。

## 1. A 档 · 单件家具（23 张，逐张映射，已落盘）

| 源文件 | 像素尺寸 | 目标 manifest id | 目标路径 | 置信度 | 备注 |
|---|---|---|---|---|---|
| `美术资产/家具/床/Sprite-大床1.png` | 64×64 | `shuangrenchuang_2x2` | `assets/village/_classmate/props/shuangrenchuang_2x2.png` | 高 | 双人大床（米色） |
| `美术资产/家具/床/Sprite-大床2.png` | 64×64 | `shuangrenchuang_2x2` | `assets/village/_classmate/props/_variants/shuangrenchuang_2x2__Sprite-大床2.png` | 高 | 双人大床（蓝被，变体） |
| `美术资产/家具/床/Sprite-床1.png` | 32×64 | `danrenchuang_1x2` | `assets/village/_classmate/props/danrenchuang_1x2.png` | 高 | 红被单床 |
| `美术资产/家具/床/Sprite-床2.png` | 32×64 | `danrenchuang_1x2` | `assets/village/_classmate/props/_variants/danrenchuang_1x2__Sprite-床2.png` | 高 | 米色被褥床（变体） |
| `美术资产/家具/床/Sprite-床3.png` | 32×64 | `danrenchuang_1x2` | `assets/village/_classmate/props/_variants/danrenchuang_1x2__Sprite-床3.png` | 高 | 蓝被床（变体） |
| `美术资产/家具/柜子/Sprite-柜子1.png` | 32×64 | `gui_1x2` | `assets/village/_classmate/props/gui_1x2.png` | 中 | 四层抽屉竖柜 |
| `美术资产/家具/柜子/Sprite-柜子2.png` | 32×32 | `gui_1x1` | `assets/village/_classmate/props/gui_1x1.png` | 高 | 两层抽屉矮柜（NEW id） |
| `美术资产/家具/柴缸灶/Sprite-柴堆.png` | 32×32 | `chaidui_1x1` | `assets/village/_classmate/props/chaidui_1x1.png` | 高 | 柴堆 |
| `美术资产/家具/柴缸灶/Sprite-柴火灶.png` | 32×32 | `chaihuozao_1x1` | `assets/village/_classmate/props/chaihuozao_1x1.png` | 高 | 柴火灶，一口锅 |
| `美术资产/家具/柴缸灶/Sprite-水缸1.png` | 32×32 | `shuigang_1x1` | `assets/village/_classmate/props/shuigang_1x1.png` | 高 | 陶水缸，院内蓄水 |
| `美术资产/家具/柴缸灶/Sprite-茅坑.png` | 32×32 | `maokeng_1x1` | `assets/village/_classmate/props/maokeng_1x1.png` | 高 | 茅坑（坑口） |
| `美术资产/家具/桌子/Sprite-书桌1.png` | 32×32 | `shuzhuo_1x1` | `assets/village/_classmate/props/shuzhuo_1x1.png` | 高 | 带抽屉书桌，摊开书册 |
| `美术资产/家具/桌子/Sprite-短桌1.png` | 32×32 | `xiaozhuo_1x1` | `assets/village/_classmate/props/xiaozhuo_1x1.png` | 高 | 素木小方桌（NEW id） |
| `美术资产/家具/桌子/Sprite-短桌2.png` | 32×32 | `hongzhuo_1x1` | `assets/village/_classmate/props/hongzhuo_1x1.png` | 高 | 铺红绸方桌/喜桌（NEW id） |
| `美术资产/家具/桌子/Sprite-短桌3.png` | 32×32 | `shuzhuo_1x1_top` | `assets/village/_classmate/props/shuzhuo_1x1_top.png` | 中 | 俯视书桌，桌上摊纸笔（NEW id） |
| `美术资产/家具/桌子/Sprite-短桌4.png` | 32×32 | `baizhuo_1x1` | `assets/village/_classmate/props/baizhuo_1x1.png` | 高 | 铺白桌布方桌/供桌（NEW id） |
| `美术资产/家具/桌子/Sprite-长桌1.png` | 64×32 | `changzhuo_2x1` | `assets/village/_classmate/props/changzhuo_2x1.png` | 高 | 长条木桌 2 格（NEW id） |
| `美术资产/家具/桌子/Sprite-餐桌1.png` | 96×32 | `cantang_3x1` | `assets/village/_classmate/props/cantang_3x1.png` | 高 | 整套餐桌：长桌+两小凳（NEW id） |
| `美术资产/家具/椅子/Sprite-短椅1.png` | 32×32 | `yi_1x1` | `assets/village/_classmate/props/yi_1x1.png` | 高 | 带靠背木椅 |
| `美术资产/家具/椅子/Sprite-短椅2.png` | 32×32 | `deng_1x1` | `assets/village/_classmate/props/deng_1x1.png` | 中 | 圆草墩（当凳） |
| `美术资产/家具/箱子/Sprite-箱子1.png` | 32×32 | `muxiang_1x1` | `assets/village/_classmate/props/muxiang_1x1.png` | 高 | 木箱 |
| `美术资产/家具/箱子/Sprite-箱子2.png` | 32×32 | `luokuang_1x1` | `assets/village/_classmate/props/luokuang_1x1.png` | 中 | 竹编扁箩筐（变体） |
| `美术资产/家具/箱子/Sprite-箱子3.png` | 32×32 | `luokuang_1x1` | `assets/village/_classmate/props/_variants/luokuang_1x1__Sprite-箱子3.png` | 中 | 竹编圆箩筐（主图） |

**A 档新增 id（用户 m00083 拍板『加新 id』）**：

| 新 id | code | 中文名 | 占地 | 来源 |
|---|---|---|---|---|
| `xiaozhuo_1x1` | P85 | 小方桌 | 1×1 | `美术资产/家具/桌子/Sprite-短桌1.png` |
| `hongzhuo_1x1` | P86 | 红绸桌 | 1×1 | `美术资产/家具/桌子/Sprite-短桌2.png` |
| `baizhuo_1x1` | P87 | 白布桌 | 1×1 | `美术资产/家具/桌子/Sprite-短桌4.png` |
| `shuzhuo_1x1_top` | P88 | 书桌（俯视） | 1×1 | `美术资产/家具/桌子/Sprite-短桌3.png` |
| `gui_1x1` | P89 | 矮柜 | 1×1 | `美术资产/家具/柜子/Sprite-柜子2.png` |
| `changzhuo_2x1` | P90 | 长桌 | 2×1 | `美术资产/家具/桌子/Sprite-长桌1.png` |
| `cantang_3x1` | P91 | 餐桌 | 3×1 | `美术资产/家具/桌子/Sprite-餐桌1.png` |

manifest 改动：`props` 84 → **91** 条（`git diff` 纯新增 168 行 / 0 删除）。

## 2. B 档 · 图集切片（源 32 张图集，已取件 13 张 / 60 切片，已落盘）

切图方法：alpha 8 连通域 → 包围盒吸附 32 网格 → 贪心合并相交框 → 候选表 `lab/_cls_atlas_cands.json`
→ 逐个目视核对编号与 @x,y 网格位置 → 裁紧内容 → 按 manifest 权威占地贴底。

| 源图集 | 切片数 | 取到的 id |
|---|---|---|
| `10_Birthday_party_32x32.png` | 2 | `xiaozhuo_2x1`、`changdeng_1x2` |
| `11_Halloween_32x32.png` | 2 | `denglong_1x1`、`paiwei_1x1` |
| `12_Kitchen_32x32.png` | 12 | `wangui_1x2`、`gui_1x1`、`jiutan_1x1`、`shuipen_1x1`、`shuichi_1x1`、`chaihuozao_1x1`、`anban_2x1` |
| `1_Generic_32x32.png` | 4 | `muxiang_1x1` |
| `2_LivingRoom_32x32.png` | 3 | `shuigang_1x1` |
| `3_Bathroom_32x32.png` | 3 | `dunbianqi_1x2` |
| `4_Bedroom_32x32.png` | 3 | `gui_2x1` |
| `5_Classroom_and_library_32x32.png` | 7 | `shujia_2x2`、`shujia_1x2`、`gui_1x2`、`shuzhuo_2x1` |
| `7_Art_32x32.png` | 7 | `deng_1x1`、`anban_2x1`、`penjing_1x1` |
| `9_Fishing_32x32.png` | 1 | `chaihuozao_1x1` |
| `Interior.png` | 14 | `shuangrenchuang_2x2`、`shujia_2x2`、`yi_1x1`、`gui_1x2`、`yigui_1x2`、`shujia_1x2`、`danrenchuang_2x1`、`xiaozhuo_2x1`、`deng_1x1`、`baxianzhuo_2x2`、`zhenglong_1x1` |
| `Interiors 13_768x768_TILESETS_B_C_D_E.png` | 1 | `shujia_2x2` |
| `Interiors 16_768x768_TILESETS_B_C_D_E.png` | 1 | `jiutan_1x1` |

### 2.1 切片编号 → 内容对照表

| # | 源图集 | 切片序号 | @x,y | 目标 id | 角色 | 落地文件 |
|---|---|---|---|---|---|---|
| 0 | `Interior.png` | #0 | 0,1 | `shuangrenchuang_2x2` | 变体 | `assets/village/_classmate/props/_variants/shuangrenchuang_2x2__Interior_0.png` |
| 1 | `Interior.png` | #2 | 3,1 | `shuangrenchuang_2x2` | 变体 | `assets/village/_classmate/props/_variants/shuangrenchuang_2x2__Interior_2.png` |
| 2 | `Interior.png` | #4 | 6,1 | `shuangrenchuang_2x2` | 变体 | `assets/village/_classmate/props/_variants/shuangrenchuang_2x2__Interior_4.png` |
| 3 | `Interior.png` | #6 | 10,1 | `shujia_2x2` | 主图 | `assets/village/_classmate/props/shujia_2x2.png` |
| 4 | `Interior.png` | #7 | 12,1 | `shujia_2x2` | 变体 | `assets/village/_classmate/props/_variants/shujia_2x2__Interior_7.png` |
| 5 | `Interior.png` | #9 | 16,2 | `yi_1x1` | 变体 | `assets/village/_classmate/props/_variants/yi_1x1__Interior_9.png` |
| 6 | `Interior.png` | #10 | 0,3 | `gui_1x2` | 变体 | `assets/village/_classmate/props/_variants/gui_1x2__Interior_10.png` |
| 7 | `Interior.png` | #11 | 5,3 | `yigui_1x2` | 主图 | `assets/village/_classmate/props/yigui_1x2.png` |
| 8 | `Interior.png` | #13 | 10,3 | `shujia_1x2` | 主图 | `assets/village/_classmate/props/shujia_1x2.png` |
| 9 | `Interior.png` | #16 | 7,4 | `danrenchuang_2x1` | 主图 | `assets/village/_classmate/props/danrenchuang_2x1.png` |
| 10 | `Interior.png` | #24 | 7,9 | `xiaozhuo_2x1` | 主图 | `assets/village/_classmate/props/xiaozhuo_2x1.png` |
| 11 | `Interior.png` | #25 | 0,10 | `deng_1x1` | 变体 | `assets/village/_classmate/props/_variants/deng_1x1__Interior_25.png` |
| 12 | `Interior.png` | #27 | 6,10 | `baxianzhuo_2x2` | 主图 | `assets/village/_classmate/props/baxianzhuo_2x2.png` |
| 13 | `Interior.png` | #38 | 5,14 | `zhenglong_1x1` | 主图 | `assets/village/_classmate/props/zhenglong_1x1.png` |
| 14 | `1_Generic_32x32.png` | #24 | 4,50 | `muxiang_1x1` | 变体 | `assets/village/_classmate/props/_variants/muxiang_1x1__1_Generic_32x32_24.png` |
| 15 | `1_Generic_32x32.png` | #25 | 5,50 | `muxiang_1x1` | 变体 | `assets/village/_classmate/props/_variants/muxiang_1x1__1_Generic_32x32_25.png` |
| 16 | `1_Generic_32x32.png` | #26 | 6,50 | `muxiang_1x1` | 变体 | `assets/village/_classmate/props/_variants/muxiang_1x1__1_Generic_32x32_26.png` |
| 17 | `1_Generic_32x32.png` | #27 | 7,50 | `muxiang_1x1` | 变体 | `assets/village/_classmate/props/_variants/muxiang_1x1__1_Generic_32x32_27.png` |
| 18 | `12_Kitchen_32x32.png` | #9 | 4,11 | `wangui_1x2` | 主图 | `assets/village/_classmate/props/wangui_1x2.png` |
| 19 | `12_Kitchen_32x32.png` | #11 | 6,11 | `wangui_1x2` | 变体 | `assets/village/_classmate/props/_variants/wangui_1x2__12_Kitchen_32x32_11.png` |
| 20 | `12_Kitchen_32x32.png` | #18 | 0,12 | `gui_1x1` | 变体 | `assets/village/_classmate/props/_variants/gui_1x1__12_Kitchen_32x32_18.png` |
| 21 | `12_Kitchen_32x32.png` | #19 | 1,12 | `gui_1x1` | 变体 | `assets/village/_classmate/props/_variants/gui_1x1__12_Kitchen_32x32_19.png` |
| 22 | `12_Kitchen_32x32.png` | #20 | 2,12 | `gui_1x1` | 变体 | `assets/village/_classmate/props/_variants/gui_1x1__12_Kitchen_32x32_20.png` |
| 23 | `12_Kitchen_32x32.png` | #14 | 10,11 | `jiutan_1x1` | 主图 | `assets/village/_classmate/props/jiutan_1x1.png` |
| 24 | `12_Kitchen_32x32.png` | #22 | 10,12 | `jiutan_1x1` | 变体 | `assets/village/_classmate/props/_variants/jiutan_1x1__12_Kitchen_32x32_22.png` |
| 25 | `12_Kitchen_32x32.png` | #34 | 2,19 | `shuipen_1x1` | 主图 | `assets/village/_classmate/props/shuipen_1x1.png` |
| 26 | `12_Kitchen_32x32.png` | #38 | 2,21 | `shuichi_1x1` | 主图 | `assets/village/_classmate/props/shuichi_1x1.png` |
| 27 | `3_Bathroom_32x32.png` | #19 | 8,12 | `dunbianqi_1x2` | 主图 | `assets/village/_classmate/props/dunbianqi_1x2.png` |
| 28 | `3_Bathroom_32x32.png` | #20 | 9,12 | `dunbianqi_1x2` | 变体 | `assets/village/_classmate/props/_variants/dunbianqi_1x2__3_Bathroom_32x32_20.png` |
| 29 | `3_Bathroom_32x32.png` | #21 | 10,12 | `dunbianqi_1x2` | 变体 | `assets/village/_classmate/props/_variants/dunbianqi_1x2__3_Bathroom_32x32_21.png` |
| 30 | `2_LivingRoom_32x32.png` | #3 | 0,9 | `shuigang_1x1` | 变体 | `assets/village/_classmate/props/_variants/shuigang_1x1__2_LivingRoom_32x32_3.png` |
| 31 | `2_LivingRoom_32x32.png` | #4 | 1,9 | `shuigang_1x1` | 变体 | `assets/village/_classmate/props/_variants/shuigang_1x1__2_LivingRoom_32x32_4.png` |
| 32 | `2_LivingRoom_32x32.png` | #5 | 2,9 | `shuigang_1x1` | 变体 | `assets/village/_classmate/props/_variants/shuigang_1x1__2_LivingRoom_32x32_5.png` |
| 33 | `5_Classroom_and_library_32x32.png` | #0 | 1,0 | `shujia_2x2` | 变体 | `assets/village/_classmate/props/_variants/shujia_2x2__5_Classroom_and_library_32x32_0.png` |
| 34 | `5_Classroom_and_library_32x32.png` | #9 | 0,4 | `shujia_1x2` | 变体 | `assets/village/_classmate/props/_variants/shujia_1x2__5_Classroom_and_library_32x32_9.png` |
| 35 | `5_Classroom_and_library_32x32.png` | #10 | 1,4 | `shujia_1x2` | 变体 | `assets/village/_classmate/props/_variants/shujia_1x2__5_Classroom_and_library_32x32_10.png` |
| 36 | `5_Classroom_and_library_32x32.png` | #11 | 0,7 | `gui_1x2` | 变体 | `assets/village/_classmate/props/_variants/gui_1x2__5_Classroom_and_library_32x32_11.png` |
| 37 | `5_Classroom_and_library_32x32.png` | #14 | 12,10 | `gui_1x2` | 变体 | `assets/village/_classmate/props/_variants/gui_1x2__5_Classroom_and_library_32x32_14.png` |
| 38 | `5_Classroom_and_library_32x32.png` | #15 | 13,10 | `shuzhuo_2x1` | 主图 | `assets/village/_classmate/props/shuzhuo_2x1.png` |
| 39 | `4_Bedroom_32x32.png` | #24 | 0,31 | `gui_2x1` | 主图 | `assets/village/_classmate/props/gui_2x1.png` |
| 40 | `4_Bedroom_32x32.png` | #26 | 0,33 | `gui_2x1` | 变体 | `assets/village/_classmate/props/_variants/gui_2x1__4_Bedroom_32x32_26.png` |
| 41 | `4_Bedroom_32x32.png` | #28 | 0,35 | `gui_2x1` | 变体 | `assets/village/_classmate/props/_variants/gui_2x1__4_Bedroom_32x32_28.png` |
| 42 | `7_Art_32x32.png` | #10 | 3,2 | `deng_1x1` | 变体 | `assets/village/_classmate/props/_variants/deng_1x1__7_Art_32x32_10.png` |
| 43 | `7_Art_32x32.png` | #11 | 5,2 | `deng_1x1` | 变体 | `assets/village/_classmate/props/_variants/deng_1x1__7_Art_32x32_11.png` |
| 44 | `7_Art_32x32.png` | #12 | 7,2 | `deng_1x1` | 变体 | `assets/village/_classmate/props/_variants/deng_1x1__7_Art_32x32_12.png` |
| 45 | `7_Art_32x32.png` | #16 | 3,4 | `anban_2x1` | 主图 | `assets/village/_classmate/props/anban_2x1.png` |
| 46 | `7_Art_32x32.png` | #17 | 5,4 | `anban_2x1` | 变体 | `assets/village/_classmate/props/_variants/anban_2x1__7_Art_32x32_17.png` |
| 47 | `11_Halloween_32x32.png` | #17 | 0,4 | `denglong_1x1` | 主图 | `assets/village/_classmate/props/denglong_1x1.png` |
| 48 | `11_Halloween_32x32.png` | #19 | 11,4 | `paiwei_1x1` | 主图 | `assets/village/_classmate/props/paiwei_1x1.png` |
| 49 | `10_Birthday_party_32x32.png` | #15 | 3,2 | `xiaozhuo_2x1` | 变体 | `assets/village/_classmate/props/_variants/xiaozhuo_2x1__10_Birthday_party_32x32_15.png` |
| 50 | `9_Fishing_32x32.png` | #25 | 8,9 | `chaihuozao_1x1` | 变体 | `assets/village/_classmate/props/_variants/chaihuozao_1x1__9_Fishing_32x32_25.png` |
| 51 | `12_Kitchen_32x32.png` | #30 | 2,16 | `chaihuozao_1x1` | 变体 | `assets/village/_classmate/props/_variants/chaihuozao_1x1__12_Kitchen_32x32_30.png` |
| 52 | `5_Classroom_and_library_32x32.png` | #1 | 3,0 | `shujia_2x2` | 变体 | `assets/village/_classmate/props/_variants/shujia_2x2__5_Classroom_and_library_32x32_1.png` |
| 53 | `Interiors 13_768x768_TILESETS_B_C_D_E.png` | #1 | 3,11 | `shujia_2x2` | 变体 | `assets/village/_classmate/props/_variants/shujia_2x2__Interiors_13_768x768_TILESETS_B_C_D_E_1.png` |
| 54 | `Interiors 16_768x768_TILESETS_B_C_D_E.png` | #7 | 14,19 | `jiutan_1x1` | 变体 | `assets/village/_classmate/props/_variants/jiutan_1x1__Interiors_16_768x768_TILESETS_B_C_D_E_7.png` |
| 55 | `12_Kitchen_32x32.png` | #23 | 0,13 | `anban_2x1` | 变体 | `assets/village/_classmate/props/_variants/anban_2x1__12_Kitchen_32x32_23.png` |
| 56 | `12_Kitchen_32x32.png` | #31 | 0,17 | `anban_2x1` | 变体 | `assets/village/_classmate/props/_variants/anban_2x1__12_Kitchen_32x32_31.png` |
| 57 | `7_Art_32x32.png` | #8 | 0,2 | `penjing_1x1` | 主图 | `assets/village/_classmate/props/penjing_1x1.png` |
| 58 | `7_Art_32x32.png` | #14 | 0,4 | `penjing_1x1` | 变体 | `assets/village/_classmate/props/_variants/penjing_1x1__7_Art_32x32_14.png` |
| 59 | `10_Birthday_party_32x32.png` | #12 | 5,1 | `changdeng_1x2` | 主图 | `assets/village/_classmate/props/changdeng_1x2.png` |

### 2.2 B 档未取件图集（19 张）

| 源图集 | 像素尺寸 | 原因 |
|---|---|---|
| `6_Music_and_sport_32x32.png` | 512×640 | 56 个候选里绝大多数是**乐器/画框/奖牌**等与 manifest 家具 id 无对应关系；只有 2 张长凳可对，但样式与 manifest 家具语义不合 |
| `8_Gym_32x32.png` | 256×272 | 256×272 体育器材图集，连通域检出的候选全为 >3 格（器材成组摆放），无可用单件 |
| `Interiors 0_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `Interiors 10_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `Interiors 11_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `Interiors 12_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `Interiors 14_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `Interiors 15_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `Interiors 17_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `Interiors 1_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `Interiors 2_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `Interiors 3_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `Interiors 4_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `Interiors 5_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `Interiors 6_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `Interiors 7_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `Interiors 8_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `Interiors 9_768x768_TILESETS_B_C_D_E.png` | 768×768 | 768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射 |
| `家具.png` | 256×256 | 256×256 混合家具大图，**alpha 连通域检不出候选（0 候选）**——内容之间互相紧贴无透明缝，需人工逐个框选；本轮未做 |

## 3. C 档 · 房屋 / 地皮 / 树 / 主角（19 张，只出方案，**不落盘**）

理由：这些是 tileset / 组件 / 序列帧，要拼成 D6 规格的整栋 `base`/`roof`（如 640×448）
工作量与风格对齐成本都很高，且本线纪律明确不写入 `assets/village/`。
以下为**拼装方案**，供后续专案使用。

| 源文件 | 像素尺寸 | 能提供什么 | 怎么用 | 还缺什么 |
|---|---|---|---|---|
| `主角/Sprite-主角-Sheet.png` | 1152×32 | 主角序列帧 | 1152×32 = 36 帧横排，每帧 32×32（帧间留 0~20px 空隙，实为等距 32px 步进） | 缺：player.gd 纯代码画圆，无贴图消费点；接序列帧需先改视觉机制线 |
| `地皮/GK_A2_CCautotile_1.png` | 768×576 | 地面 autotile | 768×576 = 24×18 格；可做地面自动拼接 | 缺：对应 scene 的 ground_*_tiles.png（单格 32×32），需重切 |
| `地皮/GK_A5_CCfloors_1.png` | 384×768 | 地面 floors tileset | 384×768 = 12×24 格 | 缺：同上 |
| `地皮/GK_C_CC_1.png` | 511×511 | 地面 tileset | 511×511；非 32 整数倍 | 缺：尺寸不规整，需重新切分 |
| `房屋/GK_B_CC_1.png` | 768×768 | 房屋整栋 tileset | 768×768 = 24×24 格；含屋顶/墙面/地板整块 | 缺：这是 24×24 格的自成体系尺寸，与游戏 20×13 / 18×13 等房屋尺寸不匹配 |
| `房屋/GK_D_CC_1.png` | 768×768 | 房屋整栋 tileset | 768×768 = 24×24 格；另一种风格 | 缺：同上 |
| `房屋/TopDownHouse_FurnitureState2.png` | 208×288 | 家具状态贴图集 | 208×288 = 6.5×9 格；俯视家具状态 | 缺：非 32 整数倍宽，网格切图需特殊处理 |
| `房屋/tileB_farmA.png` | 512×512 | 农田 tileset | 512×512 = 16×16 格；对应 scene 的 field_* | 缺：与 AI field_patch_tiles.png 风格不同，替换需重做田块布局 |
| `房屋/tileB_farmB.png` | 768×768 | 农田 tileset | 768×768 = 24×24 格；农田变体 | 缺：同上 |
| `房屋/tileB_fortA.png` | 512×512 | 围墙/要塞 tileset | 512×512 = 16×16 格 | 缺：manifest 无对应 id |
| `房屋/tileB_fortB.png` | 512×512 | 围墙/要塞 tileset | 512×512 = 16×16 格；变体 | 缺：同上 |
| `房屋/地板.png` | 128×128 | 房屋 base 地板层 | 4×4 = 32px 地砖，可铺满 base 的 floor 区域；D6 base 画布 640×416(=20×13格) 需重复铺贴 | 缺：与游戏现有地面色 (#6e7a4c) 的色差需美术确认 |
| `房屋/地毯.png` | 192×384 | 房屋 base 装饰层 | 6×12 = 32px 地毯，192×384；可作室内装饰叠加 | 缺：与 manifest 无对应 id，暂不入库 |
| `房屋/墙面.png` | 192×192 | 房屋 base 墙面层 | 6×6 = 32px 墙砖，含门窗贴图；对应 manifest shell 的 layer='base' 中的『墙』段 | 缺：门窗贴图风格与 AI 图不一致 |
| `房屋/屋檐1.png` | 320×144 | 房屋 roof 屋顶层 | 10×4.5 格 = 320×144；对应 shell layer='roof' 的『屋顶』段 | 缺：需按房屋尺寸 (20×13 等) 平铺拼接 |
| `房屋/屋檐2.png` | 192×384 | 房屋 roof 屋顶层 | 6×12 = 192×384；备用檐口样式 | 缺：同屋檐1 |
| `房屋/屋檐3.png` | 192×384 | 房屋 roof 屋顶层 | 6×12 = 192×384；第三种檐口 | 缺：同屋檐1 |
| `树/Redtree8.png` | 64×64 | 红树变体 | 64×64 = 2×2 格 | 缺：同上 |
| `树/tree.png` | 96×128 | 树 / scene tree_a* | 96×128 = 3×4 格；对应 scene 的 tree_a1(2×2)/a2(4×4)/a3(6×6) | 缺：树冠有 3 态(春/夏/秋)，且 game 侧 scene 树占位比源图大 |

### 3.1 房屋整栋拼装草图（示意，不落盘）

```
D6 base 画布 = 占地宽×32 × (占地高×32 + 32)   例：lu_house 20×13 → 640×448

  ┌─────────────────────────────────────────────┐  ← cpx 640×448
  │  roof 层  ← 屋檐1/2/3.png 平铺（320×144 起）  │     渲染时叠在 base 之上
  ├─────────────────────────────────────────────┤  ← px 640×416
  │  墙 层    ← 墙面.png 6×6 墙砖 + 门窗贴图      │
  │  家具层  ← 家具.png / A、B 档切片            │
  │  地 层    ← 地板.png 4×4 地砖 平铺            │
  └─────────────────────────────────────────────┘

  现状提示：world_view.gd:366 只真实绘制 roof；:239 的 base 只当开关不贴图。
  ⇒ 即使 C 档拼完，游戏里当前也只看得到 roof。
```

### 3.2 主角序列帧

- `Sprite-主角-Sheet.png` = 1152×32，**36 帧等距 32px 步进**（非空列段实测 36 段，步进 32px）。
- 帧内容：站立 / 行走 / 做事等若干循环，**没有现成的方向分组标记**，需要同学补一张帧序表。
- 引擎侧 `player.gd` 是纯代码 `draw_self()` 画圆，**没有贴图消费点**。
- 结论：接序列帧必须先由视觉机制线加贴图消费点，本线不越界改 `scripts/`。

## 4. 未映射清单与理由

### 4.1 源图 → 未映射

- B 档 19 张图集未取件：见 §2.2（`Interiors 0..17` 18 张 + `家具.png` + `8_Gym`），
  其中 `6_Music_and_sport` 与 `家具.png` 也不含可映射单件。
- C 档 19 张：按纪律**只出方案不落盘**，映射关系已登记在 §3。
- **实际未映射源文件 = 19 张 B 档图集 + 19 张 C 档 = 38 张**；
  C 档有明确拼装方案（§3），B 档 19 张是『图集级素材不适合做单件』或『需人工逐框』。

### 4.2 manifest id → 尚无同学图（52 个，共 91 个 props id）

| manifest id | 占地 | uses | 名称 |
|---|---|---|---|
| `liangdun_2x2` | 2×2 | 7 | 粮囤 |
| `maofang_3x2` | 3×2 | 6 | 茅房 |
| `shuangrenchuang_3x3` | 3×3 | 4 | 双人床 |
| `changdeng_2x1` | 2×1 | 4 | 长凳 |
| `baxianzhuo_2x3` | 2×3 | 3 | 八仙桌 |
| `zaotai_1x4` | 1×4 | 3 | 灶台 |
| `zhiwutai_1x1` | 1×1 | 3 | 置物台 |
| `laojing_1x1` | 1×1 | 3 | 老井 |
| `zhangzhuo_1x4` | 1×4 | 3 | 账桌 |
| `qiangji_ankan_1x4` | 1×4 | 2 | 墙基暗龛 |
| `pingfeng_1x2` | 1×2 | 2 | 屏风 |
| `jiu_muxiang_1x1` | 1×1 | 2 | 旧木箱 |
| `tiaoan_1x3` | 1×3 | 2 | 条案 |
| `shimo_2x4` | 2×4 | 2 | 石磨 |
| `zuzong_paiwei_2x3` | 2×3 | 2 | 祖宗牌位 |
| `huapen_1x1` | 1×1 | 2 | 花盆 |
| `tengyi_1x1` | 1×1 | 2 | 藤椅 |
| `bianmin_tai_2x1` | 2×1 | 1 | 便民服务台 |
| `daota_zaotai_1x4` | 1×4 | 1 | 倒塌的灶台残砖 |
| `nongjujia_2x1` | 2×1 | 1 | 农具架 |
| `deng_1x3` | 1×3 | 1 | 凳 |
| `danjuji_suanpan_2x1` | 2×1 | 1 | 单据柜+算盘 |
| `tuyuancang_3x3` | 3×3 | 1 | 土圆仓 |
| `tupi_zaotai_2x1` | 2×1 | 1 | 土坯灶台 |
| `tangwu_diji_2x3` | 2×3 | 1 | 堂屋地基痕迹 |
| `xiao_yigui_1x2` | 1×2 | 1 | 小衣柜 |
| `tingshu_2x2` | 2×2 | 1 | 庭树 |
| `qizhi_shimo_2x2` | 2×2 | 1 | 弃置石磨 |
| `gongtong_1x1` | 1×1 | 1 | 恭桶 |
| `tangcipen_1x1` | 1×1 | 1 | 搪瓷盆 |
| `jiu_muchuang_1x2` | 1×2 | 1 | 旧木床 |
| `shaixi_2x1` | 2×1 | 1 | 晒席 |
| `mutiaoban_jimapai_2x1` | 2×1 | 1 | 木跳板+记码牌 |
| `tiaodeng_1x1` | 1×1 | 1 | 条凳 |
| `shuini_fengceng_1x1` | 1×1 | 1 | 水泥封层 |
| `xishoupen_1x1` | 1×1 | 1 | 洗手盆 |
| `liushai_1x1` | 1×1 | 1 | 溜筛 |
| `denglong_1x4` | 1×4 | 1 | 灯笼 |
| `zaotai_1x2` | 1×2 | 1 | 灶台 |
| `penjing_1x4` | 1×4 | 1 | 盆景 |
| `shizhuo_2x1` | 2×1 | 1 | 石桌 |
| `bangcheng_2x1` | 2×1 | 1 | 磅秤 |
| `liangdun_1x1` | 1×1 | 1 | 粮囤 |
| `tengyi_1x4` | 1×4 | 1 | 藤椅 |
| `fengwomeilu_1x4` | 1×4 | 1 | 蜂窝煤炉 |
| `zhangzhuo_2x1` | 2×1 | 1 | 账桌 |
| `tieguo_1x1` | 1×1 | 1 | 铁锅 |
| `fengche_2x1` | 2×1 | 1 | 风车 |
| `yanliangtai_2x1` | 2×1 | 1 | 验粮台+取样铁管 |
| `yanliangqi_1x1` | 1×1 | 1 | 验粮器 |
| `jilong_2x1` | 2×1 | 1 | 鸡笼 |
| `madai_1x1` | 1×1 | 1 | 麻袋 |

> 说明：这些 id 大多是**剧情专用道具**（石磨、粮囤、账桌、验粮台、风车…）或**大尺寸建筑构件**
> （灶台 1×4、墙基暗龛 1×4、藤椅 1×4），同学图里没有对应素材。
> 另：`shuangrenchuang_3x3`（3×3 双人床）同学只画了 2×2 版本，尺寸口径不同，**不强行缩放**。

## 5. 自检结果

**对照预览图（每格：左=同学手绘，右=AI 程序化图）**

| 文件 | 内容 |
|---|---|
| `lab/_classmate_compare_a.png` | A 档 19 张主图 vs AI 同 id 图 |
| `lab/_classmate_compare_a2.png` | A 档 4 张同学变体 vs AI 主图 |
| `lab/_classmate_compare_b.png` | B 档 60 条切片 vs AI 同 id 图 |
| `lab/_cls_pick_check.png` | B 档切片确认表（标 id/尺寸/图集#序号/角色） |
| `lab/_cls_c_sheet.png` | C 档 19 张源图目视接触表 |

生成脚本：`lab/_cls_compare.py`（对照图）、`lab/_cls_doc.py`（本文档，可重跑）。

| 检查项 | 结果 |
|---|---|
| 源文件覆盖 | 74/74 已登记（§1 A 档 23、§2 B 档 32、§3 C 档 19） |
| 交付尺寸 = manifest `(w*32)×(h*32+32)` | 84/84 通过 |
| 内容贴底（底行 = 画布高-1） | 84/84 通过 |
| Godot `--headless --import` | exit=0，无资源 ERROR（仅编辑器证书/设置目录告警，非项目问题） |
| `.import` 生成 | `_classmate/` 下 84 张 PNG 全部有 `.import` |
| 边界检查 | 只新增 `docs/ART-MAPPING-classmate.md`、`assets/village/_classmate/`、`lab/`；
|  | manifest 仅**新增** 7 条 props（P85–P91），未删改既有条目 |
| 未覆盖既有资产 | `assets/village/props/`、`houses/`、`scene/`、`scripts/*.gd`、`houses_data.json`、`frames.json` 均未改动 |

### 5.1 引擎消费点缺口（导入 ≠ 进游戏能看到）

- `scripts/world_view.gd:366` 只真实绘制 **roof**；`:239` 的 base 只当『有没有图』的开关，图本身不贴。
- `scripts/` 全目录对 **props / scene**（河/路/田/井/树）**零消费点**。
- `scripts/player.gd` 纯代码画圆，主角贴图无消费点。
⇒ 本线交付的 84 张家具图**在游戏里目前一张都看不到**；要看到必须等视觉机制线补消费点。

## 6. 替换建议清单（等本人拍板，本线**未执行**任何替换）

判定规则：

- **尺寸一致** = AI 目录 `assets/village/props/<id>.png` 存在且像素尺寸与同学图交付画布完全相同 → 直接换文件即可。
- **尺寸不同** = 同 id 但 AI 图规格与 manifest 不同 → 换之前要先对齐画布，否则会错位。
- **AI 无此图** = manifest 里有这个 id，但 AI 目录没出图 → 同学图属**纯补位**，不是替换。

| 同学图 id | 同学图文件 | 尺寸 | AI 对应图 | AI 尺寸 | 判定 | 建议 |
|---|---|---|---|---|---|---|
| `shuigang_1x1` | `assets/village/_classmate/props/shuigang_1x1.png` | 32×64 | `assets/village/props/shuigang_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `chaihuozao_1x1` | `assets/village/_classmate/props/chaihuozao_1x1.png` | 32×64 | `assets/village/props/chaihuozao_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `chaidui_1x1` | `assets/village/_classmate/props/chaidui_1x1.png` | 32×64 | `assets/village/props/chaidui_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `maokeng_1x1` | `assets/village/_classmate/props/maokeng_1x1.png` | 32×64 | `assets/village/props/maokeng_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `danrenchuang_1x2` | `assets/village/_classmate/props/danrenchuang_1x2.png` | 32×96 | `assets/village/props/danrenchuang_1x2.png` | 32×96 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `shuangrenchuang_2x2` | `assets/village/_classmate/props/shuangrenchuang_2x2.png` | 64×96 | `assets/village/props/shuangrenchuang_2x2.png` | 64×96 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `gui_1x2` | `assets/village/_classmate/props/gui_1x2.png` | 32×96 | `assets/village/props/gui_1x2.png` | 32×96 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `gui_1x1` | `assets/village/_classmate/props/gui_1x1.png` | 32×64 | — | — | **AI 无此图** | 纯补位：manifest 已登记该 id，AI 侧未出图，建议直接采用 |
| `muxiang_1x1` | `assets/village/_classmate/props/muxiang_1x1.png` | 32×64 | `assets/village/props/muxiang_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `luokuang_1x1` | `assets/village/_classmate/props/luokuang_1x1.png` | 32×64 | `assets/village/props/luokuang_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `yi_1x1` | `assets/village/_classmate/props/yi_1x1.png` | 32×64 | `assets/village/props/yi_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `deng_1x1` | `assets/village/_classmate/props/deng_1x1.png` | 32×64 | `assets/village/props/deng_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `xiaozhuo_1x1` | `assets/village/_classmate/props/xiaozhuo_1x1.png` | 32×64 | — | — | **AI 无此图** | 纯补位：manifest 已登记该 id，AI 侧未出图，建议直接采用 |
| `hongzhuo_1x1` | `assets/village/_classmate/props/hongzhuo_1x1.png` | 32×64 | — | — | **AI 无此图** | 纯补位：manifest 已登记该 id，AI 侧未出图，建议直接采用 |
| `shuzhuo_1x1_top` | `assets/village/_classmate/props/shuzhuo_1x1_top.png` | 32×64 | — | — | **AI 无此图** | 纯补位：manifest 已登记该 id，AI 侧未出图，建议直接采用 |
| `baizhuo_1x1` | `assets/village/_classmate/props/baizhuo_1x1.png` | 32×64 | — | — | **AI 无此图** | 纯补位：manifest 已登记该 id，AI 侧未出图，建议直接采用 |
| `shuzhuo_1x1` | `assets/village/_classmate/props/shuzhuo_1x1.png` | 32×64 | `assets/village/props/shuzhuo_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `changzhuo_2x1` | `assets/village/_classmate/props/changzhuo_2x1.png` | 64×64 | — | — | **AI 无此图** | 纯补位：manifest 已登记该 id，AI 侧未出图，建议直接采用 |
| `cantang_3x1` | `assets/village/_classmate/props/cantang_3x1.png` | 96×64 | — | — | **AI 无此图** | 纯补位：manifest 已登记该 id，AI 侧未出图，建议直接采用 |
| `shujia_2x2` | `assets/village/_classmate/props/shujia_2x2.png` | 64×96 | `assets/village/props/shujia_2x2.png` | 64×96 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `yigui_1x2` | `assets/village/_classmate/props/yigui_1x2.png` | 32×96 | `assets/village/props/yigui_1x2.png` | 32×96 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `shujia_1x2` | `assets/village/_classmate/props/shujia_1x2.png` | 32×96 | `assets/village/props/shujia_1x2.png` | 32×96 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `danrenchuang_2x1` | `assets/village/_classmate/props/danrenchuang_2x1.png` | 64×64 | `assets/village/props/danrenchuang_2x1.png` | 64×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `xiaozhuo_2x1` | `assets/village/_classmate/props/xiaozhuo_2x1.png` | 64×64 | `assets/village/props/xiaozhuo_2x1.png` | 64×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `baxianzhuo_2x2` | `assets/village/_classmate/props/baxianzhuo_2x2.png` | 64×96 | `assets/village/props/baxianzhuo_2x2.png` | 64×96 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `zhenglong_1x1` | `assets/village/_classmate/props/zhenglong_1x1.png` | 32×64 | `assets/village/props/zhenglong_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `wangui_1x2` | `assets/village/_classmate/props/wangui_1x2.png` | 32×96 | `assets/village/props/wangui_1x2.png` | 32×96 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `jiutan_1x1` | `assets/village/_classmate/props/jiutan_1x1.png` | 32×64 | `assets/village/props/jiutan_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `shuipen_1x1` | `assets/village/_classmate/props/shuipen_1x1.png` | 32×64 | `assets/village/props/shuipen_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `shuichi_1x1` | `assets/village/_classmate/props/shuichi_1x1.png` | 32×64 | `assets/village/props/shuichi_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `dunbianqi_1x2` | `assets/village/_classmate/props/dunbianqi_1x2.png` | 32×96 | `assets/village/props/dunbianqi_1x2.png` | 32×96 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `shuzhuo_2x1` | `assets/village/_classmate/props/shuzhuo_2x1.png` | 64×64 | `assets/village/props/shuzhuo_2x1.png` | 64×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `gui_2x1` | `assets/village/_classmate/props/gui_2x1.png` | 64×64 | `assets/village/props/gui_2x1.png` | 64×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `anban_2x1` | `assets/village/_classmate/props/anban_2x1.png` | 64×64 | `assets/village/props/anban_2x1.png` | 64×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `denglong_1x1` | `assets/village/_classmate/props/denglong_1x1.png` | 32×64 | `assets/village/props/denglong_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `paiwei_1x1` | `assets/village/_classmate/props/paiwei_1x1.png` | 32×64 | `assets/village/props/paiwei_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `penjing_1x1` | `assets/village/_classmate/props/penjing_1x1.png` | 32×64 | `assets/village/props/penjing_1x1.png` | 32×64 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |
| `changdeng_1x2` | `assets/village/_classmate/props/changdeng_1x2.png` | 32×96 | `assets/village/props/changdeng_1x2.png` | 32×96 | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |

小结：**尺寸一致 31 个 / 尺寸不同 0 个 / AI 无此图 7 个**（共 38 个唯一 id）。

> 提醒：替换只解决**图**，不解决**看不到**的问题。
> 上面 §5.1 说得很直白——`scripts/` 目前对 props 零消费点，
> 即使全换了，游戏里依然一张都显示不出来。**建议先让视觉机制线把 props 消费点做掉，再回来替换**，
> 否则只是一次看不见的替换。

### 6.1 替换时必须人工过一眼的几张（已知风险点）

| id | 风险 | 说明 |
|---|---|---|
| `shuangrenchuang_3x3` | 规格不符 | manifest 是 3×3 双人床，同学只画了 2×2 版本 `shuangrenchuang_2x2`；**不缩放**，等同学补 3×3 |
| `gui_1x1` | 语义近似 | 同学画的是两层抽屉矮柜，manifest 的 `gui_1x2` 是四层竖柜，两者不是同一件家具 |
| `luokuang_1x1` | 语义近似 | 同学的是竹编扁箩筐/圆箩筐，manifest `luokuang` 口径需确认是否指『箩筐』而非『筐』 |
| `deng_1x1` | 语义近似 | 同学画的是圆草墩，manifest `deng` 若指木凳则需换 `yi_1x1` 或让同学补 |
| `shuzhuo_1x1` | 俯视/侧视混用 | 同学有两张书桌（侧视带抽屉、俯视摊纸笔），已拆成 `shuzhuo_1x1` 与 `shuzhuo_1x1_top`；游戏里用哪张取决于视角，**两者不可互换** |
| `chaihuozao_1x1` | 与剧情道具重合 | manifest 里另有 `zaotai_1x4`/`tupi_zaotai_2x1`/`daota_zaotai_1x4` 三个灶台 id，同学的柴火灶到底顶替哪一个，要美术/剧情定 |
| `danrenchuang_1x2` | 剧情优先度 | manifest 有 `danrenchuang_1x2`（用得多）与 `jiu_muchuang_1x2`（旧木床）两个，同学图偏『旧木床』质感，替换前确认要哪个调性 |

### 6.2 同学图的风格差距（替换前要有预期）

- 同学图是**带描边、有高光/阴影的精细像素画**；AI 图是**平涂色块**。同屏混用会明显不协调。
- 同学图多为**正面/等距 3/4 视角**，AI 图多为**俯视视角**。
⇒ 如果要做的是『整体换风格』，建议**一次性全换**而不是挑几张替换；
  如果只换一部分，需要先定一个过渡方案（例如先统一描边）。

