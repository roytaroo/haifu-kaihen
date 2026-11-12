# 引き継ぎメモ

## 基本
- マイクラ統合版の配布ワールド改変(配布者の許可取得済み)。ワールドごとにフォルダを分ける。
- ユーザーは「だいき」と呼ぶ。返事は短く。ゲームで未確認のものは「未確認」と書く。頼まれてない変更はしない。
- **容量に注意**: 不必要な作業は最小限。全体を読まず、必要な所だけ grep して読む。
- 元のワールドは直接いじらず、パックを足す/差し替える形で改変する。

## 道具
- `tools/cmdblocks.py <db フォルダ> <出力.json>`: ワールドの LevelDB からコマンドブロック(座標・コマンド・auto)を全部抜き出す。

## 1. mmg/ — megami MMG Many Mini Games
- 原本: `mmg/original/MMG.mcworld`(作業前に一時フォルダへ unzip して使う)
- 展開済み(node_modules・db 抜き): `mmg/src/`。コマンドブロック一覧: `mmg/command_blocks.json`(1682個)
- パック: BP `main`(Many mini game: scripts/game.js + functions 51個)、`k-behavior_`(kohaku: 設定UI gameee.js)、`mmg-user-setting`(MMG OreUI)。RP `mmg-r`、`k-resource_`。
- 仕組み(コマンド中心、スクリプトは補助):
  - スコア `game` に偽プレイヤーで状態を持つ。`selectgame` = 今のゲーム番号(1〜24)。
  - `functions/select_game.mcfunction`: `random selectgame 1 24` → 番号ごとに地下のコマンド回路へ redstone_block。ゲーム名と説明の tellraw もここ。
  - `game_start` / `finish_game`(番号ごとのポイント付与 `scoreboard players add ... point 1`)/ `main_finish2`(全体の後片付け。ここで `point` を消して作り直す → **累計ランキングは別に保存が必要**)。
  - `game.js`: ランダムTP・投票UI・game4/10/12/17/22/24 の補助。`ranking` を 1 にするとチャットに point の順位を出す。
  - 設定: スコア `setting`(round, round-auto, testmode 等)、レベル `level game`(1〜5)。
- ゲーム一覧(selectgame): 1 Escape Lava / 2 熱帯魚相撲 / 3 High and Low / 4 TNT RUN / 5 Adventure PVP / 6 TNT TAG / 7 Drop PVP / 8 降下デスマッチ / 9 逆らえ！ / 10 金床避け / 11 読みぶろぱ / 12 TNT避け / 13 アスレチック / 14 どうぶつリレー / 15 Block Party / 16 鉱石バトル / 17 崩れる床で生き延びろ / 18 穴落とし / 19 色塗りバトル / 20 クラフトマスター / 21 Warden Escape / 22 マグマノックバック / 23 村人数え / 24 モンスターバトル
- ビルド: `python3 tools/build_mmg.py v<番号>` → `dist/MMG-v<番号>.mcworld`(dist は git に入れない。毎回番号を上げる)。最新 v15。
- 改変(v1、ゲーム内は未確認):
  - 追加パック `mmg_plus`(BP、scripts/main.js)+ `mmg_plus_r`(RP、掲示板の見えないエンティティ)。
  - 抽選をスクリプトへ: `select_game` → `scriptevent mmgplus:select`(OFFを除いて抽選、同じゲームの連続なし)→ `select_game_body`(元の残り+25〜27の説明)。
  - 25 計算早押し / 26 色の記憶 / 27 椅子取りゲーム。25以上は `mmgplus:prep`(会場づくり→game_ready)と `game_start` 末尾の `mmgplus:start` で動く。終わったら point 付与 → `function finish_game` → game_next_ready=1。
  - 設定メニュー(gameee.js settingUI_main)に「ミニゲームのON/OFF」「ランキング掲示板」を追加(admin_game-setting 権限)。OFF一覧は mmg_plus の dynamic property "off"。
  - ランキング: point の増加を見張って累計・ゲーム別勝利(ポイントを取った回数)、試合終了(playing 1→0)で優勝・最下位・0pt、死亡数、記録(25 最速回答、26 最長)。掲示板は OP が置いた場所に 8秒ごとにページ切替。kill 文に `type=!mmgplus:board` を追加。
  - 改変したパックはバージョンを上げた(main 0.1.5、k-behavior_ 0.1.2)。
- v2(未確認): 28 宝探しプール / 29 ジャンプ縄跳び / 30 ボートレース / 31 ピッタリ止め / 32 ニワトリ集め を追加。mmg_plus 1.0.1。
- v3(未確認): BOT。BP `mmg_bot`(scripts/bot.js、@minecraft/server-gametest 1.0.0-beta の spawnSimulatedPlayer)。**Beta APIs が要る**ので build_mmg.py が level.dat の experiments.gametest=1 を立てる。ワールドは 1.26.52 で保存されていた。ベータは版ごとに変わるので、マイクラ更新で動かなくなったら manifest の版を合わせる(npm の @minecraft/server-gametest の 1.0.0-beta.<版>-stable を確認)。
  - BOT はダミーのプレイヤーなので元のゲームの @a にそのまま入る。タグ `mmgbot`。設定メニュー「BOT」で人数(0〜12)と強さ(よわい/ふつう/つよい、setting の bot_strength にも入れる)。ワールドを開き直すと前の人数を出し直す。
  - 動き: 攻撃系(2,5,7,8,22,24)は近くの相手を追ってなぐる、TNT TAG は鬼なら追う/ちがえば逃げる、Escape Lava はダイヤへ、鉱石バトルは近くの鉱石を掘る、椅子取りは空いたトロッコへ、宝探しは金ブロックへ、ニワトリ集めはたねを持って往復、ほかは歩き回る。
  - mmg_plus 側: 計算早押し・ピッタリ止めは BOT の答えを作る(フォームを出さない)、色の記憶は床へ飛ばす、縄跳びは `scriptevent mmgbot:jump <名前>` でジャンプさせる、ボートレースはボートを押して角をめざす。BOT はランキングに入れない。
- v4(未確認): 文句ボード(https://claude.ai/artifact/8kwXB8zc3jXF9kogUtkjTV、db の complaints)の18件に対応。
  - 削除: 3 High and Low / 8 降下デスマッチ / 10 金床避け / 11 読みぶろぱ / 12 TNT避け / 16 鉱石バトル / 17 崩れる床(main.js の REMOVED。抽選・ON/OFF・掲示板から外す)。
  - TNT TAG: 生き残りが参加人数の1/3以下で終了(mmg_plus が stopgame=1 と元の終了回路 29 -14 17 を叩く)。村人数え: 時間 60/50/42/36/30秒。逆らえ！: 命令18種(9〜18 の判定は mmg_plus、game9_1/game9_2 にも追加)。
  - 追加ゲーム作り直し: 計算早押し(むずかしく)、色の記憶(5色・五角形・光る柱・判定を厳しく)、椅子取り(イスのモデル mmgplus:chair・曲)、宝探し(29x29・浮く宝 mmgplus:treasure_*、金1/ダイヤ3/エメ5点、**砂を使わない**: v1〜v3 は y=0 に砂を置いてコマンド部屋に落ちた)、29 はファイアバー(mmgplus:fireball 2本)、ボートレース(z -46→46 の一本道)、ピッタリ止め(よーい→スタートの合図)、ニワトリ集め(半径20・エサやり禁止)。
  - 会場の片付けは field 全体(x -24〜25, z -49〜50, y 1〜8)。
- v5(未確認): 新ゲーム 33 一番多い色は？/34 早押し反射(しゃがむ)/35 矢の雨/36 隕石よけ/37 押し寄せる壁/38 障害物ダッシュ/39 配置の記憶。改変: 逆らえ！28種、村人数え(時間 80/70/60/55/50・Lv4以降に行商人と村人ゾンビ)、椅子取り(ニセモノ mmgplus_fake・逃げるイス mmgplus_run)、宝探し(43x43・フグで2点落とす)、ファイアバー(15秒で上の棒・しゃがみでよける)、ニワトリ(25秒でキツネ)、最終2ラウンド得点2倍、ラウンド結果(チャット+タイトル)、優勝の演出(試合後)。
- v6(未確認): 選んだ残り全部。40 レーザー回避〜57 バンパーカー の18ゲーム + 58 アスレチック(5コース、元の13は REMOVED)。モデルは `tools/models.py`(色つきの箱 → BP/RP のエンティティ・geo・テクスチャ・アニメと dist/model_preview/*.png)。図鑑: https://claude.ai/artifact/CfGKr5h5usUtREPKKMeaaL
  - 乗り物(コマ・カート・大玉・牛)は rideable のカスタムエンティティに applyImpulse。大きさ・傾き・かみつき・暴れは entity property(mmgplus:size/tilt/bite/buck)でアニメ。
  - 旗あげゲームの声はまだ(だいきが音をくれたら RP の sounds に入れて playsound する)。
- v7(未確認): ラウンド結果を専用の JSON UI に(tools/rank_ui.py → RP ui/server_form.json。タイトルの印 RANK_MARK、ボタン2つで1行、行の背景 = 順位の色×上下×自分、行は順にすべりこむ、7秒で閉じる)。文字をクラシック(カクカク)フォントにそろえる UI 上書き(hud/chat/scoreboard/ボタン/フォームのタイトル)。ワニと牛のモデルを作り込み版に(残り13個は だいきの OK 待ち)。
- v8(未確認): モデル16個すべてを作り込み版に(tools/models.py の rounded/disc/eyes で丸み・目・模様)。イスも models.py に移した(props.geo.json から外した)。
- v9(未確認): ワニの歯を巨大ワニに(scale 4、長さ約14マス、当たり判定は胴の真ん中だけ)。叩く歯8本(scale 2)を開いた口の下あごに並べる(TOOTH_SPOTS)。かまれると画面がゆれる。
- v10: v7〜v9 でオペレーターアイテムのフォームが見えなくなった件の修正(未確認)。server_form.json の long_form を modifications で足すのをやめて、BOWFLIT と同じく long_form をまるごと定義。推測で書いたボタン/タイトルのフォント上書き(ui_template_buttons/dialogs)を削除。結果画面の alpha アニメを削除(offset だけ)。
- v11(未確認): BOT がロビーでも歩き回る・走る/跳ぶ(lively, lobbyRoam)。初めから OFF: 1,2,4,5,6,7,14,15,18,20,22(DEFAULT_OFF、保存済みの設定にも offv=2 で一度だけ足す)。全ゲーム順番モード(ON/OFF 画面の一番上のトグル → seq を保存して main_start、round を本数に。DEFAULT_OFF は入れない)。頭脳系(計算・色の記憶・一番多い色・配置の記憶・ピクセル・旗あげ・ピッタリ止め)と早押し反射の BOT を弱く。
  - 確認リスト: https://claude.ai/artifact/8GN43ZJKurVTvMCWRsUPw3(db "checks")
- v12(未確認): だいきの文句に対応。削除: 35 矢の雨・39 配置の記憶・41 しっぽ取り。カウントダウン(元の game_start_countdown の titleraw と音)を消した。暗視をどのゲームにも(47以外)。Warden の透明を消す。村人数えのまぎらわしいモブは行商人と魔女、BOT の答えは scoreboard game23_a に入れる。計算かんたん、色の記憶ゆっくり、オクラホマミキサー、宝探し・卵30秒、スイカ・コイン45秒、ニワトリ60秒、ファイアバーは端まで、ボート・ダッシュ・大玉はゴールで観戦へ、隕石むずかしく、壁の速さをなだらかに、ダッシュむずかしく、レーザーはモデル(mmgplus:laser_beam)、ものまねは4色の壁、ピクセルは仕切りと名前、卵は BOT が散る、風船は輪になって動けない(inputpermission)、コインは噴水のまわりから、ワニの向き、コマ/カートはブースト(mmgplus:boost、tools/items.py)と場外の線がせまる、旗あげは旗のアイテム(赤=オフハンド・しゃがむ、白=右手・右クリック)、大玉は柵のすきま保証・速く・体力1、BOT の名前から Bot_ を外した、色塗りで雪玉、泳ぐポーズを直す。
  - v13: ラウンド結果で全行が1行目になる件 → collection_name を行・段・カードにもつけた。カードを細く(230)。出すきっかけを nextgame.mcfunction の scriptevent mmgplus:round_end に(前は 5tick ごとの見張りで見逃していた)。
- v14(未確認): OP メニューに「このゲームをスキップ」(確認画面 → スキップ)。run.active を止め、元の回路の redstone_block を消し(main_finish2 と同じ範囲)、selectgame=0 で finish_game、会場を空にして game_next_ready=1。ポイントは入らない。
- v15(未確認): 椅子取りの曲を だいきがくれた音(オクラホマミキサー、28秒)に。RP sounds/mmgplus/chair_music.ogg + sound_definitions(mmgplus.chair_music、category record)。毎ラウンド最初から流して 6〜20秒で stopsound。
- 次の候補: 記録系を既存ゲーム(アスレのタイム等)にも広げる。

## だいきが選んだもの(100ゲーム計画 https://claude.ai/artifact/UCiagkMnba3rgPeyUqeSmV の db "picks")
- 新ゲーム25: 隕石よけ/矢の雨/押し寄せる壁/レーザー回避/しっぽ取り/障害物ダッシュ/ものまねポーズ/一番多い色は？/配置の記憶/早押し反射/ピクセルアート再現/卵キャッチ/コイン噴水/ふくらむ風船(1/3残るまで)/まっくらスイカ割り/下がる天井/風船割り合戦/ボヨンボール/ワニの歯/コマぶつけ/旗あげゲーム(声はだいきが渡す、指示のバリエーションを考える)/お皿バランス/大玉ころがし/ロデオ/バンパーカー
- 改変10: 逆らえ！のバリエーション追加 / アスレ5コース / 村人数え: Lv4以降ほかのモブ混ぜ・時間さらにのばす / 椅子取り: 座ると消えるニセモノと逃げるイスだけ / 宝探し: 妨害の魚・プールを広く / ファイアバー: 棒を増やす / ニワトリ: キツネ乱入 / 最終ラウンド得点2倍 / 勝者の演出(試合全体の最後) / ラウンド結果の画面
- 作る順: v5 = 改変(アスレ以外)+ モデル不要の7ゲーム。v6 以降 = 残り(モデルが要るもの、アスレ5コース)。

## 2. mpl/ — MEGAMI PARTY LAND(MPL)
- MMG から移行した新しいワールド。**元の配布ワールドのものは何も使わない**(パック・絵・文言・コマンドブロック・建物)。使っていいのは自分たちで作ったもの(mmg_plus の追加ゲーム・モデル・画面・音・BOT)。
- ビルド: `python3 tools/build_mpl.py v<番号>` → `dist/MPL-v<番号>.mcworld`。空のワールド(ボイド)、昼で固定、Beta APIs ON。level.dat は形式だけ借りて値は MPL 用。
- パック: BP `mpl_bp`(scripts/main.js = 共通 + ミニゲーム(mmg_plus から持ってきた 25〜58)+ すごろく)、BP `mpl_bot`(BOT)、RP `mpl_rp`(モデル・UI・音・アイテム)。MPL だけのモデル(サイコロ・スター)とメニューのアイテムは `tools/mpl_assets.py`。
- 場所: ミニゲームの会場 x -24〜25, z -49〜50(床 y=0)、ボードは中心 (0,0,130)、33マス(青+3・赤-3・?イベント・!ラッキー)。tickingarea で両方を読み込んだままにする。
- 流れ: メニュー(mpl:menu、最初に入った人 = タグ mpl_admin が持つ)→ パーティを始める(ターン数・むずかしさ)→ 1人ずつサイコロ(叩く)→ 進む(スターのマスを通ると20コインで買える)→ マスの効果 → 全員が終わったらミニゲーム(ルーレット)→ 勝った人 +10コイン → 順位の画面。最後はボーナススター(ミニゲーム王・コイン王)と優勝の演出。
- ミニゲームの約束: スコアボード game の selectgame/playing/level、タグ playing・mmgplus_out・mmgbot。ミニゲームの関数は勝った人の配列を返す。
- 引き継ぐ元のゲーム(仕組みも文言も作り直す、まだ): ブンブンバット(熱帯魚相撲)・あまのじゃく(逆らえ！)・競馬(どうぶつリレー、全部馬・馬名と服の色)・Block Party・縄張りバトル(色塗りバトル)・スティーブ数え(村人数え)。アスレチックは自作の5コースだけ。
- MPL v2(未確認): 右の表 = スコアボードの名前に順位バッジ・★・コインのアイコン(RP font/glyph_E1.png、tools/mpl_glyphs.py、U+E100〜)、点数の列は消す、見出しはターン。結果画面は 8倍の解像度(MPL_RP=… RANK_SCALE=8 python3 tools/rank_ui.py)。
  - すごろく: スポーンは広場 (0,1,124)。ボードを島+城+アーチ+街灯+噴水+木に。マス: 青・赤・?・!・ショップ(紫、通ると買える)・ドクロ。アイテム5種(ダブル/トリプルサイコロ・ワープパイプ・金のパイプ・どろぼう手袋、3つまで)。サイコロはジャンプして頭で叩く(lateral_movement だけ止めて、ジャンプはできる)。スタート通過 +5。カメラ演出(camera コマンド)。BGM はオリジナル(tools/mpl_music.py、sounds/mpl/*.ogg、is3D false)。メニューに「すごろくを終わる」「ミニゲームを1つ選んで遊ぶ」「BGM の ON/OFF」。
  - BOT: ミニゲームからの指示 scriptevent mmgbot:move/look/sneak/stop/jump(BOT パック)。ワープ移動をやめて歩く・向く。タグ mpl_lock / mpl_board の間は動かない。
  - ミニゲーム: 風船割り合戦(49)削除。押し寄せる壁の会場(buildWalls)が消えていたのを戻した(MMG も)。ファイアバーは棒までの距離で当たり判定・炎の玉のモデル・バリアの囲い。会場のまわりの柵はバリアに。ボヨンボールは壁ではね上がる。風船は「すき間のない球」(models.py sphere)。ワニは体と口の横をバリア、歯は口の前のほうに2列、口に入ったら押し出す。持ち物は左手・よろいも消す。
- MPL v6(未確認): BGM は合成のものが不評 → 最初 OFF(メニューで ON)。だいきの音: スター獲得 sounds/mpl/star_get.ogg(8.0秒、カメラが1周→アップ→花火)、結果発表 drumroll.ogg(8.8秒、横一列の前をカメラが流れ、鳴り終わりで優勝者にズーム)。ショップは屋台(buildStall、マスの外側): 止まるとシャッターが開き村人(villager_v2、タグ mpl_shopkeeper)、カウンターに5種から3品(mpl:item_*、tools/mpl_assets.py)、買う/立ち去るで閉まる。通るだけでは開かない。

## MPL v7(演出を作り直し)
- 安っぽい表示をやめた: ふつうの文字タイトル・マスの上に浮く名札・チャットのお知らせ
- 新しい演出: `tools/mpl_ui.py`(rank_ui.py の「あと」に実行)
  - ロゴ 18種(グラデ + 太いふち + ポンと出る + きらっと光る + 放射)、サイコロの数字 0〜30、色つきの帯 6色、ミニゲーム説明カード
  - しくみ: タイトルの頭に見えない印 `BMARK` + キー番号(main.js の `BKEYS` と mpl_ui.py の `KEYS` は同じ順番)。HUD のタイトルの中にロゴを入れ、印がある時だけふつうのタイトルをかくす
  - main.js: `banner(key, sub, stay, players, text)` / `ribbon(color, text, sub, stay, players)` / `subAll()`(ルーレット)
  - 専用フォーム: タイトルに `FORM_MARK` → カード + 帯の見出し + 専用ボタン(ショップ・スター・アイテム・メニュー・ミニゲーム選び)
  - チャット → 画面下のお知らせ(`toast` / `bar`、背景も差しかえ)。管理者向けエラー [MPL] だけチャット
  - サイドバーの背景も差しかえ
- ボード v7: マスの名札・大看板・SHOP の名札・お店の人の名前を消した(建て直しで消える)
- サイコロの数字・残りマスの名札 → ロゴの数字・下のお知らせ
- bot の LOBBY を z 124.5 に
- すべて未確認(とくに: ロゴがタイトルの位置に出るか、専用フォームのボタンが押せるか、サイドバー背景)

## MPL v8(全部英語表記)
- だいきの指示「全部英語表記」: main.js の表示文字 349個をすべて英語に(ミニゲーム名・説明・帯・フォーム・お知らせ)。bot.js・アイテム名・「乗る」・パック説明も英語
- ロゴも英語(InterDisplay Black Italic)。傾きをやめて、立体の厚み + 文字間を詰めた
- 置きかえ表: 作業時の jp.txt / en.txt(同じ順番)。同じ日本語は同じ英語にしたので、文字列で比べる処理(旗あげの RED/WHITE、ポーズの SNEAK/JUMP など)はそのまま動くはず
- 未確認

## MPL v9(ロゴを太字のドット文字に)
- 自作の 5x7 ドット文字(tools/mpl_pixfont.py、A-Z 0-9 ! . 空白)を横に1ドット太らせて使う
- 小さく描いて、ぼかさずに拡大。3段グラデ + 上の列だけ光る + 内の色ふち・白ふち・黒ふち + 下に3ドットの厚み
- 未確認

## MPL v10
- (失敗: 戻しが効いておらずドットのまま。使わない)

## MPL v11
- v9 のドット文字ロゴをやめて、v8 の英語・立体ロゴに戻した(だいきの指示)。ロゴ・UI・tools/mpl_ui.py は v8 と同じ。パックのバージョンだけ上げた

## MPL v12(英語は演出の見出しだけ)
- だいき: 英語にしたいのは演出のタイトルだけ。チャット・メニューのボタン・設定は日本語のままでいい
  - main.js・bot.js・アイテム名・「乗る」・パック説明を v7 の日本語に戻した
  - 英語のまま: ロゴ全部 + 帯の見出し(PASSED START / NOT ENOUGH COINS / SEE YOU AGAIN! / COIN SHOWER! / COIN THIEF! / WARP! / SWAP! / DROPPED COINS / A GIFT! / EVERYONE EQUAL! / NO WINNER / MINIGAME STAR / COIN STAR)
- 専用フォーム: 見出しの星アイコンがはみ出していた → フォームの見出しからアイコンを消した
- 専用フォームの文字は全部太字(§l)+ 英語設定と同じフォント(classic、ほかの画面と同じ仕組み)
- 未確認

## MPL v13(メニューを一番右に固定)
- keepMenu(p): 管理者のスロット9(一番右)に mpl:menu を「スロットに固定(ItemLockMode.slot)+ 死んでも残る(keepOnDeath)」で置く
- 0.5秒ごとに確認して、消された(ミニゲームの clear など)・ちがう物がある時は戻す。スロット9にあった物はほかの場所へよける。ほかの場所のメニューは消す
- 未確認

## MPL v14(フォント統一・太字 / BOT が動かない)
- フォント: MPL の UI の全ラベルを font_type "unicode"(英語設定と同じマイクラのドット文字。漢字・かなもドット)に。mpl_ui.py の最後の unify() で hud・フォーム・サイドバー・チャットをまとめて変える(前の "#font_type: classic" はやめた)
- 太字: main.js / bot.js で setTitle・setActionBar・updateSubtitle・sendMessage・フォームの文字を包んで §l をつける(boldText)。先頭の見えない印はそのまま残す。色コードのあとにも §l。サイドバーの行も太字
  - ふつうのフォーム(ModalForm の設定など)は文字だけ太字。フォントは標準のまま(未対応)
- BOT: navigateToLocation は道が見つからないと何もしない → 会場の中は moveToLocation でまっすぐ歩く。ロビーは道さがし → だめならまっすぐ。止まったままなら行き先を変える(ファイアバーで同じ場所でジャンプし続けていた)
- 未確認

## MPL v15(メニューをスクロール)
- 専用フォーム: ボタンが6個以上の時は高さ 88% のカードにして、ボタンの部分を common.scrolling_panel でスクロール(公式の long_form と同じ書き方)。5個以下は今まで通り中身に合わせた大きさ
  - 表示の切りかえは #form_button_length で判定
- 未確認
