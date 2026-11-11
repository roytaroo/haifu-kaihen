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
]; // 番号 = 添字 + 1
const FIRST_PLUS = 25;
// だいきの指示で消したゲーム(抽選・ON/OFF・ランキングに出さない)
const REMOVED = [3, 8, 10, 11, 12, 16, 17];
const ACTIVE = GAMES.map((_, i) => i + 1).filter((id) => !REMOVED.includes(id));
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
    const off = load("off", []);
    let ids = ACTIVE.filter((id) => !off.includes(id));
    if (ids.length === 0) ids = ACTIVE;
    // 同じゲームが2回続かないように(選べるのが1つの時は別)
    const last = score("game", "selectgame");
    if (ids.length > 1) ids = ids.filter((id) => id !== last);
    setScore("game", "selectgame", ids[rand(0, ids.length - 1)]);
    cmd("function select_game_body");
}

async function gamesUI(player) {
    const off = load("off", []);
    const form = new ModalFormData().title("ミニゲームのON/OFF");
    ACTIVE.forEach((id) => form.toggle(`${id}. ${GAMES[id - 1]}${id >= FIRST_PLUS ? " §e(追加)" : ""}`, { defaultValue: !off.includes(id) }));
    const res = await form.show(player);
    if (res.canceled) return;
    const next = [];
    res.formValues.forEach((on, i) => { if (!on) next.push(ACTIVE[i]); });
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
    cmd("tag @a remove mmgplus_out");
    if (id === 28) cmd("tp @a[tag=playing] 0 7 0");
    else if (id === 29) cmd("tp @a[tag=playing] 0 1 5");
    else if (id === 37) cmd("tp @a[tag=playing] 0 1 6");
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
const CUSTOM = ["mmgplus:chair", "mmgplus:treasure_gold", "mmgplus:treasure_diamond", "mmgplus:treasure_emerald", "mmgplus:fireball"];
function clearArena() {
    cmd("fill -24 1 -49 25 8 0 air");
    cmd("fill -24 1 1 25 8 50 air");
    cmd("fill -24 0 -49 25 0 50 black_concrete");
    for (const t of CUSTOM) cmd(`kill @e[type=${t}]`);
    cmd("kill @e[type=boat,tag=mmgplus_boat]");
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
                const delay = rand(...[[100, 260], [70, 180], [40, 110]][botStr()]);
                const ok = chance(0.5, 0.7, 0.88);
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
                    if (t % [16, 12, 8][botStr()] !== 0) continue;
                    const miss = [0.08, 0.04, 0.015][botStr()] + seq.length * [0.012, 0.006, 0.003][botStr()];
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
    for (const p of players.filter(isBot)) res.set(p.name, Math.max(0.5, target + (Math.random() * 2 - 1) * [1.6, 0.9, 0.35][botStr()]));
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
            if (isBot(p)) { answered.set(p.name, chance(0.5, 0.7, 0.85) ? ans : rand(0, n - 1)); continue; }
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
        const botT = new Map(players.filter(isBot).map((p) => [p.name, rand(...[[7, 14], [5, 10], [4, 7]][botStr()])]));
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
                if (isBot(g.p)) { if (t === 100) for (const k of lit) if (chance(0.6, 0.8, 0.92)) m.add(k); continue; }
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
const RECORD_UNIT = { 25: "秒", 26: "個", 28: "点", 29: "秒", 30: "秒", 31: "秒ずれ", 32: "羽", 34: "秒", 35: "秒", 36: "秒", 38: "秒", 39: "点" };
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
function showRoundResult() {
    const rows = Object.entries(allPts).filter(([n]) => world.getPlayers({ name: n }).length).sort((a, b) => b[1] - a[1]);
    if (!rows.length) return;
    const lines = rows.map(([n, v], i) => {
        const before = prevRank[n], mark = before === undefined || before === i ? "§7－" : before > i ? "§a↑" : "§c↓";
        return `${mark} §f${i + 1}位 ${n} §e${v}pt`;
    });
    prevRank = Object.fromEntries(rows.map(([n], i) => [n, i]));
    world.sendMessage(`§l§b＝ ラウンド ${score("game", "round") ?? 0} の結果 ＝§r\n` + lines.join("\n"));
    for (const p of world.getPlayers()) {
        const i = rows.findIndex(([n]) => n === p.name);
        p.onScreenDisplay.setTitle("§lラウンド結果", { subtitle: `§f1位 ${rows[0][0]} ${rows[0][1]}pt${i >= 0 ? `  §7あなた ${i + 1}位` : ""}`, fadeInDuration: 5, stayDuration: 50, fadeOutDuration: 10 });
    }
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
    const rows = Object.entries(allPts), top = Math.max(0, ...rows.map(([, v]) => v));
    if (top > 0) celebrate(rows.filter(([, v]) => v === top).map(([n]) => n));
    allPts = {}; prevRank = {};
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
