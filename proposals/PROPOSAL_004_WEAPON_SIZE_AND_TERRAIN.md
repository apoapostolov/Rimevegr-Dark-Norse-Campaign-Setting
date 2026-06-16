# PROPOSAL 004 — Weapon Size and Terrain Constraints

## Status

Proposed — 2026-04-13

## Motivation

PROPOSAL*003 introduced reach as a distance-band mechanic. It left unanswered
the equally important question of \_swing arc*: a great sword or spear that
cannot be brought fully around becomes a liability rather than a threat. The
problem is terrain-specific. A spear-bearer who steps into a burial mound
corridor cannot level the shaft; a longhouse brawl gives the dagger wielder
every advantage.

Historical record is unambiguous:

- Norse sagas note house fights resolved quickly and lethally by the knife.
- HEMA practitioners confirm indoor longsword fighting defaults to half-sword
  grips or dagger draws.
- Shieldwall sources (Saxo, the Welsh Annals) describe polearm use in formed
  units — unusable in broken terrain without the surrounding structure.

---

## Weapon Size Tiers

| Tier | Weapon                     | Approx. length |
| ---- | -------------------------- | -------------- |
| 0    | unarmed                    | —              |
| 1    | dagger, seax               | 20–35 cm       |
| 2    | hand axe, mace, shield     | 50–70 cm       |
| 3    | sword, generic, improvised | 70–110 cm      |
| 4    | great sword, long axe      | 120–160 cm     |
| 5    | spear                      | 180–260 cm     |

---

## Space / Terrain Classification

| `terrain_context`                 | Space tier   | Examples                       |
| --------------------------------- | ------------ | ------------------------------ |
| `open`, `stone`, `winter`, `sand` | `free`       | field, courtyard, shore        |
| `ship`, `interior`, `forest`      | `moderate`   | longhouse, sparse woodland     |
| `narrow`, `forest_dense`          | `tight`      | corridor, alley, dense thicket |
| `crowd`                           | `packed`     | surrounded by combatants       |
| `barrow`, `low_ceiling`           | `very_tight` | burial mound, mine drift       |

---

## Attack Modifier — Space × Weapon Size

| Space      | sz 0 | sz 1 | sz 2 | sz 3 | sz 4 | sz 5 |
| ---------- | ---: | ---: | ---: | ---: | ---: | ---: |
| free       |    0 |    0 |    0 |    0 |    0 |    0 |
| moderate   |    0 |    0 |    0 |   −5 |  −15 |  −25 |
| tight      |   +5 |   +5 |    0 |  −10 |  −25 |  −40 |
| very_tight |  +10 |  +15 |   +5 |  −20 |  −40 |  −60 |
| packed     |    0 |   +5 |    0 |  −10 |  −20 |  −30 |

Short weapons gain a small positive modifier in tight/very_tight — the unarmed
fighter or knife-fighter has an actual tactical advantage in close quarters.

---

## Stamina Surcharge — per Offensive/Control Action

| Space      | sz 0 | sz 1 | sz 2 | sz 3 | sz 4 | sz 5 |
| ---------- | ---: | ---: | ---: | ---: | ---: | ---: |
| free       |    0 |    0 |    0 |    0 |    0 |    0 |
| moderate   |    0 |    0 |    0 |    0 |   +1 |   +1 |
| tight      |    0 |    0 |    0 |   +1 |   +2 |   +3 |
| very_tight |    0 |    0 |   +1 |   +2 |   +3 |   +4 |
| packed     |    0 |    0 |    0 |   +1 |   +2 |   +2 |

Applies to attack, control, and grapple-entry maneuvers only. Recovery moves
(GUARD, STAND, STEP_IN/BACK) are unaffected — you can always flinch backward.

---

## Special Rules

### HEAVY_BLOW blocked in very_tight

No room for the overhead arc. The maneuver is removed from the available set in
`barrow` and `low_ceiling` terrain.

### STEP_BACK blocked in very_tight

No room to disengage rearward in a dead-end tunnel or collapsed structure.

### Polearm in very_tight = haft-only

A spear (sz 5) in `very_tight` space cannot be used normally even if reach
distance is technically fine — same `haft_only = True` override as reach fouls
(base damage 3, −60 attack modifier applied by the terrain rule).

### Prone + large weapon

A fighter on the ground with a great sword orsword of size ≥ 4 cannot lever the
weapon effectively. Each size tier above 3 adds −15 to attacks:

- sz 4 (great sword): −15 additional while prone
- sz 5 (spear): −30 additional while prone

This stacks with the normal prone penalties.

### Friendly fire in packed/very_tight terrain

When a large-weapon fighter (sz ≥ 4) misses an attack in `packed` or
`very_tight` space, their backswing may clip an ally.

- sz 4: 10 % chance per miss
- sz 5: 20 % chance per miss

Target: random living ally on the same side. Damage: `weapon_base // 2`
(glancing blow only), no defense roll. Produces `is_friendly_fire: True` flag
in the action log.

---

## Large Skirmish Auto-Crowd

When `run_skirmish` starts with six or more total fighters and all fighters have
`open` terrain, their terrain is automatically upgraded to `crowd`. This models
the reality that six people hacking at each other in a field rapidly form a
packed melee — there is no clean swing room.

---

## AI Behaviour

- **Polearm / great weapon in very_tight**: immediately prefers `STEP_BACK` to
  escape the space. Falls back to `GUARD` if retreat is blocked.
- **Dagger / unarmed in tight/very_tight**: small aggression boost (+25 %
  chance of choosing an attack over a wait) to exploit the positional advantage.
- **Existing distance management** (PROPOSAL*003) is unaffected; the two
  systems layer — a short weapon fighter will want to both \_close distance* and
  *stay in tight terrain* when advantageous.
- **Weapon switching in tight terrain or at foul range**: if a fighter carries
  a secondary weapon (size ≤ 2) and the active weapon is either fouled by
  distance (`reach_pen ≤ −30`) or the terrain is `tight`/`very_tight` with
  weapon size ≥ 4, the AI returns `SWITCH_WEAPON` before falling back to
  `STEP_BACK` or `GUARD`. No switch occurs when the secondary is the same size
  class or larger than the active weapon.

---

## Interaction with PROPOSAL_003 (Weapon Reach)

Both penalties apply simultaneously:

- Spear at CLOSE (reach-fouled, −30) in a `narrow` corridor (terrain, −40):
  total −70 plus haft-only override from whichever rule triggers first.
- Dagger at LONG (reach penalty −40) but in `very_tight` space (+15 bonus):
  net −25 — the dagger fighter is still compromised by distance, but less so
  than in open ground because the cramped space protects both parties equally.

---

## Implementation Checklist

- [x] `WEAPON_SIZE_TABLE` constant
- [x] `TERRAIN_SPACE_CLASS` mapping
- [x] `TERRAIN_SIZE_ATTACK_MODS` table
- [x] `TERRAIN_SIZE_STAMINA_EXTRA` table
- [x] Helper functions: `get_weapon_size`, `get_space_class`,
      `compute_terrain_penalty`, `terrain_stamina_extra`
- [x] `Fighter.weapon_size` auto-set in `__post_init__`
- [x] `to_dict` / `from_dict` updated
- [x] `can_maneuver`: HEAVY_BLOW and STEP_BACK blocked in `very_tight`
- [x] `resolve_fighter_action`: terrain stamina surcharge on offensive actions
- [x] `resolve_attack`: terrain modifier, polearm-in-tunnel haft-only,
      prone + large weapon penalty
- [x] `choose_maneuver`: terrain/size AI block
- [x] `run_skirmish`: auto-crowd upgrade, friendly fire on miss
- [x] Narrative output: friendly fire line in duel and skirmish printers
- [x] `20_SIMULATION_RULES.md` §4.3 added
- [x] `test_weapon_size.py` — full test suite
- [x] `Maneuver.SWITCH_WEAPON` added to enum and `MANEUVER_STAMINA`
- [x] `Fighter.secondary_weapons` field; `switch_to_best_secondary()` method
- [x] `can_maneuver(SWITCH_WEAPON)`: gated on non-empty secondary list,
      not GRAPPLED/PINNED; allowed while DISARMED (drawing backup clears it)
- [x] `resolve_fighter_action`: SWITCH_WEAPON case, clears DISARMED,
      falls back to GUARD if secondary list is empty at resolution time
- [x] `choose_maneuver`: switch at foul band OR tight terrain + large weapon
- [x] `pick_secondary_weapons_from_gear` in `bestiary_loader.py`;
      `entry_to_fighter` populates `secondary_weapons`
- [x] `to_dict` / `from_dict` updated for `secondary_weapons`
- [x] Narrative output: duel + skirmish printers handle `switch_weapon` action
- [x] `20_SIMULATION_RULES.md` §4.2 SWITCH_WEAPON entry added
- [x] `test_weapon_switch.py` — full test suite
