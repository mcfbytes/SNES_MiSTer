#!/bin/sh
# mp4ab.sh <out.mp4> <label=recdir>...: tasty recordings side by side (2 per row; 3+ stack in rows), labelled, each frame
# doubled down (512x448), H.264. Every recording plays the same movie from power-on, so frame n is the same movie frame.
# FROM/TO (seconds) trim; COLS=1 stacks vertically.
out=$1; shift; in=""; f=""; i=0; cols=${COLS:-2}
for lr in "$@"; do lab=${lr%%=*}; dir=${lr#*=}
  avi=$(ls "$dir"/*_000.avi | head -1)
  in="$in ${FROM:+-ss $FROM} ${TO:+-to $TO} -i $avi"
  f="$f[$i:v]scale=512:448:flags=neighbor,setsar=1,drawtext=text='$lab':fontcolor=white:box=1:boxcolor=black@0.75:x=8:y=8:fontsize=24[v$i];"
  i=$((i+1)); done
if [ $i -le $cols ]; then st=""; j=0; while [ $j -lt $i ]; do st="$st[v$j]"; j=$((j+1)); done; lay="${st}hstack=inputs=$i:shortest=1"
  [ $cols = 1 ] && lay="${st}vstack=inputs=$i:shortest=1"
else lay=""; xs=""; j=0; while [ $j -lt $i ]; do lay="$lay[v$j]"; xs="$xs|$(( (j % cols) * 512 ))_$(( (j / cols) * 448 ))"; j=$((j+1)); done
  lay="${lay}xstack=inputs=$i:layout=${xs#|}:fill=white:shortest=1"; fi
ffmpeg -v error -y $in -filter_complex "${f}${lay},format=yuv420p" -an -c:v libx264 -crf ${CRF:-20} -preset slow -r 60000/1001 "$out"
ls -la "$out" | awk '{print $5, $9}'
