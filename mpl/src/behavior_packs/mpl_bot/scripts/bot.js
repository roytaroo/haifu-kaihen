// MMG Bot: ダミーのプレイヤー(SimulatedPlayer)を BOT として出し入れし、ゲームごとにざっくり動かす
// BOT は本物のプレイヤー扱いなので、元のゲームの @a[tag=playing] などにそのまま入る。目印のタグは "mmgbot"
// mmg_plus からの指示: scriptevent mmgbot:jump <名前>(縄跳び)
import { world, system, GameMode, ItemStack, Player, EquipmentSlot } from "@minecraft/server";
import { ActionFormData, ModalFormData } from "@minecraft/server-ui";
// 文字を全部太字に(main.js と同じ)
const boldText = (t) => { if (typeof t !== "string") return t; const m = t.match(/^(?:§.)*/)[0]; return m + "§l" + t.slice(m.length).replace(/§([0-9a-fr])/g, "§$1§l"); };
for (const [proto, names] of [[ModalFormData.prototype, ["title", "slider", "dropdown", "toggle"]], [ActionFormData.prototype, ["title", "body", "button"]], [Player.prototype, ["sendMessage"]]])
    for (const n of names) { const f = proto?.[n]; if (typeof f === "function") proto[n] = function (...a) { a[0] = boldText(a[0]); return f.apply(this, a); }; }
import { spawnSimulatedPlayer } from "@minecraft/server-gametest";

const TAG = "mmgbot";
// BOT は10人。スキンは RP の entity/player.entity.json + render_controllers/mpl_bot(名前で差しかえ)
const NAMES = ["Jack", "Humming", "Widow", "Splash", "Oracle", "Byte", "Shade", "Jester", "Replica", "Comet"];
const PROFILE = {
    Jack: "元気なお調子者", Humming: "がんばり屋", Widow: "無口でけだるい", Splash: "いつも眠いマイペース", Oracle: "ヘラヘラ天才",
    Byte: "ロボット", Shade: "いたずら好きのうっかり者", Jester: "びっくりさせ屋", Replica: "なぞめいたからかい屋", Comet: "ぶっきらぼうな脳筋",
};
// せりふ(場面ごと)。main.js から scriptevent mmgbot:say <名前> <場面>
const LINES = {
    Jack: { start: ["主役はオレだ！ みんな見とけよ〜！", "今日もいっちょ目立ってやるぜ！"], turn: ["よっしゃ、オレの番！ 注目〜！", "見てろよ、ド派手にいくぜ！"], good: ["見た！？ 今の見た！？", "さすがオレ！ 天才！"], bad: ["ちょ、今のナシ！ ナシで！", "いや〜、これも演出ってやつ？"], star: ["スターはオレのためにある！", "主役にスター、似合いすぎだろ！"], win: ["当然の1位！ 拍手〜！", "勝っちゃった〜！ ごめんね〜！"], lose: ["次！ 次こそ本気出す！", "今のは手加減したの！ ほんとだって！"], champ: ["優勝〜！ 今日の主役はオレでした〜！", "サインいる？ 今なら無料だぜ！"] },
    Humming: { start: ["が、がんばります！ 負けないから！", "今日こそ1位、とるんだから！"], turn: ["よし…集中、集中！", "見てて、ちゃんとやるから！"], good: ["ほらね、練習したもん！", "やった…！ 当然だけどね！"], bad: ["う…ま、まだ平気だし！", "今のは、えっと…想定内！"], star: ["スター！ がんばったかいがあった〜！", "ふふん、これくらい余裕よ！"], win: ["1位！ ぜんぶ計算どおり…なんてね！", "やった！ 練習の成果！"], lose: ["くやしい…！ 次は絶対勝つ！", "べ、別に本気じゃなかったし…"], champ: ["優勝…！ 本当に？ やったぁ！", "がんばってよかった…！ ありがと！"] },
    Widow: { start: ["…眠い。早く終わらせよ", "…起こさないでね"], turn: ["…ん", "…行く"], good: ["…ふーん", "…悪くない"], bad: ["…はぁ", "…まあ、いいけど"], star: ["…もらっとく", "…スター。ふわぁ"], win: ["…簡単", "…終わり。寝ていい？"], lose: ["…寝てたから", "…次は起きてる"], champ: ["…優勝。…じゃ、昼寝する", "…当然。おやすみ"] },
    Splash: { start: ["ふぁ〜…パーティ？ がんばる〜", "眠いけど…やるときはやるよ〜"], turn: ["ん〜…ぼくの番〜？", "ゆっくり行こ〜"], good: ["わ〜い、ラッキ〜", "ふふ〜、いい感じ〜"], bad: ["あ〜…まいっか〜", "ねむ〜い…"], star: ["スター、もらっちゃった〜", "わ〜、キラキラ〜"], win: ["…本気出しちゃった。てへ", "あれ、勝ってる〜？"], lose: ["ふぁ〜…寝てた〜", "次は本気出す…たぶん〜"], champ: ["優勝〜？ じゃあ、ごほうびに寝る〜", "みんなありがと〜…zzz"] },
    Oracle: { start: ["は〜い、今日もサクッと勝っちゃお〜", "みんな、手加減しとくね？ あはは"], turn: ["ほいほい、いっくよ〜", "サイコロさん、いい子にしてね〜"], good: ["知ってた〜♪", "ね？ 言ったでしょ〜"], bad: ["あはは、そういうこともあるよね〜", "ま、計算のうちってことで〜"], star: ["スター、いただきま〜す♪", "予想どおりすぎて逆に笑う〜"], win: ["はい1位〜♪ かる〜い", "ごめんね〜、強くて〜"], lose: ["あれ〜？ 今日は調子悪いかも〜", "次は本気、出しちゃおっかな〜"], champ: ["優勝〜♪ ま、当然だよね〜", "みんなおつかれ〜♪ また遊ぼ〜"] },
    Byte: { start: ["システム起動。勝利プロトコル、開始シマス。", "パーティモード、オン。"], turn: ["ワタシノ番。サイコロ、投下シマス。", "移動ルート、計算中…"], good: ["予定ドオリデス。", "成功。ピピッ。"], bad: ["エラー。想定外ノ事態デス。", "損失ヲ記録シマシタ。"], star: ["スター、取得。満足度、上昇。", "目標ヲ達成シマシタ。"], win: ["勝利。データ通リデス。", "1位ヲ記録。ピピピ。"], lose: ["敗北。学習シマス。", "再計算ガ必要デス。"], champ: ["優勝。…コレガ、ウレシイ、トイウ感情？", "全プログラム、完了。アリガトウ。"] },
    Shade: { start: ["にしし、今日は何してやろっかな〜", "いたずらの準備はばっちり！ …あれ、どこ置いたっけ"], turn: ["オレの番か！ …サイコロどこ？", "よーし、こっそり行くぞ〜"], good: ["にしし、作戦どおり！", "やった！ …たまたまだけど！"], bad: ["わっ、しまった！", "あちゃ〜、うっかりした〜"], star: ["スター、こっそりいただき！", "にしし、だれにも見られてないよな？"], win: ["いたずら成功〜！ じゃなくて1位！", "にしし、勝っちゃった！"], lose: ["うっかりしてた…", "次は落とし穴しかけとくからな！"], champ: ["優勝！？ うっかり勝っちゃった〜！", "にしし、みんなまんまとだまされたな！"] },
    Jester: { start: ["ばぁっ！ …びっくりした？ 始めよっか！", "今日はどんなサプライズが起きるかな〜！"], turn: ["さあ、何が起きるかお楽しみ！", "ジャジャーン！ ボクの番だよ！"], good: ["サプライズ大成功！", "ほら、驚いたでしょ！"], bad: ["うわっ、ボクが驚かされた！", "これはこれで、おもしろい！"], star: ["ジャーン！ スターでした〜！", "みんなの顔、最高！"], win: ["ばぁっ！ 1位だよ〜！", "驚いた？ ボクの勝ち！"], lose: ["ちぇっ、次はもっと驚かすからね", "まさかボクが負けるなんて…これもサプライズ！"], champ: ["最後のサプライズ！ ボクの優勝〜！", "みんな、今日いちばん驚いたでしょ？"] },
    Replica: { start: ["ふふ…わたしはだれでしょう？", "今日は、だれのマネをしようかな"], turn: ["わたしの番。…それとも、あなたの番？", "ふふ、どこへ行くと思う？"], good: ["ほら、言ったとおり", "ふふ…あなたもこうしたかった？"], bad: ["…あら。わざとよ", "ふうん。そう来るのね"], star: ["スター…あなたが欲しかったもの、でしょ？", "ふふ、もらっていくわ"], win: ["勝ったのは、本物のわたし？", "ふふ、つかまえてごらん"], lose: ["負けたのは、わたしのニセモノ", "…今日は、ゆずってあげる"], champ: ["優勝。…さて、本当はだれでしょう？", "ふふ、また会いましょう"] },
    Comet: { start: ["さっさと始めるぞ。勝つのはオレだ", "考えるのは苦手だ。走って勝つ"], turn: ["オレの番だ。どけ", "……行くぞ"], good: ["ふん、当然だ", "…べ、別にうれしくねーし"], bad: ["チッ…", "なんだよこれ…力でなんとかならねーのか"], star: ["スター？ …まあ、もらってやる", "…ありがとな。言わせんな"], win: ["力こそパワーだ", "ふん。楽勝だ"], lose: ["…くそっ、もう1回だ！", "べ、別にくやしくねーし！"], champ: ["優勝…？ …べ、別にうれしくなんか…ある", "…今日は、楽しかった。…なんでもねー"] },
};
function say(name, ev) {
    const l = LINES[name]?.[ev]; if (!l) return;
    world.sendMessage(`§e<${name}>§r ${l[Math.floor(Math.random() * l.length)]}`);
}
const LOBBY = { x: 0.5, y: 1, z: 65.5 }; // MPL のロビー(港の広場)
const STRENGTH = ["よわい", "ふつう", "つよい"];
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
    const pool = (setting().chosen ?? NAMES).filter((n) => NAMES.includes(n));
    const name = pool.find((n) => !bots.has(n) && !world.getPlayers({ name: n }).length);
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
    if (ev.id === "mmgbot:add") { const n = Number(ev.message) || 1; for (let k = 0; k < n; k++) addBot(); return; }
    // すごろくで抜けた人の代わり: 決まった名前の BOT を出す / 戻ってきたら消す
    if (ev.id === "mmgbot:spawnas") { const n = ev.message.trim(); if (NAMES.includes(n) && !bots.has(n)) { const p = spawnSimulatedPlayer({ dimension: dim(), ...LOBBY }, n, GameMode.Adventure ?? GameMode.adventure); p.addTag(TAG); bots.set(n, p); } return; }
    if (ev.id === "mmgbot:remove") { const n = ev.message.trim(), p = bots.get(n); if (p) { try { p.disconnect(); } catch {} bots.delete(n); brain.delete(n); } return; }
    // ミニゲームからの指示: jump <名前> / move <名前> x y z [速さ] / look <名前> x y z / sneak <名前> 0|1 / stop <名前>
    const [who, ...a] = ev.message.trim().split(/\s+/), b = bots.get(who);
    if (!b) return;
    try {
        if (ev.id === "mmgbot:jump") b.jump();
        if (ev.id === "mmgbot:move") { const [x, y, z, sp] = a.map(Number); b.isSprinting = true; b.moveToLocation({ x, y, z }, { speed: sp || speed(), faceTarget: true }); held.set(who, system.currentTick + 30); }
        if (ev.id === "mmgbot:look") { const [x, y, z] = a.map(Number); b.lookAtLocation({ x, y, z }); held.set(who, system.currentTick + 20); }
        if (ev.id === "mmgbot:sneak") b.isSneaking = a[0] === "1";
        if (ev.id === "mmgbot:stop") { b.stopMoving(); held.set(who, system.currentTick + 20); }
        if (ev.id === "mmgbot:say") say(who, a[0]);
    } catch {}
});

// BOT を選ぶ: 出すBOTにチェック(上から順に人数ぶん出る)+ 強さ
async function botUI(player) {
    const st = setting(), chosen = new Set(st.chosen ?? NAMES.slice(0, 3));
    const f = new ModalFormData().title("BOT");
    NAMES.forEach((n) => f.toggle(`${n}  §7${PROFILE[n]}`, { defaultValue: chosen.has(n) && (bots.has(n) || !bots.size) }));
    f.dropdown("BOTの強さ", STRENGTH, { defaultValueIndex: strength() });
    const res = await f.show(player);
    if (res.canceled) return;
    const v = res.formValues, pick = NAMES.filter((_, i) => v[i]);
    st.strength = v[NAMES.length]; st.chosen = pick; saveSetting(st);
    for (const n of [...bots.keys()]) if (!pick.includes(n)) { try { bots.get(n).disconnect(); } catch {} bots.delete(n); brain.delete(n); }
    for (const n of pick) if (!bots.has(n)) addBot();
    const s2 = setting(); s2.count = bots.size; saveSetting(s2);
    player.sendMessage(`§aBOT: ${[...bots.keys()].join(", ") || "なし"}(${STRENGTH[st.strength]})`);
    for (const n of bots.keys()) system.runTimeout(() => say(n, "start"), 20 + Math.floor(Math.random() * 40));
}

// ===== 見た目 =====
// スキンは RP 側で名前ごとに差しかえる。前の版で着せた革の服は脱がせる
system.runInterval(() => { for (const [, p] of bots) { try { const eq = p.getComponent("minecraft:equippable"); for (const sl of [EquipmentSlot.Chest, EquipmentSlot.Legs, EquipmentSlot.Feet]) if (eq?.getEquipment(sl)?.typeId?.startsWith("minecraft:leather_")) eq.setEquipment(sl); } catch {} } }, 100);

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
    const v = p.getVelocity(), stuck = Math.hypot(v.x, v.z) < 0.01 && system.currentTick > (b.since ?? 0) + 8;
    if (b.goal && !stuck && Math.hypot(b.goal.x - l.x, b.goal.z - l.z) > 1.2 && system.currentTick < b.next) return;
    b.since = system.currentTick;
    const goal = { x: l.x + rand(-radius, radius), y: l.y, z: l.z + rand(-radius, radius) };
    if (inArena && !IN_ARENA(goal)) { goal.x = rand(-6, 6); goal.z = rand(-6, 6); }
    b.goal = goal; b.next = system.currentTick + Math.floor(rand(20, 45));
    p.moveToLocation(goal, { speed: speed(), faceTarget: true });
}
// 道さがしで歩く。道が見つからない時は まっすぐ歩く
function walk(p, goal) {
    let ok = false;
    try { const r = p.navigateToLocation(goal, speed()); ok = !!r?.isFullPath; } catch {}
    if (!ok) p.moveToLocation(goal, { speed: speed(), faceTarget: true });
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
    walk(p, goal);
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
