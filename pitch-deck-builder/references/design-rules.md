# Design and writing rules

## The 1-2-3-4 rule (every slide)
- **1** key message per slide. The title states it as a sentence, not a label.
- **2** fonts at most: one for titles, one for body. Bold and size changes are fine.
- **3** colours: background, text, one accent. Shades of one colour count as one. Real
  logos don't count. A second accent only when it carries meaning, never as decoration.
- **4** sub-points at most (cards, bullets, steps, rows). Five or more: split or merge.

`scripts/audit.py` checks fonts and card counts automatically.

## Fonts
Pick fonts installed on both Mac and Windows, so the deck looks the same on the
presenter's laptop:

| Deck language | Titles | Body | Note |
|---|---|---|---|
| English | Georgia | Calibri | deck_kit default |
| Thai, or Thai + English | Tahoma | Tahoma | Georgia and Calibri have no Thai letters; PowerPoint swaps in a random fallback font |
| Thai, more style | Leelawadee UI | Leelawadee UI | Windows; on Mac it falls back. Embed fonts or export PDF |

Set the fonts in `Theme(font_title=..., font_body=...)`. If you use a font that is not on
the presenting machine, also hand over a PDF.

## Sizes (16:9, 13.33 x 7.5 in)
- Title 36-46 pt, card heading 16-18 pt, body 14-20 pt, footer 10-11 pt.
- Big room or online with small windows: no body text under 18 pt.
- One big number in 32+ pt beats a paragraph.

## Writing for non-technical audiences
- Short sentences. Translate every technical term, or remove it.
- Big number + one short line beats a paragraph. Detail goes in the speaker notes.
- Impact/benefit cards: icon + pain question + one big figure or word + one sentence.
- Headline pattern: small ALL-CAPS kicker + one large title.
- Use names they know before introducing new ones.
- Avoid hype words: one-click, seamless, revolutionary, world-class, enterprise-grade,
  guaranteed. Say what it does and how long it takes.
- Label example numbers as "Example". Label sourced numbers with "Source: ...".

## Images and editability
- Without an image model, paint backgrounds with code (`scripts/gen_backgrounds.py`:
  gradient + glows + faint dot grid + grain) and keep all text editable.
- Full-image slides look polished but the sales team cannot edit them. Use images for
  decoration, real text for words and numbers.
- Use a company's real logo only with permission. Never mock up a customer logo.
