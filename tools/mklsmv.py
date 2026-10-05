#!/usr/bin/env python3
"""mklsmv.py <rom> <out.lsmv> <frames> [script]: an lsnes rr1 movie from power-on for tasty.

script: comma-separated "start-end:p1buttons/p2buttons" spans (buttons from BYsSudlrAXLR, e.g. 'r' = Right);
without it every frame is empty. Two pads when the script mentions pad 2, else one.
"""
import hashlib, os, sys, zipfile
ORDER = "BYsSudlrAXLR"
rom, out, frames = sys.argv[1], sys.argv[2], int(sys.argv[3])
spans = []
for part in (sys.argv[4].split(",") if len(sys.argv) > 4 else []):
    rng, keys = part.split(":")
    a, b = (int(v) for v in rng.split("-"))
    p1, _, p2 = keys.partition("/")
    spans.append((a, b, p1, p2))
two = any(s[3] for s in spans)
data = open(rom, "rb").read()
if len(data) % 1024 == 512:
    data = data[512:]
def pad(keys):
    return "".join(c if c in keys else "." for c in ORDER)
lines = []
for f in range(frames):
    p1 = p2 = ""
    for a, b, k1, k2 in spans:
        if a <= f < b:
            p1 += k1; p2 += k2
    lines.append("F. 0 0|" + pad(p1) + ("|" + pad(p2) if two else ""))
with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as z:
    for k, v in (("systemid", "lsnes-rr1"), ("controlsversion", "0"), ("gametype", os.environ.get("GAMETYPE", "snes_ntsc")),
                 ("rom.sha256", hashlib.sha256(data).hexdigest()), ("coreversion", "bsnes v085 (Accuracy core)"),
                 ("port1", "gamepad"), ("port2", "gamepad" if two else "none"), ("authors", "idle movie for core A/B"),
                 ("rerecords", "0")):
        z.writestr(k, v + "\n")
    z.writestr("input", "\n".join(lines) + "\n")
print(out, frames, "frames,", "2 pads" if two else "1 pad", "sha256", hashlib.sha256(data).hexdigest()[:12])
