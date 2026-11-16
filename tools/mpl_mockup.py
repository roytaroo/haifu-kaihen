# 画面の見本(だいたいの見た目): よくある画面の大きさ(GUI 427x240、3倍)に、RP の部品を JSON と同じ大きさ・位置で並べる
#   python3 tools/mpl_mockup.py → mpl/mockup.png(4場面: ターンのはじめ / 帯とお知らせ / DJ のせりふ / メニュー)
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp', 'textures', 'ui', 'mpl')
K = 3; GW, GH = 427, 240
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
def f(sc): return ImageFont.truetype(FONT, int(8 * sc * K))
import json as _j
def nine(name, w, h, sl=None):
    # RP の .json(base_size・nineslice_size)どおりに: 角は画面の大きさで描く
    im = Image.open(os.path.join(T, name + '.png')).convert('RGBA'); W, H = im.size
    meta = _j.load(open(os.path.join(T, name + '.json'))); bw = meta['base_size'][0]; sc = W / bw
    ns = meta['nineslice_size']; ns = [ns] * 4 if isinstance(ns, int) else ns
    l, t, r, b = [int(v * sc) for v in ns]; s = K / sc
    out = Image.new('RGBA', (int(w * K), int(h * K)))
    def part(box, size):
        c = im.crop(box)
        if c.width < 1 or c.height < 1: raise SystemExit(f'{name}: 角が大きすぎて真ん中がない')
        return c.resize((max(1, int(size[0])), max(1, int(size[1]))), Image.LANCZOS)
    ow, oh = out.size; L, Tt, Rr, B = l * s, t * s, r * s, b * s
    for (sx0, sx1, dx0, dx1) in ((0, l, 0, L), (l, W - r, L, ow - Rr), (W - r, W, ow - Rr, ow)):
        for (sy0, sy1, dy0, dy1) in ((0, t, 0, Tt), (t, H - b, Tt, oh - B), (H - b, H, oh - B, oh)):
            if dx1 > dx0 and dy1 > dy0: out.paste(part((sx0, sy0, sx1, sy1), (dx1 - dx0, dy1 - dy0)), (int(dx0), int(dy0)))
    return out
# 文字: ふつうの字はフォント、U+E2xx / U+E3xx は RP の glyph ページの絵(ゲームと同じ: 1マス = 文字の高さ、幅は絵の右はしまで)
FD = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp', 'font')
_pages = {}
def glyph(ch):
    pg = ord(ch) >> 8; k = ord(ch) & 255
    if pg not in _pages: _pages[pg] = Image.open(os.path.join(FD, f'glyph_{pg:02X}.png')).convert('RGBA')
    P = _pages[pg]; c = P.width // 16
    g = P.crop(((k % 16) * c, (k // 16) * c, (k % 16) * c + c, (k // 16) * c + c)); bb = g.getbbox()
    return g, ((bb[2] if bb else c // 2) + c // 16) / c
def segs(s):
    out, buf = [], ''
    for ch in s:
        if 0xE200 <= ord(ch) <= 0xE3FF:
            if buf: out.append(buf); buf = ''
            out.append(ch)
        else: buf += ch
    if buf: out.append(buf)
    return out
def tw(s, sc=1.0):
    w = 0
    for g in segs(s): w += glyph(g)[1] * 8 * sc if len(g) == 1 and ord(g) >= 0xE200 else f(sc).getlength(g) / K
    return w
def text(d, xy, s, sc=1.0, col=(255, 255, 255), anchor='mt'):
    W = tw(s, sc); x = xy[0] - (W / 2 if anchor[0] == 'm' else 0); y = xy[1]
    im = d._image
    for g in segs(s):
        if len(g) == 1 and ord(g) >= 0xE200:
            gi, wf = glyph(g); sz = int(8 * sc * K); gi = gi.resize((sz, sz), Image.LANCZOS)
            im.alpha_composite(gi, (int(x * K), int((y - 0.5 * sc) * K))); x += wf * 8 * sc
        else:
            d.text((x * K + K, y * K + K), g, font=f(sc), fill=(40, 40, 40), anchor='lt')
            d.text((x * K, y * K), g, font=f(sc), fill=col, anchor='lt', stroke_width=1, stroke_fill=col); x += f(sc).getlength(g) / K
def bg():
    im = Image.new('RGBA', (GW * K, GH * K)); d = ImageDraw.Draw(im)
    for y in range(GH * K): d.line([(0, y), (GW * K, y)], fill=(120 + y // 30, 180 + y // 40, 240) if y < GH * K * 0.55 else (86, 160, 70))
    for x in range(0, GW * K, 60): d.rectangle((x, GH * K * 0.55, x + 30, GH * K * 0.55 + 8), fill=(70, 140, 60))
    # 人(画面の真ん中あたり)
    cx, cy = GW * K // 2, int(GH * K * 0.62)
    d.rectangle((cx - 24, cy - 120, cx + 24, cy - 72), fill=(200, 150, 110)); d.rectangle((cx - 24, cy - 72, cx + 24, cy), fill=(60, 170, 200)); d.rectangle((cx - 24, cy, cx + 24, cy + 60), fill=(50, 60, 150))
    return im
def paste(im, part, x, y): im.alpha_composite(part, (int(x * K), int(y * K)))
def sidebar(im, d):
    B = lambda n: chr(0xE302 + n)
    rows = [(B(1) + " \ue3002 \ue30134  ", "Daiki", (255, 220, 80), "\ue30b \ue201"), (B(2) + " \ue3001 \ue30151  ", "Jack", (255, 255, 255), ""),
            (B(3) + " \ue3001 \ue30112  ", "Oracle", (130, 230, 255), ""), (B(4) + " \ue3000 \ue30109  ", "Comet", (255, 150, 150), "")]
    w = max(tw(a + b + c) for a, b, _, c in rows) + 16; h = 18 + 11 * len(rows) + 8
    x, y = GW - 3 - w, GH - 3 - h
    paste(im, nine('side', w, h), x, y)
    text(d, (x + w / 2, y + 5), "TURN 3 / 10", 1, (255, 255, 255))
    paste(im, Image.open(os.path.join(T, "line.png")).convert("RGBA").resize((int((w - 20) * K), K)), x + 10, y + 15)
    for i, (a, b, c, e) in enumerate(rows):
        yy = y + 18 + i * 11; text(d, (x + 8, yy), a, 1, (255, 255, 255), 'lt'); xx = x + 8 + tw(a)
        text(d, (xx, yy), b, 1, c, 'lt'); text(d, (xx + tw(b), yy), e, 1, (255, 255, 255), 'lt')
TOP = 6 + 2  # 画面の上から(hud_title_text の offset 6 + 中の panel 2)
def scene_turn():
    im = bg(); d = ImageDraw.Draw(im)
    lg = Image.open(os.path.join(T, 'logo_yourturn.png')).convert('RGBA').resize((210 * K, 52 * K), Image.LANCZOS); paste(im, lg, GW / 2 - 105, TOP)
    s = "\ue300まで あと 12 マス"; w = tw(s) + 16; paste(im, nine('toast', w, 16), GW / 2 - w / 2, TOP + 54); text(d, (GW / 2, TOP + 58), s)
    sidebar(im, d); return im
def scene_ribbon():
    im = bg(); d = ImageDraw.Draw(im)
    t, sub = "+3 \ue301", "Daiki"
    w = max(tw(t, 1.3), tw(sub, 0.9)) + 40
    paste(im, nine('ribbon_blue', w, 34), GW / 2 - w / 2, TOP); text(d, (GW / 2, TOP + 5), t, 1.3); text(d, (GW / 2, TOP + 20), sub, 0.9, (209, 219, 247))
    t2 = "MIRROR!"; w2 = tw(t2, 1.3) + 40
    paste(im, nine('ribbon_purple', w2, 22), GW / 2 - w2 / 2, TOP + 60); text(d, (GW / 2, TOP + 66), t2, 1.3)
    sidebar(im, d); return im
def scene_dj():
    im = bg(); d = ImageDraw.Draw(im)
    lines = ["タイムセール開始！ 今のターンはショップ全品半額！", "急げ急げ〜！"]
    h = 9 * len(lines) + 20; y = TOP + 128; x0 = GW / 2 - 150
    paste(im, nine('card', 300, h), x0, y)
    pw = tw("DJトシオ") + 16; paste(im, nine('plate', pw, 13), x0 + 10, y - 7); text(d, (x0 + 18, y - 4.5), "DJトシオ", 1, (255, 255, 255), 'lt')
    for i, l in enumerate(lines): text(d, (x0 + 12, y + 12 + i * 9), l, 1, (255, 255, 255), 'lt')
    sidebar(im, d); return im
def scene_menu():
    im = bg(); sh = Image.new('RGBA', im.size, (0, 0, 0, 115)); im.alpha_composite(sh); d = ImageDraw.Draw(im)
    btns = ["すごろくを始める", "ミニゲーム勝ち抜き戦(5回)", "ミニゲームを1つ選んで遊ぶ", "ミニゲームを全部順番に遊ぶ", "ミニゲームの ON/OFF", "次のページ ▶"]
    h = 4 + 24 + 6 + 8 + 6 + 28 * len(btns) + 20; y0 = GH / 2 - h / 2
    paste(im, nine('card', 250, h), GW / 2 - 125, y0)
    y = y0 + 10 + 4; paste(im, nine('head', 226, 24), GW / 2 - 113, y); text(d, (GW / 2, y + 12), "VENUS PARTY", 1.2, (255, 255, 255)); y += 24 + 6
    text(d, (GW / 2, y), "何をする？  (1/2)", 1, (199, 209, 242)); y += 14
    for i, b in enumerate(btns):
        paste(im, nine('btn_hover' if i == 0 else 'btn', 218, 25, (6, 6, 6, 6)), GW / 2 - 109, y + 1.5); text(d, (GW / 2, y + 12), b); y += 28
    return im
os.makedirs(os.path.join(ROOT, 'mpl'), exist_ok=True)
sc = [scene_turn(), scene_ribbon(), scene_dj(), scene_menu()]
W, H = sc[0].size; out = Image.new('RGB', (W * 2 + 20, H * 2 + 20), (20, 20, 20))
for i, s in enumerate(sc): out.paste(s.convert('RGB'), ((i % 2) * (W + 20), (i // 2) * (H + 20)))
out = out.resize((out.width // 2, out.height // 2), Image.LANCZOS); out.save(os.path.join(ROOT, 'mpl', 'mockup.png')); print('ok', out.size)
