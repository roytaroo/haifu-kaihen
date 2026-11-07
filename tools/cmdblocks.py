# Bedrock LevelDB(.ldb) から コマンドブロックの座標とコマンドを抜き出す(最小実装)
import sys, os, zlib, struct, json
def varint(b, i):
    r = s = 0
    while True:
        c = b[i]; i += 1; r |= (c & 0x7f) << s; s += 7
        if c < 0x80: return r, i
def block(f, off, size):
    f.seek(off); d = f.read(size + 5); t = d[size]; d = d[:size]
    if t == 0: return d
    if t == 2: return zlib.decompress(d)
    if t == 4: return zlib.decompress(d, -15)
    raise ValueError(t)
def entries(d):
    n = struct.unpack('<I', d[-4:])[0]; end = len(d) - 4 - 4 * n; i = 0; key = b''
    while i < end:
        sh, i = varint(d, i); ns, i = varint(d, i); vl, i = varint(d, i)
        key = key[:sh] + d[i:i + ns]; i += ns; yield key, d[i:i + vl]; i += vl
def table(p):
    with open(p, 'rb') as f:
        f.seek(-48, 2); ft = f.read(48); i = 0
        _, i = varint(ft, i); _, i = varint(ft, i); io, i = varint(ft, i); isz, i = varint(ft, i)
        for _, h in entries(block(f, io, isz)):
            o, j = varint(h, 0); s, j = varint(h, j)
            yield from entries(block(f, o, s))
# 簡易NBT
def nbt(b, i, t):
    if t == 1: return b[i], i + 1
    if t == 2: return struct.unpack_from('<h', b, i)[0], i + 2
    if t == 3: return struct.unpack_from('<i', b, i)[0], i + 4
    if t == 4: return struct.unpack_from('<q', b, i)[0], i + 8
    if t == 5: return struct.unpack_from('<f', b, i)[0], i + 4
    if t == 6: return struct.unpack_from('<d', b, i)[0], i + 8
    if t == 7: n = struct.unpack_from('<i', b, i)[0]; return None, i + 4 + n
    if t == 8: n = struct.unpack_from('<H', b, i)[0]; return b[i + 2:i + 2 + n].decode('utf-8', 'replace'), i + 2 + n
    if t == 9:
        et = b[i]; n = struct.unpack_from('<i', b, i + 1)[0]; i += 5; out = []
        for _ in range(n): v, i = nbt(b, i, et); out.append(v)
        return out, i
    if t == 10:
        out = {}
        while True:
            tt = b[i]; i += 1
            if tt == 0: return out, i
            n = struct.unpack_from('<H', b, i)[0]; name = b[i + 2:i + 2 + n].decode('utf-8', 'replace'); i += 2 + n
            out[name], i = nbt(b, i, tt)
    if t == 11: n = struct.unpack_from('<i', b, i)[0]; return None, i + 4 + 4 * n
    if t == 12: n = struct.unpack_from('<i', b, i)[0]; return None, i + 4 + 8 * n
    raise ValueError(t)
db = sys.argv[1]; seen = {}
for fn in sorted(os.listdir(db)):
    if not fn.endswith('.ldb'): continue
    for k, v in table(os.path.join(db, fn)):
        ukey = k[:-8]
        if len(ukey) in (9, 13) and ukey[-1] == 0x31 and v:
            i = 0
            while i < len(v):
                t = v[i]; n = struct.unpack_from('<H', v, i + 1)[0]; i += 3 + n
                c, i = nbt(v, i, t)
                if c.get('id') == 'CommandBlock':
                    seen[(c['x'], c['y'], c['z'])] = c   # 後のファイルが新しい
out = [{'pos': [c['x'], c['y'], c['z']], 'cmd': c.get('Command', ''), 'auto': c.get('auto'), 'name': c.get('CustomName', ''), 'delay': c.get('TickDelay')} for c in seen.values()]
out.sort(key=lambda e: (e['pos'][0], e['pos'][2], e['pos'][1]))
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=0)
print(len(out), 'command blocks')
