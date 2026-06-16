# Magic Schema — Iron Ledger Magic Data System

## Overview

The `data/magic/` directory contains canonical data for the Rimevegr's
magical infrastructure: practitioners, services, and items. All data
cross-references `08_MAGIC_OF_RIMEVEGR.md` (Sections 7-8),
`20_SIMULATION_RULES.md` (§11 magic mechanics), and
`22_MEMBER_STATBLOCKS.md` (band practitioner statblocks).

## Files

| File                  | Contents                                    |
| --------------------- | ------------------------------------------- |
| `practitioners.yaml`  | Registry of all known magical practitioners |
| `magic_services.yaml` | Canonical pricing for magical services      |
| `magic_items.yaml`    | Enchanted, cursed, and rune-marked items    |
| `MAGIC_SCHEMA.md`     | This document — format reference            |

## YAML Format: Practitioners

```yaml
practitioners:
  - id: "PRAC_001" # Unique practitioner ID
    name: "Ash" # Full/common name
    call_name: "Ash" # Nickname or call-name
    tradition: "galdr" # galdr | seidr | wyrd_reading
    rank: 3 # Highest magic skill rank (null if none)
    wyrd: 3 # WYR attribute value
    primary_skill: "Rune-lore" # Primary magical skill name
    primary_skill_rank: 3 # Primary skill rank
    secondary_skills: # Additional relevant skills
      - name: "Sagas"
        rank: 2
    lifecycle_stage:
      "active" # latent | apprentice | active |
      # declining | retired | dead
    age: "early 30s" # Approximate age
    affiliation: "Black Axes" # Band, settlement, or independent
    location_current: "mobile" # Current location
    training_location: "..." # Where trained
    training_master: "..." # Who trained them
    manifestation_age: ~ # Age when talent first showed
    years_active: ~10 # Years of active practice
    physical_toll: # Visible damage from practice
      hands: "..."
      aging: "..."
      other: "..."
    decline_indicators: [] # Observable signs of declining ability
    projected_peak_age: 35 # Estimated peak capability age
    projected_decline_onset: 40 # When decline becomes measurable
    death_risk_factors: [] # Likely causes of death
    encoded_truth_ref: "..." # Link to encoded spoiler (if any)
    statblock_ref: "..." # Document containing full statblock
    notes: "..." # Narrative context
```

### Practitioner ID Ranges

| Range       | Category               |
| ----------- | ---------------------- |
| PRAC_001-09 | Black Axes band        |
| PRAC_010-29 | Settlement-based       |
| PRAC_030-49 | Rival band / itinerant |
| PRAC_050-69 | Historical / deceased  |
| PRAC_070+   | Expansion              |

### Lifecycle Stages

| Stage      | Description                                          |
| ---------- | ---------------------------------------------------- |
| latent     | Talent present but unrecognized or untrained         |
| apprentice | In training under a master                           |
| active     | Practicing at or near peak capability                |
| declining  | Measurable capability loss (skill, physical, mental) |
| retired    | Stopped active practice (voluntary or forced)        |
| dead       | Deceased — death circumstances documented            |

## YAML Format: Magic Services

```yaml
magic_services:
  galdr:
    - id: "MSVC_GAL_001"
      name: "Trail-Mark"
      galdr_rank_required: 1 # Minimum skill rank to perform
      base_price_copper: 5 # Standard market rate
      duration: "1 day" # How long the effect lasts
      material_cost_copper: 0 # Component costs on top of service
      description: "..." # What the service does
      availability: "common" # common | uncommon | rare | exotic
      providers: ["..."] # Who can perform this
      notes: "..." # Additional context
```

### Service ID Prefixes

| Prefix    | Tradition    |
| --------- | ------------ |
| MSVC*GAL* | Galdr        |
| MSVC*SDR* | Seiðr        |
| MSVC*WYR* | Wyrd-reading |

### Price Modifiers

All base prices are modified by context:

| Modifier       | Multiplier | Trigger                           |
| -------------- | ---------- | --------------------------------- |
| Urgency        | ×2.0       | Service needed within hours       |
| Wartime        | ×1.5       | Active conflict in region         |
| Long Dark      | ×1.3       | Winter season                     |
| Reputation     | ×1.5       | High-status practitioner          |
| Danger premium | ×2.0       | Barrow, hostile site, active zone |
| Political risk | ×1.5       | Social/legal risk to practitioner |
| Blood price    | varies     | Literal blood instead of copper   |

## YAML Format: Magic Items

```yaml
magic_items:
  - id: "MITM_001"
    name: "Frostfjord Hollow Ward-Stones"
    type:
      "ward_stone" # ward_stone | rune_weapon |
      # binding_amulet | cursed_weapon |
      # curse_installation | installation |
      # divination_tool
    subtype: "settlement_boundary" # Specific variant
    origin: "ancient" # ancient | crafted | barrow_loot | cursed
    age: "pre-Cracking" # Approximate age or creation date
    location: "..." # Current physical location
    status:
      "active" # active | dormant | destroyed |
      # lost | unknown
    galdr_rank_at_creation: 5 # Rank needed to make this
    current_effective_rank: 4 # Current functional power level
    description: "..." # Physical and magical description
    mechanical_effect: "..." # Game mechanic impact (per §11)
    degradation_rate: "..." # How fast it weakens
    estimated_remaining_years: 100 # Before failure (if degrading)
    value_copper: 0 # Market value (0 = priceless)
    curse_effect: "..." # If cursed — what happens
    encoded_truth_ref: "..." # Link to encoded spoiler (if any)
    notes: "..." # Narrative context
```

### Item ID Ranges

| Range       | Category                 |
| ----------- | ------------------------ |
| MITM_001-09 | Ward-stones              |
| MITM_010-19 | Rune-marked weapons      |
| MITM_020-29 | Protective items         |
| MITM_030-39 | Cursed items             |
| MITM_040-49 | Barrow artifacts         |
| MITM_050-59 | Seiðr/divination objects |
| MITM_060+   | Expansion                |

## Cross-References

| Topic                    | Document                                 |
| ------------------------ | ---------------------------------------- |
| Magic mechanics          | `20_SIMULATION_RULES.md` §11             |
| Political magic rules    | `20_SIMULATION_RULES.md` §11.8           |
| Band practitioner stats  | `22_MEMBER_STATBLOCKS.md`                |
| Material economy         | `08_MAGIC_OF_RIMEVEGR.md` §7             |
| Practitioner lifecycle   | `08_MAGIC_OF_RIMEVEGR.md` §8             |
| Encoded mysteries        | `08_MAGIC_OF_RIMEVEGR.md` §6             |
| Trade goods (components) | `data/economy/trade_goods.yaml`          |
| Settlement economies     | `data/economy/settlement_economies.yaml` |
| Encoded truths           | `data/hidden/magic_truth.txt`            |
| Mystery manifest         | `data/hidden/mystery_manifest.yaml`      |

## Currency Reference

- 1 silver = 10 copper
- Common merc retainer: 2 silver/week (20 copper)
- Food baseline: 1 silver/week/person (10 copper)
- Iron hand-axe: 40 copper
- Annual building ward: 250 copper
- Barrow sealing: 500 copper
