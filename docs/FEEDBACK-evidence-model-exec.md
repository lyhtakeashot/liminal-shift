# L5 证物模型改造 · 执行反馈

任务书：`docs/PROMPT-evidence-model-exec.md`　开工 HEAD：`a025d99`　Godot v4.7.2.stable

**一句话**：证物从「一条一件」改成「**一件物件一张卡 · 卡内按年代追加观察**」——归一键让同一件东西跨年代认成同一张卡，
新年代就在卡里多一条观察；界面从平铺清单改成「卡列表 → 卡内观察记录」两级。实测 **27 张卡 / 58 条观察**。

## 1. 四项改动

### ① 归一键（`scripts/evidence_store.gd:44-95`）

规则 A 家具 = `<房屋族>::<家具名>`（`furniture_key()` :66）；规则 B 地标 = title 第一个「·」之前的部分（`landmark_key()` :74）；
规则 C 家具带 `族::`、地标不带 ⇒ 两边永不合卡（`normalize_key()` :84）。
新增 `const HOUSE_FAMILY`（:48）：`lu_house/lu_a2/lu_a3→lu`、`shen_a1..shen_a4→shen`、`mill_a1..mill_a3→mill`、
`zhou_house/zhou_a2/zhou_a3/zhou_a4→zhou`、`market→market`、`zheng_a4→zheng`、`school→school`、`toyshop→toyshop`。
**`zheng_a4` 独立成族**：与陆家同址但是另一户人家，story 上对旧事一无所知 ⇒ 不能合卡。

- **改前**：key = `house_id::家具名`（`mill_a1::账桌`）或 `title`（`老井 · 石板`）⇒ 换 id 就换卡、地标状态一变就丢旧记录。
- **改后**：`mill::账桌`（A1/A2/A3 同一张卡）、`老井`（`老井 · 石板`/`三层水泥`/`沥青补丁` 同一张卡）。
- `mill::老井`（磨坊院里那口井）与地标 `老井`（村口那口井）**永远是两张卡**——有意保留。

### ② 卡片结构 + 三态收集（`scripts/evidence_store.gd:9-27, 39-42, 97-139`）

卡结构 `{key, name(首次收集时的 title), order, observations:[{year,title,source,text,order}]}`。
`try_collect()` 改成三态（:39-42）：`RESULT_NEW_CARD`=1 首次见到 → 建卡 + 第 1 条观察；`RESULT_DUPLICATE`=0 同年代已记过 →
**什么都不做**；`RESULT_NEW_OBSERVATION`=2 新年代 → 该卡 observations **末尾追加一条**。
**改前**返回 bool、同 key 直接 false ⇒ 换个年代再看一次什么都留不下；**改后**每条观察保留自己的 `year/title/source/text`，
`source` 写法不变（家具 `%s · %d`、地标 `%d · 村中`）。

### ③ 界面两级化（`scripts/evidence_archive.gd`，484 行）

- 标题栏 :182：「已收集 %d 件」→「已收集 %d 件 · %d 条观察」（`title_summary()` :375）。
- 列表页 :203：一行 = 一条证据 → 一行 = **一张卡**（卡名 + 「新」角标 + 右对齐年份跨度 `1926 · 2026` + 首条观察摘要）。
- 详情页 :272：无 → 卡名 + 「已记录 %d 次观察」+ **按年代升序**的观察列表（`sorted_observations()` :384 / `detail_lines()` :420）。
- 滚动：列表固定 → 详情页可滚（`_max_scroll()` :441 改用真实行数）。
- footer :325：一行操作提示 → 两行（操作提示 + 「**世界已暂停 · 按 I 或 Esc 关闭档案**」）。
- toast :100：「新证物：X」→ 新卡「新证物：X」／新观察「新观察：X」。
- **「新」角标口径**（任务书允许自定）：**新增卡 + 新增观察都算新**。`pending_new()` 记账、`is_new_key(key)` 标卡，
  关档时 `clear_new_flags()` 结算清零。⇒ 老卡被追加观察后会重新亮「新」（内容变了，值得再看一眼）。

### ④ 开档时不响应 SHIFT / E（`scripts/main.gd:137-157`）

**改前** `shift_axis` 在 :100、`inspect` 在 :131，**都在档案暂停 return 之前** ⇒ 一边翻档案一边切时代、一边按 E 顺手收走新年代的证物；
**改后**两个分支整体挪到暂停 return **之后**（:151 `shift_axis`、:155 `inspect`）。
另 `main.gd:269/273` 改用 `furniture_key()` / `landmark_key()`；:276 `try_collect(key,title,source,text,f.year)` 拿三态，
`RESULT_DUPLICATE` 直接 return，否则 save() + `flash_collected()`。

## 2. 条数实测：**27 张卡 / 58 条观察**

真实代码路径实测（`Timeline.load_frames()` → `frame_data.setup()` → `house_shape.hotspots()` → `try_collect`，**不是 Python 仿真**）
输出 `PROBE cards=27 observations=58`。分卡：老槐/老井/界碑/坝/田 **各 5**（1926·1951·1976·2001·2026）；
`mill::账桌` 3、`mill::老井` 3、`mill::石磨` 2、`mill::墙基暗龛` 2、`zhou::小桌` 2、`zhou::账桌` 2、`shen::蜂窝煤炉` 2、
`market::文件柜` 2、`market::上磨盘` 2；其余 13 张各 1 条。
（显示名取首次收集时的 hotspot title：`mill::老井` 显示「磨坊 · 院里」、`超市工地` 显示「超市工地 · 南大门」、`路口` 显示「路口 · 红绿灯基座」。）

### 与任务书 §2.5「27 卡 / 39 观察」的差异说明

**卡数一致（27），观察数 58 ≠ 39。** §2.5 的 39 是**按唯一 title 去重**的旧口径（`lab/_evidence_count_b.py` 也这么数），
它列的多观察卡表只列了 8 张、漏掉老槐/界碑/坝/田。按 §2.2 规则表（「新年份 → 追加一条」），老槐在 1951/1976/2026 的变化
**本就该记下来**——§1 明确把「老槐五帧 title 都是『老槐』⇒ 1951 歪了、1976 露根、2026 一百岁全被丢掉」列为**要修的病**，
§1.1 也画出老槐 5 行。所以按 §2.2 实现就是 58 条；§2.5 的 39 是未按新规则重算的旧值（§2.5 原文即写「以你自己实测为准」
「对不上先查归一实现，再报告」）。已复查：**归一实现本身没有偏差**。## 3. 测试改造清单（`_mdtest/evidence_archive_check.gd`，530 行 / 122 处断言）

**改写的旧断言：**

| 原行 | 原期望 | 现期望 |
|---|---|---|
| :63-67 | 3 条、name 序列 | 3 张卡、name 序列不变（字段移到 `observations[0]`） |
| :86-92 | 3 条 / source 在条目上 | 3 卡 / 4 观察 / source 在 `observations[0]` |
| :196-197 | 条目上取 name/source | 从 `observations[0]` 取 |
| :202 二次检视 | 不新增 | 同年代二次检视：卡数、观察数都不变 |
| :227 A2 磨坊账桌 | **多一条**（卡数 2） | **卡数不变（1）**，该卡多一条 1951 观察 |
| :237-245 地标老井 | 多一条（卡数 3） | 卡数按序数变化，查 key=="老井" 的卡 |
| :249-258 老井·石板 | 多一条（卡数 4） | **归一到 `老井` 卡第 2 条观察**，卡数不变、观察 +1 |

**新增的 7 条（任务书 §3 点名要的）：**
① 跨年代同物件 ⇒ 卡数不变、观察 +1、年份序列 `[1926,1951]`、追加观察保留自己的 source；
② 同年代重复检视 ⇒ 卡数与观察数都不变（`RESULT_DUPLICATE`）；
③ 同房换 id 仍归一 ⇒ `mill_a1::账桌` + `mill_a2::账桌` ⇒ 1 卡 2 观察；
④ 家具与地标不混 ⇒ `mill::老井` ≠ `老井`；
⑤ 详情页按年代升序 ⇒ 故意按 2026→1951→1976 收集，`sorted_observations()` 与 `detail_lines()` 的年份行都断言 `[1951,1976,2026]`；
⑥ 开档时 SHIFT 不切时代、E 不检视 ⇒ `_archive_pauses_world()` :501，**每段前放反向对照**（档案关着时两键必须有效）；
⑦ 存档往返 ⇒ save → clear → load 后卡数 / 观察数 / 卡片顺序都不变。
另补 **v1 旧存档兼容**（读回不崩、归一为 `mill::账桌` 与 `老井`、年份从 source 解析）；
另补 **守卫断言**（:333）——`main.archive == null` 直接 FAIL，防止主场景初始化被别的脚本打断后「断言被静默跳过却仍打 EVIDENCE_OK」。

## 4. 回归结果

| 套件 | 结果 |
|---|---|
| `evidence_archive_check` | **PASS 111 / FAIL 0**，`EVIDENCE_CHECK_DONE fails=0` + `COLLECTED` + `NO_DUP` + `EVIDENCE_OK` |
| `greybox_check` | `UNEXPLAINED_BLOCKS=0`、`REACH_OK=true`、五帧热点 10/11/13/13/11 |
| `display_check` | `CONTENT_SCALE_MODE=1`、`ASPECT=1`、`SIZE=(1280,720)`、纹理过滤 0、`STRETCH_SCALE_MODE=0` |
| `camera_check` / `hud_layout_check` / `asset_draw_check` / `sort_check` / `interior_check` | 全部 `fails=0`（`CAMERA_CHECK_DONE` / `HUD_CHECK_DONE` / `ASSET_DRAW_CHECK_DONE` / `SORT_CHECK_DONE` / `RESULT: ALL PASS`） |

**测试坑（值得记）**：`Input.is_action_just_pressed()` 只在「按下那一帧的槽位」里为真——
`Input.action_press()` 之后 **await 一帧再查永远是 false**（引擎帧末清掉「刚按下」边沿）。
⇒ 依赖 just_pressed 的 headless 测试必须 `press → 同槽查 → release`，中间不能有 await。
⇒ 这也是本测试每条「开档不响应」断言前都加**反向对照**的原因：注入若失效，对照会先 FAIL，不会假通过。

## 5. 旧存档兼容

`SAVE_VERSION` 1 → 2，`load()` 按 `version` 分支：v2 走 `_load_card_v2()`（:262），v1 走 `_load_card_v1()`（:285）。
v1 旧存档每条 = 一件 = **一张卡 + 一条观察**，key 再归一一次（`mill_a1::账桌` → `mill::账桌`），
年份从 source 解析（`_year_from_source()` :315，`"磨坊 · 1926"` → 1926），解析不出当 0。
存档损坏 / 非法 JSON ⇒ 返回 false，档案保持空，不崩（:240-247）。

## 6. 遗留问题

1. **`scripts/world_view.gd` parse 失败（他线未提交 WIP，不属本线）**：`:431` 调用 `_circle_sort_y(sd)`，
   但该函数只在注释里出现、**没有定义** ⇒ parse error ⇒ `main._ready()` 中断 ⇒ `main.archive` 为 Nil ⇒
   主场景相关断言被静默跳过、脚本仍打 `EVIDENCE_OK`（**假通过**）。本线不碰该文件（任务书明令），
   回归时临时替换为 HEAD 版跑完再**按字节还原**（哈希已核对回原值）。本线已加守卫断言把这类假通过变成显式 FAIL。
2. **`scripts/house_shape.gd:375-377` 注释过期**：写着「磨坊数据里的『老井』rect [6,10] 已在 lot 下界之外」，
   但当前 `houses_data.json` 里老井 rect 是 `[6,12,1,1]`，落在 mill lot `[0,0,17,12]` 内 ⇒ `mill::老井` 卡**真实存在**。
   该文件属 L4 线独占，本线不能改，按当前数据为准。
3. **「新」角标口径**：新增卡 + 新增观察都算新（§1 ③）。若总策划希望「只有新卡才算新」，改 `pending_new()` 一处即可。
4. **观察追加在卡内末尾（收集顺序），展示时才按年代升序**：若玩家不按时间线顺序游玩，卡内观察的物理顺序与年代顺序会不一致
   —— 展示层已按年代排序，存档 `order` 字段记的仍是收集次序。
