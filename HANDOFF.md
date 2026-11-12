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
- ビルド: `python3 tools/build_mmg.py v<番号>` → `dist/MMG-v<番号>.mcworld`(dist は git に入れない。毎回番号を上げる)。最新 v11。
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
- 次の候補: 記録系を既存ゲーム(アスレのタイム等)にも広げる。

## だいきが選んだもの(100ゲーム計画 https://claude.ai/artifact/UCiagkMnba3rgPeyUqeSmV の db "picks")
- 新ゲーム25: 隕石よけ/矢の雨/押し寄せる壁/レーザー回避/しっぽ取り/障害物ダッシュ/ものまねポーズ/一番多い色は？/配置の記憶/早押し反射/ピクセルアート再現/卵キャッチ/コイン噴水/ふくらむ風船(1/3残るまで)/まっくらスイカ割り/下がる天井/風船割り合戦/ボヨンボール/ワニの歯/コマぶつけ/旗あげゲーム(声はだいきが渡す、指示のバリエーションを考える)/お皿バランス/大玉ころがし/ロデオ/バンパーカー
- 改変10: 逆らえ！のバリエーション追加 / アスレ5コース / 村人数え: Lv4以降ほかのモブ混ぜ・時間さらにのばす / 椅子取り: 座ると消えるニセモノと逃げるイスだけ / 宝探し: 妨害の魚・プールを広く / ファイアバー: 棒を増やす / ニワトリ: キツネ乱入 / 最終ラウンド得点2倍 / 勝者の演出(試合全体の最後) / ラウンド結果の画面
- 作る順: v5 = 改変(アスレ以外)+ モデル不要の7ゲーム。v6 以降 = 残り(モデルが要るもの、アスレ5コース)。
