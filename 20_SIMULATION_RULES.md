# Iron Ledger — Simulation Rules

## Iron Ledger Rules — Complete Simulation System

**Purpose:** This is the authoritative game system for the Rimevegr living
world simulation. All mechanics are designed for computer resolution via
Python scripts. No human dice rolling is needed.

---

## 1. Attributes (1-10 Scale)

Every character has six attributes rated 1-10.

| Attribute  | Abbr | Governs                                             |
| ---------- | ---- | --------------------------------------------------- |
| Might      | MIG  | Physical strength, melee damage, carrying capacity  |
| Nimbleness | NIM  | Speed, coordination, stealth, ranged accuracy       |
| Toughness  | TOU  | Endurance, cold resistance, wound recovery, health  |
| Wits       | WIT  | Perception, cunning, tactics, learning speed        |
| Will       | WIL  | Courage, leadership, mental fortitude, intimidation |
| Wyrd       | WYR  | Fate-sense, rune-affinity, spirit-sensitivity       |

### Attribute Ranges

| Range | Description      | Typical Bearer                     |
| ----- | ---------------- | ---------------------------------- |
| 1-2   | Weak / Deficient | Children, the infirm               |
| 3-4   | Below average    | Common thralls, elderly            |
| 5     | Average human    | Typical farmer or fisher           |
| 6-7   | Above average    | Trained fighter, skilled craftsman |
| 8-9   | Exceptional      | Named Man, veteran champion        |
| 10    | Legendary        | Once-in-a-generation               |

### Wyrd Special Rules

Most people have Wyrd 1-2. Values of 4+ indicate genuine supernatural
sensitivity. Characters with high Wyrd:

- Can attempt galdr (rune scribing) and seiðr (spirit communion)
- Sense the Hush before it falls
- Are more vulnerable to supernatural horror
- May receive visions (Wyrd-reading) but always at personal cost

---

## 2. Skills (0-5 Ranks)

Skills represent trained competency. Rank 0 means untrained (may still
attempt if the action allows it, at heavy penalty).

### Combat Skills

| Skill   | Governs                                           |
| ------- | ------------------------------------------------- |
| Axes    | Axes, hatchets, woodcutting tools used as weapons |
| Blades  | Swords, seaxes, long knives                       |
| Spears  | Spears, javelins, improvised pole weapons         |
| Bows    | Short bows, hunting bows, slings                  |
| Shields | Shield defense, shield bash, formation fighting   |
| Brawl   | Unarmed fighting, wrestling, grappling            |

### Survival Skills

| Skill      | Governs                                                |
| ---------- | ------------------------------------------------------ |
| Forage     | Gathering food, identifying edible plants, trapping    |
| Track      | Following trails, reading sign, hunting                |
| Navigate   | Pathfinding, dead reckoning, reading stars and terrain |
| Shelter    | Building camps, fire-craft, cold weather survival      |
| Heal       | Treating wounds, setting bones, herbal medicine        |
| Seamanship | Sailing, rowing, longship handling, reading tides      |

### Social Skills

| Skill      | Governs                                             |
| ---------- | --------------------------------------------------- |
| Command    | Giving orders, maintaining discipline, rallying men |
| Deceive    | Lying, misdirection, concealing intentions          |
| Intimidate | Threats, menacing presence, breaking will           |
| Bargain    | Negotiation, trade, assessing fair value            |
| Persuade   | Convincing, inspiring, appealing to reason or honor |

### Craft Skills

| Skill       | Governs                                       |
| ----------- | --------------------------------------------- |
| Smithing    | Metalwork, weapon/armor repair, tool-making   |
| Woodcraft   | Carpentry, boatbuilding, fortification        |
| Leatherwork | Armor repair, belt/saddle making, hide curing |

### Lore Skills

| Skill         | Governs                                                |
| ------------- | ------------------------------------------------------ |
| Rune-lore     | Galdr (rune carving and chanting), reading rune-stones |
| Spirit-lore   | Seiðr (spirit communion, ancestor speaking)            |
| Wyrd-reading  | Fate divination, casting lots, reading omens           |
| Sagas         | History, law, genealogy, old knowledge                 |
| Weather-sense | Predicting weather, reading sky and wind patterns      |

---

## 3. Resolution System

All action resolution is percentage-based, computed by `engine.py`.

### Base Success Chance

```text
success_chance = (attribute × 5) + (skill × 10) + 15
```

This gives a range from 20% (attribute 1, skill 0) to 95% cap.

### Modifiers (Applied Additively)

| Condition              | Modifier                |
| ---------------------- | ----------------------- |
| Favorable conditions   | +10 to +20              |
| Proper tools/equipment | +5 to +15               |
| Unfavorable conditions | -10 to -20              |
| Wounded (Light)        | -5                      |
| Wounded (Serious)      | -15                     |
| Wounded (Critical)     | -30                     |
| Exhausted              | -10                     |
| Frostbitten            | -10 per affected limb   |
| Rime-Fog               | -10 (perception/ranged) |
| Driving Snow           | -20 (all physical)      |
| Rime Storm             | -30 (all physical)      |
| The Hush               | -20 (all sound-based)   |
| High morale (band 5)   | +5                      |
| Low morale (band 1-2)  | -10                     |
| Outnumbered 2:1        | -15                     |
| Shield wall formation  | +15 (defense)           |
| Darkness (no torch)    | -20                     |

### Final Chance

```text
final_chance = clamp(success_chance + sum(modifiers), 5, 95)
```

Always at least 5% chance of success and 5% chance of failure.

### Degrees of Success

| Roll vs Final Chance        | Result           |
| --------------------------- | ---------------- |
| Roll <= final_chance × 0.20 | Critical success |
| Roll <= final_chance        | Success          |
| Roll > final_chance         | Failure          |
| Roll > 95                   | Critical failure |

### Opposed Checks

When two characters oppose each other:

```text
attacker_roll = random(1, 100)
defender_roll = random(1, 100)

attacker_margin = attacker_final_chance - attacker_roll
defender_margin = defender_final_chance - defender_roll

winner = whoever has higher positive margin
# If both fail, status quo holds
```

---

## 4. Combat System

Combat is resolved round-by-round via `combat_sim.py`.

### Initiative

```text
initiative = (Nimbleness × 3) + (Wits × 2) + weapon_speed + random(1, 20)
```

Higher initiative acts first. Ties broken by Nimbleness, then Wits.

### Weapon Speed Modifiers

| Weapon Type         | Speed                           |
| ------------------- | ------------------------------- |
| Dagger / Seax       | +6                              |
| Hand axe            | +3                              |
| Sword               | +4                              |
| Spear (one-hand)    | +5                              |
| Long axe (two-hand) | +0                              |
| Great sword         | +1                              |
| Bow                 | +2 (ranged, fires before melee) |

### Attack Resolution

```text
attack_chance = (attack_attribute × 5) + (weapon_skill × 10) + 15 + modifiers

# Attack attribute = Might for melee, Nimbleness for ranged
```

### Defense Resolution

```text
defense_chance = (Nimbleness × 5) + (Shields × 10) + armor_dodge + modifiers

# No shield skill = Nimbleness × 5 + 5 (basic dodge only)
```

If attack succeeds and defense fails: **hit landed**. If both succeed:
compare margins (attacker wins ties). If attack fails: miss regardless of
defense.

### Hit Location (d100)

| Roll   | Location  | Damage Multiplier |
| ------ | --------- | ----------------- |
| 01-10  | Head      | ×1.5              |
| 11-40  | Torso     | ×1.0              |
| 41-50  | Right Arm | ×0.8              |
| 51-60  | Left Arm  | ×0.8              |
| 61-80  | Legs      | ×0.9              |
| 81-90  | Hands     | ×0.6              |
| 91-100 | Feet      | ×0.6              |

### Damage Calculation

```text
raw_damage = weapon_base_damage + (Might / 3, rounded down)
armor_reduction = armor_value_at_location
final_damage = max(0, (raw_damage × location_multiplier) - armor_reduction)
```

### Weapon Damage Table

| Weapon              | Base Damage | Notes                      |
| ------------------- | ----------- | -------------------------- |
| Fist / Kick         | 2           | Always available           |
| Dagger / Seax       | 4           | Concealable                |
| Hand axe            | 6           | Standard Svarthird weapon  |
| Sword               | 7           | Expensive, higher status   |
| Spear (one-hand)    | 6           | See §4.2 reach system      |
| Long axe (two-hand) | 9           | Devastating but slow       |
| Great sword         | 8           | Rare in the Rimevegr       |
| Short bow           | 5           | Effective to 30m           |
| Javelin             | 5           | One-use ranged, then spear |

### Armor Table

| Armor Type                  | Torso      | Arms | Legs | Head | Weight |
| --------------------------- | ---------- | ---- | ---- | ---- | ------ |
| None (wool/leather clothes) | 0          | 0    | 0    | 0    | 0      |
| Thick leather               | 2          | 1    | 1    | 0    | 3 kg   |
| Padded gambeson             | 3          | 2    | 1    | 0    | 5 kg   |
| Chainmail shirt             | 5          | 3    | 0    | 0    | 12 kg  |
| Chainmail hauberk           | 5          | 3    | 3    | 0    | 18 kg  |
| Iron helm                   | 0          | 0    | 0    | 4    | 2 kg   |
| Wooden shield               | +3 defense | —    | —    | —    | 4 kg   |
| Iron-rimmed shield          | +5 defense | —    | —    | —    | 6 kg   |

---

## 4.1 Undead Combat Mechanics

Undead are not impaired by wounds the way the living are. Set `is_undead:
true` in the Fighter JSON to activate all of the following.

### Bleeding Immunity

Undead have no circulating blood. Any entity with `"bleeding"` in their
`resistances` list accumulates zero bleed per round regardless of wound
severity. Pass `resistances: ["bleeding", ...]` in the fighter JSON.

### Pain Immunity (Unfeeling)

Undead do not feel pain. Any entity with `is_undead: true` or `"unfeeling"`
in their `traits` list has `wound_penalty = 0` at all times. Wounds reduce
HP and can destroy them, but do not impair their attack or defense rolls.

### No Daze or Stagger from Wounds

Living fighters can be dazed (serious/critical head blow) or staggered
(critical torso blow). Undead are immune to both — structural damage to the
skull or chest does not shock a nervous system that no longer functions.

### Stance Logic

Undead don't self-preserve. They never adopt DEFENSIVE or BALANCED stance
based on low HP or low stamina. MIG ≥ 6 → AGGRESSIVE; otherwise BALANCED.
They press forward until destroyed.

### No Counter-Attacks

Undead without the `"combat_memory"` trait cannot execute Nachreisen
counter-attacks. Their movements are purposeful but not tactically
responsive — they advance, they do not exploit openings.

### Sim Trait Reference

| Trait tag             | Effect                                                            |
| --------------------- | ----------------------------------------------------------------- |
| `unfeeling`           | Wound penalty = 0 (no daze, no stagger, no attack impairment)     |
| `terrifying_presence` | Pre-battle WIL check; failure → opponent STAGGERED 2 rounds       |
| `combat_memory`       | Re-enables counter-attacks for undead with retained martial skill |
| `ancient_resilience`  | Incoming weapon damage halved (min 1)                             |

---

## 4.2 Weapon Reach and Distance

Every weapon has a physical length. A longer weapon creates a threat zone
that a shorter-weapon fighter must penetrate to land a blow. The fight
engine tracks a shared **distance band** between two combatants each round.

### Distance Bands

| Band | Name    | Approx. range | Optimal weapons              |
| ---- | ------- | ------------- | ---------------------------- |
| 0    | GRAPPLE | 0–40 cm       | unarmed, grapple entry       |
| 1    | CLOSE   | 40–90 cm      | dagger, seax, hand axe       |
| 2    | MELEE   | 90–150 cm     | sword, mace (default start)  |
| 3    | LONG    | 150–250 cm    | spear, long axe, great sword |

Default starting distance is **MELEE (2)** — standard fighting distance for
two combatants who have closed to engage.

### Weapon Reach Table

| Weapon                | Reach tier | Min band | Max band | Foul band   |
| --------------------- | ---------- | -------- | -------- | ----------- |
| Unarmed / fist        | 0          | 0        | 0        | —           |
| Dagger, seax          | 1          | 0        | 1        | —           |
| Hand axe, mace        | 2          | 0        | 2        | —           |
| Sword                 | 3          | 1        | 2        | —           |
| Long axe, great sword | 4          | 2        | 3        | GRAPPLE (0) |
| Spear                 | 5          | 2        | 3        | CLOSE (1)   |

**Foul band** — if the distance drops to this band or below, the weapon is
driven inside its own guard. The wielder can only strike with the haft:
attack −30, damage base 3 (blunt), labelled `haft_only` in simulation
output.

### Attack Penalties by Distance

```text
Too far  (distance > max_band): −20 per band above maximum
Too close (distance < min_band): −15 per band below minimum
Fouled   (distance ≤ foul_band): −30 attack, weapon_base overridden to 3
In range (min_band ≤ distance ≤ max_band): no modifier
```

**Key matchups:**

- Spear vs sword at LONG (3): spear −0, sword −20 → decisive spear
advantage
- Spear vs sword at MELEE (2): both −0 → neutral fight
- Spear vs sword at CLOSE (1): spear fouled −30 (haft only), sword −0 →
sword wins
- Dagger vs sword at MELEE (2): dagger −20 → dagger fighter must close to
CLOSE first
- Unarmed vs sword at MELEE (2): fist −40 → must close two bands

### Distance Management Maneuvers

**STEP_IN** — Close distance by one band.

- As an action: costs 1 stamina.
- As a free reaction: triggered automatically when the opponent's
attack-type maneuver misses and the defender's weapon reach is ≤ the
attacker's. No stamina cost; does not consume the fighter's action slot.

**STEP_BACK** — Open distance by one band.

- As an action: costs 1 stamina.
- No free-reaction variant.

**SWITCH_WEAPON** — Draw a secondary carried weapon and stow the active
one.

- Available only when the fighter has at least one weapon in their
`secondary_weapons` list.
- Costs 1 stamina. Distance does not change.
- `weapon_type`, `weapon_base`, `weapon_speed`, `weapon_reach`, and
`weapon_size` all update immediately to the new active weapon. The old
weapon is pushed to the back of the secondary list.
- If the fighter is DISARMED when this maneuver resolves, the condition is
cleared (drawing a backup counts as rearming).
- AI trigger A — **foul range**: when `reach_pen ≤ −30` (weapon fouled by
distance) and a smaller secondary is available, the AI draws it instead of
attacking blind.
- AI trigger B — **tight terrain**: when terrain is `tight` or `very_tight`
and the active weapon is size ≥ 4, the AI switches to the best secondary of
size ≤ 2 before attempting `STEP_BACK` or `GUARD`.
- Typical scenario: spearman rushed to CLOSE draws his seax rather than
jabbing with the haft.

### Grapple Entry Distance Gate

All grapple initiation maneuvers (BROKARTOK, LAUSATOK, HRYGGSPENNA, TACKLE,
and the basic GRAPPLE control maneuver) require `current_distance ≤ 1`
(CLOSE or GRAPPLE). At MELEE or LONG range the entry is blocked — the
fighter must STEP_IN first.

This means an unarmed fighter facing a swordsman at default MELEE distance
must spend at least one action closing before a throw is possible.

---

## 4.3 Weapon Size and Terrain Constraints

### Weapon size tiers

| Tier | Weapon                     | Approx. length |
| ---- | -------------------------- | -------------- |
| 0    | unarmed                    | —              |
| 1    | dagger, seax               | 20–35 cm       |
| 2    | hand axe, mace, shield     | 50–70 cm       |
| 3    | sword, generic, improvised | 70–110 cm      |
| 4    | great sword, long axe      | 120–160 cm     |
| 5    | spear                      | 180–260 cm     |

### Space / terrain classification

| `terrain_context`                 | Tier       | Examples                       |
| --------------------------------- | ---------- | ------------------------------ |
| `open`, `stone`, `winter`, `sand` | free       | field, courtyard, shore        |
| `ship`, `interior`, `forest`      | moderate   | longhouse, tavern, sparse wood |
| `narrow`, `forest_dense`          | tight      | corridor, alley, dense thicket |
| `crowd`                           | packed     | surrounded by combatants       |
| `barrow`, `low_ceiling`           | very_tight | burial mound, mine drift       |

### Attack modifier — space × weapon size

| Space      | sz 0 | sz 1 | sz 2 | sz 3 | sz 4 | sz 5 |
| ---------- | ---- | ---- | ---- | ---- | ---- | ---- |
| free       | 0    | 0    | 0    | 0    | 0    | 0    |
| moderate   | 0    | 0    | 0    | −5   | −15  | −25  |
| tight      | +5   | +5   | 0    | −10  | −25  | −40  |
| very_tight | +10  | +15  | +5   | −20  | −40  | −60  |
| packed     | 0    | +5   | 0    | −10  | −20  | −30  |

Short weapons gain an attack bonus in tight/very_tight space. The dagger
fighter or unarmed grappler is genuinely advantaged inside a burial mound.

### Stamina surcharge — per offensive/control action

| Space      | sz 0 | sz 1 | sz 2 | sz 3 | sz 4 | sz 5 |
| ---------- | ---- | ---- | ---- | ---- | ---- | ---- |
| free       | 0    | 0    | 0    | 0    | 0    | 0    |
| moderate   | 0    | 0    | 0    | 0    | +1   | +1   |
| tight      | 0    | 0    | 0    | +1   | +2   | +3   |
| very_tight | 0    | 0    | +1   | +2   | +3   | +4   |
| packed     | 0    | 0    | 0    | +1   | +2   | +2   |

Applies to attack, control, and grapple-entry maneuvers only; not to GUARD,
STEP_IN, STEP_BACK, STAND.

### Special rules

**HEAVY_BLOW blocked in very_tight.** No room for the overhead arc in a
barrow or low-ceiling cellar.

**STEP_BACK blocked in very_tight.** No exit in a dead-end tunnel or
collapsed structure.

**Polearm (sz 5) in very_tight = haft-only.** The shaft cannot be levelled
— same `haft_only` override as reach fouls: base damage 3, −60 attack
modifier.

**Prone + large weapon.** A fighter on the ground adds an extra penalty per
tier above sz 3: sz 4 (great sword, long axe) adds −15; sz 5 (spear) adds
−30. Stacks with normal prone penalties and reach penalties.

**Friendly fire in packed/very_tight.** A large-weapon fighter (sz ≥ 4) who
misses an attack in packed or very_tight space has a chance of clipping an
ally on the backswing: 10 % at sz 4, 20 % at sz 5. Target is a random
living ally. Damage is `weapon_base ÷ 2` (no defense roll — the ally had no
warning).

**Auto-crowd in skirmish.** When `run_skirmish` starts with six or more
total fighters and all carry `open` terrain, terrain is upgraded to `crowd`
for all participants. Six people hacking at each other leave no clean swing
room.

### Interaction with §4.2 reach system

Both penalty systems apply simultaneously and stack. A spear fouled by
reach at CLOSE range and fighting in a `narrow` corridor accumulates both
penalties. A dagger wielder closing at LONG distance incurs reach penalty
but gains the tight-space bonus once the terrain is `narrow` — net penalty
is smaller than in open ground.

---

## 4.4 Grappling and Glíma

### Awareness Model

Grappling replaces the flat `GRAPPLE` maneuver with a full positional
sub-game. Once two fighters are locked together the fight becomes a series
of opposed checks for dominant position, with each position unlocking a
distinct menu of follow-up moves. Short weapons gain inside a grapple; long
weapons become liabilities.

### Distance Gate

All grapple entry maneuvers require `current_distance ≤ 1` (CLOSE band or
already at GRAPPLE range). Attempting a grapple entry from MELEE or LONG
distance fails automatically. The AI is aware of this gate and will only
attempt grapple entry after a `STEP_IN` has succeeded.

### Grapple Position State Machine

Once a grapple entry succeeds, both fighters are assigned a shared
`GrappleState` object. The `position` field is one of nine values:

| Position          | Description                                                   |
| ----------------- | ------------------------------------------------------------- |
| `clinch`          | Default entry; neither fighter dominant                       |
| `dominant_clinch` | Attacker controls grips, hips inside, options open            |
| `neutral_clinch`  | Contested grip; both fighters seeking opening                 |
| `rear_control`    | Attacker behind opponent; most dominant standing position     |
| `mounted`         | Attacker on top on the ground; dominant striking position     |
| `guard`           | Bottom fighter wraps legs around attacker; limited but active |
| `side_control`    | Attacker on top with weight on chest; no leg wrap             |
| `trip_setup`      | One-round telegraph; attacker coiled for a trip               |
| `weapon_press`    | Attacker is redirecting opponent's blade into its owner       |

Position changes via opposed checks each round. `GrappleState` also tracks:
`dominant` (fighter name or empty string), `position_round`, `ground` flag,
`throat_seized`, `weapon_pressed`, `weapon_pressed_by`, `arm_locked`, and
`choke_rounds`.

### A. Grapple Entry Maneuvers

These are the four ways to initiate a grapple. All require CLOSE or GRAPPLE
distance. All are resolved against the same opposed check framework.

| ID  | Maneuver                          | Eng. attribute | Result on success                        | Special                                                     |
| --- | --------------------------------- | -------------- | ---------------------------------------- | ----------------------------------------------------------- |
| A1  | `BROKARTOK` — belt and thigh grip | MIG vs. NIM    | `dominant_clinch`                        | +10 if opponent wears a belt; -10 if no belt grip available |
| A2  | `LAUSATOK` — collar tie-up        | NIM vs. NIM    | `neutral_clinch` with B5 unlock          | Cannot be used if attacker carries a shield                 |
| A3  | `HRYGGSPENNA` — back-wrap         | MIG vs. MIG    | `rear_control` immediately               | Requires a prior feint success or opponent PRONE/DISARMED   |
| A4  | `TACKLE` — waist charge           | MIG (no skill) | both `PRONE`, attacker in `side_control` | -20 if attacker is armed; bypasses shield completely        |

Counter-checks on failure: BROKARTOK → wide-stance NIM drop; HRYGGSPENNA →
sit-out MIG check. A successful counter returns the position to
`neutral_clinch` rather than giving the attacker the entry.

### B. In-Grapple Positional Moves

All require an active `GrappleState` on both fighters. All cost stamina.
Each resolves as an opposed check and may advance or regress the
`GrappleState.position` field.

| ID  | Maneuver         | Requires                          | Attribute   | Stamina | Outcome on success                                                |
| --- | ---------------- | --------------------------------- | ----------- | ------- | ----------------------------------------------------------------- |
| B1  | `CLINCH_IMPROVE` | any clinch                        | NIM         | 1       | Advance position toward dominant                                  |
| B2  | `LEG_TRIP`       | `dominant_clinch`                 | MIG         | 3       | Opponent PRONE; attacker chooses to follow or stay standing       |
| B3  | `HIP_THROW`      | `dominant_clinch`, MIG ≥ 5        | MIG         | 4       | Opponent PRONE, 1d6 landing damage (×1.5 on stone)                |
| B4  | `GROUND_CONTROL` | both PRONE                        | MIG/NIM avg | 2       | Attacker → `mounted`; opponent → `guard`                          |
| B5  | `THROAT_SEIZE`   | `dominant_clinch` or `mounted`    | MIG         | 2       | Opponent gains `CHOKED` condition                                 |
| B6  | `ARM_TRAP`       | any clinch                        | NIM         | 2       | Opponent's weapon arm `ARM_LOCKED`; -40 attack                    |
| B7  | `ELBOW_STRIKE`   | any clinch                        | MIG         | 2       | 1–4 damage to head/torso; `STAGGERED` on critical                 |
| B8  | `KNEE_STRIKE`    | standing clinch or `mounted`      | MIG         | 2       | 3–6 torso/groin damage; TOU check or `WINDED`                     |
| B9  | `SLAM`           | `rear_control` or `mounted`       | MIG         | 4       | 1d8 + MIG crush damage; `STAGGERED`; +4 vs. stone                 |
| B10 | `WEAPON_PRESS`   | `dominant_clinch`, opponent armed | NIM         | 3       | Opponent's own weapon deals base damage to self                   |
| B11 | `BREAK_DISTANCE` | any grapple                       | NIM         | 2       | Grapple ends; both standing; attacker re-establishes weapon range |
| B12 | `PIN_HOLD`       | `mounted`                         | MIG         | 3/round | Opponent `PINNED`; attacker free-strikes at +20 next round        |

### C. Glíma Specialist Finishers

Available only to fighters with `Brawl rank ≥ 3` or a glíma-specific trait
(`glima_brokartok`, `glima_lausatok`, `glima_hryggspenna`).

| ID  | Maneuver                     | Requires                      | Attribute   | Stamina | Outcome                                                                  |
| --- | ---------------------------- | ----------------------------- | ----------- | ------- | ------------------------------------------------------------------------ |
| C1  | `GLIMA_LAS` — back heel trip | `dominant_clinch`             | NIM         | 3       | Opponent PRONE and STAGGERED; attacker stays standing free               |
| C2  | `SNUNINGUR` — hip rotation   | `dominant_clinch`, low stance | MIG/NIM avg | 4       | 1d8 damage, PRONE; full rotation throw                                   |
| C3  | `BEINHNYKKUR` — leg snap     | `side_control`                | NIM         | 3       | Joint lock; opponent surrenders or takes permanent tendon wound          |
| C4  | `HNAKKATAK` — nape takedown  | any clinch                    | NIM         | 2       | PRONE + DAZED 2 rounds; requires opponent with long hair or exposed nape |

### D. Dirty Tactics

Dirty tactics do not require an active grapple. Range is melee contact
(arm's reach) for all of them. Every dirty tactic triggers a `WIT`-based
counter check: a target with `WIT ≥ 6` gets a free interrupt check at
difficulty 55% to partially negate the action.

| ID  | Maneuver                        | Available                                                      | Attribute   | Stamina | Effect on success                                                      |
| --- | ------------------------------- | -------------------------------------------------------------- | ----------- | ------- | ---------------------------------------------------------------------- |
| D1  | `BITE` — flesh tear             | always while GRAPPLED, PINNED, or MOUNTED; -30 outside grapple | NIM vs. WIT | 1       | 1–3 damage (face/hand); `PAIN_SHOCK` 1 round                           |
| D2  | `HEADBUTT` — close strike       | arm's reach                                                    | MIG         | 1       | 2–4 head damage; `BLEEDING_NOSE` or `DAZED` by location                |
| D3  | `NOSE_BUTT` — nasal crush       | `dominant_clinch` or target PINNED                             | MIG         | 1       | 3 damage, `BLEEDING_NOSE`; -10 attack from eye-watering                |
| D4  | `DIRT_EYES` — sand/snow in eyes | requires loose debris in environment                           | NIM/WIT     | 0       | `BLINDED` 1d3 rounds; must spend an action to clear                    |
| D5  | `SPIT_EYES` — blink reflex      | within one pace; always available                              | NIM         | 0       | -10 attack 1 round; enables free HEADBUTT counter-check                |
| D6  | `HAIR_GRIP` — skeggtak          | any clinch; target needs shoulder-length hair or notable beard | NIM         | 1       | Target dragged; +10 to follow-up grapple; direct path to C4            |
| D7  | `THUMB_GOUGE` — pressure point  | `mounted`, `pinned`, or `side_control`                         | NIM         | 1       | WIL save or surrender; critical → 1d4 eye damage + partial vision loss |
| D8  | `EAR_CUP` — concussion slap     | arm's reach, two free hands                                    | MIG         | 2       | `DAZED` 1 round; TOU check or `PRONE` on critical                      |

**Hair and beard requirement for hair-based tactics:** The fighter record
includes a `hair` field (`short`, `medium`, `long`). D6 and C4 both check
this field; they fail automatically against a fighter with `hair ==
"short"`.

### E. New Conditions

| Condition       | Attack mod | Defense mod | Cleared by                                             |
| --------------- | ---------- | ----------- | ------------------------------------------------------ |
| `CHOKED`        | —          | —           | Grapple break; attacker releases; 4 HP drain per round |
| `ARM_LOCKED`    | -40        | 0           | SHOVE success or forced break                          |
| `PINNED`        | -50        | -30         | MIG opposed check at -10 for bottom fighter            |
| `BLINDED`       | -30        | -30         | Spend one action to clear, or 1d3 rounds expire        |
| `BLEEDING_NOSE` | 0          | 0           | Clears after combat; no mechanical healing needed      |
| `PAIN_SHOCK`    | -10        | -10         | Automatic (1 round only)                               |

`CHOKED` additionally blocks speech and commands. Undead fighters are
immune to `CHOKED` — they have no functioning airway.

### F. Weapon Asymmetry in Grapple

A fighter's weapon type affects how willing the AI is to enter a grapple
(stored in `GRAPPLE_WEAPON_MODIFIERS`) and how effective weapon-based
in-grapple attacks are:

| Weapon                 | AI grapple willingness | In-grapple attack mod |
| ---------------------- | ---------------------- | --------------------- |
| Unarmed                | +0                     | +20                   |
| Dagger / seax          | +10                    | +15                   |
| Hand axe               | -5                     | 0                     |
| Mace                   | -5                     | 0                     |
| Sword (one-hand)       | -15                    | -10                   |
| Spear                  | -30                    | -20                   |
| Long axe / great sword | -40                    | -30                   |

Long weapons at -30 or -40 willingness will effectively never initiate a
grapple unless the AI is already in one from a reactive entry.

### G. Monster Grapple Hooks

Creature traits map directly to existing grapple moves:

| Trait                       | Mapped move        | Special rule                                |
| --------------------------- | ------------------ | ------------------------------------------- |
| `Deathgrip` (Draugr_01)     | B6 — Arm Trap      | MIG break check at -1                       |
| `Deathgrip` (Draugr_02)     | B12 — Pin Hold     | MIG break at -2; no stamina cost for draugr |
| `Crushing Embrace`          | B9 — Slam          | 1d8 ongoing each round; TOU check           |
| Bear mauling                | B3 + D1 same round | Creature skips Brawl skill cost             |
| Wolf throat bite            | D1 + B5 combo      | Counts as one action for wolves             |
| `combat_memory` (Draugr_03) | Full C1–C4 access  | Was a trained grappler in life              |

### H. Fighter Fields Added by This System

Three fields on the `Fighter` dataclass support grapple mechanics:

- `grapple_state: Optional[GrappleState]` — shared state object; `None`
when not grappling.
- `brawl_skill: int` — `Brawl` ranks (0–5); used in all grapple opposed
checks and gates C-tier finishers at rank ≥ 3.
- `glima_mode: str` — empty string or one of `"brokartok"`,
`"lausatok"`, `"hryggspenna"` to indicate training style.
- `wants_nonlethal: bool` — if `True`, AI prefers submission moves (B12,
C3, B11) over damaging ones.
- `hair: str` — `"short"` | `"medium"` | `"long"`; gates D6 and C4.

---

## 4.5 Surprise and Awareness

### Overview

Awareness determines whether a fighter enters combat with full faculties or
is caught mid-thought with their sword still on their hip. It is a
pre-combat state, not a condition that develops during a fight — though
darkness and loud ambient noise can prolong effective unawareness across
multiple rounds.

### Fighter Fields

- `aware: bool` — defaults to `True`. Set to `False` when the fighter
does not know combat has started (ambush, wake-up attack, shot from
concealment, etc.).
- `ambient: list` — list of `AmbientCondition` string values active for
this fighter at fight start. Independent per fighter: one side may be in
darkness while the other is not.

### AmbientCondition Values

| Value      | Description                                                                                                         |
| ---------- | ------------------------------------------------------------------------------------------------------------------- |
| `darkness` | Fighter cannot see. Approach from any direction goes undetected. Applies `BLINDED` for the duration.                |
| `noise`    | Loud ambient sound (waterfall, forge, crowd). Flanking and rear approaches cannot be heard. Does not apply BLINDED. |
| `obscured` | Fog, heavy rain, dense smoke. Vision is degraded but not absent. -10 attack and defense.                            |

### The Surprise Round

When any fighter has `aware=False` at fight start:

1. The unaware fighters receive the `UNAWARE` condition (1 round duration).
2. The fight log records a `"type": "surprise_round"` pre-battle entry
listing which fighters are unaware.
3. In round 1 initiative: all fighters with `UNAWARE` are sorted **after**
all aware fighters regardless of NIM or WIT score.
4. While `UNAWARE` is active:
   - Defense modifier: -50 (the fighter is not set for combat).
   - No counter-attacks are available (they cannot react to a defended
hit).
   - No free reactions (step-in after long-weapon miss is blocked).
   - Only `GUARD` is available as a forced maneuver — the fighter cannot
choose any offensive action.
5. At the end of round 1 the `UNAWARE` condition expires automatically via
the standard `tick_conditions()` pass.

### Darkness (`ambient: ["darkness"]`)

A fighter with `"darkness"` in their `ambient` list at fight start is
marked `BLINDED` with a persistent duration (9999 rounds) immediately
before round 1.

`BLINDED` effects: -30 attack, -30 defense, no visual targeting.

The condition persists until explicitly cleared by the caller (e.g., a
torch is lit, dawn breaks). Clearing is done by removing `BLINDED` from the
fighter's condition list and removing `"darkness"` from `ambient`.

**Interactions:**

- A fighter in darkness who is also `UNAWARE` has both -50 (UNAWARE,
round 1 only) and -30 (BLINDED, ongoing) stacked on their defense.
- Undead fighters with `"no_eyes"` in their traits are immune to BLINDED
from darkness — they do not rely on sight.

### Noise (`ambient: ["noise"]`)

Noise does not apply BLINDED. Its mechanical effect is narrative: the
caller should treat any `UNAWARE` state caused by a rear approach as valid
even when the target has high WIT, since the target never heard the
approach. The system itself does not add a penalty for `noise` alone — that
is handled by the `aware=False` + `UNAWARE` flow above.

### Worked Examples

**Ambush from concealment:**

```python
target.aware = False     # did not see attacker step out of shadow
attacker.aware = True

run_duel(attacker, target)
# Pre-battle log: {"type": "surprise_round", "unaware": ["target_name"]}
# Round 1: attacker acts first; target has UNAWARE (-50 def); no counter
# Round 2+: normal initiative
```

**Night fight, both sides blind:**

```python
for f in [fighter_a, fighter_b]:
    f.ambient = ["darkness"]

run_duel(fighter_a, fighter_b)
# Both receive persistent BLINDED before round 1
# Initiative proceeds normally (both aware); both suffer -30 attack / -30 def
```

**Attacked from behind in a noisy smithy:**

```python
target.aware = False
target.ambient = ["noise"]  # noise explains why awareness check failed
attacker.aware = True

run_duel(attacker, target)
# Same as plain ambush: UNAWARE round 1, then normal
```

### WIT and Awareness Checks

The simulation does not auto-roll awareness checks — that is handled at the
scenario layer. The caller decides whether to set `aware=False` based on:

- Whether the fighter could plausibly have detected the threat (sight,
sound, smell, prior warning).
- Active `ambient` conditions restricting detection channels.
- Traits: a fighter with `"combat_memory"` or `"vigilant"` in their
traits list may be granted `aware=True` even in noise/darkness at the
caller's discretion.

A WIT-based check at difficulty 55 is the recommended gate: roll WIT ×
difficulty; succeed → `aware=True`; fail → `aware=False`.

---

## 4.6 Animal Combat Mechanics

Animal traits are expressed through `sim_traits` and evaluated directly in
`combat_sim.py`.

### Active Animal Trait Rules

| Trait               | Live effect in simulation                                   |
| ------------------- | ----------------------------------------------------------- |
| `pack_tactics`      | +10 attack per ally in fight (max +30).                     |
| `hamstring`         | Critical/mortal hit applies `HAMSTRUNG` (6 rounds).         |
| `starvation_frenzy` | First wound penalty is ignored for that fighter.            |
| `terrifying_charge` | First successful attack gains +2 damage.                    |
| `maul_bite`         | While grapple maintained, automatic bite tick each round.   |
| `den_fighter`       | +20 attack in `cave`, `barrow`, or `den` terrain.           |
| `crushing_weight`   | While grappling, target takes 4 automatic damage per round. |
| `territorial_rage`  | Activates at 50% HP: +10 attack modifier thereafter.        |

### Animal Conditions Added

- `HAMSTRUNG` halves stamina recovery during its duration.
- `MAUL_ACTIVE` tracks sustained bear/wolf mauling windows.

## 4.7 Supernatural Combat Mechanics

Supernatural entities extend standard combat resolution with trait-driven
hooks at pre-battle, attack, defense, and end-of-round steps.

### Implemented Core Behaviors

| Trait/Mechanic           | Effect                                                                |
| ------------------------ | --------------------------------------------------------------------- |
| `incorporeal`            | Physical attacks deal 0 unless fire/iron/supernatural bypass applies. |
| `domain_bonus_3`         | Domain holder gains strong attack/defense bonuses in home terrain.    |
| `water_strength`         | Enhanced offense in `water` terrain.                                  |
| `wrong_geometry`         | First strike may force auto-hit on failed defender WIT reaction.      |
| `killing_cold_contact`   | Successful hit applies `FROSTBITTEN` DOT for d4 rounds.               |
| `cold_aura`              | Adjacent opponents suffer roll penalties in exchanges.                |
| `fire_aversion` weakness | AI avoids aggressive melee vs fire-bearing opponents.                 |
| `temperature_plunge`     | Pre-battle global TOU reduction for combat duration.                  |
| `reality_warping`        | Opponents suffer attack penalties in opening rounds.                  |

### Supernatural Conditions

- `FLEEING`: panic retreat state, blocks normal offense.
- `FROSTBITTEN`: recurring cold damage each round via stored DOT value.

## 4.8 Bloodied Phase System

Bloodied behavior is generic and data-driven.

### Trigger Model

```text
if hp <= max_hp * bloodied_at and not bloodied_triggered:
    bloodied_triggered = True
    apply bloodied_traits
    apply bloodied_mig_bonus / bloodied_nim_bonus
```

- Default threshold: `bloodied_at = 0.5`.
- Death-quarter threshold: 25% HP via `death_quarter_traits`.
- One-shot behavior uses `used_traits` tracking.

### Typical Bloodied Outcomes

- Add trait packages such as `relentless_advance`, `ancient_fury`,
or `desperate_fury`.
- Apply temporary or persistent stat boosts.
- Emit narrative state transition with `[BLOODIED]` lines.

## 4.9 On-Death Dispatch

When a fighter drops, configured `death_effects` are dispatched once per
fighter and logged as `[ON-DEATH]` events.

### Current On-Death Effects

| Effect key              | Resolution summary                                    |
| ----------------------- | ----------------------------------------------------- |
| `death_rattle`          | Narrative trigger only (alert flavor).                |
| `weapon_throw_on_death` | Final attack at -20 accuracy against an enemy target. |
| `corpse_burst_4_2`      | 4 damage AOE to survivors (TOU check halves).         |
| `nauseating_burst`      | TOU failure applies `WINDED` (3 rounds).              |
| `death_command`         | Allied buff window for attack bonus rounds.           |
| `veil_snap_aoe`         | d8 reality backlash AOE (WIL check halves).           |
| `flash_freeze`          | d6 cold burst to survivors.                           |
| `petrification_cascade` | d6 impact to currently grappled survivors.            |

## 4.10 Resistance and Weakness Reference Table

Use these tags under `resistances` and `weaknesses` in bestiary records.

### Resistance tags (combat-active)

| Tag                     | Effect                                   |
| ----------------------- | ---------------------------------------- |
| `bleeding`              | Prevents bleed accumulation from wounds. |
| `cold`                  | Halves cold-type damage.                 |
| `cold_immune`           | Negates cold-type damage.                |
| `piercing`              | Halves thrust damage.                    |
| `physical_weapons`      | Ignores non-bypass physical attacks.     |
| `cutting_weapons`       | Negates `CUT` and `HEAVY_BLOW` damage.   |
| `non-magical_weapons`   | Reduces incoming mundane damage.         |
| `all_physical`          | Suppresses physical damage resolution.   |
| `pain`/`pain_penalties` | Suppresses pain-based combat impairment. |

### Weakness tags (combat-active)

| Tag             | Effect                                                    |
| --------------- | --------------------------------------------------------- |
| `fire`          | Fire damage multiplier applied.                           |
| `silver`        | Silver attacks bypass key undead resilience paths.        |
| `decapitation`  | Critical/mortal head wounds force immediate downing.      |
| `sunlight`      | Daylight tick damage; prolonged exposure destroys target. |
| `loud_noise`    | Pre-battle panic/flee checks for noise-sensitive beasts.  |
| `iron`          | Iron bypass support for spectral defenses.                |
| `spear_set`     | Extra damage after prior-guard spear setup.               |
| `fire_aversion` | AI stance/maneuver restrictions near fire sources.        |

---

## 4.11 Formation Warfare, Morale Contagion, and Rout Dynamics

Prompt 5 adds a battlefield layer above individual duels. In medium and
large skirmishes, fighters carry formation state, cohesion, morale, and
frontage pressure. These values are updated every round and can break a
line even before body count decides the fight.

### Formation State Fields

Each fighter in skirmish mode may carry:

- `formation`: `shield_wall | loose_line | wedge | broken`
- `cohesion_score`: `0-100`
- `morale_score`: `0-100`
- `frontage_pressure`: `0-100`
- `rout_state`: `steady | wavering | rout`
- `is_commander`: explicit commander marker; commander-like traits also
count (`rally_allies`, `veteran_eye`)

If formation is not supplied, the engine defaults spear/shield-heavy
fighters toward `shield_wall` and other fighters toward `loose_line`.

### Formation Attack and Defense Relief

The formation layer is primarily defensive. The simulator currently uses
the following relief values while calculating line pressure:

| Formation   | Defense Relief | Attack Bias |
| ----------- | -------------- | ----------- |
| shield_wall | +8             | -2          |
| loose_line  | 0              | 0           |
| wedge       | -3             | +4          |
| broken      | -10            | -6          |

These do not replace weapon-level combat math. They shape whether a fighter
holds position, starts wavering, or breaks.

### Depth and Pressure Model

The engine approximates local rank depth as:

$$ ext{depth} = \max(1, \lfloor \text{standing fighters} / 3 \rfloor) $$

Depth advantage matters because shallow lines lose push contests faster.

Per fighter, base frontage pressure is built from:

- enemy local outnumbering,
- multiple attackers on the same target,
- commander loss,
- already-routed allies nearby,
- supernatural fear pressure.

Current round pressure is computed as:

$$ \text{pressure} = \text{base pressure} - \text{formation relief} -
\text{depth relief} + \text{shock modifiers} $$

Base pressure formula:

$$ \text{base pressure} = (\text{enemy\_standing} - \text{self\_standing})
\times 8 + \max(0, \text{attackers} - 1) \times 12 $$

Where depth relief is currently `4 × (self_depth - enemy_depth)`.

Shock modifiers applied to base pressure:

- `+12` if commander/rally veteran is down on this side
- `+6` per already-routed ally visible to this fighter
- `+4` if enemy has `terrifying_presence` trait

### Cohesion and Morale Drift Per Round

Round pressure drives both cohesion and morale loss:

- `cohesion_delta = -(pressure // 8)`
- `morale_delta = -(pressure // 10)`

Recovery channels currently implemented:

- `DEFENSIVE` stance: `+1` cohesion recovery
- active commander on the side: `+1` morale recovery
- `shield_wall`: additional `+1` cohesion recovery

All values are clamped to `0-100`.

### Breakpoint Thresholds

The line state changes automatically once cohesion or morale falls past
thresholds:

| Condition                                    | Result                                                      |
| -------------------------------------------- | ----------------------------------------------------------- |
| `cohesion_score < 15` or `morale_score < 15` | `rout_state = rout`, `formation = broken`                   |
| `cohesion_score < 30` or `morale_score < 30` | `rout_state = wavering`; shield wall degrades to loose line |
| otherwise                                    | `rout_state = steady`                                       |

When a fighter newly enters `rout`, the simulator logs a `breakpoint`
event.

### Morale Contagion and Break Cascade

Prompt 5 includes local-to-wide break spread. When one fighter or segment
breaks, nearby allies may suffer `morale_shock`.

Current cascade chances:

- base contagion chance: `18%`
- if the nearby ally is already `wavering`: `+8%`

On contagion (if ally morale > 20):

- ally morale is reduced by `20`
- ally becomes `wavering` if previously `steady`

Note: morale reduction only applies if the ally's morale is already above
20.

This is the main mechanism by which one weak point can turn into a wider
collapse.

### Special Shock Sources

Additional pressure can come from:

- commander down on that side: `+12` pressure
- routed allies already visible: `+6` pressure per routed ally
- heavy local attacker concentration: derived from outnumber and
multi-attack penalty
- `terrifying_presence` on the enemy side: `+4` pressure

These do not create a separate morale subsystem. They are folded into the
same frontage pressure calculation.

### Rout Behavior in Skirmish Mode

Fighters already in `rout` stop behaving like normal duelists.

- They take `rout_action` instead of standard attack resolution.
- If a commander is still active, they have an `organized_withdrawal`
chance of `45%`.
- Otherwise they `panic_flee`.

If no organized withdrawal occurs:

- `cohesion_score -= 4`
- `morale_score -= 3`

Steady allies may screen retreating units with a `rearguard_cover` event at
`30%` chance.

### Pursuit and Overextension

When a non-routing attacker lands a hit on a defender already in `rout`,
the engine may enter a pursuit branch.

Base pursuit chance:

- `62%` if attacker is `AGGRESSIVE`
- `45%` otherwise
- mounted attacker chasing routed foot: additional `+22%`

Overextension risk starts at `18%` and rises with:

- low cohesion (`+22%` if cohesion < 35),
- high frontage pressure (`+18%` if > 60),
- aggressive stance (`+10%`),
- mounted fatigue and repeated pursuit chaining.

Outcomes:

- **Overextended pursuit**: attacker becomes `STAGGERED`, loses cohesion,
and the log records `pursuit_event: overextended`.
- **Clean pursuit**: target takes bonus torso damage; mounted pursuit
against routed foot is stronger and adds horse fatigue.
- **Held line**: attacker does not chase.

This means pursuit is useful but not automatically correct.

---

## 4.12 Missile Combat, Volleys, Suppression, and Ammo Discipline

Prompt 8 adds a pre-melee missile phase to skirmish combat. Missile units
are no longer just melee fighters with ranged flavor; they have ammunition,
fire mode, weather sensitivity, suppression output, and formation-aware
targeting.

### Missile-Capable Fighters

The simulator treats a fighter as missile-capable when any of the following
is true:

- `weapon_type` is in `MISSILE_WEAPONS`
- `ammo_max > 0`
- `ammo_current > 0`

Tracked fields:

- `ammo_max`
- `ammo_current`
- `missile_mode: auto | aimed | volley`
- `suppression_rounds`
- `resupplies_used`

### Missile Phase Placement

In `run_skirmish`, missile attacks resolve before normal stance, maneuver,
and melee action sequencing each round.

This means volleys can wound, suppress, or kill before the melee order is
even rolled.

### Ammunition and Resupply

Ammo is spent per fire mode:

- aimed shot: `1` ammo
- volley fire: `2` ammo

When a missile fighter reaches `ammo_current <= 0`, they may attempt one
conservative in-fight resupply if `resupplies_used < 1`.

Current resupply chance:

- `18%`

Recovered ammo:

- `2` shots for unspecified missile capacity (`ammo_max <= 0`), or
- `min(2, max(1, ammo_max // 4))` for defined capacity (at least 1 shot, up
to 2 total)

If no resupply succeeds, the engine logs `missile_ammo_empty` and the
fighter stops contributing missile fire.

### Fire Modes

#### Aimed Shot

- single-target fire
- `+6` accuracy bonus
- `+2` base damage bonus
- lower suppression chance than volleys

#### Volley Fire

- targets up to `3` enemy fighters
- `-12` accuracy penalty
- best against clusters, exposed lines, and soft morale states
- heavy suppression output

#### Auto Mode

`missile_mode = auto` chooses between aimed and volley fire:

**Low Ammo Definition**: `ammo_current <= max(1, ammo_max // 5)` (one-fifth
of capacity or less)

- if low ammo: switch to `aimed`
- if 4+ live enemies and at least 2 ammo in reserve: switch to `volley`
- otherwise default to `aimed`

### Missile Hit Chance

The live chance model is:

$$ ext{chance} = 42 + 8 \times \text{weapon skill} + 4 \times (\text{WIT} -
5) + \text{weather mod} + \text{mode/target modifiers} $$

Then modified by target qualities:

- `-3 × max(0, defender.nim - 3)`
- `-3 × shield_def`
- volley fire: `-12`
- aimed shot: `+6`
- steady shield wall under volley: additional `-15`
- wavering or routing target: `+8`
- frontage pressure `>= 50`: `+5`

Final chance is clamped to `8-92%`.

### Weather Effects on Missile Fire

Current weather/terrain string modifiers:

| Condition string in terrain | Missile Modifier |
| --------------------------- | ---------------- |
| `blizzard` or `storm`       | -20              |
| `fog` or `rain`             | -12              |
| `wind`                      | -8               |
| otherwise                   | 0                |

This is why ranged lethality collapses in seeded blizzard tests.

### Target Selection Priorities

Volley targeting sorts enemies by:

1. whether they are in `shield_wall`,
2. torso armor value,
3. current frontage pressure.

The system prefers to harass packed or pressured enemies while still
recognizing that shielded fronts are harder to hurt.

### Formation and Shield Interaction

Prompt 8 explicitly interacts with Prompt 5 formation state.

- steady `shield_wall` reduces missile damage to `45%` of normal
frontal lethality
- exposed or pressured targets (`frontage_pressure >= 60` or not steady)
take `×1.25` damage

This creates the intended shield-front vs exposed-line difference.

### Suppression

Suppression is represented with:

- `ConditionType.SUPPRESSED`
- `suppression_rounds`

Current suppression chances:

- volley fire: `75%`
- aimed fire on hit: `30%`
- aimed fire on miss: `15%`

Suppression lasts:

- `2` rounds from volley fire
- `1` round from aimed fire

Suppressed fighters currently suffer:

- `-10` attack
- `-5` defense

Suppression ticks down automatically at end of round.

### Missile Log Events

The missile layer emits structured events including:

- `missile_attack`
- `missile_resupply`
- `missile_ammo_empty`

Each attack event records mode, ammo left, hit/miss, and whether
suppression was applied.

---

## 4.13 Mounted Combat, Anti-Cavalry Counters, and Dismount Flow

Prompt 9 adds mounted combat as a skirmish subsystem rather than a flat
stat bonus. It models charge windows, horse control, anti-cavalry setups,
forced dismounts, and pursuit mobility.

### Scenario Gate: `horses_allowed`

Mounted logic is not globally active.

`run_skirmish(..., horses_allowed=False)` is the default.

When `horses_allowed` is false:

- all fighters are normalized to `mounted = False`
- horse fatigue and charge cooldown are cleared
- dismount vulnerability state is cleared

This is deliberate. Normal barrow and camp fights do not assume horses.
Mounted rules only activate in combats explicitly marked as horse-allowed.

### Mount State Fields

Tracked mounted fields:

- `mounted: bool`
- `mount_condition: steady | panicked | wounded`
- `rider_stability: 0-100`
- `mount_fatigue: 0-100`
- `charge_cooldown`
- `dismount_vulnerability_rounds`
- `mounted_pursuit_chain`

### Charge Window

A mounted fighter may attempt a charge only if all of the following are
true:

- `mounted = True`
- `charge_cooldown == 0`
- fighter is not `GRAPPLED`
- fighter is not `PRONE`
- `mount_condition != panicked` (panicked mounts can attempt dismount
instead)
- horses are allowed in the scenario

**Panicked Mount Logic**: If mount is panicked and rider stability < 35,
there is a 35% chance the mount will throw the rider before charge is
attempted (`mount_panicked` dismount).

Base charge chance is currently:

$$ \text{charge chance} = 0.62 $$

Modified by:

- `+0.12` if stance is `AGGRESSIVE`
- `-0.30` in tight terrain (`forest`, `swamp`, `ruin`, `barrow`, etc.)
- `-0.18` in crowded combat
- `-0.15` if `mount_condition == wounded`

Final effective chance is clamped to `5-92%`.

### Charge Bonuses on Success

Successful charge setup currently grants:

- `attack_mod = +12`
- `target_def_mod = -5`
- `bonus_damage = +3`

The rider also gains:

- `charged_this_fight = True`
- `charge_cooldown = 2`
- `mount_fatigue += 12`

### Tight Terrain and Crowd Penalties

Mounted impact is situational, not universal.

If the charge occurs in tight terrain:

- `attack_mod -= 8`
- `target_def_mod += 3`
- `bonus_damage -= 2`

If combat is crowded:

- `attack_mod -= 5`
- `target_def_mod += 2`
- `bonus_damage -= 1`

This is why cavalry spikes hard in open ground but loses value in forests,
ruins, barrows, and packed melee.

### Anti-Cavalry Counters

Anti-cavalry defense is available through:

- braced anti-cavalry weapons (`spear`, `pike`, `halberd`, `poleaxe`,
`staff_spear`), combined with `DEFENSIVE` stance or `GUARD`
- stake or obstacle terrain markers

Brace success chance is currently:

$$ ext{brace chance} = 42 + 5 \times \text{weapon skill} +
\text{stance/stake bonuses} $$

With bonuses:

- `+10` for proper brace setup
- `+15` if stakes or obstacles are present

On successful brace:

- mounted attacker `attack_mod -= 14`
- target defensive burden improves (`target_def_mod += 6`)
- charge `bonus_damage` is reduced by `3`
- rider stability drops by `18-30`
- stakes also wound the mount

If rider stability falls low enough, a forced dismount may occur.

### Horse Fear Checks

Horses can panic under battlefield shock even before a successful hit.

Fear pressure increases from:

- enemy `terrifying_presence`: `+18` fear pressure
- fire-bearing weapons or fire traits: `+22` fear pressure
- very high frontage pressure on the defender (`>= 60`): `+8` fear pressure

If the fear roll succeeds against the mount:

- `mount_condition = panicked`
- `rider attack_mod -= 8`
- `target_def_mod += 4`
- rider stability drops by `12`

If rider stability drops to `≤ 22`, forced dismount occurs
(`mount_panic_throw`).

### Forced Dismount

When dismounted by brace, panic, or failed stability, the simulator:

- sets `mounted = False`
- sets `mount_condition = wounded`
- reduces `rider_stability`
- sets `dismount_vulnerability_rounds = 2`
- applies `STAGGERED` for 1 round

The action log records `dismount_event`.

### Post-Dismount Vulnerability

While `dismount_vulnerability_rounds > 0`, incoming attackers gain an
additional `+8` attack modifier against that fighter.

This models the scramble to recover footing and weapon control after being
thrown or forced down off the horse.

### Horse Fatigue and Recovery

At end of round:

- `charge_cooldown` ticks down by `1`
- `dismount_vulnerability_rounds` ticks down by `1`
- `mount_fatigue` recovers slowly (`-3` per round)

If `mount_fatigue >= 70` and the horse was still steady, the engine marks
the mount as `wounded`.

Panicked mounts may settle back to `steady` or `wounded` depending on
fatigue and recovery chance.

### Mounted Pursuit

Mounted fighters gain a meaningful edge when pursuing routed foot units.

In the pursuit branch:

- mounted attacker vs routed foot gains additional pursuit chance
- successful clean pursuit deals extra damage
- each mounted pursuit adds horse fatigue
- repeated pursuit chains increase overextension risk

This keeps cavalry strong in open-field collapse phases without making it
free or endless.

### Horse Sheet

The existing mounted fields are enough for simple skirmish gating, but a
full campaign horse should carry a separate horse sheet. Use this when a
mount matters across scenes, weeks, breeding, resale, or injury recovery.

Minimum horse sheet:

- `name`
- `breed`
- `sex: mare | stallion | gelding`
- `age_class: foal | yearling | young | prime | aging | old`
- `role: riding | scout | pack | war | courier | breeding`
- `mood: calm | eager | sour | stubborn | watchful | frightened`
- `condition`
- `bond_rider`
- `speed`
- `wind`
- `foot`
- `nerve`
- `load`
- `sense`
- `traits`
- `tricks`
- `bloodline_tags`

Recommended 1-5 horse stat scale:

| Stat    | Meaning                                            |
| ------- | -------------------------------------------------- |
| `speed` | Top-end movement and burst                         |
| `wind`  | Recovery, stamina, repeated effort                 |
| `foot`  | Balance, traction, rough-ground confidence         |
| `nerve` | Fear resistance under noise, blood, fire, pressure |
| `load`  | Carrying capacity and draft tolerance              |
| `sense` | Early warning, path judgment, rider responsiveness |

### Breed Templates

Breeds are not cosmetic. Each breed defines the likely baseline, common
traits, and common failure mode.

| Breed               | Speed | Wind | Foot | Nerve | Load | Sense | Typical Traits               | Common Weakness                  |
| ------------------- | ----- | ---- | ---- | ----- | ---- | ----- | ---------------------------- | -------------------------------- |
| Rimefjord pony      | 2     | 4    | 4    | 4     | 3    | 4     | cold_hardy, calm_mouth       | lacks burst                      |
| Moor-runner         | 5     | 4    | 3    | 2     | 2    | 3     | fast_break, long_stride      | stressy, feed-sensitive          |
| Pine-cob            | 2     | 3    | 3    | 5     | 5    | 3     | dead_pull, patient           | poor acceleration                |
| Spine pony          | 2     | 4    | 5    | 4     | 3    | 4     | cliff-footed, sparse-forager | dislikes crowd crush             |
| Southblood warhorse | 4     | 3    | 3    | 3     | 4    | 2     | charge_mass, tall_frame      | cold-soft, costly, hotter temper |

Breed modifies acquisition, breeding value, and task success. A breed is
the base package; individuals still vary by traits, training, and care.

### Horse Moods

Mood is the short-horizon mental state of the horse. It changes faster than
condition and should be checked whenever the horse is hungry, tired,
afraid, mishandled, or working with a bad rider.

| Mood         | Effects                                                         |
| ------------ | --------------------------------------------------------------- |
| `calm`       | No modifier                                                     |
| `eager`      | `+10` to charge, pursuit, and courier checks; `-5` to restraint |
| `sour`       | `-10` to rider-directed work; resists tricks                    |
| `stubborn`   | `-5` general, but `+10` against panic or forced hazards         |
| `watchful`   | `+10` to ambush notice and danger-sense checks                  |
| `frightened` | `-15` to control; immediate fear check in battle scenes         |

Mood shifts:

- hard ride without cooldown: one step worse
- good feed, rubdown, quiet rest: one step better
- rider the horse trusts takes over: one step better
- fire, screaming undead, or barrow phenomena: one step worse immediately

### Horse Conditions

Condition is the physical state now affecting work.

| Condition     | Mechanical Effect                                   |
| ------------- | --------------------------------------------------- |
| `fresh`       | `+5` to all horsing checks                          |
| `worked`      | no modifier                                         |
| `winded`      | `-10` to speed and charge checks                    |
| `blown`       | no charge; `-20` to pursuit; recover with rest only |
| `hoof_sore`   | `-15` on stone, ice, and hardpack                   |
| `lame`        | cannot charge; travel speed halved                  |
| `chilled`     | `-10` until dried and warmed                        |
| `hungry`      | mood worsens one step per day; `-5` all work        |
| `dehydrated`  | `-15` wind; recovery slowed                         |
| `skin_rubbed` | `-10` ridden work until tack is adjusted            |
| `panicked`    | existing mounted-combat panic rules apply           |
| `wounded`     | existing mounted-combat wounded rules apply         |

Campaign horses should normally track both the current condition and the
existing combat fields `mount_condition`, `rider_stability`, and
`mount_fatigue`. The combat layer is a short-term slice of the wider horse
sheet.

### Horsing Checks

Use the normal skill-check formula from §1, but horses use a defined
horse-and-rider resolution block:

```text
horsing_check =
    (rider_attribute × 5)
  + (rider_skill × 10)
  + (horse_relevant_stat × 8)
  + mood_mod
  + condition_mod
  + bond_mod
  + breed_mod
  + terrain_mod
```

Recommended rider attribute and skill pairings:

| Task                            | Attribute | Skill                    |
| ------------------------------- | --------- | ------------------------ |
| Keep seat under shock           | NIM       | command or ride/horsing  |
| Settle panic or bad temper      | WIL       | command or ride/horsing  |
| Read ground, ford, or safe path | WIT       | navigate or ride/horsing |
| Push pace over distance         | WIL       | ride/horsing             |
| Pack loading and balance        | WIT       | survival or ride/horsing |
| Mounted trick execution         | NIM       | ride/horsing             |

Default rider modifiers:

- `bond_rider = primary rider`: `+10`
- rider known but not bonded: `+0`
- unfamiliar rider: `-10`
- hostile or feared rider: `-20`

If the system is not using a distinct `ride/horsing` skill, substitute the
best relevant existing skill shown above and apply `-10` if the character
has never worked horses seriously.

### Horse Tricks

Tricks are trained, repeatable mount behaviors. A horse may know `1` basic
trick per point of `sense`, plus one additional trick if it is prime-aged
and has a dedicated rider.

| Trick             | Use                                         | Check Modifier                                       |
| ----------------- | ------------------------------------------- | ---------------------------------------------------- |
| `kneel_mount`     | Easier mounting, wounded rider support      | `+10` to mount under pressure                        |
| `stand_fire`      | Hold position under missile or torch threat | `+10` vs fear from ranged noise/fire                 |
| `come_to_whistle` | Recover loose horse                         | `+15` recall if within earshot                       |
| `drag_wounded`    | Haul injured person by loop or cloak        | `+10` casualty extraction, speed capped              |
| `pack_crouch`     | Lower body for loading                      | `+10` load/balance checks                            |
| `sidepass`        | Gate, hedge, and tight obstacle handling    | `+10` in narrow terrain                              |
| `trample_drive`   | Push through broken foot or fleeing rabble  | `+10` pursuit shock, high fatigue                    |
| `barrow_refusal`  | Refuses uncanny ground unless forced        | `+15` detect supernatural unease, but blocks advance |

Failed trick checks do not mean the horse forgets the trick. They mean the
current rider, mood, terrain, or pressure broke execution.

### Breeding and Inheritance

Breeding should create tendencies, not certainty. Use the breed template as
the base, then inherit bloodline tags and one or two standout stats.

Foal generation:

1. Choose base breed.
Dam breed if same-breed pairing or local mixed stock. `50/50` between dam
and sire for deliberate cross-breeding.
2. Inherit one strong stat from each parent.
On each inherited stat, foal gets parent value or parent value `-1`.
3. Inherit two `bloodline_tags`.
One from dam, one from sire.
4. Roll one foal quirk.
`steady_mouth`, `late_maturing`, `bad_feeder`, `crowd_shy`, `ice-wise`,
`hard_keeper`, `throws_big`, `throws_small`.
5. Adjust for care.
Poor winter during foal year: `-1 wind` or `-1 load`. Excellent care and
sound handling: `+1 sense` or remove one bad quirk.

Useful bloodline tags:

- `good_feet`
- `deep_wind`
- `cold_hardy`
- `hot_blooded`
- `sure_step`
- `strong_back`
- `soft_mouth`
- `crowd_sour`
- `night_spook`
- `foal_strong`

Breeding outcomes should matter economically:

- broodmare with `good_feet` + `cold_hardy` lines: `+20-40%` value
- proven scout line with `deep_wind`: `+30-60%` value
- repeated `night_spook` or `crowd_sour`: heavy discount unless sold to
isolated civilian work

### Horse Value Bands

Use this when pricing a specific horse beyond the coarse economy tables.

```text
horse_value =
    breed_base_value
  + (sum(stats) - 18) × 2 silver
  + trained_tricks × 1 silver
  + bloodline_bonus
  - condition_penalty
  - vice_penalty
```

Reference adjustments:

- bonded proven scout mount: `+6 to +12 silver`
- war-trained charger with `charge_mass`: `+10 to +25 silver`
- chronic hoof soreness: `-4 to -10 silver`
- panic history under fire or undead pressure: `-6 to -15 silver`
- broodmare with two desirable bloodline tags: `+5 to +15 silver`

### Mounted Log Events

Prompt 9 emits explicit structured events:

- `mount_charge`
- `anti_cavalry_brace`
- `mount_fear`
- `dismount_event`
- `mount_charge_impact`

These are the main log hooks for narrative rendering and debugging of the
mounted subsystem.

---

## 4.14 Dogs, Working Checks, and Breeding

Dogs use the same campaign-asset logic as horses, but on a smaller and
faster scale. They mature sooner, eat less, bond harder, and fail more
often through handling mistakes than through pure expense. Use a full dog
sheet whenever a working dog matters across scenes, watches, hunts,
tracking, war-dog use, breeding, resale, or repeated camp play.

### Dog Sheet

Minimum dog sheet:

- `name`
- `breed`
- `sex: bitch | dog`
- `age_class: pup | juvenile | young | prime | aging | old`
- `role: guard | tracker | hunter | war | herd | companion | breeding`
- `mood`
- `condition`
- `bond_handler`
- `nose`
- `speed`
- `grit`
- `bite`
- `sense`
- `voice`
- `traits`
- `tricks`
- `bloodline_tags`

Recommended 1-5 dog stat scale:

| Stat    | Meaning                                                      |
| ------- | ------------------------------------------------------------ |
| `nose`  | Scent retention, trail quality, corpse/game finding          |
| `speed` | Burst, pursuit, and general quickness                        |
| `grit`  | Pain tolerance, persistence, cold toughness, refusal to quit |
| `bite`  | Clamp strength, attack confidence, hold quality              |
| `sense` | Handler response, judgment, strange-thing awareness          |
| `voice` | Alarm quality, bark carry, controlled signaling              |

### Breed Templates

| Breed               | Nose | Speed | Grit | Bite | Sense | Voice | Typical Traits                          | Common Weakness         |
| ------------------- | ---- | ----- | ---- | ---- | ----- | ----- | --------------------------------------- | ----------------------- |
| Fjord hound         | 4    | 3     | 3    | 2    | 4     | 4     | weather_sense, bark_alarm, shorewise    | soft_in_line            |
| Black Pine wolf-dog | 5    | 4     | 5    | 5    | 3     | 2     | winter_hunter, hard_bite, silent_worker | stranger_sour, pack_hot |
| Bog tracker         | 5    | 3     | 3    | 2    | 5     | 3     | marsh_footed, deep_nose, careful_step   | kennel_sour             |
| Hall mastiff        | 3    | 2     | 5    | 4    | 3     | 5     | gate_guard, hold_fast, loud_warning     | poor_endurance          |
| Moor lurcher        | 3    | 5     | 2    | 2    | 4     | 2     | long_legs, hare_killer, quick_return    | thin_coat               |

Breed matters to acquisition, training ceilings, working role, and breeding
value. Dogs are less pure-bred in practice than horses, but the lines still
produce recognizable packages of strengths and failures.

### Dog Moods

| Mood       | Effects                                                |
| ---------- | ------------------------------------------------------ |
| `calm`     | No modifier                                            |
| `eager`    | `+10` to hunt, pursuit, and fetch/recall checks        |
| `watchful` | `+10` to alarm and uncanny-notice checks               |
| `sour`     | `-10` to handler-directed work                         |
| `pack_hot` | `+10` to attack and pursuit, `-10` to discipline       |
| `shaken`   | `-15` to bite, hold, and night movement                |
| `fixated`  | `+10` on one target or scent, `-10` to everything else |

Mood shifts:

- missed meal, cold kennel, or rough handling: one step worse
- good feed, known handler, warm rest: one step better
- blood in the air, pack chorus, or active pursuit: toward `eager` or
  `pack_hot`
- barrow phenomena, corpse-stink, impossible silence: toward `watchful` or
  `shaken`

### Dog Conditions

| Condition      | Mechanical Effect                                                   |
| -------------- | ------------------------------------------------------------------- |
| `fresh`        | `+5` to all dog-work checks                                         |
| `worked`       | no modifier                                                         |
| `winded`       | `-10` to pursuit and attack checks                                  |
| `pawed_raw`    | `-15` on rock, ice, bog crust, or long travel                       |
| `hungry`       | mood worsens one step per day; `-5` all work                        |
| `chilled`      | `-10` until dried and warmed                                        |
| `mange`        | `-10` social value and `-5` grit                                    |
| `kennel_cough` | no sustained pursuit; `-15` winded recovery                         |
| `panicked`     | no hold or attack without a successful settle check                 |
| `wounded`      | `-15` all work; bite checks at disadvantage in narrative resolution |

### Dog Checks

Use the normal skill-check formula from §1 through this dog-and-handler
resolution block:

```text
dog_check =
    (handler_attribute × 5)
  + (handler_skill × 10)
  + (dog_relevant_stat × 8)
  + mood_mod
  + condition_mod
  + bond_mod
  + breed_mod
  + terrain_mod
```

Recommended handler pairings:

| Task                       | Attribute | Skill                       |
| -------------------------- | --------- | --------------------------- |
| Hold trail                 | WIT       | track or dog-handling       |
| Settle fear or aggression  | WIL       | command or dog-handling     |
| Send to seize or hold      | NIM       | command or dog-handling     |
| Night watch interpretation | WIT       | animal lore or dog-handling |
| Hunt or flush game         | WIT       | survival or dog-handling    |
| Recall under distraction   | WIL       | command or dog-handling     |

Default handler modifiers:

- `bond_handler = primary handler`: `+10`
- known handler: `+0`
- unfamiliar handler: `-10`
- feared or disliked handler: `-20`

If the system is not using a distinct `dog-handling` skill, substitute the
best relevant existing skill and apply `-10` if the character has little
real dog experience.

### Dog Tricks

A dog may know `1` basic trick per point of `sense`, plus one additional
trick if it is prime-aged and has a stable bond handler.

| Trick          | Use                                             | Check Modifier                         |
| -------------- | ----------------------------------------------- | -------------------------------------- |
| `bark_alarm`   | Loud, directional warning                       | `+10` to alarm checks                  |
| `silent_watch` | Notice without barking until signaled           | `+10` to stealthy guard work           |
| `blood_track`  | Hold wounded target scent                       | `+10` on blood spoor                   |
| `find_home`    | Return to camp or hall from distance            | `+15` recall/navigation                |
| `hold_thief`   | Seize and pin without killing                   | `+10` bite-and-hold                    |
| `boar_turn`    | Harass dangerous game from flanks               | `+10` hunt teamwork                    |
| `corpse_find`  | Find dead or buried bodies by scent             | `+10` corpse/hidden-corpse detection   |
| `heel_fire`    | Stay close during chaos, fire, or missile noise | `+10` control under battlefield stress |
| `line_guard`   | Patrol a defined perimeter repeatedly           | `+10` repetitive watch work            |

Failed trick checks mean the current fear, distraction, handler, or ground
broke execution. They do not mean the dog forgot the trick.

### Dog Breeding and Inheritance

Breeding dogs should create working tendencies, not guaranteed outcomes.
The line matters, but so do handling, culling, and early use.

Pup generation:

1. Choose base breed.
Dam breed if same-line pairing or common mixed stock. `50/50` between dam
and sire for deliberate crossing.
2. Inherit one strong stat from each parent.
On each inherited stat, pup gets parent value or parent value `-1`.
3. Inherit two `bloodline_tags`.
One from dam, one from sire.
4. Roll one puppy quirk.
`sure_returner`, `late_head`, `cold_nose`, `kennel_sour`, `loud_mouth`,
`soft_mouth`, `hard_keeper`, `fight_picker`.
5. Adjust for raising.
Good handler and steady kennel: `+1 sense` or remove one bad quirk. Hard
winter or bad feeding: `-1 grit` or `-1 speed`.

Useful bloodline tags:

- `deep_nose`
- `winter_hunter`
- `hard_bite`
- `calm_house`
- `gate_guard`
- `homewise`
- `quick_return`
- `loud_warning`
- `stranger_sour`
- `pack_hot`

Breeding value guidance:

- proven tracker line with `deep_nose`: `+2 to +5 silver`
- war line with `hard_bite` + `winter_hunter`: `+4 to +8 silver`
- repeated `pack_hot` or `stranger_sour`: discount unless sold for kennel
  war work
- bitch with three litters of working pups: major local prestige even if
  plain

### Dog Value Bands

```text
dog_value =
    breed_base_value
  + (sum(stats) - 18) × 1 silver
  + trained_tricks × 1 silver
  + bloodline_bonus
  - condition_penalty
  - vice_penalty
```

Reference adjustments:

- proven hall guard that already stopped a thief: `+2 to +4 silver`
- tracker that can hold trail through rain or bog: `+3 to +6 silver`
- kennel cough, mange, or chronic paw damage: `-1 to -4 silver`
- panic around undead, caves, or battle noise: `-2 to -5 silver`

---

## 5. Health and Wounds

> **Lore cross-reference:** `wound-and-healing-system.md` contains > the
  setting-specific medical lore (humoral framework, leech tools, > wound
  classification descriptions, healing stage narratives, > medieval
  terminology glossary). This section contains all > simulation mechanics.

### 5.1 Hit Points

```text
max_hp = (Toughness × 3) + Might + 10
```

Typical range: 14 (feeble) to 50 (legendary warrior).

### 5.2 Wound Severity (Per Hit)

| Damage Dealt | Wound Level    | Effect                                             |
| ------------ | -------------- | -------------------------------------------------- |
| 1-3          | Scratch        | No mechanical effect. Stings.                      |
| 4-6          | Light wound    | -5 to rolls using affected location                |
| 7-10         | Serious wound  | -15 to rolls, bleeding (1 HP/round)                |
| 11-15        | Critical wound | -30 to rolls, heavy bleeding (2 HP/round)          |
| 16+          | Mortal wound   | Incapacitated. Death in minutes without Heal check |

### 5.3 Bleeding

Serious+ wounds bleed until treated. Heal check difficulty:

| Wound Level | Heal Difficulty Modifier |
| ----------- | ------------------------ |
| Serious     | +0                       |
| Critical    | -15                      |
| Mortal      | -30                      |

### 5.4 Wound Record Schema

Every wound inflicted by `combat_sim.py` produces a discrete `Wound`
record. Wounds accumulate — they do not merge. A man with three separate
light wounds on his right arm has three wounds, not one medium wound. Each
requires separate treatment and heals on its own timeline.

```yaml
wound:
  id: "w_001" # Unique wound identifier
  location:
    "right_arm" # head, torso, right_arm, left_arm,
    # legs, hands, feet
  sublocation: "forearm_outer" # Specific anatomical sublocation
  type:
    "hewn" # hewn, stab, crush, arrow, burn,
    # frostbite
  severity:
    "serious" # scratch, light, serious, critical,
    # mortal
  damage: 8 # Raw damage number from combat
  bleeding: 1 # HP/round bleeding rate (0 if stopped)
  description: "Deep axe-cut across the outer forearm, muscle partially
    severed, bone visible at the deepest point."
  inflicted_day: 87 # Simulation day when wound occurred
  inflicted_by: "Bandit Raider" # Source of the wound
  weapon_used: "hand_axe" # Source weapon

  # Treatment State
  treated: false
  treatment_type:
    null # first_aid, field_surgery, full_surgery,
    # cauterized, amputated
  treated_by: null
  treated_day: null
  stitched: false
  stitch_count: 0
  poulticed: false
  poultice_type: null # yarrow, plantain, comfrey, honey, moss
  splinted: false
  bandaged: false

  # Healing State
  healing_stage:
    "fresh" # fresh, clotting, closing, knitting,
    # scarring, healed
  healing_day_count: 0
  healing_target_days: 20
  clean: true
  infected: false
  infection_stage: null # early, spreading, deep, mortifying
  infection_day_count: 0
  fever: false

  # Complication Flags
  foreign_body: false
  foreign_body_type:
    null # arrowhead, blade_fragment, cloth,
    # bone_splinter, dirt
  bone_broken: false
  bone_set: false
  tendon_severed: false
  joint_damaged: false
  nerve_damaged: false

  # Outcome
  scar: null # null until healed, then scar record
  permanent_effect: null
  resolved: false # true when fully healed/scarred
```

### 5.5 Sublocation System

Each main location has specific sublocations that determine structures at
risk and activities impaired.

#### Head Sublocations

| Sublocation   | Structures at Risk       | Activities Affected               |
| ------------- | ------------------------ | --------------------------------- |
| Scalp         | Skin, blood vessels      | None (bleeds heavily, heals well) |
| Temple        | Skull, brain             | Consciousness, balance, vision    |
| Forehead      | Skull, brow ridge        | Vision (blood in eyes)            |
| Jaw           | Jawbone, teeth, tongue   | Eating, speaking, biting          |
| Ear           | Cartilage, eardrum       | Hearing, balance                  |
| Eye socket    | Eye, orbital bone        | Vision, depth perception          |
| Nose          | Nasal cartilage, sinuses | Breathing, scent                  |
| Cheek         | Facial muscle, cheekbone | Chewing, expression               |
| Throat / neck | Windpipe, vessels, spine | Breathing, voice, life            |

#### Torso Sublocations

| Sublocation   | Structures at Risk              | Activities Affected           |
| ------------- | ------------------------------- | ----------------------------- |
| Chest (front) | Ribs, lungs, heart              | Breathing, exertion, stamina  |
| Chest (side)  | Ribs, intercostal muscle        | Twisting, reaching, breathing |
| Belly (upper) | Stomach, liver, spleen          | Digestion, blood volume       |
| Belly (lower) | Intestines, bladder             | Digestion, infection risk     |
| Flank         | Kidney, lower ribs              | Twisting, bending, stamina    |
| Back (upper)  | Shoulder blade, spine, lungs    | Arm movement, breathing       |
| Back (lower)  | Spine, muscles                  | Bending, lifting, walking     |
| Collarbone    | Clavicle, shoulder joint        | Arm raising, carrying         |
| Shoulder      | Joint, rotator muscles, tendons | All arm use, shield, weapon   |

#### Arm Sublocations

| Sublocation     | Structures at Risk            | Activities Affected          |
| --------------- | ----------------------------- | ---------------------------- |
| Upper arm outer | Deltoid, humerus              | Lifting, swinging, carrying  |
| Upper arm inner | Brachial artery, bicep        | Grip, pulling, bleeding risk |
| Elbow           | Joint, tendons, bone point    | Flexion, extension, weapon   |
| Forearm outer   | Forearm bones, extensors      | Wrist control, grip strength |
| Forearm inner   | Flexor tendons, radial artery | Grip, bleeding danger        |
| Wrist           | Joint, carpal bones, tendons  | All hand function            |

#### Hand Sublocations

| Sublocation  | Structures at Risk            | Activities Affected            |
| ------------ | ----------------------------- | ------------------------------ |
| Fingers      | Tendons, joints, bone         | Grip, fine work, weapon hold   |
| Thumb        | Thenar muscle, joint          | Opposition grip, weapon ctrl   |
| Palm         | Tendons, flexor muscles       | Grip strength, tool use        |
| Back of hand | Extensor tendons, metacarpals | Finger extension, knuckle      |
| Knuckles     | Joints, skin over bone        | Punching, gripping, fine motor |

#### Leg Sublocations

| Sublocation   | Structures at Risk             | Activities Affected         |
| ------------- | ------------------------------ | --------------------------- |
| Thigh (front) | Quadriceps, femur              | Standing, climbing, kicking |
| Thigh (inner) | Femoral artery, adductors      | Walking, bleeding danger    |
| Thigh (outer) | IT band, hip joint muscles     | Lateral movement, stability |
| Knee          | Joint, ligaments, kneecap      | Kneeling, running, pivoting |
| Shin          | Tibia, periosteum              | Walking, running, pain      |
| Calf          | Gastrocnemius, Achilles tendon | Walking, running, jumping   |
| Ankle         | Joint, ligaments, tendons      | All foot movement, balance  |

#### Foot Sublocations

| Sublocation | Structures at Risk          | Activities Affected        |
| ----------- | --------------------------- | -------------------------- |
| Toes        | Joints, bones               | Balance, push-off, running |
| Arch        | Plantar fascia, small bones | Weight bearing, marching   |
| Heel        | Calcaneus, fat pad          | Walking on hard ground     |
| Top of foot | Metatarsals, extensors      | Foot flexion, boot wearing |

#### Sublocation Determination (d100)

```python
SUBLOCATION_TABLE = {
    "head": [
        (1, 15, "scalp"), (16, 25, "temple"), (26, 40, "forehead"),
        (41, 55, "jaw"), (56, 65, "ear"), (66, 75, "eye_socket"),
        (76, 82, "nose"), (83, 90, "cheek"), (91, 100, "throat"),
    ],
    "torso": [
        (1, 20, "chest_front"), (21, 30, "chest_side"),
        (31, 45, "belly_upper"), (46, 55, "belly_lower"),
        (56, 65, "flank"), (66, 75, "back_upper"),
        (76, 85, "back_lower"), (86, 92, "collarbone"),
        (93, 100, "shoulder"),
    ],
    "right_arm": [
        (1, 25, "upper_arm_outer"), (26, 35, "upper_arm_inner"),
        (36, 50, "elbow"), (51, 70, "forearm_outer"),
        (71, 85, "forearm_inner"), (86, 100, "wrist"),
    ],
    "left_arm": [
        (1, 25, "upper_arm_outer"), (26, 35, "upper_arm_inner"),
        (36, 50, "elbow"), (51, 70, "forearm_outer"),
        (71, 85, "forearm_inner"), (86, 100, "wrist"),
    ],
    "hands": [
        (1, 30, "fingers"), (31, 50, "thumb"), (51, 70, "palm"),
        (71, 90, "back_of_hand"), (91, 100, "knuckles"),
    ],
    "legs": [
        (1, 25, "thigh_front"), (26, 35, "thigh_inner"),
        (36, 45, "thigh_outer"), (46, 65, "knee"),
        (66, 80, "shin"), (81, 90, "calf"), (91, 100, "ankle"),
    ],
    "feet": [
        (1, 35, "toes"), (36, 60, "arch"),
        (61, 80, "heel"), (81, 100, "top_of_foot"),
    ],
}
```

#### Weapon to Wound Type Mapping

```python
WEAPON_WOUND_TYPE = {
    "hand_axe": "hewn", "bearded_axe": "hewn", "long_axe": "hewn",
    "sword": "hewn", "sword_thrust": "stab", "seax": "hewn",
    "seax_thrust": "stab", "spear": "stab", "javelin": "stab",
    "short_bow": "arrow", "fist": "crush", "kick": "crush",
    "shield_bash": "crush", "mordschlag": "crush",
    "grapple": "crush", "fire": "burn", "cold": "frostbite",
    "fall": "crush",
}
```

### 5.6 Wound Accumulation Rules

1. **Each hit = one wound record.** No merging.

2. **Location stacking penalty.** Multiple wounds on the same location:
   - Two wounds on same sublocation: healing time × 1.3 for newer wound.
   - Three+ wounds on same location: healing time × 1.5 for each wound
beyond the second. Infection risk per day doubles.

3. **Total wound load.** Total active wounds affect systemic health:

| Active Wounds | Systemic Effect                          |
| ------------- | ---------------------------------------- |
| 1–2           | No systemic effect                       |
| 3–4           | -5 all rolls (body dividing resources)   |
| 5–6           | -10 all rolls, appetite loss, poor sleep |
| 7+            | -20 all rolls, wound-fever risk per day  |

4. **Blood loss accumulation.** Each wound's bleeding rate stacks. If
total bleeding exceeds 3 HP/round during combat, collapse in minutes.
Post-combat, untreated bleeding converts to HP loss per hour.

5. **The worst wound governs.** Worst untreated wound determines overall
condition category:

| Worst Active Wound | Condition Category |
| ------------------ | ------------------ |
| Scratch only       | Functional         |
| Light              | Wounded (limited)  |
| Serious            | Badly wounded      |
| Critical           | Incapacitated      |
| Mortal             | Dying              |

### 5.7 Healing Stages (Mechanical)

Each wound passes through defined stages. The stage determines mechanical
penalties, complication risks, and activity restrictions.

| Stage | Name     | Duration (Light) | Duration (Serious) | Duration (Critical) |
| ----- | -------- | ---------------- | ------------------ | ------------------- |
| 1     | Fresh    | 0–4 hours        | 0–4 hours          | 0–4 hours           |
| 2     | Clotting | 4–48 hours       | 4–48 hours         | 4–48 hours          |
| 3     | Closing  | Day 2–7          | Day 2–14           | Day 14–30           |
| 4     | Knitting | Day 7–21         | Day 14–45          | Day 30–90           |
| 5     | Scarring | Day 21+          | Day 45+            | Day 90+             |
| 6     | Healed   | Resolved         | Resolved           | Resolved            |

**Stage-specific mechanics:**

- **Fresh:** Bleeding at wound rate. `treated: false` until leech
attends. All wound penalties at full.
- **Clotting:** `bleeding: 0` if properly treated. Daily infection
check active. Full wound penalties.
- **Closing:** Wound penalties reduce by one step if properly treated.
Infection check drops to 2% per day.
- **Knitting:** Wound penalties halved from worst. Physical exertion
check required — any combat or heavy labor forces a TOU check or wound
re-opens (reverts to Stage 1 with healing time × 1.5).
- **Scarring:** Wound penalties removed except permanent effects. Scar
record generated.
- **Healed:** Wound record marked `resolved: true`. Permanent effects
remain on statblock.

### 5.8 Healing Timeline Summary

#### By Wound Severity (Full Rest)

| Severity | Fresh→Clotting | Clotting→Closing | Closing→Knitting | Knitting→Scarring | Total to Healed |
| -------- | -------------- | ---------------- | ---------------- | ----------------- | --------------- |
| Scratch  | Hours          | 1 day            | 1–2 days         | —                 | 2–3 days        |
| Light    | Hours          | 1–2 days         | 3–5 days         | 7–14 days         | 14–21 days      |
| Serious  | Hours          | 2–3 days         | 7–14 days        | 21–45 days        | 30–60 days      |
| Critical | Hours          | 3–5 days         | 14–30 days       | 45–90 days        | 60–120 days     |
| Mortal   | Hours          | 5–7 days         | 30–60 days       | 90–180 days       | 120–240 days    |

#### By Bone Injury (Full Rest)

| Bone Injury          | Splint Duration  | Weight Bearing | Full Strength | Permanent?          |
| -------------------- | ---------------- | -------------- | ------------- | ------------------- |
| Cracked rib          | 2 weeks binding  | 3–4 weeks      | 6–8 weeks     | Weather-sensitive   |
| Broken forearm       | 4–6 weeks splint | 6 weeks        | 10–12 weeks   | Possible grip loss  |
| Broken upper arm     | 6–8 weeks splint | 8 weeks        | 12–16 weeks   | Possible weakness   |
| Broken shin (tibia)  | 8–10 weeks       | 10 weeks       | 16–20 weeks   | Possible limp       |
| Broken thigh (femur) | 12–16 weeks      | 16 weeks       | 24–32 weeks   | Likely limp         |
| Broken collarbone    | 4–6 weeks sling  | 6 weeks        | 8–12 weeks    | Often heals well    |
| Broken jaw           | 4–6 weeks bound  | 6 weeks        | 8–10 weeks    | Bite alignment      |
| Dislocated shoulder  | 2–4 weeks sling  | 3 weeks        | 6 weeks       | Re-dislocation risk |
| Dislocated finger    | 1 week binding   | 2 days         | 2 weeks       | Stiffness           |
| Crushed kneecap      | 6–8 weeks splint | 10 weeks       | Never full    | Permanent limit     |

#### Rest Quality Multiplier

| Rest Quality | Healing Speed | Description                               |
| ------------ | ------------- | ----------------------------------------- |
| full_rest    | ×1.0          | Settlement, bed, regular meals, no duty   |
| field_rest   | ×0.5          | Camp, sleeping rough, limited movement    |
| active_duty  | ×0.2          | Marching, working, fighting while wounded |

All healing timelines above assume full rest. In the field, multiply by ×2.
On active duty, multiply by ×5 — wounds essentially do not heal while
marching and may worsen.

### 5.9 Infection System

#### Infection Check (Daily)

```text
daily_infection_chance = base_chance
  + foreign_body_bonus
  + environment_bonus
  - treatment_bonus
  - toughness_bonus

base_chance:
  scratch: 5%, light: 10%, serious: 20%,
  critical: 30%, mortal: 50%

foreign_body_bonus:
  cloth fragments: +10%, dirt/rust: +15%,
  arrowhead: +20%, bone splinter: +10%

environment_bonus:
  clean camp: +0%, field (dry): +5%,
  field (wet/mud): +15%, swamp/stagnant: +25%,
  Long Dark: +5%

treatment_bonus:
  cleaned properly: -15%, honey dressing: -10%,
  fresh poultice: -5%, cauterized: -20%

toughness_bonus:
  per TOU point: -2%
```

This check runs daily from day after injury until wound enters Stage 3
(closing) or becomes infected. After Stage 3, check drops to 2% per day.

#### Infection Stages

| Stage | Name          | Onset              | Mechanical Effect                          |
| ----- | ------------- | ------------------ | ------------------------------------------ |
| 1     | Early Rot     | 1–3 days           | -10 all rolls at location. Heal check +0   |
| 2     | Spreading     | 3–5 days untreated | -15 all rolls. 1 HP/day. Fever. Heal -15   |
| 3     | Deep Rot      | 5–10 days          | -30 all rolls. 2 HP/day. Fever. Heal -30   |
| 4     | Mortification | 10+ days           | Incapacitated. 5 HP/day. Death in 2–5 days |

**Progression:** Failed heal check at each stage advances infection to the
next stage. Successful check at Stage 1 contains it; at Stage 2 retreats to
Stage 1; at Stage 3 stabilizes at Stage 2. Mortification requires
amputation of affected limb or death.

**Wound-Fever (Sárhiti):** Systemic fever from Stage 2+ infection. Daily
TOU check to break fever (difficulty scales with infection stage). Adds -5
additional to all rolls when feverish.

### 5.10 Bone Complications

#### Simple Fracture

Bone broken, skin intact. Treatment: traction + splinting. Immobilize joint
above and below break. See bone injury healing table (§ 5.8).

#### Compound Fracture

Bone broken AND skin breached. Emergency. Infection base: 40%. Treatment:
irrigate, reduce bone, set, splint, dress wound. Double healing time of
simple fracture.

#### Dislocated Joint

Joint forced from socket. Reduction required within hours (muscle spasm
makes later reduction very difficult). After reduction, joint works
immediately but is loose and re-dislocation prone for weeks.

### 5.11 Pain System

Pain is not a modifier. Wounds already carry mechanical penalties (§ 5.2, §
5.13). Pain is a narrative layer — it shapes how a character acts, speaks,
thinks, and sleeps. The simulation tracks pain level; the prose renders
what pain _does_ to a person.

> Pain does not stack with wound penalties. It coexists. A man > with a
  serious arm wound already fights at -15 to that arm. Pain > tells you
  _how_ he fights at -15: whether he flinches before the > swing, whether
  his breathing has gone shallow, whether he has > stopped speaking.

#### Pain Levels

| Pain Level  | What the Man Experiences                                     |
| ----------- | ------------------------------------------------------------ |
| None        | Nothing. The body is quiet.                                  |
| Mild        | A dull ache noticed only at rest or when pressing the wound. |
| Moderate    | A deep throb that refuses to fade. Constant companion.       |
| Severe      | Sharp, shooting, breath-catching. Comes in waves.            |
| Agonizing   | Overwhelming. The world shrinks to the wound.                |
| Unconscious | Pain exceeds tolerance. Body shuts down.                     |

#### Pain Modifiers by Wound State

| Wound Condition       | Pain Adjustment                                    |
| --------------------- | -------------------------------------------------- |
| Fresh wound           | One step above wound severity base                 |
| Treated wound         | Wound severity base                                |
| Infected wound        | Two steps above current wound severity             |
| Knitting wound        | One step below wound severity base                 |
| Scarring wound        | None or Mild (weather-sensitive)                   |
| Cauterized wound      | Agonizing (day 1), Severe (day 2–3), then Moderate |
| Amputated             | Agonizing → Severe → Moderate → Mild (weeks)       |
| Bone fracture (set)   | Moderate (immobilized), Severe (any movement)      |
| Bone fracture (unset) | Severe (constant), Agonizing (any movement)        |
| Dislocated joint      | Agonizing until reduced, then Moderate             |

#### Narrative Effects of Pain

These are rendering directives. They tell the prose what to show. They do
not add numerical penalties — the wound penalties already cover that.

**Mild pain — the ache beneath attention:**

- The character adjusts posture often, favouring the wound side.
- Fine tasks take fractionally longer as fingers hesitate.
- Sleep is restless but possible.

**Moderate pain — the constant companion:**

- The character's voice flattens. Fewer words, shorter sentences.
- Faces harden into a set jaw. Laughter disappears.
- Appetite drops. Meals become duty, not pleasure.
- Sleep requires exhaustion or ale. Dreams are thin.
- Focus narrows — long conversations become difficult to follow.
- Peripheral awareness softens. The man stares at middle distance.

**Severe pain — the breath-catcher:**

- Vision narrows. The world contracts to a corridor of focus
directly ahead. Flanking threats go unseen.
- Sudden spikes cause involuntary gasps, grunts, or hissing
through clenched teeth.
- Movement becomes deliberate and slow — the body refuses
to surprise itself.
- The character stops initiating conversation. Responds in
monosyllables when addressed.
- Hands shake on tasks requiring steadiness. Threading a
needle, drawing a bowstring, or writing become unreliable.
- Sleep is impossible without total exhaustion or strong drink.
The character dozes sitting upright, wakes at every shift.
- Pale face, cold sweat on the brow and upper lip. Others
notice before the wounded man admits it.

**Agonizing pain — the world shrinks to the wound:**

- Tunnel vision. The character can focus only on what is
directly in front of them. Everything peripheral is lost — not blurred, but
simply absent.
- Hearing goes selective. Voices sound distant and muffled,
as if underwater. The character may not respond to their name.
- Light hurts. Bright day or firelight produces a stabbing
sensation behind the eyes. The character shades their face, turns away from
flame.
- Nausea builds. The gut clenches. Vomiting is common,
especially when moved or when the wound is touched.
- Involuntary sounds — groaning, whimpering, sudden cries
at spikes — that the character cannot suppress. Pride means nothing; the
body speaks for itself.
- Decision-making collapses. The character cannot weigh options.
They follow orders or repeat the last thing they were doing. Initiative is
gone.
- Time distorts. Minutes feel like hours. The character loses
track of when events happened. "Was that this morning or yesterday?"
- The character forgets to eat, drink, or relieve themselves
unless reminded. The body has one priority.
- Others must make choices for them. Dalla says "drink this" and
hands appear and the cup is at his lips before he knows he moved.

**Unconscious pain threshold:**

- The character collapses. Eyes roll back. Breathing goes
shallow and rapid.
- Responds to nothing — not voice, not cold water, not a slap.
Only the leech's work can bring them back by reducing the pain source.

#### Pain and Willpower

Characters enduring Moderate+ pain make daily WIL checks.

- **Success:** Endures. No mechanical change. The prose may
note clenched fists or bitten lips.
- **Failure:** Temporary WIL degradation (-1 until a full day of
pain-free rest). The character becomes passive, withdrawn, or irritable.
- **Chronic pain** (14+ continuous days at Severe or above):
permanent -1 WIL. The character's baseline shifts. They become someone who
has learned to live with it — quieter, harder, or more brittle, depending
on who they were before.

Recovery: 1 temporary WIL point per day of pain-free rest. Permanent WIL
loss does not recover.

#### Pain in Combat (Narrative Rendering)

When combat_sim produces rounds, pain level shapes the prose description of
the fighter's actions:

| Pain Level | Combat Prose Directive                                                                                                                                                  |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| None–Mild  | Normal combat narration. No pain references.                                                                                                                            |
| Moderate   | Note favouring: shortened swings, guarded stance, slow recovery between exchanges.                                                                                      |
| Severe     | Mention: flinch before commitment, pale face, teeth clenched, breath hissing. He fights like a man who knows exactly where the wound is.                                |
| Agonizing  | Tunnel vision explicit: "He cannot see the second man." Delayed reactions. Swings that stop short because the body refuses to follow through. Stumbling after exertion. |

#### Pain and Sleep

| Pain Level | Sleep Quality                                                                                                             |
| ---------- | ------------------------------------------------------------------------------------------------------------------------- |
| None–Mild  | Normal. Wakes rested.                                                                                                     |
| Moderate   | Tosses. Wakes stiff. Rest quality counts as field_rest even in a hall.                                                    |
| Severe     | Cannot sleep without exhaustion or strong drink. Rest counts as active_duty for healing purposes.                         |
| Agonizing  | No real sleep. Passes out from exhaustion in fragments. No healing benefit. WIL check each morning or temporary WIL loss. |

#### Pain and Weather

Old scars carry memory of the wounds that made them. Before weather changes
(rime storms, deep cold, damp), healed wounds ache. Characters with
weather-sensitive scars experience a brief rise in pain level (one step,
lasting hours) that serves as an involuntary forecast. This is covered in §
5.14.

### 5.12 Incapacitation System

Wounds produce specific functional impairments tracked as incapacitation
records.

```yaml
incapacitation:
  id: "inc_001"
  source_wound: "w_001"
  location: "right_arm"
  sublocation: "forearm_outer"
  type: "limited_motion" # See types below
  severity: "moderate" # mild, moderate, severe, total
  description: "Partially severed extensor muscle."
  mechanical_effect: "-15 to weapon use with right hand."
  activity_effects:
    - activity: "weapon_swing"
      penalty: -15
    - activity: "shield_grip"
      penalty: -10
    - activity: "climbing"
      penalty: -20
    - activity: "fine_work"
      penalty: -25
  pain_level: "moderate"
  duration: "temporary" # temporary, long_term, permanent
  days_remaining: 14
  can_worsen: true
  can_improve: true
```

#### Incapacitation Types

| Type            | Description                  | Common Causes                          |
| --------------- | ---------------------------- | -------------------------------------- |
| pain            | Pain impedes function        | Any wound, inflammation, infection     |
| limited_motion  | Reduced range of movement    | Tendon damage, contracture, joint      |
| weakness        | Reduced strength             | Muscle damage, nerve, atrophy          |
| numbness        | Loss of sensation            | Nerve damage, frostbite, crush         |
| instability     | Joint gives way under load   | Ligament damage, repeated dislocation  |
| tremor          | Involuntary shaking          | Nerve damage, head trauma, infection   |
| stiffness       | Limb resists movement        | Scar contracture, poorly healed break  |
| impaired_sense  | Vision, hearing, balance     | Head wound, ear damage, eye injury     |
| impaired_speech | Cannot speak clearly         | Jaw injury, throat wound, tooth loss   |
| impaired_breath | Breathing labored or painful | Rib fracture, chest wound, lung damage |
| amputation      | Body part missing            | Surgical or traumatic loss             |

### 5.13 Activity-Specific Penalty Tables

#### Head Wound Penalties

| Sublocation | Mild (-5)                     | Moderate (-15)                 | Severe (-30)                         | Total (-50+)                      |
| ----------- | ----------------------------- | ------------------------------ | ------------------------------------ | --------------------------------- |
| Scalp       | Blood in eyes until bandaged  | Headache, light sensitivity    | Skull exposed, bone infection risk   | —                                 |
| Temple      | Ringing ears, mild dizziness  | Vertigo, nausea, double vision | Unconsciousness, seizures            | Death or permanent brain damage   |
| Jaw         | Painful chewing, swollen      | No solid food, slurred speech  | Jawbone broken, bound with leather   | Permanent feeding difficulty      |
| Ear         | Tinnitus, muffled hearing     | Partial deafness that side     | Total deafness, balance impaired     | Permanent vertigo                 |
| Eye socket  | Swollen shut (temporary)      | Vision blurred or partial loss | Eye destroyed, depth perception gone | —                                 |
| Nose        | Swollen, mouth breathing      | Broken, must be reset          | Cartilage destroyed, breathing limit | —                                 |
| Throat      | Hoarse voice, painful swallow | Cannot project voice           | Crushed windpipe, breathing crisis   | Severed artery — death in minutes |

#### Arm and Hand Wound Penalties

| Sublocation | Mild (-5)                  | Moderate (-15)                      | Severe (-30)                     | Total (-50+)                  |
| ----------- | -------------------------- | ----------------------------------- | -------------------------------- | ----------------------------- |
| Upper arm   | Aching lift, tires quickly | Cannot raise above shoulder         | Arm hangs, needs sling           | Arm useless, amputation risk  |
| Elbow       | Painful to extend/flex     | Cannot straighten or bend past 90°  | Joint locked at one angle        | Joint destroyed, arm lost     |
| Forearm     | Weak grip, clumsy tools    | Cannot twist forearm                | Major muscle severed, hand weak  | Both bones broken, arm flails |
| Wrist       | Painful under load         | Cannot flex/extend hand             | Joint fused by scar, fixed angle | —                             |
| Fingers     | Stiff, slow grip           | One or two locked/missing           | Multiple gone, grip is a clamp   | Hand is a claw or stump       |
| Thumb       | Weak pinch, drops items    | Cannot oppose, cannot grip properly | Thumb gone, cannot hold weapon   | —                             |
| Palm        | Painful grip               | Tendon damage, fingers don't close  | Open wound, no grip until healed | —                             |

**Arm/hand activity impairments:**

| Activity           | Weapon-Arm Wound Effect                    | Shield-Arm Wound Effect                |
| ------------------ | ------------------------------------------ | -------------------------------------- |
| Weapon swing       | Shortened arc, reduced power, slow recover | Compromised balance, less wind-up      |
| Shield hold        | N/A (use other arm)                        | Shield sags, guard opens, arm tires    |
| Shield bash        | N/A                                        | Cannot generate force                  |
| Two-handed weapon  | Cannot grip or control                     | Cannot grip or control                 |
| Throwing           | Reduced range/accuracy, painful release    | Impaired balance during throw          |
| Climbing           | Cannot grip/pull with that arm             | Cannot grip/pull with that arm         |
| Carrying           | Load must go on other arm or back          | Load must go on other arm or back      |
| Sewing / repair    | Cannot hold needle/thread in that hand     | Cannot hold fabric taut                |
| Rowing             | Stroke weak on that side                   | Stroke weak on that side               |
| Fire-starting      | Cannot grip/strike fire-steel consistently | Cannot hold tinder nest or flint       |
| Cooking/butchering | Cannot cut, chop, or stir with that hand   | Cannot hold meat or pot steady         |
| Tying knots        | One-handed knotting (slow, unreliable)     | One-handed knotting (slow, unreliable) |

#### Leg and Foot Wound Penalties

| Sublocation | Mild (-5)                    | Moderate (-15)                    | Severe (-30)                       | Total (-50+)                      |
| ----------- | ---------------------------- | --------------------------------- | ---------------------------------- | --------------------------------- |
| Thigh       | Aching stride, tires quickly | Visible limp, cannot run          | Cannot bear weight without support | Leg useless, carried/amputated    |
| Knee        | Stiff, painful kneeling      | Cannot kneel/pivot, gives way     | Knee locked or collapses           | Joint destroyed, leg rigid/floppy |
| Shin        | Sharp pain on impact         | Cracked bone, every step a wince  | Broken tibia, cannot walk          | Compound fracture, amputation     |
| Calf        | Tight, cramps on hills       | Cannot push off, stride shortened | Achilles severed, foot drops       | —                                 |
| Ankle       | Stiff, swollen, painful      | Cannot rotate foot, flat only     | Joint wrecked, permanent angle     | —                                 |
| Toes        | Painful in boots             | Missing toe(s), balance affected  | Multiple toes gone, push-off lost  | Flat shuffle only                 |
| Arch        | Painful on hard ground       | Every step sends pain upward      | Bones broken, no weight bearing    | Foot crushed, amputation likely   |
| Heel        | Bruise ache, avoids impacts  | Cracked heel bone                 | Shattered, side-of-foot walking    | —                                 |

**Leg/foot activity impairments:**

| Activity            | Thigh Wound                       | Knee Wound                       | Lower Leg/Ankle/Foot             |
| ------------------- | --------------------------------- | -------------------------------- | -------------------------------- |
| Walking (flat)      | Limp, shortened stride            | Stiff-legged gait, no bend       | Shuffle, favoring other foot     |
| Walking (rough)     | Very slow, must pick footing      | Dangerous — knee gives on uneven | Extreme pain, ankle rolls easily |
| Running             | Cannot, or very painful/slow      | Impossible                       | Impossible or painful shuffle    |
| Kneeling            | Painful but possible              | Agonizing or impossible          | Difficult, pain on compression   |
| Standing from kneel | Must use arms, slow               | Roll to other knee and push up   | Weight on good foot only         |
| Climbing stairs     | Leads with good leg, halved speed | One step at a time, arms on wall | One step at a time, arms support |
| Shield wall stance  | Cannot brace, pushed back easily  | Cannot hold low stance           | Cannot plant, slides under push  |
| Jumping             | Reduced distance, painful land    | Impossible                       | Impossible                       |

#### Torso Wound Penalties

| Sublocation | Mild (-5)                    | Moderate (-15)                       | Severe (-30)                          | Total (-50+)                     |
| ----------- | ---------------------------- | ------------------------------------ | ------------------------------------- | -------------------------------- |
| Chest front | Pain on deep breath          | Cannot fill lungs, stamina halved    | Rib(s) broken, lung risk              | Chest caved, mortal              |
| Chest side  | Pain on twisting             | Cannot rotate torso, swings weakened | Floating rib broken, internal bleed   | Multiple ribs, breathing failure |
| Belly upper | Nausea, painful after eating | Vomiting blood, internal bleed risk  | Organ damage, peritonitis (mortal)    | Gut perforated — mortal          |
| Belly lower | Cramping, difficulty bending | Blood in urine, bladder compromise   | Gut wound, mortal without miracle     | —                                |
| Flank       | Deep ache, painful twist     | Kidney bruised, blood in urine       | Kidney ruptured, internal bleed       | —                                |
| Back upper  | Stiff, painful weapon swing  | Shoulder blade cracked, arm limited  | Spine at risk, partial paralysis      | Spinal cord damaged, paralysis   |
| Back lower  | Cannot bend without pain     | Cannot lift from ground              | Cannot stand upright, must be carried | Spine fractured, legs lost       |
| Shoulder    | Arm tires faster             | Cannot raise arm above shoulder      | Dislocated/destroyed, arm in sling    | Joint shattered, arm disabled    |

**Chest wound breathing effects:**

| Activity          | Rib Bruise             | Cracked Rib             | Broken Rib                   | Multiple Broken Ribs      |
| ----------------- | ---------------------- | ----------------------- | ---------------------------- | ------------------------- |
| Breathing at rest | Shallow, catches       | Shallow, one-sided      | Gasping, cannot inhale full  | Labored, visible effort   |
| On exertion       | Panting, quick fatigue | Cannot sustain effort   | Any effort produces distress | Cannot exert at all       |
| Coughing          | Sharp pain             | Doubles over in agony   | May cough blood              | Coughing may kill         |
| Speaking loudly   | Voice catches          | Cannot project          | Whisper only                 | Cannot sustain speech     |
| Sleeping          | One position only      | Cannot lie on that side | Must sleep propped upright   | Cannot sleep without pain |
| Lifting           | Painful, avoided       | Cannot lift above waist | Cannot lift anything         | Cannot lift anything      |

### 5.14 Weather Sensitivity of Scars

Old scars and healed fractures ache before weather changes (barometric
pressure effect). Mechanical effects:

- Before rime storm: old wounds throb, healed fractures ache, scar
tissue pulls tight.
- In deep cold: healed frostbite sites burn and tingle.
- In damp: old joint injuries stiffen.

Characters with 3+ healed serious wounds or any healed critical wound gain
Weather-sense 1 (passive) — their body predicts weather. Stacks with
existing Weather-sense skill.

### 5.15 Special Conditions

#### The Wound-Addled (Sárviti)

**Threshold:** 5+ healed serious wounds, or 2+ healed critical wounds, or
any healed mortal wound.

**Effects:**

- Flinch reflex: -5 to initiative.
- Pain sensitivity: pain levels from new wounds one step higher.
- Weather-sensitivity stacks (all old wounds ache together).
- Will erosion: -1 permanent WIL.

#### The Iron Scar (Járnörr)

Rare. Character who healed a mortal wound carries authority among fighting
men.

**Effects:**

- +1 Intimidate (the scar speaks before the man does).
- -1 maximum HP permanently.
- Weather-sensitivity at the mortal wound site.
- Other characters treat the bearer differently.

### 5.16 Health Subsystem Commands

These commands drive the wound lifecycle. Invoked by the narrative director
(AI) to track state changes as the story progresses.

#### wound_apply

Apply a new wound to a character.

```yaml
command: wound_apply
target: "Kell Hook"
wound:
  location: "right_arm"
  sublocation: "forearm_outer"
  type: "hewn"
  severity: "serious"
  damage: 9
  bleeding: 1
  description: "A bearded axe catches Kell across the outer forearm."
  inflicted_by: "Bandit Raider"
  weapon_used: "bearded_axe"
  foreign_body: true
  foreign_body_type: "cloth"
```

**Effects:** Creates wound record, subtracts HP, adds bleeding, triggers
incapacitation check, updates condition.

#### wound_treat

Apply medical treatment to an existing wound.

```yaml
command: wound_treat
target: "Kell Hook"
wound_id: "w_001"
treatment_type: "field_surgery"
treated_by: "Dalla"
actions:
  ["cleaned", "foreign_body_removed", "stitched", "poulticed", "bandaged"]
```

**Treatment types:**

| Type          | Prerequisites           | Heal Mod | Infection Reduction | Healing Speed   |
| ------------- | ----------------------- | -------- | ------------------- | --------------- |
| first_aid     | Heal 0+ (anyone)        | -10      | -5%                 | ×1.0            |
| field_surgery | Heal 2+                 | +0       | -15%                | ×0.8            |
| full_surgery  | Heal 3+, shelter, tools | +10      | -25%                | ×0.6            |
| cauterized    | Heal 1+, fire, iron     | +0       | -20%                | ×1.3 (burn)     |
| amputated     | Heal 2+, tools          | -15      | Removes source      | N/A (new wound) |

**Heal check resolution:**

```text
heal_check = (WIT × 5) + (Heal × 10) + 15
  + treatment_type_modifier + wound_severity_modifier
  + environment_modifier + tool_modifier

wound_severity: scratch +20, light +10, serious +0,
  critical -15, mortal -30
environment: dry hall +10, clean camp +0, wet camp -10,
  field -15, combat -25
tools: full kit +10, basic +0, improvised -10, nothing -20
```

**Success:** Wound properly treated. Healing clock starts. Bleeding stops.
Infection chance reduced per treatment type.

**Failure:** Treatment partial. 50% chance bleeding continues. Infection
reduction halved. Foreign bodies may be missed (+15% infection chance).

**Critical failure:** Treatment worsens condition. Possible wound
re-opening, additional damage, incorrect bone setting.

#### wound_heal

Advance a wound's healing timeline during time-skip or daily resolution.

```yaml
command: wound_heal
target: "Kell Hook"
wound_id: "w_001"
days_elapsed: 7
rest_quality: "field_rest"
complications_check: true
```

Each wound's `healing_day_count` advances by `days_elapsed ×
rest_quality_multiplier`. When count reaches next stage threshold, wound
advances. Complication check rolls for infection (Stages 1–2), re-opening
(Stage 4 + active duty), and bone re-break (knitting + heavy activity).

#### wound_infect

Manually apply infection to a wound when narrative conditions warrant.

```yaml
command: wound_infect
target: "Kell Hook"
wound_id: "w_001"
infection_stage: "early"
cause: "Foreign cloth fragment missed during treatment."
```

#### wound_worsen

Increase wound severity (re-opening, infection advance, aggravation).

```yaml
command: wound_worsen
target: "Kell Hook"
wound_id: "w_001"
new_severity: "critical"
cause: "Stitches tear during shield-wall collapse."
```

**Effects:** Updates severity and penalties, resets healing to "fresh",
restarts bleeding, updates incapacitation. HP damage = difference between
old and new severity.

#### wound_improve

Decrease wound severity (effective treatment, high TOU, excellent care).

```yaml
command: wound_improve
target: "Kell Hook"
wound_id: "w_001"
new_severity: "light"
cause: "Dalla's comfrey poultice and fourteen days of rest."
```

Does NOT reset healing stage — improvement accelerates healing.

#### wound_scar

Convert healed wound to permanent scar record.

```yaml
command: wound_scar
target: "Kell Hook"
wound_id: "w_001"
scar:
  description: "White ridge from elbow to wrist on outer forearm."
  visibility: "obvious" # hidden, visible, obvious, disfiguring
  permanent_effect:
    type: "weakness"
    severity: "mild"
    activity_effects:
      - activity: "sustained_grip"
        penalty: -5
      - activity: "climbing"
        penalty: -5
  weather_sensitive: true
  narrative_tag: "Kell rubs the white line on his forearm when thinking."
```

#### wound_remove

Fully remove a resolved wound (scratches, healed minor wounds).

```yaml
command: wound_remove
target: "Kell Hook"
wound_id: "w_003"
reason: "Scratch on left hand. Healed in two days, no scar."
```

#### amputation

Specialized command for limb loss.

```yaml
command: amputation
target: "Ubbe Ironside"
location: "left_arm"
sublocation: "below_elbow"
reason: "Deep rot advanced to mortification."
performed_by: "Dalla"
method: "bone_saw_and_cautery"
```

**Effects:** Resolves all wounds on amputated portion. Creates surgical
wound at stump. Creates permanent incapacitation record. Reduces max_hp:

| Lost Part       | HP Reduction |
| --------------- | ------------ |
| Hand            | -2           |
| Forearm (below) | -4           |
| Full arm        | -6           |
| Foot            | -3           |
| Below knee      | -5           |
| Full leg        | -8           |
| Eye             | -1           |
| Ear             | -1           |

#### condition_update

Recalculate overall condition based on all active wounds, infections, and
incapacitations.

| Condition              | Criteria                                        |
| ---------------------- | ----------------------------------------------- |
| Dead                   | HP <= 0 and no Heal check success               |
| Dying                  | Mortal wound, or HP <= 0 with active Heal check |
| Incapacitated          | Critical wound untreated, or mortification      |
| Badly wounded          | Serious wound untreated, or infection Stage 3+  |
| Wounded (limited)      | Light wound or treated serious wound            |
| Wounded (recovering)   | All wounds in Stage 3+ (closing/knitting)       |
| Exhausted              | No wounds but stamina/rest depleted             |
| Scarred but functional | All wounds resolved, permanent effects present  |
| Healthy                | No active wounds or effects                     |

### 5.17 Combat Sim Integration

When `combat_sim.py` produces a wound, the health subsystem converts it to
a full wound record:

```python
# combat_sim.py produces:
wound = Wound(location="right_arm", severity="serious",
              damage=9, bleeding=1)

# Health subsystem expands to full record:
wound_record = {
    "id": generate_wound_id(),
    "location": "right_arm",
    "sublocation": determine_sublocation("right_arm"),
    "type": weapon_to_wound_type(weapon_used),
    "severity": "serious",
    "damage": 9,
    "bleeding": 1,
    "description": generate_wound_description(
        location, sublocation, type, severity, weapon),
    "inflicted_day": current_day,
    "inflicted_by": attacker.name,
    "weapon_used": weapon_used,
    "treated": False,
    "healing_stage": "fresh",
    "clean": True,
    "infected": False,
}
```

Statblocks (`22_MEMBER_STATBLOCKS.md`) and band state
(`data/band_state.yaml`) are updated when wound commands execute.

### 5.18 Psychological Trauma System

Trauma is tracked alongside physical wounds. Where wounds damage the body,
trauma damages the _hugr_ (mind-soul). The system mirrors the physical
wound lifecycle: trauma is inflicted, manifests, worsens or recovers, and
leaves permanent marks.

> **Lore reference:** `psychological_trauma.md` covers period- > accurate
  Norse concepts of mind-damage, presentation patterns, > coping
  mechanisms, cultural constraints, and rendering rules. > This section
  covers only simulation mechanics.

#### Trauma Stress Points (TSP)

Every character has a **Stress Threshold** derived from WIL:

```text
stress_threshold = WIL × 3
```

**Trauma Stress Points (TSP)** accumulate from traumatic events. When TSP
exceeds the stress threshold, a **trauma condition** manifests. TSP does
not reset when a condition manifests — the threshold is recalculated
against the new WIL baseline.

### 5.19 Trauma Sources and Severity

Each traumatic event has a base TSP cost:

| Event Category             | TSP  | Examples                                 |
| -------------------------- | ---- | ---------------------------------------- |
| Minor shock                | 1–2  | First kill, witnessing a brawl death     |
| Combat exposure            | 2–4  | Full engagement, being wounded           |
| Severe combat              | 4–6  | Nearly dying, seeing a companion die     |
| Horror-sight               | 5–8  | Atrocity, torture, mass death            |
| Betrayal-wound             | 4–7  | Oath broken against you, abandoned       |
| Shield-brother death       | 6–10 | Losing your skjaldvinr                   |
| Killing unarmed/helpless   | 3–6  | Moral injury from own actions            |
| Extended deprivation       | 2–4  | Starvation, exposure, captivity (per wk) |
| Cumulative campaign stress | 1/wk | Ongoing active campaign beyond 4 weeks   |

**TSP Modifiers:**

| Condition                        | TSP Modifier                      |
| -------------------------------- | --------------------------------- |
| Active shield-bond (skjaldvinr)  | -2 TSP                            |
| Strong belief framework (WYR 3+) | -1 TSP                            |
| Already carrying 2+ conditions   | +2 TSP                            |
| Chronic pain (physical)          | +1 TSP                            |
| Drunk during event               | -1 TSP (deferred +2 next morning) |
| First exposure (no prior combat) | +2 TSP                            |

### 5.20 Trauma Conditions

When TSP exceeds stress_threshold, a trauma condition manifests. The type
depends on the triggering event and the character's personality (WIL,
background, existing conditions).

#### Trauma Record Schema

```yaml
trauma:
  id: "t_001"
  condition: "flinch_sickness"
  source_event: "Shield-brother Rolf killed beside him"
  source_day: 142
  severity: "moderate"
  tsp_at_onset: 18
  triggers:
    - "sudden_sounds"
    - "iron_clang"
  manifestation: "chronic"
  recovery_stage: "active"
  recovery_day_count: 0
  will_cost: 0
  resolved: false
  residual: null
```

#### Condition Types

| Condition        | Key               | Primary Manifestation                    |
| ---------------- | ----------------- | ---------------------------------------- |
| Battle-shock     | `battle_shock`    | Freezing, vacancy, inability to act      |
| Night terrors    | `night_terrors`   | Sleep disruption, waking panic           |
| Flinch-sickness  | `flinch_sickness` | Startle response, trigger sensitivity    |
| Anger-storm      | `anger_storm`     | Disproportionate rage, loss of control   |
| Killing-calm     | `killing_calm`    | Emotional numbness during/after violence |
| Withdrawal       | `withdrawal`      | Social isolation, loss of engagement     |
| Drink-need       | `drink_need`      | Functional dependence on alcohol         |
| Risk-seeking     | `risk_seeking`    | Death-wish behavior, reckless engagement |
| Grief-lock       | `grief_lock`      | Inability to move past a loss            |
| Mind-flight      | `mind_flight`     | Dissociation, vacancy, losing time       |
| Heavy-mindedness | `heavy_mind`      | Persistent low mood, loss of drive       |

#### Condition Severity

| Severity  | Mechanical Effect                                      |
| --------- | ------------------------------------------------------ |
| Mild      | -5 on rolls related to trigger; WIL check 1/week       |
| Moderate  | -10 on trigger rolls; -5 general; WIL check 1/day      |
| Severe    | -15 on trigger rolls; -10 general; WIL check 2/day     |
| Crippling | -20 all rolls; cannot initiate combat; WIL check 3/day |

#### Condition-Specific Penalties

| Condition       | Additional Effect                                      |
| --------------- | ------------------------------------------------------ |
| battle_shock    | Cannot act for 1d6 rounds when trigger fires           |
| night_terrors   | Rest quality one step worse; band morale -1 if shared  |
| flinch_sickness | -5 initiative; perception penalty from blind-spot      |
| anger_storm     | Failed WIL check = attack nearest target (friend/foe)  |
| killing_calm    | +5 combat rolls; -10 all social; loyalty loss -1/month |
| withdrawal      | -10 Command/Persuade targeting this character          |
| drink_need      | -5 all rolls when sober >12hrs; immune to fear drunk   |
| risk_seeking    | Ignores retreat/cover orders on failed WIL check       |
| grief_lock      | Cannot form new shield-bonds; -10 Morale contribution  |
| mind_flight     | Lose 1d6 minutes during trigger; -5 all concentration  |
| heavy_mind      | -5 all rolls; march speed -1 tier; no initiative acts  |

### 5.21 Trauma Triggers

Each condition has associated triggers — stimuli that activate the acute
response. Triggers are specific and tracked per condition.

#### Common Triggers (by Source Event)

| Source                   | Likely Triggers                                       |
| ------------------------ | ----------------------------------------------------- |
| Battle / combat wound    | Iron clang, war-cries, blood smell, sudden movement   |
| Shield-brother death     | Empty seat, the dead man's name, similar faces        |
| Horror-sight             | Corpses, fire (if burning), children, confined spaces |
| Betrayal                 | Oaths, promises, being left behind, locked doors      |
| Starvation / deprivation | Empty plates, food waste, cold, tight spaces          |
| First kill               | Blood on hands, knife-edge glint, the dying sound     |

#### Trigger Check

When a trigger is encountered, the character makes a **WIL check**:

```text
Target: 50 + (WIL × 5) + modifiers
Roll: d100
Success: The man endures. Visible tension but no breakdown.
Failure: Condition activates for 1d6 × 10 minutes (combat) or
         1d6 hours (non-combat). See condition-specific effects.
Critical failure: Condition activates at one severity worse.
                  +1 TSP added.
```

**Trigger check modifiers:**

| Factor                | Modifier |
| --------------------- | -------- |
| Shield-brother nearby | +10      |
| Dalla present         | +5       |
| At the fire (camp)    | +5       |
| Drunk (moderate)      | +5       |
| Drunk (heavy)         | -10      |
| Fatigued              | -10      |
| In pain (moderate+)   | -5       |
| Night / darkness      | -5       |
| Alone                 | -10      |

### 5.22 Trauma Recovery

Recovery is slow, non-linear, and not guaranteed. A man can improve,
plateau, or relapse. There are no medications and no therapy — only time,
conditions, and the band.

#### Recovery Stages

| Stage    | Duration            | Effect                                                         |
| -------- | ------------------- | -------------------------------------------------------------- |
| Acute    | 0–7 days            | Full condition severity; high TSP                              |
| Active   | 1–8 weeks           | Condition active; triggers frequent                            |
| Easing   | 2–12 weeks          | Severity drops one step; triggers less frequent (check 1/week) |
| Residual | Permanent or months | Mild trigger sensitivity remains; may flare under new stress   |
| Resolved | Permanent           | Condition removed; TSP reduced                                 |

#### Recovery Factors

Recovery advances when **recovery conditions** are met. Each day of met
conditions accumulates **recovery points (RP)**. Recovery thresholds by
severity:

| Severity  | RP to Advance Stage |
| --------- | ------------------- |
| Mild      | 14                  |
| Moderate  | 30                  |
| Severe    | 60                  |
| Crippling | 120                 |

**Daily recovery point generation:**

| Condition                         | RP/Day |
| --------------------------------- | ------ |
| Full rest, secure hall            | 3      |
| Field rest, safe camp             | 2      |
| Active duty, no combat            | 1      |
| Active duty, combat this week     | 0      |
| Meaningful work (non-combat task) | +1     |
| Shield-brother present            | +1     |
| Dalla's care (seiðr/herbs)        | +1     |
| Saga-told (their deeds retold)    | +1     |
| Fire inclusion (nightly)          | +0.5   |
| Trigger event this day            | -2     |
| New trauma this week              | -5     |
| Drunk (self-medicating)           | -1     |
| Isolation (by choice)             | -2     |

#### Recovery Check

When sufficient RP accumulates, the character makes a **WIL check** to
advance to the next recovery stage:

```text
Target: 40 + (WIL × 5) + recovery_modifiers
Roll: d100

Success: Advance to next recovery stage.
Failure: No advancement. RP resets to 75% of threshold.
Critical failure: Relapse — severity worsens by one step.
                  RP resets to zero.
Critical success: Advance two stages. TSP reduced by 2.
```

#### WIL Degradation from Trauma

Unresolved trauma erodes WIL over time:

| Duration Unresolved | WIL Effect                         |
| ------------------- | ---------------------------------- |
| < 30 days           | Temporary -1 WIL (recovers)        |
| 30–90 days          | Temporary -2 WIL (recovers slowly) |
| 90+ days            | Permanent -1 WIL per 90 days       |
| Crippling severity  | Permanent -1 WIL immediately       |

Temporary WIL recovers: 1 point per 14 days of resolved condition.
Permanent WIL loss does not recover.

### 5.23 Psychological Profile Fields

Each member's statblock includes a psychological profile that tracks
accumulated trauma, resilience status, and behavioral baseline:

```yaml
psychological_profile:
  tsp: 12
  stress_threshold: 15
  trauma_conditions:
    - id: "t_001"
      condition: "night_terrors"
      severity: "moderate"
      recovery_stage: "active"
      triggers: ["sudden_sounds", "iron_clang"]
  resilience_factors:
    shield_bond: "Kell Hook"
    belief_framework: "moderate"
    prior_recoveries: 1
    coping_method: "fire_and_drink"
  behavioral_baseline:
    speech_pattern: "terse_but_functional"
    sleep_quality: "poor"
    appetite: "reduced"
    social_engagement: "minimal"
    drinking_level: "moderate"
  will_damage:
    temporary: 0
    permanent: 1
  trauma_history:
    - event: "Hall fire that killed family"
      day: 0
      tsp_gained: 8
      conditions_produced: ["flinch_sickness"]
```

The profile is maintained alongside physical wound/scar records.
`condition_update` (§ 5.16) factors in active trauma conditions when
computing overall member state.

### 5.24 Trauma Subsystem Commands

All commands mutate member state and return result dicts. CLI interface
matches `wounds.py` conventions.

#### trauma_apply

Inflict a traumatic event. Adds TSP, checks for condition manifestation.

```yaml
command: trauma_apply
target: "Ubbe Ironside"
event: "Shield-brother Rolf killed beside him"
category: "shield_brother_death"
tsp: 8
day: 142
modifiers:
  shield_bond_active: false
  chronic_pain: true
```

**Process:**

1. Calculate effective TSP (base + modifiers).
2. Add TSP to member total.
3. If TSP > stress_threshold: select condition type based on
event category and character profile.
4. Set condition severity based on overshoot
(TSP - threshold): 0–3 = mild, 4–8 = moderate, 9–15 = severe, 16+ =
crippling.
5. Generate triggers from source event.
6. Update behavioral baseline.

#### trauma_trigger

Fire a trigger check. Resolves whether the condition activates and for how
long.

```yaml
command: trauma_trigger
target: "Ubbe Ironside"
trauma_id: "t_001"
trigger: "iron_clang"
context: "combat"
modifiers:
  shield_brother_nearby: true
  fatigued: false
```

#### trauma_recover

Advance recovery timeline by elapsed days and conditions.

```yaml
command: trauma_recover
target: "Ubbe Ironside"
trauma_id: "t_001"
days_elapsed: 7
conditions:
  rest_quality: "field_rest"
  meaningful_work: true
  shield_brother_present: false
  dalla_care: true
  fire_inclusion: true
  trigger_events_today: 0
  isolation: false
  drunk: false
```

#### trauma_worsen

Increase trauma severity (relapse, new trigger event, compound stress).

```yaml
command: trauma_worsen
target: "Ubbe Ironside"
trauma_id: "t_001"
new_severity: "severe"
cause: "Another companion killed. The old pattern returns."
tsp_added: 4
```

#### trauma_improve

Decrease trauma severity (successful recovery check, extraordinary event).

```yaml
command: trauma_improve
target: "Ubbe Ironside"
trauma_id: "t_001"
new_severity: "mild"
cause: "Winter quarters. Three months of secure rest."
```

#### trauma_resolve

Mark a trauma condition as resolved. May leave residual marker.

```yaml
command: trauma_resolve
target: "Ubbe Ironside"
trauma_id: "t_001"
residual: "Remains sensitive to sudden iron sounds. Flinch is
  gone but the man still turns his head."
tsp_reduction: 6
```

#### trauma_add_condition

Manually add a trauma condition (for backstory, for events outside normal
TSP flow).

```yaml
command: trauma_add_condition
target: "Thorne Ash-Born"
condition: "flinch_sickness"
severity: "mild"
source: "Backstory — hall fire"
triggers: ["open_flame", "smoke_smell", "screaming"]
```

#### profile_update

Recalculate full psychological profile from all active conditions, TSP, WIL
degradation, and resilience factors.

```yaml
command: profile_update
target: "Ubbe Ironside"
```

### 5.25 Trauma and Combat Integration

When `combat_sim.py` produces a kill, a wound, or a significant event, the
trauma subsystem checks for TSP accrual:

```python
# After combat resolution:
for fighter in all_fighters:
    tsp = 0
    if fighter.kills_this_fight > 0 and fighter.total_kills < 3:
        tsp += 2  # early kills carry more weight
    if fighter.saw_companion_die:
        tsp += 6  # shield-brother death
    elif fighter.saw_companion_wounded_critical:
        tsp += 3
    if fighter.hp <= fighter.max_hp * 0.25:
        tsp += 3  # nearly died
    if fighter.was_incapacitated:
        tsp += 2

    if tsp > 0:
        trauma_apply(member, event=combat_summary,
                     category=determine_category(fighter),
                     tsp=tsp, day=current_day)
```

Band-level events (Named Man death, atrocity, betrayal) trigger TSP for all
witnesses with appropriate modifiers.

### 5.26 Interaction with Physical Health

Psychological and physical damage compound:

| Physical State           | Trauma Effect                        |
| ------------------------ | ------------------------------------ |
| Chronic pain (any wound) | +1 TSP per event; -5 recovery checks |
| Wound-Addled (§ 5.15)    | +2 TSP per event; recovery RP halved |
| Active serious+ wound    | -1 RP/day recovery; trigger check -5 |
| Infection (active)       | +1 TSP per week of fever             |
| Recently amputated       | +6 TSP immediate; grief-lock risk    |

| Trauma State               | Physical Effect                         |
| -------------------------- | --------------------------------------- |
| Active moderate+ condition | Wound healing speed -25%                |
| Withdrawal (active)        | Wound treatment delayed (self-neglect)  |
| Drink-need (active)        | Infection risk +10% (poor self-care)    |
| Heavy-mindedness           | Rest quality one step worse             |
| Risk-seeking               | +50% chance of new wound per engagement |

### 5.18 Psychological Trauma System

Trauma is tracked alongside physical wounds. Where wounds damage the body,
trauma damages the _hugr_ (mind-soul). The system mirrors the physical
wound lifecycle: trauma is inflicted, manifests, worsens or recovers, and
leaves permanent marks.

> **Lore reference:** `psychological_trauma.md` covers period- > accurate
  Norse concepts of mind-damage, presentation patterns, > coping
  mechanisms, cultural constraints, and rendering rules. > This section
  covers only simulation mechanics.

#### Trauma Stress Points (TSP)

Every character has a **Stress Threshold** derived from WIL:

```text
stress_threshold = WIL × 3
```

**Trauma Stress Points (TSP)** accumulate from traumatic events. When TSP
exceeds the stress threshold, a **trauma condition** manifests. TSP does
not reset when a condition manifests — the threshold is recalculated
against the new WIL baseline.

### 5.19 Trauma Sources and Severity

Each traumatic event has a base TSP cost:

| Event Category             | TSP  | Examples                                 |
| -------------------------- | ---- | ---------------------------------------- |
| Minor shock                | 1–2  | First kill, witnessing a brawl death     |
| Combat exposure            | 2–4  | Full engagement, being wounded           |
| Severe combat              | 4–6  | Nearly dying, seeing a companion die     |
| Horror-sight               | 5–8  | Atrocity, torture, mass death            |
| Betrayal-wound             | 4–7  | Oath broken against you, abandoned       |
| Shield-brother death       | 6–10 | Losing your skjaldvinr                   |
| Killing unarmed/helpless   | 3–6  | Moral injury from own actions            |
| Extended deprivation       | 2–4  | Starvation, exposure, captivity (per wk) |
| Cumulative campaign stress | 1/wk | Ongoing active campaign beyond 4 weeks   |

**TSP Modifiers:**

| Condition                        | TSP Modifier                      |
| -------------------------------- | --------------------------------- |
| Active shield-bond (skjaldvinr)  | -2 TSP                            |
| Strong belief framework (WYR 3+) | -1 TSP                            |
| Already carrying 2+ conditions   | +2 TSP                            |
| Chronic pain (physical)          | +1 TSP                            |
| Drunk during event               | -1 TSP (deferred +2 next morning) |
| First exposure (no prior combat) | +2 TSP                            |

### 5.20 Trauma Conditions

When TSP exceeds stress_threshold, a trauma condition manifests. The type
depends on the triggering event and the character's personality (WIL,
background, existing conditions).

#### Trauma Record Schema

```yaml
trauma:
  id: "t_001"
  condition: "flinch_sickness"
  source_event: "Shield-brother Rolf killed beside him"
  source_day: 142
  severity: "moderate"
  tsp_at_onset: 18
  triggers:
    - "sudden_sounds"
    - "iron_clang"
  manifestation: "chronic"
  recovery_stage: "active"
  recovery_day_count: 0
  will_cost: 0
  resolved: false
  residual: null
```

#### Condition Types

| Condition        | Key               | Primary Manifestation                    |
| ---------------- | ----------------- | ---------------------------------------- |
| Battle-shock     | `battle_shock`    | Freezing, vacancy, inability to act      |
| Night terrors    | `night_terrors`   | Sleep disruption, waking panic           |
| Flinch-sickness  | `flinch_sickness` | Startle response, trigger sensitivity    |
| Anger-storm      | `anger_storm`     | Disproportionate rage, loss of control   |
| Killing-calm     | `killing_calm`    | Emotional numbness during/after violence |
| Withdrawal       | `withdrawal`      | Social isolation, loss of engagement     |
| Drink-need       | `drink_need`      | Functional dependence on alcohol         |
| Risk-seeking     | `risk_seeking`    | Death-wish behavior, reckless engagement |
| Grief-lock       | `grief_lock`      | Inability to move past a loss            |
| Mind-flight      | `mind_flight`     | Dissociation, vacancy, losing time       |
| Heavy-mindedness | `heavy_mind`      | Persistent low mood, loss of drive       |

#### Condition Severity

| Severity  | Mechanical Effect                                      |
| --------- | ------------------------------------------------------ |
| Mild      | -5 on rolls related to trigger; WIL check 1/week       |
| Moderate  | -10 on trigger rolls; -5 general; WIL check 1/day      |
| Severe    | -15 on trigger rolls; -10 general; WIL check 2/day     |
| Crippling | -20 all rolls; cannot initiate combat; WIL check 3/day |

#### Condition-Specific Penalties

| Condition       | Additional Effect                                      |
| --------------- | ------------------------------------------------------ |
| battle_shock    | Cannot act for 1d6 rounds when trigger fires           |
| night_terrors   | Rest quality one step worse; band morale -1 if shared  |
| flinch_sickness | -5 initiative; perception penalty from blind-spot      |
| anger_storm     | Failed WIL check = attack nearest target (friend/foe)  |
| killing_calm    | +5 combat rolls; -10 all social; loyalty loss -1/month |
| withdrawal      | -10 Command/Persuade targeting this character          |
| drink_need      | -5 all rolls when sober >12hrs; immune to fear drunk   |
| risk_seeking    | Ignores retreat/cover orders on failed WIL check       |
| grief_lock      | Cannot form new shield-bonds; -10 Morale contribution  |
| mind_flight     | Lose 1d6 minutes during trigger; -5 all concentration  |
| heavy_mind      | -5 all rolls; march speed -1 tier; no initiative acts  |

### 5.21 Trauma Triggers

Each condition has associated triggers — stimuli that activate the acute
response. Triggers are specific and tracked per condition.

#### Common Triggers (by Source Event)

| Source                   | Likely Triggers                                       |
| ------------------------ | ----------------------------------------------------- |
| Battle / combat wound    | Iron clang, war-cries, blood smell, sudden movement   |
| Shield-brother death     | Empty seat, the dead man's name, similar faces        |
| Horror-sight             | Corpses, fire (if burning), children, confined spaces |
| Betrayal                 | Oaths, promises, being left behind, locked doors      |
| Starvation / deprivation | Empty plates, food waste, cold, tight spaces          |
| First kill               | Blood on hands, knife-edge glint, the dying sound     |

#### Trigger Check

When a trigger is encountered, the character makes a **WIL check**:

```text
Target: 50 + (WIL × 5) + modifiers
Roll: d100
Success: The man endures. Visible tension but no breakdown.
Failure: Condition activates for 1d6 × 10 minutes (combat) or
         1d6 hours (non-combat). See condition-specific effects.
Critical failure: Condition activates at one severity worse.
                  +1 TSP added.
```

**Trigger check modifiers:**

| Factor                | Modifier |
| --------------------- | -------- |
| Shield-brother nearby | +10      |
| Dalla present         | +5       |
| At the fire (camp)    | +5       |
| Drunk (moderate)      | +5       |
| Drunk (heavy)         | -10      |
| Fatigued              | -10      |
| In pain (moderate+)   | -5       |
| Night / darkness      | -5       |
| Alone                 | -10      |

### 5.22 Trauma Recovery

Recovery is slow, non-linear, and not guaranteed. A man can improve,
plateau, or relapse. There are no medications and no therapy — only time,
conditions, and the band.

#### Recovery Stages

| Stage    | Duration            | Effect                                                         |
| -------- | ------------------- | -------------------------------------------------------------- |
| Acute    | 0–7 days            | Full condition severity; high TSP                              |
| Active   | 1–8 weeks           | Condition active; triggers frequent                            |
| Easing   | 2–12 weeks          | Severity drops one step; triggers less frequent (check 1/week) |
| Residual | Permanent or months | Mild trigger sensitivity remains; may flare under new stress   |
| Resolved | Permanent           | Condition removed; TSP reduced                                 |

#### Recovery Factors

Recovery advances when **recovery conditions** are met. Each day of met
conditions accumulates **recovery points (RP)**. Recovery thresholds by
severity:

| Severity  | RP to Advance Stage |
| --------- | ------------------- |
| Mild      | 14                  |
| Moderate  | 30                  |
| Severe    | 60                  |
| Crippling | 120                 |

**Daily recovery point generation:**

| Condition                         | RP/Day |
| --------------------------------- | ------ |
| Full rest, secure hall            | 3      |
| Field rest, safe camp             | 2      |
| Active duty, no combat            | 1      |
| Active duty, combat this week     | 0      |
| Meaningful work (non-combat task) | +1     |
| Shield-brother present            | +1     |
| Dalla's care (seiðr/herbs)        | +1     |
| Saga-told (their deeds retold)    | +1     |
| Fire inclusion (nightly)          | +0.5   |
| Trigger event this day            | -2     |
| New trauma this week              | -5     |
| Drunk (self-medicating)           | -1     |
| Isolation (by choice)             | -2     |

#### Recovery Check

When sufficient RP accumulates, the character makes a **WIL check** to
advance to the next recovery stage:

```text
Target: 40 + (WIL × 5) + recovery_modifiers
Roll: d100

Success: Advance to next recovery stage.
Failure: No advancement. RP resets to 75% of threshold.
Critical failure: Relapse — severity worsens by one step.
                  RP resets to zero.
Critical success: Advance two stages. TSP reduced by 2.
```

#### WIL Degradation from Trauma

Unresolved trauma erodes WIL over time:

| Duration Unresolved | WIL Effect                         |
| ------------------- | ---------------------------------- |
| < 30 days           | Temporary -1 WIL (recovers)        |
| 30–90 days          | Temporary -2 WIL (recovers slowly) |
| 90+ days            | Permanent -1 WIL per 90 days       |
| Crippling severity  | Permanent -1 WIL immediately       |

Temporary WIL recovers: 1 point per 14 days of resolved condition.
Permanent WIL loss does not recover.

### 5.23 Psychological Profile Fields

Each member's statblock includes a psychological profile that tracks
accumulated trauma, resilience status, and behavioral baseline:

```yaml
psychological_profile:
  tsp: 12
  stress_threshold: 15
  trauma_conditions:
    - id: "t_001"
      condition: "night_terrors"
      severity: "moderate"
      recovery_stage: "active"
      triggers: ["sudden_sounds", "iron_clang"]
  resilience_factors:
    shield_bond: "Kell Hook"
    belief_framework: "moderate"
    prior_recoveries: 1
    coping_method: "fire_and_drink"
  behavioral_baseline:
    speech_pattern: "terse_but_functional"
    sleep_quality: "poor"
    appetite: "reduced"
    social_engagement: "minimal"
    drinking_level: "moderate"
  will_damage:
    temporary: 0
    permanent: 1
  trauma_history:
    - event: "Hall fire that killed family"
      day: 0
      tsp_gained: 8
      conditions_produced: ["flinch_sickness"]
```

The profile is maintained alongside physical wound/scar records.
`condition_update` (§ 5.16) factors in active trauma conditions when
computing overall member state.

### 5.24 Trauma Subsystem Commands

All commands mutate member state and return result dicts. CLI interface
matches `wounds.py` conventions.

#### trauma_apply

Inflict a traumatic event. Adds TSP, checks for condition manifestation.

```yaml
command: trauma_apply
target: "Ubbe Ironside"
event: "Shield-brother Rolf killed beside him"
category: "shield_brother_death"
tsp: 8
day: 142
modifiers:
  shield_bond_active: false
  chronic_pain: true
```

**Process:**

1. Calculate effective TSP (base + modifiers).
2. Add TSP to member total.
3. If TSP > stress_threshold: select condition type based on
event category and character profile.
4. Set condition severity based on overshoot
(TSP - threshold): 0–3 = mild, 4–8 = moderate, 9–15 = severe, 16+ =
crippling.
5. Generate triggers from source event.
6. Update behavioral baseline.

#### trauma_trigger

Fire a trigger check. Resolves whether the condition activates and for how
long.

```yaml
command: trauma_trigger
target: "Ubbe Ironside"
trauma_id: "t_001"
trigger: "iron_clang"
context: "combat"
modifiers:
  shield_brother_nearby: true
  fatigued: false
```

#### trauma_recover

Advance recovery timeline by elapsed days and conditions.

```yaml
command: trauma_recover
target: "Ubbe Ironside"
trauma_id: "t_001"
days_elapsed: 7
conditions:
  rest_quality: "field_rest"
  meaningful_work: true
  shield_brother_present: false
  dalla_care: true
  fire_inclusion: true
  trigger_events_today: 0
  isolation: false
  drunk: false
```

#### trauma_worsen

Increase trauma severity (relapse, new trigger event, compound stress).

```yaml
command: trauma_worsen
target: "Ubbe Ironside"
trauma_id: "t_001"
new_severity: "severe"
cause: "Another companion killed. The old pattern returns."
tsp_added: 4
```

#### trauma_improve

Decrease trauma severity (successful recovery check, extraordinary event).

```yaml
command: trauma_improve
target: "Ubbe Ironside"
trauma_id: "t_001"
new_severity: "mild"
cause: "Winter quarters. Three months of secure rest."
```

#### trauma_resolve

Mark a trauma condition as resolved. May leave residual marker.

```yaml
command: trauma_resolve
target: "Ubbe Ironside"
trauma_id: "t_001"
residual: "Remains sensitive to sudden iron sounds. Flinch is
  gone but the man still turns his head."
tsp_reduction: 6
```

#### trauma_add_condition

Manually add a trauma condition (for backstory, for events outside normal
TSP flow).

```yaml
command: trauma_add_condition
target: "Thorne Ash-Born"
condition: "flinch_sickness"
severity: "mild"
source: "Backstory — hall fire"
triggers: ["open_flame", "smoke_smell", "screaming"]
```

#### profile_update

Recalculate full psychological profile from all active conditions, TSP, WIL
degradation, and resilience factors.

```yaml
command: profile_update
target: "Ubbe Ironside"
```

### 5.25 Trauma and Combat Integration

When `combat_sim.py` produces a kill, a wound, or a significant event, the
trauma subsystem checks for TSP accrual:

```python
# After combat resolution:
for fighter in all_fighters:
    tsp = 0
    if fighter.kills_this_fight > 0 and fighter.total_kills < 3:
        tsp += 2  # early kills carry more weight
    if fighter.saw_companion_die:
        tsp += 6  # shield-brother death
    elif fighter.saw_companion_wounded_critical:
        tsp += 3
    if fighter.hp <= fighter.max_hp * 0.25:
        tsp += 3  # nearly died
    if fighter.was_incapacitated:
        tsp += 2

    if tsp > 0:
        trauma_apply(member, event=combat_summary,
                     category=determine_category(fighter),
                     tsp=tsp, day=current_day)
```

Band-level events (Named Man death, atrocity, betrayal) trigger TSP for all
witnesses with appropriate modifiers.

### 5.26 Interaction with Physical Health

Psychological and physical damage compound:

| Physical State           | Trauma Effect                        |
| ------------------------ | ------------------------------------ |
| Chronic pain (any wound) | +1 TSP per event; -5 recovery checks |
| Wound-Addled (§ 5.15)    | +2 TSP per event; recovery RP halved |
| Active serious+ wound    | -1 RP/day recovery; trigger check -5 |
| Infection (active)       | +1 TSP per week of fever             |
| Recently amputated       | +6 TSP immediate; grief-lock risk    |

| Trauma State               | Physical Effect                         |
| -------------------------- | --------------------------------------- |
| Active moderate+ condition | Wound healing speed -25%                |
| Withdrawal (active)        | Wound treatment delayed (self-neglect)  |
| Drink-need (active)        | Infection risk +10% (poor self-care)    |
| Heavy-mindedness           | Rest quality one step worse             |
| Risk-seeking               | +50% chance of new wound per engagement |

---

## 6. Morale System

Band morale is tracked on a 1-5 scale. Computed by `morale.py`.

| Level | Name     | Effect                               |
| ----- | -------- | ------------------------------------ |
| 5     | Keen     | +5 all rolls, no desertion risk      |
| 4     | Steady   | No modifiers                         |
| 3     | Shaken   | -5 all rolls, minor desertion risk   |
| 2     | Wavering | -10 all rolls, active desertion risk |
| 1     | Broken   | -15 all rolls, band may scatter      |

### Morale Triggers (Checked Weekly)

| Event                          | Morale Change         |
| ------------------------------ | --------------------- |
| Won engagement, few casualties | +1                    |
| Paid on time                   | +1 (once per season)  |
| Secured winter hall            | +1                    |
| 20%+ casualties in engagement  | -1                    |
| Late payment (3+ days)         | -1                    |
| Captain broke oath/contract    | -2                    |
| Named Man killed               | -1                    |
| Atrocity with no plunder       | -1                    |
| Food deficit (3+ days)         | -1                    |
| The Hush (extended, 10+ min)   | -1 (superstition)     |
| Ward-stones intact at camp     | +1 (once, on arrival) |
| Ward-stones failed or absent   | -1                    |
| Galdr-worker performed rites   | +1 (once per season)  |
| Wyrd-reading favorable omen    | +1 (once per week)    |
| Wyrd-reading ill omen          | -1                    |
| Seiðr-wife confirmed dead rest | +1 (post-battle)      |
| Folk charm available to band   | stabilize (no drop)   |

### Folk Magic and Morale

Folk magic — household wards, herb-bundles, carved threshold runes — does
not produce mechanical magical effects. Its effect is on morale: men who
see familiar protective rituals performed feel safer, even when the rituals
do nothing measurable.

**Ward confidence:** When camp is made near intact ward-stones (settlement
or standalone), the band gains +1 morale (one-time, on arrival) as long as
the ward-stones are visibly maintained. If the ward-stones are cracked,
dark, or obviously failing, the morale bonus becomes -1 instead.

**Ritual comfort:** A galdr-worker who performs camp-warding rites (even
purely symbolic ones, below Rune-lore rank thresholds) stabilizes morale:
prevents any superstition-based morale drops for that week. This costs the
galdr-worker 1 Willpower.

**Omen dependency:** Repeated favorable wyrd-readings create omen
dependency: if the band receives 3+ consecutive favorable readings then a
negative one, the morale drop is -2 instead of -1. The men expected good
fortune and feel betrayed by fate.

See `08_MAGIC_OF_RIMEVEGR.md` §3 (Folk Magic: The Household Layer) for
narrative context.

### Grievance Resolution

Captain addresses grievances at fire (once per week). Uses Command or
Persuade check with difficulty based on grievance severity:

| Grievance Type         | Difficulty Modifier |
| ---------------------- | ------------------- |
| Late wages             | +0                  |
| Named Man killed       | +0                  |
| Broken oath            | -15                 |
| Atrocity w/o gain      | -15                 |
| Stacked (3+ same type) | additional -10      |

---

## 7. Logistics and Supply

### Food Consumption

```text
daily_food_units = band_size × 1.0 (Long Summer)
daily_food_units = band_size × 1.2 (Long Dark, 20% increase)
```

One food unit = one person-day of sustenance.

### Carrying Capacity

```text
carry_limit_kg = (Might × 5) + 10
```

Each fighter carries personal gear (3-8 kg) plus share of communal
supplies. Exceeding carry limit: -10 to all physical rolls, march speed
halved.

### March Speed

```text
base_speed = 25 km/day (clear terrain, Long Summer)

Terrain modifiers:
  Fjord coast path:  ×1.0
  Black Pine Wilds:  ×0.6
  High Rime-Moors:   ×0.7
  Frozen rivers:     ×0.8
  Mountain pass:     ×0.4

Weather modifiers:
  Clear Grey:       ×1.0
  Rime-Fog:         ×0.7
  Driving Snow:     ×0.5
  Rime Storm:       ×0.2

Season modifier:
  Long Summer:      ×1.0
  Long Dark:        ×0.8

Weak link penalty:  ×0.85 (if band has members with NIM < 3)

final_speed = base × terrain × weather × season × weak_link
```

### Weight Budget (Band Level)

Track total weight of: weapons, armor, food stores, trade goods, silver,
tools, and personal effects. A 14-person band typically carries 200-350 kg
total. Overweight slows march speed further.

---

## 8. Economy

### Currency

- 1 silver = 10 copper as the bookkeeping rate
- 1 gold = 10 silver by clean weight in contracts and treasury accounts
- 1 málsverðr = 1 copper as the everyday food-price anchor
- Typical daily wage for a laborer: 2 copper
- A week's food for one person: 1 silver
- Local daily life runs on copper, barter, and favors
- Outsider and professional services usually mix copper, food, and silver
- Military, legal, long-distance, and elite exchange uses weighed silver, sometimes gold

### Weekly Retainer Pay

| Rank                    | Weekly Pay                |
| ----------------------- | ------------------------- |
| Common fighter          | 2 silver                  |
| Veteran                 | 3 silver                  |
| Named Man               | 5 silver                  |
| Shield-maiden (veteran) | 3 silver                  |
| Captain                 | Takes from treasury share |

### Mission Pay (Daily, During Active Contracts)

| Rank           | Daily Pay         |
| -------------- | ----------------- |
| Common fighter | 5 copper          |
| Veteran        | 1 silver          |
| Named Man      | 1 silver 5 copper |

### Non-Payment Table (Checked When Wages Late)

Roll d100 when wages are 14+ days late on retainer or 3+ days late on
active mission:

| Roll   | Consequence                                                     |
| ------ | --------------------------------------------------------------- |
| 01-15  | D3 unhappy men desert at night. May sell information            |
| 16-30  | Named Man demands written debt acknowledgment                   |
| 31-50  | Band becomes Shaken for the week (-5 to all)                    |
| 51-70  | Sergeant confronts captain publicly. Command check or Morale -1 |
| 71-85  | Quiet muttering. No immediate effect this week                  |
| 86-100 | Men accept for now. Next non-payment rolls twice                |

### Loot Division by Band Archetype

| Archetype          | Captain | Named Men | Veterans | Commons |
| ------------------ | ------- | --------- | -------- | ------- |
| Tyrant Hird        | 60%     | 20%       | 12%      | 8%      |
| Standard Svarthird | 40%     | 25%       | 20%      | 15%     |
| Fraternal Band     | 25%     | 25%       | 25%      | 25%     |
| Kin-Clan           | 20%     | 20%       | 25%      | 35%     |

---

## 9. Foraging

Resolved by `foraging.py`. Output = food units per day.

### Base Output by Terrain

| Terrain              | 1-2 Foragers | 3-5 | 6-10 | 11+ |
| -------------------- | ------------ | --- | ---- | --- |
| Inner Fjords / Coast | 4            | 10  | 18   | 30  |
| Black Pine Wilds     | 3            | 8   | 16   | 28  |
| High Rime-Moors      | 1            | 3   | 7    | 12  |
| Frozen Rivers / Ice  | 0            | 2   | 4    | 8   |

### Season Penalty

- Long Summer: no penalty
- Long Dark: output reduced by 30% (multiply by 0.7)

### Weather Penalty

- Rime-Fog: output reduced by 20%
- Driving Snow: output reduced by 50%
- Rime Storm: foraging impossible

### Forager Skill Bonus

Average Forage skill of assigned foragers adds percentage bonus:

```text
skill_bonus = average_forage_skill × 8%
final_output = base × season_mod × weather_mod × (1 + skill_bonus)
```

---

## 10. Weather Generation

Resolved by `weather.py`. Checked daily.

### Long Summer Weather Table (d100)

| Roll  | Weather       | Duration             |
| ----- | ------------- | -------------------- |
| 01-40 | Clear Grey    | 1-3 days             |
| 41-70 | Rime-Fog      | 1-2 days             |
| 71-85 | Light rain    | 1 day                |
| 86-95 | Driving Snow  | 1 day                |
| 96-99 | The Hush      | 1-10 minutes (event) |
| 100   | Veil-Thinning | 1 night (omen event) |

### Long Dark Weather Table (d100)

| Roll  | Weather       | Duration             |
| ----- | ------------- | -------------------- |
| 01-20 | Clear Grey    | 1-2 days             |
| 21-50 | Rime-Fog      | 1-3 days             |
| 51-75 | Driving Snow  | 1-3 days             |
| 76-90 | Rime Storm    | 1-2 days             |
| 91-97 | The Hush      | 1-30 minutes (event) |
| 98-99 | Veil-Thinning | 1 night (omen event) |
| 100   | Blood Sun     | 1 day (terror event) |

### Frostbite Risk

Per day in Driving Snow or Rime Storm without shelter:

```text
frostbite_chance = 15% + (10% × days_exposed) - (Toughness × 2%)
# Modified by: +10% if no proper cloak, +15% if wounded
```

---

## 11. Norse Magic System

Magic is rare, feared, and always costs something. Only characters with
Wyrd 3+ can reliably attempt magical actions. Three traditions:

### Galdr (Rune Scribing)

Carving runes and speaking words of power. The most accepted form of magic,
though still viewed with suspicion.

**Mechanic:**

```text
galdr_chance = (Wyrd × 5) + (Rune-lore × 10) + 15 + modifiers
```

**Effects by Rune-lore Rank:**

| Rank | Capability                                                                  |
| ---- | --------------------------------------------------------------------------- |
| 1    | Read and identify rune-stones. Simple wards (one night).                    |
| 2    | Carve minor runes: mark a trail, strengthen a weapon (+1 dmg, 1 day).       |
| 3    | Bind runes: ward a camp overnight, compel a bleeding rune-stone to speak.   |
| 4    | Powerful runes: curse a weapon, seal a barrow entrance, reveal hidden text. |
| 5    | Master galdr: call down fog, break an ancient seal, inscribe fate.          |

**Cost of Galdr:**

- Rank 1-2 effects: 1 Willpower + 1-2 stamina (tiring but not yet
life-burning)
- Rank 3 effects: 2 Willpower + 4 stamina + blood equal to the greater of 3
HP or 10% of Max HP (rounded up)
- Rank 4 effects: 3 Willpower + 6 stamina + blood equal to the greater of 6
HP or 22% of Max HP (rounded up) + material component
- Rank 5 effects: 5 Willpower + 8 stamina + blood equal to the greater of 9
HP or 33% of Max HP (rounded up) + rare material
- These costs are paid on success or failure. Galdr is not a free spell
slot; it is exertion, blood loss, and shortened life.

**Typical working example:** a competent galdr-worker with 25 Max HP and 23
Max Stamina pays about 3 HP and 4 stamina for rank 3 work, 6 HP and 6
stamina for rank 4 work, and 9 HP and 8 stamina for rank 5 work.

**Failure Consequences (d100 on failed galdr):**

| Roll   | Consequence                                                  |
| ------ | ------------------------------------------------------------ |
| 01-40  | Rune fizzles. Willpower cost still paid.                     |
| 41-70  | Backlash: 1d6 damage to carver, rune cracks.                 |
| 71-90  | Rune inverts: opposite of intended effect.                   |
| 91-100 | Something notices. The Hush falls. Wyrd check or gain dread. |

### Seiðr (Spirit Talking)

Communion with the dead, land-spirits, and hidden presences. Deeply
stigmatized for men (considered ergi / unmanly). Women practitioners
(völvur) are feared but respected.

**Mechanic:**

```text
seidr_chance = (Wyrd × 5) + (Spirit-lore × 10) + 10 + modifiers
# Note: base is +10 not +15 (seiðr is harder than galdr)
```

**Effects by Spirit-lore Rank:**

| Rank | Capability                                               |
| ---- | -------------------------------------------------------- |
| 1    | Sense if spirits are nearby. Identify a haunting.        |
| 2    | Speak with fresh dead (within 3 days). Ask 1 question.   |
| 3    | Commune with land-spirits. Negotiate passage or shelter. |
| 4    | Command lesser dead. Bind a spirit to guard a location.  |
| 5    | Walk between worlds briefly. Speak with ancient dead.    |

**Cost of Seiðr:**

- Always costs 2+ Willpower
- Rank 3+ requires a trance state (1 hour, vulnerable)
- Rank 4+ costs blood and sanity (permanent Wits reduction risk)
- Social cost: if seen performing seiðr, male practitioners lose standing

### Wyrd-Reading (Fate Divination)

Casting lots, reading entrails, interpreting omens. The most common and
least stigmatized form of supernatural practice.

**Mechanic:**

```text
wyrd_chance = (Wyrd × 5) + (Wyrd-reading × 10) + 15 + modifiers
```

**Effects by Wyrd-reading Rank:**

| Rank | Capability                                                    |
| ---- | ------------------------------------------------------------- |
| 1    | Sense general fortune (good/bad omen for the day).            |
| 2    | Cast lots for a specific question (yes/no, cryptic).          |
| 3    | Read the wyrd of a person (hidden loyalties, sickness).       |
| 4    | Foresee danger (ambush warning, storm coming, betrayal).      |
| 5    | See the threads of fate. Reveal hidden events. Always costly. |

**Cost of Wyrd-Reading:**

- Rank 1-2: mental fatigue only (temporary -1 Wits)
- Rank 3+: the knowledge always comes with dread or obsession
- Rank 5: permanent Wyrd increase but permanent Will decrease
- The future shown is always true but never complete

### 11.8 Political Magic Integration

Where Section 11 defines what magic can do and Section 18 defines how
politics works, this section governs the intersection: how magical practice
creates, distorts, and arbitrates political power at the ting and Allthing.

#### 11.8.1 Ward-Rights at the Allthing

Ward-right is a political appointment determining which union's
galdr-worker wards the Allthing stones for the assembly's duration. The
ward-holder controls magical safety for all participants.

**Appointment:** Resolved on Allthing Day 1 (see 18.10), before any other
Allthing actions are taken.

**Ward Influence Formula:**

```text
ward_influence = band_reputation × 2
               + galdr_worker_rune_lore × 5
               + overjarl_favor
# overjarl_favor = 0-3, set by narrative state
# galdr_worker_rune_lore = Rune-lore rank of nominated worker
```

**Resolution:**

1. Each union nominates one galdr-worker from its members.
2. The nomination with the highest `ward_influence` wins.
3. Ties broken by highest `galdr_worker_rune_lore`, then by
lot (d100, high wins).

**Effects of Holding Ward-Right:**

- Ward-holding union gains **+1 modifier** to all Allthing
action rolls (see 18.10 Allthing Actions table).
- Other unions may challenge the appointment. Challenge
requires a Persuade check: `challenge_chance = (Wits × 5) + (Persuade × 10)
+ 15` DC = `ward_influence` of current holder. On success, the challenger's
nomination replaces the holder.

**Ward Sabotage (requires Dark Arts level 3+):**

- Sabotaging union rolls against the ward:
`sabotage_chance = dark_arts_level × 15 + saboteur_rune_lore × 10`
- If `sabotage_chance` roll succeeds: wards collapse. All
Allthing action rolls take a **-2 modifier** for the remainder of the
assembly. Sabotaging union gains **+2** to `intel_chance` (see 18.10).
- If sabotage is detected (opposing galdr-worker rolls
`galdr_chance` per Section 11): sabotaging union loses 1 reputation
(Section 13) and ward-holding union gains +1 to all remaining rolls for the
session.

#### 11.8.2 Seiðr Testimony Rules

Whether seiðr testimony — a völva's report of what the dead or spirits
reveal — is admissible at a ting or the Allthing varies by union law.

**Admissibility by Union:**

| Union                   | Seiðr Testimony | Conditions                      |
| ----------------------- | --------------- | ------------------------------- |
| Iron Grip               | Forbidden       | Dead men don't vote             |
| Fjord Compact           | Allowed         | Must be witnessed by 2+ freemen |
| Whispering Circle       | Required        | All major decisions use seiðr   |
| Independent settlements | Varies          | Headman decides per case        |

**Testimony Weight Formula (when allowed):**

```text
testimony_weight = seidr_worker_wyrd × 3 + spirit_lore × 5
# seidr_worker_wyrd = Wyrd attribute of the testifying worker
# spirit_lore = Spirit-lore rank of the testifying worker
```

**Testimony Weight Thresholds:**

| Weight | Classification      | Effect on Dispute Resolution   |
| ------ | ------------------- | ------------------------------ |
| 31+    | Compelling evidence | +3 modifier to supported party |
| 15-30  | Supporting evidence | +1 modifier to supported party |
| 0-14   | Hearsay             | Ignored. No mechanical effect. |

**Counter — Living Witness Challenge:**

Any party to a dispute may invoke "living witness over dead witness,"
demanding that testimony from living freemen overrule seiðr testimony.
Invoking this costs the challenger **1 reputation** (Section 13). If
invoked, seiðr testimony weight is halved (round down) for that dispute
only.

#### 11.8.3 Curse Arbitration

When a jarl deploys a niding-pole (see galdr Rank 4, Section 11) against
another and the target brings the matter to the ting, the ting must rule on
the curse's legitimacy.

**Curse Legitimacy Formula:**

```text
curse_legitimacy = carver_rune_lore × 5
                 + grievance_severity × 10
                 - defender_reputation × 3
# carver_rune_lore = Rune-lore rank of the curse-carver
# grievance_severity = 1-5, assessed by ting (see below)
# defender_reputation = reputation (Section 13) of target
```

**Grievance Severity Scale:**

| Severity | Example Grievance                              |
| -------- | ---------------------------------------------- |
| 1        | Insult, broken minor oath                      |
| 2        | Unpaid debt, trespass on land                  |
| 3        | Theft, broken contract (Section 13)            |
| 4        | Kinslaying of a thrall or freedman             |
| 5        | Murder of a freeman, oath-breaking before ting |

**Legitimacy Outcomes:**

| Score | Ruling                                                                                   |
| ----- | ---------------------------------------------------------------------------------------- |
| 51+   | Curse stands. Target must resolve the grievance or accept the curse's effects.           |
| 25-50 | Compromise imposed. Both parties lose 1 reputation (Section 13).                         |
| 0-24  | Curse removed. Carver branded niding. Carver loses 2 reputation. Feud +1 (Section 18.6). |

**Blood-Galdr Exception:**

If the curse used blood-galdr (another person's blood as material
component): automatic niding ruling regardless of `curse_legitimacy` score.
Carver declared outlaw. Feud +3 (Section 18.6) between carver's settlement
and target's settlement. Dark Arts level of carver's union increases by 1
(Section 18.9).

#### 11.8.4 Dark Arts Definitions and Boundaries

This section provides precise mechanical classification of magical
practices referenced by Sections 11, 18.9, and 18.10.

**Practice Classification Table:**

| Practice                       | Class         | Consequence if Discovered                             |
| ------------------------------ | ------------- | ----------------------------------------------------- |
| Standard galdr (own blood/mat) | Legal         | None                                                  |
| Defensive wards (walls, doors) | Legal         | None                                                  |
| Seiðr consultation (private)   | Tolerated     | Social stigma (male workers)                          |
| Seiðr testimony at ting        | Union-dep.    | Per 11.8.2                                            |
| Niding-pole (valid grievance)  | Legal         | Per 11.8.3                                            |
| Blood-galdr (another's blood)  | **Forbidden** | Outlawry, -3 reputation                               |
| Death-seiðr (compelling dead)  | **Forbidden** | Outlawry, -3 rep., feud +2                            |
| Veil-thinning (intentional)    | **Forbidden** | Settlement panic, feud +3 all neighboring settlements |
| Invocation (Veil entities)     | **Forbidden** | Dark Arts consequences (18.9)                         |

**The Counsel-Coercion Boundary:**

The mechanical line between legal seiðr consultation and forbidden
death-seiðr is determined by the Spirit-lore rank used:

- **Rank 1-3 effects** (sense, speak, commune): the dead are
asked. This is counsel. Legal or tolerated.
- **Rank 4+ effects** (command, bind): the dead are compelled.
This is coercion. Classified as death-seiðr (forbidden).

**Proving Dark Arts Accusations at the Allthing:**

Any Dark Arts accusation raised at the Allthing (Section 18.10) requires
proof. Proof requires a seiðr-worker willing to testify under the rules of
11.8.2. The accusing union must produce a seiðr-worker whose
`testimony_weight` (per 11.8.2) meets the Compelling threshold (31+).

This creates a structural dependency: proving forbidden magic requires the
very tradition the accusation targets. Unions that forbid seiðr testimony
(Iron Grip) cannot bring Dark Arts accusations without first securing a
seiðr-worker from another union — a political transaction with its own
costs.

**Accusation Resolution:**

```text
accusation_chance = accuser_testimony_weight
                  + evidence_quality × 5
                  - accused_reputation × 3
                  - accused_dark_arts_concealment × 10
# evidence_quality = 0-5 (physical evidence, witnesses)
# dark_arts_concealment = 0-3 (Whispering Circle starts at 2)
```

| Score | Outcome                                                            |
| ----- | ------------------------------------------------------------------ |
| 41+   | Accused convicted. Consequences per table above                    |
| 20-40 | Inconclusive. Accused gains feud +1 with accuser. No punishment.   |
| 0-19  | Accusation fails. Accuser loses 1 reputation for false accusation. |

### 11.9 Practitioner Degradation Tracking

Magical practice extracts a cumulative physical toll. This section tracks
when practitioners begin to lose capability due to years of use.
Degradation is tracked per practitioner, not per tradition.

**Degradation Onset:**

| Tradition    | Active Years Before Onset | Onset Trigger                 |
| ------------ | ------------------------- | ----------------------------- |
| Galdr        | 15-20 years               | Hands lose fine motor control |
| Seiðr        | 10-15 years               | Trance recovery lengthens     |
| Wyrd-reading | 20-25 years               | Readings become incoherent    |

**Degradation Formula:**

```text
degradation_chance = years_active × 3 + total_willpower_spent × 0.5
                   - (Toughness × 2) - (Will × 2)
# Checked annually. If degradation_chance > 50, onset begins.
# After onset: effective skill rank drops by 1 every 3-5 years.
```

**Degradation Effects:**

| Stage    | Mechanical Effect                                 |
| -------- | ------------------------------------------------- |
| Onset    | -5 to all magic rolls. Physical symptoms appear.  |
| Early    | Effective rank -1. Cost per use +1 Willpower.     |
| Mid      | Effective rank -2. Trance/carving time doubles.   |
| Late     | Effective rank -3. 10% chance of failure per use. |
| Terminal | Cannot perform. Knowledge remains, hands do not.  |

**Physical Markers by Tradition:**

- **Galdr:** Hands tremble, fingers stiffen, inscription lines waver.
Old rune-carvers cannot hold a chisel steady in cold weather.
- **Seiðr:** Trance recovery extends from hours to days. Memory gaps
after sessions. Confusion between spirit-speech and waking speech.
- **Wyrd:** Readings blur — the lots say too much or nothing at all.
The reader cannot distinguish signal from noise.

**Named Character Degradation Status:**

| Practitioner        | Tradition    | Stage     | Notes              |
| ------------------- | ------------ | --------- | ------------------ |
| Ash (Black Axes)    | Galdr        | Pre-onset | ~10 years active   |
| Dalla (Black Axes)  | Seiðr        | Pre-onset | ~8 years active    |
| Petra (Black Axes)  | Wyrd-reading | Pre-onset | ~5 years active    |
| Thorne (Black Axes) | Galdr (life) | Pre-onset | Rune craft only    |
| Audun (Skaldhaven)  | Galdr        | Early     | Hands declining    |
| Ragnhild (Icebreak) | Seiðr        | Mid       | Trance recovery 2d |

See `08_MAGIC_OF_RIMEVEGR.md` §8 (Practitioner Lifecycle) for full
narrative context and `data/magic/practitioners.yaml` for canonical
practitioner data.

### 11.10 Rune-Script Construction Rules

This section governs galdr rune-scribing: how scripts are built, how many
runes can be combined, how the voice (kvæði) modifies the effect, and how
rune-blight accumulates. Used by `galdr_simulation.py`.

#### 11.10.1 Script Size Limits

| Rune Count | Rank Required | Kvæði Duration | Base Difficulty |
| ---------- | ------------- | -------------- | --------------- |
| 3          | 1+            | 2-5 minutes    | +0              |
| 5          | 3+            | 10-20 minutes  | +15             |
| 7          | 4+            | 20-40 minutes  | +30             |
| 9          | 5             | 1-3 hours      | +50             |

**Script construction formula:**

```text
script_chance = galdr_chance - base_difficulty - face_modifier
              - material_modifier - environmental_modifier
# galdr_chance from Section 11 base formula
# face_modifier: 0 for dagmál, +15 for náttmál
# material_modifier: stone +0, bone +5, wood -5, iron +10
# environmental_modifier: daylight -5, Long Dark +5,
#   near Veil-thinning +15
```

#### 11.10.2 Dagmál vs Náttmál Resolution

The face (dagmál or náttmál) is determined by carver intent plus
environmental pressure:

```text
face_drift_chance = veil_proximity × 10
                  + emotional_state_modifier
                  + blight_stage × 15
                  - (Will × 3)
# veil_proximity: 0 (none), 1 (distant), 2 (near), 3 (active)
# emotional_state_modifier: calm 0, angry +10, grief +15,
#   flat/Veil-touched +20
# blight_stage: 0-5 per 11.10.5
```

If `face_drift_chance > 50`, the rune defaults to náttmál regardless of
carver intent. The carver may force dagmál with a Will check:

```text
force_dagmal = (Will × 5) + 15 - face_drift_chance
# Success: rune stays dagmál
# Failure: rune goes náttmál, carver takes 1 Willpower damage
```

#### 11.10.3 Rune Combination Grammar

Each rune in a script must fill one of these grammatical slots:

| Slot        | Role                     | Examples               |
| ----------- | ------------------------ | ---------------------- |
| Subject     | What/who the script acts | Fé, Maður, Yr, Steinn  |
| Force       | The action or quality    | Kaun, Móðr, Nauð, Úr   |
| Consequence | The intended outcome     | Nið, Elgur, Vend, Ár   |
| Modifier    | Scope, timing, location  | Reið, Mórk, Vetr, Hlið |
| Amplifier   | Intensity boost          | Blóð, Hagall, Sól      |

**Grammar validation rules:**

- A 3-rune script must have Subject + Force + Consequence.
- A 5-rune script adds 1 Modifier and 1 Amplifier.
- A 7-rune script adds 2 Modifiers and 2 Amplifiers.
- A 9-rune script fills all slots and may double one.
- Duplicate runes in a script are forbidden (backlash
automatic).
- A rune may fill multiple slots if its meaning supports both
(e.g., Kaun as Force and Consequence). This costs +5 difficulty per
dual-slotted rune.

#### 11.10.4 Kvæði (Voice-Chant) Modifiers

The spoken chant modifies the script's effectiveness, but it now also
drains the body that carries it:

```text
kvaedi_bonus = kvaedi_quality × 5 + harmonic_bonus
# kvaedi_quality: 0 (mumbled), 1 (spoken), 2 (chanted),
#   3 (throat-sung), 4 (full galdr-voice)
# harmonic_bonus: +5 per additional singer (max 3 additional)
```

**Chant maintenance strain:**

```text
chant_stamina_drain = max(1, rank + max(0, kvaedi_quality - 1))
# Check once per active chant interval:
# - short carvings: every 5 minutes
# - long workings: every 10 minutes
# - combat singing / maintained warding: every round or scene
```

**Thresholds for dark singing:**

- Above 25% Max Stamina: the voice remains controlled.
- At or below 25% Max Stamina: the black-tongue threshold is reached. The
narrative effects of singing unlock even on a successful working — voices
deepen, listeners become uneasy, animals balk, and the carver takes -10 to
calm social interaction until properly rested.
- Below 0 stamina: every negative stamina point immediately costs 1 HP.
This always unlocks the dark effects of singing.
- If HP reaches 0 while the galdr-worker is still singing, the result is
**Divine Stroke** rather than ordinary collapse.

**Group galdr risks:**

```text
group_overflow_chance = (singer_count - 1) × 15
                      + kvaedi_quality × 5
# If group_overflow_chance > 40: all non-singers in earshot
#   roll Will check or suffer galdr overflow effects
```

**Galdr overflow effects (failed Will check by listeners):**

| d100  | Effect                                                                                           |
| ----- | ------------------------------------------------------------------------------------------------ |
| 01-25 | Dark emotional resonance. -1 Wits for 1d6 hours.                                                 |
| 26-45 | Compulsive humming. Cannot stop until galdr ends.                                                |
| 46-60 | Physical arousal. Social -2 for scene. No save.                                                  |
| 61-75 | Numbness. -1 to all physical skill checks, 1d6 hrs.                                              |
| 76-90 | Blood pressure surge. 1d4 HP damage, headache 24 hrs.                                            |
| 91-99 | Guðslag warning. 2d6 HP, permanent -1 Toughness.                                                 |
| 100   | Divine stroke. Save vs death (Toughness × 5 + Will × 3). Failure: death or permanent disability. |

#### 11.10.5 Rune-Blight Accumulation

Blight tracks cumulative rune damage to the galdr-worker. It is a
persistent value, not a per-session cost.

```text
blight_gain = overreach_count × 2
            + nattmal_uses × 1
            + failed_galdr_backlashes × 3
            + forced_rune_overrides × 5
# overreach_count: scripts above current rank
# nattmal_uses: intentional náttmál carvings
# failed_galdr_backlashes: results 41-100 on failure table
# forced_rune_overrides: fighting the rune's shape (see 08)
```

**Blight stage thresholds:**

| Blight Total | Stage | Effect                                                                                                                                                |
| ------------ | ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0-15         | 0     | Normal. Standard galdr costs.                                                                                                                         |
| 16-30        | 1     | Tremor. -5 galdr checks. +10 failure shift.                                                                                                           |
| 31-50        | 2     | Echo. Will check per carving or drift to náttmál. Dark-face whispers audible.                                                                         |
| 51-75        | 3     | Mark. Rune-lines visible on body. Env effects (blue fire, metal drift). -10 galdr.                                                                    |
| 76-100       | 4     | Speaking. Second voice. Constant low-level overflow. Living with worker costs 1 Wits per month to household members.                                  |
| 101+         | 5     | Terminal. Body becomes active rune-stone. 50-pace radius of Veil-thinning and galdr overflow. Cannot be stopped. Settlement must resolve or evacuate. |

**Blight reduction:**

```text
blight_recovery = rest_months × 2 + healer_seidr_rank × 3
                - blight_stage × 5
# rest_months: consecutive months with zero galdr use
# healer_seidr_rank: seiðr-worker's Spirit-lore rank
# Cannot reduce below (blight_stage × 5) — permanent floor
```

#### 11.10.6 Bind-Rune Construction

Bind-runes are permanent compound runes. Different rules from scripts.

```text
bind_chance = galdr_chance - (rune_count × 10) - material_mod
            + (crafting_hours × 2)
# rune_count: number of runes overlaid (2-4 typical)
# material_mod: per 11.10.1
# crafting_hours: time invested (min 4, max 48)
```

**Bind-rune durability:**

```text
durability_years = (galdr_worker_rune_lore × 5)
                 + material_base
                 - veil_exposure_modifier
# material_base: stone 50, iron 30, bone 20, wood 10
# veil_exposure_modifier: per 11.10.2 veil_proximity × 5
```

**Standing protection reserve tax:**

Permanent protections are not free once carved. While a protection remains
active, the galdr-worker loses Max HP equal to that protection's rank.

```text
protection_tax = protection_rank
current_effective_max_hp = base_max_hp - sum(active_protection_ranks)
```

- A rank 3 village ward costs -3 Max HP while it stands.
- A rank 4 perimeter or mine-ward costs -4 Max HP while it stands.
- A rank 5 great barrier or ancient seal costs -5 Max HP while it stands.
- These taxes stack. Galdr-workers maintaining multiple village protections
become visibly sickly, weak, and hard to mistake for healthy men.
- If total reserve tax reaches 25% or more of base Max HP, the practitioner
counts as physically drawn even when unwounded.
- When a protection is destroyed, exhausted, or removed, its Max HP tax
lifts immediately. The galdr-worker feels the rupture at once and knows a
ward has been lost somewhere, but not which one without investigation.

**Bind-rune failure (d100 on failed bind attempt):**

| Roll   | Consequence                                                                                           |
| ------ | ----------------------------------------------------------------------------------------------------- |
| 01-30  | Fizzle. Materials wasted. Willpower cost paid.                                                        |
| 31-60  | Partial bind. 1 rune activates, others inert.                                                         |
| 61-80  | Inverted bind. All runes activate in náttmál.                                                         |
| 81-95  | Backlash. 2d6 damage, +3 blight.                                                                      |
| 96-100 | Catastrophic. Bind explodes. 4d6 damage radius 10ft. All runes activate simultaneously, uncontrolled. |

#### 11.10.7 Soulbane Interaction Table

When a galdr-worker has undergone one or more soulbanes (see Chapter 14 /
`08_MAGIC_OF_RIMEVEGR.md` Rune-Blight section):

| Soulbane               | Soul Killed | Galdr Effect                                                                                 |
| ---------------------- | ----------- | -------------------------------------------------------------------------------------------- |
| Mannát (Eating)        | Hugr        | All galdr defaults náttmál. face_drift_chance always > 50. Blight gain per working × 2.      |
| Dýrríða (Riding)       | Hamr        | Speaking (Stage 4) immediate. No barrier between rune and body. Blight gain per working × 3. |
| Villimennska (Wilding) | Fylgja      | Galdr ceases to function. All galdr_chance = 0. Runes do not glow. Permanent.                |

---

## 12. Named Man Loyalty System

Computed by `morale.py` alongside band morale.

### Loyalty Scale (1-5)

| Level | Meaning                                           |
| ----- | ------------------------------------------------- |
| 5     | Blood-bound. Will die for the band.               |
| 4     | Personally invested. Reliable under pressure.     |
| 3     | Professional. Does the job, watches for problems. |
| 2     | Discontented. Watching for the exit.              |
| 1     | Ready to leave, betray, or act against the band.  |

### Loyalty Triggers

Each Named Man has a personal Trigger. When it fires:

```text
loyalty_check_chance = (Captain's Will × 5) + (Command × 10) + 15
                     + morale_modifier + relationship_modifier
```

Failure drops Named Man's loyalty by 1.

### Agenda Progress

Moving the band toward a Named Man's personal Agenda: +1 loyalty. Ignoring
it for 30+ days: -1 loyalty per month.

---

## 13. Contracts and Reputation

### Reputation Scale (0-5)

| Level | Name           | Effect                                           |
| ----- | -------------- | ------------------------------------------------ |
| 0     | Unknown        | Only desperate employers offer work              |
| 1     | Known          | Basic escort and guard contracts available       |
| 2     | Respected      | Standard contracts; settlements negotiate fairly |
| 3     | Feared/Admired | Choice contracts; jarls seek you out             |
| 4     | Legendary      | Can demand premium pay; rivals avoid you         |
| 5     | Mythic         | Shape regional politics; all doors open          |

### Contract Generation

Contracts available depend on reputation, location, season, and current
political conditions. Generated by `contracts.py`.

### Feud Track (0-4)

Tracked per settlement or faction. Increased by tribute, atrocity, broken
contracts. Decreased by time, weregild payment, or service.

| Level | Name       | Effect                              |
| ----- | ---------- | ----------------------------------- |
| 0     | Cold       | No active hostility                 |
| 1     | Tense      | Prices +20%, information restricted |
| 2     | Hostile    | Gates closed, ambush risk           |
| 3     | Blood-feud | Active hunting, bounties posted     |
| 4     | Vengeance  | Full war, no quarter                |

---

## 14. Calendar and Time

One year = 360 days (12 months × 30 days).

- Long Summer: Days 1-60 (Months 1-2: Frostwake, Rimeblood)
- Long Dark: Days 61-360 (Months 3-12)

Key time costs:

| Activity                      | Time Cost         |
| ----------------------------- | ----------------- |
| Full day march                | 1 day             |
| Foraging (full)               | 1 quarter-day     |
| Barrow clearing               | 1-3 days          |
| Settlement recruitment search | 1 quarter-day     |
| Heal (treat wounds)           | 1 quarter-day     |
| Galdr (rune carving)          | 1-4 hours         |
| Seiðr (spirit communion)      | 1+ hours (trance) |
| Wyrd-reading                  | 10-30 minutes     |
| Pay ritual                    | 1 hour            |
| Camp setup                    | 2 hours           |

---

## 15. Character Generation (NPCs and Recruits)

### Quick NPC Generation

```text
1. Determine background: farmer, fisher, thrall, huscarl, wanderer, outlaw
2. Assign attributes:
   - Base 5 for all
   - Add +1d4 to primary attribute (by background)
   - Subtract -1d3 from weakest attribute
   - Wyrd: 1 (90%), 2 (7%), 3 (2.5%), 4+ (0.5%)
3. Assign skills: 1-3 skills at rank 1-2 based on background
4. Generate: name, physical description, one personality trait
5. For Named Men: add Trigger, Agenda, starting Loyalty
```

### Recruit Quality by Settlement Size

| Settlement    | Pool Size    | Average Quality            |
| ------------- | ------------ | -------------------------- |
| Hamlet        | 1d4 recruits | Mostly common (1-2 skills) |
| Village       | 2d4 recruits | Mix of common and trained  |
| Large Village | 2d6 recruits | Some veterans available    |
| Small Town    | 3d6 recruits | Veterans and specialists   |

---

## 16. Hidden Information Protocol

All secret information is encoded in CJK characters using
`scripts/spoiler_codec.py` before being written to any public-facing file.

### What Gets Encoded

- Future events from the calendar
- Named Men betrayal plans and secret agendas
- NPC hidden motivations
- Rival band movements and plans
- Wyrd-reading results not yet revealed in narrative
- Contact network secrets
- Campaign arc progression triggers

### Storage Location

Hidden data is stored in `data/hidden/` as `.txt` files containing
CJK-encoded text. Decode as needed during narrative development or play.

### Protocol

1. AI determines secret information during simulation
2. AI runs: `python hidden_info.py encode "<secret text>"`
3. AI writes encoded output to appropriate hidden data file
4. During play, AI runs: `python hidden_info.py decode "<chinese text>"`
5. AI uses decoded information to inform narration without revealing source

---

## 17. Life Skills and Practical Knowledge

Every member of the band carries a baseline of practical knowledge — the
ambient competence of people who survive outdoors, fight, and travel for a
living. This section defines what characters can plausibly do without a
skill check, what requires a check, and what specialist knowledge
individual members carry beyond the baseline.

### Every Man Baseline (No Check Required)

Any band member can do these in normal conditions. Checks only apply under
extreme stress, injury, or hostile conditions:

- Light a fire in dry conditions (wet/wind: Shelter check).
- Sharpen his own weapons and perform basic maintenance.
- Dress a wound with cloth and pressure (anything beyond
first aid: Heal check).
- Tie functional knots (rigging, loads, snares).
- Set a basic camp (shelter, fire, latrine placement).
- Read weather within the next six hours (beyond six hours:
Weather-sense check).
- Cook meat over fire without poisoning himself.
- Fix a torn seam or a split boot (anything structural:
Leatherwork or Craft check).
- Navigate by sun and pole star in clear conditions
(overcast/forest: Navigate check).
- Estimate distance and time of travel on known terrain.

### Specialist Knowledge

Beyond the baseline, individual members carry deep knowledge in their
domains. This knowledge is tracked per-character in
`22_MEMBER_STATBLOCKS.md` under the `Life Skills` field.

Specialist knowledge determines what a character can do _competently_
without a check, or with advantage on the check. It also determines what
they notice automatically — the cook spots spoiled grain, the tracker reads
a three-day-old trail, the quartermaster detects short-weight goods.

**Mapping to simulation skills:**

| Specialist Domain | Governed By            | Example Characters   |
| ----------------- | ---------------------- | -------------------- |
| Cooking/Healing   | Heal, Forage           | Dalla                |
| Hunting/Tracking  | Track, Forage          | Thorne, Petra        |
| Quartermastery    | Bargain, Weather-sense | Gest                 |
| Rune Craft        | Rune-lore              | Thorne               |
| Woodcraft         | Woodcraft, Shelter     | Any with Shelter 2+  |
| Trapping          | Forage, Track          | Any with Forage 2+   |
| Seamanship        | Seamanship             | Any with Seamanship  |
| Trading           | Bargain, Sagas         | Gest, any Bargain 2+ |
| War Leadership    | Command, Shields       | Voss, Petra          |
| Scouting          | Track, Navigate        | Thorne               |
| Brewing/Chemistry | Forage, Heal           | Dalla                |

### When to Check vs. When to Narrate

- **No check:** Baseline actions in normal conditions. Specialist
actions within the character's domain under normal conditions.
- **Standard check:** Baseline actions under stress. Specialist
actions under hostile conditions.
- **Hard check:** Actions outside a character's domain. Specialist
actions under extreme conditions (blizzard, combat, injury).
- **Impossible without specialist:** Some actions require specialist
knowledge. An untrained man cannot set a bone, read runes, or navigate by
stars in overcast. He can try, but the check is penalized and failure has
consequences.

---

## 18. Political Simulation (Village Networks)

Resolved by `village_politics.py`. Simulates the political landscape of
Rimevegr settlements over weeks, months, and seasons. Tracks village
economies, population dynamics, feuds, union formation, and the long-term
march toward regional war.

**Lore reference:** `references/political_villages.md`

### 18.1 Village Economy Tick (Weekly)

Each settlement runs an economic tick once per week. Computed from
`data/political_state.yaml` runtime state plus authored economy inputs from
`data/economy/settlement_economies.yaml`, `data/settlements.yaml`, and
`data/geography/routes.yaml`.

**Weekly execution order:**

1. settlement food, silver, and stock update
2. import shortage resolution
3. route throughput and market-liquidity update
4. union treasury, tribute, levy, and seat-support pass
5. covert and dark-arts economy pass
6. wolfshead territorial-pressure pass
7. contract-market budget and offer pass

```text
field_food = crop_fields × season_mod × labor_ratio
goods_food = sum(authored_food_goods converted to person-days)
food_import_bonus = route throughput from imported staples
food_production = field_food + goods_food + food_import_bonus
food_consumption = population × season_consumption_rate
net_food = food_production - food_consumption
food_stores += net_food

for each produced good:
  commodity_stocks[good] += weekly_output_units

silver_income = weekly_income × trade_mod × feud_penalty + export route bonus
silver_expense = weekly_expense baseline + import drag + war or tribute drains
net_silver = silver_income - silver_expense
treasury += net_silver
```

**Minimum runtime state per settlement economy:**

```yaml
economies:
  "Frostfjord Hollow":
    crop_fields: 6
    livestock: { sheep: 30, goats: 15, cattle: 3, pigs: 5 }
    food_stores_days: 120
    food_stores_max: 160
    silver_treasury: 45
    weekly_trade_income: 10
    weekly_expenses: 6
    labor_allocation:
      farming: 0.50
      building: 0.10
      defense: 0.20
      crafting: 0.10
      idle: 0.10
    commodity_stocks:
      dried_cod: 10
      rope: 4
    stock_buckets:
      food: 10
      materials: 4
      trade: 0
    stock_capacities:
      food: 78
      materials: 28
      trade: 8
    weekly_production_by_good:
      dried_cod: 5
      rope: 2
    strategic_resource_flags:
      - deep_water_harbour
      - fishing_fleet
    unmet_imports: []
    dependency_health: 1.0
    repair_capacity_penalty: 0
    military_readiness_penalty: 0
    vulnerability_pressure: 0
    market_liquidity: 1.0
    local_price_pressure: 1.0
    route_partner_losses: []
    route_disruption_flags: []
    shortage_flags: []
```

**Production quantity mapping from authored settlement profiles:**

| Authored quantity | Runtime units per week | Meaning |
| ----------------- | ---------------------- | ------- |
| `low` | 2 | cottage or side-output |
| `medium` | 5 | stable local production |
| `high` | 9 | regional surplus or strategic specialty |

The runtime units above are abstract handling units for stock tracking, not
coins or exact pounds. They are deliberately small so one weekly tick can show
meaningful gains and shortages without turning state files into accounting
sprawl.

**Season Modifiers:**

| Season              | Food Production | Food Consumption |
| ------------------- | --------------- | ---------------- |
| Long Summer (1-60)  | ×1.0            | ×1.0 per person  |
| Early Dark (61-150) | ×0.3 (stored)   | ×1.1 per person  |
| Deep Dark (151-300) | ×0.0 (no grow)  | ×1.2 per person  |
| Late Dark (301-360) | ×0.0 (no grow)  | ×1.3 per person  |

**Labor Ratio:** Fraction of working-age population assigned to food
production vs. construction, defense, or other tasks. Default 0.7 (70%
food, 30% other). Adjustable per settlement.

**Food vs. non-food handling:**

- `crop_fields` and food-producing authored goods both feed `food_stores_days`
  indirectly.
- `commodity_stocks` tracks named goods such as `dried_cod`, `rope`, `timber`,
  or `iron_bloom`.
- `stock_buckets` provides three broad pressure summaries:
  - `food`
  - `materials`
  - `trade`
- `stock_capacities` are derived from actual built storage and workshop fabric
  in `data/settlements.yaml`.
- `strategic_resource_flags` are copied from authored settlement economy
  profiles so later systems can key off harbours, tar-works, mine heads,
  fishing fleets, and similar leverage points without reparsing prose.

**Import dependency and shortage propagation:**

For each authored import:

```text
need_units = urgency_weight
coverage_ratio = min(1.0, route_throughput / baseline_import_access)
short_units = need_units - covered_units - local_stock_cover
```

Effects:

- unmet food imports reduce effective weekly food gain
- unmet material imports add extra silver drag to emergency procurement
- essential timber, iron, nails, charcoal, salt, tar, rope, and tool shortages
  add repair or readiness penalties
- wartime `essential_imports_at_risk` marks shortages as strategically serious
- `economic_vulnerabilities` can add extra pressure tags such as blockade
  chokepoint or repair bottleneck

**Runtime shortage fields:**

- `unmet_imports`: named goods currently failing to arrive in sufficient volume
- `dependency_health`: `0.0-1.0` summary of how well import demand is being met
- `repair_capacity_penalty`: current penalty from tool, iron, timber, or fuel shortage
- `military_readiness_penalty`: current penalty from shortages affecting walls,
  boats, weapons, salt stores, or transport capacity
- `vulnerability_pressure`: aggregate stress from essential dependency failure
- `shortage_flags`: machine-readable tags such as `food_shortage:grain` or
  `vulnerability:blockade_chokepoint`

**Route throughput, disruption, and market liquidity:**

Routes now do more than add one abstract trade modifier. Each weekly tick reads
authored `trade_routes`, route seasonal access, route traffic level, route
frequency, feud drag, and the settlement's market profile.

```text
route_throughput = access_mod × traffic_mod × frequency_mod × feud_mod

market_liquidity =
  (route_support × trader_visit_mod × market_day_mod) + stall_support

local_price_pressure =
  market_price_modifier + illiquidity_penalty + partner_loss_penalty
```

Interpretation:

- low route throughput cuts export bonus and raises import drag
- dangerous or closed routes add disruption flags
- badly degraded routes can count as temporary trade-partner loss
- more stalls and more regular traders improve liquidity
- weak liquidity increases local price pressure even without a total blockade

**Runtime route-market fields:**

- `market_liquidity`: current `0.4-1.6` liquidity summary
- `local_price_pressure`: local market stress multiplier
- `route_partner_losses`: destinations currently functioning as lost or nearly
  lost partners
- `route_disruption_flags`: machine-readable route stress tags such as
  `route_access:RTE_001:dangerous`, `route_feud_drag:RTE_003`, or
  `partner_loss:2`

**Union treasury, tribute, levy, and trade-bonus economics:**

After all settlements resolve their own weekly economy tick, each union applies
a second weekly pass across its members. This pass consumes authored union data
from `data/political_state.yaml` directly.

Silver tribute is converted into weekly pressure like this:

```text
weekly_tribute_silver =
  tribute_silver_weekly
  + (tribute_silver_monthly / 4)
  + (tribute_silver_seasonal / 13)
  + campaign_season ? (tribute_silver_monthly_campaign_season / 4) : 0
```

Mixed dues are the default. Authored note fields such as `tribute_goods_note`
and `tribute_service_note` can create recurring food tribute, material tribute,
or service burden when they name winter stores, peat carts, lookout duty,
labor service, ferry priority, or forced crossings.

Effects:

- silver tribute leaves the member settlement treasury and enters
  `union.treasury_silver`
- food tribute moves from member `food_stores_days` into the seat's food stores
- material tribute moves through the `materials` stock bucket into the seat
- livestock tribute is accumulated weekly and transferred once whole animals are
  due
- levy obligations create a weekly readiness burden on the contributing member,
  not just a narrative flag
- `trade_bonus` on a member creates extra local trade silver and a smaller cut
  of dues into the union treasury

**Seat support burden:**

The overjarl's seat is not free to maintain. Each week, the union treasury must
cover the silver burden of retainers, messengers, feasts, patrol planning,
accounting, and command travel, plus a separate food draw at the seat. Military
unions pay more in silver under high war readiness; covert unions pay more when
dark-arts practice and whisper networks are active.

If the union treasury cannot pay full silver upkeep, the shortfall is paid
directly by the seat settlement's own treasury.

**Runtime union fields:**

```yaml
unions:
  - name: "The Iron Grip"
    treasury_silver: 14.2
    weekly_tribute_in_silver: 3.1
    weekly_tribute_in_food: 1.6
    weekly_tribute_in_materials: 1.2
    weekly_trade_bonus_silver: 0.0
    weekly_trade_dues_silver: 0.0
    weekly_levy_cost_silver: 0.0
    weekly_levy_fighters: 0
    seat_support_cost_silver: 4.6
    seat_support_cost_food: 1.8
    support_shortfall_silver: 0.0
    member_flows:
      - settlement: "Raven's Perch"
        silver_paid: 2.9
        food_paid: 1.6
        materials_paid: 0.0
        livestock_paid: 0
        service_burden_silver: 0.5
        levy_cost_silver: 0.0
        trade_bonus_silver: 0.0
        trade_dues_silver: 0.0
```

**Runtime settlement burden fields added by union pass:**

- `union_membership`
- `union_tribute_paid_silver`
- `union_tribute_paid_food`
- `union_tribute_paid_materials`
- `union_support_burden_silver`
- `union_levy_cost_silver`
- `union_trade_bonus_silver`
- `union_trade_dues_silver`

These make extraction and support costs inspectable through the CLI instead of
burying them in lore tables.

**Dark-arts and covert-network upkeep:**

After union tribute and seat support resolve, any union with
`dark_arts_level`, `dark_arts_practitioners`, or `whisper_agents` applies a
third weekly pass for occult and covert economy pressure.

```text
dark_arts_upkeep =
  practitioners × (0.6 + dark_arts_level × 0.2)
  + deteriorating_practitioners × 0.3

whisper_network_upkeep =
  sum(0.25 + quality × 0.2 for each whisper_agent)

smuggling_income =
  (total_agent_quality × 0.35)
  + (dark_arts_level × 0.15)
  - (deteriorating_practitioners × 0.1)
```

Effects:

- smuggling and covert skimming add silver to the union treasury before upkeep
  is paid
- occult upkeep drains union treasury, with any shortfall paid by the seat
  settlement directly
- the seat gains `covert_fear_pressure` and `confidence_shock_pressure`
- dark-arts practice reduces market liquidity at the seat and raises local
  price pressure
- each whisper agent applies smaller confidence and liquidity pressure at its
  target settlement
- targeted settlements receive machine-readable covert flags for inspection and
  later event logic

**Runtime covert fields:**

- On unions:
  - `dark_arts_upkeep_silver`
  - `whisper_network_upkeep_silver`
  - `smuggling_income_silver`
  - `confidence_shock_pressure`
  - `confidence_shock_targets`
- On settlement economies:
  - `covert_fear_pressure`
  - `confidence_shock_pressure`
  - `smuggling_leak_silver`
  - `covert_flags`

**Wolfshead band economy and territorial pressure:**

Wolfshead bands are now treated as weekly economic actors rather than pure
encounter flavor. Each band reads from `data/wolfshead_bands.yaml` and creates
runtime state from:

- `size`
- `threat_tier`
- `territory`
- `survival_strategy`
- `relationship_to_mercenaries`

The weekly pass estimates silver intake, food intake, desperation, target
settlements, and mercenary-market competition from the strategy text.

```text
weekly_income_silver = size × 0.12 × strategy_revenue_factor
weekly_food_gain = size × 0.35 × strategy_food_factor / winter_hunger_mod
food_need = size × seasonal_band_food_need
desperation = max(0, (food_need - weekly_food_gain) / (size / 2))
```

Pressure then propagates to named settlements found in the band's territory,
hook, winter strategy, or notes.

Effects on pressured settlements:

- `outlaw_pressure` rises to the highest active weekly threat nearby
- `night_market_chance` increases from that pressure
- coercive tribute or toll-taking creates `wolfshead_tribute_drag_silver`
- escort, toll, piracy, and protection-racket bands create
  `mercenary_competition_pressure`
- outlaw presence reduces local market liquidity and increases local price
  pressure
- settlement state gains machine-readable wolfshead pressure flags

**Runtime wolfshead fields:**

- On settlement economies:
  - `outlaw_pressure`
  - `night_market_chance`
  - `wolfshead_tribute_drag_silver`
  - `mercenary_competition_pressure`
  - `wolfshead_pressure_flags`
- On `state.wolfshead_state[band_id]`:
  - `weekly_income_silver`
  - `weekly_food_gain`
  - `desperation`
  - `pressure_targets`
  - `mercenary_competition`

**Contract-market budget and consequence wiring:**

The world contract market is derived from authored contract pools in
`data/contracts/*.yaml`, then filtered and stressed by current settlement
conditions each week.

For each settlement:

- load contracts anchored to that settlement
- filter by season and year
- honor basic political blockers such as `requires_feud_max`
- calculate an issuer budget from local treasury plus limited union support
- reduce effective payout capacity under scarcity, feud, outlaw pressure, and
  route stress
- rank contracts by local need rather than only by face-value silver

```text
issuer_budget_silver =
  settlement_treasury × 0.32
  + limited_union_support

demand_multiplier =
  1.0
  + outlaw_pressure × 0.12
  + route_stress
  + scarcity_stress
  + feud_pressure

payout_capacity_silver =
  issuer_budget_silver / demand_multiplier
```

The runtime market then exposes a small visible offer set, not the entire raw
contract library.

**Advance and payout handling:**

When a contract is activated:

- the employer pays `advance_silver` immediately
- the remaining payout is locked as `reserved_payout_silver`
- the contract is added to `contract_market.active_contracts`

When a contract resolves:

- success pays the reserved amount and improves the targeted settlement state
  according to contract type
- failure does not refund the advance and pushes the settlement further into
  stress

Examples:

- successful `guard`, `patrol`, or `garrison` work reduces `outlaw_pressure`
- successful `escort` or `trade_protection` work improves liquidity and lowers
  local price pressure
- failed defensive work increases outlaw pressure
- failed trade-protection work increases wolfshead tribute drag
- failed construction or siege-support work raises repair strain

**Runtime contract-market fields:**

- On settlement contract market state:
  - `available_contract_ids`
  - `offer_count`
  - `issuer_budget_silver`
  - `payout_capacity_silver`
  - `advance_capacity_silver`
  - `contract_value_locked_silver`
  - `advances_paid_silver`
  - `demand_multiplier`
  - `pressure_tags`
  - `visible_offers`
- On settlement economies:
  - `contract_offer_pressure`
  - `contract_budget_pressure`
  - `contract_market_tags`
- On active contracts:
  - `advance_paid_silver`
  - `reserved_payout_silver`
  - `days_remaining`
  - `status`

**Worked examples:**

**1. Blockade on a staple route**

- Frostfjord loses one winter route to closure and another drops to dangerous
  passage.
- `route_throughput` falls, `market_liquidity` drops, and
  `local_price_pressure` rises.
- grain or timber imports begin to miss weekly need.
- `unmet_imports`, `repair_capacity_penalty`, and shortage flags appear.
- if the blockade continues, the settlement grows poorer in both silver and
  resilience, not just in flavor text.

**2. Tribute squeeze on a subordinate village**

- Raven's Perch pays campaign-season silver plus winter stores into the Iron
  Grip.
- its treasury and food stores fall in the union pass.
- Grimholt gains inflow at first, but the seat also pays support cost every
  week.
- if the squeeze lasts too long, the subordinate weakens faster than the seat
  grows strong, which is the intended coercive dynamic.

**3. Outlaw predation around a trade settlement**

- a wolfshead band using toll-taking or smuggling raises `outlaw_pressure` on
  named nearby settlements.
- `night_market_chance` rises, market liquidity falls, and
  `wolfshead_tribute_drag_silver` appears.
- settlements facing this pressure also gain
  `mercenary_competition_pressure`, because outlaw escorts and protection cuts
  into lawful paid violence.

**4. Contract-driven supply disruption**

- a stressed settlement still advertises contracts, but its
  `issuer_budget_silver` and `payout_capacity_silver` are reduced by route
  stress, scarcity, feud, or outlaw pressure.
- activating a contract pays the advance immediately and locks the remaining
  payout.
- a successful escort or guard contract can improve local market conditions or
  reduce outlaw pressure.
- a failed escort, patrol, or siege-support contract worsens the settlement's
  economic state instead of disappearing into narrative abstraction.

### 18.2 Population Dynamics (Monthly)

Population changes computed monthly. Each settlement tracks:

```yaml
demographics:
  children: 18 # Under 10, consumers only
  elderly: 12 # Reduced labor
  women_working: 27 # Full labor, some fighters
  men_working: 28 # Full labor, primary fighters
  fighters: 10 # Trained warriors (subset of men/women_working)
  total: 95
```

**Monthly Events:**

| Event           | Calculation                                      |
| --------------- | ------------------------------------------------ |
| Births          | women_working × 0.006 × season_birth_mod         |
| Infant deaths   | births_this_month × 0.03                         |
| Disease deaths  | population × 0.001 × crowding_mod × season_mod   |
| Starvation      | If food_stores < 0: population × 0.02 per week   |
| Cold deaths     | Deep Dark only: population × 0.002 × shelter_mod |
| Violence deaths | From raids, feuds, or war (event-driven)         |
| Aging (yearly)  | Children → working age, working → elderly        |

**Season Birth Modifier:** Long Summer: ×1.5 (births from prior season
pregnancies). Long Dark: ×0.8 (fewer conceptions, harder conditions).

**Fighter Training:** A settlement can train new fighters at a rate of 1
per 30 days per existing fighter acting as trainer. Trainees must be
working-age men or women. Training costs 2 silver per week per trainee
(equipment, food supplement). Maximum trainable at once: 20% of current
fighter count (rounded up, minimum 1).

### 18.3 Village Infrastructure System

Settlement infrastructure is tracked as physical built fabric, not abstract
prosperity. A hall burns differently from a granary. A palisade rots
differently from a stone gatehouse. A jetty storm-damages without the
settlement being "attacked" in any conventional sense.

Each named settlement can carry explicit entries for:

- `defenses`
- `structures`
- `construction_capacity`
- `maintenance_burden`
- `damage_state`

#### 18.3.1 Infrastructure categories

| Category | Typical tags | Main simulation effect |
| -------- | ------------ | ---------------------- |
| Domestic | `longhouse`, `cottar_hut`, `byre`, `stable`, `barn` | shelter, cold-death reduction, labor retention |
| Storage | `granary`, `storehouse`, `root_cellar`, `smokehouse`, `fish_shed` | food capacity, spoilage reduction, siege resilience |
| Productive | `smithy`, `pit_workshop`, `loom_shed`, `kiln`, `tar_pit`, `charcoal_clamp`, `boathouse`, `jetty`, `dry_dock` | trade output, repair capacity, special goods |
| Civic | `hall`, `guesthall`, `inn`, `market_yard`, `thing_site`, `law_stone` | morale, politics, contracts, recruitment |
| Religious | `temple`, `shrine`, `altar_stone`, `barrow_keeper_hut`, `seidr_hut` | ritual legitimacy, ward maintenance, morale stability |
| Defensive | `hedge`, `ditch`, `palisade`, `wall`, `gatehouse`, `watchtower`, `beacon`, `harbor_chain` | alert time, defense multiplier, anti-raid friction |

#### 18.3.2 Build resources and throughput

All new works consume some mixture of wood, stone, turf, iron fittings, and
labor. Silver can replace missing materials only by trade and only if supply
routes are open.

**Core resource units:**

- `wood_units`: usable timbers, planks, poles, and brush bundles
- `stone_units`: quarried or field stone fit for foundation, walling, or ditch
  facing
- `turf_units`: sod, clay, wattle, daub, and roofing earth
- `iron_units`: nails, clamps, hinges, tools, chain, and gate fittings
- `labor_days`: one adult worker's hard day on a construction site

**Weekly build throughput:**

```text
base_labor_days = (working_population × building_labor_ratio × 6)
skilled_bonus = (carpenters × 4) + (masons × 4) + (smiths × 2)
season_mod = 1.0 long_summer, 0.8 early_dark, 0.35 deep_dark, 0.5 late_dark
disruption_mod = 0.0-1.0 from raids, fear, occupation, famine, or siege

effective_labor_days = floor((base_labor_days + skilled_bonus) × season_mod × disruption_mod)
```

**Interpretation:**

- Hamlets usually sustain 8-20 effective labor-days per week without starving
  themselves.
- Villages usually sustain 15-40.
- Large villages usually sustain 30-70.
- Small towns or heavily mobilized seats can exceed 80, but usually at an
  economic cost elsewhere.

If a settlement diverts more than 25% of its working population to building
for more than one month, apply one of the following:

- `food_production -10%`
- `trade_income -10%`
- `defense_readiness -1`

#### 18.3.3 Canonical structure costs

These values are sized for Rimevegr settlements rather than for private
adventurer strongholds.

| Structure | Wood | Stone | Turf | Iron | Labor-days | Annual upkeep | Notes |
| --------- | ---- | ----- | ---- | ---- | ---------- | ------------- | ----- |
| Hedge line / thorn belt (100 m) | 6 | 0 | 2 | 0 | 20 | 6 | Fast to raise, slow to keep dense |
| Ditch (100 m) | 2 | 6 | 0 | 0 | 36 | 4 | Spoil can reinforce bank |
| Palisade (100 m) | 18 | 2 | 2 | 1 | 48 | 10 | Rot risk high in wet ground |
| Timber gatehouse | 12 | 4 | 2 | 2 | 40 | 8 | Requires wall, hedge, or palisade anchor |
| Watchtower / beacon tower | 10 | 4 | 1 | 1 | 28 | 6 | Best on ridge, cliff, or harbor edge |
| Stone wall (100 m) | 8 | 24 | 4 | 2 | 90 | 12 | Needs masons or time doubles |
| Longhouse / farmhouse | 16 | 4 | 10 | 1 | 55 | 8 | Can absorb byre under same roof |
| Byre / barn | 10 | 2 | 6 | 1 | 28 | 6 | Livestock shelter and fodder store |
| Granary / raised storehouse | 8 | 6 | 4 | 1 | 26 | 5 | Food capacity +60 person-days |
| Root cellar | 2 | 8 | 6 | 0 | 18 | 3 | Food capacity +40 person-days |
| Smokehouse / fish shed | 6 | 2 | 4 | 0 | 14 | 3 | Preserves fish and meat |
| Smithy (basic) | 10 | 8 | 4 | 4 | 36 | 7 | Repair work, nails, tools |
| Smithy (skilled) | 14 | 10 | 4 | 6 | 58 | 10 | Weapon and armor craft |
| Hall / guesthall | 20 | 6 | 12 | 2 | 70 | 10 | Morale, hospitality, contracts |
| Temple / stone shrine | 6 | 18 | 4 | 1 | 60 | 8 | Legitimacy and ward focus |
| Boathouse | 12 | 2 | 6 | 1 | 24 | 5 | Weatherproof hull storage |
| Jetty / landing stage | 14 | 6 | 0 | 2 | 32 | 7 | Storm damage risk high |
| Dry-dock / shipyard shed | 18 | 8 | 4 | 3 | 54 | 9 | Needed for serious ship repair |
| Harbor chain emplacement | 6 | 8 | 0 | 8 | 30 | 6 | Requires harbor geometry |
| Tar pit / charcoal clamp site | 6 | 2 | 2 | 0 | 12 | 2 | Production site more than a building |

#### 18.3.4 Build sequencing and requirements

Structures cannot be built in any order the settlement wants. They require
materials, labor, and often prerequisite fabric.

| Structure | Typical prerequisite |
| --------- | -------------------- |
| Gatehouse | existing `hedge`, `palisade`, or `wall` |
| Watchtower | defended perimeter or commanding terrain |
| Skilled smithy | basic smithy or imported master smith |
| Temple | stable population 80+ or regional pilgrimage role |
| Jetty / harbor chain | viable shore, river, or harbor frontage |
| Stone wall | quarry access or trade access to stone plus mason labor |
| Hall | enough food surplus to host non-kin gatherings regularly |

**Build time:**

```text
weeks_to_complete = ceil(total_labor_days / max(1, effective_labor_days))
```

If a required skilled trade is missing:

- no carpenters for timber frame or jetty work: `labor_days × 1.5`
- no masons for stone wall or temple work: `labor_days × 2.0`
- no smith for iron gate, chain, or skilled forge: structure capped at
  improvised quality or delayed until fittings are imported

#### 18.3.5 Annual maintenance and neglect

Every structure has annual upkeep measured in maintenance points. These can be
paid in labor and materials during the yearly repair season.

```text
maintenance_points_paid =
  floor(labor_days_committed / 3)
  + wood_units_spent
  + stone_units_spent
  + iron_units_spent × 2
```

```text
maintenance_ratio = maintenance_points_paid / annual_upkeep_required
```

**Maintenance outcomes:**

| Ratio | Outcome |
| ----- | ------- |
| 1.0+  | Sound. No decay tick. |
| 0.75+ | Worn. Cosmetic wear only. |
| 0.5+  | Strained. One vulnerable structure becomes `worn`. |
| 0.25+ | Neglected. One vulnerable structure becomes `damaged`; spoilage and cold risk rise. |
| <0.25 | Failing. Defensive works lose effect; random collapse or fire vulnerability check. |

**Automatic maintenance pressure:**

- Coast and river structures pay +25% upkeep due to rot, ice, and storm wear.
- Moor hedge and turf works pay +20% upkeep after bad-weather years.
- Occupied settlements pay only half normal upkeep unless occupiers invest in
  the place.

#### 18.3.6 Damage states and repair

Each structure or settlement-wide element can sit in one of five states:

| State | Integrity | Mechanical effect |
| ----- | --------- | ----------------- |
| `sound` | 100-85% | full effect |
| `worn` | 84-65% | no major penalty, but first future hit escalates faster |
| `damaged` | 64-40% | half effect; visible weakness; morale penalty if civic or religious |
| `crippled` | 39-15% | nearly unusable; defense or production bonus mostly lost |
| `ruined` | 14-0% | no function; site remains as debris, burned shell, collapsed wall, or flooded works |

**Repair cost by state:**

| Target state | Cost |
| ------------ | ---- |
| `worn` -> `sound` | 25% of original labor and material cost |
| `damaged` -> `sound` | 50% of original cost |
| `crippled` -> `sound` | 75% of original cost |
| `ruined` -> `sound` | 90% of original cost unless stone foundations survive; then 75% |

**Repair rule:** repairs must restore the structural bottleneck first. A
granary with a broken roof but intact floor can be repaired cheaply; a palisade
with burned posts and a failed gate needs the gate throat rebuilt before the
line counts as defensive again.

#### 18.3.7 Fire, sack, and razing

Not all destruction is equal.

**Fire vulnerability by structure:**

| Structure class | Fire risk |
| --------------- | --------- |
| Timber/turf hall, longhouse, byre, boathouse | High |
| Granary, smokehouse, fish shed, jetty | Very high |
| Palisade, gatehouse, tower | High |
| Stone wall, root cellar, stone temple | Low to medium |
| Ditch, earth bank, thorn belt | Very low |

**Raid fire resolution:**

```text
fire_damage_score = attacker_success_margin + dry_weather_mod + pitch_or_tar_bonus - defender_response
```

| Fire damage score | Outcome |
| ----------------- | ------- |
| 0 or less | fire contained |
| 1-2 | one vulnerable structure becomes `damaged` |
| 3-4 | one vulnerable structure becomes `crippled`; adjacent timber work becomes `worn` |
| 5-6 | one structure becomes `ruined`; one more becomes `damaged` |
| 7+ | local conflagration; 1d3 structures ruined, morale -1, food losses severe if storage burns |

**Deliberate razing:** a victorious attacker in control of a settlement may
raze fabric after the fight.

```text
raze_progress_per_day = floor(attacking_laborers / 8) + engineer_bonus + fire_bonus
```

Suggested raze thresholds:

- 2 progress: burn one household cluster or one production site
- 4 progress: destroy one gate complex or hall
- 6 progress: make a hamlet nonfunctional for the season
- 10 progress: reduce a village's defensive perimeter to broken segments

Stone works usually become gutted or dismantled, not erased. Mark them
`ruined`, not absent, unless labor is spent to quarry them away over weeks.

#### 18.3.8 Occupation, tribute, and slow structural death

Repeated tribute and occupation damage settlements even when no dramatic sack
occurs.

**Occupation decay check (monthly):**

```text
occupation_decay = occupier_extraction + unpaid_maintenance + crowding + fear_factor
```

Effects by result:

- `0-2`: no structural change
- `3-4`: one storage or domestic structure becomes `worn`
- `5-6`: one defensive or productive structure becomes `damaged`
- `7+`: one key structure becomes `crippled`, morale -1, population flight risk

**Repeated tribute:** each season of harsh tribute without compensating support:

- convert 10-20% of available maintenance labor into tribute handling,
  transport, provisioning, and escort duty
- reduce new construction by 25%
- strip 1-3 silver equivalent per 25 population in mixed dues: silver, grain,
  livestock, peat, charcoal, or hauled goods depending on settlement economy
- after two consecutive seasons, one nonessential structure cluster becomes
  `worn`

This is how villages hollow out before they visibly collapse.

### 18.4 Crop and Livestock System

**Crops:** Planted during Long Summer only (Days 1-60). Harvest quality
depends on weather, labor, and whether raiders disrupted planting.

```text
crop_yield = planted_fields × soil_quality × weather_score × labor_ratio
             × (1.0 - raid_disruption)
```

**Planted Fields:** Each settlement has a maximum field capacity based on
terrain and population. One worker can tend 2 fields. One field feeds 3
people for a year in ideal conditions.

**Livestock:**

| Type   | Feed Cost/Week | Products                      | Breeding Rate |
| ------ | -------------- | ----------------------------- | ------------- |
| Sheep  | 0.5 food units | Wool, mutton, milk            | 1.2/year      |
| Goats  | 0.3 food units | Milk, hides, some meat        | 1.5/year      |
| Cattle | 1.5 food units | Milk, beef, hides, draft work | 0.8/year      |
| Pigs   | 1.0 food units | Pork, lard                    | 2.0/year      |

**Winter Culling:** Before Deep Dark, settlements slaughter livestock they
cannot feed. Remaining animals consume stored feed. A settlement that
miscalculates loses animals to starvation mid-winter.

**Livestock Raiding:** The most common cause of feuds. Each raided animal =
1 feud point with the victim settlement.

### 18.5 Raiding and Livestock Theft

Raids are the engine of feuds. A raid is a quick strike: arrive, take what
you can carry, leave.

**Raid Calculation:**

```text
raid_force = num_raiders × average_combat_power
defense_force = settlement_fighters × defensibility_mod × alert_mod

If raid_force > defense_force × 1.5: raid succeeds, no raider losses
If raid_force > defense_force: raid succeeds, 10% raider casualties
If raid_force > defense_force × 0.7: partial success, 20% casualties
Else: raid fails, 30% raider casualties
```

**Raid Loot:**

| Target       | Loot per Success Point                 |
| ------------ | -------------------------------------- |
| Livestock    | 2d6 sheep or 1d4 cattle                |
| Grain stores | 10-30 food days stolen                 |
| Silver       | 5-20 silver                            |
| Thralls      | 1d4 captives (if raider takes thralls) |

**Raid Consequences:**

- Feud level with raided settlement: +1 (minimum)
- Feud level +2 if buildings burned
- Feud level +3 if people killed
- Victim settlement morale: -1
- Raider settlement morale: +1 if loot > 10 silver equivalent
- Apply `18.3.6` damage states to any struck structures instead of treating
  "building damage" as a binary on/off flag.
- If granaries, smokehouses, root cellars, or fish sheds are burned, remove
  the associated stored food before weekly economy ticks resume.

### 18.6 Feud System (Settlement-to-Settlement)

Feuds track hostility between pairs of settlements. Stored in
`data/political_state.yaml`.

**Feud Scale (0-4):**

| Level | Name       | Trade | Raid Risk | Hired Bands | War Host |
| ----- | ---------- | ----- | --------- | ----------- | -------- |
| 0     | Cold       | Open  | None      | No          | No       |
| 1     | Tense      | -20%  | Low       | No          | No       |
| 2     | Hostile    | -50%  | Medium    | Maybe       | No       |
| 3     | Blood-feud | None  | High      | Yes         | Forming  |
| 4     | Vengeance  | None  | Constant  | Yes         | Active   |

**Feud Escalation Triggers (per season):**

| Event                     | Feud Change |
| ------------------------- | ----------- |
| Livestock raided          | +1          |
| Buildings burned          | +2          |
| People killed in raid     | +2          |
| Leader insulted at thing  | +1          |
| Border encroachment       | +1          |
| Tribute demanded/refused  | +1          |
| Hired band attacked other | +1          |

**Feud De-Escalation (per season):**

| Action                  | Feud Change |
| ----------------------- | ----------- |
| Weregild paid (full)    | -2          |
| Shared external threat  | -1          |
| Marriage alliance       | -1          |
| Thing judgment accepted | -1          |
| One full year of peace  | -1          |

**Minimum feud:** 0. **Maximum:** 4. Feud at 4 can only decrease through
weregild, marriage, or destruction of one settlement.

### 18.7 Union Mechanics

Unions are tracked as named alliance structures in
`data/political_state.yaml`.

```yaml
unions:
  - name: "The Iron Grip"
    overjarl: "Ordovast"
    seat: "Grimholt"
    type: military # military / economic / covert
    cohesion: 4 # 1-5, how tightly bound
    members:
      - settlement: "Grimholt"
        role: core
        loyalty: 5
        tribute_silver_weekly: 0
      - settlement: "Raven's Perch"
        role: subordinate
        loyalty: 3
        tribute_silver_monthly_campaign_season: 6
        tribute_silver_seasonal: 18
        tribute_goods_note: "winter stores and lookout service demanded when Ordovast readies a march"
    combined_fighters: 58
    combined_population: 243
    war_readiness: 3 # 0-5
    dark_arts_level: 0 # 0-5
```

**Union Cohesion (1-5):**

| Level | Meaning                                            |
| ----- | -------------------------------------------------- |
| 5     | Unified command. Members obey without question.    |
| 4     | Strong. Minor grumbling but reliable in crisis.    |
| 3     | Functional. Requires active diplomacy to maintain. |
| 2     | Fragile. One bad event could cause defection.      |
| 1     | Nominal. Members already looking for alternatives. |

**Cohesion Modifiers (checked seasonally):**

| Event                             | Cohesion Change |
| --------------------------------- | --------------- |
| Successful joint defense          | +1              |
| Overjarl shares loot fairly       | +1              |
| Member settlement raided, no help | -2              |
| Overjarl increases tribute        | -1              |
| Overjarl dies                     | -2              |
| External threat declared          | +1              |
| Internal feud between members     | -1              |
| Allthing renewal ceremony         | +1              |

### 18.8 War Readiness

Union war readiness tracks how close a union is to launching a campaign
against another.

**War Readiness Scale (0-5):**

| Level | State                                            |
| ----- | ------------------------------------------------ |
| 0     | Peacetime. No military preparation.              |
| 1     | Alert. Scouts watching borders. Stockpiling.     |
| 2     | Mobilizing. Calling in levies. Hiring bands.     |
| 3     | Ready. War-host assembled. Waiting for trigger.  |
| 4     | Marching. Committed to campaign.                 |
| 5     | Total war. All resources devoted to destruction. |

**War Readiness Increase (checked monthly):**

| Condition                       | Readiness Change |
| ------------------------------- | ---------------- |
| Feud with rival union at 3+     | +1               |
| Overjarl ambition (personality) | +1 per season    |
| Rival union weakened            | +1               |
| Successful raid on rival        | +1               |
| Svarthird band recruited        | +1               |

**War Readiness Decrease:**

| Condition                         | Readiness Change |
| --------------------------------- | ---------------- |
| Bad harvest (food stores < 60d)   | -1               |
| Lost engagement                   | -1               |
| Cohesion drops below 3            | -1               |
| Overjarl dies or is incapacitated | -2               |
| Allthing peace treaty             | -2               |

### 18.9 Dark Arts Level

Tracks a union's investment in forbidden supernatural practices. Only the
Whispering Circle starts with a nonzero value.

**Dark Arts Scale (0-5):**

| Level | Capability                                           |
| ----- | ---------------------------------------------------- |
| 0     | None. Normal rune-craft only.                        |
| 1     | Seidr-worker consulted. Dream-sending possible.      |
| 2     | Active curse-carving. Nithing-poles deployed.        |
| 3     | Veil-thinning at specific sites. Fear weapons.       |
| 4     | Death-reading operational. Targeted assassinations.  |
| 5     | Invocation attempted. Drawing Veil-entities' notice. |

**Dark Arts Consequences:**

| Level | Risk                                                    |
| ----- | ------------------------------------------------------- |
| 1     | Practitioners show wear. Manageable.                    |
| 2     | Neighboring settlements hear rumors. Fear +1.           |
| 3     | Veil instability near seat. Random supernatural events. |
| 4     | Practitioners deteriorating. 10% chance of loss/month.  |
| 5     | Uncontrollable Veil breach possible. 20%/month.         |

**Dark Arts Interaction with Other Unions:**

- At level 2+, other unions gain a "fear_of_dark_arts" modifier
that reduces their willingness to attack directly (-1 war readiness when
considering direct assault on the dark-arts user).
- At level 3+, neutral settlements may refuse to trade with the
dark-arts user (feud +1 with all non-allied settlements).
- At level 5, the Veil response is uncontrollable. The invocation
may succeed (devastating weapon against enemies) or backfire (Veil breach
at the caster's own settlement, draugr incursion, permanent supernatural
contamination).

### 18.10 The Allthing (Annual Assembly)

**Timing:** Day 90-100 (after harvest, early Long Dark).

**Resolution:** The Allthing resolves accumulated political tension. All
unions and independent settlements send representatives.

**Allthing Actions (each leader gets 1-2 actions):**

| Action             | Effect                                        |
| ------------------ | --------------------------------------------- |
| Declare feud       | Formal feud +1 with named settlement          |
| End feud           | Feud -2 if both parties agree + weregild      |
| Propose alliance   | Roll Persuade vs. target's Wits to join union |
| Demand tribute     | Roll Intimidate vs. target's Will             |
| Trade deal         | Both settlements +10% trade income for year   |
| Marriage pact      | Feud -1 + cohesion +1 between families        |
| Declare outlawry   | Named person banned from all settlements      |
| Share intelligence | Reveal hidden info to allies                  |

**Allthing Intrigue:** The Pale Widow's agents operate during the Allthing.
Each Allthing, roll for whisper-agent success:

```text
intel_chance = dark_arts_level × 15 + widow_wit × 5
If success: Widow learns one hidden agenda or plan from target union
If critical: Widow can plant false information in target union
```

### 18.11 Seasonal Political Tick

The political simulation runs a major tick once per season (4 times per
year). Each tick:

1. **Economy:** All settlements run weekly ticks for the season
(aggregate). Food stores updated. Silver updated.
2. **Population:** Monthly population changes applied (3 months per
season for Long Dark, 2 months for Long Summer).
3. **Feuds:** All active feuds checked for escalation/de-escalation.
4. **Unions:** Cohesion checked. War readiness updated. Dark arts
consequences applied.
5. **Raids:** AI determines which settlements or unions launch raids
based on food shortage, feud level, and overjarl personality.
6. **Building:** Construction progress advanced.
   Maintenance arrears, repairs, and occupation decay also advance here.
7. **Training:** Fighter training progress advanced.
8. **Events:** Political hidden events checked and triggered.

### 18.12 Starting Political State (Year 312)

```yaml
# --- Starting Feuds ---
feuds:
  - pair: ["Grimholt", "Deepholm"]
    level: 2 # Hostile — Ordovast expanding toward Sigrun's territory
  - pair: ["Frostfjord Hollow", "Ashen Reach"]
    level: 1 # Tense — historical rivalry, Pale Widow scheming
  - pair: ["Grimholt", "Thornwall"]
    level: 1 # Tense — Ordovast wants Thornwall's pastureland
  - pair: ["Feldwick", "Three Wolves"]
    level: 3 # Blood-feud — second occupation this year

# --- Starting Unions ---
unions:
  - name: "The Iron Grip"
    overjarl: "Ordovast"
    seat: "Grimholt"
    type: military
    cohesion: 4
    war_readiness: 2 # Mobilizing
    dark_arts_level: 0
    members: ["Grimholt", "Raven's Perch", "Bleakwater Landing", "Moor's End"]

  - name: "The Fjord Compact"
    overjarl: "Sigrun"
    seat: "Deepholm"
    type: economic
    cohesion: 3
    war_readiness: 1 # Alert
    dark_arts_level: 0
    members: ["Deepholm", "Thornwall", "Kolvik", "Skaldhaven", "Ashmark"]

  - name: "The Whispering Circle"
    overjarl: "Pale Widow"
    seat: "Ashen Reach"
    type: covert
    cohesion: 2
    war_readiness: 1 # Alert
    dark_arts_level: 2 # Active curse-carving
    members: ["Ashen Reach", "Frostfjord Hollow", "Vargheim"]

# --- Independent Settlements ---
independent: ["Feldwick", "Stonebay Hamlet", "Icebreak"]

# --- Projected Timeline (encoded — use spoiler_codec.py to decode) ---
# SPOILER: 乙乥乡乲丠丳丱串丠乓乥乡乳乯乮丠丱为丠乕乮乥乡乳乹丠买乥乡乣乥丮丠乕乮乩乯乮乳丠乣乯乮乳乯乬乩乤乡乴乩乮乧丮
# SPOILER: 乙乥乡乲丠丳丱串丠乓乥乡乳乯乮丠串中丳为丠乏乲乤乯乶乡乳乴丠乢乥乧乩乮乳丠乢乯乲乤乥乲丠买乲乥乳乳乵乲乥丠乯乮丠乔乨乯乲乮乷乡乬乬丮
# SPOILER: 乙乥乡乲丠丳丱串丠乓乥乡乳乯乮丠临为丠乁乬乬乴乨乩乮乧丠仢亀五丠乬乡乳乴丠乣乨乡乮乣乥丠书乯乲丠乤乩买乬乯乭乡乣乹丮
# SPOILER: 乙乥乡乲丠丳丱丳丠乓乥乡乳乯乮丠丱为丠乏乲乤乯乶乡乳乴丠乭乡乲乣乨乥乳丠乩书丠乷乡乲也乲乥乡乤乩乮乥乳乳丠乲乥乡乣乨乥乳丠临丮
# SPOILER: 乙乥乡乲丠丳丱丳丠乓乥乡乳乯乮丠串中丳为丠乆乵乬乬丠乲乥乧乩乯乮乡乬丠乷乡乲丠乩书丠乮乯乴丠乡乶乥乲乴乥乤丮
# SPOILER: 乙乥乡乲丠丳丱丳丫为丠乐乡乬乥丠乗乩乤乯乷丠乤乡乲乫丠乧乡乭乢乩乴丠乴乲乩乧乧乥乲乳丠乩书丠乢乯乴乨丠乵乮乩乯乮乳丠乷乥乡乫乥乮丮
```

### 18.13 Political Subsystem Commands

All commands run from the `scripts/` directory.

```bash
# Show current political state
python village_politics.py status

# Show specific union
python village_politics.py union --name "The Iron Grip"

# Show feuds
python village_politics.py feuds

# Advance one season
python village_politics.py tick --season

# Advance one week (economy only)
python village_politics.py tick --week

# Run the Allthing
python village_politics.py allthing

# Execute a raid
python village_politics.py raid --from Grimholt --target Thornwall --force 20

# Show village economy
python village_politics.py economy --settlement "Deepholm"

# Show population demographics
python village_politics.py demographics --settlement "Grimholt"

# Show war readiness for all unions
python village_politics.py war-readiness

# Show dark arts status
python village_politics.py dark-arts --union "The Whispering Circle"

# Generate narrative summary of political season
python village_politics.py narrative --season 3
```

---

## 18. Political Simulation (Village Networks)

Resolved by `village_politics.py`. Simulates the political landscape of
Rimevegr settlements over weeks, months, and seasons. Tracks village
economies, population dynamics, feuds, union formation, and the long-term
march toward regional war.

**Lore reference:** `references/political_villages.md`

### 18.1 Village Economy Tick (Weekly)

Each settlement runs an economic tick once per week. Computed from
`data/settlements.yaml` fields.

```text
food_production = base_food × season_mod × labor_ratio × weather_mod
food_consumption = population × season_consumption_rate
net_food = food_production - food_consumption
food_stores += net_food

silver_income = weekly_income × trade_mod × feud_penalty
silver_expense = garrison_pay + tribute_out + maintenance
net_silver = silver_income - silver_expense
treasury += net_silver
```

**Season Modifiers:**

| Season              | Food Production | Food Consumption |
| ------------------- | --------------- | ---------------- |
| Long Summer (1-60)  | ×1.0            | ×1.0 per person  |
| Early Dark (61-150) | ×0.3 (stored)   | ×1.1 per person  |
| Deep Dark (151-300) | ×0.0 (no grow)  | ×1.2 per person  |
| Late Dark (301-360) | ×0.0 (no grow)  | ×1.3 per person  |

**Labor Ratio:** Fraction of working-age population assigned to food
production vs. construction, defense, or other tasks. Default 0.7 (70%
food, 30% other). Adjustable per settlement.

### 18.2 Population Dynamics (Monthly)

Population changes computed monthly. Each settlement tracks:

```yaml
demographics:
  children: 18 # Under 10, consumers only
  elderly: 12 # Reduced labor
  women_working: 27 # Full labor, some fighters
  men_working: 28 # Full labor, primary fighters
  fighters: 10 # Trained warriors (subset of men/women_working)
  total: 95
```

**Monthly Events:**

| Event           | Calculation                                      |
| --------------- | ------------------------------------------------ |
| Births          | women_working × 0.006 × season_birth_mod         |
| Infant deaths   | births_this_month × 0.03                         |
| Disease deaths  | population × 0.001 × crowding_mod × season_mod   |
| Starvation      | If food_stores < 0: population × 0.02 per week   |
| Cold deaths     | Deep Dark only: population × 0.002 × shelter_mod |
| Violence deaths | From raids, feuds, or war (event-driven)         |
| Aging (yearly)  | Children → working age, working → elderly        |

**Season Birth Modifier:** Long Summer: ×1.5 (births from prior season
pregnancies). Long Dark: ×0.8 (fewer conceptions, harder conditions).

**Fighter Training:** A settlement can train new fighters at a rate of 1
per 30 days per existing fighter acting as trainer. Trainees must be
working-age men or women. Training costs 2 silver per week per trainee
(equipment, food supplement). Maximum trainable at once: 20% of current
fighter count (rounded up, minimum 1).

### 18.3 Community Buildings

Settlements can build and upgrade structures. Buildings provide economic
bonuses, defensive capacity, or special capabilities.

| Building         | Cost (silver) | Build Time | Effect                        |
| ---------------- | ------------- | ---------- | ----------------------------- |
| Palisade         | 30            | 30 days    | Defensibility +1              |
| Stone wall       | 120           | 90 days    | Defensibility +2              |
| Watchtower       | 40            | 20 days    | Raid warning +1 day           |
| Granary          | 25            | 15 days    | Food stores capacity +30 days |
| Smithy (basic)   | 50            | 30 days    | Weapon/armor repair           |
| Smithy (skilled) | 150           | 60 days    | Weapon/armor crafting         |
| Healer's lodge   | 20            | 10 days    | Wound recovery ×1.5           |
| Hall upgrade     | 80            | 45 days    | Morale +1, capacity +20       |
| Dock/shipwright  | 100           | 45 days    | Ship repair, coastal trade    |
| Temple           | 60            | 30 days    | Morale +1, rune services      |
| Charcoal kiln    | 35            | 20 days    | Fuel production, trade good   |

**Building requires:** Available labor (at least 5 workers diverted from
other tasks), materials (wood/stone/iron from stores or trade), and no
active siege or occupation.

**Damaged buildings:** Raids at feud level 2+ may damage buildings. Damaged
buildings lose their bonuses until repaired (half original build time, half
cost).

### 18.4 Crop and Livestock System

**Crops:** Planted during Long Summer only (Days 1-60). Harvest quality
depends on weather, labor, and whether raiders disrupted planting.

```text
crop_yield = planted_fields × soil_quality × weather_score × labor_ratio
             × (1.0 - raid_disruption)
```

**Planted Fields:** Each settlement has a maximum field capacity based on
terrain and population. One worker can tend 2 fields. One field feeds 3
people for a year in ideal conditions.

**Livestock:**

| Type   | Feed Cost/Week | Products                      | Breeding Rate |
| ------ | -------------- | ----------------------------- | ------------- |
| Sheep  | 0.5 food units | Wool, mutton, milk            | 1.2/year      |
| Goats  | 0.3 food units | Milk, hides, some meat        | 1.5/year      |
| Cattle | 1.5 food units | Milk, beef, hides, draft work | 0.8/year      |
| Pigs   | 1.0 food units | Pork, lard                    | 2.0/year      |

**Winter Culling:** Before Deep Dark, settlements slaughter livestock they
cannot feed. Remaining animals consume stored feed. A settlement that
miscalculates loses animals to starvation mid-winter.

**Livestock Raiding:** The most common cause of feuds. Each raided animal =
1 feud point with the victim settlement.

### 18.5 Raiding and Livestock Theft

Raids are the engine of feuds. A raid is a quick strike: arrive, take what
you can carry, leave.

**Raid Calculation:**

```text
raid_force = num_raiders × average_combat_power
defense_force = settlement_fighters × defensibility_mod × alert_mod

If raid_force > defense_force × 1.5: raid succeeds, no raider losses
If raid_force > defense_force: raid succeeds, 10% raider casualties
If raid_force > defense_force × 0.7: partial success, 20% casualties
Else: raid fails, 30% raider casualties
```

**Raid Loot:**

| Target       | Loot per Success Point                 |
| ------------ | -------------------------------------- |
| Livestock    | 2d6 sheep or 1d4 cattle                |
| Grain stores | 10-30 food days stolen                 |
| Silver       | 5-20 silver                            |
| Thralls      | 1d4 captives (if raider takes thralls) |

**Raid Consequences:**

- Feud level with raided settlement: +1 (minimum)
- Feud level +2 if buildings burned
- Feud level +3 if people killed
- Victim settlement morale: -1
- Raider settlement morale: +1 if loot > 10 silver equivalent

### 18.6 Feud System (Settlement-to-Settlement)

Feuds track hostility between pairs of settlements. Stored in
`data/political_state.yaml`.

**Feud Scale (0-4):**

| Level | Name       | Trade | Raid Risk | Hired Bands | War Host |
| ----- | ---------- | ----- | --------- | ----------- | -------- |
| 0     | Cold       | Open  | None      | No          | No       |
| 1     | Tense      | -20%  | Low       | No          | No       |
| 2     | Hostile    | -50%  | Medium    | Maybe       | No       |
| 3     | Blood-feud | None  | High      | Yes         | Forming  |
| 4     | Vengeance  | None  | Constant  | Yes         | Active   |

**Feud Escalation Triggers (per season):**

| Event                     | Feud Change |
| ------------------------- | ----------- |
| Livestock raided          | +1          |
| Buildings burned          | +2          |
| People killed in raid     | +2          |
| Leader insulted at thing  | +1          |
| Border encroachment       | +1          |
| Tribute demanded/refused  | +1          |
| Hired band attacked other | +1          |

**Feud De-Escalation (per season):**

| Action                  | Feud Change |
| ----------------------- | ----------- |
| Weregild paid (full)    | -2          |
| Shared external threat  | -1          |
| Marriage alliance       | -1          |
| Thing judgment accepted | -1          |
| One full year of peace  | -1          |

**Minimum feud:** 0. **Maximum:** 4. Feud at 4 can only decrease through
weregild, marriage, or destruction of one settlement.

### 18.7 Union Mechanics

Unions are tracked as named alliance structures in
`data/political_state.yaml`.

```yaml
unions:
  - name: "The Iron Grip"
    overjarl: "Ordovast"
    seat: "Grimholt"
    type: military # military / economic / covert
    cohesion: 4 # 1-5, how tightly bound
    members:
      - settlement: "Grimholt"
        role: core
        loyalty: 5
        tribute_silver_weekly: 0
      - settlement: "Raven's Perch"
        role: subordinate
        loyalty: 3
        tribute_silver_monthly_campaign_season: 6
        tribute_silver_seasonal: 18
        tribute_goods_note: "winter stores and lookout service demanded when Ordovast readies a march"
    combined_fighters: 58
    combined_population: 243
    war_readiness: 3 # 0-5
    dark_arts_level: 0 # 0-5
```

**Union Cohesion (1-5):**

| Level | Meaning                                            |
| ----- | -------------------------------------------------- |
| 5     | Unified command. Members obey without question.    |
| 4     | Strong. Minor grumbling but reliable in crisis.    |
| 3     | Functional. Requires active diplomacy to maintain. |
| 2     | Fragile. One bad event could cause defection.      |
| 1     | Nominal. Members already looking for alternatives. |

**Cohesion Modifiers (checked seasonally):**

| Event                             | Cohesion Change |
| --------------------------------- | --------------- |
| Successful joint defense          | +1              |
| Overjarl shares loot fairly       | +1              |
| Member settlement raided, no help | -2              |
| Overjarl increases tribute        | -1              |
| Overjarl dies                     | -2              |
| External threat declared          | +1              |
| Internal feud between members     | -1              |
| Allthing renewal ceremony         | +1              |

### 18.8 War Readiness

Union war readiness tracks how close a union is to launching a campaign
against another.

**War Readiness Scale (0-5):**

| Level | State                                            |
| ----- | ------------------------------------------------ |
| 0     | Peacetime. No military preparation.              |
| 1     | Alert. Scouts watching borders. Stockpiling.     |
| 2     | Mobilizing. Calling in levies. Hiring bands.     |
| 3     | Ready. War-host assembled. Waiting for trigger.  |
| 4     | Marching. Committed to campaign.                 |
| 5     | Total war. All resources devoted to destruction. |

**War Readiness Increase (checked monthly):**

| Condition                       | Readiness Change |
| ------------------------------- | ---------------- |
| Feud with rival union at 3+     | +1               |
| Overjarl ambition (personality) | +1 per season    |
| Rival union weakened            | +1               |
| Successful raid on rival        | +1               |
| Svarthird band recruited        | +1               |

**War Readiness Decrease:**

| Condition                         | Readiness Change |
| --------------------------------- | ---------------- |
| Bad harvest (food stores < 60d)   | -1               |
| Lost engagement                   | -1               |
| Cohesion drops below 3            | -1               |
| Overjarl dies or is incapacitated | -2               |
| Allthing peace treaty             | -2               |

### 18.9 Dark Arts Level

Tracks a union's investment in forbidden supernatural practices. Only the
Whispering Circle starts with a nonzero value.

**Dark Arts Scale (0-5):**

| Level | Capability                                           |
| ----- | ---------------------------------------------------- |
| 0     | None. Normal rune-craft only.                        |
| 1     | Seidr-worker consulted. Dream-sending possible.      |
| 2     | Active curse-carving. Nithing-poles deployed.        |
| 3     | Veil-thinning at specific sites. Fear weapons.       |
| 4     | Death-reading operational. Targeted assassinations.  |
| 5     | Invocation attempted. Drawing Veil-entities' notice. |

**Dark Arts Consequences:**

| Level | Risk                                                    |
| ----- | ------------------------------------------------------- |
| 1     | Practitioners show wear. Manageable.                    |
| 2     | Neighboring settlements hear rumors. Fear +1.           |
| 3     | Veil instability near seat. Random supernatural events. |
| 4     | Practitioners deteriorating. 10% chance of loss/month.  |
| 5     | Uncontrollable Veil breach possible. 20%/month.         |

**Dark Arts Interaction with Other Unions:**

- At level 2+, other unions gain a "fear_of_dark_arts" modifier
that reduces their willingness to attack directly (-1 war readiness when
considering direct assault on the dark-arts user).
- At level 3+, neutral settlements may refuse to trade with the
dark-arts user (feud +1 with all non-allied settlements).
- At level 5, the Veil response is uncontrollable. The invocation
may succeed (devastating weapon against enemies) or backfire (Veil breach
at the caster's own settlement, draugr incursion, permanent supernatural
contamination).

### 18.10 The Allthing (Annual Assembly)

**Timing:** Day 90-100 (after harvest, early Long Dark).

**Resolution:** The Allthing resolves accumulated political tension. All
unions and independent settlements send representatives.

**Allthing Actions (each leader gets 1-2 actions):**

| Action             | Effect                                        |
| ------------------ | --------------------------------------------- |
| Declare feud       | Formal feud +1 with named settlement          |
| End feud           | Feud -2 if both parties agree + weregild      |
| Propose alliance   | Roll Persuade vs. target's Wits to join union |
| Demand tribute     | Roll Intimidate vs. target's Will             |
| Trade deal         | Both settlements +10% trade income for year   |
| Marriage pact      | Feud -1 + cohesion +1 between families        |
| Declare outlawry   | Named person banned from all settlements      |
| Share intelligence | Reveal hidden info to allies                  |

**Allthing Intrigue:** The Pale Widow's agents operate during the Allthing.
Each Allthing, roll for whisper-agent success:

```text
intel_chance = dark_arts_level × 15 + widow_wit × 5
If success: Widow learns one hidden agenda or plan from target union
If critical: Widow can plant false information in target union
```

### 18.11 Seasonal Political Tick

The political simulation runs a major tick once per season (4 times per
year). Each tick:

1. **Economy:** All settlements run weekly ticks for the season
(aggregate). Food stores updated. Silver updated.
2. **Population:** Monthly population changes applied (3 months per
season for Long Dark, 2 months for Long Summer).
3. **Feuds:** All active feuds checked for escalation/de-escalation.
4. **Unions:** Cohesion checked. War readiness updated. Dark arts
consequences applied.
5. **Raids:** AI determines which settlements or unions launch raids
based on food shortage, feud level, and overjarl personality.
6. **Building:** Construction progress advanced.
7. **Training:** Fighter training progress advanced.
8. **Events:** Political hidden events checked and triggered.

### 18.12 Starting Political State (Year 312)

```yaml
# --- Starting Feuds ---
feuds:
  - pair: ["Grimholt", "Deepholm"]
    level: 2 # Hostile — Ordovast expanding toward Sigrun's territory
  - pair: ["Frostfjord Hollow", "Ashen Reach"]
    level: 1 # Tense — historical rivalry, Pale Widow scheming
  - pair: ["Grimholt", "Thornwall"]
    level: 1 # Tense — Ordovast wants Thornwall's pastureland
  - pair: ["Feldwick", "Three Wolves"]
    level: 3 # Blood-feud — second occupation this year

# --- Starting Unions ---
unions:
  - name: "The Iron Grip"
    overjarl: "Ordovast"
    seat: "Grimholt"
    type: military
    cohesion: 4
    war_readiness: 2 # Mobilizing
    dark_arts_level: 0
    members: ["Grimholt", "Raven's Perch", "Bleakwater Landing", "Moor's End"]

  - name: "The Fjord Compact"
    overjarl: "Sigrun"
    seat: "Deepholm"
    type: economic
    cohesion: 3
    war_readiness: 1 # Alert
    dark_arts_level: 0
    members: ["Deepholm", "Thornwall", "Kolvik", "Skaldhaven", "Ashmark"]

  - name: "The Whispering Circle"
    overjarl: "Pale Widow"
    seat: "Ashen Reach"
    type: covert
    cohesion: 2
    war_readiness: 1 # Alert
    dark_arts_level: 2 # Active curse-carving
    members: ["Ashen Reach", "Frostfjord Hollow", "Vargheim"]

# --- Independent Settlements ---
independent: ["Feldwick", "Stonebay Hamlet", "Icebreak"]

# --- Projected Timeline (encoded — use spoiler_codec.py to decode) ---
# SPOILER: 乙乥乡乲丠丳丱串丠乓乥乡乳乯乮丠丱为丠乕乮乥乡乳乹丠买乥乡乣乥丮丠乕乮乩乯乮乳丠乣乯乮乳乯乬乩乤乡乴乩乮乧丮
# SPOILER: 乙乥乡乲丠丳丱串丠乓乥乡乳乯乮丠串中丳为丠乏乲乤乯乶乡乳乴丠乢乥乧乩乮乳丠乢乯乲乤乥乲丠买乲乥乳乳乵乲乥丠乯乮丠乔乨乯乲乮乷乡乬乬丮
# SPOILER: 乙乥乡乲丠丳丱串丠乓乥乡乳乯乮丠临为丠乁乬乬乴乨乩乮乧丠仢亀五丠乬乡乳乴丠乣乨乡乮乣乥丠书乯乲丠乤乩买乬乯乭乡乣乹丮
# SPOILER: 乙乥乡乲丠丳丱丳丠乓乥乡乳乯乮丠丱为丠乏乲乤乯乶乡乳乴丠乭乡乲乣乨乥乳丠乩书丠乷乡乲也乲乥乡乤乩乮乥乳乳丠乲乥乡乣乨乥乳丠临丮
# SPOILER: 乙乥乡乲丠丳丱丳丠乓乥乡乳乯乮丠串中丳为丠乆乵乬乬丠乲乥乧乩乯乮乡乬丠乷乡乲丠乩书丠乮乯乴丠乡乶乥乲乴乥乤丮
# SPOILER: 乙乥乡乲丠丳丱丳丫为丠乐乡乬乥丠乗乩乤乯乷丠乤乡乲乫丠乧乡乭乢乩乴丠乴乲乩乧乧乥乲乳丠乩书丠乢乯乴乨丠乵乮乩乯乮乳丠乷乥乡乫乥乮丮
```

### 18.13 Political Subsystem Commands

All commands run from the `scripts/` directory.

```bash
# Show current political state
python village_politics.py status

# Show specific union
python village_politics.py union --name "The Iron Grip"

# Show feuds
python village_politics.py feuds

# Advance one season
python village_politics.py tick --season

# Advance one week (economy only)
python village_politics.py tick --week

# Run the Allthing
python village_politics.py allthing

# Execute a raid
python village_politics.py raid --from Grimholt --target Thornwall --force 20

# Show village economy
python village_politics.py economy --settlement "Deepholm"

# Show population demographics
python village_politics.py demographics --settlement "Grimholt"

# Show war readiness for all unions
python village_politics.py war-readiness

# Show dark arts status
python village_politics.py dark-arts --union "The Whispering Circle"

# Generate narrative summary of political season
python village_politics.py narrative --season 3
```

### 18.14 Outlawry and Settlement Interaction

This section governs how outlaw populations interact with settlements, how
settlements respond, and how outlawry creates political pressure and
narrative events.

See `data/culture/outlawry_system.yaml` for the full legal framework and
`data/culture/honor_contract_system.yaml` for mercenary-specific honor
mechanics.

#### 18.14.1 Outlaw Pressure (Settlement Stat)

Each settlement tracks `outlaw_pressure` (0-5), representing how many
outlaws operate nearby and how aggressively.

**Outlaw Pressure Scale:**

| Level | Name       | Effect                                       |
| ----- | ---------- | -------------------------------------------- |
| 0     | Clear      | No outlaw activity. Safe roads. Full trade.  |
| 1     | Watchful   | Occasional sightings. Travellers cautious.   |
| 2     | Threatened | Regular presence. Caravans hire guards.      |
| 3     | Pressured  | Active threat. Settlement considers tribute. |
| 4     | Besieged   | Siege-like pressure. Night markets flourish. |
| 5     | Controlled | Settlement partly controlled by outlaws.     |

**Pressure Change Triggers:**

| Event                            | Pressure Change |
| -------------------------------- | --------------- |
| New outlaw band forms nearby     | +1              |
| Outlaw band raided/destroyed     | -1              |
| Tribute paid to outlaws          | -1 (temporary)  |
| Mercenary patrol contracted      | -1              |
| Outlaw band grows (size +5)      | +1              |
| Winter onset (outlaws desperate) | +1 (seasonal)   |
| Amnesty granted to outlaw band   | -2              |

**Pressure Effects on Settlement:**

```text
trade_modifier = -(outlaw_pressure × 10)%
contract_availability = max(0, base_contracts - outlaw_pressure)
militia_readiness = min(5, base_readiness + outlaw_pressure)
night_market_chance = outlaw_pressure × 15%
```

#### 18.14.2 Settlement Responses

Settlements respond to outlaw pressure based on their resources and
political alignment.

**Response Options:**

| Response              | Cost (copper) | Effect                       |
| --------------------- | ------------- | ---------------------------- |
| Hire mercenary patrol | 50/week       | -1 pressure per week patrol  |
| Organize militia      | 20 (one-time) | -1 pressure, +1 feud risk    |
| Pay tribute           | 30/season     | -1 pressure, +1 outlaw rep   |
| Negotiate amnesty     | 0 (political) | -2 pressure, reputation risk |
| Ignore                | 0             | Pressure continues rising    |

**Amnesty Mechanics:**

A settlement headman may offer amnesty to select outlaws who agree to serve
the settlement (militia, labor, or specific tasks). This requires ting
approval.

```text
amnesty_chance = headman_persuade × 10 + settlement_desperation × 5
              - outlaw_severity × 15
# settlement_desperation = outlaw_pressure level
# outlaw_severity = 1 (lesser) or 3 (full)
# Success: outlaw integrated, pressure -2, community tension +1
# Failure: outlaw refuses or ting rejects, pressure unchanged
```

#### 18.14.3 Night Markets

Night markets are illegal trading sessions held outside settlement walls
after dark. They emerge when outlaw_pressure reaches 2+.

**Night Market Mechanics:**

```text
night_market_chance = outlaw_pressure × 15 + season_modifier
# season_modifier: winter +10, summer -5
# Checked weekly. On success: night market occurs.
```

**Night Market Effects:**

| Effect                | Mechanical Impact                                                       |
| --------------------- | ----------------------------------------------------------------------- |
| Rare goods available  | Items not in normal market (barrow loot, stolen weapons, foreign goods) |
| Disease risk          | 5% chance of camp sickness per visit                                    |
| Stolen property       | 20% of goods are stolen — legal risk                                    |
| Information           | Rumors, outlaw movements, contract leads                                |
| Settlement reputation | -1 if headman is seen tolerating it                                     |

**Band Interaction:**

A mercenary band may attend a night market. This provides access to rare
goods and information but risks reputation if discovered by the contracting
settlement. If the band is hired to STOP the night market, attending it is
a contract violation.

#### 18.14.4 Outlaw-to-Citizen Paths

An outlawed person can earn back legal status through:

| Path                      | Requirement                           | Difficulty |
| ------------------------- | ------------------------------------- | ---------- |
| Exceptional service       | Save a jarl's kin, fight in war       | Hard       |
| Bounty delivery           | Bring a worse outlaw's head to ting   | Moderate   |
| Jarl's petition           | Formal petition with ting approval    | Hard       |
| Weregild (lesser only)    | Pay full weregild + ting fee          | Easy       |
| Dead man's loophole       | Be declared dead, vanish, new name    | Moderate   |
| Time served (lesser only) | Survive 3-year exile without incident | Easy       |

#### 18.14.5 Outlaw-Related Events

The following events integrate with the existing event system. Event IDs
use the `EVT_OUTLAW_` prefix.

| Event ID               | Trigger                  | Effect                    |
| ---------------------- | ------------------------ | ------------------------- |
| `outlaw_raid`          | Pressure 2+, weekly roll | Settlement raided, -trade |
| `outlaw_parley`        | Pressure 3+              | Outlaws demand terms      |
| `outlaw_joins_band`    | Band near outlaw camp    | Recruitment opportunity   |
| `wolfshead_war`        | Two bands, same region   | Outlaw bands fight        |
| `night_market`         | Pressure 2+              | Illegal trade occurs      |
| `amnesty_offer`        | Pressure 4+              | Headman offers terms      |
| `merc_declared_outlaw` | Contract default + anger | Band declared outlawed    |

See `data/events/outlaw_events.yaml` for full event definitions.
