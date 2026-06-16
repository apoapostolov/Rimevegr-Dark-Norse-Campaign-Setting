#!/usr/bin/env python3
"""
Iron Ledger — Weather Generator

Procedural daily weather generation based on season. Tables from
20_SIMULATION_RULES.md §10 and 09_WEATHER_SEASONS_AND_HAZARDS.md.
Extended with historical weather lookup from data/weather/*.yaml.

Usage:
    python weather.py generate --season long_dark --day 87
    python weather.py generate --season long_summer --days 7
    python weather.py frostbite --days-exposed 2 --toughness 6 --no-cloak
    python weather.py modifiers --weather rime_fog
    python weather.py history --year 313 --week 22
    python weather.py lookup --year 312 --day 3
    python weather.py report --year 313 --season long_dark
    python weather.py named-event --id WE_001
    python weather.py hazards --terrain forest --season long_dark
"""

import argparse
import json
import os
import random
import sys
import textwrap

import yaml

sys.path.insert(0, __file__ and __import__('os').path.dirname(__file__) or '.')
from engine import roll_d100

# --- Weather Tables ---

LONG_SUMMER_TABLE = [
    (40, "clear_grey", (1, 3)),
    (70, "rime_fog", (1, 2)),
    (85, "light_rain", (1, 1)),
    (95, "driving_snow", (1, 1)),
    (99, "the_hush", (0, 0)),     # event, not multi-day
    (100, "veil_thinning", (0, 0)),
]

LONG_DARK_TABLE = [
    (20, "clear_grey", (1, 2)),
    (50, "rime_fog", (1, 3)),
    (75, "driving_snow", (1, 3)),
    (90, "rime_storm", (1, 2)),
    (97, "the_hush", (0, 0)),
    (99, "veil_thinning", (0, 0)),
    (100, "blood_sun", (1, 1)),
]

# --- Weather Modifiers ---
WEATHER_MODIFIERS = {
    "clear_grey": {
        "forage_mod": 1.0,
        "travel_mod": 1.0,
        "combat_mod": 0,
        "ranged_mod": 0,
        "special": None,
    },
    "rime_fog": {
        "forage_mod": 0.8,
        "travel_mod": 0.7,
        "combat_mod": 0,
        "ranged_mod": -10,
        "special": "Hush likely",
    },
    "light_rain": {
        "forage_mod": 0.9,
        "travel_mod": 0.9,
        "combat_mod": 0,
        "ranged_mod": -5,
        "special": None,
    },
    "driving_snow": {
        "forage_mod": 0.5,
        "travel_mod": 0.5,
        "combat_mod": -20,
        "ranged_mod": -20,
        "special": "Frostbite risk",
    },
    "rime_storm": {
        "forage_mod": 0.0,
        "travel_mod": 0.2,
        "combat_mod": -30,
        "ranged_mod": -30,
        "special": "High frostbite risk, foraging impossible",
    },
    "the_hush": {
        "forage_mod": 1.0,
        "travel_mod": 1.0,
        "combat_mod": -20,
        "ranged_mod": 0,
        "special": "Fear, weirdness, all sound-based actions fail",
    },
    "veil_thinning": {
        "forage_mod": 1.1,
        "travel_mod": 1.0,
        "combat_mod": 0,
        "ranged_mod": 0,
        "special": "Omen event, Wyrd checks for Wyrd 3+",
    },
    "blood_sun": {
        "forage_mod": 1.0,
        "travel_mod": 0.5,
        "combat_mod": -10,
        "ranged_mod": -10,
        "special": "Terror event, animals refuse to move",
    },
}

WEATHER_DISPLAY = {
    "clear_grey": "Clear Grey",
    "rime_fog": "Rime-Fog",
    "light_rain": "Light Rain",
    "driving_snow": "Driving Snow",
    "rime_storm": "Rime Storm",
    "the_hush": "The Hush",
    "veil_thinning": "Veil-Thinning",
    "blood_sun": "Blood Sun",
}


def determine_season(day_of_year: int) -> str:
    """Determine season from day of year (1-360)."""
    return "long_summer" if 1 <= day_of_year <= 60 else "long_dark"


def determine_sub_season(day_of_year: int) -> str:
    """Determine sub-season from day of year (1-360)."""
    if 1 <= day_of_year <= 30:
        return "thaw"
    elif 31 <= day_of_year <= 60:
        return "long_sun"
    elif 61 <= day_of_year <= 90:
        return "harvest"
    else:
        return "long_dark"


def day_to_week(day_of_year: int) -> int:
    """Convert day of year (1-360) to week number (1-48)."""
    return min(48, max(1, (day_of_year - 1) // 7 + 1))


# --- Data File Loaders ---

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "data", "weather")


def _load_yaml(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def load_weather_history() -> dict:
    data = _load_yaml("weather_history.yaml")
    return data.get("weather_history", data)


def load_named_events() -> list[dict]:
    data = _load_yaml("named_events.yaml")
    return data.get("named_events", [])


def load_hazards() -> dict:
    data = _load_yaml("hazards.yaml")
    return data.get("hazards", data)


def load_seasonal_life() -> dict:
    data = _load_yaml("seasonal_life.yaml")
    return data.get("seasonal_life", data)


# --- History Lookup ---

def history_week(year: int, week: int) -> dict | None:
    """Look up a specific week from the weather history."""
    wh = load_weather_history()
    years = wh.get("years", {})
    year_data = years.get(year, years.get(str(year)))
    if not year_data:
        return None
    for w in year_data.get("weeks", []):
        if w.get("week") == week:
            return w
    return None


def history_day(year: int, day: int) -> dict | None:
    """Look up the weather for a specific day (finds the containing week)."""
    week = day_to_week(day)
    result = history_week(year, week)
    if result:
        result = dict(result)
        result["queried_day"] = day
        result["sub_season"] = determine_sub_season(day)
    return result


def history_season(year: int, season: str) -> list[dict]:
    """Get all weeks for a given season in a year."""
    season_map = {
        "thaw": range(1, 5), "spring": range(1, 5),
        "long_sun": range(5, 9), "summer": range(5, 9),
        "harvest": range(9, 13), "autumn": range(9, 13),
        "long_dark": range(13, 49), "winter": range(13, 49),
    }
    weeks = season_map.get(season, range(1, 49))
    wh = load_weather_history()
    years = wh.get("years", {})
    year_data = years.get(year, years.get(str(year)))
    if not year_data:
        return []
    return [w for w in year_data.get("weeks", [])
            if w.get("week") in weeks]


# --- Named Event Lookup ---

def find_named_event(event_id: str) -> dict | None:
    """Find a named weather event by ID (e.g., WE_001)."""
    for ev in load_named_events():
        if ev.get("id") == event_id:
            return ev
    return None


def named_events_for_year(year: int) -> list[dict]:
    """All named events in a given year."""
    return [ev for ev in load_named_events() if ev.get("year") == year]


# --- Hazard Lookup ---

def hazards_for_terrain(terrain: str, season: str | None = None) -> list[dict]:
    """Get hazards for a terrain, optionally filtered by season."""
    h = load_hazards()
    th = h.get("terrain_hazards", {})
    terrain_data = th.get(terrain, {})
    results = []
    if isinstance(terrain_data, dict):
        # Always include all_seasons
        results.extend(terrain_data.get("all_seasons", []))
        if season:
            results.extend(terrain_data.get(season, []))
        else:
            for key, entries in terrain_data.items():
                if key != "all_seasons" and isinstance(entries, list):
                    results.extend(entries)
    # Add universal hazards if present
    for uh in h.get("universal_hazards", []):
        if season:
            triggers = uh.get("season_triggers", [])
            if not triggers or season in triggers:
                results.append(uh)
        else:
            results.append(uh)
    return results


# --- Narrative Report Generator ---

def generate_narrative_report(year: int, season: str | None = None,
                              week: int | None = None) -> str:
    """Generate a prose weather report for novel writing."""
    lines = []

    if week:
        w = history_week(year, week)
        if not w:
            return f"No data for Y{year} week {week}."
        lines.append(f"=== Y{year}, Week {w['week']} ({w.get('season','?').upper()}) ===")
        lines.append(f"Days {w.get('days', '?')}")
        lines.append("")
        lines.append(f"Conditions: {WEATHER_DISPLAY.get(w.get('dominant_weather',''), w.get('dominant_weather',''))}")
        lines.append(f"Temperature: {w.get('temperature','?').replace('_',' ').title()}")
        lines.append(f"Wind: {w.get('wind','?').replace('_',' ').title()}")
        lines.append(f"Precipitation: {w.get('precipitation','?').replace('_',' ').title()}")
        lines.append(f"Visibility: {w.get('visibility','?').title()}")
        if w.get("named_event"):
            ev = find_named_event(w["named_event"])
            if ev:
                lines.append(f"\nNamed Event: {ev['name']} ({ev['id']})")
                lines.append(f"  Severity: {ev.get('severity','?')}")
                desc = ev.get("description", "")
                if desc:
                    lines.append(f"  {desc.strip()}")
        narrative = w.get("narrative", "")
        if narrative:
            lines.append(f"\n{narrative}")
        mods = WEATHER_MODIFIERS.get(w.get("dominant_weather", ""), {})
        if mods:
            lines.append(f"\nModifiers: forage x{mods.get('forage_mod',1)}, "
                         f"travel x{mods.get('travel_mod',1)}, "
                         f"combat {mods.get('combat_mod',0):+d}, "
                         f"ranged {mods.get('ranged_mod',0):+d}")
            if mods.get("special"):
                lines.append(f"Special: {mods['special']}")
    elif season:
        weeks = history_season(year, season)
        if not weeks:
            return f"No data for Y{year} {season}."
        season_label = season.replace("_", " ").title()
        lines.append(f"=== Y{year} — {season_label} Weather Report ===")
        lines.append("")
        # Summary table
        lines.append(f"{'Week':<6}{'Days':<10}{'Weather':<18}{'Temp':<14}{'Wind':<16}{'Vis':<10}{'Event'}")
        lines.append("-" * 90)
        for w in weeks:
            ev_name = ""
            if w.get("named_event"):
                ev = find_named_event(w["named_event"])
                ev_name = ev["name"] if ev else w["named_event"]
            display = WEATHER_DISPLAY.get(w.get("dominant_weather", ""),
                                          w.get("dominant_weather", ""))
            temp = w.get("temperature", "?").replace("_", " ")
            wind = w.get("wind", "?").replace("_", " ")
            vis = w.get("visibility", "?")
            lines.append(f"{w['week']:<6}{w.get('days','?'):<10}{display:<18}"
                         f"{temp:<14}{wind:<16}{vis:<10}{ev_name}")
        # Named events summary
        year_events = [ev for ev in named_events_for_year(year)
                       if ev.get("season") == season]
        if year_events:
            lines.append(f"\n--- Named Events in {season_label} ---")
            for ev in year_events:
                lines.append(f"  {ev['id']}: {ev['name']} (day {ev.get('start_day','?')}, "
                             f"{ev.get('duration_days','?')}d, {ev.get('severity','?')})")
    else:
        return f"Specify --season or --week for the report."

    return "\n".join(lines)


def generate_weather(season: str) -> dict:
    """Generate a single weather event for the given season."""
    table = LONG_SUMMER_TABLE if "summer" in season else LONG_DARK_TABLE
    roll = roll_d100()

    for threshold, weather_type, duration_range in table:
        if roll <= threshold:
            if duration_range[0] == 0:
                duration = 0  # event, not multi-day
            else:
                duration = random.randint(duration_range[0], duration_range[1])

            mods = WEATHER_MODIFIERS.get(weather_type, {})
            return {
                "roll": roll,
                "weather": weather_type,
                "display": WEATHER_DISPLAY.get(weather_type, weather_type),
                "duration_days": duration,
                "is_event": duration == 0,
                "modifiers": mods,
            }

    # Fallback (should not reach)
    return {"roll": roll, "weather": "clear_grey", "display": "Clear Grey",
            "duration_days": 1, "is_event": False, "modifiers": WEATHER_MODIFIERS["clear_grey"]}


def generate_weather_sequence(season: str, days: int) -> list[dict]:
    """Generate weather for multiple days, respecting durations."""
    sequence = []
    remaining = days
    day_num = 0

    while remaining > 0:
        event = generate_weather(season)
        dur = max(1, event["duration_days"]) if not event["is_event"] else 1

        for _ in range(min(dur, remaining)):
            day_num += 1
            day_entry = {
                "day": day_num,
                "weather": event["weather"],
                "display": event["display"],
                "is_event": event["is_event"],
                "modifiers": event["modifiers"],
            }
            sequence.append(day_entry)
            remaining -= 1

    return sequence


def frostbite_chance(
    days_exposed: int,
    toughness: int,
    no_cloak: bool = False,
    wounded: bool = False,
) -> dict:
    """Calculate frostbite risk per the rules.
    frostbite_chance = 15% + (10% * days_exposed) - (Toughness * 2%)
    +10% if no cloak, +15% if wounded
    """
    base = 15 + (10 * days_exposed) - (toughness * 2)
    if no_cloak:
        base += 10
    if wounded:
        base += 15
    chance = max(0, min(95, base))
    roll = roll_d100()
    got_frostbite = roll <= chance

    return {
        "chance_pct": chance,
        "roll": roll,
        "frostbite": got_frostbite,
        "days_exposed": days_exposed,
        "toughness": toughness,
        "no_cloak": no_cloak,
        "wounded": wounded,
    }


def get_modifiers(weather: str) -> dict:
    """Get all modifiers for a weather type."""
    mods = WEATHER_MODIFIERS.get(weather, WEATHER_MODIFIERS["clear_grey"])
    return {
        "weather": weather,
        "display": WEATHER_DISPLAY.get(weather, weather),
        **mods,
    }


def main():
    parser = argparse.ArgumentParser(description="Iron Ledger Weather Generator")
    subparsers = parser.add_subparsers(dest="command")

    # --- generate ---
    gen_p = subparsers.add_parser("generate", help="Generate weather")
    gen_p.add_argument("--season", type=str, default="long_dark",
                       choices=["long_summer", "summer", "long_dark", "dark"])
    gen_p.add_argument("--day", type=int, help="Day of year (auto-determines season)")
    gen_p.add_argument("--days", type=int, default=1, help="Number of days to generate")
    gen_p.add_argument("--json", action="store_true")

    # --- frostbite ---
    fb_p = subparsers.add_parser("frostbite", help="Check frostbite risk")
    fb_p.add_argument("--days-exposed", type=int, required=True)
    fb_p.add_argument("--toughness", type=int, required=True)
    fb_p.add_argument("--no-cloak", action="store_true")
    fb_p.add_argument("--wounded", action="store_true")
    fb_p.add_argument("--json", action="store_true")

    # --- modifiers ---
    mod_p = subparsers.add_parser("modifiers", help="Get weather modifiers")
    mod_p.add_argument("--weather", type=str, required=True,
                       choices=list(WEATHER_MODIFIERS.keys()))
    mod_p.add_argument("--json", action="store_true")

    # --- history ---
    hist_p = subparsers.add_parser("history",
                                   help="Look up historical weather by year/week")
    hist_p.add_argument("--year", type=int, required=True)
    hist_p.add_argument("--week", type=int, required=True)
    hist_p.add_argument("--json", action="store_true")

    # --- lookup ---
    look_p = subparsers.add_parser("lookup",
                                   help="Look up weather for a specific day")
    look_p.add_argument("--year", type=int, required=True)
    look_p.add_argument("--day", type=int, required=True)
    look_p.add_argument("--json", action="store_true")

    # --- report ---
    rep_p = subparsers.add_parser("report",
                                  help="Narrative weather report for a season or week")
    rep_p.add_argument("--year", type=int, required=True)
    rep_p.add_argument("--season", type=str,
                       choices=["thaw", "long_sun", "harvest", "long_dark",
                                "spring", "summer", "autumn", "winter"])
    rep_p.add_argument("--week", type=int)
    rep_p.add_argument("--json", action="store_true")

    # --- named-event ---
    ne_p = subparsers.add_parser("named-event",
                                 help="Look up a named weather event")
    ne_p.add_argument("--id", type=str, dest="event_id",
                      help="Event ID (e.g., WE_001)")
    ne_p.add_argument("--year", type=int,
                      help="List all named events in a year")
    ne_p.add_argument("--json", action="store_true")

    # --- hazards ---
    haz_p = subparsers.add_parser("hazards",
                                  help="Look up terrain hazards")
    haz_p.add_argument("--terrain", type=str, required=True,
                       choices=["coastal", "forest", "moor", "mountain",
                                "marsh", "river_lake", "ice_tundra",
                                "underground"])
    haz_p.add_argument("--season", type=str,
                       choices=["thaw", "long_sun", "harvest", "long_dark"])
    haz_p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "generate":
        season = args.season
        if args.day:
            season = determine_season(args.day)

        if args.days == 1:
            result = generate_weather(season)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Weather: {result['display']}")
                if result["is_event"]:
                    print(f"  Type: Event")
                else:
                    print(f"  Duration: {result['duration_days']} day(s)")
                if result["modifiers"].get("special"):
                    print(f"  Special: {result['modifiers']['special']}")
        else:
            sequence = generate_weather_sequence(season, args.days)
            if args.json:
                print(json.dumps(sequence, indent=2))
            else:
                for day in sequence:
                    event_tag = " [EVENT]" if day["is_event"] else ""
                    special = ""
                    if day["modifiers"].get("special"):
                        special = f" -- {day['modifiers']['special']}"
                    print(f"  Day {day['day']}: {day['display']}{event_tag}{special}")

    elif args.command == "frostbite":
        result = frostbite_chance(
            args.days_exposed, args.toughness,
            args.no_cloak, args.wounded,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            status = "FROSTBITE!" if result["frostbite"] else "Safe"
            print(f"Frostbite check: {result['chance_pct']}% chance, roll {result['roll']} — {status}")

    elif args.command == "modifiers":
        result = get_modifiers(args.weather)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Weather: {result['display']}")
            print(f"  Forage: x{result['forage_mod']}")
            print(f"  Travel: x{result['travel_mod']}")
            print(f"  Combat: {result['combat_mod']:+d}")
            print(f"  Ranged: {result['ranged_mod']:+d}")
            if result.get("special"):
                print(f"  Special: {result['special']}")

    elif args.command == "history":
        result = history_week(args.year, args.week)
        if not result:
            print(f"No data for Y{args.year} week {args.week}.")
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            display = WEATHER_DISPLAY.get(result.get("dominant_weather", ""),
                                          result.get("dominant_weather", ""))
            print(f"Y{args.year} Week {result['week']} ({result.get('season','?')}), "
                  f"Days {result.get('days','?')}")
            print(f"  Weather: {display}")
            print(f"  Temp: {result.get('temperature','?')}")
            print(f"  Wind: {result.get('wind','?')}")
            print(f"  Precip: {result.get('precipitation','?')}")
            print(f"  Visibility: {result.get('visibility','?')}")
            if result.get("named_event"):
                print(f"  Named event: {result['named_event']}")
            if result.get("narrative"):
                print(f"  {result['narrative']}")

    elif args.command == "lookup":
        result = history_day(args.year, args.day)
        if not result:
            print(f"No data for Y{args.year} day {args.day}.")
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            display = WEATHER_DISPLAY.get(result.get("dominant_weather", ""),
                                          result.get("dominant_weather", ""))
            print(f"Y{args.year} Day {args.day} (week {result['week']}, "
                  f"{result.get('sub_season','?')})")
            print(f"  Weather: {display}")
            print(f"  Temp: {result.get('temperature','?')}")
            print(f"  Wind: {result.get('wind','?')}")
            if result.get("named_event"):
                ev = find_named_event(result["named_event"])
                if ev:
                    print(f"  Named event: {ev['name']} — {ev.get('severity','')}")
            if result.get("narrative"):
                print(f"  {result['narrative']}")

    elif args.command == "report":
        text = generate_narrative_report(args.year, args.season, args.week)
        if args.json:
            print(json.dumps({"report": text}))
        else:
            print(text)

    elif args.command == "named-event":
        if args.event_id:
            ev = find_named_event(args.event_id)
            if not ev:
                print(f"Named event {args.event_id} not found.")
                sys.exit(1)
            if args.json:
                print(json.dumps(ev, indent=2))
            else:
                print(f"{ev['id']}: {ev['name']}")
                print(f"  Year: {ev.get('year')}, Season: {ev.get('season')}, "
                      f"Day: {ev.get('start_day')}")
                print(f"  Duration: {ev.get('duration_days')} days, "
                      f"Severity: {ev.get('severity')}")
                print(f"  Type: {ev.get('weather_type')}")
                regions = ev.get("affected_regions", [])
                if regions:
                    print(f"  Regions: {', '.join(regions)}")
                settlements = ev.get("affected_settlements", [])
                if settlements:
                    print(f"  Settlements: {', '.join(settlements)}")
                desc = ev.get("description", "")
                if desc:
                    for line in textwrap.wrap(desc.strip(), 72):
                        print(f"  {line}")
                for c in ev.get("narrative_consequences", []):
                    print(f"  → {c}")
        elif args.year:
            events = named_events_for_year(args.year)
            if args.json:
                print(json.dumps(events, indent=2))
            else:
                print(f"Named weather events in Y{args.year}: {len(events)}")
                for ev in events:
                    print(f"  {ev['id']}: {ev['name']} — {ev.get('season')} "
                          f"day {ev.get('start_day')}, {ev.get('severity')}")
        else:
            print("Specify --id or --year.")
            sys.exit(1)

    elif args.command == "hazards":
        results = hazards_for_terrain(args.terrain, args.season)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            label = args.terrain.replace("_", " ").title()
            season_label = f" ({args.season})" if args.season else ""
            print(f"Hazards for {label}{season_label}: {len(results)}")
            for h in results:
                sev = h.get("severity", "?")
                freq = h.get("frequency", "?")
                print(f"\n  [{sev.upper()}] {h.get('name', '?')} ({freq})")
                desc = h.get("description", "")
                if desc:
                    for line in textwrap.wrap(desc.strip(), 68):
                        print(f"    {line}")
                mech = h.get("mechanical_effect", {})
                if mech:
                    check = mech.get("check", "?")
                    diff = mech.get("difficulty", "?")
                    print(f"    Check: {check} (difficulty {diff})")
                prev = h.get("prevention", "")
                if prev:
                    print(f"    Prevention: {prev}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
