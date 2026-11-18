# ミニゲームのあとの集合で、プレイヤーの足もとに出す順位の文字(mmgplus:rankplate、1st〜8th)
#   python3 tools/mpl_rankplate.py → RP: 絵 8 枚・geo・動き・描き分け・client entity / BP: entity、見本 mpl/rankplate_preview.png
#   文字: 太い斜めの数字 + 小さい st/nd/rd/th。1位 金 / 2位 銀 / 3位 銅 / 4位〜 むらさき。こい縁 + 白いふち + 下に影(立体っぽく)
#   板: カメラの方(-z)を向いた縦の板(はば 1.7 × 高さ 0.85 ブロック)。出るときにポンと大きくなる
import os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp')
BP = os.path.join(ROOT, 'mpl', 'src', 'behavior_packs', 'mpl_bp')
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf'
W, H = 512, 256
COLS = {1: ((255, 246, 150), (255, 190, 30), (150, 80, 0)), 2: ((250, 252, 255), (180, 190, 210), (80, 90, 110)),
        3: ((255, 214, 170), (205, 120, 60), (110, 50, 20)), 4: ((240, 190, 255), (175, 90, 235), (80, 30, 120))}
SUF = {1: 'st', 2: 'nd', 3: 'rd'}

def plate(n):
    top, bot, dark = COLS[min(n, 4)]
    num, suf = str(n), SUF.get(n, 'th')
    fb, fs = ImageFont.truetype(FONT, 230), ImageFont.truetype(FONT, 120)
    wn = fb.getlength(num); ws = fs.getlength(suf); x0 = (W - (wn + ws + 6)) / 2
    def draw(d, fill, stroke, sw, dx=0, dy=0):
        d.text((x0 + dx, 222 + dy), num, font=fb, anchor='ls', fill=fill, stroke_width=sw, stroke_fill=stroke)
        d.text((x0 + wn + 6 + dx, 222 + dy), suf, font=fs, anchor='ls', fill=fill, stroke_width=sw, stroke_fill=stroke)
    im = Image.new('RGBA', (W, H))
    # 影(下・右へずらす)→ こい縁 → 白いふち → 中のグラデ
    sh = Image.new('RGBA', (W, H)); draw(ImageDraw.Draw(sh), (20, 10, 30, 160), (20, 10, 30, 160), 22, 6, 10); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))
    ol = Image.new('RGBA', (W, H)); draw(ImageDraw.Draw(ol), dark + (255,), dark + (255,), 20); im.alpha_composite(ol)
    wl = Image.new('RGBA', (W, H)); draw(ImageDraw.Draw(wl), (255, 255, 255, 255), (255, 255, 255, 255), 9); im.alpha_composite(wl)
    mk = Image.new('L', (W, H)); draw(ImageDraw.Draw(mk), 255, 255, 2)
    g = Image.new('RGBA', (W, H)); gd = ImageDraw.Draw(g)
    for y in range(H): t = max(0, min(1, (y - 40) / 170)); gd.line([(0, y), (W, y)], fill=tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,))
    im.paste(g, (0, 0), mk)
    hl = Image.new('L', (W, H)); draw(ImageDraw.Draw(hl), 255, 255, 0, -4, -6)   # 上のつや(少しずらした形との差)
    hl = ImageChops.subtract(mk, hl).point(lambda v: v // 2); im.paste(Image.new('RGBA', (W, H), (255, 255, 255, 255)), (0, 0), hl)
    return im

os.makedirs(os.path.join(RP, 'textures', 'entity', 'mpl_rank'), exist_ok=True)
prev = Image.new('RGBA', (4 * 260, 130), (40, 50, 90, 255))
for n in range(1, 9):
    im = plate(n); im.resize((256, 128), Image.LANCZOS).save(os.path.join(RP, 'textures', 'entity', 'mpl_rank', f'r{n}.png'))
    if n <= 4: prev.alpha_composite(im.resize((256, 128), Image.LANCZOS), ((n - 1) * 260, 1))
prev.save(os.path.join(ROOT, 'mpl', 'rankplate_preview.png'))
# 板(縦、-z 向き): はば 27px・高さ 13.5px
geo = {'format_version': '1.12.0', 'minecraft:geometry': [{'description': {'identifier': 'geometry.mpl.rankplate', 'texture_width': 256, 'texture_height': 128,
       'visible_bounds_width': 3, 'visible_bounds_height': 2, 'visible_bounds_offset': [0, 0.5, 0]},
       'bones': [{'name': 'p', 'pivot': [0, 0, 0], 'cubes': [{'origin': [-13.5, 0, 0], 'size': [27, 13.5, 0], 'uv': {'north': {'uv': [0, 0], 'uv_size': [256, 128]}}}]}]}]}
json.dump(geo, open(os.path.join(RP, 'models', 'entity', 'mpl_rankplate.geo.json'), 'w'), indent=1)
anim = {'format_version': '1.8.0', 'animations': {'animation.mpl.rankplate': {'loop': True, 'bones': {'p': {
    'scale': "q.life_time < 0.18 ? q.life_time / 0.18 * 1.25 : (q.life_time < 0.3 ? 1.25 - (q.life_time - 0.18) / 0.12 * 0.25 : 1.0 + math.sin(q.life_time * 200) * 0.03)",
    'position': [0, "math.sin(q.life_time * 120) * 0.4", 0]}}}}}
json.dump(anim, open(os.path.join(RP, 'animations', 'mpl_rankplate.animation.json'), 'w'), indent=1)
rc = {'format_version': '1.8.0', 'render_controllers': {'controller.render.mpl_rankplate': {
    'arrays': {'textures': {'Array.r': [f'Texture.r{n}' for n in range(1, 9)]}}, 'geometry': 'Geometry.default', 'materials': [{'*': 'Material.default'}],
    'textures': ["Array.r[math.max(0, q.property('mmgplus:rank') - 1)]"]}}}
json.dump(rc, open(os.path.join(RP, 'render_controllers', 'mpl_rankplate.render_controllers.json'), 'w'), indent=1)
ce = {'format_version': '1.10.0', 'minecraft:client_entity': {'description': {'identifier': 'mmgplus:rankplate', 'materials': {'default': 'entity_alphablend'},
      'textures': {f'r{n}': f'textures/entity/mpl_rank/r{n}' for n in range(1, 9)}, 'geometry': {'default': 'geometry.mpl.rankplate'},
      'render_controllers': ['controller.render.mpl_rankplate'], 'animations': {'a': 'animation.mpl.rankplate'}, 'scripts': {'animate': ['a']}}}}
json.dump(ce, open(os.path.join(RP, 'entity', 'mpl_rankplate.entity.json'), 'w'), indent=1)
be = {'format_version': '1.21.20', 'minecraft:entity': {'description': {'identifier': 'mmgplus:rankplate', 'is_spawnable': False, 'is_summonable': True,
      'properties': {'mmgplus:rank': {'type': 'int', 'range': [1, 8], 'default': 1, 'client_sync': True}}},
      'components': {'minecraft:collision_box': {'width': 0.1, 'height': 0.1}, 'minecraft:physics': {'has_gravity': False, 'has_collision': False},
                     'minecraft:damage_sensor': {'triggers': [{'cause': 'all', 'deals_damage': 'no'}]}, 'minecraft:pushable': {'is_pushable': False, 'is_pushable_by_piston': False},
                     'minecraft:type_family': {'family': ['mmgplus_prop', 'inanimate']}}}}
json.dump(be, open(os.path.join(BP, 'entities', 'mpl_rankplate.json'), 'w'), indent=1)
print('rankplate ok')
