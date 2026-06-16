#!/usr/bin/env python3
"""
Iron Ledger — Calendar Engine

Tracks game date, advances time, determines season, and manages time costs
for activities. Calendar from 20_SIMULATION_RULES.md §14.

Usage:
    python calendar_sim.py show --year 312 --day 87
    python calendar_sim.py advance --year 312 --day 87 --days 3
    python calendar_sim.py season --day 87
    python calendar_sim.py time-cost --activity march
    python calendar_sim.py week-summary --year 312 --day 85 --day-end 91
"""

import argparse
import json
import sys

# --- Calendar Constants ---
DAYS_PER_MONTH = 30
MONTHS_PER_YEAR = 12
DAYS_PER_YEAR = DAYS_PER_MONTH * MONTHS_PER_YEAR  # 360

MONTH_NAMES = [
    "Frostwake",    # 1 (summer)
    "Rimeblood",    # 2 (summer)
    "Veilthin",     # 3
    "Ashfall",      # 4
    "Ironmoon",     # 5
    "Wolfmoot",     # 6
    "Barrowrise",   # 7
    "Longnight",    # 8
    "Hearthstar",   # 9
    "Bloodtide",    # 10
    "Skaldsong",    # 11
    "Yuledeep",     # 12
]

SUMMER_MONTHS = {1, 2}  # Frostwake, Rimeblood

# --- Time Costs ---
TIME_COSTS = {
    "march": {"cost": "1 day", "days": 1.0, "quarter_days": 4},
    "forage": {"cost": "1 quarter-day", "days": 0.25, "quarter_days": 1},
    "barrow_clearing": {"cost": "1-3 days", "days": 2.0, "quarter_days": 8},
    "recruitment_search": {"cost": "1 quarter-day", "days": 0.25, "quarter_days": 1},
    "heal": {"cost": "1 quarter-day", "days": 0.25, "quarter_days": 1},
    "galdr": {"cost": "1-4 hours", "days": 0.125, "quarter_days": 1},
    "seidr": {"cost": "1+ hours (trance)", "days": 0.25, "quarter_days": 1},
    "wyrd_reading": {"cost": "10-30 minutes", "days": 0.05, "quarter_days": 0},
    "pay_ritual": {"cost": "1 hour", "days": 0.04, "quarter_days": 0},
    "camp_setup": {"cost": "2 hours", "days": 0.08, "quarter_days": 1},
    "rest_full_day": {"cost": "1 day", "days": 1.0, "quarter_days": 4},
}


def day_to_date(day_of_year: int) -> dict:
    """Convert day of year (1-360) to month and day of month."""
    day_of_year = max(1, min(DAYS_PER_YEAR, day_of_year))
    month_idx = (day_of_year - 1) // DAYS_PER_MONTH
    day_of_month = ((day_of_year - 1) % DAYS_PER_MONTH) + 1

    return {
        "month_number": month_idx + 1,
        "month_name": MONTH_NAMES[month_idx],
        "day_of_month": day_of_month,
    }


def get_season(day_of_year: int) -> str:
    """Determine season from day of year."""
    return "Long Summer" if 1 <= day_of_year <= 60 else "The Long Dark"


def get_season_key(day_of_year: int) -> str:
    """Return season key for script interop."""
    return "long_summer" if 1 <= day_of_year <= 60 else "long_dark"


def show_date(year: int, day_of_year: int) -> dict:
    """Full date display."""
    date = day_to_date(day_of_year)
    season = get_season(day_of_year)
    return {
        "year": year,
        "day_of_year": day_of_year,
        "month_number": date["month_number"],
        "month_name": date["month_name"],
        "day_of_month": date["day_of_month"],
        "season": season,
        "season_key": get_season_key(day_of_year),
        "display": f"Day {date['day_of_month']}, {date['month_name']}, Year {year} ({season})",
    }


def advance_time(year: int, day_of_year: int, days: int) -> dict:
    """Advance the calendar by a number of days."""
    total_day = day_of_year + days
    new_year = year
    while total_day > DAYS_PER_YEAR:
        total_day -= DAYS_PER_YEAR
        new_year += 1

    old_date = show_date(year, day_of_year)
    new_date = show_date(new_year, total_day)

    # Check for season change
    old_season = get_season_key(day_of_year)
    new_season = get_season_key(total_day)
    season_changed = old_season != new_season

    # Check for month change
    old_month = day_to_date(day_of_year)["month_number"]
    new_month = day_to_date(total_day)["month_number"]
    month_changed = old_month != new_month or new_year != year

    return {
        "from": old_date,
        "to": new_date,
        "days_advanced": days,
        "season_changed": season_changed,
        "month_changed": month_changed,
    }


def week_summary(year: int, day_start: int, day_end: int) -> dict:
    """Summarize a week period for simulation cycle."""
    days = []
    for d in range(day_start, day_end + 1):
        day = d
        y = year
        while day > DAYS_PER_YEAR:
            day -= DAYS_PER_YEAR
            y += 1
        info = show_date(y, day)
        days.append(info)

    return {
        "year": year,
        "day_range": f"{day_start}-{day_end}",
        "days_count": len(days),
        "season": days[0]["season"] if days else "unknown",
        "month": days[0]["month_name"] if days else "unknown",
        "pay_due": True,  # weekly retainer due
        "forage_checks": len(days),  # one per day
        "morale_check": True,  # weekly
        "grievance_resolution": True,  # weekly
        "days": days,
    }


def get_time_cost(activity: str) -> dict:
    """Look up time cost for an activity."""
    cost = TIME_COSTS.get(activity)
    if not cost:
        return {"error": f"Unknown activity: {activity}",
                "available": list(TIME_COSTS.keys())}
    return {"activity": activity, **cost}


def main():
    parser = argparse.ArgumentParser(description="Iron Ledger Calendar Engine")
    subparsers = parser.add_subparsers(dest="command")

    # --- show ---
    show_p = subparsers.add_parser("show", help="Show current date")
    show_p.add_argument("--year", type=int, required=True)
    show_p.add_argument("--day", type=int, required=True, help="Day of year (1-360)")
    show_p.add_argument("--json", action="store_true")

    # --- advance ---
    adv_p = subparsers.add_parser("advance", help="Advance time")
    adv_p.add_argument("--year", type=int, required=True)
    adv_p.add_argument("--day", type=int, required=True)
    adv_p.add_argument("--days", type=int, required=True, help="Days to advance")
    adv_p.add_argument("--json", action="store_true")

    # --- season ---
    sea_p = subparsers.add_parser("season", help="Check season")
    sea_p.add_argument("--day", type=int, required=True)
    sea_p.add_argument("--json", action="store_true")

    # --- time-cost ---
    tc_p = subparsers.add_parser("time-cost", help="Look up activity time cost")
    tc_p.add_argument("--activity", type=str, required=True,
                      choices=list(TIME_COSTS.keys()))
    tc_p.add_argument("--json", action="store_true")

    # --- week-summary ---
    ws_p = subparsers.add_parser("week-summary", help="Summarize a week")
    ws_p.add_argument("--year", type=int, required=True)
    ws_p.add_argument("--day-start", type=int, required=True)
    ws_p.add_argument("--day-end", type=int, required=True)
    ws_p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "show":
        result = show_date(args.year, args.day)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result["display"])

    elif args.command == "advance":
        result = advance_time(args.year, args.day, args.days)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"From: {result['from']['display']}")
            print(f"To:   {result['to']['display']}")
            print(f"Days: {result['days_advanced']}")
            if result["season_changed"]:
                print(f"SEASON CHANGE: {result['from']['season']} -> {result['to']['season']}")
            if result["month_changed"]:
                print(f"Month change: {result['from']['month_name']} -> {result['to']['month_name']}")

    elif args.command == "season":
        season = get_season(args.day)
        key = get_season_key(args.day)
        if args.json:
            print(json.dumps({"day": args.day, "season": season, "season_key": key}))
        else:
            print(f"Day {args.day}: {season}")

    elif args.command == "time-cost":
        result = get_time_cost(args.activity)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"{result['activity']}: {result['cost']}")

    elif args.command == "week-summary":
        result = week_summary(args.year, args.day_start, args.day_end)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Week: Days {result['day_range']}, Year {args.year}")
            print(f"Season: {result['season']}, Month: {result['month']}")
            print(f"Checks due: pay, morale, grievance, {result['forage_checks']}x forage")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
