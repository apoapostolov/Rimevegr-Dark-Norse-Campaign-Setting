import village_politics as vp


def _seed_state():
    return {
        "current_date": {"day_of_year": 10},
        "economies": {
            "Frostfjord Hollow": {
                "crop_fields": 0,
                "livestock": {"sheep": 0, "goats": 0, "cattle": 0, "pigs": 0},
                "food_stores_days": 0,
                "food_stores_max": 50,
                "silver_treasury": 20,
                "weekly_trade_income": 5,
                "weekly_expenses": 1,
                "labor_allocation": {
                    "farming": 0.0,
                    "building": 0.1,
                    "defense": 0.2,
                    "crafting": 0.4,
                    "idle": 0.3,
                },
            }
        },
        "demographics": {
            "Frostfjord Hollow": {
                "children": 0,
                "elderly": 0,
                "women_working": 3,
                "men_working": 4,
                "fighters": 1,
                "total": 7,
            }
        },
        "feuds": [],
    }


def test_economy_tick_bootstraps_runtime_fields(monkeypatch):
    state = _seed_state()

    monkeypatch.setattr(
        vp,
        "load_detailed_economies",
        lambda: {
            "Frostfjord Hollow": {
                "production": [
                    {"good": "dried_cod", "quantity_weekly": "medium"},
                    {"good": "rope", "quantity_weekly": "low"},
                ],
                "strategic_resources": [{"resource": "deep-water harbour"}],
                "trade_routes": [],
                "imports": [],
                "exports": [],
            }
        },
    )
    monkeypatch.setattr(
        vp,
        "load_settlements",
        lambda: {
            "settlements": [
                {
                    "name": "Frostfjord Hollow",
                    "defensibility": 2,
                    "structures": {
                        "storage": {"granaries": 1, "root_cellars": 2, "storehouses": 1},
                        "productive": {"fish_sheds": 1, "smithies": 1},
                    },
                }
            ]
        },
    )
    monkeypatch.setattr(vp, "load_routes", lambda: {})

    result = vp.economy_tick_week(state, "Frostfjord Hollow")
    econ = state["economies"]["Frostfjord Hollow"]

    assert result["produced_goods"]["dried_cod"] == 5.0
    assert econ["commodity_stocks"]["dried_cod"] >= 15.0
    assert econ["stock_buckets"]["food"] >= 15.0
    assert "deep_water_harbour" in econ["strategic_resource_flags"]
    assert econ["stock_capacities"]["food"] > 0


def test_food_goods_production_increases_food_stores(monkeypatch):
    state = _seed_state()

    monkeypatch.setattr(
        vp,
        "load_detailed_economies",
        lambda: {
            "Frostfjord Hollow": {
                "production": [{"good": "dried_cod", "quantity_weekly": "medium"}],
                "strategic_resources": [],
                "trade_routes": [],
                "imports": [],
                "exports": [],
            }
        },
    )
    monkeypatch.setattr(
        vp,
        "load_settlements",
        lambda: {
            "settlements": [
                {
                    "name": "Frostfjord Hollow",
                    "defensibility": 1,
                    "structures": {"storage": {"granaries": 1}, "productive": {"fish_sheds": 1}},
                }
            ]
        },
    )
    monkeypatch.setattr(vp, "load_routes", lambda: {})

    result = vp.economy_tick_week(state, "Frostfjord Hollow")

    assert result["food_produced"] > 0
    assert state["economies"]["Frostfjord Hollow"]["food_stores_days"] > 0


def test_essential_food_import_failure_sets_shortage_flags(monkeypatch):
    state = _seed_state()
    state["economies"]["Frostfjord Hollow"]["food_stores_days"] = 20
    state["current_date"]["day_of_year"] = 200

    monkeypatch.setattr(
        vp,
        "load_detailed_economies",
        lambda: {
            "Frostfjord Hollow": {
                "production": [],
                "strategic_resources": [],
                "trade_routes": [],
                "imports": [{"good": "grain", "urgency": "high"}],
                "exports": [],
                "wartime_impact": {"essential_imports_at_risk": ["grain"]},
                "economic_vulnerabilities": ["Single trade road easily blockaded"],
            }
        },
    )
    monkeypatch.setattr(
        vp,
        "load_settlements",
        lambda: {
            "settlements": [
                {"name": "Frostfjord Hollow", "defensibility": 1, "structures": {"storage": {"granaries": 1}}}
            ]
        },
    )
    monkeypatch.setattr(vp, "load_routes", lambda: {})

    result = vp.economy_tick_week(state, "Frostfjord Hollow")
    econ = state["economies"]["Frostfjord Hollow"]

    assert result["dependency_health"] < 1.0
    assert econ["unmet_imports"][0]["good"] == "grain"
    assert any(flag.startswith("food_shortage:grain") for flag in econ["shortage_flags"])
    assert "vulnerability:blockade_chokepoint" in econ["shortage_flags"]
    assert result["food_shortfall_days"] > 0


def test_material_import_failure_penalizes_repair_and_readiness(monkeypatch):
    state = _seed_state()
    state["economies"]["Frostfjord Hollow"]["commodity_stocks"] = {"timber": 0.0}
    state["economies"]["Frostfjord Hollow"]["stock_buckets"] = {"food": 0.0, "materials": 0.0, "trade": 0.0}
    state["current_date"]["day_of_year"] = 200

    monkeypatch.setattr(
        vp,
        "load_detailed_economies",
        lambda: {
            "Frostfjord Hollow": {
                "production": [],
                "strategic_resources": [],
                "trade_routes": [],
                "imports": [{"good": "timber", "urgency": "high"}],
                "exports": [],
                "wartime_impact": {"essential_imports_at_risk": ["timber"]},
                "economic_vulnerabilities": ["Palisade repairs impossible without wood imports"],
            }
        },
    )
    monkeypatch.setattr(
        vp,
        "load_settlements",
        lambda: {
            "settlements": [
                {"name": "Frostfjord Hollow", "defensibility": 2, "structures": {"storage": {"storehouses": 1}}}
            ]
        },
    )
    monkeypatch.setattr(vp, "load_routes", lambda: {})

    result = vp.economy_tick_week(state, "Frostfjord Hollow")
    econ = state["economies"]["Frostfjord Hollow"]

    assert econ["repair_capacity_penalty"] >= 1
    assert econ["military_readiness_penalty"] >= 1
    assert any(flag.startswith("repair_shortage:timber") for flag in econ["shortage_flags"])
    assert any(flag.startswith("readiness_shortage:timber") for flag in econ["shortage_flags"])
    assert result["silver_out"] > state["economies"]["Frostfjord Hollow"]["weekly_expenses"]


def test_route_disruption_reduces_liquidity_and_marks_partner_loss(monkeypatch):
    state = _seed_state()
    state["current_date"]["day_of_year"] = 200

    monkeypatch.setattr(
        vp,
        "load_detailed_economies",
        lambda: {
            "Frostfjord Hollow": {
                "production": [],
                "strategic_resources": [],
                "trade_routes": [
                    {"to": "Ashen Reach", "route_id": "RTE_001", "frequency": "weekly"},
                    {"to": "Skaldhaven", "route_id": "RTE_002", "frequency": "monthly"},
                ],
                "imports": [],
                "exports": [{"good": "dried_cod", "destinations": ["Ashen Reach"], "volume": "high"}],
                "market": {
                    "market_day": "every Thorsdag",
                    "stall_count": 2,
                    "visiting_traders": "occasional",
                    "price_modifier": 1.1,
                },
            },
            "Skaldhaven": {},
            "Ashen Reach": {},
        },
    )
    monkeypatch.setattr(
        vp,
        "load_settlements",
        lambda: {
            "settlements": [
                {"name": "Frostfjord Hollow", "defensibility": 2, "structures": {"storage": {"storehouses": 1}}}
            ]
        },
    )
    monkeypatch.setattr(
        vp,
        "load_routes",
        lambda: {
            "RTE_001": {"id": "RTE_001", "to_settlement": "Ashen Reach", "seasonal_access": {"winter": "closed"}, "trade_traffic": "low"},
            "RTE_002": {"id": "RTE_002", "to_settlement": "Skaldhaven", "seasonal_access": {"winter": "dangerous"}, "trade_traffic": "low"},
        },
    )
    state["feuds"] = [{"pair": ["Frostfjord Hollow", "Ashen Reach"], "level": 2}]

    result = vp.economy_tick_week(state, "Frostfjord Hollow")
    econ = state["economies"]["Frostfjord Hollow"]

    assert result["market_liquidity"] < 1.0
    assert result["local_price_pressure"] > 1.0
    assert "Ashen Reach" in econ["route_partner_losses"]
    assert any(flag.startswith("route_access:RTE_001:closed") for flag in econ["route_disruption_flags"])
    assert any(flag.startswith("route_feud_drag:RTE_001") for flag in econ["route_disruption_flags"])


def test_union_tribute_moves_mixed_dues_into_union_treasury(monkeypatch):
    state = {
        "current_date": {"day_of_year": 200},
        "economies": {
            "Grimholt": {
                "crop_fields": 0,
                "livestock": {"sheep": 10},
                "food_stores_days": 100,
                "food_stores_max": 200,
                "silver_treasury": 20,
                "weekly_trade_income": 0,
                "weekly_expenses": 0,
                "labor_allocation": {"farming": 0.3, "building": 0.1, "defense": 0.3, "crafting": 0.2, "idle": 0.1},
            },
            "Raven's Perch": {
                "crop_fields": 0,
                "livestock": {"sheep": 5},
                "food_stores_days": 40,
                "food_stores_max": 80,
                "silver_treasury": 12,
                "weekly_trade_income": 0,
                "weekly_expenses": 0,
                "labor_allocation": {"farming": 0.4, "building": 0.1, "defense": 0.2, "crafting": 0.1, "idle": 0.2},
            },
            "Moor's End": {
                "crop_fields": 0,
                "livestock": {"sheep": 6},
                "food_stores_days": 35,
                "food_stores_max": 50,
                "silver_treasury": 6,
                "weekly_trade_income": 0,
                "weekly_expenses": 0,
                "labor_allocation": {"farming": 0.5, "building": 0.1, "defense": 0.1, "crafting": 0.1, "idle": 0.2},
                "stock_buckets": {"food": 0.0, "materials": 4.0, "trade": 0.0},
            },
        },
        "demographics": {
            "Grimholt": {"children": 0, "elderly": 0, "women_working": 5, "men_working": 5, "fighters": 8, "total": 10},
            "Raven's Perch": {"children": 0, "elderly": 0, "women_working": 4, "men_working": 4, "fighters": 3, "total": 8},
            "Moor's End": {"children": 0, "elderly": 0, "women_working": 3, "men_working": 3, "fighters": 2, "total": 6},
        },
        "unions": [
            {
                "name": "The Iron Grip",
                "seat": "Grimholt",
                "type": "military",
                "war_readiness": 2,
                "dark_arts_level": 0,
                "members": [
                    {"settlement": "Grimholt", "role": "core", "tribute_silver_weekly": 0},
                    {
                        "settlement": "Raven's Perch",
                        "role": "subordinate",
                        "tribute_silver_monthly_campaign_season": 6,
                        "tribute_silver_seasonal": 18,
                        "tribute_goods_note": "winter stores and lookout service demanded when Ordovast readies a march",
                    },
                    {
                        "settlement": "Moor's End",
                        "role": "tributary",
                        "tribute_silver_seasonal": 4,
                        "tribute_livestock_monthly": 1,
                        "tribute_goods_note": "peat carts and labor service when called",
                    },
                ],
            }
        ],
        "feuds": [],
    }

    monkeypatch.setattr(vp, "load_detailed_economies", lambda: {})
    monkeypatch.setattr(vp, "load_settlements", lambda: {"settlements": []})

    reports = vp.apply_union_economy_week(state)
    union = state["unions"][0]

    assert reports[0]["weekly_tribute_in_silver"] > 0
    assert union["weekly_tribute_in_food"] > 0
    assert union["weekly_tribute_in_materials"] > 0
    assert state["economies"]["Raven's Perch"]["union_tribute_paid_silver"] > 0
    assert state["economies"]["Moor's End"]["union_tribute_paid_materials"] > 0
    assert union["seat_support_cost_food"] > 0


def test_union_levy_and_trade_bonus_create_real_member_costs(monkeypatch):
    state = {
        "current_date": {"day_of_year": 50},
        "economies": {
            "Deepholm": {
                "crop_fields": 0,
                "livestock": {"sheep": 10},
                "food_stores_days": 200,
                "food_stores_max": 300,
                "silver_treasury": 50,
                "weekly_trade_income": 0,
                "weekly_expenses": 0,
                "labor_allocation": {"farming": 0.3, "building": 0.1, "defense": 0.2, "crafting": 0.3, "idle": 0.1},
            },
            "Thornwall": {
                "crop_fields": 0,
                "livestock": {"sheep": 20},
                "food_stores_days": 120,
                "food_stores_max": 160,
                "silver_treasury": 30,
                "weekly_trade_income": 8,
                "weekly_expenses": 0,
                "labor_allocation": {"farming": 0.5, "building": 0.1, "defense": 0.2, "crafting": 0.1, "idle": 0.1},
            },
            "Kolvik": {
                "crop_fields": 0,
                "livestock": {"sheep": 8},
                "food_stores_days": 110,
                "food_stores_max": 140,
                "silver_treasury": 20,
                "weekly_trade_income": 12,
                "weekly_expenses": 0,
                "market_liquidity": 1.2,
                "labor_allocation": {"farming": 0.4, "building": 0.1, "defense": 0.1, "crafting": 0.3, "idle": 0.1},
            },
        },
        "demographics": {
            "Deepholm": {"children": 0, "elderly": 0, "women_working": 10, "men_working": 10, "fighters": 6, "total": 20},
            "Thornwall": {"children": 0, "elderly": 0, "women_working": 7, "men_working": 7, "fighters": 5, "total": 14},
            "Kolvik": {"children": 0, "elderly": 0, "women_working": 6, "men_working": 6, "fighters": 3, "total": 12},
        },
        "unions": [
            {
                "name": "The Fjord Compact",
                "seat": "Deepholm",
                "type": "economic",
                "war_readiness": 1,
                "dark_arts_level": 0,
                "members": [
                    {"settlement": "Deepholm", "role": "core", "tribute_silver_weekly": 0},
                    {"settlement": "Thornwall", "role": "ally", "tribute_silver_weekly": 0, "levy_fighters": 15},
                    {"settlement": "Kolvik", "role": "partner", "tribute_silver_weekly": 0, "trade_bonus": 1.1},
                ],
            }
        ],
        "feuds": [],
    }

    monkeypatch.setattr(vp, "load_detailed_economies", lambda: {})
    monkeypatch.setattr(vp, "load_settlements", lambda: {"settlements": []})

    vp.apply_union_economy_week(state)
    union = state["unions"][0]

    assert union["weekly_levy_fighters"] == 15
    assert state["economies"]["Thornwall"]["union_levy_cost_silver"] > 0
    assert state["economies"]["Kolvik"]["union_trade_bonus_silver"] > 0
    assert union["weekly_trade_dues_silver"] > 0
    assert union["treasury_silver"] >= 0


def test_dark_arts_and_whisper_agents_hit_confidence_and_treasury(monkeypatch):
    state = {
        "current_date": {"day_of_year": 140},
        "economies": {
            "Ashen Reach": {
                "crop_fields": 0,
                "livestock": {"sheep": 6},
                "food_stores_days": 120,
                "food_stores_max": 160,
                "silver_treasury": 30,
                "weekly_trade_income": 10,
                "weekly_expenses": 0,
                "market_liquidity": 1.0,
                "local_price_pressure": 1.0,
                "labor_allocation": {"farming": 0.4, "building": 0.1, "defense": 0.1, "crafting": 0.3, "idle": 0.1},
            },
            "Deepholm": {
                "crop_fields": 0,
                "livestock": {"sheep": 6},
                "food_stores_days": 140,
                "food_stores_max": 200,
                "silver_treasury": 40,
                "weekly_trade_income": 12,
                "weekly_expenses": 0,
                "market_liquidity": 1.0,
                "local_price_pressure": 1.0,
                "labor_allocation": {"farming": 0.4, "building": 0.1, "defense": 0.1, "crafting": 0.3, "idle": 0.1},
            },
            "Grimholt": {
                "crop_fields": 0,
                "livestock": {"sheep": 6},
                "food_stores_days": 140,
                "food_stores_max": 200,
                "silver_treasury": 40,
                "weekly_trade_income": 12,
                "weekly_expenses": 0,
                "market_liquidity": 1.0,
                "local_price_pressure": 1.0,
                "labor_allocation": {"farming": 0.4, "building": 0.1, "defense": 0.1, "crafting": 0.3, "idle": 0.1},
            },
        },
        "demographics": {
            "Ashen Reach": {"children": 0, "elderly": 0, "women_working": 6, "men_working": 6, "fighters": 3, "total": 12},
            "Deepholm": {"children": 0, "elderly": 0, "women_working": 6, "men_working": 6, "fighters": 3, "total": 12},
            "Grimholt": {"children": 0, "elderly": 0, "women_working": 6, "men_working": 6, "fighters": 3, "total": 12},
        },
        "unions": [
            {
                "name": "The Whispering Circle",
                "seat": "Ashen Reach",
                "type": "covert",
                "war_readiness": 1,
                "dark_arts_level": 2,
                "treasury_silver": 5.0,
                "dark_arts_practitioners": [
                    {"name": "The Cave-Woman", "health": "deteriorating"},
                    {"name": "Grim", "health": "deteriorating"},
                ],
                "whisper_agents": [
                    {"location": "Deepholm", "quality": 3, "cover": "Wandering healer"},
                    {"location": "Grimholt", "quality": 2, "cover": "Iron-ore trader"},
                ],
                "members": [{"settlement": "Ashen Reach", "role": "core", "tribute_silver_weekly": 0}],
            }
        ],
        "feuds": [],
    }

    monkeypatch.setattr(vp, "load_detailed_economies", lambda: {})
    monkeypatch.setattr(vp, "load_settlements", lambda: {"settlements": []})

    reports = vp.apply_dark_arts_economy_week(state)
    union = state["unions"][0]

    assert reports[0]["dark_arts_upkeep_silver"] > 0
    assert reports[0]["smuggling_income_silver"] > 0
    assert union["confidence_shock_targets"] == ["Deepholm", "Grimholt"]
    assert state["economies"]["Ashen Reach"]["local_price_pressure"] > 1.0
    assert state["economies"]["Deepholm"]["market_liquidity"] < 1.0
    assert any(flag.startswith("whisper_pressure:the_whispering_circle") for flag in state["economies"]["Grimholt"]["covert_flags"])


def test_wolfshead_bands_create_outlaw_pressure_and_trade_drag(monkeypatch):
    state = {
        "current_date": {"day_of_year": 220},
        "economies": {
            "Ashmark": {
                "crop_fields": 0,
                "livestock": {"sheep": 4},
                "food_stores_days": 90,
                "food_stores_max": 120,
                "silver_treasury": 20,
                "weekly_trade_income": 6,
                "weekly_expenses": 0,
                "market_liquidity": 1.0,
                "local_price_pressure": 1.0,
                "labor_allocation": {"farming": 0.5, "building": 0.1, "defense": 0.1, "crafting": 0.2, "idle": 0.1},
            },
            "Vargheim": {
                "crop_fields": 0,
                "livestock": {"sheep": 4},
                "food_stores_days": 100,
                "food_stores_max": 140,
                "silver_treasury": 25,
                "weekly_trade_income": 8,
                "weekly_expenses": 0,
                "market_liquidity": 1.0,
                "local_price_pressure": 1.0,
                "labor_allocation": {"farming": 0.5, "building": 0.1, "defense": 0.1, "crafting": 0.2, "idle": 0.1},
            },
        },
        "demographics": {
            "Ashmark": {"children": 0, "elderly": 0, "women_working": 4, "men_working": 4, "fighters": 2, "total": 8},
            "Vargheim": {"children": 0, "elderly": 0, "women_working": 4, "men_working": 4, "fighters": 2, "total": 8},
        },
        "unions": [],
        "feuds": [],
    }

    monkeypatch.setattr(
        vp,
        "load_wolfshead_bands",
        lambda: [
            {
                "id": "WOLF_001",
                "name": "The Burnt Charter",
                "size": 14,
                "threat_tier": 2,
                "territory": "Southern Black Pine, between Ashmark and the Beinvegr ridge",
                "survival_strategy": "toll-taking on the Beinvegr, escort work for smugglers avoiding Frostfjord tolls, occasional poaching",
                "narrative_hook": "",
                "winter_strategy": "",
                "notes": "",
            },
            {
                "id": "WOLF_003",
                "name": "Grimketil's Hold",
                "size": 25,
                "threat_tier": 3,
                "territory": "Deep Black Pine, roughly ten kilometres north-east of Vargheim",
                "survival_strategy": "protection racket on isolated farmsteads, smuggling goods between settlements avoiding toll stations",
                "narrative_hook": "",
                "winter_strategy": "",
                "notes": "",
            },
        ],
    )

    reports = vp.apply_wolfshead_economy_week(state)

    assert len(reports) == 2
    assert state["economies"]["Ashmark"]["outlaw_pressure"] >= 1
    assert state["economies"]["Vargheim"]["outlaw_pressure"] >= 1
    assert state["economies"]["Ashmark"]["night_market_chance"] > 0
    assert state["economies"]["Vargheim"]["market_liquidity"] < 1.0
    assert any(flag.startswith("wolfshead:WOLF_003") for flag in state["economies"]["Vargheim"]["wolfshead_pressure_flags"])
    assert state["wolfshead_state"]["WOLF_003"]["mercenary_competition"] > 0


def test_contract_market_builds_budgeted_offers_from_economy_pressure(monkeypatch):
    state = {
        "current_date": {"year": 312, "day_of_year": 210},
        "economies": {
            "Kolvik": {
                "crop_fields": 0,
                "livestock": {"sheep": 4},
                "food_stores_days": 90,
                "food_stores_max": 120,
                "silver_treasury": 80,
                "weekly_trade_income": 8,
                "weekly_expenses": 0,
                "market_liquidity": 0.9,
                "local_price_pressure": 1.25,
                "dependency_health": 0.8,
                "outlaw_pressure": 3,
                "labor_allocation": {"farming": 0.4, "building": 0.1, "defense": 0.1, "crafting": 0.3, "idle": 0.1},
            }
        },
        "demographics": {
            "Kolvik": {"children": 0, "elderly": 0, "women_working": 4, "men_working": 4, "fighters": 2, "total": 8}
        },
        "unions": [],
        "feuds": [{"pair": ["Kolvik", "Grimholt"], "level": 2}],
    }

    monkeypatch.setattr(
        vp,
        "load_contracts",
        lambda: [
            {
                "id": "CONT_A",
                "title": "Guard the Harbour",
                "type": "guard",
                "settlement": "Kolvik",
                "season": "winter",
                "year_range": [312, 314],
                "payment_silver": 55,
                "advance_silver": 10,
                "political_conditions": {"requires_feud_max": 2},
            },
            {
                "id": "CONT_B",
                "title": "Escort Salt Cargo",
                "type": "escort",
                "settlement": "Kolvik",
                "season": "winter",
                "year_range": [312, 314],
                "payment_silver": 35,
                "advance_silver": 5,
                "political_conditions": {"requires_feud_max": 3},
            },
        ],
    )

    reports = vp.apply_contract_market_week(state)
    market = state["contract_market"]["by_settlement"]["Kolvik"]

    assert reports[0]["offer_count"] >= 1
    assert market["issuer_budget_silver"] > 0
    assert market["payout_capacity_silver"] > 0
    assert "outlaw_demand" in market["pressure_tags"]
    assert "route_stress" in market["pressure_tags"]
    assert market["visible_offers"][0]["id"] == "CONT_A"


def test_activate_and_resolve_contract_mutates_budget_and_settlement_state(monkeypatch):
    state = {
        "current_date": {"year": 312, "day_of_year": 210},
        "economies": {
            "Kolvik": {
                "crop_fields": 0,
                "livestock": {"sheep": 4},
                "food_stores_days": 90,
                "food_stores_max": 120,
                "silver_treasury": 80,
                "weekly_trade_income": 8,
                "weekly_expenses": 0,
                "market_liquidity": 0.9,
                "local_price_pressure": 1.2,
                "outlaw_pressure": 3,
                "labor_allocation": {"farming": 0.4, "building": 0.1, "defense": 0.1, "crafting": 0.3, "idle": 0.1},
            }
        },
        "demographics": {
            "Kolvik": {"children": 0, "elderly": 0, "women_working": 4, "men_working": 4, "fighters": 2, "total": 8}
        },
        "unions": [],
        "feuds": [],
        "event_log": [],
        "contract_market": {
            "by_settlement": {
                "Kolvik": {
                    "advance_capacity_silver": 15.0,
                    "payout_capacity_silver": 30.0,
                    "contract_value_locked_silver": 0.0,
                    "visible_offers": [],
                }
            },
            "active_contracts": [],
        },
    }

    monkeypatch.setattr(
        vp,
        "load_contracts",
        lambda: [
            {
                "id": "CONT_A",
                "title": "Guard the Harbour",
                "type": "guard",
                "settlement": "Kolvik",
                "payment_silver": 55,
                "advance_silver": 10,
                "duration_days": 14,
            }
        ],
    )

    activated = vp.activate_contract(state, "CONT_A")
    assert activated["status"] == "active"
    assert state["economies"]["Kolvik"]["silver_treasury"] == 70

    resolved = vp.resolve_contract(state, "CONT_A", "success")
    assert resolved["outcome"] == "success"
    assert state["economies"]["Kolvik"]["silver_treasury"] == 25
    assert state["economies"]["Kolvik"]["outlaw_pressure"] == 2
    assert state["contract_market"]["active_contracts"][0]["status"] == "success"


def test_runtime_view_builds_union_wolfshead_and_contract_layers(monkeypatch):
    state = {
        "current_date": {"year": 312, "day_of_year": 220, "season": "Deep Dark"},
        "economies": {
            "Kolvik": {
                "crop_fields": 0,
                "livestock": {"sheep": 4},
                "food_stores_days": 90,
                "food_stores_max": 120,
                "silver_treasury": 80,
                "weekly_trade_income": 8,
                "weekly_expenses": 0,
                "market_liquidity": 1.0,
                "local_price_pressure": 1.0,
                "labor_allocation": {"farming": 0.4, "building": 0.1, "defense": 0.1, "crafting": 0.3, "idle": 0.1},
            },
            "Deepholm": {
                "crop_fields": 0,
                "livestock": {"sheep": 4},
                "food_stores_days": 120,
                "food_stores_max": 160,
                "silver_treasury": 120,
                "weekly_trade_income": 20,
                "weekly_expenses": 0,
                "market_liquidity": 1.0,
                "local_price_pressure": 1.0,
                "labor_allocation": {"farming": 0.3, "building": 0.1, "defense": 0.1, "crafting": 0.4, "idle": 0.1},
            },
        },
        "demographics": {
            "Kolvik": {"children": 0, "elderly": 0, "women_working": 4, "men_working": 4, "fighters": 2, "total": 8},
            "Deepholm": {"children": 0, "elderly": 0, "women_working": 5, "men_working": 5, "fighters": 3, "total": 10},
        },
        "unions": [
            {
                "name": "The Fjord Compact",
                "seat": "Deepholm",
                "type": "economic",
                "war_readiness": 1,
                "dark_arts_level": 0,
                "members": [
                    {"settlement": "Deepholm", "role": "core", "tribute_silver_weekly": 0},
                    {"settlement": "Kolvik", "role": "partner", "tribute_silver_weekly": 0, "trade_bonus": 1.1},
                ],
            }
        ],
        "feuds": [],
    }

    monkeypatch.setattr(
        vp,
        "load_wolfshead_bands",
        lambda: [
            {
                "id": "WOLF_003",
                "name": "Grimketil's Hold",
                "size": 25,
                "threat_tier": 3,
                "territory": "Deep Black Pine, roughly ten kilometres north-east of Kolvik",
                "survival_strategy": "protection racket and smuggling",
                "narrative_hook": "",
                "winter_strategy": "",
                "notes": "",
            }
        ],
    )
    monkeypatch.setattr(
        vp,
        "load_contracts",
        lambda: [
            {
                "id": "CONT_A",
                "title": "Guard the Harbour",
                "type": "guard",
                "settlement": "Kolvik",
                "season": "winter",
                "year_range": [312, 314],
                "payment_silver": 55,
                "advance_silver": 10,
                "political_conditions": {"requires_feud_max": 2},
            }
        ],
    )

    view = vp.build_runtime_view_state(state)

    assert "The Fjord Compact" == view["unions"][0]["name"]
    assert view["unions"][0]["weekly_trade_dues_silver"] > 0
    assert view["wolfshead_state"]["WOLF_003"]["weekly_income_silver"] > 0
    assert view["contract_market"]["by_settlement"]["Kolvik"]["offer_count"] == 1


def test_print_helpers_surface_new_runtime_sections(capsys, monkeypatch):
    state = {
        "current_date": {"year": 312, "day_of_year": 220, "season": "Deep Dark"},
        "economies": {
            "Kolvik": {
                "crop_fields": 0,
                "livestock": {"sheep": 4},
                "food_stores_days": 90,
                "food_stores_max": 120,
                "silver_treasury": 80,
                "weekly_trade_income": 8,
                "weekly_expenses": 0,
                "market_liquidity": 1.0,
                "local_price_pressure": 1.0,
                "labor_allocation": {"farming": 0.4, "building": 0.1, "defense": 0.1, "crafting": 0.3, "idle": 0.1},
            },
            "Deepholm": {
                "crop_fields": 0,
                "livestock": {"sheep": 4},
                "food_stores_days": 120,
                "food_stores_max": 160,
                "silver_treasury": 120,
                "weekly_trade_income": 20,
                "weekly_expenses": 0,
                "market_liquidity": 1.0,
                "local_price_pressure": 1.0,
                "labor_allocation": {"farming": 0.3, "building": 0.1, "defense": 0.1, "crafting": 0.4, "idle": 0.1},
            },
        },
        "demographics": {
            "Kolvik": {"children": 0, "elderly": 0, "women_working": 4, "men_working": 4, "fighters": 2, "total": 8},
            "Deepholm": {"children": 0, "elderly": 0, "women_working": 5, "men_working": 5, "fighters": 3, "total": 10},
        },
        "unions": [
            {
                "name": "The Fjord Compact",
                "seat": "Deepholm",
                "type": "economic",
                "war_readiness": 1,
                "dark_arts_level": 0,
                "members": [
                    {"settlement": "Deepholm", "role": "core", "tribute_silver_weekly": 0},
                    {"settlement": "Kolvik", "role": "partner", "tribute_silver_weekly": 0, "trade_bonus": 1.1},
                ],
            }
        ],
        "feuds": [],
    }

    monkeypatch.setattr(
        vp,
        "load_wolfshead_bands",
        lambda: [
            {
                "id": "WOLF_003",
                "name": "Grimketil's Hold",
                "size": 25,
                "threat_tier": 3,
                "territory": "Deep Black Pine, roughly ten kilometres north-east of Kolvik",
                "survival_strategy": "protection racket and smuggling",
                "narrative_hook": "",
                "winter_strategy": "",
                "notes": "",
            }
        ],
    )
    monkeypatch.setattr(
        vp,
        "load_contracts",
        lambda: [
            {
                "id": "CONT_A",
                "title": "Guard the Harbour",
                "type": "guard",
                "settlement": "Kolvik",
                "season": "winter",
                "year_range": [312, 314],
                "payment_silver": 55,
                "advance_silver": 10,
                "political_conditions": {"requires_feud_max": 2},
            }
        ],
    )

    view = vp.build_runtime_view_state(state)
    vp.print_union_economy(view)
    vp.print_wolfshead(view, band_id="WOLF_003", settlement=None)
    vp.print_contract_market(view, settlement="Kolvik")
    output = capsys.readouterr().out

    assert "UNION ECONOMY" in output
    assert "WOLFSHEAD PRESSURE" in output
    assert "CONTRACT MARKET" in output
    assert "CONT_A" in output
