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
