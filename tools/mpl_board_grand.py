# 女神の島 v6「大建築」: mpl_board.py の最後(コマンドにまとめる前)に exec で読みこむ。道とマスはさわらない
#   1. 大聖堂(白い外装のお城): 灰色のレンガ + 白い太いわく、白い大アーチ 3 つ、バルコニー、三角屋根、塔 4 本(青緑の広がる屋根・旗)、うしろに棟 2 棟
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

# ---------- 1. 大聖堂(白い外装のお城) ----------
#   参考: 明るい灰色のレンガの壁 + 白い太いわく(窓・アーチ・柱・軒)、1階は白い大アーチ 3 つ、2階に白い手すりのバルコニーと木の帯、
#   真ん中は大きな三角屋根(屋根のふちが白い破風を A の字にかこむ・上に窓)、塔 4 本(内がわ 2 本が高い)、
#   青緑の屋根は段ごとに外へ広がる(スカート)・先に金属のかざり・ピンクと白の旗
B = 9                                                     # 丘の上の床の上
hill = {c for c, h in H.items() if h == 8 and abs(c[0]) <= 12 and wz(-1.5) < c[1] < wz(4.75)}
hill_s = min(z for (x, z) in hill if x == 0); hill_n = max(z for (x, z) in hill if x == 0)
G_clear_above(-18, hill_s - 6, 18, hill_n + 2, 9, 48)
FZ0 = hill_s                                               # 正面の面(南向き)
HZ0, HZ1 = FZ0 + 9, hill_n - 3                             # うしろの棟
GREY = lambda: rnd.choice(['stone_bricks'] * 7 + ['polished_andesite', 'andesite', 'cracked_stone_bricks'])
WHT, WHT2, ROOF, ROOF2, GLASS, WOOD = 'white_concrete', 'smooth_quartz', 'prismarine_bricks', 'prismarine', 'blue_stained_glass', 'stripped_spruce_log'
def ground(x, z): return H.get((x, z), 8)
def colfill(x, z, y1, y2, b):
    for y in range(min(ground(x, z) + 1, y1), y2 + 1): put(x, y, z, b() if callable(b) else b)
def open_road(x1, x2, z0, z1, top):
    for x in range(x1, x2 + 1):
        for z in range(z0, z1 + 1):
            lo = ROAD.get((x, z), ground(x, z)) + 1
            for y in range(lo, top + 1): V.pop((x, y, z), None)
def flared_roof(cx, cz, y0, r0, hgt, tip=True):
    """塔の屋根: 下は塔より広く、段ごとに細くなる。3 段ごとに外へ 1 つ広い輪(スカート)"""
    for k in range(hgt):
        t = k / hgt
        r = max(0.0, r0 * (1 - t) ** 1.25)
        R = int(r) + 2
        for x in range(cx - R, cx + R + 1):
            for z in range(cz - R, cz + R + 1):
                d = math.hypot(x - cx, z - cz)
                if d <= r + 0.35: put(x, y0 + k, z, ROOF if (x + z + k) % 7 else ROOF2)
                elif k % 3 == 0 and k < hgt - 3 and d <= r + 1.35: put(x, y0 + k - 1, z, ROOF)
    if tip:
        put(cx, y0 + hgt, cz, 'iron_block'); box(cx, y0 + hgt + 1, cz, cx, y0 + hgt + 2, cz, 'iron_bars'); put(cx, y0 + hgt + 3, cz, 'lightning_rod')
def flag(x, y, z, s):
    """ピンクと白の旗(風でなびく形)"""
    box(x, y, z, x, y + 3, z, 'iron_bars')
    for (i, k) in ((1, 3), (2, 3), (3, 2), (4, 2), (5, 3), (1, 2), (2, 2), (3, 1), (4, 1), (5, 2)):
        put(x + s * i, y + k, z, 'pink_wool' if (i + k) % 2 else 'white_wool')
def castle_tower(cx, cz, top, r, roof_h, window=True):
    """丸い塔: 灰色のレンガ・白い台座の帯・白いわくの縦長の青い窓・上の白い軒・広がる屋根"""
    R = int(r) + 2
    for x in range(cx - R, cx + R + 1):
        for z in range(cz - R, cz + R + 1):
            d = math.hypot(x - cx, z - cz)
            if d <= r:
                if d > r - 1.1: colfill(x, z, B - 2, top, GREY)
                else: colfill(x, z, B - 2, B - 1, GREY)
            if r < d <= r + 1.0:
                put(x, B - 1, z, WHT)                                   # 台座の白い帯
                put(x, top + 1, z, WHT)                                 # 上の白い軒
    for (dx, dz) in ((0, -1), (-1, 0), (1, 0)):                       # 窓(前と左右)
        x, z = round(cx + dx * r), round(cz + dz * r)
        y1, y2 = (B + 3, B + 8) if window else (B + 4, B + 5)
        for y in range(y1, y2 + 1): put(x, y, z, GLASS)
        for y in range(y1 - 1, y2 + 2):
            for (ox, oz) in ((dz, dx), (-dz, -dx)): put(x + ox, y, z + oz, WHT)
        put(x, y1 - 1, z, WHT); put(x, y2 + 1, z, WHT)
        for y in (top - 4, top - 3): put(x, y, z, GLASS)                # 上の小さい窓
        put(x, top - 5, z, WHT); put(x, top - 2, z, WHT)
    flared_roof(cx, cz, top + 2, r + 1.6, roof_h)
# --- 塔 4 本: 外がわは低く太い、内がわは高い ---
for s in (-1, 1):
    castle_tower(s * 14, FZ0 + 3, B + 13, 3.4, 15)
    castle_tower(s * 8, FZ0 + 5, B + 20, 2.6, 17)
flag(14 + 1, B + 31, FZ0 + 3, 1); flag(-14 - 1, B + 31, FZ0 + 3, -1)
# --- 真ん中の棟(x -11..11): 1階の白い大アーチ 3 つ ---
for x in range(-11, 12):
    for z in range(FZ0, HZ0):
        edge = z == FZ0 or abs(x) == 11 or z == HZ0 - 1
        if edge: colfill(x, z, B - 2, B + 8, GREY)
        put(x, B - 1, z, 'polished_andesite')
for (ax, hw, ht) in ((0, 3, 6), (-8, 1, 4), (8, 1, 4)):              # アーチ(白い太いわく、上は丸い)
    for x in range(ax - hw - 2, ax + hw + 3):
        for y in range(B - 1, B + ht + 3):
            dxx = abs(x - ax); top_curve = B + ht - (1 if dxx >= hw else 0)
            inside = dxx <= hw and y <= top_curve
            ring = (dxx <= hw + 2 and y <= top_curve + 2) and not inside
            if ring: put(x, y, FZ0, WHT if (dxx >= hw + 1 or y > top_curve) else WHT2); put(x, y, FZ0 - 1, WHT) if dxx in (hw + 1, hw + 2) and y < top_curve else None
            if inside and ax != 0: put(x, y, FZ0, GLASS if y > B + 1 else WHT)
open_road(-3, 3, FZ0 - 1, HZ0 - 1, B + 5); open_road(-2, 2, FZ0 - 1, HZ0 - 1, B + 6)   # 真ん中のアーチの下は道(あける)。上は丸く、白いわくはのこす
for z in range(FZ0, HZ0):                                                              # アーチの中: 赤いじゅうたんの両わき
    for x in (-3, 3): put(x, ROAD.get((x, z), 8), z, 'red_concrete') if (x, z) not in ROAD else None
# --- 1階と2階のあいだ: 木の帯 + 白い手すりのバルコニー ---
for x in range(-11, 12):
    put(x, B + 9, FZ0, WOOD if abs(x) % 4 else WHT)
    put(x, B + 10, FZ0 - 1, WHT2); put(x, B + 11, FZ0 - 1, 'diorite_wall' if x % 2 else WHT)
    put(x, B + 10, FZ0, WHT2)
# --- 2階: 灰色の壁・白い柱・まんなかのバルコニーの扉 ---
for x in range(-7, 8):
    for z in range(FZ0 + 1, HZ0):
        if abs(x) == 7 or z == FZ0 + 1: colfill(x, z, B + 11, B + 17, GREY)
for x in (-7, -4, 4, 7):
    for y in range(B + 11, B + 18): put(x, y, FZ0 + 1, WHT)
for x in (-6, -5, 5, 6):
    for y in range(B + 13, B + 16): put(x, y, FZ0 + 1, GLASS)
for y in range(B + 11, B + 15):
    for x in (-1, 0, 1): put(x, y, FZ0 + 1, 'spruce_planks' if y < B + 14 else WHT)
put(0, B + 12, FZ0 + 1, 'lantern')
for x in range(-3, 4): put(x, B + 11, FZ0, WHT2); put(x, B + 12, FZ0 - 0, 'diorite_wall') if abs(x) == 3 else None
# --- 真ん中の大きな三角屋根: ふちが白い破風を A の字にかこむ。うしろへ棟がつづく ---
RY0, RH, RHW = B + 18, 15, 9
for k in range(RH):
    hw = RHW - k * RHW / RH
    for x in range(-int(hw) - 1, int(hw) + 2):
        ax_ = abs(x)
        if ax_ > hw + 0.6: continue
        outer = ax_ > hw - 2.2                       # 屋根のふち(前の面)
        for z in range(FZ0 + 1, HZ0 + 2):
            if outer or z > FZ0 + 2: put(x, RY0 + k, z, ROOF if (x + k) % 6 else ROOF2) if (outer or z == HZ0 + 1 or ax_ > hw - 1.2) else None
        if not outer: put(x, RY0 + k, FZ0 + 1, WHT if ax_ > hw - 3.2 else GREY())   # 白い破風(内がわは灰色)
    if k % 3 == 0 and hw > 2:                        # 段のスカート(ふちの外へ 1 つ)
        for x in (-int(hw) - 1, int(hw) + 1): put(x, RY0 + k - 1, FZ0 + 1, ROOF)
for y in range(RY0 + 6, RY0 + 10):                   # 破風の窓
    for x in (-1, 0, 1): put(x, y, FZ0 + 1, GLASS if abs(x) < 1 or y < RY0 + 9 else WHT)
for x in (-2, 2):
    for y in range(RY0 + 5, RY0 + 11): put(x, y, FZ0 + 1, WHT)
put(0, RY0 + RH, FZ0 + 2, 'iron_block'); box(0, RY0 + RH + 1, FZ0 + 2, 0, RY0 + RH + 2, FZ0 + 2, 'iron_bars'); put(0, RY0 + RH + 3, FZ0 + 2, 'lightning_rod')
# ---------- うしろの棟 2 棟(道の左右): 灰色の壁・白いわくの窓と柱・青緑の屋根 ----------
for s in (-1, 1):
    xi, xo = s * 5, s * 10
    xa, xb = min(xi, xo), max(xi, xo)
    for z in range(HZ0, HZ1 + 1):
        for x in range(xa, xb + 1):
            if x in (xa, xb) or z in (HZ0, HZ1): colfill(x, z, B - 2, B + 9, GREY)
            put(x, B - 1, z, 'polished_andesite')
        for x in (xi, xo): put(x, B + 10, z, WHT)                              # 軒(白)
    for z in range(HZ0 + 2, HZ1 - 1, 4):                                      # 白いわくの縦長の窓(外と内)
        for x in (xi, xo):
            for y in range(B + 2, B + 7): put(x, y, z, GLASS)
            for y in range(B + 1, B + 8):
                put(x, y, z - 1, WHT); put(x, y, z + 1, WHT)
            put(x, B + 1, z, WHT); put(x, B + 7, z, WHT)
    for z in range(HZ0, HZ1 + 1, 4):                                          # 白い柱(外がわ)
        x = xo + s
        g = ground(x, z)
        for y in range(max(0, g + 1), B + 10): put(x, y, z, WHT if (y - B) % 5 else WHT2)
    for k in range(5):                                                        # 青緑の屋根(とがる、端は 1 つ下へ)
        for z in range(HZ0 - 1, HZ1 + 2):
            for x in range(xa - 1 + k, xb + 2 - k):
                put(x, B + 11 + k, z, ROOF if (x + z + k) % 7 else ROOF2)
        put(xa - 1 + k, B + 10 + k, HZ0 - 1, ROOF); put(xb + 1 - k, B + 10 + k, HZ0 - 1, ROOF)
    put((xa + xb) // 2, B + 16, HZ0, 'iron_block'); put((xa + xb) // 2, B + 17, HZ0, 'lightning_rod')
# 北のはしの門(白い太いアーチ)
for x in range(-4, 5):
    for y in range(B + 7, B + 11): put(x, y, HZ1 + 1, WHT if (y == B + 10 or abs(x) == 4) else GREY())
for x in (-4, 4):
    for y in range(B, B + 7): put(x, y, HZ1 + 1, WHT)
# 道の両がわの白い手すりと灯り(うしろの棟のあいだ)
for z in range(HZ0, HZ1 + 1):
    for x in (-3, 3):
        if (x, z) in ROAD or H.get((x, z)) != 8: continue
        put(x, B, z, 'diorite_wall' if z % 6 else WHT)
        if z % 6 == 0: box(x, B + 1, z, x, B + 2, z, WHT2); put(x, B + 3, z, 'lantern')
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
# (天使の像は置かない: お城の 1 階の白いアーチがかくれるため)
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
for (x, z) in ((-19, wz(2)), (20, wz(2.5)), (-21, wz(4)), (22, wz(-0.5))):   # お城の正面の前には植えない
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
