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
    cmd("tag @a remove mmgplus_out");
    if (id === 28) cmd("tp @a[tag=playing] 0 7 0");
    else if (id === 29) cmd("tp @a[tag=playing] 0 1 5");
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
        spots.forEach((s) => { try { dim().spawnEntity("mmgplus:chair", s).setRotation({ x: 0, y: rand(0, 3) * 90 }); } catch {} });
        title("§c§l座れ！", `§fイス ${spots.length}脚  §7(イスを右クリック/タップ)`, 20);
        soundAll("random.anvil_land", 1.5);
        for (let t = 0; t < 120 && !aborted(); t += 2) {
            const n = alive().filter(seated).length;
            actionbar(`§c座れ！ §f${n}/${spots.length}  §7残り ${Math.ceil((120 - t) / 20)}秒`);
            if (n >= spots.length) break;
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
    cmd("fill -15 0 -15 15 6 15 prismarine_bricks");
    cmd("fill -14 0 -14 14 0 14 dark_prismarine");
    cmd("fill -14 1 -14 14 5 14 water");
    cmd("fill -14 6 -14 14 6 14 air");
    for (const [x, z] of [[-15, -15], [15, -15], [-15, 15], [15, 15], [0, -15], [0, 15], [-15, 0], [15, 0]]) cmd(`setblock ${x} 6 ${z} sea_lantern`);
}
async function gamePool() {
    const TIME = 1200;
    const got = new Map();
    const want = () => Math.max(10, playing().length * 3);
    const pick = () => { let r = Math.random() * 100; return TREASURE.find((t) => (r -= t.w) < 0) ?? TREASURE[0]; };
    const spawn = () => {
        const t = pick();
        try { dim().spawnEntity(t.type, { x: rand(-13, 13) + 0.5, y: 1.2 + Math.random() * 3, z: rand(-13, 13) + 0.5 }); } catch {}
    };
    cmd("effect @a[tag=playing] water_breathing 90 0 true");
    cmd("effect @a[tag=playing] night_vision 90 0 true");
    title("§l宝探し！", "§6金1点 §bダイヤ3点 §aエメラルド5点");
    for (let t = 0; t < TIME && !aborted(); t += 2) {
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
    let theta = 0, dir = 1, omega = (Math.PI * 2) / 100, swept = 0, revs = 0;
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

// ===== 元のゲームの調整 =====
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
};
let defyFrom = 0, defyLast = 0;
system.runInterval(() => {
    if (score("game", "selectgame") !== 9) return;
    const m = score("game", "game9_m") ?? 0, x = score("game", "game9_x");
    if (x !== 1) { defyLast = 0; return; }
    if (m !== defyLast) { defyLast = m; defyFrom = system.currentTick + 20; }
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
const RECORD_UNIT = { 25: "秒", 26: "個", 28: "点", 29: "秒", 30: "秒", 31: "秒ずれ", 32: "羽" };
const fmtRecord = (id, v) => (Number.isInteger(v) ? `${v}` : v.toFixed(2)) + (RECORD_UNIT[id] ?? "");

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
