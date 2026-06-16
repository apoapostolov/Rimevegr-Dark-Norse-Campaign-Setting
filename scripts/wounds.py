#!/usr/bin/env python3
"""
Iron Ledger — Wound Management System

Full wound lifecycle management: apply, treat, heal, infect, worsen,
improve, scar, remove, amputate, and condition assessment.  All rules
from 20_SIMULATION_RULES.md § 5.

Operates on band JSON files produced by band_manager.py, or on
standalone member JSON dicts piped in from combat_sim.py.

Usage:
    python wounds.py apply   --band-file band.json --target "Kell Hook" --location right_arm --sublocation forearm_outer --type hewn --severity serious --damage 9 --weapon bearded_axe --inflicted-by "Bandit Raider"
    python wounds.py treat   --band-file band.json --target "Kell Hook" --wound-id w_001 --treatment field_surgery --healer "Dalla"
    python wounds.py heal    --band-file band.json --target "Kell Hook" --wound-id w_001 --days 7 --rest field_rest
    python wounds.py infect  --band-file band.json --target "Kell Hook" --wound-id w_001 --stage early
    python wounds.py worsen  --band-file band.json --target "Kell Hook" --wound-id w_001 --new-severity critical --cause "Stitches tore"
    python wounds.py improve --band-file band.json --target "Kell Hook" --wound-id w_001 --new-severity light --cause "Rest and comfrey"
    python wounds.py scar    --band-file band.json --target "Kell Hook" --wound-id w_001
    python wounds.py remove  --band-file band.json --target "Kell Hook" --wound-id w_001
    python wounds.py amputate --band-file band.json --target "Ubbe Ironside" --location left_arm --sublocation below_elbow --healer "Dalla"
    python wounds.py status  --band-file band.json --target "Kell Hook"
    python wounds.py roster  --band-file band.json
    python wounds.py describe --band-file band.json --target "Kell Hook" --wound-id w_001
"""

import argparse
import json
import random
import sys
import os
from copy import deepcopy
from dataclasses import dataclass, field, asdict
from typing import Optional

try:
    import yaml as _yaml
except ImportError:
    _yaml = None

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import (
    resolve_check,
    wound_severity as severity_from_damage,
    compute_max_hp,
    roll_d100,
    ResultLevel,
)


# ───────────────────────────────────────────────────────────────────────
# Constants — from 20_SIMULATION_RULES.md § 5
# ───────────────────────────────────────────────────────────────────────

SEVERITY_ORDER = ["none", "scratch", "light", "serious", "critical", "mortal"]

BLEEDING_RATE = {
    "none": 0, "scratch": 0, "light": 0,
    "serious": 1, "critical": 2, "mortal": 3,
}

WOUND_PENALTY = {
    "none": 0, "scratch": 0, "light": -5,
    "serious": -15, "critical": -30, "mortal": -50,
}

SUBLOCATION_TABLE = {
    "head": [
        (1, 15, "scalp"), (16, 25, "temple"), (26, 40, "forehead"),
        (41, 55, "jaw"), (56, 65, "ear"), (66, 75, "eye_socket"),
        (76, 82, "nose"), (83, 90, "cheek"), (91, 100, "throat"),
    ],
    "torso": [
        (1, 20, "chest_front"), (21, 30, "chest_side"),
        (31, 45, "belly_upper"), (46, 55, "belly_lower"),
        (56, 65, "flank"), (66, 75, "back_upper"),
        (76, 85, "back_lower"), (86, 92, "collarbone"),
        (93, 100, "shoulder"),
    ],
    "right_arm": [
        (1, 25, "upper_arm_outer"), (26, 35, "upper_arm_inner"),
        (36, 50, "elbow"), (51, 70, "forearm_outer"),
        (71, 85, "forearm_inner"), (86, 100, "wrist"),
    ],
    "left_arm": [
        (1, 25, "upper_arm_outer"), (26, 35, "upper_arm_inner"),
        (36, 50, "elbow"), (51, 70, "forearm_outer"),
        (71, 85, "forearm_inner"), (86, 100, "wrist"),
    ],
    "hands": [
        (1, 30, "fingers"), (31, 50, "thumb"), (51, 70, "palm"),
        (71, 90, "back_of_hand"), (91, 100, "knuckles"),
    ],
    "legs": [
        (1, 25, "thigh_front"), (26, 35, "thigh_inner"),
        (36, 45, "thigh_outer"), (46, 65, "knee"),
        (66, 80, "shin"), (81, 90, "calf"), (91, 100, "ankle"),
    ],
    "feet": [
        (1, 35, "toes"), (36, 60, "arch"),
        (61, 80, "heel"), (81, 100, "top_of_foot"),
    ],
}

WEAPON_WOUND_TYPE = {
    "hand_axe": "hewn", "bearded_axe": "hewn", "long_axe": "hewn",
    "iron_axe": "hewn", "sword": "hewn", "sword_thrust": "stab",
    "seax": "hewn", "seax_thrust": "stab", "great_sword": "hewn",
    "spear": "stab", "javelin": "stab", "short_bow": "arrow",
    "fist": "crush", "kick": "crush", "shield_bash": "crush",
    "mordschlag": "crush", "grapple": "crush", "mace": "crush",
    "fire": "burn", "cold": "frostbite", "fall": "crush",
}

TREATMENT_TABLE = {
    "first_aid":     {"heal_mod": -10, "infection_reduction": 5,  "speed_mult": 1.0},
    "field_surgery": {"heal_mod": 0,   "infection_reduction": 15, "speed_mult": 0.8},
    "full_surgery":  {"heal_mod": 10,  "infection_reduction": 25, "speed_mult": 0.6},
    "cauterized":    {"heal_mod": 0,   "infection_reduction": 20, "speed_mult": 1.3},
    "amputated":     {"heal_mod": -15, "infection_reduction": 100,"speed_mult": 1.0},
}

SEVERITY_HEAL_MOD = {
    "scratch": 20, "light": 10, "serious": 0, "critical": -15, "mortal": -30,
}

ENVIRONMENT_HEAL_MOD = {
    "dry_hall": 10, "clean_camp": 0, "wet_camp": -10,
    "field": -15, "combat": -25,
}

TOOL_HEAL_MOD = {
    "full_kit": 10, "basic": 0, "improvised": -10, "nothing": -20,
}

REST_QUALITY_MULT = {
    "full_rest": 1.0, "field_rest": 0.5, "active_duty": 0.2,
}

# Healing thresholds in days (by severity) for stage transitions
# Stages: fresh(0) → clotting(1) → closing(2) → knitting(3) → scarring(4) → healed(5)
HEALING_DAYS = {
    "scratch":  [0.0, 0.2, 1.0, 2.0, 0, 0],
    "light":    [0.0, 0.2, 2.0, 5.0, 14.0, 21.0],
    "serious":  [0.0, 0.2, 3.0, 14.0, 45.0, 60.0],
    "critical": [0.0, 0.2, 5.0, 30.0, 90.0, 120.0],
    "mortal":   [0.0, 0.2, 7.0, 60.0, 180.0, 240.0],
}

STAGES = ["fresh", "clotting", "closing", "knitting", "scarring", "healed"]

INFECTION_BASE_CHANCE = {
    "scratch": 5, "light": 10, "serious": 20, "critical": 30, "mortal": 50,
}

INFECTION_STAGES = ["none", "early", "spreading", "deep_rot", "mortification"]

INFECTION_EFFECTS = {
    "early":          {"penalty": -10, "hp_per_day": 0,  "heal_mod": 0},
    "spreading":      {"penalty": -15, "hp_per_day": 1,  "heal_mod": -15},
    "deep_rot":       {"penalty": -30, "hp_per_day": 2,  "heal_mod": -30},
    "mortification":  {"penalty": -50, "hp_per_day": 5,  "heal_mod": -50},
}

AMPUTATION_HP_COST = {
    "hand": 2, "fingers": 2, "thumb": 1, "palm": 2,
    "wrist": 3, "forearm_outer": 4, "forearm_inner": 4,
    "elbow": 5, "upper_arm_outer": 6, "upper_arm_inner": 6,
    "foot": 3, "toes": 2, "arch": 3, "heel": 3, "top_of_foot": 3,
    "ankle": 4, "shin": 5, "calf": 5, "knee": 6,
    "thigh_front": 8, "thigh_inner": 8, "thigh_outer": 8,
    "eye_socket": 1, "ear": 1, "nose": 1,
    "below_elbow": 4, "below_knee": 5, "full_arm": 6, "full_leg": 8,
}

# ── Pain narrative descriptors (§ 5.11 lore extension) ──

PAIN_LEVELS = ["none", "mild", "moderate", "severe", "agonizing", "unconscious"]

PAIN_BY_WOUND_STATE = {
    "fresh_untreated":   2,   # two steps above base
    "fresh_treated":     1,   # one step above base
    "clotting":          0,   # base severity
    "closing":          -1,   # one step below
    "knitting":         -1,
    "scarring":         -2,   # mostly gone
    "healed":           -3,
    "infected_early":    1,   # stacks
    "infected_spreading": 2,
    "infected_deep":     3,
    "cauterized_day1":   4,   # agonizing
    "cauterized_day2":   3,
    "cauterized_day3":   2,
}

PAIN_SEVERITY_BASE = {
    "scratch": 0, "light": 1, "serious": 2,
    "critical": 3, "mortal": 4,
}


# ───────────────────────────────────────────────────────────────────────
# Wound Description Generator
# ───────────────────────────────────────────────────────────────────────

_WOUND_VERBS = {
    "hewn": [
        "laid open", "split", "hacked into", "cut deep across",
        "carved through", "cleaved", "gouged",
    ],
    "stab": [
        "punctured", "pierced", "driven into", "thrust through",
        "skewered", "stabbed into",
    ],
    "arrow": [
        "punched through by an arrowhead", "pinned by a shaft",
        "pierced by a broadhead", "transfixed by an arrow",
    ],
    "crush": [
        "crushed", "caved in", "cracked", "shattered against",
        "pounded into", "smashed", "buckled",
    ],
    "burn": [
        "blackened by flame", "blistered raw", "charred",
        "scorched through to the meat",
    ],
    "frostbite": [
        "gone white and dead from cold", "blackened at the tips by frost",
        "waxy and numb from freezing", "cracked and bleeding from deep cold",
    ],
}

_LOCATION_NAMES = {
    "scalp": "the scalp", "temple": "the temple", "forehead": "the brow",
    "jaw": "the jaw", "ear": "the ear", "eye_socket": "the eye socket",
    "nose": "the nose", "cheek": "the cheek", "throat": "the throat",
    "chest_front": "the chest", "chest_side": "the ribs",
    "belly_upper": "the upper belly", "belly_lower": "the gut",
    "flank": "the flank", "back_upper": "the upper back",
    "back_lower": "the small of the back", "collarbone": "the collarbone",
    "shoulder": "the shoulder",
    "upper_arm_outer": "the outer arm", "upper_arm_inner": "the inner arm",
    "elbow": "the elbow", "forearm_outer": "the forearm",
    "forearm_inner": "the inner forearm", "wrist": "the wrist",
    "fingers": "the fingers", "thumb": "the thumb", "palm": "the palm",
    "back_of_hand": "the back of the hand", "knuckles": "the knuckles",
    "thigh_front": "the thigh", "thigh_inner": "the inner thigh",
    "thigh_outer": "the outer thigh", "knee": "the knee",
    "shin": "the shin", "calf": "the calf", "ankle": "the ankle",
    "toes": "the toes", "arch": "the sole", "heel": "the heel",
    "top_of_foot": "the top of the foot",
}

_SEVERITY_ADJ = {
    "scratch": "shallow", "light": "clean", "serious": "deep",
    "critical": "grievous", "mortal": "ruinous",
}


def generate_wound_description(
    location: str, sublocation: str, wound_type: str,
    severity: str, weapon: str = "",
) -> str:
    """Generate a terse prose description of the wound."""
    verb = random.choice(_WOUND_VERBS.get(wound_type, _WOUND_VERBS["hewn"]))
    loc_name = _LOCATION_NAMES.get(sublocation, sublocation.replace("_", " "))
    adj = _SEVERITY_ADJ.get(severity, "")
    weapon_str = f" by a {weapon.replace('_', ' ')}" if weapon else ""
    return f"A {adj} wound — {loc_name} {verb}{weapon_str}."


# ───────────────────────────────────────────────────────────────────────
# Sublocation Resolution
# ───────────────────────────────────────────────────────────────────────

def determine_sublocation(location: str) -> str:
    """Roll on the sublocation table for a given body location."""
    table = SUBLOCATION_TABLE.get(location)
    if not table:
        return location
    roll = roll_d100()
    for lo, hi, name in table:
        if lo <= roll <= hi:
            return name
    return table[-1][2]


# ───────────────────────────────────────────────────────────────────────
# Wound ID generation
# ───────────────────────────────────────────────────────────────────────

_wound_counter = 0


def generate_wound_id(member: dict) -> str:
    """Generate a unique wound ID for a member."""
    global _wound_counter
    existing = {w.get("id", "") for w in member.get("wounds", [])}
    for i in range(1, 999):
        wid = f"w_{i:03d}"
        if wid not in existing:
            return wid
    _wound_counter += 1
    return f"w_{_wound_counter:03d}"


# ───────────────────────────────────────────────────────────────────────
# Pain Calculation
# ───────────────────────────────────────────────────────────────────────

def compute_pain_level(wound: dict) -> str:
    """Compute the pain level for a single wound based on its state."""
    severity = wound.get("severity", "scratch")
    base = PAIN_SEVERITY_BASE.get(severity, 0)
    stage = wound.get("healing_stage", "fresh")
    treated = wound.get("treated", False)

    # State key
    if stage == "fresh":
        adjustment = PAIN_BY_WOUND_STATE["fresh_treated" if treated else "fresh_untreated"]
    elif stage in PAIN_BY_WOUND_STATE:
        adjustment = PAIN_BY_WOUND_STATE[stage]
    else:
        adjustment = 0

    # Infection stacks
    infection = wound.get("infection_stage", "none")
    if infection == "early":
        adjustment += PAIN_BY_WOUND_STATE["infected_early"]
    elif infection == "spreading":
        adjustment += PAIN_BY_WOUND_STATE["infected_spreading"]
    elif infection in ("deep_rot", "mortification"):
        adjustment += PAIN_BY_WOUND_STATE["infected_deep"]

    idx = max(0, min(len(PAIN_LEVELS) - 1, base + adjustment))
    return PAIN_LEVELS[idx]


def compute_overall_pain(member: dict) -> str:
    """Compute overall pain level across all active wounds."""
    worst = 0
    for w in member.get("wounds", []):
        if w.get("resolved"):
            continue
        level = compute_pain_level(w)
        idx = PAIN_LEVELS.index(level)
        worst = max(worst, idx)
    return PAIN_LEVELS[worst]


# ───────────────────────────────────────────────────────────────────────
# Core Commands
# ───────────────────────────────────────────────────────────────────────

def wound_apply(
    member: dict,
    location: str,
    severity: str,
    damage: int,
    weapon: str = "",
    inflicted_by: str = "",
    sublocation: str = "",
    wound_type: str = "",
    foreign_body: bool = False,
    foreign_body_type: str = "",
    current_day: int = 0,
) -> dict:
    """
    Apply a new wound to a member.  Returns the wound record.
    Mutates member in-place (hp, wounds list, status).
    """
    if not sublocation:
        sublocation = determine_sublocation(location)
    if not wound_type:
        wound_type = WEAPON_WOUND_TYPE.get(weapon, "hewn")

    wid = generate_wound_id(member)
    bleed = BLEEDING_RATE.get(severity, 0)
    description = generate_wound_description(
        location, sublocation, wound_type, severity, weapon,
    )

    wound = {
        "id": wid,
        "location": location,
        "sublocation": sublocation,
        "type": wound_type,
        "severity": severity,
        "damage": damage,
        "bleeding": bleed,
        "description": description,
        "inflicted_day": current_day,
        "inflicted_by": inflicted_by,
        "weapon_used": weapon,
        "treated": False,
        "treated_by": None,
        "treatment_type": None,
        "healing_stage": "fresh",
        "healing_day_count": 0,
        "clean": not foreign_body,
        "infected": False,
        "infection_stage": "none",
        "foreign_body": foreign_body,
        "foreign_body_type": foreign_body_type if foreign_body else "",
        "resolved": False,
        "scar": None,
        "pain_level": None,
    }
    wound["pain_level"] = compute_pain_level(wound)

    if "wounds" not in member:
        member["wounds"] = []
    member["wounds"].append(wound)

    # HP reduction
    hp = member.get("hp", member.get("max_hp", 30))
    member["hp"] = max(0, hp - damage)

    # Status update
    if member["hp"] <= 0 or severity == "mortal":
        member["status"] = "dying"
    elif severity in ("serious", "critical"):
        member["status"] = "wounded"
    elif severity == "light" and member.get("status") == "active":
        member["status"] = "wounded"

    return wound


def wound_treat(
    member: dict,
    wound_id: str,
    treatment_type: str,
    healer_name: str = "",
    healer_wit: int = 5,
    healer_heal_skill: int = 1,
    environment: str = "clean_camp",
    tools: str = "basic",
) -> dict:
    """
    Treat an existing wound.  Resolves a Heal check and updates
    wound state.  Returns result dict.
    """
    wound = _find_wound(member, wound_id)
    if not wound:
        return {"error": f"Wound {wound_id} not found on {member['name']}."}

    treatment = TREATMENT_TABLE.get(treatment_type)
    if not treatment:
        return {"error": f"Unknown treatment type: {treatment_type}"}

    # Heal check
    sev_mod = SEVERITY_HEAL_MOD.get(wound["severity"], 0)
    env_mod = ENVIRONMENT_HEAL_MOD.get(environment, 0)
    tool_mod = TOOL_HEAL_MOD.get(tools, 0)
    total_mod = treatment["heal_mod"] + sev_mod + env_mod + tool_mod

    check = resolve_check(healer_wit, healer_heal_skill, total_mod, "heal")

    result = {
        "wound_id": wound_id,
        "treatment": treatment_type,
        "healer": healer_name,
        "check": check.to_dict(),
    }

    if check.result in (ResultLevel.SUCCESS, ResultLevel.CRITICAL_SUCCESS):
        wound["treated"] = True
        wound["treated_by"] = healer_name
        wound["treatment_type"] = treatment_type
        wound["bleeding"] = 0

        # Foreign body removal on success
        if wound.get("foreign_body") and treatment_type in ("field_surgery", "full_surgery"):
            wound["foreign_body"] = False
            wound["clean"] = True
            result["foreign_body_removed"] = True

        # Advance to clotting if still fresh
        if wound["healing_stage"] == "fresh":
            wound["healing_stage"] = "clotting"

        result["success"] = True
        result["message"] = (
            f"{healer_name or 'The leech'} treats {member['name']}'s "
            f"{wound['sublocation']} wound ({treatment_type}). "
            f"Bleeding stopped.  Healing begins."
        )

        if check.result == ResultLevel.CRITICAL_SUCCESS:
            result["message"] += "  Exceptional work — healing speed improved."

    elif check.result == ResultLevel.CRITICAL_FAILURE:
        # Critical failure — wound worsens
        wound["treated"] = False
        if wound["bleeding"] > 0:
            wound["bleeding"] += 1
        result["success"] = False
        result["critical_failure"] = True
        result["message"] = (
            f"{healer_name or 'The leech'} botches the treatment of "
            f"{member['name']}'s wound. The wound is worse than before."
        )
    else:
        wound["treated"] = False
        # Partial: 50% chance bleeding continues
        if wound["bleeding"] > 0 and random.random() < 0.5:
            result["bleeding_continues"] = True
        else:
            wound["bleeding"] = 0
        result["success"] = False
        result["message"] = (
            f"{healer_name or 'The leech'} treats {member['name']}'s wound, "
            f"but the result is uncertain."
        )

    wound["pain_level"] = compute_pain_level(wound)
    result["pain_level"] = wound["pain_level"]
    return result


def wound_heal(
    member: dict,
    wound_id: str,
    days_elapsed: int,
    rest_quality: str = "full_rest",
    check_complications: bool = True,
) -> dict:
    """
    Advance a wound's healing timeline.  Returns result dict with
    stage transitions, complication checks, and narrative text.
    """
    wound = _find_wound(member, wound_id)
    if not wound:
        return {"error": f"Wound {wound_id} not found on {member['name']}."}
    if wound.get("resolved"):
        return {"wound_id": wound_id, "message": "Wound already healed."}

    rest_mult = REST_QUALITY_MULT.get(rest_quality, 0.5)
    effective_days = days_elapsed * rest_mult
    severity = wound["severity"]
    thresholds = HEALING_DAYS.get(severity, HEALING_DAYS["light"])

    old_stage = wound["healing_stage"]
    old_stage_idx = STAGES.index(old_stage)
    wound["healing_day_count"] = wound.get("healing_day_count", 0) + effective_days

    # Check stage advancement
    new_stage_idx = old_stage_idx
    for i in range(old_stage_idx + 1, len(STAGES)):
        if i < len(thresholds) and wound["healing_day_count"] >= thresholds[i]:
            new_stage_idx = i
        else:
            break

    events = []
    complications = []

    # Knitting stage + active duty: re-opening risk
    if (check_complications and rest_quality == "active_duty"
            and new_stage_idx >= STAGES.index("knitting")):
        tou = member.get("tou", 5)
        check = resolve_check(tou, 0, 0, "re-opening")
        if check.result in (ResultLevel.FAILURE, ResultLevel.CRITICAL_FAILURE):
            wound["healing_stage"] = "fresh"
            wound["healing_day_count"] = 0
            wound["bleeding"] = BLEEDING_RATE.get(severity, 0)
            wound["treated"] = False
            complications.append(
                f"The wound re-opens from exertion.  {member['name']} "
                f"bleeds again.  Healing time will be longer."
            )
            wound["pain_level"] = compute_pain_level(wound)
            return {
                "wound_id": wound_id,
                "old_stage": old_stage,
                "new_stage": "fresh",
                "days_elapsed": days_elapsed,
                "rest_quality": rest_quality,
                "events": events,
                "complications": complications,
                "pain_level": wound["pain_level"],
            }

    # Infection check (stages 0–1, daily)
    if check_complications and not wound.get("infected"):
        infection_days = min(days_elapsed, 14)
        for _ in range(infection_days):
            if wound.get("infected"):
                break
            if wound["healing_stage"] in ("fresh", "clotting"):
                chance = _daily_infection_chance(wound, member, rest_quality)
                if random.randint(1, 100) <= chance:
                    wound["infected"] = True
                    wound["infection_stage"] = "early"
                    complications.append(
                        f"The wound festers.  Redness spreads around "
                        f"{wound['sublocation'].replace('_', ' ')}.  "
                        f"Early infection."
                    )

    # Advance stage
    wound["healing_stage"] = STAGES[new_stage_idx]

    if new_stage_idx > old_stage_idx:
        for i in range(old_stage_idx + 1, new_stage_idx + 1):
            events.append(f"Wound advances to {STAGES[i]}.")
        if STAGES[new_stage_idx] == "scarring":
            events.append("The wound is closing to scar tissue.")
        elif STAGES[new_stage_idx] == "healed":
            wound["resolved"] = True
            wound["bleeding"] = 0
            events.append("The wound is healed.")

    wound["pain_level"] = compute_pain_level(wound)

    return {
        "wound_id": wound_id,
        "old_stage": old_stage,
        "new_stage": STAGES[new_stage_idx],
        "days_elapsed": days_elapsed,
        "rest_quality": rest_quality,
        "healing_day_count": wound["healing_day_count"],
        "events": events,
        "complications": complications,
        "pain_level": wound["pain_level"],
    }


def wound_infect(
    member: dict,
    wound_id: str,
    stage: str = "early",
    cause: str = "",
) -> dict:
    """Manually apply or advance infection on a wound."""
    wound = _find_wound(member, wound_id)
    if not wound:
        return {"error": f"Wound {wound_id} not found on {member['name']}."}

    old_stage = wound.get("infection_stage", "none")
    wound["infected"] = True
    wound["infection_stage"] = stage
    wound["pain_level"] = compute_pain_level(wound)

    effects = INFECTION_EFFECTS.get(stage, {})
    message = (
        f"{member['name']}'s wound at {wound['sublocation'].replace('_', ' ')} "
        f"is now infected ({stage}).  "
    )
    if cause:
        message += cause + "  "
    if effects.get("hp_per_day"):
        message += f"Losing {effects['hp_per_day']} HP per day."

    return {
        "wound_id": wound_id,
        "old_infection": old_stage,
        "new_infection": stage,
        "cause": cause,
        "effects": effects,
        "pain_level": wound["pain_level"],
        "message": message,
    }


def wound_worsen(
    member: dict,
    wound_id: str,
    new_severity: str,
    cause: str = "",
) -> dict:
    """Increase wound severity (re-opening, infection, aggravation)."""
    wound = _find_wound(member, wound_id)
    if not wound:
        return {"error": f"Wound {wound_id} not found on {member['name']}."}

    old_severity = wound["severity"]
    old_idx = SEVERITY_ORDER.index(old_severity)
    new_idx = SEVERITY_ORDER.index(new_severity)
    if new_idx <= old_idx:
        return {"error": f"New severity must be worse than {old_severity}."}

    # HP cost = damage difference
    old_penalty = abs(WOUND_PENALTY.get(old_severity, 0))
    new_penalty = abs(WOUND_PENALTY.get(new_severity, 0))
    hp_cost = max(1, new_penalty - old_penalty)

    wound["severity"] = new_severity
    wound["healing_stage"] = "fresh"
    wound["healing_day_count"] = 0
    wound["treated"] = False
    wound["bleeding"] = BLEEDING_RATE.get(new_severity, 0)
    member["hp"] = max(0, member.get("hp", 30) - hp_cost)

    if member["hp"] <= 0 or new_severity == "mortal":
        member["status"] = "dying"
    elif new_severity in ("serious", "critical"):
        member["status"] = "wounded"

    wound["pain_level"] = compute_pain_level(wound)

    return {
        "wound_id": wound_id,
        "old_severity": old_severity,
        "new_severity": new_severity,
        "hp_cost": hp_cost,
        "cause": cause,
        "pain_level": wound["pain_level"],
        "message": (
            f"{member['name']}'s wound worsens from {old_severity} to "
            f"{new_severity}.  {cause}"
        ),
    }


def wound_improve(
    member: dict,
    wound_id: str,
    new_severity: str,
    cause: str = "",
) -> dict:
    """Decrease wound severity (good treatment, high TOU)."""
    wound = _find_wound(member, wound_id)
    if not wound:
        return {"error": f"Wound {wound_id} not found on {member['name']}."}

    old_severity = wound["severity"]
    old_idx = SEVERITY_ORDER.index(old_severity)
    new_idx = SEVERITY_ORDER.index(new_severity)
    if new_idx >= old_idx:
        return {"error": f"New severity must be better than {old_severity}."}

    wound["severity"] = new_severity
    # Does NOT reset healing stage — improvement accelerates healing
    wound["bleeding"] = BLEEDING_RATE.get(new_severity, 0)
    wound["pain_level"] = compute_pain_level(wound)

    return {
        "wound_id": wound_id,
        "old_severity": old_severity,
        "new_severity": new_severity,
        "cause": cause,
        "pain_level": wound["pain_level"],
        "message": (
            f"{member['name']}'s wound improves from {old_severity} to "
            f"{new_severity}.  {cause}"
        ),
    }


def wound_scar(
    member: dict,
    wound_id: str,
    scar_description: str = "",
    visibility: str = "visible",
    permanent_effect: dict | None = None,
    weather_sensitive: bool = False,
    narrative_tag: str = "",
) -> dict:
    """Convert a healed wound to a permanent scar record."""
    wound = _find_wound(member, wound_id)
    if not wound:
        return {"error": f"Wound {wound_id} not found on {member['name']}."}

    if not scar_description:
        loc_name = _LOCATION_NAMES.get(
            wound["sublocation"], wound["sublocation"].replace("_", " "),
        )
        sev_adj = _SEVERITY_ADJ.get(wound["severity"], "")
        scar_description = f"A {sev_adj} scar across {loc_name}."

    scar = {
        "location": wound["location"],
        "sublocation": wound["sublocation"],
        "type": wound["type"],
        "description": scar_description,
        "visibility": visibility,
        "permanent_effect": permanent_effect,
        "weather_sensitive": weather_sensitive,
        "narrative_tag": narrative_tag,
        "source_wound_id": wound_id,
    }

    wound["resolved"] = True
    wound["healing_stage"] = "healed"
    wound["bleeding"] = 0
    wound["scar"] = scar

    # Add to member scars list
    if "scars" not in member:
        member["scars"] = []
    member["scars"].append(scar)

    return {
        "wound_id": wound_id,
        "scar": scar,
        "message": (
            f"{member['name']}'s wound at "
            f"{wound['sublocation'].replace('_', ' ')} "
            f"has scarred over.  {scar_description}"
        ),
    }


def wound_remove(
    member: dict,
    wound_id: str,
    reason: str = "Healed without complication.",
) -> dict:
    """Fully remove a resolved wound (scratches, minor healed wounds)."""
    wound = _find_wound(member, wound_id)
    if not wound:
        return {"error": f"Wound {wound_id} not found on {member['name']}."}

    member["wounds"] = [w for w in member["wounds"] if w.get("id") != wound_id]
    return {
        "wound_id": wound_id,
        "removed": True,
        "reason": reason,
        "message": f"Wound {wound_id} removed from {member['name']}.  {reason}",
    }


def amputation(
    member: dict,
    location: str,
    sublocation: str,
    healer_name: str = "",
    method: str = "bone_saw_and_cautery",
    reason: str = "",
) -> dict:
    """
    Amputate a body part.  Resolves all wounds on the amputated
    portion, creates a surgical wound at the stump, and reduces max_hp.
    """
    hp_cost = AMPUTATION_HP_COST.get(sublocation, 3)

    # Resolve all wounds on the amputated location
    resolved_wounds = []
    for w in member.get("wounds", []):
        if w["location"] == location and not w.get("resolved"):
            w["resolved"] = True
            w["healing_stage"] = "healed"
            w["bleeding"] = 0
            resolved_wounds.append(w["id"])

    # Reduce max HP permanently
    member["max_hp"] = member.get("max_hp", 30) - hp_cost
    if member["hp"] > member["max_hp"]:
        member["hp"] = member["max_hp"]

    # Create surgical wound at stump
    stump_wound = wound_apply(
        member,
        location=location,
        severity="serious",
        damage=0,
        weapon="",
        inflicted_by=healer_name or "surgery",
        sublocation=sublocation,
        wound_type="crush",
    )
    stump_wound["description"] = (
        f"Amputation stump at {sublocation.replace('_', ' ')}.  "
        f"Method: {method.replace('_', ' ')}."
    )

    # Create permanent incapacitation
    if "special_conditions" not in member:
        member["special_conditions"] = []
    member["special_conditions"].append({
        "type": "amputation",
        "location": location,
        "sublocation": sublocation,
        "description": f"Missing: {sublocation.replace('_', ' ')}",
    })

    return {
        "location": location,
        "sublocation": sublocation,
        "hp_cost": hp_cost,
        "new_max_hp": member["max_hp"],
        "resolved_wounds": resolved_wounds,
        "stump_wound_id": stump_wound["id"],
        "reason": reason,
        "message": (
            f"{healer_name or 'The leech'} amputates {member['name']}'s "
            f"{sublocation.replace('_', ' ')}.  "
            f"Max HP reduced by {hp_cost}.  "
            f"{len(resolved_wounds)} wound(s) resolved."
        ),
    }


def condition_update(member: dict) -> dict:
    """
    Recalculate overall condition from all active wounds, infections,
    and incapacitations.  Returns condition string and detail.
    """
    if member.get("hp", 1) <= 0:
        # Check for active heal attempts
        active_heals = any(
            w.get("treated") and w["severity"] == "mortal"
            for w in member.get("wounds", [])
        )
        if active_heals:
            member["condition"] = "dying"
        else:
            member["condition"] = "dead"
        return {"condition": member["condition"], "detail": "HP at zero."}

    active_wounds = [
        w for w in member.get("wounds", []) if not w.get("resolved")
    ]

    if not active_wounds:
        has_scars = bool(member.get("scars"))
        has_special = bool(member.get("special_conditions"))
        if has_scars or has_special:
            member["condition"] = "scarred_but_functional"
            member["status"] = "active"
        else:
            member["condition"] = "healthy"
            member["status"] = "active"
        return {"condition": member["condition"]}

    # Score by worst wound
    worst = max(
        active_wounds,
        key=lambda w: SEVERITY_ORDER.index(w["severity"]),
    )
    worst_sev = worst["severity"]

    # Check infection
    worst_infection = "none"
    for w in active_wounds:
        inf = w.get("infection_stage", "none")
        if INFECTION_STAGES.index(inf) > INFECTION_STAGES.index(worst_infection):
            worst_infection = inf

    # Check healing stage (all in stage 3+ means recovering)
    all_closing = all(
        STAGES.index(w.get("healing_stage", "fresh")) >= STAGES.index("closing")
        for w in active_wounds
    )

    if worst_sev == "mortal" or worst_infection == "mortification":
        cond = "dying"
        member["status"] = "dying"
    elif worst_sev == "critical" and not worst.get("treated"):
        cond = "incapacitated"
        member["status"] = "wounded"
    elif worst_infection in ("deep_rot", "mortification"):
        cond = "badly_wounded"
        member["status"] = "wounded"
    elif worst_sev == "serious" and not worst.get("treated"):
        cond = "badly_wounded"
        member["status"] = "wounded"
    elif all_closing:
        cond = "wounded_recovering"
        member["status"] = "wounded"
    else:
        cond = "wounded_limited"
        member["status"] = "wounded"

    # Pain overlay
    pain = compute_overall_pain(member)

    # Wound count systemic penalty
    n = len(active_wounds)
    if n <= 2:
        systemic = "none"
    elif n <= 4:
        systemic = "-5 all rolls"
    elif n <= 6:
        systemic = "-10 all rolls, appetite loss, poor sleep"
    else:
        systemic = "-20 all rolls, wound-fever risk"

    member["condition"] = cond
    return {
        "condition": cond,
        "worst_wound": worst_sev,
        "worst_infection": worst_infection,
        "active_wound_count": n,
        "systemic_effect": systemic,
        "overall_pain": pain,
    }


# ───────────────────────────────────────────────────────────────────────
# Status / Describe / Roster
# ───────────────────────────────────────────────────────────────────────

def member_wound_status(member: dict) -> dict:
    """Full wound status report for a member."""
    active = [w for w in member.get("wounds", []) if not w.get("resolved")]
    resolved = [w for w in member.get("wounds", []) if w.get("resolved")]
    scars = member.get("scars", [])

    cond = condition_update(member)
    pain = compute_overall_pain(member)

    wound_details = []
    for w in active:
        wound_details.append({
            "id": w["id"],
            "location": w["location"],
            "sublocation": w["sublocation"],
            "severity": w["severity"],
            "healing_stage": w["healing_stage"],
            "treated": w["treated"],
            "infected": w["infected"],
            "infection_stage": w.get("infection_stage", "none"),
            "bleeding": w["bleeding"],
            "pain": compute_pain_level(w),
            "description": w["description"],
        })

    return {
        "name": member["name"],
        "hp": member.get("hp"),
        "max_hp": member.get("max_hp"),
        "condition": cond["condition"],
        "overall_pain": pain,
        "active_wounds": wound_details,
        "resolved_wounds": len(resolved),
        "scars": len(scars),
        "special_conditions": member.get("special_conditions", []),
    }


def describe_wound(member: dict, wound_id: str) -> dict:
    """Generate narrative description of a wound's current state."""
    wound = _find_wound(member, wound_id)
    if not wound:
        return {"error": f"Wound {wound_id} not found."}

    stage = wound.get("healing_stage", "fresh")
    sev = wound["severity"]
    loc = wound["sublocation"].replace("_", " ")
    pain = compute_pain_level(wound)

    # Build description
    lines = [wound["description"]]
    lines.append(f"Severity: {sev}.  Stage: {stage}.  Pain: {pain}.")

    if wound.get("treated"):
        lines.append(
            f"Treated by {wound.get('treated_by', 'unknown')} "
            f"({wound.get('treatment_type', 'unknown')})."
        )
    else:
        lines.append("Untreated.")

    if wound.get("bleeding", 0) > 0:
        lines.append(f"Bleeding: {wound['bleeding']} HP per round.")

    if wound.get("infected"):
        inf = wound.get("infection_stage", "early")
        lines.append(f"INFECTED — {inf}.  The flesh around the wound is angry and hot.")

    if stage == "knitting":
        lines.append("The wound is knitting.  Heavy exertion risks re-opening.")
    elif stage == "scarring":
        lines.append("Scar tissue is forming.  The wound is nearly healed.")
    elif stage == "fresh":
        lines.append("The wound is fresh and raw.")

    # Pain narrative
    if pain == "agonizing":
        lines.append(
            f"{member['name']} cannot think past the pain.  "
            f"Everything narrows to the wound."
        )
    elif pain == "severe":
        lines.append(
            f"The pain catches {member['name']}'s breath with every movement."
        )
    elif pain == "moderate":
        lines.append(
            f"A constant throb from the {loc} that {member['name']} "
            f"cannot ignore."
        )

    return {
        "wound_id": wound_id,
        "description": "  ".join(lines),
        "pain_level": pain,
    }


def roster_wounds(band: dict) -> list[dict]:
    """Get wound summary for all band members."""
    results = []
    for m in band.get("members", []):
        active = [w for w in m.get("wounds", []) if not w.get("resolved")]
        if active or m.get("status") in ("wounded", "dying"):
            cond = condition_update(m)
            pain = compute_overall_pain(m)
            results.append({
                "name": m["name"],
                "status": m.get("status"),
                "condition": cond["condition"],
                "hp": f"{m.get('hp', '?')}/{m.get('max_hp', '?')}",
                "active_wounds": len(active),
                "overall_pain": pain,
                "wounds": [
                    f"{w['id']}: {w['severity']} {w['sublocation']} ({w['healing_stage']})"
                    for w in active
                ],
            })
    return results


# ───────────────────────────────────────────────────────────────────────
# Internal helpers
# ───────────────────────────────────────────────────────────────────────

def _find_wound(member: dict, wound_id: str) -> dict | None:
    """Find a wound by ID on a member."""
    for w in member.get("wounds", []):
        if w.get("id") == wound_id:
            return w
    return None


def _daily_infection_chance(
    wound: dict, member: dict, rest_quality: str,
) -> int:
    """Compute daily infection chance percentage for a wound."""
    base = INFECTION_BASE_CHANCE.get(wound["severity"], 10)

    fb_bonus = 0
    if wound.get("foreign_body"):
        fb_type = wound.get("foreign_body_type", "cloth")
        fb_bonus = {"cloth": 10, "dirt": 15, "rust": 15,
                    "arrowhead": 20, "bone_splinter": 10}.get(fb_type, 10)

    env_bonus = 0
    if rest_quality == "active_duty":
        env_bonus = 10
    elif rest_quality == "field_rest":
        env_bonus = 5

    treatment_bonus = 0
    if wound.get("treated"):
        treatment_bonus = TREATMENT_TABLE.get(
            wound.get("treatment_type", "first_aid"), {},
        ).get("infection_reduction", 0)

    tou_bonus = member.get("tou", 5) * 2

    chance = base + fb_bonus + env_bonus - treatment_bonus - tou_bonus
    return max(1, min(95, chance))


# ───────────────────────────────────────────────────────────────────────
# Band-level wound helpers
# ───────────────────────────────────────────────────────────────────────

def advance_all_wounds(band: dict, days: int, rest_quality: str = "field_rest") -> list[dict]:
    """Advance all active wounds for all band members.  Returns events."""
    all_events = []
    for m in band.get("members", []):
        if m.get("status") == "dead":
            continue
        for w in m.get("wounds", []):
            if w.get("resolved"):
                continue
            result = wound_heal(m, w["id"], days, rest_quality)
            if result.get("events") or result.get("complications"):
                result["member"] = m["name"]
                all_events.append(result)
        # Run infection progression
        for w in m.get("wounds", []):
            if w.get("resolved") or not w.get("infected"):
                continue
            _advance_infection(m, w, days)
        # Update condition
        condition_update(m)
    return all_events


def _advance_infection(member: dict, wound: dict, days: int):
    """Advance infection state over time if untreated."""
    stage = wound.get("infection_stage", "none")
    if stage == "none":
        return
    stage_idx = INFECTION_STAGES.index(stage)

    # Each day of unresolved infection has a chance to advance
    for _ in range(days):
        if stage_idx >= len(INFECTION_STAGES) - 1:
            break
        # Heal check to contain
        tou = member.get("tou", 5)
        check = resolve_check(tou, 0, INFECTION_EFFECTS.get(stage, {}).get("heal_mod", 0))
        if check.result in (ResultLevel.FAILURE, ResultLevel.CRITICAL_FAILURE):
            if random.random() < 0.3:  # 30% per failed day to advance
                stage_idx += 1
                stage = INFECTION_STAGES[stage_idx]
                wound["infection_stage"] = stage

    # HP cost from infection
    hp_cost = INFECTION_EFFECTS.get(stage, {}).get("hp_per_day", 0) * days
    if hp_cost > 0:
        member["hp"] = max(0, member.get("hp", 30) - hp_cost)
        if member["hp"] <= 0:
            member["status"] = "dying"


# ───────────────────────────────────────────────────────────────────────
# CLI
# ───────────────────────────────────────────────────────────────────────

def _load_band(path: str) -> dict:
    """Load a band JSON or YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    if path.endswith((".yaml", ".yml")):
        if _yaml is None:
            raise ImportError("pyyaml is required for YAML band files.")
        return _yaml.safe_load(raw)
    return json.loads(raw)


def _save_band(band: dict, path: str):
    """Save a band JSON or YAML file, preserving format."""
    if path.endswith((".yaml", ".yml")):
        if _yaml is None:
            raise ImportError("pyyaml is required for YAML band files.")
        with open(path, "w", encoding="utf-8") as f:
            _yaml.dump(band, f, allow_unicode=True, sort_keys=False)
    else:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(band, f, indent=2, ensure_ascii=False)


def _find_member(band: dict, name: str) -> dict | None:
    """Find a member by name (case insensitive)."""
    for m in band.get("members", []):
        if m["name"].lower() == name.lower():
            return m
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Iron Ledger — Wound Management System",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview mutations without writing band file",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # ── apply ──
    apply_p = subparsers.add_parser("apply", help="Apply a new wound")
    apply_p.add_argument("--band-file", required=True)
    apply_p.add_argument("--target", required=True)
    apply_p.add_argument("--location", required=True,
                         choices=list(SUBLOCATION_TABLE.keys()))
    apply_p.add_argument("--sublocation", default="")
    apply_p.add_argument("--severity", required=True,
                         choices=SEVERITY_ORDER[1:])
    apply_p.add_argument("--damage", type=int, required=True)
    apply_p.add_argument("--type", dest="wound_type", default="")
    apply_p.add_argument("--weapon", default="")
    apply_p.add_argument("--inflicted-by", default="")
    apply_p.add_argument("--foreign-body", action="store_true")
    apply_p.add_argument("--foreign-body-type", default="cloth")
    apply_p.add_argument("--save", action="store_true")
    apply_p.add_argument("--json", action="store_true")

    # ── treat ──
    treat_p = subparsers.add_parser("treat", help="Treat an existing wound")
    treat_p.add_argument("--band-file", required=True)
    treat_p.add_argument("--target", required=True)
    treat_p.add_argument("--wound-id", required=True)
    treat_p.add_argument("--treatment", required=True,
                         choices=list(TREATMENT_TABLE.keys()))
    treat_p.add_argument("--healer", default="")
    treat_p.add_argument("--healer-wit", type=int, default=5)
    treat_p.add_argument("--healer-skill", type=int, default=1)
    treat_p.add_argument("--environment", default="clean_camp",
                         choices=list(ENVIRONMENT_HEAL_MOD.keys()))
    treat_p.add_argument("--tools", default="basic",
                         choices=list(TOOL_HEAL_MOD.keys()))
    treat_p.add_argument("--save", action="store_true")
    treat_p.add_argument("--json", action="store_true")

    # ── heal ──
    heal_p = subparsers.add_parser("heal", help="Advance healing timeline")
    heal_p.add_argument("--band-file", required=True)
    heal_p.add_argument("--target", required=True)
    heal_p.add_argument("--wound-id", required=True)
    heal_p.add_argument("--days", type=int, required=True)
    heal_p.add_argument("--rest", default="full_rest",
                        choices=list(REST_QUALITY_MULT.keys()))
    heal_p.add_argument("--save", action="store_true")
    heal_p.add_argument("--json", action="store_true")

    # ── infect ──
    inf_p = subparsers.add_parser("infect", help="Apply infection")
    inf_p.add_argument("--band-file", required=True)
    inf_p.add_argument("--target", required=True)
    inf_p.add_argument("--wound-id", required=True)
    inf_p.add_argument("--stage", default="early",
                       choices=INFECTION_STAGES[1:])
    inf_p.add_argument("--cause", default="")
    inf_p.add_argument("--save", action="store_true")
    inf_p.add_argument("--json", action="store_true")

    # ── worsen ──
    wor_p = subparsers.add_parser("worsen", help="Worsen a wound")
    wor_p.add_argument("--band-file", required=True)
    wor_p.add_argument("--target", required=True)
    wor_p.add_argument("--wound-id", required=True)
    wor_p.add_argument("--new-severity", required=True,
                       choices=SEVERITY_ORDER[1:])
    wor_p.add_argument("--cause", default="")
    wor_p.add_argument("--save", action="store_true")
    wor_p.add_argument("--json", action="store_true")

    # ── improve ──
    imp_p = subparsers.add_parser("improve", help="Improve a wound")
    imp_p.add_argument("--band-file", required=True)
    imp_p.add_argument("--target", required=True)
    imp_p.add_argument("--wound-id", required=True)
    imp_p.add_argument("--new-severity", required=True,
                       choices=SEVERITY_ORDER[1:])
    imp_p.add_argument("--cause", default="")
    imp_p.add_argument("--save", action="store_true")
    imp_p.add_argument("--json", action="store_true")

    # ── scar ──
    scar_p = subparsers.add_parser("scar", help="Convert wound to scar")
    scar_p.add_argument("--band-file", required=True)
    scar_p.add_argument("--target", required=True)
    scar_p.add_argument("--wound-id", required=True)
    scar_p.add_argument("--description", default="")
    scar_p.add_argument("--visibility", default="visible",
                        choices=["hidden", "visible", "obvious", "disfiguring"])
    scar_p.add_argument("--weather-sensitive", action="store_true")
    scar_p.add_argument("--save", action="store_true")
    scar_p.add_argument("--json", action="store_true")

    # ── remove ──
    rem_p = subparsers.add_parser("remove", help="Remove a resolved wound")
    rem_p.add_argument("--band-file", required=True)
    rem_p.add_argument("--target", required=True)
    rem_p.add_argument("--wound-id", required=True)
    rem_p.add_argument("--reason", default="Healed without complication.")
    rem_p.add_argument("--save", action="store_true")
    rem_p.add_argument("--json", action="store_true")

    # ── amputate ──
    amp_p = subparsers.add_parser("amputate", help="Amputate a body part")
    amp_p.add_argument("--band-file", required=True)
    amp_p.add_argument("--target", required=True)
    amp_p.add_argument("--location", required=True)
    amp_p.add_argument("--sublocation", required=True)
    amp_p.add_argument("--healer", default="")
    amp_p.add_argument("--method", default="bone_saw_and_cautery")
    amp_p.add_argument("--reason", default="")
    amp_p.add_argument("--save", action="store_true")
    amp_p.add_argument("--json", action="store_true")

    # ── status ──
    stat_p = subparsers.add_parser("status", help="Wound status for one member")
    stat_p.add_argument("--band-file", required=True)
    stat_p.add_argument("--target", required=True)
    stat_p.add_argument("--json", action="store_true")

    # ── describe ──
    desc_p = subparsers.add_parser("describe", help="Narrative wound description")
    desc_p.add_argument("--band-file", required=True)
    desc_p.add_argument("--target", required=True)
    desc_p.add_argument("--wound-id", required=True)
    desc_p.add_argument("--json", action="store_true")

    # ── roster ──
    ros_p = subparsers.add_parser("roster", help="All wounded members")
    ros_p.add_argument("--band-file", required=True)
    ros_p.add_argument("--json", action="store_true")

    # ── advance / daily_tick ──
    for _cmd, _help in [
        ("advance", "Advance all wounds by days"),
        ("daily_tick", "Auto-tick wounds/infection for N days (alias for advance)"),
    ]:
        adv_p = subparsers.add_parser(_cmd, help=_help)
        adv_p.add_argument("--band-file", required=True)
        adv_p.add_argument("--days", type=int, required=True)
        adv_p.add_argument(
            "--rest", "--rest-quality",
            default="field_rest", dest="rest",
            choices=list(REST_QUALITY_MULT.keys()),
        )
        adv_p.add_argument("--member", default="",
                           help="Limit tick to one member by name")
        adv_p.add_argument("--save", action="store_true")
        adv_p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    band = _load_band(args.band_file)

    # Commands that need a target member
    if args.command in ("apply", "treat", "heal", "infect", "worsen",
                        "improve", "scar", "remove", "amputate",
                        "status", "describe"):
        member = _find_member(band, args.target)
        if not member:
            print(f"Error: Member '{args.target}' not found.", file=sys.stderr)
            sys.exit(1)

    if args.command == "apply":
        result = wound_apply(
            member, args.location, args.severity, args.damage,
            weapon=args.weapon, inflicted_by=args.inflicted_by,
            sublocation=args.sublocation, wound_type=args.wound_type,
            foreign_body=args.foreign_body,
            foreign_body_type=args.foreign_body_type,
            current_day=band.get("day_of_year", 0),
        )
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Applied {result['severity']} wound to "
                  f"{member['name']}'s {result['sublocation']}.")
            print(f"  {result['description']}")
            print(f"  HP: {member['hp']}/{member.get('max_hp', '?')}")

    elif args.command == "treat":
        result = wound_treat(
            member, args.wound_id, args.treatment,
            healer_name=args.healer,
            healer_wit=args.healer_wit,
            healer_heal_skill=args.healer_skill,
            environment=args.environment,
            tools=args.tools,
        )
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result.get("message", "Treatment complete."))

    elif args.command == "heal":
        result = wound_heal(
            member, args.wound_id, args.days, args.rest,
        )
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            for e in result.get("events", []):
                print(f"  {e}")
            for c in result.get("complications", []):
                print(f"  !! {c}")
            print(f"  Stage: {result.get('new_stage')} | "
                  f"Pain: {result.get('pain_level')}")

    elif args.command == "infect":
        result = wound_infect(member, args.wound_id, args.stage, args.cause)
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result.get("message"))

    elif args.command == "worsen":
        result = wound_worsen(
            member, args.wound_id, args.new_severity, args.cause,
        )
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result.get("message"))

    elif args.command == "improve":
        result = wound_improve(
            member, args.wound_id, args.new_severity, args.cause,
        )
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result.get("message"))

    elif args.command == "scar":
        result = wound_scar(
            member, args.wound_id,
            scar_description=args.description,
            visibility=args.visibility,
            weather_sensitive=args.weather_sensitive,
        )
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result.get("message"))

    elif args.command == "remove":
        result = wound_remove(member, args.wound_id, args.reason)
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result.get("message"))

    elif args.command == "amputate":
        result = amputation(
            member, args.location, args.sublocation,
            healer_name=args.healer, method=args.method,
            reason=args.reason,
        )
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result.get("message"))

    elif args.command == "status":
        result = member_wound_status(member)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"=== {result['name']} ===")
            print(f"HP: {result['hp']}/{result['max_hp']}")
            print(f"Condition: {result['condition']}")
            print(f"Overall pain: {result['overall_pain']}")
            for w in result["active_wounds"]:
                inf = f" [INFECTED: {w['infection_stage']}]" if w["infected"] else ""
                print(f"  {w['id']}: {w['severity']} {w['sublocation']} "
                      f"({w['healing_stage']}) pain:{w['pain']}{inf}")
            if result["scars"]:
                print(f"Scars: {result['scars']}")
            for sc in result.get("special_conditions", []):
                print(f"  Special: {sc}")

    elif args.command == "describe":
        result = describe_wound(member, args.wound_id)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result.get("description", "No description."))

    elif args.command == "roster":
        results = roster_wounds(band)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            if not results:
                print("No wounded members.")
            for r in results:
                print(f"{r['name']}: {r['condition']} ({r['hp']}) "
                      f"pain:{r['overall_pain']}")
                for w in r["wounds"]:
                    print(f"  {w}")

    elif args.command in ("advance", "daily_tick"):
        target_name = getattr(args, "member", "")
        if target_name:
            # Single-member tick
            target_member = _find_member(band, target_name)
            if not target_member:
                print(f"Error: Member '{target_name}' not found.", file=sys.stderr)
                sys.exit(1)
            # Build a temporary band-like dict with just that member
            scratch = {"members": [target_member],
                       "day_of_year": band.get("day_of_year",
                           band.get("band", {}).get("day_of_year", 0))}
            events = advance_all_wounds(scratch, args.days, args.rest)
        else:
            events = advance_all_wounds(band, args.days, args.rest)
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(events, indent=2))
        else:
            label = target_name or "all members"
            if not events:
                print(f"=== {args.days}-day wound tick ({args.rest}) — {label} ===")
                print("  No wound changes.")
            else:
                for e in events:
                    name = e.get("member", "?")
                    wid = e.get("wound_id", "?")
                    print(f"=== {args.days}-day wound tick ({args.rest}) — {name} ===")
                    for ev in e.get("events", []):
                        print(f"  {wid}: {ev}")
                    for c in e.get("complications", []):
                        print(f"  !! {wid}: {c}")


if __name__ == "__main__":
    main()
