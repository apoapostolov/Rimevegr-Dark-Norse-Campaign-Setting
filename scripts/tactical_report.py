#!/usr/bin/env python3
"""Strategist tactical assessment tool."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BAND_FILE = ROOT / "data" / "band_state.yaml"


def _load_band() -> dict:
    with open(BAND_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def readiness() -> dict:
    payload = _load_band()
    band = payload.get("band", {})
    members = payload.get("members", [])

    wounded_count = len([m for m in members if m.get("status") == "wounded"])
    exhausted_count = len([m for m in members if "exhaust" in " ".join(m.get("special_conditions", [])).lower()])
    band_size = len([m for m in members if m.get("status") not in ("dead", "left", "deserted")])

    effective_fighters = max(0, band_size - wounded_count - exhausted_count)

    food_units = 0
    for n in band.get("notes", []) or []:
        if "Food stores:" in str(n):
            digits = "".join(ch for ch in str(n) if ch.isdigit())
            if digits:
                food_units = int(digits)
                break
    supply_days = round(food_units / max(1, (band_size / 2.0)), 1) if food_units else 0.0
    morale = int(band.get("morale", 3))
    morale_modifier = (morale - 4) * 5

    return {
        "day": band.get("day_of_year"),
        "band_size": band_size,
        "effective_fighters": effective_fighters,
        "wounded_count": wounded_count,
        "exhausted_count": exhausted_count,
        "food_units": food_units,
        "supply_days": supply_days,
        "morale": morale,
        "morale_modifier": morale_modifier,
    }


def assess(enemy_count: int, enemy_rank: str, terrain: str, season: str) -> dict:
    rd = readiness()
    rank_mod = {"rabble": -10, "common": 0, "veteran": 10, "elite": 20}.get(enemy_rank, 0)
    terrain_mod = {"forest": -5, "barrow": -10, "open": 5}.get(terrain, 0)
    strength_gap = (rd["effective_fighters"] - enemy_count) * 4
    score = 50 + strength_gap + rd["morale_modifier"] + terrain_mod - rank_mod

    if score >= 70:
        rec = "ENGAGE"
    elif score >= 45:
        rec = "ENGAGE WITH CAUTION"
    elif score >= 30:
        rec = "HOLD"
    else:
        rec = "RETREAT"

    return {
        **rd,
        "enemy_count": enemy_count,
        "enemy_rank": enemy_rank,
        "terrain": terrain,
        "season": season,
        "assessment_score": score,
        "recommendation": rec,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Tactical report")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("readiness")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("assess")
    p.add_argument("--enemy-count", type=int, default=0)
    p.add_argument("--enemy-rank", default="common")
    p.add_argument("--terrain", default="forest")
    p.add_argument("--season", default="long_dark")
    p.add_argument("--json", action="store_true")

    args = parser.parse_args()
    out = readiness() if args.cmd == "readiness" else assess(args.enemy_count, args.enemy_rank, args.terrain, args.season)

    if getattr(args, "json", False):
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(f"=== TACTICAL ASSESSMENT — Day {out['day']} ===")
        print(f"Band: {out['effective_fighters']} effective fighters ({out['band_size']} total)")
        print(f"Supply: {out['food_units']} food — {out['supply_days']} days")
        print(f"Morale: {out['morale']} (mod {out['morale_modifier']:+d})")
        if args.cmd == "assess":
            print(f"Enemy: ~{out['enemy_count']} {out['enemy_rank']}")
            print(f"Assessment score: {out['assessment_score']}")
            print(f"Recommendation: {out['recommendation']}")


if __name__ == "__main__":
    main()
