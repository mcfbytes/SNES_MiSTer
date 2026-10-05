#!/usr/bin/env python3
"""rowcolor.py <shot.png> <first_row> <n> <col0> <col1>: per text row, G (green), R (red) or - from the 8x8 cells in
columns col0..col1 (256-dot grid; 512-wide shots are halved, Mesen's 239-line buffer is offset 7 lines)."""
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGB")
r0, n, c0, c1 = map(int, sys.argv[2:6])
sx = im.size[0] // 256
oy = 7 if im.size[1] == 239 else 0
out = ""
for r in range(r0, r0 + n):
    red = green = 0
    for y in range(r * 8 + oy, r * 8 + 8 + oy):
        for x in range(c0 * 8, (c1 + 1) * 8):
            p = im.getpixel((x * sx, y))
            red += p[0] > 150 and p[1] < 100
            green += p[1] > 150 and p[0] < 100
    out += "R" if red > green else "G" if green else "-"
print(out, out.count("G"), "of", n)
