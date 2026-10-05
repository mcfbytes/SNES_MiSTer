#!/usr/bin/env python3
"""Build busprobe.sfc. With ref.json present (from bsnes), its values become the green/red reference."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASS = os.path.join(ROOT, "snes-test-roms/bass-untech/bass/out/bass-untech")
FONT = os.path.join(ROOT, "snes-test-roms/gen/textbuffer/font-1bpp-tiles.tiles")
BUS = ["BASE", "NOP ROM", "NOP FAST", "NOP WRAM", "LDA WRAM", "LDA 4300", "LDA 4100", "LDA 2101", "LDA 6000",
         "PHA 01FF", "PHA 437F", "PHA 41FF", "PHA 21FF", "IRQ 01FF", "IRQ 437F", "IRQ 41FF", "IRQ 4203H",
         "IRQ 4203L", "BRK 217F", "BRK 2180", "WRIO 1-0", "WRIO 0-1", "LDA 2137"]
IRQ = ["WAKE H+V", "WAKE V", "2137 WR7F", "PHA 4201"] + [f"SLED +{d}" for d in range(14)]
VARIANT = sys.argv[1] if len(sys.argv) > 1 and __name__ == "__main__" else "bus"
PAL = os.environ.get("PAL") == "1"
NAMES = {"bus": BUS, "irq": IRQ}[VARIANT]


def tile(c):
    if c == " ": return 0x5F
    if c.isdigit(): return 0x01 + ord(c) - ord("0")
    if c.isupper(): return 0x0B + ord(c) - ord("A")
    if c.islower(): return 0x25 + ord(c) - ord("a")
    for base, first, n in ((0x3F, "!", 15), (0x4E, ":", 7), (0x55, "[", 6), (0x5B, "{", 4)):
        if 0 <= ord(c) - ord(first) < n: return base + ord(c) - ord(first)
    raise ValueError(c)


def main():
    refp = os.path.join(HERE, f"ref-{VARIANT}{'-pal' if PAL else ''}.json")
    ref = json.load(open(refp)) if os.path.exists(refp) else None
    f1 = open(FONT, "rb").read()
    font = b"".join(bytes(x for r in f1[t * 8:t * 8 + 8] for x in (r, 0)) for t in range(len(f1) // 8))
    tmap = [tile(" ")] * 1024

    def put(row, col, s, attr=0):
        for i, c in enumerate(s):
            tmap[row * 32 + col + i] = tile(c) | attr << 8
    put(0, 0, f"{VARIANT}probe{' PAL' if PAL else ''}", 0x0C); put(0, 16, "apu3=", 0x0C); put(0, 24, "78=", 0x0C)
    put(1, 13, "got", 0x0C); put(1, 21, "bsnes", 0x0C); put(1, 29, "wm", 0x0C)
    put(2, 13, "Hmin Hmax  Hmin Hmax", 0x0C)
    reftab = bytearray(32 * 8)
    for i, n in enumerate(NAMES):
        put(3 + i, 0, f"{i:02d} {n}")
        if ref:
            lo, hi, v, wm = ref[i]
            put(3 + i, 21, f"{lo:03X} {hi:03X}")
            reftab[i * 8:i * 8 + 7] = lo.to_bytes(2, "little") + hi.to_bytes(2, "little") + v.to_bytes(2, "little") + bytes([wm])
        else:
            put(3 + i, 21, "--- ---", 0x0C)
    put(27, 0, "16 rounds; red=range or V differs", 0x0C)
    le = lambda v, n: v.to_bytes(n, "little")
    w = lambda name, data: open(os.path.join(HERE, name), "wb").write(data)
    w("font.bin", font)
    w("map.bin", b"".join(le(v, 2) for v in tmap))
    w("hex.bin", bytes(tile(c) for c in "0123456789ABCDEF"))
    w("rowpos.bin", b"".join(le((3 + i) * 32 + 13, 2) for i in range(len(NAMES))))
    w("ref.bin", bytes(reftab))
    open(os.path.join(HERE, "gen.inc"), "w").write(f"constant APUPOS = {21:#x}\nconstant STATPOS = {27:#x}\nconstant NPROBES = {len(NAMES)}\nconstant COUNTRY = {2 if PAL else 1}\n")
    open(os.path.join(HERE, "probes.inc"), "w").write(open(os.path.join(HERE, f"probes-{VARIANT}.inc")).read())
    subprocess.run([BASS, "busprobe.asm"], cwd=HERE, check=True)
    p = os.path.join(HERE, "out.sfc")
    rom = bytearray(open(p, "rb").read())
    assert len(rom) == 0x8000, hex(len(rom))
    rom[0x7FDC:0x7FE0] = b"\xff\xff\x00\x00"
    s = sum(rom) & 0xFFFF
    rom[0x7FDC:0x7FE0] = le(s ^ 0xFFFF, 2) + le(s, 2)
    open(os.path.join(HERE, f"{'pal-' if PAL else ''}{VARIANT}probe.sfc"), "wb").write(rom)
    print("built", "with ref" if ref else "without ref")


if __name__ == "__main__":
    main()
