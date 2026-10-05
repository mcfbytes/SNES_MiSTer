#!/bin/sh
# rigrun.sh <tag> <rbf> <name>...: tasty play <name>.lsmv with <name>.sfc on one core, recording to <tag>-<name>/
# (AVI + frames.tsv hash log). Runs on the DE10-Nano from the directory holding the ROMs and movies.
D=$(cd "$(dirname "$0")" && pwd); T=${TASTY:-/media/fat/tasty/tasty}; tag=$1; rbf=$2; shift 2
for r in "$@"; do
  rm -rf "$D/$tag-$r"
  $T play "$D/$r.lsmv" --rom "$D/$r.sfc" --core "$rbf" --record "$D/$tag-$r" --linger 0 --no-splash > "$D/$tag-$r.out" 2>&1
  echo "$tag $r rc=$? $(grep -o '"captured":[0-9]*' "$D/$tag-$r.out" | tail -1) $(grep -o '"late":[0-9]*' "$D/$tag-$r.out" | tail -1)"
done
