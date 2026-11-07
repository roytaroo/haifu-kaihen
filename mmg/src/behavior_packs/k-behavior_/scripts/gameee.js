import { world, system, ItemStack } from "@minecraft/server";
import { ActionFormData, ModalFormData, MessageFormData } from "@minecraft/server-ui";


const ADMIN_ITEM_ID = "item:setting_admin";
const SETTING_ITEM_ID = "item:setting";
const ADMIN_TAGS = ["admin", "admin_game-start", "admin_player-auth", "admin_game-setting"];
const HOST_ASSIGNED_PROPERTY = "kohaku:host_assigned";


// テスト
function generateRandomChart(length = 30, noteRate = 0.3) {
    return Array.from({ length }, () =>
        Math.random() < noteRate ? "O" : "-"
    );
}

/* ユーティリティ */

function getObjective(name) {
    let obj = world.scoreboard.getObjective(name);
    if (!obj) {
        try {
            world.scoreboard.addObjective(name, name);
        } catch {
            // 既に作成済みの場合は無視
        }
        obj = world.scoreboard.getObjective(name);
    }
    return obj;
}

function getScore(objective, participant, defaultValue = 0) {
    try {
        const score = objective.getScore(participant);
        return typeof score === "number" ? score : defaultValue;
    } catch {
        return defaultValue;
    }
}

function setTag(entity, tag, value) {
    if (value) {
        if (!entity.hasTag(tag)) entity.addTag(tag);
    } else {
        if (entity.hasTag(tag)) entity.removeTag(tag);
    }
}

function getSortedPlayers() {
    return world.getAllPlayers().sort((a, b) => a.name.localeCompare(b.name));
}

function hasAnyAdminTag(player) {
    return player.hasTag("host") || ADMIN_TAGS.some((tag) => player.hasTag(tag));
}

function hasPermission(player, tag) {
    return player.hasTag("admin") || player.hasTag("host") || player.hasTag(tag);
}

function isHost(player) {
    return player.hasTag("host");
}

/* hostタグの付与（ワールドに最初に参加した1人のみ） */

world.afterEvents.playerSpawn.subscribe((event) => {
    if (!event.initialSpawn) return;

    const alreadyAssigned = world.getDynamicProperty(HOST_ASSIGNED_PROPERTY);
    const currentHostOnline = world.getAllPlayers().some((p) => p.hasTag("host"));

    // フラグ上は割り当て済みでも、実際にhostタグを持つプレイヤーが誰もいない場合
    // （配布マップを別の人が開いた場合など）は、改めて割り当て直す。
    if (alreadyAssigned && currentHostOnline) return;

    world.setDynamicProperty(HOST_ASSIGNED_PROPERTY, true);
    if (!event.player.hasTag("host")) {
        event.player.addTag("host");
    }
});

/* アイテム使用イベント */

world.beforeEvents.itemUse.subscribe((event) => {
    const player = event.source;
    if (event.itemStack.typeId !== ADMIN_ITEM_ID) return;

    if (!hasAnyAdminTag(player)) {
        system.run(() => player.sendMessage("§cあなたは管理者ではありません"));
        return;
    }

    const gameObj = getObjective("game");
    const playing = getScore(gameObj, "playing", 0);
    if (playing === 1) {
        system.run(() => player.sendMessage("§c[!] ゲーム中は設定を開けません。"));
        return;
    }

    system.run(() => settingUI_main(player));
});

/* 管理者アイテムの自動付与（5tick毎） */
// スローダウン問題改善
let adminItemLoopStarted = false;
world.afterEvents.playerSpawn.subscribe((event) => {
    if (!event.initialSpawn || adminItemLoopStarted) return;
    adminItemLoopStarted = true;

    system.runTimeout(() => {
        system.runInterval(() => {
            const gameObj = getObjective("game");
            const playing = getScore(gameObj, "playing", 0);
            if (playing === 1) return;

            for (const player of world.getAllPlayers()) {
                if (!hasAnyAdminTag(player)) continue;

                const inventory = player.getComponent("minecraft:inventory")?.container;
                if (!inventory) continue;

                const slotItem = inventory.getItem(8);
                if (!slotItem || slotItem.typeId !== ADMIN_ITEM_ID) {
                    inventory.setItem(8, new ItemStack(ADMIN_ITEM_ID, 1));
                }
            }
        }, 5);
    }, 100);
});

/* 管理者アイテムのドロップ防止 */

world.afterEvents.entitySpawn.subscribe((event) => {
    const entity = event.entity;
    if (entity.typeId !== "minecraft:item") return;

    const itemComponent = entity.getComponent("minecraft:item");
    if (itemComponent && itemComponent.itemStack.typeId === ADMIN_ITEM_ID) {
        entity.remove();
    }
});

/* 設定アイテムの自動付与（5tick毎） */
// スローダウン問題改善
let settingItemLoopStarted = false;
world.afterEvents.playerSpawn.subscribe((event) => {
    if (!event.initialSpawn || settingItemLoopStarted) return;
    settingItemLoopStarted = true;

    system.runTimeout(() => {
        system.runInterval(() => {
            const gameObj = getObjective("game");
            const playing = getScore(gameObj, "playing", 0);
            if (playing === 1) return;

            for (const player of world.getAllPlayers()) {

                const inventory = player.getComponent("minecraft:inventory")?.container;
                if (!inventory) continue;

                const slotItem = inventory.getItem(0);
                if (!slotItem || slotItem.typeId !== SETTING_ITEM_ID) {
                    inventory.setItem(0, new ItemStack(SETTING_ITEM_ID, 1));
                }
            }
        }, 5);
    }, 100);
});

/* 設定アイテムのドロップ防止 */

world.afterEvents.entitySpawn.subscribe((event) => {
    const entity = event.entity;
    if (entity.typeId !== "minecraft:item") return;

    const itemComponent = entity.getComponent("minecraft:item");
    if (itemComponent && itemComponent.itemStack.typeId === SETTING_ITEM_ID) {
        entity.remove();
    }
});


    // 再ログイン検知
world.afterEvents.playerSpawn.subscribe((event) => {
        const { player, initialSpawn } = event;

        if (initialSpawn) {
            try {
                player.runCommand("tag @s add login");
                player.runCommand("execute as @s[tag=host] at @s run function hostlogin");
            } catch (e) {}
        }
    });


/* ユーザー メインメニュー */

function user_settingUI_main(player) {
    const gui = new ActionFormData()
        .title("設定")
        .button("ナビゲーター表示をON/OFF");

    gui.show(player).then((result) => {
        if (result.canceled) return;
        switch (result.selection) {
            case 0:
                    player.runCommand("say test");
                    return;
        }
    });
}

/* メインメニュー */

function settingUI_main(player) {
    const gui = new ActionFormData()
        .title("設定")
        .button("ゲームを開始")
        .button("プレイヤーの設定")
        .button("ゲーム設定")
        .button("ミニゲームのON/OFF")
        .button("ランキング掲示板")
        .button("BOT");

    gui.show(player).then((result) => {
        if (result.canceled) return;
        switch (result.selection) {
            case 0:
                if (!hasPermission(player, "admin_game-start")) {
                    player.sendMessage("§cあなたはこれを編集する権限がありません！");
                    return;
                }
                player.runCommand("function main_start");
                break;
            case 1:
                if (!hasPermission(player, "admin_player-auth")) {
                    player.sendMessage("§cあなたはこれを編集する権限がありません！");
                    return;
                }
                settingUI_1(player);
                break;
            case 2:
                if (!hasPermission(player, "admin_game-setting")) {
                    player.sendMessage("§cあなたはこれを編集する権限がありません！");
                    return;
                }
                settingUI_2(player);
                break;
            case 3:
            case 4:
            case 5:
                // mmg_plus パックの画面を開く
                if (!hasPermission(player, "admin_game-setting")) {
                    player.sendMessage("§cあなたはこれを編集する権限がありません！");
                    return;
                }
                player.runCommand(["scriptevent mmgplus:games_ui", "scriptevent mmgplus:board_ui", "scriptevent mmgbot:ui"][result.selection - 3]);
                break;
        }
    });
}

/* プレイヤーの設定 */

function settingUI_1(player) {
    const gui = new ActionFormData()
        .title("§8設定 / §r§lプレイヤーの設定")
        .button("プレイヤーの権限")
        .button("プレイヤーをBAN")
        .button("BAN処理を一時的にON/OFF");
    gui.show(player).then((result) => {
        if (result.canceled) return;
        switch (result.selection) {
            case 0:
                settingUI_1_1(player);
                break;
            case 1:
                settingUI_1_2(player);
                break;
            case 2:
                player.runCommand("setblock -18 -14 16 redstone_block");
                break;
        }
    });
}

function settingUI_1_1(player) {
    const players = getSortedPlayers();

    const gui = new ActionFormData().title("§8設定 / §rプレイヤーの権限");
    for (const p of players) {
        gui.button(p.name);
    }

    gui.show(player).then((result) => {
        if (result.canceled) return;
        const target = players[result.selection];
        if (!target) return;
        showPermissionUI(player, target);
    });
}

function showPermissionUI(player, target) {
    if (isHost(target)) {
        const gui = new ActionFormData()
            .title(target.name)
            .body("§c[!] ホストの権限を変更することはできません！")
            .button("OK");
        gui.show(player).then((result) => {
            if (result.canceled) return;
            settingUI_1_1(player);
        });
        return;
    }

    const gui = new ModalFormData()
        .title(target.name)
        .toggle("§e[!] 管理者権限を付与すると、それより下のすべての権限が有効化されます！\n管理者権限を付与", target.hasTag("admin"))
        .toggle("ゲームの開始を許可", target.hasTag("admin_game-start"))
        .toggle("プレイヤーの権限の変更を許可", target.hasTag("admin_player-auth"))
        .toggle("ゲーム設定の変更を許可", target.hasTag("admin_game-setting"));

    gui.show(player).then((response) => {
        if (response.canceled) return;
        const [isAdmin, gameStart, playerAuth, gameSetting] = response.formValues;

        setTag(target, "admin", isAdmin);
        setTag(target, "admin_game-start", isAdmin || gameStart);
        setTag(target, "admin_player-auth", isAdmin || playerAuth);
        setTag(target, "admin_game-setting", isAdmin || gameSetting);

        player.sendMessage(`§a${target.name} の権限を更新しました。`);
    }).catch((err) => console.error(err));
}

function settingUI_1_2(player) {
    const players = getSortedPlayers();

    const gui = new ActionFormData().title("§8設定 / §rプレイヤーをBAN");
    for (const p of players) {
        gui.button(p.name);
    }

    gui.show(player).then((result) => {
        if (result.canceled) return;
        const target = players[result.selection];
        if (!target) return;
        showBanUI(player, target);
    });
}

function showBanUI(player, target) {
    if (isHost(target)) {
        const gui = new ActionFormData()
            .title(target.name)
            .body("§c[!] ホストをBANすることはできません！")
            .button("OK");
        gui.show(player).then((result) => {
            if (result.canceled) return;
            settingUI_1_2(player);
        });
        return;
    }

    const gui = new ActionFormData()
        .title(target.name)
        .button("このプレイヤーをBANする")
        .button("戻る");

    gui.show(player).then((result) => {
        if (result.canceled) return;
        switch (result.selection) {
            case 0:
                confirmBanUI(player, target);
                break;
            case 1:
                settingUI_1_2(player);
                break;
        }
    });
}

function confirmBanUI(player, target) {
    const gui = new MessageFormData()
        .title("確認")
        .body("本当にBANしますか？\nBANを解除するまで、このプレイヤーはサーバーに参加できません。")
        .button1("はい")
        .button2("いいえ");

    gui.show(player).then((result) => {
        if (result.canceled) return;
        if (result.selection === 0) {
            if (!target.hasTag("ban")) target.addTag("ban");
            player.sendMessage(`§a${target.name} をBANしました。`);
        } else {
            showBanUI(player, target);
        }
    }).catch((err) => console.error(err));
}

/* ゲーム設定 */

function settingUI_2(player) {
    const settingObj = getObjective("setting");
    const gameObj = getObjective("game");

    if (!settingObj || !gameObj) {
        player.sendMessage("§c[!] スコアボードの取得に失敗しました。管理者に連絡してください。");
        console.error("settingUI_2: setting または game オブジェクティブの取得に失敗しました。");
        return;
    }

    const currentRound = getScore(settingObj, "round", 20);
    const currentAuto = getScore(settingObj, "round-auto", 1);
    const currentLevel = getScore(gameObj, "level", 0);
    const currentGusu = getScore(settingObj, "gusu-play", 0);
    const currentMulti = getScore(settingObj, "multi-play", 0);

    const defaultLevelIndex = currentAuto === 1 ? 0 : currentLevel;

    const gui = new ModalFormData()
        .title("§lゲーム設定")
        .slider("ラウンド数", 0, 100, 5, currentRound)
        .dropdown("レベル", ["自動設定", "レベル1", "レベル2", "レベル3", "レベル4", "レベル5"], defaultLevelIndex)

    gui.show(player).then((response) => {
        if (response.canceled) return;
        const [round, levelIndex, gusuPlay, multiPlay] = response.formValues;

        settingObj.setScore("round", round);

        if (levelIndex === 0) {
            settingObj.setScore("round-auto", 1);
            gameObj.setScore("level", 0);
        } else {
            settingObj.setScore("round-auto", 0);
            gameObj.setScore("level", levelIndex);
        }

        settingObj.setScore("gusu-play", gusuPlay ? 1 : 0);
        settingObj.setScore("multi-play", multiPlay ? 1 : 0);

        player.sendMessage(`§a設定を保存しました！`);
        player.sendMessage(`ラウンド数: ${round}`);
        player.sendMessage(`レベル: ${levelIndex === 0 ? "自動設定" : "レベル" + levelIndex}`);
    }).catch((err) => {
        console.error(err);
    });
}

/* ミニゲーム無効/有効 */

function settingUI_3(player) {
    const gui = new ModalFormData()
        .title("§lミニゲーム無効/有効")
        .toggle("Escape Lava", true)
        .toggle("ニモ相撲", true);

    gui.show(player).then((response) => {
        if (response.canceled) return;
        const [escapeLava, nimoSumo] = response.formValues;
        player.sendMessage(`§a設定を保存しました！`);
        player.sendMessage(`Escape Lava: ${escapeLava}`);
        player.sendMessage(`ニモ相撲: ${nimoSumo}`);
    }).catch((err) => {
        console.error(err);
    });
}