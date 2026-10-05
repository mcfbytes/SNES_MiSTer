import sys
from PIL import Image, ImageDraw
rows = sys.argv[2:]; out = sys.argv[1]
ims = []
for spec in rows:
    lab, p = spec.split("=", 1)
    im = Image.open(p).convert("RGB")
    if im.width < 400: im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    c = Image.new("RGB", (im.width + 70, im.height), (40, 40, 40)); c.paste(im, (70, 0))
    ImageDraw.Draw(c).text((4, 4), lab, fill=(255, 255, 0)); ims.append(c)
W = max(i.width for i in ims); H = sum(i.height + 4 for i in ims)
s = Image.new("RGB", (W, H), (0, 0, 0)); y = 0
for i in ims: s.paste(i, (0, y)); y += i.height + 4
s.save(out)
