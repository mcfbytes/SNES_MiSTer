# Evidence for the SNES H/V IRQ, PPU timing and `$2137` PRs (refs #460)

This branch holds evidence only: no RTL. The changes live on these branches of `mcfbytes/SNES_MiSTer`:

| PR | branch | commit | base |
|---|---|---|---|
| A: H/V IRQ flag 6 master clocks later | `irq-timing` | `2ff03cf` | `2302683` |
| B: PPU BG fetch, output and force-blank timing | `ppu-460-pr` | `18f47d6` (one commit on A) | `2ff03cf` |
| C: `$2137` latches only while `$4201` bit 7 is set | `slhv-wrio-gate` | `57160ab` | `2302683` |

The cores in every comparison:

| label | build |
|---|---|
| upstream | `2302683` (master) |
| +IRQ | `2ff03cf` (A) |
| +IRQ+PPU | `0148bb7`, the same tree as `18f47d6` (A + B). One comparison (SMAS, section 4) uses **f2**, an earlier build of B without its Mode 7 fix. f2 and the final build are frame-identical on every non-Mode 7 recording in both: the four #460 movies, Voronoi, TwistIT and HblankEmuTest. |

All builds use Quartus 17.0.2 with the `.qsf`'s seed. All recordings come from a DE10-Nano running the core, captured with
[tasty](https://github.com/mcfbytes/Tasty_MiSTer), which replays a movie from power-on and records every frame the
core outputs, before the scaler. Each run is deterministic: the same movie on the same core gives the same frames.

## Index: A/B packs

One directory per test under [`ab/`](ab/README.md): the ROM or its link and sha256, the tasty movie, a labelled side-by-side
(upstream | PR | bsnes | MesenCE | hardware), the MiSTer recordings as MP4, and tasty's per-frame hash logs. Prebuilt cores
and raw AVIs: pre-release [`evidence-460-cores`](https://github.com/mcfbytes/SNES_MiSTer/releases/tag/evidence-460-cores).
Every MiSTer recording passed a quality gate (no missed, torn, dropped or late frame; `ab/README.md`). "—" = no capture.

**PR A** (H/V IRQ +6 master clocks, `2ff03cf`)

| test | what to look at | upstream | PR A | bsnes | MesenCE | hardware |
|---|---|---|---|---|---|---|
| [test_irqb_verbose](ab/A/test_irqb_verbose/) | checks against the ROM's built-in expected values (byuu) | 8 of 32 wrong | 32/32 | 32/32 (2014) | 32/32 | — |
| [irqprobe](ab/A/irqprobe/) | IRQ wake/entry H, 16 rounds | NTSC 0/18 rows equal bsnes; PAL 4/18 in band | 9/18 equal, 6 more within 1 dot; PAL 17/18 | reference | 18/18 | — |
| [busprobe](ab/A/busprobe/) | bus access and IRQ entry H | NTSC 0/23; PAL 7/23 | 20/23; PAL 22/23 | reference | 23/23 | — |
| [mode7_hirq](ab/A/mode7_hirq/) (#274, #275) | H-IRQ value where the M7VOFS line flickers | matches 6 of 7 hardware thresholds; `$FFFF` no IRQ | **every threshold about 1 H step earlier, 0 of 7**; `$FFFF` no IRQ | not a reference (differs from hardware) | not a reference (line at every H) | paulb-nl, 1-chip (#274) |
| [games](ab/A/games/) | attract modes, 9,000 frames | | Kawasaki, WeaponLord, Aladdin identical; Chuck Rock, Cybernator and the Full Throttle water race differ by 1-4 dots on one line; Full Throttle's attract picks another track later | | | — |

**PR B** (PPU fetch/output/force-blank timing, `18f47d6` = A + B; +IRQ alone as context)

| test | what to look at | upstream | PR A+B | +IRQ only | bsnes v115 | MesenCE | hardware |
|---|---|---|---|---|---|---|---|
| [bg_fb](ab/B/bg_fb/) | bar end, red N, at start / R1 / R2 | N: no / 2 of 3 / yes | no / no / 2 of 3 | 1-2 of 3 / 2-3 of 3 / no | no N at any point | no N at any point | no / no / yes (paulb-nl, #430/#460) |
| [contra_test_fb](ab/B/contra_test_fb/) | last line: tile at x 52-60, start / R1 | 1-2 of 3 / yes | **no / yes** | 3 of 3 / yes | — (224 lines) and no tile | no tile at any point | no / yes (paulb-nl, #460) |
| [bg_dense](ab/B/bg_dense/) | bar-end x where the N shows | 160-161, 168-169 | **159-160, 167-168** | 160-161, 168-169 | no N | no N | 151-152, 159-160, 167-168 (paulb-nl video) |
| [hblankemu](ab/B/hblankemu/) | lines 2-3 | garbled in 2 of 4 states | **"Beha UR / -Emu" every frame** | worse | no sprites | every sprite | "Beha UR / -Emu" (paulb_nl) |
| sweep screens: [hvdma_max, INIDISP](#3-regression-sweep-b-against-a) | hvdma_max / brightness step dot / first lit dot | striped / 76-77 / 41 | clean / 74-75 / 39 | 1,792 px / 77-78 / 43 | clean / none / whole line | clean / 76-77 / 41 | — |
| [mode7_hirq](ab/A/mode7_hirq/) | as PR A | | frame-identical to PR A | | | | |

**PR C** (`$2137` latches only while `$4201` bit 7 is set, `57160ab`)

| test | what to look at | upstream | PR C | bsnes 2014 | MesenCE | hardware |
|---|---|---|---|---|---|---|
| [slhv-wrio](ab/C/slhv-wrio/) (ours, NTSC and PAL) | 6 cases, latched V | 3 of 6 PASS (cases 2, 3, 6 latch at the read) | 6/6 | 6/6 | 6/6 | — (photo wanted) |
| [probe rows](ab/C/probe-rows/) | irqprobe `2137 WR7F`, busprobe `IRQ 4203L` | the read overwrites the latch (040, 04A) | the earlier latch survives (097-098, 036) | 09A, 037-038 | 09A, 037-038 | — |

## 1. #460 force-blank tests (PR B), against paulb-nl's hardware captures

paulb-nl's test ROMs and hardware captures: `bg_fb.smc` ([#430](https://github.com/MiSTer-devel/SNES_MiSTer/issues/430),
hardware video there) and `contra_test_fb.smc`
([#423](https://github.com/MiSTer-devel/SNES_MiSTer/issues/423#issuecomment-3397223469)). Photos from
[#460](https://github.com/MiSTer-devel/SNES_MiSTer/issues/460) are copied here with credit:
`460/hardware-bg_fb-paulb-nl.png` and `460/hardware-contra_test_fb-paulb-nl.png`.

- `460/bg_fb-states.png`: the bar row of `bg_fb` at start, after one R and after two R. Each block shows every
  distinct frame in that window; a mid-line IRQ lands on one of 3 dot phases, so each window has 3 frames. Each
  frame is captioned with its share of the window.
- `460/contra_last-states.png`: the last line (239-line mode, V-IRQ on the last line) of `contra_test_fb`: start, R x1, R x2.
- `460/bg_dense-bar-end-vs-N.tsv`: per bar-end position, the frames showing the red "N" (16 R presses), with the same
  measurement run on paulb-nl's hardware video (`tools/feat.py`).
- `460/*.mp4`: the three cores stacked (upstream, +IRQ, +IRQ+PPU), the whole movie, 2x.

| observable | hardware | upstream | +IRQ | +IRQ+PPU |
|---|---|---|---|---|
| bg_fb, start: red N | absent | absent | in 1 of 3 phases | absent |
| bg_fb, after 1 R: red N | absent | in 2 of 3 phases | in 2 of 3 | absent |
| bg_fb, after 2 R: red N | present | present | absent (bar moved) | present in 2 of 3 |
| bg_dense: bar-end x where the N shows | 151-152, 159-160, 167-168 | 160-161, 168-169 | 160-161, 168-169 | **159-160, 167-168** |
| bg_dense: bar end at start | ~156 (photo: black 38-156) | 157-158 | 159 | 155-156 |
| contra_test_fb last line, start: release mark x | 37-38 | 38-39 | 39-40 | 36-37 |
| contra_test_fb last line, start: tile at x 52-60 | absent | in 2 of 3 phases | in 3 of 3 | **absent** |
| contra_test_fb last line, after 1 R: tile | present | present | present | present |

The IRQ fix alone (A) moves these tests further from hardware: the core's PPU sampled force blank and fetched BG
tiles slightly early, and the early IRQ partly hid that. B moves the BG fetch 2 dots later and math/output 1 dot later,
and applies force blank while /PAWR is low. Together, A and B match the hardware captures on all three observables.

## 2. HblankEmuTest (PR B)

The test is Motive's HblankEmuTest (force blank in h-blank must stop sprite loading). The hardware photo is from paulb_nl,
taken on all his consoles and stable: `hblankemu/hardware-paulb_nl-bpuXsI4.png`
([nesdev forum t=18216](https://forums.nesdev.org/viewtopic.php?t=18216)). bsnes and Mesen load every sprite here.

`hblankemu/hblankemu-states.png` shows the first three distinct frames of frames 300-900 (of 4 or more); `hblankemu.mp4`
covers the whole run.

- upstream: line 2 is garbled in two of four states ("BEHAVI..." bleeds through "Beha").
- +IRQ: worse; one 38-frame state shows the full "Behaviour / -Emulator".
- +IRQ+PPU: lines 2-3 read "Beha UR" / "-Emu" in every frame, as on hardware.
- All cores show "THIS IS CORRECT" on line 1, where hardware keeps the "Incor" sprites; a sprite-side item that stays open.

## 3. Regression sweep (B against A)

281 test ROMs (`sweep/roms.txt`: the higan collection by KungFuFurby, jonasquinn, Sour, tukuyomi and undisbeliever, plus
undisbeliever's `snes-test-roms`). Each ROM was loaded by MGL and screenshotted after a fixed time, once on +IRQ and once
on +IRQ+PPU; the two were compared pixel for pixel (`tools/sweepdiff.py`).

- **262 of 281 pixel-identical.** The 19 that differ are listed in `sweep/sweep-m1-vs-pr2.tsv`.
- **12 of the 19 are run-to-run noise.** They also differ between two runs of the same stock core
  (`sweep/noise-stock-run-a-vs-run-z.tsv`): speed_test_v51, test_hello, test_noise, ppubusact, five auto-joypad
  timing ROMs, hdmaen_latch_test_2 (u-), dma-ends-hdma-start-1-ch (u-).
- **The other 7, rerun twice on each core** (`sweep/screens/`; rows upstream / +IRQ / +IRQ+PPU, bsnes, Mesen):

| ROM | upstream | +IRQ | +IRQ+PPU | reference |
|---|---|---|---|---|
| 001 hvdma | varies run to run on every core; the sweep's grey frame came from being the first ROM loaded after a movie | | | |
| 002 hvdma_max | 3,568 non-green px (striped left column) | 1,792 | **0 (clean green)** | bsnes, Mesen: clean green |
| 016 HblankEmuTest | see section 2 | | **matches hardware** | |
| 192 hdmaen_latch_test_2 | varies run to run | | +IRQ+PPU pass 1 == +IRQ pass 1 | known open item (below) |
| 193/218 inidisp_brightness_delay | brightness step at dot 76-77 | 77-78 | 74-75 | Mesen 76-77, bsnes none |
| 195/219 inidisp_enable_display_mid_frame | first lit dot on line 88: 41 | 43 | 39 | Mesen 41, bsnes whole line |

The two INIDISP ROMs are stable on every core across both passes. Their shift has the same mechanism the force-blank
tests validate: brightness and force blank apply at the math/output stage, which now sees each pixel 3 dots later. Mesen
does not match the bg_fb hardware windows either, so it is not a reference for this timing. We have no hardware capture
of these two ROMs.

## 4. Games and demos (B against A)

`games/game-ab.tsv`: per-frame hashes of whole movies, +IRQ against +IRQ+PPU (`tools/hashcmp.py`; tasty's encoder
duplicates are excluded).

- Identical: Contra III TAS (45,442 frames valid in both runs, Mode 7 stages included), Super Punch-Out!! TAS (57,224),
  Super Mario Kart attract (10,800) and F-Zero attract (10,800, both Mode 7), Voronoi split-screen demo (3,600). Both
  TAS runs finished on both cores with every input applied on time.
- TwistIT: 2 of 14,400 frames differ by a few pixels on one scanline.
- SMAS (Super Mario Bros.) TAS, on f2 (the pr2 run got one late input from the replay side and left the movie): 19 of 18,235 frames differ, all by 1-2 px at the left end of line 31, the status-bar IRQ split
  (`games/smas-line31-zoom.png`). Every movie stays in sync to the end.
- f2 (before the Mode 7 fix) differed on the last 2 pixels of every Mode 7 line; the final commit's Mode 7 output is
  identical to +IRQ on both Mode 7 attract modes and on Contra III.

## 5. The game in #460 (Contra SNES MSU-1)

Not addressed by these PRs and not claimed. Its poster-menu symptom appears where the game releases force blank
mid-line, so it may be related to the same timing; it needs hardware statistics before anything can be said.

## 6. H/V IRQ timing (PR A) and the `$2137` gate (PR C)

- `irq/irqb-verbose-{before,after}.png`: byuu's `test_irqb` (checked against the ROM's built-in expected values), rebuilt with a verbose
  results screen (`probes/test_irqb_verbose/`: `gen.py` + `patch.asm` applied to the original `test_irqb.smc`; the
  measurement code is unchanged). Upstream: 8 of 32 checks wrong (sub-tests 4 and 5, 3-4 dots early). With A: 32/32.
- `irq/{busprobe,irqprobe}-{before,after}.png` and `pal-*`: two probe ROMs written for this (`probes/`, source and
  ROMs; `gen.py` builds them with bass-untech and undisbeliever's `snes-test-roms` font, checked out beside it; `refs.sh`
  regenerates the references). Each probe times one bus access or IRQ entry with the H/V counter latch, 16 rounds. The references are
  bsnes 2014 accuracy and MesenCE 2.2.1, which agree on all 41 NTSC rows. Before A, every IRQ-timed row is 1-2 dots
  early. With A, busprobe matches on 21 of 23 rows; the other 2 each have one round landing on DRAM refresh. irqprobe
  matches on 9 of 18 rows, 7 more are within 1 dot, and 2 NOP-sled rows sit on a phase boundary, where the two
  emulators also spread in PAL. PAL: 41 of 41 rows fall inside the bsnes/Mesen band, against 11 of 41 before.
  Per-row tables: `irq/probe-tables.md`.
- The section 6 measurements were taken before master moved to `2302683`. "Before" is a control build of `c61bfd4`;
  `2302683` adds only #511 (CX4 DMA timing), and A's patch is identical on both. The "after" screenshots come from a
  build with both A and C. C affects only the irqprobe row `2137 WR7F` and the busprobe row `IRQ 4203L`.
- Regression for A (119 IRQ/NMI/DMA/HDMA/timing ROMs, the c61bfd4 control against +IRQ): 105 identical. test_irqb fails → passes. The
  noise ROMs are as in section 3. Sour timing_test (WIP) end H-POS $10 → $0E; dma-ends-hdma-start still "HDMA OK";
  hdmaen_latch_test(_2) red lines change (below).
- **Known open item:** `hdmaen_latch_test_2` red lines (8 channels x 13 HTIMEs) are 35 upstream, about 15-17 with A
  (and the same with B), against 52 on bsnes 2014 accuracy and 28-32 on MesenCE (it varies between runs). The two emulators disagree, and we have no hardware
  count. The early IRQ was partly masking a separate HDMAEN latch question.
- **`slhv-wrio` (PR C), a test ROM written for it** (`ab/C/slhv-wrio/`: source, build script, NTSC and PAL ROMs, MGLs,
  movies). No input; six cases, each priming a latch at line 40 and then acting at line 120, judged on the latched V
  against bsnes 2014 accuracy (MesenCE agrees on every V). Upstream passes 3 of 6: a `$2137` read with `$4201` bit 7 clear
  latches (case 2), even after bit 7 was set and cleared earlier (case 3, fullsnes's "or was set"), and three reads in a row
  latch each time (case 6). PR C passes 6 of 6, NTSC and PAL. Both cores latch on the 1→0 write itself (case 4, the
  EXTLATCH falling edge; `JOY2_P6_in` is 1 with no gun or SNAC) and not on 0→1 (case 5), as both emulators do.
  No real-console result yet.
- **A hardware reference PR A does not match: paulb-nl's mode 7 H-IRQ tests (#274)** (`ab/A/mode7_hirq/`). Upstream
  reproduces the 1-chip console's flicker thresholds on six of seven variants; PR A moves each about one H step earlier
  and matches none. A+B is frame-identical to A there. `test_irqb` (fixed by A) and these tests pull in opposite directions.

## 7. Timing closure (MiSTer Seedy, 30 seeds per side, Quartus 17.0.2)

| PR | run | result |
|---|---|---|
| A | `irq-timing` 2ff03cf vs 2302683: queued; the report will follow as a comment on the PR | the same patch on c61bfd4: [run 37205363393](https://github.com/mcfbytes/SNES_MiSTer/actions/runs/37205363393), `seedy/A-earlier-*.md`. "Possible regression": 3/30 seeds meet timing against 12/30; `emu c2` setup fails more often, on master's own `sdram|rbuf → P65C816|P` path |
| A+B | [run 37264587249](https://github.com/mcfbytes/SNES_MiSTer/actions/runs/37264587249), `seedy/B-ppu-460-0148bb7-vs-2302683.md` | 9/30 seeds meet timing against 8/30 (p 1.00). Hold flag: 6/30 seeds against 1/30, all on existing `msu_data_store`/`savestates` → `ddram` cache-address crossings, no PPU paths: `seedy/B-hold-analysis.md` |
| C | `slhv-wrio-gate` 57160ab vs 2302683: queued; the report will follow as a comment on the PR | the same patch on c61bfd4: [run 37214664117](https://github.com/mcfbytes/SNES_MiSTer/actions/runs/37214664117), "no measurable regression" (8/30 against 12/30, p 0.41) |

## 8. Reproducing a recording

Build the core from the branch and put the `.rbf` on the SD card. Then:

```sh
tasty play <movie> --rom <rom> --core <core.rbf> --record <outdir> --linger 0 --no-splash [--lead -1]
```

`<outdir>/<movie>.frames.tsv` lists every frame (movie frame, hash, size, encoder duplicate flag) and `<outdir>/*.avi` holds the
video. `tools/hashcmp.py a.tsv b.tsv` compares two runs by movie frame. `tools/vsheet.sh` and `tools/sbs.sh` made the
sheets and MP4s here, for example:

```sh
X0=200 CW=200 VS=8 tools/vsheet.sh <recdir> bg_fb 4 20 bg_fb-states.png "upstream=m0,+IRQ=m1,+IRQ+PPU=pr2" \
  "start:10:300" "after R x1:305:420" "after R x2:425:540"
X0=0 CW=160 VS=24 tools/vsheet.sh <recdir> contra_last 236 3 contra_last-states.png "upstream=m0,+IRQ=m1,+IRQ+PPU=pr2" \
  "start:540:650" "after R x1:655:770" "after R x2:775:890"
sh tools/sbs.sh <recdir> bg_fb 0 bg_fb.mp4 m0:upstream m1:+IRQ pr2:+IRQ+PPU
```

Here `<recdir>/<tag>-<movie>/` is a tasty `--record` directory.

| recording | movie (`movies/`) | ROM (not included) | ROM SHA-256 |
|---|---|---|---|
| bg_fb | `bg_fb.lsmv` (R at 300/420/540/660) | paulb-nl `bg_fb.smc`, #430 | `30755fb70bc883163bdff41efe951ff27b0f5b77c67f1cb27242d6e35e95ccc5` |
| bg_dense | `bg_dense.lsmv` (`bg_dense.script`: R every 60 frames) | same | same |
| contra_last | `contra_last.lsmv` (`contra_last.script`: 12 Up, then R) | paulb-nl `contra_test_fb.smc`, #423 | `419ecacf802cf7b8b7eabcd3e2f2c1fed9ec9411eab15172aaac5f1c859a8fb4` |
| contra_fb | `contra_fb.lsmv` | same | same |
| HblankEmuTest | `hblankemu.lsmv` (900 idle frames) | Motive, nesdev t=18216 | `80706521642cc6183f406f74249d18f0ff3a501e574dd5acae67fe0c04bf0fc7` |
| Voronoi | `voronoi.lsmv` (scripted 2-pad) | marian-m12l "SNES dynamic split-screen" (SNESDEV 2025) | `82be8f1713b0ec90842d6c075c23ffe23b2a1246a71fb6b9154235ce63b26072` |
| TwistIT | `twistit.lsmv` | Resistance "TwistIT" (Demobit 2018), 64K mirrored to 128K | `5a76bd8a6a7471d5d2036f9c8910fc204fd66f27505185ac2f791229190ddec2` |
| Super Mario Kart attract | `smk-attract.lsmv` | Super Mario Kart (USA) | `2ada8919688087be60a6a48cace8f877add60c45d2e5d09e2442faa55be62a49` |
| F-Zero attract | `fzero-attract.lsmv` | F-Zero (USA) | `bf16c3c867c58e2ab061c70de9295b6930d63f29f81cc986f5ecae03e0ad18d2` |
| SMAS SMB | `smas-6744M.bk2` ([TASVideos 6744M](https://tasvideos.org/6744M)), `--lead -1` | Super Mario Collection (Japan) | SHA-1 `BEE927B5FFE277EBD537B0872D2424EEAC37B8E3` |
| Contra III | `contra3-4363M.bk2` ([TASVideos 4363M](https://tasvideos.org/4363M)) | Contra III - The Alien Wars (USA) | `a93ea87fc835c530b5135c5294433d15eef6dbf656144b387e89ac19cf864996` |
| Super Punch-Out!! | [TASVideos 4933M](https://tasvideos.org/4933M) (`spo-4933M.bk2`, not copied here) | Super Punch-Out!! (USA) | as TASVideos 4933M |

The `.lsmv` movies are generated by `tools/mklsmv.py <rom> <out.lsmv> <frames> [script]`. They hold the ROM's SHA-256
and no ROM data. Test-ROM sweep: MGL load, then a screenshot after ~45 s (20 s for short
ROMs) per ROM; compare with `tools/sweepdiff.py <dir> <tagA> <tagB>`. `tools/stack.py` made `sweep/screens/`.

Not committed, by size (available on request): the raw tasty recordings (AVI + frame logs) and the 60 per-seed Seedy
STA reports (in the runs' `seedy-reports` artifacts).

Credits: paulb-nl (test ROMs, hardware photos and videos), paulb_nl/Motive (HblankEmuTest), byuu (test_irqb),
undisbeliever (snes-test-roms; its 1bpp font is used by the probe ROMs), the higan test-ROM authors, the TASVideos
authors (HappyLee for 6744M and the authors of 4363M and 4933M), MesenCE and bsnes for the references.
