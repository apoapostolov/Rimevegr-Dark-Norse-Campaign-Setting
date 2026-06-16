#!/usr/bin/env python3
"""
Iron Ledger — Recruitment Engine

Generates recruit pools at settlements and handles hiring. Recruit quality
depends on settlement size. Rules from 20_SIMULATION_RULES.md §15.

Usage:
    python recruitment.py pool --settlement village --reputation 2
    python recruitment.py hire --recruit '{"name":"Bjorn","rank":"common","mig":5}'
    python recruitment.py cost --rank veteran --weeks 1
"""

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, __file__ and __import__('os').path.dirname(__file__) or '.')
from engine import roll_sum, roll_d100
from horse_breeding import estimate_horse_value, load_breed_data as load_horse_breeds
from dog_breeding import estimate_dog_value, load_breed_data as load_dog_breeds
from animal_care import ensure_animal_health

# --- Backgrounds ---
BACKGROUNDS = {
    "farmer": {
        "primary_attr": "tou",
        "skills": {"forage": (1, 2), "shelter": (0, 1)},
        "description": "A hardened farmer, used to long hours and cold.",
    },
    "fisher": {
        "primary_attr": "nim",
        "skills": {"seamanship": (1, 2), "forage": (0, 1)},
        "description": "A fisherman with salt in his blood and rope-worn hands.",
    },
    "thrall": {
        "primary_attr": "tou",
        "skills": {"brawl": (0, 1)},
        "description": "A freed thrall, tough and wary, owing nothing.",
        "attr_penalty": True,
    },
    "huscarl": {
        "primary_attr": "mig",
        "skills": {"axes": (1, 3), "shields": (1, 2), "command": (0, 1)},
        "description": "A former house-guard with real combat experience.",
    },
    "wanderer": {
        "primary_attr": "wit",
        "skills": {"navigate": (1, 2), "track": (0, 1), "forage": (0, 1)},
        "description": "A drifter who has walked the Rimevegr end to end.",
    },
    "outlaw": {
        "primary_attr": "nim",
        "skills": {"blades": (1, 2), "deceive": (0, 1), "stealth": (0, 1)},
        "description": "A marked man, quick with a knife and quicker to run.",
    },
}

# --- Settlement Recruit Pool ---
SETTLEMENT_POOLS = {
    "hamlet": {"dice": (1, 4), "max_rank": "common", "veteran_chance": 0},
    "village": {"dice": (2, 4), "max_rank": "veteran", "veteran_chance": 15},
    "large_village": {"dice": (2, 6), "max_rank": "veteran", "veteran_chance": 30},
    "small_town": {"dice": (3, 6), "max_rank": "named_man", "veteran_chance": 45},
}

# --- Wyrd Distribution ---
WYRD_TABLE = [
    (90, 1),    # 90% chance Wyrd 1
    (97, 2),    # 7% chance Wyrd 2
    (99, 3),    # 2.5% chance Wyrd 3
    (100, 4),   # 0.5% chance Wyrd 4+
]

# --- Hiring cost (signing bonus in silver) ---
HIRING_COST = {
    "common": 5,
    "veteran": 15,
    "named_man": 30,
}

# --- Norse Name Lists ---
MALE_NAMES = [
    "Bjorn", "Eirik", "Gunnar", "Halvar", "Ivar", "Kjartan", "Leif",
    "Magnus", "Njall", "Olaf", "Ragnar", "Sigurd", "Thorvald", "Ulf",
    "Vidar", "Yrjar", "Asmund", "Brynjar", "Dagfinn", "Einar",
    "Frode", "Grim", "Harald", "Ingvar", "Jostein", "Ketil",
    "Ljot", "Mord", "Nori", "Orm", "Petur", "Rolf",
    "Snorri", "Torsten", "Ubbe", "Varg", "Yngvar",
]

FEMALE_NAMES = [
    "Astrid", "Brynhild", "Dagny", "Eira", "Freydis", "Gudrun",
    "Halla", "Inga", "Jorunn", "Katla", "Ljufa", "Magnhild",
    "Nessa", "Oddny", "Ragnhild", "Sigrid", "Thora", "Ulfhild",
    "Vigdis", "Ylva", "Asa", "Bergliot", "Dalla",
]

BYNAMES = [
    "the Scarred", "the Quiet", "One-Eye", "Blackhand", "the Red",
    "the Lame", "Ironside", "the Young", "the Old", "Crow-feeder",
    "the Bitter", "the Tall", "Half-troll", "the Lean", "Frostbeard",
    "Skullsplitter", "the Grey", "Oxback", "Shieldbreaker", "the Lucky",
    "the Grim", "Stonefist", "the Wanderer", "the Swift", "Boneless",
]

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
SETTLEMENTS_FILE = DATA_DIR / "settlements.yaml"
HORSE_HERDS_FILE = DATA_DIR / "horse_herds.yaml"
DOG_KENNELS_FILE = DATA_DIR / "dog_kennels.yaml"


def _generate_wyrd() -> int:
    """Generate Wyrd value from distribution table."""
    roll = roll_d100()
    for threshold, value in WYRD_TABLE:
        if roll <= threshold:
            return value
    return 1


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _settlement_size(settlement_name: str) -> str:
    data = _load_yaml(SETTLEMENTS_FILE)
    for settlement in data.get("settlements", []):
        if settlement.get("name", "").lower() == settlement_name.lower():
            return settlement.get("size", "village")
    return "village"


def _available_horse_replacements(settlement_name: str) -> list[dict[str, Any]]:
    if not HORSE_HERDS_FILE.exists():
        return []
    breed_db = load_horse_breeds()
    data = _load_yaml(HORSE_HERDS_FILE)
    candidates = []
    for herd in data.get("horse_herds", []):
        if str(herd.get("owner_name", "")).lower() != settlement_name.lower():
            continue
        for horse in herd.get("horses", []):
            if horse.get("role") in {"stud", "broodmare", "captain_mount", "champion_mount"}:
                continue
            ensure_animal_health(horse, "horse")
            if horse.get("health_status", "sound") in {"dead", "laid_up"}:
                continue
            candidates.append(
                {
                    "species": "horse",
                    "name": horse.get("name"),
                    "breed": horse.get("breed"),
                    "role": horse.get("role"),
                    "health_status": horse.get("health_status", "sound"),
                    "estimated_cost_silver": estimate_horse_value(horse, breed_db),
                    "hp": horse.get("hp"),
                    "max_hp": horse.get("max_hp"),
                }
            )
    return candidates


def _available_dog_replacements(settlement_name: str) -> list[dict[str, Any]]:
    if not DOG_KENNELS_FILE.exists():
        return []
    breed_db = load_dog_breeds()
    data = _load_yaml(DOG_KENNELS_FILE)
    candidates = []
    for kennel in data.get("dog_kennels", []):
        if str(kennel.get("owner_name", "")).lower() != settlement_name.lower():
            continue
        for dog in kennel.get("dogs", []):
            if dog.get("role") in {"stud", "breeding", "war_dog"}:
                continue
            ensure_animal_health(dog, "dog")
            if dog.get("health_status", "sound") in {"dead", "laid_up"}:
                continue
            candidates.append(
                {
                    "species": "dog",
                    "name": dog.get("name"),
                    "breed": dog.get("breed"),
                    "role": dog.get("role"),
                    "health_status": dog.get("health_status", "sound"),
                    "estimated_cost_silver": estimate_dog_value(dog, breed_db),
                    "hp": dog.get("hp"),
                    "max_hp": dog.get("max_hp"),
                }
            )
    return candidates


def settlement_replacement_market(settlement_name: str) -> dict[str, Any]:
    horses = _available_horse_replacements(settlement_name)
    dogs = _available_dog_replacements(settlement_name)
    horse_foals = 0
    dog_pups = 0
    if HORSE_HERDS_FILE.exists():
        for herd in _load_yaml(HORSE_HERDS_FILE).get("horse_herds", []):
            if str(herd.get("owner_name", "")).lower() == settlement_name.lower():
                horse_foals += len(herd.get("foals", []))
    if DOG_KENNELS_FILE.exists():
        for kennel in _load_yaml(DOG_KENNELS_FILE).get("dog_kennels", []):
            if str(kennel.get("owner_name", "")).lower() == settlement_name.lower():
                dog_pups += len(kennel.get("pups", []))
    return {
        "settlement": settlement_name,
        "mount_replacements": horses,
        "dog_replacements": dogs,
        "future_mount_stock": horse_foals,
        "future_dog_stock": dog_pups,
    }


def _random_name(gender: str = "male") -> str:
    """Generate a random Norse name."""
    names = MALE_NAMES if gender == "male" else FEMALE_NAMES
    name = random.choice(names)
    if random.random() < 0.35:
        name += f" {random.choice(BYNAMES)}"
    return name


def generate_recruit(rank: str = "common", background: str | None = None) -> dict:
    """Generate a single recruit with stats based on background and rank."""
    if background is None:
        background = random.choice(list(BACKGROUNDS.keys()))

    bg = BACKGROUNDS[background]

    # Base attributes: all 5
    attrs = {"mig": 5, "nim": 5, "tou": 5, "wit": 5, "wil": 5}

    # Boost primary attribute by 1-4
    primary = bg["primary_attr"]
    attrs[primary] += random.randint(1, 4)

    # Reduce weakest attribute by 1-3
    weakest = min(attrs, key=lambda k: attrs[k] if k != primary else 99)
    attrs[weakest] = max(1, attrs[weakest] - random.randint(1, 3))

    # Thralls have overall lower stats
    if bg.get("attr_penalty"):
        for attr in attrs:
            if attr != primary:
                attrs[attr] = max(1, attrs[attr] - 1)

    # Veterans get stat boost
    if rank in ("veteran", "named_man"):
        boost_attr = random.choice(["mig", "nim", "tou"])
        attrs[boost_attr] = min(10, attrs[boost_attr] + random.randint(1, 2))

    # Named men get additional boost
    if rank == "named_man":
        attrs["wil"] = min(10, attrs["wil"] + random.randint(1, 2))

    # Clamp all to 1-10
    for attr in attrs:
        attrs[attr] = max(1, min(10, attrs[attr]))

    # Wyrd
    wyrd = _generate_wyrd()

    # Skills from background
    skills = {}
    for skill_name, (low, high) in bg["skills"].items():
        rank_val = random.randint(low, high)
        if rank_val > 0:
            skills[skill_name] = rank_val

    # Veterans and Named Men get combat skills
    if rank in ("veteran", "named_man"):
        combat_skill = random.choice(["axes", "blades", "spears", "shields"])
        skills[combat_skill] = max(skills.get(combat_skill, 0), random.randint(2, 3))

    if rank == "named_man":
        extra = random.choice(["command", "intimidate", "persuade"])
        skills[extra] = max(skills.get(extra, 0), random.randint(1, 2))

    # Gender and name
    gender = "female" if random.random() < 0.15 else "male"
    name = _random_name(gender)

    recruit = {
        "name": name,
        "gender": gender,
        "background": background,
        "rank": rank,
        **attrs,
        "wyr": wyrd,
        "skills": skills,
        "description": bg["description"],
        "hiring_cost_silver": HIRING_COST.get(rank, HIRING_COST["common"]),
    }

    return recruit


def generate_pool(
    settlement_type: str = "village",
    reputation: int = 1,
) -> dict:
    """Generate a recruit pool at a settlement."""
    actual_settlement_name = None
    if settlement_type not in SETTLEMENT_POOLS:
        actual_settlement_name = settlement_type
        settlement_type = _settlement_size(settlement_type)

    pool_info = SETTLEMENT_POOLS.get(settlement_type, SETTLEMENT_POOLS["village"])
    count, sides = pool_info["dice"]
    pool_size = roll_sum(count, sides)

    # Reputation bonus to pool size
    pool_size += reputation

    recruits = []
    for _ in range(pool_size):
        roll = roll_d100()
        if roll <= pool_info["veteran_chance"] and pool_info["max_rank"] in ("veteran", "named_man"):
            # Small chance of named man in towns
            if pool_info["max_rank"] == "named_man" and roll <= 5:
                rank = "named_man"
            else:
                rank = "veteran"
        else:
            rank = "common"

        recruits.append(generate_recruit(rank))

    result = {
        "settlement_type": settlement_type,
        "settlement_name": actual_settlement_name,
        "reputation": reputation,
        "pool_size": len(recruits),
        "recruits": recruits,
        "veterans": sum(1 for r in recruits if r["rank"] == "veteran"),
        "named_men": sum(1 for r in recruits if r["rank"] == "named_man"),
        "total_hiring_cost": sum(r["hiring_cost_silver"] for r in recruits),
    }
    if actual_settlement_name:
        result["animal_replacements"] = settlement_replacement_market(actual_settlement_name)
    return result


def hiring_cost(rank: str, weeks_advance: int = 0) -> dict:
    """Calculate hiring cost for a recruit."""
    base = HIRING_COST.get(rank, HIRING_COST["common"])
    # First week retainer included
    from ledger import WEEKLY_RETAINER
    weekly = WEEKLY_RETAINER.get(rank, WEEKLY_RETAINER["common"])
    total_copper = (base * 10) + (weekly * weeks_advance)
    return {
        "rank": rank,
        "signing_bonus_silver": base,
        "weekly_retainer_copper": weekly,
        "weeks_advance_pay": weeks_advance,
        "total_copper": total_copper,
        "total_display": f"{total_copper // 10} silver {total_copper % 10} copper",
    }


def main():
    parser = argparse.ArgumentParser(description="Iron Ledger Recruitment Engine")
    subparsers = parser.add_subparsers(dest="command")

    # --- pool ---
    pool_p = subparsers.add_parser("pool", help="Generate recruit pool at settlement")
    pool_p.add_argument("--settlement", type=str, default="village",
                        help="Settlement size or named settlement")
    pool_p.add_argument("--reputation", type=int, default=1)
    pool_p.add_argument("--json", action="store_true")

    rep_p = subparsers.add_parser("replacements", help="List animal replacement market for a settlement")
    rep_p.add_argument("--settlement", required=True)
    rep_p.add_argument("--json", action="store_true")

    # --- recruit ---
    rec_p = subparsers.add_parser("recruit", help="Generate a single recruit")
    rec_p.add_argument("--rank", type=str, default="common",
                       choices=["common", "veteran", "named_man"])
    rec_p.add_argument("--background", type=str, default=None,
                       choices=list(BACKGROUNDS.keys()))
    rec_p.add_argument("--json", action="store_true")

    # --- cost ---
    cost_p = subparsers.add_parser("cost", help="Calculate hiring cost")
    cost_p.add_argument("--rank", type=str, required=True,
                        choices=["common", "veteran", "named_man"])
    cost_p.add_argument("--weeks", type=int, default=0, help="Weeks advance pay")
    cost_p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "pool":
        result = generate_pool(args.settlement, args.reputation)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Recruit Pool at {result['settlement_type']} "
                  f"(Reputation {result['reputation']}):")
            print(f"  Total: {result['pool_size']} "
                  f"(Veterans: {result['veterans']}, Named: {result['named_men']})")
            for r in result["recruits"]:
                skills_str = ", ".join(f"{k}:{v}" for k, v in r["skills"].items())
                print(f"  [{r['rank']}] {r['name']} ({r['background']}) "
                      f"MIG:{r['mig']} NIM:{r['nim']} TOU:{r['tou']} "
                      f"WIT:{r['wit']} WIL:{r['wil']} WYR:{r['wyr']} "
                      f"— {skills_str}")
            market = result.get("animal_replacements")
            if market:
                print(f"Animal replacements at {market['settlement']}:")
                for horse in market["mount_replacements"]:
                    print(f"  [horse] {horse['name']} {horse['breed']} {horse['estimated_cost_silver']}s")
                for dog in market["dog_replacements"]:
                    print(f"  [dog] {dog['name']} {dog['breed']} {dog['estimated_cost_silver']}s")
                print(
                    f"  Future stock: {market['future_mount_stock']} foals, "
                    f"{market['future_dog_stock']} pups"
                )

    elif args.command == "replacements":
        result = settlement_replacement_market(args.settlement)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Replacement market at {result['settlement']}:")
            print(f"  Mounts: {len(result['mount_replacements'])}")
            print(f"  Dogs: {len(result['dog_replacements'])}")
            print(f"  Future stock: {result['future_mount_stock']} foals, {result['future_dog_stock']} pups")

    elif args.command == "recruit":
        result = generate_recruit(args.rank, args.background)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            skills_str = ", ".join(f"{k}:{v}" for k, v in result["skills"].items())
            print(f"{result['name']} [{result['rank']}] ({result['background']})")
            print(f"  MIG:{result['mig']} NIM:{result['nim']} TOU:{result['tou']} "
                  f"WIT:{result['wit']} WIL:{result['wil']} WYR:{result['wyr']}")
            print(f"  Skills: {skills_str}")
            print(f"  {result['description']}")

    elif args.command == "cost":
        result = hiring_cost(args.rank, args.weeks)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Hiring {result['rank']}:")
            print(f"  Signing bonus: {result['signing_bonus_silver']} silver")
            print(f"  Weekly retainer: {result['weekly_retainer_copper']} copper")
            print(f"  Total: {result['total_display']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
