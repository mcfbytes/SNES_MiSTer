#!/usr/bin/env python3
"""framediff.py <recA> <recB> [max_report]: for movie frames whose hashes differ, decode both AVIs and report per frame
the differing pixel count and the lines (0-based, of the core's picture) that differ; then a summary by line set."""
import glob, os, subprocess, sys
from collections import Counter
import numpy as np
def load(d):
    tsv = glob.glob(os.path.join(d, "*.frames.tsv"))[0]
    m = {}
    for l in list(open(tsv))[1:]:
        c = l.rstrip("\n").split("\t")
        if c[3] == "none" and c[4] != "-1" and c[9] != "-1": m.setdefault(int(c[4]), (c[5], int(c[9]), int(c[7])))
    return m, glob.glob(os.path.join(d, "*_000.avi"))[0]
def frames(avi, h):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", avi, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = 0
    while True:
        b = p.stdout.read(512 * h * 3)
        if len(b) < 512 * h * 3: break
        yield n, np.frombuffer(b, np.uint8).reshape(h, 512, 3)
        n += 1
(a, aa), (b, ba) = load(sys.argv[1]), load(sys.argv[2])
diff = sorted(f for f in set(a) & set(b) if a[f][0] != b[f][0])
want_a = {a[f][1]: f for f in diff}; want_b = {b[f][1]: f for f in diff}
h = a[diff[0]][2] if diff else 224
fa = {want_a[n]: x.copy() for n, x in frames(aa, h) if n in want_a}
fb = {want_b[n]: x.copy() for n, x in frames(ba, h) if n in want_b}
summary = Counter(); rep = []
for f in diff:
    if f not in fa or f not in fb: continue
    d = (fa[f] != fb[f]).any(axis=2)
    lines = np.nonzero(d.any(axis=1))[0]
    key = f"{lines.min()}-{lines.max()}" if len(lines) else "none"
    summary[(key, len(lines))] += 1
    rep.append((f, int(d.sum()), key, len(lines)))
print(f"{len(diff)} differing frames")
for (key, n), c in summary.most_common(12): print(f"  lines {key} ({n} lines): {c} frames")
big = sorted(rep, key=lambda r: -r[1])[:int(sys.argv[3]) if len(sys.argv) > 3 else 5]
for f, px, key, n in big: print(f"  frame {f}: {px} px, lines {key}")
