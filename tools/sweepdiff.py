#!/usr/bin/env python3
"""sweepdiff.py <dir> <tagA> <tagB>: compare rr-<rom>-<tagA>.png vs rr-<rom>-<tagB>.png sweep screenshots.

Prints one row per ROM: identical / size mismatch / differing pixel count + bbox; summary at the end.
"""
import glob, os, sys
import numpy as np
from PIL import Image
d, a, b = sys.argv[1:4]
rows = []
for pa in sorted(glob.glob(os.path.join(d, f"rr-*-{a}.png"))):
    rom = os.path.basename(pa)[3:-len(a) - 5]
    pb = os.path.join(d, f"rr-{rom}-{b}.png")
    if not os.path.exists(pb):
        rows.append((rom, "missing-" + b, 0, None)); continue
    ia, ib = np.asarray(Image.open(pa).convert("RGB")), np.asarray(Image.open(pb).convert("RGB"))
    if ia.shape != ib.shape:
        rows.append((rom, f"size {ia.shape[1]}x{ia.shape[0]} vs {ib.shape[1]}x{ib.shape[0]}", -1, None)); continue
    m = (ia != ib).any(axis=2)
    n = int(m.sum())
    if n == 0:
        rows.append((rom, "same", 0, None)); continue
    ys, xs = np.nonzero(m)
    rows.append((rom, "diff", n, (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))))
for rom, k, n, bb in rows:
    if k != "same":
        print(f"{rom}\t{k}\t{n}\t{bb}")
from collections import Counter
print("summary:", dict(Counter(k.split()[0] for _, k, _, _ in rows)), "of", len(rows))
