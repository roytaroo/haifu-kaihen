execute if score level game matches 1 if score game3_round game > constant3 constant run setblock 17 -14 20 redstone_block
execute if score level game matches 2 if score game3_round game > constant4 constant run setblock 17 -14 20 redstone_block
execute if score level game matches 3 if score game3_round game > constant5 constant run setblock 17 -14 20 redstone_block
execute if score level game matches 4 if score game3_round game > constant6 constant run setblock 17 -14 20 redstone_block
execute if score level game matches 5 if score game3_round game > constant7 constant run setblock 17 -14 20 redstone_block

execute as @a[tag=playing,tag=!lose] at @s run scoreboard players set game3_players game 1
execute if score game3_players game matches 1 run scoreboard players set game3_aa game 1
execute unless score game3_players game matches 1 run setblock 17 -14 20 redstone_block

execute if score game3_aa game matches 1 if score level game matches 1 if score game3_round game < constant4 constant run setblock 17 -14 14 redstone_block
execute if score game3_aa game matches 1 if score level game matches 2 if score game3_round game < constant5 constant run setblock 17 -14 14 redstone_block
execute if score game3_aa game matches 1 if score level game matches 3 if score game3_round game < constant6 constant run setblock 17 -14 14 redstone_block
execute if score game3_aa game matches 1 if score level game matches 4 if score game3_round game < constant7 constant run setblock 17 -14 14 redstone_block
execute if score game3_aa game matches 1 if score level game matches 5 if score game3_round game < constant8 constant run setblock 17 -14 14 redstone_block

setblock 17 -14 17 air

tag @a remove game3_low
tag @a remove game3_high
tag @a remove game3_win

scoreboard players set game3_players game 0
scoreboard players set game3_aa game 0