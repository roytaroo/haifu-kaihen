# 紹介用のイメージ画像(キービジュアル)を作る
#   python3 tools/mpl_keyart.py → mpl/keyart.png(1920x1080)と mpl/keyart_square.png(1080x1080)
#   素材: ロゴ・ボードの見本(mpl_board.py)・BOT とDJ のスキン・幽霊船の見本・アイコン・マスの台・順位の文字
import os, sys, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp')
JP = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
EN = '/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf'
random.seed(3)

# ---------- スキンを斜め前から描く(上・前・左がわの3面、奥から順にぬる) ----------
def homography(src, dst):
    A = []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
    return np.linalg.solve(np.array(A, float), np.array([c for p in src for c in p], float)).tolist()
def quad(canvas, tex, box, pts, shade=1.0):
    u, v, w, h = box
    if w <= 0 or h <= 0: return
    face = tex.crop((u, v, u + w, v + h)).resize((w * 16, h * 16), Image.NEAREST)
    if shade != 1.0:
        a = face.getchannel('A'); face = Image.eval(face.convert('RGB'), lambda c: int(c * shade)).convert('RGBA'); face.putalpha(a)
    W, H = face.size
    co = homography([(0, 0), (W, 0), (W, H), (0, H)], pts)
    canvas.alpha_composite(face.transform(canvas.size, Image.PERSPECTIVE, co, Image.NEAREST))
def skin_figure(tex, S=13, pose='stand', flip=False):
    tex = tex.convert('RGBA')
    ex, ey, ez = (0.94, 0.30), (0, -1), (-0.42, 0.33)       # x(右)・y(上)・z(手前)が画面でどちらへ進むか
    if flip: ex, ez = (-0.94, 0.30), (0.42, 0.33)
    W, H = 46 * S, 48 * S; ox, oy = W / 2, H - 9 * S
    P = lambda x, y, z: (ox + (x * ex[0] + z * ez[0]) * S, oy + (y * ey[1] + x * ex[1] + z * ez[1]) * S)
    cv = Image.new('RGBA', (int(W), int(H)))
    def box(x0, y0, z0, w, h, d, uv, inf=0.0, flipv=False):
        x0 -= inf; y0 -= inf; z0 -= inf; w += 2 * inf; h += 2 * inf; d += 2 * inf
        u, v = uv; bw, bh, bd = int(round(w - 2 * inf)), int(round(h - 2 * inf)), int(round(d - 2 * inf))
        x1, y1, z1 = x0 + w, y0 + h, z0 + d
        top = (u + bd, v, bw, bd); front = (u + bd, v + bd, bw, bh); side = (u + bd + bw, v + bd, bd, bh) if not flip else (u, v + bd, bd, bh)
        if flipv: top = (u + bd + bw, v, bw, bd)
        sx = x1 if not flip else x0
        if not flipv: quad(cv, tex, top, [P(x0, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y1, z1)], 1.08)
        fp = [P(x0, y1, z1), P(x1, y1, z1), P(x1, y0, z1), P(x0, y0, z1)]
        if flipv: fp = [fp[3], fp[2], fp[1], fp[0]][::1]; fp = [P(x1, y0, z1), P(x0, y0, z1), P(x0, y1, z1), P(x1, y1, z1)]
        quad(cv, tex, front, fp, 1.0)
        sp = [P(sx, y1, z1), P(sx, y1, z0), P(sx, y0, z0), P(sx, y0, z1)]
        if flipv: sp = [P(sx, y0, z1), P(sx, y0, z0), P(sx, y1, z0), P(sx, y1, z1)]
        quad(cv, tex, side, sp, 0.78)
    up = pose == 'cheer'
    parts = [  # (並べる順のための奥ゆき, 箱)
        ('rleg', lambda: (box(-4, 0, -2, 4, 12, 4, (0, 16)), box(-4, 0, -2, 4, 12, 4, (0, 32), 0.25))),
        ('lleg', lambda: (box(0, 0, -2, 4, 12, 4, (16, 48)), box(0, 0, -2, 4, 12, 4, (0, 48), 0.25))),
        ('rarm', lambda: (box(-8, 22 if up else 12, -2, 4, 12, 4, (40, 16), flipv=up), box(-8, 22 if up else 12, -2, 4, 12, 4, (40, 32), 0.25, flipv=up))),
        ('body', lambda: (box(-4, 12, -2, 8, 12, 4, (16, 16)), box(-4, 12, -2, 8, 12, 4, (16, 32), 0.25))),
        ('larm', lambda: (box(4, 22 if up else 12, -2, 4, 12, 4, (32, 48), flipv=up), box(4, 22 if up else 12, -2, 4, 12, 4, (48, 48), 0.25, flipv=up))),
        ('head', lambda: (box(-4, 24, -4, 8, 8, 8, (0, 0)), box(-4, 24, -4, 8, 8, 8, (32, 0), 0.5))),
    ]
    order = ['rarm', 'rleg', 'lleg', 'body', 'larm', 'head'] if not flip else ['larm', 'lleg', 'rleg', 'body', 'rarm', 'head']
    d = dict(parts)
    for k in order: d[k]()
    return cv.crop(cv.getbbox())

def shadow(w, h):
    im = Image.new('RGBA', (w, h)); ImageDraw.Draw(im).ellipse((0, 0, w - 1, h - 1), fill=(10, 20, 50, 110)); return im.filter(ImageFilter.GaussianBlur(h / 5))
def text_img(s, font, size, fill, stroke, sw, shadow_c=(20, 10, 40, 150)):
    f = ImageFont.truetype(font, size); bb = f.getbbox(s, stroke_width=sw)
    im = Image.new('RGBA', (bb[2] - bb[0] + 20, bb[3] - bb[1] + 24)); d = ImageDraw.Draw(im)
    d.text((10 - bb[0] + 3, 10 - bb[1] + 6), s, font=f, fill=shadow_c, stroke_width=sw, stroke_fill=shadow_c)
    d.text((10 - bb[0], 10 - bb[1]), s, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)
    return im
def pill(text, bg, fg=(255, 255, 255), size=34):
    f = ImageFont.truetype(JP, size); w = int(f.getlength(text)) + 56; h = size + 30
    im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 4, w - 1, h - 1), h // 2, fill=(20, 16, 50, 120)); d.rounded_rectangle((0, 0, w - 1, h - 5), h // 2, fill=bg + (255,), outline=(255, 255, 255, 255), width=3)
    d.text((w / 2, (h - 5) / 2), text, font=f, fill=fg, anchor='mm', stroke_width=1, stroke_fill=fg)
    return im

def compose(W, H, square=False):
    cv = Image.new('RGBA', (W, H))
    # 空: 上は夕方のピンク → 水色、下は海
    g = np.zeros((H, W, 4), np.uint8)
    for y in range(H):
        t = y / H
        c = np.array([255, 170, 210]) * (1 - t) ** 2 + np.array([120, 200, 255]) * (1 - (1 - t) ** 2) if t < 0.55 else np.array([40, 110, 190]) * 1.0
        g[y, :, :3] = c; g[y, :, 3] = 255
    cv = Image.fromarray(g, 'RGBA')
    d = ImageDraw.Draw(cv)
    for _ in range(14):   # 雲
        x, y, r = random.randint(0, W), random.randint(int(H * 0.05), int(H * 0.4)), random.randint(40, 110)
        cl = Image.new('RGBA', (r * 5, r * 3)); cd = ImageDraw.Draw(cl)
        for k in range(5): cd.ellipse((r * 0.5 + k * r * 0.6, r - (k % 2) * r * 0.3, r * 0.5 + k * r * 0.6 + r * 1.3, r * 2.3), fill=(255, 255, 255, 140))
        cv.alpha_composite(cl.filter(ImageFilter.GaussianBlur(10)), (x - r * 2, y - r))
    # 光の筋(ロゴのうしろ)
    rays = Image.new('RGBA', (W, H)); rd = ImageDraw.Draw(rays); cx, cy = W / 2, H * (0.22 if not square else 0.18)
    for k in range(18):
        a0, a1 = k * 20, k * 20 + 9
        rd.polygon([(cx, cy), (cx + math.cos(math.radians(a0)) * W, cy + math.sin(math.radians(a0)) * W), (cx + math.cos(math.radians(a1)) * W, cy + math.sin(math.radians(a1)) * W)], fill=(255, 255, 255, 34))
    cv.alpha_composite(rays.filter(ImageFilter.GaussianBlur(3)))
    # 島(ボードの見本の島の部分だけ、海の色を消して置く)
    bd = Image.open(os.path.join(ROOT, 'mpl', 'preview_board.png')).convert('RGBA').crop((20, 260, 1460, 1330))
    a = np.array(bd); sea = np.array([42, 106, 168])
    diff = np.abs(a[:, :, :3].astype(int) - sea).sum(axis=2); a[:, :, 3] = np.where(diff < 30, 0, 255); bd = Image.fromarray(a)
    iw = int(W * (0.62 if not square else 0.92)); bd = bd.resize((iw, int(bd.height * iw / bd.width)), Image.LANCZOS)
    iy = int(H * (0.30 if not square else 0.34))
    cv.alpha_composite(bd.filter(ImageFilter.GaussianBlur(0.4)), ((W - iw) // 2, iy))
    # 幽霊船(右奥の海)
    gs = Image.open(os.path.join(ROOT, 'mpl', 'preview_ghostship.png')).convert('RGBA'); gs = gs.crop(gs.getbbox())
    gw = int(W * (0.13 if not square else 0.2)); gs = gs.resize((gw, int(gs.height * gw / gs.width)), Image.LANCZOS)
    gs.putalpha(gs.getchannel('A').point(lambda v: int(v * 0.92)))
    cv.alpha_composite(gs, (int(W * (0.64 if not square else 0.66)), int(H * (0.27 if not square else 0.33))))
    # 下を少し暗く(キャラと文字を目立たせる)
    vg = Image.new('RGBA', (W, H)); vd = ImageDraw.Draw(vg)
    for y in range(int(H * 0.55), H): vd.line([(0, y), (W, y)], fill=(16, 18, 60, int(170 * ((y - H * 0.55) / (H * 0.45)) ** 1.6)))
    cv.alpha_composite(vg)
    # ロゴ
    lg = Image.open(os.path.join(RP, 'textures', 'ui', 'mpl', 'logo_venus.png')).convert('RGBA'); lg = lg.crop(lg.getbbox())
    lw = int(W * (0.44 if not square else 0.74)); lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    glow = Image.new('RGBA', lg.size, (255, 255, 255, 0)); glow.putalpha(lg.getchannel('A').filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.8)))
    lx, ly = (W - lw) // 2, int(H * (0.03 if not square else 0.03))
    cv.alpha_composite(glow, (lx, ly)); cv.alpha_composite(lg, (lx, ly))
    # キャラ(手前に横一列。真ん中は両手を上げる)
    tx = lambda n: Image.open(os.path.join(RP, 'textures', 'entity', 'mpl_bots', f'{n}.png'))
    cast = [('comet', 'stand', False), ('oracle', 'stand', False), ('jack', 'stand', False), ('dj', 'stand', True), ('splash', 'stand', True), ('widow', 'stand', True)]
    if square: cast = [cast[2], cast[3]]
    S = 13 if not square else 12
    figs = []
    for n, pose, fl in cast:
        t = Image.open(os.path.join(ROOT, 'mpl', 'assets', 'dj_skin.png')) if n == 'dj' else tx(n)
        figs.append(skin_figure(t, S, pose, fl))
    base = H - int(H * 0.04); half = len(figs) // 2
    target = H * (0.40 if not square else 0.30)
    xs = ([0.06, 0.15, 0.235, 0.775, 0.86, 0.945] if not square else [0.10, 0.90])
    for i, f in enumerate(figs):
        k = target / f.height * (1.1 if i in (half - 1, half) else 0.95)
        f = f.resize((int(f.width * k), int(f.height * k)), Image.NEAREST)
        cx = W * xs[i]; by = base - (0 if i in (half - 1, half) else int(H * 0.03))
        sh = shadow(int(f.width * 0.9), 36); cv.alpha_composite(sh, (int(cx - sh.width / 2), by - 20))
        cv.alpha_composite(f, (int(cx - f.width / 2), by - f.height))
    # 浮かぶスター・コイン・マスの台
    import importlib.util
    spec = importlib.util.spec_from_file_location('icons', os.path.join(ROOT, 'tools', 'mpl_icons.py')); ic = importlib.util.module_from_spec(spec)
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(ic)
    for (fx, fy, k, s) in ([(0.08, 0.10, 'star', 120), (0.90, 0.12, 'star', 90), (0.16, 0.30, 'coin', 70), (0.84, 0.33, 'coin', 80), (0.05, 0.42, 'coin', 56), (0.94, 0.52, 'star', 70)] if not square else
                           [(0.08, 0.06, 'star', 110), (0.90, 0.08, 'star', 90), (0.10, 0.36, 'coin', 70), (0.88, 0.40, 'coin', 70)]):
        im = (ic.star() if k == 'star' else ic.coin()).resize((s, s), Image.LANCZOS).rotate(random.randint(-20, 20), Image.BICUBIC, expand=True)
        cv.alpha_composite(im, (int(W * fx - im.width / 2), int(H * fy - im.height / 2)))
    # 文字: キャッチコピーと特ちょう
    cp = text_img('女神の島で、すごろく × ミニゲーム！', JP, 44 if not square else 32, (255, 255, 255), (60, 30, 120), 7)
    cy2 = int(H * (0.78 if not square else 0.76))
    pw = max(cp.width, 2 * 260) + 60; ph = int(H * 0.22) if not square else int(H * 0.21)
    panel = Image.new('RGBA', (pw, ph)); ImageDraw.Draw(panel).rounded_rectangle((0, 0, pw - 1, ph - 1), 28, fill=(18, 14, 50, 175), outline=(255, 255, 255, 90), width=2)
    cv.alpha_composite(panel, ((W - pw) // 2, cy2 - 14))
    cv.alpha_composite(cp, ((W - cp.width) // 2, cy2))
    chips = [('最大8人', (240, 80, 120)), ('BOT 10人', (70, 140, 240)), ('ミニゲーム 30種', (250, 160, 30)), ('噴火・満潮・幽霊船', (140, 80, 220))]
    ims = [pill(t, c, size=26 if not square else 22) for t, c in chips]
    rows = [ims[:2], ims[2:]]
    yy = cy2 + cp.height + 4
    for row in rows:
        tw = sum(i.width for i in row) + 18 * (len(row) - 1); x = (W - tw) // 2
        for i in row: cv.alpha_composite(i, (x, yy)); x += i.width + 18
        yy += row[0].height + 10
    # 右下: Minecraft 統合版のワールド
    ft = text_img('Minecraft 統合版 ワールド', JP, 26, (255, 255, 255), (30, 20, 60), 3)
    if not square: cv.alpha_composite(ft, (W - ft.width - 24, 18))
    return cv.convert('RGB')

compose(1920, 1080).save(os.path.join(ROOT, 'mpl', 'keyart.png'))
compose(1080, 1080, square=True).save(os.path.join(ROOT, 'mpl', 'keyart_square.png'))
print('keyart ok')
