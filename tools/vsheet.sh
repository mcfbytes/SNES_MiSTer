#!/bin/sh
# vsheet.sh <rigdir> <movie> <y0> <h> <out.png> <label=tag,...> <name:a:b>...: sheet2.py once per window, stacked
# vertically (one block per window, one row per core). CW/X0/VS pass through to sheet2.py.
d=$(dirname "$0"); rig=$1; m=$2; y0=$3; h=$4; out=$5; cores=$6; shift 6
parts=""; i=0
for w in "$@"; do p="$out.w$i.png"; python3 "$d/sheet2.py" "$rig" "$m" "$y0" "$h" "$p" "$cores" "$w" >/dev/null; parts="$parts $p"; i=$((i+1)); done
convert $parts -background white -append "$out"; rm -f $parts; rm -rf "$out".w*.png.d
echo "$out"
