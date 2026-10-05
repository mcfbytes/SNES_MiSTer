# A/B packs: how they were made and how to re-run them

One directory per test, `ab/<PR>/<test>/`. Each holds:

- the ROM, or our source plus build script; for third-party ROMs, a link and sha256;
- the tasty movie (`.lsmv`) that drives the recording, from power-on (for a test ROM with no input, a movie of empty frames);
- `ab*.png`, a labelled side-by-side: upstream 2302683 | the PR | bsnes | MesenCE | hardware (where we have it, credited);
- `ab.mp4` (or a link to an existing one), the MiSTer recordings side by side;
- `hashes/*.frames.tsv`, tasty's per-frame hash log of each MiSTer recording, so two runs can be compared by hash.

The prebuilt cores and the raw AVIs are assets of the pre-release
[`evidence-460-cores`](https://github.com/mcfbytes/SNES_MiSTer/releases/tag/evidence-460-cores), not files in this branch.

## Cores

| label | commit | release asset |
|---|---|---|
| upstream | `2302683` (master) | `SNES_upstream-2302683.rbf` |
| PR A | `2ff03cf` | `SNES_A-2ff03cf.rbf` |
| PR A+B | `18f47d6` (built from `0148bb7`, the same git tree) | `SNES_AB-18f47d6.rbf` |
| PR C | `57160ab` | `SNES_C-57160ab.rbf` |

Quartus 17.0.2 Lite, the `.qsf` seed. sha256 of each is in the release notes.

## Re-running a pack on a MiSTer

Copy the core, the ROM and the movie to the card, then run [tasty](https://github.com/mcfbytes/Tasty_MiSTer):

```sh
tasty play <test>.lsmv --rom <test>.sfc --core SNES_<label>.rbf --record <outdir> --linger 0 --no-splash
```

`<outdir>` gets `<test>_000.avi` and `<test>.frames.tsv`. Every recording starts at power-on and plays the same movie, so movie
frame n is the same moment on every core. Two runs of the same core give the same hashes; compare yours with
`hashes/<label>.frames.tsv` by the `movie_frame` and `hash` columns (`tools/hashcmp.py` in the branch root does this). Without
tasty, the MGL in a pack (where there is one) loads the core and ROM; the result screens of the test ROMs are static.

`tools/rigrun.sh <label> <rbf> <test>...` is the loop we ran on the card. `tools/pad128k.py` makes the 128 KiB probe ROMs
from the 32 KiB ones in `probes/`: tasty will not hash a SNES ROM under 128 KiB, and the core mirrors a 32 KiB LoROM anyway.

## Emulators

- **bsnes 2014 accuracy** (libretro), for the test ROMs of A and C, the probe references' source. `tools/emushot.sh <rom> <frames> <dir>`
  runs it headless with `probes/lrrun.c`.
- **bsnes v115.1** (libretro, `bsnes_ppu_fast=OFF`, `bsnes_entropy=None`, no overscan crop), for B's movies:
  `tools/emumovie.sh <rom> <movie.lsmv> <frames> <dir>` replays the movie's input with `tools/lrrun2.c`. bsnes 2014 is not used
  for B: its `bg_fb` frames alternate columns with the backdrop colour, as if pseudo-hires were on, which hides the bar row; we did not chase why.
- **MesenCE 2.2.1**, `--testRunner` with `Snes.DisableFrameSkipping` on; `tools/mesen-shot.lua` (a test ROM's screen) and
  `tools/mesen-movie.py` (a movie's input, screens at listed frames).

We kept emulator screenshots, not videos. Each test ROM's result screen is static, and for B's tests the emulators show no
frame-to-frame phase variation (the three-frame stacks in the B panels).

## Recording quality

Every MiSTer recording in a pack passed this gate (`tools/recgate.py <tasty.out> <frames.tsv>`): tasty's final `rec` status
has `missed`, `torn`, `backpressure`, `wdrop`, `werr`, `avi_drop`, `gaps` and `drift` all 0; the replay's `late`, `lost` and
`underruns` are 0; and the hash log has no `dup_reason` other than `none` and no `core_frame` gap. A run that failed was re-run.
The only exception allowed is a `resize` row at the mode switch before frame 10 of the 239-line Contra test, outside every
compared window. Each pack's README carries its counters line.

Rig: DE10-Nano, kernel `7.2.9` PREEMPT_RT, with `vm.compact_unevictable_allowed=0`, `vm.compaction_proactiveness=0` and the
writeback workqueue cpumask `1` (set at boot). Recordings were written to the SD card.

## Panels

`tools/abpanel.py <out.png> <title> <label=image>...` builds every side-by-side: each screen is brought to the core's 512-wide
frame, doubled vertically, nearest-neighbour; `CROP` zooms into a box, `a+b+c` stacks consecutive frames. `tools/avifr.py`
pulls a movie frame out of a recording. `tools/probeband.py` reads the probe screens back to numbers, and `tools/rowcolor.py` counts
their green/red rows.
