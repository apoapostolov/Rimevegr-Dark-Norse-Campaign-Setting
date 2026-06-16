#!/usr/bin/env python3
"""NPC combat bridge for Iron Ledger.

Converts NPC records into combat_sim fighters and runs duel/skirmish.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from engine import compute_max_hp, compute_max_stamina
from npc_manager import load_all_npcs
from combat_model import Fighter
from combat_sim import run_duel, run_skirmish
from animal_care import ensure_animal_health


COMBAT_SKILLS = {"Axes", "Blades", "Spears", "Bows", "Brawl", "Shields"}
_CAVALRY_BANDS = {
    "Voss's Black Axes",
    "The Three Wolves",
    "The Bone Pack",
    "The Hollow Hall",
    "The Iron Tide Remnant",
    "The Burnt Charter",
    "The Grey Shields",
}


def _extract_mount_state(npc: dict[str, Any]) -> dict[str, Any]:
    horse = npc.get("horse", {}) if isinstance(npc.get("horse"), dict) else {}
    if horse:
        ensure_animal_health(horse, "horse")
    dogs = list(npc.get("dogs", []) or [])
    for dog in dogs:
        ensure_animal_health(dog, "dog")
    explicit_mounted = (
        bool(npc.get("mounted", False))
        or bool(horse.get("mounted", False))
        or bool(horse.get("has_horse", False))
    )

    if explicit_mounted:
        mounted = True
    else:
        band_name = str(npc.get("band", "")).strip()
        role = str(npc.get("role", "")).strip().lower()
        mounted = band_name in _CAVALRY_BANDS and role in {"scout", "champion"}

    return {
        "mounted": bool(mounted),
        "mount_condition": str(
            npc.get("mount_condition")
            or horse.get("condition")
            or "steady"
        ),
        "rider_stability": int(
            npc.get("rider_stability", horse.get("rider_stability", 70))
        ),
        "mount_fatigue": int(
            npc.get("mount_fatigue", horse.get("fatigue", 0))
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


def _skill_rank(npc: dict[str, Any], names: set[str]) -> int:
    ranks = [s.get("rank", 0) for s in npc.get("skills", []) if s.get("name") in names]
    return max(ranks) if ranks else 0


def _to_fighter(npc: dict[str, Any]) -> Fighter:
    st = npc.get("stats", {})
    mig = int(st.get("MIG", 5))
    nim = int(st.get("NIM", 5))
    tou = int(st.get("TOU", 5))
    wit = int(st.get("WIT", 5))
    wil = int(st.get("WIL", 5))

    atk_skill = _skill_rank(npc, {"Axes", "Blades", "Spears", "Bows", "Brawl"})
    def_skill = _skill_rank(npc, {"Shields", "Brawl"})

    weapon_base = 6
    speed = 3
    weapon_type = "sword"
    gear = npc.get("gear", {})
    weapons = gear.get("weapons", []) if isinstance(gear, dict) else []
    if weapons:
        w = weapons[0]
        weapon_base = int(w.get("base_damage", 6))
        weapon_type = w.get("type", weapon_type)

    armor_map = {"head": 0, "torso": 0, "right_arm": 0, "left_arm": 0, "legs": 0, "hands": 0, "feet": 0}
    armor = gear.get("armor", {}) if isinstance(gear, dict) else {}
    if isinstance(armor, dict):
        armor_map["head"] = int(armor.get("head", 0) or 0)
        armor_map["torso"] = int(armor.get("torso", 0) or 0)
        arms = int(armor.get("arms", 0) or 0)
        armor_map["right_arm"] = arms
        armor_map["left_arm"] = arms
        armor_map["legs"] = int(armor.get("legs", 0) or 0)

    mount_state = _extract_mount_state(npc)

    return Fighter(
        name=npc.get("name", npc.get("id", "Unknown")),
        mig=mig,
        nim=nim,
        tou=tou,
        wit=wit,
        wil=wil,
        weapon_skill=max(1, atk_skill),
        weapon_base=weapon_base,
        weapon_speed=speed,
        weapon_type=weapon_type,
        shield_skill=max(0, def_skill),
        shield_def=2 if def_skill > 0 else 0,
        armor=armor_map,
        hp=compute_max_hp(tou, mig),
        max_hp=compute_max_hp(tou, mig),
        stamina=compute_max_stamina(tou, wil),
        max_stamina=compute_max_stamina(tou, wil),
        mounted=mount_state["mounted"],
        mount_condition=mount_state["mount_condition"],
        rider_stability=mount_state["rider_stability"],
        mount_fatigue=mount_state["mount_fatigue"],
        mount_breed=mount_state["mount_breed"],
        mount_mood=mount_state["mount_mood"],
        mount_traits=mount_state["mount_traits"],
        mount_tricks=mount_state["mount_tricks"],
        mount_stats=mount_state["mount_stats"],
        mount_max_hp=mount_state["mount_max_hp"],
        mount_hp=mount_state["mount_hp"],
        mount_wounds=mount_state["mount_wounds"],
        dog_companions=mount_state["dog_companions"],
    )


def _index_npcs() -> dict[str, dict[str, Any]]:
    idx: dict[str, dict[str, Any]] = {}
    for n in load_all_npcs():
        idx[n.get("id", "").lower()] = n
        idx[n.get("name", "").lower()] = n
        if n.get("call_name"):
            idx[str(n["call_name"]).lower()] = n
    return idx


def _resolve(name_or_id: str, idx: dict[str, dict[str, Any]]) -> dict[str, Any]:
    key = name_or_id.lower().strip()
    if key in idx:
        return idx[key]
    candidates = [v for k, v in idx.items() if key in k]
    if not candidates:
        raise SystemExit(f"NPC not found: {name_or_id}")
    # choose first deterministic by name
    candidates.sort(key=lambda x: x.get("name", ""))
    return candidates[0]


def _combat_capable(npc: dict[str, Any]) -> bool:
    return _skill_rank(npc, COMBAT_SKILLS) >= 1


def cmd_roster() -> list[dict[str, Any]]:
    return [n for n in load_all_npcs() if _combat_capable(n)]


def main() -> None:
    parser = argparse.ArgumentParser(description="NPC combat bridge")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("duel")
    p.add_argument("--attacker", required=True)
    p.add_argument("--defender", required=True)
    p.add_argument("--rounds", type=int, default=30)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("skirmish")
    p.add_argument("--side-a", required=True, help="Comma-separated NPC names/ids")
    p.add_argument("--side-b", required=True, help="Comma-separated NPC names/ids")
    p.add_argument("--rounds", type=int, default=30)
    p.add_argument(
        "--horses-allowed",
        action="store_true",
        help="Enable mounted combat logic for this skirmish (default: disabled).",
    )
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("roster")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("statblock")
    p.add_argument("--npc", required=True)
    p.add_argument("--json", action="store_true")

    args = parser.parse_args()
    idx = _index_npcs()

    if args.cmd == "roster":
        roster = cmd_roster()
        out = [
            {
                "id": n.get("id"),
                "name": n.get("name"),
                "call_name": n.get("call_name"),
                "category": n.get("_category"),
            }
            for n in roster
        ]
        if args.json:
            print(json.dumps(out, indent=2, ensure_ascii=False))
        else:
            for r in out:
                print(f"{r['id']}: {r['name']} ({r.get('category')})")
        return

    if args.cmd == "statblock":
        npc = _resolve(args.npc, idx)
        f = _to_fighter(npc)
        out = {
            "name": f.name,
            "mig": f.mig,
            "nim": f.nim,
            "tou": f.tou,
            "wit": f.wit,
            "wil": f.wil,
            "weapon_skill": f.weapon_skill,
            "weapon_base": f.weapon_base,
            "weapon_type": f.weapon_type,
            "shield_skill": f.shield_skill,
            "shield_def": f.shield_def,
            "hp": f.hp,
            "stamina": f.stamina,
        }
        if args.json:
            print(json.dumps(out, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(out, ensure_ascii=False))
        return

    if args.cmd == "duel":
        a = _to_fighter(_resolve(args.attacker, idx))
        d = _to_fighter(_resolve(args.defender, idx))
        result = run_duel(a, d, max_rounds=args.rounds)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Winner: {result['winner']} in {result['rounds']} rounds")
            print(json.dumps(result, ensure_ascii=False))
        return

    if args.cmd == "skirmish":
        side_a = [_to_fighter(_resolve(x.strip(), idx)) for x in args.side_a.split(",") if x.strip()]
        side_b = [_to_fighter(_resolve(x.strip(), idx)) for x in args.side_b.split(",") if x.strip()]
        result = run_skirmish(
            side_a,
            side_b,
            max_rounds=args.rounds,
            horses_allowed=bool(getattr(args, "horses_allowed", False)),
        )
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Winner: {result['winner']} in {result['rounds']} rounds")
            print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
