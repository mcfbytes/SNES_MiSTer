# contra_test_fb: force blank released on the last line (paulb-nl, #423/#460)

- ROM: paulb-nl's `contra_test_fb.smc` from [#423](https://github.com/MiSTer-devel/SNES_MiSTer/issues/423#issuecomment-3397223469)
  (not copied here); sha256 `419ecacf802cf7b8b7eabcd3e2f2c1fed9ec9411eab15172aaac5f1c859a8fb4`, 262,144 bytes.
- Movies: `contra_last.lsmv` (Up x12 to move the V-IRQ to the true last line of 239-line mode, then R at 650, 770, 890; 1,010
  frames) and `contra_fb.lsmv` (Up x4, R at 450, 570, 690; 810 frames).
- Hardware: paulb-nl's capture from #460 (`460/hardware-contra_test_fb-paulb-nl.png`, credited).

The observable is the last line: the force-blank release mark, and whether a tile shows at x 52-60.

| window (`contra_last`) | hardware | upstream 2302683 | PR A+B 18f47d6 | +IRQ only (A) | bsnes v115.1 | MesenCE 2.2.1 |
|---|---|---|---|---|---|---|
| start (`ab-start.png`) | mark at x 37-38, no tile | mark 38-39; tile in 1 of these 3 frames (2 of 3 over the window) | mark 36-37, no tile | tile in 3 of 3 | no mark, no tile | no mark, no tile |
| after R x1 (`ab-R1.png`) | tile | tile | tile | tile | no tile | no tile |

The panels zoom on the last 7 lines, dots 0-128, three consecutive frames each. Neither emulator shows the tile at any point,
so neither is a reference here.

- MP4 of the whole `contra_last` movie, three cores stacked: `460/contra_last.mp4`. Raw AVIs: release `evidence-460-cores`.
- `hashes/`: both movies, upstream, A, A+B. Each recording has one `resize` row at movie frame 6, when the ROM switches to
  239-line mode; it is outside every compared window.

Counters (re-recorded 2026-10-05 on the current image, frame-hash identical to the 2026-10-04 runs behind section 1): every run missed 0, torn 0, late 0, lost 0, gap_max 1.1-1.2 ms; no encoder duplicates in any compared window.
