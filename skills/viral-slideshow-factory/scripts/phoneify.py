#!/usr/bin/env python3
"""Make an AI image look like an ordinary phone photo: a bit soft, a bit noisy, compressed, flatter colours.

Usage: python phoneify.py in.png out.png [--strength 1.0] [--seed 1]
make_slides.py runs this on every photo slide automatically (screenshots are left alone).
"""
import argparse, io, random
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

def phoneify(img, strength=1.0, seed=None):
    rnd = random.Random(seed)
    img = img.convert("RGB")
    w, h = img.size
    # Phone sensors and in-app compression lose fine detail: down-sample then up-sample.
    f = 0.62 - 0.08 * (strength - 1)
    img = img.resize((max(1, int(w * f)), max(1, int(h * f))), Image.BILINEAR).resize((w, h), Image.BICUBIC)
    img = img.filter(ImageFilter.GaussianBlur(0.45 * strength))
    # AI images are too saturated and contrasty; phone shots in normal rooms are flatter.
    img = ImageEnhance.Color(img).enhance(1 - 0.10 * strength)
    img = ImageEnhance.Contrast(img).enhance(1 - 0.07 * strength)
    a = np.asarray(img).astype(np.float32)
    # Slight white-balance drift (warm or cool), and lifted blacks.
    shift = rnd.choice([(6, 2, -6), (-4, 0, 6), (3, 2, -2)])
    a += np.array(shift, dtype=np.float32) * strength
    a = a * (1 - 0.04 * strength) + 10 * strength
    # Sensor noise, stronger in the shadows like a real phone in indoor light.
    luma = a.mean(axis=2, keepdims=True) / 255.0
    rng = np.random.default_rng(rnd.randint(0, 10**6))
    noise = rng.normal(0, 1, a.shape[:2] + (1,)).astype(np.float32)
    a += noise * (3.0 + 6.0 * (1 - luma)) * strength
    # Gentle vignette from a small lens.
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a *= (1 - 0.10 * strength * np.clip(r - 0.5, 0, 1))[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    # JPEG round-trip, as every phone photo has been through.
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=int(78 - 6 * (strength - 1))); buf.seek(0)
    return Image.open(buf).convert("RGB")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--strength", type=float, default=1.0); ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()
    phoneify(Image.open(a.inp), a.strength, a.seed).save(a.out, quality=95)
