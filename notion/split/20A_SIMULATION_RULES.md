# Iron Ledger — Simulation Rules

<!-- notion-export:toc -->


## Iron Ledger Rules — Complete Simulation System

**Purpose:** This is the authoritative game system for the Rimevegr living world simulation. All mechanics are designed for computer resolution via Python scripts. No human dice rolling is needed.

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

Most people have Wyrd 1-2. Values of 4+ indicate genuine supernatural sensitivity. Characters with high Wyrd:

- Can attempt galdr (rune scribing) and seiðr (spirit communion)
- Sense the Hush before it falls
- Are more vulnerable to supernatural horror
- May receive visions (Wyrd-reading) but always at personal cost

---

## 2. Skills (0-5 Ranks)

Skills represent trained competency. Rank 0 means untrained (may still attempt if the action allows it, at heavy penalty).

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

If attack succeeds and defense fails: **hit landed**. If both succeed: compare margins (attacker wins ties). If attack fails: miss regardless of defense.

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

Undead are not impaired by wounds the way the living are. Set `is_undead: true` in the Fighter JSON to activate all of the following.

### Bleeding Immunity

Undead have no circulating blood. Any entity with `"bleeding"` in their `resistances` list accumulates zero bleed per round regardless of wound severity. Pass `resistances: ["bleeding", ...]` in the fighter JSON.

### Pain Immunity (Unfeeling)

Undead do not feel pain. Any entity with `is_undead: true` or `"unfeeling"` in their `traits` list has `wound_penalty = 0` at all times. Wounds reduce HP and can destroy them, but do not impair their attack or defense rolls.

### No Daze or Stagger from Wounds

Living fighters can be dazed (serious/critical head blow) or staggered (critical torso blow). Undead are immune to both — structural damage to the skull or chest does not shock a nervous system that no longer functions.

### Stance Logic

Undead don't self-preserve. They never adopt DEFENSIVE or BALANCED stance based on low HP or low stamina. MIG ≥ 6 → AGGRESSIVE; otherwise BALANCED. They press forward until destroyed.

### No Counter-Attacks

Undead without the `"combat_memory"` trait cannot execute Nachreisen counter-attacks. Their movements are purposeful but not tactically responsive — they advance, they do not exploit openings.

### Sim Trait Reference

| Trait tag             | Effect                                                            |
| --------------------- | ----------------------------------------------------------------- |
| `unfeeling`           | Wound penalty = 0 (no daze, no stagger, no attack impairment)     |
| `terrifying_presence` | Pre-battle WIL check; failure → opponent STAGGERED 2 rounds       |
| `combat_memory`       | Re-enables counter-attacks for undead with retained martial skill |
| `ancient_resilience`  | Incoming weapon damage halved (min 1)                             |

---

## 4.2 Weapon Reach and Distance

Every weapon has a physical length. A longer weapon creates a threat zone that a shorter-weapon fighter must penetrate to land a blow. The fight engine tracks a shared **distance band** between two combatants each round.

### Distance Bands

| Band | Name    | Approx. range | Optimal weapons              |
| ---- | ------- | ------------- | ---------------------------- |
| 0    | GRAPPLE | 0–40 cm       | unarmed, grapple entry       |
| 1    | CLOSE   | 40–90 cm      | dagger, seax, hand axe       |
| 2    | MELEE   | 90–150 cm     | sword, mace (default start)  |
| 3    | LONG    | 150–250 cm    | spear, long axe, great sword |

Default starting distance is **MELEE (2)** — standard fighting distance for two combatants who have closed to engage.

### Weapon Reach Table

| Weapon                | Reach tier | Min band | Max band | Foul band   |
| --------------------- | ---------- | -------- | -------- | ----------- |
| Unarmed / fist        | 0          | 0        | 0        | —           |
| Dagger, seax          | 1          | 0        | 1        | —           |
| Hand axe, mace        | 2          | 0        | 2        | —           |
| Sword                 | 3          | 1        | 2        | —           |
| Long axe, great sword | 4          | 2        | 3        | GRAPPLE (0) |
| Spear                 | 5          | 2        | 3        | CLOSE (1)   |

**Foul band** — if the distance drops to this band or below, the weapon is driven inside its own guard. The wielder can only strike with the haft: attack −30, damage base 3 (blunt), labelled `haft_only` in simulation output.

### Attack Penalties by Distance

```text
Too far  (distance > max_band): −20 per band above maximum
Too close (distance < min_band): −15 per band below minimum
Fouled   (distance ≤ foul_band): −30 attack, weapon_base overridden to 3
In range (min_band ≤ distance ≤ max_band): no modifier
```

**Key matchups:**

- Spear vs sword at LONG (3): spear −0, sword −20 → decisive spear advantage
- Spear vs sword at MELEE (2): both −0 → neutral fight
- Spear vs sword at CLOSE (1): spear fouled −30 (haft only), sword −0 → sword wins
- Dagger vs sword at MELEE (2): dagger −20 → dagger fighter must close to CLOSE first
- Unarmed vs sword at MELEE (2): fist −40 → must close two bands

### Distance Management Maneuvers

**STEP_IN** — Close distance by one band.

- As an action: costs 1 stamina.
- As a free reaction: triggered automatically when the opponent's attack-type maneuver misses and the defender's weapon reach is ≤ the attacker's. No stamina cost; does not consume the fighter's action slot.

**STEP_BACK** — Open distance by one band.

- As an action: costs 1 stamina.
- No free-reaction variant.

**SWITCH_WEAPON** — Draw a secondary carried weapon and stow the active one.

- Available only when the fighter has at least one weapon in their `secondary_weapons` list.
- Costs 1 stamina. Distance does not change.
- `weapon_type`, `weapon_base`, `weapon_speed`, `weapon_reach`, and `weapon_size` all update immediately to the new active weapon. The old weapon is pushed to the back of the secondary list.
- If the fighter is DISARMED when this maneuver resolves, the condition is cleared (drawing a backup counts as rearming).
- AI trigger A — **foul range**: when `reach_pen ≤ −30` (weapon fouled by distance) and a smaller secondary is available, the AI draws it instead of attacking blind.
- AI trigger B — **tight terrain**: when terrain is `tight` or `very_tight` and the active weapon is size ≥ 4, the AI switches to the best secondary of size ≤ 2 before attempting `STEP_BACK` or `GUARD`.
- Typical scenario: spearman rushed to CLOSE draws his seax rather than jabbing with the haft.

### Grapple Entry Distance Gate

All grapple initiation maneuvers (BROKARTOK, LAUSATOK, HRYGGSPENNA, TACKLE, and the basic GRAPPLE control maneuver) require `current_distance ≤ 1` (CLOSE or GRAPPLE). At MELEE or LONG range the entry is blocked — the fighter must STEP_IN first.

This means an unarmed fighter facing a swordsman at default MELEE distance must spend at least one action closing before a throw is possible.

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

Short weapons gain an attack bonus in tight/very_tight space. The dagger fighter or unarmed grappler is genuinely advantaged inside a burial mound.

### Stamina surcharge — per offensive/control action

| Space      | sz 0 | sz 1 | sz 2 | sz 3 | sz 4 | sz 5 |
| ---------- | ---- | ---- | ---- | ---- | ---- | ---- |
| free       | 0    | 0    | 0    | 0    | 0    | 0    |
| moderate   | 0    | 0    | 0    | 0    | +1   | +1   |
| tight      | 0    | 0    | 0    | +1   | +2   | +3   |
| very_tight | 0    | 0    | +1   | +2   | +3   | +4   |
| packed     | 0    | 0    | 0    | +1   | +2   | +2   |

Applies to attack, control, and grapple-entry maneuvers only; not to GUARD, STEP_IN, STEP_BACK, STAND.

### Special rules

**HEAVY_BLOW blocked in very_tight.** No room for the overhead arc in a barrow or low-ceiling cellar.

**STEP_BACK blocked in very_tight.** No exit in a dead-end tunnel or collapsed structure.

**Polearm (sz 5) in very_tight = haft-only.** The shaft cannot be levelled — same `haft_only` override as reach fouls: base damage 3, −60 attack modifier.

**Prone + large weapon.** A fighter on the ground adds an extra penalty per tier above sz 3: sz 4 (great sword, long axe) adds −15; sz 5 (spear) adds −30. Stacks with normal prone penalties and reach penalties.

**Friendly fire in packed/very_tight.** A large-weapon fighter (sz ≥ 4) who misses an attack in packed or very_tight space has a chance of clipping an ally on the backswing: 10 % at sz 4, 20 % at sz 5. Target is a random living ally. Damage is `weapon_base ÷ 2` (no defense roll — the ally had no warning).

**Auto-crowd in skirmish.** When `run_skirmish` starts with six or more total fighters and all carry `open` terrain, terrain is upgraded to `crowd` for all participants. Six people hacking at each other leave no clean swing room.

### Interaction with §4.2 reach system

Both penalty systems apply simultaneously and stack. A spear fouled by reach at CLOSE range and fighting in a `narrow` corridor accumulates both penalties. A dagger wielder closing at LONG distance incurs reach penalty but gains the tight-space bonus once the terrain is `narrow` — net penalty is smaller than in open ground.

---

## 4.4 Grappling and Glíma

### Awareness Model

Grappling replaces the flat `GRAPPLE` maneuver with a full positional sub-game. Once two fighters are locked together the fight becomes a series of opposed checks for dominant position, with each position unlocking a distinct menu of follow-up moves. Short weapons gain inside a grapple; long weapons become liabilities.

### Distance Gate

All grapple entry maneuvers require `current_distance ≤ 1` (CLOSE band or already at GRAPPLE range). Attempting a grapple entry from MELEE or LONG distance fails automatically. The AI is aware of this gate and will only attempt grapple entry after a `STEP_IN` has succeeded.

### Grapple Position State Machine

Once a grapple entry succeeds, both fighters are assigned a shared `GrappleState` object. The `position` field is one of nine values:

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

Position changes via opposed checks each round. `GrappleState` also tracks: `dominant` (fighter name or empty string), `position_round`, `ground` flag, `throat_seized`, `weapon_pressed`, `weapon_pressed_by`, `arm_locked`, and `choke_rounds`.

### A. Grapple Entry Maneuvers

These are the four ways to initiate a grapple. All require CLOSE or GRAPPLE distance. All are resolved against the same opposed check framework.

| ID  | Maneuver                          | Eng. attribute | Result on success                        | Special                                                     |
| --- | --------------------------------- | -------------- | ---------------------------------------- | ----------------------------------------------------------- |
| A1  | `BROKARTOK` — belt and thigh grip | MIG vs. NIM    | `dominant_clinch`                        | +10 if opponent wears a belt; -10 if no belt grip available |
| A2  | `LAUSATOK` — collar tie-up        | NIM vs. NIM    | `neutral_clinch` with B5 unlock          | Cannot be used if attacker carries a shield                 |
| A3  | `HRYGGSPENNA` — back-wrap         | MIG vs. MIG    | `rear_control` immediately               | Requires a prior feint success or opponent PRONE/DISARMED   |
| A4  | `TACKLE` — waist charge           | MIG (no skill) | both `PRONE`, attacker in `side_control` | -20 if attacker is armed; bypasses shield completely        |

Counter-checks on failure: BROKARTOK → wide-stance NIM drop; HRYGGSPENNA → sit-out MIG check. A successful counter returns the position to `neutral_clinch` rather than giving the attacker the entry.

### B. In-Grapple Positional Moves

All require an active `GrappleState` on both fighters. All cost stamina. Each resolves as an opposed check and may advance or regress the `GrappleState.position` field.

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

Available only to fighters with `Brawl rank ≥ 3` or a glíma-specific trait (`glima_brokartok`, `glima_lausatok`, `glima_hryggspenna`).

| ID  | Maneuver                     | Requires                      | Attribute   | Stamina | Outcome                                                                  |
| --- | ---------------------------- | ----------------------------- | ----------- | ------- | ------------------------------------------------------------------------ |
| C1  | `GLIMA_LAS` — back heel trip | `dominant_clinch`             | NIM         | 3       | Opponent PRONE and STAGGERED; attacker stays standing free               |
| C2  | `SNUNINGUR` — hip rotation   | `dominant_clinch`, low stance | MIG/NIM avg | 4       | 1d8 damage, PRONE; full rotation throw                                   |
| C3  | `BEINHNYKKUR` — leg snap     | `side_control`                | NIM         | 3       | Joint lock; opponent surrenders or takes permanent tendon wound          |
| C4  | `HNAKKATAK` — nape takedown  | any clinch                    | NIM         | 2       | PRONE + DAZED 2 rounds; requires opponent with long hair or exposed nape |

### D. Dirty Tactics

Dirty tactics do not require an active grapple. Range is melee contact (arm's reach) for all of them. Every dirty tactic triggers a `WIT`-based counter check: a target with `WIT ≥ 6` gets a free interrupt check at difficulty 55% to partially negate the action.

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

**Hair and beard requirement for hair-based tactics:** The fighter record includes a `hair` field (`short`, `medium`, `long`). D6 and C4 both check this field; they fail automatically against a fighter with `hair == "short"`.

### E. New Conditions

| Condition       | Attack mod | Defense mod | Cleared by                                             |
| --------------- | ---------- | ----------- | ------------------------------------------------------ |
| `CHOKED`        | —          | —           | Grapple break; attacker releases; 4 HP drain per round |
| `ARM_LOCKED`    | -40        | 0           | SHOVE success or forced break                          |
| `PINNED`        | -50        | -30         | MIG opposed check at -10 for bottom fighter            |
| `BLINDED`       | -30        | -30         | Spend one action to clear, or 1d3 rounds expire        |
| `BLEEDING_NOSE` | 0          | 0           | Clears after combat; no mechanical healing needed      |
| `PAIN_SHOCK`    | -10        | -10         | Automatic (1 round only)                               |

`CHOKED` additionally blocks speech and commands. Undead fighters are immune to `CHOKED` — they have no functioning airway.

### F. Weapon Asymmetry in Grapple

A fighter's weapon type affects how willing the AI is to enter a grapple (stored in `GRAPPLE_WEAPON_MODIFIERS`) and how effective weapon-based in-grapple attacks are:

| Weapon                 | AI grapple willingness | In-grapple attack mod |
| ---------------------- | ---------------------- | --------------------- |
| Unarmed                | +0                     | +20                   |
| Dagger / seax          | +10                    | +15                   |
| Hand axe               | -5                     | 0                     |
| Mace                   | -5                     | 0                     |
| Sword (one-hand)       | -15                    | -10                   |
| Spear                  | -30                    | -20                   |
| Long axe / great sword | -40                    | -30                   |

Long weapons at -30 or -40 willingness will effectively never initiate a grapple unless the AI is already in one from a reactive entry.

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

- `grapple_state: Optional[GrappleState]` — shared state object; `None` when not grappling.
- `brawl_skill: int` — `Brawl` ranks (0–5); used in all grapple opposed checks and gates C-tier finishers at rank ≥ 3.
- `glima_mode: str` — empty string or one of `"brokartok"`, `"lausatok"`, `"hryggspenna"` to indicate training style.
- `wants_nonlethal: bool` — if `True`, AI prefers submission moves (B12, C3, B11) over damaging ones.
- `hair: str` — `"short"` | `"medium"` | `"long"`; gates D6 and C4.

---

## 4.5 Surprise and Awareness

### Overview

Awareness determines whether a fighter enters combat with full faculties or is caught mid-thought with their sword still on their hip. It is a pre-combat state, not a condition that develops during a fight — though darkness and loud ambient noise can prolong effective unawareness across multiple rounds.

### Fighter Fields

- `aware: bool` — defaults to `True`. Set to `False` when the fighter does not know combat has started (ambush, wake-up attack, shot from concealment, etc.).
- `ambient: list` — list of `AmbientCondition` string values active for this fighter at fight start. Independent per fighter: one side may be in darkness while the other is not.

### AmbientCondition Values

| Value      | Description                                                                                                         |
| ---------- | ------------------------------------------------------------------------------------------------------------------- |
| `darkness` | Fighter cannot see. Approach from any direction goes undetected. Applies `BLINDED` for the duration.                |
| `noise`    | Loud ambient sound (waterfall, forge, crowd). Flanking and rear approaches cannot be heard. Does not apply BLINDED. |
| `obscured` | Fog, heavy rain, dense smoke. Vision is degraded but not absent. -10 attack and defense.                            |

### The Surprise Round

When any fighter has `aware=False` at fight start:

1. The unaware fighters receive the `UNAWARE` condition (1 round duration).
2. The fight log records a `"type": "surprise_round"` pre-battle entry listing which fighters are unaware.
3. In round 1 initiative: all fighters with `UNAWARE` are sorted **after** all aware fighters regardless of NIM or WIT score.
4. While `UNAWARE` is active:
- Defense modifier: -50 (the fighter is not set for combat).
- No counter-attacks are available (they cannot react to a defended hit).
- No free reactions (step-in after long-weapon miss is blocked).
- Only `GUARD` is available as a forced maneuver — the fighter cannot choose any offensive action.
5. At the end of round 1 the `UNAWARE` condition expires automatically via the standard `tick_conditions()` pass.

### Darkness (`ambient: ["darkness"]`)

A fighter with `"darkness"` in their `ambient` list at fight start is marked `BLINDED` with a persistent duration (9999 rounds) immediately before round 1.

`BLINDED` effects: -30 attack, -30 defense, no visual targeting.

The condition persists until explicitly cleared by the caller (e.g., a torch is lit, dawn breaks). Clearing is done by removing `BLINDED` from the fighter's condition list and removing `"darkness"` from `ambient`.

**Interactions:**

- A fighter in darkness who is also `UNAWARE` has both -50 (UNAWARE, round 1 only) and -30 (BLINDED, ongoing) stacked on their defense.
- Undead fighters with `"no_eyes"` in their traits are immune to BLINDED from darkness — they do not rely on sight.

### Noise (`ambient: ["noise"]`)

Noise does not apply BLINDED. Its mechanical effect is narrative: the caller should treat any `UNAWARE` state caused by a rear approach as valid even when the target has high WIT, since the target never heard the approach. The system itself does not add a penalty for `noise` alone — that is handled by the `aware=False` + `UNAWARE` flow above.

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

The simulation does not auto-roll awareness checks — that is handled at the scenario layer. The caller decides whether to set `aware=False` based on:

- Whether the fighter could plausibly have detected the threat (sight, sound, smell, prior warning).
- Active `ambient` conditions restricting detection channels.
- Traits: a fighter with `"combat_memory"` or `"vigilant"` in their traits list may be granted `aware=True` even in noise/darkness at the caller's discretion.

A WIT-based check at difficulty 55 is the recommended gate: roll WIT × difficulty; succeed → `aware=True`; fail → `aware=False`.

---

## 4.6 Animal Combat Mechanics

Animal traits are expressed through `sim_traits` and evaluated directly in `combat_sim.py`.

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

Supernatural entities extend standard combat resolution with trait-driven hooks at pre-battle, attack, defense, and end-of-round steps.

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

- Add trait packages such as `relentless_advance`, `ancient_fury`, or `desperate_fury`.
- Apply temporary or persistent stat boosts.
- Emit narrative state transition with `[BLOODIED]` lines.

## 4.9 On-Death Dispatch

When a fighter drops, configured `death_effects` are dispatched once per fighter and logged as `[ON-DEATH]` events.

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

Prompt 5 adds a battlefield layer above individual duels. In medium and large skirmishes, fighters carry formation state, cohesion, morale, and frontage pressure. These values are updated every round and can break a line even before body count decides the fight.

### Formation State Fields

Each fighter in skirmish mode may carry:

- `formation`: `shield_wall | loose_line | wedge | broken`
- `cohesion_score`: `0-100`
- `morale_score`: `0-100`
- `frontage_pressure`: `0-100`
- `rout_state`: `steady | wavering | rout`
- `is_commander`: explicit commander marker; commander-like traits also count (`rally_allies`, `veteran_eye`)

If formation is not supplied, the engine defaults spear/shield-heavy fighters toward `shield_wall` and other fighters toward `loose_line`.

### Formation Attack and Defense Relief

The formation layer is primarily defensive. The simulator currently uses the following relief values while calculating line pressure:

| Formation   | Defense Relief | Attack Bias |
| ----------- | -------------- | ----------- |
| shield_wall | +8             | -2          |
| loose_line  | 0              | 0           |
| wedge       | -3             | +4          |
| broken      | -10            | -6          |

These do not replace weapon-level combat math. They shape whether a fighter holds position, starts wavering, or breaks.

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

$$ \text{pressure} = \text{base pressure} - \text{formation relief} - \text{depth relief} + \text{shock modifiers} $$

Base pressure formula:

$$ \text{base pressure} = (\text{enemy\_standing} - \text{self\_standing}) \times 8 + \max(0, \text{attackers} - 1) \times 12 $$

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

The line state changes automatically once cohesion or morale falls past thresholds:

| Condition                                    | Result                                                      |
| -------------------------------------------- | ----------------------------------------------------------- |
| `cohesion_score < 15` or `morale_score < 15` | `rout_state = rout`, `formation = broken`                   |
| `cohesion_score < 30` or `morale_score < 30` | `rout_state = wavering`; shield wall degrades to loose line |
| otherwise                                    | `rout_state = steady`                                       |

When a fighter newly enters `rout`, the simulator logs a `breakpoint` event.

### Morale Contagion and Break Cascade

Prompt 5 includes local-to-wide break spread. When one fighter or segment breaks, nearby allies may suffer `morale_shock`.

Current cascade chances:

- base contagion chance: `18%`
- if the nearby ally is already `wavering`: `+8%`

On contagion (if ally morale > 20):

- ally morale is reduced by `20`
- ally becomes `wavering` if previously `steady`

Note: morale reduction only applies if the ally's morale is already above 20.

This is the main mechanism by which one weak point can turn into a wider collapse.

### Special Shock Sources

Additional pressure can come from:

- commander down on that side: `+12` pressure
- routed allies already visible: `+6` pressure per routed ally
- heavy local attacker concentration: derived from outnumber and multi-attack penalty
- `terrifying_presence` on the enemy side: `+4` pressure

These do not create a separate morale subsystem. They are folded into the same frontage pressure calculation.

### Rout Behavior in Skirmish Mode

Fighters already in `rout` stop behaving like normal duelists.

- They take `rout_action` instead of standard attack resolution.
- If a commander is still active, they have an `organized_withdrawal` chance of `45%`.
- Otherwise they `panic_flee`.

If no organized withdrawal occurs:

- `cohesion_score -= 4`
- `morale_score -= 3`

Steady allies may screen retreating units with a `rearguard_cover` event at `30%` chance.

### Pursuit and Overextension

When a non-routing attacker lands a hit on a defender already in `rout`, the engine may enter a pursuit branch.

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

- **Overextended pursuit**: attacker becomes `STAGGERED`, loses cohesion, and the log records `pursuit_event: overextended`.
- **Clean pursuit**: target takes bonus torso damage; mounted pursuit against routed foot is stronger and adds horse fatigue.
- **Held line**: attacker does not chase.

This means pursuit is useful but not automatically correct.

---

## 4.12 Missile Combat, Volleys, Suppression, and Ammo Discipline

Prompt 8 adds a pre-melee missile phase to skirmish combat. Missile units are no longer just melee fighters with ranged flavor; they have ammunition, fire mode, weather sensitivity, suppression output, and formation-aware targeting.

### Missile-Capable Fighters

The simulator treats a fighter as missile-capable when any of the following is true:

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

In `run_skirmish`, missile attacks resolve before normal stance, maneuver, and melee action sequencing each round.

This means volleys can wound, suppress, or kill before the melee order is even rolled.

### Ammunition and Resupply

Ammo is spent per fire mode:

- aimed shot: `1` ammo
- volley fire: `2` ammo

When a missile fighter reaches `ammo_current <= 0`, they may attempt one conservative in-fight resupply if `resupplies_used < 1`.

Current resupply chance:

- `18%`

Recovered ammo:

- `2` shots for unspecified missile capacity (`ammo_max <= 0`), or
- `min(2, max(1, ammo_max // 4))` for defined capacity (at least 1 shot, up to 2 total)

If no resupply succeeds, the engine logs `missile_ammo_empty` and the fighter stops contributing missile fire.

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

**Low Ammo Definition**: `ammo_current <= max(1, ammo_max // 5)` (one-fifth of capacity or less)

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

The system prefers to harass packed or pressured enemies while still recognizing that shielded fronts are harder to hurt.

### Formation and Shield Interaction

Prompt 8 explicitly interacts with Prompt 5 formation state.

- steady `shield_wall` reduces missile damage to `45%` of normal frontal lethality
- exposed or pressured targets (`frontage_pressure >= 60` or not steady) take `×1.25` damage

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

Each attack event records mode, ammo left, hit/miss, and whether suppression was applied.

---

## 4.13 Mounted Combat, Anti-Cavalry Counters, and Dismount Flow

Prompt 9 adds mounted combat as a skirmish subsystem rather than a flat stat bonus. It models charge windows, horse control, anti-cavalry setups, forced dismounts, and pursuit mobility.

### Scenario Gate: `horses_allowed`

Mounted logic is not globally active.

`run_skirmish(..., horses_allowed=False)` is the default.

When `horses_allowed` is false:

- all fighters are normalized to `mounted = False`
- horse fatigue and charge cooldown are cleared
- dismount vulnerability state is cleared

This is deliberate. Normal barrow and camp fights do not assume horses. Mounted rules only activate in combats explicitly marked as horse-allowed.

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

A mounted fighter may attempt a charge only if all of the following are true:

- `mounted = True`
- `charge_cooldown == 0`
- fighter is not `GRAPPLED`
- fighter is not `PRONE`
- `mount_condition != panicked` (panicked mounts can attempt dismount instead)
- horses are allowed in the scenario

**Panicked Mount Logic**: If mount is panicked and rider stability < 35, there is a 35% chance the mount will throw the rider before charge is attempted (`mount_panicked` dismount).

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

This is why cavalry spikes hard in open ground but loses value in forests, ruins, barrows, and packed melee.

### Anti-Cavalry Counters

Anti-cavalry defense is available through:

- braced anti-cavalry weapons (`spear`, `pike`, `halberd`, `poleaxe`, `staff_spear`), combined with `DEFENSIVE` stance or `GUARD`
- stake or obstacle terrain markers

Brace success chance is currently:

$$ ext{brace chance} = 42 + 5 \times \text{weapon skill} + \text{stance/stake bonuses} $$

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

If rider stability drops to `≤ 22`, forced dismount occurs (`mount_panic_throw`).

### Forced Dismount

When dismounted by brace, panic, or failed stability, the simulator:

- sets `mounted = False`
- sets `mount_condition = wounded`
- reduces `rider_stability`
- sets `dismount_vulnerability_rounds = 2`
- applies `STAGGERED` for 1 round

The action log records `dismount_event`.

### Post-Dismount Vulnerability

While `dismount_vulnerability_rounds > 0`, incoming attackers gain an additional `+8` attack modifier against that fighter.

This models the scramble to recover footing and weapon control after being thrown or forced down off the horse.

### Horse Fatigue and Recovery

At end of round:

- `charge_cooldown` ticks down by `1`
- `dismount_vulnerability_rounds` ticks down by `1`
- `mount_fatigue` recovers slowly (`-3` per round)

If `mount_fatigue >= 70` and the horse was still steady, the engine marks the mount as `wounded`.

Panicked mounts may settle back to `steady` or `wounded` depending on fatigue and recovery chance.

### Mounted Pursuit

Mounted fighters gain a meaningful edge when pursuing routed foot units.

In the pursuit branch:

- mounted attacker vs routed foot gains additional pursuit chance
- successful clean pursuit deals extra damage
- each mounted pursuit adds horse fatigue
- repeated pursuit chains increase overextension risk

This keeps cavalry strong in open-field collapse phases without making it free or endless.

### Horse Sheet

The existing mounted fields are enough for simple skirmish gating, but a full campaign horse should carry a separate horse sheet. Use this when a mount matters across scenes, weeks, breeding, resale, or injury recovery.

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

Breeds are not cosmetic. Each breed defines the likely baseline, common traits, and common failure mode.

| Breed               | Speed | Wind | Foot | Nerve | Load | Sense | Typical Traits               | Common Weakness                  |
| ------------------- | ----- | ---- | ---- | ----- | ---- | ----- | ---------------------------- | -------------------------------- |
| Rimefjord pony      | 2     | 4    | 4    | 4     | 3    | 4     | cold_hardy, calm_mouth       | lacks burst                      |
| Moor-runner         | 5     | 4    | 3    | 2     | 2    | 3     | fast_break, long_stride      | stressy, feed-sensitive          |
| Pine-cob            | 2     | 3    | 3    | 5     | 5    | 3     | dead_pull, patient           | poor acceleration                |
| Spine pony          | 2     | 4    | 5    | 4     | 3    | 4     | cliff-footed, sparse-forager | dislikes crowd crush             |
| Southblood warhorse | 4     | 3    | 3    | 3     | 4    | 2     | charge_mass, tall_frame      | cold-soft, costly, hotter temper |

Breed modifies acquisition, breeding value, and task success. A breed is the base package; individuals still vary by traits, training, and care.

### Horse Moods

Mood is the short-horizon mental state of the horse. It changes faster than condition and should be checked whenever the horse is hungry, tired, afraid, mishandled, or working with a bad rider.

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

Campaign horses should normally track both the current condition and the existing combat fields `mount_condition`, `rider_stability`, and `mount_fatigue`. The combat layer is a short-term slice of the wider horse sheet.

### Horsing Checks

Use the normal skill-check formula from §1, but horses use a defined horse-and-rider resolution block:

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

If the system is not using a distinct `ride/horsing` skill, substitute the best relevant existing skill shown above and apply `-10` if the character has never worked horses seriously.

### Horse Tricks

Tricks are trained, repeatable mount behaviors. A horse may know `1` basic trick per point of `sense`, plus one additional trick if it is prime-aged and has a dedicated rider.

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

Failed trick checks do not mean the horse forgets the trick. They mean the current rider, mood, terrain, or pressure broke execution.

### Breeding and Inheritance

Breeding should create tendencies, not certainty. Use the breed template as the base, then inherit bloodline tags and one or two standout stats.

Foal generation:

1. Choose base breed. Dam breed if same-breed pairing or local mixed stock. `50/50` between dam and sire for deliberate cross-breeding.
2. Inherit one strong stat from each parent. On each inherited stat, foal gets parent value or parent value `-1`.
3. Inherit two `bloodline_tags`. One from dam, one from sire.
4. Roll one foal quirk. `steady_mouth`, `late_maturing`, `bad_feeder`, `crowd_shy`, `ice-wise`, `hard_keeper`, `throws_big`, `throws_small`.
5. Adjust for care. Poor winter during foal year: `-1 wind` or `-1 load`. Excellent care and sound handling: `+1 sense` or remove one bad quirk.

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
- repeated `night_spook` or `crowd_sour`: heavy discount unless sold to isolated civilian work

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

These are the main log hooks for narrative rendering and debugging of the mounted subsystem.

---

## 4.14 Dogs, Working Checks, and Breeding

Dogs use the same campaign-asset logic as horses, but on a smaller and faster scale. They mature sooner, eat less, bond harder, and fail more often through handling mistakes than through pure expense. Use a full dog sheet whenever a working dog matters across scenes, watches, hunts, tracking, war-dog use, breeding, resale, or repeated camp play.

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

Breed matters to acquisition, training ceilings, working role, and breeding value. Dogs are less pure-bred in practice than horses, but the lines still produce recognizable packages of strengths and failures.

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
- blood in the air, pack chorus, or active pursuit: toward `eager` or `pack_hot`
- barrow phenomena, corpse-stink, impossible silence: toward `watchful` or `shaken`

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

Use the normal skill-check formula from §1 through this dog-and-handler resolution block:

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

If the system is not using a distinct `dog-handling` skill, substitute the best relevant existing skill and apply `-10` if the character has little real dog experience.

### Dog Tricks

A dog may know `1` basic trick per point of `sense`, plus one additional trick if it is prime-aged and has a stable bond handler.

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

Failed trick checks mean the current fear, distraction, handler, or ground broke execution. They do not mean the dog forgot the trick.

### Dog Breeding and Inheritance

Breeding dogs should create working tendencies, not guaranteed outcomes. The line matters, but so do handling, culling, and early use.

Pup generation:

1. Choose base breed. Dam breed if same-line pairing or common mixed stock. `50/50` between dam and sire for deliberate crossing.
2. Inherit one strong stat from each parent. On each inherited stat, pup gets parent value or parent value `-1`.
3. Inherit two `bloodline_tags`. One from dam, one from sire.
4. Roll one puppy quirk. `sure_returner`, `late_head`, `cold_nose`, `kennel_sour`, `loud_mouth`, `soft_mouth`, `hard_keeper`, `fight_picker`.
5. Adjust for raising. Good handler and steady kennel: `+1 sense` or remove one bad quirk. Hard winter or bad feeding: `-1 grit` or `-1 speed`.

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
- repeated `pack_hot` or `stranger_sour`: discount unless sold for kennel war work
- bitch with three litters of working pups: major local prestige even if plain

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
