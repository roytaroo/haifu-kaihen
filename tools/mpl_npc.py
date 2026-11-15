# DJ トシオ(司会の村人)と幽霊船のモデルを作る
#   python3 tools/mpl_npc.py → mpl_rp / mpl_bp の mmgplus:dj と mmgplus:ghostship、見本 mpl/preview_dj.png・preview_ghostship.png
#   DJ のプロパティ mmgplus:mood  0 = ノリノリで待つ / 1 = しゃべる(身ぶり手ぶり)/ 2 = おどろく(目を見開いて、サングラスが上へはねる)
import os, sys, json, math, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import models as M
ROOT = M.ROOT
M.BP = os.path.join(ROOT, 'mpl', 'src', 'behavior_packs', 'mpl_bp')
M.RP = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp')
M.PREVIEW = os.path.join(ROOT, 'mpl', 'npc_preview')
C = M.C
SKIN, SKIN2 = (196, 142, 108), (170, 118, 88)
JACKET, JACKET2, GOLD, BLACK = (92, 46, 150), (66, 30, 112), (250, 200, 60), (24, 22, 30)
HAIR = (52, 36, 30)
dj = [
    # すそ長の上着(村人の形)・帯・金のチャック
    C([-4, 0, -3], [8, 12, 6], JACKET2, bone='body'), C([-4, 12, -3], [8, 12, 6], JACKET, bone='body'),
    C([-4.2, 11, -3.2], [8.4, 1.4, 6.4], BLACK, bone='body'), C([-0.4, 1, -3.3], [0.8, 22, 0.4], GOLD, flat=True, bone='body'),
    *[C([-3.6 + i * 1.2, 21.6 - abs(i - 3) * 0.6, -3.4], [1, 0.8, 0.4], GOLD, flat=True, bone='body') for i in range(7)],  # 金のネックレス
    # ヘッドホン(首にかける)
    C([-4.6, 22.6, -3.6], [9.2, 1.4, 7.2], BLACK, bone='body'), C([-5.4, 21.2, -1.6], [1.6, 3.4, 3.2], (40, 220, 220), bone='body'), C([3.8, 21.2, -1.6], [1.6, 3.4, 3.2], (40, 220, 220), bone='body'),
    # 頭(村人の大きな頭)・鼻・髪・耳
    C([-4, 24, -4], [8, 10, 8], SKIN, bone='head'), C([-1, 25, -6], [2, 4, 2], SKIN2, bone='head'),
    C([-4.3, 32, -4.3], [8.6, 2.6, 8.6], HAIR, bone='head'), C([-4.3, 27, 1.5], [8.6, 5, 2.8], HAIR, bone='head'),
    C([-4.8, 28.5, -1], [0.8, 2, 2], SKIN2, bone='head'), C([4, 28.5, -1], [0.8, 2, 2], SKIN2, bone='head'),
    # まゆ・口ひげ
    C([-3.4, 30.2, -4.15], [2.6, 0.6, 0.3], HAIR, flat=True, bone='head'), C([0.8, 30.2, -4.15], [2.6, 0.6, 0.3], HAIR, flat=True, bone='head'),
    C([-2.4, 24.6, -4.15], [4.8, 0.8, 0.3], HAIR, flat=True, bone='head'),
    # 目(白目 + 緑のひとみ)
    C([-3.2, 27.6, -4.12], [2.4, 1.8, 0.2], (250, 250, 250), flat=True, bone='eyes'), C([0.8, 27.6, -4.12], [2.4, 1.8, 0.2], (250, 250, 250), flat=True, bone='eyes'),
    C([-2.2, 27.8, -4.22], [1.2, 1.4, 0.2], (40, 160, 70), flat=True, bone='eyes'), C([1.0, 27.8, -4.22], [1.2, 1.4, 0.2], (40, 160, 70), flat=True, bone='eyes'),
    # おでこのサングラス(黒いふち + ピンクのレンズ)
    C([-4.4, 31.2, -4.6], [8.8, 0.8, 0.5], BLACK, flat=True, bone='glasses'),
    C([-3.8, 31.2, -4.75], [3.4, 2.2, 0.5], BLACK, flat=True, bone='glasses'), C([0.4, 31.2, -4.75], [3.4, 2.2, 0.5], BLACK, flat=True, bone='glasses'),
    C([-3.4, 31.6, -4.95], [2.6, 1.4, 0.3], (255, 80, 170), flat=True, bone='glasses'), C([0.8, 31.6, -4.95], [2.6, 1.4, 0.3], (255, 80, 170), flat=True, bone='glasses'),
    C([-2.9, 32.4, -5.05], [0.8, 0.4, 0.2], (255, 220, 240), flat=True, bone='glasses'), C([1.3, 32.4, -5.05], [0.8, 0.4, 0.2], (255, 220, 240), flat=True, bone='glasses'),
    C([-4.6, 31.4, -4.5], [0.5, 0.6, 5], BLACK, flat=True, bone='glasses'), C([4.1, 31.4, -4.5], [0.5, 0.6, 5], BLACK, flat=True, bone='glasses'),
    # うで(上着のそで + 手)
    C([-8, 13, -2], [4, 10, 4], JACKET, bone='rightArm'), C([-8, 10, -2], [4, 3, 4], SKIN, bone='rightArm'), C([-8.1, 20, -2.1], [4.2, 1, 4.2], GOLD, flat=True, bone='rightArm'),
    C([4, 13, -2], [4, 10, 4], JACKET, bone='leftArm'), C([4, 10, -2], [4, 3, 4], SKIN, bone='leftArm'), C([3.9, 20, -2.1], [4.2, 1, 4.2], GOLD, flat=True, bone='leftArm'),
]
mood = "q.property('mmgplus:mood')"
talk, surp = f"({mood} == 1)", f"({mood} == 2)"
dj_anim = {
    'root': {'position': [0, f"math.abs(math.sin(q.life_time * 240)) * 0.6 * (1 - {surp})", 0]},
    'head': {'rotation': [f"{talk} * math.sin(q.life_time * 520) * 7 + (1 - {talk}) * (1 - {surp}) * math.sin(q.life_time * 240) * 5 - {surp} * 8", f"{talk} * math.sin(q.life_time * 170) * 14", 0]},
    'eyes': {'scale': [1, f"1 + {surp} * 0.7", 1]},
    'glasses': {'position': [0, f"{surp} * (2.6 + math.sin(q.life_time * 900) * 0.4)", f"{surp} * -0.6"]},
    'rightArm': {'rotation': [f"{talk} * (-80 + math.sin(q.life_time * 430) * 35) + {surp} * -150 + (1 - {talk}) * (1 - {surp}) * (-35 + math.sin(q.life_time * 480) * 12)", 0, f"{talk} * (15 + math.sin(q.life_time * 300) * 20) + {surp} * 25"]},
    'leftArm': {'rotation': [f"{talk} * (-60 + math.sin(q.life_time * 380 + 90) * 30) + {surp} * -150 + (1 - {talk}) * (1 - {surp}) * (-45 + math.sin(q.life_time * 480 + 180) * 6)", 0, f"{talk} * (-10 - math.sin(q.life_time * 250) * 20) - {surp} * 25"]},
}
M.model('dj', 'DJトシオ(司会の村人)', dj, bones={'root': [0, 0, 0], 'body': [0, 12, 0], 'head': [0, 24, 0], 'eyes': [0, 28.5, -4.2], 'glasses': [0, 32, -4.6], 'rightArm': [-6, 22, 0], 'leftArm': [6, 22, 0]},
        anim=dj_anim, box=(0.6, 1.9), props={'mmgplus:mood': {'type': 'int', 'range': [0, 2], 'default': 0, 'client_sync': True}})
# 幽霊船(大きなモデル。scale 3)
HULL, HULL2, SAIL, GLOW = (58, 48, 70), (40, 32, 50), (200, 230, 210), (90, 255, 160)
ship = []
for i in range(14):
    z = -26 + i * 4; t = abs(i - 6.5) / 7; hw = max(2, round(9 * (1 - t ** 3)))
    ship += [C([-hw, 0, z], [hw * 2, 8 - (2 if t > 0.75 else 0), 4], HULL if i % 2 else HULL2, flat=True)]
    ship += [C([-hw - 0.5, 8, z], [1, 2, 4], HULL2, flat=True), C([hw - 0.5, 8, z], [1, 2, 4], HULL2, flat=True)]
ship += [C([-8, 7.5, -22], [16, 0.6, 46], (80, 64, 60), flat=True)]
for mz, mh in ((-10, 40), (10, 32)):
    ship += [C([-1, 8, mz - 1], [2, mh, 2], (60, 44, 34))]
    for k in range(6):
        w = 14 - abs(k - 2.5) * 2
        if (k + mz) % 3 == 0: continue
        ship += [C([-w / 2, 14 + k * 4, mz + 1], [w, 3.6, 0.5], SAIL, flat=True)]
    ship += [C([-0.2, 8 + mh, mz + 1], [0.4, 5, 7], (20, 20, 20), flat=True), C([-0.3, 9.6 + mh, mz + 3], [0.5, 2.2, 2.2], (240, 240, 230), flat=True)]
ship += [C([x, 10, z], [1.2, 1.6, 1.2], GLOW, flat=True) for x in (-9, 8) for z in (-18, -2, 14)]
ship += [C([-0.5, 6, -32], [1, 1, 8], (60, 44, 34))]
M.model('ghostship', '幽霊船(港に来る)', ship, anim={'root': {'rotation': ["math.sin(q.life_time * 60) * 2", 0, "math.sin(q.life_time * 45) * 3"], 'position': [0, "math.sin(q.life_time * 80) * 0.6", 0]}},
        box=(1.0, 1.0), scale=3.0)
os.makedirs(M.PREVIEW, exist_ok=True)
for d in [os.path.join(M.RP, 'models', 'entity'), os.path.join(M.RP, 'animations'), os.path.join(M.RP, 'entity'), os.path.join(M.BP, 'entities')]: os.makedirs(d, exist_ok=True)
for n in ('dj', 'ghostship'): M.write(n, M.MODELS[n])
# DJ: 目とサングラスは頭といっしょに動く(頭の子にする)
p = os.path.join(M.RP, 'models', 'entity', 'dj.geo.json'); g = json.load(open(p))
for b in g['minecraft:geometry'][0]['bones']:
    if b['name'] in ('eyes', 'glasses'): b['parent'] = 'head'
    if b['name'] in ('head', 'rightArm', 'leftArm'): b['parent'] = 'body'
json.dump(g, open(p, 'w'), indent=1)
for n in ('dj', 'ghostship'): shutil.copy(os.path.join(M.PREVIEW, f'{n}.png'), os.path.join(ROOT, 'mpl', f'preview_{n}.png'))
print('ok')
