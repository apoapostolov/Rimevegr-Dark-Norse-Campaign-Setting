# AGENTS.md - Iron Ledger: Mercenaries of the Rimevegr

## Purpose

This is a living-world simulation project set in the Rimevegr — a dark,
low-fantasy Norse world of perpetual twilight, rime-fog, and brutal
mercenary survival. It has two modes:

- **Novel mode:** Use `00_NOVEL_WRITING_PROMPT.md` and the numbered documents
  (01-16) as a world database to write fiction. The data is mode-neutral —
  settlements, NPCs, contracts, events, and lore can feed any narrative.
- **Roleplaying mode:** Use `00_ROLEPLAYING_PROMPT.md` as an interactive
  text-adventure. All player-character rules, scoring, commands, and
  game-specific framing live exclusively in the RP prompt.

## Instruction Quality Standard

Treat this file as the mode router, not as the full encyclopedia.

- Put exact commands, script behavior, and regeneration steps in the narrower
  child AGENTS files.
- Keep world-state rules here only when they apply to both modes.
- If a section becomes a catalog or long reference table, move it to a sibling
  doc and leave only the routing rule in this file.
- Prefer acceptance rules over design notes.
- Keep the novel/RP split explicit so the agent does not mix player-facing and
  authoring instructions.

## How It Works

### For Novel Writing

1. Load `00_NOVEL_WRITING_PROMPT.md` as the authoring guide.
2. Use numbered documents (01-16) as the world database for setting, characters,
   events, and simulation data.
3. Spoiler-encoded content (CJK characters) can be decoded via
   `scripts/spoiler_codec.py` for plot planning.
4. Python scripts in `scripts/` resolve simulation details (combat, travel,
   weather, economy) to keep fiction grounded.

### For Roleplaying

1. Open `00_ROLEPLAYING_PROMPT.md` and paste it into an AI chat session.
2. Play by typing commands (n/s/e/w, look, examine, talk, inventory, etc.).
3. The AI narrates using data from the numbered documents.
4. Player-character specifics (Lump as POV, scoring, hidden-info secrecy)
   are defined only in the RP prompt.

### For the AI (Both Modes)

1. Load numbered documents as world context.
2. Use Python scripts in `scripts/` to resolve actions, simulate combat,
   track logistics, manage the ledger, and advance the calendar.
3. Spoiler content (traitor plans, secret events, NPC agendas) is stored as
   CJK-encoded text via `scripts/spoiler_codec.py`.
4. Update YAML data files in `data/` to persist world state between sessions.

## Document Map

| File                               | Purpose                                         |
| ---------------------------------- | ----------------------------------------------- |
| 00_ROLEPLAYING_PROMPT.md           | Player-facing game prompt (paste into AI chat)  |
| 00_NOVEL_WRITING_PROMPT.md         | Novel authoring mode prompt                     |
| 01_RIMEVEGR_SETTING_BIBLE.md       | World lore, society, Norse magic overview       |
| 03_GEOGRAPHY_AND_MAP.md            | Regions, landmarks, travel distances, map data  |
| 04_CULTURE_AND_CUSTOMS.md          | Daily life, customs, law, social structure      |
| 05_ECONOMY_OF_RIMEVEGR.md          | Currency, barter, costs, services, trade routes |
| 06_DICTIONARY_OF_NORSE_TERMS.md    | Norse vocabulary and terminology reference      |
| 06_RESEARCH_NOTES_OUTLAWRY.md      | Historical research on Viking Age outlawry      |
| 16_NAMED_MEN_AND_ARCHETYPES.md     | Band archetypes and character templates         |
| 11_VILLAGES_AND_SETTLEMENTS.md     | Settlement data and economy                     |
| 13_RIVAL_BANDS_AND_FACTIONS.md     | Opposition forces and political factions        |
| 20_SIMULATION_RULES.md             | Complete custom game system (Iron Ledger Rules) |
| 15_MERCENARY_LIFESTYLE.md          | Daily life, contracts, pay rituals              |
| 21_BAND_SIMULATION.md              | Band state tracking (YAML-formatted)            |
| 22_MEMBER_STATBLOCKS.md            | Full character sheets for all band members      |
| 09_WEATHER_SEASONS_AND_HAZARDS.md  | Weather, terrain, and environmental rules       |
| 10_CALENDAR_AND_HIDDEN_EVENTS.md   | Calendar system and hidden event engine         |
| 08_MAGIC_OF_RIMEVEGR.md            | Supernatural lore: galdr, seiðr, wyrd-reading   |
| 18_BARROWS_OF_RIMEVEGR.md          | Barrow atlas — burial sites and dungeon entries |
| 23_CAMPAIGN_ARCS_AND_PLOT_SEEDS.md | Long-term story arcs and plot hooks             |
| 24_VIGNETTES_AND_SCENES.md         | Voice-standard fiction vignettes (41 scenes)    |
| 19_GAME_CONTENT_BIBLE.md           | All game content tables and data structures     |
| 02_MASTER_INDEX.md                 | Master index of all data, files, and entities   |
| skills/novel-writing/SKILL.md      | Cook-Abercrombie voice specification            |
| skills/novel-writing/TODO.md       | Novel-writing mega-skill roadmap (Prompts 8-15) |

## Scripts Reference

All scripts live in `scripts/` and are Python 3.10+. Run any script with
`--help` for usage. Core scripts:

| Script          | Purpose                                | Example                                                  |
| --------------- | -------------------------------------- | -------------------------------------------------------- |
| engine.py       | Core resolution engine (action checks) | `python engine.py check --attr 6 --skill 3 --diff 0`     |
| hidden_info.py  | Encode/decode secrets in Chinese       | `python hidden_info.py encode "Kell plans to desert"`    |
| combat_sim.py   | Simulate combat between fighters       | `python combat_sim.py --attacker voss --defender bandit` |
| logistics.py    | Calculate supply burn, march speed     | `python logistics.py --band-size 14 --terrain forest`    |
| ledger.py       | Manage treasury, pay cycles            | `python ledger.py pay --week 12`                         |
| morale.py       | Track and resolve morale/grievances    | `python morale.py check --event "late_pay"`              |
| weather.py      | Generate weather for current day       | `python weather.py --season long_dark --day 87`          |
| foraging.py     | Simulate foraging results              | `python foraging.py --terrain fjord --foragers 4`        |
| calendar_sim.py | Advance time, check season             | `python calendar_sim.py advance --days 3`                |
| contracts.py    | Generate and manage contracts          | `python contracts.py generate --reputation 3`            |
| travel.py       | Simulate travel with hazards           | `python travel.py --from frostfjord --to ashen_reach`    |
| recruitment.py  | Recruit fighters at settlements        | `python recruitment.py --settlement frostfjord`          |
| settlement.py   | Settlement state management            | `python settlement.py show --name frostfjord`            |
| band_manager.py | Band state snapshots and updates       | `python band_manager.py status`                          |

## Spoiler Encoding System (CJK)

Spoiler content (plot twists, NPC secrets, future events) is stored as
CJK-encoded text in data files using `scripts/spoiler_codec.py`. This keeps
spoilers out of casual browsing for both novel planning and RP play.

```bash
# Encode a spoiler
python scripts/spoiler_codec.py encode "Kell plans to desert on day 95"

# Decode a spoiler
python scripts/spoiler_codec.py decode "<encoded text>"

# Encode/decode entire files
python scripts/spoiler_codec.py encode-file data/hidden/npc_secrets.txt
python scripts/spoiler_codec.py decode-file data/hidden/npc_secrets.txt
```

CJK characters in YAML/MD files are encoded spoiler content. Decode as
needed for plot planning or narrative development.

## Norse Magic System

Magic in the Rimevegr is rare, costly, and terrifying. Three traditions:

1. **Galdr (Rune Scribing)** — Carving and chanting runes for practical
   effects. Requires Rune-lore skill. Costs willpower and sometimes blood.
2. **Seiðr (Spirit Talking)** — Communion with the dead and land-spirits.
   Requires Spirit-lore skill. Socially dangerous (seen as unmanly for men).
3. **Wyrd-Reading (Fate Divination)** — Reading omens, casting lots, and
   sensing the threads of fate. Requires Wyrd-reading skill. Reveals
   hidden information but the knowledge always has a cost.

## Game System Summary

The Iron Ledger Rules (full details in 20_SIMULATION_RULES.md):

- **6 Attributes** (1-10): Might, Nimbleness, Toughness, Wits, Will, Wyrd
- **Skills** (0-5): Combat, survival, social, craft, and lore categories
- **Resolution**: Percentage-based, computer-simulated via scripts
- **Combat**: Initiative → attack/defend → hit location → wound severity
- **Health**: Hit points per location, wound tracking, bleeding, infection
- **Logistics**: Calorie-based food, weight-based carrying, distance-based travel

## Guardrails

- All documents must stay consistent with 01_RIMEVEGR_SETTING_BIBLE.md
- The world is authentic Norse + a thin layer of deniable supernatural dread (the Veil Ceiling)
- Only humans exist — no fantasy races
- Magic follows the three Norse traditions only (galdr, seiðr, wyrd-reading)
- Hidden information must be CJK-encoded before writing to data files
- Scripts must be run to resolve mechanical outcomes (no hand-waving)
- The world persists: changes to data files carry forward between sessions
- When asked to clean TODO.md, remove archived prompt blocks instead of preserving them unless the user explicitly asks to keep an archive
- Keep TODO.md lean: current focus, working rules, and the active prompt queue only

## Last reviewed

2026-06-01. Bump on any meaningful change to this file or its siblings.
