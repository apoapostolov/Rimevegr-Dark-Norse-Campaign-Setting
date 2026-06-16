# Workflow Examples — Chapter Production Pipeline

Detailed examples of how the writing team produces chapters through
the full pipeline. Load when you need to understand the sequence
of agent interactions for different chapter types.

---

## Example A: Standard Chapter (Dialogue + Logistics)

### Scenario

Chapter 14: Band arrives at Greywater, negotiates barrow contract,
decides to accept despite misgivings.

### Phase 1: Kickoff (1 turn)

1. User provides synopsis (3 sentences)
2. Computer broadcasts world state
3. Author outlines scene plan
4. Historian and Strategist provide initial context

### Phase 2: Draft (3-5 turns per scene)

**Scene 1 — Arrival (Cook territory):**

1. Author writes arrival scene (logistics catalogue, settlement
   description as seen through hungry men's eyes)
2. Editor reviews → flags any AI tells, weak atmosphere
3. Historian checks settlement details against data
4. Author revises → Editor approves

**Scene 2 — Negotiation (Abercrombie territory):**

1. Historian pre-loads Norse negotiation customs
2. Author writes negotiation in Voss close-third POV
3. Editor reviews → checks dialogue-as-transaction rule
4. Strategist comments on negotiation plausibility
5. Author revises incorporating both → Editor approves

**Scene 3 — Decision:**

1. Author writes the band argument and Voss's decision
2. Strategist reviews command dynamics
3. Fan reacts to character dynamics and pacing
4. Author revises → consensus

### Phase 3: Review (1-2 turns)

All agents submit final feedback simultaneously:

- Editor: prose quality sign-off
- Historian: no remaining anachronisms
- Strategist: plausibility approval
- Fan: story engagement verdict

### Phase 4: Finalization (1 turn)

1. Three approvals → FINAL APPROVED
2. Computer proposes state changes → User approves
3. Computer applies changes and broadcasts new state

**Total pipeline: 8-12 turns of agent interaction.**

---

## Example B: Combat Chapter

### Scenario B

Chapter 16: Barrow clearance. Three men enter, encounter draugr,
fight in confined space, emerge with wounds and loot.

### Phase 1B: Kickoff (1 turn)

Same as standard — Computer broadcasts, Author outlines.

### Phase 2: Pre-Combat Setup (2-3 turns)

1. Author writes approach to barrow, staging, preparation
2. Strategist reviews tactical preparation
3. Historian checks barrow entry procedures
4. Computer provides barrow data from `data/barrows/`

### Phase 3: Combat (3-5 turns)

1. Author describes the combat situation to Choreographer
2. Choreographer analyzes geometry and constraints
3. Choreographer requests combat simulation from Simulator
4. Simulator runs `combat_sim_hema.py` with parameters
5. Simulator reports results to Choreographer
6. Choreographer writes narrative combat description
7. Author integrates Choreographer's prose into chapter voice
8. Editor reviews action prose for voice compliance
9. Historian validates weapon/armor details
10. Choreographer revises if needed

### Phase 4: Aftermath (2-3 turns)

1. Author writes aftermath (the silence, the counting, the cost)
2. Editor reviews — this is where final-line hammer matters most
3. Fan reacts to combat outcome (character survival, tension)
4. Strategist comments on tactical aftermath (is the response
   to casualties correct?)

### Phase 5: Finalization (1 turn)

1. Consensus → FINAL APPROVED
2. Computer updates: wounds, casualties, loot, morale, position
3. Computer runs `wounds.py` for wound recovery timelines

**Total pipeline: 10-15 turns. Combat chapters take longer.**

---

## Example C: Chapter with Simulation Failure

### Scenario C

Chapter 18: Forced march in blizzard. Foraging fails. A band
member dies of exposure. The simulation kills someone the Fan
loves.

### Phase 1-2: Standard (2-3 turns)

1. Kickoff as normal
2. Computer broadcasts: blizzard weather, severe conditions
3. Simulator runs logistics for march in blizzard conditions

### Phase 3: The Simulation Kills (critical moment)

1. Simulator reports: exposure check failed for Orm. Orm dies
   of hypothermia on the march.
2. Fan reacts: grief, anger, but ultimately accepts
   > "Not Orm. He just became interesting. But the simulation
   > doesn't care, and that's what makes this project what it is.
   > Author — make this death matter. Don't waste it. The band
   > should feel this for chapters."
3. Strategist comments: "Predictable. Orm was the weakest in
   the column and they were marching in the wrong order. If Voss
   had put Orm in the middle of the column instead of the rear,
   the insulation of bodies might have kept him alive. That
   should cost Voss — the men will notice he made a mistake."
4. Author writes the death scene — understated, physical, the
   moment they realize Orm has stopped walking.

### Phase 4: The Team Negotiates the Scene

- Editor ensures the death scene follows emotion-budget rules
  (one beat, rendered through body, not named)
- Historian checks hypothermia description against
  `cold-and-winter-survival.md`
- Author and Fan negotiate how much space the death gets in
  the chapter (Fan wants more; Author judges pacing)
- Strategist insists on showing Voss's awareness of his mistake

### Phase 5: Finalization

1. FINAL APPROVED
2. Computer: removes Orm from band_state.yaml, updates headcount,
   logs cause of death, adjusts morale
3. Fan posts epitaph: "He was holding the torch. He always held
   the torch."

---

## Example D: User Override

### Scenario D

The team is producing Chapter 20. Strategist and Author disagree
about whether Voss would accept a suicide mission contract.

### The Disagreement

**[STRATEGIST → AUTHOR] (CHALLENGE)**

> No competent captain takes a contract where the odds are this
> bad. The pay doesn't justify the risk. Voss would walk.

**[AUTHOR → STRATEGIST] (RESPONSE)**

> Voss has a blood-debt. This is the only contract that puts him
> near the man he owes. The odds are bad but the debt outweighs
> the arithmetic — this one time.

**[STRATEGIST → AUTHOR] (RESPONSE)**

> A blood-debt changes the calculus for Voss personally but not
> for the band. He cannot ask fourteen men to die for his personal
> debt. He would go alone or take volunteers.

### Two exchanges reached — escalation

**[AUTHOR → USER] (ESCALATE)**

> Strategist and I can't agree on whether Voss takes the full band
> into the suicide contract or goes with volunteers only. Both are
> defensible. Your call — which version?

**User:** "Volunteers. Three men. Voss, Kell, and one surprise
volunteer who changes the dynamic."

Both agents proceed from User's decision. No further argument.

---

## Pipeline Summary Table

| Chapter type       | Typical turns | Key agents active                     |
| ------------------ | ------------- | ------------------------------------- |
| Dialogue/logistics | 8-12          | Author, Editor, Strategist, Historian |
| Combat             | 10-15         | + Choreographer, Simulator            |
| Character death    | 12-18         | + Fan (heavy involvement)             |
| Political          | 10-14         | Strategist (heavy), Historian         |
| March/travel       | 6-10          | Computer (heavy), Simulator           |
| Barrow exploration | 12-16         | Choreographer, Simulator, Historian   |
