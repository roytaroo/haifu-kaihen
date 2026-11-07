scoreboard players random game9_m game 1 8

execute if score game9_m game matches 1 run tellraw @a {"rawtext":[{"text":"奈落へ落ちるな"}]}
execute if score game9_m game matches 2 run tellraw @a {"rawtext":[{"text":"奈落へ落ちろ"}]}
execute if score game9_m game matches 3 run tellraw @a {"rawtext":[{"text":"飛べ"}]}
execute if score game9_m game matches 4 run tellraw @a {"rawtext":[{"text":"飛ぶな"}]}
execute if score game9_m game matches 5 run tellraw @a {"rawtext":[{"text":"水を飲め"}]}
execute if score game9_m game matches 6 run tellraw @a {"rawtext":[{"text":"水を飲むな"}]}
execute if score game9_m game matches 7 run tellraw @a {"rawtext":[{"text":"緑色のブロックを踏め"}]}
execute if score game9_m game matches 8 run tellraw @a {"rawtext":[{"text":"緑色のブロックを踏むな"}]}

scoreboard players set game9_timer game 4
scoreboard players set game9_x game 1

setblock 43 -14 17 redstone_block
setblock 43 -14 20 redstone_block