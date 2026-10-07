#!/usr/bin/env python3
"""Build the H/V IRQ test ROMs: gen.py wrap|enable|ophct

Environment: PAL=1 for the PAL header/timing variant; KIT=1 for the hardware-kit screen (white text, no emulator
columns, no colouring); RACE=1 (ophct only) keeps the single $4210 read and shifts the vblank-poll phase per round,
to reproduce the "$4210 read inside the NMI set window" race on the emulators. Not shipped.

Each ROM = irqtest.asm + test-<variant>.inc (bass, 65816). Results land in WRAM at $0400 and are printed as a
table; with ref-<variant>[-pal]-{bsnes,mesen}.json present (from run.sh) the dev build colours each row green when
it equals the bsnes reference, red otherwise, grey for model-only rows. The "hw" column of the wrap ROM is the
hardware model of DESIGN-v2.md; the rows with a hardware statement (paulb-nl) are white in the dev build."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/mnt/source/snes-tests"
BASS = os.path.join(ROOT, "snes-test-roms/bass-untech/bass/out/bass-untech")
FONT = os.path.join(ROOT, "snes-test-roms/gen/textbuffer/font-1bpp-tiles.tiles")
VARIANT = sys.argv[1] if len(sys.argv) > 1 else "wrap"
PAL = os.environ.get("PAL") == "1"
KIT = os.environ.get("KIT") == "1"
RACE = os.environ.get("RACE") == "1"
LAST = 311 if PAL else 261          # last line, non-interlace
NL = LAST + 1                        # lines per frame

# ---- wrap: (label, mode, htime, vtime, setini, hw-expected (min,max)) ----
# mode: 1=H-only 2=V-only 3=HV.  Expected per frame (NMI to NMI) under the hardware model:
#  - HV (last,339) never; HV (0,339) twice; H-only 339 fires on every line except the NTSC short line (odd frames).
#  - interlace: frames alternate NL/NL+1 lines; no short line; PAL long line (V=311,F=1) samples H=340.
# The interlace cases come first so the 224<->448 resize happens once, at the start, and never again.
def wrap_cases():
    L = LAST
    inter = [
        ("iHV 0.339", 3, 339, 0, 1, (2, 2)),
        ("iHV %d.339" % (L + 1), 3, 339, L + 1, 1, (0, 0)),
        ("iHV %d.0" % (L + 1), 3, 0, L + 1, 1, (0, 1)),
        ("iH 339", 1, 339, 0, 1, (NL, NL + 1)),
        ("iHV %d.339" % L, 3, 339, L, 1, (0, 1)),
    ]
    if PAL:
        inter.append(("iH 340", 1, 340, 0, 1, (0, 1)))     # the long line only
    prog = [
        ("HV %d.339" % L, 3, 339, L, 0, (0, 0)),
        ("HV 0.339", 3, 339, 0, 0, (2, 2)),
        ("HV 0.338", 3, 338, 0, 0, (1, 1)),
        ("HV %d.338" % L, 3, 338, L, 0, (1, 1)),
        ("HV 1.339", 3, 339, 1, 0, (1, 1)),
        ("HV 0.0", 3, 0, 0, 0, (1, 1)),
        ("HV %d.0" % L, 3, 0, L, 0, (1, 1)),
        ("H 339", 1, 339, 0, 0, (NL, NL) if PAL else (NL - 1, NL)),
        ("H 338", 1, 338, 0, 0, (NL, NL)),
        ("H 0", 1, 0, 0, 0, (NL, NL)),
        ("H 340", 1, 340, 0, 0, (0, 0)),
        ("V %d" % L, 2, 0, L, 0, (1, 1)),
        ("V 0", 2, 0, 0, 0, (1, 1)),
        ("V %d" % (L + 1), 2, 0, L + 1, 0, (0, 0)),
        ("HV %d.0" % (L + 1), 3, 0, L + 1, 0, (0, 0)),
    ]
    c = inter + prog
    # hardware statements exist only for HV (last,339) and HV (0,339) (paulb-nl p310687) and HTIME>339 (fullsnes)
    hw = {i for i, r in enumerate(c) if r[0] in ("HV %d.339" % L, "HV 0.339", "H 340")}
    return c, hw


# ---- enable: rows of 16 steps, 8 rounds each; each sample is a bitmap (bit0 = $4211.7 after the delay,
# bit1 = the early read for rows E9/E10). The screen shows min and max over the rounds per step. ----
HS, VS = 40, 100
ENABLE_ROWS = [
    ("E0 HVen 52", "EnHV", 52, 0),
    ("E1 HVen 60", "EnHV", 60, 0),
    ("E2 HVenN52", "EnHVnop", 52, 0),
    ("E3 HVenN60", "EnHVnop", 60, 0),
    ("E4 HTwr 20", "WrH", 20, 0),
    ("E5 HTwr 28", "WrH", 28, 0),
    ("E6 VenVT-8", "EnV", 0, 1),
    ("E7 dis/en48", "DisEn", 48, 0),
    ("E8 dis/en64", "DisEn", 64, 0),
    ("E9 4211rd40", "Rd", 40, 0),
    ("E10 rdN 40", "Rdnop", 40, 0),
    ("E11 Hen 60", "EnH", 60, 0),
]
NROUNDS_ENABLE = 8

# ---- ophct: (label, mode, htime, flags); flags bit0 = sled row, bit1 = VTIME=0 (else VS). ----
OPHCT_ROWS = [("HV %d" % h, 3, h, 0) for h in (0, 1, 2, 3, 4, 8, 16, 40, 64, 128, 255, 320, 330, 336, 338, 339, 340)]
OPHCT_ROWS += [("V only", 2, 0, 0), ("V only VT0", 2, 0, 2)]
OPHCT_ROWS += [("sled HV %d" % h, 3, h, 1) for h in (0, 1, 40, 320)]
NROUNDS = 8


def tile(c):
    if c == " ": return 0x5F
    if c.isdigit(): return 0x01 + ord(c) - ord("0")
    if c.isupper(): return 0x0B + ord(c) - ord("A")
    if c.islower(): return 0x25 + ord(c) - ord("a")
    for base, first, n in ((0x3F, "!", 15), (0x4E, ":", 7), (0x55, "[", 6), (0x5B, "{", 4)):
        if 0 <= ord(c) - ord(first) < n: return base + ord(c) - ord(first)
    raise ValueError(c)


def main():
    sfx = "-pal" if PAL else ""
    refs = {}
    for emu in ("bsnes", "mesen"):
        p = os.path.join(HERE, f"ref-{VARIANT}{sfx}-{emu}.json")
        refs[emu] = json.load(open(p)) if os.path.exists(p) else None
    f1 = open(FONT, "rb").read()
    font = b"".join(bytes(x for r in f1[t * 8:t * 8 + 8] for x in (r, 0)) for t in range(len(f1) // 8))
    tmap = [tile(" ")] * 1024
    le = lambda v, n: v.to_bytes(n, "little")
    GREY = 0 if KIT else 0x0C

    def put(row, col, s, attr=0):
        for i, c in enumerate(s):
            tmap[row * 32 + col + i] = tile(c) | attr << 8
    rowpos, reftab, inc = [], bytearray(), []
    title = f"irq-{VARIANT}{' PAL' if PAL else ' NTSC'}"
    if VARIANT == "wrap":
        cases, hw = wrap_cases()
        put(0, 0, title + " IRQs per frame", GREY)
        if KIT:
            put(1, 0, "no case    got", GREY)
            put(2, 0, "           min max", GREY)
        else:
            put(1, 0, "no case    got     hw    bsn msn", GREY)
            put(2, 0, "           min max min max", GREY)
        for i, (lab, mode, ht, vt, si, exp) in enumerate(cases):
            r = 3 + i
            put(r, 0, f"{i:02d} {lab}")
            rowpos.append(r * 32 + 11)
            if not KIT:
                col = 0x00 if i in hw else 0x0C
                put(r, 19, f"{exp[0]:03d} {exp[1]:03d}", col)
                for k, emu in enumerate(("bsnes", "mesen")):
                    v = refs[emu][i] if refs[emu] else None
                    put(r, 26 + k * 3, f"{v[0]:03d}" if v and v[0] == v[1] else (f"{v[0] % 1000:03d}" if v else "---"), 0x0C)
            bnd = 1 if lab in ("H 339", "H 338", "H 0", "iH 339") else 0   # boundary from OPVCT wrap (per-line rows)
            reftab += le(exp[0], 2) + le(exp[1], 2) + bytes([mode, ht & 0xFF, ht >> 8, vt & 0xFF, vt >> 8, si, 1 if i in hw else 0, bnd])
        put(26, 0, "12 frames, frames 3-11 counted", GREY)
        put(27, 0, "N = a frame had no NMI" if KIT else "grn=hw red=diff gry=model N=noNMI", GREY)
        inc.append(f"constant NCASES = {len(cases)}\nconstant CASESZ = 12\n")
    elif VARIANT == "enable":
        put(0, 0, title + "  write vs trigger", GREY)
        put(1, 0, f"sync WAI HV V{VS} H{HS}; d=0..15", GREY)
        put(2, 0, f"row  d0.............d15 {NROUNDS_ENABLE} rounds", GREY)
        for i, (lab, kind, base, isv) in enumerate(ENABLE_ROWS):
            r = 3 + i * 2
            put(r, 0, f"{i:02d}")
            put(r + 1, 0, lab[3:11] if len(lab) > 3 else "", GREY)
            rowpos.append(r * 32 + 5)
            rowpos.append((r + 1) * 32 + 5)
            put(r, 22, "min", GREY)
            put(r + 1, 22, "max", GREY)
            v = refs["bsnes"][i] if refs["bsnes"] else None
            reftab += bytes(v) if v else bytes(32)
        put(27, 0, "values only, see README" if KIT else "1=4211.7 set; E9/10 bit1=early rd", GREY)
        inc.append(f"constant NROWS = {len(ENABLE_ROWS)}\nconstant NROUNDS = {NROUNDS_ENABLE}\nconstant HS = {HS}\nconstant VS = {VS}\n")
        inc.append("".join(f"constant BASE{i} = {b}\n" for i, (_, _, b, _) in enumerate(ENABLE_ROWS)))
    elif VARIANT == "ophct":
        put(0, 0, title + " 2137 in handler", GREY)
        put(1, 0, f"V{VS}; {NROUNDS} rounds; H min max", GREY)
        put(2, 0, "no row        got     " + ("" if KIT else "bsn msn"), GREY)
        for i, (lab, mode, ht, flags) in enumerate(OPHCT_ROWS):
            r = 3 + i
            put(r, 0, f"{i:02d} {lab}")
            rowpos.append(r * 32 + 14)
            if not KIT:
                for k, emu in enumerate(("bsnes", "mesen")):
                    v = refs[emu][i] if refs[emu] else None
                    put(r, 22 + k * 4, f"{v[0]:03X}" if v else "---", 0x0C)
            b = refs["bsnes"][i] if refs["bsnes"] else [0x1FF, 0x1FF]
            reftab += bytes([mode, ht & 0xFF, ht >> 8, flags]) + le(b[0], 2) + le(b[1], 2)
        put(26, 0, "1FF = no IRQ (NMI rescue)", GREY)
        put(27, 0, "values only, see README" if KIT else "green = range equals bsnes", GREY)
        inc.append(f"constant NROWS = {len(OPHCT_ROWS)}\nconstant NROUNDS = {NROUNDS}\nconstant VS = {VS}\n")
    w = lambda name, data: open(os.path.join(HERE, name), "wb").write(data)
    w("font.bin", font)
    w("map.bin", b"".join(le(v, 2) for v in tmap))
    w("hex.bin", bytes(tile(c) for c in "0123456789ABCDEF"))
    w("rowpos.bin", b"".join(le(p, 2) for p in rowpos))
    w("ref.bin", bytes(reftab))
    inc.append(f"constant COUNTRY = {2 if PAL else 1}\nconstant KIT = {1 if KIT else 0}\nconstant RACE = {1 if RACE else 0}\n")
    open(os.path.join(HERE, "gen.inc"), "w").write("".join(inc))
    open(os.path.join(HERE, "test.inc"), "w").write(open(os.path.join(HERE, f"test-{VARIANT}.inc")).read())
    subprocess.run([BASS, "irqtest.asm"], cwd=HERE, check=True)
    p = os.path.join(HERE, "out.sfc")
    rom = bytearray(open(p, "rb").read())
    assert len(rom) == 0x8000, hex(len(rom))
    rom = rom * 4                       # 128 KiB: tasty will not hash a smaller SNES ROM
    rom[0x7FD7] = 0x07
    rom[0x7FDC:0x7FE0] = b"\xff\xff\x00\x00"
    s = sum(rom) & 0xFFFF
    rom[0x7FDC:0x7FE0] = le(s ^ 0xFFFF, 2) + le(s, 2)
    name = f"irq-{VARIANT}{sfx}{'-kit' if KIT else ''}{'-race' if RACE else ''}.sfc"
    out = os.path.join(HERE, name)
    open(out, "wb").write(rom)
    os.remove(p)
    print("built", out, "refs:", {k: bool(v) for k, v in refs.items()})


if __name__ == "__main__":
    main()
