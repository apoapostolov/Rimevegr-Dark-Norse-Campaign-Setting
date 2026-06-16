# Character Arcs — Iron Ledger

**Purpose:** Arc types suited to grimdark military fiction. Each arc
defines a pattern of change (or resistance to change) that the
simulation's constraints can drive naturally. These are not hero's
journeys. They are the shapes that survival, economics, and
proximity carve into people over time.

---

## Arc Design Rules

1. **Arcs are measured in behavior, not revelation.** A character
   does not realize something. A character starts doing something
   differently. The reader infers the realization.

2. **Simulation drives beats.** Arc beats are triggered by
   simulation states — morale thresholds, treasury levels, wound
   timelines, contract outcomes. The arc does not fight the numbers.
   The numbers push the arc forward.

3. **Arcs do not announce themselves.** No character says "I've
   changed." The narrator does not observe growth. The reader
   notices that a common is no longer last in the march line.
   The reader does the work.

4. **Most arcs are not complete by novel's end.** In Cook and
   Abercrombie, character change is slow and partial. A man who
   began as a coward may die slightly less of one. That counts.

5. **Arcs can reverse.** Progress earned in Act 2 can be lost in
   Act 3. The simulation does not protect character development.
   If morale breaks, a man who was growing loyal may desert.

---

## The Six Arc Types

### 1. The Grudging Rise

**The pattern:** A low-status character earns tolerance through
accumulated usefulness. Not heroism. Not a single defining
moment. A series of small proofs — each one insufficient alone,
together sufficient to change the arithmetic.

**Beat structure (across novel):**

| Beat                  | Trigger                                 | What Changes                                                                                       |
| --------------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------- |
| 1. Contempt baseline  | Joining                                 | Last in every line. Double weight. No voice. No seat.                                              |
| 2. First useful act   | Any task competently done               | One Named Man stops avoiding eye contact. Barely perceptible.                                      |
| 3. Witness survival   | Surviving danger without fleeing        | The band acknowledges the character was present. Not praised — noted.                              |
| 4. Inherited position | A man dies or deserts                   | The character fills a gap in the column or at the fire. The gap was not offered — it was occupied. |
| 5. Grudging inclusion | Accumulated evidence                    | Someone hands the character ale without being asked. Someone uses a different name.                |
| 6. Tested             | A crisis where the character could flee | The character stays. Not out of courage. Out of having nowhere else to go.                         |
| 7. Earned place       | End-state                               | The character is no longer last. Not first. Not Named. But present. Counted. Missed if absent.     |

**Simulation integration:**

- Beat 2 triggers when the character's action produces measurable
  gain: successful foraging, weight carried, a fire maintained.
- Beat 4 triggers when `band_manager.py` records a death or
  desertion and the roster shifts.
- Beat 6 triggers when morale drops below 3 and desertions are
  mechanically possible.

**Current assignment:** Lump (observed through Voss's and
Gest's POV — the reader tracks Lump's progress through the
POV characters' shifting assessments, not Lump's interiority)

**Anti-pattern:** Do not compress the arc. If the character earns
tolerance in Chapter 5, the arc has no weight. The arc must
run the full length. Setbacks are mandatory — a moment where
the character is pushed back to an earlier beat by a new failure.

---

### 2. The Erosion

**The pattern:** A competent man worn down by the arithmetic of
what he maintains. Not a fall — a thinning. The man who keeps the
ledger, the man who holds the line, the man whose knees are going.
The arc is the slow subtraction of capacity while responsibility
remains constant or increases.

**Beat structure:**

| Beat                      | Trigger                                               | What Changes                                                                                                                                                                         |
| ------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1. Competence established | Early chapters                                        | The character is the person the band depends on for X. This is shown, not stated.                                                                                                    |
| 2. First cost             | Physical, financial, or psychological                 | The work takes something. A wound that heals slow. A number in the ledger that keeps the man awake.                                                                                  |
| 3. Compensation           | Response to cost                                      | The character develops a workaround. The workaround works but requires effort that was previously unnecessary.                                                                       |
| 4. Accumulation           | Multiple costs stack                                  | The workarounds multiply. The character is spending more energy maintaining capacity than performing the work.                                                                       |
| 5. Visible thinning       | Others notice                                         | A Named Man covers for the eroding character without being asked. This is not kindness. It is the band adapting to a degrading asset.                                                |
| 6. Crisis                 | The work demands capacity the character no longer has | Failure or near-failure. The gap between what the band needs and what the character can provide becomes visible.                                                                     |
| 7. Resolution             | Not heroic                                            | The character either accepts a diminished role, or the band absorbs the loss, or the character dies doing the work one last time — not heroically, but because the work demanded it. |

**Simulation integration:**

- Beat 2 triggers from wound timelines, accumulating exhaustion
  (logistics.py), or morale costs.
- Beat 4 triggers when multiple debts or wounds overlap in
  band_state.yaml.
- Beat 6 triggers during a high-demand contract when the
  character's stats cannot meet the check threshold.

**Current assignments:** Gest (ledger/arithmetic erosion),
Snorri (physical erosion)

---

### 3. The Quiet Betrayal

**The pattern:** A trusted member who was building an exit while
the band assumed loyalty. Not a dramatic reveal. A gradual
realization — by the band, by the reader, or by both — that the
person's calculations diverged from the group's some time ago.

**Beat structure:**

| Beat                    | Trigger                       | What Changes                                                                                                                                                         |
| ----------------------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Integration          | Early chapters                | The character performs competently. Accepted. Trusted with tasks.                                                                                                    |
| 2. Private geometry     | Small moments                 | The character makes choices that serve personal interest and band interest simultaneously. Nobody notices the overlap because both are served.                       |
| 3. Divergence           | A decision point              | The character's interests and the band's interests stop aligning. The character chooses personal, disguised as band service.                                         |
| 4. Evidence accumulates | Others' POV notice            | Small inconsistencies. A pack slightly lighter than expected. A conversation overheard. A route suggestion that serves no obvious tactical purpose.                  |
| 5. Confrontation gap    | The moment someone should ask | Nobody asks. The cost of asking — the trust that would break, the number that would change — is too high.                                                            |
| 6. The act              | Desertion, theft, or trade    | The betrayal happens. It is small, practical, and quietly devastating. Not dramatic. Not a speech. Someone is gone, or something is missing, and the ledger adjusts. |
| 7. Aftermath            | Band absorbs                  | The gap closes. The column adjusts. Gest writes the entry. Life continues because it must.                                                                           |

**Simulation integration:**

- Beat 3 triggers when the character's personal silver or resource
  accumulation diverges from what retainer payments would produce.
- Beat 6 triggers when morale or treasury hits a threshold that
  makes departure mechanically rational.

**Current assignment:** Ubbe (building exit fund), Orm (potential
— arc direction undecided)

**Anti-pattern:** Do not make the betrayal feel like villainy.
The betrayer did arithmetic. The arithmetic said leave. In the
Rimevegr, this is reasonable. The narrator does not judge.

---

### 4. The Competence Trap

**The pattern:** A reliable person assigned to every hard task
until reliability becomes a death sentence. The band unconsciously
loads more onto the person who never fails, until the load is
unsurvivable.

**Beat structure:**

| Beat                  | Trigger                         | What Changes                                                                                                                        |
| --------------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 1. Reliability proven | Combat, barrow, hard task       | The character performs. Others notice. "That was right."                                                                            |
| 2. Default assignment | Next hard task                  | The character is chosen first. Not because of favoritism — because of evidence.                                                     |
| 3. Pattern forms      | Third, fourth, fifth assignment | The character holds every gap. Takes every hard position. The pattern is invisible because it looks like respect.                   |
| 4. Weight shows       | Physical cost                   | Wounds stack. Exhaustion accumulates. The character compensates — shorter sentences, smaller motions, the body economizing.         |
| 5. Trap visible       | Others see but cannot change    | The band cannot afford to stop using the character. The alternative is risking someone less reliable, which costs more if it fails. |
| 6. The break          | One task too many               | Whatever breaks — armor, body, luck — breaks because it was overloaded, not because it was weak.                                    |
| 7. Recalibration      | Band or character               | Either the character sets a boundary (rare, costly), or the band learns what replacement costs.                                     |

**Simulation integration:**

- Beat 3 tracks through command decisions — which characters are
  assigned to combat positions, barrow entries, and hard tasks in
  consecutive chapters.
- Beat 4 triggers from accumulated wound timelines and
  exhaustion modifiers in band_state.yaml.

**Current assignment:** Kell

---

### 5. The Loyalty Test

**The pattern:** A leader whose personal cost of serving the
group conflicts with the group's need. The arc asks: what does
the leader sacrifice, and at what price does the sacrifice stop
being worth it?

**Beat structure:**

| Beat                        | Trigger                                                                  | What Changes                                                                                                                               |
| --------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 1. Authority established    | Early chapters                                                           | The leader commands. The band follows. The mechanism works.                                                                                |
| 2. Personal cost introduced | An old debt, a private agenda                                            | The reader learns the leader carries something older than the band. A blood-debt. A promise. An obligation that pre-dates the current job. |
| 3. Costs conflict           | A decision where band interest and personal obligation point differently | The leader chooses band. But the personal cost is visible — in a silence, in a gesture, in what the leader does not say.                   |
| 4. Escalation               | The personal cost increases                                              | The obligation presses harder. The unchosen path becomes more expensive the longer it waits.                                               |
| 5. The test                 | A moment where the leader must choose decisively                         | Band or self. Both choices are expensive. Neither is clean.                                                                                |
| 6. Resolution               | Not satisfying                                                           | The choice costs exactly what it costs. No redemption. No vindication. The ledger adjusts.                                                 |

**Simulation integration:**

- Beat 3 triggers when the campaign arc requires a route or
  contract decision that conflicts with the captain's agenda.
- Beat 5 triggers during a plot chain climax (Whispering Debt,
  Stolen Ground, or Pale Widow).

**Current assignment:** Voss

---

### 6. The Slow Corruption

**The pattern:** A person who enters with clear principles and
watches those principles erode through the daily arithmetic of
survival. Not dramatic moral collapse. A series of small
concessions — each individually reasonable, together adding up
to someone the character would not have recognized at the start.

**Beat structure:**

| Beat                           | Trigger                                | What Changes                                                                                                                                                          |
| ------------------------------ | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Principle established       | Early behavior                         | The character draws a line — explicit or implicit. They will not do X.                                                                                                |
| 2. First concession            | Survival pressure                      | The line bends. Not broken — adjusted. The character tells themselves the situation was exceptional.                                                                  |
| 3. Normalization               | The adjusted line becomes the baseline | The concession is repeated. It stops feeling like a concession. The new standard is just how things work.                                                             |
| 4. Second concession           | Greater pressure                       | The already-adjusted line bends again. The distance from the original principle is now visible — to the reader, not to the character.                                 |
| 5. Mirror                      | Another character reflects the change  | Someone new — a recruit, a villager, a prisoner — reacts to the character in a way that reveals how far they have moved. The character does not recognize the mirror. |
| 6. The line that does not bend | A final demand                         | Something asks the character to cross the last line. They either cross it or they do not. Either outcome costs everything.                                            |

**Simulation integration:**

- Beat 2 triggers from supply shortages or morale crises that
  make morally questionable actions mechanically optimal (looting
  a village, abandoning wounded, breaking a contract).
- Beat 5 triggers from new character introductions (recruitment
  events) that provide a fresh perspective on the band's behavior.

**Current assignment:** Unassigned — this arc activates
conditionally. It is not pre-assigned but triggers when a
character's simulation-driven decisions accumulate past a
moral threshold. Potential candidates and their activation
conditions:

- **Voss** (authority version) — orders that cost lives for
  margin; activates if three or more men die under avoidable
  circumstances within two contracts.
- **Gest** (ledger version) — the numbers start justifying
  cruelty; activates if treasury arithmetic forces two
  morally compromised decisions in sequence.
- **Petra** (mission version) — compromising the sister-search
  for band survival; activates when Petra delays or abandons
  a concrete lead on her sister's location because the band
  cannot afford the detour. Petra's arc is deliberately
  unassigned at novel start because the sister-search is
  background tension that may or may not escalate into a
  full Slow Corruption depending on whether the simulation
  produces the right pressure.

---

## Arc Anti-Patterns

These arc types do not fit the Iron Ledger voice. Avoid them.

### The Redemption Arc

A bad person becomes good through suffering or love. Rejected:
the narrator does not distinguish good from bad. The narrator
records behavior and cost. Redemption requires moral judgment
the narrative voice does not provide.

### The Mentor-Student Arc

A wise figure teaches a younger one. Rejected: Snorri's advice
at the fire is not mentorship. It is an old man talking because
the ale loosened him. The difference is that mentorship implies
investment. Snorri invested nothing. He stated a fact. The
listener happened to carry it.

### The Chosen-One Arc

Anyone is special or destined. Rejected: the Rimevegr does not
choose anyone. The arithmetic does not care. People survive by
being useful, lucky, or both, and the useful ones outlast the
lucky ones on average.

### The Love Arc

Romantic attachment as primary driver. Rejected: not because
romance cannot exist in the band, but because the voice does not
permit the narrator to describe it. If two people are sleeping
together, the narrator notes the bedroll proximity. The reader
infers. The narrator does not invest in the inference.

### The Revenge Completed Arc

A character pursues vengeance and achieves satisfying closure.
Rejected: Thorne's blood-debt may be settled but the settling
will not feel like satisfaction. It will feel like a transaction
that cost more than anticipated. The ledger closes. The man is
not healed by it.

---

## Arc Interaction Map

Arcs do not operate in isolation. The simulation creates pressure
that pushes multiple arcs simultaneously.

| **State**                | **Arcs affected**                     | **How**                                                                                                                                               |
| ------------------------ | ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Treasury below 20 silver | Loyalty Test, Quiet Betrayal, Erosion | Voss faces hard choices. Ubbe's exit math improves. Gest's numbers get worse.                                                                         |
| Morale below 3           | Grudging Rise, Quiet Betrayal         | Low-status progress freezes — low morale means the band does not notice anyone's contributions. Desertion becomes mechanically rational.              |
| Named Man wounded        | Competence Trap, Erosion              | Another man fills the gap. The filler accumulates load. The wounded man erodes.                                                                       |
| Contract underpaid       | Loyalty Test, Slow Corruption         | Voss chooses between the band's interests and the employer's, setting a precedent.                                                                    |
| Death in the band        | Grudging Rise, Erosion                | Low-status men move up. Equipment redistributes. The living absorb the dead man's work. Everyone's margin thins.                                      |
| Supernatural event       | Multiple                              | Fear-state changes behavior. Thorne's knowledge becomes more valuable. The band's principles are tested by something that does not follow arithmetic. |

---

## Chapter-Level Arc Tracking

For each chapter, identify:

```text
ARC BEATS THIS CHAPTER:
- [Character]: [Arc type], beat [N] → [N+1]
  Trigger: [simulation state that pushed the beat]
  Evidence: [specific behavior change shown in prose]
```

Rules:

- Maximum 2 arc beats per chapter. More dilutes the impact.
- One chapter can advance one arc and show steady state for
  another.
- Not every chapter advances an arc. Some chapters are pure
  logistics. The logistics chapters are the baseline that makes
  arc movements visible by contrast.

---

## Arc Resolution Guidelines

When an arc reaches its final beat:

1. **Do not write a climax scene.** The resolution happens inside
   a normal chapter — a march, a contract, a camp scene. The arc
   ends the same way it progressed: through behavior, not
   announcement.

2. **The reader may not notice.** That is acceptable. The arc's
   final beat is a behavior that has changed enough to be
   different from the first chapter but not enough to be dramatic.
   Re-readers will catch it. First-time readers may only feel it.

3. **Cost the resolution.** Whatever the character gained from
   the arc, the gaining cost something else. A place at the
   fire costs the option of walking away. Kell's reputation
   cost him his body. Gest's ledger cost him the ability to see
   people as anything other than numbers. The cost is the
   resolution's weight.
