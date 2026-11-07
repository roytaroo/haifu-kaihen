execute if score round-auto setting matches 1 if score round game = m2 game run scoreboard players set level game 2
execute if score round-auto setting matches 1 if score round game = m3 game run scoreboard players set level game 3
execute if score round-auto setting matches 1 if score round game = m4 game run scoreboard players set level game 4
execute if score round-auto setting matches 1 if score round game = m5 game run scoreboard players set level game 5

execute if score round-auto setting matches 1 if score round game = m2 game run tellraw @a {"rawtext":[{"text":"§aレベルが 2 になりました！\n§eゲームの進行速度が速くなったり、ラウンド数が増えたり...と、難しくなっていきます！"}]}
execute if score round-auto setting matches 1 if score round game = m3 game run tellraw @a {"rawtext":[{"text":"§eレベルが 3 になりました！"}]}
execute if score round-auto setting matches 1 if score round game = m4 game run tellraw @a {"rawtext":[{"text":"§cレベルが 4 になりました！"}]}
execute if score round-auto setting matches 1 if score round game = m5 game run tellraw @a {"rawtext":[{"text":"§4レベルが 5 になりました！"}]}

execute if score round-auto setting matches 1 if score round game = m2 game as @a at @s run playsound random.levelup @s ~~~ 1 1.1
execute if score round-auto setting matches 1 if score round game = m3 game as @a at @s run playsound random.levelup @s ~~~ 1 1.3
execute if score round-auto setting matches 1 if score round game = m4 game as @a at @s run playsound random.levelup @s ~~~ 1 1.5
execute if score round-auto setting matches 1 if score round game = m5 game as @a at @s run playsound random.levelup @s ~~~ 1 1.7