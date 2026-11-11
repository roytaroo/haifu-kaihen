
execute if score testmode setting matches 1 run scoreboard players set selectgame game 2

execute if score selectgame game matches 1 run setblock -7 -14 6 redstone_block
execute if score selectgame game matches 2 run setblock -7 -14 2 redstone_block
execute if score selectgame game matches 3 run setblock -7 -14 -2 redstone_block
execute if score selectgame game matches 4 run setblock -7 -14 -6 redstone_block
execute if score selectgame game matches 5 run setblock -7 -14 -10 redstone_block
execute if score selectgame game matches 6 run setblock -7 -14 -14 redstone_block
execute if score selectgame game matches 7 run setblock -7 -14 -18 redstone_block
execute if score selectgame game matches 8 run setblock -7 -14 -22 redstone_block
execute if score selectgame game matches 9 run setblock -7 -14 -26 redstone_block
execute if score selectgame game matches 10 run setblock -7 -14 -30 redstone_block
execute if score selectgame game matches 11 run setblock -23 -14 5 redstone_block
execute if score selectgame game matches 12 run setblock -23 -14 2 redstone_block
execute if score selectgame game matches 13 run setblock -23 -14 -2 redstone_block
execute if score selectgame game matches 14 run setblock -23 -14 -6 redstone_block
execute if score selectgame game matches 15 run setblock -23 -14 -10 redstone_block
execute if score selectgame game matches 16 run setblock -23 -14 -14 redstone_block
execute if score selectgame game matches 17 run setblock -23 -14 -18 redstone_block
execute if score selectgame game matches 18 run setblock -23 -14 -22 redstone_block
execute if score selectgame game matches 19 run setblock -23 -14 -26 redstone_block
execute if score selectgame game matches 20 run setblock -23 -14 -30 redstone_block
execute if score selectgame game matches 21 run setblock -39 -14 6 redstone_block
execute if score selectgame game matches 22 run setblock -39 -14 2 redstone_block
execute if score selectgame game matches 23 run setblock -39 -14 -2 redstone_block
execute if score selectgame game matches 24 run setblock -39 -14 -6 redstone_block
execute if score selectgame game matches 25.. run scriptevent mmgplus:prep

tellraw @a {"rawtext":[{"text":"ラウンド "},{"score":{"name":"round","objective":"game"}},{"text":" / "},{"score":{"name":"round","objective":"setting"}},{"text":""}]}

execute if score selectgame game matches 1 run tellraw @a {"rawtext":[{"text":"次のゲーム: §6Escape Lava\n§r上がってくるマグマから逃げきれ！10階層ある4x4の迷路から、ダイヤモンドブロックを見つけて上へ上がろう！\n§7制限時間: マグマが最上階に到達するまで"}]}
execute if score selectgame game matches 2 run tellraw @a {"rawtext":[{"text":"次のゲーム: §6熱帯魚相撲\n§r32x32のフィールドで、熱帯魚で相手をノックバックして落とそう！フィールドはだんだん狭くなっていきます！\n§7制限時間: 30秒"}]}
execute if score selectgame game matches 3 run tellraw @a {"rawtext":[{"text":"次のゲーム: §cHigh §fand §9Low\n§r1~9の数字がランダムに出てきます。その数字よりも、次に出てくる数字が大きくなるか小さくなるかを当てるゲームです！\n§7制限時間: 3ラウンド終了したら§8(*レベルによって変動します)"}]}
execute if score selectgame game matches 4 run tellraw @a {"rawtext":[{"text":"次のゲーム: §cTNT RUN\n§r5秒後に、TNTが崩れていきます。奈落に落ちないように逃げ回ろう！\n§7制限時間: レベル1なら30秒、レベル+1ごとに +10秒"}]}
execute if score selectgame game matches 5 run tellraw @a {"rawtext":[{"text":"次のゲーム: §4Adventure PVP\n§r勝利を目指して、みんなを倒しまくろう！フィールドはだんだん狭くなっていきます。\n§7制限時間: 90秒"}]}
execute if score selectgame game matches 6 run tellraw @a {"rawtext":[{"text":"次のゲーム: §cTNT TAG\n§rTNTは一定時間後に爆発します。鬼に捕まらないように、プレイヤーは逃げ回ろう！鬼側はプレイヤーを追いかけて、殴ることで鬼が変わります。§r\n§7制限時間: TNTが5回爆発するまで§8(*人数によって変動します)"}]}
execute if score selectgame game matches 7 run tellraw @a {"rawtext":[{"text":"次のゲーム: §aDrop §cPVP\n§r床が 緑→黄→橙→赤 の順番に壊れていきます！落下しないように、気を付けてバトルをしましょう。また、アイテムがランダムな位置に召喚されます。アイテムを右クリックして強化しましょう！§r\n§7制限時間: 180秒"}]}
execute if score selectgame game matches 8 run tellraw @a {"rawtext":[{"text":"次のゲーム: §e降下デスマッチ\n§r低速落下のエフェクトがつきながら高いところから落下します。緑色のブロックに着地するとゴール熱帯魚を使い、他のプレイヤーの着地を妨害しよう！§r\n§7制限時間: 3ラウンド終了したら"}]}
execute if score selectgame game matches 9 run tellraw @a {"rawtext":[{"text":"次のゲーム: §b逆らえ！\n§r命令が出されるので、出された命令に逆らいましょう。§r\n§7制限時間: 3ラウンド終了したら§8(*レベルによって変動します)"}]}
execute if score selectgame game matches 10 run tellraw @a {"rawtext":[{"text":"次のゲーム: §e金床避け\n§r空から金床が落ちてきます。金床に当たらないようによけましょう！§r\n§7制限時間: 10秒§8(*レベルによって変動します)"}]}
execute if score selectgame game matches 11 run tellraw @a {"rawtext":[{"text":"次のゲーム: §e読みぶろぱ\n§r投票で消したいブロックを選びます。みんなが選ぶであろうブロックを投票して、プレイヤーを落としましょう！§r\n§7制限時間: 1ラウンド§8(*レベルによって変動します)"}]}
execute if score selectgame game matches 12 run tellraw @a {"rawtext":[{"text":"次のゲーム: §cTNT避け\n§r空から落ちてくるTNTを避けよう！§r\n§7制限時間: 10秒§8(*レベルによって変動します)"}]}
execute if score selectgame game matches 13 run tellraw @a {"rawtext":[{"text":"次のゲーム: §aアスレチック\n§r100mもの長さのアスレチックをクリアしよう§r\n§7制限時間: 70秒§8(*レベルによって変動します)"}]}
execute if score selectgame game matches 14 run tellraw @a {"rawtext":[{"text":"次のゲーム: §aどうぶつリレー\n§r90mもの長さをどうぶつが走ります！勝ちそうなどうぶつを投票しましょう。§r\n§7制限時間: どうぶつがゴールするまで"}]}
execute if score selectgame game matches 15 run tellraw @a {"rawtext":[{"text":"次のゲーム: §dBlock Party\n§r指定されたブロック以外が消滅します！落ちないように逃げ回ろう！§r\n§7制限時間: 3ラウンド終了したら§8(*レベルによって変動します)"}]}
execute if score selectgame game matches 16 run tellraw @a {"rawtext":[{"text":"次のゲーム: §b鉱石バトル\n§r指定された鉱石を掘りましょう！§r\n§7制限時間: 30秒§8(*レベルによって変動します)"}]}
execute if score selectgame game matches 17 run tellraw @a {"rawtext":[{"text":"次のゲーム: §b崩れる床で生き延びろ\n§r床が 黄→橙→赤→マグマ の順番に壊れていきます！マグマに落下しないように、気を付けましょう！§r\n§7制限時間: 15秒§8(*レベルによって変動します)"}]}
execute if score selectgame game matches 18 run tellraw @a {"rawtext":[{"text":"次のゲーム: §d穴落とし\n§r床に穴をあけて、プレイヤーを落とそう！自分が落ちないように慎重にブロックを破壊しましょう。§r\n§7制限時間: 15秒§8(*レベルによって変動します)"}]}
execute if score selectgame game matches 19 run tellraw @a {"rawtext":[{"text":"次のゲーム: §b色塗りバトル\n§r白と黒チームにほぼ均等に分かれます。自分の陣地の色に雪玉を投げて変えよう！最終的にフィールド内に最も色が多いチームの勝利です。§r\n§7制限時間: 30秒"}]}
execute if score selectgame game matches 20 run tellraw @a {"rawtext":[{"text":"次のゲーム: §aクラフトマスター\n§r制限時間内に指定されたアイテムをすばやくクラフトしよう！§r\n§7制限時間: 3ラウンド, 1ラウンド20秒§8(*レベルによって変動します)"}]}
execute if score selectgame game matches 21 run tellraw @a {"rawtext":[{"text":"次のゲーム: §cWarden Escape\n§rウォーデンが追いかけてきます。脱出口を探して脱出しよう！§r\n§7制限時間: 120秒"}]}
execute if score selectgame game matches 22 run tellraw @a {"rawtext":[{"text":"次のゲーム: §6マグマノックバック\n§r氷のフィールドの上でプレイヤーを落しあおう！§r\n§7制限時間: 15秒 §8(*レベルによって変動します)"}]}
execute if score selectgame game matches 23 run tellraw @a {"rawtext":[{"text":"次のゲーム: §6村人数え\n§r村人の数を数えよう！ミスをしないように気をつけて。§r\n§7制限時間: 25秒 §8(*レベルによって変動します)"}]}
execute if score selectgame game matches 24 run tellraw @a {"rawtext":[{"text":"次のゲーム: §aモンスターバトル\n§rモンスターを倒そう！最もモンスターを倒した者が勝利。§r\n§7制限時間: 60秒"}]}
execute if score selectgame game matches 25 run tellraw @a {"rawtext":[{"text":"次のゲーム: §b計算早押し\n§r出された計算の答えを、だれよりも早く選ぼう！正解数がいちばん多い人が勝利。§r\n§7全5問"}]}
execute if score selectgame game matches 26 run tellraw @a {"rawtext":[{"text":"次のゲーム: §d色の記憶\n§r5色の床と柱が光った順番をおぼえて、同じ順に床をふもう！まちがえたら脱落。最後まで残った人が勝利。"}]}
execute if score selectgame game matches 27 run tellraw @a {"rawtext":[{"text":"次のゲーム: §e椅子取りゲーム\n§r曲が止まったら、出てきたイスに座ろう！乗れなかったら脱落。最後まで残った人が勝利。"}]}
execute if score selectgame game matches 28 run tellraw @a {"rawtext":[{"text":"次のゲーム: §6宝探しプール\n§r水の中の宝を泳いで集めよう！金1点・ダイヤ3点・エメラルド5点。点数がいちばん多い人が勝利。§r\n§7制限時間: 60秒"}]}
execute if score selectgame game matches 29 run tellraw @a {"rawtext":[{"text":"次のゲーム: §6ファイアバー\n§r回ってくる火の玉の棒をジャンプでよけよう！当たったら脱落。最後まで残った人が勝利。"}]}
execute if score selectgame game matches 30 run tellraw @a {"rawtext":[{"text":"次のゲーム: §bボートレース\n§r氷の一本道をボートでまっすぐゴールへ！1〜3位がポイント。"}]}
execute if score selectgame game matches 31 run tellraw @a {"rawtext":[{"text":"次のゲーム: §eピッタリ止め\n§r目標の秒数ぴったりで「ストップ！」を押そう。いちばん近い人が勝利。"}]}
execute if score selectgame game matches 32 run tellraw @a {"rawtext":[{"text":"次のゲーム: §aニワトリ集め\n§rたねを持ってニワトリを自分の囲いに連れていこう！最後に囲いの中にいる数で勝負。§r\n§7制限時間: 60秒"}]}
execute if score selectgame game matches 33 run tellraw @a {"rawtext":[{"text":"次のゲーム: §e一番多い色は？\n§r前の壁に一瞬だけ色のモザイクが出る。一番多かった色を答えよう！全5問。"}]}
execute if score selectgame game matches 34 run tellraw @a {"rawtext":[{"text":"次のゲーム: §a早押し反射\n§r前の壁が緑になった瞬間にしゃがもう！早すぎるとフライング。全5ラウンド。"}]}
execute if score selectgame game matches 35 run tellraw @a {"rawtext":[{"text":"次のゲーム: §c矢の雨\n§r四方の壁から飛んでくる矢をよけよう！3回当たったら脱落。"}]}
execute if score selectgame game matches 36 run tellraw @a {"rawtext":[{"text":"次のゲーム: §c隕石よけ\n§r赤い印の所に隕石が落ちてくる。印から逃げよう！"}]}
execute if score selectgame game matches 37 run tellraw @a {"rawtext":[{"text":"次のゲーム: §6押し寄せる壁\n§r穴のあいた壁が迫ってくる。穴の位置に立ってすり抜けよう！"}]}
execute if score selectgame game matches 38 run tellraw @a {"rawtext":[{"text":"次のゲーム: §b障害物ダッシュ\n§r動く壁とハードルをこえてゴールへ！当たるとチェックポイントに戻る。1〜3位がポイント。"}]}
execute if score selectgame game matches 39 run tellraw @a {"rawtext":[{"text":"次のゲーム: §d配置の記憶\n§r自分のマスで光ったところを覚えて、消えたあと同じマスをふもう！全4ラウンド。"}]}

scoreboard players set game_next_ready game 0
scoreboard players set game_ready game 0
setblock 5 -14 11 redstone_block

execute if score selectgame game matches 1 run tp @a[tag=playing] 0 3 20
execute if score selectgame game matches 5 run tp @a[tag=playing] 0 3 30
execute if score selectgame game matches 6 run tp @a[tag=playing] 0 3 30
execute if score selectgame game matches 14 run tp @a[tag=playing] 0 5 0
execute if score selectgame game matches 21 run tp @a[tag=playing] 0 5 -25
execute if score selectgame game matches 22 run tp @a[tag=playing] 0 5 -25
execute if score selectgame game matches 23 run tp @a[tag=playing] 0 5 -25

effect @a clear

scoreboard players set game2_1 game 0