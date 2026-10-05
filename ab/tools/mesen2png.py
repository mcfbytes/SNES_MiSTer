#!/usr/bin/env python3
"""mesen2png.py <testrunner stdout> <out.png>: rebuild the SCREEN line printed by mesen-shot.lua as a PNG."""
import re, subprocess, sys
txt = open(sys.argv[1]).read()
m = re.search(r"SCREEN (\d+) ([0-9A-F]+)", txt)
n, hx = int(m.group(1)), m.group(2)
w = 512 if n % 512 == 0 and n // 512 in (448, 478) else 256
h = n // w
raw = bytes.fromhex(hx)
subprocess.run(["convert", "-size", f"{w}x{h}", "-depth", "8", "rgb:-", sys.argv[2]], input=raw, check=True)
print(w, h)
