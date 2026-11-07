execute if score playing game matches 1 run tellraw @s {"rawtext":[{"text":"MMG へようこそ！\nあなたはゲームを遊んでいる途中でサーバーを閉じてしまったようです。自動でゲームを強制的に終了します！"}]}
execute if score playing game matches 1 run tellraw @s {"rawtext":[{"text":"§c現在、ゲームを強制的にリセットしています。少々お待ちください。"}]}
execute if score playing game matches 1 run setblock -14 -14 16 redstone_block

execute if score playing game matches 0 run tellraw @s {"rawtext":[{"text":"ヒント: §eスロットの一番右端のアイテムを右クリック(スマホ: 短くタップ)して、ゲームの開始/設定ができます！"}]}