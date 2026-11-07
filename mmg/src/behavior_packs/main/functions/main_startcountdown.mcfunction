scoreboard players add gamestartcountdown game -1

execute if score gamestartcountdown game matches 3 run structure load screen-countdown-3 -85 31 -31 180_degrees
execute if score gamestartcountdown game matches 3 run structure load screen-countdown-3 84 31 -31
execute if score gamestartcountdown game matches 2 run structure load screen-countdown-2 -85 31 -31 180_degrees
execute if score gamestartcountdown game matches 2 run structure load screen-countdown-2 84 31 -31
execute if score gamestartcountdown game matches 1 run structure load screen-countdown-1 -85 31 -31 180_degrees
execute if score gamestartcountdown game matches 1 run structure load screen-countdown-1 84 31 -31
execute if score gamestartcountdown game matches 0 run structure load screen-go -85 31 -31 180_degrees
execute if score gamestartcountdown game matches 0 run structure load screen-go 84 31 -31

setblock 84 32 -31 air
setblock -83 32 32 air

execute if score gamestartcountdown game > constant0 constant as @a at @s run playsound random.orb @s ~~~ 1 1.5 1
execute if score gamestartcountdown game matches 0 as @a at @s run playsound random.orb @s ~~~ 1 2 1

titleraw @a actionbar {"rawtext":[{"text":"ゲーム開始まで "},{"score":{"name":"gamestartcountdown","objective":"game"}},{"text":"秒"}]}
execute if score gamestartcountdown game < constant1 constant run title @a actionbar スタート！

execute if score gamestartcountdown game < constant1 constant run setblock -6 -14 15 redstone_block