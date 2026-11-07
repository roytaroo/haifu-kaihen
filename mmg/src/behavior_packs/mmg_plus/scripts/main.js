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
    "計算早押し", "色の記憶", "椅子取りゲーム",
]; // 番号 = 添字 + 1
const FIRST_PLUS = 25;
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
    let ids = GAMES.map((_, i) => i + 1).filter((id) => !off.includes(id));
    if (ids.length === 0) ids = GAMES.map((_, i) => i + 1);
    // 同じゲームが2回続かないように(選べるのが1つの時は別)
    const last = score("game", "selectgame");
    if (ids.length > 1) ids = ids.filter((id) => id !== last);
    setScore("game", "selectgame", ids[rand(0, ids.length - 1)]);
    cmd("function select_game_body");
}

async function gamesUI(player) {
    const off = load("off", []);
    const form = new ModalFormData().title("ミニゲームのON/OFF");
    GAMES.forEach((name, i) => form.toggle(`${i + 1}. ${name}${i + 1 >= FIRST_PLUS ? " §e(追加)" : ""}`, { defaultValue: !off.includes(i + 1) }));
    const res = await form.show(player);
    if (res.canceled) return;
    const next = [];
    res.formValues.forEach((on, i) => { if (!on) next.push(i + 1); });
    if (next.length === GAMES.length) { player.sendMessage("§c全部OFFにはできません。1つ以上ONにしてください"); return; }
    save("off", next);
    player.sendMessage(`§aミニゲームの設定を保存しました(ON ${GAMES.length - next.length} / OFF ${next.length})`);
}

// ===== 追加ゲームの共通処理 =====
// 会場は元のゲームと同じ場所(0,0 のまわり、床は y=0 の黒コンクリート)
const run = { id: 0, active: false };
const aborted = () => !run.active || score("game", "playing") !== 1 || score("game", "selectgame") !== run.id;

async function prepGame() {
    const id = score("game", "selectgame");
    if (id === 26) buildSimon();
    if (id === 27) buildChairs();
    cmd("tag @a remove mmgplus_out");
    cmd("tp @a[tag=playing] 0 1 0");
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
    } catch (e) { console.warn(`[mmg_plus] game${id}: ${e}`); }
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
function wall(r, h, block) {
    cmd(`fill ${-r} 1 ${-r} ${r} ${h} ${-r} ${block}`); cmd(`fill ${-r} 1 ${r} ${r} ${h} ${r} ${block}`);
    cmd(`fill ${-r} 1 ${-r} ${-r} ${h} ${r} ${block}`); cmd(`fill ${r} 1 ${-r} ${r} ${h} ${r} ${block}`);
}
function clearArena() {
    cmd("fill -10 1 -10 10 6 10 air");
    cmd("fill -10 0 -10 10 0 10 black_concrete");
    cmd("kill @e[type=minecart,tag=mmgplus_chair]");
    cmd("kill @e[type=item,x=0,y=1,z=0,r=15]");
    cmd("tag @a remove mmgplus_out");
}
const actionbar = (text, players = playing()) => players.forEach((p) => p.onScreenDisplay.setActionBar(text));
const title = (text, sub = "") => playing().forEach((p) => p.onScreenDisplay.setTitle(text, { subtitle: sub, fadeInDuration: 0, stayDuration: 30, fadeOutDuration: 5 }));

// ===== 25. 計算早押し =====
function makeQuestion(lv) {
    let a, b, op;
    if (lv === 1) { a = rand(1, 9); b = rand(1, 9); op = "+"; }
    else if (lv === 2) { op = Math.random() < 0.5 ? "+" : "-"; a = rand(10, 99); b = rand(10, 99); if (op === "-" && b > a) [a, b] = [b, a]; }
    else if (lv === 3) { op = "×"; a = rand(2, 9); b = rand(2, 9); }
    else if (lv === 4) { op = "×"; a = rand(11, 29); b = rand(2, 9); }
    else { op = ["+", "-", "×"][rand(0, 2)]; a = op === "×" ? rand(12, 49) : rand(100, 999); b = op === "×" ? rand(3, 19) : rand(100, 999); if (op === "-" && b > a) [a, b] = [b, a]; }
    const ans = op === "+" ? a + b : op === "-" ? a - b : a * b;
    const choices = new Set([ans]);
    const spread = Math.max(3, Math.round(Math.abs(ans) * 0.15));
    while (choices.size < 4) { const c = ans + rand(-spread, spread); if (c !== ans && c >= 0) choices.add(c); }
    return { text: `${a} ${op} ${b}`, ans, choices: [...choices].sort(() => Math.random() - 0.5) };
}

async function gameQuiz() {
    const QUESTIONS = 5, LIMIT = 200; // 1問10秒
    const correct = new Map();
    for (let q = 1; q <= QUESTIONS; q++) {
        if (aborted()) return [];
        const Q = makeQuestion(level());
        let winner;
        const players = playing();
        title(`§lQ${q}`, `§f${Q.text} = ?`);
        cmd("playsound random.orb @a");
        await wait(20);
        const asked = Date.now();
        for (const p of players) {
            const form = new ActionFormData().title(`計算早押し Q${q}/${QUESTIONS}`).body(`§l${Q.text} = ?`);
            Q.choices.forEach((c) => form.button(`§l${c}`));
            form.show(p).then((res) => {
                if (res.canceled || winner || aborted()) return;
                if (Q.choices[res.selection] === Q.ans) {
                    winner = p;
                    const sec = (Date.now() - asked) / 1000;
                    correct.set(p.name, (correct.get(p.name) ?? 0) + 1);
                    world.sendMessage(`§a${p.name} が正解！ §7(${sec.toFixed(2)}秒) §f答え: ${Q.ans}`);
                    record(25, p.name, sec, "min");
                    cmd(`playsound random.levelup "${p.name}"`);
                    for (const o of playing()) if (o.id !== p.id) uiManager.closeAllForms(o);
                } else {
                    p.sendMessage("§cざんねん！この問題はもう答えられません");
                    cmd(`playsound note.bass "${p.name}"`);
                }
            }).catch(() => {});
        }
        for (let t = 0; t < LIMIT && !winner && !aborted(); t += 5) {
            actionbar(`§b計算早押し §fQ${q}/${QUESTIONS}  §7残り ${Math.ceil((LIMIT - t) / 20)}秒`);
            await wait(5);
        }
        players.forEach((p) => { try { uiManager.closeAllForms(p); } catch {} });
        if (!winner) world.sendMessage(`§7時間切れ！ 答え: ${Q.ans}`);
        await wait(40);
    }
    const best = Math.max(0, ...correct.values());
    if (best === 0) return [];
    return playing().filter((p) => correct.get(p.name) === best);
}

// ===== 26. 色の記憶 =====
// 中央3x3から東西南北に 5x5 の色の床。光る = シーランタン
const PADS = [
    { name: "§c赤", wool: "red_wool", x: [-2, 2], z: [-6, -2], pitch: 0.7 },
    { name: "§9青", wool: "blue_wool", x: [2, 6], z: [-2, 2], pitch: 0.9 },
    { name: "§a緑", wool: "lime_wool", x: [-2, 2], z: [2, 6], pitch: 1.1 },
    { name: "§e黄", wool: "yellow_wool", x: [-6, -2], z: [-2, 2], pitch: 1.3 },
];
const padFill = (pad, block) => cmd(`fill ${pad.x[0]} 0 ${pad.z[0]} ${pad.x[1]} 0 ${pad.z[1]} ${block}`);
function buildSimon() {
    clearArena();
    PADS.forEach((pad) => padFill(pad, pad.wool));
    cmd("fill -1 0 -1 1 0 1 smooth_stone");
    wall(7, 3, "glass");
}
function padAt(p) {
    const x = Math.floor(p.location.x), z = Math.floor(p.location.z);
    // 色の床が重なる角は中立にする
    const hits = PADS.filter((pad) => x >= pad.x[0] && x <= pad.x[1] && z >= pad.z[0] && z <= pad.z[1]);
    return hits.length === 1 && p.location.y < 2 ? hits[0] : null;
}

async function gameSimon() {
    const start = playing();
    const seq = [rand(0, 3)];
    const flash = [14, 12, 10, 8, 7][level() - 1];
    const cleared = new Map(); // 名前 → クリアできた一番長い個数
    for (let round = 1; round <= 20; round++) {
        if (aborted()) return [];
        seq.push(rand(0, 3));
        const players = alive();
        if (players.length === 0) break;
        cmd("tp @a[tag=playing,tag=!mmgplus_out] 0 1 0");
        title(`§l${seq.length}個`, "§fおぼえよう！");
        await wait(30);
        for (const i of seq) {
            if (aborted()) return [];
            padFill(PADS[i], "sea_lantern");
            cmd(`playsound note.pling @a 0 1 0 1 ${PADS[i].pitch}`);
            actionbar(`§d色の記憶 §f${PADS[i].name}`);
            await wait(flash);
            padFill(PADS[i], PADS[i].wool);
            await wait(4);
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
                const pad = padAt(p);
                if (pad && pad !== s.prev) {
                    if (PADS.indexOf(pad) === seq[s.idx]) {
                        s.idx++;
                        cmd(`playsound note.pling "${p.name}" ~ ~ ~ 1 ${pad.pitch}`);
                        if (s.idx >= seq.length) { p.sendMessage("§aクリア！"); left--; }
                    } else { out(p, `§cまちがえた！ §7(${seq.length}個のラウンド)`); left--; }
                }
                s.prev = pad;
            }
            actionbar(`§d色の記憶 §f${seq.length}個  §7残り ${Math.ceil((limit - t) / 20)}秒`);
            if (left === 0) break;
            await wait(2);
        }
        for (const p of alive()) if ((state.get(p.id)?.idx ?? 0) < seq.length) out(p, "§c時間切れ！");
        for (const p of alive()) cleared.set(p.name, seq.length);
        const now = alive().length;
        if (now === 0 || (start.length > 1 && now === 1)) break;
        await wait(30);
    }
    // 一番長くクリアした人が勝ち(ひとりの時は 5個以上で勝ち)
    const best = Math.max(0, ...cleared.values());
    if (best === 0 || (start.length === 1 && best < 5)) return [];
    const names = [...cleared].filter(([, v]) => v === best).map(([n]) => n);
    names.forEach((n) => record(26, n, best, "max"));
    return playing().filter((p) => names.includes(p.name));
}

// ===== 27. 椅子取りゲーム =====
function buildChairs() {
    clearArena();
    cmd("fill -7 0 -7 7 0 7 oak_planks");
    wall(8, 3, "oak_fence");
}
const chairs = () => dim().getEntities({ type: "minecraft:minecart", tags: ["mmgplus_chair"] });
const ridingCart = (p) => p.getComponent("minecraft:riding")?.entityRidingOn?.hasTag("mmgplus_chair");

async function gameChairs() {
    const start = playing();
    if (start.length < 2) world.sendMessage("§7ひとりなので、トロッコに乗れたら勝ち！");
    while (!aborted()) {
        const players = alive();
        if (players.length <= 1 && start.length > 1) return players;
        // 音楽(ランダムな長さ)
        const len = rand(100, 240);
        title("§l♪", "§f歩き回ろう");
        for (let t = 0; t < len && !aborted(); t += 5) {
            cmd(`playsound note.harp @a 0 2 0 1 ${(0.6 + Math.random() * 1.2).toFixed(2)}`);
            actionbar("§e椅子取りゲーム §f♪ 音楽が止まったら座ろう");
            await wait(5);
        }
        if (aborted()) return [];
        // トロッコを (人数-1) 台
        const need = Math.max(1, players.length - 1);
        const spawn = () => {
            const e = dim().spawnEntity("minecraft:minecart", { x: rand(-6, 6) + 0.5, y: 1, z: rand(-6, 6) + 0.5 });
            e.addTag("mmgplus_chair");
        };
        for (let i = 0; i < need; i++) spawn();
        title("§c§l座れ！", `§fトロッコ ${need}台`);
        cmd("playsound random.anvil_land @a 0 2 0 1 1.5");
        for (let t = 0; t < 100 && !aborted(); t += 2) {
            // 壊されたら出し直す
            cmd("kill @e[type=item,x=0,y=1,z=0,r=12]");
            for (let n = chairs().length; n < need; n++) spawn();
            const seated = alive().filter(ridingCart).length;
            actionbar(`§c座れ！ §f${seated}/${need}  §7残り ${Math.ceil((100 - t) / 20)}秒`);
            if (seated >= need) break;
            await wait(2);
        }
        const losers = alive().filter((p) => !ridingCart(p));
        if (start.length < 2) return losers.length ? [] : alive();
        losers.forEach((p) => out(p, "§c座れなかった..."));
        cmd("ride @a stop_riding");
        cmd("kill @e[type=minecart,tag=mmgplus_chair]");
        await wait(40);
    }
    return [];
}

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
const fmtRecord = (id, v) => (id === 25 ? `${v.toFixed(2)}秒` : `${v}個`);

// point を見張って増えた分を記録する(試合の最後に point は消されるので、その直前の値で順位を決める)
let lastPts = {};
let matchPlayers = new Set();
let wasPlaying = false;
system.runInterval(() => {
    const isPlaying = score("game", "playing") === 1;
    const sg = score("game", "selectgame") ?? 0;
    if (isPlaying) {
        for (const p of playing()) matchPlayers.add(p.name);
        const o = obj("point");
        if (o) {
            for (const part of o.getParticipants()) {
                let v; try { v = o.getScore(part); } catch { continue; }
                const name = part.displayName, prev = lastPts[name] ?? 0;
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
    if (p.typeId === "minecraft:player" && p.hasTag("playing")) { st(p.name).death++; dirty = true; }
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
    for (let g = 0; g < GAMES.length; g += 9) {
        const lines = [];
        for (let id = g + 1; id <= Math.min(g + 9, GAMES.length); id++) {
            const best = each((s) => s.gw[id] ?? 0).filter(([, v]) => v > 0).sort((a, b) => b[1] - a[1])[0];
            lines.push(`§f${GAMES[id - 1]}: ${best ? `§a${best[0]} §b${best[1]}勝` : "§7-"}`);
        }
        list.push([`§l§aゲーム別 勝利数王 (${g / 9 + 1}/3)§r`, ...lines].join("\n"));
    }
    const recs = Object.entries(records).map(([id, r]) => `§f${GAMES[id - 1]}: §a${r.name} §b${fmtRecord(+id, r.v)}`);
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
