import { world, system, ItemStack, EnchantmentTypes, DisplaySlotId } from "@minecraft/server";
import { ModalFormData, ActionFormData } from "@minecraft/server-ui";
import * as server from "@minecraft/server";

const TICK_INTERVAL = 5;

function ensureObjective(id) {
    let obj = world.scoreboard.getObjective(id);
    if (!obj) {
        obj = world.scoreboard.addObjective(id, id);
    }
    return obj;
}

let objX, objY, objZ, objGame, objPoint;
let objGame24Kill;

const TP_MIN_X = -23;
const TP_MAX_X = 24;
const TP_MIN_Z = -23;
const TP_MAX_Z = 24;
const TP_START_Y = 2;   // 探索開始Y座標
const TP_MAX_Y = 320;   // エラー時
const TP6_MIN = -20;
const TP6_MAX = 20;
const PLAYING_TAG = "playing";
const TRIGGER_NAME = "game5_random_tp";
const TRIGGER_NAME_6 = "game6_random_tp";
const SELECT_GAME_NAME = "selectgame";
const TRIGGER_NAME_7 = "game7_random_tp";
const TRIGGER_NAME_DROP = "game7_item_drop_random1";
const TRIGGER_SYOKI = "game7_give_item_syoki";
const TRIGGER_NAME_10 = "game10_random";
const TRIGGER_NAME_11 = "game11_data";
const TRIGGER_NAME_12 = "game12_random";
const TRIGGER_NAME_17 = "game17_random";
const TRIGGER_NAME_18 = "game18_random_tp";
const TRIGGER_NAME_22 = "game22_random";
const TRIGGER_NAME_24 = "game24_random";
const TRIGGER_NAME_RANKING = "ranking";

const game4StationaryData = new Map();

const RANK_COLORS = { 1: "§e", 2: "§7", 3: "§6" };
const GAME11_COLORS = [
    { key: "red", label: "赤" },
    { key: "green", label: "緑" },
    { key: "blue", label: "青" },
    { key: "yellow", label: "黄" },
    { key: "white", label: "白" },
    { key: "purple", label: "紫" }
];
const GAME14_MOBS = [
    { label: "ブタ", tag: "game14_1" },
    { label: "ヒツジ", tag: "game14_2" },
    { label: "ニワトリ", tag: "game14_3" },
    { label: "ウシ", tag: "game14_4" }
];

let game7_bat_timer = 0;

function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}
// 通行可能(足元・頭上をこれで判定する)ブロックの一覧
const PASSABLE_BLOCK_IDS = new Set([
    "minecraft:air",
    "minecraft:cave_air",
    "minecraft:void_air",
    ...Array.from({ length: 16 }, (_, i) => `minecraft:light_block_${i}`)
]);

function isPassableBlock(block) {
    if (!block) return false; 
    if (block.isAir) return true;
    if (PASSABLE_BLOCK_IDS.has(block.typeId)) return true;
    return false;
}

function isSolidGroundBlock(block) {
    if (!block) return false;
    if (isPassableBlock(block)) return false;
    if (block.isLiquid) return false; 
    return true;
}

function findSafeY(dimension, x, z, startY, maxY) {
    var sY = (startY !== undefined) ? startY : 2;
    var mY = (maxY !== undefined) ? maxY : 100;

    for (let y = sY; y <= mY; y++) {
        try {
            const feetBlock = dimension.getBlock({ x: x, y: y, z: z });
            if (!feetBlock) continue;

            const headBlock = dimension.getBlock({ x: x, y: y + 1, z: z });
            const groundBlock = dimension.getBlock({ x: x, y: y - 1, z: z });

            if (!headBlock || !groundBlock) continue;

            const feetClear = isPassableBlock(feetBlock);
            const headClear = isPassableBlock(headBlock);
            const groundSolid = isSolidGroundBlock(groundBlock);

            if (feetClear && headClear && groundSolid) {
                return y;
            }
        } catch (e) {
            continue;
        }
    }
    return null;
}

function randomTeleportPlayingPlayers() {
    const players = world.getPlayers({ tags: [PLAYING_TAG] });

    for (const player of players) {
        const dimension = player.dimension;

        let safeY = null;
        let x, z;
        let attempts = 0;
        let lastLog = null;

        while (safeY === null && attempts < 300) {
            x = randomInt(TP_MIN_X, TP_MAX_X);
            z = randomInt(TP_MIN_Z, TP_MAX_Z);
            safeY = findSafeY(dimension, x, z, 2, 3);
            attempts++;

            // 最初の数回だけ詳細ログ
            if (attempts <= 3) {
                try {
                    const feetBlock = dimension.getBlock({ x, y: 2, z });
                    const groundBlock = dimension.getBlock({ x, y: 1, z });
                    console.warn(` x=${x} z=${z} feet=${feetBlock?.typeId ?? "null"} feetSolid=${feetBlock?.isSolid} ground=${groundBlock?.typeId ?? "null"} groundSolid=${groundBlock?.isSolid}`);
                } catch (e) {
                    console.warn(` getBlock例外: ${e}`);
                }
            }
        }

        if (safeY === null) 
            continue;

        try {
            player.teleport(
                { x: x + 0.5, y: safeY, z: z + 0.5 },
                { dimension }
            );
        } catch (e) {
            console.warn(`[game5] teleport失敗: ${player.name} - ${e}`);
        }
    }
}

function randomTeleportGame6() {
    const players = world.getPlayers({ tags: [PLAYING_TAG] });

    for (const player of players) {
        const dimension = player.dimension;

        let safeY = null;
        let x, z;
        let attempts = 0;
        while (safeY === null && attempts < 300) {
            x = randomInt(-20, 20);
            z = randomInt(-20, 20);
            safeY = findSafeY(dimension, x, z, 2, 5);
            attempts++;
        }
        if (safeY === null) continue;

        try {
            player.teleport(
                { x: x + 0.5, y: safeY, z: z + 0.5 },
                { dimension }
            );
        } catch (e) {}
    }
}

function randomTeleportGame7() {
    const players = world.getPlayers({ tags: [PLAYING_TAG] });

    for (const player of players) {
        const dimension = player.dimension;

        let safeY = null;
        let x, z;
        let attempts = 0;
        while (safeY === null && attempts < 300) {
            x = randomInt(-23, 24);
            z = randomInt(-23, 24);
            safeY = findSafeY(dimension, x, z, 6, 7);
            attempts++;
        }
        if (safeY === null) {
            console.warn(`失敗: ${player.name}  (attempts=${attempts})`);
            continue;
        }

        try {
            player.teleport(
                { x: x + 0.5, y: safeY, z: z + 0.5 },
                { dimension }
            );
        } catch (e) {}
    }
}

function randomTeleportGame18() {
    const players = world.getPlayers({ tags: [PLAYING_TAG] });

    for (const player of players) {
        const dimension = player.dimension;

        let safeY = null;
        let x, z;
        let attempts = 0;
        while (safeY === null && attempts < 300) {
            x = randomInt(-15, 15);
            z = randomInt(-15, 15);
            safeY = findSafeY(dimension, x, z, 6, 7);
            attempts++;
        }
        if (safeY === null) {
            console.warn(`失敗: ${player.name}  (attempts=${attempts})`);
            continue;
        }

        try {
            player.teleport(
                { x: x + 0.5, y: safeY, z: z + 0.5 },
                { dimension }
            );
        } catch (e) {}
    }
}

// scoreboard スコア取得用共通関数
function getTriggerScore(objective, name) {
    const participant = objective
        .getParticipants()
        .find((p) => p.displayName === name);

    if (!participant) return { participant: undefined, score: undefined };

    let score;
    try {
        score = objective.getScore(participant);
    } catch (e) {
        score = undefined;
    }

    return { participant, score };
}

// ランキング
function formatRankingMessage() {
    const participants = objPoint.getParticipants();
    const entries = participants
        .map((p) => {
            let score;
            try {
                score = objPoint.getScore(p);
            } catch (e) {
                score = undefined;
            }
            return { name: p.displayName, score };
        })
        .filter((e) => typeof e.score === "number");

    if (entries.length === 0) {
        return [
            "§l＝＝＝ランキング＝＝＝",
            "§r§cデータが見つからないため、ランキングを表示できません・・・。"
        ].join("\n");
    }

    entries.sort((a, b) => b.score - a.score);

    // 同点は同順位
    const ranks = new Array(entries.length);
    let i = 0;
    while (i < entries.length) {
        let j = i;
        while (j < entries.length && entries[j].score === entries[i].score) j++;
        for (let k = i; k < j; k++) ranks[k] = i + 1;
        i = j;
    }

    const lines = ["§l＝＝＝ランキング＝＝＝§r"];
    let blankInserted = false;

    for (let idx = 0; idx < entries.length; idx++) {
        const rank = ranks[idx];

        if (rank >= 4 && !blankInserted) {
            lines.push("");
            blankInserted = true;
        }

        const color = RANK_COLORS[rank] ?? "";
        lines.push(`§r${color}${rank}位: §r${entries[idx].name} §b${entries[idx].score}pt`);
    }

    return lines.join("\n");
}

function registerGameLogic() {
    system.runInterval(() => {
        for (const player of world.getPlayers()) {
            const { x, y, z } = player.location;
            objX.setScore(player, Math.floor(x));
            objY.setScore(player, Math.floor(y));
            objZ.setScore(player, Math.floor(z));

            const equippable = player.getComponent("minecraft:equippable");
            if (equippable) {
                if (player.hasTag("game7_give_1_o")) {
                    equippable.setEquipment("Head", new ItemStack("minecraft:copper_helmet"));
                    equippable.setEquipment("Chest", new ItemStack("minecraft:copper_chestplate"));
                    equippable.setEquipment("Legs", new ItemStack("minecraft:copper_leggings"));
                    equippable.setEquipment("Feet", new ItemStack("minecraft:copper_boots"));
                    player.removeTag("game7_give_1_o");
                } else if (player.hasTag("game7_give_2_o")) {
                    equippable.setEquipment("Head", new ItemStack("minecraft:iron_helmet"));
                    equippable.setEquipment("Chest", new ItemStack("minecraft:iron_chestplate"));
                    equippable.setEquipment("Legs", new ItemStack("minecraft:iron_leggings"));
                    equippable.setEquipment("Feet", new ItemStack("minecraft:iron_boots"));
                    player.removeTag("game7_give_2_o");
                } else if (player.hasTag("game7_give_3_o")) {
                    equippable.setEquipment("Head", new ItemStack("minecraft:diamond_helmet"));
                    equippable.setEquipment("Chest", new ItemStack("minecraft:diamond_chestplate"));
                    equippable.setEquipment("Legs", new ItemStack("minecraft:diamond_leggings"));
                    equippable.setEquipment("Feet", new ItemStack("minecraft:diamond_boots"));
                    player.removeTag("game7_give_3_o");
                } else if (player.hasTag("game7_give_4_o")) {
                    equippable.setEquipment("Head", new ItemStack("minecraft:netherite_helmet"));
                    equippable.setEquipment("Chest", new ItemStack("minecraft:netherite_chestplate"));
                    equippable.setEquipment("Legs", new ItemStack("minecraft:netherite_leggings"));
                    equippable.setEquipment("Feet", new ItemStack("minecraft:netherite_boots"));
                    player.removeTag("game7_give_4_o");
                }
            }
        }

        // ランダムTP(adventure PVP)
        const tpStatus = getTriggerScore(objGame, TRIGGER_NAME);
        if (tpStatus.participant && tpStatus.score === 1) {
            randomTeleportPlayingPlayers();
            objGame.setScore(tpStatus.participant, 0);
        }

        // ランダムTP(TNT TAG)
        const tpStatus6 = getTriggerScore(objGame, TRIGGER_NAME_6);
        if (tpStatus6.participant && tpStatus6.score === 1) {
            randomTeleportGame6();
            objGame.setScore(tpStatus6.participant, 0);
        }

        const { score: gameScore } = getTriggerScore(objGame, SELECT_GAME_NAME);

        // ランダムTP (Drop PVP)
        const tpStatus7 = getTriggerScore(objGame, TRIGGER_NAME_7);
        if (tpStatus7.participant && tpStatus7.score === 1) {
            randomTeleportGame7();
            objGame.setScore(tpStatus7.participant, 0);
        }

        // ランダムTP (穴落とし)
        const tpStatus18 = getTriggerScore(objGame, TRIGGER_NAME_18);
        if (tpStatus18.participant && tpStatus18.score === 1) {
            randomTeleportGame18();
            objGame.setScore(tpStatus18.participant, 0);
        }

        // コウモリ召喚 (Drop PVP)
        if (gameScore === 7) {
            const dropStatus = getTriggerScore(objGame, TRIGGER_NAME_DROP);
            if (dropStatus.score === 1) {
                for (let i = 0; i < 24; i++) {
                    const rx = randomInt(-23, 24);
                    const rz = randomInt(-23, 24);
                    world.getDimension("overworld").spawnEntity("minecraft:bat", { x: rx + 0.5, y: 5, z: rz + 0.5 });
                }
                objGame.setScore(dropStatus.participant, 0);
            } else if (dropStatus.score === 2) {
                game7_bat_timer += TICK_INTERVAL;
                if (game7_bat_timer >= 60) {
                    const rx = randomInt(-23, 24);
                    const rz = randomInt(-23, 24);
                    world.getDimension("overworld").spawnEntity("minecraft:bat", { x: rx + 0.5, y: 5, z: rz + 0.5 });
                    game7_bat_timer = 0;
                }
            }
        }

        // 初期装備 (Drop PVP)
        const syokiStatus = getTriggerScore(objGame, TRIGGER_SYOKI);
        if (syokiStatus.participant && syokiStatus.score === 1) {
            const players = world.getPlayers({ tags: [PLAYING_TAG] });

            for (const player of players) {
                // 装備
                const equippable = player.getComponent("minecraft:equippable");
                if (equippable) {
                    equippable.setEquipment("Head", new ItemStack("minecraft:leather_helmet"));
                    equippable.setEquipment("Chest", new ItemStack("minecraft:leather_chestplate"));
                    equippable.setEquipment("Legs", new ItemStack("minecraft:leather_leggings"));
                    equippable.setEquipment("Feet", new ItemStack("minecraft:leather_boots"));
                }

                // 配布
                const inventory = player.getComponent("minecraft:inventory").container;
                if (inventory) {
                    // 木の剣
                    inventory.addItem(new ItemStack("minecraft:wooden_sword", 1));

                    // 無限弓
                    const bow = new ItemStack("minecraft:bow", 1);
                    const enchantable = bow.getComponent("minecraft:enchantable");
                    if (enchantable) {
                        const enchantmentType = EnchantmentTypes.get("infinity");
                        if (enchantmentType) {
                            enchantable.addEnchantment({ type: enchantmentType, level: 1 });
                        }
                    }
                    inventory.addItem(bow);

                    // 矢
                    inventory.addItem(new ItemStack("minecraft:arrow", 1));
                }
            }
            objGame.setScore(syokiStatus.participant, 0);
        }

        // game11 投票集計
        const g11Status = getTriggerScore(objGame, TRIGGER_NAME_11);
        if (g11Status.participant && g11Status.score === 1) {
            const dimension = world.getDimension("overworld");

            let maxScore = -Infinity;
            let totalVotes = 0;
            const colorScores = [];

            for (const color of GAME11_COLORS) {
                const { score: colorScore } = getTriggerScore(objGame, `game11_${color.key}`);
                const s = colorScore ?? 0;
                colorScores.push({ key: color.key, score: s });
                totalVotes += s;
                if (s > maxScore) {
                    maxScore = s;
                }
            }

            if (totalVotes === 0) {
                // 1票もなかった場合
                try {
                    dimension.runCommand(`scoreboard players set game11_x game 1`);
                } catch (e) {

                }
            } else {
                // 同点→該当色をすべて1
                const winners = colorScores.filter((c) => c.score === maxScore);
                for (const winner of winners) {
                    try {
                        dimension.runCommand(`scoreboard players set game11_${winner.key}_a game 1`);
                    } catch (e) {

                    }
                }
            }

            objGame.setScore(g11Status.participant, 0);
        }
    }, TICK_INTERVAL);

    // game4 (静止TNT消去)
system.runInterval(() => {
    const { score: gameScore } = getTriggerScore(objGame, SELECT_GAME_NAME);
    if (gameScore !== 4) {
        game4StationaryData.clear();
        return;
    }

    const dimension = world.getDimension("overworld");
    const players = world.getPlayers({ tags: [PLAYING_TAG] });
    const EPS = 0.01; // 浮動小数点誤差の許容範囲
    const STILL_TICKS_THRESHOLD = 10; // 0.5秒 = 10tick

    for (const player of players) {
        const loc = player.location;
        const prev = game4StationaryData.get(player.id);

        const moved =
            !prev ||
            Math.abs(loc.x - prev.x) > EPS ||
            Math.abs(loc.y - prev.y) > EPS ||
            Math.abs(loc.z - prev.z) > EPS;

        if (moved) {
            game4StationaryData.set(player.id, { x: loc.x, y: loc.y, z: loc.z, stillTicks: 0 });
            continue;
        }

        // 静止中: TICK_INTERVALごとに加算
        prev.stillTicks += TICK_INTERVAL;

        if (prev.stillTicks >= STILL_TICKS_THRESHOLD) {
            // プレイヤー周辺のTNTを消去
            try {
                const minX = loc.x - 1.5;
                const maxX = loc.x + 1.5;
                const minZ = loc.z - 1.5;
                const maxZ = loc.z + 1.5;
                const minY = loc.y - 1;
                const maxY = loc.y;

                const tnts = dimension.getEntities({
                    type: "minecraft:tnt",
                    location: { x: minX, y: minY, z: minZ },
                    volume: { x: maxX - minX, y: maxY - minY, z: maxZ - minZ }
                });

                for (const tnt of tnts) {
                    tnt.remove();
                }
            } catch (e) {
                console.warn(`$失敗: ${e}`);
            }

            // 連続削除を避けたい場合はリセット(不要なら削除してOK)
            prev.stillTicks = 0;
        }

        game4StationaryData.set(player.id, prev);
    }
}, TICK_INTERVAL);

    // game10 (金床避け)
    system.runInterval(() => {
        const status = getTriggerScore(objGame, TRIGGER_NAME_10);

        if (status.score === 1) {
            const dimension = world.getDimension("overworld");
            const armorStands = dimension.getEntities({
                type: "minecraft:armor_stand",
                name: "game10_random"
            });

            for (const as of armorStands) {
                // x: -4~4, z: -4~4, y: -4
                const rx = randomInt(-4, 4);
                const rz = randomInt(-4, 4);

                try {
                    as.teleport(
                        { x: rx + 0.5, y: -4, z: rz + 0.5 },
                        { dimension }
                    );
                } catch (e) {

                }
            }
        }
    }, 2);

    // game12 (TNT避け)
    system.runInterval(() => {
        const status = getTriggerScore(objGame, TRIGGER_NAME_12);

        if (status.score === 1) {
            const dimension = world.getDimension("overworld");
            const armorStands = dimension.getEntities({
                type: "minecraft:armor_stand",
                name: "game12_random"
            });

            for (const as of armorStands) {
                // x: -8~8, z: -8~8, y: -4
                const rx = randomInt(-8, 8);
                const rz = randomInt(-8, 8);

                try {
                    as.teleport(
                        { x: rx + 0.5, y: -4, z: rz + 0.5 },
                        { dimension }
                    );
                } catch (e) {

                }
            }
        }
    }, TICK_INTERVAL);

        // game17 (崩れる床で生き延びろ)
    system.runInterval(() => {
        const status = getTriggerScore(objGame, TRIGGER_NAME_17);

        if (status.score === 1) {
            const dimension = world.getDimension("overworld");
            const armorStands = dimension.getEntities({
                type: "minecraft:armor_stand",
                name: "game17_random"
            });

            for (const as of armorStands) {
                // x: -8~8, z: -8~8, y: -4
                const rx = randomInt(-8, 8);
                const rz = randomInt(-8, 8);

                try {
                    as.teleport(
                        { x: rx + 0.5, y: -4, z: rz + 0.5 },
                        { dimension }
                    );
                } catch (e) {

                }
            }
        }
    }, 0);

        // game22 (マグマノックバック)
    system.runInterval(() => {
        const status = getTriggerScore(objGame, TRIGGER_NAME_22);

        if (status.score === 1) {
            const dimension = world.getDimension("overworld");
            const armorStands = dimension.getEntities({
                type: "minecraft:armor_stand",
                name: "game22_random"
            });

            for (const as of armorStands) {
                // x: -7~7, z: -7~7, y: -4
                const rx = randomInt(-7, 7);
                const rz = randomInt(-7, 7);

                try {
                    as.teleport(
                        { x: rx + 0.5, y: -4, z: rz + 0.5 },
                        { dimension }
                    );
                } catch (e) {

                }
            }
        }
    }, 2);

        // game24 (モンスターバトル)
    system.runInterval(() => {
        const status = getTriggerScore(objGame, TRIGGER_NAME_24);

        if (status.score === 1) {
            const dimension = world.getDimension("overworld");
            const armorStands = dimension.getEntities({
                type: "minecraft:armor_stand",
                name: "game24_random"
            });

            for (const as of armorStands) {
                // x: -10~10, z: -10~10, y: -4
                const rx = randomInt(-10, 10);
                const rz = randomInt(-10, 10);

                try {
                    as.teleport(
                        { x: rx + 0.5, y: -4, z: rz + 0.5 },
                        { dimension }
                    );
                } catch (e) {

                }
            }
        }
    }, 5);

    // ランキング表示
    system.runInterval(() => {
        const status = getTriggerScore(objGame, TRIGGER_NAME_RANKING);

        if (status.participant && status.score === 1) {
            world.sendMessage(formatRankingMessage());
            objGame.setScore(status.participant, 0);
        }
    }, TICK_INTERVAL);

    // 死亡時
    world.afterEvents.entityDie.subscribe((event) => {
        const deadEntity = event.deadEntity;
        const damageSource = event.damageSource;
        if (deadEntity.typeId !== "minecraft:player") return;

        const { score } = getTriggerScore(objGame, SELECT_GAME_NAME);
        const victimName = deadEntity.nameTag;
        const killer = damageSource.damagingEntity;

        // 5 adventure PVP
        if (score === 5) {
            deadEntity.addTag("game5_died");
            system.run(() => {
                if (killer) {
                    const killerName = killer.nameTag || killer.typeId;
                    world.sendMessage(`${victimName} が ${killerName} に倒された`);
                } else {
                    world.sendMessage(`${victimName} は自由を求めた結果死亡した`);
                }
            });
        }

        // 7 Drop PVP
        else if (score === 7) {
            deadEntity.addTag("game7_died");
            system.run(() => {
                if (killer) {
                    const killerName = killer.nameTag || killer.typeId;
                    world.sendMessage(`${killerName} が ${victimName} を倒した`);
                } else {
                    world.sendMessage(`${victimName} は奈落に落ちた`);
                }
            });
        }

        // 10 金床避け
        else if (score === 10) {
            deadEntity.addTag("game10_died");
            system.run(() => {
                if (killer) {
                    const killerName = killer.nameTag || killer.typeId;
                    world.sendMessage(`${killerName} が ${victimName} を倒した`);
                } else {
                    world.sendMessage(`${victimName} は金床に押しつぶされた`);
                }
            });
        }

        // 12 TNT避け
        else if (score === 12) {
            deadEntity.addTag("game12_died");
            system.run(() => {
                if (killer) {
                    const killerName = killer.nameTag || killer.typeId;
                    world.sendMessage(`${killerName} が ${victimName} を倒した`);
                } else {
                    world.sendMessage(`${victimName} はTNTの爆発に巻き込まれた`);
                }
            });
        }

        // 21 Warden Escape
        else if (score === 21) {
            deadEntity.addTag("game21_died");
            system.run(() => {
                if (killer) {
                    const killerName = killer.nameTag || killer.typeId;
                    world.sendMessage(`${killerName} が ${victimName} を倒した`);
                } else {
                    world.sendMessage(`${victimName} はウォーデンに殺害された`);
                }
            });
        }

        // 24 モンスターバトル
        else if (score === 24) {
            deadEntity.addTag("game24_died");
            system.run(() => {
                if (killer) {
                    const killerName = killer.nameTag || killer.typeId;
                    world.sendMessage(`${killerName} が ${victimName} を倒した`);
                } else {
                    world.sendMessage(`${victimName} は死亡した`);
                }
            });
        }
    });

    world.afterEvents.playerLeave.subscribe((event) => {
        const name = event.playerName;

        objX.removeParticipant(name);
        objY.removeParticipant(name);
        objZ.removeParticipant(name);
    });

    // Drop PVP 右クリック検知
    world.afterEvents.itemUse.subscribe((event) => {
        const { source: player, itemStack } = event;
        const { score: gameScore } = getTriggerScore(objGame, SELECT_GAME_NAME);

        if (gameScore === 7 && player.hasTag(PLAYING_TAG)) {
            const itemId = itemStack.typeId;

            if (itemId === "minecraft:copper_ingot") {
                player.addTag("game7_give_1");
            } else if (itemId === "minecraft:iron_ingot") {
                player.addTag("game7_give_2");
            } else if (itemId === "minecraft:diamond") {
                player.addTag("game7_give_3");
            } else if (itemId === "minecraft:netherite_ingot") {
                player.addTag("game7_give_4");
            }
        }
    });

    const TARGET_ITEM = "minecraft:tropical_fish";
    const KNOCKBACK_LEVEL = 3;

    world.afterEvents.entityHitEntity.subscribe((event) => {
        const { damagingEntity, hitEntity } = event;

        // TNT TAG
        const { score: gameScore } = getTriggerScore(objGame, SELECT_GAME_NAME);
        if (gameScore === 6) {
            if (damagingEntity.typeId === "minecraft:player" && hitEntity.typeId === "minecraft:player") {

                if (damagingEntity.hasTag("game6_oni") && hitEntity.hasTag("playing") && !hitEntity.hasTag("died")) {
                    hitEntity.addTag("game6_oni");
                    damagingEntity.removeTag("game6_oni");

                    hitEntity.sendMessage(`§c${damagingEntity.nameTag} にタッチされました！`);
                    damagingEntity.sendMessage(`§a${hitEntity.nameTag} に鬼を交代しました！`);
                }
            }
        }

if (damagingEntity.typeId !== "minecraft:player") return;
        if (damagingEntity.getEffect("minecraft:weakness")) return;

        const equippable = damagingEntity.getComponent("minecraft:equippable");
        const heldItem = equippable?.getEquipment("Mainhand");

        if (heldItem?.typeId !== TARGET_ITEM) return;

        const dx = hitEntity.location.x - damagingEntity.location.x;
        const dz = hitEntity.location.z - damagingEntity.location.z;
        const length = Math.sqrt(dx * dx + dz * dz) || 1;
        
        // 元のコードの計算式を維持
        const horizontalStrength = 0.4 + KNOCKBACK_LEVEL * 0.5;
        const verticalStrength = 0.4;

        system.run(() => {
            try {
                hitEntity.applyKnockback(
                    {
                        x: (dx / length) * horizontalStrength,
                        z: (dz / length) * horizontalStrength,
                    },
                    verticalStrength
                );
            } catch (e) {
                console.warn(`applyKnockback failed: ${e}`);
            }
        });
    });



// 12 TNT避け
world.afterEvents.entitySpawn.subscribe((event) => {
    const entity = event.entity;
    if (entity.typeId !== "minecraft:ender_crystal") return;

    const { score } = getTriggerScore(objGame, SELECT_GAME_NAME);

    if (score === 12) {
        try {
            entity.applyDamage(1000);
        } catch (e) {

        }
    }
});

// 19 色塗りバトル
world.afterEvents.entitySpawn.subscribe((event) => {
    const entity = event.entity;
    if (entity.typeId !== "minecraft:snowball") return;

    const { score } = getTriggerScore(objGame, SELECT_GAME_NAME);
    if (score !== 19) return;

    const projectile = entity.getComponent("minecraft:projectile");
    const owner = projectile?.owner;

    if (!owner || owner.typeId !== "minecraft:player") return;

    if (owner.hasTag("game19_white")) {
        entity.addTag("white");
    } else if (owner.hasTag("game19_black")) {
        entity.addTag("black");
    }
});

    // ここからUI
world.beforeEvents.itemUse.subscribe((event) => {
    const player = event.source;

    if (event.itemStack.typeId === "mmg:vote") {
        system.run(() => {
            const { score: gameScore } = getTriggerScore(objGame, SELECT_GAME_NAME);

if (gameScore === 11) {
    voteUI(player);
} else if (gameScore === 14) {
    const { score: sScore } = getTriggerScore(objGame, "game14_s");
    if (sScore === 1) {
        voteMobUI(player);
    } else {
        player.sendMessage("§c今は投票期間ではありません");
    }
} else {
    player.sendMessage("§c今はこのアイテムを使用できません");
}
        });
    }
})};



// メイン処理

// game: 11

function voteUI(player) {
    const visibleColors = GAME11_COLORS.filter((c) => {
        const { score } = getTriggerScore(objGame, `game11_${c.key}_a`);
        return score !== 2;
    });

    if (visibleColors.length === 0) {
        player.sendMessage("§cこのアイテムは現在使えません");
        return;
    }

    const gui = new ActionFormData()
        .title("投票")
        .body("消したいブロックを選択してください\n§7票数が一番多いブロックが消えます");

    for (const c of visibleColors) {
        gui.button(c.label);
    }

    gui.show(player).then((result) => {
        if (result.canceled) return;

        const selected = visibleColors[result.selection];
        if (!selected) return;

        const { score: g11aScore } = getTriggerScore(objGame, "game11_a");
        if (g11aScore !== 1) {
            if (g11aScore === 2 || g11aScore === 3 || g11aScore === 4) {
                player.sendMessage("§cすでに投票は終了しています");
            } else {
                player.sendMessage("§c不明なエラーが発生しました");
            }
            return;
        }

        player.sendMessage(`${selected.label}を選択しました。`);

        // タグの付け替え処理
        for (const c of GAME11_COLORS) {
            if (c.key === selected.key) {
                player.addTag(`game11_${c.key}`);
            } else {
                player.removeTag(`game11_${c.key}`);
            }
        }
    });
}

// どうぶつリレー 投票
function voteMobUI(player) {
    const gui = new ActionFormData()
        .title("投票")
        .body("勝ちそうなモブを投票してください");

    for (const mob of GAME14_MOBS) {
        gui.button(mob.label);
    }

    gui.show(player).then((result) => {
        if (result.canceled) return;

        const selectedMob = GAME14_MOBS[result.selection];
        if (!selectedMob) return;

        // 投票期間の再確認
        const { score: sScore } = getTriggerScore(objGame, "game14_s");
        if (sScore !== 1) {
            player.sendMessage("§c投票期間が終了しました");
            return;
        }

        // タグの重複防止
        for (const mob of GAME14_MOBS) {
            player.removeTag(mob.tag);
        }

        // 選択したタグを付与
        player.addTag(selectedMob.tag);
        player.sendMessage(`§a${selectedMob.label}に投票しました。`);
    });
}

// その他スクリプト

// game23 - 村人数え
// 上下アイテム右クリックで動作
world.afterEvents.itemUse.subscribe(ev => {
    const player = ev.source;
    if (!player) return;

    if (ev.itemStack.typeId == "mmg:up"){
        player.runCommand("execute if score selectgame game matches 23 if score game23_s game matches 1 run scoreboard players add @s game23_a 1");
        player.runCommand("execute if score selectgame game matches 23 if score game23_s game matches 1 run playsound note.snare @s ~~~ 1 1.2 1");
        player.runCommand('execute if score selectgame game matches 23 if score game23_s game matches 2 run tellraw @s {"rawtext":[{"text":"§cスコアの変更はできません"}]}');
    }
    else if (ev.itemStack.typeId == "mmg:down"){
        player.runCommand("execute if score selectgame game matches 23 if score game23_s game matches 1 run scoreboard players add @s game23_a -1");
        player.runCommand("execute if score selectgame game matches 23 if score game23_s game matches 1 run playsound note.snare @s ~~~ 1 0.8 1");
        player.runCommand('execute if score selectgame game matches 23 if score game23_s game matches 2 run tellraw @s {"rawtext":[{"text":"§cスコアの変更はできません"}]}');
    }
});

// game24 - モンスターバトル
world.afterEvents.entityDie.subscribe((event) => {
    if (!objGame || !objGame24Kill) return;

    const deadEntity = event.deadEntity;
    const damageSource = event.damageSource;

    if (deadEntity.typeId === "minecraft:player") return;

    const killer = damageSource.damagingEntity;
    if (!killer || killer.typeId !== "minecraft:player") return;

    const { score: gameScore } = getTriggerScore(objGame, SELECT_GAME_NAME);
    if (gameScore !== 24) return;

    objGame24Kill.addScore(killer, 1);
});

// game24
// 最もモンスターを倒しているものにtag付与
system.runInterval(() => {
    if (!objGame || !objGame24Kill) return; // 初期化前の安全策

    const { score: gameScore } = getTriggerScore(objGame, SELECT_GAME_NAME);
    if (gameScore !== 24) return;

    // 現在の最高スコアを集計(0は対象外なので初期値0)
    let maxScore = 0;
    for (const participant of objGame24Kill.getParticipants()) {
        let s;
        try {
            s = objGame24Kill.getScore(participant);
        } catch (e) {
            continue;
        }
        if (typeof s === "number" && s > maxScore) {
            maxScore = s;
        }
    }

    for (const player of world.getPlayers()) {
        let myScore;
        try {
            myScore = objGame24Kill.getScore(player);
        } catch (e) {
            myScore = undefined;
        }

        // スコアが0、または未参加なら絶対に付与しない
        if (typeof myScore !== "number" || myScore <= 0) {
            if (player.hasTag("game24_max")) player.removeTag("game24_max");
            continue;
        }

        if (myScore === maxScore) {
            // トップ(逆転した側) → タグ付与
            if (!player.hasTag("game24_max")) player.addTag("game24_max");
        } else {
            // トップから外れた(抜かされた側) → タグ消去
            if (player.hasTag("game24_max")) player.removeTag("game24_max");
        }
    }
}, TICK_INTERVAL);

// セットアップ
// スローダウン問題改善
let gameLogicStarted = false;

function startGameLogic() {
    if (gameLogicStarted) return;
    gameLogicStarted = true;

    system.runTimeout(() => {
        objX = ensureObjective("player_x");
        objY = ensureObjective("player_y");
        objZ = ensureObjective("player_z");
        objGame = ensureObjective("game");
        objPoint = ensureObjective("point");
        objGame24Kill = ensureObjective("game24_kill");

        registerGameLogic();
    }, 100);
}

// ワールド起動時
world.afterEvents.playerSpawn.subscribe((event) => {
    if (!event.initialSpawn) return;
    startGameLogic();
});

// /reload 対策
system.runTimeout(() => {
    if (world.getAllPlayers().length > 0) {
        startGameLogic();
    }
}, 1);

// コマンド

server.system.beforeEvents.startup.subscribe(ev => {
    ev.customCommandRegistry.registerCommand({
        name:"mmg:spectator",
        description:"観戦中なら、スペクテイターモードになれます",
        permissionLevel : server.CommandPermissionLevel.Any,
        mandatoryParameters:[
        ],
        optionalParameters:[
        ]
    },(origin, arg) => {
        server.system.runTimeout(() => {
            origin.sourceEntity.runCommand("tag @s add game_spectator")
        },1)
    })
})