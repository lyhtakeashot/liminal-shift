extends Node

## 音频单例（autoload 名 = **Aud**，不是 Audio —— 避开 AudioServer/AudioStream 的自动补全撞名）。
##
## 设计口径（任务书 L18 §4）：
##   · 13 个 WAV 一次性 load 进内存（合计约 1.0MB，Web 导出反而更快；不流式、不读 user://）。
##   · 总线在 _ready() 里**运行时建**（AudioServer.add_bus），不碰 default_bus_layout.tres。
##   · SFX 用 8 个 AudioStreamPlayer 循环复用，同名可重叠（不打断上一条）。
##   · 循环环境音在加载时打上 LOOP_FORWARD；接缝由 tools/gen_audio.py 的 50ms 交叉淡化保证，
##     这里只负责「循环起来」，不做任何实时淡入淡出。
##   · 路径写错不静默：ready_check()["missing"] 会把加载失败的 key 报出来，_ready 时打一行日志。
##
## 本文件**不接线**（任务书 §2.3 / §9）：主循环里还没有任何一个 Aud.play(...)，那是 L18b。

const BUS_MASTER := "Master"
const BUS_AMBIENT := "Ambient"
const BUS_SFX := "SFX"

## SFX 表（任务书 §3 表 6–13）。key 就是游戏里调用时写的名字。
const SFX_PATHS := {
	"step_1": "res://assets/audio/step_1.wav",
	"step_2": "res://assets/audio/step_2.wav",
	"shift_fwd": "res://assets/audio/shift_fwd.wav",
	"shift_back": "res://assets/audio/shift_back.wav",
	"axis": "res://assets/audio/axis.wav",
	"collect": "res://assets/audio/collect.wav",
	"ui_toggle": "res://assets/audio/ui_toggle.wav",
	"ending": "res://assets/audio/ending.wav",
}

## 环境底噪表（任务书 §3 表 1–5）。key 是**帧 id**（timeline.gd 用的那套）。
const AMBIENT_PATHS := {
	"a1_1926": "res://assets/audio/amb_a1.wav",
	"a2_1951": "res://assets/audio/amb_a2.wav",
	"a3_1976": "res://assets/audio/amb_a3.wav",
	"a4_2001": "res://assets/audio/amb_a4.wav",
	"a5_2026": "res://assets/audio/amb_a5.wav",
}

const POOL_SIZE := 8
const AMBIENT_DB := -6.0    # 底噪压在 SFX 之下（赛前不做音量设置，先给个能听的静态值）
const SFX_DB := -2.0

var _sfx: Dictionary = {}            # name -> AudioStreamWAV
var _amb: Dictionary = {}            # frame_id -> AudioStreamWAV
var _missing: Array = []             # 加载失败的 key（ready_check 里报出来）
var _pool: Array = []                # 8 个复用的 AudioStreamPlayer
var _pool_i := 0
var _amb_player: AudioStreamPlayer = null
var _current_ambient := ""


func _ready() -> void:
	_ensure_buses()
	_sfx = _load_table(SFX_PATHS, false)
	_amb = _load_table(AMBIENT_PATHS, true)

	_amb_player = AudioStreamPlayer.new()
	_amb_player.name = "AmbientPlayer"
	_amb_player.bus = BUS_AMBIENT
	add_child(_amb_player)

	for i in POOL_SIZE:
		var p := AudioStreamPlayer.new()
		p.name = "Sfx%d" % i
		p.bus = BUS_SFX
		add_child(p)
		_pool.append(p)

	set_volume_db(BUS_AMBIENT, AMBIENT_DB)
	set_volume_db(BUS_SFX, SFX_DB)

	var rc := ready_check()
	print("AUDIO_READY streams=%d buses=%s ambient=%s missing=%s"
		% [rc["streams"], ",".join(rc["buses"]), rc["ambient"], ",".join(rc["missing"])])


# ---- 对外接口（任务书 §4，签名照抄，不自创） --------------------------------

## 播一条 SFX。同名可重叠，不打断上一条。
func play(sfx: String) -> void:
	if not _sfx.has(sfx):
		push_warning("Aud.play: 未登记的 SFX「%s」（见 SFX_PATHS）" % sfx)
		return
	if _pool.is_empty():
		return
	var p: AudioStreamPlayer = _pool[_pool_i]
	_pool_i = (_pool_i + 1) % _pool.size()
	p.stream = _sfx[sfx]
	p.play()


## 切环境底噪（"a1_1926" … "a5_2026"）。同名重复调用是 no-op（不重启循环）。
func ambient(frame_id: String) -> void:
	if frame_id == _current_ambient:
		return
	if not _amb.has(frame_id):
		push_warning("Aud.ambient: 未登记的帧「%s」（见 AMBIENT_PATHS）" % frame_id)
		return
	_current_ambient = frame_id
	_amb_player.stream = _amb[frame_id]
	_amb_player.play()


func stop_ambient() -> void:
	_current_ambient = ""
	if _amb_player != null:
		_amb_player.stop()
		_amb_player.stream = null


func set_volume_db(bus: String, db: float) -> void:
	var idx := AudioServer.get_bus_index(bus)
	if idx == -1:
		push_warning("Aud.set_volume_db: 没有总线「%s」" % bus)
		return
	AudioServer.set_bus_volume_db(idx, db)


## 给断言/调试用：streams 应该是 13，buses 应该是 [Master, Ambient, SFX]。
func ready_check() -> Dictionary:
	var buses: Array = []
	for i in AudioServer.get_bus_count():
		buses.append(AudioServer.get_bus_name(i))
	return {
		"streams": _sfx.size() + _amb.size(),
		"buses": buses,
		"ambient": _current_ambient,
		"missing": _missing.duplicate(),
	}


# ---- 内部 ------------------------------------------------------------------

func _ensure_buses() -> void:
	_bus_or_add(BUS_MASTER)    # Master 一定在，这里只是兜住「被别的东西清空」的情况
	_bus_or_add(BUS_AMBIENT)
	_bus_or_add(BUS_SFX)


func _bus_or_add(bus_name: String) -> int:
	var idx := AudioServer.get_bus_index(bus_name)
	if idx != -1:
		return idx
	AudioServer.add_bus()
	idx = AudioServer.get_bus_count() - 1
	AudioServer.set_bus_name(idx, bus_name)
	AudioServer.set_bus_send(idx, BUS_MASTER)
	return idx


func _load_table(paths: Dictionary, looped: bool) -> Dictionary:
	var out := {}
	for key in paths:
		var path: String = paths[key]
		if not ResourceLoader.exists(path):
			push_error("Aud: 音频文件缺失「%s」→ %s" % [key, path])
			_missing.append(key)
			continue
		var s = load(path)
		if s == null or not (s is AudioStreamWAV):
			push_error("Aud: 不是 AudioStreamWAV「%s」→ %s" % [key, path])
			_missing.append(key)
			continue
		if looped:
			_apply_loop(s)
		out[key] = s
	return out


## 让 AudioStreamWAV 整段循环。16-bit 单声道 ⇒ 帧数 = data.size() / 2。
func _apply_loop(s: AudioStreamWAV) -> void:
	var frames := s.data.size() / 2
	if frames <= 0:
		return
	s.loop_mode = AudioStreamWAV.LOOP_FORWARD
	s.loop_begin = 0
	s.loop_end = frames