# MPL のボード「女神の島」を設計する(すべて自作)
#   エリア: 南の広場(スタート・ロビー)/ 東の川と崖(灯台・遺跡・クリスタル・滝)/ 北の町 / 西の森(大きなキノコ)/ 南西の港(帆船)/ 真ん中の丘の神殿
#   道は高さが変わる(崖へのスロープ・高いつり橋・階段)。町から神殿を通る近道(分かれ道)
#   出力: mpl_bp/scripts/board_data.js(マスの一覧 + 組み立てのコマンド)と、上から見た見本 mpl/preview_board.png
#   python3 tools/mpl_board.py
import json, math, os, random
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JS = os.path.join(ROOT, 'mpl', 'src', 'behavior_packs', 'mpl_bp', 'scripts', 'board_data.js')
OUT_PNG = os.path.join(ROOT, 'mpl', 'preview_board.png')
random.seed(7)
X0, X1, Z0, Z1, YB, YT = -52, 52, 78, 182, -4, 30
CZ = 130
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
LEAF = {'oak': 'oak_leaves ["persistent_bit"=true]', 'birch': 'birch_leaves ["persistent_bit"=true]', 'azalea': 'azalea_leaves_flowered ["persistent_bit"=true]', 'cherry': 'cherry_leaves ["persistent_bit"=true]'}

# ===== 地形の高さ =====
def noise(x, z):
    return math.sin(x * 0.21 + z * 0.13) * 0.6 + math.sin(x * 0.07 - z * 0.19) * 0.9 + math.cos(z * 0.31) * 0.4
def inside(x, z):
    u, v = x / 47, (z - CZ) / 47
    return u ** 4 + v ** 4 < 1 + noise(x, z) * 0.06
RIVER = [(26, 182), (26, 168), (24, 150), (22, 128), (25, 108), (27, 92), (28, 76)]
def river_d(x, z):
    best = 99
    for (ax, az), (bx, bz) in zip(RIVER, RIVER[1:]):
        dx, dz = bx - ax, bz - az; t = max(0, min(1, ((x - ax) * dx + (z - az) * dz) / (dx * dx + dz * dz)))
        best = min(best, math.hypot(x - ax - dx * t, z - az - dz * t))
    return best
def height(x, z):
    if not inside(x, z): return None
    r = math.hypot(x, z - CZ)
    if x >= 31 and z >= 110: return 7                           # 東の崖
    if x >= 31 and 104 <= z < 110: return 7 - (110 - z)          # 崖のすそ
    if r <= 6.5: return 9                                          # 丘のてっぺん(神殿)
    if r <= 11.5: return 6
    if r <= 16.5: return 3
    return 0
H = {}
for x in range(X0, X1 + 1):
    for z in range(Z0, Z1 + 1):
        h = height(x, z)
        if h is None: continue
        if river_d(x, z) <= 2.6 and not (x >= 31 and z >= 110): h = -3
        H[(x, z)] = h

# ===== 道(高さつき)。マスは 5ブロックごと =====
MAIN = [(0, 0, 100), (12, 0, 100), (20, 0, 100), (22, 1, 100), (31, 1, 100), (38, 0, 100), (38, 0, 108), (38, 7, 122), (38, 7, 140),
        (37, 7, 156), (34, 7, 166), (20, 7, 166), (15, 7, 166), (7, 0, 166), (-4, 0, 166), (-20, 0, 166), (-36, 0, 166), (-39, 0, 158),
        (-39, 0, 148), (-39, 3, 142), (-39, 3, 126), (-39, 0, 120), (-39, 0, 104), (-31, 0, 96), (-25, 1, 88), (-12, 1, 88), (-7, 0, 94), (-2, 0, 99)]
SHORT = [(-4, 0, 166), (-3, 0, 156), (-2, 3, 148), (-1, 6, 142), (0, 9, 136), (0, 9, 124), (1, 6, 118), (1, 3, 113), (1, 0, 106), (0, 0, 100)]
def cells(poly):
    out = []
    for (ax, ay, az), (bx, by, bz) in zip(poly, poly[1:]):
        n = max(abs(bx - ax), abs(bz - az))
        for i in range(n):
            t = i / n; out.append((round(ax + (bx - ax) * t), round(ay + (by - ay) * t), round(az + (bz - az) * t)))
    out.append(poly[-1]); return out
def sample(c, step=5, closed=False):
    pts = [c[0]]; acc = 0
    for a, b in zip(c, c[1:]):
        acc += math.hypot(b[0] - a[0], b[2] - a[2])
        if acc >= step - 0.01: pts.append(b); acc = 0
    if closed and math.hypot(pts[-1][0] - c[0][0], pts[-1][2] - c[0][2]) < 3: pts.pop()
    return pts
main_cells = cells(MAIN + [MAIN[0]])
mains = sample(main_cells, 5, closed=True)
short_cells = cells(SHORT)
shorts = sample(short_cells, 5)[1:-1]  # 両はしは本線のマス
J = min(range(len(mains)), key=lambda i: math.hypot(mains[i][0] + 4, mains[i][2] - 166))  # 分かれ道
mains[J] = (-4, 0, 166)

# マスの種類
N = len(mains)
kinds = ['blue'] * N
kinds[0] = 'start'
for i in range(1, N):
    if i % 7 == 3: kinds[i] = 'red'
    elif i % 6 == 5: kinds[i] = 'event'
    elif i % 13 == 9: kinds[i] = 'lucky'
def nearest(p): return min(range(N), key=lambda i: math.hypot(mains[i][0] - p[0], mains[i][2] - p[1]))
for p in [(38, 140), (-30, 166), (-39, 112)]: kinds[nearest(p)] = 'shop'
for p in [(10, 166), (-39, 134)]: kinds[nearest(p)] = 'skull'
kinds[J] = 'blue'
skinds = (['blue', 'event', 'blue', 'red', 'blue', 'lucky', 'event', 'blue', 'red', 'blue', 'event', 'blue'] * 2)[:len(shorts)]
spaces = [{'x': x, 'y': y, 'z': z, 'kind': k, 'next': [(i + 1) % N]} for i, ((x, y, z), k) in enumerate(zip(mains, kinds))]
spaces[J]['next'] = [(J + 1) % N, N]
spaces[(J + 1) % N]['way'] = '町を進む'
for i, ((x, y, z), k) in enumerate(zip(shorts, skinds)):
    spaces.append({'x': x, 'y': y, 'z': z, 'kind': k, 'next': [N + i + 1 if i + 1 < len(shorts) else 0]})
spaces[N]['way'] = '神殿の近道'
PATH = set((x, z) for x, y, z in main_cells + short_cells)
PATHY = {}
for x, y, z in main_cells + short_cells: PATHY[(x, z)] = max(PATHY.get((x, z), -9), y)
SPACE_XZ = set()
for s in spaces:
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1): SPACE_XZ.add((s['x'] + dx, s['z'] + dz))
def near_path(x, z, r=2):
    return any((x + dx, z + dz) in PATH or (x + dx, z + dz) in SPACE_XZ for dx in range(-r, r + 1) for dz in range(-r, r + 1))
# ショップの屋台の向き(道から外へ、平らな方)。屋台は main.js の buildStall が 外向き 3〜7 × 横 ±3 に建てる
RESERVED = set()
for i, s in enumerate(spaces):
    if s['kind'] != 'shop': continue
    best = None
    for n in ([1, 0], [-1, 0], [0, 1], [0, -1]):
        t = [-n[1], n[0]]
        area = [(s['x'] + n[0] * a + t[0] * b, s['z'] + n[1] * a + t[1] * b) for a in range(2, 9) for b in range(-4, 5)]
        bad = sum(1 for p in area if p in PATH or p in SPACE_XZ) * 10 + sum(1 for p in area if H.get(p) != s['y'])
        if best is None or bad < best[0]: best = (bad, n, area)
    s['n'] = best[1]
    for p in best[2]: RESERVED.add(p); H[p] = s['y']

# ===== 地面 =====
for (x, z), h in H.items():
    sea_edge = not all(inside(x + dx, z + dz) for dx, dz in ((4, 0), (-4, 0), (0, 4), (0, -4)))
    beach = z < 98 and h == 0 and x > -20 or sea_edge and h <= 0
    if h == -3:  # 川
        box(x, YB, z, x, -4, z, 'stone'); put(x, -3, z, 'sand'); put(x, -2, z, 'water'); put(x, -1, z, 'water'); continue
    box(x, YB, z, x, h - 2, z, 'stone')
    if h >= 3:  # 崖・段の側面
        for y in range(0, h):
            put(x, y, z, random.choice(['stone', 'stone', 'andesite', 'cobblestone', 'mossy_cobblestone']) if x >= 31 else ('stone_bricks' if random.random() < 0.8 else 'mossy_stone_bricks'))
    put(x, h - 1, z, 'sand' if beach else 'dirt')
    put(x, h, z, 'sand' if beach else ('moss_block' if (x < -24 and random.random() < 0.35) else 'grass_block'))
# 段の上のふちに石のふち取り(丘)
for (x, z), h in list(H.items()):
    if h in (3, 6, 9) and x < 31:
        if any(H.get((x + dx, z + dz), 99) < h for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))): put(x, h, z, 'polished_andesite' if h < 9 else 'quartz_block')
# 海(外まわり)と、水が外へ流れないふち
for x in range(X0, X1 + 1):
    for z in range(Z0, Z1 + 1):
        if (x, z) in H: continue
        edge = x in (X0, X1) or z in (Z0, Z1)
        put(x, -4, z, 'prismarine_bricks' if edge else 'sand')
        for y in (-3, -2, -1): put(x, y, z, 'prismarine_bricks' if edge else 'water')
        if edge: put(x, 0, z, 'prismarine_bricks')
# 滝: 北東の崖の上から川へ(上の水は3方を囲む)
box(21, 0, 172, 31, 7, 182, 'stone'); [put(x, 8, z, 'grass_block') for x in range(21, 32) for z in range(172, 183)]
clear(24, 1, 172, 28, 7, 172)
box(23, 8, 173, 29, 8, 175, 'mossy_cobblestone'); box(24, 8, 173, 28, 8, 174, 'water'); put(26, 8, 172, 'water')
box(22, 0, 166, 30, 0, 171, 'water')

# ===== 道とマス =====
COL = {'start': 'white_concrete', 'blue': 'light_blue_concrete', 'red': 'red_concrete', 'event': 'lime_concrete', 'lucky': 'yellow_concrete',
       'shop': 'purple_concrete', 'skull': 'black_concrete'}
for i, (x, y, z) in enumerate(main_cells + short_cells):
    ground = H.get((x, z))
    bridge = ground is None or ground < y - 1 or ground == -3
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            if (dx and dz): continue
            g = H.get((x + dx, z + dz))
            if g is not None and g > y: clear(x + dx, y + 1, z + dz, x + dx, g + 1, z + dz)  # 崖を切り通す
            if bridge:
                put(x + dx, y, z + dz, 'spruce_planks' if (dx or dz) else 'stripped_spruce_log')
                lo = (g if g is not None and g != -3 else -2)
                if (x + z) % 6 == 0 and not (dx or dz) and y - lo > 1: box(x, lo + 1, z, x, y - 1, z, 'spruce_fence')
            elif g is not None and g < y: box(x + dx, max(g, -2), z + dz, x + dx, y - 1, z + dz, 'stone_bricks')
    put(x, y, z, 'magenta_glazed_terracotta' if i % 3 == 0 else 'white_concrete')
    clear(x, y + 1, z, x, y + 3, z)
for s in spaces:
    x, y, z = s['x'], s['y'], s['z']
    box(x - 2, y, z - 2, x + 2, y, z + 2, 'smooth_quartz')
    box(x - 1, y, z - 1, x + 1, y, z + 1, COL[s['kind']])
    clear(x - 2, y + 1, z - 2, x + 2, y + 4, z + 2)
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            g = H.get((x + dx, z + dz))
            if g is None or g < y - 1: box(x + dx, max(-2, g if g is not None else -2), z + dz, x + dx, y - 1, z + dz, 'stone_bricks')
# 町の人が使う街灯(道のそば)
for k, (x, y, z) in enumerate(main_cells[::9]):
    for dx, dz in ((2, 0), (-2, 0), (0, 2), (0, -2)):
        p = (x + dx, z + dz)
        if p in PATH or p in SPACE_XZ or p in RESERVED or H.get(p) != y: continue
        box(x + dx, y + 1, z + dz, x + dx, y + 2, z + dz, 'dark_oak_fence'); put(x + dx, y + 3, z + dz, 'lantern'); break

def free(x1, z1, x2, z2, y=None):
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            if (x, z) in PATH or (x, z) in SPACE_XZ or (x, z) in RESERVED or (x, z) not in H: return False
            if y is not None and H[(x, z)] != y: return False
    return True

# ===== 北の町 =====
WALLS = ['white_terracotta', 'orange_terracotta', 'yellow_terracotta', 'light_gray_terracotta', 'cyan_terracotta', 'pink_terracotta', 'stripped_birch_wood', 'smooth_sandstone']
ROOFS = ['red_nether_bricks', 'dark_prismarine', 'deepslate_tiles', 'brick_block', 'blue_terracotta', 'green_terracotta', 'mud_bricks']
def house(x, z, w, d, flo=2):
    y = 0
    wall, roof = random.choice(WALLS), random.choice(ROOFS)
    hgt = 4 * flo
    box(x, y + 1, z, x + w - 1, y + hgt, z + d - 1, wall)
    box(x + 1, y + 1, z + 1, x + w - 2, y + hgt, z + d - 2, 'air')
    for cx in (x, x + w - 1):
        for cz in (z, z + d - 1): box(cx, y + 1, cz, cx, y + hgt, cz, 'stripped_dark_oak_log')
    for f in range(flo):
        yy = y + 2 + f * 4
        for xx in range(x + 2, x + w - 2, 2): put(xx, yy, z, 'glass'); put(xx, yy, z + d - 1, 'glass')
        for zz in range(z + 2, z + d - 2, 2): put(x, yy, zz, 'glass'); put(x + w - 1, yy, zz, 'glass')
        box(x, y + 4 + f * 4, z, x + w - 1, y + 4 + f * 4, z, 'stripped_dark_oak_log') if f < flo - 1 else None
    # 屋根(だんだん小さく)
    k = 0
    while True:
        x1, z1, x2, z2 = x - 1, z - 1 + k, x + w, z + d - k
        if z1 > z2: break
        box(x1, y + hgt + 1 + k, z1, x2, y + hgt + 1 + k, z2, roof)
        if z1 + 1 <= z2 - 1: box(x, y + hgt + 1 + k, z1 + 1, x + w - 1, y + hgt + 1 + k, z2 - 1, wall)  # 妻壁
        if z1 + 2 <= z2 - 2: box(x + 1, y + hgt + 1 + k, z1 + 2, x + w - 2, y + hgt + 1 + k, z2 - 2, 'air')
        k += 1
    box(x - 1, y + hgt + k, z + (d - 1) // 2, x + w, y + hgt + k, z + d // 2, roof)
    if random.random() < 0.6: box(x + 1, y + hgt + 1, z + 1, x + 1, y + hgt + k + 1, z + 1, 'bricks'.replace('bricks', 'brick_block'))
    # 入口(道の方 = 南か北)
    door_z = z if abs(z - 166) < abs(z + d - 1 - 166) else z + d - 1
    box(x + w // 2, y + 1, door_z, x + w // 2, y + 2, door_z, 'air'); put(x + w // 2, y + 3, door_z, 'lantern' if False else wall)
    put(x + w // 2 - 1, y + 3, door_z + (-1 if door_z == z else 1), 'lantern')
for side, z in ((-1, 162), (1, 170)):
    x = 12
    while x > -40:
        w, d = random.randint(6, 8), random.randint(6, 7)
        zz = z - d + 1 if side < 0 else z
        if free(x - w, zz - 1, x + 1, zz + d, 0): house(x - w + 1, zz, w, d, random.choice([1, 2, 2])); x -= w + random.randint(1, 2)
        else: x -= 2
# 町の市場の小さな屋台(色つきの屋根)
for x, z, c in ((-14, 160, 'yellow'), (-30, 160, 'lime'), (2, 160, 'light_blue')):
    if free(x - 1, z - 1, x + 2, z + 1, 0):
        box(x, 1, z, x + 1, 1, z, 'barrel'); box(x - 1, 1, z - 1, x - 1, 2, z - 1, 'oak_fence'); box(x + 2, 1, z - 1, x + 2, 2, z - 1, 'oak_fence')
        box(x - 1, 3, z - 1, x + 2, 3, z + 1, f'{c}_wool')
# 町の広場の小さな噴水と花だん
box(-24, 1, 158, -20, 1, 162, 'stone_bricks'); box(-23, 1, 159, -21, 1, 161, 'water'); box(-22, 1, 160, -22, 3, 160, 'prismarine_wall'); put(-22, 4, 160, 'sea_lantern')

# ===== 木・キノコ =====
def tree(x, z, kind='oak', big=False):
    y = H.get((x, z));
    if y is None or y < 0: return
    hgt = random.randint(6, 9) if big else random.randint(4, 6)
    log = {'oak': 'oak_log', 'birch': 'birch_log', 'azalea': 'oak_log', 'cherry': 'cherry_log'}[kind]
    box(x, y + 1, z, x, y + hgt, z, log)
    r = 3 if big else 2
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            for dy in range(-1, 3):
                if dx * dx + dz * dz + (dy * 1.6) ** 2 <= r * r + 1 and random.random() < 0.93 and (x + dx, y + hgt + dy, z + dz) not in V:
                    put(x + dx, y + hgt + dy, z + dz, LEAF[kind])
def mushroom(x, z, red=True):
    y = H.get((x, z));
    if y is None: return
    h = random.randint(6, 9)
    box(x, y + 1, z, x, y + h, z, 'bone_block'); box(x - 1, y + 1, z - 1, x + 1, y + 2, z + 1, 'bone_block')
    cap = 'red_mushroom_block ["huge_mushroom_bits"=14]' if red else 'brown_mushroom_block ["huge_mushroom_bits"=14]'
    r = 4 if red else 5
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            d = math.hypot(dx, dz)
            if d <= r: put(x + dx, y + h + (1 if d < r - 1.5 else 0) + (1 if d < 1.5 and red else 0), z + dz, cap)
            if red and r - 1 <= d <= r: put(x + dx, y + h - 1, z + dz, cap)
    if red:
        for dx, dz in ((2, 1), (-1, 2), (1, -2), (-2, -1)): put(x + dx, y + h + 2 if math.hypot(dx, dz) < 2.5 else y + h + 1, z + dz, 'white_concrete')
# 西の森
for i in range(70):
    x, z = random.randint(-49, -22), random.randint(96, 162)
    if free(x - 2, z - 2, x + 2, z + 2): tree(x, z, random.choice(['oak', 'birch', 'oak', 'azalea']), big=random.random() < 0.4)
for (x, z, red) in [(-30, 128, True), (-31, 145, False), (-29, 110, True), (-46, 140, True), (-46, 117, False)]:
    if free(x - 1, z - 1, x + 1, z + 1): mushroom(x, z, red)
# あちこちの木(桜)
for i in range(40):
    x, z = random.randint(-46, 46), random.randint(84, 176)
    if abs(x) < 18 and abs(z - CZ) < 18: continue
    if free(x - 2, z - 2, x + 2, z + 2, 0): tree(x, z, 'cherry' if random.random() < 0.5 else 'oak')

# ===== 東の崖: 灯台・遺跡・クリスタル =====
def lighthouse(x, z):
    y = H[(x, z)]
    for k in range(14):
        r = 3 if k < 6 else 2
        b = 'red_concrete' if (k // 2) % 2 else 'white_concrete'
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r + 1: put(x + dx, y + 1 + k, z + dz, b)
    box(x - 2, y + 15, z - 2, x + 2, y + 15, z + 2, 'iron_block'); box(x - 1, y + 16, z - 1, x + 1, y + 17, z + 1, 'glass'); put(x, y + 16, z, 'sea_lantern'); put(x, y + 17, z, 'sea_lantern')
    box(x - 2, y + 18, z - 2, x + 2, y + 18, z + 2, 'red_concrete'); box(x - 1, y + 19, z - 1, x + 1, y + 19, z + 1, 'red_concrete'); put(x, y + 20, z, 'gold_block')
lighthouse(45, 118)
for (x, z) in [(43, 132), (46, 146), (42, 158), (32, 150)]:
    if free(x - 1, z - 1, x + 1, z + 1):
        h = random.randint(3, 7); y = H[(x, z)]
        box(x, y + 1, z, x, y + h, z, 'quartz_pillar'); put(x, y + h + 1, z, 'chiseled_quartz_block')
        if random.random() < 0.5: put(x + 1, y + 1, z, 'quartz_block'); put(x, y + 1, z + 1, 'smooth_quartz')
for (x, z) in [(44, 126), (33, 138), (45, 165), (40, 150), (34, 126)]:
    if free(x - 1, z - 1, x + 1, z + 1):
        y = H[(x, z)]
        for k in range(random.randint(3, 6)): put(x, y + 1 + k, z, 'amethyst_block')
        put(x + 1, y + 1, z, 'amethyst_block'); put(x, y + 1, z - 1, 'amethyst_block'); put(x - 1, y + 2, z, 'amethyst_block'); put(x, y + 1, z + 1, 'glowstone')
# 崖のまわりに滝の上の小屋
box(27, 9, 178, 30, 12, 181, 'spruce_planks'); box(28, 9, 179, 29, 11, 180, 'air'); box(26, 13, 177, 31, 13, 182, 'dark_oak_planks'); box(27, 14, 178, 30, 14, 181, 'dark_oak_planks')
# 高いつり橋の西のはしの塔
box(14, 0, 162, 20, 7, 170, 'stone_bricks'); box(15, 1, 163, 19, 6, 169, 'air')
for (x, z) in ((14, 162), (20, 162), (14, 170), (20, 170)): box(x, 8, z, x, 9, z, 'stone_brick_wall'); put(x, 10, z, 'lantern')
box(14, 7, 166, 20, 7, 166, 'stripped_spruce_log')

# ===== 南西の港: 桟橋と帆船 =====
box(-26, 0, 80, -24, 0, 92, 'spruce_planks'); [box(-26, -3, z, -26, -1, z, 'spruce_log') or box(-24, -3, z, -24, -1, z, 'spruce_log') for z in range(80, 93, 3)]
def ship(cx, cz):
    L = 22
    for i in range(L):
        z = cz - L // 2 + i
        t = abs(i - L / 2) / (L / 2)
        hw = max(1, round(4 * (1 - t ** 3)))
        bot = -2 if t < 0.7 else -1
        for dx in range(-hw, hw + 1):
            box(cx + dx, bot, z, cx + dx, 1, z, 'dark_oak_planks' if abs(dx) == hw else 'air')
            put(cx + dx, bot, z, 'dark_oak_planks')
        box(cx - hw + 1, 1, z, cx + hw - 1, 1, z, 'spruce_planks')
        put(cx - hw, 2, z, 'dark_oak_fence'); put(cx + hw, 2, z, 'dark_oak_fence')
        box(cx - hw, -1, z, cx - hw, 0, z, 'red_concrete'); box(cx + hw, -1, z, cx + hw, 0, z, 'red_concrete')
    for mz, mh in ((cz - 4, 13), (cz + 5, 10)):
        box(cx, 2, mz, cx, 2 + mh, mz, 'spruce_log')
        for k in range(2, mh - 2):
            w = 4 - abs(k - mh // 2) // 3
            box(cx - w, 2 + k + 1, mz + 1, cx + w, 2 + k + 1, mz + 1, 'white_wool')
        put(cx, 3 + mh, mz, 'red_wool'); put(cx, 3 + mh, mz + 1, 'red_wool')
    box(cx, 1, cz + L // 2, cx, 1, cz + L // 2 + 5, 'spruce_fence')  # 船首の棒
    box(cx - 2, 2, cz - L // 2 + 1, cx + 2, 4, cz - L // 2 + 4, 'dark_oak_planks'); box(cx - 1, 3, cz - L // 2 + 1, cx + 1, 3, cz - L // 2 + 1, 'glass')
ship(-36, 88)

# ===== 真ん中の丘: 女神の神殿 =====
cx, cz, ty = 0, 130, 9
for dx in range(-6, 7):
    for dz in range(-6, 7):
        if dx * dx + dz * dz <= 42: put(cx + dx, ty, cz + dz, 'quartz_block' if (dx + dz) % 2 else 'smooth_quartz')
for k in range(8):
    a = k / 8 * math.pi * 2
    px, pz = round(cx + math.cos(a) * 6), round(cz + math.sin(a) * 6)
    if (px, pz) in PATH or any((px + ddx, pz + ddz) in PATH for ddx in (-1, 0, 1) for ddz in (-1, 0, 1)): continue
    box(px, ty + 1, pz, px, ty + 8, pz, 'quartz_pillar'); put(px, ty + 9, pz, 'gold_block')
# 女神の像(白い石 + 金の髪かざり)
box(-5, ty + 1, 133, -3, ty + 1, 135, 'chiseled_quartz_block')
box(-4, ty + 2, 134, -4, ty + 6, 134, 'quartz_block'); box(-5, ty + 4, 134, -3, ty + 4, 134, 'quartz_block'); put(-4, ty + 7, 134, 'white_concrete')
box(-5, ty + 2, 134, -5, ty + 3, 134, 'quartz_block'); put(-3, ty + 5, 134, 'quartz_block'); put(-2, ty + 6, 134, 'quartz_block')
box(4, ty + 1, 133, 4, ty + 1, 135, 'chiseled_quartz_block'); box(3, ty + 1, 134, 5, ty + 1, 134, 'chiseled_quartz_block')
# 宙にうかぶ金の輪
for k in range(56):
    a = k / 56 * math.pi * 2
    put(round(cx + math.cos(a) * 8), ty + 14, round(cz + math.sin(a) * 8), 'gold_block')
for k in range(4):
    a = k / 4 * math.pi * 2 + math.pi / 4
    put(round(cx + math.cos(a) * 8), ty + 15, round(cz + math.sin(a) * 8), 'sea_lantern')
# 丘の段の花だん
for i in range(260):
    x, z = random.randint(-16, 16), random.randint(114, 146)
    h = H.get((x, z))
    if h in (3, 6) and (x, z) not in PATH and (x, z) not in SPACE_XZ and (x, y := h + 1, z) not in V and V.get((x, h, z)) == 'grass_block' and random.random() < 0.5:
        put(x, h + 1, z, random.choice(['poppy', 'dandelion', 'cornflower', 'allium', 'pink_tulip', 'azure_bluet', 'lily_of_the_valley']))

# ===== 南の広場(ロビー・スタート)=====
for x in range(-13, 14):
    for z in range(98, 115):
        if (x, z) in H and H[(x, z)] == 0 and (x, z) not in PATH:
            put(x, 0, z, 'polished_diorite' if (x + z) % 2 else 'smooth_stone')
box(-14, 0, 97, 14, 0, 97, 'gold_block'); box(-14, 0, 115, 14, 0, 115, 'gold_block')
for x in (-12, 12):
    for z in (100, 112):
        box(x, 1, z, x, 4, z, 'quartz_pillar'); put(x, 5, z, 'sea_lantern')
# 入口のアーチ(南)
box(-4, 1, 97, -4, 7, 97, 'quartz_pillar'); box(4, 1, 97, 4, 7, 97, 'quartz_pillar'); box(-5, 8, 97, 5, 8, 97, 'quartz_block')
for x, c in zip(range(-3, 4), ['red', 'orange', 'yellow', 'lime', 'light_blue', 'blue', 'purple']): put(x, 9, 97, f'{c}_concrete')
clear(-3, 1, 97, 3, 7, 97)

# 浜辺: パラソル・ヤシ・岩
def palm(x, z):
    y = H.get((x, z), 0); hgt = random.randint(5, 7)
    for k in range(hgt): put(x + (1 if k > hgt * 0.6 else 0), y + 1 + k, z, 'jungle_log')
    tx = x + 1; ty = y + hgt
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2), (3, -1), (-3, -1), (-1, 3), (1, -3)): put(tx + dx, ty + (0 if abs(dx) + abs(dz) < 3 else -1), z + dz, LEAF['oak'].replace('oak', 'jungle'))
    put(tx, ty + 1, z, LEAF['oak'].replace('oak', 'jungle'))
for i in range(60):
    x, z = random.randint(-44, 44), random.randint(80, 100)
    if V.get((x, 0, z)) != 'sand' or near_path(x, z, 2) or (x, z) in RESERVED: continue
    r = random.random()
    if r < 0.25 and free(x - 1, z - 1, x + 1, z + 1): palm(x, z)
    elif r < 0.45 and free(x - 2, z - 2, x + 2, z + 2):
        c = random.choice(['red', 'orange', 'light_blue', 'pink', 'lime'])
        box(x, 1, z, x, 3, z, 'oak_fence'); box(x - 1, 4, z - 1, x + 1, 4, z + 1, f'{c}_wool'); put(x, 5, z, f'{c}_wool')
        put(x + 2, 1, z, 'white_carpet') if (x + 2, 1, z) not in V else None
    elif r < 0.6: put(x, 1, z, random.choice(['cobblestone', 'mossy_cobblestone', 'andesite']))
# 港の荷物
for x, z in ((-23, 90), (-23, 91), (-22, 90), (-27, 84)): put(x, 1, z, random.choice(['barrel', 'oak_planks', 'hay_block']))
# 崖の上: 草むら・こわれた壁・木
for i in range(80):
    x, z = random.randint(31, 47), random.randint(110, 176)
    if H.get((x, z)) != 7 or near_path(x, z, 1) or (x, z) in RESERVED or (x, 8, z) in V: continue
    r = random.random()
    if r < 0.35: put(x, 8, z, LEAF['azalea'])
    elif r < 0.45: box(x, 8, z, x, 8 + random.randint(0, 2), z, random.choice(['mossy_stone_bricks', 'cracked_stone_bricks', 'stone_bricks']))
    elif r < 0.5 and free(x - 2, z - 2, x + 2, z + 2): tree(x, z, 'birch')
# 森と丘のまわりの草むら
for i in range(220):
    x, z = random.randint(-48, 30), random.randint(96, 176)
    h = H.get((x, z))
    if h != 0 or near_path(x, z, 1) or (x, z) in RESERVED or (x, 1, z) in V or V.get((x, 0, z)) not in ('grass_block', 'moss_block'): continue
    if random.random() < 0.35: put(x, 1, z, LEAF['oak'] if random.random() < 0.7 else LEAF['azalea'])

# 丘と川の間: 風車と花畑
def windmill(x, z):
    y = H.get((x, z), 0)
    for k in range(10):
        r = 3 if k < 5 else 2
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if max(abs(dx), abs(dz)) == r: put(x + dx, y + 1 + k, z + dz, 'stripped_birch_wood' if k % 4 else 'stripped_dark_oak_log')
    for k in range(3): box(x - 2 + k, y + 11 + k, z - 2 + k, x + 2 - k, y + 11 + k, z + 2 - k, 'red_nether_bricks')
    box(x, y + 2, z - 3, x, y + 3, z - 3, 'air'); put(x, y + 7, z - 4, 'stripped_spruce_log')
    for a in range(4):  # 羽根(南向き)
        for t in range(1, 8):
            dx, dy = [(t, 0), (-t, 0), (0, t), (0, -t)][a]
            put(x + dx, y + 7 + dy, z - 5, 'spruce_fence' if t < 3 else 'white_wool')
            if t >= 3: put(x + dx + (0 if dx else 1), y + 7 + dy + (0 if dy else 1), z - 5, 'white_wool')
if free(10, 136, 16, 142, 0): windmill(13, 139)
for (fx, fz, w, d) in ((8, 110, 10, 8), (-28, 170, 8, 5), (6, 146, 9, 4)):
    for x in range(fx, fx + w):
        for z in range(fz, fz + d):
            if H.get((x, z)) == 0 and not near_path(x, z, 1) and (x, z) not in RESERVED and (x, 1, z) not in V:
                put(x, 1, z, ['red_tulip', 'orange_tulip', 'white_tulip', 'pink_tulip'][(x // 2) % 4])
# 花をあちこちに
for i in range(500):
    x, z = random.randint(-48, 48), random.randint(80, 180)
    h = H.get((x, z))
    if h is None or h < 0 or near_path(x, z, 1) or (x, z) in RESERVED: continue
    if V.get((x, h, z)) in ('grass_block', 'moss_block') and (x, h + 1, z) not in V and random.random() < 0.35:
        put(x, h + 1, z, random.choice(['poppy', 'dandelion', 'cornflower', 'oxeye_daisy', 'allium', 'pink_tulip', 'short_grass', 'short_grass', 'fern']))

# ===== コマンドにまとめる(同じブロックの直方体をまとめる)=====
def merge():
    by = {}
    for (x, y, z), b in V.items(): by.setdefault(b, set()).add((x, y, z))
    cmds = []
    for b, pts in by.items():
        pts = set(pts)
        while pts:
            x, y, z = min(pts)
            x2 = x
            while (x2 + 1, y, z) in pts: x2 += 1
            z2 = z
            while all((xx, y, z2 + 1) in pts for xx in range(x, x2 + 1)): z2 += 1
            y2 = y
            while all((xx, y2 + 1, zz) in pts for xx in range(x, x2 + 1) for zz in range(z, z2 + 1)) and (x2 - x + 1) * (z2 - z + 1) * (y2 - y + 2) <= 32000: y2 += 1
            for xx in range(x, x2 + 1):
                for yy in range(y, y2 + 1):
                    for zz in range(z, z2 + 1): pts.discard((xx, yy, zz))
            cmds.append((y, f'fill {x} {y} {z} {x2} {y2} {z2} {b}' if (x, y, z) != (x2, y2, z2) else f'setblock {x} {y} {z} {b}'))
    # 下から順に(花や灯りは土台のあと)
    order = lambda c: (c[0], 1 if any(k in c[1] for k in ('lantern', 'poppy', 'dandelion', 'cornflower', 'allium', 'tulip', 'bluet', 'valley', 'daisy', 'grass ', 'fern', 'water', 'fence')) else 0)
    return [c for _, c in sorted(cmds, key=order)]
cmds = merge()
data = {'spaces': spaces, 'cmds': cmds, 'area': [X0, YB, Z0, X1, YT, Z1], 'center': {'x': 0.5, 'z': 130.5}, 'lobby': {'x': 0.5, 'y': 1, 'z': 106.5},
        'finale': {'z': 110.5, 'camZ': 104.5}, 'version': 8}
open(OUT_JS, 'w', encoding='utf-8').write('// tools/mpl_board.py で作ったボード「女神の島」のデータ(手で書きかえない)\nexport const BOARD_DATA = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('spaces', len(spaces), 'main', N, 'short', len(shorts), 'junction', J, 'cmds', len(cmds), 'kb', os.path.getsize(OUT_JS) // 1024)

# ===== 見本(ななめ上から)=====
C = {'jungle_log': (90, 70, 40), 'oak_fence': (150, 120, 70), 'barrel': (120, 85, 50), 'hay_block': (200, 170, 40), 'oak_planks': (170, 135, 80), 'cracked_stone_bricks': (115, 115, 115), 'white_carpet': (240, 240, 240), 'yellow_wool': (240, 210, 50), 'lime_wool': (120, 200, 40), 'light_blue_wool': (100, 170, 230), 'orange_wool': (240, 130, 30), 'pink_wool': (240, 150, 180), 'grass_block': (110, 170, 70), 'moss_block': (90, 140, 50), 'dirt': (130, 95, 60), 'stone': (125, 125, 125), 'andesite': (135, 135, 135), 'cobblestone': (110, 110, 110),
     'mossy_cobblestone': (95, 115, 90), 'stone_bricks': (120, 120, 120), 'mossy_stone_bricks': (100, 120, 95), 'sand': (220, 210, 160), 'water': (50, 110, 210),
     'prismarine_bricks': (80, 160, 140), 'polished_andesite': (150, 150, 150), 'quartz_block': (235, 230, 225), 'smooth_quartz': (240, 236, 230), 'spruce_planks': (115, 85, 50),
     'stripped_spruce_log': (140, 110, 70), 'spruce_fence': (115, 85, 50), 'white_concrete': (240, 240, 240), 'magenta_glazed_terracotta': (220, 90, 200),
     'light_blue_concrete': (60, 160, 230), 'red_concrete': (190, 40, 40), 'lime_concrete': (110, 200, 40), 'yellow_concrete': (245, 200, 30), 'purple_concrete': (120, 40, 170),
     'black_concrete': (25, 25, 30), 'dark_oak_fence': (70, 50, 30), 'lantern': (255, 200, 90), 'oak_log': (110, 85, 50), 'birch_log': (220, 215, 200), 'cherry_log': (90, 50, 60),
     'bone_block': (230, 225, 205), 'white_terracotta': (210, 180, 165), 'orange_terracotta': (165, 85, 40), 'yellow_terracotta': (185, 135, 35), 'light_gray_terracotta': (135, 105, 95),
     'cyan_terracotta': (85, 90, 90), 'pink_terracotta': (160, 80, 80), 'stripped_birch_wood': (200, 180, 120), 'smooth_sandstone': (220, 205, 155), 'red_nether_bricks': (90, 15, 15),
     'dark_prismarine': (50, 90, 75), 'deepslate_tiles': (55, 55, 60), 'brick_block': (150, 80, 65), 'blue_terracotta': (75, 60, 90), 'green_terracotta': (75, 85, 40), 'mud_bricks': (140, 105, 80),
     'stripped_dark_oak_log': (70, 55, 35), 'glass': (200, 230, 240), 'iron_block': (220, 220, 220), 'sea_lantern': (200, 230, 230), 'gold_block': (250, 210, 60),
     'quartz_pillar': (235, 230, 220), 'chiseled_quartz_block': (230, 225, 215), 'amethyst_block': (150, 100, 200), 'glowstone': (250, 220, 130), 'dark_oak_planks': (65, 45, 25),
     'white_wool': (245, 245, 245), 'red_wool': (180, 40, 40), 'polished_diorite': (200, 200, 200), 'smooth_stone': (170, 170, 170), 'stone_brick_wall': (120, 120, 120),
     'spruce_log': (80, 60, 35), 'prismarine_wall': (90, 160, 150), 'orange_concrete': (240, 120, 20), 'blue_concrete': (45, 50, 150), 'light_gray_concrete': (150, 150, 150)}
def colr(b):
    if b in C: return C[b]
    if 'leaves' in b: return {'oak': (60, 130, 40), 'bir': (110, 150, 60), 'aza': (90, 140, 70), 'che': (240, 170, 200), 'jun': (50, 140, 40)}[b[:3]]
    if 'mushroom' in b: return (200, 40, 40) if b.startswith('red') else (150, 110, 80)
    return (230, 120, 160) if any(k in b for k in ('poppy', 'tulip', 'allium')) else (240, 220, 80) if 'dandelion' in b else (110, 160, 70)
S = 9
W, Hh = 1500, 1150
img = Image.new('RGB', (W, Hh), (40, 110, 170)); zb = [[-1e9] * Hh for _ in range(W)]
pix = img.load()
def proj(x, y, z):  # 南から見下ろす
    return W / 2 - 60 + (x - 0) * S * 1.2 + (z - CZ) * S * 0.25, Hh * 0.55 - (z - CZ) * S * 0.75 - y * S * 1.05
top = {}
for (x, y, z), b in V.items():
    if (x, y + 1, z) in V and 'leaves' not in V[(x, y + 1, z)]: continue
    k = (x, z)
    if k not in top or top[k][0] < y: top[k] = (y, b)
items = sorted(V.items(), key=lambda kv: (-kv[0][2], kv[0][1]))
d = ImageDraw.Draw(img)
for (x, y, z), b in items:
    if (x, y + 1, z) in V and (x, y, z - 1) in V and V[(x, y, z - 1)] != 'water' and V[(x, y + 1, z)] != 'water': continue
    c = colr(b)
    px, py = proj(x, y, z)
    d.polygon([(px, py), (px + S * 1.2, py), (px + S * 1.2 + S * 0.25, py - S * 0.75), (px + S * 0.25, py - S * 0.75)], fill=c)
    if (x, y, z - 1) not in V or V.get((x, y, z - 1)) == 'water':
        dc = tuple(int(v * 0.72) for v in c)
        d.polygon([(px, py), (px + S * 1.2, py), (px + S * 1.2, py + S * 1.05), (px, py + S * 1.05)], fill=dc)
img.save(OUT_PNG)
print('preview ok')
