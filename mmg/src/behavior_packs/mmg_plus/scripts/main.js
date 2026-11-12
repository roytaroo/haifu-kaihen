// MMG Plus: ミニゲームの抽選(ON/OFF)・追加ゲーム(25〜27)・ランキング掲示板
// 元のワールドとのつなぎ:
//   select_game.mcfunction → scriptevent mmgplus:select → ここで selectgame を決めて function select_game_body
//   select_game_body(25以上) → scriptevent mmgplus:prep → 会場を作って game_ready=1
//   game_start(25以上)      → scriptevent mmgplus:start → ゲーム → point 付与 → function finish_game → game_next_ready=1
//   設定メニュー(gameee.js)  → scriptevent mmgplus:games_ui / mmgplus:board_ui
import { world, system, GameMode } from "@minecraft/server";
import { ActionFormData, ModalFormData, MessageFormData, uiManager } from "@minecraft/server-ui";

const GAMES = [
    "Escape Lava", "熱帯魚相撲", "High and Low", "TNT RUN", "Adventure PVP", "TNT TAG", "Drop PVP", "降下デスマッチ",
    "逆らえ！", "金床避け", "読みぶろぱ", "TNT避け", "アスレチック", "どうぶつリレー", "Block Party", "鉱石バトル",
    "崩れる床で生き延びろ", "穴落とし", "色塗りバトル", "クラフトマスター", "Warden Escape", "マグマノックバック", "村人数え", "モンスターバトル",
    "計算早押し", "色の記憶", "椅子取りゲーム", "宝探しプール", "ファイアバー", "ボートレース", "ピッタリ止め", "ニワトリ集め",
    "一番多い色は？", "早押し反射", "矢の雨", "隕石よけ", "押し寄せる壁", "障害物ダッシュ", "配置の記憶",
    "レーザー回避", "しっぽ取り", "ものまねポーズ", "ピクセルアート再現", "卵キャッチ", "コイン噴水", "ふくらむ風船", "まっくらスイカ割り", "下がる天井", "風船割り合戦",
    "ボヨンボール", "ワニの歯", "コマぶつけ", "旗あげゲーム", "お皿バランス", "大玉ころがし", "ロデオ", "バンパーカー", "アスレチック(5コース)",
]; // 番号 = 添字 + 1
const FIRST_PLUS = 25;
// だいきの指示で消したゲーム(抽選・ON/OFF・ランキングに出さない)
const REMOVED = [3, 8, 10, 11, 12, 13, 16, 17]; // 13 は「アスレチック(5コース)」(58)に置きかえ
const ACTIVE = GAMES.map((_, i) => i + 1).filter((id) => !REMOVED.includes(id));
// だいきの指示で、初めは OFF(ON/OFF で ON にはできる)。全ゲーム順番モードには入れない
const DEFAULT_OFF = [1, 2, 4, 5, 6, 7, 14, 15, 18, 20, 22];
const SEQ_IDS = ACTIVE.filter((id) => !DEFAULT_OFF.includes(id));
function offList() {
    // 前に保存した設定にも、初めから OFF のゲームを一度だけ足す
    if ((load("offv", 0)) < 2) { save("off", [...new Set([...load("off", []), ...DEFAULT_OFF])]); save("offv", 2); }
    return load("off", []);
}
const SPECTATOR = GameMode.Spectator ?? GameMode.spectator;
const ADVENTURE = GameMode.Adventure ?? GameMode.adventure;
const dim = () => world.getDimension("overworld");
const cmd = (c) => { try { dim().runCommand(c); } catch (e) { console.warn(`[mmg_plus] ${c}: ${e}`); } };
const wait = (ticks) => new Promise((r) => system.runTimeout(r, ticks));
const rand = (a, b) => a + Math.floor(Math.random() * (b - a + 1));

// ===== 保存 =====
function load(key, def) {
    try { const v = world.getDynamicProperty(key); return typeof v === "string" ? JSON.parse(v) : def; } catch { return def; }
}
const save = (key, v) => world.setDynamicProperty(key, JSON.stringify(v));

// ===== スコア =====
const obj = (name) => world.scoreboard.getObjective(name);
function score(objective, name) {
    const o = obj(objective); if (!o) return undefined;
    try { return o.getScore(name); } catch { return undefined; }
}
const setScore = (objective, name, v) => obj(objective)?.setScore(name, v);
const level = () => Math.min(5, Math.max(1, score("game", "level") ?? 1));
const playing = () => world.getPlayers({ tags: ["playing"] });
// BOT(mmg_bot パック)。強さ 0〜2 は mmg_bot が setting の bot_strength に入れる
const isBot = (p) => p.hasTag("mmgbot");
const botNames = new Set();
const botStr = () => score("setting", "bot_strength") ?? 1;
const chance = (weak, normal, strong) => Math.random() < [weak, normal, strong][botStr()];

// ===== 抽選(OFFのゲームを除く) =====
system.afterEvents.scriptEventReceive.subscribe((ev) => {
    const p = ev.sourceEntity?.typeId === "minecraft:player" ? ev.sourceEntity : undefined;
    switch (ev.id) {
        case "mmgplus:select": selectGame(); break;
        case "mmgplus:prep": prepGame(); break;
        case "mmgplus:start": startGame(); break;
        case "mmgplus:games_ui": if (p) gamesUI(p); break;
        case "mmgplus:board_ui": if (p) boardUI(p); break;
    }
});

function selectGame() {
    // 全ゲーム順番モード: 決まった順に1回ずつ
    const seq = load("seq", null);
    if (seq && seq.i < seq.ids.length) {
        const id = seq.ids[seq.i++]; save("seq", seq);
        world.sendMessage(`§e[全ゲーム順番モード] ${seq.i} / ${seq.ids.length}: ${GAMES[id - 1]}`);
        setScore("game", "selectgame", id);
        cmd("function select_game_body");
        return;
    }
    const off = offList();
    let ids = ACTIVE.filter((id) => !off.includes(id));
    if (ids.length === 0) ids = ACTIVE;
    // 同じゲームが2回続かないように(選べるのが1つの時は別)
    const last = score("game", "selectgame");
    if (ids.length > 1) ids = ids.filter((id) => id !== last);
    setScore("game", "selectgame", ids[rand(0, ids.length - 1)]);
    cmd("function select_game_body");
}

async function gamesUI(player) {
    const off = offList();
    const form = new ModalFormData().title("ミニゲームのON/OFF");
    form.toggle(`§e全ゲーム順番モードで試合を始める§r\n§7(バグ確認用: ${SEQ_IDS.length}ゲームを1回ずつ順番に。下のON/OFFは関係なし)`, { defaultValue: false });
    ACTIVE.forEach((id) => form.toggle(`${id}. ${GAMES[id - 1]}${id >= FIRST_PLUS ? " §e(追加)" : ""}`, { defaultValue: !off.includes(id) }));
    const res = await form.show(player);
    if (res.canceled) return;
    const [seqOn, ...vals] = res.formValues;
    if (seqOn) {
        save("seq", { ids: SEQ_IDS, i: 0 });
        setScore("setting", "round", SEQ_IDS.length); setScore("setting", "round-auto", 0);
        player.sendMessage(`§e全ゲーム順番モードで始めます(${SEQ_IDS.length}ゲーム)`);
        cmd("function main_start");
        return;
    }
    const next = [];
    vals.forEach((on, i) => { if (!on) next.push(ACTIVE[i]); });
    if (next.length === ACTIVE.length) { player.sendMessage("§c全部OFFにはできません。1つ以上ONにしてください"); return; }
    save("off", next);
    player.sendMessage(`§aミニゲームの設定を保存しました(ON ${ACTIVE.length - next.length} / OFF ${next.length})`);
}

// ===== 追加ゲームの共通処理 =====
// 会場は元のゲームと同じ場所(x -24〜25, z -49〜50、床は y=0 の黒コンクリート)。y=0 より下はコマンドの部屋なので、
// 床を落下するブロック(砂など)にしない・y=0 より下は触らない
const run = { id: 0, active: false };
const aborted = () => !run.active || score("game", "playing") !== 1 || score("game", "selectgame") !== run.id;

async function prepGame() {
    const id = score("game", "selectgame");
    if (id === 26) buildSimon();
    if (id === 27) buildChairs();
    if (id === 28) buildPool();
    if (id === 29) buildFirebar();
    if (id === 30) buildRace();
    if (id === 32) buildFarm();
    if (id === 33 || id === 34) buildWallRoom();
    if (id === 35) buildArena(9, "smooth_stone", "glass", 4);
    if (id === 36) buildArena(10, "basalt", "glass", 3);
    if (id === 37) buildWalls();
    if (id === 38) buildDash();
    ({
        40: () => buildArena(9, "gray_concrete", "glass", 4), 41: () => buildArena(10, "grass_block", "oak_fence", 2), 42: () => buildArena(7, "smooth_quartz", "glass", 3),
        44: () => buildArena(10, "white_concrete", "glass", 3), 45: () => buildArena(11, "smooth_sandstone", "glass", 3), 46: () => buildArena(8, "pink_concrete", "glass", 3),
        47: () => buildArena(10, "grass_block", "oak_fence", 2), 48: () => buildArena(7, "stone_bricks", "glass", 8), 49: () => buildArena(10, "light_blue_concrete", "glass", 4),
        50: () => buildArena(9, "smooth_stone", "glass", 8), 51: () => buildArena(12, "smooth_sandstone", "glass", 3), 52: () => buildRing(10, "polished_andesite"),
        53: () => clearArena(), 54: () => buildStraight("white_concrete", false), 55: () => buildStraight("lime_concrete", true), 56: () => buildArena(12, "coarse_dirt", "oak_fence", 2),
        57: () => buildRing(11, "light_gray_concrete"), 58: () => buildCourse(),
    })[id]?.();
    cmd("tag @a remove mmgplus_out");
    if (id === 28) cmd("tp @a[tag=playing] 0 7 0");
    else if (id === 29) cmd("tp @a[tag=playing] 0 1 5");
    else if (id === 37) cmd("tp @a[tag=playing] 0 1 6");
    else if (id === 48) cmd("tp @a[tag=playing] 0 4 0");
    else if (id === 54 || id === 55) cmd("tp @a[tag=playing] 0 1 -44");
    else if (id === 38) cmd("tp @a[tag=playing] 0 1 -44");
    else if (id === 30) cmd(`tp @a[tag=playing] ${raceX(RACE_START - 3) + 0.5} 1 ${RACE_START - 3} facing ${raceX(0)} 1 0`);
    else cmd("tp @a[tag=playing] 0 1 0");
    await wait(40);
    setScore("game", "game_ready", 1);
}

async function startGame() {
    const id = score("game", "selectgame");
    if (run.active) return; // game_start は何度か呼ばれる
    Object.assign(run, { id, active: true });
    let winners = [];
    try {
        if (id === 25) winners = await gameQuiz();
        if (id === 26) winners = await gameSimon();
        if (id === 27) winners = await gameChairs();
        if (id === 28) winners = await gamePool();
        if (id === 29) winners = await gameFirebar();
        if (id === 30) winners = await gameRace();
        if (id === 31) winners = await gameStop();
        if (id === 32) winners = await gameFarm();
        if (id === 33) winners = await gameColors();
        if (id === 34) winners = await gameReflex();
        if (id === 35) winners = await gameArrows();
        if (id === 36) winners = await gameMeteor();
        if (id === 37) winners = await gameWalls();
        if (id === 38) winners = await gameDash();
        if (id === 39) winners = await gameMemory();
        const G6 = { 40: gameLaser, 41: gameTails, 42: gamePose, 43: gamePixel, 44: gameEggs, 45: gameCoins, 46: gameBalloon, 47: gameMelon, 48: gameCeiling, 49: gameBalloonWar,
            50: gameBoyon, 51: gameCroc, 52: () => gameBumper("mmgplus:top", 10, "コマぶつけ"), 53: gameFlags, 54: gamePlates, 55: gameBigball, 56: gameRodeo, 57: () => gameBumper("mmgplus:car", 11, "バンパーカー"), 58: gameCourse };
        if (G6[id]) winners = await G6[id]();
    } catch (e) {
        console.warn(`[mmg_plus] game${id}: ${e}`);
        // 管理者にだけエラーを見せる(直す時の手がかり)
        for (const p of world.getPlayers()) if (p.hasTag("admin") || p.hasTag("host")) p.sendMessage(`§7[mmg_plus] ${GAMES[id - 1]} でエラー: ${e}`);
    }
    if (aborted()) { run.active = false; return; }
    run.active = false;
    finishGame(winners);
}

async function finishGame(winners) {
    const names = new Set(winners.map((p) => p.name));
    for (const p of playing()) {
        if (p.getGameMode() === SPECTATOR) p.setGameMode(ADVENTURE);
        if (names.has(p.name)) {
            obj("point")?.addScore(p, 1);
            p.sendMessage("§a1ポイント獲得！");
            p.addTag("game_finish_a");
        } else p.sendMessage("§c勝てませんでした...");
    }
    cmd("ride @a stop_riding");
    cmd("function finish_game");
    clearArena();
    await wait(60);
    setScore("game", "game_next_ready", 1);
}

function out(p, msg) {
    p.addTag("mmgplus_out");
    p.sendMessage(msg);
    p.setGameMode(SPECTATOR);
    cmd(`playsound note.bass "${p.name}"`);
}
const alive = () => playing().filter((p) => !p.hasTag("mmgplus_out"));
// 半径 r の円の外周に壁
function ring(r, h, block, y = 1) {
    for (let a = 0; a < 360; a += 2) {
        const x = Math.round(Math.cos((a * Math.PI) / 180) * r), z = Math.round(Math.sin((a * Math.PI) / 180) * r);
        cmd(`fill ${x} ${y} ${z} ${x} ${y + h - 1} ${z} ${block}`);
    }
}
// 半径 r の円の床
function disc(r, block, y = 0) {
    for (let z = -r; z <= r; z++) { const w = Math.floor(Math.sqrt(r * r - z * z)); cmd(`fill ${-w} ${y} ${z} ${w} ${y} ${z} ${block}`); }
}
const CUSTOM = ["mmgplus:chair", "mmgplus:treasure_gold", "mmgplus:treasure_diamond", "mmgplus:treasure_emerald", "mmgplus:fireball",
    "mmgplus:balloon", "mmgplus:coin", "mmgplus:egg", "mmgplus:golden_egg", "mmgplus:melon", "mmgplus:croc", "mmgplus:tooth", "mmgplus:top", "mmgplus:car", "mmgplus:bigball", "mmgplus:boyon", "mmgplus:bull", "mmgplus:plates", "mmgplus:tail", "mmgplus:laser"];
function clearArena() {
    cmd("fill -24 1 -49 25 8 0 air");
    cmd("fill -24 1 1 25 8 50 air");
    cmd("fill -24 0 -49 25 0 50 black_concrete");
    for (const t of CUSTOM) cmd(`kill @e[type=${t}]`);
    cmd("kill @e[type=boat,tag=mmgplus_boat]");
    cmd("kill @e[type=mmgplus:board,tag=mmgplus_label]");
    cmd("kill @e[type=fox,tag=mmgplus_fox]"); cmd("kill @e[type=pufferfish,tag=mmgplus_puffer]"); cmd("kill @e[type=arrow,x=-24,y=0,z=-49,dx=49,dy=12,dz=99]");
    cmd("kill @e[type=chicken,tag=mmgplus_chicken]");
    cmd("kill @e[type=item,x=-24,y=0,z=-49,dx=49,dy=12,dz=99]");
    cmd("tag @a remove mmgplus_out");
}
const actionbar = (text, players = playing()) => players.forEach((p) => p.onScreenDisplay.setActionBar(text));
const title = (text, sub = "", stay = 30) => playing().forEach((p) => p.onScreenDisplay.setTitle(text, { subtitle: sub, fadeInDuration: 0, stayDuration: stay, fadeOutDuration: 5 }));
const soundAll = (s, pitch = 1) => cmd(`execute as @a[tag=playing] at @s run playsound ${s} @s ~ ~ ~ 1 ${pitch}`);

// ===== 25. 計算早押し =====
// レベル1でも2けた。レベルが上がると かけ算・3つの数・2けた×2けた
function makeQuestion(lv) {
    let text, ans;
    if (lv === 1) { const a = rand(23, 89), b = rand(14, 69); if (Math.random() < 0.5) { text = `${a} + ${b}`; ans = a + b; } else { const [x, y] = a > b ? [a, b] : [b, a]; text = `${x} - ${y}`; ans = x - y; } }
    else if (lv === 2) { const a = rand(13, 39), b = rand(3, 9); text = `${a} × ${b}`; ans = a * b; }
    else if (lv === 3) { const a = rand(4, 9), b = rand(6, 12), c = rand(11, 59); if (Math.random() < 0.5) { text = `${a} × ${b} + ${c}`; ans = a * b + c; } else { text = `${a} × ${b} - ${c}`; ans = a * b - c; } }
    else if (lv === 4) { const a = rand(12, 29), b = rand(11, 19); text = `${a} × ${b}`; ans = a * b; }
    else { const a = rand(11, 29), b = rand(6, 19), c = rand(3, 9), d = rand(12, 79); text = `(${a} + ${b}) × ${c} - ${d}`; ans = (a + b) * c - d; }
    // まぎらわしい選択肢(1ちがい・10ちがい・下1けた同じ)
    const near = [1, -1, 2, -2, 10, -10, 9, -9, 11, -11, 20, -20].map((d) => ans + d).filter((v) => v >= 0).sort(() => Math.random() - 0.5);
    const choices = [ans, ...near.slice(0, 3)].sort(() => Math.random() - 0.5);
    return { text, ans, choices };
}

async function gameQuiz() {
    const QUESTIONS = 5, LIMIT = 300; // 1問15秒
    const correct = new Map();
    for (let q = 1; q <= QUESTIONS; q++) {
        if (aborted()) return [];
        const Q = makeQuestion(level());
        let winner;
        const players = playing();
        title(`§lQ${q}`, `§f${Q.text} = ?`);
        soundAll("random.orb");
        await wait(20);
        const asked = Date.now();
        const answer = (p, choice) => {
            if (winner || aborted()) return;
            if (choice === Q.ans) {
                winner = p;
                const sec = (Date.now() - asked) / 1000;
                correct.set(p.name, (correct.get(p.name) ?? 0) + 1);
                world.sendMessage(`§a${p.name} が正解！ §7(${sec.toFixed(2)}秒) §f${Q.text} = ${Q.ans}`);
                record(25, p.name, sec, "min");
                cmd(`playsound random.levelup "${p.name}"`);
                for (const o of playing()) if (o.id !== p.id) uiManager.closeAllForms(o);
            } else {
                p.sendMessage("§cざんねん！この問題はもう答えられません");
                cmd(`playsound note.bass "${p.name}"`);
            }
        };
        for (const p of players) {
            if (isBot(p)) {
                const delay = rand(...[[140, 290], [110, 260], [80, 220]][botStr()]);
                const ok = chance(0.3, 0.45, 0.6);
                system.runTimeout(() => answer(p, ok ? Q.ans : Q.choices.find((c) => c !== Q.ans)), delay);
                continue;
            }
            const form = new ActionFormData().title(`計算早押し Q${q}/${QUESTIONS}`).body(`§l${Q.text} = ?`);
            Q.choices.forEach((c) => form.button(`§l${c}`));
            form.show(p).then((res) => { if (!res.canceled) answer(p, Q.choices[res.selection]); }).catch(() => {});
        }
        for (let t = 0; t < LIMIT && !winner && !aborted(); t += 5) {
            actionbar(`§b計算早押し §fQ${q}/${QUESTIONS}  §7残り ${Math.ceil((LIMIT - t) / 20)}秒`);
            await wait(5);
        }
        players.forEach((p) => { try { uiManager.closeAllForms(p); } catch {} });
        const timedOut = !winner;
        winner ??= "時間切れ"; // あとから届いた BOT の答えを受けつけない
        if (timedOut) world.sendMessage(`§7時間切れ！ ${Q.text} = ${Q.ans}`);
        await wait(40);
    }
    const best = Math.max(0, ...correct.values());
    if (best === 0) return [];
    return playing().filter((p) => correct.get(p.name) === best);
}

// ===== 26. 色の記憶 =====
// 中央の台のまわりに5色の床(五角形)。床の奥に同じ色の光る柱。床と柱が光った順番に、床をふむ
const PADS = [
    { name: "§c赤", color: "red", pitch: 0.6 },
    { name: "§9青", color: "blue", pitch: 0.75 },
    { name: "§a緑", color: "lime", pitch: 0.9 },
    { name: "§e黄", color: "yellow", pitch: 1.1 },
    { name: "§5紫", color: "purple", pitch: 1.3 },
].map((p, i) => {
    const a = ((i * 72 - 90) * Math.PI) / 180;
    return { ...p, cx: Math.round(Math.cos(a) * 7), cz: Math.round(Math.sin(a) * 7), px: Math.round(Math.cos(a) * 11), pz: Math.round(Math.sin(a) * 11) };
});
const padFill = (pad, block) => cmd(`fill ${pad.cx - 2} 0 ${pad.cz - 2} ${pad.cx + 2} 0 ${pad.cz + 2} ${block}`);
const pillarFill = (pad, block) => cmd(`fill ${pad.px} 1 ${pad.pz} ${pad.px} 4 ${pad.pz} ${block}`);
function simonLight(pad, on) {
    padFill(pad, on ? "sea_lantern" : `${pad.color}_concrete`);
    pillarFill(pad, on ? "sea_lantern" : `${pad.color}_stained_glass`);
}
function buildSimon() {
    clearArena();
    disc(13, "polished_andesite");
    ring(14, 3, "tinted_glass");
    cmd("fill -2 0 -2 2 0 2 smooth_quartz");
    PADS.forEach((pad) => {
        cmd(`fill ${pad.cx - 3} 0 ${pad.cz - 3} ${pad.cx + 3} 0 ${pad.cz + 3} polished_deepslate`); // ふち
        simonLight(pad, false);
        cmd(`setblock ${pad.px} 0 ${pad.pz} polished_deepslate`);
    });
}
// 床の内側(ふちから0.25マス内)にしっかり乗っている時だけ、その色とみなす
function padAt(p) {
    const { x, y, z } = p.location;
    if (y > 1.2) return null;
    return PADS.find((pad) => x >= pad.cx - 1.75 && x <= pad.cx + 2.75 && z >= pad.cz - 1.75 && z <= pad.cz + 2.75) ?? null;
}

async function gameSimon() {
    const start = playing();
    const seq = [rand(0, 4), rand(0, 4)];
    const flash = [12, 10, 8, 7, 6][level() - 1];
    const cleared = new Map();
    for (let round = 1; round <= 25; round++) {
        if (aborted()) return [];
        seq.push(rand(0, 4));
        const players = alive();
        if (players.length === 0) break;
        cmd("tp @a[tag=playing,tag=!mmgplus_out] 0 1 0");
        title(`§l${seq.length}個`, "§fおぼえよう！");
        await wait(30);
        for (const i of seq) {
            if (aborted()) return [];
            simonLight(PADS[i], true);
            soundAll("note.pling", PADS[i].pitch);
            actionbar(`§d色の記憶 §f${PADS[i].name}`);
            await wait(flash);
            simonLight(PADS[i], false);
            await wait(3);
        }
        title("§lスタート！", "§f同じ順に床をふもう");
        const state = new Map(players.map((p) => [p.id, { idx: 0, prev: padAt(p) }]));
        const limit = 60 + seq.length * 20;
        for (let t = 0; t < limit && !aborted(); t += 2) {
            let left = 0;
            for (const p of alive()) {
                const s = state.get(p.id);
                if (!s || s.idx >= seq.length) continue;
                left++;
                if (isBot(p)) {
                    if (t % [22, 18, 14][botStr()] !== 0) continue;
                    const miss = [0.15, 0.1, 0.06][botStr()] + seq.length * [0.03, 0.02, 0.012][botStr()];
                    const i = Math.random() < miss ? (seq[s.idx] + rand(1, 4)) % 5 : seq[s.idx];
                    p.teleport({ x: PADS[i].cx + 0.5, y: 1, z: PADS[i].cz + 0.5 });
                    if (i === seq[s.idx]) { s.idx++; if (s.idx >= seq.length) left--; }
                    else { out(p, `§cまちがえた！ §7(${seq.length}個のラウンド)`); left--; }
                    continue;
                }
                const pad = padAt(p);
                if (pad && pad !== s.prev) {
                    if (PADS.indexOf(pad) === seq[s.idx]) {
                        s.idx++;
                        cmd(`playsound note.pling "${p.name}" ~ ~ ~ 1 ${pad.pitch}`);
                        p.onScreenDisplay.setActionBar(`§d色の記憶 §f${s.idx} / ${seq.length}`);
                        if (s.idx >= seq.length) { p.sendMessage("§aクリア！"); left--; }
                    } else { out(p, `§cまちがえた！ §7(${seq.length}個のラウンド)`); left--; }
                }
                if (pad !== null || p.location.y <= 1.2) s.prev = pad; // ジャンプ中は前の床のまま
            }
            if (t % 10 === 0) actionbar(`§d色の記憶 §f${seq.length}個  §7残り ${Math.ceil((limit - t) / 20)}秒`, alive().filter((p) => (state.get(p.id)?.idx ?? 0) === 0));
            if (left === 0) break;
            await wait(2);
        }
        for (const p of alive()) if ((state.get(p.id)?.idx ?? 0) < seq.length) out(p, "§c時間切れ！");
        for (const p of alive()) cleared.set(p.name, seq.length);
        const now = alive().length;
        if (now === 0 || (start.length > 1 && now === 1)) break;
        await wait(30);
    }
    const best = Math.max(0, ...cleared.values());
    if (best === 0 || (start.length === 1 && best < 6)) return [];
    const names = [...cleared].filter(([, v]) => v === best).map(([n]) => n);
    names.forEach((n) => record(26, n, best, "max"));
    return playing().filter((p) => names.includes(p.name));
}

// ===== 27. 椅子取りゲーム =====
// 丸い部屋。曲が止まったら、人数より1つ少ないイス(mmgplus:chair)が出る
function buildChairs() {
    clearArena();
    disc(11, "stripped_cherry_wood");
    disc(4, "red_carpet", 1);
    ring(12, 3, "cherry_fence");
    for (let a = 0; a < 360; a += 45) cmd(`setblock ${Math.round(Math.cos((a * Math.PI) / 180) * 11)} 1 ${Math.round(Math.sin((a * Math.PI) / 180) * 11)} lantern`);
}
// 「むすんでひらいて」風の短い曲(半音の数)。1音 = 4tick
const MELODY = [7, 7, 5, 4, 4, 5, 7, 7, 9, 7, 5, 4, 2, 2, 4, 5, 7, 7, 5, 4, 2, 4, 0, -1];
const notePitch = (n) => Math.min(2, Math.max(0.5, 0.8 * 2 ** (n / 12)));
const chairs = () => dim().getEntities({ type: "mmgplus:chair" });
const seated = (p) => p.getComponent("minecraft:riding")?.entityRidingOn?.typeId === "mmgplus:chair";

async function gameChairs() {
    const start = playing();
    if (start.length < 2) world.sendMessage("§7ひとりなので、イスに座れたら勝ち！");
    for (let round = 1; !aborted(); round++) {
        const players = alive();
        if (players.length <= 1 && start.length > 1) return players;
        cmd("ride @a stop_riding");
        cmd("kill @e[type=mmgplus:chair]");
        title(`§lラウンド ${round}`, "§f♪ 曲のあいだ歩き回ろう");
        await wait(30);
        const len = rand(20, 50); // 音の数
        for (let i = 0; i < len && !aborted(); i++) {
            const n = MELODY[i % MELODY.length];
            soundAll("note.harp", notePitch(n));
            if (i % 2 === 0) soundAll("note.bd", 1);
            actionbar("§e椅子取りゲーム §f♪♪♪");
            await wait(4);
        }
        if (aborted()) return [];
        // 曲が止まった → イスを出す(重ならないように)
        const need = Math.max(1, players.length - 1);
        const spots = [];
        for (let tries = 0; spots.length < need && tries < 400; tries++) {
            const a = Math.random() * Math.PI * 2, r = rand(2, 9);
            const s = { x: Math.round(Math.cos(a) * r) + 0.5, y: 1, z: Math.round(Math.sin(a) * r) + 0.5 };
            if (spots.every((o) => Math.hypot(o.x - s.x, o.z - s.z) >= 2.5)) spots.push(s);
        }
        // 本物 need 脚 + ニセモノ(座ると消える)1脚。本物のうち1脚は逃げるイス
        if (players.length >= 2) for (let tries = 0; spots.length < need + 1 && tries < 400; tries++) {
            const a = Math.random() * Math.PI * 2, r = rand(2, 9);
            const s = { x: Math.round(Math.cos(a) * r) + 0.5, y: 1, z: Math.round(Math.sin(a) * r) + 0.5 };
            if (spots.every((o) => Math.hypot(o.x - s.x, o.z - s.z) >= 2.5)) spots.push(s);
        }
        spots.forEach((s, i) => {
            try {
                const c = dim().spawnEntity("mmgplus:chair", s); c.setRotation({ x: 0, y: rand(0, 3) * 90 });
                if (i === need) c.addTag("mmgplus_fake"); else if (i === 0 && need >= 2) c.addTag("mmgplus_run");
            } catch {}
        });
        title("§c§l座れ！", `§fイス ${need}脚 §7(ニセモノと逃げるイスに注意)`, 20);
        soundAll("random.anvil_land", 1.5);
        for (let t = 0; t < 120 && !aborted(); t += 2) {
            for (const c of chairs()) {
                const riders = c.getComponent("minecraft:rideable")?.getRiders() ?? [];
                if (c.hasTag("mmgplus_fake") && riders.length) { riders.forEach((r) => r.sendMessage("§cニセモノのイスだった！")); cmd("playsound random.pop @a 0 2 0 1 0.6"); c.remove(); continue; }
                if (c.hasTag("mmgplus_run") && !riders.length) {
                    const near = alive().map((p) => ({ p, d: Math.hypot(p.location.x - c.location.x, p.location.z - c.location.z) })).sort((a, b) => a.d - b.d)[0];
                    if (near && near.d < 4) {
                        const dx = c.location.x - near.p.location.x, dz = c.location.z - near.p.location.z, d = Math.hypot(dx, dz) || 1;
                        let nx = c.location.x + (dx / d) * 0.3, nz = c.location.z + (dz / d) * 0.3;
                        if (Math.hypot(nx, nz) > 9.5) { nx = c.location.x - (dz / d) * 0.3; nz = c.location.z + (dx / d) * 0.3; } // 壁ぎわは横へにげる
                        c.teleport({ x: nx, y: c.location.y, z: nz });
                    }
                }
            }
            const n = alive().filter(seated).length;
            actionbar(`§c座れ！ §f${n}/${need}  §7残り ${Math.ceil((120 - t) / 20)}秒`);
            if (n >= need) break;
            await wait(2);
        }
        const losers = alive().filter((p) => !seated(p));
        if (start.length < 2) return losers.length ? [] : alive();
        losers.forEach((p) => out(p, "§c座れなかった..."));
        await wait(40);
    }
    return [];
}

// ===== 28. 宝探しプール =====
// 29x29、深さ5のプール。水の中にういている宝(その場から動かない)にさわって集める。金1点・ダイヤ3点・エメラルド5点(レア)
const TREASURE = [
    { type: "mmgplus:treasure_gold", pt: 1, w: 70, name: "§6金" },
    { type: "mmgplus:treasure_diamond", pt: 3, w: 25, name: "§bダイヤ" },
    { type: "mmgplus:treasure_emerald", pt: 5, w: 5, name: "§aエメラルド" },
];
function buildPool() {
    clearArena();
    cmd("fill -22 0 -22 22 6 22 prismarine_bricks");
    cmd("fill -21 0 -21 21 0 21 dark_prismarine");
    cmd("fill -21 1 -21 21 5 21 water");
    cmd("fill -21 6 -21 21 6 21 air");
    for (const x of [-22, -11, 0, 11, 22]) for (const z of [-22, 22]) { cmd(`setblock ${x} 6 ${z} sea_lantern`); cmd(`setblock ${z} 6 ${x} sea_lantern`); }
}
async function gamePool() {
    const TIME = 1200;
    const got = new Map();
    const want = () => Math.max(16, playing().length * 4);
    const stung = new Map();
    const pick = () => { let r = Math.random() * 100; return TREASURE.find((t) => (r -= t.w) < 0) ?? TREASURE[0]; };
    const spawn = () => {
        const t = pick();
        try { dim().spawnEntity(t.type, { x: rand(-20, 20) + 0.5, y: 1.2 + Math.random() * 3, z: rand(-20, 20) + 0.5 }); } catch {}
    };
    cmd("effect @a[tag=playing] water_breathing 90 0 true");
    cmd("effect @a[tag=playing] night_vision 90 0 true");
    title("§l宝探し！", "§6金1点 §bダイヤ3点 §aエメラルド5点");
    for (let t = 0; t < TIME && !aborted(); t += 2) {
        // 妨害のフグ: さわると2点落とす(2秒に1回まで)
        const puffers = dim().getEntities({ type: "minecraft:pufferfish", tags: ["mmgplus_puffer"] });
        for (let n = puffers.length; n < Math.max(3, playing().length); n++) { try { dim().spawnEntity("minecraft:pufferfish", { x: rand(-19, 19) + 0.5, y: 2.5, z: rand(-19, 19) + 0.5 }).addTag("mmgplus_puffer"); } catch {} }
        for (const p of playing()) {
            if ((stung.get(p.name) ?? 0) > system.currentTick) continue;
            if (!puffers.some((f) => Math.hypot(f.location.x - p.location.x, f.location.y - (p.location.y + 0.8), f.location.z - p.location.z) < 1.6)) continue;
            stung.set(p.name, system.currentTick + 40);
            const lost = Math.min(2, got.get(p.name) ?? 0);
            if (lost) { got.set(p.name, got.get(p.name) - lost); p.sendMessage(`§cフグにさされて ${lost}点 落とした！`); cmd(`playsound mob.pufferfish.sting "${p.name}"`); }
        }
        const list = TREASURE.flatMap((tr) => dim().getEntities({ type: tr.type }).map((e) => ({ e, tr })));
        for (let n = list.length; n < want(); n++) spawn();
        for (const p of playing()) {
            const l = p.location;
            const hit = list.find(({ e }) => e.isValid && Math.hypot(e.location.x - l.x, e.location.y - (l.y + 0.8), e.location.z - l.z) < 1.4);
            if (!hit) continue;
            hit.e.remove();
            got.set(p.name, (got.get(p.name) ?? 0) + hit.tr.pt);
            cmd(`playsound ${hit.tr.pt >= 5 ? "random.levelup" : "random.orb"} "${p.name}"`);
            if (hit.tr.pt >= 5) world.sendMessage(`§a${p.name} がエメラルドを見つけた！ §f(+5点)`);
        }
        if (t % 10 === 0) for (const p of playing()) p.onScreenDisplay.setActionBar(`§6宝探し §fあなた: §e${got.get(p.name) ?? 0}点  §7残り ${Math.ceil((TIME - t) / 20)}秒`);
        await wait(2);
    }
    const best = Math.max(0, ...got.values());
    if (best === 0) return [];
    const win = playing().filter((p) => got.get(p.name) === best);
    win.forEach((p) => record(28, p.name, best, "max"));
    world.sendMessage(`§6宝探し: ${win.map((p) => p.name).join(", ")} が ${best}点で1位！`);
    return win;
}

// ===== 29. ファイアバー =====
// 中心のブロックから2本の火の玉の棒(mmgplus:fireball)が回る。ジャンプでよける。だんだん速く、ときどき逆回転
const FB_LEN = 7, FB_STEP = 0.95;
const lastJump = new Map();
function buildFirebar() {
    clearArena();
    disc(9, "polished_blackstone_bricks");
    disc(2, "gilded_blackstone");
    ring(10, 2, "nether_brick_fence");
    cmd("setblock 0 1 0 gold_block");
}
async function gameFirebar() {
    const start = playing();
    const balls = [];
    for (let arm = 0; arm < 2; arm++) for (let i = 1; i <= FB_LEN; i++) {
        try { balls.push({ e: dim().spawnEntity("mmgplus:fireball", { x: 0.5, y: 1.25, z: 0.5 }), arm, r: i * FB_STEP }); } catch {}
    }
    let theta = 0, dir = 1, omega = (Math.PI * 2) / 100, swept = 0, revs = 0, high = null;
    const t0 = Date.now();
    title("§6§lファイアバー！", "§f回ってくる火の玉をジャンプでよけよう");
    await wait(40);
    const place = () => balls.forEach((b) => { if (b.e.isValid) b.e.teleport({ x: 0.5 + Math.cos(theta + b.arm * Math.PI) * b.r, y: 1.25, z: 0.5 + Math.sin(theta + b.arm * Math.PI) * b.r }); });
    for (let t = 0; t < 2400 && !aborted(); t++) {
        const prev = theta, step = omega * dir;
        theta += step;
        place();
        for (const p of alive()) {
            const { x, y, z } = p.location;
            const r = Math.hypot(x - 0.5, z - 0.5);
            if (r < 0.6 || r > FB_LEN * FB_STEP + 0.6) continue;
            const ang = Math.atan2(z - 0.5, x - 0.5);
            for (let arm = 0; arm < 2; arm++) {
                const from = Math.min(prev, theta) + arm * Math.PI, d = (((ang - from) % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
                const span = Math.abs(step) + 0.45 / Math.max(r, 1);
                // 当たり: 棒が通った角度の中にいて、足が火の玉より下
                if (y < 1.5 && (d <= span || d >= Math.PI * 2 - 0.45 / Math.max(r, 1))) {
                    out(p, "§c火の玉に当たった！");
                    cmd(`particle minecraft:large_explosion ${x} ${y + 1} ${z}`);
                    break;
                }
                // BOT は火の玉が近づいたらジャンプ(たまに失敗)
                if (isBot(p) && y < 1.05 && (lastJump.get(p.name) ?? 0) < system.currentTick - 10) {
                    const ahead = dir > 0 ? (((ang - theta - arm * Math.PI) % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2) : (((theta + arm * Math.PI - ang) % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
                    if (ahead <= Math.abs(step) * 6) { lastJump.set(p.name, system.currentTick); if (chance(0.75, 0.88, 0.96)) cmd(`scriptevent mmgbot:jump ${p.name}`); }
                }
            }
        }
        // 15秒たったら、反対向きに回る「上の棒」(頭の高さ)を追加。しゃがめばよけられる
        if (!high && (Date.now() - t0) / 1000 >= 15) {
            high = { theta: Math.PI / 2, balls: [] };
            for (let i = 2; i <= FB_LEN; i++) { try { high.balls.push({ e: dim().spawnEntity("mmgplus:fireball", { x: 0.5, y: 2.1, z: 0.5 }), r: i * FB_STEP }); } catch {} }
            title("§c§l上の棒が出た！", "§f上の棒は§eしゃがんで§fよけよう", 30); soundAll("mob.blaze.shoot", 0.7);
        }
        if (high) {
            const hp = high.theta, hs = -step * 0.7;
            high.theta += hs;
            high.balls.forEach((b) => { if (b.e.isValid) b.e.teleport({ x: 0.5 + Math.cos(high.theta) * b.r, y: 2.1, z: 0.5 + Math.sin(high.theta) * b.r }); });
            for (const p of alive()) {
                const { x, z } = p.location, r = Math.hypot(x - 0.5, z - 0.5);
                if (r < 1.5 || r > FB_LEN * FB_STEP + 0.6 || p.isSneaking) continue;
                const from = Math.min(hp, high.theta), d = (((Math.atan2(z - 0.5, x - 0.5) - from) % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
                if (d <= Math.abs(hs) + 0.45 / r || d >= Math.PI * 2 - 0.45 / r) {
                    if (isBot(p) && chance(0.6, 0.8, 0.93)) continue; // BOT はしゃがんだことにする
                    out(p, "§c上の棒に当たった！(しゃがむとよけられる)");
                }
            }
        }
        swept += Math.abs(step);
        if (swept >= Math.PI) {
            swept = 0; revs++;
            omega = Math.min(omega * 1.07, (Math.PI * 2) / 30);
            if (revs >= 4 && Math.random() < 0.3) { dir = -dir; title("§c§l逆回転！", "", 15); soundAll("mob.blaze.shoot"); }
            else soundAll("note.hat", 1.5);
        }
        const sec = (Date.now() - t0) / 1000;
        if (t % 10 === 0) actionbar(`§6ファイアバー §f残り ${alive().length}人  §7${sec.toFixed(0)}秒`);
        const n = alive().length;
        if (n === 0 || (start.length > 1 && n === 1) || (start.length === 1 && sec >= 40)) break;
        await wait(1);
    }
    balls.forEach((b) => { try { b.e.remove(); } catch {} });
    high?.balls.forEach((b) => { try { b.e.remove(); } catch {} });
    const sec = Math.round((Date.now() - t0) / 100) / 10;
    const win = alive();
    win.forEach((p) => record(29, p.name, sec, "max"));
    return win;
}

// ===== 30. ボートレース =====
// z = -46 から 46 までの広い一本道(はば11)。ゆるいS字。氷の上をボートで前へ進み、ゴールの白黒の線をこえたらゴール
const RACE_START = -40, RACE_GOAL = 44, RACE_HALF = 5;
const raceX = (z) => Math.round(8 * Math.sin(((z + 46) / 92) * Math.PI * 3));
function buildRace() {
    clearArena();
    for (let z = -47; z <= 47; z++) {
        const cx = raceX(z), px = raceX(z - 1);
        const lo = Math.min(cx, px), hi = Math.max(cx, px);
        cmd(`fill ${cx - RACE_HALF} 0 ${z} ${cx + RACE_HALF} 0 ${z} packed_ice`);
        cmd(`fill ${lo - RACE_HALF - 1} 1 ${z} ${cx - RACE_HALF - 1} 2 ${z} ${((z % 8) + 8) % 8 < 4 ? "red_concrete" : "white_concrete"}`);
        cmd(`fill ${cx + RACE_HALF + 1} 1 ${z} ${hi + RACE_HALF + 1} 2 ${z} ${((z % 8) + 8) % 8 < 4 ? "red_concrete" : "white_concrete"}`);
        if (z % 6 === 0) { cmd(`setblock ${cx - RACE_HALF - 1} 3 ${z} glowstone`); cmd(`setblock ${cx + RACE_HALF + 1} 3 ${z} glowstone`); }
    }
    // うしろの壁・スタートの線・ゴールの白黒
    cmd(`fill ${raceX(-47) - RACE_HALF} 1 -47 ${raceX(-47) + RACE_HALF} 2 -47 red_concrete`);
    cmd(`fill ${raceX(47) - RACE_HALF} 1 47 ${raceX(47) + RACE_HALF} 2 47 red_concrete`);
    cmd(`fill ${raceX(RACE_START) - RACE_HALF} 0 ${RACE_START} ${raceX(RACE_START) + RACE_HALF} 0 ${RACE_START} lime_concrete`);
    for (let x = -RACE_HALF; x <= RACE_HALF; x++) for (const z of [RACE_GOAL, RACE_GOAL + 1]) cmd(`setblock ${raceX(z) + x} 0 ${z} ${(x + z) % 2 === 0 ? "white_concrete" : "black_concrete"}`);
    // スタートのゲート(GO で開く)
    cmd(`fill ${raceX(RACE_START) - RACE_HALF} 1 ${RACE_START} ${raceX(RACE_START) + RACE_HALF} 2 ${RACE_START} glass`);
}
async function gameRace() {
    const TIME = 3000;
    const players = playing();
    const st = new Map();
    const boatFor = (p, loc) => {
        const b = dim().spawnEntity("minecraft:boat", loc ?? p.location);
        b.addTag("mmgplus_boat");
        b.setRotation({ x: 0, y: 0 }); // ゴールの方(+z)を向く
        try { b.getComponent("minecraft:rideable")?.addRider(p); } catch {}
    };
    players.forEach((p, i) => {
        const z = RACE_START - 3 - Math.floor(i / 5) * 2.5;
        const loc = { x: raceX(Math.floor(z)) + ((i % 5) - 2) * 2 + 0.5, y: 1, z };
        p.teleport(loc, { rotation: { x: 0, y: 0 } });
        boatFor(p, loc);
        st.set(p.id, { done: 0, off: 0 });
    });
    title("§lボートレース", "§fまっすぐ前へ！ 白黒の線がゴール", 50);
    await wait(50);
    for (const n of ["3", "2", "1"]) { title(`§l${n}`); soundAll("note.pling", 0.8); await wait(20); }
    cmd(`fill ${raceX(RACE_START) - RACE_HALF} 1 ${RACE_START} ${raceX(RACE_START) + RACE_HALF} 2 ${RACE_START} air`);
    title("§a§lGO!"); soundAll("note.pling", 1.6);
    const t0 = Date.now();
    const order = [];
    for (let t = 0; t < TIME && !aborted(); t += 2) {
        for (const p of playing()) {
            const s = st.get(p.id);
            if (!s || s.done) continue;
            const z = p.location.z;
            if (z >= RACE_GOAL) {
                s.done = (Date.now() - t0) / 1000;
                order.push(p);
                world.sendMessage(`§b${order.length}位 §f${p.name} §7${s.done.toFixed(2)}秒`);
                record(30, p.name, s.done, "min");
                cmd(`playsound random.levelup "${p.name}"`);
                continue;
            }
            const riding = p.getComponent("minecraft:riding")?.entityRidingOn;
            if (riding && isBot(p)) steerBot(riding);
            if (riding) s.off = 0; else if (++s.off >= 10) { s.off = 0; boatFor(p); }
            if (t % 10 === 0) {
                const pct = Math.max(0, Math.min(100, Math.round(((z - RACE_START) / (RACE_GOAL - RACE_START)) * 100)));
                p.onScreenDisplay.setActionBar(`§bボートレース §fゴールまで ${pct}%  §7${((Date.now() - t0) / 1000).toFixed(0)}秒`);
            }
        }
        if (t % 40 === 0) for (const b of dim().getEntities({ type: "minecraft:boat", tags: ["mmgplus_boat"] })) if (!b.getComponent("minecraft:rideable")?.getRiders().length) b.remove();
        if (players.every((p) => st.get(p.id)?.done || !p.isValid)) break;
        await wait(2);
    }
    cmd("ride @a stop_riding");
    const n = players.length === 1 ? 1 : Math.min(3, players.length - 1);
    return order.slice(0, n);
}
// BOT のボート: 少し先のコースの真ん中をめざして押す
function steerBot(boat) {
    const l = boat.location, tz = l.z + 6, tx = raceX(Math.floor(tz)) + 0.5;
    const dx = tx - l.x, dz = tz - l.z, d = Math.hypot(dx, dz);
    const v = boat.getVelocity(), max = [0.45, 0.6, 0.75][botStr()];
    if (Math.hypot(v.x, v.z) < max) boat.applyImpulse({ x: (dx / d) * 0.08, y: 0, z: (dz / d) * 0.08 });
    boat.setRotation({ x: 0, y: (Math.atan2(-dx, dz) * 180) / Math.PI });
}

// ===== 31. ピッタリ止め =====
// 「よーい」→「スタート！」の音と同時に計り始める。ボタンの画面にも「もうスタートしている」と書く
async function gameStop() {
    const target = level() <= 2 ? 10 : rand(5, 15);
    title(`§l${target}.00秒`, "§f「スタート！」から数えて、ぴったりで押そう", 60);
    await wait(80);
    title("§e§lよーい…", "", 20); soundAll("note.pling", 0.7);
    await wait(rand(25, 45)); // 合図のタイミングを読ませない
    const res = new Map();
    const players = playing();
    title("§a§lスタート！", "§f頭の中で数えよう", 20); soundAll("random.levelup", 1.4);
    const t0 = Date.now();
    for (const p of players.filter(isBot)) res.set(p.name, Math.max(0.5, target + (Math.random() * 2 - 1) * [2.2, 1.5, 0.9][botStr()]));
    const forms = Promise.all(players.filter((p) => !isBot(p)).map((p) =>
        new ActionFormData().title("ピッタリ止め").body(`§a§lもうスタートしています！§r\n\n§l${target}.00秒§r ぴったりで押そう`).button("§l§cストップ！").show(p)
            .then((r) => { if (!r.canceled && !aborted()) res.set(p.name, (Date.now() - t0) / 1000); }).catch(() => {})));
    await Promise.race([forms, wait(target * 20 + 200)]);
    players.forEach((p) => { try { uiManager.closeAllForms(p); } catch {} });
    if (aborted() || res.size === 0) return [];
    const rows = [...res].map(([n, v]) => [n, v, Math.abs(v - target)]).sort((a, b) => a[2] - b[2]);
    world.sendMessage(`§e§lピッタリ止め 結果 §r§7(目標 ${target}.00秒)`);
    rows.forEach(([n, v, d], i) => world.sendMessage(`§f${i + 1}. ${n} §b${v.toFixed(2)}秒 §7(${d.toFixed(2)}秒ずれ)`));
    const best = rows[0][2];
    const names = rows.filter((r) => r[2] === best).map((r) => r[0]);
    names.forEach((n) => record(31, n, Math.round(best * 100) / 100, "min"));
    return playing().filter((p) => names.includes(p.name));
}

// ===== 32. ニワトリ集め =====
// 半径20の牧場。まわりに8つの囲い(中は5x5)。たねで連れてくるだけで、エサはあげられない
const PENS = [[0, -16], [12, -12], [16, 0], [12, 12], [0, 16], [-12, 12], [-16, 0], [-12, -12]];
const PEN_COLORS = ["red", "orange", "yellow", "lime", "light_blue", "blue", "purple", "pink"];
function buildFarm() {
    clearArena();
    disc(21, "grass_block");
    ring(22, 2, "oak_fence");
    PENS.forEach(([cx, cz], i) => {
        cmd(`fill ${cx - 2} 0 ${cz - 2} ${cx + 2} 0 ${cz + 2} ${PEN_COLORS[i]}_concrete`);
        cmd(`fill ${cx - 3} 1 ${cz - 3} ${cx + 3} 1 ${cz + 3} oak_fence`);
        cmd(`fill ${cx - 2} 1 ${cz - 2} ${cx + 2} 1 ${cz + 2} air`);
        // 中心向きの面に3マスの入口
        const ox = Math.sign(-cx), oz = Math.sign(-cz);
        if (Math.abs(cx) >= Math.abs(cz)) cmd(`fill ${cx + ox * 3} 1 ${cz - 1} ${cx + ox * 3} 1 ${cz + 1} air`);
        else cmd(`fill ${cx - 1} 1 ${cz + oz * 3} ${cx + 1} 1 ${cz + oz * 3} air`);
    });
}
world.beforeEvents.playerInteractWithEntity.subscribe((ev) => {
    if (ev.target.typeId === "minecraft:chicken" && ev.target.hasTag("mmgplus_chicken")) ev.cancel = true; // エサやり・繁殖を止める
});
async function gameFarm() {
    const TIME = 1600;
    const players = playing();
    const pen = new Map(players.map((p, i) => [p.name, i % PENS.length]));
    players.forEach((p) => {
        const [cx, cz] = PENS[pen.get(p.name)];
        p.teleport({ x: cx * 0.7 + 0.5, y: 1, z: cz * 0.7 + 0.5 });
        p.sendMessage(`§fあなたの囲いは ${PEN_COLORS[pen.get(p.name)]} の床です`);
    });
    cmd("give @a[tag=playing] wheat_seeds 1");
    const n = Math.min(50, Math.max(10, players.length * 5));
    for (let i = 0; i < n; i++) {
        const a = Math.random() * Math.PI * 2, r = rand(0, 9);
        dim().spawnEntity("minecraft:chicken", { x: Math.cos(a) * r + 0.5, y: 1, z: Math.sin(a) * r + 0.5 }).addTag("mmgplus_chicken");
    }
    title("§lニワトリ集め！", "§fたねを持つとついてくる。自分の囲いへ連れていこう");
    const count = () => {
        const c = PENS.map(() => 0);
        for (const e of dim().getEntities({ type: "minecraft:chicken", tags: ["mmgplus_chicken"] })) {
            const x = Math.floor(e.location.x), z = Math.floor(e.location.z);
            const i = PENS.findIndex(([cx, cz]) => Math.abs(x - cx) <= 2 && Math.abs(z - cz) <= 2);
            if (i >= 0) c[i]++;
        }
        return c;
    };
    for (let t = 0; t < TIME && !aborted(); t += 10) {
        if (t === 500) {
            for (let i = 0; i < 2 + Math.floor(players.length / 4); i++) { try { dim().spawnEntity("minecraft:fox", { x: rand(-5, 5) + 0.5, y: 1, z: rand(-5, 5) + 0.5 }).addTag("mmgplus_fox"); } catch {} }
            title("§6§lキツネが来た！", "§fニワトリを守れ", 30); soundAll("mob.fox.screech");
        }
        if (t === 800) cmd("kill @e[type=fox,tag=mmgplus_fox]");
        const c = count();
        for (const p of playing()) p.onScreenDisplay.setActionBar(`§aニワトリ集め §fあなたの囲い: §e${c[pen.get(p.name)] ?? 0}羽  §7残り ${Math.ceil((TIME - t) / 20)}秒`);
        await wait(10);
    }
    cmd("clear @a[tag=playing] wheat_seeds");
    const c = count();
    const best = Math.max(...c);
    if (best === 0) return [];
    const win = playing().filter((p) => c[pen.get(p.name)] === best);
    win.forEach((p) => record(32, p.name, best, "max"));
    world.sendMessage(`§aニワトリ集め: ${win.map((p) => p.name).join(", ")} が ${best}羽で1位！`);
    return win;
}

// ===== 33. 一番多い色は？ =====
// 前の壁に色のモザイクを一瞬だけ見せる。一番多かった色をボタンで答える。5問で正解数を競う
const MOSAIC = [["red", "§c赤"], ["blue", "§9青"], ["lime", "§a緑"], ["yellow", "§e黄"], ["purple", "§5紫"]];
function buildWallRoom() {
    clearArena();
    cmd("fill -9 0 -12 9 0 4 smooth_quartz");
    cmd("fill -9 1 -13 9 11 -13 black_concrete");
}
async function gameColors() {
    const correct = new Map();
    for (let q = 1; q <= 5 && !aborted(); q++) {
        const n = 2 + Math.min(3, Math.ceil(level() / 2) + Math.floor(q / 3)); // 使う色の数
        const cols = MOSAIC.slice().sort(() => Math.random() - 0.5).slice(0, n);
        const count = cols.map(() => 0);
        title(`§lQ${q}`, "§f前の壁を見て！");
        await wait(30);
        for (let x = -8; x <= 8; x++) for (let y = 1; y <= 10; y++) {
            const i = rand(0, n - 1); count[i]++;
            cmd(`setblock ${x} ${y} -13 ${cols[i][0]}_concrete`);
        }
        let ans = count.indexOf(Math.max(...count));
        if (count.filter((c) => c === count[ans]).length > 1) { count[ans]++; cmd(`setblock 0 5 -13 ${cols[ans][0]}_concrete`); } // 同数をなくす
        await wait([60, 50, 40, 30, 25][level() - 1]);
        cmd("fill -8 1 -13 8 10 -13 black_concrete");
        const answered = new Map();
        const players = playing();
        for (const p of players) {
            if (isBot(p)) { answered.set(p.name, chance(0.3, 0.45, 0.6) ? ans : rand(0, n - 1)); continue; }
            const f = new ActionFormData().title(`一番多い色は？ Q${q}`).body("一番多かった色は？");
            cols.forEach((c) => f.button(`§l${c[1]}`));
            f.show(p).then((r) => { if (!r.canceled) answered.set(p.name, r.selection); }).catch(() => {});
        }
        for (let t = 0; t < 200 && answered.size < players.length && !aborted(); t += 5) { actionbar(`§e一番多い色は？ §7残り ${Math.ceil((200 - t) / 20)}秒`); await wait(5); }
        players.forEach((p) => { try { uiManager.closeAllForms(p); } catch {} });
        world.sendMessage(`§f答え: ${cols[ans][1]}§f (${cols.map((c, i) => `${c[1]}${count[i]}`).join(" ")}§f)`);
        for (const [name, a] of answered) if (a === ans) correct.set(name, (correct.get(name) ?? 0) + 1);
        await wait(40);
    }
    const best = Math.max(0, ...correct.values());
    return best ? playing().filter((p) => correct.get(p.name) === best) : [];
}

// ===== 34. 早押し反射 =====
// 前の壁が赤から緑に変わった瞬間にしゃがむ。早かった順に得点。緑になる前にしゃがむとそのラウンドは失格
async function gameReflex() {
    const wins = new Map();
    title("§l早押し反射", "§f壁が§a緑§fになったらしゃがむ！ 早すぎると失格", 50);
    await wait(60);
    for (let r = 1; r <= 5 && !aborted(); r++) {
        cmd("fill -8 1 -13 8 10 -13 red_concrete");
        title(`§lラウンド ${r}`, "§fまだ…", 20);
        await wait(30);
        const players = playing();
        const foul = new Set();
        const delay = rand(30, 120);
        for (let t = 0; t < delay && !aborted(); t++) {
            for (const p of players) if (!foul.has(p.name) && p.isSneaking) { foul.add(p.name); p.sendMessage("§cフライング！"); cmd(`playsound note.bass "${p.name}"`); }
            await wait(1);
        }
        cmd("fill -8 1 -13 8 10 -13 lime_concrete");
        soundAll("note.pling", 2);
        const t0 = system.currentTick, times = new Map();
        // BOT の反応時間(tick)
        const botT = new Map(players.filter(isBot).map((p) => [p.name, rand(...[[12, 22], [9, 17], [7, 13]][botStr()])]));
        for (const p of players.filter(isBot)) if (Math.random() < 0.12) foul.add(p.name); // BOT もたまにフライング
        for (let t = 0; t < 60 && !aborted(); t++) {
            for (const p of players) {
                if (foul.has(p.name) || times.has(p.name)) continue;
                if (isBot(p) ? t >= botT.get(p.name) : p.isSneaking) times.set(p.name, (system.currentTick - t0) * 50);
            }
            await wait(1);
        }
        const order = [...times].sort((a, b) => a[1] - b[1]);
        if (order.length) {
            const [name, ms] = order[0];
            wins.set(name, (wins.get(name) ?? 0) + 1);
            record(34, name, ms / 1000, "min");
            world.sendMessage(`§aラウンド${r}: ${order.slice(0, 3).map(([n, v], i) => `${i + 1}位 ${n} ${(v / 1000).toFixed(2)}秒`).join(" / ")}`);
        }
        await wait(30);
    }
    const best = Math.max(0, ...wins.values());
    return best ? playing().filter((p) => wins.get(p.name) === best) : [];
}

// ===== 35. 矢の雨 =====
// 四方の壁から矢が飛んでくる。3回当たったら脱落。だんだん増える
const hits = new Map();
world.afterEvents.entityHurt.subscribe((ev) => {
    const p = ev.hurtEntity;
    if (p.typeId !== "minecraft:player" || score("game", "selectgame") !== 35 || !p.hasTag("playing") || p.hasTag("mmgplus_out")) return;
    if (ev.damageSource.cause !== "projectile") return;
    const n = (hits.get(p.name) ?? 0) + 1;
    hits.set(p.name, n);
    try { p.addEffect("instant_health", 1, { amplifier: 4, showParticles: false }); } catch {}
    if (n >= 3) out(p, "§c矢に3回当たった！"); else p.onScreenDisplay.setActionBar(`§c当たった！ §f残り ${3 - n}回`);
});
function buildArena(r, floor, wallBlock, h = 4) {
    clearArena();
    cmd(`fill ${-r} 0 ${-r} ${r} 0 ${r} ${floor}`);
    cmd(`fill ${-r - 1} 1 ${-r - 1} ${r + 1} ${h} ${-r - 1} ${wallBlock}`); cmd(`fill ${-r - 1} 1 ${r + 1} ${r + 1} ${h} ${r + 1} ${wallBlock}`);
    cmd(`fill ${-r - 1} 1 ${-r - 1} ${-r - 1} ${h} ${r + 1} ${wallBlock}`); cmd(`fill ${r + 1} 1 ${-r - 1} ${r + 1} ${h} ${r + 1} ${wallBlock}`);
}
async function gameArrows() {
    hits.clear();
    const start = playing();
    title("§l矢の雨", "§f四方から飛んでくる矢をよけよう(3回でアウト)");
    await wait(40);
    const t0 = Date.now();
    for (let t = 0; t < 1800 && !aborted(); t += 4) {
        const sec = (Date.now() - t0) / 1000;
        const perTick = Math.min(4, 1 + sec / 15 + level() * 0.2);
        for (let k = 0; k < perTick; k++) if (Math.random() < 0.5) {
            const side = rand(0, 3), a = rand(-9, 9) + 0.5;
            const from = [{ x: a, z: -9.3 }, { x: a, z: 9.3 }, { x: -9.3, z: a }, { x: 9.3, z: a }][side];
            const tgt = alive()[rand(0, Math.max(0, alive().length - 1))];
            const tx = tgt && Math.random() < 0.5 ? tgt.location.x : rand(-8, 8), tz = tgt && Math.random() < 0.5 ? tgt.location.z : rand(-8, 8);
            try {
                const e = dim().spawnEntity("minecraft:arrow", { x: from.x, y: 1.6, z: from.z });
                const dx = tx - from.x, dz = tz - from.z, d = Math.hypot(dx, dz) || 1, v = 1.1 + Math.min(1, sec / 60);
                e.applyImpulse({ x: (dx / d) * v, y: 0.08, z: (dz / d) * v });
            } catch {}
        }
        if (t % 40 === 0) cmd("kill @e[type=arrow,x=-12,y=0,z=-12,dx=24,dy=6,dz=24]");
        if (t % 20 === 0) actionbar(`§c矢の雨 §f残り ${alive().length}人  §7${sec.toFixed(0)}秒`);
        const n = alive().length;
        if (n === 0 || (start.length > 1 && n <= Math.max(1, Math.floor(start.length / 3))) || (start.length === 1 && sec >= 45)) break;
        await wait(4);
    }
    cmd("kill @e[type=arrow]");
    const sec = Math.round((Date.now() - t0) / 100) / 10;
    alive().forEach((p) => record(35, p.name, sec, "max"));
    return alive();
}

// ===== 36. 隕石よけ =====
// 着弾する場所に赤い印が出て、1.5秒後に空から隕石(火の玉のモデル)が落ちる。半径2.5以内にいたら脱落
async function gameMeteor() {
    const start = playing();
    title("§c§l隕石よけ", "§f赤い印から逃げろ！");
    await wait(40);
    const falling = [];
    const t0 = Date.now();
    for (let t = 0; t < 2400 && !aborted(); t += 2) {
        const sec = (Date.now() - t0) / 1000;
        if (t % Math.max(6, 30 - Math.floor(sec / 3) - level() * 2) === 0) {
            const tgt = alive()[rand(0, Math.max(0, alive().length - 1))];
            const x = tgt && Math.random() < 0.6 ? tgt.location.x + rand(-2, 2) : rand(-9, 9) + 0.5, z = tgt && Math.random() < 0.6 ? tgt.location.z + rand(-2, 2) : rand(-9, 9) + 0.5;
            let e; try { e = dim().spawnEntity("mmgplus:fireball", { x, y: 30, z }); } catch {}
            if (e) falling.push({ e, x, z, land: system.currentTick + 30 });
        }
        for (const m of falling.slice()) {
            const left = m.land - system.currentTick;
            if (t % 4 === 0) cmd(`particle minecraft:redstone_wire_dust_particle ${m.x} 1.1 ${m.z}`);
            for (let i = 0; i < 6; i++) { const a = (i / 6) * Math.PI * 2; if (t % 4 === 0) cmd(`particle minecraft:basic_flame_particle ${m.x + Math.cos(a) * 2.5} 1.1 ${m.z + Math.sin(a) * 2.5}`); }
            if (left > 0) { try { m.e.teleport({ x: m.x, y: 1 + left, z: m.z }); } catch {} continue; }
            falling.splice(falling.indexOf(m), 1);
            try { m.e.remove(); } catch {}
            cmd(`particle minecraft:huge_explosion_emitter ${m.x} 1.5 ${m.z}`);
            cmd(`playsound random.explode @a ${m.x} 1 ${m.z} 1 1`);
            for (const p of alive()) if (Math.hypot(p.location.x - m.x, p.location.z - m.z) < 2.5) out(p, "§c隕石に当たった！");
        }
        if (t % 20 === 0) actionbar(`§c隕石よけ §f残り ${alive().length}人  §7${sec.toFixed(0)}秒`);
        const n = alive().length;
        if (n === 0 || (start.length > 1 && n <= Math.max(1, Math.floor(start.length / 3))) || (start.length === 1 && sec >= 45)) break;
        await wait(2);
    }
    falling.forEach((m) => { try { m.e.remove(); } catch {} });
    const sec = Math.round((Date.now() - t0) / 100) / 10;
    alive().forEach((p) => record(36, p.name, sec, "max"));
    return alive();
}

// ===== 37. 押し寄せる壁 =====
// 通路(x -7〜7)の奥から、穴のあいた壁が迫ってくる。穴の位置に立てばすり抜けられる。だんだん速く・穴が小さく
async function gameWalls() {
    const start = playing();
    title("§l押し寄せる壁", "§f穴の位置に立ってすり抜けろ！");
    await wait(40);
    for (let wave = 1; wave <= 30 && !aborted(); wave++) {
        const hw = Math.max(1, 3 - Math.floor(wave / 4)); // 穴のはば
        const holes = [];
        for (let k = 0; k < (wave < 6 ? 2 : 1); k++) holes.push(rand(-7, 7 - hw + 1));
        const inHole = (x) => holes.some((h) => x >= h && x < h + hw);
        const speed = Math.max(1, 4 - Math.floor(wave / 3) - Math.floor(level() / 3));
        const color = ["orange", "magenta", "cyan", "lime", "pink"][wave % 5];
        for (let z = -19; z <= 11 && !aborted(); z++) {
            cmd(`fill -7 1 ${z - 1} 7 3 ${z - 1} air`);
            cmd(`fill -7 1 ${z} 7 3 ${z} ${color}_concrete`);
            for (const h of holes) cmd(`fill ${h} 1 ${z} ${h + hw - 1} 2 ${z} air`);
            for (const p of alive()) {
                const px = Math.floor(p.location.x), pz = Math.floor(p.location.z);
                if (pz === z && !inHole(px)) out(p, "§c壁に押しつぶされた！");
            }
            // BOT は穴の位置へ
            if (z === -10) for (const p of alive().filter(isBot)) if (chance(0.6, 0.8, 0.95)) p.teleport({ x: holes[0] + hw / 2, y: 1, z: p.location.z });
            await wait(speed);
        }
        cmd("fill -7 1 11 7 3 12 air");
        if (wave % 3 === 0) soundAll("note.hat", 1.5);
        actionbar(`§6押し寄せる壁 §f${wave}枚目  残り ${alive().length}人`);
        const n = alive().length;
        if (n === 0 || (start.length > 1 && n <= Math.max(1, Math.floor(start.length / 3))) || (start.length === 1 && wave >= 12)) break;
    }
    return alive();
}

// ===== 38. 障害物ダッシュ =====
// z -44 → 44 のまっすぐなコース。左右に動く壁とハードルをこえてゴールへ。当たるとひとつ前のチェックポイントに戻る
const DASH_W = 4;
const dashBars = [-30, -18, -6, 6, 18, 30].map((z, i) => ({ z, w: 3, x: -DASH_W, dir: i % 2 ? 1 : -1 }));
function buildWalls() {
    clearArena();
    cmd("fill -8 0 -20 8 0 12 light_gray_concrete");
    cmd("fill -8 1 -20 -8 4 12 glass"); cmd("fill 8 1 -20 8 4 12 glass"); cmd("fill -8 1 12 8 4 12 glass");
}
function buildDash() {
    clearArena();
    cmd(`fill ${-DASH_W} 0 -46 ${DASH_W} 0 46 white_concrete`);
    cmd(`fill ${-DASH_W - 1} 1 -46 ${-DASH_W - 1} 2 46 glass`); cmd(`fill ${DASH_W + 1} 1 -46 ${DASH_W + 1} 2 46 glass`);
    cmd(`fill ${-DASH_W} 1 -46 ${DASH_W} 2 -46 glass`);
    for (const z of [-36, -24, -12, 0, 12, 24, 36]) cmd(`fill ${-DASH_W} 1 ${z} ${DASH_W} 1 ${z} oak_slab`); // ハードル
    for (const z of [-24, 0, 24]) cmd(`fill ${-DASH_W} 0 ${z - 2} ${DASH_W} 0 ${z - 2} lime_concrete`); // チェックポイント
    cmd(`fill ${-DASH_W} 0 -42 ${DASH_W} 0 -42 lime_concrete`);
    for (let x = -DASH_W; x <= DASH_W; x++) for (const z of [44, 45]) cmd(`setblock ${x} 0 ${z} ${(x + z) % 2 === 0 ? "white_concrete" : "black_concrete"}`);
    cmd(`fill ${-DASH_W} 1 -41 ${DASH_W} 2 -41 glass`);
}
async function gameDash() {
    const players = playing();
    players.forEach((p, i) => p.teleport({ x: -3 + (i % 7) + 0.5, y: 1, z: -44 + Math.floor(i / 7) * 1.2 }, { rotation: { x: 0, y: 0 } }));
    for (const n of ["3", "2", "1"]) { title(`§l${n}`); soundAll("note.pling", 0.8); await wait(20); }
    cmd(`fill ${-DASH_W} 1 -41 ${DASH_W} 2 -41 air`);
    title("§a§lGO!"); soundAll("note.pling", 1.6);
    cmd("effect @a[tag=playing] speed 120 0 true");
    const t0 = Date.now(), order = [];
    const cp = (z) => [-42, -26, -2, 22].filter((c) => c <= z).pop() ?? -42;
    for (let t = 0; t < 3000 && !aborted(); t += 2) {
        for (const b of dashBars) {
            cmd(`fill ${b.x} 1 ${b.z} ${b.x + b.w - 1} 2 ${b.z} air`);
            if (t % [6, 5, 4, 3, 3][level() - 1] === 0) { b.x += b.dir; if (b.x <= -DASH_W || b.x + b.w - 1 >= DASH_W) b.dir = -b.dir; }
            cmd(`fill ${b.x} 1 ${b.z} ${b.x + b.w - 1} 2 ${b.z} red_concrete`);
        }
        for (const p of playing()) {
            if (order.includes(p)) continue;
            const { x, z } = p.location;
            if (isBot(p) && t % 4 === 0) { try { p.teleport({ x: p.location.x, y: 1, z: z + [0.5, 0.7, 0.9][botStr()] }); } catch {} }
            if (dashBars.some((b) => Math.floor(z) === b.z && Math.floor(x) >= b.x && Math.floor(x) < b.x + b.w)) {
                const c = cp(z); p.teleport({ x: 0.5, y: 1, z: c + 0.5 }, { rotation: { x: 0, y: 0 } });
                p.sendMessage("§c当たった！ チェックポイントへ戻る"); cmd(`playsound note.bass "${p.name}"`);
            }
            if (z >= 44) {
                order.push(p);
                const sec = (Date.now() - t0) / 1000;
                world.sendMessage(`§b${order.length}位 §f${p.name} §7${sec.toFixed(2)}秒`);
                record(38, p.name, sec, "min");
            }
            if (t % 10 === 0) p.onScreenDisplay.setActionBar(`§b障害物ダッシュ §fゴールまで ${Math.max(0, Math.round(44 - z))}m`);
        }
        if (players.every((p) => order.includes(p) || !p.isValid)) break;
        await wait(2);
    }
    cmd("effect @a[tag=playing] clear");
    return order.slice(0, players.length === 1 ? 1 : Math.min(3, players.length - 1));
}

// ===== 39. 配置の記憶 =====
// ひとり1つの4x4のマス。光ったマスを覚えて、消えたあと同じマスをふむ(ふむと光る、もう一度ふむと消える)
async function gameMemory() {
    clearArena();
    const players = playing();
    const grids = players.map((p, i) => ({ p, ox: (i % 6) * 7 - 18, oz: Math.floor(i / 6) * 7 - 4 }));
    for (const g of grids) {
        cmd(`fill ${g.ox - 1} 0 ${g.oz - 1} ${g.ox + 4} 0 ${g.oz + 4} polished_deepslate`);
        cmd(`fill ${g.ox} 0 ${g.oz} ${g.ox + 3} 0 ${g.oz + 3} white_concrete`);
        g.p.teleport({ x: g.ox + 2, y: 1, z: g.oz - 1.5 }, { rotation: { x: 40, y: 0 } });
    }
    const score2 = new Map();
    for (let r = 1; r <= 4 && !aborted(); r++) {
        const n = 3 + r + level() - 1;
        const lit = new Set();
        while (lit.size < Math.min(12, n)) lit.add(rand(0, 15));
        title(`§lラウンド ${r}`, `§f${lit.size}マス 光ります`);
        await wait(30);
        for (const g of grids) for (const k of lit) cmd(`setblock ${g.ox + (k % 4)} 0 ${g.oz + Math.floor(k / 4)} sea_lantern`);
        await wait([80, 70, 60, 50, 40][level() - 1]);
        for (const g of grids) cmd(`fill ${g.ox} 0 ${g.oz} ${g.ox + 3} 0 ${g.oz + 3} white_concrete`);
        title("§lふもう！", "§f光っていたマスをふむ(もう一度ふむと取り消し)");
        const marks = new Map(grids.map((g) => [g.p.name, new Set()]));
        const prev = new Map();
        for (let t = 0; t < 240 && !aborted(); t += 2) {
            for (const g of grids) {
                if (!g.p.isValid) continue;
                const m = marks.get(g.p.name);
                if (isBot(g.p)) { if (t === 100) { for (const k of lit) if (chance(0.45, 0.6, 0.72)) m.add(k); if (Math.random() < 0.6) m.add(rand(0, 15)); } continue; }
                const lx = Math.floor(g.p.location.x) - g.ox, lz = Math.floor(g.p.location.z) - g.oz;
                const k = lx >= 0 && lx < 4 && lz >= 0 && lz < 4 && g.p.location.y < 1.3 ? lz * 4 + lx : -1;
                if (k >= 0 && prev.get(g.p.name) !== k) {
                    if (m.has(k)) m.delete(k); else m.add(k);
                    cmd(`setblock ${g.ox + lx} 0 ${g.oz + lz} ${m.has(k) ? "yellow_concrete" : "white_concrete"}`);
                    cmd(`playsound note.hat "${g.p.name}"`);
                }
                prev.set(g.p.name, k);
            }
            if (t % 20 === 0) actionbar(`§d配置の記憶 §7残り ${Math.ceil((240 - t) / 20)}秒`);
            await wait(2);
        }
        for (const g of grids) {
            const m = marks.get(g.p.name);
            let ok = 0, ng = 0;
            for (const k of m) lit.has(k) ? ok++ : ng++;
            const pts = Math.max(0, ok - ng);
            score2.set(g.p.name, (score2.get(g.p.name) ?? 0) + pts);
            for (const k of lit) cmd(`setblock ${g.ox + (k % 4)} 0 ${g.oz + Math.floor(k / 4)} ${m.has(k) ? "lime_concrete" : "red_concrete"}`);
            if (g.p.isValid) g.p.sendMessage(`§fラウンド${r}: 正解 ${ok} / まちがい ${ng} → ${pts}点`);
        }
        await wait(50);
    }
    const best = Math.max(0, ...score2.values());
    playing().filter((p) => score2.get(p.name) === best).forEach((p) => record(39, p.name, best, "max"));
    return best ? playing().filter((p) => score2.get(p.name) === best) : [];
}

// ===== v6 の共通処理 =====
const spawnAt = (type, loc) => { try { return dim().spawnEntity(type, loc); } catch { return undefined; } };
const endSurvive = (start, sec, soloSec = 45) => { const n = alive().length; return n === 0 || (start.length > 1 && n <= Math.max(1, Math.floor(start.length / 3))) || (start.length === 1 && sec >= soloSec); };
const safeFight = () => { cmd("gamerule pvp true"); cmd("effect @a[tag=playing] resistance 600 255 true"); cmd("effect @a[tag=playing] instant_health 1 10 true"); };
const nearestOf = (p, list) => list.filter((o) => o.id !== p.id).map((o) => ({ o, d: Math.hypot(o.location.x - p.location.x, o.location.z - p.location.z) })).sort((a, b) => a.d - b.d)[0];
// 乗り物を見ている方向へ押す(BOT は近くの相手の方へ)
function drive(veh, p, power, max, targets) {
    let dx, dz;
    if (isBot(p)) { const t = nearestOf(p, targets ?? alive()); if (!t) return; dx = t.o.location.x - p.location.x; dz = t.o.location.z - p.location.z; const d = Math.hypot(dx, dz) || 1; dx /= d; dz /= d; }
    else { const v = p.getViewDirection(); const d = Math.hypot(v.x, v.z) || 1; dx = v.x / d; dz = v.z / d; }
    const vel = veh.getVelocity();
    if (Math.hypot(vel.x, vel.z) < max) veh.applyImpulse({ x: dx * power, y: 0, z: dz * power });
    veh.setRotation({ x: 0, y: (Math.atan2(-dx, dz) * 180) / Math.PI });
}
function mount(p, type, loc) {
    const v = spawnAt(type, loc);
    if (v) { v.addTag("mmgplus_vehicle"); try { v.getComponent("minecraft:rideable")?.addRider(p); } catch {} }
    return v;
}
const riding = (p, type) => p.getComponent("minecraft:riding")?.entityRidingOn?.typeId === type;
function labels(list) { for (const [text, x, z] of list) { const e = spawnAt("mmgplus:board", { x, y: 2.5, z }); if (e) { e.addTag("mmgplus_label"); e.nameTag = text; } } }
const tops = (pts) => { const best = Math.max(0, ...pts.values()); return best ? playing().filter((p) => pts.get(p.name) === best) : []; };

// ===== 40. レーザー回避 =====
// 部屋の端から端へレーザーがゆっくり動く。低いレーザー(足元)はジャンプ、高いレーザー(頭)はしゃがんでよける
async function gameLaser() {
    const start = playing(), t0 = Date.now();
    title("§c§lレーザー回避", "§f低いのは§eジャンプ§f、高いのは§eしゃがみ§fでよける");
    await wait(50);
    const lasers = [];
    for (let t = 0; t < 2400 && !aborted(); t += 2) {
        const sec = (Date.now() - t0) / 1000;
        if (t % Math.max(30, 90 - Math.floor(sec) - level() * 6) === 0) {
            const axis = Math.random() < 0.5 ? "x" : "z", dir = Math.random() < 0.5 ? 1 : -1, high = Math.random() < 0.4;
            lasers.push({ axis, dir, pos: -9 * dir, high, speed: 0.12 + Math.min(0.2, sec / 300) + level() * 0.02 });
        }
        for (const L of lasers.slice()) {
            const prev = L.pos; L.pos += L.dir * L.speed * 2;
            const y = L.high ? 2.0 : 1.25;
            for (let k = -9; k <= 9; k += 0.75) cmd(`particle minecraft:redstone_wire_dust_particle ${L.axis === "x" ? L.pos : k} ${y} ${L.axis === "x" ? k : L.pos}`);
            for (const p of alive()) {
                const c = L.axis === "x" ? p.location.x : p.location.z;
                if ((c - prev) * (c - L.pos) > 0 && Math.abs(c - L.pos) > 0.3) continue; // 通り過ぎていない
                const dodge = L.high ? p.isSneaking : p.location.y > 1.45;
                if (isBot(p) ? !chance(0.7, 0.85, 0.95) : !dodge) out(p, L.high ? "§c頭のレーザーに当たった！(しゃがむ)" : "§c足のレーザーに当たった！(ジャンプ)");
            }
            if (Math.abs(L.pos) > 9.5) lasers.splice(lasers.indexOf(L), 1);
        }
        if (t % 20 === 0) actionbar(`§cレーザー回避 §f残り ${alive().length}人`);
        if (endSurvive(start, sec)) break;
        await wait(2);
    }
    return alive();
}

// ===== 41. しっぽ取り =====
// みんなしっぽ1本から。相手を叩くとしっぽを1本うばえる。60秒で一番多く持っていた人の勝ち
const tails = new Map();
world.afterEvents.entityHitEntity.subscribe((ev) => {
    const a = ev.damagingEntity, b = ev.hitEntity;
    if (a?.typeId !== "minecraft:player" || b?.typeId !== "minecraft:player" || score("game", "selectgame") !== 41 || !run.active) return;
    const tb = tails.get(b.name);
    if (!tb || tb.n <= 0 || tb.until > system.currentTick) return;
    tb.n--; tb.until = system.currentTick + 20;
    const ta = tails.get(a.name); if (ta) ta.n++;
    a.sendMessage(`§aしっぽをうばった！ (${ta?.n ?? 0}本)`); b.sendMessage("§cしっぽをとられた！");
    cmd(`playsound random.pop "${a.name}"`);
});
async function gameTails() {
    tails.clear(); safeFight();
    for (const p of playing()) tails.set(p.name, { n: 1, until: 0, e: spawnAt("mmgplus:tail", p.location) });
    title("§6§lしっぽ取り", "§f相手を叩いてしっぽをうばえ！");
    for (let t = 0; t < 1200 && !aborted(); t++) {
        for (const p of playing()) {
            const tl = tails.get(p.name); if (!tl?.e?.isValid) continue;
            const v = p.getViewDirection(), d = Math.hypot(v.x, v.z) || 1;
            tl.e.teleport({ x: p.location.x - (v.x / d) * 0.45, y: p.location.y + 0.55, z: p.location.z - (v.z / d) * 0.45 }, { rotation: { x: 0, y: p.getRotation().y } });
            tl.e.nameTag = tl.n > 1 ? `§6×${tl.n}` : tl.n === 0 ? "§7なし" : "";
        }
        if (t % 10 === 0) for (const p of playing()) p.onScreenDisplay.setActionBar(`§6しっぽ取り §fあなた: ${tails.get(p.name)?.n ?? 0}本  §7残り ${Math.ceil((1200 - t) / 20)}秒`);
        await wait(1);
    }
    cmd("gamerule pvp false");
    return tops(new Map([...tails].map(([n, v]) => [n, v.n])));
}

// ===== 42. ものまねポーズ =====
// お手本(向き + しゃがむ/ジャンプ/そのまま)が出る。合図の時に同じポーズをしていないと脱落
const DIRS = [["北", 180], ["東", -90], ["南", 0], ["西", 90]];
async function gamePose() {
    const start = playing();
    title("§d§lものまねポーズ", "§fお手本と同じ向き・ポーズで「ハイ！」を待とう", 50);
    await wait(50);
    for (let r = 1; r <= 20 && !aborted(); r++) {
        const [dn, yaw] = DIRS[rand(0, 3)], act = ["しゃがむ", "ジャンプ", "そのまま"][rand(0, 2)];
        const time = Math.max(14, 50 - r * 2 - level() * 3);
        title(`§l${dn}を向いて`, `§e${act}`, time);
        soundAll("note.pling", 1);
        await wait(time);
        title("§a§lハイ！", "", 10);
        if (act === "ジャンプ") await wait(3);
        for (const p of alive()) {
            const dy = Math.abs(((p.getRotation().y - yaw) % 360 + 540) % 360 - 180);
            const ok = dy < 45 && (act === "しゃがむ" ? p.isSneaking : act === "ジャンプ" ? p.location.y > 1.15 : !p.isSneaking && p.location.y < 1.15);
            if (isBot(p) ? !chance(0.75, 0.88, 0.96) : !ok) out(p, `§cちがうポーズ！(${dn}・${act})`);
        }
        if (endSurvive(start, r * 5, 60)) break;
        await wait(30);
    }
    return alive();
}

// ===== 43. ピクセルアート再現 =====
// ひとり1つの4x4のキャンバス。ふむたびに 白→赤→青→黄 と色が変わる。となりのお手本と同じにする。早くそろえた人が上
const PIX = ["white", "red", "blue", "yellow"];
async function gamePixel() {
    clearArena();
    const players = playing();
    const target = Array.from({ length: 16 }, () => (Math.random() < 0.35 ? 0 : rand(1, 3)));
    const grids = players.map((p, i) => ({ p, ox: (i % 4) * 11 - 20, oz: Math.floor(i / 4) * 8 - 10, cells: Array(16).fill(0), done: 0 }));
    for (const g of grids) {
        cmd(`fill ${g.ox - 1} 0 ${g.oz - 1} ${g.ox + 9} 0 ${g.oz + 4} polished_deepslate`);
        for (let k = 0; k < 16; k++) {
            cmd(`setblock ${g.ox + (k % 4)} 0 ${g.oz + Math.floor(k / 4)} white_concrete`);
            cmd(`setblock ${g.ox + 5 + (k % 4)} 1 ${g.oz + Math.floor(k / 4)} ${PIX[target[k]]}_concrete`); // お手本(1段上)
        }
        g.p.teleport({ x: g.ox + 2, y: 1, z: g.oz - 0.5 });
    }
    title("§b§lピクセルアート再現", "§f右のお手本と同じ色にしよう(ふむと色が変わる)", 50);
    const t0 = Date.now(), prev = new Map(), order = [];
    for (let t = 0; t < 1600 && !aborted(); t += 2) {
        for (const g of grids) {
            if (!g.p.isValid || g.done) continue;
            if (isBot(g.p)) { if (t % [44, 34, 26][botStr()] === 0) { const k = g.cells.findIndex((c, i) => c !== target[i]); if (k >= 0) { g.cells[k] = target[k]; cmd(`setblock ${g.ox + (k % 4)} 0 ${g.oz + Math.floor(k / 4)} ${PIX[target[k]]}_concrete`); } } }
            else {
                const lx = Math.floor(g.p.location.x) - g.ox, lz = Math.floor(g.p.location.z) - g.oz;
                const k = lx >= 0 && lx < 4 && lz >= 0 && lz < 4 && g.p.location.y < 1.3 ? lz * 4 + lx : -1;
                if (k >= 0 && prev.get(g.p.name) !== k) { g.cells[k] = (g.cells[k] + 1) % 4; cmd(`setblock ${g.ox + lx} 0 ${g.oz + lz} ${PIX[g.cells[k]]}_concrete`); cmd(`playsound note.hat "${g.p.name}"`); }
                prev.set(g.p.name, k);
            }
            if (g.cells.every((c, i) => c === target[i])) { g.done = (Date.now() - t0) / 1000; order.push(g.p); world.sendMessage(`§b${order.length}位 §f${g.p.name} §7${g.done.toFixed(1)}秒で完成！`); record(43, g.p.name, g.done, "min"); }
        }
        if (t % 20 === 0) actionbar(`§bピクセルアート §7残り ${Math.ceil((1600 - t) / 20)}秒`);
        if (grids.every((g) => g.done || !g.p.isValid)) break;
        await wait(2);
    }
    if (order.length) return order.slice(0, players.length === 1 ? 1 : Math.min(3, players.length - 1));
    const m = new Map(grids.map((g) => [g.p.name, g.cells.filter((c, i) => c === target[i]).length]));
    return tops(m);
}

// ===== 44. 卵キャッチ =====
// 空から卵がふってくる(落ちる所に影)。下でキャッチすると1点、金の卵は3点
async function gameEggs() {
    const pts = new Map(), eggs = [];
    title("§e§l卵キャッチ", "§f落ちてくる卵の下に行こう！ 金の卵は3点");
    await wait(40);
    for (let t = 0; t < 1200 && !aborted(); t++) {
        if (t % Math.max(4, 14 - level() * 2) === 0) {
            const gold = Math.random() < 0.1, x = rand(-9, 9) + 0.5, z = rand(-9, 9) + 0.5;
            const e = spawnAt(gold ? "mmgplus:golden_egg" : "mmgplus:egg", { x, y: 16, z });
            if (e) eggs.push({ e, x, z, y: 16, gold, v: 0.12 + Math.random() * 0.1 });
        }
        for (const g of eggs.slice()) {
            g.y -= g.v; if (g.e.isValid) g.e.teleport({ x: g.x, y: g.y, z: g.z });
            if (t % 4 === 0) cmd(`particle minecraft:basic_smoke_particle ${g.x} 1.05 ${g.z}`);
            const catcher = playing().find((p) => Math.hypot(p.location.x - g.x, p.location.z - g.z) < 1.1 && g.y > p.location.y && g.y < p.location.y + 2.6);
            if (catcher || g.y <= 1) {
                eggs.splice(eggs.indexOf(g), 1); try { g.e.remove(); } catch {}
                if (catcher) { pts.set(catcher.name, (pts.get(catcher.name) ?? 0) + (g.gold ? 3 : 1)); cmd(`playsound ${g.gold ? "random.levelup" : "random.orb"} "${catcher.name}"`); }
                else cmd(`particle minecraft:egg_destroy_emitter ${g.x} 1.1 ${g.z}`);
            }
        }
        // BOT は一番近い卵の下へ
        if (t % 6 === 0) for (const p of playing().filter(isBot)) { const g = eggs.filter((e) => e.y < 10).sort((a, b) => Math.hypot(a.x - p.location.x, a.z - p.location.z) - Math.hypot(b.x - p.location.x, b.z - p.location.z))[0]; if (g && chance(0.4, 0.6, 0.8)) p.teleport({ x: p.location.x + Math.sign(g.x - p.location.x) * Math.min(1, Math.abs(g.x - p.location.x)), y: 1, z: p.location.z + Math.sign(g.z - p.location.z) * Math.min(1, Math.abs(g.z - p.location.z)) }); }
        if (t % 10 === 0) for (const p of playing()) p.onScreenDisplay.setActionBar(`§e卵キャッチ §fあなた: ${pts.get(p.name) ?? 0}点  §7残り ${Math.ceil((1200 - t) / 20)}秒`);
        await wait(1);
    }
    eggs.forEach((g) => { try { g.e.remove(); } catch {} });
    const w = tops(pts); w.forEach((p) => record(44, p.name, pts.get(p.name), "max")); return w;
}

// ===== 45. コイン噴水 =====
// 真ん中の噴水からコインが飛び出す。拾うと1枚。相手を叩くとコインを3枚落とさせられる
const coins = new Map();
const coinList = [];
function dropCoins(x, z, n) {
    for (let i = 0; i < n; i++) {
        const a = Math.random() * Math.PI * 2, r = 1.5 + Math.random() * 2;
        const e = spawnAt("mmgplus:coin", { x, y: 1.3, z }); if (e) coinList.push({ e, from: { x, z }, to: { x: x + Math.cos(a) * r, z: z + Math.sin(a) * r }, t: 0, len: 12 });
    }
}
world.afterEvents.entityHitEntity.subscribe((ev) => {
    const a = ev.damagingEntity, b = ev.hitEntity;
    if (a?.typeId !== "minecraft:player" || b?.typeId !== "minecraft:player" || score("game", "selectgame") !== 45 || !run.active) return;
    const n = Math.min(3, coins.get(b.name) ?? 0); if (!n) return;
    coins.set(b.name, coins.get(b.name) - n); dropCoins(b.location.x, b.location.z, n);
    b.sendMessage(`§cコインを${n}枚落とした！`); cmd(`playsound random.break "${b.name}"`);
});
async function gameCoins() {
    coins.clear(); coinList.length = 0; safeFight();
    cmd("fill -2 1 -2 2 1 2 quartz_block"); cmd("fill -1 2 -1 1 2 1 light_blue_stained_glass"); cmd("setblock 0 3 0 gold_block");
    for (const p of playing()) coins.set(p.name, 0);
    title("§6§lコイン噴水", "§fコインを拾え！ 叩くと相手がコインを落とす");
    for (let t = 0; t < 1200 && !aborted(); t++) {
        if (t % Math.max(3, 8 - level()) === 0) {
            const a = Math.random() * Math.PI * 2, r = 3 + Math.random() * 7;
            const e = spawnAt("mmgplus:coin", { x: 0.5, y: 4, z: 0.5 }); if (e) coinList.push({ e, from: { x: 0.5, z: 0.5 }, to: { x: 0.5 + Math.cos(a) * r, z: 0.5 + Math.sin(a) * r }, t: 0, len: 20 });
            if (t % 20 === 0) cmd("particle minecraft:water_splash_particle 0.5 3.5 0.5");
        }
        for (const c of coinList.slice()) {
            if (!c.e.isValid) { coinList.splice(coinList.indexOf(c), 1); continue; }
            if (c.t < c.len) { c.t++; const k = c.t / c.len; c.e.teleport({ x: c.from.x + (c.to.x - c.from.x) * k, y: 1.2 + Math.sin(k * Math.PI) * 4, z: c.from.z + (c.to.z - c.from.z) * k }); continue; }
            const p = playing().find((q) => Math.hypot(q.location.x - c.to.x, q.location.z - c.to.z) < 1.2);
            if (p) { c.e.remove(); coinList.splice(coinList.indexOf(c), 1); coins.set(p.name, (coins.get(p.name) ?? 0) + 1); cmd(`playsound random.orb "${p.name}" ~ ~ ~ 0.6 1.5`); }
        }
        if (t % 10 === 0) for (const p of playing()) p.onScreenDisplay.setActionBar(`§6コイン噴水 §fあなた: §e${coins.get(p.name) ?? 0}枚  §7残り ${Math.ceil((1200 - t) / 20)}秒`);
        await wait(1);
    }
    coinList.forEach((c) => { try { c.e.remove(); } catch {} }); coinList.length = 0;
    cmd("gamerule pvp false");
    const w = tops(coins); w.forEach((p) => record(45, p.name, coins.get(p.name), "max")); return w;
}

// ===== 46. ふくらむ風船 =====
// 順番にポンプを1〜3回押す。風船が割れたら、その時押していた人がアウト。3分の1になるまで
async function gameBalloon() {
    const start = playing();
    cmd("fill -1 1 -1 1 1 1 red_concrete");
    let balloon, size, limit;
    const fresh = () => { try { balloon?.remove(); } catch {} balloon = spawnAt("mmgplus:balloon", { x: 0.5, y: 2, z: 0.5 }); size = 3; limit = rand(10, 24); balloon?.setProperty("mmgplus:size", size); };
    fresh();
    title("§c§lふくらむ風船", "§f順番にポンプを押そう。割った人がアウト");
    await wait(40);
    for (let turn = 0; turn < 200 && !aborted(); turn++) {
        const order = alive();
        if (endSurvive(start, turn * 10, 999) || (start.length === 1 && turn >= 6)) break;
        const p = order[turn % order.length];
        title(`§l${p.name} の番`, "", 20);
        let n = 1;
        if (isBot(p)) { await wait(20); n = size + 3 > limit && chance(0.2, 0.5, 0.7) ? 1 : rand(1, 3); }
        else {
            const r = await Promise.race([new ActionFormData().title("ふくらむ風船").body(`ポンプを何回押す？\n§7(今の大きさ ${size})`).button("§l1回").button("§l2回").button("§l3回").show(p).catch(() => ({ canceled: true })), wait(200).then(() => ({ canceled: true }))]);
            try { uiManager.closeAllForms(p); } catch {}
            n = r.canceled ? 1 : r.selection + 1;
        }
        for (let i = 0; i < n && !aborted(); i++) {
            size++; balloon?.setProperty("mmgplus:size", Math.min(30, size));
            soundAll("random.pop", 0.5 + size * 0.05);
            await wait(8);
            if (size >= limit) {
                cmd("particle minecraft:huge_explosion_emitter 0.5 3 0.5"); soundAll("random.explode", 1.4);
                out(p, "§c風船が割れた！"); title(`§c§lパーン！`, `§f${p.name} がアウト`, 30);
                await wait(40); fresh(); break;
            }
        }
        await wait(10);
    }
    try { balloon?.remove(); } catch {}
    return alive();
}

// ===== 47. まっくらスイカ割り =====
// 真っ暗の中、スイカが鳴らす音をたよりに探して叩く。叩いた数で勝負
const melonPts = new Map();
world.afterEvents.entityHitEntity.subscribe((ev) => {
    const a = ev.damagingEntity, b = ev.hitEntity;
    if (a?.typeId !== "minecraft:player" || b?.typeId !== "mmgplus:melon" || !run.active) return;
    melonPts.set(a.name, (melonPts.get(a.name) ?? 0) + 1);
    cmd(`particle minecraft:large_explosion ${b.location.x} ${b.location.y + 0.5} ${b.location.z}`);
    cmd(`playsound random.break "${a.name}"`); a.sendMessage(`§aスイカ割り成功！ (${melonPts.get(a.name)}個)`);
    b.remove();
});
async function gameMelon() {
    melonPts.clear();
    cmd("effect @a[tag=playing] darkness 70 0 true"); cmd("effect @a[tag=playing] blindness 70 0 true");
    title("§2§lまっくらスイカ割り", "§f音のする方へ行って、スイカを叩け！");
    for (let t = 0; t < 1200 && !aborted(); t += 5) {
        const ms = dim().getEntities({ type: "mmgplus:melon" });
        for (let n = ms.length; n < Math.max(3, Math.ceil(playing().length / 2)); n++) spawnAt("mmgplus:melon", { x: rand(-9, 9) + 0.5, y: 1, z: rand(-9, 9) + 0.5 });
        if (t % 15 === 0) for (const m of ms) cmd(`playsound note.bell @a ${m.location.x} ${m.location.y + 1} ${m.location.z} 1.5 ${(0.8 + Math.random() * 0.4).toFixed(2)}`);
        if (t % 20 === 0) for (const p of playing().filter(isBot)) { const m = ms[rand(0, Math.max(0, ms.length - 1))]; if (m && chance(0.15, 0.25, 0.4)) { melonPts.set(p.name, (melonPts.get(p.name) ?? 0) + 1); m.remove(); } }
        if (t % 10 === 0) for (const p of playing()) p.onScreenDisplay.setActionBar(`§2スイカ割り §fあなた: ${melonPts.get(p.name) ?? 0}個  §7残り ${Math.ceil((1200 - t) / 20)}秒`);
        await wait(5);
    }
    cmd("effect @a[tag=playing] clear");
    return tops(melonPts);
}

// ===== 48. 下がる天井 =====
// 足場(y=4)の上に立つ。トゲの天井が下がってくる。足場の穴に落ちて隠れれば助かる。穴は毎回へる
async function gameCeiling() {
    const start = playing();
    title("§8§l下がる天井", "§f足場の穴に入って天井から隠れろ！");
    for (let r = 1; r <= 12 && !aborted(); r++) {
        cmd("fill -7 1 -7 7 8 7 air");
        cmd("fill -7 3 -7 7 3 7 polished_andesite");
        const holes = Math.max(1, alive().length - 1 - Math.floor(r / 3));
        const hs = []; while (hs.length < holes) { const h = [rand(-6, 6), rand(-6, 6)]; if (!hs.some((o) => o[0] === h[0] && o[1] === h[1])) hs.push(h); }
        for (const [x, z] of hs) cmd(`setblock ${x} 3 ${z} air`);
        cmd("tp @a[tag=playing,tag=!mmgplus_out] 0 4 0");
        title(`§lラウンド ${r}`, `§f穴は ${holes}個`, 20);
        await wait(30);
        const speed = Math.max(6, 20 - r * 2 - level() * 2);
        for (let y = 8; y >= 5 && !aborted(); y--) {
            if (y < 8) cmd(`fill -7 ${y + 1} -7 7 ${y + 1} air`);
            cmd(`fill -7 ${y} -7 7 ${y} polished_blackstone`);
            soundAll("block.grindstone.use", 0.6);
            if (y === 6) for (const p of alive().filter(isBot)) if (chance(0.5, 0.7, 0.9)) { const [x, z] = hs[rand(0, hs.length - 1)]; p.teleport({ x: x + 0.5, y: 1, z: z + 0.5 }); }
            await wait(speed);
        }
        for (const p of alive()) if (p.location.y >= 3.5) out(p, "§c天井につぶされた！");
        cmd("fill -7 4 -7 7 8 7 air");
        if (endSurvive(start, r * 8, 999) || (start.length === 1 && r >= 5)) break;
        await wait(20);
    }
    cmd("fill -7 1 -7 7 8 7 air");
    return alive();
}

// ===== 49. 風船割り合戦 =====
// みんな頭の上に風船3つ。弓や素手で相手の風船を割る。全部割られたらアウト
const myBalloons = new Map();
function popBalloon(e, by) {
    for (const [name, list] of myBalloons) {
        const i = list.indexOf(e); if (i < 0 || name === by?.name) continue;
        list.splice(i, 1); try { e.remove(); } catch {}
        cmd(`particle minecraft:large_explosion ${e.location.x} ${e.location.y} ${e.location.z}`); soundAll("random.pop", 1.2);
        const p = world.getPlayers({ name })[0];
        if (p) { p.sendMessage(`§c風船が割られた！ 残り${list.length}個`); if (!list.length) out(p, "§c風船が全部割れた！"); }
        by?.sendMessage?.("§a風船を割った！");
    }
}
world.afterEvents.projectileHitEntity.subscribe((ev) => { const e = ev.getEntityHit()?.entity; if (e?.typeId === "mmgplus:balloon" && score("game", "selectgame") === 49) popBalloon(e, ev.source); });
world.afterEvents.entityHitEntity.subscribe((ev) => { if (ev.hitEntity?.typeId === "mmgplus:balloon" && score("game", "selectgame") === 49) popBalloon(ev.hitEntity, ev.damagingEntity); });
async function gameBalloonWar() {
    const start = playing(); myBalloons.clear(); safeFight();
    for (const p of playing()) {
        const list = []; for (let i = 0; i < 3; i++) { const e = spawnAt("mmgplus:balloon", p.location); if (e) { e.setProperty("mmgplus:size", 0); list.push(e); } }
        myBalloons.set(p.name, list);
    }
    cmd("give @a[tag=playing] bow 1"); cmd("give @a[tag=playing] arrow 64");
    title("§c§l風船割り合戦", "§f弓や素手で相手の風船を割れ！");
    const t0 = Date.now();
    for (let t = 0; t < 1800 && !aborted(); t++) {
        for (const p of alive()) (myBalloons.get(p.name) ?? []).forEach((e, i) => { if (e.isValid) e.teleport({ x: p.location.x + Math.cos(i * 2.1 + t * 0.03) * 0.6, y: p.location.y + 2.1, z: p.location.z + Math.sin(i * 2.1 + t * 0.03) * 0.6 }); });
        if (t % 40 === 0) for (const p of alive().filter(isBot)) if (chance(0.08, 0.15, 0.25)) { const v = nearestOf(p, alive()); const b = v && myBalloons.get(v.o.name)?.[0]; if (b) popBalloon(b, p); }
        if (t % 20 === 0) cmd("kill @e[type=arrow,x=-12,y=0,z=-12,dx=24,dy=10,dz=24]");
        if (t % 10 === 0) actionbar(`§c風船割り合戦 §f残り ${alive().length}人`);
        if (endSurvive(start, (Date.now() - t0) / 1000, 30)) break;
        await wait(1);
    }
    for (const list of myBalloons.values()) list.forEach((e) => { try { e.remove(); } catch {} });
    cmd("clear @a[tag=playing] bow"); cmd("clear @a[tag=playing] arrow"); cmd("gamerule pvp false");
    const left = new Map(alive().map((p) => [p.name, myBalloons.get(p.name)?.length ?? 0]));
    return start.length > 1 ? tops(left) : alive();
}

// ===== 50. ボヨンボール =====
// はねまわる大きなボールをよける。ボールは10秒ごとにふえる。当たったら脱落
async function gameBoyon() {
    const start = playing(), balls = [], t0 = Date.now();
    const add = () => { const e = spawnAt("mmgplus:boyon", { x: 0.5, y: 8, z: 0.5 }); if (e) balls.push({ e, x: rand(-6, 6), y: 8, z: rand(-6, 6), vx: (Math.random() - 0.5) * 0.5, vy: 0, vz: (Math.random() - 0.5) * 0.5 }); };
    title("§d§lボヨンボール", "§fはねるボールに当たるな！");
    await wait(30); add(); add();
    for (let t = 0; t < 2400 && !aborted(); t++) {
        const sec = (Date.now() - t0) / 1000;
        if (t % Math.max(100, 220 - level() * 20) === 0 && t > 0) { add(); soundAll("mob.slime.big", 1); }
        for (const b of balls) {
            b.vy -= 0.04; b.x += b.vx; b.y += b.vy; b.z += b.vz;
            if (b.y < 1) { b.y = 1; b.vy = 0.65 + Math.random() * 0.2; cmd(`playsound mob.slime.big @a ${b.x} 1 ${b.z} 0.6 1.3`); }
            if (Math.abs(b.x) > 8) { b.x = Math.sign(b.x) * 8; b.vx = -b.vx; }
            if (Math.abs(b.z) > 8) { b.z = Math.sign(b.z) * 8; b.vz = -b.vz; }
            if (b.e.isValid) b.e.teleport({ x: b.x, y: b.y, z: b.z });
            for (const p of alive()) if (Math.hypot(p.location.x - b.x, p.location.y + 0.9 - (b.y + 1), p.location.z - b.z) < 1.9) { if (isBot(p) && chance(0.5, 0.7, 0.85)) continue; out(p, "§cボールに当たった！"); }
        }
        if (t % 20 === 0) actionbar(`§dボヨンボール §f残り ${alive().length}人  ボール ${balls.length}個`);
        if (endSurvive(start, sec)) break;
        await wait(1);
    }
    balls.forEach((b) => { try { b.e.remove(); } catch {} });
    return alive();
}

// ===== 51. ワニの歯 =====
// 巨大なワニ(長さ約14マス)が大きく口を開けている。順番に口の中の歯を1本叩く。1本だけ「かまれる歯」がある。3分の1になるまで
// 歯の位置: ワニのモデルの下あご(y=5px、x=-5.5/4.5px、z=-19〜-7px)を、ワニの位置・180度回転・4倍に合わせてワールドの座標にしたもの
const CROC_AT = { x: 0.5, y: 1, z: -2.5 }, CROC_S = 4 / 16;
const TOOTH_SPOTS = [-5.5, 4.5].flatMap((mx) => [-19, -16, -13, -10].map((mz) => ({ x: CROC_AT.x - mx * CROC_S, y: CROC_AT.y + 5 * CROC_S, z: CROC_AT.z - mz * CROC_S })));
let toothHit = null;
world.afterEvents.entityHitEntity.subscribe((ev) => { if (ev.hitEntity?.typeId === "mmgplus:tooth" && ev.damagingEntity?.typeId === "minecraft:player") toothHit = { p: ev.damagingEntity, e: ev.hitEntity }; });
async function gameCroc() {
    const start = playing();
    const croc = spawnAt("mmgplus:croc", CROC_AT); croc?.setRotation({ x: 0, y: 180 });
    let teeth = [], bad;
    const reset = () => {
        teeth.forEach((e) => { try { e.remove(); } catch {} });
        teeth = TOOTH_SPOTS.map((p) => spawnAt("mmgplus:tooth", p)).filter(Boolean);
        bad = teeth[rand(0, teeth.length - 1)]; croc?.setProperty("mmgplus:bite", 0);
    };
    reset();
    cmd("tp @a[tag=playing] 0.5 1 6 facing 0.5 2 0");
    title("§2§l巨大ワニの歯", "§f順番に、口の中の歯を1本叩こう。かまれたらアウト");
    await wait(50);
    for (let turn = 0; turn < 200 && !aborted(); turn++) {
        const order = alive();
        if (endSurvive(start, turn * 10, 999) || (start.length === 1 && turn >= 6)) break;
        const p = order[turn % order.length];
        title(`§l${p.name} の番`, `§f口の中の歯を1本叩いて §7(残り ${teeth.length}本)`, 30);
        toothHit = null;
        let hitE;
        for (let t = 0; t < 200 && !aborted(); t += 2) {
            if (isBot(p) && t === 30) { hitE = teeth[rand(0, teeth.length - 1)]; p.teleport({ x: hitE.location.x, y: 1, z: hitE.location.z + 1.2 }); }
            if (toothHit && toothHit.p.name === p.name) hitE = toothHit.e;
            if (hitE) break;
            if (t % 20 === 0) cmd(`playsound note.hat @a ${CROC_AT.x} 2 ${CROC_AT.z} 0.5 ${(0.8 + t / 400).toFixed(2)}`); // カチ…カチ…
            await wait(2);
        }
        hitE ??= teeth[rand(0, teeth.length - 1)]; // 時間切れは勝手に1本
        if (hitE === bad) {
            croc?.setProperty("mmgplus:bite", 1);
            soundAll("mob.ravager.bite", 0.7); soundAll("random.explode", 0.6);
            cmd("camerashake add @a[tag=playing] 0.8 0.6 positional");
            cmd(`particle minecraft:huge_explosion_emitter ${CROC_AT.x} 2.5 ${CROC_AT.z + 3}`);
            out(p, "§cワニにかまれた！"); title("§c§lガブッ！！", `§f${p.name} がアウト`, 40);
            await wait(50); reset();
        } else {
            soundAll("random.click", 1.4); teeth.splice(teeth.indexOf(hitE), 1); try { hitE.remove(); } catch {}
            p.sendMessage("§aセーフ！");
            await wait(12);
        }
    }
    teeth.forEach((e) => { try { e.remove(); } catch {} }); try { croc?.remove(); } catch {}
    return alive();
}

// ===== 52. コマぶつけ / 57. バンパーカー =====
// 乗り物に乗って、見ている方向へ進む。ぶつけて相手を場外(赤い線の外)へ。3分の1になるまで
async function gameBumper(type, R, name) {
    const start = playing(), t0 = Date.now();
    start.forEach((p, i) => { const a = (i / start.length) * Math.PI * 2; mount(p, type, { x: Math.cos(a) * (R - 3) + 0.5, y: 1, z: Math.sin(a) * (R - 3) + 0.5 }); });
    title(`§l${name}`, "§f見ている方へ進む。ぶつけて場外へ！");
    await wait(40);
    for (let t = 0; t < 2400 && !aborted(); t++) {
        const sec = (Date.now() - t0) / 1000;
        const vs = dim().getEntities({ type, tags: ["mmgplus_vehicle"] });
        for (const p of alive()) {
            const v = p.getComponent("minecraft:riding")?.entityRidingOn;
            if (v?.typeId === type) drive(v, p, 0.06, 0.55, alive());
            else if (t % 20 === 0) { const nv = vs.find((x) => !x.getComponent("minecraft:rideable")?.getRiders().length); if (nv) { try { nv.getComponent("minecraft:rideable").addRider(p); } catch {} } }
            if (Math.hypot(p.location.x - 0.5, p.location.z - 0.5) > R + 0.5) { out(p, "§c場外！"); cmd(`ride "${p.name}" stop_riding`); }
        }
        // 乗り物どうしがぶつかったらはね返す
        for (let i = 0; i < vs.length; i++) for (let j = i + 1; j < vs.length; j++) {
            const a = vs[i], b = vs[j], dx = b.location.x - a.location.x, dz = b.location.z - a.location.z, d = Math.hypot(dx, dz);
            if (d > 0.01 && d < 1.4) {
                const va = a.getVelocity(), vb = b.getVelocity(), k = 0.5 + Math.hypot(va.x - vb.x, va.z - vb.z) * 1.6;
                b.applyImpulse({ x: (dx / d) * k, y: 0.15, z: (dz / d) * k }); a.applyImpulse({ x: (-dx / d) * k, y: 0.15, z: (-dz / d) * k });
                cmd(`playsound random.anvil_land @a ${a.location.x} 1 ${a.location.z} 0.4 1.8`);
            }
        }
        if (t % 20 === 0) actionbar(`§e${name} §f残り ${alive().length}人`);
        if (endSurvive(start, sec)) break;
        await wait(1);
    }
    cmd("ride @a stop_riding"); cmd(`kill @e[type=${type}]`);
    return alive();
}
function buildRing(R, floor) {
    clearArena();
    disc(R, floor);
    for (let a = 0; a < 360; a += 3) cmd(`setblock ${Math.round(Math.cos((a * Math.PI) / 180) * (R + 1))} 0 ${Math.round(Math.sin((a * Math.PI) / 180) * (R + 1))} red_concrete`);
}

// ===== 53. 旗あげゲーム =====
// 床が4つ(赤↑白↑ / 赤↑白↓ / 赤↓白↑ / 赤↓白↓)。指示を聞いて、旗の形に合う床へ移動。まちがえたらアウト
// 指示の読み上げの声は、あとでだいきがくれる音を入れる(今は文字と効果音)
const FLAG_Q = [["赤↑白↑", -4, -4], ["赤↑白↓", 5, -4], ["赤↓白↑", -4, 5], ["赤↓白↓", 5, 5]];
function makeOrder(state, lv) {
    // state: [赤が上か, 白が上か]
    const pick = () => ["赤", "白", "両方"][rand(0, lv >= 3 ? 2 : 1)];
    const one = () => { const f = pick(), up = Math.random() < 0.5, neg = Math.random() < (lv >= 2 ? 0.3 : 0.1); return { f, up, neg, text: `${f}${up ? "上げ" : "下げ"}${neg ? "ない" : "て"}` }; };
    const parts = [one()]; if (lv >= 2 && Math.random() < 0.5) parts.push(one());
    let [r, w] = state;
    for (const o of parts) if (!o.neg) { if (o.f !== "白") r = o.up; if (o.f !== "赤") w = o.up; }
    // ひっかけ:「赤上げ……ない！」
    const fake = lv >= 3 && Math.random() < 0.2;
    const text = fake ? `${parts[0].f}${parts[0].up ? "上げ" : "下げ"}……ない！` : parts.map((o) => o.text).join("、");
    if (fake) [r, w] = state;
    return { text, state: [r, w] };
}
async function gameFlags() {
    const start = playing();
    cmd("fill -9 0 -9 0 0 0 pink_concrete"); cmd("fill 1 0 -9 9 0 0 orange_concrete"); cmd("fill -9 0 1 0 0 9 light_blue_concrete"); cmd("fill 1 0 1 9 0 9 gray_concrete");
    labels(FLAG_Q.map(([t, x, z]) => [`§l${t.replace("赤", "§c赤").replace("白", "§f白")}`, x, z]));
    let state = [false, false];
    cmd("tp @a[tag=playing] 5 1 5");
    title("§l旗あげゲーム", "§f指示どおりの旗の形の床へ移動しよう(今は 赤↓白↓)", 60);
    await wait(70);
    for (let r = 1; r <= 25 && !aborted(); r++) {
        const o = makeOrder(state, Math.min(3, 1 + Math.floor((r + level()) / 5)));
        state = o.state;
        title(`§l${o.text}`, "", 40); soundAll("note.pling", 1.2);
        await wait(Math.max(25, 60 - r * 2 - level() * 3));
        const want = FLAG_Q[(state[0] ? 0 : 2) + (state[1] ? 0 : 1)];
        for (const p of alive()) {
            const q = FLAG_Q[(p.location.z < 0.5 ? 0 : 2) + (p.location.x < 0.5 ? 0 : 1)];
            if (isBot(p)) { if (chance(0.6, 0.72, 0.82)) p.teleport({ x: want[1] + 0.5, y: 1, z: want[2] + 0.5 }); else out(p, "§cまちがえた！"); continue; }
            if (q !== want) out(p, `§cまちがえた！ 正しくは ${want[0]}`);
        }
        actionbar(`§f今の旗: §l${want[0]}`);
        if (endSurvive(start, r * 4, 60)) break;
        await wait(20);
    }
    return alive();
}

// ===== 54. お皿バランス =====
// 頭の上にお皿の塔。急に動いたり曲がったりすると傾く。傾きすぎると落ちてスタートからやり直し。1〜3位がポイント
async function gamePlates() {
    const players = playing(), st = new Map(), order = [], t0 = Date.now();
    players.forEach((p, i) => { p.teleport({ x: -3 + (i % 7) + 0.5, y: 1, z: -44 }, { rotation: { x: 0, y: 0 } }); st.set(p.name, { e: spawnAt("mmgplus:plates", p.location), tilt: 0, v: { x: 0, z: 0 } }); });
    title("§b§lお皿バランス", "§fお皿を落とさずにゴールへ。急ぐと傾く！");
    await wait(50);
    cmd(`fill ${-DASH_W} 1 -41 ${DASH_W} 2 -41 air`);
    for (let t = 0; t < 3600 && !aborted(); t++) {
        for (const p of playing()) {
            const s = st.get(p.name); if (!s || order.includes(p)) continue;
            const v = p.getVelocity(), sp = Math.hypot(v.x, v.z), acc = Math.hypot(v.x - s.v.x, v.z - s.v.z);
            const turn = s.v.x * v.z - s.v.z * v.x;
            s.tilt += (Math.sign(turn) || (Math.random() < 0.5 ? 1 : -1)) * acc * (6 + level()) + Math.sign(s.tilt) * sp * 0.25 * (p.isSprinting ? 3 : 1);
            if (sp < 0.03) s.tilt *= 0.93;
            if (isBot(p)) { s.tilt *= 0.8; if (t % 4 === 0) p.teleport({ x: p.location.x, y: 1, z: p.location.z + [0.3, 0.4, 0.5][botStr()] }); }
            s.v = { x: v.x, z: v.z };
            if (s.e?.isValid) { s.e.teleport({ x: p.location.x, y: p.location.y + 2.05, z: p.location.z }, { rotation: { x: 0, y: p.getRotation().y } }); s.e.setProperty("mmgplus:tilt", Math.max(-10, Math.min(10, Math.round(s.tilt)))); }
            if (Math.abs(s.tilt) > 10) { s.tilt = 0; cmd(`playsound random.glass "${p.name}"`); p.sendMessage("§cお皿が落ちた！ スタートから"); p.teleport({ x: 0.5, y: 1, z: -40 }, { rotation: { x: 0, y: 0 } }); }
            if (p.location.z >= 44) { order.push(p); const sec = (Date.now() - t0) / 1000; world.sendMessage(`§b${order.length}位 §f${p.name} §7${sec.toFixed(1)}秒`); record(54, p.name, sec, "min"); }
            if (t % 5 === 0) p.onScreenDisplay.setActionBar(`§bお皿バランス §f傾き ${"■".repeat(Math.min(10, Math.round(Math.abs(s.tilt))))}${"□".repeat(10 - Math.min(10, Math.round(Math.abs(s.tilt))))}  §7ゴールまで ${Math.max(0, Math.round(44 - p.location.z))}m`);
        }
        if (players.every((p) => order.includes(p) || !p.isValid)) break;
        await wait(1);
    }
    for (const s of st.values()) try { s.e?.remove(); } catch {}
    return order.slice(0, players.length === 1 ? 1 : Math.min(3, players.length - 1));
}
function buildStraight(floor, posts) {
    clearArena();
    cmd(`fill ${-DASH_W} 0 -46 ${DASH_W} 0 46 ${floor}`);
    cmd(`fill ${-DASH_W - 1} 1 -46 ${-DASH_W - 1} 2 46 glass`); cmd(`fill ${DASH_W + 1} 1 -46 ${DASH_W + 1} 2 46 glass`); cmd(`fill ${-DASH_W} 1 -46 ${DASH_W} 2 -46 glass`);
    cmd(`fill ${-DASH_W} 1 -41 ${DASH_W} 2 -41 glass`);
    for (let x = -DASH_W; x <= DASH_W; x++) for (const z of [44, 45]) cmd(`setblock ${x} 0 ${z} ${(x + z) % 2 === 0 ? "white_concrete" : "black_concrete"}`);
    if (posts) for (let z = -34; z < 40; z += 6) for (let k = 0; k < 2; k++) cmd(`fill ${rand(-DASH_W, DASH_W)} 1 ${z} ${rand(-DASH_W, DASH_W)} 1 ${z} oak_fence`);
}

// ===== 55. 大玉ころがし =====
// 大玉に乗って、見ている方へ転がしてゴールへ。柵をよけながら進む。1〜3位がポイント
async function gameBigball() {
    const players = playing(), order = [], t0 = Date.now();
    players.forEach((p, i) => mount(p, "mmgplus:bigball", { x: -3 + (i % 4) * 2 + 0.5, y: 1, z: -44 + Math.floor(i / 4) * 2 }));
    for (const n of ["3", "2", "1"]) { title(`§l${n}`, "§f見ている方へ転がる"); soundAll("note.pling", 0.8); await wait(20); }
    cmd(`fill ${-DASH_W} 1 -41 ${DASH_W} 2 -41 air`); title("§a§lGO!"); soundAll("note.pling", 1.6);
    for (let t = 0; t < 3600 && !aborted(); t++) {
        for (const p of playing()) {
            if (order.includes(p)) continue;
            const v = p.getComponent("minecraft:riding")?.entityRidingOn;
            if (v?.typeId === "mmgplus:bigball") {
                if (isBot(p)) { const vel = v.getVelocity(); if (Math.hypot(vel.x, vel.z) < [0.25, 0.32, 0.4][botStr()]) v.applyImpulse({ x: (Math.random() - 0.5) * 0.04, y: 0, z: 0.05 }); }
                else drive(v, p, 0.035, 0.42);
            } else if (t % 20 === 0) mount(p, "mmgplus:bigball", p.location);
            if (p.location.z >= 44) { order.push(p); cmd(`ride "${p.name}" stop_riding`); const sec = (Date.now() - t0) / 1000; world.sendMessage(`§b${order.length}位 §f${p.name} §7${sec.toFixed(1)}秒`); record(55, p.name, sec, "min"); }
            if (t % 10 === 0) p.onScreenDisplay.setActionBar(`§c大玉ころがし §fゴールまで ${Math.max(0, Math.round(44 - p.location.z))}m`);
        }
        if (t % 40 === 0) for (const b of dim().getEntities({ type: "mmgplus:bigball" })) if (!b.getComponent("minecraft:rideable")?.getRiders().length) b.remove();
        if (players.every((p) => order.includes(p) || !p.isValid)) break;
        await wait(1);
    }
    cmd("ride @a stop_riding"); cmd("kill @e[type=mmgplus:bigball]");
    return order.slice(0, players.length === 1 ? 1 : Math.min(3, players.length - 1));
}

// ===== 56. ロデオ =====
// 自分の暴れ牛に乗る。「←」「→」が出たら、すぐその向きに顔を向ける。遅れるかちがう向きだと振り落とされる
async function gameRodeo() {
    const start = playing(), bulls = new Map();
    start.forEach((p, i) => { const b = mount(p, "mmgplus:bull", { x: (i % 6) * 4 - 10 + 0.5, y: 1, z: Math.floor(i / 6) * 5 - 2 + 0.5 }); b?.setRotation({ x: 0, y: 180 }); bulls.set(p.name, b); });
    title("§6§lロデオ", "§f矢印が出たら、すぐその向きを見る！");
    await wait(60);
    for (let r = 1; r <= 30 && !aborted(); r++) {
        const left = Math.random() < 0.5, buck = Math.min(3, 1 + Math.floor(r / 6));
        for (const b of bulls.values()) b?.setProperty("mmgplus:buck", buck);
        const base = new Map(alive().map((p) => [p.name, p.getRotation().y]));
        title(left ? "§l§e← 左！" : "§l§e右！ →", "", 15); soundAll("mob.cow.hurt", 0.6);
        await wait(Math.max(12, 30 - r - level() * 2));
        for (const p of alive()) {
            const d = ((p.getRotation().y - base.get(p.name)) % 360 + 540) % 360 - 180;
            const ok = riding(p, "mmgplus:bull") && (left ? d < -25 : d > 25);
            if (isBot(p) ? !chance(0.75, 0.88, 0.96) : !ok) { cmd(`ride "${p.name}" stop_riding`); out(p, "§c振り落とされた！"); }
        }
        for (const b of bulls.values()) b?.setProperty("mmgplus:buck", 0);
        if (endSurvive(start, r * 3, 60)) break;
        await wait(rand(10, 30));
    }
    cmd("ride @a stop_riding"); cmd("kill @e[type=mmgplus:bull]");
    return alive();
}

// ===== 58. アスレチック(5コース) =====
// 元のアスレチックの代わり。5つのコースから毎回1つ。足場を跳んでゴールへ。落ちたら最後のチェックポイントへ。1〜3位がポイント
const COURSE_BLOCKS = [["quartz_block", "lime_concrete"], ["prismarine_bricks", "sea_lantern"], ["mossy_stone_bricks", "glowstone"], ["red_nether_bricks", "shroomlight"], ["purpur_block", "end_rod"]];
function courseOf(n) {
    let seed = n * 9973 + 17; const rnd = () => ((seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648);
    const pts = []; let x = 0, y = 2, z = -42;
    pts.push({ x, y, z, w: 2, cp: true });
    let i = 0;
    while (z < 40) {
        i++;
        const hard = n >= 3 ? 0.5 : 0.25;
        z += 2 + Math.floor(rnd() * 2) + (rnd() < hard ? 1 : 0);
        x = Math.max(-6, Math.min(6, x + Math.floor(rnd() * 5) - 2));
        y = Math.max(1, Math.min(6, y + Math.floor(rnd() * 3) - 1));
        pts.push({ x, y, z, w: rnd() < (n >= 4 ? 0.7 : 0.4) ? 0 : 1, cp: i % 8 === 0 });
    }
    pts.push({ x: 0, y, z: 44, w: 2, goal: true });
    return pts;
}
let course = 1;
function buildCourse() {
    clearArena();
    course = rand(1, 5);
    const [blk, cpb] = COURSE_BLOCKS[course - 1];
    for (const q of courseOf(course)) cmd(`fill ${q.x - q.w} ${q.y} ${q.z - (q.w ? 1 : 0)} ${q.x + q.w} ${q.y} ${q.z + (q.w ? 1 : 0)} ${q.goal ? "emerald_block" : q.cp ? "gold_block" : blk}`);
    void cpb;
}
async function gameCourse() {
    const pts = courseOf(course), players = playing(), order = [], cp = new Map(), t0 = Date.now();
    const start = pts[0];
    players.forEach((p) => p.teleport({ x: start.x + 0.5, y: start.y + 1, z: start.z + 0.5 }, { rotation: { x: 0, y: 0 } }));
    title(`§a§lアスレチック コース${course}`, "§f金のブロックがチェックポイント、エメラルドがゴール", 50);
    await wait(50);
    for (let t = 0; t < 4800 && !aborted(); t += 2) {
        for (const p of playing()) {
            if (order.includes(p)) continue;
            const l = p.location;
            if (isBot(p) && t % [30, 22, 15][botStr()] === 0) { const i = pts.findIndex((q) => q.z > l.z + 0.5); const q = pts[i]; if (q) { if (chance(0.7, 0.82, 0.92)) p.teleport({ x: q.x + 0.5, y: q.y + 1, z: q.z + 0.5 }); else p.teleport({ x: l.x, y: 1, z: l.z }); } }
            for (const q of pts) if (q.cp && Math.abs(l.x - (q.x + 0.5)) < 2.6 && Math.abs(l.z - (q.z + 0.5)) < 2.6 && Math.abs(l.y - (q.y + 1)) < 0.6 && (cp.get(p.name)?.z ?? -99) < q.z) { cp.set(p.name, q); p.sendMessage("§eチェックポイント！"); cmd(`playsound random.orb "${p.name}"`); }
            if (l.y < 1.5) { const c = cp.get(p.name) ?? start; p.teleport({ x: c.x + 0.5, y: c.y + 1, z: c.z + 0.5 }, { rotation: { x: 0, y: 0 } }); }
            if (l.z >= 43 && l.y >= pts[pts.length - 1].y + 0.5) { order.push(p); const sec = (Date.now() - t0) / 1000; world.sendMessage(`§a${order.length}位 §f${p.name} §7${sec.toFixed(1)}秒`); record(58, p.name, sec, "min"); }
            if (t % 10 === 0) p.onScreenDisplay.setActionBar(`§aアスレチック コース${course} §fゴールまで ${Math.max(0, Math.round(44 - l.z))}m`);
        }
        if (players.every((p) => order.includes(p) || !p.isValid)) break;
        await wait(2);
    }
    return order.slice(0, players.length === 1 ? 1 : Math.min(3, players.length - 1));
}

// ===== 元のゲームの調整 =====
// 村人数え(23): レベル4以降、村人に似たモブ(行商人・村人ゾンビ)を混ぜる。数えるのは村人だけ
let decoyDone = false;
system.runInterval(() => {
    if (score("game", "selectgame") !== 23 || score("game", "playing") !== 1) { decoyDone = false; return; }
    if (decoyDone || level() < 4) return;
    const vs = dim().getEntities({ type: "minecraft:villager" });
    if (vs.length < 3) return;
    decoyDone = true;
    const n = Math.ceil(vs.length * (level() === 4 ? 0.3 : 0.5));
    for (let i = 0; i < n; i++) {
        const at = vs[rand(0, vs.length - 1)].location;
        try {
            const e = dim().spawnEntity(Math.random() < 0.5 ? "minecraft:wandering_trader" : "minecraft:zombie_villager_v2", { x: at.x + rand(-1, 1), y: at.y, z: at.z + rand(-1, 1) });
            e.addEffect("fire_resistance", 20000, { showParticles: false });
        } catch {}
    }
}, 10);

// TNT TAG(6): 生き残りが参加人数の3分の1まで減ったら終わり(元は最後の1人まで)
let tagTotal = 0;
system.runInterval(() => {
    if (score("game", "selectgame") !== 6 || score("game", "playing") !== 1) { tagTotal = 0; return; }
    const ps = playing();
    tagTotal = Math.max(tagTotal, ps.length);
    const left = ps.filter((p) => !p.hasTag("died")).length;
    if (tagTotal >= 3 && left >= 1 && left <= Math.floor(tagTotal / 3) && score("game", "stopgame") === 0) {
        setScore("game", "stopgame", 1);
        world.sendMessage(`§c残り ${left}人になったので終了！`);
        cmd("setblock 29 -14 17 redstone_block"); // 元の「残り1人」と同じ終わり方
    }
}, 20);

// 逆らえ！(9): 命令を 8 → 18 種類に。9〜18 の判定はここでする(1〜8 は元のコマンドのまま)
//   奇数 = 「〜しろ」(すると脱落)、偶数 = 「〜するな」(すると成功)。命令から1秒は判定しない
const DEFY = {
    9: (p) => p.isSneaking, 10: (p) => p.isSneaking,
    11: (p) => !p.isOnGround && p.getVelocity().y > 0.2, 12: (p) => !p.isOnGround && p.getVelocity().y > 0.2,
    13: (p) => { const v = p.getVelocity(); return Math.hypot(v.x, v.z) > 0.08; }, 14: (p) => { const v = p.getVelocity(); return Math.hypot(v.x, v.z) > 0.08; },
    15: (p) => p.getRotation().x < -50, 16: (p) => p.getRotation().x < -50,
    17: (p) => p.isSprinting, 18: (p) => p.isSprinting,
    19: (p) => p.getRotation().x > 50, 20: (p) => p.getRotation().x > 50,
    21: (p) => Math.hypot(p.location.x, p.location.z) < 2.5, 22: (p) => Math.hypot(p.location.x, p.location.z) < 2.5,
    23: (p) => Math.hypot(p.location.x, p.location.z) > 6, 24: (p) => Math.hypot(p.location.x, p.location.z) > 6,
    25: (p) => punched.has(p.name), 26: (p) => punched.has(p.name),
    27: (p) => turnedBack(p), 28: (p) => turnedBack(p),
};
let defyFrom = 0, defyLast = 0;
const punched = new Set(), startYaw = new Map();
const turnedBack = (p) => { const a = Math.abs(((p.getRotation().y - (startYaw.get(p.name) ?? 0)) % 360 + 540) % 360 - 180); return a > 135; };
world.afterEvents.entityHitEntity.subscribe((ev) => { if (ev.damagingEntity.typeId === "minecraft:player" && ev.hitEntity.typeId === "minecraft:player") punched.add(ev.damagingEntity.name); });
system.runInterval(() => {
    if (score("game", "selectgame") !== 9) return;
    const m = score("game", "game9_m") ?? 0, x = score("game", "game9_x");
    if (x !== 1) { defyLast = 0; return; }
    if (m !== defyLast) { defyLast = m; defyFrom = system.currentTick + 20; punched.clear(); startYaw.clear(); for (const p of playing()) startYaw.set(p.name, p.getRotation().y); }
    if (!DEFY[m] || system.currentTick < defyFrom) return;
    for (const p of playing()) {
        if (p.hasTag("died") || p.hasTag("game9_die") || p.hasTag("game9_goal")) continue;
        let did = false; try { did = DEFY[m](p); } catch {}
        if (did) p.addTag(m % 2 === 1 ? "game9_die" : "game9_goal");
    }
}, 2);

// ===== ランキングの記録 =====
// 保存: "stats" = { 名前: { pt, win, gw: {番号: 回数}, last, zero, death } } / "records" = { 番号: { name, v } }
const stats = load("stats", {});
const records = load("records", {});
let dirty = false;
const st = (name) => (stats[name] ??= { pt: 0, win: 0, gw: {}, last: 0, zero: 0, death: 0 });
function record(id, name, v, kind) {
    const r = records[id];
    if (!r || (kind === "min" ? v < r.v : v > r.v)) {
        records[id] = { name, v, kind };
        save("records", records);
        world.sendMessage(`§6★ ${GAMES[id - 1]} の新記録！ §f${name} ${fmtRecord(id, v)}`);
    }
}
const RECORD_UNIT = { 25: "秒", 26: "個", 28: "点", 29: "秒", 30: "秒", 31: "秒ずれ", 32: "羽", 34: "秒", 35: "秒", 36: "秒", 38: "秒", 39: "点", 43: "秒", 44: "点", 45: "枚", 54: "秒", 55: "秒", 58: "秒" };
const fmtRecord = (id, v) => (Number.isInteger(v) ? `${v}` : v.toFixed(2)) + (RECORD_UNIT[id] ?? "");

// 最終2ラウンドは得点2倍。増えた分と同じだけ足す(BOT も)。allPts は BOT も入れた今の得点
let seenPts = {}, allPts = {}, lastRound = 0, prevRank = {};
const isBonusRound = () => { const r = score("game", "round") ?? 0, total = score("setting", "round") ?? 0; return total >= 3 && r >= total - 1; };
system.runInterval(() => {
    if (score("game", "playing") !== 1) { seenPts = {}; lastRound = 0; return; }
    const o = obj("point"); if (!o) return;
    const r = score("game", "round") ?? 0;
    if (r !== lastRound) { lastRound = r; if (isBonusRound()) { title("§6§lボーナスラウンド！", "§fこのラウンドは得点2倍", 50); soundAll("random.levelup", 0.8); } }
    for (const part of o.getParticipants()) {
        let v; try { v = o.getScore(part); } catch { continue; }
        const name = part.displayName, seen = seenPts[name] ?? 0;
        if (v > seen && isBonusRound()) { o.addScore(part, v - seen); world.sendMessage(`§6${name} ボーナス +${v - seen}`); v += v - seen; }
        seenPts[name] = v; allPts[name] = v;
    }
}, 5);
// ラウンド結果: 次のゲームの準備に入った時に、今の順位と上がり下がりを出す
let wasNext = 0;
system.runInterval(() => {
    const nx = score("game", "game_next_ready") ?? 0;
    if (nx === 1 && wasNext !== 1 && score("game", "playing") === 1) showRoundResult();
    wasNext = nx;
}, 5);
// 専用の画面(RP の ui/server_form.json、tools/rank_ui.py で作る)。タイトルに RANK_MARK を入れたフォームがこの見た目になる
// ボタン2つで1行: 左「順位 名前」(アイコン = 行の背景: 順位の色・上がった/下がった・自分)、右「点数 +このラウンドの点」
const RANK_MARK = "§r§m§r§n§r";
let prevPtsRound = {};
function showRoundResult() {
    const rows = Object.entries(allPts).filter(([n]) => world.getPlayers({ name: n }).length).sort((a, b) => b[1] - a[1]).slice(0, 12);
    if (!rows.length) return;
    const r = score("game", "round") ?? 0, total = score("setting", "round") ?? 0;
    const rankOf = (i) => rows.findIndex(([, v]) => v === rows[i][1]); // 同点は同じ順位
    const body = total >= 3 && r + 1 >= total - 1 && r < total ? "§6NEXT ROUND: BONUS x2" : `§7ROUND ${r} / ${total || "?"}`;
    for (const p of world.getPlayers()) {
        if (isBot(p)) continue;
        const f = new ActionFormData().title(`${RANK_MARK}§lROUND ${r} RESULTS`).body(body);
        rows.forEach(([n, v], i) => {
            const rank = rankOf(i), before = prevRank[n];
            const tier = ["gold", "silver", "bronze"][rank] ?? "normal";
            const kind = before === undefined || before === rank ? "same" : before > rank ? "up" : "down";
            const gain = v - (prevPtsRound[n] ?? 0);
            f.button(`§l${rank + 1}§r  ${n === p.name ? "§e" : "§f"}${n}${before !== undefined && before !== rank ? ` §7(${before + 1}→${rank + 1})` : ""}`, `textures/ui/mmgplus_rank/${tier}_${kind}${n === p.name ? "_me" : ""}`);
            f.button(`§f${v}pt${gain > 0 ? ` §a+${gain}` : ""}`);
        });
        f.show(p).catch(() => {});
    }
    soundAll("random.levelup", 1.6);
    system.runTimeout(() => world.getPlayers().forEach((p) => { try { uiManager.closeAllForms(p); } catch {} }), 140);
    prevRank = Object.fromEntries(rows.map(([n], i) => [n, rankOf(i)]));
    prevPtsRound = Object.fromEntries(rows);
    world.sendMessage(`§b§lROUND ${r}§r §f1st: ${rows[0][0]} (${rows[0][1]}pt)`);
}
// 優勝の演出(試合全体の最後): ロビーに戻ったあと、1位にスポットライトと花火
async function celebrate(names) {
    await wait(60);
    const winners = names.map((n) => world.getPlayers({ name: n })[0]).filter(Boolean);
    if (!winners.length) return;
    for (const p of world.getPlayers()) p.onScreenDisplay.setTitle(`§6§l優勝 ${names.join(" & ")}`, { subtitle: "§fおめでとう！", fadeInDuration: 10, stayDuration: 100, fadeOutDuration: 20 });
    cmd("execute as @a at @s run playsound random.totem @s ~ ~ ~ 1 1");
    for (let i = 0; i < 16; i++) {
        for (const w of winners) {
            if (!w.isValid) continue;
            const l = w.location;
            cmd(`particle minecraft:totem_particle ${l.x} ${l.y + 1} ${l.z}`);
            for (let k = 0; k < 8; k++) { const a = (k / 8) * Math.PI * 2 + i * 0.3; cmd(`particle minecraft:endrod ${l.x + Math.cos(a) * 1.5} ${l.y + 0.2 + (i % 4) * 0.6} ${l.z + Math.sin(a) * 1.5}`); }
            if (i % 4 === 0) { try { dim().spawnEntity("minecraft:fireworks_rocket", { x: l.x + rand(-3, 3), y: l.y + 1, z: l.z + rand(-3, 3) }); } catch {} }
        }
        await wait(10);
    }
}

// point を見張って増えた分を記録する(試合の最後に point は消されるので、その直前の値で順位を決める)
let lastPts = {};
let matchPlayers = new Set();
let wasPlaying = false;
system.runInterval(() => {
    const isPlaying = score("game", "playing") === 1;
    const sg = score("game", "selectgame") ?? 0;
    if (isPlaying) {
        for (const p of playing()) (isBot(p) ? botNames : matchPlayers).add(p.name);
        const o = obj("point");
        if (o) {
            for (const part of o.getParticipants()) {
                let v; try { v = o.getScore(part); } catch { continue; }
                const name = part.displayName, prev = lastPts[name] ?? 0;
                if (botNames.has(name)) continue;
                if (v > prev) {
                    const s = st(name);
                    s.pt += v - prev;
                    if (sg >= 1) s.gw[sg] = (s.gw[sg] ?? 0) + 1;
                    dirty = true;
                }
                lastPts[name] = v;
            }
        }
    } else if (wasPlaying) endMatch();
    wasPlaying = isPlaying;
    if (dirty) { save("stats", stats); dirty = false; }
}, 10);

function endMatch() {
    if (load("seq", null)) { world.setDynamicProperty("seq", undefined); world.sendMessage("§e全ゲーム順番モードが終わりました"); }
    const rows = Object.entries(allPts), top = Math.max(0, ...rows.map(([, v]) => v));
    if (top > 0) celebrate(rows.filter(([, v]) => v === top).map(([n]) => n));
    allPts = {}; prevRank = {}; prevPtsRound = {};
    const names = [...matchPlayers];
    if (names.length) {
        const pts = names.map((n) => lastPts[n] ?? 0);
        const max = Math.max(...pts), min = Math.min(...pts);
        names.forEach((n, i) => {
            const s = st(n);
            if (max > 0 && pts[i] === max) s.win++;
            if (names.length >= 2 && min < max && pts[i] === min) s.last++;
            if (pts[i] === 0) s.zero++;
        });
        dirty = true;
    }
    lastPts = {}; matchPlayers = new Set();
}

world.afterEvents.entityDie.subscribe((ev) => {
    const p = ev.deadEntity;
    if (p.typeId === "minecraft:player" && p.hasTag("playing") && !isBot(p)) { st(p.name).death++; dirty = true; }
});

// ===== ランキング掲示板 =====
function top(list, n = 10) {
    return list.filter(([, v]) => v > 0).sort((a, b) => b[1] - a[1]).slice(0, n)
        .map(([name, v], i) => `${["§e", "§7", "§6"][i] ?? "§f"}${i + 1}. §f${name} §b${v}`);
}
const each = (f) => Object.entries(stats).map(([n, s]) => [n, f(s)]);
function pages() {
    const list = [];
    const page = (head, lines) => list.push([`§l${head}§r`, ...(lines.length ? lines : ["§7まだ記録がありません"])].join("\n"));
    page("§6累計ポイント", top(each((s) => s.pt)));
    page("§e優勝回数", top(each((s) => s.win)));
    for (let g = 0; g < ACTIVE.length; g += 9) {
        const lines = [];
        for (const id of ACTIVE.slice(g, g + 9)) {
            const best = each((s) => s.gw[id] ?? 0).filter(([, v]) => v > 0).sort((a, b) => b[1] - a[1])[0];
            lines.push(`§f${GAMES[id - 1]}: ${best ? `§a${best[0]} §b${best[1]}勝` : "§7-"}`);
        }
        list.push([`§l§aゲーム別 勝利数王 (${g / 9 + 1}/${Math.ceil(ACTIVE.length / 9)})§r`, ...lines].join("\n"));
    }
    const recs = Object.entries(records).filter(([id]) => ACTIVE.includes(+id)).map(([id, r]) => `§f${GAMES[id - 1]}: §a${r.name} §b${fmtRecord(+id, r.v)}`);
    page("§b記録", recs);
    const neg = (h, f) => { const t = top(each(f), 3); return [`§c${h}`, ...(t.length ? t : ["§7-"])]; };
    page("§cマイナス部門", [...neg("最下位回数", (s) => s.last), ...neg("0ポイント回数", (s) => s.zero), ...neg("死亡回数", (s) => s.death)]);
    return list;
}

let pageIdx = 0;
system.runInterval(() => {
    const loc = load("board", null);
    if (!loc) return;
    const d = dim();
    let e;
    try { e = d.getEntities({ type: "mmgplus:board", location: loc, maxDistance: 2 })[0]; } catch { return; } // 読み込まれていない
    if (!e) { try { e = d.spawnEntity("mmgplus:board", loc); } catch { return; } }
    const ps = pages();
    e.nameTag = ps[pageIdx++ % ps.length];
}, 160);

async function boardUI(player) {
    const res = await new ActionFormData().title("ランキング掲示板")
        .button("ここに掲示板を置く").button("掲示板を消す").button("§cランキングをリセット").show(player);
    if (res.canceled) return;
    if (res.selection === 0 || res.selection === 1) {
        cmd("kill @e[type=mmgplus:board]");
        if (res.selection === 0) {
            const l = player.location;
            save("board", { x: l.x, y: l.y + 1.5, z: l.z });
            player.sendMessage("§a掲示板を置きました(8秒ごとにページが切り替わります)");
        } else { world.setDynamicProperty("board", undefined); player.sendMessage("§a掲示板を消しました"); }
        return;
    }
    const ok = await new MessageFormData().title("ランキングをリセット").body("全員の記録を消します。元に戻せません。").button1("やめる").button2("§cリセット").show(player);
    if (ok.selection !== 1) return;
    for (const k of Object.keys(stats)) delete stats[k];
    for (const k of Object.keys(records)) delete records[k];
    save("stats", stats); save("records", records);
    player.sendMessage("§aランキングをリセットしました");
}
