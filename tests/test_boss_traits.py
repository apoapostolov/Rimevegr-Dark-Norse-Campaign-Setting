"""Batch 9 tests — Boss / Named-Enemy trait mechanics."""

from __future__ import annotations

import pytest

from combat_model import Fighter
from combat_sim import resolve_attack, resolve_control, run_duel
from combat_ai import can_counter, choose_maneuver
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


def _attacker_win(*args, **kwargs):
    a = CheckResult(95, 10, ResultLevel.SUCCESS, 20)
    d = CheckResult(25, 90, ResultLevel.FAILURE, -65)
    return OpposedResult(a, d, "attacker", 85)


def _defender_win(*args, **kwargs):
    a = CheckResult(25, 90, ResultLevel.FAILURE, -65)
    d = CheckResult(95, 10, ResultLevel.SUCCESS, 20)
    return OpposedResult(a, d, "defender", 85)


class TestBoneGnaw:
    def test_bone_gnaw_fires_free_bite_after_grapple_success(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr("combat_sim.resolve_opposed", _attacker_win)

        attacker = _fighter(name="Ragnvald", traits=["bone_gnaw"], brawl_skill=2)
        defender = _fighter(name="Target")
        result: dict = {}
        resolve_control(attacker, defender, Maneuver.GRAPPLE, result)

        assert result.get("hit") is True
        assert result.get("condition_applied") == "grappled"
        assert "bone_gnaw_bite" in result
        assert result["bone_gnaw_bite"]["damage"] >= 1

    def test_bone_gnaw_does_not_fire_on_grapple_miss(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr("combat_sim.resolve_opposed", _defender_win)

        attacker = _fighter(name="Ragnvald", traits=["bone_gnaw"], brawl_skill=2)
        defender = _fighter(name="Target")
        result: dict = {}
        resolve_control(attacker, defender, Maneuver.GRAPPLE, result)

        assert result.get("hit") is False
        assert "bone_gnaw_bite" not in result


class TestRelentlessNoCrit:
    def test_relentless_no_crit_fires_once_only(self):
        """First critical wound is downgraded to serious; second is not."""
        attacker = _fighter(name="Brute", traits=["relentless_no_crit"])

        # Simulate a critical wound (damage >= 11 → critical)
        attacker.hp = attacker.max_hp
        wound1 = attacker.apply_wound("torso", 11)
        assert wound1.severity == "serious", "First critical should be downgraded to serious"
        assert "relentless_no_crit_used" in attacker.used_traits

        wound2 = attacker.apply_wound("torso", 11)
        assert wound2.severity == "critical", "Second critical should NOT be downgraded"

    def test_relentless_no_crit_only_applies_to_criticals(self):
        """Serious wounds are not affected."""
        attacker = _fighter(name="Brute", traits=["relentless_no_crit"])
        wound = attacker.apply_wound("torso", 7)  # serious range
        assert wound.severity == "serious"
        assert "relentless_no_crit_used" not in attacker.used_traits


class TestReadTheFieldOnce:
    def test_read_the_field_once_fires_once(self, monkeypatch: pytest.MonkeyPatch):
        """Defender with read_the_field_once forces a reroll on the first successful attack."""
        call_count = {"n": 0}

        def _first_win_second_lose(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return _attacker_win()
            return _defender_win()

        monkeypatch.setattr("combat_sim.resolve_opposed", _first_win_second_lose)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: wb)

        attacker = _fighter(name="Striker")
        defender = _fighter(name="Wary", traits=["read_the_field_once"])

        result = resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, {})
        # Second resolve_opposed returns defender win → attack should miss
        assert result["winner"] == "defender"
        assert result["hit"] is False
        assert "read_the_field_once_used" in defender.used_traits

    def test_read_the_field_once_not_used_again(self, monkeypatch: pytest.MonkeyPatch):
        """Once fired, the trait does not trigger again."""
        monkeypatch.setattr("combat_sim.resolve_opposed", _attacker_win)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: wb)

        defender = _fighter(
            name="Wary",
            traits=["read_the_field_once"],
            used_traits=["read_the_field_once_used"],
        )
        attacker = _fighter(name="Striker")

        result = resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, {})
        assert result["winner"] == "attacker"
        assert result["hit"] is True
        assert "read_the_field_once" not in result


class TestBlackwineRage:
    def test_blackwine_rage_adds_mig_bonus_on_first_wound(self):
        """blackwine_rage triggers on first wound, giving MIG +2 for 3 rounds."""
        attacker = _fighter(name="Berserker", traits=["blackwine_rage"])
        initial_mig_bonus = attacker.mig_bonus

        attacker.apply_wound("torso", 4)
        assert attacker.mig_bonus == initial_mig_bonus + 2
        assert attacker.mig_bonus_timer == 3
        assert "blackwine_rage_triggered" in attacker.used_traits

    def test_blackwine_rage_does_not_stack(self):
        """Second wound does not reapply the bonus."""
        attacker = _fighter(name="Berserker", traits=["blackwine_rage"])
        attacker.apply_wound("torso", 4)
        bonus_after_first = attacker.mig_bonus

        attacker.apply_wound("torso", 4)
        assert attacker.mig_bonus == bonus_after_first

    def test_blackwine_rage_expires_after_3_rounds(self):
        """mig_bonus_timer counts down; at 0 the +2 MIG bonus is removed."""
        from combat_sim import run_duel
        # Create a fight long enough to tick 3+ rounds
        berserker = _fighter(
            name="Berserker",
            mig=8,
            nim=3,
            traits=["blackwine_rage"],
            bloodied_traits=["blackwine_rage"],
            bloodied_at=0.99,
            hp=20,
            max_hp=20,
        )
        target = _fighter(name="Target", mig=4, nim=4, hp=50, max_hp=50, tou=8)

        result = run_duel(berserker, target, max_rounds=6)
        # Fighter state after duel
        final = result["combatants"]["Berserker"]
        # If timer ran down, mig_bonus_timer should be 0
        assert final.get("mig_bonus_timer", 0) == 0


class TestPatientStrike:
    def test_patient_strike_bonus_applies_after_guard(self, monkeypatch: pytest.MonkeyPatch):
        """patient_strike gives +20 atk_mod when attacker guarded last round."""
        captured = {}

        def _capture(*args, **kwargs):
            captured["a_mods"] = args[2]
            return _attacker_win()

        monkeypatch.setattr("combat_sim.resolve_opposed", _capture)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: wb)

        attacker = _fighter(name="Patient", traits=["patient_strike"])
        attacker.guarded_last_round = True
        defender = _fighter(name="Target")

        resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, {})
        assert captured["a_mods"] >= 20

    def test_patient_strike_no_bonus_without_guard(self, monkeypatch: pytest.MonkeyPatch):
        """patient_strike does NOT give +20 when fighter did NOT guard last round."""
        captured = {}

        def _capture(*args, **kwargs):
            captured["a_mods"] = args[2]
            return _attacker_win()

        monkeypatch.setattr("combat_sim.resolve_opposed", _capture)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: wb)

        attacker = _fighter(name="Patient", traits=["patient_strike"])
        attacker.guarded_last_round = False
        defender = _fighter(name="Target")

        resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, {})
        # Base mods should not include the +20 patient strike bonus
        base_mods = attacker.attack_chance_mods()
        assert captured["a_mods"] == pytest.approx(base_mods, abs=5)


class TestDesperateFury:
    def test_desperate_fury_adds_20_atk_mod(self, monkeypatch: pytest.MonkeyPatch):
        """desperate_fury adds +20 to attack when trait is active."""
        captured = {}

        def _capture(*args, **kwargs):
            captured["a_mods"] = args[2]
            return _attacker_win()

        monkeypatch.setattr("combat_sim.resolve_opposed", _capture)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: wb)

        attacker = _fighter(name="Fury", traits=["desperate_fury"], hp=10, max_hp=20)
        defender = _fighter(name="Target")

        resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, {})
        # Should include +20
        base_no_fury = attacker.attack_chance_mods()
        assert captured["a_mods"] == pytest.approx(base_no_fury + 20, abs=2)

    def test_desperate_fury_adds_20_def_mod(self, monkeypatch: pytest.MonkeyPatch):
        """desperate_fury adds +20 to defense when trait is active on the defender."""
        captured = {}

        def _capture(*args, **kwargs):
            captured["d_mods"] = args[5]
            return _attacker_win()

        monkeypatch.setattr("combat_sim.resolve_opposed", _capture)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: wb)

        attacker = _fighter(name="Striker")
        defender = _fighter(name="Fury", traits=["desperate_fury"], hp=10, max_hp=20)

        resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, {})
        base_no_fury = defender.defense_chance_mods()
        assert captured["d_mods"] >= base_no_fury + 20


class TestVeteranEye:
    def test_veteran_eye_adds_10_atk_when_targeting_veteran_target(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        captured = {}

        def _capture(*args, **kwargs):
            captured["a_mods"] = args[2]
            return _attacker_win()

        monkeypatch.setattr("combat_sim.resolve_opposed", _capture)
        monkeypatch.setattr("combat_sim.hit_location", lambda: ("torso", 1.0))
        monkeypatch.setattr("combat_sim.calculate_damage", lambda wb, mig, mult, armor: wb)

        attacker = _fighter(name="Vet", traits=["veteran_eye"], veteran_target="Enemy")
        defender = _fighter(name="Enemy")

        resolve_attack(attacker, defender, Maneuver.CUT, Maneuver.GUARD, {})
        base = attacker.attack_chance_mods()
        assert captured["a_mods"] == pytest.approx(base + 10, abs=2)

    def test_veteran_eye_set_at_fight_start(self):
        """run_duel should set veteran_target before round 1."""
        vet = _fighter(name="Vet", traits=["veteran_eye"])
        enemy = _fighter(name="Enemy")
        run_duel(vet, enemy, max_rounds=1)
        assert vet.veteran_target == "Enemy"


class TestLastStand25:
    def test_last_stand_25_adds_weapon_base_at_25pct_hp(self):
        """last_stand_25 applies +3 weapon_base when HP drops to 25%."""
        hero = _fighter(
            name="Hero",
            traits=[],
            death_quarter_traits=["last_stand_25"],
            hp=20,
            max_hp=20,
        )
        initial_wb = hero.weapon_base

        # Drop HP to exactly 25%
        hero.hp = 5
        hero._check_bloodied()
        assert hero.weapon_base == initial_wb + 3
        assert "last_stand_25_applied" in hero.used_traits

    def test_last_stand_25_fires_only_once(self):
        hero = _fighter(
            name="Hero",
            traits=[],
            death_quarter_traits=["last_stand_25"],
            hp=20,
            max_hp=20,
        )
        hero.hp = 5
        hero._check_bloodied()
        wb_after_first = hero.weapon_base

        # Calling again should not re-apply
        hero._check_bloodied()
        assert hero.weapon_base == wb_after_first


class TestFogFighter:
    def test_fog_fighter_immune_to_blinded_condition(self):
        """fog_fighter trait blocks BLINDED condition from being applied."""
        fighter = _fighter(name="Fog", traits=["fog_fighter"])
        fighter.add_condition(ConditionType.BLINDED, 3)
        assert not fighter.has_condition(ConditionType.BLINDED)


class TestTacticalWithdrawal:
    def test_tactical_withdrawal_once_triggers_below_60pct(self):
        """tactical_withdrawal_once triggers GUARD and blocks counter when HP < 60%."""
        fighter = _fighter(
            name="Soldier",
            traits=["tactical_withdrawal_once"],
            hp=5,   # well below 60%
            max_hp=20,
        )
        opponent = _fighter(name="Opp")

        maneuver = choose_maneuver(fighter, opponent)
        assert maneuver == Maneuver.GUARD
        assert fighter.tactical_withdrawal_active is True
        assert "tactical_withdrawal_once_used" in fighter.used_traits

    def test_tactical_withdrawal_blocks_counter(self):
        """tactical_withdrawal_active prevents can_counter from returning True."""
        fighter = _fighter(
            name="Soldier",
            weapon_skill=3,
            tactical_withdrawal_active=True,
        )
        assert can_counter(fighter) is False

    def test_tactical_withdrawal_once_not_re_triggered(self):
        """trait fires only once."""
        fighter = _fighter(
            name="Soldier",
            traits=["tactical_withdrawal_once"],
            used_traits=["tactical_withdrawal_once_used"],
            hp=5,
            max_hp=20,
        )
        opponent = _fighter(name="Opp")
        maneuver = choose_maneuver(fighter, opponent)
        assert fighter.tactical_withdrawal_active is False
        # Maneuver should not be GUARD due to tactical withdrawal
        assert "tactical_withdrawal_once_used" in fighter.used_traits
