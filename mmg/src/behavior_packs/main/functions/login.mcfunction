tellraw @a[tag=login] {"rawtext":[{"text":"MMG へようこそ！"}]}

tag @a[tag=login] remove playing

execute as @a[tag=login] at @s run playsound random.levelup @s
clear @a[tag=login]
effect @a[tag=login] clear
effect @a[tag=login] saturation 1 255 true
effect @a[tag=login] instant_health 1 255 true
gamemode 2 @a[tag=login]
tag @a[tag=login] remove goal
tag @a[tag=login] remove died
tag @a[tag=login] remove lose
xp -1000L @a[tag=login]

inputpermission set @a[tag=login] movement enabled

tag @a[tag=login] remove game3_win
tag @a[tag=login] remove game6_oni
tag @a[tag=login] remove game13_c1
tag @a[tag=login] remove game13_c2

tp @a[tag=login] 48 13 1.0 facing 0 13 1.0

tag @a[tag=login] remove login