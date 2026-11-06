# Using an image model (ChatGPT, Codex, other hosts)

Read this in Stage 5 when the app you run in can generate images. An AI image makes a
slide feel designed: a hero background, the analogy drawn as a picture, a before/after
scene. It never carries words, numbers or logos. Those stay real, editable text so the
sales team can change them and so nothing is misspelled or invented.

## 1. Which path to use
| Where you run | Image tool | What to do |
|---|---|---|
| ChatGPT (chat, Projects, Custom GPT with Image Generation on) | built-in image generation | Generate each image in the chat, one call per image. Then get the file into the code sandbox (section 5). |
| Codex CLI / Codex in the ChatGPT desktop app | built-in `image_gen` (Codex's `imagegen` skill) | One `image_gen` call per image. Codex saves it under `$CODEX_HOME/generated_images/`; copy the chosen file into the project, e.g. `build/img/`. Never leave a deck asset only there. |
| Any host, user explicitly wants the API and has `OPENAI_API_KEY` set | Image API | Use the host's own image skill or CLI if it has one. Never ask the user to paste a key into chat. |
| No image tool (Claude, Kiro Crew without an image model, offline) | none | Use `scripts/gen_backgrounds.py` and the drawn icons. The deck still looks designed. |

Ask before generating more than 6 images: each one takes time and may cost the user credits.

## 2. What to generate, and what not to
| Generate (decoration and metaphor) | Never generate (keep it real) |
|---|---|
| Hero background for the opening question, reveal and CTA | Any text, headline, label, number or chart |
| Dark/light backgrounds with a calm area for text | Logos (yours, customers', tools'): use the real files |
| The analogy as a picture (a bridge, a gate, a lighthouse) | Icons in a set: use deck_kit's drawn icons so they match |
| A before/after scene (a person waiting vs. getting an answer) | Screenshots of the product: use real screenshots |
| A texture or abstract shape behind a section break | Real people's faces, or anything that looks like a customer photo |

Budget for a 12-16 slide deck: 3-6 images. One hero background, reused for the reveal and
the CTA, plus 1-2 illustrations, is often enough. A taste, not a feast (A1) applies to
pictures too.

## 3. Keep every image in one style
Write one **style line** once and paste it into every prompt, with the theme's colours:

```
Style: modern editorial illustration, soft gradients, subtle grain, deep navy #0A1221
background, warm amber #F7A81E accent light, calm and premium, consistent across a set.
Constraints: no text, no letters, no numbers, no logos, no watermark, no UI, no faces.
```

Change only the subject between images. If one image comes out in a different style,
regenerate it with the same style line rather than changing the others.

## 4. Prompt recipes (fill the <...>)
Prompts follow the structure Codex's `imagegen` skill uses. Size: ask for a wide landscape
image (16:9 if the tool takes a size, e.g. 1536x864 or 2048x1152; otherwise landscape).
`prep_image.py` fixes the aspect afterwards.

**Hero background** (opening question, reveal, CTA: text in the centre)
```
Use case: stylized-concept
Asset type: presentation slide background, 16:9
Primary request: an abstract scene that suggests <the analogy, e.g. light bridges connecting islands>
Composition/framing: wide; keep the centre 60% dark, calm and empty for a large headline;
detail only near the edges
Lighting/mood: low-key, glowing amber accents
<style line>
```

**Section background** (title top-left, cards below)
```
Use case: stylized-concept
Asset type: presentation slide background, 16:9
Primary request: soft abstract shapes that hint at <topic>
Composition/framing: detail in the top-right corner only; the left two-thirds and the lower
half stay smooth and dark for text and cards
<style line>
```

**Analogy illustration** (the "Name the concept" slide: text left, picture right)
```
Use case: illustration-story
Asset type: illustration for the right side of a slide, about 5:4
Primary request: <the analogy drawn simply, e.g. a small suspension bridge linking an AI
assistant island to a company-building island>
Composition/framing: one clear subject, centred, generous margin, plain background that
blends into deep navy
<style line>
```

**Before/after scene** (benefits slide strip, or a use-case slide)
```
Use case: illustration-story
Asset type: pair of illustrations, same style, side by side, each about 4:3
Primary request: before: <someone waiting, e.g. a salesperson waiting a day for a report>;
after: <the same person getting the answer at once>
Composition/framing: same character, same room, same camera angle in both; only the
situation changes
<style line>
```
Generate the two halves as two calls with the same prompt except the before/after line.

## 5. Get the image into the deck
1. Save each chosen image into the project, e.g. `build/img/hero-raw.png`.
   - Codex: copy from `$CODEX_HOME/generated_images/...`.
   - ChatGPT: if the code sandbox cannot see the generated image, ask the user to download it
     and attach it to the chat, then continue. Say this plainly; don't pretend it is there.
2. Fit it with `scripts/prep_image.py`, which crops to the aspect, resizes, darkens the text
   zone and checks contrast:
   ```bash
   # background with a centred headline
   python scripts/prep_image.py build/img/hero-raw.png --out build/bg/bg-hero.jpg --scrim center
   # background with a title top-left and cards
   python scripts/prep_image.py build/img/sec-raw.png --out build/bg/bg-dark-a.jpg --scrim left
   # illustration for a 5 x 4.2 inch box
   python scripts/prep_image.py build/img/bridge-raw.png --out build/img/bridge.png --aspect 5:4.2 --width 1500
   ```
   A `WARN` means light text will be hard to read there: raise `--strength`, move the scrim,
   or pick another image.
3. Use it in the build script:
   - Backgrounds named `bg-hero.jpg`, `bg-dark-a.jpg` (b, c), `bg-light-a.jpg` (b) in one
     folder are picked up by `Theme(backgrounds_dir=...)`. Mix freely: generate only
     `bg-hero.jpg` and let `gen_backgrounds.py` paint the rest.
   - One slide only: `deck.set_background(slide, "build/img/special.jpg")`.
   - Illustration: `deck.image(slide, "build/img/bridge.png", x, y, w, h, radius=0.06)`.
4. Render (`scripts/render.sh`) and look: the headline must be readable, the picture must not
   compete with the one message of the slide (1-2-3-4 rule), and the style must match across
   slides.

## 6. Truth and rights
- An AI picture is an illustration, never evidence. Do not make it look like a real customer,
  a real office or a real product screen.
- Do not generate a competitor's or customer's logo or a lookalike.
- Keep the final prompt list in the hand-off (Stage 7) so the user can regenerate an image.
