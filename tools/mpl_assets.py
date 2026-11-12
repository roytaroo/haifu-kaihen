# MPL だけのモデル・アイテム(サイコロ・スター・メニュー)を作る
#   python3 tools/mpl_assets.py → mpl/src/{behavior_packs/mpl_bp, resource_packs/mpl_rp}
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import models
from models import C, rounded, eyes, model, MODELS
from PIL import Image, ImageDraw
ROOT = models.ROOT
models.BP = os.path.join(ROOT, 'mpl', 'src', 'behavior_packs', 'mpl_bp')
models.RP = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp')
models.PREVIEW = os.path.join(ROOT, 'dist', 'mpl_preview')
MODELS.clear()
W, PIP = (250, 250, 248), (30, 30, 40)
def pips(n):
    # 12x12 の面に目を描く
    a, b, c = 1, 5, 8  # 3x3 の目を置く場所(左上)
    at = {1: [(b, b)], 2: [(a, a), (c, c)], 3: [(a, a), (b, b), (c, c)], 4: [(a, a), (c, a), (a, c), (c, c)], 5: [(a, a), (c, a), (b, b), (a, c), (c, c)], 6: [(a, a), (c, a), (a, b), (c, b), (a, c), (c, c)]}[n]
    col = (220, 40, 50) if n == 1 else PIP
    big = 4 if n == 1 else 3
    return [(x + dx - (1 if n == 1 else 0), y + dy - (1 if n == 1 else 0), col) for (x, y) in at for dx in range(big) for dy in range(big)]
# サイコロ: 叩くと止まる。回っている間は mmgplus:rolling = 1
model('dice', 'サイコロ(すごろく)', [C([-6, 0, -6], [12, 12, 12], W, flat=True, decal={'north': pips(1), 'south': pips(6), 'east': pips(3), 'west': pips(4), 'top': pips(5), 'bottom': pips(2)})],
      bones={'root': [0, 6, 0]},
      anim={'root': {'rotation': ["q.property('mmgplus:rolling') * q.life_time * 720", "q.property('mmgplus:rolling') * q.life_time * 540", 0], 'position': [0, "math.sin(q.life_time * 300) * 1", 0]}},
      props={'mmgplus:rolling': {'type': 'int', 'range': [0, 1], 'default': 1, 'client_sync': True}, 'mmgplus:face': {'type': 'int', 'range': [0, 6], 'default': 0, 'client_sync': True}}, box=(0.9, 0.9), scale=1.0)
# スター: 5本の腕の星・目つき。くるくる回ってふわふわ
GOLD, GOLD2 = (255, 205, 40), (255, 235, 140)
# 腕: 根元は太く(7)、先は細く(3)。中心から少しだけ出す
arms = [c for a in (0, 72, 144, 216, 288) for c in (C([-3, 10, -1.5], [6, 6, 3], GOLD, rot=[0, 0, a], pivot=[0, 8, 0]), C([-1.5, 16, -1.5], [3, 4, 3], GOLD, rot=[0, 0, a], pivot=[0, 8, 0]))]
model('star', 'スター(すごろく)', [*rounded(0, 8, 0, 4.5, 4.5, 2, GOLD, step=1), *arms, *eyes(0, 7.5, -2.2, gap=2.5, size=2), C([-3, 11, -2.3], [2, 1, 0.3], GOLD2, flat=True)],
      bones={'root': [0, 8, 0]}, anim={'root': {'rotation': [0, "q.life_time * 90", 0], 'position': [0, "math.sin(q.life_time * 120) * 2", 0]}}, box=(1.2, 1.2), scale=2.0)
for d in [os.path.join(models.RP, 'models', 'entity'), os.path.join(models.RP, 'animations'), os.path.join(models.RP, 'entity'), os.path.join(models.BP, 'entities')]: os.makedirs(d, exist_ok=True)
for name, m in MODELS.items(): models.write(name, m)
# メニューのアイテム(オリジナルの絵: 星のついたステッキ)
im = Image.new('RGBA', (16, 16)); d = ImageDraw.Draw(im)
d.line([(3, 14), (9, 8)], fill=(150, 90, 200, 255), width=2)
d.polygon([(11, 1), (12, 4), (15, 5), (12, 7), (13, 10), (11, 8), (8, 10), (9, 7), (6, 5), (9, 4)], fill=(255, 210, 50, 255), outline=(200, 140, 20, 255))
im.save(os.path.join(models.RP, 'textures', 'items', 'mpl_menu.png'))
it = os.path.join(models.RP, 'textures', 'item_texture.json'); t = json.load(open(it)); t['texture_data']['mpl_menu'] = {'textures': 'textures/items/mpl_menu'}; t['resource_pack_name'] = 'mpl'; json.dump(t, open(it, 'w'), indent=1)
json.dump({'format_version': '1.20.50', 'minecraft:item': {'description': {'identifier': 'mpl:menu', 'menu_category': {'category': 'items'}},
           'components': {'minecraft:max_stack_size': 1, 'minecraft:icon': {'texture': 'mpl_menu'}, 'minecraft:display_name': {'value': '§eMPLのメニュー\n§7右クリック/タップ'}, 'minecraft:hand_equipped': True}}},
          open(os.path.join(models.BP, 'items', 'menu.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok')
