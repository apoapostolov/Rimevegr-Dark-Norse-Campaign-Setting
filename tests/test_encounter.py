"""test_encounter.py — Tests for encounter.py table structure and roll_encounter."""
import pytest

from encounter import (
    roll_encounter,
    get_encounter_table,
    ENCOUNTER_TABLES,
    SEASON_MODIFIERS,
    TIME_MODIFIERS,
)

VALID_CATEGORIES = {
    "combat", "social", "environment", "exploration",
    "supernatural", "hazard", "neutral",
}

KNOWN_TERRAINS = list(ENCOUNTER_TABLES.keys())


class TestEncounterTableStructure:
    def test_all_tables_have_final_100_threshold(self):
        for terrain, table in ENCOUNTER_TABLES.items():
            assert table[-1][0] == 100, (
                f"{terrain}: last threshold should be 100, got {table[-1][0]}"
            )

    def test_all_tables_thresholds_ascending(self):
        for terrain, table in ENCOUNTER_TABLES.items():
            thresholds = [entry[0] for entry in table]
            assert thresholds == sorted(thresholds), (
                f"{terrain}: thresholds not sorted"
            )

    def test_each_entry_has_5_elements(self):
        for terrain, table in ENCOUNTER_TABLES.items():
            for entry in table:
                assert len(entry) == 5, (
                    f"{terrain}: entry {entry} has {len(entry)} elements, expected 5"
                )

    def test_entry_types_are_valid(self):
        for terrain, table in ENCOUNTER_TABLES.items():
            for threshold, name, category, description, details in table:
                assert isinstance(threshold, int)
                assert isinstance(name, str) and name
                assert isinstance(category, str)
                assert category in VALID_CATEGORIES, (
                    f"{terrain}/{name}: unknown category '{category}'"
                )
                assert isinstance(description, str)
                assert isinstance(details, dict)


class TestGetEncounterTable:
    def test_known_terrain_returns_list(self):
        table = get_encounter_table("coast")
        assert isinstance(table, list)
        assert len(table) > 0

    def test_unknown_terrain_returns_default(self):
        table = get_encounter_table("unknown_terrain_xyz")
        assert isinstance(table, list)

    def test_each_dict_has_threshold(self):
        table = get_encounter_table("forest")
        for entry in table:
            assert "threshold" in entry


class TestRollEncounter:
    def test_returns_none_or_dict(self):
        # May return None (no encounter triggered)
        for _ in range(30):
            result = roll_encounter("coast")
            assert result is None or isinstance(result, dict)

    def test_dict_result_has_required_keys(self):
        # Force an encounter by calling many times
        results = [roll_encounter("coast", "long_summer", "day", 0) for _ in range(50)]
        encounters = [r for r in results if r is not None]
        if encounters:
            for key in ("type", "category", "description", "terrain"):
                assert key in encounters[0]

    def test_encounter_category_valid_when_returned(self):
        for _ in range(40):
            result = roll_encounter("forest", "long_summer", "night")
            if result is not None:
                assert result["category"] in VALID_CATEGORIES

    def test_barrow_terrain_works(self):
        results = [roll_encounter("barrow") for _ in range(20)]
        # Should not throw; may return None or dict
        for r in results:
            assert r is None or isinstance(r, dict)


class TestSeasonModifiers:
    def test_long_dark_higher_encounter_chance(self):
        dark = SEASON_MODIFIERS["long_dark"]["encounter_chance"]
        summer = SEASON_MODIFIERS["long_summer"]["encounter_chance"]
        assert dark >= summer

    def test_dark_higher_supernatural_mod(self):
        dark = SEASON_MODIFIERS["long_dark"]["supernatural_mod"]
        summer = SEASON_MODIFIERS["long_summer"]["supernatural_mod"]
        assert dark >= summer


class TestTimeModifiers:
    def test_night_higher_encounter_chance_mod(self):
        night_mod = TIME_MODIFIERS["night"]["encounter_chance_mod"]
        day_mod = TIME_MODIFIERS["day"]["encounter_chance_mod"]
        assert night_mod >= day_mod
