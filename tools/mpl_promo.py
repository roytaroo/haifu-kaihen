# 紹介画像(6枚、1920x1080)を HTML で組んで、ブラウザで画像にする
#   1) python3 tools/mpl_promo_assets.py   (キャラ・アイコン・島の素材)
#   2) フォント: npm i @fontsource/noto-sans-jp @fontsource/dela-gothic-one @fontsource/dotgothic16 @fontsource/m-plus-rounded-1c を FONTS のフォルダに
#   3) python3 tools/mpl_promo.py            → mpl/promo/01_kv.png 〜 06_credits.png
import os, sys, json, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PR = os.path.join(ROOT, 'mpl', 'promo'); A = 'assets'
FONTS = os.environ.get('MPL_FONTS', '/tmp/claude-0/-home-user/27f9a445-997c-58ba-94fa-f114226baa21/scratchpad/kv/node_modules/@fontsource')
F = lambda p: f'@import url("file://{FONTS}/{p}");'
CSS = '\n'.join([F('noto-sans-jp/400.css'), F('noto-sans-jp/700.css'), F('noto-sans-jp/900.css'), F('dela-gothic-one/400.css'), F('dotgothic16/400.css'), F('m-plus-rounded-1c/800.css')]) + '''
:root{--bg1:#0c0a20;--bg2:#171238;--ink:#fff;--sub:#a8a5d8;--line:rgba(255,255,255,.16);--pink:#ff5fa8;--sky:#4fd2ff;--gold:#ffc93d;--green:#7be36a;--purple:#b48cff;--orange:#ff9a3d}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;overflow:hidden}
body{background:radial-gradient(1400px 900px at 70% 30%,#231a55 0%,var(--bg1) 70%);color:var(--ink);font-family:"Noto Sans JP",sans-serif;position:relative}
.dela{font-family:"Dela Gothic One",sans-serif}.dot{font-family:"DotGothic16",sans-serif}.round{font-family:"M PLUS Rounded 1c",sans-serif}
.head{position:absolute;left:72px;top:56px;right:72px;display:flex;align-items:center;gap:30px;padding-bottom:30px;border-bottom:2px solid rgba(255,255,255,.75)}
.head img{height:74px}.head .bar{width:3px;height:60px;background:rgba(255,255,255,.8)}
.head h1{font-family:"Noto Sans JP";font-weight:900;font-size:62px;letter-spacing:.02em}
.head .right{margin-left:auto;font-size:26px;font-weight:700;color:var(--sub);display:flex;gap:26px}
.sky{color:var(--sky)}.pink{color:var(--pink)}.gold{color:var(--gold)}.green{color:var(--green)}.purple{color:var(--purple)}.orange{color:var(--orange)}
.grain{position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(255,255,255,.015) 0 2px,transparent 2px 4px);pointer-events:none}
'''
def page(name, body, extra=''):
    html = f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{extra}</style></head><body>{body}<div class="grain"></div></body></html>'
    open(os.path.join(PR, f'{name}.html'), 'w', encoding='utf-8').write(html)
    return name

pages = []
# ===== 1. 表紙 =====
#   背景はグラデーション。左にロゴとコピー、その右に DJトシオ(元の向きのまま、島の方を向く)、右に島の絵
pages.append(page('01_kv', f'''
<div class="glow"></div>
<img class="isl" src="{A}/island.png">
<div class="fade"></div>
<div class="sh"></div><img class="dj" src="{A}/char_dj.png">
<div class="left">
  <img class="logo" src="{A}/logo.png">
  <p class="copy">島じゅう巻きこむ、<br>すごろくパーティ。</p>
  <p class="foot">Minecraft 統合版</p>
</div>
''', '''
body{background:linear-gradient(120deg,#100d2c 0%,#1d1650 38%,#2a2a7a 70%,#2f5aa8 100%)}
.glow{position:absolute;right:60px;top:140px;width:1000px;height:860px;background:radial-gradient(closest-side,rgba(120,170,255,.35),rgba(120,170,255,0))}
.isl{position:absolute;right:-150px;top:170px;width:1000px}
.fade{position:absolute;inset:0;background:linear-gradient(90deg,#100d2c 0%,rgba(16,13,44,.8) 34%,rgba(16,13,44,0) 50%)}
.dj{position:absolute;left:1040px;bottom:70px;height:620px;image-rendering:pixelated}
.sh{position:absolute;left:1035px;bottom:46px;width:300px;height:56px;border-radius:50%;background:radial-gradient(closest-side,rgba(5,4,20,.65),rgba(5,4,20,0))}
.left{position:absolute;left:70px;top:170px;width:900px}
.logo{display:block;width:900px}
.left p{padding-left:193px}   /* PARTY の P の左はしにそろえる(ロゴの幅の 21.5%) */
.copy{margin-top:64px;font-weight:900;font-size:40px;line-height:1.45;letter-spacing:.02em}
.foot{margin-top:30px;font-weight:700;font-size:22px;color:#a7a3d6;letter-spacing:.04em}
.grain{display:none}
'''))
# ===== 2. あそびかた =====
pages.append(page('02_rules', f'''
<div class="head"><img src="{A}/logo.png"><div class="bar"></div><h1>あそびかた</h1></div>
<div class="row top">
  <div class="c"><img src="{A}/icon_star.png"><h2 class="gold">スター</h2><p class="b">いちばん多く集めた人が優勝</p><p class="s">同じ数ならコインの多い人</p></div>
  <div class="c"><img src="{A}/icon_coin.png"><h2 class="orange">コイン</h2><p class="b">20枚でスターが1つ買える</p><p class="s">マスやミニゲームで増える</p></div>
  <div class="c"><img src="{A}/icon_dice.png"><h2 class="pink">サイコロ</h2><p class="b">1〜10。ジャンプで叩く</p><p class="s">アイテムで2個・3個ふれる</p></div>
  <div class="c"><img src="{A}/icon_crown.png"><h2 class="sky">ミニゲーム</h2><p class="b">毎ターンの最後に全員で</p><p class="s">1位 10・2位 5・3位 3コイン</p></div>
</div>
<div class="flow">
  <div class="lbl">1ターンの流れ</div>
  <div class="steps"><div><i>1</i>アイテムを使う</div><span>›</span><div><i>2</i>サイコロ</div><span>›</span><div><i>3</i>止まったマスのできごと</div><span>›</span><div><i>4</i>全員でミニゲーム</div></div>
</div>
<div class="row bottom">
  <div class="c2"><h3>ターン数</h3><p class="big sky">5 / 10 / 15 / 20</p><p class="s">ラスト3ターンは青・赤マスが2倍</p></div>
  <div class="c2"><h3>ショップとアイテム</h3><p class="big pink">11 種類</p><p class="s">ダブルサイコロ・ワープパイプ ほか</p></div>
  <div class="c2"><h3>BOT</h3><p class="big gold">10 人から選べる</p><p class="s">人数が足りなくても遊べる。強さは3段階</p></div>
</div>
''', '''
.row{position:absolute;left:72px;right:72px;display:grid}
.top{top:220px;grid-template-columns:repeat(4,1fr)}
.top .c{padding:0 34px;border-left:2px solid var(--line)}.top .c:first-child{border-left:0;padding-left:0}
.top img{width:84px;height:84px;margin-bottom:8px}
.top h2{font-weight:900;font-size:58px;line-height:1.15}
.b{font-weight:700;font-size:30px;margin-top:12px}.s{color:var(--sub);font-size:24px;margin-top:6px}
.flow{position:absolute;left:72px;right:72px;top:600px;border-top:2px solid var(--line);border-bottom:2px solid var(--line);padding:26px 0;display:flex;align-items:center;gap:40px}
.lbl{font-size:24px;color:var(--sub);font-weight:700;white-space:nowrap}
.steps{display:flex;align-items:center;gap:22px;font-size:32px;font-weight:900}
.steps i{font-style:normal;display:inline-grid;place-items:center;width:46px;height:46px;border-radius:50%;background:var(--purple);color:#140f33;font-size:26px;margin-right:12px;vertical-align:3px}
.steps span{color:var(--sub);font-size:44px;font-weight:400}
.bottom{top:780px;grid-template-columns:repeat(3,1fr)}
.c2{padding:0 34px;border-left:2px solid var(--line)}.c2:first-child{border-left:0;padding-left:0}
.c2 h3{font-size:24px;color:var(--sub);font-weight:700}.big{font-size:46px;font-weight:900;margin-top:4px}
'''))
# ===== 3. 島のイベント =====
EV = [('噴火', 'red', '溶岩が流れ出す。火山の上の人はコインを落としてふもとへ'), ('満潮', 'sky', '3ターンごとに浜が水びたし。近道が沈んで、潮の道が開く'),
      ('幽霊船', 'purple', '霧の中から来航。帆船の上を通ると、幻の店に寄れる'), ('ドローブリッジ', 'gold', '2ターンごとに上下する。通れる道が変わる'),
      ('鏡のマス', 'pink', 'ガイコツがタダでコインを、50枚でスターを奪う'), ('DJトシオ', 'green', '今日のルール・タイムセール・潮の予報をお知らせ')]
ev_html = ''.join(f'<div class="ev"><h2 style="color:var(--{"pink" if c=="red" else c})">{t}</h2><p>{d}</p></div>' for t, c, d in EV)
pages.append(page('03_island', f'''
<div class="head"><img src="{A}/logo.png"><div class="bar"></div><h1>女神の島</h1><div class="right"><span>108マス</span><span>分かれ道 6</span><span>高低差あり</span></div></div>
<img class="isl" src="{A}/island.png">
<div class="evs">{ev_html}</div>
''', '''
.isl{position:absolute;left:30px;top:210px;width:960px;filter:drop-shadow(0 30px 40px rgba(0,0,0,.5))}
.gs{position:absolute;left:760px;top:250px;width:230px;filter:drop-shadow(0 12px 18px rgba(0,0,0,.5))}
.evs{position:absolute;left:1040px;right:72px;top:214px;display:flex;flex-direction:column;gap:20px}
.ev{border-left:4px solid rgba(255,255,255,.25);padding:6px 0 8px 24px}
.ev h2{font-weight:900;font-size:40px;line-height:1.15}.ev p{color:#d9d6f5;font-size:25px;line-height:1.5;margin-top:4px;white-space:nowrap}
'''))
# ===== 4. キャラ =====
BOT = [('Jack', 'jack', '元気なお調子者', '主役はオレだ！ みんな見とけよ〜！', 'sky'), ('Humming', 'humming', 'がんばり屋', 'が、がんばります！ 負けないから！', 'gold'),
       ('Widow', 'widow', '無口でけだるい', '…眠い。早く終わらせよ', 'purple'), ('Splash', 'splash', 'いつも眠いマイペース', 'ふぁ〜…パーティ？ がんばる〜', 'green'),
       ('Oracle', 'oracle', 'ヘラヘラ天才', 'は〜い、今日もサクッと勝っちゃお〜', 'pink'), ('Byte', 'byte', 'ロボット', 'システム起動。勝利プロトコル、開始シマス。', 'sky'),
       ('Shade', 'shade', 'いたずら好きのうっかり者', 'にしし、今日は何してやろっかな〜', 'orange'), ('Jester', 'jester', 'びっくりさせ屋', 'ばぁっ！ …びっくりした？ 始めよっか！', 'pink'),
       ('Replica', 'replica', 'なぞめいたからかい屋', 'ふふ…わたしはだれでしょう？', 'purple'), ('Comet', 'comet', 'ぶっきらぼうな脳筋', 'さっさと始めるぞ。勝つのはオレだ', 'gold')]
cards = ''.join(f'<div class="cd" style="--c:var(--{c})"><img src="{A}/head_{f}.png"><div><div class="nm">{n}<span>{p}</span></div><div class="ln">「{l}」</div></div></div>' for n, f, p, l, c in BOT)
pages.append(page('04_chars', f'''
<div class="head"><img src="{A}/logo.png"><div class="bar"></div><h1>BOT 10人</h1><div class="right"><span>人数が足りなくても、にぎやかに</span></div></div>
<div class="cards">{cards}</div>
''', '''
.cards{position:absolute;left:72px;right:72px;top:206px;display:grid;grid-template-columns:1fr 1fr;gap:18px 30px}
.cd{display:flex;align-items:center;gap:22px;background:linear-gradient(90deg,rgba(255,255,255,.07),rgba(255,255,255,.02));border-left:6px solid var(--c);padding:12px 22px;clip-path:polygon(0 0,calc(100% - 22px) 0,100% 22px,100% 100%,0 100%)}
.cd img{width:104px;height:104px;object-fit:contain}
.nm{font-weight:900;font-size:40px;line-height:1.1;display:flex;align-items:baseline;gap:16px}.nm span{font-size:22px;font-weight:700;color:var(--c);border:2px solid var(--c);padding:1px 12px;clip-path:polygon(0 0,calc(100% - 10px) 0,100% 10px,100% 100%,0 100%)}
.ln{color:#d9d6f5;font-size:24px;margin-top:8px}
'''))
# ===== 5. ミニゲーム =====
MG = ["計算早押し", "色の記憶", "椅子取りゲーム", "宝探しプール", "ファイアバー", "ボートレース", "ピッタリ止め", "ニワトリ集め", "一番多い色は？", "早押し反射", "隕石よけ", "押し寄せる壁", "障害物ダッシュ", "レーザー回避", "ものまねポーズ",
      "ピクセルアート", "卵キャッチ", "コイン噴水", "ふくらむ風船", "まっくらスイカ割り", "下がる天井", "ボヨンボール", "巨大ワニの歯", "コマぶつけ", "旗あげゲーム", "お皿バランス", "大玉ころがし", "ロデオ", "バンパーカー", "アスレチック"]
cols = ['sky', 'pink', 'gold', 'green', 'purple']
mg_html = ''.join(f'<div class="mg" style="--c:var(--{cols[i % 5]})"><i>{i + 1:02d}</i>{n}</div>' for i, n in enumerate(MG))
pages.append(page('05_minigames', f'''
<div class="head"><img src="{A}/logo.png"><div class="bar"></div><h1>ミニゲーム 30種</h1><div class="right"><span>毎ターンの最後にルーレットで決定</span></div></div>
<div class="mgs">{mg_html}</div>
<div class="note">同じミニゲームは続けて出ない ・ 4回に1回はコイン2倍のボーナス ・ 勝ち抜き戦モードもあり</div>
''', '''
.mgs{position:absolute;left:72px;right:72px;top:210px;display:grid;grid-template-columns:repeat(5,1fr);gap:20px 16px}
.mg{font-weight:900;font-size:31px;background:rgba(255,255,255,.05);border-bottom:4px solid var(--c);padding:26px 18px;display:flex;align-items:center;gap:14px;white-space:nowrap}
.mg i{font-style:normal;font-family:"DotGothic16";color:var(--c);font-size:28px}
.note{position:absolute;left:72px;right:72px;bottom:64px;border-top:2px solid var(--line);padding-top:24px;color:var(--sub);font-size:26px;font-weight:700}
'''))
# ===== 6. クレジット =====
pages.append(page('06_credits', f'''
<img class="lg" src="{A}/logo.png">
<div class="ttl">CREDITS</div>
<div class="cr">
  <div><h4>制作</h4><p>VENUS PARTY</p></div>
  <div><h4>音楽</h4><p>オリジナル曲</p><small>このワールドのために作曲</small></div>
  <div><h4>効果音</h4><p>Minecraft のゲーム内の音</p></div>
  <div><h4>ゲームの中の文字</h4><p>Minecraft のフォント</p></div>
  <div class="wide"><h4>画像のフォント</h4><p>Noto Sans JP / Dela Gothic One / DotGothic16</p><small>SIL Open Font License</small></div>
</div>
<div class="disc">NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.</div>
''', '''
body{text-align:center}
.lg{width:520px;margin-top:70px}
.ttl{font-weight:900;font-size:44px;color:var(--sky);margin-top:20px;letter-spacing:.06em}
.cr{display:grid;grid-template-columns:1fr 1fr;gap:40px 120px;width:1300px;margin:36px auto 0}
.cr h4{color:var(--gold);font-weight:700;font-size:28px}.cr p{font-weight:900;font-size:44px;margin-top:4px}.cr small{display:block;color:var(--sub);font-size:24px;margin-top:4px}.cr .wide{grid-column:1 / 3}
.disc{position:absolute;left:0;right:0;bottom:44px;color:#6f6c99;font-size:20px;letter-spacing:.02em}
'''))
# ===== ブラウザで画像に =====
js = os.path.join(PR, '_shot.cjs')
open(js, 'w').write('''const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
for (const n of process.argv.slice(2)) { await p.goto('file://' + __dirname + '/' + n + '.html'); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400); await p.screenshot({ path: __dirname + '/' + n + '.png' }); }
await b.close(); })();''')
subprocess.run(['node', js, *pages], check=True, cwd=PR)
print('promo', pages)
