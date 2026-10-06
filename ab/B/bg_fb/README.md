# bg_fb: force blank released mid-line by an H-IRQ (paulb-nl, #430/#460)

- ROM: paulb-nl's `bg_fb.smc`, attached to [#430](https://github.com/MiSTer-devel/SNES_MiSTer/issues/430) (not copied here);
  sha256 `30755fb70bc883163bdff41efe951ff27b0f5b77c67f1cb27242d6e35e95ccc5`, 262,144 bytes. Rename to `bg_fb.sfc` for tasty.
- Movie: `bg_fb.lsmv`, 780 frames from power-on, R pressed at frames 300, 420, 540 and 660 (each R moves the IRQ a step right).
- Hardware: paulb-nl's capture from #460 (`460/hardware-bg_fb-paulb-nl.png`, credited) and his #430 video for the R presses.

The observable is the bar row: where the black force-blank bar ends, the green segment, and whether a red "N" tile appears
past it. A mid-line IRQ lands on one of three dot phases from frame to frame, so each panel stacks three consecutive frames.

| window | hardware | upstream 2302683 | PR B (A+B) 3f33d28 | PR A alone (dcde04d) | bsnes v115.1 | MesenCE 2.2.1 |
|---|---|---|---|---|---|---|
| start (`ab-start.png`) | black 38-156, green to 176, no N | black to 157, no N | black to 155, green 156-175, no N | N in 2 of 3 frames | black 46-163, no green, no N | black 39-156, no green, no N |
| after R x1 (`ab-R1.png`) | no N | N in 2 of 3 | no N | N in 3 of 3 | no N | no N |
| after R x2 (`ab-R2.png`) | N | N | N in 1-2 of 3 | no N (bar moved) | no N | no N |

Neither emulator draws the green segment or the N, so neither is a reference for this test; hardware is. The window shares
over every frame are in the README's section 1 table; the counts above are from the three frames shown.

- `bar.gif`: the bar row, upstream over PR B (A+B), frames 280-560 (R at 300, 420, 540), for the phase flicker.
- MP4 of the whole movie, three cores stacked: `460/bg_fb.mp4`. Raw AVIs: release `evidence-460-cores`.
- `hashes/`: upstream, A, A+B.

- Counters: 3 runs, captured 782 each; missed 0, torn 0, late 0, lost 0; encoder duplicates in compared windows 0; worst gap_max 1.2 ms
