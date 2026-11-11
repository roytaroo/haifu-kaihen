execute if score game9_m game matches 2 run tag @a[tag=!game9_die,tag=!game9_goal,tag=!died] add game9_goal
execute if score game9_m game matches 3 run tag @a[tag=!game9_die,tag=!game9_goal,tag=!died] add game9_goal
execute if score game9_m game matches 5 run tag @a[tag=!game9_die,tag=!game9_goal,tag=!died] add game9_goal
execute if score game9_m game matches 7 run tag @a[tag=!game9_die,tag=!game9_goal,tag=!died] add game9_goal
execute if score game9_m game matches 9 run tag @a[tag=!game9_die,tag=!game9_goal,tag=!died] add game9_goal
execute if score game9_m game matches 11 run tag @a[tag=!game9_die,tag=!game9_goal,tag=!died] add game9_goal
execute if score game9_m game matches 13 run tag @a[tag=!game9_die,tag=!game9_goal,tag=!died] add game9_goal
execute if score game9_m game matches 15 run tag @a[tag=!game9_die,tag=!game9_goal,tag=!died] add game9_goal
execute if score game9_m game matches 17 run tag @a[tag=!game9_die,tag=!game9_goal,tag=!died] add game9_goal
execute if score game9_m game matches 19 run tag @a[tag=!game9_die,tag=!game9_goal,tag=!died] add game9_goal
execute if score game9_m game matches 21 run tag @a[tag=!game9_die,tag=!game9_goal,tag=!died] add game9_goal
execute if score game9_m game matches 23 run tag @a[tag=!game9_die,tag=!game9_goal,tag=!died] add game9_goal
execute if score game9_m game matches 25 run tag @a[tag=!game9_die,tag=!game9_goal,tag=!died] add game9_goal
execute if score game9_m game matches 27 run tag @a[tag=!game9_die,tag=!game9_goal,tag=!died] add game9_goal

tag @a[tag=!game9_goal,tag=playing,tag=!game9_die,tag=!game9_goal2] add game9_die

tag @a[tag=game9_goal2] add game9_goal

tag @a remove game9_goal2

clear @a[tag=playing]