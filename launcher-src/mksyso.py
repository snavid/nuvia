# Build a COFF .syso containing RT_ICON + RT_GROUP_ICON resources from an .ico
import struct, sys
ico = open(sys.argv[1], 'rb').read()
_, _, n = struct.unpack_from('<HHH', ico, 0)
icons, grp = [], struct.pack('<HHH', 0, 1, n)
for i in range(n):
    w, h, c, r, planes, bits, size, off = struct.unpack_from('<BBBBHHII', ico, 6 + 16 * i)
    icons.append(ico[off:off + size])
    grp += struct.pack('<BBBBHHIH', w, h, c, r, planes, bits, size, i + 1)

resources = [(3, i + 1, d) for i, d in enumerate(icons)] + [(14, 1, grp)]
types = sorted({t for t, _, _ in resources})
DIR, ENT, DATA = 16, 8, 16
def dirhdr(k): return struct.pack('<IIHHHH', 0, 0, 0, 0, 0, k)

# layout offsets
off = DIR + ENT * len(types)
type_off = {}
for t in types:
    type_off[t] = off
    off += DIR + ENT * sum(1 for r in resources if r[0] == t)
lang_off = {}
for r in resources:
    lang_off[r[:2]] = off; off += DIR + ENT
dentry_off = {}
for r in resources:
    dentry_off[r[:2]] = off; off += DATA
data_off = {}
for r in resources:
    off = (off + 7) & ~7
    data_off[r[:2]] = off; off += len(r[2])

sec = bytearray(off)
def put(o, b): sec[o:o + len(b)] = b
put(0, dirhdr(len(types)))
for i, t in enumerate(types):
    put(DIR + ENT * i, struct.pack('<II', t, 0x80000000 | type_off[t]))
    rs = [r for r in resources if r[0] == t]
    put(type_off[t], dirhdr(len(rs)))
    for j, r in enumerate(rs):
        put(type_off[t] + DIR + ENT * j, struct.pack('<II', r[1], 0x80000000 | lang_off[r[:2]]))
relocs = []
for r in resources:
    k = r[:2]
    put(lang_off[k], dirhdr(1))
    put(lang_off[k] + DIR, struct.pack('<II', 0x0409, dentry_off[k]))
    put(dentry_off[k], struct.pack('<IIII', data_off[k], len(r[2]), 0, 0))
    relocs.append(dentry_off[k])
    put(data_off[k], r[2])

hdr_size = 20 + 40
raw_ptr = hdr_size
reloc_ptr = raw_ptr + len(sec)
sym_ptr = reloc_ptr + 10 * len(relocs)
out = struct.pack('<HHIIIHH', 0x8664, 1, 0, sym_ptr, 1, 0, 0)
out += struct.pack('<8sIIIIIIHHI', b'.rsrc', 0, 0, len(sec), raw_ptr, reloc_ptr, 0, len(relocs), 0, 0x40000040)
out += bytes(sec)
for r in relocs:
    out += struct.pack('<IIH', r, 0, 3)  # IMAGE_REL_AMD64_ADDR32NB
out += struct.pack('<8sIhHBB', b'.rsrc', 0, 1, 0, 3, 0)
out += struct.pack('<I', 4)
open(sys.argv[2], 'wb').write(out)
