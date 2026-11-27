# N1 · NPC 立绘生成卡（你在百炼里跑，6 张）

> lead 出卡 2026-11-27 · 对应 `docs/剩余工作流程表.md` 的 N1
> 目标：**6 个 NPC**，每个都只是「站在那里的人影」，不需要动作、不需要表情包。
> 赛后要换皮随时能换，所以这一版**只要不怪**就行。

---

## §1 出图规格（照填，别改）

| 项 | 值 |
|---|---|
| 尺寸 | **768 × 1024**（竖构图，全身） |
| 背景 | **纯白 `#FFFFFF`**（后面按阈值抠透明，白底最稳） |
| 姿态 | 站立，**侧身 3/4 朝左**（游戏里朝右朝左靠翻转） |
| 内容 | 全身，从头到脚，**不留边、不裁脚** |
| 禁止 | 不要文字、不要边框、不要地面阴影、不要多个人、不要半身 |
| 模型 | `wan2.2-t2i-flash`（快）或 `qwen-image`（好看但慢）。**6 张必须用同一个模型** |
| 一致性 | 6 张**必须共用 §2 那段前缀**，只换 §3 的人设句 |

---

## §2 统一风格前缀（每张都粘这段在最前面）

```
pixel art, 16-bit era, chinese rural village, muted earthy palette with muted blue and grey,
limited color palette, hard pixel edges, no anti-aliasing, no dithering gradients,
full body standing character, three-quarter side view facing left,
simple flat colors, clear silhouette, no outlines glow, no text, no border, no ground shadow,
solid pure white background, centered, full figure head to toe
```

---

## §3 六张的人设句（接在 §2 后面）

### W1 · 农妇甲（1926 / 1951 / 1976）

```
an elderly chinese peasant woman in her fifties, dark blue cotton jacket with faded patches,
grey cloth headscarf tied at the back, wide cloth trousers, cloth shoes,
hands clasped in front of her waist, slightly hunched back, weathered calm face, thin lips
```

### W2 · 农妇乙（1926 / 1951 / 1976）

```
a middle-aged chinese peasant woman in her forties, indigo blue jacket, sleeves rolled up,
hair in a low bun with a wooden hairpin, apron tied at the waist, cloth shoes,
one hand resting on her hip, upright posture, sun-darkened face, plain expression
```

### M1 · 男声甲（1926 / 1951 / 1976）

```
an elderly chinese farmer in his sixties, dark grey padded cotton jacket, cloth belt at waist,
short cropped grey hair, deep wrinkles, holding a bamboo pipe in one hand,
slightly bowed shoulders, worn cloth shoes, calm tired face
```

### M2 · 男声乙（1926 / 1951 / 1976）

```
a middle-aged chinese farmer in his forties, faded blue work jacket, cotton trousers rolled to ankle,
straw hat pushed back on his head, bare forearms, straw sandals,
standing straight with arms at sides, sunburnt square face, blunt expression
```

### W3 · 2026 老太太

```
an elderly chinese woman in her seventies in 2026, plain modern dark grey cardigan over a cotton shirt,
short permed grey hair, reading glasses on a cord around her neck, dark trousers, soft walking shoes,
both hands on a simple wooden walking stick, upright but frail posture, gentle lined face
```

### M3 · 2026 年轻居民

```
a young chinese man in his late twenties in 2026, dark navy casual jacket over a light t-shirt,
straight-leg dark jeans, white sneakers, short modern haircut, thin black-framed glasses,
phone in one hand at his side, relaxed stance, neutral calm face
```

---

## §4 交付与命名

跑完 6 张，**原图（768×1024）直接丢进**：

```
assets/audio_raw/       ← 别放这里，这是音频
assets/npc_raw/         ← 放这里（新建目录，原图，不入库）
```

文件名：

```
w1_farmer_wife_a.png
w2_farmer_wife_b.png
m1_farmer_old.png
m2_farmer_mid.png
w3_old_lady_2026.png
m3_young_man_2026.png
```

> 原图**不入库**（避免又一批大图进 git）。我拿到后做后处理，只提交 32×64 的成品。

---

## §5 后处理（lead 做，你不用管）

1. 纯白阈值抠背景 → alpha
2. 裁到人物 bbox，等比缩到高 **64px**（2 格）
3. 限色到 **16 色**，硬边（最近邻）
4. 输出 `assets/npc/<同名>.png` **32×64** + `.import`
5. 五帧里各摆 2 个：a1/a2/a3 用 W1+W2 或 M1+M2（按场景），a4/a5 用 W3+M3

---

## §6 验收（我验）

- [ ] 6 张全在，同一模型出图，风格看得出是一套
- [ ] 白底干净，抠完边缘没有白边毛刺
- [ ] 缩到 32×64 之后**还能看出是人**（这条最容易翻车，翻车就重跑提示词）
- [ ] 六个人**身高比例相近**（不能 4 个人 1 米 7、2 个人 1 米 5）
- [ ] 没有文字/边框/第二个人

**如果 32×64 缩完糊成一团**：先用 128×256 试一版看看能不能接受（人物会占 4 格高，和主角 2 格不一致），不接受就回到 32×64 并从「减少衣服褶皱描述」重跑 —— 像素越小，越要少细节。