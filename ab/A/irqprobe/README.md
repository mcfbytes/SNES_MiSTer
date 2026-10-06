# irqprobe: H/V IRQ wake and IRQ entry, against bsnes and Mesen

Our probe ROM (`probes/`, `gen.py irq`): an H+V timer at V=100 H=40, `WAI` with I set, then the case under test and a `$2137`
latch, 16 rounds; the screen shows Hmin/Hmax per row against bsnes 2014 accuracy's values. Rows 04-17 take the IRQ inside a
slow-ROM NOP sled with HTIME stepped by one dot per row. The ROM here is `probes/irqprobe.sfc` padded to 128 KiB
(`tools/pad128k.py`); `irqprobe.lsmv` / `pal-irqprobe.lsmv` are 900 / 750 empty frames.

| | upstream 2302683 | PR A dcde04d | bsnes 2014 accuracy | MesenCE 2.2.1 | hardware |
|---|---|---|---|---|---|
| NTSC rows equal to bsnes | 0 of 18 (every row 1-3 dots early; row 02 is PR C's) | 9 of 18 | 18 of 18 | 18 of 18 | — |
| PAL rows inside the bsnes..Mesen band | 4 of 18 | 17 of 18 | | | — |

PR A, NTSC, the other nine rows: 00 `WAKE H+V` 043-044 against 043 and 01 `WAKE V` 01A-01B against 01B (one of the 16 rounds
lands a dot off); 03-06 within 1 dot; 08 and 11 are NOP-sled rows on a phase boundary (070-073 against 070, 076 against 074);
02 `2137 WR7F` is PR C's row (`ab/C/probe-rows`). In PAL the one row outside the band is 02, PR C's.

bsnes raises /IRQ when its H counter, delayed 10 master clocks, equals `(HTIME+1)*4`, i.e. at HTIME + 3.5 dots, and at
2.5 dots for V-only (`sfc/cpu/irq.cpp`, `io.cpp`, bsnes v115). The wake rows put PR A within one dot (round to round) of that
point; upstream is 1-2 dots before it.

- `ab.png` (NTSC), `ab-pal.png`: upstream | PR A | bsnes | MesenCE. The bsnes column printed on each screen is the embedded
  reference (for PAL, a band between the two emulators; the ROM colours a row red unless it equals it exactly).
- `ab.mp4`: NTSC and PAL, upstream and PR A.
- `hashes/`. Counters: 6 runs, captured 751-902 each; missed 0, torn 0, late 0, lost 0; encoder duplicates in compared windows 0; worst gap_max 1.3 ms

PR B (A+B, 3f33d28) gives the same result screens as A, NTSC and PAL. At most one hash per run differs: the frame
where the result screen first appears (B's one-dot output shift on the display turn-on). `hashes/`: upstream, A, A+B.
