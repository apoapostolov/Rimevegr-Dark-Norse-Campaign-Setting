# Campaign Arcs and Plot Seeds

**Project:** Iron Ledger -- Mercenaries of the Rimevegr
**Purpose:** Long-term campaign arcs and hidden plot seeds. Hidden event
details are encoded in Chinese via `scripts/hidden_info.py`.

---

## 1. Major Campaign Arcs

### Arc 1: The Whispering Debt (Personal to Epic)

**Theme:** A blood-debt that refuses to stay buried.
**Trigger:** The band clears or camps near a restless barrow.
**Progression:**

- Season 1: First bleeding rune-stone. A Named Man or Lump hears
  their name whispered.
- Season 2: A draugr begins targeting the weakest member. Grievances
  pile up.
- Season 3: The barrow reveals an ancient oath tied to a Named Man's
  bloodline. The band must pay the debt in silver, blood, or by breaking
  the barrow seal (releasing something worse).

**Endings:** Pay the debt and gain a rune-ally, destroy the barrow and
unleash greater horror, or betray a Named Man to silence it.

### Arc 2: The Stolen Ground (Political)

**Theme:** The Bone Pack's lost ancestral land.
**Trigger:** The band encounters the Bone Pack.
**Progression:**

- Bone Pack offers alliance for help reclaiming territory.
- Rival jarls and Three Wolves want the same land.
- Internal tension: some Named Men see profit in betrayal.

**Endings:** Help the Bone Pack (powerful allies), seize land yourself
(enemies for life), or sell them out (short gain, long curse).

### Arc 3: The Pale Widow's Game (Intrigue)

**Theme:** A cunning jarl playing bands against each other.
**Trigger:** Take a contract for the Pale Widow of Ashen Reach.
**Progression:**

- Increasingly lucrative contracts while she secretly tests loyalty.
- She hires rival bands to probe for weakness.
- The band realizes they are being played.

**Endings:** Become her Sworn band, expose her plot and spark war, or
betray her first and seize her hall.

### Arc 4: The Long Winter Host (Large-Scale)

**Theme:** Warchief Ordovast forging a Host from broken bands.
**Trigger:** Multiple bands offered Sworn allegiance with massive pay.
**Progression:**

- Early contracts seem generous.
- Later demands become brutal (raiding kin-clans, clearing sacred
  barrows).
- Internal fractures as Named Men refuse dark orders.

**Endings:** Join the Host, lead rebellion, or survive neutral.

---

## 2. Plot Seeds (Ready to Drop)

**Seed 1: The Wrong Tribute**
A village the band extorted already pays protection to another Svarthird.
The rival now hunts the band.

**Seed 2: The Bleeding Rune**
A rune-stone near camp bleeds every night. One Named Man's name is
whispered. He insists it means nothing -- but his Trigger is about to
fire.

**Seed 3: The Shadow**
Lump notices his own shadow moving half a second late.
Others see it but say nothing. Superstition or something real?

**Seed 4: Desertion in the Long Dark**
A veteran reaches Loyalty 1 and plans to desert during a blizzard,
taking silver and part of the ledger.

**Seed 5: The Jarl's Daughter**
A jarl offers triple pay to escort his daughter. She is Veil-touched
(high Wyrd) and sees things that should not be seen.

**Seed 6: The Hollow Longship**
A drifting longship with frozen dead and a sealed iron chest. Taking it
triggers hidden events.

**Seed 7: Kin Blood on the Snow**
The Bone Pack asks for help against a rival clan. Refusing damages
reputation with all kin-clans; accepting risks blood-feud with a jarl.

---

## 3. Campaign Arc Integration Chains (Prompt 6)

These chains link arcs, plot seeds, hidden events, rival bands, and
settlements into multi-season storylines. Each chain specifies the
hidden event triggers that advance it.

### Chain A: The Waking Barrows (Supernatural Escalation)

Connects Arc 1 (Whispering Debt) + EVT_007 + EVT_008 + EVT_011 +
SECRET_BRYN + Grave Wardens + Moor's End + Deepholm.

**Season 1 (Days 87-150):**

1. EVT_007 (Day 105): Rune-stones bleed on the trade road. Galdr ward
   check. If the band cleared the Whispering Barrow without galdr, the
   draugr curse is active — the bleeding stones whisper Kell's name.
2. EVT_011 (Day 160): Fresh rune-stone appears on march path. Warning
   from the barrow draugr. If ignored, barrow-wight encounter.
3. Gest recognizes the rune-form as Deepholm work and suggests the band
   seek Skaldhaven's rune archive for answers.

**Season 2 (Days 150-250):**

1. EVT_008 (Day 140): Moor's End standing stone cracks. The Grave
   Wardens investigate but need reinforcement. They send word to any
   professional band in the region.
2. If the band helps the Grave Wardens, Bryn shares SECRET_BRYN — the
   Iron Barrow contains a galdr-forge. Ordovast also knows.
3. Bryn's field map marks recent awakenings in a rough northeast-
   southwest line through the Grimholt district. Most Wardens call it
   coincidence unless someone starts plotting dates.
4. EVT_012 (Day 250): The six-hour Hush. All galdr wards fail. The
   barrow curse intensifies. Kell hears his ancestor's voice clearly.

**Season 3 (Days 250-360):**

1. The draugr lord sends a dream-summons: Clear the Iron Barrow, or
   the curse consumes Kell. Kell's loyalty drops to 1 if ignored.
2. Resolution options: (a) ally with Grave Wardens to seal the barrow
   properly using galdr-forge knowledge; (b) pay the blood-debt in
   silver or sacrifice at Skaldhaven; (c) deliver Kell to the barrow
   to end the curse (betrayal, -2 morale, +dark reputation).

**Side Thread — Thorne's Defection Risk:**
EVT_004 (Day 120): If Thorne's blood-debt with the Bone Pack is
unaddressed, his loyalty drops to 2 and he contacts Kolla. If the band
is simultaneously dealing with barrow trouble, Thorne may interpret the
supernatural pressure as proof the band is cursed. Losing Thorne to the
Bone Pack during a barrow expedition leaves the band critically short of
fighters for the Iron Barrow.

### Chain B: The Widow's Web (Political Intrigue)

Connects Arc 3 (Pale Widow) + EVT_003 + ARC_WIDOW + SECRET_VARIS +
Three Wolves + Ashen Reach + Feldwick.

**Season 1 (Days 87-130):**

1. The Pale Widow offers increasingly good contracts from Ashen Reach
   (contracts 003-005 in the pool).
2. EVT_003 (Day 110): Three Wolves move into the Inner Fjords, competing
   for the same work. This is not coincidence — the Widow hired both
   bands to weaken each other.
3. SECRET_VARIS: If Hadric orders another village burning, his Named Man
   Varis approaches neutral bands about defection. The band may recruit
   a skilled fighter from the enemy.

**Season 2 (Days 130-200):**

1. The Widow's contracts begin requiring the band to patrol near Three
   Wolves territory. She is engineering a confrontation.
2. If the band discovers the manipulation (Wits or Bargain check when
   reviewing contract terms), they can confront the Widow or play along.
3. EVT_010 (Day 200): The three-day blood sun. Settlements lock gates.
   The Widow uses the chaos to move her own armed retainers into position.

**Season 3 (Resolution):**

1. Options: (a) Expose the Widow's scheme at a Thing assembly in
   Deepholm — she loses political standing; (b) destroy the Three
   Wolves for her and become her Sworn band (profit but servitude);
   (c) ally with the Three Wolves against the Widow (Varis facilitates);
   (d) walk away — the Widow marks the band for elimination.

### Chain C: The Iron Host (Military Escalation)

Connects Arc 4 (Long Winter Host) + SECRET_SIGRID + Iron Tide Remnant +
Grimholt + Raven's Perch + Thornwall.

**Season 1 (Days 87-150):**

1. Ordovast offers generous contracts from Grimholt (contract 006).
   Early work is professional: garrison duty, patrol.
2. SECRET_SIGRID: Visiting Raven's Perch reveals that the Iron Tide
   Remnant is also watching Ordovast with suspicion. Halvard Keg
   mentions a possible alliance.
3. Ordovast begins demanding loyalty oaths from contracted bands.

**Season 2 (Days 150-250):**

1. Ordovast's demands escalate: raid the Bone Pack's ancestral land,
   clear a sacred barrow against omens, burn a settlement that refused
   tribute (Thornwall).
2. Named Men begin refusing dark orders. Loyalty checks required.
3. The Iron Tide Remnant, Bone Pack, and Hollow Hall start sharing
   intelligence about Ordovast's true plan: a Host to conquer Deepholm.

**Season 3 (Resolution):**

1. Options: (a) Join the Host and share in Deepholm's wealth (dark
   path — Named Men desert, reputation as tyrants); (b) lead a
   coalition of smaller bands against Ordovast (requires alliances
   with Iron Tide, Bone Pack, and at least one jarl); (c) warn Jarl
   Sigrun of Deepholm and earn her patronage (best pay but Ordovast
   becomes a blood-enemy); (d) flee the region entirely.

### Chain D: The Red Hunt (Rescue Mission)

Connects PLOT_PETRA_VISION + Red Tide + Icebreak + Northern Ice-Reach.

**Trigger:** Any Veil-Thinning event while Petra is in the band.

1. Petra's vision reveals her sister alive in a Red Tide camp. Petra's
   loyalty: 5 if the band agrees, 1 if refused.
2. Intelligence gathering: Kolvik sailors or Bleakwater Landing
   travelers may know the Red Tide's current camp location.
3. Hermit Ragnhild at Icebreak (seidr practitioner, WYR 5) can
   confirm the vision's truth for a blood price.
4. Assault on the Red Tide camp requires at least 12 fighters or a
   clever plan (distraction, night raid, or buying a thrall's freedom).
5. Wulfgar the Branded does not forgive theft of property. If the
   rescue succeeds, the Red Tide hunts the band for two seasons.

---

## 4. AI Usage Rules

- Select 1-2 active arcs and 2-4 plot seeds at season start.
- Cross-reference hidden events from 09.
- Consequences always feel earned from ledger, oaths, and decisions.
- Never reveal future events directly -- show only ripples.
- Encode all upcoming triggers in Chinese via hidden_info.py.
