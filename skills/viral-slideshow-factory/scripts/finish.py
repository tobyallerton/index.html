#!/usr/bin/env python3
"""Check and package one finished slideshow.

Usage: python finish.py "<Slideshows/date/NN - Product - FORMAT>"

Reads _build/post.json and _build/slides.json, then:
  - checks the posting pack is complete
  - price check: every £/$ amount and "% off" in the slide text, title and caption must match
    the price recorded from the product page (ERROR otherwise)
  - flags risky claims and fake urgency (WARN)
  - writes post.txt (ready to copy when posting)
  - builds comparison.png: viral original (top row) vs our remake (bottom row)
Exits with code 1 if there is any ERROR.
"""
import glob, json, os, re, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

RISKY = [
    r"\bcure[sd]?\b", r"\bheal(s|ed|ing)?\b", r"\btreat(s|ed|ment)?\b", r"\bclinically\b", r"\bproven\b",
    r"\bguarantee[sd]?\b", r"\bdoctor\b", r"\bdermatologist\b", r"\bmedical\b", r"\bprescription\b",
    r"\blose weight\b", r"\bweight loss\b", r"\bfat burn", r"\b\d+\s?(kg|lbs?|pounds|stone)\b",
    r"\banxiety\b", r"\bdepression\b", r"\bacne\b", r"\beczema\b", r"\bhair loss\b", r"\bregrow",
    r"\bdetox\b", r"\bimmune\b", r"\bpain relief\b", r"\bmiracle\b", r"\b100% (safe|natural|effective)\b",
]
# The last slide must tell people what to do next (soft call to action).
CTA = re.compile(r"basket|cheap|bargain|link|shop|tap|grab|get (yours|one|it)|check (it )?out|below|in my (bio|showcase)|buy|order|add to cart", re.I)
URGENCY = [r"only \d+ left", r"selling out", r"last chance", r"ends (tonight|today)", r"limited stock", r"almost gone"]
MONEY = re.compile(r"([£$])\s?(\d+(?:[.,]\d{1,2})?)")
PCT = re.compile(r"(\d{1,2})\s?%\s?off", re.I)
SYM = {"GBP": "£", "USD": "$"}

errors, warns = [], []

def get(d, path):
    for k in path.split("."):
        if not isinstance(d, dict) or d.get(k) in (None, "", []):
            return None
        d = d[k]
    return d

def check(post, slides):
    for f in ["title", "caption", "hashtags", "sound.name", "product.name", "product.url",
              "product.price", "product.currency", "product.checked_at", "hooks.used"]:
        if get(post, f) is None:
            errors.append(f"post.json is missing {f}")
    if get(post, "source.mode") in ("A", "B") and not get(post, "source.url"):
        errors.append("post.json is missing source.url (the original post link)")
    cpp = get(post, "product.commission_per_sale")
    if cpp is None:
        warns.append("commission_per_sale not recorded")

    sl = slides.get("slides", [])
    if sl and not CTA.search(str(sl[-1].get("text", ""))):
        errors.append("last slide has no call to action (e.g. 'linked in the basket', 'tap the basket') - every slideshow must end with one")
    texts = [("title", post.get("title", "")), ("caption", post.get("caption", ""))]
    texts += [(f"slide {i}", s.get("text", "")) for i, s in enumerate(slides.get("slides", []), 1)]
    price, was = get(post, "product.price"), get(post, "product.was_price")
    sym = SYM.get(str(get(post, "product.currency") or "").upper())
    allowed = [p for p in (price, was) if isinstance(p, (int, float))]
    for where, t in texts:
        t = str(t)
        for s, amt in MONEY.findall(t):
            v = float(amt.replace(",", "."))
            if sym and s != sym:
                errors.append(f"{where}: '{s}{amt}' uses the wrong currency (product is {get(post, 'product.currency')})")
            elif not any(abs(v - p) < 0.006 for p in allowed):
                errors.append(f"{where}: price '{s}{amt}' doesn't match the checked price {allowed} — fix the text or re-check the listing")
        for pct in PCT.findall(t):
            if not (isinstance(was, (int, float)) and isinstance(price, (int, float)) and was > price):
                errors.append(f"{where}: says '{pct}% off' but no crossed-out price was recorded")
            elif abs(round((1 - price / was) * 100) - int(pct)) > 1:
                errors.append(f"{where}: says '{pct}% off' but the real discount is {round((1 - price / was) * 100)}%")
        low = t.lower()
        for r in RISKY:
            m = re.search(r, low)
            if m:
                warns.append(f"{where}: possible health/result claim '{m.group(0)}' — keep only if the product listing itself says it")
        for r in URGENCY:
            m = re.search(r, low)
            if m:
                warns.append(f"{where}: urgency '{m.group(0)}' — only keep if it's true on the listing right now")

def write_post_txt(folder, post, n_slides):
    p = post.get("product", {})
    sym = SYM.get(str(p.get("currency", "")).upper(), "")
    m = lambda v: f"{float(v):.2f}" if isinstance(v, (int, float)) else str(v)
    price = f"{sym}{m(p.get('price'))}" + (f" (was {sym}{m(p['was_price'])})" if p.get("was_price") else "")
    lines = [
        f"TITLE\n{post.get('title', '')}\n",
        f"CAPTION\n{post.get('caption', '')}\n\n{' '.join(post.get('hashtags', []))}\n",
        f"SOUND\n{get(post, 'sound.name') or ''}\n{get(post, 'sound.url') or ''}\n{get(post, 'sound.why') or ''}\n",
        f"PRODUCT LINK (add to the post)\n{p.get('name', '')}\n{p.get('url', '')}\n",
        f"PRICE CHECK\n{price} — checked {p.get('checked_at', '?')} on {p.get('checked_on', 'the product page')}"
        + (f"\nCommission per sale: {sym}{float(p['commission_per_sale']):.2f}" if p.get("commission_per_sale") else "")
        + "\nRe-check the price before posting if it's been more than a day.\n",
        f"SLIDES\nPost slide-1.png to slide-{n_slides}.png in order.\n",
        "BEFORE YOU POST\n- Switch on the 'AI-generated content' label.\n- Add the product link above.\n- Pick the sound above (or a similar trending one).\n",
        f"SOURCE (for your reference, don't post)\nFormat: {get(post, 'source.format') or ''}\nInspired by: {get(post, 'source.url') or 'your own idea'}"
        + (f" ({get(post, 'source.creator')}, {get(post, 'source.views')} views, {get(post, 'source.gmv')} GMV)" if get(post, "source.creator") else "") + "\n",
    ]
    with open(os.path.join(folder, "post.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def font(size):
    for p in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)

def numkey(p):
    n = re.findall(r"\d+", os.path.basename(p))
    return (int(n[-1]) if n else 0, p)

def comparison(folder):
    ours = sorted(glob.glob(os.path.join(folder, "slide-*.png")), key=numkey)
    orig = sorted([p for p in glob.glob(os.path.join(folder, "_build", "original", "*"))
                   if p.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))], key=numkey)
    if not orig:
        warns.append("no original slides in _build/original/ — comparison shows only our slides")
    tw, th, gap, label_w = 300, 533, 12, 70
    cols = max(len(ours), len(orig), 1)
    rows = [("ORIGINAL", orig), ("OURS", ours)] if orig else [("OURS", ours)]
    W = label_w + cols * (tw + gap) + gap
    H = len(rows) * (th + gap) + gap
    sheet = Image.new("RGB", (W, H), (18, 18, 18))
    d = ImageDraw.Draw(sheet)
    f = font(30)
    for r, (label, imgs) in enumerate(rows):
        y = gap + r * (th + gap)
        txt = Image.new("RGBA", (th, label_w), (0, 0, 0, 0))
        ImageDraw.Draw(txt).text((th / 2, label_w / 2), label, font=f, fill=(255, 255, 255), anchor="mm")
        sheet.paste(txt.rotate(90, expand=True), (0, y), txt.rotate(90, expand=True))
        for c, p in enumerate(imgs):
            try:
                im = ImageOps.pad(ImageOps.exif_transpose(Image.open(p)).convert("RGB"), (tw, th), color=(0, 0, 0))
            except Exception as e:
                warns.append(f"couldn't open {p}: {e}")
                continue
            sheet.paste(im, (label_w + gap + c * (tw + gap), y))
    out = os.path.join(folder, "comparison.png")
    sheet.save(out)
    return out

def main():
    folder = os.path.abspath(sys.argv[1])
    b = os.path.join(folder, "_build")
    try:
        post = json.load(open(os.path.join(b, "post.json"), encoding="utf-8"))
    except Exception as e:
        sys.exit(f"ERROR: can't read _build/post.json: {e}")
    try:
        slides = json.load(open(os.path.join(b, "slides.json"), encoding="utf-8"))
    except Exception as e:
        slides = {"slides": []}
        errors.append(f"can't read _build/slides.json: {e}")
    finished = glob.glob(os.path.join(folder, "slide-*.png"))
    if not finished:
        errors.append("no finished slide-N.png files in the slideshow folder (run make_slides.py and move them up)")
    elif slides.get("slides") and len(finished) != len(slides["slides"]):
        warns.append(f"{len(finished)} finished slides but slides.json lists {len(slides['slides'])}")
    check(post, slides)
    write_post_txt(folder, post, len(finished))
    comp = comparison(folder)
    for w in warns:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    print(json.dumps({"ok": not errors, "post_txt": os.path.join(folder, "post.txt"), "comparison": comp,
                      "errors": len(errors), "warnings": len(warns)}))
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
