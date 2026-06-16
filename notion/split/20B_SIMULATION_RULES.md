# Iron Ledger — Simulation Rules

<!-- notion-export:toc -->


## 5. Health and Wounds

> **Lore cross-reference:** `wound-and-healing-system.md` contains > the
setting-specific medical lore (humoral framework, leech tools, > wound classification descriptions, healing stage narratives, > medieval terminology glossary). This section contains all > simulation mechanics.

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

Every wound inflicted by `combat_sim.py` produces a discrete `Wound` record. Wounds accumulate — they do not merge. A man with three separate light wounds on his right arm has three wounds, not one medium wound. Each requires separate treatment and heals on its own timeline.

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

Each main location has specific sublocations that determine structures at risk and activities impaired.

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
- Three+ wounds on same location: healing time × 1.5 for each wound beyond the second. Infection risk per day doubles.

3. **Total wound load.** Total active wounds affect systemic health:

| Active Wounds | Systemic Effect                          |
| ------------- | ---------------------------------------- |
| 1–2           | No systemic effect                       |
| 3–4           | -5 all rolls (body dividing resources)   |
| 5–6           | -10 all rolls, appetite loss, poor sleep |
| 7+            | -20 all rolls, wound-fever risk per day  |

4. **Blood loss accumulation.** Each wound's bleeding rate stacks. If total bleeding exceeds 3 HP/round during combat, collapse in minutes. Post-combat, untreated bleeding converts to HP loss per hour.

5. **The worst wound governs.** Worst untreated wound determines overall condition category:

| Worst Active Wound | Condition Category |
| ------------------ | ------------------ |
| Scratch only       | Functional         |
| Light              | Wounded (limited)  |
| Serious            | Badly wounded      |
| Critical           | Incapacitated      |
| Mortal             | Dying              |

### 5.7 Healing Stages (Mechanical)

Each wound passes through defined stages. The stage determines mechanical penalties, complication risks, and activity restrictions.

| Stage | Name     | Duration (Light) | Duration (Serious) | Duration (Critical) |
| ----- | -------- | ---------------- | ------------------ | ------------------- |
| 1     | Fresh    | 0–4 hours        | 0–4 hours          | 0–4 hours           |
| 2     | Clotting | 4–48 hours       | 4–48 hours         | 4–48 hours          |
| 3     | Closing  | Day 2–7          | Day 2–14           | Day 14–30           |
| 4     | Knitting | Day 7–21         | Day 14–45          | Day 30–90           |
| 5     | Scarring | Day 21+          | Day 45+            | Day 90+             |
| 6     | Healed   | Resolved         | Resolved           | Resolved            |

**Stage-specific mechanics:**

- **Fresh:** Bleeding at wound rate. `treated: false` until leech attends. All wound penalties at full.
- **Clotting:** `bleeding: 0` if properly treated. Daily infection check active. Full wound penalties.
- **Closing:** Wound penalties reduce by one step if properly treated. Infection check drops to 2% per day.
- **Knitting:** Wound penalties halved from worst. Physical exertion check required — any combat or heavy labor forces a TOU check or wound re-opens (reverts to Stage 1 with healing time × 1.5).
- **Scarring:** Wound penalties removed except permanent effects. Scar record generated.
- **Healed:** Wound record marked `resolved: true`. Permanent effects remain on statblock.

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

All healing timelines above assume full rest. In the field, multiply by ×2. On active duty, multiply by ×5 — wounds essentially do not heal while marching and may worsen.

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

This check runs daily from day after injury until wound enters Stage 3 (closing) or becomes infected. After Stage 3, check drops to 2% per day.

#### Infection Stages

| Stage | Name          | Onset              | Mechanical Effect                          |
| ----- | ------------- | ------------------ | ------------------------------------------ |
| 1     | Early Rot     | 1–3 days           | -10 all rolls at location. Heal check +0   |
| 2     | Spreading     | 3–5 days untreated | -15 all rolls. 1 HP/day. Fever. Heal -15   |
| 3     | Deep Rot      | 5–10 days          | -30 all rolls. 2 HP/day. Fever. Heal -30   |
| 4     | Mortification | 10+ days           | Incapacitated. 5 HP/day. Death in 2–5 days |

**Progression:** Failed heal check at each stage advances infection to the next stage. Successful check at Stage 1 contains it; at Stage 2 retreats to Stage 1; at Stage 3 stabilizes at Stage 2. Mortification requires amputation of affected limb or death.

**Wound-Fever (Sárhiti):** Systemic fever from Stage 2+ infection. Daily TOU check to break fever (difficulty scales with infection stage). Adds -5 additional to all rolls when feverish.

### 5.10 Bone Complications

#### Simple Fracture

Bone broken, skin intact. Treatment: traction + splinting. Immobilize joint above and below break. See bone injury healing table (§ 5.8).

#### Compound Fracture

Bone broken AND skin breached. Emergency. Infection base: 40%. Treatment: irrigate, reduce bone, set, splint, dress wound. Double healing time of simple fracture.

#### Dislocated Joint

Joint forced from socket. Reduction required within hours (muscle spasm makes later reduction very difficult). After reduction, joint works immediately but is loose and re-dislocation prone for weeks.

### 5.11 Pain System

Pain is not a modifier. Wounds already carry mechanical penalties (§ 5.2, § 5.13). Pain is a narrative layer — it shapes how a character acts, speaks, thinks, and sleeps. The simulation tracks pain level; the prose renders what pain _does_ to a person.

> Pain does not stack with wound penalties. It coexists. A man > with a
serious arm wound already fights at -15 to that arm. Pain > tells you _how_ he fights at -15: whether he flinches before the > swing, whether his breathing has gone shallow, whether he has > stopped speaking.

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

These are rendering directives. They tell the prose what to show. They do not add numerical penalties — the wound penalties already cover that.

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

- Vision narrows. The world contracts to a corridor of focus directly ahead. Flanking threats go unseen.
- Sudden spikes cause involuntary gasps, grunts, or hissing through clenched teeth.
- Movement becomes deliberate and slow — the body refuses to surprise itself.
- The character stops initiating conversation. Responds in monosyllables when addressed.
- Hands shake on tasks requiring steadiness. Threading a needle, drawing a bowstring, or writing become unreliable.
- Sleep is impossible without total exhaustion or strong drink. The character dozes sitting upright, wakes at every shift.
- Pale face, cold sweat on the brow and upper lip. Others notice before the wounded man admits it.

**Agonizing pain — the world shrinks to the wound:**

- Tunnel vision. The character can focus only on what is directly in front of them. Everything peripheral is lost — not blurred, but simply absent.
- Hearing goes selective. Voices sound distant and muffled, as if underwater. The character may not respond to their name.
- Light hurts. Bright day or firelight produces a stabbing sensation behind the eyes. The character shades their face, turns away from flame.
- Nausea builds. The gut clenches. Vomiting is common, especially when moved or when the wound is touched.
- Involuntary sounds — groaning, whimpering, sudden cries at spikes — that the character cannot suppress. Pride means nothing; the body speaks for itself.
- Decision-making collapses. The character cannot weigh options. They follow orders or repeat the last thing they were doing. Initiative is gone.
- Time distorts. Minutes feel like hours. The character loses track of when events happened. "Was that this morning or yesterday?"
- The character forgets to eat, drink, or relieve themselves unless reminded. The body has one priority.
- Others must make choices for them. Dalla says "drink this" and hands appear and the cup is at his lips before he knows he moved.

**Unconscious pain threshold:**

- The character collapses. Eyes roll back. Breathing goes shallow and rapid.
- Responds to nothing — not voice, not cold water, not a slap. Only the leech's work can bring them back by reducing the pain source.

#### Pain and Willpower

Characters enduring Moderate+ pain make daily WIL checks.

- **Success:** Endures. No mechanical change. The prose may note clenched fists or bitten lips.
- **Failure:** Temporary WIL degradation (-1 until a full day of pain-free rest). The character becomes passive, withdrawn, or irritable.
- **Chronic pain** (14+ continuous days at Severe or above): permanent -1 WIL. The character's baseline shifts. They become someone who has learned to live with it — quieter, harder, or more brittle, depending on who they were before.

Recovery: 1 temporary WIL point per day of pain-free rest. Permanent WIL loss does not recover.

#### Pain in Combat (Narrative Rendering)

When combat_sim produces rounds, pain level shapes the prose description of the fighter's actions:

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

Old scars carry memory of the wounds that made them. Before weather changes (rime storms, deep cold, damp), healed wounds ache. Characters with weather-sensitive scars experience a brief rise in pain level (one step, lasting hours) that serves as an involuntary forecast. This is covered in § 5.14.

### 5.12 Incapacitation System

Wounds produce specific functional impairments tracked as incapacitation records.

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

Old scars and healed fractures ache before weather changes (barometric pressure effect). Mechanical effects:

- Before rime storm: old wounds throb, healed fractures ache, scar tissue pulls tight.
- In deep cold: healed frostbite sites burn and tingle.
- In damp: old joint injuries stiffen.

Characters with 3+ healed serious wounds or any healed critical wound gain Weather-sense 1 (passive) — their body predicts weather. Stacks with existing Weather-sense skill.

### 5.15 Special Conditions

#### The Wound-Addled (Sárviti)

**Threshold:** 5+ healed serious wounds, or 2+ healed critical wounds, or any healed mortal wound.

**Effects:**

- Flinch reflex: -5 to initiative.
- Pain sensitivity: pain levels from new wounds one step higher.
- Weather-sensitivity stacks (all old wounds ache together).
- Will erosion: -1 permanent WIL.

#### The Iron Scar (Járnörr)

Rare. Character who healed a mortal wound carries authority among fighting men.

**Effects:**

- +1 Intimidate (the scar speaks before the man does).
- -1 maximum HP permanently.
- Weather-sensitivity at the mortal wound site.
- Other characters treat the bearer differently.

### 5.16 Health Subsystem Commands

These commands drive the wound lifecycle. Invoked by the narrative director (AI) to track state changes as the story progresses.

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

**Effects:** Creates wound record, subtracts HP, adds bleeding, triggers incapacitation check, updates condition.

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

**Success:** Wound properly treated. Healing clock starts. Bleeding stops. Infection chance reduced per treatment type.

**Failure:** Treatment partial. 50% chance bleeding continues. Infection reduction halved. Foreign bodies may be missed (+15% infection chance).

**Critical failure:** Treatment worsens condition. Possible wound re-opening, additional damage, incorrect bone setting.

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

Each wound's `healing_day_count` advances by `days_elapsed × rest_quality_multiplier`. When count reaches next stage threshold, wound advances. Complication check rolls for infection (Stages 1–2), re-opening (Stage 4 + active duty), and bone re-break (knitting + heavy activity).

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

**Effects:** Updates severity and penalties, resets healing to "fresh", restarts bleeding, updates incapacitation. HP damage = difference between old and new severity.

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

**Effects:** Resolves all wounds on amputated portion. Creates surgical wound at stump. Creates permanent incapacitation record. Reduces max_hp:

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

Recalculate overall condition based on all active wounds, infections, and incapacitations.

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

When `combat_sim.py` produces a wound, the health subsystem converts it to a full wound record:

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

Statblocks (`22_MEMBER_STATBLOCKS.md`) and band state (`data/band_state.yaml`) are updated when wound commands execute.

### 5.18 Psychological Trauma System

Trauma is tracked alongside physical wounds. Where wounds damage the body, trauma damages the _hugr_ (mind-soul). The system mirrors the physical wound lifecycle: trauma is inflicted, manifests, worsens or recovers, and leaves permanent marks.

> **Lore reference:** `psychological_trauma.md` covers period- > accurate
Norse concepts of mind-damage, presentation patterns, > coping mechanisms, cultural constraints, and rendering rules. > This section covers only simulation mechanics.

#### Trauma Stress Points (TSP)

Every character has a **Stress Threshold** derived from WIL:

```text
stress_threshold = WIL × 3
```

**Trauma Stress Points (TSP)** accumulate from traumatic events. When TSP exceeds the stress threshold, a **trauma condition** manifests. TSP does not reset when a condition manifests — the threshold is recalculated against the new WIL baseline.

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

When TSP exceeds stress_threshold, a trauma condition manifests. The type depends on the triggering event and the character's personality (WIL, background, existing conditions).

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

Each condition has associated triggers — stimuli that activate the acute response. Triggers are specific and tracked per condition.

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

Recovery is slow, non-linear, and not guaranteed. A man can improve, plateau, or relapse. There are no medications and no therapy — only time, conditions, and the band.

#### Recovery Stages

| Stage    | Duration            | Effect                                                         |
| -------- | ------------------- | -------------------------------------------------------------- |
| Acute    | 0–7 days            | Full condition severity; high TSP                              |
| Active   | 1–8 weeks           | Condition active; triggers frequent                            |
| Easing   | 2–12 weeks          | Severity drops one step; triggers less frequent (check 1/week) |
| Residual | Permanent or months | Mild trigger sensitivity remains; may flare under new stress   |
| Resolved | Permanent           | Condition removed; TSP reduced                                 |

#### Recovery Factors

Recovery advances when **recovery conditions** are met. Each day of met conditions accumulates **recovery points (RP)**. Recovery thresholds by severity:

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

When sufficient RP accumulates, the character makes a **WIL check** to advance to the next recovery stage:

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

Temporary WIL recovers: 1 point per 14 days of resolved condition. Permanent WIL loss does not recover.

### 5.23 Psychological Profile Fields

Each member's statblock includes a psychological profile that tracks accumulated trauma, resilience status, and behavioral baseline:

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

The profile is maintained alongside physical wound/scar records. `condition_update` (§ 5.16) factors in active trauma conditions when computing overall member state.

### 5.24 Trauma Subsystem Commands

All commands mutate member state and return result dicts. CLI interface matches `wounds.py` conventions.

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
3. If TSP > stress_threshold: select condition type based on event category and character profile.
4. Set condition severity based on overshoot (TSP - threshold): 0–3 = mild, 4–8 = moderate, 9–15 = severe, 16+ = crippling.
5. Generate triggers from source event.
6. Update behavioral baseline.

#### trauma_trigger

Fire a trigger check. Resolves whether the condition activates and for how long.

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

Manually add a trauma condition (for backstory, for events outside normal TSP flow).

```yaml
command: trauma_add_condition
target: "Thorne Ash-Born"
condition: "flinch_sickness"
severity: "mild"
source: "Backstory — hall fire"
triggers: ["open_flame", "smoke_smell", "screaming"]
```

#### profile_update

Recalculate full psychological profile from all active conditions, TSP, WIL degradation, and resilience factors.

```yaml
command: profile_update
target: "Ubbe Ironside"
```

### 5.25 Trauma and Combat Integration

When `combat_sim.py` produces a kill, a wound, or a significant event, the trauma subsystem checks for TSP accrual:

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

Band-level events (Named Man death, atrocity, betrayal) trigger TSP for all witnesses with appropriate modifiers.

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

Trauma is tracked alongside physical wounds. Where wounds damage the body, trauma damages the _hugr_ (mind-soul). The system mirrors the physical wound lifecycle: trauma is inflicted, manifests, worsens or recovers, and leaves permanent marks.

> **Lore reference:** `psychological_trauma.md` covers period- > accurate
Norse concepts of mind-damage, presentation patterns, > coping mechanisms, cultural constraints, and rendering rules. > This section covers only simulation mechanics.

#### Trauma Stress Points (TSP)

Every character has a **Stress Threshold** derived from WIL:

```text
stress_threshold = WIL × 3
```

**Trauma Stress Points (TSP)** accumulate from traumatic events. When TSP exceeds the stress threshold, a **trauma condition** manifests. TSP does not reset when a condition manifests — the threshold is recalculated against the new WIL baseline.

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

When TSP exceeds stress_threshold, a trauma condition manifests. The type depends on the triggering event and the character's personality (WIL, background, existing conditions).

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

Each condition has associated triggers — stimuli that activate the acute response. Triggers are specific and tracked per condition.

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

Recovery is slow, non-linear, and not guaranteed. A man can improve, plateau, or relapse. There are no medications and no therapy — only time, conditions, and the band.

#### Recovery Stages

| Stage    | Duration            | Effect                                                         |
| -------- | ------------------- | -------------------------------------------------------------- |
| Acute    | 0–7 days            | Full condition severity; high TSP                              |
| Active   | 1–8 weeks           | Condition active; triggers frequent                            |
| Easing   | 2–12 weeks          | Severity drops one step; triggers less frequent (check 1/week) |
| Residual | Permanent or months | Mild trigger sensitivity remains; may flare under new stress   |
| Resolved | Permanent           | Condition removed; TSP reduced                                 |

#### Recovery Factors

Recovery advances when **recovery conditions** are met. Each day of met conditions accumulates **recovery points (RP)**. Recovery thresholds by severity:

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

When sufficient RP accumulates, the character makes a **WIL check** to advance to the next recovery stage:

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

Temporary WIL recovers: 1 point per 14 days of resolved condition. Permanent WIL loss does not recover.

### 5.23 Psychological Profile Fields

Each member's statblock includes a psychological profile that tracks accumulated trauma, resilience status, and behavioral baseline:

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

The profile is maintained alongside physical wound/scar records. `condition_update` (§ 5.16) factors in active trauma conditions when computing overall member state.

### 5.24 Trauma Subsystem Commands

All commands mutate member state and return result dicts. CLI interface matches `wounds.py` conventions.

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
3. If TSP > stress_threshold: select condition type based on event category and character profile.
4. Set condition severity based on overshoot (TSP - threshold): 0–3 = mild, 4–8 = moderate, 9–15 = severe, 16+ = crippling.
5. Generate triggers from source event.
6. Update behavioral baseline.

#### trauma_trigger

Fire a trigger check. Resolves whether the condition activates and for how long.

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

Manually add a trauma condition (for backstory, for events outside normal TSP flow).

```yaml
command: trauma_add_condition
target: "Thorne Ash-Born"
condition: "flinch_sickness"
severity: "mild"
source: "Backstory — hall fire"
triggers: ["open_flame", "smoke_smell", "screaming"]
```

#### profile_update

Recalculate full psychological profile from all active conditions, TSP, WIL degradation, and resilience factors.

```yaml
command: profile_update
target: "Ubbe Ironside"
```

### 5.25 Trauma and Combat Integration

When `combat_sim.py` produces a kill, a wound, or a significant event, the trauma subsystem checks for TSP accrual:

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

Band-level events (Named Man death, atrocity, betrayal) trigger TSP for all witnesses with appropriate modifiers.

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

Folk magic — household wards, herb-bundles, carved threshold runes — does not produce mechanical magical effects. Its effect is on morale: men who see familiar protective rituals performed feel safer, even when the rituals do nothing measurable.

**Ward confidence:** When camp is made near intact ward-stones (settlement or standalone), the band gains +1 morale (one-time, on arrival) as long as the ward-stones are visibly maintained. If the ward-stones are cracked, dark, or obviously failing, the morale bonus becomes -1 instead.

**Ritual comfort:** A galdr-worker who performs camp-warding rites (even purely symbolic ones, below Rune-lore rank thresholds) stabilizes morale: prevents any superstition-based morale drops for that week. This costs the galdr-worker 1 Willpower.

**Omen dependency:** Repeated favorable wyrd-readings create omen dependency: if the band receives 3+ consecutive favorable readings then a negative one, the morale drop is -2 instead of -1. The men expected good fortune and feel betrayed by fate.

See `08_MAGIC_OF_RIMEVEGR.md` §3 (Folk Magic: The Household Layer) for narrative context.

### Grievance Resolution

Captain addresses grievances at fire (once per week). Uses Command or Persuade check with difficulty based on grievance severity:

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

Each fighter carries personal gear (3-8 kg) plus share of communal supplies. Exceeding carry limit: -10 to all physical rolls, march speed halved.

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

Track total weight of: weapons, armor, food stores, trade goods, silver, tools, and personal effects. A 14-person band typically carries 200-350 kg total. Overweight slows march speed further.

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

Roll d100 when wages are 14+ days late on retainer or 3+ days late on active mission:

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
