# Master Index — Iron Ledger: Mercenaries of the Rimevegr

The franchise bible for the Iron Ledger project — a complete index of
every data file, schema, script, test, and relationship in the
Rimevegr simulation and novel-writing system.

Last updated: 2026-04-14

---

## Project Statistics

| Category            | Count                                                 |
| ------------------- | ----------------------------------------------------- |
| Lore documents      | 24 numbered Markdown files                            |
| Data files          | 54 YAML + 3 CJK-encoded text files                    |
| Total data lines    | ~77,000                                               |
| Python scripts      | 31 modules                                            |
| Test files          | 21 files + conftest.py                                |
| Events              | 306 across 4 years (Y312–Y315)                        |
| Named NPCs          | 157 across 6 databases                                |
| Settlements         | 15 with full economy profiles                         |
| Bestiary entries    | 114+ across 7 categories                              |
| Contracts           | 60+ across 4 contract pools                           |
| Named locations     | 149 in the geographic atlas                           |
| Travel routes       | 42 connecting settlements                             |
| Barrows             | 20+ with procedural generator                         |
| Chapter outlines    | 136 across 10 volumes                                 |
| Cultural entries    | 335+ (proverbs, insults, expressions, colloquialisms) |
| Trade goods         | 91 items with seasonal pricing                        |
| Weather records     | 192 weeks (Y312–Y315)                                 |
| Total project lines | ~115,000+                                             |

---

## Quick Reference

### How To

| Task                      | Command                                                                   |
| ------------------------- | ------------------------------------------------------------------------- |
| Run the simulation engine | `python scripts/engine.py`                                                |
| Simulate combat           | `python scripts/combat_sim.py --attacker voss --defender bandit`          |
| Generate a barrow         | `python scripts/barrow_generator.py generate --size medium --age ancient` |
| Look up an NPC            | `python scripts/npc_manager.py --search "name"`                           |
| Generate a random NPC     | `python scripts/npc_generator.py`                                         |
| Query events by year      | `python scripts/event_manager.py --year 312`                              |
| Check weather history     | `python scripts/weather.py history --year 312`                            |
| Calculate supply burn     | `python scripts/logistics.py --band-size 14 --terrain forest`             |
| Manage treasury/pay       | `python scripts/ledger.py pay --week 12`                                  |
| Check morale              | `python scripts/morale.py check --event "late_pay"`                       |
| Look up bestiary          | `python scripts/bestiary.py`                                              |
| Plan travel route         | `python scripts/travel.py`                                                |
| Manage contracts          | `python scripts/contract_manager.py`                                      |
| Manage band roster        | `python scripts/band_manager.py`                                          |
| Validate all data         | `python scripts/validate_data.py`                                         |
| Run all tests             | `python -m pytest tests/ -q`                                              |
| Encode spoiler text       | `python scripts/spoiler_codec.py encode "secret text"`                    |
| Decode spoiler file       | `python scripts/spoiler_codec.py decode-file data/hidden/file.txt`        |

---

## Document Index

All numbered Markdown files live at the project root. They serve as
the world database for both novel-writing and roleplaying modes.

### Prompt and Mode Files

| File                                     | Lines | Purpose                                              |
| ---------------------------------------- | ----- | ---------------------------------------------------- |
| `00_DUNGEON_MASTER_CAMPAIGN_PLANNING.md` | 500   | DM-facing campaign planning guide                    |
| `00_NOVEL_WRITING_PROMPT.md`             | 508   | Novel authoring mode prompt (Cook-Abercrombie voice) |
| `00_ROLEPLAYING_PROMPT.md`               | 120   | Interactive text-adventure prompt for AI chat        |

### World Bible (01–24)

| File                                  | Lines | Purpose                                           |
| ------------------------------------- | ----- | ------------------------------------------------- |
| `01_RIMEVEGR_SETTING_BIBLE.md`        | 1,608 | Core world canon and high-level continuity anchor |
| `02_MASTER_INDEX.md`                  | 516   | Full repository index and cross-reference map     |
| `03_GEOGRAPHY_AND_MAP.md`             | 169   | Regional geography, travel frame, map baseline    |
| `04_CULTURE_AND_CUSTOMS.md`           | 599   | Social norms, law, hierarchy, daily life          |
| `05_ECONOMY_OF_RIMEVEGR.md`           | 845   | Economy model, currency, labor, trade             |
| `06_DICTIONARY_OF_NORSE_TERMS.md`     | 3,404 | Canon vocabulary and linguistic consistency       |
| `07_PANTHEON_AND_DIVINE_PRACTICES.md` | 294   | Divine cosmology, rites, invocation practice      |
| `08_MAGIC_OF_RIMEVEGR.md`             | 5,036 | Supernatural theory, practice, consequences       |
| `09_WEATHER_SEASONS_AND_HAZARDS.md`   | 108   | Climate and hazard baseline                       |
| `10_CALENDAR_AND_HIDDEN_EVENTS.md`    | 113   | Temporal structure and hidden-cycle logic         |
| `11_VILLAGES_AND_SETTLEMENTS.md`      | 402   | Settlement-level canon and material profile       |
| `12_POLITICAL_VILLAGES_AND_UNIONS.md` | 559   | Political topology, union dynamics, feuds         |
| `13_RIVAL_BANDS_AND_FACTIONS.md`      | 321   | External power actors and conflict pressures      |
| `14_WOLFSHEADS_OF_RIMEVEGR.md`        | 1,375 | Primary outlaw cohort dossier and operating logic |
| `15_MERCENARY_LIFESTYLE.md`           | 198   | Contracting life-cycle and practical field norms  |
| `16_NAMED_MEN_AND_ARCHETYPES.md`      | 154   | Character archetype framework                     |
| `17_CHARACTER_BIBLE.md`               | 1,085 | Deep cast continuity and relationship network     |
| `18_BARROWS_OF_RIMEVEGR.md`           | 153   | Barrow atlas and burial-site lore                 |
| `19_GAME_CONTENT_BIBLE.md`            | 931   | Structured game content tables                    |
| `20_SIMULATION_RULES.md`              | 4,775 | Full mechanical rule system                       |
| `21_BAND_SIMULATION.md`               | 131   | Runtime band state modeling                       |
| `22_MEMBER_STATBLOCKS.md`             | 749   | Member-level mechanical profiles                  |
| `23_CAMPAIGN_ARCS_AND_PLOT_SEEDS.md`  | 243   | Long-form narrative scaffolding                   |
| `24_VIGNETTES_AND_SCENES.md`          | 1,127 | Scene bank for tone, voice, and execution         |

### Meta Files

| File        | Purpose                                              |
| ----------- | ---------------------------------------------------- |
| `AGENTS.md` | Operating rules for AI agents working on the project |
| `TODO.md`   | Project status, completed prompts, expansion roadmap |

---

## Data File Index

All data files live under `data/`. YAML is the canonical format.
CJK-encoded text files contain spoiler content decoded via
`scripts/spoiler_codec.py`.

### Core State (4 files)

| File                            | Lines | Contents                                             |
| ------------------------------- | ----- | ---------------------------------------------------- |
| `data/band_state.yaml`          | 1,065 | Band roster, stats, treasury, morale, wounds         |
| `data/contracts_available.yaml` | 148   | Currently active and available contracts             |
| `data/political_state.yaml`     | 519   | 3 political unions, feuds, demographics              |
| `data/settlements.yaml`         | 882   | 15 settlements with travel routes, faction relations |

### Barrows (4 files, ~5,960 lines)

| File                                 | Lines | Contents                                          |
| ------------------------------------ | ----- | ------------------------------------------------- |
| `data/barrows/barrows.yaml`          | 758   | 20+ barrow definitions by region                  |
| `data/barrows/encounter_tables.yaml` | 1,550 | 100+ barrow combat/environmental encounters       |
| `data/barrows/loot_tables.yaml`      | 1,416 | 4-tier treasure tables (grave goods → artifacts)  |
| `data/barrows/room_templates.yaml`   | 2,235 | 60-80 procedural room types for barrow generation |

### Bestiary (7 files, ~11,840 lines)

| File                               | Lines | Contents                                         |
| ---------------------------------- | ----- | ------------------------------------------------ |
| `data/bestiary/animals.yaml`       | 907   | Wolves, bears, boar, aurochs, serpents, ravens   |
| `data/bestiary/encounters.yaml`    | 3,728 | Terrain+tier encounter tables                    |
| `data/bestiary/humans.yaml`        | 1,481 | Bandits (5 tiers), raiders, berserkers, huskarls |
| `data/bestiary/named_enemies.yaml` | 1,206 | Unique antagonists with full statblocks          |
| `data/bestiary/supernatural.yaml`  | 1,266 | Mara, trolls, Veil-shadows, nykr, rune-ghosts    |
| `data/bestiary/undead.yaml`        | 1,606 | Draugr (5 variants), haugbui, aptrgangr, wights  |
| `data/bestiary/world_bosses.yaml`  | 1,099 | Legendary adversaries (Barrow-King, Draugr-Jarl) |

### Contracts (4 files, ~5,180 lines)

| File                                         | Lines | Contents                                                  |
| -------------------------------------------- | ----- | --------------------------------------------------------- |
| `data/contracts/desperate_contracts.yaml`    | 985   | High-risk: plague relief, assassination, corpse retrieval |
| `data/contracts/faction_contracts.yaml`      | 901   | Union-aligned work that forces political choices          |
| `data/contracts/settlement_contracts.yaml`   | 2,401 | 4-6 per settlement: guard, escort, raid, hunt, patrol     |
| `data/contracts/supernatural_contracts.yaml` | 892   | Barrow clearing, draugr hunts, Veil-event response        |

### Culture (8 files, ~8,030 lines)

| File                                   | Lines | Contents                                          |
| -------------------------------------- | ----- | ------------------------------------------------- |
| `data/culture/colloquialisms.yaml`     | 370   | 68 everyday camp-talk phrases                     |
| `data/culture/expressions.yaml`        | 382   | 66 toasts, exclamations, idioms                   |
| `data/culture/insults_extended.yaml`   | 386   | 67 insults (cowardice, lineage, nid verses)       |
| `data/culture/legal_customs.yaml`      | 1,910 | Holmgang, weregild, Thing law, blood-feud, oaths  |
| `data/culture/material_culture.yaml`   | 1,652 | Clothing, tools, food, drink, architecture, ships |
| `data/culture/names_and_language.yaml` | 1,101 | 198 name entries, kennings, battle cries          |
| `data/culture/proverbs_extended.yaml`  | 314   | 68 proverbs (weather, survival, war, fate)        |
| `data/culture/rituals.yaml`            | 1,914 | Birth to death: blóts, funerals, seiðr, oaths     |

### Economy (4 files, ~4,735 lines)

| File                                     | Lines | Contents                                              |
| ---------------------------------------- | ----- | ----------------------------------------------------- |
| `data/economy/mercenary_costs.yaml`      | 690   | 88 entries: pay, gear, wounds, bribes, funerals       |
| `data/economy/settlement_economies.yaml` | 1,366 | 15 settlements with production, imports, exports      |
| `data/economy/trade_goods.yaml`          | 1,456 | 91 items with base prices, weight, seasonal modifiers |
| `data/economy/war_economy.yaml`          | 1,223 | 59 events: blockades, famine, war taxes, refugees     |

### Events (5 files, ~7,320 lines)

| File                                         | Lines | Contents                                           |
| -------------------------------------------- | ----- | -------------------------------------------------- |
| `data/events/personal_band_events.yaml`      | 1,431 | Kell's desertion, Petra's sister, Thorne's curse   |
| `data/events/supernatural_chain_events.yaml` | 1,294 | Waking Barrows escalation, Veil-thinning arc       |
| `data/events/y312_events.yaml`               | 1,227 | 86 events: border incidents → siege of Thornwall   |
| `data/events/y313_events.yaml`               | 1,547 | 100 events: Ordovast marches, war, dark arts       |
| `data/events/y314_y315_events.yaml`          | 1,822 | 120 events: reconstruction, barrow crisis, endgame |

### Geography (3 files, ~9,740 lines)

| File                                     | Lines | Contents                                            |
| ---------------------------------------- | ----- | --------------------------------------------------- |
| `data/geography/atlas.yaml`              | 5,606 | 149 named locations: passes, stones, ruins, springs |
| `data/geography/routes.yaml`             | 2,083 | 42 travel routes with distance, terrain, hazards    |
| `data/geography/terrain_encounters.yaml` | 2,055 | 120 terrain encounters by biome and season          |

### Hidden (1 YAML + 3 encoded text files)

| File                              | Lines | Contents                             |
| --------------------------------- | ----- | ------------------------------------ |
| `data/hidden/manifest.yaml`       | 141   | Secret content index and decode keys |
| `data/hidden/calendar_events.txt` | —     | CJK-encoded calendar secrets         |
| `data/hidden/campaign_arcs.txt`   | —     | CJK-encoded campaign secrets         |
| `data/hidden/npc_secrets.txt`     | —     | CJK-encoded NPC secrets and agendas  |

### NPCs (6 files, ~7,640 lines)

| File                               | Lines | Contents                                     |
| ---------------------------------- | ----- | -------------------------------------------- |
| `data/npcs/antagonist_npcs.yaml`   | 1,052 | Villains: cult leaders, slavers, renegades   |
| `data/npcs/relationship_web.yaml`  | 1,555 | NPC relationship graph (allies, rivals, kin) |
| `data/npcs/rival_band_npcs.yaml`   | 1,540 | Full statblocks for 4+ rival band rosters    |
| `data/npcs/settlement_npcs.yaml`   | 1,690 | Jarls, advisors, smiths, healers, merchants  |
| `data/npcs/supernatural_npcs.yaml` | 722   | Draugr-kings, Veil-touched, seiðr ghosts     |
| `data/npcs/traveling_npcs.yaml`    | 1,080 | Merchants, skalds, hermits, wandering seiðr  |

### Volumes (5 files, ~7,450 lines)

| File                                  | Lines | Contents                                        |
| ------------------------------------- | ----- | ----------------------------------------------- |
| `data/volumes/chapter_templates.yaml` | 1,343 | 17 reusable chapter types mapped to event types |
| `data/volumes/volume_arcs.yaml`       | 1,186 | 10-volume master structure with character arcs  |
| `data/volumes/volumes_1_3.yaml`       | 1,914 | 38 chapters covering Y312 (Spring–Winter)       |
| `data/volumes/volumes_4_7.yaml`       | 1,809 | 57 chapters covering Y313 (the war year)        |
| `data/volumes/volumes_8_10.yaml`      | 1,195 | 41 chapters covering Y314–Y315 (endgame)        |

### Weather (4 files, ~7,335 lines)

| File                                | Lines | Contents                                          |
| ----------------------------------- | ----- | ------------------------------------------------- |
| `data/weather/hazards.yaml`         | 1,251 | 75 terrain hazards by biome and season            |
| `data/weather/named_events.yaml`    | 1,610 | 38 named storms: Blood Snow, Ice Lock, Thaw Flood |
| `data/weather/seasonal_life.yaml`   | 2,229 | Flora, fauna, foraging calendars by season        |
| `data/weather/weather_history.yaml` | 2,245 | 192 weekly records spanning Y312–Y315             |

---

## Script Index

All scripts live in `scripts/`. Python 3.10+. Run with `--help` for
usage.

### Core Engine

| Script              | Lines | Purpose                                            |
| ------------------- | ----- | -------------------------------------------------- |
| `engine.py`         | 469   | Main simulation engine — action resolution, checks |
| `calendar_sim.py`   | 248   | Calendar advancement and time tracking             |
| `combat_model.py`   | 480   | Core combat model (attack, defend, damage)         |
| `combat_sim.py`     | 1,271 | Full combat simulator with multiple rounds         |
| `combat_ai.py`      | 308   | AI tactical decisions during combat                |
| `combat_grapple.py` | 774   | Grappling/clinch subsystem                         |
| `combat_types.py`   | 468   | Combat data types and enums                        |
| `wounds.py`         | 1,571 | Wound system (location, severity, healing)         |
| `trauma.py`         | 1,527 | Psychological trauma and stress damage             |

### World Management

| Script                | Lines | Purpose                                         |
| --------------------- | ----- | ----------------------------------------------- |
| `band_manager.py`     | 444   | Band roster, recruitment, replacement tracking  |
| `settlement.py`       | 523   | Settlement interactions, trade, market access   |
| `village_politics.py` | 1,123 | Political simulation (unions, feuds, economics) |
| `npc_manager.py`      | 558   | NPC database queries and lookup                 |
| `npc_generator.py`    | 433   | Procedural NPC generation                       |
| `event_manager.py`    | 522   | Event timeline queries, filtering, advancement  |

### Economy and Logistics

| Script                | Lines | Purpose                                        |
| --------------------- | ----- | ---------------------------------------------- |
| `ledger.py`           | 636   | Financial ledger, treasury, pay cycles         |
| `logistics.py`        | 295   | Supply burn, march speed, camp management      |
| `morale.py`           | 321   | Morale tracking, grievances, recovery          |
| `contracts.py`        | 418   | Contract data loading from multiple YAML pools |
| `contract_manager.py` | 555   | Contract lifecycle: accept, progress, complete |
| `recruitment.py`      | 324   | Mercenary recruitment and hiring               |

### Exploration and Environment

| Script                | Lines | Purpose                                        |
| --------------------- | ----- | ---------------------------------------------- |
| `travel.py`           | 716   | Travel planning, day-by-day route logs         |
| `weather.py`          | 681   | Weather generation, history lookup, reports    |
| `encounter.py`        | 520   | Random encounter generation by terrain/season  |
| `foraging.py`         | 236   | Foraging system (seasonal availability, yield) |
| `barrow_generator.py` | 596   | Procedural barrow/dungeon generation           |

### Data and Utilities

| Script               | Lines | Purpose                                      |
| -------------------- | ----- | -------------------------------------------- |
| `bestiary_loader.py` | 386   | YAML bestiary loading and validation         |
| `bestiary.py`        | 797   | Bestiary CLI: lookup, filter, encounter gen  |
| `hidden_info.py`     | 189   | Secret content management                    |
| `spoiler_codec.py`   | 209   | CJK spoiler encoding/decoding                |
| `validate_data.py`   | —     | YAML validation and cross-reference checking |

---

## Test Coverage

All tests live in `tests/`. Run with `python -m pytest tests/ -q`.

### Test Files (21)

| Test File                      | Covers                                 |
| ------------------------------ | -------------------------------------- |
| `test_bestiary_loader.py`      | YAML bestiary loading and schema       |
| `test_calendar.py`             | Calendar advancement, season detection |
| `test_combat_grapple.py`       | Grappling holds, escapes, damage       |
| `test_encounter.py`            | Random encounter generation            |
| `test_engine.py`               | Core resolution engine                 |
| `test_foraging.py`             | Foraging yields by season/terrain      |
| `test_ledger.py`               | Treasury math, pay cycles              |
| `test_logistics.py`            | Supply burn, march rate                |
| `test_morale.py`               | Morale checks, events                  |
| `test_npc_generator.py`        | Procedural NPC generation              |
| `test_recruitment.py`          | Recruitment mechanics                  |
| `test_resistances.py`          | Creature resistance mechanics          |
| `test_script_imports_smoke.py` | All script modules import cleanly      |
| `test_settlement.py`           | Settlement interactions, trade         |
| `test_spoiler_codec.py`        | CJK encode/decode round-trip           |
| `test_weaknesses.py`           | Creature weakness mechanics            |
| `test_weapon_reach.py`         | Weapon reach and distance rules        |
| `test_weapon_size.py`          | Weapon size and terrain modifiers      |
| `test_weapon_switch.py`        | Mid-combat weapon switching            |
| `test_weather.py`              | Weather lookups, season queries        |
| `conftest.py`                  | Shared fixtures and test configuration |

### Coverage Gaps

Scripts without dedicated test files:

- `combat_ai.py` — AI decision logic
- `combat_model.py` — core combat (partially covered by combat_grapple)
- `combat_sim.py` — full simulation (partially covered by combat tests)
- `combat_types.py` — data types (partially covered by combat tests)
- `trauma.py` — psychological damage
- `wounds.py` — wound system
- `band_manager.py` — roster management
- `contract_manager.py` — contract lifecycle
- `event_manager.py` — event queries
- `npc_manager.py` — NPC database
- `travel.py` — route planning
- `village_politics.py` — political simulation
- `barrow_generator.py` — barrow generation
- `bestiary.py` — bestiary CLI
- `validate_data.py` — data validation

---

## Data Architecture

```text
data/
├── band_state.yaml          ← Central band state (scripts read/write)
├── contracts_available.yaml ← Active contracts (contract_manager.py)
├── political_state.yaml     ← Union/feud state (village_politics.py)
├── settlements.yaml         ← Settlement DB (settlement.py, travel.py)
├── barrows/                 ← Barrow data (barrow_generator.py)
├── bestiary/                ← Enemies (bestiary.py, encounter.py)
├── contracts/               ← Contract pools (contracts.py)
├── culture/                 ← Writing reference (no script consumers)
├── economy/                 ← Trade/costs (ledger.py, settlement.py)
├── events/                  ← Timeline (event_manager.py)
├── geography/               ← Atlas/routes (travel.py, encounter.py)
├── hidden/                  ← Spoilers (spoiler_codec.py)
├── npcs/                    ← NPC DB (npc_manager.py)
├── volumes/                 ← Novel outlines (no script consumers)
└── weather/                 ← Climate data (weather.py, foraging.py)
```

### Data Flow

Events, contracts, and NPCs reference locations by settlement ID
(matching `settlements.yaml` and `data/geography/atlas.yaml`).
Bestiary entries feed into `encounter.py` and `barrow_generator.py`.
Weather history drives `foraging.py` yields and `travel.py` hazards.
Political state evolves via `village_politics.py` tick cycles.

---

## Cross-Reference Map

Which scripts read which data files, and which data files reference
each other.

### Script → Data Dependencies

| Script                | Reads                                                                               |
| --------------------- | ----------------------------------------------------------------------------------- |
| `engine.py`           | `band_state.yaml`                                                                   |
| `band_manager.py`     | `band_state.yaml`                                                                   |
| `settlement.py`       | `settlements.yaml`, `economy/settlement_economies.yaml`, `economy/trade_goods.yaml` |
| `village_politics.py` | `political_state.yaml`, `settlements.yaml`, `events/`                               |
| `combat_sim.py`       | `band_state.yaml`, `bestiary/`                                                      |
| `combat_grapple.py`   | `band_state.yaml`                                                                   |
| `trauma.py`           | `band_state.yaml`                                                                   |
| `wounds.py`           | `band_state.yaml`                                                                   |
| `contract_manager.py` | `contracts_available.yaml`, `contracts/`                                            |
| `contracts.py`        | `contracts/` (all 4 pools)                                                          |
| `ledger.py`           | `band_state.yaml`, `economy/mercenary_costs.yaml`                                   |
| `logistics.py`        | `band_state.yaml`                                                                   |
| `morale.py`           | `band_state.yaml`                                                                   |
| `recruitment.py`      | `band_state.yaml`                                                                   |
| `travel.py`           | `geography/routes.yaml`, `geography/atlas.yaml`, `weather/`                         |
| `weather.py`          | `weather/weather_history.yaml`, `weather/named_events.yaml`, `weather/hazards.yaml` |
| `encounter.py`        | `bestiary/encounters.yaml`, `geography/terrain_encounters.yaml`                     |
| `foraging.py`         | `weather/seasonal_life.yaml`                                                        |
| `event_manager.py`    | `events/` (all 5 files)                                                             |
| `npc_manager.py`      | `npcs/` (all 6 files)                                                               |
| `npc_generator.py`    | `culture/names_and_language.yaml`, `npcs/`                                          |
| `barrow_generator.py` | `barrows/` (all 4 files)                                                            |
| `bestiary_loader.py`  | `bestiary/` (all 7 files)                                                           |
| `bestiary.py`         | `bestiary/` via `bestiary_loader.py`                                                |
| `spoiler_codec.py`    | `hidden/` (text files)                                                              |
| `hidden_info.py`      | `hidden/manifest.yaml`                                                              |
| `calendar_sim.py`     | `events/`, `weather/weather_history.yaml`                                           |

### Data → Data Cross-References

| Source Data                         | References IDs In                                    |
| ----------------------------------- | ---------------------------------------------------- |
| `events/*.yaml`                     | `settlements.yaml`, `npcs/`, `bestiary/`, `barrows/` |
| `contracts/*.yaml`                  | `settlements.yaml`, `npcs/`, `bestiary/`, `barrows/` |
| `npcs/relationship_web.yaml`        | All other `npcs/` files                              |
| `npcs/settlement_npcs.yaml`         | `settlements.yaml`                                   |
| `npcs/rival_band_npcs.yaml`         | `band_state.yaml` (rival bands section)              |
| `geography/routes.yaml`             | `settlements.yaml`, `geography/atlas.yaml`           |
| `geography/terrain_encounters.yaml` | `bestiary/encounters.yaml`                           |
| `barrows/encounter_tables.yaml`     | `bestiary/undead.yaml`, `bestiary/supernatural.yaml` |
| `barrows/loot_tables.yaml`          | `economy/trade_goods.yaml` (value references)        |
| `economy/settlement_economies.yaml` | `settlements.yaml`                                   |
| `economy/war_economy.yaml`          | `events/`, `political_state.yaml`                    |
| `volumes/*.yaml`                    | `events/`, `npcs/`, `settlements.yaml`, `contracts/` |
| `weather/named_events.yaml`         | `geography/atlas.yaml` (affected areas)              |

---

## Volume and Novel Structure

10 volumes spanning 3 in-world years. 136 total chapter outlines.

| Volume | Year                    | Chapters | Central Conflict                     |
| ------ | ----------------------- | -------- | ------------------------------------ |
| 1      | Y312 Spring             | 12       | Band formation, first contracts      |
| 2      | Y312 Summer             | 13       | Allthing, diplomatic window          |
| 3      | Y312 Autumn–Winter      | 13       | Harvest politics, siege of Thornwall |
| 4      | Y313 Spring             | 14       | Ordovast marches, war begins         |
| 5      | Y313 Summer             | 15       | Regional war, major battles          |
| 6      | Y313 Autumn             | 14       | Widow's gambit, dark arts escalation |
| 7      | Y313 Winter             | 14       | Aftermath of first war, power vacuum |
| 8      | Y314 Spring–Summer      | 14       | Reconstruction vs. continued war     |
| 9      | Y314 Autumn–Y315 Spring | 14       | Barrow crisis escalation             |
| 10     | Y315                    | 13       | Endgame, band legacy                 |

Volume outlines are in `data/volumes/`. Chapter templates are in
`data/volumes/chapter_templates.yaml` (17 reusable types: battle,
march, negotiation, barrow delve, aftermath, etc.).

---

## Proposals and Roadmap

### Active Proposals

| File                                                  | Status            | Summary                                          |
| ----------------------------------------------------- | ----------------- | ------------------------------------------------ |
| `proposals/BESTIARY_SIM_IMPLEMENTATION_PLAN.md`       | Reference         | Bestiary simulation integration plan             |
| `proposals/PROPOSAL_001_MAGIC_OF_RIMEVEGR.md`         | Planned (P31–35)  | Magic system: Cracking, seiðr, galdr, folk magic |
| `proposals/PROPOSAL_002_GLIMA_AND_GRAPPLING.md`       | Implemented (P17) | Grappling subsystem — `combat_grapple.py`        |
| `proposals/PROPOSAL_003_WEAPON_REACH_AND_DISTANCE.md` | Implemented       | Weapon reach rules in combat                     |
| `proposals/PROPOSAL_004_WEAPON_SIZE_AND_TERRAIN.md`   | Implemented       | Weapon size and terrain modifiers                |

### Roadmap (from TODO.md)

| Prompt                       | Status      | Goal                                |
| ---------------------------- | ----------- | ----------------------------------- |
| 20: Master Event Timeline    | Complete    | 306 events across Y312–Y315         |
| 21: Enemy Bestiary           | Complete    | 114+ enemies in 7 categories        |
| 22: Barrow Map and Generator | Complete    | 20+ barrows, procedural dungeon gen |
| 23: Extended Contracts       | Complete    | 60+ contracts in 4 pools            |
| 24: NPC Database             | Complete    | 157 NPCs in 6 databases             |
| 25: Geography and Travel     | Complete    | 149 locations, 42 routes            |
| 26: Economy and Trade        | Complete    | 91 trade goods, war economy         |
| 27: Culture Database         | Complete    | 335+ cultural entries               |
| 28: Weather Expansion        | Complete    | 192 weeks, 38 named storms          |
| 29: Volume Outlines          | Complete    | 136 chapters across 10 volumes      |
| 30: Data Integrity Audit     | In progress | Validation, cross-ref, master index |
| 31–35: Magic of Rimevegr     | Planned     | Full magic system per Proposal 001  |

---

## Campaign Materials

Session play materials live in `campaign/`:

| Directory            | Contents                        |
| -------------------- | ------------------------------- |
| `campaign/data/`     | Session-specific data snapshots |
| `campaign/handouts/` | Player-facing handout documents |
| `campaign/maps/`     | Regional and local maps         |
| `campaign/npcs/`     | NPC sheets for active sessions  |
| `campaign/prep/`     | GM session preparation notes    |
| `campaign/sessions/` | Session logs and play records   |

---

## Skills (Writing Guidance)

| Skill                 | Path                                      | Purpose                                           |
| --------------------- | ----------------------------------------- | ------------------------------------------------- |
| Medieval authenticity | `skills/medieval-authenticity-reference/` | Historical accuracy for 10th-century Norse detail |
| Novel writing         | `skills/novel-writing/`                   | Cook-Abercrombie prose voice, 4-pass revision     |
| Writing team          | `skills/writing-team/`                    | Multi-agent collaborative fiction framework       |
