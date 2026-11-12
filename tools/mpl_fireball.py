# MPL のファイアバーの火の玉(大きく太い炎の玉)を作り直す
#   python3 tools/mpl_fireball.py → mpl_rp / mpl_bp の mmgplus:fireball と見本 mpl/preview_fireball.png
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import models as M
ROOT = M.ROOT
M.BP = os.path.join(ROOT, 'mpl', 'src', 'behavior_packs', 'mpl_bp')
M.RP = os.path.join(ROOT, 'mpl', 'src', 'resource_packs', 'mpl_rp')
M.PREVIEW = os.path.join(ROOT, 'mpl')
R = 7  # 半径 7px(直径 約0.9ブロック)
# 下が赤オレンジ → 上ほど黄色 → てっぺんが白っぽい(炎の玉のグラデ)。球を少しずつ上にずらして重ねる
cubes = [*M.sphere(0, R, 0, R, (235, 70, 10), step=1.0, light=30),
         *M.sphere(0, R + 0.9, 0, R - 0.6, (255, 160, 25), step=1.0, light=30),
         *M.sphere(0, R + 2.6, 0, R - 2.5, (255, 235, 130), step=1.0, light=15)]
import math
M.model('fireball', '大きな炎の玉(ファイアバー・隕石)', cubes, bones={'root': [0, R, 0]},
        anim={'root': {'rotation': ["math.sin(q.life_time * 500) * 12", "q.life_time * 540", 0], 'scale': "1 + math.sin(q.life_time * 1100) * 0.06"}}, box=(0.5, 0.5))  # 当たり判定はスクリプトで見る。体の箱は小さいまま
M.write('fireball', M.MODELS['fireball'])
os.replace(os.path.join(M.PREVIEW, 'fireball.png'), os.path.join(ROOT, 'mpl', 'preview_fireball.png')) if os.path.exists(os.path.join(M.PREVIEW, 'fireball.png')) else None
print('ok')
