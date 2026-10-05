#!/usr/bin/env python3
"""Build slhv-wrio.sfc (PAL=1: pal-slhv-wrio.sfc). With ref.json present (bsnes 2014 accuracy), its V and $213F.6
become the expected column and the PASS/FAIL test. BASS and FONT default to a snes-test-roms checkout beside this tree."""
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("SNES_TEST_ROMS", os.path.join(os.path.dirname(HERE), "snes-test-roms"))
BASS = os.environ.get("BASS", os.path.join(ROOT, "bass-untech/bass/out/bass-untech"))
FONT = os.path.join(ROOT, "gen/textbuffer/font-1bpp-tiles.tiles")
PAL = os.environ.get("PAL") == "1"
LP, LM, LA = 40, 80, 120
CASES = [  # label, legend
    ("1 set,rd", f"1 4201=FF, read 2137 @{LA}"),
    ("2 clr,rd", f"2 4201=7F @{LP}, read 2137 @{LA}"),
    ("3 was,rd", f"3 7F @{LP}, FF+7F @{LM}, rd @{LA}"),
    ("4 1>0", f"4 4201 1->0 @{LA}, no read"),
    ("5 0>1", f"5 7F @{LP}, 4201 0->1 @{LA}"),
    ("6 clr,rd3", f"6 7F @{LP}, rd @{LA},{LA+40},{LA+80}"),
]
ROW0, COLH = 5, 11


def tile(c):
    if c == " ": return 0x5F
    if c.isdigit(): return 0x01 + ord(c) - ord("0")
    if c.isupper(): return 0x0B + ord(c) - ord("A")
    if c.islower(): return 0x25 + ord(c) - ord("a")
    for base, first, n in ((0x3F, "!", 15), (0x4E, ":", 7), (0x55, "[", 6), (0x5B, "{", 4)):
        if 0 <= ord(c) - ord(first) < n: return base + ord(c) - ord(first)
    raise ValueError(c)


def main():
    refp = os.path.join(HERE, f"ref{'-pal' if PAL else ''}.json")
    ref = json.load(open(refp)) if os.path.exists(refp) else None
    f1 = open(FONT, "rb").read()
    font = b"".join(bytes(x for r in f1[t * 8:t * 8 + 8] for x in (r, 0)) for t in range(len(f1) // 8))
    tmap = [tile(" ")] * 1024

    def put(row, col, s, attr=0):
        for i, c in enumerate(s):
            tmap[row * 32 + col + i] = tile(c) | attr << 8
    put(0, 0, f"slhv-wrio{' PAL' if PAL else ' NTSC'}  2137 vs 4201.7", 0x0C)
    put(1, 0, "latch V: does it change?", 0x0C)
    put(3, COLH, "got", 0x0C); put(3, 21, "bsnes", 0x0C)
    put(4, 0, "case", 0x0C); put(4, COLH, "  H   V F  V  F", 0x0C)
    reftab = bytearray(8 * len(CASES))
    for i, (lab, leg) in enumerate(CASES):
        put(ROW0 + i, 0, lab)
        if ref:
            v, f = ref[i]["v"], ref[i]["f"]
            put(ROW0 + i, 21, f"{v:03d} {f}")
            reftab[i * 8:i * 8 + 4] = v.to_bytes(2, "little") + bytes([f, 1])
        else:
            put(ROW0 + i, 21, "--- -", 0x0C)
    r = ROW0 + len(CASES) + 1
    put(r, 0, f"each case: 4201=FF, latch @{LP}", 0x0C)
    for i, (lab, leg) in enumerate(CASES):
        put(r + 1 + i, 0, leg, 0x0C)
    r += len(CASES) + 2
    put(r, 0, "V = line of last latch", 0x0C)
    put(r + 1, 0, "F = 213F bit 6 after", 0x0C)
    put(r + 2, 0, "PASS = V and F match bsnes", 0x0C)
    put(r + 3, 0, "    (MesenCE agrees)", 0x0C)
    le = lambda v, n: v.to_bytes(n, "little")
    w = lambda name, data: open(os.path.join(HERE, name), "wb").write(data)
    w("font.bin", font)
    w("map.bin", b"".join(le(v, 2) for v in tmap))
    w("hex.bin", bytes(tile(c) for c in "0123456789ABCDEF"))
    w("words.bin", bytes(tile(c) for c in "PASSFAIL"))
    w("rowpos.bin", b"".join(le((ROW0 + i) * 32 + COLH, 2) for i in range(len(CASES))))
    w("ref.bin", bytes(reftab))
    open(os.path.join(HERE, "gen.inc"), "w").write(
        f"constant NCASES = {len(CASES)}\nconstant COUNTRY = {2 if PAL else 1}\nconstant LP = {LP}\nconstant LM = {LM}\n"
        f"constant LA = {LA}\nconstant VERDOFS = {27 - COLH}\n")
    subprocess.run([BASS, "slhvwrio.asm"], cwd=HERE, check=True)
    p = os.path.join(HERE, "out.sfc")
    rom = bytearray(open(p, "rb").read())
    assert len(rom) == 0x8000, hex(len(rom))
    rom = rom * 4  # 128 KiB, four mirrors: tasty will not hash a SNES ROM under 128 KiB
    rom[0x7FD7] = 0x07
    rom[0x7FDC:0x7FE0] = b"\xff\xff\x00\x00"
    s = sum(rom) & 0xFFFF
    rom[0x7FDC:0x7FE0] = le(s ^ 0xFFFF, 2) + le(s, 2)
    open(os.path.join(HERE, f"{'pal-' if PAL else ''}slhv-wrio.sfc"), "wb").write(rom)
    os.remove(p)
    print("built", "with ref" if ref else "without ref")


if __name__ == "__main__":
    main()
