---
name: pitch-deck-builder
description: Plan and build a persuasive pitch deck or sales presentation for a non-technical audience (executives, sales, customers, a committee). Runs a 5W1H brief, a 6-step storyline with a 30/40/30 ratio, sourced evidence, then an editable 16:9 .pptx with speaker notes that is rendered and audited. Use for pitch deck, sales deck, product presentation, demo pitch, slide outline or talk script. Thai triggers - ทำสไลด์ pitch, เตรียมพรีเซนต์ลูกค้า, ทำ presentation ขายของ, เขียนสคริปต์พรีเซนต์. Not for lecture slides, data reports or document formatting.
license: MIT
compatibility: Works with any Agent Skills client. Building the .pptx needs Python 3.9+ with python-pptx and Pillow; rendering needs LibreOffice and pdftoppm. Without code execution, deliver content only (brief, outline, slide spec, notes).
metadata:
  version: "2.2.0"
  author: auaii
---

# Pitch Deck Builder

A pitch earns the next step (a demo, a meeting, a pilot). It does not explain everything
and it does not close the deal. This skill turns a product or idea into a short story
with one clear call to action, then into an editable deck that a sales team can present.

## Files in this skill
Paths are relative to this skill's folder. Read a reference file only when its stage needs it.

| File | Read it when |
|---|---|
| `references/structure.md` | Stage 3: the 6-step structure, 30/40/30 ratio, summary pattern |
| `references/layouts.md` | Stage 5: which layout fits each slide |
| `references/design-rules.md` | Stage 5: 1-2-3-4 rule, writing rules, fonts (incl. Thai) |
| `references/speaker-notes.md` | Stage 5: the notes format the audit reads |
| `references/image-generation.md` | Stage 5, when the app has an image model (ChatGPT, Codex) |
| `references/gotchas.md` | Something renders wrong, or a tool fails |
| `references/example-ai-platform.md` | You want a finished real example of brief + outline |
| `assets/brief-template.md`, `assets/outline-template.md` | Stages 1 and 3: copy and fill |
| `assets/objections-template.md` | Stage 7: Q&A and objection prep |
| `scripts/deck_kit.py` | Stage 5: python-pptx helpers, one function per layout |
| `scripts/example_deck.py` | Stage 5: a complete 8-slide deck to copy as a start |
| `scripts/gen_backgrounds.py` | Stage 5: paint background images with code (no image model) |
| `scripts/prep_image.py` | Stage 5: fit a generated image to a slide (crop, scrim, contrast check) |
| `scripts/render.sh` | Stage 6: .pptx -> PDF -> PNG per slide + contact sheet |
| `scripts/audit.py` | Stage 6: automatic rule checks on any .pptx |

## Choose the output mode first
- **Full mode** (you can run Python): build, render and audit the .pptx with the scripts.
- **Content mode** (no code execution, or the user only wants words): deliver the brief,
  the outline, a slide-by-slide spec (title, body, layout name, visual idea) and the
  speaker notes. Every stage still applies except the build and render steps.
Say which mode you are in. Install dependencies with `pip install -r requirements.txt`.

---

# Part A: Principles (apply at every step)

**A1. A taste, not a feast.** The audience should want to taste more, not eat the whole meal.
- Show only the 2-3 points that matter most to this audience.
- Stop at "what" and "why it matters". Save the full "how" for the demo.
- The CTA is the next small step (book a 30-minute demo), never "sign now".
- Keep deep detail off the slides: speaker notes, appendix, Q&A prep.
- When in doubt, cut. If a slide can go and the story still holds, remove it.

**A2. Always tell a story.** A presentation is a story, never a list of slides.
- Start from the familiar (what they already use), then move to the new idea.
- The hero is the audience, not the product. The product helps the hero.
- Build tension before the answer: problem -> cost -> turn -> reveal.
- One analogy carries the whole story (e.g. bridge = a connection, gate = the control
  point). Never switch metaphors.
- Show a scene, not a claim: a concrete before/after beats an adjective.
- Every slide hands off to the next: the notes end with a lead-in line.
- Close the loop: the last slide answers the opening question.
- Test: the whole deck can be told in 5 sentences.

**A3. Persuasion frameworks.**
- **Define the target before you throw.** Know the audience's KPIs and what value means
  to them. Every pain and every benefit maps to something they are measured on.
- **70/30 pre-pitch.** In the meeting: 70% listening and asking, 30% pitching. Open with a
  question, put pauses and room questions in the notes, prepare 3-5 discovery questions.
- **[K] + [F] + [C] = impact.** Each section and the whole deck needs a Key message, a
  Found story (an example, a scene) and a Call to action. Missing one: add it or cut the section.

**A4. Truth.** Never invent statistics, customer names, quotes or logos. Every number on a
slide has a source line or is labelled "Example". Claims match what the product does today.
Missing data stays a visible placeholder and goes on the open-items list.

---

# Part B: Workflow (7 stages, each ends with a check)

### Stage 1. Prepare the brief (5W1H)
Ask only what you cannot read or infer, and state every assumption. Copy
`assets/brief-template.md` and fill it in.

| Question | Ask | It decides |
|---|---|---|
| **WHO** | Audience, role, technical level, who decides, their KPIs and fears | Vocabulary, depth, which pains lead |
| **WHY** | The one action we want; what they gain by listening | The CTA and the opening hook |
| **WHAT** | Topic, key message in one sentence, standout points, proof | Solution content, what to research |
| **WHEN** | Date, slot length, draft deadline | Slide count (about 1 per 1-2 min), timing |
| **WHERE** | Online or in person, screen, whose laptop, internet | Font size, theme, PDF backup, live demo or not |
| **HOW** | Presenter(s), format (talk, demo, Q&A), extras (handout, rehearsal) | Deliverables beyond the deck |

Language: write the deck in the language the audience will read. For Thai, see the font
rule in `references/design-rules.md`.
**Check:** WHO, WHY and WHAT are answered. WHEN/WHERE/HOW may use stated defaults
(20 minutes, in person, 16:9, presenter's laptop).

### Stage 2. Understand the subject and choose the points
1. Read the real product, UI or docs. List what it actually does today. (A client-rendered
   web app with no readable HTML can often be read from its JS bundle: UI strings, nav labels.)
2. Offer those real capabilities as a list. The user picks 2-3. These become the pains
   that run through the whole story.
**Check:** the user has chosen the points, and each maps to an audience KPI.

### Stage 3. Write the storyline
1. Map the story onto the 6-step structure and the 30/40/30 ratio (`references/structure.md`).
2. Thread rule: the same 2-3 pains run question -> impact -> benefit -> feature -> recap,
   with the same icon and the same words each time.
3. Pick the single analogy.
4. Write the outline with `assets/outline-template.md`: one line per slide, labelled with
   its step, its part (problem/solution/summary) and its layout.
5. Write the 5-sentence version of the deck at the top of the outline.
**Check:** the user agrees the outline; it passes the 5-sentence test and [K]+[F]+[C].

### Stage 4. Gather evidence and check claims
1. Search for impact statistics and the presenter's credentials. Record each source
   (publisher, title, date, link).
2. No reliable figure: use words, not an invented number.
3. Compare every claim with the product. Cut overclaims ("no engineers required",
   "one-click", "enterprise-grade" with no facts behind it). Put caveats in the notes.
**Check:** every number has a source; no claim goes beyond the product.

### Stage 5. Design and build
1. Choose a layout per slide (`references/layouts.md`).
2. Apply the 1-2-3-4 rule and the writing rules (`references/design-rules.md`).
3. Visuals. If this app can generate images (ChatGPT image generation, Codex `image_gen`),
   follow `references/image-generation.md`: 3-6 images in one style (hero background,
   the analogy as a picture, a before/after scene), never with text, numbers or logos in
   them, each fitted with `scripts/prep_image.py`. Without an image model, run
   `scripts/gen_backgrounds.py --out build/bg`. Either way, pass the folder as
   `Theme(backgrounds_dir=...)`.
4. Full mode: start from `scripts/example_deck.py`, which uses `scripts/deck_kit.py`.
   Use real text, real logos (only with permission) and speaker notes on every slide in
   the format of `references/speaker-notes.md`.
5. Content mode: write the slide-by-slide spec and the notes in the same format, plus an
   image prompt for each slide that should have a picture.
**Check:** the deck builds without errors and every slide has notes.

### Stage 6. Review
1. Full mode: run `scripts/render.sh build/deck.pptx` and look at every slide PNG and the
   contact sheet. Never report a design you have not looked at.
2. Run `python scripts/audit.py build/deck.pptx --minutes <slot> --jargon "<words>"`.
   Fix every FAIL; fix each WARN or explain why it is fine.
3. Check by hand what a script cannot judge:
   - Every step of the 6-step structure is present and in order (step table: step -> slides)
   - Thread: no pain drops out between question, benefit, feature and recap
   - One analogy only; the last slide answers the first slide's question
   - The deck passes the 5-sentence test
**Check:** the audit has no FAIL, and each manual item passes or is an open item.

### Stage 7. Hand off
Give the user: the file path, the step table, the source list, the audit result, and the
open items (placeholders, figures to confirm, contact details, logo permissions), and the
image prompts used, so any picture can be regenerated. Offer
the HOW extras: Q&A and objection prep (`assets/objections-template.md`), a PDF backup,
a one-page handout, a rehearsal timing pass.

---

## Never do
- End on a "Thank you", "Q&A" or "Any questions?" slide. The CTA slide is last and stays up
  during questions; the presenter says thank you aloud.
- Put more than 4 cards, bullets, steps or rows on one slide.
- Show a raw technical term to a non-technical audience without translating it.
- Use a real company's logo or name as a customer without the user confirming it is true.
- Put words, numbers or logos inside a generated image. They go on the slide as real text.
