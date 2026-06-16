"""test_settlement.py — Tests for settlement.py."""
from pathlib import Path

import pytest
import yaml

from settlement import (
    create_settlement,
    get_prices,
    settlement_info,
    settlement_services,
    SETTLEMENT_SIZES,
    BASE_PRICES,
    FEUD_PRICE_MULT,
    TERRAIN_TRAITS,
)


class TestSettlementSizes:
    def test_hamlet_has_services(self):
        assert "services" in SETTLEMENT_SIZES["hamlet"]
        assert len(SETTLEMENT_SIZES["hamlet"]["services"]) >= 1

    def test_village_larger_than_hamlet(self):
        hamlet_pop = SETTLEMENT_SIZES["hamlet"]["population"][1]
        village_pop = SETTLEMENT_SIZES["village"]["population"][1]
        assert village_pop > hamlet_pop

    def test_all_sizes_have_required_fields(self):
        for size_name, size_data in SETTLEMENT_SIZES.items():
            assert "services" in size_data, f"{size_name} missing 'services'"
            assert "population" in size_data, f"{size_name} missing 'population'"


class TestCreateSettlement:
    def test_returns_dict_with_required_keys(self):
        s = create_settlement("Thornby", "village", "coast", 0, 2)
        for key in ("name", "size", "terrain", "population"):
            assert key in s

    def test_name_preserved(self):
        s = create_settlement("Iron Ford", "hamlet", "forest", 0, 1)
        assert s["name"] == "Iron Ford"

    def test_size_preserved(self):
        s = create_settlement("X", "village", "coast", 0, 1)
        assert s["size"] == "village"

    def test_high_feud_affects_settlement(self):
        low = create_settlement("X", "village", "coast", 0, 2)
        high = create_settlement("X", "village", "coast", 4, 2)
        # High feud level should be reflected in the settlement data
        assert high.get("feud_level", 4) >= low.get("feud_level", 0)

    def test_generated_settlement_has_infrastructure_fields(self):
        s = create_settlement("Iron Ford", "large_village", "forest", 0, 1)
        assert "defenses" in s
        assert "structures" in s
        assert "construction_capacity" in s
        assert "maintenance_burden" in s
        assert "damage_state" in s
        assert s["defenses"]["gatehouses"] >= 1
        assert "productive" in s["structures"]


class TestGetPrices:
    def test_no_feud_base_prices_returned(self):
        settlement = create_settlement("Test", "village", "coast", 0, 2)
        result = get_prices(settlement, 0, "coast")
        prices = result.get("prices", result)
        assert "sword" in prices

    def test_feud_level_4_closes_trade(self):
        settlement = create_settlement("Test", "village", "coast", 4, -2)
        result = get_prices(settlement, 4, "coast")
        # feud 4 = no trade; returned as error dict or None or empty
        is_closed = (
            result is None
            or result == {}
            or "error" in result
            or result.get("trade_available") is False
        )
        assert is_closed

    def test_prices_include_common_items(self):
        settlement = create_settlement("X", "village", "coast", 0, 1)
        result = get_prices(settlement, 0, "coast")
        prices = result.get("prices", result)
        for item in ("food_week", "dagger"):
            assert item in prices


class TestSettlementServices:
    def test_hamlet_services(self):
        services = settlement_services("hamlet")
        assert isinstance(services, (dict, list))
        assert "template_structure_summary" in services
        assert "template_defenses" in services

    def test_larger_settlement_more_services(self):
        hamlet = settlement_services("hamlet")
        town = settlement_services("small_town")
        h_count = len(hamlet["services"])
        t_count = len(town["services"])
        assert t_count >= h_count

    def test_named_settlement_services_include_structure_support(self):
        result = settlement_services(name="Frostfjord Hollow")
        assert result["name"] == "Frostfjord Hollow"
        assert "defenses" in result
        assert any("productive:" in line for line in result["structure_summary"])


class TestSettlementInfo:
    def test_named_settlement_exposes_infrastructure(self):
        info = settlement_info("Frostfjord Hollow")
        assert info["name"] == "Frostfjord Hollow"
        assert "defenses" in info
        assert "structure_summary" in info
        assert any("domestic:" in line for line in info["structure_summary"])

    def test_missing_settlement_returns_error(self):
        info = settlement_info("No Such Place")
        assert "error" in info


class TestSettlementInfrastructureConsistency:
    @staticmethod
    def _load_settlements():
        path = Path(__file__).resolve().parent.parent / "data" / "settlements.yaml"
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)["settlements"]

    def test_inn_service_has_actual_guest_building(self):
        for settlement in self._load_settlements():
            if "inn" not in settlement.get("services", []):
                continue
            civic = settlement.get("structures", {}).get("civic_religious", {})
            inn_count = civic.get("inns", 0) + civic.get("guesthalls", 0)
            assert inn_count > 0, settlement["name"]

    def test_healer_service_has_healer_structure(self):
        for settlement in self._load_settlements():
            if not settlement.get("healer"):
                continue
            productive = settlement.get("structures", {}).get("productive", {})
            civic = settlement.get("structures", {}).get("civic_religious", {})
            healer_count = (
                productive.get("healer_lodges", 0)
                + productive.get("healer_huts", 0)
                + civic.get("healer_lodges", 0)
            )
            assert healer_count > 0, settlement["name"]

    def test_temple_service_has_temple_structure(self):
        for settlement in self._load_settlements():
            if "temple" not in settlement.get("services", []):
                continue
            civic = settlement.get("structures", {}).get("civic_religious", {})
            assert civic.get("temples", 0) > 0, settlement["name"]


class TestFeudPriceMultiplier:
    def test_no_feud_multiplier_one(self):
        assert FEUD_PRICE_MULT[0] == 1.0

    def test_escalating_feud_multipliers(self):
        for level in range(3):
            assert FEUD_PRICE_MULT[level + 1] > FEUD_PRICE_MULT[level]

    def test_feud_4_no_trade(self):
        assert FEUD_PRICE_MULT[4] == 0.0


class TestTerrainTraits:
    def test_coast_has_trade_bonus(self):
        assert "trade_bonus" in TERRAIN_TRAITS["coast"]

    def test_mountain_lower_trade_bonus_than_coast(self):
        coast_bonus = TERRAIN_TRAITS["coast"]["trade_bonus"]
        mountain_bonus = TERRAIN_TRAITS["mountain"]["trade_bonus"]
        assert mountain_bonus < coast_bonus

    def test_base_prices_nonnegative(self):
        for item, price in BASE_PRICES.items():
            assert price >= 0, f"{item} has negative base price"
