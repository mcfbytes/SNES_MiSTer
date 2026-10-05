#!/bin/sh
# emushot.sh <rom> <frames> <outdir>: screen after <frames> frames on bsnes 2014 accuracy (lrrun) and MesenCE 2.2.1
# (--testRunner). Writes <outdir>/bsnes.png and <outdir>/mesen.png. LRRUN/BSNES/MESEN override the tool paths.
rom=$(readlink -f "$1"); n=$2; out=$3; d=$(dirname "$(readlink -f "$0")")
mkdir -p "$out"; out=$(readlink -f "$out")
(cd "$out" && ${LRRUN:-/mnt/source/tools/libretro/lrrun} ${BSNES:-/mnt/source/tools/libretro/bsnes2014_accuracy_libretro.so} "$rom" "$n" . 2>/dev/null \
  && convert last.ppm bsnes.png && rm -f last.ppm)
sed "s/^local frames = .*/local frames = $n/" "$d/mesen-shot.lua" > "$out/mesen-shot.lua"
DISPLAY= WAYLAND_DISPLAY= timeout 300 ${MESEN:-/mnt/source/tools/mesence/Mesen} --testRunner "$out/mesen-shot.lua" "$rom" --enableStdout > "$out/mesen.txt" 2>/dev/null
python3 "$d/mesen2png.py" "$out/mesen.txt" "$out/mesen.png" >/dev/null && grep -o '^WRAM [0-9A-F]*' "$out/mesen.txt" > "$out/mesen-wram.txt"; rm -f "$out/mesen.txt"
ls "$out"
