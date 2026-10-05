# HblankEmuTest (Motive): force blank in h-blank must stop sprite loading

- ROM: `HblankEmuTest.sfc` from the higan test-ROM collection
  ([gitlab.com/higan/snes-test-roms](https://gitlab.com/higan/snes-test-roms), `Motive-test-ROMs/`; nesdev forum
  [t=18216](https://forums.nesdev.org/viewtopic.php?t=18216)); sha256
  `80706521642cc6183f406f74249d18f0ff3a501e574dd5acae67fe0c04bf0fc7`. Movie: `hblankemu.lsmv`, 900 empty frames.
- Hardware: paulb_nl's photo, the same on all his consoles (`hblankemu/hardware-paulb_nl-bpuXsI4.png`, credited).

| | hardware | upstream 2302683 | PR A+B 18f47d6 | +IRQ only (A) | bsnes v115.1 (accurate PPU) | MesenCE 2.2.1 |
|---|---|---|---|---|---|---|
| lines 2-3 | "Beha UR" / "-Emu" | garbled in 2 of 4 states | "Beha UR" / "-Emu" in every frame | worse (one state shows "Behaviour / -Emulator") | no sprites at all ("THIS IS CORRECT BEHAVIOUR") | every sprite ("Incorrect Behaviour -Emulator") |
| line 1 | "Incor" + "RRECT" | "THIS IS CORRECT", a sprite bar across it | "THIS IS CORRECT" | as upstream | "THIS IS CORRECT" | "Incor" + "ORRECT" |

bsnes 2014 accuracy and bsnes v115.1 with the fast PPU show every sprite. No emulator matches hardware; PR A+B matches it on
lines 2-3 and not on line 1 (a sprite-side item that stays open).

- `ab.png`: frame 301. `hblankemu/hblankemu-states.png`: the distinct MiSTer states. MP4: `hblankemu/hblankemu.mp4`.
- `hashes/`: upstream, A, A+B.

Counters (re-recorded 2026-10-05 on the current image, frame-hash identical to the 2026-10-04 runs behind section 1): every run missed 0, torn 0, late 0, lost 0, gap_max 1.1-1.2 ms; no encoder duplicates in any compared window.
