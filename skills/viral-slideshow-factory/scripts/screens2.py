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

def groupchat(s):
    """iMessage-style chat that also supports group sender names and a bank-transfer bubble.
    {"type":"groupchat","title":"The Fam 🎄","members":5,"light":true,"time":"19:42","messages":[
       {"from":"them","name":"Aunt Sue","text":"..."}, {"from":"me","text":"..."},
       {"from":"them","name":"Jake","kind":"payment","bank":"You've received money","note":"get the one you keep showing me"}]}"""
    light = s.get("light", True)
    bg, fg = ((255, 255, 255), (0, 0, 0)) if light else ((0, 0, 0), (255, 255, 255))
    them_bg, them_fg = ((233, 233, 235), (0, 0, 0)) if light else ((38, 38, 40), (255, 255, 255))
    sub = (140, 140, 146)
    img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img)
    status_bar(d, s.get("time", "19:42"), fg)
    d.rectangle([0, 120, W, 340], fill=(246, 246, 246) if light else (22, 22, 24))
    blue = (10, 132, 255)
    d.line([(60, 205), (38, 228), (60, 251)], fill=blue, width=7, joint="curve")
    n = s.get("members", 1)
    cols = [(176, 140, 120), (120, 150, 180), (190, 160, 130), (150, 120, 140), (130, 160, 140)]
    if n > 1:
        for i in range(min(n, 4)):
            cx = W / 2 - 75 + i * 50
            d.ellipse([cx - 40, 150 + (i % 2) * 12, cx + 40, 230 + (i % 2) * 12], fill=cols[i], outline=bg, width=4)
    else:
        d.ellipse([W / 2 - 52, 140, W / 2 + 52, 244], fill=(110, 110, 118))
        d.text((W / 2, 192), s["title"][:1].upper(), font=font("medium", 54), fill=fg, anchor="mm")
    text_emoji(img, (W / 2, 268), s["title"] + "  ›", font("regular", 30), (60, 60, 66) if light else (210, 210, 215), anchor_center=True)
    d.rounded_rectangle([W - 120, 196, W - 64, 232], radius=8, outline=blue, width=5)
    d.polygon([(W - 64, 214), (W - 40, 200), (W - 40, 228)], fill=blue)
    d.text((W / 2, 380), s.get("stamp", "Today " + s.get("time", "19:42")), font=font("medium", 26), fill=sub, anchor="mm")
    f = font("regular", 40); y = 420; max_w = 640; prev = None
    for m in s["messages"]:
        mine = m.get("from") == "me"
        if not mine and n > 1 and m.get("name") and (prev != m.get("name")):
            y += 20; d.text((150, y), m["name"], font=font("regular", 26), fill=sub); y += 34
        else:
            y += 14 if prev == (m.get("name") if not mine else "me") else 30
        if m.get("kind") == "payment":
            bw, bh = 560, 230; x0 = W - 40 - bw if mine else (130 if n > 1 else 40)
            d.rounded_rectangle([x0, y, x0 + bw, y + bh], radius=36, fill=them_bg if not mine else blue)
            tc = them_fg if not mine else (255, 255, 255)
            d.ellipse([x0 + 30, y + 30, x0 + 96, y + 96], fill=(0, 180, 120)); d.text((x0 + 63, y + 63), "£", font=font("semibold", 40), fill="white", anchor="mm")
            d.text((x0 + 116, y + 34), m.get("bank", "You've received money"), font=font("semibold", 34), fill=tc)
            d.text((x0 + 116, y + 80), "Bank transfer", font=font("regular", 28), fill=sub)
            for i, l in enumerate(wrap(d, m.get("note", ""), font("regular", 32), bw - 60)[:2]):
                d.text((x0 + 30, y + 130 + i * 42), l, font=font("regular", 32), fill=tc)
        else:
            lines = wrap(d, EMOJI.sub("", m["text"]).strip(), f, max_w)
            tw = max(d.textlength(l, font=f) for l in lines); lh = 52; bh = len(lines) * lh + 34; bw = tw + 56
            x0 = W - 40 - bw if mine else (130 if n > 1 else 40)
            d.rounded_rectangle([x0, y, x0 + bw, y + bh], radius=40, fill=blue if mine else them_bg)
            for i, l in enumerate(lines):
                d.text((x0 + 28, y + 14 + i * lh), l, font=f, fill=(255, 255, 255) if mine else them_fg)
        if not mine and n > 1:
            ci = sum(map(ord, m.get("name", "x"))) % len(cols)
            d.ellipse([40, y + bh - 70, 110, y + bh], fill=cols[ci])
            d.text((75, y + bh - 35), m.get("name", "x")[:1], font=font("medium", 30), fill="white", anchor="mm")
        y += bh; prev = m.get("name") if not mine else "me"
    if s.get("read"):
        d.text((W - 44, y + 14), s["read"], font=font("medium", 28), fill=sub, anchor="ra")
    d.rounded_rectangle([130, H - 150, W - 40, H - 70], radius=40, outline=(205, 205, 210) if light else (60, 60, 64), width=3)
    d.text((170, H - 110), "iMessage", font=font("regular", 36), fill=(130, 130, 136), anchor="lm")
    d.ellipse([40, H - 145, 110, H - 75], fill=(233, 233, 235) if light else (44, 44, 48)); d.text((75, H - 110), "+", font=font("regular", 50), fill=sub, anchor="mm")
    return img

def facebook(s):
    """Facebook text post, light, shown on white. {"type":"facebook","name":"Kerry B","date":"14 Nov","text":"\"reminder to ...\"...","reacts":"You, Sarah Jones and 1.5K others"}"""
    p = Image.new("RGB", (W, 760), (255, 255, 255)); d = ImageDraw.Draw(p)
    d.line([(46, 70), (26, 90), (46, 110)], fill=(30, 30, 30), width=6)
    d.ellipse([70, 40, 170, 140], fill=(150, 120, 100))
    d.text((190, 50), s["name"], font=font("semibold", 36), fill=(5, 5, 5))
    d.text((190, 98), s.get("date", "14 Nov") + " · 🌐".replace("🌐", "◍"), font=font("regular", 28), fill=(101, 103, 107))
    d.text((W - 50, 80), "•••", font=font("semibold", 30), fill=(60, 60, 60), anchor="mm")
    y = 190
    for l in wrap(d, s["text"], font("regular", 46), W - 100):
        d.text((50, y), l, font=font("regular", 46), fill=(5, 5, 5)); y += 62
    y += 40; d.line([(40, y), (W - 40, y)], fill=(220, 222, 226), width=2); y += 26
    for i, t in enumerate(["👍 Like", "💬 Comment", "➤ Send", "↪ Share"]):
        text_emoji(p, (60 + i * 255, y), t, font("regular", 30), (101, 103, 107))
    y += 70; d.line([(40, y), (W - 40, y)], fill=(220, 222, 226), width=2); y += 26
    text_emoji(p, (50, y), "😆❤️👍 " + s.get("reacts", "You and 1.5K others"), font("regular", 30), (60, 60, 60))
    p = p.crop((0, 0, W, y + 70))
    img = Image.new("RGB", (W, H), (255, 255, 255)); img.paste(p, (0, 200))
    return img

def tweet(s):
    """X/Twitter post with optional photo and reply. {"type":"tweet","name":"Ellie 🎀","handle":"@ellie_x","ago":"8h","text":"...","photo":"raw/x.png","stats":["437","1.2K","12K","620K"],
        "reply":{"name":"mads","handle":"@madds_lee","ago":"7h","text":"let me know when you find out","stats":["9","15","412","27K"]}}"""
    img = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(img)
    def post(y, t, photo=None):
        d.ellipse([40, y, 140, y + 100], fill=(150, 120, 110))
        x = 165
        w = text_emoji(img, (x, y + 4), t["name"], font("semibold", 34), (15, 20, 25))
        d.text((x + w + 12, y + 6), f"{t['handle']} · {t.get('ago', '8h')}", font=font("regular", 32), fill=(83, 100, 113))
        ty = y + 54
        for l in wrap(d, t["text"], font("regular", 36), W - x - 50):
            text_emoji(img, (x, ty), l, font("regular", 36), (15, 20, 25)); ty += 48
        if photo:
            ph = ImageOps.fit(Image.open(photo).convert("RGB"), (W - x - 50, 760), Image.LANCZOS)
            m = Image.new("L", ph.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, ph.width, ph.height], radius=30, fill=255)
            img.paste(ph, (x, ty + 14), m); ty += 790
        sx = x
        for icon, v in zip(["◯", "⇄", "♡", "▥"], t.get("stats", ["437", "1.2K", "12K", "620K"])):
            d.text((sx, ty + 12), f"{icon} {v}", font=font("regular", 28), fill=(83, 100, 113)); sx += 190
        return ty + 80
    y = post(120, s, s.get("photo"))
    if s.get("reply"):
        d.line([(90, 230), (90, y - 30)], fill=(207, 217, 222), width=4)
        post(y, s["reply"])
    return img

def pastel(s):
    """Text-only slide on a soft pastel background, serif type, like the US parenting-book lists.
    {"type":"pastel","bg":"#f6d5c8","title":"#1","head":"Once a month...","body":["line", "line"]} or {"type":"pastel","cover":"Christmas Traditions ..."}"""
    from PIL import ImageFont
    bg = s.get("bg", "#f6d5c8")
    img = Image.new("RGB", (W, H), bg)
    glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse([-200, 300, W + 200, H - 300], fill=70)
    img = Image.composite(Image.new("RGB", (W, H), "#fff3ec"), img, glow.filter(ImageFilter.GaussianBlur(160)))
    d = ImageDraw.Draw(img)
    serif = lambda w, sz: (lambda f: (f.set_variation_by_axes([w]), f)[1])(ImageFont.truetype(os.path.join(FONTS, "PlayfairDisplay-Variable.ttf"), sz))
    col = (40, 30, 30)
    if s.get("cover"):
        lines = wrap(d, s["cover"], serif(400, 62), W - 220); y = H / 2 - len(lines) * 40
        for l in lines: d.text((W / 2, y), l, font=serif(400, 62), fill=col, anchor="mm"); y += 80
    else:
        y = 700
        d.text((W / 2, y), s["title"], font=serif(700, 48), fill=col, anchor="mm"); y += 80
        for l in wrap(d, s["head"], serif(700, 54), W - 240):
            d.text((W / 2, y), l, font=serif(700, 54), fill=col, anchor="mm"); y += 70
        y += 40
        for para in s.get("body", []):
            for l in wrap(d, para, serif(400, 40), W - 300):
                d.text((W / 2, y), l, font=serif(400, 40), fill=col, anchor="mm"); y += 54
            y += 34
    for i in range(6):
        text_emoji(img, (60 + i * 190, H - 120), "🤍", font("regular", 40), col)
    return img

def main():
    spec_path = os.path.abspath(sys.argv[1])
    spec = json.load(open(spec_path, encoding="utf-8"))
    os.chdir(os.path.dirname(spec_path))
    out_dir = spec.get("out_dir", ".")
    os.makedirs(out_dir, exist_ok=True)
    outs = []
    for s in spec["screens"]:
        img = {"notification": notification, "instagram": instagram, "google": google, "comment": comment, "snapchat": snapchat, "groupchat": groupchat, "facebook": facebook, "tweet": tweet, "pastel": pastel}[s["type"]](s)
        p = os.path.join(out_dir, s["out"]); img.convert("RGB").save(p); outs.append(p)
    print(json.dumps({"screens": outs}))

if __name__ == "__main__":
    main()
