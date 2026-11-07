scoreboard players set sound_navi game 1

execute if score selectgame game matches 1 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§eダイヤモンドブロックに乗ることで、浮遊の効果を得られます！"}]}
execute if score selectgame game matches 2 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§e熱帯魚でプレイヤーを殴ると相手を遠くへ飛ばすことができます。"}]}
execute if score selectgame game matches 3 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§e中央のディスプレイの数字より、次に出る数字が高いか低いかを選びましょう。赤が高い、青が低いです。"}]}
execute if score selectgame game matches 4 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§eTNTが歩いたところを中心に崩れていきます。奈落に落ちないように走り続けましょう。"}]}
execute if score selectgame game matches 5 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§eネザー化した場所に行くとダメージを受けるので注意。"}]}

# 6はスキップ(TNT TAG, 複雑なため)

execute if score selectgame game matches 7 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§e鉱石を右クリック もしくは 短くタップ することで、武器をアップグレードできます。"}]}
execute if score selectgame game matches 8 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§e黄緑色のコンクリートブロックに着地しましょう。"}]}
execute if score selectgame game matches 9 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§e命令と逆のことをしましょう。"}]}
execute if score selectgame game matches 10 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§e上をみて避けましょう！"}]}

execute if score selectgame game matches 11 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§eスロットにあるアイテム(投票)を右クリック もしくは 短くタップ して、消すブロックを選べます。"}]}
execute if score selectgame game matches 12 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§eTNTが毎度落ちてくるので、死なないように避けましょう。"}]}
execute if score selectgame game matches 13 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§e制限時間(経験値と同期)内にアスレチックをクリアしましょう。"}]}
execute if score selectgame game matches 14 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§eスロットにあるアイテム(投票)を右クリック もしくは 短くタップ して、競争に勝つであろうどうぶつを予想できます。"}]}
execute if score selectgame game matches 15 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§e画面下部に消すブロックが表示されます。"}]}
execute if score selectgame game matches 16 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§e画面下部に表示された鉱石をツルハシを使って掘りましょう。"}]}
execute if score selectgame game matches 17 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§eマグマに落下すると死亡してしまいます。落ちないように気を付けて！"}]}
execute if score selectgame game matches 18 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§eハサミで床に穴をあけれます。"}]}
execute if score selectgame game matches 19 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§e雪玉を投げるとブロックの色が自陣営の色に変わります！"}]}
execute if score selectgame game matches 20 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§e画面下部に表示されたアイテムを素早くクラフトしましょう。原木を木材にして、木材を棒にして...という手順が必要なこともありますよ。"}]}
execute if score selectgame game matches 21 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§eウォーデンがいる部屋から出口を見つけて脱出しましょう。"}]}
execute if score selectgame game matches 22 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§e雪玉や釣竿を使ってプレイヤーをフィールドから落そう。"}]}
execute if score selectgame game matches 23 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§eマップ内の村人の数を数えてください。"}]}
execute if score selectgame game matches 24 run tellraw @a[tag=navi] {"rawtext":[{"text":"§l§f[§b!§f] §r§eモンスターを一番倒せたら勝ちです。"}]}

scoreboard players set navi_message game 1