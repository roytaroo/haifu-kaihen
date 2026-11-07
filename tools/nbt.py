# 統合版 level.dat (リトルエンディアン NBT, 8バイトヘッダ) の読み書き
import struct
def read(path):
    data = open(path, 'rb').read()
    ver, ln = struct.unpack('<ii', data[:8]); pos = [8]
    def rd(fmt):
        v = struct.unpack_from('<' + fmt, data, pos[0]); pos[0] += struct.calcsize('<' + fmt); return v[0]
    def rstr():
        n = rd('H'); s = data[pos[0]:pos[0] + n].decode('utf-8', 'replace'); pos[0] += n; return s
    def payload(t):
        if t == 1: return rd('b')
        if t == 2: return rd('h')
        if t == 3: return rd('i')
        if t == 4: return rd('q')
        if t == 5: return rd('f')
        if t == 6: return rd('d')
        if t == 7: n = rd('i'); b = data[pos[0]:pos[0] + n]; pos[0] += n; return ('bytes', b)
        if t == 8: return rstr()
        if t == 9:
            et = rd('b'); n = rd('i'); return ('list', et, [payload(et) for _ in range(n)])
        if t == 10:
            d = {}
            while True:
                tt = rd('b')
                if tt == 0: return d
                k = rstr(); d[k] = (tt, payload(tt))
        if t == 11: n = rd('i'); return ('ints', [rd('i') for _ in range(n)])
        if t == 12: n = rd('i'); return ('longs', [rd('q') for _ in range(n)])
        raise ValueError(t)
    t = rd('b'); name = rstr(); root = payload(t)
    return ver, name, root
def write(path, ver, name, root):
    out = bytearray()
    def w(fmt, v): out.extend(struct.pack('<' + fmt, v))
    def wstr(s): b = s.encode('utf-8'); w('H', len(b)); out.extend(b)
    def payload(t, v):
        if t == 1: w('b', v)
        elif t == 2: w('h', v)
        elif t == 3: w('i', v)
        elif t == 4: w('q', v)
        elif t == 5: w('f', v)
        elif t == 6: w('d', v)
        elif t == 7: w('i', len(v[1])); out.extend(v[1])
        elif t == 8: wstr(v)
        elif t == 9:
            _, et, items = v; w('b', et); w('i', len(items))
            for it in items: payload(et, it)
        elif t == 10:
            for k, (tt, vv) in v.items(): w('b', tt); wstr(k); payload(tt, vv)
            w('b', 0)
        elif t == 11: w('i', len(v[1])); [w('i', x) for x in v[1]]
        elif t == 12: w('i', len(v[1])); [w('q', x) for x in v[1]]
    w('b', 10); wstr(name); payload(10, root)
    open(path, 'wb').write(struct.pack('<ii', ver, len(out)) + bytes(out))
