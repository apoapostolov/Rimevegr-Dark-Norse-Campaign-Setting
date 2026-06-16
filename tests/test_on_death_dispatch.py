"""Batch 7 tests — on-death dispatch effects."""

from __future__ import annotations

import pytest

from combat_model import Fighter
from combat_sim import dispatch_death_effects
from combat_types import ConditionType
from engine import CheckResult, OpposedResult, ResultLevel


def _fighter(**kwargs) -> Fighter:
    base = dict(
        name="F",
        mig=6,
        nim=5,
        tou=6,
        wit=5,
        wil=5,
        weapon_skill=2,
        weapon_base=6,
        weapon_speed=3,
        weapon_type="sword",
        hp=24,
        max_hp=24,
    )
    base.update(kwargs)
    return Fighter(**base)


def _success_check(*args, **kwargs):
    return CheckResult(10, 80, ResultLevel.SUCCESS, 70)


def _failure_check(*args, **kwargs):
    return CheckResult(90, 20, ResultLevel.FAILURE, -70)


def _attacker_win(*args, **kwargs):
    a = CheckResult(95, 10, ResultLevel.SUCCESS, 20)
    d = CheckResult(25, 90, ResultLevel.FAILURE, -65)
    return OpposedResult(a, d, "attacker", 85)


class TestOnDeathDispatch:
    def test_corpse_burst_4_2_damage_and_halve(self, monkeypatch: pytest.MonkeyPatch):
        dead = _fighter(name="Bloated", hp=0, max_hp=24, is_down=True, death_effects=["corpse_burst_4_2"])
        fast = _fighter(name="Fast", tou=8)
        weak = _fighter(name="Weak", tou=2)

        checks = iter([_success_check(), _failure_check()])
        monkeypatch.setattr("combat_sim.resolve_check", lambda *a, **k: next(checks))

        events = []
        dispatch_death_effects(dead, [dead, fast, weak], [dead], events)

        burst = [e for e in events if e.get("effect") == "corpse_burst_4_2"][0]
        by_target = {x["target"]: x for x in burst["hits"]}

        assert by_target["Fast"]["damage"] == 2
        assert by_target["Fast"]["halved"] is True
        assert by_target["Weak"]["damage"] == 4
        assert weak.hp == weak.max_hp - 4

    def test_weapon_throw_on_death_fires_final_attack(self, monkeypatch: pytest.MonkeyPatch):
        dead = _fighter(name="Thrown", hp=0, max_hp=24, is_down=True, death_effects=["weapon_throw_on_death"])
        target = _fighter(name="Target")

        monkeypatch.setattr("combat_sim.resolve_opposed", _attacker_win)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: wb)

        events = []
        dispatch_death_effects(dead, [dead, target], [dead], events)

        throw = [e for e in events if e.get("effect") == "weapon_throw_on_death"][0]
        assert throw["is_death_throw"] is True
        assert throw["attack_roll"] is not None
        assert throw["hit"] is True
        assert throw["defender"] == "Target"

    def test_multiple_death_effects_fire(self, monkeypatch: pytest.MonkeyPatch):
        dead = _fighter(
            name="Ancient",
            hp=0,
            max_hp=24,
            is_down=True,
            death_effects=["death_rattle", "nauseating_burst"],
        )
        survivor = _fighter(name="Survivor")

        monkeypatch.setattr("combat_sim.resolve_check", _failure_check)

        events = []
        dispatch_death_effects(dead, [dead, survivor], [dead], events)

        effects = {e["effect"] for e in events}
        assert "death_rattle" in effects
        assert "nauseating_burst" in effects
        assert survivor.has_condition(ConditionType.WINDED)
