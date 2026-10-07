# E: PR #513 as five commits (`ppu-timing-stack` at `ae0818c`)

PR #513 was rebuilt after review into five commits on master `2302683`, one topic each. This pack maps each commit to
the cores it was built and run as, and collects the results. The older packs (`ab/A`, `ab/B`, `ab/D`) describe the
earlier four-commit layout; their recordings still apply where this README says so.

| # | commit | subject | files |
|---|---|---|---|
| 1 | `1f69c08` | CPU: an NMI latched during an interrupt sequence is taken after it | `rtl/65C816/P65C816.vhd` |
| 2 | `e98ca40` | CPU: V counter resets as VBLANK clears (HV IRQ at V=0, H=339) | `rtl/CPU.vhd` |
| 3 | `5fe4edd` | CPU: H/V IRQ reaches the 65C816 6 clocks later; Mode 7 precalc with it | `rtl/CPU.vhd`, `rtl/PPU.vhd`, `rtl/PPU_PKG.vhd` |
| 4 | `dce0098` | PPU: BG fetch 2 dots later, output 1 dot later, force blank on /PAWR | `rtl/PPU.vhd`, `rtl/PPU_PKG.vhd`, `rtl/SNES.vhd`, `rtl/sdram.sv`, `SNES.sv`, `rtl/lightgun.sv` |
| 5 | `ae0818c` | PPU: OBJ time stage under force blank (HblankEmuTest) | `rtl/PPU.vhd` |

## Which core each result comes from

Most rig runs were made on builds of an earlier cut of the same series (`315c348`, `04384c6`, and `ec98508` for the
head). The current commits differ from those trees only in comments, one VHDL sensitivity-list entry (`H_BG`, which
synthesis ignores), two constants moved from `PPU.vhd` to `PPU_PKG.vhd` with the same values, and one comment line in
`sdram.sv` (`git diff ec98508 ae0818c`: 4 files, +12/-11). Synthesis is unchanged: each `.rbf` built from the current commits
is **byte-identical** to the one built from the tree it was tested as, on the same day (sha256 below).

| # | prebuilt core (release asset) | rig results from | how they relate |
|---|---|---|---|
| 1 | not built alone | the head | GHDL simulation of the NMI case; on the rig only as part of the head |
| 2 | not built alone | `7d0ec00` (this change alone on an earlier base) and the head | `7d0ec00` explains the Contra III difference (below) |
| 3 | `SNES_513v3-c3-5fe4edd.rbf` | `315c348` (`P3`) | the same `.rbf` |
| 4 | `SNES_513v3-c4-dce0098.rbf` | `04384c6` (`P4`) | the same `.rbf` |
| 5 | `SNES_513v3-c5-ae0818c.rbf` | `ec98508` (`I`) and `ae0818c` itself | the same `.rbf` |

## Cores and timing (seed 1, no Seedy sweep for this version)

Quartus 17.0.2 Lite in `theypsilon/quartus-lite-c5:17.0.2`, `quartus_sh --flow compile SNES` on a `git archive` of the
commit, the `.qsf` seed (1), build date `261007`. Slack in ns from `quartus_sta` per corner (`clk_mem` = SDRAM clock,
`clk_sys` = core clock); worst hold over all clocks. **No 30-seed Seedy sweep was run for this version.** At one seed
the failing path moves from build to build (it is never in the changed logic), so these numbers say how these files
placed, not whether the design closes timing; the 30-seed statistics for the earlier layout are in the branch README,
section 10.

| core | sha256 | slow 100 °C mem / sys / HDMI / hold | slow −40 °C mem / sys / HDMI / hold | failing endpoint |
|---|---|---|---|---|
| `SNES_513v3-c3-5fe4edd.rbf` (commit 3) | `11d739e9762f999537a7020933c0c00dcb8f72e4bb3d50cc1d3856114edf61fc` | +0.372 / +0.193 / **−0.262** / **−0.020** | +0.641 / +0.373 / **−0.371** / +0.066 | HDMI: `ascal` (scaler); hold also fails at the fast corners (−0.026 / −0.051) on `savestates` → `ddram` |
| `SNES_513v3-c4-dce0098.rbf` (commit 4) | `350aa6a7793db38cff44261b6409e18a25c397648e09e3f84f882737292e51a9` | **−0.804** / **−0.393** / +0.419 / +0.244 | **−0.379** / +0.358 / +0.170 / +0.158 | `sdram` `rbuf[11]` → `din[1][3]` |
| `SNES_513v3-c5-ae0818c.rbf` (commit 5, head) | `925a93d6bd421c96b213aba40da46fc05440c0472420b9dd2f5c73eecbea3adf` | **−0.386** / +0.071 / +0.240 / +0.243 | **−0.219** / +0.312 / +0.138 / +0.110 | `sdram` `rbuf[11]` → `din[1][3]` |

Each `.rbf` is **byte-identical** to the build of the tree it was tested as: commit 3 to `315c348` (P3), commit 4 to
`04384c6` (P4), commit 5 to `ec98508` (I). So the rig results below were recorded on these exact files. For comparison,
master `2302683` at the same seed: +0.067 setup / +0.241 hold in this image on build date `261005` (branch README), and
−0.345 ns in Seedy's own `.qsf`-seed build. None of the failing paths is in the PPU or IRQ logic this PR changes.

The fast corners pass setup on every build here.

## Equivalence check of the head core on the rig

The `ae0818c` core, from the release, against the `ec98508` recordings, by tasty's per-frame hashes:

| run | result |
|---|---|
| `test_irqb_verbose` (600 frames) | identical to I on every frame |
| HblankEmuTest (900 frames) | identical to I on every frame; 1 state over movie frames 300-900, 69 px from the hardware photo |
| gunprobe, 2 cold loads (Super Scope on Joy1 via `SNES.CFG`) | H=0A9 V=070, Hmin=Hmax=0A9, Vmin=Vmax=070, flag 63 / E3: as I and master |
| Contra III TAS, whole movie, recorded to the SD card | identical to I on all 45,187 frames it hashed; the SD card stalled the AVI writer for 309 frames near the end (44,934-45,494), and its log has no row for movie frame 16,947, so this take fails the gate; its hashes and its clean frames are used |
| Contra III TAS, whole movie, video for the release | all 45,497 movie frames, each identical to I. No single take passed the gate: three takes to a network share had 8-10 encoder-backpressure frames each (and the share's stalls dropped some AVI segments to half size), and a tail take to the SD card from frame 44,800 had backpressure near the end too. A second tail take, from frame 45,100, passed the gate; it was recorded after `/media/fat` was remounted without `sync` (the operator's change for SD-card stalls). The published video is spliced by `splice.py`: for every movie frame, a full-size AVI frame from a take whose row is clean, checked against I's hash for that frame. Source per frame: the first SD take 45,187, tail from 45,100: 161, tail from 44,800: 148, share take 1: 1 (movie frame 16,947, which the first SD take's log lacks). Every take replayed in sync (late 0, lost 0) |

## Per commit

### Commits 1-2: the NMI and the V counter

- **1 (NMI).** On master, an NMI whose edge falls inside an IRQ sequence is dropped: with an H-IRQ at HTIME 330 or 335
  and NMI on, every frame loses its NMI; at 336 and 337, 2 and 1 frames of 4 (GHDL simulation of `CPU.vhd` + the
  65C816, 47 cases). With the fix the NMI is taken after the IRQ. The SA-1 instantiates the same 65C816, so it gets the
  fix too. No recording in the regression set changed because of it.
- **2 (V counter).** The V counter now resets as VBLANK clears instead of one tick later. HV IRQs at (0,339) fire twice per
  frame and at (261,339) never, as on paulb-nl's console (#274). It also moves the V-only VTIME=0 `/IRQ` 4 clocks earlier
  (Mesen's value; bsnes's is 4 clocks later). That is the whole Contra III difference against the earlier version of this
  PR: 21 of 45,497 frames (9,332-9,381 and 32,048-32,080, both on the Mode 7 "choose your starting point" screens), a few pixels on lines 0 and 111-112; built alone
  (`7d0ec00`), this commit is identical to the full IRQ change on all 45,497 frames.

`irq/wrap-ntsc.png`: the `irq-wrap` result screen on master, the head and MesenCE. The head equals MesenCE on all 20
NTSC rows; master differs on rows 00, 01, 04, 05 and 06 (red on its screen).

| row | case | master | head | MesenCE 2.2.1 | bsnes 2014 | hardware |
|---|---|---|---|---|---|---|
| 00 | interlace HV 0.339 | 1 | 2 | 2 | 1 | — |
| 01 | interlace HV 262.339 | 0/1 | 0 | 0 | 0 | — |
| 04 | interlace HV 261.339 | 1 | 0/1 | 0/1 | 0/1 | — |
| 05 | HV 261.339 | 1 | **0** | 0 | 0 | 0 (paulb-nl) |
| 06 | HV 0.339 | 1 | **2** | 2 | 1 | 2 (paulb-nl) |
| 02, 03, 07-19 | the other H/V/HV cases | = | = | = | = | — |

(IRQs per frame, min/max over 9 frames.) PAL: the head equals MesenCE except rows 00, 04 and 05, which fall on the 312-line field's 1368-clock long line (the
emulators do not model it; master and the head agree on 04 and 05), and row 13 (H 339), where MesenCE gives 311/312 and
the head, master and bsnes 312. The long line is a kit row (below).

### Commit 3: H/V IRQ 6 clocks later, with the Mode 7 precalc (run as `315c348`)

| test | master | after commit 3 | reference |
|---|---|---|---|
| byuu `test_irqb` | fail (red) | **pass** (blue) | pass on bsnes, MesenCE and a 3-chip GPM-02, 20 of 20 (#164) |
| `test_irqb` verbose build: wrong of 32 | 8 | **0** | 0 |
| jonasquinn `demo_irq` / `demo_irqtest` (sweep ROMs 003, 110, 130, 179) | red `$001F` (FAIL) | **blue `$7C00` (PASS)**, 2 loads each | the ROMs' own pass colour |
| paulb-nl #274, 8 `mode7_*` ROMs | 7 of 7 hardware rows | 7 of 7, hash-identical to the head | paulb-nl and srg320 consoles |
| irqprobe NTSC / PAL (rows equal to bsnes) | 0 of 18 / 4 of 18 in band | 9 of 18 (+6 within 1 dot) / 17 of 18 | bsnes 2014 = MesenCE |
| busprobe NTSC / PAL | 0 of 23 / 7 of 23 | 20 of 23 / 22 of 23 | bsnes 2014 = MesenCE |
| Jurassic Park island attract (bsnes #397), 12,300 frames | clean | hash-identical to master | — |
| `irq-wrap` NTSC/PAL result screens | — | byte-identical to the head | — |

`irq/demo_irq.png`: the four ROMs' screens on master and the head. `IRQ_HOLD_CLK` (the `$4211` hold) and `IRQ_LINE_DLY`
(flag to `/IRQ`) are provisional: the `$4211` flag time and the `/IRQ` time are not yet separated by a hardware capture
(the kit below would). `M7_XY_LATCH` is tuned together with `IRQ_LINE_DLY`; the code comments at both say so.

### Commit 4: BG fetch, output and force blank (run as `04384c6`)

| test | result |
|---|---|
| `bg_fb`, `bg_dense`, `contra_fb`, `contra_last` (#430, #460, #423) | hash-identical to the head and to the earlier draft `f1cfd5f` |
| gunprobe ×2 | H=0A9 V=070, as master: the light-gun P6 delay moves with the pipeline |
| `test_irqb_verbose` | identical to the head |
| HblankEmuTest | 7 states, 428-707 px from the photo: expected before commit 5 (master: 4 states, 546-1010 px) |
| Kirby Super Star attract, 7,200 frames (SA-1, hashes) | identical to master |

**Kirby Super Star and `DI_WAIT`.** An earlier draft of this commit (`f1cfd5f` and the cores before it) drew a 8-16 px
streak of sprite-palette colour on picture row 96 in 1,523 of 7,200 attract frames (2,895-5,403). The game's HDMA writes
`$2100 = $0F` at scanline 96, H clock 1132 (dot ~283, inside the next line's OBJ fetch window; MesenCE trace). Force
blank on /PAWR sampled `DI(7)` while the data bus still held the previous SDRAM read, so for a few clocks the PPU saw
force blank and dropped OBJ slots. `DI_WAIT` holds the sample until the written byte is valid (cart data from its first
valid clock, WRAM at `SYSCLK_CE`). With it the attract is hash-identical to master on all 7,200 frames, and MesenCE and
bsnes show no streak either.

- `kss/kss-head-earlier-mesen.png`: row 96 at frames 2,900, 2,976, 3,200 and 5,000, zoomed: head | earlier draft |
  MesenCE. MesenCE matches the head on the streak line in all 9 sampled frames.
- `kss/sbs-2900-5000.png`: the whole frames, head and earlier draft.
- `kss/z3-bsnes-2900.png`, `kss/z3-bsnes-3200.png`: the same crop with bsnes as the third column.

Bisection (each core 7,200 frames against master): `19beeb2` (force blank on /PAWR, no `DI_WAIT`) = the earlier draft;
`2bb2e3d` (`DI_WAIT` added) identical to master. Not covered: HDMA `$2100` from special-chip ROM; `DI_WAIT` assumes
plain SDRAM timing (`sdram.sv`'s CAS latency and RAS-CAS delay, cross-referenced in the code).

### Commit 5: OBJ time stage under force blank

`hblankemu/ab.png`: hardware | master (2 of its 4 states) | after commit 4 (2 of 7 states) | after commit 5. The head
gives one state in all 600 frames of 300-899, 69 px from paulb_nl's photo (the photo's anti-aliased letter edges; the floor
of this comparison). Scoring: `../D/hblankemu/score_rec.py`. The head's hash log is `hblankemu/hblankemu-c5-ae0818c.frames.tsv`;
it equals `ab/D`'s `0f6b5e4` log except movie frame 10, where they differ by 1 px (the frame the display turns on).

#423: `alttp_oam_copy2` and `alttp_oam_copy2_1` (three movies) are hash-identical on the head and on `f1cfd5f`, which
matched master on every row. The FF3 mine cart was not run (no save available).

## Regression set on the head (run as `ec98508`)

- 30 recordings against the PPU-only lane (`07d9ede`) and the IRQ-only lane (`b5f5b61`): identical to the IRQ lane wherever the PPU
  commits change nothing, and to the PPU lane wherever the IRQ commits change nothing. Contra III differs from the earlier
  version of this PR on exactly the 21 frames above.
- 281 test ROMs (adaptive screenshot, then fixed-wait controls ×2 on four cores for each one that differed): 261
  identical to the earlier version; of the 20 that differ, 5 are the IRQ change (the four `demo_irq` ROMs and `112-irq`),
  6 are capture timing (identical at the fixed wait) and 9 vary between loads of every core.
- Special chips, 7,200-frame idle attracts, hashes only: Kirby Super Star = master. Super Mario RPG (SA-1), Yoshi's Island
  (Super FX 2), Star Fox (Super FX) and Street Fighter Alpha 2 (S-DD1) differ from master on 9, 2,622, 5,159 and 43 frames;
  the same frames differ on the earlier PPU-only version, and the IRQ commits change none of them. Those frames have
  **not** been inspected pixel by pixel. Contra MSU-1 is not reproducible run to run on any core (the MSU stream comes
  from the SD card).

## With #514 merged on top (`278a53d` = `ec98508` + `cfcd933`)

One textual conflict, in a comment next to `HVLATCH` in `PPU.vhd`; the rest merged cleanly.

| test | result |
|---|---|
| gunprobe ×2 | H=0A9 V=070, as the head |
| the six `$2137`/DMA ROMs of #514 (`test_hdmatiming` ×4, `test_dmasync`, `test_mdrhdma`), 2 loads each | identical to #514 alone and to master |
| `test_irqb_verbose`, HblankEmuTest | identical to the head (1 state, 69 px) |
| Contra III, first 10,000 frames | identical to the head |
| `slhv-wrio` NTSC and PAL | 6 of 6; latched H 1-2 dots later than #514 alone (this PR's IRQ timing); V identical |

## Hardware kit

`kit/`: nine small homebrew test ROMs (no commercial data) that measure the H/V IRQ timer, the `$2137` latch and the
light-gun latch on a real console and leave a table on screen; no input needed except gunprobe (Super Scope). How to run
them and what to send back: `kit/README.md`. Sources: `kit/src/` (bass 65816; `gen.py` builds the IRQ ROMs, `KIT=1` for the
kit screens). They would settle the provisional constants of commit 3 (`ophct` row 18 against row 17 separates the
VTIME=0 case), the PAL long line, and `slhv-wrio` on hardware.

## Files

- `irq/demo_irq.png`, `irq/wrap-ntsc.png`
- `hblankemu/ab.png`, `hblankemu/hblankemu-c5-ae0818c.frames.tsv`
- `kss/`: the Kirby Super Star images above
- `hashes/`: the head's hash logs from the equivalence check (Contra III: `contra3-*.frames.tsv`); `splice.py`
- `kit/`: the hardware kit
- Release assets: the three cores, the Contra III full run (`contra3-4363M-513v3-ae0818c.mp4` and `.frames.tsv`)

Recording gate (`../tools/recgate.py`): every recording used here passes (missed, torn, duplicates, late and lost 0),
except where noted: the `irq-wrap` runs' interlace switch (outside the result window), one `resize` row in the 239-line
Contra tests (as on master), and the Contra III takes above (the published video is spliced from their clean frames).
