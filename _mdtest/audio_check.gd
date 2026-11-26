extends SceneTree

## 音效层自检（任务书 L18 §6 的 G1–G4 / G6 / G7）。
## 跑法：godot --headless --path . -s res://_mdtest/audio_check.gd
##
## 口径（为什么这样测）：
##   · headless 下音频驱动是 dummy ⇒ **绝不测「有没有出声」**。出声只能由人在真机上听（写进反馈的「未做」）。
##     这里只测：资源能不能 load、参数对不对、峰值有没有越界、循环接缝数值、单例接口通不通。
##   · G3/G4 直接读 AudioStreamWAV.data 的 PCM（16-bit 小端），不经过任何播放器 ⇒ 与听感无关的硬数值。
##   · 「首尾采样差」用 /32768 归一（与 tools/gen_audio.py 的 _stats() 同口径），
##     所以命令行打印的 seam 与生成器打印的 seam 应该是同一个数。
##   · G6 的「输出里没有 SCRIPT ERROR」由命令行侧人眼/脚本看；这里测 autoload 确实挂上、ready_check 的数对不对。

const FILES := {
	"amb_a1": "res://assets/audio/amb_a1.wav",
	"amb_a2": "res://assets/audio/amb_a2.wav",
	"amb_a3": "res://assets/audio/amb_a3.wav",
	"amb_a4": "res://assets/audio/amb_a4.wav",
	"amb_a5": "res://assets/audio/amb_a5.wav",
	"step_1": "res://assets/audio/step_1.wav",
	"step_2": "res://assets/audio/step_2.wav",
	"shift_fwd": "res://assets/audio/shift_fwd.wav",
	"shift_back": "res://assets/audio/shift_back.wav",
	"axis": "res://assets/audio/axis.wav",
	"collect": "res://assets/audio/collect.wav",
	"ui_toggle": "res://assets/audio/ui_toggle.wav",
	"ending": "res://assets/audio/ending.wav",
}

## 循环音（任务书 §3 表 1–5）
const LOOPED := ["amb_a1", "amb_a2", "amb_a3", "amb_a4", "amb_a5"]

## 期望采样数（时长 × 22050，四舍五入；与生成器的 _n() 同算法）
const EXPECT_FRAMES := {
	"amb_a1": 88200, "amb_a2": 88200, "amb_a3": 88200, "amb_a4": 88200, "amb_a5": 88200,
	"step_1": 1764, "step_2": 1764,
	"shift_fwd": 6615, "shift_back": 6615,
	"axis": 4410, "collect": 5513, "ui_toggle": 2205, "ending": 55125,
}

const SR := 22050
const PEAK_MAX := 0.9
const SEAM_MAX := 0.02
const EXPECT_STREAMS := 13

var fails := 0
var rows := {}


func _ok(cond: bool, label: String, detail: String = "") -> void:
	if cond:
		print("PASS %s%s" % [label, "" if detail == "" else "  [%s]" % detail])
	else:
		print("FAIL %s  [%s]" % [label, detail])
		fails += 1


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	# 等 autoload 的 _ready 跑完（它要建总线、load 资源、打 AUDIO_READY 日志）
	await process_frame
	await process_frame

	_asset_checks()   # G1 / G2 / G3 / G4
	_singleton_checks()  # G6 / G7

	print("---- 实测参数表（时长 / 帧数 / 峰值 / 首尾差）----")
	for key in FILES:
		var r: Dictionary = rows.get(key, {})
		if r.is_empty():
			print("  %-11s (未测)" % key)
			continue
		print("  %-11s %6.3fs frames=%6d peak=%.3f seam=%.4f"
			% [key, r["dur"], r["frames"], r["peak"], r["seam"]])

	print("AUDIO_CHECK_DONE fails=%d" % fails)
	if fails == 0:
		print("AUDIO_OK 13 个 WAV 可加载 / 22050Hz·16bit·单声道 / 峰值≤0.9 / 5 条循环接缝<0.02；Aud 单例 13 streams + 3 buses")
	else:
		print("AUDIO_FAIL 见上面的 FAIL 行")
	quit(1 if fails > 0 else 0)


# ---- G1 / G2 / G3 / G4 ----------------------------------------------------

func _asset_checks() -> void:
	for key in FILES:
		var path: String = FILES[key]

		# G1：文件在、load() 出来是 AudioStreamWAV
		var exists := ResourceLoader.exists(path)
		_ok(exists, "G1 %s 资源存在" % key, path)
		if not exists:
			continue
		var st := load(path) as AudioStreamWAV
		_ok(st != null, "G1 %s load() 是 AudioStreamWAV" % key, str(type_string(typeof(load(path)))))
		if st == null:
			continue

		# G2：采样率 / 位深 / 声道 / 时长
		_ok(st.mix_rate == SR, "G2 %s 采样率 %d" % [key, SR], "mix_rate=%d" % st.mix_rate)
		_ok(st.format == AudioStreamWAV.FORMAT_16_BITS, "G2 %s 16-bit PCM" % key, "format=%d" % st.format)
		_ok(not st.stereo, "G2 %s 单声道" % key, "stereo=%s" % str(st.stereo))

		var samples := _pcm_info(st)
		var frames := int(samples["frames"])
		_ok(frames > 0, "G2 %s 时长 > 0" % key, "frames=%d" % frames)
		_ok(frames == int(EXPECT_FRAMES[key]), "G2 %s 帧数符合 §3 时长" % key,
			"frames=%d 期望=%d" % [frames, int(EXPECT_FRAMES[key])])
		if frames <= 0:
			continue

		# G3：峰值 ≤ 0.9（逐样点取绝对值最大）
		var peak := float(samples["peak"])
		_ok(peak <= PEAK_MAX, "G3 %s 峰值 ≤ %.1f（不削波）" % [key, PEAK_MAX], "peak=%.3f" % peak)

		# G4：循环音首尾采样差 < 0.02
		var first := float(samples["first"])
		var last := float(samples["last"])
		var seam := absf(first - last)
		if key in LOOPED:
			_ok(seam < SEAM_MAX, "G4 %s 首尾采样差 < %.2f（接缝不爆音）" % [key, SEAM_MAX],
				"seam=%.5f" % seam)
			# 设计口径：循环音必须被 Aud 打上 LOOP_FORWARD（否则播一遍就停）
			_ok(st.loop_mode == AudioStreamWAV.LOOP_FORWARD, "G4 %s 已设为循环播放" % key,
				"loop_mode=%d loop_end=%d" % [st.loop_mode, st.loop_end])

		rows[key] = {
			"frames": frames,
			"dur": float(frames) / float(SR),
			"peak": peak,
			"seam": seam,
		}


## 一趟扫完 PCM：帧数 / 峰值 / 首尾采样。
## 注：Godot 4 的 PackedByteArray 没有 to_int16_array()（只有 32/64 位与浮点），
##     所以只能 decode_s16 逐样点读；13 个文件合计约 46 万点，实测 1s 内跑完。
func _pcm_info(st: AudioStreamWAV) -> Dictionary:
	var data := st.data
	var frames := data.size() / 2
	var peak := 0.0
	for i in frames:
		var a := absf(float(data.decode_s16(i * 2)) / 32768.0)
		if a > peak:
			peak = a
	if frames <= 0:
		return {"frames": 0, "peak": 0.0, "first": 0.0, "last": 0.0}
	return {
		"frames": frames,
		"peak": peak,
		"first": float(data.decode_s16(0)) / 32768.0,
		"last": float(data.decode_s16((frames - 1) * 2)) / 32768.0,
	}


# ---- G6 / G7 --------------------------------------------------------------

func _singleton_checks() -> void:
	var aud = root.get_node_or_null("Aud")
	_ok(aud != null, "G6 autoload「Aud」已挂到 /root", "node=%s" % str(aud))
	if aud == null:
		return

	var rc: Dictionary = aud.ready_check()
	_ok(int(rc["streams"]) == EXPECT_STREAMS, "G6 ready_check().streams == %d" % EXPECT_STREAMS,
		"streams=%d" % int(rc["streams"]))

	var buses: Array = rc["buses"]
	_ok(buses.has("Master") and buses.has("Ambient") and buses.has("SFX"),
		"G6 三条总线 Master/Ambient/SFX 就位", ",".join(buses))
	_ok(buses.size() == 3, "G6 总线数量 == 3", ",".join(buses))
	_ok((rc["missing"] as Array).is_empty(), "G6 没有加载失败的 key",
		",".join(rc["missing"]))

	# G7：play() 真的把 stream 挂到了一个池播放器上（不是「调用没崩」就算过）
	aud.play("collect")
	var got_stream := false
	for c in aud.get_children():
		if c is AudioStreamPlayer and c.stream != null:
			got_stream = true
	_ok(got_stream, "G7 Aud.play(\"collect\") 把 stream 挂上了池播放器", "")

	aud.ambient("a3_1976")
	_ok(String(aud.ready_check()["ambient"]) == "a3_1976",
		"G7 Aud.ambient(\"a3_1976\") 生效", "ambient=%s" % String(aud.ready_check()["ambient"]))
	aud.ambient("a3_1976")   # 同名重复调用必须是 no-op（不重启循环、不报错）
	_ok(String(aud.ready_check()["ambient"]) == "a3_1976",
		"G7 同名重复 ambient 仍生效（no-op 不报错）", "")

	aud.stop_ambient()
	_ok(String(aud.ready_check()["ambient"]) == "", "G7 stop_ambient() 清空当前底噪", "")