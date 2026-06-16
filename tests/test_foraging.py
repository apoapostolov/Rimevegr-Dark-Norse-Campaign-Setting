"""test_foraging.py — Tests for foraging.py."""
import pytest

from foraging import (
    lookup_base_output,
    forage,
    check_deficit,
    FORAGING_TABLE,
    SEASON_MULT,
    WEATHER_FORAGE_MULT,
)


class TestLookupBaseOutput:
    def test_fjord_2_foragers(self):
        assert lookup_base_output("fjord", 2) == FORAGING_TABLE["fjord"]["1-2"]

    def test_fjord_5_foragers(self):
        assert lookup_base_output("fjord", 5) == FORAGING_TABLE["fjord"]["3-5"]

    def test_fjord_10_foragers(self):
        assert lookup_base_output("fjord", 10) == FORAGING_TABLE["fjord"]["6-10"]

    def test_fjord_15_foragers(self):
        assert lookup_base_output("fjord", 15) == FORAGING_TABLE["fjord"]["11+"]

    def test_zero_foragers(self):
        assert lookup_base_output("fjord", 0) == 0

    def test_coast_aliases_to_fjord(self):
        assert lookup_base_output("coast", 2) == lookup_base_output("fjord", 2)

    def test_pine_aliases_to_forest(self):
        assert lookup_base_output("pine", 2) == lookup_base_output("forest", 2)

    def test_high_moors_aliases_to_moors(self):
        assert lookup_base_output("high_moors", 2) == lookup_base_output("moors", 2)

    def test_ice_yields_lowest(self):
        assert lookup_base_output("ice", 2) <= lookup_base_output("fjord", 2)


class TestForage:
    def test_returns_dict_with_required_keys(self):
        result = forage("fjord", 4, 2.0, "long_summer", "clear_grey")
        for key in ("food_gathered", "base_output", "season_mult", "weather_mult"):
            assert key in result

    def test_dark_season_reduces_output(self):
        summer = forage("fjord", 4, 0.0, "long_summer", "clear_grey")
        dark = forage("fjord", 4, 0.0, "long_dark", "clear_grey")
        assert dark["food_gathered"] <= summer["food_gathered"]

    def test_rime_storm_zeroes_output(self):
        result = forage("fjord", 4, 0.0, "long_summer", "rime_storm")
        assert result["food_gathered"] == 0

    def test_skill_increases_output(self):
        low = forage("forest", 4, 0.0, "long_summer", "clear_grey")
        high = forage("forest", 4, 3.0, "long_summer", "clear_grey")
        assert high["food_gathered"] >= low["food_gathered"]

    def test_output_nonnegative(self):
        for terrain in ("fjord", "forest", "moors", "ice"):
            result = forage(terrain, 2, 0.0, "long_dark", "rime_storm")
            assert result["food_gathered"] >= 0


class TestCheckDeficit:
    def test_surplus_when_stores_ample(self):
        result = check_deficit(100, 10, "long_summer", 3)
        assert result["status"] == "surplus"
        assert result["surplus_deficit"] > 0

    def test_deficit_when_stores_low(self):
        result = check_deficit(5, 10, "long_summer", 3)
        assert result["status"] == "deficit"

    def test_days_remaining_formula(self):
        result = check_deficit(20, 10, "long_summer", 1)
        # daily = 10 * 1.0 = 10; days left = 20 / 10 = 2.0
        assert result["days_of_food_remaining"] == pytest.approx(2.0, abs=0.01)

    def test_morale_risk_when_less_than_3_days(self):
        result = check_deficit(5, 10, "long_summer", 1)
        # 5 / 10 = 0.5 days → morale_risk True
        assert result["morale_risk"] is True

    def test_no_morale_risk_when_ample(self):
        result = check_deficit(100, 10, "long_summer", 1)
        assert result["morale_risk"] is False
