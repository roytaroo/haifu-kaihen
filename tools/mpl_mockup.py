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
def text(d, xy, s, sc=1.0, col=(255, 255, 255), anchor='mt'):
    d.text((xy[0] * K + K, xy[1] * K + K), s, font=f(sc), fill=(40, 40, 40), anchor=anchor)
    d.text((xy[0] * K, xy[1] * K), s, font=f(sc), fill=col, anchor=anchor, stroke_width=1, stroke_fill=col)
def tw(s, sc=1.0): return f(sc).getlength(s) / K
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
    rows = ["▶① ★2 ●34 Daiki ◆", " ② ★1 ●51 Jack", " ③ ★1 ●12 Oracle", " ④ ★0 ● 9 Comet"]
    w = max(tw(r) for r in rows) + 6; h = 10 * (len(rows) + 1) + 2
    x, y = GW - 3 - w, GH - 3 - h
    paste(im, nine('side', w, h, (3, 3, 3, 3)), x, y)
    text(d, (x + w / 2, y + 1), "♛ TURN 3/10", 1, (255, 210, 80))
    for i, r in enumerate(rows): text(d, (x + 3, y + 11 + i * 10), r, 1, (255, 255, 255), 'lt')
TOP = 6 + 2  # 画面の上から(hud_title_text の offset 6 + 中の panel 2)
def scene_turn():
    im = bg(); d = ImageDraw.Draw(im)
    lg = Image.open(os.path.join(T, 'logo_yourturn.png')).convert('RGBA').resize((210 * K, 52 * K), Image.LANCZOS); paste(im, lg, GW / 2 - 105, TOP)
    s = "★まで あと 12 マス"; w = tw(s) + 16; paste(im, nine('toast', w, 16, (9, 9, 9, 9)), GW / 2 - w / 2, TOP + 54); text(d, (GW / 2, TOP + 58), s)
    sidebar(im, d); return im
def scene_ribbon():
    im = bg(); d = ImageDraw.Draw(im)
    s = "+3 ●"; w = tw(s, 1.3) + 44; h = 8 * 1.3 + 12
    paste(im, nine('ribbon_blue', w, h, (16, 7, 16, 7)), GW / 2 - w / 2, TOP); text(d, (GW / 2, TOP + 6), s, 1.3)
    s2 = "Daiki"; w2 = tw(s2) + 16; paste(im, nine('toast', w2, 16, (9, 9, 9, 9)), GW / 2 - w2 / 2, TOP + h + 4); text(d, (GW / 2, TOP + h + 8), s2)
    sidebar(im, d); return im
def scene_dj():
    im = bg(); d = ImageDraw.Draw(im)
    lines = ["タイムセール開始！ 今のターンはショップ全品半", "額！ 急げ急げ〜！"]
    h = 8 + 3 + 1 + 4 + 9 * len(lines) + 16; y = TOP + 122; x0 = GW / 2 - 20 - 145
    paste(im, nine('card', 290, h), x0, y)
    text(d, (x0 + 11, y + 8), "DJトシオ", 1, (255, 210, 77), 'lt')
    d.line([((x0 + 11) * K, (y + 19) * K), ((x0 + 279) * K, (y + 19) * K)], fill=(255, 255, 255, 90), width=K)
    for i, l in enumerate(lines): text(d, (x0 + 11, y + 24 + i * 9), l, 1, (255, 255, 255), 'lt')
    sidebar(im, d); return im
def scene_menu():
    im = bg(); sh = Image.new('RGBA', im.size, (0, 0, 0, 115)); im.alpha_composite(sh); d = ImageDraw.Draw(im)
    btns = ["すごろくを始める", "ミニゲーム勝ち抜き戦(5回)", "ミニゲームを1つ選んで遊ぶ", "ミニゲームを全部順番に遊ぶ", "ミニゲームの ON/OFF", "次のページ ▶"]
    h = 4 + 24 + 6 + 8 + 6 + 28 * len(btns) + 20; y0 = GH / 2 - h / 2
    paste(im, nine('card', 250, h, (12, 12, 12, 12)), GW / 2 - 125, y0)
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
