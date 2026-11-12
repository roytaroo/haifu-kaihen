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
def song(seconds, bpm, prog, seed, swing=False, lead_duty=0.5, drums=True):
    rnd = random.Random(seed)
    beat = 60 / bpm; bars = int(round(seconds / (beat * 4)))
    buf = np.zeros(int(SR * bars * beat * 4) + SR)
    # メロディの型(1小節 = 8つの8分音符。None は休み)を4つ作って使い回す(覚えやすく)
    motifs = []
    for _ in range(4):
        m = []
        for k in range(8):
            m.append(None if (k in (3, 7) and rnd.random() < 0.5) else rnd.choice([0, 1, 2, 2, 3, 4, 5]))
        motifs.append(m)
    form = [0, 1, 0, 2, 0, 1, 3, 2]
    for b in range(bars):
        ch = CHORDS[prog[b % len(prog)]]
        t0 = b * 4 * beat
        # ベース: ルート → 5度 の8分
        for k in range(8):
            n = ch[0] - 24 + (7 if k % 4 == 2 else 0)
            put(buf, t0 + k * beat / 2, tri(hz(n), beat / 2 * 0.9))
        # 和音のアルペジオ(小さく)
        for k in range(8):
            put(buf, t0 + k * beat / 2 + (beat * 0.08 if swing and k % 2 else 0), sq(hz(ch[k % 3] + 12), beat / 2 * 0.8, 0.25, 0.07))
        # メロディ: 和音の音と上の音階から
        scale = sorted(set([x + 12 for x in ch] + [ch[0] + 14, ch[0] + 17, ch[0] + 19, ch[0] + 24]))
        m = motifs[form[b % len(form)]]
        for k, deg in enumerate(m):
            if deg is None: continue
            dur = beat / 2 * (2 if k % 4 == 3 else 1) * 0.9
            put(buf, t0 + k * beat / 2 + (beat * 0.08 if swing and k % 2 else 0), sq(hz(scale[min(deg, len(scale) - 1)]), dur, lead_duty, 0.17))
        # ドラム
        if drums:
            for k in range(4):
                put(buf, t0 + k * beat, kick() if k % 2 == 0 else noise(0.12, 0.25, 25))
                put(buf, t0 + k * beat + beat / 2, noise(0.04, 0.08, 80))
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
save('bgm_board', song(32, 120, ['C', 'Am', 'F', 'G'], seed=11, swing=True), 32)
save('bgm_minigame', song(24, 160, ['Am', 'F', 'C', 'G', 'Am', 'F', 'G', 'E'], seed=23, lead_duty=0.25), 24)
save('bgm_finale', song(15, 108, ['F', 'G', 'Em', 'Am', 'F', 'G', 'C', 'C'], seed=5, drums=True), 15)
save('fanfare_star', fanfare([72, 76, 79, 84, 79, 84, 88], 0.12))
defs = {f'mpl.{n}': {'category': 'record', 'sounds': [{'name': f'sounds/mpl/{n}', 'stream': n.startswith('bgm'), 'volume': 1.0}]} for n in ['bgm_board', 'bgm_minigame', 'bgm_finale', 'fanfare_star']}
p = os.path.join(RP, 'sounds', 'sound_definitions.json'); d = json.load(open(p)) if os.path.exists(p) else {'format_version': '1.14.0', 'sound_definitions': {}}
d['sound_definitions'].update(defs); json.dump(d, open(p, 'w'), indent=1)
print('ok')
