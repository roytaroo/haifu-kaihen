# MMG Plus のモデル(エンティティ)を作る: BP の entities、RP の client entity・geometry・texture・animation、プレビュー画像
#   python3 tools/models.py → mmg/src/{behavior_packs/mmg_plus, resource_packs/mmg_plus_r} と dist/model_preview/*.png
# モデルは「色つきの箱」の組み合わせ。箱ごとに box UV の場所を自動で割り当て、色(少しノイズ入り)を塗る
import json, math, os, random
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, 'mmg', 'src', 'behavior_packs', 'mmg_plus')
RP = os.path.join(ROOT, 'mmg', 'src', 'resource_packs', 'mmg_plus_r')
PREVIEW = os.path.join(ROOT, 'dist', 'model_preview')

def C(origin, size, color, faces=None, bone='root', inflate=0):
    return dict(origin=origin, size=size, color=color, faces=faces or {}, bone=bone, inflate=inflate)

# 名前: (説明, 箱, 骨(名前→pivot), アニメ, BPの追加, 当たり判定 [w,h], 座る位置, プロパティ)
RIDE = lambda y: {"minecraft:rideable": {"seat_count": 1, "family_types": ["player"], "interact_text": "乗る", "pull_in_entities": False, "seats": {"position": [0, y, 0]}}}
MODELS = {}
def model(name, desc, cubes, bones=None, anim=None, extra=None, box=(0.6, 0.6), gravity=False, props=None, scale=1.0):
    MODELS[name] = dict(desc=desc, cubes=cubes, bones=bones or {'root': [0, 0, 0]}, anim=anim, extra=extra or {}, box=box, gravity=gravity, props=props or {}, scale=scale)

RED, WHITE, GOLD, GOLD2 = (220, 50, 60), (240, 240, 235), (245, 196, 40), (255, 230, 120)
# 風船(大きさは mmgplus:size で変わる)
model('balloon', '風船(ふくらむ風船・風船割り合戦)', [
    C([-5, 10, -5], [10, 12, 10], RED, inflate=0), C([-4, 22, -4], [8, 1, 8], RED), C([-4, 9, -4], [8, 1, 8], RED),
    C([-1, 7, -1], [2, 2, 2], (180, 30, 40)), C([-0.5, 0, -0.5], [1, 7, 1], WHITE),
    C([-3, 18, -5.2], [2, 3, 0.2], (255, 160, 170))],
    anim={'root': {'scale': "0.5 + q.property('mmgplus:size') * 0.15"}},
    props={'mmgplus:size': {'type': 'int', 'range': [0, 30], 'default': 3, 'client_sync': True}})
model('coin', 'コイン(コイン噴水)', [C([-4, 0, -0.5], [8, 8, 1], GOLD), C([-3, 1, -0.7], [6, 6, 1.4], GOLD2), C([-1, 2, -0.9], [2, 4, 1.8], GOLD)],
      anim={'root': {'rotation': [0, "q.life_time * 240", 0]}})
model('egg', 'たまご(卵キャッチ)', [C([-3, 0, -3], [6, 7, 6], (245, 235, 210)), C([-2, 7, -2], [4, 2, 4], (245, 235, 210)), C([-2, 1, -3.1], [1, 1, 0.1], (200, 180, 150))])
model('golden_egg', '金のたまご(卵キャッチ・3点)', [C([-3, 0, -3], [6, 7, 6], GOLD), C([-2, 7, -2], [4, 2, 4], GOLD2)],
      anim={'root': {'rotation': [0, "q.life_time * 180", 0]}})
GREEN, DGREEN = (60, 150, 60), (30, 90, 40)
model('melon', 'スイカ(まっくらスイカ割り)', [C([-7, 0, -7], [14, 13, 14], GREEN, faces={'stripes': DGREEN}), C([-1, 13, -1], [2, 2, 2], (90, 60, 30))], box=(0.9, 0.9))
CROC, CROC2 = (70, 140, 70), (50, 110, 55)
model('croc', 'ワニ(ワニの歯)', [
    C([-14, 0, -18], [28, 5, 34], CROC2, bone='jaw'), C([-13, 5, -17], [26, 1, 32], (200, 70, 80), bone='jaw'),
    C([-14, 6, -18], [28, 6, 34], CROC, bone='upper'), C([-11, 12, 6], [6, 5, 6], WHITE, bone='upper'), C([5, 12, 6], [6, 5, 6], WHITE, bone='upper'),
    C([-9, 14, 5.8], [2, 3, 0.4], (20, 20, 20), bone='upper'), C([7, 14, 5.8], [2, 3, 0.4], (20, 20, 20), bone='upper'),
    C([-6, 12, -16], [2, 1, 2], (30, 60, 30), bone='upper'), C([4, 12, -16], [2, 1, 2], (30, 60, 30), bone='upper')],
    bones={'root': [0, 0, 0], 'jaw': [0, 0, 16], 'upper': [0, 6, 16]},
    anim={'upper': {'rotation': ["-35 + q.property('mmgplus:bite') * 35", 0, 0]}},
    props={'mmgplus:bite': {'type': 'int', 'range': [0, 1], 'default': 0, 'client_sync': True}}, box=(1.8, 0.8), scale=1.6)
model('tooth', 'ワニの歯(叩く)', [C([-1.5, 0, -1.5], [3, 5, 3], WHITE), C([-1, 5, -1], [2, 1, 2], (255, 250, 240))], box=(0.4, 0.5))
model('top', 'コマ(コマぶつけ・乗れる)', [
    C([-8, 7, -8], [16, 4, 16], RED, faces={'stripes': (250, 210, 60)}), C([-6, 4, -6], [12, 3, 12], (250, 210, 60)), C([-4, 1, -4], [8, 3, 8], RED),
    C([-1, 0, -1], [2, 1, 2], (60, 60, 60)), C([-2, 11, -2], [4, 5, 4], (90, 60, 30))],
    anim={'root': {'rotation': [0, "q.life_time * 900", 0]}}, extra=RIDE(0.7), box=(1.0, 1.0), gravity=True)
BLUE = (50, 110, 220)
model('car', 'バンパーカー(乗れる)', [
    C([-9, 3, -13], [18, 7, 26], BLUE), C([-10, 2, -14], [20, 2, 28], (250, 150, 40)), C([-6, 9, 4], [12, 8, 3], BLUE),
    C([-10, 0, -10], [2, 4, 5], (40, 40, 40)), C([8, 0, -10], [2, 4, 5], (40, 40, 40)), C([-10, 0, 6], [2, 4, 5], (40, 40, 40)), C([8, 0, 6], [2, 4, 5], (40, 40, 40)),
    C([-2, 9, -10], [4, 4, 1], (60, 60, 60)), C([-1, 17, 5], [2, 10, 1], (200, 200, 200)), C([-3, 25, 5.5], [6, 4, 0.2], (250, 220, 0))],
    extra=RIDE(0.55), box=(1.3, 1.0), gravity=True)
def ball(color, color2):
    return [C([-12, 4, -8], [24, 16, 16], color, faces={'stripes': color2}), C([-8, 0, -12], [16, 24, 24], color, faces={'stripes': color2}), C([-10, 2, -10], [20, 20, 20], color2)]
model('bigball', '大玉(大玉ころがし・乗れる)', ball((230, 60, 60), WHITE), bones={'root': [0, 12, 0]},
      anim={'root': {'rotation': ["q.modified_distance_moved * 60", 0, 0]}}, extra=RIDE(1.55), box=(1.5, 1.5), gravity=True)
model('boyon', 'ボヨンボール(よける)', ball((240, 120, 200), (255, 230, 120)), bones={'root': [0, 12, 0]},
      anim={'root': {'rotation': ["q.life_time * 200", "q.life_time * 90", 0]}}, box=(1.5, 1.5), scale=1.4)
BROWN = (110, 70, 40)
model('bull', '暴れ牛(ロデオ・乗れる)', [
    C([-7, 10, -11], [14, 12, 22], BROWN), C([-6, 0, -10], [4, 10, 4], BROWN), C([2, 0, -10], [4, 10, 4], BROWN), C([-6, 0, 6], [4, 10, 4], BROWN), C([2, 0, 6], [4, 10, 4], BROWN),
    C([-5, 14, -19], [10, 10, 8], BROWN), C([-3, 14, -20], [6, 4, 1], (230, 170, 160)), C([-9, 22, -16], [4, 2, 2], WHITE), C([5, 22, -16], [4, 2, 2], WHITE),
    C([-4, 20, -19.2], [2, 2, 0.2], (20, 20, 20)), C([2, 20, -19.2], [2, 2, 0.2], (20, 20, 20)), C([-5, 22, -6], [10, 1, 10], (200, 40, 40)), C([-1, 18, 11], [2, 2, 6], BROWN)],
    bones={'root': [0, 0, 0]},
    anim={'root': {'rotation': ["math.sin(q.life_time * 500) * 6 * q.property('mmgplus:buck')", 0, "q.property('mmgplus:buck') * 0"],
                   'position': [0, "math.abs(math.sin(q.life_time * 500)) * 3 * q.property('mmgplus:buck')", 0]}},
    props={'mmgplus:buck': {'type': 'int', 'range': [0, 3], 'default': 0, 'client_sync': True}}, extra=RIDE(1.45), box=(1.0, 1.4), gravity=True)
model('plates', 'お皿の塔(お皿バランス・頭の上)', [C([-6, i * 3, -6], [12, 1, 12], WHITE, faces={'rim': (60, 110, 220)}) for i in range(5)] + [C([-1, 15, -1], [2, 2, 2], (250, 120, 40))],
      anim={'root': {'rotation': [0, 0, "q.property('mmgplus:tilt') * 4"]}},
      props={'mmgplus:tilt': {'type': 'int', 'range': [-10, 10], 'default': 0, 'client_sync': True}})
model('tail', 'しっぽ(しっぽ取り・叩いてうばう)', [C([-2, 4, -2], [4, 4, 4], (240, 140, 40)), C([-1.5, 5, 2], [3, 3, 5], (240, 140, 40)), C([-1.5, 6, 7], [3, 3, 4], WHITE)],
      anim={'root': {'rotation': [0, "math.sin(q.life_time * 400) * 20", 0]}}, box=(0.5, 0.6))
model('laser', 'レーザーの発射台(レーザー回避)', [C([-4, 0, -4], [8, 6, 8], (60, 60, 70)), C([-2, 6, -2], [4, 3, 4], (255, 40, 40))])

# ===== 書き出し =====
def noise(c, k):
    return tuple(max(0, min(255, v + k)) for v in c)

def build_texture(name, m):
    # 箱ごとに box UV の場所を棚づめで割り当てる
    W = 128
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
        for px in range(u, u + 2 * d + 2 * w):
            for py in range(v, v + d + h):
                if py < v + d and not (u + d <= px < u + d + 2 * w): continue  # 上下の面の外は空き
                c = noise(col, rnd.randint(-10, 10))
                lx, ly = px - u, py - v
                if 'stripes' in f and ((lx // 3) % 2 == 0): c = noise(f['stripes'], rnd.randint(-8, 8))
                if 'rim' in f and py < v + d and (px in (u + d, u + d + w - 1) or py in (v, v + d - 1)): c = f['rim']
                if py >= v + d and (py == v + d + h - 1): c = noise(c, -25)  # 下のふちを少し暗く
                im.putpixel((px, py), c + (255,))
    os.makedirs(os.path.join(RP, 'textures', 'entity'), exist_ok=True)
    im.save(os.path.join(RP, 'textures', 'entity', f'mmgplus_{name}.png'))
    return im

def write(name, m):
    tex = build_texture(name, m)
    bones = []
    for b, piv in m['bones'].items():
        cubes = [{'origin': cb['origin'], 'size': cb['size'], 'uv': cb['uv'], **({'inflate': cb['inflate']} if cb['inflate'] else {})} for cb in m['cubes'] if cb['bone'] == b]
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

def preview(name, m, tex, size=320, yaw=-35, pitch=28):
    cy, sy, cp, sp = math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    def rot(p):
        x, y, z = p; x, z = x * cy - z * sy, x * sy + z * cy
        y, z = y * cp - z * sp, y * sp + z * cp
        return x, y, z
    pts = [rot(c) for cb in m['cubes'] for f, _ in faces_of(cb) for c in f]
    minx, maxx = min(p[0] for p in pts), max(p[0] for p in pts); miny, maxy = min(p[1] for p in pts), max(p[1] for p in pts)
    k = (size * 0.8) / max(maxx - minx, maxy - miny, 1)
    ox, oy = size / 2 - (minx + maxx) / 2 * k, size / 2 + (miny + maxy) / 2 * k
    proj = lambda p: (ox + p[0] * k, oy - p[1] * k)
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    faces = []
    for cb in m['cubes']:
        for corners, rect in faces_of(cb):
            r = [rot(c) for c in corners]
            # 裏向きの面は描かない
            (ax, ay, _), (bx, by, _), (cx, cy2, _) = r[0], r[1], r[2]
            if (bx - ax) * (cy2 - ay) - (by - ay) * (cx - ax) <= 0: continue
            cz = rot([cb['origin'][i] + cb['size'][i] / 2 for i in range(3)])[2]
            faces.append(((cz, sum(p[2] for p in r) / 4), [proj(p) for p in r], rect))
    shade = {0: 1.0}
    for depth, quad, (u0, v0, u1, v1) in sorted(faces, key=lambda f: (-f[0][0], -f[0][1])):
        if u1 <= u0 or v1 <= v0: continue
        src = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        try: coeff = homography(src, quad)
        except Exception: continue
        warped = tex.transform((size, size), Image.PERSPECTIVE, coeff, Image.NEAREST)
        mask = Image.new('L', (size, size), 0); ImageDraw.Draw(mask).polygon(quad, fill=255)
        img.paste(warped, (0, 0), Image.composite(warped.split()[3], mask, mask))
    os.makedirs(PREVIEW, exist_ok=True)
    img.save(os.path.join(PREVIEW, f'{name}.png'))

if __name__ == '__main__':
    for d in [os.path.join(RP, 'models', 'entity'), os.path.join(RP, 'animations'), os.path.join(RP, 'entity'), os.path.join(BP, 'entities')]: os.makedirs(d, exist_ok=True)
    for name, m in MODELS.items(): write(name, m)
    json.dump({n: m['desc'] for n, m in MODELS.items()}, open(os.path.join(PREVIEW, 'index.json'), 'w'), ensure_ascii=False, indent=1)
    print(len(MODELS), 'models')
