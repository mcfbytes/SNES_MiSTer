# SNES H/V IRQ timing kit — for flash-cart owners

Nine small test ROMs that measure how the S-CPU's H/V IRQ timer, the `$2137` latch and the light-gun latch behave
on a real console. **No input is needed** (except gunprobe, which needs a Super Scope). Each ROM boots, runs for a
few seconds and leaves a table on screen. We know what MiSTer, bsnes and Mesen show; the column we do not have is
yours. There is no PASS/FAIL on the IRQ screens on purpose: nobody knows the hardware answer yet.

## What to do

1. Copy the `.sfc` files to the flash cart (FXPAK Pro / SD2SNES, Everdrive or similar). Use the `-ntsc` ROMs on an
   NTSC console and the `-pal` ROMs on a PAL console (the ROM header carries the region; most carts do not care).
2. Boot each ROM and wait: **wrap 10 s, ophct 10 s, enable 40 s** (PAL: a bit longer), slhv-wrio 3 s, gunprobe runs
   continuously. The screen stops changing when the test is done.
3. **Photograph the screen** so that every digit is readable: fill the frame with the picture, no flash, hold the
   phone still, and check the photo before moving on. A composite/S-video/RGB capture is just as good.
4. Note your **console model**: 1-CHIP or 3-chip (the serial-number prefix and the board revision if you know it,
   e.g. `SHVC-CPU-01`, `SNS-CPU-GPM-02`, `SNS-CPU-1CHIP-01`), NTSC or PAL, and the flash cart used.
5. Return the photos as a comment on the MiSTer SNES core PR
   [MiSTer-devel/SNES_MiSTer#513](https://github.com/MiSTer-devel/SNES_MiSTer/pull/513) (drag the images into the
   comment box), with the console details. One photo per ROM is enough; two consoles of different revisions are
   worth more than two photos of one.

> **Note (PR #513 v3).** The "MiSTer #513" columns below were measured on an earlier version of the PR (`f1cfd5f`).
> The current head `ae0818c` gives MesenCE's value on all 20 NTSC `irq-wrap` rows (`../README.md`), and gunprobe reads
> H=0A9 V=070, the same as master.

`SHA256SUMS` lists the files. The ROMs are 128 KiB LoROM images (32 KiB of code mirrored); they do not write to SRAM.

## The ROMs

| file | region | what it shows | wait |
|---|---|---|---|
| `irq-wrap-ntsc.sfc` / `-pal` | NTSC / PAL | IRQs counted per frame for 20 (PAL 21) H/V/HV settings, including the frame-wrap corner cases | 10 s |
| `irq-enable-ntsc.sfc` / `-pal` | NTSC / PAL | whether a `$4200`/`$4207` write stepped across the trigger point still produces the IRQ; 12 rows × 16 steps, min and max over 8 rounds | 40 s |
| `irq-ophct-ntsc.sfc` / `-pal` | NTSC / PAL | the H counter (`$2137`/`$213C`) read as the first instruction of the IRQ handler, for 23 settings, min and max over 8 rounds | 10 s |
| `slhv-wrio.sfc` / `pal-slhv-wrio.sfc` | NTSC / PAL | whether `$2137` latches while `$4201` bit 7 is clear (6 cases; this one does show PASS/FAIL against bsnes) | 3 s |
| `gunprobe.sfc` | NTSC header | the light-gun latch H/V every frame with min/max, Super Scope on port 2 aimed at the centre of the screen | continuous |

The IRQ screens use white text only. `1FF` means "no IRQ arrived" (the NMI rescued the row). An `N` after a
wrap row means a frame went by in which the console serviced no NMI (we do not expect that on hardware; the
MiSTer core does it today and the marker is there to prove the fix).

## Reference values

Columns: **bsnes** = bsnes 2014 accuracy (libretro), **Mesen** = MesenCE 2.2.1, **MiSTer master** = SNES_MiSTer
2302683, **MiSTer #513** = PR #513 at f1cfd5f. The two MiSTer columns were measured on a DE10-Nano with an earlier
build of the same ROMs (single-sample enable rows, and an ophct build whose vblank wait could hit an NMI race, which
is why some rows there read `1FF`; their numbering is remapped to the rows below). "a/b" = min/max over the frames
or rounds. The emulator columns come from the exact ROMs in this kit.

### irq-wrap (IRQs per frame; frames 3-11 of 12)

Case notation: `HV v.h` = IRQ at V=v and H=h; `H h` = every line at H=h; `V v` = once per frame at V=v; `i` =
interlace on (the first five rows; the screen flickers once when they finish). NTSC last line = 261, PAL = 311.

| row | case (NTSC) | bsnes | Mesen | MiSTer master | MiSTer #513 | model (p310801/p310687) | your console |
|---|---|---|---|---|---|---|---|
| 00 | iHV 0.339 | 1 | 2 | 1 | 1 | 2 | |
| 01 | iHV 262.339 | 0 | 0 | 0/1 | 0/1 | 0 | |
| 02 | iHV 262.0 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | |
| 03 | iH 339 | 262/263 | 262/263 | 262/263 (one frame doubled: an NMI lost) | 262/263 | 262/263 | |
| 04 | iHV 261.339 | 0/1 | 0/1 | 1 | 1 | 0/1 | |
| 05 | HV 261.339 | 0 | 0 | 1 | 1 | **0** (hardware, paulb-nl) | |
| 06 | HV 0.339 | 1 | 2 | 1 | 1 | **2** (hardware, paulb-nl) | |
| 07 | HV 0.338 | 1 | 1 | 1 | 1 | 1 | |
| 08 | HV 261.338 | 1 | 1 | 1 | 1 | 1 | |
| 09 | HV 1.339 | 1 | 1 | 1 | 1 | 1 | |
| 10 | HV 0.0 | 1 | 1 | 1 | 1 | 1 | |
| 11 | HV 261.0 | 1 | 1 | 1 | 1 | 1 | |
| 12 | H 339 | 261/262 | 261/262 | 261/262 (+N) | 261/262 | 261/262 (Anomie's notes say 260/261) | |
| 13 | H 338 | 262 | 262 | 262 (+N) | 262 (+N) | 262 | |
| 14 | H 0 | 262 | 262 | 262 | 262 | 262 | |
| 15 | H 340 | 0 | 0 | 0 | 0 | 0 | |
| 16 | V 261 | 1 | 1 | 1 | 1 | 1 | |
| 17 | V 0 | 1 | 1 | 1 | 1 | 1 | |
| 18 | V 262 | 0 | 0 | 0 | 0 | 0 | |
| 19 | HV 262.0 | 0 | 0 | 0 | 0 | 0 | |

PAL (`irq-wrap-pal.sfc`): rows 00-04 as above with 312/311 for 262/261, row 05 = `iH 340` (bsnes 0, Mesen 0, MiSTer
0/1, model 0/1: the 1368-clock long line), rows 06-20 = the NTSC rows 05-19 with 311 for 261. Measured PAL values:
row 03 bsnes 312/313, Mesen 312/313, MiSTer 312/313; row 13 (H 339) bsnes 312, Mesen 311/312, MiSTer 312; rows 14/15
(H 338, H 0) 312 on all. Note: PAL has no short line, so `H 339` is 312 every frame.

### irq-enable (a write stepped across the trigger; 1 = the IRQ flag was set, 0 = not)

Each row is 16 steps (d = 0..15, one dot each) with two lines: **min** and **max** over 8 rounds. The sync point is
an HV IRQ at V=100, H=40; HTIME under test = 40 + base + d. Rows: E0/E1 disable, set HTIME, enable HV (base 52/60);
E2/E3 the same with one NOP before the enable; E4/E5 HTIME written with HV left enabled (base 20/28); E6 enable V-only
with VTIME = 92+d mid-line (only d=8 can fire); E7/E8 disable then re-enable back to back (base 48/64); E9/E10 an early
`$4211` read (bit 1) then a late one (bit 0), E10 with a NOP first (so 2 = early read saw it, 1 = only the late read,
3 = both: the un-clearable window); E11 = E0 with H-only.

| row | bsnes min / max | Mesen min / max | MiSTer master (1 sample) | MiSTer #513 (1 sample) | your console |
|---|---|---|---|---|---|
| E0 | 0000000000000001 / 0000000000000011 | 0000000000000000 / 0000000000000001 | 0000000000000111 | 0000000000000011 | |
| E1 | 0000000111111111 / 0000001111111111 | 0000000011111111 / 0000000111111111 | 0000111111111111 | 0000000111111111 | |
| E2 | 0000000000000000 | 0000000000000000 | 0000000000000000 | 0000000000000000 | |
| E3 | 0000000000111111 / 0000000001111111 | 0000000000011111 / 0000000000111111 | 0000000011111111 | 0000000000111111 | |
| E4 | 0000000111111111 / 0000001111111111 | 0000000111111111 / 0000001111111111 | 0000111111111111 | 0000001111111111 | |
| E5 | 1111111111111111 | 1111111111111111 | 1111111111111111 | 1111111111111111 | |
| E6 | 0000000010000000 | 0000000010000000 | 0000000010000000 | 0000000010000000 | |
| E7 | 0000000000011111 / 0000000000111111 | 0000000000001111 / 0000000000011111 | 0000000001111111 | 0000000000011111 | |
| E8 | 1111111111111111 | 1111111111111111 | 1111111111111111 | 1111111111111111 | |
| E9 | 2222221111111111 / 2222233111111111 | same as bsnes | 2222311111111111 | 2222311111111111 | |
| E10 | 2222222221111111 / 2222222233111111 | same as bsnes | 2222222331111111 | 2222222331111111 | |
| E11 | 0000000111111111 / 0000001111111111 | 0000000011111111 / 0000000111111111 | 0000011111111111 | 0000001111111111 | |

PAL: bsnes and Mesen give the same strings as NTSC. A min/max pair that differs by one step is normal: the CPU's
phase against the line drifts with the frame parity.

### irq-ophct (H counter read in the IRQ handler; hex, min max over 8 rounds)

All rows use VTIME = 100 except row 18 (VTIME = 0). Rows 00-16 and 17-18 wake from `WAI`; rows 19-22 spin in a NOP
loop ("sled"). `1FF 1FF` on row 16 (HTIME = 340) is expected: that HTIME never fires on a normal line.

| row | setting | bsnes | Mesen | MiSTer master | MiSTer #513 | your console |
|---|---|---|---|---|---|---|
| 00 | HV 0 | 01D-01E | 01D-01E | 01B | 01C-01D | |
| 01 | HV 1 | 01F | 01F | (1FF: ROM race) | 01E-01F | |
| 02 | HV 2 | 020 | 020 | 01E | 020 | |
| 03 | HV 3 | 020-021 | 020-021 | 01F | 020-021 | |
| 04 | HV 4 | 021 | 021 | 020 | 021-022 | |
| 05 | HV 8 | 026 | 026 | 024-025 | 026 | |
| 06 | HV 16 | 02E | 02E | 02C | 02E | |
| 07 | HV 40 | 045 | 045 | 044 | 045-046 | |
| 08 | HV 64 | 05E | 05E | 05C | 05E | |
| 09 | HV 128 | 0A8 | 0A8 | (1FF: ROM race) | 0A7-0A8 | |
| 10 | HV 255 | 11D | 11D | 11B | 11D (-1FF: ROM race) | |
| 11 | HV 320 | 009 | 009 | 007-008 | 008-009 | |
| 12 | HV 330 | 013 | 013 | 011 (-1FF) | 013 | |
| 13 | HV 336 | 018 | 018 | 017 | 018-019 | |
| 14 | HV 338 | 01B | 01B | 019-01A | 01A-01B | |
| 15 | HV 339 | 01C | 01C | 01A | 01B-01C | |
| 16 | HV 340 | 1FF | 1FF | 1FF | 1FF | |
| 17 | V only (VTIME 100) | 01C | 01C | 01B-01C | 01C-01D | |
| 18 | V only, VTIME 0 | 01D | 01C | — | — | |
| 19 | sled HV 0 | 01E | 01D | 01B-01D | 01C-01E | |
| 20 | sled HV 1 | 020 | 01F | 01C-01D | 01D-01E | |
| 21 | sled HV 40 | 046 | 045 | 043-045 | 044-046 | |
| 22 | sled HV 320 | 00A | 008 | 007-008 | 008-009 | |

PAL (`irq-ophct-pal.sfc`), bsnes / Mesen: 00 01D-01E / 01D; 01 01E-01F / 01F; 02 01F-020 / 020; 03 020-021 / 021;
04 021 / 022; 05 026 / 026; 06 02D / 02E; 07 045 / 046; 08 05E / 05D; 09 0A8 / 0A8; 10 11D / 11D; 11 008 / 009;
12 012 / 013; 13 018 / 019; 14 01B / 01A; 15 01C / 01B; 16 1FF / 1FF; 17 01C / 01D; 18 01D / 01B; 19 01D / 01F;
20 020 / 01F; 21 045 / 045; 22 009 / 00A.

The MiSTer ophct columns are from the earlier ROM build and sit about one dot below the kit ROM's emulator values
(the kit ROM's second `$4210` read moves the CPU phase); compare the two MiSTer columns with each other and the
emulators with your console, not MiSTer with the emulators at the one-dot level.

### slhv-wrio

The screen prints PASS/FAIL per case against bsnes's V. Upstream MiSTer reads 3 of 6, PR #513's branch C 6 of 6,
bsnes and Mesen 6 of 6 (`screens/slhv-wrio-ab.png`). Hardware: unknown. The cases: 1 read `$2137` with `$4201.7` set;
2 read with it clear; 3 clear, then set+clear earlier, then read; 4 a 1→0 write of `$4201.7` with no read; 5 a 0→1
write; 6 clear, then three reads.

### gunprobe (optional, Super Scope required)

Shows the H/V the light-gun latch captured on each frame, with min/max since power-on. MiSTer master latches
H=0A9 V=070 with the gun pointed at the centre; PR #513 latches H=0AC. Point the Super Scope at the centre of the
screen from about a metre and photograph after a few seconds. Without a gun the flag reads 03 and H/V stay at 000.

## Screens from the emulators

`screens/*.png` are the kit ROMs' result screens on bsnes and Mesen, so you can see what a finished screen looks like
before you photograph your own.
