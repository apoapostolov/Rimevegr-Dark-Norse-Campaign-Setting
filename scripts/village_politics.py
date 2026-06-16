#!/usr/bin/env python3
"""
Iron Ledger — Village Politics Simulation

Simulates political relationships, village economies, population
dynamics, feuds, union mechanics, and the march toward regional
war across the Rimevegr settlements.

Rules: §18 of 20_SIMULATION_RULES.md
Lore:  references/political_villages.md
Data:  data/political_state.yaml, data/settlements.yaml

Usage:
    python village_politics.py status
    python village_politics.py union --name "The Iron Grip"
    python village_politics.py feuds
    python village_politics.py tick --week
    python village_politics.py tick --season
    python village_politics.py allthing
    python village_politics.py raid --from Grimholt --target Thornwall --force 20
    python village_politics.py economy --settlement Deepholm
    python village_politics.py demographics --settlement Grimholt
    python village_politics.py war-readiness
    python village_politics.py dark-arts --union "The Whispering Circle"
    python village_politics.py narrative --season 3
    python village_politics.py spoilers
    python village_politics.py spoilers --file 11_VILLAGES_AND_SETTLEMENTS.md
"""
from __future__ import annotations

import argparse
import copy
import glob
import json
import math
import os
import random
import sys
import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# --- Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
POLITICAL_STATE = DATA_DIR / "political_state.yaml"
SETTLEMENTS_FILE = DATA_DIR / "settlements.yaml"
DETAILED_ECONOMIES_FILE = DATA_DIR / "economy" / "settlement_economies.yaml"
ROUTES_FILE = DATA_DIR / "geography" / "routes.yaml"
WOLFSHEAD_BANDS_FILE = DATA_DIR / "wolfshead_bands.yaml"
CONTRACTS_DIR = DATA_DIR / "contracts"

sys.path.insert(0, str(SCRIPT_DIR))
from engine import resolve_check, compute_success_chance, roll_d100

# ============================================================
# Constants (from §18 of 20_SIMULATION_RULES.md)
# ============================================================

SEASON_FOOD_MOD = {
    "Long Summer": 1.0,
    "Early Dark": 0.3,
    "Deep Dark": 0.0,
    "Late Dark": 0.0,
}

SEASON_CONSUMPTION_MOD = {
    "Long Summer": 1.0,
    "Early Dark": 1.1,
    "Deep Dark": 1.2,
    "Late Dark": 1.3,
}

SEASON_BIRTH_MOD = {
    "Long Summer": 1.5,
    "Early Dark": 1.0,
    "Deep Dark": 0.8,
    "Late Dark": 0.8,
}

LIVESTOCK_FEED = {"sheep": 0.5, "goats": 0.3, "cattle": 1.5, "pigs": 1.0}
LIVESTOCK_BREED_RATE = {"sheep": 1.2, "goats": 1.5, "cattle": 0.8, "pigs": 2.0}

FEUD_LABELS = {0: "Cold", 1: "Tense", 2: "Hostile", 3: "Blood-feud", 4: "Vengeance"}
FEUD_TRADE_MOD = {0: 1.0, 1: 0.8, 2: 0.5, 3: 0.0, 4: 0.0}

COHESION_LABELS = {
    5: "Unified command",
    4: "Strong",
    3: "Functional",
    2: "Fragile",
    1: "Nominal",
}

WAR_LABELS = {
    0: "Peacetime",
    1: "Alert",
    2: "Mobilizing",
    3: "Ready",
    4: "Marching",
    5: "Total war",
}

DARK_LABELS = {
    0: "None",
    1: "Seidr consulted",
    2: "Curse-carving",
    3: "Veil-thinning",
    4: "Death-reading",
    5: "Invocation",
}

ROUTE_ACCESS_MOD = {
    "good": 1.0,
    "passable": 0.8,
    "dangerous": 0.45,
    "closed": 0.0,
    "unknown": 0.6,
}
TRAFFIC_MOD = {"none": 0.0, "low": 0.7, "moderate": 1.0, "high": 1.25}
FREQUENCY_MOD = {"weekly": 1.0, "fortnightly": 0.6, "monthly": 0.3}
IMPORT_URGENCY = {"high": 1.5, "medium": 1.0, "low": 0.5}
EXPORT_VOLUME = {"high": 1.4, "medium": 1.0, "low": 0.6}
FOOD_IMPORT_KEYS = {"grain", "cod", "fish", "mutton", "root", "vegetable", "meat"}
TRADER_VISIT_MOD = {"none": 0.45, "occasional": 0.7, "regular": 1.0, "frequent": 1.2}
PRODUCTION_UNITS = {"low": 2.0, "medium": 5.0, "high": 9.0}
GOODS_TO_FOOD_DAYS = {
    "dried_cod": 2.4,
    "salt_fish": 2.0,
    "grain": 2.6,
    "root_vegetables": 1.8,
    "mutton": 1.8,
    "dried_meat": 2.0,
    "ale": 0.8,
    "cheese": 1.6,
}


_DRY_RUN = False


def day_to_season(day: int) -> str:
    """Return season name for the given day of year (1-360)."""
    if 1 <= day <= 60:
        return "Long Summer"
    if 61 <= day <= 150:
        return "Early Dark"
    if 151 <= day <= 300:
        return "Deep Dark"
    return "Late Dark"


# ============================================================
# Data Loading / Saving
# ============================================================


def load_state() -> dict:
    with open(POLITICAL_STATE) as f:
        return yaml.safe_load(f)


def save_state(state: dict) -> None:
    if _DRY_RUN:
        return
    with open(POLITICAL_STATE, "w") as f:
        yaml.dump(state, f, default_flow_style=False, allow_unicode=True,
                  sort_keys=False, width=120)


def load_settlements() -> dict:
    with open(SETTLEMENTS_FILE) as f:
        return yaml.safe_load(f)


def load_detailed_economies() -> dict[str, Any]:
    with open(DETAILED_ECONOMIES_FILE) as f:
        data = yaml.safe_load(f)
    return {entry["settlement"]: entry for entry in data.get("settlement_economies", [])}


def load_routes() -> dict[str, Any]:
    with open(ROUTES_FILE) as f:
        data = yaml.safe_load(f)
    return {entry["id"]: entry for entry in data.get("routes", [])}


def load_wolfshead_bands() -> list[dict[str, Any]]:
    with open(WOLFSHEAD_BANDS_FILE) as f:
        data = yaml.safe_load(f)
    return data.get("wolfshead_bands", [])


def load_contracts() -> list[dict[str, Any]]:
    """Load all authored contracts from data/contracts."""
    contracts: list[dict[str, Any]] = []
    if not CONTRACTS_DIR.exists():
        return contracts
    for fpath in sorted(glob.glob(str(CONTRACTS_DIR / "*.yaml"))):
        with open(fpath, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        for contract in data.get("contracts", []):
            entry = dict(contract)
            entry["_source"] = os.path.basename(fpath)
            contracts.append(entry)
    return contracts


def _settlement_base_entry(name: str, settlements_data: dict | None = None) -> dict[str, Any]:
    """Return one settlement base entry from settlements.yaml."""
    settlements_data = settlements_data or load_settlements()
    for settlement in settlements_data.get("settlements", []):
        if settlement.get("name") == name:
            return settlement
    return {}


def log_event(state: dict, text: str) -> None:
    dt = state.get("current_date", {})
    entry = f"Y{dt.get('year',0)} D{dt.get('day_of_year',0)}: {text}"
    state.setdefault("event_log", []).append(entry)


def _seasonal_access_key(season: str) -> str:
    if season == "Long Summer":
        return "summer"
    if season == "Early Dark":
        return "autumn"
    if season == "Deep Dark":
        return "winter"
    return "spring"


def _normalize_key(text: str) -> str:
    return str(text).lower().replace("-", "_").replace(" ", "_")


def _good_bucket(good_name: str) -> str:
    """Map a good into a broad economy stock bucket."""
    key = _normalize_key(good_name)
    if any(token in key for token in ("cod", "fish", "grain", "vegetable", "meat", "mutton", "cheese", "ale", "honey")):
        return "food"
    if any(token in key for token in ("iron", "ore", "metal", "timber", "wood", "tar", "charcoal", "salt", "oil", "peat")):
        return "materials"
    return "trade"


def _food_days_from_goods(good_name: str, units: float) -> float:
    """Convert produced food goods into supplemental person-day value."""
    return GOODS_TO_FOOD_DAYS.get(_normalize_key(good_name), 0.0) * units


def _import_need_units(urgency: str) -> float:
    """Translate authored urgency into weekly dependency pressure."""
    return {"high": 3.0, "medium": 2.0, "low": 1.0}.get(str(urgency), 2.0)


def _is_food_good(good_name: str) -> bool:
    return _good_bucket(good_name) == "food"


def _resolve_import_shortages(
    econ: dict[str, Any],
    profile: dict[str, Any],
    route_effects: dict[str, Any],
) -> dict[str, Any]:
    """Resolve authored imports into unmet goods, shortages, and penalties."""
    imports = profile.get("imports", [])
    if not imports:
        return {
            "dependency_health": 1.0,
            "unmet_imports": [],
            "food_shortfall_days": 0.0,
            "silver_drag": 0.0,
            "repair_penalty": 0,
            "military_penalty": 0,
            "vulnerability_pressure": 0,
            "shortage_flags": [],
        }

    throughput_total = float(route_effects.get("throughput_total", 0.0))
    coverage_ratio = min(1.0, throughput_total / 1.2) if imports else 1.0
    essential_at_risk = {
        _normalize_key(item)
        for item in profile.get("wartime_impact", {}).get("essential_imports_at_risk", [])
    }
    commodity_stocks = econ.setdefault("commodity_stocks", {})
    stock_buckets = econ.setdefault("stock_buckets", {"food": 0.0, "materials": 0.0, "trade": 0.0})

    unmet_imports: list[dict[str, Any]] = []
    food_shortfall_days = 0.0
    silver_drag = 0.0
    repair_penalty = 0
    military_penalty = 0
    vulnerability_pressure = 0
    shortage_flags: list[str] = []
    total_need = 0.0
    satisfied_need = 0.0

    for item in imports:
        good_name = str(item.get("good", ""))
        if not good_name:
            continue
        urgency = str(item.get("urgency", "medium"))
        need_units = _import_need_units(urgency)
        total_need += need_units
        covered_units = need_units * coverage_ratio
        short_units = max(0.0, need_units - covered_units)
        bucket = _good_bucket(good_name)
        stock_cover = min(short_units, commodity_stocks.get(good_name, 0.0))
        if stock_cover > 0:
            commodity_stocks[good_name] = round(commodity_stocks.get(good_name, 0.0) - stock_cover, 1)
            stock_buckets[bucket] = round(max(0.0, stock_buckets.get(bucket, 0.0) - stock_cover), 1)
        short_units = max(0.0, short_units - stock_cover)
        satisfied_need += need_units - short_units

        if short_units <= 0.1:
            continue

        normalized = _normalize_key(good_name)
        essential = normalized in essential_at_risk or urgency == "high"
        unmet_imports.append(
            {
                "good": good_name,
                "urgency": urgency,
                "short_units": round(short_units, 1),
                "essential": essential,
            }
        )

        if _is_food_good(good_name):
            penalty = short_units * 1.1
            food_shortfall_days += penalty
            shortage_flags.append(f"food_shortage:{normalized}")
        else:
            drag = short_units * (1.4 if essential else 0.7)
            silver_drag += drag
            if any(token in normalized for token in ("iron", "timber", "tool", "nail", "charcoal")):
                repair_penalty += 1 if essential else 0
                shortage_flags.append(f"repair_shortage:{normalized}")
            if any(token in normalized for token in ("timber", "salt", "iron", "tar", "rope", "nail")):
                military_penalty += 1 if essential else 0
                shortage_flags.append(f"readiness_shortage:{normalized}")

        if essential:
            vulnerability_pressure += 1

    vulnerability_notes = " ".join(profile.get("economic_vulnerabilities", []))
    if vulnerability_pressure and vulnerability_notes:
        notes_lower = vulnerability_notes.lower()
        if "blockad" in notes_lower or "single trade road" in notes_lower or "chokepoint" in notes_lower:
            shortage_flags.append("vulnerability:blockade_chokepoint")
            vulnerability_pressure += 1
        if "smith" in notes_lower or "smelter" in notes_lower or "forge" in notes_lower:
            shortage_flags.append("vulnerability:repair_bottleneck")
        if "fire" in notes_lower or "arson" in notes_lower:
            shortage_flags.append("vulnerability:fire_chain")

    dependency_health = 1.0 if total_need <= 0 else max(0.0, min(1.0, satisfied_need / total_need))
    return {
        "dependency_health": round(dependency_health, 2),
        "unmet_imports": unmet_imports,
        "food_shortfall_days": round(food_shortfall_days, 1),
        "silver_drag": round(silver_drag, 1),
        "repair_penalty": repair_penalty,
        "military_penalty": military_penalty,
        "vulnerability_pressure": vulnerability_pressure,
        "shortage_flags": sorted(set(shortage_flags)),
    }


def _storage_capacities(base_entry: dict[str, Any]) -> dict[str, float]:
    """Estimate stock capacity from authored settlement structures."""
    structures = base_entry.get("structures", {})
    storage = structures.get("storage", {})
    productive = structures.get("productive", {})
    food_capacity = (
        storage.get("granaries", 0) * 30
        + storage.get("storehouses", 0) * 24
        + storage.get("root_cellars", 0) * 12
        + storage.get("smokehouses", 0) * 10
        + productive.get("fish_sheds", 0) * 8
    )
    material_capacity = (
        storage.get("storehouses", 0) * 18
        + productive.get("boathouses", 0) * 8
        + productive.get("jetties", 0) * 4
        + productive.get("smithies", 0) * 6
        + productive.get("work_sheds", 0) * 4
    )
    trade_capacity = max(8.0, storage.get("storehouses", 0) * 12 + base_entry.get("defensibility", 1) * 4)
    return {
        "food": max(12.0, float(food_capacity)),
        "materials": max(10.0, float(material_capacity)),
        "trade": float(trade_capacity),
    }


def _ensure_economy_runtime_fields(
    state: dict,
    settle_name: str,
    detailed_economies: dict[str, Any] | None = None,
    settlements_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Bootstrap richer economy runtime fields when missing."""
    detailed_economies = detailed_economies or load_detailed_economies()
    settlements_data = settlements_data or load_settlements()
    econ = state["economies"].setdefault(settle_name, {})
    profile = detailed_economies.get(settle_name, {})
    base_entry = _settlement_base_entry(settle_name, settlements_data)

    econ.setdefault("commodity_stocks", {})
    econ.setdefault("stock_buckets", {"food": 0.0, "materials": 0.0, "trade": 0.0})
    econ.setdefault("stock_capacities", _storage_capacities(base_entry))
    econ.setdefault("strategic_resource_flags", [])
    econ.setdefault("weekly_production_by_good", {})
    econ.setdefault("shortage_flags", [])
    econ.setdefault("unmet_imports", [])
    econ.setdefault("dependency_health", 1.0)
    econ.setdefault("repair_capacity_penalty", 0)
    econ.setdefault("military_readiness_penalty", 0)
    econ.setdefault("vulnerability_pressure", 0)
    econ.setdefault("market_liquidity", 1.0)
    econ.setdefault("local_price_pressure", 1.0)
    econ.setdefault("route_partner_losses", [])
    econ.setdefault("route_disruption_flags", [])
    econ.setdefault("union_tribute_paid_silver", 0.0)
    econ.setdefault("union_tribute_paid_food", 0.0)
    econ.setdefault("union_tribute_paid_materials", 0.0)
    econ.setdefault("union_support_burden_silver", 0.0)
    econ.setdefault("union_levy_cost_silver", 0.0)
    econ.setdefault("union_trade_bonus_silver", 0.0)
    econ.setdefault("union_trade_dues_silver", 0.0)
    econ.setdefault("union_livestock_tribute_progress", 0.0)
    econ.setdefault("union_membership", "")
    econ.setdefault("covert_fear_pressure", 0.0)
    econ.setdefault("confidence_shock_pressure", 0.0)
    econ.setdefault("smuggling_leak_silver", 0.0)
    econ.setdefault("covert_flags", [])
    econ.setdefault("outlaw_pressure", 0)
    econ.setdefault("night_market_chance", 0.0)
    econ.setdefault("wolfshead_tribute_drag_silver", 0.0)
    econ.setdefault("mercenary_competition_pressure", 0.0)
    econ.setdefault("wolfshead_pressure_flags", [])
    econ.setdefault("contract_offer_pressure", 0.0)
    econ.setdefault("contract_budget_pressure", 0.0)
    econ.setdefault("contract_market_tags", [])

    if profile.get("strategic_resources") and not econ["strategic_resource_flags"]:
        econ["strategic_resource_flags"] = [
            _normalize_key(resource.get("resource", ""))
            for resource in profile.get("strategic_resources", [])
            if resource.get("resource")
        ]

    if profile.get("production") and not econ["commodity_stocks"]:
        for production in profile.get("production", []):
            good_name = str(production.get("good", ""))
            units = PRODUCTION_UNITS.get(str(production.get("quantity_weekly", "medium")), 5.0) * 2
            bucket = _good_bucket(good_name)
            econ["commodity_stocks"][good_name] = round(units, 1)
            econ["stock_buckets"][bucket] = round(econ["stock_buckets"].get(bucket, 0.0) + units, 1)

    return econ


# ============================================================
# Economy Tick (Weekly) — §18.1
# ============================================================


def economy_tick_week(state: dict, settle_name: str) -> dict:
    """Advance one settlement's economy by one week. Returns change dict."""
    econ = state["economies"].get(settle_name, {})
    demo = state["demographics"].get(settle_name, {})
    if not econ or not demo:
        return {}

    season = day_to_season(state["current_date"]["day_of_year"])
    detailed_economies = load_detailed_economies()
    settlements_data = load_settlements()
    econ = _ensure_economy_runtime_fields(
        state,
        settle_name,
        detailed_economies=detailed_economies,
        settlements_data=settlements_data,
    )
    econ["union_tribute_paid_silver"] = 0.0
    econ["union_tribute_paid_food"] = 0.0
    econ["union_tribute_paid_materials"] = 0.0
    econ["union_support_burden_silver"] = 0.0
    econ["union_levy_cost_silver"] = 0.0
    econ["union_trade_bonus_silver"] = 0.0
    econ["union_trade_dues_silver"] = 0.0
    union = get_settlement_union(state, settle_name)
    econ["union_membership"] = union["name"] if union else ""
    routes = load_routes()
    route_effects = compute_route_throughput(state, settle_name, detailed_economies, routes)
    profile = detailed_economies.get(settle_name, {})
    shortage_effects = _resolve_import_shortages(econ, profile, route_effects)
    pop = demo["total"]
    labor = econ.get("labor_allocation", {})
    farm_ratio = labor.get("farming", 0.5)

    # Food production
    base_food = econ["crop_fields"] * 2.0  # 2 food units per field per week
    food_mod = SEASON_FOOD_MOD.get(season, 0.0)
    food_prod = base_food * food_mod * farm_ratio

    # Authored production by named good
    produced_goods: dict[str, float] = {}
    food_goods_bonus = 0.0
    stock_buckets = econ.setdefault("stock_buckets", {"food": 0.0, "materials": 0.0, "trade": 0.0})
    commodity_stocks = econ.setdefault("commodity_stocks", {})
    for production in profile.get("production", []):
        good_name = str(production.get("good", ""))
        units = PRODUCTION_UNITS.get(str(production.get("quantity_weekly", "medium")), 5.0)
        if not good_name:
            continue
        produced_goods[good_name] = round(units, 1)
        commodity_stocks[good_name] = round(commodity_stocks.get(good_name, 0.0) + units, 1)
        bucket = _good_bucket(good_name)
        stock_buckets[bucket] = round(stock_buckets.get(bucket, 0.0) + units, 1)
        if bucket == "food":
            food_goods_bonus += _food_days_from_goods(good_name, units)

    # Livestock food contribution (milk, eggs etc. — small)
    livestock = econ.get("livestock", {})
    livestock_food = sum(livestock.get(t, 0) * 0.1 for t in livestock)

    # Food consumption: 1 person = 1 food unit per week
    cons_mod = SEASON_CONSUMPTION_MOD.get(season, 1.0)
    food_cons = pop * cons_mod / 7.0  # per-day converted from weekly

    net_food = (
        food_prod
        + livestock_food
        + food_goods_bonus
        + route_effects["food_import_bonus"]
        - shortage_effects["food_shortfall_days"]
        - food_cons
    )
    stores = econ["food_stores_days"] + net_food
    stores = min(stores, econ.get("food_stores_max", 999))
    stores = max(stores, 0)

    # Silver income
    feud_penalty = _worst_feud_trade_mod(state, settle_name)
    silver_in = (
        (econ["weekly_trade_income"] * feud_penalty * route_effects["market_liquidity"])
        + route_effects["export_bonus_silver"]
    )
    silver_out = econ["weekly_expenses"] + route_effects["import_cost_silver"] + shortage_effects["silver_drag"]
    net_silver = silver_in - silver_out
    treasury = max(0, econ["silver_treasury"] + net_silver)

    # Livestock feed cost (deducted from food stores)
    feed_cost = sum(
        livestock.get(t, 0) * LIVESTOCK_FEED.get(t, 0) for t in livestock
    )
    stores = max(0, stores - feed_cost)

    # Write back
    econ["food_stores_days"] = round(stores, 1)
    econ["silver_treasury"] = round(treasury, 1)
    econ["weekly_production_by_good"] = produced_goods
    econ["stock_buckets"] = stock_buckets
    econ["shortage_flags"] = shortage_effects["shortage_flags"]
    econ["unmet_imports"] = shortage_effects["unmet_imports"]
    econ["dependency_health"] = shortage_effects["dependency_health"]
    econ["repair_capacity_penalty"] = shortage_effects["repair_penalty"]
    econ["military_readiness_penalty"] = shortage_effects["military_penalty"]
    econ["vulnerability_pressure"] = shortage_effects["vulnerability_pressure"]
    econ["market_liquidity"] = route_effects["market_liquidity"]
    econ["local_price_pressure"] = route_effects["local_price_pressure"]
    econ["route_partner_losses"] = route_effects["trade_partner_losses"]
    econ["route_disruption_flags"] = route_effects["route_disruption_flags"]

    return {
        "settlement": settle_name,
        "food_produced": round(food_prod + livestock_food + food_goods_bonus, 1),
        "food_consumed": round(food_cons + feed_cost, 1),
        "net_food": round(net_food - feed_cost, 1),
        "stores": round(stores, 1),
        "silver_in": round(silver_in, 1),
        "silver_out": silver_out,
        "treasury": round(treasury, 1),
        "route_throughput": route_effects["throughput_total"],
        "export_bonus_silver": route_effects["export_bonus_silver"],
        "import_cost_silver": route_effects["import_cost_silver"],
        "food_import_bonus": route_effects["food_import_bonus"],
        "active_routes": route_effects["active_routes"],
        "market_liquidity": route_effects["market_liquidity"],
        "local_price_pressure": route_effects["local_price_pressure"],
        "trade_partner_losses": route_effects["trade_partner_losses"],
        "route_disruption_flags": route_effects["route_disruption_flags"],
        "produced_goods": produced_goods,
        "strategic_resource_flags": econ.get("strategic_resource_flags", []),
        "dependency_health": shortage_effects["dependency_health"],
        "unmet_imports": shortage_effects["unmet_imports"],
        "food_shortfall_days": shortage_effects["food_shortfall_days"],
        "repair_penalty": shortage_effects["repair_penalty"],
        "military_penalty": shortage_effects["military_penalty"],
        "vulnerability_pressure": shortage_effects["vulnerability_pressure"],
        "shortage_flags": shortage_effects["shortage_flags"],
    }


def _worst_feud_trade_mod(state: dict, settle_name: str) -> float:
    """Return the worst feud trade modifier affecting a settlement."""
    worst = 1.0
    for feud in state.get("feuds", []):
        if settle_name in feud["pair"]:
            lvl = feud["level"]
            worst = min(worst, FEUD_TRADE_MOD.get(lvl, 1.0))
    return worst


def compute_route_throughput(
    state: dict,
    settle_name: str,
    detailed_economies: dict[str, Any],
    routes: dict[str, Any],
) -> dict[str, Any]:
    profile = detailed_economies.get(settle_name, {})
    season = day_to_season(state["current_date"]["day_of_year"])
    season_key = _seasonal_access_key(season)
    route_entries = profile.get("trade_routes", [])
    active_routes = []
    throughput_total = 0.0
    export_bonus = 0.0
    food_import_bonus = 0.0
    trade_partner_losses: list[str] = []
    route_disruption_flags: list[str] = []

    export_lookup: dict[str, float] = {}
    for export in profile.get("exports", []):
        for destination in export.get("destinations", []) or []:
            export_lookup.setdefault(destination, 0.0)
            export_lookup[destination] += EXPORT_VOLUME.get(str(export.get("volume", "medium")), 1.0)

    for route_ref in route_entries:
        route = routes.get(route_ref.get("route_id"))
        if not route:
            continue
        destination = str(route_ref.get("to") or route.get("to_settlement") or "")
        access = str(route.get("seasonal_access", {}).get(season_key, "unknown"))
        access_mod = ROUTE_ACCESS_MOD.get(access, 0.6)
        traffic_mod = TRAFFIC_MOD.get(str(route.get("trade_traffic", "moderate")), 1.0)
        frequency_mod = FREQUENCY_MOD.get(str(route_ref.get("frequency", "monthly")), 0.3)
        feud_mod = min(
            _worst_feud_trade_mod(state, settle_name),
            _worst_feud_trade_mod(state, destination) if destination else 1.0,
        )
        route_throughput = access_mod * traffic_mod * frequency_mod * feud_mod
        throughput_total += route_throughput
        export_bonus += export_lookup.get(destination, 0.5) * route_throughput * 0.9
        goods_flow = str(route_ref.get("goods_flow", "")).lower()
        if any(token in goods_flow for token in FOOD_IMPORT_KEYS):
            food_import_bonus += 1.2 * route_throughput
        if access in ("dangerous", "closed"):
            route_disruption_flags.append(f"route_access:{route.get('id')}:{access}")
        if feud_mod < 1.0:
            route_disruption_flags.append(f"route_feud_drag:{route.get('id')}")
        if route_throughput < 0.25 and destination:
            trade_partner_losses.append(destination)
        active_routes.append(
            {
                "route_id": route.get("id"),
                "to": destination,
                "throughput": round(route_throughput, 2),
                "access": access,
            }
        )

    import_pressure = 0.0
    for item in profile.get("imports", []):
        import_pressure += IMPORT_URGENCY.get(str(item.get("urgency", "medium")), 1.0)
    import_gap = max(0.0, import_pressure - max(1.0, throughput_total * 2.2))

    market = profile.get("market", {})
    stall_count = float(market.get("stall_count", 0))
    trader_mod = TRADER_VISIT_MOD.get(str(market.get("visiting_traders", "occasional")), 0.7)
    market_day_mod = 1.1 if market.get("market_day") else 0.8
    route_support = 0.55 + min(0.85, throughput_total * 0.35)
    stall_support = min(0.35, stall_count * 0.025)
    market_liquidity = max(0.4, min(1.6, route_support * trader_mod * market_day_mod + stall_support))
    market_price_mod = float(market.get("price_modifier", 1.0))
    partner_loss_penalty = len(set(trade_partner_losses)) * 0.08
    local_price_pressure = max(0.75, min(1.8, market_price_mod + (1.15 - market_liquidity) + partner_loss_penalty))
    if len(set(trade_partner_losses)) > 0:
        route_disruption_flags.append(f"partner_loss:{len(set(trade_partner_losses))}")

    return {
        "season": season,
        "throughput_total": round(throughput_total, 2),
        "export_bonus_silver": round(export_bonus, 1),
        "import_pressure": round(import_pressure, 1),
        "import_cost_silver": round(import_gap * 1.1, 1),
        "food_import_bonus": round(food_import_bonus, 1),
        "active_routes": active_routes,
        "market_liquidity": round(market_liquidity, 2),
        "local_price_pressure": round(local_price_pressure, 2),
        "trade_partner_losses": sorted(set(trade_partner_losses)),
        "route_disruption_flags": sorted(set(route_disruption_flags)),
    }


# ============================================================
# Population Tick (Monthly) — §18.2
# ============================================================


def population_tick_month(state: dict, settle_name: str) -> dict:
    """Advance one settlement's population by one month."""
    demo = state["demographics"].get(settle_name, {})
    econ = state["economies"].get(settle_name, {})
    if not demo:
        return {}

    season = day_to_season(state["current_date"]["day_of_year"])
    changes = {"births": 0, "deaths": 0, "starvation": 0}

    # Births
    women = demo["women_working"]
    birth_mod = SEASON_BIRTH_MOD.get(season, 1.0)
    births = max(0, round(women * 0.006 * birth_mod))
    infant_deaths = max(0, round(births * 0.03))
    net_births = births - infant_deaths
    demo["children"] += net_births
    demo["total"] += net_births
    changes["births"] = net_births

    # Disease
    pop = demo["total"]
    disease = max(0, round(pop * 0.001))
    if season in ("Deep Dark", "Late Dark"):
        disease = max(0, round(pop * 0.002))
    demo["total"] = max(1, demo["total"] - disease)
    demo["elderly"] = max(0, demo["elderly"] - min(disease, demo["elderly"]))
    changes["deaths"] += disease

    # Starvation
    stores = econ.get("food_stores_days", 0) if econ else 999
    if stores <= 0:
        starved = max(0, round(pop * 0.02))
        demo["total"] = max(1, demo["total"] - starved)
        demo["men_working"] = max(0, demo["men_working"] - max(0, starved // 2))
        demo["women_working"] = max(0, demo["women_working"] - max(0, starved - starved // 2))
        changes["starvation"] = starved
        changes["deaths"] += starved

    # Cold deaths (deep/late dark)
    if season in ("Deep Dark", "Late Dark"):
        cold = max(0, round(pop * 0.002))
        demo["total"] = max(1, demo["total"] - cold)
        demo["elderly"] = max(0, demo["elderly"] - min(cold, demo["elderly"]))
        changes["deaths"] += cold

    return changes


# ============================================================
# Feud Mechanics — §18.6
# ============================================================


def get_feud(state: dict, a: str, b: str) -> dict | None:
    """Find feud between two settlements."""
    for f in state.get("feuds", []):
        if set(f["pair"]) == {a, b}:
            return f
    return None


def modify_feud(state: dict, a: str, b: str, delta: int, cause: str) -> int:
    """Change feud level. Returns new level."""
    feud = get_feud(state, a, b)
    if feud is None:
        feud = {"pair": [a, b], "level": 0, "cause": cause, "duration_seasons": 0}
        state.setdefault("feuds", []).append(feud)
    old = feud["level"]
    feud["level"] = max(0, min(4, feud["level"] + delta))
    if delta > 0:
        feud["cause"] = cause
    if feud["level"] != old:
        direction = "escalated" if delta > 0 else "de-escalated"
        log_event(state, f"Feud {a} ↔ {b} {direction} to {feud['level']} ({FEUD_LABELS[feud['level']]}): {cause}")
    return feud["level"]


# ============================================================
# Union Mechanics — §18.7
# ============================================================


def find_union(state: dict, name: str) -> dict | None:
    for u in state.get("unions", []):
        if u["name"].lower() == name.lower():
            return u
    return None


def get_settlement_union(state: dict, settle_name: str) -> dict | None:
    for u in state.get("unions", []):
        for m in u.get("members", []):
            if m["settlement"] == settle_name:
                return u
    return None


def union_combined_fighters(state: dict, union: dict) -> int:
    total = 0
    for m in union.get("members", []):
        demo = state["demographics"].get(m["settlement"], {})
        total += demo.get("fighters", 0)
    return total


def union_combined_population(state: dict, union: dict) -> int:
    total = 0
    for m in union.get("members", []):
        demo = state["demographics"].get(m["settlement"], {})
        total += demo.get("total", 0)
    return total


def union_combined_treasury(state: dict, union: dict) -> float:
    total = 0.0
    for m in union.get("members", []):
        econ = state["economies"].get(m["settlement"], {})
        total += econ.get("silver_treasury", 0)
    return total


def _ensure_union_runtime_fields(union: dict) -> dict:
    """Bootstrap runtime treasury and weekly-flow summaries for one union."""
    union.setdefault("treasury_silver", 0.0)
    union.setdefault("weekly_tribute_in_silver", 0.0)
    union.setdefault("weekly_tribute_in_food", 0.0)
    union.setdefault("weekly_tribute_in_materials", 0.0)
    union.setdefault("weekly_trade_bonus_silver", 0.0)
    union.setdefault("weekly_trade_dues_silver", 0.0)
    union.setdefault("weekly_levy_cost_silver", 0.0)
    union.setdefault("weekly_levy_fighters", 0)
    union.setdefault("seat_support_cost_silver", 0.0)
    union.setdefault("seat_support_cost_food", 0.0)
    union.setdefault("support_shortfall_silver", 0.0)
    union.setdefault("dark_arts_upkeep_silver", 0.0)
    union.setdefault("whisper_network_upkeep_silver", 0.0)
    union.setdefault("smuggling_income_silver", 0.0)
    union.setdefault("confidence_shock_pressure", 0.0)
    union.setdefault("confidence_shock_targets", [])
    union.setdefault("member_flows", [])
    return union


def _campaign_season_active(season: str) -> bool:
    return season in ("Long Summer", "Early Dark")


def _member_weekly_silver_tribute(member: dict, season: str) -> float:
    weekly = float(member.get("tribute_silver_weekly", 0.0) or 0.0)
    weekly += float(member.get("tribute_silver_monthly", 0.0) or 0.0) / 4.0
    weekly += float(member.get("tribute_silver_seasonal", 0.0) or 0.0) / 13.0
    if _campaign_season_active(season):
        weekly += float(member.get("tribute_silver_monthly_campaign_season", 0.0) or 0.0) / 4.0
    return round(weekly, 2)


def _member_service_and_goods_burden(member: dict, season: str) -> dict[str, float]:
    """Infer recurring mixed dues from authored tribute notes."""
    note_text = " ".join(
        str(member.get(key, "") or "")
        for key in ("tribute_goods_note", "tribute_service_note", "notes")
    ).lower()
    food_due = 0.0
    material_due = 0.0
    service_burden = 0.0
    seat_route_bonus = 0.0

    if "winter store" in note_text:
        food_due += 1.6 if season in ("Early Dark", "Deep Dark", "Late Dark") else 0.6
    if "peat" in note_text:
        material_due += 1.2
    if "lookout" in note_text:
        service_burden += 0.5
    if "labor" in note_text:
        service_burden += 0.7
    if "ferry priority" in note_text or "forced crossing" in note_text:
        service_burden += 0.5
        seat_route_bonus += 0.6

    return {
        "food_due": round(food_due, 2),
        "material_due": round(material_due, 2),
        "service_burden_silver": round(service_burden, 2),
        "seat_route_bonus_silver": round(seat_route_bonus, 2),
    }


def _transfer_material_dues(member_econ: dict, seat_econ: dict, due: float) -> float:
    """Move material tribute through the stock bucket abstraction."""
    if due <= 0:
        return 0.0
    member_buckets = member_econ.setdefault("stock_buckets", {"food": 0.0, "materials": 0.0, "trade": 0.0})
    seat_buckets = seat_econ.setdefault("stock_buckets", {"food": 0.0, "materials": 0.0, "trade": 0.0})
    available = float(member_buckets.get("materials", 0.0))
    actual = round(min(due, available), 1)
    if actual > 0:
        member_buckets["materials"] = round(max(0.0, available - actual), 1)
        seat_buckets["materials"] = round(seat_buckets.get("materials", 0.0) + actual, 1)
    return actual


def apply_union_economy_week(state: dict) -> list[dict[str, Any]]:
    """Apply weekly union tribute, levy, trade-bonus, and seat-support effects."""
    season = day_to_season(state["current_date"]["day_of_year"])
    union_reports: list[dict[str, Any]] = []

    for union in state.get("unions", []):
        union = _ensure_union_runtime_fields(union)
        union["weekly_tribute_in_silver"] = 0.0
        union["weekly_tribute_in_food"] = 0.0
        union["weekly_tribute_in_materials"] = 0.0
        union["weekly_trade_bonus_silver"] = 0.0
        union["weekly_trade_dues_silver"] = 0.0
        union["weekly_levy_cost_silver"] = 0.0
        union["weekly_levy_fighters"] = 0
        union["seat_support_cost_silver"] = 0.0
        union["seat_support_cost_food"] = 0.0
        union["support_shortfall_silver"] = 0.0
        union["member_flows"] = []

        seat_econ = state.get("economies", {}).get(union.get("seat", ""), {})
        if not seat_econ:
            continue
        _ensure_economy_runtime_fields(state, union["seat"])

        for member in union.get("members", []):
            settlement = member.get("settlement")
            if not settlement:
                continue
            member_econ = state.get("economies", {}).get(settlement, {})
            if not member_econ:
                continue
            _ensure_economy_runtime_fields(state, settlement)

            silver_due = _member_weekly_silver_tribute(member, season)
            burdens = _member_service_and_goods_burden(member, season)
            food_due = burdens["food_due"]
            material_due = burdens["material_due"]
            service_burden = burdens["service_burden_silver"]
            seat_route_bonus = burdens["seat_route_bonus_silver"]

            paid_silver = round(min(silver_due, member_econ.get("silver_treasury", 0.0)), 1)
            member_econ["silver_treasury"] = round(max(0.0, member_econ.get("silver_treasury", 0.0) - paid_silver), 1)
            member_econ["union_tribute_paid_silver"] = round(paid_silver, 1)
            union["treasury_silver"] = round(union.get("treasury_silver", 0.0) + paid_silver, 1)
            union["weekly_tribute_in_silver"] = round(union["weekly_tribute_in_silver"] + paid_silver, 1)

            actual_food = round(min(food_due, member_econ.get("food_stores_days", 0.0)), 1)
            member_econ["food_stores_days"] = round(max(0.0, member_econ.get("food_stores_days", 0.0) - actual_food), 1)
            seat_econ["food_stores_days"] = round(seat_econ.get("food_stores_days", 0.0) + actual_food, 1)
            member_econ["union_tribute_paid_food"] = round(actual_food, 1)
            union["weekly_tribute_in_food"] = round(union["weekly_tribute_in_food"] + actual_food, 1)

            actual_materials = _transfer_material_dues(member_econ, seat_econ, material_due)
            member_econ["union_tribute_paid_materials"] = round(actual_materials, 1)
            union["weekly_tribute_in_materials"] = round(union["weekly_tribute_in_materials"] + actual_materials, 1)

            if service_burden > 0:
                actual_service = round(min(service_burden, member_econ.get("silver_treasury", 0.0)), 1)
                member_econ["silver_treasury"] = round(max(0.0, member_econ.get("silver_treasury", 0.0) - actual_service), 1)
                member_econ["union_support_burden_silver"] = round(actual_service, 1)

            if seat_route_bonus > 0:
                seat_econ["silver_treasury"] = round(seat_econ.get("silver_treasury", 0.0) + seat_route_bonus, 1)

            livestock_monthly = float(member.get("tribute_livestock_monthly", 0.0) or 0.0)
            actual_livestock = 0
            if livestock_monthly > 0:
                member_econ["union_livestock_tribute_progress"] = round(
                    member_econ.get("union_livestock_tribute_progress", 0.0) + livestock_monthly / 4.0,
                    2,
                )
                due_animals = int(member_econ["union_livestock_tribute_progress"])
                if due_animals > 0:
                    herd = member_econ.setdefault("livestock", {})
                    seat_herd = seat_econ.setdefault("livestock", {})
                    for _ in range(due_animals):
                        if herd.get("sheep", 0) <= 0:
                            break
                        herd["sheep"] -= 1
                        seat_herd["sheep"] = seat_herd.get("sheep", 0) + 1
                        actual_livestock += 1
                    member_econ["union_livestock_tribute_progress"] = round(
                        max(0.0, member_econ["union_livestock_tribute_progress"] - actual_livestock),
                        2,
                    )

            levy_cost = 0.0
            levy_fighters = int(member.get("levy_fighters", 0) or 0)
            if levy_fighters > 0:
                levy_activation = 0.25 + (union.get("war_readiness", 0) * 0.15)
                levy_cost = round(levy_fighters * levy_activation * 0.12, 1)
                actual_levy_cost = round(min(levy_cost, member_econ.get("silver_treasury", 0.0)), 1)
                member_econ["silver_treasury"] = round(
                    max(0.0, member_econ.get("silver_treasury", 0.0) - actual_levy_cost),
                    1,
                )
                member_econ["union_levy_cost_silver"] = actual_levy_cost
                union["weekly_levy_cost_silver"] = round(union["weekly_levy_cost_silver"] + actual_levy_cost, 1)
                union["weekly_levy_fighters"] += levy_fighters

            trade_bonus = float(member.get("trade_bonus", 1.0) or 1.0)
            trade_bonus_gain = 0.0
            trade_dues = 0.0
            if trade_bonus > 1.0:
                gross_bonus = member_econ.get("weekly_trade_income", 0.0) * (trade_bonus - 1.0) * member_econ.get(
                    "market_liquidity",
                    1.0,
                )
                trade_dues = round(gross_bonus * 0.15, 1)
                trade_bonus_gain = round(max(0.0, gross_bonus - trade_dues), 1)
                member_econ["silver_treasury"] = round(member_econ.get("silver_treasury", 0.0) + trade_bonus_gain, 1)
                member_econ["union_trade_bonus_silver"] = trade_bonus_gain
                member_econ["union_trade_dues_silver"] = trade_dues
                union["treasury_silver"] = round(union.get("treasury_silver", 0.0) + trade_dues, 1)
                union["weekly_trade_bonus_silver"] = round(union["weekly_trade_bonus_silver"] + trade_bonus_gain, 1)
                union["weekly_trade_dues_silver"] = round(union["weekly_trade_dues_silver"] + trade_dues, 1)

            union["member_flows"].append(
                {
                    "settlement": settlement,
                    "silver_paid": paid_silver,
                    "food_paid": actual_food,
                    "materials_paid": actual_materials,
                    "livestock_paid": actual_livestock,
                    "service_burden_silver": round(member_econ.get("union_support_burden_silver", 0.0), 1),
                    "levy_cost_silver": round(member_econ.get("union_levy_cost_silver", 0.0), 1),
                    "trade_bonus_silver": trade_bonus_gain,
                    "trade_dues_silver": trade_dues,
                }
            )

        support_base = {"military": 2.6, "economic": 1.8, "covert": 2.2}.get(union.get("type", ""), 1.6)
        support_silver = (
            support_base
            + (len(union.get("members", [])) * 0.25)
            + (union.get("war_readiness", 0) * 0.6)
            + (union.get("dark_arts_level", 0) * 0.4)
            + (len(union.get("whisper_agents", [])) * 0.15)
        )
        support_food = 0.8 + (len(union.get("members", [])) * 0.25) + (union.get("dark_arts_level", 0) * 0.2)
        union["seat_support_cost_silver"] = round(support_silver, 1)
        union["seat_support_cost_food"] = round(support_food, 1)

        paid_support = round(min(union.get("treasury_silver", 0.0), support_silver), 1)
        union["treasury_silver"] = round(max(0.0, union.get("treasury_silver", 0.0) - paid_support), 1)
        support_shortfall = round(max(0.0, support_silver - paid_support), 1)
        union["support_shortfall_silver"] = support_shortfall
        if support_shortfall > 0:
            seat_econ["silver_treasury"] = round(max(0.0, seat_econ.get("silver_treasury", 0.0) - support_shortfall), 1)
        seat_econ["food_stores_days"] = round(max(0.0, seat_econ.get("food_stores_days", 0.0) - support_food), 1)

        union_reports.append(
            {
                "union": union["name"],
                "treasury_silver": union.get("treasury_silver", 0.0),
                "weekly_tribute_in_silver": union["weekly_tribute_in_silver"],
                "weekly_tribute_in_food": union["weekly_tribute_in_food"],
                "weekly_tribute_in_materials": union["weekly_tribute_in_materials"],
                "weekly_trade_bonus_silver": union["weekly_trade_bonus_silver"],
                "weekly_trade_dues_silver": union["weekly_trade_dues_silver"],
                "weekly_levy_cost_silver": union["weekly_levy_cost_silver"],
                "weekly_levy_fighters": union["weekly_levy_fighters"],
                "seat_support_cost_silver": union["seat_support_cost_silver"],
                "seat_support_cost_food": union["seat_support_cost_food"],
                "support_shortfall_silver": union["support_shortfall_silver"],
            }
        )

    return union_reports


def apply_dark_arts_economy_week(state: dict) -> list[dict[str, Any]]:
    """Apply ongoing occult and covert economy effects after union dues resolve."""
    reports: list[dict[str, Any]] = []

    for union in state.get("unions", []):
        union = _ensure_union_runtime_fields(union)
        level = int(union.get("dark_arts_level", 0) or 0)
        practitioners = union.get("dark_arts_practitioners", []) or []
        agents = union.get("whisper_agents", []) or []
        if level <= 0 and not practitioners and not agents:
            continue

        seat = union.get("seat", "")
        seat_econ = state.get("economies", {}).get(seat, {})
        if not seat_econ:
            continue
        _ensure_economy_runtime_fields(state, seat)

        # Reset visible runtime fields for the current week.
        union["dark_arts_upkeep_silver"] = 0.0
        union["whisper_network_upkeep_silver"] = 0.0
        union["smuggling_income_silver"] = 0.0
        union["confidence_shock_pressure"] = 0.0
        union["confidence_shock_targets"] = []

        seat_econ["covert_fear_pressure"] = 0.0
        seat_econ["confidence_shock_pressure"] = 0.0
        seat_econ["smuggling_leak_silver"] = 0.0
        seat_econ["covert_flags"] = []

        deteriorating = sum(1 for practitioner in practitioners if practitioner.get("health") == "deteriorating")
        agent_quality_total = sum(int(agent.get("quality", 1) or 1) for agent in agents)

        dark_upkeep = round((len(practitioners) * (0.6 + level * 0.2)) + (deteriorating * 0.3), 1)
        whisper_upkeep = round(sum(0.25 + (int(agent.get("quality", 1) or 1) * 0.2) for agent in agents), 1)
        smuggling_income = round(max(0.0, (agent_quality_total * 0.35) + (level * 0.15) - (0.1 * deteriorating)), 1)
        confidence_pressure = round((level * 0.08) + (agent_quality_total * 0.03), 2)

        union["dark_arts_upkeep_silver"] = dark_upkeep
        union["whisper_network_upkeep_silver"] = whisper_upkeep
        union["smuggling_income_silver"] = smuggling_income
        union["confidence_shock_pressure"] = confidence_pressure

        # Smuggling adds to the covert union's war chest before upkeep is paid.
        union["treasury_silver"] = round(union.get("treasury_silver", 0.0) + smuggling_income, 1)
        total_upkeep = round(dark_upkeep + whisper_upkeep, 1)
        paid_upkeep = round(min(union.get("treasury_silver", 0.0), total_upkeep), 1)
        union["treasury_silver"] = round(max(0.0, union.get("treasury_silver", 0.0) - paid_upkeep), 1)
        upkeep_shortfall = round(max(0.0, total_upkeep - paid_upkeep), 1)
        if upkeep_shortfall > 0:
            seat_econ["silver_treasury"] = round(max(0.0, seat_econ.get("silver_treasury", 0.0) - upkeep_shortfall), 1)

        seat_econ["covert_fear_pressure"] = round(level * 0.12 + deteriorating * 0.08, 2)
        seat_econ["confidence_shock_pressure"] = round(confidence_pressure, 2)
        seat_econ["smuggling_leak_silver"] = smuggling_income
        seat_econ["market_liquidity"] = round(max(0.4, seat_econ.get("market_liquidity", 1.0) - (confidence_pressure * 0.35)), 2)
        seat_econ["local_price_pressure"] = round(min(1.8, seat_econ.get("local_price_pressure", 1.0) + confidence_pressure), 2)
        seat_econ["covert_flags"] = sorted(
            set(seat_econ.get("covert_flags", []) + [f"dark_arts:{_normalize_key(union['name'])}"])
        )

        for agent in agents:
            target_name = str(agent.get("location", ""))
            target_econ = state.get("economies", {}).get(target_name)
            if not target_econ:
                continue
            _ensure_economy_runtime_fields(state, target_name)
            quality = int(agent.get("quality", 1) or 1)
            target_pressure = round(quality * 0.05, 2)
            target_econ["covert_fear_pressure"] = round(target_econ.get("covert_fear_pressure", 0.0) + target_pressure, 2)
            target_econ["confidence_shock_pressure"] = round(
                target_econ.get("confidence_shock_pressure", 0.0) + target_pressure,
                2,
            )
            target_econ["market_liquidity"] = round(max(0.4, target_econ.get("market_liquidity", 1.0) - target_pressure), 2)
            target_econ["local_price_pressure"] = round(
                min(1.8, target_econ.get("local_price_pressure", 1.0) + target_pressure),
                2,
            )
            target_econ["covert_flags"] = sorted(
                set(target_econ.get("covert_flags", []) + [f"whisper_pressure:{_normalize_key(union['name'])}"])
            )
            union["confidence_shock_targets"].append(target_name)

        union["confidence_shock_targets"] = sorted(set(union["confidence_shock_targets"]))
        reports.append(
            {
                "union": union["name"],
                "dark_arts_upkeep_silver": dark_upkeep,
                "whisper_network_upkeep_silver": whisper_upkeep,
                "smuggling_income_silver": smuggling_income,
                "confidence_shock_pressure": confidence_pressure,
                "confidence_shock_targets": union["confidence_shock_targets"],
            }
        )

    return reports


def _band_strategy_profile(strategy: str) -> dict[str, float]:
    text = strategy.lower()
    revenue = 0.4
    food = 0.2
    pressure = 0.4
    competition = 0.0

    if "toll" in text or "passage fee" in text:
        revenue += 1.0
        pressure += 0.8
        competition += 0.5
    if "escort" in text or "protection" in text:
        revenue += 0.8
        pressure += 0.4
        competition += 0.7
    if "smuggling" in text:
        revenue += 0.9
        pressure += 0.3
        competition += 0.5
    if "piracy" in text:
        revenue += 1.0
        pressure += 0.8
        competition += 0.7
    if "raid" in text or "raiding" in text:
        revenue += 0.7
        pressure += 1.0
        competition += 0.3
    if "poaching" in text or "foraging" in text or "hunting" in text or "trapping" in text or "fishing" in text:
        food += 0.8
        pressure += 0.2
    if "trade" in text or "trader" in text:
        revenue += 0.5
    if "seiðr" in text or "divination" in text or "curse" in text:
        revenue += 0.3
        food += 0.4
        pressure += 0.4
    if "scavenging" in text or "petty theft" in text:
        revenue -= 0.1
        food += 0.3
        pressure += 0.3

    return {
        "revenue_factor": revenue,
        "food_factor": food,
        "pressure_factor": pressure,
        "competition_factor": competition,
    }


def _band_pressure_targets(band: dict[str, Any], settlement_names: list[str]) -> list[str]:
    haystack = " ".join(
        str(band.get(field, "") or "")
        for field in ("territory", "survival_strategy", "narrative_hook", "winter_strategy", "notes")
    ).lower()
    targets = [name for name in settlement_names if name.lower() in haystack]
    return sorted(set(targets))


def apply_wolfshead_economy_week(state: dict) -> list[dict[str, Any]]:
    """Turn outlaw bands into weekly economic actors and settlement pressure."""
    season = day_to_season(state["current_date"]["day_of_year"])
    settlements = list(state.get("economies", {}).keys())
    reports: list[dict[str, Any]] = []
    wolfshead_state = state.setdefault("wolfshead_state", {})

    for name in settlements:
        econ = state["economies"].get(name, {})
        if not econ:
            continue
        _ensure_economy_runtime_fields(state, name)
        econ["outlaw_pressure"] = 0
        econ["night_market_chance"] = 0.0
        econ["wolfshead_tribute_drag_silver"] = 0.0
        econ["mercenary_competition_pressure"] = 0.0
        econ["wolfshead_pressure_flags"] = []

    for band in load_wolfshead_bands():
        band_id = str(band.get("id", "WOLF_UNKNOWN"))
        runtime = wolfshead_state.setdefault(
            band_id,
            {
                "weekly_income_silver": 0.0,
                "weekly_food_gain": 0.0,
                "desperation": 0.0,
                "pressure_targets": [],
                "mercenary_competition": 0.0,
            },
        )
        profile = _band_strategy_profile(str(band.get("survival_strategy", "")))
        size = int(band.get("size", 0) or 0)
        threat = int(band.get("threat_tier", 1) or 1)
        targets = _band_pressure_targets(band, settlements)

        winter_hunger = 1.25 if season in ("Deep Dark", "Late Dark") else 1.0
        revenue = round(max(0.0, size * 0.12 * profile["revenue_factor"]), 1)
        food_gain = round(max(0.0, size * 0.35 * profile["food_factor"] / winter_hunger), 1)
        food_need = round(size * (0.45 if season in ("Long Summer", "Early Dark") else 0.6), 1)
        desperation = round(max(0.0, (food_need - food_gain) / max(1.0, size / 2.0)), 2)
        competition = round(profile["competition_factor"] * max(1.0, threat * 0.5), 2)

        runtime["weekly_income_silver"] = revenue
        runtime["weekly_food_gain"] = food_gain
        runtime["desperation"] = desperation
        runtime["pressure_targets"] = targets
        runtime["mercenary_competition"] = competition

        for target in targets:
            econ = state["economies"].get(target, {})
            if not econ:
                continue
            pressure_points = profile["pressure_factor"] + (0.2 * threat) + desperation
            pressure_level = max(1, min(5, math.ceil(pressure_points)))
            econ["outlaw_pressure"] = max(int(econ.get("outlaw_pressure", 0)), pressure_level)
            econ["night_market_chance"] = round(
                max(float(econ.get("night_market_chance", 0.0)), min(0.75, econ["outlaw_pressure"] * 0.15)),
                2,
            )
            tribute_drag = round(max(0.0, (pressure_level - 2) * 0.4), 1)
            competition_drag = round(max(0.0, competition * 0.2), 1)
            econ["wolfshead_tribute_drag_silver"] = round(
                econ.get("wolfshead_tribute_drag_silver", 0.0) + tribute_drag,
                1,
            )
            econ["mercenary_competition_pressure"] = round(
                econ.get("mercenary_competition_pressure", 0.0) + competition_drag,
                1,
            )
            econ["market_liquidity"] = round(max(0.4, econ.get("market_liquidity", 1.0) - (pressure_level * 0.06)), 2)
            econ["local_price_pressure"] = round(
                min(1.8, econ.get("local_price_pressure", 1.0) + (pressure_level * 0.07)),
                2,
            )
            econ["silver_treasury"] = round(max(0.0, econ.get("silver_treasury", 0.0) - tribute_drag), 1)
            econ["wolfshead_pressure_flags"] = sorted(
                set(
                    econ.get("wolfshead_pressure_flags", [])
                    + [f"wolfshead:{band_id}", f"outlaw_pressure:{pressure_level}"]
                )
            )

        reports.append(
            {
                "band_id": band_id,
                "band_name": band.get("name", band_id),
                "weekly_income_silver": revenue,
                "weekly_food_gain": food_gain,
                "desperation": desperation,
                "pressure_targets": targets,
                "mercenary_competition": competition,
            }
        )

    return reports


def _contract_season_matches(contract: dict[str, Any], season: str) -> bool:
    contract_season = str(contract.get("season", "any") or "any").lower()
    season_key = {
        "Long Summer": "summer",
        "Early Dark": "autumn",
        "Deep Dark": "winter",
        "Late Dark": "spring",
    }.get(season, "any")
    return contract_season in ("any", season_key)


def _contract_year_matches(contract: dict[str, Any], year: int) -> bool:
    year_range = contract.get("year_range")
    if not year_range:
        return True
    if isinstance(year_range, list) and len(year_range) == 2:
        return int(year_range[0]) <= year <= int(year_range[1])
    return True


def _settlement_feud_level(state: dict, settle_name: str) -> int:
    level = 0
    for feud in state.get("feuds", []):
        if settle_name in feud.get("pair", []):
            level = max(level, int(feud.get("level", 0) or 0))
    return level


def _contract_priority(state: dict, settle_name: str, econ: dict[str, Any], contract: dict[str, Any]) -> float:
    ctype = str(contract.get("type", "")).lower()
    priority = 1.0
    outlaw_pressure = int(econ.get("outlaw_pressure", 0) or 0)
    shortage_pressure = max(0.0, 1.0 - float(econ.get("dependency_health", 1.0)))
    route_pressure = max(0.0, float(econ.get("local_price_pressure", 1.0)) - 1.0)
    feud_level = _settlement_feud_level(state, settle_name)

    if ctype in {"guard", "patrol", "garrison", "coastal_defense", "shared_defense", "winter_hold"}:
        priority += outlaw_pressure * 0.45 + feud_level * 0.35 + route_pressure * 0.3
    if ctype in {"escort", "naval_escort", "trade_protection", "arms_escort", "diplomatic_escort", "courier", "messenger"}:
        priority += route_pressure * 0.7 + max(0.0, outlaw_pressure - 1) * 0.25
    if ctype in {"bounty", "raid", "sabotage", "assassination", "combat", "war_band", "siege_support"}:
        priority += feud_level * 0.6 + outlaw_pressure * 0.25
    if ctype in {"investigation", "rescue", "retrieval", "barrow_clear", "barrow_retrieval", "ritual"}:
        priority += shortage_pressure * 0.25 + float(econ.get("covert_fear_pressure", 0.0)) * 0.35
    if float(contract.get("advance_silver", 0) or 0) > max(0.0, econ.get("silver_treasury", 0.0) * 0.45):
        priority -= 0.8
    return round(priority, 2)


def apply_contract_market_week(state: dict) -> list[dict[str, Any]]:
    """Build a weekly contract market from authored pools and current pressure."""
    current = state.get("current_date", {})
    season = day_to_season(current.get("day_of_year", 1))
    year = int(current.get("year", 312) or 312)
    contract_market = state.setdefault("contract_market", {})
    active_contracts = contract_market.setdefault("active_contracts", [])
    by_settlement: dict[str, Any] = {}
    reports: list[dict[str, Any]] = []
    contracts = load_contracts()

    for settle_name, econ in state.get("economies", {}).items():
        _ensure_economy_runtime_fields(state, settle_name)
        econ["contract_offer_pressure"] = 0.0
        econ["contract_budget_pressure"] = 0.0
        econ["contract_market_tags"] = []

        base_contracts = [
            c for c in contracts
            if c.get("settlement") == settle_name
            and _contract_season_matches(c, season)
            and _contract_year_matches(c, year)
        ]
        feud_level = _settlement_feud_level(state, settle_name)
        filtered_contracts = []
        for contract in base_contracts:
            political = contract.get("political_conditions", {}) or {}
            feud_max = political.get("requires_feud_max")
            if feud_max is not None and feud_level > int(feud_max):
                continue
            filtered_contracts.append(contract)

        base_budget = float(econ.get("silver_treasury", 0.0)) * 0.32
        if econ.get("union_membership"):
            union = find_union(state, str(econ.get("union_membership")))
            if union:
                base_budget += float(union.get("treasury_silver", 0.0)) * 0.12

        demand_multiplier = (
            1.0
            + (int(econ.get("outlaw_pressure", 0) or 0) * 0.12)
            + (max(0.0, float(econ.get("local_price_pressure", 1.0)) - 1.0) * 0.4)
            + (max(0.0, 1.0 - float(econ.get("dependency_health", 1.0))) * 0.5)
            + (_settlement_feud_level(state, settle_name) * 0.1)
        )
        payout_capacity = round(max(0.0, base_budget / max(1.0, demand_multiplier)), 1)
        advance_capacity = round(max(0.0, payout_capacity * 0.35), 1)

        ranked_contracts = sorted(
            filtered_contracts,
            key=lambda contract: _contract_priority(state, settle_name, econ, contract),
            reverse=True,
        )
        visible_offers: list[dict[str, Any]] = []
        visible_budget = 0.0
        for contract in ranked_contracts:
            payment = float(contract.get("payment_silver", 0.0) or 0.0)
            reserve_need = payment * 0.5
            if visible_budget + reserve_need > max(12.0, payout_capacity * 2.0):
                continue
            visible_budget += reserve_need
            visible_offers.append(
                {
                    "id": contract.get("id"),
                    "title": contract.get("title"),
                    "type": contract.get("type"),
                    "payment_silver": payment,
                    "advance_silver": float(contract.get("advance_silver", 0.0) or 0.0),
                    "priority": _contract_priority(state, settle_name, econ, contract),
                }
            )
            if len(visible_offers) >= 5:
                break

        pressure_tags: list[str] = []
        if int(econ.get("outlaw_pressure", 0) or 0) >= 2:
            pressure_tags.append("outlaw_demand")
        if float(econ.get("local_price_pressure", 1.0)) > 1.15:
            pressure_tags.append("route_stress")
        if float(econ.get("dependency_health", 1.0)) < 0.85:
            pressure_tags.append("scarcity")
        if feud_level >= 2:
            pressure_tags.append("feud")
        if float(econ.get("covert_fear_pressure", 0.0)) > 0:
            pressure_tags.append("covert_fear")

        active_here = [item for item in active_contracts if item.get("settlement") == settle_name and item.get("status") == "active"]
        locked_value = round(sum(float(item.get("reserved_payout_silver", 0.0) or 0.0) for item in active_here), 1)
        advances_paid = round(sum(float(item.get("advance_paid_silver", 0.0) or 0.0) for item in active_here), 1)

        by_settlement[settle_name] = {
            "settlement": settle_name,
            "available_contract_ids": [item["id"] for item in visible_offers],
            "offer_count": len(visible_offers),
            "issuer_budget_silver": round(base_budget, 1),
            "payout_capacity_silver": payout_capacity,
            "advance_capacity_silver": advance_capacity,
            "contract_value_locked_silver": locked_value,
            "advances_paid_silver": advances_paid,
            "demand_multiplier": round(demand_multiplier, 2),
            "pressure_tags": pressure_tags,
            "visible_offers": visible_offers,
        }
        econ["contract_offer_pressure"] = round(max(0.0, demand_multiplier - 1.0), 2)
        econ["contract_budget_pressure"] = round(max(0.0, (locked_value + advances_paid) / max(1.0, payout_capacity or 1.0)), 2)
        econ["contract_market_tags"] = pressure_tags

        reports.append(
            {
                "settlement": settle_name,
                "offer_count": len(visible_offers),
                "issuer_budget_silver": round(base_budget, 1),
                "payout_capacity_silver": payout_capacity,
                "active_contracts": len(active_here),
                "pressure_tags": pressure_tags,
            }
        )

    contract_market["by_settlement"] = by_settlement
    return reports


def activate_contract(state: dict, contract_id: str, taker: str = "manual_band") -> dict[str, Any]:
    """Reserve budget, pay advance, and mark a contract active."""
    contracts = {contract["id"]: contract for contract in load_contracts() if contract.get("id")}
    contract = contracts.get(contract_id)
    if not contract:
        return {"error": f"Unknown contract: {contract_id}"}

    settlement = contract.get("settlement")
    econ = state.get("economies", {}).get(settlement, {})
    market = state.setdefault("contract_market", {}).setdefault("by_settlement", {}).get(settlement)
    if not econ or not market:
        return {"error": f"Missing economy or contract market for: {settlement}"}

    advance = float(contract.get("advance_silver", 0.0) or 0.0)
    payment = float(contract.get("payment_silver", 0.0) or 0.0)
    reserved = round(max(0.0, payment - advance), 1)
    if advance > market.get("advance_capacity_silver", 0.0):
        return {"error": f"Advance budget too small for {contract_id}"}

    econ["silver_treasury"] = round(max(0.0, econ.get("silver_treasury", 0.0) - advance), 1)
    state["contract_market"].setdefault("active_contracts", []).append(
        {
            "id": contract_id,
            "settlement": settlement,
            "title": contract.get("title"),
            "taker": taker,
            "status": "active",
            "advance_paid_silver": advance,
            "reserved_payout_silver": reserved,
            "duration_days": int(contract.get("duration_days", 0) or 0),
            "days_remaining": int(contract.get("duration_days", 0) or 0),
        }
    )
    log_event(state, f"Contract {contract_id} activated at {settlement}; advance {advance:.1f}s paid to {taker}")
    return {
        "contract_id": contract_id,
        "settlement": settlement,
        "advance_paid_silver": advance,
        "reserved_payout_silver": reserved,
        "status": "active",
    }


def resolve_contract(state: dict, contract_id: str, outcome: str) -> dict[str, Any]:
    """Resolve an active contract and mutate settlement economy on outcome."""
    active_contracts = state.setdefault("contract_market", {}).setdefault("active_contracts", [])
    record = next((item for item in active_contracts if item.get("id") == contract_id and item.get("status") == "active"), None)
    if not record:
        return {"error": f"Active contract not found: {contract_id}"}

    contracts = {contract["id"]: contract for contract in load_contracts() if contract.get("id")}
    contract = contracts.get(contract_id)
    if not contract:
        return {"error": f"Unknown contract metadata: {contract_id}"}

    settlement = record["settlement"]
    econ = state.get("economies", {}).get(settlement, {})
    if not econ:
        return {"error": f"Missing settlement economy: {settlement}"}

    reserved = float(record.get("reserved_payout_silver", 0.0) or 0.0)
    advance = float(record.get("advance_paid_silver", 0.0) or 0.0)
    ctype = str(contract.get("type", "")).lower()

    if outcome == "success":
        econ["silver_treasury"] = round(max(0.0, econ.get("silver_treasury", 0.0) - reserved), 1)
        if ctype in {"guard", "patrol", "garrison", "coastal_defense", "winter_hold", "shared_defense"}:
            econ["outlaw_pressure"] = max(0, int(econ.get("outlaw_pressure", 0) or 0) - 1)
            econ["market_liquidity"] = round(min(1.6, econ.get("market_liquidity", 1.0) + 0.08), 2)
        if ctype in {"escort", "trade_protection", "naval_escort", "arms_escort"}:
            econ["local_price_pressure"] = round(max(0.75, econ.get("local_price_pressure", 1.0) - 0.06), 2)
            econ["market_liquidity"] = round(min(1.6, econ.get("market_liquidity", 1.0) + 0.06), 2)
        if ctype in {"fort_building", "siege_support"}:
            econ["repair_capacity_penalty"] = max(0, int(econ.get("repair_capacity_penalty", 0) or 0) - 1)
        if ctype in {"barrow_clear", "beast_hunt", "bounty", "raid", "sabotage"}:
            econ["covert_fear_pressure"] = round(max(0.0, econ.get("covert_fear_pressure", 0.0) - 0.08), 2)
    else:
        econ["local_price_pressure"] = round(min(1.8, econ.get("local_price_pressure", 1.0) + 0.08), 2)
        econ["market_liquidity"] = round(max(0.4, econ.get("market_liquidity", 1.0) - 0.08), 2)
        if ctype in {"guard", "patrol", "garrison", "coastal_defense", "winter_hold", "shared_defense"}:
            econ["outlaw_pressure"] = min(5, int(econ.get("outlaw_pressure", 0) or 0) + 1)
        if ctype in {"escort", "trade_protection", "naval_escort", "arms_escort"}:
            econ["wolfshead_tribute_drag_silver"] = round(econ.get("wolfshead_tribute_drag_silver", 0.0) + 0.8, 1)
        if ctype in {"fort_building", "siege_support"}:
            econ["repair_capacity_penalty"] = int(econ.get("repair_capacity_penalty", 0) or 0) + 1

    record["status"] = outcome
    record["resolved_day"] = int(state.get("current_date", {}).get("day_of_year", 0) or 0)
    log_event(
        state,
        f"Contract {contract_id} at {settlement} resolved as {outcome}; advance {advance:.1f}s, payout reserve {reserved:.1f}s",
    )
    return {
        "contract_id": contract_id,
        "settlement": settlement,
        "outcome": outcome,
        "advance_paid_silver": advance,
        "reserved_payout_silver": reserved,
    }


def modify_cohesion(state: dict, union_name: str, delta: int, cause: str) -> int:
    union = find_union(state, union_name)
    if not union:
        return -1
    old = union["cohesion"]
    union["cohesion"] = max(1, min(5, union["cohesion"] + delta))
    if union["cohesion"] != old:
        log_event(state, f"{union_name} cohesion {'+'if delta>0 else ''}{delta} → {union['cohesion']}: {cause}")
    return union["cohesion"]


def modify_war_readiness(state: dict, union_name: str, delta: int, cause: str) -> int:
    union = find_union(state, union_name)
    if not union:
        return -1
    old = union["war_readiness"]
    union["war_readiness"] = max(0, min(5, union["war_readiness"] + delta))
    if union["war_readiness"] != old:
        log_event(state, f"{union_name} war readiness {'+'if delta>0 else ''}{delta} → {union['war_readiness']}: {cause}")
    return union["war_readiness"]


# ============================================================
# Dark Arts — §18.9
# ============================================================


def dark_arts_consequences(state: dict, union: dict) -> list[str]:
    """Apply dark arts consequences. Returns list of narrative events."""
    level = union.get("dark_arts_level", 0)
    events = []

    if level >= 3:
        # Random supernatural event near seat
        if random.randint(1, 100) <= 15:
            events.append(f"Veil instability near {union['seat']}. Strange lights. Dogs refuse to enter.")
            log_event(state, f"Veil instability near {union['seat']}")

    if level >= 4:
        # Practitioner deterioration
        for p in union.get("dark_arts_practitioners", []):
            if p.get("health") == "deteriorating" and random.randint(1, 100) <= 10:
                p["health"] = "lost"
                events.append(f"Practitioner {p['name']} lost — consumed by the craft.")
                log_event(state, f"Dark arts practitioner {p['name']} lost in {union['name']}")

    if level >= 5:
        # Catastrophic Veil breach chance
        if random.randint(1, 100) <= 20:
            events.append(f"VEIL BREACH at {union['seat']}. Draugr incursion. Permanent supernatural contamination.")
            log_event(state, f"VEIL BREACH at {union['seat']} — catastrophic dark arts failure")
            # Devastate the seat settlement
            demo = state["demographics"].get(union["seat"], {})
            if demo:
                losses = max(1, demo["total"] // 5)
                demo["total"] = max(1, demo["total"] - losses)
                demo["fighters"] = max(0, demo["fighters"] - losses // 3)
                events.append(f"{union['seat']} loses {losses} people to the breach.")

    # Fear effect on other unions
    if level >= 2:
        for other in state.get("unions", []):
            if other["name"] != union["name"]:
                # Reduce willingness to attack directly
                pass  # Handled in war readiness calculations

    return events


# ============================================================
# Raid — §18.5
# ============================================================


def resolve_raid(state: dict, attacker: str, target: str, num_raiders: int) -> dict:
    """Resolve a raid. Returns result dict with narrative."""
    target_demo = state["demographics"].get(target, {})
    target_econ = state["economies"].get(target, {})
    if not target_demo or not target_econ:
        return {"success": False, "narrative": f"Unknown settlement: {target}"}

    defense_fighters = target_demo.get("fighters", 0)
    # Load defensibility from settlements.yaml
    settle_data = load_settlements()
    defensibility = 1
    for s in settle_data.get("settlements", []):
        if s.get("name") == target:
            defensibility = s.get("defensibility", 1)
            break

    raid_force = num_raiders * 1.0  # Average combat power = 1
    defense_force = defense_fighters * defensibility * 0.5

    result = {
        "attacker": attacker,
        "target": target,
        "raiders": num_raiders,
        "defenders": defense_fighters,
        "raid_force": round(raid_force, 1),
        "defense_force": round(defense_force, 1),
    }

    if raid_force > defense_force * 1.5:
        result["outcome"] = "overwhelming_success"
        result["raider_losses"] = 0
        result["loot_silver"] = random.randint(10, 20)
        result["loot_livestock"] = random.randint(4, 12)
    elif raid_force > defense_force:
        result["outcome"] = "success"
        result["raider_losses"] = max(1, round(num_raiders * 0.10))
        result["loot_silver"] = random.randint(5, 15)
        result["loot_livestock"] = random.randint(2, 8)
    elif raid_force > defense_force * 0.7:
        result["outcome"] = "partial_success"
        result["raider_losses"] = max(1, round(num_raiders * 0.20))
        result["loot_silver"] = random.randint(2, 8)
        result["loot_livestock"] = random.randint(1, 4)
    else:
        result["outcome"] = "failure"
        result["raider_losses"] = max(1, round(num_raiders * 0.30))
        result["loot_silver"] = 0
        result["loot_livestock"] = 0

    # Apply consequences
    if result["loot_silver"] > 0:
        target_econ["silver_treasury"] = max(0, target_econ["silver_treasury"] - result["loot_silver"])
    if result["loot_livestock"] > 0:
        # Remove sheep first
        livestock = target_econ.get("livestock", {})
        removed = 0
        for animal in ("sheep", "goats", "pigs", "cattle"):
            while removed < result["loot_livestock"] and livestock.get(animal, 0) > 0:
                livestock[animal] -= 1
                removed += 1

    # Feud escalation
    modify_feud(state, attacker, target, 1, f"Raid by {attacker}")

    # Log
    log_event(state, f"Raid: {attacker} → {target} ({num_raiders} raiders). Outcome: {result['outcome']}. "
              f"Loot: {result['loot_silver']}s, {result['loot_livestock']} livestock. "
              f"Raider losses: {result['raider_losses']}")

    return result


# ============================================================
# Event Integration
# ============================================================

from event_manager import load_all_events  # noqa: E402

_EVENT_CACHE: list[dict] | None = None


def _get_events() -> list[dict]:
    """Lazy-load event database once."""
    global _EVENT_CACHE
    if _EVENT_CACHE is None:
        _EVENT_CACHE = load_all_events()
    return _EVENT_CACHE


def get_events_for_day(year: int, day: int) -> list[dict]:
    """Return events matching a specific year and day."""
    return [e for e in _get_events() if e.get("year") == year and e.get("day") == day]


def get_events_for_season(year: int, season: str) -> list[dict]:
    """Return events matching a specific year and season."""
    return [e for e in _get_events() if e.get("year") == year and e.get("season") == season]


def apply_event_effects(state: dict, event: dict) -> list[str]:
    """Apply an event's effects dict to the simulation state. Returns log lines."""
    effects = event.get("effects", {})
    if not effects:
        return []
    logs = []
    eid = event.get("id", "???")
    location = event.get("location")
    for key, value in effects.items():
        if key == "dark_arts" and location:
            # Modify dark_arts_level on the union controlling this location
            for union in state.get("unions", []):
                if location in union.get("members", []) or location == union.get("seat"):
                    old = union.get("dark_arts_level", 0)
                    union["dark_arts_level"] = max(0, old + value)
                    logs.append(f"[{eid}] {union['name']} dark_arts {old}→{union['dark_arts_level']}")
                    break
        elif key == "morale":
            state.setdefault("band_state", {})["morale"] = (
                state.get("band_state", {}).get("morale", 50) + value
            )
            logs.append(f"[{eid}] band morale {value:+d}")
        elif key == "cohesion":
            state.setdefault("band_state", {})["cohesion"] = (
                state.get("band_state", {}).get("cohesion", 50) + value
            )
            logs.append(f"[{eid}] band cohesion {value:+d}")
        elif key == "war_readiness" and location:
            for union in state.get("unions", []):
                if location in union.get("members", []) or location == union.get("seat"):
                    modify_war_readiness(state, union["name"], value, f"event {eid}")
                    logs.append(f"[{eid}] {union['name']} war_readiness {value:+d}")
                    break
        elif key == "food_stores" and location:
            econ = state.get("economies", {}).get(location, {})
            if econ:
                old = econ.get("food_stores_days", 0)
                econ["food_stores_days"] = max(0, old + value)
                logs.append(f"[{eid}] {location} food_stores {old}→{econ['food_stores_days']}")
        elif key == "population" and location:
            demo = state.get("demographics", {}).get(location, {})
            if demo:
                old = demo.get("population", 0)
                demo["population"] = max(0, old + value)
                logs.append(f"[{eid}] {location} population {old}→{demo['population']}")
        else:
            logs.append(f"[{eid}] unhandled effect: {key}={value}")
    return logs


def fire_events_for_week(state: dict) -> list[str]:
    """Check and fire any events matching the current week's day range."""
    date = state.get("current_date", {})
    year = date.get("year", 312)
    day = date.get("day_of_year", 1)
    logs = []
    for evt in _get_events():
        if evt.get("year") == year and abs(evt.get("day", -999) - day) <= 3:
            title = evt.get("title", evt.get("id", "???"))
            logs.append(f"EVENT FIRED: {evt.get('id')} — {title}")
            logs.extend(apply_event_effects(state, evt))
            log_event(state, f"Event triggered: {evt.get('id')} — {title}")
    return logs


# ============================================================
# Seasonal Tick — §18.11
# ============================================================


def tick_week(state: dict) -> list[dict]:
    """Advance all settlements by one week. Returns economy reports."""
    reports = []
    for name in state.get("demographics", {}):
        r = economy_tick_week(state, name)
        if r:
            reports.append(r)
    apply_union_economy_week(state)
    apply_dark_arts_economy_week(state)
    apply_wolfshead_economy_week(state)
    apply_contract_market_week(state)
    # Fire any events matching this week
    event_logs = fire_events_for_week(state)
    if event_logs:
        reports.append({"type": "events", "logs": event_logs})
    # Advance day
    state["current_date"]["day_of_year"] += 7
    if state["current_date"]["day_of_year"] > 360:
        state["current_date"]["day_of_year"] -= 360
        state["current_date"]["year"] += 1
    state["current_date"]["season"] = day_to_season(state["current_date"]["day_of_year"])
    return reports


def tick_season(state: dict) -> dict:
    """Advance one full season (~13 weeks economy, ~3 months population)."""
    summary = {
        "economy_weeks": [],
        "population_changes": {},
        "feud_changes": [],
        "union_events": [],
        "dark_arts_events": [],
        "narrative": [],
    }

    # Economy: 13 weekly ticks
    for _ in range(13):
        reports = tick_week(state)
        summary["economy_weeks"].append(reports)

    # Population: 3 monthly ticks
    for name in list(state.get("demographics", {})):
        total_changes = {"births": 0, "deaths": 0, "starvation": 0}
        for _ in range(3):
            c = population_tick_month(state, name)
            for k in total_changes:
                total_changes[k] += c.get(k, 0)
        summary["population_changes"][name] = total_changes

    # Feud de-escalation: 1 year of peace = -1
    for feud in state.get("feuds", []):
        feud["duration_seasons"] = feud.get("duration_seasons", 0) + 1
        if feud["duration_seasons"] >= 4 and feud["level"] > 0:
            old_level = feud["level"]
            feud["level"] = max(0, feud["level"] - 1)
            if feud["level"] != old_level:
                summary["feud_changes"].append(
                    f"{feud['pair'][0]} ↔ {feud['pair'][1]}: de-escalated to "
                    f"{feud['level']} ({FEUD_LABELS[feud['level']]}) — peace decay"
                )
            feud["duration_seasons"] = 0

    # Union checks
    for union in state.get("unions", []):
        # War readiness drift based on overjarl personality
        stats = union.get("overjarl_stats", {})
        if union["type"] == "military" and union["war_readiness"] < 5:
            # Aggressive overjails push war readiness
            if random.randint(1, 100) <= 40:
                modify_war_readiness(state, union["name"], 1, "overjarl ambition")
                summary["union_events"].append(f"{union['name']}: war readiness +1 (ambition)")

        # Food-based war readiness decrease
        seat_econ = state["economies"].get(union["seat"], {})
        if seat_econ.get("food_stores_days", 999) < 60:
            modify_war_readiness(state, union["name"], -1, "food shortage at seat")
            summary["union_events"].append(f"{union['name']}: war readiness -1 (low food)")

        # Cohesion check
        if union["cohesion"] < 3 and union["war_readiness"] > 0:
            modify_war_readiness(state, union["name"], -1, "low cohesion")

        # Dark arts
        if union.get("dark_arts_level", 0) > 0:
            events = dark_arts_consequences(state, union)
            summary["dark_arts_events"].extend(events)

    return summary


# ============================================================
# Allthing — §18.10
# ============================================================


# ============================================================
# Atrocity / Bounty / Feud Stage — §11 economics
# ============================================================

_BAND_STATE_FILE = DATA_DIR / "band_state.yaml"

_FEUD_STAGE_LABELS = {
    0: "Cold",
    1: "Resentful",
    2: "Coordinating",
    3: "Armed",
    4: "Vengeance",
}

_BOUNTY_TIERS = [
    (40,  "local_farmers"),
    (150, "regional_hunters"),
    (400, "professional_hunters"),
]

_PERSONAL_CRIME_BASE = {
    1: 5,
    2: 15,
    3: 40,
    4: 90,
    5: 180,
}

_PERSONAL_BOUNTY_TIERS = [
    (40, "local_hunters"),
    (150, "regional_hunters"),
    (400, "professional_hunters"),
]


def _load_settlements_list() -> tuple[list[dict], dict]:
    """Return (settlements list, {header comment}) from settlements.yaml."""
    with open(SETTLEMENTS_FILE, 'r', encoding='utf-8') as f:
        raw = f.read()
    data = yaml.safe_load(raw)
    header = "\n".join(ln for ln in raw.splitlines() if ln.startswith('#'))
    return data.get('settlements', []), header


def _save_settlements_list(settlements: list[dict], header: str = "") -> None:
    if _DRY_RUN:
        return
    with open(SETTLEMENTS_FILE, 'w', encoding='utf-8') as f:
        if header:
            f.write(header + "\n\n")
        yaml.dump({'settlements': settlements}, f, allow_unicode=True, sort_keys=False)


def _load_band_bs() -> dict:
    with open(_BAND_STATE_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def _save_band_bs(data: dict) -> None:
    if _DRY_RUN:
        return
    with open(_BAND_STATE_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


def _find_member(bd: dict, member_name: str) -> dict | None:
    needle = member_name.lower()
    for m in bd.get('members', []):
        if m.get('name', '').lower() == needle:
            return m
    return None


def _personal_bounty_tier(amount: int) -> str:
    for threshold, label in _PERSONAL_BOUNTY_TIERS:
        if amount < threshold:
            return label
    return "open_season"


def _append_named_man_bounty(band: dict, member_name: str, amount: int,
                             issuer: str, reason: str) -> None:
    band.setdefault('named_man_bounties', [])
    band['named_man_bounties'].append({
        "name": member_name,
        "amount_silver": amount,
        "tier": _personal_bounty_tier(amount),
        "issuing_settlement": issuer,
        "reason": reason,
        "day": band.get('day_of_year', 0),
    })


def cmd_personal_crime(member_name: str, settlement_name: str, crime_type: str,
                       severity: int, witnesses: int = 0) -> dict:
    """Record a personal crime and apply bounty escalation to one member."""
    bd = _load_band_bs()
    band = bd['band']
    member = _find_member(bd, member_name)
    if member is None:
        return {"error": f"Member '{member_name}' not found"}

    base = _PERSONAL_CRIME_BASE.get(severity)
    if base is None:
        return {"error": f"Invalid severity: {severity}"}

    w = max(0, min(witnesses, 5))
    final_bounty = int(round(base * (1 + w * 0.1)))

    member.setdefault('personal_crimes', [])
    member.setdefault('personal_bounty_silver', 0)
    member.setdefault('personal_bounty_tier', None)
    member.setdefault('outlaw_status', False)

    member['personal_crimes'].append({
        "day": band.get('day_of_year', 0),
        "settlement": settlement_name,
        "crime_type": crime_type,
        "severity": severity,
        "witnesses": witnesses,
        "blood_price_silver": final_bounty,
    })
    member['personal_bounty_silver'] += final_bounty
    member['personal_bounty_tier'] = _personal_bounty_tier(member['personal_bounty_silver'])
    if member['personal_bounty_silver'] >= 150:
        member['outlaw_status'] = True

    _append_named_man_bounty(
        band,
        member_name=member.get('name', member_name),
        amount=member['personal_bounty_silver'],
        issuer=settlement_name,
        reason=f"{crime_type} (severity {severity})",
    )

    _save_band_bs(bd)
    return {
        "member": member.get('name', member_name),
        "crime": crime_type,
        "severity": severity,
        "witnesses": witnesses,
        "bounty_added": final_bounty,
        "personal_bounty_silver": member['personal_bounty_silver'],
        "personal_bounty_tier": member['personal_bounty_tier'],
        "outlaw_status": member['outlaw_status'],
    }


def cmd_personal_bounty(member_name: str, amount: int,
                        issuer: str, reason: str) -> dict:
    """Post/update a personal bounty for a named man or wolfshead."""
    bd = _load_band_bs()
    band = bd['band']
    member = _find_member(bd, member_name)
    if member is None:
        return {"error": f"Member '{member_name}' not found"}

    member.setdefault('personal_bounty_silver', 0)
    member.setdefault('personal_bounty_tier', None)
    member.setdefault('outlaw_status', False)
    member.setdefault('personal_crimes', [])

    member['personal_bounty_silver'] = max(0, member['personal_bounty_silver'] + amount)
    member['personal_bounty_tier'] = _personal_bounty_tier(member['personal_bounty_silver'])
    if member['personal_bounty_silver'] >= 150:
        member['outlaw_status'] = True

    _append_named_man_bounty(
        band,
        member_name=member.get('name', member_name),
        amount=member['personal_bounty_silver'],
        issuer=issuer,
        reason=reason,
    )

    _save_band_bs(bd)
    return {
        "member": member.get('name', member_name),
        "amount_added": amount,
        "personal_bounty_silver": member['personal_bounty_silver'],
        "personal_bounty_tier": member['personal_bounty_tier'],
        "outlaw_status": member['outlaw_status'],
        "issuer": issuer,
        "reason": reason,
    }


def cmd_personal_amnesty(member_name: str, issuer: str,
                         cost: int = 0) -> dict:
    """Reduce or clear a personal bounty through amnesty/weregild."""
    bd = _load_band_bs()
    band = bd['band']
    member = _find_member(bd, member_name)
    if member is None:
        return {"error": f"Member '{member_name}' not found"}

    member.setdefault('personal_bounty_silver', 0)
    member.setdefault('personal_bounty_tier', None)
    member.setdefault('outlaw_status', False)
    member.setdefault('personal_crimes', [])

    old = member['personal_bounty_silver']
    new_value = max(0, old - max(0, cost)) if cost else 0
    member['personal_bounty_silver'] = new_value
    member['personal_bounty_tier'] = _personal_bounty_tier(new_value) if new_value > 0 else None
    if new_value < 150:
        member['outlaw_status'] = False

    member['personal_crimes'].append({
        "day": band.get('day_of_year', 0),
        "settlement": issuer,
        "crime_type": "amnesty",
        "severity": 0,
        "witnesses": 0,
        "blood_price_silver": -min(old, cost) if cost else -old,
    })

    _save_band_bs(bd)
    return {
        "member": member.get('name', member_name),
        "issuer": issuer,
        "old_bounty": old,
        "new_bounty": new_value,
        "personal_bounty_tier": member['personal_bounty_tier'],
        "outlaw_status": member['outlaw_status'],
    }


def cmd_personal_pressure(member_name: str, settlement_name: str) -> dict:
    """Return settlement pressure effects from personal bounty state."""
    bd = _load_band_bs()
    member = _find_member(bd, member_name)
    if member is None:
        return {"error": f"Member '{member_name}' not found"}

    bounty = int(member.get('personal_bounty_silver', 0))
    outlaw = bool(member.get('outlaw_status', False))
    crimes = member.get('personal_crimes', [])
    issued_here = [c for c in crimes if c.get('settlement', '').lower() == settlement_name.lower()]

    encounter_risk_bonus = 0
    diplomacy_penalty = 0
    if bounty >= 40:
        diplomacy_penalty -= 5
    if bounty >= 150:
        encounter_risk_bonus += 15
        diplomacy_penalty -= 10
    if outlaw and issued_here:
        encounter_risk_bonus += 20
        diplomacy_penalty -= 10

    return {
        "member": member.get('name', member_name),
        "settlement": settlement_name,
        "personal_bounty_silver": bounty,
        "outlaw_status": outlaw,
        "issued_here_count": len(issued_here),
        "encounter_risk_bonus": encounter_risk_bonus,
        "diplomacy_penalty": diplomacy_penalty,
    }


def cmd_atrocity(settlement_name: str, severity: int, rumor_range: int,
                 loot_silver: int = 0) -> dict:
    """Apply atrocity standing penalties and record in band state."""
    settlements, hdr = _load_settlements_list()
    needle = settlement_name.lower()
    victim_idx = next((i for i, s in enumerate(settlements)
                       if s.get('name', '').lower() == needle), -1)
    if victim_idx < 0:
        return {"error": f"Settlement '{settlement_name}' not found"}

    # Penalty table
    if severity <= 2:
        direct_pen = -1
        rumor_pen = 0
        post_bounty = False
    elif severity == 3:
        direct_pen = -2
        rumor_pen = -1
        post_bounty = True
    else:  # 4-5
        direct_pen = -3
        rumor_pen = -2
        post_bounty = True

    affected = []

    # Apply direct penalty to victim
    old_s = settlements[victim_idx].get('standing_with_band', 0)
    settlements[victim_idx]['standing_with_band'] = old_s + direct_pen
    settlements[victim_idx]['feud_level'] = settlements[victim_idx].get('feud_level', 0) + 1
    affected.append({"settlement": settlement_name, "standing_delta": direct_pen, "direct": True})

    # Apply rumor penalty to nearest N neighbors (by list proximity, no graph data)
    neighbors = [s for i, s in enumerate(settlements) if i != victim_idx][:rumor_range]
    for nb in neighbors:
        if rumor_pen:
            nb['standing_with_band'] = nb.get('standing_with_band', 0) + rumor_pen
            affected.append({"settlement": nb.get('name'), "standing_delta": rumor_pen, "direct": False})

    _save_settlements_list(settlements, hdr)

    # Band state: record atrocity, post bounty, morale effect
    bd = _load_band_bs()
    band = bd['band']
    band.setdefault('atrocities', [])
    band['atrocities'].append({
        "day": band.get('day_of_year', 0),
        "settlement": settlement_name,
        "severity": severity,
    })

    morale_delta = 0
    if loot_silver == 0:
        morale_delta = -1
    elif loot_silver > 20 and band.get('morale', 1) <= 2:
        morale_delta = +1
    if morale_delta:
        band['morale'] = band.get('morale', 1) + morale_delta

    bounty_silver = 0
    bounty_tier = None
    if post_bounty:
        base = severity * 25
        band['bounty_silver'] = band.get('bounty_silver', 0) + base
        bounty_silver = band['bounty_silver']
        for threshold, tier_label in _BOUNTY_TIERS:
            if bounty_silver < threshold:
                bounty_tier = tier_label
                break
        else:
            bounty_tier = "everyone"
        band['bounty_tier'] = bounty_tier

    _save_band_bs(bd)

    return {
        "settlement": settlement_name,
        "severity": severity,
        "direct_penalty": direct_pen,
        "rumor_penalty": rumor_pen,
        "neighbors_affected": len(neighbors),
        "bounty_posted": post_bounty,
        "bounty_silver": bounty_silver,
        "bounty_tier": bounty_tier,
        "morale_delta": morale_delta,
        "new_morale": band.get('morale', 1),
        "affected": affected,
    }


def cmd_bounty(amount: int, target_band: str) -> dict:
    """Post/update a bounty and determine its tier."""
    bd = _load_band_bs()
    band = bd['band']

    old_bounty = band.get('bounty_silver', 0)
    band['bounty_silver'] = old_bounty + amount

    tier = "everyone"
    for threshold, tier_label in _BOUNTY_TIERS:
        if band['bounty_silver'] < threshold:
            tier = tier_label
            break
    band['bounty_tier'] = tier
    _save_band_bs(bd)

    return {
        "target": target_band,
        "added": amount,
        "total_bounty": band['bounty_silver'],
        "tier": tier,
    }


def cmd_feud_stage(settlement_name: str) -> dict:
    """Show the feud stage for a settlement (read-only)."""
    settlements, _ = _load_settlements_list()
    needle = settlement_name.lower()
    entry = next((s for s in settlements if s.get('name', '').lower() == needle), None)
    if entry is None:
        return {"error": f"Settlement '{settlement_name}' not found"}

    feud_level = entry.get('feud_level', 0)
    clamped = max(0, min(4, feud_level))
    return {
        "settlement": settlement_name,
        "feud_level": feud_level,
        "stage": _FEUD_STAGE_LABELS[clamped],
        "standing_with_band": entry.get('standing_with_band', 0),
    }


def resolve_allthing(state: dict) -> dict:
    """Resolve the annual Allthing assembly."""
    results = {"actions": [], "feuds_resolved": [], "alliances": []}

    log_event(state, "ALLTHING convened. Leaders gather.")

    # Auto-resolve: each union leader renews alliance (cohesion +1)
    for union in state.get("unions", []):
        if union["cohesion"] < 5:
            modify_cohesion(state, union["name"], 1, "Allthing renewal ceremony")
            results["actions"].append(f"{union['overjarl']} renews {union['name']} bonds (+1 cohesion)")

    # Whispering Circle intelligence operation
    widow = find_union(state, "The Whispering Circle")
    if widow and widow.get("dark_arts_level", 0) >= 1:
        stats = widow.get("overjarl_stats", {})
        intel_chance = widow["dark_arts_level"] * 15 + stats.get("wit", 5) * 5
        roll = random.randint(1, 100)
        if roll <= intel_chance:
            target_union = random.choice([u for u in state["unions"] if u["name"] != widow["name"]])
            results["actions"].append(
                f"Pale Widow's agents learn a hidden agenda from {target_union['name']} (roll {roll} vs {intel_chance})"
            )
            log_event(state, f"Whispering Circle intelligence success against {target_union['name']}")
        else:
            results["actions"].append(f"Pale Widow's agents fail to gather intelligence (roll {roll} vs {intel_chance})")

    # Feud resolution attempts (if any feud ≥ 3, attempt weregild)
    for feud in state.get("feuds", []):
        if feud["level"] >= 3:
            # 30% chance each Allthing that parties attempt resolution
            if random.randint(1, 100) <= 30:
                success_roll = random.randint(1, 100)
                if success_roll <= 40:
                    old = feud["level"]
                    feud["level"] = max(0, feud["level"] - 2)
                    results["feuds_resolved"].append(
                        f"{feud['pair'][0]} ↔ {feud['pair'][1]}: weregild accepted, "
                        f"{old} → {feud['level']}"
                    )
                    log_event(state, f"Allthing: weregild accepted between {feud['pair'][0]} and {feud['pair'][1]}")
                else:
                    results["actions"].append(
                        f"Weregild offer rejected between {feud['pair'][0]} and {feud['pair'][1]}"
                    )

    return results


# ============================================================
# Display Functions
# ============================================================


def build_runtime_view_state(state: dict) -> dict:
    """Build a read-only derived state snapshot for CLI inspection."""
    view = copy.deepcopy(state)
    apply_union_economy_week(view)
    apply_dark_arts_economy_week(view)
    apply_wolfshead_economy_week(view)
    apply_contract_market_week(view)
    return view


def print_status(state: dict) -> None:
    dt = state["current_date"]
    print(f"\n{'='*60}")
    print(f"  RIMEVEGR POLITICAL STATE — Year {dt['year']}, Day {dt['day_of_year']}")
    print(f"  Season: {dt['season']}  |  Month: {dt.get('month', '?')}")
    print(f"{'='*60}\n")

    print("UNIONS:")
    for u in state.get("unions", []):
        _ensure_union_runtime_fields(u)
        fighters = union_combined_fighters(state, u)
        pop = union_combined_population(state, u)
        local_treasury = union_combined_treasury(state, u)
        members = [m["settlement"] for m in u["members"]]
        print(f"  {u['name']} ({u['type']})")
        print(f"    Overjarl: {u['overjarl']} (seat: {u['seat']})")
        print(f"    Members:  {', '.join(members)}")
        print(
            f"    Pop: {pop}  Fighters: {fighters}"
            f"  Member Treasuries: {local_treasury:.0f}s  Union Treasury: {u.get('treasury_silver', 0.0):.1f}s"
        )
        print(f"    Cohesion: {u['cohesion']}/5 ({COHESION_LABELS.get(u['cohesion'], '?')})")
        print(f"    War Readiness: {u['war_readiness']}/5 ({WAR_LABELS.get(u['war_readiness'], '?')})")
        if u.get("weekly_tribute_in_silver") or u.get("weekly_tribute_in_food") or u.get("weekly_levy_fighters"):
            print(
                "    Weekly Flows:"
                f" tribute {u.get('weekly_tribute_in_silver', 0.0):.1f}s,"
                f" food {u.get('weekly_tribute_in_food', 0.0):.1f},"
                f" levy {u.get('weekly_levy_fighters', 0)} fighters,"
                f" seat cost {u.get('seat_support_cost_silver', 0.0):.1f}s"
            )
        if u.get("dark_arts_upkeep_silver") or u.get("whisper_network_upkeep_silver"):
            print(
                "    Covert Burden:"
                f" dark arts {u.get('dark_arts_upkeep_silver', 0.0):.1f}s,"
                f" whisper network {u.get('whisper_network_upkeep_silver', 0.0):.1f}s,"
                f" smuggling {u.get('smuggling_income_silver', 0.0):.1f}s"
            )
        if u.get("dark_arts_level", 0) > 0:
            print(f"    Dark Arts: {u['dark_arts_level']}/5 ({DARK_LABELS.get(u['dark_arts_level'], '?')})")
        print()

    print("FEUDS:")
    for f in state.get("feuds", []):
        print(f"  {f['pair'][0]} ↔ {f['pair'][1]}: Level {f['level']} ({FEUD_LABELS[f['level']]})")
        print(f"    Cause: {f['cause']}  Duration: {f.get('duration_seasons', 0)} seasons")

    print(f"\nINDEPENDENT: {', '.join(state.get('independent', []))}")

    detailed_economies = load_detailed_economies()
    routes = load_routes()
    route_snapshots = []
    for name in state.get("economies", {}):
        route = compute_route_throughput(state, name, detailed_economies, routes)
        route_snapshots.append((name, route))
    route_snapshots.sort(key=lambda item: item[1]["throughput_total"])
    print("\nTRADE BOTTLENECKS:")
    for name, route in route_snapshots[:5]:
        print(
            f"  {name}: throughput {route['throughput_total']:.2f}, "
            f"import cost {route['import_cost_silver']:.1f}s, food imports {route['food_import_bonus']:.1f}"
        )

    outlaw_snapshots = []
    for name, econ in state.get("economies", {}).items():
        outlaw_snapshots.append((name, econ.get("outlaw_pressure", 0), econ.get("night_market_chance", 0.0)))
    outlaw_snapshots.sort(key=lambda item: item[1], reverse=True)
    print("\nOUTLAW PRESSURE:")
    for name, pressure, night_market in outlaw_snapshots[:5]:
        print(f"  {name}: pressure {pressure}/5, night market {night_market:.0%}")

    # Recent events
    events = state.get("event_log", [])
    if events:
        print(f"\nRECENT EVENTS (last 5):")
        for e in events[-5:]:
            print(f"  {e}")
    print()


def print_union(state: dict, name: str) -> None:
    union = find_union(state, name)
    if not union:
        print(f"Union not found: {name}")
        return
    union = _ensure_union_runtime_fields(union)
    fighters = union_combined_fighters(state, union)
    pop = union_combined_population(state, union)
    treasury = union_combined_treasury(state, union)

    print(f"\n{'='*50}")
    print(f"  {union['name']} — {union['type'].upper()} UNION")
    print(f"{'='*50}")
    print(f"  Overjarl: {union['overjarl']}")
    print(f"  Seat: {union['seat']}")
    print(f"  Cohesion: {union['cohesion']}/5 ({COHESION_LABELS.get(union['cohesion'], '?')})")
    print(f"  War Readiness: {union['war_readiness']}/5 ({WAR_LABELS.get(union['war_readiness'], '?')})")
    print(f"  Dark Arts: {union.get('dark_arts_level',0)}/5 ({DARK_LABELS.get(union.get('dark_arts_level',0), '?')})")
    print(
        f"  Combined: Pop {pop}, Fighters {fighters},"
        f" Member Treasuries {treasury:.0f}s, Union Treasury {union.get('treasury_silver', 0.0):.1f}s"
    )
    print(
        "  Weekly Flow:"
        f" tribute {union.get('weekly_tribute_in_silver', 0.0):.1f}s,"
        f" food {union.get('weekly_tribute_in_food', 0.0):.1f},"
        f" materials {union.get('weekly_tribute_in_materials', 0.0):.1f},"
        f" trade dues {union.get('weekly_trade_dues_silver', 0.0):.1f}s,"
        f" levy cost {union.get('weekly_levy_cost_silver', 0.0):.1f}s,"
        f" seat upkeep {union.get('seat_support_cost_silver', 0.0):.1f}s"
    )
    if union.get("dark_arts_upkeep_silver") or union.get("whisper_network_upkeep_silver"):
        print(
            "  Covert Flow:"
            f" dark-arts upkeep {union.get('dark_arts_upkeep_silver', 0.0):.1f}s,"
            f" whisper upkeep {union.get('whisper_network_upkeep_silver', 0.0):.1f}s,"
            f" smuggling {union.get('smuggling_income_silver', 0.0):.1f}s,"
            f" shock {union.get('confidence_shock_pressure', 0.0):.2f}"
        )
        if union.get("confidence_shock_targets"):
            print(f"  Confidence shock targets: {', '.join(union['confidence_shock_targets'])}")
    if union.get("support_shortfall_silver", 0.0) > 0:
        print(f"  Support shortfall: {union['support_shortfall_silver']:.1f}s paid by the seat directly")
    print(f"\n  MEMBERS:")
    for m in union["members"]:
        demo = state["demographics"].get(m["settlement"], {})
        econ = state["economies"].get(m["settlement"], {})
        print(f"    {m['settlement']} ({m['role']}) — Loyalty {m.get('loyalty','?')}/5")
        print(f"      Pop: {demo.get('total',0)}  Fighters: {demo.get('fighters',0)}  "
              f"Treasury: {econ.get('silver_treasury',0):.0f}s  Food: {econ.get('food_stores_days',0):.0f}d")
        if union.get("member_flows"):
            flow = next((item for item in union["member_flows"] if item["settlement"] == m["settlement"]), None)
            if flow:
                print(
                    f"      Weekly dues: {flow['silver_paid']:.1f}s,"
                    f" food {flow['food_paid']:.1f},"
                    f" materials {flow['materials_paid']:.1f},"
                    f" livestock {flow['livestock_paid']},"
                    f" levy {flow['levy_cost_silver']:.1f}s,"
                    f" trade bonus {flow['trade_bonus_silver']:.1f}s"
                )

    if union.get("dark_arts_practitioners"):
        print(f"\n  DARK ARTS PRACTITIONERS:")
        for p in union["dark_arts_practitioners"]:
            print(f"    {p['name']} ({p['role']}) — Health: {p.get('health','unknown')}")
            print(f"      Capabilities: {', '.join(p.get('capabilities', []))}")

    if union.get("whisper_agents"):
        print(f"\n  WHISPER AGENTS:")
        for a in union["whisper_agents"]:
            print(f"    {a['location']} — Cover: {a['cover']} (quality {a['quality']}/3)")
    print()


def print_feuds(state: dict) -> None:
    print(f"\n{'='*50}")
    print(f"  ACTIVE FEUDS")
    print(f"{'='*50}")
    for f in state.get("feuds", []):
        label = FEUD_LABELS[f["level"]]
        trade = FEUD_TRADE_MOD[f["level"]]
        print(f"  {f['pair'][0]} ↔ {f['pair'][1]}")
        print(f"    Level: {f['level']}/4 ({label})  Trade: {trade*100:.0f}%")
        print(f"    Cause: {f['cause']}")
        print(f"    Duration: {f.get('duration_seasons', 0)} seasons")
    print()


def print_economy(state: dict, name: str) -> None:
    detailed = load_detailed_economies()
    settlements_data = load_settlements()
    econ = state["economies"].get(name, {})
    demo = state["demographics"].get(name, {})
    if not econ:
        print(f"No economy data for: {name}")
        return
    econ = _ensure_economy_runtime_fields(
        state,
        name,
        detailed_economies=detailed,
        settlements_data=settlements_data,
    )
    season = day_to_season(state["current_date"]["day_of_year"])
    route_effects = compute_route_throughput(state, name, detailed, load_routes())
    print(f"\n{'='*50}")
    print(f"  {name} — ECONOMY ({season})")
    print(f"{'='*50}")
    print(f"  Food stores: {econ['food_stores_days']:.0f} / {econ.get('food_stores_max',0)} person-days")
    print(f"  Crop fields: {econ['crop_fields']}")
    livestock = econ.get("livestock", {})
    print(f"  Livestock: {', '.join(f'{v} {k}' for k,v in livestock.items() if v > 0)}")
    print(f"  Treasury: {econ['silver_treasury']:.0f} silver")
    print(f"  Weekly income: {econ['weekly_trade_income']}s  Expenses: {econ['weekly_expenses']}s")
    print(
        f"  Route throughput: {route_effects['throughput_total']:.2f}"
        f"  | Export bonus: {route_effects['export_bonus_silver']:.1f}s"
        f"  | Import drag: {route_effects['import_cost_silver']:.1f}s"
        f"  | Food imports: {route_effects['food_import_bonus']:.1f}"
    )
    print(
        f"  Market liquidity: {econ.get('market_liquidity', 1.0):.2f}"
        f"  | Local price pressure: ×{econ.get('local_price_pressure', 1.0):.2f}"
    )
    if route_effects["active_routes"]:
        print("  Active routes:")
        for route in route_effects["active_routes"]:
            print(
                f"    - {route['route_id']} → {route['to']}: "
                f"{route['throughput']:.2f} ({route['access']})"
            )
    if econ.get("route_partner_losses"):
        print(f"  Trade partner losses: {', '.join(econ['route_partner_losses'])}")
    if econ.get("route_disruption_flags"):
        print(f"  Route disruptions: {', '.join(econ['route_disruption_flags'])}")
    if econ.get("weekly_production_by_good"):
        print("  Weekly production:")
        for good, units in econ["weekly_production_by_good"].items():
            print(f"    - {good}: {units:.1f} units")
    stocks = econ.get("commodity_stocks", {})
    if stocks:
        print("  Commodity stocks:")
        for good, units in sorted(stocks.items()):
            print(f"    - {good}: {units:.1f}")
    stock_buckets = econ.get("stock_buckets", {})
    if stock_buckets:
        capacities = econ.get("stock_capacities", {})
        print(
            "  Stock buckets:"
            f" food={stock_buckets.get('food', 0.0):.1f}/{capacities.get('food', 0.0):.1f},"
            f" materials={stock_buckets.get('materials', 0.0):.1f}/{capacities.get('materials', 0.0):.1f},"
            f" trade={stock_buckets.get('trade', 0.0):.1f}/{capacities.get('trade', 0.0):.1f}"
        )
    print(
        f"  Dependency health: {econ.get('dependency_health', 1.0):.2f}"
        f"  | Repair penalty: {econ.get('repair_capacity_penalty', 0)}"
        f"  | Readiness penalty: {econ.get('military_readiness_penalty', 0)}"
        f"  | Vulnerability pressure: {econ.get('vulnerability_pressure', 0)}"
    )
    if econ.get("unmet_imports"):
        print("  Unmet imports:")
        for item in econ["unmet_imports"]:
            essential = " essential" if item.get("essential") else ""
            print(
                f"    - {item['good']}: short {item['short_units']:.1f}"
                f" [{item['urgency']}{essential}]"
            )
    if econ.get("shortage_flags"):
        print(f"  Shortage flags: {', '.join(econ['shortage_flags'])}")
    if econ.get("strategic_resource_flags"):
        print(f"  Strategic resources: {', '.join(econ['strategic_resource_flags'])}")
    if econ.get("union_membership"):
        print(
            f"  Union: {econ['union_membership']}"
            f"  | Tribute paid: {econ.get('union_tribute_paid_silver', 0.0):.1f}s"
            f" + food {econ.get('union_tribute_paid_food', 0.0):.1f}"
            f" + materials {econ.get('union_tribute_paid_materials', 0.0):.1f}"
        )
        if econ.get("union_support_burden_silver") or econ.get("union_levy_cost_silver") or econ.get("union_trade_bonus_silver"):
            print(
                f"  Union burdens: service {econ.get('union_support_burden_silver', 0.0):.1f}s,"
                f" levy {econ.get('union_levy_cost_silver', 0.0):.1f}s,"
                f" trade bonus {econ.get('union_trade_bonus_silver', 0.0):.1f}s,"
                f" trade dues {econ.get('union_trade_dues_silver', 0.0):.1f}s"
            )
    if econ.get("covert_fear_pressure") or econ.get("confidence_shock_pressure"):
        print(
            f"  Covert pressure: fear {econ.get('covert_fear_pressure', 0.0):.2f},"
            f" confidence shock {econ.get('confidence_shock_pressure', 0.0):.2f},"
            f" smuggling {econ.get('smuggling_leak_silver', 0.0):.1f}s"
        )
        if econ.get("covert_flags"):
            print(f"  Covert flags: {', '.join(econ['covert_flags'])}")
    if econ.get("outlaw_pressure") or econ.get("wolfshead_pressure_flags"):
        print(
            f"  Outlaw pressure: {econ.get('outlaw_pressure', 0)}/5"
            f"  | Night market chance: {econ.get('night_market_chance', 0.0):.0%}"
            f"  | Tribute drag: {econ.get('wolfshead_tribute_drag_silver', 0.0):.1f}s"
            f"  | Merc pressure: {econ.get('mercenary_competition_pressure', 0.0):.1f}"
        )
        if econ.get("wolfshead_pressure_flags"):
            print(f"  Wolfshead flags: {', '.join(econ['wolfshead_pressure_flags'])}")
    contract_market = state.get("contract_market", {}).get("by_settlement", {}).get(name)
    if contract_market:
        print(
            f"  Contract market: {contract_market.get('offer_count', 0)} offers"
            f"  | Issuer budget: {contract_market.get('issuer_budget_silver', 0.0):.1f}s"
            f"  | Payout capacity: {contract_market.get('payout_capacity_silver', 0.0):.1f}s"
            f"  | Locked value: {contract_market.get('contract_value_locked_silver', 0.0):.1f}s"
        )
        if contract_market.get("pressure_tags"):
            print(f"  Contract tags: {', '.join(contract_market['pressure_tags'])}")
        if contract_market.get("visible_offers"):
            print("  Visible offers:")
            for offer in contract_market["visible_offers"][:3]:
                print(
                    f"    - {offer['id']} [{offer['type']}]"
                    f" {offer['payment_silver']:.0f}s"
                    f" advance {offer['advance_silver']:.0f}s"
                    f" priority {offer['priority']:.2f}"
                )
    labor = econ.get("labor_allocation", {})
    print(f"  Labor: {', '.join(f'{k}={v*100:.0f}%' for k,v in labor.items())}")
    print()


def print_demographics(state: dict, name: str) -> None:
    demo = state["demographics"].get(name, {})
    if not demo:
        print(f"No demographics for: {name}")
        return
    print(f"\n{'='*50}")
    print(f"  {name} — DEMOGRAPHICS")
    print(f"{'='*50}")
    print(f"  Total: {demo['total']}")
    print(f"  Children: {demo['children']}  Elderly: {demo['elderly']}")
    print(f"  Women (working): {demo['women_working']}  Men (working): {demo['men_working']}")
    print(f"  Fighters: {demo['fighters']} ({demo['fighters']/max(1,demo['total'])*100:.0f}% of pop)")
    print()


def print_war_readiness(state: dict) -> None:
    print(f"\n{'='*50}")
    print(f"  WAR READINESS")
    print(f"{'='*50}")
    for u in state.get("unions", []):
        fighters = union_combined_fighters(state, u)
        print(f"  {u['name']}: {u['war_readiness']}/5 ({WAR_LABELS[u['war_readiness']]})")
        print(f"    Fighters: {fighters}  Cohesion: {u['cohesion']}/5")
        if u.get("dark_arts_level", 0) >= 2:
            print(f"    Dark Arts: {u['dark_arts_level']}/5 — other unions fear direct assault")
    print()


def print_dark_arts(state: dict, union_name: str) -> None:
    union = find_union(state, union_name)
    if not union:
        print(f"Union not found: {union_name}")
        return
    level = union.get("dark_arts_level", 0)
    print(f"\n{'='*50}")
    print(f"  {union['name']} — DARK ARTS: {level}/5 ({DARK_LABELS[level]})")
    print(f"{'='*50}")
    if level == 0:
        print("  No dark arts activity.")
    else:
        for p in union.get("dark_arts_practitioners", []):
            print(f"  {p['name']} ({p['role']})")
            print(f"    WYR: {p.get('wyr','?')}  WIL: {p.get('wil','?')}  Health: {p.get('health','?')}")
            print(f"    Capabilities: {', '.join(p.get('capabilities', []))}")
            if p.get("notes"):
                print(f"    Notes: {p['notes']}")
        if union.get("whisper_agents"):
            print(f"\n  INTELLIGENCE NETWORK:")
            for a in union["whisper_agents"]:
                print(f"    Agent at {a['location']} — {a['cover']} (quality {a['quality']}/3)")
    print(f"\n  RISK: ", end="")
    if level <= 1:
        print("Low. Practitioners show wear but manageable.")
    elif level == 2:
        print("Moderate. Rumors spreading. Fear building.")
    elif level == 3:
        print("High. Veil instability. Random supernatural events near seat.")
    elif level == 4:
        print("Critical. Practitioners deteriorating. 10% loss/month.")
    else:
        print("EXTREME. Veil breach possible. 20%/month catastrophic failure.")
    print()


def print_union_economy(state: dict, union_name: str | None = None) -> None:
    unions = state.get("unions", [])
    if union_name:
        union = find_union(state, union_name)
        unions = [union] if union else []
    if not unions:
        print(f"Union not found: {union_name}" if union_name else "No unions available.")
        return

    print(f"\n{'='*60}")
    print("  UNION ECONOMY")
    print(f"{'='*60}")
    for union in unions:
        union = _ensure_union_runtime_fields(union)
        print(f"  {union['name']} ({union['type']})")
        print(
            f"    Treasury: {union.get('treasury_silver', 0.0):.1f}s"
            f"  | Tribute in: {union.get('weekly_tribute_in_silver', 0.0):.1f}s"
            f" + food {union.get('weekly_tribute_in_food', 0.0):.1f}"
            f" + materials {union.get('weekly_tribute_in_materials', 0.0):.1f}"
        )
        print(
            f"    Trade dues: {union.get('weekly_trade_dues_silver', 0.0):.1f}s"
            f"  | Levy cost: {union.get('weekly_levy_cost_silver', 0.0):.1f}s"
            f"  | Levied fighters: {union.get('weekly_levy_fighters', 0)}"
        )
        print(
            f"    Seat upkeep: {union.get('seat_support_cost_silver', 0.0):.1f}s"
            f" + food {union.get('seat_support_cost_food', 0.0):.1f}"
            f"  | Shortfall: {union.get('support_shortfall_silver', 0.0):.1f}s"
        )
        if union.get("member_flows"):
            print("    Member flows:")
            for flow in union["member_flows"]:
                print(
                    f"      - {flow['settlement']}:"
                    f" silver {flow['silver_paid']:.1f},"
                    f" food {flow['food_paid']:.1f},"
                    f" materials {flow['materials_paid']:.1f},"
                    f" levy {flow['levy_cost_silver']:.1f}s,"
                    f" trade bonus {flow['trade_bonus_silver']:.1f}s"
                )
        print()


def print_wolfshead(state: dict, band_id: str | None = None, settlement: str | None = None) -> None:
    runtime = state.get("wolfshead_state", {})
    economies = state.get("economies", {})
    bands = load_wolfshead_bands()
    band_map = {band.get("id"): band for band in bands}
    selected_ids = sorted(runtime.keys() if not band_id else [band_id])

    print(f"\n{'='*60}")
    print("  WOLFSHEAD PRESSURE")
    print(f"{'='*60}")

    if settlement:
        econ = economies.get(settlement)
        if not econ:
            print(f"Settlement not found: {settlement}")
            return
        print(
            f"  {settlement}: pressure {econ.get('outlaw_pressure', 0)}/5"
            f"  | Night market {econ.get('night_market_chance', 0.0):.0%}"
            f"  | Tribute drag {econ.get('wolfshead_tribute_drag_silver', 0.0):.1f}s"
            f"  | Merc competition {econ.get('mercenary_competition_pressure', 0.0):.1f}"
        )
        if econ.get("wolfshead_pressure_flags"):
            print(f"  Flags: {', '.join(econ['wolfshead_pressure_flags'])}")
        print()
        return

    if not selected_ids:
        print("  No wolfshead runtime state available.")
        print()
        return

    for current_id in selected_ids:
        runtime_entry = runtime.get(current_id)
        band = band_map.get(current_id, {})
        if not runtime_entry:
            continue
        print(f"  {current_id} — {band.get('name', current_id)}")
        print(
            f"    Income: {runtime_entry.get('weekly_income_silver', 0.0):.1f}s"
            f"  | Food gain: {runtime_entry.get('weekly_food_gain', 0.0):.1f}"
            f"  | Desperation: {runtime_entry.get('desperation', 0.0):.2f}"
            f"  | Merc competition: {runtime_entry.get('mercenary_competition', 0.0):.2f}"
        )
        targets = runtime_entry.get("pressure_targets", [])
        if targets:
            print(f"    Pressure targets: {', '.join(targets)}")
        print()


def print_contract_market(state: dict, settlement: str | None = None) -> None:
    market = state.get("contract_market", {}).get("by_settlement", {})
    active = state.get("contract_market", {}).get("active_contracts", [])
    selected = [settlement] if settlement else sorted(market.keys())

    print(f"\n{'='*60}")
    print("  CONTRACT MARKET")
    print(f"{'='*60}")

    if not selected or (settlement and settlement not in market):
        print(f"Settlement not found in contract market: {settlement}" if settlement else "No contract market state.")
        print()
        return

    for name in selected:
        if name not in market:
            continue
        entry = market[name]
        active_here = [item for item in active if item.get("settlement") == name]
        print(f"  {name}")
        print(
            f"    Offers: {entry.get('offer_count', 0)}"
            f"  | Issuer budget: {entry.get('issuer_budget_silver', 0.0):.1f}s"
            f"  | Payout capacity: {entry.get('payout_capacity_silver', 0.0):.1f}s"
            f"  | Advance capacity: {entry.get('advance_capacity_silver', 0.0):.1f}s"
        )
        print(
            f"    Locked value: {entry.get('contract_value_locked_silver', 0.0):.1f}s"
            f"  | Advances paid: {entry.get('advances_paid_silver', 0.0):.1f}s"
            f"  | Demand: ×{entry.get('demand_multiplier', 1.0):.2f}"
        )
        if entry.get("pressure_tags"):
            print(f"    Pressure tags: {', '.join(entry['pressure_tags'])}")
        if entry.get("visible_offers"):
            print("    Visible offers:")
            for offer in entry["visible_offers"][:5]:
                print(
                    f"      - {offer['id']} [{offer['type']}]"
                    f" {offer['payment_silver']:.0f}s"
                    f" advance {offer['advance_silver']:.0f}s"
                    f" priority {offer['priority']:.2f}"
                )
        if active_here:
            print("    Active contracts:")
            for item in active_here:
                print(
                    f"      - {item['id']}: {item['status']}"
                    f" advance {item.get('advance_paid_silver', 0.0):.1f}s"
                    f" reserve {item.get('reserved_payout_silver', 0.0):.1f}s"
                    f" days left {item.get('days_remaining', 0)}"
                )
        print()


def generate_narrative(state: dict, season_num: int) -> str:
    """Generate a narrative summary of the political season."""
    lines = []
    dt = state["current_date"]
    lines.append(f"--- Season {season_num}, Year {dt['year']} ---\n")

    for union in state.get("unions", []):
        fighters = union_combined_fighters(state, union)
        pop = union_combined_population(state, union)
        name = union["name"]
        oj = union["overjarl"]
        wr = union["war_readiness"]
        co = union["cohesion"]

        if wr >= 4:
            lines.append(f"{oj}'s {name} marches. {fighters} fighters on the road. The war has begun.")
        elif wr == 3:
            lines.append(f"{oj} musters the war-host of {name}. {fighters} fighters stand ready. "
                         f"One more provocation and they march.")
        elif wr == 2:
            lines.append(f"Levies gather under {oj}'s banner. {name} mobilizes — "
                         f"{fighters} fighters drilling, stockpiles growing.")
        elif wr == 1:
            lines.append(f"{oj} watches the borders. {name} is alert but not yet armed for war.")
        else:
            lines.append(f"{name} holds peace. {oj} tends to trade and governance.")

        if union.get("dark_arts_level", 0) >= 2:
            lines.append(f"  Dark whispers follow {name}. The practitioners work unseen.")

        if co <= 2:
            lines.append(f"  But the alliance frays. Members doubt {oj}'s vision. One shock could break it.")
        lines.append("")

    # Feuds
    hot = [f for f in state.get("feuds", []) if f["level"] >= 3]
    if hot:
        lines.append("Blood feuds burn:")
        for f in hot:
            lines.append(f"  {f['pair'][0]} and {f['pair'][1]} — {FEUD_LABELS[f['level']]}. {f['cause']}.")
        lines.append("")

    detailed_economies = load_detailed_economies()
    routes = load_routes()
    route_snapshots = []
    for name in state.get("economies", {}):
        route = compute_route_throughput(state, name, detailed_economies, routes)
        route_snapshots.append((name, route))
    route_snapshots.sort(key=lambda item: item[1]["throughput_total"])
    if route_snapshots:
        lines.append("Trade pressure:")
        for name, route in route_snapshots[:3]:
            lines.append(
                f"  {name}: throughput {route['throughput_total']:.2f}, "
                f"import drag {route['import_cost_silver']:.1f}s."
            )
        lines.append("")

    # Recent events
    events = state.get("event_log", [])[-3:]
    if events:
        lines.append("Recent events:")
        for e in events:
            lines.append(f"  {e}")

    return "\n".join(lines)


# ============================================================
# CLI
# ============================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="village_politics",
        description="Iron Ledger — Village Political Simulation (§18)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview outcomes without writing state files",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show current political state")

    p_union = sub.add_parser("union", help="Show specific union")
    p_union.add_argument("--name", required=True)
    p_union_econ = sub.add_parser("union-economy", help="Show union treasury and tribute flows")
    p_union_econ.add_argument("--name")

    sub.add_parser("feuds", help="Show all feuds")

    p_tick = sub.add_parser("tick", help="Advance time")
    tick_group = p_tick.add_mutually_exclusive_group(required=True)
    tick_group.add_argument("--week", action="store_true")
    tick_group.add_argument("--season", action="store_true")

    sub.add_parser("allthing", help="Run annual Allthing")

    p_raid = sub.add_parser("raid", help="Resolve a raid")
    p_raid.add_argument("--from", dest="attacker", required=True)
    p_raid.add_argument("--target", required=True)
    p_raid.add_argument("--force", type=int, required=True, help="Number of raiders")

    p_econ = sub.add_parser("economy", help="Show village economy")
    p_econ.add_argument("--settlement", required=True)

    p_demo = sub.add_parser("demographics", help="Show village demographics")
    p_demo.add_argument("--settlement", required=True)

    sub.add_parser("war-readiness", help="Show war readiness for all unions")

    p_dark = sub.add_parser("dark-arts", help="Show dark arts status")
    p_dark.add_argument("--union", required=True)
    p_wolf = sub.add_parser("wolfshead", help="Show wolfshead revenue and pressure state")
    p_wolf.add_argument("--band-id")
    p_wolf.add_argument("--settlement")
    p_contract = sub.add_parser("contract-market", help="Show contract market state")
    p_contract.add_argument("--settlement")

    p_nar = sub.add_parser("narrative", help="Generate narrative summary")
    p_nar.add_argument("--season", type=int, required=True)

    p_spoil = sub.add_parser("spoilers", help="Decode all spoiler-encoded content")
    p_spoil.add_argument("--file", dest="spoiler_file",
                         help="Decode specific file (relative to project root)")

    # ── Atrocity / Bounty / Feud Stage ──
    p_atr = sub.add_parser("atrocity", help="Apply atrocity penalties to a settlement")
    p_atr.add_argument("--settlement", required=True)
    p_atr.add_argument("--severity", type=int, required=True, choices=[1, 2, 3, 4, 5])
    p_atr.add_argument("--rumor-range", type=int, default=3, dest="rumor_range",
                       help="Number of neighbor settlements in rumor range (default 3)")
    p_atr.add_argument("--loot", type=int, default=0, help="Silver looted (for morale calc)")
    p_atr.add_argument("--json", action="store_true")

    p_bty = sub.add_parser("bounty", help="Post or update a bounty")
    p_bty.add_argument("--amount", type=int, required=True, help="Silver amount")
    p_bty.add_argument("--target", type=str, required=True, help="Target band name")
    p_bty.add_argument("--json", action="store_true")

    p_fs = sub.add_parser("feud_stage", help="Show feud stage for a settlement")
    p_fs.add_argument("--settlement", required=True)
    p_fs.add_argument("--json", action="store_true")

    # ── Personal Crime / Named-Man Bounties ──
    p_pc = sub.add_parser("personal_crime", help="Record a personal crime and bounty escalation")
    p_pc.add_argument("--member", required=True)
    p_pc.add_argument("--settlement", required=True)
    p_pc.add_argument("--crime", required=True)
    p_pc.add_argument("--severity", type=int, required=True, choices=[1, 2, 3, 4, 5])
    p_pc.add_argument("--witnesses", type=int, default=0)
    p_pc.add_argument("--json", action="store_true")

    p_pb = sub.add_parser("personal_bounty", help="Post/update bounty for one member")
    p_pb.add_argument("--member", required=True)
    p_pb.add_argument("--amount", type=int, required=True)
    p_pb.add_argument("--issuer", required=True)
    p_pb.add_argument("--reason", required=True)
    p_pb.add_argument("--json", action="store_true")

    p_pa = sub.add_parser("personal_amnesty", help="Reduce/clear personal bounty")
    p_pa.add_argument("--member", required=True)
    p_pa.add_argument("--issuer", required=True)
    p_pa.add_argument("--cost", type=int, default=0)
    p_pa.add_argument("--json", action="store_true")

    p_pp = sub.add_parser("personal_pressure", help="Show settlement pressure from personal bounty")
    p_pp.add_argument("--member", required=True)
    p_pp.add_argument("--settlement", required=True)
    p_pp.add_argument("--json", action="store_true")

    return parser


def main() -> None:
    global _DRY_RUN
    parser = build_parser()
    args = parser.parse_args()
    _DRY_RUN = bool(getattr(args, "dry_run", False))
    state = load_state()
    read_only_view_commands = {"status", "union", "union-economy", "economy", "war-readiness", "dark-arts", "wolfshead", "contract-market"}
    view_state = build_runtime_view_state(state) if args.command in read_only_view_commands else state

    if args.command == "status":
        print_status(view_state)

    elif args.command == "union":
        print_union(view_state, args.name)

    elif args.command == "union-economy":
        print_union_economy(view_state, args.name)

    elif args.command == "feuds":
        print_feuds(state)

    elif args.command == "tick":
        if args.week:
            reports = tick_week(state)
            save_state(state)
            print(f"Advanced 1 week. Day {state['current_date']['day_of_year']}, "
                  f"Year {state['current_date']['year']}.")
            for r in reports[:3]:  # Show first 3
                print(
                    f"  {r['settlement']}: food {r['stores']:.0f}d, silver {r['treasury']:.0f}s, "
                    f"routes {r.get('route_throughput', 0):.2f}"
                )
            if len(reports) > 3:
                print(f"  ... and {len(reports)-3} more settlements.")
        elif args.season:
            summary = tick_season(state)
            save_state(state)
            dt = state["current_date"]
            print(f"Advanced 1 season. Now: Day {dt['day_of_year']}, Year {dt['year']}, {dt['season']}.")
            for name, changes in summary["population_changes"].items():
                if changes["births"] or changes["deaths"]:
                    print(f"  {name}: +{changes['births']} births, -{changes['deaths']} deaths")
            for e in summary["union_events"]:
                print(f"  {e}")
            for e in summary["dark_arts_events"]:
                print(f"  [DARK] {e}")
            if summary["economy_weeks"]:
                last_week = summary["economy_weeks"][-1]
                for r in last_week[:3]:
                    print(
                        f"  [TRADE] {r['settlement']}: throughput {r.get('route_throughput', 0):.2f}, "
                        f"import drag {r.get('import_cost_silver', 0):.1f}s"
                    )

    elif args.command == "allthing":
        results = resolve_allthing(state)
        save_state(state)
        print("\n--- ALLTHING RESULTS ---")
        for a in results["actions"]:
            print(f"  {a}")
        for f in results["feuds_resolved"]:
            print(f"  [FEUD] {f}")
        for a in results["alliances"]:
            print(f"  [ALLIANCE] {a}")

    elif args.command == "raid":
        result = resolve_raid(state, args.attacker, args.target, args.force)
        save_state(state)
        print(f"\n--- RAID: {result['attacker']} → {result['target']} ---")
        print(f"  Raiders: {result['raiders']}  Defenders: {result['defenders']}")
        print(f"  Force: {result['raid_force']} vs Defense: {result['defense_force']}")
        print(f"  Outcome: {result['outcome']}")
        if result.get("loot_silver"):
            print(f"  Loot: {result['loot_silver']}s, {result['loot_livestock']} livestock")
        print(f"  Raider losses: {result.get('raider_losses', 0)}")

    elif args.command == "economy":
        print_economy(view_state, args.settlement)

    elif args.command == "demographics":
        print_demographics(state, args.settlement)

    elif args.command == "war-readiness":
        print_war_readiness(view_state)

    elif args.command == "dark-arts":
        print_dark_arts(view_state, args.union)

    elif args.command == "wolfshead":
        print_wolfshead(view_state, args.band_id, args.settlement)

    elif args.command == "contract-market":
        print_contract_market(view_state, args.settlement)

    elif args.command == "narrative":
        text = generate_narrative(state, args.season)
        print(text)

    elif args.command == "spoilers":
        from spoiler_codec import decode_file  # noqa: lazy import
        spoiler_files = [
            PROJECT_DIR / "11_VILLAGES_AND_SETTLEMENTS.md",
            PROJECT_DIR / "20_SIMULATION_RULES.md",
            PROJECT_DIR / "data" / "political_state.yaml",
            PROJECT_DIR / "skills" / "novel-writing" / "references" / "political_villages.md",
        ]
        if args.spoiler_file:
            target = PROJECT_DIR / args.spoiler_file
            if not target.exists():
                print(f"File not found: {target}")
                return
            spoiler_files = [target]
        for fpath in spoiler_files:
            if not fpath.exists():
                continue
            blocks = decode_file(str(fpath))
            if blocks:
                print(f"\n=== {fpath.name} ({len(blocks)} spoiler blocks) ===")
                for i, block in enumerate(blocks, 1):
                    print(f"\n--- Block {i} ---")
                    print(block)

    elif args.command == "atrocity":
        result = cmd_atrocity(
            args.settlement,
            args.severity,
            args.rumor_range,
            getattr(args, "loot", 0),
        )
        if "error" in result:
            print(result["error"])
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Atrocity: {args.settlement} | severity {args.severity}")
            print(f"  Direct penalty: {result['direct_penalty']} standing")
            if result['rumor_penalty']:
                print(f"  Rumor ({result['neighbors_affected']} settlements): {result['rumor_penalty']} standing")
            if result['bounty_posted']:
                print(f"  Bounty posted: {result['bounty_silver']} silver ({result['bounty_tier']})")
            if result['morale_delta']:
                print(f"  Morale Δ: {result['morale_delta']:+d} → {result['new_morale']}")

    elif args.command == "bounty":
        result = cmd_bounty(args.amount, args.target)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Bounty on {result['target']}: +{result['added']} silver "
                  f"(total {result['total_bounty']} s) — tier: {result['tier']}")

    elif args.command == "feud_stage":
        result = cmd_feud_stage(args.settlement)
        if "error" in result:
            print(result["error"])
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"{args.settlement}: feud {result['feud_level']} → {result['stage']} "
                  f"| standing {result['standing_with_band']}")

    elif args.command == "personal_crime":
        result = cmd_personal_crime(
            member_name=args.member,
            settlement_name=args.settlement,
            crime_type=args.crime,
            severity=args.severity,
            witnesses=args.witnesses,
        )
        if "error" in result:
            print(result["error"])
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Personal crime recorded for {result['member']}: {result['crime']} "
                  f"(sev {result['severity']})")
            print(f"  Bounty +{result['bounty_added']}s → {result['personal_bounty_silver']}s "
                  f"({result['personal_bounty_tier']})")
            if result['outlaw_status']:
                print("  ⚠ Outlaw status active")

    elif args.command == "personal_bounty":
        result = cmd_personal_bounty(
            member_name=args.member,
            amount=args.amount,
            issuer=args.issuer,
            reason=args.reason,
        )
        if "error" in result:
            print(result["error"])
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Personal bounty on {result['member']}: +{result['amount_added']}s "
                  f"→ {result['personal_bounty_silver']}s ({result['personal_bounty_tier']})")
            if result['outlaw_status']:
                print("  ⚠ Outlaw status active")

    elif args.command == "personal_amnesty":
        result = cmd_personal_amnesty(
            member_name=args.member,
            issuer=args.issuer,
            cost=args.cost,
        )
        if "error" in result:
            print(result["error"])
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Amnesty: {result['member']} at {result['issuer']} "
                  f"{result['old_bounty']}s → {result['new_bounty']}s")
            if not result['outlaw_status']:
                print("  Outlaw status cleared")

    elif args.command == "personal_pressure":
        result = cmd_personal_pressure(
            member_name=args.member,
            settlement_name=args.settlement,
        )
        if "error" in result:
            print(result["error"])
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Pressure for {result['member']} in {result['settlement']}: ")
            print(f"  Encounter risk bonus: +{result['encounter_risk_bonus']}")
            print(f"  Diplomacy penalty: {result['diplomacy_penalty']}")


if __name__ == "__main__":
    main()
