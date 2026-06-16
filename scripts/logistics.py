#!/usr/bin/env python3
"""
Iron Ledger — Logistics Engine

Calculates supply burn, carrying capacity, march speed, and weight budgets
for a Svarthird band. All formulas from 20_SIMULATION_RULES.md §7.

Usage:
    python logistics.py supply --band-size 14 --season long_dark --days 3
    python logistics.py march --terrain forest --weather rime_fog --season long_dark --weak-link
    python logistics.py carry --might 6 --gear-kg 8
    python logistics.py band-weight --band-file band.json
"""

import argparse
import json
import sys

sys.path.insert(0, __file__ and __import__('os').path.dirname(__file__) or '.')
from engine import compute_carry_limit, compute_march_speed

# --- Terrain Multipliers ---
TERRAIN_MULT = {
    "coast": 1.0,
    "fjord": 1.0,
    "forest": 0.6,
    "pine": 0.6,
    "moors": 0.7,
    "river": 0.8,
    "ice": 0.8,
    "mountain": 0.4,
}

# --- Weather Multipliers ---
WEATHER_MULT = {
    "clear": 1.0,
    "clear_grey": 1.0,
    "rime_fog": 0.7,
    "light_rain": 0.9,
    "driving_snow": 0.5,
    "rime_storm": 0.2,
    "the_hush": 1.0,
    "veil_thinning": 1.0,
    "blood_sun": 0.5,
}

# --- Season Multipliers ---
SEASON_MULT = {
    "long_summer": 1.0,
    "summer": 1.0,
    "long_dark": 0.8,
    "dark": 0.8,
}

# --- Food consumption ---
FOOD_PER_PERSON_SUMMER = 1.0
FOOD_PER_PERSON_DARK = 1.2


def daily_food_consumption(band_size: int, season: str = "long_summer") -> float:
    """Calculate daily food units needed for the band."""
    rate = FOOD_PER_PERSON_DARK if "dark" in season else FOOD_PER_PERSON_SUMMER
    return band_size * rate


def food_for_days(band_size: int, days: int, season: str = "long_summer") -> float:
    """Calculate total food needed for a given number of days."""
    return daily_food_consumption(band_size, season) * days


def march_speed(
    terrain: str = "coast",
    weather: str = "clear",
    season: str = "long_summer",
    weak_link: bool = False,
    base_km: float = 25.0,
) -> dict:
    """Calculate march speed with all modifiers applied."""
    t_mult = TERRAIN_MULT.get(terrain, 1.0)
    w_mult = WEATHER_MULT.get(weather, 1.0)
    s_mult = SEASON_MULT.get(season, 1.0)

    speed = compute_march_speed(base_km, t_mult, w_mult, s_mult, weak_link)
    return {
        "base_km": base_km,
        "terrain": terrain,
        "terrain_mult": t_mult,
        "weather": weather,
        "weather_mult": w_mult,
        "season": season,
        "season_mult": s_mult,
        "weak_link": weak_link,
        "weak_link_mult": 0.85 if weak_link else 1.0,
        "final_km_per_day": speed,
    }


def carry_check(might: int, gear_kg: float) -> dict:
    """Check carrying capacity vs current load."""
    limit = compute_carry_limit(might)
    over = max(0.0, gear_kg - limit)
    return {
        "might": might,
        "carry_limit_kg": limit,
        "current_load_kg": gear_kg,
        "overloaded": over > 0,
        "excess_kg": round(over, 1),
        "penalty": "-10 all physical, march speed halved" if over > 0 else "none",
    }


def band_weight_summary(members: list[dict]) -> dict:
    """Summarize band weight budget. Each member dict needs 'name', 'might', 'gear_kg'."""
    total_weight = 0.0
    total_capacity = 0.0
    overloaded = []

    details = []
    for m in members:
        name = m.get("name", "unknown")
        might = m.get("might", m.get("mig", 5))
        gear = m.get("gear_kg", 5.0)
        limit = compute_carry_limit(might)
        total_weight += gear
        total_capacity += limit
        over = gear > limit
        if over:
            overloaded.append(name)
        details.append({
            "name": name,
            "carry_limit_kg": limit,
            "load_kg": gear,
            "overloaded": over,
        })

    return {
        "total_weight_kg": round(total_weight, 1),
        "total_capacity_kg": round(total_capacity, 1),
        "utilization_pct": round((total_weight / total_capacity * 100) if total_capacity else 0, 1),
        "overloaded_members": overloaded,
        "members": details,
    }


def travel_estimate(
    distance_km: float,
    terrain: str = "coast",
    weather: str = "clear",
    season: str = "long_summer",
    weak_link: bool = False,
    band_size: int = 14,
) -> dict:
    """Estimate travel time and food cost for a journey."""
    ms = march_speed(terrain, weather, season, weak_link)
    speed = ms["final_km_per_day"]
    if speed <= 0:
        days = 999
    else:
        days = distance_km / speed
    import math
    full_days = math.ceil(days)
    food_needed = food_for_days(band_size, full_days, season)

    return {
        "distance_km": distance_km,
        "march_speed_km_day": speed,
        "estimated_days": round(days, 1),
        "full_days": full_days,
        "food_needed": round(food_needed, 1),
        "conditions": ms,
    }


def main():
    parser = argparse.ArgumentParser(description="Iron Ledger Logistics Engine")
    subparsers = parser.add_subparsers(dest="command")

    # --- supply ---
    sup_p = subparsers.add_parser("supply", help="Calculate food requirements")
    sup_p.add_argument("--band-size", type=int, required=True)
    sup_p.add_argument("--season", type=str, default="long_summer",
                       choices=list(SEASON_MULT.keys()))
    sup_p.add_argument("--days", type=int, default=1)
    sup_p.add_argument("--json", action="store_true")

    # --- march ---
    mar_p = subparsers.add_parser("march", help="Calculate march speed")
    mar_p.add_argument("--terrain", type=str, default="coast",
                       choices=list(TERRAIN_MULT.keys()))
    mar_p.add_argument("--weather", type=str, default="clear",
                       choices=list(WEATHER_MULT.keys()))
    mar_p.add_argument("--season", type=str, default="long_summer",
                       choices=list(SEASON_MULT.keys()))
    mar_p.add_argument("--weak-link", action="store_true")
    mar_p.add_argument("--json", action="store_true")

    # --- carry ---
    car_p = subparsers.add_parser("carry", help="Check carrying capacity")
    car_p.add_argument("--might", type=int, required=True)
    car_p.add_argument("--gear-kg", type=float, required=True)
    car_p.add_argument("--json", action="store_true")

    # --- band-weight ---
    bw_p = subparsers.add_parser("band-weight", help="Band weight summary")
    bw_p.add_argument("--band-file", type=str, required=True, help="JSON file with member list")
    bw_p.add_argument("--json", action="store_true")

    # --- travel ---
    trv_p = subparsers.add_parser("travel", help="Estimate travel time and food cost")
    trv_p.add_argument("--distance", type=float, required=True, help="Distance in km")
    trv_p.add_argument("--terrain", type=str, default="coast",
                       choices=list(TERRAIN_MULT.keys()))
    trv_p.add_argument("--weather", type=str, default="clear",
                       choices=list(WEATHER_MULT.keys()))
    trv_p.add_argument("--season", type=str, default="long_summer",
                       choices=list(SEASON_MULT.keys()))
    trv_p.add_argument("--weak-link", action="store_true")
    trv_p.add_argument("--band-size", type=int, default=14)
    trv_p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "supply":
        daily = daily_food_consumption(args.band_size, args.season)
        total = food_for_days(args.band_size, args.days, args.season)
        result = {
            "band_size": args.band_size,
            "season": args.season,
            "food_per_day": daily,
            "days": args.days,
            "total_food_needed": total,
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Band size: {args.band_size}, Season: {args.season}")
            print(f"Daily food: {daily} units")
            print(f"Total for {args.days} day(s): {total} food units")

    elif args.command == "march":
        result = march_speed(args.terrain, args.weather, args.season, args.weak_link)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"March speed: {result['final_km_per_day']} km/day")
            print(f"  Terrain: {args.terrain} (x{result['terrain_mult']})")
            print(f"  Weather: {args.weather} (x{result['weather_mult']})")
            print(f"  Season: {args.season} (x{result['season_mult']})")
            if args.weak_link:
                print(f"  Weak link: x0.85")

    elif args.command == "carry":
        result = carry_check(args.might, args.gear_kg)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Carry limit: {result['carry_limit_kg']} kg (Might {args.might})")
            print(f"Current load: {result['current_load_kg']} kg")
            if result["overloaded"]:
                print(f"OVERLOADED by {result['excess_kg']} kg!")
                print(f"Penalty: {result['penalty']}")
            else:
                print("Within capacity.")

    elif args.command == "band-weight":
        with open(args.band_file, 'r', encoding='utf-8') as f:
            members = json.load(f)
        result = band_weight_summary(members)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Total weight: {result['total_weight_kg']} / {result['total_capacity_kg']} kg "
                  f"({result['utilization_pct']}%)")
            if result["overloaded_members"]:
                print(f"Overloaded: {', '.join(result['overloaded_members'])}")

    elif args.command == "travel":
        result = travel_estimate(
            args.distance, args.terrain, args.weather,
            args.season, args.weak_link, args.band_size,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Distance: {args.distance} km")
            print(f"Speed: {result['march_speed_km_day']} km/day")
            print(f"Estimated: {result['full_days']} day(s)")
            print(f"Food needed: {result['food_needed']} units")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
