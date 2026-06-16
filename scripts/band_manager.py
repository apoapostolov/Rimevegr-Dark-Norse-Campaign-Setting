#!/usr/bin/env python3
"""
Iron Ledger — Band Manager

Full CRUD for mercenary band state: members, treasury, morale, reputation,
contracts, and snapshot serialization. Central state management for the
simulation.

Usage:
    python band_manager.py create --name "Voss's Black Axes" --captain Voss
    python band_manager.py add-member --band-file band.json --member '{"name":"Bjorn","rank":"common"}'
    python band_manager.py remove-member --band-file band.json --name Bjorn
    python band_manager.py snapshot --band-file band.json
    python band_manager.py summary --band-file band.json
"""

import argparse
import json
import os
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path

try:
    import yaml as _yaml
except ImportError:
    _yaml = None  # type: ignore

sys.path.insert(0, __file__ and __import__('os').path.dirname(__file__) or '.')
from engine import compute_max_hp, compute_carry_limit
from animal_care import ensure_animal_health

# --- Default Band Structure ---
DEFAULT_BAND = {
    "name": "Unnamed Band",
    "captain": None,
    "archetype": "standard",    # tyrant, standard, fraternal, kin_clan
    "reputation": 1,
    "morale": 4,                # 1-5, default Steady
    "treasury_silver": 0,
    "treasury_goods_value": 0,
    "debts_owed": 0,
    "credits_pending": 0,
    "current_contract": None,
    "feud_tracker": {},         # settlement_name -> feud_level
    "members": [],
    "year": 312,
    "day_of_year": 1,
    "location": None,
    "notes": [],
    "history": [],
}

# --- Member Template ---
DEFAULT_MEMBER = {
    "name": "Unknown",
    "rank": "common",       # common, veteran, named_man, captain
    "background": "farmer",
    "gender": "male",
    "mig": 5, "nim": 5, "tou": 5, "wit": 5, "wil": 5, "wyr": 1,
    "skills": {},
    "weapon": "hand_axe",
    "weapon_base": 6,
    "weapon_speed": 3,
    "weapon_skill": 1,
    "shield_skill": 0,
    "shield_def": 0,
    "armor": {"head": 0, "torso": 2, "right_arm": 1, "left_arm": 1,
              "legs": 1, "hands": 0, "feet": 0},
    "gear_kg": 5.0,
    "hp": None,         # auto-calculated
    "max_hp": None,     # auto-calculated
    "wounds": [],
    "status": "active",     # active, wounded, dead, deserted
    # Named Man fields
    "trigger": None,
    "agenda": None,
    "loyalty": None,        # 1-5, only for named men
}


def create_band(name: str, captain_name: str, archetype: str = "standard") -> dict:
    """Create a new band with a captain."""
    band = deepcopy(DEFAULT_BAND)
    band["name"] = name
    band["archetype"] = archetype

    captain = deepcopy(DEFAULT_MEMBER)
    captain["name"] = captain_name
    captain["rank"] = "captain"
    captain["mig"] = 7
    captain["nim"] = 6
    captain["tou"] = 6
    captain["wit"] = 6
    captain["wil"] = 7
    captain["wyr"] = 2
    captain["skills"] = {"command": 3, "axes": 3, "intimidate": 2, "shields": 2}
    captain["weapon_skill"] = 3
    captain["armor"] = {"head": 4, "torso": 5, "right_arm": 3, "left_arm": 3,
                        "legs": 0, "hands": 0, "feet": 0}
    captain["shield_skill"] = 2
    captain["shield_def"] = 3
    captain["gear_kg"] = 12.0
    _compute_member_hp(captain)

    band["captain"] = captain_name
    band["members"].append(captain)
    band["history"].append({
        "event": "band_created",
        "details": f"Band '{name}' formed under Captain {captain_name}.",
    })

    return band


def _compute_member_hp(member: dict):
    """Compute max_hp and set hp if not set."""
    member["max_hp"] = compute_max_hp(member["tou"], member["mig"])
    if member["hp"] is None:
        member["hp"] = member["max_hp"]


def add_member(band: dict, member: dict) -> dict:
    """Add a member to the band."""
    m = deepcopy(DEFAULT_MEMBER)
    m.update(member)
    _compute_member_hp(m)

    # Check for duplicate names
    existing = [mem["name"] for mem in band["members"]]
    if m["name"] in existing:
        return {"error": f"Member '{m['name']}' already exists in band."}

    band["members"].append(m)
    band["history"].append({
        "event": "member_added",
        "details": f"{m['name']} ({m['rank']}) joined the band.",
    })

    return {"added": m["name"], "rank": m["rank"], "band_size": len(band["members"])}


def remove_member(band: dict, name: str, reason: str = "departed") -> dict:
    """Remove a member from the band."""
    for i, m in enumerate(band["members"]):
        if m["name"].lower() == name.lower():
            removed = band["members"].pop(i)
            band["history"].append({
                "event": "member_removed",
                "details": f"{removed['name']} ({removed['rank']}) {reason}.",
            })
            return {"removed": removed["name"], "reason": reason,
                    "band_size": len(band["members"])}

    return {"error": f"Member '{name}' not found."}


def update_member(band: dict, name: str, updates: dict) -> dict:
    """Update a member's attributes."""
    for m in band["members"]:
        if m["name"].lower() == name.lower():
            changed = {}
            for key, value in updates.items():
                if key in m:
                    old = m[key]
                    m[key] = value
                    changed[key] = {"old": old, "new": value}
            # Recompute HP if attributes changed
            if "tou" in updates or "mig" in updates:
                _compute_member_hp(m)
            return {"updated": name, "changes": changed}

    return {"error": f"Member '{name}' not found."}


def get_member(band: dict, name: str) -> dict | None:
    """Find a member by name."""
    for m in band["members"]:
        if m["name"].lower() == name.lower():
            return m
    return None


def band_summary(band: dict) -> dict:
    """Generate a summary of the band's current state."""
    members = band["members"]
    active = [m for m in members if m["status"] == "active"]
    wounded = [m for m in members if m["status"] == "wounded"]
    dead = [m for m in members if m["status"] == "dead"]
    deserted = [m for m in members if m["status"] == "deserted"]

    rank_counts = {}
    for m in active:
        rank = m["rank"]
        rank_counts[rank] = rank_counts.get(rank, 0) + 1

    total_carry = sum(compute_carry_limit(m["mig"]) for m in active)
    total_gear = sum(m.get("gear_kg", 5.0) for m in active)

    # Weekly retainer cost (copper)
    from ledger import WEEKLY_RETAINER
    weekly_cost = sum(
        WEEKLY_RETAINER.get(m["rank"], WEEKLY_RETAINER["common"])
        for m in active if m["rank"] != "captain"
    )

    return {
        "name": band["name"],
        "captain": band["captain"],
        "archetype": band["archetype"],
        "reputation": band["reputation"],
        "morale": band["morale"],
        "treasury_silver": band["treasury_silver"],
        "total_members": len(members),
        "active": len(active),
        "wounded": len(wounded),
        "dead": len(dead),
        "deserted": len(deserted),
        "rank_breakdown": rank_counts,
        "total_carry_capacity_kg": round(total_carry, 1),
        "total_gear_weight_kg": round(total_gear, 1),
        "weekly_retainer_copper": weekly_cost,
        "current_contract": band.get("current_contract"),
        "location": band.get("location"),
        "year": band.get("year"),
        "day_of_year": band.get("day_of_year"),
    }


def combat_roster(band: dict) -> list[dict]:
    """Get members formatted for combat_sim.py Fighter input."""
    roster = []
    for m in band["members"]:
        if m["status"] not in ("active", "wounded"):
            continue
        horse = m.get("horse", {}) if isinstance(m.get("horse"), dict) else {}
        dogs = m.get("dogs", []) if isinstance(m.get("dogs"), list) else []
        if horse:
            ensure_animal_health(horse, "horse")
        for dog in dogs:
            ensure_animal_health(dog, "dog")
        mounted = bool(
            m.get("mounted", False)
            or horse.get("mounted", False)
            or horse.get("has_horse", False)
        )
        fighter = {
            "name": m["name"],
            "mig": m["mig"],
            "nim": m["nim"],
            "tou": m["tou"],
            "wit": m["wit"],
            "wil": m["wil"],
            "weapon_skill": m.get("weapon_skill", 1),
            "weapon_base": m.get("weapon_base", 6),
            "weapon_speed": m.get("weapon_speed", 3),
            "shield_skill": m.get("shield_skill", 0),
            "shield_def": m.get("shield_def", 0),
            "armor": m.get("armor", {loc: 0 for loc in
                          ["head", "torso", "right_arm", "left_arm",
                           "legs", "hands", "feet"]}),
            "mounted": mounted,
            "mount_condition": str(
                m.get("mount_condition")
                or horse.get("condition")
                or "steady"
            ),
            "rider_stability": int(
                m.get("rider_stability", horse.get("rider_stability", 70))
            ),
            "mount_fatigue": int(
                m.get("mount_fatigue", horse.get("fatigue", 0))
            ),
            "mount_breed": str(horse.get("breed", "")),
            "mount_mood": str(horse.get("mood", "calm")),
            "mount_traits": list(horse.get("traits", []) or []),
            "mount_tricks": list(horse.get("tricks", []) or []),
            "mount_stats": {
                key: int(horse.get(key, 0) or 0)
                for key in ("speed", "wind", "foot", "nerve", "load", "sense")
                if key in horse
            },
            "mount_max_hp": int(horse.get("max_hp", 0) or 0),
            "mount_hp": int(horse.get("hp", 0) or 0),
            "mount_wounds": list(horse.get("wounds", []) or []),
            "dog_companions": dogs,
        }
        roster.append(fighter)
    return roster


def snapshot(band: dict, filepath: str | None = None) -> dict:
    """Save band state to JSON. Returns the state dict."""
    state = deepcopy(band)
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        return {"saved": filepath, "members": len(state["members"])}
    return state


def load_band(filepath: str) -> dict:
    """Load band state from JSON or YAML file.

    For YAML files (band_state.yaml format), merges the top-level ``band:``
    dict with the ``members:`` list so callers see a flat structure.
    """
    if filepath.endswith(('.yaml', '.yml')):
        if _yaml is None:
            raise RuntimeError("PyYAML required to load .yaml band files.")
        with open(filepath, 'r', encoding='utf-8') as f:
            raw = _yaml.safe_load(f)
        # Merge band: and members: into a single flat dict
        merged = dict(raw.get('band', {}))
        if 'members' not in merged:
            merged['members'] = raw.get('members', [])
        # Ensure required keys for band_summary
        merged.setdefault('history', [])
        return merged
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def update_treasury(band: dict, silver_change: int, reason: str = "") -> dict:
    """Add or remove silver from treasury."""
    old = band["treasury_silver"]
    band["treasury_silver"] = max(0, old + silver_change)
    band["history"].append({
        "event": "treasury_change",
        "details": f"Treasury {old} → {band['treasury_silver']} silver. {reason}",
    })
    return {
        "previous": old,
        "change": silver_change,
        "current": band["treasury_silver"],
        "reason": reason,
    }


def update_morale(band: dict, change: int, reason: str = "") -> dict:
    """Adjust band morale."""
    old = band["morale"]
    band["morale"] = max(1, min(5, old + change))
    return {
        "previous": old,
        "change": change,
        "current": band["morale"],
        "reason": reason,
    }


def set_contract(band: dict, contract: dict | None) -> dict:
    """Set or clear the band's current contract."""
    old = band["current_contract"]
    band["current_contract"] = contract
    if contract:
        band["history"].append({
            "event": "contract_accepted",
            "details": f"Accepted contract: {contract.get('name', 'Unknown')}.",
        })
    else:
        band["history"].append({
            "event": "contract_completed",
            "details": "Contract completed or cancelled.",
        })
    return {"previous_contract": old, "current_contract": contract}


def advance_date(band: dict, days: int) -> dict:
    """Advance the band's calendar."""
    from calendar_sim import advance_time
    result = advance_time(band["year"], band["day_of_year"], days)
    band["year"] = result["to"]["year"]
    band["day_of_year"] = result["to"]["day_of_year"]
    return result


# ───────────────────────────────────────────────────────────
# Oath-breaker tracking (§9 reputation)
# ───────────────────────────────────────────────────────────

_DEFAULT_BAND_STATE = Path(__file__).resolve().parent.parent / "data" / "band_state.yaml"


def _load_band_state_yaml(path: str | None = None) -> dict:
    if _yaml is None:
        raise RuntimeError("PyYAML required for band_state.yaml commands.")
    p = path or str(_DEFAULT_BAND_STATE)
    with open(p, 'r', encoding='utf-8') as f:
        return _yaml.safe_load(f)


def _save_band_state_yaml(data: dict, path: str | None = None) -> None:
    if _yaml is None:
        raise RuntimeError("PyYAML required for band_state.yaml commands.")
    p = path or str(_DEFAULT_BAND_STATE)
    with open(p, 'w', encoding='utf-8') as f:
        _yaml.dump(data, f, allow_unicode=True, sort_keys=False)


def _find_member_in_state(data: dict, member_name: str) -> dict | None:
    needle = member_name.lower()
    for member in data.get('members', []):
        if member.get('name', '').lower() == needle:
            return member
    return None


def _personal_bounty_tier(amount: int) -> str | None:
    if amount <= 0:
        return None
    if amount < 40:
        return 'local_hunters'
    if amount < 150:
        return 'regional_hunters'
    if amount < 400:
        return 'professional_hunters'
    return 'open_season'


def cmd_oath_break(contract_id: str | None = None,
                   state_path: str | None = None,
                   dry_run: bool = False) -> dict:
    """Increment oath_break_count; flag band as oath_breaker at 3+."""
    data = _load_band_state_yaml(state_path)
    band = data['band']

    band.setdefault('oath_break_count', 0)
    band.setdefault('oath_breaker', False)

    band['oath_break_count'] += 1
    if band['oath_break_count'] >= 3:
        band['oath_breaker'] = True

    note = f"Oath broken (count {band['oath_break_count']})"
    if contract_id:
        note += f" — contract: {contract_id}"
    band.setdefault('history', []).append({"event": "oath_break", "details": note})

    if not dry_run:
        _save_band_state_yaml(data, state_path)
    return {
        "oath_break_count": band['oath_break_count'],
        "oath_breaker": band['oath_breaker'],
        "note": note,
        "dry_run": dry_run,
    }


def cmd_oath_clear(witness_rep: int, state_path: str | None = None,
                   dry_run: bool = False) -> dict:
    """Clear oath_breaker flag if witness_rep >= 2."""
    if witness_rep < 2:
        return {
            "cleared": False,
            "reason": f"witness_rep {witness_rep} < 2; oath_breaker status unchanged",
        }
    data = _load_band_state_yaml(state_path)
    band = data['band']
    was_set = band.get('oath_breaker', False)
    band['oath_breaker'] = False
    band.setdefault('history', []).append({
        "event": "oath_clear",
        "details": f"Oath-breaker status cleared (witness_rep={witness_rep})",
    })
    if not dry_run:
        _save_band_state_yaml(data, state_path)
    return {
        "cleared": True,
        "was_set": was_set,
        "oath_break_count": band.get('oath_break_count', 0),
        "dry_run": dry_run,
    }


def cmd_named_man_status(member_name: str,
                         state_path: str | None = None) -> dict:
    """Return personal bounty/crime status for a single named man."""
    data = _load_band_state_yaml(state_path)
    member = _find_member_in_state(data, member_name)
    if member is None:
        return {"error": f"Member '{member_name}' not found"}

    personal_bounty = int(member.get('personal_bounty_silver', 0))
    tier = member.get('personal_bounty_tier') or _personal_bounty_tier(personal_bounty)
    outlaw = bool(member.get('outlaw_status', False))
    crimes = member.get('personal_crimes', [])
    open_cases = [c for c in crimes if c.get('crime_type') != 'amnesty']

    return {
        "member": member.get('name', member_name),
        "rank": member.get('rank'),
        "personal_bounty_silver": personal_bounty,
        "personal_bounty_tier": tier,
        "outlaw_status": outlaw,
        "crime_count": len(open_cases),
        "latest_crime": open_cases[-1] if open_cases else None,
    }


def cmd_named_man_pardon_check(member_name: str,
                               witness_rep: int,
                               silver_paid: int,
                               state_path: str | None = None,
                               dry_run: bool = False) -> dict:
    """Resolve a pardon check and reduce personal bounty if successful."""
    data = _load_band_state_yaml(state_path)
    band = data.get('band', {})
    member = _find_member_in_state(data, member_name)
    if member is None:
        return {"error": f"Member '{member_name}' not found"}

    rank = member.get('rank', 'common')
    if rank not in {'named_man', 'captain'}:
        return {"error": f"{member.get('name', member_name)} is not a named man"}

    current = int(member.get('personal_bounty_silver', 0))
    if current <= 0:
        return {
            "member": member.get('name', member_name),
            "success": True,
            "reason": "No personal bounty to pardon",
            "old_bounty": 0,
            "new_bounty": 0,
            "outlaw_status": bool(member.get('outlaw_status', False)),
        }

    witness_score = max(0, witness_rep) * 20
    payment_score = min(max(0, silver_paid), current) * 2
    threshold = max(80, min(220, current))
    success = (witness_score + payment_score) >= threshold

    if not success:
        return {
            "member": member.get('name', member_name),
            "success": False,
            "reason": "Not enough witness reputation or silver paid",
            "witness_rep": witness_rep,
            "silver_paid": silver_paid,
            "required_score": threshold,
            "actual_score": witness_score + payment_score,
            "old_bounty": current,
            "new_bounty": current,
            "outlaw_status": bool(member.get('outlaw_status', False)),
        }

    old_bounty = current
    reduction = min(max(0, silver_paid), current)
    new_bounty = max(0, current - reduction)

    member['personal_bounty_silver'] = new_bounty
    member['personal_bounty_tier'] = _personal_bounty_tier(new_bounty)
    if new_bounty < 150:
        member['outlaw_status'] = False

    member.setdefault('personal_crimes', []).append({
        "day": band.get('day_of_year', 0),
        "settlement": "pardon_court",
        "crime_type": "amnesty",
        "severity": 0,
        "witnesses": witness_rep,
        "blood_price_silver": -reduction,
    })
    band.setdefault('history', []).append({
        "event": "named_man_pardon",
        "details": (
            f"Pardon granted for {member.get('name', member_name)}: "
            f"{old_bounty}s -> {new_bounty}s (rep={witness_rep}, paid={silver_paid})"
        ),
    })

    if not dry_run:
        _save_band_state_yaml(data, state_path)
    return {
        "member": member.get('name', member_name),
        "success": True,
        "witness_rep": witness_rep,
        "silver_paid": silver_paid,
        "old_bounty": old_bounty,
        "new_bounty": new_bounty,
        "personal_bounty_tier": member['personal_bounty_tier'],
        "outlaw_status": bool(member.get('outlaw_status', False)),
        "dry_run": dry_run,
    }


def main():
    parser = argparse.ArgumentParser(description="Iron Ledger Band Manager")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- create ---
    cre_p = subparsers.add_parser("create", help="Create a new band")
    cre_p.add_argument("--name", type=str, required=True)
    cre_p.add_argument("--captain", type=str, required=True)
    cre_p.add_argument("--archetype", type=str, default="standard",
                       choices=["tyrant", "standard", "fraternal", "kin_clan"])
    cre_p.add_argument("--output", type=str, help="Save to JSON file")
    cre_p.add_argument("--json", action="store_true")

    # --- summary ---
    sum_p = subparsers.add_parser("summary", help="Show band summary")
    sum_p.add_argument("--band-file", type=str, required=True)
    sum_p.add_argument("--json", action="store_true")

    # --- add-member ---
    add_p = subparsers.add_parser("add-member", help="Add a member")
    add_p.add_argument("--band-file", type=str, required=True)
    add_p.add_argument("--member", type=str, required=True, help="JSON member data")
    add_p.add_argument("--save", action="store_true", help="Save changes to file")
    add_p.add_argument("--json", action="store_true")

    # --- remove-member ---
    rem_p = subparsers.add_parser("remove-member", help="Remove a member")
    rem_p.add_argument("--band-file", type=str, required=True)
    rem_p.add_argument("--name", type=str, required=True)
    rem_p.add_argument("--reason", type=str, default="departed")
    rem_p.add_argument("--save", action="store_true")
    rem_p.add_argument("--json", action="store_true")

    # --- roster ---
    ros_p = subparsers.add_parser("roster", help="Get combat roster")
    ros_p.add_argument("--band-file", type=str, required=True)
    ros_p.add_argument("--json", action="store_true")

    # --- snapshot ---
    snap_p = subparsers.add_parser("snapshot", help="Save band state")
    snap_p.add_argument("--band-file", type=str, required=True)
    snap_p.add_argument("--output", type=str, help="Output file path")
    snap_p.add_argument("--json", action="store_true")

    # --- oath_break ---
    ob_p = subparsers.add_parser("oath_break", help="Record an oath break")
    ob_p.add_argument("--contract-id", type=str, default=None,
                      help="Optional contract reference")
    ob_p.add_argument("--state-file", type=str, default=None,
                      help="Path to band_state.yaml (default: ../data/band_state.yaml)")
    ob_p.add_argument("--json", action="store_true")

    # --- oath_clear ---
    oc_p = subparsers.add_parser("oath_clear", help="Clear oath-breaker status")
    oc_p.add_argument("--witness-rep", type=int, required=True,
                      help="Witness reputation (must be >= 2 to clear)")
    oc_p.add_argument("--state-file", type=str, default=None)
    oc_p.add_argument("--json", action="store_true")

    # --- named_man_status ---
    nms_p = subparsers.add_parser(
        "named_man_status",
        help="Show personal bounty/crime status for one named man",
    )
    nms_p.add_argument("--member", type=str, required=True)
    nms_p.add_argument("--state-file", type=str, default=None)
    nms_p.add_argument("--json", action="store_true")

    # --- named_man_pardon_check ---
    nmp_p = subparsers.add_parser(
        "named_man_pardon_check",
        help="Resolve a named-man pardon check and reduce personal bounty",
    )
    nmp_p.add_argument("--member", type=str, required=True)
    nmp_p.add_argument("--witness-rep", type=int, required=True)
    nmp_p.add_argument("--silver-paid", type=int, required=True)
    nmp_p.add_argument("--state-file", type=str, default=None)
    nmp_p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "create":
        band = create_band(args.name, args.captain,
                           getattr(args, "archetype", "standard"))
        if args.output and not args.dry_run:
            snapshot(band, args.output)
            print(f"Band saved to {args.output}")
        elif args.output and args.dry_run:
            print(f"[DRY RUN] Band not saved to {args.output}")
        if args.json or not args.output:
            print(json.dumps(band, indent=2))

    elif args.command == "summary":
        band = load_band(args.band_file)
        result = band_summary(band)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"=== {result['name']} ===")
            print(f"Captain: {result['captain']} | Archetype: {result['archetype']}")
            print(f"Reputation: {result['reputation']} | Morale: {result['morale']}")
            print(f"Treasury: {result['treasury_silver']} silver")
            print(f"Active: {result['active']} | Wounded: {result['wounded']} | "
                  f"Dead: {result['dead']} | Deserted: {result['deserted']}")
            print(f"Ranks: {result['rank_breakdown']}")
            print(f"Carry: {result['total_gear_weight_kg']}/{result['total_carry_capacity_kg']} kg")
            print(f"Weekly retainer: {result['weekly_retainer_copper']} copper")
            # Oath and atrocity fields (present in band_state.yaml)
            oath_count = band.get('oath_break_count', 0)
            oath_flag = band.get('oath_breaker', False)
            if oath_count or oath_flag:
                print(f"Oath breaks: {oath_count} | Oath-breaker: {oath_flag}")
            bounty = band.get('bounty_silver', 0)
            if bounty:
                print(f"Bounty: {bounty} silver ({band.get('bounty_tier', '?')})")

    elif args.command == "add-member":
        band = load_band(args.band_file)
        member_data = json.loads(args.member)
        result = add_member(band, member_data)
        if args.save and not args.dry_run:
            snapshot(band, args.band_file)
        result["dry_run"] = bool(args.dry_run)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Added {result['added']} ({result['rank']}). "
                      f"Band size: {result['band_size']}")

    elif args.command == "remove-member":
        band = load_band(args.band_file)
        result = remove_member(band, args.name, args.reason)
        if args.save and not args.dry_run:
            snapshot(band, args.band_file)
        result["dry_run"] = bool(args.dry_run)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Removed {result['removed']} ({result['reason']}). "
                      f"Band size: {result['band_size']}")

    elif args.command == "roster":
        band = load_band(args.band_file)
        roster = combat_roster(band)
        if args.json:
            print(json.dumps(roster, indent=2))
        else:
            for f in roster:
                print(f"  {f['name']}: MIG:{f['mig']} NIM:{f['nim']} "
                      f"WS:{f['weapon_skill']} WB:{f['weapon_base']}")

    elif args.command == "snapshot":
        band = load_band(args.band_file)
        outfile = args.output or args.band_file
        if args.dry_run:
            result = {"saved": outfile, "members": len(band.get("members", [])), "dry_run": True}
        else:
            result = snapshot(band, outfile)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Snapshot saved: {result['saved']} ({result['members']} members)")

    elif args.command == "oath_break":
        result = cmd_oath_break(
            contract_id=getattr(args, "contract_id", None),
            state_path=getattr(args, "state_file", None),
            dry_run=bool(args.dry_run),
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            flag = " ⚠ OATH-BREAKER FLAGGED" if result["oath_breaker"] else ""
            print(f"Oath break recorded: count {result['oath_break_count']}{flag}")

    elif args.command == "oath_clear":
        result = cmd_oath_clear(
            witness_rep=args.witness_rep,
            state_path=getattr(args, "state_file", None),
            dry_run=bool(args.dry_run),
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result["cleared"]:
                print(f"Oath-breaker status cleared (count remains "
                      f"{result['oath_break_count']}; witness_rep ok)")
            else:
                print(f"Not cleared: {result.get('reason', '')}")

    elif args.command == "named_man_status":
        result = cmd_named_man_status(
            member_name=args.member,
            state_path=getattr(args, "state_file", None),
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"{result['member']} ({result.get('rank', 'unknown')})")
                print(f"  Personal bounty: {result['personal_bounty_silver']} "
                      f"({result['personal_bounty_tier']})")
                print(f"  Outlaw: {result['outlaw_status']} | Crimes: {result['crime_count']}")

    elif args.command == "named_man_pardon_check":
        result = cmd_named_man_pardon_check(
            member_name=args.member,
            witness_rep=args.witness_rep,
            silver_paid=args.silver_paid,
            state_path=getattr(args, "state_file", None),
            dry_run=bool(args.dry_run),
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if "error" in result:
                print(f"Error: {result['error']}")
            elif result.get("success"):
                print(f"Pardon granted for {result['member']}: "
                      f"{result['old_bounty']}s -> {result['new_bounty']}s")
            else:
                print(f"Pardon denied for {result['member']}: {result.get('reason', '')}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
