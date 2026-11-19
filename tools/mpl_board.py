# MPL のボード「女神の島」v2 を設計する(すべて自作)
#   全部を 6ブロックの格子にそろえる: マス(3x3)は格子の点、道(幅3)は格子の線の上だけ(斜めなし)→ ズレない
#   エリア: 港の広場(スタート)/ 浜辺 / 川 / 東のクリスタル台地(高さ6)/ 北の火山(高さ12、火口)/ 西の森(高さ3)と木の上の道(高さ7)/ 真ん中の女神の神殿(高さ8)/ 帆船
#   分かれ道 5つ: 船 / はね橋 / 火山 / 関所(神殿の近道)/ 木の上。通行止め: はね橋(奇数ターンは上がっている)、関所(コイン10)
#   場所ごとのハプニング: ev = volcano(噴火)/ cannon(大砲)/ wave(大波)/ spore(キノコジャンプ)/ crystal(クリスタルくじ)/ bless(女神の祝福)
#   出力: mpl_bp/scripts/board_data.js と見本 mpl/preview_board.png        python3 tools/mpl_board.py
import json, math, os, random
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JS = os.path.join(ROOT, 'mpl', 'src', 'behavior_packs', 'mpl_bp', 'scripts', 'board_data.js')
OUT_PNG = os.path.join(ROOT, 'mpl', 'preview_board.png')
random.seed(11)
G, ZC = 6, 124
X0, X1, Z0, Z1, YB, YT = -68, 64, 30, 196, -4, 48
wx = lambda gx: int(round(gx * G))
wz = lambda gz: int(round(ZC + gz * G))
V = {}
def put(x, y, z, b): V[(x, y, z)] = b
def box(x1, y1, z1, x2, y2, z2, b):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for z in range(min(z1, z2), max(z1, z2) + 1): V[(x, y, z)] = b
def clear(x1, y1, z1, x2, y2, z2):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for z in range(min(z1, z2), max(z1, z2) + 1): V.pop((x, y, z), None)
def leaf(k): return f'{k}_leaves ["persistent_bit"=true]'
# 作りこみ版の小物(tree_ / palm / crystal / lamp と、岩・遺跡・パラソル・荷物・花だん・花畑)
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mpl_board_deco.py'), encoding='utf-8').read())

# ===== マスと道(格子)=====
nodes, at = [], {}
def node(gx, gz, y, zone):
    if (gx, gz) in at: return at[(gx, gz)]
    at[(gx, gz)] = len(nodes); nodes.append({'g': (gx, gz), 'x': wx(gx), 'y': y, 'z': wz(gz), 'kind': 'blue', 'next': [], 'zone': zone}); return len(nodes) - 1
def route(pts, link_from=None, link_to=None):
    ids = [node(*p) for p in pts]
    seq = ([link_from] if link_from is not None else []) + ids + ([link_to] if link_to is not None else [])
    for a, b in zip(seq, seq[1:]):
        if b not in nodes[a]['next']: nodes[a]['next'].append(b)
    return ids
main = ([(0, -9, 0, 'port'), (1, -9, 0, 'port'), (2, -9, 0, 'port')] + [(x, -9, 0, 'beach') for x in range(3, 8)] + [(7, z, 0, 'beach') for z in range(-8, -3)]
        + [(7, -3, 3, 'cliff'), (7, -2, 6, 'cliff')] + [(7, z, 6, 'crystal') for z in range(-1, 7)] + [(6, 6, 6, 'crystal'), (5, 6, 6, 'crystal'), (4, 6, 6, 'foot')]
        + [(x, 6, 6, 'foot') for x in range(3, -8, -1)] + [(-7, 5, 6, 'forest')] + [(-7, z, 3, 'forest') for z in range(4, -4, -1)]
        + [(-7, z, 0, 'harbor') for z in range(-4, -10, -1)] + [(x, -9, 0, 'harbor') for x in range(-6, -2)] + [(-2, -9, 0, 'port'), (-1, -9, 0, 'port')])
M = route(main); nodes[M[-1]]['next'].append(M[0])
# 分かれ道(最初に書いた next が「本線」。あとから足すのが寄り道)
ship = route([(-6, -10, 1, 'ship'), (-6, -11, 2, 'ship'), (-5, -11, 2, 'ship'), (-4, -11, 2, 'ship'), (-3, -11, 2, 'ship'), (-3, -10, 1, 'ship')], at[(-6, -9)], at[(-3, -9)])
bridge = route([(5, -8, 0, 'beach'), (5, -7, 0, 'beach'), (5, -6, 0, 'beach'), (5, -5, 0, 'beach'), (5, -4, 0, 'beach'), (5, -3, 3, 'cliff'), (6, -3, 3, 'cliff')], at[(5, -9)], at[(7, -3)])
# 火山の道: 盛り上がった斜面にそって上り下りする(地面より1低い切り通し)
def vy(gx, gz): d = math.hypot(gx / 1.15, (gz - 9.8) / 0.75); return max(6, round(7 + max(0.0, 5.0 - d) ** 1.35 * 4.0) - 1)
volc = route([(4, 7, vy(4, 7) + 2, 'volcano'), (4, 8, vy(4, 8), 'volcano')] + [(x, 8, vy(x, 8), 'volcano') for x in range(3, -5, -1)] + [(-4, 7, vy(-4, 7) + 2, 'volcano')], at[(4, 6)], at[(-4, 6)])
center = route([(0, 5, 6, 'shrine'), (0, 4, 8, 'shrine'), (0, 3, 8, 'shrine'), (0, 2, 8, 'shrine'), (0, 1, 8, 'shrine'), (0, 0, 8, 'shrine'), (0, -1, 6, 'shrine'), (0, -2, 4, 'shrine'), (0, -3, 2, 'meadow'),
                (0, -4, 0, 'meadow'), (0, -5, 0, 'meadow'), (0, -6, 0, 'meadow'), (0, -7, 0, 'port'), (0, -8, 0, 'port')], at[(0, 6)], at[(0, -9)])
tree = route([(-8, 1, 5, 'tree'), (-9, 1, 7, 'tree'), (-9, 0, 7, 'tree'), (-9, -1, 7, 'tree'), (-9, -2, 7, 'tree'), (-9, -3, 7, 'tree'), (-8, -3, 5, 'tree')], at[(-7, 1)], at[(-7, -3)])
# 潮の道(満潮のときだけ開く。浜の外がわ、水びたしの中を進む。宝のマスがある)
tideway = route([(x, -10, 0, 'beach') for x in range(3, 8)], at[(3, -9)], at[(7, -9)])
def N(gx, gz): return nodes[at[(gx, gz)]]
for g, w in {(-5, -9): '浜辺を進む', (-6, -10): '船に乗る', (4, -9): '浜辺を進む', (3, -10): '潮の道(満潮だけ)', (6, -9): '浜辺を進む', (5, -8): 'ドローブリッジをわたる', (3, 6): 'ふもとの道', (4, 7): '火山にのぼる',
             (-1, 6): 'ふもとの道', (0, 5): '神殿の近道', (-7, 0): '森の道', (-8, 1): '木の上の道'}.items(): N(*g)['way'] = w
N(5, -8)['gate'] = 'bridge'; N(0, 5)['gate'] = 'toll'
KIND = {'shop': [(7, 2), (-5, 6), (-7, -6)], 'skull': [(0, 8), (-7, -1), (0, -3)], 'lucky': [(-9, -1), (-4, -11), (5, -6), (2, 8), (0, 0), (7, -7)],
        'red': [(6, -9), (7, -5), (7, 5), (1, 6), (-6, 6), (-7, 3), (-7, -8), (-4, -9), (0, 4), (0, -1), (-3, 8), (1, 8), (-9, -3), (5, -7), (-7, 5), (3, -9), (0, -7)],
        'event': [(-2, 6), (2, 6), (-7, -7), (-2, -9), (0, -6), (7, -8)]}
EV = {'volcano': [(-2, 8), (3, 8), (-1, 8)], 'cannon': [(-5, -11)], 'wave': [(4, -9), (-7, -5)], 'spore': [(-7, 2), (-9, 0)], 'crystal': [(7, 0), (7, 4), (5, 6)], 'bless': [(0, 2)]}
for k, lst in KIND.items():
    for g in lst: N(*g)['kind'] = k
for e, lst in EV.items():
    for g in lst: N(*g)['kind'] = 'event'; N(*g)['ev'] = e
nodes[0]['kind'] = 'start'
# v3: シャッフルマス・銀行マス(1つずつ)、火山のラッキーを増やす、潮で沈む浜の道
N(0, -6)['kind'] = 'shuffle'; N(0, -6).pop('ev', None)
N(1, -9)['kind'] = 'bank'
for g in [(1, 8), (-3, 8)]: N(*g)['kind'] = 'lucky'
N(-5, -9)['gate'] = 'tide'
N(3, -10)['gate'] = 'tidehigh'
for g in [(4, -10), (6, -10)]: N(*g)['kind'] = 'lucky'
N(7, 2)['n'] = [1, 0]; N(-5, 6)['n'] = [0, 1]; N(-7, -6)['n'] = [-1, 0]

# 道のセル: (x,z) → 高さ。マスは 3x3、マスの間 3セルで高さをつなぐ
ROAD, TILE = {}, {}
for nd in nodes:
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1): ROAD[(nd['x'] + dx, nd['z'] + dz)] = nd['y']; TILE[(nd['x'] + dx, nd['z'] + dz)] = nd
EDGE_ZONE = {}
for a in nodes:
    for j in a['next']:
        b = nodes[j]
        dx, dz = (b['x'] > a['x']) - (b['x'] < a['x']), (b['z'] > a['z']) - (b['z'] < a['z'])
        for k in range(2, 5):
            y = round(a['y'] + (b['y'] - a['y']) * (k - 1) / 3)
            for w in (-1, 0, 1):
                c = (a['x'] + dx * k + (w if dz else 0), a['z'] + dz * k + (w if dx else 0))
                ROAD[c] = y; EDGE_ZONE[c] = b['zone'] if b['zone'] in ('tree', 'ship', 'volcano', 'shrine') else a['zone']
def near_road(x, z, r=2): return any((x + i, z + j) in ROAD for i in range(-r, r + 1) for j in range(-r, r + 1))
RESERVED = set()
for nd in nodes:
    if nd['kind'] == 'shop':
        n = nd['n']; t = [-n[1], n[0]]
        for a in range(2, 9):
            for b in range(-4, 5): RESERVED.add((nd['x'] + n[0] * a + t[0] * b, nd['z'] + n[1] * a + t[1] * b))
RES_Y = {c: next(nd['y'] for nd in nodes if nd['kind'] == 'shop' and abs(nd['x'] - c[0]) < 10 and abs(nd['z'] - c[1]) < 10) for c in RESERVED}
# 鏡のマス(2つ): 道の横の空いた側に大きな鏡。中からガイコツが出てくる
MIRRORS = []
for gg in [(-7, -2), (0, -4), (7, 3), (-4, 6), (-7, 4)]:
    if len(MIRRORS) >= 2 or gg not in at: continue
    nd = N(*gg)
    if nd['kind'] != 'blue' or 'gate' in nd: continue
    for n in ([1, 0], [-1, 0], [0, 1], [0, -1]):
        t = [-n[1], n[0]]
        cells = [(nd['x'] + n[0] * a + t[0] * b, nd['z'] + n[1] * a + t[1] * b) for a in range(2, 7) for b in range(-3, 4)]
        if any(c in ROAD or c in RESERVED or not (X0 + 3 <= c[0] <= X1 - 3 and Z0 + 3 <= c[1] <= Z1 - 3) for c in cells): continue
        if any(c in ROAD for a in range(2, 7) for b in range(-3, 4) for c in [(nd['x'] + n[0] * a + t[0] * b + 0, nd['z'] + n[1] * a + t[1] * b)]): continue
        nd['kind'] = 'mirror'; nd['n'] = n; MIRRORS.append(nd)
        for c in cells: RESERVED.add(c); RES_Y[c] = nd['y']
        break

# ===== 地形 =====
def noise(x, z): return math.sin(x * 0.21 + z * 0.13) * 0.6 + math.sin(x * 0.07 - z * 0.19) * 0.9 + math.cos(z * 0.31) * 0.4
def inside(x, z):
    u, v = x / G, (z - ZC) / G
    return ((u + 0.3) / 10.6) ** 4 + ((v - 0.4) / 11.3) ** 4 < 1 + noise(x, z) * 0.04
RIV = [[(9, -1.4), (9, -4.5), (2.5, -4.5), (2.5, -11.6)]]
def river_d(x, z):
    u, v = x / G, (z - ZC) / G; best = 99
    for line in RIV:
        for (ax, az), (bx, bz) in zip(line, line[1:]):
            dx, dz = bx - ax, bz - az; t = max(0, min(1, ((u - ax) * dx + (v - az) * dz) / (dx * dx + dz * dz)))
            best = min(best, math.hypot(u - ax - dx * t, v - az - dz * t))
    return best * G
def vol(x, z): return math.hypot(x / G / 1.15, ((z - ZC) / G - 9.8) / 0.75)
RIM, CRATER = 26, 19          # 火山: 火口のふち・火口の底(溶岩はその1つ上)
def vh(d): return 7 + max(0.0, 5.0 - d) ** 1.35 * 4.0   # 火山の斜面(下はゆるく、上ほど急)
def sstep(a, b, t): t = max(0.0, min(1.0, (t - a) / (b - a))); return t * t * (3 - 2 * t)
def height(x, z):
    if not inside(x, z): return None
    u, v = x / G, (z - ZC) / G
    d = vol(x, z)
    if d < 1.0: return CRATER                      # 火口(溶岩)
    if d < 1.9: return RIM                         # 火口のふち
    if d < 5.0: return round(vh(d) + noise(x * 1.7, z * 1.7) * 0.6)   # 盛り上がった斜面(少しでこぼこ)
    hs = [6 * sstep(4.0, 4.6, v)]                                     # 北の台地(なだらかに上がる)
    hs.append(6 * sstep(3.0, 3.6, u) * sstep(-2.2, -1.6, v))          # 東のクリスタル台地
    hs.append(3 * sstep(-4.8, -5.4, u) * sstep(-4.2, -3.6, v) * (1 - sstep(4.0, 4.6, v)))   # 西の森
    s = max(abs(u) / 1.7, abs(v - 2) / 2.7)
    hs.append(8 if s < 1 else 8 * (1 - sstep(1.0, 1.5, s)))         # 神殿の丘(まわりは坂)
    h = max(hs)
    return int(round(h)) if h >= 0.5 else 0
H = {}
for x in range(X0, X1 + 1):
    for z in range(Z0, Z1 + 1):
        h = height(x, z)
        if h is None: continue
        if river_d(x, z) <= 2.6 and h <= 0: h = -3
        H[(x, z)] = h
for p in RESERVED:  # 屋台の場所は平らに
    if p in H: H[p] = RES_Y[p]
ZONE_TOP = lambda x, z, h: ('sand' if h <= 0 and (not all(inside(x + i, z + j) for i, j in ((5, 0), (-5, 0), (0, 5), (0, -5))) or (z - ZC) / G < -7.6) else
                            'blackstone' if vol(x, z) < 5.0 else 'moss_block' if h == 3 and x < -30 and noise(x * 2.3, z * 1.9) > 0.7 else 'grass_block')
def cliff_block(x, z, y):
    if vol(x, z) < 5.3: return random.choice(['blackstone', 'blackstone', 'basalt', 'deepslate', 'magma_block' if random.random() < 0.25 else 'blackstone'])
    if x >= 20: return random.choice(['stone', 'stone', 'andesite', 'calcite', 'tuff'])
    if abs(x) < 14 and 100 < z < 156: return 'stone_bricks' if random.random() < 0.85 else 'mossy_stone_bricks'
    return random.choice(['stone', 'cobblestone', 'mossy_cobblestone', 'stone', 'andesite'])
for (x, z), h in H.items():
    if h == -3:
        box(x, YB, z, x, -4, z, 'stone'); put(x, -3, z, 'sand'); put(x, -2, z, 'water'); put(x, -1, z, 'water'); put(x, 0, z, 'water'); continue   # 川の水面は浜と同じ高さ
    box(x, YB, z, x, -1, z, 'stone')
    low = min([H.get((x + i, z + j), -3) for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1))])
    for y in range(0, h): put(x, y, z, cliff_block(x, z, y) if y >= low else ('blackstone' if vol(x, z) < 5.3 else 'stone'))
    top = ZONE_TOP(x, z, h)
    if top in ('grass_block', 'moss_block') and h > 0: put(x, h - 1, z, 'dirt')
    put(x, h, z, top)
    if h == CRATER and vol(x, z) < 1.0: put(x, CRATER + 1, z, 'lava'); put(x, CRATER, z, 'magma_block')   # 火口の溶岩(ふちに囲まれている)
# 鏡: 金のわく(5x5)・中は黒いガラス + 奥に泣く黒曜石(紫に光る)・上にソウルランタン・前に黒い石の床
for nd in MIRRORS:
    n = nd['n']; t = [-n[1], n[0]]; y = nd['y']
    P = lambda a, b: (nd['x'] + n[0] * a + t[0] * b, nd['z'] + n[1] * a + t[1] * b)
    for a in range(2, 7):
        for b in range(-3, 4):
            x, z = P(a, b); clear(x, y + 1, z, x, y + 8, z)
    for a in (2, 3):
        for b in range(-2, 3): x, z = P(a, b); put(x, y, z, 'polished_blackstone_bricks' if (a + b) % 2 else 'deepslate_tiles')
    for b in range(-2, 3):
        for k in range(1, 6):
            x, z = P(4, b); edge = abs(b) == 2 or k in (1, 5)
            put(x, y + k, z, 'gold_block' if edge else 'black_stained_glass')
            x2, z2 = P(5, b); put(x2, y + k, z2, 'polished_blackstone' if edge else 'crying_obsidian')
    x, z = P(4, 0); put(x, y + 6, z, 'chiseled_polished_blackstone'); put(x, y + 7, z, 'soul_lantern')
    for b in (-3, 3): x, z = P(4, b); put(x, y + 1, z, 'polished_blackstone_wall'); put(x, y + 2, z, 'soul_lantern')
    nd['mirror'] = {'x': nd['x'] + n[0] * 4 + 0.5, 'y': y + 1, 'z': nd['z'] + n[1] * 4 + 0.5, 'nx': n[0], 'nz': n[1]}
# 海とふち: 水面は y=0(浜の砂と同じ高さ。段差なし)。岸の近くは浅く(底が上がる)、沖ほど深い → 水の色が自然に変わる
from collections import deque
SEA_D = {}; dq = deque()
for x in range(X0, X1 + 1):
    for z in range(Z0, Z1 + 1):
        if (x, z) in H: continue
        if any((x + i, z + j) in H and H[(x + i, z + j)] >= 0 for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1))): SEA_D[(x, z)] = 1; dq.append((x, z))
while dq:
    x, z = dq.popleft()
    for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        c = (x + i, z + j)
        if X0 <= c[0] <= X1 and Z0 <= c[1] <= Z1 and c not in H and c not in SEA_D: SEA_D[c] = SEA_D[(x, z)] + 1; dq.append(c)
for x in range(X0, X1 + 1):
    for z in range(Z0, Z1 + 1):
        if (x, z) in H: continue
        edge = x in (X0, X1) or z in (Z0, Z1)
        d = SEA_D.get((x, z), 99)
        floor = -1 if d <= 2 else -2 if d <= 5 else -4
        if edge:
            for y in range(-4, 1): put(x, y, z, 'prismarine_bricks')
            continue
        for y in range(-4, floor + 1): put(x, y, z, 'sand')
        for y in range(floor + 1, 1): put(x, y, z, 'water')
        if d <= 2 and random.random() < 0.06: put(x, floor, z, 'gravel')
# 火山の溶岩の筋(光るブロック。流れない)
for a in (-2.4, -1.2, 0.3, 1.5, 2.6):
    for k in range(80):
        d = 1.9 + k * 0.04
        x, z = round((math.sin(a) * d) * 1.15 * G), round(ZC + (9.8 - math.cos(a) * d * 0.75) * G)
        if (x, z) in H and not near_road(x, z, 1) and H[(x, z)] >= 7 and vol(x, z) < 5.0: put(x, H[(x, z)], z, 'magma_block' if k % 3 else 'shroomlight')
# 滝(東の台地のふちから川へ)
fx, fz = wx(9), wz(-1.6)
fz = int(fz)
box(fx - 2, 6, fz, fx + 2, 6, fz + 3, 'mossy_cobblestone'); box(fx - 1, 6, fz + 1, fx + 1, 6, fz + 2, 'water'); put(fx, 6, fz, 'water')
clear(fx - 1, 0, fz - 1, fx + 1, 6, fz - 1)

# ===== 道をしく =====
ROADMAT = {'port': 'smooth_sandstone', 'beach': 'smooth_sandstone', 'harbor': 'spruce_planks', 'cliff': 'polished_andesite', 'crystal': 'polished_andesite', 'foot': 'polished_deepslate',
           'forest': 'packed_mud', 'tree': 'spruce_planks', 'ship': 'spruce_planks', 'volcano': 'polished_blackstone_bricks', 'shrine': 'quartz_bricks', 'meadow': 'smooth_sandstone'}
COL = {'shuffle': 'pink_concrete', 'bank': 'cyan_concrete', 'start': 'white_concrete', 'blue': 'light_blue_concrete', 'red': 'red_concrete', 'event': 'lime_concrete', 'lucky': 'yellow_concrete', 'shop': 'purple_concrete', 'skull': 'black_concrete', 'mirror': 'amethyst_block'}
BRIDGE_BOX = None
for (x, z), y in ROAD.items():
    g = H.get((x, z))
    nd = TILE.get((x, z)); zone = nd['zone'] if nd else EDGE_ZONE[(x, z)]
    over_water = g is None or g == -3
    if g is not None and g > y:
        for i in range(-1, 2):
            for j in range(-1, 2):
                gg = H.get((x + i, z + j))
                if gg is not None and gg > y: clear(x + i, y + 1, z + j, x + i, gg + 1, z + j); H[(x + i, z + j)] = max(y, -3) if (x + i, z + j) not in ROAD else H[(x + i, z + j)]
                if gg is not None and gg > y and (x + i, z + j) not in ROAD: put(x + i, y, z + j, cliff_block(x + i, z + j, y))
    clear(x, y + 1, z, x, y + 4, z)
    put(x, y, z, ROADMAT[zone])   # マスの印はブロックでなく丸い台(mmgplus:space、main.js)
    lo = -2 if over_water else g
    if lo < y - 1:   # 浮いている道: 下を支える
        if zone in ('tree', 'ship', 'harbor') or over_water:
            if (x % 3 == 0 and z % 3 == 0): box(x, lo + 1, z, x, y - 1, z, 'spruce_log')
        else: box(x, lo + 1, z, x, y - 1, z, 'stone_bricks' if zone not in ('volcano', 'foot') else 'polished_blackstone_bricks')
# 道を敷く順番で、となりの道の処理が先に敷いた道ブロックを消すことがある → 最後にもう一度、道ブロックと上の空間をそろえる
for (x, z), y in ROAD.items():
    nd = TILE.get((x, z)); zone = nd['zone'] if nd else EDGE_ZONE[(x, z)]
    if (x, y, z) not in V: put(x, y, z, ROADMAT[zone])
    for yy in range(y + 1, y + 4):
        if V.get((x, yy, z), 'air') not in ('air', 'lantern') and not V.get((x, yy, z), '').startswith(('spruce_fence', 'lantern')): V.pop((x, yy, z), None)
# 橋・木の上の道の手すり(道の外側 1ブロック)
for (x, z), y in list(ROAD.items()):
    zone = TILE[(x, z)]['zone'] if (x, z) in TILE else EDGE_ZONE[(x, z)]
    g = H.get((x, z)); over = g is None or g == -3 or zone == 'tree'
    if not over: continue
    for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        c = (x + i, z + j)
        if c in ROAD: continue
        gg = H.get(c)
        if gg is not None and gg >= y: continue
        put(c[0], y, c[1], 'spruce_planks'); put(c[0], y + 1, c[1], 'spruce_fence')
        if (c[0] + c[1]) % 4 == 0: put(c[0], y + 2, c[1], 'lantern')
# はね橋: (5,-5)-(5,-4) の間の3セル。データに場所を入れて、ゲーム中に上げ下げする
bx, bz = wx(5), wz(-5)
BRIDGE_BOX = [bx - 1, 0, bz + 2, bx + 1, 0, bz + 4]
for z in range(bz + 2, bz + 5):
    for x in range(bx - 2, bx + 3): put(x, 0, z, 'dark_oak_planks'); V.pop((x, 1, z), None); V.pop((x, 2, z), None)
for zz in (bz + 1, bz + 5):   # 橋の両はしの塔
    for xx in (bx - 2, bx + 2):
        box(xx, 0, zz, xx, 5, zz, 'stone_bricks'); put(xx, 6, zz, 'stone_brick_wall'); put(xx, 7, zz, 'lantern')
    box(bx - 2, 5, zz, bx + 2, 5, zz, 'stone_bricks'); box(bx - 1, 4, zz, bx + 1, 4, zz, 'spruce_fence')
# 関所(神殿の近道の入口): 石の門
gx_, gz_ = wx(0), wz(6) - 3
for xx in (-2, 2): box(gx_ + xx, 7, gz_, gx_ + xx, 11, gz_, 'polished_blackstone_bricks')
box(gx_ - 2, 12, gz_, gx_ + 2, 12, gz_, 'polished_blackstone_bricks'); box(gx_ - 3, 13, gz_, gx_ + 3, 13, gz_, 'red_nether_brick_slab'); put(gx_, 14, gz_, 'gold_block')
for xx in (-1, 0, 1): put(gx_ + xx, 11, gz_, 'iron_bars')
put(gx_ - 2, 9, gz_ - 1, 'lantern'); put(gx_ + 2, 9, gz_ - 1, 'lantern')

def free(x1, z1, x2, z2, y=None, margin=1):
    for x in range(x1 - margin, x2 + margin + 1):
        for z in range(z1 - margin, z2 + margin + 1):
            if (x, z) in ROAD or (x, z) in RESERVED or (x, z) not in H or H[(x, z)] == -3: return False
            if y is not None and H[(x, z)] != y: return False
    return all((x, H[(x, z)] + 1, z) not in V for x in range(x1, x2 + 1) for z in range(z1, z2 + 1))
def _old_lamp(x, z):
    y = H.get((x, z))
    if y is None or (x, z) in ROAD or (x, z) in RESERVED or (x, y + 1, z) in V: return
    box(x, y + 1, z, x, y + 3, z, 'dark_oak_fence'); put(x, y + 4, z, 'lantern')
# 街灯: マスの角の外側(格子にそろえる)
for nd in nodes:
    if nd['zone'] in ('tree', 'ship') or (nd['g'][0] + nd['g'][1]) % 2: continue
    for i, j in ((2, 2), (-2, -2)):
        if (nd['x'] + i, nd['z'] + j) not in ROAD and H.get((nd['x'] + i, nd['z'] + j)) == nd['y']: lamp(nd['x'] + i, nd['z'] + j); break

# ===== 建物・飾り =====
def _old_tree_(x, z, kind='oak', big=False):
    y = H.get((x, z))
    if y is None or y < 0: return
    hgt = random.randint(7, 10) if big else random.randint(4, 6)
    box(x, y + 1, z, x, y + hgt, z, {'oak': 'oak_log', 'birch': 'birch_log', 'cherry': 'cherry_log', 'jungle': 'jungle_log', 'spruce': 'spruce_log'}[kind])
    r = 3 if big else 2
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            for dy in range(-1, 3):
                if dx * dx + dz * dz + (dy * 1.5) ** 2 <= r * r + 1 and (x + dx, y + hgt + dy, z + dz) not in V and not (abs(dx) == r and abs(dz) == r):
                    put(x + dx, y + hgt + dy, z + dz, leaf(kind))
def mushroom(x, z, red=True, h=None):
    y = H.get((x, z)); h = h or random.randint(6, 9)
    box(x, y + 1, z, x, y + h, z, 'bone_block')
    cap = ('red' if red else 'brown') + '_mushroom_block ["huge_mushroom_bits"=14]'
    r = 3 if red else 4
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            d = max(abs(dx), abs(dz)) if not red else math.hypot(dx, dz)
            if d <= r + 0.3:
                put(x + dx, y + h + (1 if d < r - 0.5 else 0), z + dz, cap)
                if red and d >= r - 0.5: put(x + dx, y + h - 1, z + dz, cap)
    if red:
        for dx, dz in ((1, 1), (-1, 0), (0, -2), (-2, -1), (2, -1)): put(x + dx, y + h + 1, z + dz, 'white_concrete')
WALLS = ['white_terracotta', 'yellow_terracotta', 'light_blue_terracotta', 'pink_terracotta', 'smooth_sandstone', 'orange_terracotta']
ROOFS = ['red_nether_bricks', 'dark_prismarine', 'brick_block', 'blue_terracotta', 'purple_terracotta']
def house(x, z, w, d, flo, door):   # door: 'n' か 's'(道のある方)
    y = H[(x, z)]; wall, roof = random.choice(WALLS), random.choice(ROOFS); hgt = 4 * flo
    box(x, y + 1, z, x + w - 1, y + hgt, z + d - 1, wall); box(x + 1, y + 1, z + 1, x + w - 2, y + hgt, z + d - 2, 'air')
    box(x, y, z, x + w - 1, y, z + d - 1, 'stone_bricks')
    for cx in (x, x + w - 1):
        for cz in (z, z + d - 1): box(cx, y + 1, cz, cx, y + hgt, cz, 'stripped_dark_oak_log')
    for f in range(flo):
        yy = y + 2 + f * 4
        for xx in range(x + 2, x + w - 2, 2): put(xx, yy, z, 'glass'); put(xx, yy, z + d - 1, 'glass')
        for zz in range(z + 2, z + d - 2, 2): put(x, yy, zz, 'glass'); put(x + w - 1, yy, zz, 'glass')
        if f: box(x, y + f * 4, z, x + w - 1, y + f * 4, z + d - 1, 'stripped_dark_oak_log'); box(x + 1, y + f * 4, z + 1, x + w - 2, y + f * 4, z + d - 2, 'spruce_planks')
    k = 0
    while True:
        z1, z2 = z - 1 + k, z + d - k
        if z1 > z2: break
        box(x - 1, y + hgt + 1 + k, z1, x + w, y + hgt + 1 + k, z2, roof)
        if z1 + 1 <= z2 - 1: box(x, y + hgt + 1 + k, z1 + 1, x + w - 1, y + hgt + 1 + k, z2 - 1, wall)
        if z1 + 2 <= z2 - 2: box(x + 1, y + hgt + 1 + k, z1 + 2, x + w - 2, y + hgt + 1 + k, z2 - 2, 'air')
        k += 1
    dz = z if door == 's' else z + d - 1
    box(x + w // 2, y + 1, dz, x + w // 2, y + 2, dz, 'air'); put(x + w // 2 + 1, y + 3, dz + (-1 if door == 's' else 1), 'lantern')
# 港の町: 浜の道(v=-9)の北がわに、格子にそろえた家
for gx, w in ((-5.0, 7), (-3.5, 7), (-1.5, 7), (1.2, 7), (3.6, 7), (5.4, 7)):
    x = round(gx * G) - w // 2; z = wz(-9) + 4
    if free(x, z, x + w - 1, z + 6, 0): house(x, z, w, 7, random.choice([1, 2, 2]), 's')
# 潮で沈む道(浜の本線、分かれ道の先 (-5,-9)〜(-3,-9) のあいだ)
TIDE = sorted({(x, z) for (x, z) in ROAD if wx(-5.5) <= x <= wx(-2.5) and wz(-9) - 1 <= z <= wz(-9) + 1})
# 広場: スタートの南に石だたみ・アーチ・旗
pz = wz(-9)
# 広場: まるい石だたみ(同心円のもよう)・噴水(水の受け皿 + 白い柱 + 金のかざり)・花だん・ベンチ・街灯。門はなし
PCX, PCZ = 0, pz - 5
for x in range(-13, 14):
    for z in range(pz - 10, pz - 1):
        if H.get((x, z)) != 0 or (x, z) in ROAD: continue
        r = math.hypot(x - PCX, (z - PCZ) * 1.3)
        if r > 13.5: continue
        ringn = int(r) // 2
        put(x, 0, z, ['polished_andesite', 'smooth_stone', 'polished_diorite', 'smooth_stone', 'polished_andesite', 'chiseled_stone_bricks', 'smooth_stone'][ringn % 7])
for x in range(PCX - 3, PCX + 4):                                   # 噴水: 受け皿(白い石のふち)と水
    for z in range(PCZ - 2, PCZ + 3):
        r = math.hypot(x - PCX, (z - PCZ) * 1.3)
        if r <= 3.4: put(x, 0, z, 'quartz_bricks'); put(x, 1, z, 'quartz_slab' if r > 2.6 else 'water')
box(PCX, 1, PCZ, PCX, 4, PCZ, 'quartz_pillar'); put(PCX, 5, PCZ, 'chiseled_quartz_block'); put(PCX, 6, PCZ, 'gold_block'); put(PCX, 7, PCZ, 'sea_lantern')
for (i, j) in ((1, 0), (-1, 0), (0, 1), (0, -1)): put(PCX + i, 4, PCZ + j, 'quartz_slab'); put(PCX + i, 3, PCZ + j, 'water')   # 柱の上から水が落ちる
for (bx_, bz_) in ((-11, PCZ - 4), (-11, PCZ + 1)):               # 高くした花だん(東は DJ ブース)
    if all(H.get((bx_ + i, bz_ + j)) == 0 and (bx_ + i, bz_ + j) not in ROAD for i in range(5) for j in range(3)): planter(bx_, bz_)
for (lx_, lz_) in ((-6, pz - 10), (6, pz - 10), (-13, pz - 6)):   # 街灯(作りこみ版)
    if H.get((lx_, lz_)) == 0 and (lx_, lz_) not in ROAD: lamp(lx_, lz_)
# (DJ ブースは帆船の甲板へ移した: tools/mpl_board_ship.py)
# 帆船(船の上が道)
def ship_(cx, cz, L=34):
    for i in range(L):
        x = cx - L // 2 + i; t = abs(i - L / 2) / (L / 2)
        hw = max(1, round(5 * (1 - t ** 3)))
        for dz in range(-hw, hw + 1):
            box(x, -2 if t < 0.75 else -1, cz + dz, x, 1, cz + dz, 'dark_oak_planks')
            if abs(dz) == hw: put(x, 2, cz + dz, 'dark_oak_planks'); put(x, 0, cz + dz, 'red_concrete'); put(x, 3, cz + dz, 'dark_oak_fence') if (x, cz + dz) not in ROAD else None
            elif (x, cz + dz) not in ROAD: put(x, 2, cz + dz, 'spruce_planks')
    for mx, mh in ((cx - 7, 16), (cx + 8, 13)):
        box(mx, 3, cz + 3, mx, 3 + mh, cz + 3, 'spruce_log')
        for k in range(3, mh - 1):
            w = 5 - abs(k - mh // 2) // 3
            box(mx + 1, 3 + k, cz + 3 - w, mx + 1, 3 + k, cz + 3 + w, 'white_wool')
        put(mx, 4 + mh, cz + 3, 'red_wool'); put(mx + 1, 4 + mh, cz + 3, 'red_wool')
    box(cx + L // 2, 2, cz, cx + L // 2 + 5, 2, cz, 'spruce_fence')
    box(cx - L // 2 + 1, 3, cz - 3, cx - L // 2 + 5, 6, cz + 3, 'dark_oak_planks'); box(cx - L // 2 + 2, 4, cz - 2, cx - L // 2 + 4, 5, cz + 2, 'air')
    for dz in (-2, 0, 2): put(cx - L // 2 + 5, 5, cz + dz, 'glass')
    box(cx + 3, 3, cz - 4, cx + 4, 3, cz - 4, 'black_concrete'); put(cx + 5, 3, cz - 4, 'coal_block')  # 大砲
# 大きな帆船 + 甲板の DJ ブース(tools/mpl_board_ship.py)
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mpl_board_ship.py'), encoding='utf-8').read())
# 森: 大きい木とキノコ、木の上の小屋
for i in range(140):
    x, z = random.randint(-62, -32), random.randint(wz(-4), wz(5))
    if free(x - 2, z - 2, x + 2, z + 2, 3, 0): tree_(x, z, random.choice(['oak', 'birch', 'spruce', 'oak']), big=random.random() < 0.5)
for (x, z, red) in [(-36, wz(2) + 3, True), (-36, wz(-2), False), (-47, wz(3), True), (-48, wz(-1) - 3, True), (-60, wz(2), False)]:
    if free(x - 1, z - 1, x + 1, z + 1, None, 0): mushroom(x, z, red)
for gz in (1, -3):  # 木の上の小屋(道の西)
    x, z = wx(-9) - 6, wz(gz)
    if (x, z) in H:
        y = 7; box(x - 2, H[(x, z)] + 1, z, x - 2, y - 1, z, 'spruce_log')
        box(x - 4, y, z - 2, x, y, z + 2, 'spruce_planks'); box(x - 4, y + 1, z - 2, x, y + 3, z + 2, 'stripped_spruce_log'); box(x - 3, y + 1, z - 1, x - 1, y + 3, z + 1, 'air')
        box(x, y + 1, z, x, y + 2, z, 'air'); box(x - 5, y + 4, z - 3, x + 1, y + 4, z + 3, 'dark_oak_planks'); box(x - 4, y + 5, z - 2, x, y + 5, z + 2, 'dark_oak_planks'); put(x - 2, y + 6, z, 'lantern')
        for xx in range(x + 1, wx(-9) - 1): put(xx, y, z, 'spruce_planks')
# クリスタル台地: 大きなクリスタル・こわれた柱・灯台
def _old_crystal(x, z, h):
    y = H[(x, z)]
    for k in range(h):
        r = 1 if k < h - 2 else 0
        for i in range(-r, r + 1):
            for j in range(-r, r + 1):
                if abs(i) + abs(j) <= r: put(x + i, y + 1 + k, z + j, 'amethyst_block' if (k + i) % 3 else 'purple_stained_glass')
    put(x, y + h + 1, z, 'sea_lantern'); put(x + 1, y + 1, z + 1, 'amethyst_block'); put(x - 1, y + 1, z - 1, 'amethyst_block'); put(x - 1, y + 2, z - 1, 'amethyst_block')
for (gx, gz, h) in [(5.5, 1, 7), (8.6, 3, 9), (5.6, 4, 6), (8.7, -0.4, 6), (8.6, 5.4, 8), (4.6, 2.6, 5), (6, 5, 5)]:
    x, z = round(gx * G), round(wz(gz))
    if free(x - 1, z - 1, x + 1, z + 1, 6, 0): crystal(x, z, h)
for (gx, gz) in [(6.2, 2.2), (8.6, 4.6)]:                     # こわれた柱廊(遺跡)
    x, z = round(gx * G), round(wz(gz))
    if _free_cells([(x + i, z + j) for i in range(-1, 10) for j in range(-1, 5)]) and all(H.get((x + i, z + j)) == 6 for i in range(0, 9) for j in range(0, 4)): ruins(x, z)
def lighthouse(x, z):
    y = H[(x, z)]
    for k in range(16):
        r = 3 if k < 7 else 2
        for i in range(-r, r + 1):
            for j in range(-r, r + 1):
                if i * i + j * j <= r * r + 1: put(x + i, y + 1 + k, z + j, 'red_concrete' if (k // 2) % 2 else 'white_concrete')
    box(x - 3, y + 17, z - 3, x + 3, y + 17, z + 3, 'iron_block'); box(x - 1, y + 18, z - 1, x + 1, y + 19, z + 1, 'glass'); box(x, y + 18, z, x, y + 19, z, 'sea_lantern')
    box(x - 2, y + 20, z - 2, x + 2, y + 20, z + 2, 'red_concrete'); box(x - 1, y + 21, z - 1, x + 1, y + 21, z + 1, 'red_concrete'); put(x, y + 22, z, 'gold_block')
lx, lz = wx(9) + 2, wz(-7)
if H.get((lx, lz)) is not None and free(lx - 3, lz - 3, lx + 3, lz + 3, None, 0): lighthouse(lx, lz)
# 神殿(丘の上): 柱・女神の像・宙にうかぶ金の輪
sx, sz, ty = 0, wz(2), 8
for i in range(-9, 10):
    for j in range(-15, 16):
        if H.get((sx + i, sz + j)) == 8 and (sx + i, sz + j) not in ROAD: put(sx + i, 8, sz + j, 'smooth_quartz' if (i + j) % 2 else 'quartz_block')
for j in (-12, -6, 0, 6, 12):
    for i in (-7, 7):
        if H.get((sx + i, sz + j)) == 8: box(sx + i, 9, sz + j, sx + i, 15, sz + j, 'quartz_pillar'); put(sx + i, 16, sz + j, 'gold_block')
for i in (-5, 5):  # 女神の像(左右に1体ずつ)
    box(i - 1, 9, sz - 1, i + 1, 9, sz + 1, 'chiseled_quartz_block'); box(i, 10, sz, i, 14, sz, 'quartz_block'); box(i, 12, sz - 1, i, 12, sz + 1, 'quartz_block')
    put(i, 15, sz, 'white_concrete'); put(i, 16, sz, 'gold_block'); put(i, 13, sz - 2 if i < 0 else sz + 2, 'quartz_block')
for k in range(72):
    a = k / 72 * math.pi * 2
    put(round(sx + math.cos(a) * 9), 22, round(sz + math.sin(a) * 9), 'gold_block' if k % 9 else 'sea_lantern')
# 野原: 風車と桜
def windmill(x, z):
    y = H[(x, z)]
    for k in range(11):
        r = 3 if k < 6 else 2
        for i in range(-r, r + 1):
            for j in range(-r, r + 1):
                if max(abs(i), abs(j)) == r: put(x + i, y + 1 + k, z + j, 'stripped_birch_wood' if k % 5 else 'stripped_dark_oak_log')
    for k in range(3): box(x - 2 + k, y + 12 + k, z - 2 + k, x + 2 - k, y + 12 + k, z + 2 - k, 'red_nether_bricks')
    box(x, y + 1, z - 3, x, y + 2, z - 3, 'air'); put(x, y + 8, z - 4, 'stripped_spruce_log')
    for a in range(4):
        for t in range(1, 8):
            i, j = [(t, 0), (-t, 0), (0, t), (0, -t)][a]
            put(x + i, y + 8 + j, z - 5, 'spruce_fence' if t < 3 else 'white_wool')
            if t >= 3: put(x + i + (0 if i else 1), y + 8 + j + (0 if j else 1), z - 5, 'white_wool')
if free(-22, wz(-2) - 3, -16, wz(-2) + 3, 0, 0): windmill(-19, wz(-2))
for i in range(60):
    x, z = random.randint(-30, 20), random.randint(wz(-8) + 6, wz(4))
    if free(x - 2, z - 2, x + 2, z + 2, 0, 1): tree_(x, z, 'cherry' if random.random() < 0.6 else 'oak')
# 野原の池(砂のふち + スイレン)
def pond(cx, cz, rx, rz):
    for i in range(-rx - 1, rx + 2):
        for j in range(-rz - 1, rz + 2):
            d = (i / rx) ** 2 + (j / rz) ** 2
            if H.get((cx + i, cz + j)) != 0 or near_road(cx + i, cz + j, 1): continue
            if d <= 1: put(cx + i, 0, cz + j, 'water'); put(cx + i, -1, cz + j, 'sand'); H[(cx + i, cz + j)] = -3
            elif d <= 1.5: put(cx + i, 0, cz + j, 'sand')
    for i, j in ((1, 0), (-2, 1), (0, -1)): put(cx + i, 1, cz + j, 'waterlily')
pond(13, wz(-2), 5, 4); pond(-13, wz(-6) + 1, 4, 3)
# 花畑(石のふちでかこみ、色ごとの列と砂利の小道)
for (fx, fz, w, d_) in ((-30, wz(-1), 14, 9), (8, wz(-7) + 2, 10, 8), (-30, wz(-7) + 3, 10, 6)): garden(fx, fz, w, d_)
# 神殿の屋根のはり(柱の上をつなぐ)と、北のはしの大きな門
for i in (-7, 7): box(sx + i, 17, sz - 12, sx + i, 17, sz + 12, 'quartz_block')
for j in (-12, 12): box(sx - 7, 17, sz + j, sx + 7, 17, sz + j, 'quartz_block'); box(sx - 4, 18, sz + j, sx + 4, 18, sz + j, 'quartz_bricks'); box(sx - 2, 19, sz + j, sx + 2, 19, sz + j, 'gold_block')
# 北の台地: 温泉(白い石のふちの湯)・枯れ木・石の塔
for (cx, cz) in ((-40, wz(7)), (-52, wz(5) + 2), (40, wz(8)), (50, wz(6) + 3)):
    for i in range(-3, 4):
        for j in range(-3, 4):
            c = (cx + i, cz + j)
            if H.get(c) != 6 or near_road(c[0], c[1], 1) or c in RESERVED: continue
            d = math.hypot(i, j)
            if d <= 2.3: put(c[0], 6, c[1], 'water'); put(c[0], 5, c[1], 'calcite')
            elif d <= 3.4:                                     # ふちは石のまぜ + ところどころ岩が立つ + 苔
                put(c[0], 6, c[1], random.choice(['stone', 'andesite', 'mossy_cobblestone', 'calcite']))
                if (i * 3 + j) % 4 == 0: put(c[0], 7, c[1], random.choice(['mossy_cobblestone', 'stone', 'moss_block']))
    if (cx + 4, cz) in H and H.get((cx + 4, cz)) == 6 and not near_road(cx + 4, cz, 1): lamp(cx + 4, cz)
for i in range(160):
    x, z = random.randint(-58, 56), random.randint(wz(5), wz(10))
    if H.get((x, z)) == 6 and free(x - 2, z - 2, x + 2, z + 2, 6, 0) and vol(x, z) > 5.6: tree_(x, z, 'spruce' if x < 0 else 'birch', big=random.random() < 0.3)
# 東の台地: 小さいクリスタルの群れ・見はらしの塔
tx_, tz_ = 54, wz(2)
if free(tx_ - 2, tz_ - 2, tx_ + 2, tz_ + 2, 6, 0):
    for k in range(12):
        for i in range(-2, 3):
            for j in range(-2, 3):
                if max(abs(i), abs(j)) == 2 and not (abs(i) == 2 and abs(j) == 2): put(tx_ + i, 7 + k, tz_ + j, 'calcite' if k % 4 else 'purple_stained_glass')
    box(tx_ - 3, 19, tz_ - 3, tx_ + 3, 19, tz_ + 3, 'quartz_block'); box(tx_ - 2, 20, tz_ - 2, tx_ + 2, 20, tz_ + 2, 'purple_stained_glass'); put(tx_, 21, tz_, 'sea_lantern')
# 南東の低地: 牧場(さく・干し草・小屋)
fx0, fz0 = 24, wz(-8) + 3
if free(fx0, fz0, fx0 + 12, fz0 + 9, 0, 0):
    for x in range(fx0, fx0 + 13):
        for z in range(fz0, fz0 + 10):
            if x in (fx0, fx0 + 12) or z in (fz0, fz0 + 9): put(x, 1, z, 'oak_fence')
    box(fx0 + 2, 1, fz0 + 2, fx0 + 3, 2, fz0 + 3, 'hay_block'); put(fx0 + 5, 1, fz0 + 2, 'hay_block'); put(fx0 + 6, 1, fz0 + 6, 'hay_block')
    box(fx0 + 8, 1, fz0 + 5, fx0 + 11, 3, fz0 + 8, 'red_terracotta'); box(fx0 + 9, 1, fz0 + 5, fx0 + 10, 2, fz0 + 5, 'air'); box(fx0 + 7, 4, fz0 + 4, fx0 + 12, 4, fz0 + 9, 'white_concrete'); box(fx0 + 8, 5, fz0 + 5, fx0 + 11, 5, fz0 + 8, 'white_concrete')
# 浜辺: ヤシ・パラソル・岩
def _old_palm(x, z):
    y = H[(x, z)]; hgt = random.randint(5, 7)
    for k in range(hgt): put(x + (1 if k > hgt * 0.6 else 0), y + 1 + k, z, 'jungle_log')
    tx, ty_ = x + 1, y + hgt
    for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2), (3, -1), (-3, 1), (-1, 3), (1, -3)): put(tx + i, ty_ + (0 if abs(i) + abs(j) < 3 else -1), z + j, leaf('jungle'))
    put(tx, ty_ + 1, z, leaf('jungle'))
for i in range(600):                                              # ヤシ(作りこみ版)だけ散らす
    x, z = random.randint(-56, 56), random.randint(wz(-11), wz(-3))
    if V.get((x, 0, z)) != 'sand' or (x, 1, z) in V: continue
    if random.random() < 0.2 and free(x - 3, z - 3, x + 3, z + 3, 0, 0): palm(x, z)
_um = [('red', 'white'), ('light_blue', 'white'), ('orange', 'yellow'), ('pink', 'white')]   # パラソルと岩は場所を決めて置く
_k = 0
for i in range(400):
    x, z = random.randint(-56, 56), random.randint(wz(-11), wz(-3))
    if _k >= 6: break
    cells = [(x + a_, z + b_) for a_ in range(-3, 4) for b_ in range(-3, 4)]
    if all(V.get((c[0], 0, c[1])) == 'sand' and (c[0], 1, c[1]) not in V and c not in ROAD for c in cells):
        (umbrella(x, z, *_um[_k % 4]) if _k % 3 != 2 else boulder(x, z, 2)); _k += 1
# 火山のふもと: 玄武岩の柱の群れと枯れ木(場所を決めて、少しだけ)
_k = 0
for i in range(300):
    x, z = random.randint(-40, 40), random.randint(wz(5.6), wz(11))
    if _k >= 8: break
    if (x, z) not in H or H[(x, z)] < 7 or not (3.4 < vol(x, z) < 4.9) or near_road(x, z, 3) or not _free_cells([(x + a_, z + b_) for a_ in range(-2, 3) for b_ in range(-2, 3)]): continue
    if any((x + a_, y_, z + b_) in V for a_ in range(-2, 3) for b_ in range(-2, 3) for y_ in range(H[(x, z)] + 1, H[(x, z)] + 4)): continue
    (basalt_cluster(x, z) if _k % 2 == 0 else dead_tree(x, z)); _k += 1
# 港: 荷物(たる・木箱・麻袋)
for gz in (-6, -8):
    x, z = wx(-7) - 4, wz(gz) + 3
    if _free_cells([(x + a_, z + b_) for a_ in range(0, 3) for b_ in range(0, 2)]): crates(x, z)
# ===== v5 大建築(大聖堂・天使・金の輪・火山・回廊・滝・藤・桜)=====
if not os.environ.get('NO_GRAND'): exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mpl_board_grand.py'), encoding='utf-8').read())
# ===== コマンドにまとめる =====
def merge():
    by = {}
    for (x, y, z), b in V.items():
        if b != 'air': by.setdefault(b, set()).add((x, y, z))
    cmds = []
    for b, pts in by.items():
        while pts:
            x, y, z = min(pts); x2 = x
            while (x2 + 1, y, z) in pts: x2 += 1
            z2 = z
            while all((xx, y, z2 + 1) in pts for xx in range(x, x2 + 1)): z2 += 1
            y2 = y
            while all((xx, y2 + 1, zz) in pts for xx in range(x, x2 + 1) for zz in range(z, z2 + 1)) and (x2 - x + 1) * (z2 - z + 1) * (y2 - y + 2) <= 32000: y2 += 1
            for xx in range(x, x2 + 1):
                for yy in range(y, y2 + 1):
                    for zz in range(z, z2 + 1): pts.discard((xx, yy, zz))
            cmds.append((y, b, f'fill {x} {y} {z} {x2} {y2} {z2} {b}' if (x, y, z) != (x2, y2, z2) else f'setblock {x} {y} {z} {b}'))
    late = ('lantern', 'poppy', 'dandelion', 'cornflower', 'allium', 'tulip', 'bluet', 'daisy', 'short_grass', 'fern', 'water', 'lava', 'fence', 'iron_bars', 'slab')
    return [c for _, _, c in sorted(cmds, key=lambda c: (1 if any(k in c[1] for k in late) else 0, c[0]))]
cmds = merge()
out_nodes = [{k: v for k, v in nd.items() if k != 'g'} for nd in nodes]
# ===== 満潮で水びたしになる浜(y=1 に水)。海に近い順に満ちる。広場・DJ ブースのまわり(+8)には入れない =====
pzz = wz(-9)
def floodable(x, z):
    if H.get((x, z)) != 0 or V.get((x, 1, z)) not in (None, 'air'): return False
    if -22 <= x <= 22 and z <= pzz + 2: return False
    top = V.get((x, 0, z), '').split(' ')[0]
    return top == 'sand' or (top == 'smooth_sandstone' and (x, z) in ROAD)
FL = {c for c in H if floodable(*c)}
dist, frontier = {}, [c for c in FL if any((c[0] + i, c[1] + j) not in H or H[(c[0] + i, c[1] + j)] < 0 for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
for c in frontier: dist[c] = 0
while frontier:
    nxt = []
    for (x, z) in frontier:
        for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + i, z + j)
            if n in FL and n not in dist: dist[n] = dist[(x, z)] + 1; nxt.append(n)
    frontier = nxt
FLOOD = []   # [x1, x2, z, 段] 同じ z・同じ段で x が続く所は 1 つにまとめる
for z in sorted({c[1] for c in dist}):
    xs = sorted(x for (x, zz) in dist if zz == z); run = None
    for x in xs:
        st = min(dist[(x, z)] // 2, 12)
        if run and x == run[1] + 1 and st == run[3]: run[1] = x
        else:
            if run: FLOOD.append(run)
            run = [x, x, z, st]
    if run: FLOOD.append(run)
# ===== 噴火の溶岩: 火口がふちまで満ちて、斜面を流れ下る(道から 5 マス・海から 6 マスの手前で止める) =====
def near_sea(x, z, r): return any((x + i, z + j) not in H or H[(x + i, z + j)] < 0 for i in range(-r, r + 1) for j in range(-r, r + 1))
POOL = [c for c in H if vol(*c) < 1.0]
FLOWS = []
for a in (-1.2, 1.5):   # 北がわ(-2.4・2.6)は海が近いので流さない
    f, last = [], None
    for k in range(200):
        d = 1.0 + k * 0.03
        x, z = round(math.sin(a) * d * 1.15 * G), round(ZC + (9.8 - math.cos(a) * d * 0.75) * G)
        if (x, z) == last: continue
        last = (x, z); h = H.get((x, z))
        if h is None or near_road(x, z, 5) or near_sea(x, z, 6) or (d > 1.9 and h < 7): break
        y = RIM + 1 if d < 1.9 else h + 1
        if V.get((x, y, z)) in (None, 'air'): f.append([x, y, z])
    FLOWS.append(f)
VOLC = {'pool': [min(c[0] for c in POOL), min(c[1] for c in POOL), max(c[0] for c in POOL), max(c[1] for c in POOL)], 'y0': CRATER + 2, 'y1': RIM, 'flows': FLOWS}
print('mirrors', [m['g'] for m in MIRRORS]); print('flood runs', len(FLOOD), 'cells', len(dist), 'flows', [len(f) for f in FLOWS])
# ===== 岸の波(mmgplus:wave を置く場所): 岸どなりの海のマスを 7 ブロックおきに。向きは陸の方。船・桟橋・道のそばはさける =====
WAVES = []
coast = sorted(c for c, d in SEA_D.items() if d == 1 and X0 + 2 < c[0] < X1 - 2 and Z0 + 2 < c[1] < Z1 - 2)
for (x, z) in coast:
    if any(abs(x - w[0]) + abs(z - w[1]) < 7 for w in WAVES): continue
    if any((x + i, z + j) in ROAD for i in range(-3, 4) for j in range(-3, 4)): continue
    if any(V.get((x + i, y, z + j), 'water').split(' ')[0] not in ('water', 'sand', 'gravel') for i in range(-2, 3) for j in range(-2, 3) for y in (0, 1, 2)
           if (x + i, z + j) not in H): continue
    vx = sum(i for i in range(-2, 3) for j in range(-2, 3) if (x + i, z + j) in H and H[(x + i, z + j)] >= 0)
    vz = sum(j for i in range(-2, 3) for j in range(-2, 3) if (x + i, z + j) in H and H[(x + i, z + j)] >= 0)
    if vx == 0 and vz == 0: continue
    yaw = round(math.degrees(math.atan2(-vx, vz)))   # 陸の方を向く(Bedrock の向き)
    WAVES.append([x, z, yaw])
print('waves', len(WAVES))
data = {'spaces': out_nodes, 'cmds': cmds, 'area': [X0, YB, Z0, X1, YT, Z1], 'island': [X0, YB, 44, X1, YT, Z1], 'center': {'x': 0.5, 'z': ZC + 6.5}, 'lobby': {'x': 0.5, 'y': 1, 'z': wz(-9) - 4.5},
        'finaleZ': STAGE['z'], 'stage': STAGE, 'bridge': BRIDGE_BOX, 'crater': {'x': 0.5, 'y': RIM - 3, 'z': wz(9.8)}, 'volcanoFoot': at[(4, 6)], 'toll': 10, 'version': 21, 'tide': TIDE, 'waves': WAVES, 'flood': FLOOD, 'volc': VOLC, 'dj': dict(DJ, eq=EQ), 'ghost': {'from': {'x': X0 + 3, 'z': SHIP_GHOST_Z}, 'to': {'x': -27, 'z': SHIP_GHOST_Z}, 'plank': {'x': -27, 'edge': SHIP_CZ - SHIP_HW}}}
open(OUT_JS, 'w', encoding='utf-8').write('// tools/mpl_board.py で作ったボード「女神の島」のデータ(手で書きかえない)\nexport const BOARD_DATA = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('spaces', len(nodes), 'junctions', sum(1 for n in nodes if len(n['next']) > 1), 'cmds', len(cmds), 'kb', os.path.getsize(OUT_JS) // 1024)

# ===== 見本(南から見下ろす)=====
C = {'grass_block': (110, 170, 70), 'moss_block': (90, 140, 50), 'dirt': (130, 95, 60), 'stone': (125, 125, 125), 'andesite': (135, 135, 135), 'cobblestone': (110, 110, 110), 'calcite': (220, 220, 215), 'tuff': (105, 110, 105),
     'mossy_cobblestone': (95, 115, 90), 'stone_bricks': (120, 120, 120), 'mossy_stone_bricks': (100, 120, 95), 'sand': (225, 212, 165), 'water': (55, 120, 220), 'lava': (255, 120, 20), 'magma_block': (190, 70, 20),
     'shroomlight': (250, 150, 60), 'blackstone': (45, 40, 48), 'basalt': (75, 75, 80), 'deepslate': (70, 70, 75), 'polished_deepslate': (80, 80, 85), 'polished_blackstone_bricks': (55, 50, 58),
     'prismarine_bricks': (80, 160, 140), 'polished_andesite': (150, 150, 150), 'quartz_block': (235, 230, 225), 'smooth_quartz': (240, 236, 230), 'quartz_bricks': (232, 228, 220), 'spruce_planks': (115, 85, 50),
     'spruce_fence': (115, 85, 50), 'white_concrete': (240, 240, 240), 'packed_mud': (145, 105, 80), 'smooth_sandstone': (222, 208, 160), 'light_blue_concrete': (60, 160, 230), 'red_concrete': (190, 40, 40),
     'lime_concrete': (110, 200, 40), 'yellow_concrete': (245, 200, 30), 'purple_concrete': (120, 40, 170), 'black_concrete': (25, 25, 30), 'dark_oak_fence': (70, 50, 30), 'lantern': (255, 200, 90),
     'oak_log': (110, 85, 50), 'birch_log': (220, 215, 200), 'cherry_log': (90, 50, 60), 'jungle_log': (90, 70, 40), 'spruce_log': (80, 60, 35), 'bone_block': (230, 225, 205), 'white_terracotta': (210, 180, 165),
     'orange_terracotta': (165, 85, 40), 'yellow_terracotta': (185, 135, 35), 'light_blue_terracotta': (115, 110, 140), 'pink_terracotta': (165, 80, 80), 'red_nether_bricks': (90, 15, 15), 'dark_prismarine': (50, 90, 75),
     'brick_block': (150, 80, 65), 'blue_terracotta': (75, 60, 90), 'purple_terracotta': (120, 70, 85), 'stripped_dark_oak_log': (70, 55, 35), 'glass': (200, 230, 240), 'iron_block': (220, 220, 220),
     'sea_lantern': (200, 230, 230), 'gold_block': (250, 210, 60), 'quartz_pillar': (235, 230, 220), 'chiseled_quartz_block': (230, 225, 215), 'amethyst_block': (150, 100, 200), 'purple_stained_glass': (170, 110, 220),
     'dark_oak_planks': (65, 45, 25), 'white_wool': (245, 245, 245), 'red_wool': (180, 40, 40), 'polished_diorite': (200, 200, 200), 'smooth_stone': (170, 170, 170), 'stone_brick_wall': (120, 120, 120),
     'stripped_spruce_log': (140, 110, 70), 'stripped_birch_wood': (200, 180, 120), 'oak_fence': (150, 120, 70), 'barrel': (120, 85, 50), 'hay_block': (200, 170, 40), 'coal_block': (20, 20, 20),
     'iron_bars': (150, 150, 150), 'pink_concrete': (240, 140, 180), 'cyan_concrete': (30, 140, 150), 'polished_blackstone': (50, 45, 55), 'polished_blackstone_slab': (55, 50, 60), 'note_block': (110, 70, 50), 'black_concrete': (20, 20, 25), 'red_terracotta': (145, 60, 45), 'waterlily': (40, 120, 50), 'red_nether_brick_slab': (90, 15, 15), 'quartz_bricks': (236, 232, 224), 'smooth_quartz': (240, 236, 228), 'calcite': (225, 225, 220), 'ochre_froglight': (255, 190, 70), 'magma_block': (190, 70, 20), 'deepslate_tiles': (55, 55, 60), 'glowstone': (255, 220, 120), 'light_blue_stained_glass': (120, 190, 240), 'chiseled_stone_bricks': (125, 125, 125), 'stone_bricks': (120, 120, 120), 'mossy_stone_bricks': (100, 120, 95), 'polished_andesite': (135, 135, 135), 'basalt': (75, 75, 80), 'blackstone': (40, 35, 45), 'quartz_slab': (236, 232, 224), 'azalea_leaves ["persistent_bit"=true]': (110, 150, 70), 'water': (55, 120, 220)}
def colr(b):
    if b in C: return C[b]
    if 'leaves' in b: return {'oak': (60, 130, 40), 'bir': (110, 150, 60), 'aza': (90, 140, 70), 'che': (240, 170, 200), 'jun': (50, 140, 40), 'spr': (45, 90, 55)}[b[:3]]
    if 'mushroom' in b: return (200, 40, 40) if b.startswith('red') else (150, 110, 80)
    if 'wool' in b or 'concrete' in b: return {'red': (200, 50, 50), 'ora': (240, 130, 30), 'yel': (240, 210, 50), 'lim': (120, 200, 40), 'gre': (70, 130, 40), 'lig': (100, 170, 230), 'blu': (50, 60, 170), 'pur': (130, 50, 180), 'pin': (240, 150, 180)}.get(b[:3], (200, 200, 200))
    return (230, 120, 160) if any(k in b for k in ('poppy', 'tulip', 'allium')) else (240, 220, 80) if 'dandelion' in b else (110, 160, 70)
S = 8; W, Hh = 1500, 1500
img = Image.new('RGB', (W, Hh), (40, 110, 170)); d = ImageDraw.Draw(img)
MZ = (Z0 + Z1) / 2
def proj(x, y, z): return W / 2 + x * S * 1.1 + (z - MZ) * S * 0.2, Hh * 0.56 - (z - MZ) * S * 0.72 - y * S * 1.0
for (x, y, z), b in sorted(V.items(), key=lambda kv: (-kv[0][2], kv[0][1])):
    if b == 'air' or ((x, y + 1, z) in V and V[(x, y + 1, z)] not in ('air',) and (x, y, z - 1) in V and V[(x, y, z - 1)] != 'air'): continue
    c = colr(b); px, py = proj(x, y, z)
    d.polygon([(px, py), (px + S * 1.1, py), (px + S * 1.3, py - S * 0.72), (px + S * 0.2, py - S * 0.72)], fill=c)
    if V.get((x, y, z - 1), 'air') == 'air': d.polygon([(px, py), (px + S * 1.1, py), (px + S * 1.1, py + S), (px, py + S)], fill=tuple(int(v * 0.72) for v in c))
img.save(OUT_PNG)
print('preview ok')
