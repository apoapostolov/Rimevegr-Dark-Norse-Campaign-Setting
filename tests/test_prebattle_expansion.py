"""Batch 10 tests — pre-battle expansion mechanics."""

from __future__ import annotations

import pytest

from combat_model import Fighter
from combat_sim import resolve_attack, run_duel, run_skirmish
from combat_types import ConditionType, Maneuver
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


def _fail_check(*args, **kwargs):
    return CheckResult(25, 90, ResultLevel.FAILURE, -65)


def _attacker_win(*args, **kwargs):
    a = CheckResult(95, 10, ResultLevel.SUCCESS, 20)
    d = CheckResult(25, 90, ResultLevel.FAILURE, -65)
    return OpposedResult(a, d, "attacker", 85)


class TestBatch10PreBattle:
    def test_grave_moan_applies_initiative_penalty(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_check", _fail_check)

        undead = _fighter(name="Moaner", traits=["grave_moan"])
        target = _fighter(name="Target")

        result = run_duel(undead, target, max_rounds=0)

        assert target.init_penalty == 5
        assert any(e["type"] == "grave_moan" for e in result.get("pre_battle", []))

    def test_commanding_presence_causes_fleeing(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_check", _fail_check)
        monkeypatch.setattr("combat_sim.random.randint", lambda a, b: 3)

        undead = _fighter(name="King", traits=["terrifying_presence", "commanding_presence"])
        target = _fighter(name="Target")

        result = run_duel(undead, target, max_rounds=0)

        assert target.has_condition(ConditionType.FLEEING)
        assert any("fleeing" in e.get("effect", "") for e in result.get("pre_battle", []) if e.get("type") == "terror_failed")

    def test_choking_darkness_applies_attack_penalty_timer(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_check", _fail_check)

        source = _fighter(name="Haug", traits=["choking_darkness"])
        target = _fighter(name="Target")

        run_duel(source, target, max_rounds=0)

        assert target.prebattle_attack_penalty == -20
        assert target.prebattle_attack_penalty_rounds == 2

    def test_sleep_weight_applies_nim_wit_penalties(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_check", _fail_check)
        monkeypatch.setattr("combat_sim.random.randint", lambda a, b: 4)

        source = _fighter(name="Mara", traits=["sleep_weight"])
        target = _fighter(name="Target")

        run_duel(source, target, max_rounds=0)

        assert target.prebattle_nim_penalty == -4
        assert target.prebattle_wit_penalty == -4
        assert target.prebattle_nim_penalty_rounds == 4
        assert target.prebattle_wit_penalty_rounds == 4

    def test_ground_tremor_applies_next_action_penalty(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("combat_sim.resolve_check", _fail_check)

        source = _fighter(name="Troll", traits=["ground_tremor"])
        target = _fighter(name="Target")

        run_duel(source, target, max_rounds=0)

        assert target.prebattle_attack_penalty == -5
        assert target.prebattle_attack_penalty_rounds == 1

    def test_temperature_plunge_reduces_toughness_once(self):
        source = _fighter(name="Wraith", traits=["temperature_plunge"], tou=7)
        target = _fighter(name="Target", tou=5)

        result = run_duel(source, target, max_rounds=0)

        assert source.tou == 6
        assert target.tou == 4
        assert any(e["type"] == "temperature_plunge" for e in result.get("pre_battle", []))

    def test_reality_warping_applies_attack_penalty_in_resolution(self, monkeypatch: pytest.MonkeyPatch):
        captured = {}

        def _capture(*args, **kwargs):
            captured["a_mods"] = args[2]
            return _attacker_win()

        monkeypatch.setattr("combat_sim.resolve_opposed", _capture)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: wb)

        attacker = _fighter(name="Attacker")
        defender = _fighter(name="Warp", reality_warping_rounds=3)

        resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, {})
        # Base attack mods should include at least the -10 reality warping penalty.
        assert captured["a_mods"] <= attacker.attack_chance_mods() - 10 + 2


class TestBatch9SkirmishHooks:
    def test_veteran_eye_targets_lowest_hp_enemy_in_skirmish(self):
        vet = _fighter(name="Vet", traits=["veteran_eye"])
        ally = _fighter(name="Ally")
        e1 = _fighter(name="EnemyHigh", hp=24, max_hp=24)
        e2 = _fighter(name="EnemyLow", hp=8, max_hp=24)

        run_skirmish([vet, ally], [e1, e2], max_rounds=0)
        assert vet.veteran_target == "EnemyLow"

    def test_rally_allies_recovers_stamina(self):
        leader = _fighter(name="Leader", traits=["rally_allies"], stamina=8, max_stamina=24)
        ally = _fighter(name="Ally", max_stamina=24)
        ally.stamina = 0
        enemy = _fighter(name="Enemy", stamina=8, max_stamina=24, hp=80, max_hp=80)

        start = ally.stamina
        run_skirmish([leader, ally], [enemy], max_rounds=1)
        assert ally.stamina > start
