#!/usr/bin/env python3
"""Build the finished slides (with text) for one slideshow from its slides.json, plus a preview sheet.

slides.json (in the slideshow folder):
{
  "style": "outline",              # or "box"
  "slides": [
    {"image": "_raw/slide-1.png", "text": "POV: your skin finally behaves", "position": "top", "size": 68},
    {"image": "_raw/slide-2.png", "text": "it took 2 weeks to notice", "position": "top"}
  ]
}
Every slide must have text. The script stops with an error if any text is missing, so a slide can't go out blank.

Usage: python make_slides.py <slideshow-folder>
Writes <folder>/slide-1.png ... and <folder>/preview.png (all slides side by side).
"""
import json, os, subprocess, sys
from PIL import Image

def main():
    folder = os.path.abspath(sys.argv[1])
    spec = json.load(open(os.path.join(folder, "slides.json")))
    slides = spec["slides"]
    missing = [i + 1 for i, s in enumerate(slides) if not str(s.get("text", "")).strip()]
    if missing:
        sys.exit(f"ERROR: slides {missing} have no text. Every slide needs on-screen text.")
    overlay = os.path.join(os.path.dirname(os.path.abspath(__file__)), "overlay.py")
    outs = []
    for i, s in enumerate(slides, 1):
        src = os.path.join(folder, s["image"])
        if not os.path.exists(src):
            sys.exit(f"ERROR: slide {i} image not found: {src}")
        out = os.path.join(folder, f"slide-{i}.png")
        cmd = [sys.executable, overlay, "--in", src, "--out", out, "--text", s["text"],
               "--position", s.get("position", "top"), "--style", s.get("style", spec.get("style", "outline")),
               "--size", str(s.get("size", 72)), "--fit", s.get("fit", "crop")]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        outs.append(out)
    thumbs = [Image.open(p).resize((360, 640)) for p in outs]
    sheet = Image.new("RGB", (360 * len(thumbs) + 10 * (len(thumbs) - 1), 640), "white")
    for i, t in enumerate(thumbs):
        sheet.paste(t, (i * 370, 0))
    sheet.save(os.path.join(folder, "preview.png"))
    print(json.dumps({"slides": outs, "preview": os.path.join(folder, "preview.png")}))

if __name__ == "__main__":
    main()
