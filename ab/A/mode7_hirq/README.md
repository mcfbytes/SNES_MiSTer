# paulb-nl's mode 7 H-IRQ tests (#274, #275): PR A alone fails them; PR A plus a Mode 7 fix matches hardware

- ROMs: `mode7_tests.zip` attached to [#274](https://github.com/MiSTer-devel/SNES_MiSTer/issues/274) (not copied here);
  sha256 `2433008623e0f60edb989082c0f1f34b5c5d8f400ab85fcede6f3dd58ae40117`. Eight variants (`.smc`, 256 KiB, renamed to `.sfc`).
- Movies (`*.lsmv`, 900 frames, `m7.script`): H-IRQ starts at H 0 (V 36); R at frames 120, 180, ... 540 steps H to 1..8;
  select at 660 resets to 0; L at 720 sets H to `$FFFF` (#275: the IRQ must then not fire).
- Measure (`tools/m7line.py`): in each H window, the share of frames where line 36, the line above the second row of
  squares, is black, i.e. the IRQ's `M7VOFS` write landed in time. On hardware it is black for small H, flickers at the
  threshold, and is gone beyond it.
- Hardware: paulb-nl's table in #274, SNES APU-01 / 1-CHIP-01 with an Everdrive: the H values at which the line flickers.
  srg320's console gives bra_nops82 2-6 (#274), so 1-6 and 2-6 both count as hardware for that variant.

## Why A alone fails, and the fix

The test measures two things together: when the H-IRQ is taken, and when the PPU reads `M7HOFS/M7VOFS/M7X/M7Y` for
the Mode 7 precalc (fullsnes: the ORG.X/ORG.Y multiplies just before the first pixel). Upstream's read point was set
against upstream's IRQ, which is ~1.5 dots early (`../irqprobe`, `../busprobe`, `../test_irqb_verbose`). PR A moves the IRQ
flag 6 master clocks later, so every M7VOFS write in these tests lands 6 clocks later against an unchanged read point.

The fix (branch `irq-timing-m7b`, `dcde04d`, on top of A `2ff03cf`) moves the whole precalc by the same 6 clocks: the
latch moves from H=7 on the dot's rising edge to H=9 on its falling edge, and the X/Y products swap edges, so every ORG
read is a pure 1.5-dot shift (`rtl/PPU.vhd`, `rtl/PPU_PKG.vhd`). The precalc still ends a dot before the first Mode 7
fetch (H=14). A one-dot shift (latch at H=8, `irq-timing-m7` `f11e31d`, +4 clocks) was tried first and is not enough.

MesenCE [PR #275](https://github.com/nesdev-org/MesenCE/pull/275) (`32be989`, by SourMesen, open; the Linux AOT CI build of
that commit) is the joint reference: bsnes's IRQ timing (test_irqb 32/32, same screens as 2.2.1) and one latch for all four
registers at hClock 44 (dot 11): a write at or after it is not seen until the next line.

## Results

Frames with the black line, per H window (52 frames each; H 0: 60):

| variant | hardware: flickers at H | upstream 2302683 | PR A 2ff03cf (A+B identical) | A + fix dcde04d | MesenCE PR #275 |
|---|---|---|---|---|---|
| wai_nops83 | 1 | 0: all, **1: 34**, 2+: none | 0: all, 1+: none | 0: all, **1: 34**, 2+: none | 0: all, **1: 41**, 2+: none |
| wai_nops95_fastrom | 3 | 0-2: all, **3: 34**, 4+: none | 0-1: all, 2: 12, 3+: none | 0-2: all, **3: 34**, 4+: none | 0-2: all, **3: 35**, 4+: none |
| wai_nops96_fastrom | 1 is too late (no flicker) | 0: all, 1+: none | **0: 17 of 60**, 1+: none | 0: all, 1+: none | 0: 42 of 60, 1+: none |
| bra_nops82 | 1-6 (srg320: 2-6) | 0-1: all, 2-6: 39/36/37/16/5, 7+: none | 0: all, 1-5: 44/29/30/24/4, 6+: none | 0-1: all, 2-6: 49/45/35/17/7, 7+: none | 0-1: all, 2-6: 47/28/30/7/4, 7+: none |
| bra_nops83 | 0-3 | 0-3: 45/24/10/3, 4+: none | 0-1: 31/12, 2+: none | 0-3: 49/26/13/7, 4+: none | 0-3: 32/21/10/3, 4+: none |
| bra_nops95_fastrom | 1-5 | 0: all, 1-5: 40/36/21/13/8, 6+: none | 0-3: 51/29/22/8, 4+: none | 0: all, 1-5: 43/30/24/12/4, 6+: none | 0: 58, 1-4: 40/29/23/10, 5+: none |
| bra_nops96_fastrom | 0-2 | 0-2: 37/15/7, 3+: none | 0: 23, 1+: none | 0-2: 34/13/5, 3+: none | 0-2: 24/14/3, 3+: none |
| wai_nops79 (no hardware row) | | all | all | all | all |
| H = `$FFFF` (#275) | no IRQ | no IRQ | no IRQ | no IRQ | no IRQ |
| matches hardware | | 7 of 7 (bra_nops82 as 2-6) | 0 of 7 | **7 of 7** (bra_nops82 as 2-6) | 6 of 7 (bra_nops95 stops at 4) |

The +4-clock trial `f11e31d`: wai_nops83 1: 18; wai_nops95 3: 17; bra_nops82 1-6: 48/43/40/32/13/1; bra_nops83 0-2: 42/20/10;
bra_nops95 1-4: 38/26/19/11; bra_nops96 0-1: 32/7. 4 of 7.

The four `wai_*` recordings of A + fix are hash-identical to upstream's on all 900 frames. The `bra_*` ones differ only
inside the flicker windows: which phase of the loop the IRQ hits changes from frame to frame with the CPU timing.

## Other checks on A + fix (rig, same quality gate)

- test_irqb (unmodified): passes, a blue screen as on bsnes and MesenCE; upstream ends red. test_irqb_verbose: 32/32.
  test_irqb_verbose, irqprobe, busprobe, pal-irqprobe, pal-busprobe: hash-identical to PR A on every frame.
- Jurassic Park (USA), the 4th attract sequence (the island; bsnes-emu/bsnes#397, a glitched line on bsnes and MesenCE 2.2.1,
  clean on MesenCE PR #275): 12300 empty frames from power-on (`jp/jp.lsmv`, AVI window 11500-12300). Upstream, PR A and
  A + fix are hash-identical on all 12300 frames, and the island frames show no glitched line (`jp/*.frames.tsv`).
- Super Mario World / SMAS+SMW, Ludwig's castle (#253): not tested; no movie that reaches Ludwig syncs here (the lsnes
  "warps" TAS desyncs at once on MesenCE; the #253 save file would need hand-made input through the castle).
- PR B on A + B + fix (`ppu-460-pr` + the fix, `d563a3a`): bg_fb, bg_dense, contra_fb, contra_last, hblankemu are
  hash-identical to A + B (`18f47d6`) on every frame (contra: the allowed `resize` row at frame 6 only).
- Games pack (Full Throttle, Chuck Rock, Cybernator, Kawasaki, WeaponLord, Aladdin; 9000 frames each): hash-identical to PR A.
- Quartus 17.0.2, the `.qsf` seed: A + fix worst setup slack +0.010 ns, hold +0.243 ns; A + B + fix +0.032 / +0.194 ns.

## Files

- `ab-wai_nops83-H1-fix.png`, `ab-bra_nops83-H3-fix.png`: four consecutive frames at the threshold H, upstream | PR A |
  A + fix | MesenCE PR #275. `ab-wai_nops83-fix.mp4`, `ab-bra_nops83-fix.mp4`: upstream, PR A, A + fix stacked, movie frames 90-720.
- `ab-wai_nops83-H1.png`, `ab-wai_nops83.mp4`: upstream | PR A, before the fix.
- `hashes/`: upstream, A, A+B, A + fix (`*-Afix-dcde04d`) for all eight. `mesence-pr275/*.rows`: MesenCE PR #275's dark
  share of line 36 per frame (buffer row 43), input for `tools/m7line.py`.
- Counters, every MiSTer run: captured 902-903, missed 0, torn 0, dups 0, late 0, lost 0, gap_max 1.1-1.2 ms.
- Emulators other than PR #275: MesenCE 2.2.1 shows the line at every H (0-8); bsnes 2014 accuracy only at small H on some variants.
