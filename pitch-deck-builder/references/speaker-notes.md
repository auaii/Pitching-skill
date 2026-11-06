# Speaker notes format

Every slide gets notes in this format. `deck_kit.Deck.notes()` writes it, and
`scripts/audit.py` reads it to check hand-offs, timing and the 30/40/30 ratio.

```
TALK: What the presenter says, in 2-4 short sentences. Include pauses ("Pause.").
ASK: An optional question for the room (the 70/30 rule: listen more than you pitch).
TIME: 1.5 min
PART: problem | STEP: 1
NEXT: The lead-in line that hands off to the next slide.
```

| Field | Required | Rule |
|---|---|---|
| TALK | yes | Spoken words, not the slide text again. Caveats and detail live here. |
| ASK | no | One open question. Put at least one on a problem slide. |
| TIME | yes | Minutes. The total should match the slot within 15%. |
| PART | yes | problem, solution or summary. Feeds the ratio check. |
| STEP | no | 1-6 from the 6-step structure. |
| NEXT | yes, except last slide | One sentence that makes them curious about the next slide. |

At about 130 spoken words a minute, a 1-minute slide holds about 130 words of TALK.
The audit warns when the notes are much longer than TIME allows.

Example:
```
TALK: Open with the question and stop. Let the room answer before you go on.
ASK: How many of your support tickets are repeat questions?
TIME: 1 min
PART: problem | STEP: 1
NEXT: Let's look at what those repeat questions cost.
```
