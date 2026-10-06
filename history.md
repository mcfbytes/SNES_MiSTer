# History: builds and results that the current evidence replaces

Everything in the README and in `ab/` was recorded on the four cores in the README's core table (2302683, dcde04d,
3f33d28, 57160ab). This note lists what came before, so links into earlier commits of this branch still make sense.
Git history has the files themselves (`git log -- <path>`).

## Earlier builds and their labels

| label (earlier files) | what it was | replaced by |
|---|---|---|
| `m0`, "upstream" | master `2302683` | the same commit, rebuilt (`SNES_upstream-2302683.rbf`) |
| `m1`, "+IRQ", `A-2ff03cf` | PR A's first commit alone | PR A `dcde04d` (both commits) |
| `pr2`, `f2`, `0148bb7`, `18f47d6`, "+IRQ+PPU" | PR B on `2ff03cf` (f2: before B's own Mode 7 fix) | PR B `3f33d28`, on `dcde04d` |
| `m7b`, `Afix-dcde04d` | PR A with the Mode 7 commit | the same commit, now PR A's head |
| `m7bB`, `d563a3a` | PR B on the Mode 7 commit | `3f33d28`, the same git tree |
| `c`, `C-57160ab` | PR C | the same commit, rebuilt |
| control `c61bfd4`, `irq/*-before.png` / `*-after.png` | master before #511, and an A+C build on it (section 6 of the first README) | the `ab/A` and `ab/C` packs on the final cores |

Results that changed with the final commits:

- **#274 (paulb-nl's mode 7 tests):** PR A's first commit alone (`2ff03cf`) moved every flicker threshold about one H step
  early and matched 0 of 7 hardware rows (recorded 2026-10-05: wai_nops83 0: all, 1+: none; bra_nops83 0-1: 31/12;
  bra_nops95 0-3: 51/29/22/8; bra_nops96 0: 23). That is why PR A now carries `dcde04d`; with it, 7 of 7.
- **Movies on PR B:** the SMAS TAS comparison used `f2`; the final PR B is recorded directly (README section 4).
- Every other recording on the final cores is hash-identical to the earlier one of the same tree, or of `2ff03cf` where
  the Mode 7 commit cannot reach (README, "Changes against earlier evidence").

## Earlier Seedy runs (30 seeds each)

`seedy/A-earlier-*.md` (the IRQ patch alone on `c61bfd4`, run 37205363393), `seedy/C-earlier-*.md` (PR C's patch on
`c61bfd4`, run 37214664117) and `seedy/B-ppu-460-0148bb7-vs-2302683.md` (`0148bb7`, B on `2ff03cf`, run 37264587249) are
for earlier heads. The reports for the final heads follow as comments on each PR.

## Builds

The first release assets were built with a different Docker image (`ryanfb/quartus-mister`), and two of them were matched
from notes rather than rebuilt. The same Quartus version in that image gives different placements: `dcde04d` built there
misses setup by 1.493 ns at the `.qsf` seed, while `theypsilon/quartus-lite-c5:17.0.2` (the image MiSTer Seedy uses)
closes it at +0.010 ns. Both builds carry the same build date (`261005`), so the difference is the image. Every core in the release is now built
with the latter; a rebuild of the same commit in it on the same date gives a byte-identical `.rbf`.
