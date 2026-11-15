# MPL の演出用 UI を作る(すべて自作)
#   1) ロゴ(金・色つきグラデ + 太いふち + ポンと出る + きらっと光る): 大事な場面のタイトルを専用ロゴにする
#   2) 帯(リボン)とカード: 文字のお知らせを、色つきの帯やカードで見せる
#   3) 専用フォーム(ショップ・スター・アイテム・メニュー): タイトルに FORM_MARK があるフォームだけこの見た目
#   4) アクションバーとサイドバーの背景を差しかえ
#   使い方: MPL_RP=... RANK_SCALE=8 python3 tools/rank_ui.py の「あと」に python3 tools/mpl_ui.py
#   スクリプト側は main.js の BANNER(キー一覧)/ banner() / ribbon() / FORM_MARK と合わせる
import json, os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp')
UI = os.path.join(RP, 'ui'); TEX = os.path.join(RP, 'textures', 'ui', 'mpl')
os.makedirs(TEX, exist_ok=True)
JP = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
EN = '/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf'
BMARK = '§r§b§r§n§r'      # main.js の BMARK と同じ
FORM_MARK = '§r§p§r§q§r'  # main.js の FORM_MARK と同じ
RANK_MARK = '§r§m§r§n§r'
code = lambda i: f'§{i // 16:x}§{i % 16:x}§r'

# ===== 色 =====
TH = {  # 上の色, 下の色, 内側のふち
    'gold': ((255, 246, 150), (255, 150, 10), (120, 50, 0)),
    'blue': ((170, 235, 255), (30, 120, 255), (10, 30, 110)),
    'red': ((255, 200, 160), (235, 30, 40), (100, 0, 10)),
    'green': ((210, 255, 160), (40, 190, 60), (0, 70, 20)),
    'purple': ((235, 190, 255), (140, 50, 230), (50, 0, 90)),
    'pink': ((255, 210, 240), (255, 70, 170), (100, 0, 60)),
    'dark': ((200, 190, 230), (90, 60, 140), (25, 10, 45)),
}
RAINBOW = ['red', 'gold', 'green', 'blue', 'purple', 'pink']

def grad(w, h, top, bot):
    g = Image.new('RGB', (1, h))
    for y in range(h):
        t = y / max(1, h - 1); t = t * t * (3 - 2 * t)
        g.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return g.resize((w, h))

def dil(m, r):
    while r > 0:
        k = min(r, 6); m = m.filter(ImageFilter.MaxFilter(2 * k + 1)); r -= k
    return m

def logo(text, theme, W=1280, H=320, jp=True, tilt=True):
    """文字をロゴにする。返り値は (RGBA 画像, 文字の塗りマスク)"""
    S = 1  # 大きめに描いて縮める
    W2, H2 = W * S, H * S
    font = ImageFont.truetype(JP if jp else EN, 230 * S)
    chars = list(text)
    # 文字ごとの大きさ
    imgs = []
    for i, ch in enumerate(chars):
        bb = font.getbbox(ch)
        cw, chh = max(1, bb[2] - bb[0]), max(1, bb[3] - bb[1])
        m = Image.new('L', (cw + 40 * S, chh + 40 * S)); ImageDraw.Draw(m).text((20 * S - bb[0], 20 * S - bb[1]), ch, font=font, fill=255)
        if not ch.strip(): m = Image.new('L', (110 * S, 40 * S))
        if jp: m = dil(m, 5 * S)  # ゴシックを太く
        if tilt and ch.strip(): m = m.rotate((-5 if i % 2 else 5), resample=Image.BICUBIC, expand=True)
        imgs.append(m)
    gap = -34 * S
    tw = sum(m.width for m in imgs) + gap * (len(imgs) - 1)
    th = max(m.height for m in imgs)
    canvas_w, canvas_h = tw + 120 * S, th + 120 * S
    full = Image.new('L', (canvas_w, canvas_h)); fill = Image.new('RGB', (canvas_w, canvas_h))
    x = 60 * S
    for i, m in enumerate(imgs):
        bob = (-10 * S if i % 2 else 6 * S) if tilt else 0
        y = 60 * S + (th - m.height) // 2 + bob
        full.paste(255, (x, y), m)
        t = theme if isinstance(theme, str) else theme[i % len(theme)]
        top, bot, _ = TH[t]
        fill.paste(grad(m.width, m.height, top, bot), (x, y), m)
        x += m.width + gap
    inner = TH[theme if isinstance(theme, str) else 'gold'][2]
    if not isinstance(theme, str): inner = (40, 20, 70)
    o3 = dil(full, 5 * S); o2 = dil(full, 15 * S); o1 = dil(full, 22 * S)
    out = Image.new('RGBA', (canvas_w, canvas_h))
    sh = o1.filter(ImageFilter.GaussianBlur(6 * S)).point(lambda v: v * 0.55)
    out.paste((0, 0, 0, 255), (0, 16 * S), sh)
    # 厚み(下に押し出した立体)
    dk = tuple(max(0, int(c * 0.45)) for c in inner)
    for k in range(12 * S, 0, -1):
        out.paste(dk + (255,), (0, k), o1)
    out.paste((25, 15, 50, 255), (0, 0), o1)
    out.paste((255, 255, 255, 255), (0, 0), o2)
    out.paste(inner + (255,), (0, 0), o3)
    out.paste(fill, (0, 0), full)
    # 上半分のつや
    hl = Image.new('L', (canvas_w, canvas_h))
    d = ImageDraw.Draw(hl)
    for y in range(canvas_h):
        a = max(0, 1 - abs(y - canvas_h * 0.36) / (canvas_h * 0.12))
        d.line([(0, y), (canvas_w, y)], fill=int(90 * a))
    out.paste((255, 255, 255, 255), (0, 0), ImageChops.multiply(hl, full.filter(ImageFilter.MinFilter(9))))
    # 収める
    bb = out.getbbox(); out = out.crop(bb); full = full.crop(bb)
    k = min((W2 - 20 * S) / out.width, (H2 - 10 * S) / out.height)
    nw, nh = int(out.width * k), int(out.height * k)
    out = out.resize((nw, nh), Image.LANCZOS); full = full.resize((nw, nh), Image.LANCZOS)
    a = Image.new('RGBA', (W2, H2)); a.paste(out, ((W2 - nw) // 2, (H2 - nh) // 2))
    f = Image.new('L', (W2, H2)); f.paste(full, ((W2 - nw) // 2, (H2 - nh) // 2))
    return a.resize((W, H), Image.LANCZOS), f.resize((W, H), Image.LANCZOS)

FR = 14  # 光が走るコマ数
def shine_strip(img, mask):
    """ロゴの上を光の帯が走るコマ送り(縦に並べる)。最初の4コマと最後はそのまま"""
    W, H = img.size
    strip = Image.new('RGBA', (W, H * FR))
    for f in range(FR):
        fr = img.copy()
        t = (f - 4) / 8
        if 0 <= t <= 1:
            band = Image.new('L', (W, H)); d = ImageDraw.Draw(band)
            cx = -W * 0.2 + t * W * 1.4
            for dx in range(-60, 61):
                a = int(200 * (1 - abs(dx) / 60) ** 1.5)
                d.line([(cx + dx - H * 0.4, H), (cx + dx + H * 0.4, 0)], fill=a)
            fr.paste((255, 255, 255, 255), (0, 0), ImageChops.multiply(band, mask))
        strip.paste(fr, (0, H * f))
    return strip

# ===== ロゴの一覧(キー, 文字, 色, 日本語?, 光の放射?)=====
LOGOS = [
    ('title', 'MEGAMI PARTY LAND', RAINBOW, False, True),
    ('turn', 'TURN', 'blue', False, False),
    ('yourturn', 'YOUR TURN!', 'gold', False, True),
    ('order', 'TURN ORDER', 'blue', False, False),
    ('starappear', 'STAR APPEARS!', 'gold', False, True),
    ('star', 'STAR GET!', 'gold', False, True),
    ('minigame', 'MINIGAME!', RAINBOW, False, True),
    ('win', 'WINNER!', 'red', False, True),
    ('happening', 'HAPPENING!', 'green', False, False),
    ('skull', 'BAD LUCK...', 'dark', False, False),
    ('shop', 'WELCOME!', 'pink', False, False),
    ('lucky', 'LUCKY!', 'gold', False, True),
    ('gameset', 'GAME SET!', 'red', False, False),
    ('result', 'RESULTS', 'gold', False, True),
    ('champion', 'CHAMPION!', 'gold', False, True),
    ('lastspurt', 'FINAL STRETCH!', 'red', False, False),
    ('bonus', 'BONUS STARS', 'gold', False, True),
    ('item', 'ITEM!', 'purple', False, False),
    ('finish', 'FINISH!', 'gold', False, True),
    ('bonusgame', 'BONUS GAME!', RAINBOW, False, True),
    ('sudden', 'SUDDEN DEATH', 'red', False, False),
    ('vs', 'VS', 'red', False, True),
]
NUMS = list(range(0, 31))
RIBBONS = {'gold': ((255, 214, 70), (220, 120, 0)), 'blue': ((90, 170, 255), (20, 70, 200)), 'red': ((255, 110, 100), (180, 20, 30)),
           'purple': ((200, 130, 255), (110, 40, 200)), 'green': ((120, 230, 110), (20, 140, 50)), 'gray': ((140, 145, 165), (60, 64, 82))}
KEYS = [k for k, *_ in LOGOS] + [f'n{n}' for n in NUMS] + [f'r_{c}' for c in RIBBONS] + ['card', 'talk']
assert len(KEYS) <= 256

def nine(name, img, sl, scale=1):
    # scale: 絵の細かさ(2 = 2倍の細かさで描いた)。base_size と nineslice_size は画面での大きさ(角がゆがまないように)
    img.save(os.path.join(TEX, name + '.png'))
    json.dump({'nineslice_size': sl, 'base_size': [img.size[0] // scale, img.size[1] // scale]}, open(os.path.join(TEX, name + '.json'), 'w'))

if not os.environ.get('MPL_UI_JSON_ONLY'):
    LW, LH = 1024, 256
    for key, text, th, jp, _ in LOGOS:
        im, m = logo(text, th, LW, LH, jp, tilt=False)
        im.save(os.path.join(TEX, f'logo_{key}.png'), optimize=True)
        pass
    for n in NUMS:
        im, _ = logo(str(n), 'gold', 240, 180, False, tilt=False)
        im.save(os.path.join(TEX, f'num_{n}.png'), optimize=True)
    # きらっと光る星(ロゴのはしに出る)
    g = Image.new('RGBA', (128, 128)); d = ImageDraw.Draw(g)
    d.polygon([(64, 0), (74, 54), (128, 64), (74, 74), (64, 128), (54, 74), (0, 64), (54, 54)], fill=(255, 255, 240, 255))
    g = Image.alpha_composite(g.filter(ImageFilter.GaussianBlur(6)), g); g.save(os.path.join(TEX, 'glint.png'))
    # 放射(回るコマ送り 8コマ)
    R, NR = 256, 16
    strip = Image.new('RGBA', (R, R * 8))
    for f in range(8):
        im = Image.new('RGBA', (R * 2, R * 2)); d = ImageDraw.Draw(im)
        for k in range(NR):
            a0 = (k / NR + f / NR / 8) * 2 * math.pi; a1 = a0 + math.pi / NR * 0.9
            d.polygon([(R, R), (R + math.cos(a0) * R * 1.5, R + math.sin(a0) * R * 1.5), (R + math.cos(a1) * R * 1.5, R + math.sin(a1) * R * 1.5)], fill=(255, 230, 120, 150))
        fade = Image.new('L', (R * 2, R * 2)); ImageDraw.Draw(fade).ellipse((R * 0.1, R * 0.1, R * 1.9, R * 1.9), fill=255)
        fade = fade.filter(ImageFilter.GaussianBlur(R * 0.35))
        im.putalpha(ImageChops.multiply(im.getchannel('A'), fade))
        strip.paste(im.resize((R, R), Image.LANCZOS), (0, R * f))
    strip.crop((0, 0, R, R)).save(os.path.join(TEX, 'rays.png'))  # 1枚だけ使う(コマ送りはゲームで効かなかった)
    # 光のフラッシュ
    fl = Image.new('L', (256, 128)); ImageDraw.Draw(fl).ellipse((20, 20, 236, 108), fill=255); fl = fl.filter(ImageFilter.GaussianBlur(22))
    Image.merge('RGBA', (Image.new('L', fl.size, 255), Image.new('L', fl.size, 250), Image.new('L', fl.size, 220), fl)).save(os.path.join(TEX, 'flash.png'))
    # 帯: 暗い半透明のカプセル + 色の細いふち + 左に色のしるし(すっきりした見た目)
    ACC = {'gold': (255, 196, 40), 'blue': (70, 160, 255), 'red': (255, 80, 80), 'purple': (180, 110, 255), 'green': (90, 220, 110), 'gray': (170, 175, 195)}
    for c in RIBBONS:
        S = 4; w, h = 96 * S, 28 * S; col = ACC[c]
        im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 10 * S, fill=(255, 255, 255, 70))
        g = grad(w, h, (30, 34, 58), (12, 14, 28)); mk = Image.new('L', (w, h))
        ImageDraw.Draw(mk).rounded_rectangle((S, S, w - 1 - S, h - 1 - S), 9 * S, fill=228)
        im.paste(g, (0, 0), mk)
        d.line([(12 * S, 3 * S), (w - 12 * S, 3 * S)], fill=(255, 255, 255, 50), width=S)          # 上のつや
        nine(f'ribbon_{c}', im.resize((w // 2, h // 2), Image.LANCZOS), [8, 5, 8, 5], 4)  # 角の丸み 5、真ん中が残る
    # カード(ミニゲームの説明・フォーム): 暗い半透明 + うすい白のふち(オレンジのふちはやめた)
    S = 4; w = h = 48 * S
    im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 9 * S, fill=(255, 255, 255, 70))
    g = grad(w, h, (30, 34, 58), (14, 16, 30)); mk = Image.new('L', (w, h))
    ImageDraw.Draw(mk).rounded_rectangle((S, S, w - 1 - S, h - 1 - S), 8 * S, fill=225)
    im.paste(g, (0, 0), mk)
    d.line([(10 * S, 2 * S), (w - 10 * S, 2 * S)], fill=(255, 255, 255, 60), width=S)
    nine('card', im.resize((96, 96), Image.LANCZOS), [12, 12, 12, 12], 2)
    # ボタン(ふつう・選択中・押した)
    # ボタン: ふだん = ガラス + うすい白のふち / 選択中 = 少し明るく + 金のふち / 押した = 暗く + 金のふち(少し下へ)
    # ボタン: ふだん = あざやかな青 / 選択中 = 金 / 押した = こい金(少し下へ)。パーティらしい色
    for name, top, bot, border in [('btn', (90, 110, 210), (45, 55, 140), (20, 14, 40)), ('btn_hover', (255, 226, 110), (240, 150, 20), (255, 255, 255)), ('btn_press', (220, 140, 20), (170, 90, 0), (255, 255, 255))]:
        S = 4; w, h = 48 * S, 24 * S
        im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 7 * S, fill=border + (255,))
        mk = Image.new('L', (w, h)); ImageDraw.Draw(mk).rounded_rectangle((2 * S, 2 * S, w - 1 - 2 * S, h - 1 - 2 * S - (0 if 'press' in name else 2 * S)), 5 * S, fill=255)
        im.paste((10, 8, 25, 255), (0, 2 * S), mk)
        im.paste(grad(w, h, top, bot), (0, 2 * S if 'press' in name else 0), mk)
        ImageDraw.Draw(im).line([(7 * S, 4 * S), (w - 7 * S, 4 * S)], fill=(255, 255, 255, 110), width=S)
        nine(name, im.resize((w // 2, h // 2), Image.LANCZOS), [6, 6, 6, 6], 2)
    # メニューの見出しの帯: ピンク→むらさきのあざやかな帯 + 白いふち
    S = 4; w, h = 96 * S, 28 * S
    im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 10 * S, fill=(255, 255, 255, 255))
    g = Image.new('RGBA', (w, h))
    for x in range(w):
        t = x / (w - 1); ImageDraw.Draw(g).line([(x, 0), (x, h)], fill=(round(255 - 120 * t), round(70 + 10 * t), round(170 + 70 * t), 255))
    mk = Image.new('L', (w, h)); ImageDraw.Draw(mk).rounded_rectangle((2 * S, 2 * S, w - 1 - 2 * S, h - 1 - 2 * S), 8 * S, fill=255)
    im.paste(g, (0, 0), mk)
    d.line([(12 * S, 5 * S), (w - 12 * S, 5 * S)], fill=(255, 255, 255, 90), width=S)
    nine('head', im.resize((w // 2, h // 2), Image.LANCZOS), [8, 6, 8, 6], 4)
    # 見出しの下の細い線
    ln = Image.new('RGBA', (64, 2)); ImageDraw.Draw(ln).line([(0, 0), (63, 0)], fill=(255, 255, 255, 90), width=1); ln.save(os.path.join(TEX, 'line.png'))
    # アクションバー・説明の文字の背景: 暗い半透明の角丸だけ(ふちなし)
    S = 4; im = Image.new('RGBA', (64 * S, 32 * S)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 64 * S - 1, 32 * S - 1), 6 * S, fill=(10, 12, 24, 170))
    im = im.resize((128, 64), Image.LANCZOS)
    nine('toast', im, [6, 6, 6, 6], 2)
    im = Image.new('RGBA', (16, 16)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 15, 15), fill=(10, 12, 24, 170)); d.rectangle((0, 0, 15, 0), fill=(255, 255, 255, 70))
    nine('side', im, [3, 3, 3, 3])
    print('textures ok')

# ===== HUD(タイトルの代わりにロゴ・帯・カード)=====
col = lambda name, over=None, kind='global': dict({'binding_name': name, 'binding_type': kind}, **({'binding_name_override': over} if over else {}))
T = '#hud_title_text_string'
has = lambda s, prop=T: f"(not (({prop} - '{s}') = {prop}))"
hasnt = lambda s, prop=T: f"(({prop} - '{s}') = {prop})"
vis = lambda expr: {'binding_type': 'view', 'source_property_name': expr, 'target_property_name': '#visible'}
hud = json.load(open(os.path.join(UI, 'hud_screen.json'), encoding='utf-8'))
hud.update({
    'mpl_pop1': {'anim_type': 'size', 'easing': 'out_quad', 'duration': 0.2, 'from': ['10%', '10%'], 'to': ['115%', '115%'], 'next': '@hud.mpl_pop2'},
    'mpl_pop2': {'anim_type': 'size', 'easing': 'in_out_sine', 'duration': 0.15, 'from': ['115%', '115%'], 'to': ['100%', '100%']},
    'mpl_flash': {'anim_type': 'alpha', 'easing': 'out_quad', 'duration': 0.6, 'from': 1.0, 'to': 0.0},
    'mpl_glint': {'anim_type': 'size', 'duration': 0.45, 'from': [0, 0], 'to': [0, 0], 'next': '@hud.mpl_glint2'},
    'mpl_glint2': {'anim_type': 'size', 'easing': 'out_quad', 'duration': 0.18, 'from': [0, 0], 'to': [34, 34], 'next': '@hud.mpl_glint3'},
    'mpl_glint3': {'anim_type': 'size', 'easing': 'in_quad', 'duration': 0.3, 'from': [34, 34], 'to': [0, 0]},
    'mpl_rays': {'anim_type': 'size', 'easing': 'in_out_sine', 'duration': 0.7, 'from': ['88%', '88%'], 'to': ['112%', '112%'], 'next': '@hud.mpl_rays2'},
    'mpl_rays2': {'anim_type': 'size', 'easing': 'in_out_sine', 'duration': 0.7, 'from': ['112%', '112%'], 'to': ['88%', '88%'], 'next': '@hud.mpl_rays'},
    'mpl_slide': {'anim_type': 'offset', 'easing': 'out_back', 'duration': 0.35, 'from': [-420, 0], 'to': [0, 0]},
    'mpl_drop': {'anim_type': 'offset', 'easing': 'out_back', 'duration': 0.4, 'from': [0, -60], 'to': [0, 0]},
    'mpl_fadein': {'anim_type': 'alpha', 'easing': 'linear', 'duration': 0.25, 'from': 0.0, 'to': 1.0},
})
SUB = {'type': 'image', 'texture': 'textures/ui/mpl/toast', 'size': ['100%c + 16px', '100%c + 8px'], 'layer': 5, 'anchor_from': 'top_middle', 'anchor_to': 'top_middle',
       'anims': ['@hud.mpl_fadein'],
       'bindings': [col('#hud_subtitle_text_string'), vis("(not (#hud_subtitle_text_string = ''))")],
       'controls': [{'t': {'type': 'label', 'text': '#hud_subtitle_text_string', 'layer': 6, 'shadow': True, 'localize': False, 'font_scale_factor': 1.0, 'color': [1, 1, 1],
                           'bindings': [col('#hud_subtitle_text_string')]}}]}
ctrls = []
for i, key in enumerate(KEYS):
    mark = BMARK + code(i)
    if key.startswith('n'):  # 数字(サイコロ)
        body = [{'num': {'type': 'image', 'texture': f'textures/ui/mpl/num_{key[1:]}', 'size': [80, 60], 'layer': 3, 'anchor_from': 'top_middle', 'anchor_to': 'top_middle',
                         'anims': ['@hud.mpl_pop1']}},
                {'sub@hud.mpl_sub': {'offset': [0, 62]}}]
    elif key.startswith('r_'):  # 帯
        body = [{'stack': {'type': 'stack_panel', 'orientation': 'vertical', 'size': ['100%', '100%c'], 'anchor_from': 'top_middle', 'anchor_to': 'top_middle', 'anims': ['@hud.mpl_slide'], 'controls': [
            {'rb': {'type': 'panel', 'size': ['100%', '100%c'], 'controls': [{'img': {'type': 'image', 'texture': f'textures/ui/mpl/ribbon_{key[2:]}', 'size': ['100%c + 44px', '100%c + 12px'], 'layer': 3,
                    'controls': [{'t': {'type': 'label', 'text': T, 'layer': 4, 'shadow': True, 'localize': False, 'font_scale_factor': 1.3, 'color': [1, 1, 1], 'bindings': [col(T)]}}]}}]}},
            {'gap': {'type': 'panel', 'size': ['100%', 4]}},
            {'sb': {'type': 'panel', 'size': ['100%', '100%c'], 'controls': [{'sub@hud.mpl_sub': {}}]}}]}}]
    elif key == 'talk':  # DJ トシオのせりふ(画面の下の方、RPG の文字の箱)
        body = [{'img': {'type': 'image', 'texture': 'textures/ui/mpl/card', 'size': [290, '100%c + 16px'], 'layer': 3, 'anchor_from': 'top_middle', 'anchor_to': 'top_middle', 'offset': [-20, 122],
                         'anims': ['@hud.mpl_fadein'], 'controls': [{'st': {'type': 'stack_panel', 'orientation': 'vertical', 'size': [268, '100%c'], 'controls': [
                             {'name': {'type': 'label', 'text': T, 'size': ['100%', 'default'], 'text_alignment': 'left', 'layer': 5, 'shadow': True, 'localize': False, 'color': [1, 0.82, 0.3], 'bindings': [col(T)]}},
                             {'g0': {'type': 'panel', 'size': ['100%', 3]}}, {'ln': {'type': 'image', 'texture': 'textures/ui/mpl/line', 'size': ['100%', 1], 'layer': 5}}, {'gap': {'type': 'panel', 'size': ['100%', 4]}},
                             {'say': {'type': 'label', 'text': '#hud_subtitle_text_string', 'size': ['100%', 'default'], 'text_alignment': 'left', 'layer': 5, 'shadow': True, 'localize': False,
                                      'font_scale_factor': 1.0, 'color': [1, 1, 1], 'bindings': [col('#hud_subtitle_text_string')]}}]}}]}}]
    elif key == 'card':  # ミニゲームの説明カード
        body = [{'img': {'type': 'image', 'texture': 'textures/ui/mpl/card', 'size': [280, '100%c + 22px'], 'layer': 3, 'anchor_from': 'top_middle', 'anchor_to': 'top_middle',
                         'anims': ['@hud.mpl_drop'], 'controls': [{'st': {'type': 'stack_panel', 'orientation': 'vertical', 'size': [256, '100%c'], 'controls': [
                             {'head': {'type': 'label', 'text': T, 'size': ['100%', 'default'], 'text_alignment': 'center', 'layer': 5, 'shadow': True, 'localize': False, 'font_scale_factor': 1.25, 'color': [1, 0.82, 0.3], 'bindings': [col(T)]}},
                             {'g0': {'type': 'panel', 'size': ['100%', 4]}}, {'ln': {'type': 'image', 'texture': 'textures/ui/mpl/line', 'size': ['100%', 1], 'layer': 5}}, {'gap': {'type': 'panel', 'size': ['100%', 5]}},
                             {'how': {'type': 'label', 'text': '#hud_subtitle_text_string', 'size': ['100%', 'default'], 'text_alignment': 'center', 'layer': 5, 'shadow': True, 'localize': False,
                                      'font_scale_factor': 1.0, 'color': [0.85, 0.88, 1], 'bindings': [col('#hud_subtitle_text_string')]}}]}}]}}]
    else:  # ロゴ
        rays = [k for k, *_, r in LOGOS if r]
        body = []
        if False and key in rays:  # 光の放射はやめた(はしが切れて見えるため)
            body.append({'rays': {'type': 'panel', 'size': [200, 200], 'offset': [0, -60], 'anchor_from': 'top_middle', 'anchor_to': 'top_middle', 'controls': [
                {'img': {'type': 'image', 'texture': 'textures/ui/mpl/rays', 'size': ['100%', '100%'], 'layer': 1, 'alpha': 0.85, 'anims': ['@hud.mpl_rays']}}]}})
        body += [{'flash': {'type': 'image', 'texture': 'textures/ui/mpl/flash', 'size': [300, 110], 'offset': [0, -20], 'layer': 2, 'anchor_from': 'top_middle', 'anchor_to': 'top_middle', 'anims': ['@hud.mpl_flash']}},
                 {'box': {'type': 'panel', 'size': [200, 103] if key == 'title' else [210, 52], 'anchor_from': 'top_middle', 'anchor_to': 'top_middle', 'controls': [
                     {'logo': {'type': 'image', 'texture': 'textures/ui/mpl/logo_venus' if key == 'title' else f'textures/ui/mpl/logo_{key}', 'size': ['100%', '100%'], 'layer': 3, 'anims': ['@hud.mpl_pop1']}},
                     {'glint': {'type': 'image', 'texture': 'textures/ui/mpl/glint', 'size': [0, 0], 'offset': [96, -18], 'layer': 4, 'anims': ['@hud.mpl_glint']}}]}},
                 ({'tsub': {'type': 'label', 'text': '#hud_subtitle_text_string', 'offset': [0, 106], 'layer': 5, 'anchor_from': 'top_middle', 'anchor_to': 'top_middle',
                            'shadow': True, 'localize': False, 'font_scale_factor': 0.9, 'color': [1, 1, 1], 'anims': ['@hud.mpl_fadein'], 'bindings': [col('#hud_subtitle_text_string')]}}
                  if key == 'title' else {'sub@hud.mpl_sub': {'offset': [0, 54]}})]  # タイトルの下は背景なし・小さめ
    ctrls.append({f'k_{key}': {'type': 'panel', 'size': ['100%', 0], 'anchor_from': 'top_middle', 'anchor_to': 'top_middle', 'offset': [0, 2],  # 画面の上の端から(人の顔に重ならない)
                                'bindings': [col(T), vis(has(mark))], 'controls': body}})
hud['mpl_sub'] = dict(SUB, offset=[0, 0])
hud['mpl_banner'] = {'type': 'panel', 'size': ['100%', 0], 'controls': ctrls}
hud['hud_title_text'] = {'anchor_from': 'top_middle', 'anchor_to': 'top_middle', 'offset': [0, 6], 'modifications': [{'array_name': 'controls', 'operation': 'insert_front', 'value': [{'mpl_banner@hud.mpl_banner': {}}]}]}
# ふつうのタイトル・サブタイトルは印がある時だけかくす
def hide(path, binds):
    d = hud.setdefault(path, {})
    d['bindings'] = list(d.get('bindings', [])) + binds
for path in ('hud_title_text/title_frame/title',):
    hide(path, [vis(hasnt(BMARK, '#text'))])
for path in ('hud_title_text/title_frame/title_background', 'hud_title_text/subtitle_frame/subtitle', 'hud_title_text/subtitle_frame/subtitle_background'):
    hide(path, [col(T), vis(hasnt(BMARK))])
hud['item_name_text'] = {'ignored': True}  # アイテムを持ったときの名前・ロックなどの表示を出さない
hud['hud_actionbar_text'] = {'texture': 'textures/ui/mpl/toast', 'size': ['100%c + 22px', '100%c + 10px']}
json.dump(hud, open(os.path.join(UI, 'hud_screen.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# サイドバーの背景
sb = json.load(open(os.path.join(UI, 'scoreboards.json'), encoding='utf-8'))
sb['scoreboard_sidebar/main'] = {'texture': 'textures/ui/mpl/side', 'alpha': 1.0, 'bindings': []}
sb.setdefault('scoreboard_sidebar_score', {})['visible'] = False  # 並び順用の数字はかくす
sb['scoreboard_sidebar'] = dict(sb.get('scoreboard_sidebar', {}), anchor_from='bottom_right', anchor_to='bottom_right', offset=[-3, -3])  # 右下に固定
sb.setdefault('scoreboard_sidebar_player', {})['max_size'] = [220, 10]  # 長い行が切れないように
sb.setdefault('scoreboard_sidebar/main/displayed_objective', {})['max_size'] = [220, 10]
json.dump(sb, open(os.path.join(UI, 'scoreboards.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ===== 専用フォーム =====
sf = json.load(open(os.path.join(UI, 'server_form.json'), encoding='utf-8'))
TT = '#title_text'
c2 = lambda name, over=None: dict({'binding_name': name, 'binding_type': 'collection', 'binding_collection_name': 'form_buttons'}, **({'binding_name_override': over} if over else {}))
sf['mpl_btn'] = {'type': 'panel', 'size': ['100%', 28], 'controls': [{'b@common.button': {
    '$pressed_button_name': 'button.form_button_click', 'size': ['100% - 8px', 25], 'anchor_from': 'center', 'anchor_to': 'center',
    'bindings': [{'binding_type': 'collection_details', 'binding_collection_name': 'form_buttons'}],
    'controls': [
        {'default': {'type': 'image', 'texture': 'textures/ui/mpl/btn', 'layer': 1}},
        {'hover': {'type': 'image', 'texture': 'textures/ui/mpl/btn_hover', 'layer': 1}},
        {'pressed': {'type': 'image', 'texture': 'textures/ui/mpl/btn_press', 'layer': 1}},
        {'icon': {'type': 'image', 'size': [20, 20], 'anchor_from': 'left_middle', 'anchor_to': 'left_middle', 'offset': [6, 0], 'layer': 4,
                  'bindings': [c2('#form_button_texture', '#texture'), c2('#form_button_texture_file_system', '#texture_file_system'),
                               vis("(not ((#texture = '') or (#texture = 'loading')))")]}},
        {'t': {'type': 'label', 'text': '#form_button_text', 'property_bag': {'#font_type': 'classic'}, 'font_type': '#font_type', 'layer': 4, 'shadow': True, 'localize': False, 'color': [1, 1, 1], 'size': ['100% - 56px', 'default'],
               'text_alignment': 'center', 'bindings': [c2('#form_button_text'), {'binding_type': 'view', 'source_property_name': '#font_type', 'target_property_name': '#font_type'}]}}]}}]}
sf['mpl_form_in'] = {'anim_type': 'offset', 'easing': 'out_back', 'duration': 0.3, 'from': [0, 40], 'to': [0, 0]}
sf['mpl_form'] = {
    'type': 'panel', 'size': ['100%', '100%'], 'layer': 60,
    'bindings': [{'binding_name': TT}, vis(has(FORM_MARK, TT))],
    'controls': [
        {'shade': {'type': 'image', 'texture': 'textures/ui/Black', 'alpha': 0.45, 'size': ['100%', '100%'], 'layer': 0}},
        {'card': {'type': 'image', 'texture': 'textures/ui/mpl/card', 'size': [250, '100%c + 20px'], 'layer': 1, 'anims': ['@server_form.mpl_form_in'], 'controls': [{'st': {
            'type': 'stack_panel', 'orientation': 'vertical', 'size': [226, '100%c'], 'controls': [
                {'pt': {'type': 'panel', 'size': ['100%', 4]}},
                {'head': {'type': 'image', 'texture': 'textures/ui/mpl/head', 'size': ['100%', 24], 'layer': 3, 'controls': [
                    {'t': {'type': 'label', 'text': TT, 'size': ['100%', 'default'], 'text_alignment': 'center', 'layer': 4, 'shadow': True, 'localize': False, 'font_scale_factor': 1.2, 'color': [1, 1, 1], 'bindings': [{'binding_name': TT}]}}]}},
                {'pad0': {'type': 'panel', 'size': ['100%', 6]}},
                {'body': {'type': 'label', 'text': '#form_text', 'property_bag': {'#font_type': 'classic'}, 'font_type': '#font_type',  'size': ['100%', 'default'], 'text_alignment': 'center', 'layer': 2, 'shadow': True, 'localize': False, 'color': [0.78, 0.82, 0.95],
                          'bindings': [{'binding_name': '#form_text'}, {'binding_type': 'view', 'source_property_name': '#font_type', 'target_property_name': '#font_type'}]}},
                {'pad1': {'type': 'panel', 'size': ['100%', 6]}},
                {'buttons': {'type': 'stack_panel', 'orientation': 'vertical', 'size': ['100%', '100%c'], 'layer': 2,
                             'factory': {'name': 'buttons', 'control_ids': {'button': 'server_form.mpl_btn'}}, 'collection_name': 'form_buttons',
                             'bindings': [{'binding_name': '#form_button_contents', 'binding_name_override': '#collection_length'}]}}]}}]}}]}
# (スクロール式は動かなかったのでやめた。ボタンが多いメニューは main.js の paged() でページ送りにする)
lf = sf['long_form']['controls']
lf[0]['long_form@common_dialogs.main_panel_no_buttons']['bindings'][1] = vis(f"({hasnt(RANK_MARK, TT)} and {hasnt(FORM_MARK, TT)})")
if not any('mpl_form@server_form.mpl_form' in c for c in lf): lf.append({'mpl_form@server_form.mpl_form': {}})
json.dump(sf, open(os.path.join(UI, 'server_form.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(ROOT, 'mpl', 'banner_keys.txt'), 'w').write('\n'.join(KEYS))
print('ui ok', len(KEYS))

# ===== 文字を全部「英語設定と同じマイクラのドット文字」(unicode)にそろえる =====
# 日本語設定だと丸いフォントになるので、ラベルに font_type: unicode を直接つける(漢字・かなもドット文字になる)
FONT = 'unicode'
def unify(o):
    if isinstance(o, dict):
        pb = o.get('property_bag')
        if isinstance(pb, dict) and '#font_type' in pb:
            pb.pop('#font_type')
            if not pb: o.pop('property_bag')
            o['font_type'] = FONT
        if 'bindings' in o and isinstance(o['bindings'], list):
            o['bindings'] = [b for b in o['bindings'] if not (isinstance(b, dict) and b.get('target_property_name') == '#font_type')]
        if o.get('type') == 'label' or 'font_type' in o: o['font_type'] = FONT
        for v in o.values(): unify(v)
    elif isinstance(o, list):
        for v in o: unify(v)
for fn in ('hud_screen.json', 'server_form.json', 'scoreboards.json', 'chat_screen.json'):
    f = os.path.join(UI, fn)
    if not os.path.exists(f): continue
    d = json.load(open(f, encoding='utf-8')); unify(d)
    json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('font ok')
