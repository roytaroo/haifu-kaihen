# VENUS PARTY の BGM(すべて自作の合成音)
#   ボード: Fメジャー 128bpm、ジャズっぽいコード進行 + 手書きのメロディ、ピアノの裏打ち、歩くベース、軽いドラム、残響
#   ミニゲーム: Cメジャー 150bpm、元気な8分のベース、16分のアルペジオ、リード、4つ打ち
#   python3 tools/mpl_bgm.py → mpl_rp/sounds/mpl/bgm_board.ogg・bgm_minigame.ogg(長さはターミナルに出る → main.js の BGM の tick 数)
import os, subprocess, tempfile, wave
import numpy as np
SR = 32000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp', 'sounds', 'mpl')
rng = np.random.default_rng(3)
hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
NOTE = {'C': 0, 'Db': 1, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11}
def n(s):  # 'C5' → 72
    k = s[:-1]; return 12 * (int(s[-1]) + 1) + NOTE[k]
CH = {'': [0, 4, 7], 'm': [0, 3, 7], '7': [0, 4, 7, 10], 'm7': [0, 3, 7, 10], 'maj7': [0, 4, 7, 11]}
def chord(name):
    for k in ('F#', 'Bb', 'Eb', 'Ab', 'Db'):
        if name.startswith(k): r, q = k, name[len(k):]; break
    else: r, q = name[0], name[1:]
    bass = None
    if '/' in q: q, bass = q.split('/')
    return NOTE[r], CH[q], (NOTE[bass] if bass else NOTE[r])

def env(n_, a, d, s, r, sus_len):
    e = np.zeros(n_); A, D, R = int(a * SR), int(d * SR), int(r * SR); S = max(0, min(n_, int(sus_len * SR)))
    e[:min(A, n_)] = np.linspace(0, 1, min(A, n_))
    if A < n_: e[A:min(A + D, n_)] = np.linspace(1, s, min(A + D, n_) - A)
    if A + D < S: e[A + D:S] = s
    if S < n_: e[S:min(S + R, n_)] = np.linspace(e[S - 1] if S else s, 0, min(S + R, n_) - S)
    return e
def piano(f, dur, vel=0.5):
    L = dur + 1.2; t = np.arange(int(L * SR)) / SR; x = np.zeros_like(t)
    for k, amp in enumerate([1, 0.5, 0.32, 0.18, 0.1, 0.06], 1):
        x += amp * np.sin(2 * np.pi * f * k * (1 + 0.0007 * k) * t) * np.exp(-t * (2.2 + k * 1.3))
    x *= env(len(t), 0.004, 0.1, 0.8, 0.25, dur)
    return x * vel
def bass(f, dur, vel=0.55):
    t = np.arange(int((dur + 0.15) * SR)) / SR
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sign(np.sin(2 * np.pi * f * t))
    return x * env(len(t), 0.005, 0.12, 0.7, 0.08, dur) * vel
def lead(f, dur, vel=0.32, bright=1.0):
    t = np.arange(int((dur + 0.2) * SR)) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t / 0.25, 0, 1)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    x = np.sin(ph) + 0.45 * np.sin(2 * ph) * bright + 0.28 * np.sin(3 * ph) * bright + 0.15 * np.sin(5 * ph) * bright
    return x * env(len(t), 0.02, 0.08, 0.8, 0.12, dur) * vel
def bell(f, dur, vel=0.18):
    t = np.arange(int((dur + 0.8) * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 3) * vel
def kick():
    t = np.arange(int(0.35 * SR)) / SR; f = 50 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 0.9
def snare():
    t = np.arange(int(0.25 * SR)) / SR
    return (rng.standard_normal(len(t)) * 0.5 * np.exp(-t * 18) + np.sin(2 * np.pi * 190 * t) * 0.4 * np.exp(-t * 25)) * 0.55
def hat(open_=False):
    t = np.arange(int((0.18 if open_ else 0.05) * SR)) / SR
    x = rng.standard_normal(len(t)); x = np.diff(np.concatenate([[0], x]))
    return x * np.exp(-t * (14 if open_ else 70)) * 0.16
def add(buf, x, at):
    i = int(at * SR); j = min(len(buf), i + len(x))
    if i < len(buf): buf[i:j] += x[:j - i]
def reverb(x, size=1.3, mix=0.22):
    L = int(size * SR); t = np.arange(L) / SR
    ir = rng.standard_normal(L) * np.exp(-t * 4.2); ir[0] = 0
    n_ = len(x) + L; N = 1 << (n_ - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[:len(x)]
    # ループさせるので、はみ出した残響は先頭に戻す
    tail = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[len(x):n_]
    wet[:len(tail)] += tail
    wet *= np.max(np.abs(x)) / (np.max(np.abs(wet)) + 1e-9)
    return x * (1 - mix) + wet * mix

def board():
    bpm = 128; B = 60 / bpm; bars = 16; L = bars * 4 * B
    buf = np.zeros(int(L * SR) + SR)
    chords = ['F', 'Dm', 'Bb', 'C', 'F', 'Dm', 'Gm7', 'C7', 'Bb', 'Bbm', 'F/A', 'D7', 'Gm7', 'C7', 'F', 'C7']
    mel = [  # (音, 拍) 1小節4拍
        [('C5', 1), ('A4', .5), ('C5', .5), ('F5', 1), ('E5', .5), ('D5', .5)], [('C5', 1), ('A4', 1), ('F4', 1), ('A4', 1)],
        [('Bb4', .5), ('D5', .5), ('F5', 1), ('G5', .5), ('F5', .5), ('D5', 1)], [('E5', 1.5), ('D5', .5), ('C5', 2)],
        [('C5', .5), ('C5', .5), ('A4', .5), ('C5', .5), ('F5', 1), ('A5', 1)], [('G5', .5), ('F5', .5), ('E5', .5), ('D5', .5), ('A4', 2)],
        [('Bb4', .5), ('D5', .5), ('G5', 1), ('F5', .5), ('E5', .5), ('D5', 1)], [('E5', 1), ('G5', 1), ('C6', 1.5), (None, .5)],
        [('D5', .5), ('F5', .5), ('Bb5', 1), ('A5', .5), ('G5', .5), ('F5', 1)], [('Db5', .5), ('F5', .5), ('Bb5', 1), ('Ab5', 1), ('F5', 1)],
        [('C5', 1), ('F5', .5), ('G5', .5), ('A5', 1), ('F5', 1)], [('F#5', 1), ('A5', .5), ('F#5', .5), ('D5', 2)],
        [('G5', .5), ('F5', .5), ('D5', .5), ('Bb4', .5), ('G4', 1), ('Bb4', 1)], [('C5', .5), ('E5', .5), ('G5', .5), ('Bb5', .5), ('A5', 1), ('G5', 1)],
        [('F5', 1.5), ('C5', .5), ('A4', 1), ('C5', 1)], [('E5', .5), ('F5', .5), ('G5', 1), (None, 2)],
    ]
    sw = lambda beat: beat + (0.12 if (beat * 2) % 2 == 1 else 0)  # 裏の8分を少し遅らせる(スイング)
    for b in range(bars):
        r, q, bs = chord(chords[b]); t0 = b * 4 * B
        # ベース: 1・3拍は根音、2・4拍は5度・経過音(歩くベース)
        nxt = chord(chords[(b + 1) % bars])[2]
        for k, iv in enumerate([0, 7, 4, None]):
            f = 36 + (bs if k == 0 else r) + (iv if iv is not None else 0)
            if iv is None: f = 36 + nxt + (1 if (nxt - r) % 12 > 6 else -1)
            add(buf, bass(hz(f + 12 if f < 40 else f), B * 0.92), t0 + k * B)
        # ピアノ: 2・4拍の裏打ち
        for beat in (1, 2.5, 3):
            for iv in q: add(buf, piano(hz(60 + r + iv if r + iv < 8 else 48 + r + iv), B * 0.4, 0.13), t0 + sw(beat) * B)
        # メロディ(ブラス風)+ オクターブ下のピアノで厚く
        t = 0
        for note, d in mel[b]:
            if note: add(buf, lead(hz(n(note)), d * B * 0.9, 0.26, 0.8), t0 + sw(t) * B); add(buf, piano(hz(n(note) - 12), d * B * 0.8, 0.09), t0 + sw(t) * B)
            t += d
        # キラキラ(4小節ごと)
        if b % 4 == 3: [add(buf, bell(hz(84 + r + iv), 0.3), t0 + 3 * B + i * B / 4) for i, iv in enumerate(q[:3] + [12])]
        # ドラム
        for k in range(4):
            if k in (0, 2): add(buf, kick(), t0 + k * B)
            if k in (1, 3): add(buf, snare() * 0.7, t0 + k * B)
            add(buf, hat(), t0 + k * B); add(buf, hat() * 0.7, t0 + sw(k + 0.5) * B)
        if b % 4 == 3: add(buf, hat(True), t0 + 3.5 * B)
    return buf, L
def minigame():
    bpm = 150; B = 60 / bpm; bars = 16; L = bars * 4 * B
    buf = np.zeros(int(L * SR) + SR)
    chords = ['C', 'G/B', 'Am', 'F', 'C', 'G', 'F', 'G', 'Am', 'F', 'C', 'G', 'F', 'G', 'C', 'G']
    riff = [('E5', .5), ('G5', .5), ('C6', .5), ('G5', .5), ('E5', .5), ('D5', .5), ('C5', 1)]
    for b in range(bars):
        r, q, bs = chord(chords[b]); t0 = b * 4 * B
        for k in range(8): add(buf, bass(hz(36 + bs + (12 if k % 2 else 0)), B * 0.42, 0.5), t0 + k * B / 2)
        arp = [60 + r + iv for iv in q] + [72 + r + q[0]]
        for k in range(16): add(buf, bell(hz(arp[k % len(arp)] + 12), 0.12, 0.08), t0 + k * B / 4)
        for iv in q: add(buf, piano(hz(60 + r + iv), B * 0.25, 0.08), t0 + 1.5 * B); add(buf, piano(hz(60 + r + iv), B * 0.25, 0.08), t0 + 3.5 * B)
        if b % 2 == 0:
            t = 0; shift = [0, 0, -3, -7, 0, 2, -7, -5, -3, -7, 0, 2, -7, -5, 0, 2][b]
            for note, d in riff: add(buf, lead(hz(n(note) + shift), d * B * 0.85, 0.22, 1.0), t0 + t * B); t += d
        else:
            for k, iv in enumerate([q[-1], q[1], q[0], 12]): add(buf, lead(hz(72 + r + iv), B * 0.8, 0.18, 1.0), t0 + k * B)
        for k in range(4):
            add(buf, kick(), t0 + k * B)
            if k in (1, 3): add(buf, snare(), t0 + k * B)
            add(buf, hat(True) * 0.6, t0 + (k + 0.5) * B)
        if b % 4 == 3: [add(buf, snare() * (0.5 + i * 0.1), t0 + (3 + i / 4) * B) for i in range(4)]
    return buf, L
def save(name, buf, L):
    x = buf[:int(L * SR)]; x = reverb(x)
    x = np.tanh(x * 1.1); x /= np.max(np.abs(x)) + 1e-9; x *= 0.85
    fd, w = tempfile.mkstemp(suffix='.wav'); os.close(fd)
    with wave.open(w, 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((x * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', w, '-c:a', 'libvorbis', '-q:a', '4', os.path.join(OUT, name + '.ogg')], check=True)
    os.remove(w); print(name, f'{L:.2f}s', round(L * 20), 'ticks')
os.makedirs(OUT, exist_ok=True)
save('bgm_board', *board()); save('bgm_minigame', *minigame())
