# Event Schema — Iron Ledger Master Event Database

## Overview

The `data/events/` directory contains the complete encoded event
database for the Rimevegr, covering Y312-Y315 (12 seasons, 3 in-world
years). Events drive the franchise-level plot, supernatural escalation,
political shifts, and personal arcs.

## YAML Event Format

```yaml
events:
  - id: "EVT_312_S01_001" # Required. Unique event ID.
    title: "Border Scouts" # Required. Short human-readable name.
    year: 312 # Required. In-world year.
    season: "spring" # Required. spring|summer|autumn|winter
    day: 15 # Required. Day of year (1-360).
    category: "political" # Required. See Event Categories.
    chain: "iron_grip" # Optional. Chain ID for linked events.
    chain_order: 1 # Optional. Position in chain.
    location: "Grimholt" # Optional. Settlement or region name.
    actors: # Optional. Named participants.
      - "Ordovast"
      - "Thane Egil Raven-Eye"
    factions: # Optional. Faction/union involvement.
      - "The Iron Grip"
    band_relevant: false # Required. Does this affect the band?
    prerequisites: # Optional. Events that must happen first.
      - "EVT_312_S01_003"
    branches: # Optional. Conditional outcomes.
      - condition: "band_cleared_barrow"
        outcome: "curse_lifted"
        triggers: ["EVT_312_A01_005"]
      - condition: "default"
        outcome: "curse_persists"
        triggers: ["EVT_312_A01_006"]
    effects: # Optional. Mechanical consequences.
      feud_change:
        pair: ["Grimholt", "Thornwall"]
        delta: 1
        cause: "border scouts spotted"
      cohesion_change:
        union: "The Iron Grip"
        delta: -1
      morale_change: -1
      reputation_change: 0
      war_readiness_change:
        union: "The Iron Grip"
        delta: 1
    spoiler: "SPOILER:丯丶丨..." # Optional. CJK-encoded hidden detail.
    summary: "Ordovast sends scouts to Thornwall border."
    detail: | # Optional. Extended narrative description.
      Ordovast dispatches three riders along the
      Thornwall sheep-routes, testing Jarl Helga's
      response time. The scouts carry no weapons —
      plausible deniability — but everyone knows.
```

## Event ID Convention

Format: `EVT_{year}_{season_code}{chain_num}_{sequence}`

- **year:** 312, 313, 314, 315
- **season_code:** S = spring, U = summer, A = autumn, W = winter,
  X = cross-season (supernatural, personal)
- **chain_num:** 2-digit chain number within the season (01-99)
- **sequence:** 3-digit sequence within chain (001-999)

Examples:

- `EVT_312_S01_001` — Y312 Spring, chain 01, event 001
- `EVT_313_A03_012` — Y313 Autumn, chain 03, event 012
- `EVT_312_X01_001` — Y312 cross-season supernatural chain, event 001

Legacy events (EVT_001 through EVT_012 in `data/hidden/`) retain
their old IDs for backward compatibility. New events use the full
format.

## Event Categories

| Category       | Description                                            |
| -------------- | ------------------------------------------------------ |
| `political`    | Union politics, ting decisions, alliances, feud shifts |
| `military`     | Raids, battles, troop movements, sieges, skirmishes    |
| `economic`     | Trade routes, harvests, price shifts, shortages        |
| `supernatural` | Veil events, barrow activity, galdr/seiðr incidents    |
| `personal`     | Band member arcs, NPC revelations, loyalty shifts      |
| `weather`      | Extreme weather events with mechanical effects         |
| `social`       | Seasonal rites, assemblies, marriages, funerals        |

## Event Chains

Events can be linked into chains via the `chain` and `chain_order`
fields. Chains represent multi-event arcs that unfold across seasons.

### Canonical Chain IDs

| Chain ID          | Description                      | Span      |
| ----------------- | -------------------------------- | --------- |
| `iron_grip`       | Ordovast's expansionist arc      | Y312-Y314 |
| `widows_web`      | Pale Widow's covert manipulation | Y312-Y314 |
| `waking_barrows`  | Supernatural escalation          | Y312-Y315 |
| `fjord_compact`   | Sigrun's economic alliance       | Y312-Y313 |
| `kell_debt`       | Kell's blood-debt and desertion  | Y312-Y313 |
| `petra_sister`    | Petra's missing sister arc       | Y312-Y313 |
| `thorne_curse`    | Thorne's rune-curse and secret   | Y312-Y315 |
| `ash_past`        | Ash's galdr lineage and origin   | Y313-Y314 |
| `dalla_awakening` | Dalla's seiðr emergence          | Y312-Y314 |
| `voss_command`    | Voss's leadership crisis         | Y313-Y314 |
| `grave_wardens`   | Barrow-specialist faction arc    | Y312-Y315 |
| `red_tide`        | Red Tide raiding escalation      | Y312-Y314 |
| `three_wolves`    | Three Wolves territorial war     | Y312-Y313 |
| `allthing`        | Annual assembly politics         | Y312-Y315 |
| `long_dark`       | Seasonal survival pressure       | Y312-Y315 |

## Season-to-Day Mapping

| Season                    | Days    | Months                                                |
| ------------------------- | ------- | ----------------------------------------------------- |
| Spring (Long Summer)      | 1-60    | Frostwake, Rimeblood                                  |
| Summer (Early Dark)       | 61-120  | Veilthin, Ashfall                                     |
| Autumn (Deep Dark begins) | 121-210 | Ironmoon, Wolfmoot, Barrowrise                        |
| Winter (Deep/Late Dark)   | 211-360 | Longnight, Hearthstar, Bloodtide, Skaldsong, Yuledeep |

## File Organization

| File                        | Contents                                        |
| --------------------------- | ----------------------------------------------- |
| `y312_events.yaml`          | All Y312 events (4 seasons, ~80 events)         |
| `y313_events.yaml`          | All Y313 events (4 seasons, ~100 events)        |
| `y314_y315_events.yaml`     | Y314-Y315 events (8 seasons, ~120 events)       |
| `supernatural_chain.yaml`   | Cross-year supernatural escalation (~50 events) |
| `band_personal_events.yaml` | Band member personal arcs (~60 events)          |
| `EVENT_SCHEMA.md`           | This document                                   |

## Integration Points

### village_politics.py

The `event_manager.py` script queries events by day and feeds them
to the `tick_week()` / `tick_season()` cycle in `village_politics.py`.

Events with `effects` fields automatically:

- Modify feuds (`feud_change`)
- Modify union cohesion (`cohesion_change`)
- Modify war readiness (`war_readiness_change`)
- Modify band morale/reputation (`morale_change`, `reputation_change`)

### Spoiler Encoding

Events containing hidden detail use the `spoiler` field with CJK
encoding via `spoiler_codec.py`. The `event_manager.py decode` command
reveals hidden content.

### Branching

Events with `branches` field create conditional paths. The
`event_manager.py advance` command takes a condition argument to
select which branch fires and which follow-up events are activated.
