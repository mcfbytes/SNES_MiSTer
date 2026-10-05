#!/bin/sh
# emumovie.sh <rom> <movie.lsmv> <dumps> <outdir>: replay the movie's pad-1 input on bsnes v115.1 libretro (accurate PPU, no entropy, no overscan crop; lrrun2) and
# MesenCE 2.2.1 (mesen-movie.py); PNGs of the listed frames (0-based) in <outdir>/bsnes/ and <outdir>/mesen/.
d=$(dirname "$(readlink -f "$0")"); rom=$(readlink -f "$1"); out=$4
set -- "$rom" "$2" "$3" "$out" $(python3 "$d/lsmv2script.py" "$2")
sc=$5; mkdir -p "$out/bsnes"; last=$(echo "$3" | tr , '\n' | sort -n | tail -1)
(cd "$out/bsnes" && LR_VARS=${LR_VARS:-bsnes_ppu_fast=OFF,bsnes_entropy=None,bsnes_ppu_overscan_v=0} ${LRRUN2:-$d/lrrun2} ${BSNES:-/mnt/source/tools/libretro/bsnes_libretro.so} "$rom" $((last + 1)) . "$sc" "$3" 2>/dev/null)
for p in "$out"/bsnes/f*.ppm; do convert "$p" "${p%.ppm}.png" && rm -f "$p"; done; rm -f "$out"/bsnes/last.ppm "$out"/bsnes/wram.bin
python3 "$d/mesen-movie.py" "$rom" "$sc" "$3" "$out/mesen" >/dev/null
ls "$out/bsnes" "$out/mesen" | tr '\n' ' '; echo
