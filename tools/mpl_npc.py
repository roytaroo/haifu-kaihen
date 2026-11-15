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
print('ok')
