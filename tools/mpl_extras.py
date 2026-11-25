# v55 の追加の絵・モデル(アイデア50 で「やる」になったもの)
#   python3 tools/mpl_extras.py
#   1) 顔のアイコン(font/glyph_E4.png): 10 人のスキンの顔。0〜9 ふつう / 16〜25 今の番(金のわく)/ 15・31 スキンなし
#   2) 小さな地図のます(font/glyph_E5.png): 地形 5 種(海・砂・草・岩・道)x のせる物 7 種(なし・スター・人1〜4・2 人以上)
#   3) 頭の上のコインの数字(mmgplus:coinnum): 背景なし。符号 + 十の位 + 一の位(コインつき)。プロパティ n(0〜99)・neg(0/1)
#   4) 使うアイテム(mpl:use_<種類>): 持ち物に入れて、右クリックで使う。絵は glyph_E2 の絵を使う
#   5) 分かれ道の矢印(mmgplus:waysign): 地面の木の矢印 + 行き先の絵と名前。プロパティ way(0〜8)
#   6) 動くモデル: 灯台の光(beam)・風車の羽(windmill)・カモメ(gull)・気球(airballoon)・竜巻(tornado)・クジラ(whale)
import os, json, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp')
BP = os.path.join(ROOT, 'mpl', 'src', 'behavior_packs', 'mpl_bp')
FONT_EN = '/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf'
FONT_JP = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
SKINS = ['jack', 'oracle', 'shade', 'comet', 'widow', 'jester', 'byte', 'splash', 'humming', 'replica']   # main.js の SKINS と同じ順
for d in ('font', 'models/entity', 'animations', 'entity', 'render_controllers', 'textures/entity/mpl_x', 'textures/items'): os.makedirs(os.path.join(RP, d), exist_ok=True)
for d in ('entities', 'items'): os.makedirs(os.path.join(BP, d), exist_ok=True)
def jdump(o, *p): json.dump(o, open(os.path.join(*p), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

# ===== 1) 顔 =====
page = Image.new('RGBA', (256, 256))
def face_of(name):
    sk = Image.open(os.path.join(RP, 'textures', 'entity', 'mpl_bots', f'{name}.png')).convert('RGBA')
    f = sk.crop((8, 8, 16, 16)); f.alpha_composite(sk.crop((40, 8, 48, 16)))
    return f
def put_face(i, f, gold):
    c = Image.new('RGBA', (16, 16))
    d = ImageDraw.Draw(c)
    if gold: d.rectangle((0, 0, 15, 15), fill=(255, 200, 40, 255)); d.rectangle((1, 1, 14, 14), fill=(120, 60, 0, 255))
    else: d.rectangle((1, 1, 14, 14), fill=(20, 20, 35, 255))
    c.alpha_composite(f.resize((12, 12), Image.NEAREST), (2, 2))
    page.alpha_composite(c, ((i % 16) * 16, (i // 16) * 16))
for i, n in enumerate(SKINS):
    f = face_of(n); put_face(i, f, False); put_face(16 + i, f, True)
gen = Image.new('RGBA', (8, 8), (200, 150, 110, 255)); gd = ImageDraw.Draw(gen); gd.rectangle((0, 0, 7, 2), fill=(70, 45, 25, 255)); gd.point([(2, 4), (5, 4)], fill=(40, 40, 90, 255))
put_face(15, gen, False); put_face(31, gen, True)
page.save(os.path.join(RP, 'font', 'glyph_E4.png'))

# ===== 2) 地図のます(16px のますいっぱいに描く。文字の間のすき間が出ないよう、はしまで色をぬる)=====
TER = [(46, 110, 200), (232, 214, 150), (98, 168, 74), (92, 84, 88), (205, 190, 160)]   # 海・砂・草・岩・道
DOT = [None, (255, 214, 40), (235, 60, 60), (70, 120, 255), (70, 210, 90), (255, 235, 70), (255, 255, 255)]
page = Image.new('RGBA', (256, 256))
for t, tc in enumerate(TER):
    for o, oc in enumerate(DOT):
        c = Image.new('RGBA', (16, 16), tc + (255,)); d = ImageDraw.Draw(c)
        if o == 1:   # スター
            pts = [(8 + math.cos(math.radians(-90 + k * 36)) * (7 if k % 2 == 0 else 3), 8.5 + math.sin(math.radians(-90 + k * 36)) * (7 if k % 2 == 0 else 3)) for k in range(10)]
            d.polygon(pts, fill=oc + (255,), outline=(120, 70, 0, 255))
        elif oc:
            d.ellipse((2, 2, 13, 13), fill=(20, 20, 30, 255)); d.ellipse((4, 4, 11, 11), fill=oc + (255,))
        i = t * 8 + o
        page.alpha_composite(c, ((i % 16) * 16, (i // 16) * 16))
page.save(os.path.join(RP, 'font', 'glyph_E5.png'))

# ===== 3) コインの数字 =====
fb = ImageFont.truetype(FONT_EN, 110)
def digit_tex(ch, gold, coin=False):
    W, H = (128 if coin else 64), 128
    im = Image.new('RGBA', (W, H)); top, bot, dark = ((255, 246, 150), (255, 170, 20), (110, 50, 0)) if gold else ((255, 190, 180), (230, 40, 40), (90, 0, 0))
    def draw(d, fill, sw, dx=0, dy=0): d.text((32 + dx, 108 + dy), ch, font=fb, anchor='ms', fill=fill, stroke_width=sw, stroke_fill=fill)
    sh = Image.new('RGBA', (W, H)); draw(ImageDraw.Draw(sh), (20, 10, 30, 150), 12, 3, 5); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2)))
    ol = Image.new('RGBA', (W, H)); draw(ImageDraw.Draw(ol), dark + (255,), 11); im.alpha_composite(ol)
    wl = Image.new('RGBA', (W, H)); draw(ImageDraw.Draw(wl), (255, 255, 255, 255), 5); im.alpha_composite(wl)
    mk = Image.new('L', (W, H)); draw(ImageDraw.Draw(mk), 255, 0)
    g = Image.new('RGBA', (W, H)); gd = ImageDraw.Draw(g)
    for y in range(H): t = max(0, min(1, (y - 30) / 80)); gd.line([(0, y), (W, y)], fill=tuple(round(top[k] + (bot[k] - top[k]) * t) for k in range(3)) + (255,))
    im.paste(g, (0, 0), mk)
    if coin:   # 右にコイン
        cx, cy, r = 96, 70, 24
        d = ImageDraw.Draw(im); d.ellipse((cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4), fill=(90, 45, 0, 255)); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 200, 40, 255))
        d.ellipse((cx - r + 7, cy - r + 7, cx + r - 7, cy + r - 7), outline=(200, 120, 0, 255), width=4); d.rectangle((cx - 3, cy - 12, cx + 3, cy + 12), fill=(200, 120, 0, 255))
    return im
X = os.path.join(RP, 'textures', 'entity', 'mpl_x')
for k in range(10):
    digit_tex(str(k), True).save(os.path.join(X, f'dg{k}.png')); digit_tex(str(k), False).save(os.path.join(X, f'dr{k}.png'))
    digit_tex(str(k), True, True).save(os.path.join(X, f'cg{k}.png')); digit_tex(str(k), False, True).save(os.path.join(X, f'cr{k}.png'))
digit_tex('+', True).save(os.path.join(X, 'plus.png')); digit_tex('-', False).save(os.path.join(X, 'minus.png'))
def quad(name, ox, w, h=8, tw=64, th=128):
    return {'format_version': '1.12.0', 'minecraft:geometry': [{'description': {'identifier': f'geometry.mpl.{name}', 'texture_width': tw, 'texture_height': th,
            'visible_bounds_width': 3, 'visible_bounds_height': 3, 'visible_bounds_offset': [0, 1, 0]},
            'bones': [{'name': name, 'pivot': [0, 0, 0], 'cubes': [{'origin': [ox, 0, 0], 'size': [w, h * 2, 0], 'uv': {'north': {'uv': [0, 0], 'uv_size': [tw, th]}}}]}]}]}
jdump(quad('cn_s', -10, 4), RP, 'models', 'entity', 'mpl_cn_s.geo.json')
jdump(quad('cn_t', -6, 4), RP, 'models', 'entity', 'mpl_cn_t.geo.json')
jdump(quad('cn_o', -2, 8, tw=128), RP, 'models', 'entity', 'mpl_cn_o.geo.json')
N, NEG = "q.property('mmgplus:n')", "q.property('mmgplus:neg')"
rc = {'format_version': '1.8.0', 'render_controllers': {
    'controller.render.mpl_cn_s': {'arrays': {'textures': {'Array.s': ['Texture.plus', 'Texture.minus']}}, 'geometry': 'Geometry.s', 'materials': [{'*': 'Material.default'}], 'textures': [f'Array.s[{NEG}]']},
    'controller.render.mpl_cn_t': {'arrays': {'textures': {'Array.t': [f'Texture.dg{k}' for k in range(10)] + [f'Texture.dr{k}' for k in range(10)]}}, 'geometry': 'Geometry.t', 'materials': [{'*': 'Material.default'}],
                                   'textures': [f'Array.t[math.floor({N} / 10) + {NEG} * 10]'], 'part_visibility': [{'*': f'{N} >= 10'}]},
    'controller.render.mpl_cn_o': {'arrays': {'textures': {'Array.o': [f'Texture.cg{k}' for k in range(10)] + [f'Texture.cr{k}' for k in range(10)]}}, 'geometry': 'Geometry.o', 'materials': [{'*': 'Material.default'}],
                                   'textures': [f'Array.o[math.mod({N}, 10) + {NEG} * 10]']}}}
jdump(rc, RP, 'render_controllers', 'mpl_coinnum.render_controllers.json')
# 出るときにポンと大きくなり、ゆっくり上へ。1 けたのときは符号を右へ寄せる
POP = "(q.life_time < 0.15 ? q.life_time / 0.15 * 1.3 : (q.life_time < 0.28 ? 1.3 - (q.life_time - 0.15) / 0.13 * 0.3 : 1.0))"
anim = {'format_version': '1.8.0', 'animations': {'animation.mpl.coinnum': {'loop': True, 'bones': {
    'cn_s': {'position': [f"{N} < 10 ? 4 : 0", "q.life_time * 6", 0], 'scale': POP},
    'cn_t': {'position': [0, "q.life_time * 6", 0], 'scale': POP}, 'cn_o': {'position': [0, "q.life_time * 6", 0], 'scale': POP}}}}}
jdump(anim, RP, 'animations', 'mpl_coinnum.animation.json')
tex = {'plus': 'textures/entity/mpl_x/plus', 'minus': 'textures/entity/mpl_x/minus'}
for k in range(10):
    for p in ('dg', 'dr', 'cg', 'cr'): tex[f'{p}{k}'] = f'textures/entity/mpl_x/{p}{k}'
jdump({'format_version': '1.10.0', 'minecraft:client_entity': {'description': {'identifier': 'mmgplus:coinnum', 'materials': {'default': 'entity_alphablend'}, 'textures': tex,
       'geometry': {'s': 'geometry.mpl.cn_s', 't': 'geometry.mpl.cn_t', 'o': 'geometry.mpl.cn_o'},
       'render_controllers': ['controller.render.mpl_cn_s', 'controller.render.mpl_cn_t', 'controller.render.mpl_cn_o'], 'animations': {'a': 'animation.mpl.coinnum'}, 'scripts': {'animate': ['a']}}}},
      RP, 'entity', 'mpl_coinnum.entity.json')
def be(ident, props=None, extra=None):
    d = {'identifier': ident, 'is_spawnable': False, 'is_summonable': True}
    if props: d['properties'] = props
    comp = {'minecraft:collision_box': {'width': 0.1, 'height': 0.1}, 'minecraft:physics': {'has_gravity': False, 'has_collision': False},
            'minecraft:damage_sensor': {'triggers': [{'cause': 'all', 'deals_damage': 'no'}]}, 'minecraft:pushable': {'is_pushable': False, 'is_pushable_by_piston': False},
            'minecraft:type_family': {'family': ['mmgplus_prop', 'inanimate']}}
    comp.update(extra or {})
    return {'format_version': '1.21.20', 'minecraft:entity': {'description': d, 'components': comp}}
jdump(be('mmgplus:coinnum', {'mmgplus:n': {'type': 'int', 'range': [0, 99], 'default': 0, 'client_sync': True}, 'mmgplus:neg': {'type': 'int', 'range': [0, 1], 'default': 0, 'client_sync': True}}),
      BP, 'entities', 'mpl_coinnum.json')

# ===== 4) 使うアイテム =====
KINDS = ['double', 'triple', 'pipe', 'gold', 'glove', 'fix', 'slow', 'magnet', 'ticket', 'bag', 'reverse']
NAMES = {'double': 'ダブルサイコロ', 'triple': 'トリプルサイコロ', 'pipe': 'ワープパイプ', 'gold': '金のパイプ', 'glove': 'どろぼう手袋', 'fix': '八百長ダイス', 'slow': 'スローダイス',
         'magnet': 'コイン磁石', 'ticket': 'ミニゲーム券', 'bag': 'ぶんどり袋', 'reverse': '逆さサイコロ'}
e2 = Image.open(os.path.join(RP, 'font', 'glyph_E2.png')).convert('RGBA')
it = json.load(open(os.path.join(RP, 'textures', 'item_texture.json'), encoding='utf-8'))
for i, k in enumerate(KINDS):
    cell = e2.crop(((i % 16) * 16, (i // 16) * 16, (i % 16) * 16 + 16, (i // 16) * 16 + 16))
    cell.save(os.path.join(RP, 'textures', 'items', f'mpl_use_{k}.png'))
    it['texture_data'][f'mpl_use_{k}'] = {'textures': f'textures/items/mpl_use_{k}'}
    jdump({'format_version': '1.20.50', 'minecraft:item': {'description': {'identifier': f'mpl:use_{k}', 'menu_category': {'category': 'none'}},
           'components': {'minecraft:max_stack_size': 1, 'minecraft:icon': {'texture': f'mpl_use_{k}'}, 'minecraft:display_name': {'value': f'§e{NAMES[k]}'},
                          'minecraft:hand_equipped': False}}}, BP, 'items', f'use_{k}.json')
jdump(it, RP, 'textures', 'item_texture.json')

# ===== 5) 分かれ道の矢印(地面に置く木の矢印 + 行き先の絵 + 名前)=====
WAYS = ['浜辺を進む', '船に乗る', '沖の桟橋', 'ドローブリッジ', 'ふもとの道', '火山にのぼる', '神殿の近道', '森の道', '木の上の道']   # mpl_board.py の way と同じ順(頭の文字でさがす)
WICON = ['sand', 'ship', 'pier', 'bridge', 'foot', 'volcano', 'temple', 'forest', 'tree']
fj = ImageFont.truetype(FONT_JP, 30)
def way_icon(d, kind, cx, cy):
    if kind == 'volcano': d.polygon([(cx - 22, cy + 16), (cx - 6, cy - 14), (cx + 6, cy - 14), (cx + 22, cy + 16)], fill=(90, 70, 70)); d.polygon([(cx - 6, cy - 14), (cx + 6, cy - 14), (cx + 2, cy - 4), (cx - 3, cy - 6)], fill=(255, 110, 30))
    elif kind == 'ship': d.polygon([(cx - 22, cy + 6), (cx + 22, cy + 6), (cx + 14, cy + 16), (cx - 14, cy + 16)], fill=(110, 70, 40)); d.line([(cx, cy + 6), (cx, cy - 18)], fill=(90, 60, 30), width=3); d.polygon([(cx + 2, cy - 16), (cx + 16, cy + 2), (cx + 2, cy + 2)], fill=(250, 250, 250))
    elif kind == 'forest': [d.polygon([(x - 10, cy + 14), (x, cy - 16), (x + 10, cy + 14)], fill=(50, 130, 60)) for x in (cx - 9, cx + 9)]
    elif kind == 'tree': d.rectangle((cx - 3, cy, cx + 3, cy + 16), fill=(110, 75, 40)); d.ellipse((cx - 16, cy - 18, cx + 16, cy + 6), fill=(70, 160, 70)); d.rectangle((cx - 8, cy - 6, cx + 8, cy + 2), fill=(150, 100, 55))
    elif kind == 'temple': d.polygon([(cx - 20, cy - 6), (cx, cy - 18), (cx + 20, cy - 6)], fill=(240, 240, 235)); [d.rectangle((x - 2, cy - 6, x + 2, cy + 12), fill=(240, 240, 235)) for x in (cx - 14, cx - 5, cx + 5, cx + 14)]; d.rectangle((cx - 20, cy + 12, cx + 20, cy + 16), fill=(220, 200, 120))
    elif kind == 'bridge': d.arc((cx - 22, cy - 10, cx + 22, cy + 30), 180, 360, fill=(120, 80, 45), width=6); d.rectangle((cx - 24, cy - 16, cx - 18, cy + 16), fill=(140, 140, 145)); d.rectangle((cx + 18, cy - 16, cx + 24, cy + 16), fill=(140, 140, 145))
    elif kind == 'pier': d.rectangle((cx - 22, cy - 4, cx + 22, cy + 3), fill=(150, 105, 60)); [d.rectangle((x - 2, cy + 3, x + 2, cy + 16), fill=(100, 70, 40)) for x in (cx - 16, cx, cx + 16)]; d.arc((cx - 24, cy + 8, cx + 24, cy + 22), 200, 340, fill=(70, 140, 230), width=3)
    elif kind == 'foot': d.polygon([(cx - 22, cy + 16), (cx - 2, cy - 12), (cx + 22, cy + 16)], fill=(120, 150, 90)); d.line([(cx - 18, cy + 14), (cx + 18, cy + 14)], fill=(210, 190, 150), width=4)
    else: d.ellipse((cx - 20, cy - 8, cx + 20, cy + 18), fill=(235, 215, 150)); d.arc((cx - 22, cy - 16, cx + 22, cy + 10), 200, 340, fill=(70, 140, 230), width=4)
for i, (w, k) in enumerate(zip(WAYS, WICON)):
    S = 2; im = Image.new('RGBA', (128 * S, 256 * S)); d = ImageDraw.Draw(im)
    # 矢印(上むき): 木の板。こいふち → 板 → 木目
    arrow = [(64, 6), (122, 70), (88, 70), (88, 250), (40, 250), (40, 70), (6, 70)]
    A = [(x * S, y * S) for x, y in arrow]
    d.polygon(A, fill=(70, 40, 15, 255))
    inner = [(64, 16), (108, 64), (82, 64), (82, 244), (46, 244), (46, 64), (20, 64)]
    d.polygon([(x * S, y * S) for x, y in inner], fill=(190, 135, 75, 255))
    for y in range(90, 244, 14): d.line([(48 * S, y * S), (80 * S, y * S)], fill=(160, 110, 60, 255), width=S)
    im = im.resize((128, 256), Image.LANCZOS); d = ImageDraw.Draw(im)
    d.ellipse((34, 70, 94, 130), fill=(255, 250, 235, 255), outline=(70, 40, 15, 255), width=3); way_icon(d, k, 64, 100)
    # 名前(たて書き)
    txt = {'ドローブリッジ': 'はね橋をわたる', '火山にのぼる': '火山へのぼる'}.get(w, w)[:7]
    for j, ch in enumerate(txt):
        y = 136 + j * 15
        d.text((64, y), ch, font=ImageFont.truetype(FONT_JP, 15), anchor='mt', fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(60, 30, 10, 255))
    im.save(os.path.join(X, f'way{i}.png'))
geo = {'format_version': '1.12.0', 'minecraft:geometry': [{'description': {'identifier': 'geometry.mpl.waysign', 'texture_width': 128, 'texture_height': 256,
       'visible_bounds_width': 5, 'visible_bounds_height': 2, 'visible_bounds_offset': [0, 0.5, 0]},
       'bones': [{'name': 'w', 'pivot': [0, 0, 0], 'cubes': [{'origin': [-12, 0.15, -24], 'size': [24, 0, 48], 'uv': {'up': {'uv': [0, 0], 'uv_size': [128, 256]}}}]}]}]}
jdump(geo, RP, 'models', 'entity', 'mpl_waysign.geo.json')
jdump({'format_version': '1.8.0', 'animations': {'animation.mpl.waysign': {'loop': True, 'bones': {'w': {'position': [0, "math.sin(q.life_time * 180) * 0.4 + 0.4", "math.sin(q.life_time * 240) * 1.2"]}}}}},
      RP, 'animations', 'mpl_waysign.animation.json')
jdump({'format_version': '1.8.0', 'render_controllers': {'controller.render.mpl_waysign': {'arrays': {'textures': {'Array.w': [f'Texture.w{i}' for i in range(len(WAYS))]}},
       'geometry': 'Geometry.default', 'materials': [{'*': 'Material.default'}], 'textures': ["Array.w[q.property('mmgplus:way')]"]}}}, RP, 'render_controllers', 'mpl_waysign.render_controllers.json')
jdump({'format_version': '1.10.0', 'minecraft:client_entity': {'description': {'identifier': 'mmgplus:waysign', 'materials': {'default': 'entity_alphatest'},
       'textures': {f'w{i}': f'textures/entity/mpl_x/way{i}' for i in range(len(WAYS))}, 'geometry': {'default': 'geometry.mpl.waysign'},
       'render_controllers': ['controller.render.mpl_waysign'], 'animations': {'a': 'animation.mpl.waysign'}, 'scripts': {'animate': ['a']}}}}, RP, 'entity', 'mpl_waysign.entity.json')
jdump(be('mmgplus:waysign', {'mmgplus:way': {'type': 'int', 'range': [0, len(WAYS) - 1], 'default': 0, 'client_sync': True}}, {'minecraft:persistent': {}}), BP, 'entities', 'mpl_waysign.json')

# ===== 6) 動くモデル(色のパレット 16x16 の 1 ますを面ごとに使う)=====
PAL = {'white': (245, 245, 245, 255), 'grey': (150, 155, 165, 255), 'dark': (40, 42, 50, 255), 'orange': (255, 150, 40, 255), 'yellow': (255, 230, 90, 255),
       'wood': (140, 95, 55, 255), 'wood2': (100, 65, 35, 255), 'red': (220, 50, 60, 255), 'pink': (255, 120, 180, 255), 'gold': (255, 200, 40, 255),
       'sail': (240, 235, 220, 255), 'blue': (45, 70, 130, 255), 'belly': (200, 210, 225, 255), 'beam': (255, 245, 170, 120), 'wind': (210, 220, 230, 140), 'wind2': (170, 180, 195, 170),
       'purple': (150, 80, 220, 255), 'sky': (110, 190, 255, 255), 'black': (15, 15, 20, 255)}
PK = list(PAL)
pal = Image.new('RGBA', (16, 16))
for i, k in enumerate(PK): pal.putpixel((i % 16, i // 16), PAL[k])
pal.save(os.path.join(X, 'pal.png'))
def C(origin, size, col, pivot=None, rot=None, infl=0):
    i = PK.index(col); uv = {f: {'uv': [i % 16, i // 16], 'uv_size': [1, 1]} for f in ('north', 'south', 'east', 'west', 'up', 'down')}
    c = {'origin': origin, 'size': size, 'uv': uv}
    if pivot: c['pivot'] = pivot
    if rot: c['rotation'] = rot
    if infl: c['inflate'] = infl
    return c
def model(name, bones, vb=(8, 8, 0)):
    jdump({'format_version': '1.12.0', 'minecraft:geometry': [{'description': {'identifier': f'geometry.mpl.{name}', 'texture_width': 16, 'texture_height': 16,
           'visible_bounds_width': vb[0], 'visible_bounds_height': vb[1], 'visible_bounds_offset': [0, vb[2], 0]}, 'bones': bones}]}, RP, 'models', 'entity', f'mpl_{name}.geo.json')
def client(ident, name, anims, mat='entity_alphatest', scripts=None):
    s = {'animate': list(anims)}
    if scripts: s['pre_animation'] = scripts
    jdump({'format_version': '1.10.0', 'minecraft:client_entity': {'description': {'identifier': ident, 'materials': {'default': mat}, 'textures': {'default': 'textures/entity/mpl_x/pal'},
           'geometry': {'default': f'geometry.mpl.{name}'}, 'render_controllers': ['controller.render.default'], 'animations': {k: v for k, v in anims.items()}, 'scripts': s}}},
          RP, 'entity', f'mpl_{name}.entity.json')
def anim(name, bones, loop=True):
    jdump({'format_version': '1.8.0', 'animations': {f'animation.mpl.{name}': {'loop': loop, 'bones': bones}}}, RP, 'animations', f'mpl_{name}.animation.json')

# 灯台の光: 中心から両がわへのびる光の板(長さ 26 ブロック)。4 秒で 1 回転
beam = [C([0, -6, -2], [416, 12, 4], 'beam'), C([-416, -6, -2], [416, 12, 4], 'beam'), C([0, -10, -1], [300, 20, 2], 'beam', infl=0), C([-300, -10, -1], [300, 20, 2], 'beam')]
model('beam', [{'name': 'b', 'pivot': [0, 0, 0], 'cubes': beam}], (60, 6, 0))
anim('beam', {'b': {'rotation': [0, "q.life_time * 90", 0]}})
client('mmgplus:beam', 'beam', {'a': 'animation.mpl.beam'}, 'entity_alphablend')
# 風車の羽: 4 本の腕(木の軸 + 白い帆 + 木のふち)。z 軸のまわりにゆっくり回る
arms = [C([-2, -2, -3], [4, 4, 6], 'wood2')]
for a in range(4):
    arms += [C([-1, 2, -1], [2, 108, 2], 'wood', [0, 0, 0], [0, 0, a * 90]), C([1, 28, -0.5], [22, 80, 1], 'sail', [0, 0, 0], [0, 0, a * 90]),
             C([22, 28, -1], [2, 80, 2], 'wood', [0, 0, 0], [0, 0, a * 90])]
model('windmill', [{'name': 'r', 'pivot': [0, 0, 0], 'cubes': arms}], (16, 16, 0))
anim('windmill', {'r': {'rotation': [0, 0, "q.life_time * 40"]}})
client('mmgplus:windmill', 'windmill', {'a': 'animation.mpl.windmill'})
# カモメ: 体・頭・くちばし・羽(はばたく)。半径 12 ブロックの輪をまわる(entity の場所が輪のまんなか)
gull_body = [C([-2, 0, -5], [4, 4, 9], 'white'), C([-2, 2, -8], [4, 4, 4], 'white'), C([-0.5, 2.5, -10.5], [1, 1.5, 3], 'orange'), C([-1.5, 0.5, 4], [3, 2, 3], 'grey'),
             C([-2.2, 4, -7], [0.4, 1, 1], 'black'), C([1.8, 4, -7], [0.4, 1, 1], 'black')]
gull = [{'name': 'root', 'pivot': [0, 0, 0]}, {'name': 'body', 'parent': 'root', 'pivot': [0, 2, 0], 'cubes': gull_body},
        {'name': 'wl', 'parent': 'body', 'pivot': [-2, 3, 0], 'cubes': [C([-14, 3, -3], [12, 1, 6], 'white'), C([-20, 3, -2], [6, 1, 4], 'grey')]},
        {'name': 'wr', 'parent': 'body', 'pivot': [2, 3, 0], 'cubes': [C([2, 3, -3], [12, 1, 6], 'white'), C([14, 3, -2], [6, 1, 4], 'grey')]}]
model('gull', gull, (30, 10, 0))
R = 192
anim('gull', {'root': {'position': [f"math.cos(q.life_time * v.sp + v.ph) * {R}", "math.sin(q.life_time * 50 + v.ph) * 10", f"math.sin(q.life_time * v.sp + v.ph) * {R}"],
                       'rotation': [0, "-(q.life_time * v.sp + v.ph)", "-12"]},
              'wl': {'rotation': [0, 0, "math.sin(q.life_time * 500) * 30"]}, 'wr': {'rotation': [0, 0, "-math.sin(q.life_time * 500) * 30"]}})
client('mmgplus:gull', 'gull', {'a': 'animation.mpl.gull'}, scripts=["v.ph = math.mod(math.abs(q.position(0) * 13 + q.position(2) * 7), 360);", "v.sp = 18 + math.mod(math.abs(q.position(0)), 8);"])
# 気球: しまもようの丸い球(段ごとに太さを変える)+ ロープ + かご + DJ の旗
env = []
cols = ['pink', 'white', 'gold', 'white']
for k in range(12):
    y = 40 + k * 6; t = (k - 5.5) / 6.2; r = round(math.sqrt(max(0.05, 1 - t * t)) * 30)
    for s in range(4):
        a = s * 22.5
        env.append(C([-r, y, -r * 0.42], [2 * r, 6, r * 0.84], cols[(k // 2 + s) % 4] if s % 2 == 0 else cols[(k // 2 + s + 1) % 4], [0, y, 0], [0, a, 0]))
env += [C([-10, 0, -10], [20, 12, 20], 'wood'), C([-11, 11, -11], [22, 2, 22], 'wood2')]
for (x, z) in ((-9, -9), (9, -9), (-9, 9), (9, 9)): env.append(C([x - 0.5, 12, z - 0.5], [1, 30, 1], 'wood2'))
env += [C([-1, -26, 0], [2, 26, 0.5], 'dark'), C([-12, -24, -0.5], [24, 14, 1], 'pink'), C([-10, -22, -0.7], [20, 3, 0.2], 'white')]
model('airballoon', [{'name': 'b', 'pivot': [0, 0, 0], 'cubes': env}], (10, 10, 2))
anim('airballoon', {'b': {'position': [0, "math.sin(q.life_time * 40) * 6", 0], 'rotation': [0, "q.life_time * 6", "math.sin(q.life_time * 30) * 2"]}})
client('mmgplus:airballoon', 'airballoon', {'a': 'animation.mpl.airballoon'})
# 竜巻: 下から上へ広がる輪(半とうめい)。段ごとに少しずれて、全体が回る
tw = []
for k in range(14):
    r = 6 + k * 3.2; y = k * 10
    tw.append({'name': f't{k}', 'parent': 'root', 'pivot': [0, y, 0], 'cubes': [C([-r, y, -r], [2 * r, 9, 2 * r], 'wind' if k % 2 else 'wind2')]})
model('tornado', [{'name': 'root', 'pivot': [0, 0, 0]}] + tw, (12, 12, 4))
anim('tornado', dict({'root': {'rotation': [0, "q.life_time * 720", 0]}}, **{f't{k}': {'position': [f"math.sin(q.life_time * 300 + {k * 40}) * {1 + k * 0.5}", 0, f"math.cos(q.life_time * 300 + {k * 40}) * {1 + k * 0.5}"],
                                                                                         'rotation': [0, f"q.life_time * {200 + k * 30}", 0]} for k in range(14)}))
client('mmgplus:tornado', 'tornado', {'a': 'animation.mpl.tornado'}, 'entity_alphablend')
# クジラ: 青い体(白いおなか)・ひれ・尾びれ(上下にふる)・目
whale = [{'name': 'body', 'pivot': [0, 0, 0], 'cubes': [C([-20, 0, -48], [40, 26, 80], 'blue'), C([-18, -2, -46], [36, 4, 70], 'belly'), C([-16, 4, -60], [32, 20, 12], 'blue'),
          C([-14, 2, -62], [28, 6, 4], 'belly'), C([-21, 18, -50], [1, 3, 3], 'black'), C([20, 18, -50], [1, 3, 3], 'black'),
          C([-36, 4, -20], [16, 3, 18], 'blue', [-20, 6, -12], [0, 0, -20]), C([20, 4, -20], [16, 3, 18], 'blue', [20, 6, -12], [0, 0, 20])]},
         {'name': 'tail', 'parent': 'body', 'pivot': [0, 12, 32], 'cubes': [C([-12, 6, 32], [24, 16, 26], 'blue'), C([-30, 12, 54], [60, 3, 16], 'blue')]}]
model('whale', whale, (12, 6, 1))
anim('whale', {'tail': {'rotation': ["math.sin(q.life_time * 120) * 18", 0, 0]}, 'body': {'rotation': ["math.sin(q.life_time * 60) * 3", 0, 0]}})
client('mmgplus:whale', 'whale', {'a': 'animation.mpl.whale'})
for n in ('beam', 'windmill', 'gull', 'airballoon', 'tornado', 'whale'):
    jdump(be(f'mmgplus:{n}', extra={'minecraft:persistent': {}} if n in ('beam', 'windmill', 'gull') else None), BP, 'entities', f'mpl_{n}.json')
print('extras ok')
