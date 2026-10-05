#!/usr/bin/env python3
"""states.py <feat.tsv>: steady states (runs of frames with the same bar top line and black start), with the spread
of bar ends, green ends and the share of frames showing the N."""
import collections, sys
rows = collections.defaultdict(list)
for line in list(open(sys.argv[1]))[1:]:
    fr, l, bs, be, ge, n = map(int, line.split("\t"))
    rows[fr].append((l, bs, be, ge, n))
seq = []
for fr in sorted(rows):
    r = rows[fr]; top = min(x[0] for x in r)
    first = [x for x in r if x[0] == top][0]
    anyN = max(x[4] for x in r)
    seq.append((fr, top, first[1], first[2], first[3], anyN))
states = []
for fr, top, bs, be, ge, n in seq:
    if states and states[-1]["top"] == top and abs(states[-1]["bs"] - bs) <= 1:
        s = states[-1]
    else:
        s = {"top": top, "bs": bs, "f0": fr, "be": collections.Counter(), "ge": collections.Counter(), "N": 0, "n": 0}
        states.append(s)
    s["be"][be] += 1; s["ge"][ge] += 1; s["N"] += n; s["n"] += 1; s["f1"] = fr
for s in states:
    if s["n"] < 20: continue
    be = "/".join(f"{k}x{v}" for k, v in sorted(s["be"].items()) if v > 2)
    ge = "/".join(f"{k}" for k, v in sorted(s["ge"].items()) if v > 2)
    print(f"f{s['f0']:5d}-{s['f1']:5d} line {s['top']:3d} bstart {s['bs']:3d}  bend {be:28s} gend {ge:12s} N {s['N']}/{s['n']}")
