execute as @a[tag=playing,tag=!died] at @s run scoreboard players add game8_user game 1
execute if score game8_user game matches ..1 run setblock 37 -14 20 redstone_block

execute if score level game matches 1 if score game8_round game > constant3 constant run setblock 37 -14 20 redstone_block
execute unless score game8_user game matches ..1 if score level game matches 1 if score game8_round game < constant4 constant run setblock 39 -14 20 redstone_block

execute if score level game matches 2 if score game8_round game > constant4 constant run setblock 37 -14 20 redstone_block
execute unless score game8_user game matches ..1 if score level game matches 2 if score game8_round game < constant5 constant run setblock 39 -14 20 redstone_block

execute if score level game matches 3 if score game8_round game > constant5 constant run setblock 37 -14 20 redstone_block
execute unless score game8_user game matches ..1 if score level game matches 3 if score game8_round game < constant6 constant run setblock 39 -14 20 redstone_block

execute if score level game matches 4 if score game8_round game > constant6 constant run setblock 37 -14 20 redstone_block
execute unless score game8_user game matches ..1 if score level game matches 4 if score game8_round game < constant7 constant run setblock 39 -14 20 redstone_block

execute if score level game matches 5 if score game8_round game > constant7 constant run setblock 37 -14 20 redstone_block
execute unless score game8_user game matches ..1 if score level game matches 5 if score game8_round game < constant8 constant run setblock 39 -14 20 redstone_block

scoreboard players set game8_user game 0