# 岸に寄せては返す波(mmgplus:wave)。海岸ぞいに 7 ブロックおきに置く(場所は mpl_board.py の WAVES)
#   python3 tools/mpl_waves.py → RP: geo・絵・動き・client entity / BP: entity、見本 mpl/wave_preview.png
#   形: 横 8 ブロックの平らな板 2 枚(前のふちの白い泡 + うしろの半とうめいの泡のあみ)。半とうめいで描く(entity_alphablend)
#   動き(5秒で1回): 沖から岸へ寄せる(はやく)→ ゆっくり引く(泡がうすくのびる)。高さは水面(0.89)→ 砂の上(1.03)
#   波ごとに始まりをずらす(v.ph = 場所から決める)
import os, json, math, random
from PIL import Image, ImageDraw, ImageFilter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp')
BP = os.path.join(ROOT, 'mpl', 'src', 'behavior_packs', 'mpl_bp')
random.seed(7)
W, CH, FH = 512, 32, 64      # 絵: はば 512、泡のふち 32、泡のあみ 64(どちらも 128px = 8 ブロックにのばす)

def crest():
    im = Image.new('RGBA', (W, CH)); d = ImageDraw.Draw(im)
    for x in range(0, W, 2):   # ふちの形(なみうつ)
        y0 = 10 + math.sin(x / 37) * 3 + math.sin(x / 11) * 1.5
        d.line([(x, y0), (x, CH - 4)], fill=(255, 255, 255, 235), width=2)
    for _ in range(260):       # 泡のつぶ
        x, y, r = random.uniform(0, W), random.uniform(6, CH - 2), random.uniform(1, 3.2)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 255))
    im = im.filter(ImageFilter.GaussianBlur(0.8))
    a = im.getchannel('A').point(lambda v: min(255, int(v * 1.1)))
    g = Image.new('L', (W, CH))
    for y in range(CH): ImageDraw.Draw(g).line([(0, y), (W, y)], fill=int(255 * min(1, (CH - y) / 8)))   # うしろのはしはうすく
    im.putalpha(Image.composite(a, Image.new('L', a.size, 0), g))
    return im

def foam():
    im = Image.new('RGBA', (W, FH)); d = ImageDraw.Draw(im)
    for _ in range(900):       # 泡のあみ(小さな輪)
        x, y = random.uniform(0, W), random.uniform(0, FH) ** 1.25 / FH ** 0.25
        r = random.uniform(1.5, 4.5)
        d.ellipse((x - r, y - r, x + r, y + r), outline=(235, 250, 255, 255), width=1)
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    a = im.getchannel('A'); fade = Image.new('L', (W, FH))
    for y in range(FH): ImageDraw.Draw(fade).line([(0, y), (W, y)], fill=int(170 * (1 - y / FH) ** 1.4))
    im.putalpha(Image.composite(a, Image.new('L', a.size, 0), fade))
    film = Image.new('RGBA', (W, FH))
    for y in range(FH): ImageDraw.Draw(film).line([(0, y), (W, y)], fill=(200, 235, 255, int(55 * (1 - y / FH))))   # うすい水の膜
    return Image.alpha_composite(film, im)

tex = Image.new('RGBA', (W, CH + FH)); tex.paste(crest(), (0, 0)); tex.alpha_composite(foam(), (0, CH))
tex = tex.resize((256, (CH + FH) // 2), Image.LANCZOS)   # 256 x 48
os.makedirs(os.path.join(RP, 'textures', 'entity'), exist_ok=True)
tex.save(os.path.join(RP, 'textures', 'entity', 'mpl_wave.png'))
prev = Image.new('RGBA', (512, 96), (40, 110, 170, 255)); prev.alpha_composite(tex.resize((512, 96)))
prev.save(os.path.join(ROOT, 'mpl', 'wave_preview.png'))

# 形: 前のふち(z -8〜-4)とうしろの泡(z -4〜+8)。どちらも上の面だけ
geo = {'format_version': '1.12.0', 'minecraft:geometry': [{'description': {'identifier': 'geometry.mpl.wave', 'texture_width': 256, 'texture_height': 48,
       'visible_bounds_width': 12, 'visible_bounds_height': 3, 'visible_bounds_offset': [0, 1, 0]},
       'bones': [{'name': 'w', 'pivot': [0, 0, -8], 'cubes': [
           {'origin': [-64, 0.02, -8], 'size': [128, 0, 4], 'uv': {'up': {'uv': [0, 0], 'uv_size': [256, 16]}}},
           {'origin': [-64, 0.0, -4], 'size': [128, 0, 12], 'uv': {'up': {'uv': [0, 16], 'uv_size': [256, 32]}}}]}]}]}
json.dump(geo, open(os.path.join(RP, 'models', 'entity', 'mpl_wave.geo.json'), 'w'), indent=1)
# 動き: v.t = 0〜1(5秒)。0〜0.45 寄せる(はやく、out)/ 0.45〜1 引く(ゆっくり)。引くとき前のふちがうすくのびる(z の大きさ)
anim = {'format_version': '1.8.0', 'animations': {'animation.mpl.wave': {'loop': True, 'bones': {'w': {
    'position': [0, "14.2 + v.p * 2.4", "10 - v.p * 22"],
    'scale': ["1 + v.p * 0.06", 1, "v.t < 0.45 ? 1 : 0.55 + v.p * 0.45"]}}}}}
json.dump(anim, open(os.path.join(RP, 'animations', 'mpl_wave.animation.json'), 'w'), indent=1)
ce = {'format_version': '1.10.0', 'minecraft:client_entity': {'description': {'identifier': 'mmgplus:wave', 'materials': {'default': 'entity_alphablend'},
      'textures': {'default': 'textures/entity/mpl_wave'}, 'geometry': {'default': 'geometry.mpl.wave'}, 'render_controllers': ['controller.render.default'],
      'animations': {'a': 'animation.mpl.wave'},
      'scripts': {'pre_animation': [
          "v.ph = math.mod(math.abs(q.position(0) * 0.37 + q.position(2) * 0.61), 5.0);",
          "v.t = math.mod(q.life_time + v.ph, 5.0) / 5.0;",
          "v.p = v.t < 0.45 ? math.sin(v.t / 0.45 * 90.0) : 1.0 - math.pow((v.t - 0.45) / 0.55, 0.8);"],
          'animate': ['a']}}}}
json.dump(ce, open(os.path.join(RP, 'entity', 'mpl_wave.entity.json'), 'w'), indent=1)
be = {'format_version': '1.21.20', 'minecraft:entity': {'description': {'identifier': 'mmgplus:wave', 'is_spawnable': False, 'is_summonable': True},
      'components': {'minecraft:collision_box': {'width': 0.1, 'height': 0.1}, 'minecraft:physics': {'has_gravity': False, 'has_collision': False},
                     'minecraft:damage_sensor': {'triggers': [{'cause': 'all', 'deals_damage': 'no'}]}, 'minecraft:pushable': {'is_pushable': False, 'is_pushable_by_piston': False},
                     'minecraft:persistent': {}, 'minecraft:type_family': {'family': ['mmgplus_prop', 'inanimate']}}}}
json.dump(be, open(os.path.join(BP, 'entities', 'mpl_wave.json'), 'w'), indent=1)
print('wave ok')
