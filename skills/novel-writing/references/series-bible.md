# Series Bible

Cross-book continuity tools for a multi-volume Iron Ledger
series. The first novel generates state. Each subsequent volume
inherits that state and must not contradict it. This document
defines what must be tracked, how hand-offs between volumes
work, and what is locked versus what is allowed to drift.

> **Cross-reference:** `01_RIMEVEGR_SETTING_BIBLE.md` defines the world
> these volumes exist within — society, economy, law, and
> customs. `pantheon.md` covers the gods.

---

## What a Volume Inherits

Every new volume opens with the world in the exact state the
previous volume left it. The following categories are canonical
and must carry forward without contradiction.

### The Ledger (Economic State)

| Element                  | Tracking Source       | Carry-Forward Rule                                                 |
| ------------------------ | --------------------- | ------------------------------------------------------------------ |
| Treasury (silver)        | Final chapter closing | Opening balance of next volume                                     |
| Outstanding debts        | Consequence registry  | Persist until repaid or defaulted                                  |
| Outstanding contracts    | Contract log          | Active contracts continue; completed ones leave reputation residue |
| Supply state             | Supply tracker        | Food, equipment, mounts carry over exactly                         |
| Band payroll obligations | Roster + rates        | Monthly burn rate is continuous                                    |

**Lock rule:** The ledger is never quietly adjusted between
volumes. If the band ended Book 1 with 14 silver, Book 2
opens with 14 silver. If the author needs a different number,
an in-narrative event must create it in the first chapters of
the new volume.

### The Roster (Cast State)

| Element             | Tracking Source     | Carry-Forward Rule                                                        |
| ------------------- | ------------------- | ------------------------------------------------------------------------- |
| Living Named Men    | Roster file         | Dead stay dead. No resurrections unless supernatural and earned           |
| Wound states        | Combat log          | Unhealed wounds persist. Healing timelines are physical, not dramatic     |
| Arc positions       | `character-arcs.md` | Each character's arc stage at volume end = arc stage at next volume start |
| Relationship states | Dialogue history    | Trust, grudges, debts between characters carry forward                    |
| Rank and role       | Roster file         | Promotions, demotions, role changes in the band are permanent             |

**Lock rule:** A character cannot regress in their arc between
volumes without a specific in-narrative cause. If Kell learned
to hold his temper by Book 1's end, Book 2 opens with that
restraint intact. It can erode — but the erosion must be shown.

### The Map (Settlement and Faction State)

| Element                     | Tracking Source                      | Carry-Forward Rule                                      |
| --------------------------- | ------------------------------------ | ------------------------------------------------------- |
| Settlement attitudes        | `settlements.yaml` faction_relations | Attitudes at volume end carry forward                   |
| Destroyed/damaged locations | Consequence registry                 | Burned villages stay burned. Rebuilding is slow (years) |
| NPC states                  | NPC tracker                          | Named NPCs: alive/dead/allied/hostile persists          |
| Faction power balance       | Faction tracker                      | Shifts from Book 1 events are the baseline for Book 2   |
| Travel route conditions     | `settlements.yaml` travel_routes     | Road degradation, blockades, new hazards persist        |

**Lock rule:** A settlement the band alienated in Book 1 does
not quietly forgive in Book 2. Reputation repair requires
on-page effort with realistic timescales.

### The Veil (Supernatural State)

| Element                   | Tracking Source         | Carry-Forward Rule                                                             |
| ------------------------- | ----------------------- | ------------------------------------------------------------------------------ |
| Veil intensity            | Calendar/weather system | Seasonal Veil patterns continue their cycle                                    |
| Supernatural encounters   | Hidden events log       | Draugr sightings, rune events, seidr visions are part of the historical record |
| Dalla's seidr development | Arc tracker             | Her abilities and their costs are cumulative                                   |
| Thorne's rune knowledge   | Arc tracker             | What he has decoded stays decoded                                              |
| Barrow/site states        | Location tracker        | Opened barrows stay opened. Disturbed sites stay disturbed                     |

**Lock rule:** The Veil Ceiling carries across volumes.
If Book 1 pushed against it aggressively, Book 2 inherits a
world where the supernatural is more present and must account
for that. The ceiling does not quietly reset.

---

## Volume Hand-Off Protocol

When completing a volume and beginning the next, execute these
steps in order.

### Step 1: State Snapshot

Generate a canonical state snapshot at the final chapter's
close. This snapshot becomes the READ-ONLY opening state for
the next volume.

```text
VOLUME_END_SNAPSHOT:
  date_in_world: [in-game calendar date]
  treasury_silver: [exact amount]
  food_days_remaining: [exact count]
  roster_count: [total Named Men alive]
  roster_wounded: [count + wound descriptions]
  active_contracts: [list with terms and deadlines]
  pending_consequences: [from consequence registry, status=pending]
  faction_states: [key settlement attitudes]
  supernatural_baseline: [Veil intensity, active phenomena]
  open_threads: [unresolved plot lines carried forward]
```

### Step 2: Consequence Migration

Review the consequence registry. For each entry:

- **Resolved:** Archive it. It stays in the historical record
  but does not need active tracking.
- **Pending with payoff window in this volume:** Flag as
  overdue. Either pay it off in the opening chapters of the
  next volume or explicitly note that it compounded into
  something else.
- **Pending with payoff window in future volumes:** Migrate
  to the new volume's active registry.

### Step 3: Arc Stage Freeze

Record each named character's arc stage at volume end.
This becomes the starting point for the next volume.
The arc stage includes:

- Current behavioral pattern (what they do, not what they feel)
- Key relationships and their current temperature
- Unresolved internal tensions
- Physical state (wounds, fatigue, age effects)

### Step 4: Timeline Reconciliation

Verify that the in-world calendar is continuous. Season,
weather patterns, and astronomical events (Veil-Thinning,
equinoxes) must be consistent across the volume boundary.

### Step 5: Map Update

Apply all settlement and faction changes from the completed
volume to the canonical `settlements.yaml`. This updated file
is the ground truth for the next volume.

---

## Cross-Volume Continuity Checks

Run these after drafting the first three chapters of a new
volume.

### Check 1: Opening State Match

Compare the first chapter's narrative state against the
`VOLUME_END_SNAPSHOT`. Every element must match. If the
narrative implies a different state, either the narrative or
the snapshot has an error — resolve before proceeding.

### Check 2: Consequence Acknowledgment

Every migrated pending consequence must be referenced or felt
within the first five chapters. Not necessarily resolved — but
the reader must see evidence that the world remembers.

### Check 3: Character Voice Consistency

Read one dialogue sample per named character from Book 1's
final chapters, then their first dialogue in Book 2. The
voice profile from `dialogue-patterns.md` must hold. Characters
do not become more articulate or less articulate between
volumes without cause.

### Check 4: Tone Calibration

The opening chapters of a new volume must match the tonal
baseline of the series. If Book 1 ended in a dark place,
Book 2 does not open with optimism unless an in-narrative
cause creates it. The world does not brighten between books.

### Check 5: Supernatural Continuity

If Book 1 established certain supernatural phenomena as real
(within the 10% ambiguity), Book 2 cannot ignore them. If
draugr walked, they still walk. If rune-stones spoke, they
still might. The supernatural accumulates — it does not reset.

---

## What Is Allowed to Change Between Volumes

Not everything is locked. These elements can shift naturally
between volumes without explicit in-narrative justification:

- **Time gaps:** Weeks or months can pass between volumes.
  State changes that would naturally occur during the gap
  (wound healing, seasonal shifts, minor reputation drift)
  are acceptable if noted in the opening chapters.
- **Off-page events:** Events that happened during the time
  gap can be referenced in dialogue or narration. They do
  not need full scenes. "Kolvik burned in the spring" is
  sufficient if the event was not dramatized.
- **Minor NPC turnover:** Commons (unnamed band members) can
  rotate between volumes. Named Men cannot vanish without
  explanation.
- **Equipment wear:** Weapons dull, armor degrades, horses
  age. This natural decay is expected and should be visible.

---

## Series-Level Arc Planning

Each volume should advance the series-level arcs by one
major stage. The series arcs are slower than character arcs
and operate on a larger scale.

### Arc Types That Span Volumes

#### The Band's Identity

What the band is changes over the series. They may begin as
a struggling sell-sword company and end as something else —
garrison force, outlaw band, extinct. Each volume should move
them one step along this trajectory.

#### The Veil

The supernatural element should intensify, stabilize, or
shift across volumes. The Veil is the series-level mystery.
Each volume should deepen the ambiguity without resolving it
until the final volume (if ever).

#### The Political Landscape

Factions rise and fall across volumes. The band's actions
ripple outward. By Book 3, the political consequences of
Book 1 should be visible at a macro scale.

#### The Ledger Itself

The economic reality of mercenary life should feel
increasingly concrete across volumes. What began as "we need
silver" in Book 1 becomes a complex web of debts, obligations,
and diminishing options by Book 3.

---

## What the Series Bible Is Not

- It is not a plot outline. Plot emerges from simulation
  and character interaction.
- It is not a world-building encyclopedia. Only track what
  has been established on-page. Speculation stays in notes,
  not in the bible.
- It is not a reference for the reader. This is a production
  tool. The reader never sees it.
