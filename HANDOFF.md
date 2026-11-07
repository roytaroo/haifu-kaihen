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
- ビルド: `python3 tools/build_mmg.py v<番号>` → `dist/MMG-v<番号>.mcworld`(dist は git に入れない。毎回番号を上げる)。最新 v3。
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
- 次の候補: 記録系を既存ゲーム(アスレのタイム等)にも広げる。
