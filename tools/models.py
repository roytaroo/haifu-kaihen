# MMG Plus のモデル(エンティティ)を作る: BP の entities、RP の client entity・geometry・texture・animation、プレビュー画像
#   python3 tools/models.py → mmg/src/{behavior_packs/mmg_plus, resource_packs/mmg_plus_r} と dist/model_preview/*.png
# モデルは「色つきの箱」の組み合わせ。箱ごとに box UV の場所を自動で割り当て、色(少しノイズ入り)を塗る
import json, math, os, random
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, 'mmg', 'src', 'behavior_packs', 'mmg_plus')
RP = os.path.join(ROOT, 'mmg', 'src', 'resource_packs', 'mmg_plus_r')
PREVIEW = os.path.join(ROOT, 'dist', 'model_preview')

def C(origin, size, color, faces=None, bone='root', inflate=0, rot=None, pivot=None, decal=None, flat=False):
    # rot: [x, y, z] 度(pivot まわり)/ decal: {面: [(x, y, 色), ...]}(面 = top/bottom/north/south/east/west、面の左上が 0,0)
    # flat=True は陰影・ふち取りなし(目や小物)
    return dict(origin=origin, size=size, color=color, faces=faces or {}, bone=bone, inflate=inflate, rot=rot, pivot=pivot, decal=decal or {}, flat=flat)

# 名前: (説明, 箱, 骨(名前→pivot), アニメ, BPの追加, 当たり判定 [w,h], 座る位置, プロパティ)
RIDE = lambda y: {"minecraft:health": {"value": 1, "max": 1}, "minecraft:rideable": {"seat_count": 1, "family_types": ["player"], "interact_text": "乗る", "pull_in_entities": False, "seats": {"position": [0, y, 0]}}}
MODELS = {}
def model(name, desc, cubes, bones=None, anim=None, extra=None, box=(0.6, 0.6), gravity=False, props=None, scale=1.0, pose=None):
    # pose: プレビューの絵だけで骨を回す(例: ワニの口を開けた絵)
    MODELS[name] = dict(desc=desc, cubes=cubes, bones=bones or {'root': [0, 0, 0]}, anim=anim, extra=extra or {}, box=box, gravity=gravity, props=props or {}, scale=scale, pose=pose or {})

RED, WHITE, GOLD, GOLD2, GOLD3 = (220, 50, 60), (240, 240, 235), (245, 196, 40), (255, 230, 120), (190, 140, 20)
SHINE = (255, 255, 255)

def rounded(cx, cy, cz, rx, ry, rz, color, step=2, bands=None, **kw):
    # 丸い形: 高さ方向に薄い板を重ね、板ごとに「+」形の2枚で八角形にする
    # 板ごとのふち取りは横じまに見えるので使わず(flat)、上ほど明るく塗って丸みを出す。bands=(色2, 何枚ごと) で横の帯もよう
    out = []
    n = max(1, int(round(2 * ry / step)))
    for k in range(n):
        y0 = cy - ry + k * step; mid = y0 + step / 2 - cy
        f = max(0.0, 1 - (mid / ry) ** 2) ** 0.5
        w, d = 2 * rx * f, 2 * rz * f
        if w < 1 or d < 1: continue
        base = bands[0] if bands and (k // bands[1]) % 2 else color
        col = tuple(max(0, min(255, v + int(22 * (mid / ry)))) for v in base)
        out.append(C([cx - w / 2, y0, cz - d * 0.31], [w, step, d * 0.62], col, flat=True, **kw))
        out.append(C([cx - w * 0.31, y0, cz - d / 2], [w * 0.62, step, d], col, flat=True, **kw))
    return out
def disc(cx, y, cz, r, h, color, **kw):
    # 八角形の円盤
    return [C([cx - r, y, cz - r * 0.42], [2 * r, h, r * 0.84], color, **kw), C([cx - r * 0.42, y, cz - r], [r * 0.84, h, 2 * r], color, **kw),
            C([cx - r * 0.72, y, cz - r * 0.72], [r * 1.44, h, r * 1.44], color, **kw)]
def eyes(x, y, z, gap=4, size=3):
    # かわいい目(白目・黒目・光)を前(-z)に
    out = []
    for sx in (x - gap / 2 - size, x + gap / 2):
        out.append(C([sx, y, z - 0.3], [size, size + 1, 0.3], SHINE, flat=True))
        out.append(C([sx + size * 0.25, y + 0.3, z - 0.5], [size * 0.55, size * 0.75, 0.3], (25, 25, 35), flat=True))
        out.append(C([sx + size * 0.3, y + size * 0.55, z - 0.6], [size * 0.25, size * 0.25, 0.2], SHINE, flat=True))
    return out

# 風船: まんまるの本体・光・結び目・くねった糸(大きさは mmgplus:size)
model('balloon', '風船(ふくらむ風船・風船割り合戦)', [
    *rounded(0, 16, 0, 6.5, 7.5, 6.5, RED, step=0.75),
    C([-1.5, 7.5, -1.5], [3, 1.2, 3], (190, 35, 45)), C([-1, 6.5, -1], [2, 1, 2], (190, 35, 45)),
    C([-0.3, 3.5, -0.3], [0.6, 3, 0.6], WHITE, flat=True, rot=[0, 0, 12], pivot=[0, 6.5, 0]),
    C([-0.3, 0.5, -0.3], [0.6, 3, 0.6], WHITE, flat=True, rot=[0, 0, -10], pivot=[0, 3.5, 0])],
    anim={'root': {'scale': "0.5 + q.property('mmgplus:size') * 0.15", 'position': [0, "math.sin(q.life_time * 120) * 0.6", 0]}},
    props={'mmgplus:size': {'type': 'int', 'range': [0, 30], 'default': 3, 'client_sync': True}})
# コイン: 八角形の金貨・ふちの段・まんなかに星
star = [(4, 1), (4, 2), (3, 3), (4, 3), (5, 3), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (3, 6), (5, 6), (2, 7), (6, 7)]
model('coin', 'コイン(コイン噴水)', [
    *[C(c['origin'], c['size'], GOLD3) for c in [dict(origin=[-5, 0.5, -0.6], size=[10, 9, 1.2]), dict(origin=[-4, -0.5, -0.6], size=[8, 11, 1.2])]],
    C([-4, 0.5, -0.9], [8, 9, 1.8], GOLD), C([-3, -0.2, -0.9], [6, 10.4, 1.8], GOLD),
    C([-4, 1, -1.1], [9, 8, 0.2], GOLD2, flat=True, decal={'north': [(x, y, (210, 150, 20)) for (x, y) in star], 'south': [(x, y, (210, 150, 20)) for (x, y) in star]}),
    C([-3, 6.5, -1.2], [1.5, 1.5, 0.2], SHINE, flat=True)],
    bones={'root': [0, 5, 0]}, anim={'root': {'rotation': [0, "q.life_time * 240", 0], 'position': [0, "math.sin(q.life_time * 200) * 0.8", 0]}})
# たまご: たまご形・うすい模様 / 金のたまご: きらきら
EGG = (246, 236, 214)
model('egg', 'たまご(卵キャッチ)', [*rounded(0, 5, 0, 3.5, 5, 3.5, EGG, step=1), C([-2.5, 6, -3.1], [1, 1, 0.2], (215, 196, 160), flat=True), C([1, 3, -3.2], [1, 1, 0.2], (215, 196, 160), flat=True),
    C([-1.8, 7.5, -2.6], [1, 1.5, 0.2], SHINE, flat=True)])
model('golden_egg', '金のたまご(卵キャッチ・3点)', [*rounded(0, 5, 0, 3.5, 5, 3.5, GOLD, step=1), C([-1.8, 7.5, -2.6], [1, 1.5, 0.2], SHINE, flat=True),
    *[C([x, y, z], [0.8, 0.8, 0.8], GOLD2, flat=True) for (x, y, z) in [(-5, 9, 0), (4.5, 7, -1), (-4, 2, 2), (4, 1, 1)]]],
    bones={'root': [0, 5, 0]}, anim={'root': {'rotation': [0, "q.life_time * 180", 0]}})
# スイカ: まるい・しまもよう・つる・葉っぱ
GREEN, DGREEN = (70, 160, 66), (30, 92, 40)
model('melon', 'スイカ(まっくらスイカ割り)', [*rounded(0, 7, 0, 7.5, 7, 7.5, GREEN, step=1.5, faces={'stripes': DGREEN}),
    C([-0.6, 13.5, -0.6], [1.2, 2.5, 1.2], (100, 70, 35)), C([0, 15.5, -0.5], [3, 1, 1], (100, 70, 35), rot=[0, 0, -30], pivot=[0, 15.5, 0]),
    C([-4, 14, -1.5], [4, 0.5, 3], (60, 150, 50), rot=[0, 25, 10], pivot=[-1, 14, 0])], box=(0.9, 0.9))
CROC, CROC2, BELLY, MOUTH = (78, 178, 72), (52, 132, 54), (196, 214, 110), (226, 96, 110)
def eye(x, y, z, look=1):
    # 目: 白目 + 黒目 + 光、上にまぶた
    d = [(i, j, (250, 250, 250)) for i in range(4) for j in range(4)] + [(1 + look, 1, (25, 25, 30)), (1 + look, 2, (25, 25, 30)), (2 + look - 1, 1, (25, 25, 30)), (2 + look - 1, 2, (25, 25, 30)), (1 + look, 1, (255, 255, 255))]
    return [C([x, y, z], [4, 4, 4], (250, 250, 250), flat=True, decal={'north': d}, bone='upper'), C([x - 0.5, y + 3.5, z - 0.5], [5, 1.5, 5], CROC, bone='upper')]
def teeth(y, z0, z1, xs, bone, down):
    out = []
    for x in xs:
        for z in range(z0, z1, 2): out.append(C([x, y - (1.5 if down else 0), z], [1, 1.5, 1], (250, 248, 235), flat=True, bone=bone))
    for x in range(-5, 6, 2): out.append(C([x, y - (1.5 if down else 0), z0 - 0.5], [1, 1.5, 1], (250, 248, 235), flat=True, bone=bone))
    return out
model('croc', 'ワニ(ワニの歯)', [
    # 胴・おなか・背中のトゲ
    C([-8, 3, -2], [16, 8, 18], CROC), C([-7, 2, -1], [14, 1, 16], BELLY),
    *[C([x, 11, z], [2, 1.5, 2], CROC2, rot=[0, 45, 0]) for z in range(0, 16, 3) for x in (-4, 2)],
    # しっぽ(先へ細く、少しくねる)
    C([-6, 4, 16], [12, 6, 6], CROC), C([-5, 4.5, 21], [10, 5, 6], CROC, rot=[0, 8, 0], pivot=[0, 6, 21]),
    C([-3.5, 5, 26], [7, 4, 6], CROC, rot=[0, -10, 0], pivot=[0, 6, 26]), C([-2, 5.5, 31], [4, 3, 5], CROC2, rot=[0, 12, 0], pivot=[0, 6, 31]),
    *[C([-0.5, 10, z], [1, 1, 1.5], CROC2) for z in (17, 20, 23)],
    # 足と白いツメ
    *[C([x, 0, z], [4, 4, 4], CROC2) for x in (-10, 6) for z in (0, 11)],
    *[C([x + i, 0, z - 0.6], [0.8, 0.8, 0.8], (245, 245, 235), flat=True) for x in (-10, 6) for z in (0, 11) for i in (0.3, 1.6, 2.9)],
    # 下あご: 口の中・舌・歯
    C([-7, 2, -22], [14, 3, 20], CROC, bone='jaw'), C([-6, 4.6, -21], [12, 0.6, 18], MOUTH, flat=True, bone='jaw'), C([-2, 4.9, -17], [4, 0.6, 9], (200, 50, 60), flat=True, bone='jaw'),
    # 上あご: 鼻の穴・目・歯
    C([-7, 6, -22], [14, 4, 20], CROC, bone='upper'), C([-6, 5.8, -21], [12, 0.4, 18], MOUTH, flat=True, bone='upper'),
    C([-4, 10, -21], [2, 1, 2], CROC2, bone='upper'), C([2, 10, -21], [2, 1, 2], CROC2, bone='upper'),
    *teeth(6, -21, -5, (-6.5, 5.5), 'upper', True),
    *eye(-7, 10, -8, 0), *eye(3, 10, -8, 1)],
    bones={'root': [0, 0, 0], 'jaw': [0, 3, -2], 'upper': [0, 6, -2]},
    anim={'upper': {'rotation': ["-28 + q.property('mmgplus:bite') * 28", 0, 0]}},
    props={'mmgplus:bite': {'type': 'int', 'range': [0, 1], 'default': 0, 'client_sync': True}}, box=(0.4, 0.6), scale=4.0, pose={'upper': [28, 0, 0]})
# ワニの歯: まるみのある歯
model('tooth', 'ワニの歯(口の中に並ぶ・叩く)', [C([-1.5, 0, -1.5], [3, 4, 3], (250, 248, 236)), C([-1, 4, -1], [2, 1.2, 2], (252, 250, 242)), C([-1.2, 2.5, -1.6], [0.6, 1.2, 0.2], SHINE, flat=True)], box=(0.35, 0.45), scale=2.0)
# コマ: 色の帯の円盤を重ねた本格的なコマ・持ち手・金属の先
model('top', 'コマ(コマぶつけ・乗れる)', [
    *disc(0, 9, 0, 9, 2, (225, 55, 60)), *disc(0, 8, 0, 8.5, 1, WHITE), *disc(0, 6, 0, 7, 2, (50, 110, 220)), *disc(0, 4, 0, 5.5, 2, (250, 200, 50)),
    *disc(0, 2, 0, 3.5, 2, (225, 55, 60)), C([-1, 0, -1], [2, 2, 2], (170, 170, 180)), C([-0.5, -0.5, -0.5], [1, 0.8, 1], (120, 120, 130)),
    *disc(0, 11, 0, 4, 1, WHITE), C([-1.5, 12, -1.5], [3, 5, 3], (130, 80, 40)), C([-2, 17, -2], [4, 1.5, 4], (150, 95, 50))],
    anim={'root': {'rotation': [0, "q.life_time * 900", 0]}}, extra=RIDE(0.95), box=(1.1, 1.0), gravity=True)
# バンパーカー: 丸い車体・黒いゴムのバンパー・イス・ハンドル・ポールと火花・ライト・番号
BLUE, DBLUE = (50, 120, 230), (30, 75, 160)
num7 = [(x, 0, (255, 255, 255)) for x in range(4)] + [(3, y, (255, 255, 255)) for y in range(1, 6)]
model('car', 'バンパーカー(乗れる)', [
    *disc(0, 0.5, 0, 12, 3, (35, 35, 40)), *disc(0, 3, 0, 11, 5, BLUE), *disc(0, 8, 0, 10, 1, DBLUE),
    C([-6, 8, 3], [12, 3, 5], (230, 60, 60)), C([-6, 11, 7], [12, 9, 2], (230, 60, 60)), C([-6.5, 19, 6.5], [13, 1.5, 3], DBLUE),
    C([-1, 9, -6], [2, 5, 2], (60, 60, 70), rot=[-25, 0, 0], pivot=[0, 9, -5]), C([-3, 13, -8], [6, 1, 1], (40, 40, 45), rot=[-25, 0, 0], pivot=[0, 13, -7.5]),
    C([-4, 6, -10.6], [3, 2, 0.4], (255, 240, 150), flat=True), C([1, 6, -10.6], [3, 2, 0.4], (255, 240, 150), flat=True),
    C([-2, 4, 10.4], [4, 6, 0.4], DBLUE, flat=True, decal={'south': num7}),
    C([-0.5, 20, 8], [1, 14, 1], (200, 200, 210)), C([-2, 34, 6.5], [4, 1, 4], (250, 220, 40), flat=True), C([-1, 35, 7.5], [2, 2, 2], (255, 250, 200), flat=True)],
    extra=RIDE(0.62), box=(1.4, 1.0), gravity=True)
# 大玉: 大きなまるい玉(赤白のしま)/ ボヨンボール: ピンクの玉に顔
model('bigball', '大玉(大玉ころがし・乗れる)', [*rounded(0, 12, 0, 12, 12, 12, (230, 60, 60), step=2, bands=(WHITE, 2)), C([-6, 18, -11.5], [4, 4, 0.4], (255, 200, 200), flat=True)],
      bones={'root': [0, 12, 0]}, anim={'root': {'rotation': ["q.modified_distance_moved * 60", 0, 0]}}, extra=RIDE(1.55), box=(1.5, 1.5), gravity=True)
PINK = (245, 125, 200)
model('boyon', 'ボヨンボール(よける)', [*rounded(0, 12, 0, 12, 12, 12, PINK, step=2), *eyes(0, 13, -11.6, gap=5, size=4),
    C([-3, 8.5, -11.8], [6, 1.5, 0.3], (120, 40, 80), flat=True), C([-8.5, 9.5, -10.8], [3, 2, 0.3], (255, 170, 200), flat=True), C([5.5, 9.5, -10.8], [3, 2, 0.3], (255, 170, 200), flat=True),
    C([-7, 19, -9.8], [3, 2, 0.3], SHINE, flat=True)],
      bones={'root': [0, 12, 0]}, anim={'root': {'scale': ["1 + math.abs(math.sin(q.life_time * 400)) * 0.08", "1 - math.abs(math.sin(q.life_time * 400)) * 0.1", "1 + math.abs(math.sin(q.life_time * 400)) * 0.08"]}}, box=(1.5, 1.5), scale=1.4)
BROWN, BROWN2, MUZZLE, HORN = (122, 74, 42), (88, 52, 30), (232, 182, 160), (238, 226, 196)
angry = [(1, 2, (30, 25, 25)), (2, 2, (30, 25, 25)), (1, 3, (30, 25, 25)), (2, 3, (255, 255, 255)), (0, 1, (40, 25, 20)), (1, 1, (40, 25, 20)), (2, 0, (40, 25, 20)), (3, 0, (40, 25, 20)),
         (8, 2, (30, 25, 25)), (9, 2, (30, 25, 25)), (9, 3, (30, 25, 25)), (8, 3, (255, 255, 255)), (10, 1, (40, 25, 20)), (9, 1, (40, 25, 20)), (8, 0, (40, 25, 20)), (7, 0, (40, 25, 20))]
def horn(side):
    s = side
    return [C([s * 6 + (0 if s > 0 else -4), 24, -19], [4, 3, 3], HORN), C([s * 9.5 + (0 if s > 0 else -3), 25, -19], [3, 4, 3], HORN, rot=[0, 0, -25 * s], pivot=[s * 10, 25, -17.5]),
            C([s * 11 + (0 if s > 0 else -2), 28, -18.5], [2, 3, 2], (250, 245, 230), rot=[0, 0, -40 * s], pivot=[s * 12, 28, -17.5])]
model('bull', '暴れ牛(ロデオ・乗れる)', [
    # 胴(むね・こぶ・おなか)
    C([-8, 12, -12], [16, 12, 24], BROWN), C([-8.5, 11, -14], [17, 14, 7], BROWN), C([-6, 24, -14], [12, 3, 6], BROWN2), C([-6, 11.5, -9], [12, 1, 19], (150, 100, 66)),
    # 足(太もも・すね・ひづめ)
    *[C([x, 6, z], [5, 9, 5], BROWN) for x in (-8, 3) for z in (-11, 6)],
    *[C([x + 0.5, 2, z + 0.5], [4, 4, 4], BROWN) for x in (-8, 3) for z in (-11, 6)],
    *[C([x + 0.25, 0, z + 0.25], [4.5, 2, 4.5], (55, 50, 50)) for x in (-8, 3) for z in (-11, 6)],
    # 頭: 怒った目・まゆ、鼻、鼻輪、耳、角
    C([-6, 16, -22], [12, 10, 9], BROWN, decal={'north': [(x + 0, y + 3, c) for (x, y, c) in angry]}),
    C([-5, 14.5, -25], [10, 6, 4], MUZZLE, decal={'north': [(2, 2, (90, 50, 50)), (2, 3, (90, 50, 50)), (7, 2, (90, 50, 50)), (7, 3, (90, 50, 50))]}),
    C([-1.5, 13.5, -25.6], [3, 1, 0.6], (250, 200, 40), flat=True), C([-1.5, 12.5, -25.6], [0.8, 1.5, 0.6], (250, 200, 40), flat=True), C([0.7, 12.5, -25.6], [0.8, 1.5, 0.6], (250, 200, 40), flat=True), C([-1.5, 11.8, -25.6], [3, 0.8, 0.6], (250, 200, 40), flat=True),
    C([-9, 22, -17], [3, 2, 2], BROWN2, rot=[0, 0, 15]), C([6, 22, -17], [3, 2, 2], BROWN2, rot=[0, 0, -15]),
    *horn(1), *horn(-1),
    # くら(金のふち)と取っ手
    C([-7.5, 24.5, -7], [15, 1, 13], (200, 40, 45), faces={'rim': (240, 200, 60)}), C([-1, 25.5, -8], [2, 3, 2], (90, 55, 30)), C([-1.5, 28, -8.5], [3, 1, 3], (110, 70, 40)),
    C([-8.6, 17, -2], [1, 8, 1], (90, 55, 30)), C([7.6, 17, -2], [1, 8, 1], (90, 55, 30)), C([-9, 16, -3], [2, 1, 3], (180, 180, 190)), C([7, 16, -3], [2, 1, 3], (180, 180, 190)),
    # しっぽ
    C([-0.5, 15, 12], [1, 9, 1], BROWN2, rot=[25, 0, 0], pivot=[0, 23, 12]), C([-1.5, 12, 14.5], [3, 4, 3], (50, 35, 25))],
    bones={'root': [0, 0, 0]},
    anim={'root': {'rotation': ["math.sin(q.life_time * 500) * 8 * q.property('mmgplus:buck')", 0, "math.sin(q.life_time * 330) * 4 * q.property('mmgplus:buck')"],
                   'position': [0, "math.abs(math.sin(q.life_time * 500)) * 3 * q.property('mmgplus:buck')", 0]}},
    props={'mmgplus:buck': {'type': 'int', 'range': [0, 3], 'default': 0, 'client_sync': True}}, extra=RIDE(1.55), box=(1.0, 1.5), gravity=True)
# お皿の塔: ふちのある丸いお皿を5枚、少しずつずらして重ねる。てっぺんにサクランボ
plates = []
for i in range(5):
    dx = [0, 0.6, -0.4, 0.5, -0.3][i]; y = i * 2.4
    plates += disc(dx, y, 0, 3.5, 0.5, (225, 225, 220))                   # 底の台
    plates += disc(dx, y + 0.5, 0, 6.5, 0.9, WHITE)                       # お皿
    plates += disc(dx, y + 1.4, 0, 4.6, 0.12, (90, 140, 225), flat=True)  # 青い模様
    plates += disc(dx, y + 1.42, 0, 3.6, 0.12, WHITE, flat=True)
plates += [*rounded(-0.3, 13.6, 0, 1.4, 1.4, 1.4, (220, 30, 50), step=0.7), C([0, 14.8, -0.2], [0.4, 2.5, 0.4], (60, 120, 40), flat=True, rot=[0, 0, -20], pivot=[0, 14.8, 0])]
model('plates', 'お皿の塔(お皿バランス・頭の上)', plates,
      anim={'root': {'rotation': [0, 0, "q.property('mmgplus:tilt') * 4"]}},
      props={'mmgplus:tilt': {'type': 'int', 'range': [-10, 10], 'default': 0, 'client_sync': True}})
# しっぽ: ふわふわのキツネのしっぽ(根元から太く、先が白い。上に反る)
ORANGE = (240, 135, 40)
model('tail', 'しっぽ(しっぽ取り・叩いてうばう)', [
    C([-1.5, 4, -1], [3, 3, 3], ORANGE),
    C([-2.5, 4, 1.5], [5, 4, 4], ORANGE, rot=[-15, 0, 0], pivot=[0, 6, 1.5]), C([-3, 4.5, 4.5], [6, 5, 4], ORANGE, rot=[-25, 0, 0], pivot=[0, 6, 4.5]),
    C([-2.5, 5.5, 7.5], [5, 4.5, 3.5], ORANGE, rot=[-35, 0, 0], pivot=[0, 7, 7.5]), C([-2, 7, 10], [4, 4, 3], WHITE, rot=[-45, 0, 0], pivot=[0, 8.5, 10]),
    C([-1.2, 8.5, 12], [2.4, 2.4, 2], WHITE, rot=[-55, 0, 0], pivot=[0, 9.5, 12])],
    anim={'root': {'rotation': [0, "math.sin(q.life_time * 400) * 20", 0]}}, box=(0.5, 0.6))
# レーザーの発射台: 金属の台・注意の黄黒しま・赤く光るレンズ
model('laser', 'レーザーの発射台(レーザー回避)', [*disc(0, 0, 0, 5, 2, (70, 72, 82)), *disc(0, 2, 0, 4, 1, (240, 200, 40), faces={'stripes': (30, 30, 30)}),
    C([-2.5, 3, -2.5], [5, 4, 5], (90, 92, 104)), C([-1.5, 4, -3.2], [3, 2, 0.8], (255, 50, 50), flat=True), C([-0.8, 4.6, -3.4], [1, 1, 0.3], (255, 200, 200), flat=True),
    C([-3, 7, -3], [6, 1, 6], (60, 62, 72))])
model('laser_beam', 'レーザー(レーザー回避・端から端まで)', [
    *[C([-152 + i * 16, -1, -1], [16, 2, 2], (255, 40, 40), flat=True) for i in range(19)],
    *[C([-152 + i * 16, -0.4, -0.4], [16, 0.8, 0.8], (255, 230, 230), flat=True, inflate=0.05) for i in range(19)]],
    anim={'root': {'scale': [1, "1 + math.sin(q.life_time * 1600) * 0.25", "1 + math.sin(q.life_time * 1600) * 0.25"]}}, box=(0.2, 0.2))
# イス: 木のイス(脚4本・すじ入りの背もたれ・赤いクッション)
WOOD, WOOD2 = (170, 115, 65), (130, 85, 45)
model('chair', 'イス(椅子取りゲーム・座れる)', [
    *[C([x, 0, z], [2, 8, 2], WOOD2) for x in (-6, 4) for z in (-6, 4)],
    C([-6.5, 8, -6.5], [13, 1.5, 13], WOOD), C([-5.5, 9.5, -5.5], [11, 1.5, 10], (210, 50, 55)), C([-4.5, 11, -4.5], [3, 0.3, 3], (240, 120, 120), flat=True),
    C([-6, 9.5, 4.5], [2, 14, 2], WOOD2), C([4, 9.5, 4.5], [2, 14, 2], WOOD2), C([-6.5, 22, 4], [13, 2.5, 3], WOOD),
    *[C([x, 11, 5], [1.5, 11, 1], WOOD) for x in (-3, -0.75, 1.5)],
    C([-6, 3, -5.5], [12, 1, 1], WOOD2), C([-6, 3, 4.5], [12, 1, 1], WOOD2)],
    extra=RIDE(0.45), box=(0.9, 0.7), gravity=True)

# ===== 書き出し =====
def noise(c, k):
    return tuple(max(0, min(255, v + k)) for v in c)

def face_rects(u, v, w, h, d):
    return {'top': (u + d, v, w, d), 'bottom': (u + d + w, v, w, d), 'east': (u, v + d, d, h), 'north': (u + d, v + d, w, h),
            'west': (u + d + w, v + d, d, h), 'south': (u + 2 * d + w, v + d, w, h)}

def build_texture(name, m):
    # 箱ごとに box UV の場所を棚づめで割り当てる
    W = 256
    x = y = rowh = 0
    for cb in m['cubes']:
        w, h, d = [max(1, math.ceil(v)) for v in cb['size']]
        uw, uh = 2 * d + 2 * w, d + h
        if x + uw > W: x, y, rowh = 0, y + rowh, 0
        cb['uv'] = [x, y]; cb['uvsize'] = (w, h, d)
        x += uw; rowh = max(rowh, uh)
    H = 1 << max(4, math.ceil(math.log2(y + rowh)))
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    rnd = random.Random(name)
    for cb in m['cubes']:
        u, v = cb['uv']; w, h, d = cb['uvsize']; col = cb['color']; f = cb['faces']
        for face, (fx, fy, fw, fh) in face_rects(u, v, w, h, d).items():
            for lx in range(fw):
                for ly in range(fh):
                    c = noise(col, rnd.randint(-6, 6))
                    if 'stripes' in f and (((fx + lx - u) // 3) % 2 == 0): c = noise(f['stripes'], rnd.randint(-5, 5))
                    if 'rim' in f and face == 'top' and (lx in (0, fw - 1) or ly in (0, fh - 1)): c = f['rim']
                    if not cb['flat']:
                        if face == 'top': c = noise(c, 14)
                        elif face == 'bottom': c = noise(c, -34)
                        else: c = noise(c, int(10 - 26 * ly / max(1, fh - 1)))  # 側面は上から下へ暗く
                        if fw >= 3 and fh >= 3 and (lx in (0, fw - 1) or ly in (0, fh - 1)): c = noise(c, -22)  # ふち取り
                    im.putpixel((fx + lx, fy + ly), c + (255,))
            for (dx, dy, dc) in cb['decal'].get(face, []):
                if 0 <= dx < fw and 0 <= dy < fh: im.putpixel((fx + dx, fy + dy), tuple(dc) + (255,))
    os.makedirs(os.path.join(RP, 'textures', 'entity'), exist_ok=True)
    im.save(os.path.join(RP, 'textures', 'entity', f'mmgplus_{name}.png'))
    return im

def write(name, m):
    tex = build_texture(name, m)
    bones = []
    for b, piv in m['bones'].items():
        cubes = [{'origin': cb['origin'], 'size': cb['size'], 'uv': cb['uv'], **({'inflate': cb['inflate']} if cb['inflate'] else {}),
                  **({'rotation': cb['rot'], 'pivot': cb['pivot'] or [cb['origin'][i] + cb['size'][i] / 2 for i in range(3)]} if cb.get('rot') else {})}
                 for cb in m['cubes'] if cb['bone'] == b]
        bone = {'name': b, 'pivot': piv, 'cubes': cubes}
        if b != 'root': bone['parent'] = 'root'
        bones.append(bone)
    geo = {'format_version': '1.12.0', 'minecraft:geometry': [{'description': {'identifier': f'geometry.mmgplus.{name}', 'texture_width': tex.width, 'texture_height': tex.height}, 'bones': bones}]}
    json.dump(geo, open(os.path.join(RP, 'models', 'entity', f'{name}.geo.json'), 'w'), indent=1)
    desc = {'identifier': f'mmgplus:{name}', 'materials': {'default': 'entity_alphatest'}, 'textures': {'default': f'textures/entity/mmgplus_{name}'},
            'geometry': {'default': f'geometry.mmgplus.{name}'}, 'render_controllers': ['controller.render.default']}
    if m['anim']:
        desc['animations'] = {'a': f'animation.mmgplus.{name}'}; desc['scripts'] = {'animate': ['a']}
        json.dump({'format_version': '1.8.0', 'animations': {f'animation.mmgplus.{name}': {'loop': True, 'bones': m['anim']}}},
                  open(os.path.join(RP, 'animations', f'{name}.animation.json'), 'w'), indent=1)
    json.dump({'format_version': '1.10.0', 'minecraft:client_entity': {'description': desc}}, open(os.path.join(RP, 'entity', f'{name}.entity.json'), 'w'), indent=1)
    comps = {'minecraft:collision_box': {'width': m['box'][0], 'height': m['box'][1]},
             'minecraft:physics': {} if m['gravity'] else {'has_gravity': False, 'has_collision': False},
             'minecraft:damage_sensor': {'triggers': [{'cause': 'all', 'deals_damage': 'no'}]},
             'minecraft:pushable': {'is_pushable': False, 'is_pushable_by_piston': False},
             'minecraft:type_family': {'family': ['mmgplus_prop', 'inanimate']}, **m['extra']}
    if m['scale'] != 1: comps['minecraft:scale'] = {'value': m['scale']}
    d = {'identifier': f'mmgplus:{name}', 'is_spawnable': False, 'is_summonable': True}
    if m['props']: d['properties'] = m['props']
    json.dump({'format_version': '1.21.20', 'minecraft:entity': {'description': d, 'components': comps}}, open(os.path.join(BP, 'entities', f'{name}.json'), 'w'), indent=1, ensure_ascii=False)
    preview(name, m, tex)

# ===== プレビュー(斜め上から見た絵) =====
def rotate_cube(cb, pts):
    if not cb.get('rot'): return pts
    piv = cb['pivot'] or [cb['origin'][i] + cb['size'][i] / 2 for i in range(3)]
    rx, ry, rz = [math.radians(a) for a in cb['rot']]
    out = []
    for (x, y, z) in pts:
        x, y, z = x - piv[0], y - piv[1], z - piv[2]
        y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
        x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
        x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
        out.append((x + piv[0], y + piv[1], z + piv[2]))
    return out

def faces_of(cb):
    (x, y, z), (w, h, d) = cb['origin'], cb['size']
    u, v = cb['uv']; tw, th, td = cb['uvsize']
    X0, X1, Y0, Y1, Z0, Z1 = x, x + w, y, y + h, z, z + d
    # (4つの角 = テクスチャの左上・右上・右下・左下 に対応, テクスチャの矩形)
    return [
        ([(X0, Y1, Z0), (X1, Y1, Z0), (X1, Y1, Z1), (X0, Y1, Z1)], (u + td, v, u + td + tw, v + td)),            # 上
        ([(X1, Y1, Z0), (X0, Y1, Z0), (X0, Y0, Z0), (X1, Y0, Z0)], (u + td, v + td, u + td + tw, v + td + th)),  # 北(-z)
        ([(X0, Y1, Z1), (X1, Y1, Z1), (X1, Y0, Z1), (X0, Y0, Z1)], (u + 2 * td + tw, v + td, u + 2 * td + 2 * tw, v + td + th)),  # 南
        ([(X1, Y1, Z1), (X1, Y1, Z0), (X1, Y0, Z0), (X1, Y0, Z1)], (u, v + td, u + td, v + td + th)),            # 東(+x)
        ([(X0, Y1, Z0), (X0, Y1, Z1), (X0, Y0, Z1), (X0, Y0, Z0)], (u + td + tw, v + td, u + 2 * td + tw, v + td + th)),  # 西
        ([(X0, Y0, Z1), (X1, Y0, Z1), (X1, Y0, Z0), (X0, Y0, Z0)], (u + td + tw, v, u + td + 2 * tw, v + td)),   # 下
    ]

def homography(src, dst):
    # dst(出力の点) → src(テクスチャの点) の 8 係数(PIL の PERSPECTIVE 用)
    import numpy as np
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return list(np.linalg.solve(np.array(A, float), np.array(B, float)))

def preview(name, m, tex, size=512, yaw=145, pitch=26):
    # 正射影 + 1ピクセルごとの奥行き(zバッファ)。面の向きで明るさを変える
    import numpy as np
    cy, sy, cp, sp = math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    def rot(p):
        x, y, z = p; x, z = x * cy - z * sy, x * sy + z * cy
        y, z = y * cp - z * sp, y * sp + z * cp
        return x, y, z
    pose = m.get('pose', {})
    def placed(cb, f):
        q = rotate_cube(cb, f)
        if cb.get('bone') in pose: q = rotate_cube({'rot': pose[cb['bone']], 'pivot': m['bones'][cb['bone']], 'origin': [0, 0, 0], 'size': [0, 0, 0]}, q)
        return q
    pts = [rot(c) for cb in m['cubes'] for f, _ in faces_of(cb) for c in placed(cb, f)]
    minx, maxx = min(p[0] for p in pts), max(p[0] for p in pts); miny, maxy = min(p[1] for p in pts), max(p[1] for p in pts)
    k = (size * 0.84) / max(maxx - minx, maxy - miny, 1)
    ox, oy = size / 2 - (minx + maxx) / 2 * k, size / 2 + (miny + maxy) / 2 * k
    T = np.array(tex.convert('RGBA')); TH, TW = T.shape[:2]
    img = np.zeros((size, size, 4), np.uint8); zb = np.full((size, size), np.inf)
    light = [1.0, 0.86, 0.74, 0.93, 0.8, 0.6]  # 上・北・南・東・西・下
    for cb in m['cubes']:
        for fi, (corners, (u0, v0, u1, v1)) in enumerate(faces_of(cb)):
            if u1 <= u0 or v1 <= v0: continue
            r = [rot(c) for c in placed(cb, corners)]
            P = [(ox + q[0] * k, oy - q[1] * k, -q[2]) for q in r]  # -z: 手前ほど小さい
            UV = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
            for tri in ((0, 1, 2), (0, 2, 3)):
                (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = [P[i] for i in tri]
                den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
                if abs(den) < 1e-9: continue
                bx0, bx1 = int(max(0, min(x0, x1, x2))), int(min(size - 1, max(x0, x1, x2)) + 1)
                by0, by1 = int(max(0, min(y0, y1, y2))), int(min(size - 1, max(y0, y1, y2)) + 1)
                if bx1 <= bx0 or by1 <= by0: continue
                X, Y = np.meshgrid(np.arange(bx0, bx1) + 0.5, np.arange(by0, by1) + 0.5)
                w0 = ((y1 - y2) * (X - x2) + (x2 - x1) * (Y - y2)) / den
                w1 = ((y2 - y0) * (X - x2) + (x0 - x2) * (Y - y2)) / den
                w2 = 1 - w0 - w1
                inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
                if not inside.any(): continue
                Z = w0 * z0 + w1 * z1 + w2 * z2
                uvs = [UV[i] for i in tri]
                U = np.clip((w0 * uvs[0][0] + w1 * uvs[1][0] + w2 * uvs[2][0]).astype(int), 0, TW - 1)
                V = np.clip((w0 * uvs[0][1] + w1 * uvs[1][1] + w2 * uvs[2][1]).astype(int), 0, TH - 1)
                col = T[V, U]
                sub = zb[by0:by1, bx0:bx1]
                ok = inside & (col[..., 3] > 10) & (Z < sub)
                sub[ok] = Z[ok]
                c = col.astype(float); c[..., :3] *= light[fi]
                img[by0:by1, bx0:bx1][ok] = c[ok].clip(0, 255).astype(np.uint8)
    os.makedirs(PREVIEW, exist_ok=True)
    Image.fromarray(img, 'RGBA').save(os.path.join(PREVIEW, f'{name}.png'))

if __name__ == '__main__':
    for d in [os.path.join(RP, 'models', 'entity'), os.path.join(RP, 'animations'), os.path.join(RP, 'entity'), os.path.join(BP, 'entities')]: os.makedirs(d, exist_ok=True)
    for name, m in MODELS.items(): write(name, m)
    json.dump({n: m['desc'] for n, m in MODELS.items()}, open(os.path.join(PREVIEW, 'index.json'), 'w'), ensure_ascii=False, indent=1)
    print(len(MODELS), 'models')
