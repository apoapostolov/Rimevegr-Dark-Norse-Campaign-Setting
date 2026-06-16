#!/usr/bin/env python3
"""
Iron Ledger — Life Skills Classifier

Determines whether an action requires a check, and generates the appropriate
engine check if one is needed. Implements §17 of 20_SIMULATION_RULES.md.

Every band member carries baseline competence. Specialist knowledge grants
automatic success within a domain under normal conditions. This script
classifies actions and routes to the correct engine check only when needed.

Usage:
    python life_skills.py classify --action light_fire --conditions wet
    python life_skills.py classify --action set_bone --specialist-domains Heal
    python life_skills.py check --action navigate_overcast --attr 5 --skill 2
    python life_skills.py domains
    python life_skills.py baseline
"""

import argparse
import json
import sys

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import resolve_check, ResultLevel
from animal_system import dog_support_profile, horse_charge_profile


# ─── §17: Baseline actions (no check required in normal conditions) ───────────

BASELINE_ACTIONS = {
    "light_fire":           "Light a fire in dry conditions.",
    "sharpen_weapons":      "Sharpen own weapons and perform basic maintenance.",
    "dress_wound_basic":    "Dress a wound with cloth and pressure (first aid only).",
    "tie_knots":            "Tie functional knots: rigging, loads, snares.",
    "set_camp_basic":       "Set a basic camp: shelter, fire, latrine.",
    "read_weather_6h":      "Read weather within the next six hours.",
    "cook_meat":            "Cook meat over fire without poisoning himself.",
    "fix_seam_boot":        "Fix a torn seam or split boot (cosmetic only).",
    "navigate_clear":       "Navigate by sun and pole star in clear conditions.",
    "estimate_distance":    "Estimate distance and travel time on known terrain.",
}

# ─── §17: Specialist domains → governing skills ───────────────────────────────

SPECIALIST_DOMAINS = {
    "cooking_healing": {
        "skills":       ["Heal", "Forage"],
        "examples":     ["Dalla"],
        "description":  "Set bones, mix medicines, preserve food, spot spoilage.",
    },
    "hunting_tracking": {
        "skills":       ["Track", "Forage"],
        "examples":     ["Thorne", "Petra"],
        "description":  "Read three-day-old trails, call game, read spoor.",
    },
    "quartermastery": {
        "skills":       ["Bargain", "Weather-sense"],
        "examples":     ["Gest"],
        "description":  "Detect short-weight goods, estimate spoilage, manage stores.",
    },
    "rune_craft": {
        "skills":       ["Rune-lore"],
        "examples":     ["Thorne"],
        "description":  "Identify rune-stones, inscribe marks, read ancient inscriptions.",
    },
    "woodcraft": {
        "skills":       ["Woodcraft", "Shelter"],
        "examples":     ["Any with Shelter 2+"],
        "description":  "Build shelters, assess timber, carve tools.",
    },
    "trapping": {
        "skills":       ["Forage", "Track"],
        "examples":     ["Any with Forage 2+"],
        "description":  "Set and read snares, pit traps, deadfalls.",
    },
    "seamanship": {
        "skills":       ["Seamanship"],
        "examples":     ["Any with Seamanship"],
        "description":  "Navigate by sea, read currents, manage a ship under sail.",
    },
    "trading": {
        "skills":       ["Bargain", "Sagas"],
        "examples":     ["Gest"],
        "description":  "Spot a bad deal, read a merchant's motives, haggle effectively.",
    },
    "war_leadership": {
        "skills":       ["Command", "Shields"],
        "examples":     ["Voss", "Petra"],
        "description":  "Order a shield wall, read a battle, coordinate flanking.",
    },
    "scouting": {
        "skills":       ["Track", "Navigate"],
        "examples":     ["Thorne"],
        "description":  "Move unseen, count enemy strength, find paths.",
    },
    "brewing_chemistry": {
        "skills":       ["Forage", "Heal"],
        "examples":     ["Dalla"],
        "description":  "Brew mead, prepare poultices, identify plants and fungi.",
    },
}

# ─── §17: Action difficulty table ────────────────────────────────────────────
# "baseline"   → no check unless conditions are extreme
# "specialist" → no check if character has domain, check otherwise
# "standard"   → Wits or relevant skill check
# "hard"       → -20 modifier applied
# "impossible" → no check; requires specialist or cannot be done

ACTION_RULES = {
    # Baseline actions in stressed/hostile conditions
    "light_fire":            {"normal": "baseline",   "wet": "standard",    "blizzard": "hard"},
    "dress_wound_basic":     {"normal": "baseline",   "combat": "standard", "blizzard": "hard"},
    "tie_knots":             {"normal": "baseline",   "combat": "hard",     "cold": "standard"},
    "set_camp_basic":        {"normal": "baseline",   "blizzard": "hard",   "night": "standard"},
    "read_weather_6h":       {"normal": "baseline",   "night": "standard"},
    "navigate_clear":        {"normal": "baseline",   "overcast": "standard", "forest": "standard",
                              "blizzard": "hard"},
    "cook_meat":             {"normal": "baseline",   "no_fire": "hard"},
    "fix_seam_boot":         {"normal": "baseline",   "no_tools": "hard"},
    "estimate_distance":     {"normal": "baseline",   "unfamiliar_terrain": "standard"},

    # Specialist actions
    "set_bone":              {"normal": "impossible", "specialist_Heal": "standard"},
    "read_runes":            {"normal": "impossible", "specialist_Rune-lore": "baseline"},
    "navigate_overcast":     {"normal": "standard",   "specialist_Navigate": "baseline"},
    "navigate_stars":        {"normal": "hard",       "specialist_Navigate": "standard"},
    "identify_spoilage":     {"normal": "standard",   "specialist_Forage": "baseline"},
    "read_trail_3days":      {"normal": "impossible", "specialist_Track": "standard"},
    "call_game":             {"normal": "hard",       "specialist_Forage": "standard"},
    "brew_medicine":         {"normal": "impossible", "specialist_Heal": "standard"},
    "set_snare":             {"normal": "standard",   "specialist_Forage": "baseline"},
    "identify_fungi_plants": {"normal": "hard",       "specialist_Forage": "standard",
                              "specialist_Heal": "standard"},
    "repair_structural":     {"normal": "hard",       "specialist_Woodcraft": "standard"},
    "read_merchant_intent":  {"normal": "hard",       "specialist_Bargain": "standard"},
    "spot_short_weight":     {"normal": "hard",       "specialist_Bargain": "baseline"},
    "order_shield_wall":     {"normal": "impossible", "specialist_Command": "standard"},
    "count_enemy_strength":  {"normal": "standard",   "specialist_Track": "baseline"},
    "navigate_by_sea":       {"normal": "impossible", "specialist_Seamanship": "standard"},
}

# Skill → attribute mapping for when we need to resolve a check
SKILL_ATTR_MAP = {
    "Heal":        "Wits",
    "Forage":      "Wits",
    "Track":       "Wits",
    "Navigate":    "Wits",
    "Bargain":     "Wits",
    "Weather-sense": "Wits",
    "Rune-lore":   "Wyrd",
    "Woodcraft":   "Nimbleness",
    "command":     "Will",
    "Command":     "Will",
    "Shields":     "Might",
    "Sagas":       "Wits",
    "Seamanship":  "Nimbleness",
    "Shelter":     "Wits",
}

DIFFICULTY_MODIFIERS = {
    "baseline":  None,  # no check
    "standard":  0,
    "hard":      -20,
    "impossible": None,  # block
}


def classify_action(action: str, conditions: list[str],
                    specialist_domains: list[str]) -> dict:
    """
    Classify an action as baseline/standard/hard/impossible given conditions
    and the character's specialist domains.

    conditions: list of condition keywords (e.g. ["wet", "combat"])
    specialist_domains: list of skill names the character specialises in
                        (e.g. ["Heal", "Track"])
    """
    if action not in ACTION_RULES:
        return {
            "action": action,
            "classification": "unknown",
            "note": "Action not in Life Skills table. Use engine.py check directly.",
        }

    rules = ACTION_RULES[action]

    # Build effective condition key — prefer specialist match first
    effective_key = "normal"
    specialist_matches = []
    for domain in specialist_domains:
        key = f"specialist_{domain}"
        if key in rules:
            specialist_matches.append((key, rules[key]))

    for cond in conditions:
        if cond in rules:
            effective_key = cond
            break

    # Specialist always wins if it loosens the requirement
    difficulty_order = ["impossible", "hard", "standard", "baseline"]
    best_classification = rules.get(effective_key, rules.get("normal", "standard"))
    for sp_key, sp_class in specialist_matches:
        if difficulty_order.index(sp_class) > difficulty_order.index(best_classification):
            best_classification = sp_class

    notes = []
    if best_classification == "impossible":
        notes.append("Requires specialist knowledge. Cannot be attempted by a layman.")
    elif best_classification == "baseline":
        notes.append("No check required under these conditions.")
    elif best_classification == "hard":
        notes.append("-20 modifier to the check.")
    if specialist_matches:
        notes.append(f"Specialist advantage from: {', '.join(d for _, d in specialist_matches)}.")

    return {
        "action": action,
        "conditions": conditions,
        "specialist_domains_held": specialist_domains,
        "classification": best_classification,
        "modifier": DIFFICULTY_MODIFIERS.get(best_classification, 0),
        "notes": notes,
    }


def generate_check(action: str, conditions: list[str],
                   specialist_domains: list[str],
                   attr: int, skill: int,
                   extra_mods: int = 0,
                   horse: dict | None = None,
                   dogs: list[dict] | None = None) -> dict:
    """
    Classify the action and, if a check is needed, resolve it via engine.
    Returns classification plus CheckResult if a roll was made.
    """
    classification = classify_action(action, conditions, specialist_domains)
    mod = classification.get("modifier")

    if mod is None:
        return {**classification, "check": None,
                "resolution": "no_roll_needed" if classification["classification"] == "baseline"
                              else "blocked_no_specialist"}

    animal_mod = 0
    if action in {"read_trail_3days", "count_enemy_strength", "navigate_overcast"}:
        animal_mod += dog_support_profile(dogs).get("tracking_bonus", 0)
    if action in {"navigate_overcast", "navigate_stars"} and horse:
        animal_mod += int(horse_charge_profile(type("HorseProxy", (), {
            "mount_traits": horse.get("traits", []),
            "mount_tricks": horse.get("tricks", []),
            "mount_mood": horse.get("mood", "calm"),
            "mount_condition": horse.get("condition", "steady"),
        })()).get("tight_attack_mod", 0))
    total_mod = mod + extra_mods + animal_mod
    result = resolve_check(attr, skill, total_mod)

    return {
        **classification,
        "check": result.to_dict(),
        "resolution": result.result.value,
        "animal_modifier": animal_mod,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Iron Ledger — Life Skills Classifier (§17)"
    )
    sub = parser.add_subparsers(dest="cmd")

    # classify
    p = sub.add_parser("classify", help="Classify an action's difficulty")
    p.add_argument("--action",   required=True, help="Action name (see 'baseline' for list)")
    p.add_argument("--conditions", nargs="*", default=[],
                   help="Active conditions (wet, blizzard, combat, overcast, ...)")
    p.add_argument("--specialist-domains", nargs="*", default=[],
                   dest="specialist_domains",
                   help="Character's specialist skill domains (Heal, Track, ...)")
    p.add_argument("--json", action="store_true")

    # check (classify + roll)
    p = sub.add_parser("check", help="Classify and resolve a check if needed")
    p.add_argument("--action",   required=True)
    p.add_argument("--attr",     type=int, required=True, help="Relevant attribute (1-10)")
    p.add_argument("--skill",    type=int, default=0,     help="Relevant skill rank (0-5)")
    p.add_argument("--conditions", nargs="*", default=[])
    p.add_argument("--specialist-domains", nargs="*", default=[],
                   dest="specialist_domains")
    p.add_argument("--mods",     type=int, default=0,     help="Extra situational modifiers")
    p.add_argument("--horse-json", type=str, default=None)
    p.add_argument("--dogs-json", type=str, default=None)
    p.add_argument("--json",     action="store_true")

    # domains
    sub.add_parser("domains", help="List all specialist domains")

    # baseline
    sub.add_parser("baseline", help="List all baseline actions")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    use_json = getattr(args, "json", False)

    if args.cmd == "classify":
        result = classify_action(args.action, args.conditions, args.specialist_domains)
        if use_json:
            print(json.dumps(result, indent=2))
        else:
            _print_classification(result)

    elif args.cmd == "check":
        horse = json.loads(args.horse_json) if args.horse_json else None
        dogs = json.loads(args.dogs_json) if args.dogs_json else None
        result = generate_check(args.action, args.conditions, args.specialist_domains,
                                args.attr, args.skill, args.mods,
                                horse=horse, dogs=dogs)
        if use_json:
            print(json.dumps(result, indent=2))
        else:
            _print_classification(result)
            if result.get("check"):
                chk = result["check"]
                print(f"  Roll: chance={chk['final_chance']}% | "
                      f"roll={chk['roll']} | {chk['result'].upper()}")

    elif args.cmd == "domains":
        for name, data in SPECIALIST_DOMAINS.items():
            print(f"  {name}")
            print(f"    Skills:   {', '.join(data['skills'])}")
            print(f"    Examples: {', '.join(data['examples'])}")
            print(f"    {data['description']}")

    elif args.cmd == "baseline":
        print("Baseline actions (no check in normal conditions):")
        for key, desc in BASELINE_ACTIONS.items():
            print(f"  {key:30s}  {desc}")


def _print_classification(r: dict) -> None:
    level_chars = {
        "baseline":   "✓",
        "standard":   "~",
        "hard":       "!",
        "impossible": "✗",
        "unknown":    "?",
    }
    sym = level_chars.get(r["classification"], "?")
    mod_str = (f"[{r['modifier']:+d}]" if r.get("modifier") is not None else "")
    print(f"\n[{sym}] {r['action']} {mod_str} — {r['classification'].upper()}")
    if r.get("conditions"):
        print(f"    Conditions: {', '.join(r['conditions'])}")
    if r.get("specialist_domains_held"):
        print(f"    Specialist: {', '.join(r['specialist_domains_held'])}")
    for note in r.get("notes", []):
        print(f"    {note}")
    if r.get("resolution") == "blocked_no_specialist":
        print("    → BLOCKED: no specialist in band — cannot attempt.")
    elif r.get("resolution") == "no_roll_needed":
        print("    → No roll needed.")


if __name__ == "__main__":
    main()
