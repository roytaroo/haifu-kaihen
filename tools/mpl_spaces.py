# マスの丸い台(mmgplus:space)。マスごとに 1 体置く。種類は mmgplus:kind(0〜10)で絵を切りかえる
#   python3 tools/mpl_spaces.py → RP: geo・絵・描き分け・client entity / BP: entity、見本 mpl/spaces_preview.png
#   台: 半径 20px(3x3 のマスより少し小さい)・厚み 2px(足がしずみすぎない)。上の面は丸い絵(ふち白 + 種類の色 + マーク)、横は種類のこい色
#   main.js の SPACE_KIND と順番を合わせる
import os, json, math
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp')
BP = os.path.join(ROOT, 'mpl', 'src', 'behavior_packs', 'mpl_bp')
FONT = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
KINDS = [  # 名前, 色, マーク
    ('blue', (70, 150, 255), 'plus'), ('red', (240, 70, 70), 'minus'), ('happen', (70, 200, 90), '?'), ('event', (255, 150, 40), '!'),
    ('lucky', (255, 205, 50), 'star'), ('shop', (180, 95, 235), 'bag'), ('skull', (70, 58, 86), 'skull'), ('bank', (40, 195, 205), 'coin'),
    ('shuffle', (255, 115, 195), 'shuffle'), ('mirror', (135, 75, 210), 'mirror'), ('start', (250, 250, 252), 'GO'),
    ('roulette', (255, 160, 40), 'roulette'), ('vs', (225, 45, 80), 'VS'),
]
R = 20; TH = 2; SEG = 32
N = 512; C = N / 2   # 上の面の絵は 512 で描いて 128 に
WHITE = (255, 255, 255, 255); OUT = (30, 24, 44, 255)

def shade(c, k): return tuple(max(0, min(255, round(v * k))) for v in c)
def top(col, mark):
    im = Image.new('RGBA', (N, N)); d = ImageDraw.Draw(im)
    d.ellipse((4, 4, N - 4, N - 4), fill=(255, 255, 255, 255))                         # 白いふち
    d.ellipse((30, 30, N - 30, N - 30), fill=shade(col, 0.62) + (255,))                # こい色の線
    # 中: 上が明るく下がこい(ふくらんで見える)
    g = Image.new('RGBA', (N, N)); gd = ImageDraw.Draw(g)
    for y in range(N): t = y / N; gd.line([(0, y), (N, y)], fill=shade(col, 1.18 - 0.36 * t) + (255,))
    mk = Image.new('L', (N, N)); ImageDraw.Draw(mk).ellipse((40, 40, N - 40, N - 40), fill=255); im.paste(g, (0, 0), mk)
    hl = Image.new('L', (N, N)); ImageDraw.Draw(hl).ellipse((90, 60, N - 150, 210), fill=60)   # 左上のつや
    im.paste(Image.new('RGBA', (N, N), (255, 255, 255, 255)), (0, 0), hl)
    ink = (30, 24, 44, 255) if mark == 'GO' else WHITE
    def outl(draw_fn):   # こい縁 → 白いマーク
        draw_fn(d, OUT, 14); draw_fn(d, ink if mark == 'GO' else WHITE, 0)
    if mark == 'plus':
        outl(lambda d, c, e: (d.rounded_rectangle((C - 34 - e, C - 120 - e, C + 34 + e, C + 120 + e), 26 + e, fill=c), d.rounded_rectangle((C - 120 - e, C - 34 - e, C + 120 + e, C + 34 + e), 26 + e, fill=c)))
    elif mark == 'minus':
        outl(lambda d, c, e: d.rounded_rectangle((C - 120 - e, C - 34 - e, C + 120 + e, C + 34 + e), 26 + e, fill=c))
    elif mark in ('?', '!', 'GO', 'VS'):
        f = ImageFont.truetype(FONT, 300 if mark not in ('GO', 'VS') else 210)
        d.text((C, C + 10), mark, font=f, anchor='mm', fill=(230, 40, 60, 255) if mark == 'GO' else WHITE, stroke_width=14, stroke_fill=OUT if mark != 'GO' else (255, 255, 255, 255))
    elif mark == 'star':
        pts = lambda r1, r2: [(C + math.cos(math.radians(-90 + i * 36)) * (r1 if i % 2 == 0 else r2), C + 14 + math.sin(math.radians(-90 + i * 36)) * (r1 if i % 2 == 0 else r2)) for i in range(10)]
        d.polygon(pts(160, 70), fill=OUT); d.polygon(pts(138, 58), fill=WHITE)
    elif mark == 'bag':
        outl(lambda d, c, e: (d.rounded_rectangle((C - 110 - e, C - 50 - e, C + 110 + e, C + 140 + e), 60 + e, fill=c), d.polygon([(C - 60 - e, C - 130 - e), (C + 60 + e, C - 130 - e), (C + 30 + e, C - 40), (C - 30 - e, C - 40)], fill=c)))
        d.rectangle((C - 50, C - 62, C + 50, C - 40), fill=shade(col, 0.7) + (255,))
    elif mark == 'skull':
        outl(lambda d, c, e: (d.ellipse((C - 120 - e, C - 140 - e, C + 120 + e, C + 80 + e), fill=c), d.rounded_rectangle((C - 70 - e, C + 30 - e, C + 70 + e, C + 140 + e), 20 + e, fill=c)))
        for x in (-50, 50): d.ellipse((C + x - 34, C - 50, C + x + 34, C + 20), fill=shade(col, 0.6) + (255,))
        d.polygon([(C, C + 30), (C - 18, C + 64), (C + 18, C + 64)], fill=shade(col, 0.6) + (255,))
        for x in (-35, 0, 35): d.rectangle((C + x - 5, C + 100, C + x + 5, C + 140), fill=shade(col, 0.6) + (255,))
    elif mark == 'coin':
        d.ellipse((C - 140, C - 140, C + 140, C + 140), fill=OUT); d.ellipse((C - 124, C - 124, C + 124, C + 124), fill=WHITE)
        d.ellipse((C - 90, C - 90, C + 90, C + 90), fill=shade(col, 0.85) + (255,)); d.rounded_rectangle((C - 22, C - 64, C + 22, C + 64), 18, fill=WHITE)
    elif mark == 'shuffle':   # 右向きの矢印(上)と左向きの矢印(下)
        def arrow(d, c, e, y, s):
            d.rounded_rectangle((C - 110 * s - e if s > 0 else C - 40 - e, y - 22 - e, C + 40 + e if s > 0 else C + 110 + e, y + 22 + e), 18 + e, fill=c)
            d.polygon([(C + 20 * s - e * s, y - 72 - e), (C + 140 * s + e * s, y), (C + 20 * s - e * s, y + 72 + e)], fill=c)
        for e, c in ((14, OUT), (0, WHITE)): arrow(d, c, e, C - 62, 1); arrow(d, c, e, C + 62, -1)
    elif mark == 'roulette':   # 6 つに分けた円 + まんなかのじく + 上の針
        d.ellipse((C - 150, C - 150, C + 150, C + 150), fill=OUT)
        for k in range(6): d.pieslice((C - 136, C - 136, C + 136, C + 136), k * 60 - 90, k * 60 - 30, fill=[WHITE, (255, 215, 80, 255)][k % 2])
        d.ellipse((C - 30, C - 30, C + 30, C + 30), fill=OUT); d.polygon([(C - 26, C - 176), (C + 26, C - 176), (C, C - 116)], fill=OUT); d.polygon([(C - 16, C - 168), (C + 16, C - 168), (C, C - 128)], fill=(230, 40, 60, 255))
    elif mark == 'mirror':
        d.ellipse((C - 100, C - 150, C + 100, C + 150), fill=OUT); d.ellipse((C - 86, C - 136, C + 86, C + 136), fill=(255, 210, 80, 255))
        d.ellipse((C - 64, C - 112, C + 64, C + 112), fill=(190, 230, 255, 255)); d.polygon([(C - 30, C - 80), (C + 10, C - 80), (C - 40, C + 20), (C - 60, C + 20)], fill=(255, 255, 255, 220))
    return im.resize((128, 128), Image.LANCZOS)

os.makedirs(os.path.join(RP, 'textures', 'entity', 'mpl_space'), exist_ok=True)
prev = Image.new('RGBA', (len(KINDS) * 132, 132), (90, 140, 80, 255))
for i, (name, col, mark) in enumerate(KINDS):
    tex = Image.new('RGBA', (144, 128)); t = top(col, mark); tex.paste(t, (0, 0))
    side = Image.new('RGBA', (16, 16), shade(col, 0.55) + (255,)); ImageDraw.Draw(side).rectangle((0, 0, 15, 3), fill=shade(col, 0.8) + (255,)); tex.paste(side, (128, 0))
    tex.save(os.path.join(RP, 'textures', 'entity', 'mpl_space', f'{name}.png'))
    prev.alpha_composite(t, (i * 132 + 2, 2))
prev.save(os.path.join(ROOT, 'mpl', 'spaces_preview.png'))
# 形: 上の丸(厚みなしの板、上の面だけ)+ 横の輪(32 枚の板を回して並べる)
cubes = [{'origin': [-R, TH, -R], 'size': [2 * R, 0, 2 * R], 'uv': {'up': {'uv': [0, 0], 'uv_size': [128, 128]}}}]
w = 2 * math.pi * R / SEG + 0.3
for k in range(SEG):
    cubes.append({'origin': [-w / 2, 0, -R], 'size': [w, TH, 0.6], 'pivot': [0, 0, 0], 'rotation': [0, k * 360 / SEG, 0],
                  'uv': {'north': {'uv': [128, 0], 'uv_size': [16, 16]}, 'up': {'uv': [128, 0], 'uv_size': [16, 4]}}})
geo = {'format_version': '1.12.0', 'minecraft:geometry': [{'description': {'identifier': 'geometry.mpl.space', 'texture_width': 144, 'texture_height': 128,
       'visible_bounds_width': 4, 'visible_bounds_height': 2, 'visible_bounds_offset': [0, 0.5, 0]}, 'bones': [{'name': 'root', 'pivot': [0, 0, 0], 'cubes': cubes}]}]}
json.dump(geo, open(os.path.join(RP, 'models', 'entity', 'mpl_space.geo.json'), 'w'), indent=1)
rc = {'format_version': '1.8.0', 'render_controllers': {'controller.render.mpl_space': {
    'arrays': {'textures': {'Array.k': [f'Texture.{n}' for n, *_ in KINDS]}}, 'geometry': 'Geometry.default', 'materials': [{'*': 'Material.default'}],
    'textures': ["Array.k[q.property('mmgplus:kind')]"]}}}
json.dump(rc, open(os.path.join(RP, 'render_controllers', 'mpl_space.render_controllers.json'), 'w'), indent=1)
ce = {'format_version': '1.10.0', 'minecraft:client_entity': {'description': {'identifier': 'mmgplus:space', 'materials': {'default': 'entity_alphatest'},
      'textures': {n: f'textures/entity/mpl_space/{n}' for n, *_ in KINDS}, 'geometry': {'default': 'geometry.mpl.space'}, 'render_controllers': ['controller.render.mpl_space']}}}
json.dump(ce, open(os.path.join(RP, 'entity', 'mpl_space.entity.json'), 'w'), indent=1)
be = {'format_version': '1.21.20', 'minecraft:entity': {'description': {'identifier': 'mmgplus:space', 'is_spawnable': False, 'is_summonable': True,
      'properties': {'mmgplus:kind': {'type': 'int', 'range': [0, len(KINDS) - 1], 'default': 0, 'client_sync': True}}},
      'components': {'minecraft:collision_box': {'width': 0.1, 'height': 0.1}, 'minecraft:physics': {'has_gravity': False, 'has_collision': False},
                     'minecraft:damage_sensor': {'triggers': [{'cause': 'all', 'deals_damage': 'no'}]}, 'minecraft:pushable': {'is_pushable': False, 'is_pushable_by_piston': False},
                     'minecraft:type_family': {'family': ['mmgplus_prop', 'inanimate']}}}}
json.dump(be, open(os.path.join(BP, 'entities', 'mpl_space.json'), 'w'), indent=1)
print('spaces', [n for n, *_ in KINDS])
