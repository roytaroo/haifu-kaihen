tag @a[tag=game7_give_1,hasitem=[{item=copper_sword,quantity=0},{item=iron_sword,quantity=0},{item=diamond_sword,quantity=0},{item=netherite_sword,quantity=0}]] add game7_give_1_o
tellraw @a[tag=game7_give_1_o] {"rawtext":[{"text":"§aアイテムを強化しました！ §n木→§6銅"}]}
clear @a[tag=game7_give_1_o] copper_ingot
tellraw @a[tag=game7_give_1,hasitem={item=copper_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: 既にレベルアップ済みです"}]}
tellraw @a[tag=game7_give_1,hasitem={item=iron_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: 既にレベルアップ済みです"}]}
tellraw @a[tag=game7_give_1,hasitem={item=diamond_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: 既にレベルアップ済みです"}]}
tellraw @a[tag=game7_give_1,hasitem={item=netherite_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: 既にレベルアップ済みです"}]}
clear @a[tag=game7_give_1_o] wooden_sword 0 1
give @a[tag=game7_give_1_o] copper_sword
playsound random.anvil.use @a[tag=game7_give_1_o]
clear @a[tag=game7_give_1,hasitem=[{item=copper_sword,quantity=0},{item=iron_sword,quantity=0},{item=diamond_sword,quantity=0},{item=netherite_sword,quantity=0}]] copper_ingot 1

tag @a[tag=game7_give_2,hasitem=[{item=wooden_sword,quantity=0},{item=copper_sword},{item=iron_sword,quantity=0},{item=diamond_sword,quantity=0},{item=netherite_sword,quantity=0}]] add game7_give_2_o
tellraw @a[tag=game7_give_2_o] {"rawtext":[{"text":"§aアイテムを強化しました！ §6銅→§f鉄"}]}
clear @a[tag=game7_give_2_o] iron_ingot
tellraw @a[tag=game7_give_2,hasitem={item=wooden_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: レベルが足りません。レベルアップには銅が必要です"}]}
tellraw @a[tag=game7_give_2,hasitem={item=iron_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: 既にレベルアップ済みです"}]}
tellraw @a[tag=game7_give_2,hasitem={item=diamond_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: 既にレベルアップ済みです"}]}
tellraw @a[tag=game7_give_2,hasitem={item=netherite_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: 既にレベルアップ済みです"}]}
clear @a[tag=game7_give_2_o] copper_sword 0 1
give @a[tag=game7_give_2_o] iron_sword
playsound random.anvil.use @a[tag=game7_give_2_o]
clear @a[tag=game7_give_2,hasitem=[{item=wooden_sword,quantity=0},{item=copper_sword},{item=iron_sword,quantity=0},{item=diamond_sword,quantity=0},{item=netherite_sword,quantity=0}]] iron_ingot 1

tag @a[tag=game7_give_3,hasitem=[{item=wooden_sword,quantity=0},{item=copper_sword,quantity=0},{item=iron_sword},{item=diamond_sword,quantity=0},{item=netherite_sword,quantity=0}]] add game7_give_3_o
tellraw @a[tag=game7_give_3_o] {"rawtext":[{"text":"§aアイテムを強化しました！ §f鉄→§bダイヤ"}]}
clear @a[tag=game7_give_3_o] diamond
tellraw @a[tag=game7_give_3,hasitem={item=wooden_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: レベルが足りません。レベルアップには銅が必要です"}]}
tellraw @a[tag=game7_give_3,hasitem={item=copper_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: レベルが足りません。レベルアップには鉄が必要です"}]}
tellraw @a[tag=game7_give_3,hasitem={item=diamond_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: 既にレベルアップ済みです"}]}
tellraw @a[tag=game7_give_3,hasitem={item=netherite_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: 既にレベルアップ済みです"}]}
clear @a[tag=game7_give_3_o] iron_sword 0 1
give @a[tag=game7_give_3_o] diamond_sword
playsound random.anvil.use @a[tag=game7_give_3_o]
clear @a[tag=game7_give_3,hasitem=[{item=wooden_sword,quantity=0},{item=copper_sword,quantity=0},{item=iron_sword},{item=diamond_sword,quantity=0},{item=netherite_sword,quantity=0}]] diamond 1

tag @a[tag=game7_give_4,hasitem=[{item=wooden_sword,quantity=0},{item=copper_sword,quantity=0},{item=iron_sword,quantity=0},{item=diamond_sword},{item=netherite_sword,quantity=0}]] add game7_give_4_o
tellraw @a[tag=game7_give_4_o] {"rawtext":[{"text":"§aアイテムを強化しました！ §bダイヤ→§dネザライト"}]}
clear @a[tag=game7_give_4_o] netherite_ingot
tellraw @a[tag=game7_give_4,hasitem={item=wooden_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: レベルが足りません。レベルアップには銅が必要です"}]}
tellraw @a[tag=game7_give_4,hasitem={item=copper_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: レベルが足りません。レベルアップには鉄が必要です"}]}
tellraw @a[tag=game7_give_4,hasitem={item=iron_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: レベルが足りません。レベルアップにはダイヤモンドが必要です"}]}
tellraw @a[tag=game7_give_4,hasitem={item=netherite_sword}] {"rawtext":[{"text":"§cアイテムを強化できません: 既にレベルアップ済みです"}]}
clear @a[tag=game7_give_4_o] diamond_sword 0 1
give @a[tag=game7_give_4_o] netherite_sword
playsound random.anvil.use @a[tag=game7_give_4_o]
clear @a[tag=game7_give_4,hasitem=[{item=wooden_sword,quantity=0},{item=copper_sword,quantity=0},{item=iron_sword,quantity=0},{item=diamond_sword},{item=netherite_sword,quantity=0}]] netherite_ingot 1

tag @a remove game7_give_1
tag @a remove game7_give_2
tag @a remove game7_give_3
tag @a remove game7_give_4
tag @a remove game7_give_1_o
tag @a remove game7_give_2_o
tag @a remove game7_give_3_o
tag @a remove game7_give_4_o