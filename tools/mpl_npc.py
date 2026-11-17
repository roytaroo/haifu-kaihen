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
# 幽霊船(大きなモデル。scale 4。船首は -z)
#   船体: 船首がとがり船尾が広い・下ほど細い・板の段と苔の筋 / 船尾の高い船室(光る窓)/ 船首の甲板・骨の船首像・斜めの帆柱
#   マスト3本(前・中・後ろ)に横木と破れた帆、中マストに見張り台とドクロの旗、ロープ、光る丸窓とランタン
HULL, HULL2, TRIM, DECK, WOOD, SAIL, SAIL2, GLOW, MOSS, BONE = (60, 50, 74), (46, 38, 58), (96, 84, 70), (88, 72, 62), (66, 50, 40), (196, 214, 200), (170, 190, 176), (100, 255, 170), (70, 110, 70), (232, 228, 212)
ship = []
def hw_at(z):   # z(-30 船首 〜 +28 船尾)での船のはば(半分)
    if z < -14: return max(1.0, 9.5 * math.sqrt(max(0.0, (z + 31) / 17)))
    return 9.5 - max(0, z - 18) * 0.12
for z in range(-30, 28, 2):
    w = hw_at(z + 1)
    for k, y in enumerate(range(0, 10, 2)):   # 下ほど細い(底は丸く)
        f = 0.55 + 0.45 * min(1, (y + 2) / 8)
        ship.append(C([-w * f, y, z], [w * f * 2, 2, 2], HULL if (y // 2 + z // 2) % 2 else HULL2, flat=True))
    ship.append(C([-w - 0.3, 6.5, z], [w * 2 + 0.6, 0.8, 2], MOSS if z % 6 == 0 else TRIM, flat=True))      # 板の段(ところどころ苔)
    ship.append(C([-w - 0.4, 10, z], [0.8, 2, 2], TRIM, flat=True)); ship.append(C([w - 0.4, 10, z], [0.8, 2, 2], TRIM, flat=True))   # ふちの手すり
    if z % 6 == 0 and -24 <= z <= 14:   # 光る丸窓
        for sx in (-1, 1): ship.append(C([sx * (w * 0.97) - 0.6, 4, z + 0.5], [1.2, 1.2, 1], GLOW, flat=True))
ship.append(C([-9, 9.5, -22], [18, 0.6, 46], DECK, flat=True))                      # 甲板
ship.append(C([-0.5, -1.5, -28], [1, 2, 54], HULL2))                                 # 竜骨
# 船尾の船室(高い)・窓・ランタン
ship += [C([-9, 10, 16], [18, 9, 12], HULL), C([-9.5, 19, 15.5], [19, 1, 13], TRIM, flat=True), C([-9.5, 20, 15.5], [1, 2, 13], TRIM, flat=True), C([8.5, 20, 15.5], [1, 2, 13], TRIM, flat=True)]
ship += [C([x, 13, 28.05], [2.4, 3, 0.4], GLOW, flat=True) for x in (-7, -3.2, 0.8, 4.6)]
ship += [C([sx, 12.5, z], [0.4, 2.6, 2], GLOW, flat=True) for sx in (-9.3, 8.9) for z in (18, 23)]
ship += [C([sx - 1, 20, 27], [2, 3, 2], GLOW, flat=True) for sx in (-8, 8)]
ship.append(C([-2, 10, 14.6], [4, 6, 1.4], WOOD, flat=True))                      # 船室の戸
# 船首の甲板と船首像(ドクロ)・斜めの帆柱
ship += [C([-6, 10, -26], [12, 2, 8], HULL), C([-2.5, 7, -34], [5, 5, 4], BONE), C([-1.7, 8.6, -34.3], [1.2, 1.4, 0.4], (20, 16, 24), flat=True), C([0.5, 8.6, -34.3], [1.2, 1.4, 0.4], (20, 16, 24), flat=True)]
ship.append(C([-0.6, 11, -46], [1.2, 1.2, 18], WOOD, rot=[16, 0, 0], pivot=[0, 11, -28]))
# マスト(前・中・後ろ): 柱・横木・破れた帆(穴あき・少しふくらむ)
for mz, mh, ys in ((-16, 40, (16, 28)), (-1, 50, (16, 30, 42)), (19, 30, (24,))):
    base = 20 if mz > 14 else 10
    ship.append(C([-1, base, mz - 1], [2, mh - (base - 10), 2], WOOD))
    for yy in ys:
        top = yy + 9 if yy + 9 < 10 + mh else 10 + mh - 2
        ship.append(C([-12, top, mz - 0.5], [24, 1, 1], WOOD))   # 横木
        rows = int((top - yy) // 3)
        for r in range(rows):
            y0 = top - 3 - r * 3; bulge = math.sin((r + 0.5) / rows * math.pi) * 1.4
            for c in range(6):
                if (c * 7 + r * 3 + mz) % 9 == 0: continue        # 破れた穴
                x0 = -11 + c * 3.7
                ship.append(C([x0, y0, mz - 1.4 - bulge], [3.7, 3, 0.4], SAIL if (c + r) % 2 else SAIL2, flat=True))
    ship.append(C([-1.5, 10 + mh - 1, mz - 1.5], [3, 2, 3], GLOW, flat=True))        # マストの上のランタン
# 中マストの見張り台・ドクロの旗
ship += [C([-3, 46, -4], [6, 0.8, 6], WOOD), C([-3, 46.8, -4], [6, 2, 0.5], WOOD, flat=True), C([-3, 46.8, 1.5], [6, 2, 0.5], WOOD, flat=True), C([-3, 46.8, -4], [0.5, 2, 6], WOOD, flat=True), C([2.5, 46.8, -4], [0.5, 2, 6], WOOD, flat=True)]
ship += [C([-0.2, 54, -1], [0.4, 6, 9], (24, 20, 30), flat=True), C([-0.35, 55.6, 2], [0.5, 2.6, 2.6], BONE, flat=True), C([-0.4, 56.4, 2.4], [0.6, 0.8, 0.6], (24, 20, 30), flat=True), C([-0.4, 56.4, 3.4], [0.6, 0.8, 0.6], (24, 20, 30), flat=True)]
# ロープ(マストの上からふちへ、ななめの細い線)
for mz, mh in ((-16, 40), (-1, 50)):
    for sx in (-1, 1):
        L = math.hypot(9, mh - 2); ang = math.degrees(math.atan2(9, mh - 2))
        ship.append(C([-0.2, 10, mz - 0.2], [0.4, L, 0.4], (40, 34, 30), flat=True, rot=[0, 0, -sx * ang], pivot=[0, 10 + mh - 2, mz]) if False else
                    C([sx * 9 - 0.2, 10, mz - 0.2], [0.4, L, 0.4], (40, 34, 30), flat=True, rot=[0, 0, sx * ang], pivot=[sx * 9, 10, mz]))
M.model('ghostship', '幽霊船(港に来る)', ship, anim={'root': {'rotation': ["math.sin(q.life_time * 60) * 2", 0, "math.sin(q.life_time * 45) * 3"], 'position': [0, "math.sin(q.life_time * 80) * 0.6", 0]}},
        box=(1.0, 1.0), scale=4.0)
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
# 幽霊船は大きいので、表示の範囲を広く(せまいと中心が画面の外に出たとき船ごと消える)
p = os.path.join(M.RP, 'models', 'entity', 'ghostship.geo.json'); g = json.load(open(p))
g['minecraft:geometry'][0]['description'].update({'visible_bounds_width': 24, 'visible_bounds_height': 24, 'visible_bounds_offset': [0, 8, 0]})
json.dump(g, open(p, 'w'), indent=1)
# ガイコツの骨の親子
p = os.path.join(M.RP, 'models', 'entity', 'mirrorskel.geo.json'); g = json.load(open(p))
for b in g['minecraft:geometry'][0]['bones']:
    b['parent'] = {'head': 'body', 'jaw': 'head', 'rightArm': 'body', 'leftArm': 'body', 'body': 'root', 'rightLeg': 'root', 'leftLeg': 'root'}.get(b['name'], b.get('parent'))
    if b['parent'] is None: b.pop('parent')
json.dump(g, open(p, 'w'), indent=1)
shutil.copy(os.path.join(M.PREVIEW, 'mirrorskel.png'), os.path.join(ROOT, 'mpl', 'preview_mirrorskel.png'))
print('ok')
