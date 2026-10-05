# busprobe: CPU bus access timing and IRQ entry, against bsnes and Mesen

Our probe ROM (`probes/`, `gen.py bus`): after a `WAI`-synchronised start, one bus access type per row (ROM, FastROM, WRAM,
`$21xx`/`$41xx`/`$43xx` reads, PHA, IRQ entry with the stack in various places, BRK, WRIO edges), then a `$2137` latch; 16
rounds, Hmin/Hmax per row against bsnes 2014 accuracy. The ROM here is `probes/busprobe.sfc` padded to 128 KiB.

| | upstream 2302683 | PR A 2ff03cf | bsnes 2014 accuracy | MesenCE 2.2.1 | hardware |
|---|---|---|---|---|---|
| NTSC rows equal to bsnes | 0 of 23 (every row 1-2 dots early; row 17 is PR C's) | 20 of 23 | 23 of 23 | 23 of 23 | — |
| PAL rows inside the bsnes..Mesen band | 7 of 23 | 22 of 23 | | | — |

PR A, NTSC: rows 04 `LDA WRAM` and 08 `LDA 6000` have one of 16 rounds landing on DRAM refresh (Hmax +10); row 17
`IRQ 4203L` is PR C's (`ab/C/probe-rows`). PAL: the one row outside the band is 17.

- `ab.png` (NTSC), `ab-pal.png`, `ab.mp4` (NTSC and PAL, upstream and PR A), `hashes/`.
- Counters, every run: captured 902 (PAL 752), missed 0, torn 0, dups 0, late 0, lost 0, gap_max 1.1-1.2 ms.
