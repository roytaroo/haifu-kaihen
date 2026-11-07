execute if score start_countdown game < constant2 constant run setblock 3 -14 11 air
execute if score start_countdown game < constant2 constant run setblock 3 -14 14 air
execute if score start_countdown game < constant2 constant run setblock 3 -14 17 air
execute if score start_countdown game < constant2 constant run setblock 3 -14 20 air
execute if score start_countdown game < constant2 constant run setblock 3 -14 23 air

execute if score start_countdown game < constant2 constant if score selectgame game matches 1 run setblock 9 -14 11 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 2 run setblock 13 -14 11 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 3 run setblock 17 -14 11 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 4 run setblock 21 -14 11 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 5 run setblock 25 -14 11 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 6 run setblock 29 -14 11 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 7 run setblock 33 -14 11 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 8 run setblock 37 -14 11 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 9 run setblock 41 -14 11 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 10 run setblock 45 -14 11 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 11 run setblock 9 -14 39 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 12 run setblock 13 -14 39 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 13 run setblock 17 -14 39 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 14 run setblock 21 -14 39 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 15 run setblock 25 -14 39 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 16 run setblock 29 -14 39 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 17 run setblock 33 -14 39 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 18 run setblock 37 -14 39 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 19 run setblock 41 -14 39 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 20 run setblock 45 -14 39 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 21 run setblock 9 -14 67 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 22 run setblock 13 -14 67 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 23 run setblock 17 -14 67 redstone_block
execute if score start_countdown game < constant2 constant if score selectgame game matches 24 run setblock 21 -14 67 redstone_block

execute if score selectgame game matches 1 run gamerule fallDamage false
execute if score selectgame game matches 1 run gamerule pvp false
execute if score selectgame game matches 2 run gamerule fallDamage false
execute if score selectgame game matches 2 run gamerule pvp true
execute if score selectgame game matches 3 run gamerule fallDamage false
execute if score selectgame game matches 3 run gamerule pvp false
execute if score selectgame game matches 4 run gamerule fallDamage false
execute if score selectgame game matches 4 run gamerule pvp true
execute if score selectgame game matches 5 run gamerule fallDamage true
execute if score selectgame game matches 5 run gamerule pvp true
execute if score selectgame game matches 6 run gamerule fallDamage true
execute if score selectgame game matches 6 run gamerule pvp true
execute if score selectgame game matches 7 run gamerule fallDamage true
execute if score selectgame game matches 7 run gamerule pvp false
execute if score selectgame game matches 8 run gamerule fallDamage false
execute if score selectgame game matches 8 run gamerule pvp true
execute if score selectgame game matches 9 run gamerule fallDamage false
execute if score selectgame game matches 9 run gamerule pvp false
execute if score selectgame game matches 10 run gamerule fallDamage false
execute if score selectgame game matches 10 run gamerule pvp false
execute if score selectgame game matches 11 run gamerule fallDamage false
execute if score selectgame game matches 11 run gamerule pvp false
execute if score selectgame game matches 12 run gamerule fallDamage false
execute if score selectgame game matches 12 run gamerule pvp false
execute if score selectgame game matches 13 run gamerule fallDamage false
execute if score selectgame game matches 13 run gamerule pvp false
execute if score selectgame game matches 14 run gamerule fallDamage false
execute if score selectgame game matches 14 run gamerule pvp false
execute if score selectgame game matches 15 run gamerule fallDamage false
execute if score selectgame game matches 15 run gamerule pvp false
execute if score selectgame game matches 16 run gamerule fallDamage false
execute if score selectgame game matches 16 run gamerule pvp false
execute if score selectgame game matches 17 run gamerule fallDamage false
execute if score selectgame game matches 17 run gamerule pvp false
execute if score selectgame game matches 18 run gamerule fallDamage false
execute if score selectgame game matches 18 run gamerule pvp false
execute if score selectgame game matches 19 run gamerule fallDamage false
execute if score selectgame game matches 19 run gamerule pvp false
execute if score selectgame game matches 20 run gamerule fallDamage false
execute if score selectgame game matches 20 run gamerule pvp false
execute if score selectgame game matches 21 run gamerule fallDamage false
execute if score selectgame game matches 21 run gamerule pvp false
execute if score selectgame game matches 22 run gamerule fallDamage false
execute if score selectgame game matches 22 run gamerule pvp true
execute if score selectgame game matches 23 run gamerule fallDamage false
execute if score selectgame game matches 23 run gamerule pvp false
execute if score selectgame game matches 24 run gamerule fallDamage false
execute if score selectgame game matches 24 run gamerule pvp false

gamemode 2 @a[tag=playing]

execute if score start_countdown game matches 0 if score selectgame game matches 1 run structure load screen-nigero -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 1 run structure load screen-nigero 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 2 run structure load screen-fight -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 2 run structure load screen-fight 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 3 run structure load screen-game-playing -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 3 run structure load screen-game-playing 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 4 run structure load screen-nigero -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 4 run structure load screen-nigero 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 5 run structure load screen-fight -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 5 run structure load screen-fight 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 6 run structure load screen-nigero -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 6 run structure load screen-nigero 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 7 run structure load screen-fight -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 7 run structure load screen-fight 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 8 run structure load screen-fight -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 8 run structure load screen-fight 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 9 run structure load screen-sakarae -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 9 run structure load screen-sakarae 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 10 run structure load screen-yokero -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 10 run structure load screen-yokero 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 11 run structure load screen-game-playing -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 11 run structure load screen-game-playing 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 12 run structure load screen-yokero -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 12 run structure load screen-yokero 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 13 run structure load screen-game-playing -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 13 run structure load screen-game-playing 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 14 run structure load screen-game-playing -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 14 run structure load screen-game-playing 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 15 run structure load screen-nigero -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 15 run structure load screen-nigero 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 16 run structure load screen-game-playing -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 16 run structure load screen-game-playing 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 17 run structure load screen-game-playing -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 17 run structure load screen-game-playing 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 18 run structure load screen-game-playing -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 18 run structure load screen-game-playing 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 19 run structure load screen-game-playing -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 19 run structure load screen-game-playing 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 20 run structure load screen-game-playing -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 20 run structure load screen-game-playing 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 21 run structure load screen-game-playing -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 21 run structure load screen-game-playing 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 22 run structure load screen-game-playing -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 22 run structure load screen-game-playing 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 23 run structure load screen-game-playing -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 23 run structure load screen-game-playing 84 31 -31

execute if score start_countdown game matches 0 if score selectgame game matches 24 run structure load screen-game-playing -84 31 -31 180_degrees
execute if score start_countdown game matches 0 if score selectgame game matches 24 run structure load screen-game-playing 84 31 -31

setblock 84 32 -31 air
setblock -83 32 32 air

scoreboard players set stopgame game 0

spawnpoint @a[tag=playing] 0 20 0