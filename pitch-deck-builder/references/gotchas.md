# Gotchas (things that broke before, and the fix)

## Rendering
- **`soffice` exits 127 on macOS.** The Homebrew cask can stay "installed" after the app
  bundle was deleted, leaving a wrapper that points at nothing. Fix:
  `brew reinstall --cask libreoffice`. The real binary is
  `/Applications/LibreOffice.app/Contents/MacOS/soffice`. `scripts/render.sh` tests each
  candidate and uses the first that runs; override with `SOFFICE=/path/to/soffice`.
- **Headless conversion does nothing** while a LibreOffice window is open. `render.sh`
  uses a private profile (`-env:UserInstallation`) to avoid this.
- **Render at 96 dpi.** Odd DPIs can show a fake 1px line at the slide edge.
- **No LibreOffice at all.** Open the .pptx in PowerPoint or Keynote, export to PDF, then
  `pdftoppm -r 96 -png deck.pdf out/slide`. In content mode, skip rendering and say so.
- LibreOffice previews can differ slightly from PowerPoint (line breaks, shadows). Leave
  some slack in text boxes; check the final in PowerPoint before presenting.

## Fonts and text
- Some serif fonts draw "+" as an ornament in previews. Set figures like "2,400+" in the
  body font.
- Thai text in Georgia/Calibri falls back to a random font. Use Tahoma
  (`references/design-rules.md`).
- **Thai text disappears in the preview.** python-pptx `font.name` sets only the Latin font
  slot; Thai is drawn from the complex-script slot (`<a:cs>`). `deck_kit` sets all three
  (latin, ea, cs). If you write runs yourself, call `deck_kit.set_script_fonts(run, face)`.
- **Headless LibreOffice ignores system fonts.** On macOS it silently swapped Georgia and
  Tahoma for LinuxLibertine and NotoSans. `render.sh` copies the fonts the deck names
  into its private profile and prints "fonts in preview: ..."; if a name there is not the
  one you chose, the preview is wrong, not the deck. Calibri shows as Carlito on a Mac
  without Office: same metrics, fine for checking layout.
- **No letter-spacing or ALL-CAPS for Thai.** Tracking pulls vowels and tone marks away
  from their consonants. `deck_kit` turns tracking off for Thai kickers automatically.
- Long words do not wrap in narrow cards. Shorten the heading or widen the card.

## Shapes and images
- Icon-set logos can touch the image edge. Pad the SVG viewBox or the tips get clipped.
- Draw connector dots and badges last, or later cards cover them.
- A straight accent strip on a rounded card pokes out at the corners. Use a separate
  rounded shape or a small bar inside the card.
- Translucent "glass" cards (`deck_kit.card`) need a background image behind them to look
  right. On a flat fill they look grey; raise the opacity or use a solid card.

## Python
- `pip install python-pptx Pillow` (the import name is `pptx`, the package name is
  `python-pptx`).
- On macOS with Homebrew Python, `pip install` may refuse ("externally managed"). Use a
  virtual environment: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.

## Content
- A client-rendered web app (SPA) returns empty HTML to simple fetch tools. Read its JS
  bundle for UI strings and nav labels, ask for screenshots, or use a real browser.
- Do not trust a statistic you cannot trace to a publisher and a date. Use words instead.
