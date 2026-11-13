# MPL の音を「距離に関係なく同じ音量で聞こえる音」にする
#   カメラ演出中は聞く位置がカメラ側に移るので、ふつうの playsound(場所つき)だと、遠いと小さい・聞こえない
#   → スクリプトで使っている音を全部調べ、公式の音ファイルを指す mplx.<もとの名前>(category ui / is3D false)を作る
#   → main.js / bot.js の cmd() が playsound の名前を mplx. に差しかえる(scripts/sound_ids.js の一覧にあるものだけ)
#   使い方: python3 tools/mpl_sounds.py <公式の sound_definitions.json>
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp')
SC = os.path.join(ROOT, 'mpl', 'src', 'behavior_packs', 'mpl_bp', 'scripts')
t = open(sys.argv[1], encoding='utf-8').read()
t = re.sub(r'(?m)^\s*//.*$', '', t); t = re.sub(r',(\s*[}\]])', r'\1', t)
van = json.loads(t); van = van.get('sound_definitions', van)
src = open(os.path.join(SC, 'main.js'), encoding='utf-8').read() + open(os.path.join(ROOT, 'mpl', 'src', 'behavior_packs', 'mpl_bot', 'scripts', 'bot.js'), encoding='utf-8').read()
ids = set(re.findall(r'playsound ([a-z_][\w.]*)', src)) | set(re.findall(r'soundAll(?:Players)?\(\s*(?:[^"\n]*\?\s*)?"([\w.]+)"', src)) | set(re.findall(r'"((?:random|note|mob|block|ambient|firework|item|dig|step|music|portal|beacon|bucket|fire|liquid|game|raid|respawn_anchor|conduit|crossbow|bubble|elytra|horn|smithing_table|ui|camera|armor|sign|use|hit|fall|jump|land|place|break|bloom|cauldron|chime|component|copper|trial_spawner|vault|mace|wind_charge)\.[\w.]+)"', src))
ids |= {'block.barrel.open', 'block.barrel.close'}; ids.discard('block.barrel.')
p = os.path.join(RP, 'sounds', 'sound_definitions.json')
d = json.load(open(p, encoding='utf-8')); sd = d['sound_definitions']
for k in [k for k in sd if k.startswith('mplx.')]: del sd[k]
ok, miss = [], []
for i in sorted(ids):
    if i.startswith('mpl.') or i.startswith('mmgplus.') or i.startswith('mplx.'): continue
    v = van.get(i)
    if not v: miss.append(i); continue
    snds = []
    for s in v['sounds']:
        s = dict(s) if isinstance(s, dict) else {'name': s}
        s = {k: s[k] for k in ('name', 'volume', 'pitch', 'weight') if k in s}; s['is3D'] = False
        snds.append(s)
    sd['mplx.' + i] = {'category': 'ui', 'sounds': snds}; ok.append(i)
# 自作の音も: 距離なし + ui(音量のつまみに左右されにくい)
for k, v in sd.items():
    if k.startswith('mpl.') or k.startswith('mmgplus.'):
        v['category'] = 'ui'
        for s in v['sounds']: s['is3D'] = False
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(SC, 'sound_ids.js'), 'w', encoding='utf-8').write('// tools/mpl_sounds.py が作る: 距離なしの音(mplx.<名前>)がある音の一覧\nexport const SOUND_IDS = new Set(' + json.dumps(ok) + ');\n')
print('ok', len(ok), 'missing', miss)
