# Proposal 002 — Glíma and Real-World Grappling

## Status

Draft — pending review and approval.

---

## Problem Statement

The current `combat_sim.py` grapple implementation is a single
`Maneuver.GRAPPLE` entry that resolves as a basic control move — it
applies the `GRAPPLED` condition and does nothing else. It does not model:

1. **The grapple sub-game** — once two fighters are clinched, nothing
   specific happens. There is no escalation within the grapple.
2. **Positional advantage** — real grappling is about achieving a dominant
   position (clinch, mount, back-take, pin). The current system has none.
3. **Weapon control inside the grapple** — a fighter with a dagger in a
   clinch and a fighter with a long sword in a clinch face entirely different
   problems. The system treats them identically.
4. **Dirty methods** — historical and literary Norse combat is full of
   tactics the current system ignores: sand and snow in the eyes, spitting,
   biting off flesh, headbutts at distance and in a clinch, hair and beard
   grips, nose-butts.
5. **Glíma specifics** — Glíma was a real codified wrestling tradition.
   Its three styles (brókartök, lausatök, hryggspenna) have distinct grips,
   legal targets, and win conditions. None of this is modelled.
6. **Monster grappling** — undead, bears, wolves all grapple in ways as
   distinct from each other as they are from a human wrestler. The current
   system has no creature-specific grapple hooks.

The result: every grapple plays the same way. A Draugr Warrior and a
trained human wrestler are mechanically identical once locked. A knife-
fight at arm's length and a knife-fight with someone's teeth in your
cheek are the same exchange. This is wrong and breaks immersion.

---

## Audit of Current State

### What Exists

| Component | Current State |
| --- | --- |
| `Maneuver.GRAPPLE` | Applies `GRAPPLED` condition, no further mechanics |
| `Maneuver.SHOVE` | Breaks grapple or knocks prone |
| `ConditionType.GRAPPLED` | -20 attack / -10 defense, cleared by SHOVE |
| `Maneuver.DISARM` | Requires BOUND or STAGGERED — works in clinch in practice |
| `Brawl` skill | Exists in attribute table, affects opposed rolls but has no dedicated sub-system |

### What's Missing

- Grapple sub-positions (clinch, mount, back-take, ground pin)
- Grapple escalation within the hold (each round a new sub-struggle)
- Weapon control inside grapple (press weapon to body, trap arm)
- Ground fighting (falling together, rolling, mount vs. bottom)
- Strike-from-hold (headbutt, knee, elbow, bite)
- Break-and-create-distance moves
- Dirty tactics as a maneuver layer (blinding, biting, hair/beard control)
- Glíma stances and trip families (brók, lausatök, hryggspenna)
- Monster-specific grapple hooks (Deathgrip, Crushing Embrace)
- Narrative output for grapple phases

---

## Design Goals

1. **No bloat** — the grapple sub-system must fit cleanly inside the
   existing round structure. No extra dice types. No new resolution engine.
   Extend what's already there.

2. **Positional state machine** — once clinched, the fight is a series of
   opposed checks for position. Each position unlocks different follow-up
   maneuvers and creates different risks.

3. **Weapon asymmetry** — short weapons (dagger, seax) gain inside the
   grapple. Long weapons (long axe, sword) suffer. This should change the
   AI's grapple willingness based on its weapon.

4. **Dirty tactics as a real option** — not just flavor. Every dirty method
   (bite, blind, headbutt, hair-grip) applies a specific condition or damage
   type and has a specific counter. Some methods are more effective against
   specific opponents (hair-grip useless against close-cropped or bald).

5. **Glíma styles as fighter builds** — a fighter trained in brókartök
   plays differently from one trained in lausatök. These should be
   expressible through the existing `traits` list.

6. **Monster grapple hooks** — undead, large animals, and supernatural
   creatures use specific grapple methods that integrate with the
   `sim_traits` system already built.

7. **Outcome granularity** — a grapple should be able to end in: escape,
   takedown, mutual fall, weapon-to-body, pin, bite injury, unconscious
   from strangle, or one-party submitting. Not just "condition cleared."

---

## Proposed Architecture

### Layer 1 — Grapple Entry

Unchanged from current: `Maneuver.GRAPPLE` resolves an opposed check.
Success → `GrappleState` is created and stored on both fighters.

### Layer 2 — Grapple Positions (State Machine)

Instead of a flat `GRAPPLED` condition, each fighter in a grapple holds
a position value. Positions escalate through an opposed check each round.

```text
CLINCH (default entry)
 ├─ DOMINANT_CLINCH   [attacker won last check — better grips]
 │   ├─ TRIP_SETUP    [Glíma throw telegraph — one more round]
 │   │   └─ TAKEDOWN  [floor fight begins]
 │   └─ WEAPON_PRESS  [weapon pushed against body]
 ├─ NEUTRAL_CLINCH    [neither party gaining]
 └─ BACK_PRESSED / WALL_PRESSED  [against obstacle]

GROUND (entered from TAKEDOWN)
 ├─ MOUNTED           [top position — dominant]
 ├─ GUARD             [bottom — legs wrap attacker]
 ├─ SIDE_CONTROL      [top, weight on chest, no legs]
 └─ REAR_CONTROL      [back-take — worst position]
```

### Layer 3 — In-Grapple Maneuver Menu

New maneuver enum extensions. All require active `GRAPPLED` condition
(both sides). Attempting them outside a grapple fails automatically.

### Layer 4 — Dirty Tactics Layer

Dirty tactics do not require being in a grapple. They are available
to any fighter in melee range (including outside grapple for some).
They have a `WIT`-based counter system: a fighter with high WIT gets
a free reaction check to avoid them.

---

## Complete Maneuver Inventory

### A. Glíma Entry Maneuvers

These are the openers — how the grapple is initiated.

**A1 — Brókartök Seize** (belt and trouser grip, leg-trip family)

- Attribute: `MIG`
- Skill: `Brawl`
- Entry: grab opponent's belt and back of thigh-cloth
- Requires: both fighters standing, within arm's reach
- Success: `DOMINANT_CLINCH`, fighter positioned for hip-throw or leg-trip
- Counter: wide stance drop (NIM check); success → `NEUTRAL_CLINCH`
- Special: +10 if opponent has visible belt/clothing handles; -10 if
  opponent is wearing only a loincloth or tunic with no belt grip

**A2 — Lausatök Grip** (open free-style grip, arm and body control)

- Attribute: `NIM`
- Skill: `Brawl`
- Entry: inside tie-up on the collar/throat area
- Requires: within arm's reach, no shield on attacker
- Success: `NEUTRAL_CLINCH` with attacker holding inside tie
- Counter: duck under (NIM check); success → position reversal
- Special: allows immediate `B5 — Throat Seize` sub-move on next action

**A3 — Hryggspenna Bear Grip** (back-grip, spine clinch)

- Attribute: `MIG`
- Skill: `Brawl`
- Entry: wrap both arms around opponent's torso from behind or side
- Requires: must have circled behind (costs one feint success or
  opponent's PRONE/DISARMED)
- Success: `REAR_CONTROL` immediately
- Counter: drop weight and sit-out (MIG check); success → `NEUTRAL_CLINCH`
- Special: 2× lift bonus — attacker may attempt to hoist and slam
  (counts as `B9 — Slam`)

**A4 — Reactive Tackle** (desperation entry)

- Attribute: `MIG`
- Skill: 0 (raw)
- Entry: charge and bear-hug at the waist
- Requires: any range, but -20 if weapon wielded
- Success: both fighters fall → `GROUND / SIDE_CONTROL` for attacker
- Counter: pivot and redirect (NIM check); success → attacker goes `PRONE`
  alone
- Special: disregards shield bonuses — a shield cannot stop a tackle at
  the waist

---

### B. In-Grapple Positional Moves

Require `GRAPPLED` condition. Each resolves as an opposed check and
transitions the `GrappleState.position` field.

#### B1 — Clinch Improvement / Grip Fight

- Purpose: gain dominant grip from neutral
- Attribute: `NIM`
- Skill: `Brawl`
- Uses: one action in place of an attack
- Success: advance position one step toward dominant
- Failure: no change

#### B2 — Leg Trip (Krokotók / Háskabrók)

- Purpose: throw opponent
- Attribute: `MIG`
- Skill: `Brawl`
- Requires: `DOMINANT_CLINCH` position
- Success: opponent → `PRONE`, attacker may choose to follow to ground
  (enters `MOUNTED`) or stay standing free
- Failure: attacker loses dominant → `NEUTRAL_CLINCH`
- Stamina cost: 3
- Special: if attacker drops in alongside opponent, enters `SIDE_CONTROL`

#### B3 — Hip Throw (Mjaðartak)

- Purpose: lift and slam overhead
- Attribute: `MIG`
- Skill: `Brawl`
- Requires: `DOMINANT_CLINCH`, attacker `MIG >= 5`
- Success: opponent → `PRONE`, 1d6 damage on landing (stone/rock floor ×1.5)
- Critical success: opponent also `STAGGERED` 1 round
- Failure: attacker loses dominant, opponent may counter with `B9 — Slam`
- Stamina cost: 4
- Special: opponent takes +3 extra damage if thrown onto their own weapon

#### B4 — Ground Control / Mount Fight

- Purpose: establish dominant ground position from neutral ground
- Attribute: `MIG / NIM` average
- Skill: `Brawl`
- Requires: both fighters `PRONE` (same location)
- Success: attacker → `MOUNTED`, opponent → `GUARD`
- Failure: no change; both remain in scramble

#### B5 — Throat Seize

- Purpose: control airway and windpipe
- Attribute: `MIG`
- Skill: `Brawl`
- Requires: `DOMINANT_CLINCH` or `MOUNTED`
- Success: opponent gains `CHOKED` condition (new) — TOU check each round
  or lose 4 HP; blocks speech and commands
- Failure: opponent can retaliate with `D3 — Bite` free action
- Stamina cost: 2

#### B6 — Arm Trap (Weapon Arm Lock)

- Purpose: immobilize weapon arm from inside grapple
- Attribute: `NIM`
- Skill: `Brawl`
- Requires: `NEUTRAL_CLINCH` or `DOMINANT_CLINCH`
- Success: opponent's weapon arm `LOCKED` (new condition) — cannot attack
  with that arm; -40 to attack rolls; opponent must `SHOVE` to free
- Counter: twist and elbow (NIM check; failure gives attacker `B7 — Elbow
  Strike` free action)
- Stamina cost: 2
- Special: a fighter whose weapon arm is locked who carries a seax can
  attempt to transfer seax to other hand (NIM check, difficulty 50%)

#### B7 — Elbow Strike (from Clinch)

- Purpose: damage without range
- Attribute: `MIG`
- Skill: `Brawl`
- Requires: `NEUTRAL_CLINCH` or `DOMINANT_CLINCH`
- Success: 1–4 damage to head or torso (no armor bypass — hits
  exposed gaps); may cause `STAGGERED` on critical
- Failure: exposes rib to opponent knee
- Stamina cost: 2
- Special: +5 if opponent locked in `DOMINANT_CLINCH`

#### B8 — Knee Strike (from Ground or Clinch)

- Purpose: damage to midsection
- Attribute: `MIG`
- Skill: `Brawl`
- Requires: standing clinch OR attacker in `MOUNTED` vs. ground opponent
- Success: 3–6 damage to torso/groin; TOU check or `WINDED` 1 round
- Critical: opponent drops to one knee → `DOMINANT_CLINCH` for attacker
- Failure: leaves attacker weight-committed, -10 next defense
- Stamina cost: 2

#### B9 — Slam (Spinal Crush or Ground Pound)

- Purpose: lift and drive opponent into ground, wall, or hard object
- Attribute: `MIG`
- Skill: `Brawl`
- Requires: `REAR_CONTROL` or `MOUNTED`
- Success: 1d8 + MIG bonus crush damage; opponent `STAGGERED` 1 round;
  if against stone → +4 damage
- Failure: both fighters scramble → `NEUTRAL_CLINCH` or mutual `PRONE`
- Stamina cost: 4
- Special creatures: Barrow Draugr `Crushing Embrace` is implemented as
  this maneuver with Deathgrip modifier (+MIG for hold, no breaking)

#### B10 — Weapon Press (Push Weapon to Wound Its Owner)

- Purpose: redirect opponent's own weapon into their body
- Attribute: `NIM`
- Skill: `Brawl`
- Requires: `DOMINANT_CLINCH`, opponent armed with edged weapon
- Success: opponent's weapon deals its base damage to their own torso or
  arm (armor applies, no skill bonus); opponent `DISARMED` if they
  release grip
- Counter: opponent may sacrifice 4 HP voluntarily to retain weapon
- Failure: attempt telegraphed — opponent gets free `SHOVE` attempt
- Stamina cost: 3

#### B11 — Break and Extend Distance

- Purpose: exit grapple safely, create range
- Attribute: `NIM`
- Skill: `Brawl`
- Requires: `GRAPPLED` (any position)
- Success: both fighters standing, grapple ended; attacker has
  re-established weapon distance
- Failure: opponent may immediately attempt `B1 — Clinch Improvement`
- Stamina cost: 2
- Special: always available as fallback (replaces current `SHOVE` logic
  for grapple break)

#### B12 — Pin and Hold

- Purpose: hold opponent immobile on the ground without killing
- Attribute: `MIG`
- Skill: `Brawl`
- Requires: `MOUNTED`
- Success: opponent is `PINNED` (new condition) — cannot act; attacker
  may use free-hand strikes next round at +20 or dictate terms
- Counter: bridge escape (MIG check at -10 for bottom fighter)
- Stamina cost: 3 per round maintained
- Special: enables sub-actions `D1`, `D3`, `D7` (see Dirty Tactics below)

---

### C. Glíma Specialist Finishers

Available only to fighters with `Brawl rank 3+` or glíma-specific traits.

#### C1 — Lás ("Lock", Back Heel Trip)

- Attribute: `NIM`
- Skill: `Brawl`
- Requires: `DOMINANT_CLINCH`
- Success: hard takedown; opponent `PRONE` and `STAGGERED`; attacker
  stays standing free
- Stamina cost: 3

#### C2 — Snúningur (Hip Rotation Throw)

- Attribute: `MIG + NIM average`
- Skill: `Brawl`
- Requires: `DOMINANT_CLINCH` + attacker has lower stance than opponent
- Success: full rotation throw; opponent hits full force → 1d8 damage and
  `PRONE`; attacker may disengage or follow to ground
- Stamina cost: 4

#### C3 — Beinhnykkur (Leg Snap — submission joint lock)

- Attribute: `NIM`
- Skill: `Brawl`
- Requires: `GROUND / SIDE_CONTROL`
- Success: leg joint hyperextended; opponent has choice: tap (surrender)
  or take `TENDON_TORN` permanent wound (+30 wound penalty, permanent
  movement impairment)
- Critical: simultaneous fracture — cannot walk without aid
- Failure: opponent rolls out → `REAR_CONTROL` given to opponent
- Stamina cost: 3

#### C4 — Hnakkatak (Back-of-Neck Takedown by Hair/Nape Grip)

- Only works if opponent has hair long enough to grab (shoulder length+)
  OR a helmet with exposed nape; fails against short-cropped or bald
- Attribute: `NIM`
- Skill: `Brawl`
- Requires: standing, from any clinch position
- Success: slam head forward → opponent `PRONE`, `DAZED` 2 rounds
- Counter: immediate `D6 — Beard Grip Counter`
- Stamina cost: 2

---

### D. Dirty Tactics

Not restricted to grapple. Range: melee contact (within arm's reach).
All dirty tactics have a `WIT` counter-check for the target.
A target with `WIT ≥ 6` gets a free interrupt check (difficulty 55%)
to anticipate and partially negate the action. This represents combat
awareness, not magical sense.

#### D1 — Bite (Flesh Tear)

- Target: face (nose, ear, cheek, lip), exposed hand, throat
- Attribute: `NIM` (to get into range) vs. `WIT` interrupt
- Skill: `Brawl` rank 0 usable
- Available: always while `GRAPPLED`, `PINNED`, or `MOUNTED`;
  outside grapple at -30 (requires getting very close)
- Success: 1–3 damage, wound location is `face` or `hand`; opponent
  must pass `WIL` check or suffer `PAIN_SHOCK` — -10 all actions 1 round
  from the intimacy of the wound
- Critical success: 4–6 damage; flesh removed (nose cartilage, ear
  cartilage, cheek chunk) → permanent facial scar; `PAIN_SHOCK` no save
- Failure: attacker's face exposed — opponent‚ gets free `D2` or `D3`
- Special for undead: Draugr bite is mechanically the same but carries
  `chilling_grip` property — target must pass `WIL` or be `STAGGERED`
  from the wrongness of it
- Counter: pull back (NIM check), works better with `combat_memory` trait
- Note: humans do this. It is not exotic. Desperate men bite. Monsters
  bite deliberately.

#### D2 — Headbutt (Close Range, Standing)

- Target: nose, forehead, chin
- Attribute: `MIG`
- Skill: `Brawl` (rank 0 usable at -10)
- Available: within arm's reach, including clinch
- Success: 2–4 damage; target location `head / nose/forehead`;
  nose hit → `BLEEDING_NOSE` (vision obscured, -5 perception rolls,
  cosmetic blood in the eyes); forehead/chin → `DAZED` 1 round
- Critical: attacker's own forehead takes 1 HP from impact (always) but
  deals 5–8; nasal fracture on target
- Failure: double miss — both heads knock together; both fighters take
  1 damage flat; `STAGGERED` 1 round each
- Stamina cost: 1
- Note: This is perhaps the easiest dirty tactic — very low stamina cost,
  very short range requirement. Accessible to any fighter in a clinch.

#### D3 — Nose-Butt (Specific Nasal Crush)

- Variant of headbutt targeting nose deliberately with own nose or
  forehead bridge (rare but documented in Icelandic sagas)
- Attribute: `MIG`
- Skill: 0 (raw instinct move)
- Requires: `DOMINANT_CLINCH` or `PINNED` target
- Success: 3 damage, `BLEEDING_NOSE` condition; target also has -10
  attack from involuntary tearing/eye-watering
- Failure: attacker puts own nose at risk — opponent may redirect into
  attacker's face
- Stamina cost: 1

#### D4 — Snow in the Eyes / Sand in the Eyes

- Environmental requirement: snow/sand/loose dirt present within reach
  (barrow: dust and stone grit; winter outdoor: always available;
  summer field: player must justify)
- Attribute: `NIM` (grab and throw in one motion)
- Skill: `WIT` (knowing when to do it)
- Available: free action if enemy has just attacked and is open
- Success: target is `BLINDED` for 1–3 rounds (d3 roll); -30 to attack
  and defense; must use one action to clear eyes or blindness persists
- Critical: target cannot act next round at all (reflexively tries to
  clear eyes)
- Failure: poorly aimed — opponent gets one free attack
- Counter (WIT check): see it coming — duck/turn face, reduce to -10
  (grit only, not full blindness)
- Special: undead are not blinded by dirt in eye sockets — they don't
  have functioning eyes

#### D5 — Spit in the Eyes

- No environmental requirement; always available
- Attribute: `NIM`
- Skill: 0
- Range: within 1 pace (contact)
- Success: -10 to target's attack rolls for 1 round (blink reflex); if
  combined with `D2` (headbutt same turn as free action after the spit),
  defender gets no counter-check for the headbutt
- Failure: poorly aimed; no effect
- Counter: shield face with arm (costs defense this round)
- Special: undead are not affected by spitting (no blink reflex)

#### D6 — Beard Grip / Hair Grip (Skeggtak)

- Hair length requirement: target must have shoulder-length+ hair OR
  notable beard (chin-length+); tracked on character sheet in description
- Attribute: `NIM`
- Skill: `Brawl`
- Available: any clinch; also from outside grapple to initiate
- Success: target is forced toward attacker's direction;
  +10 to all follow-up grapple moves this round as target is off-balance;
  can transition directly to `C4 — Hnakkatak` without needing prior clinch
- On sustained hold: each round attacker holds, target has -10 to escaping
  the grapple; roots feel this in their scalp — cumulative distraction
- Failure: target twists; attacker's wrist is caught — treated as
  `B6 — Arm Trap` on the attacker for 1 round
- Stamina cost: 1
- Counter-beard grip: if holding opponent by beard, opponent may attempt
  their own beard/hair grip simultaneously (resolved simultaneously as
  purely opposed NIM checks); loser is dragged first

#### D7 — Thumb Gouge (Eye Socket Press / Pressure Point)

- Target: eye socket, temple, throat notch, groin, ear canal
- Attribute: `NIM`
- Skill: 0
- Requires: `MOUNTED`, `PINNED`, or `SIDE_CONTROL`
- Success: no structural damage; instead forces `WIL` check; failure → target
  taps out (surrender) or attempts to thrash free at -20
- Critical success: actual injury — eye gouge deals 1d4 damage and
  may give permanent partial vision impairment (serious wound to eye socket)
- Stamina cost: 1
- Counter: tuck chin, cover temples (costs next attack to be defensive)
- Special for undead: eye gouges do nothing to draugr — no nerve response

#### D8 — Ear Cup (Concussion Strike)

- Open-palm slap both ears simultaneously; disorienting concussion
- Attribute: `MIG`
- Skill: `Brawl` rank 0 usable at -10
- Requires: within arm's reach, both hands free (not if holding weapon)
- Success: target `DAZED` 1 round; ringing ears (-10 hearing-based
  perception for remainder of encounter)
- Critical: TOU check or drop prone from disorientation
- Failure: target gets head out of way; attacker's arms wide open — free
  `B7 — Elbow Strike` for target
- Stamina cost: 2
- Special: works on humans only; undead have no functional inner ear

---

### E. New Conditions Required

| Condition | Effect | Cleared By |
| --- | --- | --- |
| `CHOKED` | -4 HP per round; cannot speak or command; cumulative | Break grapple, or attacker releases |
| `ARM_LOCKED` | Cannot attack with locked arm; -40 to all attacks | `SHOVE` success or forced break |
| `PINNED` | Cannot move or attack; bottom fighter only | MIG opposed check; attacker must spend 3 stam/round to maintain |
| `BLINDED` | -30 attack and defense, 1–3 rounds | Spend one action to clear; or d3 rounds expire |
| `BLEEDING_NOSE` | -5 perception rolls; visual blood distraction | Clears after combat; no mechanical healing needed |
| `PAIN_SHOCK` | -10 all actions, 1 round | Automatic (duration only) |
| `ARM_LOCKED` | Cannot attack with locked arm | SHOVE or forced break |

---

### F. GrappleState Data Structure

New object tracking the live grapple.

```python
@dataclass
class GrappleState:
    position: str           # "clinch", "dominant_clinch", "rear_control",
                            # "mounted", "guard", "side_control",
                            # "trip_setup", "weapon_press", "neutral_clinch"
    dominant: str           # name of dominant fighter; "" if neutral
    position_round: int     # how many rounds dominant has held this position
    ground: bool            # True if both fighters are on the ground

    # Special sub-states
    throat_seized: bool     # B5 active
    weapon_pressed: bool    # B10 active; which weapon/whose
    weapon_pressed_by: str  # fighter name
    arm_locked: str         # name of fighter whose arm is locked (B6)
    choke_rounds: int       # rounds of active CHOKED condition
```

---

### G. Weapon Asymmetry in Grapple

The current system has no weapon modifier inside grapple. This must change.

| Weapon Type | In-Grapple Status | Rule |
| --- | --- | --- |
| Unarmed | Neutral | Full access to all grapple moves |
| Dagger / Seax | Advantaged | +10 to all in-grapple attacks; can target armpits and throat |
| Hand axe | Slightly hindered | -5 in-grapple attacks; haft useful for choke |
| Sword (one-hand) | Hindered | -15 in-grapple attacks; length works against it |
| Spear | Severely hindered | -30 in-grapple; must be dropped or counts as brawl action to use as grapple aid |
| Long axe / Great sword | Useless | Cannot attack inside grapple; treated as unarmed if not dropped |
| Shield | Encumbering | -10 in-grapple defense; shield boss can be used as `B9 — Slam` substitute |

AI should be less willing to initiate grapple with a sword against a
dagger-wielder. Logic hook: `choose_maneuver()` checks weapon asymmetry
table before returning `Maneuver.GRAPPLE`.

---

### H. Monster Grapple Hooks

Map specific creature abilities to the new system.

| Creature Ability | Mapped To | Special |
| --- | --- | --- |
| Deathgrip (Draugr_01) | `B6 — Arm Trap` | MIG check at -1 to break |
| Deathgrip (Draugr_02) | `B12 — Pin and Hold` | MIG at -2 to break; draugr does not tire (no stamina cost) |
| Crushing Embrace | `B9 — Slam` | Deals d8 + ongoing TOU check each round |
| Bear Mauling | `B3 — Hryggspenna` + `D1 — Bite` on same round | Creature has no `Brawl` skill cost |
| Wolf throat bite | `D1 + B5` combo | Counts as one action for wolves |
| Draugr_03 Combat Memory | Full grapple maneuver access including `C1–C4` | Was a trained warrior in life |

---

## Rollout Phases

Each phase is a discrete, testable unit. Phases are independent but
build in dependency order.

---

### Phase 1 — New Conditions and GrappleState Data Structure

**Objective:** extend `Fighter` and `ConditionType` without changing
any resolution logic.

- [ ] Add `GrappleState` dataclass to `combat_sim.py`
- [ ] Add new `ConditionType` entries: `CHOKED`, `ARM_LOCKED`, `PINNED`,
      `BLINDED`, `BLEEDING_NOSE`, `PAIN_SHOCK`
- [ ] Add `CONDITION_EFFECTS` entries for each new condition (attack/defense mods)
- [ ] Add `grapple_state: Optional[GrappleState]` field to `Fighter`
- [ ] Add `ground: bool = False` field to `Fighter`
- [ ] Update `Fighter.to_dict()` and `Fighter.from_dict()` for new fields
- [ ] Update `Fighter.tick_conditions()` to handle duration-based new conditions
- [ ] Add bleed-through skip for undead on `CHOKED` (they do not choke)
- [ ] Write unit test: Fighter can hold `CHOKED` + `PINNED` simultaneously
- [ ] Write unit test: undead does not accumulate HP loss from `CHOKED`

---

### Phase 2 — Grapple Position State Machine

**Objective:** replace flat `GRAPPLED` condition with positional state.

- [ ] Add `GrapplePosition` enum: `CLINCH`, `DOMINANT_CLINCH`,
      `NEUTRAL_CLINCH`, `REAR_CONTROL`, `MOUNTED`, `GUARD`,
      `SIDE_CONTROL`, `TRIP_SETUP`, `WEAPON_PRESS`
- [ ] Modify `resolve_control(GRAPPLE)` to create `GrappleState` with
      position `CLINCH` rather than just applying `GRAPPLED` condition
- [ ] Add position-aware modifiers: `MOUNTED` attacker gets +10 attack,
      `GUARD` bottom fighter gets +0 attack but full grapple access
- [ ] Add `REAR_CONTROL` modifiers: -20 attack for bottom, +20 for top
- [ ] Modify `choose_maneuver()` to read `grapple_state.position` and
      select positional follow-ups rather than blind repeat grapple
- [ ] Add `choose_grapple_followup()` helper: given position, return
      logical next maneuver from the new inventory
- [ ] Modify narrative printer to describe position transitions:
      "Voss forces the clinch, drives to dominant grip"
- [ ] Write unit test: after successful GRAPPLE, fighters have a
      `GrappleState` with position `CLINCH`
- [ ] Write unit test: DOMINANT_CLINCH gives correct attack modifier
- [ ] Write unit test: SHOVE correctly clears `GrappleState`

---

### Phase 3 — Entry Maneuvers (A1–A4)

**Objective:** replace current single `GRAPPLE` with four distinct
entry moves.

- [ ] Add `BROKARTOK`, `LAUSATOK`, `HRYGGSPENNA`, `TACKLE` to
      `Maneuver` enum
- [ ] Add each to `MANEUVER_STAMINA` with correct costs
- [ ] Add `"unarmed"` weapon maneuver list updates (include all 4 entries)
- [ ] Add resolution logic for each in `resolve_control()`:
  - [ ] `A1 — BROKARTOK`: clothing-grip check; success → `DOMINANT_CLINCH`
  - [ ] `A2 — LAUSATOK`: collar tie-up; success → `NEUTRAL_CLINCH` with
        immediate `B5` unlock
  - [ ] `A3 — HRYGGSPENNA`: back-wrap; success → `REAR_CONTROL` directly
  - [ ] `A4 — TACKLE`: raw charge; both prone on success
- [ ] Add trait check `"glima_brokartok"` / `"glima_lausatok"` giving +10
      to their respective entry check
- [ ] Add `BROKARTOK`-specific counter (wide-stance NIM check)
- [ ] Add `HRYGGSPENNA`-specific counter (sit-out MIG check)
- [ ] Add descriptive strings to `MANEUVER_HIT_DESC`
- [ ] Write unit test: BROKARTOK against opponent with no belt/clothing
      gets -10 modifier
- [ ] Write unit test: HRYGGSPENNA directly sets position to REAR_CONTROL

---

### Phase 4 — In-Grapple Positional Moves (B1–B12)

**Objective:** full grapple sub-game. This is the largest phase.

- [ ] Add to `Maneuver` enum: `CLINCH_IMPROVE`, `LEG_TRIP`, `HIP_THROW`,
      `GROUND_CONTROL`, `THROAT_SEIZE`, `ARM_TRAP`, `ELBOW_STRIKE`,
      `KNEE_STRIKE`, `SLAM`, `WEAPON_PRESS`, `BREAK_DISTANCE`, `PIN_HOLD`
- [ ] Gate each behind `fighter.grapple_state is not None` in
      `can_maneuver()`
- [ ] Add `MANEUVER_STAMINA` entries for each
- [ ] Add to appropriate weapon_maneuver lists (unarmed gets full access;
      weapons get subsets per asymmetry table)
- [ ] Implement `resolve_control()` extensions for each (B1–B12):
  - [ ] B1 — `CLINCH_IMPROVE`: NIM + Brawl vs. opponent; position
        advances on success
  - [ ] B2 — `LEG_TRIP`: MIG + Brawl from DOMINANT only; opponent PRONE
  - [ ] B3 — `HIP_THROW`: MIG + Brawl; requires DOMINANT + MIG ≥ 5;
        contact damage on landing; ×1.5 on stone floor
  - [ ] B4 — `GROUND_CONTROL`: both PRONE; average(MIG,NIM) vs. same
  - [ ] B5 — `THROAT_SEIZE`: MIG + Brawl; applies `CHOKED` condition;
        counter enables free `D1`
  - [ ] B6 — `ARM_TRAP`: NIM + Brawl; applies `ARM_LOCKED`; weapon
        transfer NIM check
  - [ ] B7 — `ELBOW_STRIKE`: MIG + Brawl; damage 1–4; `STAGGERED` on
        crit; -5 to attacker if not DOMINANT
  - [ ] B8 — `KNEE_STRIKE`: MIG + Brawl; damage 3–6; `WINDED` on success
  - [ ] B9 — `SLAM`: MIG + Brawl from REAR_CONTROL or MOUNTED; 1d8+MIG
        bonus; +4 on stone
  - [ ] B10 — `WEAPON_PRESS`: NIM + Brawl; redirects opponent weapon;
        sets `grapple_state.weapon_pressed = True`; opponent may sacrifice
        HP or go DISARMED
  - [ ] B11 — `BREAK_DISTANCE`: NIM + Brawl; clears GrappleState;
        replaces SHOVE for grapple break
  - [ ] B12 — `PIN_HOLD`: MIG + Brawl from MOUNTED; applies PINNED;
        stamina drain per round
- [ ] Add position validity checks: each move fails silently if called
      from wrong position (e.g., LEG_TRIP outside DOMINANT_CLINCH)
- [ ] Update `choose_grapple_followup()` with full position→maneuver map
- [ ] Update `_print_narrative_duel()` to output grapple sub-actions:
      "Voss drives a knee into the draugr's gut", "The draugr presses the
      axe back against Voss's throat" etc.
- [ ] Write unit test: B9 (SLAM) on stone floor deals +4 extra damage
- [ ] Write unit test: B10 (WEAPON_PRESS) applies damage to weapon
      owner's armor location
- [ ] Write unit test: B12 (PIN_HOLD) applies PINNED; stamina cost
      continues per round
- [ ] Write unit test: LEG_TRIP fails outside DOMINANT_CLINCH position

---

### Phase 5 — Glíma Specialist Finishers (C1–C4)

**Objective:** finishers for Brawl rank 3+ fighters and glíma-trained.

- [ ] Add to `Maneuver` enum: `GLIMA_LAS`, `GLIMA_SNUNINGUR`,
      `GLIMA_BEINHNYKKUR`, `GLIMA_HNAKKATAK`
- [ ] Gate all behind `fighter.weapon_skill >= 3 OR "glima_brok" in
      fighter.traits` check
- [ ] Implement each in `resolve_control()`:
  - [ ] C1 `GLIMA_LAS`: NIM+Brawl from DOMINANT; hard takedown → opponent
        PRONE + STAGGERED; attacker stays free
  - [ ] C2 `GLIMA_SNUNINGUR`: avg(MIG,NIM)+Brawl from DOMINANT + low
        stance condition; full rotation throw; 1d8 damage; attacker choice
        on follow-through
  - [ ] C3 `GLIMA_BEINHNYKKUR`: NIM+Brawl from SIDE_CONTROL only; joint
        lock; opponent chooses tap or permanent wound; implement
        `TENDON_TORN` wound record
  - [ ] C4 `GLIMA_HNAKKATAK`: NIM+Brawl; hair/beard length check against
        target character description; PRONE + DAZED on success
- [ ] Add hair/beard length field lookup: `fighter.traits` may include
      `"long_hair"` or `"bearded"` as descriptors checked by opponent's C4
- [ ] C4 counter: opponent C4/D6 simultaneous — both NIM opposed
- [ ] Write unit test: C3 BEINHNYKKUR fails from MOUNTED position
- [ ] Write unit test: C4 HNAKKATAK fails against fighter with
      `"short_hair"` trait

---

### Phase 6 — Dirty Tactics (D1–D8)

**Objective:** the unpredictable layer; WIT counter-check system.

- [ ] Add to `Maneuver` enum: `BITE`, `HEADBUTT`, `NOSE_BUTT`,
      `DIRT_EYES`, `SPIT_EYES`, `HAIR_GRIP`, `THUMB_GOUGE`, `EAR_CUP`
- [ ] Add stamina costs per maneuver
- [ ] Implement WIT counter-check: before any dirty tactic resolves,
      if target WIT ≥ 6, run a WIT check (55% base); success = partial
      mitigate (half effect or condition downgraded)
- [ ] Implement each in `resolve_dirty()` (new function):
  - [ ] D1 `BITE`: NIM + 0 skill; available inside grapple always;
        outside at -30; damage 1–3 or 4–6 crit; face wound sublocations;
        `PAIN_SHOCK` on WIL fail; undead bite adds `chilling_grip` tag
  - [ ] D2 `HEADBUTT`: MIG + Brawl(0); within arm's reach; damage 2–4;
        attacker takes 1 self-damage; nose → `BLEEDING_NOSE`;
        head → `DAZED`; failure = mutual 1 damage + STAGGERED both
  - [ ] D3 `NOSE_BUTT`: MIG + 0; DOMINANT_CLINCH or PINNED only;
        damage 3; `BLEEDING_NOSE`; -10 attack on target
  - [ ] D4 `DIRT_EYES`: NIM + WIT; environment check (snow/sand/dust);
        `BLINDED` d3 rounds; one action to clear; undead immune
  - [ ] D5 `SPIT_EYES`: NIM + 0; always available; -10 next round;
        synergy with D2 (headbutt loses counter window); undead immune
  - [ ] D6 `HAIR_GRIP`: NIM + Brawl; hair check; +10 all next grapple
        moves; enables C4 without prior clinch prep; counter-beard
        simultaneous check
  - [ ] D7 `THUMB_GOUGE`: NIM + 0; MOUNTED/PINNED/SIDE_CONTROL;
        WIL check or surrender; crit = actual eye damage; undead immune
  - [ ] D8 `EAR_CUP`: MIG + Brawl(0); both hands free; `DAZED` 1 round;
        ringing (-10 hearing); TOU check or PRONE on crit; failure =
        arms wide, free elbow for target
- [ ] Add `resolve_dirty()` dispatch in `resolve_fighter_action()`
- [ ] Add dirty tactics to appropriate weapon_maneuver lists (most
      available as unarmed secondary; D4 requires environment)
- [ ] Add environment check for D4: `Fighter.terrain_context` optional
      field (defaults to `"open"` which allows D4 in winter, barrow)
- [ ] Add undead immunity checks inside `resolve_dirty()`:
      D4, D5, D7, D8 do nothing to `is_undead` targets (print note)
- [ ] Write unit test: D1 (BITE) outside grapple gets -30 penalty
- [ ] Write unit test: D4 (DIRT_EYES) fails against undead
- [ ] Write unit test: D6 (HAIR_GRIP) fails against `"short_hair"` fighter
- [ ] Write unit test: D2 (HEADBUTT) deals 1 HP self-damage to attacker
      on success

---

### Phase 7 — Weapon Asymmetry in Grapple

**Objective:** weapon type affects grapple willingness and
in-grapple attack rolls.

- [ ] Add `GRAPPLE_WEAPON_MODIFIERS` dict: maps weapon type to
      `(attack_mod, willingness_mod)` tuple
- [ ] Apply `attack_mod` to all in-grapple attack maneuvers in
      `resolve_attack()` when `fighter.grapple_state is not None`
- [ ] Modify `choose_maneuver()` to check `GRAPPLE_WEAPON_MODIFIERS`
      before returning GRAPPLE/BROKARTOK: if `willingness_mod <= -20` and
      opponent has short weapon, reduce grapple probability by 50%
- [ ] Add seax/dagger +10 in-grapple bonus to `MANEUVER_STAMINA` costs
      (reduce by 1 for dagger/seax inside grapple)
- [ ] Add spear/long axe penalty: attempting any grapple move while
      holding these applies -30 unless fighter first drops weapon (free
      action), which triggers `DISARMED` condition temporarily
- [ ] Write unit test: sword fighter's grapple attempt returns correct
      -15 penalty on attack roll
- [ ] Write unit test: AI with long axe vs. dagger wielder does not
      choose GRAPPLE_ENTRY maneuvers

---

### Phase 8 — Monster Grapple Hook Wiring

**Objective:** map bestiary `sim_traits` to the new grapple moves.

- [ ] Add `"deathgrip_1"` and `"deathgrip_2"` to sim_traits in
      `undead.yaml` (UND_DRAUGR_01 and UND_DRAUGR_02)
- [ ] Add `"combat_memory"` to UND_DRAUGR_03 (already done) —
      confirm it enables C1–C4 for that fighter
- [ ] Add `"grapple_no_stamina_cost"` trait: creature does not pay
      stamina for grapple maintenance moves (draugr do not tire)
- [ ] Add `"bite_routine"` trait for wolves and bears: makes D1 part
      of every attack action after first hit
- [ ] Add `"crushing_embrace"` trait: maps to B9 (SLAM) with no
      stamina cost and auto-targeting torso
- [ ] Wire trait checks into `choose_grapple_followup()` for each trait
- [ ] Write unit test: fighter with `"grapple_no_stamina_cost"` does
      not lose stamina maintaining PIN_HOLD

---

### Phase 9 — Narrative Output

**Objective:** grapple sub-game reads like a fight, not a log.

- [ ] Write grapple position transition descriptions:
      `"clinch → dominant_clinch"` → "Voss yanks him in, pins the
      elbow, controls the hip"
- [ ] Write finisher descriptions for each C maneuver result
- [ ] Write dirty tactic hit/miss descriptions for D1–D8
- [ ] Write B-move descriptions (B1–B12 hit/miss)
- [ ] Add `"ground: True"` flag to narrative — when both fighters
      are on the ground, preface round with ground-fight framing
- [ ] Pass terrain context to narrative (barrow stone = +4 slam damage
      explained in output)
- [ ] Add WIT-counter narrative: "Voss reads the move too late — snow
      hits his eye at full force" vs. "Voss turns his face in time —
      the grit stings but he keeps his sight"
- [ ] Write unit test: narrative output for D2 (HEADBUTT) miss prints
      "both heads crack together" mutual damage description

---

### Phase 10 — Integration Tests and Balance Pass

**Objective:** everything works end-to-end; no positions get stuck.

- [ ] Run 100 automated duels: unarmed vs. unarmed — confirm no
      infinite grapple loops
- [ ] Run 50 duels: armed fighter vs. unarmed — confirm armed fighter
      does not voluntarily grapple if weapon asymmetry is strongly negative
- [ ] Run 20 duels: Voss (armed) vs. Barrow Draugr with full undead
      traits — confirm draugr uses grapple sub-system; confirm pinned
      condition does not cause infinite loops for draugr (no stamina loss)
- [ ] Run 10 duels with `"glima_brokartok"` trait fighter vs. untrained
      brawler — confirm specialist gets noticeably better outcomes
- [ ] Check that no fighter can be simultaneously `MOUNTED` and
      `STAGGERED` without that being physically valid
- [ ] Verify all new `ConditionType` entries are correctly handled in
      `to_dict()` / `from_dict()`
- [ ] Verify all new maneuvers appear in `--summary` output correctly
- [ ] Run `markdownlint` on this proposal and the updated rules section
- [ ] Update `20_SIMULATION_RULES.md` with full grapple sub-system tables
- [ ] Update `BESTIARY_SCHEMA.md` with new sim_traits: `deathgrip_1`,
      `deathgrip_2`, `grapple_no_stamina_cost`, `bite_routine`,
      `crushing_embrace`, `glima_brokartok`, `glima_lausatok`

---

## Open Questions Before Implementation

1. **GrappleState persistence across rounds** — should the position
   state live on the `Fighter` object or on a separate shared object?
   A shared object is cleaner but requires passing context to all
   resolution functions. Fighter attribute is simpler.

2. **Ground fighting and shields** — a fighter with a shield who goes
   to ground: does the shield remain defensive or become an anchor?
   Current proposal: shield loses defense bonus entirely on GROUND;
   shield boss can be used once as SLAM sub-variant.

3. **Two grapple entrants in a group fight** — if a third person attacks
   a grappled pair, which fighter is targeted? Current proposal: the
   `MOUNTED` or `DOMINANT` fighter is assumed exposed; the `PINNED`
   fighter is protected by the attacker's body.

4. **Trait `"long_hair"` / `"short_hair"` for Voss** — Voss has
   short-cropped hair per his statblock. C4 and D6 should fail against
   him. Do we add this to his statblock `traits` list explicitly?
   Recommendation: yes.

5. **Bite and infection risk** — flesh bites in a dirty fight carry
   infection. The current wound system supports `infected: bool` on
   wound records. Should bite wounds have elevated infection chance?
   Recommendation: yes, bite wounds set `infection_chance: +20%` flag.

---

## Reference Sources for Implementation

- Glíma styles: `06_RESEARCH_NOTES_OUTLAWRY.md` (if populated) and external
  Icelandic wrestling codification
- Working grapple mechanics reference: `20_SIMULATION_RULES.md` §4
  (current GRAPPLE maneuver), §5 (wound records)
- Undead integration hooks: §4.1 (Undead Combat Mechanics, added prior)
- Bestiary monster abilities: `data/bestiary/undead.yaml` Deathgrip,
  Crushing Embrace entries
- Current `Fighter` dataclass: `scripts/combat_sim.py` lines 200–440
