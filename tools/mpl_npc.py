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
# 見た目はだいきのスキン(mpl/assets/dj_skin.png、64x64 の Steve 型)。下の M.model の箱は仮で、geo と絵はあとでスキン用に差しかえる
dj = [C([-4, 0, -2], [8, 32, 4], (0, 0, 0))]
# 動き(128bpm に合わせる。1拍 = 768度/秒)。気分の切りかえは pre_animation で少しずつ変える(パッと変わらない)
B = "q.life_time * 768"
tk, sp, idl = "v.tk", "v.sp", "(1 - v.tk - v.sp)"
dj_anim = {
    'root': {'position': [0, f"{idl} * math.abs(math.sin(q.life_time * 384)) * 0.5 + {sp} * math.abs(math.sin(q.life_time * 500)) * 1.5", 0]},
    'body': {'rotation': [f"{idl} * 4 + {tk} * math.sin(q.life_time * 200) * 2", f"{tk} * math.sin(q.life_time * 150) * 6", 0]},
    'head': {'rotation': [f"{idl} * (math.sin({B}) * 7 + 3) + {tk} * math.sin(q.life_time * 400) * 4 - {sp} * 12", f"{tk} * math.sin(q.life_time * 130) * 10 + {idl} * math.sin(q.life_time * 96) * 8", 0]},
    # まつとき: 両手をデッキに(右はスクラッチ、左はつまみ) / しゃべる: 右手で客をさす・左手は軽く / おどろく: 両手を上へ
    'rightArm': {'rotation': [f"{idl} * (-68 + math.sin({B}) * 4) + {tk} * (-75 + math.sin(q.life_time * 300) * 12) + {sp} * -165", f"{idl} * math.sin({B} * 2) * 10", f"{tk} * 8 + {sp} * 18"]},
    'leftArm': {'rotation': [f"{idl} * (-62 + math.sin({B} + 180) * 3) + {tk} * (-25 + math.sin(q.life_time * 260 + 90) * 10) + {sp} * -165", 0, f"{tk} * -10 - {sp} * 18"]},
}
M.model('dj', 'DJトシオ(司会)', dj, bones={'root': [0, 0, 0], 'rightLeg': [-2, 12, 0], 'leftLeg': [2, 12, 0], 'body': [0, 12, 0], 'head': [0, 24, 0], 'rightArm': [-6, 22, 0], 'leftArm': [6, 22, 0]},
        anim=dj_anim, box=(0.6, 1.9), props={'mmgplus:mood': {'type': 'int', 'range': [0, 2], 'default': 0, 'client_sync': True}})
# 鏡のガイコツ(鏡のマス): 骨・ろっ骨・あご・紫に光る目・ぼろぼろのスカーフ。動きはガクガク(1秒に7回、急に向きが変わる)
#   mmgplus:act 0 = ガクガク待つ / 1 = 手をのばして奪う / 2 = 笑う(あごをカタカタ、頭をそらす)
BONE, BONE2, DARK, EYE, CLOTH = (234, 230, 214), (204, 198, 180), (28, 20, 38), (200, 100, 255), (92, 40, 132)
skel = [
    C([-3, 1, -1], [2, 11, 2], BONE, bone='rightLeg'), C([-3.5, 0, -2.5], [3, 1, 4], BONE2, bone='rightLeg'), C([-3.5, 6, -1.5], [3, 1.5, 3], BONE2, bone='rightLeg'),
    C([1, 1, -1], [2, 11, 2], BONE, bone='leftLeg'), C([0.5, 0, -2.5], [3, 1, 4], BONE2, bone='leftLeg'), C([0.5, 6, -1.5], [3, 1.5, 3], BONE2, bone='leftLeg'),
    C([-4, 11, -1.5], [8, 2, 3], BONE, bone='body'), C([-1, 13, 0], [2, 11, 2], BONE2, bone='body'),
    *[C([-4, 15 + i * 2, -2], [8, 1, 4], BONE, bone='body') for i in range(4)],
    C([-5, 23, -1], [10, 1, 2], BONE, bone='body'),
    C([-4.5, 21, -2.5], [9, 2, 5], CLOTH, bone='body'), C([-3.5, 14, 2.5], [2, 7, 0.5], CLOTH, flat=True, bone='body'), C([1, 16, 2.5], [2, 5, 0.5], CLOTH, flat=True, bone='body'),
    C([-7, 11, -1], [2, 12, 2], BONE, bone='rightArm'), C([-7.5, 8, -1.5], [3, 3, 3], BONE2, bone='rightArm'), C([-7.5, 7, -1.5], [0.5, 1, 0.5], DARK, flat=True, bone='rightArm'), C([-5, 7, -1.5], [0.5, 1, 0.5], DARK, flat=True, bone='rightArm'),
    C([5, 11, -1], [2, 12, 2], BONE, bone='leftArm'), C([4.5, 8, -1.5], [3, 3, 3], BONE2, bone='leftArm'), C([4.5, 7, -1.5], [0.5, 1, 0.5], DARK, flat=True, bone='leftArm'), C([7, 7, -1.5], [0.5, 1, 0.5], DARK, flat=True, bone='leftArm'),
    C([-4, 25, -4], [8, 7, 8], BONE, bone='head'),
    C([-3.25, 27.5, -4.5], [2.5, 2.5, 0.5], DARK, flat=True, bone='head'), C([0.75, 27.5, -4.5], [2.5, 2.5, 0.5], DARK, flat=True, bone='head'),
    C([-2.5, 28.25, -4.8], [1, 1, 0.5], EYE, flat=True, bone='head'), C([1.5, 28.25, -4.8], [1, 1, 0.5], EYE, flat=True, bone='head'),
    C([-0.5, 26, -4.5], [1, 1.25, 0.5], DARK, flat=True, bone='head'),
    *[C([-3 + i * 1.25, 25, -4.5], [1, 0.75, 0.5], (250, 248, 238), flat=True, bone='head') for i in range(5)],
    C([-3.5, 22.5, -4], [7, 2.5, 6], BONE2, bone='jaw'),
    *[C([-3 + i * 1.25, 24.5, -4.3], [1, 0.75, 0.5], (250, 248, 238), flat=True, bone='jaw') for i in range(5)],
]
st = "math.floor(q.life_time * 7)"
tw = lambda k, amp: f"math.sin({st} * {k}) * {amp}"
act = "q.property('mmgplus:act')"
I0, I1, I2 = f"({act} == 0)", f"({act} == 1)", f"({act} == 2)"
skel_anim = {
    'root': {'position': [0, f"math.abs(math.sin({st} * 53)) * 0.8 + {I2} * math.abs(math.sin(q.life_time * 900)) * 0.6", 0]},
    'body': {'rotation': [f"{tw(37, 8)} + {I1} * 15", tw(71, 14), tw(13, 9)]},
    'head': {'rotation': [f"{tw(19, 18)} - {I2} * 28", tw(83, 32), tw(47, 24)]},
    'jaw': {'rotation': [f"math.mod(math.floor(q.life_time * (10 + {I2} * 8)), 2) * (10 + {I2} * 22)", 0, 0]},
    'rightArm': {'rotation': [f"{I0} * (-25 + {tw(29, 40)}) + {I1} * (-95 + {tw(31, 8)}) + {I2} * (-35 + {tw(17, 10)})", tw(59, 15), f"{I0} * (12 + {tw(61, 18)}) + {I2} * 30"]},
    'leftArm': {'rotation': [f"{I0} * (-25 + {tw(43, 40)}) + {I1} * (-95 + {tw(23, 8)}) + {I2} * (-35 + {tw(41, 10)})", tw(67, 15), f"{I0} * (-12 - {tw(7, 18)}) - {I2} * 30"]},
    'rightLeg': {'rotation': [tw(11, 14), 0, tw(89, 6)]},
    'leftLeg': {'rotation': [tw(97, 14), 0, tw(3, 6)]},
}
M.model('mirrorskel', '鏡のガイコツ(鏡のマス)', skel, bones={'root': [0, 0, 0], 'rightLeg': [-2, 12, 0], 'leftLeg': [2, 12, 0], 'body': [0, 12, 0], 'head': [0, 24, 0], 'jaw': [0, 24, 2], 'rightArm': [-6, 23, 0], 'leftArm': [6, 23, 0]},
        anim=skel_anim, box=(0.6, 1.9), props={'mmgplus:act': {'type': 'int', 'range': [0, 2], 'default': 0, 'client_sync': True}})
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
for n in ('dj', 'ghostship', 'mirrorskel'): M.write(n, M.MODELS[n])
# DJ: プレイヤーと同じ体(2層め: 帽子・上着・そで・ズボンつき)にスキンをはる
def bone(name, parent, pivot, cubes):
    d = {'name': name, 'pivot': pivot, 'cubes': [{'origin': o, 'size': sz, 'uv': uv, **({'inflate': inf} if inf else {})} for o, sz, uv, inf in cubes]}
    if parent: d['parent'] = parent
    return d
bones = [
    bone('root', None, [0, 0, 0], []),
    bone('body', 'root', [0, 12, 0], [([-4, 12, -2], [8, 12, 4], [16, 16], 0), ([-4, 12, -2], [8, 12, 4], [16, 32], 0.25)]),
    bone('head', 'body', [0, 24, 0], [([-4, 24, -4], [8, 8, 8], [0, 0], 0), ([-4, 24, -4], [8, 8, 8], [32, 0], 0.5)]),
    bone('rightArm', 'body', [-5, 22, 0], [([-8, 12, -2], [4, 12, 4], [40, 16], 0), ([-8, 12, -2], [4, 12, 4], [40, 32], 0.25)]),
    bone('leftArm', 'body', [5, 22, 0], [([4, 12, -2], [4, 12, 4], [32, 48], 0), ([4, 12, -2], [4, 12, 4], [48, 48], 0.25)]),
    bone('rightLeg', 'root', [-1.9, 12, 0], [([-3.9, 0, -2], [4, 12, 4], [0, 16], 0), ([-3.9, 0, -2], [4, 12, 4], [0, 32], 0.25)]),
    bone('leftLeg', 'root', [1.9, 12, 0], [([-0.1, 0, -2], [4, 12, 4], [16, 48], 0), ([-0.1, 0, -2], [4, 12, 4], [0, 48], 0.25)]),
]
geo = {'format_version': '1.12.0', 'minecraft:geometry': [{'description': {'identifier': 'geometry.mmgplus.dj', 'texture_width': 64, 'texture_height': 64,
       'visible_bounds_width': 3, 'visible_bounds_height': 3, 'visible_bounds_offset': [0, 1.5, 0]}, 'bones': bones}]}
json.dump(geo, open(os.path.join(M.RP, 'models', 'entity', 'dj.geo.json'), 'w'), indent=1)
shutil.copy(os.path.join(ROOT, 'mpl', 'assets', 'dj_skin.png'), os.path.join(M.RP, 'textures', 'entity', 'mmgplus_dj.png'))
# 気分をなめらかに変える
p = os.path.join(M.RP, 'entity', 'dj.entity.json'); e = json.load(open(p))
e['minecraft:client_entity']['description']['scripts']['pre_animation'] = [
    "v.tk = math.lerp(v.tk ?? 0, q.property('mmgplus:mood') == 1, 0.12);", "v.sp = math.lerp(v.sp ?? 0, q.property('mmgplus:mood') == 2, 0.18);"]
json.dump(e, open(p, 'w'), indent=1)
shutil.copy(os.path.join(M.PREVIEW, 'ghostship.png'), os.path.join(ROOT, 'mpl', 'preview_ghostship.png'))
# ガイコツの骨の親子
p = os.path.join(M.RP, 'models', 'entity', 'mirrorskel.geo.json'); g = json.load(open(p))
for b in g['minecraft:geometry'][0]['bones']:
    b['parent'] = {'head': 'body', 'jaw': 'head', 'rightArm': 'body', 'leftArm': 'body', 'body': 'root', 'rightLeg': 'root', 'leftLeg': 'root'}.get(b['name'], b.get('parent'))
    if b['parent'] is None: b.pop('parent')
json.dump(g, open(p, 'w'), indent=1)
shutil.copy(os.path.join(M.PREVIEW, 'mirrorskel.png'), os.path.join(ROOT, 'mpl', 'preview_mirrorskel.png'))
print('ok')
