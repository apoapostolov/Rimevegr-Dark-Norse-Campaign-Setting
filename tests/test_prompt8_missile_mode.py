"""Prompt 8 tests — missile combat, volleys, suppression, and ammo discipline."""

from __future__ import annotations

import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))

from combat_model import Fighter
from combat_sim import run_skirmish


def _fighter(name: str, **kwargs) -> Fighter:
    base = dict(
        name=name,
        mig=5,
        nim=5,
        tou=5,
        wit=5,
        wil=5,
        weapon_skill=2,
        weapon_base=6,
        weapon_speed=3,
        weapon_type="sword",
        max_hp=45,
        hp=45,
        formation="loose_line",
        cohesion_score=70,
        morale_score=70,
        ammo_max=0,
        ammo_current=0,
    )
    base.update(kwargs)
    return Fighter(**base)


def _team(prefix: str, n: int, **kwargs) -> list[Fighter]:
    return [_fighter(f"{prefix}{i}", **kwargs) for i in range(n)]


def _missile_damage(round_log: list[dict]) -> int:
    total = 0
    for rnd in round_log:
        for act in rnd.get("actions", []):
            if act.get("type") == "missile_attack" and act.get("hit"):
                total += int(act.get("final_damage", 0))
    return total


def test_volley_fire_applies_suppression_pressure():
    random.seed(81)
    archers = _team(
        "A",
        2,
        weapon_type="bow",
        weapon_skill=4,
        wit=7,
        ammo_max=8,
        ammo_current=8,
        missile_mode="volley",
    )
    defenders = _team("B", 6, weapon_type="spear", formation="loose_line")

    result = run_skirmish(archers, defenders, max_rounds=1, combat_mode="skirmish")
    missile_events = [
        a for a in result["round_log"][0]["actions"]
        if a.get("type") == "missile_attack" and a.get("mode") == "volley"
    ]

    assert missile_events, "Expected volley missile events in round 1"
    assert any(a.get("suppressed") for a in missile_events), "Expected suppression from volley pressure"


def test_shield_wall_front_reduces_missile_damage_vs_exposed_line():
    random.seed(82)
    shooters_1 = _team(
        "A",
        3,
        weapon_type="bow",
        weapon_skill=4,
        wit=7,
        ammo_max=10,
        ammo_current=10,
        missile_mode="volley",
    )
    shield_front = _team("B", 6, weapon_type="spear", formation="shield_wall", rout_state="steady")

    res_shield = run_skirmish(shooters_1, shield_front, max_rounds=1, combat_mode="skirmish")
    dmg_shield = _missile_damage(res_shield["round_log"])

    random.seed(82)
    shooters_2 = _team(
        "A",
        3,
        weapon_type="bow",
        weapon_skill=4,
        wit=7,
        ammo_max=10,
        ammo_current=10,
        missile_mode="volley",
    )
    exposed = _team("B", 6, weapon_type="sword", formation="loose_line", frontage_pressure=80, rout_state="wavering")

    res_exposed = run_skirmish(shooters_2, exposed, max_rounds=1, combat_mode="skirmish")
    dmg_exposed = _missile_damage(res_exposed["round_log"])

    assert dmg_exposed > dmg_shield, (
        f"Expected exposed line to take more missile damage; shield={dmg_shield}, exposed={dmg_exposed}"
    )


def test_ammo_depletion_changes_archer_behavior():
    random.seed(83)
    archer = _fighter(
        "A0",
        weapon_type="bow",
        weapon_skill=4,
        wit=7,
        ammo_max=2,
        ammo_current=2,
        missile_mode="aimed",
        resupplies_used=1,
    )
    defenders = _team("B", 3, weapon_type="spear")

    result = run_skirmish([archer], defenders, max_rounds=3, combat_mode="skirmish")

    all_actions = [a for r in result["round_log"] for a in r.get("actions", [])]
    empty_events = [a for a in all_actions if a.get("type") == "missile_ammo_empty" and a.get("attacker") == "A0"]

    assert empty_events, "Expected ammo-empty event after limited ammunition is spent"
    assert result["side_a"]["A0"]["ammo_current"] == 0


def test_bad_weather_reduces_missile_hit_quality():
    random.seed(84)
    fair_archers = _team(
        "A",
        2,
        weapon_type="bow",
        weapon_skill=4,
        wit=7,
        ammo_max=8,
        ammo_current=8,
        missile_mode="aimed",
        terrain="open",
    )
    defenders_1 = _team("B", 4, weapon_type="spear")
    fair = run_skirmish(fair_archers, defenders_1, max_rounds=1, combat_mode="skirmish")

    random.seed(84)
    storm_archers = _team(
        "A",
        2,
        weapon_type="bow",
        weapon_skill=4,
        wit=7,
        ammo_max=8,
        ammo_current=8,
        missile_mode="aimed",
        terrain="blizzard",
    )
    defenders_2 = _team("B", 4, weapon_type="spear")
    storm = run_skirmish(storm_archers, defenders_2, max_rounds=1, combat_mode="skirmish")

    fair_hits = sum(1 for a in fair["round_log"][0]["actions"] if a.get("type") == "missile_attack" and a.get("hit"))
    storm_hits = sum(1 for a in storm["round_log"][0]["actions"] if a.get("type") == "missile_attack" and a.get("hit"))

    assert storm_hits <= fair_hits, (
        f"Expected blizzard to reduce ranged hit quality; fair={fair_hits}, storm={storm_hits}"
    )
