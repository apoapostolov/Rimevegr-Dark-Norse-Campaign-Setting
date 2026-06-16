#!/usr/bin/env python3
"""
Iron Ledger — Band Weekly Tick

Orchestrates the 7-step weekly simulation loop.  Reads from (and
optionally writes to) data/band_state.yaml.

Steps per week:
  1. Foraging   — terrain + forager count → food gathered
  2. Pay cycle  — retainer check; roll non-payment consequence if short
  3. Morale     — apply late_pay / food_deficit triggers
  4. Loyalty    — Named Man agenda-erosion tick
  5. Contracts  — generate available work at current settlement
  6. Hidden     — list encoded event IDs due this week (stub)
  7. State save — advance day_of_year +7, snapshot

Usage:
    python3 band_weekly_tick.py run \\
        --season long_dark --terrain forest --foragers 4
    python3 band_weekly_tick.py run --week 3 --dry-run
    python3 band_weekly_tick.py history --last 4
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

sys.path.insert(0, os.path.dirname(__file__))
from foraging import forage as _forage_fn
from ledger import (
    calculate_weekly_retainer,
    roll_non_payment,
    WEEKLY_RETAINER,
)
from morale import (
    apply_morale_events,
    loyalty_tick as _loyalty_tick,
    LOYALTY_NAMES,
)
from horse_breeding import tick_herd_season as _tick_herd_season
from dog_breeding import tick_kennel_season as _tick_kennel_season
from recruitment import settlement_replacement_market as _settlement_replacement_market

# ── Paths ────────────────────────────────────────────────────────────────
_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPTS)
_DATA = os.path.join(_ROOT, "data")
_BAND_STATE = os.path.join(_DATA, "band_state.yaml")
_WORKSPACE = os.path.join(_ROOT, "workspace")
_JOURNAL = os.path.join(_WORKSPACE, "journal.md")
_TICK_LOG = os.path.join(_WORKSPACE, "weekly_ticks.json")
_HORSE_HERDS = os.path.join(_DATA, "horse_herds.yaml")
_DOG_KENNELS = os.path.join(_DATA, "dog_kennels.yaml")


# ── I/O helpers ──────────────────────────────────────────────────────────

def _load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _save(data: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


def _active_members(members: list[dict]) -> list[dict]:
    return [m for m in members if m.get("status") not in ("dead", "left", "deserted")]


def _contracts_via_subprocess(
    reputation: int,
    settlement: str,
    season: str,
) -> list[dict]:
    """Generate contract offers using contracts.py CLI."""
    cmd = [
        sys.executable,
        os.path.join(_SCRIPTS, "contracts.py"),
        "generate",
        "--reputation", str(reputation),
        "--settlement", settlement,
        "--season", season,
        "--json",
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.PIPE, timeout=10)
        return json.loads(out)
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return []


def _season_slot(day_of_year: int) -> int:
    day = ((int(day_of_year) - 1) % 360) + 1
    return ((day - 1) // 90) + 1


def _season_id(year: int, day_of_year: int) -> str:
    return f"Y{int(year)}-S{_season_slot(day_of_year)}"


def _run_seasonal_animal_ticks(year: int, day_start: int, day_end: int, dry_run: bool) -> dict:
    start_slot = _season_slot(day_start)
    end_slot = _season_slot(day_end)
    if start_slot == end_slot:
        return {"triggered": False, "season_id": _season_id(year, day_end), "horse_herds": [], "dog_kennels": []}

    season_id = _season_id(year, day_end)
    if dry_run:
        return {"triggered": True, "season_id": season_id, "horse_herds": [], "dog_kennels": [], "dry_run": True}

    horse_results = []
    dog_results = []
    if os.path.exists(_HORSE_HERDS):
        herds = _load(_HORSE_HERDS).get("horse_herds", [])
        for herd in herds:
            horse_results.append(
                _tick_herd_season(herd["herd_id"], herd_file=Path(_HORSE_HERDS), season_id=season_id)
            )
    if os.path.exists(_DOG_KENNELS):
        kennels = _load(_DOG_KENNELS).get("dog_kennels", [])
        for kennel in kennels:
            dog_results.append(
                _tick_kennel_season(kennel["kennel_id"], kennel_file=Path(_DOG_KENNELS), season_id=season_id)
            )
    return {
        "triggered": True,
        "season_id": season_id,
        "horse_herds": horse_results,
        "dog_kennels": dog_results,
    }


# ── Core tick logic ──────────────────────────────────────────────────────

def run_weekly_tick(
    band_file: str,
    season: str,
    terrain: str,
    forager_count: int,
    forager_skill: float = 0.0,
    week_override: int | None = None,
    captain_wil: int | None = None,
    command_skill: int | None = None,
    dry_run: bool = False,
) -> dict:
    """Execute one full weekly simulation cycle.  Returns summary dict."""
    data = _load(band_file)
    band_meta = data["band"]
    members = data.get("members", [])
    active = _active_members(members)

    day_start = band_meta.get("day_of_year", 0)
    year = band_meta.get("year", 1)
    week = week_override or (day_start // 7 + 1)

    # Captain stats (from member record if not provided)
    captain = next(
        (m for m in members if m.get("rank", "").lower() == "captain"),
        None,
    )
    if captain_wil is None:
        captain_wil = captain["wil"] if captain else 7
    if command_skill is None:
        skills = captain.get("skills", {}) if captain else {}
        command_skill = skills.get("command", 3)

    summary: dict = {
        "week": week,
        "year": year,
        "day_start": day_start,
        "day_end": day_start + 7,
        "season": season,
        "dry_run": dry_run,
        "steps": {},
        "warnings": [],
    }

    # ── Step 1: Foraging ─────────────────────────────────────────────────
    forage_result = _forage_fn(terrain, forager_count, forager_skill, season)
    food_gathered = forage_result.get("food_gathered", 0)
    food_deficit = food_gathered < len(active)
    summary["steps"]["foraging"] = {
        "foragers": forager_count,
        "terrain": terrain,
        "food_gathered": food_gathered,
        "band_size": len(active),
        "deficit": food_deficit,
    }

    # ── Step 2: Pay cycle ────────────────────────────────────────────────
    retainer = calculate_weekly_retainer(active)
    cost_copper = retainer["total_copper"]
    treasury_copper = band_meta.get("treasury_silver", 0) * 10
    can_pay = treasury_copper >= cost_copper
    pay_step: dict = {
        "cost_copper": cost_copper,
        "treasury_copper": treasury_copper,
        "paid": can_pay,
    }
    non_pay_result = None
    if can_pay:
        silver_spent = cost_copper // 10
        pay_step["silver_spent"] = silver_spent
        pay_step["treasury_after"] = band_meta.get("treasury_silver", 0) - silver_spent
        if not dry_run:
            band_meta["treasury_silver"] = max(
                0, band_meta.get("treasury_silver", 0) - silver_spent,
            )
    else:
        days_late = 7
        non_pay_result = roll_non_payment(days_late)
        pay_step["non_payment"] = non_pay_result
        summary["warnings"].append("Pay deficit — non-payment rolled.")
    summary["steps"]["pay"] = pay_step

    # ── Step 3: Morale triggers ──────────────────────────────────────────
    morale_events = []
    if not can_pay:
        morale_events.append("late_pay")
    if food_deficit:
        morale_events.append("food_deficit")

    current_morale = band_meta.get("morale", 4)
    if morale_events:
        morale_result = apply_morale_events(current_morale, morale_events)
        if not dry_run:
            band_meta["morale"] = morale_result["new_morale"]
        summary["steps"]["morale"] = {
            "events_fired": morale_events,
            "old_morale": current_morale,
            "new_morale": morale_result["new_morale"] if morale_events else current_morale,
            "morale_name": morale_result.get("morale_name", ""),
        }
    else:
        summary["steps"]["morale"] = {
            "events_fired": [],
            "morale": current_morale,
            "note": "No morale triggers this week.",
        }

    # ── Step 4: Named Man loyalty tick ───────────────────────────────────
    band_for_tick = {
        "members": members,
        "day_of_year": day_start,
        "band": band_meta,
    }
    loyalty_results = _loyalty_tick(
        band_for_tick,
        captain_wil=captain_wil,
        command_skill=command_skill,
        band_morale=band_meta.get("morale", current_morale),
    )
    for lr in loyalty_results:
        if lr.get("change", 0) < 0 and lr.get("new_loyalty", 5) <= 1:
            summary["warnings"].append(
                f"{lr['member']} loyalty = 1 — trigger_check recommended next week.",
            )
    summary["steps"]["loyalty"] = loyalty_results

    # ── Step 5: Contracts ────────────────────────────────────────────────
    location = band_meta.get("location", "village")
    reputation = band_meta.get("reputation", 1)
    settlement_type = "village"  # default; override via --settlement flag
    contracts = _contracts_via_subprocess(reputation, settlement_type, season)
    summary["steps"]["contracts"] = {
        "reputation": reputation,
        "settlement": location,
        "new_offers": len(contracts),
        "offers": contracts[:3],  # top 3
    }

    if location and location not in {"village", "hamlet", "large_village", "small_town"}:
        summary["steps"]["replacements"] = _settlement_replacement_market(location)
    else:
        summary["steps"]["replacements"] = {
            "settlement": location,
            "mount_replacements": [],
            "dog_replacements": [],
            "future_mount_stock": 0,
            "future_dog_stock": 0,
        }

    # ── Step 6: Hidden events (stub) ─────────────────────────────────────
    summary["steps"]["hidden_events"] = {
        "note": (
            "hidden_info.py has no list_due command yet. "
            "Check data/hidden_events/ manually for day " + str(day_start + 7) + "."
        ),
    }

    summary["steps"]["animals"] = _run_seasonal_animal_ticks(year, day_start, day_start + 7, dry_run)

    # ── Step 7: State save ───────────────────────────────────────────────
    day_end = day_start + 7
    if not dry_run:
        band_meta["day_of_year"] = day_end
        _save(data, band_file)
        _append_tick_log(summary)
        _append_journal(summary)

    summary["saved"] = not dry_run
    return summary


# ── Logging helpers ───────────────────────────────────────────────────────

def _append_tick_log(summary: dict) -> None:
    """Append summary to workspace/weekly_ticks.json."""
    os.makedirs(_WORKSPACE, exist_ok=True)
    log = []
    if os.path.exists(_TICK_LOG):
        with open(_TICK_LOG, "r", encoding="utf-8") as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []
    log.append(summary)
    with open(_TICK_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def _append_journal(summary: dict) -> None:
    """Append a Markdown weekly summary to workspace/journal.md if it exists."""
    os.makedirs(_WORKSPACE, exist_ok=True)
    forage = summary["steps"].get("foraging", {})
    pay = summary["steps"].get("pay", {})
    morale_step = summary["steps"].get("morale", {})
    loyalty = summary["steps"].get("loyalty", [])
    contracts = summary["steps"].get("contracts", {})
    replacements = summary["steps"].get("replacements", {})
    animals = summary["steps"].get("animals", {})

    lines = [
        f"\n## Week {summary['week']} — Day {summary['day_start']}→{summary['day_end']}"
        f" ({summary['season'].replace('_', ' ').title()})\n",
        f"- **Foraging:** {forage.get('foragers','?')} foragers, "
        f"{forage.get('terrain','?')} → {forage.get('food_gathered','?')} food units"
        f"{'  ⚠ DEFICIT' if forage.get('deficit') else ''}\n",
        f"- **Pay:** {'✓ PAID' if pay.get('paid') else '✗ MISSED'}"
        f" ({pay.get('cost_copper','?')} copper)"
        f" | Treasury after: {pay.get('treasury_after', pay.get('treasury_copper','?'))} copper\n",
        f"- **Morale:** {morale_step.get('morale_name', morale_step.get('morale','?'))}"
        f" — events: {morale_step.get('events_fired', []) or 'none'}\n",
    ]
    for lr in loyalty:
        if lr.get("change", 0) != 0:
            lines.append(
                f"- **Loyalty [{lr['member']}]:** "
                f"{lr.get('old_loyalty','?')} → {lr.get('new_loyalty','?')}"
                f" ({lr.get('change',0):+d}) — {lr.get('note','')}\n",
            )
    lines.append(
        f"- **Contracts:** {contracts.get('new_offers', 0)} new offers"
        f" (reputation {contracts.get('reputation','?')}, {contracts.get('settlement','?')})\n",
    )
    if replacements.get("settlement"):
        lines.append(
            f"- **Replacements [{replacements['settlement']}]:** "
            f"{len(replacements.get('mount_replacements', []))} mounts, "
            f"{len(replacements.get('dog_replacements', []))} dogs"
            f" | future stock {replacements.get('future_mount_stock', 0)} foals, "
            f"{replacements.get('future_dog_stock', 0)} pups\n",
        )
    if animals.get("triggered"):
        horse_foals = sum(entry.get("foals_born", 0) for entry in animals.get("horse_herds", []))
        dog_pups = sum(entry.get("pups_born", 0) for entry in animals.get("dog_kennels", []))
        lines.append(
            f"- **Seasonal Breeding [{animals.get('season_id')}]:** "
            f"{horse_foals} foals, {dog_pups} pups\n",
        )
    for w in summary.get("warnings", []):
        lines.append(f"- ⚠ {w}\n")

    entry = "".join(lines)
    mode = "a" if os.path.exists(_JOURNAL) else "w"
    with open(_JOURNAL, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write("# Iron Ledger — Campaign Journal\n")
        f.write(entry)


# ── History command ───────────────────────────────────────────────────────

def load_history(last_n: int = 4) -> list[dict]:
    if not os.path.exists(_TICK_LOG):
        return []
    with open(_TICK_LOG, "r", encoding="utf-8") as f:
        try:
            log = json.load(f)
        except json.JSONDecodeError:
            return []
    return log[-last_n:]


# ── Pretty print ──────────────────────────────────────────────────────────

def _print_summary(s: dict) -> None:
    forage = s["steps"].get("foraging", {})
    pay = s["steps"].get("pay", {})
    morale_step = s["steps"].get("morale", {})
    loyalty = s["steps"].get("loyalty", [])
    contracts = s["steps"].get("contracts", {})
    replacements = s["steps"].get("replacements", {})
    animals = s["steps"].get("animals", {})

    print(
        f"\n=== WEEK {s['week']} TICK — Day {s['day_start']} → {s['day_end']}"
        f" ({s['season'].replace('_',' ').title()})"
        f"{' [DRY RUN]' if s.get('dry_run') else ''} ===",
    )
    print(
        f"Foraging:  {forage.get('foragers','?')} foragers, "
        f"{forage.get('terrain','?')} → "
        f"+{forage.get('food_gathered','?')} food units"
        f"{'  ⚠ DEFICIT' if forage.get('deficit') else ''}",
    )
    if pay.get("paid"):
        silver = pay.get("silver_spent", pay.get("cost_copper", 0) // 10)
        after = pay.get("treasury_after", "?")
        print(f"Pay:       {silver}s paid. Treasury → {after}s")
    else:
        print(
            f"Pay:       ✗ MISSED ({pay.get('cost_copper','?')} copper needed, "
            f"{pay.get('treasury_copper','?')} copper available)",
        )
        for r in pay.get("non_payment", []):
            print(f"  !! [{r['event_type']}] {r['description']}")
    morale_val = morale_step.get("new_morale", morale_step.get("morale", "?"))
    morale_name = morale_step.get("morale_name", "")
    events_desc = (
        ", ".join(morale_step.get("events_fired", [])) or "none"
    )
    print(f"Morale:    {'STEADY' if not morale_step.get('events_fired') else events_desc}"
          f" ({morale_val}{(' / ' + morale_name) if morale_name else ''})")
    for lr in loyalty:
        if lr.get("change", 0) != 0:
            nm = LOYALTY_NAMES.get(lr.get("new_loyalty", 3), "")
            print(
                f"Loyalty:   {lr['member']} [{lr.get('old_loyalty','?')} → "
                f"{lr.get('new_loyalty','?')} / {nm}]"
                f"  {lr.get('change',0):+d} — {lr.get('note','')}",
            )
        else:
            print(f"Loyalty:   {lr['member']} — {lr.get('note','no change')}")
    print(
        f"Contracts: {contracts.get('new_offers', 0)} new offers"
        f" (reputation {contracts.get('reputation','?')}, {contracts.get('settlement','?')})",
    )
    if replacements.get("settlement"):
        print(
            f"Replacem.: {len(replacements.get('mount_replacements', []))} mounts, "
            f"{len(replacements.get('dog_replacements', []))} dogs"
            f" at {replacements.get('settlement')}",
        )
    if animals.get("triggered"):
        horse_foals = sum(entry.get("foals_born", 0) for entry in animals.get("horse_herds", []))
        dog_pups = sum(entry.get("pups_born", 0) for entry in animals.get("dog_kennels", []))
        print(
            f"Animals:   seasonal tick {animals.get('season_id')} "
            f"→ {horse_foals} foals, {dog_pups} pups",
        )
    for w in s.get("warnings", []):
        print(f"⚠  {w}")
    if s.get("saved"):
        print(f"State:     Day {s['day_end']}. band_state.yaml updated.")
    else:
        print("State:     DRY RUN — no files written.")


# ── CLI ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Iron Ledger — Band Weekly Tick Orchestrator",
    )
    sub = parser.add_subparsers(dest="command")

    # run
    run_p = sub.add_parser("run", help="Execute one weekly tick")
    run_p.add_argument(
        "--band-file", default=_BAND_STATE,
        help=f"Band state YAML (default: {_BAND_STATE})",
    )
    run_p.add_argument(
        "--season", required=False, default="long_dark",
        choices=["thaw", "long_sun", "harvest", "long_dark"],
    )
    run_p.add_argument(
        "--terrain", required=False, default="forest",
        choices=["forest", "hills", "mountain", "wetland", "coast",
                 "tundra", "farmland", "river"],
    )
    run_p.add_argument("--foragers", type=int, default=3)
    run_p.add_argument("--forager-skill", type=float, default=0.0)
    run_p.add_argument("--week", type=int, default=None)
    run_p.add_argument("--captain-wil", type=int, default=None)
    run_p.add_argument("--command-skill", type=int, default=None)
    run_p.add_argument(
        "--dry-run", action="store_true",
        help="Preview without writing any files",
    )
    run_p.add_argument("--json", action="store_true")

    # history
    hist_p = sub.add_parser("history", help="Show last N weekly ticks")
    hist_p.add_argument("--last", type=int, default=4)
    hist_p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "run":
        summary = run_weekly_tick(
            band_file=args.band_file,
            season=args.season,
            terrain=args.terrain,
            forager_count=args.foragers,
            forager_skill=args.forager_skill,
            week_override=args.week,
            captain_wil=args.captain_wil,
            command_skill=args.command_skill,
            dry_run=args.dry_run,
        )
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            _print_summary(summary)

    elif args.command == "history":
        entries = load_history(args.last)
        if args.json:
            print(json.dumps(entries, indent=2))
        else:
            if not entries:
                print("No weekly tick history found.")
            for e in entries:
                _print_summary(e)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
