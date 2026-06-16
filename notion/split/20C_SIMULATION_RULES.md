# Iron Ledger — Simulation Rules

<!-- notion-export:toc -->


## 11. Norse Magic System

Magic is rare, feared, and always costs something. Only characters with Wyrd 3+ can reliably attempt magical actions. Three traditions:

### Galdr (Rune Scribing)

Carving runes and speaking words of power. The most accepted form of magic, though still viewed with suspicion.

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

- Rank 1-2 effects: 1 Willpower + 1-2 stamina (tiring but not yet life-burning)
- Rank 3 effects: 2 Willpower + 4 stamina + blood equal to the greater of 3 HP or 10% of Max HP (rounded up)
- Rank 4 effects: 3 Willpower + 6 stamina + blood equal to the greater of 6 HP or 22% of Max HP (rounded up) + material component
- Rank 5 effects: 5 Willpower + 8 stamina + blood equal to the greater of 9 HP or 33% of Max HP (rounded up) + rare material
- These costs are paid on success or failure. Galdr is not a free spell slot; it is exertion, blood loss, and shortened life.

**Typical working example:** a competent galdr-worker with 25 Max HP and 23 Max Stamina pays about 3 HP and 4 stamina for rank 3 work, 6 HP and 6 stamina for rank 4 work, and 9 HP and 8 stamina for rank 5 work.

**Failure Consequences (d100 on failed galdr):**

| Roll   | Consequence                                                  |
| ------ | ------------------------------------------------------------ |
| 01-40  | Rune fizzles. Willpower cost still paid.                     |
| 41-70  | Backlash: 1d6 damage to carver, rune cracks.                 |
| 71-90  | Rune inverts: opposite of intended effect.                   |
| 91-100 | Something notices. The Hush falls. Wyrd check or gain dread. |

### Seiðr (Spirit Talking)

Communion with the dead, land-spirits, and hidden presences. Deeply stigmatized for men (considered ergi / unmanly). Women practitioners (völvur) are feared but respected.

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

Casting lots, reading entrails, interpreting omens. The most common and least stigmatized form of supernatural practice.

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

Where Section 11 defines what magic can do and Section 18 defines how politics works, this section governs the intersection: how magical practice creates, distorts, and arbitrates political power at the ting and Allthing.

#### 11.8.1 Ward-Rights at the Allthing

Ward-right is a political appointment determining which union's galdr-worker wards the Allthing stones for the assembly's duration. The ward-holder controls magical safety for all participants.

**Appointment:** Resolved on Allthing Day 1 (see 18.10), before any other Allthing actions are taken.

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
3. Ties broken by highest `galdr_worker_rune_lore`, then by lot (d100, high wins).

**Effects of Holding Ward-Right:**

- Ward-holding union gains **+1 modifier** to all Allthing action rolls (see 18.10 Allthing Actions table).
- Other unions may challenge the appointment. Challenge requires a Persuade check: `challenge_chance = (Wits × 5) + (Persuade × 10)
+ 15` DC = `ward_influence` of current holder. On success, the challenger's nomination replaces the holder.

**Ward Sabotage (requires Dark Arts level 3+):**

- Sabotaging union rolls against the ward: `sabotage_chance = dark_arts_level × 15 + saboteur_rune_lore × 10`
- If `sabotage_chance` roll succeeds: wards collapse. All Allthing action rolls take a **-2 modifier** for the remainder of the assembly. Sabotaging union gains **+2** to `intel_chance` (see 18.10).
- If sabotage is detected (opposing galdr-worker rolls `galdr_chance` per Section 11): sabotaging union loses 1 reputation (Section 13) and ward-holding union gains +1 to all remaining rolls for the session.

#### 11.8.2 Seiðr Testimony Rules

Whether seiðr testimony — a völva's report of what the dead or spirits reveal — is admissible at a ting or the Allthing varies by union law.

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

Any party to a dispute may invoke "living witness over dead witness," demanding that testimony from living freemen overrule seiðr testimony. Invoking this costs the challenger **1 reputation** (Section 13). If invoked, seiðr testimony weight is halved (round down) for that dispute only.

#### 11.8.3 Curse Arbitration

When a jarl deploys a niding-pole (see galdr Rank 4, Section 11) against another and the target brings the matter to the ting, the ting must rule on the curse's legitimacy.

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

If the curse used blood-galdr (another person's blood as material component): automatic niding ruling regardless of `curse_legitimacy` score. Carver declared outlaw. Feud +3 (Section 18.6) between carver's settlement and target's settlement. Dark Arts level of carver's union increases by 1 (Section 18.9).

#### 11.8.4 Dark Arts Definitions and Boundaries

This section provides precise mechanical classification of magical practices referenced by Sections 11, 18.9, and 18.10.

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

The mechanical line between legal seiðr consultation and forbidden death-seiðr is determined by the Spirit-lore rank used:

- **Rank 1-3 effects** (sense, speak, commune): the dead are asked. This is counsel. Legal or tolerated.
- **Rank 4+ effects** (command, bind): the dead are compelled. This is coercion. Classified as death-seiðr (forbidden).

**Proving Dark Arts Accusations at the Allthing:**

Any Dark Arts accusation raised at the Allthing (Section 18.10) requires proof. Proof requires a seiðr-worker willing to testify under the rules of 11.8.2. The accusing union must produce a seiðr-worker whose `testimony_weight` (per 11.8.2) meets the Compelling threshold (31+).

This creates a structural dependency: proving forbidden magic requires the very tradition the accusation targets. Unions that forbid seiðr testimony (Iron Grip) cannot bring Dark Arts accusations without first securing a seiðr-worker from another union — a political transaction with its own costs.

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

Magical practice extracts a cumulative physical toll. This section tracks when practitioners begin to lose capability due to years of use. Degradation is tracked per practitioner, not per tradition.

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

- **Galdr:** Hands tremble, fingers stiffen, inscription lines waver. Old rune-carvers cannot hold a chisel steady in cold weather.
- **Seiðr:** Trance recovery extends from hours to days. Memory gaps after sessions. Confusion between spirit-speech and waking speech.
- **Wyrd:** Readings blur — the lots say too much or nothing at all. The reader cannot distinguish signal from noise.

**Named Character Degradation Status:**

| Practitioner        | Tradition    | Stage     | Notes              |
| ------------------- | ------------ | --------- | ------------------ |
| Ash (Black Axes)    | Galdr        | Pre-onset | ~10 years active   |
| Dalla (Black Axes)  | Seiðr        | Pre-onset | ~8 years active    |
| Petra (Black Axes)  | Wyrd-reading | Pre-onset | ~5 years active    |
| Thorne (Black Axes) | Galdr (life) | Pre-onset | Rune craft only    |
| Audun (Skaldhaven)  | Galdr        | Early     | Hands declining    |
| Ragnhild (Icebreak) | Seiðr        | Mid       | Trance recovery 2d |

See `08_MAGIC_OF_RIMEVEGR.md` §8 (Practitioner Lifecycle) for full narrative context and `data/magic/practitioners.yaml` for canonical practitioner data.

### 11.10 Rune-Script Construction Rules

This section governs galdr rune-scribing: how scripts are built, how many runes can be combined, how the voice (kvæði) modifies the effect, and how rune-blight accumulates. Used by `galdr_simulation.py`.

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

The face (dagmál or náttmál) is determined by carver intent plus environmental pressure:

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

If `face_drift_chance > 50`, the rune defaults to náttmál regardless of carver intent. The carver may force dagmál with a Will check:

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
- Duplicate runes in a script are forbidden (backlash automatic).
- A rune may fill multiple slots if its meaning supports both (e.g., Kaun as Force and Consequence). This costs +5 difficulty per dual-slotted rune.

#### 11.10.4 Kvæði (Voice-Chant) Modifiers

The spoken chant modifies the script's effectiveness, but it now also drains the body that carries it:

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
- At or below 25% Max Stamina: the black-tongue threshold is reached. The narrative effects of singing unlock even on a successful working — voices deepen, listeners become uneasy, animals balk, and the carver takes -10 to calm social interaction until properly rested.
- Below 0 stamina: every negative stamina point immediately costs 1 HP. This always unlocks the dark effects of singing.
- If HP reaches 0 while the galdr-worker is still singing, the result is **Divine Stroke** rather than ordinary collapse.

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

Blight tracks cumulative rune damage to the galdr-worker. It is a persistent value, not a per-session cost.

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

Permanent protections are not free once carved. While a protection remains active, the galdr-worker loses Max HP equal to that protection's rank.

```text
protection_tax = protection_rank
current_effective_max_hp = base_max_hp - sum(active_protection_ranks)
```

- A rank 3 village ward costs -3 Max HP while it stands.
- A rank 4 perimeter or mine-ward costs -4 Max HP while it stands.
- A rank 5 great barrier or ancient seal costs -5 Max HP while it stands.
- These taxes stack. Galdr-workers maintaining multiple village protections become visibly sickly, weak, and hard to mistake for healthy men.
- If total reserve tax reaches 25% or more of base Max HP, the practitioner counts as physically drawn even when unwounded.
- When a protection is destroyed, exhausted, or removed, its Max HP tax lifts immediately. The galdr-worker feels the rupture at once and knows a ward has been lost somewhere, but not which one without investigation.

**Bind-rune failure (d100 on failed bind attempt):**

| Roll   | Consequence                                                                                           |
| ------ | ----------------------------------------------------------------------------------------------------- |
| 01-30  | Fizzle. Materials wasted. Willpower cost paid.                                                        |
| 31-60  | Partial bind. 1 rune activates, others inert.                                                         |
| 61-80  | Inverted bind. All runes activate in náttmál.                                                         |
| 81-95  | Backlash. 2d6 damage, +3 blight.                                                                      |
| 96-100 | Catastrophic. Bind explodes. 4d6 damage radius 10ft. All runes activate simultaneously, uncontrolled. |

#### 11.10.7 Soulbane Interaction Table

When a galdr-worker has undergone one or more soulbanes (see Chapter 14 / `08_MAGIC_OF_RIMEVEGR.md` Rune-Blight section):

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

Moving the band toward a Named Man's personal Agenda: +1 loyalty. Ignoring it for 30+ days: -1 loyalty per month.

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

Contracts available depend on reputation, location, season, and current political conditions. Generated by `contracts.py`.

### Feud Track (0-4)

Tracked per settlement or faction. Increased by tribute, atrocity, broken contracts. Decreased by time, weregild payment, or service.

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

All secret information is encoded in CJK characters using `scripts/spoiler_codec.py` before being written to any public-facing file.

### What Gets Encoded

- Future events from the calendar
- Named Men betrayal plans and secret agendas
- NPC hidden motivations
- Rival band movements and plans
- Wyrd-reading results not yet revealed in narrative
- Contact network secrets
- Campaign arc progression triggers

### Storage Location

Hidden data is stored in `data/hidden/` as `.txt` files containing CJK-encoded text. Decode as needed during narrative development or play.

### Protocol

1. AI determines secret information during simulation
2. AI runs: `python hidden_info.py encode "<secret text>"`
3. AI writes encoded output to appropriate hidden data file
4. During play, AI runs: `python hidden_info.py decode "<chinese text>"`
5. AI uses decoded information to inform narration without revealing source

---

## 17. Life Skills and Practical Knowledge

Every member of the band carries a baseline of practical knowledge — the ambient competence of people who survive outdoors, fight, and travel for a living. This section defines what characters can plausibly do without a skill check, what requires a check, and what specialist knowledge individual members carry beyond the baseline.

### Every Man Baseline (No Check Required)

Any band member can do these in normal conditions. Checks only apply under extreme stress, injury, or hostile conditions:

- Light a fire in dry conditions (wet/wind: Shelter check).
- Sharpen his own weapons and perform basic maintenance.
- Dress a wound with cloth and pressure (anything beyond first aid: Heal check).
- Tie functional knots (rigging, loads, snares).
- Set a basic camp (shelter, fire, latrine placement).
- Read weather within the next six hours (beyond six hours: Weather-sense check).
- Cook meat over fire without poisoning himself.
- Fix a torn seam or a split boot (anything structural: Leatherwork or Craft check).
- Navigate by sun and pole star in clear conditions (overcast/forest: Navigate check).
- Estimate distance and time of travel on known terrain.

### Specialist Knowledge

Beyond the baseline, individual members carry deep knowledge in their domains. This knowledge is tracked per-character in `22_MEMBER_STATBLOCKS.md` under the `Life Skills` field.

Specialist knowledge determines what a character can do _competently_ without a check, or with advantage on the check. It also determines what they notice automatically — the cook spots spoiled grain, the tracker reads a three-day-old trail, the quartermaster detects short-weight goods.

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

- **No check:** Baseline actions in normal conditions. Specialist actions within the character's domain under normal conditions.
- **Standard check:** Baseline actions under stress. Specialist actions under hostile conditions.
- **Hard check:** Actions outside a character's domain. Specialist actions under extreme conditions (blizzard, combat, injury).
- **Impossible without specialist:** Some actions require specialist knowledge. An untrained man cannot set a bone, read runes, or navigate by stars in overcast. He can try, but the check is penalized and failure has consequences.

---

## 18. Political Simulation (Village Networks)

Resolved by `village_politics.py`. Simulates the political landscape of Rimevegr settlements over weeks, months, and seasons. Tracks village economies, population dynamics, feuds, union formation, and the long-term march toward regional war.

**Lore reference:** `references/political_villages.md`

### 18.1 Village Economy Tick (Weekly)

Each settlement runs an economic tick once per week. Computed from `data/political_state.yaml` runtime state plus authored economy inputs from `data/economy/settlement_economies.yaml`, `data/settlements.yaml`, and `data/geography/routes.yaml`.

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

The runtime units above are abstract handling units for stock tracking, not coins or exact pounds. They are deliberately small so one weekly tick can show meaningful gains and shortages without turning state files into accounting sprawl.

**Season Modifiers:**

| Season              | Food Production | Food Consumption |
| ------------------- | --------------- | ---------------- |
| Long Summer (1-60)  | ×1.0            | ×1.0 per person  |
| Early Dark (61-150) | ×0.3 (stored)   | ×1.1 per person  |
| Deep Dark (151-300) | ×0.0 (no grow)  | ×1.2 per person  |
| Late Dark (301-360) | ×0.0 (no grow)  | ×1.3 per person  |

**Labor Ratio:** Fraction of working-age population assigned to food production vs. construction, defense, or other tasks. Default 0.7 (70% food, 30% other). Adjustable per settlement.

**Food vs. non-food handling:**

- `crop_fields` and food-producing authored goods both feed `food_stores_days` indirectly.
- `commodity_stocks` tracks named goods such as `dried_cod`, `rope`, `timber`, or `iron_bloom`.
- `stock_buckets` provides three broad pressure summaries:
- `food`
- `materials`
- `trade`
- `stock_capacities` are derived from actual built storage and workshop fabric in `data/settlements.yaml`.
- `strategic_resource_flags` are copied from authored settlement economy profiles so later systems can key off harbours, tar-works, mine heads, fishing fleets, and similar leverage points without reparsing prose.

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
- essential timber, iron, nails, charcoal, salt, tar, rope, and tool shortages add repair or readiness penalties
- wartime `essential_imports_at_risk` marks shortages as strategically serious
- `economic_vulnerabilities` can add extra pressure tags such as blockade chokepoint or repair bottleneck

**Runtime shortage fields:**

- `unmet_imports`: named goods currently failing to arrive in sufficient volume
- `dependency_health`: `0.0-1.0` summary of how well import demand is being met
- `repair_capacity_penalty`: current penalty from tool, iron, timber, or fuel shortage
- `military_readiness_penalty`: current penalty from shortages affecting walls, boats, weapons, salt stores, or transport capacity
- `vulnerability_pressure`: aggregate stress from essential dependency failure
- `shortage_flags`: machine-readable tags such as `food_shortage:grain` or `vulnerability:blockade_chokepoint`

**Route throughput, disruption, and market liquidity:**

Routes now do more than add one abstract trade modifier. Each weekly tick reads authored `trade_routes`, route seasonal access, route traffic level, route frequency, feud drag, and the settlement's market profile.

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
- `route_partner_losses`: destinations currently functioning as lost or nearly lost partners
- `route_disruption_flags`: machine-readable route stress tags such as `route_access:RTE_001:dangerous`, `route_feud_drag:RTE_003`, or `partner_loss:2`

**Union treasury, tribute, levy, and trade-bonus economics:**

After all settlements resolve their own weekly economy tick, each union applies a second weekly pass across its members. This pass consumes authored union data from `data/political_state.yaml` directly.

Silver tribute is converted into weekly pressure like this:

```text
weekly_tribute_silver =
  tribute_silver_weekly
  + (tribute_silver_monthly / 4)
  + (tribute_silver_seasonal / 13)
  + campaign_season ? (tribute_silver_monthly_campaign_season / 4) : 0
```

Mixed dues are the default. Authored note fields such as `tribute_goods_note` and `tribute_service_note` can create recurring food tribute, material tribute, or service burden when they name winter stores, peat carts, lookout duty, labor service, ferry priority, or forced crossings.

Effects:

- silver tribute leaves the member settlement treasury and enters `union.treasury_silver`
- food tribute moves from member `food_stores_days` into the seat's food stores
- material tribute moves through the `materials` stock bucket into the seat
- livestock tribute is accumulated weekly and transferred once whole animals are due
- levy obligations create a weekly readiness burden on the contributing member, not just a narrative flag
- `trade_bonus` on a member creates extra local trade silver and a smaller cut of dues into the union treasury

**Seat support burden:**

The overjarl's seat is not free to maintain. Each week, the union treasury must cover the silver burden of retainers, messengers, feasts, patrol planning, accounting, and command travel, plus a separate food draw at the seat. Military unions pay more in silver under high war readiness; covert unions pay more when dark-arts practice and whisper networks are active.

If the union treasury cannot pay full silver upkeep, the shortfall is paid directly by the seat settlement's own treasury.

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

These make extraction and support costs inspectable through the CLI instead of burying them in lore tables.

**Dark-arts and covert-network upkeep:**

After union tribute and seat support resolve, any union with `dark_arts_level`, `dark_arts_practitioners`, or `whisper_agents` applies a third weekly pass for occult and covert economy pressure.

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

- smuggling and covert skimming add silver to the union treasury before upkeep is paid
- occult upkeep drains union treasury, with any shortfall paid by the seat settlement directly
- the seat gains `covert_fear_pressure` and `confidence_shock_pressure`
- dark-arts practice reduces market liquidity at the seat and raises local price pressure
- each whisper agent applies smaller confidence and liquidity pressure at its target settlement
- targeted settlements receive machine-readable covert flags for inspection and later event logic

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

Wolfshead bands are now treated as weekly economic actors rather than pure encounter flavor. Each band reads from `data/wolfshead_bands.yaml` and creates runtime state from:

- `size`
- `threat_tier`
- `territory`
- `survival_strategy`
- `relationship_to_mercenaries`

The weekly pass estimates silver intake, food intake, desperation, target settlements, and mercenary-market competition from the strategy text.

```text
weekly_income_silver = size × 0.12 × strategy_revenue_factor
weekly_food_gain = size × 0.35 × strategy_food_factor / winter_hunger_mod
food_need = size × seasonal_band_food_need
desperation = max(0, (food_need - weekly_food_gain) / (size / 2))
```

Pressure then propagates to named settlements found in the band's territory, hook, winter strategy, or notes.

Effects on pressured settlements:

- `outlaw_pressure` rises to the highest active weekly threat nearby
- `night_market_chance` increases from that pressure
- coercive tribute or toll-taking creates `wolfshead_tribute_drag_silver`
- escort, toll, piracy, and protection-racket bands create `mercenary_competition_pressure`
- outlaw presence reduces local market liquidity and increases local price pressure
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

The world contract market is derived from authored contract pools in `data/contracts/*.yaml`, then filtered and stressed by current settlement conditions each week.

For each settlement:

- load contracts anchored to that settlement
- filter by season and year
- honor basic political blockers such as `requires_feud_max`
- calculate an issuer budget from local treasury plus limited union support
- reduce effective payout capacity under scarcity, feud, outlaw pressure, and route stress
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

The runtime market then exposes a small visible offer set, not the entire raw contract library.

**Advance and payout handling:**

When a contract is activated:

- the employer pays `advance_silver` immediately
- the remaining payout is locked as `reserved_payout_silver`
- the contract is added to `contract_market.active_contracts`

When a contract resolves:

- success pays the reserved amount and improves the targeted settlement state according to contract type
- failure does not refund the advance and pushes the settlement further into stress

Examples:

- successful `guard`, `patrol`, or `garrison` work reduces `outlaw_pressure`
- successful `escort` or `trade_protection` work improves liquidity and lowers local price pressure
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

**Season Birth Modifier:** Long Summer: ×1.5 (births from prior season pregnancies). Long Dark: ×0.8 (fewer conceptions, harder conditions).

**Fighter Training:** A settlement can train new fighters at a rate of 1 per 30 days per existing fighter acting as trainer. Trainees must be working-age men or women. Training costs 2 silver per week per trainee (equipment, food supplement). Maximum trainable at once: 20% of current fighter count (rounded up, minimum 1).

### 18.3 Village Infrastructure System

Settlement infrastructure is tracked as physical built fabric, not abstract prosperity. A hall burns differently from a granary. A palisade rots differently from a stone gatehouse. A jetty storm-damages without the settlement being "attacked" in any conventional sense.

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

All new works consume some mixture of wood, stone, turf, iron fittings, and labor. Silver can replace missing materials only by trade and only if supply routes are open.

**Core resource units:**

- `wood_units`: usable timbers, planks, poles, and brush bundles
- `stone_units`: quarried or field stone fit for foundation, walling, or ditch facing
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

- Hamlets usually sustain 8-20 effective labor-days per week without starving themselves.
- Villages usually sustain 15-40.
- Large villages usually sustain 30-70.
- Small towns or heavily mobilized seats can exceed 80, but usually at an economic cost elsewhere.

If a settlement diverts more than 25% of its working population to building for more than one month, apply one of the following:

- `food_production -10%`
- `trade_income -10%`
- `defense_readiness -1`

#### 18.3.3 Canonical structure costs

These values are sized for Rimevegr settlements rather than for private adventurer strongholds.

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

Structures cannot be built in any order the settlement wants. They require materials, labor, and often prerequisite fabric.

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
- no smith for iron gate, chain, or skilled forge: structure capped at improvised quality or delayed until fittings are imported

#### 18.3.5 Annual maintenance and neglect

Every structure has annual upkeep measured in maintenance points. These can be paid in labor and materials during the yearly repair season.

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
- Occupied settlements pay only half normal upkeep unless occupiers invest in the place.

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

**Repair rule:** repairs must restore the structural bottleneck first. A granary with a broken roof but intact floor can be repaired cheaply; a palisade with burned posts and a failed gate needs the gate throat rebuilt before the line counts as defensive again.

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

**Deliberate razing:** a victorious attacker in control of a settlement may raze fabric after the fight.

```text
raze_progress_per_day = floor(attacking_laborers / 8) + engineer_bonus + fire_bonus
```

Suggested raze thresholds:

- 2 progress: burn one household cluster or one production site
- 4 progress: destroy one gate complex or hall
- 6 progress: make a hamlet nonfunctional for the season
- 10 progress: reduce a village's defensive perimeter to broken segments

Stone works usually become gutted or dismantled, not erased. Mark them `ruined`, not absent, unless labor is spent to quarry them away over weeks.

#### 18.3.8 Occupation, tribute, and slow structural death

Repeated tribute and occupation damage settlements even when no dramatic sack occurs.

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

- convert 10-20% of available maintenance labor into tribute handling, transport, provisioning, and escort duty
- reduce new construction by 25%
- strip 1-3 silver equivalent per 25 population in mixed dues: silver, grain, livestock, peat, charcoal, or hauled goods depending on settlement economy
- after two consecutive seasons, one nonessential structure cluster becomes `worn`

This is how villages hollow out before they visibly collapse.

### 18.4 Crop and Livestock System

**Crops:** Planted during Long Summer only (Days 1-60). Harvest quality depends on weather, labor, and whether raiders disrupted planting.

```text
crop_yield = planted_fields × soil_quality × weather_score × labor_ratio
             × (1.0 - raid_disruption)
```

**Planted Fields:** Each settlement has a maximum field capacity based on terrain and population. One worker can tend 2 fields. One field feeds 3 people for a year in ideal conditions.

**Livestock:**

| Type   | Feed Cost/Week | Products                      | Breeding Rate |
| ------ | -------------- | ----------------------------- | ------------- |
| Sheep  | 0.5 food units | Wool, mutton, milk            | 1.2/year      |
| Goats  | 0.3 food units | Milk, hides, some meat        | 1.5/year      |
| Cattle | 1.5 food units | Milk, beef, hides, draft work | 0.8/year      |
| Pigs   | 1.0 food units | Pork, lard                    | 2.0/year      |

**Winter Culling:** Before Deep Dark, settlements slaughter livestock they cannot feed. Remaining animals consume stored feed. A settlement that miscalculates loses animals to starvation mid-winter.

**Livestock Raiding:** The most common cause of feuds. Each raided animal = 1 feud point with the victim settlement.

### 18.5 Raiding and Livestock Theft

Raids are the engine of feuds. A raid is a quick strike: arrive, take what you can carry, leave.

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
- Apply `18.3.6` damage states to any struck structures instead of treating "building damage" as a binary on/off flag.
- If granaries, smokehouses, root cellars, or fish sheds are burned, remove the associated stored food before weekly economy ticks resume.

### 18.6 Feud System (Settlement-to-Settlement)

Feuds track hostility between pairs of settlements. Stored in `data/political_state.yaml`.

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

**Minimum feud:** 0. **Maximum:** 4. Feud at 4 can only decrease through weregild, marriage, or destruction of one settlement.

### 18.7 Union Mechanics

Unions are tracked as named alliance structures in `data/political_state.yaml`.

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

Union war readiness tracks how close a union is to launching a campaign against another.

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

Tracks a union's investment in forbidden supernatural practices. Only the Whispering Circle starts with a nonzero value.

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

- At level 2+, other unions gain a "fear_of_dark_arts" modifier that reduces their willingness to attack directly (-1 war readiness when considering direct assault on the dark-arts user).
- At level 3+, neutral settlements may refuse to trade with the dark-arts user (feud +1 with all non-allied settlements).
- At level 5, the Veil response is uncontrollable. The invocation may succeed (devastating weapon against enemies) or backfire (Veil breach at the caster's own settlement, draugr incursion, permanent supernatural contamination).

### 18.10 The Allthing (Annual Assembly)

**Timing:** Day 90-100 (after harvest, early Long Dark).

**Resolution:** The Allthing resolves accumulated political tension. All unions and independent settlements send representatives.

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

**Allthing Intrigue:** The Pale Widow's agents operate during the Allthing. Each Allthing, roll for whisper-agent success:

```text
intel_chance = dark_arts_level × 15 + widow_wit × 5
If success: Widow learns one hidden agenda or plan from target union
If critical: Widow can plant false information in target union
```

### 18.11 Seasonal Political Tick

The political simulation runs a major tick once per season (4 times per year). Each tick:

1. **Economy:** All settlements run weekly ticks for the season (aggregate). Food stores updated. Silver updated.
2. **Population:** Monthly population changes applied (3 months per season for Long Dark, 2 months for Long Summer).
3. **Feuds:** All active feuds checked for escalation/de-escalation.
4. **Unions:** Cohesion checked. War readiness updated. Dark arts consequences applied.
5. **Raids:** AI determines which settlements or unions launch raids based on food shortage, feud level, and overjarl personality.
6. **Building:** Construction progress advanced. Maintenance arrears, repairs, and occupation decay also advance here.
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
