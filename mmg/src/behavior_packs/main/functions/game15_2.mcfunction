scoreboard players add game15_round game 0
scoreboard players add game15_round game 1

execute as @a[tag=playing,tag=!died] at @s run scoreboard players add game15_user game 1
execute if score game15_user game matches ..1 run setblock 25 -14 51 redstone_block

execute if score level game matches 1 if score game15_round game > constant3 constant run setblock 25 -14 51 redstone_block
execute if score level game matches 2 if score game15_round game > constant4 constant run setblock 25 -14 51 redstone_block
execute if score level game matches 3 if score game15_round game > constant5 constant run setblock 25 -14 51 redstone_block
execute if score level game matches 4 if score game15_round game > constant6 constant run setblock 25 -14 51 redstone_block
execute if score level game matches 5 if score game15_round game > constant7 constant run setblock 25 -14 51 redstone_block

execute unless score game15_user game matches ..1 if score level game matches 1 if score game15_round game < constant4 constant run setblock 27 -14 45 redstone_block
execute unless score game15_user game matches ..1 if score level game matches 2 if score game15_round game < constant5 constant run setblock 27 -14 45 redstone_block
execute unless score game15_user game matches ..1 if score level game matches 3 if score game15_round game < constant6 constant run setblock 27 -14 45 redstone_block
execute unless score game15_user game matches ..1 if score level game matches 4 if score game15_round game < constant7 constant run setblock 27 -14 45 redstone_block
execute unless score game15_user game matches ..1 if score level game matches 5 if score game15_round game < constant8 constant run setblock 27 -14 45 redstone_block

execute if score level game matches 1 if score game15_round game < constant4 constant run scoreboard players set game15_timer2_s game 5
execute if score level game matches 2 if score game15_round game < constant5 constant run scoreboard players set game15_timer2_s game 4
execute if score level game matches 3 if score game15_round game < constant6 constant run scoreboard players set game15_timer2_s game 3
execute if score level game matches 4 if score game15_round game < constant7 constant run scoreboard players set game15_timer2_s game 2
execute if score level game matches 5 if score game15_round game < constant8 constant run scoreboard players set game15_timer2_s game 1

setblock 25 -14 48 air

scoreboard players random game15_block game 1 8

setblock 25 -14 45 air