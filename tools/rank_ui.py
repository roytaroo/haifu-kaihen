# MMG Plus の画面(JSON UI)を作る
#   1) ラウンド結果の専用画面: タイトルに印 MARK があるフォームだけ、この見た目にする
#      ボタンは 2つで1行(偶数 = 左の「順位 名前」+ 行の背景の絵、奇数 = 右の「点数」)。最大12行。行は上から順にすべりこむ
#   2) 文字を「クラシック(カクカク)」フォントにそろえる: 日本語設定でも英語設定と同じ見た目にする
#   python3 tools/rank_ui.py → mmg/src/resource_packs/mmg_plus_r/ui/*.json と textures/ui/mmgplus_rank/*.png
import json, os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, 'mmg', 'src', 'resource_packs', 'mmg_plus_r')
UI = os.path.join(RP, 'ui'); TEX = os.path.join(RP, 'textures', 'ui', 'mmgplus_rank')
os.makedirs(UI, exist_ok=True); os.makedirs(TEX, exist_ok=True)
MARK = '§r§m§r§n§r'  # scripts/main.js の RANK_MARK と同じ
ROWS, W, RH = 12, 230, 18

# ===== 行の背景の絵: 順位の色(金・銀・銅・ふつう)× 上がった/下がった/そのまま × 自分かどうか =====
TIER = {'gold': (232, 180, 40), 'silver': (180, 190, 205), 'bronze': (196, 120, 70), 'normal': (70, 80, 110)}
def arrow(d, kind, x, y):
    if kind == 'up': d.polygon([(x, y + 12), (x + 7, y + 3), (x + 14, y + 12)], fill=(80, 230, 110))
    elif kind == 'down': d.polygon([(x, y + 4), (x + 7, y + 13), (x + 14, y + 4)], fill=(240, 80, 80))
    else: d.rectangle([x + 2, y + 7, x + 12, y + 9], fill=(170, 170, 185))
for tier, col in TIER.items():
    for kind in ('up', 'down', 'same'):
        for me in (0, 1):
            k = 4
            im = Image.new('RGBA', (W * k, RH * k)); d = ImageDraw.Draw(im)
            d.rounded_rectangle((0, 0, W * k - 1, RH * k - 1), 5 * k, fill=(24, 28, 44, 235) if not me else (44, 52, 90, 245),
                                outline=(255, 255, 255, 255) if me else None, width=k if me else 0)
            d.rounded_rectangle((0, 0, 16 * k, RH * k - 1), 5 * k, fill=col + (255,))  # 左の順位の帯
            d.rectangle((10 * k, 0, 16 * k, RH * k - 1), fill=col + (255,))
            im = im.resize((W * 2, RH * 2), Image.LANCZOS)
            arrow(ImageDraw.Draw(im), kind, W * 2 - 34, 10)
            im.save(os.path.join(TEX, f'{tier}_{kind}{"_me" if me else ""}.png'))
bg = Image.new('RGBA', (8, 8), (8, 10, 20, 228)); bg.save(os.path.join(TEX, 'shade.png'))
card = Image.new('RGBA', (64, 64)); ImageDraw.Draw(card).rounded_rectangle((0, 0, 63, 63), 10, fill=(14, 17, 30, 245), outline=(255, 210, 80, 255), width=2)
card.save(os.path.join(TEX, 'card.png')); json.dump({'nineslice_size': [12, 12, 12, 12], 'base_size': [64, 64]}, open(os.path.join(TEX, 'card.json'), 'w'))

# ===== ラウンド結果の画面 =====
coll = lambda name, over=None: dict({'binding_name': name, 'binding_type': 'collection', 'binding_collection_name': 'form_buttons'}, **({'binding_name_override': over} if over else {}))
ui = {'namespace': 'server_form'}
rows = []
for i in range(ROWS):
    delay = 0.15 + i * 0.07
    ui[f'mmg_row_o{i}'] = {'anim_type': 'offset', 'from': [-400, 0], 'to': [-400, 0], 'duration': delay, 'next': '@server_form.mmg_row_o'}
    left = {'type': 'panel', 'size': [W, RH], 'collection_index': i * 2, 'bindings': [coll('#form_button_text'), {'binding_type': 'view', 'source_property_name': "(not (#form_button_text = ''))", 'target_property_name': '#visible'}],
            'controls': [
                {'bg': {'type': 'image', 'size': ['100%', '100%'], 'layer': 1, 'bindings': [coll('#form_button_texture', '#texture'), coll('#form_button_texture_file_system', '#texture_file_system')]}},
                {'t': {'type': 'label', 'text': '#form_button_text', 'layer': 2, 'anchor_from': 'left_middle', 'anchor_to': 'left_middle', 'offset': [5, 1], 'size': [W - 70, 'default'], 'shadow': True, 'localize': False, 'font_type': 'MinecraftTen', 'bindings': [coll('#form_button_text')]}}]}
    right = {'type': 'label', 'text': '#form_button_text', 'layer': 3, 'collection_index': i * 2 + 1, 'anchor_from': 'right_middle', 'anchor_to': 'right_middle', 'offset': [-22, 1],
             'size': [70, 'default'], 'text_alignment': 'right', 'shadow': True, 'localize': False, 'font_type': 'MinecraftTen', 'bindings': [coll('#form_button_text')]}
    rows.append({f'row{i}': {'type': 'panel', 'size': [W, RH + 3], 'collection_name': 'form_buttons', 'anims': [f'@server_form.mmg_row_o{i}'],
                             'controls': [{'l': left}, {'r': right}]}})
ui['mmg_row_o'] = {'anim_type': 'offset', 'from': [-400, 0], 'to': [0, 0], 'duration': 0.35, 'easing': 'out_back'}
ui['mmg_rank_form'] = {
    'type': 'panel', 'size': ['100%', '100%'], 'layer': 60, 'collection_name': 'form_buttons',
    'bindings': [{'binding_name': '#title_text'}, {'binding_type': 'view', 'source_property_name': f"(not ((#title_text - '{MARK}') = #title_text))", 'target_property_name': '#visible'}],
    'controls': [
        {'shade': {'type': 'image', 'texture': 'textures/ui/mmgplus_rank/shade', 'size': ['100%', '100%'], 'layer': 0}},
        {'card': {'type': 'image', 'texture': 'textures/ui/mmgplus_rank/card', 'size': [W + 24, 'children'], 'layer': 1, 'collection_name': 'form_buttons', 'controls': [{'stack': {
            'type': 'stack_panel', 'orientation': 'vertical', 'size': [W, 'children'], 'offset': [0, 0], 'collection_name': 'form_buttons',
            'controls': [
                {'pad0': {'type': 'panel', 'size': ['100%', 10]}},
                {'head': {'type': 'label', 'text': '#title_text', 'size': ['100%', 'default'], 'text_alignment': 'center', 'font_type': 'MinecraftTen', 'font_scale_factor': 1.3, 'color': [1, 0.85, 0.3], 'shadow': True, 'localize': False,
                          'bindings': [{'binding_name': '#title_text'}]}},
                {'sub': {'type': 'label', 'text': '#form_text', 'size': ['100%', 'default'], 'text_alignment': 'center', 'font_type': 'MinecraftTen', 'color': [0.8, 0.85, 1], 'localize': False,
                         'bindings': [{'binding_name': '#form_text'}]}},
                {'pad1': {'type': 'panel', 'size': ['100%', 8]}},
                *rows,
                {'pad2': {'type': 'panel', 'size': ['100%', 8]}}]}}]}}]}
# 画面に足す: long_form をまるごと定義(BOWFLIT で動いている形)。ふつうのフォームは印がない時だけ出す
NORMAL = {'$title_panel': 'common_dialogs.standard_title_label', '$title_size': ['100% - 14px', 10], 'size': [225, 200], '$text_name': '#title_text',
          '$title_text_binding_type': 'none', '$child_control': 'server_form.long_form_panel', 'layer': 2,
          'bindings': [{'binding_name': '#title_text'}, {'binding_type': 'view', 'source_property_name': f"((#title_text - '{MARK}') = #title_text)", 'target_property_name': '#visible'}]}
ui['long_form'] = {'type': 'panel', 'size': ['100%', '100%'], 'controls': [{'long_form@common_dialogs.main_panel_no_buttons': NORMAL}, {'mmg_rank_form@server_form.mmg_rank_form': {}}]}
json.dump(ui, open(os.path.join(UI, 'server_form.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ===== 文字をクラシックフォントにそろえる =====
# どのラベルも「#font_type を classic にする」+ 元からある紐付けをそのまま残す
CLASSIC = lambda binds=(), extra=None: dict({'property_bag': {'#font_type': 'classic'}, 'bindings': list(binds) + [{'binding_type': 'view', 'source_property_name': '#font_type', 'target_property_name': '#font_type'}]}, **(extra or {}))
FT = {'font_type': '#font_type'}
g = lambda name, over=None, **kw: dict({'binding_name': name, 'binding_type': 'global'}, **({'binding_name_override': over} if over else {}), **kw)
files = {
    'hud_screen.json': {'namespace': 'hud',
        'hud_actionbar_text/actionbar_message': CLASSIC(),
        'hud_title_text/title_frame/title': CLASSIC([g('#hud_title_text_string', '#text')]),
        'hud_title_text/subtitle_frame/subtitle': CLASSIC([g('#hud_subtitle_text_string', '#text')]),
        'chat_label': CLASSIC([{'binding_name': '#chat_text', 'binding_name_override': '#text', 'binding_type': 'collection', 'binding_collection_name': 'chat_text_grid', 'binding_condition': 'once'}], dict(FT, font_scale_factor=1.0)),
        'item_name_text_root/item_text_aligner/item_text_control/item_text_label': CLASSIC([{'binding_name': '$text_binding', 'binding_name_override': '#text'}]),
        'hud_tip_text/item_text_label': CLASSIC([{'binding_name': '#tip_text', 'binding_name_override': '#text'}]),
        'boss_name_panel/boss_name': CLASSIC([{'binding_name': '#bossName', 'binding_type': 'collection', 'binding_collection_name': 'boss_bars'}])},
    'chat_screen.json': {'namespace': 'chat', 'messages_text/text': CLASSIC([], dict(FT, font_scale_factor=1.0))},
    'scoreboards.json': {'namespace': 'scoreboard',
        'scoreboard_sidebar_score': CLASSIC([{'binding_name': '#player_score_sidebar', 'binding_type': 'collection', 'binding_collection_name': 'scoreboard_scores'}]),
        'scoreboard_sidebar_player': CLASSIC([{'binding_name': '#player_name_sidebar', 'binding_type': 'collection', 'binding_collection_name': 'scoreboard_players'}]),
        'scoreboard_sidebar/main/displayed_objective': CLASSIC([g('#objective_sidebar_name')])},
}
for fn, d in files.items(): json.dump(d, open(os.path.join(UI, fn), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for fn in ('ui_template_buttons.json', 'ui_template_dialogs.json'):
    if os.path.exists(os.path.join(UI, fn)): os.remove(os.path.join(UI, fn))
print('ok')
