#!/usr/bin/env python3
"""Scenario dispatcher for multi-script campaign simulation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from travel import simulate_travel
from weather import generate_weather
from foraging import forage
from logistics import march_speed
from settlement import settlement_economy_profile
from npc_manager import load_all_npcs
from contracts import generate_contracts

ROOT = Path(__file__).resolve().parent.parent
BAND_FILE = ROOT / "data" / "band_state.yaml"


def _load_band() -> dict:
    with open(BAND_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def scenario_overland(distance: float, terrain: str, days: int, band_size: int, food_stores: float, season: str) -> dict:
    travel = simulate_travel(distance, terrain, season, band_size, food_stores)
    weather = generate_weather("long_dark" if "dark" in season else "long_summer")
    forage_out = forage(terrain, max(1, band_size // 3), 1.0, season, weather.get("weather", "clear"))
    march = march_speed(terrain, weather.get("weather", "clear"), season)
    food_delta = forage_out.get("food_gathered", 0) - travel.get("day_log", [{}])[-1].get("food_consumed", 0)
    return {
        "scenario": "overland_travel",
        "travel": travel,
        "weather": weather,
        "foraging": forage_out,
        "march": march,
        "food_delta": round(food_delta, 1),
    }


def scenario_camp_night(terrain: str, band_size: int, food_stores: float, season: str) -> dict:
    weather = generate_weather("long_dark" if "dark" in season else "long_summer")
    forage_out = forage(terrain, max(1, band_size // 4), 1.0, season, weather.get("weather", "clear"))
    encounter_roll = weather.get("roll", 50)
    encounter = encounter_roll <= 20
    food_delta = forage_out.get("food_gathered", 0) - (band_size * (1.2 if "dark" in season else 1.0))
    return {
        "scenario": "camp_night",
        "terrain": terrain,
        "season": season,
        "weather": weather,
        "encounter": encounter,
        "encounter_roll": encounter_roll,
        "foraging": forage_out,
        "food_delta": round(food_delta, 1),
    }


def scenario_settlement_visit(settlement: str) -> dict:
    econ = settlement_economy_profile(settlement)
    npcs = [n for n in load_all_npcs() if settlement.lower() in (n.get("settlement", "").lower(), n.get("base", "").lower())]
    contracts = generate_contracts(reputation=2, settlement_type="village", season="long_dark")
    return {
        "scenario": "settlement_visit",
        "settlement": settlement,
        "economy": econ,
        "npcs": [{"id": n.get("id"), "name": n.get("name"), "role": n.get("role") or n.get("type")} for n in npcs[:15]],
        "contracts": contracts,
    }


def scenario_contract_assessment() -> dict:
    band = _load_band().get("band", {})
    contract = band.get("current_contract") or {}
    day = int(band.get("day_of_year", 0))
    deadline = int(contract.get("deadline_day", day))
    days_left = max(0, deadline - day)
    pay = int(contract.get("payment_silver", 0))
    morale = int(band.get("morale", 3))
    readiness = morale * 10 + max(0, 30 - days_left)
    if days_left <= 3:
        recommendation = "retreat_or_urgent_push"
    elif readiness >= 60:
        recommendation = "go"
    else:
        recommendation = "hold"
    return {
        "scenario": "contract_assessment",
        "contract": contract,
        "day": day,
        "days_left": days_left,
        "payment_silver": pay,
        "morale": morale,
        "readiness_score": readiness,
        "recommendation": recommendation,
    }


def _emit(result: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Scenario runner")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("overland_travel")
    p.add_argument("--distance", type=float, required=True)
    p.add_argument("--terrain", required=True)
    p.add_argument("--days", type=int, required=True)
    p.add_argument("--band-size", type=int, required=True)
    p.add_argument("--food-stores", type=float, required=True)
    p.add_argument("--season", required=True)
    p.add_argument("--format", choices=["text", "json"], default="text")

    p = sub.add_parser("camp_night")
    p.add_argument("--terrain", required=True)
    p.add_argument("--band-size", type=int, required=True)
    p.add_argument("--food-stores", type=float, required=True)
    p.add_argument("--season", required=True)
    p.add_argument("--format", choices=["text", "json"], default="text")

    p = sub.add_parser("settlement_visit")
    p.add_argument("--settlement", required=True)
    p.add_argument("--format", choices=["text", "json"], default="text")

    p = sub.add_parser("contract_assessment")
    p.add_argument("--format", choices=["text", "json"], default="text")

    args = parser.parse_args()

    if args.cmd == "overland_travel":
        r = scenario_overland(args.distance, args.terrain, args.days, args.band_size, args.food_stores, args.season)
        _emit(r, args.format == "json")
    elif args.cmd == "camp_night":
        r = scenario_camp_night(args.terrain, args.band_size, args.food_stores, args.season)
        _emit(r, args.format == "json")
    elif args.cmd == "settlement_visit":
        r = scenario_settlement_visit(args.settlement)
        _emit(r, args.format == "json")
    elif args.cmd == "contract_assessment":
        r = scenario_contract_assessment()
        _emit(r, args.format == "json")


if __name__ == "__main__":
    main()
