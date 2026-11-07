scoreboard players add round game 1

execute if score round-auto setting matches 1 if score round game = m2 game run setblock -2 -14 20 redstone_block
execute if score round-auto setting matches 1 if score round game = m3 game run setblock -2 -14 20 redstone_block
execute if score round-auto setting matches 1 if score round game = m4 game run setblock -2 -14 20 redstone_block
execute if score round-auto setting matches 1 if score round game = m5 game run setblock -2 -14 20 redstone_block

execute if block -2 -14 20 air if score round setting > round game run setblock -4 -14 20 redstone_block
execute if block -2 -14 20 air if score round setting = round game run setblock -4 -14 20 redstone_block

execute if score round setting < round game run setblock -6 -14 20 redstone_block

scoreboard players set game_next_ready game 0
scoreboard players set game_ready game 0