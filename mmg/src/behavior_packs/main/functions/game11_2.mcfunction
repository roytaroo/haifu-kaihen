execute if score game11_red_a game matches 1 run tellraw @a {"rawtext":[{"text":"最も票が多かったのは§c赤§rでした！"}]}
execute if score game11_red_a game matches 1 run fill -10 6 13 10 5 17 air
execute if score game11_red_a game matches 1 run scoreboard players set game11_red_a game 2

execute if score game11_green_a game matches 1 run tellraw @a {"rawtext":[{"text":"最も票が多かったのは§a緑§rでした！"}]}
execute if score game11_green_a game matches 1 run fill -10 6 7 10 5 11 air
execute if score game11_green_a game matches 1 run scoreboard players set game11_green_a game 2

execute if score game11_blue_a game matches 1 run tellraw @a {"rawtext":[{"text":"最も票が多かったのは§9青§rでした！"}]}
execute if score game11_blue_a game matches 1 run fill -10 6 1 10 5 5 air
execute if score game11_blue_a game matches 1 run scoreboard players set game11_blue_a game 2

execute if score game11_yellow_a game matches 1 run tellraw @a {"rawtext":[{"text":"最も票が多かったのは§e黄§rでした！"}]}
execute if score game11_yellow_a game matches 1 run fill -10 6 -5 10 5 -1 air
execute if score game11_yellow_a game matches 1 run scoreboard players set game11_yellow_a game 2

execute if score game11_white_a game matches 1 run tellraw @a {"rawtext":[{"text":"最も票が多かったのは§f白§rでした！"}]}
execute if score game11_white_a game matches 1 run fill -10 6 -11 10 5 -7 air
execute if score game11_white_a game matches 1 run scoreboard players set game11_white_a game 2

execute if score game11_purple_a game matches 1 run tellraw @a {"rawtext":[{"text":"最も票が多かったのは§d紫§rでした！"}]}
execute if score game11_purple_a game matches 1 run fill -10 6 -17 10 5 -13 air
execute if score game11_purple_a game matches 1 run scoreboard players set game11_purple_a game 2

execute if score game11_x game matches 1 run tellraw @a {"rawtext":[{"text":"§7誰も投票しなかったので、何も消えませんでした。"}]}

tellraw @a {"rawtext":[{"text":"§eそれぞれの色の票数"}]}
tellraw @a {"rawtext":[{"text":"§c赤§r: "},{"score":{"name":"game11_red","objective":"game"}},{"text":"票\n§r投票者: §e"},{"selector":"@a[tag=game11_red]"},{"text":"\n"}]}
tellraw @a {"rawtext":[{"text":"§a緑§r: "},{"score":{"name":"game11_green","objective":"game"}},{"text":"票\n§r投票者: §e"},{"selector":"@a[tag=game11_green]"},{"text":"\n"}]}
tellraw @a {"rawtext":[{"text":"§9青§r: "},{"score":{"name":"game11_blue","objective":"game"}},{"text":"票\n§r投票者: §e"},{"selector":"@a[tag=game11_blue]"},{"text":"\n"}]}
tellraw @a {"rawtext":[{"text":"§e黄§r: "},{"score":{"name":"game11_yellow","objective":"game"}},{"text":"票\n§r投票者: §e"},{"selector":"@a[tag=game11_yellow]"},{"text":"\n"}]}
tellraw @a {"rawtext":[{"text":"白: "},{"score":{"name":"game11_white","objective":"game"}},{"text":"票\n§r投票者: §e"},{"selector":"@a[tag=game11_white]"},{"text":"\n"}]}
tellraw @a {"rawtext":[{"text":"§d紫§r: "},{"score":{"name":"game11_purple","objective":"game"}},{"text":"票\n§r投票者: §e"},{"selector":"@a[tag=game11_purple]"},{"text":"\n"}]}

scoreboard players set game11_red game 0
scoreboard players set game11_green game 0
scoreboard players set game11_blue game 0
scoreboard players set game11_yellow game 0
scoreboard players set game11_white game 0
scoreboard players set game11_purple game 0
scoreboard players set game11_x game 0

inputpermission set @a[tag=playing] movement enabled

tag @a remove game11_red
tag @a remove game11_green
tag @a remove game11_blue
tag @a remove game11_yellow
tag @a remove game11_white
tag @a remove game11_purple