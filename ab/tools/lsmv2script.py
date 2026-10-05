#!/usr/bin/env python3
"""lsmv2script.py <movie.lsmv>: pad-1 input spans "a-b:keys" (a <= frame < b, as mklsmv.py and lrrun2; keys from BYsSudlrAXLR), and the frame count."""
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
rows = [l for l in z.read("input").decode().splitlines() if l.startswith("F")]
ORDER = "BYsSudlrAXLR"
spans, cur, start = [], "", 0
for i, l in enumerate(rows + ["F. 0 0|............"]):
    pad = l.split("|")[1]
    k = "".join(c for c in pad if c != ".")
    if k != cur:
        if cur: spans.append(f"{start}-{i}:{cur}")
        cur, start = k, i
print(",".join(spans) or "none", len(rows))
