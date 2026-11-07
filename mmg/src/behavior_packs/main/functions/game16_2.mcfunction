execute if score game16_set game matches 1 run tag @a[tag=!win,hasitem={item=coal,quantity=3..}] add game16_win1
execute if score game16_set game matches 2 run tag @a[tag=!win,hasitem={item=raw_copper,quantity=3..}] add game16_win1
execute if score game16_set game matches 3 run tag @a[tag=!win,hasitem={item=raw_iron,quantity=3..}] add game16_win1
execute if score game16_set game matches 4 run tag @a[tag=!win,hasitem={item=diamond,quantity=3..}] add game16_win1
execute if score game16_set game matches 5 run tag @a[tag=!win,hasitem={item=emerald,quantity=3..}] add game16_win1
execute if score game16_set game matches 6 run tag @a[tag=!win,hasitem={item=raw_gold,quantity=3..}] add game16_win1
execute if score game16_set game matches 7 run tag @a[tag=!win,hasitem={item=redstone,quantity=12..}] add game16_win1
execute if score game16_set game matches 8 run tag @a[tag=!win,hasitem={item=lapis_lazuli,quantity=12..}] add game16_win1

tellraw @a[tag=game16_win1] {"rawtext":[{"text":"§a鉱石を獲得しました！"}]}
playsound random.orb @a[tag=game16_win1]
tag @a[tag=game16_win1] add win
clear @a[tag=game16_win1]
tag @a[tag=game16_win1] remove game16_win1