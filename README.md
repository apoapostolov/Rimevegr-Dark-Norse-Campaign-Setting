<p align="center">
  <img src="images/logo.png" alt="Rimevegr Logo" width="400"/>
</p>

# Rimevegr — Dark Norse Campaign Setting

> *A world drowning in perpetual twilight, rime-fog, and the long cold. The gods
> are silent but their absence is felt in every empty sky. Life is short,
> measured by the ledger, the axe, and the fire. Glory is a lie the dead tell
> themselves.*

**Rimevegr** (literally **"The Rime-Way"** or **"The Frost Road"**) is a dark,
low-fantasy Norse campaign setting for tabletop roleplaying and fiction. It is
the companion world bible for the **Iron Ledger** simulation project — a
complete living-world system of mercenary survival, economic pressure, grounded
combat, and deniable supernatural dread.

---

## Overview

| Aspect | |
|---|---|
| **Era** | ~850–1050 CE Norse world, collapsed into eternal twilight |
| **Magic** | Low, costly, terrifying — galdr runes, seiðr spirits, wyrd-reading |
| **Tone** | Authentic early-medieval grit, economic pressure, grounded dread |
| **Focus** | Mercenary survival — contracts, supply, weather, loyalty, debt |
| **Inspiration** | Viking Age Scandinavia, *The Northman*, *The Last Kingdom* (grit), *Valhalla* (tone) |

## What's Inside

| Module | Description |
|---|---|
| **📖 Setting Bible** | Complete world lore: geography, culture, economy, religion, calendar, weather, and magic system |
| **⚔️ Simulation Rules** | Iron Ledger custom game system — combat, travel, logistics, morale, recruitment, wounds, and band management |
| **🗺️ Living World Data** | Settlement economies, bestiary, contracts, weather engine, political state, and NPC tracking in structured YAML |
| **🐍 Python Engine** | Scripts for combat resolution, logistics, weather, morale, NPC generation, economy simulation, and campaign journaling |
| **📜 Campaign Content** | Five plot arcs spanning Y311–Y315, 41 narrative vignettes, barrow dungeons, rival factions, and named NPCs |
| **🎲 RP & Writing Modes** | Player-facing roleplaying prompt for interactive play, plus novel-writing mode for fiction authors |
| **🗺️ Hex Map Tool** | Interactive geographic explorer for the frozen villages, barrows, and routes of the Rimevegr |

## Quick Start

### For Game Masters

1. Read `01_RIMEVEGR_SETTING_BIBLE.md` for world context.
2. Load `00_ROLEPLAYING_PROMPT.md` as your player-facing game prompt.
3. Use `20_SIMULATION_RULES.md` for combat, travel, and economy resolution.
4. Run Python scripts in `scripts/` to simulate encounters, weather, and band logistics.

### For Writers

1. Read `01_RIMEVEGR_SETTING_BIBLE.md` for world context.
2. Load `00_NOVEL_WRITING_PROMPT.md` as your authoring guide.
3. Reference numbered documents (01–24) as your world database.
4. Use `24_VIGNETTES_AND_SCENES.md` for tone and narrative examples.

### For Developers

```bash
pip install -r scripts/requirements.txt
python scripts/engine.py --help
python scripts/combat_sim.py --help
python scripts/ledger.py --help
```

Run tests with:

```bash
pytest tests/
```

## Document Map

| File | Content |
|---|---|
| `01_RIMEVEGR_SETTING_BIBLE.md` | Core world lore, tone, and setting foundations |
| `03_GEOGRAPHY_AND_MAP.md` | Regions, landmarks, travel distances |
| `04_CULTURE_AND_CUSTOMS.md` | Daily life, laws, social structure |
| `05_ECONOMY_OF_RIMEVEGR.md` | Currency, trade routes, costs, services |
| `07_RELIGION_OF_RIMEVEGR.md` | Pantheon, cult practices, divine silence |
| `08_MAGIC_OF_RIMEVEGR.md` | Galdr, seiðr, wyrd-reading, magic system |
| `09_WEATHER_SEASONS_AND_HAZARDS.md` | Climate, environmental rules |
| `10_CALENDAR_AND_HIDDEN_EVENTS.md` | Timeline, seasonal events, hidden engine |
| `11_VILLAGES_AND_SETTLEMENTS.md` | Settlement data and economies |
| `13_RIVAL_BANDS_AND_FACTIONS.md` | Opposition forces, political factions |
| `18_BARROWS_OF_RIMEVEGR.md` | Burial sites, dungeon encounters |
| `20_SIMULATION_RULES.md` | Complete Iron Ledger game system |
| `23_CAMPAIGN_ARCS_AND_PLOT_SEEDS.md` | Y311–Y315 story arcs |
| `24_VIGNETTES_AND_SCENES.md` | 41 narrative vignettes for tone and inspiration |

## Screenshots & Media

![Campaign Cover Art](images/image01.png)

> *Cover: A mercenary walking the frozen road through the perpetual twilight of
> the Rimevegr.*

## License

This project is published as a public campaign setting. See individual source
files for author attribution. All original content is released under the terms
specified in the repository.

---

<p align="center">
  <sub>Built with the Iron Ledger simulation engine — mercenary survival in the
  long cold.</sub>
</p>
