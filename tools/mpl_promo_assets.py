# 紹介画像の素材(mpl/promo/assets/)
#   python3 tools/mpl_promo_assets.py
#   キャラの立ち絵(斜め前から・こい縁つき)、顔のアイコン(頭の立方体)、大きいアイコン(スター・コイン・サイコロ)、ぼかした島
import os, sys, math, json, importlib.util, io, contextlib
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp')
OUT = os.path.join(ROOT, 'mpl', 'promo', 'assets'); os.makedirs(OUT, exist_ok=True)
OUTLINE = (14, 10, 36, 255)

def homography(src, dst):
    A = []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
    return np.linalg.solve(np.array(A, float), np.array([c for p in src for c in p], float)).tolist()
def quad(cv, tex, box, pts, shade=1.0):
    u, v, w, h = box
    face = tex.crop((u, v, u + w, v + h)).resize((w * 16, h * 16), Image.NEAREST)
    if shade != 1.0:
        a = face.getchannel('A'); face = Image.eval(face.convert('RGB'), lambda c: int(c * shade)).convert('RGBA'); face.putalpha(a)
    W, H = face.size
    cv.alpha_composite(face.transform(cv.size, Image.PERSPECTIVE, homography([(0, 0), (W, 0), (W, H), (0, H)], pts), Image.NEAREST))

def render(tex, S=22, flip=False, only_head=False):
    tex = tex.convert('RGBA')
    ex, ez = ((0.94, 0.30), (-0.42, 0.33)) if not flip else ((-0.94, 0.30), (0.42, 0.33))
    W, H = 50 * S, 52 * S; ox, oy = W / 2, H - 10 * S
    P = lambda x, y, z: (ox + (x * ex[0] + z * ez[0]) * S, oy + (-y + x * ex[1] + z * ez[1]) * S)
    cv = Image.new('RGBA', (int(W), int(H)))
    def box(x0, y0, z0, w, h, d, uv, inf=0.0):
        bw, bh, bd = w, h, d
        x0 -= inf; y0 -= inf; z0 -= inf; w += 2 * inf; h += 2 * inf; d += 2 * inf
        u, v = uv; x1, y1, z1 = x0 + w, y0 + h, z0 + d
        top = (u + bd, v, bw, bd); front = (u + bd, v + bd, bw, bh)
        side = (u + bd + bw, v + bd, bd, bh) if not flip else (u, v + bd, bd, bh); sx = x1 if not flip else x0
        quad(cv, tex, top, [P(x0, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y1, z1)], 1.06)
        quad(cv, tex, front, [P(x0, y1, z1), P(x1, y1, z1), P(x1, y0, z1), P(x0, y0, z1)], 1.0)
        quad(cv, tex, side, [P(sx, y1, z1), P(sx, y1, z0), P(sx, y0, z0), P(sx, y0, z1)], 0.74)
    parts = {
        'rleg': lambda: (box(-4, 0, -2, 4, 12, 4, (0, 16)), box(-4, 0, -2, 4, 12, 4, (0, 32), 0.25)),
        'lleg': lambda: (box(0, 0, -2, 4, 12, 4, (16, 48)), box(0, 0, -2, 4, 12, 4, (0, 48), 0.25)),
        'rarm': lambda: (box(-8, 12, -2, 4, 12, 4, (40, 16)), box(-8, 12, -2, 4, 12, 4, (40, 32), 0.25)),
        'body': lambda: (box(-4, 12, -2, 8, 12, 4, (16, 16)), box(-4, 12, -2, 8, 12, 4, (16, 32), 0.25)),
        'larm': lambda: (box(4, 12, -2, 4, 12, 4, (32, 48)), box(4, 12, -2, 4, 12, 4, (48, 48), 0.25)),
        'head': lambda: (box(-4, 24, -4, 8, 8, 8, (0, 0)), box(-4, 24, -4, 8, 8, 8, (32, 0), 0.5)),
    }
    order = ['head'] if only_head else (['rarm', 'rleg', 'lleg', 'body', 'larm', 'head'] if not flip else ['larm', 'lleg', 'rleg', 'body', 'rarm', 'head'])
    for k in order: parts[k]()
    return cv.crop(cv.getbbox())

def outlined(im, r):
    pad = r * 2 + 2
    big = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2)); big.alpha_composite(im, (pad, pad))
    a = big.getchannel('A').point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(r * 2 + 1))
    o = Image.new('RGBA', big.size, OUTLINE); o.putalpha(a)
    o.alpha_composite(big)
    return o.crop(o.getbbox())

BOTS = ['jack', 'humming', 'widow', 'splash', 'oracle', 'byte', 'shade', 'jester', 'replica', 'comet']
for n in BOTS + ['dj']:
    t = Image.open(os.path.join(ROOT, 'mpl', 'assets', 'dj_skin.png') if n == 'dj' else os.path.join(RP, 'textures', 'entity', 'mpl_bots', f'{n}.png'))
    outlined(render(t, 22), 9).save(os.path.join(OUT, f'char_{n}.png'))
    outlined(render(t, 22, flip=True), 9).save(os.path.join(OUT, f'char_{n}_r.png'))
    outlined(render(t, 26, only_head=True), 8).save(os.path.join(OUT, f'head_{n}.png'))
# 大きいアイコン(tools/mpl_icons.py の形を大きく)
spec = importlib.util.spec_from_file_location('icons', os.path.join(ROOT, 'tools', 'mpl_icons.py')); ic = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(ic)
for k, f in (('star', ic.star), ('coin', ic.coin), ('dice', ic.dice), ('crown', ic.crown), ('crystal', ic.crystal)):
    f().resize((256, 256), Image.LANCZOS).save(os.path.join(OUT, f'icon_{k}.png'))
# 島(海の色をぬいて)
bd = Image.open(os.path.join(ROOT, 'mpl', 'preview_board.png')).convert('RGBA')
a = np.array(bd); diff = np.abs(a[:, :, :3].astype(int) - np.array([42, 106, 168])).sum(axis=2); a[:, :, 3] = np.where(diff < 30, 0, 255)
isl = Image.fromarray(a); isl = isl.crop(isl.getbbox()); isl.save(os.path.join(OUT, 'island.png'))
for f in ('preview_ghostship.png', 'preview_mirrorskel.png', 'spaces_preview.png'):
    im = Image.open(os.path.join(ROOT, 'mpl', f)).convert('RGBA'); im.crop(im.getbbox()).save(os.path.join(OUT, f.replace('preview_', '')))
lg = Image.open(os.path.join(RP, 'textures', 'ui', 'mpl', 'logo_venus.png')).convert('RGBA'); lg.crop(lg.getbbox()).save(os.path.join(OUT, 'logo.png'))
print('assets ok')
