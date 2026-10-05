#!/usr/bin/env python3
"""mesen-movie.py <rom> <script> <dumps> <outdir>: MesenCE --testRunner with pad-1 input spans ("a-b:keys", a <= frame < b, keys from
BYsSudlrAXLR as in mklsmv.py) and a PNG of each frame listed in <dumps> (comma list, 0-based), outdir/fNNNNN.png."""
import os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
rom, script, dumps, out = sys.argv[1:5]
os.makedirs(out, exist_ok=True)
KEY = dict(zip("BYsSudlrAXLR", ["b", "y", "select", "start", "up", "down", "left", "right", "a", "x", "l", "r"]))
spans = []
for part in (p for p in script.split(",") if ":" in p):
    rng, keys = part.split(":")
    a, b = rng.split("-")
    spans.append("{%s,%s,{%s}}" % (a, b, ",".join(f"{KEY[k]}=true" for k in keys)))
want = sorted(int(x) for x in dumps.split(","))
lua = f"""
local spans = {{{",".join(spans)}}}
local want = {{{",".join(f"[{w}]=true" for w in want)}}}
local last = {want[-1]}
local n = 0
emu.addEventCallback(function()
  for _, s in ipairs(spans) do
    if n >= s[1] and n < s[2] then emu.setInput(s[3], 0) end
  end
end, emu.eventType.inputPolled)
emu.addEventCallback(function()
  if want[n] then
    local buf = emu.getScreenBuffer()
    local t = {{}}
    for i = 1, #buf do t[i] = string.format("%06X", buf[i] & 0xFFFFFF) end
    print("SCREEN " .. n .. " " .. #buf .. " " .. table.concat(t))
  end
  if n >= last then emu.stop(0) end
  n = n + 1
end, emu.eventType.endFrame)
"""
lp = os.path.join(out, "movie.lua")
open(lp, "w").write(lua)
env = dict(os.environ, DISPLAY="", WAYLAND_DISPLAY="")
r = subprocess.run([os.environ.get("MESEN", "/mnt/source/tools/mesence/Mesen"), "--testRunner", lp, os.path.abspath(rom),
                    "--enableStdout"], capture_output=True, text=True, env=env, timeout=900)
for m in re.finditer(r"SCREEN (\d+) (\d+) ([0-9A-F]+)", r.stdout):
    f, n, hx = int(m.group(1)), int(m.group(2)), m.group(3)
    w = 256 if n in (256 * 239, 256 * 224) else 512
    subprocess.run(["convert", "-size", f"{w}x{n // w}", "-depth", "8", "rgb:-", os.path.join(out, f"f{f:05d}.png")],
                   input=bytes.fromhex(hx), check=True)
print(sorted(os.listdir(out)))
