# MPL の文字の中で使えるアイコン(RP の font/glyph_E1.png)
#   U+E100〜: ★スター / ◎コイン / サイコロ / 王冠 / 上向き / 下向き / ハート / 稲妻 / ふくろ / 時計
#   U+E110〜U+E117: 順位のバッジ 1〜8(金・銀・銅・青)
#   python3 tools/mpl_glyphs.py
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp', 'font'); os.makedirs(OUT, exist_ok=True)
CELL, K = 32, 4  # 1マス 32px(高解像度)。描くときは4倍で描いて縮める
page = Image.new('RGBA', (CELL * 16, CELL * 16))
def cell(i, draw):
    big = Image.new('RGBA', (CELL * K, CELL * K)); d = ImageDraw.Draw(big)
    draw(d, CELL * K)
    page.paste(big.resize((CELL, CELL), Image.LANCZOS), ((i % 16) * CELL, (i // 16) * CELL))
def star(d, s, fill=(255, 210, 40), line=(150, 90, 0)):
    import math
    pts = [(s / 2 + math.cos(math.radians(-90 + i * 36)) * (s * 0.46 if i % 2 == 0 else s * 0.2), s / 2 + 2 + math.sin(math.radians(-90 + i * 36)) * (s * 0.46 if i % 2 == 0 else s * 0.2)) for i in range(10)]
    d.polygon(pts, fill=fill, outline=line, width=s // 16)
    d.ellipse((s * 0.36, s * 0.42, s * 0.44, s * 0.56), fill=(40, 30, 20)); d.ellipse((s * 0.56, s * 0.42, s * 0.64, s * 0.56), fill=(40, 30, 20))
def coin(d, s):
    d.ellipse((s * 0.08, s * 0.08, s * 0.92, s * 0.92), fill=(255, 196, 30), outline=(170, 110, 0), width=s // 14)
    d.ellipse((s * 0.24, s * 0.24, s * 0.76, s * 0.76), outline=(255, 235, 140), width=s // 18)
    d.rectangle((s * 0.45, s * 0.3, s * 0.55, s * 0.7), fill=(190, 130, 0))
def dice(d, s):
    d.rounded_rectangle((s * 0.1, s * 0.1, s * 0.9, s * 0.9), s // 8, fill=(250, 250, 250), outline=(60, 60, 70), width=s // 16)
    for x, y in [(0.3, 0.3), (0.5, 0.5), (0.7, 0.7)]: d.ellipse((s * (x - 0.08), s * (y - 0.08), s * (x + 0.08), s * (y + 0.08)), fill=(30, 30, 40))
def crown(d, s):
    d.polygon([(s * 0.1, s * 0.75), (s * 0.12, s * 0.3), (s * 0.32, s * 0.52), (s * 0.5, s * 0.2), (s * 0.68, s * 0.52), (s * 0.88, s * 0.3), (s * 0.9, s * 0.75)], fill=(255, 205, 40), outline=(150, 90, 0), width=s // 16)
    for x in (0.3, 0.5, 0.7): d.ellipse((s * (x - 0.05), s * 0.6, s * (x + 0.05), s * 0.7), fill=(220, 40, 60))
def arrow(d, s, up):
    col = (70, 220, 100) if up else (240, 70, 70)
    d.polygon([(s * 0.5, s * 0.15), (s * 0.88, s * 0.62), (s * 0.12, s * 0.62)] if up else [(s * 0.5, s * 0.85), (s * 0.88, s * 0.38), (s * 0.12, s * 0.38)], fill=col, outline=(20, 20, 20), width=s // 20)
def heart(d, s):
    d.ellipse((s * 0.1, s * 0.2, s * 0.52, s * 0.6), fill=(240, 60, 80)); d.ellipse((s * 0.48, s * 0.2, s * 0.9, s * 0.6), fill=(240, 60, 80)); d.polygon([(s * 0.12, s * 0.48), (s * 0.88, s * 0.48), (s * 0.5, s * 0.88)], fill=(240, 60, 80))
def bolt(d, s): d.polygon([(s * 0.58, s * 0.05), (s * 0.2, s * 0.55), (s * 0.45, s * 0.55), (s * 0.35, s * 0.95), (s * 0.8, s * 0.4), (s * 0.55, s * 0.4), (s * 0.7, s * 0.05)], fill=(255, 220, 40), outline=(180, 110, 0), width=s // 20)
def bag(d, s):
    d.ellipse((s * 0.15, s * 0.3, s * 0.85, s * 0.92), fill=(170, 110, 60), outline=(90, 55, 25), width=s // 18); d.rectangle((s * 0.38, s * 0.15, s * 0.62, s * 0.32), fill=(170, 110, 60))
    coin(lambda: None, 0) if False else None
def clock(d, s):
    d.ellipse((s * 0.1, s * 0.1, s * 0.9, s * 0.9), fill=(245, 245, 250), outline=(60, 60, 70), width=s // 14); d.line((s * 0.5, s * 0.5, s * 0.5, s * 0.22), fill=(30, 30, 40), width=s // 12); d.line((s * 0.5, s * 0.5, s * 0.72, s * 0.5), fill=(30, 30, 40), width=s // 12)
for i, f in enumerate([star, coin, dice, crown, lambda d, s: arrow(d, s, True), lambda d, s: arrow(d, s, False), heart, bolt, bag, clock]): cell(i, f)
try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', CELL * K // 2)
except Exception: font = ImageFont.load_default()
for n in range(1, 9):
    col = {1: (255, 200, 40), 2: (200, 210, 225), 3: (215, 135, 70)}.get(n, (80, 130, 230))
    def badge(d, s, n=n, col=col):
        d.ellipse((s * 0.05, s * 0.05, s * 0.95, s * 0.95), fill=col, outline=(30, 30, 40), width=s // 14)
        d.text((s / 2, s / 2 + s * 0.02), str(n), font=font, fill=(255, 255, 255), anchor='mm', stroke_width=s // 16, stroke_fill=(30, 30, 40))
    cell(16 + n - 1, badge)
page.save(os.path.join(OUT, 'glyph_E1.png'))
print('ok')
