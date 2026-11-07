tag @a remove playing

execute as @a at @s run playsound random.orb @s
clear @a
effect @a clear
effect @a saturation 1 255 true
effect @a instant_health 1 255 true
gamemode 2 @a
tag @a remove goal
tag @a remove died
tag @a remove lose
xp -1000L @a

inputpermission set @a movement enabled

tag @a remove game3_win
tag @a remove game6_oni
tag @a remove game13_c1
tag @a remove game13_c2
tag @a remove game19_white
tag @a remove game21_goala

scoreboard players set stopgame game 1

scoreboard players set game1_yuuyo_time game 0
scoreboard players set game2_1 game 0
scoreboard players set game2_time_s game 3
scoreboard players set game2_time_s2 game 0
scoreboard players set game12_random game 0

scoreboard players set game11_red_a game 0
scoreboard players set game11_green_a game 0
scoreboard players set game11_blue_a game 0
scoreboard players set game11_yellow_a game 0
scoreboard players set game11_white_a game 0
scoreboard players set game11_purple_a game 0

gamerule fallDamage false
gamerule pvp false
gamerule naturalRegeneration true

fill -24 0 50 25 0 -49 black_concrete

kill @e[type=!player,type=!armor_stand,type=!painting]

tp @a 48 13 1.0 facing 0 13 1.0
spawnpoint @a 47.99 13.00 0.92

fill -24 0 50 25 0 -49 black_concrete
fill -24 1 50 25 5 -49 air
fill -24 10 50 25 5 -49 air
fill -24 15 50 25 10 -49 air
fill -24 15 50 25 20 -49 air
fill -24 20 50 25 25 -49 air
fill -24 25 50 25 30 -49 air
fill -24 30 50 25 35 -49 air
fill -24 35 50 25 40 -49 air
fill -24 40 50 25 45 -49 air
fill -24 45 50 25 50 -49 air
fill -24 50 50 25 55 -49 air
fill -24 56 50 25 58 -49 air

scoreboard players set game_next_ready game 0
scoreboard players set playing game 0
scoreboard players set player game 0
scoreboard players set round game 0

scoreboard players set game15_timer game 0
scoreboard players set game15_timer2_s game 0
scoreboard players set game15_timer2_s2 game 0
scoreboard players set game15_block game 0
scoreboard players set game15_s game 0
scoreboard players set game15_round game 0

scoreboard players set game_ready game 0

scoreboard objectives remove point 
scoreboard objectives add point dummy
scoreboard objectives setdisplay sidebar point

structure load mmg -84 31 -31 180_degrees
structure load mmg 84 31 -31

setblock 84 32 -31 air
setblock -83 32 32 air

fill -6 -14 6 -34 -12 -32 air replace redstone_block
fill 9 -14 10 47 -8 62 air replace redstone_block

setblock 5 -14 11 air
