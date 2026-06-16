# Iron Ledger — Simulation Rules

<!-- notion-export:toc -->


## 18. Political Simulation (Village Networks)

Resolved by `village_politics.py`. Simulates the political landscape of Rimevegr settlements over weeks, months, and seasons. Tracks village economies, population dynamics, feuds, union formation, and the long-term march toward regional war.

**Lore reference:** `references/political_villages.md`

### 18.1 Village Economy Tick (Weekly)

Each settlement runs an economic tick once per week. Computed from `data/settlements.yaml` fields.

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

**Labor Ratio:** Fraction of working-age population assigned to food production vs. construction, defense, or other tasks. Default 0.7 (70% food, 30% other). Adjustable per settlement.

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

### 18.3 Community Buildings

Settlements can build and upgrade structures. Buildings provide economic bonuses, defensive capacity, or special capabilities.

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

**Building requires:** Available labor (at least 5 workers diverted from other tasks), materials (wood/stone/iron from stores or trade), and no active siege or occupation.

**Damaged buildings:** Raids at feud level 2+ may damage buildings. Damaged buildings lose their bonuses until repaired (half original build time, half cost).

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

This section governs how outlaw populations interact with settlements, how settlements respond, and how outlawry creates political pressure and narrative events.

See `data/culture/outlawry_system.yaml` for the full legal framework and `data/culture/honor_contract_system.yaml` for mercenary-specific honor mechanics.

#### 18.14.1 Outlaw Pressure (Settlement Stat)

Each settlement tracks `outlaw_pressure` (0-5), representing how many outlaws operate nearby and how aggressively.

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

Settlements respond to outlaw pressure based on their resources and political alignment.

**Response Options:**

| Response              | Cost (copper) | Effect                       |
| --------------------- | ------------- | ---------------------------- |
| Hire mercenary patrol | 50/week       | -1 pressure per week patrol  |
| Organize militia      | 20 (one-time) | -1 pressure, +1 feud risk    |
| Pay tribute           | 30/season     | -1 pressure, +1 outlaw rep   |
| Negotiate amnesty     | 0 (political) | -2 pressure, reputation risk |
| Ignore                | 0             | Pressure continues rising    |

**Amnesty Mechanics:**

A settlement headman may offer amnesty to select outlaws who agree to serve the settlement (militia, labor, or specific tasks). This requires ting approval.

```text
amnesty_chance = headman_persuade × 10 + settlement_desperation × 5
              - outlaw_severity × 15
# settlement_desperation = outlaw_pressure level
# outlaw_severity = 1 (lesser) or 3 (full)
# Success: outlaw integrated, pressure -2, community tension +1
# Failure: outlaw refuses or ting rejects, pressure unchanged
```

#### 18.14.3 Night Markets

Night markets are illegal trading sessions held outside settlement walls after dark. They emerge when outlaw_pressure reaches 2+.

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

A mercenary band may attend a night market. This provides access to rare goods and information but risks reputation if discovered by the contracting settlement. If the band is hired to STOP the night market, attending it is a contract violation.

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

The following events integrate with the existing event system. Event IDs use the `EVT_OUTLAW_` prefix.

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
