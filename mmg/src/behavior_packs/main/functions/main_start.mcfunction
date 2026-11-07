execute if score round setting matches 5 run scoreboard players set m2 game 2
execute if score round setting matches 5 run scoreboard players set m3 game 3
execute if score round setting matches 5 run scoreboard players set m4 game 4
execute if score round setting matches 5 run scoreboard players set m5 game 5

execute if score round setting matches 10 run scoreboard players set m2 game 4
execute if score round setting matches 10 run scoreboard players set m3 game 6
execute if score round setting matches 10 run scoreboard players set m4 game 8
execute if score round setting matches 10 run scoreboard players set m5 game 10

execute if score round setting matches 15 run scoreboard players set m2 game 6
execute if score round setting matches 15 run scoreboard players set m3 game 9
execute if score round setting matches 15 run scoreboard players set m4 game 12
execute if score round setting matches 15 run scoreboard players set m5 game 15

execute if score round setting matches 20 run scoreboard players set m2 game 8
execute if score round setting matches 20 run scoreboard players set m3 game 12
execute if score round setting matches 20 run scoreboard players set m4 game 16
execute if score round setting matches 20 run scoreboard players set m5 game 20

execute if score round setting matches 25 run scoreboard players set m2 game 10
execute if score round setting matches 25 run scoreboard players set m3 game 15
execute if score round setting matches 25 run scoreboard players set m4 game 20
execute if score round setting matches 25 run scoreboard players set m5 game 25

execute if score round setting matches 30 run scoreboard players set m2 game 12
execute if score round setting matches 30 run scoreboard players set m3 game 18
execute if score round setting matches 30 run scoreboard players set m4 game 24
execute if score round setting matches 30 run scoreboard players set m5 game 30

execute if score round setting matches 35 run scoreboard players set m2 game 14
execute if score round setting matches 35 run scoreboard players set m3 game 21
execute if score round setting matches 35 run scoreboard players set m4 game 28
execute if score round setting matches 35 run scoreboard players set m5 game 35

execute if score round setting matches 40 run scoreboard players set m2 game 16
execute if score round setting matches 40 run scoreboard players set m3 game 24
execute if score round setting matches 40 run scoreboard players set m4 game 32
execute if score round setting matches 40 run scoreboard players set m5 game 40

execute if score round setting matches 45 run scoreboard players set m2 game 18
execute if score round setting matches 45 run scoreboard players set m3 game 27
execute if score round setting matches 45 run scoreboard players set m4 game 36
execute if score round setting matches 45 run scoreboard players set m5 game 45

execute if score round setting matches 50 run scoreboard players set m2 game 20
execute if score round setting matches 50 run scoreboard players set m3 game 30
execute if score round setting matches 50 run scoreboard players set m4 game 40
execute if score round setting matches 50 run scoreboard players set m5 game 50

execute if score round setting matches 55 run scoreboard players set m2 game 22
execute if score round setting matches 55 run scoreboard players set m3 game 33
execute if score round setting matches 55 run scoreboard players set m4 game 44
execute if score round setting matches 55 run scoreboard players set m5 game 55

execute if score round setting matches 60 run scoreboard players set m2 game 24
execute if score round setting matches 60 run scoreboard players set m3 game 36
execute if score round setting matches 60 run scoreboard players set m4 game 48
execute if score round setting matches 60 run scoreboard players set m5 game 60

execute if score round setting matches 65 run scoreboard players set m2 game 26
execute if score round setting matches 65 run scoreboard players set m3 game 39
execute if score round setting matches 65 run scoreboard players set m4 game 52
execute if score round setting matches 65 run scoreboard players set m5 game 65

execute if score round setting matches 70 run scoreboard players set m2 game 28
execute if score round setting matches 70 run scoreboard players set m3 game 42
execute if score round setting matches 70 run scoreboard players set m4 game 56
execute if score round setting matches 70 run scoreboard players set m5 game 70

execute if score round setting matches 75 run scoreboard players set m2 game 30
execute if score round setting matches 75 run scoreboard players set m3 game 45
execute if score round setting matches 75 run scoreboard players set m4 game 60
execute if score round setting matches 75 run scoreboard players set m5 game 75

execute if score round setting matches 80 run scoreboard players set m2 game 32
execute if score round setting matches 80 run scoreboard players set m3 game 48
execute if score round setting matches 80 run scoreboard players set m4 game 64
execute if score round setting matches 80 run scoreboard players set m5 game 80

execute if score round setting matches 85 run scoreboard players set m2 game 34
execute if score round setting matches 85 run scoreboard players set m3 game 51
execute if score round setting matches 85 run scoreboard players set m4 game 68
execute if score round setting matches 85 run scoreboard players set m5 game 85

execute if score round setting matches 90 run scoreboard players set m2 game 36
execute if score round setting matches 90 run scoreboard players set m3 game 54
execute if score round setting matches 90 run scoreboard players set m4 game 72
execute if score round setting matches 90 run scoreboard players set m5 game 90

execute if score round setting matches 95 run scoreboard players set m2 game 38
execute if score round setting matches 95 run scoreboard players set m3 game 57
execute if score round setting matches 95 run scoreboard players set m4 game 76
execute if score round setting matches 95 run scoreboard players set m5 game 95

execute if score round setting matches 100 run scoreboard players set m2 game 40
execute if score round setting matches 100 run scoreboard players set m3 game 60
execute if score round setting matches 100 run scoreboard players set m4 game 80
execute if score round setting matches 100 run scoreboard players set m5 game 100

tag @a add playing
gamemode 2 @a
tp @a 0 2 0
scoreboard players set gamestartcountdown game 5
scoreboard players set game_ready game 2

setblock -6 -14 11 redstone_block

execute if score round-auto setting matches 1 run scoreboard players set level game 1
scoreboard players set round game 0
scoreboard players set selectgame game 0
scoreboard players set playing game 1
execute as @a at @s run scoreboard players add player game 1

clear @a