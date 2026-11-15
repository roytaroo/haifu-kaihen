# 新しいミニゲームのモデル: 走るスティーブ(スティーブ数え)、騎手つき競走馬6頭(競馬)、砲弾(大砲よけ)
#   python3 tools/mpl_game_models.py → mpl_rp / mpl_bp、見本 mpl/npc_preview/*.png
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import models as M
ROOT = M.ROOT
M.BP = os.path.join(ROOT, 'mpl', 'src', 'behavior_packs', 'mpl_bp'); M.RP = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp'); M.PREVIEW = os.path.join(ROOT, 'mpl', 'npc_preview')
C = M.C
SK, HAIR, SHIRT, PANTS, SHOE = (199, 150, 112), (60, 40, 25), (0, 175, 175), (60, 60, 160), (90, 90, 90)
walk = lambda ph: f"math.sin(q.life_time * 900 + {ph}) * 45"
M.model('steve', 'スティーブ(スティーブ数え)', [
    C([-4, 24, -4], [8, 8, 8], SK, bone='head'), C([-4.2, 30, -4.2], [8.4, 2.4, 8.4], HAIR, bone='head'), C([-4.2, 27, 1], [8.4, 3, 3.2], HAIR, bone='head'),
    C([-3, 27.2, -4.15], [2, 1, 0.2], (255, 255, 255), flat=True, bone='head'), C([1, 27.2, -4.15], [2, 1, 0.2], (255, 255, 255), flat=True, bone='head'),
    C([-2, 27.2, -4.25], [1, 1, 0.2], (70, 60, 160), flat=True, bone='head'), C([2, 27.2, -4.25], [1, 1, 0.2], (70, 60, 160), flat=True, bone='head'),
    C([-1, 25.5, -4.15], [2, 1, 0.2], (120, 70, 50), flat=True, bone='head'),
    C([-4, 12, -2], [8, 12, 4], SHIRT, bone='body'),
    C([-8, 12, -2], [4, 12, 4], SHIRT, bone='rightArm'), C([-8, 12, -2], [4, 4, 4], SK, bone='rightArm'),
    C([4, 12, -2], [4, 12, 4], SHIRT, bone='leftArm'), C([4, 12, -2], [4, 4, 4], SK, bone='leftArm'),
    C([-4, 0, -2], [4, 12, 4], PANTS, bone='rightLeg'), C([-4, 0, -2], [4, 2, 4], SHOE, bone='rightLeg'),
    C([0, 0, -2], [4, 12, 4], PANTS, bone='leftLeg'), C([0, 0, -2], [4, 2, 4], SHOE, bone='leftLeg')],
    bones={'root': [0, 0, 0], 'head': [0, 24, 0], 'body': [0, 24, 0], 'rightArm': [-5, 22, 0], 'leftArm': [5, 22, 0], 'rightLeg': [-2, 12, 0], 'leftLeg': [2, 12, 0]},
    anim={'rightArm': {'rotation': [walk(180), 0, 0]}, 'leftArm': {'rotation': [walk(0), 0, 0]}, 'rightLeg': {'rotation': [walk(0), 0, 0]}, 'leftLeg': {'rotation': [walk(180), 0, 0]},
          'root': {'position': [0, "math.abs(math.sin(q.life_time * 900)) * 1", 0]}}, box=(0.6, 1.8))
# 競走馬(騎手がまたがった1体のモデル)。馬の色 × 騎手の服の色
HORSES = [((120, 72, 40), (230, 50, 50)), ((235, 230, 220), (40, 120, 230)), ((40, 32, 30), (250, 200, 40)), ((170, 110, 60), (60, 190, 80)),
          ((130, 130, 135), (170, 70, 220)), ((200, 150, 90), (255, 120, 180))]
gal = lambda ph, a=38: f"math.sin(q.life_time * 1100 + {ph}) * {a}"
for i, (coat, silk) in enumerate(HORSES):
    mane = tuple(max(0, c - 50) for c in coat)
    M.model(f'racehorse{i}', f'競走馬{i + 1}(競馬)', [
        # 馬: 胴・首・頭・たてがみ・しっぽ・足
        C([-5, 14, -10], [10, 10, 22], coat, bone='body'),
        C([-3, 20, -16], [6, 12, 7], coat, rot=[-35, 0, 0], pivot=[0, 22, -10], bone='body'),
        C([-3, 28, -24], [6, 5, 10], coat, rot=[-35, 0, 0], pivot=[0, 22, -10], bone='body'), C([-2, 28.5, -26], [4, 4, 3], mane, rot=[-35, 0, 0], pivot=[0, 22, -10], bone='body'),
        C([-1, 24, -13], [2, 12, 6], mane, rot=[-35, 0, 0], pivot=[0, 22, -10], bone='body'),
        C([-3.2, 31, -20], [1.4, 3, 1.4], coat, rot=[-35, 0, 0], pivot=[0, 22, -10], bone='body'), C([1.8, 31, -20], [1.4, 3, 1.4], coat, rot=[-35, 0, 0], pivot=[0, 22, -10], bone='body'),
        C([-3.1, 29.5, -22], [0.4, 1.2, 1.2], (20, 20, 20), flat=True, rot=[-35, 0, 0], pivot=[0, 22, -10], bone='body'), C([2.7, 29.5, -22], [0.4, 1.2, 1.2], (20, 20, 20), flat=True, rot=[-35, 0, 0], pivot=[0, 22, -10], bone='body'),
        C([-1.5, 17, 11], [3, 10, 3], mane, rot=[30, 0, 0], pivot=[0, 22, 11], bone='tail'),
        C([-4.5, 0, -8], [3, 14, 3], coat, bone='legFR'), C([1.5, 0, -8], [3, 14, 3], coat, bone='legFL'), C([-4.5, 0, 7], [3, 14, 3], coat, bone='legBR'), C([1.5, 0, 7], [3, 14, 3], coat, bone='legBL'),
        *[C([x, 0, z], [3.2, 2, 3.2], (40, 30, 25), bone=b) for x, z, b in ((-4.6, -8.1, 'legFR'), (1.4, -8.1, 'legFL'), (-4.6, 6.9, 'legBR'), (1.4, 6.9, 'legBL'))],
        # くら・ゼッケン
        C([-5.2, 23.5, -4], [10.4, 1.2, 10], (60, 40, 30), bone='body'), C([-5.4, 18, -3], [0.4, 5, 7], (250, 250, 250), flat=True, bone='body'), C([5, 18, -3], [0.4, 5, 7], (250, 250, 250), flat=True, bone='body'),
        # 騎手: またがった足・体(前かがみ)・頭・帽子・うで
        C([-6, 21, -3], [2.4, 7, 3], silk, rot=[-20, 0, 10], pivot=[-5, 25, -1], bone='rider'), C([3.6, 21, -3], [2.4, 7, 3], silk, rot=[-20, 0, -10], pivot=[5, 25, -1], bone='rider'),
        C([-3, 25, -3], [6, 9, 4], silk, rot=[-35, 0, 0], pivot=[0, 25, -1], bone='rider'), C([-3.2, 28, -3.2], [6.4, 1.2, 4.4], (255, 255, 255), flat=True, rot=[-35, 0, 0], pivot=[0, 25, -1], bone='rider'),
        C([-2.5, 31, -9], [5, 5, 5], (210, 160, 120), bone='rider'), C([-2.8, 34, -9.3], [5.6, 2.6, 5.6], silk, bone='rider'), C([-2.8, 34, -10.8], [5.6, 0.8, 2], silk, bone='rider'),
        C([-2, 32.8, -9.15], [1.2, 1, 0.3], (30, 30, 30), flat=True, bone='rider'), C([0.8, 32.8, -9.15], [1.2, 1, 0.3], (30, 30, 30), flat=True, bone='rider'),
        C([-4.5, 25, -10], [2, 2, 7], silk, bone='rider'), C([2.5, 25, -10], [2, 2, 7], silk, bone='rider'),
    ], bones={'root': [0, 0, 0], 'body': [0, 14, 0], 'tail': [0, 22, 11], 'legFR': [-3, 14, -6.5], 'legFL': [3, 14, -6.5], 'legBR': [-3, 14, 8.5], 'legBL': [3, 14, 8.5], 'rider': [0, 24, 0]},
       anim={'legFR': {'rotation': [gal(0), 0, 0]}, 'legFL': {'rotation': [gal(60), 0, 0]}, 'legBR': {'rotation': [gal(180), 0, 0]}, 'legBL': {'rotation': [gal(240), 0, 0]},
             'body': {'rotation': [gal(0, 4), 0, 0]}, 'tail': {'rotation': [gal(90, 15), 0, 0]}, 'rider': {'position': [0, "math.abs(math.sin(q.life_time * 1100)) * 1.6", 0]},
             'root': {'position': [0, "math.abs(math.sin(q.life_time * 1100)) * 1.2", 0]}}, box=(1.2, 1.8))
M.model('cannonball', '砲弾(大砲よけ)', [*M.sphere(0, 6, 0, 6, (55, 55, 62), step=1.0, light=50), *M.sphere(-2, 8.5, -2, 2, (140, 140, 150), step=1.0, light=20)],
        bones={'root': [0, 6, 0]}, anim={'root': {'rotation': ["q.life_time * 720", 0, 0]}}, box=(0.7, 0.7))
os.makedirs(M.PREVIEW, exist_ok=True)
for n in ['steve', 'cannonball'] + [f'racehorse{i}' for i in range(len(HORSES))]: M.write(n, M.MODELS[n])
for b in ['body', 'rider']:
    pass
import json
for i in range(len(HORSES)):  # 馬: 首より先・くらは胴の子、騎手も胴の子(いっしょにゆれる)
    p = os.path.join(M.RP, 'models', 'entity', f'racehorse{i}.geo.json'); g = json.load(open(p))
    for b in g['minecraft:geometry'][0]['bones']:
        if b['name'] in ('tail', 'rider'): b['parent'] = 'body'
    json.dump(g, open(p, 'w'), indent=1)
print('ok')
