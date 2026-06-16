#!/usr/bin/env python3
"""Iron Ledger — world state broadcast.

Produces a single session-start snapshot by aggregating band, politics,
weather, contracts, event horizon, and integration signals from prompt 1–7
systems.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
DATA_DIR = ROOT / "data"
BAND_FILE = DATA_DIR / "band_state.yaml"
POL_FILE = DATA_DIR / "political_state.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _morale_label(v: int) -> str:
    if v <= 2:
        return "BROKEN"
    if v == 3:
        return "SHAKY"
    if v == 4:
        return "STEADY"
    if v <= 6:
        return "HIGH"
    return "INSPIRED"


def _deadline_flag(days_left: int) -> str:
    if days_left <= 3:
        return "🔴 CRITICAL"
    if days_left <= 10:
        return "⚠ URGENT"
    return ""


def _safe_imports():
    # local imports delayed for startup resilience
    from weather import determine_season, generate_weather
    from event_manager import load_all_events
    from ledger import cmd_weekly_summary
    from village_politics import cmd_feud_stage
    from magic import cmd_practitioners
    return determine_season, generate_weather, load_all_events, cmd_weekly_summary, cmd_feud_stage, cmd_practitioners


def build_report() -> dict[str, Any]:
    determine_season, generate_weather, load_all_events, cmd_weekly_summary, cmd_feud_stage, cmd_practitioners = _safe_imports()

    band_root = _load_yaml(BAND_FILE)
    pol = _load_yaml(POL_FILE)

    band = band_root.get("band", {})
    members = band_root.get("members", [])

    day = int(band.get("day_of_year", 1))
    year = int(band.get("year", 312))
    location = band.get("location", "Unknown")
    morale = int(band.get("morale", 3))
    treasury = int(band.get("treasury_silver", 0))
    goods = int(band.get("treasury_goods_value", 0))
    debts = int(band.get("debts_owed", 0))
    credits = int(band.get("credits_pending", 0))

    season_key = determine_season(day)
    weather = generate_weather(season_key)

    notes = band.get("notes", []) or []
    food_units = 0
    for n in notes:
        if isinstance(n, str) and "Food stores:" in n:
            digits = "".join(ch for ch in n if ch.isdigit())
            if digits:
                food_units = int(digits)
                break

    band_size = len([m for m in members if m.get("status") not in ("dead", "left", "deserted")])
    food_days = round((food_units / max(1, band_size / 2.0)), 1) if food_units else 0.0

    contract = band.get("current_contract") or {}
    deadline = int(contract.get("deadline_day", day)) if contract else day
    days_left = max(0, deadline - day)

    events = []
    for e in load_all_events():
        if e.get("year") == year and day <= int(e.get("day", -999)) <= day + 20:
            events.append(e)

    weekly = cmd_weekly_summary()

    feud = None
    if location:
        feud = cmd_feud_stage(location.split(",")[0].strip())
        if "error" in feud:
            feud = None

    practitioners = cmd_practitioners()

    return {
        "date": {"year": year, "day": day, "season": season_key},
        "location": location,
        "band": {
            "name": band.get("name", "Unknown Band"),
            "members": band_size,
            "morale": morale,
            "morale_label": _morale_label(morale),
        },
        "treasury": {
            "silver": treasury,
            "goods_value": goods,
            "debts": debts,
            "credits_pending": credits,
        },
        "food": {
            "units": food_units,
            "days_surplus": food_days,
        },
        "weather": weather,
        "contract": {
            "title": contract.get("title"),
            "payment_silver": contract.get("payment_silver"),
            "advance_received": contract.get("advance_received"),
            "deadline_day": deadline if contract else None,
            "days_left": days_left if contract else None,
            "deadline_flag": _deadline_flag(days_left) if contract else "",
            "status": contract.get("status"),
        },
        "political": {
            "feud": feud,
        },
        "events_horizon": {
            "count": len(events),
            "events": [
                {
                    "id": e.get("id"),
                    "day": e.get("day"),
                    "title": e.get("title"),
                    "category": e.get("category"),
                }
                for e in sorted(events, key=lambda x: x.get("day", 0))
            ],
        },
        "weekly_ledger": weekly,
        "magic_practitioners": practitioners,
    }


def as_text(r: dict[str, Any]) -> str:
    c = r["contract"]
    pay = c.get("payment_silver")
    adv = c.get("advance_received")
    pay_str = f"{pay} silver" if pay is not None else "?"
    adv_str = f"{adv} paid" if adv is not None else "advance unknown"

    feud = r["political"].get("feud")
    feud_line = "Unknown"
    if feud:
        feud_line = f"{feud.get('settlement')}: {feud.get('stage')} ({feud.get('feud_level')}/4)"

    return (
        "=== SESSION START — COMPUTER BROADCAST ===\n"
        f"Date:       Day {r['date']['day']} ({r['date']['season']}), Year {r['date']['year']}\n"
        f"Location:   {r['location']}\n"
        f"Band:       {r['band']['name']} — {r['band']['members']} members, morale "
        f"{r['band']['morale_label']} ({r['band']['morale']})\n"
        f"Treasury:   {r['treasury']['silver']} silver + goods ~{r['treasury']['goods_value']} | "
        f"Debts: {r['treasury']['debts']} | Credits pending: {r['treasury']['credits_pending']}\n"
        f"Food:       {r['food']['units']} units — {r['food']['days_surplus']} days surplus\n"
        f"Weather:    {r['weather'].get('display', r['weather'].get('weather','?'))}, "
        f"{r['weather'].get('duration_days', 1)} day(s).\n\n"
        f"Active contract: {c.get('title') or 'None'}\n"
        f"  Payment:  {pay_str} | Advance: {adv_str}\n"
        f"  Deadline: Day {c.get('deadline_day')} ({c.get('days_left')} days remaining) {c.get('deadline_flag','')}\n"
        f"  Status:   {c.get('status')}\n\n"
        f"Political: {feud_line}\n"
        f"Events:    {r['events_horizon']['count']} due in next 20 days\n"
        "==========================================="
    )


def as_md(r: dict[str, Any]) -> str:
    c = r["contract"]
    lines = [
        "# Session Start — Computer Broadcast",
        "",
        f"- **Date:** Day {r['date']['day']}, Year {r['date']['year']} ({r['date']['season']})",
        f"- **Location:** {r['location']}",
        f"- **Band:** {r['band']['name']} ({r['band']['members']} members)",
        f"- **Morale:** {r['band']['morale_label']} ({r['band']['morale']})",
        f"- **Treasury:** {r['treasury']['silver']} silver + goods ~{r['treasury']['goods_value']}",
        f"- **Food:** {r['food']['units']} units (~{r['food']['days_surplus']} days)",
        f"- **Weather:** {r['weather'].get('display', r['weather'].get('weather','?'))}",
        "",
        "## Contract",
        "",
        f"- **Title:** {c.get('title') or 'None'}",
        f"- **Payment:** {c.get('payment_silver')}",
        f"- **Advance:** {c.get('advance_received')}",
        f"- **Deadline:** Day {c.get('deadline_day')} ({c.get('days_left')} days) {c.get('deadline_flag', '')}",
        f"- **Status:** {c.get('status')}",
        "",
        f"## Event Horizon ({r['events_horizon']['count']})",
        "",
    ]
    for e in r["events_horizon"]["events"][:10]:
        lines.append(f"- Day {e.get('day')}: `{e.get('id')}` — {e.get('title')}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="World state reporter")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("report", help="Build world state report")
    p.add_argument("--format", choices=["text", "json", "md"], default="text")

    args = parser.parse_args()
    report = build_report()

    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.format == "md":
        print(as_md(report))
    else:
        print(as_text(report))


if __name__ == "__main__":
    main()
