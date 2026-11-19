# 大きな帆船 + 甲板の DJ ブース(結果発表・集合の会場): mpl_board.py で ship_ のかわりに exec
#   参考: オークの船体に濃い木のもよう(ジグザグ)・金色の帯・大砲・船首の帆柱・船尾の高い船室、3 本のマストに段の白い帆(前へふくらむ)、
#   帆の上下の横木(金のふち)・見張り台・ロープ(段のはしご状)・てっぺんの旗
#   甲板の道のマスの列(z 57〜59)はそのまま。DJ ブースはその手前(z 53〜56)、人の列はさらに手前(z 51)
SHIP_X0, SHIP_X1 = -54, -2                 # 船尾(西) 〜 船首(東)
SHIP_CZ, SHIP_HW = 53, 6                   # まんなかの z とはば(半分)
DECK = 2                                    # 甲板(上の面は 3)
_sr = random.Random(41)
def _hw(x):
    t = (x - SHIP_X0) / (SHIP_X1 - SHIP_X0)            # 0 船尾 → 1 船首
    if t < 0.08: return SHIP_HW - 1
    if t > 0.62: return max(1, round(SHIP_HW * (1 - ((t - 0.62) / 0.38) ** 1.7)))
    return SHIP_HW
def _line(p, q, b):
    n = max(abs(q[0] - p[0]), abs(q[1] - p[1]), abs(q[2] - p[2]))
    for k in range(n + 1):
        c = tuple(round(p[i] + (q[i] - p[i]) * k / max(1, n)) for i in range(3))
        if (c[0], c[2]) not in ROAD or c[1] > DECK + 3: put(*c, b)
# ---- 船体 ----
for x in range(SHIP_X0, SHIP_X1 + 1):
    hw = _hw(x)
    for z in range(SHIP_CZ - hw, SHIP_CZ + hw + 1):
        edge = abs(z - SHIP_CZ) == hw or x in (SHIP_X0, SHIP_X1)
        bottom = -3 if abs(z - SHIP_CZ) < hw - 1 else -2
        for y in range(bottom, DECK + 1):
            if (x, z) in ROAD and y >= DECK: continue
            if edge:
                # 外がわのもよう: 下はこい木、まんなかに金の帯、上にジグザグ
                if y <= -1: b = 'dark_oak_planks'
                elif y == 0: b = 'stripped_oak_log' if x % 6 else 'dispenser ["facing_direction"=3]' if z > SHIP_CZ else 'dispenser ["facing_direction"=2]'
                elif y == 1: b = 'honeycomb_block' if (x // 2) % 2 == 0 else 'oak_planks'
                else: b = 'dark_oak_planks' if ((x + y) // 2) % 3 == 0 else 'oak_planks'
                put(x, y, z, b)
            elif y == DECK: put(x, y, z, 'spruce_planks')
            else: V.pop((x, y, z), None) if y > -1 else put(x, y, z, 'dark_oak_planks')
        if abs(z - SHIP_CZ) == hw and (x, z) not in ROAD:                       # 手すり(柱 + さく)
            put(x, DECK + 1, z, 'oak_planks' if x % 4 == 0 else 'oak_fence')
            if x % 4 == 0: put(x, DECK + 2, z, 'lantern')
# ---- 船尾の高い船室(西): 2 階・窓・バルコニー・旗 ----
for x in range(SHIP_X0, SHIP_X0 + 9):
    hw = _hw(x)
    for z in range(SHIP_CZ - hw, SHIP_CZ + hw + 1):
        if (x, z) in ROAD: continue
        edge = abs(z - SHIP_CZ) == hw or x in (SHIP_X0, SHIP_X0 + 8)
        for y in range(DECK + 1, DECK + 7):
            if edge: put(x, y, z, 'dark_oak_planks' if y in (DECK + 3, DECK + 6) else ('glass' if (y in (DECK + 1, DECK + 2, DECK + 4, DECK + 5) and (z + x) % 3 == 0) else 'oak_planks'))
        put(x, DECK + 7, z, 'spruce_planks')
        if edge: put(x, DECK + 8, z, 'oak_fence')
    put(SHIP_X0 + 4, DECK + 8, SHIP_CZ, 'lantern')
box(SHIP_X0 + 1, DECK + 8, SHIP_CZ, SHIP_X0 + 1, DECK + 14, SHIP_CZ, 'spruce_fence')
for k, b in enumerate(['red_wool', 'white_wool', 'red_wool']): put(SHIP_X0 + 2 + k, DECK + 13, SHIP_CZ, b); put(SHIP_X0 + 2 + k, DECK + 14, SHIP_CZ, 'white_wool' if k % 2 == 0 else 'red_wool')
# ---- 船首の甲板(東)と帆柱 ----
for x in range(SHIP_X1 - 6, SHIP_X1 + 1):
    hw = _hw(x)
    for z in range(SHIP_CZ - hw, SHIP_CZ + hw + 1):
        if (x, z) in ROAD: continue
        put(x, DECK + 1, z, 'spruce_planks')
        if abs(z - SHIP_CZ) == hw: put(x, DECK + 2, z, 'oak_fence')
for k in range(13):                                           # 帆柱(ななめ上へ)
    put(SHIP_X1 + k, DECK + 2 + k // 2, SHIP_CZ, 'stripped_oak_log' if k % 3 else 'honeycomb_block')
BOW = (SHIP_X1 + 12, DECK + 8, SHIP_CZ)
# ---- マスト 3 本・段の帆・横木・見張り台・旗 ----
MASTS = [(-43, 24), (-34, 30), (-10, 26)]       # DJ ブース(x -31〜-13)のじゃまにならない位置
for (mx, mh) in MASTS:
    for y in range(-2, DECK + mh):
        if not ((mx, SHIP_CZ) in ROAD and DECK <= y <= DECK + 3): put(mx, y, SHIP_CZ, 'spruce_log')
    tiers = [(DECK + 5, DECK + 11, 6), (DECK + 13, DECK + 18, 5)] + ([(DECK + 20, DECK + 24, 4)] if mh >= 26 else [])
    for (y0, y1, w) in tiers:
        for z in range(SHIP_CZ - w - 1, SHIP_CZ + w + 2):              # 上の横木(金のふち)と下の横木
            put(mx, y1 + 1, z, 'stripped_spruce_log'); put(mx, y1 + 2, z, 'honeycomb_block' if abs(z - SHIP_CZ) % 2 == 0 else 'stripped_spruce_log')
            if abs(z - SHIP_CZ) <= w: put(mx, y0 - 1, z, 'stripped_spruce_log')
        for y in range(y0, y1 + 1):                                    # 帆: 前(東)へふくらむ
            t = (y - y0) / max(1, y1 - y0)
            bulge = 2 if 0.25 < t < 0.85 else 1
            for z in range(SHIP_CZ - w, SHIP_CZ + w + 1):
                if z == SHIP_CZ: continue
                put(mx + bulge, y, z, 'white_wool' if (z + y) % 5 else 'white_concrete')
                if bulge == 2: put(mx + 1, y, z, 'white_wool')
    for (ny, r) in ((DECK + 12, 1), (DECK + 19, 1)):                  # 見張り台
        for i in range(-r - 1, r + 2):
            for j in range(-r - 1, r + 2):
                put(mx + i, ny, SHIP_CZ + j, 'spruce_planks' if max(abs(i), abs(j)) <= r else 'oak_fence')
        put(mx, ny, SHIP_CZ, 'spruce_log')
    for k, b in enumerate(['white_wool', 'white_wool', 'red_wool']): put(mx + 1 + k, DECK + mh, SHIP_CZ, b)   # 旗
    put(mx, DECK + mh, SHIP_CZ, 'spruce_fence')
# ロープ(はしご状): マストの上から船首の帆柱・船尾・左右のへりへ
for i, (mx, mh) in enumerate(MASTS):
    top = (mx, DECK + mh - 2, SHIP_CZ)
    if i == len(MASTS) - 1: _line(top, BOW, 'dark_oak_fence')
    else: _line(top, (MASTS[i + 1][0], DECK + MASTS[i + 1][1] - 2, SHIP_CZ), 'dark_oak_fence')
    for s in (-1, 1): _line((mx, DECK + 12, SHIP_CZ + s * 2), (mx - 3, DECK + 2, SHIP_CZ + s * (_hw(mx - 3))), 'dark_oak_fence')
_line((MASTS[0][0], DECK + MASTS[0][1] - 2, SHIP_CZ), (SHIP_X0 + 2, DECK + 8, SHIP_CZ), 'dark_oak_fence')

# ---- 甲板の DJ ブース(結果発表・集合の会場) ----
DJX, DJZ = -22, 55                          # DJ の立つ場所(まんなか。マストとマストのあいだ)
Y3 = DECK + 1                               # 甲板の上
for x in range(DJX - 9, DJX + 10):          # ステージの床(黒)と前のふちの光
    for z in range(DJZ - 2, DJZ + 2):
        if (x, z) not in ROAD: put(x, DECK, z, 'polished_deepslate' if (x + z) % 2 else 'black_concrete')
    if x % 2 == 0 and (x, DJZ - 3) not in ROAD: put(x, DECK, DJZ - 3, 'sea_lantern')
# うしろの光る壁(LED)のわく。中の 5 列 x 4 段はゲーム中に動く(BD.dj.eq)
for x in range(DJX - 5, DJX + 6):
    for y in range(Y3, Y3 + 7):
        frame = x in (DJX - 5, DJX + 5) or y in (Y3, Y3 + 6)
        put(x, y, DJZ + 1, 'black_concrete' if frame else ('sea_lantern' if (x + y) % 2 else 'light_blue_stained_glass'))
EQ = {'x0': DJX - 2, 'y0': Y3 + 1, 'z': DJZ + 1, 'w': 5, 'h': 4}
# DJ 卓: 鉄の台にターンテーブル 2 つとミキサー、前は光る板
for x in range(DJX - 2, DJX + 3):
    put(x, Y3, DJZ - 1, 'iron_block' if abs(x - DJX) == 2 else 'black_concrete')
    put(x, Y3 + 1, DJZ - 1, 'heavy_weighted_pressure_plate' if abs(x - DJX) == 1 else ('amethyst_block' if x == DJX else 'polished_blackstone_slab'))
put(DJX, Y3, DJZ - 2, 'pearlescent_froglight')
# スピーカー(左右): 黒い台の上に、スピーカーの顔(溶鉱炉の前)を 3 段 x 2 列
for s in (-1, 1):
    for i in range(3):
        x = DJX + s * (6 + i)
        for z in (DJZ - 1, DJZ):
            put(x, Y3, z, 'black_concrete')
            for y in range(Y3 + 1, Y3 + 5 - (i == 2)): put(x, y, z, 'blast_furnace ["minecraft:cardinal_direction"="north"]' if z == DJZ - 1 else 'black_concrete')
        put(x, Y3 + 5 - (i == 2), DJZ - 1, 'end_rod ["facing_direction"=1]' if i == 1 else 'black_concrete')
DJ = {'x': DJX + 0.5, 'y': Y3, 'z': DJZ + 0.5, 'cam': {'x': DJX + 0.5, 'y': Y3 + 2.4, 'z': DJZ - 6}}
STAGE = {'x': DJX + 0.5, 'y': Y3, 'z': DJZ - 4 + 0.5}          # 人の列(DJ ブースの前)
SHIP_GHOST_Z = SHIP_CZ - SHIP_HW - 6                            # 幽霊船が止まる z(船の外がわ)
