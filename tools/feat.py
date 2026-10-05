#!/usr/bin/env python3
"""feat.py <video> <x0> <x1> <y0> <rows_per_line> <out.tsv> [lines]: per frame, every line holding a force-blank bar.
Columns: frame, line, black start, black end, green end, N (red/white right after the green run), all in SNES pixels."""
import subprocess, sys
import numpy as np
v, x0, x1, y0, rpl, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
W, H = (int(v) for v in subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", v], capture_output=True, text=True).stdout.strip().split(","))
NL = int(sys.argv[7]) if len(sys.argv) > 7 else 224
sc = (x1 - x0) / 256
cols = np.array([int(x0 + (x + 0.5) * sc) for x in range(256)])
rows = np.array([int(y0 + (l + 0.5) * rpl) for l in range(NL)])
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", v, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
f = open(out, "w"); f.write("frame\tline\tbstart\tbend\tgend\tN\n"); n = 0
while True:
    buf = p.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    a = np.frombuffer(buf, np.uint8).reshape(H, W, 3)[rows][:, cols].astype(int)
    s = a.sum(axis=2)
    blk = s < 90
    grn = (a[..., 1] > 170) & (a[..., 0] < 100) & (a[..., 2] < 100)
    redw = ((a[..., 0] > 170) & (a[..., 1] < 110)) | (s > 690)
    for l in range(NL):
        b = blk[l]
        if b[40:140].sum() < 90: continue          # the bar: mostly black across the middle
        xs = np.nonzero(b[:200])[0]
        # bar run containing x=100
        e = 100
        while e < 255 and b[e + 1]: e += 1
        st = 100
        while st > 0 and b[st - 1]: st -= 1
        g = e + 1
        while g < 255 and grn[l, g]: g += 1
        N = int(redw[max(0, l - 3):l + 4, g:g + 14].any()) if g > e + 1 else 0
        f.write(f"{n}\t{l}\t{st}\t{e + 1}\t{g}\t{N}\n")
    n += 1
print(n, "frames")
