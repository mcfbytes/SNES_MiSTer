# Games whose IRQ timing was tuned against the 2024 S-CPU rework (bd4d8fb), upstream against PR A

Attract modes, no input: each movie is 9,000 empty frames (2.5 minutes) from power-on. The ROMs are not here; the movies record
each ROM's sha256 (No-Intro USA sets, headerless). Compared by tasty frame hash (`tools/hashcmp.py`), then by pixels
(`tools/framediff.py`).

| game (issue) | frames that differ | where |
|---|---|---|
| Full Throttle - All-American Racing (#279) | 1,494 of 9,000 | The intro logo fade (frames 210-397) runs at a slightly different brightness per frame; from frame 8,031 the attract has chosen a different track (`ft-8100.png`). In the water-bike race (frames 5,300-7,000; the #279 scene) 282 frames differ, each in one dot: line 152, dot 251, at the right edge (`ft-5343.png`). The bottom-line garbage of #279 does not return. |
| Chuck Rock (#220) | 123 | one line: line 96, dots 184-187 (97 frames), or line 223 (15 frames) (`chuck-1095.png`) |
| Cybernator (#103) | 64 | one dot: line 22, dots 247-248 (63 frames); one frame on line 13 (`cyber-3011.png`) |
| Kawasaki Superbike Challenge | 0 | identical |
| WeaponLord (#502) | 0 | identical |
| Aladdin | 0 | identical |

We have no hardware capture of any of these scenes, so the one-dot differences cannot be called right or wrong here; they sit
on mid-line split points, where a 1.5-dot later IRQ would move a write by one dot. The Full Throttle attract's track choice
depends on its own frame timing, so a different track is expected once anything shifts.

- `hashes/`: upstream and A for all six. Counters, every run: captured 9,001-9,006, missed 0, torn 0, dups 0, late 0, lost 0,
  gap_max 1.1-1.6 ms. Raw AVIs: release `evidence-460-cores`.
