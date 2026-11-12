# MMG Plus のアイテム(BP items + RP の絵と item_texture.json)
#   python3 tools/items.py
#   mmgplus:boost      … コマ・バンパーカーのブースト(右クリック/タップ、クールタイムあり)
#   mmgplus:flag_*     … 旗あげゲームの旗。赤はオフハンド(左手)、白はメインハンド(右手)。上げ/下げで絵が変わる
import json, os
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, 'mmg', 'src', 'behavior_packs', 'mmg_plus', 'items')
RP = os.path.join(ROOT, 'mmg', 'src', 'resource_packs', 'mmg_plus_r')
TEX = os.path.join(RP, 'textures', 'items'); os.makedirs(BP, exist_ok=True); os.makedirs(TEX, exist_ok=True)
items = {}
def item(ident, name, tex, offhand=False):
    comps = {'minecraft:max_stack_size': 1, 'minecraft:icon': {'texture': tex}, 'minecraft:display_name': {'value': name}, 'minecraft:hand_equipped': True}
    if offhand: comps['minecraft:allow_off_hand'] = True
    json.dump({'format_version': '1.20.50', 'minecraft:item': {'description': {'identifier': ident, 'menu_category': {'category': 'items'}}, 'components': comps}},
              open(os.path.join(BP, ident.split(':')[1] + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    items[tex] = {'textures': f'textures/items/{tex}'}
# 絵(16x16): 旗
def flag(color, up):
    im = Image.new('RGBA', (16, 16)); d = ImageDraw.Draw(im)
    pole = (120, 80, 40, 255); c = color + (255,); dark = tuple(max(0, v - 50) for v in color) + (255,)
    if up:   # まっすぐ上に立てて、上に旗
        d.line([(4, 15), (4, 0)], fill=pole, width=2)
        d.rectangle([6, 1, 14, 7], fill=c); d.line([(6, 7), (14, 7)], fill=dark); d.point((5, 0), fill=(240, 200, 60, 255))
    else:    # 下に向けて、旗は下
        d.line([(2, 4), (12, 15)], fill=pole, width=2)
        d.polygon([(8, 9), (14, 15), (9, 15), (5, 11)], fill=c)
    return im
for col, rgb in (('red', (220, 40, 50)), ('white', (245, 245, 245))):
    for up in (True, False):
        k = f'mmgplus_flag_{col}_{"up" if up else "down"}'
        flag(rgb, up).save(os.path.join(TEX, k + '.png'))
        item(f'mmgplus:flag_{col}_{"up" if up else "down"}', f'{"§c赤" if col == "red" else "§f白"}の旗{"(上)" if up else "(下)"}\n§7{"しゃがむ" if col == "red" else "右クリック/タップ"}で上げ下げ', k, offhand=(col == 'red'))
# ブースト(稲妻)
im = Image.new('RGBA', (16, 16)); d = ImageDraw.Draw(im)
d.polygon([(9, 0), (3, 9), (7, 9), (5, 15), (13, 5), (9, 5), (11, 0)], fill=(255, 220, 40, 255), outline=(200, 120, 0, 255))
im.save(os.path.join(TEX, 'mmgplus_boost.png'))
item('mmgplus:boost', '§eブースト\n§7右クリック/タップで前へダッシュ(3秒に1回)', 'mmgplus_boost')
json.dump({'resource_pack_name': 'mmgplus', 'texture_name': 'atlas.items', 'texture_data': items}, open(os.path.join(RP, 'textures', 'item_texture.json'), 'w'), indent=1)
print(len(items), 'items')
