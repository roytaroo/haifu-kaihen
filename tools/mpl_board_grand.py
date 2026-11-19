# 女神の島 v5「大建築」: mpl_board.py の最後(コマンドにまとめる前)に exec で読みこむ。道とマスはさわらない
#   1. 大聖堂: 丘の北のはしに、道をまたぐ正面(中央の門・ばら窓・中央の尖塔・左右の翼・外の塔)。道の両がわに低い手すりと金の灯り
#   2. 天使の像: 道の左右に1体ずつ(台座・ローブ・広げた翼・頭の上の輪)
#   3. 金の輪: 大聖堂の尖塔のまわりに3つ、火山の上に2つ(宙にうかぶ)
#   4. 火山: 火口のふちにギザギザの岩、斜面に光る溶岩の川(太く、流れない)
#   5. 回廊: 火山のふもとを東西にぐるっと囲むアーチの回廊と塔(尖った屋根・金の先・光る窓)
#   6. 丘の段: 東西のがけに滝(下の受け池でとまる)、がけの上に藤(紫)、まわりに大きな桜
def G_clear_above(x1, z1, x2, z2, y1, y2, keep_road=True):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for z in range(min(z1, z2), max(z1, z2) + 1):
            if keep_road and (x, z) in ROAD: continue
            for y in range(y1, y2 + 1): V.pop((x, y, z), None)
def ring(cx, cy, cz, rx, rz, b='gold_block', glow='sea_lantern', n=None):
    n = n or int(2 * math.pi * max(rx, rz) * 1.4)
    seen = set()
    for k in range(n):
        a = k / n * math.pi * 2
        c = (round(cx + math.cos(a) * rx), cy, round(cz + math.sin(a) * rz))
        if c in seen: continue
        seen.add(c); put(c[0], c[1], c[2], glow if len(seen) % 7 == 0 else b)
WH, WH2, TRIM, GOLD = 'quartz_bricks', 'smooth_quartz', 'chiseled_quartz_block', 'gold_block'

# ---------- 1. 大聖堂 ----------
cx0 = 0
hill_n = max(z for (x, z), h in H.items() if x == 0 and h == 8 and z < wz(4.75))   # 丘の上の北のはし(火山の斜面はふくめない)
FZ0, FZ1 = hill_n - 2, hill_n          # 正面の壁(3ブロックの厚み)。マスとマスのあいだの道の上(マスの上はふさがない)
B = 9                                  # 丘の上の床の上
# 古い神殿(柱・はり・像・輪)を消す(床と道はのこす)
G_clear_above(-12, wz(2) - 16, 12, hill_n + 1, 9, 30)
for y in range(17, 23):
    for x in range(-12, 13):
        for z in range(wz(2) - 16, hill_n + 2): V.pop((x, y, z), None)
def wall(x1, x2, y1, y2, mat=WH):
    for x in range(x1, x2 + 1):
        for z in range(FZ0, FZ1 + 1):
            for y in range(y1, y2 + 1): put(x, y, z, mat)
# 中央: 門のまわり(x -4..4)
wall(-4, 4, B, B + 9)
for x in range(-2, 3):                 # 門の口(道の上をあける。上はアーチ)
    top = B + 6 + (1 if abs(x) <= 1 else 0)
    for z in range(FZ0, FZ1 + 1):
        lo = ROAD.get((x, z), H.get((x, z), 8)) + 1          # 道(と地面)のブロックはのこす
        for y in range(lo, top + 1): V.pop((x, y, z), None)
for x in (-3, 3):
    for y in range(B, B + 8): put(x, y, FZ0 - 1, 'quartz_pillar')   # 門の両がわの柱(前に出る)
put(-3, B + 8, FZ0 - 1, GOLD); put(3, B + 8, FZ0 - 1, GOLD)
for x in range(-3, 4): put(x, B + 9, FZ0 - 1, TRIM if abs(x) < 3 else GOLD)
wall(-4, 4, B + 10, B + 17)
for y in range(B + 11, B + 17):        # ばら窓(丸)
    for x in range(-3, 4):
        r = math.hypot(x, y - (B + 14))
        if r <= 2.6: put(x, y, FZ0, 'gold_block' if r > 2.0 else ('purple_stained_glass' if (x + y) % 2 else 'light_blue_stained_glass'))
for k in range(6):                     # 三角の破風
    for x in range(-4 + k, 5 - k): put(x, B + 18 + k, FZ0 + 1, WH); put(x, B + 18 + k, FZ0, TRIM if k == 0 else WH)
for x in range(-4, 5): put(x, B + 18, FZ0 - 1, GOLD)
# 中央の尖塔(3x3 → 紫の屋根 → 金の先)
for y in range(B + 18, B + 28):
    for x in range(-1, 2):
        for z in range(FZ0 + 1, FZ1 + 2): put(x, y, z, WH)
    if y % 3 == 0: put(0, y, FZ0, 'light_blue_stained_glass')
for x in (-2, 2):
    for z in (FZ0, FZ1 + 2): put(x, B + 28, z, GOLD); put(x, B + 29, z, GOLD)
for k in range(5):
    w = 2 - k // 2
    for x in range(-w, w + 1):
        for z in range(FZ0 + 1 - w + 1, FZ1 + 1 + w): put(x, B + 28 + k, z, 'purple_concrete' if k < 4 else GOLD)
box(0, B + 33, FZ0 + 1, 0, B + 36, FZ0 + 1, GOLD); put(0, B + 37, FZ0 + 1, 'sea_lantern')
# 左右の翼(x 5..10): 高い窓と控え柱、上に小さな尖塔
for s in (-1, 1):
    xs = [s * x for x in range(5, 11)]
    wall(min(xs), max(xs), B, B + 18)
    for x in (s * 6, s * 8):                                  # 縦長の窓(上がとがる)
        for y in range(B + 3, B + 14): put(x, y, FZ0, 'light_blue_stained_glass')
        put(x, B + 14, FZ0, 'purple_stained_glass'); put(x, B + 15, FZ0, GOLD)
    for x in (s * 5, s * 10):                                 # 控え柱(前に出る)と小さな尖塔
        for y in range(B, B + 19): put(x, y, FZ0 - 1, 'quartz_pillar')
        put(x, B + 19, FZ0 - 1, TRIM); box(x, B + 20, FZ0 - 1, x, B + 22, FZ0 - 1, GOLD)
        put(x, B + 19, FZ0, WH); put(x, B + 20, FZ0, 'purple_concrete')
    for x in range(min(xs), max(xs) + 1): put(x, B + 19, FZ0, GOLD if x % 2 else WH2)
    for k in range(3):                                        # 翼の上の屋根(紫、うしろへ)
        for x in range(min(xs) + k, max(xs) + 1 - k):
            for z in range(FZ0 + 1, FZ1 + 1): put(x, B + 19 + k, z, 'purple_concrete' if k < 2 else GOLD)
    for x in (s * 7,):                                         # 翼の旗(紫に金)
        for y in range(B + 1, B + 3): put(x, y, FZ0 - 1, 'purple_wool')
# 外の塔(x 11..13): 地面から立てる
for s in (-1, 1):
    tx = s * 12
    for x in range(tx - 1, tx + 2):
        for z in range(FZ0 - 1, FZ1 + 2):
            g = H.get((x, z), 4)
            for y in range(max(0, g + 1), B + 26): put(x, y, z, WH if (y % 5) else TRIM)
    for y in range(B + 4, B + 24, 4): put(tx, y, FZ0 - 2, 'glowstone')
    for k in range(4):
        w = 1 - k // 2
        for x in range(tx - w, tx + w + 1):
            for z in range(FZ0 - w, FZ1 + w + 1): put(x, B + 26 + k, z, 'purple_concrete' if k < 3 else GOLD)
    box(tx, B + 30, FZ0, tx, B + 33, FZ0, GOLD)
# 道の両がわの低い手すり(白)と金の灯り(大聖堂の手前の丘の上)
for z in range(wz(2) - 14, FZ0 - 1):
    for x in (-2, 2):
        if (x, z) in ROAD or H.get((x, z)) != 8: continue
        put(x, B, z, 'quartz_slab' if z % 6 else 'chiseled_quartz_block')
        if z % 6 == 0: box(x, B + 1, z, x, B + 2, z, 'quartz_pillar'); put(x, B + 3, z, GOLD); put(x, B + 4, z, 'lantern')
# ---------- 2. 天使の像(道の左右、丘の上の真ん中あたり。南を向く) ----------
def angel(ax, az):
    box(ax - 1, B, az - 1, ax + 1, B + 1, az + 1, TRIM)                 # 台座
    put(ax, B + 2, az, WH); box(ax - 1, B + 2, az, ax + 1, B + 2, az, WH2)  # すそ
    box(ax, B + 3, az, ax, B + 6, az, 'white_concrete')                # ローブ
    put(ax, B + 7, az, 'calcite')                                       # 頭
    ring(ax, B + 9, az, 1, 1, GOLD, GOLD, 8)                             # 頭の上の輪
    for side in (-1, 1):                                                # 翼(外へ広がって上がる)
        for k in range(1, 5):
            for y in range(B + 3 + k // 2, B + 8 + k - (2 if k == 4 else 0)):
                if y - (B + 3) < 2 + k: put(ax + side * k, y, az + 1, 'white_wool' if k < 4 else 'white_concrete')
        put(ax + side * 4, B + 3, az + 1, 'white_wool')
angel(-6, wz(2) - 2); angel(6, wz(2) - 2)
# ---------- 3. 金の輪 ----------
ring(0, B + 31, FZ0 + 1, 8, 5); ring(0, B + 35, FZ0 + 1, 5, 3)
VCX, VCZ = 0, round(ZC + 9.8 * G)
ring(VCX, 40, VCZ + 4, 7, 5)
# ---------- 4. 火山: ふちのギザギザ・光る溶岩の川 ----------
for (x, z), h in list(H.items()):
    d = vol(x, z)
    if 1.0 <= d < 1.9 and not near_road(x, z, 2):
        n = int(abs(math.sin(x * 1.7 + z * 0.9) * 2 + math.sin(x * 0.4 - z * 1.3) * 1.5))   # ふちの岩は低め(最大3)
        for y in range(19, 19 + n): put(x, y, z, random.choice(['blackstone', 'basalt', 'blackstone', 'polished_blackstone']))
for a in (-2.6, -1.8, -0.9, 0.6, 1.4, 2.2):
    for k in range(140):
        d = 1.85 + k * 0.025
        x, z = round(math.sin(a) * d * 1.15 * G), round(ZC + (9.8 - math.cos(a) * d * 0.75) * G)
        if (x, z) not in H or near_road(x, z, 1) or H[(x, z)] < 7 or vol(x, z) >= 5.0: continue
        w = 1 if k < 40 else 2
        for i in range(-w + 1, w):
            for j in range(-w + 1, w):
                c = (x + i, z + j)
                if c in H and not near_road(c[0], c[1], 1) and H[c] >= 7: put(c[0], H[c], c[1], 'ochre_froglight' if (i == 0 and j == 0) else 'magma_block')
# ---------- 5. 回廊(火山のふもと、東と西): アーチと塔 ----------
def arcade_pts(a0, a1, d):
    pts, last = [], None
    for k in range(400):
        a = a0 + (a1 - a0) * k / 399
        c = (round(math.sin(a) * d * 1.15 * G), round(ZC + (9.8 - math.cos(a) * d * 0.75) * G))
        if c != last: pts.append(c); last = c
    return pts
for (a0, a1) in ((0.95, 2.3), (-2.3, -0.95)):
    pts = arcade_pts(a0, a1, 5.55)
    ok = [p for p in pts if H.get(p) == 6 and not near_road(p[0], p[1], 2)]
    print('arcade', len(pts), len(ok))
    for i, (x, z) in enumerate(ok):
        G_clear_above(x - 1, z - 1, x + 1, z + 1, 7, 26)
        pil = i % 5 == 0
        for y in range(7, 16):
            if pil or y >= 12 or (y == 11 and i % 5 in (1, 4)): put(x, y, z, 'stone_bricks' if y < 15 else 'polished_andesite')
        if i % 2 == 0: put(x, 16, z, 'stone_brick_wall')
        if pil: put(x, 16, z, 'lantern')
    for t in (ok[0], ok[len(ok) // 2], ok[-1]) if ok else ():   # 塔
        tx, tz = t
        for x in range(tx - 2, tx + 3):
            for z in range(tz - 2, tz + 3):
                if abs(x - tx) == 2 and abs(z - tz) == 2: continue
                G_clear_above(x, z, x, z, 7, 34)
                for y in range(7, 26): put(x, y, z, 'stone_bricks' if (y % 6) else 'chiseled_stone_bricks')
        for y in range(10, 25, 4):
            for (x, z) in ((tx - 2, tz), (tx + 2, tz), (tx, tz - 2), (tx, tz + 2)): put(x, y, z, 'glowstone')
        for k in range(5):
            w = 2 - (k + 1) // 2
            for x in range(tx - w, tx + w + 1):
                for z in range(tz - w, tz + w + 1): put(x, 26 + k, z, 'deepslate_tiles' if k < 4 else GOLD)
        box(tx, 31, tz, tx, 33, tz, GOLD)
# ---------- 6. 丘の段: 滝・藤・桜 ----------
hill = {c for c, h in H.items() if h == 8 and abs(c[0]) <= 12 and 100 < c[1] < 160}
edges = sorted(c for c in hill if (c[0] + 1, c[1]) not in hill or (c[0] - 1, c[1]) not in hill)
falls = []
for s in (-1, 1):
    side = sorted((c for c in edges if c[0] * s > 4 and (c[0] + s, c[1]) not in hill and H.get((c[0] + s, c[1])) == 4 and not near_road(c[0], c[1], 3)), key=lambda c: c[1])
    for c in side[len(side) // 4: len(side) // 4 + 1] + side[len(side) * 2 // 3: len(side) * 2 // 3 + 1]:
        falls.append((c, s))
for (x, z), s in falls:
    put(x, 8, z, 'water')                                    # 上の水(まわりは床なので外へだけ流れる)
    put(x - s, 8, z, 'stone_bricks'); put(x, 8, z - 1, 'stone_bricks'); put(x, 8, z + 1, 'stone_bricks')
    V.pop((x, 9, z), None)
    for (i, j) in ((1, 0), (2, 0), (1, -1), (1, 1), (2, -1), (2, 1)):   # 下の受け池(水の上に落ちると広がらない)
        c = (x + s * i, z + j)
        if H.get(c) == 4 and c not in ROAD: put(c[0], 4, c[1], 'water'); put(c[0], 3, c[1], 'stone_bricks'); V.pop((c[0], 5, c[1]), None)
    for (i, j) in ((3, -1), (3, 0), (3, 1), (1, -2), (2, -2), (1, 2), (2, 2)):
        c = (x + s * i, z + j)
        if H.get(c) == 4 and c not in ROAD: put(c[0], 5, c[1], 'mossy_stone_bricks')
# 藤: 丘のがけの上のふちから紫が垂れる
for (x, z) in edges[::3]:
    if near_road(x, z, 2): continue
    s = 1 if (x + 1, z) not in hill else -1
    if H.get((x + s, z)) != 4: continue
    put(x, 9, z, 'azalea_leaves ["persistent_bit"=true]')
    for y in range(6, 9): put(x + s, y, z, 'purple_wool' if y > 6 else 'magenta_wool')
# 大きな桜(丘のまわりと野原)
for (x, z) in ((-9, wz(2) - 9), (9, wz(2) + 5), (-16, wz(-0.5)), (17, wz(1.5)), (-20, wz(3.8)), (21, wz(-1.2))):
    if (x, z) in H and not near_road(x, z, 3):
        G_clear_above(x - 4, z - 4, x + 4, z + 4, H[(x, z)] + 1, H[(x, z)] + 14, True)
        tree_(x, z, 'cherry', big=True)
