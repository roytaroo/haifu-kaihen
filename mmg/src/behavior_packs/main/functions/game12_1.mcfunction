execute if score level game matches 1 run scoreboard players set game12_timer game 10
execute if score level game matches 2 run scoreboard players set game12_timer game 15
execute if score level game matches 3 run scoreboard players set game12_timer game 20
execute if score level game matches 4 run scoreboard players set game12_timer game 25
execute if score level game matches 5 run scoreboard players set game12_timer game 30

execute if score level game matches 1 run xp 10L @a
execute if score level game matches 2 run xp 15L @a
execute if score level game matches 3 run xp 20L @a
execute if score level game matches 4 run xp 25L @a
execute if score level game matches 5 run xp 30L @a

tp @a[tag=playing] 0 7 0

setblock 15 -14 42 redstone_block

scoreboard players set game12_random game 1