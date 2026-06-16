"""test_ledger.py — Tests for ledger.py financial functions."""
import pytest

from ledger import (
    copper_to_display,
    calculate_weekly_retainer,
    calculate_mission_pay,
    divide_loot,
    WEEKLY_RETAINER,
    DAILY_MISSION,
    LOOT_SPLITS,
)


class TestCopperToDisplay:
    def test_round_silver(self):
        assert copper_to_display(10) in ("1 silver", "1 silver 0 copper")

    def test_copper_and_silver(self):
        assert copper_to_display(35) in ("3 silver 5 copper", "3s 5c")

    def test_zero_copper(self):
        result = copper_to_display(0)
        assert "0" in result

    def test_pure_copper(self):
        result = copper_to_display(5)
        assert "5" in result

    def test_large_value_has_silver(self):
        result = copper_to_display(100)
        assert "silver" in result or "s" in result

    def test_returns_string(self):
        assert isinstance(copper_to_display(15), str)


class TestWeeklyRetainer:
    def test_single_common(self):
        result = calculate_weekly_retainer([{"name": "Grimolf", "rank": "common"}])
        assert result["total_copper"] == WEEKLY_RETAINER["common"]

    def test_single_veteran(self):
        result = calculate_weekly_retainer([{"name": "Brynn", "rank": "veteran"}])
        assert result["total_copper"] == WEEKLY_RETAINER["veteran"]

    def test_single_named_man(self):
        result = calculate_weekly_retainer([{"name": "The Iron Wolf", "rank": "named_man"}])
        assert result["total_copper"] == WEEKLY_RETAINER["named_man"]

    def test_empty_band_is_zero(self):
        result = calculate_weekly_retainer([])
        assert result["total_copper"] == 0

    def test_mixed_band_sums_correctly(self):
        members = [
            {"name": "A", "rank": "common"},
            {"name": "B", "rank": "veteran"},
        ]
        result = calculate_weekly_retainer(members)
        expected = WEEKLY_RETAINER["common"] + WEEKLY_RETAINER["veteran"]
        assert result["total_copper"] == expected

    def test_breakdown_present(self):
        members = [{"name": "X", "rank": "common"}]
        result = calculate_weekly_retainer(members)
        assert "breakdown" in result


class TestMissionPay:
    def test_single_common_one_day(self):
        result = calculate_mission_pay([{"name": "Orm", "rank": "common"}], days=1)
        assert result["total_copper"] == DAILY_MISSION["common"]

    def test_three_days(self):
        result = calculate_mission_pay([{"name": "Orm", "rank": "common"}], days=3)
        assert result["total_copper"] == DAILY_MISSION["common"] * 3

    def test_veteran_earns_more_than_common(self):
        c = calculate_mission_pay([{"name": "A", "rank": "common"}], days=1)["total_copper"]
        v = calculate_mission_pay([{"name": "B", "rank": "veteran"}], days=1)["total_copper"]
        assert v > c


class TestDivideLoot:
    def test_standard_archetype_total_check(self):
        counts = {"captain": 1, "named": 0, "veteran": 2, "common": 4}
        result = divide_loot(100, "standard", counts)
        assert result["total_silver"] == 100
        assert result["archetype"] == "standard"

    def test_fractions_sum_to_one(self):
        for archetype, splits in LOOT_SPLITS.items():
            total = sum(splits.values())
            assert total == pytest.approx(1.0, abs=0.001), (
                f"{archetype} fractions sum to {total}"
            )

    def test_captain_gets_most_in_standard(self):
        counts = {"captain": 1, "named": 1, "veteran": 1, "common": 1}
        result = divide_loot(200, "standard", counts)
        cap_pp = result["division"]["captain"]["per_person_copper"]
        com_pp = result["division"]["common"]["per_person_copper"]
        assert cap_pp > com_pp

    def test_equal_share_when_all_one_person(self):
        # All equal weight if only one person in each rank
        counts = {"captain": 1, "named": 0, "veteran": 0, "common": 0}
        result = divide_loot(100, "standard", counts)
        captain_pool = result["division"]["captain"]["pool_copper"]
        expected = int(1000 * LOOT_SPLITS["standard"]["captain"])
        assert captain_pool == expected

    def test_division_key_present(self):
        result = divide_loot(50, "standard", {"captain": 1, "named": 0, "veteran": 1, "common": 2})
        assert "division" in result


class TestLedgerConstants:
    def test_named_man_highest_retainer(self):
        assert WEEKLY_RETAINER["named_man"] > WEEKLY_RETAINER["veteran"]
        assert WEEKLY_RETAINER["veteran"] > WEEKLY_RETAINER["common"]

    def test_veteran_daily_higher_than_common(self):
        assert DAILY_MISSION["veteran"] > DAILY_MISSION["common"]
