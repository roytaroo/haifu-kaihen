// MEGAMI PARTY LAND(MPL): すごろく + ミニゲーム
// 場所: ミニゲームの会場 = x -24〜25, z -49〜50(床 y=0)/ ボード = 中心 (0, 0, 130)/ 空のワールド(ボイド)
// ミニゲームの共通の約束(下の「ミニゲーム」の部分はこれを使う):
//   スコアボード game に selectgame(今のミニゲームの番号)・playing(1 = 遊んでいる)・level(むずかしさ 1〜5)
//   参加している人はタグ playing。脱落はタグ mmgplus_out。BOT はタグ mmgbot(BOT パックがつける)
import { world, system, GameMode, ItemStack, ItemLockMode, ScreenDisplay, World, Player } from "@minecraft/server";
import { ActionFormData, ModalFormData, MessageFormData, uiManager } from "@minecraft/server-ui";

// ===== 文字を全部太字に(タイトル・お知らせ・チャット・フォーム)=====
// 頭の見えない印(§のつづき)はそのまま残して、そのあとを太字にする。色を変えても太字が切れないように §x のあとにも §l
const boldText = (t) => {
    if (typeof t !== "string") return t;
    const m = t.match(/^(?:§.)*/)[0];
    return m + "§l" + t.slice(m.length).replace(/§([0-9a-fr])/g, "§$1§l");
};
const wrapBold = (proto, names, argIdx = [0]) => {
    for (const n of names) {
        const f = proto?.[n]; if (typeof f !== "function") continue;
        proto[n] = function (...a) { for (const i of argIdx) if (i < a.length) a[i] = typeof a[i] === "object" && a[i] && "subtitle" in a[i] ? { ...a[i], subtitle: boldText(a[i].subtitle) } : boldText(a[i]); return f.apply(this, a); };
    }
};
try {
    wrapBold(ScreenDisplay.prototype, ["setActionBar", "updateSubtitle"]);
    wrapBold(ScreenDisplay.prototype, ["setTitle"], [0, 1]);
    wrapBold(World.prototype, ["sendMessage"]); wrapBold(Player.prototype, ["sendMessage"]);
    wrapBold(ActionFormData.prototype, ["title", "body", "button"]);
    wrapBold(MessageFormData.prototype, ["title", "body", "button1", "button2"]);
    wrapBold(ModalFormData.prototype, ["title", "toggle", "slider", "dropdown", "textField"]);
} catch {}


const SPECTATOR = GameMode.Spectator ?? GameMode.spectator;
const ADVENTURE = GameMode.Adventure ?? GameMode.adventure;
const dim = () => world.getDimension("overworld");
const cmd = (c) => { try { dim().runCommand(c); } catch (e) { console.warn(`[MPL] ${c}: ${e}`); } };
const wait = (ticks) => new Promise((r) => system.runTimeout(r, Math.max(1, Math.floor(ticks))));
const rand = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
function load(key, def) { try { const v = world.getDynamicProperty(key); return typeof v === "string" ? JSON.parse(v) : def; } catch { return def; } }
const save = (key, v) => world.setDynamicProperty(key, JSON.stringify(v));
function obj(name) { return world.scoreboard.getObjective(name) ?? world.scoreboard.addObjective(name, name); }
function score(objective, name) { try { return world.scoreboard.getObjective(objective)?.getScore(name); } catch { return undefined; } }
const setScore = (objective, name, v) => obj(objective).setScore(name, v);
const level = () => Math.min(5, Math.max(1, score("game", "level") ?? 2));
const playing = () => world.getPlayers({ tags: ["playing"] });
const isBot = (p) => p.hasTag("mmgbot");
const botStr = () => score("setting", "bot_strength") ?? 1;
const chance = (weak, normal, strong) => Math.random() < [weak, normal, strong][botStr()];
const isAdmin = (p) => p.hasTag("mpl_admin");
const botGo = (p, x, y, z, sp = "") => cmd(`scriptevent mmgbot:move ${p.name} ${x.toFixed(2)} ${y.toFixed(2)} ${z.toFixed(2)} ${sp}`);
const botLook = (p, x, y, z) => cmd(`scriptevent mmgbot:look ${p.name} ${x} ${y} ${z}`);
const botSneak = (p, on) => cmd(`scriptevent mmgbot:sneak ${p.name} ${on ? 1 : 0}`);
const botJump = (p) => cmd(`scriptevent mmgbot:jump ${p.name}`);

// ===== ミニゲームの一覧(番号はミニゲームのコードと同じ)=====
const MINIGAMES = {
    25: "計算早押し", 26: "色の記憶", 27: "椅子取りゲーム", 28: "宝探しプール", 29: "ファイアバー", 30: "ボートレース", 31: "ピッタリ止め", 32: "ニワトリ集め",
    33: "一番多い色は？", 34: "早押し反射", 36: "隕石よけ", 37: "押し寄せる壁", 38: "障害物ダッシュ", 40: "レーザー回避", 42: "ものまねポーズ", 43: "ピクセルアート",
    44: "卵キャッチ", 45: "コイン噴水", 46: "ふくらむ風船", 47: "まっくらスイカ割り", 48: "下がる天井", 50: "ボヨンボール", 51: "巨大ワニの歯",
    52: "コマぶつけ", 53: "旗あげゲーム", 54: "お皿バランス", 55: "大玉ころがし", 56: "ロデオ", 57: "バンパーカー", 58: "アスレチック",
};
const MG_IDS = Object.keys(MINIGAMES).map(Number);
const GAMES = []; for (const [id, n] of Object.entries(MINIGAMES)) GAMES[id - 1] = n; // ミニゲームのコードが GAMES[id - 1] を使う時のため

// ===== ミニゲームの共通処理 =====
const run = { id: 0, active: false };
const aborted = () => !run.active || score("game", "playing") !== 1 || score("game", "selectgame") !== run.id;
function out(p, msg) {
    p.addTag("mmgplus_out");
    bar(p, msg);
    p.setGameMode(SPECTATOR);
    cmd(`playsound note.bass "${p.name}"`);
}
const alive = () => playing().filter((p) => !p.hasTag("mmgplus_out"));
function ring(r, h, block, y = 1) {
    for (let a = 0; a < 360; a += 2) {
        const x = Math.round(Math.cos((a * Math.PI) / 180) * r), z = Math.round(Math.sin((a * Math.PI) / 180) * r);
        cmd(`fill ${x} ${y} ${z} ${x} ${y + h - 1} ${z} ${block}`);
    }
}
function disc(r, block, y = 0) {
    for (let z = -r; z <= r; z++) { const w = Math.floor(Math.sqrt(r * r - z * z)); cmd(`fill ${-w} ${y} ${z} ${w} ${y} ${z} ${block}`); }
}
const PROPS = ["chair", "treasure_gold", "treasure_diamond", "treasure_emerald", "fireball", "balloon", "coin", "egg", "golden_egg", "melon", "croc", "tooth", "top", "car", "bigball", "boyon", "bull", "plates", "tail", "laser", "laser_beam"];
function clearArena() {
    cmd("fill -24 1 -49 25 8 0 air"); cmd("fill -24 1 1 25 8 50 air");
    cmd("fill -24 0 -49 25 0 50 black_concrete");
    for (const t of PROPS) cmd(`kill @e[type=mmgplus:${t}]`);
    cmd("kill @e[type=boat,tag=mmgplus_boat]"); cmd("kill @e[type=mmgplus:board,tag=mmgplus_label]");
    for (const t of ["chicken", "fox", "pufferfish", "wandering_trader", "witch"]) cmd(`kill @e[type=${t},x=-24,y=-10,z=-49,dx=49,dy=40,dz=99]`);
    cmd("kill @e[type=item,x=-24,y=-10,z=-49,dx=49,dy=40,dz=99]"); cmd("kill @e[type=arrow,x=-24,y=-10,z=-49,dx=49,dy=40,dz=99]");
    cmd("tag @a remove mmgplus_out");
}
const bar = (p, t) => { try { p.onScreenDisplay.setActionBar(t); } catch {} };
const toast = (t) => world.getPlayers().forEach((p) => bar(p, t));
const actionbar = (text, players = playing()) => players.forEach((p) => p.onScreenDisplay.setActionBar(text));
const title = (text, sub = "", stay = 30) => playing().forEach((p) => p.onScreenDisplay.setTitle(text, { subtitle: sub, fadeInDuration: 0, stayDuration: stay, fadeOutDuration: 5 }));
const soundAll = (s, pitch = 1) => cmd(`execute as @a[tag=playing] at @s run playsound ${s} @s ~ ~ ~ 1 ${pitch}`);
// 記録(ゲームごとの一番)
const records = load("records", {});
function record(id, name, v, kind) {
    const r = records[id];
    if (!r || (kind === "min" ? v < r.v : v > r.v)) { records[id] = { name, v, kind }; save("records", records); toast(`§6★ ${MINIGAMES[id]} の新記録！ §f${name} ${Number.isInteger(v) ? v : v.toFixed(2)}`); }
}

// ===== 25. 計算早押し =====
// レベル1でも2けた。レベルが上がると かけ算・3つの数・2けた×2けた
function makeQuestion(lv) {
    let text, ans;
    if (lv === 1) { const a = rand(2, 9), b = rand(2, 9); text = `${a} + ${b}`; ans = a + b; }
    else if (lv === 2) { const a = rand(11, 39), b = rand(2, 9); if (Math.random() < 0.5) { text = `${a} + ${b}`; ans = a + b; } else { text = `${a} - ${b}`; ans = a - b; } }
    else if (lv === 3) { const a = rand(2, 9), b = rand(2, 9); text = `${a} × ${b}`; ans = a * b; }
    else if (lv === 4) { const a = rand(12, 49), b = rand(11, 39); if (Math.random() < 0.5) { text = `${a} + ${b}`; ans = a + b; } else { const [x, y] = a > b ? [a, b] : [b, a]; text = `${x} - ${y}`; ans = x - y; } }
    else { const a = rand(11, 25), b = rand(2, 6); text = `${a} × ${b}`; ans = a * b; }
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
                toast(`§a${p.name} が正解！ §7(${sec.toFixed(2)}秒) §f${Q.text} = ${Q.ans}`);
                record(25, p.name, sec, "min");
                cmd(`playsound random.levelup "${p.name}"`);
                for (const o of playing()) if (o.id !== p.id) uiManager.closeAllForms(o);
            } else {
                bar(p, "§cざんねん！この問題はもう答えられません");
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
        if (timedOut) toast(`§7時間切れ！ ${Q.text} = ${Q.ans}`);
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
    const flash = [22, 19, 16, 14, 12][level() - 1];
    const cleared = new Map();
    for (let round = 1; round <= 25; round++) {
        if (aborted()) return [];
        seq.push(rand(0, 4));
        const players = alive();
        if (players.length === 0) break;
        cmd("tp @a[tag=playing,tag=!mmgplus_out] 0 1 0");
        title(`§l${seq.length}個`, "§fおぼえよう！ §7(光る床と柱を見て)", 40);
        await wait(round === 1 ? 70 : 45);
        for (const i of seq) {
            if (aborted()) return [];
            simonLight(PADS[i], true);
            soundAll("note.pling", PADS[i].pitch);
            actionbar(`§d色の記憶 §f${PADS[i].name}`);
            await wait(flash);
            simonLight(PADS[i], false);
            await wait(7);
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
                    botGo(p, PADS[i].cx + 0.5, 1, PADS[i].cz + 0.5);
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
                        if (s.idx >= seq.length) { bar(p, "§aクリア！"); left--; }
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
    ring(12, 3, "barrier");
    for (let a = 0; a < 360; a += 45) cmd(`setblock ${Math.round(Math.cos((a * Math.PI) / 180) * 11)} 1 ${Math.round(Math.sin((a * Math.PI) / 180) * 11)} lantern`);
}
// 「むすんでひらいて」風の短い曲(半音の数)。1音 = 4tick
const chairs = () => dim().getEntities({ type: "mmgplus:chair" });
const seated = (p) => p.getComponent("minecraft:riding")?.entityRidingOn?.typeId === "mmgplus:chair";

async function gameChairs() {
    const start = playing();
    if (start.length < 2) toast("§7ひとりなので、イスに座れたら勝ち！");
    for (let round = 1; !aborted(); round++) {
        const players = alive();
        if (players.length <= 1 && start.length > 1) return players;
        cmd("ride @a stop_riding");
        cmd("kill @e[type=mmgplus:chair]");
        title(`§lラウンド ${round}`, "§f♪ 曲のあいだ歩き回ろう");
        await wait(30);
        // 曲(だいきがくれたオクラホマミキサー、RP の sounds/mmgplus/chair_music.ogg)を最初から流し、6〜20秒のどこかで止める
        cmd("playsound mmgplus.chair_music @a[tag=playing] 0 3 0 4 1");
        const len = rand(120, 400);
        for (let t = 0; t < len && !aborted(); t += 5) {
            actionbar("§e椅子取りゲーム §f♪♪♪");
            await wait(5);
        }
        cmd("stopsound @a mmgplus.chair_music");
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
                if (c.hasTag("mmgplus_fake") && riders.length) { riders.forEach((r) => bar(r, "§cニセモノのイスだった！")); cmd("playsound random.pop @a 0 2 0 1 0.6"); c.remove(); continue; }
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
    const TIME = 600;
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
            if (lost) { got.set(p.name, got.get(p.name) - lost); bar(p, `§cフグにさされて ${lost}点 落とした！`); cmd(`playsound mob.pufferfish.sting "${p.name}"`); }
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
            if (hit.tr.pt >= 5) toast(`§a${p.name} がエメラルドを見つけた！ §f(+5点)`);
        }
        if (t % 10 === 0) for (const p of playing()) p.onScreenDisplay.setActionBar(`§6宝探し §fあなた: §e${got.get(p.name) ?? 0}点  §7残り ${Math.ceil((TIME - t) / 20)}秒`);
        await wait(2);
    }
    const best = Math.max(0, ...got.values());
    if (best === 0) return [];
    const win = playing().filter((p) => got.get(p.name) === best);
    win.forEach((p) => record(28, p.name, best, "max"));
    toast(`§6宝探し: ${win.map((p) => p.name).join(", ")} が ${best}点で1位！`);
    return win;
}

// ===== 29. ファイアバー =====
// 中心のブロックから2本の火の玉の棒(mmgplus:fireball)が回る。ジャンプでよける。だんだん速く、ときどき逆回転
const FB_LEN = 10, FB_STEP = 0.95; // 10個 × 0.95 = 半径9.5(床の端まで)
const lastJump = new Map();
function buildFirebar() {
    clearArena();
    disc(10, "magma_block");
    disc(9, "polished_blackstone_bricks");
    disc(2, "gilded_blackstone");
    ring(10, 3, "barrier");
    // 真ん中の炎の柱(ここから棒が出る)
    cmd("fill 0 1 0 0 2 0 nether_bricks"); cmd("setblock 0 3 0 magma_block");
    for (let a = 0; a < 360; a += 30) cmd(`setblock ${Math.round(Math.cos((a * Math.PI) / 180) * 9)} 0 ${Math.round(Math.sin((a * Math.PI) / 180) * 9)} shroomlight`);
}
// 棒(中心から角度 a の線)までの距離と、根元からの長さ
function barHit(px, pz, a, len) {
    const dx = px - 0.5, dz = pz - 0.5, along = dx * Math.cos(a) + dz * Math.sin(a), perp = Math.abs(-dx * Math.sin(a) + dz * Math.cos(a));
    return along > 0.4 && along < len + 0.4 && perp < 0.6;
}
async function gameFirebar() {
    const start = playing();
    const balls = [];
    for (let arm = 0; arm < 2; arm++) for (let i = 1; i <= FB_LEN; i++) {
        try { balls.push({ e: dim().spawnEntity("mmgplus:fireball", { x: 0.5, y: 1.3, z: 0.5 }), arm, r: i * FB_STEP }); } catch {}
    }
    let theta = 0, dir = 1, omega = (Math.PI * 2) / 100, swept = 0, revs = 0, high = null;
    const t0 = Date.now();
    title("§6§lファイアバー！", "§f回ってくる火の玉をジャンプでよけよう");
    await wait(40);
    const place = () => balls.forEach((b) => { if (b.e.isValid) b.e.teleport({ x: 0.5 + Math.cos(theta + b.arm * Math.PI) * b.r, y: 1.3, z: 0.5 + Math.sin(theta + b.arm * Math.PI) * b.r }); });
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
                // 当たり: このtickで棒が通った角度(前・中・今の3か所)のどこかで棒に近く、足が火の玉より下
                const hitNow = [0, 0.5, 1].some((k) => barHit(x, z, prev + step * k + arm * Math.PI, FB_LEN * FB_STEP));
                if (y < 1.6 && hitNow) {
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
            for (let i = 2; i <= FB_LEN; i++) { try { high.balls.push({ e: dim().spawnEntity("mmgplus:fireball", { x: 0.5, y: 2.2, z: 0.5 }), r: i * FB_STEP }); } catch {} }
            title("§c§l上の棒が出た！", "§f上の棒は§eしゃがんで§fよけよう", 30); soundAll("mob.blaze.shoot", 0.7);
        }
        if (high) {
            const hp = high.theta, hs = -step * 0.7;
            high.theta += hs;
            high.balls.forEach((b) => { if (b.e.isValid) b.e.teleport({ x: 0.5 + Math.cos(high.theta) * b.r, y: 2.2, z: 0.5 + Math.sin(high.theta) * b.r }); });
            for (const p of alive()) {
                const { x, z } = p.location, r = Math.hypot(x - 0.5, z - 0.5);
                if (r < 1.5 || r > FB_LEN * FB_STEP + 0.6 || p.isSneaking) continue;
                if ([0, 0.5, 1].some((k) => barHit(x, z, hp + hs * k, FB_LEN * FB_STEP))) {
                    if (isBot(p) && chance(0.6, 0.8, 0.93)) continue; // BOT はしゃがんだことにする
                    out(p, "§c上の棒に当たった！(しゃがむとよけられる)");
                }
            }
        }
        if (t % 3 === 0) for (const b of balls) if (b.e.isValid && Math.random() < 0.35) cmd(`particle minecraft:basic_flame_particle ${b.e.location.x} ${b.e.location.y + 0.2} ${b.e.location.z}`);
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
                toast(`§b${order.length}位 §f${p.name} §7${s.done.toFixed(2)}秒`);
                record(30, p.name, s.done, "min");
                cmd(`playsound random.levelup "${p.name}"`);
                const boat = p.getComponent("minecraft:riding")?.entityRidingOn;
                cmd(`ride "${p.name}" stop_riding`); try { boat?.remove(); } catch {}
                p.setGameMode(SPECTATOR);
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
    toast(`§e目標 ${target}.00秒  ` + rows.slice(0, 3).map(([n, v], i) => `§f${i + 1}. ${n} §b${v.toFixed(2)}`).join("  "));
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
    ring(22, 3, "barrier");
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
    const TIME = 1200;
    const players = playing();
    const pen = new Map(players.map((p, i) => [p.name, i % PENS.length]));
    players.forEach((p) => {
        const [cx, cz] = PENS[pen.get(p.name)];
        p.teleport({ x: cx * 0.7 + 0.5, y: 1, z: cz * 0.7 + 0.5 });
        bar(p, `§fあなたの囲いは ${PEN_COLORS[pen.get(p.name)]} の床です`);
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
    toast(`§aニワトリ集め: ${win.map((p) => p.name).join(", ")} が ${best}羽で1位！`);
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
        toast(`§f答え: ${cols[ans][1]}§f (${cols.map((c, i) => `${c[1]}${count[i]}`).join(" ")}§f)`);
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
            for (const p of players) if (!foul.has(p.name) && p.isSneaking) { foul.add(p.name); bar(p, "§cフライング！"); cmd(`playsound note.bass "${p.name}"`); }
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
            toast(`§aラウンド${r}: ${order.slice(0, 3).map(([n, v], i) => `${i + 1}位 ${n} ${(v / 1000).toFixed(2)}秒`).join(" / ")}`);
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
        if (t % Math.max(4, 16 - Math.floor(sec / 4) - level()) === 0) {
            const tgt = alive()[rand(0, Math.max(0, alive().length - 1))];
            const x = tgt && Math.random() < 0.85 ? tgt.location.x + rand(-1, 1) : rand(-9, 9) + 0.5, z = tgt && Math.random() < 0.85 ? tgt.location.z + rand(-1, 1) : rand(-9, 9) + 0.5;
            let e; try { e = dim().spawnEntity("mmgplus:fireball", { x, y: 30, z }); } catch {}
            if (e) falling.push({ e, x, z, land: system.currentTick + Math.max(16, 24 - level()) });
        }
        for (const m of falling.slice()) {
            const left = m.land - system.currentTick;
            if (t % 4 === 0) cmd(`particle minecraft:redstone_wire_dust_particle ${m.x} 1.1 ${m.z}`);
            for (let i = 0; i < 8; i++) { const a = (i / 8) * Math.PI * 2; if (t % 4 === 0) cmd(`particle minecraft:basic_flame_particle ${m.x + Math.cos(a) * 3} 1.1 ${m.z + Math.sin(a) * 3}`); }
            if (left > 0) { try { m.e.teleport({ x: m.x, y: 1 + left, z: m.z }); } catch {} continue; }
            falling.splice(falling.indexOf(m), 1);
            try { m.e.remove(); } catch {}
            cmd(`particle minecraft:huge_explosion_emitter ${m.x} 1.5 ${m.z}`);
            cmd(`playsound random.explode @a ${m.x} 1 ${m.z} 1 1`);
            for (const p of alive()) if (Math.hypot(p.location.x - m.x, p.location.z - m.z) < 3) { if (isBot(p) && chance(0.4, 0.55, 0.7)) continue; out(p, "§c隕石に当たった！"); }
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
        const speed = Math.max(2, 5 - Math.floor(wave / 4) - (level() >= 4 ? 1 : 0));
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
            if (z === -14) for (const p of alive().filter(isBot)) if (chance(0.6, 0.8, 0.95)) botGo(p, holes[0] + hw / 2, 1, p.location.z);
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
// z -44 → 44 のまっすぐなコース。動く壁(2段の速さ)・ブロックのハードル・押し戻しの床をこえてゴールへ。当たるとひとつ前のチェックポイントに戻る
const DASH_W = 4;
const dashBars = [];
function buildWalls() {
    clearArena();
    cmd("fill -8 0 -20 8 0 12 light_gray_concrete");
    cmd("fill -8 1 -20 -8 4 12 barrier"); cmd("fill 8 1 -20 8 4 12 barrier"); cmd("fill -8 1 12 8 4 12 barrier");
    for (let z = -18; z <= 10; z += 4) { cmd(`setblock -8 0 ${z} sea_lantern`); cmd(`setblock 8 0 ${z} sea_lantern`); }
}
function buildDash() {
    clearArena();
    dashBars.length = 0;
    for (let z = -36; z <= 38; z += 5) dashBars.push({ z, w: rand(3, 4), x: rand(-DASH_W, 0), dir: Math.random() < 0.5 ? 1 : -1, fast: z > 0 });
    cmd(`fill ${-DASH_W} 0 -46 ${DASH_W} 0 46 white_concrete`);
    cmd(`fill ${-DASH_W - 1} 1 -46 ${-DASH_W - 1} 3 46 glass`); cmd(`fill ${DASH_W + 1} 1 -46 ${DASH_W + 1} 3 46 glass`);
    cmd(`fill ${-DASH_W} 1 -46 ${DASH_W} 3 -46 glass`);
    // ハードル(1マスのブロック。すきまは1か所だけ)
    for (const z of [-38, -27, -17, -8, 3, 13, 23, 33]) { cmd(`fill ${-DASH_W} 1 ${z} ${DASH_W} 1 ${z} red_wool`); const g = rand(-DASH_W, DASH_W); cmd(`setblock ${g} 1 ${z} air`); }
    // 押し戻しの床(ソウルサンドでおそくなる)
    for (const z of [-22, 8, 28]) cmd(`fill ${-DASH_W} 0 ${z} ${DASH_W} 0 ${z + 1} soul_sand`);
    for (const z of [-24, 0, 24]) cmd(`fill ${-DASH_W} 0 ${z - 2} ${DASH_W} 0 ${z - 2} lime_concrete`); // チェックポイント
    cmd(`fill ${-DASH_W} 0 -42 ${DASH_W} 0 -42 lime_concrete`);
    for (let x = -DASH_W; x <= DASH_W; x++) for (const z of [44, 45]) cmd(`setblock ${x} 0 ${z} ${(x + z) % 2 === 0 ? "white_concrete" : "black_concrete"}`);
    cmd(`fill ${-DASH_W} 1 -41 ${DASH_W} 2 -41 glass`);
}
async function gameDash() {
    const players = playing();
    players.forEach((p, i) => p.teleport({ x: -3 + (i % 7) + 0.5, y: 1, z: -44 + Math.floor(i / 7) * 1.2 }, { rotation: { x: 0, y: 0 } }));
    title("§b§l障害物ダッシュ", "§f動く壁とハードルをこえてゴールへ！", 30); await wait(30);
    cmd(`fill ${-DASH_W} 1 -41 ${DASH_W} 2 -41 air`);
    title("§a§lGO!"); soundAll("note.pling", 1.6);
    const t0 = Date.now(), order = [];
    const cp = (z) => [-42, -26, -2, 22].filter((c) => c <= z).pop() ?? -42;
    for (let t = 0; t < 3000 && !aborted(); t += 2) {
        for (const b of dashBars) {
            const every = b.fast ? [3, 2, 2, 1, 1][level() - 1] : [5, 4, 3, 3, 2][level() - 1];
            if (t % (every * 2) !== 0) continue;
            cmd(`fill ${b.x} 1 ${b.z} ${b.x + b.w - 1} 2 ${b.z} air`);
            b.x += b.dir; if (b.x <= -DASH_W || b.x + b.w - 1 >= DASH_W) b.dir = -b.dir;
            cmd(`fill ${b.x} 1 ${b.z} ${b.x + b.w - 1} 2 ${b.z} ${b.fast ? "orange_concrete" : "red_concrete"}`);
        }
        for (const p of playing()) {
            if (order.includes(p)) continue;
            const { x, z } = p.location;
            if (isBot(p) && t % 6 === 0) {
                const bar = dashBars.find((b) => b.z > z && b.z < z + 5);
                let tx = p.location.x;
                if (bar && tx >= bar.x - 1 && tx <= bar.x + bar.w + 1) tx = bar.x - 1.5 >= -DASH_W ? bar.x - 1.5 : bar.x + bar.w + 1.5; // 壁のないほうへ
                tx = Math.max(-DASH_W + 0.5, Math.min(DASH_W + 0.5, tx + (Math.random() - 0.5)));
                botGo(p, tx, 1, Math.min(46, z + 5), [0.8, 0.95, 1.1][botStr()]);
            }
            if (isBot(p) && t % 4 === 0 && [-38, -27, -17, -8, 3, 13, 23, 33].some((hz) => hz - z > 0 && hz - z < 1.6)) botJump(p);
            if (dashBars.some((b) => Math.floor(z) === b.z && Math.floor(x) >= b.x && Math.floor(x) < b.x + b.w)) {
                if (isBot(p) && chance(0.4, 0.55, 0.7)) continue; // BOT もよけることがある
                const c = cp(z); p.teleport({ x: 0.5, y: 1, z: c + 0.5 }, { rotation: { x: 0, y: 0 } });
                bar(p, "§c当たった！ チェックポイントへ戻る"); cmd(`playsound note.bass "${p.name}"`);
            }
            if (z >= 44) {
                order.push(p); p.setGameMode(SPECTATOR);
                const sec = (Date.now() - t0) / 1000;
                toast(`§b${order.length}位 §f${p.name} §7${sec.toFixed(2)}秒`);
                record(38, p.name, sec, "min");
            }
            if (t % 10 === 0) p.onScreenDisplay.setActionBar(`§b障害物ダッシュ §fゴールまで ${Math.max(0, Math.round(44 - z))}m`);
        }
        if (players.every((p) => order.includes(p) || !p.isValid)) break;
        await wait(2);
    }
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
            if (g.p.isValid) bar(g.p, `§fラウンド${r}: 正解 ${ok} / まちがい ${ng} → ${pts}点`);
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
// 光るレーザーの棒(モデル)が部屋の端から端へ動く。低いのはジャンプ、高いのはしゃがみでよける
async function gameLaser() {
    const start = playing(), t0 = Date.now();
    title("§c§lレーザー回避", "§f低いのは§eジャンプ§f、高いのは§eしゃがみ§fでよける");
    await wait(50);
    const lasers = [];
    for (let t = 0; t < 2400 && !aborted(); t += 2) {
        const sec = (Date.now() - t0) / 1000;
        if (t % Math.max(30, 90 - Math.floor(sec) - level() * 6) === 0) {
            const axis = Math.random() < 0.5 ? "x" : "z", dir = Math.random() < 0.5 ? 1 : -1, high = Math.random() < 0.4;
            const e = spawnAt("mmgplus:laser_beam", { x: 0.5, y: high ? 1.9 : 1.2, z: 0.5 });
            if (e) lasers.push({ e, axis, dir, pos: -9 * dir, high, speed: 0.12 + Math.min(0.2, sec / 300) + level() * 0.02 });
            soundAll("mob.guardian.attack", 1.6);
        }
        for (const L of lasers.slice()) {
            const prev = L.pos; L.pos += L.dir * L.speed * 2;
            const y = L.high ? 1.9 : 1.2;
            try { L.e.teleport(L.axis === "x" ? { x: L.pos, y, z: 0.5 } : { x: 0.5, y, z: L.pos }, { rotation: { x: 0, y: L.axis === "x" ? 90 : 0 } }); } catch {}
            for (const p of alive()) {
                const c = L.axis === "x" ? p.location.x : p.location.z;
                if ((c - prev) * (c - L.pos) > 0 && Math.abs(c - L.pos) > 0.3) continue;
                const dodge = L.high ? p.isSneaking : p.location.y > 1.45;
                if (isBot(p) ? !chance(0.7, 0.85, 0.95) : !dodge) out(p, L.high ? "§c頭のレーザーに当たった！(しゃがむ)" : "§c足のレーザーに当たった！(ジャンプ)");
            }
            if (Math.abs(L.pos) > 9.5) { lasers.splice(lasers.indexOf(L), 1); try { L.e.remove(); } catch {} }
        }
        if (t % 20 === 0) actionbar(`§cレーザー回避 §f残り ${alive().length}人`);
        if (endSurvive(start, sec)) break;
        await wait(2);
    }
    lasers.forEach((L) => { try { L.e.remove(); } catch {} });
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
    bar(a, `§aしっぽをうばった！ (${ta?.n ?? 0}本)`); bar(b, "§cしっぽをとられた！");
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
// 4つの壁が 赤・青・黄・緑。「〇の壁を向いて」+「しゃがむ/ジャンプ/そのまま」。合図の時にちがったら脱落
const POSE_WALLS = [["§c赤", 180, "red"], ["§9青", -90, "blue"], ["§e黄", 0, "yellow"], ["§a緑", 90, "lime"]]; // 北・東・南・西
function buildPose() {
    buildArena(7, "smooth_quartz", "glass", 3);
    cmd("fill -8 1 -8 8 5 -8 red_concrete"); cmd("fill 8 1 -8 8 5 8 blue_concrete"); cmd("fill -8 1 8 8 5 8 yellow_concrete"); cmd("fill -8 1 -8 -8 5 8 lime_concrete");
}
async function gamePose() {
    const start = playing();
    title("§d§lものまねポーズ", "§f言われた色の壁を向いて、ポーズで「ハイ！」を待とう", 50);
    await wait(50);
    for (let r = 1; r <= 20 && !aborted(); r++) {
        const [cn, yaw] = POSE_WALLS[rand(0, 3)], act = ["しゃがむ", "ジャンプ", "そのまま"][rand(0, 2)];
        const time = Math.max(16, 50 - r * 2 - level() * 3);
        title(`§l${cn}§fの壁を向いて`, `§e${act}`, time);
        soundAll("note.pling", 1);
        const wallAt = { 180: [0.5, 2, -10], [-90]: [10, 2, 0.5], 0: [0.5, 2, 10], 90: [-10, 2, 0.5] }[yaw];
        system.runTimeout(() => { for (const p of alive().filter(isBot)) { const ok = Math.random() < [0.72, 0.84, 0.92][botStr()]; const w = ok ? wallAt : [rand(-10, 10), 2, rand(-10, 10)]; botLook(p, ...w); botSneak(p, act === "しゃがむ" && ok); } }, Math.floor(time / 2));
        await wait(time);
        for (const p of alive().filter(isBot)) if (act === "ジャンプ") botJump(p);
        title("§a§lハイ！", "", 10);
        if (act === "ジャンプ") await wait(3);
        for (const p of alive()) {
            const dy = Math.abs(((p.getRotation().y - yaw) % 360 + 540) % 360 - 180);
            const ok = dy < 45 && (act === "しゃがむ" ? p.isSneaking : act === "ジャンプ" ? p.location.y > 1.15 : !p.isSneaking && p.location.y < 1.15);
            if (!ok) out(p, `§cちがうポーズ！(${cn}§c・${act})`);
            if (isBot(p)) botSneak(p, false);
        }
        if (endSurvive(start, r * 5, 60)) break;
        await wait(30);
    }
    return alive();
}

// ===== 43. ピクセルアート再現 =====
// ひとり1つの4x4のキャンバス(まわりをガラスでしきる、上に名前)。ふむたびに 白→赤→青→黄。右のお手本と同じにする
const PIX = ["white", "red", "blue", "yellow"];
async function gamePixel() {
    clearArena();
    const players = playing();
    const target = Array.from({ length: 16 }, () => (Math.random() < 0.35 ? 0 : rand(1, 3)));
    const grids = players.map((p, i) => ({ p, ox: (i % 4) * 12 - 22, oz: Math.floor(i / 4) * 9 - 12, cells: Array(16).fill(0), done: 0 }));
    for (const g of grids) {
        cmd(`fill ${g.ox - 2} 0 ${g.oz - 2} ${g.ox + 9} 0 ${g.oz + 5} polished_deepslate`);
        cmd(`fill ${g.ox - 2} 1 ${g.oz - 2} ${g.ox + 9} 3 ${g.oz - 2} light_blue_stained_glass`); cmd(`fill ${g.ox - 2} 1 ${g.oz + 5} ${g.ox + 9} 3 ${g.oz + 5} light_blue_stained_glass`);
        cmd(`fill ${g.ox - 2} 1 ${g.oz - 2} ${g.ox - 2} 3 ${g.oz + 5} light_blue_stained_glass`); cmd(`fill ${g.ox + 9} 1 ${g.oz - 2} ${g.ox + 9} 3 ${g.oz + 5} light_blue_stained_glass`);
        for (let k = 0; k < 16; k++) {
            cmd(`setblock ${g.ox + (k % 4)} 0 ${g.oz + Math.floor(k / 4)} white_concrete`);
            cmd(`setblock ${g.ox + 5 + (k % 4)} 1 ${g.oz + Math.floor(k / 4)} ${PIX[target[k]]}_concrete`);
        }
        labels([[`§e${g.p.name}`, g.ox + 2, g.oz - 1]]);
        g.p.teleport({ x: g.ox + 2, y: 1, z: g.oz - 0.8 });
    }
    title("§b§lピクセルアート再現", "§f右のお手本と同じ色にしよう(ふむと色が変わる)", 50);
    const t0 = Date.now(), prev = new Map(), order = [];
    for (let t = 0; t < 1600 && !aborted(); t += 2) {
        for (const g of grids) {
            if (!g.p.isValid || g.done) continue;
            if (isBot(g.p)) { if (t % [80, 60, 46][botStr()] === 0) { const k = g.cells.findIndex((c, i) => c !== target[i]); if (k >= 0) { botGo(g.p, g.ox + (k % 4) + 0.5, 1, g.oz + Math.floor(k / 4) + 0.5); g.cells[k] = Math.random() < 0.8 ? target[k] : (target[k] + 1) % 4; cmd(`setblock ${g.ox + (k % 4)} 0 ${g.oz + Math.floor(k / 4)} ${PIX[g.cells[k]]}_concrete`); } } }
            else {
                const lx = Math.floor(g.p.location.x) - g.ox, lz = Math.floor(g.p.location.z) - g.oz;
                const k = lx >= 0 && lx < 4 && lz >= 0 && lz < 4 && g.p.location.y < 1.3 ? lz * 4 + lx : -1;
                if (k >= 0 && prev.get(g.p.name) !== k) { g.cells[k] = (g.cells[k] + 1) % 4; cmd(`setblock ${g.ox + lx} 0 ${g.oz + lz} ${PIX[g.cells[k]]}_concrete`); cmd(`playsound note.hat "${g.p.name}"`); }
                prev.set(g.p.name, k);
            }
            if (g.cells.every((c, i) => c === target[i])) { g.done = (Date.now() - t0) / 1000; order.push(g.p); toast(`§b${order.length}位 §f${g.p.name} §7${g.done.toFixed(1)}秒で完成！`); record(43, g.p.name, g.done, "min"); }
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
    for (let t = 0; t < 600 && !aborted(); t++) {
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
        const taken = new Set();
        if (t % 6 === 0) for (const p of playing().filter(isBot)) { const g = eggs.filter((e) => e.y < 12 && !taken.has(e)).sort((a, b) => Math.hypot(a.x - p.location.x, a.z - p.location.z) - Math.hypot(b.x - p.location.x, b.z - p.location.z))[0]; if (g) taken.add(g); if (g && chance(0.5, 0.7, 0.85)) botGo(p, g.x, 1, g.z); }
        if (t % 10 === 0) for (const p of playing()) p.onScreenDisplay.setActionBar(`§e卵キャッチ §fあなた: ${pts.get(p.name) ?? 0}点  §7残り ${Math.ceil((600 - t) / 20)}秒`);
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
    bar(b, `§cコインを${n}枚落とした！`); cmd(`playsound random.break "${b.name}"`);
});
async function gameCoins() {
    coins.clear(); coinList.length = 0; safeFight();
    cmd("fill -2 1 -2 2 1 2 quartz_block"); cmd("fill -1 2 -1 1 2 1 light_blue_stained_glass"); cmd("setblock 0 3 0 gold_block");
    playing().forEach((p, i, all) => { coins.set(p.name, 0); const a = (i / all.length) * Math.PI * 2; p.teleport({ x: 0.5 + Math.cos(a) * 6, y: 1, z: 0.5 + Math.sin(a) * 6 }, { facingLocation: { x: 0.5, y: 2, z: 0.5 } }); });
    title("§6§lコイン噴水", "§fコインを拾え！ 叩くと相手がコインを落とす");
    for (let t = 0; t < 900 && !aborted(); t++) {
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
        if (t % 10 === 0) for (const p of playing()) p.onScreenDisplay.setActionBar(`§6コイン噴水 §fあなた: §e${coins.get(p.name) ?? 0}枚  §7残り ${Math.ceil((900 - t) / 20)}秒`);
        await wait(1);
    }
    coinList.forEach((c) => { try { c.e.remove(); } catch {} }); coinList.length = 0;
    cmd("gamerule pvp false");
    const w = tops(coins); w.forEach((p) => record(45, p.name, coins.get(p.name), "max")); return w;
}

// ===== 46. ふくらむ風船 =====
// みんなで風船のまわりに輪になって、真ん中を向いて動けない。順番にポンプを1〜3回。割った人がアウト。3分の1になるまで
async function gameBalloon() {
    const start = playing();
    cmd("fill -1 1 -1 1 1 1 red_concrete");
    start.forEach((p, i) => { const a = (i / start.length) * Math.PI * 2; p.teleport({ x: 0.5 + Math.cos(a) * 4.5, y: 1, z: 0.5 + Math.sin(a) * 4.5 }, { facingLocation: { x: 0.5, y: 2.5, z: 0.5 } }); });
    cmd("inputpermission set @a[tag=playing] movement disabled"); cmd("tag @a[tag=playing] add mpl_lock");
    let balloon, size, limit;
    const fresh = () => { try { balloon?.remove(); } catch {} balloon = spawnAt("mmgplus:balloon", { x: 0.5, y: 2, z: 0.5 }); size = 3; limit = rand(10, 24); balloon?.setProperty("mmgplus:size", size); };
    fresh();
    title("§c§lふくらむ風船", "§f順番にポンプを押そう。割った人がアウト");
    await wait(40);
    try {
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
                size++; try { balloon?.setProperty("mmgplus:size", Math.min(30, size)); } catch {}
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
    } finally { cmd("inputpermission set @a movement enabled"); cmd("tag @a remove mpl_lock"); }
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
    cmd(`playsound random.break "${a.name}"`); bar(a, `§aスイカ割り成功！ (${melonPts.get(a.name)}個)`);
    b.remove();
});
async function gameMelon() {
    melonPts.clear();
    cmd("effect @a[tag=playing] darkness 70 0 true"); cmd("effect @a[tag=playing] blindness 70 0 true");
    title("§2§lまっくらスイカ割り", "§f音のする方へ行って、スイカを叩け！");
    for (let t = 0; t < 900 && !aborted(); t += 5) {
        const ms = dim().getEntities({ type: "mmgplus:melon" }).filter((m) => m.isValid);
        for (let n = ms.length; n < Math.max(3, Math.ceil(playing().length / 2)); n++) spawnAt("mmgplus:melon", { x: rand(-9, 9) + 0.5, y: 1, z: rand(-9, 9) + 0.5 });
        if (t % 15 === 0) for (const m of ms) if (m.isValid) cmd(`playsound note.bell @a ${m.location.x} ${m.location.y + 1} ${m.location.z} 1.5 ${(0.8 + Math.random() * 0.4).toFixed(2)}`);
        if (t % 20 === 0) for (const p of playing().filter(isBot)) { const m = ms[rand(0, Math.max(0, ms.length - 1))]; if (m?.isValid && chance(0.15, 0.25, 0.4)) { melonPts.set(p.name, (melonPts.get(p.name) ?? 0) + 1); try { m.remove(); } catch {} } }
        if (t % 10 === 0) for (const p of playing()) p.onScreenDisplay.setActionBar(`§2スイカ割り §fあなた: ${melonPts.get(p.name) ?? 0}個  §7残り ${Math.ceil((900 - t) / 20)}秒`);
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
            if (y === 8) for (const p of alive().filter(isBot)) if (chance(0.5, 0.7, 0.9)) { const [x, z] = hs[rand(0, hs.length - 1)]; botGo(p, x + 0.5, 4, z + 0.5); }
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

// ===== 50. ボヨンボール =====
// はねまわる大きなボールをよける。ボールは10秒ごとにふえる。当たったら脱落
async function gameBoyon() {
    const start = playing(), balls = [], t0 = Date.now();
    const add = () => { const e = spawnAt("mmgplus:boyon", { x: 0.5, y: 8, z: 0.5 }); const a = Math.random() * Math.PI * 2, v = 0.28 + Math.random() * 0.15; if (e) balls.push({ e, x: rand(-6, 6), y: 8, z: rand(-6, 6), vx: Math.cos(a) * v, vy: 0, vz: Math.sin(a) * v }); };
    title("§d§lボヨンボール", "§fはねるボールに当たるな！");
    await wait(30); add(); add();
    for (let t = 0; t < 2400 && !aborted(); t++) {
        const sec = (Date.now() - t0) / 1000;
        if (t % Math.max(100, 220 - level() * 20) === 0 && t > 0) { add(); soundAll("mob.slime.big", 1); }
        for (const b of balls) {
            b.vy -= 0.04; b.x += b.vx; b.y += b.vy; b.z += b.vz;
            if (b.y < 1) { b.y = 1; b.vy = 0.65 + Math.random() * 0.2; cmd(`playsound mob.slime.big @a ${b.x} 1 ${b.z} 0.6 1.3`); }
            const wallHit = (k) => { b[k] = Math.sign(b[k]) * 8; b["v" + k] = -b["v" + k] * (1 + Math.random() * 0.15); b.vy = Math.max(b.vy, 0.35 + Math.random() * 0.3); cmd(`playsound mob.slime.small @a ${b.x} ${b.y} ${b.z} 0.6 1.6`); };
            if (Math.abs(b.x) > 8) wallHit("x");
            if (Math.abs(b.z) > 8) wallHit("z");
            if (b.y > 7) { b.y = 7; b.vy = -Math.abs(b.vy); }
            const sp = Math.hypot(b.vx, b.vz); if (sp > 0.6) { b.vx *= 0.6 / sp; b.vz *= 0.6 / sp; }
            for (const o of balls) if (o !== b) { const dx = o.x - b.x, dz = o.z - b.z, dy = o.y - b.y, d = Math.hypot(dx, dy, dz); if (d > 0 && d < 2.2) { b.vx -= (dx / d) * 0.12; b.vz -= (dz / d) * 0.12; } }
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
const TOOTH_SPOTS = [-5.5, 4.5].flatMap((mx) => [-20, -17, -14, -11].map((mz) => ({ x: CROC_AT.x - mx * CROC_S, y: CROC_AT.y + 5 * CROC_S, z: CROC_AT.z - mz * CROC_S })));
let toothHit = null;
world.afterEvents.entityHitEntity.subscribe((ev) => { if (ev.hitEntity?.typeId === "mmgplus:tooth" && ev.damagingEntity?.typeId === "minecraft:player") toothHit = { p: ev.damagingEntity, e: ev.hitEntity }; });
async function gameCroc() {
    const start = playing();
    const croc = spawnAt("mmgplus:croc", CROC_AT); croc?.setRotation({ x: 0, y: 0 });
    let teeth = [], bad;
    const reset = () => {
        teeth.forEach((e) => { try { e.remove(); } catch {} });
        teeth = TOOTH_SPOTS.map((p) => spawnAt("mmgplus:tooth", p)).filter(Boolean);
        bad = teeth[rand(0, teeth.length - 1)]; croc?.setProperty("mmgplus:bite", 0);
    };
    reset();
    cmd("tp @a[tag=playing] 0.5 1 5 facing 0.5 2 0");
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
            if (isBot(p) && t === 4) { p.botTarget = teeth[rand(0, teeth.length - 1)]; botGo(p, Math.max(-0.8, Math.min(1.8, p.botTarget.location.x)), 1, 2.8); }
            if (isBot(p) && t === 40 && p.botTarget?.isValid) { botLook(p, p.botTarget.location.x, p.botTarget.location.y + 0.3, p.botTarget.location.z); hitE = p.botTarget; }
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
            bar(p, "§aセーフ！");
            await wait(12);
        }
    }
    teeth.forEach((e) => { try { e.remove(); } catch {} }); try { croc?.remove(); } catch {}
    return alive();
}

// ===== 52. コマぶつけ / 57. バンパーカー =====
// 乗り物に乗って見ている方へ進む。ブーストのアイテム(右クリック/タップ)で3秒に1回ダッシュ。ぶつけて場外へ
// 30秒たつと場外の線が少しずつ内側へせまる。BOT は近い相手にねらいを定めて、近づくとブースト
const boostAt = new Map();
function boost(p, veh) {
    if ((boostAt.get(p.name) ?? 0) > system.currentTick) return false;
    boostAt.set(p.name, system.currentTick + 60);
    let dx, dz;
    if (isBot(p)) { const t = nearestOf(p, alive()); if (!t) return false; dx = t.o.location.x - p.location.x; dz = t.o.location.z - p.location.z; }
    else { const v = p.getViewDirection(); dx = v.x; dz = v.z; }
    const d = Math.hypot(dx, dz) || 1;
    veh.applyImpulse({ x: (dx / d) * 1.1, y: 0.1, z: (dz / d) * 1.1 });
    cmd(`playsound mob.blaze.shoot @a ${p.location.x} ${p.location.y} ${p.location.z} 0.7 1.4`);
    cmd(`particle minecraft:large_explosion ${p.location.x} ${p.location.y} ${p.location.z}`);
    return true;
}
world.afterEvents.itemUse.subscribe((ev) => {
    if (ev.itemStack?.typeId !== "mmgplus:boost") return;
    const v = ev.source.getComponent("minecraft:riding")?.entityRidingOn;
    if (v?.hasTag("mmgplus_vehicle") && !boost(ev.source, v)) ev.source.onScreenDisplay.setActionBar("§7ブーストのじゅんび中…");
});
async function gameBumper(type, R0, name) {
    const start = playing(), t0 = Date.now();
    let R = R0;
    boostAt.clear();
    start.forEach((p, i) => { const a = (i / start.length) * Math.PI * 2; mount(p, type, { x: Math.cos(a) * (R - 3) + 0.5, y: 1, z: Math.sin(a) * (R - 3) + 0.5 }); });
    cmd("give @a[tag=playing] mmgplus:boost 1");
    title(`§l${name}`, "§f見ている方へ進む。§eブースト(右クリック)§fでダッシュ！ ぶつけて場外へ");
    await wait(40);
    for (let t = 0; t < 2400 && !aborted(); t++) {
        const sec = (Date.now() - t0) / 1000;
        if (sec > 30 && t % 100 === 0 && R > 4) {
            R--; soundAll("note.bass", 0.6); actionbar(`§c場外の線がせまってきた！`);
            for (let a = 0; a < 360; a += 3) cmd(`setblock ${Math.round(Math.cos((a * Math.PI) / 180) * (R + 1))} 0 ${Math.round(Math.sin((a * Math.PI) / 180) * (R + 1))} red_concrete`);
        }
        const vs = dim().getEntities({ type, tags: ["mmgplus_vehicle"] });
        for (const p of alive()) {
            const v = p.getComponent("minecraft:riding")?.entityRidingOn;
            if (v?.typeId === type) {
                drive(v, p, 0.07, 0.6, alive());
                if (isBot(p)) { const n = nearestOf(p, alive()); if (n && n.d < 4 && Math.random() < [0.03, 0.06, 0.1][botStr()]) boost(p, v); }
            } else if (t % 20 === 0) { const nv = vs.find((x) => !x.getComponent("minecraft:rideable")?.getRiders().length); if (nv) { try { nv.getComponent("minecraft:rideable").addRider(p); } catch {} } }
            if (Math.hypot(p.location.x - 0.5, p.location.z - 0.5) > R + 0.5) { cmd(`ride "${p.name}" stop_riding`); out(p, "§c場外！"); }
        }
        // ぶつかったら速さの差ぶんはね返す(速い方が強い)。少しランダムに横へもずらす
        for (let i = 0; i < vs.length; i++) for (let j = i + 1; j < vs.length; j++) {
            const a = vs[i], b = vs[j], dx = b.location.x - a.location.x, dz = b.location.z - a.location.z, d = Math.hypot(dx, dz);
            if (d > 0.01 && d < 1.5) {
                const va = a.getVelocity(), vb = b.getVelocity(), sa = Math.hypot(va.x, va.z), sb = Math.hypot(vb.x, vb.z);
                const nx = dx / d + (Math.random() - 0.5) * 0.6, nz = dz / d + (Math.random() - 0.5) * 0.6;
                b.applyImpulse({ x: nx * (0.4 + sa * 2.2), y: 0.12, z: nz * (0.4 + sa * 2.2) });
                a.applyImpulse({ x: -nx * (0.4 + sb * 2.2), y: 0.12, z: -nz * (0.4 + sb * 2.2) });
                cmd(`playsound random.anvil_land @a ${a.location.x} 1 ${a.location.z} 0.4 1.8`);
            }
        }
        if (t % 20 === 0) for (const p of alive()) { const left = Math.max(0, Math.ceil(((boostAt.get(p.name) ?? 0) - system.currentTick) / 20)); p.onScreenDisplay.setActionBar(`§e${name} §f残り ${alive().length}人  ${left ? `§7ブースト ${left}秒` : "§aブーストOK"}`); }
        if (endSurvive(start, sec)) break;
        await wait(1);
    }
    cmd("ride @a stop_riding"); cmd(`kill @e[type=${type}]`); cmd("clear @a[tag=playing] mmgplus:boost");
    return alive();
}
function buildRing(R, floor) {
    clearArena();
    disc(R, floor);
    for (let a = 0; a < 360; a += 3) cmd(`setblock ${Math.round(Math.cos((a * Math.PI) / 180) * (R + 1))} 0 ${Math.round(Math.sin((a * Math.PI) / 180) * (R + 1))} red_concrete`);
}

// ===== 53. 旗あげゲーム =====
// 赤い旗を左手(オフハンド)、白い旗を右手に持つ。赤は「しゃがむ」、白は「右クリック/タップ」で上げ下げ。手に持った旗の絵が上/下に変わる
// 指示どおりの形で「ハイ」を待つ。ちがったらアウト。声はあとでだいきがくれる音を入れる(今は文字と効果音)
const flagState = new Map(); // 名前 → [赤が上, 白が上]
function showFlags(p) {
    const [r, w] = flagState.get(p.name) ?? [false, false];
    const eq = p.getComponent("minecraft:equippable");
    try {
        eq?.setEquipment("Offhand", new ItemStack(`mmgplus:flag_red_${r ? "up" : "down"}`));
        p.getComponent("minecraft:inventory")?.container?.setItem(0, new ItemStack(`mmgplus:flag_white_${w ? "up" : "down"}`));
        p.selectedSlotIndex = 0;
    } catch {}
}
world.afterEvents.itemUse.subscribe((ev) => {
    const id = ev.itemStack?.typeId ?? "";
    if (!id.startsWith("mmgplus:flag_white")) return;
    const s = flagState.get(ev.source.name); if (!s) return;
    s[1] = !s[1]; showFlags(ev.source); cmd(`playsound random.click "${ev.source.name}" ~ ~ ~ 1 ${s[1] ? 1.5 : 0.9}`);
});
const wasSneak = new Map();
function makeOrder(state, lv) {
    const pick = () => ["赤", "白", "両方"][rand(0, lv >= 3 ? 2 : 1)];
    const one = () => { const f = pick(), up = Math.random() < 0.5, neg = Math.random() < (lv >= 2 ? 0.3 : 0.1); return { f, up, neg, text: `${f}${up ? "上げ" : "下げ"}${neg ? "ない" : "て"}` }; };
    const parts = [one()]; if (lv >= 2 && Math.random() < 0.5) parts.push(one());
    let [r, w] = state;
    for (const o of parts) if (!o.neg) { if (o.f !== "白") r = o.up; if (o.f !== "赤") w = o.up; }
    const fake = lv >= 3 && Math.random() < 0.2;
    const text = fake ? `${parts[0].f}${parts[0].up ? "上げ" : "下げ"}……ない！` : parts.map((o) => o.text).join("、");
    if (fake) [r, w] = state;
    return { text, state: [r, w] };
}
async function gameFlags() {
    const start = playing();
    flagState.clear(); wasSneak.clear();
    for (const p of start) { flagState.set(p.name, [false, false]); showFlags(p); }
    start.forEach((p, i) => p.teleport({ x: (i % 6) * 2.5 - 6, y: 1, z: Math.floor(i / 6) * 3 - 2 }, { rotation: { x: 0, y: 180 } }));
    title("§l旗あげゲーム", "§c赤(左手)=しゃがむ §f白(右手)=右クリック で上げ下げ", 80);
    await wait(90);
    let want = [false, false];
    for (let r = 1; r <= 25 && !aborted(); r++) {
        const o = makeOrder(want, Math.min(3, 1 + Math.floor((r + level()) / 5)));
        want = o.state;
        title(`§l${o.text}`, "", 40); soundAll("note.pling", 1.2);
        const until = system.currentTick + Math.max(30, 70 - r * 2 - level() * 3);
        while (system.currentTick < until && !aborted()) {
            for (const p of alive()) {
                const s = flagState.get(p.name); if (!s) continue;
                if (isBot(p)) continue;
                if (p.isSneaking && !wasSneak.get(p.name)) { s[0] = !s[0]; showFlags(p); cmd(`playsound random.click "${p.name}" ~ ~ ~ 1 ${s[0] ? 1.5 : 0.9}`); }
                wasSneak.set(p.name, p.isSneaking);
            }
            await wait(1);
        }
        title("§a§lハイ！", "", 10);
        for (const p of alive()) {
            const s = flagState.get(p.name) ?? [false, false];
            if (isBot(p)) { if (chance(0.62, 0.74, 0.84)) { flagState.set(p.name, [...want]); showFlags(p); } else { out(p, "§cまちがえた！"); continue; } }
            else if (s[0] !== want[0] || s[1] !== want[1]) out(p, `§cまちがえた！ 正しくは 赤${want[0] ? "↑" : "↓"} 白${want[1] ? "↑" : "↓"}`);
        }
        actionbar(`§f正しい形: §c赤${want[0] ? "↑" : "↓"} §f白${want[1] ? "↑" : "↓"}`);
        if (endSurvive(start, r * 4, 60)) break;
        await wait(20);
    }
    cmd("clear @a[tag=playing] mmgplus:flag_red_up"); cmd("clear @a[tag=playing] mmgplus:flag_red_down"); cmd("clear @a[tag=playing] mmgplus:flag_white_up"); cmd("clear @a[tag=playing] mmgplus:flag_white_down");
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
            if (isBot(p)) { s.tilt *= 0.8; if (t % 10 === 0) botGo(p, Math.max(-3, Math.min(3, p.location.x + (Math.random() - 0.5) * 2)), 1, Math.min(46, p.location.z + 4), [0.55, 0.7, 0.85][botStr()]); }
            s.v = { x: v.x, z: v.z };
            if (s.e?.isValid) { s.e.teleport({ x: p.location.x, y: p.location.y + 2.05, z: p.location.z }, { rotation: { x: 0, y: p.getRotation().y } }); s.e.setProperty("mmgplus:tilt", Math.max(-10, Math.min(10, Math.round(s.tilt)))); }
            if (Math.abs(s.tilt) > 10) { s.tilt = 0; cmd(`playsound random.glass "${p.name}"`); bar(p, "§cお皿が落ちた！ スタートから"); p.teleport({ x: 0.5, y: 1, z: -40 }, { rotation: { x: 0, y: 0 } }); }
            if (p.location.z >= 44) { order.push(p); const sec = (Date.now() - t0) / 1000; toast(`§b${order.length}位 §f${p.name} §7${sec.toFixed(1)}秒`); record(54, p.name, sec, "min"); }
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
    bigballGaps.length = 0;
    // 柵: 1列につき1本(はば2〜3)だけ。必ず4マス以上のすきまが残る
    if (posts) for (let z = -34; z < 40; z += 7) {
        const w = rand(2, 3), x0 = Math.random() < 0.5 ? -DASH_W : DASH_W - w + 1;
        cmd(`fill ${x0} 1 ${z} ${x0 + w - 1} 1 ${z} oak_fence`);
        bigballGaps.push({ z, x: x0 < 0 ? (x0 + w + DASH_W) / 2 : (-DASH_W + x0 - 1) / 2 });
    }
}
const bigballGaps = [];

// ===== 55. 大玉ころがし =====
// 大玉に乗って、見ている方へ転がしてゴールへ。柵をよけて進む。1〜3位がポイント。ゴールした人は観戦へ
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
                if (isBot(p)) {
                    // BOT: 次の柵のすきまをめざす
                    const g = bigballGaps.find((q) => q.z > p.location.z - 0.5);
                    const tx = g ? g.x + 0.5 : 0.5, tz = g ? g.z + 2 : 46;
                    const dx = tx - p.location.x, dz = tz - p.location.z, d = Math.hypot(dx, dz) || 1, vel = v.getVelocity();
                    if (Math.hypot(vel.x, vel.z) < [0.4, 0.5, 0.6][botStr()]) v.applyImpulse({ x: (dx / d) * 0.07, y: 0, z: (dz / d) * 0.07 });
                } else drive(v, p, 0.06, 0.62);
            } else if (t % 20 === 0) mount(p, "mmgplus:bigball", p.location);
            if (p.location.z >= 44) { order.push(p); cmd(`ride "${p.name}" stop_riding`); p.setGameMode(SPECTATOR); const sec = (Date.now() - t0) / 1000; toast(`§b${order.length}位 §f${p.name} §7${sec.toFixed(1)}秒`); record(55, p.name, sec, "min"); }
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
        system.runTimeout(() => { for (const p of alive().filter(isBot)) { const ok = Math.random() < [0.75, 0.88, 0.96][botStr()]; const l = p.location; botLook(p, l.x + ((left === ok) ? -6 : 6), l.y + 1.5, l.z - 1); } }, rand(6, 12));
        await wait(Math.max(12, 30 - r - level() * 2));
        for (const p of alive()) {
            const d = ((p.getRotation().y - base.get(p.name)) % 360 + 540) % 360 - 180;
            const ok = riding(p, "mmgplus:bull") && (left ? d < -25 : d > 25);
            if (!ok) { cmd(`ride "${p.name}" stop_riding`); out(p, "§c振り落とされた！"); }
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
            for (const q of pts) if (q.cp && Math.abs(l.x - (q.x + 0.5)) < 2.6 && Math.abs(l.z - (q.z + 0.5)) < 2.6 && Math.abs(l.y - (q.y + 1)) < 0.6 && (cp.get(p.name)?.z ?? -99) < q.z) { cp.set(p.name, q); bar(p, "§eチェックポイント！"); cmd(`playsound random.orb "${p.name}"`); }
            if (l.y < 1.5) { const c = cp.get(p.name) ?? start; p.teleport({ x: c.x + 0.5, y: c.y + 1, z: c.z + 0.5 }, { rotation: { x: 0, y: 0 } }); }
            if (l.z >= 43 && l.y >= pts[pts.length - 1].y + 0.5) { order.push(p); const sec = (Date.now() - t0) / 1000; toast(`§a${order.length}位 §f${p.name} §7${sec.toFixed(1)}秒`); record(58, p.name, sec, "min"); }
            if (t % 10 === 0) p.onScreenDisplay.setActionBar(`§aアスレチック コース${course} §fゴールまで ${Math.max(0, Math.round(44 - l.z))}m`);
        }
        if (players.every((p) => order.includes(p) || !p.isValid)) break;
        await wait(2);
    }
    return order.slice(0, players.length === 1 ? 1 : Math.min(3, players.length - 1));
}


// ===== ミニゲームを1つ遊ぶ(準備 → 開始 → 勝った人を返す) =====
const PREP = {
    26: () => buildSimon(), 27: () => buildChairs(), 28: () => buildPool(), 29: () => buildFirebar(), 30: () => buildRace(), 32: () => buildFarm(),
    33: () => buildWallRoom(), 34: () => buildWallRoom(), 36: () => buildArena(10, "basalt", "glass", 3), 37: () => buildWalls(), 38: () => buildDash(),
    40: () => buildArena(9, "gray_concrete", "glass", 4), 42: () => buildPose(), 44: () => buildArena(10, "white_concrete", "glass", 3), 45: () => buildArena(11, "smooth_sandstone", "glass", 3),
    46: () => buildArena(8, "pink_concrete", "glass", 3), 47: () => buildArena(10, "grass_block", "barrier", 3), 48: () => buildArena(7, "stone_bricks", "glass", 8),
    50: () => buildArena(9, "smooth_stone", "barrier", 8),
    51: () => { buildArena(12, "smooth_sandstone", "barrier", 3); cmd("fill -2 1 -12 2 4 -3 barrier"); cmd("fill -2 1 -3 -2 4 2 barrier"); cmd("fill 2 1 -3 2 4 2 barrier"); cmd("fill -1 1 -3 1 1 2 barrier"); },
    52: () => buildRing(10, "polished_andesite"), 54: () => buildStraight("white_concrete", false), 55: () => buildStraight("lime_concrete", true),
    56: () => buildArena(12, "coarse_dirt", "barrier", 3), 57: () => buildRing(11, "light_gray_concrete"), 58: () => buildCourse(),
};
const START_AT = { 28: "0 7 0", 29: "0 1 5", 37: "0 1 6", 48: "0 4 0", 54: "0 1 -44", 55: "0 1 -44", 38: "0 1 -44" };
const PLAY = {
    25: gameQuiz, 26: gameSimon, 27: gameChairs, 28: gamePool, 29: gameFirebar, 30: gameRace, 31: gameStop, 32: gameFarm, 33: gameColors, 34: gameReflex,
    36: gameMeteor, 37: gameWalls, 38: gameDash, 40: gameLaser, 42: gamePose, 43: gamePixel, 44: gameEggs, 45: gameCoins, 46: gameBalloon, 47: gameMelon,
    48: gameCeiling, 50: gameBoyon, 51: gameCroc, 52: () => gameBumper("mmgplus:top", 10, "コマぶつけ"), 53: gameFlags, 54: gamePlates,
    55: gameBigball, 56: gameRodeo, 57: () => gameBumper("mmgplus:car", 11, "バンパーカー"), 58: gameCourse,
};
// 持ち物を全部消す(左手・よろいも)。BOT も
function clearItems() {
    cmd("clear @a[tag=playing]");
    for (const s of ["slot.weapon.offhand 0", "slot.armor.head 0", "slot.armor.chest 0", "slot.armor.legs 0", "slot.armor.feet 0"]) cmd(`replaceitem entity @a[tag=playing] ${s} air`);
}
async function playMinigame(id, players) {
    // 準備: 会場を作り、参加者に playing をつけて会場へ
    for (const p of world.getPlayers()) p.removeTag("playing");
    for (const p of players) { p.addTag("playing"); p.removeTag("mpl_board"); p.setGameMode(ADVENTURE); }
    setScore("game", "selectgame", id); setScore("game", "playing", 1);
    cmd("inputpermission set @a movement enabled"); cmd("inputpermission set @a lateral_movement enabled"); cmd("tag @a remove mpl_lock");
    clearItems(); cmd("effect @a[tag=playing] clear");
    clearArena();
    try { (PREP[id] ?? (() => clearArena()))(); } catch (e) { for (const p of world.getPlayers()) if (isAdmin(p)) p.sendMessage(`§7[MPL] ${MINIGAMES[id]} の会場でエラー: ${e}`); }
    cmd(`tp @a[tag=playing] ${START_AT[id] ?? (id === 30 ? `${raceX(RACE_START - 3) + 0.5} 1 ${RACE_START - 3}` : "0 1 0")}`);
    cmd("effect @a[tag=playing] night_vision 600 0 true");
    banner("card", MG_HOWTO[id] ?? "", 80, players, `§l${MINIGAMES[id]}`);
    soundAll("random.levelup", 1.2);
    await wait(80);
    // 開始
    Object.assign(run, { id, active: true });
    let winners = [];
    try { winners = (await PLAY[id]()) ?? []; }
    catch (e) {
        console.warn(`[MPL] minigame ${id}: ${e}`);
        for (const p of world.getPlayers()) if (isAdmin(p)) p.sendMessage(`§7[MPL] ${MINIGAMES[id]} でエラー: ${e} ${String(e?.stack ?? "").split("\n")[1]?.trim() ?? ""}`);
    }
    const skipped = !run.active;
    run.active = false;
    // 後片付け
    cmd("ride @a stop_riding"); cmd("inputpermission set @a movement enabled"); cmd("gamerule pvp false");
    for (const p of playing()) { if (p.getGameMode() === SPECTATOR) p.setGameMode(ADVENTURE); }
    clearItems(); cmd("effect @a[tag=playing] clear"); cmd("tag @a remove mpl_lock");
    clearArena();
    setScore("game", "playing", 0); setScore("game", "selectgame", 0);
    for (const p of world.getPlayers()) p.removeTag("playing");
    return skipped ? [] : winners.filter((p) => p.isValid);
}
// ミニゲームの最初に出す一言の遊び方
const MG_HOWTO = {
    25: "いちばん早く正しい答えを選ぼう", 26: "光った順番に床をふもう", 27: "曲が止まったらイスに座ろう", 28: "水の中の宝を集めよう", 29: "回る火の玉をジャンプでよけよう",
    30: "ボートで一本道をゴールへ", 31: "ぴったりの秒数でストップ", 32: "たねでニワトリを囲いへ", 33: "一番多かった色を答えよう", 34: "緑になったらすぐしゃがむ",
    36: "赤い印から逃げよう", 37: "穴の位置に立って壁をすり抜けよう", 38: "動く壁をよけてゴールへ", 40: "低いのはジャンプ、高いのはしゃがむ", 42: "言われた色の壁を向いてポーズ",
    43: "お手本と同じ絵を床に作ろう", 44: "落ちてくる卵をキャッチ", 45: "コインを拾おう、叩くと相手が落とす", 46: "順番にポンプ、割ったらアウト", 47: "音をたよりにスイカを叩こう",
    48: "穴に隠れて天井をよけよう", 49: "相手の風船を割ろう", 50: "はねるボールをよけよう", 51: "口の中の歯を1本叩こう", 52: "ぶつけて場外へ(右クリックでブースト)",
    53: "赤=しゃがむ、白=右クリックで旗を上げ下げ", 54: "お皿を落とさずゴールへ", 55: "大玉に乗ってゴールへ", 56: "矢印の向きをすぐ見よう", 57: "ぶつけて場外へ(右クリックでブースト)", 58: "足場を跳んでゴールへ",
};
// ミニゲームの ON/OFF
const mgOn = () => MG_IDS.filter((id) => !load("mg_off", []).includes(id));

// ===== アイコン(RP の font/glyph_E1.png、tools/mpl_glyphs.py)=====
const I = { star: "", coin: "", dice: "", crown: "", up: "", down: "", heart: "", bolt: "", bag: "", clock: "" };
const BADGE = (n) => String.fromCharCode(0xe110 + Math.min(7, Math.max(0, n - 1)));

// ===== 音楽(RP の sounds/mpl/*.ogg、tools/mpl_music.py で作ったオリジナル曲)=====
const BGM = { board: ["mpl.bgm_board", 640], minigame: ["mpl.bgm_minigame", 480], finale: ["mpl.bgm_finale", 300] };
let bgmNow = null, bgmTimer = null;
function bgm(kind) {
    if (bgmTimer !== null) { system.clearRun(bgmTimer); bgmTimer = null; }
    if (bgmNow) cmd(`stopsound @a ${bgmNow}`);
    bgmNow = null;
    if (!kind || load("bgm_off", true)) return;
    const [snd, len] = BGM[kind];
    bgmNow = snd;
    const play = () => cmd(`execute as @a at @s run playsound ${snd} @s ~ ~ ~ 0.55 1`);
    play(); bgmTimer = system.runInterval(play, len);
}

// ===== カメラ(演出)=====
const cam = {
    to: (who, pos, look, sec = 1, ease = "in_out_sine") => cmd(`camera ${who} set minecraft:free ease ${sec} ${ease} pos ${pos.x} ${pos.y} ${pos.z} facing ${look.x} ${look.y} ${look.z}`),
    clear: (who = "@a") => cmd(`camera ${who} clear`),
    fade: (who = "@a", inS = 0.3, hold = 0.3, outS = 0.4) => cmd(`camera ${who} fade time ${inS} ${hold} ${outS} color 0 0 0`),
};
// 今の人の少し後ろ・上から見る
function follow(p, sec = 0.6) {
    const l = p.location, dx = l.x - BOARD.x, dz = l.z - BOARD.z, d = Math.hypot(dx, dz) || 1;
    cam.to("@a[tag=mpl_board]", { x: l.x + (dx / d) * 7, y: l.y + 6, z: l.z + (dz / d) * 7 }, { x: l.x, y: l.y + 1, z: l.z }, sec);
}

// ===== ボード =====
// 中心 (0, 0, 130)。外まわりに 3x3 のマスが 33個(4マスおき)。真ん中は広場(ロビー)と城
const BOARD = { x: 0.5, z: 130.5 };
const LOBBY = { x: 0.5, y: 1, z: 124.5 };
const SPACES = (() => {
    const pts = [];
    for (let x = -20; x <= 20; x += 4) pts.push([x, 116]);
    for (let z = 120; z <= 140; z += 4) pts.push([20, z]);
    for (let x = 16; x >= -20; x -= 4) pts.push([x, 144]);
    for (let z = 140; z >= 120; z -= 4) pts.push([-20, z]);
    // マスの種類: 0 = スタート。青(+3)が多め、赤(-3)、?(イベント)、!(ラッキー)、ショップ、ドクロ
    const kinds = ["start", ...Array.from({ length: pts.length - 1 }, (_, i) => (i % 9 === 4 ? "event" : i % 9 === 7 ? "red" : i % 11 === 9 ? "lucky" : i % 6 === 2 ? "event" : i % 7 === 5 ? "red" : "blue"))];
    for (const i of [6, 17, 28]) kinds[i] = "shop";
    kinds[22] = "skull";
    return pts.map(([x, z], i) => ({ x, z, kind: kinds[i] }));
})();
const SPACE_LOOK = {
    start: ["white_concrete", "§f§lSTART"], blue: ["light_blue_concrete", `§9§l+3${I.coin}`], red: ["red_concrete", `§c§l-3${I.coin}`],
    event: ["lime_concrete", "§a§l?"], lucky: ["gold_block", "§6§l!"], shop: ["purple_concrete", `§d§l${I.bag}SHOP`], skull: ["black_concrete", "§8§lドクロ"],
};
function buildBoard() {
    cmd("tickingarea add -34 -8 98 34 40 162 mpl_board true");
    // 土台: 島(石の崖 + 草 + 外側に水のふち)
    cmd("fill -30 -6 104 30 -2 156 stone"); cmd("fill -30 -1 104 30 -1 156 dirt"); cmd("fill -30 0 104 30 0 156 grass_block");
    cmd("fill -31 -1 103 31 -1 103 water"); cmd("fill -31 -1 157 31 -1 157 water"); cmd("fill -31 -1 103 -31 -1 157 water"); cmd("fill 31 -1 103 31 -1 157 water");
    cmd("fill -31 -2 103 31 -2 157 prismarine");
    cmd("fill -30 1 104 30 30 156 air");
    // 道: マスとマスの間は石のレンガ、ふちは石のハーフ
    for (let i = 0; i < SPACES.length; i++) {
        const a = SPACES[i], b = SPACES[(i + 1) % SPACES.length];
        cmd(`fill ${Math.min(a.x, b.x)} 0 ${Math.min(a.z, b.z)} ${Math.max(a.x, b.x)} 0 ${Math.max(a.z, b.z)} polished_andesite`);
    }
    // マス: 3x3。まわり 5x5 を白いふち、真ん中は光る
    for (const s of SPACES) {
        cmd(`fill ${s.x - 2} 0 ${s.z - 2} ${s.x + 2} 0 ${s.z + 2} smooth_quartz`);
        cmd(`fill ${s.x - 1} 0 ${s.z - 1} ${s.x + 1} 0 ${s.z + 1} ${SPACE_LOOK[s.kind][0]}`);
        cmd(`setblock ${s.x} 0 ${s.z} ${s.kind === "skull" ? "crying_obsidian" : "sea_lantern"}`);
    }
    // 角のアーチ(4つ)と、道ぞいの街灯
    for (const [x, z] of [[-20, 116], [20, 116], [20, 144], [-20, 144]]) {
        cmd(`fill ${x - 3} 1 ${z - 3} ${x - 3} 6 ${z - 3} quartz_pillar`); cmd(`fill ${x + 3} 1 ${z + 3} ${x + 3} 6 ${z + 3} quartz_pillar`);
        cmd(`fill ${x - 3} 7 ${z - 3} ${x + 3} 7 ${z + 3} smooth_quartz_slab`); cmd(`setblock ${x} 8 ${z} beacon`);
    }
    SPACES.forEach((s, i) => { if (i % 2 === 1) { const ox = s.z === 116 ? 0 : s.z === 144 ? 0 : s.x > 0 ? 3 : -3, oz = s.z === 116 ? -3 : s.z === 144 ? 3 : 0; cmd(`fill ${s.x + ox} 1 ${s.z + oz} ${s.x + ox} 3 ${s.z + oz} dark_oak_fence`); cmd(`setblock ${s.x + ox} 4 ${s.z + oz} lantern`); } });
    // 真ん中: 広場と城
    cmd("fill -14 0 121 14 0 139 smooth_quartz"); cmd("fill -13 0 122 13 0 138 polished_diorite"); cmd("fill -1 0 121 1 0 139 gold_block");
    cmd("fill -6 1 130 6 1 138 quartz_bricks"); cmd("fill -5 2 131 5 8 137 quartz_bricks"); cmd("fill -4 2 132 4 7 136 air");
    cmd("fill -1 2 130 1 4 131 air"); cmd("fill -5 9 131 5 9 137 purple_concrete"); cmd("fill -4 10 132 4 10 136 purple_concrete"); cmd("fill -2 11 133 2 11 135 purple_concrete"); cmd("setblock 0 12 134 gold_block");
    for (const [x, z] of [[-6, 130], [6, 130], [-6, 138], [6, 138]]) { cmd(`fill ${x} 1 ${z} ${x} 11 ${z} quartz_pillar`); cmd(`setblock ${x} 12 ${z} sea_lantern`); cmd(`fill ${x} 13 ${z} ${x} 14 ${z} purple_stained_glass`); }
    for (const x of [-4, -2, 2, 4]) cmd(`setblock ${x} 6 130 ${["red", "yellow", "lime", "light_blue"][(x + 4) / 2 | 0]}_wool`);
    // 噴水(水は石の器の中だけ)
    cmd("fill -4 1 123 4 1 127 stone_bricks"); cmd("fill -3 1 124 3 1 126 water"); cmd("fill 0 1 125 0 3 125 prismarine_wall"); cmd("setblock 0 4 125 sea_lantern");
    // 木と花
    for (const [x, z] of [[-26, 110], [26, 110], [-26, 150], [26, 150], [-10, 112], [10, 148], [-26, 130], [26, 130]]) cmd(`place feature minecraft:fancy_oak_tree_feature ${x} 1 ${z}`);
    for (let i = 0; i < 90; i++) { const x = rand(-29, 29), z = rand(105, 155); if (Math.abs(x) < 24 && z > 112 && z < 148) continue; cmd(`setblock ${x} 1 ${z} ${["poppy", "dandelion", "cornflower", "oxeye_daisy", "allium", "pink_tulip"][rand(0, 5)]} keep`); }
    // マスの上の文字
    cmd("kill @e[type=mmgplus:board,tag=mpl_label]");
    for (let i = 0; i < SPACES.length; i++) if (SPACES[i].kind === "shop") buildStall(i);
    save("board_built", 7);
}

// ===== すごろく =====
const G = { on: false, turn: 0, turns: 10, players: [], star: 0, stars: {}, coins: {}, pos: {}, items: {}, mgWins: {}, coinsGot: {}, now: null };
const spaceAt = (i) => SPACES[((i % SPACES.length) + SPACES.length) % SPACES.length];
const spot = (i, k = 0) => { const s = spaceAt(i); return { x: s.x + 0.5 + [0, 0.8, -0.8, 0.8, -0.8, 0][k % 6], y: 1.05, z: s.z + 0.5 + [0, 0.8, 0.8, -0.8, -0.8, 0][k % 6] }; };
const gp = () => G.players.map((n) => world.getPlayers({ name: n })[0]).filter(Boolean);
const lookCenter = { facingLocation: { x: BOARD.x, y: 1, z: BOARD.z } };
function addCoins(name, d) { G.coins[name] = Math.max(0, (G.coins[name] ?? 0) + d); if (d > 0) G.coinsGot[name] = (G.coinsGot[name] ?? 0) + d; hud(); }
const rankRows = () => G.players.map((n) => [n, G.stars[n] ?? 0, G.coins[n] ?? 0]).sort((a, b) => b[1] - a[1] || b[2] - a[2]);
function rankOfName(n) { const rows = rankRows(), i = rows.findIndex((r) => r[0] === n); return rows.findIndex((r) => r[1] === rows[i][1] && r[2] === rows[i][2]) + 1; }
function hud() {
    // 右の表: 順位のバッジ・名前・★・コイン。今の番の人は ▶。見出しはターン
    try { world.scoreboard.removeObjective("mpl_hud"); } catch {}
    const o = world.scoreboard.addObjective("mpl_hud", `§e§l${I.crown} TURN ${Math.max(1, G.turn)}/${G.turns}`);
    const rows = rankRows();
    rows.forEach(([n, st, co]) => o.setScore(boldText(`${G.now === n ? "§e▶" : " "}${BADGE(rankOfName(n))} §f${n.slice(0, 10)}  §e${I.star}${st} §6${I.coin}${co}`), st * 1000 + co));
    cmd("scoreboard objectives setdisplay sidebar mpl_hud descending");
}
let starEntity;
function placeStar(exclude = -1) {
    let i; do { i = rand(4, SPACES.length - 1); } while (i === exclude || ["start", "shop", "skull"].includes(SPACES[i].kind));
    G.star = i;
    try { starEntity?.remove(); } catch {}
    const s = spaceAt(i);
    starEntity = spawnAt("mmgplus:star", { x: s.x + 0.5, y: 2.6, z: s.z + 0.5 });
    return s;
}
async function showStar(text) {
    const s = spaceAt(G.star);
    cam.to("@a[tag=mpl_board]", { x: s.x + 6, y: 6, z: s.z + 6 }, { x: s.x + 0.5, y: 2.5, z: s.z + 0.5 }, 1.2);
    banner("starappear", `${text}  ${I.coin}${STAR_PRICE}で買える`, 60); soundAllPlayers("random.levelup", 1.4);
    for (let k = 0; k < 6; k++) { cmd(`particle minecraft:totem_particle ${s.x + 0.5} 3 ${s.z + 0.5}`); await wait(10); }
}
const STAR_PRICE = 20;
const ITEMS = {
    double: { name: "ダブルサイコロ", price: 10, desc: "サイコロを2つふれる" },
    triple: { name: "トリプルサイコロ", price: 18, desc: "サイコロを3つふれる" },
    pipe: { name: "ワープパイプ", price: 12, desc: "だれかと場所をこうかん" },
    gold: { name: "金のパイプ", price: 28, desc: "スターの手前までワープ" },
    glove: { name: "どろぼう手袋", price: 14, desc: "だれかからコインを5〜10枚うばう" },
};
// ===== 演出(RP の ui/hud_screen.json、tools/mpl_ui.py)=====
// タイトルの頭に見えない印 + キー番号を入れると、ふつうの文字の代わりに専用ロゴ / 帯 / カードが出る
const BMARK = "§r§b§r§n§r";
const BKEYS = ["title", "turn", "yourturn", "order", "starappear", "star", "minigame", "win", "happening", "skull", "shop", "lucky", "gameset", "result", "champion", "lastspurt", "bonus", "item",
    ...Array.from({ length: 31 }, (_, n) => `n${n}`), "r_gold", "r_blue", "r_red", "r_purple", "r_green", "r_gray", "card"];
const bcode = (key) => { const i = Math.max(0, BKEYS.indexOf(key)); return `${BMARK}§${(i >> 4).toString(16)}§${(i & 15).toString(16)}§r`; };
// 一度消してから出す(ロゴの登場アニメを毎回最初から)
function banner(key, sub = "", stay = 40, players = world.getPlayers(), text = "") {
    for (const p of players) { try { p.onScreenDisplay.clearTitle(); } catch {} }
    system.runTimeout(() => { for (const p of players) { try { if (p.isValid) p.onScreenDisplay.setTitle(bcode(key) + text, { subtitle: sub, fadeInDuration: 0, stayDuration: stay, fadeOutDuration: 8 }); } catch {} } }, 1);
}
const ribbon = (color, text, sub = "", stay = 40, players = world.getPlayers()) => banner(`r_${color}`, sub, stay, players, text);
const subAll = (t) => world.getPlayers().forEach((p) => { try { p.onScreenDisplay.updateSubtitle(t); } catch {} });
const FORM_MARK = "§r§p§r§q§r";
const titleAll = (t, s = "", stay = 40) => world.getPlayers().forEach((p) => p.onScreenDisplay.setTitle(t, { subtitle: s, fadeInDuration: 5, stayDuration: stay, fadeOutDuration: 10 }));
const soundAllPlayers = (s, pitch = 1) => cmd(`execute as @a at @s run playsound ${s} @s ~ ~ ~ 1 ${pitch}`);
const lockBoard = () => { cmd("inputpermission set @a[tag=mpl_board] lateral_movement disabled"); cmd("tag @a[tag=mpl_board] add mpl_lock"); };
const unlockAll = () => { cmd("inputpermission set @a lateral_movement enabled"); cmd("inputpermission set @a movement enabled"); cmd("tag @a remove mpl_lock"); };

async function startParty(turns, players) {
    if (G.on) return;
    Object.assign(G, { on: true, turn: 0, turns, players: players.map((p) => p.name).sort(() => Math.random() - 0.5), stars: {}, coins: {}, pos: {}, items: {}, mgWins: {}, coinsGot: {}, now: null });
    for (const n of G.players) { G.coins[n] = 10; G.stars[n] = 0; G.pos[n] = 0; G.items[n] = []; }
    if ((load("board_built", 0)) < 7) buildBoard();
    for (const p of gp()) { p.addTag("mpl_board"); p.teleport(spot(0, G.players.indexOf(p.name)), lookCenter); p.setGameMode(ADVENTURE); }
    lockBoard(); hud();
    try {
        // オープニング: 島のまわりをカメラが回る
        bgm("board");
        cam.fade();
        await wait(8);
        cam.to("@a[tag=mpl_board]", { x: -40, y: 30, z: 95 }, { x: 0, y: 2, z: 130 }, 0.1);
        banner("title", `${turns}ターン勝負！ スターを一番多く集めよう`, 90);
        soundAllPlayers("random.totem", 1);
        cam.to("@a[tag=mpl_board]", { x: 40, y: 22, z: 95 }, { x: 0, y: 2, z: 130 }, 3);
        await wait(60);
        cam.to("@a[tag=mpl_board]", { x: 40, y: 18, z: 165 }, { x: 0, y: 2, z: 130 }, 3);
        await wait(60);
        cam.to("@a[tag=mpl_board]", { x: 0.5, y: 14, z: 100 }, { x: 0.5, y: 4, z: 128 }, 2);
        await wait(40);
        banner("order", G.players.map((n, i) => `${BADGE(i + 1)}${n}`).join("  "), 60);
        await wait(70);
        placeStar(); await showStar("スターがあらわれた！"); await wait(20);
        for (G.turn = 1; G.turn <= G.turns && G.on; G.turn++) {
            const last = G.turn > G.turns - 3;
            hud();
            cam.to("@a[tag=mpl_board]", { x: 0.5, y: 34, z: 131 }, { x: 0.5, y: 0, z: 130 }, 1.2);
            banner(last ? "lastspurt" : "turn", last ? `TURN ${G.turn} / ${G.turns}  青と赤のマスが2倍` : `${G.turn} / ${G.turns}`, 50);
            soundAllPlayers(last ? "mob.wither.spawn" : "random.levelup", last ? 1.6 : 0.9);
            await wait(55);
            for (let k = 0; k < G.players.length && G.on; k++) {
                const n = G.players[k], p = world.getPlayers({ name: n })[0];
                if (p) await takeTurn(p, last, G.players[(k + 1) % G.players.length]);
            }
            G.now = null; hud();
            if (!G.on) break;
            await minigameRound();
        }
        if (G.on) await finale();
    } finally {
        G.on = false; G.now = null;
        bgm(null); unlockAll(); cam.clear();
        for (const p of world.getPlayers()) { p.removeTag("mpl_board"); }
        try { starEntity?.remove(); } catch {}
        cmd("kill @e[type=mmgplus:dice]");
        cmd("kill @e[type=villager_v2,tag=mpl_shopkeeper]"); for (const k of Object.keys(ITEMS)) cmd(`kill @e[type=mpl:item_${k}]`);
        try { world.scoreboard.removeObjective("mpl_hud"); } catch {}
        for (const p of world.getPlayers()) p.teleport(LOBBY);
    }
}

// 1人ぶんのターン: アイテム → サイコロ(ジャンプして頭で叩く)→ 1マスずつ進む(スター・ショップを通ると止まる)→ マスの効果
let lastY = new Map();
async function takeTurn(p, last, nextName) {
    const name = p.name;
    G.now = name; hud();
    p.teleport(spot(G.pos[name]), lookCenter);
    follow(p, 1);
    banner("yourturn", `つぎ: ${nextName}`, 40, [p]); ribbon("gold", `${name} の番`, `つぎ: ${nextName}`, 40, world.getPlayers().filter((q) => q.name !== name));
    cmd(`playsound note.pling @a ${p.location.x} ${p.location.y} ${p.location.z} 1 1.8`);
    await wait(30);
    // アイテム
    let dice = 1;
    const used = await useItem(p);
    if (!G.on) return;
    if (used === "double") dice = 2; else if (used === "triple") dice = 3;
    if (used === "pipe" || used === "gold" || used === "glove") { await wait(20); }
    // サイコロ
    let total = 0;
    for (let d = 0; d < dice && G.on; d++) {
        const base = p.location;
        const die = spawnAt("mmgplus:dice", { x: base.x, y: base.y + 2.55, z: base.z });
        die?.setProperty("mmgplus:rolling", 1);
        if (!isBot(p)) p.onScreenDisplay.setActionBar(`${I.dice} §eジャンプして頭でサイコロを叩こう！`);
        let hit = false;
        for (let t = 0; t < 240 && G.on; t += 1) {
            const l = p.location;
            if (l.y - base.y > 0.45 && Math.hypot(l.x - base.x, l.z - base.z) < 0.9) hit = true; // ジャンプで頭が届いた
            if (isBot(p) && t === 30) cmd(`scriptevent mmgbot:jump ${name}`);
            if (hit || t >= 239) break;
            if (t % 3 === 0) cmd(`playsound random.click @a ${base.x} ${base.y} ${base.z} 0.35 ${(1 + Math.random()).toFixed(2)}`);
            await wait(1);
        }
        const roll = rand(1, 6);
        total += roll;
        try { die?.setProperty("mmgplus:rolling", 0); } catch {}
        cmd(`particle minecraft:totem_particle ${base.x} ${base.y + 2.6} ${base.z}`);
        cmd(`playsound random.anvil_land @a ${base.x} ${base.y} ${base.z} 0.5 2`); cmd(`playsound random.levelup @a ${base.x} ${base.y} ${base.z} 1 1.6`);
        banner(`n${Math.min(30, roll)}`, dice > 1 ? `合計 ${total}` : name, 22);
        await wait(25);
        try { die?.remove(); } catch {}
    }
    // 1マスずつ進む
    for (let k = total; k >= 1 && G.on; k--) {
        G.pos[name] = (G.pos[name] + 1) % SPACES.length;
        const s = spot(G.pos[name]);
        p.teleport({ x: s.x, y: s.y + 0.7, z: s.z }, lookCenter);
        actionbar(`${I.dice} のこり §e§l${k - 1}`, world.getPlayers());
        cmd(`playsound note.pling @a ${s.x} ${s.y} ${s.z} 0.9 ${(0.8 + (total - k) * 0.08).toFixed(2)}`);
        follow(p, 0.35);
        await wait(4);
        p.teleport(s, lookCenter);
        await wait(4);
        if (G.pos[name] === G.star) await buyStar(p);
        if (G.pos[name] === 0) { addCoins(name, 5); ribbon("gold", `PASSED START +5${I.coin}`, name, 25); }
    }
    // 止まったマス
    const sp = spaceAt(G.pos[name]), mul = last ? 2 : 1;
    if (sp.kind === "blue") { addCoins(name, 3 * mul); ribbon("blue", `+${3 * mul} ${I.coin}`, name, 25); soundAllPlayers("random.orb", 1.4); cmd(`particle minecraft:villager_happy ${p.location.x} ${p.location.y + 1} ${p.location.z}`); }
    else if (sp.kind === "red") { addCoins(name, -3 * mul); ribbon("red", `-${3 * mul} ${I.coin}`, name, 25); soundAllPlayers("note.bass", 0.7); cmd(`particle minecraft:villager_angry ${p.location.x} ${p.location.y + 1} ${p.location.z}`); }
    else if (sp.kind === "lucky") { const n = rand(5, 15); addCoins(name, n); banner("lucky", `+${n} ${I.coin}  ${name}`, 35); soundAllPlayers("random.levelup", 1.2); }
    else if (sp.kind === "event") await happening(p);
    else if (sp.kind === "shop") await shop(p);
    else if (sp.kind === "skull") await skull(p);
    await wait(25);
}
// アイテムを使う(サイコロの前)。持っていなければ何もしない
async function useItem(p) {
    const name = p.name, bag = G.items[name] ?? [];
    if (!bag.length) return null;
    let pick = null;
    if (isBot(p)) { if (Math.random() < 0.6) pick = bag[0]; }
    else {
        const f = new ActionFormData().title(`${FORM_MARK}§lアイテム`).body("§lサイコロの前にアイテムを使う？");
        bag.forEach((k) => f.button(`§l${ITEMS[k].name}\n§7${ITEMS[k].desc}`));
        f.button("§l§7使わない");
        const r = await Promise.race([f.show(p).catch(() => ({ canceled: true })), wait(240).then(() => ({ canceled: true }))]);
        try { uiManager.closeAllForms(p); } catch {}
        if (!r.canceled && r.selection < bag.length) pick = bag[r.selection];
    }
    if (!pick) return null;
    bag.splice(bag.indexOf(pick), 1);
    banner("item", `${ITEMS[pick].name}  ${name}`, 35); soundAllPlayers("random.orb", 0.8);
    const others = G.players.filter((n) => n !== name);
    if (pick === "pipe" && others.length) { const t = others[rand(0, others.length - 1)]; [G.pos[name], G.pos[t]] = [G.pos[t], G.pos[name]]; for (const n of [name, t]) world.getPlayers({ name: n })[0]?.teleport(spot(G.pos[n]), lookCenter); ribbon("purple", `${name} と ${t} が場所をこうかん！`, "", 40); }
    if (pick === "gold") { G.pos[name] = (G.star - 1 + SPACES.length) % SPACES.length; p.teleport(spot(G.pos[name]), lookCenter); follow(p, 0.8); }
    if (pick === "glove" && others.length) { const t = others.sort((a, b) => (G.coins[b] ?? 0) - (G.coins[a] ?? 0))[0], n = Math.min(rand(5, 10), G.coins[t] ?? 0); addCoins(t, -n); addCoins(name, n); ribbon("purple", `${t} から ${n}${I.coin} うばった！`, name, 40); }
    return pick;
}
// ===== 屋台のショップ =====
// ショップのマスの外側に屋台。手前のカウンターに商品が3つ浮かぶ。止まるとガレージ(シャッター)が下から上へ開いて村人が出てくる。
// 3つから好きなものを1つ買える。買うか立ち去るとシャッターが閉まる
function stallFrame(i) {
    const s = spaceAt(i);
    const n = s.z === 116 ? [0, -1] : s.z === 144 ? [0, 1] : s.x === 20 ? [1, 0] : [-1, 0]; // 外向き
    const t = [-n[1], n[0]];                                                                  // 横向き
    const at = (a, b, y = 1) => ({ x: s.x + n[0] * a + t[0] * b, y, z: s.z + n[1] * a + t[1] * b });
    return { s, n, t, at };
}
const fillRel = (f, a1, b1, y1, a2, b2, y2, block) => { const p = f.at(a1, b1, y1), q = f.at(a2, b2, y2); cmd(`fill ${p.x} ${p.y} ${p.z} ${q.x} ${q.y} ${q.z} ${block}`); };
function buildStall(i) {
    const f = stallFrame(i);
    fillRel(f, 3, -3, 0, 7, 3, 0, "spruce_planks");                 // 床
    fillRel(f, 3, -3, 1, 7, 3, 5, "air");
    fillRel(f, 3, -3, 1, 7, -3, 4, "stripped_spruce_log"); fillRel(f, 3, 3, 1, 7, 3, 4, "stripped_spruce_log"); // 横の壁
    fillRel(f, 7, -3, 1, 7, 3, 4, "spruce_planks");                  // 奥の壁
    fillRel(f, 3, -2, 1, 3, 2, 1, "stripped_oak_wood");             // 手前のカウンター
    fillRel(f, 2, -3, 5, 7, 3, 5, "red_wool"); for (let b = -3; b <= 3; b += 2) fillRel(f, 2, b, 5, 7, b, 5, "white_wool"); // しましまの屋根
    fillRel(f, 2, -3, 4, 2, 3, 4, "red_wool");
    fillRel(f, 6, -2, 1, 6, 2, 3, "barrel");                         // 奥のたな
    const lamp = f.at(4, 0, 4); cmd(`setblock ${lamp.x} ${lamp.y} ${lamp.z} lantern`);
    stallShutter(i, true);
    
}
// シャッター: カウンターの上(高さ 2〜4)。開ける時は下の段から消える
async function stallShutter(i, close, animate = false) {
    const f = stallFrame(i);
    const rows = close ? [4, 3, 2] : [2, 3, 4];
    for (const y of rows) { fillRel(f, 3, -2, y, 3, 2, y, close ? "white_concrete" : "air"); if (animate) { const p = f.at(3, 0, y); cmd(`playsound block.barrel.${close ? "close" : "open"} @a ${p.x} ${p.y} ${p.z} 1 0.8`); await wait(5); } }
}
async function shop(p) {
    const name = p.name, bag = G.items[name] ?? (G.items[name] = []);
    const i = G.pos[name], f = stallFrame(i);
    // カメラ: マスの少し手前から屋台を見る
    const eye = f.at(-1.5, 0, 3.2), look = f.at(4, 0, 2.2);
    cam.to("@a[tag=mpl_board]", { x: eye.x + 0.5, y: eye.y, z: eye.z + 0.5 }, { x: look.x + 0.5, y: look.y, z: look.z + 0.5 }, 0.8);
    await wait(16);
    await stallShutter(i, false, true);
    const vpos = f.at(4.5, 0, 1); const v = spawnAt("minecraft:villager_v2", { x: vpos.x + 0.5, y: 1, z: vpos.z + 0.5 });
    try { v?.addEffect("slowness", 600, { amplifier: 255, showParticles: false }); v?.setRotation({ x: 0, y: Math.atan2(f.n[0], -f.n[1]) * 180 / Math.PI }); v?.addTag("mpl_shopkeeper"); } catch {}
    cmd(`playsound mob.villager.haggle @a ${vpos.x} 1 ${vpos.z} 1 1`);
    // 今日の3品(5つからランダム)を、カウンターの上に
    const keys = Object.keys(ITEMS).sort(() => Math.random() - 0.5).slice(0, 3);
    const shown = keys.map((k, j) => { const q = f.at(3, j - 1, 2.15); return spawnAt(`mpl:item_${k}`, { x: q.x + 0.5, y: q.y, z: q.z + 0.5 }); });
    banner("shop", name, 40);
    await wait(15);
    let buy = null;
    if (bag.length >= 3) ribbon("gray", "アイテムはもう3つ持っている", "3つまで", 30, [p]);
    else if (isBot(p)) { const ok = keys.filter((k) => ITEMS[k].price <= (G.coins[name] ?? 0) - 5); if (ok.length && Math.random() < 0.7) buy = ok[rand(0, ok.length - 1)]; await wait(30); }
    else {
        const fm = new ActionFormData().title(`${FORM_MARK}§lショップ`).body(`§l§fいらっしゃい！ どれにする？ §6${I.coin}${G.coins[name] ?? 0}§f 持っている`);
        keys.forEach((k) => fm.button(`§l${ITEMS[k].name}  §6${I.coin}${ITEMS[k].price}\n§7${ITEMS[k].desc}`));
        fm.button("§l§7立ち去る");
        const r = await Promise.race([fm.show(p).catch(() => ({ canceled: true })), wait(300).then(() => ({ canceled: true }))]);
        try { uiManager.closeAllForms(p); } catch {}
        if (!r.canceled && r.selection < keys.length) buy = keys[r.selection];
    }
    if (buy && (G.coins[name] ?? 0) < ITEMS[buy].price) { ribbon("gray", "NOT ENOUGH COINS", name, 25); buy = null; await wait(20); }
    if (buy) {
        addCoins(name, -ITEMS[buy].price); bag.push(buy);
        const j = keys.indexOf(buy); try { shown[j]?.remove(); } catch {}
        cmd(`playsound mob.villager.yes @a ${vpos.x} 1 ${vpos.z} 1 1`); cmd(`playsound random.orb @a ${vpos.x} 1 ${vpos.z} 1 1.4`);
        ribbon("purple", `${ITEMS[buy].name} を買った！`, "まいど！", 30);
    } else { cmd(`playsound mob.villager.no @a ${vpos.x} 1 ${vpos.z} 1 1`); ribbon("gray", "SEE YOU AGAIN!", name, 25); }
    await wait(25);
    try { v?.remove(); } catch {}
    shown.forEach((e) => { try { e?.remove(); } catch {} });
    await stallShutter(i, true, true);
    follow(p, 0.6);
    await wait(10);
}

// スターを買う。ファンファーレ(8秒)に合わせて、カメラがまわりをぐるっと1周 → 正面でアップ
async function buyStar(p) {
    const name = p.name;
    const s = spaceAt(G.star);
    cam.to("@a[tag=mpl_board]", { x: s.x + 4, y: 4, z: s.z + 4 }, { x: s.x + 0.5, y: 2, z: s.z + 0.5 }, 0.8);
    if ((G.coins[name] ?? 0) < STAR_PRICE) { ribbon("gray", `NOT ENOUGH COINS`, `${name}: スターは ${I.coin}${STAR_PRICE}`, 30); await wait(30); return; }
    let yes = isBot(p) ? Math.random() < 0.92 : false;
    if (!isBot(p)) {
        const r = await Promise.race([new ActionFormData().title(`${FORM_MARK}§lスター`).body(`§lコイン ${STAR_PRICE}枚でスターを買う？\n§7(今 ${I.coin}${G.coins[name]})`).button(`§l${I.star} 買う！`).button("§lやめる").show(p).then((r) => ({ selection: r.canceled ? 0 : r.selection === 0 ? 1 : 0 })).catch(() => ({ selection: 0 })), wait(200).then(() => ({ selection: 0 }))]);
        try { uiManager.closeAllForms(p); } catch {}
        yes = r.selection === 1;
    }
    if (!yes) return;
    addCoins(name, -STAR_PRICE); G.stars[name] = (G.stars[name] ?? 0) + 1; hud();
    const keep = bgmNow; bgm(null);
    cmd("execute as @a at @s run playsound mpl.star_get @s ~ ~ ~ 1 1");
    try { starEntity?.remove(); } catch {}
    const c = p.location;
    // 0〜6秒: まわりを1周(1秒ごとに60度)。6秒: 正面に寄ってアップ。7秒: 花火
    for (let k = 0; k <= 6; k++) {
        const a = (k / 6) * Math.PI * 2 + Math.PI / 2;
        cam.to("@a[tag=mpl_board]", { x: c.x + Math.cos(a) * 4.5, y: c.y + 2.2 + (k % 2) * 0.6, z: c.z + Math.sin(a) * 4.5 }, { x: c.x, y: c.y + 1.4, z: c.z }, 1, "linear");
        if (k === 1) banner("star", name, 100);
        if (k % 2 === 0) cmd(`particle minecraft:totem_particle ${c.x} ${c.y + 1} ${c.z}`);
        await wait(20);
    }
    cam.to("@a[tag=mpl_board]", { x: c.x, y: c.y + 1.7, z: c.z + 2.2 }, { x: c.x, y: c.y + 1.5, z: c.z }, 0.8, "out_back");
    for (let k = 0; k < 4; k++) spawnAt("minecraft:fireworks_rocket", { x: c.x + rand(-3, 3), y: c.y + 1, z: c.z + rand(-3, 3) });
    await wait(30);
    if (keep) bgm("board");
    placeStar(G.star);
    await showStar("スターがべつの場所へ！");
    follow(p, 0.8); await wait(20);
}

// ? マスのできごと
async function happening(p) {
    const name = p.name, others = G.players.filter((n) => n !== name);
    banner("happening", "", 25); soundAllPlayers("random.orb", 0.6);
    for (let i = 0; i < 8; i++) { cmd(`particle minecraft:villager_happy ${p.location.x} ${p.location.y + 1.5} ${p.location.z}`); await wait(3); }
    const ev = rand(1, 7);
    if (ev === 1) { const n = rand(5, 12); addCoins(name, n); ribbon("green", `COIN SHOWER! +${n}${I.coin}`, `${name}`, 30); }
    else if (ev === 2 && others.length) { const t = others[rand(0, others.length - 1)], n = Math.min(5, G.coins[t] ?? 0); addCoins(t, -n); addCoins(name, n); ribbon("purple", `COIN THIEF!`, `${name} が ${t} から ${n}${I.coin}`, 40); }
    else if (ev === 3) { G.pos[name] = (G.star - 1 + SPACES.length) % SPACES.length; cam.fade(); await wait(8); p.teleport(spot(G.pos[name]), lookCenter); follow(p, 0.6); ribbon("blue", `WARP!`, `${name} がスターの手前へ`, 40); }
    else if (ev === 4 && others.length) { const t = others[rand(0, others.length - 1)]; [G.pos[name], G.pos[t]] = [G.pos[t], G.pos[name]]; cam.fade(); await wait(8); for (const n of [name, t]) world.getPlayers({ name: n })[0]?.teleport(spot(G.pos[n]), lookCenter); ribbon("gold", `SWAP!`, `${name} ⇔ ${t}`, 40); }
    else if (ev === 5) { const n = Math.min(8, G.coins[name] ?? 0); addCoins(name, -n); ribbon("red", `DROPPED COINS -${n}${I.coin}`, `${name}`, 30); }
    else if (ev === 6) { const k = Object.keys(ITEMS)[rand(0, 4)]; if ((G.items[name] ?? []).length < 3) { G.items[name].push(k); ribbon("purple", `A GIFT!`, `${name} に ${ITEMS[k].name}`, 40); } }
    else { const total = G.players.reduce((s, n) => s + (G.coins[n] ?? 0), 0), each = Math.floor(total / G.players.length); for (const n of G.players) G.coins[n] = each; hud(); ribbon("gold", `EVERYONE EQUAL!`, `コインを全員 ${each}${I.coin} に`, 40); }
    soundAllPlayers("mob.villager.yes", 1.2);
    await wait(50);
}
// ドクロのマス: コイン半分 か スターを1つ取られる(まれ)
async function skull(p) {
    const name = p.name;
    cmd(`camera @a fade time 0.2 0.6 0.4 color 80 0 0`); soundAllPlayers("mob.wither.ambient", 0.8);
    await wait(20);
    if ((G.stars[name] ?? 0) > 0 && Math.random() < 0.25) { G.stars[name]--; hud(); banner("skull", `${I.star} を1つ失った…  ${name}`, 50); }
    else { const n = Math.floor((G.coins[name] ?? 0) / 2); addCoins(name, -n); banner("skull", `コインが半分… -${n}${I.coin}  ${name}`, 50); }
    await wait(50);
}
// ターンの最後のミニゲーム(ルーレットで決める)
async function minigameRound() {
    const list = mgOn(); if (!list.length) return;
    cam.to("@a[tag=mpl_board]", { x: 0.5, y: 8, z: 118 }, { x: 0.5, y: 8, z: 134 }, 1);
    let id = list[0];
    banner("minigame", "", 150); await wait(4);
    for (let i = 0; i < 22; i++) { id = list[rand(0, list.length - 1)]; subAll(`§f${MINIGAMES[id]}`); soundAllPlayers("random.click", 1 + i * 0.03); await wait(2 + Math.floor(i / 4)); }
    subAll(`§e§l${MINIGAMES[id]}`); soundAllPlayers("random.levelup", 1);
    await wait(40);
    cam.fade(); await wait(8);
    cam.clear(); unlockAll();
    bgm("minigame");
    const players = gp();
    const winners = await playMinigame(id, players);
    bgm("board");
    const names = winners.map((w) => w.name);
    for (const n of names) { addCoins(n, 10); G.mgWins[n] = (G.mgWins[n] ?? 0) + 1; }
    // ボードに戻る
    cam.fade(); await wait(8);
    for (const p of gp()) { p.addTag("mpl_board"); p.teleport(spot(G.pos[p.name], G.players.indexOf(p.name)), lookCenter); }
    lockBoard();
    cam.to("@a[tag=mpl_board]", { x: 0.5, y: 30, z: 106 }, { x: 0.5, y: 0, z: 130 }, 1);
    if (names.length) banner("win", `+10${I.coin}  ${names.join(", ")}`, 50); else ribbon("gray", "NO WINNER", "", 45);
    await wait(30);
    showStandings(`TURN ${G.turn} RESULTS`);
    await wait(150);
}
// 順位の画面(RP の ui/server_form.json)
const RANK_MARK = "§r§m§r§n§r";
let prevOrder = {};
function showStandings(head) {
    const rows = rankRows();
    for (const p of world.getPlayers()) {
        if (isBot(p)) continue;
        const f = new ActionFormData().title(`${RANK_MARK}§l${head}`).body(`§7TURN ${G.turn} / ${G.turns}`);
        rows.forEach(([n, st, co]) => {
            const rank = rankOfName(n), before = prevOrder[n];
            const tier = ["gold", "silver", "bronze"][rank - 1] ?? "normal";
            const kind = before === undefined || before === rank ? "same" : before > rank ? "up" : "down";
            f.button(`${BADGE(rank)} ${n === p.name ? "§e" : "§f"}${n}`, `textures/ui/mmgplus_rank/${tier}_${kind}${n === p.name ? "_me" : ""}`);
            f.button(`§e${I.star}${st}  §6${I.coin}${co}`);
        });
        f.show(p).catch(() => {});
    }
    system.runTimeout(() => world.getPlayers().forEach((p) => { try { uiManager.closeAllForms(p); } catch {} }), 140);
    prevOrder = Object.fromEntries(rows.map(([n]) => [n, rankOfName(n)]));
}
// 最後: ボーナススター → 結果発表(ドラムロール 8.8秒に合わせて全員の前をカメラが流れ、鳴り終わりで優勝者にズーム)→ 順位の画面
async function finale() {
    bgm(null);
    banner("gameset", "ボーナススターの発表", 60);
    cam.to("@a[tag=mpl_board]", { x: 0.5, y: 6, z: 116 }, { x: 0.5, y: 5, z: 134 }, 1.5);
    await wait(70);
    banner("bonus", "", 45); soundAllPlayers("random.levelup", 1.2); await wait(50);
    for (const [label, m] of [["MINIGAME STAR", G.mgWins], ["COIN STAR", G.coinsGot]]) {
        const best = Math.max(0, ...G.players.map((n) => m[n] ?? 0)); if (!best) continue;
        const win = G.players.filter((n) => (m[n] ?? 0) === best);
        for (const n of win) G.stars[n] = (G.stars[n] ?? 0) + 1;
        hud(); ribbon("gold", `${I.crown} ${label}`, `${win.join(", ")} に ${I.star}+1`, 60); soundAllPlayers("random.totem", 1.4);
        await wait(80);
    }
    const rows = rankRows();
    const winners = rows.filter((r) => r[1] === rows[0][1] && r[2] === rows[0][2]).map((r) => r[0]);
    // 全員を城の前に横一列(順位はまだ秘密)
    cam.fade(); await wait(8);
    const line = [...G.players].sort(() => Math.random() - 0.5);
    line.forEach((n, i) => world.getPlayers({ name: n })[0]?.teleport({ x: 0.5 + (i - (line.length - 1) / 2) * 2, y: 1, z: 128.5 }, { facingLocation: { x: 0.5 + (i - (line.length - 1) / 2) * 2, y: 1.6, z: 118 } }));
    const left = 0.5 - (line.length - 1), right = 0.5 + (line.length - 1);
    cam.to("@a", { x: left - 2, y: 2.2, z: 124 }, { x: left, y: 1.6, z: 128.5 }, 0.2);
    banner("result", "", 160);
    await wait(6);
    cmd("execute as @a at @s run playsound mpl.drumroll @s ~ ~ ~ 1 1");
    // ドラムロールの間(約8秒): 左から右へゆっくり流れながら少し引く
    cam.to("@a", { x: right + 2, y: 3.2, z: 121.5 }, { x: right, y: 1.6, z: 128.5 }, 7.6, "in_out_sine");
    await wait(152);
    // 鳴り終わり: 優勝した人にズーム → 花火
    const w0 = world.getPlayers({ name: winners[0] })[0], wl = w0?.location ?? { x: 0.5, y: 1, z: 128.5 };
    cam.to("@a", { x: wl.x, y: wl.y + 1.7, z: wl.z - 2.6 }, { x: wl.x, y: wl.y + 1.6, z: wl.z }, 0.6, "out_back");
    await wait(12);
    banner("champion", `${I.crown} ${winners.join(" & ")} ${I.crown}`, 120);
    soundAllPlayers("random.totem", 1);
    for (let i = 0; i < 16; i++) {
        for (const n of winners) { const w = world.getPlayers({ name: n })[0]; if (!w) continue; const l = w.location; cmd(`particle minecraft:totem_particle ${l.x} ${l.y + 1} ${l.z}`); if (i % 3 === 0) spawnAt("minecraft:fireworks_rocket", { x: l.x + rand(-4, 4), y: l.y + 1, z: l.z + rand(-4, 4) }); }
        await wait(10);
    }
    cam.clear();
    showStandings("FINAL RESULTS");
    await wait(150);
    const st = load("party_stats", {}); for (const n of winners) st[n] = (st[n] ?? 0) + 1; save("party_stats", st);
}

// ===== ミニゲームだけ遊ぶ(1つ選ぶ / 全部を順番に)=====
async function minigameTour(ids) {
    if (G.on) return;
    G.on = true;
    try {
        for (let i = 0; i < ids.length && G.on; i++) {
            const id = ids[i];
            if (ids.length > 1) { ribbon("purple", `${i + 1} / ${ids.length}`, MINIGAMES[id], 40); await wait(45); }
            bgm("minigame");
            const w = await playMinigame(id, world.getPlayers());
            bgm(null);
            if (w.length) banner("win", w.map((p) => p.name).join(", "), 45); else ribbon("gray", "NO WINNER", "", 40);
            for (const p of world.getPlayers()) p.teleport(LOBBY);
            await wait(50);
        }
    } finally { G.on = false; bgm(null); }
}

// ===== メニュー(MPL のメニューのアイテム: mpl:menu)=====
// 管理者のメニューはいつでも一番右(スロット9)に固定。動かせない・落とせない・死んでも消えない。消されても すぐ戻す
function keepMenu(p) {
    const inv = p.getComponent("minecraft:inventory")?.container; if (!inv) return;
    const cur = inv.getItem(8);
    if (cur?.typeId === "mpl:menu" && cur.lockMode === ItemLockMode.slot && cur.keepOnDeath) return;
    for (let i = 0; i < inv.size; i++) if (i !== 8 && inv.getItem(i)?.typeId === "mpl:menu") inv.setItem(i); // ほかの場所のメニューは消す
    if (cur && cur.typeId !== "mpl:menu") { inv.setItem(8); const rest = inv.addItem(cur); if (rest) p.dimension.spawnItem(rest, p.location); } // スロット9にあった物はよける
    const m = new ItemStack("mpl:menu"); m.lockMode = ItemLockMode.slot; m.keepOnDeath = true;
    inv.setItem(8, m);
}
system.runInterval(() => { for (const p of world.getPlayers()) if (isAdmin(p)) { try { keepMenu(p); } catch {} } }, 10);
world.afterEvents.itemUse.subscribe((ev) => { if (ev.itemStack?.typeId === "mpl:menu") menu(ev.source); });
async function menu(p) {
    if (!isAdmin(p)) { bar(p, "§cメニューは管理者だけ使えます"); return; }
    const items = G.on
        ? [["§c§lすごろくを終わる", stopParty], ["§cミニゲームをスキップ", skipNow], ["BOT", (q) => q.runCommand("scriptevent mmgbot:ui")]]
        : [["§e§lすごろくを始める", startUI], ["ミニゲームを1つ選んで遊ぶ", pickUI], ["ミニゲームを全部順番に遊ぶ", tourUI], ["ミニゲームの ON/OFF", mgUI], ["BOT", (q) => q.runCommand("scriptevent mmgbot:ui")], ["BGM の ON/OFF", bgmUI], ["ボードを建て直す", () => buildBoard()]];
    const f = new ActionFormData().title(`${FORM_MARK}§lMEGAMI PARTY LAND`).body(G.on ? `§l§7ターン ${G.turn} / ${G.turns}` : "§l§7何をする？");
    items.forEach(([t]) => f.button(`§l${t}`));
    const r = await f.show(p); if (r.canceled) return;
    items[r.selection][1](p);
}
async function startUI(p) {
    const r = await new ModalFormData().title("すごろくを始める")
        .dropdown("ターン数", ["5ターン", "10ターン", "15ターン", "20ターン"], { defaultValueIndex: 1 })
        .dropdown("ミニゲームのむずかしさ", ["1", "2", "3", "4", "5"], { defaultValueIndex: 1 })
        .show(p);
    if (r.canceled) return;
    setScore("game", "level", r.formValues[1] + 1);
    startParty([5, 10, 15, 20][r.formValues[0]], world.getPlayers());
}
async function pickUI(p) {
    const ids = MG_IDS;
    const f = new ActionFormData().title(`${FORM_MARK}§lミニゲームを選ぶ`).body("§l遊ぶミニゲームを選んでね");
    ids.forEach((id) => f.button(`§l${MINIGAMES[id]}\n§7${MG_HOWTO[id] ?? ""}`));
    const r = await f.show(p); if (r.canceled) return;
    minigameTour([ids[r.selection]]);
}
async function tourUI(p) {
    const ids = mgOn();
    const r = await new MessageFormData().title("ミニゲームを全部順番に").body(`ONのミニゲーム ${ids.length}個を、1回ずつ順番に遊びます`).button1("やめる").button2("§a始める").show(p);
    if (r.selection === 1) minigameTour(ids);
}
async function mgUI(p) {
    const off = load("mg_off", []);
    const f = new ModalFormData().title("ミニゲームの ON/OFF");
    MG_IDS.forEach((id) => f.toggle(MINIGAMES[id], { defaultValue: !off.includes(id) }));
    const r = await f.show(p); if (r.canceled) return;
    const next = MG_IDS.filter((_, i) => !r.formValues[i]);
    if (next.length === MG_IDS.length) { bar(p, "§c1つ以上ONにしてください"); return; }
    save("mg_off", next); bar(p, `§aON ${MG_IDS.length - next.length} / OFF ${next.length}`);
}
async function bgmUI(p) { const off = !load("bgm_off", true); save("bgm_off", off); bar(p, off ? "§7BGM を OFF にしました" : "§aBGM を ON にしました"); if (off) bgm(null); }
async function skipNow(p) {
    if (!run.active) { bar(p, "§c今はミニゲーム中ではありません"); return; }
    const r = await new MessageFormData().title("ミニゲームをスキップ").body(`「${MINIGAMES[run.id]}」をスキップしますか？\n§7だれにもコインは入りません`).button1("やめる").button2("§cスキップする").show(p);
    if (r.selection !== 1 || !run.active) return;
    toast(`§e${p.name} が「${MINIGAMES[run.id]}」をスキップしました`);
    run.active = false;
}
async function stopParty(p) {
    const r = await new MessageFormData().title("すごろくを終わる").body("今のすごろくを途中で終わりますか？\n§7結果は残りません").button1("やめる").button2("§c終わる").show(p);
    if (r.selection !== 1) return;
    G.on = false; run.active = false;
    toast(`§e${p.name} がすごろくを終わりました`);
}

// ===== ワールドの準備・入ってきた人 =====
system.runTimeout(() => {
    for (const o of ["game", "setting"]) obj(o);
    for (const c of ["gamerule dodaylightcycle false", "time set 6000", "gamerule doweathercycle false", "weather clear", "gamerule domobspawning false", "gamerule pvp false",
        "gamerule falldamage false", "gamerule keepinventory true", "gamerule doimmediaterespawn true", "gamerule sendcommandfeedback false", "gamerule commandblockoutput false",
        "gamerule showcoordinates false", `setworldspawn ${LOBBY.x | 0} ${LOBBY.y} ${LOBBY.z | 0}`, "tickingarea add -24 -5 -49 25 40 0 mpl_field1 true", "tickingarea add -24 -5 1 25 40 50 mpl_field2 true"]) cmd(c);
    if ((load("board_built", 0)) < 7) buildBoard();
}, 60);
world.afterEvents.playerSpawn.subscribe((ev) => {
    const p = ev.player;
    if (isBot(p)) return;
    if (!load("host", null)) { save("host", p.name); p.addTag("mpl_admin"); }
    if (isAdmin(p)) keepMenu(p);
    if (ev.initialSpawn) {
        if (!G.on) p.teleport(LOBBY, lookCenter);
        banner("title", "ようこそ！", 70, [p]);
    }
});
// ワニの口の中に入らない(入ったら前へ押し出す)
system.runInterval(() => {
    if (score("game", "selectgame") !== 51) return;
    for (const p of playing()) { const l = p.location; if (l.x > -2 && l.x < 3 && l.z > -12 && l.z < 2.6 && !isBot(p)) p.teleport({ x: l.x, y: 1, z: 2.7 }); }
}, 2);
