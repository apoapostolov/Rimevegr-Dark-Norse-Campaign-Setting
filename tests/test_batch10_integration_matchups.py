"""Batch 10 integration-style matchup tests."""

from __future__ import annotations

import pathlib
import random

import pytest

from bestiary_loader import load_enemy
from combat_model import Fighter
from combat_sim import resolve_attack, run_duel
from combat_types import Maneuver
from engine import CheckResult, OpposedResult, ResultLevel


DATA_DIR = pathlib.Path(__file__).parent.parent / "data" / "bestiary"


def _voss(*, fire: bool = False, iron: bool = True) -> Fighter:
    props = []
    if fire:
        props.append("fire")
    if iron:
        props.append("iron")
    return Fighter(
        name="Voss",
        mig=7,
        nim=6,
        tou=7,
        wit=6,
        wil=6,
        weapon_skill=3,
        weapon_base=7,
        weapon_speed=4,
        weapon_type="sword",
        weapon_properties=props,
        hp=36,
        max_hp=36,
    )


def _attacker_win(*args, **kwargs):
    a = CheckResult(95, 10, ResultLevel.SUCCESS, 20)
    d = CheckResult(25, 90, ResultLevel.FAILURE, -65)
    return OpposedResult(a, d, "attacker", 85)


class TestBatch10Matchups:
    def test_voss_vs_bear_01_runs(self):
        random.seed(42)
        voss = _voss()
        bear = load_enemy("ANI_BEAR_01", DATA_DIR)

        result = run_duel(voss, bear, max_rounds=20)

        assert result["type"] == "duel"
        assert 0 <= result["rounds"] <= 20
        assert "Voss" in result["combatants"]
        assert bear.name in result["combatants"]

    def test_wolf_pack_tactics_bonus_with_allies(self, monkeypatch: pytest.MonkeyPatch):
        wolf = load_enemy("ANI_WOLF_01", DATA_DIR)
        target = _voss()

        captured = {}

        def _capture(*args, **kwargs):
            captured["a_mods"] = args[2]
            return _attacker_win()

        monkeypatch.setattr("combat_sim.resolve_opposed", _capture)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: wb)

        wolf.allies_in_fight = 0
        resolve_attack(wolf, target, Maneuver.CUT, Maneuver.GUARD, {})
        base_mods = captured["a_mods"]

        wolf.allies_in_fight = 2
        resolve_attack(wolf, target, Maneuver.CUT, Maneuver.GUARD, {})

        assert captured["a_mods"] >= base_mods + 20

    def test_voss_vs_draugr_04_runs(self):
        random.seed(43)
        voss = _voss()
        draugr = load_enemy("UND_DRAUGR_04", DATA_DIR)

        result = run_duel(voss, draugr, max_rounds=20)

        assert result["type"] == "duel"
        assert "UND_DRAUGR_04" in draugr.id if hasattr(draugr, "id") else True
        assert result["rounds"] <= 20

    def test_incorporeal_requires_iron_or_fire(self, monkeypatch: pytest.MonkeyPatch):
        spirit = load_enemy("SUP_SPIRIT_01", DATA_DIR)
        plain = _voss(iron=False, fire=False)
        iron = _voss(iron=True, fire=False)

        monkeypatch.setattr("combat_sim.resolve_opposed", _attacker_win)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: wb)

        physical = resolve_attack(plain, spirit, Maneuver.CUT, Maneuver.GUARD, {})
        assert physical.get("final_damage", 0) == 0

        iron_hit = resolve_attack(iron, spirit, Maneuver.CUT, Maneuver.GUARD, {})
        assert iron_hit.get("final_damage", 0) > 0

    def test_voss_vs_sup_wild_01_sunlight_progresses(self):
        random.seed(44)
        voss = _voss()
        troll = load_enemy("SUP_WILD_01", DATA_DIR)
        voss.terrain = "daylight_open"
        troll.terrain = "daylight_open"

        result = run_duel(voss, troll, max_rounds=5)

        troll_state = result["combatants"][troll.name]
        assert troll_state.get("sunlight_rounds", 0) >= 1

    def test_voss_vs_sup_wild_02_temperature_plunge(self):
        voss = _voss()
        wraith = load_enemy("SUP_WILD_02", DATA_DIR)
        start_voss_tou = voss.tou
        start_wraith_tou = wraith.tou

        run_duel(voss, wraith, max_rounds=0)

        assert voss.tou == max(1, start_voss_tou - 1)
        assert wraith.tou == max(1, start_wraith_tou - 1)

    def test_voss_vs_bos_rival_02_runs(self):
        random.seed(45)
        voss = _voss()
        hrafn = load_enemy("BOS_RIVAL_02", DATA_DIR)

        result = run_duel(voss, hrafn, max_rounds=20)

        assert result["type"] == "duel"
        assert result["rounds"] <= 20
        assert "bone_gnaw" in hrafn.traits
        assert "relentless_no_crit" in hrafn.traits
