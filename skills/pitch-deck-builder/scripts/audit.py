#!/usr/bin/env python3
"""Audit a pitch deck against the skill's rules (Stage 6). Works on ANY .pptx.

Usage:
    python audit.py deck.pptx [--minutes 20] [--jargon "MCP,schema,API"] [--json]

FAIL (exit code 1): a rule is broken.
    notes        a slide has no speaker notes
    fonts        more than 2 font families in the deck
    sub-points   more than 4 cards on a slide (shapes named "card" by deck_kit)
    ending       the last slide says Thank you / Q&A / Any questions
WARN: worth a look; may be fine.
    hand-off     no "NEXT:" line in the notes (all slides but the last)
    timing       TIME: lines missing, or total differs from --minutes by >15%
    talk-length  notes are much longer than TIME allows (~130 spoken words per minute)
    ratio        problem / solution / summary minutes far from 30 / 40 / 30
    numbers      a statistic (68%, $2M, 2,400+, 3x) with no "Source" and no "example" label
    hype         words like "one-click", "seamless", "revolutionary"
    jargon       words from --jargon appear on a slide
Notes convention (deck_kit writes it): TALK:, ASK:, TIME: <n> min, PART: problem|solution|summary, NEXT:.
Checks of story and judgement (5-sentence test, thread, analogy) stay manual.
"""
import argparse
import json
import re
import sys
from collections import defaultdict

from pptx import Presentation

HYPE = ["one-click", "one click", "seamless", "revolutionary", "game-changing", "game changer",
        "best-in-class", "world-class", "enterprise-grade", "cutting-edge", "next-gen",
        "no engineers required", "effortless", "magic", "guaranteed", "100% secure"]
ENDINGS = ["thank you", "thanks", "q&a", "q & a", "any questions", "questions?",
           "ขอบคุณ", "ถาม-ตอบ", "ถาม ตอบ", "มีคำถาม", "คำถามและคำตอบ"]
WPM = 130
STAT = re.compile(r"\d+(\.\d+)?\s?%|[$€£¥฿]\s?\d|\d\s?(USD|THB|บาท)\b|\b\d{1,3}(,\d{3})+\b|\d\+"
                  r"|\b\d+(\.\d+)?\s?[x×]\b|\b\d+(\.\d+)?\s?(k|m|bn|million|billion|ล้าน)\b", re.I)


def slide_texts(slide):
    """(text, font_names) for every text run on the slide, groups included."""
    out = []

    def walk(shapes):
        for sh in shapes:
            if sh.shape_type == 6:  # group
                walk(sh.shapes)
                continue
            if getattr(sh, "has_text_frame", False) and sh.has_text_frame:
                for p in sh.text_frame.paragraphs:
                    for r in p.runs:
                        out.append((r.text, r.font.name))
            if getattr(sh, "has_table", False) and sh.has_table:
                for row in sh.table.rows:
                    for cell in row.cells:
                        for p in cell.text_frame.paragraphs:
                            for r in p.runs:
                                out.append((r.text, r.font.name))
    walk(slide.shapes)
    return out


def count_cards(slide):
    return sum(1 for sh in slide.shapes if sh.name == "card")


def parse_notes(slide):
    if not slide.has_notes_slide:
        return "", {}
    text = slide.notes_slide.notes_text_frame.text.strip()
    fields = {}
    m = re.search(r"TIME:\s*([\d.]+)", text)
    if m:
        fields["time"] = float(m.group(1))
    m = re.search(r"PART:\s*(problem|solution|summary)", text, re.I)
    if m:
        fields["part"] = m.group(1).lower()
    fields["next"] = bool(re.search(r"^NEXT:\s*\S", text, re.M))
    return text, fields


def audit(path, minutes=None, jargon=()):
    prs = Presentation(path)
    slides = list(prs.slides)
    findings = []  # (level, rule, slide_no or None, message)
    fonts = set()
    part_min = defaultdict(float)
    total_time, timed = 0.0, 0

    # Text on more than half the slides is the frame (product name in the footer, etc.):
    # skip it for content checks, or the product name trips the jargon check everywhere.
    per_slide = [slide_texts(s) for s in slides]
    seen = defaultdict(int)
    for runs in per_slide:
        for t in {t.strip() for t, _ in runs if t.strip()}:
            seen[t] += 1
    frame = {t for t, n in seen.items() if len(slides) >= 4 and n > len(slides) / 2}

    for i, (s, all_runs) in enumerate(zip(slides, per_slide), 1):
        fonts.update(f for _, f in all_runs if f)
        runs = [(t, f) for t, f in all_runs if t.strip() not in frame]
        visible = " ".join(t for t, _ in runs)
        low = visible.lower()
        notes, nf = parse_notes(s)
        last = i == len(slides)

        if not notes:
            findings.append(("FAIL", "notes", i, "no speaker notes"))
        else:
            if not last and not nf["next"]:
                findings.append(("WARN", "hand-off", i, "no NEXT: lead-in line in notes"))
            if "time" in nf:
                total_time += nf["time"]
                timed += 1
                words = len(notes.split())
                if words > nf["time"] * WPM * 1.5:
                    findings.append(("WARN", "talk-length", i,
                                     f"{words} words of notes for {nf['time']:g} min (~{WPM} wpm)"))
                if "part" in nf:
                    part_min[nf["part"]] += nf["time"]

        n_cards = count_cards(s)
        if n_cards > 4:
            findings.append(("FAIL", "sub-points", i, f"{n_cards} cards; split or merge to 4 or fewer"))

        # numbers: only statistic-like figures (68%, $2M, 2,400+, 3x, 5 million), not times or phones
        figures = [t for t, _ in runs if STAT.search(t)]
        if figures and not re.search(r"\bsources?\b|ที่มา|example|illustrative|ตัวอย่าง", low):
            findings.append(("WARN", "numbers", i,
                             f"figure(s) {figures[:3]} with no 'Source:' or 'example' label"))

        for w in HYPE:
            if w in low:
                findings.append(("WARN", "hype", i, f"'{w}': replace with a concrete, true claim"))
        for w in jargon:
            if re.search(rf"\b{re.escape(w.lower())}\b", low):
                findings.append(("WARN", "jargon", i, f"'{w}' on slide: translate for this audience"))

        if last:
            for w in ENDINGS:
                if w in low:
                    findings.append(("FAIL", "ending", i, f"last slide says '{w}'; end on the CTA"))
                    break

    if len(fonts) > 2:
        findings.append(("FAIL", "fonts", None, f"{len(fonts)} fonts: {sorted(fonts)} (max 2)"))

    if timed < len(slides):
        findings.append(("WARN", "timing", None, f"{len(slides) - timed} slide(s) have no TIME: line"))
    if minutes and total_time and abs(total_time - minutes) > 0.15 * minutes:
        findings.append(("WARN", "timing", None, f"notes add up to {total_time:g} min, slot is {minutes:g} min"))

    ratio = {}
    tp = sum(part_min.values())
    if tp:
        ratio = {k: round(100 * part_min[k] / tp) for k in ("problem", "solution", "summary")}
        target = {"problem": 30, "solution": 40, "summary": 30}
        off = {k: ratio[k] for k in target if abs(ratio[k] - target[k]) > 10}
        if off:
            findings.append(("WARN", "ratio", None,
                             f"problem/solution/summary = {ratio['problem']}/{ratio['solution']}/"
                             f"{ratio['summary']}%, target 30/40/30"))

    return {"deck": path, "slides": len(slides), "fonts": sorted(fonts),
            "minutes": total_time, "ratio": ratio,
            "findings": [dict(level=l, rule=r, slide=s, message=m) for l, r, s, m in findings]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--minutes", type=float, help="time slot in minutes")
    ap.add_argument("--jargon", default="", help="comma-separated words this audience won't know")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rep = audit(a.deck, a.minutes, [w.strip() for w in a.jargon.split(",") if w.strip()])

    if a.json:
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print(f"{rep['deck']}: {rep['slides']} slides, fonts {rep['fonts']}, "
              f"{rep['minutes']:g} min in notes, ratio {rep['ratio'] or 'n/a'}")
        if not rep["findings"]:
            print("PASS: no findings")
        for f in rep["findings"]:
            where = f"slide {f['slide']:02d}" if f["slide"] else "deck"
            print(f"  {f['level']:4}  {f['rule']:<11} {where:<9} {f['message']}")
        fails = sum(f["level"] == "FAIL" for f in rep["findings"])
        warns = len(rep["findings"]) - fails
        print(f"{fails} FAIL, {warns} WARN")
    sys.exit(1 if any(f["level"] == "FAIL" for f in rep["findings"]) else 0)


if __name__ == "__main__":
    main()
