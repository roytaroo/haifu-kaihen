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
SKIN, SKIN2 = (198, 140, 104), (176, 120, 88)
HOOD, HOOD2, TEE, JEANS, GOLD, BLACK = (34, 32, 44), (24, 22, 32), (245, 245, 250), (52, 64, 104), (250, 200, 60), (20, 18, 26)
CAP, CAP2, NEON, HAIR = (235, 60, 150), (190, 40, 120), (60, 230, 240), (40, 30, 26)
# プレイヤーと同じ体の形(足 12・体 12・頭 8・うで 4x12)。小物は 0.5 以上の厚みで、体から少しだけ浮かせる(欠けとズレをふせぐ)
dj = [
    # 足: ジーンズ + 白いスニーカー(ピンクの線)
    C([-4, 2, -2], [4, 10, 4], JEANS, bone='rightLeg'), C([-4, 0, -2.5], [4, 2, 4.5], TEE, bone='rightLeg'), C([-4.05, 0.6, -2.55], [4.1, 0.6, 4.6], CAP, flat=True, bone='rightLeg'),
    C([0, 2, -2], [4, 10, 4], JEANS, bone='leftLeg'), C([0, 0, -2.5], [4, 2, 4.5], TEE, bone='leftLeg'), C([-0.05, 0.6, -2.55], [4.1, 0.6, 4.6], CAP, flat=True, bone='leftLeg'),
    # 体: 黒いパーカー(前が開いて白い T シャツ)・金のくさり・背中のフード
    C([-4, 12, -2], [8, 12, 4], HOOD, bone='body'),
    C([-2, 12.5, -2.5], [4, 11, 0.5], TEE, flat=True, bone='body'),
    C([-1, 17, -2.8], [2, 2, 0.5], CAP, flat=True, bone='body'),                                   # T シャツのマーク
    *[C([-1.75 + i * 0.5 - 0.25, 21.5 - min(i, 7 - i) * 0.5, -2.9], [0.5, 0.5, 0.5], GOLD, flat=True, bone='body') for i in range(8)],
    C([-4, 21, 2], [8, 3, 1.5], HOOD2, bone='body'),
    C([-4, 12, -2.05], [8, 1, 4.1], HOOD2, flat=True, bone='body'),                                # すその帯
    # 頭: はだ・髪(横は短く)・まゆ・口
    C([-4, 24, -4], [8, 8, 8], SKIN, bone='head'),
    C([-4.25, 29, -4.25], [8.5, 2.5, 8.5], HAIR, bone='head'), C([-4.25, 25, 0], [8.5, 4, 4.25], HAIR, bone='head'),
    C([-3, 25.5, -4.3], [2, 0.5, 0.5], (150, 80, 70), flat=True, bone='head'), C([-1, 25.5, -4.3], [3, 0.5, 0.5], (150, 80, 70), flat=True, bone='head'),  # にやっとした口
    C([-4.3, 26, -1], [0.5, 1.5, 1.5], SKIN2, flat=True, bone='head'), C([3.8, 26, -1], [0.5, 1.5, 1.5], SKIN2, flat=True, bone='head'),
    # 後ろ向きのキャップ(つばは後ろ)
    C([-4.5, 30.5, -4.5], [9, 2.5, 9], CAP, bone='head'), C([-4.5, 30.5, -4.55], [9, 1, 9.1], CAP2, flat=True, bone='head'),
    C([-3.5, 30.5, 4.5], [7, 0.5, 3.5], CAP2, bone='head'),
    # ヘッドホン(耳にかけて、上のバンドはキャップの上)
    C([-5.5, 25.5, -1.5], [1.5, 4, 3], NEON, bone='head'), C([4, 25.5, -1.5], [1.5, 4, 3], NEON, bone='head'),
    C([-5.5, 29.5, -0.5], [1, 3.5, 1], BLACK, bone='head'), C([4.5, 29.5, -0.5], [1, 3.5, 1], BLACK, bone='head'),
    C([-5.5, 33, -0.5], [11, 1, 1], BLACK, bone='head'),
    # サングラス(1 つの骨: おどろくと上へはねる)
    C([-4.5, 27, -4.6], [9, 0.5, 0.5], BLACK, flat=True, bone='glasses'),
    C([-3.75, 25.75, -4.75], [3.25, 1.75, 0.5], BLACK, flat=True, bone='glasses'), C([0.5, 25.75, -4.75], [3.25, 1.75, 0.5], BLACK, flat=True, bone='glasses'),
    C([-3.25, 26.0, -5.0], [2.25, 1.25, 0.5], (255, 70, 170), flat=True, bone='glasses'), C([1.0, 26.0, -5.0], [2.25, 1.25, 0.5], (150, 80, 255), flat=True, bone='glasses'),
    C([-3.0, 26.75, -5.1], [0.75, 0.5, 0.5], (255, 230, 245), flat=True, bone='glasses'), C([1.25, 26.75, -5.1], [0.75, 0.5, 0.5], (240, 230, 255), flat=True, bone='glasses'),
    # うで: パーカーのそで・金のそで口・手
    C([-8, 15, -2], [4, 9, 4], HOOD, bone='rightArm'), C([-8.05, 14.5, -2.05], [4.1, 1, 4.1], GOLD, flat=True, bone='rightArm'), C([-8, 12, -2], [4, 2.5, 4], SKIN, bone='rightArm'),
    C([4, 15, -2], [4, 9, 4], HOOD, bone='leftArm'), C([3.95, 14.5, -2.05], [4.1, 1, 4.1], GOLD, flat=True, bone='leftArm'), C([4, 12, -2], [4, 2.5, 4], SKIN, bone='leftArm'),
]
# 動き(128bpm に合わせる。1拍 = 768度/秒)。気分の切りかえは pre_animation で少しずつ変える(パッと変わらない)
B = "q.life_time * 768"
tk, sp, idl = "v.tk", "v.sp", "(1 - v.tk - v.sp)"
dj_anim = {
    'root': {'position': [0, f"{idl} * math.abs(math.sin(q.life_time * 384)) * 0.5 + {sp} * math.abs(math.sin(q.life_time * 500)) * 1.5", 0]},
    'body': {'rotation': [f"{idl} * 4 + {tk} * math.sin(q.life_time * 200) * 2", f"{tk} * math.sin(q.life_time * 150) * 6", 0]},
    'head': {'rotation': [f"{idl} * (math.sin({B}) * 7 + 3) + {tk} * math.sin(q.life_time * 400) * 4 - {sp} * 12", f"{tk} * math.sin(q.life_time * 130) * 10 + {idl} * math.sin(q.life_time * 96) * 8", 0]},
    'glasses': {'position': [0, f"{sp} * 2.5", f"{sp} * -0.5"]},
    # まつとき: 両手をデッキに(右はスクラッチ、左はつまみ) / しゃべる: 右手で客をさす・左手は軽く / おどろく: 両手を上へ
    'rightArm': {'rotation': [f"{idl} * (-68 + math.sin({B}) * 4) + {tk} * (-75 + math.sin(q.life_time * 300) * 12) + {sp} * -165", f"{idl} * math.sin({B} * 2) * 10", f"{tk} * 8 + {sp} * 18"]},
    'leftArm': {'rotation': [f"{idl} * (-62 + math.sin({B} + 180) * 3) + {tk} * (-25 + math.sin(q.life_time * 260 + 90) * 10) + {sp} * -165", 0, f"{tk} * -10 - {sp} * 18"]},
}
M.model('dj', 'DJトシオ(司会)', dj, bones={'root': [0, 0, 0], 'rightLeg': [-2, 12, 0], 'leftLeg': [2, 12, 0], 'body': [0, 12, 0], 'head': [0, 24, 0], 'glasses': [0, 27, -4.6], 'rightArm': [-6, 22, 0], 'leftArm': [6, 22, 0]},
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
    if b['name'] == 'glasses': b['parent'] = 'head'
    if b['name'] in ('head', 'rightArm', 'leftArm'): b['parent'] = 'body'
    if b['name'] in ('body', 'rightLeg', 'leftLeg'): b['parent'] = 'root'
json.dump(g, open(p, 'w'), indent=1)
# 気分をなめらかに変える
p = os.path.join(M.RP, 'entity', 'dj.entity.json'); e = json.load(open(p))
e['minecraft:client_entity']['description']['scripts']['pre_animation'] = [
    "v.tk = math.lerp(v.tk ?? 0, q.property('mmgplus:mood') == 1, 0.12);", "v.sp = math.lerp(v.sp ?? 0, q.property('mmgplus:mood') == 2, 0.18);"]
json.dump(e, open(p, 'w'), indent=1)
for n in ('dj', 'ghostship'): shutil.copy(os.path.join(M.PREVIEW, f'{n}.png'), os.path.join(ROOT, 'mpl', f'preview_{n}.png'))
print('ok')
