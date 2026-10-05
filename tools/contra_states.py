#!/usr/bin/env python3
"""contra_states.py <rec dir> <movie>: per window (start, R1..R3) of contra_last.lsmv, each distinct frame's last line
(y 238): first lit x in SNES pixels and whether a tile (non-magenta, lit) sits at x 50-62; with frame shares."""
import collections, subprocess, sys
import numpy as np
d, m = sys.argv[1], sys.argv[2]
WINS = [("start", 540, 650), ("R1", 655, 770), ("R2", 775, 890), ("R3", 895, 1010)]
r = {}
with open(f"{d}/{m}.frames.tsv") as f:
    ix = {c: i for i, c in enumerate(f.readline().rstrip("\n").split("\t"))}
    for line in f:
        v = line.rstrip("\n").split("\t")
        if v[ix["dup_reason"]] == "none":
            r.setdefault(int(v[ix["movie_frame"]]), (v[ix["hash"]], int(v[ix["segment"]]), int(v[ix["avi_frame"]])))
out = []
for name, a, b in WINS:
    cnt = collections.Counter(); first = {}
    for fr in range(a, b):
        if fr in r: cnt[r[fr][0]] += 1; first.setdefault(r[fr][0], fr)
    tot = sum(cnt.values()); parts = []
    for h, c in sorted(cnt.items(), key=lambda kv: first[kv[0]]):
        if c * 20 < tot: continue
        _, seg, af = r[first[h]]
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{d}/{m}_{seg:03d}.avi", "-vf", f"select=eq(n\\,{af})",
                              "-vframes", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
        a3 = np.frombuffer(raw, np.uint8).reshape(239, 512, 3)[238, 1::2].astype(int)
        lit = np.nonzero(a3.sum(axis=1) > 24)[0]
        x0 = int(lit[0]) if len(lit) else -1
        mag = (a3[:, 0] > 150) & (a3[:, 2] > 150) & (a3[:, 1] < 100)
        tile = bool(((a3[50:63].sum(axis=1) > 24) & ~mag[50:63]).any())
        parts.append(f"x{x0}{' TILE' if tile else ''} {c}/{tot}")
    out.append(f"{name}: " + ", ".join(parts))
print(" | ".join(out))
