#!/usr/bin/env python3
"""hashcmp.py a.tsv b.tsv: compare tasty hash logs by movie_frame (timestamps ignored)."""
import sys
def load(p):
    rows = {}
    with open(p) as f:
        cols = f.readline().rstrip("\n").split("\t")
        mi, hi, di = cols.index("movie_frame"), cols.index("hash"), cols.index("dup_reason")
        for line in f:
            v = line.rstrip("\n").split("\t")
            if len(v) > hi and v[mi] not in ("", "-1") and v[di] == "none":
                rows.setdefault(int(v[mi]), v[hi])
    return rows
a, b = load(sys.argv[1]), load(sys.argv[2])
common = sorted(set(a) & set(b))
diff = [f for f in common if a[f] != b[f]]
print(f"frames a={len(a)} b={len(b)} common={len(common)} differing={len(diff)}" +
      (f" first={diff[0]} last={diff[-1]}" if diff else " IDENTICAL"))
sys.exit(1 if diff else 0)
