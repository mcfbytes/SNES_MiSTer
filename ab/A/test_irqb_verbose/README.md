# test_irqb_verbose: byuu's test_irqb with every check on screen

- ROM: `test_irqb_verbose.sfc`, built by `probes/test_irqb_verbose/gen.py` + `patch.asm` from byuu's `test_irqb.smc`
  (higan test-ROM collection, [gitlab.com/higan/snes-test-roms](https://gitlab.com/higan/snes-test-roms),
  `KungFuFurby-test-ROMs/`; sha256 `184e32affb285abb85611ba6c5237ebc5df3249594c6c51858b11131a5c05ee0`). The measurement
  code is byte-identical; the 32 fail jumps are NOPed so every check runs, and the pass path jumps to a results screen.
  sha256 of the verbose ROM: `dab1e4d79b908947f071c280cb4af722197b7ffdbee04f115bba1ee44003bebf`.
- Movie: `test_irqb_verbose.lsmv`, 600 empty frames. The screen is final well before the end.

The G rows are what the target measured, the E rows the ROM's built-in expected values (byuu); a mismatch is red.

| | upstream 2302683 | PR A 2ff03cf | bsnes 2014 accuracy | MesenCE 2.2.1 | hardware |
|---|---|---|---|---|---|
| mismatches of 32 | 8 (sub-tests 4 and 5: H 3-4 dots early) | 0 | 0 | 0 | — |

The unmodified `test_irqb.smc` ends on the same screen on bsnes 2014 accuracy and on MesenCE.

- `ab.png`: upstream | PR A | bsnes | MesenCE. `ab.mp4`: upstream and PR A.
- `hashes/`. Counters: upstream captured 602, PR A 602; missed 0, torn 0, dups 0, late 0, lost 0, gap_max 1.1-1.2 ms.
