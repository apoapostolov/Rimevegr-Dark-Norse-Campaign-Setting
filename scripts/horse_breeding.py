#!/usr/bin/env python3
"""Iron Ledger — Horse breeding and valuation utilities.

This script implements the horse breeding rules added to
20_SIMULATION_RULES.md §4.13 and reads the canonical breed data from
data/horse_breeds.yaml.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

import yaml
from animal_care import ensure_animal_health


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
DEFAULT_BREED_FILE = DATA_DIR / "horse_breeds.yaml"
DEFAULT_BAND_FILE = DATA_DIR / "band_state.yaml"
DEFAULT_HERD_FILE = DATA_DIR / "horse_herds.yaml"

HORSE_STATS = ("speed", "wind", "foot", "nerve", "load", "sense")
HORSE_SEXES = ("mare", "stallion", "gelding")
DEFAULT_BREED = "rimefjord_pony"


def load_breed_data(path: Path = DEFAULT_BREED_FILE) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_band(path: Path = DEFAULT_BAND_FILE) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_herds(path: Path = DEFAULT_HERD_FILE) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def save_herds(payload: dict[str, Any], path: Path = DEFAULT_HERD_FILE) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True, width=120)


def _clamp_stat(value: int) -> int:
    return max(1, min(5, int(value)))


def _find_member_with_horse(band: dict[str, Any], member_name: str) -> dict[str, Any]:
    for member in band.get("members", []):
        if member.get("name", "").lower() == member_name.lower():
            horse = member.get("horse")
            if isinstance(horse, dict) and horse.get("has_horse"):
                return {"member_name": member.get("name"), "horse": horse}
            raise KeyError(f"Member '{member_name}' does not have a horse record.")
    raise KeyError(f"Member '{member_name}' not found in band file.")


def _find_herd(path: Path, herd_id: str) -> dict[str, Any]:
    herds = load_herds(path)
    for herd in herds.get("horse_herds", []):
        if herd.get("herd_id") == herd_id:
            return herd
    raise KeyError(f"Herd '{herd_id}' not found.")


def _coerce_parent(
    horse: dict[str, Any],
    breed_db: dict[str, Any],
    member_name: str | None = None,
) -> dict[str, Any]:
    breeds = breed_db["horse_breeds"]
    breed_id = str(horse.get("breed") or DEFAULT_BREED)
    template = breeds.get(breed_id)
    if template is None:
        raise KeyError(f"Unknown breed '{breed_id}'.")

    out = dict(horse)
    out["breed"] = breed_id
    out["display_breed"] = template["display_name"]
    out["member_name"] = member_name
    out.setdefault("name", "Unnamed Horse")
    out.setdefault("sex", "mare")
    out.setdefault("mood", "calm")
    out.setdefault("condition", "worked")
    out.setdefault("age_class", "prime")
    out.setdefault("bloodline_tags", list(template.get("common_bloodline_tags", []))[:2])
    out.setdefault("traits", list(template.get("common_traits", []))[:2])

    stats = template["stats"]
    for stat in HORSE_STATS:
        out[stat] = _clamp_stat(out.get(stat, stats[stat]))

    return out


def _find_named_horse(horses: list[dict[str, Any]], horse_name: str) -> dict[str, Any]:
    for horse in horses:
        if str(horse.get("name", "")).lower() == horse_name.lower():
            return horse
    raise KeyError(f"Horse '{horse_name}' not found.")


def _roll_foal_name(dam: dict[str, Any], sire: dict[str, Any], rng: random.Random) -> str:
    dam_bits = [bit for bit in str(dam.get("name", "Foal")).split("-") if bit]
    sire_bits = [bit for bit in str(sire.get("name", "Foal")).split("-") if bit]
    head = rng.choice(dam_bits or ["Foal"])
    tail = rng.choice(sire_bits or ["Born"])
    if head == tail:
        tail = "Step"
    return f"{head}-{tail}"


def resolve_parent(
    *,
    band_file: Path,
    parent_json: str | None,
    member_name: str | None,
    breed_db: dict[str, Any],
) -> dict[str, Any]:
    if parent_json:
        horse = json.loads(parent_json)
        return _coerce_parent(horse, breed_db)

    if member_name:
        band = load_band(band_file)
        found = _find_member_with_horse(band, member_name)
        return _coerce_parent(found["horse"], breed_db, member_name=found["member_name"])

    raise ValueError("Parent must be provided via --*-json or --*-member.")


def _pick_base_breed(dam: dict[str, Any], sire: dict[str, Any], rng: random.Random) -> str:
    if dam["breed"] == sire["breed"]:
        return dam["breed"]
    return rng.choice([dam["breed"], sire["breed"]])


def _strong_parent_stat(parent: dict[str, Any], rng: random.Random) -> str:
    ranked = sorted(HORSE_STATS, key=lambda stat: parent.get(stat, 1), reverse=True)
    top_value = parent.get(ranked[0], 1)
    top_stats = [stat for stat in ranked if parent.get(stat, 1) == top_value]
    return rng.choice(top_stats)


def _inherit_bloodline_tags(
    dam: dict[str, Any],
    sire: dict[str, Any],
    breed_template: dict[str, Any],
    rng: random.Random,
) -> list[str]:
    dam_tags = list(dam.get("bloodline_tags") or breed_template.get("common_bloodline_tags", []))
    sire_tags = list(sire.get("bloodline_tags") or breed_template.get("common_bloodline_tags", []))
    chosen = []
    if dam_tags:
        chosen.append(rng.choice(dam_tags))
    if sire_tags:
        chosen.append(rng.choice(sire_tags))
    return list(dict.fromkeys(chosen))


def _apply_quirk(foal: dict[str, Any], quirk_id: str, breed_db: dict[str, Any]) -> None:
    quirk = breed_db["foal_quirks"][quirk_id]
    for stat, delta in quirk.get("stat_mods", {}).items():
        foal[stat] = _clamp_stat(foal.get(stat, 1) + delta)
    for trait in quirk.get("add_traits", []):
        if trait not in foal["traits"]:
            foal["traits"].append(trait)


def estimate_horse_value(horse: dict[str, Any], breed_db: dict[str, Any]) -> int:
    breed = breed_db["horse_breeds"][horse["breed"]]
    bloodline_bonus_map = breed_db.get("bloodline_bonus_tags", {})

    stats_total = sum(_clamp_stat(horse.get(stat, 1)) for stat in HORSE_STATS)
    bloodline_bonus = sum(
        bloodline_bonus_map.get(tag, 0) for tag in horse.get("bloodline_tags", [])
    )

    condition_penalties = {
        "fresh": 0,
        "worked": 0,
        "winded": 2,
        "blown": 4,
        "hoof_sore": 5,
        "lame": 12,
        "chilled": 3,
        "hungry": 2,
        "dehydrated": 4,
        "skin_rubbed": 3,
        "panicked": 6,
        "wounded": 10,
    }
    vice_penalties = {
        "hot_blooded": 3,
        "crowd_sour": 4,
        "night_spook": 5,
        "bad_feeder": 3,
    }

    condition = str(horse.get("condition", "worked"))
    base_value = int(breed["base_value_silver"])
    tricks_bonus = len(horse.get("tricks", []))
    vice_penalty = sum(vice_penalties.get(trait, 0) for trait in horse.get("traits", []))
    value = base_value + ((stats_total - 18) * 2) + tricks_bonus + bloodline_bonus
    value -= condition_penalties.get(condition, 0)
    value -= vice_penalty
    return max(4, int(value))


def breed_foal(
    dam: dict[str, Any],
    sire: dict[str, Any],
    breed_db: dict[str, Any],
    *,
    seed: int | None = None,
) -> dict[str, Any]:
    rng = random.Random(seed)
    breed_id = _pick_base_breed(dam, sire, rng)
    breed_template = breed_db["horse_breeds"][breed_id]

    foal = {
        "name": _roll_foal_name(dam, sire, rng),
        "breed": breed_id,
        "display_breed": breed_template["display_name"],
        "sex": rng.choice(("mare", "stallion")),
        "age": 0,
        "age_class": "foal",
        "role": "breeding",
        "mood": "calm",
        "condition": "fresh",
        "bond_rider": None,
        "traits": list(dict.fromkeys(list(breed_template.get("common_traits", []))[:2])),
        "tricks": [],
        "bloodline_tags": _inherit_bloodline_tags(dam, sire, breed_template, rng),
        "inheritance": [],
    }

    for stat in HORSE_STATS:
        foal[stat] = _clamp_stat(breed_template["stats"][stat])

    for label, parent in (("dam", dam), ("sire", sire)):
        chosen = _strong_parent_stat(parent, rng)
        inherited = max(1, parent.get(chosen, 1) - rng.choice((0, 1)))
        foal[chosen] = _clamp_stat(max(foal[chosen], inherited))
        foal["inheritance"].append(
            f"{label} strong stat {chosen} -> {foal[chosen]}"
        )

    quirk_id = rng.choice(sorted(breed_db["foal_quirks"].keys()))
    foal["foal_quirk"] = quirk_id
    _apply_quirk(foal, quirk_id, breed_db)

    if "good_feet" in foal["bloodline_tags"] and "good_feet" not in foal["traits"]:
        foal["traits"].append("good_feet")
    if "deep_wind" in foal["bloodline_tags"] and "deep_wind" not in foal["traits"]:
        foal["traits"].append("deep_wind")

    foal["estimated_value_silver"] = estimate_horse_value(foal, breed_db)
    foal["age_seasons"] = 0
    ensure_animal_health(foal, "horse")
    return foal


def tick_herd_season(
    herd_id: str,
    *,
    herd_file: Path = DEFAULT_HERD_FILE,
    breed_db: dict[str, Any] | None = None,
    season_id: str = "Y312-S1",
    seed: int | None = None,
) -> dict[str, Any]:
    rng = random.Random(seed)
    breed_db = breed_db or load_breed_data()
    payload = load_herds(herd_file)

    target = None
    for herd in payload.get("horse_herds", []):
        if herd.get("herd_id") == herd_id:
            target = herd
            break
    if target is None:
        raise KeyError(f"Herd '{herd_id}' not found.")

    horses = target.setdefault("horses", [])
    breeding_history = target.setdefault("breeding_history", [])
    foals = target.setdefault("foals", [])
    produced = []
    promoted = []
    next_pairs = []

    for horse in horses:
        if isinstance(horse.get("age"), (int, float)):
            horse["age"] = int(horse["age"]) + 1
        ensure_animal_health(horse, "horse")

    aging_foals = []
    for foal in foals:
        foal["age_seasons"] = int(foal.get("age_seasons", 0)) + 1
        ensure_animal_health(foal, "horse")
        if foal["age_seasons"] >= 8:
            promoted_horse = dict(foal)
            promoted_horse["age"] = 2
            promoted_horse["age_class"] = "young"
            promoted_horse["role"] = "remount"
            horses.append(promoted_horse)
            promoted.append(promoted_horse["name"])
        else:
            aging_foals.append(foal)
    target["foals"] = aging_foals
    foals = target["foals"]

    for pair in target.get("breeding_pairs", []):
        if pair.get("target_season") != season_id:
            next_pairs.append(pair)
            continue
        dam = _coerce_parent(_find_named_horse(horses, str(pair["dam"])), breed_db)
        sire = _coerce_parent(_find_named_horse(horses, str(pair["sire"])), breed_db)
        foal_seed = rng.randint(1, 10_000_000)
        foal = breed_foal(dam, sire, breed_db, seed=foal_seed)
        foal["season_born"] = season_id
        foal["sire"] = sire["name"]
        foal["dam"] = dam["name"]
        produced.append(foal)
        foals.append(foal)
        breeding_history.append(
            {
                "season": season_id,
                "dam": dam["name"],
                "sire": sire["name"],
                "foal": foal["name"],
                "breed": foal["breed"],
                "estimated_value_silver": foal["estimated_value_silver"],
            }
        )

    target["breeding_pairs"] = next_pairs
    save_herds(payload, herd_file)
    return {
        "herd_id": herd_id,
        "season": season_id,
        "foals_born": len(produced),
        "foals": produced,
        "promoted_to_stock": promoted,
    }


def _json_out(payload: Any) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_foal(args: argparse.Namespace) -> None:
    breed_db = load_breed_data(Path(args.breed_file))
    dam = resolve_parent(
        band_file=Path(args.band_file),
        parent_json=args.dam_json,
        member_name=args.dam_member,
        breed_db=breed_db,
    )
    sire = resolve_parent(
        band_file=Path(args.band_file),
        parent_json=args.sire_json,
        member_name=args.sire_member,
        breed_db=breed_db,
    )
    foal = breed_foal(dam, sire, breed_db, seed=args.seed)
    if args.json:
        _json_out(foal)
        return
    print(f"Foal: {foal['name']}")
    print(f"Breed: {foal['display_breed']} ({foal['breed']})")
    print(f"Sex: {foal['sex']}")
    print(f"Quirk: {foal['foal_quirk']}")
    print(f"Stats: " + ", ".join(f"{s}={foal[s]}" for s in HORSE_STATS))
    print(f"Bloodline: {', '.join(foal['bloodline_tags']) or 'none'}")
    print(f"Traits: {', '.join(foal['traits']) or 'none'}")
    print(f"Estimated value: {foal['estimated_value_silver']} silver")


def cmd_value(args: argparse.Namespace) -> None:
    breed_db = load_breed_data(Path(args.breed_file))
    horse = resolve_parent(
        band_file=Path(args.band_file),
        parent_json=args.horse_json,
        member_name=args.member,
        breed_db=breed_db,
    )
    result = {
        "name": horse.get("name"),
        "breed": horse["breed"],
        "estimated_value_silver": estimate_horse_value(horse, breed_db),
    }
    _json_out(result) if args.json else print(
        f"{result['name']} ({result['breed']}): {result['estimated_value_silver']} silver"
    )


def cmd_tick_herd(args: argparse.Namespace) -> None:
    breed_db = load_breed_data(Path(args.breed_file))
    result = tick_herd_season(
        args.herd_id,
        herd_file=Path(args.herd_file),
        breed_db=breed_db,
        season_id=args.season_id,
        seed=args.seed,
    )
    if args.json:
        _json_out(result)
        return
    print(f"Herd: {result['herd_id']}")
    print(f"Season: {result['season']}")
    print(f"Foals born: {result['foals_born']}")
    for foal in result["foals"]:
        print(f"  - {foal['name']} ({foal['breed']}) {foal['estimated_value_silver']} silver")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Horse breeding and valuation")
    parser.add_argument(
        "--breed-file",
        default=str(DEFAULT_BREED_FILE),
        help="Path to horse_breeds.yaml",
    )
    parser.add_argument(
        "--band-file",
        default=str(DEFAULT_BAND_FILE),
        help="Path to band_state.yaml for member-based horse lookup",
    )
    parser.add_argument(
        "--herd-file",
        default=str(DEFAULT_HERD_FILE),
        help="Path to horse_herds.yaml for persistent herd operations",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    foal = sub.add_parser("foal", help="Generate a foal from two parent horses")
    foal.add_argument("--dam-member")
    foal.add_argument("--sire-member")
    foal.add_argument("--dam-json")
    foal.add_argument("--sire-json")
    foal.add_argument("--seed", type=int, default=None)
    foal.add_argument("--json", action="store_true")
    foal.set_defaults(func=cmd_foal)

    value = sub.add_parser("value", help="Estimate the value of a horse")
    value.add_argument("--member")
    value.add_argument("--horse-json")
    value.add_argument("--json", action="store_true")
    value.set_defaults(func=cmd_value)

    herd = sub.add_parser("tick-herd", help="Advance one persistent herd breeding season")
    herd.add_argument("--herd-id", required=True)
    herd.add_argument("--season-id", default="Y312-S1")
    herd.add_argument("--seed", type=int, default=None)
    herd.add_argument("--json", action="store_true")
    herd.set_defaults(func=cmd_tick_herd)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
