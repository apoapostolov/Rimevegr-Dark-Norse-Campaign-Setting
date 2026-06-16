#!/usr/bin/env python3
"""Iron Ledger — Dog breeding and valuation utilities."""

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
DEFAULT_BREED_FILE = DATA_DIR / "dog_breeds.yaml"
DEFAULT_BAND_FILE = DATA_DIR / "band_state.yaml"
DEFAULT_KENNEL_FILE = DATA_DIR / "dog_kennels.yaml"

DOG_STATS = ("nose", "speed", "grit", "bite", "sense", "voice")
DEFAULT_BREED = "fjord_hound"


def load_breed_data(path: Path = DEFAULT_BREED_FILE) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_band(path: Path = DEFAULT_BAND_FILE) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_kennels(path: Path = DEFAULT_KENNEL_FILE) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def save_kennels(payload: dict[str, Any], path: Path = DEFAULT_KENNEL_FILE) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True, width=120)


def _clamp_stat(value: int) -> int:
    return max(1, min(5, int(value)))


def _coerce_parent(dog: dict[str, Any], breed_db: dict[str, Any]) -> dict[str, Any]:
    breeds = breed_db["dog_breeds"]
    breed_id = str(dog.get("breed") or DEFAULT_BREED)
    template = breeds.get(breed_id)
    if template is None:
        raise KeyError(f"Unknown breed '{breed_id}'.")

    out = dict(dog)
    out["breed"] = breed_id
    out["display_breed"] = template["display_name"]
    out.setdefault("name", "Unnamed Dog")
    out.setdefault("sex", "dog")
    out.setdefault("mood", "calm")
    out.setdefault("condition", "worked")
    out.setdefault("age_class", "prime")
    out.setdefault("bloodline_tags", list(template.get("common_bloodline_tags", []))[:2])
    out.setdefault("traits", list(template.get("common_traits", []))[:2])

    stats = template["stats"]
    for stat in DOG_STATS:
        out[stat] = _clamp_stat(out.get(stat, stats[stat]))

    return out


def _find_named_dog(dogs: list[dict[str, Any]], dog_name: str) -> dict[str, Any]:
    for dog in dogs:
        if str(dog.get("name", "")).lower() == dog_name.lower():
            return dog
    raise KeyError(f"Dog '{dog_name}' not found.")


def _roll_pup_name(dam: dict[str, Any], sire: dict[str, Any], rng: random.Random) -> str:
    dam_bits = [bit for bit in str(dam.get("name", "Pup")).split("-") if bit]
    sire_bits = [bit for bit in str(sire.get("name", "Pup")).split("-") if bit]
    head = rng.choice(dam_bits or ["Pup"])
    tail = rng.choice(sire_bits or ["Born"])
    if head == tail:
        tail = "Bark"
    return f"{head}-{tail}"


def resolve_parent(parent_json: str, breed_db: dict[str, Any]) -> dict[str, Any]:
    return _coerce_parent(json.loads(parent_json), breed_db)


def _pick_base_breed(dam: dict[str, Any], sire: dict[str, Any], rng: random.Random) -> str:
    if dam["breed"] == sire["breed"]:
        return dam["breed"]
    return rng.choice([dam["breed"], sire["breed"]])


def _strong_parent_stat(parent: dict[str, Any], rng: random.Random) -> str:
    ranked = sorted(DOG_STATS, key=lambda stat: parent.get(stat, 1), reverse=True)
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


def _apply_quirk(pup: dict[str, Any], quirk_id: str, breed_db: dict[str, Any]) -> None:
    quirk = breed_db["puppy_quirks"][quirk_id]
    for stat, delta in quirk.get("stat_mods", {}).items():
        pup[stat] = _clamp_stat(pup.get(stat, 1) + delta)
    for trait in quirk.get("add_traits", []):
        if trait not in pup["traits"]:
            pup["traits"].append(trait)


def estimate_dog_value(dog: dict[str, Any], breed_db: dict[str, Any]) -> int:
    breed = breed_db["dog_breeds"][dog["breed"]]
    bloodline_bonus_map = breed_db.get("bloodline_bonus_tags", {})
    stats_total = sum(_clamp_stat(dog.get(stat, 1)) for stat in DOG_STATS)
    bloodline_bonus = sum(
        bloodline_bonus_map.get(tag, 0) for tag in dog.get("bloodline_tags", [])
    )
    condition_penalties = {
        "fresh": 0,
        "worked": 0,
        "winded": 1,
        "pawed_raw": 2,
        "hungry": 1,
        "chilled": 2,
        "mange": 3,
        "kennel_cough": 2,
        "panicked": 3,
        "wounded": 5,
    }
    vice_penalties = {
        "stranger_sour": 3,
        "kennel_sour": 2,
        "pack_hot": 4,
        "thin_coat": 2,
        "fight_picker": 2,
    }

    base_value = int(breed["base_value_silver"])
    tricks_bonus = len(dog.get("tricks", []))
    vice_penalty = sum(vice_penalties.get(trait, 0) for trait in dog.get("traits", []))
    value = base_value + ((stats_total - 18) * 1) + tricks_bonus + bloodline_bonus
    value -= condition_penalties.get(str(dog.get("condition", "worked")), 0)
    value -= vice_penalty
    return max(1, int(value))


def breed_pup(
    dam: dict[str, Any],
    sire: dict[str, Any],
    breed_db: dict[str, Any],
    *,
    seed: int | None = None,
) -> dict[str, Any]:
    rng = random.Random(seed)
    breed_id = _pick_base_breed(dam, sire, rng)
    breed_template = breed_db["dog_breeds"][breed_id]

    pup = {
        "name": _roll_pup_name(dam, sire, rng),
        "breed": breed_id,
        "display_breed": breed_template["display_name"],
        "sex": rng.choice(("bitch", "dog")),
        "age": 0,
        "age_class": "pup",
        "role": "breeding",
        "mood": "calm",
        "condition": "fresh",
        "bond_handler": None,
        "traits": list(dict.fromkeys(list(breed_template.get("common_traits", []))[:2])),
        "tricks": [],
        "bloodline_tags": _inherit_bloodline_tags(dam, sire, breed_template, rng),
        "inheritance": [],
    }

    for stat in DOG_STATS:
        pup[stat] = _clamp_stat(breed_template["stats"][stat])

    for label, parent in (("dam", dam), ("sire", sire)):
        chosen = _strong_parent_stat(parent, rng)
        inherited = max(1, parent.get(chosen, 1) - rng.choice((0, 1)))
        pup[chosen] = _clamp_stat(max(pup[chosen], inherited))
        pup["inheritance"].append(f"{label} strong stat {chosen} -> {pup[chosen]}")

    quirk_id = rng.choice(sorted(breed_db["puppy_quirks"].keys()))
    pup["puppy_quirk"] = quirk_id
    _apply_quirk(pup, quirk_id, breed_db)

    if "deep_nose" in pup["bloodline_tags"] and "deep_nose" not in pup["traits"]:
        pup["traits"].append("deep_nose")
    if "hard_bite" in pup["bloodline_tags"] and "hard_bite" not in pup["traits"]:
        pup["traits"].append("hard_bite")

    pup["estimated_value_silver"] = estimate_dog_value(pup, breed_db)
    pup["age_seasons"] = 0
    ensure_animal_health(pup, "dog")
    return pup


def tick_kennel_season(
    kennel_id: str,
    *,
    kennel_file: Path = DEFAULT_KENNEL_FILE,
    breed_db: dict[str, Any] | None = None,
    season_id: str = "Y312-S1",
    seed: int | None = None,
) -> dict[str, Any]:
    rng = random.Random(seed)
    breed_db = breed_db or load_breed_data()
    payload = load_kennels(kennel_file)

    target = None
    for kennel in payload.get("dog_kennels", []):
        if kennel.get("kennel_id") == kennel_id:
            target = kennel
            break
    if target is None:
        raise KeyError(f"Kennel '{kennel_id}' not found.")

    dogs = target.setdefault("dogs", [])
    breeding_history = target.setdefault("breeding_history", [])
    pups = target.setdefault("pups", [])
    produced = []
    promoted = []
    next_pairs = []

    for dog in dogs:
        if isinstance(dog.get("age"), (int, float)):
            dog["age"] = int(dog["age"]) + 1
        ensure_animal_health(dog, "dog")

    aging_pups = []
    for pup in pups:
        pup["age_seasons"] = int(pup.get("age_seasons", 0)) + 1
        ensure_animal_health(pup, "dog")
        if pup["age_seasons"] >= 4:
            promoted_dog = dict(pup)
            promoted_dog["age"] = 1
            promoted_dog["age_class"] = "young"
            promoted_dog["role"] = "working_stock"
            dogs.append(promoted_dog)
            promoted.append(promoted_dog["name"])
        else:
            aging_pups.append(pup)
    target["pups"] = aging_pups
    pups = target["pups"]

    for pair in target.get("breeding_pairs", []):
        if pair.get("target_season") != season_id:
            next_pairs.append(pair)
            continue
        dam = _coerce_parent(_find_named_dog(dogs, str(pair["dam"])), breed_db)
        sire = _coerce_parent(_find_named_dog(dogs, str(pair["sire"])), breed_db)
        pup_seed = rng.randint(1, 10_000_000)
        pup = breed_pup(dam, sire, breed_db, seed=pup_seed)
        pup["season_born"] = season_id
        pup["sire"] = sire["name"]
        pup["dam"] = dam["name"]
        produced.append(pup)
        pups.append(pup)
        breeding_history.append(
            {
                "season": season_id,
                "dam": dam["name"],
                "sire": sire["name"],
                "pup": pup["name"],
                "breed": pup["breed"],
                "estimated_value_silver": pup["estimated_value_silver"],
            }
        )

    target["breeding_pairs"] = next_pairs
    save_kennels(payload, kennel_file)
    return {
        "kennel_id": kennel_id,
        "season": season_id,
        "pups_born": len(produced),
        "pups": produced,
        "promoted_to_stock": promoted,
    }


def _json_out(payload: Any) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_pup(args: argparse.Namespace) -> None:
    breed_db = load_breed_data(Path(args.breed_file))
    dam = resolve_parent(args.dam_json, breed_db)
    sire = resolve_parent(args.sire_json, breed_db)
    pup = breed_pup(dam, sire, breed_db, seed=args.seed)
    if args.json:
        _json_out(pup)
        return
    print(f"Pup: {pup['name']}")
    print(f"Breed: {pup['display_breed']} ({pup['breed']})")
    print(f"Sex: {pup['sex']}")
    print(f"Quirk: {pup['puppy_quirk']}")
    print(f"Stats: " + ", ".join(f"{s}={pup[s]}" for s in DOG_STATS))
    print(f"Bloodline: {', '.join(pup['bloodline_tags']) or 'none'}")
    print(f"Traits: {', '.join(pup['traits']) or 'none'}")
    print(f"Estimated value: {pup['estimated_value_silver']} silver")


def cmd_value(args: argparse.Namespace) -> None:
    breed_db = load_breed_data(Path(args.breed_file))
    dog = resolve_parent(args.dog_json, breed_db)
    result = {
        "name": dog.get("name"),
        "breed": dog["breed"],
        "estimated_value_silver": estimate_dog_value(dog, breed_db),
    }
    _json_out(result) if args.json else print(
        f"{result['name']} ({result['breed']}): {result['estimated_value_silver']} silver"
    )


def cmd_tick_kennel(args: argparse.Namespace) -> None:
    breed_db = load_breed_data(Path(args.breed_file))
    result = tick_kennel_season(
        args.kennel_id,
        kennel_file=Path(args.kennel_file),
        breed_db=breed_db,
        season_id=args.season_id,
        seed=args.seed,
    )
    if args.json:
        _json_out(result)
        return
    print(f"Kennel: {result['kennel_id']}")
    print(f"Season: {result['season']}")
    print(f"Pups born: {result['pups_born']}")
    for pup in result["pups"]:
        print(f"  - {pup['name']} ({pup['breed']}) {pup['estimated_value_silver']} silver")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dog breeding and valuation")
    parser.add_argument(
        "--breed-file",
        default=str(DEFAULT_BREED_FILE),
        help="Path to dog_breeds.yaml",
    )
    parser.add_argument(
        "--band-file",
        default=str(DEFAULT_BAND_FILE),
        help="Reserved for future live dog lookups",
    )
    parser.add_argument(
        "--kennel-file",
        default=str(DEFAULT_KENNEL_FILE),
        help="Path to dog_kennels.yaml for persistent kennel operations",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    pup = sub.add_parser("pup", help="Generate a pup from two parent dogs")
    pup.add_argument("--dam-json", required=True)
    pup.add_argument("--sire-json", required=True)
    pup.add_argument("--seed", type=int, default=None)
    pup.add_argument("--json", action="store_true")
    pup.set_defaults(func=cmd_pup)

    value = sub.add_parser("value", help="Estimate the value of a dog")
    value.add_argument("--dog-json", required=True)
    value.add_argument("--json", action="store_true")
    value.set_defaults(func=cmd_value)

    kennel = sub.add_parser("tick-kennel", help="Advance one persistent kennel breeding season")
    kennel.add_argument("--kennel-id", required=True)
    kennel.add_argument("--season-id", default="Y312-S1")
    kennel.add_argument("--seed", type=int, default=None)
    kennel.add_argument("--json", action="store_true")
    kennel.set_defaults(func=cmd_tick_kennel)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
