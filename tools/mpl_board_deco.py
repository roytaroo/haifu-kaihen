# 女神の島の小物(作りこみ版): mpl_board.py の最初の方で exec。同じ名前の関数(tree_ / palm / crystal / lamp)を置きかえ、新しい小物を足す
#   方針: 1〜2 ブロックの散らばった飾りは置かない。置くものは形・材料のまぜ・あかり・影まで作る
_dr = random.Random(23)
def _y(x, z): return H.get((x, z))
def _free_cells(cells):
    return all(c in H and c not in ROAD and c not in RESERVED and H[c] >= 0 for c in cells)
SLAB_TOP = lambda b: f'{b} ["minecraft:vertical_half"="top"]'

def lamp(x, z):
    """街灯: 彫った石の台座・黒い柱・上の台・左右に腕・腕からつるしたランタン"""
    y = _y(x, z)
    if y is None or (x, z) in ROAD or (x, z) in RESERVED or (x, y + 1, z) in V: return
    axis = (1, 0) if ((x + 1, z) not in ROAD and (x - 1, z) not in ROAD) else (0, 1)
    put(x, y + 1, z, 'chiseled_stone_bricks')
    box(x, y + 2, z, x, y + 4, z, 'polished_blackstone_wall')
    put(x, y + 5, z, 'polished_blackstone'); put(x, y + 6, z, 'polished_blackstone_wall'); put(x, y + 7, z, 'lantern')
    for s in (-1, 1):
        ax, az = x + axis[0] * s, z + axis[1] * s
        if (ax, az) in ROAD: continue
        put(ax, y + 5, az, SLAB_TOP('polished_blackstone_slab')); put(ax, y + 4, az, 'lantern ["hanging"=true]')

def tree_(x, z, kind='oak', big=False):
    """木: 根の張り出し・枝・いくつかの葉のかたまり(ふちはまばら)・下にたれる葉。spruce は段の円すい"""
    y = _y(x, z)
    if y is None or y < 0: return
    log = {'oak': 'oak_log', 'birch': 'birch_log', 'cherry': 'cherry_log', 'jungle': 'jungle_log', 'spruce': 'spruce_log'}[kind]
    hgt = _dr.randint(8, 11) if big else _dr.randint(5, 7)
    box(x, y + 1, z, x, y + hgt, z, log)
    for (i, j) in _dr.sample([(1, 0), (-1, 0), (0, 1), (0, -1)], 2 if big else 1):   # 根
        if (x + i, z + j) not in ROAD: put(x + i, y + 1, z + j, log)
    if kind == 'spruce':
        top = y + hgt + 2
        for k in range(hgt - 1):
            r = 1 + (k % 3 == 0) + (hgt - 1 - k) // 3
            yy = top - k
            for i in range(-r, r + 1):
                for j in range(-r, r + 1):
                    if i * i + j * j <= r * r + (0 if k % 3 else 1) and (x + i, yy, z + j) not in V and (x + i, z + j) not in ROAD and _dr.random() > 0.08:
                        put(x + i, yy, z + j, leaf('spruce'))
        box(x, y + hgt + 1, z, x, top + 1, z, leaf('spruce'))
        return
    blobs = [(0, 0, 0, 3.2 if big else 2.4)]
    for _ in range(3 if big else 2):
        a = _dr.random() * math.tau; r0 = 2.0 if big else 1.3
        blobs.append((round(math.cos(a) * r0), _dr.randint(-1, 1), round(math.sin(a) * r0), (2.4 if big else 1.8)))
    for (bx, by, bz, br) in blobs:                                  # 枝(葉のかたまりへ)
        if (bx, bz) != (0, 0):
            for t in range(1, 3): put(x + round(bx * t / 2), y + hgt - 2 + t, z + round(bz * t / 2), log)
        cy = y + hgt + by
        R = int(br) + 1
        for i in range(-R, R + 1):
            for j in range(-R, R + 1):
                for k in range(-R, R + 1):
                    d = math.sqrt(i * i + j * j + (k * 1.4) ** 2)
                    if d <= br and not (d > br - 0.9 and _dr.random() < 0.35):
                        c = (x + bx + i, cy + k, z + bz + j)
                        if c not in V and (c[0], c[2]) not in ROAD: put(*c, leaf(kind))   # 道の上には出さない
    if kind == 'cherry' or big:                                      # 下にたれる葉
        for _ in range(8 if big else 4):
            a = _dr.random() * math.tau; rr = (3.0 if big else 2.2)
            c = (x + round(math.cos(a) * rr), z + round(math.sin(a) * rr))
            for k in range(1, _dr.randint(2, 3)):
                p = (c[0], y + hgt - k, c[1])
                if p not in V and c not in ROAD: put(*p, leaf(kind))

def palm(x, z):
    """ヤシ: 少しまがった幹・6方向にたれる葉・ヤシの実"""
    y = _y(x, z)
    if y is None: return
    hgt = _dr.randint(6, 8); dx = _dr.choice([1, -1])
    cx_ = x
    for k in range(hgt):
        if k in (hgt // 2, hgt - 2): cx_ += dx
        put(cx_, y + 1 + k, z, 'jungle_log')
    tx, ty_ = cx_, y + hgt
    put(tx, ty_ + 1, z, leaf('jungle'))
    for (i, j) in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)):
        for t in range(1, 5):
            put(tx + i * t, ty_ + 1 - (t * t) // 6, z + j * t, leaf('jungle'))
    put(tx + 1, ty_ - 1, z, 'brown_terracotta'); put(tx, ty_ - 1, z + 1, 'brown_terracotta')

def crystal(x, z, h):
    """クリスタルの群れ: こんもりした台(アメジスト・芽)・かたむいた大きな結晶 1 本 + 小さい結晶 3 本・先はガラス・ふもとに光"""
    y = _y(x, z)
    if y is None: return
    for i in range(-2, 3):
        for j in range(-2, 3):
            if i * i + j * j <= 5 and (x + i, z + j) not in ROAD:
                put(x + i, y + 1, z + j, 'budding_amethyst' if (i + j) % 3 == 0 else 'amethyst_block')
    def shard(sx, sz, hh, lx, lz, r):
        for k in range(hh):
            ox, oz = round(lx * k / hh), round(lz * k / hh)
            rr = r if k < hh * 0.6 else max(0, r - 1)
            for i in range(-rr, rr + 1):
                for j in range(-rr, rr + 1):
                    if abs(i) + abs(j) <= rr: put(sx + ox + i, y + 2 + k, sz + oz + j, 'purple_stained_glass' if k >= hh - 2 else ('amethyst_block' if (k + i) % 3 else 'purple_stained_glass'))
        put(sx + lx, y + 2 + hh, sz + lz, 'amethyst_cluster')
    shard(x, z, h, _dr.choice([-1, 1]), _dr.choice([-1, 0, 1]), 1)
    for (i, j, hh) in ((2, 1, h // 2), (-2, 0, h // 2 + 1), (0, -2, h // 3 + 1)):
        shard(x + i, z + j, max(2, hh), i // 2, j // 2, 0)
    put(x, y + 1, z, 'pearlescent_froglight')

def ruins(x, z):
    """こわれた柱廊: 高さのちがう柱 3 本(柱頭つき)・2 本をつなぐはり・たおれた柱・苔"""
    y = _y(x, z)
    if y is None: return
    for k, (i, hh) in enumerate(((0, 7), (4, 5), (8, 2))):
        put(x + i, y + 1, z, 'chiseled_quartz_block')
        box(x + i, y + 2, z, x + i, y + 1 + hh, z, 'quartz_pillar')
        if hh > 3: put(x + i, y + 2 + hh, z, 'chiseled_quartz_block')
    box(x, y + 9, z, x + 4, y + 9, z, 'smooth_quartz'); put(x + 2, y + 10, z, 'quartz_slab')
    box(x + 2, y + 1, z + 3, x + 6, y + 1, z + 3, 'quartz_pillar ["pillar_axis"="x"]')   # たおれた柱
    for (i, j) in ((1, 1), (3, 2), (5, -1), (7, 1), (2, 4), (6, 4)):
        if (x + i, z + j) in H and (x + i, z + j) not in ROAD: put(x + i, _y(x + i, z + j), z + j, 'moss_block')

def umbrella(x, z, c1, c2):
    """パラソル: 柱・しまの日よけ(ドーム)・下にタオル 2 枚"""
    y = _y(x, z)
    box(x, y + 1, z, x, y + 4, z, 'birch_fence')
    for i in range(-2, 3):
        for j in range(-2, 3):
            d = math.hypot(i, j)
            if d <= 2.3: put(x + i, y + 5 if d > 1.2 else y + 6, z + j, f'{c1}_wool' if (math.atan2(j, i) * 4 / math.pi) % 2 < 1 else f'{c2}_wool')
    put(x, y + 7, z, 'white_wool')
    for (i, c) in ((-2, c1), (2, c2)):
        put(x + i, y + 1, z + 1, f'{c}_carpet'); put(x + i, y + 1, z + 2, f'{c}_carpet')

def boulder(x, z, r=2):
    """岩: まるい形・石のまぜ・上に苔"""
    y = _y(x, z)
    if y is None: return
    for i in range(-r, r + 1):
        for j in range(-r, r + 1):
            for k in range(0, r + 1):
                if i * i + j * j + (k * 1.6) ** 2 <= r * r + 0.6 and (x + i, z + j) not in ROAD:
                    put(x + i, y + 1 + k, z + j, 'moss_block' if k == r and _dr.random() < 0.6 else _dr.choice(['stone', 'andesite', 'cobblestone', 'mossy_cobblestone', 'tuff']))

def basalt_cluster(x, z):
    """玄武岩の柱の群れ: 高さのちがう柱が寄りあつまる・すきまにマグマ・まわりに黒い岩"""
    y = _y(x, z)
    if y is None: return
    for i in range(-2, 3):
        for j in range(-2, 3):
            if i * i + j * j > 5 or (x + i, z + j) in ROAD: continue
            g = _y(x + i, z + j) or y
            hh = max(1, 6 - (i * i + j * j) + _dr.randint(-1, 1))
            box(x + i, g + 1, z + j, x + i, g + hh, z + j, 'basalt' if (i + j) % 2 else 'polished_basalt')
            if (i, j) in ((1, 0), (-1, 1)): put(x + i, g + 1, z + j, 'magma_block')

def dead_tree(x, z):
    """枯れ木: こげた幹・ななめの枝 3 本"""
    y = _y(x, z)
    if y is None: return
    hh = _dr.randint(5, 7)
    box(x, y + 1, z, x, y + hh, z, 'dark_oak_log')
    for (i, j, k) in ((1, 0, 3), (-1, 1, 4), (0, -1, 5)):
        for t in range(1, 3): put(x + i * t, y + k + t, z + j * t, 'dark_oak_log')

def crates(x, z):
    """荷物: たるとわく木の箱を 2 段・上に麻袋・くさりでしばる"""
    y = _y(x, z)
    for (i, j, k, b) in ((0, 0, 1, 'barrel'), (1, 0, 1, 'spruce_planks'), (0, 1, 1, 'spruce_planks'), (1, 1, 1, 'barrel'), (0, 0, 2, 'spruce_planks'), (1, 0, 2, 'barrel'),
                         (0, 0, 3, 'white_wool'), (2, 0, 1, 'barrel'), (2, 1, 1, 'hay_block')):
        put(x + i, y + k, z + j, b)
    put(x + 1, y + 2, z + 1, 'chain')

def planter(x, z, w=5, d=3):
    """花だん(高くした): 石のふち・土・色の列の花・まんなかに小さな茂み"""
    y = _y(x, z)
    for i in range(w):
        for j in range(d):
            c = (x + i, z + j)
            if c in ROAD: continue
            edge = i in (0, w - 1) or j in (0, d - 1)
            put(c[0], y + 1, c[1], 'stone_bricks' if edge else 'dirt')
            if not edge: put(c[0], y + 2, c[1], ['pink_tulip', 'allium', 'oxeye_daisy', 'cornflower', 'azure_bluet', 'red_tulip'][(i + 2 * j) % 6])
    put(x + w // 2, y + 2, z + d // 2, leaf('azalea')); put(x + w // 2, y + 3, z + d // 2, leaf('azalea'))

def garden(fx, fz, w, d):
    """花畑: 石のふちでかこみ、色ごとの列のあいだに砂利の小道"""
    for x in range(fx, fx + w):
        for z in range(fz, fz + d):
            if H.get((x, z)) != 0 or near_road(x, z, 1) or (x, 1, z) in V: continue
            edge = x in (fx, fx + w - 1) or z in (fz, fz + d - 1)
            if edge: put(x, 0, z, 'stone_bricks'); put(x, 1, z, 'stone_brick_slab' if (x + z) % 3 else 'lantern'); continue
            if (x - fx) % 4 == 0: put(x, 0, z, 'gravel'); continue
            put(x, 0, z, 'grass_block')
            put(x, 1, z, ['red_tulip', 'orange_tulip', 'white_tulip', 'pink_tulip', 'cornflower', 'allium'][((x - fx) // 4) % 6])
