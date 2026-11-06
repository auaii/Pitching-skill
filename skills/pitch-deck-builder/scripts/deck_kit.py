#!/usr/bin/env python3
"""deck_kit: helpers for building editable 16:9 pitch decks with python-pptx.

Import it from your own build script:

    import sys; sys.path.insert(0, "<skill-dir>/scripts")
    from deck_kit import Deck, Theme

    deck = Deck(Theme(product="Acme Helpdesk", accent="F7A81E"))
    s = deck.question("You use AI every day.", "But does it know your business?")
    deck.notes(s, talk="Pause. Let them answer.", ask="Who here used AI today?",
               time=1, part="problem", next="So what do you already use?")
    deck.save("deck.pptx")

Every layout helper draws the common frame (kicker, logo, product name, page
number) and returns the slide, so you add speaker notes right after it.
AI-generated pictures: prepare them with prep_image.py, then use Deck.set_background()
or Deck.image() (references/image-generation.md).
Cards are named "card" so scripts/audit.py can count sub-points per slide.
All text stays real, editable text. Backgrounds are images only when
Theme.backgrounds_dir points at the output of scripts/gen_backgrounds.py.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt


def rgb(hex_str: str) -> RGBColor:
    h = hex_str.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"colour must be 6 hex digits, got {hex_str!r}")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def set_script_fonts(run, face: str):
    """Set the East-Asian and complex-script font slots too, not only Latin.

    python-pptx's font.name writes <a:latin> only. Thai (and Arabic, Hindi...) is drawn
    from <a:cs>, so without this the text falls back to a font with no Thai letters and
    can render as blank boxes or nothing at all.
    """
    rPr = run._r.get_or_add_rPr()
    latin = rPr.find(qn("a:latin"))
    anchor = latin
    for tag in ("a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {})
            if anchor is not None:
                anchor.addnext(el)
            else:
                rPr.append(el)
        el.set("typeface", face)
        anchor = el


@dataclass
class Theme:
    """Three colours (background, text, one accent) and two fonts: the 1-2-3-4 rule.

    For a Thai-language deck use a font with Thai glyphs that ships on Mac and
    Windows, e.g. font_title="Tahoma", font_body="Tahoma" (see references/design-rules.md).
    """
    product: str = "Product name"
    ink: str = "0C1626"          # dark background
    ink_card: str = "1A2C47"     # card fill on dark (shade of ink, same colour family)
    ink_line: str = "243857"     # card border on dark
    paper: str = "F6F8FC"        # light background
    paper_line: str = "D8E1EE"   # card border on light
    text_dark: str = "0E1826"
    text_light: str = "EFF4FB"
    muted_dark: str = "55667D"
    muted_light: str = "93A4BE"
    accent: str = "F7A81E"
    font_title: str = "Georgia"
    font_body: str = "Calibri"
    logo_on_dark: Optional[str] = None    # path to a white/light logo PNG
    logo_on_light: Optional[str] = None   # path to a colour logo PNG
    backgrounds_dir: Optional[str] = None  # folder with bg-dark-*.jpg / bg-light-*.jpg / bg-hero.jpg


class Deck:
    W = Inches(13.333)
    H = Inches(7.5)
    MARGIN = Inches(0.95)

    def __init__(self, theme: Optional[Theme] = None):
        self.t = theme or Theme()
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = self.W, self.H
        self._blank = self.prs.slide_layouts[6]
        self._page = 0
        self._dark_cycle = 0

    # ------------------------------------------------------------------ primitives
    def _shape(self, slide, kind, x, y, w, h):
        sp = slide.shapes.add_shape(kind, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
        sp.shadow.inherit = False
        return sp

    def fill(self, sp, hex_color: str, opacity: Optional[float] = None):
        sp.fill.solid()
        sp.fill.fore_color.rgb = rgb(hex_color)
        sp.line.fill.background()
        if opacity is not None:
            clr = sp.fill._xPr.find(qn("a:solidFill"))[0]
            clr.append(clr.makeelement(qn("a:alpha"), {"val": str(int(opacity * 100000))}))
        return sp

    def rect(self, slide, x, y, w, h, color, opacity=None):
        return self.fill(self._shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h), color, opacity)

    def rrect(self, slide, x, y, w, h, color, radius=0.08, opacity=None):
        sp = self._shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        sp.adjustments[0] = radius
        return self.fill(sp, color, opacity)

    def oval(self, slide, x, y, w, h, color):
        return self.fill(self._shape(slide, MSO_SHAPE.OVAL, x, y, w, h), color)

    def line(self, slide, x1, y1, x2, y2, color, width=1.5):
        cn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Emu(int(x1)), Emu(int(y1)),
                                        Emu(int(x2)), Emu(int(y2)))
        cn.line.color.rgb = rgb(color)
        cn.line.width = Pt(width)
        return cn

    def text(self, slide, x, y, w, h, text, size, color, bold=False, title=False,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, tracking=None, spacing=1.0):
        """One text box. `text` may contain '\n' for several paragraphs of the same style."""
        box = slide.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        for i, chunk in enumerate(text.split("\n")):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            p.line_spacing = spacing
            p.space_after = Pt(6)
            self.run(p, chunk, size, color, bold=bold, title=title, tracking=tracking)
        return tf

    def run(self, p, text, size, color, bold=False, title=False, tracking=None):
        r = p.add_run()
        r.text = text
        f = r.font
        f.size, f.bold = Pt(size), bold
        face = self.t.font_title if title else self.t.font_body
        f.name = face
        f.color.rgb = rgb(color)
        set_script_fonts(r, face)
        if tracking is not None:
            r._r.get_or_add_rPr().set("spc", str(int(tracking * 100)))
        return r

    def card(self, slide, x, y, w, h, dark=True):
        """Glass card. Named 'card' so audit.py can count sub-points."""
        if dark:
            sp = self.rrect(slide, x, y, w, h, self.t.ink_card, opacity=0.78)
            sp.line.color.rgb = rgb(self.t.ink_line)
        else:
            sp = self.rrect(slide, x, y, w, h, "FFFFFF", opacity=0.97)
            sp.line.color.rgb = rgb(self.t.paper_line)
        sp.line.width = Pt(0.75)
        sp.name = "card"
        return sp

    # ------------------------------------------------------------------ icons
    def icon(self, slide, key: str, cx, cy, s, color: Optional[str] = None, hole: Optional[str] = None):
        """Drawn vector icon centred on (cx, cy), nominal size s (EMU).

        Keys: blocks (build / easy), shield (safe / control), cloud (scale / ready),
        clock (speed / time), chart (growth / results), number:N (a numbered disc).
        """
        c = color or self.t.accent
        h = hole or self.t.ink_card
        if key == "blocks":
            g, b = 0.04 * s, 0.28 * s
            ox, oy = cx - 0.3 * s, cy - 0.3 * s
            for i in range(2):
                for j in range(2):
                    r = self.rrect(slide, ox + j * (b + g), oy + i * (b + g), b, b, c, radius=0.25)
                    if i == 1 and j == 1:
                        self.fill(r, h)
                        r.line.color.rgb, r.line.width = rgb(c), Pt(1.5)
        elif key == "shield":
            sh = self.fill(self._shape(slide, MSO_SHAPE.REGULAR_PENTAGON,
                                       cx - 0.4 * s, cy - 0.42 * s, 0.8 * s, 0.8 * s), c)
            sh.rotation = 180
            self.oval(slide, cx - 0.1 * s, cy - 0.16 * s, 0.2 * s, 0.2 * s, h)
        elif key == "cloud":
            self.oval(slide, cx - 0.42 * s, cy - 0.05 * s, 0.34 * s, 0.34 * s, c)
            self.oval(slide, cx - 0.18 * s, cy - 0.22 * s, 0.42 * s, 0.42 * s, c)
            self.oval(slide, cx + 0.12 * s, cy - 0.05 * s, 0.32 * s, 0.32 * s, c)
            self.rect(slide, cx - 0.4 * s, cy + 0.12 * s, 0.8 * s, 0.14 * s, c)
        elif key == "clock":
            self.oval(slide, cx - 0.38 * s, cy - 0.38 * s, 0.76 * s, 0.76 * s, c)
            self.oval(slide, cx - 0.29 * s, cy - 0.29 * s, 0.58 * s, 0.58 * s, h)
            self.line(slide, cx, cy, cx, cy - 0.2 * s, c, 2.25)
            self.line(slide, cx, cy, cx + 0.15 * s, cy, c, 2.25)
        elif key == "chart":
            for k, hh in enumerate((0.25, 0.42, 0.62)):
                self.rect(slide, cx - 0.33 * s + k * 0.24 * s, cy + 0.32 * s - hh * s,
                          0.17 * s, hh * s, c)
        elif key.startswith("number:"):
            self.oval(slide, cx - 0.36 * s, cy - 0.36 * s, 0.72 * s, 0.72 * s, c)
            self.text(slide, cx - 0.36 * s, cy - 0.36 * s, 0.72 * s, 0.72 * s, key.split(":", 1)[1],
                      18, self.t.ink, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        else:
            raise ValueError(f"unknown icon {key!r}")

    def icon_disc(self, slide, key, x, y, d, dark=True):
        disc = self.t.ink if dark else self.t.ink_card
        self.oval(slide, x, y, d, d, disc)
        self.icon(slide, key, x + d / 2, y + d / 2, d * 0.8, hole=disc)

    # ------------------------------------------------------------------ canvas + frame
    def _bg_path(self, name):
        d = self.t.backgrounds_dir
        p = os.path.join(d, f"bg-{name}.jpg") if d else None
        return p if p and os.path.exists(p) else None

    def new_slide(self, dark=True, hero=False):
        """Blank slide with a painted background (image if available, else a flat fill)."""
        s = self.prs.slides.add_slide(self._blank)
        if hero:
            name = "hero"
        elif dark:
            name = "dark-" + "abc"[self._dark_cycle % 3]
            self._dark_cycle += 1
        else:
            name = "light-" + "ab"[self._page % 2]
        p = self._bg_path(name)
        if p:
            bg = s.shapes.add_picture(p, 0, 0, width=self.W, height=self.H)
        else:
            bg = self.rect(s, 0, 0, self.W, self.H, self.t.ink if (dark or hero) else self.t.paper)
        bg.name = "background"
        s._kit_dark = dark or hero  # remembered for frame()
        return s

    def set_background(self, slide, path: str):
        """Replace the slide's background with an image (e.g. one prepared with prep_image.py)."""
        tree = slide.shapes._spTree
        for old in [sh for sh in slide.shapes if sh.name == "background"]:
            tree.remove(old._element)
        pic = slide.shapes.add_picture(path, 0, 0, width=self.W, height=self.H)
        tree.remove(pic._element)
        tree.insert(2, pic._element)  # first after the required group properties = bottom of z-order
        pic.name = "background"
        return pic

    def image(self, slide, path: str, x, y, w, h, radius: Optional[float] = None):
        """Place an illustration in a box, cropped to fill it (no stretching).

        Text never goes inside generated images; put it beside them as real text.
        radius: optional rounded corners (0-0.5), drawn as a rounded-rectangle picture crop.
        """
        from PIL import Image as _Img
        with _Img.open(path) as im:
            iw, ih = im.size
        pic = slide.shapes.add_picture(path, Emu(int(x)), Emu(int(y)), width=Emu(int(w)), height=Emu(int(h)))
        box, img = w / h, iw / ih
        if img > box:   # image wider than the box: trim left/right
            t = (1 - box / img) / 2
            pic.crop_left = pic.crop_right = t
        elif img < box:  # taller: trim top/bottom
            t = (1 - img / box) / 2
            pic.crop_top = pic.crop_bottom = t
        if radius is not None:
            geom = pic._element.spPr.find(qn("a:prstGeom"))
            geom.set("prst", "roundRect")
            av = geom.find(qn("a:avLst"))
            if av is None:
                av = geom.makeelement(qn("a:avLst"), {})
                geom.append(av)
            av.append(av.makeelement(qn("a:gd"), {"name": "adj", "fmla": f"val {int(radius * 100000)}"}))
        pic.name = "illustration"
        return pic

    def kicker(self, slide, label: str, x=None, y=Inches(0.8)):
        x = self.MARGIN if x is None else x
        self.rect(slide, x, y - Inches(0.1), Inches(0.5), Inches(0.055), self.t.accent)
        # Letter-spacing splits Thai vowels and tone marks from their consonants: Latin only.
        thai = any("\u0e00" <= ch <= "\u0e7f" for ch in label)
        self.text(slide, x + Inches(0.66), y - Inches(0.19), Inches(9.5), Inches(0.5),
                  label.upper(), 13, self.t.accent, bold=True, tracking=None if thai else 2.2)

    def title(self, slide, text, y=Inches(1.15), size=40, w=None, align=PP_ALIGN.LEFT, x=None):
        c = self.t.text_light if slide._kit_dark else self.t.text_dark
        x = self.MARGIN if x is None else x
        w = (self.W - 2 * self.MARGIN) if w is None else w
        return self.text(slide, x, y, w, Inches(1.6), text, size, c, title=True, align=align)

    def frame(self, slide):
        """Logo top-right, product bottom-left, page number bottom-right. Drawn last, on top."""
        self._page += 1
        dark = slide._kit_dark
        muted = self.t.muted_light if dark else self.t.muted_dark
        logo = self.t.logo_on_dark if dark else self.t.logo_on_light
        if logo and os.path.exists(logo):
            lw = Inches(1.5)
            slide.shapes.add_picture(logo, self.W - lw - Inches(0.5), Inches(0.45), width=lw)
        self.text(slide, Inches(12.0), Inches(6.95), Inches(1.1), Inches(0.4),
                  f"{self._page:02d}", 11, muted, align=PP_ALIGN.RIGHT)
        thai = any("\u0e00" <= ch <= "\u0e7f" for ch in self.t.product)
        self.text(slide, self.MARGIN, Inches(6.95), Inches(6), Inches(0.4),
                  self.t.product, 10, muted, tracking=None if thai else 1.0)

    def source(self, slide, text):
        """Source line for any number on the slide (truth rule A4)."""
        c = self.t.muted_light if slide._kit_dark else self.t.muted_dark
        self.text(slide, self.MARGIN, Inches(6.55), Inches(11), Inches(0.35), "Source: " + text, 10, c)

    # ------------------------------------------------------------------ notes
    @staticmethod
    def notes(slide, talk: str, time: float, part: str, next: Optional[str] = None,
              ask: Optional[str] = None, step: Optional[int] = None):
        """Speaker notes in the convention audit.py reads (references/speaker-notes.md).

        part: problem | solution | summary.   time: minutes.   next: the hand-off line.
        """
        if part not in ("problem", "solution", "summary"):
            raise ValueError("part must be problem, solution or summary")
        lines = [f"TALK: {talk}"]
        if ask:
            lines.append(f"ASK: {ask}")
        lines.append(f"TIME: {time:g} min")
        lines.append(f"PART: {part}" + (f" | STEP: {step}" if step else ""))
        if next:
            lines.append(f"NEXT: {next}")
        slide.notes_slide.notes_text_frame.text = "\n".join(lines)

    # ------------------------------------------------------------------ layouts (Part C2)
    def question(self, line1: str, line2: str):
        """Opening question: hero background, one question on two lines, nothing else."""
        s = self.new_slide(hero=True)
        tf = self.text(s, Inches(1.2), Inches(2.4), self.W - Inches(2.4), Inches(1.2), line1, 46,
                       self.t.text_light, title=True, align=PP_ALIGN.CENTER)
        p = tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        self.run(p, line2, 46, self.t.accent, title=True)
        self.frame(s)
        return s

    def three_cards(self, kicker: str, title: str,
                    cards: Sequence[Tuple[str, str, str, str]], dark=False,
                    band: Optional[str] = None, source: Optional[str] = None):
        """Problem+impact or Benefits: up to 4 cards of (icon, heading, big word/figure, sentence)."""
        if not 1 <= len(cards) <= 4:
            raise ValueError("1-4 cards (1-2-3-4 rule)")
        s = self.new_slide(dark=dark)
        self.kicker(s, kicker)
        self.title(s, title)
        n = len(cards)
        gap = Inches(0.35)
        top = Inches(2.75)
        cw = (self.W - 2 * self.MARGIN - gap * (n - 1)) / n
        ch = Inches(2.75) if band else Inches(3.4)
        txt = self.t.text_light if dark else self.t.text_dark
        muted = self.t.muted_light if dark else self.t.muted_dark
        for i, (ic, head, big, sentence) in enumerate(cards):
            x = self.MARGIN + i * (cw + gap)
            self.card(s, x, top, cw, ch, dark=dark)
            self.icon_disc(s, ic, x + Inches(0.35), top + Inches(0.35), Inches(0.75), dark=True)
            self.text(s, x + Inches(1.25), top + Inches(0.42), cw - Inches(1.45), Inches(0.7),
                      head, 17, txt, bold=True)
            self.text(s, x + Inches(0.35), top + Inches(1.2), cw - Inches(0.7), Inches(0.8),
                      big, 32, self.t.accent, bold=True, title=True)
            self.text(s, x + Inches(0.35), top + Inches(1.9), cw - Inches(0.7), Inches(0.9),
                      sentence, 14, muted)
        if band:
            by = top + ch + Inches(0.3)
            self.rrect(s, self.MARGIN, by, self.W - 2 * self.MARGIN, Inches(0.7), self.t.ink, radius=0.2)
            self.text(s, self.MARGIN + Inches(0.4), by, self.W - 2 * self.MARGIN - Inches(0.8),
                      Inches(0.7), band, 17, self.t.text_light, anchor=MSO_ANCHOR.MIDDLE)
        if source:
            self.source(s, source)
        self.frame(s)
        return s

    def reveal(self, setup: str, product: str, tagline: str):
        """Reveal: hero background, setup line, INTRODUCING, product name, tagline."""
        s = self.new_slide(hero=True)
        mid_w = self.W - Inches(2.4)
        self.text(s, Inches(1.2), Inches(1.7), mid_w, Inches(0.6), setup, 20, self.t.muted_light,
                  align=PP_ALIGN.CENTER)
        self.text(s, Inches(1.2), Inches(2.55), mid_w, Inches(0.5), "INTRODUCING", 14, self.t.accent,
                  bold=True, align=PP_ALIGN.CENTER, tracking=4)
        self.text(s, Inches(1.2), Inches(3.05), mid_w, Inches(1.2), product, 54, self.t.text_light,
                  title=True, align=PP_ALIGN.CENTER)
        self.text(s, Inches(1.2), Inches(4.45), mid_w, Inches(0.8), tagline, 22, self.t.text_light,
                  align=PP_ALIGN.CENTER)
        self.frame(s)
        return s

    def recap(self, kicker: str, title: str, rows: Sequence[Tuple[str, str, str, str]]):
        """Recap table: one row per pain of (icon, question, cost, answer)."""
        if not 1 <= len(rows) <= 4:
            raise ValueError("1-4 rows (1-2-3-4 rule)")
        s = self.new_slide(dark=False)
        self.kicker(s, kicker)
        self.title(s, title)
        top, rh, gap = Inches(2.6), Inches(1.0), Inches(0.22)
        full = self.W - 2 * self.MARGIN
        for i, (ic, q, cost, ans) in enumerate(rows):
            y = top + i * (rh + gap)
            self.card(s, self.MARGIN, y, full, rh, dark=False)
            self.icon_disc(s, ic, self.MARGIN + Inches(0.2), y + Inches(0.15), Inches(0.7))
            self.text(s, self.MARGIN + Inches(1.1), y, Inches(3.6), rh, q, 17, self.t.text_dark,
                      bold=True, anchor=MSO_ANCHOR.MIDDLE)
            self.text(s, self.MARGIN + Inches(4.8), y, Inches(2.8), rh, cost, 14, self.t.muted_dark,
                      anchor=MSO_ANCHOR.MIDDLE)
            ax = self.MARGIN + Inches(7.75)
            self.line(s, ax, y + rh / 2, ax + Inches(0.5), y + rh / 2, self.t.accent, 2.5)
            self.text(s, self.MARGIN + Inches(8.45), y, full - Inches(8.6), rh, ans, 17,
                      self.t.text_dark, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        self.frame(s)
        return s

    def steps(self, kicker: str, title: str, steps: Sequence[Tuple[str, str]], band: Optional[str] = None):
        """Next steps: 3-4 numbered step cards of (heading, sentence) + a reassurance band."""
        if not 1 <= len(steps) <= 4:
            raise ValueError("1-4 steps (1-2-3-4 rule)")
        cards = [(f"number:{i + 1}", h, "", txt) for i, (h, txt) in enumerate(steps)]
        s = self.new_slide(dark=True)
        self.kicker(s, kicker)
        self.title(s, title)
        n, gap, top = len(cards), Inches(0.35), Inches(2.75)
        cw = (self.W - 2 * self.MARGIN - gap * (n - 1)) / n
        for i, (ic, head, _, sentence) in enumerate(cards):
            x = self.MARGIN + i * (cw + gap)
            self.card(s, x, top, cw, Inches(2.4))
            self.icon(s, ic, x + Inches(0.7), top + Inches(0.7), Inches(0.8))
            self.text(s, x + Inches(0.35), top + Inches(1.25), cw - Inches(0.7), Inches(0.5),
                      head, 18, self.t.text_light, bold=True)
            self.text(s, x + Inches(0.35), top + Inches(1.7), cw - Inches(0.7), Inches(0.7),
                      sentence, 14, self.t.muted_light)
        if band:
            by = top + Inches(2.75)
            self.rrect(s, self.MARGIN, by, self.W - 2 * self.MARGIN, Inches(0.7), self.t.accent, radius=0.2)
            self.text(s, self.MARGIN + Inches(0.4), by, self.W - 2 * self.MARGIN - Inches(0.8), Inches(0.7),
                      band, 17, self.t.ink, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        self.frame(s)
        return s

    def cta(self, title: str, callback: str, button: str, contact: str):
        """CTA, the last slide: closing title, call-back to the opening question, one button."""
        s = self.new_slide(hero=True)
        mid_w = self.W - Inches(2.4)
        self.text(s, Inches(1.2), Inches(1.9), mid_w, Inches(1.2), title, 44, self.t.text_light,
                  title=True, align=PP_ALIGN.CENTER)
        self.text(s, Inches(1.2), Inches(3.15), mid_w, Inches(0.8), callback, 20, self.t.muted_light,
                  align=PP_ALIGN.CENTER)
        bw, bh = Inches(4.2), Inches(0.85)
        bx = (self.W - bw) / 2
        self.rrect(s, bx, Inches(4.25), bw, bh, self.t.accent, radius=0.5)
        self.text(s, bx, Inches(4.25), bw, bh, button, 20, self.t.ink, bold=True,
                  align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        self.text(s, Inches(1.2), Inches(5.45), mid_w, Inches(0.5), contact, 14, self.t.muted_light,
                  align=PP_ALIGN.CENTER)
        self.frame(s)
        return s

    # ------------------------------------------------------------------ output
    def save(self, path: str):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self.prs.save(path)
        return path


__all__: List[str] = ["Deck", "Theme", "rgb"]
