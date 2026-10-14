# python sheet.py <dir> <out.png> [cols] [width]  -> labelled contact sheet of the stills
import sys, os
from PIL import Image, ImageDraw, ImageFont
d, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 10
w = int(sys.argv[4]) if len(sys.argv) > 4 else 216
fs = sorted(f for f in os.listdir(d) if f.endswith('.png'))
h = int(w * 1920 / 1080); rows = (len(fs) + cols - 1) // cols
S = Image.new('RGB', (cols * w, rows * (h + 22)), (20, 20, 20)); D = ImageDraw.Draw(S)
font = None
for fp in ('C:/Windows/Fonts/arialbd.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
           '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold.ttf'):
    try: font = ImageFont.truetype(fp, 16); break
    except Exception: pass
if font is None: font = ImageFont.load_default()
for i, f in enumerate(fs):
    im = Image.open(os.path.join(d, f)).convert('RGB').resize((w, h), Image.LANCZOS)
    x, y = (i % cols) * w, (i // cols) * (h + 22)
    S.paste(im, (x, y + 22)); D.text((x + 4, y + 2), f[1:-4] + 's', fill=(255, 255, 255), font=font)
S.save(out); print(out, S.size)
