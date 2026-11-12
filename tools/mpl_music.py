# MPL のオリジナル BGM・効果音を合成する(パーティゲーム風: はずむシャッフル・セブンスの和音・歩くベース・マリンバとブラス)
# どれもオリジナルの曲(既存の曲は使っていない)。
#   python3 tools/mpl_music.py → mpl/src/resource_packs/mpl_rp/sounds/mpl/*.ogg と sound_definitions.json
import json, os, random, subprocess, tempfile, wave
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp'); OUT = os.path.join(RP, 'sounds', 'mpl'); os.makedirs(OUT, exist_ok=True)
SR = 32000
hz = lambda n: 440 * 2 ** ((n - 69) / 12)
T = lambda dur: np.arange(int(SR * dur)) / SR

# ===== 楽器 =====
def marimba(f, dur, vol=0.3):  # 木をたたく音: 基音 + 4倍音、すぐ減衰
    t = T(dur + 0.4)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 18)) * np.exp(-t * 7) * vol
def brass(f, dur, vol=0.18):  # ラッパっぽい音: のこぎり波を少し丸め、立ち上がりに勢い
    t = T(dur)
    saw = sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 7))
    env = np.minimum(1, t / 0.03) * np.minimum(1, np.maximum(0, dur - t) / 0.05) * (0.85 + 0.15 * np.exp(-t * 8))
    return saw * env * vol * (1 + 0.02 * np.sin(2 * np.pi * 5.5 * t))
def bell(f, dur, vol=0.12):  # キラキラ(和音のアクセント)
    t = T(dur + 0.6)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 4) * vol
def pluck_bass(f, dur, vol=0.42):  # はじくベース
    t = T(dur)
    w = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t)
    return w * np.exp(-t * 4) * np.minimum(1, np.maximum(0, dur - t) / 0.02) * vol
def piano_chord(notes, dur, vol=0.07):
    t = T(dur)
    return sum(np.sin(2 * np.pi * hz(n) * t) + 0.3 * np.sin(2 * np.pi * hz(n) * 2 * t) for n in notes) * np.exp(-t * 3) * np.minimum(1, np.maximum(0, dur - t) / 0.03) * vol
def noise(dur, vol, decay):
    t = T(dur); return np.random.uniform(-1, 1, len(t)) * vol * np.exp(-t * decay)
def kick(): t = T(0.18); return np.sin(2 * np.pi * (45 + 110 * np.exp(-t * 30)) * t) * np.exp(-t * 16) * 0.7
def snare(): return noise(0.16, 0.28, 22) + np.sin(2 * np.pi * 190 * T(0.16)) * np.exp(-T(0.16) * 30) * 0.2
def clap(): return sum(np.roll(noise(0.12, 0.18, 30), int(SR * d)) for d in (0, 0.01, 0.02))
def put(buf, at, s):
    i = int(at * SR); j = min(len(buf), i + len(s)); 
    if i < len(buf): buf[i:j] += s[: j - i]

# セブンスの和音(MIDI)。ベースは根音
CH = {'Cmaj7': [60, 64, 67, 71], 'Am7': [57, 60, 64, 67], 'Dm7': [62, 65, 69, 72], 'G7': [55, 59, 62, 65], 'Fmaj7': [53, 57, 60, 64], 'Em7': [52, 55, 59, 62],
      'E7': [52, 56, 59, 62], 'A7': [57, 61, 64, 67], 'D7': [62, 66, 69, 72], 'C': [60, 64, 67, 72], 'F': [53, 57, 60, 65], 'G': [55, 59, 62, 67]}
MAJOR = [0, 2, 4, 5, 7, 9, 11]

def song(seconds, bpm, prog, seed, shuffle=True, lead='marimba', drums='party'):
    rnd = random.Random(seed)
    beat = 60 / bpm
    swing = (2 / 3) if shuffle else 0.5  # 8分の裏をずらす(シャッフル)
    pos8 = lambda k: (k // 2) * beat + (beat * swing if k % 2 else 0)  # 小節内の 8分 k 番目の時刻
    bars = int(round(seconds / (beat * 4)))
    buf = np.zeros(int(SR * (bars * beat * 4 + 1)))
    scale = sorted(12 * o + d for o in range(5, 8) for d in MAJOR)
    # メロディのリズムの型(1 = 鳴らす)。裏で食い込む形を多めに
    bank = [[1, 0, 0, 1, 0, 1, 1, 0], [1, 1, 0, 1, 0, 0, 1, 0], [0, 1, 1, 0, 1, 0, 1, 1], [1, 0, 1, 0, 0, 1, 0, 1], [1, 1, 1, 0, 1, 0, 0, 0]]
    motif = [rnd.choice(bank) for _ in range(3)]
    form = [0, 1, 0, 2]
    cur = 76
    for b in range(bars):
        name = prog[b % len(prog)]; ch = CH[name]
        nxt = CH[prog[(b + 1) % len(prog)]]
        t0 = b * 4 * beat
        tones = {n for n in range(60, 96) if (n - ch[0]) % 12 in {(x - ch[0]) % 12 for x in ch}}
        # 歩くベース: 根音 → 3度 → 5度 → 次の根音へ半音でつなぐ
        root = ch[0] - 24 if ch[0] >= 58 else ch[0] - 12
        walk = [root, root + (ch[1] - ch[0]), root + (ch[2] - ch[0]), (nxt[0] - 24 if nxt[0] >= 58 else nxt[0] - 12) + rnd.choice([-1, 1])]
        for k, n in enumerate(walk): put(buf, t0 + k * beat, pluck_bass(hz(n), beat * 0.95))
        # 和音: 2拍目と4拍目の裏で短く(はずむ伴奏)
        for k in (1, 3):
            put(buf, t0 + k * beat + beat * swing, piano_chord([n for n in ch], beat * 0.45))
        put(buf, t0, bell(hz(ch[-1] + 12), beat))
        # メロディ: 強い拍は和音の音、ほかは音階のとなり。最後の小節は長くのばす
        rh = motif[form[b % len(form)]] if b % 8 != 7 else [1, 0, 0, 0, 0, 0, 0, 0]
        hits = [k for k in range(8) if rh[k]]
        for idx, k in enumerate(hits):
            if k in (0, 4) or idx == 0 or b % 8 == 7:
                cand = [n for n in tones if 72 <= n <= 88]
                cur = min(cand, key=lambda n: abs(n - cur) + rnd.random() * 4)
            else:
                # この小節の音階: 和音の音と半音でぶつかる音階の音は、和音の音に置きかえる(A7 の時は C → C# など)
                local = sorted({n for n in scale if not any(abs(n - t) == 1 for t in tones)} | {n for n in tones if 60 <= n <= 96})
                i = min(range(len(local)), key=lambda j: abs(local[j] - cur))
                cur = max(72, min(88, local[max(0, min(len(local) - 1, i + rnd.choice([-1, 1, 2, -2, 1])))]))
            end = hits[idx + 1] if idx + 1 < len(hits) else 8
            dur = max(0.08, pos8(end) - pos8(k)) * 0.9
            inst = marimba if lead == 'marimba' else brass
            put(buf, t0 + pos8(k), inst(hz(cur), dur))
            if lead == 'both' or (lead == 'marimba' and b % 8 >= 4): put(buf, t0 + pos8(k), brass(hz(cur - 12), dur, 0.08))
        # ドラム: ドン・パン(クラップ)・シャッフルのハイハット
        for k in range(4):
            put(buf, t0 + k * beat, kick() if k in (0, 2) else (clap() if drums == 'party' else snare()))
            for s in (0, swing): put(buf, t0 + k * beat + s * beat, noise(0.035, 0.07 if s else 0.05, 90))
        if b % 4 == 3: put(buf, t0 + 3 * beat + beat * swing, noise(0.25, 0.12, 8))  # 4小節ごとにシンバル
    return buf

def fanfare(notes, step):
    buf = np.zeros(int(SR * (len(notes) * step + 2)))
    for i, n in enumerate(notes):
        long = i == len(notes) - 1
        d = step * (8 if long else 0.95)
        put(buf, i * step, brass(hz(n), d, 0.22)); put(buf, i * step, brass(hz(n - 5), d, 0.1)); put(buf, i * step, marimba(hz(n + 12), d, 0.12))
    put(buf, (len(notes) - 1) * step, piano_chord([60, 64, 67, 72], step * 8, 0.12)); put(buf, (len(notes) - 1) * step, noise(1.2, 0.12, 3))
    return buf

def save(name, buf, seconds=None):
    if seconds: buf = buf[: int(SR * seconds)]
    buf = np.tanh(buf / max(1e-6, np.max(np.abs(buf))) * 1.2) * 0.85  # 少しまるく
    fade = int(SR * 0.05); buf[-fade:] *= np.linspace(1, 0, fade)
    with tempfile.TemporaryDirectory() as d:
        w = os.path.join(d, 'a.wav')
        with wave.open(w, 'wb') as f: f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((buf * 32767).astype(np.int16).tobytes())
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', w, '-c:a', 'libvorbis', '-q:a', '5', os.path.join(OUT, name + '.ogg')], check=True)

np.random.seed(7)
# すごろく: のんびりはずむ(シャッフル 128)。I-vi-ii-V と IV-iii-ii-V
save('bgm_board', song(32, 128, ['Cmaj7', 'Am7', 'Dm7', 'G7', 'Cmaj7', 'Am7', 'Dm7', 'G7', 'Fmaj7', 'Em7', 'Dm7', 'G7', 'Fmaj7', 'E7', 'Dm7', 'G7'], seed=3), 32)
# ミニゲーム: 速くてにぎやか(シャッフルなし 168、ブラスも重ねる)
save('bgm_minigame', song(24, 168, ['C', 'A7', 'Dm7', 'G7', 'C', 'A7', 'D7', 'G7', 'F', 'G', 'Em7', 'A7', 'Dm7', 'G7', 'C', 'G7'], seed=19, shuffle=False, lead='both'), 24)
# 結果発表: ゆったり豪華
save('bgm_finale', song(15, 100, ['Fmaj7', 'G7', 'Em7', 'Am7', 'Dm7', 'G7', 'Cmaj7', 'Cmaj7'], seed=8, lead='brass'), 15)
save('fanfare_star', fanfare([67, 72, 76, 79, 76, 79, 84], 0.11))
defs = {f'mpl.{n}': {'category': 'record', 'sounds': [{'name': f'sounds/mpl/{n}', 'stream': n.startswith('bgm'), 'volume': 1.0, 'is3D': False}]} for n in ['bgm_board', 'bgm_minigame', 'bgm_finale', 'fanfare_star']}
p = os.path.join(RP, 'sounds', 'sound_definitions.json'); d = json.load(open(p)) if os.path.exists(p) else {'format_version': '1.14.0', 'sound_definitions': {}}
d['sound_definitions'].update(defs); json.dump(d, open(p, 'w'), indent=1)
print('ok')
