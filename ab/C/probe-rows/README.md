# PR C rows of the probe ROMs: irqprobe `2137 WR7F`, busprobe `IRQ 4203L`

The probes are in `probes/` (source, ROMs) and are run as in `ab/A/irqprobe` and `ab/A/busprobe` (same movies, same padded
ROMs, upstream recordings there). Two rows exercise PR C:

- irqprobe row 02 `2137 WR7F`: `$4201 = $7F` (whose 1→0 edge latches), then `LDA $2137` at the timed point.
- busprobe row 17 `IRQ 4203L`: an IRQ with the stack at `$4203`, so the push of PCL writes `$4201` (and latches); the handler
  then reads `$2137` with bit 7 clear.

On both, a `$2137` read that latches overwrites the latch the probe is measuring.

| row (Hmin-Hmax over 16 rounds) | upstream 2302683 | PR C 57160ab | bsnes 2014 accuracy | MesenCE 2.2.1 |
|---|---|---|---|---|
| irqprobe 02, NTSC | 040 (the read's latch) | 097-098 | 09A | 09A |
| irqprobe 02, PAL | 040 | 098 | 099-09A | 09A |
| busprobe 17, NTSC | 04A-04B (the read's latch) | 036 | 037-038 | 037-038 |
| busprobe 17, PAL | 04B | 036 | 037 | 037-038 |

With C, the earlier latch survives, as on both emulators. It still reads 1-3 dots early because C alone keeps master's H/V
IRQ timing; with A as well, both rows match (`irq/*-after.png`, built with A and C).

- `ab-irqprobe.png`, `ab-busprobe.png`: NTSC, upstream | PR C | bsnes | MesenCE. Only the named row is PR C's; the other rows
  are PR A's subject and stay early on C.
- `ab.mp4`: irqprobe and busprobe, upstream and PR C.
- `hashes/`: PR C's four runs (NTSC and PAL). Counters, every run: captured 902 (PAL 752), missed 0, torn 0, dups 0, late 0,
  lost 0, gap_max 1.1-1.2 ms.
