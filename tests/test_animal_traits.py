"""Batch 5 tests — Animal trait mechanics in combat_sim/combat_model."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from combat_model import Fighter
from combat_sim import resolve_attack
from combat_types import ConditionType, Maneuver
from engine import CheckResult, OpposedResult, ResultLevel


def _fighter(**kwargs) -> Fighter:
    base = dict(
        name="F",
        mig=6,
        nim=5,
        tou=6,
        wit=4,
        wil=4,
        weapon_skill=2,
        weapon_base=6,
        weapon_speed=3,
        weapon_type="sword",
    )
    base.update(kwargs)
    return Fighter(**base)


def _attacker_win_opposed(*args, **kwargs):
    a = CheckResult(95, 10, ResultLevel.SUCCESS, 20)
    d = CheckResult(25, 90, ResultLevel.FAILURE, -65)
    return OpposedResult(a, d, "attacker", 85)


class TestTerrifyingCharge:
    def test_first_attack_gets_plus2_only_once(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_opposed", _attacker_win_opposed)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: wb)

        attacker = _fighter(name="Bear", traits=["terrifying_charge"], weapon_base=6)
        defender = _fighter(name="Target", tou=5)

        r1 = resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, {})
        r2 = resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, {})

        assert r1["final_damage"] == 8  # weapon_base(6) + terrifying_charge(+2)
        assert r2["final_damage"] == 6  # bonus consumed


class TestPackTactics:
    def test_pack_tactics_adds_plus30_attack_mod(self, monkeypatch: pytest.MonkeyPatch):
        captured = {}

        def _capture_opposed(a_attr, a_skill, a_mods, d_attr, d_skill, d_mods, **kwargs):
            captured["a_mods"] = a_mods
            return _attacker_win_opposed()

        monkeypatch.setattr("combat_sim.resolve_opposed", _capture_opposed)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: wb)

        attacker = _fighter(name="Wolf", traits=["pack_tactics"], allies_in_fight=3)
        defender = _fighter(name="Target")

        resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, {})
        assert captured["a_mods"] >= 30


class TestTerritorialRageAndStarvationFrenzy:
    def test_territorial_rage_activates_below_half_hp(self):
        bear = _fighter(name="Cave Bear", traits=["territorial_rage"], tou=8, mig=8)

        # Above 50% HP
        bear.apply_wound("torso", 2)
        assert bear.hp > bear.max_hp * 0.5
        assert bear.territorial_rage_active is False

        # Cross below 50%
        bear.apply_wound("torso", 20)
        assert bear.hp <= bear.max_hp * 0.5
        assert bear.territorial_rage_active is True

    def test_starvation_frenzy_ignores_first_wound_only(self):
        wolf = _fighter(name="Starved Wolf", traits=["starvation_frenzy"], tou=5, mig=5)

        wolf.apply_wound("torso", 6)  # serious wound
        assert len(wolf.wounds) == 1
        assert wolf.wound_penalty == 0

        wolf.apply_wound("torso", 6)  # second serious wound
        assert len(wolf.wounds) == 2
        assert wolf.wound_penalty > 0


class TestHamstringCondition:
    def test_hamstring_applies_on_critical_or_mortal(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_opposed", _attacker_win_opposed)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: 12)  # critical range

        attacker = _fighter(name="Wolf", traits=["hamstring"])
        defender = _fighter(name="Target", tou=8)

        resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, {})
        assert defender.has_condition(ConditionType.HAMSTRUNG)
