# test_irqb (byuu): the unmodified ROM and a verbose build of it

- `test_irqb.smc`: byuu's test, from the higan test-ROM collection
  ([gitlab.com/higan/snes-test-roms](https://gitlab.com/higan/snes-test-roms), `KungFuFurby-test-ROMs/`; not copied here);
  sha256 `184e32affb285abb85611ba6c5237ebc5df3249594c6c51858b11131a5c05ee0`. It ends on a blue screen (pass) or a red one
  (fail). Movie: `test_irqb.lsmv`, 600 empty frames.
- `test_irqb_verbose.sfc`: the same test with every check on screen, built by `probes/test_irqb_verbose/gen.py` + `patch.asm`.
  The measurement code is byte-identical; the 32 fail jumps are NOPed so every check runs, and the pass path jumps to a
  results screen. sha256 `dab1e4d79b908947f071c280cb4af722197b7ffdbee04f115bba1ee44003bebf`. Movie: `test_irqb_verbose.lsmv`,
  600 empty frames. The G rows are what the target measured, the E rows the ROM's built-in expected values; a mismatch is red.
- Hardware: James-F2 ran the unmodified ROM on a real 3-chip console (GPM-02): "test_irqb (pass 20/20)"
  ([#164](https://github.com/MiSTer-devel/SNES_MiSTer/issues/164#issuecomment-571223903)).

| | upstream 2302683 | PR A dcde04d | bsnes 2014 accuracy | MesenCE 2.2.1 | hardware |
|---|---|---|---|---|---|
| `test_irqb` | **fail** (red) | pass (blue) | pass | pass | pass, 20 of 20 (James-F2, GPM-02, #164) |
| `test_irqb_verbose`: mismatches of 32 | 8 (sub-tests 4 and 5: H 3-4 dots early) | 0 | 0 | 0 | not run; the E rows are the values the unmodified ROM passes against |

PR B (A+B, 3f33d28) ends on the same screens as A. Its `test_irqb_verbose` log is hash-identical to A's; in `test_irqb`,
one frame differs (movie frame 21, the frame where the display first turns on: 6 pixels on line 1, dots 199-201, which is
B's one-dot output shift).

- `ab-test_irqb.png` (unmodified) and `ab.png` (verbose): upstream | PR A | bsnes | MesenCE | hardware.
- `ab.mp4`: both ROMs, upstream and PR A.
- `hashes/`: upstream, A, A+B for both ROMs.
- Counters: 6 runs, captured 602 each; missed 0, torn 0, late 0, lost 0; encoder duplicates in compared windows 0; worst gap_max 1.5 ms
