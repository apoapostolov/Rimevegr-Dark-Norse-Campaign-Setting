"""test_weather.py — Tests for weather.py deterministic / structure functions."""
import pytest

from weather import (
    determine_season,
    determine_sub_season,
    day_to_week,
    generate_weather,
    WEATHER_MODIFIERS,
    LONG_SUMMER_TABLE,
    LONG_DARK_TABLE,
)


class TestDetermineSeason:
    def test_day_1_summer(self):
        assert determine_season(1) == "long_summer"

    def test_day_60_summer(self):
        assert determine_season(60) == "long_summer"

    def test_day_61_dark(self):
        assert determine_season(61) == "long_dark"

    def test_day_360_dark(self):
        assert determine_season(360) == "long_dark"


class TestDetermineSubSeason:
    def test_thaw(self):
        result = determine_sub_season(15)
        assert result in ("thaw",)

    def test_long_sun(self):
        result = determine_sub_season(45)
        assert result in ("long_sun",)

    def test_harvest(self):
        result = determine_sub_season(50)
        assert result in ("harvest", "long_sun")  # 45-60 may vary

    def test_long_dark(self):
        result = determine_sub_season(200)
        assert result == "long_dark"

    def test_returns_string(self):
        for day in (1, 30, 60, 90, 180, 300, 360):
            assert isinstance(determine_sub_season(day), str)


class TestDayToWeek:
    def test_day_1_week_1(self):
        assert day_to_week(1) == 1

    def test_day_7_week_1(self):
        assert day_to_week(7) == 1

    def test_day_8_week_2(self):
        assert day_to_week(8) == 2

    def test_day_14_week_2(self):
        assert day_to_week(14) == 2

    def test_day_15_week_3(self):
        assert day_to_week(15) == 3

    def test_capped_at_48(self):
        assert day_to_week(999) == 48


class TestWeatherModifiers:
    def test_clear_grey_has_all_mod_keys(self):
        mods = WEATHER_MODIFIERS["clear_grey"]
        assert "forage_mod" in mods
        assert "travel_mod" in mods

    def test_rime_storm_travel_very_low(self):
        assert WEATHER_MODIFIERS["rime_storm"]["travel_mod"] <= 0.3

    def test_rime_storm_foraging_zero(self):
        assert WEATHER_MODIFIERS["rime_storm"]["forage_mod"] == 0.0

    def test_multiplier_modare_numeric(self):
        """All modifiers should be numeric (can be negative — e.g. ranged_mod is a penalty)."""
        numeric_keys = {"forage_mod", "travel_mod", "combat_mod", "ranged_mod"}
        for w_type, mods in WEATHER_MODIFIERS.items():
            for k, v in mods.items():
                if k in numeric_keys:
                    assert isinstance(v, (int, float)), (
                        f"{w_type}.{k} has non-numeric value {v!r}"
                    )


class TestWeatherTables:
    def test_summer_table_last_entry_is_100(self):
        assert LONG_SUMMER_TABLE[-1][0] == 100

    def test_dark_table_last_entry_is_100(self):
        assert LONG_DARK_TABLE[-1][0] == 100

    def test_summer_table_sorted_ascending(self):
        thresholds = [entry[0] for entry in LONG_SUMMER_TABLE]
        assert thresholds == sorted(thresholds)

    def test_dark_table_sorted_ascending(self):
        thresholds = [entry[0] for entry in LONG_DARK_TABLE]
        assert thresholds == sorted(thresholds)

    def test_all_summer_weather_types_in_modifiers(self):
        for threshold, weather_type, _dur in LONG_SUMMER_TABLE:
            assert weather_type in WEATHER_MODIFIERS, (
                f"Weather type '{weather_type}' in LONG_SUMMER_TABLE has no entry in WEATHER_MODIFIERS"
            )

    def test_all_dark_weather_types_in_modifiers(self):
        for threshold, weather_type, _dur in LONG_DARK_TABLE:
            assert weather_type in WEATHER_MODIFIERS, (
                f"Weather type '{weather_type}' in LONG_DARK_TABLE has no entry in WEATHER_MODIFIERS"
            )


class TestGenerateWeather:
    def test_returns_required_keys(self):
        result = generate_weather("long_summer")
        for key in ("weather", "display", "duration_days", "is_event", "modifiers", "roll"):
            assert key in result, f"missing key: {key}"

    def test_weather_type_known(self):
        for _ in range(20):
            result = generate_weather("long_summer")
            assert result["weather"] in WEATHER_MODIFIERS

    def test_dark_season(self):
        result = generate_weather("long_dark")
        assert result["weather"] in WEATHER_MODIFIERS

    def test_roll_in_range(self):
        for _ in range(20):
            result = generate_weather("long_summer")
            assert 1 <= result["roll"] <= 100
