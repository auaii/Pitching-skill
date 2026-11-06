# Worked example: an AI-connection platform pitch

A real deck built with this skill, condensed. Product and company names are replaced with
placeholders: "the Platform" (a tool that builds and governs the connections between a
company's AI assistants and its own systems) and "the Partner" (the cloud consultancy
that sells it).

## Brief (Stage 1, condensed)
- **WHO:** executives and sales-side buyers, zero technical background. They decide on
  risk, speed and control.
- **WHY:** book a 30-minute demo. They gain a safe way to let AI use company data.
- **WHAT:** "The Platform lets your AI use your company's systems safely, with control
  and an audit trail, without a long IT project."
- **WHEN / WHERE / HOW:** about 20 minutes, in person, 16:9, presenter's laptop, English.
- **Words banned on slides:** MCP (only named once, then translated), schema, Lambda, API.

## Points chosen (Stage 2)
From the product's real capabilities the user chose three, each tied to a buyer KPI:

| Pain question | KPI | Feature | Icon |
|---|---|---|---|
| Who builds them? | speed, IT cost | No-code builder | blocks |
| Who can use what? | risk, compliance | Access control + activity log | shield |
| Can it run for real? | time to value | Ready to deploy on the cloud the company already uses | cloud |

## Analogy (Stage 3)
Each connection between the AI and one system is a **bridge**. Many bridges raise three
questions. The Platform builds the bridges; its gateway is the **guarded gate** every
request crosses. The deck never switches to another metaphor.

## 5-sentence test
1. You use AI every day, but it only knows the public internet, not your business.
2. To help with real work it must connect to your systems, one bridge per system.
3. Many bridges raise three questions: who builds them, who can use what, can it run for real?
4. The Platform builds the bridges without code and guards them with one gate.
5. Book a 30-minute demo and we'll connect your AI to one of your systems.

## Outline (16 slides, about 20 minutes)
| # | Step | Part | Layout | Slide |
|---|---|---|---|---|
| 1 | 1 | problem | Opening question | "You use AI every day. But does it know your business?" |
| 2 | 1 | problem | Familiar things | ChatGPT, Claude, Gemini logos; "...but it only knows the public internet" |
| 3 | 1 | problem | Fan-out connection | Your AI fans out to four systems; each connection is a bridge |
| 4 | 1 | problem | Name the concept | "They're called MCP": bridge illustration, one system = one bridge |
| 5 | 2 | problem | Problem + impact | The three questions, each with a sourced figure |
| 6 | 3 | solution | Proof | The Partner heard these three questions from customers (sourced count) |
| 7 | 3 | solution | Reveal | INTRODUCING the Platform: "builds your AI bridges, and guards them" |
| 8 | 3 | solution | Middle-layer diagram | Systems -> one gate -> AI apps |
| 9 | 4 | solution | Benefits | Faster / Safer / Ready to grow, with an example before -> after |
| 10-12 | 5 | solution | Feature x3 | One per question, each with "ANSWERS: ..." and a mini diagram |
| 13 | 6 | summary | Recap table | Three questions. Three answers. |
| 14 | 6 | summary | Proof | Why us: partner tier, customer count, awards (all sourced) |
| 15 | 6 | summary | Next steps | Demo -> pilot on one system -> review together |
| 16 | 6 | summary | CTA | "Does your AI know your business? It can." Book a 30-minute demo |

## What the audit found on the first draft (Stage 6)
Running `scripts/audit.py --jargon "MCP,schema,Lambda"` on the draft found:
- No TIME:/NEXT: lines in the notes (written before the notes format existed).
- A raw cloud-service name left on a feature slide: translated to "runs on your cloud".
- "2,400+ businesses" and two percentages on the recap with no source line: sources added.
- One hype word ("magic") in a caption: replaced with what actually happens.

## Lessons from this deck
- Benefits slide placed BEFORE the three feature slides worked better than after.
- "One-click deploy" was an overclaim; "ready to deploy on your cloud" is true and still strong.
- The example strip ("about a day of waiting for an export -> an answer in seconds") was
  labelled "Example" because no customer measurement existed yet.
