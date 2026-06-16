# Iron Ledger — Game Content Bible

## Iron Ledger — Complete Game Content Reference

**Purpose:** This document captures every table, list, constant, and data structure that lives in the Python scripts. Together with `20_SIMULATION_RULES.md` (core mechanics), it forms the full authoritative ruleset. AI sessions **must** reference both documents to run the game consistently.

**Relationship to 20_SIMULATION_RULES.md:** The rules document defines _how mechanics work_ (formulas, resolution, combat flow). This document defines _what content exists_ (encounter tables, contract types, NPC data, settlement structures, name lists, pricing, terrain hazards, etc.).

---

## Table of Contents

1. [Calendar and Months](#1-calendar-and-months)
2. [Weather Modifier Tables](#2-weather-modifier-tables)
3. [Terrain Data](#3-terrain-data)
4. [Settlements](#4-settlements)
5. [Economy and Pricing](#5-economy-and-pricing)
6. [Contracts](#6-contracts)
7. [Feud System Data](#7-feud-system-data)
8. [Recruitment](#8-recruitment)
9. [NPC Generation](#9-npc-generation)
10. [Encounter Tables](#10-encounter-tables)
11. [Travel Hazards](#11-travel-hazards)
12. [Band State Structure](#12-band-state-structure)
13. [Morale Modifier Tables](#13-morale-modifier-tables)
14. [Pay and Loot Values](#14-pay-and-loot-values)
15. [Time Costs](#15-time-costs)

---

## 1. Calendar and Months

One year = 360 days (12 months × 30 days each).

| #   | Month Name | Season      |
| --- | ---------- | ----------- |
| 1   | Frostwake  | Long Summer |
| 2   | Rimeblood  | Long Summer |
| 3   | Veilthin   | Long Dark   |
| 4   | Ashfall    | Long Dark   |
| 5   | Ironmoon   | Long Dark   |
| 6   | Wolfmoot   | Long Dark   |
| 7   | Barrowrise | Long Dark   |
| 8   | Longnight  | Long Dark   |
| 9   | Hearthstar | Long Dark   |
| 10  | Bloodtide  | Long Dark   |
| 11  | Skaldsong  | Long Dark   |
| 12  | Yuledeep   | Long Dark   |

Long Summer = Months 1-2 (Days 1-60). Long Dark = Months 3-12 (Days 61-360).

---

## 2. Weather Modifier Tables

Each weather type imposes specific modifiers to foraging, travel, combat, and ranged rolls. Sourced from `weather.py`.

| Weather       | Forage Mod | Travel Mod | Combat Mod | Ranged Mod | Special                             |
| ------------- | ---------- | ---------- | ---------- | ---------- | ----------------------------------- |
| Clear Grey    | ×1.0       | ×1.0       | +0         | +0         | —                                   |
| Rime-Fog      | ×0.8       | ×0.7       | +0         | -10        | Hush likely                         |
| Light Rain    | ×0.9       | ×0.9       | +0         | -5         | —                                   |
| Driving Snow  | ×0.5       | ×0.5       | -20        | -20        | Frostbite risk                      |
| Rime Storm    | ×0.0       | ×0.2       | -30        | -30        | High frostbite, foraging impossible |
| The Hush      | ×1.0       | ×1.0       | -20        | +0         | Sound-based actions fail, fear      |
| Veil-Thinning | ×1.1       | ×1.0       | +0         | +0         | Omen event, Wyrd checks (WYR 3+)    |
| Blood Sun     | ×1.0       | ×0.5       | -10        | -10        | Terror event, animals freeze        |

### Weather Hazard Multipliers (Travel)

Bad weather increases terrain hazard chance during travel:

| Weather           | Hazard Chance Multiplier |
| ----------------- | ------------------------ |
| Driving Snow      | ×1.5                     |
| Rime Storm        | ×1.5                     |
| Rime-Fog          | ×1.2                     |
| All other weather | ×1.0                     |

---

## 3. Terrain Data

### March Speed Multipliers

From `logistics.py`. Applied to base 25 km/day.

| Terrain  | Speed Mult |
| -------- | ---------- |
| Coast    | ×1.0       |
| Fjord    | ×1.0       |
| Forest   | ×0.6       |
| Pine     | ×0.6       |
| Moors    | ×0.7       |
| River    | ×0.8       |
| Ice      | ×0.8       |
| Mountain | ×0.4       |

### Weather Speed Multipliers

| Weather       | Speed Mult |
| ------------- | ---------- |
| Clear Grey    | ×1.0       |
| Clear (alias) | ×1.0       |
| Rime-Fog      | ×0.7       |
| Light Rain    | ×0.9       |
| Driving Snow  | ×0.5       |
| Rime Storm    | ×0.2       |
| The Hush      | ×1.0       |
| Veil-Thinning | ×1.0       |
| Blood Sun     | ×0.5       |

### Season Speed Multiplier

| Season      | Mult |
| ----------- | ---- |
| Long Summer | ×1.0 |
| Long Dark   | ×0.8 |

### Terrain Trade and Food Traits

From `settlement.py`. Affects settlement pricing and food availability.

| Terrain  | Trade Bonus | Food Mod | Description                                   |
| -------- | ----------- | -------- | --------------------------------------------- |
| Coast    | 1.0         | 0.9      | Coastal settlement with fishing and trade     |
| Forest   | 0.8         | 0.85     | Woodland settlement, timber-rich but isolated |
| Moors    | 0.7         | 1.1      | Exposed moorland settlement, wind-blasted     |
| Mountain | 0.6         | 1.2      | Mountain settlement, defensible but poor      |
| River    | 0.9         | 0.95     | Riverside settlement with trade route access  |
| Fjord    | 1.0         | 0.9      | Fjord settlement with deep-water harbor       |

**Trade bonus** makes gear cheaper (higher = lower non-food prices). **Food mod** affects food prices (higher = more expensive).

---

## 4. Settlements

### Settlement Sizes

| Size          | Population | Services Available                                                        | Defense               | Notable Buildings |
| ------------- | ---------- | ------------------------------------------------------------------------- | --------------------- | ----------------- |
| Hamlet        | 20-60      | Inn, General Trade                                                        | Palisade or none      | 1                 |
| Village       | 60-200     | Inn, General Trade, Smithy, Healer                                        | Wooden palisade       | 2                 |
| Large Village | 200-500    | Inn, General Trade, Smithy, Healer, Shipwright, Temple                    | Wooden wall with gate | 3                 |
| Small Town    | 500-2000   | Inn, General Trade, Smithy, Healer, Shipwright, Temple, Jarl Hall, Market | Stone wall, garrison  | 5                 |

### Service Descriptions

| Service       | Description                                                         |
| ------------- | ------------------------------------------------------------------- |
| Inn           | Rest, food, ale, and rumors. Hear about local events and contracts. |
| General Trade | Buy and sell common goods, food, and basic equipment.               |
| Smithy        | Weapon and armor repair, basic metalwork. Can commission gear.      |
| Healer        | Treat wounds, cure infections, set bones. Reduces recovery time.    |
| Shipwright    | Repair and commission boats. Access to coastal routes.              |
| Temple        | Blessings, rune consultations, and spiritual counsel.               |
| Jarl Hall     | Audience with the local lord. High-value contracts and disputes.    |
| Market        | Weekly market with wider goods selection and better prices.         |

### Notable Building Types

Randomly assigned to settlements based on size. 15 possibilities:

- Ancient rune-stone, mead hall, watchtower, barrow nearby, hot spring, sacred grove, old longship hull (landmark), iron mine entrance, tannery, rope walk, salt works, brewery, chieftain's longhouse, trading post, fisher's wharf

### Settlement Events

Random events that trigger at settlements (from `settlement.py`):

| Event          | Description                                              | Effect              |
| -------------- | -------------------------------------------------------- | ------------------- |
| Market Day     | Weekly market — all prices reduced 10%                   | Price reduction     |
| Festival       | Seasonal festival — free ale, +1 morale if band attends  | Morale boost        |
| Plague Scare   | Sickness in settlement — healer busy, risk of infection  | Infection risk      |
| Raider Warning | Raiders spotted nearby — guard contracts available       | Contract available  |
| Trade Caravan  | Southern trade caravan arrives — rare goods available    | Rare goods          |
| Feud Flare     | Old blood-feud erupts — brawl in the street              | Feud increase       |
| Wanderer       | A lone wanderer seeks shelter — potential recruit or spy | NPC encounter       |
| Thing Assembly | Local thing (assembly) — disputes settled, oaths sworn   | Reputation chance   |
| Bad Harvest    | Failed harvest — food prices increase 30%                | Food price increase |
| Good Fishing   | Excellent catch — food prices decrease 20%               | Food price decrease |

### Canonical Settlement List (15 Locations)

| Settlement         | Size          | Leader              | Key Economy       | Notable Feature           |
| ------------------ | ------------- | ------------------- | ----------------- | ------------------------- |
| Frostfjord Hollow  | Village       | Jarl Hrothgar       | Dried cod         | Rune-stone nearby         |
| Ashen Reach        | Large Village | Pale Widow          | Pine tar, iron    | Skilled blacksmith        |
| Feldwick           | Village       | Three Wolves (occ)  | Sheep, root veg   | Occupied, desperate       |
| Stonebay Hamlet    | Hamlet        | None                | Fishing           | Remote, no blacksmith     |
| Grimholt           | Large Village | Ordovast            | Iron mining       | Strong defenses (lv 4)    |
| Raven's Perch      | Village       | Thane Egil          | Goat hides, iron  | Mountain lookout (lv 4)   |
| Vargheim           | Large Village | Jarl Ulf Vargson    | Charcoal, kennels | Wolf-warden kennels       |
| Kolvik             | Village       | Harbour-Master Inga | Shipwright, fish  | Only shipwright nearby    |
| Moor's End         | Hamlet        | Elder Brosa         | Sheep, peat       | Humming standing stones   |
| Ashmark            | Village       | Reeve Torsten       | Pine tar, herbs   | Neutral ground, healer    |
| Deepholm           | Small Town    | Jarl Sigrun         | Iron, weapons     | Masterwork smithy, market |
| Bleakwater Landing | Hamlet        | Ferryman Olaf       | Ferry tolls, fish | River crossing point      |
| Skaldhaven         | Village       | Lore-Keeper Audun   | Relic trade       | Hall of Sagas, rune arch. |
| Thornwall          | Large Village | Jarl Helga          | Wool, mutton      | Thorn-hedge walls         |
| Icebreak           | Hamlet        | Hermit Ragnhild     | None (outpost)    | Seidr practitioner WYR 5  |

### Rival Band Reference (7 Bands)

| Band               | Leader            | Size | Archetype | Location                |
| ------------------ | ----------------- | ---: | --------- | ----------------------- |
| The Three Wolves   | Hadric Wolfsmile  |   22 | Tyrant    | Inner Fjords            |
| The Bone Pack      | Grandmother Kolla |   18 | Kin Clan  | Outer Reaches, nomadic  |
| The Silent Oar     | Gunvald No-Name   |   12 | Fraternal | Coastal, moving south   |
| The Hollow Hall    | Brek Saltmarch    |    9 | Fraternal | Pest-clearance contract |
| The Iron Tide Rem. | Sigrid Blackwine  |   14 | Standard  | Wintering Raven's Perch |
| The Grave Wardens  | Elder Bryn        |    7 | Kin Clan  | Iron Barrow, Grimholt   |
| The Red Tide       | Wulfgar Branded   |   20 | Tyrant    | Northern Ice-Reach      |

---

## 5. Economy and Pricing

### Base Prices (Copper)

1 silver = 10 copper. From `settlement.py`.

| Item             | Base Price (copper) | Equiv Silver |
| ---------------- | ------------------: | -----------: |
| Food (1 week)    |                  10 |           1s |
| Ale (mug)        |                   1 |            — |
| Room (1 night)   |                   3 |            — |
| Horse            |                 200 |          20s |
| Dagger           |                  20 |           2s |
| Hand Axe         |                  40 |           4s |
| Sword            |                 100 |          10s |
| Spear            |                  50 |           5s |
| Leather Armor    |                  60 |           6s |
| Chainmail        |                 250 |          25s |
| Iron Helm        |                  80 |           8s |
| Wooden Shield    |                  30 |           3s |
| Iron Shield      |                  60 |           6s |
| Rope (20m)       |                   5 |            — |
| Torch Bundle     |                   3 |            — |
| Healing Herbs    |                  15 |        1s 5c |
| Warm Cloak       |                  20 |           2s |
| Rations (1 week) |                  10 |           1s |

### Price Modifiers

Actual price = base × terrain modifier × feud modifier.

**Food items:** modified by terrain `food_mod`.
**Non-food items:** modified by `(2.0 - trade_bonus)` (higher trade bonus = cheaper non-food goods).

### Feud Price Multipliers

| Feud Level | Name       | Price Mult |
| ---------- | ---------- | ---------- |
| 0          | Cold       | ×1.0       |
| 1          | Tense      | ×1.2       |
| 2          | Hostile    | ×1.5       |
| 3          | Blood-feud | ×2.0       |
| 4          | Vengeance  | No trade   |

---

## 6. Contracts

### Contract Types

10 templates, each with reputation gate, pay, duration, risk, and minimum band size. From `contracts.py`.

| Contract          | Min Rep | Base Pay (silver) | Duration (days) | Risk     | Min Band | Skills Valued               |
| ----------------- | ------: | ----------------: | --------------- | -------- | -------: | --------------------------- |
| Escort Duty       |       0 |                30 | 5-15            | Low      |        5 | Command, Navigate           |
| Settlement Guard  |       1 |                60 | 20-60           | Moderate |        8 | Command, Intimidate         |
| Raiding Party     |       2 |                80 | 3-10            | High     |       10 | Axes, Stealth, Navigate     |
| Bounty Hunt       |       1 |                50 | 7-21            | Moderate |        4 | Track, Bows                 |
| Barrow Clearing   |       2 |               100 | 1-3             | High     |        6 | Rune-lore, Spears           |
| Debt Collection   |       1 |                25 | 3-7             | Low      |        3 | Intimidate, Bargain         |
| War Band Levy     |       3 |               150 | 30-90           | Extreme  |       12 | Command, Shields, Axes      |
| Diplomatic Escort |       3 |                70 | 7-20            | Moderate |        6 | Persuade, Navigate, Command |
| Beast Hunt        |       2 |                90 | 5-14            | High     |        6 | Track, Spears, Bows         |
| Winter Hold       |       2 |               120 | 60-120          | Moderate |       10 | Shelter, Command, Forage    |

### Season Contract Availability (Weights)

Higher weight = more likely to appear. Weight 0 = unavailable that season.

| Contract          | Long Summer | Long Dark |
| ----------------- | ----------- | --------- |
| Escort            | 3           | 1         |
| Guard             | 2           | 3         |
| Raid              | 3           | 1         |
| Bounty            | 2           | 1         |
| Barrow Clear      | 2           | 1         |
| Debt Collection   | 2           | 1         |
| War Band          | 2           | 0         |
| Diplomatic Escort | 2           | 1         |
| Beast Hunt        | 2           | 1         |
| Winter Hold       | 0           | 3         |

### Settlement Contract Pool Size

| Settlement    | Contracts Available |
| ------------- | ------------------: |
| Hamlet        |                   1 |
| Village       |                   2 |
| Large Village |                   3 |
| Small Town    |                   4 |

Feud reduces pool: `pool = pool - feud_level` (min 0).

### Contract Evaluation

Pay per fighter per day (silver):

```text
pay_per_day = base_pay / duration
pay_per_fighter_day = pay_per_day / band_size
```

Pay rating thresholds: >0.7 silver/fighter/day = good; 0.3-0.7 = fair; <0.3 = poor.

---

## 7. Feud System Data

### Feud Actions

Actions that modify a settlement's feud level toward the band. From `contracts.py`.

| Action          | Feud Change |
| --------------- | ----------- |
| Tribute         | -1          |
| Weregild        | -2          |
| Service         | -1          |
| Time Passage    | -1          |
| Atrocity        | +2          |
| Broken Contract | +1          |
| Raid Settlement | +2          |
| Killed Notable  | +1          |

Feud is clamped 0-4 after any change.

---

## 8. Recruitment

### Backgrounds (6 Recruit Types)

From `recruitment.py`. Each background defines a primary attribute boost and starting skills.

| Background | Primary Attr | Skills                               | Special                  |
| ---------- | ------------ | ------------------------------------ | ------------------------ |
| Farmer     | TOU          | Forage 1-2, Shelter 0-1              | —                        |
| Fisher     | NIM          | Seamanship 1-2, Forage 0-1           | —                        |
| Thrall     | TOU          | Brawl 0-1                            | -1 all non-primary attrs |
| Huscarl    | MIG          | Axes 1-3, Shields 1-2, Command 0-1   | Former house-guard       |
| Wanderer   | WIT          | Navigate 1-2, Track 0-1, Forage 0-1  | —                        |
| Outlaw     | NIM          | Blades 1-2, Deceive 0-1, Stealth 0-1 | —                        |

### Attribute Generation

```text
1. All attributes start at 5
2. Primary attribute: +1d4
3. Weakest non-primary attribute: -1d3 (min 1)
4. Thralls: additional -1 to all non-primary (min 1)
5. Veterans: +1d2 to random physical attr (MIG, NIM, or TOU)
6. Named Men: +1d2 to WIL additionally
7. All clamped 1-10
```

### Settlement Recruit Pools

| Settlement    | Pool Dice | Max Rank  | Veteran Chance | Named Man (if town) |
| ------------- | --------- | --------- | -------------- | ------------------- |
| Hamlet        | 1d4       | Common    | 0%             | —                   |
| Village       | 2d4       | Veteran   | 15%            | —                   |
| Large Village | 2d6       | Veteran   | 30%            | —                   |
| Small Town    | 3d6       | Named Man | 45%            | 5% (roll ≤ 5)       |

Reputation adds directly to pool size: `pool = dice_roll + reputation`.

### Hiring Costs (Signing Bonus)

| Rank      | Silver |
| --------- | -----: |
| Common    |      5 |
| Veteran   |     15 |
| Named Man |     30 |

First-week retainer is included in the signing cost.

### Wyrd Distribution

| Roll (d100) | Wyrd Value | Probability |
| ----------- | ---------- | ----------- |
| 01-90       | 1          | 90%         |
| 91-97       | 2          | 7%          |
| 98-99       | 3          | 2.5%        |
| 100         | 4+         | 0.5%        |

---

## 9. NPC Generation

### Backgrounds (10 Full NPC Types)

From `npc_generator.py`. Expanded from the 6 recruit backgrounds with additional specialist types. Each has primary, secondary, and weak attributes plus flavor text.

| Background | Primary | Secondary | Weak | Flavor            | Key Skills                          |
| ---------- | ------- | --------- | ---- | ----------------- | ----------------------------------- |
| Farmer     | TOU     | MIG       | WIT  | Calloused farmer  | Forage 1-2, Shelter 0-1             |
| Fisher     | NIM     | TOU       | WIL  | Salt-crusted      | Seamanship 1-2, Forage 0-1          |
| Thrall     | TOU     | MIG       | WIL  | Scarred ex-thrall | Brawl 0-1                           |
| Huscarl    | MIG     | TOU       | WIT  | Tested guard      | Axes 1-3, Shields 1-2, Command 0-1  |
| Wanderer   | WIT     | NIM       | MIG  | Long-road drifter | Navigate 1-2, Track 0-1, Forage 0-1 |
| Outlaw     | NIM     | WIT       | WIL  | Marked outlaw     | Blades 1-2, Deceive 0-1             |
| Skald      | WIT     | WIL       | MIG  | Silver-tongued    | Sagas 1-3, Persuade 1-2             |
| Hunter     | NIM     | WIT       | WIL  | Patient hunter    | Track 2-3, Bows 1-2, Forage 1       |
| Smith      | MIG     | TOU       | NIM  | Soot-blackened    | Smithing 2-3, Leatherwork 0-1       |
| Healer     | WIT     | WIL       | MIG  | Herb-wise healer  | Heal 2-3, Forage 1-2                |

### NPC Attribute Generation

```text
1. All attributes start at 5
2. Primary attribute: +1d4
3. Secondary attribute: +0d2 (0-2)
4. Weak attribute: -1d3 (min 1)
5. Thralls: -1 all non-primary (min 1)
6. Veterans: +1d2 to random physical attr
7. Named Men: additional +1d2 to WIL
8. All clamped 1-10
```

### Physical Description Tables

Randomly combined into appearance string: `"[age], [build], [hair] hair, [face]"`.

**Builds (10):** Gaunt, lean, wiry, stocky, broad-shouldered, tall, squat, thick-limbed, rangy, heavy-set.

**Hair (10):** Dark, rust-red, straw-blond, grey-streaked, black, iron-grey, fox-red, ash-brown, white-blond, bald.

**Faces (13):** Scarred cheek, broken nose, deep-set eyes, sharp jaw, weather-beaten, pockmarked, long scar across brow, a missing ear, pale eyes, thick brows, thin lips, burn scars along the neck, tattoo across the temple.

**Ages (5):** Young (16-20), prime (21-30), seasoned (31-40), weathered (41-50), old (51+).

### Personality Traits (20)

Each NPC gets one personality descriptor:

1. Quiet and watchful
2. Quick to anger
3. Dry-humored
4. Pious and superstitious
5. Greedy but reliable
6. Loyal to a fault
7. Cowardly under pressure
8. Cruel when drunk
9. Oddly cheerful
10. Sullen and withdrawn
11. Boastful storyteller
12. Cunning and patient
13. Honest to a fault
14. Haunted by old deeds
15. Ambitious and scheming
16. Gentle except in battle
17. Perpetually cold
18. Obsessed with omens
19. Fiercely independent
20. Respects only strength

### Named Man Triggers (12)

Personal loyalty flashpoints. When triggered, captain must pass a Command check or Named Man loses 1 loyalty.

1. Captain shows weakness in combat
2. Band retreats from a winnable fight
3. Personal insult goes unanswered
4. A blood-kin is harmed by the band
5. Captain breaks an oath or sworn word
6. Loot is divided unfairly
7. Band attacks unarmed folk without cause
8. Captain consults a seiðr-worker (if male traditionalist)
9. Band enters a barrow against omens
10. A Named Man companion is executed or sacrificed
11. Captain shows mercy to a sworn enemy
12. The band stays too long in one place (restless)

### Named Man Agendas (12)

Personal goals. Moving toward an agenda: +1 loyalty. Ignoring it 30+ days: -1 loyalty/month.

1. Seek vengeance against a specific person or settlement
2. Accumulate enough silver to buy farmland back home
3. Find a lost sibling taken by slavers
4. Earn enough fame to return home with honor
5. Locate a specific barrow or rune-stone
6. Kill a particular beast that scarred them
7. Become captain of their own band
8. Find a cure for a wasting sickness in their family
9. Repay a weregild debt to a powerful jarl
10. Prove themselves worthy of a specific person's hand
11. Discover the truth about a parent's death
12. Collect saga-worthy deeds to be remembered after death

### Tavern NPCs

The `tavern` command generates 1-N social NPCs with common backgrounds suitable for inn/tavern encounters. Uses the same generation rules but limits ranks to common.

---

## 10. Encounter Tables

### How Encounters Work

From `encounter.py`. Encounters are checked when the band travels or camps.

**Step 1 — Does an encounter happen?**

```text
base_chance = season encounter_chance (Summer: 40%, Dark: 50%)
modified_chance = base × time_of_day_mod × reputation_mod
```

If `random() > modified_chance`, no encounter.

**Step 2 — Roll on terrain table** (d100, consult appropriate table).

**Step 3 — Supernatural filter.** If the encounter is supernatural and `random() > supernatural_season_mod × supernatural_time_mod`, suppress it.

### Season Modifiers

| Season      | Encounter Chance | Beast Mod | Supernatural Mod |
| ----------- | ---------------- | --------- | ---------------- |
| Long Summer | 40%              | ×1.0      | ×0.5             |
| Long Dark   | 50%              | ×1.3      | ×1.5             |

### Time-of-Day Modifiers

| Time  | Encounter Mod | Combat Mod | Supernatural Mod |
| ----- | ------------- | ---------- | ---------------- |
| Dawn  | ×0.8          | -10        | ×0.5             |
| Day   | ×1.0          | +0         | ×0.3             |
| Dusk  | ×1.2          | +0         | ×1.0             |
| Night | ×1.5          | -20        | ×1.5             |

High reputation (3+) reduces encounter chance by 20%.

### Coast Encounters (d100)

| Roll   | Encounter      | Type         | Description                                       |
| ------ | -------------- | ------------ | ------------------------------------------------- |
| 01-15  | Trader Caravan | Combat       | Merchant caravan with 2-4 guards. May trade.      |
| 16-25  | Fishing Boat   | Social       | Fishermen near shore. News or help requests.      |
| 26-35  | Seal Colony    | Environment  | Rocky beach with seals. Forage bonus +4.          |
| 36-45  | Shipwreck      | Exploration  | Wreckage with possible salvage (3-15s, 20% trap). |
| 46-55  | Rival Band     | Combat       | 8-12 rival fighters on the same path.             |
| 56-70  | Pilgrim        | Social       | Lone pilgrim with information (80% chance).       |
| 71-80  | Storm Debris   | Environment  | Blocked path. Half-day clearance.                 |
| 81-90  | Abandoned Camp | Exploration  | Recently abandoned. 1-5s loot, 40% info.          |
| 91-95  | Sea Beast      | Combat       | Sea-troll or giant seal. Elite rank. 10-30s loot. |
| 96-100 | The Hush       | Supernatural | Silence falls. Wyrd check, -1 morale.             |

### Forest Encounters (d100)

| Roll   | Encounter        | Type         | Description                                       |
| ------ | ---------------- | ------------ | ------------------------------------------------- |
| 01-12  | Wolf Pack        | Combat       | 4-8 hungry wolves.                                |
| 13-24  | Outlaw Camp      | Combat       | 3-6 outlaws hiding in trees. 5-15s loot.          |
| 25-36  | Herb Clearing    | Environment  | Medicinal herbs. Forage +6, healing herbs.        |
| 37-48  | Hunter           | Social       | Solitary hunter with trail information (70%).     |
| 49-58  | Ancient Tree     | Supernatural | Gnarled tree with runes. Wyrd + Rune-lore checks. |
| 59-68  | Deadfall Trap    | Hazard       | Concealed pit. NIM check or 2d6 damage.           |
| 69-78  | Charcoal Burners | Social       | Simple folk, 50% info, trade available.           |
| 79-88  | Boar             | Combat       | Massive territorial boar. 5-10 food on kill.      |
| 89-95  | Barrow Mound     | Exploration  | Old barrow. 10-50s loot, 30% trap, 40% undead.    |
| 96-100 | Veil-Thinning    | Supernatural | Air shimmers, old voices. Wyrd check, -1 morale.  |

### Moors Encounters (d100)

| Roll   | Encounter       | Type         | Description                                    |
| ------ | --------------- | ------------ | ---------------------------------------------- |
| 01-15  | Fog Shapes      | Supernatural | Shapes in fog. Wyrd check, 30% becomes combat. |
| 16-30  | Lost Traveler   | Social       | Disoriented person. 30% info, 20% recruit.     |
| 31-42  | Standing Stones | Supernatural | Ring of stones. Wyrd + Rune-lore checks.       |
| 43-54  | Bog Body        | Environment  | Preserved corpse with old offerings (2-8s).    |
| 55-66  | Raiders         | Combat       | 5-8 warriors moving fast. 10-30s loot.         |
| 67-76  | Cairn Marker    | Exploration  | Trail marker. 60% info, navigation bonus.      |
| 77-86  | Exposure        | Hazard       | Relentless wind. TOU check or exhaustion.      |
| 87-93  | Shepherd        | Social       | Moorland shepherd. 50% info, 2-4 food.         |
| 94-97  | Banshee Wind    | Supernatural | Wind screams. -1 morale, Wyrd check.           |
| 98-100 | The Hush        | Supernatural | Total silence. Wyrd check, -1 morale.          |

### Mountain Encounters (d100)

| Roll   | Encounter       | Type         | Description                                        |
| ------ | --------------- | ------------ | -------------------------------------------------- |
| 01-12  | Rockslide       | Hazard       | Loose rocks. NIM check or 2d6 dmg, half-day delay. |
| 13-24  | Mountain Goats  | Environment  | Wild goats. 3-8 food (Bows check).                 |
| 25-36  | Eagle Nest      | Environment  | High vantage. Navigation bonus (WIT check).        |
| 37-48  | Abandoned Mine  | Exploration  | Boarded mine. 5-30s loot, 25% trap.                |
| 49-58  | Mountain Hermit | Social       | Reclusive hermit, possibly rune-carver. 70% info.  |
| 59-68  | Ice Bridge      | Hazard       | Natural ice bridge. NIM check or 4d6 damage.       |
| 69-78  | Giant Tracks    | Exploration  | Enormous footprints. 30% info, 15% combat.         |
| 79-88  | Cave Camp       | Environment  | Dry cave shelter. Rest bonus.                      |
| 89-95  | Troll           | Combat       | Mountain troll. Elite rank. 15-40s loot.           |
| 96-100 | Rune Wall       | Supernatural | Cliff of ancient runes. Wyrd + Rune-lore, galdr.   |

### River Encounters (d100)

| Roll   | Encounter      | Type         | Description                                         |
| ------ | -------------- | ------------ | --------------------------------------------------- |
| 01-15  | Thin Ice       | Hazard       | Ice groans. NIM check or fall through, frostbite.   |
| 16-30  | Ice Fishing    | Environment  | Good fishing spot. Forage +5.                       |
| 31-42  | Frozen Corpse  | Exploration  | Body in ice. 3-12s preserved gear.                  |
| 43-54  | Trading Post   | Social       | Riverbank outpost. Trade and info (60%).            |
| 55-66  | Bandits on Ice | Combat       | 4-7 ambushing bandits. 8-20s loot.                  |
| 67-78  | Otter Colony   | Environment  | Peaceful otter colony. Scenery.                     |
| 79-88  | Ice Crack      | Hazard       | Ice splits. Half-day reroute.                       |
| 89-95  | Drowned Dead   | Supernatural | Faces under ice. Wyrd check, -1 morale, 20% combat. |
| 96-100 | River Spirit   | Supernatural | Glowing ice, voice below. Wyrd + Seiðr checks.      |

### Ice Encounters (d100)

| Roll   | Encounter          | Type         | Description                                        |
| ------ | ------------------ | ------------ | -------------------------------------------------- |
| 01-15  | Crevasse           | Hazard       | Hidden crevasse. WIT+Nav check or 3d6 damage.      |
| 16-28  | Blizzard Pocket    | Environment  | Localized whiteout. 1d4 hours lost.                |
| 29-40  | Frozen Beast       | Exploration  | Ancient frozen creature. 20% info, Wyrd check.     |
| 41-52  | Ice Cave           | Exploration  | Cave shelter. 20% trap, 5-25s possible loot.       |
| 53-64  | Polar Bears        | Combat       | 1-2 bears, elite rank. 10-20 food on kill.         |
| 65-76  | Aurora             | Supernatural | Sky erupts in light. Wyrd check, +1 morale.        |
| 77-86  | Frostbite Exposure | Hazard       | Extreme cold. Frostbite check for all.             |
| 87-93  | Snow Shrine        | Supernatural | Ice shrine with offerings. Wyrd + Rune-lore.       |
| 94-97  | Ice Worm           | Combat       | Something vast beneath. Legendary rank, -1 morale. |
| 98-100 | The Hush           | Supernatural | Perfect silence. Wyrd check, -2 morale.            |

---

## 11. Travel Hazards

### Terrain Hazard Tables

From `travel.py`. Checked daily during travel. Each entry: (chance %, hazard, description, day penalty).

#### Coast

| Chance | Hazard     | Description                               | Day Penalty |
| ------ | ---------- | ----------------------------------------- | ----------- |
| 15%    | Rough Surf | Heavy surf blocks path. Half-day detour.  | 0.5         |
| 8%     | Rockslide  | Loose rocks injure a fighter. Heal check. | 0           |
| 5%     | Tidal Trap | Rising tide traps band. Wait 4 hours.     | 0.25        |

#### Forest

| Chance | Hazard       | Description                              | Day Penalty |
| ------ | ------------ | ---------------------------------------- | ----------- |
| 12%    | Fallen Trees | Blocked path requires clearing.          | 0.5         |
| 10%    | Predator     | Wolf pack shadows the band.              | 0           |
| 6%     | Bog          | Hidden bog slows march, risks gear loss. | 0.25        |

#### Moors

| Chance | Hazard   | Description                                   | Day Penalty |
| ------ | -------- | --------------------------------------------- | ----------- |
| 15%    | Fog Lost | Dense fog causes navigation error. WIT check. | 0.5         |
| 10%    | Sinkhole | Fighter steps into sinkhole. TOU check.       | 0           |
| 5%     | Exposure | Wind saps warmth. Extra food consumption.     | 0           |

#### Mountain

| Chance | Hazard         | Description                          | Day Penalty |
| ------ | -------------- | ------------------------------------ | ----------- |
| 18%    | Avalanche Risk | NIM check per fighter or 2d6 damage. | 0           |
| 12%    | Cliff Face     | Steep climb requires ropes.          | 0.5         |
| 8%     | Altitude       | Thin air. -5 all rolls for 1 day.    | 0           |

#### River

| Chance | Hazard   | Description                                    | Day Penalty |
| ------ | -------- | ---------------------------------------------- | ----------- |
| 15%    | Thin Ice | Ice cracks. NIM check or fall through.         | 0           |
| 10%    | Crossing | Difficult river crossing.                      | 0.5         |
| 5%     | Current  | Strong current sweeps supplies. Lose 1d6 food. | 0           |

#### Ice

| Chance | Hazard    | Description                                  | Day Penalty |
| ------ | --------- | -------------------------------------------- | ----------- |
| 20%    | Crevasse  | Hidden crevasse. WIT+Navigate check or fall. | 0           |
| 12%    | Whiteout  | Total whiteout. Full day lost.               | 1.0         |
| 8%     | Ice Quake | Ice shifts and cracks. Morale check.         | 0           |

### Exposure Food Increase

In driving snow or rime storm on moors/mountain/ice terrain, daily food consumption increases by 30% (`×1.3`).

---

## 12. Band State Structure

### Band Template

From `band_manager.py`. The canonical band state object:

```text
name              — Band name (string)
captain           — Captain's name (string)
archetype         — "tyrant", "standard", "fraternal", "kin_clan"
reputation        — 0-5 (integer)
morale            — 1-5 (integer, default 4 = Steady)
treasury_silver   — Current silver (integer)
treasury_goods    — Trade goods value (integer)
debts_owed        — Outstanding debts (integer)
credits_pending   — Money owed to band (integer)
current_contract  — Active contract or null
feud_tracker      — Dict of settlement_name → feud_level
members           — List of member objects
year              — Current year (default 312)
day_of_year       — 1-360
location          — Current location or null
notes             — Freeform notes list
history           — Event log list
```

### Member Template

Each band member carries this structure:

```text
name, rank, background, gender
mig, nim, tou, wit, wil, wyr     — Attributes (1-10, Wyrd 1-4+)
skills                           — Dict of skill_name → rank (0-5)
weapon, weapon_base, weapon_speed, weapon_skill
shield_skill, shield_def
armor                            — Dict: head, torso, right_arm, left_arm,
                                   legs, hands, feet (each armor value)
gear_kg                          — Equipment weight
hp, max_hp                       — Current and max health
wounds                           — List of active wounds
status                           — "active", "wounded", "dead", "deserted"
trigger                          — Named Man only: loyalty trigger
agenda                           — Named Man only: personal goal
loyalty                          — Named Man only: 1-5
```

### Default Captain Stats

When creating a new band, the captain starts with:

| Attribute | Value | Skills            |
| --------- | ----: | ----------------- |
| MIG       |     7 | Command 3, Axes 3 |
| NIM       |     6 | Intimidate 2      |
| TOU       |     6 | Shields 2         |
| WIT       |     6 | —                 |
| WIL       |     7 | —                 |
| WYR       |     2 | —                 |

Armor: Head 4, Torso 5, Arms 3. Shield def 3. Gear 12 kg.

---

## 13. Morale Modifier Tables

### Roll Modifiers by Morale Level

From `morale.py`. Applied to all resolution rolls.

| Morale Level | Name     | Roll Modifier |
| ------------ | -------- | ------------- |
| 5            | Keen     | +5            |
| 4            | Steady   | +0            |
| 3            | Shaken   | -5            |
| 2            | Wavering | -10           |
| 1            | Broken   | -15           |

### Grievance Resolution Modifiers

Exact difficulty values for captain's Command/Persuade check:

| Grievance Type         | Difficulty Modifier |
| ---------------------- | ------------------- |
| Late wages             | +0                  |
| Named Man killed       | +0                  |
| Broken oath            | -15                 |
| Atrocity without gain  | -15                 |
| Stacked (3+ same type) | additional -10      |

---

## 14. Pay and Loot Values

### Weekly Retainer (Copper)

Exact values from `ledger.py`. These are the copper amounts.

| Rank          | Weekly Pay (copper) | Silver Equiv |
| ------------- | ------------------: | -----------: |
| Common        |                  20 |           2s |
| Veteran       |                  30 |           3s |
| Named Man     |                  50 |           5s |
| Shield-maiden |                  30 |           3s |

### Daily Mission Pay (Copper)

| Rank      | Daily Pay (copper) | Silver Equiv |
| --------- | -----------------: | -----------: |
| Common    |                  5 |           5c |
| Veteran   |                 10 |           1s |
| Named Man |                 15 |        1s 5c |

### Loot Division Percentages

| Archetype | Captain | Named Men | Veterans | Commons |
| --------- | ------: | --------: | -------: | ------: |
| Tyrant    |     60% |       20% |      12% |      8% |
| Standard  |     40% |       25% |      20% |     15% |
| Fraternal |     25% |       25% |      25% |     25% |
| Kin-Clan  |     20% |       20% |      25% |     35% |

### Non-Payment Consequences (d100)

Checked when wages 14+ days late (retainer) or 3+ days late (mission).

| Roll   | Consequence                                       |
| ------ | ------------------------------------------------- |
| 01-15  | D3 men desert at night. May sell information.     |
| 16-30  | Named Man demands written debt acknowledgment.    |
| 31-50  | Band becomes Shaken (-5 all) for the week.        |
| 51-70  | Confrontation. Command check or Morale -1.        |
| 71-85  | Quiet muttering. No effect this week.             |
| 86-100 | Men accept for now. Next non-payment rolls twice. |

---

## 15. Time Costs

### Exact Activity Times

From `calendar_sim.py`. Both absolute and game-turn values.

| Activity              | Time Cost     |  Days | Quarter-days |
| --------------------- | ------------- | ----: | -----------: |
| March (full day)      | 1 day         |  1.00 |            4 |
| Forage                | 1 quarter-day |  0.25 |            1 |
| Barrow Clearing       | 1-3 days      |  2.00 |            8 |
| Recruitment Search    | 1 quarter-day |  0.25 |            1 |
| Heal (treat wounds)   | 1 quarter-day |  0.25 |            1 |
| Galdr (rune carving)  | 1-4 hours     | 0.125 |            1 |
| Seiðr (spirit trance) | 1+ hours      |  0.25 |            1 |
| Wyrd-reading          | 10-30 minutes |  0.05 |            0 |
| Pay Ritual            | 1 hour        |  0.04 |            0 |
| Camp Setup            | 2 hours       |  0.08 |            1 |
| Rest (full day)       | 1 day         |  1.00 |            4 |

### Food Consumption Rates

| Season      | Food Units / Person / Day |
| ----------- | ------------------------- |
| Long Summer | 1.0                       |
| Long Dark   | 1.2                       |

---

## Name Lists

### Male Names (44)

Bjorn, Eirik, Gunnar, Halvar, Ivar, Kjartan, Leif, Magnus, Njall, Olaf, Ragnar, Sigurd, Thorvald, Ulf, Vidar, Yrjar, Asmund, Brynjar, Dagfinn, Einar, Frode, Grim, Harald, Ingvar, Jostein, Ketil, Ljot, Mord, Nori, Orm, Petur, Rolf, Snorri, Torsten, Ubbe, Varg, Yngvar, Hakon, Thrain, Skuli, Egil, Bard, Stein, Rorik.

### Female Names (24)

Astrid, Brynhild, Dagny, Eira, Freydis, Gudrun, Halla, Inga, Jorunn, Katla, Ljufa, Magnhild, Nessa, Oddny, Ragnhild, Sigrid, Thora, Ulfhild, Vigdis, Ylva, Asa, Bergliot, Dalla, Hervor.

### Bynames (30)

the Scarred, the Quiet, One-Eye, Blackhand, the Red, the Lame, Ironside, the Young, the Old, Crow-feeder, the Bitter, the Tall, Half-troll, the Lean, Frostbeard, Skullsplitter, the Grey, Oxback, Shieldbreaker, the Lucky, the Grim, Stonefist, the Wanderer, the Swift, Boneless, Wolftooth, Rimewatcher, Deepcaller, Shorthair, Longstride.

Gender: 85% male, 15% female. Byname applied 30-35% of the time.

### Settlement Leader Names (10)

Thorolf, Sigvat, Brynjar, Kolbein, Hallstein, Gudmund, Arnkel, Hrafn, Thorgrim, Ketil. Title: "elder" (hamlet/village), "jarl" (large village/town).
