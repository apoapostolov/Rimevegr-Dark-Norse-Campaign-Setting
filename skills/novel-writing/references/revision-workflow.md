# Revision Workflow

A four-pass system for revising draft chapters. Each pass has a
single focus. Do not combine passes — fixing voice while checking
simulation accuracy splits attention and catches neither.

Run the passes in order. A chapter that fails Pass 1 does not
advance to Pass 2. Fix, then restart from the failed pass.

---

## Before You Start

Gather these before opening the draft:

1. **Simulation state** for the chapter's in-game date: roster,
   morale, food, silver, weather, active contracts, wound states.
   Source: simulation outputs and `consequence-tracking.md` ledger.
2. **Previous chapter's closing state** — its last paragraph
   should contain economic grounding. The current chapter must
   not contradict it.
3. **Character arc tracker** — where each named character stood
   at end of previous chapter. Source: `character-arcs.md`.

---

## Pass 1: Simulation Accuracy

**Focus:** Does the chapter match the world's mechanical state?

### What to Check

| Element    | Source                            | Check                                                          |
| ---------- | --------------------------------- | -------------------------------------------------------------- |
| Roster     | simulation roster file            | Every named character present is alive and at correct location |
| Wounds     | combat_sim output                 | Wounded characters show wounds — limps, bandages, favored arms |
| Weather    | weather system                    | Precipitation, temperature, wind match the generated forecast  |
| Food       | supply tracker                    | Meals described match stores (no feast when food is critical)  |
| Silver     | ledger                            | Spending and income events match treasury balance              |
| Calendar   | `data/hidden/calendar_events.txt` | Any triggered hidden events reflected in narrative             |
| Contracts  | contract state                    | Band is working toward the correct objective                   |
| Settlement | `data/settlements.yaml`           | Geography, NPCs, faction attitude match data                   |

### How to Run

1. Open the simulation output for this chapter's date range.
2. Read the chapter with the data visible beside it.
3. Mark every sentence that references a mechanical state.
4. Cross-check each marked sentence against the data.

### Failure Indicators

- A dead character speaks or acts.
- Food is described when stores read zero.
- Sunshine in a storm. Snow in Long Summer.
- A settlement described with wrong geography or attitude.
- Silver spent on something when the treasury cannot cover it.
- A wound from two chapters ago has vanished without treatment
  or time passing.

### How to Fix

Replace the contradicting detail with the correct mechanical
state. Do not adjust the simulation to match the prose — the
simulation is canonical. If a desired narrative beat requires
state that does not exist, note it for future simulation
adjustment, but do not fabricate state in prose.

### Exit Criteria

Zero contradictions between narrative and simulation data.

---

## Pass 2: Voice Calibration

**Focus:** Does the prose sound like the Iron Ledger voice?

### Voice Checks

Run through these in order. Stop at first failure, fix it,
then continue from that point.

#### 2a. POV Anchor

Read every paragraph. Flag any sentence where the camera floats
outside the declared POV character. "The camp was tense" is
omniscient. "Voss looked at the camp and counted the men who
were not sleeping" is anchored.

Reference: `review-checklist.md`, item A1.

#### 2b. Sentence Rhythm

Count word lengths for ten consecutive sentences at three random
points. Compute standard deviation. If StdDev < 4 at any point,
the rhythm is flat. Shatter the pattern: insert a 3-word sentence
after a 20-word one. Cut a 15-word sentence into two fragments.

Reference: `pacing-and-rhythm.md`, sentence variation rules.

#### 2c. Register

Read aloud. Circle any word that sounds modern, academic, or
therapeutic. "Process," "escalate," "proactive," "meaningful,"
"significant" — these belong in HR emails, not the Rimevegr.

Reference: `anti-ai-detection-library.md`, Category 2 (Lexical
Tells) and Category 4.3 (Therapeutic Framing).

#### 2d. Physical Grounding

Every page must contain at least one physical-sense detail:
something seen, heard, smelled, tasted, or felt against the
body. If a page runs on abstraction, insert a sense-detail
sentence. Prefer smell and touch — they are the most
under-used senses and the most grounding.

Reference: `opening-and-closing-patterns.md`, opening grounding
rules.

#### 2e. Understatement Check

Find the most violent or emotional moment in the chapter.
Measure its prose density (words per beat) against the
surrounding mundane context. If the violent moment is the
longest paragraph on the page, it is inflated. Compress it.
The worst things get the fewest words.

Reference: `combat-to-prose.md`, violence rendering rules.

#### 2f. Dialogue Voice

Cover attributions. Read three exchanges. Can you identify the
speaker from words alone? If not, consult `dialogue-patterns.md`
for each character's speech profile and rewrite to match.

### Voice Fixes

Use `rewrite-calibration-examples.md` as a reference. Find the
failure type that matches your flagged passage. Apply the fix
pattern shown in the before/after pair.

### Voice Exit Criteria

- Zero omniscient slips.
- Sentence rhythm StdDev > 4 at all three sample points.
- Zero register breaks.
- Every page grounded in a physical sense.
- Violent/emotional moments are compressed, not expanded.
- 3/3 blind dialogue identifications correct.

---

## Pass 3: Anti-AI Audit

**Focus:** Does any passage sound generated?

### AI Detection Checks

Run the full scan from `anti-ai-detection-library.md`:

#### 3a. Lexical Scan

Search the chapter for:

- Copula substitutes: "serves as," "acts as," "functions as,"
  "stands as," "represents" → zero allowed
- Hedging: "perhaps," "seemed," "almost," "might have" → max 1
  per page
- AI vocabulary: "tapestry," "landscape" (abstract), "testament,"
  "nuanced," "multifaceted," "delve," "resonated," "compelling,"
  "palpable," "visceral," "deftly," "pivotal," "profound" → zero
  allowed
- Negative parallelisms: "not just X but Y," "not merely,"
  "not only" → max 1 per chapter

#### 3b. Structural Scan

- Count triple-lists per page → max 1
- Check first three words of consecutive paragraphs for mirror
  patterns → max 1 repeat per page
- Measure dialogue turn variance → word counts must vary > 30%

#### 3c. Content Scan

- Read the last sentence of every dark passage → zero
  silver-lining endings
- Search for "realized," "understood," "knew in that moment" →
  zero allowed
- Search for therapeutic language in narration → zero allowed

#### 3d. Fresh-Eyes Pass

Read the chapter as a stranger with no knowledge of the project.
If any paragraph triggers the gut instinct "this sounds
generated," it fails regardless of whether it passed the
mechanical scans.

### AI Detection Fixes

For each failed item:

1. Identify the specific tell from the detection library.
2. Find the matching failure type in
   `rewrite-calibration-examples.md`.
3. Rewrite the passage using the fix pattern.
4. Re-run only the failed scan on the fixed passage.

### AI Detection Exit Criteria

All 21 items on the self-audit checklist in
`anti-ai-detection-library.md` pass their thresholds.

---

## Pass 4: Continuity and Consequence

**Focus:** Do consequences persist? Do arcs advance? Does the
chapter connect to what came before and what comes after?

### Continuity Checks

#### 4a. Wound Persistence

Every physical wound from previous chapters must appear until
healed. A broken arm does not disappear between scenes. A
bruised rib affects how a character moves for days.

Cross-reference: simulation wound states and
`consequence-tracking.md`.

#### 4b. Economic Continuity

The chapter's opening financial state must match the previous
chapter's closing state. Any expenditure or income in this
chapter must be reflected in the closing cost-accounting
paragraph.

Cross-reference: ledger in `consequence-tracking.md`.

#### 4c. Relationship Tracking

Did an NPC react to the band differently than last encounter?
If so, is there a cause (completed contract, broken promise,
reputation change)? Faction attitudes do not shift without
events driving them.

Cross-reference: `settlements.yaml` faction relations and
`consequence-tracking.md` reputation ledger.

#### 4d. Character Arc Micro-Progression

At least one named character must have advanced one micro-step
in their arc. Not a dramatic beat — a small observable change.
Kell's fuse is shorter. Gest's handwriting is shakier. Dalla
offers information she would have withheld two chapters ago.

Cross-reference: `character-arcs.md` for each character's
current arc stage and planned progression.

#### 4e. Foreshadowing and Payoff Audit

List every foreshadowing seed planted in the chapter (dialogue
hints, environmental details, NPC behavior). Verify each has
a planned payoff in the `plot-planning.md` structure. List
every payoff delivered in the chapter and verify the
foreshadowing seed exists in a previous chapter.

Orphan seeds (planted, never paid off) are acceptable — they
add texture. Orphan payoffs (delivered without setup) are
failures that break trust with the reader.

#### 4f. Closing Cost Accountability

The chapter's final paragraph must reference at least two
concrete costs from the day's events. Silver, food, time,
men hurt, miles marched, morale lost. The ledger must close.

Cross-reference: `opening-and-closing-patterns.md` closing
patterns and `review-checklist.md` item F2.

### Continuity Fixes

Continuity failures require inserting or adjusting specific
details:

- Missing wound → add a single physical reference (a limp,
  a favored arm, a wince when sitting).
- Economic gap → add a ledger-line to the closing paragraph.
- Relationship error → adjust the NPC's dialogue or body
  language to match faction state.
- Static arc → find one moment where the character acts and
  adjust their behavior by one degree.
- Orphan payoff → either add the seed to a previous chapter
  (preferred) or cut the payoff.

### Continuity Exit Criteria

- All wounds persist appropriately.
- Economic state continuous across chapter boundaries.
- NPC attitudes match faction data.
- At least one character arc micro-advanced.
- Zero orphan payoffs.
- Closing paragraph contains 2+ concrete costs.

---

## Workflow Summary

```text
Draft Chapter
     │
     ▼
Pass 1: Simulation Accuracy
     │ fail → fix → restart Pass 1
     ▼ pass
Pass 2: Voice Calibration
     │ fail → fix → restart Pass 2
     ▼ pass
Pass 3: Anti-AI Audit
     │ fail → fix → restart Pass 3
     ▼ pass
Pass 4: Continuity & Consequence
     │ fail → fix → restart Pass 4
     ▼ pass
Chapter Final
```

A chapter is final only when all four passes complete without
failure. There is no shortcut. There is no "good enough."

---

## Pass Timing

| Pass          | When to Run             | Duration                              |
| ------------- | ----------------------- | ------------------------------------- |
| 1. Simulation | Immediately after draft | Fast — binary checks                  |
| 2. Voice      | After Pass 1 clears     | Slow — requires reading aloud         |
| 3. Anti-AI    | After Pass 2 clears     | Medium — mechanical scans + gut check |
| 4. Continuity | After Pass 3 clears     | Medium — cross-reference heavy        |

Do not batch passes across multiple chapters. Finish all four
passes on one chapter before moving to the next. Continuity
errors compound across chapters and become unfixable if left to
accumulate.
