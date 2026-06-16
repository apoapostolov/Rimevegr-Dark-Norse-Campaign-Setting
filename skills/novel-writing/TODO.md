# TODO — Novel-Writing Mega-Skill

**Location:** `skills/novel-writing/`
**Purpose:** Expand the novel-writing skill from a single SKILL.md into
a comprehensive authoring toolkit covering character management, plot
planning, chapter structure, and simulation-to-prose integration.

---

## Current State (Prompt 10 — Complete)

- [x] `SKILL.md` — Core voice specification (Cook-Abercrombie composite)
- [x] `03_VIGNETTES_AND_SCENES.md` — 41 voice-standard vignettes rewritten
- [x] `00_NOVEL_WRITING_PROMPT.md` — Novel authoring mode prompt
- [x] This TODO
- [x] `references/character-bible.md` — Full dossiers for 12 cast members
- [x] `references/character-arcs.md` — 6 arc types with beat structures
- [x] `references/character-archetypes.md` — 10 mercenary archetypes
- [x] `references/dialogue-patterns.md` — Per-character dialogue rules
- [x] `references/chapter-structure.md` — 7 chapter types with templates
- [x] `references/pacing-and-rhythm.md` — Sentence/chapter/act-level pacing
- [x] `references/opening-and-closing-patterns.md` — Opening/closing banks
- [x] `references/plot-planning.md` — Arc templates and interlacing rules
- [x] `references/tension-and-stakes.md` — 7 tension sources, escalation
- [x] `references/consequence-tracking.md` — Registry, standing, drift

## Working Rules

**Cleanup rule:** when asked to clean this file, remove completed prompt dumps
instead of preserving them unless the user explicitly asks for archives.

**Removal rule:** if the user says to remove prompts, tasks, or completed items
from this file, delete them outright. Do not archive them elsewhere unless the
user explicitly asks for an archive.

**Protected template rule:** keep the example prompt template and rule scaffold
in this file unless the user explicitly says to remove the template itself.

**Continuation rule:** if the current prompt or session leaves a clear next
prompt that can be handled without major context drift, continue automatically.
If the next prompt is a materially different undertaking, requires rebuilding a
large context window, or introduces a major codebase/topic shift, it is allowed
to ask the user whether to continue before proceeding.

**Prompt autonomy rule:** AI is allowed to expand a prompt with additional
subtasks, create follow-up prompts or sub-prompts, split or combine prompts, and
modify prompt boundaries when discoveries suggest a better implementation path.
If a better approach changes scope or sequencing in a meaningful way, present
the proposal to the user and ask how to handle development before committing to
the new direction.

## Protected Template

Use this structure when adding a new prompt sequence or expanding this queue:

```md
## Current Focus

- one-sentence mission
- explicit canonical file or system owner

## Scope And Boundaries

- what this pass owns
- what this pass explicitly does not own

## Prompt N — <goal>

Short prompt description.

- [ ] expected file or system result

Validation:

- tests, lint, review passes, or manual checks

## Decision Log

- YYYY-MM-DD: important scope or design decision

## Risks And Blockers

- open risk
- explicit blocker if present
```

Template minimums:

- every active TODO should declare current focus, scope boundaries, prompt
  queue, working rules, and a protected template block
- every prompt should state outputs
- risky prompts should also state validation
- partial completion should be represented by sub-prompts instead of vague
  prose updates
- if scope changes during execution, record it in a decision log or directly in
  the prompt text
- completed prompt dumps can be removed during cleanup, but the protected
  template stays unless explicitly removed by the user

---

## ~~Prompt 8 — Character Bible and Arc Templates~~ DONE

Build the character management layer for long-form fiction.

- [x] Create `references/character-bible.md`
  - Full dossier template: physical description, voice sample, gesture
    inventory, relationships, arc position, tracking fields
  - Populated for 11 cast: Voss (Primary POV), Gest, Kell, Thorne,
    Orm, Petra, Ash, Dalla, Snorri, Ubbe, Dagfinn, Lump (minor)
  - Includes "dead man's file" template and cast interaction rules
- [x] Create `references/character-arcs.md`
  - 6 arc types: Grudging Rise, Erosion, Quiet Betrayal, Competence
    Trap, Loyalty Test, Slow Corruption
  - Each with beat structure, simulation integration, current assignment
  - 5 anti-patterns: Redemption, Mentor-Student, Chosen-One, Love, Revenge
  - Arc interaction map (how simulation states push multiple arcs)
- [x] Create `references/character-archetypes.md`
  - 10 archetypes: Captain by Competence, Ledger-Keeper, Quiet Blade,
    New Blood, Old Campaigner, Caster Tolerated, Deserter, Tyrant,
    Political Animal, Functional Infrastructure
  - Each with behavioral signature, dialogue pattern, hierarchy role
  - Pairing map (10 friction-generating combinations)
  - New character generation checklist
- [x] Create `references/dialogue-patterns.md`
  - Per-character rules for all 11 cast members
  - Universal rules: said-only tags, beat tags, silence defaults
  - Scene construction templates (two-person, group)
  - 10 forbidden dialogue patterns with rationale

---

## ~~Prompt 9 — Chapter Planning Framework~~ DONE

Build the structural tools for planning and writing chapters.

- [x] Create `references/chapter-structure.md`
  - Chapter anatomy: opening (physical grounding, 1-3 sentences), body
    (2-4 scenes or 1 extended scene), closing (cost accounting)
  - Chapter types: March Chapter, Camp Chapter, Contract Chapter, Combat
    Chapter, Settlement Chapter, Barrow Chapter, Transition Chapter
  - Each type: structural template, simulation requirements, POV
    recommendations, pacing targets
  - Scene transition rules: hard breaks vs. continuous, time compression
    techniques
- [x] Create `references/pacing-and-rhythm.md`
  - Chapter-level pacing: when to compress time (march montage), when
    to expand (combat, confrontation, the Hush)
  - Sentence-level rhythm patterns: the Cook catalogue (list followed
    by silence), the Abercrombie pivot (setup then reversal), the
    loaded pause (dialogue → silence → gesture)
  - Act-level pacing across a contract arc: approach → negotiation →
    march → event → aftermath → cost
- [x] Create `references/opening-and-closing-patterns.md`
  - Bank of opening sentence patterns that work for each chapter type
  - Bank of closing patterns (cost accounting, silence, the road ahead)
  - Anti-patterns: openings that start with weather decoration, closings
    that moralize, transitions that summarize

---

## ~~Prompt 10 — Plot Planning and Arc Management~~ DONE

Build the tools for managing multi-chapter and multi-arc narrative.

- [x] Create `references/plot-planning.md`
  - Contract arc template: 3-8 chapters, from hiring through payment
  - Political arc template: faction dynamics, alliance/betrayal beats
  - Supernatural arc template: escalation pattern (whisper → event →
    crisis → resolution/cost)
  - Interlacing rules: how to weave arcs together without losing the
    logistical baseline
- [x] Create `references/tension-and-stakes.md`
  - Tension sources specific to mercenary fiction: the ledger gap,
    the morale cliff, the supply countdown, the rival band, the
    employer's betrayal, the internal grievance, the supernatural debt
  - How simulation state creates narrative tension automatically
    (food at 3/14 = tension without author effort)
  - Escalation patterns: how to stack tensions within a single arc
- [x] Create `references/consequence-tracking.md`
  - Long-term consequence registry: every major decision tracked across
    chapters with expected narrative payoff windows
  - Settlement standing as plot memory (the village the band stripped =
    closed gates 10 chapters later)
  - Character relationship drift: how small moments accumulate into
    arc-level changes (who sits where at the fire across 20 chapters)
  - The "empty hex" principle: consequences are permanent, settlements
    do not quietly restore

---

## Prompt 11 — Simulation-to-Prose Deep Integration — Complete

Deepen the connection between game simulation and narrative output.

- [x] Create `references/simulation-rendering-guide.md`
  - Detailed rendering rules for every simulation system: weather,
    food, morale, combat, injury, money, contracts, settlements,
    travel, encounters, supernatural events
  - For each system: what the numbers mean in prose, how to show
    rather than tell, specific sentence patterns for common states
    (e.g., Morale 2/Wavering = "shorter answers, longer silences")
  - Forbidden renderings: never state a number directly in prose,
    never say "morale was low," never use game terminology
- [x] Create `references/combat-to-prose.md`
  - How to convert combat_sim.py output into fiction: hit locations
    as physical experience, wound severity as immediate cost, the
    difference between a fight that takes 30 seconds and one that
    takes 5 minutes
  - Violence rendering rules: physical impact over choreography,
    sound over visual, aftermath over the moment of killing
  - Mass combat vs. small fight rendering differences
- [x] Create `references/weather-as-character.md`
  - Weather in the Rimevegr is not atmosphere — it is a physical
    antagonist. How to render each weather type as something that
    acts on the characters' bodies, gear, morale, and movement
  - Season-specific rendering: Long Dark prose (short sentences,
    cold details, the weight of grey sky) vs. Long Summer prose
    (mud instead of ice, different exhaustion)

---

## Prompt 12 — Anti-AI Detection and Quality Assurance

Build the quality gate that ensures all output passes as human-written.

- [x] Create `references/anti-ai-detection-library.md`
  - 5-category catalogue: structural (paragraph sameness, three-beat,
    mirror openings, symmetric dialogue), lexical (copula avoidance,
    elegant variation, hedging, inflated verbs, AI vocabulary),
    rhythmic (em-dash, sentence-length, conjunction addiction),
    content (generic positivity, false depth, therapeutic framing,
    significance inflation, negative parallelism), dialogue
    (thesis statements, equal eloquence, wrap-up lines)
  - Each tell: detection method, failure example, fix example
  - 20-item self-audit checklist with pass thresholds
- [x] Create `references/rewrite-calibration-examples.md`
  - 10 before/after pairs across 4 failure types
  - Voice failure (mood fog, lost POV anchor)
  - Structure failure (paragraph sameness, symmetric dialogue)
  - Tell failure (copula+variation, hedging+positivity, em-dash+parallelism)
  - Subtext failure (thesis dialogue, emotional explanation,
    over-explained backstory)
  - Quick-reference fix-pattern table
- [x] Create `references/review-checklist.md`
  - 19-item chapter review checklist across 6 sections
  - A: Voice consistency (5), B: Simulation accuracy (3),
    C: Character continuity (3), D: Dialogue fidelity (2),
    E: Anti-AI audit (4), F: Physical/temporal grounding (2)
  - Pass/fail criteria per item, gate rule for chapter advancement

---

## Prompt 13 — Revision Workflow

Build the four-pass revision system for draft chapters.

- [x] Create `references/revision-workflow.md`
  - Pass 1: Simulation accuracy (roster, wounds, weather, food,
    silver, calendar, contracts, settlement cross-checks)
  - Pass 2: Voice calibration (POV anchor, sentence rhythm,
    register, physical grounding, understatement, dialogue voice)
  - Pass 3: Anti-AI audit (lexical scan, structural scan, content
    scan, fresh-eyes pass)
  - Pass 4: Continuity and consequence (wound persistence, economic
    continuity, relationship tracking, arc micro-progression,
    foreshadowing/payoff audit, closing cost accountability)
  - Workflow diagram, pass timing table, exit criteria per pass

---

## Prompt 14 — Series Bible

Cross-book continuity tools for a multi-volume series.

- [x] Create `references/series-bible.md`
  - Canonical carry-forward tables: ledger (economic), roster
    (cast), map (settlements/factions), Veil (supernatural)
  - Lock rules per category (no quiet resets between volumes)
  - Volume hand-off protocol: state snapshot, consequence
    migration, arc stage freeze, timeline reconciliation, map
    update
  - Cross-volume continuity checks (5): opening state match,
    consequence acknowledgment, character voice consistency,
    tone calibration, supernatural continuity
  - Rules for allowed between-volume changes (time gaps,
    off-page events, minor NPC turnover, equipment wear)
  - Series-level arc planning (band identity, Veil, political
    landscape, the ledger itself)

---

## Prompt 15 — Adaptation Notes

Voice and pacing guidance for translating the prose to other
media.

- [x] Create `references/adaptation-notes.md`
  - Part 1: Audiobook — narrator selection criteria (flat affect,
    contained intensity, rhythm awareness), pacing rules (silence
    after short sentences, combat acceleration, ledger-closing
    slowdown), audio-specific adaptations
  - Part 2: Screenplay — translation solutions for physical
    grounding (camera language), understatement (performance
    direction), the ledger (Gest-writing visual motif),
    consequence persistence (production design), subtext-to-
    composition rules, sound design as voice substitute,
    controlled dialogue expansion (4 rules), cut list
  - Part 3: Cross-media constants (6 non-negotiable elements
    that survive any adaptation)

---

## Prompt 16 — Consistency Audit Fixes

Resolve contradictions, gaps, and redundancies found during the
full-skill audit (2025-07-18).

### Critical — Contradictions

- [x] **C1: Dalla's triple role (cook / seidr-wife / healer)**
  - character-archetypes.md + dialogue-patterns.md → cook only
  - simulation-rendering-guide.md → seidr-wife, runecarver,
    supernatural interpreter
  - combat-to-prose.md → healer (medical, non-magical)
  - pantheon.md + series-bible.md → seidr practitioner who
    speaks to the dead
  - **Fix:** Decide canonical role stack. Update character-bible
    entry (currently omits seidr entirely). Reconcile archetype
    assignment — she may need dual archetype (Functional
    Infrastructure + partial Caster).

- [x] **C2: Supernatural interpreter — Thorne vs Dalla**
  - plot-planning.md, dialogue-patterns.md, chapter-structure.md
    → Thorne is the band's supernatural interpreter
  - simulation-rendering-guide.md, weather-as-character.md →
    Dalla is the supernatural lens, events filter through her
  - pantheon.md → Both have distinct roles (Thorne reads runes,
    Dalla has seidr/speaks to dead) but the rendering pipeline
    only names Dalla
  - **Fix:** Define the division of labor explicitly. Add a
    "Supernatural Rendering Pipeline" section or amend both
    simulation-rendering-guide and weather-as-character to
    include Thorne's rune-reading alongside Dalla's seidr.

- [x] **C3: Morale scale — 1-5 vs 1-6**
  - simulation-rendering-guide.md → 1-5 (Keen / Steady /
    Shaken / Wavering / Broken) with full rendering table
  - tension-and-stakes.md → references "1-6 scale"
  - character-arcs.md → "morale below 3" (no scale stated)
  - **Fix:** Align to 1-5 (the detailed rendering guide is
    canonical). Correct tension-and-stakes reference.

- [x] **C4: Contract arc phase names and sequence**
  - plot-planning.md → Contact / Negotiation / Approach /
    Execution / Complication / Resolution
  - pacing-and-rhythm.md → Approach / Negotiation / March /
    Event / Aftermath / Settlement
  - Different names, different order, different functional
    descriptions
  - **Fix:** Unify into one canonical 6-phase sequence used by
    both files. One file defines structure, the other defines
    pacing per phase.

- [x] **C5: Band name — undefined / inconsistent**
  - simulation-rendering-guide.md → "White Hrafn" (only
    occurrence in entire project)
  - tension-and-stakes.md → "the Rimevegr" used as if band
    name (Rimevegr is the land, not the band)
  - No canonical band name established in setting bible,
    character bible, novel prompt, or SKILL.md
  - **Fix:** Decide band name (or confirm "the band" is
    sufficient and remove "White Hrafn"). Update all
    references.

### High — Gaps That Block Writing

- [x] **G1: Lump missing from character-archetypes.md**
  - Extensive dialogue profile exists in dialogue-patterns.md
  - Assigned Grudging Rise arc in character-arcs.md
  - Zero presence in character-archetypes.md — no archetype,
    no pairing friction, no generation checklist entry
  - **Fix:** Add Lump as a holder (likely New Blood or a
    custom non-combatant variant). Add to pairing map.

- [x] **G2: Dalla's character-bible entry omits seidr**
  - character-bible.md heading: "Dalla — Cook"
  - No mention of seidr, speaking to the dead, supernatural
    role, or rune-work
  - pantheon.md + series-bible.md both describe her seidr
  - **Fix:** Update Dalla's bible entry after resolving C1.

- [x] **G3: Petra has no assigned arc**
  - character-arcs.md names her as Slow Corruption candidate
    ("compromising the sister-search for band survival") but
    arc is "Unassigned"
  - **Fix:** Either assign Petra's arc or document her as
    deliberately unassigned with reasoning.

- [x] **G4: SKILL.md sentence targets not referenced anywhere**
  - 60% default (10-18w), 25% short (2-7w), 15% long (25-40w)
  - pacing-and-rhythm.md covers sentence rhythm through named
    patterns (Cook Catalogue, Abercrombie Pivot, etc.) but
    never references the quantitative targets
  - **Fix:** Add a bridge section in pacing-and-rhythm.md that
    maps named patterns to the SKILL.md distribution targets.

- [x] **G5: Split-sentence negative missing from anti-AI library**
  - SKILL.md Part 6 Rule 3: "Split-sentence negative ('It is
    not X. It is Y.') is a hard AI tell"
  - Not included in anti-ai-detection-library.md's 20-item
    checklist
  - **Fix:** Add as item 21 or fold into existing Category 4.

### Medium — Cross-Reference and Naming Issues

- [x] **M1: Broken filename in review-checklist.md**
  - References `opening-and-closing.md` — actual file is
    `opening-and-closing-patterns.md`

- [x] **M2: TODO.md architecture tree — 4 wrong filenames**
  - `opening-and-closing.md` → `opening-and-closing-patterns.md`
  - `simulation-rendering.md` → `simulation-rendering-guide.md`
  - `anti-ai-detection.md` → `anti-ai-detection-library.md`
  - `rewrite-calibration.md` → `rewrite-calibration-examples.md`

- [x] **M3: Pantheon oath-phrases not linked to dialogue-patterns**
  - pantheon.md defines character-specific invocations (Thurr's
    cracked hands, Odynn's rope, Hael's chair)
  - dialogue-patterns.md has per-character voice rules but no
    oath/invocation guidance
  - **Fix:** Add oath usage to relevant character profiles in
    dialogue-patterns.md.

- [x] **M4: No cross-references between overlapping files**
  - simulation-rendering-guide.md and weather-as-character.md
    cover the same 8 weather states with no "see also"
  - simulation-rendering-guide.md and combat-to-prose.md
    duplicate wound severity tables, stance tables, maneuver
    lists, and conditions
  - **Fix:** Add cross-references. Designate one file as
    canonical per topic, other file references it.

- [x] **M5: `calendar_events.txt` referenced but undocumented**
  - revision-workflow.md Pass 1 references this file
  - No documentation of format or location
  - **Fix:** Document or correct the reference.

- [x] **M6: `settlements.yaml` path unspecified in skill docs**
  - Several reference files cite `settlements.yaml` without
    path — it lives in `data/settlements.yaml`, outside the
    skill's `references/` directory
  - **Fix:** Add explicit relative paths.

### Low — Redundancy (Maintenance Cost)

- [x] **R1: Wound severity table duplicated**
  - Identical ranges (Scratch 1-3, Light 4-7, Serious 8-11,
    Critical 12-15, Mortal 16+) in both simulation-rendering-
    guide.md and combat-to-prose.md
  - **Fix:** Keep in combat-to-prose.md (specialist doc),
    reference from simulation-rendering-guide.md.

- [x] **R2: HEMA stances duplicated**
  - Both files cover Aggressive/Balanced/Defensive/Low Guard
    with overlapping but not identical descriptions
  - **Fix:** Same as R1 — combat-to-prose.md owns stances.

- [x] **R3: Maneuver lists duplicated**
  - 12 maneuvers covered in both files
  - **Fix:** Same approach.

- [x] **R4: Food supply states duplicated**
  - simulation-rendering-guide.md and tension-and-stakes.md
    both describe supply countdown narratively
  - **Fix:** Cross-reference instead of duplicate.

- [x] **R5: The Hush described in 5 files**
  - plot-planning.md, pacing-and-rhythm.md, simulation-
    rendering-guide.md, weather-as-character.md, tension-
    and-stakes.md
  - **Fix:** weather-as-character.md is canonical. Others
    should reference it.

### Not Yet Covered — Areas to Develop

- [x] **N1: Scene-level transition guidance**
  - Added `scene-transitions.md` — transition types (time skip,
    location change, focus shift, continuous), hard/soft breaks,
    transition anchors, pacing rules, common failures.

- [x] **N2: POV character selection logic**
  - Added `pov-selection-logic.md` — three-narrator system,
    switch triggers and anti-triggers, distribution rules,
    chapter type matrix, awareness gaps.

- [x] **N3: Exposition delivery and world-building pacing**
  - Added `exposition-pacing.md` — information budget per
    chapter type, four delivery methods (transaction,
    correction, contrast, ritual), pacing rules, exposition
    debt tracking, anti-patterns.
    across chapters — how much new information per chapter,
    when to trust the reader, how to avoid info-dumps in
    settlement chapters.

- [x] **N4: Managing simultaneous storylines**
  - Added `storyline-management.md` — band split handling,
    timeline tracking with physical markers, intercut patterns,
    check-ins, reunion protocol, parallel event narration,
    consistency tracking, structural limits.

- [ ] **N5: Chapter-to-chapter connective tissue**
  - How the end of one chapter and the start of the next
    relate — time gap handling, information continuity,
    maintaining momentum across a chapter boundary. The
    series-bible covers book-to-book; nothing covers
    chapter-to-chapter.

---

## Skill Architecture (Target)

```text
skills/novel-writing/
├── SKILL.md                          # Core voice (done)
├── TODO.md                           # This file (done)
├── references/
│   ├── character-bible.md            # Prompt 8
│   ├── character-arcs.md             # Prompt 8
│   ├── character-archetypes.md       # Prompt 8
│   ├── dialogue-patterns.md          # Prompt 8
│   ├── chapter-structure.md          # Prompt 9
│   ├── pacing-and-rhythm.md          # Prompt 9
│   ├── opening-and-closing-patterns.md  # Prompt 9
│   ├── plot-planning.md              # Prompt 10
│   ├── tension-and-stakes.md         # Prompt 10
│   ├── consequence-tracking.md       # Prompt 10
│   ├── simulation-rendering-guide.md # Prompt 11
│   ├── combat-to-prose.md            # Prompt 11
│   ├── weather-as-character.md       # Prompt 11
│   ├── anti-ai-detection-library.md  # Prompt 12
│   ├── rewrite-calibration-examples.md  # Prompt 12
│   ├── review-checklist.md           # Prompt 12
│   ├── revision-workflow.md          # Prompt 13
│   ├── series-bible.md              # Prompt 14
│   ├── adaptation-notes.md          # Prompt 15
│   ├── pantheon.md                   # World-building
│   ├── medieval-skills-and-authenticity.md  # Prompt 18
│   ├── scene-transitions.md          # Prompt 19 (N1)
│   ├── pov-selection-logic.md        # Prompt 19 (N2)
│   ├── exposition-pacing.md          # Prompt 19 (N3)
│   └── storyline-management.md       # Prompt 19 (N4)
```
