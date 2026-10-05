#!/usr/bin/env python3
"""abpanel.py <out.png> <title> <label=image|-> ...: a labelled side-by-side of SNES screens, three per row.

Each image is brought to the core's 512x224 frame (any other size is a photo, fitted with its aspect kept) (Mesen's 256x239 buffer: rows 7-230, doubled across; bsnes v115's 512x240: rows 8-231; a 256-wide
shot doubled across), then doubled down to 512x448, nearest-neighbour. "label=-" draws an empty panel ("no capture"); "label=-:text" one carrying that text ("/n" breaks a line).
CROP=x0,y0,x1,y1 zooms into that box of the 512-wide frame (ZY = pixels per line; default keeps the aspect). TALL=1 keeps all 239 lines (overscan mode). An image may be "a.png+b.png+..." (stacked). A label may carry a second line after a '|'.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, LH, PAD, COLS, GAP = 512, 52, 8, 3, 4
TALL = os.environ.get("TALL") == "1"  # 239-line mode: keep every line, no crop
H = 478 if TALL else 448
CROP = [int(v) for v in os.environ["CROP"].split(",")] if os.environ.get("CROP") else None  # x0,y0,x1,y1 of the 512xN frame
if CROP:
    ZX = W / (CROP[2] - CROP[0])
    H = round((CROP[3] - CROP[1]) * float(os.environ.get("ZY", 2 * ZX)))


def norm(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    if (w, h) not in ((256, 224), (512, 224), (256, 239), (512, 239), (512, 240), (512, 448), (512, 478)):
        k = min(W / w, H / h)  # a photo: fit, aspect kept, on grey
        im = im.resize((max(1, round(w * k)), max(1, round(h * k))), Image.LANCZOS)
        bg = Image.new("RGB", (W, H), (40, 40, 40))
        bg.paste(im, ((W - im.size[0]) // 2, (H - im.size[1]) // 2))
        return bg
    if h in (239, 478) and not TALL:  # Mesen: a 224-line picture sits at rows 7-230
        k = h // 239
        im = im.crop((0, 7 * k, w, (7 + 224) * k))
    if h == 240:  # bsnes v115, overscan uncropped: line 1 at row 1 (239-line mode), row 8 (224-line mode)
        im = im.crop((0, 1, w, 240)) if TALL else im.crop((0, 8, w, 232))
    if im.size[1] in (448, 478):
        im = im.resize((im.size[0], 224), Image.NEAREST)
    if im.size[0] != 512:
        im = im.resize((512, im.size[1]), Image.NEAREST)
    if CROP:
        im = im.crop(tuple(CROP))
    return im.resize((W, H), Image.NEAREST)


def stack(path):
    """'a.png+b.png+c.png': the frames one under another (consecutive frames: one per IRQ dot phase)."""
    ims = [norm(q) for q in path.split("+")]
    out = Image.new("RGB", (W, len(ims) * (H + GAP) - GAP), (255, 255, 255))
    for i, im in enumerate(ims):
        out.paste(im, (0, i * (H + GAP)))
    return out


def main():
    out, title, items = sys.argv[1], sys.argv[2], sys.argv[3:]
    k = max(it.partition("=")[2].count("+") + 1 for it in items)
    PH = k * (H + GAP) - GAP
    cols = min(COLS, len(items))
    rows = (len(items) + cols - 1) // cols
    TH = 40
    sheet = Image.new("RGB", (cols * (W + PAD) + PAD, TH + rows * (PH + LH + PAD) + PAD), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    d.text((PAD, 8), title, fill=(0, 0, 0), font=ImageFont.truetype(FB, 22))
    f1, f2 = ImageFont.truetype(FB, 20), ImageFont.truetype(F, 15)
    for i, it in enumerate(items):
        lab, _, path = it.partition("=")
        l1, _, l2 = lab.partition("|")
        x = PAD + (i % cols) * (W + PAD)
        y = TH + (i // cols) * (PH + LH + PAD)
        d.text((x, y + 2), l1, fill=(0, 0, 0), font=f1)
        if l2:
            d.text((x, y + 28), l2, fill=(80, 80, 80), font=f2)
        if path.startswith("-"):
            msg = path[2:] if path.startswith("-:") else "no capture"
            d.rectangle((x, y + LH, x + W - 1, y + LH + PH - 1), fill=(225, 225, 225))
            d.multiline_text((x + W // 2, y + LH + PH // 2), msg.replace("/n", "\n"), fill=(90, 90, 90), font=f1,
                             anchor="mm", align="center", spacing=8)
        else:
            sheet.paste(stack(path), (x, y + LH))
    sheet.save(out, optimize=True)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
