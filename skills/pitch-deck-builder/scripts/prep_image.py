#!/usr/bin/env python3
"""Fit an AI-generated image to a slide: crop to the aspect, resize, add a scrim, check contrast.

Image models return fixed sizes (often 1536x1024, which is 3:2, not 16:9). This script makes
any image ready for deck_kit:

  background (full slide, 16:9, 2560x1440):
    python prep_image.py gen.png --out build/bg/bg-hero.jpg --scrim center
  illustration (a box on the slide, e.g. 5 x 4.2 inches):
    python prep_image.py gen.png --out build/img/bridge.png --aspect 5:4.2 --width 1500

--scrim darkens where text will sit, so light text stays readable on any picture:
  none | full | left | right | bottom | center
--focus picks what to keep when cropping: center (default) | left | right | top | bottom
Then it measures the text zone and prints PASS or WARN for light-text contrast.

Naming a background bg-hero.jpg / bg-dark-a.jpg / bg-light-a.jpg ... in one folder lets
Theme(backgrounds_dir=...) use it automatically; or pass any file to Deck.set_background().
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageStat


def parse_aspect(s):
    a, b = s.split(":")
    return float(a) / float(b)


def crop_to(img, aspect, focus):
    w, h = img.size
    if w / h > aspect:  # too wide: trim the sides
        nw = int(h * aspect)
        x = {"left": 0, "right": w - nw}.get(focus, (w - nw) // 2)
        return img.crop((x, 0, x + nw, h))
    nh = int(w / aspect)  # too tall: trim top/bottom
    y = {"top": 0, "bottom": h - nh}.get(focus, (h - nh) // 2)
    return img.crop((0, y, w, y + nh))


def zone(size, where):
    w, h = size
    return {
        "left": (0, 0, int(w * 0.6), h),
        "right": (int(w * 0.4), 0, w, h),
        "bottom": (0, int(h * 0.55), w, h),
        "center": (int(w * 0.15), int(h * 0.2), int(w * 0.85), int(h * 0.8)),
        "full": (0, 0, w, h),
    }.get(where)


def scrim(img, where, strength, color):
    """Soft dark gradient over the text zone (not a hard box)."""
    if where == "none":
        return img
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    a = int(255 * strength)
    if where == "full":
        mask = Image.new("L", (w, h), a)
    elif where in ("left", "right"):
        for x in range(w):
            t = x / w if where == "right" else 1 - x / w
            d.line([(x, 0), (x, h)], fill=int(a * min(1.0, max(0.0, (t - 0.25) / 0.5))))
    elif where == "bottom":
        for y in range(h):
            t = y / h
            d.line([(0, y), (w, y)], fill=int(a * min(1.0, max(0.0, (t - 0.35) / 0.45))))
    elif where == "center":
        d.ellipse([w * 0.05, h * 0.05, w * 0.95, h * 0.95], fill=a)
        mask = mask.filter(ImageFilter.GaussianBlur(min(w, h) * 0.18))
    layer = Image.new("RGB", (w, h), color)
    return Image.composite(layer, img, mask)


def luminance(img, box):
    """Mean relative luminance (0-1) of the text zone."""
    region = img.crop(box).convert("RGB").resize((64, 64))
    r, g, b = [c / 255 for c in ImageStat.Stat(region).mean]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("--out", required=True)
    ap.add_argument("--aspect", default="16:9", help="W:H, e.g. 16:9 or 5:4.2 (inches)")
    ap.add_argument("--width", type=int, default=2560, help="output width in px")
    ap.add_argument("--focus", default="center", choices=["center", "left", "right", "top", "bottom"])
    ap.add_argument("--scrim", default="none", choices=["none", "full", "left", "right", "bottom", "center"])
    ap.add_argument("--strength", type=float, default=0.6, help="scrim darkness 0-1")
    ap.add_argument("--scrim-color", default="0A1221", help="hex, usually the theme's ink colour")
    ap.add_argument("--text", default="light", choices=["light", "dark"],
                    help="colour of the text that will sit on it (for the contrast check)")
    a = ap.parse_args()

    if not os.path.exists(a.src):
        sys.exit(f"error: no such file: {a.src}")
    img = Image.open(a.src)
    alpha = img.mode in ("RGBA", "LA") and a.out.lower().endswith(".png")
    img = img.convert("RGBA" if alpha else "RGB")

    ratio = parse_aspect(a.aspect)
    img = crop_to(img, ratio, a.focus)
    img = img.resize((a.width, int(round(a.width / ratio))), Image.LANCZOS)
    c = a.scrim_color.lstrip("#")
    if not alpha:
        img = scrim(img, a.scrim, a.strength, tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)))

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    if a.out.lower().endswith((".jpg", ".jpeg")):
        img.convert("RGB").save(a.out, quality=88, optimize=True)
    else:
        img.save(a.out)

    if a.scrim == "none" and abs(ratio - 16 / 9) > 0.01:
        print(f"saved {a.out} ({img.size[0]}x{img.size[1]}); illustration, no text on it, contrast not checked")
        return
    box = zone(img.size, a.scrim if a.scrim != "none" else "center")
    lum = luminance(img, box)
    ok = lum < 0.35 if a.text == "light" else lum > 0.6
    print(f"saved {a.out} ({img.size[0]}x{img.size[1]}); text-zone luminance {lum:.2f} "
          f"-> {'PASS' if ok else 'WARN'} for {a.text} text"
          + ("" if ok else "; raise --strength, change --scrim, or pick another image"))


if __name__ == "__main__":
    main()
