#!/usr/bin/env python3
"""
Iron Ledger — Travel Simulator

Simulates multi-day travel with terrain hazards, weather effects, food
consumption, and random events. Integrates logistics, weather, and foraging.

Usage:
    python travel.py simulate --distance 80 --terrain forest --season long_dark --band-size 14 --food-stores 30
    python travel.py hazard --terrain mountain --weather driving_snow --season long_dark
    python travel.py route --segments '[{"distance":40,"terrain":"coast"},{"distance":30,"terrain":"forest"}]'
"""

import argparse
import json
import math
import random
import sys

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import resolve_check, roll_d100, ResultLevel
from logistics import (
    march_speed, daily_food_consumption, TERRAIN_MULT, WEATHER_MULT, SEASON_MULT
)
from weather import generate_weather, WEATHER_MODIFIERS
from animal_system import travel_companion_profile

import yaml

# --- Terrain Hazards ---
TERRAIN_HAZARDS = {
    "coast": [
        (15, "rough_surf", "Heavy surf blocks coastal path. Half-day detour.", 0.5),
        (8, "rockslide", "Loose rocks injure a fighter. Heal check needed.", 0),
        (5, "tidal_trap", "Rising tide traps the band. Wait 4 hours.", 0.25),
    ],
    "forest": [
        (12, "fallen_trees", "Blocked path requires clearing. Half-day lost.", 0.5),
        (10, "predator", "Wolf pack shadows the band. Intimidate or fight.", 0),
        (6, "bog", "Hidden bog slows march and risks gear loss.", 0.25),
    ],
    "moors": [
        (15, "fog_lost", "Dense fog causes navigation error. WIT+Navigate check.", 0.5),
        (10, "sinkhole", "A fighter steps into a sinkhole. TOU check or injury.", 0),
        (5, "exposure", "Wind exposure saps warmth. Extra food consumption.", 0),
    ],
    "mountain": [
        (18, "avalanche_risk", "Avalanche terrain. NIM check per fighter or 2d6 damage.", 0),
        (12, "cliff_face", "Steep climb requires ropes. Half-day penalty.", 0.5),
        (8, "altitude", "Thin air causes exhaustion. -5 all rolls for 1 day.", 0),
    ],
    "river": [
        (15, "thin_ice", "Ice cracks underfoot. NIM check or fall through.", 0),
        (10, "crossing", "Difficult river crossing. Half-day delay.", 0.5),
        (5, "current", "Strong current sweeps away supplies. Lose 1d6 food units.", 0),
    ],
    "ice": [
        (20, "crevasse", "Hidden crevasse. WIT+Navigate check or fall.", 0),
        (12, "whiteout", "Total whiteout. Full day lost navigating.", 1.0),
        (8, "ice_quake", "Ice shifts and cracks. Morale check (the_hush_extended).", 0),
    ],
}

# Default for terrains without specific hazards
DEFAULT_HAZARDS = [
    (10, "minor_delay", "Minor obstacle delays the band.", 0.25),
    (5, "injured_fighter", "A fighter is injured on the trail.", 0),
]


def check_daily_hazard(terrain: str, weather: str) -> dict | None:
    """Roll for a terrain hazard during a day's march."""
    hazards = TERRAIN_HAZARDS.get(terrain, DEFAULT_HAZARDS)

    # Bad weather increases hazard chance
    weather_hazard_mult = 1.0
    if weather in ("driving_snow", "rime_storm"):
        weather_hazard_mult = 1.5
    elif weather in ("rime_fog",):
        weather_hazard_mult = 1.2

    roll = roll_d100()

    for chance_pct, haz_type, description, day_penalty in hazards:
        threshold = int(chance_pct * weather_hazard_mult)
        if roll <= threshold:
            return {
                "hazard": haz_type,
                "description": description,
                "day_penalty": day_penalty,
                "roll": roll,
                "threshold": threshold,
            }

    return None


def simulate_travel(
    distance_km: float,
    terrain: str,
    season: str,
    band_size: int,
    food_stores: float,
    weak_link: bool = False,
    horse: dict | None = None,
    dogs: list[dict] | None = None,
) -> dict:
    """Simulate a multi-day journey with weather, hazards, and food tracking."""
    season_key = "long_dark" if "dark" in season else "long_summer"
    day_log = []
    remaining_distance = distance_km
    remaining_food = food_stores
    total_days = 0
    hazards_hit = []
    food_ran_out = False

    while remaining_distance > 0:
        total_days += 1
        if total_days > 100:  # safety cap
            break

        # Generate weather for the day
        weather_result = generate_weather(season_key)
        weather = weather_result["weather"]

        # Calculate march speed
        ms = march_speed(terrain, weather, season_key, weak_link)
        daily_km = ms["final_km_per_day"]
        animal_support = travel_companion_profile(horse, dogs, terrain=terrain, weather=weather)
        daily_km += animal_support["speed_bonus_km"]

        # Check for hazard
        hazard = check_daily_hazard(terrain, weather)
        day_penalty = 0
        if hazard:
            buffered_penalty = max(0.0, hazard["day_penalty"] - (0.1 * animal_support["hazard_buffer"]))
            day_penalty = hazard["day_penalty"]
            hazards_hit.append(hazard)
            # Reduce effective distance covered
            daily_km *= max(0, 1.0 - buffered_penalty)

        km_covered = min(daily_km, remaining_distance)
        remaining_distance -= km_covered

        # Food consumption
        daily_food = daily_food_consumption(band_size, season_key)
        # Exposure in bad weather on moors/mountain increases food need
        if weather in ("driving_snow", "rime_storm") and terrain in ("moors", "mountain", "ice"):
            daily_food *= 1.3
        remaining_food -= daily_food

        if remaining_food < 0 and not food_ran_out:
            food_ran_out = True

        day_log.append({
            "day": total_days,
            "weather": weather,
            "km_covered": round(km_covered, 1),
            "remaining_km": round(max(0, remaining_distance), 1),
            "food_consumed": round(daily_food, 1),
            "food_remaining": round(remaining_food, 1),
            "hazard": hazard,
            "animal_support": animal_support if any(animal_support.values()) else None,
        })

    return {
        "distance_km": distance_km,
        "terrain": terrain,
        "season": season_key,
        "band_size": band_size,
        "total_days": total_days,
        "arrived": remaining_distance <= 0,
        "food_stores_start": food_stores,
        "food_stores_end": round(remaining_food, 1),
        "food_deficit": food_ran_out,
        "hazards_count": len(hazards_hit),
        "hazards": hazards_hit,
        "day_log": day_log,
    }


def route_travel(segments: list[dict], season: str, band_size: int,
                 food_stores: float, weak_link: bool = False,
                 horse: dict | None = None, dogs: list[dict] | None = None) -> dict:
    """Simulate travel across multiple terrain segments."""
    total_days = 0
    remaining_food = food_stores
    all_hazards = []
    segment_results = []
    arrived = True

    for seg in segments:
        dist = seg.get("distance", 0)
        terrain = seg.get("terrain", "coast")
        result = simulate_travel(dist, terrain, season, band_size,
                                 remaining_food, weak_link, horse=horse, dogs=dogs)
        if not result.get("arrived", False):
            arrived = False
        remaining_food = result["food_stores_end"]
        total_days += result["total_days"]
        all_hazards.extend(result["hazards"])
        segment_results.append({
            "terrain": terrain,
            "distance_km": dist,
            "days": result["total_days"],
            "hazards": len(result["hazards"]),
            "food_consumed": round(food_stores - remaining_food
                                   if not segment_results
                                   else segment_results[-1].get("_food_end", food_stores) - remaining_food, 1),
            "_food_end": remaining_food,
        })

    # Clean internal fields
    for sr in segment_results:
        sr.pop("_food_end", None)

    return {
        "total_distance_km": sum(s.get("distance", 0) for s in segments),
        "total_days": total_days,
        "arrived": arrived,
        "season": season,
        "band_size": band_size,
        "food_stores_start": food_stores,
        "food_stores_end": round(remaining_food, 1),
        "total_hazards": len(all_hazards),
        "segments": segment_results,
        "hazards": all_hazards,
    }


def terrain_hazard_info(terrain: str) -> dict:
    """List possible hazards for a terrain type."""
    hazards = TERRAIN_HAZARDS.get(terrain, DEFAULT_HAZARDS)
    return {
        "terrain": terrain,
        "hazards": [
            {"chance_pct": h[0], "type": h[1], "description": h[2], "day_penalty": h[3]}
            for h in hazards
        ],
    }


# --- Fine-grained → broad terrain mapping ---

TERRAIN_CATEGORY_MAP = {
    "fjord_ridge": "fjord", "fjord_shore": "fjord", "fjord_slope": "fjord",
    "pine_slope": "forest", "pine_clearing": "forest", "dense_pine": "forest",
    "old_growth": "forest", "canopy_dark": "forest", "forest_stream": "forest",
    "sea_cliff": "coast", "shingle_beach": "coast", "rocky_shore": "coast",
    "harbour_approach": "coast", "tidal_flat": "coast",
    "open_moor": "moors", "peat_bog": "moors", "heather_heath": "moors",
    "exposed_heath": "moors", "thorn_scrub": "moors",
    "rime_moor": "iron_moor", "iron_ridge": "iron_moor", "rocky_plateau": "iron_moor",
    "granite_peak": "mountain", "knife_ridge": "mountain", "alpine_scree": "mountain",
    "mountain_pass": "mountain", "cliff_face": "mountain",
    "ice_field": "ice", "permafrost": "ice", "snowfield": "ice",
    "glacial_moraine": "ice", "frozen_shore": "ice",
    "underground_hall": "underground", "mine_tunnel": "underground",
    "stone_ravine": "underground",
    "bare_rock": "mountain", "iron_moor": "iron_moor",
}

# Keywords for fallback terrain inference
_TERRAIN_KEYWORDS = [
    ("coast", "coast"), ("fjord", "fjord"), ("forest", "forest"),
    ("pine", "forest"), ("moor", "moors"), ("mountain", "mountain"),
    ("ice", "ice"), ("river", "river"), ("mine", "underground"),
    ("underground", "underground"), ("barrow", "moors"),
]

# Map broad encounter categories to logistics terrain keys
_LOGISTICS_TERRAIN_MAP = {
    "iron_moor": "moors",
    "underground": "mountain",
    "barrow_downs": "moors",
}

# Season name mappings between systems
_SEASON_TO_ENCOUNTER = {
    "spring": "thaw", "summer": "long_sun", "autumn": "harvest",
    "winter": "long_dark",
    "long_summer": "long_sun", "long_dark": "long_dark",
    "thaw": "thaw", "long_sun": "long_sun", "harvest": "harvest",
}

_SEASON_TO_LOGISTICS = {
    "spring": "long_summer", "summer": "long_summer",
    "autumn": "long_summer", "winter": "long_dark",
    "long_summer": "long_summer", "long_dark": "long_dark",
    "thaw": "long_summer", "long_sun": "long_summer",
    "harvest": "long_summer",
}

_SEASON_TO_ACCESS = {
    "long_summer": "summer", "long_dark": "winter",
    "long_sun": "summer", "thaw": "spring", "harvest": "autumn",
    "spring": "spring", "summer": "summer",
    "autumn": "autumn", "winter": "winter",
}


def _data_path(filename: str) -> str:
    """Return absolute path to a file under data/geography/."""
    return os.path.join(os.path.dirname(__file__), "..", "data", "geography", filename)


def load_routes() -> list[dict]:
    """Load routes.yaml and return list of route dicts."""
    with open(_data_path("routes.yaml"), "r") as f:
        data = yaml.safe_load(f)
    return data.get("routes", [])


def load_encounters() -> dict:
    """Load terrain_encounters.yaml and return the terrain_encounters dict."""
    with open(_data_path("terrain_encounters.yaml"), "r") as f:
        data = yaml.safe_load(f)
    return data.get("terrain_encounters", {})


def load_atlas() -> dict:
    """Load atlas.yaml and return dict keyed by location ID → location dict."""
    with open(_data_path("atlas.yaml"), "r") as f:
        data = yaml.safe_load(f)
    locations = data.get("locations", [])
    return {loc["id"]: loc for loc in locations if "id" in loc}


def resolve_terrain_category(fine_terrain: str) -> str:
    """Map a fine-grained terrain name to a broad encounter/logistics category."""
    # Direct lookup
    if fine_terrain in TERRAIN_CATEGORY_MAP:
        return TERRAIN_CATEGORY_MAP[fine_terrain]
    # Already a broad category
    if fine_terrain in TERRAIN_MULT:
        return fine_terrain
    # Keyword fallback
    lower = fine_terrain.lower()
    for keyword, category in _TERRAIN_KEYWORDS:
        if keyword in lower:
            return category
    return "moors"


def _logistics_terrain(category: str) -> str:
    """Convert a broad encounter category to a logistics-compatible terrain key."""
    if category in TERRAIN_MULT:
        return category
    return _LOGISTICS_TERRAIN_MAP.get(category, "moors")


def roll_encounter(terrain_category: str, season: str,
                   encounters_data: dict) -> dict | None:
    """Roll against a terrain's encounter table for the given season.

    Returns the first encounter that triggers, or None.
    """
    enc_season = _SEASON_TO_ENCOUNTER.get(season, season)
    terrain_block = encounters_data.get(terrain_category)
    if not terrain_block:
        return None
    encounter_list = terrain_block.get("encounters", [])
    for enc in encounter_list:
        if enc_season not in enc.get("seasons", []):
            continue
        roll = roll_d100()
        if roll <= enc.get("chance_percent", 0):
            return {**enc, "_roll": roll}
    return None


def named_route_travel(
    route_id_or_name: str,
    season: str,
    band_size: int,
    food_stores: float,
    weak_link: bool = False,
    horse: dict | None = None,
    dogs: list[dict] | None = None,
) -> dict:
    """Simulate travel along a named route from routes.yaml.

    Walks each terrain segment day-by-day, rolling weather, encounters,
    and tracking food, landmarks, and shelters.
    """
    routes = load_routes()
    encounters_data = load_encounters()
    atlas = load_atlas()

    # Find route by ID or name (case-insensitive partial match)
    route = None
    needle = route_id_or_name.strip().lower()
    for r in routes:
        if r["id"].lower() == needle or needle in r.get("name", "").lower():
            route = r
            break
    if route is None:
        return {"error": f"Route not found: {route_id_or_name}"}

    logistics_season = _SEASON_TO_LOGISTICS.get(season, "long_summer")
    access_season = _SEASON_TO_ACCESS.get(season, "summer")
    seasonal_access = route.get("seasonal_access", {}).get(access_season, "unknown")

    # Pre-index shelters and landmarks by distance_from_start
    shelters = route.get("shelters", [])
    landmark_ids = route.get("landmarks", [])
    landmark_names = {}
    for lid in landmark_ids:
        loc = atlas.get(lid)
        if loc:
            landmark_names[lid] = loc.get("name", lid)
        else:
            landmark_names[lid] = lid

    day_log = []
    remaining_food = food_stores
    total_days = 0
    total_encounters = 0
    km_from_start = 0.0
    food_ran_out = False

    for seg in route.get("terrain_segments", []):
        seg_terrain_fine = seg.get("terrain", "open_moor")
        seg_distance = seg.get("distance_km", 0)
        seg_description = seg.get("description", "")
        broad_terrain = resolve_terrain_category(seg_terrain_fine)
        log_terrain = _logistics_terrain(broad_terrain)
        remaining_seg = seg_distance

        while remaining_seg > 0:
            total_days += 1
            if total_days > 200:
                break

            # Weather
            weather_result = generate_weather(logistics_season)
            weather = weather_result["weather"]

            # March speed
            ms = march_speed(log_terrain, weather, logistics_season, weak_link)
            daily_km = ms["final_km_per_day"]
            animal_support = travel_companion_profile(
                horse, dogs, terrain=broad_terrain, weather=weather
            )
            daily_km += animal_support["speed_bonus_km"]

            # Hazard from existing terrain hazard system
            hazard = check_daily_hazard(log_terrain, weather)
            if hazard:
                buffered_penalty = max(0.0, hazard["day_penalty"] - (0.1 * animal_support["hazard_buffer"]))
                daily_km *= max(0, 1.0 - buffered_penalty)

            km_covered = min(daily_km, remaining_seg)
            remaining_seg -= km_covered
            prev_km = km_from_start
            km_from_start += km_covered

            # Food
            daily_food = daily_food_consumption(band_size, logistics_season)
            if weather in ("driving_snow", "rime_storm") and log_terrain in ("moors", "mountain", "ice"):
                daily_food *= 1.3
            remaining_food -= daily_food
            if remaining_food < 0 and not food_ran_out:
                food_ran_out = True

            # Encounter from terrain_encounters.yaml
            encounter = roll_encounter(broad_terrain, season, encounters_data)
            if encounter:
                if animal_support["encounter_notice"] > 0:
                    encounter["animal_notice_bonus"] = animal_support["encounter_notice"]
                total_encounters += 1

            # Landmarks passed this day
            day_landmarks = []
            total_route_km = route.get("distance_km", 0)
            for i, lid in enumerate(landmark_ids):
                # Distribute landmarks evenly along the route if no explicit
                # distance data; use fraction-based positioning
                if total_route_km > 0:
                    lm_km = total_route_km * (i + 1) / (len(landmark_ids) + 1)
                else:
                    lm_km = 0
                if prev_km < lm_km <= km_from_start:
                    day_landmarks.append({
                        "id": lid,
                        "name": landmark_names.get(lid, lid),
                    })

            # Shelters available based on distance
            day_shelters = []
            for sh in shelters:
                sh_km = sh.get("distance_from_start_km", 0)
                if prev_km <= sh_km <= km_from_start:
                    day_shelters.append(sh)

            day_entry = {
                "day": total_days,
                "terrain_segment": seg_terrain_fine,
                "terrain_category": broad_terrain,
                "weather": weather,
                "km_covered": round(km_covered, 1),
                "km_from_start": round(km_from_start, 1),
                "food_consumed": round(daily_food, 1),
                "food_remaining": round(remaining_food, 1),
                "hazard": hazard,
                "encounter": _encounter_summary(encounter) if encounter else None,
                "landmarks": day_landmarks if day_landmarks else None,
                "shelter": day_shelters if day_shelters else None,
                "animal_support": animal_support if any(animal_support.values()) else None,
            }
            day_log.append(day_entry)

    return {
        "route_id": route["id"],
        "route_name": route["name"],
        "from": route.get("from_settlement", ""),
        "to": route.get("to_settlement", ""),
        "distance_km": route.get("distance_km", 0),
        "season": season,
        "seasonal_access": seasonal_access,
        "band_size": band_size,
        "total_days": total_days,
        "food_stores_start": food_stores,
        "food_stores_end": round(remaining_food, 1),
        "food_deficit": food_ran_out,
        "encounters_count": total_encounters,
        "tracking_bonus": travel_companion_profile(
            horse, dogs, terrain="route", weather=""
        )["tracking_bonus"],
        "day_log": day_log,
    }


def _encounter_summary(enc: dict) -> dict:
    """Extract printable fields from an encounter dict."""
    return {
        "id": enc.get("id", ""),
        "name": enc.get("name", ""),
        "category": enc.get("category", ""),
        "severity": enc.get("severity", ""),
        "check": enc.get("check", ""),
        "success_benefit": enc.get("success_benefit", ""),
        "failure_consequence": enc.get("failure_consequence", ""),
        "duration_hours": enc.get("duration_hours", 0),
        "description": enc.get("description", ""),
        "animal_notice_bonus": enc.get("animal_notice_bonus", 0),
    }


def list_routes(from_settlement: str | None = None) -> list[dict]:
    """Return summary info for all routes, optionally filtered by departure."""
    routes = load_routes()
    results = []
    for r in routes:
        if from_settlement:
            if from_settlement.lower() not in r.get("from_settlement", "").lower():
                continue
        results.append({
            "id": r["id"],
            "name": r.get("name", ""),
            "from": r.get("from_settlement", ""),
            "to": r.get("to_settlement", ""),
            "distance_km": r.get("distance_km", 0),
            "travel_days_summer": r.get("travel_days_summer", "?"),
            "travel_days_winter": r.get("travel_days_winter", "?"),
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Iron Ledger Travel Simulator")
    subparsers = parser.add_subparsers(dest="command")

    # --- simulate ---
    sim_p = subparsers.add_parser("simulate", help="Simulate a journey")
    sim_p.add_argument("--distance", type=float, required=True, help="Distance in km")
    sim_p.add_argument("--terrain", type=str, default="coast",
                       choices=list(TERRAIN_MULT.keys()))
    sim_p.add_argument("--season", type=str, default="long_summer")
    sim_p.add_argument("--band-size", type=int, default=14)
    sim_p.add_argument("--food-stores", type=float, default=30)
    sim_p.add_argument("--weak-link", action="store_true")
    sim_p.add_argument("--horse-json", type=str, default=None)
    sim_p.add_argument("--dogs-json", type=str, default=None)
    sim_p.add_argument("--json", action="store_true")

    # --- hazard ---
    haz_p = subparsers.add_parser("hazard", help="Show terrain hazard table")
    haz_p.add_argument("--terrain", type=str, required=True,
                       choices=list(TERRAIN_HAZARDS.keys()))
    haz_p.add_argument("--json", action="store_true")

    # --- route ---
    rte_p = subparsers.add_parser("route", help="Multi-segment route travel")
    rte_p.add_argument("--segments", type=str, required=True, help="JSON array of segments")
    rte_p.add_argument("--season", type=str, default="long_summer")
    rte_p.add_argument("--band-size", type=int, default=14)
    rte_p.add_argument("--food-stores", type=float, default=50)
    rte_p.add_argument("--weak-link", action="store_true")
    rte_p.add_argument("--horse-json", type=str, default=None)
    rte_p.add_argument("--dogs-json", type=str, default=None)
    rte_p.add_argument("--json", action="store_true")

    # --- named-route ---
    nr_p = subparsers.add_parser("named-route", help="Travel a named route from routes.yaml")
    nr_p.add_argument("--route", type=str, required=True,
                      help="Route ID (e.g. RTE_007) or name substring")
    nr_p.add_argument("--season", type=str, default="long_sun")
    nr_p.add_argument("--band-size", type=int, default=14)
    nr_p.add_argument("--food-stores", type=float, default=50)
    nr_p.add_argument("--weak-link", action="store_true")
    nr_p.add_argument("--horse-json", type=str, default=None)
    nr_p.add_argument("--dogs-json", type=str, default=None)
    nr_p.add_argument("--json", action="store_true")

    # --- list-routes ---
    lr_p = subparsers.add_parser("list-routes", help="List available routes")
    lr_p.add_argument("--from", dest="from_settlement", type=str, default=None,
                      help="Filter by departure settlement")
    lr_p.add_argument("--json", action="store_true")

    # --- encounter ---
    enc_p = subparsers.add_parser("encounter", help="Roll a random encounter")
    enc_p.add_argument("--terrain", type=str, required=True,
                       help="Broad terrain category (coast, forest, moors, etc.)")
    enc_p.add_argument("--season", type=str, default="long_sun")
    enc_p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "simulate":
        horse = json.loads(args.horse_json) if args.horse_json else None
        dogs = json.loads(args.dogs_json) if args.dogs_json else None
        result = simulate_travel(args.distance, args.terrain, args.season,
                                 args.band_size, args.food_stores, args.weak_link,
                                 horse=horse, dogs=dogs)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Journey: {result['distance_km']} km through {result['terrain']}")
            print(f"  Days: {result['total_days']}")
            print(f"  Arrived: {'Yes' if result['arrived'] else 'No'}")
            print(f"  Food: {result['food_stores_start']} → {result['food_stores_end']}")
            print(f"  Hazards: {result['hazards_count']}")
            for h in result['hazards']:
                print(f"    - {h['hazard']}: {h['description']}")

    elif args.command == "hazard":
        result = terrain_hazard_info(args.terrain)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Hazards for {result['terrain']}:")
            for h in result["hazards"]:
                print(f"  [{h['chance_pct']}%] {h['type']}: {h['description']}")

    elif args.command == "route":
        segments = json.loads(args.segments)
        horse = json.loads(args.horse_json) if args.horse_json else None
        dogs = json.loads(args.dogs_json) if args.dogs_json else None
        result = route_travel(segments, args.season, args.band_size,
                              args.food_stores, args.weak_link, horse=horse, dogs=dogs)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Route: {result['total_distance_km']} km, {result['total_days']} days")
            for s in result["segments"]:
                print(f"  {s['terrain']}: {s['distance_km']} km in {s['days']} days")
            print(f"  Food: {result['food_stores_start']} → {result['food_stores_end']}")
            print(f"  Hazards: {result['total_hazards']}")

    elif args.command == "named-route":
        horse = json.loads(args.horse_json) if args.horse_json else None
        dogs = json.loads(args.dogs_json) if args.dogs_json else None
        result = named_route_travel(args.route, args.season, args.band_size,
                                    args.food_stores, args.weak_link,
                                    horse=horse, dogs=dogs)
        if "error" in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Route: {result['route_name']} — {result['from']} → {result['to']}")
            print(f"Season: {result['season']} | Band: {result['band_size']}"
                  f" | Food: {result['food_stores_start']} units")
            print(f"Seasonal access: {result['seasonal_access']}")
            print()
            for d in result["day_log"]:
                print(f"Day {d['day']} — {d['terrain_segment']} ({d['terrain_category']})")
                print(f"  Weather: {d['weather']} | Covered: {d['km_covered']} km"
                      f" | Food: {d['food_remaining']}")
                if d.get("landmarks"):
                    for lm in d["landmarks"]:
                        print(f"  Landmark: {lm['name']}")
                if d.get("shelter"):
                    for sh in d["shelter"]:
                        print(f"  Shelter available: {sh['name']}"
                              f" (capacity {sh.get('capacity', '?')},"
                              f" {sh.get('quality', '?')} quality)")
                if d.get("encounter"):
                    enc = d["encounter"]
                    print(f"  Encounter: {enc['name']} [{enc['category']},"
                          f" {enc['severity']}]")
                    print(f"    Check: {enc['check']}"
                          f" — Success: {enc['success_benefit']}"
                          f" Failure: {enc['failure_consequence']}")
                elif d.get("hazard"):
                    hz = d["hazard"]
                    print(f"  Hazard: {hz['hazard']} — {hz['description']}")
                else:
                    print("  No encounter.")
            print()
            print(f"ARRIVED in {result['total_days']} days."
                  f" Food: {result['food_stores_end']} remaining."
                  f" Encounters: {result['encounters_count']}.")

    elif args.command == "list-routes":
        routes = list_routes(args.from_settlement)
        if args.json:
            print(json.dumps(routes, indent=2))
        else:
            if not routes:
                print("No routes found.")
            else:
                for r in routes:
                    print(f"[{r['id']}] {r['name']}")
                    print(f"  {r['from']} → {r['to']} | {r['distance_km']} km"
                          f" | summer {r['travel_days_summer']}d"
                          f" / winter {r['travel_days_winter']}d")

    elif args.command == "encounter":
        encounters_data = load_encounters()
        enc = roll_encounter(args.terrain, args.season, encounters_data)
        if args.json:
            print(json.dumps(enc, indent=2) if enc else json.dumps(None))
        else:
            if enc:
                print(f"Encounter: {enc.get('name', '?')}"
                      f" [{enc.get('category', '?')}, {enc.get('severity', '?')}]")
                print(f"  {enc.get('description', '')}")
                print(f"  Check: {enc.get('check', 'none')}")
                print(f"  Success: {enc.get('success_benefit', '')}")
                print(f"  Failure: {enc.get('failure_consequence', '')}")
                print(f"  Duration: {enc.get('duration_hours', 0)}h"
                      f" | Roll: {enc.get('_roll', '?')}")
            else:
                print("No encounter triggered.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
