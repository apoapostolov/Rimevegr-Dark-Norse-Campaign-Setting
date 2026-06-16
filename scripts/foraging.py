#!/usr/bin/env python3
"""
Iron Ledger — Foraging Engine

Simulates food gathering based on terrain, season, weather, and forager
skill. All tables from 20_SIMULATION_RULES.md §9.

Usage:
    python foraging.py forage --terrain fjord --foragers 4 --skill 2 --season long_dark --weather rime_fog
    python foraging.py deficit --food-stores 11 --band-size 14 --season long_dark
    python foraging.py table
"""

import argparse
import json
import sys

sys.path.insert(0, __file__ and __import__('os').path.dirname(__file__) or '.')
from engine import compute_foraging

# --- Terrain Base Output ---
# Keyed by terrain name, values = base output for 1-2 foragers
TERRAIN_BASES = {
    "fjord": 4,
    "coast": 4,
    "inner_fjords": 4,
    "forest": 3,
    "pine": 3,
    "black_pine": 3,
    "moors": 1,
    "high_moors": 1,
    "river": 0,
    "ice": 0,
    "frozen_river": 0,
}

# Full table for reference
FORAGING_TABLE = {
    "fjord":  {"1-2": 4, "3-5": 10, "6-10": 18, "11+": 30},
    "forest": {"1-2": 3, "3-5": 8,  "6-10": 16, "11+": 28},
    "moors":  {"1-2": 1, "3-5": 3,  "6-10": 7,  "11+": 12},
    "ice":    {"1-2": 0, "3-5": 2,  "6-10": 4,  "11+": 8},
}

# Direct table lookup for precise foraging results
def lookup_base_output(terrain: str, num_foragers: int) -> int:
    """Look up base output from the exact foraging table."""
    # Normalize terrain
    terrain_key = terrain
    if terrain in ("coast", "inner_fjords", "fjord"):
        terrain_key = "fjord"
    elif terrain in ("pine", "black_pine", "forest"):
        terrain_key = "forest"
    elif terrain in ("high_moors", "moors"):
        terrain_key = "moors"
    elif terrain in ("river", "frozen_river", "ice"):
        terrain_key = "ice"

    table = FORAGING_TABLE.get(terrain_key, FORAGING_TABLE["forest"])

    if num_foragers <= 0:
        return 0
    elif num_foragers <= 2:
        return table["1-2"]
    elif num_foragers <= 5:
        return table["3-5"]
    elif num_foragers <= 10:
        return table["6-10"]
    else:
        return table["11+"]


# --- Season Multipliers ---
SEASON_MULT = {
    "long_summer": 1.0,
    "summer": 1.0,
    "long_dark": 0.7,
    "dark": 0.7,
}

# --- Weather Multipliers for Foraging ---
WEATHER_FORAGE_MULT = {
    "clear_grey": 1.0,
    "clear": 1.0,
    "rime_fog": 0.8,
    "light_rain": 0.9,
    "driving_snow": 0.5,
    "rime_storm": 0.0,   # impossible
    "the_hush": 1.0,
    "veil_thinning": 1.1,
    "blood_sun": 1.0,
}

# Food per person per day
FOOD_RATE = {"long_summer": 1.0, "summer": 1.0, "long_dark": 1.2, "dark": 1.2}


def forage(
    terrain: str,
    num_foragers: int,
    avg_skill: float = 0.0,
    season: str = "long_summer",
    weather: str = "clear",
) -> dict:
    """Simulate a foraging expedition. Returns food units gathered."""
    base = lookup_base_output(terrain, num_foragers)
    s_mult = SEASON_MULT.get(season, 1.0)
    w_mult = WEATHER_FORAGE_MULT.get(weather, 1.0)
    skill_bonus = 1.0 + (avg_skill * 0.08)

    raw_output = base * s_mult * w_mult * skill_bonus
    final_output = max(0, int(raw_output))

    return {
        "terrain": terrain,
        "num_foragers": num_foragers,
        "avg_forage_skill": avg_skill,
        "season": season,
        "weather": weather,
        "base_output": base,
        "season_mult": s_mult,
        "weather_mult": w_mult,
        "skill_bonus_mult": round(skill_bonus, 2),
        "raw_output": round(raw_output, 1),
        "food_gathered": final_output,
    }


def check_deficit(
    food_stores: int,
    band_size: int,
    season: str = "long_summer",
    days_ahead: int = 1,
) -> dict:
    """Check current food deficit/surplus status."""
    rate = FOOD_RATE.get(season, 1.0)
    daily_need = band_size * rate
    total_need = daily_need * days_ahead
    surplus = food_stores - total_need
    days_left = food_stores / daily_need if daily_need > 0 else 999

    return {
        "food_stores": food_stores,
        "band_size": band_size,
        "season": season,
        "daily_consumption": daily_need,
        "days_checked": days_ahead,
        "total_needed": total_need,
        "surplus_deficit": round(surplus, 1),
        "days_of_food_remaining": round(days_left, 1),
        "status": "surplus" if surplus >= 0 else "deficit",
        "morale_risk": days_left < 3,
    }


def print_table():
    """Print the full foraging reference table."""
    print("Foraging Output Table (food units per day)")
    print(f"{'Terrain':<15} {'1-2':>5} {'3-5':>5} {'6-10':>5} {'11+':>5}")
    print("-" * 40)
    for terrain, cols in FORAGING_TABLE.items():
        print(f"{terrain:<15} {cols['1-2']:>5} {cols['3-5']:>5} "
              f"{cols['6-10']:>5} {cols['11+']:>5}")
    print("\nLong Dark: multiply all by 0.7")
    print("Weather mults: rime_fog x0.8, driving_snow x0.5, rime_storm x0.0")


def main():
    parser = argparse.ArgumentParser(description="Iron Ledger Foraging Engine")
    subparsers = parser.add_subparsers(dest="command")

    # --- forage ---
    for_p = subparsers.add_parser("forage", help="Simulate foraging")
    for_p.add_argument("--terrain", type=str, required=True,
                       choices=list(TERRAIN_BASES.keys()))
    for_p.add_argument("--foragers", type=int, required=True)
    for_p.add_argument("--skill", type=float, default=0.0,
                       help="Average Forage skill of foragers")
    for_p.add_argument("--season", type=str, default="long_summer",
                       choices=list(SEASON_MULT.keys()))
    for_p.add_argument("--weather", type=str, default="clear",
                       choices=list(WEATHER_FORAGE_MULT.keys()))
    for_p.add_argument("--json", action="store_true")

    # --- deficit ---
    def_p = subparsers.add_parser("deficit", help="Check food deficit")
    def_p.add_argument("--food-stores", type=int, required=True)
    def_p.add_argument("--band-size", type=int, required=True)
    def_p.add_argument("--season", type=str, default="long_summer",
                       choices=list(SEASON_MULT.keys()))
    def_p.add_argument("--days-ahead", type=int, default=1)
    def_p.add_argument("--json", action="store_true")

    # --- table ---
    subparsers.add_parser("table", help="Print foraging reference table")

    args = parser.parse_args()

    if args.command == "forage":
        result = forage(
            args.terrain, args.foragers, args.skill,
            args.season, args.weather,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Foraging: {result['food_gathered']} food units")
            print(f"  Terrain: {args.terrain} (base {result['base_output']})")
            print(f"  Foragers: {args.foragers} (skill avg {args.skill})")
            print(f"  Season: {args.season} (x{result['season_mult']})")
            print(f"  Weather: {args.weather} (x{result['weather_mult']})")

    elif args.command == "deficit":
        result = check_deficit(
            args.food_stores, args.band_size,
            args.season, args.days_ahead,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Food stores: {result['food_stores']} units")
            print(f"Daily need: {result['daily_consumption']} ({args.band_size} people, {args.season})")
            print(f"Days remaining: {result['days_of_food_remaining']}")
            print(f"Status: {result['status'].upper()}")
            if result["morale_risk"]:
                print("WARNING: Morale risk (< 3 days of food)")

    elif args.command == "table":
        print_table()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
