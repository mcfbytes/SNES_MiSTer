# slhv-wrio: does `$2137` latch the H/V counters while `$4201` bit 7 is clear?

A self-checking test ROM written for PR C. It needs no input and shows its verdicts after about a second.

- `slhv-wrio.sfc` (NTSC), `pal-slhv-wrio.sfc` (PAL): 128 KiB LoROM (32 KiB of code, mirrored four times).
- `src/`: `slhvwrio.asm` (bass-untech) and `gen.py`, which builds both ROMs and embeds bsnes 2014's results (`ref*.json`) as
  the expected column. `PAL=1 python3 gen.py` for PAL. Fonts and assembler as for `probes/` (undisbeliever's
  `snes-test-roms` checked out beside this tree, or `SNES_TEST_ROMS=`).
- `*.mgl`: load the ROM from `games/SNES/` on a MiSTer. `*.lsmv`: 300 (PAL 250) empty frames for tasty.

## What it does

Each case first sets `$4201 = $FF`, waits for line 40 (V-IRQ, `WAI` with I set), reads `$2137` to latch V = 40, and reads
`$213F` to reset the OPHCT/OPVCT flip-flops. Then:

| case | action | latched V, bsnes and Mesen | upstream 2302683 | PR C 57160ab |
|---|---|---|---|---|
| 1 set,rd | read `$2137` at line 120 | 120 (latches) | 120 | 120 |
| 2 clr,rd | `$4201 = $7F` at 40; read `$2137` at 120 | 40 (no latch; the 1→0 edge latched at 40) | **120** | 40 |
| 3 was,rd | `$7F` at 40; at 80 `$FF` then `$7F`; read at 120 | 80 (no latch at the read) | **120** | 80 |
| 4 1>0 | `$4201 = $7F` at 120, no read | 120 (the pin's falling edge latches) | 120 | 120 |
| 5 0>1 | `$7F` at 40; `$4201 = $FF` at 120, no read | 40 (a rising edge does not latch) | 40 | 40 |
| 6 clr,rd3 | `$7F` at 40; read `$2137` at 120, 160 and 200 | 40 | **200** | 40 |

The screen lists H (dots) and V (decimal) as read, `$213F` bit 6 (F), the expected V and F, and PASS/FAIL on V and F.
H is shown but not judged: upstream's H/V IRQ wakes 1-2 dots early (PR A), so its H differs from the emulators by that much.
F reads 1 in every case on every target: with bit 7 clear, `$213F` bit 6 reads 1 (on the core and on both emulators), so F cannot tell the cases apart.

Results: upstream 3 of 6 (NTSC and PAL), PR C 6 of 6, bsnes 2014 accuracy 6 of 6, MesenCE 2.2.1 6 of 6. bsnes and MesenCE
agree on every V (and on H within a dot in PAL).

Case 3 is fullsnes's "(or was) set": having set bit 7 earlier does not make a later read latch, on either emulator or on PR C.
Cases 4 and 5 are the EXTLATCH pin: on the core, `EXTLATCH = JPIO67(7) and JOY2_P6_in`, and with no light gun or SNAC
`JOY2_P6_in` is 1 (`SNES.sv`: `LG_P6_out | !GUN_MODE`), so a 1→0 write to bit 7 is the falling edge that `PPU.vhd` latches on.
We have not seen this ROM on a real console; a photo of the result screen from one, via a flash cart, is the missing column.

## Files

- `ab.png` / `ab-pal.png`: upstream | PR C | bsnes 2014 accuracy | MesenCE | (no hardware yet).
- `ab.mp4`: the four MiSTer recordings (NTSC and PAL, upstream and PR C).
- `hashes/`: tasty hash logs. Counters: every run `missed 0, torn 0, dups 0, late 0, lost 0`; captured 302 (NTSC) / 252 (PAL);
  gap_max 1.1-1.2 ms.
- `mgl-release-SNES_20260823.png`: the MGL route checked on the DE10-Nano with the released core `SNES_20260823.rbf` and the
  MiSTer screenshot command: the same 3 of 6 as upstream.
