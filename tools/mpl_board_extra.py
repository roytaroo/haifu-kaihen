# v55 の島の追加(mpl_board.py で mpl_board_grand.py のあとに exec)
#   灯台(夕暮れに光が回る: mmgplus:beam)・風車の羽を回るモデルに(mmgplus:windmill)・広場の噴水に女神像・分かれ道の地面の矢印(mmgplus:waysign)・カモメの輪のまんなか
WAYNAMES = ['浜辺を進む', '船に乗る', '沖の桟橋', 'ドローブリッジ', 'ふもとの道', '火山にのぼる', '神殿の近道', '森の道', '木の上の道']   # tools/mpl_extras.py の WAYS と同じ順

# ---- 灯台: 東の海ぞい、道から離れた砂の上。白と赤のしま・鉄の見はり台・ガラスのランプ室・赤い屋根 ----
def lighthouse2(x, z):
    y = H[(x, z)]
    for k in range(18):
        r = 3 if k < 6 else (2.6 if k < 12 else 2.2)
        for i in range(-3, 4):
            for j in range(-3, 4):
                d = math.hypot(i, j)
                if d <= r + 0.3: put(x + i, y + 1 + k, z + j, ('red_concrete' if (k // 3) % 2 else 'white_concrete') if d > r - 1.1 else 'air')
        if k in (5, 11): put(x + (3 if k == 5 else 2), y + 1 + k, z, 'glass_pane')            # 小さい窓
    for i in range(-3, 4):                                                                   # 見はり台(鉄の床 + 手すり)
        for j in range(-3, 4):
            if i * i + j * j <= 10: put(x + i, y + 19, z + j, 'polished_andesite')
            if 7 <= i * i + j * j <= 10: put(x + i, y + 20, z + j, 'iron_bars')
    for i in range(-1, 2):
        for j in range(-1, 2):
            put(x + i, y + 20, z + j, 'glass'); put(x + i, y + 21, z + j, 'glass')
    put(x, y + 20, z, 'sea_lantern'); put(x, y + 21, z, 'sea_lantern')
    for i in range(-2, 3):
        for j in range(-2, 3):
            if abs(i) + abs(j) <= 3: put(x + i, y + 22, z + j, 'red_concrete')
    for i in range(-1, 2):
        for j in range(-1, 2): put(x + i, y + 23, z + j, 'red_concrete')
    put(x, y + 24, z, 'red_concrete'); put(x, y + 25, z, 'lightning_rod')
    put(x, y + 1, z - 3, 'spruce_door ["direction"=3]'); put(x, y + 2, z - 3, 'spruce_door ["upper_block_bit"=true,"direction"=3]')
    return {'x': x + 0.5, 'y': y + 20.6, 'z': z + 0.5}
LIGHT = None
_best = None
for (x, z), h in H.items():
    if h is None or h < 0 or x < 40: continue
    if any((x + i, z + j) not in H or H[(x + i, z + j)] != h for i in range(-3, 4) for j in range(-3, 4)): continue
    if near_road(x, z, 7) or any((x + i, y, z + j) in V for i in range(-4, 5) for j in range(-4, 5) for y in range(h + 1, h + 26)): continue
    sea = min((abs(i) + abs(j) for i in range(-10, 11) for j in range(-10, 11) if (x + i, z + j) not in H), default=99)
    if sea < 5: continue
    sc = sea + abs(z - wz(-5)) * 0.05
    if _best is None or sc < _best[0]: _best = (sc, x, z)
if _best: LIGHT = lighthouse2(_best[1], _best[2])

# ---- 風車: 白い帆の羽(ブロック)を消して、回るモデルを置く ----
WINDMILL = None
_wx, _wz = -19, wz(-2)
if (_wx, _wz) in H:
    _y0 = H[(_wx, _wz)]
    for i in range(-9, 10):
        for j in range(-9, 10):
            if V.get((_wx + i, _y0 + 8 + j, _wz - 5), '').split(' ')[0] in ('white_wool', 'spruce_fence'): V.pop((_wx + i, _y0 + 8 + j, _wz - 5), None)
    WINDMILL = {'x': _wx + 0.5, 'y': _y0 + 8.5, 'z': _wz - 5.2}

# ---- 広場の噴水: まんなかの柱を女神像にする(台座 → すそが広がる白い服 → 体 → 顔 → 金の髪、右手に光る星)。夜は水の中のあかりで光る ----
for y in range(1, 9): V.pop((PCX, y, PCZ), None)
for (i, j) in ((1, 0), (-1, 0), (0, 1), (0, -1)): V.pop((PCX + i, 4, PCZ + j), None); V.pop((PCX + i, 3, PCZ + j), None)
box(PCX - 1, 1, PCZ - 1, PCX + 1, 1, PCZ + 1, 'chiseled_quartz_block'); box(PCX - 1, 2, PCZ - 1, PCX + 1, 2, PCZ + 1, 'quartz_bricks')
for (i, j) in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)): put(PCX + i, 3, PCZ + j, 'calcite')                 # すそ
for (i, j) in ((1, 0), (-1, 0), (0, 0)): put(PCX + i, 4, PCZ + j, 'calcite')
put(PCX, 5, PCZ, 'calcite'); put(PCX, 6, PCZ, 'smooth_quartz')                                                   # 体
put(PCX - 1, 6, PCZ, 'smooth_quartz'); put(PCX + 1, 6, PCZ, 'smooth_quartz'); put(PCX + 1, 7, PCZ, 'smooth_quartz'); put(PCX + 1, 8, PCZ, 'smooth_quartz')   # 両腕(右手を上へ)
put(PCX, 7, PCZ, 'white_concrete'); put(PCX, 8, PCZ, 'gold_block'); put(PCX, 7, PCZ + 1, 'gold_block')           # 顔・髪
put(PCX + 1, 9, PCZ, 'glowstone')                                                                                 # 右手の星
put(PCX - 1, 5, PCZ, 'calcite'); put(PCX - 1, 5, PCZ + 1, 'quartz_slab')                                          # 左手で服のすそを持つ
for (i, j) in ((2, 1), (-2, -1), (1, -2), (-1, 2)):
    if V.get((PCX + i, 1, PCZ + j)) == 'water': put(PCX + i, 0, PCZ + j, 'sea_lantern')                          # 水の中のあかり

# ---- 分かれ道の地面の矢印: 分かれ道のマスから、それぞれの道の方へ 3 ブロック先(道の上) ----
WAYSIGNS = []
for nd in nodes:
    if len(nd['next']) < 2: continue
    for j in nd['next']:
        b = nodes[j]; w = b.get('way')
        if not w: continue
        k = next((i for i, n in enumerate(WAYNAMES) if w.startswith(n)), None)
        if k is None: continue
        dx, dz = (b['x'] > nd['x']) - (b['x'] < nd['x']), (b['z'] > nd['z']) - (b['z'] < nd['z'])
        cx, cz = nd['x'] + dx * 3, nd['z'] + dz * 3
        y = ROAD.get((cx, cz), nd['y'])
        WAYSIGNS.append([cx + 0.5, y + 1, cz + 0.5, round(math.degrees(math.atan2(-dx, dz))), k])
# ---- カモメ: 浜・港・船の上をまわる(輪のまんなか、高さ)----
GULLS = [[wx(5), 15, wz(-8)], [wx(-6), 18, wz(-8)], [-30, 24, 52], [wx(7), 20, wz(1)]]
print('extra: light', LIGHT, 'windmill', WINDMILL, 'waysigns', len(WAYSIGNS))
