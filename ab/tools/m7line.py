#!/usr/bin/env python3
"""m7line.py <recdir|rows.txt>: paulb-nl's #274 mode 7 test. For each H-IRQ window of the movie (H=0, then R steps
H to 1..8 every 60 frames from 120, select resets to 0 at 660, L sets $FFFF at 720), the share of frames whose line 36
(the line above the second row of squares) is black: the M7VOFS write landed in time. Movie frames 0-899."""
import glob, os, subprocess, sys
import numpy as np
d = sys.argv[1]
def frames_avi():
    tsv = glob.glob(os.path.join(d, "*.frames.tsv"))[0]
    rows = [l.rstrip("\n").split("\t") for l in open(tsv)][1:]
    avi = glob.glob(os.path.join(d, "*_000.avi"))[0]
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", avi, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    fs = np.frombuffer(raw, np.uint8).reshape(-1, 224, 512, 3)
    out = {}
    for c in rows:
        mf, af = int(c[4]), int(c[9])
        if mf >= 0 and af >= 0 and af < len(fs): out[mf] = fs[af][36]
    return out
if os.path.isfile(d):  # an emulator's "ROW <frame> <dark share>" log (lrrun2 LR_ROW / mesen-movie.py MESEN_ROW)
    fr = {int(a): float(b) for _, a, b in (l.split() for l in open(d) if l.startswith("ROW"))}
    black = lambda share: share > 0.5
else:
    fr = frames_avi()
    black = lambda line: (line.max(axis=1) < 40).mean() > 0.5  # most of the line is black
wins = [("H=0", 60, 120)] + [(f"H={k}", 120 + 60 * (k - 1) + 8, 120 + 60 * k) for k in range(1, 9)] + [("H=0 again", 668, 720), ("H=$FFFF", 728, 900)]
res = []
for name, a, b in wins:
    fs = [black(fr[f]) for f in range(a, b) if f in fr]
    res.append(f"{name}:{sum(fs)}/{len(fs)}")
print(d.rstrip("/").split("/")[-2] + "/" + os.path.basename(d.rstrip("/")) if os.path.isfile(d) else os.path.basename(d.rstrip("/")), " ".join(res))
