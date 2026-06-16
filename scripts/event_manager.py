#!/usr/bin/env python3
"""
Iron Ledger — Event Manager

CLI tool for querying, filtering, decoding, and advancing the master
event database. Events are stored in YAML files under data/events/.

Usage:
    python event_manager.py list
    python event_manager.py list --year 312 --season spring
    python event_manager.py list --category supernatural
    python event_manager.py list --chain waking_barrows
    python event_manager.py list --day-range 61 120
    python event_manager.py show EVT_312_S01_001
    python event_manager.py show EVT_312_S01_001 --decode
    python event_manager.py chain waking_barrows
    python event_manager.py timeline --year 312
    python event_manager.py decode EVT_312_S01_001
    python event_manager.py advance EVT_312_A01_005 --condition band_cleared_barrow
    python event_manager.py stats
    python event_manager.py validate

Schema: data/events/EVENT_SCHEMA.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

# --- Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
EVENTS_DIR = DATA_DIR / "events"

# Import spoiler codec
sys.path.insert(0, str(SCRIPT_DIR))
from spoiler_codec import decode as spoiler_decode  # noqa: E402
from spoiler_codec import YAML_VALUE_SPOILER_RE  # noqa: E402

# --- Season/Category constants ---
VALID_SEASONS = {"spring", "summer", "autumn", "winter"}
VALID_CATEGORIES = {
    "political", "military", "economic", "supernatural",
    "personal", "weather", "social",
}
SEASON_DAY_RANGES = {
    "spring": (1, 60),
    "summer": (61, 120),
    "autumn": (121, 210),
    "winter": (211, 360),
}


# ============================================================
# Data Loading
# ============================================================


def load_all_events() -> list[dict]:
    """Load and merge events from all YAML files under data/events/."""
    all_events: list[dict] = []
    if not EVENTS_DIR.exists():
        return all_events
    for path in sorted(EVENTS_DIR.glob("*.yaml")):
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data and "events" in data:
                for evt in data["events"]:
                    evt["_source"] = path.name
                    all_events.append(evt)
        except (yaml.YAMLError, OSError) as exc:
            print(f"Warning: failed to load {path.name}: {exc}", file=sys.stderr)
    return all_events


def _decode_spoiler(value: str) -> str:
    """Decode a SPOILER:... value."""
    match = YAML_VALUE_SPOILER_RE.match(f'"{value}"')
    if match:
        return spoiler_decode(match.group(1))
    if value.startswith("SPOILER:"):
        return spoiler_decode(value[8:])
    return value


# ============================================================
# Filtering
# ============================================================


def filter_events(
    events: list[dict],
    *,
    year: int | None = None,
    season: str | None = None,
    category: str | None = None,
    chain: str | None = None,
    day_min: int | None = None,
    day_max: int | None = None,
    band_only: bool = False,
    location: str | None = None,
    actor: str | None = None,
) -> list[dict]:
    """Filter events by multiple criteria."""
    result = events
    if year is not None:
        result = [e for e in result if e.get("year") == year]
    if season is not None:
        result = [e for e in result if e.get("season") == season]
    if category is not None:
        result = [e for e in result if e.get("category") == category]
    if chain is not None:
        result = [e for e in result if e.get("chain") == chain]
    if day_min is not None:
        result = [e for e in result if e.get("day", 0) >= day_min]
    if day_max is not None:
        result = [e for e in result if e.get("day", 999) <= day_max]
    if band_only:
        result = [e for e in result if e.get("band_relevant")]
    if location is not None:
        loc_lower = location.lower()
        result = [e for e in result if loc_lower in (e.get("location") or "").lower()]
    if actor is not None:
        actor_lower = actor.lower()
        result = [
            e for e in result
            if any(actor_lower in a.lower() for a in e.get("actors", []))
        ]
    return result


# ============================================================
# Display
# ============================================================


def format_event_row(evt: dict) -> str:
    """Format a single event as a compact row."""
    eid = evt.get("id", "???")
    day = evt.get("day", "?")
    cat = evt.get("category", "?")[:5]
    title = evt.get("title", "Untitled")
    chain = evt.get("chain", "-")
    loc = evt.get("location", "-")
    band = "★" if evt.get("band_relevant") else " "
    return f"  {band} {eid:<24s} D{day:<4} {cat:<6s} {chain:<20s} {loc:<20s} {title}"


def show_event(evt: dict, *, decode: bool = False) -> str:
    """Format a full event display."""
    lines = [
        f"ID:       {evt.get('id', '???')}",
        f"Title:    {evt.get('title', 'Untitled')}",
        f"Year:     {evt.get('year', '?')}",
        f"Season:   {evt.get('season', '?')}",
        f"Day:      {evt.get('day', '?')}",
        f"Category: {evt.get('category', '?')}",
    ]
    if evt.get("chain"):
        lines.append(f"Chain:    {evt['chain']} (order: {evt.get('chain_order', '?')})")
    if evt.get("location"):
        lines.append(f"Location: {evt['location']}")
    if evt.get("actors"):
        lines.append(f"Actors:   {', '.join(evt['actors'])}")
    if evt.get("factions"):
        lines.append(f"Factions: {', '.join(evt['factions'])}")
    lines.append(f"Band:     {'Yes' if evt.get('band_relevant') else 'No'}")
    if evt.get("prerequisites"):
        lines.append(f"Requires: {', '.join(evt['prerequisites'])}")
    lines.append(f"\nSummary:  {evt.get('summary', '-')}")
    if evt.get("detail"):
        lines.append(f"\nDetail:\n  {evt['detail'].strip()}")
    if evt.get("spoiler"):
        if decode:
            decoded = _decode_spoiler(evt["spoiler"])
            lines.append(f"\n[DECODED SPOILER]\n  {decoded}")
        else:
            lines.append(f"\nSpoiler:  (encoded — use --decode to reveal)")
    if evt.get("branches"):
        lines.append("\nBranches:")
        for br in evt["branches"]:
            cond = br.get("condition", "?")
            outcome = br.get("outcome", "?")
            triggers = br.get("triggers", [])
            lines.append(f"  IF {cond}: {outcome} → {', '.join(triggers)}")
    if evt.get("effects"):
        lines.append("\nEffects:")
        for key, val in evt["effects"].items():
            lines.append(f"  {key}: {val}")
    lines.append(f"\nSource:   {evt.get('_source', '?')}")
    return "\n".join(lines)


# ============================================================
# Chain Display
# ============================================================


def show_chain(events: list[dict], chain_id: str) -> str:
    """Display all events in a chain, ordered."""
    chain_events = [e for e in events if e.get("chain") == chain_id]
    chain_events.sort(key=lambda e: (e.get("year", 0), e.get("day", 0), e.get("chain_order", 0)))
    if not chain_events:
        return f"No events found for chain: {chain_id}"
    lines = [f"Chain: {chain_id} ({len(chain_events)} events)\n"]
    for evt in chain_events:
        lines.append(format_event_row(evt))
    return "\n".join(lines)


# ============================================================
# Timeline Display
# ============================================================


def show_timeline(events: list[dict], year: int) -> str:
    """Display chronological timeline for a year."""
    year_events = [e for e in events if e.get("year") == year]
    year_events.sort(key=lambda e: e.get("day", 0))
    if not year_events:
        return f"No events for year {year}."

    lines = [f"Timeline — Year {year} ({len(year_events)} events)\n"]
    current_season = None
    for evt in year_events:
        season = evt.get("season", "?")
        if season != current_season:
            current_season = season
            lines.append(f"\n  === {season.upper()} ===")
        lines.append(format_event_row(evt))
    return "\n".join(lines)


# ============================================================
# Advance (Branch Resolution)
# ============================================================


def advance_event(events: list[dict], event_id: str, condition: str) -> str:
    """Resolve a branching event with a given condition."""
    evt = next((e for e in events if e.get("id") == event_id), None)
    if not evt:
        return f"Event not found: {event_id}"
    if not evt.get("branches"):
        return f"Event {event_id} has no branches."
    for br in evt["branches"]:
        if br.get("condition") == condition:
            triggers = br.get("triggers", [])
            return (
                f"Condition '{condition}' met for {event_id}.\n"
                f"Outcome: {br.get('outcome', '?')}\n"
                f"Triggered events: {', '.join(triggers) if triggers else 'none'}"
            )
    # Fall back to default
    for br in evt["branches"]:
        if br.get("condition") == "default":
            triggers = br.get("triggers", [])
            return (
                f"No match for '{condition}'; using default branch.\n"
                f"Outcome: {br.get('outcome', '?')}\n"
                f"Triggered events: {', '.join(triggers) if triggers else 'none'}"
            )
    return f"No matching branch for condition '{condition}' in {event_id}."


# ============================================================
# Statistics
# ============================================================


def show_stats(events: list[dict]) -> str:
    """Display event database statistics."""
    if not events:
        return "No events loaded."

    by_year: dict[int, int] = {}
    by_season: dict[str, int] = {}
    by_category: dict[str, int] = {}
    by_chain: dict[str, int] = {}
    by_source: dict[str, int] = {}
    band_count = 0
    spoiler_count = 0
    branch_count = 0

    for evt in events:
        y = evt.get("year", 0)
        by_year[y] = by_year.get(y, 0) + 1
        s = evt.get("season", "?")
        by_season[s] = by_season.get(s, 0) + 1
        c = evt.get("category", "?")
        by_category[c] = by_category.get(c, 0) + 1
        ch = evt.get("chain")
        if ch:
            by_chain[ch] = by_chain.get(ch, 0) + 1
        src = evt.get("_source", "?")
        by_source[src] = by_source.get(src, 0) + 1
        if evt.get("band_relevant"):
            band_count += 1
        if evt.get("spoiler"):
            spoiler_count += 1
        if evt.get("branches"):
            branch_count += 1

    lines = [f"Event Database — {len(events)} total events\n"]
    lines.append("By Year:")
    for y in sorted(by_year):
        lines.append(f"  Y{y}: {by_year[y]}")
    lines.append("\nBy Season:")
    for s in sorted(by_season):
        lines.append(f"  {s}: {by_season[s]}")
    lines.append("\nBy Category:")
    for c in sorted(by_category):
        lines.append(f"  {c}: {by_category[c]}")
    lines.append(f"\nBand-relevant: {band_count}")
    lines.append(f"Spoiler-encoded: {spoiler_count}")
    lines.append(f"Branching: {branch_count}")
    lines.append(f"\nChains ({len(by_chain)}):")
    for ch in sorted(by_chain):
        lines.append(f"  {ch}: {by_chain[ch]}")
    lines.append(f"\nSources ({len(by_source)}):")
    for src in sorted(by_source):
        lines.append(f"  {src}: {by_source[src]}")
    return "\n".join(lines)


# ============================================================
# Validation
# ============================================================


def validate_events(events: list[dict]) -> str:
    """Validate event data integrity."""
    issues: list[str] = []
    seen_ids: set[str] = set()
    all_ids = {e.get("id") for e in events}

    for evt in events:
        eid = evt.get("id", "MISSING_ID")
        src = evt.get("_source", "?")

        # Duplicate ID check
        if eid in seen_ids:
            issues.append(f"DUPLICATE ID: {eid} (in {src})")
        seen_ids.add(eid)

        # Required fields
        for field in ("id", "title", "year", "season", "day", "category", "band_relevant"):
            if field not in evt:
                issues.append(f"MISSING FIELD '{field}': {eid} (in {src})")

        # Valid season
        season = evt.get("season")
        if season and season not in VALID_SEASONS:
            issues.append(f"INVALID SEASON '{season}': {eid}")

        # Valid category
        category = evt.get("category")
        if category and category not in VALID_CATEGORIES:
            issues.append(f"INVALID CATEGORY '{category}': {eid}")

        # Day in range
        day = evt.get("day", 0)
        if not 1 <= day <= 360:
            issues.append(f"DAY OUT OF RANGE ({day}): {eid}")

        # Season-day consistency
        if season and day:
            expected_min, expected_max = SEASON_DAY_RANGES.get(season, (0, 360))
            if not expected_min <= day <= expected_max:
                issues.append(
                    f"DAY/SEASON MISMATCH: {eid} day={day} but season={season} "
                    f"(expected {expected_min}-{expected_max})"
                )

        # Prerequisites exist
        for prereq in evt.get("prerequisites", []):
            if prereq not in all_ids:
                issues.append(f"MISSING PREREQUISITE '{prereq}': {eid}")

        # Branch triggers exist
        for br in evt.get("branches", []):
            for trigger in br.get("triggers", []):
                if trigger not in all_ids:
                    issues.append(f"MISSING BRANCH TRIGGER '{trigger}': {eid}")

        # Chain consistency
        if evt.get("chain") and not evt.get("chain_order"):
            issues.append(f"CHAIN WITHOUT ORDER: {eid} (chain={evt['chain']})")

    if not issues:
        return f"Validation passed — {len(events)} events, 0 issues."
    return f"Validation found {len(issues)} issue(s):\n" + "\n".join(f"  • {i}" for i in issues)


# ============================================================
# CLI
# ============================================================


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Iron Ledger — Event Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    # list
    p_list = sub.add_parser("list", help="List events with optional filters")
    p_list.add_argument("--year", type=int)
    p_list.add_argument("--season", choices=sorted(VALID_SEASONS))
    p_list.add_argument("--category", choices=sorted(VALID_CATEGORIES))
    p_list.add_argument("--chain")
    p_list.add_argument("--day-range", nargs=2, type=int, metavar=("MIN", "MAX"))
    p_list.add_argument("--band", action="store_true", help="Band-relevant only")
    p_list.add_argument("--location")
    p_list.add_argument("--actor")

    # show
    p_show = sub.add_parser("show", help="Show full event details")
    p_show.add_argument("event_id")
    p_show.add_argument("--decode", action="store_true", help="Decode spoilers")

    # chain
    p_chain = sub.add_parser("chain", help="Show all events in a chain")
    p_chain.add_argument("chain_id")

    # timeline
    p_timeline = sub.add_parser("timeline", help="Chronological timeline for a year")
    p_timeline.add_argument("--year", type=int, required=True)

    # decode
    p_decode = sub.add_parser("decode", help="Decode spoiler for a specific event")
    p_decode.add_argument("event_id")

    # advance
    p_advance = sub.add_parser("advance", help="Resolve a branching event")
    p_advance.add_argument("event_id")
    p_advance.add_argument("--condition", required=True)

    # stats
    sub.add_parser("stats", help="Show event database statistics")

    # validate
    sub.add_parser("validate", help="Validate event data integrity")

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    events = load_all_events()

    if args.command == "list":
        day_min = args.day_range[0] if args.day_range else None
        day_max = args.day_range[1] if args.day_range else None
        filtered = filter_events(
            events,
            year=args.year,
            season=args.season,
            category=args.category,
            chain=args.chain,
            day_min=day_min,
            day_max=day_max,
            band_only=args.band,
            location=args.location,
            actor=args.actor,
        )
        filtered.sort(key=lambda e: (e.get("year", 0), e.get("day", 0)))
        print(f"Events: {len(filtered)} (of {len(events)} total)\n")
        header = f"  {'':1s} {'ID':<24s} {'Day':<5s} {'Cat':<6s} {'Chain':<20s} {'Location':<20s} Title"
        print(header)
        print("  " + "-" * (len(header) - 2))
        for evt in filtered:
            print(format_event_row(evt))

    elif args.command == "show":
        evt = next((e for e in events if e.get("id") == args.event_id), None)
        if not evt:
            print(f"Event not found: {args.event_id}", file=sys.stderr)
            sys.exit(1)
        print(show_event(evt, decode=args.decode))

    elif args.command == "chain":
        print(show_chain(events, args.chain_id))

    elif args.command == "timeline":
        print(show_timeline(events, args.year))

    elif args.command == "decode":
        evt = next((e for e in events if e.get("id") == args.event_id), None)
        if not evt:
            print(f"Event not found: {args.event_id}", file=sys.stderr)
            sys.exit(1)
        if not evt.get("spoiler"):
            print(f"Event {args.event_id} has no encoded spoiler.")
        else:
            print(_decode_spoiler(evt["spoiler"]))

    elif args.command == "advance":
        print(advance_event(events, args.event_id, args.condition))

    elif args.command == "stats":
        print(show_stats(events))

    elif args.command == "validate":
        print(validate_events(events))


if __name__ == "__main__":
    main()
