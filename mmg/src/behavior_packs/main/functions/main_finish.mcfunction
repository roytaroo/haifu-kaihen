tellraw @a {"rawtext":[{"text":"§cゲーム終了！"}]}

scoreboard players set ranking game 1
playsound random.levelup @a ~ ~ ~ 1 0.5
setblock -10 -14 16 redstone_block
