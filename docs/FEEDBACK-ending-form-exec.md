# 归档表（L15）执行反馈

- 任务书：`docs/PROMPT-ending-form-exec.md`（438 行）
- 下限 commit：`3f5bc49`；开工实测 HEAD `5387822`（合格）；交付时 HEAD `9ec040a`
- 交付状态：**只差接线**。`scripts/main.gd` **一个字没动**（L17 未交付 ⇒ 按 §5.2 跳第 ② 段 commit，接线补丁见 §5）

## 1. 交付物

| 文件 | 行数 | 职责 |
| --- | --- | --- |
| `scripts/ending_store.gd` | 286 | 填格状态 + 存档（`static var`，纯逻辑，不碰 UI） |
| `scripts/ending_report.gd` | 323 | 记述生成器：快照 → 三变体文本 + 两个出口（纯逻辑，不读文件） |
| `scripts/ending_form.gd` | 736 | 归档表界面（自绘 `Control`，无 `OptionButton` / `PopupMenu`）；**随时可开，抬头带填表进度** |
| `_mdtest/ending_check.gd` | 605 | 自检套件 E1–E14（含界面层），139 条断言 |

## 2. 验收（E1–E10）

`ENDING_CHECK_DONE fails=0`，`PASS=139`，进程 exit=0（`lab/_l15_after_ending.txt`）。

- **E1** 全填对（放任/间接故意、蓄谋/直接故意×2、蓄谋/无、无/无＋债务纠纷/1951/补丁下/二）⇒ 变体甲，**14 行逐行等于 story.md §10.3**（`_cmp_lines` 逐行比，报第一个不一致下标）。
- **E2** 1951 案性质＝杀人灭口 ⇒ 变体乙，`prose` 只剩两行，且「三十七笔 / 债务纠纷 / 五代之中 / 没有人被平反」一个字都不出现。
- **E3** 任一单选「无法确定」⇒ 变体丙，不报错、不弹错、状态不变；降级不改玩家填的值（填井下就还是井下）。
- **E4** 埋尸＝井下 ⇒ 按「井下」念，不会被「补丁下」顶掉；最早一具＝1926 也照念。
- **E5** 「第一起无起意。第四起无死者。」在甲乙丙三变体＋空白表的 `body` 里都出现（一行两句、中间无空格，与 story.md:702 一致）。
- **E6** 甲乙丙＋两出口全部扫禁用词，零命中；另有反向自检（故意塞一个必须抓到，防扫描器空转）。
- **E7** 两个出口原文与 story.md:751-757 一致；换出口不改正文；没选＝空串（不默认选）。
- **E8** 五帧归档员：1926 陈阿福 / 1951 陈志强 / 1976 陈卫东 / 2001 陈小军 / 2026 陈浩；未知帧回落陈浩；界面记住开表时的帧年份。
- **E9** 存档往返一致（十格＋四单选＋出口全保住）；脏 JSON ⇒ `load()` 返回 false 且状态仍空；结构对但值非法的格子合法值保留、非法值归空；文件不存在不崩；可覆盖写。
- **E10** 刚开局：十格＋四单选全空、出口没选（**没有默认值，也没有「哪个对」的提示**）。

额外补了 **E11–E14**（任务书没列，但界面是自绘的，不测等于没交付）：节点拿得到视口尺寸（不是 0×0，`PRESET_FULL_RECT` 生效）、循环改值能一路转回空格、↑↓ 按列走且环形、Tab/Shift+Tab 换格、记述区焦点只滚动不换格、填满立刻变甲、`max_scroll>0`、`commit_exit` 发 `exit_chosen` 且自己关表、关表也存盘、`mouse_filter` 开/关切换。**E14 是填表进度**：`fill_total()=14`、空表 0/14、只填三处就是 3/14（早开表也算数）、填满 14/14 且 `fill_ratio()=1.0`。

## 3. 七套回归

- 基线：开工时取（`lab/_l15_baseline.txt`，HEAD `5387822`），七套全绿。
- 复跑：交付前取（`lab/_l15_after_*.txt`，HEAD `9ec040a`），七套全部 **exit=0 / FAIL=0**：greybox / camera / hud_layout / asset_draw / sort / evidence_archive / display。
- 逐行比对脚本 `lab/_l15_cmp_after.py`：**唯一差异**是 greybox 的 `a4_2001` 行（`solids 646→812`、`hotspots 13→12`、`REACH_MOVE_BAND 88%→100%`）——来自期间并行落地的 A4 重排 commit `9ec040a`，**不是本线改动**；其余六套逐行完全一致。
- 本线四个新文件没有被任何既有脚本 `preload`/引用（`EndingForm|EndingStore|EndingReport` 的 grep 命中只在本线文件内），所以对七套回归在物理上不可能有影响。

## 4. 设计决定（请总策划过一眼）

1. **变体乙的 `body` 仍含固定两句，`prose` 只有两行。** E5 要求固定句在所有变体都在，E2 要求「后面整段消失只剩两句」——两者靠 `body`（含固定句，给人看）和 `prose`（只有变体专属正文，给断言）两个字段分开满足。理由是那两句是「表算出来的事实」，不随玩家填写改变，不属于「被降级掉的那一段」。
2. **变体丙只念「最早一具 / 埋尸位置 / 埋葬人数」三栏**，降掉「五代之中」「1951 段」「没有人被平反」；没填的栏念「未填」，不猜。
3. **「五代之中」四档统计按玩家填的那十格算**（表格不会替他填）；十格没填满 ⇒ 整行不出现（局部降级，不崩）。
4. **四档互斥且和恒为 5**：无/无＝不知情者；起意有、故意「无」＝算计而未动手者；直接故意＝动手者；其余（含放任＋间接故意）＝起意者。
5. **乙丙可叠加时以丙为准**（丙更宽：算不出来优先）。
6. 出口文本在 store 里存单一字符串，内部用 `\n` 分两行；E7 用 `.replace("\n","")` 与原文对齐。
7. **没有默认值**：选项表构造为 `[""] + 选项`，←→ 能一路转回空格；§10.1 的设计约束（不提示哪个对）靠这个保证。
8. 键位只用 **F**（开表/关表）＋ Esc / ↑↓ / ←→ / Tab / Shift+Tab / Enter，**没有新增 InputMap action**（改 project.godot 要重启编辑器），没占用 SHIFT/E/I/WASD。
9. 存档 `user://ending_form.json`，`res://.ending_form.json` 只作兜底（见 §6 第 6 条）。
10. **表随时可开，不是「结局专用」。** 开局就能按 F 打开、填已知的那几格；抬头右侧常驻「已填 n/14」，标题栏底边一条金色进度条按 `fill_ratio()` 走。理由（用户 2026-11-26 当面纠正）：本作的玩法是**反复切换年代搜集真相**，起点是 2026、没有固定的「终点站」，所以归档表必须是全程可写的工作台，而不是最后一关的一次性表单。
11. 「已填 n/14」只报**填了几格**，不报甲/乙/丙——报变体等于告诉玩家「你选到真相了」，spoiler（记述区本来就随填随变，玩家自己看文本即可）。

## 5. 接线补丁（等 L17 交付后由接线线落地，本线未落）

七处改动，均在 `scripts/main.gd`。**行号以 commit `6141ff8`/`768f36b` 之后的版本为准；L16 双日记线正在并行改同一个文件（J 键 + `_make_diary()`），落地前请按函数名重新定位。**

```gdscript
# ① preload 区，scripts/main.gd:19 之后
const EndingForm = preload("res://scripts/ending_form.gd")

# ② 状态区，scripts/main.gd:40-41 旁
var ending_form: Control = null      # 结案归档表（代码动态建，挂 Main 下）
var _ending_f_down := false          # F 键边沿检测（轮询，不用事件）

# ③ _ready()（scripts/main.gd:52）里 _make_archive() 调用之后加一行
	_make_ending_form()

# ④ _make_archive()（scripts/main.gd:81）旁边照抄一份
func _make_ending_form() -> void:
	ending_form = EndingForm.new()
	ending_form.name = "EndingForm"
	add_child(ending_form)
	ending_form.exit_chosen.connect(_on_ending_chosen)
	ending_form.form_closed.connect(_on_ending_closed)

# ⑤ _process()（scripts/main.gd:136）里 I 键那段（:169-178）之后照抄一份 F 键
	var form_now := false
	if Input.is_key_pressed(KEY_F) or Input.is_physical_key_pressed(KEY_F):
		form_now = true
	if form_now and not _ending_f_down and ending_form != null:
		ending_form.toggle(tl.current().year)
	_ending_f_down = form_now

# ⑥ early-return（scripts/main.gd:190-193）前面插一段同样的
	if ending_form != null and ending_form.is_open():
		player.walking = false
		_set_hud_hidden(true)
		return

# ⑦ 两个回调（放 _clear_hotspot() 附近，scripts/main.gd:354 旁）
func _on_ending_chosen(choice: String) -> void:
	print("[归档表] 落定出口：", choice)
	# 两段之间世界一模一样（story §10.5）—— 这里故意什么都不做

func _on_ending_closed() -> void:
	_set_hud_hidden(false)
	_clear_hotspot()
```

行为约定：开表 ⇒ 世界停（`player.walking=false` ＋ HUD 让开）；关表 ⇒ HUD 回来、热点清掉。`exit_chosen` 只打日志，不推进世界、不给奖励、不改任何状态。⑤ 里的 `tl.current().year` 就是「你在哪个年代开的表」，归档员跟着它变，所以**任何一站都能开，不限定 A5**。

## 6. 已知缺口 / 待拍板

1. **⚠️ 起点年代对不上（本线发现，需要拍板）。** 用户口径：**起点是 2026，没有终点，靠反复切换年代挖真相**。但当前代码 `scripts/timeline.gd:58` 是 `index = 0`，而 `data/frames.json` 的帧顺序是 `a1_1926 → a5_2026` ⇒ **进游戏实际站在 1926**；全仓库没有任何地方把 index 设到 4（`tl.index` 只被读来画色偏和 HUD）。`timeline.gd` / `frames.json` 都在本线禁改清单里，所以只报告不动手。
2. **「证物搜集进度条」不在本线。** 那是 HUD 层的常驻信息（`hud.gd` 禁改），数据源是 `evidence_store.gd`（也禁改）。本线只做了**归档表自己的填表进度**（已填 n/14 ＋ 标题栏进度条）；要 HUD 那条常驻进度，得另派一条线。
3. **HUD 上的「归档员 X」常驻行也不在本线**（`scripts/*.gd` 里目前没有「归档员」字样）。本线只保证归档表抬头按帧写对归档员——而且因为你反复切年代，同一个玩家在不同年代开表会看到不同归档员，这一点本身就是设计的一部分。
4. **界面单独不可达**：没有接线，F 键在游戏里打不开表。本线的 E11–E14 是把 `EndingForm` 直接 `add_child` 到 `SceneTree.root` 上测的（等价于主场景的兄弟层）。
5. **表是模态的**（Esc/F 才关，点面板外不关），刻意没做「点外面就关浮层」——填表途中误点外面会丢掉刚填的格。
6. **记述区不能鼠标拖动**，只能 ↑↓ 在记述区焦点上滚；滚轮可滚。
7. **沙箱实测：`user://` 写不进去**（启动日志 `Failed to open 'user://logs/…'`），所以 `save()` 落到 `res://.ending_form.json` 兜底，`EndingStore.SAVE_PATH` 仍是 `user://ending_form.json` 且是回退链第一站。真实玩家机器上不会走兜底。E9 因此断言「落到回退链某一站」并打印实际那一站，而不是硬断言 `user://`。
8. 变体文本的换行位置按 story.md 的段落走（空行也是一个元素），如果后面要做打字机效果，需要另加「逐字」层。

## 7. 没做的事（按用户本轮指令「只做新文件」）

- 没碰禁改清单里的任何文件（`git status --porcelain` 对着清单逐个查过，零命中）。
- 没提交 `lab/` 与 `_mdtest` 的临时产物；`git add` 只加本线四个文件 ＋ 本文档，**没有 `git add -A`**。
- 第 ② 段 commit（接线）没做：L17 未交付。