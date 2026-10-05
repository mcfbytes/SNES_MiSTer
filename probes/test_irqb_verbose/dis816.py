#!/usr/bin/env python3
"""65816 disassembly that follows REP/SEP, so immediates get the right width.

capstone decodes with M=X=16; an immediate operand is resized here from the tracked flags.
"""
import sys
import capstone as cs

D = cs.Cs(cs.CS_ARCH_MOS65XX, cs.CS_MODE_MOS65XX_65816_LONG_MX)
A_IMM = {0x09, 0x29, 0x49, 0x69, 0x89, 0xA9, 0xC9, 0xE9}  # ora and eor adc bit lda cmp sbc #
X_IMM = {0xA0, 0xA2, 0xC0, 0xE0}                          # ldy ldx cpy cpx #


def run(rom, start, end, m16=0, x16=0):
    pc, out = start, []
    while pc < end:
        off = pc - 0x8000
        op = rom[off]
        ins = next(D.disasm(rom[off:off + 4], pc), None)
        if ins is None:
            out.append(f"{pc:06X}  {op:02x}          .db ${op:02x}")
            pc += 1
            continue
        size = ins.size
        if op in A_IMM:
            size = 3 if m16 else 2
        elif op in X_IMM:
            size = 3 if x16 else 2
        raw = rom[off:off + size]
        text = f"{ins.mnemonic} {ins.op_str}"
        if op in A_IMM or op in X_IMM:
            val = int.from_bytes(raw[1:], "little")
            text = f"{ins.mnemonic} #${val:0{2 * (size - 1)}X}"
        out.append(f"{pc:06X}  {raw.hex():8s}  {text}")
        if op in (0xC2, 0xE2):
            on, v = op == 0xC2, raw[1]
            if v & 0x20:
                m16 = 1 if on else 0
            if v & 0x10:
                x16 = 1 if on else 0
        pc += size
    return out


if __name__ == "__main__":
    rom = open(sys.argv[1], "rb").read()
    a, b = int(sys.argv[2], 16), int(sys.argv[3], 16)
    m = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    x = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    print("\n".join(run(rom, a, b, m, x)))
