# paulb-nl's mode 7 H-IRQ tests (#274, #275), against two consoles

- ROMs: `mode7_tests.zip` attached to [#274](https://github.com/MiSTer-devel/SNES_MiSTer/issues/274) (not copied here);
  sha256 `2433008623e0f60edb989082c0f1f34b5c5d8f400ab85fcede6f3dd58ae40117`. Eight variants (`.smc`, 256 KiB, renamed to `.sfc`).
- Movies (`*.lsmv`, 900 frames, `m7.script`): H-IRQ starts at H 0 (V 36); R at frames 120, 180, ... 540 steps H to 1..8;
  select at 660 resets to 0; L at 720 sets H to `$FFFF` (#275: the IRQ must then not fire).
- Measure (`tools/m7line.py`): in each H window, the share of frames where line 36, the line above the second row of
  squares, is black, i.e. the IRQ's `M7VOFS` write landed in time. On hardware it is black for small H, flickers at the
  threshold, and is gone beyond it.
- Hardware, two consoles:
  - paulb-nl, SNES APU-01 / 1-CHIP-01 with an Everdrive: the H values at which the line flickers
    ([#274](https://github.com/MiSTer-devel/SNES_MiSTer/issues/274), first post).
  - srg320: "On my original hardware bra_nops82 had 2-6 flicker"
    ([#274 comment](https://github.com/MiSTer-devel/SNES_MiSTer/issues/274#issuecomment-2657501805)); paulb-nl: "If your
    hardware has 2-6 flicker then it is perfect now"
    ([#274 comment](https://github.com/MiSTer-devel/SNES_MiSTer/issues/274#issuecomment-2658775799)).
    So for bra_nops82, 1-6 and 2-6 both count as hardware.
- MesenCE [PR #275](https://github.com/nesdev-org/MesenCE/pull/275) (`32be989`, by SourMesen, open; the Linux AOT CI build of
  that commit): bsnes's IRQ timing (test_irqb 32/32) and one latch for all four registers at hClock 44 (dot 11). It is the
  only emulator here that reproduces the thresholds: MesenCE 2.2.1 shows the line at every H (0-8), bsnes 2014 accuracy only
  at small H on some variants.

![#274: hardware against upstream, PR A and MesenCE PR #275](m7-hardware-vs-cores.png)

## Results

Frames with the black line, per H window (52 frames each; H 0: 60):

| variant | hardware: flickers at H | upstream 2302683 | PR A dcde04d | MesenCE PR #275 |
|---|---|---|---|---|
| wai_nops83 | 1 | 0: all, **1: 34**, 2+: none | 0: all, **1: 34**, 2+: none | 0: all, **1: 41**, 2+: none |
| wai_nops95_fastrom | 3 | 0-2: all, **3: 34**, 4+: none | 0-2: all, **3: 34**, 4+: none | 0-2: all, **3: 35**, 4+: none |
| wai_nops96_fastrom | 1 is too late (no flicker) | 0: all, 1+: none | 0: all, 1+: none | 0: 42 of 60, 1+: none |
| bra_nops82 | 1-6 (paulb-nl), 2-6 (srg320) | 0-1: all, 2-6: 39/36/37/16/5, 7+: none | 0-1: all, 2-6: 49/45/35/17/7, 7+: none | 0-1: all, 2-6: 47/28/30/7/4, 7+: none |
| bra_nops83 | 0-3 | 0-3: 45/24/10/3, 4+: none | 0-3: 49/26/13/7, 4+: none | 0-3: 32/21/10/3, 4+: none |
| bra_nops95_fastrom | 1-5 | 0: all, 1-5: 40/36/21/13/8, 6+: none | 0: all, 1-5: 43/30/24/12/4, 6+: none | 0: 58, 1-4: 40/29/23/10, 5+: none |
| bra_nops96_fastrom | 0-2 | 0-2: 37/15/7, 3+: none | 0-2: 34/13/5, 3+: none | 0-2: 24/14/3, 3+: none |
| wai_nops79 (no hardware row) | | all | all | all |
| H = `$FFFF` (#275) | no IRQ | no IRQ | no IRQ | no IRQ |
| matches hardware | | 7 of 7 (bra_nops82 as srg320's 2-6) | **7 of 7** (bra_nops82 as srg320's 2-6) | 6 of 7 (bra_nops95 stops at 4) |

PR B (A+B, 3f33d28) is hash-identical to PR A on all eight recordings. The four `wai_*` recordings of PR A are
hash-identical to upstream's on all 900 frames. The `bra_*` ones differ only inside the flicker windows: which phase of
the loop the IRQ hits changes from frame to frame with the CPU timing, so the shares move by a few frames while the
thresholds stay.

## Why PR A has two commits

The test measures two things together: when the H-IRQ is taken, and when the PPU reads `M7HOFS/M7VOFS/M7X/M7Y` for the
Mode 7 precalc (fullsnes: the ORG.X/ORG.Y multiplies just before the first pixel). Upstream's read point has always been set
against upstream's IRQ timing, and was re-tuned each time that timing moved:

| date | commit | change | #274 on MiSTer |
|---|---|---|---|
| 2021-05-03 | `a04ac87` (#272) | Mode 7 parameters latched at `M7_FETCH_START-1` (H 13), for an SMW glitch | every threshold 3-4 H late, e.g. bra_nops82 6-10 against 1-6 (paulb-nl, first post) |
| 2021-05-07 | `1922a49` (#277) | `M7_XY_LATCH` = 11: "the right time ... is H_CNT = 11" ([srg320](https://github.com/MiSTer-devel/SNES_MiSTer/issues/274#issuecomment-834503750)) | close: bra_nops82 3-7, wai_nops96 0 ([paulb-nl](https://github.com/MiSTer-devel/SNES_MiSTer/issues/274#issuecomment-834826314)) |
| 2024-09-29 | `f2409f0` | `M7_XY_LATCH` = 8, with the S-CPU rework `bd4d8fb` (2024-10-01) | "almost the same as real hardware", bra_nops82 2-6 ([paulb-nl](https://github.com/MiSTer-devel/SNES_MiSTer/issues/274#issuecomment-2600790322)) |
| 2024-10-06 | `657758e` | 65C816 IRQ fix (emudetect); the read point unchanged | broken again: bra_nops83 0-1, bra_nops96 0 (same comment) |
| 2025-02-13 | `4502df9` | interrupt delay after DMA by 1 cycle | fixed ([srg320](https://github.com/MiSTer-devel/SNES_MiSTer/issues/274#issuecomment-2657501805), [paulb-nl](https://github.com/MiSTer-devel/SNES_MiSTer/issues/274#issuecomment-2658775799)) |
| 2025-09-28 | `5eeddd6` | `M7_XY_LATCH` = 7 (BG and Mode 7 force-blank accuracy); still 7 on master `2302683` | 7 of 7 above |

PR A's first commit (`2ff03cf`) moves the H/V IRQ flag 6 master clocks later (see `../irqprobe`, `../busprobe`,
`../test_irqb`). Against the unchanged read point, every #274 threshold then moves about one H step early: 0 of 7 hardware
rows (an earlier recording of `2ff03cf` alone; `history.md` in the branch root). The second commit (`dcde04d`) moves the
precalc by the same 6 clocks: the latch moves from H 7 on the dot's rising edge to H 9 on its falling edge, and the X/Y
products swap edges, so every ORG read is a pure 1.5-dot shift (`rtl/PPU.vhd`, `rtl/PPU_PKG.vhd`). The precalc still ends a
dot before the first Mode 7 fetch (H 14). A one-dot shift (latch at H 8, +4 clocks) was tried first and matched 4 of 7.

## Files

- `m7-hardware-vs-cores.png`: the table above as a chart (`ab/tools/m7chart.py`).
- `ab-wai_nops83-H1.png`, `ab-bra_nops83-H3.png`: four consecutive frames at the threshold H, upstream | PR A | MesenCE PR #275.
- `ab-wai_nops83.mp4`, `ab-bra_nops83.mp4`: upstream and PR A, movie seconds 1.5-12 (H 0 to 3; watch the line above the
  second row of squares).
- `hashes/`: upstream, A, A+B for all eight. `mesence-pr275/*.rows`: MesenCE PR #275's dark share of line 36 per frame (buffer
  row 43), input for `tools/m7line.py`.
- Counters: 24 runs, captured 902 each; missed 0, torn 0, late 0, lost 0; encoder duplicates in compared windows 0; worst gap_max 1.3 ms
