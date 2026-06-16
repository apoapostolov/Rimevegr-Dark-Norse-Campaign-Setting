#!/usr/bin/env python3
"""Shared horse and dog runtime helpers for Iron Ledger."""

from __future__ import annotations

from typing import Any


HORSE_TRAIT_CHARGE_MODS = {
    "charge_mass": {"attack_mod": 2, "bonus_damage": 2},
    "fast_break": {"attack_mod": 5},
    "long_stride": {"attack_mod": 2},
    "good_feet": {"tight_attack_mod": 4, "crowded_attack_mod": 2},
    "sure_step": {"tight_attack_mod": 5, "crowded_attack_mod": 1},
    "cliff_footed": {"tight_attack_mod": 5},
    "calm_mouth": {"stability": 8, "fear_resist": 8},
    "hard_to_catch": {"pursuit": 2},
    "cold_hardy": {"fatigue_delta": -2},
    "hot_blooded": {"crowded_attack_mod": -4, "stability": -5},
    "crowd_sour": {"crowded_attack_mod": -6, "stability": -6},
}

HORSE_MOOD_CHARGE_MODS = {
    "calm": {"charge_chance": 0.03, "stability": 3},
    "watchful": {"attack_mod": 1, "fear_resist": 4},
    "eager": {"charge_chance": 0.08, "attack_mod": 3, "stability": -2},
    "sour": {"charge_chance": -0.05, "stability": -4},
    "frayed": {"charge_chance": -0.12, "attack_mod": -3, "stability": -8},
    "panicked": {"charge_chance": -0.22, "attack_mod": -8, "stability": -15},
}

HORSE_TRICK_MODS = {
    "mount_charge": {"charge_chance": 0.08, "attack_mod": 2, "bonus_damage": 1},
    "stand_fire": {"fear_resist": 14},
    "sidepass": {"tight_attack_mod": 4},
    "pick_way": {"tight_attack_mod": 5},
    "come_to_whistle": {"recovery": 1},
    "stand_hobble": {"recovery": 1},
    "kneel_mount": {"stability": 3},
}

HORSE_CONDITION_MODS = {
    "steady": {"charge_chance": 0.0, "attack_mod": 0, "fatigue_delta": 0},
    "fresh": {"charge_chance": 0.05, "attack_mod": 2, "fatigue_delta": -2},
    "worked": {"charge_chance": 0.0, "attack_mod": 0, "fatigue_delta": 0},
    "winded": {"charge_chance": -0.12, "attack_mod": -3, "fatigue_delta": 4},
    "blown": {"charge_chance": -0.4, "attack_mod": -6, "fatigue_delta": 8},
    "hoof_sore": {"tight_attack_mod": -6, "fatigue_delta": 4},
    "lame": {"charge_chance": -0.5, "tight_attack_mod": -8, "fatigue_delta": 6},
    "wounded": {"charge_chance": -0.15, "attack_mod": -2, "fatigue_delta": 6},
    "panicked": {"charge_chance": -0.25, "attack_mod": -6, "fatigue_delta": 6},
}

DOG_ATTACK_TRAITS = {"hard_bite", "hold_fast", "gate_guard"}
DOG_ALERT_TRAITS = {"bark_alarm", "loud_warning", "weather_sense", "deep_nose", "homewise"}
DOG_TRACK_TRAITS = {"deep_nose", "winter_hunter", "careful_step", "marsh_footed", "quick_return"}
DOG_ATTACK_TRICKS = {"hold_fast", "guard_master", "heel_fire", "hold_thief"}
DOG_TRACK_TRICKS = {"trail_blood", "silent_circle", "find_master"}
DOG_ALERT_TRICKS = {"bark_alarm", "keep_gate"}


def _merge_mods(out: dict[str, int | float], mods: dict[str, int | float]) -> None:
    for key, value in mods.items():
        out[key] = out.get(key, 0) + value


def horse_charge_profile(fighter: Any) -> dict[str, int | float]:
    profile: dict[str, int | float] = {
        "charge_chance": 0.0,
        "attack_mod": 0,
        "tight_attack_mod": 0,
        "crowded_attack_mod": 0,
        "bonus_damage": 0,
        "fear_resist": 0,
        "stability": 0,
        "fatigue_delta": 0,
        "pursuit": 0,
        "recovery": 0,
    }
    for trait in getattr(fighter, "mount_traits", []) or []:
        _merge_mods(profile, HORSE_TRAIT_CHARGE_MODS.get(str(trait), {}))
    for trick in getattr(fighter, "mount_tricks", []) or []:
        _merge_mods(profile, HORSE_TRICK_MODS.get(str(trick), {}))
    _merge_mods(
        profile,
        HORSE_MOOD_CHARGE_MODS.get(str(getattr(fighter, "mount_mood", "calm")), {}),
    )
    _merge_mods(
        profile,
        HORSE_CONDITION_MODS.get(str(getattr(fighter, "mount_condition", "steady")), {}),
    )
    return profile


def dog_support_profile(dogs: list[dict[str, Any]] | None) -> dict[str, int]:
    profile = {
        "attack_mod": 0,
        "target_def_mod": 0,
        "awareness": 0,
        "morale": 0,
        "tracking_bonus": 0,
        "hazard_buffer": 0,
        "encounter_notice": 0,
    }
    for dog in dogs or []:
        if dog.get("health_status") in {"dead", "laid_up"}:
            continue
        traits = set(dog.get("traits", []) or [])
        tricks = set(dog.get("tricks", []) or [])
        role = str(dog.get("role", ""))

        if traits & DOG_ATTACK_TRAITS or tricks & DOG_ATTACK_TRICKS or role == "war_dog":
            profile["attack_mod"] += 4
            profile["target_def_mod"] -= 2
            profile["morale"] += 2
        if traits & DOG_ALERT_TRAITS or tricks & DOG_ALERT_TRICKS or role == "alarm_dog":
            profile["awareness"] += 1
            profile["encounter_notice"] += 12
        if traits & DOG_TRACK_TRAITS or tricks & DOG_TRACK_TRICKS or role == "tracker":
            profile["tracking_bonus"] += 10
            profile["hazard_buffer"] += 1
    return profile


def travel_companion_profile(
    horse: dict[str, Any] | None = None,
    dogs: list[dict[str, Any]] | None = None,
    *,
    terrain: str = "",
    weather: str = "",
) -> dict[str, int]:
    dog_profile = dog_support_profile(dogs)
    profile = {
        "speed_bonus_km": 0,
        "hazard_buffer": dog_profile["hazard_buffer"],
        "tracking_bonus": dog_profile["tracking_bonus"],
        "encounter_notice": dog_profile["encounter_notice"],
    }
    horse_traits = set((horse or {}).get("traits", []) or [])
    horse_tricks = set((horse or {}).get("tricks", []) or [])
    if horse and horse.get("has_horse", True):
        if horse_traits & {"good_feet", "sure_step", "cliff_footed"}:
            if terrain in {"mountain", "moors", "ice", "river", "fjord"}:
                profile["hazard_buffer"] += 1
        if horse_traits & {"fast_break", "long_stride"}:
            profile["speed_bonus_km"] += 2
        if "cold_hardy" in horse_traits and weather in {"driving_snow", "rime_storm", "rime_fog"}:
            profile["speed_bonus_km"] += 1
        if "pick_way" in horse_tricks or "sidepass" in horse_tricks:
            profile["hazard_buffer"] += 1
    return profile
