#!/usr/bin/env python3
"""Turn a generated image into a 1080x1920 TikTok slide with TikTok-style text.

Usage:
  python overlay.py --in raw.png --out slide.png --text "POV: you finally found it" \
      [--position top|middle|bottom] [--style outline|box] [--size 64] [--fit crop|pad] [--font path.ttf]

Text style "outline" = white text with a black outline (the classic TikTok look).
"box" = black text on white rounded boxes, line by line (the TikTok "background" text style).
Keep text away from the bottom ~18% and right edge: TikTok's caption and buttons cover them.
"""
import argparse, os, re, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H = 1080, 1920
FONTS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",       # macOS
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",                              # Windows
    "/usr/share/fonts/opentype/inter/Inter-Bold.otf",            # Linux
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

def font(path, size):
    for p in ([path] if path else []) + FONTS:
        if p and os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)

def fit_canvas(img, mode):
    img = ImageOps.exif_transpose(img).convert("RGB")
    if mode == "crop":
        return ImageOps.fit(img, (W, H), Image.LANCZOS, centering=(0.5, 0.45))
    bg = ImageOps.fit(img, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
    fg = ImageOps.contain(img, (W, H), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    return bg

EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]")

def wrap(draw, text, fnt, max_w):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            test = (cur + " " + word).strip()
            if draw.textlength(test, font=fnt) <= max_w:
                cur = test
            else:
                if cur: lines.append(cur)
                cur = word
        lines.append(cur)
    return lines

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--text", default="")
    ap.add_argument("--position", default="top", choices=["top", "middle", "bottom"])
    ap.add_argument("--style", default="outline", choices=["outline", "box"])
    ap.add_argument("--size", type=int, default=72)
    ap.add_argument("--fit", default="crop", choices=["crop", "pad"])
    ap.add_argument("--font")
    a = ap.parse_args()

    img = fit_canvas(Image.open(a.inp), a.fit)
    d = ImageDraw.Draw(img)
    a.text = EMOJI.sub("", a.text).strip()  # most fonts lack emoji glyphs; they render as boxes
    if a.text:
        fnt = font(a.font, a.size)
        max_w = int(W * 0.80)
        lines = wrap(d, a.text, fnt, max_w)
        asc, desc = fnt.getmetrics()
        lh = int((asc + desc) * 1.18)
        block_h = lh * len(lines)
        safe_top, safe_bottom = int(H * 0.12), int(H * 0.80)
        y = {"top": safe_top + 40, "middle": (H - block_h) // 2, "bottom": safe_bottom - block_h}[a.position]
        for line in lines:
            tw = d.textlength(line, font=fnt)
            x = (W - tw) / 2 - 20  # nudge left, away from TikTok's right-side buttons
            if a.style == "box":
                pad = int(a.size * 0.28)
                d.rounded_rectangle([x - pad, y - pad * 0.4, x + tw + pad, y + asc + desc + pad * 0.4], radius=pad, fill="white")
                d.text((x, y), line, font=fnt, fill="black")
            else:
                d.text((x, y), line, font=fnt, fill="white", stroke_width=max(3, a.size // 12), stroke_fill="black")
            y += lh
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    img.save(a.out, quality=95)
    print(a.out)

if __name__ == "__main__":
    sys.exit(main())
