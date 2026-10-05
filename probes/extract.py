#!/usr/bin/env python3
"""wram.bin -> per probe [Hmin, Hmax, V(round 0), wm(round 0)] over 16 rounds; prints the H histogram."""
import json, sys
from collections import Counter
w = open(sys.argv[1], "rb").read()
out = []
for i in range(int(sys.argv[3]) if len(sys.argv) > 3 else 23):
    hs, vs = [], set()
    for r in range(16):
        b = 0x400 + r * 0x100 + i * 8
        hs.append(w[b] | w[b + 1] << 8); vs.add(w[b + 2] | w[b + 3] << 8)
    b = 0x400 + i * 8
    out.append([min(hs), max(hs), w[b + 2] | w[b + 3] << 8, w[b + 4]])
    print(f"{i:02d} H {dict(sorted(Counter(hs).items()))} V {sorted(vs)} wm={w[b + 4]:02X}")
if len(sys.argv) > 2:
    json.dump(out, open(sys.argv[2], "w"))
