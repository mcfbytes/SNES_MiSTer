# bg_dense: bg_fb with an R every 60 frames, against paulb-nl's hardware video

- ROM: `bg_fb.smc` (see `ab/B/bg_fb`). Movie: `bg_dense.lsmv`, 1,320 frames, R at 300, 360, ... 1200 (16 presses).
- Hardware: paulb-nl's #430 video, measured with the same tool (`tools/feat.py`); not copied here.

Measured over the whole movie, per bar-end position, which frames show the red N (`460/bg_dense-bar-end-vs-N.tsv`):

| | hardware | upstream 2302683 | PR B (A+B) 3f33d28 | PR A alone (dcde04d) |
|---|---|---|---|---|
| bar-end x where the N shows | 151-152, 159-160, 167-168 | 160-161, 168-169 | 159-160, 167-168 | 160-161, 168-169 |
| bar end at start | ~156 | 157-158 | 155-156 | 159 |

- `ab-R2.png`: the bar row after R x2 (frames 417-419), upstream | A+B | A alone | bsnes v115.1 | MesenCE. As on `bg_fb`, neither
  emulator draws the green segment or the N.
- MP4: `460/bg_dense.mp4`. Raw AVIs: release `evidence-460-cores`. `hashes/`: upstream, A, A+B.

- Counters: 3 runs, captured 1,322 each; missed 0, torn 0, late 0, lost 0; encoder duplicates in compared windows 0; worst gap_max 1.2 ms
