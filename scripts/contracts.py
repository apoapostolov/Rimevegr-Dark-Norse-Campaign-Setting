#!/usr/bin/env python3
"""
Iron Ledger — Contract Generator and Manager

Generates and manages mercenary contracts based on reputation, location,
season, and political conditions. Rules from 20_SIMULATION_RULES.md §13.

Usage:
    python contracts.py generate --reputation 2 --settlement village --season long_dark
    python contracts.py detail --contract-type escort
    python contracts.py evaluate --contract-type raid --band-size 14 --reputation 2
    python contracts.py feud --level 2 --action weregild
"""

import argparse
import json
import random
import sys

sys.path.insert(0, __file__ and __import__('os').path.dirname(__file__) or '.')
from engine import roll_d100, roll_sum

# --- Reputation Scale ---
REPUTATION = {
    0: {"name": "Unknown", "effect": "Only desperate employers offer work"},
    1: {"name": "Known", "effect": "Basic escort and guard contracts available"},
    2: {"name": "Respected", "effect": "Standard contracts; settlements negotiate fairly"},
    3: {"name": "Feared/Admired", "effect": "Choice contracts; jarls seek you out"},
    4: {"name": "Legendary", "effect": "Can demand premium pay; rivals avoid you"},
    5: {"name": "Mythic", "effect": "Shape regional politics; all doors open"},
}

# --- Contract Templates ---
CONTRACT_TYPES = {
    "escort": {
        "name": "Escort Duty",
        "description": "Guard a merchant or noble caravan between settlements.",
        "min_reputation": 0,
        "base_pay_silver": 30,
        "duration_days": (5, 15),
        "risk": "low",
        "band_size_min": 5,
        "skills_valued": ["command", "navigate"],
    },
    "guard": {
        "name": "Settlement Guard",
        "description": "Protect a settlement from raiders or beasts for a season.",
        "min_reputation": 1,
        "base_pay_silver": 60,
        "duration_days": (20, 60),
        "risk": "moderate",
        "band_size_min": 8,
        "skills_valued": ["command", "intimidate"],
    },
    "raid": {
        "name": "Raiding Party",
        "description": "Strike an enemy settlement or rival band's camp.",
        "min_reputation": 2,
        "base_pay_silver": 80,
        "duration_days": (3, 10),
        "risk": "high",
        "band_size_min": 10,
        "skills_valued": ["axes", "stealth", "navigate"],
    },
    "bounty": {
        "name": "Bounty Hunt",
        "description": "Track and eliminate a specific outlaw or beast.",
        "min_reputation": 1,
        "base_pay_silver": 50,
        "duration_days": (7, 21),
        "risk": "moderate",
        "band_size_min": 4,
        "skills_valued": ["track", "bows"],
    },
    "barrow_clear": {
        "name": "Barrow Clearing",
        "description": "Explore and clear a barrow mound of restless dead or occupants.",
        "min_reputation": 2,
        "base_pay_silver": 100,
        "duration_days": (1, 3),
        "risk": "high",
        "band_size_min": 6,
        "skills_valued": ["rune_lore", "spears"],
    },
    "debt_collection": {
        "name": "Debt Collection",
        "description": "Enforce payment of debts owed to a jarl or merchant.",
        "min_reputation": 1,
        "base_pay_silver": 25,
        "duration_days": (3, 7),
        "risk": "low",
        "band_size_min": 3,
        "skills_valued": ["intimidate", "bargain"],
    },
    "war_band": {
        "name": "War Band Levy",
        "description": "Join a jarl's host for a campaign against a rival hold.",
        "min_reputation": 3,
        "base_pay_silver": 150,
        "duration_days": (30, 90),
        "risk": "extreme",
        "band_size_min": 12,
        "skills_valued": ["command", "shields", "axes"],
    },
    "diplomatic_escort": {
        "name": "Diplomatic Escort",
        "description": "Escort an emissary through hostile territory.",
        "min_reputation": 3,
        "base_pay_silver": 70,
        "duration_days": (7, 20),
        "risk": "moderate",
        "band_size_min": 6,
        "skills_valued": ["persuade", "navigate", "command"],
    },
    "beast_hunt": {
        "name": "Beast Hunt",
        "description": "Track and slay a dangerous creature terrorizing the area.",
        "min_reputation": 2,
        "base_pay_silver": 90,
        "duration_days": (5, 14),
        "risk": "high",
        "band_size_min": 6,
        "skills_valued": ["track", "spears", "bows"],
    },
    "winter_hold": {
        "name": "Winter Hold Defense",
        "description": "Garrison a remote hold through the Long Dark.",
        "min_reputation": 2,
        "base_pay_silver": 120,
        "duration_days": (60, 120),
        "risk": "moderate",
        "band_size_min": 10,
        "skills_valued": ["shelter", "command", "forage"],
    },
}

# --- Season Availability Modifiers ---
SEASON_CONTRACT_WEIGHTS = {
    "long_summer": {
        "escort": 3, "guard": 2, "raid": 3, "bounty": 2,
        "barrow_clear": 2, "debt_collection": 2, "war_band": 2,
        "diplomatic_escort": 2, "beast_hunt": 2, "winter_hold": 0,
    },
    "long_dark": {
        "escort": 1, "guard": 3, "raid": 1, "bounty": 1,
        "barrow_clear": 1, "debt_collection": 1, "war_band": 0,
        "diplomatic_escort": 1, "beast_hunt": 1, "winter_hold": 3,
    },
}

# --- Settlement Size Contract Pool ---
SETTLEMENT_CONTRACT_POOL = {
    "hamlet": 1,
    "village": 2,
    "large_village": 3,
    "small_town": 4,
}

# --- Feud Track ---
FEUD_LEVELS = {
    0: {"name": "Cold", "effect": "No active hostility"},
    1: {"name": "Tense", "effect": "Prices +20%, information restricted"},
    2: {"name": "Hostile", "effect": "Gates closed, ambush risk"},
    3: {"name": "Blood-feud", "effect": "Active hunting, bounties posted"},
    4: {"name": "Vengeance", "effect": "Full war, no quarter"},
}

FEUD_ACTIONS = {
    "tribute": -1,
    "weregild": -2,
    "service": -1,
    "time_passage": -1,
    "atrocity": +2,
    "broken_contract": +1,
    "raid_settlement": +2,
    "killed_notable": +1,
}


def generate_contracts(
    reputation: int,
    settlement_type: str = "village",
    season: str = "long_summer",
    feud_level: int = 0,
) -> list[dict]:
    """Generate available contracts based on conditions."""
    season_key = "long_dark" if "dark" in season else "long_summer"
    weights = SEASON_CONTRACT_WEIGHTS[season_key]
    pool_size = SETTLEMENT_CONTRACT_POOL.get(settlement_type, 2)

    # Filter by reputation
    available = {
        k: v for k, v in CONTRACT_TYPES.items()
        if v["min_reputation"] <= reputation and weights.get(k, 0) > 0
    }

    if not available:
        return [{"note": "No contracts available — reputation too low or off-season."}]

    # Feud reduces pool
    if feud_level >= 2:
        pool_size = max(1, pool_size - 1)
    if feud_level >= 3:
        return [{"note": f"Blood-feud active (level {feud_level}) — no work offered."}]

    # Weighted random selection
    weighted_pool = []
    for ctype, template in available.items():
        w = weights.get(ctype, 1)
        weighted_pool.extend([(ctype, template)] * w)

    contracts = []
    selected = set()
    attempts = 0
    while len(contracts) < pool_size and attempts < pool_size * 5:
        attempts += 1
        ctype, template = random.choice(weighted_pool)
        if ctype in selected:
            continue
        selected.add(ctype)

        # Calculate pay with reputation bonus
        rep_mult = 1.0 + (reputation * 0.1)
        base = template["base_pay_silver"]
        pay = int(base * rep_mult)

        # Randomize duration
        dur_min, dur_max = template["duration_days"]
        duration = random.randint(dur_min, dur_max)

        contracts.append({
            "type": ctype,
            "name": template["name"],
            "description": template["description"],
            "pay_silver": pay,
            "duration_days": duration,
            "risk": template["risk"],
            "band_size_min": template["band_size_min"],
            "skills_valued": template["skills_valued"],
            "reputation_required": template["min_reputation"],
        })

    return contracts


def contract_detail(contract_type: str) -> dict:
    """Get full details of a contract type."""
    template = CONTRACT_TYPES.get(contract_type)
    if not template:
        return {"error": f"Unknown contract type: {contract_type}",
                "available": list(CONTRACT_TYPES.keys())}
    return {"type": contract_type, **template}


def evaluate_contract(
    contract_type: str,
    band_size: int,
    reputation: int,
) -> dict:
    """Evaluate whether a band can take a contract and expected profit/risk."""
    template = CONTRACT_TYPES.get(contract_type)
    if not template:
        return {"error": f"Unknown contract type: {contract_type}"}

    can_take = (
        reputation >= template["min_reputation"]
        and band_size >= template["band_size_min"]
    )

    rep_mult = 1.0 + (reputation * 0.1)
    pay = int(template["base_pay_silver"] * rep_mult)
    dur_min, dur_max = template["duration_days"]
    avg_duration = (dur_min + dur_max) // 2

    # Rough cost estimate: 1 silver/person/week food + retainer ~2 silver/person/week
    weekly_cost_silver = band_size * 3
    weeks = max(1, avg_duration // 7)
    estimated_cost = weekly_cost_silver * weeks
    estimated_profit = pay - estimated_cost

    return {
        "type": contract_type,
        "name": template["name"],
        "can_take": can_take,
        "issues": [] if can_take else [
            f"Need reputation {template['min_reputation']}, have {reputation}"
            if reputation < template["min_reputation"] else None,
            f"Need {template['band_size_min']} fighters, have {band_size}"
            if band_size < template["band_size_min"] else None,
        ],
        "estimated_pay_silver": pay,
        "avg_duration_days": avg_duration,
        "estimated_cost_silver": estimated_cost,
        "estimated_profit_silver": estimated_profit,
        "risk": template["risk"],
        "profitable": estimated_profit > 0,
    }


def update_feud(current_level: int, action: str) -> dict:
    """Update feud track based on an action."""
    change = FEUD_ACTIONS.get(action, 0)
    new_level = max(0, min(4, current_level + change))
    return {
        "previous_level": current_level,
        "previous_name": FEUD_LEVELS[current_level]["name"],
        "action": action,
        "change": change,
        "new_level": new_level,
        "new_name": FEUD_LEVELS[new_level]["name"],
        "effect": FEUD_LEVELS[new_level]["effect"],
    }


def reputation_info(level: int) -> dict:
    """Get reputation level details."""
    level = max(0, min(5, level))
    info = REPUTATION[level]
    return {"level": level, **info}


def main():
    parser = argparse.ArgumentParser(description="Iron Ledger Contract Manager")
    subparsers = parser.add_subparsers(dest="command")

    # --- generate ---
    gen_p = subparsers.add_parser("generate", help="Generate available contracts")
    gen_p.add_argument("--reputation", type=int, required=True, help="Band reputation (0-5)")
    gen_p.add_argument("--settlement", type=str, default="village",
                       choices=list(SETTLEMENT_CONTRACT_POOL.keys()))
    gen_p.add_argument("--season", type=str, default="long_summer")
    gen_p.add_argument("--feud", type=int, default=0, help="Feud level with settlement (0-4)")
    gen_p.add_argument("--json", action="store_true")

    # --- detail ---
    det_p = subparsers.add_parser("detail", help="Contract type details")
    det_p.add_argument("--contract-type", type=str, required=True,
                       choices=list(CONTRACT_TYPES.keys()))
    det_p.add_argument("--json", action="store_true")

    # --- evaluate ---
    eva_p = subparsers.add_parser("evaluate", help="Evaluate a contract for the band")
    eva_p.add_argument("--contract-type", type=str, required=True,
                       choices=list(CONTRACT_TYPES.keys()))
    eva_p.add_argument("--band-size", type=int, required=True)
    eva_p.add_argument("--reputation", type=int, required=True)
    eva_p.add_argument("--json", action="store_true")

    # --- feud ---
    feud_p = subparsers.add_parser("feud", help="Update feud track")
    feud_p.add_argument("--level", type=int, required=True, help="Current feud level (0-4)")
    feud_p.add_argument("--action", type=str, required=True,
                        choices=list(FEUD_ACTIONS.keys()))
    feud_p.add_argument("--json", action="store_true")

    # --- reputation ---
    rep_p = subparsers.add_parser("reputation", help="Show reputation level info")
    rep_p.add_argument("--level", type=int, required=True)
    rep_p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "generate":
        result = generate_contracts(args.reputation, args.settlement, args.season, args.feud)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            for c in result:
                if "note" in c:
                    print(c["note"])
                else:
                    print(f"[{c['type']}] {c['name']} — {c['pay_silver']} silver, "
                          f"{c['duration_days']}d, risk: {c['risk']}")
                    print(f"  {c['description']}")

    elif args.command == "detail":
        result = contract_detail(args.contract_type)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            for k, v in result.items():
                print(f"  {k}: {v}")

    elif args.command == "evaluate":
        result = evaluate_contract(args.contract_type, args.band_size, args.reputation)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            status = "CAN TAKE" if result["can_take"] else "CANNOT TAKE"
            print(f"{result['name']} — {status}")
            print(f"  Pay: ~{result['estimated_pay_silver']} silver")
            print(f"  Cost: ~{result['estimated_cost_silver']} silver")
            print(f"  Profit: ~{result['estimated_profit_silver']} silver")
            print(f"  Risk: {result['risk']}")

    elif args.command == "feud":
        result = update_feud(args.level, args.action)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Feud: {result['previous_name']} ({result['previous_level']}) "
                  f"→ {result['new_name']} ({result['new_level']})")
            print(f"  Effect: {result['effect']}")

    elif args.command == "reputation":
        result = reputation_info(args.level)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Reputation {result['level']}: {result['name']}")
            print(f"  {result['effect']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
