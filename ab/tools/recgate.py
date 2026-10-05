#!/usr/bin/env python3
"""recgate.py <tasty.out> <frames.tsv> [from to]: the quality gate for one tasty recording. Prints a one-line counters
summary and FAIL if any frame was missed, torn, dropped, late or lost, or if the hash log has an encoder duplicate or a
core_frame gap inside [from, to) movie frames (default: the whole log)."""
import json, sys
out, tsv = sys.argv[1], sys.argv[2]
lo, hi = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (None, None)
rec = tas = None
for line in open(out, errors="replace"):
    line = line.strip()
    if not line.startswith("{"): continue
    try: j = json.loads(line)
    except ValueError: continue
    if j.get("t") == "rec" and "captured" in j: rec = j
    if j.get("t") == "tas" and "late" in j: tas = j
bad = []
for k in ("missed", "torn", "backpressure", "wdrop", "werr", "avi_drop", "gaps", "drift"):
    if rec is None or rec.get(k, 0): bad.append(f"{k}={rec.get(k) if rec else '?'}")
for k in ("late", "lost", "underruns"):
    if tas is None or tas.get(k, 0): bad.append(f"{k}={tas.get(k) if tas else '?'}")
rows = [l.rstrip("\n").split("\t") for l in open(tsv)][1:]
dups = gaps = 0
prev = None
for c in rows:
    cf, mf = int(c[0]), int(c[4])
    inwin = lo is None or (mf >= 0 and lo <= mf < hi)
    if inwin and c[3] != "none": dups += 1
    if prev is not None and cf != prev + 1 and inwin: gaps += 1
    prev = cf
if dups: bad.append(f"tsv_dups={dups}")
if gaps: bad.append(f"core_frame_gaps={gaps}")
gm = tas.get("gap_max_us", 0) / 1000 if tas else -1
s = (f"captured {rec['captured'] if rec else '?'}, missed {rec.get('missed') if rec else '?'}, torn {rec.get('torn') if rec else '?'}, "
     f"dups {rec.get('dups') if rec else '?'} (in window {dups}), late {tas.get('late') if tas else '?'}, lost {tas.get('lost') if tas else '?'}, "
     f"gap_max {gm:.1f} ms")
print(("FAIL " + " ".join(bad) + " | " if bad else "ok | ") + s)
