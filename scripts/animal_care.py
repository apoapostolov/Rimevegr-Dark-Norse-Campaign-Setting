#!/usr/bin/env python3
"""Bounded horse and dog health, wounds, and recovery."""

from __future__ import annotations

import argparse
import json
from typing import Any


HORSE_STATS = ("speed", "wind", "foot", "nerve", "load", "sense")
DOG_STATS = ("nose", "speed", "grit", "bite", "sense", "voice")
ANIMAL_SEVERITY_ORDER = ("scratch", "light", "serious", "critical", "mortal")
ANIMAL_HEALING_DAYS = {
    "horse": {"scratch": 2, "light": 8, "serious": 24, "critical": 50, "mortal": 90},
    "dog": {"scratch": 1, "light": 5, "serious": 16, "critical": 32, "mortal": 60},
}
REST_MULT = {"stall_rest": 1.2, "kennel_rest": 1.2, "field_rest": 0.8, "working": 0.45}
SPECIES_SPEED = {"horse": 1.15, "dog": 1.3}


def species_for_animal(animal: dict[str, Any]) -> str:
    return "horse" if "wind" in animal or "load" in animal else "dog"


def compute_animal_max_hp(animal: dict[str, Any], species: str | None = None) -> int:
    species = species or species_for_animal(animal)
    stats = HORSE_STATS if species == "horse" else DOG_STATS
    base = 18 if species == "horse" else 10
    return base + (sum(int(animal.get(stat, 1) or 1) for stat in stats) * (2 if species == "horse" else 1))


def ensure_animal_health(animal: dict[str, Any], species: str | None = None) -> dict[str, Any]:
    species = species or species_for_animal(animal)
    animal.setdefault("species", species)
    animal.setdefault("max_hp", compute_animal_max_hp(animal, species))
    animal.setdefault("hp", animal["max_hp"])
    animal.setdefault("wounds", [])
    animal.setdefault("healing_days", 0.0)
    animal.setdefault("health_status", "sound")
    return animal


def wound_severity_from_damage(damage: int) -> str:
    if damage <= 2:
        return "scratch"
    if damage <= 5:
        return "light"
    if damage <= 8:
        return "serious"
    if damage <= 12:
        return "critical"
    return "mortal"


def apply_animal_wound(
    animal: dict[str, Any],
    *,
    damage: int,
    location: str,
    cause: str,
    severity: str | None = None,
) -> dict[str, Any]:
    ensure_animal_health(animal)
    severity = severity or wound_severity_from_damage(damage)
    wound = {
        "id": f"aw_{len(animal['wounds']) + 1:03d}",
        "location": location,
        "damage": int(damage),
        "severity": severity,
        "cause": cause,
        "treated": False,
        "healing_days": 0.0,
        "resolved": False,
    }
    animal["wounds"].append(wound)
    animal["hp"] = max(0, int(animal["hp"]) - int(damage))
    if animal["hp"] <= 0 or severity == "mortal":
        animal["health_status"] = "dead"
    elif severity in {"critical", "serious"}:
        animal["health_status"] = "laid_up"
    else:
        animal["health_status"] = "wounded"
    return wound


def treat_animal(animal: dict[str, Any], wound_id: str) -> dict[str, Any]:
    ensure_animal_health(animal)
    for wound in animal.get("wounds", []):
        if wound.get("id") == wound_id:
            wound["treated"] = True
            return wound
    raise KeyError(f"Wound '{wound_id}' not found.")


def heal_animal(animal: dict[str, Any], *, days: int, rest_quality: str = "field_rest") -> dict[str, Any]:
    species = species_for_animal(animal)
    ensure_animal_health(animal, species)
    effective_days = float(days) * REST_MULT.get(rest_quality, 0.8) * SPECIES_SPEED[species]
    animal["healing_days"] = float(animal.get("healing_days", 0.0)) + effective_days

    resolved = 0
    for wound in animal.get("wounds", []):
        if wound.get("resolved"):
            continue
        wound["healing_days"] = float(wound.get("healing_days", 0.0)) + effective_days
        threshold = ANIMAL_HEALING_DAYS[species][wound["severity"]]
        treatment_bonus = 1.2 if wound.get("treated") else 1.0
        if wound["healing_days"] >= threshold / treatment_bonus:
            wound["resolved"] = True
            resolved += 1

    active_wounds = [w for w in animal.get("wounds", []) if not w.get("resolved")]
    if animal["hp"] <= 0:
        animal["health_status"] = "dead"
    elif not active_wounds:
        animal["health_status"] = "sound"
        animal["hp"] = min(int(animal["max_hp"]), int(animal["hp"]) + max(1, int(effective_days // 3)))
    elif any(w["severity"] in {"critical", "mortal"} for w in active_wounds):
        animal["health_status"] = "laid_up"
    else:
        animal["health_status"] = "wounded"

    return {
        "species": species,
        "resolved_wounds": resolved,
        "health_status": animal["health_status"],
        "hp": animal["hp"],
        "active_wounds": len(active_wounds),
    }


def _json_out(payload: Any) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Animal wound and healing helper")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("status")
    p.add_argument("--animal-json", required=True)

    p = sub.add_parser("wound")
    p.add_argument("--animal-json", required=True)
    p.add_argument("--damage", required=True, type=int)
    p.add_argument("--location", required=True)
    p.add_argument("--cause", required=True)

    p = sub.add_parser("heal")
    p.add_argument("--animal-json", required=True)
    p.add_argument("--days", required=True, type=int)
    p.add_argument("--rest-quality", default="field_rest")

    args = parser.parse_args()
    animal = json.loads(args.animal_json)

    if args.command == "status":
        _json_out(ensure_animal_health(animal))
    elif args.command == "wound":
        apply_animal_wound(animal, damage=args.damage, location=args.location, cause=args.cause)
        _json_out(animal)
    elif args.command == "heal":
        heal_animal(animal, days=args.days, rest_quality=args.rest_quality)
        _json_out(animal)


if __name__ == "__main__":
    main()
