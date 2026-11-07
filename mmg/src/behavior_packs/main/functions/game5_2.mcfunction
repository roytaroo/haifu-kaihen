execute as @e[name=game5_a] at @s run fill ~ 5 -24 ~ 1 25 stripped_mangrove_log replace oak_log
execute as @e[name=game5_a] at @s run fill ~ 5 -24 ~ 1 25 crimson_planks replace oak_planks
execute as @e[name=game5_a] at @s run fill ~ 5 -24 ~ 1 25 nether_wart_block replace grass
execute as @e[name=game5_a] at @s run fill ~ 5 -24 ~ 1 25 structure_void replace light_block_15

execute as @e[name=game5_b] at @s run fill -24 5 ~ 25 1 ~ stripped_mangrove_log replace oak_log
execute as @e[name=game5_b] at @s run fill -24 5 ~ 25 1 ~ crimson_planks replace oak_planks
execute as @e[name=game5_b] at @s run fill -24 5 ~ 25 1 ~ nether_wart_block replace grass
execute as @e[name=game5_b] at @s run fill -24 5 ~ 25 1 ~ structure_void replace light_block_15

execute as @e[name=game5_c] at @s run fill ~ 5 -24 ~ 1 25 stripped_mangrove_log replace oak_log
execute as @e[name=game5_c] at @s run fill ~ 5 -24 ~ 1 25 crimson_planks replace oak_planks
execute as @e[name=game5_c] at @s run fill ~ 5 -24 ~ 1 25 nether_wart_block replace grass
execute as @e[name=game5_c] at @s run fill ~ 5 -24 ~ 1 25 structure_void replace light_block_15

execute as @e[name=game5_d] at @s run fill -24 5 ~ 25 1 ~ stripped_mangrove_log replace oak_log
execute as @e[name=game5_d] at @s run fill -24 5 ~ 25 1 ~ crimson_planks replace oak_planks
execute as @e[name=game5_d] at @s run fill -24 5 ~ 25 1 ~ nether_wart_block replace grass
execute as @e[name=game5_d] at @s run fill -24 5 ~ 25 1 ~ structure_void replace light_block_15

execute as @e[name=game5_a] at @s run tp @s ~1 ~ ~
execute as @e[name=game5_b] at @s run tp @s ~ ~ ~-1
execute as @e[name=game5_c] at @s run tp @s ~-1 ~ ~
execute as @e[name=game5_d] at @s run tp @s ~ ~ ~1

execute if score level game matches 1 run scoreboard players set game5_time_s game 8
execute if score level game matches 2 run scoreboard players set game5_time_s game 7
execute if score level game matches 3 run scoreboard players set game5_time_s game 6
execute if score level game matches 4 run scoreboard players set game5_time_s game 5
execute if score level game matches 5 run scoreboard players set game5_time_s game 4