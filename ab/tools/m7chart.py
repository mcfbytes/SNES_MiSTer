#!/usr/bin/env python3
"""m7chart.py <out.png> <label=m7line-output.txt>...: paulb-nl's #274 table against the cores, one block per variant.
Each input is m7line.py's output (one line per variant). Cells: H-IRQ 0..8; black = the line is black in every frame
(write on time), orange with the % = flickers, white = never. The hardware row is paulb-nl's (#274), with srg320's 2-6 for bra_nops82."""
import sys, re
from PIL import Image, ImageDraw, ImageFont
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
FS = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
HW = {"mode7_wai_nops83": (1, 1), "mode7_wai_nops95_fastrom": (3, 3), "mode7_wai_nops96_fastrom": (None, 0),
      "mode7_bra_nops82": (1, 6), "mode7_bra_nops83": (0, 3), "mode7_bra_nops95_fastrom": (1, 5), "mode7_bra_nops96_fastrom": (0, 2)}
ALT = {"mode7_bra_nops82": (2, 6)}
out, srcs = sys.argv[1], [a.split("=", 1) for a in sys.argv[2:]]
data = {}
for lab, p in srcs:
    for l in open(p):
        v = l.split()
        if not v: continue
        name = v[0].split("/")[-1]; name = re.sub(r"^[^-]*-(mode7_)", r"\1", name) if not name.startswith("mode7_") else name
        name = re.sub(r"\.rows$", "", name)
        cells = {f"H={h}": (int(a), int(b)) for h, a, b in re.findall(r"H=(\d+):(\d+)/(\d+)", l)}
        data[(lab, name)] = [cells.get(f"H={h}", (0, 0)) for h in range(9)]
CW, RH, LW, TOP = 46, 22, 250, 34
labs = [l for l, _ in srcs]
blocks = list(HW)
H = TOP + len(blocks) * ((len(labs) + 1) * RH + 30) + RH + 60
im = Image.new("RGB", (max(LW + 9 * CW + 20, 720), H), "white"); d = ImageDraw.Draw(im)
d.text((8, 8), "#274 mode 7 H-IRQ tests: share of frames with the black line, per H-IRQ value", font=FB, fill="black")
y = TOP
def cell(x, y, a, b, hw=None):
    if hw is not None:
        col, txt = hw
    elif b == 0: col, txt = (230, 230, 230), "-"
    elif a == b: col, txt = (20, 20, 20), ""
    elif a == 0: col, txt = (255, 255, 255), ""
    else: col, txt = (245, 150, 40), f"{round(100 * a / b)}"
    d.rectangle([x, y, x + CW - 2, y + RH - 2], fill=col, outline=(160, 160, 160))
    if txt: d.text((x + CW // 2, y + RH // 2), txt, font=FS, fill="black", anchor="mm")
for name in blocks:
    d.text((8, y + 4), name.replace("mode7_", ""), font=FB, fill="black")
    for h in range(9): d.text((LW + h * CW + CW // 2, y + 12), f"H {h}", font=FS, fill="black", anchor="mm")
    y += 24
    for who, (lo, hi) in [("paulb-nl", HW[name])] + ([("srg320", ALT[name])] if name in ALT else []):
        for h in range(9):
            if lo is None: hw = ((20, 20, 20), "") if h < 1 else ((255, 255, 255), "")
            elif h < lo: hw = ((20, 20, 20), "")
            elif h <= hi: hw = ((245, 150, 40), "fl")
            else: hw = ((255, 255, 255), "")
            cell(LW + h * CW, y, 0, 0, hw)
        d.text((8, y + 3), f"hardware ({who})", font=F, fill="black"); y += RH
    for lab in labs:
        d.text((8, y + 3), lab, font=F, fill="black")
        for h, (a, b) in enumerate(data.get((lab, name), [(0, 0)] * 9)): cell(LW + h * CW, y, a, b)
        y += RH
    y += 6
d.text((8, y + 4), "black: the line is black in every frame (the write is on time); white: never.", font=FS, fill="black")
d.text((8, y + 20), "orange: flickers (number = % of frames black on MiSTer/emulator; fl = flickers on hardware). Hardware: #274.", font=FS, fill="black")
im.save(out); print(out, im.size)
