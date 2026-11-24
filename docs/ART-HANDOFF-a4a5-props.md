# A4/A5 家具贴图缺口清单（机器生成，勿手改）

> 本文件由 `lab/gen_props_table.py` 从 `_ref/houses/houses_data.json` + `_ref/art/_assets_a1a3/_a1a3_assets.json` 生成；改数据请改那两个源，别手改这里。

统计：A4/A5 六栋共 **193 种**「短名×占地」组合 —— manifest 里**已有 35 种**（其中 23 种占地完全一致可直接用、12 种尺寸不一致靠引擎缩放凑合），**完全缺图 158 种**，另有 **2 件线索家具虽然找得到近似图但尺寸不对**，按线索要求重画。

口径（与 `scripts/asset_draw.gd` 一致）：

- 画布 px ＝ 占地宽×32 × (占地高×32 + 32)，多出的一格在**顶部**，锚点**底边中心**。
- 目标文件名 ＝ `<拼音>_<宽>x<高>.png`，放到 `assets/village/props/`。
- ★ ＝ 可检视线索家具（玩家用 SHIFT 检视的关键物证），优先画。
- 批次：**P1 线索 > P3 高频（同件多处摆放）> P4 其余**。

## 1 缺图 / 重画清单（160 条）

| 批次 | 短名 | 占地 | 画布 px | 目标文件名 | 用在 | 线索 | 备注 |
|---|---|---|---|---|---|---|---|
| P1 | 上磨盘 | 2×1 | 64×64 | `shangmopan_2x1.png` | market | ★ | A4 2001 粮站拆出、暂放工地围挡角落，刻「沈氏丰源·一九五七」／A5 2026 摆进超市门厅（story §7.2⑥ 的现代物证）——… |
| P1 | 保险柜 | 1×2 | 32×96 | `baoxiangui_1x2.png` | shen_a4 | ★ | 账房 · 长边贴东墙，改稿底本锁在里面 |
| P1 | 保险柜 | 1×3 | 32×128 | `baoxiangui_1x3.png` | zhou_a4 | ★ | 卧室西南角 · 会计家的小保险柜，存着往来账的誊抄本（夹层原件 A5 才出土） |
| P1 | 招牌 | 2×1 | 64×64 | `zhaopai_2x1.png` | toyshop | ★ | 「本店由沈氏物业出租」· 店面北墙西端 · A5 铁证链一环 |
| P1 | 文件柜 | 1×2 | 32×96 | `wenjiangui_1x2.png` | market | ★ | A4 2001 在工地办公室 · 土地登记表第二联 + 改过的地质报告（写「地下有暗河，不宜大开挖」）／A5 2026 搬进超市办公室 ——… |
| P1 | 煤炉 | 1×2 | 32×96 | `meilu_1x2.png` | shen_a4 | ★（重画） | 现有 fengwomeilu_1x4.png 尺寸不对；灶间 · 1976 镇上家庭烧蜂窝煤（大件明面） |
| P1 | 账柜 | 2×1 | 64×64 | `zhanggui_2x1.png` | toyshop | ★ | 贴账房北墙 · 周有田往来账可能在此（位置待定，未定论） |
| P1 | 账桌 | 3×1 | 96×64 | `zhangzhuo_3x1.png` | shen_a4 | ★（重画） | 现有 zhangzhuo_1x4.png、zhangzhuo_2x1.png 尺寸不对；账房 · 沈建国在此改地质勘察报告，写「地下有暗河，不宜大开挖」，桩位绕开老井 |
| P3 | 便器 | 1×1 | 32×64 | `bianqi_1x1.png` | shen_a4、zhou_a4 |  | 净房 · 水冲蹲便（1976 干部楼带抽水设备） |
| P3 | 冰箱 | 1×1 | 32×64 | `bingxiang_1x1.png` | zhou_a4、zheng_a4 |  | 起居室 · 新添的冰箱 |
| P3 | 太师椅 | 1×1 | 32×64 | `taishiyi_1x1.png` | shen_a4 |  | 中堂 · 主客座 |
| P3 | 未拆封货架 | 1×3 | 32×128 | `weichaifenghuojia_1x3.png` | market |  | 大厅 · 未拆封（第二排） |
| P3 | 未拆封货架 | 1×4 | 32×160 | `weichaifenghuojia_1x4.png` | market |  | 大厅 · 货架裹着塑料膜，尚未上架 |
| P3 | 梳妆台 | 1×1 | 32×64 | `shuzhuangtai_1x1.png` | zhou_a4、zheng_a4 |  | 卧室 · 梳妆台 |
| P3 | 水桶 | 1×1 | 32×64 | `shuitong_1x1.png` | market、toyshop |  | 工棚 · 施工用水桶 |
| P3 | 沙发 | 2×1 | 64×64 | `shafa_2x1.png` | zhou_a4、zheng_a4 |  | 起居室 · 新添的布沙发，翻向后靠临街一侧 |
| P3 | 洗衣机 | 1×1 | 32×64 | `xiyiji_1x1.png` | zhou_a4、zheng_a4 |  | 院子角落 · 2001 年的新物件 |
| P3 | 电视柜 | 1×1 | 32×64 | `dianshigui_1x1.png` | zhou_a4、zheng_a4 |  | 起居室 · 电视柜 |
| P3 | 算盘 | 1×1 | 32×64 | `suanpan_1x1.png` | shen_a4、toyshop |  | 账房 · 算盘 |
| P3 | 茶几 | 1×1 | 32×64 | `chaji_1x1.png` | shen_a4、zhou_a4、zheng_a4 |  | 西厢客房 · 茶几 |
| P3 | 讲义筐 | 1×1 | 32×64 | `jiangyikuang_1x1.png` | school |  | 讲义筐 |
| P3 | 讲台 | 4×1 | 128×64 | `jiangtai_4x1.png` | school |  | 讲台正对黑板 |
| P3 | 课桌 | 2×1 | 64×64 | `kezhuo_2x1.png` | school |  | 教室一 |
| P3 | 课程表 | 2×1 | 64×64 | `kechengbiao_2x1.png` | school |  | 钉在教室北墙的课程表 |
| P3 | 货架 | 1×2 | 32×96 | `huojia_1x2.png` | shen_a4、toyshop |  | 耳房 · 货架，长边贴西墙 |
| P3 | 货架 | 3×1 | 96×64 | `huojia_3x1.png` | toyshop |  | 老货架 · 架上摆着旧货：陀螺、竹蜻蜓、弹弓 |
| P3 | 货箱 | 2×1 | 64×64 | `huoxiang_2x1.png` | market、toyshop |  | 仓库 · 未开封货箱 |
| P3 | 跑道 | 1×1 | 32×64 | `paodao_1x1.png` | school |  | 像素格逐格拼出的体育场形跑道（两段半圆＋中间直段） |
| P3 | 黑板 | 4×1 | 128×64 | `heiban_4x1.png` | school |  | 钉在教室北墙 |
| P4 | 主席台 | 8×2 | 256×96 | `zhuxitai_8x2.png` | school |  | 跑道北侧边上的高台 · 沈明远在这儿剪彩 |
| P4 | 书包架 | 1×1 | 32×64 | `shubaojia_1x1.png` | school |  | 挂书包的地方 |
| P4 | 书包架 | 1×2 | 32×96 | `shubaojia_1x2.png` | school |  | 挂书包的地方 |
| P4 | 会客椅 | 1×1 | 32×64 | `huikeyi_1x1.png` | zhou_a4 |  | 账房 · 来谈财务的客人坐这儿，不必进内屋 |
| P4 | 伞架 | 1×1 | 32×64 | `sanjia_1x1.png` | school |  | 门边的伞架 |
| P4 | 保险箱 | 1×1 | 32×64 | `baoxianxiang_1x1.png` | market |  | 办公室 · 工地保险箱 |
| P4 | 信报箱 | 1×1 | 32×64 | `xinbaoxiang_1x1.png` | zhou_a4 |  | 院里 · 订了报纸，沈氏会计要看账目公告 |
| P4 | 储物 | 1×1 | 32×64 | `chuwu_1x1.png` | zheng_a4 |  | 楼梯间杂物 · 让开 (11,2) 门口 |
| P4 | 儿童自行车 | 2×1 | 64×64 | `ertongzixingche_2x1.png` | toyshop |  | 落地陈列的大件 · 儿童自行车 |
| P4 | 公告板 | 1×2 | 32×96 | `gonggaoban_1x2.png` | school |  | 钉在门厅西墙 |
| P4 | 其他垃圾桶 | 1×1 | 32×64 | `qitalajitong_1x1.png` | toyshop |  | 垃圾分类 · 其他垃圾（灰桶），靠南墙一排 |
| P4 | 剪彩台 | 2×1 | 64×64 | `jiancaitai_2x1.png` | school |  | 剪彩用的条桌，紧挨主席台东端 |
| P4 | 办公桌 | 2×1 | 64×64 | `bangongzhuo_2x1.png` | toyshop |  | 账房办公 · 桌上算盘与流水 |
| P4 | 办公桌 | 3×1 | 96×64 | `bangongzhuo_3x1.png` | market |  | 办公室 · 工地办公桌 |
| P4 | 升旗台 | 2×2 | 64×96 | `shengqitai_2x2.png` | school |  | 跑道西北边 · 每周一升旗 |
| P4 | 单床 | 2×1 | 64×64 | `danchuang_2x1.png` | shen_a4 |  | 西厢客房 · 单人床，长边贴北墙 |
| P4 | 厨余垃圾桶 | 1×1 | 32×64 | `chuyulajitong_1x1.png` | toyshop |  | 垃圾分类 · 厨余垃圾（绿桶），靠南墙一排 |
| P4 | 可回收垃圾桶 | 1×1 | 32×64 | `kehuishoulajitong_1x1.png` | toyshop |  | 垃圾分类 · 可回收物（蓝桶），靠南墙一排 |
| P4 | 图书角 | 1×2 | 32×96 | `tushujiao_1x2.png` | school |  | 教室东墙的书架 |
| P4 | 图书角 | 2×2 | 64×96 | `tushujiao_2x2.png` | school |  | 教室东墙的书架 |
| P4 | 图纸桌 | 4×1 | 128×64 | `tuzhizhuo_4x1.png` | market |  | 办公室 · 摊开的施工图 |
| P4 | 圆桌 | 2×2 | 64×96 | `yuanzhuo_2x2.png` | shen_a4 |  | 长辈房 · 起坐圆桌 |
| P4 | 坐便器 | 1×1 | 32×64 | `zuobianqi_1x1.png` | zheng_a4 |  | 水冲坐便 · 新式卫生间 |
| P4 | 大床 | 2×2 | 64×96 | `dachuang_2x2.png` | zheng_a4 |  | 2001 新买的席梦思双人床 |
| P4 | 大床 | 3×3 | 96×128 | `dachuang_3x3.png` | shen_a4 |  | 长辈房 · 3×3 富家床，床头靠北墙 |
| P4 | 大柜 | 1×2 | 32×96 | `dagui_1x2.png` | shen_a4 |  | 耳房 · 储物大柜，长边贴东墙 |
| P4 | 大衣柜 | 1×2 | 32×96 | `dayigui_1x2.png` | zhou_a4 |  | 卧室 · 新添的大衣柜，贴西墙长边沿墙摆放 |
| P4 | 妆台 | 2×1 | 64×64 | `zhuangtai_2x1.png` | shen_a4 |  | 长辈房 · 梳妆台 |
| P4 | 安全帽架 | 1×2 | 32×96 | `anquanmaojia_1x2.png` | market |  | 门厅 · 安全帽 |
| P4 | 宣传栏 | 1×3 | 32×128 | `xuanchuanlan_1x3.png` | school |  | 钉在走廊东墙 · 贴通知 |
| P4 | 宣传栏 | 3×1 | 96×64 | `xuanchuanlan_3x1.png` | school |  | 钉在门厅与走廊之间的墙上 · 贴通知 |
| P4 | 小板凳 | 1×1 | 32×64 | `xiaobandeng_1x1.png` | toyshop |  | 门口的小板凳 |
| P4 | 工具箱 | 2×1 | 64×64 | `gongjuxiang_2x1.png` | market |  | 门厅 · 木工工具箱 |
| P4 | 工地椅 | 1×1 | 32×64 | `gongdiyi_1x1.png` | market |  | 办公室 · 折椅 |
| P4 | 工棚铺 | 3×1 | 96×64 | `gongpengpu_3x1.png` | market |  | 工棚 · 民工临时铺 |
| P4 | 床头柜 | 1×1 | 32×64 | `chuangtougui_1x1.png` | zhou_a4 |  | 卧室 · 床头柜 |
| P4 | 床头灯 | 1×1 | 32×64 | `chuangtoudeng_1x1.png` | zhou_a4 |  | 卧室 · 床头灯 |
| P4 | 废纸篓 | 1×1 | 32×64 | `feizhilou_1x1.png` | toyshop |  | 账房角落 |
| P4 | 建材堆 | 3×2 | 96×96 | `jiancaidui_3x2.png` | market |  | 工棚 · 零碎建材 |
| P4 | 彩电 | 1×1 | 32×64 | `caidian_1x1.png` | zhou_a4 |  | 2001 年的新物件 · 起居室彩电，翻向后与沙发相对 |
| P4 | 彩电柜 | 1×1 | 32×64 | `caidiangui_1x1.png` | zheng_a4 |  | 客厅彩电 · 让开 (9,5) 卫生间门口 |
| P4 | 手台 | 1×1 | 32×64 | `shoutai_1x1.png` | shen_a4 |  | 净房 · 洗手台 |
| P4 | 手推车 | 2×1 | 64×64 | `shoutuiche_2x1.png` | market |  | 通道 · 运砖手推车 |
| P4 | 手盆 | 1×1 | 32×64 | `shoupen_1x1.png` | shen_a4 |  | 净房 · 洗手盆 |
| P4 | 打印机 | 1×1 | 32×64 | `dayinji_1x1.png` | shen_a4 |  | 账房 · 打印改稿 |
| P4 | 扫帚 | 1×1 | 32×64 | `saozhou_1x1.png` | toyshop |  | 门口靠墙的扫帚 |
| P4 | 扫把 | 1×1 | 32×64 | `saba_1x1.png` | school |  | 走廊靠墙 |
| P4 | 折椅 | 1×1 | 32×64 | `zheyi_1x1.png` | market |  | 办公室 · 折椅 |
| P4 | 拆封样品 | 2×1 | 64×64 | `chaifengyangpin_2x1.png` | toyshop |  | 拆了包装的样品箱 |
| P4 | 拖把 | 1×1 | 32×64 | `tuoba_1x1.png` | school |  | 走廊东南角 |
| P4 | 指示牌 | 1×1 | 32×64 | `zhishipai_1x1.png` | school |  | 立着的指路牌 · 操场往南 |
| P4 | 捐建牌匾 | 4×1 | 128×64 | `juanjianpaibian_4x1.png` | school |  | 「沈氏捐建」牌匾钉在门厅外墙 · 他什么都不知道 |
| P4 | 捐款箱 | 1×1 | 32×64 | `juankuanxiang_1x1.png` | school |  | 村民捐建的心意箱 |
| P4 | 摇摇马 | 1×1 | 32×64 | `yaoyaoma_1x1.png` | toyshop |  | 门口 · 摇摇马，靠南墙摆门前给孩子试骑 |
| P4 | 摩托 | 2×1 | 64×64 | `motuo_2x1.png` | zheng_a4 |  | 院里停的摩托 · 先富起来的人家 |
| P4 | 收银台 | 3×1 | 96×64 | `shouyintai_3x1.png` | toyshop |  | 前门旁 · 算盘与找零抽屉 |
| P4 | 文件柜 | 1×1 | 32×64 | `wenjiangui_1x1.png` | zhou_a4 |  | 账房 · 保险柜挪进卧室后，账册再装一只文件柜 |
| P4 | 文件柜 | 2×1 | 64×64 | `wenjiangui_2x1.png` | shen_a4 |  | 账房 · 卷宗文件柜，长边贴南墙 |
| P4 | 文件箱 | 1×1 | 32×64 | `wenjianxiang_1x1.png` | zhou_a4 |  | 院子 · 装订好的旧账册，堆在文件箱里没扔 |
| P4 | 施工公告栏 | 3×1 | 96×64 | `shigonggonggaolan_3x1.png` | market |  | 门厅 · 施工公告与进度表 |
| P4 | 施工围挡 | 1×1 | 32×64 | `shigongweidang_1x1.png` | market |  | 南门口 · 施工围挡（院门西侧） |
| P4 | 旗杆 | 1×1 | 32×64 | `qigan_1x1.png` | school |  | 升旗台边上的旗杆（美术画成竖杆） |
| P4 | 旧台灯 | 1×1 | 32×64 | `jiutaideng_1x1.png` | toyshop |  | 桌上的旧台灯 |
| P4 | 旧招牌板 | 2×1 | 64×64 | `jiuzhaopaiban_2x1.png` | toyshop |  | 三代没换过的旧门板 · 靠在墙边 |
| P4 | 旧招牌架 | 2×1 | 64×64 | `jiuzhaopaijia_2x1.png` | toyshop |  | 门口 · 挂着的旧幌子，三代没换过 |
| P4 | 旧挂钟 | 1×1 | 32×64 | `jiuguazhong_1x1.png` | school |  | 钉在门厅西墙 |
| P4 | 旧衣柜 | 1×2 | 32×96 | `jiuyigui_1x2.png` | toyshop |  | 贴东墙 |
| P4 | 晾衣架 | 1×1 | 32×64 | `liangyijia_1x1.png` | zheng_a4 |  | 院子晾晒 |
| P4 | 暖水瓶 | 1×1 | 32×64 | `nuanshuiping_1x1.png` | toyshop |  | 账房角落 |
| P4 | 有害垃圾桶 | 1×1 | 32×64 | `youhailajitong_1x1.png` | toyshop |  | 垃圾分类 · 有害垃圾（红桶），靠南墙一排 |
| P4 | 木工台 | 2×1 | 64×64 | `mugongtai_2x1.png` | market |  | 大厅 · 现支木工台 |
| P4 | 木料堆 | 4×1 | 128×64 | `muliaodui_4x1.png` | market |  | 门厅 · 木料码放 |
| P4 | 条几 | 2×1 | 64×64 | `tiaoji_2x1.png` | shen_a4 |  | 门厅 · 迎客条几，长边贴北墙 |
| P4 | 板车 | 2×1 | 64×64 | `banche_2x1.png` | toyshop |  | 门口 · 卸货用的板车，靠南墙放 |
| P4 | 标语牌 | 6×1 | 192×64 | `biaoyupai_6x1.png` | school |  | 「好好学习 天天向上」钉在操场南围墙 |
| P4 | 桌 | 2×1 | 64×64 | `zhuo_2x1.png` | shen_a4 |  | 门房 · 门房桌，长边贴北墙 |
| P4 | 档案柜 | 1×1 | 32×64 | `danganggui_1x1.png` | toyshop |  | 贴西墙 · 旧账本 |
| P4 | 楼梯 | 2×3 | 64×128 | `louti_2x3.png` | zheng_a4 |  | 通往二层的楼梯 · 旧版照抄平房格局时完全缺失 |
| P4 | 橱柜 | 1×2 | 32×96 | `chugui_1x2.png` | zheng_a4 |  | 整体橱柜 · 现代厨房 |
| P4 | 水泥库 | 3×2 | 96×96 | `shuiniku_3x2.png` | market |  | 仓库 · 袋装水泥堆 |
| P4 | 水泥袋堆 | 3×2 | 96×96 | `shuinidaidui_3x2.png` | market |  | 门厅 · 水泥袋码放 |
| P4 | 淋浴 | 1×1 | 32×64 | `linyu_1x1.png` | zheng_a4 |  | 燃气热水器 · 不用再烧水 |
| P4 | 淋浴 | 1×3 | 32×128 | `linyu_1x3.png` | zhou_a4 |  | 独立卫生间 · 淋浴喷头，不再是院子里的旱厕 |
| P4 | 灰浆槽 | 2×1 | 64×64 | `huijiangcao_2x1.png` | market |  | 大厅 · 灰浆槽 |
| P4 | 煤气灶 | 1×1 | 32×64 | `meiqizao_1x1.png` | zheng_a4 |  | 液化气灶台 · 让开 (11,8) 门口 |
| P4 | 煤气灶 | 2×1 | 64×64 | `meiqizao_2x1.png` | zhou_a4 |  | 土坯灶台拆了 · 换煤气灶 |
| P4 | 煤油灯 | 1×1 | 32×64 | `meiyoudeng_1x1.png` | toyshop |  | 看店人自己留的灯 |
| P4 | 煤球堆 | 1×3 | 32×128 | `meiqiudui_1x3.png` | zhou_a4 |  | 院子角落 · 蜂窝煤，2001 年还在烧 |
| P4 | 瓷砖堆 | 2×1 | 64×64 | `cizhuandui_2x1.png` | market |  | 仓库 · 待贴瓷砖 |
| P4 | 电脑 | 1×1 | 32×64 | `diannao_1x1.png` | shen_a4 |  | 账房 · 2001 台式电脑 |
| P4 | 电话 | 1×1 | 32×64 | `dianhua_1x1.png` | zhou_a4 |  | 起居室 · 沈氏会计的电话，家里也装了一部 |
| P4 | 电钻台 | 1×2 | 32×96 | `dianzuantai_1x2.png` | market |  | 工棚 · 电钻台 |
| P4 | 石料堆 | 3×2 | 96×96 | `shiliaodui_3x2.png` | market |  | 门厅 · 碎石料堆 |
| P4 | 石榴 | 1×2 | 32×96 | `shiliu_1x2.png` | shen_a4 |  | 天井 · 庭树石榴 |
| P4 | 砂堆 | 3×1 | 96×64 | `shadui_3x1.png` | market |  | 仓库 · 黄砂 |
| P4 | 砂堆 | 3×2 | 96×96 | `shadui_3x2.png` | market |  | 门厅 · 黄砂堆 |
| P4 | 砂浆搅拌机 | 2×1 | 64×64 | `shajiangjiaobanji_2x1.png` | market |  | 大厅 · 施工机械 |
| P4 | 砂浆搅拌机 | 3×2 | 96×96 | `shajiangjiaobanji_3x2.png` | market |  | 门厅 · 小型搅拌机 |
| P4 | 砖垛 | 2×1 | 64×64 | `zhuanduo_2x1.png` | market |  | 仓库 · 红砖垛 |
| P4 | 空调 | 1×1 | 32×64 | `kongtiao_1x1.png` | zheng_a4 |  | 立式柜机·美术按贴墙 1×2 格出图（占地(8,8)，上沿(8,9)另占1格）·不压墙门 |
| P4 | 童车展示 | 2×1 | 64×64 | `tongchezhanshi_2x1.png` | toyshop |  | 落地陈列的大件 · 折叠童车，摆在店里给人看 |
| P4 | 签到处 | 2×1 | 64×64 | `qiandaochu_2x1.png` | school |  | 来宾签到的小桌 |
| P4 | 算盘柜 | 1×1 | 32×64 | `suanpangui_1x1.png` | zhou_a4 |  | 账房 · 算盘与账册收在柜里，谈账不必再进卧室 |
| P4 | 算盘盒 | 1×1 | 32×64 | `suanpanhe_1x1.png` | toyshop |  | 装旧算盘的盒子 |
| P4 | 红绸横幅 | 8×1 | 256×64 | `hongchouhengfu_8x1.png` | school |  | 红绸挂在主席台背后的墙上 · 题「沈氏捐建 村小落成」 |
| P4 | 纸箱 | 1×1 | 32×64 | `zhixiang_1x1.png` | toyshop |  | 角落的纸箱 |
| P4 | 纸箱堆 | 2×1 | 64×64 | `zhixiangdui_2x1.png` | toyshop |  | 纸箱堆 |
| P4 | 老货柜 | 3×1 | 96×64 | `laohuogui_3x1.png` | toyshop |  | 玻璃柜台 · 架上摆着镇店的旧货：拨浪鼓、铁皮青蛙、纸风车、木陀螺 |
| P4 | 脚手架 | 1×5 | 32×192 | `jiaoshoujia_1x5.png` | market |  | 通道 · 贴墙钢管脚手架 |
| P4 | 脚手架 | 1×6 | 32×224 | `jiaoshoujia_1x6.png` | market |  | 门厅 · 贴墙钢管脚手架 |
| P4 | 脸盆架 | 1×1 | 32×64 | `lianpenjia_1x1.png` | toyshop |  | 里屋西南角 |
| P4 | 自行车 | 2×1 | 64×64 | `zixingche_2x1.png` | zhou_a4 |  | 院里停放 · 周家上下班骑的车 |
| P4 | 花坛 | 2×1 | 64×64 | `huatan_2x1.png` | zheng_a4 |  | 院角花坛 · 不知道脚下埋着什么 |
| P4 | 花篮 | 1×1 | 32×64 | `hualan_1x1.png` | school |  | 剪彩摆的花篮 |
| P4 | 茶水柜 | 1×1 | 32×64 | `chashuigui_1x1.png` | zheng_a4 |  | 堂屋待客 |
| P4 | 荣誉榜 | 1×3 | 32×128 | `rongyubang_1x3.png` | school |  | 钉在走廊西墙 |
| P4 | 衣架 | 1×1 | 32×64 | `yijia_1x1.png` | shen_a4 |  | 门厅 · 衣帽架 |
| P4 | 被褥 | 2×1 | 64×64 | `beiru_2x1.png` | toyshop |  | 叠在床尾的旧被褥 |
| P4 | 警示牌 | 1×1 | 32×64 | `jingshipai_1x1.png` | market |  | 门厅 · 施工警示牌 |
| P4 | 账本堆 | 1×1 | 32×64 | `zhangbendui_1x1.png` | toyshop |  | 一摞流水账 |
| P4 | 货架 | 2×1 | 64×64 | `huojia_2x1.png` | toyshop |  | 货架列 · 架上摆着新货：遥控车配件、气球 |
| P4 | 货箱堆 | 2×1 | 64×64 | `huoxiangdui_2x1.png` | toyshop |  | 门口 · 等着搬进仓库的箱子 |
| P4 | 运料斗 | 2×1 | 64×64 | `yunliaodou_2x1.png` | market |  | 通道 · 斗车运料 |
| P4 | 钢筋堆 | 4×1 | 128×64 | `gangjindui_4x1.png` | market |  | 门厅 · 捆扎钢筋 |
| P4 | 铁皮柜 | 1×2 | 32×96 | `tiepigui_1x2.png` | toyshop |  | 贴西墙 · 上锁的柜子 |
| P4 | 鞋架 | 1×1 | 32×64 | `xiejia_1x1.png` | shen_a4 |  | 门厅 · 鞋架，进门换鞋（东南院门穿堂） |
| P4 | 鞋柜 | 1×1 | 32×64 | `xiegui_1x1.png` | zheng_a4 |  | 院门进门处 · 让开 (7,9) 入院通道 |
| P4 | 饭桌 | 2×1 | 64×64 | `fanzhuo_2x1.png` | zhou_a4 |  | 起居室 · 一家人吃饭的桌子，退到南侧内屋 |
| P4 | 饭桌 | 2×2 | 64×96 | `fanzhuo_2x2.png` | zheng_a4 |  | 一家人吃饭的圆桌 |
| P4 | 饮水机 | 1×1 | 32×64 | `yinshuiji_1x1.png` | school |  | 门厅角落 |
| P4 | 马扎 | 1×1 | 32×64 | `mazha_1x1.png` | toyshop |  | 小桌旁的马扎 |

## 2 已有可复用（33 条，不用画）

| 短名 | 占地 | 画布 px | 已有文件 | 状态 | 用在 |
|---|---|---|---|---|---|
| 书架 | 1×2 | 32×96 | `shujia_1x2.png` | ✅ 完全一致 | shen_a4、zhou_a4 |
| 书桌 | 2×1 | 64×64 | `shuzhuo_2x1.png` | ✅ 完全一致 | zheng_a4 |
| 八仙桌 | 2×2 | 64×96 | `baxianzhuo_2x2.png` | ✅ 完全一致 | shen_a4 |
| 凳 | 1×1 | 32×64 | `deng_1x1.png` | ✅ 完全一致 | shen_a4、zheng_a4 |
| 单人床 | 2×1 | 64×64 | `danrenchuang_2x1.png` | ✅ 完全一致 | zheng_a4、toyshop |
| 小桌 | 2×1 | 64×64 | `xiaozhuo_2x1.png` | ✅ 完全一致 | toyshop |
| 屏风 | 1×2 | 32×96 | `pingfeng_1x2.png` | ✅ 完全一致 | shen_a4 |
| 木箱 | 1×1 | 32×64 | `muxiang_1x1.png`、`jiu_muxiang_1x1.png` | ✅ 完全一致 | shen_a4 |
| 条案 | 1×3 | 32×128 | `tiaoan_1x3.png` | ✅ 完全一致 | zhou_a4 |
| 柜 | 1×2 | 32×96 | `gui_1x2.png` | ✅ 完全一致 | shen_a4 |
| 案板 | 2×1 | 64×64 | `anban_2x1.png` | ✅ 完全一致 | shen_a4 |
| 椅 | 1×1 | 32×64 | `yi_1x1.png` | ✅ 完全一致 | shen_a4、zheng_a4、toyshop |
| 水池 | 1×1 | 32×64 | `shuichi_1x1.png` | ✅ 完全一致 | shen_a4、zhou_a4、zheng_a4 |
| 水缸 | 1×1 | 32×64 | `shuigang_1x1.png` | ✅ 完全一致 | toyshop |
| 洗手盆 | 1×1 | 32×64 | `xishoupen_1x1.png` | ✅ 完全一致 | zhou_a4、zheng_a4 |
| 牌位 | 1×1 | 32×64 | `paiwei_1x1.png` | ✅ 完全一致 | shen_a4 |
| 石桌 | 2×1 | 64×64 | `shizhuo_2x1.png` | ✅ 完全一致 | shen_a4 |
| 碗柜 | 1×2 | 32×96 | `wangui_1x2.png` | ✅ 完全一致 | shen_a4 |
| 花盆 | 1×1 | 32×64 | `huapen_1x1.png` | ✅ 完全一致 | shen_a4 |
| 藤椅 | 1×1 | 32×64 | `tengyi_1x1.png` | ✅ 完全一致 | shen_a4 |
| 衣柜 | 1×2 | 32×96 | `yigui_1x2.png` | ✅ 完全一致 | shen_a4、zheng_a4 |
| 账桌 ★ | 2×1 | 64×64 | `zhangzhuo_2x1.png` | ✅ 完全一致 | zhou_a4 |
| 铁锅 | 1×1 | 32×64 | `tieguo_1x1.png` | ✅ 完全一致 | shen_a4 |
| 书桌 | 3×1 | 96×64 | `shuzhuo_1x1.png`、`shuzhuo_1x2.png`、`shuzhuo_2x1.png` | ⚠️ 尺寸不一致（缩放凑合） | shen_a4 |
| 双人床 | 3×2 | 96×96 | `shuangrenchuang_3x3.png`、`shuangrenchuang_2x2.png` | ⚠️ 尺寸不一致（缩放凑合） | zhou_a4 |
| 木箱 | 2×1 | 64×64 | `muxiang_1x1.png`、`jiu_muxiang_1x1.png` | ⚠️ 尺寸不一致（缩放凑合） | toyshop |
| 条案 | 3×1 | 96×64 | `tiaoan_1x3.png` | ⚠️ 尺寸不一致（缩放凑合） | shen_a4 |
| 柜 | 1×1 | 32×64 | `gui_1x2.png`、`gui_2x1.png` | ⚠️ 尺寸不一致（缩放凑合） | shen_a4 |
| 水缸 | 1×3 | 32×128 | `shuigang_1x1.png` | ⚠️ 尺寸不一致（缩放凑合） | zhou_a4 |
| 碗柜 | 1×1 | 32×64 | `wangui_1x2.png` | ⚠️ 尺寸不一致（缩放凑合） | zhou_a4 |
| 衣柜 | 1×1 | 32×64 | `yigui_1x2.png` | ⚠️ 尺寸不一致（缩放凑合） | shen_a4 |
| 酒坛 | 1×2 | 32×96 | `jiutan_1x1.png` | ⚠️ 尺寸不一致（缩放凑合） | shen_a4 |
| 长凳 | 3×1 | 96×64 | `changdeng_1x2.png`、`changdeng_2x1.png` | ⚠️ 尺寸不一致（缩放凑合） | school |

> 尺寸不一致的 12 条里，有 2 条是线索件（煤炉 1×2、账桌 3×1），已提到 P1 要求重画。

