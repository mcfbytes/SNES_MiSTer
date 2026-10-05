#!/usr/bin/env python3
"""Build test_irqb_verbose.sfc: byuu's test_irqb with the verdict replaced by an expected/actual table.

Measurement code is untouched. The 32 `JMP $84C3` (fail) sites become NOPs so every check runs; the pass
path at $8499 jumps to display code at $00:8600 (bass, patch.asm) which prints all 60 result bytes.
"""
import os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "higan-snes-test-roms/KungFuFurby-test-ROMs/test_irqb.smc")
BASS = os.path.join(ROOT, "snes-test-roms/bass-untech/bass/out/bass-untech")
FONT = os.path.join(ROOT, "snes-test-roms/gen/textbuffer/font-1bpp-tiles.tiles")

rom = bytearray(open(SRC, "rb").read())
sites = [m.start() for m in re.finditer(rb"\xaf(.)\x00\x7f\xc9(.)\xf0\x03\x4c\xc3\x84", rom[:0x8000], re.S)]
assert len(sites) == 32, len(sites)
exp, chk = [0] * 60, [0] * 60
for o in sites:
    exp[rom[o + 1]], chk[rom[o + 1]] = rom[o + 5], 1
    rom[o + 8:o + 11] = b"\xea\xea\xea"
assert rom[0x0499 - 0] != 0x5C
rom[0x0499:0x049D] = bytes([0x5C, 0x00, 0x86, 0x00])  # JML $008600

def tile(c):
    if c == " ": return 0x5F
    if c.isdigit(): return 0x01 + ord(c) - ord("0")
    if c.isupper(): return 0x0B + ord(c) - ord("A")
    if c.islower(): return 0x25 + ord(c) - ord("a")
    for base, first, n in ((0x3F, "!", 15), (0x4E, ":", 7), (0x55, "[", 6), (0x5B, "{", 4)):
        if 0 <= ord(c) - ord(first) < n: return base + ord(c) - ord(first)
    raise ValueError(c)

f1 = open(FONT, "rb").read()
font = b"".join(bytes(x for r in f1[t * 8:t * 8 + 8] for x in (r, 0)) for t in range(len(f1) // 8))
tmap = [tile(" ")] * 1024
def put(row, col, s, attr=0):
    for i, c in enumerate(s):
        tmap[row * 32 + col + i] = tile(c) | attr << 8
put(1, 1, "test_irqb  verbose", 0x0C)
put(2, 1, "G=got E=expected per sub-test")
put(3, 1, "3 groups of HCNT.lo HCNT.hi")
put(4, 1, "VCNT.lo VCNT.hi  (OPHCT/OPVCT)")
put(5, 1, "A=in IRQ  B=after 4201  C=2137")
put(6, 4, "A        B        C")
pos = []
for t in range(5):
    r = 7 + t * 3
    put(r, 1, f"{t + 1}G")
    put(r + 1, 2, "E")
    for g in range(3):
        for k in range(4):
            i = t * 12 + g * 4 + k
            col = 4 + g * 9 + k * 2
            pos.append(r * 32 + col)
            put(r + 1, col, f"{exp[i]:02X}" if chk[i] else "--", 0x00 if chk[i] else 0x0C)
put(23, 1, "mismatches:")
mis = 23 * 32 + 13
put(25, 1, "green ok  red wrong  grey n/c", 0x0C)
le = lambda v, n: v.to_bytes(n, "little")
open(os.path.join(HERE, "font.bin"), "wb").write(font)
open(os.path.join(HERE, "map.bin"), "wb").write(b"".join(le(v, 2) for v in tmap))
open(os.path.join(HERE, "tables.bin"), "wb").write(
    b"".join(le(p, 2) for p in pos) + bytes(exp) + bytes(chk) + bytes(tile(c) for c in "0123456789ABCDEF"))
open(os.path.join(HERE, "mispos.inc"), "w").write(f"constant MISPOS = {mis:#x}\n")
subprocess.run([BASS, "-o", "patch.bin", "patch.asm"], cwd=HERE, check=True)
blob = open(os.path.join(HERE, "patch.bin"), "rb").read()
assert len(blob) < 0xF800 - 0x8600 and not any(rom[0x600:0x600 + len(blob)])
rom[0x600:0x600 + len(blob)] = blob
open(os.path.join(HERE, "test_irqb_verbose.sfc"), "wb").write(rom)
print("patch", len(blob), "bytes; checked", sum(chk))
