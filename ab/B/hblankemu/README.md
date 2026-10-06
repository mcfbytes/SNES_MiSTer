# HblankEmuTest (Motive): force blank in h-blank must stop sprite loading

- ROM: `HblankEmuTest.sfc` from the higan test-ROM collection
  ([gitlab.com/higan/snes-test-roms](https://gitlab.com/higan/snes-test-roms), `Motive-test-ROMs/`); sha256
  `80706521642cc6183f406f74249d18f0ff3a501e574dd5acae67fe0c04bf0fc7`. Movie: `hblankemu.lsmv`, 900 empty frames.
- Hardware: paulb_nl's photo, the same on four consoles (PAL 3-chip, PAL 1-chip, NTSC CPU-APU, NTSC 1-chip) plus creaothceann's SFC ([nesdev p231279](https://forums.nesdev.org/viewtopic.php?p=231279#p231279)); copied here with credit as `hblankemu/hardware-paulb_nl-bpuXsI4.png` in the branch root.

Result: **partial. PR B fixes the BG side; the sprite side stays open.**

| | hardware (paulb_nl) | upstream 2302683 | PR B (A+B) 3f33d28 | PR A alone (dcde04d) | bsnes v115.1 (accurate PPU) | MesenCE 2.2.1 |
|---|---|---|---|---|---|---|
| distinct frames, movie frames 300-899 | 1 (stable on all his consoles) | 4, 150 frames each | 7: 225, 113, 75, 74, 38, 38, 37 frames | 10: 151, 113, 74, 38, 38, 38, 37, 37, 37, 37 frames | 1 | 1 |
| large BG text of lines 2-3 | "Beha" / "-Emu" | garbled in 2 of 4 states ("BEHAVI..." bleeds through) | "Beha" / "-Emu" in every frame | worse (one state shows "Behaviour / -Emulator") | no sprites at all ("THIS IS CORRECT BEHAVIOUR") | every sprite ("Incorrect Behaviour -Emulator") |
| tall white vertical bar | none | not counted (`hblankemu-states.png`) | full bar in 2 of 7 states (299 of 600 frames); a stub at the bottom in most of the others | not counted | no sprites | every sprite |
| dotted column at the left, small glyph before "Beha" | none | not counted | present in every state | not counted | no sprites | every sprite |
| line 1 | "Incor" + "ORRECT" | "THIS IS CORRECT", a sprite bar across it | "THIS IS CORRECT" | as upstream | "THIS IS CORRECT" | "Incor" + "ORRECT" |

What PR B fixes: the large BG text of lines 2-3 is stable and correct. What stays open, all sprite-side: the
white bar, the dotted left column and the small glyph (sprites that hardware does not load across force blank), line 1
("THIS IS CORRECT" where hardware keeps the "Incor" sprites), and the flicker between states, where hardware shows one
stable picture. Sprites: fixed by the next commit in the stack (`8e89569`, tested as `0f6b5e4`; `ab/D`). bsnes 2014 accuracy and bsnes v115.1 with the fast PPU show every sprite; no emulator matches hardware.

- `ab.png`: frame 301. `hblankemu/hblankemu-states.png`: the distinct MiSTer states. MP4: `hblankemu/hblankemu.mp4`.
- `hashes/`: upstream, A, A+B.

- Counters: 3 runs, captured 902 each; missed 0, torn 0, late 0, lost 0; encoder duplicates in compared windows 0; worst gap_max 1.2 ms
