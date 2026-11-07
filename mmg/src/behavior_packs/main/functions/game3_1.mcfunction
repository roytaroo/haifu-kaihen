fill 2 4 8 -2 8 8 air

execute if score game3_kazu game matches 1 run fill 1 4 8 -1 4 8 redstone_block
execute if score game3_kazu game matches 1 run fill 0 4 8 0 8 8 redstone_block
execute if score game3_kazu game matches 1 run setblock 1 7 8 redstone_block

execute if score game3_kazu game matches 2 run fill 1 4 8 -1 8 8 redstone_block
execute if score game3_kazu game matches 2 run fill 1 7 8 0 7 8 air
execute if score game3_kazu game matches 2 run fill 0 5 8 -1 5 8 air

execute if score game3_kazu game matches 3 run fill 1 4 8 -1 8 8 redstone_block
execute if score game3_kazu game matches 3 run fill 1 7 8 0 7 8 air
execute if score game3_kazu game matches 3 run fill 1 5 8 0 5 8 air

execute if score game3_kazu game matches 4 run fill 1 4 8 -1 8 8 redstone_block
execute if score game3_kazu game matches 4 run fill 0 7 8 0 8 8 air
execute if score game3_kazu game matches 4 run fill 1 4 8 0 5 8 air

execute if score game3_kazu game matches 5 run fill 1 4 8 -1 8 8 redstone_block
execute if score game3_kazu game matches 5 run fill 0 7 8 -1 7 8 air
execute if score game3_kazu game matches 5 run fill 1 5 8 0 5 8 air

execute if score game3_kazu game matches 6 run fill 1 4 8 -1 8 8 redstone_block
execute if score game3_kazu game matches 6 run fill 0 7 8 -1 7 8 air
execute if score game3_kazu game matches 6 run setblock 0 5 8 air

execute if score game3_kazu game matches 7 run fill 1 4 8 -1 8 8 redstone_block
execute if score game3_kazu game matches 7 run fill 1 4 8 0 7 8 air
execute if score game3_kazu game matches 7 run setblock 1 7 8 redstone_block

execute if score game3_kazu game matches 8 run fill 1 4 8 -1 8 8 redstone_block
execute if score game3_kazu game matches 8 run setblock 0 7 8 air
execute if score game3_kazu game matches 8 run setblock 0 5 8 air

execute if score game3_kazu game matches 9 run fill 1 4 8 -1 8 8 redstone_block
execute if score game3_kazu game matches 9 run setblock 0 7 8 air
execute if score game3_kazu game matches 9 run fill 1 5 8 0 5 8 air

structure load screen-game3_high-low -84 31 -31 180_degrees
structure load screen-game3_high-low 84 31 -31
setblock 84 32 -31 air
setblock -83 32 32 air