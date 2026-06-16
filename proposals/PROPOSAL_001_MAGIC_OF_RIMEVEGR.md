# Proposal 001 — The Magic of Rimevegr: Supernatural Deepening

## Status

Draft — pending review.

## Problem Statement

The Rimevegr's supernatural layer is mechanically functional but
thematically shallow. Three magic traditions exist (galdr, seiðr,
wyrd-reading) with rank-by-rank cost tables and success formulas, but
they read like game rules rather than a lived magical reality. The
system lacks:

1. **Internal contradictions** — real magical traditions are messy,
   disputed, and politically weaponized. Ours are clean taxonomies.
2. **Integration in daily life** — magic is treated as a specialist
   activity. In a world where the Veil cracked, magic would seep into
   every household: birth rites, death rites, bread-baking, ironwork,
   navigation, animal husbandry.
3. **Political and social depth** — we track "Dark Arts Level" as
   a settlement integer. In reality, magic would be a lever of power:
   who controls the galdr-worker controls the ward-line, the crop
   blessing, the curse deterrent. Seiðr-wives would be power brokers,
   not hired hands.
4. **Differentiation of magical effects** — all three traditions
   currently feel like "roll, spend WIL, get effect." They need
   distinct phenomenology: galdr should feel like carving, seiðr like
   drowning, wyrd-reading like vertigo.
5. **Encoded mysteries** — the hidden event system uses CJK encoding
   for plot spoilers, but the supernatural itself has no deep mysteries
   that reward re-reading. The Hush is the sole exception.

## Audit Summary

### What's Solid

| Element | Status | Location |
| --- | --- | --- |
| Galdr mechanics (5 ranks, costs, failure cascade) | Complete | 04\_SIMULATION\_RULES L2440-2475 |
| Seiðr mechanics (5 ranks, costs, trance rules) | Complete | 04\_SIMULATION\_RULES L2475-2510 |
| Wyrd-reading mechanics (5 ranks, costs) | Complete | 04\_SIMULATION\_RULES L2508-2537 |
| Veil Ceiling prose rule | Complete | 01\_SETTING\_BIBLE L703-747 |
| Draugr definition and ambiguity framework | Complete | 16\_DICTIONARY L760-768 |
| Dark Arts Level system (settlements) | Complete | 04\_SIMULATION\_RULES L3048-3082 |
| Named practitioners (Ash, Thorne, Ragnhild, Cave-Woman) | Partial | scattered |
| The Hush (atmospheric rendering) | Solid | 16\_DICTIONARY L1432-1438 |
| Campaign supernatural chain (EVT\_001-012) | Scoped | 11\_CAMPAIGN\_ARCS |

### What's Missing or Shallow

| Gap | Impact |
| --- | --- |
| No folk magic layer (everyday superstition with mechanical teeth) | Magic feels like a specialist menu, not a lived world |
| No contraband/forbidden knowledge economy | Dark arts has no supply chain |
| No magic-as-political-leverage system beyond Dark Arts integer | Jarls and unions can't weaponize magic meaningfully |
| No differentiated sensory phenomenology per tradition | All three traditions feel the same in prose |
| No deep mysteries with encoded resolution paths | Hidden content is plot-spoiler, not lore-mystery |
| No cost-of-knowledge theme (knowing always hurts) | Wyrd-reading is too clean |
| No internal contradictions between traditions | Practitioners never disagree about what magic IS |
| No magic corruption / long-term practitioner effects | Seiðr "changes you" but no tracked degradation |
| Creatures undefined: haugbui, aptrgangr, mara, land-wights, nykr | Bestiary is placeholder stubs |
| No ritual structure (when, where, what materials, what witnesses) | Magic has no ceremony, just mechanics |
| No magic-in-trade (enchanted goods, rune-marked tools, ward-stones) | Economy ignores supernatural goods |

## Proposal: New Document `08_MAGIC_OF_RIMEVEGR.md`

A comprehensive supernatural reference document covering everything the
numbered docs currently scatter across 8+ files. Not a replacement —
a consolidation and deepening. The numbered docs keep their mechanical
tables; `08_MAGIC_OF_RIMEVEGR.md` owns the lore, phenomenology,
contradictions, social rules, and mysteries.

### Document Outline

#### Section 1 — The Cracking and Its Consequences

What the Cracking actually did to the world's supernatural fabric.
Not one clean theory — three competing explanations held by different
groups, all partially true, all partially wrong:

- **The Galdr-Workers' Theory:** The gods withdrew their protection and
  the runes they left behind are decaying echoes. Magic is a finite
  resource being consumed. Every casting burns a thread that cannot be
  rewoven. Galdr-workers are custodians of a dying art.
- **The Seiðr-Wives' Theory:** The gods did not leave — they were
  devoured. Something ate them and now wears their silence. The dead
  know this. The living sense it. Seiðr-practitioners commune with
  what remains, and what remains is frightened.
- **The Common View:** The sky broke, the cold came, the dead walk.
  It doesn't matter why. What matters is whether the rune-ward holds
  tonight.

Each theory has evidence supporting it and evidence contradicting it.
The truth is CJK-encoded in `data/hidden/magic_truth.txt`.

#### Section 2 — The Three Traditions: Phenomenology

Not what they do (that's in `20_SIMULATION_RULES.md`) but what they
feel like — to the practitioner, to witnesses, and to the world.

##### Galdr — The Carving

- **Practitioner experience:** A galdr-worker describes the sensation
  as "listening to the stone." The rune already exists inside the
  material — the carver's job is to find it and release it. Wrong
  strokes feel like a tooth being pulled. Right strokes feel like
  nothing at all.
- **Witness experience:** Bystanders feel pressure drop. Hair stands.
  The smell of hot iron without a forge. Minor galdr (wards, marks)
  is unremarkable. Major galdr (binding, cursing, sealing) makes
  observers nauseous and creates a persistent ringing in the ears.
- **Environmental signature:** Frost crystallizes along rune-lines
  even in summer. Carved runes glow faintly in peripheral vision but
  never when looked at directly. Old galdr sites have slightly warmer
  soil temperature year-round.
- **Long-term practitioner cost:** Galdr-workers develop permanent
  scored marks on their hands — not from the carving tool, but from
  the runes themselves. Ash's palms are cross-hatched with white lines
  no blade made.

##### Seiðr — The Drowning

- **Practitioner experience:** Entering trance feels like sinking into
  cold water. The world above recedes. Sounds become distant, then
  invert — whispers become shouts, shouts become whispers. Contact
  with spirits feels like a hand closing over your throat: intimate,
  terrifying, impossible to mistake for imagination.
- **Witness experience:** The seiðr-worker stops blinking. Their eyes
  go glassy. The temperature around them drops measurably. Sometimes
  they speak in a voice that is not theirs — different pitch, different
  accent, sometimes a language no one present knows. The air tastes of
  grave-earth.
- **Environmental signature:** Animals flee the area. Dogs whimper. Fire
  burns blue or refuses to light. Small objects move toward the
  practitioner (not dramatically — a cup shifts, a knife rotates, a
  pouch slides). Lasts for hours after the trance ends.
- **Long-term practitioner cost:** Seiðr-workers begin to see the dead
  everywhere — not hallucinations, but an inability to stop seeing what
  was always there. Ragnhild at Icebreak can no longer enter a room
  without counting the dead who died there. This is why seiðr-workers
  live alone.

##### Wyrd-Reading — The Vertigo

- **Practitioner experience:** Casting lots or reading entrails feels
  like leaning over a cliff edge. The world tilts. Time becomes
  palpable — you can feel the weight of what has already happened
  pressing against what might happen next. True readings arrive as
  certainty, not vision: you simply know, the way you know where
  the ground is.
- **Witness experience:** Nothing visible happens. This is what makes
  wyrd-reading the most socially acceptable tradition. The reader
  shakes some rune-stones, stares at them, and says something cryptic.
  Occasionally their hands tremble or they go very still. No
  supernatural displays.
- **Environmental signature:** None that anyone can measure. This is
  also why some people insist wyrd-reading is fraud. The readers
  themselves cannot explain why it works. They just know when it does.
- **Long-term practitioner cost:** Wyrd-readers develop a fatalism that
  is indistinguishable from depression. They stop making plans. They
  stop arguing. They accept outcomes before they arrive. Thorne's
  habit of "moving his bedroll to the danger side" is not prescience —
  it's resignation. He knows where the trouble will come. He goes to
  meet it because avoiding it changes nothing.

#### Section 3 — Folk Magic: The Household Layer

Magic that ordinary people practice — not galdr, seiðr, or
wyrd-reading, but the inherited habits of a people living under a
broken sky. No mechanical cost, no checks, no ranks. Whether any of
it works is unknown. Everyone does it anyway.

Topics:

- **Birth rites:** A rune scratched in the door-frame when a child is
  born. The mother's blood, specifically. Which rune depends on the
  family's tradition. Some families carve Thurisaz (protection);
  others carve Berkana (growth). Families that carve Isa (ice/stasis)
  are considered unlucky — but their children do survive the Long Dark
  at higher rates, and no one talks about why.
- **Death rites:** The body is oriented north. A coin on each eye (for
  Hael's toll). The mouth is sewn shut with leather thread — not for
  dignity, but to prevent the dead from speaking their way back.
  Families that skip the mouth-sewing are shunned. Everyone has a
  story about what happened to a family that skipped it.
- **Threshold magic:** Salt lines at doorways. Iron nails driven into
  door-frames. A knife buried under the threshold, blade-up. Every
  farmstead has these. No galdr-worker taught it — it predates the
  Cracking. Whether it works is irrelevant; a home without threshold
  iron feels wrong.
- **Seasonal rites:** Midwinter fire (kept burning all Long Dark, if
  it goes out the household is cursed for a year). Spring blood (first
  animal slaughtered, blood poured on the field). Midsummer silence
  (one hour at noon where no one speaks — to avoid drawing the Hush).
- **Food and craft magic:** Bread baked with a rune pressed into the
  dough (feeds the household's luck). Iron quenched in urine (makes
  it harder — true metallurgically, but attributed to magic). Wool
  dyed with specific plants during specific moon phases (the color
  holds better — coincidence or not).
- **Navigation superstition:** Never camp near a barrow. If you hear
  singing, walk the other way. If a raven follows you for three days,
  you owe a death. If fog rolls in from the north, stop moving.

Mechanical integration: folk magic has no dice rolls, but settlement
morale is affected by whether rites are observed. Bands that camp in
a village and interrupt seasonal rites take a REPUTATION penalty.
Bands that participate gain trust.

#### Section 4 — Magic, Power, and Authority

How the three traditions intersect with political structures.

##### The Galdr-Worker as Political Asset

- Every jarl needs wards. Wards on the longhouse, the grain store, the
  armory. Wards on the harbor entrance if coastal. Wards on the
  border-stones.
- A jarl without a galdr-worker is a jarl with unprotected walls. This
  creates dependency: the galdr-worker can negotiate terms that no
  warrior would dare ask for. Separate quarters. Exemption from
  labor. Payment in silver, not kind.
- But the galdr-worker who overreaches dies. Jarls kill them and find
  another. There is always another. Galdr is the most common tradition
  because it is the most tolerated — and the most replaceable.

##### The Seiðr-Wife as Power Broker

- Seiðr-wives know secrets. The dead talk. The spirits of dead jarls
  reveal where they buried silver, what oaths they broke, whom they
  wronged. A seiðr-wife who communes with a dead jarl now holds power
  over the living jarl's legitimacy.
- This is why seiðr-wives live alone, outside settlements. Not because
  they choose isolation — because the jarl demands it. A seiðr-wife
  inside the walls knows too much. A seiðr-wife outside the walls can
  be controlled: you bring questions to her, on your terms.
- Male seiðr-practitioners are doubly dangerous: they hold death-
  knowledge AND break gender taboos. A man who practices seiðr has
  already demonstrated willingness to defy social order. What else
  will he defy? This is the real root of the ergi stigma — not
  effeminacy, but uncontrollability.

##### The Wyrd-Reader as Reluctant Advisor

- Wyrd-readers are the most common and least powerful magical tradition.
  Every band has someone who can cast lots. Jarls consult wyrd-readers
  before battles, journeys, alliances.
- But wyrd-readers cannot change what they see. Their value is
  informational, not interventional. A jarl who dislikes a reading
  simply ignores it. The wyrd-reader has no leverage.
- Exception: a wyrd-reader who sees a jarl's death can create a
  succession crisis simply by speaking. Wise wyrd-readers learn to
  lie by omission. This is why Thorne phrases everything as "I see
  trouble" rather than "I see Voss dead in the snow."

##### Magic in Union Politics

How the *ting* (assembly) and union system from `20_SIMULATION_RULES.md`
interacts with magic:

- **Ward-rights:** Which galdr-worker wards the Allthing stones during
  assembly? The appointment is political. Control the wards, control
  who speaks safely under them.
- **Seiðr testimony:** Can a seiðr-wife testify at the ting about what
  the dead told her? Some unions allow it (Frost March Compact); others
  forbid it (Northern Defense Pact). This difference is a source of
  inter-union tension.
- **Curse arbitration:** When one jarl cursing another via niding-pole
  escalates to a formal complaint at the ting, who adjudicates? The
  galdr-worker who carved it? The seiðr-wife who can verify intent?
  The wyrd-reader who saw the outcome? Each union handles this
  differently.
- **Dark Arts prohibition:** The Allthing officially prohibits "blood-
  galdr and death-seiðr" but definitions vary. A ward that requires
  the carver's blood is standard galdr. A ward that requires someone
  else's blood is blood-galdr. The line is political, not magical.

#### Section 5 — Contradictions and Disputes

Genuine disagreements between practitioners and traditions. These are
not plot holes — they are features of a world where no one fully
understands the supernatural.

- **What is the Hush?**
  Galdr-workers say it is the silence of dying runes — the world's
  magical fabric fraying. Seiðr-workers say it is something listening
  from behind the Veil, something large enough that its attention
  alone suppresses sound. Wyrd-readers say it is simply the absence
  of fate — a moment where nothing is woven, and the world holds
  its breath. All three explanations predict different behaviors for
  the Hush, and all three are occasionally right.

- **Do the gods still exist?**
  The Cracking silenced them. Seiðr-workers who contact the very old
  dead (pre-Cracking) receive fragmentary impressions of divine
  presence. Post-Cracking dead report nothing. But galdr still works
  — and galdr was originally Odin's gift. If Odin is gone, who powers
  the runes? Galdr-workers avoid this question. Some have gone mad
  pursuing it.

- **Can draugr be healed?**
  Seiðr tradition says yes — a restless dead can be guided to
  stillness through communion, laying them properly with the right
  rites. Galdr tradition says no — a draugr is a broken rune, a body
  animated by decaying magic, and must be destroyed. The common wisdom
  says burn it. The real question nobody asks: was the draugr ever
  actually dead?

- **Is wyrd-reading magic?**
  Many practitioners and common folk insist it is not. Casting lots is
  just pattern recognition. Reading entrails is just observation.
  Birds fly in predictable patterns. The philosophical problem: if
  wyrd-reading is not magic, why do wyrd-readers develop the same
  fatalism, the same thousand-yard stare, the same inability to sleep
  through the night?

- **Who owns barrow contents?**
  Galdr-workers say rune-inscribed artifacts are sacred heritage that
  must be preserved and studied. Seiðr-workers say disturbing barrow
  contents offends the dead and thins the Veil. Jarls say barrow loot
  belongs to whoever paid for the clearing. Bands say it belongs to
  whoever went in and survived. These four claims collide on every
  contract.

#### Section 6 — Encoded Mysteries

Deep lore that has no single correct interpretation in the public
documents, with CJK-encoded resolutions in `data/hidden/`.

Each mystery includes:

- The question as characters would ask it
- 2-3 plausible theories grounded in existing lore
- Clues scattered across specific documents (cross-references)
- The "true" answer (CJK-encoded) — which is always more complicated
  than any single theory

##### Mystery 1: What the Cracking Actually Released

Public theories documented above. The encoded truth involves an entity
that is neither god nor dead — something the Veil was originally built
to contain, not to separate.

##### Mystery 2: Why Galdr Still Works

Public theories: residual power, self-sustaining rune logic, the runes
were never divine. Encoded truth: the runes are parasitic — they draw
power from the carver's lifespan, not from any external source. Every
galdr shortens the caster's life. The white scars on Ash's hands are
not metaphorical.

##### Mystery 3: What the Dead Actually Say

Seiðr contacts report fragmentary, confused speech from the dead. The
encoded truth: the dead are not confused. They are being edited. The
messages arrive intact on the other side, but something between the
living and the dead is censoring specific content. What is it and why?

##### Mystery 4: The Hush is Not One Thing

Multiple phenomena are collectively called "the Hush." Some are Veil-
thinning events. Some are the attention of the entity from Mystery 1.
Some are the death-echoes of mass casualties (battlefields, plague
villages). Each type has subtly different characteristics that a
careful observer could distinguish — but no character in the setting
has yet assembled the pattern.

##### Mystery 5: Thorne's Real Condition

Public knowledge: Thorne is old, knows galdr, has wyrd-sense, moved his
bedroll to danger before it arrives. Encoded truth: Thorne died seven
years ago. His body kept moving. He is the only draugr that doesn't
know it is a draugr. His wyrd-reading works because the dead always
know where death is coming from. His "rune-lore" is muscle memory
from a life he no longer lives. The band does not know. Thorne does
not know. The Hush knows.

##### Mystery 6: The Pattern in the Barrow Awakenings

Barrows are waking along a geographic line that no character has
mapped. Encoded data: the line traces the path the Cracking took when
the sky split. The barrows closest to the original fracture-point are
waking first. The fracture-point is not in the far north where
everyone assumes — it is directly beneath the Iron Barrow.

#### Section 7 — Magic and the Material World

How supernatural forces physically interact with the setting's economy,
logistics, and daily trade.

- **Rune-marked trade goods:** Some smiths carve runes into tools,
  weapons, and household items. Most are decorative — the smith has no
  galdr talent, just a chisel. Occasionally a genuine galdr-worker
  marks a real rune, and the item works differently. There is no way
  to tell which is which except by use. This creates a market for
  "rune-guaranteed" goods that is half craft and half fraud.
- **Ward-stones (settlement infrastructure):** Genuine galdr wards at
  settlement boundaries. Require annual renewal. A settlement whose
  wards lapse experiences increased supernatural activity — or claims
  to. The galdr-worker's annual visit is both a service and a shakedown.
- **Seiðr consultation pricing:** A seiðr-wife's services have no fixed
  price because the value depends on what the dead reveal. Blood price
  (physical blood, not silver) is standard for serious consultations.
  Some seiðr-wives also demand a "secret" — the questioner must reveal
  something true about themselves before the dead will speak.
- **Wyrd-reading as insurance:** Merchants, travelers, and warband
  leaders routinely pay for readings before major journeys. Cost: 1-5
  silver depending on specificity. Accuracy is disputed. Repeat
  customers swear by their reader; skeptics call it fortune-telling.
  The economic effect is real: a wyrd-reader who predicts a bad trade
  season can crash grain prices through rumor alone.
- **Barrow loot as cursed inventory:** Items retrieved from barrows
  carry stigma. Silver is silver, but a ring taken from a draugr's
  finger requires ritual cleaning (galdr) before resale. Weapons are
  worse — a blade that killed its last owner tends to find a way to
  kill this one too, or so the stories say. Bands that specialize in
  barrow-clearing (like the Grave Wardens) maintain relationships
  with galdr-workers who "clean" loot for a percentage.

#### Section 8 — Practitioner Lifecycle

How magical practitioners develop, function, break down, and die.
Tracked effects for use in simulation and prose.

- **Early manifestation:** Most galdr and seiðr talent appears in youth
  (ages 8-14). Wyrd-sensitivity can emerge at any age, often after
  head trauma or near-death experiences. Late-onset seiðr (after 30)
  is associated with madness.
- **Training:** No formal schools. Galdr is apprenticed (master/student,
  5-10 years). Seiðr is transmitted woman-to-woman (mother-daughter,
  mentor-student, or volva-to-chosen). Wyrd-reading is self-taught
  or inherited. This training gap means every practitioner's technique
  is slightly different — there is no "standard" galdr, only lineages.
- **Active career:** 15-30 years for galdr-workers. Seiðr-wives have no
  retirement — the dead don't stop talking when you're tired. Wyrd-
  readers often practice their entire lives because the cost is invisible
  (emotional, not physical).
- **Degradation:** Galdr-workers lose fine motor control in their hands
  (the scars deepen, the fingers stiffen). Seiðr-workers lose the
  boundary between here and there (the dead become as real as the
  living). Wyrd-readers lose agency (they stop choosing because they
  already know).
- **Death:** Galdr-workers who overreach die from rune-backlash
  (explosive, physical). Seiðr-workers who go too deep don't come
  back from trance (quiet, witnessed, terrifying for observers).
  Wyrd-readers die the way they predicted they would, which is the
  final proof that the tradition works.

## Implementation Plan: Prompt Sequence

This proposal requires 5 execution prompts plus 1 integration prompt.

### Prompt 31 — Core Lore: Cracking, Phenomenology, Folk Magic (Sections 1-3)

**Subagents (3):**

- **31A:** Write Section 1 (Cracking theories, competing explanations,
  supporting/contradicting evidence). Create
  `data/hidden/magic_truth.txt` with CJK-encoded true answers.
- **31B:** Write Section 2 (phenomenology for all three traditions:
  practitioner, witness, environmental, long-term cost). Cross-
  reference existing statblocks in `22_MEMBER_STATBLOCKS.md`.
- **31C:** Write Section 3 (folk magic layer: birth/death/threshold/
  seasonal/food/navigation). Define morale/reputation integration
  points for `20_SIMULATION_RULES.md`.

**Output:** First three sections of `08_MAGIC_OF_RIMEVEGR.md` +
encoded hidden data.

### Prompt 32 — Power, Politics, and Contradictions (Sections 4-5)

**Subagents (3):**

- **32A:** Write Section 4 (magic as political lever: galdr-worker as
  asset, seiðr-wife as broker, wyrd-reader as advisor, magic in union
  politics). Cross-reference `20_SIMULATION_RULES.md` §18 political
  system.
- **32B:** Write Section 5 (contradictions and disputes: the Hush,
  gods, draugr healing, wyrd-reading legitimacy, barrow ownership).
  Ensure contradictions reference existing lore in specific docs.
- **32C:** Update `20_SIMULATION_RULES.md` with new political-magic
  integration rules (ward-rights, seiðr testimony, curse arbitration,
  dark arts definitions). Update settlement YAML schemas if needed.

**Output:** Sections 4-5 of `08_MAGIC_OF_RIMEVEGR.md` + simulation
rule updates.

### Prompt 33 — Encoded Mysteries (Section 6)

**Subagents (3):**

- **33A:** Write the public-facing mystery entries (questions, theories,
  clue locations) for Mysteries 1-3. Plant cross-reference clues in
  existing docs (subtle additions to `01`, `06`, `09`, `11`).
- **33B:** Write public-facing entries for Mysteries 4-6. Plant clues.
  Special attention to Mystery 5 (Thorne) — must be subtly consistent
  with existing Thorne content across all docs without breaking
  anything.
- **33C:** Encode all mystery resolutions via `spoiler_codec.py` into
  `data/hidden/magic_truth.txt`. Create
  `data/hidden/mystery_manifest.yaml` with decoded-state tracking.
  Validate encoding with existing test suite.

**Output:** Section 6 of `08_MAGIC_OF_RIMEVEGR.md` + hidden data +
clue plantings across existing docs.

### Prompt 34 — Material World and Practitioner Lifecycle (Sections 7-8)

**Subagents (3):**

- **34A:** Write Section 7 (rune-marked goods, ward-stones, seiðr
  pricing, wyrd-reading economics, cursed inventory). Define trade
  items for `data/economy/` integration.
- **34B:** Write Section 8 (practitioner lifecycle: manifestation,
  training, career, degradation, death). Cross-reference NPC ages
  and conditions in `22_MEMBER_STATBLOCKS.md`.
- **34C:** Create `data/magic/` directory with YAML schemas:
  `folk_rites.yaml`, `practitioner_effects.yaml`,
  `magic_trade_goods.yaml`. Define schema in
  `data/magic/MAGIC_SCHEMA.md`.

**Output:** Sections 7-8 of `08_MAGIC_OF_RIMEVEGR.md` + data schemas.

### Prompt 35 — Integration and Cross-Document Updates

**Subagents (4):**

- **35A:** Update `01_RIMEVEGR_SETTING_BIBLE.md` — expand Norse Magic
  System section with references to `08_MAGIC_OF_RIMEVEGR.md`. Add
  folk magic mentions to daily life sections. Add contradiction hints.
- **35B:** Update `20_SIMULATION_RULES.md` — add folk magic morale
  rules, ward-rights political mechanics, seiðr testimony rules,
  practitioner degradation tracking. Update magic check formulas if
  phenomenology implies changes.
- **35C:** Update `22_MEMBER_STATBLOCKS.md` — add practitioner
  degradation notes to Ash, Thorne, Ragnhild. Add folk magic
  observations to relevant band members. Update triggers for
  supernatural-aware NPCs.
- **35D:** Update `06_DICTIONARY_OF_NORSE_TERMS.md` — add terms:
  blood-galdr, death-seiðr, threshold-iron, birth-rune, Hael's toll,
  mouth-sewing, ward-stone, rune-guarantee, wyrd-fatigue. Update
  existing supernatural terms with phenomenology references.

**Output:** Cross-document consistency. All docs reference
`08_MAGIC_OF_RIMEVEGR.md` where appropriate.

### Prompt 36 — Novel-Writing Skill Update

**Subagents (2):**

- **36A:** Update `skills/novel-writing/references/` — add
  `supernatural_phenomenology.md` covering how to write each tradition
  in prose. Add writing guidelines for folk magic scenes, political-
  magic scenes, and mystery-layering techniques.
- **36B:** Update `00_NOVEL_WRITING_PROMPT.md` — add supernatural
  writing rules section referencing new phenomenology. Update existing
  magic mentions to reference `08_MAGIC_OF_RIMEVEGR.md`.

**Output:** Novel-writing skill fully updated for deep supernatural
prose.

## Success Criteria

- [ ] `08_MAGIC_OF_RIMEVEGR.md` exists with all 8 sections.
- [ ] At least 6 CJK-encoded mystery resolutions in `data/hidden/`.
- [ ] `data/magic/` directory with 3+ YAML files and schema doc.
- [ ] Each magic tradition has distinct phenomenology (practitioner,
      witness, environmental, long-term cost).
- [ ] Folk magic layer covers 6+ categories of daily practice.
- [ ] Political-magic integration rules added to `20_SIMULATION_RULES.md`.
- [ ] 5 contradictions documented with 2-3 competing explanations each.
- [ ] Practitioner lifecycle (manifestation → death) fully tracked.
- [ ] Cross-references planted in `01`, `04`, `06`, `09`, `11`, `16`.
- [ ] Novel-writing skill updated with supernatural prose guidelines.
- [ ] All tests still pass (existing 111 + any new).
- [ ] `npx -y markdownlint-cli2 --fix` clean on all new/edited files.

## Estimated Scope

| Prompt | Sections | Subagents | Estimated New Content |
| --- | --- | --- | --- |
| 31 | 1-3 | 3 | ~3,000 words + hidden data |
| 32 | 4-5 | 3 | ~2,500 words + rule updates |
| 33 | 6 | 3 | ~2,000 words + encoded data |
| 34 | 7-8 | 3 | ~2,000 words + YAML schemas |
| 35 | Integration | 4 | ~1,500 words across 4 docs |
| 36 | Skill update | 2 | ~1,000 words + reference doc |
| **Total** | **8 sections** | **18 subagents** | **~12,000 words** |

## Dependencies

- Requires `spoiler_codec.py` (exists, tested).
- Requires `20_SIMULATION_RULES.md` §18 political rules (exists).
- Requires `data/hidden/` directory and manifest (exists).
- Soft dependency on Prompt 21 (bestiary) for creature details —
  can proceed independently; creature stat blocks added later.

## Risks

- **Scope creep:** 8 sections is a lot. Mitigated by strict section
  boundaries and per-prompt deliverables.
- **Veil Ceiling violation:** Deep magic system risks making the
  supernatural too present. Mitigated by Section 3 (folk magic is
  ambiguous) and Section 6 (mysteries stay encoded).
- **Contradiction management:** Invented contradictions must not
  conflict with existing lore. Mitigated by Prompt 35 (integration
  pass) and existing test suite.
- **Thorne reveal (Mystery 5):** Must be planted so subtly that
  re-reading existing content feels natural, not retconned. Highest-
  risk single element.
