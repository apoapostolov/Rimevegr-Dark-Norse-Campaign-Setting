"""Batch 6 tests — Bloodied phase system and loader mapping."""

from __future__ import annotations

import pathlib

import pytest

from combat_model import Fighter
from combat_sim import resolve_attack
from combat_types import Maneuver
from engine import CheckResult, OpposedResult, ResultLevel
from bestiary_loader import load_enemy


DATA_DIR = pathlib.Path(__file__).parent.parent / "data" / "bestiary"


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


class TestBloodiedStateTransitions:
    def test_bloodied_false_before_threshold_true_after(self):
        f = _fighter(
            bloodied_traits=["relentless_advance"],
            bloodied_mig_bonus=1,
            bloodied_nim_bonus=1,
            bloodied_at=0.5,
        )

        # Keep above 50%
        f.apply_wound("torso", 2)
        assert f.bloodied_triggered is False

        # Force below 50%
        f.apply_wound("torso", 30)
        assert f.bloodied_triggered is True
        assert "relentless_advance" in f.traits
        assert f.mig_bonus == 1
        assert f.nim_bonus == 1

    def test_bloodied_traits_added_exactly_once(self):
        f = _fighter(bloodied_traits=["ancient_fury"], bloodied_mig_bonus=1)

        f.apply_wound("torso", 30)  # cross bloodied
        first_count = f.traits.count("ancient_fury")
        f.apply_wound("torso", 2)
        second_count = f.traits.count("ancient_fury")

        assert first_count == 1
        assert second_count == 1


class TestBloodiedCombatBonuses:
    def test_mig_bonus_piped_into_attack_attr(self, monkeypatch: pytest.MonkeyPatch):
        captured = {}

        def _capture_opposed(a_attr, a_skill, a_mods, d_attr, d_skill, d_mods, **kwargs):
            captured["a_attr"] = a_attr
            return _attacker_win_opposed()

        monkeypatch.setattr("combat_sim.resolve_opposed", _capture_opposed)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: wb)

        attacker = _fighter(name="A", mig=6, mig_bonus=2)
        defender = _fighter(name="D")

        resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, {})
        assert captured["a_attr"] == 8

    def test_ancient_fury_adds_d4_after_bloodied(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_opposed", _attacker_win_opposed)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: 5)
        monkeypatch.setattr("combat_sim.random.randint", lambda a, b: 4)

        attacker = _fighter(name="Ancient", traits=["ancient_fury"], bloodied_triggered=True)
        defender = _fighter(name="Target", tou=6)

        result = resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, {})
        assert result["final_damage"] == 9  # 5 base + 4 fury bonus
        assert result["ancient_fury_cold_bonus"] == 4


class TestLoaderBloodiedMapping:
    def test_loader_maps_ancient_fury_from_draugr(self):
        f = load_enemy("UND_DRAUGR_05", DATA_DIR)
        assert "ancient_fury" in f.bloodied_traits

    def test_loader_maps_last_stand_25_for_gunnar(self):
        f = load_enemy("BOS_RIVAL_05", DATA_DIR)
        assert "last_stand_25" in f.death_quarter_traits

    def test_blackwine_rage_uses_first_wound_threshold(self):
        f = load_enemy("BOS_RIVAL_01", DATA_DIR)
        assert "blackwine_rage" in f.bloodied_traits
        assert f.bloodied_at >= 0.95
