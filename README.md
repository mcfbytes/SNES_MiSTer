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
| +IRQ+PPU | `0148bb7`, the same tree as `18f47d6` (A + B). Some recordings (marked **f2**) come from an earlier build of B, without B's Mode 7 fix. These test ROMs do not use Mode 7, and f2 and B's final build are frame-identical on every non-Mode 7 recording we have (Voronoi 3,600 frames, TwistIT 14,400, HblankEmuTest 900). |

All builds use Quartus 17.0.2 with the `.qsf`'s seed. All recordings come from a DE10-Nano running the core, captured with
[tasty](https://github.com/mcfbytes/Tasty_MiSTer), which replays a movie from power-on and records every frame the
core outputs, before the scaler. Each run is deterministic: the same movie on the same core gives the same frames.

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

| observable | hardware | upstream | +IRQ | +IRQ+PPU (f2) |
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

- Identical: Voronoi split-screen demo (3,600), Super Mario Kart attract (10,800) and F-Zero attract (10,800, both Mode 7),
  Super Punch-Out!! TAS (57,224, on f2).
- TwistIT: 2 of 14,400 frames differ by a few pixels on one scanline.
- SMAS (Super Mario Bros.) TAS, on f2: 19 of 18,235 frames differ, all by 1-2 px at the left end of line 31, the status-bar IRQ split
  (`games/smas-line31-zoom.png`). Every movie stays in sync to the end.
- f2 (before the Mode 7 fix) differed on the last 2 pixels of every Mode 7 line; the final commit's Mode 7 output is
  identical to +IRQ on both Mode 7 attract modes.

## 5. Contra (SNES) MSU-1 poster menu, the game in #460: unchanged, needs hardware statistics

`contra-msu/04-gap-*.png`: for each poster transition kind, the black gap between posters, zoomed on rows 217/237 at
x 96-167: hardware video (1 sample), Mesen, upstream, +IRQ, +IRQ+PPU. `06-gap-frame-hw-pr2-mesen.png` shows one whole frame.

- The game force-blanks for a poster DMA that overruns vblank, then releases force blank mid-line (dot ~148). All cores
  and the hardware show fetch garbage at that release point; Mesen does not.
- The cores sometimes show an 8-pixel tile on row 237 in NES->Arcade and Arcade->Movie. The hardware video does not, but
  it has only one sample of each transition. The rate is a per-transition lottery (DMA end jitter): 7 of 22 on
  upstream, 4 on +IRQ, 11 on +IRQ+PPU (Fisher p 0.36 / 0.055). **PR B does not fix this symptom.** It moves the tile by
  one column and puts the Movie->NES white segment's start at x 124-125, against 125 on hardware (+IRQ: 126-129).
- Outside those rows, the three cores are frame-identical to each other. They also match Mesen (aligned by
  transition) apart from the blink phase of the arrow sprites. The earlier
  "one-frame artefacts" count was poster-slide motion, not glitches.
- Deciding this needs about 30 or more hardware captures per transition kind.

## 6. H/V IRQ timing (PR A) and the `$2137` gate (PR C)

- `irq/irqb-verbose-{before,after}.png`: byuu's `test_irqb` (expected values from a real SNES), rebuilt with a verbose
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

## 7. Timing closure (MiSTer Seedy, 30 seeds per side, Quartus 17.0.2)

| PR | run | result |
|---|---|---|
| A | ⟪PENDING: tonight's run, `irq-timing` 2ff03cf vs 2302683⟫ | the same patch on c61bfd4: [run 37205363393](https://github.com/mcfbytes/SNES_MiSTer/actions/runs/37205363393), `seedy/A-earlier-*.md`. "Possible regression": 3/30 seeds meet timing against 12/30; `emu c2` setup fails more often, on master's own `sdram|rbuf → P65C816|P` path |
| A+B | [run 37264587249](https://github.com/mcfbytes/SNES_MiSTer/actions/runs/37264587249), `seedy/B-ppu-460-0148bb7-vs-2302683.md` | 9/30 seeds meet timing against 8/30 (p 1.00). Hold flag: 6/30 seeds against 1/30, all on existing `msu_data_store`/`savestates` → `ddram` cache-address crossings, no PPU paths: `seedy/B-hold-analysis.md` |
| C | ⟪PENDING: tonight's run, `slhv-wrio-gate` 57160ab vs 2302683⟫ | the same patch on c61bfd4: [run 37214664117](https://github.com/mcfbytes/SNES_MiSTer/actions/runs/37214664117), "no measurable regression" (8/30 against 12/30, p 0.41) |

## 8. Reproducing a recording

Build the core from the branch and put the `.rbf` on the SD card. Then:

```sh
tasty play <movie> --rom <rom> --core <core.rbf> --record <outdir> --linger 0 --no-splash [--lead -1]
```

`<outdir>/<movie>.frames.tsv` lists every frame (movie frame, hash, size, encoder duplicate flag) and `<outdir>/*.avi` holds the
video. `tools/hashcmp.py a.tsv b.tsv` compares two runs by movie frame. `tools/vsheet.sh` and `tools/sbs.sh` made the
sheets and MP4s here, for example:

```sh
X0=200 CW=200 VS=8 tools/vsheet.sh <recdir> bg_fb 4 20 bg_fb-states.png "upstream=m0,+IRQ=m1,+IRQ+PPU=f2" \
  "start:10:300" "after R x1:305:420" "after R x2:425:540"
X0=0 CW=160 VS=24 tools/vsheet.sh <recdir> contra_last 236 3 contra_last-states.png "upstream=m0,+IRQ=m1,+IRQ+PPU=f2" \
  "start:540:650" "after R x1:655:770" "after R x2:775:890"
sh tools/sbs.sh <recdir> bg_fb 0 bg_fb.mp4 m0:upstream m1:+IRQ f2:+IRQ+PPU
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
| Contra SNES MSU-1 | `contra_msu.lsmv` (7,370 frames, 36 Right) | "Contra SNES" (MSU-1) as described in #460, with its `.msu` and `-N.pcm` files | `93e505bdb35acdebc15d73f32bf444a7d8d7cfa53b7089af5b9f7ea8feb6efbe` |

The `.lsmv` movies are generated by `tools/mklsmv.py <rom> <out.lsmv> <frames> [script]`. They hold the ROM's SHA-256
and no ROM data. The Contra MSU-1 recordings came from a development tasty build that also serves the MSU-1 data
track; the released tasty does not do that yet. Test-ROM sweep: MGL load, then a screenshot after ~45 s (20 s for short
ROMs) per ROM; compare with `tools/sweepdiff.py <dir> <tagA> <tagB>`. `tools/stack.py` made `sweep/screens/`.

Not committed, by size (available on request): the raw tasty recordings (AVI + frame logs) and the 60 per-seed Seedy
STA reports (in the runs' `seedy-reports` artifacts).

Credits: paulb-nl (test ROMs, hardware photos and videos), paulb_nl/Motive (HblankEmuTest), byuu (test_irqb),
undisbeliever (snes-test-roms; its 1bpp font is used by the probe ROMs), the higan test-ROM authors, the TASVideos
authors (HappyLee for 6744M and the authors of 4363M and 4933M), MesenCE and bsnes for the references.
