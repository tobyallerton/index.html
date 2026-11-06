#!/usr/bin/env python3
"""Draw phone-screenshot slides (1080x1920) for formats built on a screenshot:
text-message chats and email threads. Drawing them is better than asking an image model:
the words come out exactly as written and stay sharp.

Usage: python screens.py spec.json
spec.json:
{
  "out_dir": "_build/raw",
  "screens": [
    {"type": "chat", "out": "slide-2.png", "time": "09:14", "contact": "Jake", "unread": 12,
     "messages": [{"from": "them", "text": "ok random question"}, {"from": "me", "text": "go on"}],
     "read": "Read 09:14"},
    {"type": "email", "out": "slide-1.png", "subject": "Secret Santa budget", "reply": false,
     "sender": "Linda Shaw", "initials": "LS", "colour": "#7b2d3b", "to": "Family Secret Santa",
     "date": "4 Dec, 18:02", "body": ["Megan,", "The limit was £10.", "Linda"]}
  ]
}
Names must be invented: never a real person's name or a real creator's handle.
Emoji aren't drawn (the fonts can't colour them), so leave them out of on-screen messages.
"""
import json, os, re, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT_DIRS = ["/usr/share/fonts/opentype/inter/", "/Library/Fonts/", "C:/Windows/Fonts/"]
EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]")

def font(weight, size):
    names = {"regular": ["Inter-Regular.otf", "arial.ttf", "Arial.ttf"],
             "medium": ["Inter-Medium.otf", "arial.ttf", "Arial.ttf"],
             "semibold": ["Inter-SemiBold.otf", "arialbd.ttf", "Arial Bold.ttf"],
             "bold": ["Inter-Bold.otf", "arialbd.ttf", "Arial Bold.ttf"]}[weight]
    for d in FONT_DIRS:
        for n in names:
            if os.path.exists(d + n):
                return ImageFont.truetype(d + n, size)
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)

def wrap(d, text, f, max_w):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= max_w: cur = t
            else:
                if cur: lines.append(cur)
                cur = w
        lines.append(cur)
    return lines

def status_bar(d, time, fg):
    d.text((90, 52), time, font=font("semibold", 40), fill=fg)
    x = W - 90  # battery
    d.rounded_rectangle([x - 66, 58, x, 90], radius=8, outline=fg, width=3)
    d.rectangle([x - 60, 64, x - 18, 84], fill=fg)
    d.rectangle([x + 3, 68, x + 7, 80], fill=fg)
    for i, h in enumerate([10, 16, 22, 28]):  # signal
        d.rectangle([x - 190 + i * 14, 90 - h, x - 181 + i * 14, 90], fill=fg)
    cx, cy = x - 104, 92  # wifi
    for r in (30, 20, 10):
        d.arc([cx - r, cy - r, cx + r, cy + r], 225, 315, fill=fg, width=5)

def chat(s):
    bg, fg = (0, 0, 0), (255, 255, 255)
    img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img)
    status_bar(d, s.get("time", "21:47"), fg)
    d.rectangle([0, 120, W, 330], fill=(22, 22, 24))
    blue = (10, 132, 255)
    d.line([(60, 205), (38, 228), (60, 251)], fill=blue, width=7, joint="curve")
    if s.get("unread"):
        t = str(s["unread"]); f = font("semibold", 30); tw = d.textlength(t, font=f)
        d.rounded_rectangle([80, 205, 80 + tw + 36, 251], radius=23, fill=blue)
        d.text((98, 210), t, font=f, fill=fg)
    name = s.get("contact", "Sam")
    d.ellipse([W / 2 - 52, 140, W / 2 + 52, 244], fill=(110, 110, 118))
    d.text((W / 2, 192), name[:1].upper(), font=font("medium", 54), fill=fg, anchor="mm")
    d.text((W / 2, 285), name + "  ›", font=font("regular", 30), fill=(200, 200, 205), anchor="mm")
    d.rounded_rectangle([W - 120, 196, W - 64, 232], radius=8, outline=blue, width=5)  # video icon
    d.polygon([(W - 64, 214), (W - 40, 200), (W - 40, 228)], fill=blue)
    f = font("regular", 40); y = 380; max_w = 640
    prev = None
    for m in s["messages"]:
        text = EMOJI.sub("", m["text"]).strip()
        mine = m.get("from") == "me"
        lines = wrap(d, text, f, max_w)
        tw = max(d.textlength(l, font=f) for l in lines)
        lh = 52; bh = len(lines) * lh + 34; bw = tw + 56
        y += 14 if prev == mine else 30
        x0 = W - 40 - bw if mine else 40
        d.rounded_rectangle([x0, y, x0 + bw, y + bh], radius=40, fill=blue if mine else (38, 38, 40))
        for i, l in enumerate(lines):
            d.text((x0 + 28, y + 14 + i * lh), l, font=f, fill=fg)
        y += bh; prev = mine
    if s.get("read"):
        d.text((W - 44, y + 14), s["read"], font=font("medium", 28), fill=(140, 140, 146), anchor="ra")
    d.rounded_rectangle([40, H - 150, W - 40, H - 70], radius=40, outline=(60, 60, 64), width=3)
    d.text((80, H - 110), "iMessage", font=font("regular", 36), fill=(100, 100, 106), anchor="lm")
    return img

def email(s):
    bg, fg, sub = (17, 17, 19), (242, 242, 244), (150, 150, 158)
    img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img)
    status_bar(d, s.get("time", "18:04"), fg)
    d.line([(68, 160), (48, 180), (68, 200)], fill=fg, width=6)
    subj = ("RE: " if s.get("reply") else "") + s["subject"]
    y = 250
    for l in wrap(d, subj, font("bold", 56), W - 120):
        d.text((56, y), l, font=font("bold", 56), fill=fg); y += 70
    y += 10
    d.rounded_rectangle([56, y, 56 + 110, y + 48], radius=10, fill=(44, 44, 48))
    d.text((56 + 55, y + 24), "Inbox", font=font("medium", 28), fill=sub, anchor="mm")
    y += 90
    d.ellipse([56, y, 56 + 96, y + 96], fill=s.get("colour", "#5b3a8c"))
    d.text((104, y + 48), s.get("initials", s["sender"][:2].upper()), font=font("semibold", 38), fill=fg, anchor="mm")
    d.text((180, y + 6), s["sender"], font=font("semibold", 42), fill=fg)
    d.text((W - 56, y + 12), s.get("date", ""), font=font("regular", 30), fill=sub, anchor="ra")
    d.text((180, y + 58), "To: " + s.get("to", "All") + "  ⌄", font=font("regular", 32), fill=sub)
    d.text((W - 60, y + 66), "•••", font=font("bold", 30), fill=sub, anchor="ra")
    y += 160
    f = font("regular", 40)
    for para in s["body"]:
        for l in wrap(d, EMOJI.sub("", para), f, W - 112):
            d.text((56, y), l, font=f, fill=(228, 228, 232)); y += 56
        y += 34
    y += 30
    bw = (W - 112 - 40) / 3
    for i, label in enumerate(["Reply", "Reply all", "Forward"]):
        x0 = 56 + i * (bw + 20)
        d.rounded_rectangle([x0, y, x0 + bw, y + 92], radius=16, fill=(32, 32, 36))
        d.text((x0 + bw / 2, y + 46), label, font=font("medium", 32), fill=fg, anchor="mm")
    return img

def main():
    spec_path = os.path.abspath(sys.argv[1])
    spec = json.load(open(spec_path, encoding="utf-8"))
    out_dir = os.path.join(os.path.dirname(spec_path), spec.get("out_dir", "."))
    os.makedirs(out_dir, exist_ok=True)
    outs = []
    for s in spec["screens"]:
        img = {"chat": chat, "email": email}[s["type"]](s)
        p = os.path.join(out_dir, s["out"]); img.save(p); outs.append(p)
    print(json.dumps({"screens": outs}))

if __name__ == "__main__":
    main()
