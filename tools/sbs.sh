#!/bin/sh
# sbs.sh <rigdir> <movie> <seg> <out.mp4> <tag:label>...: the given AVI segment of each recording stacked vertically,
# labelled, 2x nearest, H.264. All recordings come from the same movie, so frame n is the same movie frame.
rig=$1; m=$2; seg=$3; out=$4; shift 4
in=""; f=""; i=0
for tl in "$@"; do tag=${tl%%:*}; lab=${tl#*:}
  in="$in -i $rig/$tag-$m/${m}_$(printf %03d $seg).avi"
  f="$f[$i:v]scale=iw*2:ih*4:flags=neighbor,drawtext=text='$lab':fontcolor=white:box=1:boxcolor=black@0.7:x=8:y=8:fontsize=28[v$i];"
  i=$((i+1)); done
st=""; j=0; while [ $j -lt $i ]; do st="$st[v$j]"; j=$((j+1)); done
ffmpeg -v error -y $in -filter_complex "${f}${st}vstack=inputs=$i,format=yuv420p" -c:v libx264 -crf 18 -preset slow -r 60000/1001 "$out"
