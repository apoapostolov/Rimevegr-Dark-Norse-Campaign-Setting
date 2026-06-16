#!/usr/bin/env python3
"""
Iron Ledger — Combat Simulator (HEMA Extended)

Round-by-round combat with Historical European Martial Arts depth:
stamina management, stances (Vom Tag/Pflug/Ochs/Alber), 14 maneuvers
(cuts, thrusts, half-sword, mordschlag, binds, grapples, disarms...),
7 condition types (prone, staggered, winded, dazed, disarmed, grappled,
bound), counter-attacks (Nachreisen), and a tactical AI that adapts
stance and maneuver selection to fighter state.

Backward-compatible with the v1 API: Fighter, run_duel, run_skirmish
all accept the same arguments and return the same base structure, with
additional HEMA fields appended.

Usage:
    python combat_sim.py duel --attacker '{"name":"Voss",...}' --defender '{"name":"Bandit",...}'
    python combat_sim.py skirmish --side-a '[...]' --side-b '[...]'
"""

import argparse
import json
import random
import sys
try:
    import yaml as _yaml
except ImportError:
    _yaml = None
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional

sys.path.insert(0, __file__ and __import__('os').path.dirname(__file__) or '.')
from engine import (
    resolve_check,
    resolve_opposed,
    hit_location,
    calculate_damage,
    wound_severity,
    compute_max_hp,
    compute_initiative,
    compute_max_stamina,
    compute_stamina_recovery,
    ResultLevel,
)


# ───────────────────────────────────────────────────────────────────────
from combat_types import *   # noqa: F401,F403
from combat_model import *   # noqa: F401,F403
from combat_targeting import (
    choose_skirmish_target,
    choose_skirmish_target_perception,
    commander_issue_orders,
    compute_directional_engagement,
)
from combat_narrative import (
    render_action,
    render_bloodied,
    render_bleeding,
    render_pre_battle,
    render_round_summary,
    render_status_line,
)
from combat_ai import *      # noqa: F401,F403
from combat_grapple import * # noqa: F401,F403
from animal_system import dog_support_profile, horse_charge_profile
from animal_care import apply_animal_wound, ensure_animal_health


# ───────────────────────────────────────────────────────────────────────
# Prompt 5 — formation warfare / morale contagion / rout helpers
# ───────────────────────────────────────────────────────────────────────

_FORMATION_DEF_BONUS = {
    "shield_wall": 8,
    "loose_line": 0,
    "wedge": -3,
    "broken": -10,
}

_FORMATION_ATK_BONUS = {
    "shield_wall": -2,
    "loose_line": 0,
    "wedge": 4,
    "broken": -6,
}


def _clamp_i(v: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, v))


def _side_depth(side: list[Fighter]) -> int:
    standing = [f for f in side if not f.is_down]
    if not standing:
        return 1
    # Approximate rank-depth for small tactical sims.
    return max(1, len(standing) // 3)


def _has_active_commander(side: list[Fighter]) -> bool:
    for f in side:
        if f.is_down:
            continue
        if f.is_commander or "rally_allies" in f.traits or "veteran_eye" in f.traits:
            return True
    return False


def _update_formation_and_morale(
    side: list[Fighter],
    enemy_side: list[Fighter],
    incoming_attackers: dict[str, list[str]],
    actions: list,
    round_num: int,
) -> None:
    """Apply per-round cohesion/morale pressure and emit Prompt 5 events."""
    standing = [f for f in side if not f.is_down]
    enemy_standing = [f for f in enemy_side if not f.is_down]
    if not standing:
        return

    depth_self = _side_depth(side)
    depth_enemy = _side_depth(enemy_side)
    depth_adv = depth_self - depth_enemy

    leader_down = any(
        (f.is_commander or "rally_allies" in f.traits or "veteran_eye" in f.traits) and f.is_down
        for f in side
    )
    leader_up = _has_active_commander(side)

    routed_allies = sum(1 for f in standing if f.rout_state == "rout")

    for f in standing:
        attackers = incoming_attackers.get(f.name, [])
        local_outnumber = max(0, len(enemy_standing) - len(standing))

        base_pressure = local_outnumber * 8 + max(0, len(attackers) - 1) * 12
        form = f.formation if f.formation in _FORMATION_DEF_BONUS else "loose_line"
        formation_relief = _FORMATION_DEF_BONUS[form]
        depth_relief = depth_adv * 4

        pressure = base_pressure - formation_relief - depth_relief
        if leader_down:
            pressure += 12
        if routed_allies > 0:
            pressure += routed_allies * 6
        if "terrifying_presence" in [t for e in enemy_standing for t in e.traits]:
            pressure += 4

        pressure = _clamp_i(pressure)
        f.frontage_pressure = pressure

        cohesion_delta = -(pressure // 8)
        morale_delta = -(pressure // 10)

        # Recovery channels
        if f.stance == Stance.DEFENSIVE:
            cohesion_delta += 1
        if leader_up:
            morale_delta += 1
        if form == "shield_wall":
            cohesion_delta += 1

        old_cohesion = f.cohesion_score
        old_morale = f.morale_score
        f.cohesion_score = _clamp_i(f.cohesion_score + cohesion_delta)
        f.morale_score = _clamp_i(f.morale_score + morale_delta)

        # Breakpoint and contagion
        old_rout = f.rout_state
        if f.cohesion_score < 15 or f.morale_score < 15:
            f.rout_state = "rout"
            f.formation = "broken"
        elif f.cohesion_score < 30 or f.morale_score < 30:
            f.rout_state = "wavering"
            if f.formation == "shield_wall":
                f.formation = "loose_line"
        else:
            f.rout_state = "steady"

        # Local-to-wide probabilistic break cascade.
        if f.rout_state == "rout" and old_rout != "rout":
            actions.append({
                "type": "breakpoint",
                "fighter": f.name,
                "round": round_num,
                "cohesion": f.cohesion_score,
                "morale": f.morale_score,
            })
            for ally in standing:
                if ally is f or ally.rout_state == "rout":
                    continue
                chance = 0.18 + (0.08 if ally.rout_state == "wavering" else 0.0)
                if random.random() < chance:
                    if ally.morale_score > 20:
                        ally.morale_score = _clamp_i(ally.morale_score - 20)
                    ally.rout_state = "wavering" if ally.rout_state == "steady" else ally.rout_state
                    actions.append({
                        "type": "morale_shock",
                        "source": f.name,
                        "target": ally.name,
                        "reason": "adjacent_unit_rout",
                    })

        # Round status surfacing for readability.
        if (old_cohesion != f.cohesion_score) or (old_morale != f.morale_score) or (old_rout != f.rout_state):
            actions.append({
                "type": "formation_status",
                "fighter": f.name,
                "formation": f.formation,
                "pressure": f.frontage_pressure,
                "cohesion": f.cohesion_score,
                "morale": f.morale_score,
                "rout_state": f.rout_state,
            })


# ───────────────────────────────────────────────────────────────────────
# Prompt 8 — missile combat, volleys, and suppression pressure
# ───────────────────────────────────────────────────────────────────────

_MISSILE_WEAPONS_LOCAL = set(MISSILE_WEAPONS)


def _is_missile_unit(f: Fighter) -> bool:
    return (
        f.weapon_type in _MISSILE_WEAPONS_LOCAL
        or getattr(f, "ammo_max", 0) > 0
        or getattr(f, "ammo_current", 0) > 0
    )


def _missile_weather_mod(terrain: str) -> int:
    t = (terrain or "").lower()
    if "blizzard" in t or "storm" in t:
        return -20
    if "fog" in t or "rain" in t:
        return -12
    if "wind" in t:
        return -8
    return 0


def _apply_suppression(target: Fighter, rounds: int) -> None:
    rounds = max(1, int(rounds))
    target.add_condition(ConditionType.SUPPRESSED, rounds)
    target.suppression_rounds = max(int(getattr(target, "suppression_rounds", 0)), rounds)


def _resolve_missile_phase(
    shooters: list[Fighter],
    enemies: list[Fighter],
    actions: list,
    round_num: int,
) -> None:
    """Resolve a pre-melee missile phase for one side."""
    if not shooters or not enemies:
        return

    for archer in [f for f in shooters if not f.is_down and _is_missile_unit(f)]:
        if archer.has_condition(ConditionType.GRAPPLED) or archer.has_condition(ConditionType.FLEEING):
            continue

        # Conservative in-fight resupply/scavenge behavior.
        if archer.ammo_current <= 0:
            if archer.resupplies_used < 1 and random.random() < 0.18:
                recovered = 2 if archer.ammo_max <= 0 else min(2, max(1, archer.ammo_max // 4))
                archer.ammo_current = recovered
                archer.resupplies_used += 1
                actions.append({
                    "type": "missile_resupply",
                    "attacker": archer.name,
                    "recovered": recovered,
                    "round": round_num,
                })
            else:
                continue

        living = [e for e in enemies if not e.is_down]
        if not living:
            return

        low_ammo = archer.ammo_max > 0 and archer.ammo_current <= max(1, archer.ammo_max // 5)
        mode = getattr(archer, "missile_mode", "auto")
        if mode not in {"auto", "aimed", "volley"}:
            mode = "auto"
        if mode == "auto":
            if low_ammo:
                mode = "aimed"
            else:
                mode = "volley" if len(living) >= 4 and archer.ammo_current >= 2 else "aimed"
        if mode == "volley" and archer.ammo_current < 2:
            mode = "aimed"

        volley_targets = sorted(
            living,
            key=lambda e: (
                e.formation == "shield_wall",
                e.get_armor_at("torso"),
                -e.frontage_pressure,
            ),
        )
        targets = [volley_targets[0]] if mode == "aimed" else volley_targets[: min(3, len(volley_targets))]
        ammo_spend = 1 if mode == "aimed" else 2
        archer.ammo_current = max(0, archer.ammo_current - ammo_spend)

        for tgt in targets:
            if tgt.is_down:
                continue
            weather_mod = _missile_weather_mod(archer.terrain)
            chance = 42 + archer.weapon_skill * 8 + (archer.wit - 5) * 4 + weather_mod
            chance -= max(0, tgt.nim - 3) * 3
            chance -= tgt.shield_def * 3

            if mode == "volley":
                chance -= 12
                if tgt.formation == "shield_wall":
                    chance -= 15
            else:
                chance += 6

            if tgt.rout_state != "steady":
                chance += 8
            if tgt.frontage_pressure >= 50:
                chance += 5

            chance = int(max(8, min(92, chance)))
            roll = random.randint(1, 100)
            hit = roll <= chance

            event = {
                "type": "missile_attack",
                "attacker": archer.name,
                "defender": tgt.name,
                "mode": mode,
                "ammo_left": archer.ammo_current,
                "hit": hit,
                "attack_roll": roll,
                "attack_chance": chance,
            }

            if hit:
                loc, loc_mult = hit_location()
                armor = tgt.get_armor_at(loc)
                base = max(1, archer.weapon_base + (archer.mig // 4) + (2 if mode == "aimed" else 0))
                dmg = calculate_damage(base, max(1, archer.mig), loc_mult, max(0, armor // 2))

                # Shield wall and frontal cover reduce lethality significantly.
                if tgt.formation == "shield_wall" and tgt.rout_state == "steady":
                    dmg = max(1, int(dmg * 0.45))
                # Exposed flanks/rear segments suffer heavier missile impact.
                if tgt.frontage_pressure >= 60 or tgt.rout_state != "steady":
                    dmg = int(dmg * 1.25)

                dmg = max(1, dmg)
                wound = tgt.apply_wound(loc, dmg)
                event.update({
                    "location": loc,
                    "final_damage": dmg,
                    "wound_severity": wound.severity,
                    "defender_down": tgt.is_down,
                })

            # Volleys suppress even on near-miss; aimed shots suppress mostly on hit.
            suppress_chance = 0.75 if mode == "volley" else (0.30 if hit else 0.15)
            if random.random() < suppress_chance:
                _apply_suppression(tgt, 2 if mode == "volley" else 1)
                event["suppressed"] = True

            actions.append(event)

        if archer.ammo_current == 0:
            actions.append({
                "type": "missile_ammo_empty",
                "attacker": archer.name,
                "round": round_num,
            })


# ───────────────────────────────────────────────────────────────────────
# Prompt 9 — mounted combat, anti-cavalry counters, and dismount flow
# ───────────────────────────────────────────────────────────────────────

_ANTI_CAV_WEAPONS = {"spear", "pike", "halberd", "poleaxe", "staff_spear"}


def _terrain_is_tight(terrain: str) -> bool:
    t = (terrain or "").lower()
    return any(k in t for k in ("forest", "woods", "swamp", "ruin", "barrow", "cave", "tight", "narrow"))


def _force_dismount(fighter: Fighter, actions: list, round_num: int, reason: str) -> None:
    if not fighter.mounted:
        return
    fighter.mounted = False
    fighter.mount_condition = "wounded"
    fighter.rider_stability = max(0, fighter.rider_stability - 25)
    fighter.dismount_vulnerability_rounds = max(fighter.dismount_vulnerability_rounds, 2)
    fighter.add_condition(ConditionType.STAGGERED, 1)
    actions.append({
        "type": "dismount_event",
        "fighter": fighter.name,
        "reason": reason,
        "round": round_num,
        "vulnerability_rounds": fighter.dismount_vulnerability_rounds,
    })


def _mount_proxy(fighter: Fighter) -> dict:
    mount = {
        "name": f"{fighter.name}'s mount",
        **dict(getattr(fighter, "mount_stats", {}) or {}),
        "hp": int(getattr(fighter, "mount_hp", 0) or 0),
        "max_hp": int(getattr(fighter, "mount_max_hp", 0) or 0),
        "wounds": list(getattr(fighter, "mount_wounds", []) or []),
        "health_status": "sound" if int(getattr(fighter, "mount_hp", 1) or 1) > 0 else "dead",
    }
    ensure_animal_health(mount, "horse")
    return mount


def _sync_mount_proxy(fighter: Fighter, mount: dict) -> None:
    fighter.mount_max_hp = int(mount.get("max_hp", fighter.mount_max_hp or 0) or 0)
    fighter.mount_hp = int(mount.get("hp", fighter.mount_hp or 0) or 0)
    fighter.mount_wounds = list(mount.get("wounds", []) or [])
    if mount.get("health_status") == "dead":
        fighter.mount_condition = "wounded"
        fighter.mounted = False


def _apply_mount_damage(fighter: Fighter, actions: list, round_num: int, damage: int, cause: str) -> None:
    mount = _mount_proxy(fighter)
    wound = apply_animal_wound(mount, damage=damage, location="torso", cause=cause)
    _sync_mount_proxy(fighter, mount)
    actions.append(
        {
            "type": "mount_wound",
            "fighter": fighter.name,
            "damage": damage,
            "severity": wound["severity"],
            "cause": cause,
            "mount_hp": fighter.mount_hp,
        }
    )
    if fighter.mount_hp <= 0:
        _force_dismount(fighter, actions, round_num, "mount_killed")


def _can_brace_anti_cavalry(defender: Fighter, defender_maneuver: Maneuver) -> bool:
    has_weapon = defender.weapon_type in _ANTI_CAV_WEAPONS
    has_stance = defender.stance == Stance.DEFENSIVE or defender_maneuver == Maneuver.GUARD
    return has_weapon and has_stance


def _resolve_mounted_charge(
    attacker: Fighter,
    defender: Fighter,
    defender_maneuver: Maneuver,
    allied_count: int,
    enemy_count: int,
    actions: list,
    round_num: int,
    horses_allowed: bool = True,
) -> dict:
    """Resolve mounted charge setup and anti-cavalry interactions.

    Returns action modifiers:
      - attack_mod
      - target_def_mod
      - bonus_damage
      - charged
    """
    out = {
        "attack_mod": 0,
        "target_def_mod": 0,
        "bonus_damage": 0,
        "charged": False,
    }

    if not horses_allowed:
        return out

    if not attacker.mounted:
        return out
    if attacker.charge_cooldown > 0:
        return out
    if attacker.has_condition(ConditionType.GRAPPLED) or attacker.has_condition(ConditionType.PRONE):
        return out

    if attacker.mount_condition == "panicked":
        # Panicked horse can throw rider if stability is already compromised.
        if attacker.rider_stability < 35 and random.random() < 0.35:
            _force_dismount(attacker, actions, round_num, "mount_panicked")
        return out

    tight = _terrain_is_tight(attacker.terrain)
    crowded = (allied_count + enemy_count) >= 10
    mount_profile = horse_charge_profile(attacker)

    charge_chance = 0.62
    if attacker.stance == Stance.AGGRESSIVE:
        charge_chance += 0.12
    if tight:
        charge_chance -= 0.30
    if crowded:
        charge_chance -= 0.18
    if attacker.mount_condition == "wounded":
        charge_chance -= 0.15
    charge_chance += float(mount_profile.get("charge_chance", 0.0))
    attacker.rider_stability = _clamp_i(
        int(attacker.rider_stability + int(mount_profile.get("stability", 0)))
    )

    if random.random() > max(0.05, min(0.92, charge_chance)):
        return out

    out["charged"] = True
    out["attack_mod"] = 12 + int(mount_profile.get("attack_mod", 0))
    out["target_def_mod"] = -5
    out["bonus_damage"] = 3 + int(mount_profile.get("bonus_damage", 0))

    if tight:
        out["attack_mod"] -= 8
        out["attack_mod"] += int(mount_profile.get("tight_attack_mod", 0))
        out["target_def_mod"] += 3
        out["bonus_damage"] = max(0, out["bonus_damage"] - 2)
    if crowded:
        out["attack_mod"] -= 5
        out["attack_mod"] += int(mount_profile.get("crowded_attack_mod", 0))
        out["target_def_mod"] += 2
        out["bonus_damage"] = max(0, out["bonus_damage"] - 1)

    attacker.charged_this_fight = True
    attacker.charge_cooldown = 2
    attacker.mount_fatigue = _clamp_i(
        int(getattr(attacker, "mount_fatigue", 0)) + 12 + int(mount_profile.get("fatigue_delta", 0))
    )

    brace = _can_brace_anti_cavalry(defender, defender_maneuver)
    stakes = "stake" in (defender.terrain or "").lower() or "stakes" in defender.traits
    if brace or stakes:
        brace_chance = 42 + defender.weapon_skill * 5 + (10 if brace else 0) + (15 if stakes else 0)
        brace_roll = random.randint(1, 100)
        brace_success = brace_roll <= max(10, min(95, brace_chance))
        actions.append({
            "type": "anti_cavalry_brace",
            "attacker": attacker.name,
            "defender": defender.name,
            "roll": brace_roll,
            "chance": max(10, min(95, brace_chance)),
            "success": brace_success,
            "stakes": stakes,
        })
        if brace_success:
            out["attack_mod"] -= 14
            out["target_def_mod"] += 6
            out["bonus_damage"] = max(0, out["bonus_damage"] - 3)
            attacker.rider_stability = max(0, attacker.rider_stability - random.randint(18, 30))
            if stakes:
                attacker.mount_condition = "wounded"
                _apply_mount_damage(attacker, actions, round_num, random.randint(4, 8), "stakes")
            if attacker.rider_stability <= 30 or random.random() < 0.35:
                _force_dismount(attacker, actions, round_num, "anti_cavalry_counter")

    fear_pressure = 0
    if "terrifying_presence" in defender.traits:
        fear_pressure += 18
    if defender.damage_type == "fire" or "fire" in defender.weapon_properties or "fire" in defender.traits:
        fear_pressure += 22
    if defender.frontage_pressure >= 60:
        fear_pressure += 8

    if fear_pressure > 0:
        fear_pressure = max(0, fear_pressure - int(mount_profile.get("fear_resist", 0)))
        fear_roll = random.randint(1, 100)
        fear_chance = min(90, fear_pressure + max(0, 50 - attacker.rider_stability) // 2)
        if fear_roll <= fear_chance:
            attacker.mount_condition = "panicked"
            out["attack_mod"] -= 8
            out["target_def_mod"] += 4
            attacker.rider_stability = max(0, attacker.rider_stability - 12)
            actions.append({
                "type": "mount_fear",
                "fighter": attacker.name,
                "roll": fear_roll,
                "chance": fear_chance,
                "trigger": "noise_fire_shock",
            })
            if attacker.rider_stability <= 22:
                _force_dismount(attacker, actions, round_num, "mount_panic_throw")
                _apply_mount_damage(attacker, actions, round_num, random.randint(2, 5), "panic_throw")

    actions.append({
        "type": "mount_charge",
        "attacker": attacker.name,
        "defender": defender.name,
        "terrain_tight": tight,
        "crowded": crowded,
        "attack_mod": out["attack_mod"],
        "target_def_mod": out["target_def_mod"],
        "bonus_damage": out["bonus_damage"],
    })
    return out

# ───────────────────────────────────────────────────────────────────────
# Resistance and Weakness helpers
# ───────────────────────────────────────────────────────────────────────

def apply_resistances(
    defender: Fighter,
    dmg: int,
    damage_type: str,
    maneuver: Maneuver,
    weapon_properties: list | None = None,
) -> int:
    """Apply defender's resistance tags to incoming damage. Returns adjusted dmg.

    Pre-battle resistances (fear, intimidation) are handled separately in
    the terrifying_presence pre-battle block; this function handles only
    damage-modifying resistances.
    """
    if weapon_properties is None:
        weapon_properties = []
    for r in defender.resistances:
        if r == "bleeding":
            pass  # handled in apply_wound / _update_wound_state
        elif r in ("pain", "pain_penalties"):
            pass  # handled in _update_wound_state via resistance check
        elif r == "cold":
            if damage_type == "cold":
                dmg = max(1, dmg // 2)
        elif r == "cold_immune":
            if damage_type == "cold":
                dmg = 0
        elif r == "piercing":
            if maneuver == Maneuver.THRUST:
                dmg = max(1, dmg // 2)
        elif r == "physical_weapons":
            bypass = {"fire", "cold", "supernatural", "iron"}
            if damage_type not in bypass and "iron" not in weapon_properties:
                dmg = 0
        elif r == "cutting_weapons":
            if maneuver in (Maneuver.CUT, Maneuver.HEAVY_BLOW):
                dmg = 0
        elif r in ("non-magical_weapons", "non-magical weapons"):
            # same effect as ancient_resilience trait: halve mundane damage
            dmg = max(1, dmg // 2)
        elif r == "all_physical":
            dmg = 0
    return max(0, dmg)


def apply_weaknesses(
    defender: Fighter,
    dmg: int,
    damage_type: str,
    attacker: Fighter,
    maneuver: Maneuver,
    loc: str,
) -> tuple:
    """Apply defender's weakness tags after resistances. Returns (adjusted_dmg, silver_bypass).

    silver_bypass=True means skip ancient_resilience and force bleeding on the
    wound even if defender has bleeding resistance.

    Notes:
    - "sunlight" per-round damage is applied in the round tick (run_duel), not here.
    - "loud_noise" pre-battle check is applied in run_duel pre-battle block.
    - "fire_aversion" AI behaviour is in combat_ai.py choose_stance/choose_maneuver.
    - "decapitation" is_down flag is set by the caller after wound is applied.
    """
    silver_bypass = False
    for w in defender.weaknesses:
        if w == "fire":
            if damage_type == "fire":
                dmg = int(dmg * 1.5)
        elif w == "silver":
            if "silver" in attacker.weapon_properties:
                silver_bypass = True
        elif w == "iron":
            # iron makes physical_weapons resistance ineffective — handled in
            # apply_resistances via weapon_properties; nothing more to do here
            pass
        elif w == "spear_set":
            if (attacker.weapon_type == "spear"
                    and getattr(attacker, "guarded_last_round", False)
                    and maneuver in (Maneuver.CUT, Maneuver.THRUST)):
                dmg += 4
        # "decapitation", "sunlight", "loud_noise", "fire_aversion",
        # "outnumbered", "hearth_warmth" handled elsewhere
    return max(0, dmg), silver_bypass


def _is_pain_immune(fighter: Fighter) -> bool:
    """Return True when a fighter should not process acute pain spikes."""
    if fighter.is_undead:
        return True
    resistances = set(getattr(fighter, "resistances", []) or [])
    traits = set(getattr(fighter, "traits", []) or [])
    return (
        "pain" in resistances
        or "pain_penalties" in resistances
        or "unfeeling" in traits
        or "incorporeal" in traits
    )


def _is_pain_fueled_berserker(fighter: Fighter) -> bool:
    """Berserker-style pain response: spikes empower offense but narrow awareness."""
    traits = set(getattr(fighter, "traits", []) or [])
    return (
        "berserk" in traits
        or "berserker_pain_fury" in traits
        or "blackwine_rage" in traits
    )


def _is_desperate_fury_active(fighter: Fighter) -> bool:
    """desperate_fury is active only at or below 50% HP."""
    return (
        "desperate_fury" in (getattr(fighter, "traits", []) or [])
        and fighter.hp <= fighter.max_hp * 0.5
    )


def _pain_spike_score(wound: Wound) -> int:
    """Compute acute spike intensity from wound severity + location + impact."""
    sev = {
        "scratch": 0,
        "light": 1,
        "serious": 2,
        "critical": 3,
        "mortal": 4,
    }
    score = sev.get(wound.severity, 0)
    if wound.location in ("head", "torso", "hands", "feet"):
        score += 1
    if wound.damage >= 8:
        score += 1
    return score


def _apply_pain_spike(defender: Fighter, wound: Wound, result: dict) -> None:
    """Apply acute neurologic pain responses from a fresh wound.

    Focus is on sudden spikes (blackout, stance loss, tunnel vision, grip loss),
    not baseline chronic pain.
    """
    if wound is None or _is_pain_immune(defender):
        return

    spike = _pain_spike_score(wound)
    if spike < 2:
        return

    # Everyone except pain-immune creatures gets narrowed perception on spikes.
    if _is_pain_fueled_berserker(defender):
        # Berserkers get stronger under pain, but perceptually narrower and less efficient.
        defender.pain_fury_rounds = min(defender.pain_fury_rounds + 2, 6)
        defender.add_condition(ConditionType.TUNNEL_VISION, 2)
        result["pain_spike"] = {
            "score": spike,
            "berserker_fury_rounds": defender.pain_fury_rounds,
        }
        return

    defender.add_condition(ConditionType.PAIN_SHOCK, 1)
    defender.add_condition(ConditionType.TUNNEL_VISION, 1)

    events = []
    if spike >= 3 and random.random() < 0.35:
        defender.add_condition(ConditionType.DISARMED, -1)
        events.append("weapon_drop")
    if spike >= 3 and random.random() < 0.30:
        defender.add_condition(ConditionType.STAGGERED, 1)
        events.append("stumble")
    if spike >= 4 and random.random() < 0.20:
        defender.add_condition(ConditionType.DAZED, 2)
        defender.add_condition(ConditionType.PRONE, 2)
        events.append("blackout")

    result["pain_spike"] = {
        "score": spike,
        "events": events,
    }


# ───────────────────────────────────────────────────────────────────────
# Batch 7 — On-Death Dispatch
# ───────────────────────────────────────────────────────────────────────

def dispatch_death_effects(
    dead: Fighter,
    all_fighters: list,
    side: list,
    events: list,
) -> None:
    """Fire on-death effects for a just-downed fighter.

    Args:
        dead:         fighter that just reached is_down=True
        all_fighters: every combatant in the fight (includes dead)
        side:         list of fighters on the same side as dead (for ally buffs)
        events:       list to append structured event dicts into
    """
    survivors = [f for f in all_fighters if not f.is_down and f is not dead]
    allies = [f for f in survivors if f in side]

    for effect in dead.death_effects:
        if effect == "death_rattle":
            events.append({
                "type": "on_death",
                "effect": "death_rattle",
                "source": dead.name,
                "narrative": f"[ON-DEATH] {dead.name}'s final moan echoes; nearby dead stir",
                "hit": False,
            })

        elif effect == "weapon_throw_on_death":
            enemies = [f for f in survivors if f not in side]
            if enemies:
                target = random.choice(enemies)
                a_attr = dead.mig + getattr(dead, "mig_bonus", 0)
                d_attr = target.nim + getattr(target, "nim_bonus", 0)
                a_mods = dead.attack_chance_mods() - 20  # -20 death penalty
                d_mods = target.defense_chance_mods() + target.shield_def
                opposed = resolve_opposed(
                    a_attr, dead.weapon_skill, a_mods,
                    d_attr, target.shield_skill, d_mods,
                    a_label=dead.name,
                    d_label=target.name,
                )
                ev = {
                    "type": "on_death",
                    "effect": "weapon_throw_on_death",
                    "source": dead.name,
                    "attacker": dead.name,
                    "defender": target.name,
                    "maneuver": "cut",
                    "stance": dead.stance.value,
                    "is_death_throw": True,
                    "attack_roll": opposed.attacker.roll,
                    "attack_chance": opposed.attacker.final_chance,
                    "defense_roll": opposed.defender.roll,
                    "defense_chance": opposed.defender.final_chance,
                    "winner": opposed.winner,
                }
                if opposed.winner == "attacker":
                    loc, loc_mult = hit_location()
                    armor_val = target.get_armor_at(loc)
                    dmg = calculate_damage(dead.weapon_base, a_attr, loc_mult, armor_val)
                    dmg = apply_resistances(
                        target, dmg, dead.damage_type, Maneuver.CUT,
                        weapon_properties=dead.weapon_properties,
                    )
                    if dmg > 0:
                        wound = target.apply_wound(loc, dmg)
                        ev.update({
                            "hit": True,
                            "location": loc,
                            "final_damage": dmg,
                            "wound_severity": wound.severity,
                            "defender_down": target.is_down,
                        })
                    else:
                        ev["hit"] = False
                else:
                    ev["hit"] = False
                events.append(ev)

        elif effect == "corpse_burst_4_2":
            hit_list = []
            for f in survivors:
                burst_dmg = 4
                tou_check = resolve_check(f.tou, 0, 0, f"{f.name} corpse_burst TOU")
                if tou_check.result.value in ("success", "critical_success"):
                    burst_dmg = 2
                w = f.apply_wound("torso", burst_dmg)
                hit_list.append({
                    "target": f.name,
                    "damage": burst_dmg,
                    "halved": burst_dmg == 2,
                    "wound_severity": w.severity,
                })
            events.append({
                "type": "on_death",
                "effect": "corpse_burst_4_2",
                "source": dead.name,
                "hits": hit_list,
                "narrative": f"[ON-DEATH] {dead.name} detonates in a spray of grave-rot",
                "hit": True,
            })

        elif effect == "nauseating_burst":
            nausea_list = []
            for f in survivors:
                tou_check = resolve_check(f.tou, 0, 0, f"{f.name} nausea TOU")
                if tou_check.result.value in ("failure", "critical_failure"):
                    f.add_condition(ConditionType.WINDED, 3)
                    nausea_list.append({"target": f.name, "effect": "winded"})
            events.append({
                "type": "on_death",
                "effect": "nauseating_burst",
                "source": dead.name,
                "affected": nausea_list,
                "narrative": f"[ON-DEATH] {dead.name}'s death-stench overwhelms the area",
                "hit": False,
            })

        elif effect == "death_command":
            rally_dur = random.randint(1, 6)
            for f in allies:
                f.death_command_rounds = rally_dur
            events.append({
                "type": "on_death",
                "effect": "death_command",
                "source": dead.name,
                "allies_buffed": [f.name for f in allies],
                "rounds": rally_dur,
                "narrative": f"[ON-DEATH] {dead.name}'s final cry drives allies forward ({rally_dur} rounds)",
                "hit": False,
            })

        elif effect == "veil_snap_aoe":
            hit_list = []
            for f in survivors:
                snap_dmg = random.randint(1, 8)
                wil_check = resolve_check(f.wil, 0, 0, f"{f.name} veil_snap WIL")
                if wil_check.result.value in ("success", "critical_success"):
                    snap_dmg = max(1, snap_dmg // 2)
                w = f.apply_wound("torso", snap_dmg)
                hit_list.append({"target": f.name, "damage": snap_dmg})
            events.append({
                "type": "on_death",
                "effect": "veil_snap_aoe",
                "source": dead.name,
                "hits": hit_list,
                "narrative": "[ON-DEATH] Reality violently reasserts — veil whiplash tears through the area",
                "hit": True,
            })

        elif effect == "flash_freeze":
            hit_list = []
            for f in survivors:
                freeze_dmg = random.randint(1, 6)
                w = f.apply_wound("torso", freeze_dmg)
                hit_list.append({"target": f.name, "damage": freeze_dmg})
            events.append({
                "type": "on_death",
                "effect": "flash_freeze",
                "source": dead.name,
                "hits": hit_list,
                "narrative": f"[ON-DEATH] {dead.name} flash-freezes the air — frost shards tear outward",
                "hit": True,
            })

        elif effect == "petrification_cascade":
            hit_list = []
            for f in survivors:
                if f.has_condition(ConditionType.GRAPPLED):
                    pet_dmg = random.randint(1, 6)
                    w = f.apply_wound("torso", pet_dmg)
                    hit_list.append({"target": f.name, "damage": pet_dmg})
            events.append({
                "type": "on_death",
                "effect": "petrification_cascade",
                "source": dead.name,
                "grappled_hit": hit_list,
                "narrative": f"[ON-DEATH] {dead.name} collapses — stone-dust shock harms grappled fighters",
                "hit": bool(hit_list),
            })


# ───────────────────────────────────────────────────────────────────────
# Resolution — Attack maneuvers
# ───────────────────────────────────────────────────────────────────────

def resolve_attack(
    attacker: Fighter,
    defender: Fighter,
    maneuver: Maneuver,
    defender_maneuver: Maneuver,
    result: dict,
) -> dict:
    """Resolve an attack-type maneuver against a defending fighter."""
    # ── Maneuver-specific modifiers ──
    atk_mod = 0
    dmg_mod = attacker.damage_bonus()
    armor_bypass = 0
    halve_extremity = False

    # Animal trait hooks (Batch 5)
    if "pack_tactics" in attacker.traits:
        atk_mod += min(getattr(attacker, "allies_in_fight", 0), 3) * 10
    if "den_fighter" in attacker.traits and attacker.terrain in ("cave", "barrow", "den"):
        atk_mod += 20
    if getattr(attacker, "territorial_rage_active", False):
        atk_mod += 10
    if "terrifying_charge" in attacker.traits and not getattr(attacker, "charged_this_fight", False):
        dmg_mod += 2
        attacker.charged_this_fight = True
    if getattr(attacker, "pain_fury_rounds", 0) > 0:
        atk_mod += 10

    # Supernatural trait hooks (Batch 8)
    _wrong_geo_auto_hit = False
    if ("wrong_geometry" in attacker.traits
            and not getattr(attacker, "wrong_geometry_used", False)):
        attacker.wrong_geometry_used = True
        wit_check = resolve_check(defender.wit, 0, 0, f"{defender.name} wrong_geometry WIT")
        if wit_check.result.value in ("failure", "critical_failure"):
            _wrong_geo_auto_hit = True
            result["wrong_geometry_surprise"] = True
    if "cold_aura" in defender.traits:
        atk_mod -= 10
    if ("domain_bonus_3" in attacker.traits
            and attacker.terrain == getattr(attacker, "home_terrain", "")):
        atk_mod += 15
    if "water_strength" in attacker.traits and attacker.terrain == "water":
        atk_mod += 10
        dmg_mod += 2
    if ("shapeshifter" in attacker.traits
            and getattr(attacker, "shapeshifter_surprise_active", False)):
        atk_mod += 20
        attacker.shapeshifter_surprise_active = False
        result["shapeshifter_surprise_used"] = True
    if getattr(attacker, "death_command_rounds", 0) > 0:
        atk_mod += 10

    # Batch 9 — Boss trait attack modifiers
    if _is_desperate_fury_active(attacker):
        atk_mod += 20
    if ("patient_strike" in attacker.traits
            and getattr(attacker, "guarded_last_round", False)):
        atk_mod += 20
    if ("veteran_eye" in attacker.traits
            and getattr(attacker, "veteran_target", "") == defender.name):
        atk_mod += 10
    if ("fire_bearer_torchbonus" in attacker.traits
            and attacker.weapon_type in ("torch", "improvised")
            and defender.is_undead):
        dmg_mod += 2
    # Batch 10 — reality_warping: attacker takes -10 when targeting a warping creature
    if getattr(defender, "reality_warping_rounds", 0) > 0:
        atk_mod -= 10

    # Wolfshead traits — attack modifiers
    # dirty_fighter: +10 atk vs opponents already destabilised
    if "dirty_fighter" in attacker.traits:
        if (defender.has_condition(ConditionType.PRONE)
                or defender.has_condition(ConditionType.STAGGERED)
                or defender.has_condition(ConditionType.DAZED)
                or defender.has_condition(ConditionType.WINDED)):
            atk_mod += 10
            result["dirty_fighter_bonus"] = True
    # curse_hex: target suffers -10 to all checks (counts as atk mod here)
    if getattr(defender, "curse_hex_rounds", 0) > 0:
        atk_mod -= 10  # defender fights worse while hexed
    if getattr(attacker, "curse_hex_rounds", 0) > 0:
        atk_mod -= 10  # attacker also degraded while hexed

    if maneuver == Maneuver.CUT:
        pass  # standard
    elif maneuver == Maneuver.THRUST:
        atk_mod = 10
        dmg_mod -= 1
        halve_extremity = True
    elif maneuver == Maneuver.HEAVY_BLOW:
        atk_mod = -15
        dmg_mod += 3
    elif maneuver == Maneuver.HALF_SWORD:
        atk_mod = 5
        dmg_mod -= 2
        armor_bypass = 3
    elif maneuver == Maneuver.MORDSCHLAG:
        atk_mod = -5
        # damage bonus/penalty resolved after location

    # ── Feint effect ──
    feint_active = attacker.feinted
    attacker.feinted = False
    if feint_active:
        atk_mod += 10
        result["feint_active"] = True

    # ── Reach penalty (PROPOSAL_003) ──
    _reach_mod, _is_fouled, _base_override = compute_reach_penalty(
        attacker.weapon_type, attacker.current_distance)
    if _reach_mod != 0:
        atk_mod += _reach_mod
        result["reach_penalty"] = _reach_mod
    if _is_fouled:
        result["haft_only"] = True

    # ── Terrain penalty (PROPOSAL_004) ──
    _terrain_mod = compute_terrain_penalty(attacker.weapon_type, attacker.terrain_context)
    if _terrain_mod != 0:
        atk_mod += _terrain_mod
        result["terrain_penalty"] = _terrain_mod
    if _terrain_mod <= -50:
        result["haft_only"] = True
        _is_fouled = True
        _base_override = _base_override or 3

    # ── Prone + weapon-size penalty (PROPOSAL_004) ──
    if attacker.has_condition(ConditionType.PRONE) and attacker.weapon_size > 3:
        _prone_pen = -(attacker.weapon_size - 3) * 15
        atk_mod += _prone_pen
        result["prone_size_penalty"] = _prone_pen

    # ── Attack roll ──
    a_attr = attacker.mig + getattr(attacker, "mig_bonus", 0)
    a_skill = attacker.weapon_skill
    a_mods = attacker.attack_chance_mods() + atk_mod
    a_mods += getattr(attacker, "prebattle_attack_penalty", 0)

    # ── Defense roll ──
    d_attr = (
        defender.nim
        + getattr(defender, "nim_bonus", 0)
        + getattr(defender, "prebattle_nim_penalty", 0)
    )
    d_skill = defender.shield_skill
    d_mods = defender.defense_chance_mods()

    shield_bonus = defender.shield_def if not feint_active else 0
    d_mods += shield_bonus

    # Guard bonus
    if defender_maneuver == Maneuver.GUARD:
        d_mods += 15

    # Batch 8 defense modifiers
    if "cold_aura" in attacker.traits:
        d_mods -= 10
    if ("domain_bonus_3" in defender.traits
            and defender.terrain == getattr(defender, "home_terrain", "")):
        d_mods += 15

    # Batch 9 — desperate_fury defense bonus
    if _is_desperate_fury_active(defender):
        d_mods += 20

    # Wolfshead — curse_hex: defender also penalised on defense
    if getattr(defender, "curse_hex_rounds", 0) > 0:
        d_mods -= 10

    if _wrong_geo_auto_hit:
        result["attack_roll"] = None
        result["attack_chance"] = None
        result["defense_roll"] = None
        result["defense_chance"] = None
        result["winner"] = "attacker"
        _winner = "attacker"
    else:
        opposed = resolve_opposed(
            a_attr, a_skill, a_mods,
            d_attr, d_skill, d_mods,
            a_label=attacker.name,
            d_label=defender.name,
        )
        result["attack_roll"] = opposed.attacker.roll
        result["attack_chance"] = opposed.attacker.final_chance
        result["defense_roll"] = opposed.defender.roll
        result["defense_chance"] = opposed.defender.final_chance
        result["winner"] = opposed.winner
        _winner = opposed.winner

    # Batch 9 — read_the_field_once: force reroll, take worse result for attacker (once)
    if (_winner == "attacker"
            and not _wrong_geo_auto_hit
            and "read_the_field_once" in defender.traits
            and "read_the_field_once_used" not in getattr(defender, "used_traits", [])):
        defender.used_traits.append("read_the_field_once_used")
        reroll = resolve_opposed(
            a_attr, a_skill, a_mods,
            d_attr, d_skill, d_mods,
            a_label=attacker.name,
            d_label=defender.name,
        )
        result["read_the_field_once"] = {
            "original_winner": "attacker",
            "reroll_winner": reroll.winner,
        }
        if reroll.winner == "defender":
            _winner = "defender"
            result["winner"] = "defender"

    if _winner == "attacker":
        loc, loc_mult = hit_location()
        armor_val = defender.get_armor_at(loc)

        # Thrust halves extremity armor
        if halve_extremity and loc in ("right_arm", "left_arm", "hands", "feet", "legs"):
            armor_val = armor_val // 2
        # Half-sword bypasses armor
        if armor_bypass > 0:
            armor_val = max(0, armor_val - armor_bypass)
        # Mordschlag: bonus vs heavy armor, penalty vs light
        if maneuver == Maneuver.MORDSCHLAG:
            if armor_val >= 4:
                dmg_mod += 4
            elif armor_val <= 1:
                dmg_mod -= 3

        # Use haft-only base when fouled (reach or terrain)
        _wb = _base_override if _base_override is not None else attacker.weapon_base
        effective_base = max(1, _wb + dmg_mod)
        dmg = calculate_damage(effective_base, a_attr, loc_mult, armor_val)
        # Resistance pass
        dmg = apply_resistances(
            defender, dmg, attacker.damage_type, maneuver,
            weapon_properties=attacker.weapon_properties,
        )
        # Weakness pass (may set silver_bypass)
        dmg, silver_bypass = apply_weaknesses(
            defender, dmg, attacker.damage_type, attacker, maneuver, loc
        )
        # incorporeal immunity (Batch 8)
        if "incorporeal" in defender.traits:
            _bypass_types = {"fire", "iron", "supernatural", "seidr"}
            if (attacker.damage_type not in _bypass_types
                    and not any(p in _bypass_types for p in attacker.weapon_properties)):
                dmg = 0
                result["incorporeal_immune"] = True
        # Ancient resilience (trait): halve non-magical damage unless silver bypass
        if not silver_bypass:
            factor = defender.incoming_damage_factor()
            if factor != 1.0 and dmg > 0:
                dmg = max(1, int(dmg * factor))

        # Bloodied ancient fury: each successful hit adds d4 frost damage
        if getattr(attacker, "bloodied_triggered", False) and "ancient_fury" in attacker.traits and dmg > 0:
            fury_cold = random.randint(1, 4)
            dmg += fury_cold
            result["ancient_fury_cold_bonus"] = fury_cold

        if dmg > 0:
            wound = defender.apply_wound(loc, dmg)
            # Silver bypass: force bleeding even on bleeding-resistant creatures
            if (silver_bypass and "bleeding" in defender.resistances
                    and wound.severity in ("serious", "critical", "mortal")):
                bleed_val = {"serious": 1, "critical": 2, "mortal": 3}[wound.severity]
                wound.bleeding = bleed_val
                defender.total_bleeding += bleed_val
            # Decapitation weakness: mortal/critical head hit = immediately down
            if ("decapitation" in defender.weaknesses
                    and loc == "head"
                    and wound.severity in ("critical", "mortal")):
                defender.is_down = True
            # Hamstring trait: critical/mortal wound cripples stamina recovery
            if ("hamstring" in attacker.traits
                    and wound.severity in ("critical", "mortal")):
                defender.add_condition(ConditionType.HAMSTRUNG, 6)
            _apply_pain_spike(defender, wound, result)
            # killing_cold_contact (Batch 8): apply FROSTBITTEN DOT on any successful hit
            if "killing_cold_contact" in attacker.traits:
                dot_dmg = random.randint(1, 4)
                dot_dur = random.randint(1, 4)
                defender.frostbitten_dmg = dot_dmg
                defender.add_condition(ConditionType.FROSTBITTEN, dot_dur)
                result["killing_cold_contact"] = {"dmg_per_round": dot_dmg, "rounds": dot_dur}
        else:
            wound = None

        result["hit"] = True
        result["location"] = loc
        result["location_multiplier"] = loc_mult
        result["raw_damage"] = effective_base + (attacker.mig // 3)
        result["armor_reduction"] = armor_val
        result["final_damage"] = dmg
        result["wound_severity"] = wound.severity if wound is not None else "none"
        result["resisted"] = (wound is None)
        result["defender_hp"] = defender.hp
        result["defender_down"] = defender.is_down
    else:
        result["hit"] = False

    return result

# ───────────────────────────────────────────────────────────────────────
# Resolution — Control maneuvers
# ───────────────────────────────────────────────────────────────────────

def resolve_control(
    attacker: Fighter,
    defender: Fighter,
    maneuver: Maneuver,
    result: dict,
) -> dict:
    """Resolve a control maneuver (bind, shove, grapple, shield bash, disarm)."""

    if maneuver == Maneuver.BIND:
        opposed = resolve_opposed(
            attacker.mig,
            attacker.weapon_skill,
            attacker.condition_attack_mod() + attacker.action_attack_mod,
            defender.mig,
            defender.weapon_skill,
            defender.condition_defense_mod() + defender.action_defense_mod,
            attacker.name, defender.name,
        )
        result["winner"] = opposed.winner
        if opposed.winner == "attacker":
            defender.add_condition(ConditionType.BOUND, 1)
            result["condition_applied"] = "bound"
            result["hit"] = True
        else:
            result["hit"] = False

    elif maneuver == Maneuver.SHOVE:
        # Also used to break grapple
        opposed = resolve_opposed(
            attacker.mig,
            0,
            attacker.condition_attack_mod() + attacker.action_attack_mod,
            defender.mig,
            0,
            defender.condition_defense_mod() + defender.action_defense_mod,
            attacker.name, defender.name,
        )
        result["winner"] = opposed.winner
        if opposed.winner == "attacker":
            if attacker.has_condition(ConditionType.GRAPPLED):
                attacker.remove_condition(ConditionType.GRAPPLED)
                defender.remove_condition(ConditionType.GRAPPLED)
                result["condition_applied"] = "grapple_broken"
            elif attacker.has_condition(ConditionType.BOUND):
                attacker.remove_condition(ConditionType.BOUND)
                result["condition_applied"] = "bind_broken"
            else:
                defender.add_condition(ConditionType.PRONE, -1)
                result["condition_applied"] = "prone"
            result["hit"] = True
        else:
            result["hit"] = False

    elif maneuver == Maneuver.GRAPPLE:
        a_attr = (attacker.mig + attacker.nim) // 2
        d_attr = (defender.mig + defender.nim) // 2
        opposed = resolve_opposed(
            a_attr,
            0,
            attacker.condition_attack_mod() + attacker.action_attack_mod,
            d_attr,
            0,
            defender.condition_defense_mod() + defender.action_defense_mod,
            attacker.name, defender.name,
        )
        result["winner"] = opposed.winner
        if opposed.winner == "attacker":
            defender.add_condition(ConditionType.GRAPPLED, -1)
            if "maul_bite" in attacker.traits:
                attacker.add_condition(ConditionType.MAUL_ACTIVE, -1)
            # bone_gnaw: free automatic bite after grapple success (no attack roll)
            if "bone_gnaw" in attacker.traits:
                _bite_dmg = 4
                _bite_wound = defender.apply_wound("torso", _bite_dmg)
                result["bone_gnaw_bite"] = {
                    "damage": _bite_dmg,
                    "severity": _bite_wound.severity,
                    "armor_bypassed": True,
                }
            result["condition_applied"] = "grappled"
            result["hit"] = True
        else:
            result["hit"] = False

    elif maneuver == Maneuver.SHIELD_BASH:
        opposed = resolve_opposed(
            attacker.mig,
            attacker.shield_skill,
            attacker.shield_def + attacker.action_attack_mod,
            defender.nim,
            0,
            defender.condition_defense_mod() + defender.action_defense_mod,
            attacker.name, defender.name,
        )
        result["winner"] = opposed.winner
        if opposed.winner == "attacker":
            defender.add_condition(ConditionType.STAGGERED, 1)
            result["condition_applied"] = "staggered"
            result["hit"] = True
        else:
            result["hit"] = False

    elif maneuver == Maneuver.DISARM:
        # Requires target to be bound or staggered
        if not (defender.has_condition(ConditionType.BOUND)
                or defender.has_condition(ConditionType.STAGGERED)):
            result["action"] = "disarm_no_opening"
            result["hit"] = False
            return result
        opposed = resolve_opposed(
            attacker.wit,
            attacker.weapon_skill,
            attacker.action_attack_mod,
            defender.wit,
            defender.weapon_skill,
            defender.action_defense_mod,
            attacker.name, defender.name,
        )
        result["winner"] = opposed.winner
        if opposed.winner == "attacker":
            defender.add_condition(ConditionType.DISARMED, -1)
            result["condition_applied"] = "disarmed"
            result["hit"] = True
        else:
            result["hit"] = False

    return result


# ───────────────────────────────────────────────────────────────────────
# Resolution — Counter-attack (Nachreisen)
# ───────────────────────────────────────────────────────────────────────

def resolve_counter(attacker: Fighter, defender: Fighter) -> dict:
    """
    Resolve a counter-attack from a successful defender.

    The counter-attacker catches the original attacker off-balance:
    - Low Guard counter: +15 accuracy (the bait paid off)
    - Standard counter: -10 accuracy (reactive, not ideal)
    - Original attacker: -5 defense, halved shield (committed to strike)
    """
    result = {
        "attacker": attacker.name,
        "defender": defender.name,
        "maneuver": "counter",
        "stance": attacker.stance.value,
        "is_counter": True,
    }

    attacker.spend_stamina(1)

    counter_mod = 15 if attacker.stance == Stance.LOW_GUARD else -10

    a_attr = attacker.mig + getattr(attacker, "mig_bonus", 0)
    a_skill = attacker.weapon_skill
    a_mods = attacker.attack_chance_mods() + counter_mod
    a_mods += getattr(attacker, "prebattle_attack_penalty", 0)
    if getattr(attacker, "pain_fury_rounds", 0) > 0:
        a_mods += 10
    if _is_desperate_fury_active(attacker):
        a_mods += 20

    d_attr = (
        defender.nim
        + getattr(defender, "nim_bonus", 0)
        + getattr(defender, "prebattle_nim_penalty", 0)
    )
    d_skill = defender.shield_skill
    d_mods = defender.defense_chance_mods() - 5  # off-balance after attacking
    if defender.shield_def > 0:
        d_mods += defender.shield_def // 2  # reduced shield effectiveness

    opposed = resolve_opposed(
        a_attr, a_skill, a_mods,
        d_attr, d_skill, d_mods,
        a_label=attacker.name,
        d_label=defender.name,
    )

    result["attack_roll"] = opposed.attacker.roll
    result["attack_chance"] = opposed.attacker.final_chance
    result["defense_roll"] = opposed.defender.roll
    result["defense_chance"] = opposed.defender.final_chance
    result["winner"] = opposed.winner

    if opposed.winner == "attacker":
        loc, loc_mult = hit_location()
        armor_val = defender.get_armor_at(loc)
        dmg = calculate_damage(attacker.weapon_base, a_attr, loc_mult, armor_val)
        # Resistance and weakness passes (counter-attacks use attacker's damage_type)
        dmg = apply_resistances(
            defender, dmg, attacker.damage_type, Maneuver.CUT,
            weapon_properties=attacker.weapon_properties,
        )
        dmg, silver_bypass = apply_weaknesses(
            defender, dmg, attacker.damage_type, attacker, Maneuver.CUT, loc
        )
        # incorporeal immunity check (same as resolve_attack)
        if "incorporeal" in defender.traits:
            _bypass_types = {"fire", "iron", "supernatural", "seidr"}
            if (attacker.damage_type not in _bypass_types
                    and not any(p in _bypass_types for p in attacker.weapon_properties)):
                dmg = 0
        if not silver_bypass:
            factor = defender.incoming_damage_factor()
            if factor != 1.0 and dmg > 0:
                dmg = max(1, int(dmg * factor))
        if getattr(attacker, "bloodied_triggered", False) and "ancient_fury" in attacker.traits and dmg > 0:
            fury_cold = random.randint(1, 4)
            dmg += fury_cold
            result["ancient_fury_cold_bonus"] = fury_cold
        if dmg > 0:
            wound = defender.apply_wound(loc, dmg)
            if (silver_bypass and "bleeding" in defender.resistances
                    and wound.severity in ("serious", "critical", "mortal")):
                bleed_val = {"serious": 1, "critical": 2, "mortal": 3}[wound.severity]
                wound.bleeding = bleed_val
                defender.total_bleeding += bleed_val
            if ("decapitation" in defender.weaknesses
                    and loc == "head"
                    and wound.severity in ("critical", "mortal")):
                defender.is_down = True
            if ("hamstring" in attacker.traits
                    and wound.severity in ("critical", "mortal")):
                defender.add_condition(ConditionType.HAMSTRUNG, 6)
            _apply_pain_spike(defender, wound, result)
        else:
            wound = None

        result["hit"] = True
        result["location"] = loc
        result["location_multiplier"] = loc_mult
        result["raw_damage"] = attacker.weapon_base + (attacker.mig // 3)
        result["armor_reduction"] = armor_val
        result["final_damage"] = dmg
        result["wound_severity"] = wound.severity if wound is not None else "none"
        result["resisted"] = (wound is None)
        result["defender_hp"] = defender.hp
        result["defender_down"] = defender.is_down
    else:
        result["hit"] = False

    return result


# ───────────────────────────────────────────────────────────────────────
# Resolution — Unified action dispatch
# ───────────────────────────────────────────────────────────────────────

def resolve_fighter_action(
    attacker: Fighter,
    defender: Fighter,
    maneuver: Maneuver,
    defender_maneuver: Maneuver,
) -> dict:
    """Resolve one fighter's chosen maneuver for the round."""
    if attacker.is_down:
        return {"action": "skip", "reason": "combatant down",
                "attacker": attacker.name, "defender": defender.name}
    if defender.is_down:
        return {"action": "skip", "reason": "target down",
                "attacker": attacker.name, "defender": defender.name}

    result = {
        "attacker": attacker.name,
        "defender": defender.name,
        "maneuver": maneuver.value,
        "stance": attacker.stance.value,
    }

    # ── Pay stamina (downgrade if insufficient) ──
    cost = MANEUVER_STAMINA[maneuver] + STANCE_MODS[attacker.stance]["stamina_extra"]
    # Terrain surcharge for weapon-swinging actions (PROPOSAL_004)
    if maneuver in ATTACK_MANEUVERS or maneuver in CONTROL_MANEUVERS:
        cost += terrain_stamina_extra(attacker.weapon_type, attacker.terrain_context)
    if cost > attacker.stamina:
        if attacker.stamina >= MANEUVER_STAMINA[Maneuver.CUT]:
            maneuver = Maneuver.CUT
            cost = MANEUVER_STAMINA[Maneuver.CUT]
        else:
            maneuver = Maneuver.GUARD
            cost = 0
        result["maneuver"] = maneuver.value
        result["downgraded"] = True
    attacker.spend_stamina(cost)

    # ── Recovery maneuvers ──
    if maneuver == Maneuver.STAND:
        attacker.remove_condition(ConditionType.PRONE)
        result["action"] = "stand"
        result["hit"] = False
        return result

    if maneuver == Maneuver.PICK_UP_WEAPON:
        attacker.remove_condition(ConditionType.DISARMED)
        result["action"] = "pick_up"
        result["hit"] = False
        return result

    if maneuver == Maneuver.SWITCH_WEAPON:
        sw = attacker.switch_to_best_secondary(prefer_size=2)
        if sw is None:
            # No usable secondary—fall back to guard recovery
            attacker.recover_stamina(2)
            result["action"] = "guard"
        else:
            attacker.remove_condition(ConditionType.DISARMED)  # backup draw clears disarmed
            result["action"] = "switch_weapon"
            result["old_weapon"] = sw["old_type"]
            result["new_weapon"] = sw["new_type"]
        result["hit"] = False
        return result

    # ── Guard ──
    if maneuver == Maneuver.GUARD:
        attacker.recover_stamina(2)  # bonus recovery for guarding
        result["action"] = "guard"
        result["hit"] = False
        return result

    # ── Distance movement (PROPOSAL_003) ──
    if maneuver == Maneuver.STEP_IN:
        new_dist = max(DIST_GRAPPLE, attacker.current_distance - 1)
        attacker.current_distance = new_dist
        defender.current_distance = new_dist
        result["action"] = "step_in"
        result["new_distance"] = new_dist
        result["hit"] = False
        return result

    if maneuver == Maneuver.STEP_BACK:
        new_dist = min(DIST_LONG, attacker.current_distance + 1)
        attacker.current_distance = new_dist
        defender.current_distance = new_dist
        result["action"] = "step_back"
        result["new_distance"] = new_dist
        result["hit"] = False
        return result

    # ── Feint ──
    if maneuver == Maneuver.FEINT:
        opposed = resolve_opposed(
            attacker.wit, attacker.weapon_skill, 0,
            defender.wit, defender.weapon_skill, 0,
            a_label=attacker.name,
            d_label=defender.name,
        )
        result["winner"] = opposed.winner
        if opposed.winner == "attacker":
            attacker.feinted = True
            result["action"] = "feint_success"
        else:
            result["action"] = "feint_fail"
        result["hit"] = False
        return result

    # ── Control maneuvers ──
    if maneuver in CONTROL_MANEUVERS:
        return resolve_control(attacker, defender, maneuver, result)

    # ── Grapple entry (PROPOSAL_002) ──
    if maneuver in GRAPPLE_ENTRY_MANEUVERS:
        return resolve_grapple_entry(attacker, defender, maneuver, result)

    # ── In-grapple positional + Glíma finishers (PROPOSAL_002) ──
    if maneuver in IN_GRAPPLE_MANEUVERS or maneuver in GLIMA_FINISHER_MANEUVERS:
        return resolve_ingrapple_move(attacker, defender, maneuver, result)

    # ── Dirty tactics (PROPOSAL_002) ──
    if maneuver in DIRTY_MANEUVERS:
        return resolve_dirty(attacker, defender, maneuver, result)

    # ── Attack maneuvers ──
    return resolve_attack(attacker, defender, maneuver, defender_maneuver, result)

# Legacy compatibility wrapper
# ───────────────────────────────────────────────────────────────────────

def resolve_attack_round(attacker: Fighter, defender: Fighter) -> dict:
    """v1 API: resolve one attack as a simple cut."""
    return resolve_fighter_action(attacker, defender, Maneuver.CUT, Maneuver.BALANCED)


# ───────────────────────────────────────────────────────────────────────
# Trauma condition round checks (§5.18–5.26)
# ───────────────────────────────────────────────────────────────────────

def check_trauma_conditions(
    fighter: Fighter,
    opponent: Fighter,
    ctx: dict,
) -> dict:
    """Apply active trauma conditions at the start of a fighter's round.

    Returns a result dict with:
      - effects: list of triggered effects with roll details
      - skip_round: True if fighter cannot act this round (battle_shock)
      - anger_storm_active: True if fighter must attack a random adjacent target
      - block_retreat: True if risk_seeking blocks a planned retreat
    """
    result: dict = {
        "type": "trauma_check",
        "fighter": fighter.name,
        "effects": [],
        "skip_round": False,
        "anger_storm_active": False,
        "block_retreat": False,
    }
    conditions = getattr(fighter, "trauma_conditions", []) or []
    if not conditions:
        return result

    shield_bonus = 10 if getattr(fighter, "allies_in_fight", 0) > 0 else 0
    fatigue_pen = -10 if fighter.stamina < fighter.max_stamina * 0.3 else 0
    wil_eff = fighter.wil + getattr(fighter, "wil_penalty", 0)
    wil_chance = max(5, min(95, 50 + wil_eff * 5 + shield_bonus + fatigue_pen))

    for tc in conditions:
        cond = tc.get("condition") if isinstance(tc, dict) else tc
        roll = random.randint(1, 100)
        passed = roll <= wil_chance

        if cond == "battle_shock":
            if not passed:
                skip = random.randint(1, 6)
                fighter.add_condition(ConditionType.STAGGERED, skip)
                result["effects"].append({
                    "condition": cond,
                    "roll": roll,
                    "chance": wil_chance,
                    "effect": f"skip {skip} rounds (battle_shock)",
                })
                result["skip_round"] = True

        elif cond == "anger_storm":
            if not passed:
                result["effects"].append({
                    "condition": cond,
                    "roll": roll,
                    "chance": wil_chance,
                    "effect": "attack_random_adjacent (anger_storm)",
                })
                result["anger_storm_active"] = True

        elif cond == "risk_seeking":
            if ctx.get("retreating"):
                if not passed:
                    result["effects"].append({
                        "condition": cond,
                        "roll": roll,
                        "chance": wil_chance,
                        "effect": "ignore_retreat_stay_and_fight (risk_seeking)",
                    })
                    result["block_retreat"] = True

        elif cond == "flinch_sickness":
            # Always applies; no WIL check
            fighter.init_penalty = getattr(fighter, "init_penalty", 0) - 5
            result["effects"].append({
                "condition": cond,
                "effect": "initiative -5 this round (flinch_sickness)",
            })

        elif cond == "heavy_mind":
            # Always applies; no WIL check
            result["effects"].append({
                "condition": cond,
                "effect": "no_initiative_based_actions (heavy_mind)",
            })
            result["skip_round"] = True

    return result


# ───────────────────────────────────────────────────────────────────────
# Initiative
# ───────────────────────────────────────────────────────────────────────

def resolve_initiative(fighters: list[Fighter]) -> list[Fighter]:
    """Determine action order, factoring in stance modifiers."""
    inits = []
    for f in fighters:
        if f.is_down:
            continue
        _nim = max(1, f.nim + getattr(f, "prebattle_nim_penalty", 0))
        _wit = max(1, f.wit + getattr(f, "prebattle_wit_penalty", 0))
        init_val = compute_initiative(_nim, _wit, f.weapon_speed)
        init_val += STANCE_MODS.get(f.stance, STANCE_MODS[Stance.BALANCED])["init"]
        init_val -= getattr(f, "init_penalty", 0)
        inits.append((init_val, f))
    inits.sort(key=lambda x: (-x[0], -x[1].nim, -x[1].wit))
    return [f for _, f in inits]


# ───────────────────────────────────────────────────────────────────────
# Combat modes
# ───────────────────────────────────────────────────────────────────────

def run_duel(
    fighter_a: Fighter, fighter_b: Fighter, max_rounds: int = 30,
    starting_distance: int = DIST_MELEE,
) -> dict:
    """Run a full duel between two fighters with HEMA depth."""
    rounds = []
    pre_battle = []
    death_effects_fired = set()

    def _dispatch_new_deaths(action_log: list) -> None:
        for dead, side in ((fighter_a, [fighter_a]), (fighter_b, [fighter_b])):
            if dead.is_down and dead.name not in death_effects_fired:
                dispatch_death_effects(dead, [fighter_a, fighter_b], side, action_log)
                death_effects_fired.add(dead.name)

    # ── Sync starting distance ──
    current_distance = starting_distance
    fighter_a.current_distance = current_distance
    fighter_b.current_distance = current_distance
    fighter_a.charged_this_fight = False
    fighter_b.charged_this_fight = False

    # ── Darkness perception penalty (PROPOSAL_005) ──
    # A fighter in darkness who cannot see an opponent adds BLINDED-equivalent
    # attack penalty (-20) for the attacker; defender in darkness is also -20.
    # Resolved by marking BLINDED on entry if ambient contains "darkness".
    for f in [fighter_a, fighter_b]:
        if "darkness" in f.ambient and not f.has_condition(ConditionType.BLINDED):
            f.add_condition(ConditionType.BLINDED, 9999)  # persists until cleared

    # ── Surprise round resolution (PROPOSAL_005) ──
    # Any fighter with aware=False gets UNAWARE (1 round, -50 defense, no counter/reaction).
    # Unaware fighters are sorted last in the surprise round regardless of NIM/WIT.
    _has_surprise = not fighter_a.aware or not fighter_b.aware
    if _has_surprise:
        for f in [fighter_a, fighter_b]:
            if not f.aware:
                f.add_condition(ConditionType.UNAWARE, 1)
        pre_battle.append({"type": "surprise_round", "unaware": [
            f.name for f in [fighter_a, fighter_b] if not f.aware
        ]})

    # ── Pre-battle: Terrifying Presence ──
    for src, tgt in [(fighter_a, fighter_b), (fighter_b, fighter_a)]:
        if "terrifying_presence" in src.traits:
            # Fear resistance tags auto-pass the WIL check
            fear_immune = (
                "fear" in tgt.resistances
                or "intimidation" in tgt.resistances
                or ("fear_from_undead" in tgt.resistances and src.is_undead)
            )
            if fear_immune:
                pre_battle.append({
                    "type": "terror_resisted",
                    "source": src.name,
                    "target": tgt.name,
                    "roll": None,
                    "chance": None,
                    "immunity": True,
                })
            else:
                wil_check = resolve_check(tgt.wil, 0, 0, f"{tgt.name} terror WIL")
                if wil_check.result.value in ("failure", "critical_failure"):
                    if "commanding_presence" in src.traits:
                        flee_rounds = random.randint(1, 4)
                        tgt.add_condition(ConditionType.FLEEING, flee_rounds)
                        pre_battle.append({
                            "type": "terror_failed",
                            "source": src.name,
                            "target": tgt.name,
                            "roll": wil_check.roll,
                            "chance": wil_check.final_chance,
                            "effect": f"fleeing ({flee_rounds} rounds)",
                        })
                    else:
                        tgt.add_condition(ConditionType.STAGGERED, 2)
                        pre_battle.append({
                            "type": "terror_failed",
                            "source": src.name,
                            "target": tgt.name,
                            "roll": wil_check.roll,
                            "chance": wil_check.final_chance,
                            "effect": "staggered (2 rounds)",
                        })
                else:
                    pre_battle.append({
                        "type": "terror_resisted",
                        "source": src.name,
                        "target": tgt.name,
                        "roll": wil_check.roll,
                        "chance": wil_check.final_chance,
                    })

    # ── Pre-battle: Loud Noise weakness ──
    for creature, opponent in [(fighter_a, fighter_b), (fighter_b, fighter_a)]:
        if "loud_noise" in creature.weaknesses:
            import random as _r
            if _r.random() < 0.40:  # 40% WIL check failure
                flee_rounds = _r.randint(1, 4)
                creature.add_condition(ConditionType.FLEEING, flee_rounds)
                pre_battle.append({
                    "type": "loud_noise_flee",
                    "target": creature.name,
                    "rounds": flee_rounds,
                })

    # ── Pre-battle: Batch 10 events ──
    _temp_plunge_done = False
    for src, tgt in [(fighter_a, fighter_b), (fighter_b, fighter_a)]:
        # grave_moan: WIL check (difficulty -5); fail → initiative -5 for fight
        if "grave_moan" in src.traits:
            check = resolve_check(tgt.wil, 0, -5, f"{tgt.name} grave_moan WIL")
            if check.result.value in ("failure", "critical_failure"):
                tgt.init_penalty = 5
                pre_battle.append({
                    "type": "grave_moan",
                    "source": src.name,
                    "target": tgt.name,
                    "roll": check.roll,
                    "chance": check.final_chance,
                    "effect": "initiative -5",
                })
            else:
                pre_battle.append({
                    "type": "grave_moan_resisted",
                    "source": src.name,
                    "target": tgt.name,
                    "roll": check.roll,
                    "chance": check.final_chance,
                })
        # stench_cloud: TOU check; fail → WINDED 1 round
        if "stench_cloud" in src.traits:
            check = resolve_check(tgt.tou, 0, 0, f"{tgt.name} stench_cloud TOU")
            if check.result.value in ("failure", "critical_failure"):
                tgt.add_condition(ConditionType.WINDED, 1)
                pre_battle.append({
                    "type": "stench_cloud",
                    "source": src.name,
                    "target": tgt.name,
                    "roll": check.roll,
                    "chance": check.final_chance,
                    "effect": "winded (1 round)",
                })
        # choking_darkness: WIT check; fail → -20 to all attacks for 2 rounds
        if "choking_darkness" in src.traits:
            check = resolve_check(tgt.wit, 0, 0, f"{tgt.name} choking_darkness WIT")
            if check.result.value in ("failure", "critical_failure"):
                tgt.prebattle_attack_penalty -= 20
                tgt.prebattle_attack_penalty_rounds = max(tgt.prebattle_attack_penalty_rounds, 2)
                pre_battle.append({
                    "type": "choking_darkness",
                    "source": src.name,
                    "target": tgt.name,
                    "roll": check.roll,
                    "chance": check.final_chance,
                    "effect": "-20 attack (2 rounds)",
                })
        # sleep_weight: WIL check; fail → -20 NIM/WIT for d6 rounds
        if "sleep_weight" in src.traits:
            check = resolve_check(tgt.wil, 0, 0, f"{tgt.name} sleep_weight WIL")
            if check.result.value in ("failure", "critical_failure"):
                dur = random.randint(1, 6)
                tgt.prebattle_nim_penalty -= 4
                tgt.prebattle_nim_penalty_rounds = max(tgt.prebattle_nim_penalty_rounds, dur)
                tgt.prebattle_wit_penalty -= 4
                tgt.prebattle_wit_penalty_rounds = max(tgt.prebattle_wit_penalty_rounds, dur)
                pre_battle.append({
                    "type": "sleep_weight",
                    "source": src.name,
                    "target": tgt.name,
                    "roll": check.roll,
                    "chance": check.final_chance,
                    "effect": f"-20 NIM/WIT ({dur} rounds)",
                    "rounds": dur,
                })
        # domain_warning: pre-activate domain_bonus_3 (home_terrain = fight terrain)
        if "domain_warning" in src.traits and "domain_bonus_3" in src.traits:
            src.home_terrain = src.terrain
            pre_battle.append({
                "type": "domain_warning",
                "source": src.name,
                "effect": f"domain bonus active (terrain={src.terrain})",
            })
        # glamour_shift: prime shapeshifter surprise
        if "glamour_shift" in src.traits and "shapeshifter" in src.traits:
            src.shapeshifter_surprise_active = True
            pre_battle.append({
                "type": "glamour_shift",
                "source": src.name,
                "effect": "shapeshifter surprise primed",
            })
        # ── Batch 8: Shapeshifter pre-battle check ──
        if "shapeshifter" in src.traits and not getattr(src, "shapeshifter_surprise_active", False):
            # If glamour_shift didn't prime it, try a direct WIT check
            check = resolve_check(tgt.wit, 0, 0, f"{tgt.name} shapeshifter WIT")
            if check.result.value in ("failure", "critical_failure"):
                src.shapeshifter_surprise_active = True
                pre_battle.append({
                    "type": "shapeshifter_disguise",
                    "source": src.name,
                    "target": tgt.name,
                    "roll": check.roll,
                    "chance": check.final_chance,
                    "effect": "shapeshifter surprise active (+20 next attack)",
                })
            else:
                pre_battle.append({
                    "type": "shapeshifter_seen_through",
                    "source": src.name,
                    "target": tgt.name,
                    "roll": check.roll,
                    "chance": check.final_chance,
                })
        # ── Batch 8: Lure_song pre-battle check ──
        if "lure_song" in src.traits:
            check = resolve_check(tgt.wil, 0, 0, f"{tgt.name} lure_song WIL", difficulty=40)
            if check.result.value in ("failure", "critical_failure"):
                entranced_rounds = random.randint(1, 4)
                tgt.lure_song_entranced_rounds = entranced_rounds
                pre_battle.append({
                    "type": "lure_song_entranced",
                    "source": src.name,
                    "target": tgt.name,
                    "roll": check.roll,
                    "chance": check.final_chance,
                    "effect": f"entranced ({entranced_rounds} rounds)",
                    "rounds": entranced_rounds,
                })
            else:
                pre_battle.append({
                    "type": "lure_song_resisted",
                    "source": src.name,
                    "target": tgt.name,
                    "roll": check.roll,
                    "chance": check.final_chance,
                })
        # ── Batch 8: Dread_aura pre-battle effect ──
        if "dread_aura" in src.traits:
            tgt.wil_penalty -= 1
            tgt.wil_penalty = max(tgt.wil_penalty, -3)  # cap at -3
            pre_battle.append({
                "type": "dread_aura",
                "source": src.name,
                "target": tgt.name,
                "effect": f"WIL penalty accumulated (current: {tgt.wil_penalty})",
                "wil_penalty": tgt.wil_penalty,
            })
        # ground_tremor: NIM check; fail → -5 to next action
        if "ground_tremor" in src.traits:
            check = resolve_check(tgt.nim, 0, 0, f"{tgt.name} ground_tremor NIM")
            if check.result.value in ("failure", "critical_failure"):
                tgt.prebattle_attack_penalty -= 5
                tgt.prebattle_attack_penalty_rounds = max(tgt.prebattle_attack_penalty_rounds, 1)
                pre_battle.append({
                    "type": "ground_tremor",
                    "source": src.name,
                    "target": tgt.name,
                    "roll": check.roll,
                    "chance": check.final_chance,
                    "effect": "-5 next action",
                })
        # temperature_plunge: all fighters suffer -1 TOU for the fight
        if "temperature_plunge" in src.traits and not _temp_plunge_done:
            _temp_plunge_done = True
            for _f in [fighter_a, fighter_b]:
                _f.tou = max(1, _f.tou - 1)
            pre_battle.append({
                "type": "temperature_plunge",
                "source": src.name,
                "effect": "all combatants: -1 TOU (bitter cold)",
            })
        # reality_warping: opponents take -10 atk for rounds 1\u20133
        if "reality_warping" in src.traits:
            src.reality_warping_rounds = 3
            pre_battle.append({
                "type": "reality_warping",
                "source": src.name,
                "effect": "opponents \u221210 attack for 3 rounds",
            })
        # ── Wolfshead: curse_hex pre-battle check ──
        # Seiðr-Worker cursing the opponent (WIL 45%); fail → -10 all rolls d4 rounds
        if "curse_hex" in src.traits:
            check = resolve_check(tgt.wil, 0, 0, f"{tgt.name} curse_hex WIL", difficulty=45)
            if check.result.value in ("failure", "critical_failure"):
                hex_rounds = random.randint(1, 4)
                tgt.curse_hex_rounds = hex_rounds
                pre_battle.append({
                    "type": "curse_hex",
                    "source": src.name,
                    "target": tgt.name,
                    "roll": check.roll,
                    "chance": check.final_chance,
                    "effect": f"hexed (-10 all rolls, {hex_rounds} rounds)",
                    "rounds": hex_rounds,
                })
            else:
                pre_battle.append({
                    "type": "curse_hex_resisted",
                    "source": src.name,
                    "target": tgt.name,
                    "roll": check.roll,
                    "chance": check.final_chance,
                })
        # ── Wolfshead: prepared_ground pre-battle trap check ──
        # Trapper has laid snares; opponent NIM check (50%); fail → HAMSTRUNG 2 rounds
        if "prepared_ground" in src.traits and not getattr(src, "prepared_ground_triggered", False):
            src.prepared_ground_triggered = True
            check = resolve_check(tgt.nim, 0, 0, f"{tgt.name} prepared_ground NIM")
            if check.result.value in ("failure", "critical_failure"):
                tgt.add_condition(ConditionType.HAMSTRUNG, 2)
                pre_battle.append({
                    "type": "prepared_ground",
                    "source": src.name,
                    "target": tgt.name,
                    "roll": check.roll,
                    "chance": check.final_chance,
                    "effect": "snare caught — HAMSTRUNG 2 rounds",
                })
            else:
                pre_battle.append({
                    "type": "prepared_ground_avoided",
                    "source": src.name,
                    "target": tgt.name,
                    "roll": check.roll,
                    "chance": check.final_chance,
                })

    # ── Veteran eye: tag primary target ──
    for src, tgt in [(fighter_a, fighter_b), (fighter_b, fighter_a)]:
        if "veteran_eye" in src.traits:
            src.veteran_target = tgt.name

    for rnd in range(1, max_rounds + 1):
        if fighter_a.is_down or fighter_b.is_down:
            break

        pre_round_events = []
        for f, opponent in ((fighter_a, fighter_b), (fighter_b, fighter_a)):
            if ("skirmisher_retreat" in f.traits
                    and not f.is_down
                    and not f.has_condition(ConditionType.FLEEING)):
                self_losing = (
                    f.hp <= f.max_hp * 0.5
                    and opponent.hp >= opponent.max_hp * 0.7
                )
                if self_losing:
                    f.add_condition(ConditionType.FLEEING, random.randint(1, 2))
                    pre_round_events.append({
                        "type": "skirmisher_retreat",
                        "fighter": f.name,
                        "effect": "retreating (outmatched)",
                    })

        # 1v1 has no pack ally bonus
        fighter_a.allies_in_fight = 0
        fighter_b.allies_in_fight = 0

        # ── Phase 1: Stance selection ──
        fighter_a.stance = choose_stance(fighter_a, fighter_b)
        fighter_b.stance = choose_stance(fighter_b, fighter_a)

        # ── Phase 2: Maneuver selection ──
        man_a = choose_maneuver(fighter_a, fighter_b)
        man_b = choose_maneuver(fighter_b, fighter_a)

        # ── Phase 3: Initiative ──
        # Unaware fighters (PROPOSAL_005) are sorted after all aware fighters
        # regardless of NIM/WIT score — they cannot act before being struck.
        order = resolve_initiative([fighter_a, fighter_b])
        order.sort(key=lambda f: (1 if f.has_condition(ConditionType.UNAWARE) else 0,))

        # ── Phase 4: Actions ──
        actions = list(pre_round_events)
        acted = set()

        for actor in order:
            if actor.is_down or actor.name in acted:
                continue

            target = fighter_b if actor is fighter_a else fighter_a
            if target.is_down:
                continue

            actor_man = man_a if actor is fighter_a else man_b
            target_man = man_b if actor is fighter_a else man_a

            # ── Trauma condition check ──
            if getattr(actor, "trauma_conditions", []):
                tc = check_trauma_conditions(actor, target, {"round": rnd})
                if tc.get("effects"):
                    actions.append(tc)
                if tc.get("skip_round"):
                    acted.add(actor.name)
                    continue

            action = resolve_fighter_action(actor, target, actor_man, target_man)
            actions.append(action)
            acted.add(actor.name)
            _dispatch_new_deaths(actions)

            # Sync shared distance after any step action
            if action.get("action") in ("step_in", "step_back"):
                current_distance = action["new_distance"]

            # Counter check: only if an attack was defended (UNAWARE fighters cannot counter)
            if (action.get("winner") == "defender"
                    and not target.is_down
                    and target.name not in acted
                    and not target.has_condition(ConditionType.UNAWARE)
                    and action.get("maneuver") in (
                        "cut", "thrust", "heavy_blow",
                        "half_sword", "mordschlag")
                    and can_counter(target)):
                counter = resolve_counter(target, actor)
                actions.append(counter)
                acted.add(target.name)
                _dispatch_new_deaths(actions)

            # Free reaction: short-weapon fighter steps in after long-weapon miss
            elif (action.get("winner") == "defender"
                    and not target.is_down
                    and target.name not in acted
                    and not target.has_condition(ConditionType.UNAWARE)
                    and current_distance > DIST_GRAPPLE
                    and preferred_distance_band(target.weapon_type) < current_distance):
                new_dist = max(DIST_GRAPPLE, current_distance - 1)
                target.current_distance = new_dist
                actor.current_distance = new_dist
                current_distance = new_dist
                actions.append({
                    "attacker": target.name,
                    "defender": actor.name,
                    "maneuver": "step_in",
                    "action": "step_in",
                    "new_distance": new_dist,
                    "hit": False,
                    "free_reaction": True,
                })
                _dispatch_new_deaths(actions)

        # ── Phase 5: End-of-round ──
        bleed_log = {}
        for f in [fighter_a, fighter_b]:
            if not f.is_down:
                # Stamina recovery
                rec = compute_stamina_recovery(f.tou)
                if f.has_condition(ConditionType.HAMSTRUNG):
                    rec = max(0, rec // 2)
                if getattr(f, "pain_fury_rounds", 0) > 0:
                    rec = max(0, rec - 1)
                    f.pain_fury_rounds = max(0, f.pain_fury_rounds - 1)
                # mig_bonus_timer: blackwine_rage expires after timer reaches 0
                if getattr(f, "mig_bonus_timer", 0) > 0:
                    f.mig_bonus_timer -= 1
                    if f.mig_bonus_timer == 0:
                        f.mig_bonus = max(0, f.mig_bonus - 2)
                # reality_warping: decrement per round
                if getattr(f, "reality_warping_rounds", 0) > 0:
                    f.reality_warping_rounds = max(0, f.reality_warping_rounds - 1)
                # tactical_withdrawal_active: clear after one round
                if getattr(f, "tactical_withdrawal_active", False):
                    f.tactical_withdrawal_active = False
                # pre-battle temporary penalties
                if getattr(f, "prebattle_attack_penalty_rounds", 0) > 0:
                    f.prebattle_attack_penalty_rounds -= 1
                    if f.prebattle_attack_penalty_rounds == 0:
                        f.prebattle_attack_penalty = 0
                if getattr(f, "prebattle_nim_penalty_rounds", 0) > 0:
                    f.prebattle_nim_penalty_rounds -= 1
                    if f.prebattle_nim_penalty_rounds == 0:
                        f.prebattle_nim_penalty = 0
                if getattr(f, "prebattle_wit_penalty_rounds", 0) > 0:
                    f.prebattle_wit_penalty_rounds -= 1
                    if f.prebattle_wit_penalty_rounds == 0:
                        f.prebattle_wit_penalty = 0
                f.recover_stamina(rec)
                # Tick conditions
                f.tick_conditions()
                # Bleeding
                bl = f.apply_bleeding()
                if bl > 0:
                    bleed_log[f.name] = bleed_log.get(f.name, 0) + bl
                # Sunlight weakness tick
                if "sunlight" in f.weaknesses and f.terrain == "daylight_open":
                    f.sunlight_rounds += 1
                    sun_dmg = random.randint(1, 6)
                    f.hp -= sun_dmg
                    bleed_log[f.name] = bleed_log.get(f.name, 0) + sun_dmg
                    if f.sunlight_rounds >= 3:
                        f.is_down = True  # petrified / destroyed by sunlight
                # Choke asphyxiation (PROPOSAL_002)
                if f.has_condition(ConditionType.CHOKED) and not f.is_undead:
                    f.hp -= 4
                    bleed_log[f.name] = bleed_log.get(f.name, 0) + 4
                    if f.hp <= 0:
                        f.is_down = True
                    # Choke round tick — unconsciousness at round 4+ (§4.4 B5)
                    gs = getattr(f, "grapple_state", None)
                    if gs is not None and not f.is_down:
                        advance_choke_round(gs, f, actions)

                # ── Batch 8: Regeneration_1 ──
                if "regeneration_1" in f.traits and not f.is_down:
                    f.hp = min(f.hp + 1, f.max_hp)
                    actions.append({
                        "type": "regeneration",
                        "fighter": f.name,
                        "healing": 1,
                    })

                # ── Batch 8: Sunlight_petrification (trait) ──
                if "sunlight_petrification" in f.traits and f.terrain == "daylight_open" and not f.is_down:
                    f.sunlight_rounds += 1
                    sun_dmg = random.randint(1, 6)
                    f.hp -= sun_dmg
                    bleed_log[f.name] = bleed_log.get(f.name, 0) + sun_dmg
                    actions.append({
                        "type": "sunlight_petrification",
                        "fighter": f.name,
                        "rounds": f.sunlight_rounds,
                        "damage": sun_dmg,
                    })
                    if f.sunlight_rounds >= 3:
                        f.is_down = True  # petrified

                # ── Batch 8: Dread_aura per-round accumulation ──
                # Apply per-round wil_penalty accumulation (checked in pre-battle)
                # Assuming opponent with dread_aura applies -1 per round
                for opponent in [fighter_a, fighter_b]:
                    if opponent != f and "dread_aura" in opponent.traits:
                        if f.wil_penalty > -3:
                            f.wil_penalty -= 1
                            f.wil_penalty = max(f.wil_penalty, -3)

                # ── Batch 8: Lure_song entranced rounds countdown ──
                if getattr(f, "lure_song_entranced_rounds", 0) > 0:
                    f.lure_song_entranced_rounds -= 1

                # ── Wolfshead: curse_hex countdown ──
                if getattr(f, "curse_hex_rounds", 0) > 0:
                    f.curse_hex_rounds -= 1

                # ── Wolfshead: skirmisher_retreat ──
                # Scout flees when clearly losing (opponent at ≥70% HP, self ≤50% HP)
                for opponent in [fighter_a, fighter_b]:
                    if (opponent != f
                            and "skirmisher_retreat" in f.traits
                            and not f.is_down
                            and not f.has_condition(ConditionType.FLEEING)):
                        self_losing = (
                            f.hp <= f.max_hp * 0.5
                            and opponent.hp >= opponent.max_hp * 0.7
                        )
                        if self_losing:
                            f.add_condition(ConditionType.FLEEING, random.randint(1, 2))
                            actions.append({
                                "type": "skirmisher_retreat",
                                "fighter": f.name,
                                "effect": "retreating (outmatched)",
                            })

                # ── Batch 8: Warmth_drain per-round tick ──
                # Check opponent for warmth_drain trait; if GRAPPLED or adjacent: d4 cold damage + -1 WIL
                for opponent in [fighter_a, fighter_b]:
                    if opponent != f and "warmth_drain" in opponent.traits and not opponent.is_down:
                        is_adjacent_or_grappled = (
                            (opponent.has_condition(ConditionType.GRAPPLED)
                             and f.has_condition(ConditionType.GRAPPLED))
                            or opponent.current_distance == 1
                        )
                        if is_adjacent_or_grappled:
                            warmth_dmg = random.randint(1, 4)
                            f.hp -= warmth_dmg
                            f.wil_penalty -= 1
                            bleed_log[f.name] = bleed_log.get(f.name, 0) + warmth_dmg
                            actions.append({
                                "type": "warmth_drain",
                                "attacker": opponent.name,
                                "target": f.name,
                                "damage": warmth_dmg,
                                "wil_penalty": -1,
                            })

                # ── Batch 8: Courage_sap per-round tick ──
                # Check opponent for courage_sap trait; if GRAPPLED or melee range: WIL check (50%)
                for opponent in [fighter_a, fighter_b]:
                    if opponent != f and "courage_sap" in opponent.traits and not opponent.is_down:
                        is_adjacent_or_grappled = (
                            (opponent.has_condition(ConditionType.GRAPPLED)
                             and f.has_condition(ConditionType.GRAPPLED))
                            or opponent.current_distance == 1
                        )
                        if is_adjacent_or_grappled:
                            wil_check = resolve_check(
                                f.wil, 0, getattr(f, "prebattle_wil_penalty", 0),
                                f"{f.name} courage_sap WIL (50%)"
                            )
                            if wil_check.result.value in ("failure", "critical_failure"):
                                f.add_condition(ConditionType.FLEEING, random.randint(1, 4))
                                actions.append({
                                    "type": "courage_sap",
                                    "attacker": opponent.name,
                                    "target": f.name,
                                    "wil_check": wil_check.result.value,
                                    "fleeing_rounds": getattr(
                                        f.conditions.get(ConditionType.FLEEING), "rounds", 0
                                    ),
                                })

        # Grapple trait ticks (maul bite / crushing weight)
        for attacker, defender in ((fighter_a, fighter_b), (fighter_b, fighter_a)):
            if attacker.is_down or defender.is_down:
                continue
            if not (attacker.has_condition(ConditionType.GRAPPLED)
                    and defender.has_condition(ConditionType.GRAPPLED)):
                continue

            if "crushing_weight" in attacker.traits:
                crush_dmg = 4
                w = defender.apply_wound("torso", crush_dmg)
                bleed_log[defender.name] = bleed_log.get(defender.name, 0) + crush_dmg
                actions.append({
                    "attacker": attacker.name,
                    "defender": defender.name,
                    "maneuver": "crushing_weight_tick",
                    "hit": True,
                    "final_damage": crush_dmg,
                    "wound_severity": w.severity,
                })

            if "maul_bite" in attacker.traits and attacker.has_condition(ConditionType.MAUL_ACTIVE):
                bite_dmg = max(1, attacker.weapon_base - defender.get_armor_at("torso"))
                tou = resolve_check(defender.tou, 0, 0, f"{defender.name} maul TOU")
                if tou.result in (ResultLevel.SUCCESS, ResultLevel.CRITICAL_SUCCESS):
                    bite_dmg = max(1, bite_dmg // 2)
                w = defender.apply_wound("torso", bite_dmg)
                bleed_log[defender.name] = bleed_log.get(defender.name, 0) + bite_dmg
                actions.append({
                    "attacker": attacker.name,
                    "defender": defender.name,
                    "maneuver": "maul_bite_tick",
                    "hit": True,
                    "final_damage": bite_dmg,
                    "wound_severity": w.severity,
                })

        # Submission yield check (§4.4 B11/B5) — any fighter at ≤25% HP in pin/choke
        for subject, grappler in ((fighter_a, fighter_b), (fighter_b, fighter_a)):
            if subject.is_down or grappler.is_down:
                continue
            gs = getattr(subject, "grapple_state", None)
            if gs is None:
                continue
            check_submission_yield(grappler, subject, gs, actions)

        _dispatch_new_deaths(actions)

        # Track whether each fighter guarded this round (for spear_set weakness)
        fighter_a.guarded_last_round = (man_a == Maneuver.GUARD)
        fighter_b.guarded_last_round = (man_b == Maneuver.GUARD)

        round_dict = asdict(RoundResult(
            round_num=rnd,
            initiative_order=[f.name for f in order],
            stances={
                fighter_a.name: fighter_a.stance.value,
                fighter_b.name: fighter_b.stance.value,
            },
            actions=actions,
            bleeding=bleed_log,
            state={f.name: f.to_dict() for f in [fighter_a, fighter_b]},
        ))
        round_dict["distance_band"] = current_distance
        rounds.append(round_dict)

    # ── Winner ──
    if fighter_a.is_down and fighter_b.is_down:
        winner = "mutual_kill"
    elif fighter_a.is_down:
        winner = fighter_b.name
    elif fighter_b.is_down:
        winner = fighter_a.name
    else:
        winner = "stalemate"

    return {
        "type": "duel",
        "combat_mode": "normal",
        "rounds": len(rounds),
        "winner": winner,
        "combatants": {
            fighter_a.name: fighter_a.to_dict(),
            fighter_b.name: fighter_b.to_dict(),
        },
        "pre_battle": pre_battle,
        "round_log": rounds,
    }

def run_skirmish(
    side_a: list[Fighter],
    side_b: list[Fighter],
    max_rounds: int = 30,
    combat_mode: str = "auto",
    horses_allowed: bool = False,
) -> dict:
    """Run a group skirmish with HEMA depth."""
    import random as _random
    rounds = []
    all_fighters = side_a + side_b
    total_combatants = len(all_fighters)
    if combat_mode not in {"auto", "normal", "skirmish"}:
        combat_mode = "auto"
    if combat_mode == "auto":
        resolved_mode = "skirmish" if total_combatants > 10 else "normal"
    else:
        resolved_mode = combat_mode

    death_effects_fired = set()
    previous_round_attackers: dict[str, list[str]] = {}

    def _dispatch_new_deaths(action_log: list) -> None:
        for dead in all_fighters:
            if dead.is_down and dead.name not in death_effects_fired:
                side = side_a if dead in side_a else side_b
                dispatch_death_effects(dead, all_fighters, side, action_log)
                death_effects_fired.add(dead.name)

    for f in all_fighters:
        f.charged_this_fight = False
        if f.formation not in {"shield_wall", "loose_line", "wedge", "broken"}:
            f.formation = "shield_wall" if f.weapon_type in {"spear", "axe_shield", "shield"} else "loose_line"
        f.cohesion_score = _clamp_i(int(getattr(f, "cohesion_score", 70)))
        f.frontage_pressure = _clamp_i(int(getattr(f, "frontage_pressure", 0)))
        f.morale_score = _clamp_i(int(getattr(f, "morale_score", 70)))
        if getattr(f, "rout_state", "steady") not in {"steady", "wavering", "rout"}:
            f.rout_state = "steady"
        if getattr(f, "mount_condition", "steady") not in {"steady", "panicked", "wounded"}:
            f.mount_condition = "steady"
        if f.mounted or getattr(f, "mount_max_hp", 0):
            mount = _mount_proxy(f)
            _sync_mount_proxy(f, mount)
        f.rider_stability = _clamp_i(int(getattr(f, "rider_stability", 70)))
        f.mount_fatigue = _clamp_i(int(getattr(f, "mount_fatigue", 0)))
        f.charge_cooldown = max(0, int(getattr(f, "charge_cooldown", 0)))
        f.dismount_vulnerability_rounds = max(0, int(getattr(f, "dismount_vulnerability_rounds", 0)))
        f.mounted_pursuit_chain = max(0, int(getattr(f, "mounted_pursuit_chain", 0)))
        if not horses_allowed:
            f.mounted = False
            f.mount_condition = "steady"
            f.rider_stability = _clamp_i(int(getattr(f, "rider_stability", 70)))
            f.mount_fatigue = 0
            f.charge_cooldown = 0
            f.dismount_vulnerability_rounds = 0
            f.mounted_pursuit_chain = 0
        dog_profile = dog_support_profile(getattr(f, "dog_companions", []))
        f.awareness = min(5, int(getattr(f, "awareness", 2)) + dog_profile["awareness"])
        f.morale_score = _clamp_i(int(getattr(f, "morale_score", 70)) + dog_profile["morale"])

    # Veteran eye: pre-select lowest-HP enemy target
    for f in all_fighters:
        if "veteran_eye" not in f.traits:
            continue
        enemies = [e for e in (side_b if f in side_a else side_a) if not e.is_down]
        if enemies:
            f.veteran_target = min(enemies, key=lambda e: e.hp).name

    # ── Darkness / surprise setup (PROPOSAL_005) ──
    for f in all_fighters:
        if "darkness" in f.ambient and not f.has_condition(ConditionType.BLINDED):
            f.add_condition(ConditionType.BLINDED, 9999)
        if not f.aware:
            f.add_condition(ConditionType.UNAWARE, 1)

    # ── Auto-crowd upgrade (PROPOSAL_004) ──
    # When 5+ fighters share the same space, treat it as "crowd" terrain unless
    # they are already in a more restrictive environment.
    _SPACE_ORDER = {"free": 0, "moderate": 1, "packed": 2, "tight": 3, "very_tight": 4}
    if len(all_fighters) >= 5:
        for f in all_fighters:
            if _SPACE_ORDER.get(get_space_class(f.terrain_context), 0) == 0:
                f.terrain_context = "crowd"

    for rnd in range(1, max_rounds + 1):
        a_standing = [f for f in side_a if not f.is_down]
        b_standing = [f for f in side_b if not f.is_down]
        if not a_standing or not b_standing:
            break

        actions = []

        # ── Prompt 8: pre-melee missile exchange ──
        _resolve_missile_phase(a_standing, b_standing, actions, rnd)
        _resolve_missile_phase(b_standing, a_standing, actions, rnd)
        _dispatch_new_deaths(actions)

        # ── Phase 1: Stance + maneuver selection ──
        maneuvers = {}
        for f in a_standing + b_standing:
            if f in side_a:
                f.allies_in_fight = max(0, len(a_standing) - 1)
            else:
                f.allies_in_fight = max(0, len(b_standing) - 1)
            opp = _random.choice(b_standing if f in side_a else a_standing)
            f.stance = choose_stance(f, opp)
            maneuvers[f.name] = choose_maneuver(f, opp)
            if f.rout_state == "wavering" and f.stance == Stance.AGGRESSIVE:
                # Wavering fighters struggle to maintain committed pressure.
                f.stance = Stance.BALANCED

        # ── Phase 2: Initiative ──
        order = resolve_initiative(a_standing + b_standing)
        order.sort(key=lambda f: (1 if f.has_condition(ConditionType.UNAWARE) else 0,))

        # ── Phase 2b: Commander orders ──
        # Each commander on each side may direct allies toward a priority target.
        # Returns {fighter_name: target_name}; empty dict if no commanders active.
        active_orders: dict[str, str] = {}
        active_orders.update(commander_issue_orders(a_standing, b_standing, rnd))
        active_orders.update(commander_issue_orders(b_standing, a_standing, rnd))

        # ── Phase 3: Actions ──
        acted = set()

        # Seed ally_assignments from previous-round target stickiness so the
        # scoring layer knows how many allies are already planning to hit each enemy.
        ally_assignments: dict[str, int] = {}
        for f in a_standing + b_standing:
            if f.current_target_name:
                enemy_side = side_b if f in side_a else side_a
                if any(e.name == f.current_target_name and not e.is_down
                       for e in enemy_side):
                    key = f.current_target_name
                    ally_assignments[key] = ally_assignments.get(key, 0) + 1

        local_noise = max(0, len(a_standing) + len(b_standing) - 6)
        new_round_attackers: dict[str, list[str]] = {}

        for actor in order:
            if actor.is_down or actor.name in acted:
                continue

            # Prompt 5: routed fighters prioritize survival over engagement.
            if actor.rout_state == "rout":
                same_side = side_a if actor in side_a else side_b
                enemy_side = side_b if actor in side_a else side_a
                commander_up = _has_active_commander(same_side)
                organized_withdrawal = commander_up and random.random() < 0.45
                actions.append({
                    "type": "rout_action",
                    "fighter": actor.name,
                    "mode": "organized_withdrawal" if organized_withdrawal else "panic_flee",
                })
                if not organized_withdrawal:
                    actor.cohesion_score = _clamp_i(actor.cohesion_score - 4)
                    actor.morale_score = _clamp_i(actor.morale_score - 3)
                # Rearguard checks: steady allies can screen a fleeing unit.
                rear_guard = [
                    a for a in same_side
                    if not a.is_down and a.name != actor.name and a.rout_state == "steady"
                ]
                if rear_guard and random.random() < 0.30:
                    actions.append({
                        "type": "rearguard_cover",
                        "fighter": random.choice(rear_guard).name,
                        "protected": actor.name,
                    })
                acted.add(actor.name)
                continue

            enemies = [f for f in (side_b if actor in side_a else side_a)
                       if not f.is_down]
            if not enemies:
                continue
            if resolved_mode == "skirmish":
                incoming = previous_round_attackers.get(actor.name, [])
                target, pmeta = choose_skirmish_target_perception(
                    actor,
                    enemies,
                    ally_assignments,
                    active_orders,
                    rnd,
                    incoming_threats=incoming,
                    local_noise=local_noise,
                )
                actions.append({
                    "type": "awareness_update",
                    "fighter": actor.name,
                    "focused": pmeta.get("focused", []),
                    "noticed": pmeta.get("noticed", []),
                    "glimpsed": pmeta.get("glimpsed", []),
                    "unseen_threat_count": pmeta.get("unseen_count", 0),
                    "attention_budget": pmeta.get("budget", 1),
                })
                if pmeta.get("order_state") and pmeta.get("order_state") != "none":
                    actions.append({
                        "type": "order_friction",
                        "fighter": actor.name,
                        "state": pmeta.get("order_state"),
                        "ordered_target": active_orders.get(actor.name, ""),
                    })
            else:
                target = choose_skirmish_target(
                    actor, enemies, ally_assignments, active_orders, rnd
                )
            # Register the chosen assignment so subsequent actors account for it
            ally_assignments[target.name] = ally_assignments.get(target.name, 0) + 1
            # Update stickiness state
            if actor.current_target_name == target.name:
                actor.turns_on_target += 1
            else:
                actor.current_target_name = target.name
                actor.turns_on_target = 1

            actor_man = maneuvers.get(actor.name, Maneuver.CUT)
            target_man = maneuvers.get(target.name, Maneuver.CUT)

            # Prompt 4: directional lethality only in skirmish mode.
            directional = {
                "vector": "front",
                "attack_mod": 0,
                "defense_mod": 0,
                "surprise": False,
                "severity_shift": 0,
            }
            if resolved_mode == "skirmish":
                pressure = ally_assignments.get(target.name, 1)
                directional = compute_directional_engagement(actor, target, pressure)
                actor.action_attack_mod += directional.get("attack_mod", 0)
                target.action_defense_mod += directional.get("defense_mod", 0)

            # Prompt 9: mounted charge and anti-cavalry counters.
            if resolved_mode == "skirmish":
                same_side_count = len(a_standing) if actor in side_a else len(b_standing)
                enemy_count = len(b_standing) if actor in side_a else len(a_standing)
                charge_state = _resolve_mounted_charge(
                    actor,
                    target,
                    target_man,
                    allied_count=same_side_count,
                    enemy_count=enemy_count,
                    actions=actions,
                    round_num=rnd,
                    horses_allowed=horses_allowed,
                )
                actor.action_attack_mod += charge_state.get("attack_mod", 0)
                target.action_defense_mod += charge_state.get("target_def_mod", 0)
            else:
                charge_state = {"charged": False, "bonus_damage": 0}

            # Post-dismount exposure window makes immediate follow-up attacks more dangerous.
            if target.dismount_vulnerability_rounds > 0:
                actor.action_attack_mod += 8

            if resolved_mode == "skirmish":
                dog_profile = dog_support_profile(getattr(actor, "dog_companions", []))
                if dog_profile["attack_mod"] or dog_profile["target_def_mod"]:
                    actor.action_attack_mod += dog_profile["attack_mod"]
                    target.action_defense_mod += dog_profile["target_def_mod"]
                    actions.append({
                        "type": "dog_support",
                        "fighter": actor.name,
                        "target": target.name,
                        "attack_mod": dog_profile["attack_mod"],
                        "target_def_mod": dog_profile["target_def_mod"],
                    })

            # ── Trauma condition check ──
            if getattr(actor, "trauma_conditions", []):
                tc = check_trauma_conditions(actor, target, {"round": rnd})
                if tc.get("effects"):
                    actions.append(tc)
                if tc.get("skip_round"):
                    acted.add(actor.name)
                    continue

            action = resolve_fighter_action(actor, target, actor_man, target_man)
            # Clear transient action modifiers immediately after resolution.
            actor.action_attack_mod = 0
            target.action_defense_mod = 0

            if resolved_mode == "skirmish":
                action["attack_vector"] = directional.get("vector", "front")
                action["surprise_contact"] = bool(directional.get("surprise", False))
                if action.get("hit") and directional.get("surprise", False):
                    target.add_condition(ConditionType.STAGGERED, 1)
                    action.setdefault("condition_applied", "staggered")

            if charge_state.get("charged"):
                action["mounted_charge"] = True

            if action.get("hit") and charge_state.get("bonus_damage", 0) > 0 and not target.is_down:
                charge_bonus = int(charge_state["bonus_damage"])
                w = target.apply_wound("torso", charge_bonus)
                action["charge_bonus_damage"] = charge_bonus
                action["charge_bonus_wound_severity"] = w.severity
                actions.append({
                    "type": "mount_charge_impact",
                    "attacker": actor.name,
                    "defender": target.name,
                    "bonus_damage": charge_bonus,
                    "wound_severity": w.severity,
                    "defender_down": target.is_down,
                })
                if target.is_down:
                    _dispatch_new_deaths(actions)

            actions.append(action)
            acted.add(actor.name)

            if action.get("hit") and getattr(target, "dog_companions", []):
                live_dogs = [dog for dog in target.dog_companions if dog.get("health_status") not in {"dead", "laid_up"}]
                if live_dogs and random.random() < 0.18:
                    dog = live_dogs[0]
                    ensure_animal_health(dog, "dog")
                    wound = apply_animal_wound(
                        dog,
                        damage=max(1, int(action.get("damage", 1) // 2)),
                        location="torso",
                        cause=f"melee around {target.name}",
                    )
                    actions.append(
                        {
                            "type": "dog_wound",
                            "dog": dog.get("name"),
                            "handler": target.name,
                            "severity": wound["severity"],
                            "hp": dog.get("hp"),
                        }
                    )

            # Prompt 5: pursuit phase on routed defenders (with overextension risk).
            if (
                action.get("hit")
                and not target.is_down
                and target.rout_state == "rout"
                and actor.rout_state != "rout"
            ):
                pursue_chance = 0.62 if actor.stance == Stance.AGGRESSIVE else 0.45
                if actor.mounted and not target.mounted:
                    pursue_chance += 0.22
                    pursue_chance += min(0.08, horse_charge_profile(actor).get("pursuit", 0) * 0.02)
                if random.random() < pursue_chance:
                    overextend_risk = 0.18
                    if actor.cohesion_score < 35:
                        overextend_risk += 0.22
                    if actor.frontage_pressure > 60:
                        overextend_risk += 0.18
                    if actor.stance == Stance.AGGRESSIVE:
                        overextend_risk += 0.10
                    if actor.mounted:
                        overextend_risk += min(0.20, actor.mount_fatigue / 500)
                        overextend_risk += 0.05 * max(0, actor.mounted_pursuit_chain - 1)
                    if random.random() < overextend_risk:
                        actor.add_condition(ConditionType.STAGGERED, 1)
                        actor.cohesion_score = _clamp_i(actor.cohesion_score - 8)
                        actor.mounted_pursuit_chain = 0
                        actions.append({
                            "type": "pursuit_event",
                            "fighter": actor.name,
                            "target": target.name,
                            "result": "overextended",
                        })
                    else:
                        bonus = 2
                        if actor.mounted and not target.mounted:
                            bonus += 2
                            actor.mount_fatigue = _clamp_i(actor.mount_fatigue + 8)
                            actor.mounted_pursuit_chain += 1
                        else:
                            actor.mounted_pursuit_chain = 0
                        w = target.apply_wound("torso", bonus)
                        actions.append({
                            "type": "pursuit_event",
                            "fighter": actor.name,
                            "target": target.name,
                            "result": "clean_pursuit",
                            "bonus_damage": bonus,
                            "wound_severity": w.severity,
                        })
                        if target.is_down:
                            _dispatch_new_deaths(actions)
                else:
                    actor.mounted_pursuit_chain = 0
                    actions.append({
                        "type": "pursuit_event",
                        "fighter": actor.name,
                        "target": target.name,
                        "result": "held_line",
                    })

            if action.get("defender") and action.get("attacker"):
                tgt_name = action.get("defender")
                att_name = action.get("attacker")
                new_round_attackers.setdefault(tgt_name, []).append(att_name)

            _dispatch_new_deaths(actions)

            # Friendly fire: large weapons that miss in packed terrain
            # can clip allies (PROPOSAL_004)
            if (action.get("winner") == "defender"
                    and get_space_class(actor.terrain_context) == "packed"
                    and actor.weapon_size >= 3):
                ff_chance = (actor.weapon_size - 2) * 10
                allies = [f for f in (side_a if actor in side_a else side_b)
                          if not f.is_down and f is not actor]
                if allies and _random.randint(1, 100) <= ff_chance:
                    ff_tgt = _random.choice(allies)
                    ff_loc, ff_loc_mult = hit_location()
                    ff_armor = ff_tgt.get_armor_at(ff_loc)
                    ff_dmg = calculate_damage(actor.weapon_base, actor.mig, ff_loc_mult, ff_armor)
                    ff_wnd = ff_tgt.apply_wound(ff_loc, ff_dmg)
                    actions.append({
                        "attacker":         actor.name,
                        "defender":         ff_tgt.name,
                        "maneuver":         "cut",
                        "action":           "friendly_fire",
                        "hit":              True,
                        "location":         ff_loc,
                        "final_damage":     ff_dmg,
                        "wound_severity":   ff_wnd.severity,
                        "is_friendly_fire": True,
                        "stance":           actor.stance.value,
                    })
                    _dispatch_new_deaths(actions)

            # Counter check — UNAWARE fighters cannot counter
            if (action.get("winner") == "defender"
                    and not target.is_down
                    and target.name not in acted
                    and not target.has_condition(ConditionType.UNAWARE)
                    and action.get("maneuver") in (
                        "cut", "thrust", "heavy_blow",
                        "half_sword", "mordschlag")
                    and can_counter(target)):
                counter = resolve_counter(target, actor)
                actions.append(counter)
                acted.add(target.name)
                _dispatch_new_deaths(actions)

        # ── Phase 4: End-of-round ──
        bleed_log = {}
        for f in all_fighters:
            if not f.is_down:
                rec = compute_stamina_recovery(f.tou)
                if f.has_condition(ConditionType.HAMSTRUNG):
                    rec = max(0, rec // 2)
                if getattr(f, "pain_fury_rounds", 0) > 0:
                    rec = max(0, rec - 1)
                    f.pain_fury_rounds = max(0, f.pain_fury_rounds - 1)
                if getattr(f, "suppression_rounds", 0) > 0:
                    f.suppression_rounds = max(0, f.suppression_rounds - 1)
                    if f.suppression_rounds == 0:
                        f.remove_condition(ConditionType.SUPPRESSED)
                if getattr(f, "charge_cooldown", 0) > 0:
                    f.charge_cooldown = max(0, f.charge_cooldown - 1)
                if getattr(f, "dismount_vulnerability_rounds", 0) > 0:
                    f.dismount_vulnerability_rounds = max(0, f.dismount_vulnerability_rounds - 1)
                if getattr(f, "mount_fatigue", 0) > 0:
                    f.mount_fatigue = max(
                        0,
                        f.mount_fatigue - 3 - int(horse_charge_profile(f).get("recovery", 0)),
                    )
                    if f.mount_fatigue >= 70 and f.mount_condition == "steady":
                        f.mount_condition = "wounded"
                if f.mount_condition == "panicked" and random.random() < 0.25:
                    f.mount_condition = "wounded" if f.mount_fatigue > 50 else "steady"
                # mig_bonus_timer: blackwine_rage expires after timer reaches 0
                if getattr(f, "mig_bonus_timer", 0) > 0:
                    f.mig_bonus_timer -= 1
                    if f.mig_bonus_timer == 0:
                        f.mig_bonus = max(0, f.mig_bonus - 2)
                # reality_warping: decrement per round
                if getattr(f, "reality_warping_rounds", 0) > 0:
                    f.reality_warping_rounds = max(0, f.reality_warping_rounds - 1)
                # tactical_withdrawal_active: clear after one round
                if getattr(f, "tactical_withdrawal_active", False):
                    f.tactical_withdrawal_active = False
                # pre-battle temporary penalties (if present in custom skirmish setup)
                if getattr(f, "prebattle_attack_penalty_rounds", 0) > 0:
                    f.prebattle_attack_penalty_rounds -= 1
                    if f.prebattle_attack_penalty_rounds == 0:
                        f.prebattle_attack_penalty = 0
                if getattr(f, "prebattle_nim_penalty_rounds", 0) > 0:
                    f.prebattle_nim_penalty_rounds -= 1
                    if f.prebattle_nim_penalty_rounds == 0:
                        f.prebattle_nim_penalty = 0
                if getattr(f, "prebattle_wit_penalty_rounds", 0) > 0:
                    f.prebattle_wit_penalty_rounds -= 1
                    if f.prebattle_wit_penalty_rounds == 0:
                        f.prebattle_wit_penalty = 0
                f.recover_stamina(rec)
                f.tick_conditions()
                bl = f.apply_bleeding()
                if bl > 0:
                    bleed_log[f.name] = bleed_log.get(f.name, 0) + bl
                # Choke asphyxiation (PROPOSAL_002)
                if f.has_condition(ConditionType.CHOKED) and not f.is_undead:
                    f.hp -= 4
                    bleed_log[f.name] = bleed_log.get(f.name, 0) + 4
                    if f.hp <= 0:
                        f.is_down = True
                    # Choke round tick — unconsciousness at round 4+ (§4.4 B5)
                    gs = getattr(f, "grapple_state", None)
                    if gs is not None and not f.is_down:
                        advance_choke_round(gs, f, actions)

        # Submission yield check (§4.4 B11/B5) — any fighter at ≤25% HP in pin/choke
        for subject in all_fighters:
            if subject.is_down:
                continue
            gs = getattr(subject, "grapple_state", None)
            if gs is None:
                continue
            # Find the grappler (the other fighter holding the grapple_state)
            for grappler in all_fighters:
                if grappler is not subject and not grappler.is_down:
                    if getattr(grappler, "grapple_state", None) is gs:
                        check_submission_yield(grappler, subject, gs, actions)
                        break

        # Grapple trait ticks in skirmish
        for attacker in [f for f in all_fighters if not f.is_down]:
            if not attacker.has_condition(ConditionType.GRAPPLED):
                continue
            enemies = side_b if attacker in side_a else side_a
            candidates = [e for e in enemies if not e.is_down and e.has_condition(ConditionType.GRAPPLED)]
            if not candidates:
                continue
            defender = _random.choice(candidates)

            if "crushing_weight" in attacker.traits:
                crush_dmg = 4
                w = defender.apply_wound("torso", crush_dmg)
                bleed_log[defender.name] = bleed_log.get(defender.name, 0) + crush_dmg
                actions.append({
                    "attacker": attacker.name,
                    "defender": defender.name,
                    "maneuver": "crushing_weight_tick",
                    "hit": True,
                    "final_damage": crush_dmg,
                    "wound_severity": w.severity,
                })

            if "maul_bite" in attacker.traits and attacker.has_condition(ConditionType.MAUL_ACTIVE):
                bite_dmg = max(1, attacker.weapon_base - defender.get_armor_at("torso"))
                tou = resolve_check(defender.tou, 0, 0, f"{defender.name} maul TOU")
                if tou.result in (ResultLevel.SUCCESS, ResultLevel.CRITICAL_SUCCESS):
                    bite_dmg = max(1, bite_dmg // 2)
                w = defender.apply_wound("torso", bite_dmg)
                bleed_log[defender.name] = bleed_log.get(defender.name, 0) + bite_dmg
                actions.append({
                    "attacker": attacker.name,
                    "defender": defender.name,
                    "maneuver": "maul_bite_tick",
                    "hit": True,
                    "final_damage": bite_dmg,
                    "wound_severity": w.severity,
                })

        _dispatch_new_deaths(actions)

        # Prompt 5: formation pressure + morale contagion + break cascade.
        _update_formation_and_morale(
            side_a,
            side_b,
            incoming_attackers=new_round_attackers,
            actions=actions,
            round_num=rnd,
        )
        _update_formation_and_morale(
            side_b,
            side_a,
            incoming_attackers=new_round_attackers,
            actions=actions,
            round_num=rnd,
        )

        # Guard memory for next round (spear_set weakness support)
        for f in a_standing + b_standing:
            f.guarded_last_round = (maneuvers.get(f.name) == Maneuver.GUARD)

        # rally_allies: one allied fighter per rally-er recovers 3 stamina
        for f in all_fighters:
            if "rally_allies" in f.traits and not f.is_down:
                same_side = [x for x in (side_a if f in side_a else side_b)
                             if x.name != f.name and not x.is_down]
                if same_side:
                    weakest = min(same_side, key=lambda a: a.stamina)
                    weakest.recover_stamina(3)

        stances_snap = {f.name: f.stance.value for f in all_fighters if not f.is_down}
        round_result = RoundResult(
            round_num=rnd,
            initiative_order=[f.name for f in order],
            stances=stances_snap,
            actions=actions,
            bleeding=bleed_log,
            state={f.name: f.to_dict() for f in all_fighters},
        )
        rounds.append(asdict(round_result))
        previous_round_attackers = new_round_attackers

    # ── Winner ──
    a_standing = [f for f in side_a if not f.is_down]
    b_standing = [f for f in side_b if not f.is_down]

    if not a_standing and not b_standing:
        winner = "mutual_destruction"
    elif not b_standing:
        winner = "side_a"
    elif not a_standing:
        winner = "side_b"
    else:
        winner = "stalemate"

    return {
        "type": "skirmish",
        "combat_mode": resolved_mode,
        "horses_allowed": bool(horses_allowed),
        "rounds": len(rounds),
        "winner": winner,
        "side_a": {f.name: f.to_dict() for f in side_a},
        "side_b": {f.name: f.to_dict() for f in side_b},
        "round_log": rounds,
    }

# I/O helpers
# ───────────────────────────────────────────────────────────────────────

def load_fighter(source: str) -> Fighter:
    """Load a fighter from a JSON string or file path."""
    try:
        data = json.loads(source)
    except json.JSONDecodeError:
        with open(source, 'r', encoding='utf-8') as f:
            data = json.load(f)
    return Fighter.from_dict(data)


def _print_narrative_duel(a, b, result):
    """Print narrative output for a duel."""
    print(f"=== DUEL: {a.name} vs {b.name} ===\n")

    # Pre-battle events
    for event in result.get("pre_battle", []):
        line = render_pre_battle(event)
        if line:
            print(line)
    if result.get("pre_battle"):
        print()

    was_bloodied: dict[str, bool] = {a.name: False, b.name: False}

    for rnd in result["round_log"]:
        print(f"--- Round {rnd['round_num']} ---")

        # Stance summary
        stances = rnd.get("stances", {})
        parts = []
        for name, st in stances.items():
            desc = STANCE_DESC.get(Stance(st), st)
            parts.append(f"{name} {desc}")
        if parts:
            print(f"  [{', '.join(parts)}]")

        state_map = rnd.get("state", {})

        # Actions
        for act in rnd["actions"]:
            line = render_action(act, state_map, was_bloodied)
            if line:
                print(line)
            if act.get("downgraded"):
                print("       (exhausted — maneuver downgraded)")

        # Bleeding
        for name, bl in rnd.get("bleeding", {}).items():
            print(render_bleeding(name, bl))

        # Bloodied transitions — suppress for fighters who died in the same hit
        for name, s in state_map.items():
            now_bloodied = bool(s.get("bloodied_triggered", False))
            if (now_bloodied
                    and not was_bloodied.get(name, False)
                    and not s.get("is_down", False)):
                is_undead = bool(s.get("is_undead", False))
                print(render_bloodied(name, is_undead))
            was_bloodied[name] = now_bloodied

        # Status line
        print(render_status_line(state_map))
        print()

    print(f"Winner: {result['winner']}")
    for name, state in result["combatants"].items():
        conds = [c["type"] for c in state.get("conditions", [])]
        cstr = f" [{','.join(conds)}]" if conds else ""
        display_hp = max(0, state['hp'])
        print(f"  {name}: {display_hp}/{state['max_hp']} HP, "
              f"stamina {state.get('stamina', '?')}/{state.get('max_stamina', '?')}, "
              f"wounds: {len(state['wounds'])}{cstr}")


def _print_narrative_skirmish(side_a, side_b, result):
    """Print narrative output for a skirmish."""
    print(f"=== SKIRMISH: {len(side_a)} vs {len(side_b)} ===\n")
    print(f"[MODE] {result.get('combat_mode', 'normal')}\n")
    a_names = {f.name for f in side_a}
    b_names = {f.name for f in side_b}

    for rnd in result["round_log"]:
        print(f"--- Round {rnd['round_num']} ---")
        state_map = rnd.get("state", {})

        for act in rnd["actions"]:
            line = render_action(act, state_map)
            if line:
                print(line)

        for name, bl in rnd.get("bleeding", {}).items():
            print(render_bleeding(name, bl))

        summary = render_round_summary(rnd, a_names, b_names)
        if summary:
            print(summary)

    print(f"\nWinner: {result['winner']}")


# ───────────────────────────────────────────────────────────────────────
# CLI
# ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Iron Ledger Combat Simulator (HEMA)")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # --- duel ---
    duel_p = subparsers.add_parser("duel", help="1v1 combat")
    duel_p.add_argument("--attacker", type=str, help="Attacker JSON string")
    duel_p.add_argument("--defender", type=str, help="Defender JSON string")
    duel_p.add_argument("--attacker-file", type=str, help="Attacker JSON file")
    duel_p.add_argument("--defender-file", type=str, help="Defender JSON file")
    duel_p.add_argument("--max-rounds", type=int, default=30)
    duel_p.add_argument("--json", action="store_true", help="Full JSON output")
    duel_p.add_argument("--summary", action="store_true", help="Summary only")
    duel_p.add_argument("--psych-profile", type=str, default=None,
                        help="YAML file mapping fighter name → list of trauma conditions")

    # --- skirmish ---
    sk_p = subparsers.add_parser("skirmish", help="Group combat")
    sk_p.add_argument("--side-a", type=str, required=True)
    sk_p.add_argument("--side-b", type=str, required=True)
    sk_p.add_argument("--max-rounds", type=int, default=30)
    sk_p.add_argument("--json", action="store_true")
    sk_p.add_argument("--summary", action="store_true")
    sk_p.add_argument(
        "--combat-mode",
        type=str,
        choices=["auto", "normal", "skirmish"],
        default="auto",
        help="Skirmish perception model mode (auto=skirmish when total combatants > 10)",
    )
    sk_p.add_argument(
        "--horses-allowed",
        action="store_true",
        help="Enable mounted combat logic for this skirmish (default: disabled).",
    )
    sk_p.add_argument("--psych-profile", type=str, default=None,
                      help="YAML file mapping fighter name → list of trauma conditions")

    args = parser.parse_args()

    if args.command == "duel":
        if args.attacker_file:
            a = load_fighter(args.attacker_file)
        elif args.attacker:
            a = load_fighter(args.attacker)
        else:
            parser.error("Provide --attacker or --attacker-file")

        if args.defender_file:
            b = load_fighter(args.defender_file)
        elif args.defender:
            b = load_fighter(args.defender)
        else:
            parser.error("Provide --defender or --defender-file")

        # Apply psych profile if provided
        if getattr(args, "psych_profile", None):
            if _yaml is None:
                sys.exit("PyYAML not installed; cannot load --psych-profile")
            with open(args.psych_profile) as _f:
                _psych = _yaml.safe_load(_f) or {}
            for _fighter in [a, b]:
                if _fighter.name in _psych:
                    _fighter.trauma_conditions = _psych[_fighter.name]

        result = run_duel(a, b, args.max_rounds)

        if args.json:
            print(json.dumps(result, indent=2))
        elif args.summary:
            print(f"Duel: {a.name} vs {b.name}")
            print(f"Rounds: {result['rounds']}")
            print(f"Winner: {result['winner']}")
            for name, state in result["combatants"].items():
                stam = f"{state.get('stamina', '?')}/{state.get('max_stamina', '?')}"
                print(f"  {name}: {state['hp']}/{state['max_hp']} HP, "
                      f"stamina {stam}, wounds: {len(state['wounds'])}")
        else:
            _print_narrative_duel(a, b, result)

    elif args.command == "skirmish":
        side_a_data = json.loads(args.side_a)
        side_b_data = json.loads(args.side_b)

        side_a = [Fighter.from_dict(d) if isinstance(d, dict) else load_fighter(d)
                  for d in side_a_data]
        side_b = [Fighter.from_dict(d) if isinstance(d, dict) else load_fighter(d)
                  for d in side_b_data]

        # Apply psych profile if provided
        if getattr(args, "psych_profile", None):
            if _yaml is None:
                sys.exit("PyYAML not installed; cannot load --psych-profile")
            with open(args.psych_profile) as _f:
                _psych = _yaml.safe_load(_f) or {}
            for _fighter in side_a + side_b:
                if _fighter.name in _psych:
                    _fighter.trauma_conditions = _psych[_fighter.name]

        result = run_skirmish(
            side_a,
            side_b,
            max_rounds=args.max_rounds,
            combat_mode=args.combat_mode,
            horses_allowed=bool(getattr(args, "horses_allowed", False)),
        )

        if args.json:
            print(json.dumps(result, indent=2))
        elif args.summary:
            print(f"Skirmish: {len(side_a)} vs {len(side_b)}")
            print(f"Rounds: {result['rounds']}")
            print(f"Winner: {result['winner']}")
            a_alive = sum(1 for s in result["side_a"].values() if not s["is_down"])
            b_alive = sum(1 for s in result["side_b"].values() if not s["is_down"])
            print(f"  Side A survivors: {a_alive}/{len(side_a)}")
            print(f"  Side B survivors: {b_alive}/{len(side_b)}")
        else:
            _print_narrative_skirmish(side_a, side_b, result)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
