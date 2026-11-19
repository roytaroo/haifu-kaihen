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

# ===================== v51: 参考画像からの作り直し =====================
def _ring(cx, y, cz, r0, r1, b):
    R = int(r1) + 1
    for x in range(cx - R, cx + R + 1):
        for z in range(cz - R, cz + R + 1):
            d = math.hypot(x - cx, z - cz)
            if r0 <= d <= r1: put(x, y, z, b() if callable(b) else b)

def mushroom(x, z, red=True, h=None):
    """大きなキノコ: ジグザグの柄(ところどころにクモの巣)・かさの裏のひだ(灰色)・段のかさ(赤に白い水玉 / 茶色はひらたく大きい)
    ・根もとは茶色い土(ポドゾル・荒れた土)に小さなキノコ・たおれた丸太と切り株"""
    y = _y(x, z)
    if y is None: return
    h = h or _dr.randint(10, 13)
    for i in range(-5, 6):                                       # 根もとの土(ふちはぎざぎざ)
        for j in range(-5, 6):
            d = math.hypot(i, j) + _dr.random() * 1.6
            c = (x + i, z + j)
            if d < 5.2 and c in H and c not in ROAD and H[c] == y:
                put(c[0], y, c[1], _dr.choice(['podzol', 'coarse_dirt', 'podzol', 'rooted_dirt']))
                if _dr.random() < 0.07: put(c[0], y + 1, c[1], 'red_mushroom' if _dr.random() < 0.6 else 'brown_mushroom')
    for (i, j, b) in ((3, -2, 'oak_log ["pillar_axis"="x"]'), (4, -2, 'oak_log ["pillar_axis"="x"]'), (-3, 3, 'oak_log'), (-3, 2, 'oak_log ["pillar_axis"="z"]')):   # たおれた丸太と切り株
        if (x + i, z + j) not in ROAD and (x + i, z + j) in H: put(x + i, H[(x + i, z + j)] + 1, z + j, b)
    cx, cz = x, z; stem = 'mushroom_stem ["huge_mushroom_bits"=15]'
    for k in range(1, h + 1):                                    # ジグザグの柄(3 段ごとに横へずれる・ずれる所は 2 つ並ぶ)
        if k in (4, 8):
            nx = cx + (1 if k == 4 else 0); nz = cz + (0 if k == 4 else 1)
            put(cx, y + k, cz, stem); cx, cz = nx, nz
        put(cx, y + k, cz, stem)
        if k == 6: 
            for (i, j) in ((1, 0), (-1, 0)): put(cx + i, y + k, cz + j, 'cobweb')
    put(x, y + 1, z + 1, stem); put(x + 1, y + 1, z, stem)        # 根もとのふくらみ
    top = y + h
    if red:
        r = 5
        _ring(cx, top, cz, 0, r - 1.2, 'smooth_stone')            # ひだ
        cap = 'red_mushroom_block ["huge_mushroom_bits"=14]'
        for (dy, rr) in ((1, r + 0.4), (2, r), (3, r - 0.8), (4, r - 2.2)):
            _ring(cx, top + dy, cz, 0, rr, cap)
        _ring(cx, top, cz, r - 1.0, r + 0.4, cap)                  # ふちが下へたれる
        for _ in range(14):                                       # 白い水玉(上と横)
            a = _dr.random() * math.tau; rr = _dr.uniform(1, r)
            dy = 4 if rr < r - 2.2 else 3 if rr < r - 0.8 else 2
            put(round(cx + math.cos(a) * rr), top + dy, round(cz + math.sin(a) * rr), 'white_concrete')
    else:
        r = 6                                                     # 茶色: ひらたく大きい・下にとがった岩がたれる
        _ring(cx, top, cz, 0, r - 1, 'smooth_stone')
        for (dy, rr) in ((1, r + 0.5), (2, r - 1.5)):
            _ring(cx, top + dy, cz, 0, rr, lambda: _dr.choice(['brown_mushroom_block ["huge_mushroom_bits"=14]'] * 3 + ['dark_oak_planks']))
        for a in range(0, 360, 45):
            px, pz = round(cx + math.cos(math.radians(a)) * (r - 1)), round(cz + math.sin(math.radians(a)) * (r - 1))
            for k in range(1, 3 + (a // 45) % 3): put(px, top + 1 - k, pz, 'pointed_dripstone ["dripstone_thickness"="tip","hanging"=true]' if k == 2 + (a // 45) % 3 else 'dripstone_block')

def cherry_big(x, z, scale=1.0):
    """大きな桜: 根が張る太い幹(ねじれながら上へ)・2〜3 本に分かれる枝・大きな花のかたまりがいくつも(ピンクのまぜ)・くさりでつるしたランタン"""
    y = _y(x, z)
    if y is None: return
    L = 'cherry_log'; LV = leaf('cherry')
    for (i, j, hh) in ((1, 0, 2), (-1, 0, 3), (0, 1, 2), (0, -1, 2), (2, 1, 1), (-2, -1, 1), (1, -2, 1)):   # 根
        c = (x + i, z + j)
        if c not in ROAD: box(c[0], y + 1, c[1], c[0], y + hh, c[1], L)
    H_ = round(9 * scale); cx, cz = float(x), float(z)
    for k in range(1, H_ + 1):                                    # ねじれる幹(下 3 段は 2x2)
        a = k * 0.55
        cx += math.cos(a) * 0.35; cz += math.sin(a) * 0.35
        put(round(cx), y + k, round(cz), L)
        if k <= 3: put(round(cx) + 1, y + k, round(cz), L); put(round(cx), y + k, round(cz) + 1, L)
    tops = []
    for b in range(3):                                            # 枝
        a = b * 2.1 + 0.4; bx, bz = cx, cz
        for k in range(1, round(5 * scale) + 1):
            bx += math.cos(a) * 0.9; bz += math.sin(a) * 0.9
            put(round(bx), y + H_ + k // 2, round(bz), L)
        tops.append((round(bx), y + H_ + round(5 * scale) // 2 + 1, round(bz)))
    tops.append((round(cx), y + H_ + 3, round(cz)))
    for (tx, ty, tz) in tops:                                      # 花のかたまり
        br = (4.2 if (tx, tz) != (round(cx), round(cz)) else 4.8) * scale
        R = int(br) + 1
        for i in range(-R, R + 1):
            for j in range(-R, R + 1):
                for k in range(-R, R + 1):
                    d = math.sqrt(i * i + j * j + (k * 1.5) ** 2)
                    if d <= br and not (d > br - 1 and _dr.random() < 0.3):
                        c = (tx + i, ty + k, tz + j)
                        if (c[0], c[2]) in ROAD: continue
                        put(*c, LV if _dr.random() < 0.82 else _dr.choice(['pink_wool', 'pink_concrete', 'magenta_wool']))
        for _ in range(3):                                          # たれる花
            a = _dr.random() * math.tau; c = (tx + round(math.cos(a) * br * 0.9), tz + round(math.sin(a) * br * 0.9))
            if c in ROAD: continue
            for k in range(1, _dr.randint(2, 4)): put(c[0], ty - round(br / 1.5) - k, c[1], LV)
    for _ in range(int(7 * scale)):                                 # くさりでつるしたランタン(花のかたまりの下)
        tx, ty, tz = _dr.choice(tops)
        a = _dr.random() * math.tau; rr = _dr.uniform(1.5, 3.5) * scale
        c = (tx + round(math.cos(a) * rr), tz + round(math.sin(a) * rr))
        if c in ROAD: continue
        yb = ty - round(3 * scale / 1.5) - 1
        for k in range(_dr.randint(1, 3)): put(c[0], yb - k, c[1], 'chain')
        put(c[0], yb - 3, c[1], 'lantern ["hanging"=true]')

_old_tree_v49 = tree_
def tree_(x, z, kind='oak', big=False):
    """木(参考の作り): 桜はねじれた幹と花のかたまり、ヤシ以外の大きい木は根が張る(段になって広がる)幹 + 枝の先の葉の台 + つるしたランタン"""
    if kind == 'cherry': return cherry_big(x, z, 0.75 if not big else 1.0)
    y = _y(x, z)
    if y is None or y < 0: return
    if kind == 'spruce' or not big: return _old_tree_v49(x, z, kind, big)
    log = {'oak': 'oak_log', 'birch': 'birch_log', 'jungle': 'jungle_log'}.get(kind, 'oak_log')
    for (i, j, hh) in ((1, 0, 3), (-1, 0, 2), (0, 1, 2), (0, -1, 3), (2, 0, 1), (-2, 1, 1), (1, 2, 1), (-1, -2, 1)):   # 根(段になって広がる)
        c = (x + i, z + j)
        if c not in ROAD and c in H: box(c[0], H[c] + 1, c[1], c[0], y + hh, c[1], log)
    hgt = _dr.randint(9, 12)
    box(x, y + 1, z, x, y + hgt, z, log)
    pads = [(0, hgt + 1, 0, 3.4)]
    for a in (0.3, 2.4, 4.3):                                       # 枝と葉の台(ひらたい)
        r0 = _dr.uniform(2.5, 3.5); ky = _dr.randint(hgt - 4, hgt - 1)
        ex, ez = round(math.cos(a) * r0), round(math.sin(a) * r0)
        for t in range(1, 4): put(x + round(ex * t / 3), y + ky + (t > 1), z + round(ez * t / 3), log)
        pads.append((ex, ky + 2, ez, 2.6))
    for (px, py, pz, pr) in pads:
        R = int(pr) + 1
        for i in range(-R, R + 1):
            for j in range(-R, R + 1):
                for k in (-1, 0, 1):
                    d = math.hypot(i, j) + abs(k) * 1.3
                    if d <= pr and not (d > pr - 0.8 and _dr.random() < 0.3):
                        c = (x + px + i, y + py + k, z + pz + j)
                        if (c[0], c[2]) not in ROAD and c not in V: put(*c, leaf(kind))
        if (px, pz) != (0, 0) and _dr.random() < 0.7:                # 枝の先のランタン
            c = (x + px + 1, z + pz)
            if c not in ROAD: put(c[0], y + py - 2, c[1], 'chain'); put(c[0], y + py - 3, c[1], 'lantern ["hanging"=true]')

def palm(x, z):
    """ヤシ(参考の作り): ジグザグに曲がる幹(2 段ごとに 1 ずれる)・6 方向の葉・実"""
    y = _y(x, z)
    if y is None: return
    hgt = _dr.randint(8, 11); dx = _dr.choice([1, -1]); cx = x
    for k in range(hgt):
        if k > 1 and k % 2 == 0: cx += dx
        put(cx, y + 1 + k, z, 'jungle_log')
        if k > 1 and k % 2 == 0: put(cx - dx, y + 1 + k, z, 'jungle_log')
    tx, ty = cx, y + hgt
    put(tx, ty + 1, z, leaf('jungle')); put(tx, ty + 2, z, leaf('jungle'))
    for (i, j) in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        for t in range(1, 5 if abs(i) + abs(j) == 1 else 4):
            put(tx + i * t, ty + 1 - (t * t) // 5, z + j * t, leaf('jungle'))
        put(tx + i * 4 if abs(i) + abs(j) == 1 else tx + i * 3, ty - 2, z + j * 4 if abs(i) + abs(j) == 1 else z + j * 3, leaf('jungle'))
    put(tx + 1, ty - 1, z, 'brown_terracotta'); put(tx, ty - 1, z + 1, 'brown_terracotta')

def witch_house(nd):
    """魔女の帽子の家: 1 階は木のわく + 青い壁(アーチの窓・扉)・オレンジの土台、緑の段のスカート、2 階は木のわく + 大きな丸い目の窓(紫)、
    つばの広い帽子(緑・水色・ピンクのまだら)の先が横へまがり、先に紫の三日月と光る星。柱にくさりのランタン。扉からガイコツが出る"""
    n = nd['n']; t = [-n[1], n[0]]; y = nd['y']
    P = lambda a, b: (nd['x'] + n[0] * a + t[0] * b, nd['z'] + n[1] * a + t[1] * b)
    CA = 9                                                          # 家のまんなか(道から 9)
    def oct_cells(r):
        out = []
        for a in range(CA - 8, CA + 9):
            for b in range(-8, 9):
                da, db = abs(a - CA), abs(b)
                if max(da, db) <= r and da + db <= r * 1.42: out.append((a, b, max(da, db) == r or da + db >= r * 1.42 - 0.9))
        return out
    for a in range(2, 17):                                          # 土地をあける
        for b in range(-8, 9):
            x, z = P(a, b); clear(x, y + 1, z, x, y + 40, z)
    for (a, b, e) in oct_cells(6.5):                                 # 1 階
        x, z = P(a, b); put(x, y, z, 'orange_terracotta' if e else 'spruce_planks')
        if not e: continue
        corner = abs(abs(a - CA) - abs(b)) <= 1 or (a - CA == 0) or b == 0
        for k in range(1, 7):
            if corner and (a - CA != -6 or b != 0): put(x, y + k, z, 'stripped_spruce_log')
            else: put(x, y + k, z, 'blue_terracotta' if k not in (3, 4) or (a + b) % 3 else 'light_blue_stained_glass')
        put(x, y + 7, z, 'spruce_planks')
    fx, fz = P(CA - 6, 0)                                           # 正面の扉(アーチ)
    for k in range(1, 5): V.pop((fx, y + k, fz), None)
    for bb in (-1, 1):
        for k in range(1, 6): put(*(lambda c: (c[0], y + k, c[1]))(P(CA - 6, bb)), 'stripped_spruce_log')
    put(*(lambda c: (c[0], y + 5, c[1]))(P(CA - 6, 0)), 'spruce_planks')
    for bb in (-4, 4):                                              # 柱のランタン(くさり)
        c = P(CA - 7, bb); put(c[0], y + 6, c[1], 'chain'); put(c[0], y + 5, c[1], 'lantern ["hanging"=true]')
    for k, r in enumerate((7.5, 6.8, 6.0)):                         # 緑の段のスカート
        for (a, b, e) in oct_cells(r):
            if e or k == 2:
                x, z = P(a, b); put(x, y + 7 + k, z, _dr.choice(['green_terracotta', 'cyan_terracotta', 'lime_terracotta', 'green_terracotta']))
    for (a, b, e) in oct_cells(7.5):
        if e: x, z = P(a, b); put(x, y + 7, z, 'spruce_planks')
    for (a, b, e) in oct_cells(4.5):                                 # 2 階
        x, z = P(a, b)
        if not e: put(x, y + 10, z, 'spruce_planks'); continue
        for k in range(10, 17): put(x, y + k, z, 'stripped_spruce_log' if (abs(a - CA) == abs(b) or b == 0 and a != CA - 4) else 'spruce_planks')
    for bb in range(-3, 4):                                          # 丸い目の窓(前)
        for k in range(10, 17):
            r = math.hypot(bb, k - 13)
            x, z = P(CA - 4, bb)
            if r <= 3.2: put(x, y + k, z, 'calcite' if r > 2.2 else ('purple_concrete' if r > 1.1 else 'crying_obsidian'))
    for (a, b, e) in oct_cells(5.5):                                 # 2 階の上のふち(光る帯)
        if e: x, z = P(a, b); put(x, y + 17, z, 'sea_lantern' if (a + b) % 3 == 0 else 'spruce_planks')
    for (a, b, e) in oct_cells(7.0):                                 # 帽子のつば
        x, z = P(a, b); put(x, y + 18, z, 'spruce_planks' if e else 'green_terracotta')
    HAT = 20                                                        # 帽子(円すい、上ほど横へまがる)
    for k in range(HAT):
        r = 5.6 * (1 - k / HAT) ** 0.9
        off = (k / HAT) ** 2.2 * 7
        ca, cb = CA, -off
        for a in range(int(ca - r) - 1, int(ca + r) + 2):
            for b in range(int(cb - r) - 1, int(cb + r) + 2):
                if math.hypot(a - ca, b - cb) <= r + 0.3:
                    x, z = P(a, b)
                    m = (a * 7 + b * 3 + k) % 11
                    put(x, y + 19 + k, z, 'pink_terracotta' if m == 0 or (k > 10 and m < 3) else 'lime_terracotta' if m in (3, 4) else 'cyan_terracotta' if k < 6 and m < 7 else 'green_terracotta')
    tip_b = -7
    for s in range(6):                                              # 先の紫の三日月 + 光る星
        x, z = P(CA + (1 if s > 2 else 0), tip_b - s)
        put(x, y + 19 + HAT - 1 + (s // 2), z, 'purple_concrete' if s % 2 else 'amethyst_block')
    x, z = P(CA + 1, tip_b - 6); put(x, y + 19 + HAT + 2, z, 'sea_lantern'); put(x, y + 19 + HAT + 3, z, 'amethyst_cluster')
    dx_, dz_ = P(CA + 3, 3); put(dx_, y + 25, dz_, 'glass'); put(dx_, y + 26, dz_, 'spruce_planks')   # 帽子の窓
    nd['mirror'] = {'x': fx + 0.5, 'y': y + 1, 'z': fz + 0.5, 'nx': n[0], 'nz': n[1]}
