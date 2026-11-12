# MPL のオリジナル BGM・効果音を合成する(ファミコン風: 矩形波のメロディ・三角波のベース・ノイズのドラム)
#   python3 tools/mpl_music.py → mpl/src/resource_packs/mpl_rp/sounds/mpl/*.ogg と sound_definitions.json
#   board(32秒・ループ)/ minigame(24秒・ループ)/ finale(15秒)/ fanfare_star(3秒)
import json, os, random, subprocess, tempfile, wave
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp'); OUT = os.path.join(RP, 'sounds', 'mpl'); os.makedirs(OUT, exist_ok=True)
SR = 32000
hz = lambda n: 440 * 2 ** ((n - 69) / 12)  # MIDI の番号 → 周波数
def sq(f, dur, duty=0.5, vol=0.25):
    t = np.arange(int(SR * dur)) / SR
    w = np.where((t * f) % 1 < duty, 1.0, -1.0) * vol
    env = np.minimum(1, np.minimum(t / 0.005, np.maximum(0, (dur - t)) / 0.03)) * np.exp(-t * 1.5)
    return w * env
def tri(f, dur, vol=0.3):
    t = np.arange(int(SR * dur)) / SR
    w = (2 * np.abs(2 * ((t * f) % 1) - 1) - 1) * vol
    return w * np.minimum(1, np.maximum(0, (dur - t)) / 0.02)
def noise(dur, vol, decay):
    t = np.arange(int(SR * dur)) / SR
    return np.random.uniform(-1, 1, len(t)) * vol * np.exp(-t * decay)
def kick(): t = np.arange(int(SR * 0.15)) / SR; return np.sin(2 * np.pi * (50 + 120 * np.exp(-t * 35)) * t) * np.exp(-t * 20) * 0.6
def put(buf, at, s):
    i = int(at * SR); j = min(len(buf), i + len(s)); buf[i:j] += s[: j - i]

CHORDS = {'C': [60, 64, 67], 'Am': [57, 60, 64], 'F': [53, 57, 60], 'G': [55, 59, 62], 'Dm': [50, 53, 57], 'Em': [52, 55, 59], 'E': [52, 56, 59]}
def song(seconds, bpm, prog, seed, lead_duty=0.5, drums=True, key_scale=(0, 2, 4, 5, 7, 9, 11)):
    # 協和する作り方:
    #   強い拍(1・3拍目の頭)= 今の和音の音だけ / 弱い拍 = 音階の中で前の音のとなり(なめらかに)
    #   メロディは 72〜86 の間で、大きく跳ばない。伴奏の和音は 1オクターブ下で小さく
    rnd = random.Random(seed)
    beat = 60 / bpm; bars = int(round(seconds / (beat * 4)))
    buf = np.zeros(int(SR * bars * beat * 4) + SR)
    scale = sorted(n for o in range(4, 8) for d in key_scale for n in [12 * o + d] if 60 <= n <= 90)
    rhythm_bank = [[1, 0, 1, 1, 1, 0, 1, 0], [1, 1, 1, 0, 1, 1, 1, 0], [1, 0, 1, 0, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0, 0, 0]]
    rhythms = [rnd.choice(rhythm_bank) for _ in range(4)]
    form = [0, 1, 0, 2, 0, 1, 3, 3]
    cur = 76
    for b in range(bars):
        ch = CHORDS[prog[b % len(prog)]]
        tones = sorted({n for n in range(60, 91) if (n - ch[0]) % 12 in [(x - ch[0]) % 12 for x in ch]} & set(range(72, 87)))
        t0 = b * 4 * beat
        # ベース: ルートと5度
        for k in range(8):
            put(buf, t0 + k * beat / 2, tri(hz(ch[0] - 24 + (7 if k % 4 == 2 else 0)), beat / 2 * 0.85, 0.28))
        # 伴奏: 和音のアルペジオ(メロディより下)
        for k in range(8):
            put(buf, t0 + k * beat / 2, sq(hz(ch[k % 3]), beat / 2 * 0.7, 0.25, 0.05))
        # メロディ
        rh = rhythms[form[b % len(form)]]
        for k in range(8):
            if not rh[k]: continue
            strong = k in (0, 4)
            if strong or b % len(form) == len(form) - 1 and k >= 4:
                cur = min(tones, key=lambda n: abs(n - cur) + rnd.random() * 3)
            else:
                i = min(range(len(scale)), key=lambda j: abs(scale[j] - cur))
                i = max(0, min(len(scale) - 1, i + rnd.choice([-1, 1, 1, -1, 2, -2])))
                cur = max(72, min(86, scale[i]))
                if not strong and k % 2 == 1 and cur not in tones: pass  # 弱い拍の通る音
            nxt = next((j for j in range(k + 1, 8) if rh[j]), 8)
            put(buf, t0 + k * beat / 2, sq(hz(cur), (nxt - k) * beat / 2 * 0.85, lead_duty, 0.16))
        # 最後の小節は和音の根音で終わる
        if drums:
            for k in range(4):
                put(buf, t0 + k * beat, kick() if k % 2 == 0 else noise(0.12, 0.2, 25))
                put(buf, t0 + k * beat + beat / 2, noise(0.04, 0.06, 80))
    return buf
def fanfare(notes, step, seed=0):
    buf = np.zeros(int(SR * (len(notes) * step + 1.5)))
    for i, n in enumerate(notes):
        long = i == len(notes) - 1
        put(buf, i * step, sq(hz(n), step * (6 if long else 0.95), 0.5, 0.22))
        put(buf, i * step, sq(hz(n - 12), step * (6 if long else 0.95), 0.25, 0.1))
        put(buf, i * step, tri(hz(n - 24), step * (6 if long else 0.95)))
    return buf
def save(name, buf, seconds=None):
    if seconds: buf = buf[: int(SR * seconds)]
    buf = buf / max(1e-6, np.max(np.abs(buf))) * 0.85
    fade = int(SR * 0.05); buf[-fade:] *= np.linspace(1, 0, fade)
    with tempfile.TemporaryDirectory() as d:
        w = os.path.join(d, 'a.wav')
        with wave.open(w, 'wb') as f: f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((buf * 32767).astype(np.int16).tobytes())
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', w, '-c:a', 'libvorbis', '-q:a', '4', os.path.join(OUT, name + '.ogg')], check=True)
np.random.seed(7)
save('bgm_board', song(32, 120, ['C', 'Am', 'F', 'G'], seed=11), 32)
save('bgm_minigame', song(24, 160, ['Am', 'F', 'C', 'G', 'Am', 'F', 'G', 'G'], seed=23, lead_duty=0.25), 24)
save('bgm_finale', song(15, 108, ['F', 'G', 'Em', 'Am', 'F', 'G', 'C', 'C'], seed=5, drums=True), 15)
save('fanfare_star', fanfare([72, 76, 79, 84, 79, 84, 88], 0.12))
defs = {f'mpl.{n}': {'category': 'record', 'sounds': [{'name': f'sounds/mpl/{n}', 'stream': n.startswith('bgm'), 'volume': 1.0}]} for n in ['bgm_board', 'bgm_minigame', 'bgm_finale', 'fanfare_star']}
p = os.path.join(RP, 'sounds', 'sound_definitions.json'); d = json.load(open(p)) if os.path.exists(p) else {'format_version': '1.14.0', 'sound_definitions': {}}
d['sound_definitions'].update(defs); json.dump(d, open(p, 'w'), indent=1)
print('ok')
