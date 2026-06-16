# Chapter Review Checklist

Run after every complete chapter draft. Each item is pass/fail.
A chapter must pass all items before it can be considered final.
Failing items require targeted rewrite, not full redraft.

---

## Section A: Voice Consistency (5 items)

### A1. POV Anchor

**Check:** Every paragraph is filtered through the declared
POV character. No omniscient slips ("the camp was tense" instead
of "Voss looked at the camp and counted the men who were not
sleeping").

**Pass:** Zero omniscient sentences.

**Fail:** Any sentence that describes something the POV character
cannot perceive, or that summarizes the inner state of another
character without observable evidence.

### A2. Sentence Rhythm Variation

**Check:** Measure word count for ten consecutive sentences
at three random points in the chapter. Compute standard deviation.

**Pass:** StdDev > 4 at all three points.

**Fail:** Any point with StdDev < 4 indicates AI sentence-length
monotony. Rewrite that section with deliberate rhythm breaks.

### A3. Register Consistency

**Check:** The prose does not slip into modern idiom, academic
language, or therapeutic vocabulary. No "she needed to process
that," no "the situation escalated," no "he was being proactive."

**Pass:** Zero register breaks per chapter.

**Fail:** Any modern phrase that would sound wrong in a Viking
Age camp.

### A4. Physical Grounding Density

**Check:** Every page has at least one sentence grounded in a
physical sense: what something looks, sounds, smells, tastes,
or feels like against the body.

**Pass:** Every page has 1+ physical-sense detail.

**Fail:** Any page that runs on abstraction, emotion-words, or
summary without a concrete sensory anchor.

### A5. Understatement Ratio

**Check:** The worst events in the chapter are described in the
fewest words. Battle aftermath gets short sentences. A man dying
gets one line. Camp logistics get longer treatment.

**Pass:** The most violent or emotional moment uses less prose
per beat than the surrounding mundane context.

**Fail:** The violent/emotional moment is the longest paragraph.
That is AI significance-inflation.

---

## Section B: Simulation Accuracy (3 items)

### B1. State Consistency

**Check:** The chapter's opening state matches the simulation
outputs for the current in-game date. Morale, food stores,
treasury, weather, roster count, wound states, contract status.

**Pass:** All narrative state markers match simulation data.
No character appears who is dead. No food is described when
stores are at zero. No sunshine when the weather system says
rime storm.

**Fail:** Any contradiction between narrative and simulation
state.

### B2. Combat Fidelity

**Check:** If the chapter contains combat, the outcomes match
a `combat_sim.py` run. Wounds appear on the correct locations.
Stances are rendered as character behavior. Maneuvers correspond
to weapon types. Stamina depletion maps to prose-rhythm
deceleration.

**Pass:** Combat outcomes aligned with simulation. HEMA
mechanics visible in prose without being named.

**Fail:** Any fight outcome that contradicts simulation results,
or any HEMA mechanic mentioned by game name ("he performed a
half-sword technique").

### B3. Ledger Accountability

**Check:** The chapter's closing section references the current
economic state. Silver spent or earned. Food consumed. Any
cost-event that occurred. The ledger is never more than one
chapter behind.

**Pass:** The closing acknowledges today's cost in concrete
terms (silver, food, men injured, time spent).

**Fail:** The chapter ends without any economic grounding.

---

## Section C: Character Continuity (3 items)

### C1. Roster Accuracy

**Check:** Every Named Man who appears in the chapter is alive,
present, and in the correct physical state. Wounded characters
show their wounds. Characters sent on detachment are absent.

**Pass:** Zero ghost appearances (dead/absent characters acting).
Wounds persist across scenes.

**Fail:** A character appears clean who was wounded last chapter.
A character speaks who was sent to scout. A dead character is
referenced as alive.

### C2. Voice Differentiation

**Check:** Cover dialogue attributions and read three dialogue
exchanges. Each character should be identifiable from word choice,
sentence length, and speech habits alone.

**Pass:** 3/3 correct blind identifications.

**Fail:** Any character whose dialogue is interchangeable with
another's. See `dialogue-patterns.md` for each character's
speech profile.

### C3. Arc Progression

**Check:** At least one named character's arc has advanced one
micro-step. This is not a dramatic beat — it is a small change:
Kell's temper is slightly shorter. Gest's calculations are a
little more frantic. Dalla volunteers something she would not have
said two chapters ago.

**Pass:** One identifiable micro-progression in at least one
character tracked in `character-arcs.md`.

**Fail:** The entire cast is in the same state they were at
chapter start. Static characters across a full chapter indicate
padding.

---

## Section D: Dialogue Fidelity (2 items)

### D1. Talk Budget

**Check:** Total dialogue does not exceed 30% of the chapter
word count. Mercenaries do not talk much. Most communication
is through action, orders, and silence.

**Pass:** Dialogue word count divided by total word count < 0.30.

**Fail:** Dialogue-heavy chapter that sounds like a stage play
rather than a military chronicle.

### D2. Silence Presence

**Check:** At least one exchange in the chapter includes a
meaningful silence — a question that gets no verbal answer, a
statement followed by someone walking away, a pause that carries
more weight than words.

**Pass:** One or more silence-beats in dialogue.

**Fail:** Every question gets an answer. Every statement gets
a reply. No one is ever too tired, angry, or suspicious to
respond.

---

## Section E: Anti-AI Audit (4 items)

### E1. Lexical Scan

**Check:** Run the searches from `anti-ai-detection-library.md`:
copula substitutes, hedging words, AI vocabulary, negative
parallelisms.

**Pass:** Zero copula substitutes. Max 1 hedge per page. Zero
AI vocabulary words. Max 1 negative parallelism per chapter.

**Fail:** Any threshold exceeded. Fix with targeted word-level
replacement.

### E2. Structural Scan

**Check:** Paragraph shapes, rule-of-three frequency, mirror
openings, dialogue symmetry.

**Pass:** Per page: max 1 triple-list, max 1 repeated opening
pattern. No dialogue exchange with all turns the same length.

**Fail:** Any pattern detected. Fix by restructuring the
affected paragraphs.

### E3. Content Scan

**Check:** Generic positivity, false depth, therapeutic framing,
significance inflation. Check last sentences of dark passages.
Check for "realized/understood" epiphanies.

**Pass:** Zero silver-lining endings. Zero epiphanies. Zero
therapeutic vocabulary.

**Fail:** Any softened ending or manufactured insight. Cut or
rewrite.

### E4. Fresh-Eyes Pass

**Check:** Read the chapter as a stranger. Does any passage
_sound_ like it was generated? This is the gut check. Even if
it passes all mechanical checks, if a paragraph sounds like an
AI wrote it, it fails.

**Pass:** No passage triggers the "this sounds generated"
instinct.

**Fail:** Rewrite the flagged passage from scratch using the
calibration examples in `rewrite-calibration-examples.md`.

---

## Section F: Physical and Temporal Grounding (2 items)

### F1. Opening Grounding

**Check:** The chapter opens with a physical detail — weather,
body state, a sound, a smell, the position of the sun. Not a
thought, not a theme, not an abstraction.

**Pass:** First sentence contains a physical observation.

**Fail:** Opening with reflection, mood, or summary. See
`opening-and-closing-patterns.md` for approved patterns.

### F2. Closing Accountability

**Check:** The chapter closes with cost accounting — what
happened today in concrete terms. Silver spent, food consumed,
miles marched, men hurt, time lost. The ledger closes the day.

**Pass:** Final paragraph references at least two concrete
costs from the chapter's events.

**Fail:** Closing on a thought, a mood, or a thematic beat
without grounding in today's arithmetic.

---

## Scoring Summary

| Section                        | Items  | Weight   |
| ------------------------------ | ------ | -------- |
| A. Voice Consistency           | 5      | Core     |
| B. Simulation Accuracy         | 3      | Core     |
| C. Character Continuity        | 3      | Core     |
| D. Dialogue Fidelity           | 2      | Standard |
| E. Anti-AI Audit               | 4      | Core     |
| F. Physical/Temporal Grounding | 2      | Standard |
| **Total**                      | **19** |          |

**Gate rule:** All Core items must pass. One Standard item may
fail with a note for next revision. Two Standard failures
require rewrite before the chapter advances.
