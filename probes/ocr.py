#!/usr/bin/env python3
"""Read the busprobe screen back to text by matching 8x8 cells against the font (512- or 256-wide shots)."""
import sys
from PIL import Image
f1 = open("../snes-test-roms/gen/textbuffer/font-1bpp-tiles.tiles", "rb").read()
chars = {}
for c in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz=*-:/ ":
    import gen
    t = gen.tile(c)
    chars[f1[t * 8:t * 8 + 8]] = c
im = Image.open(sys.argv[1]).convert("RGB")
sx = im.size[0] // 256
for row in range(28):
    line, cols = "", []
    for col in range(32):
        bits, color = [], None
        for y in range(8):
            b = 0
            for x in range(8):
                p = im.getpixel(((col * 8 + x) * sx, row * 8 + y))
                if sum(p) > 120:
                    b |= 0x80 >> x
                    color = color or p
            bits.append(b)
        ch = chars.get(bytes(bits), "?")
        line += ch
        cols.append("r" if color and color[0] > 150 and color[1] < 100 else ".")
    print(line, "".join(cols) if "r" in cols else "")
