# PROPOSAL 003 — Weapon Reach and Distance Management

## Status

Proposed · Not yet implemented in 20_SIMULATION_RULES.md or combat_sim.py

---

## Summary

Weapons have physical lengths. A longer weapon creates a threat zone that a shorter-weapon
fighter must penetrate to land a blow. This proposal adds a four-band distance model to
every duel and skirmish, attaches a reach tier to each weapon, and applies attack penalties
when a fighter is outside their weapon's effective range. Two new distance-management
maneuvers — STEP\_IN and STEP\_BACK — let fighters shift the engagement distance.

The system ties directly into unarmed combat and the grapple sub-game: to initiate a throw
or seize, a fighter must first close to CLOSE range.

---

## Historical Basis — Real Weapon Lengths

Lengths are approximate for Viking-age northern Europe (8th–11th century).

| Weapon | Total length | Effective striking range | Period source |
| --- | --- | --- | --- |
| Fist / unarmed | arm length ~70 cm | body contact ~0–30 cm | universal |
| Dagger (knifr) | 30–45 cm overall | ~30–50 cm from body | Scandinavian finds |
| Seax (broad knife) | 45–65 cm overall | ~50–70 cm from body | Germanic / Norse |
| Hand axe (handsöx) | 50–70 cm overall | ~60–80 cm from body | Norse graves |
| Mace / club | 50–70 cm overall | ~60–80 cm from body | period finds |
| Sword (sverd) | 90–110 cm overall | ~80–110 cm from body | Viking-age swords |
| Great sword / war sword | 130–160 cm overall | ~130–160 cm from body | late period |
| Long axe (breiðöx) | 110–150 cm shaft | ~120–150 cm from body | sagas, Bayeux |
| Spear (spjót) | 180–240 cm overall | ~180–220 cm from body | burials, sagas |

---

## Distance Bands

Four discrete combat ranges replace the implied single-range model.

| Band | Name | Approx. real range | Optimal weapon class |
| --- | --- | --- | --- |
| 0 | GRAPPLE | 0–40 cm | unarmed, grapple |
| 1 | CLOSE | 40–90 cm | dagger, seax, hand axe |
| 2 | MELEE | 90–150 cm | sword, long axe (default start) |
| 3 | LONG | 150–250 cm | spear, great sword |

**Default starting distance is MELEE (2).** This reflects two fighters who have walked forward
to engage — sword range is the natural meeting point.

---

## Weapon Reach Table

| Weapon | Reach tier | Min band | Max band | Foul band | Notes |
| --- | --- | --- | --- | --- | --- |
| unarmed | 0 | 0 | 0 | — | must be at body contact |
| dagger | 1 | 0 | 1 | — | works from GRAPPLE to CLOSE |
| seax | 1 | 0 | 1 | — | same as dagger |
| hand\_axe | 2 | 0 | 2 | — | works from GRAPPLE to MELEE |
| mace | 2 | 0 | 2 | — | same as hand axe |
| sword | 3 | 1 | 2 | — | CLOSE to MELEE; -15 at GRAPPLE |
| great\_sword | 4 | 2 | 3 | 0 | MELEE to LONG; fouled at GRAPPLE |
| long\_axe | 4 | 2 | 3 | 0 | same as great sword |
| spear | 5 | 2 | 3 | 1 | MELEE to LONG; fouled at CLOSE/GRAPPLE |
| generic | 3 | 1 | 2 | — | fallback = sword profile |
| improvised | 2 | 0 | 2 | — | = axe profile |
| shield | 2 | 0 | 2 | — | shield-bash profile |

**Foul band** — if distance\_band ≤ foul\_band, the weapon is inside its own guard: only a
haft strike is possible (base damage 3, attack −30, labelled haft\_only in output).

---

## Attack Penalties

```text
Too far  (distance > max_band): −20 per band above maximum (can't reach)
Too close (distance < min_band): −15 per band below minimum (cramped, no swing arc)
Fouled   (distance ≤ foul_band): −30 attack, force weapon_base = 3 (haft strike)
In range (min_band ≤ distance ≤ max_band): 0 modifier
```

### Key interactions

- Spear vs sword at LONG (3): spear +0, sword −20 → spear has large effective advantage
- Spear vs sword at MELEE (2): both +0 → neutral
- Spear vs sword at CLOSE (1): spear FOULED −30 (haft only), sword +0 → sword wins decisively
- Dagger vs sword at MELEE (2): dagger −20, sword +0 → dagger fighter must close to CLOSE
- Unarmed vs sword at MELEE (2): fist −40, sword −15 → unarmed must reach GRAPPLE

---

## Distance Management Maneuvers

### STEP\_IN (close by one band)

- **As action**: 1 stamina, moves distance band −1 (minimum GRAPPLE)
- **As free reaction**: triggered automatically when the opponent's attack-type maneuver
  misses AND the defender's weapon reach is ≤ the attacker's; no stamina cost, does not
  consume the fighter's action slot for the round.
- AI preference: STEP\_IN is strongly preferred when current reach penalty ≥ 15.

### STEP\_BACK (open by one band)

- **As action**: 1 stamina, moves distance band +1 (maximum LONG)
- No free-reaction variant.
- AI preference: STEP\_BACK is preferred when the fight is inside the weapon's min\_band
  and the fighter needs to restore effective range.

Both maneuvers return `new_distance` in the action result. The fight loop immediately
syncs both fighters to the new band.

---

## Polearm Fouling Logic

When a spear or long axe is driven inside their guard (CLOSE or GRAPPLE for spear;
GRAPPLE for long axe / great sword):

- `haft_only: true` in the action result
- Attack modifier set to −30
- Weapon base damage overridden to 3 (blunt haft strike)
- Damage type carries no extra penetration — armour is fully effective

The polearm fighter recovers by executing STEP\_BACK on their turn. The swordsman/grappler
wins each round the distance stays inside the foul band.

---

## Grapple Entry Distance Gate

BROKARTOK, LAUSATOK, HRYGGSPENNA, TACKLE, and the legacy GRAPPLE control maneuver all
require `current_distance ≤ 1` (CLOSE). At MELEE or LONG, the grapple attempt is
unavailable — the fighter must STEP\_IN first.

This ties the grapple sub-game to the reach system: an unarmed fighter vs a swordsman must
close two bands (MELEE → CLOSE or GRAPPLE) before a throw is possible. In practice this
requires at least one STEP\_IN action before initiating a clinch.

---

## AI Behaviour

```
choose_maneuver additions:
  1. If current_distance > preferred_distance_band AND reach_penalty <= -15 → STEP_IN
  2. If current_distance < preferred_distance_band AND reach_penalty <= -15 → STEP_BACK
  3. If moderate penalty (-5 to -14) → include STEP_IN/STEP_BACK in pool at 70 % weight
  4. Long weapon vs opponent with shorter reach by 2+ tiers → weight STEP_BACK to avoid close-in

Free reaction (run_duel/run_skirmish):
  After each missed attack-type maneuver:
    if defender.weapon_reach <= attacker.weapon_reach
    and current_distance > preferred_distance_band(defender)
    → automatically apply STEP_IN, no cost, no action slot used
```

---

## Implementation Checklist

- [ ] Maneuver enum: `STEP_IN`, `STEP_BACK`
- [ ] MANEUVER\_STAMINA: both at 1
- [ ] WEAPON\_MANEUVERS: add "step\_in", "step\_back" to all weapon type sets
- [ ] MANEUVER\_HIT\_DESC: add "step\_in", "step\_back"
- [ ] Constants: `DIST_GRAPPLE=0`, `DIST_CLOSE=1`, `DIST_MELEE=2`, `DIST_LONG=3`
- [ ] Constants: `WEAPON_REACH_TABLE` dict
- [ ] Helper functions: `get_weapon_reach`, `compute_reach_penalty`, `preferred_distance_band`
- [ ] Fighter: `weapon_reach: int = 0` (auto-set in `__post_init__`)
- [ ] Fighter: `current_distance: int = 2` (synced by fight loop)
- [ ] Fighter.to\_dict(): include `weapon_reach`, `current_distance`
- [ ] `can_maneuver`: grapple entry (including legacy GRAPPLE) requires `current_distance <= 1`
- [ ] `can_maneuver`: STEP\_IN/STEP\_BACK always available (via WEAPON\_MANEUVERS)
- [ ] `choose_maneuver`: distance-aware AI branch
- [ ] `resolve_fighter_action`: dispatch STEP\_IN/STEP\_BACK, return `new_distance`
- [ ] `resolve_attack`: apply `compute_reach_penalty` to attack modifier; override base when fouled
- [ ] `run_duel`: track `distance` variable; sync fighters; handle free STEP\_IN reaction
- [ ] `run_skirmish`: same; pair-level distance via `current_distance` fields
- [ ] `_print_narrative_duel`: handle "step\_in", "step\_back" action types
- [ ] `20_SIMULATION_RULES.md`: add §4.2 Weapon Reach and Distance
- [ ] Tests: `test_weapon_reach.py`
