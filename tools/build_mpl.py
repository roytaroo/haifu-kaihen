# MEGAMI PARTY LAND のワールドを作る
#   python3 tools/build_mpl.py v<番号> → dist/MPL-v<番号>.mcworld
# 地形もコマンドブロックもない空のワールド(ボイド)。建物はスクリプトが最初に建てる。
# level.dat はマイクラのワールド設定の形式だけ借りて、中身はすべて MPL 用の値にする
import json, os, random, sys, tempfile, time, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'mpl', 'src')
tag = sys.argv[1] if len(sys.argv) > 1 else 'dev'
out = os.path.join(ROOT, 'dist', f'MPL-{tag}.mcworld')

def level_dat():
    # 形式(キーと型)は 1.26 のワールド設定。値は MPL のもの
    with zipfile.ZipFile(os.path.join(ROOT, 'mmg', 'original', 'MMG.mcworld')) as z: raw = z.read('level.dat')
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'level.dat'); open(p, 'wb').write(raw)
        ver, name, root = nbt.read(p)
        keep_types = {k: v[0] for k, v in root.items()}
        def put(k, v): root[k] = (keep_types.get(k, 8 if isinstance(v, str) else 3), v)
        put('LevelName', f'VENUS PARTY {tag}')
        put('RandomSeed', random.randint(1, 2**62)); put('LastPlayed', int(time.time())); put('currentTick', 0); put('worldStartCount', 0)
        put('SpawnX', 0); put('SpawnY', 1); put('SpawnZ', 65); put('Time', 6000); put('PlayerHasDied', 0)
        put('GameType', 2); put('Difficulty', 1); put('Generator', 2)
        put('FlatWorldLayers', json.dumps({'biome_id': 1, 'block_layers': [], 'encoding_version': 6, 'structure_options': None, 'world_version': 'version.post_1_18'}))
        for k, v in {'dodaylightcycle': 0, 'doweathercycle': 0, 'domobspawning': 0, 'pvp': 0, 'falldamage': 0, 'keepinventory': 1, 'doimmediaterespawn': 1,
                     'sendcommandfeedback': 0, 'commandblockoutput': 0, 'showcoordinates': 0, 'mobgriefing': 0, 'showdeathmessages': 0, 'commandsEnabled': 1, 'cheatsEnabled': 1}.items(): put(k, v)
        root['experiments'] = (10, {'gametest': (1, 1), 'experiments_ever_used': (1, 1), 'saved_with_toggled_experiments': (1, 1)})
        nbt.write(p, ver, name, root)
        return open(p, 'rb').read()

def icon():
    # だいきのロゴ(VENUS PARTY)を空色の背景にのせる
    im = Image.new('RGB', (256, 256)); d = ImageDraw.Draw(im)
    for y in range(256): d.line([(0, y), (256, y)], fill=(90 + y // 4, 170 + y // 6, 255 - y // 5))
    lg = Image.open(os.path.join(SRC, 'resource_packs', 'mpl_rp', 'textures', 'ui', 'mpl', 'logo_venus.png')).convert('RGBA')
    w = 240; lg = lg.resize((w, round(lg.height * w / lg.width)), Image.LANCZOS)
    im.paste(lg, ((256 - w) // 2, (256 - lg.height) // 2), lg)
    p = tempfile.mktemp(suffix='.jpeg'); im.save(p, quality=92); return open(p, 'rb').read()

def ref(kind, folder):
    h = json.load(open(os.path.join(SRC, kind, folder, 'manifest.json')))['header']
    return {'pack_id': h['uuid'], 'version': h['version']}

os.makedirs(os.path.dirname(out), exist_ok=True)
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('level.dat', level_dat())
    z.writestr('levelname.txt', f'VENUS PARTY {tag}')
    z.writestr('world_icon.jpeg', icon())
    for kind in ('behavior_packs', 'resource_packs'):
        for r, _, fs in os.walk(os.path.join(SRC, kind)):
            for f in fs: z.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), SRC))
    z.writestr('world_behavior_packs.json', json.dumps([ref('behavior_packs', 'mpl_bot'), ref('behavior_packs', 'mpl_bp')], indent=2))
    z.writestr('world_resource_packs.json', json.dumps([ref('resource_packs', 'mpl_rp')], indent=2))
print('->', out)
