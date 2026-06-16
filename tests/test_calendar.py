"""test_calendar.py — Tests for calendar_sim.py (deterministic functions only)."""
import pytest

from calendar_sim import (
    day_to_date,
    get_season,
    get_season_key,
    DAYS_PER_YEAR,
    MONTH_NAMES,
    TIME_COSTS,
)


class TestDayToDate:
    def test_first_day_is_month_1_day_1(self):
        d = day_to_date(1)
        assert d["month_number"] == 1
        assert d["day_of_month"] == 1
        assert d["month_name"] == MONTH_NAMES[0]

    def test_last_day_of_month_1(self):
        d = day_to_date(30)
        assert d["month_number"] == 1
        assert d["day_of_month"] == 30

    def test_first_day_of_month_2(self):
        d = day_to_date(31)
        assert d["month_number"] == 2
        assert d["day_of_month"] == 1

    def test_last_day_of_year(self):
        d = day_to_date(360)
        assert d["month_number"] == 12
        assert d["day_of_month"] == 30

    def test_clamped_min(self):
        d = day_to_date(0)
        assert d["month_number"] == 1
        assert d["day_of_month"] == 1

    def test_clamped_max(self):
        d = day_to_date(999)
        assert d["month_number"] == 12
        assert d["day_of_month"] == 30

    def test_all_12_months_accessible(self):
        months_seen = set()
        for day in range(1, DAYS_PER_YEAR + 1):
            months_seen.add(day_to_date(day)["month_number"])
        assert months_seen == set(range(1, 13))


class TestGetSeason:
    def test_day_1_is_long_summer(self):
        assert "Summer" in get_season(1)

    def test_day_60_is_long_summer(self):
        assert "Summer" in get_season(60)

    def test_day_61_is_long_dark(self):
        assert "Dark" in get_season(61)

    def test_day_360_is_long_dark(self):
        assert "Dark" in get_season(360)


class TestGetSeasonKey:
    def test_summer_key(self):
        assert get_season_key(1) == "long_summer"
        assert get_season_key(60) == "long_summer"

    def test_dark_key(self):
        assert get_season_key(61) == "long_dark"
        assert get_season_key(350) == "long_dark"


class TestTimeCosts:
    def test_march_costs_1_day(self):
        assert TIME_COSTS["march"]["days"] == 1.0

    def test_forage_costs_quarter_day(self):
        assert TIME_COSTS["forage"]["days"] == 0.25

    def test_rest_full_day(self):
        assert TIME_COSTS["rest_full_day"]["days"] == 1.0

    def test_all_entries_have_days_field(self):
        for key, val in TIME_COSTS.items():
            assert "days" in val, f"{key} missing 'days' field"
