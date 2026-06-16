# Y313 Deepholm Campaign

## Purpose

This file is now the detailed operational home for the Y313 war phase.

Use it for the southward approach, the Deepholm siege, assault logic,
breach risk, retreat logic, and the immediate military cost accounting that
follows. The foundation and chronology still live in 23A, but the
high-detail campaign objects from Prompt 12 onward belong here.

## Canon sources for this pass

- volume_arcs.yaml
- y313_events.yaml
- political_state.yaml
- band_state.yaml
- supernatural_chain_events.yaml

---

## 1. Role of the Deepholm campaign inside Y313

The Deepholm war phase should not read like one loud battle scene. It
should feel like a real campaign with several linked problems:

- getting the host to the target intact
- keeping wagons, food, and tools alive long enough to matter
- deciding where to spend good men first
- forcing the defender to react without exhausting the attacker too early
- understanding when a push is worth the dead it will cost

This is where competence becomes visible. The side that survives longer is
not necessarily the braver one. It is the side that wastes less time, less
food, less discipline, and fewer men.

## 2. Prompt 12 — siege and breach doctrine

### Core doctrine

- no assault should happen without a reason tied to supply, morale, timing,
  or
political pressure
- gate attacks, harbor control, and outer-screen fighting should interact
  rather
than occur as isolated scenes
- retreat is not automatically cowardice; sometimes it is the only
  competent way
to preserve later force
- commanders should make trade-offs that hurt, not cinematic moves that
  cost
nothing

### Attacker and defender realities

| Problem         | Ordovast must solve                                                         | Sigrun must solve                                                             | What the band experiences                                            |
| --------------- | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| gate pressure   | bring rams, fire teams, and protected approach lanes close enough to matter | rotate defenders, repair damage, and stop panic when the wood starts to crack | the band gets used wherever the line looks most likely to fail       |
| supply strain   | keep grain and spare timber coming over bad roads                           | stretch finite stores without visibly breaking confidence                     | every extra day at the walls increases exhaustion and price pressure |
| morale          | convert fear and punishment into forward motion                             | turn civic defense into stubborn endurance                                    | men begin measuring orders against survival instead of honor alone   |
| withdrawal risk | avoid turning a failed push into a rout                                     | avoid mistaking one successful defense for long-term safety                   | the band may need to cover somebody else's orderly retreat           |

### Branching rule for the siege pass

Every major Deepholm war object should change one or more of these values:

- gate integrity
- attacker supply health
- defender fatigue
- harbor access
- band casualty load
- public legitimacy after the fighting

If an action does not change one of those pressures, it is not central
enough to carry a major node.

---

## 3. Main operational objects for Prompt 12

### O313-U01 — The Walls Before Dawn

- **Year window:** Y313 summer, days 68-78
- **Class:** siege-preparation object
- **POV:** Voss, Gest, or a defense-facing witness
- **Canon anchors:** EVT_313_U01_026, EVT_313_U04_029, EVT_313_U08_033
- **Setup:** both sides can now see the main confrontation coming;
  palisades,
carts, rope, tar, watch rotations, and gate braces matter more than
speeches
- **Decision pressure:** where does the band place its strength before the
  first
full assault begins?
- **Competent options:** reinforce the likeliest pressure point, inventory
  spare
tools, keep reserves mobile, and make clear fallback signals
- **Desperate options:** crowd the walls with too many men, leave the gate
unsupported, or waste energy on symbolic bravado before contact
- **Likely state touches:** siege_readiness, defender_fatigue,
  band_discipline,
gate_integrity
- **Routes:**
  - **O313-U02** — the first heavy push comes at the wood and hinges.
  - **O313-U03** — if the harbor or flank approaches look weaker than the
    gate.
  - **O313-A01** — if preparation failure creates later blame and
    bitterness.
- **Mystery-box note:** answers where the line may break first, but not
  which
commander is secretly planning beyond the gate itself

### O313-U02 — Rams in Mud and Fire

- **Year window:** Y313 summer, days 79-100
- **Class:** main assault object
- **POV:** Voss, Thorne, Petra, or a wall-sector witness
- **Canon anchors:** EVT_313_U05_030, EVT_313_U15_040, EVT_313_U17_042
- **Setup:** Ordovast commits to the gate with rams, fire, and concentrated
  men;
Deepholm must absorb the shock without letting one cracked beam become
collapse
- **Decision pressure:** should the band hold, sally to burn the ram, or
  shift to
a threatened secondary point before the attackers exploit it?
- **Competent options:** rotate shield lines, use fire and hooks carefully,
protect repair crews, and strike only when the sortie can return alive
- **Desperate options:** charge into open ground without extraction logic,
  leave
a breach unattended, or throw reserves into panic instead of sequence
- **Likely state touches:** gate_integrity, attacker_losses,
  defender_losses,
band_reputation, morale_state
- **Routes:**
  - **O313-U03** — if the fighting broadens to the harbor and outer edges.
  - **O313-U04** — if one side gains a temporary break or suffers a failed
    push.
  - **O313-A01** — the dead and damaged gear begin writing the next phase.
- **Mystery-box note:** answers how the gate battle is fought, but not
  whether
the assault was ever truly meant to take the city or only to bleed it white

### O313-U03 — Harbor Chains and Side Pressure

- **Year window:** Y313 summer, days 82-103
- **Class:** flank-and-access object
- **POV:** Petra, Gest, or a harbor-side observer
- **Canon anchors:** EVT_313_U10_035, EVT_313_U19_044, EVT_313_U25_050
- **Setup:** even while the gate takes the eye, the real survival question
  may be
food, berths, repair wood, and whether the sea route can still relieve the
city
- **Decision pressure:** does the band help secure the harbor, escort
  emergency
stores, or stay committed to the wall sector already under strain?
- **Competent options:** preserve supply lanes, protect ship-to-wall
  transfers,
and prevent a secondary collapse caused by hunger rather than blades
- **Desperate options:** chase glory at the main gate while the harbor
  quietly
fails, or split the band so badly that no position holds well
- **Likely state touches:** harbor_access, food_security, compact_stamina,
campaign_duration, local_standing
- **Routes:**
  - **O313-U04** — if pressure at multiple points forces hard command
    choices.
  - **O313-A01** — shortages and exhaustion feed the post-battle reckoning.
  - **O313-H01** — strange sightings among the drowned and unburied deepen
    the
horror line.
- **Mystery-box note:** answers that the campaign is larger than one gate,
  but
not whose hidden supply calculations will decide the next month

### O313-U04 — The Break That Does Not Hold

- **Year window:** Y313 summer to early autumn, days 100-115
- **Class:** breach-and-counterpressure object
- **POV:** Voss or a command-near witness
- **Canon anchors:** EVT_313_U17_042, EVT_313_U18_043, EVT_313_U21_046
- **Setup:** after the brutal assault, one side believes it has finally
  created
an opening, but the cost of exploiting that opening may be greater than the
value of the ground taken
- **Decision pressure:** does the commander spend the last ready men to
  enlarge a
weak break, or pull back before a local success turns into operational
failure?
- **Competent options:** count the dead honestly, recognize fatigue,
  preserve a
reserve, and treat the enemy's apparent weakness with suspicion
- **Desperate options:** feed men into a narrow breach, refuse to disengage
  from
pride, or mistake noise and smoke for actual control
- **Likely state touches:** breach_status, casualty_memory,
  command_legitimacy,
retreat_quality, war_exhaustion
- **Routes:**
  - **O313-A01** — the campaign shifts into cost, blame, and hidden damage.
  - **O313-H01** — the dead left too long begin to change the tone of the
    war.
  - **O314-R01** — the consequences of this choice echo far beyond the
    season.
- **Mystery-box note:** answers why the siege fails to become clean
  victory, but
not whether either side has strength left for one more serious push

### O313-A01 — Mud, Names, and Spent Victory

- **Year window:** Y313 early autumn, days 110-140
- **Class:** immediate aftermath object
- **POV:** Gest, Petra, or Voss
- **Canon anchors:** EVT_313_U18_043, EVT_313_A04_054, EVT_313_A05_055
- **Setup:** once the biggest clash passes, everybody counts missing men,
  broken
tools, thin stores, and the lies told about what the fighting supposedly
won
- **Decision pressure:** who gets blamed, who gets buried, and what damage
  must
be admitted before the next phase begins?
- **Competent options:** count dead accurately, prioritize treatment and
  grain,
prevent theft, and prepare for the war's quieter but uglier second cost
- **Desperate options:** hide casualty totals, fake triumph, hoard
  medicine, or
force another push with a hollowed force
- **Likely state touches:** treasury, casualty_memory, faction_blame,
morale_state, long_dark_vulnerability
- **Routes:**
  - **Prompt 13** — carries directly into the hidden cost of victory pass.
  - **Prompt 14** — lets the horror escalation feed on war exhaustion.
  - **Prompt 15** — plants the fracture lines that later reconstruction
    inherits.
- **Mystery-box note:** answers what the siege cost immediately, but not
  yet the
full price that winter and revelation will demand

---

## 4. Prompt 13 — the aftermath and hidden cost of victory

Prompt 13 should make it clear that surviving the siege is not the same
thing as winning. The real damage spreads after the shouting: empty grain
lofts, fever, desertion, blame, broken trade, and the political lies told
to disguise all of that.

### Hidden-cost doctrine

- every battle result should be followed by a count of dead, wounded,
  stores,
and lost confidence
- tactical success should still worsen at least one civilian or logistical
pressure downstream
- victory claims made by leaders should be tested against the ledger
  reality on
the ground
- the aftermath must position the Widow, famine, and the Long Dark to
  become as
dangerous as open combat

### Post-siege damage streams

| Damage stream            | What it looks like after the fighting                                                          | Why it matters                                                   |
| ------------------------ | ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| treasury and supply burn | iron prices rise, grain turns scarce, carts and rope are gone, and repairs eat the last silver | even the side that held or struck well becomes materially weaker |
| morale damage            | desertion talk, burial labor, sleepless watches, and command distrust increase                 | cohesion erodes after battle, not only during it                 |
| political blame          | headmen question taxes, allies peel away, and every faction rewrites the story of the siege    | war outcomes reshape legitimacy more than speeches do            |
| civilian cost            | refugees, famine pricing, burned farms, and closed roads make peace impossible                 | the land itself inherits the battle                              |

### O313-A02 — The Ledger After the Smoke

- **Year window:** Y313 early autumn, days 120-150
- **Class:** material-cost object
- **POV:** Gest first, Voss second
- **Canon anchors:** EVT_313_U18_043, EVT_313_A05_055, EVT_313_A11_061
- **Setup:** once the battlefield noise fades, the real measure of survival
  is
entered in ledgers: grain left, iron cost, shield losses, men too hurt to
march, and which debts can no longer be hidden behind war glory
- **Decision pressure:** what gets paid for first when nothing essential is
  fully
affordable anymore?
- **Competent options:** prioritize food, treatment, and repair capacity;
  cut
vanity purchases; admit that some contracts are no longer worth taking
- **Desperate options:** fake solvency, spend the last silver on prestige,
  or
promise pay that cannot possibly be honored
- **Likely state touches:** treasury, repair_capacity, food_security,
wounded_burden, desertion_risk
- **Routes:**
  - **O313-A03** — scarcity begins to change politics and civilian life.
  - **O313-W01** — weakened material state carries forward into winter
    collapse.
  - **23C** — the Long Dark now inherits these shortages in full.
- **Mystery-box note:** answers how costly the siege really was, but not
  how
many later betrayals will grow directly from those numbers

### O313-A03 — Hollow Triumph in the Market

- **Year window:** Y313 autumn, days 134-170
- **Class:** social-economic fallout object
- **POV:** Petra, Gest, or a settlement-facing witness
- **Canon anchors:** EVT_313_A05_055, EVT_313_A11_061, EVT_313_A23_073,
EVT_313_A24_074
- **Setup:** every settlement must choose between feeding soldiers, feeding
children, or pretending there is enough for both while the market collapses
- **Decision pressure:** who is protected first when food can no longer be
  bought
cleanly with silver alone?
- **Competent options:** secure barter chains, protect vulnerable routes,
  ration
honestly, and keep settlements from fracturing into theft and panic
- **Desperate options:** hoard secretly, let prices run wild, strip
  villages for
army needs, or call famine discipline by a noble name
- **Likely state touches:** local_fear, barter_pressure, faction_blame,
settlement_trust, widow_leverage
- **Routes:**
  - **O313-A04** — economic pain becomes overt political realignment.
  - **23C** — the winter horror phase feeds directly on weakened
    communities.
  - **O314-R01** — the next year inherits structural damage, not recovery.
- **Mystery-box note:** answers why the land feels spent after battle, but
  not
who is deliberately widening the dependence for later advantage

### O313-A04 — Blame, Desertion, and the Price of Holding On

- **Year window:** Y313 autumn to first winter, days 140-220
- **Class:** political-fracture object
- **POV:** Voss, Petra, or a leadership-adjacent witness
- **Canon anchors:** EVT_313_A08_058, EVT_313_A12_062, EVT_313_W02_077,
EVT_313_W03_078, EVT_313_W06_081
- **Setup:** with the main campaign spent, leaders begin losing allies and
  men;
deserters slip away, settlements defect, and the Widow's trade web starts
to look like the only system still functioning
- **Decision pressure:** how does the band remain intact when the
  institutions
around it are visibly fraying?
- **Competent options:** keep obligations clear, stop panic early, accept
  that
some retreats are strategic, and preserve the people who still trust one
another
- **Desperate options:** punish too hard, deny reality, cling to dead
  alliances,
or abandon the weakest dependents first and call it necessity
- **Likely state touches:** band_cohesion, faction_blame, widow_power,
desertion_risk, winter_readiness
- **Routes:**
  - **23C** — carries directly into the Long Dark and horror escalation
    phase.
  - **O314-R01** — determines what kind of remnant enters reconstruction.
  - **O315-E01** — some late costs begin here, long before the endgame
    descent.
- **Mystery-box note:** answers why no one gets a clean victory, but not
  yet who
will still be standing when the war gives way to something worse

## 5. Usage rule for later war drafting

When later scenes need a detailed Y313 battlefield home, use this file
first.

- 23A keeps the chronology and broad campaign ladder
- 23B owns the Deepholm campaign and immediate hidden-cost aftermath
- 23C owns the later Y313 Long Dark collapse and horror convergence
- later files should inherit these state changes rather than re-explaining
  them
