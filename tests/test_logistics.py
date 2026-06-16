"""test_logistics.py — Tests for logistics.py deterministic functions."""
import pytest

from logistics import (
    daily_food_consumption,
    food_for_days,
    march_speed,
    carry_check,
    TERRAIN_MULT,
    WEATHER_MULT,
    SEASON_MULT,
    FOOD_PER_PERSON_SUMMER,
    FOOD_PER_PERSON_DARK,
)


class TestDailyFoodConsumption:
    def test_summer_rate(self):
        r = daily_food_consumption(10, "long_summer")
        assert r == pytest.approx(10 * FOOD_PER_PERSON_SUMMER)

    def test_dark_rate_higher(self):
        summer = daily_food_consumption(10, "long_summer")
        dark = daily_food_consumption(10, "long_dark")
        assert dark > summer

    def test_dark_alias(self):
        assert daily_food_consumption(10, "dark") == daily_food_consumption(10, "long_dark")

    def test_zero_band_size(self):
        assert daily_food_consumption(0, "long_summer") == 0.0


class TestFoodForDays:
    def test_single_day(self):
        assert food_for_days(10, 1, "long_summer") == daily_food_consumption(10, "long_summer")

    def test_seven_days(self):
        assert food_for_days(10, 7) == pytest.approx(daily_food_consumption(10, "long_summer") * 7)

    def test_dark_season_costs_more(self):
        assert food_for_days(14, 7, "long_dark") > food_for_days(14, 7, "long_summer")


class TestMarchSpeed:
    def test_clear_coast_full_speed(self):
        result = march_speed("coast", "clear_grey", "long_summer", False)
        assert result["terrain_mult"] == 1.0
        assert result["weather_mult"] == 1.0
        assert result["season_mult"] == 1.0
        assert result["final_km_per_day"] == 25.0

    def test_forest_slower_than_coast(self):
        f = march_speed("forest", "clear_grey", "long_summer", False)
        c = march_speed("coast", "clear_grey", "long_summer", False)
        assert f["final_km_per_day"] < c["final_km_per_day"]

    def test_rime_storm_near_zero(self):
        result = march_speed("coast", "rime_storm", "long_summer", False)
        assert result["final_km_per_day"] <= 6.0

    def test_weak_link_reduces_speed(self):
        no_wl = march_speed("coast", "clear_grey", "long_summer", False)
        with_wl = march_speed("coast", "clear_grey", "long_summer", True)
        assert with_wl["final_km_per_day"] < no_wl["final_km_per_day"]
        assert with_wl["weak_link_mult"] == 0.85

    def test_dark_season_reduces_speed(self):
        s = march_speed("coast", "clear_grey", "long_summer", False)
        d = march_speed("coast", "clear_grey", "long_dark", False)
        assert d["final_km_per_day"] < s["final_km_per_day"]

    def test_result_has_required_keys(self):
        r = march_speed()
        for key in ("terrain", "weather", "season", "final_km_per_day", "weak_link"):
            assert key in r


class TestCarryCheck:
    def test_under_limit_not_overloaded(self):
        result = carry_check(might=6, gear_kg=10.0)
        assert not result["overloaded"]
        assert result["excess_kg"] == 0.0

    def test_at_limit_not_overloaded(self):
        limit = (6 * 5.0) + 10.0  # = 40.0
        result = carry_check(6, limit)
        assert not result["overloaded"]

    def test_over_limit_is_overloaded(self):
        result = carry_check(might=6, gear_kg=50.0)
        assert result["overloaded"]
        assert result["excess_kg"] > 0

    def test_carry_limit_formula(self):
        result = carry_check(might=5, gear_kg=0)
        # (5 * 5) + 10 = 35
        assert result["carry_limit_kg"] == 35.0
