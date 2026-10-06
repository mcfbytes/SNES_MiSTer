#!/usr/bin/env python3
"""sweepmeasure.py <png>...: the numbers B's sweep table quotes, per screenshot.
hvdma_max: pixels other than the dominant (green) colour. inidisp_brightness_delay: on each bright stripe row, the dots where
the brightness turns off and on (the lines where a stripe starts or ends). inidisp_enable_display_mid_frame: the first lit dot on line 88."""
import sys, re, collections
import numpy as np
from PIL import Image
for p in sys.argv[1:]:
    a = np.asarray(Image.open(p).convert("RGB")).astype(int); k = a[:, :, 0] * 65536 + a[:, :, 1] * 256 + a[:, :, 2]
    if "hvdma_max" in p:
        print(p, "non-green px", int((k != np.bincount(k.ravel()).argmax()).sum()))
    elif "brightness_delay" in p:
        on, off = set(), set()
        for y in range(a.shape[0]):
            row = a[y].sum(axis=1); ch = np.nonzero(row[1:] != row[:-1])[0]
            if len(ch): (on if row[ch[0] + 1] > row[ch[0]] else off).add(int(ch[0] + 1) // 2)
        print(p, "brightness off at dots", sorted(off), "on at dots", sorted(on))
    elif "enable_display_mid_frame" in p:
        lit = np.nonzero(a[88].sum(axis=1) > 30)[0]
        print(p, "line 88 first lit dot", int(lit[0]) // 2 if len(lit) else None)
# hdmaen_latch_test(_2): red lines per band (8 channels) and in total
for p in sys.argv[1:]:
    if "hdmaen_latch_test" not in p: continue
    a = np.asarray(Image.open(p).convert("RGB")).astype(int)
    red = (a[:, :, 0] > 150) & (a[:, :, 1] < 100)
    rows = red.mean(axis=1) > 0.5
    ys = np.nonzero(rows)[0]; bands = []
    for i, y in enumerate(ys):
        if i == 0 or y - ys[i - 1] > 4: bands.append(0)
        bands[-1] += 1
    print(p, "red lines", int(rows.sum()), "per channel band", bands)
