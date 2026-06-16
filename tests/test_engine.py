"""test_engine.py — Tests for the core resolution engine (engine.py)."""
import random

import pytest

from engine import (
    ResultLevel,
    CheckResult,
    OpposedResult,
    compute_success_chance,
    resolve_check,
    resolve_opposed,
    roll_d100,
    roll_dice,
    roll_sum,
    hit_location,
    calculate_damage,
    wound_severity,
    compute_max_hp,
    compute_max_stamina,
    compute_stamina_recovery,
    compute_carry_limit,
    compute_march_speed,
    compute_foraging,
)


# ── compute_success_chance ─────────────────────────────────────────────────

class TestComputeSuccessChance:
    def test_formula(self):
        # (6 * 5) + (3 * 10) + 15 = 30 + 30 + 15 = 75
        assert compute_success_chance(6, 3, 0) == 75

    def test_min_clamp(self):
        assert compute_success_chance(1, 0, -100) == 5

    def test_max_clamp(self):
        assert compute_success_chance(10, 10, 100) == 95

    def test_modifier_adds(self):
        base = compute_success_chance(5, 2, 0)
        boosted = compute_success_chance(5, 2, 10)
        assert boosted == base + 10

    def test_zero_attr_zero_skill(self):
        # (0 * 5) + (0 * 10) + 15 = 15
        assert compute_success_chance(0, 0, 0) == 15


# ── wound_severity ─────────────────────────────────────────────────────────

class TestWoundSeverity:
    def test_no_damage(self):
        assert wound_severity(0) == "none"

    def test_negative_damage(self):
        assert wound_severity(-5) == "none"

    def test_scratch(self):
        assert wound_severity(1) == "scratch"
        assert wound_severity(3) == "scratch"

    def test_light(self):
        assert wound_severity(4) == "light"
        assert wound_severity(6) == "light"

    def test_serious(self):
        assert wound_severity(7) == "serious"
        assert wound_severity(10) == "serious"

    def test_critical(self):
        assert wound_severity(11) == "critical"
        assert wound_severity(15) == "critical"

    def test_mortal(self):
        assert wound_severity(16) == "mortal"
        assert wound_severity(100) == "mortal"


# ── calculate_damage ───────────────────────────────────────────────────────

class TestCalculateDamage:
    def test_basic(self):
        # raw = 6 + (6 // 3) = 8; modified = round(8 * 1.0) = 8; final = 8 - 2 = 6
        dmg = calculate_damage(weapon_base=6, might=6, location_multiplier=1.0, armor_at_location=2)
        assert dmg == 6

    def test_head_multiplier(self):
        # raw = 6 + 2 = 8; modified = round(8 * 1.5) = 12; final = 12 - 0 = 12
        dmg = calculate_damage(6, 6, 1.5, 0)
        assert dmg == 12

    def test_armor_negates_all(self):
        dmg = calculate_damage(3, 3, 1.0, 20)
        assert dmg == 0

    def test_minimum_zero(self):
        dmg = calculate_damage(2, 3, 0.5, 100)
        assert dmg == 0

    def test_high_might_scales(self):
        dmg_low = calculate_damage(6, 3, 1.0, 0)
        dmg_high = calculate_damage(6, 9, 1.0, 0)
        assert dmg_high > dmg_low


# ── compute_max_hp ─────────────────────────────────────────────────────────

class TestComputeMaxHp:
    def test_formula(self):
        # (tou * 3) + mig + 10 = (5 * 3) + 5 + 10 = 30
        assert compute_max_hp(5, 5) == 30

    def test_low_stats(self):
        assert compute_max_hp(1, 1) == 14

    def test_high_stats(self):
        assert compute_max_hp(10, 10) == 50


# ── compute_max_stamina ────────────────────────────────────────────────────

class TestComputeMaxStamina:
    def test_formula(self):
        # (tou * 2) + wil + 10 = 10 + 5 + 10 = 25
        assert compute_max_stamina(5, 5) == 25


# ── compute_stamina_recovery ───────────────────────────────────────────────

class TestComputeStaminaRecovery:
    def test_low_tou(self):
        assert compute_stamina_recovery(1) == 1  # 1 + (1 // 3) = 1

    def test_mid_tou(self):
        assert compute_stamina_recovery(6) == 3  # 1 + 2

    def test_high_tou(self):
        assert compute_stamina_recovery(9) == 4  # 1 + 3


# ── compute_carry_limit ────────────────────────────────────────────────────

class TestComputeCarryLimit:
    def test_formula(self):
        # (mig * 5) + 10 = 30 + 10 = 40
        assert compute_carry_limit(6) == 40.0

    def test_minimum(self):
        assert compute_carry_limit(1) == 15.0


# ── compute_march_speed ─────────────────────────────────────────────────────

class TestComputeMarchSpeed:
    def test_clear_coast(self):
        speed = compute_march_speed(25.0, 1.0, 1.0, 1.0, False)
        assert speed == 25.0

    def test_terrain_forest(self):
        speed = compute_march_speed(25.0, 0.6, 1.0, 1.0, False)
        assert speed == 15.0

    def test_weak_link(self):
        speed_full = compute_march_speed(25.0, 1.0, 1.0, 1.0, False)
        speed_wl = compute_march_speed(25.0, 1.0, 1.0, 1.0, True)
        assert speed_wl < speed_full
        assert speed_wl == pytest.approx(25.0 * 0.85, abs=0.1)

    def test_all_modifiers(self):
        speed = compute_march_speed(25.0, 0.6, 0.7, 0.8, False)
        assert speed == pytest.approx(25 * 0.6 * 0.7 * 0.8, abs=0.1)


# ── compute_foraging ───────────────────────────────────────────────────────

class TestComputeForaging:
    def test_zero_foragers(self):
        assert compute_foraging(4, 0, 0.0) == 0

    def test_two_foragers(self):
        # base = 4, all mults 1.0 → 4
        assert compute_foraging(4, 2, 0.0) == 4

    def test_season_mult_reduces(self):
        summer = compute_foraging(4, 2, 0.0, season_mult=1.0)
        dark = compute_foraging(4, 2, 0.0, season_mult=0.7)
        assert dark < summer


# ── resolve_check ─────────────────────────────────────────────────────────

class TestResolveCheck:
    def test_forced_crit_success(self):
        random.seed(1)
        # Chance = 75; crit threshold = 15; need roll <= 15
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(random, "randint", lambda a, b: 1)
            result = resolve_check(6, 3, 0)
            assert result.result == ResultLevel.CRITICAL_SUCCESS

    def test_forced_crit_failure(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(random, "randint", lambda a, b: 100)
            result = resolve_check(4, 2, 0)  # chance = 55, roll 100 > 95 → crit fail
            assert result.result == ResultLevel.CRITICAL_FAILURE

    def test_forced_success(self):
        with pytest.MonkeyPatch.context() as mp:
            # chance = 75, crit threshold = 15; roll = 50 → success
            mp.setattr(random, "randint", lambda a, b: 50)
            result = resolve_check(6, 3, 0)
            assert result.result in (ResultLevel.SUCCESS, ResultLevel.CRITICAL_SUCCESS)

    def test_forced_failure(self):
        with pytest.MonkeyPatch.context() as mp:
            # chance = 15 (attr=0, skill=0 → 15), roll = 30 → failure
            mp.setattr(random, "randint", lambda a, b: 30)
            result = resolve_check(0, 0, 0)
            assert result.result in (ResultLevel.FAILURE, ResultLevel.CRITICAL_FAILURE)

    def test_returns_check_result(self):
        result = resolve_check(5, 2, 0)
        assert isinstance(result, CheckResult)
        assert hasattr(result, "final_chance")
        assert hasattr(result, "roll")
        assert hasattr(result, "result")
        assert hasattr(result, "margin")

    def test_final_chance_computed_correctly(self):
        result = resolve_check(5, 2, 0)
        expected_chance = compute_success_chance(5, 2, 0)
        assert result.final_chance == expected_chance

    def test_margin_positive_on_success(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(random, "randint", lambda a, b: 1)
            result = resolve_check(6, 3, 0)  # chance 75, roll 1 → margin +74
            assert result.margin > 0


# ── resolve_opposed ────────────────────────────────────────────────────────

class TestResolveOpposed:
    def test_attacker_wins_when_only_attacker_succeeds(self):
        rolls = iter([1, 100])  # attacker rolls 1 (success), defender 100 (crit fail)
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(random, "randint", lambda a, b: next(rolls))
            r = resolve_opposed(6, 3, 0, 3, 0, 0)
            assert r.winner == "attacker"

    def test_defender_wins_when_only_defender_succeeds(self):
        rolls = iter([100, 1])  # attacker crit-fails, defender crit-succeeds
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(random, "randint", lambda a, b: next(rolls))
            r = resolve_opposed(3, 0, 0, 6, 3, 0)
            assert r.winner == "defender"

    def test_stalemate_when_both_fail(self):
        # Both have very low chance — high rolls → both fail
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(random, "randint", lambda a, b: 50)
            # chance for (0, 0, 0) = 15; roll 50 > 15 → failure for both
            r = resolve_opposed(0, 0, 0, 0, 0, 0)
            assert r.winner == "stalemate"

    def test_returns_opposed_result(self):
        r = resolve_opposed(5, 2, 0, 5, 2, 0)
        assert isinstance(r, OpposedResult)
        assert r.winner in ("attacker", "defender", "stalemate")


# ── hit_location ──────────────────────────────────────────────────────────

class TestHitLocation:
    def test_head_at_roll_10(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(random, "randint", lambda a, b: 10)
            loc, mult = hit_location()
            assert loc == "head"
            assert mult == 1.5

    def test_torso_at_roll_40(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(random, "randint", lambda a, b: 40)
            loc, mult = hit_location()
            assert loc == "torso"
            assert mult == 1.0

    def test_right_arm_at_roll_50(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(random, "randint", lambda a, b: 50)
            loc, mult = hit_location()
            assert loc == "right_arm"

    def test_valid_location_always_returned(self):
        valid_locs = {"head", "torso", "right_arm", "left_arm", "legs", "hands", "feet"}
        for seed in range(50):
            random.seed(seed)
            loc, mult = hit_location()
            assert loc in valid_locs
            assert mult > 0


# ── roll utilities ─────────────────────────────────────────────────────────

class TestRollUtilities:
    def test_roll_d100_range(self):
        for _ in range(200):
            r = roll_d100()
            assert 1 <= r <= 100

    def test_roll_dice_count(self):
        results = roll_dice(3, 6)
        assert len(results) == 3
        for r in results:
            assert 1 <= r <= 6

    def test_roll_sum_range(self):
        s = roll_sum(2, 6)
        assert 2 <= s <= 12

    def test_roll_sum_single_die(self):
        for _ in range(20):
            assert 1 <= roll_sum(1, 20) <= 20
