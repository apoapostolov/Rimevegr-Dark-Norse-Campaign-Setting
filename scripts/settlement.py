#!/usr/bin/env python3
"""
Iron Ledger — Settlement Manager

Manages settlement states, services, prices, and interactions. Settlements
have size, feud level, available services, and dynamic pricing.

Usage:
    python settlement.py info --name Greyhaven
    python settlement.py prices --name Greyhaven --feud 1
    python settlement.py services --size village
    python settlement.py services --name "Frostfjord Hollow"
    python settlement.py create --name Ironford --size hamlet --terrain coast
"""

import argparse
import json
import os
import random
import sys

sys.path.insert(0, __file__ and __import__('os').path.dirname(__file__) or '.')
from engine import roll_d100

try:
    import yaml
except ImportError:
    yaml = None

from recruitment import settlement_replacement_market

# --- Settlement Templates ---
SETTLEMENT_SIZES = {
    "hamlet": {
        "population": (20, 60),
        "services": ["general_trade"],
        "defense": "fence, hedge, or no formal perimeter",
        "defensibility": 1,
        "notable_buildings": 1,
        "structures": {
            "domestic": {"longhouses": 4, "cottar_huts": 2, "byres": 2},
            "storage": {"root_cellars": 2, "sheds": 2},
            "productive": {"animal_pens": 2},
            "civic_religious": {"elder_houses": 1, "shrine_sites": 1},
        },
        "defenses": {
            "perimeter": "thorn_hedge_or_none",
            "ditch": "none",
            "gatehouses": 0,
            "towers": 0,
        },
        "construction_capacity": {
            "laborers": 8,
            "carpenters": 1,
            "masons": 0,
            "smiths": 0,
            "build_points_per_season": 10,
        },
        "maintenance_burden": {"upkeep_points_per_year": 5},
        "damage_state": {"overall": "sound", "damaged_elements": []},
    },
    "village": {
        "population": (60, 200),
        "services": ["inn", "general_trade", "smithy", "healer"],
        "defense": "partial palisade with one gate",
        "defensibility": 2,
        "notable_buildings": 2,
        "structures": {
            "domestic": {"longhouses": 10, "cottar_huts": 4, "byres": 4},
            "storage": {"granaries": 1, "root_cellars": 6, "smokehouses": 1},
            "productive": {"smithies": 1, "healer_huts": 1, "work_sheds": 2},
            "civic_religious": {"halls": 1, "inns": 1, "law_stones": 1},
        },
        "defenses": {
            "perimeter": "split_log_palisade",
            "ditch": "shallow",
            "gatehouses": 1,
            "towers": 0,
        },
        "construction_capacity": {
            "laborers": 18,
            "carpenters": 2,
            "masons": 0,
            "smiths": 1,
            "build_points_per_season": 20,
        },
        "maintenance_burden": {"upkeep_points_per_year": 10},
        "damage_state": {"overall": "sound", "damaged_elements": []},
    },
    "large_village": {
        "population": (200, 500),
        "services": ["inn", "general_trade", "smithy", "healer", "shipwright", "temple"],
        "defense": "timber wall with gate control",
        "defensibility": 3,
        "notable_buildings": 3,
        "structures": {
            "domestic": {"longhouses": 18, "cottar_huts": 8, "byres": 8},
            "storage": {"granaries": 2, "storehouses": 2, "root_cellars": 10, "smokehouses": 2},
            "productive": {"smithies": 1, "healer_lodges": 1, "pit_workshops": 2, "boathouses": 1},
            "civic_religious": {"halls": 1, "inns": 1, "market_yards": 1, "thing_sites": 1, "temples": 1},
        },
        "defenses": {
            "perimeter": "timber_wall",
            "ditch": "partial",
            "gatehouses": 1,
            "towers": 1,
        },
        "construction_capacity": {
            "laborers": 28,
            "carpenters": 3,
            "masons": 1,
            "smiths": 2,
            "build_points_per_season": 32,
        },
        "maintenance_burden": {"upkeep_points_per_year": 16},
        "damage_state": {"overall": "sound", "damaged_elements": []},
    },
    "small_town": {
        "population": (500, 2000),
        "services": ["inn", "general_trade", "smithy", "healer", "shipwright",
                     "temple", "jarl_hall", "market"],
        "defense": "wall circuit with gatehouses and garrison works",
        "defensibility": 4,
        "notable_buildings": 5,
        "structures": {
            "domestic": {"longhouses": 30, "cottar_huts": 16, "byres": 10},
            "storage": {"granaries": 4, "storehouses": 4, "root_cellars": 16, "smokehouses": 3},
            "productive": {"smithies": 2, "healer_lodges": 1, "pit_workshops": 4, "boathouses": 2},
            "civic_religious": {"halls": 1, "guesthalls": 1, "inns": 2, "market_yards": 1, "thing_sites": 1, "temples": 1},
        },
        "defenses": {
            "perimeter": "stone_or_heavy_timber_wall",
            "ditch": "outer_ditch",
            "gatehouses": 2,
            "towers": 2,
        },
        "construction_capacity": {
            "laborers": 48,
            "carpenters": 5,
            "masons": 3,
            "smiths": 3,
            "build_points_per_season": 50,
        },
        "maintenance_burden": {"upkeep_points_per_year": 28},
        "damage_state": {"overall": "sound", "damaged_elements": []},
    },
}

# --- Base Prices (copper) ---
BASE_PRICES = {
    "food_week": 10,          # 1 silver per week per person
    "ale_mug": 1,
    "room_night": 3,
    "horse": 200,             # 20 silver
    "dagger": 20,             # 2 silver
    "hand_axe": 40,           # 4 silver
    "sword": 100,             # 10 silver
    "spear": 50,              # 5 silver
    "leather_armor": 60,      # 6 silver
    "chainmail": 250,         # 25 silver
    "iron_helm": 80,          # 8 silver
    "wooden_shield": 30,      # 3 silver
    "iron_shield": 60,        # 6 silver
    "rope_20m": 5,
    "torch_bundle": 3,
    "healing_herbs": 15,
    "warm_cloak": 20,         # 2 silver
    "rations_week": 10,       # 1 silver per week per person
}

# --- Service Descriptions ---
SERVICES = {
    "inn": "Rest, food, ale, and rumors. Hear about local events and contracts.",
    "general_trade": "Buy and sell common goods, food, and basic equipment.",
    "smithy": "Weapon and armor repair, basic metalwork. Can commission gear.",
    "healer": "Treat wounds, cure infections, set bones. Reduces recovery time.",
    "shipwright": "Repair and commission boats. Access to coastal routes.",
    "temple": "Blessings, rune consultations, and spiritual counsel.",
    "jarl_hall": "Audience with the local lord. High-value contracts and disputes.",
    "market": "Weekly market with wider goods selection and better prices.",
}

# --- Terrain Traits ---
TERRAIN_TRAITS = {
    "coast": {"trade_bonus": 1.0, "food_mod": 0.9, "desc": "Coastal settlement with fishing and trade."},
    "forest": {"trade_bonus": 0.8, "food_mod": 0.85, "desc": "Woodland settlement, timber-rich but isolated."},
    "moors": {"trade_bonus": 0.7, "food_mod": 1.1, "desc": "Exposed moorland settlement, wind-blasted."},
    "mountain": {"trade_bonus": 0.6, "food_mod": 1.2, "desc": "Mountain settlement, defensible but poor."},
    "river": {"trade_bonus": 0.9, "food_mod": 0.95, "desc": "Riverside settlement with trade route access."},
    "fjord": {"trade_bonus": 1.0, "food_mod": 0.9, "desc": "Fjord settlement with deep-water harbor."},
}

# --- Feud Price Modifiers ---
FEUD_PRICE_MULT = {
    0: 1.0,     # Cold — normal prices
    1: 1.2,     # Tense — +20%
    2: 1.5,     # Hostile — +50% (if gates even open)
    3: 2.0,     # Blood-feud (unlikely to trade)
    4: 0.0,     # Vengeance (no trade)
}

# --- Notable Building Types ---
NOTABLE_BUILDINGS = [
    "ancient rune-stone", "mead hall", "watchtower", "barrow nearby",
    "hot spring", "sacred grove", "old longship hull (landmark)",
    "iron mine entrance", "tannery", "rope walk", "salt works",
    "brewery", "chieftain's longhouse", "trading post", "fisher's wharf",
]


def _copy_structure_template(size: str) -> dict:
    """Return a JSON-safe deep copy of a size template."""
    return json.loads(json.dumps(SETTLEMENT_SIZES.get(size, SETTLEMENT_SIZES["village"])))


def _structure_focus_for_terrain(terrain: str) -> list[str]:
    """Return likely infrastructure specializations for generated settlements."""
    mapping = {
        "coast": ["boathouse", "jetty", "fish_shed"],
        "fjord": ["boathouse", "jetty", "fish_shed"],
        "forest": ["tar_pit", "charcoal_clamp", "timber_shed"],
        "moors": ["peat_stack", "sheep_pens", "fold_wall"],
        "mountain": ["watchtower", "ore_shed", "retaining_wall"],
        "river": ["jetty", "ferry_landing", "storehouse"],
    }
    return mapping.get(terrain, [])


def create_settlement(
    name: str,
    size: str = "village",
    terrain: str = "coast",
    feud_level: int = 0,
    reputation_with: int = 1,
) -> dict:
    """Create a settlement with generated details."""
    size_info = _copy_structure_template(size)
    terrain_info = TERRAIN_TRAITS.get(terrain, TERRAIN_TRAITS["coast"])

    pop_min, pop_max = size_info["population"]
    population = random.randint(pop_min, pop_max)

    # Pick notable buildings
    notables = random.sample(NOTABLE_BUILDINGS,
                             min(size_info["notable_buildings"], len(NOTABLE_BUILDINGS)))

    # Generate leader
    leader_title = "elder" if size in ("hamlet", "village") else "jarl"
    leader_name = random.choice([
        "Thorolf", "Sigvat", "Brynjar", "Kolbein", "Hallstein",
        "Gudmund", "Arnkel", "Hrafn", "Thorgrim", "Ketil",
    ])

    structures = size_info["structures"]
    terrain_focus = _structure_focus_for_terrain(terrain)

    if terrain_focus:
        productive = structures.setdefault("productive", {})
        for key in terrain_focus[:2]:
            productive[key + "s" if not key.endswith("s") else key] = 1

    defenses = size_info["defenses"]
    if terrain in ("coast", "fjord", "river"):
        defenses["natural_barriers"] = [f"{terrain}_frontage"]
    elif terrain == "mountain":
        defenses["natural_barriers"] = ["steep_approach"]
    else:
        defenses["natural_barriers"] = []

    return {
        "name": name,
        "size": size,
        "terrain": terrain,
        "population": population,
        "leader": f"{leader_title} {leader_name}",
        "defense": size_info["defense"],
        "defensibility": size_info["defensibility"],
        "services": size_info["services"],
        "notable_buildings": notables,
        "defenses": defenses,
        "structures": structures,
        "construction_capacity": size_info["construction_capacity"],
        "maintenance_burden": size_info["maintenance_burden"],
        "damage_state": size_info["damage_state"],
        "terrain_description": terrain_info["desc"],
        "trade_bonus": terrain_info["trade_bonus"],
        "food_price_mod": terrain_info["food_mod"],
        "feud_level": feud_level,
        "reputation_with": reputation_with,
    }


def get_prices(settlement: dict | None = None, feud_level: int = 0,
               terrain: str = "coast") -> dict:
    """Calculate current prices at a settlement."""
    terrain_info = TERRAIN_TRAITS.get(terrain, TERRAIN_TRAITS["coast"])
    feud_mult = FEUD_PRICE_MULT.get(feud_level, 1.0)

    if feud_mult == 0:
        return {"error": "Settlement refuses all trade (Vengeance feud level)."}

    trade_bonus = terrain_info["trade_bonus"]
    food_mod = terrain_info["food_mod"]

    prices = {}
    for item, base_price in BASE_PRICES.items():
        # Food items modified by terrain food cost
        if "food" in item or "rations" in item:
            price = int(base_price * food_mod * feud_mult)
        else:
            # Non-food: trade bonus reduces prices (better = cheaper)
            price = int(base_price * (2.0 - trade_bonus) * feud_mult)
        prices[item] = {
            "base_copper": base_price,
            "current_copper": max(1, price),
            "current_display": f"{max(1, price) // 10}s {max(1, price) % 10}c"
                               if max(1, price) >= 10
                               else f"{max(1, price)}c",
        }

    return {
        "terrain": terrain,
        "feud_level": feud_level,
        "feud_mult": feud_mult,
        "trade_bonus": trade_bonus,
        "prices": prices,
    }


def settlement_services(size: str | None = None, name: str | None = None) -> dict:
    """List available services for a settlement size or a canonical named settlement."""
    if name:
        base = _find_settlement_base(name)
        if base is None:
            return {"error": f"Settlement '{name}' not found."}
        structures = base.get("structures", {})
        result = []
        for svc in base.get("services", []):
            result.append({
                "service": svc,
                "description": SERVICES.get(svc, "Unknown service."),
            })
        return {
            "name": base.get("name", name),
            "size": base.get("size", "village"),
            "services": result,
            "defenses": base.get("defenses", {}),
            "structure_summary": _flatten_structure_counts(structures),
        }

    size_info = SETTLEMENT_SIZES.get(size or "village", SETTLEMENT_SIZES["village"])
    result = []
    for svc in size_info["services"]:
        result.append({
            "service": svc,
            "description": SERVICES.get(svc, "Unknown service."),
        })
    return {
        "size": size or "village",
        "services": result,
        "template_structure_summary": _flatten_structure_counts(size_info.get("structures")),
        "template_defenses": size_info.get("defenses", {}),
    }


def settlement_event(settlement: dict) -> dict:
    """Generate a random event at a settlement."""
    events = [
        {"type": "market_day", "description": "Weekly market — all prices reduced 10%.", "effect": "price_reduction"},
        {"type": "festival", "description": "Seasonal festival — free ale, +1 morale if band attends.", "effect": "morale_boost"},
        {"type": "plague_scare", "description": "Sickness in the settlement — healer busy, risk of infection.", "effect": "infection_risk"},
        {"type": "raider_warning", "description": "Raiders spotted nearby — settlement nervous, guard contracts available.", "effect": "contract_available"},
        {"type": "trade_caravan", "description": "Southern trade caravan arrives — rare goods available.", "effect": "rare_goods"},
        {"type": "feud_flare", "description": "Old blood-feud erupts — brawl in the street, tensions high.", "effect": "feud_increase"},
        {"type": "wanderer_arrives", "description": "A lone wanderer seeks shelter — potential recruit or spy.", "effect": "npc_encounter"},
        {"type": "thing_assembly", "description": "Local thing (assembly) — disputes settled, oaths sworn.", "effect": "reputation_chance"},
        {"type": "bad_harvest", "description": "Failed harvest — food prices increase 30%.", "effect": "food_price_increase"},
        {"type": "good_fishing", "description": "Excellent catch — food prices decrease 20%.", "effect": "food_price_decrease"},
    ]
    event = random.choice(events)
    return {
        "settlement": settlement.get("name", "unknown"),
        **event,
    }


# --- YAML Data Loaders ---

def _data_path(*parts: str) -> str:
    """Resolve a path relative to the data/ directory."""
    return os.path.join(os.path.dirname(__file__), '..', 'data', *parts)


def _load_settlement_economies() -> list[dict]:
    """Load settlement_economies.yaml."""
    with open(_data_path('economy', 'settlement_economies.yaml'), 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)['settlement_economies']


def _load_trade_goods() -> dict:
    """Load trade_goods.yaml (keyed by category)."""
    with open(_data_path('economy', 'trade_goods.yaml'), 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)['trade_goods']


def _load_settlements() -> list[dict]:
    """Load settlements.yaml (the base settlement list with size/terrain/feud)."""
    with open(_data_path('settlements.yaml'), 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)['settlements']


def _find_settlement_economy(name: str) -> dict | None:
    """Find a settlement economy profile by case-insensitive name."""
    needle = name.lower()
    for se in _load_settlement_economies():
        if se.get('settlement', '').lower() == needle:
            return se
    return None


def _find_settlement_base(name: str) -> dict | None:
    """Find a base settlement entry by case-insensitive name."""
    needle = name.lower()
    for s in _load_settlements():
        if s.get('name', '').lower() == needle:
            return s
    return None


def _flatten_structure_counts(structures: dict | None) -> list[str]:
    """Flatten nested structure counts into compact display lines."""
    if not isinstance(structures, dict):
        return []

    lines: list[str] = []
    for category, values in structures.items():
        if not isinstance(values, dict):
            continue
        parts = []
        for key, value in values.items():
            label = key.replace('_', ' ')
            if isinstance(value, int):
                parts.append(f"{value} {label}")
            elif isinstance(value, list) and value:
                parts.append(f"{label}: {len(value)}")
        if parts:
            lines.append(f"{category.replace('_', ' ')}: " + ", ".join(parts))
    return lines


def settlement_info(name: str) -> dict:
    """Return canonical settlement info including infrastructure summaries."""
    base = _find_settlement_base(name)
    if base is None:
        return {"error": f"Settlement '{name}' not found."}

    defenses = base.get("defenses", {})
    structures = base.get("structures", {})
    construction = base.get("construction_capacity", {})
    maintenance = base.get("maintenance_burden", {})
    damage = base.get("damage_state", {})

    return {
        "name": base.get("name", name),
        "size": base.get("size", "village"),
        "terrain": base.get("terrain", "coast"),
        "population": base.get("population"),
        "leader": base.get("leader"),
        "defense": base.get("defense"),
        "defensibility": base.get("defensibility"),
        "services": base.get("services", []),
        "notable_buildings": base.get("notable_buildings", []),
        "defenses": defenses,
        "structure_summary": _flatten_structure_counts(structures),
        "construction_capacity": construction,
        "maintenance_burden": maintenance,
        "damage_state": damage,
    }


# --- Economy Command ---

def settlement_economy_profile(name: str) -> dict:
    """Retrieve full economic profile for a named settlement."""
    se = _find_settlement_economy(name)
    if se is None:
        return {"error": f"Settlement economy profile not found for '{name}'."}
    return se


# --- Market Command ---

SIZE_AVAILABILITY = {
    "hamlet": ["common"],
    "village": ["common", "uncommon"],
    "large_village": ["common", "uncommon", "rare"],
    "small_town": ["common", "uncommon", "rare", "exotic"],
}


def settlement_market(
    name: str,
    season: str,
    feud_override: int | None = None,
    wartime: bool = False,
) -> dict:
    """List available trade goods at a settlement with applied price modifiers.

    Uses settlement size to determine availability tiers, then applies
    settlement price_modifier × seasonal × wartime × feud modifiers.
    """
    se = _find_settlement_economy(name)
    base = _find_settlement_base(name)

    if se is None and base is None:
        return {"error": f"Settlement '{name}' not found."}

    # Determine size and feud
    size = (se or {}).get('size') or (base or {}).get('size', 'village')
    feud_level = feud_override if feud_override is not None else (base or {}).get('feud_level', 0)
    settlement_price_mod = 1.0
    if se and 'market' in se:
        settlement_price_mod = se['market'].get('price_modifier', 1.0)

    feud_mult = FEUD_PRICE_MULT.get(feud_level, 1.0)
    if feud_mult == 0:
        return {"error": f"Settlement refuses all trade (feud level {feud_level})."}

    allowed_tiers = SIZE_AVAILABILITY.get(size, SIZE_AVAILABILITY["village"])
    goods_data = _load_trade_goods()

    market_goods = []
    for category, items in goods_data.items():
        for good in items:
            avail = good.get('availability', 'common')
            if avail not in allowed_tiers:
                continue

            base_price = good['base_price_copper']
            seasonal_mod = good.get('seasonal_modifier', {}).get(season, 1.0)
            war_mod = good.get('wartime_modifier', 1.0) if wartime else 1.0
            final = int(base_price * seasonal_mod * war_mod * settlement_price_mod * feud_mult)
            final = max(1, final)

            silver = final // 10
            copper = final % 10
            display = f"{silver}s {copper}c" if final >= 10 else f"{final}c"

            market_goods.append({
                "name": good['name'],
                "id": good.get('id', ''),
                "category": category,
                "availability": avail,
                "base_price_copper": base_price,
                "final_price_copper": final,
                "final_price_display": display,
            })

    return {
        "settlement": (se or {}).get('settlement') or (base or {}).get('name', name),
        "size": size,
        "season": season,
        "feud_level": feud_level,
        "wartime": wartime,
        "price_modifier": round(settlement_price_mod * feud_mult, 2),
        "goods_count": len(market_goods),
        "goods": market_goods,
    }


def main():
    parser = argparse.ArgumentParser(description="Iron Ledger Settlement Manager")
    subparsers = parser.add_subparsers(dest="command")

    # --- create ---
    cre_p = subparsers.add_parser("create", help="Create a new settlement")
    cre_p.add_argument("--name", type=str, required=True)
    cre_p.add_argument("--size", type=str, default="village",
                       choices=list(SETTLEMENT_SIZES.keys()))
    cre_p.add_argument("--terrain", type=str, default="coast",
                       choices=list(TERRAIN_TRAITS.keys()))
    cre_p.add_argument("--feud", type=int, default=0)
    cre_p.add_argument("--reputation", type=int, default=1)
    cre_p.add_argument("--json", action="store_true")

    # --- prices ---
    pri_p = subparsers.add_parser("prices", help="Show settlement prices")
    pri_p.add_argument("--terrain", type=str, default="coast",
                       choices=list(TERRAIN_TRAITS.keys()))
    pri_p.add_argument("--feud", type=int, default=0)
    pri_p.add_argument("--json", action="store_true")

    # --- services ---
    svc_p = subparsers.add_parser("services", help="Show available services")
    svc_p.add_argument("--size", type=str, default="village",
                       choices=list(SETTLEMENT_SIZES.keys()))
    svc_p.add_argument("--name", type=str, help="Canonical settlement name")
    svc_p.add_argument("--json", action="store_true")

    # --- info ---
    inf_p = subparsers.add_parser("info", help="Show canonical settlement info")
    inf_p.add_argument("--name", type=str, required=True)
    inf_p.add_argument("--json", action="store_true")

    # --- event ---
    evt_p = subparsers.add_parser("event", help="Generate a settlement event")
    evt_p.add_argument("--name", type=str, default="Settlement")
    evt_p.add_argument("--json", action="store_true")

    # --- economy ---
    eco_p = subparsers.add_parser("economy", help="Show full economic profile")
    eco_p.add_argument("--name", type=str, required=True, help="Settlement name")
    eco_p.add_argument("--json", action="store_true")

    ani_p = subparsers.add_parser("animal-stock", help="Show local mount and dog replacement stock")
    ani_p.add_argument("--name", type=str, required=True, help="Settlement name")
    ani_p.add_argument("--json", action="store_true")

    # --- market ---
    mkt_p = subparsers.add_parser("market", help="List available trade goods at a settlement")
    mkt_p.add_argument("--name", type=str, required=True, help="Settlement name")
    mkt_p.add_argument("--season", type=str, required=True,
                       choices=["thaw", "long_sun", "harvest", "long_dark"])
    mkt_p.add_argument("--feud", type=int, default=None, help="Override feud level (0-4)")
    mkt_p.add_argument("--wartime", action="store_true", help="Apply wartime modifiers")
    mkt_p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "create":
        result = create_settlement(args.name, args.size, args.terrain,
                                   args.feud, args.reputation)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"{result['name']} ({result['size']}, {result['terrain']})")
            print(f"  Population: {result['population']}")
            print(f"  Leader: {result['leader']}")
            print(f"  Defense: {result['defense']}")
            print(f"  Services: {', '.join(result['services'])}")
            print(f"  Notable: {', '.join(result['notable_buildings'])}")
            defenses = result.get("defenses", {})
            if defenses:
                print(
                    "  Perimeter works:"
                    f" {defenses.get('perimeter', 'unknown')},"
                    f" ditch={defenses.get('ditch', 'none')},"
                    f" gatehouses={defenses.get('gatehouses', 0)},"
                    f" towers={defenses.get('towers', 0)}"
                )
            structures = _flatten_structure_counts(result.get("structures"))
            if structures:
                print("  Structures:")
                for line in structures:
                    print(f"    - {line}")
            print(f"  {result['terrain_description']}")

    elif args.command == "prices":
        result = get_prices(feud_level=args.feud, terrain=args.terrain)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if "error" in result:
                print(result["error"])
            else:
                print(f"Prices (feud {result['feud_level']}, {result['terrain']}):")
                for item, info in result["prices"].items():
                    print(f"  {item}: {info['current_display']} (base: {info['base_copper']}c)")

    elif args.command == "services":
        if args.name and yaml is None:
            print("Error: PyYAML is required for named settlement services. Install with: pip install pyyaml")
            sys.exit(1)
        result = settlement_services(size=args.size, name=args.name)
        if "error" in result:
            print(result["error"])
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            heading = result.get("name") or result["size"]
            print(f"Services at {heading}:")
            for s in result["services"]:
                print(f"  {s['service']}: {s['description']}")
            for line in result.get("structure_summary", result.get("template_structure_summary", [])):
                print(f"  Structure support: {line}")
            defenses = result.get("defenses", result.get("template_defenses", {}))
            if defenses:
                print(
                    "  Defense fabric:"
                    f" perimeter={defenses.get('perimeter', 'unknown')},"
                    f" ditch={defenses.get('ditch', 'none')},"
                    f" gatehouses={defenses.get('gatehouses', 0)},"
                    f" towers={defenses.get('towers', 0)}"
                )

    elif args.command == "info":
        if yaml is None:
            print("Error: PyYAML is required for info. Install with: pip install pyyaml")
            sys.exit(1)
        result = settlement_info(args.name)
        if "error" in result:
            print(result["error"])
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"{result['name']} ({result['size']}, {result['terrain']})")
            print(f"  Population: {result['population']}")
            print(f"  Leader: {result['leader']}")
            print(f"  Defense: {result['defense']} [defensibility {result['defensibility']}]")
            if result["services"]:
                print(f"  Services: {', '.join(result['services'])}")
            if result["notable_buildings"]:
                print(f"  Notable: {', '.join(result['notable_buildings'])}")
            defenses = result["defenses"]
            if defenses:
                perimeter = defenses.get("perimeter", "unknown")
                ditch = defenses.get("ditch", "none")
                gates = defenses.get("gatehouses", 0)
                towers = defenses.get("towers", 0)
                print(
                    f"  Perimeter works: {perimeter}, ditch={ditch}, "
                    f"gatehouses={gates}, towers={towers}"
                )
            if result["structure_summary"]:
                print("  Structures:")
                for line in result["structure_summary"]:
                    print(f"    - {line}")
            if result["construction_capacity"]:
                c = result["construction_capacity"]
                print(
                    "  Construction capacity:"
                    f" laborers={c.get('laborers', 0)},"
                    f" carpenters={c.get('carpenters', 0)},"
                    f" masons={c.get('masons', 0)},"
                    f" smiths={c.get('smiths', 0)},"
                    f" build_points_per_season={c.get('build_points_per_season', 0)}"
                )
            if result["maintenance_burden"]:
                m = result["maintenance_burden"]
                print(f"  Maintenance burden: {m.get('upkeep_points_per_year', '?')} per year")
            if result["damage_state"]:
                d = result["damage_state"]
                print(f"  Damage state: {d.get('overall', 'unknown')}")
                for item in d.get("damaged_elements", []):
                    print(f"    - {item}")

    elif args.command == "event":
        result = settlement_event({"name": args.name})
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Event at {result['settlement']}: [{result['type']}]")
            print(f"  {result['description']}")

    elif args.command == "economy":
        if yaml is None:
            print("Error: PyYAML is required for economy. Install with: pip install pyyaml")
            sys.exit(1)
        result = settlement_economy_profile(args.name)
        if "error" in result:
            print(result["error"])
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"=== {result['settlement']} ({result.get('size', '?')}, {result.get('terrain', '?')}) ===")
            print(f"  Population: {result.get('population', '?')}")
            if result.get('production'):
                print("  Production:")
                for p in result['production']:
                    print(f"    - {p['good']} ({p['quantity_weekly']}): {p.get('notes', '')}")
            if result.get('imports'):
                print("  Imports:")
                for i in result['imports']:
                    print(f"    - {i['good']} from {i['source']} [{i['urgency']}]")
            if result.get('exports'):
                print("  Exports:")
                for e in result['exports']:
                    print(f"    - {e['good']} → {', '.join(e['destinations'])} ({e['volume']})")
            if result.get('strategic_resources'):
                print("  Strategic resources:")
                for sr in result['strategic_resources']:
                    print(f"    - {sr['resource']}: {sr['military_value']}")
            if result.get('market'):
                m = result['market']
                print(f"  Market: {m.get('market_day', 'none')} | stalls: {m.get('stall_count', 0)} | price mod: {m.get('price_modifier', 1.0)}")
            if result.get('economic_vulnerabilities'):
                print("  Vulnerabilities:")
                for v in result['economic_vulnerabilities']:
                    print(f"    - {v}")
            if result.get('wartime_impact'):
                wi = result['wartime_impact']
                print(f"  Wartime: food={wi.get('food_security', '?')}, siege={wi.get('siege_endurance_weeks', '?')} weeks")
            replacements = settlement_replacement_market(args.name)
            print(
                f"  Animal replacements: {len(replacements['mount_replacements'])} mounts, "
                f"{len(replacements['dog_replacements'])} dogs"
                f" | future stock {replacements['future_mount_stock']} foals, "
                f"{replacements['future_dog_stock']} pups"
            )

    elif args.command == "animal-stock":
        result = settlement_replacement_market(args.name)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Animal stock at {result['settlement']}:")
            for horse in result["mount_replacements"]:
                print(f"  [horse] {horse['name']} {horse['breed']} {horse['estimated_cost_silver']}s")
            for dog in result["dog_replacements"]:
                print(f"  [dog] {dog['name']} {dog['breed']} {dog['estimated_cost_silver']}s")
            print(
                f"  Future stock: {result['future_mount_stock']} foals, "
                f"{result['future_dog_stock']} pups"
            )

    elif args.command == "market":
        if yaml is None:
            print("Error: PyYAML is required for market. Install with: pip install pyyaml")
            sys.exit(1)
        result = settlement_market(args.name, args.season, args.feud, args.wartime)
        if "error" in result:
            print(result["error"])
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Market at {result['settlement']} ({result['size']}, {result['season']})"
                  f" — feud {result['feud_level']}, price mod ×{result['price_modifier']}"
                  + (" [WARTIME]" if result['wartime'] else ""))
            print(f"  {result['goods_count']} goods available:")
            for g in result['goods']:
                print(f"    {g['name']:30s} {g['category']:12s} {g['final_price_display']:>8s} ({g['availability']})")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
