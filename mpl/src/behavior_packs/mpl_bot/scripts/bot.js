// MMG Bot: ダミーのプレイヤー(SimulatedPlayer)を BOT として出し入れし、ゲームごとにざっくり動かす
// BOT は本物のプレイヤー扱いなので、元のゲームの @a[tag=playing] などにそのまま入る。目印のタグは "mmgbot"
// mmg_plus からの指示: scriptevent mmgbot:jump <名前>(縄跳び)
import { world, system, GameMode, ItemStack } from "@minecraft/server";
import { ActionFormData, ModalFormData } from "@minecraft/server-ui";
import { spawnSimulatedPlayer } from "@minecraft/server-gametest";

const TAG = "mmgbot";
const NAMES = ["Aki", "Ren", "Mio", "Sora", "Yuu", "Haru", "Nagi", "Kai", "Rin", "Tomo", "Sei", "Hina"];
const LOBBY = { x: 0.5, y: 1, z: 124.5 }; // MPL のロビー
const STRENGTH = ["EASY", "NORMAL", "HARD"];
const dim = () => world.getDimension("overworld");
const rand = (a, b) => a + Math.random() * (b - a);
const bots = new Map(); // 名前 → SimulatedPlayer
const brain = new Map(); // 名前 → { next, goal, phase }
const held = new Map(); // 名前 → この tick までは自分で考えない(ミニゲームから動きを指示された)

function setting() {
    try { return JSON.parse(world.getDynamicProperty("bot") ?? "{}"); } catch { return {}; }
}
function saveSetting(s) {
    world.setDynamicProperty("bot", JSON.stringify(s));
    // mmg_plus のゲームが BOT の強さを見られるように
    try { world.scoreboard.getObjective("setting")?.setScore("bot_strength", s.strength ?? 1); } catch {}
}
const strength = () => setting().strength ?? 1; // 0 よわい / 1 ふつう / 2 つよい
const speed = () => [0.85, 1, 1.15][strength()];
function score(objective, name) {
    try { return world.scoreboard.getObjective(objective)?.getScore(name); } catch { return undefined; }
}

// ===== 出し入れ =====
function addBot() {
    const name = NAMES.find((n) => !bots.has(n) && !world.getPlayers({ name: n }).length);
    if (!name) return false;
    const p = spawnSimulatedPlayer({ dimension: dim(), ...LOBBY }, name, GameMode.Adventure ?? GameMode.adventure);
    p.addTag(TAG);
    bots.set(name, p);
    return true;
}
function removeBots(n = Infinity) {
    for (const [name, p] of [...bots]) {
        if (n-- <= 0) break;
        try { p.disconnect(); } catch {}
        bots.delete(name); brain.delete(name);
    }
}
function setCount(n) {
    while (bots.size > n) removeBots(1);
    while (bots.size < n && addBot());
    const s = setting(); s.count = bots.size; saveSetting(s);
}
// 開き直した時は前の人数に戻す(ダミーはワールドを閉じると消えるため)
system.runTimeout(() => { const n = setting().count ?? 0; if (n) setCount(n); }, 100);

world.afterEvents.entityDie.subscribe((ev) => {
    const p = ev.deadEntity;
    if (p.typeId === "minecraft:player" && bots.has(p.name)) system.runTimeout(() => { try { bots.get(p.name)?.respawn(); } catch {} }, 40);
});

system.afterEvents.scriptEventReceive.subscribe((ev) => {
    if (ev.id === "mmgbot:ui" && ev.sourceEntity?.typeId === "minecraft:player") botUI(ev.sourceEntity);
    // ミニゲームからの指示: jump <名前> / move <名前> x y z [速さ] / look <名前> x y z / sneak <名前> 0|1 / stop <名前>
    const [who, ...a] = ev.message.trim().split(/\s+/), b = bots.get(who);
    if (!b) return;
    try {
        if (ev.id === "mmgbot:jump") b.jump();
        if (ev.id === "mmgbot:move") { const [x, y, z, sp] = a.map(Number); b.isSprinting = true; b.moveToLocation({ x, y, z }, { speed: sp || speed(), faceTarget: true }); held.set(who, system.currentTick + 30); }
        if (ev.id === "mmgbot:look") { const [x, y, z] = a.map(Number); b.lookAtLocation({ x, y, z }); held.set(who, system.currentTick + 20); }
        if (ev.id === "mmgbot:sneak") b.isSneaking = a[0] === "1";
        if (ev.id === "mmgbot:stop") { b.stopMoving(); held.set(who, system.currentTick + 20); }
    } catch {}
});

async function botUI(player) {
    const res = await new ModalFormData().title("BOT")
        .slider("Number of bots", 0, NAMES.length, { valueStep: 1, defaultValue: bots.size })
        .dropdown("Bot strength", STRENGTH, { defaultValueIndex: strength() })
        .show(player);
    if (res.canceled) return;
    const [n, st] = res.formValues;
    const s = setting(); s.strength = st; saveSetting(s);
    setCount(n);
    player.sendMessage(`§aBots: ${bots.size} (${STRENGTH[st]})`);
}

// ===== 動き =====
// ゲームの種類ごとにざっくり動かす。細かい判断がいるゲーム(投票・数え・クラフト)は歩き回るだけ
const ATTACK = new Set([2, 5, 7, 22, 41, 45]); // 近くの相手をなぐる
const KEEP_MOVING = new Set([4, 15, 18, 19, 21, 29]); // 止まらずに動く
const IN_ARENA = (l) => l.x > -24 && l.x < 25 && l.z > -49 && l.z < 50;

function nearest(p, list) {
    let best, bd = Infinity;
    for (const e of list) {
        if (e.id === p.id) continue;
        const d = (e.location.x - p.location.x) ** 2 + (e.location.z - p.location.z) ** 2 + (e.location.y - p.location.y) ** 2;
        if (d < bd) { bd = d; best = e; }
    }
    return best ? { e: best, d: Math.sqrt(bd) } : undefined;
}
// 歩き回る: 1〜2秒ごとに行き先を変えて、走ったり跳んだりする(止まって見えないように)
function roam(p, b, radius = 7, inArena = true) {
    const l = p.location;
    lively(p);
    if (b.goal && Math.hypot(b.goal.x - l.x, b.goal.z - l.z) > 1.2 && system.currentTick < b.next) return;
    const goal = { x: l.x + rand(-radius, radius), y: l.y, z: l.z + rand(-radius, radius) };
    if (inArena && !IN_ARENA(goal)) { goal.x = rand(-6, 6); goal.z = rand(-6, 6); }
    b.goal = goal; b.next = system.currentTick + Math.floor(rand(20, 45));
    try { p.navigateToLocation(goal, speed()); } catch { p.moveToLocation(goal, { speed: speed() }); }
}
function lively(p) {
    try { const v = p.getVelocity(); p.isSprinting = Math.hypot(v.x, v.z) > 0.05; } catch {}
    if (Math.random() < 0.004) { try { p.jump(); } catch {} } // たまに跳ぶくらい
}
// ロビー: スタート地点のまわりを歩き回る(遠くへ行きすぎたら戻る)
function lobbyRoam(p, b) {
    const l = p.location;
    lively(p);
    if (b.goal && Math.hypot(b.goal.x - l.x, b.goal.z - l.z) > 1.2 && system.currentTick < b.next) return;
    const far = Math.hypot(l.x - LOBBY.x, l.z - LOBBY.z) > 12;
    const base = far ? LOBBY : l;
    const goal = { x: base.x + rand(-6, 6), y: l.y, z: base.z + rand(-6, 6) };
    b.goal = goal; b.next = system.currentTick + Math.floor(rand(25, 60));
    try { p.navigateToLocation(goal, speed()); } catch { p.moveToLocation(goal, { speed: speed() }); }
}
function chase(p, target, hit = true) {
    lively(p);
    p.lookAtEntity(target.e);
    p.moveToLocation(target.e.location, { speed: speed() });
    if (hit && target.d < 3 && Math.random() < [0.25, 0.45, 0.7][strength()]) p.attackEntity(target.e);
}
function flee(p, from) {
    const l = p.location, f = from.e.location;
    const dx = l.x - f.x, dz = l.z - f.z, n = Math.hypot(dx, dz) || 1;
    const goal = { x: l.x + (dx / n) * 5 + rand(-2, 2), y: l.y, z: l.z + (dz / n) * 5 + rand(-2, 2) };
    p.moveToLocation(IN_ARENA(goal) ? goal : { x: rand(-5, 5), y: l.y, z: rand(-5, 5) }, { speed: speed() });
}
function findBlock(p, ids, r = 6, dy = [-1, 0]) {
    const l = p.location, d = dim();
    let best, bd = Infinity;
    for (let x = -r; x <= r; x++) for (let z = -r; z <= r; z++) for (const y of dy) {
        const pos = { x: Math.floor(l.x) + x, y: Math.floor(l.y) + y, z: Math.floor(l.z) + z };
        let id; try { id = d.getBlock(pos)?.typeId; } catch { continue; }
        if (!ids.includes(id)) continue;
        const dist = x * x + z * z;
        if (dist < bd) { bd = dist; best = pos; }
    }
    return best;
}

system.runInterval(() => {
    const sg = score("game", "selectgame") ?? 0;
    const players = world.getPlayers({ tags: ["playing"] });
    for (const [name, p] of bots) {
        if (!p.isValid) { bots.delete(name); continue; }
        if (p.getGameMode() === (GameMode.Spectator ?? GameMode.spectator)) continue;
        if (p.hasTag("mpl_board") || p.hasTag("mpl_lock")) { try { p.stopMoving(); } catch {} continue; } // すごろくの間・動けない時は待つ
        if ((held.get(name) ?? 0) > system.currentTick) continue;
        if (!p.hasTag("playing")) { let b = brain.get(name); if (!b || b.sg !== -1) { b = { sg: -1 }; brain.set(name, b); } try { lobbyRoam(p, b); } catch {} continue; }
        let b = brain.get(name);
        if (!b || b.sg !== sg) { b = { sg }; brain.set(name, b); try { p.stopSwimming(); p.stopMoving(); } catch {} } // ゲームが変わったら考え直す(泳ぐポーズも直す)
        try { think(p, b, sg, players); } catch (e) { /* 動けない場面は無視 */ }
    }
}, 4);

function think(p, b, sg, players) {
    const others = players.filter((o) => o.id !== p.id);
    if (sg === 6) {
        // TNT TAG: 鬼なら追う(タッチ)、ちがえば鬼から逃げる
        const isOni = p.hasTag("game6_oni");
        const t = nearest(p, isOni ? others.filter((o) => !o.hasTag("game6_oni")) : others.filter((o) => o.hasTag("game6_oni")));
        if (t) return isOni ? chase(p, t) : (t.d < 8 ? flee(p, t) : roam(p, b));
    }
    if (sg === 24) {
        const mobs = dim().getEntities({ location: p.location, maxDistance: 24, families: ["monster"] });
        const t = nearest(p, mobs);
        if (t) return chase(p, t);
    }
    if (ATTACK.has(sg)) { const t = nearest(p, others); if (t) return chase(p, t); }
    if (sg === 19) {
        // 色塗りバトル: 近くの相手チームに雪玉を投げながら歩き回る
        const t = nearest(p, others);
        if (t && t.d < 14 && system.currentTick % [24, 16, 10][strength()] === 0) { p.lookAtEntity(t.e); try { p.useItem(new ItemStack("minecraft:snowball", 1)); } catch {} }
        return roam(p, b, 8);
    }
    if (sg === 1) {
        // Escape Lava: ダイヤブロックに乗ると上の階へ
        const dia = findBlock(p, ["minecraft:diamond_block"], 6, [-1]);
        if (dia) return p.moveToLocation({ x: dia.x + 0.5, y: dia.y + 1, z: dia.z + 0.5 }, { speed: speed() });
    }
    if (sg === 16 && system.currentTick % 20 === 0) {
        const ore = findBlock(p, ["minecraft:coal_ore", "minecraft:iron_ore", "minecraft:gold_ore", "minecraft:diamond_ore", "minecraft:emerald_ore", "minecraft:redstone_ore", "minecraft:lapis_ore", "minecraft:copper_ore"], 4, [-1, 0, 1]);
        if (ore) { p.lookAtBlock(ore); p.breakBlock(ore); return; }
    }
    if (sg === 27) {
        // 椅子取り: 空いているイスへ
        const free = dim().getEntities({ type: "mmgplus:chair" }).filter((c) => !c.getComponent("minecraft:rideable")?.getRiders().length);
        const t = nearest(p, free);
        if (t) { p.moveToLocation(t.e.location, { speed: speed() }); if (t.d < 2.5 && Math.random() < [0.3, 0.5, 0.8][strength()]) p.interactWithEntity(t.e); return; }
    }
    if (sg === 28) {
        // 宝探し: 近くの宝へ泳ぐ(下にあればもぐる)
        const t = nearest(p, ["gold", "diamond", "emerald"].flatMap((k) => dim().getEntities({ type: `mmgplus:treasure_${k}` })));
        if (t) { p.moveToLocation(t.e.location, { speed: speed() }); if (t.e.location.y < p.location.y - 0.5) p.stopSwimming(); else p.swim(); return; }
    }
    if (sg === 32) return farm(p, b);
    roam(p, b, KEEP_MOVING.has(sg) ? 5 : 8);
}

// ニワトリ集め: たねを持ってニワトリに近づき、自分の囲いへ戻る(囲いの位置は mmg_plus と同じ並び)
const PENS = [[0, -16], [12, -12], [16, 0], [12, 12], [0, 16], [-12, 12], [-16, 0], [-12, -12]];
function farm(p, b) {
    if (!b.seeded) { p.setItem(new ItemStack("minecraft:wheat_seeds", 1), 0, true); b.seeded = true; }
    const players = world.getPlayers({ tags: ["playing"] });
    const pen = PENS[players.findIndex((o) => o.id === p.id) % PENS.length];
    const home = { x: pen[0] + 0.5, y: 1, z: pen[1] + 0.5 };
    const atHome = Math.hypot(p.location.x - home.x, p.location.z - home.z) < 1.5;
    if (b.phase === "home") { if (atHome || system.currentTick > b.next) b.phase = "get"; else return p.moveToLocation(home, { speed: speed() * 0.6 }); }
    const chickens = dim().getEntities({ type: "minecraft:chicken", tags: ["mmgplus_chicken"] })
        .filter((c) => Math.abs(c.location.x - pen[0]) > 1.5 || Math.abs(c.location.z - pen[1]) > 1.5);
    const t = nearest(p, chickens);
    if (!t) return;
    if (t.d < 2.5) { b.phase = "home"; b.next = system.currentTick + 200; return; }
    p.moveToLocation(t.e.location, { speed: speed() });
}
