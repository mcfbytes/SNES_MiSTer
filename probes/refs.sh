#!/bin/sh
# refs.sh: regenerate ref-{bus,irq}[-pal].json from bsnes2014-accuracy, rebuild, and cross-check MesenCE.
# LRRUN = lrrun built from lrrun.c (a minimal headless libretro runner), BSNES = the bsnes2014 accuracy core, MESEN = MesenCE 2.2.1.

cd "$(dirname "$0")"
for pal in 0 1; do for v in bus irq; do
  n=$([ $v = bus ] && echo 23 || echo 18); sfx=$([ $pal = 1 ] && echo -pal || echo ""); rom=$([ $pal = 1 ] && echo pal-)${v}probe.sfc
  rm -f ref-$v$sfx.json; PAL=$pal python3 gen.py $v >/dev/null
  d=lr-$v$sfx; mkdir -p $d; (cd $d && ${LRRUN:-lrrun} ${BSNES:-bsnes2014_accuracy_libretro.so} ../$rom 900 . >/dev/null 2>&1)
  python3 extract.py $d/wram.bin ref-$v$sfx.json $n > $d/extract.txt
  PAL=$pal python3 gen.py $v >/dev/null
  DISPLAY= WAYLAND_DISPLAY= timeout 120 ${MESEN:-Mesen} --testRunner ../mesen-wram.lua $rom --enableStdout 2>/dev/null | grep '^WRAM' > $d/mesen.txt
  python3 - "$d/mesen.txt" ref-$v$sfx.json $n <<'PY'
import json, re, sys
w = bytes.fromhex(re.search(r'WRAM ([0-9A-F]+)', open(sys.argv[1]).read()).group(1)); ref = json.load(open(sys.argv[2]))
bad = [i for i in range(int(sys.argv[3])) if (min(w[r*256+i*8] | w[r*256+i*8+1] << 8 for r in range(16)),
       max(w[r*256+i*8] | w[r*256+i*8+1] << 8 for r in range(16))) != tuple(ref[i][:2])]
print(sys.argv[2], "MesenCE vs bsnes:", "all rows equal" if not bad else f"rows differ {bad}")
PY
done; done
rm -f out.sfc
