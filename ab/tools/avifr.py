#!/usr/bin/env python3
"""avifr.py <recdir> <movie_frame> <out.png>: the core picture tasty recorded for that movie frame (frames.tsv -> AVI)."""
import glob, os, subprocess, sys
d, mf, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
tsv = glob.glob(os.path.join(d, "*.frames.tsv"))[0]
stem = os.path.basename(tsv)[:-len(".frames.tsv")]
for line in open(tsv):
    c = line.rstrip("\n").split("\t")
    if c[4] == str(mf) and c[9] != "-1":
        seg, af = int(c[8]), int(c[9])
        avi = os.path.join(d, f"{stem}_{seg:03d}.avi")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", avi, "-vf", f"select=eq(n\\,{af})", "-frames:v", "1",
                        "-update", "1", out], check=True)
        print(out, "hash", c[5])
        break
else:
    sys.exit(f"movie frame {mf} not in {tsv}")
