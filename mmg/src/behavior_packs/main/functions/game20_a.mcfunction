execute if score game20_random_item game matches 1 run tag @a[hasitem={item=wooden_pickaxe}] add game20_win_a
execute if score game20_random_item game matches 2 run tag @a[hasitem={item=furnace}] add game20_win_a
execute if score game20_random_item game matches 3 run tag @a[hasitem={item=blast_furnace}] add game20_win_a
execute if score game20_random_item game matches 4 run tag @a[hasitem={item=cake}] add game20_win_a
execute if score game20_random_item game matches 5 run tag @a[hasitem={item=bread}] add game20_win_a
execute if score game20_random_item game matches 6 run tag @a[hasitem={item=diamond_pickaxe}] add game20_win_a
execute if score game20_random_item game matches 7 run tag @a[hasitem={item=wooden_axe}] add game20_win_a
execute if score game20_random_item game matches 8 run tag @a[hasitem={item=quartz_block}] add game20_win_a
execute if score game20_random_item game matches 9 run tag @a[hasitem={item=wool}] add game20_win_a
execute if score game20_random_item game matches 10 run tag @a[hasitem={item=gold_ingot}] add game20_win_a

execute as @a[tag=game20_win_a] at @s run tellraw @a {"rawtext":[{"text":"§e"},{"selector":"@s"},{"text":" がクラフトを完了しました！"}]}
execute as @a[tag=game20_win_a] at @s run playsound note.pling @a
clear @a[tag=game20_win_a]
tag @a[tag=game20_win_a] add game20_win
tag @a remove game20_win_a