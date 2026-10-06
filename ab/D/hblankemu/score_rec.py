#!/usr/bin/env python3
"""score_rec.py <recdir> <label> [f0 f1]: distinct frame states of a tasty HblankEmuTest recording (movie frames
f0..f1, default 300..900), each scored against hardware-aligned.pgm (paulb_nl's photo, scaled to 256x224 and thresholded). Writes <recdir>/state-N.pgm."""
import sys, subprocess, collections, hashlib, glob
import os
D = os.path.dirname(os.path.abspath(__file__)) + '/'
rec, label = sys.argv[1], sys.argv[2]
f0, f1 = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (300, 900)
hw = open(D + 'hardware-aligned.pgm', 'rb').read(); hw = hw[hw.index(b'255\n') + 4:]
rows = [l.split('\t') for l in open(glob.glob(rec + '/*.frames.tsv')[0])][1:]
avis = sorted(glob.glob(rec + '/*.avi'))
def half(fr):  # 512 -> 256 wide (pixels doubled), threshold
    return bytes(1 if fr[y * 512 + 2 * x] > 100 else 0 for y in range(224) for x in range(256))
frames = {}
for seg, avi in enumerate(avis):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', avi, '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
    w, h = 512, 224; n = len(raw) // (w * h)
    for r in rows:
        if int(r[8]) == seg and f0 <= int(r[4]) <= f1 and int(r[9]) < n:
            a = int(r[9]); frames[int(r[4])] = raw[a * w * h:(a + 1) * w * h]
states = collections.OrderedDict()
for mf in sorted(frames):
    k = hashlib.md5(half(frames[mf])).hexdigest()
    states.setdefault(k, []).append(mf)
print(f'{label}: {len(frames)} frames {f0}-{f1}, {len(states)} distinct states')
for i, (k, mfs) in enumerate(sorted(states.items(), key=lambda kv: -len(kv[1]))):
    b = half(frames[mfs[0]]); best = None
    for dy in range(-3, 4):
        for dx in range(-4, 5):
            bad = 0
            for y in range(8, 216):
                yy = y + dy
                for x in range(16, 240):
                    if b[yy * 256 + x + dx] != (hw[y * 256 + x] > 100): bad += 1
            if best is None or bad < best[0]: best = (bad, dy, dx)
    open(f'{rec}/state-{i}.pgm', 'wb').write(b'P5 256 224 255\n' + bytes(255 * v for v in b))
    print(f'  state {i}: {len(mfs)} frames (first {mfs[0]}), mismatch vs photo {best[0]} px at dy={best[1]} dx={best[2]}')
