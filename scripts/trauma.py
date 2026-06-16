#!/usr/bin/env python3
"""
Hugr Ledger — Psychological Trauma Management System

Full trauma lifecycle: apply, trigger, recover, worsen, improve,
resolve, add-condition, and profile assessment.  All rules from
20_SIMULATION_RULES.md § 5.18–5.26.

Operates on band JSON files produced by band_manager.py, or on
standalone member JSON dicts piped in from combat_sim.py.

Usage:
    python trauma.py apply    --band-file band.json --target "Ubbe Ironside" --event "Rolf killed beside him" --category shield_brother_death --tsp 8
    python trauma.py trigger  --band-file band.json --target "Ubbe Ironside" --trauma-id t_001 --trigger iron_clang --context combat
    python trauma.py recover  --band-file band.json --target "Ubbe Ironside" --trauma-id t_001 --days 7 --rest field_rest
    python trauma.py worsen   --band-file band.json --target "Ubbe Ironside" --trauma-id t_001 --new-severity severe --cause "Another death"
    python trauma.py improve  --band-file band.json --target "Ubbe Ironside" --trauma-id t_001 --new-severity mild --cause "Winter quarters"
    python trauma.py resolve  --band-file band.json --target "Ubbe Ironside" --trauma-id t_001
    python trauma.py add      --band-file band.json --target "Thorne Ash-Born" --condition flinch_sickness --severity mild --source "Hall fire"
    python trauma.py status   --band-file band.json --target "Ubbe Ironside"
    python trauma.py roster   --band-file band.json
    python trauma.py advance  --band-file band.json --days 7 --rest field_rest
"""

import argparse
import json
import random
import sys
import os
from copy import deepcopy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import resolve_check, roll_d100, ResultLevel


# ───────────────────────────────────────────────────────────────────────
# Constants — from 20_SIMULATION_RULES.md § 5.18–5.26
# ───────────────────────────────────────────────────────────────────────

SEVERITY_ORDER = ["none", "mild", "moderate", "severe", "crippling"]

CONDITION_TYPES = [
    "battle_shock", "night_terrors", "flinch_sickness", "anger_storm",
    "killing_calm", "withdrawal", "drink_need", "risk_seeking",
    "grief_lock", "mind_flight", "heavy_mind",
]

# TSP ranges per event category
TSP_BASE = {
    "minor_shock":             (1, 2),
    "combat_exposure":         (2, 4),
    "severe_combat":           (4, 6),
    "horror_sight":            (5, 8),
    "betrayal_wound":          (4, 7),
    "shield_brother_death":    (6, 10),
    "killing_unarmed":         (3, 6),
    "extended_deprivation":    (2, 4),
    "campaign_stress":         (1, 1),
}

# Default likely conditions by event category
CATEGORY_CONDITIONS = {
    "minor_shock":          ["battle_shock", "flinch_sickness"],
    "combat_exposure":      ["battle_shock", "night_terrors", "flinch_sickness"],
    "severe_combat":        ["night_terrors", "flinch_sickness", "anger_storm", "mind_flight"],
    "horror_sight":         ["night_terrors", "mind_flight", "heavy_mind", "withdrawal"],
    "betrayal_wound":       ["withdrawal", "anger_storm", "drink_need"],
    "shield_brother_death": ["grief_lock", "night_terrors", "withdrawal", "risk_seeking"],
    "killing_unarmed":      ["heavy_mind", "killing_calm", "drink_need"],
    "extended_deprivation":  ["heavy_mind", "withdrawal", "anger_storm"],
    "campaign_stress":      ["heavy_mind", "drink_need", "night_terrors"],
}

# Default triggers by event source
DEFAULT_TRIGGERS = {
    "combat_exposure":      ["iron_clang", "war_cries", "blood_smell", "sudden_movement"],
    "severe_combat":        ["iron_clang", "blood_smell", "weapons_drawn", "screaming"],
    "horror_sight":         ["corpses", "fire", "children", "confined_spaces"],
    "betrayal_wound":       ["oaths", "promises", "being_left_behind", "locked_doors"],
    "shield_brother_death": ["empty_seat", "dead_mans_name", "similar_faces"],
    "killing_unarmed":      ["blood_on_hands", "knife_edge", "dying_sound"],
    "minor_shock":          ["sudden_sounds", "blood_smell"],
    "extended_deprivation":  ["empty_plates", "food_waste", "cold"],
    "campaign_stress":      ["war_drums", "marching", "exhaustion"],
}

# Condition-specific penalties (§ 5.20)
CONDITION_PENALTIES = {
    "battle_shock":    {"trigger_effect": "freeze_1d6_rounds", "social_mod": 0},
    "night_terrors":   {"rest_quality_penalty": 1, "band_morale_cost": 1},
    "flinch_sickness": {"initiative_mod": -5, "perception_mod": -5},
    "anger_storm":     {"failed_wil_effect": "attack_nearest"},
    "killing_calm":    {"combat_mod": 5, "social_mod": -10, "loyalty_loss_monthly": 1},
    "withdrawal":      {"social_target_mod": -10},
    "drink_need":      {"sober_penalty": -5, "drunk_fear_immunity": True},
    "risk_seeking":    {"ignores_retreat_on_fail": True},
    "grief_lock":      {"no_new_bonds": True, "morale_contribution": -10},
    "mind_flight":     {"lost_time": "1d6_minutes", "concentration_mod": -5},
    "heavy_mind":      {"all_rolls_mod": -5, "march_penalty": 1, "no_initiative": True},
}

# Severity penalties (§ 5.20)
SEVERITY_PENALTIES = {
    "mild":      {"trigger_mod": -5,  "general_mod": 0,   "wil_check_freq": "weekly"},
    "moderate":  {"trigger_mod": -10, "general_mod": -5,  "wil_check_freq": "daily"},
    "severe":    {"trigger_mod": -15, "general_mod": -10, "wil_check_freq": "twice_daily"},
    "crippling": {"trigger_mod": -20, "general_mod": -20, "wil_check_freq": "three_daily"},
}

# Recovery RP thresholds by severity
RECOVERY_RP_THRESHOLD = {
    "mild": 14, "moderate": 30, "severe": 60, "crippling": 120,
}

# Recovery stages
RECOVERY_STAGES = ["acute", "active", "easing", "residual", "resolved"]

# RP generation rates
RP_RATES = {
    "full_rest":     3,
    "field_rest":    2,
    "active_duty":   1,
    "active_combat": 0,
}

RP_BONUSES = {
    "meaningful_work":       1,
    "shield_brother_present": 1,
    "dalla_care":            1,
    "saga_told":             1,
    "fire_inclusion":        0.5,
}

RP_PENALTIES = {
    "trigger_event":    -2,
    "new_trauma":       -5,
    "drunk":            -1,
    "isolation":        -2,
}

# WIL degradation thresholds (days unresolved)
WIL_DEGRADATION = [
    (90,  "permanent", -1),
    (30,  "temporary", -2),
    (0,   "temporary", -1),
]


# ───────────────────────────────────────────────────────────────────────
# Narrative Descriptors
# ───────────────────────────────────────────────────────────────────────

CONDITION_DESCRIPTIONS = {
    "battle_shock": {
        "mild": "Freezes for a heartbeat in the press of bodies. Recovers. No one is sure they saw it.",
        "moderate": "Goes vacant when steel rings. Hands drop. Comes back with a jolt, breathing hard.",
        "severe": "Cannot enter a fight without freezing. Stands like a post while iron swings past him.",
        "crippling": "Cannot function where violence is present. The body has decided. The man has no say.",
    },
    "night_terrors": {
        "mild": "Wakes suddenly, breathing fast, hands gripping the blanket. Falls back to sleep.",
        "moderate": "Wakes screaming. Thrashes. Takes minutes to know where he is. The band loses sleep.",
        "severe": "Wakes fighting. Has struck men trying to wake him. No one sleeps near him.",
        "crippling": "Does not sleep. Sits awake through the dark hours, afraid of what comes when he closes his eyes.",
    },
    "flinch_sickness": {
        "mild": "Turns his head at sudden sounds. Recovers quickly. Only the sharp-eyed notice.",
        "moderate": "Flinches hard at door-slams, iron-clang, raised voices. Everyone notices.",
        "severe": "Ducks, covers, or draws steel at unexpected sounds. Cannot control the reaction.",
        "crippling": "Lives in a permanent state of expecting the blow. Cannot be near loud work.",
    },
    "anger_storm": {
        "mild": "Snaps at small things — a spilled cup, a slow answer. Apologizes or walks away.",
        "moderate": "Erupts over nothing. Shoves, shouts, throws things. Regrets it when calm returns.",
        "severe": "Violent outbursts. Has fought band members over imagined slights. Dangerous at close quarters.",
        "crippling": "Rage at everything, constant. The man is a weapon with no safety. Will kill on provocation.",
    },
    "killing_calm": {
        "mild": "Quieter after kills than before. The fire does not bother him. Nothing does.",
        "moderate": "Performs violence efficiently, without expression. Others find this more disturbing than rage.",
        "severe": "No emotional response to any violence. The man kills as he chops wood. Functional. Empty.",
        "crippling": "Has crossed into something the band does not want to name. Not fury — absence.",
    },
    "withdrawal": {
        "mild": "Takes the far seat at the fire. Answers when spoken to. Does not initiate.",
        "moderate": "Eats alone. Takes solo watches willingly. The band has to seek him out for orders.",
        "severe": "Functionally absent from the band. Does his work in silence. Sleeps apart.",
        "crippling": "Gone. Physically present but no one can reach him. Responds to direct orders. Nothing else.",
    },
    "drink_need": {
        "mild": "Drinks more than he used to. Reaches for the horn sooner. Not drunk — just steady.",
        "moderate": "Needs drink to sleep. Hands shake by midmorning without it. Performance suffers sober.",
        "severe": "Drunk by noon, if supply allows. Functional drunk, barely. The man he was is behind the horn.",
        "crippling": "Cannot function without drink. Will trade gear, silver, dignity for ale. Liability.",
    },
    "risk_seeking": {
        "mild": "Volunteers for dangerous work. Takes the forward position. Could be courage.",
        "moderate": "Ignores cover. Leaves his shield behind. Fights like a man who does not expect to return.",
        "severe": "Provokes enemies. Picks fights. The band suspects what this is but does not say it.",
        "crippling": "Actively seeking death. Will walk into a fight alone. Not courage — surrender.",
    },
    "grief_lock": {
        "mild": "Keeping the dead man's seat empty. Quieter since. Functional.",
        "moderate": "Cannot form new bonds. Rebuffs attempts at connection. Carries the dead man's gear.",
        "severe": "Speaks to the dead man. At the fire, in the dark. The band pretends not to hear.",
        "crippling": "Locked in mourning. Cannot process the loss. The living mean nothing next to the dead.",
    },
    "mind_flight": {
        "mild": "Loses a few seconds. Blinks back. 'What?' Occasional.",
        "moderate": "Goes away for minutes. Eyes open, mind elsewhere. Misses orders, misses cues.",
        "severe": "Extended absences from the present. The man walks, works, but is not here.",
        "crippling": "More gone than present. The body continues. The person returns in fragments.",
    },
    "heavy_mind": {
        "mild": "Slower to rise. Slower to start. Does the work but finds no drive in it.",
        "moderate": "No initiative. Waits to be told. Eats because the food is there. Flat voice.",
        "severe": "Cannot motivate. Sits unless moved. Gear deteriorates. Hygiene lapses.",
        "crippling": "Non-functional. Must be led, fed, dressed. The man is somewhere the band cannot follow.",
    },
}


# ───────────────────────────────────────────────────────────────────────
# ID generation
# ───────────────────────────────────────────────────────────────────────

def generate_trauma_id(member: dict) -> str:
    """Generate unique trauma ID."""
    profile = _ensure_profile(member)
    existing = {
        t.get("id", "") for t in profile.get("trauma_conditions", [])
    }
    for i in range(1, 999):
        tid = f"t_{i:03d}"
        if tid not in existing:
            return tid
    return f"t_{random.randint(100, 999):03d}"


# ───────────────────────────────────────────────────────────────────────
# Profile management
# ───────────────────────────────────────────────────────────────────────

def _ensure_profile(member: dict) -> dict:
    """Ensure member has a psychological_profile dict."""
    if "psychological_profile" not in member:
        wil = member.get("wil", member.get("attributes", {}).get("wil", 5))
        member["psychological_profile"] = {
            "tsp": 0,
            "stress_threshold": wil * 3,
            "trauma_conditions": [],
            "resilience_factors": {
                "shield_bond": None,
                "belief_framework": "low",
                "prior_recoveries": 0,
                "coping_method": "fire_and_drink",
            },
            "behavioral_baseline": {
                "speech_pattern": "normal",
                "sleep_quality": "normal",
                "appetite": "normal",
                "social_engagement": "normal",
                "drinking_level": "social",
            },
            "will_damage": {
                "temporary": 0,
                "permanent": 0,
            },
            "trauma_history": [],
        }
    return member["psychological_profile"]


def _get_wil(member: dict) -> int:
    """Extract effective WIL from member."""
    base = member.get("wil", member.get("attributes", {}).get("wil", 5))
    profile = member.get("psychological_profile", {})
    wd = profile.get("will_damage", {})
    return max(1, base - wd.get("temporary", 0) - wd.get("permanent", 0))


def _active_conditions(member: dict) -> list[dict]:
    """Get active (non-resolved) trauma conditions."""
    profile = _ensure_profile(member)
    return [
        t for t in profile.get("trauma_conditions", [])
        if not t.get("resolved")
    ]


# ───────────────────────────────────────────────────────────────────────
# Core Commands
# ───────────────────────────────────────────────────────────────────────

def trauma_apply(
    member: dict,
    event: str,
    category: str,
    tsp: int = 0,
    current_day: int = 0,
    shield_bond_active: bool = False,
    chronic_pain: bool = False,
    already_carrying_2plus: bool = False,
    first_exposure: bool = False,
    drunk: bool = False,
    wyr: int = 0,
) -> dict:
    """
    Apply a traumatic event.  Adds TSP, checks for condition onset.
    Mutates member in-place.
    """
    profile = _ensure_profile(member)

    # Base TSP
    if tsp == 0:
        lo, hi = TSP_BASE.get(category, (2, 4))
        tsp = random.randint(lo, hi)

    # Modifiers
    effective_tsp = tsp
    modifiers_log = []

    if shield_bond_active:
        effective_tsp -= 2
        modifiers_log.append("Shield-bond: -2")
    if wyr >= 3:
        effective_tsp -= 1
        modifiers_log.append("Strong belief (WYR 3+): -1")
    if already_carrying_2plus or len(_active_conditions(member)) >= 2:
        effective_tsp += 2
        modifiers_log.append("Carrying 2+ conditions: +2")
    if chronic_pain:
        effective_tsp += 1
        modifiers_log.append("Chronic pain: +1")
    if drunk:
        effective_tsp -= 1
        modifiers_log.append("Drunk: -1 (deferred +2 next day)")
    if first_exposure:
        effective_tsp += 2
        modifiers_log.append("First exposure: +2")

    effective_tsp = max(0, effective_tsp)

    # Add to total
    profile["tsp"] = profile.get("tsp", 0) + effective_tsp

    # Record history
    profile.setdefault("trauma_history", []).append({
        "event": event,
        "category": category,
        "day": current_day,
        "tsp_gained": effective_tsp,
        "modifiers": modifiers_log,
    })

    result = {
        "target": member["name"],
        "event": event,
        "category": category,
        "base_tsp": tsp,
        "effective_tsp": effective_tsp,
        "total_tsp": profile["tsp"],
        "stress_threshold": profile["stress_threshold"],
        "modifiers": modifiers_log,
        "condition_manifested": None,
    }

    # Check for condition manifestation
    if profile["tsp"] > profile["stress_threshold"]:
        overshoot = profile["tsp"] - profile["stress_threshold"]
        condition = _select_condition(member, category)
        severity = _overshoot_to_severity(overshoot)
        triggers = _select_triggers(category)

        tid = generate_trauma_id(member)
        trauma_record = {
            "id": tid,
            "condition": condition,
            "source_event": event,
            "source_day": current_day,
            "severity": severity,
            "tsp_at_onset": profile["tsp"],
            "triggers": triggers,
            "manifestation": "acute",
            "recovery_stage": "acute",
            "recovery_day_count": 0,
            "recovery_points": 0,
            "will_cost": 0,
            "resolved": False,
            "residual": None,
        }
        profile["trauma_conditions"].append(trauma_record)

        # Update behavioral baseline
        _update_baseline(member, condition, severity)

        # WIL impact for crippling
        if severity == "crippling":
            profile.setdefault("will_damage", {})
            profile["will_damage"]["permanent"] = \
                profile["will_damage"].get("permanent", 0) + 1
            profile["stress_threshold"] = _get_wil(member) * 3

        desc = CONDITION_DESCRIPTIONS.get(condition, {}).get(severity, "")

        result["condition_manifested"] = {
            "id": tid,
            "condition": condition,
            "severity": severity,
            "triggers": triggers,
            "description": desc,
        }
        result["message"] = (
            f"{member['name']} develops {condition.replace('_', ' ')} "
            f"({severity}). {desc}"
        )
    else:
        headroom = profile["stress_threshold"] - profile["tsp"]
        result["message"] = (
            f"{member['name']} absorbs the shock. TSP {profile['tsp']}/"
            f"{profile['stress_threshold']} (headroom: {headroom})."
        )

    return result


def trauma_trigger(
    member: dict,
    trauma_id: str,
    trigger: str,
    context: str = "non_combat",
    shield_brother_nearby: bool = False,
    dalla_present: bool = False,
    at_fire: bool = False,
    drunk_level: str = "sober",
    fatigued: bool = False,
    in_pain: bool = False,
    night: bool = False,
    alone: bool = False,
) -> dict:
    """
    Fire a trigger check.  Returns whether condition activates
    and for how long.
    """
    trauma = _find_trauma(member, trauma_id)
    if not trauma:
        return {"error": f"Trauma {trauma_id} not found on {member['name']}."}

    if trigger not in trauma.get("triggers", []):
        return {
            "trauma_id": trauma_id,
            "trigger": trigger,
            "activated": False,
            "message": f"'{trigger}' is not a trigger for {trauma['condition']}.",
        }

    wil = _get_wil(member)

    # Trigger check: target = 50 + (WIL × 5) + modifiers
    mods = 0
    mod_log = []
    if shield_brother_nearby:
        mods += 10; mod_log.append("Shield-brother: +10")
    if dalla_present:
        mods += 5; mod_log.append("Dalla present: +5")
    if at_fire:
        mods += 5; mod_log.append("At the fire: +5")
    if drunk_level == "moderate":
        mods += 5; mod_log.append("Moderate drink: +5")
    elif drunk_level == "heavy":
        mods -= 10; mod_log.append("Heavy drink: -10")
    if fatigued:
        mods -= 10; mod_log.append("Fatigued: -10")
    if in_pain:
        mods -= 5; mod_log.append("In pain: -5")
    if night:
        mods -= 5; mod_log.append("Night: -5")
    if alone:
        mods -= 10; mod_log.append("Alone: -10")

    # Use WIL as attribute, 0 skill, computed mods
    # Target formula: 50 + WIL*5 + mods → engine uses attr*5 + skill*10 + 15
    # So: attr*5 + 15 = 50 + WIL*5 → we pass WIL + 7 extra via mod
    # Actually let's compute directly:
    target = 50 + (wil * 5) + mods
    target = max(5, min(95, target))
    roll = random.randint(1, 100)

    crit_threshold = max(1, int(target * 0.20))

    if roll <= crit_threshold:
        result_level = "critical_success"
    elif roll <= target:
        result_level = "success"
    elif roll > 95:
        result_level = "critical_failure"
    else:
        result_level = "failure"

    result = {
        "trauma_id": trauma_id,
        "trigger": trigger,
        "context": context,
        "target": target,
        "roll": roll,
        "result": result_level,
        "modifiers": mod_log,
    }

    if result_level in ("success", "critical_success"):
        result["activated"] = False
        result["message"] = (
            f"{member['name']} endures. The {trigger.replace('_', ' ')} "
            f"hits a nerve, but the man holds."
        )
    else:
        # Condition activates
        if context == "combat":
            duration_units = random.randint(1, 6)
            duration_str = f"{duration_units * 10} minutes"
        else:
            duration_units = random.randint(1, 6)
            duration_str = f"{duration_units} hours"

        effective_severity = trauma["severity"]
        if result_level == "critical_failure":
            sev_idx = SEVERITY_ORDER.index(trauma["severity"])
            effective_severity = SEVERITY_ORDER[
                min(len(SEVERITY_ORDER) - 1, sev_idx + 1)
            ]
            # +1 TSP on critical failure
            profile = _ensure_profile(member)
            profile["tsp"] = profile.get("tsp", 0) + 1
            result["tsp_added"] = 1

        desc = CONDITION_DESCRIPTIONS.get(
            trauma["condition"], {},
        ).get(effective_severity, "")

        result["activated"] = True
        result["duration"] = duration_str
        result["effective_severity"] = effective_severity
        result["description"] = desc
        result["message"] = (
            f"{member['name']}'s {trauma['condition'].replace('_', ' ')} "
            f"activates ({effective_severity}, {duration_str}). {desc}"
        )

    return result


def trauma_recover(
    member: dict,
    trauma_id: str,
    days_elapsed: int,
    rest_quality: str = "field_rest",
    meaningful_work: bool = False,
    shield_brother_present: bool = False,
    dalla_care: bool = False,
    saga_told: bool = False,
    fire_inclusion: bool = True,
    trigger_events_today: int = 0,
    new_trauma_this_week: bool = False,
    drunk: bool = False,
    isolation: bool = False,
) -> dict:
    """
    Advance recovery timeline by elapsed days and conditions.
    """
    trauma = _find_trauma(member, trauma_id)
    if not trauma:
        return {"error": f"Trauma {trauma_id} not found on {member['name']}."}
    if trauma.get("resolved"):
        return {"trauma_id": trauma_id, "message": "Already resolved."}

    # Calculate daily RP
    base_rp = RP_RATES.get(rest_quality, 1)
    daily_rp = base_rp
    rp_log = [f"Base ({rest_quality}): {base_rp}"]

    if meaningful_work:
        daily_rp += RP_BONUSES["meaningful_work"]
        rp_log.append("Meaningful work: +1")
    if shield_brother_present:
        daily_rp += RP_BONUSES["shield_brother_present"]
        rp_log.append("Shield-brother: +1")
    if dalla_care:
        daily_rp += RP_BONUSES["dalla_care"]
        rp_log.append("Dalla's care: +1")
    if saga_told:
        daily_rp += RP_BONUSES["saga_told"]
        rp_log.append("Saga told: +1")
    if fire_inclusion:
        daily_rp += RP_BONUSES["fire_inclusion"]
        rp_log.append("Fire inclusion: +0.5")
    if trigger_events_today > 0:
        penalty = RP_PENALTIES["trigger_event"] * trigger_events_today
        daily_rp += penalty
        rp_log.append(f"Trigger events (×{trigger_events_today}): {penalty}")
    if new_trauma_this_week:
        daily_rp += RP_PENALTIES["new_trauma"]
        rp_log.append("New trauma: -5")
    if drunk:
        daily_rp += RP_PENALTIES["drunk"]
        rp_log.append("Self-medicating: -1")
    if isolation:
        daily_rp += RP_PENALTIES["isolation"]
        rp_log.append("Isolation: -2")

    total_rp = daily_rp * days_elapsed
    trauma["recovery_points"] = trauma.get("recovery_points", 0) + total_rp
    trauma["recovery_day_count"] = trauma.get("recovery_day_count", 0) + days_elapsed

    severity = trauma["severity"]
    threshold = RECOVERY_RP_THRESHOLD.get(severity, 30)
    old_stage = trauma.get("recovery_stage", "acute")

    result = {
        "trauma_id": trauma_id,
        "condition": trauma["condition"],
        "days_elapsed": days_elapsed,
        "daily_rp": daily_rp,
        "total_rp_gained": total_rp,
        "total_rp": trauma["recovery_points"],
        "rp_threshold": threshold,
        "rp_factors": rp_log,
        "old_stage": old_stage,
        "new_stage": old_stage,
        "events": [],
    }

    # Acute → Active after 7 days automatically
    if old_stage == "acute" and trauma["recovery_day_count"] >= 7:
        trauma["recovery_stage"] = "active"
        result["new_stage"] = "active"
        result["events"].append("Acute phase passed. Condition stabilizes.")

    # Check for stage advancement
    if trauma["recovery_points"] >= threshold and old_stage not in ("residual", "resolved"):
        wil = _get_wil(member)
        check = resolve_check(wil, 0, 0, "trauma_recovery")

        if check.result == ResultLevel.CRITICAL_SUCCESS:
            # Advance two stages
            stage_idx = RECOVERY_STAGES.index(trauma["recovery_stage"])
            new_idx = min(len(RECOVERY_STAGES) - 1, stage_idx + 2)
            trauma["recovery_stage"] = RECOVERY_STAGES[new_idx]
            trauma["recovery_points"] = 0
            profile = _ensure_profile(member)
            profile["tsp"] = max(0, profile.get("tsp", 0) - 2)

            if trauma["recovery_stage"] == "resolved":
                trauma["resolved"] = True
                result["events"].append(
                    "Breakthrough recovery. The condition resolves."
                )
            else:
                # Severity drops with stage
                sev_idx = SEVERITY_ORDER.index(severity)
                if sev_idx > 1:
                    trauma["severity"] = SEVERITY_ORDER[sev_idx - 1]
                result["events"].append(
                    f"Strong recovery. Advances to "
                    f"{trauma['recovery_stage']}. TSP reduced by 2."
                )

        elif check.result == ResultLevel.SUCCESS:
            stage_idx = RECOVERY_STAGES.index(trauma["recovery_stage"])
            new_idx = min(len(RECOVERY_STAGES) - 1, stage_idx + 1)
            trauma["recovery_stage"] = RECOVERY_STAGES[new_idx]
            trauma["recovery_points"] = 0

            if trauma["recovery_stage"] == "resolved":
                trauma["resolved"] = True
                result["events"].append("The condition resolves.")
            elif trauma["recovery_stage"] == "easing":
                sev_idx = SEVERITY_ORDER.index(severity)
                if sev_idx > 1:
                    trauma["severity"] = SEVERITY_ORDER[sev_idx - 1]
                result["events"].append(
                    f"Advances to easing. Severity drops to "
                    f"{trauma['severity']}."
                )
            else:
                result["events"].append(
                    f"Advances to {trauma['recovery_stage']}."
                )

        elif check.result == ResultLevel.CRITICAL_FAILURE:
            # Relapse
            sev_idx = SEVERITY_ORDER.index(severity)
            new_sev = SEVERITY_ORDER[min(len(SEVERITY_ORDER) - 1, sev_idx + 1)]
            trauma["severity"] = new_sev
            trauma["recovery_points"] = 0
            trauma["recovery_stage"] = "acute"
            result["events"].append(
                f"Relapse. Severity worsens to {new_sev}. "
                f"Recovery resets."
            )
        else:
            # Failure: RP resets to 75% of threshold
            trauma["recovery_points"] = int(threshold * 0.75)
            result["events"].append(
                f"Recovery check fails. RP reduced to "
                f"{trauma['recovery_points']}/{threshold}."
            )

        result["recovery_check"] = check.to_dict()

    result["new_stage"] = trauma["recovery_stage"]
    result["severity"] = trauma["severity"]

    # WIL degradation check
    _check_wil_degradation(member, trauma)

    result["message"] = (
        f"{member['name']}'s {trauma['condition'].replace('_', ' ')}: "
        f"+{total_rp:.0f} RP ({trauma['recovery_points']:.0f}/"
        f"{threshold}). Stage: {trauma['recovery_stage']}."
    )

    return result


def trauma_worsen(
    member: dict,
    trauma_id: str,
    new_severity: str,
    cause: str = "",
    tsp_added: int = 0,
) -> dict:
    """Increase trauma severity."""
    trauma = _find_trauma(member, trauma_id)
    if not trauma:
        return {"error": f"Trauma {trauma_id} not found on {member['name']}."}

    old_severity = trauma["severity"]
    old_idx = SEVERITY_ORDER.index(old_severity)
    new_idx = SEVERITY_ORDER.index(new_severity)
    if new_idx <= old_idx:
        return {"error": f"New severity must be worse than {old_severity}."}

    trauma["severity"] = new_severity
    trauma["recovery_stage"] = "acute"
    trauma["recovery_points"] = 0
    trauma["recovery_day_count"] = 0

    if tsp_added > 0:
        profile = _ensure_profile(member)
        profile["tsp"] = profile.get("tsp", 0) + tsp_added

    if new_severity == "crippling":
        profile = _ensure_profile(member)
        profile["will_damage"]["permanent"] = \
            profile["will_damage"].get("permanent", 0) + 1
        profile["stress_threshold"] = _get_wil(member) * 3

    _update_baseline(member, trauma["condition"], new_severity)

    desc = CONDITION_DESCRIPTIONS.get(
        trauma["condition"], {},
    ).get(new_severity, "")

    return {
        "trauma_id": trauma_id,
        "old_severity": old_severity,
        "new_severity": new_severity,
        "cause": cause,
        "description": desc,
        "message": (
            f"{member['name']}'s {trauma['condition'].replace('_', ' ')} "
            f"worsens to {new_severity}. {cause}"
        ),
    }


def trauma_improve(
    member: dict,
    trauma_id: str,
    new_severity: str,
    cause: str = "",
) -> dict:
    """Decrease trauma severity."""
    trauma = _find_trauma(member, trauma_id)
    if not trauma:
        return {"error": f"Trauma {trauma_id} not found on {member['name']}."}

    old_severity = trauma["severity"]
    old_idx = SEVERITY_ORDER.index(old_severity)
    new_idx = SEVERITY_ORDER.index(new_severity)
    if new_idx >= old_idx:
        return {"error": f"New severity must be better than {old_severity}."}

    trauma["severity"] = new_severity
    _update_baseline(member, trauma["condition"], new_severity)

    desc = CONDITION_DESCRIPTIONS.get(
        trauma["condition"], {},
    ).get(new_severity, "")

    return {
        "trauma_id": trauma_id,
        "old_severity": old_severity,
        "new_severity": new_severity,
        "cause": cause,
        "description": desc,
        "message": (
            f"{member['name']}'s {trauma['condition'].replace('_', ' ')} "
            f"improves to {new_severity}. {cause}"
        ),
    }


def trauma_resolve(
    member: dict,
    trauma_id: str,
    residual: str = "",
    tsp_reduction: int = 0,
) -> dict:
    """Mark a trauma condition as resolved."""
    trauma = _find_trauma(member, trauma_id)
    if not trauma:
        return {"error": f"Trauma {trauma_id} not found on {member['name']}."}

    trauma["resolved"] = True
    trauma["recovery_stage"] = "resolved"
    trauma["residual"] = residual or None

    profile = _ensure_profile(member)
    if tsp_reduction > 0:
        profile["tsp"] = max(0, profile.get("tsp", 0) - tsp_reduction)

    # Count recovery
    profile["resilience_factors"]["prior_recoveries"] = \
        profile["resilience_factors"].get("prior_recoveries", 0) + 1

    # Recalculate baseline
    _recalculate_baseline(member)

    return {
        "trauma_id": trauma_id,
        "resolved": True,
        "residual": residual,
        "tsp_after": profile["tsp"],
        "message": (
            f"{member['name']}'s {trauma['condition'].replace('_', ' ')} "
            f"resolves. {residual}" if residual else
            f"{member['name']}'s {trauma['condition'].replace('_', ' ')} "
            f"resolves."
        ),
    }


def trauma_add_condition(
    member: dict,
    condition: str,
    severity: str,
    source: str = "",
    triggers: list[str] | None = None,
    current_day: int = 0,
) -> dict:
    """Manually add a trauma condition (backstory, manual events)."""
    if condition not in CONDITION_TYPES:
        return {"error": f"Unknown condition: {condition}"}
    if severity not in SEVERITY_ORDER[1:]:
        return {"error": f"Invalid severity: {severity}"}

    profile = _ensure_profile(member)
    tid = generate_trauma_id(member)

    if triggers is None:
        # Derive from condition type
        for cat, conds in CATEGORY_CONDITIONS.items():
            if condition in conds:
                triggers = DEFAULT_TRIGGERS.get(cat, [])[:3]
                break
        if triggers is None:
            triggers = []

    trauma_record = {
        "id": tid,
        "condition": condition,
        "source_event": source,
        "source_day": current_day,
        "severity": severity,
        "tsp_at_onset": profile.get("tsp", 0),
        "triggers": triggers,
        "manifestation": "chronic",
        "recovery_stage": "active",
        "recovery_day_count": 0,
        "recovery_points": 0,
        "will_cost": 0,
        "resolved": False,
        "residual": None,
    }
    profile["trauma_conditions"].append(trauma_record)
    _update_baseline(member, condition, severity)

    desc = CONDITION_DESCRIPTIONS.get(condition, {}).get(severity, "")

    return {
        "trauma_id": tid,
        "condition": condition,
        "severity": severity,
        "source": source,
        "triggers": triggers,
        "description": desc,
        "message": (
            f"Added {condition.replace('_', ' ')} ({severity}) to "
            f"{member['name']}. {desc}"
        ),
    }


def profile_update(member: dict) -> dict:
    """Recalculate full psychological profile."""
    profile = _ensure_profile(member)

    # Update stress threshold
    wil = _get_wil(member)
    profile["stress_threshold"] = wil * 3

    active = _active_conditions(member)
    _recalculate_baseline(member)

    # Compute overall state
    if not active:
        state = "stable"
    else:
        worst = max(
            active,
            key=lambda t: SEVERITY_ORDER.index(t["severity"]),
        )
        state = f"compromised ({worst['condition']}: {worst['severity']})"

    return {
        "name": member["name"],
        "effective_wil": wil,
        "tsp": profile["tsp"],
        "stress_threshold": profile["stress_threshold"],
        "active_conditions": len(active),
        "state": state,
        "behavioral_baseline": profile["behavioral_baseline"],
        "will_damage": profile["will_damage"],
        "resilience": profile["resilience_factors"],
    }


# ───────────────────────────────────────────────────────────────────────
# Status / Roster
# ───────────────────────────────────────────────────────────────────────

def member_trauma_status(member: dict) -> dict:
    """Full psychological status report."""
    profile = _ensure_profile(member)
    active = _active_conditions(member)
    resolved = [
        t for t in profile.get("trauma_conditions", []) if t.get("resolved")
    ]

    wil = _get_wil(member)
    condition_details = []
    for t in active:
        desc = CONDITION_DESCRIPTIONS.get(
            t["condition"], {},
        ).get(t["severity"], "")
        condition_details.append({
            "id": t["id"],
            "condition": t["condition"],
            "severity": t["severity"],
            "recovery_stage": t["recovery_stage"],
            "triggers": t["triggers"],
            "recovery_points": t.get("recovery_points", 0),
            "rp_threshold": RECOVERY_RP_THRESHOLD.get(t["severity"], 30),
            "description": desc,
        })

    return {
        "name": member["name"],
        "effective_wil": wil,
        "tsp": profile["tsp"],
        "stress_threshold": profile["stress_threshold"],
        "active_conditions": condition_details,
        "resolved_conditions": len(resolved),
        "behavioral_baseline": profile["behavioral_baseline"],
        "will_damage": profile["will_damage"],
        "resilience": profile["resilience_factors"],
        "trauma_history_count": len(profile.get("trauma_history", [])),
    }


def roster_trauma(band: dict) -> list[dict]:
    """Get trauma summary for all band members."""
    results = []
    for m in band.get("members", []):
        if m.get("status") == "dead":
            continue
        profile = m.get("psychological_profile")
        if not profile:
            continue
        active = [
            t for t in profile.get("trauma_conditions", [])
            if not t.get("resolved")
        ]
        if active or profile.get("tsp", 0) > 0:
            wil = _get_wil(m)
            results.append({
                "name": m["name"],
                "effective_wil": wil,
                "tsp": f"{profile['tsp']}/{profile['stress_threshold']}",
                "active_conditions": len(active),
                "conditions": [
                    f"{t['id']}: {t['condition']} ({t['severity']}, "
                    f"{t['recovery_stage']})"
                    for t in active
                ],
                "will_damage": profile.get("will_damage", {}),
            })
    return results


# ───────────────────────────────────────────────────────────────────────
# Band-level helpers
# ───────────────────────────────────────────────────────────────────────

def advance_all_trauma(
    band: dict,
    days: int,
    rest_quality: str = "field_rest",
    dalla_care: bool = False,
    fire_inclusion: bool = True,
) -> list[dict]:
    """Advance recovery for all active trauma conditions."""
    all_events = []
    for m in band.get("members", []):
        if m.get("status") == "dead":
            continue
        profile = m.get("psychological_profile")
        if not profile:
            continue
        for t in profile.get("trauma_conditions", []):
            if t.get("resolved"):
                continue
            # Check shield-brother presence
            sb = profile.get("resilience_factors", {}).get("shield_bond")
            sb_present = False
            if sb:
                sb_member = _find_member_in_band(band, sb)
                sb_present = sb_member is not None and \
                    sb_member.get("status") not in ("dead", "deserted")

            result = trauma_recover(
                m, t["id"], days,
                rest_quality=rest_quality,
                shield_brother_present=sb_present,
                dalla_care=dalla_care,
                fire_inclusion=fire_inclusion,
            )
            if result.get("events"):
                result["member"] = m["name"]
                all_events.append(result)
    return all_events


def _find_member_in_band(band: dict, name: str) -> dict | None:
    """Find member by name."""
    for m in band.get("members", []):
        if m["name"].lower() == name.lower():
            return m
    return None


# ───────────────────────────────────────────────────────────────────────
# Internal helpers
# ───────────────────────────────────────────────────────────────────────

def _find_trauma(member: dict, trauma_id: str) -> dict | None:
    """Find a trauma record by ID."""
    profile = _ensure_profile(member)
    for t in profile.get("trauma_conditions", []):
        if t.get("id") == trauma_id:
            return t
    return None


def _select_condition(member: dict, category: str) -> str:
    """Select which condition manifests based on category and character."""
    options = CATEGORY_CONDITIONS.get(category, CONDITION_TYPES[:3])

    # Avoid duplicating existing active conditions
    active_types = {t["condition"] for t in _active_conditions(member)}
    available = [c for c in options if c not in active_types]
    if not available:
        available = options  # allow duplicates if all options exhausted

    # Weight by character traits
    wil = _get_wil(member)
    if wil >= 6:
        # High WIL: more likely internalized conditions
        internalized = ["withdrawal", "killing_calm", "heavy_mind", "mind_flight"]
        weighted = [c for c in available if c in internalized] or available
    else:
        # Low WIL: more likely externalized conditions
        externalized = ["battle_shock", "anger_storm", "drink_need", "flinch_sickness"]
        weighted = [c for c in available if c in externalized] or available

    return random.choice(weighted)


def _overshoot_to_severity(overshoot: int) -> str:
    """Map TSP overshoot to condition severity."""
    if overshoot <= 3:
        return "mild"
    elif overshoot <= 8:
        return "moderate"
    elif overshoot <= 15:
        return "severe"
    else:
        return "crippling"


def _select_triggers(category: str) -> list[str]:
    """Select 2-3 triggers from the category defaults."""
    all_triggers = DEFAULT_TRIGGERS.get(category, ["sudden_sounds"])
    count = min(len(all_triggers), random.randint(2, 3))
    return random.sample(all_triggers, count)


def _update_baseline(member: dict, condition: str, severity: str):
    """Update behavioral baseline based on active condition."""
    profile = _ensure_profile(member)
    baseline = profile["behavioral_baseline"]

    sev_idx = SEVERITY_ORDER.index(severity)

    if condition in ("withdrawal", "heavy_mind", "grief_lock"):
        if sev_idx >= 2:
            baseline["social_engagement"] = "minimal"
            baseline["speech_pattern"] = "monosyllabic"
        if sev_idx >= 3:
            baseline["appetite"] = "poor"
    elif condition in ("night_terrors", "flinch_sickness"):
        baseline["sleep_quality"] = "poor" if sev_idx >= 2 else "restless"
    elif condition == "drink_need":
        baseline["drinking_level"] = (
            "heavy" if sev_idx >= 3 else
            "functional" if sev_idx >= 2 else "increased"
        )
    elif condition == "anger_storm":
        baseline["speech_pattern"] = "volatile" if sev_idx >= 2 else "terse"
    elif condition == "killing_calm":
        baseline["social_engagement"] = "distant"
        baseline["speech_pattern"] = "flat"


def _recalculate_baseline(member: dict):
    """Recalculate baseline from all active conditions."""
    profile = _ensure_profile(member)
    # Reset to default
    profile["behavioral_baseline"] = {
        "speech_pattern": "normal",
        "sleep_quality": "normal",
        "appetite": "normal",
        "social_engagement": "normal",
        "drinking_level": "social",
    }
    # Apply worst of each
    for t in _active_conditions(member):
        _update_baseline(member, t["condition"], t["severity"])


def _check_wil_degradation(member: dict, trauma: dict):
    """Check and apply WIL degradation from unresolved trauma."""
    profile = _ensure_profile(member)
    days = trauma.get("recovery_day_count", 0)

    for threshold_days, damage_type, amount in WIL_DEGRADATION:
        if days >= threshold_days:
            if damage_type == "permanent":
                # Only apply once per 90-day period
                periods = days // 90
                current_perm = profile["will_damage"].get("permanent", 0)
                if current_perm < periods:
                    profile["will_damage"]["permanent"] = periods
                    profile["stress_threshold"] = _get_wil(member) * 3
            else:
                profile["will_damage"]["temporary"] = max(
                    profile["will_damage"].get("temporary", 0),
                    abs(amount),
                )
            break


# ───────────────────────────────────────────────────────────────────────
# CLI
# ───────────────────────────────────────────────────────────────────────

def _load_band(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_band(band: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(band, f, indent=2, ensure_ascii=False)


def _find_member(band: dict, name: str) -> dict | None:
    for m in band.get("members", []):
        if m["name"].lower() == name.lower():
            return m
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Hugr Ledger — Psychological Trauma System",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview mutations without writing band file",
    )
    sub = parser.add_subparsers(dest="command", help="Command to run")

    # ── apply ──
    p = sub.add_parser("apply", help="Apply traumatic event")
    p.add_argument("--band-file", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--event", required=True)
    p.add_argument("--category", required=True,
                   choices=list(TSP_BASE.keys()))
    p.add_argument("--tsp", type=int, default=0)
    p.add_argument("--shield-bond", action="store_true")
    p.add_argument("--chronic-pain", action="store_true")
    p.add_argument("--first-exposure", action="store_true")
    p.add_argument("--drunk", action="store_true")
    p.add_argument("--save", action="store_true")
    p.add_argument("--json", action="store_true")

    # ── trigger ──
    p = sub.add_parser("trigger", help="Fire trigger check")
    p.add_argument("--band-file", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--trauma-id", required=True)
    p.add_argument("--trigger", required=True)
    p.add_argument("--context", default="non_combat",
                   choices=["combat", "non_combat"])
    p.add_argument("--shield-brother", action="store_true")
    p.add_argument("--dalla", action="store_true")
    p.add_argument("--at-fire", action="store_true")
    p.add_argument("--drunk-level", default="sober",
                   choices=["sober", "moderate", "heavy"])
    p.add_argument("--fatigued", action="store_true")
    p.add_argument("--in-pain", action="store_true")
    p.add_argument("--night", action="store_true")
    p.add_argument("--alone", action="store_true")
    p.add_argument("--save", action="store_true")
    p.add_argument("--json", action="store_true")

    # ── recover ──
    p = sub.add_parser("recover", help="Advance recovery")
    p.add_argument("--band-file", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--trauma-id", required=True)
    p.add_argument("--days", type=int, required=True)
    p.add_argument("--rest", default="field_rest",
                   choices=list(RP_RATES.keys()))
    p.add_argument("--meaningful-work", action="store_true")
    p.add_argument("--shield-brother", action="store_true")
    p.add_argument("--dalla", action="store_true")
    p.add_argument("--saga-told", action="store_true")
    p.add_argument("--fire", action="store_true", default=True)
    p.add_argument("--triggers-today", type=int, default=0)
    p.add_argument("--new-trauma", action="store_true")
    p.add_argument("--drunk", action="store_true")
    p.add_argument("--isolation", action="store_true")
    p.add_argument("--save", action="store_true")
    p.add_argument("--json", action="store_true")

    # ── worsen ──
    p = sub.add_parser("worsen", help="Worsen trauma")
    p.add_argument("--band-file", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--trauma-id", required=True)
    p.add_argument("--new-severity", required=True,
                   choices=SEVERITY_ORDER[1:])
    p.add_argument("--cause", default="")
    p.add_argument("--tsp-added", type=int, default=0)
    p.add_argument("--save", action="store_true")
    p.add_argument("--json", action="store_true")

    # ── improve ──
    p = sub.add_parser("improve", help="Improve trauma")
    p.add_argument("--band-file", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--trauma-id", required=True)
    p.add_argument("--new-severity", required=True,
                   choices=SEVERITY_ORDER[1:])
    p.add_argument("--cause", default="")
    p.add_argument("--save", action="store_true")
    p.add_argument("--json", action="store_true")

    # ── resolve ──
    p = sub.add_parser("resolve", help="Resolve trauma")
    p.add_argument("--band-file", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--trauma-id", required=True)
    p.add_argument("--residual", default="")
    p.add_argument("--tsp-reduction", type=int, default=0)
    p.add_argument("--save", action="store_true")
    p.add_argument("--json", action="store_true")

    # ── add ──
    p = sub.add_parser("add", help="Add condition manually")
    p.add_argument("--band-file", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--condition", required=True,
                   choices=CONDITION_TYPES)
    p.add_argument("--severity", required=True,
                   choices=SEVERITY_ORDER[1:])
    p.add_argument("--source", default="")
    p.add_argument("--triggers", nargs="*", default=None)
    p.add_argument("--save", action="store_true")
    p.add_argument("--json", action="store_true")

    # ── status ──
    p = sub.add_parser("status", help="Psychological status")
    p.add_argument("--band-file", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--json", action="store_true")

    # ── roster ──
    p = sub.add_parser("roster", help="All members with trauma")
    p.add_argument("--band-file", required=True)
    p.add_argument("--json", action="store_true")

    # ── advance ──
    p = sub.add_parser("advance", help="Advance all recovery")
    p.add_argument("--band-file", required=True)
    p.add_argument("--days", type=int, required=True)
    p.add_argument("--rest", default="field_rest",
                   choices=list(RP_RATES.keys()))
    p.add_argument("--dalla", action="store_true")
    p.add_argument("--fire", action="store_true", default=True)
    p.add_argument("--save", action="store_true")
    p.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    band = _load_band(args.band_file)

    # Commands requiring a target
    member = None
    if args.command in ("apply", "trigger", "recover", "worsen",
                        "improve", "resolve", "add", "status"):
        member = _find_member(band, args.target)
        if not member:
            print(f"Error: '{args.target}' not found.", file=sys.stderr)
            sys.exit(1)

    if args.command == "apply":
        result = trauma_apply(
            member, args.event, args.category, tsp=args.tsp,
            current_day=band.get("day_of_year", 0),
            shield_bond_active=args.shield_bond,
            chronic_pain=args.chronic_pain,
            first_exposure=args.first_exposure,
            drunk=args.drunk,
            wyr=member.get("wyr", member.get("attributes", {}).get("wyr", 1)),
        )
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result.get("message", ""))

    elif args.command == "trigger":
        result = trauma_trigger(
            member, args.trauma_id, args.trigger,
            context=args.context,
            shield_brother_nearby=args.shield_brother,
            dalla_present=args.dalla,
            at_fire=args.at_fire,
            drunk_level=args.drunk_level,
            fatigued=args.fatigued,
            in_pain=args.in_pain,
            night=args.night,
            alone=args.alone,
        )
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result.get("message", ""))

    elif args.command == "recover":
        result = trauma_recover(
            member, args.trauma_id, args.days,
            rest_quality=args.rest,
            meaningful_work=args.meaningful_work,
            shield_brother_present=args.shield_brother,
            dalla_care=args.dalla,
            saga_told=args.saga_told,
            fire_inclusion=args.fire,
            trigger_events_today=args.triggers_today,
            new_trauma_this_week=args.new_trauma,
            drunk=args.drunk,
            isolation=args.isolation,
        )
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result.get("message", ""))
            for e in result.get("events", []):
                print(f"  {e}")

    elif args.command == "worsen":
        result = trauma_worsen(
            member, args.trauma_id, args.new_severity,
            cause=args.cause, tsp_added=args.tsp_added,
        )
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result.get("message", ""))

    elif args.command == "improve":
        result = trauma_improve(
            member, args.trauma_id, args.new_severity, cause=args.cause)
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result.get("message", ""))

    elif args.command == "resolve":
        result = trauma_resolve(
            member, args.trauma_id,
            residual=args.residual,
            tsp_reduction=args.tsp_reduction,
        )
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result.get("message", ""))

    elif args.command == "add":
        result = trauma_add_condition(
            member, args.condition, args.severity,
            source=args.source, triggers=args.triggers,
            current_day=band.get("day_of_year", 0),
        )
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result.get("message", ""))

    elif args.command == "status":
        result = member_trauma_status(member)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"=== {result['name']} — Psychological Profile ===")
            print(f"Effective WIL: {result['effective_wil']}")
            print(f"TSP: {result['tsp']}/{result['stress_threshold']}")
            wd = result["will_damage"]
            print(f"WIL damage: temp {wd.get('temporary', 0)}, "
                  f"perm {wd.get('permanent', 0)}")
            bl = result["behavioral_baseline"]
            print(f"Baseline: sleep={bl['sleep_quality']}, "
                  f"appetite={bl['appetite']}, "
                  f"social={bl['social_engagement']}, "
                  f"drinking={bl['drinking_level']}")
            for c in result["active_conditions"]:
                print(f"  {c['id']}: {c['condition']} ({c['severity']}, "
                      f"{c['recovery_stage']}) — "
                      f"RP {c['recovery_points']}/{c['rp_threshold']}")
                if c.get("description"):
                    print(f"    {c['description']}")

    elif args.command == "roster":
        results = roster_trauma(band)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            if not results:
                print("No trauma recorded.")
            for r in results:
                wd = r["will_damage"]
                print(f"{r['name']}: TSP {r['tsp']} | "
                      f"WIL damage: t{wd.get('temporary', 0)} "
                      f"p{wd.get('permanent', 0)}")
                for c in r["conditions"]:
                    print(f"  {c}")

    elif args.command == "advance":
        events = advance_all_trauma(
            band, args.days, args.rest,
            dalla_care=args.dalla,
            fire_inclusion=args.fire,
        )
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(events, indent=2))
        else:
            if not events:
                print(f"Advanced {args.days} days. No recovery changes.")
            for e in events:
                name = e.get("member", "?")
                tid = e.get("trauma_id", "?")
                for ev in e.get("events", []):
                    print(f"  {name} [{tid}]: {ev}")


if __name__ == "__main__":
    main()
