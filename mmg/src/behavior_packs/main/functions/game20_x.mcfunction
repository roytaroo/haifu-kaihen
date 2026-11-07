execute if score level game matches 1 run scoreboard players set game20_roundx game 3
execute if score level game matches 2 run scoreboard players set game20_roundx game 4
execute if score level game matches 3 run scoreboard players set game20_roundx game 5
execute if score level game matches 4 run scoreboard players set game20_roundx game 6
execute if score level game matches 5 run scoreboard players set game20_roundx game 7

scoreboard players set game20_timer_1 game 5

setblock 47 -14 39 redstone_block
setblock 45 -14 42 redstone_block

tp @a[tag=playing] 0 8 0