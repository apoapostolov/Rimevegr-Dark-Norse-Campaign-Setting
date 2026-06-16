from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))

from animal_care import apply_animal_wound, ensure_animal_health, heal_animal


def test_horse_wound_and_heal_cycle():
    horse = {"name": "Ice-Mane", "speed": 2, "wind": 4, "foot": 4, "nerve": 4, "load": 3, "sense": 4}
    ensure_animal_health(horse, "horse")

    wound = apply_animal_wound(horse, damage=6, location="torso", cause="spear brace")
    assert wound["severity"] == "serious"
    assert horse["health_status"] == "laid_up"

    result = heal_animal(horse, days=30, rest_quality="stall_rest")
    assert result["health_status"] in {"sound", "wounded"}


def test_dog_heals_faster_than_horse():
    dog = {"name": "Crow-Fang", "nose": 5, "speed": 4, "grit": 5, "bite": 5, "sense": 3, "voice": 2}
    horse = {"name": "Ash-Crow", "speed": 2, "wind": 4, "foot": 5, "nerve": 4, "load": 3, "sense": 4}
    ensure_animal_health(dog, "dog")
    ensure_animal_health(horse, "horse")
    apply_animal_wound(dog, damage=5, location="torso", cause="melee")
    apply_animal_wound(horse, damage=5, location="torso", cause="melee")

    dog_result = heal_animal(dog, days=8, rest_quality="kennel_rest")
    horse_result = heal_animal(horse, days=8, rest_quality="stall_rest")

    assert dog_result["resolved_wounds"] >= horse_result["resolved_wounds"]
