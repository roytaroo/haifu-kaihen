# mmg/src のパックで MMG のワールドを作り直す
#   python3 tools/build_mmg.py <タグ> → dist/MMG-<タグ>.mcworld
# 原本(mmg/original/MMG.mcworld)の地形・level.dat はそのまま、パックと適用リストだけ差し替える。ワールド名にタグを付ける
import json, os, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'mmg', 'src')
tag = sys.argv[1] if len(sys.argv) > 1 else 'dev'
out = os.path.join(ROOT, 'dist', f'MMG-{tag}.mcworld'); os.makedirs(os.path.dirname(out), exist_ok=True)

def packs(kind, order):
    # order: 上ほど優先。リストにないパックは後ろに足す
    names = [n for n in order if os.path.isdir(os.path.join(SRC, kind, n))]
    names += sorted(n for n in os.listdir(os.path.join(SRC, kind)) if n not in names)
    ref = []
    for n in names:
        h = json.load(open(os.path.join(SRC, kind, n, 'manifest.json'), encoding='utf-8'))['header']
        ref.append({'pack_id': h['uuid'], 'version': h['version']})
    return ref

with zipfile.ZipFile(os.path.join(ROOT, 'mmg', 'original', 'MMG.mcworld')) as zin, zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for item in zin.infolist():
        top = item.filename.split('/')[0]
        if top in ('behavior_packs', 'resource_packs', 'world_behavior_packs.json', 'world_resource_packs.json', 'levelname.txt'):
            continue
        z.writestr(item, zin.read(item.filename))
    for kind in ('behavior_packs', 'resource_packs'):
        for r, _, fs in os.walk(os.path.join(SRC, kind)):
            for f in fs:
                full = os.path.join(r, f); z.write(full, os.path.relpath(full, SRC))
    z.writestr('world_behavior_packs.json', json.dumps(packs('behavior_packs', ['mmg_plus', 'mmg-user-setting', 'k-behavior_', 'main']), indent=2))
    z.writestr('world_resource_packs.json', json.dumps(packs('resource_packs', ['mmg_plus_r', 'mmg-r', 'k-resource_']), indent=2))
    z.writestr('levelname.txt', f'megami MMG Plus {tag}')
print('->', out)
