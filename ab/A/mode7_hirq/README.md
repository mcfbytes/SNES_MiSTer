# paulb-nl's mode 7 H-IRQ tests (#274, #275): a hardware reference that PR A does not match

- ROMs: `mode7_tests.zip` attached to [#274](https://github.com/MiSTer-devel/SNES_MiSTer/issues/274) (not copied here);
  sha256 `2433008623e0f60edb989082c0f1f34b5c5d8f400ab85fcede6f3dd58ae40117`. Eight variants (`.smc`, 256 KiB, renamed to `.sfc`).
- Movies (`*.lsmv`, 900 frames, `m7.script`): H-IRQ starts at H 0 (V 36); R at frames 120, 180, ... 540 steps H to 1..8;
  select at 660 resets to 0; L at 720 sets H to `$FFFF` (#275: the IRQ must then not fire).
- Measure (`tools/m7line.py`): in each H window, the share of frames where line 36, the line above the second row of
  squares, is black, i.e. the IRQ's `M7VOFS` write landed in time. On hardware it is black for small H, flickers at the
  threshold, and is gone beyond it.
- Hardware: paulb-nl's table in #274, SNES APU-01 / 1-CHIP-01 with an Everdrive: the H values at which the line flickers.

Frames with the black line, per H window (52 frames each; H 0: 60):

| variant | hardware: flickers at H | upstream 2302683 | PR A 2ff03cf (A+B identical) |
|---|---|---|---|
| wai_nops83 | 1 | 0: all, **1: 34**, 2+: none | 0: all, 1+: none |
| wai_nops95_fastrom | 3 | 0-2: all, **3: 34**, 4+: none | 0-1: all, 2: 12, 3+: none |
| wai_nops96_fastrom | 1 is too late (no flicker) | 0: all, 1+: none | **0: 17 of 60**, 1+: none |
| bra_nops82 | 1-6 | 0-1: all, 2-6: 39/36/37/16/5, 7+: none | 0: all, 1-5: 44/29/30/24/4, 6+: none |
| bra_nops83 | 0-3 | 0-3: 45/24/10/3, 4+: none | 0-1: 31/12, 2+: none |
| bra_nops95_fastrom | 1-5 | 0: all, 1-5: 40/36/21/13/8, 6+: none | 0-3: 51/29/22/8, 4+: none |
| bra_nops96_fastrom | 0-2 | 0-2: 37/15/7, 3+: none | 0: 23, 1+: none |
| wai_nops79 (no hardware row) | | all | all |
| H = `$FFFF` (#275) | no IRQ | no IRQ | no IRQ |

Upstream matches the hardware thresholds on six of seven variants (bra_nops82 starts one step late). PR A moves every
threshold about one H step earlier and matches none of the seven exactly; A+B (`18f47d6`) gives frame-identical results to A.
`$FFFF` is handled correctly by both.

- `ab-wai_nops83-H1.png`: H = 1, four consecutive frames: upstream flickers as on hardware, PR A never shows the line.
- Emulators are not a reference here: MesenCE 2.2.1 shows the line at every H (0-8); bsnes 2014 accuracy only at small H on
  some variants (bra_nops82 0-3, bra_nops95 0-1, wai_nops79 all, wai_nops95 0, the others never).
- `hashes/`: upstream, A, A+B for all eight. Counters, every run: captured 901-903, missed 0, torn 0, dups 0, late 0, lost 0,
  gap_max 1.1-1.2 ms.
- `ab-wai_nops83.mp4`: wai_nops83, upstream and PR A, movie frames ~90-720 (H 0, then one step per second up to 8; watch the line above the second row).
