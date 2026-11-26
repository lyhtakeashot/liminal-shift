# 归档表（L15）执行反馈

- 任务书：`docs/PROMPT-ending-form-exec.md`（438 行）
- 下限 commit：`3f5bc49`；开工实测 HEAD `5387822`（合格）；交付时 HEAD `9ec040a`
- 交付状态：**只差接线**。`scripts/main.gd` **一个字没动**（L17 未交付 ⇒ 按 §5.2 跳第 ② 段 commit，接线补丁见 §5）

## 1. 交付物

| 文件 | 行数 | 职责 |
| --- | --- | --- |
| `scripts/ending_store.gd` | 286 | 填格状态 + 存档（`static var`，纯逻辑，不碰 UI） |
| `scripts/ending_report.gd` | 323 | 记述生成器：快照 → 三变体文本 + 两个出口（纯逻辑，不读文件） |
| `scripts/ending_form.gd` | 695 | 归档表界面（自绘 `Control`，无 `OptionButton` / `PopupMenu`） |
| `_mdtest/ending_check.gd` | 590 | 自检套件 E1–E10 ＋ 界面层 E11–E13，132 条断言 |

## 2. 验收（E1–E10）

`ENDING_CHECK_DONE fails=0`，`PASS=132`，进程 exit=0（`lab/_l15_after_ending.txt`）。

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

额外补了 **E11–E13**（任务书没列，但界面是自绘的，不测等于没交付）：节点拿得到视口尺寸（不是 0×0，`PRESET_FULL_RECT` 生效）、循环改值能一路转回空格、↑↓ 按列走且环形、Tab/Shift+Tab 换格、记述区焦点只滚动不换格、填满立刻变甲、`max_scroll>0`、`commit_exit` 发 `exit_chosen` 且自己关表、关表也存盘、`mouse_filter` 开/关切换。

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

## 5. 接线补丁（等 L17 交付后由接线线落地，本线未落）

四处改动，均在 `scripts/main.gd`：

```gdscript
# ① preload 区，scripts/main.gd:16-19 之后
const EndingForm = preload("res://scripts/ending_form.gd")

# ② 状态区，scripts/main.gd:38-39 旁
var ending_form: Control = null      # 结案归档表（代码动态建，挂 Main 下）
var _ending_f_down := false          # F 键边沿检测（轮询，不用事件）

# ③ _ready()：scripts/main.gd:68 的 _make_archive() 之后加一行
	_make_ending_form()

# ④ _make_archive()（scripts/main.gd:76-79）旁边照抄一份
func _make_ending_form() -> void:
	ending_form = EndingForm.new()
	ending_form.name = "EndingForm"
	add_child(ending_form)
	ending_form.exit_chosen.connect(_on_ending_chosen)
	ending_form.form_closed.connect(_on_ending_closed)

# ⑤ _process()：在 I 键那段（scripts/main.gd:131-138）之后照抄一份 F 键
	var form_now := false
	if Input.is_key_pressed(KEY_F) or Input.is_physical_key_pressed(KEY_F):
		form_now = true
	if form_now and not _ending_f_down and ending_form != null:
		ending_form.toggle(tl.current().year)
	_ending_f_down = form_now

# ⑥ early-return（scripts/main.gd:143-146）前面插一段同样的
	if ending_form != null and ending_form.is_open():
		player.walking = false
		_set_hud_hidden(true)
		return

# ⑦ 两个回调（放 _clear_hotspot() 附近，scripts/main.gd:301 旁）
func _on_ending_chosen(choice: String) -> void:
	print("[归档表] 落定出口：", choice)
	# 两段之间世界一模一样（story §10.5）—— 这里故意什么都不做

func _on_ending_closed() -> void:
	_set_hud_hidden(false)
	_clear_hotspot()
```

行为约定：开表 ⇒ 世界停（`player.walking=false` ＋ HUD 让开）；关表 ⇒ HUD 回来、热点清掉。`exit_chosen` 只打日志，不推进世界、不给奖励、不改任何状态。

## 6. 已知缺口 / 待拍板

1. **A5 超市里还没有「打开归档表」的入口。** 任务书没指定用哪件家具 / 哪个热点开表，我没有自己发明一个 hotspot（那会动 `data/frames.json`，在禁改清单里）。需要总策划定：是复用超市里已有的某条 clue 热点，还是在 §10 结局前自动弹出。
2. **HUD 上的「归档员 陈阿福」常驻行不在本线。** `scripts/*.gd` 里目前没有「归档员」字样（`hud.gd` 在禁改清单里）。本线只保证归档表抬头按帧写对归档员。
3. **界面单独不可达**：没有接线，F 键在游戏里打不开表。本线的 E11–E13 是把 `EndingForm` 直接 `add_child` 到 `SceneTree.root` 上测的（等价于主场景的兄弟层）。
4. **表是模态的**（Esc/F 才关，点面板外不关），刻意没做「点外面就关浮层」——填表途中误点外面会丢掉刚填的格。
5. **记述区不能鼠标拖动**，只能 ↑↓ 在记述区焦点上滚；滚轮可滚。
6. **沙箱实测：`user://` 写不进去**（启动日志 `Failed to open 'user://logs/…'`），所以 `save()` 落到 `res://.ending_form.json` 兜底，`EndingStore.SAVE_PATH` 仍是 `user://ending_form.json` 且是回退链第一站。真实玩家机器上不会走兜底。E9 因此断言「落到回退链某一站」并打印实际那一站，而不是硬断言 `user://`。
7. 变体文本的换行位置按 story.md 的段落走（空行也是一个元素），如果后面要做打字机效果，需要另加「逐字」层。

## 7. 没做的事（按用户本轮指令「只做新文件」）

- 没碰禁改清单里的任何文件（`git status --porcelain` 对着清单逐个查过，零命中）。
- 没提交 `lab/` 与 `_mdtest` 的临时产物；`git add` 只加本线四个文件 ＋ 本文档，**没有 `git add -A`**。
- 第 ② 段 commit（接线）没做：L17 未交付。