#!/usr/bin/env python3
"""
Iron Ledger — Morale Engine

Tracks band morale (1-5), Named Man loyalty (1-5), grievances, and
resolution. All rules from 20_SIMULATION_RULES.md §6 and §12.

Usage:
    python morale.py check --morale 4 --events late_pay,named_killed
    python morale.py resolve --captain-wil 7 --command-skill 3 --grievance late_wages
    python morale.py loyalty --loyalty 3 --trigger-fired --captain-wil 7 --command-skill 3
    python morale.py status --morale 3
    python morale.py loyalty_tick --band-file ../data/band_state.yaml --captain-wil 7 --command-skill 3 --morale 4
    python morale.py agenda_advance --band-file ../data/band_state.yaml --member "Kell Hook"
    python morale.py trigger_check --band-file ../data/band_state.yaml --member "Kell Hook" --captain-wil 7 --command-skill 3 --morale 4
    python morale.py named_man_defect --band-file ../data/band_state.yaml --member "Lump" --cause "Left in the night"
"""

import argparse
import json
import sys

try:
    import yaml as _yaml
except ImportError:
    _yaml = None

sys.path.insert(0, __file__ and __import__('os').path.dirname(__file__) or '.')
from engine import resolve_check, compute_success_chance, ResultLevel

# --- Morale Triggers ---
MORALE_TRIGGERS = {
    "won_engagement": +1,
    "paid_on_time": +1,         # once per season
    "secured_winter_hall": +1,
    "heavy_casualties": -1,     # 20%+ casualties
    "late_pay": -1,             # 3+ days
    "captain_broke_oath": -2,
    "named_killed": -1,
    "atrocity_no_plunder": -1,
    "food_deficit": -1,         # 3+ days
    "the_hush_extended": -1,    # 10+ minutes
}

MORALE_NAMES = {
    5: "Keen",
    4: "Steady",
    3: "Shaken",
    2: "Wavering",
    1: "Broken",
}

MORALE_EFFECTS = {
    5: "+5 all rolls, no desertion risk",
    4: "No modifiers",
    3: "-5 all rolls, minor desertion risk",
    2: "-10 all rolls, active desertion risk",
    1: "-15 all rolls, band may scatter",
}

MORALE_ROLL_MOD = {
    5: +5,
    4: 0,
    3: -5,
    2: -10,
    1: -15,
}

# --- Grievance Difficulty ---
GRIEVANCE_DIFFICULTY = {
    "late_wages": 0,
    "named_killed": 0,
    "broken_oath": -15,
    "atrocity_no_gain": -15,
}
STACKED_PENALTY = -10  # per 3+ of same type


# --- Loyalty Scale ---
LOYALTY_NAMES = {
    5: "Blood-bound",
    4: "Personally invested",
    3: "Professional",
    2: "Discontented",
    1: "Ready to leave/betray",
}


def apply_morale_events(current_morale: int, events: list[str]) -> dict:
    """Apply a list of event triggers to current morale. Returns new morale and log."""
    log = []
    total_change = 0
    for event in events:
        change = MORALE_TRIGGERS.get(event, 0)
        if change != 0:
            log.append({"event": event, "change": change})
            total_change += change
        else:
            log.append({"event": event, "change": 0, "note": "unknown event"})

    new_morale = max(1, min(5, current_morale + total_change))
    return {
        "previous_morale": current_morale,
        "events": log,
        "total_change": total_change,
        "new_morale": new_morale,
        "morale_name": MORALE_NAMES.get(new_morale, "Unknown"),
        "effect": MORALE_EFFECTS.get(new_morale, ""),
    }


def resolve_grievance(
    captain_wil: int,
    command_skill: int,
    grievance_type: str,
    current_morale: int,
    stacked_count: int = 0,
) -> dict:
    """Captain tries to resolve a grievance at the fire. Uses Command check."""
    base_mod = GRIEVANCE_DIFFICULTY.get(grievance_type, 0)
    morale_mod = MORALE_ROLL_MOD.get(current_morale, 0)
    stack_mod = STACKED_PENALTY if stacked_count >= 3 else 0
    total_mods = base_mod + morale_mod + stack_mod

    result = resolve_check(captain_wil, command_skill, total_mods, "grievance_resolution")

    success = result.result in (ResultLevel.SUCCESS, ResultLevel.CRITICAL_SUCCESS)
    morale_change = 0
    if success:
        morale_change = +1 if result.result == ResultLevel.CRITICAL_SUCCESS else 0
    else:
        morale_change = -1

    return {
        "grievance_type": grievance_type,
        "check_result": result.to_dict(),
        "success": success,
        "morale_change": morale_change,
        "modifiers": {
            "grievance": base_mod,
            "morale": morale_mod,
            "stacked": stack_mod,
            "total": total_mods,
        },
    }


def resolve_loyalty_check(
    captain_wil: int,
    command_skill: int,
    current_morale: int,
    relationship_mod: int = 0,
) -> dict:
    """When a Named Man's Trigger fires, captain makes loyalty check."""
    morale_mod = MORALE_ROLL_MOD.get(current_morale, 0)
    total_mods = morale_mod + relationship_mod

    result = resolve_check(captain_wil, command_skill, total_mods, "loyalty_check")

    success = result.result in (ResultLevel.SUCCESS, ResultLevel.CRITICAL_SUCCESS)
    loyalty_change = 0 if success else -1

    return {
        "check_result": result.to_dict(),
        "success": success,
        "loyalty_change": loyalty_change,
        "modifiers": {
            "morale": morale_mod,
            "relationship": relationship_mod,
            "total": total_mods,
        },
    }


def update_loyalty(
    current_loyalty: int,
    trigger_fired: bool = False,
    trigger_check_failed: bool = False,
    agenda_progress: bool = False,
    agenda_ignored_days: int = 0,
) -> dict:
    """Update Named Man loyalty based on events."""
    changes = []
    total = 0

    if trigger_fired and trigger_check_failed:
        changes.append({"reason": "trigger_fired_unresolved", "change": -1})
        total -= 1

    if agenda_progress:
        changes.append({"reason": "agenda_progress", "change": +1})
        total += 1

    if agenda_ignored_days >= 30:
        months_ignored = agenda_ignored_days // 30
        change = -months_ignored
        changes.append({"reason": f"agenda_ignored_{months_ignored}_months", "change": change})
        total += change

    new_loyalty = max(1, min(5, current_loyalty + total))
    return {
        "previous_loyalty": current_loyalty,
        "changes": changes,
        "total_change": total,
        "new_loyalty": new_loyalty,
        "loyalty_name": LOYALTY_NAMES.get(new_loyalty, "Unknown"),
    }


def morale_status(morale: int) -> dict:
    """Get full morale status."""
    return {
        "morale": morale,
        "name": MORALE_NAMES.get(morale, "Unknown"),
        "effect": MORALE_EFFECTS.get(morale, ""),
        "roll_modifier": MORALE_ROLL_MOD.get(morale, 0),
    }


# ─────────────────────────────────────────────────────────────────────
# Band-file helpers
# ─────────────────────────────────────────────────────────────────────

def _load_band(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    if path.endswith((".yaml", ".yml")):
        if _yaml is None:
            raise ImportError("pyyaml is required for YAML band files.")
        return _yaml.safe_load(raw)
    return json.loads(raw)


def _save_band(band: dict, path: str):
    if path.endswith((".yaml", ".yml")):
        if _yaml is None:
            raise ImportError("pyyaml is required for YAML band files.")
        with open(path, "w", encoding="utf-8") as f:
            _yaml.dump(band, f, allow_unicode=True, sort_keys=False)
    else:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(band, f, indent=2, ensure_ascii=False)


def _find_member(band: dict, name: str) -> dict | None:
    members = band.get("members", [])
    for m in members:
        if m["name"].lower() == name.lower():
            return m
    return None


def _named_men(band: dict) -> list[dict]:
    """Return all members with a loyalty field (Named Men)."""
    return [m for m in band.get("members", []) if m.get("loyalty") is not None]


def _current_day(band: dict) -> int:
    """Extract current day_of_year from flat or nested band structure."""
    return band.get("day_of_year", band.get("band", {}).get("day_of_year", 0))


# ─────────────────────────────────────────────────────────────────────
# Band-aware Named Man helpers
# ─────────────────────────────────────────────────────────────────────

def loyalty_tick(
    band: dict,
    captain_wil: int,
    command_skill: int,
    band_morale: int,
) -> list[dict]:
    """
    Apply loyalty erosion to ALL Named Men in band.
    For each Named Man: if agenda_last_advanced_day is set and
    (current_day - agenda_last_advanced_day) >= 30, deduct -1 per
    full 30-day block.  Returns list of change records.
    """
    current = _current_day(band)
    results = []
    for m in _named_men(band):
        if m.get("status") == "dead":
            continue
        last_day = m.get("agenda_last_advanced_day")
        if last_day is None:
            results.append({
                "member": m["name"],
                "loyalty": m["loyalty"],
                "change": 0,
                "note": "no agenda_last_advanced_day set — use agenda_advance first",
            })
            continue
        ignored_days = current - last_day
        if ignored_days < 30:
            results.append({
                "member": m["name"],
                "loyalty": m["loyalty"],
                "change": 0,
                "note": f"{ignored_days} days since last agenda advance (< 30)",
            })
            continue
        months_ignored = ignored_days // 30
        erosion = -months_ignored
        old = m["loyalty"]
        m["loyalty"] = max(1, old + erosion)
        results.append({
            "member": m["name"],
            "old_loyalty": old,
            "new_loyalty": m["loyalty"],
            "change": erosion,
            "ignored_days": ignored_days,
            "note": f"Agenda ignored {months_ignored} month(s)",
        })
    return results


def agenda_advance(band: dict, member_name: str) -> dict:
    """Record that a Named Man's agenda was meaningfully advanced today."""
    m = _find_member(band, member_name)
    if not m:
        return {"error": f"Member '{member_name}' not found."}
    if m.get("loyalty") is None:
        return {"error": f"'{member_name}' is not a Named Man."}
    current = _current_day(band)
    m["agenda_last_advanced_day"] = current
    # Loyalty +1 for agenda progress
    old = m["loyalty"]
    m["loyalty"] = min(5, old + 1)
    return {
        "member": member_name,
        "old_loyalty": old,
        "new_loyalty": m["loyalty"],
        "change": +1,
        "agenda_last_advanced_day": current,
        "agenda": m.get("agenda", ""),
    }


def trigger_check(
    band: dict,
    member_name: str,
    captain_wil: int,
    command_skill: int,
    band_morale: int,
) -> dict:
    """
    Named Man's trigger has fired.  Captain makes loyalty check.
    On failure: loyalty -1.  On critical success: loyalty +1.
    """
    m = _find_member(band, member_name)
    if not m:
        return {"error": f"Member '{member_name}' not found."}
    if m.get("loyalty") is None:
        return {"error": f"'{member_name}' is not a Named Man."}
    relationship_mod = m.get("relationship_modifier", 0)
    check = resolve_loyalty_check(
        captain_wil, command_skill, band_morale, relationship_mod,
    )
    old = m["loyalty"]
    if check["success"] and check["check_result"].get("result") == ResultLevel.CRITICAL_SUCCESS.value:
        m["loyalty"] = min(5, old + 1)
    elif not check["success"]:
        m["loyalty"] = max(1, old - 1)
    check["member"] = member_name
    check["trigger"] = m.get("trigger", "")
    check["old_loyalty"] = old
    check["new_loyalty"] = m["loyalty"]
    check["loyalty_change"] = m["loyalty"] - old
    return check


def named_man_defect(band: dict, member_name: str, cause: str = "") -> dict:
    """
    A Named Man at loyalty 1 defects or leaves.
    Sets status='left', records cause and final note.
    """
    m = _find_member(band, member_name)
    if not m:
        return {"error": f"Member '{member_name}' not found."}
    if m.get("loyalty") is None:
        return {"error": f"'{member_name}' is not a Named Man."}
    old_status = m.get("status", "active")
    m["status"] = "left"
    note = cause or "Loyalty fell to 1 — left the band."
    m.setdefault("notes", [])
    if isinstance(m["notes"], list):
        m["notes"].append(note)
    else:
        m["notes"] = [str(m["notes"]), note]
    return {
        "member": member_name,
        "old_status": old_status,
        "new_status": "left",
        "loyalty": m["loyalty"],
        "trigger": m.get("trigger", ""),
        "agenda": m.get("agenda", ""),
        "cause": note,
    }

def main():
    parser = argparse.ArgumentParser(description="Iron Ledger Morale Engine")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview mutations without writing band file",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- check ---
    chk_p = subparsers.add_parser("check", help="Apply morale events")
    chk_p.add_argument("--morale", type=int, required=True, help="Current morale (1-5)")
    chk_p.add_argument("--events", type=str, required=True,
                        help="Comma-separated events (e.g., late_pay,named_killed)")
    chk_p.add_argument("--json", action="store_true")

    # --- resolve ---
    res_p = subparsers.add_parser("resolve", help="Resolve a grievance")
    res_p.add_argument("--captain-wil", type=int, required=True)
    res_p.add_argument("--command-skill", type=int, required=True)
    res_p.add_argument("--grievance", type=str, required=True,
                        choices=list(GRIEVANCE_DIFFICULTY.keys()))
    res_p.add_argument("--morale", type=int, default=4)
    res_p.add_argument("--stacked", type=int, default=0)
    res_p.add_argument("--json", action="store_true")

    # --- loyalty ---
    loy_p = subparsers.add_parser("loyalty", help="Named Man loyalty check or update")
    loy_p.add_argument("--loyalty", type=int, required=True, help="Current loyalty (1-5)")
    loy_p.add_argument("--trigger-fired", action="store_true")
    loy_p.add_argument("--captain-wil", type=int, default=7)
    loy_p.add_argument("--command-skill", type=int, default=3)
    loy_p.add_argument("--morale", type=int, default=4)
    loy_p.add_argument("--relationship-mod", type=int, default=0)
    loy_p.add_argument("--agenda-progress", action="store_true")
    loy_p.add_argument("--agenda-ignored-days", type=int, default=0)
    loy_p.add_argument("--json", action="store_true")

    # --- status ---
    sta_p = subparsers.add_parser("status", help="Show morale status")
    sta_p.add_argument("--morale", type=int, required=True)
    sta_p.add_argument("--json", action="store_true")

    # --- loyalty_tick ---
    lt_p = subparsers.add_parser("loyalty_tick",
                                 help="Erode Named Man loyalty for agenda neglect")
    lt_p.add_argument("--band-file", required=True)
    lt_p.add_argument("--captain-wil", type=int, default=7)
    lt_p.add_argument("--command-skill", type=int, default=3)
    lt_p.add_argument("--morale", type=int, default=4)
    lt_p.add_argument("--save", action="store_true")
    lt_p.add_argument("--json", action="store_true")

    # --- agenda_advance ---
    aa_p = subparsers.add_parser("agenda_advance",
                                 help="Record agenda progress for a Named Man")
    aa_p.add_argument("--band-file", required=True)
    aa_p.add_argument("--member", required=True)
    aa_p.add_argument("--save", action="store_true")
    aa_p.add_argument("--json", action="store_true")

    # --- trigger_check ---
    tc_p = subparsers.add_parser("trigger_check",
                                 help="Fire a Named Man trigger, run captain loyalty check")
    tc_p.add_argument("--band-file", required=True)
    tc_p.add_argument("--member", required=True)
    tc_p.add_argument("--captain-wil", type=int, required=True)
    tc_p.add_argument("--command-skill", type=int, required=True)
    tc_p.add_argument("--morale", type=int, default=4)
    tc_p.add_argument("--save", action="store_true")
    tc_p.add_argument("--json", action="store_true")

    # --- named_man_defect ---
    nd_p = subparsers.add_parser("named_man_defect",
                                 help="Named Man leaves or defects from band")
    nd_p.add_argument("--band-file", required=True)
    nd_p.add_argument("--member", required=True)
    nd_p.add_argument("--cause", default="")
    nd_p.add_argument("--save", action="store_true")
    nd_p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "check":
        events = [e.strip() for e in args.events.split(",") if e.strip()]
        result = apply_morale_events(args.morale, events)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Morale: {result['previous_morale']} -> {result['new_morale']} "
                  f"({result['morale_name']})")
            for e in result["events"]:
                print(f"  {e['event']}: {e['change']:+d}")
            print(f"Effect: {result['effect']}")

    elif args.command == "resolve":
        result = resolve_grievance(
            args.captain_wil, args.command_skill,
            args.grievance, args.morale, args.stacked,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            status = "SUCCESS" if result["success"] else "FAILED"
            print(f"Grievance ({args.grievance}): {status}")
            print(f"  Check: {result['check_result']['details']}")
            if result["morale_change"]:
                print(f"  Morale change: {result['morale_change']:+d}")

    elif args.command == "loyalty":
        # If trigger fired, do a loyalty check first
        trigger_failed = False
        check_result = None
        if args.trigger_fired:
            check = resolve_loyalty_check(
                args.captain_wil, args.command_skill,
                args.morale, args.relationship_mod,
            )
            trigger_failed = not check["success"]
            check_result = check

        result = update_loyalty(
            args.loyalty,
            trigger_fired=args.trigger_fired,
            trigger_check_failed=trigger_failed,
            agenda_progress=args.agenda_progress,
            agenda_ignored_days=args.agenda_ignored_days,
        )
        if check_result:
            result["trigger_check"] = check_result

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Loyalty: {result['previous_loyalty']} -> {result['new_loyalty']} "
                  f"({result['loyalty_name']})")
            for c in result["changes"]:
                print(f"  {c['reason']}: {c['change']:+d}")

    elif args.command == "status":
        result = morale_status(args.morale)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Morale {result['morale']}: {result['name']}")
            print(f"  Effect: {result['effect']}")
            print(f"  Roll modifier: {result['roll_modifier']:+d}")

    elif args.command == "loyalty_tick":
        band = _load_band(args.band_file)
        results = loyalty_tick(band, args.captain_wil, args.command_skill, args.morale)
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for r in results:
                name = r["member"]
                if r.get("change", 0) != 0:
                    old = r.get("old_loyalty", "?")
                    new = r.get("new_loyalty", "?")
                    print(f"  {name}: loyalty {old} -> {new} ({r['change']:+d})  [{r.get('note','')}]")
                else:
                    print(f"  {name}: no change  [{r.get('note','')}]")

    elif args.command == "agenda_advance":
        band = _load_band(args.band_file)
        result = agenda_advance(band, args.member)
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"{result['member']}: agenda advanced on day {result['agenda_last_advanced_day']}")
            print(f"  Loyalty: {result['old_loyalty']} -> {result['new_loyalty']} (+1)")
            print(f"  Agenda: {result['agenda']}")

    elif args.command == "trigger_check":
        band = _load_band(args.band_file)
        result = trigger_check(band, args.member,
                               args.captain_wil, args.command_skill, args.morale)
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            status = "SUCCESS" if result["success"] else "FAILED"
            name = result["member"]
            print(f"Trigger check — {name}: {status}")
            print(f"  Trigger: {result['trigger']}")
            print(f"  Loyalty: {result['old_loyalty']} -> {result['new_loyalty']} "
                  f"({result['loyalty_change']:+d})")

    elif args.command == "named_man_defect":
        band = _load_band(args.band_file)
        result = named_man_defect(band, args.member, args.cause)
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        if args.save and not args.dry_run:
            _save_band(band, args.band_file)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"{result['member']} has left the band.")
            print(f"  Cause: {result['cause']}")
            print(f"  Loyalty at departure: {result['loyalty']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
