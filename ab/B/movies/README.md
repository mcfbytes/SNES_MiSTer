# Movies: whole-run frame hashes, upstream, PR A and PR B (A+B)

Each movie replays from power-on on each core; tasty hashes every core frame, and two runs are compared by movie frame
(`tools/hashcmp.py`; frames whose hash is missing in either run are left out). Where hashes differ, `ab/tools/framediff.py`
decodes both AVIs and reports the differing pixels. Movies and ROM hashes: README section 11 (`movies/`).

| movie | frames | upstream vs PR A | PR A vs PR B (A+B) | every input applied on time |
|---|---|---|---|---|
| Voronoi split-screen demo | 3,600 | identical | identical | yes, all three |
| TwistIT (Resistance) | 14,400 | identical | 2 frames (4,214 and 6,706): 2 dots on one line each (lines 26 and 24) | yes |
| Super Mario Kart attract (Mode 7) | 10,800 | identical | identical | yes |
| F-Zero attract (Mode 7) | 10,800 | identical | identical | yes |
| SMAS (Super Mario Bros.) TAS 6744M, `--lead -1` | 18,235 | 14 frames, each 2-3 dots near the left end of line 31 (the status-bar IRQ split) | 19 frames, each 2 dots at the same place | yes |
| Contra III TAS 4363M | 45,497 | 56 frames, in two clusters (9,332-9,819 and 32,043-32,093) | identical (45,494 frames compared; see below) | yes |
| Super Punch-Out!! TAS 4933M | 57,224 | identical | identical | yes |

Every movie stays in sync to its end on all three cores.

- Contra III's two clusters are scenes where the game writes Mode 7 registers from an IRQ: they are the frames PR A's Mode 7
  commit changes (the same clusters differ between PR A and its first commit alone). Contra III on PR A and A+B was recorded
  as a hash log only (`--hashes-only`): with an AVI, both runs hit encoder backpressure from about movie frame 32,000 on,
  while upstream's AVI run passed. The A+B hash-log run has three movie frames without a hash (0, 7,272, 32,178; frame 0 is
  outside the compared window).
- `smas-line31-zoom.png`: movie frame 17,174, line 31, upstream | PR A | PR B.
- `hashes/`: all 21 runs. Raw AVIs: release `evidence-460-cores` (Contra III on A and A+B: hash logs only).
- Counters: 20 of 21 runs, captured 3,602-57,226 each; missed 0, torn 0, late 0, lost 0; encoder duplicates in compared windows 0; worst gap_max 1.6 ms. The 21st, Contra III on A+B (hash log only), reports `missed 1`: movie frame 0, before the compared window; two later movie frames (7,272 and 32,178) have no hash. Its other 45,494 frames are hash-identical to PR A's.
