scoreboard players add start_countdown game -1

titleraw @a title {"rawtext":[{"text":". . . ."},{"score":{"name":"start_countdown","objective":"game"}},{"text":". . . ."}]}

execute if score start_countdown game > constant0 constant as @a at @s run playsound note.pling @s ~~~ 1 0.8 1
execute if score start_countdown game = constant0 constant as @a at @s run playsound note.pling @s ~~~ 1 1.05 1


execute if score start_countdown game matches 3 run structure load screen-countdown-3 -85 31 -31 180_degrees
execute if score start_countdown game matches 3 run structure load screen-countdown-3 84 31 -31

execute if score start_countdown game matches 2 run structure load screen-countdown-2 -85 31 -31 180_degrees
execute if score start_countdown game matches 2 run structure load screen-countdown-2 84 31 -31

execute if score start_countdown game matches 1 run structure load screen-countdown-1 -85 31 -31 180_degrees
execute if score start_countdown game matches 1 run structure load screen-countdown-1 84 31 -31

setblock 84 33 -31 air
setblock -83 33 32 air

execute if score start_countdown game < constant1 constant if score navi_message game matches 0 run function navi_message