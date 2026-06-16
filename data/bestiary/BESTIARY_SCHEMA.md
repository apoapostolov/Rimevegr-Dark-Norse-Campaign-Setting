# Bestiary Schema

Enemy and creature database format for the Iron Ledger setting.

## YAML Structure

```yaml
enemies:
  - id: "HUM_BANDIT_01"
    name: "Roadside Bandit"
    category: "human"
    subcategory: "bandit"
    tier: 2
    description: "Short physical description."
    stats:
      MIG: 4
      NIM: 5
      TOU: 4
      WIT: 3
      WIL: 3
      WYR: 1
    hp: 8
    skills:
      - name: "Axes"
        rank: 2
      - name: "Brawl"
        rank: 1
    gear:
      weapons:
        - name: "Hand Axe"
          type: "axe"
          speed: 3
          base_damage: 4
      armor:
        torso: "Leather Jerkin"
        head: "None"
    tactics: |
      Hits from ambush. Runs if outnumbered or wounded.
    morale_break: "Flees below 50% HP or if leader falls."
    encounter_conditions:
      terrain: ["road", "forest_edge", "moor"]
      season: ["spring", "summer", "autumn"]
      day_range: [1, 210]
    loot:
      silver_range: [2, 15]
      items: ["hand_axe", "leather_scraps"]
      special: null
    image_prompt: |
      A gaunt man in patched leather, scarred hands gripping a
      notched hand axe. Greasy hair, broken teeth, wary eyes.
      Muted palette: browns, greys, rust. Dark Norse aesthetic.
```

## Required Fields

| Field        | Type    | Description                                   |
| ------------ | ------- | --------------------------------------------- |
| id           | string  | Unique ID: `{CAT}_{SUB}_{NUM}`                |
| name         | string  | Display name                                  |
| category     | string  | One of the categories below                   |
| tier         | int 1-5 | Danger level (1 trivial, 5 legendary)         |
| description  | string  | Physical description, 1-3 sentences           |
| stats        | dict    | MIG, NIM, TOU, WIT, WIL, WYR (1-10)           |
| hp           | int     | Hit points (derived from TOU or set directly) |
| tactics      | string  | Combat behavior and preferred approach        |
| morale_break | string  | When this enemy flees or surrenders           |

## Optional Fields

| Field                | Type   | Description                                                                                              |
| -------------------- | ------ | -------------------------------------------------------------------------------------------------------- |
| subcategory          | string | Finer grouping within category                                                                           |
| skills               | list   | Skill name + rank pairs                                                                                  |
| gear                 | dict   | weapons, armor sub-dicts                                                                                 |
| encounter_conditions | dict   | terrain, season, day_range                                                                               |
| loot                 | dict   | silver_range, items, special                                                                             |
| image_prompt         | string | Physical description for art generation                                                                  |
| abilities            | list   | Special abilities beyond normal combat                                                                   |
| combat_phases        | dict   | Phase-triggered combat abilities (see below)                                                             |
| resistances          | list   | Damage types or conditions resisted                                                                      |
| weaknesses           | list   | Exploitable vulnerabilities                                                                              |
| is_undead            | bool   | True for undead — enables bleeding immunity, no daze/stagger, no wound penalty, no survival-based stance |
| sim_traits           | list   | Machine-readable trait tags consumed by `combat_sim.py` — see Sim Traits table below                     |
| achilles_heel        | dict   | Mandatory for world_boss (see below)                                                                     |
| group_size           | string | Typical encounter size: "1", "2-4", "5-10"                                                               |
| named                | bool   | True for unique/boss enemies                                                                             |
| lore                 | string | Historical or cultural background                                                                        |
| associated_locations | list   | Settlement or barrow IDs                                                                                 |
| associated_chains    | list   | Event chain IDs this enemy appears in                                                                    |

## Categories

| Code | Category              | ID Prefix |
| ---- | --------------------- | --------- |
| HUM  | Human                 | HUM\_     |
| UND  | Undead and Barrow     | UND\_     |
| SUP  | Supernatural and Veil | SUP\_     |
| ANI  | Animal and Natural    | ANI\_     |
| BOS  | Named Enemy / Boss    | BOS\_     |
| WBS  | World Boss            | WBS\_     |

## Sim Traits

Machine-readable tags for `sim_traits:` consumed by `combat_sim.py` `Fighter.from_dict()`.
Pass these under the `traits` key when constructing a fighter JSON.

### Core traits (implemented in Batch 1–2)

| Tag                   | Effect in combat_sim.py                                                 |
| --------------------- | ----------------------------------------------------------------------- |
| `unfeeling`           | Wound penalty always 0 — injuries don't impair attack/defense rolls     |
| `terrifying_presence` | Pre-battle WIL check for opponent; failure → STAGGERED 2 rounds         |
| `combat_memory`       | Undead can counter-attack (Nachreisen) despite `is_undead` flag         |
| `ancient_resilience`  | Incoming damage halved (rounded down, min 1) — non-magical weapons only |
| `no_counter`          | Explicitly disables counter-attacks even for non-undead fighters        |

### Animal traits

| Tag                 | Intended effect                                                                  |
| ------------------- | -------------------------------------------------------------------------------- |
| `pack_tactics`      | +1 attack roll when at least one ally is adjacent to the same target             |
| `hamstring`         | On hit, target NIM reduced by 1 until end of encounter (stacks once)             |
| `scavenger`         | Morale break threshold increased — scavengers flee later than average beasts     |
| `starvation_frenzy` | Attacks twice per round when initiating; loses shield-parry access               |
| `terrifying_charge` | First attack of combat: +2 damage; target must pass WIL or lose initiative       |
| `maul_bite`         | After successful grapple, free bite attack at base_damage 3, ignores AR          |
| `thick_hide_2`      | Torso and limb AR both +2 (natural armor on top of gear)                         |
| `thick_hide_3`      | Torso and limb AR both +3 (natural armor on top of gear)                         |
| `den_fighter`       | +2 MIG and +1 TOU when fighting inside a den/enclosed terrain                    |
| `crushing_weight`   | Grapple damage doubled; escape MIG contest at -2 for smaller opponents           |
| `territorial_rage`  | If attacked in home terrain, gains +1 attack roll each successive round (max +3) |

### Undead traits

| Tag                         | Intended effect                                                            |
| --------------------------- | -------------------------------------------------------------------------- |
| `deathgrip_1`               | Grapple attempt on every hit; MIG 3 vs target to maintain hold             |
| `deathgrip_2`               | Grapple attempt on every hit; MIG 5 vs target; break costs full action     |
| `death_rattle`              | On reaching 0 HP, makes one final free attack before collapsing            |
| `dark_hardened`             | AR 1 on all locations vs non-fire, non-silver weapons                      |
| `relentless_advance`        | Immune to KNOCKBACK and STAGGER effects                                    |
| `last_stand`                | Below 25% HP: wound penalties reversed to attack bonuses (+1 per wound)    |
| `weapon_throw_on_death`     | On reaching 0 HP, throws held weapon at nearest enemy (base damage, no AR) |
| `slow_init`                 | Initiative roll at -3; always acts last in first round                     |
| `foul_stench`               | All adjacent opponents must pass TOU each round or suffer -1 to attacks    |
| `corpse_burst_4_2`          | On death: 4-pace radius burst, 2 damage per target, TOU halves             |
| `nauseating_burst`          | Same trigger as `corpse_burst_*`; failed TOU → STAGGERED 1 round           |
| `ancient_fury`              | +2 MIG and +2 WIL for the entire encounter (no scaling)                    |
| `command_dead`              | Activates any other undead in the scene on turn 1 (no action cost)         |
| `raise_fallen_once`         | Once per encounter, restores one ally from 0 HP to 1 HP                    |
| `phase_through_stone`       | Can attack through walls; ignores cover and shield vs barrow terrain       |
| `armor_bypass_supernatural` | Attacks ignore mundane AR; only magical protection or silver applies       |
| `territorial_fury_barrow`   | +2 MIG and +2 NIM when fighting inside its bound barrow                    |
| `choking_darkness`          | Pre-battle: all torches extinguished, vision capped at 1 pace              |
| `dormant_trigger`           | Does not act until linked artifact or territory is disturbed               |

### Supernatural traits

| Tag                      | Intended effect                                                             |
| ------------------------ | --------------------------------------------------------------------------- |
| `incorporeal`            | Not targeted by physical attacks; only fire, silver, rune-weapons, or seidr |
| `nightmare_drain`        | Each hit reduces target WIL by 1 (recovers at dawn)                         |
| `sleep_paralysis`        | Pre-battle: target with lowest WIL must pass WIL or start STUNNED 1 round   |
| `domain_bonus_3`         | +3 to all rolls when fighting inside its bound domain                       |
| `bound_territory`        | Cannot pursue beyond domain edge; morale-breaks if dragged past threshold   |
| `shapeshifter`           | Once per combat, changes form — resets surprise and forces new WIT check    |
| `lure_song`              | Pre-battle WIL test; failure → moves toward creature rather than acting     |
| `water_strength`         | +3 MIG and +2 TOU while in or adjacent to deep water                        |
| `cold_burst_aoe`         | Triggered attack (on provocation): 3-pace cold burst, d6 damage, TOU halves |
| `warmth_drain`           | Each hit reduces target TOU by 1 for the encounter (cold sickness)          |
| `courage_sap`            | Target loses morale bonus; WIL test each round to maintain fighting resolve |
| `dread_aura`             | Persistent: all within 5 paces take -1 WIL per round spent adjacent         |
| `wrong_geometry`         | Reach 2 paces longer than visible; NIM test to avoid surprise strikes       |
| `reality_stutter`        | -2 to ranged attacks targeting it; moves in lurching, unpredictable steps   |
| `seidr_hunger`           | Attacks seidr users preferentially; gains +1 MIG after absorbing seidr cast |
| `stone_skin`             | Immune to cutting damage from mundane weapons; AR 8 on all locations        |
| `sunlight_petrification` | d6 damage per round in direct sunlight; fully petrified after 3 rounds      |
| `crushing_grip_3`        | Grapple deals d8 per round; escape MIG contest at -3                        |
| `regeneration_1`         | Regains 1 HP per round while in darkness or deep shade                      |
| `killing_cold_contact`   | Melee hit: d6 cold damage + d4 ongoing frostbite per round until warmed     |
| `cold_aura`              | All within 5 paces suffer -1 NIM and -1 MIG from numbing cold               |
| `fire_aversion`          | Cannot move within 3 paces of large fire; takes d4 per round from flames    |

### Boss / named-enemy traits

| Tag                        | Intended effect                                                         |
| -------------------------- | ----------------------------------------------------------------------- |
| `blackwine_rage`           | On first wound: +2 MIG for 3 rounds; triggers once per encounter        |
| `read_the_field_once`      | Once per encounter: force one enemy to reroll a successful attack       |
| `bone_gnaw`                | After grapple: free bite attack, d4 damage, ignores AR                  |
| `relentless_no_crit`       | Ignores the first critical wound effect received in the encounter       |
| `fog_fighter`              | No penalty to attack or defense in low-visibility conditions            |
| `patient_strike`           | If attack is deliberately delayed one round: +2 base damage on next hit |
| `tactical_withdrawal_once` | Once per combat: disengage without triggering free attacks              |
| `desperate_fury`           | Below 50% HP: +2 to all combat rolls                                    |
| `veteran_eye`              | Identifies lowest-TOU opponent automatically; +1 attack vs that target  |
| `last_stand_25`            | Below 25% HP: +3 damage on all attacks                                  |
| `shield_wall_master`       | +2 AR (all locations) when fighting alongside at least 2 allies         |
| `barrow_wise`              | +2 to all rolls involving undead detection, countering, and weaknesses  |
| `fire_bearer_torchbonus`   | Torch/fire attacks deal +2 damage vs undead targets                     |

## Tier Scale

| Tier | Label        | Description                      |
| ---- | ------------ | -------------------------------- |
| 1    | Trivial      | Single warrior handles easily    |
| 2    | Common       | Fair fight for one fighter       |
| 3    | Dangerous    | Needs a competent group          |
| 4    | Deadly       | Full band, prepared, with losses |
| 5    | Legendary    | Campaign-defining threat         |
| 6    | World-Ending | Army-level; exploitable weakness |

## Stat Ranges by Tier

| Tier | Stat Range | HP Range | Skill Max |
| ---- | ---------- | -------- | --------- |
| 1    | 2-4        | 4-6      | 1         |
| 2    | 3-5        | 6-10     | 2         |
| 3    | 4-7        | 8-14     | 3         |
| 4    | 5-8        | 12-20    | 4         |
| 5    | 6-10       | 16-30    | 5         |
| 6    | 8-10       | 40-100+  | 5+        |

## File Organization

```text
data/bestiary/
  BESTIARY_SCHEMA.md    # This file
  humans.yaml           # HUM_ entries
  undead.yaml           # UND_ entries
  supernatural.yaml     # SUP_ entries
  animals.yaml          # ANI_ entries
  named_enemies.yaml    # BOS_ entries
  world_bosses.yaml     # WBS_ entries (Tier 6 world-ending threats)
  image_prompts.md      # Compiled image prompts for all entries
```

## Combat Phases

Supernatural and undead creatures may have a `combat_phases` field with
phase-triggered abilities. Only include phases that make sense for the creature.
Non-combatant entities (hazards, phenomena) skip this field entirely.

```yaml
    combat_phases:
      pre_battle:
        - name: "Ability Name"
          description: "Effect that occurs before combat starts (auras, warnings, environmental shifts)"
      maneuvers:
        - name: "Ability Name"
          description: "Special combat actions available during the fight"
          cost: "Replaces attack" | "Free action" | "Once per encounter" | "Once per 3 rounds"
      bloodied:
        - name: "Ability Name"
          trigger: "Below 50% HP"
          description: "Effect triggered when the creature drops below half HP"
      on_death:
        - name: "Ability Name"
          description: "Effect that occurs when the creature reaches 0 HP"
```

### Phase Descriptions

| Phase      | Trigger       | Design Intent                                      |
| ---------- | ------------- | -------------------------------------------------- |
| pre_battle | Before combat | Atmospheric dread, environmental setup, surprise   |
| maneuvers  | During combat | Special actions replacing or supplementing attacks |
| bloodied   | Below 50% HP  | Escalation, desperation mechanics, danger spikes   |
| on_death   | 0 HP          | Death throes, curses, environmental consequences   |

### Guidelines

- Low-HP creatures (4-5 HP) may skip `bloodied` — their threshold is barely meaningful.
- Existing flat `abilities` that describe phase behavior (e.g., "Corpse Burst: on death...") remain in the `abilities` list for backward compatibility; `combat_phases` provides structured, machine-readable equivalents.
- Ability descriptions must include mechanical details: save types, damage dice, distances in paces, durations in rounds.
- Not every creature needs all four phases. Use only what fits the creature's nature.

## Achilles Heel (World Bosses)

All `world_boss` entries require an `achilles_heel` dict. World bosses are
Dark Souls-grade threats — army-level catastrophes that cannot be overcome
through conventional combat. Each has exactly one exploitable fundamental
weakness that makes defeating them possible through cunning, research,
sacrifice, or manipulation rather than raw force.

```yaml
achilles_heel:
  name: "Short name for the weakness"
  discovery: "How PCs can learn this weakness exists — NPCs, texts, signs"
  location: "Where the weakness can be exploited — physical place or condition"
  exploit: "Exact mechanical steps to use the weakness against the boss"
  difficulty: "What makes exploiting the weakness hard — the quest within the quest"
```

### Design Principles

- **Not a fight — a problem.** World bosses are solved, not defeated in combat.
- **One narrow path.** Each boss has exactly one Achilles heel. No alternatives.
- **Discovery is gameplay.** Finding the weakness is a multi-session quest.
- **The exploit is dangerous.** Using the weakness still risks lives.
- **Consequences are permanent.** World bosses reshape the setting when they
  appear and when they are defeated.
- **HP 0 special cases.** Some world bosses have 0 HP (The Red Jarl, The First
  Barrow) because conventional damage is irrelevant to them. The validator
  exempts `cursed_warlord` and `primordial` subcategories from the HP check.

## Integration Points

- `scripts/bestiary.py` — CLI to query, filter, random encounter
- `scripts/combat_sim.py` — stat format compatible
- `data/events/` — enemies referenced by ID in event actors
- `data/barrows/` (future) — encounter tables reference bestiary IDs
- `data/contracts/` — target enemies in contract objectives
