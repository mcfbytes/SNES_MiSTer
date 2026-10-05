#!/usr/bin/env python3
"""pad128k.py <in.sfc> <out.sfc>: a 32 KiB LoROM repeated to 128 KiB (what the core's mirroring shows anyway).
tasty will not hash a SNES ROM under 128 KiB; the probe movies (ab/A/*/*.lsmv) were made against these padded files."""
import sys
d = open(sys.argv[1], "rb").read()
assert len(d) == 0x8000, len(d)
open(sys.argv[2], "wb").write(d * 4)
