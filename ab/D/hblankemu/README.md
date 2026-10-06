# HblankEmuTest (Motive), sprite side: commit 4 of `ppu-timing-stack`

- **ROM:** `HblankEmuTest.sfc` from the higan test-ROM collection
  ([gitlab.com/higan/snes-test-roms](https://gitlab.com/higan/snes-test-roms), `Motive-test-ROMs/`).
  sha256 `80706521642cc6183f406f74249d18f0ff3a501e574dd5acae67fe0c04bf0fc7`.
- **Movie:** `hblankemu.lsmv`, 900 empty frames (the same file as `ab/B/hblankemu/`).
- **Hardware:** paulb_nl's photo on nesdev ([post](https://forums.nesdev.org/viewtopic.php?p=231279#p231279), imgur `bpuXsI4`,
  the same on all four of his consoles; creaothceann's SFC agrees). The copy is `../../../hblankemu/hardware-paulb_nl-bpuXsI4.png`.
  `hardware-aligned.pgm` is that photo scaled to 256x224 and aligned to the core's frame.
- **Core:** commit 4 `8e89569` (tested as `0f6b5e4`, the same tree), on commit 3 `b7d997f` (= `3f33d28`), built as the other packs. sha256
  `05ab6399b5f086eb46322c41d48c47dbc18ac936f94307f675835121ef136bd2`.
- **Slack at the `.qsf` seed:** worst setup -0.212 ns, on one path only: `sdram|rbuf[8]` to the CPU's `P[1]`, at the
  slow 100C corner. That path is outside the PPU. MiSTer Seedy, 30 seeds vs master: 4/30 close (master 8/30); seed 14 meets (+0.103 ns).

| | hardware | master 2302683 | after commit 3 (b7d997f) | commit 4 (8e89569) |
|---|---|---|---|---|
| distinct frames (thresholded), movie frames 300-899 | 1 | 4 | 7 | **1** (also 1 over frames 30-899) |
| px different from the photo, per state | — | 546-1010 | 428-707 | **69** |
| line 1 | "Incor" + "ORRECT" | "THIS IS CORRECT", sprite bar | "THIS IS CORRECT" | **"Incor" + "ORRECT"** |
| white bar, dotted left column, small "B" | none | yes | yes | **none** |

The 69 px are anti-aliased letter edges in the photo, so it is the floor for this comparison.

The 1-chip consoles also show a purple bar at the left of the picture (paulb_nl, imgur `NBOesED`), which comes from the
ROM writing $FF to $2100 (koitsu's analysis in the thread). That is a separate 1-chip PPU2 effect. It is not modelled
here and is out of scope.

- `ab.png`: hardware | master (2 of 4 states) | after commit 3 (3 of 7 states) | commit 4. The labels give the frame counts and the
  px scores.
- `ab.mp4`: after commit 3 (top) and commit 4 (bottom), movie frames 280-400.
- `hashes/`: hash logs of commit 4 (0f6b5e4), commit 3 (3f33d28) and master (2302683). The master and commit 3 columns of the table come from those recordings.
- `score_rec.py <recdir> <label> [f0 f1]`: groups a recording's frames into states and scores each one against
  `hardware-aligned.pgm`.

- Counters: captured 902, missed 0, torn 0, backpressure 0, dups 0, late 0, lost 0, gap_max 1.1 ms
  (`tools/recgate.py ... 10 100000000`: ok).
