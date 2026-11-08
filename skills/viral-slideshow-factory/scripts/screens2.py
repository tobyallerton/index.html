#!/usr/bin/env python3
"""More screenshot slides (1080x1920), drawn so the words are exact and sharp, to copy winners that use:

  notification  iOS Notification Centre card, cropped and shown on black like a posted screenshot
  instagram     an Instagram text post (big bold words on a coloured square) with likes/comments row
  google        a Google search: query box, tabs and a big answer card or an "AI Overview" paragraph
  comment       a TikTok comment + reply, cropped and shown on black
  snapchat      a Snapchat story overlay on a photo: name bar at the top and black caption bars

Usage: python screens2.py spec.json   (same layout as screens.py: {"out_dir": "...", "screens": [ {...}, ... ]})
Every name and handle must be invented. Emoji in "text" fields are drawn in colour.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from screens import font, wrap, status_bar  # noqa: E402
from overlay import emoji_img, runs, EMOJI  # noqa: E402

W, H = 1080, 1920
FONTS = os.path.join(os.path.dirname(HERE), "fonts")

def text_emoji(img, xy, text, f, fill, anchor_center=False):
    """Draw text with colour emoji; returns width."""
    d = ImageDraw.Draw(img)
    asc, desc = f.getmetrics(); em = asc * 0.95
    total = sum(em * 1.12 if k == "e" else f.getlength(s) for k, s in runs(text))
    x, y = xy
    if anchor_center: x -= total / 2
    for k, s in runs(text):
        if k == "t":
            d.text((x, y), s, font=f, fill=fill); x += f.getlength(s)
        else:
            e = emoji_img(s, int(em))
            if e is not None: img.paste(e, (int(x + em * 0.06), int(y + (asc - em) * 0.6)), e)
            x += em * 1.12
    return total

def on_black(panel, y=None):
    img = Image.new("RGB", (W, H), (0, 0, 0))
    img.paste(panel, (0, y if y is not None else (H - panel.height) // 2 - 80))
    return img

def notification(s):
    """{"type":"notification","app":"Messages","sender":"Mum X","initial":"M","text":"...","ago":"now","wallpaper":"#1d4f6e"}"""
    ph = 560
    p = Image.new("RGB", (W, ph), s.get("wallpaper", "#1c4a66"))
    g = Image.linear_gradient("L").resize((W, ph)).rotate(90, expand=False)
    p = Image.composite(p, Image.new("RGB", (W, ph), "#0d2333"), g)
    d = ImageDraw.Draw(p)
    d.text((40, 6), "Notification Centre", font=font("semibold", 58), fill=(255, 255, 255))
    d.ellipse([W - 90, 18, W - 40, 68], fill=(80, 100, 115)); d.text((W - 65, 43), "×", font=font("regular", 40), fill="white", anchor="mm")
    card = [30, 110, W - 30, 110 + 330]
    d.rounded_rectangle(card, radius=44, fill=(70, 96, 112))
    d.ellipse([60, 160, 160, 260], fill=(150, 160, 170)); d.text((110, 210), s.get("initial", "M"), font=font("semibold", 50), fill="white", anchor="mm")
    d.ellipse([132, 228, 172, 268], fill=(52, 199, 89))
    d.text((190, 150), s["sender"], font=font("semibold", 38), fill="white")
    d.text((W - 70, 152), s.get("ago", "now"), font=font("regular", 32), fill=(200, 210, 218), anchor="ra")
    f = font("regular", 36); y = 200
    for l in wrap(d, EMOJI.sub("", s["text"]), f, W - 190 - 70):
        d.text((190, y), l, font=f, fill=(240, 244, 247)); y += 46
    d.rounded_rectangle([60, 470, W - 60, 560], radius=40, fill=(60, 84, 99))
    return on_black(p)

def instagram(s):
    """{"type":"instagram","user":"mia.c","lines":["TEA DRINKERS....","Dont forget ..."],"bg":"#f8d7e3","likes":"7.4K",
        "comments":"1.1K","shares":"842","caption":"who's getting it? 😭","ago":"5 hours ago","stories":["chloe.w",...]}"""
    img = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(img)
    top = 230
    for i, n in enumerate(s.get("stories", ["your story", "chloe.w", "sophie.l", "lauren.j", "maisie.h"])[:5]):
        cx = 110 + i * 215
        d.ellipse([cx - 80, top - 150, cx + 80, top + 10], outline=(230, 120, 60), width=6)
        d.ellipse([cx - 68, top - 138, cx + 68, top - 2], fill=[(176, 140, 120), (120, 150, 180), (190, 160, 130), (150, 120, 140), (130, 160, 140)][i])
        d.text((cx, top + 50), n, font=font("regular", 26), fill=(230, 230, 230), anchor="mm")
    y = top + 110
    d.ellipse([30, y, 110, y + 80], fill=(150, 120, 110))
    d.text((130, y + 40), s["user"], font=font("semibold", 34), fill="white", anchor="lm")
    d.text((W - 50, y + 36), "•••", font=font("semibold", 30), fill="white", anchor="mm")
    sq = top + 230
    d.rectangle([0, sq, W, sq + W], fill=s.get("bg", "#f7d6e2"))
    bf = os.path.join(FONTS, "Anton-Regular.ttf")
    yy = sq + 40
    from PIL import ImageFont
    for i, l in enumerate(s["lines"]):
        size = s.get("first_size", 170) if i == 0 else s.get("size", 110)
        f = ImageFont.truetype(bf, size)
        # condense: draw wide then squeeze horizontally like the original's tight bold type
        tw = int(text_width(l, f)) + 40
        tmp = Image.new("RGBA", (tw, int(size * 1.35)), (0, 0, 0, 0))
        text_emoji(tmp, (10, 0), l, f, (10, 10, 10))
        sx = min(1.0, (W - 40) / tmp.width)
        tmp = tmp.resize((int(tmp.width * sx), tmp.height), Image.LANCZOS)
        img.paste(tmp, (20, yy), tmp); yy += int(size * 1.12)
    d = ImageDraw.Draw(img)
    ry = sq + W + 40
    d.text((40, ry), "♥", font=font("semibold", 56), fill=(237, 73, 86))
    d.text((110, ry + 12), s.get("likes", "7.4K"), font=font("regular", 32), fill="white")
    d.text((250, ry + 4), "◯", font=font("regular", 48), fill="white")
    d.text((322, ry + 12), s.get("comments", "1.1K"), font=font("regular", 32), fill="white")
    d.text((440, ry + 4), "▷", font=font("regular", 48), fill="white")
    d.text((500, ry + 12), s.get("shares", "842"), font=font("regular", 32), fill="white")
    d.polygon([(W - 92, ry + 6), (W - 52, ry + 6), (W - 52, ry + 58), (W - 72, ry + 42), (W - 92, ry + 58)], outline="white", width=4)
    w = d.textlength(s["user"] + " ", font=font("semibold", 32))
    d.text((40, ry + 90), s["user"], font=font("semibold", 32), fill="white")
    text_emoji(img, (40 + w, ry + 90), s.get("caption", ""), font("regular", 32), (240, 240, 240))
    d.text((40, ry + 140), s.get("ago", "5 hours ago"), font=font("regular", 26), fill=(150, 150, 150))
    return img

def text_width(t, f):
    asc, _ = f.getmetrics()
    return sum(asc * 0.95 * 1.12 if k == "e" else f.getlength(x) for k, x in runs(t))

def google(s):
    """{"type":"google","dark":true,"query":"how many days left in november","card":{"label":"Duration › Day","big":"22 days","small":"8 November – 30 November 2026"}}
       or "overview":["paragraph", ...] for an AI Overview answer. "full": true draws a full-height screen with status bar."""
    dark = s.get("dark", True)
    bg, fg, sub, box = ((32, 33, 36), (232, 234, 237), (154, 160, 166), (48, 49, 52)) if dark else ((255, 255, 255), (32, 33, 36), (95, 99, 104), (241, 243, 244))
    full = s.get("full", False)
    ph = H if full else 760
    p = Image.new("RGB", (W, ph), bg); d = ImageDraw.Draw(p)
    y = 0
    if full:
        status_bar(d, s.get("time", "22:53"), fg); y = 120
    gf = font("medium", 64)
    gx = W / 2 - d.textlength("Google", font=gf) / 2
    for ch, col in zip("Google", [(66, 133, 244), (234, 67, 53), (251, 188, 5), (66, 133, 244), (52, 168, 83), (234, 67, 53)]):
        d.text((gx, y + 20), ch, font=gf, fill=col if not dark else (232, 234, 237)); gx += d.textlength(ch, font=gf)
    y += 130
    d.rounded_rectangle([30, y, W - 30, y + 100], radius=50, fill=box)
    d.text((110, y + 50), s["query"], font=font("regular", 34), fill=fg, anchor="lm")
    d.ellipse([52, y + 32, 84, y + 64], outline=sub, width=4)
    y += 140
    tx = 40
    for i, t in enumerate(["AI Mode", "All", "Images", "News", "Videos", "Shopping"]):
        d.text((tx, y), t, font=font("medium" if t == "All" else "regular", 30), fill=fg if t == "All" else sub)
        if t == "All": d.line([tx, y + 48, tx + d.textlength(t, font=font("medium", 30)), y + 48], fill=fg, width=5)
        tx += d.textlength(t, font=font("regular", 30)) + 50
    y += 80
    d.line([0, y, W, y], fill=box, width=2); y += 40
    if s.get("card"):
        c = s["card"]
        d.text((40, y), c.get("label", ""), font=font("regular", 28), fill=sub); y += 60
        d.rounded_rectangle([30, y, W - 30, y + 250], radius=30, fill=box)
        d.text((W / 2, y + 100), c["big"], font=font("regular", 84), fill=fg, anchor="mm")
        d.text((W / 2, y + 190), c.get("small", ""), font=font("regular", 28), fill=sub, anchor="mm")
        y += 290
    if s.get("overview"):
        d.text((90, y), "AI Overview", font=font("medium", 32), fill=fg)
        d.text((40, y - 4), "✦", font=font("regular", 40), fill=(66, 133, 244)); y += 80
        for para in s["overview"]:
            for l in wrap(d, para, font("regular", 36), W - 80):
                d.text((40, y), l, font=font("regular", 36), fill=fg); y += 50
            y += 40
    if full: return p
    return on_black(p)

def comment(s):
    """{"type":"comment","user":"ellie.h","text":"...","likes":"1.8K","date":"11-06","reply":{"user":"sophie.w","text":"you dont have to!","likes":"67"}}"""
    p = Image.new("RGB", (W, 620), (18, 18, 18)); d = ImageDraw.Draw(p)
    def one(x, y, user, text, likes, date, r):
        d.ellipse([x, y, x + 2 * r, y + 2 * r], fill=(180, 150, 140))
        tx = x + 2 * r + 24
        d.text((tx, y), user, font=font("medium", 32), fill=(235, 235, 235))
        ty = y + 46
        for l in wrap(d, EMOJI.sub("", text), font("regular", 38), W - tx - 140):
            d.text((tx, ty), l, font=font("regular", 38), fill=(240, 240, 240)); ty += 50
        d.text((tx, ty + 8), f"{date}    Reply", font=font("regular", 28), fill=(140, 140, 146))
        d.text((W - 150, ty + 8), "♡ " + likes, font=font("regular", 30), fill=(140, 140, 146))
        return ty + 70
    y = one(40, 40, s["user"], s["text"], s.get("likes", ""), s.get("date", "11-06"), 48)
    if s.get("reply"):
        r = s["reply"]; y = one(170, y, r["user"], r["text"], r.get("likes", ""), r.get("date", "11-06"), 36)
    return on_black(p.crop((0, 0, W, y + 10)), y=300)

def snapchat(s):
    """{"type":"snapchat","bg":"raw/x.png","name":"Brooke","ago":"5m ago","captions":[{"text":"plotted...","y":0.30,"align":"left"},{"text":"wait i need her set","y":0.39}]}"""
    img = ImageOps.fit(Image.open(s["bg"]).convert("RGB"), (W, H), Image.LANCZOS)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([36, 60, 126, 150], fill=(255, 220, 120))
    d.text((150, 66), s.get("name", "Brooke"), font=font("semibold", 36), fill="white")
    d.text((150, 112), s.get("ago", "5m ago"), font=font("regular", 28), fill=(235, 235, 235))
    d.text((W - 50, 100), "⋮", font=font("semibold", 44), fill="white", anchor="mm")
    for c in s.get("captions", []):
        y = int(H * c["y"])
        d.rectangle([0, y, W, y + 82], fill=(0, 0, 0, 140))
        f = font("regular", 40)
        if c.get("align") == "left":
            d.text((120, y + 41), c["text"], font=f, fill="white", anchor="lm")
        else:
            d.text((W / 2, y + 41), c["text"], font=f, fill="white", anchor="mm")
    return img

def main():
    spec_path = os.path.abspath(sys.argv[1])
    spec = json.load(open(spec_path, encoding="utf-8"))
    os.chdir(os.path.dirname(spec_path))
    out_dir = spec.get("out_dir", ".")
    os.makedirs(out_dir, exist_ok=True)
    outs = []
    for s in spec["screens"]:
        img = {"notification": notification, "instagram": instagram, "google": google, "comment": comment, "snapchat": snapchat}[s["type"]](s)
        p = os.path.join(out_dir, s["out"]); img.convert("RGB").save(p); outs.append(p)
    print(json.dumps({"screens": outs}))

if __name__ == "__main__":
    main()
