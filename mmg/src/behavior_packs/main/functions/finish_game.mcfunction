tp @a[tag=playing] 0 1 0

execute if score selectgame game matches 1 run tp @a[tag=playing] 0 2 -19
execute if score selectgame game matches 1 run scoreboard players add @a[tag=playing,tag=goal] point 1
execute if score selectgame game matches 1 run tellraw @a[tag=playing,tag=!goal] {"rawtext":[{"text":"§cゴールできませんでした..."}]}
execute if score selectgame game matches 1 run tellraw @a[tag=playing,tag=goal] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 1 run tag @a[tag=playing,tag=goal] add game_finish_a
execute if score selectgame game matches 1 run setblock -14 -14 6 redstone_block
execute if score selectgame game matches 1 run tp @e[name=game1_lava] 0 -13 0

execute if score selectgame game matches 2 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 2 run scoreboard players add @a[tag=playing,tag=!died] point 1
execute if score selectgame game matches 2 run tellraw @a[tag=playing,tag=died] {"rawtext":[{"text":"§c死んでしまいました..."}]}
execute if score selectgame game matches 2 run tellraw @a[tag=playing,tag=!died] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 2 run tag @a[tag=playing,tag=!died] add game_finish_a
execute if score selectgame game matches 2 run setblock -14 -14 2 redstone_block

execute if score selectgame game matches 3 run tp @a[tag=playing] 0 2 -19
execute if score selectgame game matches 3 run scoreboard players add @a[tag=playing,tag=!lose] point 1
execute if score selectgame game matches 3 run tellraw @a[tag=playing,tag=lose] {"rawtext":[{"text":"§c予想が当たりませんでした..."}]}
execute if score selectgame game matches 3 run tellraw @a[tag=playing,tag=!lose] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 3 run tag @a[tag=playing,tag=!lose] add game_finish_a
execute if score selectgame game matches 3 run setblock -14 -14 -2 redstone_block

execute if score selectgame game matches 4 run tp @a[tag=playing] 0 2 -19
execute if score selectgame game matches 4 run scoreboard players add @a[tag=playing,tag=!died] point 1
execute if score selectgame game matches 4 run tellraw @a[tag=playing,tag=died] {"rawtext":[{"text":"§c落下してしまいました..."}]}
execute if score selectgame game matches 4 run tellraw @a[tag=playing,tag=!died] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 4 run tag @a[tag=playing,tag=!died] add game_finish_a
execute if score selectgame game matches 4 run setblock -14 -14 -6 redstone_block

execute if score selectgame game matches 5 run tp @a[tag=playing] 0 2 30
execute if score selectgame game matches 5 run scoreboard players add @a[tag=playing,tag=!died] point 1
execute if score selectgame game matches 5 run tellraw @a[tag=playing,tag=died] {"rawtext":[{"text":"§c死んでしまいました..."}]}
execute if score selectgame game matches 5 run tellraw @a[tag=playing,tag=!died] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 5 run tag @a[tag=playing,tag=!died] add game_finish_a
execute if score selectgame game matches 5 run setblock -14 -14 -10 redstone_block

execute if score selectgame game matches 6 run tp @a[tag=playing] 0 2 30
execute if score selectgame game matches 6 run scoreboard players add @a[tag=playing,tag=!died] point 1
execute if score selectgame game matches 6 run tellraw @a[tag=playing,tag=died] {"rawtext":[{"text":"§c死んでしまいました..."}]}
execute if score selectgame game matches 6 run tellraw @a[tag=playing,tag=!died] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 6 run tag @a[tag=playing,tag=!died] add game_finish_a
execute if score selectgame game matches 6 run setblock -14 -14 -14 redstone_block

execute if score selectgame game matches 7 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 7 run scoreboard players add @a[tag=playing,tag=!died] point 1
execute if score selectgame game matches 7 run tellraw @a[tag=playing,tag=died] {"rawtext":[{"text":"§c死んでしまいました..."}]}
execute if score selectgame game matches 7 run tellraw @a[tag=playing,tag=!died] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 7 run tag @a[tag=playing,tag=!died] add game_finish_a
execute if score selectgame game matches 7 run setblock -14 -14 -18 redstone_block

execute if score selectgame game matches 8 run tp @a[tag=playing] 0 2 40
execute if score selectgame game matches 8 run scoreboard players add @a[tag=playing,tag=!died] point 1
execute if score selectgame game matches 8 run tellraw @a[tag=playing,tag=died] {"rawtext":[{"text":"§c着地できませんでした..."}]}
execute if score selectgame game matches 8 run tellraw @a[tag=playing,tag=!died] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 8 run tag @a[tag=playing,tag=!died] add game_finish_a
execute if score selectgame game matches 8 run setblock -14 -14 -22 redstone_block

execute if score selectgame game matches 9 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 9 run scoreboard players add @a[tag=playing,tag=!died] point 1
execute if score selectgame game matches 9 run tellraw @a[tag=playing,tag=died] {"rawtext":[{"text":"§c逆らいきれませんでした..."}]}
execute if score selectgame game matches 9 run tellraw @a[tag=playing,tag=!died] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 9 run tag @a[tag=playing,tag=!died] add game_finish_a
execute if score selectgame game matches 9 run setblock -14 -14 -26 redstone_block

execute if score selectgame game matches 10 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 10 run scoreboard players add @a[tag=playing,tag=!died] point 1
execute if score selectgame game matches 10 run tellraw @a[tag=playing,tag=died] {"rawtext":[{"text":"§c押しつぶされました..."}]}
execute if score selectgame game matches 10 run tellraw @a[tag=playing,tag=!died] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 10 run tag @a[tag=playing,tag=!died] add game_finish_a
execute if score selectgame game matches 10 run setblock -14 -14 -30 redstone_block

execute if score selectgame game matches 11 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 11 run scoreboard players add @a[tag=playing,tag=!died] point 1
execute if score selectgame game matches 11 run tellraw @a[tag=playing,tag=died] {"rawtext":[{"text":"§c予測が当たりませんでした..."}]}
execute if score selectgame game matches 11 run tellraw @a[tag=playing,tag=!died] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 11 run tag @a[tag=playing,tag=!died] add game_finish_a
execute if score selectgame game matches 11 run setblock -30 -14 6 redstone_block

execute if score selectgame game matches 12 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 12 run scoreboard players add @a[tag=playing,tag=!died] point 1
execute if score selectgame game matches 12 run tellraw @a[tag=playing,tag=died] {"rawtext":[{"text":"§cTNTを避けれませんでした..."}]}
execute if score selectgame game matches 12 run tellraw @a[tag=playing,tag=!died] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 12 run tag @a[tag=playing,tag=!died] add game_finish_a
execute if score selectgame game matches 12 run setblock -30 -14 2 redstone_block

execute if score selectgame game matches 13 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 13 run scoreboard players add @a[tag=playing,tag=goal] point 1
execute if score selectgame game matches 13 run tellraw @a[tag=playing,tag=!goal] {"rawtext":[{"text":"§cクリアできませんでした..."}]}
execute if score selectgame game matches 13 run tellraw @a[tag=playing,tag=goal] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 13 run tag @a[tag=playing,tag=goal] add game_finish_a
execute if score selectgame game matches 13 run setblock -30 -14 -2 redstone_block

execute if score selectgame game matches 14 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 14 run scoreboard players add @a[tag=playing,tag=win] point 1
execute if score selectgame game matches 14 run tellraw @a[tag=playing,tag=!win] {"rawtext":[{"text":"§c予想が当たりませんでした..."}]}
execute if score selectgame game matches 14 run tellraw @a[tag=playing,tag=win] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 14 run tag @a[tag=playing,tag=win] add game_finish_a
execute if score selectgame game matches 14 run setblock -30 -14 -6 redstone_block

execute if score selectgame game matches 15 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 15 run scoreboard players add @a[tag=playing,tag=!died] point 1
execute if score selectgame game matches 15 run tellraw @a[tag=playing,tag=died] {"rawtext":[{"text":"§c落ちてしまいました..."}]}
execute if score selectgame game matches 15 run tellraw @a[tag=playing,tag=!died] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 15 run tag @a[tag=playing,tag=!died] add game_finish_a
execute if score selectgame game matches 15 run setblock -30 -14 -10 redstone_block

execute if score selectgame game matches 16 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 16 run scoreboard players add @a[tag=playing,tag=win] point 1
execute if score selectgame game matches 16 run tellraw @a[tag=playing,tag=!win] {"rawtext":[{"text":"§c鉱石を掘れませんでした..."}]}
execute if score selectgame game matches 16 run tellraw @a[tag=playing,tag=win] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 16 run tag @a[tag=playing,tag=win] add game_finish_a
execute if score selectgame game matches 16 run setblock -30 -14 -14 redstone_block

execute if score selectgame game matches 17 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 17 run scoreboard players add @a[tag=playing,tag=!died] point 1
execute if score selectgame game matches 17 run tellraw @a[tag=playing,tag=died] {"rawtext":[{"text":"§c死亡してしまいました..."}]}
execute if score selectgame game matches 17 run tellraw @a[tag=playing,tag=!died] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 17 run tag @a[tag=playing,tag=!died] add game_finish_a
execute if score selectgame game matches 17 run setblock -30 -14 -18 redstone_block

execute if score selectgame game matches 18 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 18 run scoreboard players add @a[tag=playing,tag=!died] point 1
execute if score selectgame game matches 18 run tellraw @a[tag=playing,tag=died] {"rawtext":[{"text":"§c死亡してしまいました..."}]}
execute if score selectgame game matches 18 run tellraw @a[tag=playing,tag=!died] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 18 run tag @a[tag=playing,tag=!died] add game_finish_a
execute if score selectgame game matches 18 run setblock -30 -14 -22 redstone_block

execute if score selectgame game matches 19 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 19 run scoreboard players add @a[tag=playing,tag=win] point 1
execute if score selectgame game matches 19 run tellraw @a[tag=playing,tag=!win] {"rawtext":[{"text":"§c勝てませんでした..."}]}
execute if score selectgame game matches 19 run tellraw @a[tag=playing,tag=win] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 19 run tag @a[tag=playing,tag=win] add game_finish_a
execute if score selectgame game matches 19 run setblock -30 -14 -26 redstone_block

execute if score selectgame game matches 20 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 20 run scoreboard players add @a[tag=playing,tag=!died] point 1
execute if score selectgame game matches 20 run tellraw @a[tag=playing,tag=died] {"rawtext":[{"text":"§c勝てませんでした..."}]}
execute if score selectgame game matches 20 run tellraw @a[tag=playing,tag=!died] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 20 run tag @a[tag=playing,tag=!died] add game_finish_a
execute if score selectgame game matches 20 run setblock -30 -14 -30 redstone_block

execute if score selectgame game matches 21 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 21 run scoreboard players add @a[tag=playing,tag=game21_goal] point 1
execute if score selectgame game matches 21 run tellraw @a[tag=playing,tag=!game21_goal] {"rawtext":[{"text":"§cゴールできませんでした..."}]}
execute if score selectgame game matches 21 run tellraw @a[tag=playing,tag=game21_goal] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 21 run tag @a[tag=playing,tag=game21_goal] add game_finish_a
execute if score selectgame game matches 21 run setblock -46 -14 6 redstone_block

execute if score selectgame game matches 22 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 22 run scoreboard players add @a[tag=playing,tag=!died] point 1
execute if score selectgame game matches 22 run tellraw @a[tag=playing,tag=died] {"rawtext":[{"text":"§c死亡してしまいました..."}]}
execute if score selectgame game matches 22 run tellraw @a[tag=playing,tag=!died] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 22 run tag @a[tag=playing,tag=!died] add game_finish_a
execute if score selectgame game matches 22 run setblock -46 -14 2 redstone_block

execute if score selectgame game matches 23 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 23 run scoreboard players add @a[tag=playing,tag=win] point 1
execute if score selectgame game matches 23 run tellraw @a[tag=playing,tag=!win] {"rawtext":[{"text":"§c予想が当たりませんでした..."}]}
execute if score selectgame game matches 23 run tellraw @a[tag=playing,tag=win] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 23 run tag @a[tag=playing,tag=win] add game_finish_a
execute if score selectgame game matches 23 run setblock -46 -14 -2 redstone_block

execute if score selectgame game matches 24 run tp @a[tag=playing] 0 2 0
execute if score selectgame game matches 24 run scoreboard players add @a[tag=playing,tag=game24_max] point 1
execute if score selectgame game matches 24 run tellraw @a[tag=playing,tag=!game24_max] {"rawtext":[{"text":"§c勝てませんでした..."}]}
execute if score selectgame game matches 24 run tellraw @a[tag=playing,tag=game24_max] {"rawtext":[{"text":"§a1ポイント獲得！"}]}
execute if score selectgame game matches 24 run tag @a[tag=playing,tag=game24_max] add game_finish_a
execute if score selectgame game matches 24 run setblock -46 -14 -6 redstone_block

scoreboard players add @a[tag=playing] point 0

execute as @a[tag=game_finish_a] at @s run playsound note.pling @s ~ ~1 ~ 1 0.8 1

execute as @a[tag=!game_finish_a,tag=playing] at @s run playsound note.pling @s ~ ~1 ~ 1 0.6 1

tag @a remove game_finish_a

clear @a
effect @a clear
effect @a saturation 1 255 true
effect @a instant_health 1 255 true
effect @a fire_resistance 7 255 true
gamemode 2 @a[tag=playing]
tag @a remove goal
tag @a remove died
tag @a remove die
tag @a remove win
tag @a remove lose
xp -1000L @a

inputpermission set @a movement enabled
inputpermission set @a sneak enabled
inputpermission set @a camera enabled
inputpermission set @a move_backward enabled
inputpermission set @a move_forward enabled

tag @a remove game2_die
tag @a remove game3_win
tag @a remove game6_oni
tag @a remove game8_goal
tag @a remove game10_die
tag @a remove game13_c1
tag @a remove game13_c2
tag @a remove game20_win
tag @a remove game21_goal
tag @a remove game21_goala
tag @a remove game24_max

scoreboard players set stopgame game 1

scoreboard players set game1_yuuyo_time game 0
scoreboard players set game2_1 game 0
scoreboard players set game2_time_s game 3
scoreboard players set game2_time_s2 game 0

scoreboard players set game4_timer2 game 0

scoreboard players set game12_random game 0

scoreboard players set game11_red_a game 0
scoreboard players set game11_green_a game 0
scoreboard players set game11_blue_a game 0
scoreboard players set game11_yellow_a game 0
scoreboard players set game11_white_a game 0
scoreboard players set game11_purple_a game 0

scoreboard players set game15_timer game 0
scoreboard players set game15_timer2_s game 0
scoreboard players set game15_timer2_s2 game 0
scoreboard players set game15_block game 0
scoreboard players set game15_s game 0
scoreboard players set game15_round game 0

scoreboard players set game16_timer game 0

scoreboard players set game17_random game 0
scoreboard players set game17_timer game 0

scoreboard players set game19_timer_1 game 0
scoreboard players set game19_timer_2 game 0
scoreboard players set game19_s game 0
scoreboard players set game19_y_black game 0
scoreboard players set game19_y_white game 0

scoreboard players set game20_timer_1 game 0
scoreboard players set game20_timer_2 game 0
scoreboard players set game20_random_item game 0
scoreboard players set game20_players game 0
scoreboard players set game20_roundx game 0
scoreboard players set game20_round game 0

scoreboard players set game22_random game 0

scoreboard players set game23_timer game 0
scoreboard players set game23_villager game 0
scoreboard objectives remove game23_a

scoreboard players set game24_timer game 0
scoreboard players set game23_a game 0
scoreboard players set game23_b game 0
scoreboard objectives remove game24_kill

gamerule fallDamage false
gamerule pvp false
gamerule naturalRegeneration true

fill -24 0 50 25 0 -49 black_concrete

kill @e[type=!player,type=!armor_stand,type=!painting,type=!cushion]

tp @e[name=game17_random] 0 -13 -2

camera @a clear

scoreboard players set navi_message game 0