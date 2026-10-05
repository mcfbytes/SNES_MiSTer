#!/usr/bin/env python3
"""probeband.py <n_rows> <bsnes.png> <mesen.png> <core.png>...: read the probe screens' "got" Hmin/Hmax per row by
matching 8x8 cells against the font, and count rows of each core inside the bsnes..Mesen band (min of the two Hmins
to max of the two Hmaxes). FONT = undisbeliever's font-1bpp-tiles.tiles."""
import os, sys
from PIL import Image
FONT = os.environ.get("FONT", "/mnt/source/snes-tests/snes-test-roms/gen/textbuffer/font-1bpp-tiles.tiles")
f1 = open(FONT, "rb").read()
def tile(c):
    if c.isdigit(): return 0x01 + ord(c) - ord("0")
    return 0x0B + ord(c) - ord("A")
glyph = {f1[tile(c) * 8:tile(c) * 8 + 8]: c for c in "0123456789ABCDEF"}
def read(path, n):
    im = Image.open(path).convert("RGB")
    sx, oy = im.size[0] // 256, 7 if im.size[1] == 239 else 0
    def cell(r, c):
        bits = bytes(sum(0x80 >> x for x in range(8) if sum(im.getpixel(((c * 8 + x) * sx, r * 8 + y + oy))) > 120)
                     for y in range(8))
        return glyph.get(bits, "?")
    rows = []
    for r in range(3, 3 + n):
        s = "".join(cell(r, c) for c in range(13, 21))
        rows.append((int(s[0:3], 16), int(s[4:7], 16)) if "?" not in s[0:3] + s[4:7] else None)
    return rows
n = int(sys.argv[1])
b, m = read(sys.argv[2], n), read(sys.argv[3], n)
band = [(min(x[0], y[0]), max(x[1], y[1])) for x, y in zip(b, m)]
print("band", " ".join(f"{lo:X}-{hi:X}" for lo, hi in band))
for p in sys.argv[4:]:
    got = read(p, n)
    ins = [g is not None and lo <= g[0] and g[1] <= hi for g, (lo, hi) in zip(got, band)]
    print(p, "".join("o" if i else "x" for i in ins), sum(ins), "of", n, "inside")
