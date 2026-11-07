#!/usr/bin/env python3
"""Turn a generated image into a 1080x1920 TikTok slide with TikTok-style text (TikTok Sans + colour emoji).

Usage:
  python overlay.py --in raw.png --out slide.png --text "POV: you finally found it 😭" \
      [--position top|middle|bottom] [--y 0.3] [--style outline|box|plain] [--size 54] [--fit crop|pad]

Styles (match the original winner):
  outline  white text, thin dark edge and soft shadow: TikTok's default look on photos
  box      black text on white rounded boxes, one box per line: TikTok's "background" style
  plain    white text with a soft shadow only (for darker photos)
Text keeps its emoji (drawn in colour). Keep it short, lower-case and casual, like a real creator types.
Stays out of the bottom ~20% and the right-hand buttons, which TikTok covers.
"""
import argparse, os, re, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(os.path.dirname(HERE), "fonts")
EMOJI_FONTS = ["/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", "/System/Library/Fonts/Apple Color Emoji.ttc",
               "C:/Windows/Fonts/seguiemj.ttf"]
FALLBACK = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
EMOJI = re.compile("((?:[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\u2300-\u23FF](?:\uFE0F)?(?:\u200D[\U0001F000-\U0001FAFF\u2600-\u27BF](?:\uFE0F)?)*|[\U0001F1E6-\U0001F1FF]{2}))")

def font(path, size, weight="Bold"):
    for p in ([path] if path else []) + [os.path.join(FONT_DIR, f"TikTokSans-{weight}.ttf")] + FALLBACK:
        if p and os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)

_emoji_font = None
def emoji_img(ch, px):
    """Render one emoji in colour, scaled to px high. None if no colour emoji font."""
    global _emoji_font
    if _emoji_font is None:
        _emoji_font = False
        for p in EMOJI_FONTS:
            if os.path.exists(p):
                try: _emoji_font = ImageFont.truetype(p, 109); break
                except Exception: pass
    if not _emoji_font: return None
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    try: ImageDraw.Draw(im).text((10, 10), ch, font=_emoji_font, embedded_color=True)
    except Exception: return None
    bb = im.getbbox()
    if not bb: return None
    im = im.crop(bb)
    return im.resize((max(1, int(im.width * px / im.height)), px), Image.LANCZOS)

def runs(text):
    out = []
    for part in EMOJI.split(text):
        if not part: continue
        out.append(("e", part) if EMOJI.fullmatch(part) else ("t", part.replace("\uFE0F", "")))
    return out

def run_width(r, f, em):
    return em * 1.12 if r[0] == "e" else f.getlength(r[1])

def wrap(text, f, em, max_w):
    lines = []
    for para in text.split("\n"):
        words, cur, cur_w = para.split(" "), [], 0.0
        for w in words:
            ww = sum(run_width(r, f, em) for r in runs(w))
            sp = f.getlength(" ") if cur else 0
            if cur and cur_w + sp + ww > max_w:
                lines.append(" ".join(cur)); cur, cur_w = [w], ww
            else:
                cur.append(w); cur_w += sp + ww
        lines.append(" ".join(cur))
    return [l for l in lines]

def line_width(line, f, em):
    return sum(run_width(r, f, em) for r in runs(line))

def draw_line(img, x, y, line, f, em, fill, stroke=0, stroke_fill=None):
    d = ImageDraw.Draw(img)
    asc, desc = f.getmetrics()
    for kind, s in runs(line):
        if kind == "t":
            d.text((x, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
            x += f.getlength(s)
        else:
            e = emoji_img(s, int(em))
            if e is not None:
                img.paste(e, (int(x + em * 0.06), int(y + (asc - em) * 0.75)), e)
            x += em * 1.12

def fit_canvas(img, mode):
    img = ImageOps.exif_transpose(img).convert("RGB")
    if mode == "crop":
        return ImageOps.fit(img, (W, H), Image.LANCZOS, centering=(0.5, 0.45))
    bg = ImageOps.fit(img, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
    fg = ImageOps.contain(img, (W, H), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    return bg

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--text", default="")
    ap.add_argument("--position", default="top", choices=["top", "middle", "bottom"])
    ap.add_argument("--y", type=float, default=None, help="top of the text block as a fraction of the height")
    ap.add_argument("--style", default="outline", choices=["outline", "box", "plain"])
    ap.add_argument("--size", type=int, default=54)
    ap.add_argument("--fit", default="crop", choices=["crop", "pad"])
    ap.add_argument("--font")
    a = ap.parse_args()

    base = fit_canvas(Image.open(a.inp), a.fit).convert("RGBA")
    text = a.text.strip()
    if text:
        f = font(a.font, a.size, "Bold" if a.style != "box" else "Bold")
        em = a.size * 0.95
        max_w = int(W * 0.78)
        lines = wrap(text, f, em, max_w)
        asc, desc = f.getmetrics()
        lh = int((asc + desc) * (1.32 if a.style == "box" else 1.14))
        block_h = lh * len(lines)
        safe_top, safe_bottom = int(H * 0.12), int(H * 0.79)
        y = int(H * a.y) if a.y is not None else {"top": int(H * 0.17), "middle": (H - block_h) // 2, "bottom": safe_bottom - block_h}[a.position]
        y = max(safe_top, min(y, safe_bottom - block_h))
        layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        if a.style == "box":
            pad_x, pad_y, r = int(a.size * 0.36), int(a.size * 0.16), int(a.size * 0.30)
            d = ImageDraw.Draw(layer)
            for i, line in enumerate(lines):
                lw = line_width(line, f, em); x = (W - lw) / 2 - 18
                d.rounded_rectangle([x - pad_x, y + i * lh - pad_y, x + lw + pad_x, y + i * lh + asc + desc + pad_y * 0.6], radius=r, fill=(255, 255, 255, 255))
            for i, line in enumerate(lines):
                lw = line_width(line, f, em); x = (W - lw) / 2 - 18
                draw_line(layer, x, y + i * lh, line, f, em, fill=(0, 0, 0, 255))
        else:
            shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
            for i, line in enumerate(lines):
                lw = line_width(line, f, em); x = (W - lw) / 2 - 18
                draw_line(shadow, x + 2, y + i * lh + 3, line, f, em, fill=(0, 0, 0, 170),
                          stroke=max(2, a.size // 16) if a.style == "outline" else 0, stroke_fill=(0, 0, 0, 170))
            layer = Image.alpha_composite(layer, shadow.filter(ImageFilter.GaussianBlur(3)))
            for i, line in enumerate(lines):
                lw = line_width(line, f, em); x = (W - lw) / 2 - 18
                draw_line(layer, x, y + i * lh, line, f, em, fill=(255, 255, 255, 255),
                          stroke=max(2, a.size // 22) if a.style == "outline" else 0, stroke_fill=(20, 20, 20, 255))
        base = Image.alpha_composite(base, layer)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    base.convert("RGB").save(a.out, quality=95)
    print(a.out)

if __name__ == "__main__":
    sys.exit(main())
