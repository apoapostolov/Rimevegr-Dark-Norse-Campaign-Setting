"""Integration tests for expanded Iron Ledger data and scripts.

Tests that all expanded scripts (Prompts 20-29) load correctly,
consume new data files, and produce valid outputs.
"""
import pytest
import os
import random
import yaml

# Scripts are on sys.path via conftest.py

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


# =====================================================================
# TestEventManager — event_manager.py
# =====================================================================

class TestEventManager:
    """Tests for event_manager.py"""

    def test_loads_all_event_files(self):
        from event_manager import load_all_events
        events = load_all_events()
        assert len(events) > 0, "Expected at least one event loaded"

    def test_every_event_has_id(self):
        from event_manager import load_all_events
        events = load_all_events()
        for evt in events:
            assert "id" in evt, f"Event missing 'id': {evt.get('title', '?')}"

    def test_event_ids_unique(self):
        from event_manager import load_all_events
        events = load_all_events()
        ids = [e["id"] for e in events]
        assert len(ids) == len(set(ids)), "Duplicate event IDs found"

    def test_filter_by_year(self):
        from event_manager import load_all_events, filter_events
        events = load_all_events()
        years = {e.get("year") for e in events if e.get("year")}
        assert len(years) > 0
        target_year = next(iter(years))
        filtered = filter_events(events, year=target_year)
        assert all(e["year"] == target_year for e in filtered)

    def test_filter_by_category(self):
        from event_manager import load_all_events, filter_events, VALID_CATEGORIES
        events = load_all_events()
        cats = {e.get("category") for e in events if e.get("category")}
        if cats:
            target_cat = next(iter(cats))
            filtered = filter_events(events, category=target_cat)
            assert len(filtered) > 0
            assert all(e["category"] == target_cat for e in filtered)

    def test_filter_by_season(self):
        from event_manager import load_all_events, filter_events
        events = load_all_events()
        seasons = {e.get("season") for e in events if e.get("season")}
        if seasons:
            target_season = next(iter(seasons))
            filtered = filter_events(events, season=target_season)
            assert all(e["season"] == target_season for e in filtered)

    def test_filter_by_chain(self):
        from event_manager import load_all_events, filter_events
        events = load_all_events()
        chains = {e.get("chain") for e in events if e.get("chain")}
        if chains:
            target_chain = next(iter(chains))
            filtered = filter_events(events, chain=target_chain)
            assert len(filtered) > 0
            assert all(e["chain"] == target_chain for e in filtered)

    def test_filter_by_day_range(self):
        from event_manager import load_all_events, filter_events
        events = load_all_events()
        filtered = filter_events(events, day_min=1, day_max=60)
        for e in filtered:
            d = e.get("day", 0)
            assert 1 <= d <= 60

    def test_filter_empty_result(self):
        from event_manager import load_all_events, filter_events
        events = load_all_events()
        filtered = filter_events(events, year=99999)
        assert filtered == []

    def test_event_source_tracking(self):
        from event_manager import load_all_events
        events = load_all_events()
        for evt in events:
            assert "_source" in evt, "Event should track source file"
            assert evt["_source"].endswith(".yaml")


# =====================================================================
# TestBestiary — bestiary.py
# =====================================================================

class TestBestiary:
    """Tests for bestiary.py (CLI/loader)"""

    def test_loads_all_enemies(self):
        from bestiary import load_all_enemies
        enemies = load_all_enemies()
        assert len(enemies) > 0

    def test_every_enemy_has_id_and_name(self):
        from bestiary import load_all_enemies
        enemies = load_all_enemies()
        for e in enemies:
            assert "id" in e, f"Enemy missing 'id': {e}"
            assert "name" in e, f"Enemy missing 'name': {e.get('id', '?')}"

    def test_enemy_ids_unique(self):
        from bestiary import load_all_enemies
        enemies = load_all_enemies()
        ids = [e["id"] for e in enemies]
        assert len(ids) == len(set(ids)), "Duplicate enemy IDs found"

    def test_filter_by_category(self):
        from bestiary import load_all_enemies, filter_enemies, VALID_CATEGORIES
        enemies = load_all_enemies()
        cats = {e.get("category") for e in enemies if e.get("category")}
        for cat in cats:
            if cat in VALID_CATEGORIES:
                filtered = filter_enemies(enemies, category=cat)
                assert len(filtered) > 0
                assert all(e["category"] == cat for e in filtered)

    def test_filter_by_tier(self):
        from bestiary import load_all_enemies, filter_enemies
        enemies = load_all_enemies()
        tiers = {e.get("tier") for e in enemies if e.get("tier")}
        if tiers:
            target_tier = next(iter(tiers))
            filtered = filter_enemies(enemies, tier=target_tier)
            assert all(e["tier"] == target_tier for e in filtered)

    def test_filter_by_tier_range(self):
        from bestiary import load_all_enemies, filter_enemies
        enemies = load_all_enemies()
        filtered = filter_enemies(enemies, tier_min=2, tier_max=4)
        for e in filtered:
            assert 2 <= e.get("tier", 0) <= 4

    def test_filter_by_terrain(self):
        from bestiary import load_all_enemies, filter_enemies
        enemies = load_all_enemies()
        # Find an enemy with terrain to test
        for e in enemies:
            terrains = e.get("encounter_conditions", {}).get("terrain", [])
            if terrains:
                terrain = terrains[0]
                filtered = filter_enemies(enemies, terrain=terrain)
                assert len(filtered) > 0
                break

    def test_filter_named_only(self):
        from bestiary import load_all_enemies, filter_enemies
        enemies = load_all_enemies()
        named = filter_enemies(enemies, named_only=True)
        for e in named:
            assert e.get("named") is True

    def test_source_tracking(self):
        from bestiary import load_all_enemies
        enemies = load_all_enemies()
        for e in enemies:
            assert "_source" in e
            assert e["_source"].endswith(".yaml")

    def test_valid_categories_only(self):
        from bestiary import load_all_enemies, VALID_CATEGORIES
        enemies = load_all_enemies()
        for e in enemies:
            cat = e.get("category")
            if cat:
                assert cat in VALID_CATEGORIES, f"Invalid category '{cat}' on {e['id']}"


# =====================================================================
# TestBarrowGenerator — barrow_generator.py
# =====================================================================

class TestBarrowGenerator:
    """Tests for barrow_generator.py"""

    def test_load_barrow_atlas(self):
        from barrow_generator import load_barrow_atlas
        barrows = load_barrow_atlas()
        assert len(barrows) > 0

    def test_barrow_atlas_has_ids(self):
        from barrow_generator import load_barrow_atlas
        barrows = load_barrow_atlas()
        for b in barrows:
            assert "id" in b, f"Barrow missing 'id': {b.get('name', '?')}"
            assert "name" in b

    def test_load_room_templates(self):
        from barrow_generator import load_room_templates
        templates = load_room_templates()
        assert len(templates) > 0

    def test_load_encounter_tables(self):
        from barrow_generator import load_encounter_tables
        encounters = load_encounter_tables()
        assert len(encounters) > 0

    def test_load_loot_tables(self):
        from barrow_generator import load_loot_tables
        loot = load_loot_tables()
        assert len(loot) > 0

    def test_generate_small_barrow(self):
        from barrow_generator import (
            generate_barrow, load_room_templates,
            load_encounter_tables, load_loot_tables, SIZE_ROOM_COUNTS,
        )
        templates = load_room_templates()
        encounters = load_encounter_tables()
        loot = load_loot_tables()
        random.seed(42)
        result = generate_barrow("small", "ancient", "frostfjord",
                                 templates, encounters, loot)
        assert result["barrow_size"] == "small"
        lo, hi = SIZE_ROOM_COUNTS["small"]
        assert lo <= result["total_rooms"] <= hi

    def test_generate_medium_barrow(self):
        from barrow_generator import (
            generate_barrow, load_room_templates,
            load_encounter_tables, load_loot_tables, SIZE_ROOM_COUNTS,
        )
        templates = load_room_templates()
        encounters = load_encounter_tables()
        loot = load_loot_tables()
        random.seed(123)
        result = generate_barrow("medium", "old", "deepholm",
                                 templates, encounters, loot)
        lo, hi = SIZE_ROOM_COUNTS["medium"]
        assert lo <= result["total_rooms"] <= hi

    def test_generate_large_barrow(self):
        from barrow_generator import (
            generate_barrow, load_room_templates,
            load_encounter_tables, load_loot_tables, SIZE_ROOM_COUNTS,
        )
        templates = load_room_templates()
        encounters = load_encounter_tables()
        loot = load_loot_tables()
        random.seed(7)
        result = generate_barrow("large", "primordial", "grimholt",
                                 templates, encounters, loot)
        lo, hi = SIZE_ROOM_COUNTS["large"]
        assert lo <= result["total_rooms"] <= hi

    def test_generated_rooms_have_required_fields(self):
        from barrow_generator import (
            generate_barrow, load_room_templates,
            load_encounter_tables, load_loot_tables,
        )
        templates = load_room_templates()
        encounters = load_encounter_tables()
        loot = load_loot_tables()
        random.seed(42)
        result = generate_barrow("medium", "ancient", "frostfjord",
                                 templates, encounters, loot)
        for room in result["rooms"]:
            assert "room_id" in room
            assert "name" in room
            assert "category" in room
            assert "depth_level" in room

    def test_filter_rooms_by_size_and_age(self):
        from barrow_generator import load_room_templates, filter_rooms
        templates = load_room_templates()
        filtered = filter_rooms(templates, "medium", "ancient")
        assert len(filtered) > 0

    def test_barrow_depth_progression(self):
        from barrow_generator import (
            generate_barrow, load_room_templates,
            load_encounter_tables, load_loot_tables, DEPTH_BY_SIZE,
        )
        templates = load_room_templates()
        encounters = load_encounter_tables()
        loot = load_loot_tables()
        random.seed(42)
        result = generate_barrow("medium", "ancient", "frostfjord",
                                 templates, encounters, loot)
        max_depth = DEPTH_BY_SIZE["medium"]
        for room in result["rooms"]:
            assert 1 <= room["depth_level"] <= max_depth


# =====================================================================
# TestContractManager — contract_manager.py
# =====================================================================

class TestContractManager:
    """Tests for contract_manager.py"""

    def test_loads_all_contracts(self):
        from contract_manager import load_all_contracts
        contracts, sources = load_all_contracts()
        assert len(contracts) > 0
        assert len(sources) > 0

    def test_every_contract_has_source(self):
        from contract_manager import load_all_contracts
        contracts, _ = load_all_contracts()
        for c in contracts:
            assert "_source" in c

    def test_contracts_have_ids(self):
        from contract_manager import load_all_contracts
        contracts, _ = load_all_contracts()
        ids = [c.get("id") for c in contracts if c.get("id")]
        assert len(ids) > 0

    def test_filter_by_settlement(self):
        from contract_manager import load_all_contracts, filter_contracts
        contracts, _ = load_all_contracts()
        settlements = {c.get("settlement") for c in contracts if c.get("settlement")}
        if settlements:
            target = next(iter(settlements))
            filtered = filter_contracts(contracts, settlement=target)
            assert len(filtered) > 0

    def test_filter_by_risk(self):
        from contract_manager import load_all_contracts, filter_contracts
        contracts, _ = load_all_contracts()
        risks = {c.get("risk") for c in contracts if c.get("risk")}
        if risks:
            target = next(iter(risks))
            filtered = filter_contracts(contracts, risk=target)
            assert all(c.get("risk", "").lower() == target.lower() for c in filtered)

    def test_filter_by_type(self):
        from contract_manager import load_all_contracts, filter_contracts
        contracts, _ = load_all_contracts()
        types = {c.get("type") for c in contracts if c.get("type")}
        if types:
            target = next(iter(types))
            filtered = filter_contracts(contracts, contract_type=target)
            assert len(filtered) > 0

    def test_generate_pool(self):
        from contract_manager import load_all_contracts, generate_pool
        contracts, _ = load_all_contracts()
        pool = generate_pool(contracts, reputation=3, max_pool=6)
        assert len(pool) <= 6

    def test_find_chains(self):
        from contract_manager import load_all_contracts, find_chains
        contracts, _ = load_all_contracts()
        chains = find_chains(contracts)
        # chains is a dict of {id: [unlocked_ids]}
        assert isinstance(chains, dict)

    def test_filter_empty_result(self):
        from contract_manager import load_all_contracts, filter_contracts
        contracts, _ = load_all_contracts()
        filtered = filter_contracts(contracts, settlement="NONEXISTENT_SETTLEMENT_XYZ")
        assert filtered == []


# =====================================================================
# TestNpcManager — npc_manager.py
# =====================================================================

class TestNpcManager:
    """Tests for npc_manager.py"""

    def test_loads_all_npcs(self):
        from npc_manager import load_all_npcs
        npcs = load_all_npcs()
        assert len(npcs) > 0

    def test_every_npc_has_id_and_name(self):
        from npc_manager import load_all_npcs
        npcs = load_all_npcs()
        for n in npcs:
            assert "id" in n, f"NPC missing 'id': {n}"
            assert "name" in n, f"NPC missing 'name': {n.get('id', '?')}"

    def test_npc_ids_unique(self):
        from npc_manager import load_all_npcs
        npcs = load_all_npcs()
        ids = [n["id"] for n in npcs]
        assert len(ids) == len(set(ids)), "Duplicate NPC IDs found"

    def test_npcs_have_category_tracking(self):
        from npc_manager import load_all_npcs
        npcs = load_all_npcs()
        for n in npcs:
            assert "_category" in n
            assert "_source" in n

    def test_filter_by_category(self):
        from npc_manager import load_all_npcs, filter_npcs, CATEGORY_FILES
        npcs = load_all_npcs()
        cats = {n.get("_category") for n in npcs}
        for cat in cats:
            if cat in CATEGORY_FILES:
                filtered = filter_npcs(npcs, category=cat)
                assert len(filtered) > 0
                assert all(n["_category"] == cat for n in filtered)

    def test_filter_by_settlement(self):
        from npc_manager import load_all_npcs, filter_npcs
        npcs = load_all_npcs()
        settlements = set()
        for n in npcs:
            s = n.get("settlement") or n.get("base") or n.get("bound_location")
            if s:
                settlements.add(s)
        if settlements:
            target = next(iter(settlements))
            filtered = filter_npcs(npcs, settlement=target)
            assert len(filtered) > 0

    def test_load_relationship_web(self):
        from npc_manager import load_relationship_web
        web = load_relationship_web()
        assert isinstance(web, dict)

    def test_all_category_files_loaded(self):
        from npc_manager import load_all_npcs, CATEGORY_FILES
        npcs = load_all_npcs()
        loaded_cats = {n.get("_category") for n in npcs}
        # At least some of the expected categories should be present
        assert len(loaded_cats) >= 3

    def test_filter_empty_result(self):
        from npc_manager import load_all_npcs, filter_npcs
        npcs = load_all_npcs()
        filtered = filter_npcs(npcs, settlement="NONEXISTENT_XYZ")
        assert filtered == []


# =====================================================================
# TestWeatherExpanded — weather.py (new CLI commands)
# =====================================================================

class TestWeatherExpanded:
    """Tests for expanded weather.py features (history, lookup, report, etc.)"""

    def test_generate_weather_long_summer(self):
        from weather import generate_weather
        random.seed(42)
        result = generate_weather("long_summer")
        assert "weather" in result
        assert "display" in result
        assert "modifiers" in result

    def test_generate_weather_long_dark(self):
        from weather import generate_weather
        random.seed(42)
        result = generate_weather("long_dark")
        assert "weather" in result

    def test_generate_weather_sequence(self):
        from weather import generate_weather_sequence
        random.seed(42)
        seq = generate_weather_sequence("long_dark", 7)
        assert len(seq) == 7
        for entry in seq:
            assert "day" in entry
            assert "weather" in entry

    def test_weather_modifiers_defined(self):
        from weather import WEATHER_MODIFIERS, WEATHER_DISPLAY
        assert len(WEATHER_MODIFIERS) > 0
        for key, mods in WEATHER_MODIFIERS.items():
            assert "forage_mod" in mods
            assert "travel_mod" in mods

    def test_load_weather_history(self):
        from weather import load_weather_history
        history = load_weather_history()
        assert isinstance(history, dict)

    def test_load_named_events(self):
        from weather import load_named_events
        events = load_named_events()
        assert isinstance(events, list)

    def test_load_hazards(self):
        from weather import load_hazards
        hazards = load_hazards()
        assert isinstance(hazards, dict)

    def test_load_seasonal_life(self):
        from weather import load_seasonal_life
        seasonal = load_seasonal_life()
        assert isinstance(seasonal, dict)

    def test_history_week_lookup(self):
        from weather import load_weather_history, history_week
        wh = load_weather_history()
        years = wh.get("years", {})
        if years:
            year_key = next(iter(years))
            year_int = int(year_key) if isinstance(year_key, str) else year_key
            year_data = years[year_key]
            weeks = year_data.get("weeks", [])
            if weeks:
                wk = weeks[0].get("week", 1)
                result = history_week(year_int, wk)
                assert result is not None
                assert result["week"] == wk

    def test_history_day_lookup(self):
        from weather import load_weather_history, history_day
        wh = load_weather_history()
        years = wh.get("years", {})
        if years:
            year_key = next(iter(years))
            year_int = int(year_key) if isinstance(year_key, str) else year_key
            result = history_day(year_int, 3)
            if result:
                assert "queried_day" in result
                assert result["queried_day"] == 3

    def test_find_named_event(self):
        from weather import load_named_events, find_named_event
        events = load_named_events()
        if events:
            eid = events[0].get("id")
            if eid:
                found = find_named_event(eid)
                assert found is not None
                assert found["id"] == eid

    def test_find_named_event_missing(self):
        from weather import find_named_event
        result = find_named_event("NONEXISTENT_999")
        assert result is None

    def test_hazards_for_terrain(self):
        from weather import hazards_for_terrain
        # Try common terrains
        for terrain in ["forest", "mountain", "coast"]:
            results = hazards_for_terrain(terrain)
            # May be empty for some terrains, that's okay
            assert isinstance(results, list)

    def test_determine_season(self):
        from weather import determine_season
        assert determine_season(1) == "long_summer"
        assert determine_season(30) == "long_summer"
        assert determine_season(60) == "long_summer"
        assert determine_season(61) == "long_dark"
        assert determine_season(200) == "long_dark"

    def test_day_to_week(self):
        from weather import day_to_week
        assert day_to_week(1) == 1
        assert day_to_week(7) == 1
        assert day_to_week(8) == 2
        assert day_to_week(360) == 48


# =====================================================================
# TestTravel — travel.py
# =====================================================================

class TestTravel:
    """Tests for travel.py"""

    def test_simulate_short_trip(self):
        from travel import simulate_travel
        random.seed(42)
        result = simulate_travel(
            distance_km=20, terrain="coast", season="long_summer",
            band_size=10, food_stores=50,
        )
        assert result["arrived"] is True
        assert result["total_days"] >= 1
        assert result["distance_km"] == 20

    def test_simulate_long_trip(self):
        from travel import simulate_travel
        random.seed(42)
        result = simulate_travel(
            distance_km=200, terrain="mountain", season="long_dark",
            band_size=14, food_stores=100,
        )
        assert result["total_days"] > 1
        assert "day_log" in result
        assert len(result["day_log"]) == result["total_days"]

    def test_food_tracking(self):
        from travel import simulate_travel
        random.seed(42)
        result = simulate_travel(
            distance_km=30, terrain="forest", season="long_dark",
            band_size=10, food_stores=100,
        )
        assert result["food_stores_end"] < result["food_stores_start"]

    def test_hazard_detection(self):
        from travel import check_daily_hazard
        random.seed(1)
        # Run many checks to see at least one hazard
        found_hazard = False
        for _ in range(100):
            h = check_daily_hazard("mountain", "driving_snow")
            if h is not None:
                found_hazard = True
                assert "hazard" in h
                assert "description" in h
                break
        assert found_hazard, "Expected at least one hazard in 100 checks"

    def test_route_travel(self):
        from travel import route_travel
        random.seed(42)
        segments = [
            {"distance": 30, "terrain": "coast"},
            {"distance": 20, "terrain": "forest"},
        ]
        result = route_travel(segments, "long_summer", band_size=10, food_stores=80)
        assert result["arrived"] is True
        assert result["total_days"] >= 2
        assert len(result["segments"]) == 2

    def test_terrain_hazards_defined(self):
        from travel import TERRAIN_HAZARDS
        assert "coast" in TERRAIN_HAZARDS
        assert "forest" in TERRAIN_HAZARDS
        assert "mountain" in TERRAIN_HAZARDS

    def test_day_log_structure(self):
        from travel import simulate_travel
        random.seed(42)
        result = simulate_travel(
            distance_km=20, terrain="coast", season="long_summer",
            band_size=5, food_stores=50,
        )
        for day in result["day_log"]:
            assert "day" in day
            assert "weather" in day
            assert "km_covered" in day
            assert "food_consumed" in day


# =====================================================================
# TestVillagePolitics — village_politics.py
# =====================================================================

class TestVillagePolitics:
    """Tests for village_politics.py"""

    def test_load_state(self):
        from village_politics import load_state
        state = load_state()
        assert isinstance(state, dict)

    def test_load_settlements(self):
        from village_politics import load_settlements
        data = load_settlements()
        assert isinstance(data, dict)

    def test_state_has_required_keys(self):
        from village_politics import load_state
        state = load_state()
        # The state should have some standard structure
        assert any(k in state for k in ["current_date", "economies", "demographics",
                                         "feuds", "unions"])

    def test_day_to_season(self):
        from village_politics import day_to_season
        assert day_to_season(1) == "Long Summer"
        assert day_to_season(60) == "Long Summer"
        assert day_to_season(61) == "Early Dark"
        assert day_to_season(150) == "Early Dark"
        assert day_to_season(151) == "Deep Dark"
        assert day_to_season(300) == "Deep Dark"
        assert day_to_season(301) == "Late Dark"

    def test_economy_tick(self):
        from village_politics import load_state, economy_tick_week
        import copy
        state = copy.deepcopy(load_state())
        if state.get("economies") and state.get("demographics"):
            settle = next(iter(state["economies"]))
            result = economy_tick_week(state, settle)
            if result:
                assert "stores" in result
                assert "treasury" in result

    def test_get_feud(self):
        from village_politics import load_state, get_feud
        state = load_state()
        feuds = state.get("feuds", [])
        if feuds:
            pair = feuds[0]["pair"]
            found = get_feud(state, pair[0], pair[1])
            assert found is not None

    def test_modify_feud(self):
        from village_politics import load_state, modify_feud
        import copy
        state = copy.deepcopy(load_state())
        # Create a feud between two arbitrary settlements
        if state.get("economies"):
            settles = list(state["economies"].keys())
            if len(settles) >= 2:
                new_level = modify_feud(state, settles[0], settles[1], 1, "test_cause")
                assert isinstance(new_level, int)
                assert 0 <= new_level <= 4

    def test_find_union(self):
        from village_politics import load_state, find_union
        state = load_state()
        unions = state.get("unions", [])
        if unions:
            name = unions[0]["name"]
            found = find_union(state, name)
            assert found is not None
            assert found["name"] == name

    def test_season_food_mods(self):
        from village_politics import SEASON_FOOD_MOD, SEASON_CONSUMPTION_MOD
        assert SEASON_FOOD_MOD["Long Summer"] == 1.0
        assert SEASON_FOOD_MOD["Deep Dark"] == 0.0
        assert SEASON_CONSUMPTION_MOD["Late Dark"] > 1.0


# =====================================================================
# TestCombatAI — combat_ai.py
# =====================================================================

class TestCombatAI:
    """Tests for combat_ai.py"""

    def _make_fighter(self, **overrides):
        from combat_model import Fighter
        defaults = dict(
            name="TestFighter", mig=5, nim=5, tou=5, wit=5, wil=5,
        )
        defaults.update(overrides)
        return Fighter(**defaults)

    def test_choose_stance_balanced_default(self):
        from combat_ai import choose_stance
        f = self._make_fighter()
        o = self._make_fighter(name="Opponent")
        stance = choose_stance(f, o)
        assert stance is not None

    def test_choose_stance_defensive_low_hp(self):
        from combat_ai import choose_stance
        from combat_types import Stance
        f = self._make_fighter()
        f.hp = 3  # well below 30% of default max_hp
        o = self._make_fighter(name="Opponent")
        stance = choose_stance(f, o)
        assert stance == Stance.DEFENSIVE

    def test_choose_stance_aggressive_fresh_strong(self):
        from combat_ai import choose_stance
        from combat_types import Stance
        f = self._make_fighter(mig=7)
        o = self._make_fighter(name="Opponent")
        # Ensure fighter is fresh with high HP and stamina
        stance = choose_stance(f, o)
        assert stance in (Stance.AGGRESSIVE, Stance.BALANCED, Stance.LOW_GUARD)

    def test_choose_stance_undead_no_retreat(self):
        from combat_ai import choose_stance
        from combat_types import Stance
        f = self._make_fighter(mig=6)
        f.is_undead = True
        f.hp = 2  # low HP — normally defensive
        o = self._make_fighter(name="Opponent")
        stance = choose_stance(f, o)
        # Undead with mig >= 6 should be aggressive regardless of HP
        assert stance == Stance.AGGRESSIVE

    def test_choose_maneuver_returns_valid(self):
        from combat_ai import choose_maneuver
        from combat_types import Maneuver
        random.seed(42)
        f = self._make_fighter()
        o = self._make_fighter(name="Opponent")
        maneuver = choose_maneuver(f, o)
        assert isinstance(maneuver, Maneuver)

    def test_choose_maneuver_prone_stands(self):
        from combat_ai import choose_maneuver
        from combat_types import Maneuver, ConditionType
        from combat_model import Condition
        f = self._make_fighter()
        f.conditions.append(Condition(ConditionType.PRONE, -1))
        o = self._make_fighter(name="Opponent")
        maneuver = choose_maneuver(f, o)
        assert maneuver == Maneuver.STAND

    def test_can_counter(self):
        from combat_ai import can_counter
        f = self._make_fighter()
        result = can_counter(f)
        assert isinstance(result, bool)

    def test_choose_grapple_followup(self):
        from combat_ai import choose_grapple_followup
        from combat_model import Fighter, GrappleState
        from combat_types import Maneuver, GrapplePosition
        random.seed(42)
        f = self._make_fighter()
        f.grapple_state = GrappleState(position=GrapplePosition.MOUNTED.value,
                                        dominant=f.name)
        o = self._make_fighter(name="Opponent")
        maneuver = choose_grapple_followup(f, o)
        assert isinstance(maneuver, Maneuver)


# =====================================================================
# TestTrauma — trauma.py
# =====================================================================

class TestTrauma:
    """Tests for trauma.py"""

    def _make_member(self, name="Kell Hook", wil=5):
        return {
            "name": name,
            "wil": wil,
            "hp": 30,
            "max_hp": 30,
            "status": "active",
        }

    def test_trauma_apply(self):
        from trauma import trauma_apply
        member = self._make_member()
        result = trauma_apply(member, event="Rolf killed", category="shield_brother_death",
                              tsp=8, current_day=100)
        assert result["target"] == "Kell Hook"
        assert result["effective_tsp"] > 0
        assert result["total_tsp"] > 0

    def test_trauma_apply_builds_profile(self):
        from trauma import trauma_apply
        member = self._make_member()
        trauma_apply(member, event="Battle", category="combat_exposure",
                     tsp=3, current_day=50)
        assert "psychological_profile" in member
        assert member["psychological_profile"]["tsp"] > 0

    def test_trauma_accumulation(self):
        from trauma import trauma_apply
        member = self._make_member()
        trauma_apply(member, event="Fight 1", category="combat_exposure",
                     tsp=3, current_day=10)
        tsp1 = member["psychological_profile"]["tsp"]
        trauma_apply(member, event="Fight 2", category="severe_combat",
                     tsp=5, current_day=20)
        assert member["psychological_profile"]["tsp"] > tsp1

    def test_trauma_condition_onset(self):
        from trauma import trauma_apply
        member = self._make_member(wil=3)  # low WIL = low threshold (9)
        result = trauma_apply(member, event="Horror", category="horror_sight",
                              tsp=12, current_day=100)
        # TSP 12 > threshold 9, so condition should manifest
        assert result["condition_manifested"] is not None

    def test_trauma_no_condition_below_threshold(self):
        from trauma import trauma_apply
        member = self._make_member(wil=8)  # high WIL = threshold 24
        result = trauma_apply(member, event="Minor", category="minor_shock",
                              tsp=1, current_day=10)
        assert result["condition_manifested"] is None

    def test_generate_trauma_id(self):
        from trauma import generate_trauma_id, _ensure_profile
        member = self._make_member()
        _ensure_profile(member)
        tid = generate_trauma_id(member)
        assert tid.startswith("t_")

    def test_severity_order(self):
        from trauma import SEVERITY_ORDER
        assert SEVERITY_ORDER == ["none", "mild", "moderate", "severe", "crippling"]

    def test_condition_types_defined(self):
        from trauma import CONDITION_TYPES
        assert len(CONDITION_TYPES) > 0
        assert "battle_shock" in CONDITION_TYPES
        assert "night_terrors" in CONDITION_TYPES

    def test_recovery_thresholds(self):
        from trauma import RECOVERY_RP_THRESHOLD
        # More severe conditions require more RP to recover
        assert RECOVERY_RP_THRESHOLD["mild"] < RECOVERY_RP_THRESHOLD["moderate"]
        assert RECOVERY_RP_THRESHOLD["moderate"] < RECOVERY_RP_THRESHOLD["severe"]
        assert RECOVERY_RP_THRESHOLD["severe"] < RECOVERY_RP_THRESHOLD["crippling"]

    def test_tsp_modifiers(self):
        from trauma import trauma_apply
        # Shield bond should reduce TSP
        member = self._make_member()
        result = trauma_apply(member, event="Fight", category="combat_exposure",
                              tsp=5, current_day=10, shield_bond_active=True)
        assert "Shield-bond: -2" in result["modifiers"]


# =====================================================================
# TestWounds — wounds.py
# =====================================================================

class TestWounds:
    """Tests for wounds.py"""

    def _make_member(self, name="Kell Hook"):
        return {
            "name": name,
            "hp": 30,
            "max_hp": 30,
            "status": "active",
            "wounds": [],
        }

    def test_wound_apply(self):
        from wounds import wound_apply
        member = self._make_member()
        wound = wound_apply(member, location="right_arm", severity="serious",
                            damage=9, weapon="bearded_axe", current_day=100)
        assert wound["id"] == "w_001"
        assert wound["severity"] == "serious"
        assert member["hp"] == 21  # 30 - 9

    def test_wound_reduces_hp(self):
        from wounds import wound_apply
        member = self._make_member()
        wound_apply(member, location="torso", severity="critical",
                    damage=15, weapon="sword", current_day=50)
        assert member["hp"] == 15

    def test_mortal_wound_sets_dying(self):
        from wounds import wound_apply
        member = self._make_member()
        wound_apply(member, location="torso", severity="mortal",
                    damage=25, weapon="great_sword", current_day=50)
        assert member["status"] == "dying"

    def test_wound_description_generated(self):
        from wounds import wound_apply
        member = self._make_member()
        wound = wound_apply(member, location="head", severity="light",
                            damage=4, weapon="hand_axe", current_day=10)
        assert wound["description"]
        assert len(wound["description"]) > 10

    def test_determine_sublocation(self):
        from wounds import determine_sublocation, SUBLOCATION_TABLE
        for location in SUBLOCATION_TABLE:
            random.seed(42)
            sub = determine_sublocation(location)
            assert isinstance(sub, str)
            assert len(sub) > 0

    def test_wound_bleeding_by_severity(self):
        from wounds import wound_apply, BLEEDING_RATE
        member = self._make_member()
        wound = wound_apply(member, location="right_arm", severity="serious",
                            damage=8, weapon="spear", current_day=50)
        assert wound["bleeding"] == BLEEDING_RATE["serious"]

    def test_wound_treat(self):
        from wounds import wound_apply, wound_treat
        member = self._make_member()
        wound = wound_apply(member, location="right_arm", severity="serious",
                            damage=9, weapon="bearded_axe", current_day=100)
        random.seed(42)
        result = wound_treat(member, wound["id"], "field_surgery",
                             healer_name="Dalla", healer_wit=6, healer_heal_skill=3)
        assert "wound_id" in result

    def test_multiple_wounds(self):
        from wounds import wound_apply
        member = self._make_member()
        w1 = wound_apply(member, location="right_arm", severity="light",
                          damage=3, weapon="seax", current_day=10)
        w2 = wound_apply(member, location="left_arm", severity="serious",
                          damage=8, weapon="sword", current_day=10)
        assert len(member["wounds"]) == 2
        assert w1["id"] != w2["id"]

    def test_generate_wound_id_unique(self):
        from wounds import generate_wound_id
        member = {"name": "Test", "wounds": [{"id": "w_001"}, {"id": "w_002"}]}
        wid = generate_wound_id(member)
        assert wid == "w_003"

    def test_compute_pain_level(self):
        from wounds import compute_pain_level, PAIN_LEVELS
        wound = {
            "severity": "serious",
            "healing_stage": "fresh",
            "treated": False,
            "infection_stage": "none",
        }
        pain = compute_pain_level(wound)
        assert pain in PAIN_LEVELS

    def test_compute_overall_pain(self):
        from wounds import compute_overall_pain, PAIN_LEVELS
        member = {
            "wounds": [
                {"severity": "light", "healing_stage": "fresh",
                 "treated": False, "infection_stage": "none", "resolved": False},
                {"severity": "serious", "healing_stage": "fresh",
                 "treated": False, "infection_stage": "none", "resolved": False},
            ]
        }
        pain = compute_overall_pain(member)
        assert pain in PAIN_LEVELS

    def test_severity_order(self):
        from wounds import SEVERITY_ORDER
        assert SEVERITY_ORDER == ["none", "scratch", "light", "serious", "critical", "mortal"]

    def test_healing_stages(self):
        from wounds import STAGES
        assert STAGES == ["fresh", "clotting", "closing", "knitting", "scarring", "healed"]
