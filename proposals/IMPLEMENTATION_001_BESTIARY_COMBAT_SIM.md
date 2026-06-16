# Bestiary → Combat Sim: Full Implementation Plan

## Status

Batches 1–6 complete. Batch 7+ next. 672 tests passing.

---

## Problem Statement

The bestiary YAML files define rich creature mechanics across six files
(animals, undead, humans, supernatural, named_enemies, world_bosses)
and 30+ creatures. The `combat_sim.py` currently implements only a thin
slice of these properties — mainly the undead work added in the last
session. The vast majority of creature abilities, resistances, weaknesses,
phased combat behaviours, and auto-load logic remain unimplemented.

This plan catalogs every property gap and organises the work into ten
depency-ordered batches.

---

## Creature Inventory

| File                  | IDs                                               | Categories                      |
| --------------------- | ------------------------------------------------- | ------------------------------- |
| `animals.yaml`        | ANI_WOLF_01-03, ANI_BEAR_01-02                    | predator                        |
| `undead.yaml`         | UND_DRAUGR_01-05, UND_HAUG_01-02                  | draugr, haugbui                 |
| `humans.yaml`         | HUM_BANDIT_01-05                                  | bandit                          |
| `named\_enemies.yaml` | BOS_RIVAL_01-07+                                  | rival_leader                    |
| `supernatural.yaml`   | SUP_SPIRIT_01-04, SUP_VEIL_01-04, SUP_WILD_01-02+ | spirit, veil_entity, wilderness |
| `world\_bosses.yaml`  | WBS_01-02+                                        | world_boss                      |

---

## What Is Already Implemented

| Feature                      | Location                                                    |
| ---------------------------- | ----------------------------------------------------------- |
| `is_undead` field on Fighter | `combat_sim.py` Fighter dataclass                           |
| `resistances` field          | Fighter dataclass, only `"bleeding"` has live effect        |
| `traits` field               | Fighter dataclass                                           |
| `unfeeling` trait            | No wound penalty, no DAZED/STAGGERED                        |
| `terrifying_presence` trait  | Pre-battle WIL check → STAGGERED 2 rounds                   |
| `combat_memory` trait        | Enables counter-attacks for undead                          |
| `ancient_resilience` trait   | 0.5× incoming damage multiplier                             |
| `from_dict` / `to_dict`      | Includes all undead fields                                  |
| Armor dict                   | Per-location integer values, populated from input JSON only |
| Pre-battle dispatch          | Only `terrifying_presence` handled                          |

---

## Master Gap Registry

### Category A — Natural Armor Parsing

Armor values in YAML are text strings. No parser converts them to `Fighter.armor`
integers when loading from the bestiary.

Required mapping (loader-side):

| YAML Text                                                     | Torso AR | Head AR | Notes                                    |
| ------------------------------------------------------------- | -------- | ------- | ---------------------------------------- |
| `"None"` / `"Burial Shroud"` / `"Rags"`                       | 0        | 0       |                                          |
| `"Distended Skin"`                                            | 0        | 0       |                                          |
| `"Leather Jerkin"` / `"Boiled Leather"` / `"Studded Leather"` | 1        | —       |                                          |
| `"Oiled Leather"` / `"Hardened Leather with Bone Plates"`     | 2        | —       |                                          |
| `"Chain Mail"` / `"Ring Mail"` / `"Ill-Fitting Chain Mail"`   | 3        | —       |                                          |
| `"Looted Mail Shirt"` / `"Old Chain Mail"`                    | 3        | —       |                                          |
| `"Rotted Leather over Mail Fragments"`                        | 2        | —       | degraded                                 |
| `"Layered Mail"`                                              | 4        | —       |                                          |
| `"Ancient Lamellar"`                                          | 4        | —       |                                          |
| `"Fused Rusted Mail"`                                         | 4        | —       | corrosion no mechanical effect           |
| `"Thick Hide (AR 2)"`                                         | 2        | —       | natural                                  |
| `"Dense Hide (AR 3)"`                                         | 3        | —       | natural                                  |
| `"Stone Skin (natural, as plate)"`                            | 5        | 5       | also triggers `cutting_resistance`       |
| `"Reality-Reject Skin (acts as mail)"`                        | 3        | —       |                                          |
| `"Bark-Plate (natural)"`                                      | 3        | —       |                                          |
| `"Incorporating"` / `"Incorporeal"`                           | 0        | 0       | handled by `physical_weapons` resistance |
| `"Leather Cap"`                                               | —        | 1       |                                          |
| `"Corroded Helmet"`                                           | —        | 2       |                                          |
| `"Steel Helm"` / `"Iron Helm"` / `"Nasal Helm"`               | —        | 3       |                                          |
| `"Bronze Crown-Helm"`                                         | —        | 3       |                                          |
| `"Thick Skull (AR 2)"`                                        | —        | 2       | natural                                  |

### Category B — Resistance System (Unexpanded)

Only `"bleeding"` has a live mechanical effect. All others are stored but ignored.

| Resistance Tag                    | Required Effect                    | Creatures Using It                               |
| --------------------------------- | ---------------------------------- | ------------------------------------------------ |
| `"fear"`                          | WIL checks vs fear auto-pass       | ANI_WOLF_03, ANI_BEAR_02, undead, SUP_WILD_01    |
| `"cold"`                          | Halve cold-typed incoming damage   | most undead, Frost-Wraith, Troll                 |
| `"pain"` / `"pain_penalties"`     | Treat as `unfeeling` trait         | ANI_BEAR_01-02, BOS_RIVAL_02                     |
| `"piercing"`                      | Halve thrust/piercing damage       | UND_DRAUGR_04 (Bloated Draugr)                   |
| `"physical_weapons"`              | Immune to all physical attacks     | SUP_SPIRIT_01/04, SUP_VEIL_01/03, SUP_WILD_02    |
| `"cutting_weapons"`               | Immune to cut-typed damage         | SUP_WILD_01 (Troll stone skin)                   |
| `"non-magical weapons"`           | 0.5× from non-silver, non-magical  | UND_DRAUGR_05 (already via `ancient_resilience`) |
| `"all_physical"` / `"all_damage"` | Fully untargetable by combat       | SUP_VEIL_02, SUP_VEIL_03                         |
| `"intimidation"`                  | WIL vs intimidation auto-pass      | BOS_RIVAL_05 (Gunnar)                            |
| `"fear_from_undead"`              | Only specific fear-source immunity | BOS_RIVAL_06 (Bryn)                              |
| `"cold_immune"`                   | Full cold immunity                 | WBS_01 (Barrow Tide)                             |

### Category C — Weakness System (Not Implemented)

| Weakness Tag      | Required Effect                                                                     | Creatures With It                  |
| ----------------- | ----------------------------------------------------------------------------------- | ---------------------------------- |
| `"fire"`          | 1.5× damage from fire-type attacks                                                  | all draugr, wolves, Troll, spirits |
| `"silver"`        | Silver-flagged weapons bypass `ancient_resilience`; same as normal vs non-resistant | draugr, spirits                    |
| `"decapitation"`  | Mortal head wound = instant destroy                                                 | UND_DRAUGR_01-03                   |
| `"sunlight"`      | d6 damage per round in daylight terrain                                             | UND_DRAUGR_02/05, SUP_WILD_01      |
| `"loud_noise"`    | WIL check or flee from sustained noise                                              | ANI_WOLF_01-02                     |
| `"iron"`          | Spirits take direct damage from iron contact                                        | SUP_SPIRIT_02-03, SUP_VEIL_01      |
| `"spear_set"`     | Double damage from readied spear on charge                                          | ANI_BEAR_01-02                     |
| `"outnumbered"`   | Flee at earlier HP threshold                                                        | ANI_WOLF_02                        |
| `"fire_aversion"` | Forced distance from fire source in skirmish                                        | SUP_WILD_02                        |
| `"hearth_warmth"` | Cannot exist indoors with active fire                                               | SUP_WILD_02                        |

### Category D — New sim_traits (Animal)

| Trait Key           | Mechanic                                                                                                    | Source Creature          |
| ------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------ |
| `pack_tactics`      | +1 attack per living packmate in same fight (max +3)                                                        | ANI_WOLF_01, ANI_WOLF_03 |
| `hamstring`         | On crit: apply HAMSTRUNG condition — stamina recovery halved for remainder                                  | ANI_WOLF_01              |
| `starvation_frenzy` | Ignore first wound penalty as if `unfeeling` for one instance                                               | ANI_WOLF_03              |
| `terrifying_charge` | First attack in round 1 (or after PRONE opponent) deals +2 damage                                           | ANI_BEAR_01              |
| `maul_bite`         | After successful GRAPPLE, each subsequent round: automatic bite (weapon_base damage) without a new hit roll | ANI_BEAR_01-02           |
| `den_fighter`       | +20 attack modifier while terrain tag = `"cave"`, `"barrow"`, or `"den"`                                    | ANI_BEAR_02              |
| `crushing_weight`   | Grapple → target takes 4 automatic damage per round while held                                              | ANI_BEAR_02              |
| `territorial_rage`  | Below 50% HP: +1 to all attack rolls                                                                        | ANI_BEAR_02              |

### Category E — New sim_traits (Undead)

| Trait Key                   | Mechanic                                                                                                                         | Source Creature              |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| `deathgrip_1`               | Opponent's SHOVE-to-break-grapple opposed check: target gets -10 modifier                                                        | UND_DRAUGR_01                |
| `deathgrip_2`               | Opponent's SHOVE-to-break-grapple: -20 modifier                                                                                  | UND_DRAUGR_02, UND_DRAUGR_05 |
| `dark_hardened`             | +1 TOU effective while terrain = barrow/cave                                                                                     | UND_DRAUGR_02                |
| `slow_init`                 | Always acts last in initiative (initiative score = 0)                                                                            | UND_DRAUGR_04                |
| `foul_stench`               | Each round attacker is within melee range: TOU check (50%) or -5 to all actions                                                  | UND_DRAUGR_04                |
| `corpse_burst_4_2`          | On death: AOE — every fighter within 2 paces takes 4 damage, TOU check to halve                                                  | UND_DRAUGR_04                |
| `nauseating_burst`          | On death: TOU check or WINDED 3 rounds (separate from damage)                                                                    | UND_DRAUGR_04                |
| `relentless_advance`        | Bloodied trigger at ≤50% HP: wound_penalty forced to 0, +1 MIG for rest of fight                                                 | UND_DRAUGR_02                |
| `last_stand`                | Bloodied trigger at ≤50% HP: +1 NIM, +1 shield_def if shielded                                                                   | UND_DRAUGR_03                |
| `ancient_fury`              | Bloodied trigger at ≤50% HP: +1 MIG, each hit adds d4 cold damage                                                                | UND_DRAUGR_05                |
| `command_dead`              | In skirmish: once per round as free action, grant +10 attack to one allied undead fighter                                        | UND_DRAUGR_05                |
| `raise_fallen_once`         | Once per encounter: when an enemy drops, create new Restless Dead Fighter with that enemy's MIG/2, TOU/2, add to attacker's side | UND_DRAUGR_05                |
| `death_rattle`              | On death: narrative note that nearby undead are alerted (no combat effect in duel mode)                                          | UND_DRAUGR_01                |
| `weapon_throw_on_death`     | On death: one final attack at full weapon_base against killer (no stance/armor bypass)                                           | UND_DRAUGR_03                |
| `phase_through_stone`       | 50% miss chance for all attacks against this fighter (haugbui phase)                                                             | UND_HAUG_01                  |
| `armor_bypass_supernatural` | Attacks ignore physical armor entirely (Grave-Cold Touch)                                                                        | UND_HAUG_01-02               |
| `territorial_fury_barrow`   | +20 attack modifier while in barrow innermost chamber context flag                                                               | UND_HAUG_01                  |
| `choking_darkness`          | Pre-battle: attacker's WIT-based perception checks at -20 for 2 rounds (darkness)                                                | UND_HAUG_01                  |
| `dormant_trigger`           | Does not act until opponent takes a specified action (loot/attack/cross threshold) — skirmish only                               | UND_HAUG_02                  |

### Category F — New sim_traits (Supernatural)

| Trait Key                | Mechanic                                                                                                  | Source Creature                               |
| ------------------------ | --------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| `incorporeal`            | All physical weapon attacks automatically miss; only fire, iron, or seidr may damage                      | SUP_SPIRIT_01/04, SUP_VEIL_01/03, SUP_WILD_02 |
| `warmth_drain`           | Each round in melee contact: d4 cold damage + WIL -1 (temporary, stacks per fighter)                      | SUP_VEIL_01                                   |
| `courage_sap`            | Each round: WIL check (50%) or gain FLEEING condition — fighter uses entire turn fleeing                  | SUP_VEIL_01                                   |
| `domain_bonus_3`         | While terrain flag matches creature's home: +3 to MIG, NIM, TOU, WIT, WIL                                 | SUP_SPIRIT_02                                 |
| `bound_territory`        | Cannot pursue beyond own domain — treated as disengaged if opponent crosses boundary                      | SUP_SPIRIT_02                                 |
| `water_strength`         | While terrain = water: +3 MIG, +2 TOU                                                                     | SUP_SPIRIT_03                                 |
| `lure_song`              | Pre-battle WIL check (40%): target must spend first d4 actions moving toward creature                     | SUP_SPIRIT_03                                 |
| `shapeshifter`           | WIT check (50%) to recognise true form; until recognised, creature gets +20 on first attack from surprise | SUP_SPIRIT_03                                 |
| `stone_skin`             | Natural plate armor (AR 5 torso/head), cutting-typed attacks deal 0 damage                                | SUP_WILD_01 (Troll)                           |
| `sunlight_petrification` | Each round terrain = daylight: take d6 damage; after 3 cumulative rounds, is_down=True (petrified)        | SUP_WILD_01                                   |
| `crushing_grip_3`        | Grapple break (SHOVE) opposed check: target at -30; d8 grapple damage per round                           | SUP_WILD_01                                   |
| `regeneration_1`         | Heal 1 HP after each round (not round fighter is downed); counts as passive between rounds                | SUP_WILD_01                                   |
| `killing_cold_contact`   | On any successful hit: target gains FROSTBITTEN condition — d4 damage per round for d4 rounds             | SUP_WILD_02                                   |
| `cold_aura`              | Every round opponent is within melee range: -10 to NIM and MIG attack mods                                | SUP_WILD_02                                   |
| `fire_aversion`          | Cannot move into melee with fire-weaponed opponent; takes d4 damage per round adjacent to large fire      | SUP_WILD_02                                   |
| `wrong_geometry`         | First attack of encounter ignores opponent's reaction — NIM check (55%) to avoid or hit is automatic      | SUP_VEIL_04                                   |
| `reality_stutter`        | All opponents get -20 to attacks after first 3 rounds (movement prediction disrupted)                     | SUP_VEIL_04                                   |
| `seidr_hunger`           | If opponent has WYR ≥ 4: attacker gains +10 to attack that target specifically                            | SUP_VEIL_04                                   |
| `nightmare_drain`        | Sleep-mode only: each "round" of sleep, WIL check or lose 1 WIL temporarily                               | SUP_SPIRIT_01 (Mara)                          |
| `sleep_paralysis`        | Sleep-mode only: target cannot act; WIL check each round to wake                                          | SUP_SPIRIT_01 (Mara)                          |
| `dread_aura`             | WIL check each round (55%); on fail, cumulative -1 to all rolls (max -3)                                  | SUP_VEIL_03                                   |
| `cold_burst_aoe`         | On provoked action: d6 cold AOE in 2-pace radius (Rune-Ghost)                                             | SUP_SPIRIT_04                                 |

### Category G — New sim_traits (Named / Bosses)

| Trait Key                  | Mechanic                                                                                  | Source Creature       |
| -------------------------- | ----------------------------------------------------------------------------------------- | --------------------- |
| `blackwine_rage`           | First time wounded: +2 MIG for next 3 rounds                                              | BOS_RIVAL_01 (Sigrid) |
| `bone_gnaw`                | While GRAPPLED: once per round, free bite attack — weapon_base 4, ignores all armor       | BOS_RIVAL_02 (Hrafn)  |
| `relentless_no_crit`       | First CRITICAL wound received: downgrade to serious (ignore crit effect once)             | BOS_RIVAL_02 (Hrafn)  |
| `read_the_field_once`      | Once per fight: when opponent hits, force a reroll — choose the worse result for attacker | BOS_RIVAL_01 (Sigrid) |
| `fog_fighter`              | No attack/defense penalties from low-visibility or BLINDED condition                      | BOS_RIVAL_03 (Eerik)  |
| `patient_strike`           | If fighter chose GUARD last round: +20 to next round's attack roll                        | BOS_RIVAL_03 (Eerik)  |
| `tactical_withdrawal_once` | Once per fight: can disengage without triggering opponent's free attack                   | BOS_RIVAL_03 (Eerik)  |
| `desperate_fury`           | Below 50% HP: +20 to all attack and defense rolls                                         | BOS_RIVAL_04 (Ylva)   |
| `veteran_eye`              | Identifies lowest-HP opponent; +10 attack when targeting them                             | BOS_RIVAL_05 (Gunnar) |
| `last_stand_25`            | Below 25% HP: +3 weapon_base damage                                                       | BOS_RIVAL_05 (Gunnar) |
| `shield_wall_master`       | In skirmish with 2+ allies: +2 effective armor to torso                                   | BOS_RIVAL_05 (Gunnar) |
| `barrow_wise`              | +20 to WIT-based checks vs undead (perception, lore); flavor effect in narrative          | BOS_RIVAL_06 (Bryn)   |
| `fire_bearer_torchbonus`   | Torch/fire weapon attacks deal +2 damage vs undead (is_undead=True targets)               | BOS_RIVAL_06 (Bryn)   |
| `rally_allies`             | In skirmish: once per round, one allied fighter recovers 3 stamina                        | BOS_RIVAL_01/05       |

### Category H — Bloodied Phase System (Generic)

No creature currently has a triggered mid-combat phase transition. This system
is needed for:

- UND_DRAUGR_02: Relentless Advance at ≤50% HP
- UND_DRAUGR_03: Last Stand Formation at ≤50% HP
- UND_DRAUGR_05: Ancient Fury at ≤50% HP
- ANI_BEAR_02: Territorial Rage at ≤50% HP
- ANI_WOLF_03: Starvation Frenzy (initial, not triggered)
- SUP_WILD_01: Berserk Rage at ≤50% HP
- SUP_WILD_02: Blizzard Scream at ≤50% HP
- SUP_VEIL_04: Reality Hemorrhage at ≤50% HP
- BOS_RIVAL_01: Blackwine Rage on first wound
- BOS_RIVAL_05: Last Stand at ≤25% HP

### Category I — On-Death Effects

No creature currently has a dispatched on-death effect. Needed for:

- UND_DRAUGR_01: Death Rattle — alert nearby undead
- UND_DRAUGR_03: Weapon Throw — final attack on killer
- UND_DRAUGR_04: Corpse Burst — AOE 4 damage in 2-pace radius
- UND_DRAUGR_05: Death Command — all remaining undead gain +1 MIG
- ANI_BEAR_01: nothing mechanical
- SUP_WILD_01: Petrification Cascade — grappled adjacent fighters take damage
- SUP_WILD_02: Flash Freeze — AOE cold on all nearby
- SUP_VEIL_04: Veil Snap — d8 AOE damage

### Category J — Bestiary Loader (Not Implemented)

No function loads a Fighter from a YAML bestiary entry. All current
sim inputs require hand-crafted JSON. This is the foundational missing piece.

---

## Implementation Batches

---

### Batch 1 — Bestiary Loader (`scripts/bestiary_loader.py`)

**Goal:** One function call loads any bestiary entry as a Fighter.
All downstream batches depend on this.

- [x] Create `scripts/bestiary_loader.py`
- [x] Function `load_all_bestiaries(data_dir) -> dict[str, dict]` — loads
      all 6 YAML files, merges into one id→entry dict
- [x] Function `parse_armor_text(armor_dict) -> dict[str, int]` — converts
      the YAML armor text entries to numeric AR values per location using
      the Category A mapping table above
- [x] Function `pick_weapon_skill(skills_list) -> int` — find highest
      combat-relevant skill (Brawl, Swords, Axes, Spears, Bows, Knives)
      and return its rank
- [x] Function `pick_weapon_from_gear(gear) -> tuple[str, int, int, str]`
      — returns (weapon_name, base_damage, speed, type) from first weapon
      entry; returns unarmed fallback if empty
- [x] Function `entry_to_fighter(entry) -> Fighter` — full mapping:
  - [x] `mig/nim/tou/wit/wil` from `entry.stats`
  - [x] `hp` from `entry.hp`
  - [x] `weapon_skill` from `pick_weapon_skill`
  - [x] `weapon_base`, `weapon_speed`, `weapon_type` from `pick_weapon_from_gear`
  - [x] `armor` from `parse_armor_text`
  - [x] `shield_skill`, `shield_def` from gear.weapons where type=shield
  - [x] `resistances` from `entry.resistances`
  - [x] `traits` from `entry.sim_traits` (where present) + auto-derived from abilities strings
  - [x] `is_undead` from `entry.is_undead` (default False)
- [x] Function `load_enemy(enemy_id, data_dir) -> Fighter` — convenience
      single-ID loader
- [x] CLI entry: `python bestiary_loader.py ANI_WOLF_01` prints Fighter JSON
- [x] Write pytest: 5 creatures from different files load without error
- [x] Write pytest: `parse_armor_text` returns correct numeric values for 10 test cases
- [x] Write pytest: `load_enemy("UND_DRAUGR_05")` produces Fighter with
      `is_undead=True`, `"ancient_resilience"` in traits, `"bleeding"` in resistances

---

### Batch 2 — sim_traits Expansion in YAML + Schema

**Goal:** Every creature has a complete `sim_traits` list matching the
new trait keys from Categories D, E, F, G above. Currently most creatures
have no `sim_traits` key at all.

- [x] Add `sim_traits` to all entries in `animals.yaml`:
  - [x] ANI_WOLF_01: `["pack_tactics", "hamstring"]`
  - [x] ANI_WOLF_02: `["scavenger"]`
  - [x] ANI_WOLF_03: `["pack_tactics", "starvation_frenzy"]`
  - [x] ANI_BEAR_01: `["terrifying_charge", "maul_bite", "thick_hide_2"]`
  - [x] ANI_BEAR_02: `["den_fighter", "maul_bite", "crushing_weight",
"territorial_rage", "thick_hide_3"]`
- [x] Add `sim_traits` to remaining entries in `undead.yaml`:
  - [x] UND_DRAUGR_01: `["unfeeling", "deathgrip_1", "death_rattle"]`
        (was `["unfeeling"]`)
  - [x] UND_DRAUGR_02: `["unfeeling", "terrifying_presence", "deathgrip_2",
"dark_hardened", "relentless_advance"]`
  - [x] UND_DRAUGR_03: `["unfeeling", "combat_memory", "last_stand",
"weapon_throw_on_death"]`
  - [x] UND_DRAUGR_04: `["unfeeling", "slow_init", "foul_stench",
"corpse_burst_4_2", "nauseating_burst"]`
  - [x] UND_DRAUGR_05: `["unfeeling", "terrifying_presence",
"ancient_resilience", "deathgrip_2", "ancient_fury",
"command_dead", "raise_fallen_once"]`
  - [x] UND_HAUG_01: `["unfeeling", "phase_through_stone",
"armor_bypass_supernatural", "territorial_fury_barrow",
"choking_darkness"]`
  - [x] UND_HAUG_02: `["unfeeling", "armor_bypass_supernatural",
"dormant_trigger", "deathgrip_2"]`
- [x] Add `sim_traits` to `supernatural.yaml`:
  - [x] SUP_SPIRIT_01: `["incorporeal", "nightmare_drain", "sleep_paralysis"]`
  - [x] SUP_SPIRIT_02: `["domain_bonus_3", "bound_territory"]`
  - [x] SUP_SPIRIT_03: `["shapeshifter", "lure_song", "water_strength"]`
  - [x] SUP_SPIRIT_04: `["incorporeal", "cold_burst_aoe"]`
  - [x] SUP_VEIL_01: `["incorporeal", "warmth_drain", "courage_sap"]`
  - [x] SUP_VEIL_02: `[]` (area entity — simulation not applicable)
  - [x] SUP_VEIL_03: `["incorporeal", "dread_aura"]`
  - [x] SUP_VEIL_04: `["wrong_geometry", "reality_stutter", "seidr_hunger"]`
  - [x] SUP_WILD_01: `["stone_skin", "sunlight_petrification",
"crushing_grip_3", "regeneration_1"]`
  - [x] SUP_WILD_02: `["incorporeal", "killing_cold_contact",
"cold_aura", "fire_aversion"]`
- [x] Add `sim_traits` to `named_enemies.yaml`:
  - [x] BOS_RIVAL_01: `["blackwine_rage", "read_the_field_once"]`
  - [x] BOS_RIVAL_02: `["bone_gnaw", "relentless_no_crit",
"terrifying_presence"]`
  - [x] BOS_RIVAL_03: `["fog_fighter", "patient_strike",
"tactical_withdrawal_once"]`
  - [x] BOS_RIVAL_04: `["desperate_fury"]`
  - [x] BOS_RIVAL_05: `["veteran_eye", "last_stand_25",
"shield_wall_master"]`
  - [x] BOS_RIVAL_06: `["barrow_wise", "fire_bearer_torchbonus"]`
- [x] Update `BESTIARY_SCHEMA.md` Sim Traits table with all 50+ new keys
- [x] Run `npx markdownlint-cli2 --fix` on updated schema doc

---

### Batch 3 — Resistance System Expansion (`combat_sim.py`)

**Goal:** Every resistance tag in Category B has an active mechanical
effect. Damage types are tagged so resistances can act on them.

- [x] Add `damage_type: str = "physical"` field to `Fighter` (default
      `"physical"` for all standard attacks)
- [x] Add optional `damage_type` override per maneuver-type:
  - [x] `"fire"` — fire weapon/torch attacks
  - [x] `"cold"` — cold-touch, frost damage
  - [x] `"supernatural"` — Grave-Cold Touch, spectral fists
- [x] In `resolve_attack()` and `resolve_counter()`: after computing `dmg`,
      call new `apply_resistances(defender, dmg, damage_type) -> int`
- [x] Implement `apply_resistances()`:
  - [x] `"fear"` — attacker's `terrifying_presence` pre-battle check: auto-pass (no STAGGERED)
  - [x] `"cold"` — halve cold-typed incoming damage
  - [x] `"pain"` / `"pain_penalties"` — set `wound_penalty = 0` (same as `unfeeling`)
  - [x] `"piercing"` — halve damage when `damage_type == "thrust"`
  - [x] `"physical_weapons"` — set dmg = 0 unless damage_type in (`"fire"`, `"cold"`,
        `"supernatural"`, `"iron"`)
  - [x] `"cutting_weapons"` — set dmg = 0 when maneuver in (CUT, HEAVY_BLOW)
  - [x] `"non-magical weapons"` — same as `ancient_resilience` (0.5× factor; this
        replaces the trait check — both paths lead to same code)
  - [x] `"all_physical"` — set dmg = 0 for all damage types
  - [x] `"intimidation"` — pre-battle terrifying_presence check: auto-pass
  - [x] `"fear_from_undead"` — terrifying_presence check from undead: auto-pass
  - [x] `"cold_immune"` — set dmg = 0 for cold-typed
  - [x] `"bleeding"` — already implemented; assert correct
- [x] Update `from_dict` to read `damage_type` field
- [x] Write pytest: fighter with `"physical_weapons"` resistance takes 0 from CUT
- [x] Write pytest: fighter with `"cold"` resistance takes half from cold-typed
- [x] Write pytest: fighter with `"piercing"` resistance takes half from THRUST
- [x] Write pytest: `"all_physical"` fighter takes 0 from any maneuver

---

### Batch 4 — Weakness System (`combat_sim.py`)

**Goal:** Every weakness tag in Category C has a mechanical effect.

- [x] Add `weapon_properties: list = []` to Fighter — flags like `"silver"`,
      `"fire"`, `"iron"` that the weapon carries
- [x] Add `terrain: str = "open"` to Fighter — `"barrow"`, `"water"`,
      `"deep_forest"`, `"cave"`, `"daylight_open"`, `"blizzard"`, etc.
- [x] Implement `apply_weaknesses(defender, dmg, damage_type, attacker) -> int`
      after resistance pass:
  - [x] `"fire"` — if `damage_type == "fire"`: multiply dmg by 1.5
  - [x] `"silver"` — if `"silver"` in `attacker.weapon_properties` and
        defender has `"bleeding"` in resistances or `ancient_resilience`:
        ignore those resistance/trait effects for this hit
  - [x] `"decapitation"` — if hit location == `"head"` and wound_severity
        in (`"critical"`, `"mortal"`): set `defender.is_down = True` immediately
  - [x] `"sunlight"` — apply at start of each round if `attacker.terrain ==
"daylight_open"`: d6 damage to target. Track `sunlight_rounds: int`
        on Fighter; at 3 → `is_down = True` (petrify flag)
  - [x] `"loud_noise"` — WIL check at start of combat (40%): if fail,
        FLEEING condition for d4 rounds
  - [x] `"iron"` — if `"iron"` in `attacker.weapon_properties`: damage
        bypasses `"physical_weapons"` resistance
  - [x] `"spear_set"` — if attacker used GUARD last round and weapon_type =
        `"spear"`: +4 damage on next CUT/THRUST
  - [x] `"fire_aversion"` — check in `choose_stance()` and `choose_maneuver()`:
        if opponent carries fire weapon, fighter with this weakness stays DEFENSIVE
        and never closes to melee
- [x] Add `sunlight_rounds: int = 0` to Fighter dataclass
- [x] Call `apply_weaknesses()` in `resolve_attack()` after `apply_resistances()`
- [x] Write pytest: `"fire"` weakness gives 1.5× on fire-type damage
- [x] Write pytest: `"silver"` weapon on Barrow Draugr deals full damage
      (bypasses bleeding resistance)
- [x] Write pytest: `"decapitation"` weakness on mortal head wound → `is_down = True`
- [x] Write pytest: `"loud_noise"` wolf fails WIL → FLEEING condition applied

---

### Batch 5 — Animal Traits (`combat_sim.py`)

**Goal:** All animal sim_traits from Category D are mechanically active.

- [x] `pack_tactics`: add `allies_in_fight: int = 0` to Fighter. In
      `resolve_attack()`: if `"pack_tactics"` in traits, `atk_mod +=
min(fighter.allies_in_fight, 3) * 10`
- [x] `hamstring`: in `resolve_attack()` after critical success detection:
      if `"hamstring"` in attacker.traits and wound.severity in
      (`"critical"`, `"mortal"`): apply new ConditionType.HAMSTRUNG (6 rounds)
      — effect: `stamina_recovery` halved
- [x] Add `ConditionType.HAMSTRUNG` to enum (attack -0, defense -0,
      but stamina recovery penalty applied in `apply_bleeding` tick)
- [x] `starvation_frenzy`: in `_update_wound_state()`: if `"starvation_frenzy"`
      in traits and len(self.wounds) == 1: ignore the first wound's penalty
      (only bypasses penalty from the very first wound record)
- [x] `terrifying_charge`: track `charged_this_fight: bool = False`. On
      round 1 (first attack by this fighter): if `"terrifying_charge"` in
      traits: dmg_mod += 2; set flag to prevent repeat
- [x] New `ConditionType.MAUL_ACTIVE` for tracking active grapple+bite:
      added when `"maul_bite"` in traits and grapple succeeds; in round
      tick: auto-deal `attacker.weapon_base` damage to grappled opponent
      (no attack roll; TOU check to resist half)
- [x] `den_fighter`: in `resolve_attack()`: if `"den_fighter"` in traits
      and `attacker.terrain in ("cave", "barrow", "den")`: atk_mod += 20
- [x] `crushing_weight`: in `resolve_control(GRAPPLE)`: if `"crushing_weight"`
      in attacker.traits and grapple succeeds: add 4 automatic damage to
      target each subsequent round while GRAPPLED
- [x] `territorial_rage`: add `territorial_rage_active: bool = False`. In
      `_update_wound_state()`: if `"territorial_rage"` in traits and
      hp <= max_hp \* 0.5 and not flag: set flag. In `resolve_attack()`:
      if flag: atk_mod += 10
- [x] `maul_bite`: in round tick after GRAPPLE is held:
      if `"maul_bite"` in attacker.traits: auto-deal attacker.weapon_base
      damage (applying armor at grappled location)
- [x] Add `charged_this_fight: bool = False` to Fighter dataclass
- [x] Add `territorial_rage_active: bool = False` to Fighter
- [x] Write pytest: ANI_BEAR_01 with `terrifying_charge` gets +2 damage on
      round 1 first attack only
- [x] Write pytest: `territorial_rage` activates at ≤50% HP, not before
- [x] Write pytest: `pack_tactics` with `allies_in_fight=3` gives +30 atk_mod
- [x] Write pytest: `starvation_frenzy` does not protect against second wound

---

### Batch 6 — Bloodied Phase System (`combat_sim.py`)

**Goal:** Generic phased-transition system. Creatures can fire trait changes
at specific HP thresholds without hardcoding each one.

- [x] Add `bloodied_triggered: bool = False` to Fighter dataclass
- [x] Add `bloodied_at: float = 0.5` — fraction of max_hp (default 0.5)
- [x] Add `bloodied_traits: list = []` — traits added to `fighter.traits`
      when threshold is crossed
- [x] Add `bloodied_mig_bonus: int = 0` / `bloodied_nim_bonus: int = 0` —
      direct stat adjustments on bloodied
- [x] Add `death_quarter_triggered: bool = False` — for 25% threshold (Gunnar)
- [x] Add `death_quarter_traits: list = []`
- [x] In `apply_wound()`: after hp update, call `_check_bloodied()`
- [x] Implement `_check_bloodied()`: - [x] If not `bloodied_triggered` and hp <= max_hp \* bloodied_at: - [x] Set `bloodied_triggered = True` - [x] Extend `traits` with `bloodied_traits` - [x] Apply `bloodied_mig_bonus` to a new `mig_bonus: int = 0` field - [x] Apply `bloodied_nim_bonus` to new `nim_bonus: int = 0` - [x] Print bloodied event in narrative - [x] Similarly check 25% for death_quarter
- [x] Pipe `mig_bonus` into `resolve_attack()` attr checks
- [x] Pipe `nim_bonus` into defense rolls
- [x] In `entry_to_fighter()` in the loader: populate `bloodied_traits` from
      the creature's `combat_phases.bloodied` block:
  - [x] `relentless_advance` → `bloodied_traits = ["relentless_advance"]`
  - [x] `last_stand` → `bloodied_traits = ["last_stand"]`
  - [x] `ancient_fury` → `bloodied_traits = ["ancient_fury"]`
  - [x] `territorial_rage` / `berserk_rage` → `bloodied_mig_bonus = 2,
bloodied_traits = ["berserk"]`
  - [x] `desperate_fury` → `bloodied_traits = ["desperate_fury"]` (below 50%)
  - [x] `last_stand_25` → `death_quarter_traits = ["last_stand_25"]`
  - [x] `blackwine_rage` → `bloodied_traits = ["blackwine_rage"]` (first wound)
- [x] `narrative_printer`: emit bloodied event line: `[BLOODIED] Barrow
Draugr's eyes go blank — wounds no longer slow it`
- [x] Write pytest: bloodied_triggered=False before 50% HP, True after
- [x] Write pytest: bloodied_traits added to fighter.traits exactly once
- [x] Write pytest: mig_bonus applied correctly in attack resolution
- [x] Write pytest: `ancient_fury` causes +d4 cold damage on each post-bloodied hit

---

### Batch 7 — On-Death Dispatch System (`combat_sim.py`)

**Goal:** Creatures fire specific effects when they reach `is_down=True`.

- [x] Add `death_effects: list = []` to Fighter — list of effect keys
      dispatched at death
- [x] In `run_duel()` and `run_skirmish()`: after `fighter.is_down` detected,
      call `dispatch_death_effects(dead_fighter, all_fighters, result)`
- [x] Implement `dispatch_death_effects()`:
  - [x] `"death_rattle"` — append narrative: `[DEATH] Final moan echoes;
nearby dead stir` (no combat effect in duel)
  - [x] `"weapon_throw_on_death"` — execute one final `resolve_attack()`
        against killer using dead fighter's weapon stats at -20 penalty;
        append result to round actions
  - [x] `"corpse_burst_4_2"` — deal 4 damage to every fighter currently
        within the fight (except dead fighter); each may TOU-check to halve;
        append to round result
  - [x] `"nauseating_burst"` — all surviving fighters TOU-check (50%) or
        gain WINDED for 3 rounds
  - [x] `"death_command"` — all allied fighters in skirmish gain +10 attack
        for d6 rounds (Condition-like timer)
  - [x] `"veil_snap_aoe"` — deal d8 damage to all fighters within the fight;
        WIL check to halve (Rift-Spawn)
  - [x] `"flash_freeze"` — d6 cold damage to all within range (Frost-Wraith)
  - [x] `"petrification_cascade"` — any fighter with GRAPPLED condition takes
        d6 damage (Troll collapse)
- [x] In `entry_to_fighter()`: populate `death_effects` from
      `combat_phases.on_death` block keys
- [x] Narrative: death effect events print in `[ON-DEATH]` prefix block
- [x] Write pytest: `"corpse_burst_4_2"` deals 4 damage to opponent when
      Bloated Draugr dies; TOU check halves it
- [x] Write pytest: `"weapon_throw_on_death"` fires a final attack dice roll
- [x] Write pytest: multiple death effects on same creature all fire

---

### Batch 8 — Supernatural Trait Mechanics (`combat_sim.py`)

**Goal:** Incorporeal immunity, cold aura, courage sap, domain bonus.
These are the most exotic traits and require new per-round check hooks.

- [x] `incorporeal`: in `resolve_attack()` and `resolve_counter()`:
      if `"incorporeal"` in defender.traits and
      `damage_type not in ("fire", "iron", "supernatural", "seidr")`:
      set dmg = 0, print `[IMMUNE] blade passes through`
- [x] `warmth_drain`: add to per-round tick in `run_duel()`:
      if fighter A has `"warmth_drain"` in traits and fighter B is GRAPPLED
      or adjacent: deal d4 cold damage to B (no attack roll), apply -1 WIL
      temporary (new `wil_penalty: int = 0` field)
- [x] `courage_sap`: per-round tick: if fighter has GRAPPLED or is within
      melee range of creature with `"courage_sap"`: WIL check (50%);
      on fail: apply new `ConditionType.FLEEING` — spend entire turn retreating
- [x] Add `ConditionType.FLEEING` — fighter moves away; no attacks; clears
      after d4 rounds or fighter leaves melee range
- [x] `domain_bonus_3`: in `resolve_attack()` and `resolve_counter()`:
      if `"domain_bonus_3"` in attacker.traits and
      `attacker.terrain == attacker.home_terrain`: atk_mod += 15, defense
      chance += 15 (approximate +3 to relevant stats)
- [x] Add `home_terrain: str = ""` to Fighter
- [x] `water_strength`: if `"water_strength"` in attacker.traits and
      terrain == "water": mig_effective += 3, tou_effective += 2
- [x] `cold_aura`: per-round: if creature with `"cold_aura"` is in melee:
      all opponents take -10 to both attack and defense rolls
- [x] `fire_aversion`: in `choose_stance()` and `choose_maneuver()`:
      if `"fire_aversion"` in fighter.traits and opponent has fire weapon:
      return Stance.DEFENSIVE always; never choose attack maneuvers
- [x] `sunlight_petrification`: per-round: if terrain == `"daylight_open"`:
      deal d6 damage; increment `sunlight_rounds`; at 3: `is_down = True`,
      narrative prints `[PETRIFIED]`
- [x] `regeneration_1`: per-round: if `"regeneration_1"` in fighter.traits
      and not `is_down`: `hp = min(hp + 1, max_hp)`
- [x] `killing_cold_contact`: on any successful hit by creature with this
      trait: apply `ConditionType.FROSTBITTEN` — d4 damage per round for d4
      rounds (random at application time); clears on counter-heal
- [x] Add `ConditionType.FROSTBITTEN` to enum
- [x] `wrong_geometry`: first attack of fight bypasses NIM-based defense
      roll; defender must make WIT check (45%) to react; on fail: attack
      is auto-hit at normal damage
- [x] `dread_aura`: pre-battle + per-round:
      accumulate `wil_penalty` on victim; at -3 cap: no further degradation
- [x] `shapeshifter`: pre-battle: WIT check; if fail: attacker's round 1
      gets +20 attack from surprise (creature's disguise is believed)
- [x] `lure_song`: pre-battle WIL check (40%); if fail: fighter wastes
      first d4 turns (equivalent to GUARD each round); print `[ENTRANCED]`
- [x] Write pytest: `incorporeal` fighter takes 0 from CUT but nonzero from fire
- [x] Write pytest: `cold_aura` applies -10 to opponent attack each round
- [x] Write pytest: `regeneration_1` heals 1 HP per round, not above max_hp
- [x] Write pytest: `sunlight_petrification` triggers is_down at 3 rounds
- [x] Write pytest: `fire_aversion` makes AI never choose attack maneuvers vs fire weapon

---

### Batch 9 — Named Enemy / Boss Traits (`combat_sim.py`)

**Goal:** Boss-tier creature abilities that require one-shot use tracking.

- [x] Add `used_traits: set = field(default_factory=set)` to Fighter —
      tracks one-use traits that have fired
- [x] `blackwine_rage`: in `apply_wound()`: if `"blackwine_rage"` in traits
      and `"blackwine_rage"` not in used_traits: add `mig_bonus += 2` with
      a 3-round timer; add to `used_traits`
- [x] Implement `mig_bonus_timer: int = 0` on Fighter; decrement per round;
      when 0: clear `mig_bonus`
- [x] `bone_gnaw`: in `resolve_control(GRAPPLE)` success path: if `"bone_gnaw"`
      in attacker.traits: after applying GRAPPLED, add free bite attack
      (weapon_base=4, armor_bypass=all, no attack roll); append to result
- [x] `relentless_no_crit`: in `apply_wound()`: if `"relentless_no_crit"` in
      traits and `"relentless_no_crit"` not in used_traits and
      severity == "critical": downgrade severity to "serious"; add to used_traits
- [x] `read_the_field_once`: hook in `resolve_attack()` for defender with
      this trait: if opponent's attack lands and `"read_the_field_once"` not
      in used_traits: force opponent to reroll the attack with the worse of
      the two results; add to used_traits
- [x] `fog_fighter`: in `apply_resistances()`: add `"blinded"` condition
      immunity — BLINDED has no effect on this fighter
- [x] `patient_strike`: track previous round maneuver. If previous ==
      GUARD and `"patient_strike"` in traits: `atk_mod += 20` this round
- [x] `tactical_withdrawal_once`: in `choose_maneuver()`: if
      `"tactical_withdrawal_once"` in traits and fighter HP below 60% and
      not in used_traits: return GUARD with a special `disengaged=True` flag
      — opponent cannot counter-attack; add to used_traits
- [x] `desperate_fury`: if `"desperate_fury"` in traits: wired via bloodied
      system (Batch 6) — +20 atk_mod and +20 def_mod below 50% HP
- [x] `veteran_eye`: at fight start: identify opponent with lowest HP raw
      value; tag as `veteran_target: str` on Fighter; in `resolve_attack()`:
      if target == veteran_target: atk_mod += 10
- [x] `last_stand_25`: wired via bloodied system 25% threshold (Batch 6) —
      +3 weapon_base damage
- [x] `fire_bearer_torchbonus`: in `resolve_attack()`: if `"fire_bearer_torchbonus"`
      in attacker.traits and weapon_type in (`"torch"`, `"improvised"`) and
      defender.is_undead: dmg_mod += 2
- [x] `rally_allies`: in skirmish per-round tick: if `"rally_allies"` in
      fighter.traits: one allied fighter on same side recovers 3 stamina
- [x] Write pytest: `bone_gnaw` fires free bite after grapple success
- [x] Write pytest: `relentless_no_crit` fires only once
- [x] Write pytest: `read_the_field_once` fires only once; result uses
      worse of two rolls
- [x] Write pytest: `blackwine_rage` bonus expires after 3 rounds

---

### Batch 10 — Pre-Battle Phase Expansion + Narrative + Tests

**Goal:** All `combat_phases.pre_battle` effects beyond `terrifying_presence`
are dispatched. Full narrative coverage added. Integration tests run on
representative matchups.

- [x] Expand pre-battle dispatch in `run_duel()`:
  - [x] `"grave_moan"` (UND_DRAUGR_01): WIL check (55%); fail → -5 initiative
  - [x] `"stench_cloud"` (UND_DRAUGR_04): TOU check (50%); fail → WINDED 1 round
  - [x] `"commanding_presence"` (UND_DRAUGR_05): already covered by
        `terrifying_presence`; extend: failure → flee d4 rounds (not STAGGERED)
  - [x] `"shield_wall_memory"` (UND_DRAUGR_03): no duel effect (skirmish only)
  - [x] `"choking_darkness"` (UND_HAUG_01): WIT check; fail → -20 to all attacks
        for 2 rounds (simulated darkness)
  - [x] `"sleep_weight"` (SUP_SPIRIT_01): WIL check (50%); fail → -20 NIM/WIT
        for d6 rounds
  - [x] `"domain_warning"` (SUP_SPIRIT_02): domain_bonus_3 pre-activates
  - [x] `"glamour_shift"` (SUP_SPIRIT_03): triggers `shapeshifter` check
  - [x] `"ground_tremor"` (SUP_WILD_01): NIM check; fail → -5 to next action
  - [x] `"temperature_plunge"` (SUP_WILD_02): all fighters take 1 TOU debuff
        for fight duration (effective -5 to TOU-based calcs)
  - [x] `"reality_warping"` (SUP_VEIL_04): -10 to all attack rolls rounds 1–3
- [x] Add `pre_battle` events to `narrative_printer` under `[PRE-BATTLE]` prefix
- [x] Add `bloodied` event descriptions from each creature's `combat_phases.bloodied`:
      `[BLOODIED] Barrow Draugr snarls past its wounds — Relentless Advance`
- [x] Add `on_death` event descriptions from each creature's `combat_phases.on_death`
- [x] Integration tests — run 20-round duel for each:
  - [x] Voss vs ANI_BEAR_01 (thick hide, terrifying charge, maul)
  - [x] Voss vs ANI_WOLF_01 (pack tactics — use `allies_in_fight=2`)
  - [x] Voss vs UND_DRAUGR_04 (slow init, foul stench, corpse burst on death)
  - [x] Voss vs SUP_SPIRIT_01 (incorporeal weapons check — confirm 0 damage
        from physical; need iron or fire weapon to damage)
  - [x] Voss vs SUP_WILD_01 (stone skin, sunlight petrification if terrain set)
  - [x] Voss vs SUP_WILD_02 (cold aura, fire aversion, killing cold contact)
  - [x] Voss vs BOS_RIVAL_02 Hrafn (terrifying presence, bone gnaw, no-crit)
- [x] Run full pytest suite: confirm 712 tests pass
- [x] Run `npx markdownlint-cli2 --fix` on:
  - [x] `20_SIMULATION_RULES.md` (add new sim traits reference table §4.x)
  - [x] `BESTIARY_SCHEMA.md` (already updated in Batch 2)
  - [x] This planning document
- [x] Add §4.6 Animal Combat Mechanics to `20_SIMULATION_RULES.md`
- [x] Add §4.7 Supernatural Combat Mechanics to `20_SIMULATION_RULES.md`
- [x] Add §4.8 Bloodied Phase System to `20_SIMULATION_RULES.md`
- [x] Add §4.9 On-Death Dispatch to `20_SIMULATION_RULES.md`
- [x] Add §4.10 Resistance and Weakness Reference Table to `20_SIMULATION_RULES.md`

---

## Dependency Order

```text
Batch 1 (Loader)
    └─► Batch 2 (YAML sim_traits)
            └─► Batch 3 (Resistance)
            └─► Batch 4 (Weakness)
            └─► Batch 5 (Animal Traits)
            └─► Batch 6 (Bloodied Phase)
                    └─► Batch 7 (On-Death)
                    └─► Batch 8 (Supernatural)
                    └─► Batch 9 (Named Bosses)
                            └─► Batch 10 (Pre-Battle + Tests + Docs)
```

Batches 3, 4, 5 can be done in any order after Batch 2.
Batches 7, 8, 9 can be done in any order after Batch 6.

---

## Scope Exclusions

These bestiary properties are intentionally excluded from simulation scope.
They are narrative or scenario-layer effects that do not belong in combat_sim.py:

| Property                              | Why Excluded                                                    |
| ------------------------------------- | --------------------------------------------------------------- |
| `loot`                                | Post-encounter only; no combat effect                           |
| `encounter_conditions`                | Encounter spawning layer, not sim layer                         |
| `morale_break` text                   | Narrative; partially replaced by flee conditions                |
| `image_prompt`                        | Art only                                                        |
| `lore`                                | Narrative only                                                  |
| `associated_locations`                | Map layer                                                       |
| SUP_VEIL_02 `The Hush`                | Area-effect phenomenon; sim is 1v1 — not simable                |
| `group_size` multi-spawn              | Spawning layer; skirmish uses pre-configured fighters           |
| WBS (World Bosses)                    | Army-scale; combat_sim cannot represent 100+ undead wave        |
| Seidr/galdr abilities                 | Magic system not yet in combat_sim scope                        |
| `sleep_paralysis` / `nightmare_drain` | Dream-layer; outside combat rounds                              |
| `lure_song` full movement             | Zone-movement not in 1v1 sim; pre-battle check is the sim proxy |

---

## File Ownership

| Batch | Files Modified                                                                        |
| ----- | ------------------------------------------------------------------------------------- |
| 1     | `scripts/bestiary_loader.py` (new), `scripts/tests/test_bestiary_loader.py` (new)     |
| 2     | `data/bestiary/*.yaml` (all 6), `data/bestiary/BESTIARY_SCHEMA.md`                    |
| 3     | `scripts/combat_sim.py`                                                               |
| 4     | `scripts/combat_sim.py`                                                               |
| 5     | `scripts/combat_sim.py`                                                               |
| 6     | `scripts/combat_sim.py`                                                               |
| 7     | `scripts/combat_sim.py`                                                               |
| 8     | `scripts/combat_sim.py`                                                               |
| 9     | `scripts/combat_sim.py`                                                               |
| 10    | `scripts/combat_sim.py`, `20_SIMULATION_RULES.md`, `data/bestiary/BESTIARY_SCHEMA.md` |
