#!/usr/bin/env python3
"""sheet2.py <rigdir> <movie> <y0> <h> <out.png> <label=tag,...> <name:a:b>...
One row per core, one block per movie-frame window: every distinct frame of that window (the 3-phase IRQ cycle),
cropped to SNES lines y0..y0+h, 3x nearest, each captioned with its share of the window's frames.
CW/X0 = crop width/left edge in recorded pixels (512 per line), VS = vertical scale; env vars."""
import collections, os, subprocess, sys
rig, m, y0, hh, out, cores = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6]
wins = [w.split(":") for w in sys.argv[7:]]
CW, VS, X0 = int(os.environ.get("CW", 400)), int(os.environ.get("VS", 3)), int(os.environ.get("X0", 0))
tmp = out + ".d"; os.makedirs(tmp, exist_ok=True)
def rows(tag):
    r = {}
    with open(f"{rig}/{tag}-{m}/{m}.frames.tsv") as f:
        ix = {c: i for i, c in enumerate(f.readline().rstrip("\n").split("\t"))}
        for line in f:
            v = line.rstrip("\n").split("\t")
            if v[ix["dup_reason"]] == "none":
                r.setdefault(int(v[ix["movie_frame"]]), (v[ix["hash"]], int(v[ix["segment"]]), int(v[ix["avi_frame"]])))
    return r
def cmd(*a): subprocess.run(list(a), check=True)
lines = []
hdr = [f"{tmp}/hdr-lab.png"]; cmd("convert", "-size", "200x40", "xc:white", hdr[0])
for name, a, b in wins:
    p = f"{tmp}/hdr-{name}.png"
    cmd("convert", "-size", f"{3*(800+6)+8}x40", "xc:white", "-gravity", "center", "-pointsize", "26", "-annotate", "0", name, p)
    hdr.append(p)
cmd("convert", *hdr, "+append", f"{tmp}/hdr.png"); lines.append(f"{tmp}/hdr.png")
for pair in cores.split(","):
    label, tag = pair.split("=")
    r = rows(tag); blocks = []
    for name, a, b in wins:
        cnt = collections.Counter(); first = {}
        for f in range(int(a), int(b)):
            if f not in r: continue
            cnt[r[f][0]] += 1; first.setdefault(r[f][0], f)
        tot = sum(cnt.values()); crops = []
        for h, c in sorted(cnt.items(), key=lambda kv: first[kv[0]])[:3]:
            if c * 20 < tot: continue
            _, seg, af = r[first[h]]
            p = f"{tmp}/{tag}-{name}-{first[h]}.png"
            cmd("ffmpeg", "-v", "error", "-y", "-i", f"{rig}/{tag}-{m}/{m}_{seg:03d}.avi", "-vf",
                f"select=eq(n\\,{af}),crop={CW}:{hh}:{X0}:{y0},scale=800:{hh*VS}:flags=neighbor", "-vframes", "1", p)
            cmd("convert", p, "-gravity", "south", "-background", "white", "-splice", "0x24", "-pointsize", "20",
                "-annotate", "+0+2", f"{c}/{tot} frames", p)
            crops.append(p)
        while len(crops) < 3:
            p = f"{tmp}/blank.png"; cmd("convert", "-size", f"800x{hh*VS+24}", "xc:white", p); crops.append(p)
        blk = f"{tmp}/{tag}-{name}-blk.png"
        cmd("convert", *crops, "-bordercolor", "white", "-border", "3", "+append", "-bordercolor", "gray60", "-border", "4", blk)
        blocks.append(blk)
    lab = f"{tmp}/{tag}-lab.png"
    cmd("convert", "-size", f"200x{hh*VS+24+14}", "xc:white", "-gravity", "center", "-pointsize", "24", "-annotate", "0", label, lab)
    row = f"{tmp}/{tag}-row.png"; cmd("convert", lab, *blocks, "+append", row); lines.append(row)
cmd("convert", *lines, "-background", "white", "-append", out)
print(out)
