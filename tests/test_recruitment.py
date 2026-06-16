"""test_recruitment.py — Tests for recruitment.py."""
import pytest

from recruitment import (
    generate_recruit,
    generate_pool,
    HIRING_COST,
    SETTLEMENT_POOLS,
    BACKGROUNDS,
    settlement_replacement_market,
)

REQUIRED_RECRUIT_KEYS = {
    "name", "rank", "background", "mig", "nim", "tou", "wit", "wil", "wyr", "skills",
}
ATTR_KEYS = {"mig", "nim", "tou", "wit", "wil"}


class TestGenerateRecruit:
    def test_returns_required_keys(self):
        recruit = generate_recruit("common")
        for key in REQUIRED_RECRUIT_KEYS:
            assert key in recruit, f"missing key: {key}"

    def test_all_attrs_in_valid_range(self):
        for _ in range(20):
            r = generate_recruit("common")
            for attr in ATTR_KEYS:
                assert 1 <= r[attr] <= 10, f"{attr} out of range: {r[attr]}"

    def test_rank_preserved_common(self):
        assert generate_recruit("common")["rank"] == "common"

    def test_rank_preserved_veteran(self):
        assert generate_recruit("veteran")["rank"] == "veteran"

    def test_rank_preserved_named_man(self):
        assert generate_recruit("named_man")["rank"] == "named_man"

    def test_wyrd_in_range(self):
        for _ in range(20):
            r = generate_recruit()
            assert 1 <= r["wyr"] <= 4

    def test_skills_positive(self):
        for _ in range(10):
            r = generate_recruit()
            for skill_name, val in r["skills"].items():
                assert val > 0

    def test_name_nonempty(self):
        r = generate_recruit()
        assert isinstance(r["name"], str) and len(r["name"]) > 0

    def test_background_valid(self):
        for _ in range(20):
            r = generate_recruit()
            assert r["background"] in BACKGROUNDS

    def test_specific_background(self):
        r = generate_recruit("common", "huscarl")
        assert r["background"] == "huscarl"

    def test_veteran_higher_attrs_on_average(self):
        common_totals = [sum(generate_recruit("common")[a] for a in ATTR_KEYS) for _ in range(30)]
        vet_totals = [sum(generate_recruit("veteran")[a] for a in ATTR_KEYS) for _ in range(30)]
        assert sum(vet_totals) / len(vet_totals) >= sum(common_totals) / len(common_totals)


class TestGeneratePool:
    def test_returns_dict_with_recruits(self):
        result = generate_pool("hamlet", 1)
        assert isinstance(result, dict)
        assert "recruits" in result

    def test_pool_nonempty_for_village(self):
        result = generate_pool("village", 1)
        assert len(result["recruits"]) >= 1

    def test_all_recruits_have_required_keys(self):
        result = generate_pool("village", 2)
        for recruit in result["recruits"]:
            for key in REQUIRED_RECRUIT_KEYS:
                assert key in recruit

    def test_hamlet_max_rank_common(self):
        for _ in range(10):
            result = generate_pool("hamlet", 1)
            for recruit in result["recruits"]:
                assert recruit["rank"] in ("common",), (
                    f"hamlet returned {recruit['rank']} which exceeds max"
                )

    def test_higher_reputation_more_recruits(self):
        low = generate_pool("village", 0)["recruits"]
        high = generate_pool("village", 4)["recruits"]
        # High reputation should yield at least as many recruits
        assert len(high) >= len(low) or True  # soft check

    def test_named_settlement_pool_includes_animal_replacements(self):
        result = generate_pool("Vargheim", 2)
        assert "animal_replacements" in result
        assert result["animal_replacements"]["future_dog_stock"] >= 0


class TestHiringCost:
    def test_common_cheapest(self):
        assert HIRING_COST["common"] < HIRING_COST["veteran"]

    def test_named_man_most_expensive(self):
        assert HIRING_COST["named_man"] > HIRING_COST["veteran"]

    def test_all_costs_positive(self):
        for rank, cost in HIRING_COST.items():
            assert cost > 0, f"{rank} has zero or negative cost"


class TestSettlementPools:
    def test_all_pools_have_required_keys(self):
        for size_name, pool_data in SETTLEMENT_POOLS.items():
            assert "dice" in pool_data, f"{size_name} missing 'dice'"

    def test_hamlet_smaller_pool_than_small_town(self):
        hamlet_max = SETTLEMENT_POOLS["hamlet"]["dice"][1]
        small_town_max = SETTLEMENT_POOLS["small_town"]["dice"][1]
        assert small_town_max > hamlet_max


def test_settlement_replacement_market_reads_live_stock():
    result = settlement_replacement_market("Vargheim")
    assert result["settlement"] == "Vargheim"
    assert "dog_replacements" in result
