# Slide layout library

The "deck_kit" column names the helper in `scripts/deck_kit.py`. "build" means compose it from
the primitives (`new_slide`, `kicker`, `title`, `card`, `icon_disc`, `line`, `text`, `frame`).

| Layout | Step | Shape | deck_kit |
|---|---|---|---|
| Opening question | 1 | Dark hero background, one question on two lines (second line in the accent colour), centred, nothing else | `question()` |
| Familiar things | 1 | 3 cards with real logos of tools they use, one dark band with the "but..." line | build |
| Fan-out connection | 1 | One node left, lines to 3-4 labelled cards on the right, one caption | build |
| Name the concept | 1 | Text left, small analogy illustration right, one dark key-line band | build |
| Problem + impact | 1-2 | 3 equal cards: icon + pain question, one big figure or word, one sentence; source line | `three_cards()` |
| Reveal | 3 | Hero background, setup line, "INTRODUCING", product name, a tagline that explains it | `reveal()` |
| Middle-layer diagram | 3 | Inputs left, product block highlighted in the centre, outputs right; straight colour-coded lines with end dots | build |
| Benefits | 4 | 3 cards (icon + outcome word + sentence), dark before -> after strip | `three_cards(dark=True, band=...)` |
| Feature | 5 | Icon + name + subtitle, "ANSWERS:" line, mini diagram with the covered part lit, 3 numbered cards, key line | build (`steps()` for the cards) |
| Proof | 5 or 6 | Title + headline-number sentence, 3-4 stat cards, awards line, source line | `three_cards(source=...)` |
| Recap table | 6 | One row per pain: icon, question, cost, arrow, answer | `recap()` |
| Next steps | 6 | 3-4 numbered step cards + reassurance band | `steps()` |
| CTA | 6, last | Hero background, closing title, call-back sentence, one button, contact line | `cta()` |

### Scene-led layouts (see `scene-led-pitch.md`)
| Layout | Step | Shape | deck_kit |
|---|---|---|---|
| Chat scene | 1, 5 | Time-stamp kicker, app-window mock-up with the persona's question and the AI's reply, "Illustrative example" label | build |
| Two workarounds | 1 | 2 tall cards (icon + name + 3 ruled cost lines), takeaway bar | build |
| Number vs number | 2 | AI answer card, "why they differ" numbered list in the middle, true-figure card; analyst quote callout below | build |
| Pillars | 2-3 | 3 cards: one-word pillar + its question + what it takes + "Where it broke: ..." | build |
| Flow with pillar chips | 3 | 4 columns left to right (inputs -> product parts -> outputs), arrows, pillar chips under the part that delivers each | build |
| Wrong vs right artifact | 5 | ✗ card (the naive way) above ✓ card (your way) on the left, the definition or config on the right | build |
| Who gains | 6 | 4 columns, one per buyer role: icon, role, their fear in quotes, 3 checks | build |
| Pilot plan | 6 | 4 chevrons (Discover, Build, Use, Decide), one line each, scope + sourced cost band | build |

**Takeaway bar:** in scene-led decks every content slide ends with a full-width tinted band
holding one "so what" sentence, at the same position on every slide.

## Common frame on every slide
ALL-CAPS kicker with an accent bar top-left, brand logo top-right, product name bottom-left,
page number bottom-right. `Deck.frame()` draws it; call it last so it sits on top.

## Rhythm
- Alternate dark and light slides so the eye gets a reset; use the hero background only
  for the opening question, the reveal and the CTA.
- Keep one layout per idea. Do not repeat the same layout more than 3 times in a row.

## Icons in deck_kit
`blocks` (build / easy), `shield` (safe / control), `cloud` (scale / ready), `clock`
(speed / time), `chart` (growth / cost), `number:N` (numbered disc). They are drawn with
shapes, so they stay editable and sharp. Use the same icon for the same pain everywhere.
