#!/usr/bin/env python3
"""Tile slide-*.png into one contact sheet with slide numbers.

Usage: python contact_sheet.py <png_dir> <out.png> [--cols 4]
"""
import argparse
import glob
import os
import re

from PIL import Image, ImageDraw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("png_dir")
    ap.add_argument("out")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--thumb", type=int, default=480, help="thumbnail width in px")
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(a.png_dir, "slide-*.png")),
                   key=lambda p: int(re.findall(r"(\d+)", os.path.basename(p))[-1]))
    if not files:
        raise SystemExit(f"error: no slide-*.png in {a.png_dir}")
    first = Image.open(files[0])
    tw = a.thumb
    th = int(first.height * tw / first.width)
    pad, label = 16, 26
    rows = (len(files) + a.cols - 1) // a.cols
    sheet = Image.new("RGB", (a.cols * (tw + pad) + pad, rows * (th + pad + label) + pad), (40, 44, 52))
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        r, c = divmod(i, a.cols)
        x, y = pad + c * (tw + pad), pad + r * (th + pad + label)
        sheet.paste(Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS), (x, y + label))
        d.text((x, y + 6), f"{i + 1:02d}", fill=(230, 230, 230))
    sheet.save(a.out)
    print(f"contact sheet: {a.out} ({len(files)} slides)")


if __name__ == "__main__":
    main()
