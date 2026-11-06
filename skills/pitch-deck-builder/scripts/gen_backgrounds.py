#!/usr/bin/env python3
"""Paint slide backgrounds with code (no image model needed).

Each image = diagonal gradient + soft colour glows + faint dot grid + film grain,
so slides look designed rather than flat. Output (16:9, 2560x1440 JPEG):
    bg-dark-a.jpg bg-dark-b.jpg bg-dark-c.jpg bg-hero.jpg bg-light-a.jpg bg-light-b.jpg
deck_kit.Theme(backgrounds_dir=OUT) picks them up.

Usage:
    python gen_backgrounds.py --out build/bg
    python gen_backgrounds.py --out build/bg --ink 0C1626 --accent F7A81E --glow 3C78F0
"""
import argparse
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter

W, H = 2560, 1440


def hex3(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def lighten(c, k):
    return tuple(min(255, int(v + (255 - v) * k)) for v in c)


def gradient(c1, c2):
    """Diagonal gradient, painted small and scaled up (fast, smooth)."""
    sw, sh = 64, 36
    small = Image.new("RGB", (sw, sh))
    px = small.load()
    for y in range(sh):
        for x in range(sw):
            t = (x / (sw - 1)) * 0.55 + (y / (sh - 1)) * 0.45
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    return small.resize((W, H), Image.BICUBIC)


def glow(img, cx, cy, r, color, strength, light=False):
    if light:
        layer = Image.new("RGB", (W, H), (255, 255, 255))
        tint = tuple(int(255 + (color[i] - 255) * strength) for i in range(3))
        ImageDraw.Draw(layer).ellipse([cx - r, cy - r, cx + r, cy + r], fill=tint)
        return ImageChops.multiply(img, layer.filter(ImageFilter.GaussianBlur(r * 0.55)))
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(layer).ellipse([cx - r, cy - r, cx + r, cy + r],
                                  fill=tuple(int(v * strength) for v in color))
    return ImageChops.add(img, layer.filter(ImageFilter.GaussianBlur(r * 0.55)))


def dots(img, color, alpha, fade, step=48, size=2):
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    fx, fy, fr = fade
    for y in range(step // 2, H, step):
        for x in range(step // 2, W, step):
            a = int(alpha * max(0.0, 1 - ((x - fx) ** 2 + (y - fy) ** 2) ** 0.5 / fr))
            if a > 0:
                d.ellipse([x - size, y - size, x + size, y + size], fill=color + (a,))
    return Image.alpha_composite(img.convert("RGBA"), over).convert("RGB")


def arcs(img, cx, cy, radii, color, alpha, width=2):
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    for i, r in enumerate(radii):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color + (int(alpha * (1 - i / (len(radii) + 1))),),
                  width=width)
    return Image.alpha_composite(img.convert("RGBA"), over).convert("RGB")


def grain(img, amount):
    noise = Image.effect_noise((W, H), 40).convert("RGB")
    return Image.blend(img, ImageChops.overlay(img, noise), amount)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="output folder")
    ap.add_argument("--ink", default="0A1221", help="dark base colour (hex)")
    ap.add_argument("--paper", default="F8FAFD", help="light base colour (hex)")
    ap.add_argument("--glow", default="3C78F0", help="glow colour, a shade that sits behind the accent")
    ap.add_argument("--accent", default="F7A81E", help="accent colour for the hero arcs")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    ink, paper, gl, ac = hex3(a.ink), hex3(a.paper), hex3(a.glow), hex3(a.accent)
    ink2, paper2 = lighten(ink, 0.06), tuple(int(v * 0.94) for v in paper)
    grid_d, grid_l = (150, 175, 215), (90, 110, 150)

    def dark(name, glows, fade, arc=None):
        img = gradient(ink, ink2)
        for g in glows:
            img = glow(img, *g)
        img = dots(img, grid_d, 70, fade)
        if arc:
            img = arcs(img, *arc)
        grain(img, 0.06).save(os.path.join(a.out, f"bg-{name}.jpg"), quality=88, optimize=True)

    def light(name, glows, fade):
        img = gradient(paper, paper2)
        for g in glows:
            img = glow(img, *g, light=True)
        img = dots(img, grid_l, 45, fade)
        grain(img, 0.035).save(os.path.join(a.out, f"bg-{name}.jpg"), quality=88, optimize=True)

    # glow positions differ so consecutive slides don't repeat
    dark("dark-a", [(2250, 120, 700, gl, 0.38)], (2200, 200, 1100))
    dark("dark-b", [(250, 150, 650, gl, 0.32), (2300, 1350, 650, gl, 0.16)], (350, 250, 1000))
    dark("dark-c", [(1280, 1550, 900, gl, 0.28)], (1280, 1300, 1200))
    dark("hero", [(1280, 700, 820, gl, 0.34), (2400, 1350, 600, gl, 0.18)], (1280, 640, 1300),
         arc=(1280, 640, [380, 520, 680, 860], ac, 90, 2))
    light("light-a", [(2300, 100, 650, gl, 0.10), (200, 1350, 600, ac, 0.10)], (2200, 200, 1100))
    light("light-b", [(250, 150, 600, ac, 0.09), (2350, 1300, 650, gl, 0.10)], (300, 250, 1000))
    print("ok:", ", ".join(sorted(f for f in os.listdir(a.out) if f.startswith("bg-"))))


if __name__ == "__main__":
    main()
