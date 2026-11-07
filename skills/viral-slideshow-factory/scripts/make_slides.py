#!/usr/bin/env python3
"""Build the finished slides (with text) for one slideshow from its slides.json, plus a preview sheet.

slides.json (in the slideshow folder):
{
  "style": "classic",              # classic (viral default: Figtree, soft shadow, no outline), box, outline or plain
  "color": "white",                # classic text colour: white, yellow (TikTok yellow) or cream
  "slides": [
    {"image": "_raw/slide-1.png", "text": "POV: your skin finally behaves", "position": "top", "size": 68},
    {"image": "_raw/slide-2.png", "text": "it took 2 weeks to notice", "position": "top"},
    {"image": "_raw/slide-3.png", "labels": [{"text": "My Mum", "x": 0.3, "y": 0.5}, {"text": "Me", "x": 0.7, "y": 0.45}]}
  ]
}
Every slide must have text, meme "labels", or "no_text": true (only for screenshot hooks, whose text is the screenshot itself). The script stops with an error if any text is missing, so a slide can't go out blank.

Usage: python make_slides.py <slideshow-folder>
Writes <folder>/slide-1.png ... and <folder>/preview.png (all slides side by side).
"""
import json, os, subprocess, sys
from PIL import Image

def draw_labels(path, labels):
    """Meme-style labels placed on the picture: [{"text": "My Mum", "x": 0.25, "y": 0.55, "size": 64}], x/y as 0-1 of the slide."""
    from PIL import ImageDraw
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from overlay import font as load_font, EMOJI
    img = Image.open(path).convert("RGB"); d = ImageDraw.Draw(img)
    for l in labels:
        size = int(l.get("size", 64)); f = load_font(None, size)
        t = EMOJI.sub("", l["text"]).strip()
        d.text((l["x"] * img.width, l["y"] * img.height), t, font=f, fill="white", anchor="mm",
               stroke_width=max(3, size // 12), stroke_fill="black")
    img.save(path, quality=95)

def main():
    folder = os.path.abspath(sys.argv[1])
    spec = json.load(open(os.path.join(folder, "slides.json")))
    slides = spec["slides"]
    missing = [i + 1 for i, s in enumerate(slides) if not str(s.get("text", "")).strip() and not s.get("labels") and not s.get("no_text")]
    if missing:
        sys.exit(f"ERROR: slides {missing} have no text. Every slide needs on-screen text.")
    overlay = os.path.join(os.path.dirname(os.path.abspath(__file__)), "overlay.py")
    outs = []
    for i, s in enumerate(slides, 1):
        src = os.path.join(folder, s["image"])
        if not os.path.exists(src):
            sys.exit(f"ERROR: slide {i} image not found: {src}")
        out = os.path.join(folder, f"slide-{i}.png")
        if not s.get("no_text") and s.get("phoneify", spec.get("phoneify", True)):
            # Photo slides get the phone-camera finish so they don't look like glossy AI renders.
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from phoneify import phoneify
            tmp = os.path.join(folder, f".phone-{i}.png")
            phoneify(Image.open(src), s.get("phone_strength", 0.85), seed=i).save(tmp)
            src = tmp
        cmd = [sys.executable, overlay, "--in", src, "--out", out, "--text", s.get("text", ""),
               "--position", s.get("position", "top"), "--style", s.get("style", spec.get("style", "classic")),
               "--color", s.get("color", spec.get("color", "white")), "--width", str(s.get("width", spec.get("width", 0.62))),
               "--size", str(s.get("size", 60)), "--fit", s.get("fit", "crop")] + (["--y", str(s["y"])] if s.get("y") is not None else [])
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        if s.get("labels"):
            draw_labels(out, s["labels"])
        outs.append(out)
    thumbs = [Image.open(p).resize((360, 640)) for p in outs]
    sheet = Image.new("RGB", (360 * len(thumbs) + 10 * (len(thumbs) - 1), 640), "white")
    for i, t in enumerate(thumbs):
        sheet.paste(t, (i * 370, 0))
    sheet.save(os.path.join(folder, "preview.png"))
    print(json.dumps({"slides": outs, "preview": os.path.join(folder, "preview.png")}))

if __name__ == "__main__":
    main()
