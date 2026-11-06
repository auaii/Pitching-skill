#!/usr/bin/env python3
"""Example: a short 8-slide pitch built with deck_kit. Copy this file as the start of a real deck.

The product ("Northwind Desk") is FICTIONAL and every number is labelled as an example,
following truth rule A4. Replace both with real, sourced content.

Usage:
    python example_deck.py --out build/example.pptx [--backgrounds build/bg]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deck_kit import Deck, Theme  # noqa: E402


def build(out, backgrounds=None):
    d = Deck(Theme(product="Northwind Desk", backgrounds_dir=backgrounds))

    # ---- PROBLEM (30%) ------------------------------------------------------
    s = d.question("Your customers ask the same questions every day.",
                   "Who answers them at 2 a.m.?")
    d.notes(s, step=1, part="problem", time=1,
            talk="Open with the question and stop. Let the room answer before you go on.",
            ask="How many of your support tickets are repeat questions?",
            next="Let's look at what those repeat questions cost.")

    s = d.three_cards("The problem", "Three questions every support lead asks", [
        ("clock", "How long do they wait?", "Hours", "Customers wait overnight for simple answers."),
        ("chart", "How much does it cost?", "Every ticket", "Each repeat question takes an agent's time."),
        ("shield", "Is the answer right?", "It depends", "Answers change from agent to agent."),
    ], band="Example: a team that answers 400 repeat questions a week.")
    d.notes(s, step=2, part="problem", time=2,
            talk="Walk through each question. Use the customer's own numbers if they gave any.",
            ask="Which of these three hurts you most today?",
            next="So what if those answers were ready before anyone asked?")

    # ---- SOLUTION (40%) -----------------------------------------------------
    s = d.reveal("What if the answers were ready before anyone asked?", "Northwind Desk",
                 "Answers your repeat questions from your own help pages, day and night.")
    d.notes(s, step=3, part="solution", time=1.5,
            talk="Say the name, then the tagline. The tagline explains the name: say nothing more yet.",
            next="Here is what changes for your team.")

    s = d.three_cards("What you get", "Faster answers. Lower cost. One right answer.", [
        ("clock", "Faster", "Minutes", "Repeat questions answered at any hour."),
        ("chart", "Lower cost", "Fewer tickets", "Agents spend time on the hard cases."),
        ("shield", "Consistent", "One answer", "Every reply comes from the same approved pages."),
    ], dark=True, band="Example: overnight wait  ->  answered in minutes.")
    d.notes(s, step=4, part="solution", time=2.5,
            talk="One benefit per question from slide 2, same icon, same order.",
            ask="What would your team do with the time back?",
            next="How does it do that? Three simple parts.")

    s = d.steps("How it works", "Three parts, one per question", [
        ("Reads your pages", "Uses the help pages you already have."),
        ("Answers any hour", "Replies in chat, day and night."),
        ("Hands off to people", "Passes hard cases to an agent, with context."),
    ], band="Your team approves which pages it can use.")
    d.notes(s, step=5, part="solution", time=2,
            talk="Stay at 'what', not 'how'. The detail belongs in the demo.",
            next="Let's put the three questions and answers side by side.")

    # ---- SUMMARY (30%) ------------------------------------------------------
    s = d.recap("Summary", "Three questions. Three answers.", [
        ("clock", "How long do they wait?", "Hours, overnight", "Minutes, any hour"),
        ("chart", "How much does it cost?", "Agent time per ticket", "Agents on hard cases"),
        ("shield", "Is the answer right?", "Varies by agent", "One approved answer"),
    ])
    d.notes(s, step=6, part="summary", time=1.5,
            talk="Read each row left to right: question, cost, answer.",
            next="So what happens next? It's small.")

    s = d.steps("What happens next", "Small steps, no big project", [
        ("30-minute demo", "On your own help pages."),
        ("Two-week pilot", "One team, one channel."),
        ("Review together", "Keep it only if the numbers work."),
    ], band="No long contract to start.")
    d.notes(s, step=6, part="summary", time=2,
            talk="Promise only what the team can really do. Change these steps to match your offer.",
            ask="Who else should see the demo?",
            next="Back to the question we started with.")

    s = d.cta("Who answers at 2 a.m.?", "With Northwind Desk, your own help pages do.",
              "Book a 30-minute demo", "name@company.com  ·  +00 000 000 000")
    d.notes(s, step=6, part="summary", time=1.5,
            talk="Close the loop on slide 1. Say thank you aloud; this slide stays up during questions.")

    return d.save(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="build/example.pptx")
    ap.add_argument("--backgrounds", help="folder made by gen_backgrounds.py")
    a = ap.parse_args()
    print("saved", build(a.out, a.backgrounds))
