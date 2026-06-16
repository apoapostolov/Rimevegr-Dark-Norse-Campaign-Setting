"""test_morale.py — Tests for morale.py."""
import pytest

from morale import (
    apply_morale_events,
    MORALE_TRIGGERS,
    MORALE_ROLL_MOD,
    MORALE_NAMES,
)


class TestApplyMoraleEvents:
    def test_positive_event_raises_morale(self):
        result = apply_morale_events(3, ["won_engagement"])
        assert result["new_morale"] == 4

    def test_negative_event_lowers_morale(self):
        result = apply_morale_events(4, ["late_pay"])
        assert result["new_morale"] == 3

    def test_multiple_events_stack(self):
        result = apply_morale_events(3, ["late_pay", "late_pay"])
        assert result["new_morale"] == 1

    def test_morale_max_clamped_at_5(self):
        result = apply_morale_events(5, ["won_engagement", "won_engagement"])
        assert result["new_morale"] <= 5

    def test_morale_min_clamped_at_1(self):
        result = apply_morale_events(1, ["captain_broke_oath", "captain_broke_oath", "late_pay"])
        assert result["new_morale"] >= 1

    def test_empty_events_unchanged(self):
        result = apply_morale_events(3, [])
        assert result["new_morale"] == 3

    def test_events_key_present(self):
        result = apply_morale_events(4, ["won_engagement"])
        assert "events" in result

    def test_heavy_casualties_big_hit(self):
        result = apply_morale_events(4, ["heavy_casualties"])
        assert result["new_morale"] < 4


class TestMoraleConstants:
    def test_morale_roll_mod_5_highest(self):
        assert MORALE_ROLL_MOD[5] > MORALE_ROLL_MOD[4]
        assert MORALE_ROLL_MOD[4] > MORALE_ROLL_MOD[3]

    def test_morale_roll_mod_1_is_penalizing(self):
        assert MORALE_ROLL_MOD[1] < 0

    def test_morale_names_all_5_levels(self):
        for i in range(1, 6):
            assert i in MORALE_NAMES

    def test_morale_triggers_has_positive_and_negative(self):
        positives = [v for v in MORALE_TRIGGERS.values() if v > 0]
        negatives = [v for v in MORALE_TRIGGERS.values() if v < 0]
        assert len(positives) > 0
        assert len(negatives) > 0

    def test_won_engagement_positive(self):
        assert MORALE_TRIGGERS["won_engagement"] > 0

    def test_late_pay_negative(self):
        assert MORALE_TRIGGERS["late_pay"] < 0
