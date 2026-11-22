# 文字の中で使うアイコン(RP の font/glyph_E3.png、U+E300〜。512x512 = 1マス 32px でくっきり)
#   python3 tools/mpl_icons.py
#   ★ スター / コイン / 王冠 / 順位バッジ 1〜8 / 今の番の矢印 / クリスタル / サイコロ / 時計 / 上下の矢印 / ハート / いなずま / ふくろ
#   どれも 1マスの中で 26px・下を 30px にそろえる(漢字より少し小さい。はみ出さない)
import os, math
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp', 'font', 'glyph_E3.png')
NUMF = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
S = 8                 # 8倍で描いて縮める
B = 22 * S            # アイコンの大きさ
OUTL = (28, 20, 40, 255)

def canvas(): return Image.new('RGBA', (B, B));
def star_pts(cx, cy, r1, r2, n=5, rot=-90):
    return [(cx + math.cos(math.radians(rot + i * 180 / n)) * (r1 if i % 2 == 0 else r2), cy + math.sin(math.radians(rot + i * 180 / n)) * (r1 if i % 2 == 0 else r2)) for i in range(n * 2)]
def vgrad(w, h, top, bot):
    g = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(g)
    for y in range(h): t = y / max(1, h - 1); d.line([(0, y), (w, y)], fill=tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,))
    return g
def fill_shape(im, draw_mask, top, bot):
    m = Image.new('L', im.size); draw_mask(ImageDraw.Draw(m)); im.paste(vgrad(*im.size, top, bot), (0, 0), m)

def star():
    im = canvas(); c = B / 2
    ImageDraw.Draw(im).polygon(star_pts(c, c + 6, c - 2, c * 0.46), fill=OUTL)
    fill_shape(im, lambda d: d.polygon(star_pts(c, c + 6, c - 2 - 3 * S, c * 0.46 - 2 * S), fill=255), (255, 236, 120), (240, 150, 10))
    ImageDraw.Draw(im).polygon(star_pts(c - 2 * S, c - 1 * S, 2.6 * S, 1.1 * S, 4, -45), fill=(255, 255, 240, 230))
    return im
def coin():
    im = canvas(); d = ImageDraw.Draw(im); r = B / 2 - 2
    d.ellipse((2, 2, B - 2, B - 2), fill=OUTL)
    fill_shape(im, lambda d: d.ellipse((2 + 2.5 * S, 2 + 2.5 * S, B - 2 - 2.5 * S, B - 2 - 2.5 * S), fill=255), (255, 226, 90), (220, 130, 0))
    fill_shape(im, lambda d: d.ellipse((2 + 5.5 * S, 2 + 5.5 * S, B - 2 - 5.5 * S, B - 2 - 5.5 * S), fill=255), (235, 160, 10), (255, 214, 70))
    d.rounded_rectangle((B / 2 - 1.2 * S, B / 2 - 4.5 * S, B / 2 + 1.2 * S, B / 2 + 4.5 * S), S, fill=(255, 244, 180))
    d.arc((4 * S, 4 * S, B - 4 * S, B - 4 * S), 200, 250, fill=(255, 255, 240), width=int(1.4 * S))
    return im
def crown():
    im = canvas(); d = ImageDraw.Draw(im)
    pts = [(1.5 * S, 7 * S), (6 * S, 12 * S), (11 * S, 4 * S), (16 * S, 12 * S), (20.5 * S, 7 * S), (19 * S, 19 * S), (3 * S, 19 * S)]
    d.polygon(pts, fill=OUTL)
    inner = [(3.4 * S, 10 * S), (6.3 * S, 14.5 * S), (11 * S, 7.5 * S), (15.7 * S, 14.5 * S), (18.6 * S, 10 * S), (17.4 * S, 17.3 * S), (4.6 * S, 17.3 * S)]
    fill_shape(im, lambda d: d.polygon(inner, fill=255), (255, 236, 120), (230, 140, 0))
    for x in (6.3, 11, 15.7): d.ellipse(((x - 1.1) * S, 14.3 * S, (x + 1.1) * S, 16.5 * S), fill=(230, 40, 80))
    return im
BADGE = [((255, 230, 110), (225, 140, 0)), ((235, 240, 250), (150, 160, 180)), ((240, 170, 110), (170, 90, 40)), ((150, 200, 255), (60, 110, 210)),
         ((150, 200, 255), (60, 110, 210)), ((150, 200, 255), (60, 110, 210)), ((150, 200, 255), (60, 110, 210)), ((150, 200, 255), (60, 110, 210))]
def badge(n):
    im = canvas(); d = ImageDraw.Draw(im)
    d.ellipse((1, 1, B - 1, B - 1), fill=OUTL)
    top, bot = BADGE[n - 1]
    fill_shape(im, lambda d: d.ellipse((2.2 * S, 2.2 * S, B - 2.2 * S, B - 2.2 * S), fill=255), top, bot)
    f = ImageFont.truetype(NUMF, int(15 * S)); d.text((B / 2 + 0.3 * S, B / 2 + 0.6 * S), str(n), font=f, fill=(255, 255, 255), anchor='mm', stroke_width=int(1.6 * S), stroke_fill=OUTL)
    return im
def arrow():
    im = canvas(); d = ImageDraw.Draw(im)
    d.polygon([(3 * S, 2 * S), (20 * S, 11 * S), (3 * S, 20 * S)], fill=OUTL)
    fill_shape(im, lambda d: d.polygon([(5.5 * S, 6 * S), (16 * S, 11 * S), (5.5 * S, 16 * S)], fill=255), (255, 240, 130), (255, 170, 20))
    return im
def crystal():
    im = canvas(); d = ImageDraw.Draw(im)
    pts = [(11 * S, 1 * S), (19 * S, 8 * S), (11 * S, 21 * S), (3 * S, 8 * S)]
    d.polygon(pts, fill=OUTL)
    fill_shape(im, lambda d: d.polygon([(11 * S, 3.6 * S), (16.6 * S, 8.4 * S), (11 * S, 17.6 * S), (5.4 * S, 8.4 * S)], fill=255), (240, 190, 255), (150, 70, 230))
    d.polygon([(11 * S, 3.6 * S), (8 * S, 8.4 * S), (11 * S, 8.4 * S)], fill=(255, 240, 255, 220))
    return im
def dice():
    im = canvas(); d = ImageDraw.Draw(im)
    d.rounded_rectangle((1, 1, B - 1, B - 1), 5 * S, fill=OUTL)
    fill_shape(im, lambda d: d.rounded_rectangle((2.4 * S, 2.4 * S, B - 2.4 * S, B - 2.4 * S), 4 * S, fill=255), (255, 255, 255), (205, 210, 225))
    for x, y in ((7, 7), (15, 15), (11, 11)): d.ellipse(((x - 1.7) * S, (y - 1.7) * S, (x + 1.7) * S, (y + 1.7) * S), fill=(230, 40, 70))
    return im
def clock():
    im = canvas(); d = ImageDraw.Draw(im)
    d.ellipse((1, 1, B - 1, B - 1), fill=OUTL)
    fill_shape(im, lambda d: d.ellipse((2.4 * S, 2.4 * S, B - 2.4 * S, B - 2.4 * S), fill=255), (255, 255, 255), (200, 210, 230))
    d.line([(11 * S, 11 * S), (11 * S, 5 * S)], fill=OUTL, width=int(2 * S)); d.line([(11 * S, 11 * S), (15.5 * S, 13 * S)], fill=OUTL, width=int(2 * S))
    return im
def tri(up, col):
    im = canvas(); d = ImageDraw.Draw(im)
    p = [(11 * S, 3 * S), (20 * S, 18 * S), (2 * S, 18 * S)] if up else [(2 * S, 4 * S), (20 * S, 4 * S), (11 * S, 19 * S)]
    d.polygon(p, fill=OUTL)
    q = [(11 * S, 6.5 * S), (17 * S, 16.2 * S), (5 * S, 16.2 * S)] if up else [(5 * S, 5.8 * S), (17 * S, 5.8 * S), (11 * S, 15.5 * S)]
    fill_shape(im, lambda d: d.polygon(q, fill=255), *col)
    return im
def heart():
    im = canvas(); d = ImageDraw.Draw(im)
    def h(d, k, fill):
        r = 5.2 * S - k
        d.ellipse((6 * S - r, 8 * S - r, 6 * S + r, 8 * S + r), fill=fill); d.ellipse((16 * S - r, 8 * S - r, 16 * S + r, 8 * S + r), fill=fill)
        d.polygon([(0.8 * S + k, 9.5 * S), (21.2 * S - k, 9.5 * S), (11 * S, 20.5 * S - k * 1.4)], fill=fill)
    h(d, 0, OUTL); fill_shape(im, lambda d: h(d, 2.2 * S, 255), (255, 120, 150), (210, 20, 60))
    return im
def bolt():
    im = canvas(); d = ImageDraw.Draw(im)
    p = [(13 * S, 1 * S), (3 * S, 12.5 * S), (10 * S, 12.5 * S), (8 * S, 21 * S), (19 * S, 8.5 * S), (12 * S, 8.5 * S)]
    d.polygon(p, fill=OUTL)
    fill_shape(im, lambda d: d.polygon([(11.6 * S, 4.5 * S), (6.2 * S, 11 * S), (12 * S, 11 * S), (10.5 * S, 17 * S), (15.8 * S, 10 * S), (10 * S, 10 * S)], fill=255), (255, 250, 150), (255, 190, 0))
    return im
def bag():
    im = canvas(); d = ImageDraw.Draw(im)
    d.rounded_rectangle((2 * S, 6 * S, 20 * S, 21 * S), 5 * S, fill=OUTL); d.polygon([(7 * S, 1 * S), (15 * S, 1 * S), (13 * S, 7 * S), (9 * S, 7 * S)], fill=OUTL)
    fill_shape(im, lambda d: d.rounded_rectangle((4.2 * S, 8.2 * S, 17.8 * S, 18.8 * S), 4 * S, fill=255), (230, 180, 120), (170, 110, 60))
    d.rectangle((8 * S, 6 * S, 14 * S, 8.2 * S), fill=(230, 60, 90))
    return im

ICONS = [star(), coin(), crown(), *[badge(n) for n in range(1, 9)], arrow(), crystal(), dice(), clock(),
         tri(True, ((150, 255, 150), (30, 170, 60))), tri(False, ((255, 150, 150), (200, 30, 40))), heart(), bolt(), bag()]
page = Image.new('RGBA', (256, 256))   # 16px のます(512 にすると画面で倍の大きさになる)
for i, ic in enumerate(ICONS):
    sm = ic.resize((12, 12), Image.LANCZOS)
    page.alpha_composite(sm, ((i % 16) * 16 + 2, (i // 16) * 16 + 14 - 12))
page.save(OUT)
prev = Image.new('RGBA', (len(ICONS) * 34, 34), (60, 70, 100, 255))
for i, ic in enumerate(ICONS): prev.alpha_composite(ic.resize((32, 32), Image.LANCZOS), (i * 34 + 1, 1))
prev.resize((prev.width * 2, prev.height * 2), Image.NEAREST).save(os.path.join(ROOT, 'mpl', 'icons_preview.png'))
print('icons', len(ICONS))
