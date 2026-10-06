# Jurassic Park (USA), the 4th attract sequence (the island)

bsnes-emu/bsnes [#397](https://github.com/bsnes-emu/bsnes/issues/397): a glitched line in the island sequence on bsnes and
MesenCE 2.2.1. It is clean on MesenCE PR #275, the emulator that also reproduces #274 (`../mode7_hirq`), and
[reported fine on MiSTer](https://github.com/MiSTer-devel/SNES_MiSTer/issues/274#issuecomment-5743341342). A change to the
H-IRQ or the Mode 7 read point could bring it back, so it is checked here.

- ROM: Jurassic Park (USA), not included; the movie records its sha256
  (`fe91d45201753ae9655d5ce38838e352f478b26b2d933c1bcb5bd8330121f9ff`).
- Movie: `jp.lsmv`, 12,300 empty frames from power-on; the island sequence is in movie frames 11,500-12,300.

| | upstream 2302683 | PR A dcde04d | PR B (A+B) 3f33d28 |
|---|---|---|---|
| island frames 11,500-12,300 | no glitched line | hash-identical to upstream | hash-identical to upstream |
| whole movie, against upstream | | hash-identical, all 12,300 frames | 1,249 frames differ (4,428-6,917), each by one dot on line 15 (frame 4,428: dot 41, black on upstream and A, dark green on A+B), a mid-line split that B's one-dot output shift moves |

- `hashes/`: upstream, A, A+B.
- Counters: 3 runs, captured 12,302 each; missed 0, torn 0, late 0, lost 0; encoder duplicates in compared windows 0; worst gap_max 1.6 ms
