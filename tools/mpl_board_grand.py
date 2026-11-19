# 女神の島 v6「大建築」: mpl_board.py の最後(コマンドにまとめる前)に exec で読みこむ。道とマスはさわらない
#   1. 大聖堂: 丘の南(階段の上)に正面(門・ばら窓・破風・中央の尖塔・左右の塔)、道の両がわに奥行きのある礼拝堂 2 棟
#      (控え柱・小尖塔・とがった窓・軒の金・紫の屋根・屋根窓)、北のはしに小さな門。道の上には屋根をかけない
#   2. 天使の像: 正面の階段の左右に1体ずつ
#   3. 火山: 火口のふちのギザギザの岩、斜面に光る溶岩の川(流れない)
#   4. 回廊: 火山のふもと東西のアーチの壁と、かざりのある塔
#   5. 桜(大きい)
#   6. 結果発表の会場: 島の南の海の上の舞台(幕・星のかざり・灯り・左右の塔)。BD.finaleZ = STAGE_Z
def G_clear_above(x1, z1, x2, z2, y1, y2, keep_road=True):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for z in range(min(z1, z2), max(z1, z2) + 1):
            if keep_road and (x, z) in ROAD: continue
            for y in range(y1, y2 + 1): V.pop((x, y, z), None)
rnd = random.Random(5)
def stone(): return rnd.choice(['stone_bricks'] * 6 + ['mossy_stone_bricks', 'cracked_stone_bricks', 'andesite'])
def white(): return rnd.choice(['quartz_bricks'] * 5 + ['smooth_quartz', 'calcite'])
GOLD = 'gold_block'

def deco_tower(cx, cz, base, top, r=2.4, kind='stone', roof='deepslate_tiles', banner='purple_wool'):
    """丸い塔: 台座(広い)・壁(石のまぜ)・帯・窓(あかり)・張り出しの胸壁・とがった屋根・金の先・旗"""
    mat = stone if kind == 'stone' else white
    trim = 'chiseled_stone_bricks' if kind == 'stone' else 'chiseled_quartz_block'
    slab = 'stone_brick_slab' if kind == 'stone' else 'quartz_slab'
    wall_ = 'stone_brick_wall' if kind == 'stone' else 'quartz_slab'
    R = int(r) + 2
    cells = lambda rr: [(x, z) for x in range(cx - R, cx + R + 1) for z in range(cz - R, cz + R + 1) if math.hypot(x - cx, z - cz) <= rr]
    G_clear_above(cx - R, cz - R, cx + R, cz + R, base, top + 12)
    for (x, z) in cells(r + 1):                                         # 台座
        g = H.get((x, z), base - 1)
        for y in range(min(g + 1, base), base + 2): put(x, y, z, trim if y == base + 1 else mat())
    for y in range(base + 2, top + 1):                                  # 壁
        for (x, z) in cells(r):
            if math.hypot(x - cx, z - cz) > r - 1: put(x, y, z, trim if (y - base) % 7 == 0 else mat())
    for y in range(base + 7, top, 7):                                   # 帯(外へ出る)
        for (x, z) in cells(r + 1):
            if math.hypot(x - cx, z - cz) > r: put(x, y, z, slab)
    for y in range(base + 4, top - 2, 5):                               # 窓(4方向、あかり)
        for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            x, z = round(cx + dx * r), round(cz + dz * r)
            put(x, y, z, 'yellow_stained_glass'); put(x, y + 1, z, 'yellow_stained_glass'); put(x - dx, y, z - dz, 'glowstone')
    for (x, z) in cells(r + 1):                                         # 張り出し + 胸壁
        if math.hypot(x - cx, z - cz) > r - 1:
            put(x, top + 1, z, trim)
            if math.hypot(x - cx, z - cz) > r and (x + z) % 2 == 0: put(x, top + 2, z, wall_)
    last = top + 2
    for k in range(int(r) + 3):                                          # とがった屋根(すこし外へ出てから細くなる)
        rr = r + 0.6 - k * 0.75
        if rr < 0.4: break
        for (x, z) in cells(rr): put(x, top + 2 + k, z, roof)
        last = top + 2 + k
    box(cx, last + 1, cz, cx, last + 3, cz, GOLD); put(cx, last + 4, cz, 'lightning_rod')
    bx_, bz_ = round(cx + r + 1), cz                                    # 旗(胸壁から下へ)
    for y in range(top - 3, top + 1): put(bx_, y, bz_, banner)
    put(bx_, top - 4, bz_, 'yellow_wool')

# ---------- 1. 大聖堂 ----------
B = 9                                                     # 丘の上の床の上
hill = {c for c, h in H.items() if h == 8 and abs(c[0]) <= 12 and wz(-1.5) < c[1] < wz(4.75)}
hill_s = min(z for (x, z) in hill if x == 0); hill_n = max(z for (x, z) in hill if x == 0)
G_clear_above(-14, hill_s - 6, 14, hill_n + 2, 9, 40)     # 前の神殿をすべて消す(床と道はのこす)
FZ0, FZ1 = hill_s, hill_s + 2                              # 正面(南向き)。厚み3
HZ0, HZ1 = FZ1 + 1, hill_n - 3                             # 礼拝堂の長さ
def fwall(x1, x2, y1, y2, z0=None, z1=None):
    for x in range(x1, x2 + 1):
        for z in range(z0 if z0 is not None else FZ0, (z1 if z1 is not None else FZ1) + 1):
            for y in range(y1, y2 + 1): put(x, y, z, white())
def open_road(x1, x2, z0, z1, top):
    for x in range(x1, x2 + 1):
        for z in range(z0, z1 + 1):
            lo = ROAD.get((x, z), H.get((x, z), 8)) + 1
            for y in range(lo, top + 1): V.pop((x, y, z), None)
# 正面: 中央(x -4..4)
fwall(-4, 4, B - 2, B + 17)
open_road(-2, 2, FZ0, FZ1, B + 6); open_road(-1, 1, FZ0, FZ1, B + 7)          # 門の口(上はアーチ)
for x in (-3, 3):
    for y in range(B - 2, B + 9): put(x, y, FZ0 - 1, 'quartz_pillar')          # 門の柱(前に出る)
    put(x, B + 9, FZ0 - 1, 'chiseled_quartz_block'); put(x, B + 10, FZ0 - 1, GOLD)
for x in range(-2, 3): put(x, B + 8, FZ0 - 1, 'chiseled_quartz_block' if abs(x) < 2 else 'quartz_bricks'); put(x, B + 9, FZ0 - 1, GOLD if x == 0 else 'quartz_slab')
for y in range(B + 11, B + 17):                                                 # ばら窓
    for x in range(-3, 4):
        r = math.hypot(x, y - (B + 14))
        if r <= 2.7: put(x, y, FZ0, GOLD if r > 2.0 else ('purple_stained_glass' if (x + y) % 2 else 'light_blue_stained_glass'))
for k in range(6):                                                             # 破風(三角)
    for x in range(-4 + k, 5 - k):
        for z in range(FZ0, FZ1 + 1): put(x, B + 18 + k, z, white())
    put(-4 + k, B + 18 + k, FZ0 - 1, 'quartz_slab'); put(4 - k, B + 18 + k, FZ0 - 1, 'quartz_slab')
for y in range(B + 22, B + 32):                                                # 中央の尖塔
    for x in range(-1, 2):
        for z in range(FZ0 + 1, FZ1 + 2):
            if not (x == 0 and z == FZ0 + 1 and y % 4 == 1): put(x, y, z, white())
            else: put(x, y, z, 'light_blue_stained_glass')
    if y in (B + 25, B + 29):
        for x in (-2, 2):
            for z in (FZ0, FZ1 + 2): put(x, y, z, 'chiseled_quartz_block'); put(x, y + 1, z, GOLD)
for k in range(5):
    w = 2 - k // 2
    for x in range(-w, w + 1):
        for z in range(FZ0 + 2 - w, FZ0 + 2 + w + 1): put(x, B + 32 + k, z, 'purple_concrete' if k < 4 else GOLD)
box(0, B + 37, FZ0 + 2, 0, B + 39, FZ0 + 2, GOLD); put(0, B + 40, FZ0 + 2, 'lightning_rod')
# 正面の左右(x 5..10)と角の塔
for s in (-1, 1):
    fwall(min(s * 5, s * 10), max(s * 5, s * 10), B - 2, B + 13)
    for x in (s * 7,):
        for y in range(B + 2, B + 10): put(x, y, FZ0, 'light_blue_stained_glass')
        put(x, B + 10, FZ0, 'purple_stained_glass'); put(x - 1, B + 10, FZ0, 'chiseled_quartz_block'); put(x + 1, B + 10, FZ0, 'chiseled_quartz_block'); put(x, B + 11, FZ0, GOLD)
    for x in (s * 5, s * 9):
        for y in range(B - 2, B + 14): put(x, y, FZ0 - 1, 'quartz_pillar')
        put(x, B + 14, FZ0 - 1, 'chiseled_quartz_block'); box(x, B + 15, FZ0 - 1, x, B + 16, FZ0 - 1, GOLD)
    for x in range(min(s * 5, s * 10), max(s * 5, s * 10) + 1): put(x, B + 14, FZ0, GOLD if x % 2 else 'chiseled_quartz_block')
    deco_tower(s * 13, FZ0 + 1, B - 1, B + 24, 2.4, 'white', 'purple_concrete', 'purple_wool')
# 礼拝堂 2 棟(道の左右、x 5..10)
for s in (-1, 1):
    xi, xo = s * 5, s * 10
    xa, xb = min(xi, xo), max(xi, xo)
    for z in range(HZ0, HZ1 + 1):
        for x in range(xa, xb + 1):
            edge = x in (xa, xb) or z in (HZ0, HZ1)
            g = H.get((x, z), 8)
            for y in range(min(g + 1, B), B + 11):
                if edge: put(x, y, z, white())
            put(x, B - 1, z, 'quartz_bricks')
    for z in range(HZ0 + 2, HZ1 - 1, 4):                                        # とがった窓(外と内)
        for x in (xi, xo):
            for y in range(B + 2, B + 8): put(x, y, z, 'light_blue_stained_glass' if y < B + 7 else 'purple_stained_glass')
            put(x, B + 8, z, 'chiseled_quartz_block')
    for z in range(HZ0, HZ1 + 1, 4):                                            # 控え柱(外がわ)と小尖塔
        x = xo + s
        g = H.get((x, z), 0)
        for y in range(max(0, g + 1), B + 9): put(x, y, z, 'quartz_bricks' if y < B + 6 else 'smooth_quartz')
        put(x, B + 9, z, 'quartz_slab'); put(xo, B + 11, z, 'chiseled_quartz_block'); put(xo, B + 12, z, 'quartz_pillar'); put(xo, B + 13, z, GOLD)
    for k in range(4):                                                          # 屋根(紫、とがる)
        for z in range(HZ0, HZ1 + 1):
            for x in range(xa + k, xb + 1 - k):
                if (x, B + 11 + k, z) in V and V[(x, B + 11 + k, z)] in ('chiseled_quartz_block', 'quartz_pillar', GOLD): continue
                put(x, B + 11 + k, z, 'purple_terracotta' if (x + z + k) % 5 == 0 else 'purple_concrete')
    for z in range(HZ0, HZ1 + 1): put((xa + xb) // 2, B + 14, z, GOLD)          # 屋根の背
    for z in range(HZ0 + 4, HZ1 - 2, 8):                                        # 屋根窓(道がわ)
        put(xi, B + 12, z, 'yellow_stained_glass'); put(xi, B + 13, z, 'quartz_slab')
    for x in range(xa, xb + 1): put(x, B + 10, HZ0, GOLD if x % 2 else 'chiseled_quartz_block')   # 南の妻の軒
    put((xa + xb) // 2, B + 6, HZ0, 'purple_stained_glass'); put((xa + xb) // 2, B + 5, HZ0, 'light_blue_stained_glass')
# 北のはしの小さな門(道をまたぐ)
for x in range(-4, 5):
    for y in range(B + 7, B + 10): put(x, y, HZ1 + 1, white())
    put(x, B + 10, HZ1 + 1, GOLD if x % 2 else 'chiseled_quartz_block')
for x in (-4, 4):
    for y in range(B, B + 7): put(x, y, HZ1 + 1, 'quartz_pillar')
# 道の両がわの白い手すりと灯り(礼拝堂のあいだ)
for z in range(HZ0, HZ1 + 1):
    for x in (-3, 3):
        if (x, z) in ROAD or H.get((x, z)) != 8: continue
        put(x, B, z, 'quartz_slab' if z % 6 else 'chiseled_quartz_block')
        if z % 6 == 0: box(x, B + 1, z, x, B + 2, z, 'quartz_pillar'); put(x, B + 3, z, 'lantern')
# ---------- 2. 天使の像(正面の階段の左右) ----------
def angel(ax, az):
    g = max(H.get((ax + i, az + j), 0) for i in (-1, 0, 1) for j in (-1, 0, 1))
    b = g + 1
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            for y in range(H.get((ax + i, az + j), 0) + 1, b + 2): put(ax + i, y, az + j, 'chiseled_quartz_block' if y == b + 1 else 'quartz_bricks')
    put(ax, b + 2, az, 'smooth_quartz'); box(ax, b + 3, az, ax, b + 6, az, 'white_concrete'); put(ax, b + 7, az, 'calcite')
    for side in (-1, 1):
        for k in range(1, 5):
            for y in range(b + 3 + k // 2, b + 8 + k - (2 if k == 4 else 0)):
                if y - (b + 3) < 2 + k: put(ax + side * k, y, az + 1, 'white_wool' if k < 4 else 'white_concrete')
for ax in (-6, 6):
    az = FZ0 - 4
    if (ax, az) in H and not near_road(ax, az, 1): angel(ax, az)
# ---------- 3. 火山: ふちのギザギザ・光る溶岩の川 ----------
for (x, z), h in list(H.items()):
    d = vol(x, z)
    if 1.0 <= d < 1.9 and not near_road(x, z, 2):
        n = int(abs(math.sin(x * 1.7 + z * 0.9) * 2 + math.sin(x * 0.4 - z * 1.3) * 1.5))
        for y in range(RIM + 1, RIM + 1 + n): put(x, y, z, rnd.choice(['blackstone', 'basalt', 'blackstone', 'tuff']))
for a in (-2.6, -1.8, -0.9, 0.6, 1.4, 2.2):
    for k in range(160):
        d = 1.85 + k * 0.022
        x, z = round(math.sin(a) * d * 1.15 * G), round(ZC + (9.8 - math.cos(a) * d * 0.75) * G)
        if (x, z) not in H or near_road(x, z, 1) or H[(x, z)] < 7 or vol(x, z) >= 5.0: continue
        w = 1 if k < 50 else 2
        for i in range(-w + 1, w):
            for j in range(-w + 1, w):
                c = (x + i, z + j)
                if c in H and not near_road(c[0], c[1], 1) and H[c] >= 7: put(c[0], H[c], c[1], 'ochre_froglight' if (i == 0 and j == 0) else 'magma_block')
# ---------- 4. 回廊(火山のふもと東西): アーチの壁 + かざりのある塔 ----------
def arcade_pts(a0, a1, d):
    pts, last = [], None
    for k in range(400):
        a = a0 + (a1 - a0) * k / 399
        c = (round(math.sin(a) * d * 1.15 * G), round(ZC + (9.8 - math.cos(a) * d * 0.75) * G))
        if c != last: pts.append(c); last = c
    return pts
for (a0, a1) in ((0.95, 2.3), (-2.3, -0.95)):
    ok = [p for p in arcade_pts(a0, a1, 5.55) if H.get(p) == 6 and not near_road(p[0], p[1], 2)]
    for i, (x, z) in enumerate(ok):
        G_clear_above(x - 1, z - 1, x + 1, z + 1, 7, 26)
        pil = i % 5 == 0
        for y in range(7, 16):
            if pil or y >= 13 or (y == 12 and i % 5 in (1, 4)): put(x, y, z, 'chiseled_stone_bricks' if (pil and y in (7, 12)) else stone())
        put(x, 16, z, 'stone_brick_wall' if i % 2 == 0 else 'stone_brick_slab')
        if pil: put(x, 17, z, 'lantern')
    for t in ((ok[0], ok[len(ok) // 2], ok[-1]) if ok else ()):
        deco_tower(t[0], t[1], 7, 24, 2.4, 'stone', 'deepslate_tiles', 'red_wool')
# ---------- 5. 大きな桜 ----------
for (x, z) in ((-12, wz(-1.4)), (12, wz(-1.2)), (-17, wz(2)), (18, wz(2.5)), (-20, wz(4)), (21, wz(-0.5))):
    if (x, z) in H and not near_road(x, z, 3) and H[(x, z)] >= 0:
        G_clear_above(x - 4, z - 4, x + 4, z + 4, H[(x, z)] + 1, H[(x, z)] + 14, True)
        tree_(x, z, 'cherry', big=True)
# ---------- 6. 結果発表の会場(島の南の海の上) ----------
STAGE_Z = 31                                   # 人が並ぶ列(BD.finaleZ)。床の上は y=1
SX0, SX1, SZ0, SZ1 = -14, 14, 26, 37
for x in range(SX0, SX1 + 1):
    for z in range(SZ0, SZ1 + 1):
        edge = x in (SX0, SX1) or z in (SZ0, SZ1)
        put(x, 0, z, GOLD if (edge and (x + z) % 4 == 0) else 'polished_blackstone_bricks' if edge else ('polished_deepslate' if (x + z) % 2 else 'deepslate_tiles'))
for x in range(-3, 4):                         # 真ん中の赤いじゅうたん(前から列まで)
    for z in range(SZ0, STAGE_Z + 2): put(x, 0, z, 'red_concrete' if abs(x) < 3 else 'gold_block')
for x in range(SX0, SX1 + 1, 4): put(x, 0, SZ0, 'sea_lantern')
for (x, z) in ((SX0, SZ0), (SX1, SZ0), (SX0, SZ1), (SX1, SZ1), (0, SZ0), (0, SZ1)):
    box(x, -4, z, x, -1, z, 'polished_blackstone_bricks')
BZ = SZ1 + 1                                   # うしろの壁: わく・赤い幕・紫の板と金の星・上の灯り
for x in range(SX0, SX1 + 1):
    for y in range(1, 15):
        frame = x in (SX0, SX1, -8, 8) or y in (1, 14)
        if frame: put(x, y, BZ, 'polished_blackstone_bricks' if y < 14 else 'chiseled_polished_blackstone')
        elif abs(x) < 8: put(x, y, BZ, 'purple_concrete' if (x + y) % 6 else 'purple_terracotta')
        else:
            hang = 13 - (abs(x) - 8) * 2
            put(x, y, BZ, 'red_wool' if y >= 14 - hang or (abs(x) - 8) < 2 else 'polished_blackstone')
    put(x, 15, BZ, 'polished_blackstone_wall' if x % 2 else 'lantern')
STAR = [(0, 6), (-1, 5), (0, 5), (1, 5), (-1, 4), (0, 4), (1, 4), (-4, 4), (-3, 4), (-2, 4), (2, 4), (3, 4), (4, 4), (-3, 3), (-2, 3), (-1, 3), (0, 3), (1, 3), (2, 3), (3, 3),
        (-2, 2), (-1, 2), (0, 2), (1, 2), (2, 2), (-2, 1), (-1, 1), (1, 1), (2, 1), (-3, 0), (-2, 0), (2, 0), (3, 0)]
for (i, j) in STAR: put(i, 4 + j, BZ - 1, GOLD)
for x in (-6, -3, 3, 6): put(x, 13, BZ - 1, 'end_rod ["facing_direction"=0]')
for s in (-1, 1): deco_tower(s * 18, SZ1 - 1, 0, 16, 2.4, 'white', 'purple_concrete', 'purple_wool')
