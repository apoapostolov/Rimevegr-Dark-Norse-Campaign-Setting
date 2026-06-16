#!/usr/bin/env python3
"""
Iron Ledger — Financial Ledger

Manages treasury, pay cycles, loot division, and financial tracking for a
Svarthird. All rates from 20_SIMULATION_RULES.md §8.

Usage:
    python ledger.py pay --band-file band.json --week 12
    python ledger.py loot --total 120 --archetype standard
    python ledger.py status --treasury-file treasury.json
    python ledger.py mission-pay --band-file band.json --days 3
    python ledger.py non-payment --days-late 14
"""

import argparse
import json
import os
import random
import sys

sys.path.insert(0, __file__ and __import__('os').path.dirname(__file__) or '.')
from engine import roll_d100

try:
    import yaml
except ImportError:
    yaml = None

# --- Pay Rates (in copper; 1 silver = 10 copper) ---
WEEKLY_RETAINER = {
    "common": 20,       # 2 silver
    "veteran": 30,      # 3 silver
    "named_man": 50,    # 5 silver
    "shield_maiden": 30, # 3 silver (veteran rate)
}

DAILY_MISSION = {
    "common": 5,        # 5 copper
    "veteran": 10,      # 1 silver
    "named_man": 15,    # 1 silver 5 copper
}

# --- Loot Division ---
LOOT_SPLITS = {
    "tyrant": {"captain": 0.60, "named": 0.20, "veteran": 0.12, "common": 0.08},
    "standard": {"captain": 0.40, "named": 0.25, "veteran": 0.20, "common": 0.15},
    "fraternal": {"captain": 0.25, "named": 0.25, "veteran": 0.25, "common": 0.25},
    "kin_clan": {"captain": 0.20, "named": 0.20, "veteran": 0.25, "common": 0.35},
}

# --- Non-Payment Table ---
NON_PAYMENT_TABLE = [
    (15, "desertion", "D3 unhappy men desert at night. May sell information."),
    (30, "debt_demand", "Named Man demands written debt acknowledgment."),
    (50, "shaken", "Band becomes Shaken for the week (-5 to all)."),
    (70, "confrontation", "Sergeant confronts captain publicly. Command check or Morale -1."),
    (85, "muttering", "Quiet muttering. No immediate effect this week."),
    (100, "acceptance", "Men accept for now. Next non-payment rolls twice."),
]


def copper_to_display(copper: int) -> str:
    """Convert copper to display string (e.g., '3 silver 5 copper')."""
    silver = copper // 10
    remainder = copper % 10
    parts = []
    if silver:
        parts.append(f"{silver} silver")
    if remainder or not parts:
        parts.append(f"{remainder} copper")
    return " ".join(parts)


def calculate_weekly_retainer(members: list[dict]) -> dict:
    """Calculate weekly retainer cost for all band members."""
    total = 0
    breakdown = []
    for m in members:
        rank = m.get("rank", "common").lower().replace(" ", "_")
        if rank == "captain":
            breakdown.append({"name": m["name"], "rank": rank, "pay": 0, "note": "takes from treasury"})
            continue
        pay = WEEKLY_RETAINER.get(rank, WEEKLY_RETAINER["common"])
        total += pay
        breakdown.append({"name": m["name"], "rank": rank, "pay": pay})

    return {
        "total_copper": total,
        "total_display": copper_to_display(total),
        "breakdown": breakdown,
    }


def calculate_mission_pay(members: list[dict], days: int) -> dict:
    """Calculate mission pay (daily rate) for active contract days."""
    total = 0
    breakdown = []
    for m in members:
        rank = m.get("rank", "common").lower().replace(" ", "_")
        if rank == "captain":
            breakdown.append({"name": m["name"], "rank": rank, "pay": 0, "note": "captain share"})
            continue
        daily = DAILY_MISSION.get(rank, DAILY_MISSION["common"])
        pay = daily * days
        total += pay
        breakdown.append({"name": m["name"], "rank": rank, "daily": daily, "days": days, "pay": pay})

    return {
        "days": days,
        "total_copper": total,
        "total_display": copper_to_display(total),
        "breakdown": breakdown,
    }


def divide_loot(total_silver: int, archetype: str, counts: dict) -> dict:
    """Divide loot by band archetype.
    counts = {"captain": 1, "named": 3, "veteran": 4, "common": 6}
    """
    splits = LOOT_SPLITS.get(archetype, LOOT_SPLITS["standard"])
    total_copper = total_silver * 10
    result = {}
    for rank, fraction in splits.items():
        pool = int(total_copper * fraction)
        count = counts.get(rank, 0)
        per_person = pool // count if count > 0 else 0
        remainder = pool - (per_person * count) if count > 0 else pool
        result[rank] = {
            "pool_copper": pool,
            "pool_display": copper_to_display(pool),
            "count": count,
            "per_person_copper": per_person,
            "per_person_display": copper_to_display(per_person),
            "remainder_copper": remainder,
        }

    return {
        "total_silver": total_silver,
        "archetype": archetype,
        "division": result,
    }


def roll_non_payment(days_late: int, double: bool = False) -> list[dict]:
    """Roll on non-payment table. days_late >= 14 for retainer, >= 3 for mission."""
    results = []
    rolls_needed = 2 if double else 1

    for _ in range(rolls_needed):
        roll = roll_d100()
        for threshold, event_type, description in NON_PAYMENT_TABLE:
            if roll <= threshold:
                results.append({
                    "roll": roll,
                    "event_type": event_type,
                    "description": description,
                    "days_late": days_late,
                })
                break

    return results


def treasury_status(treasury: dict) -> dict:
    """Analyze treasury health."""
    silver = treasury.get("treasury_silver", 0)
    goods_value = treasury.get("treasury_goods_value", 0)
    debts = treasury.get("total_debts_owed", 0)
    credits = treasury.get("credits_to_collect", 0)
    weekly_cost = treasury.get("weekly_retainer_cost", 0)

    total_liquid = silver + goods_value
    net_worth = total_liquid - debts + credits
    weeks_runway = (total_liquid // weekly_cost) if weekly_cost > 0 else 999

    return {
        "treasury_silver": silver,
        "goods_value_silver": goods_value,
        "total_liquid_silver": total_liquid,
        "debts_owed_silver": debts,
        "credits_pending_silver": credits,
        "net_worth_silver": net_worth,
        "weekly_retainer_cost_silver": weekly_cost,
        "weeks_runway": weeks_runway,
        "health": "healthy" if weeks_runway >= 4 else "tight" if weeks_runway >= 2 else "critical",
    }


# --- YAML Data Loaders ---

def _data_path(*parts: str) -> str:
    """Resolve a path relative to the data/ directory."""
    return os.path.join(os.path.dirname(__file__), '..', 'data', *parts)


def load_trade_goods() -> dict:
    """Load trade_goods.yaml and return the trade_goods dict (keyed by category)."""
    with open(_data_path('economy', 'trade_goods.yaml'), 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)['trade_goods']


def load_settlement_economies() -> list[dict]:
    """Load settlement_economies.yaml and return the list of settlement economy profiles."""
    with open(_data_path('economy', 'settlement_economies.yaml'), 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)['settlement_economies']


def load_war_economy() -> dict:
    """Load war_economy.yaml and return the full dict."""
    with open(_data_path('economy', 'war_economy.yaml'), 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_mercenary_costs() -> dict:
    """Load mercenary_costs.yaml and return the mercenary_costs dict."""
    with open(_data_path('economy', 'mercenary_costs.yaml'), 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)['mercenary_costs']


# --- Trade Price Logic ---

def find_trade_good(goods_data: dict, good_id_or_name: str) -> tuple[dict | None, str | None]:
    """Find a good by ID or partial name match across all categories.

    Returns (good_dict, category_name) or (None, None).
    """
    needle = good_id_or_name.lower()
    for category, items in goods_data.items():
        for item in items:
            if item.get('id', '').lower() == needle:
                return item, category
            if needle in item.get('name', '').lower():
                return item, category
            # Also match underscore-style names (e.g. "iron_hand_axe")
            if needle.replace('_', ' ') in item.get('name', '').lower():
                return item, category
    return None, None


def _find_settlement_economy(name: str) -> dict | None:
    """Find a settlement in settlement_economies.yaml by case-insensitive name."""
    economies = load_settlement_economies()
    needle = name.lower()
    for se in economies:
        if se.get('settlement', '').lower() == needle:
            return se
    return None


def calculate_trade_price(
    good: dict,
    season: str,
    wartime: bool = False,
    settlement_name: str | None = None,
) -> dict:
    """Calculate modified price for a trade good.

    Applies seasonal, wartime, and settlement price modifiers.
    """
    base = good['base_price_copper']
    modifiers_applied = []

    # Seasonal modifier
    seasonal_mod = good.get('seasonal_modifier', {}).get(season, 1.0)
    modifiers_applied.append({"type": "seasonal", "season": season, "multiplier": seasonal_mod})

    # Wartime modifier
    war_mod = good.get('wartime_modifier', 1.0) if wartime else 1.0
    if wartime:
        modifiers_applied.append({"type": "wartime", "multiplier": war_mod})

    # Settlement price modifier
    settlement_mod = 1.0
    if settlement_name:
        se = _find_settlement_economy(settlement_name)
        if se and 'market' in se:
            settlement_mod = se['market'].get('price_modifier', 1.0)
            modifiers_applied.append({
                "type": "settlement",
                "settlement": se['settlement'],
                "multiplier": settlement_mod,
            })

    final_price = int(base * seasonal_mod * war_mod * settlement_mod)
    final_price = max(1, final_price)

    return {
        "name": good['name'],
        "id": good.get('id', ''),
        "base_price_copper": base,
        "final_price_copper": final_price,
        "final_price_display": copper_to_display(final_price),
        "modifiers": modifiers_applied,
        "combined_multiplier": round(seasonal_mod * war_mod * settlement_mod, 3),
    }


# --- Upkeep Logic ---

FOOD_COST_PER_PERSON_WEEKLY = 10  # standard rations copper

def calculate_upkeep(
    band_size: int,
    veterans: int = 0,
    named: int = 0,
    season: str = "long_sun",
) -> dict:
    """Calculate total weekly band upkeep.

    Combines retainer pay, food, camp supplies, and seasonal overhead.
    """
    costs = load_mercenary_costs()

    # Find seasonal multipliers
    seasonal_entry = None
    for entry in costs.get('seasonal_costs', []):
        if entry['season'] == season:
            seasonal_entry = entry
            break
    if seasonal_entry is None:
        seasonal_entry = {"camp_modifier": 1.0, "food_modifier": 1.0}

    commons = band_size - veterans - named
    if commons < 0:
        commons = 0

    # Pay
    pay_common = commons * WEEKLY_RETAINER["common"]
    pay_veteran = veterans * WEEKLY_RETAINER["veteran"]
    pay_named = named * WEEKLY_RETAINER["named_man"]
    total_pay = pay_common + pay_veteran + pay_named

    # Food (seasonal modifier applied)
    food_raw = band_size * FOOD_COST_PER_PERSON_WEEKLY
    food_cost = int(food_raw * seasonal_entry.get('food_modifier', 1.0))

    # Camp supplies estimate (firewood + salt + medical basic + lamp oil ~ 23 copper/week base)
    camp_base = 23
    camp_cost = int(camp_base * seasonal_entry.get('camp_modifier', 1.0))

    # Seasonal overhead note
    seasonal_note = seasonal_entry.get('notes', '')

    total = total_pay + food_cost + camp_cost

    return {
        "band_size": band_size,
        "commons": commons,
        "veterans": veterans,
        "named": named,
        "season": season,
        "breakdown": {
            "pay_copper": total_pay,
            "pay_display": copper_to_display(total_pay),
            "food_copper": food_cost,
            "food_display": copper_to_display(food_cost),
            "camp_copper": camp_cost,
            "camp_display": copper_to_display(camp_cost),
        },
        "seasonal_modifiers": {
            "food": seasonal_entry.get('food_modifier', 1.0),
            "camp": seasonal_entry.get('camp_modifier', 1.0),
        },
        "total_copper": total,
        "total_display": copper_to_display(total),
        "seasonal_note": seasonal_note,
    }


# --- War Event Logic ---

EVENT_CATEGORIES = [
    "blockades", "raided_caravans", "burned_granaries", "refugee_influx",
    "war_taxes", "famine_and_shortage", "trade_disruption", "economic_opportunity",
]


def roll_war_event(season: str, category: str | None = None) -> dict:
    """Roll a random war economy event.

    If category is specified, roll from that category only.
    Otherwise, pick a category weighted by chance_per_season × seasonal modifier,
    then pick a random event from that category.
    """
    data = load_war_economy()
    events_data = data.get('war_economy_events', {})
    seasonal_mods = data.get('seasonal_modifiers', {}).get(season, {})

    if category:
        pool = events_data.get(category, [])
        if not pool:
            return {"error": f"No events in category '{category}'."}
        event = random.choice(pool)
        return _format_war_event(event, category)

    # Build weighted pool across all categories
    weighted: list[tuple[dict, str, float]] = []
    for cat in EVENT_CATEGORIES:
        cat_events = events_data.get(cat, [])
        cat_season_mult = seasonal_mods.get(cat, 1.0)
        for ev in cat_events:
            base_chance = ev.get('chance_per_season', 5)
            # Filter by season if the event has a seasons list
            ev_seasons = ev.get('seasons', ['any'])
            if 'any' not in ev_seasons and season not in ev_seasons:
                continue
            weight = base_chance * cat_season_mult
            weighted.append((ev, cat, weight))

    if not weighted:
        return {"error": f"No events available for season '{season}'."}

    events, cats, weights = zip(*weighted)
    chosen_idx = random.choices(range(len(events)), weights=weights, k=1)[0]
    return _format_war_event(events[chosen_idx], cats[chosen_idx])


def _format_war_event(event: dict, category: str) -> dict:
    """Format a war economy event for output."""
    return {
        "category": category,
        "id": event.get('id', ''),
        "name": event.get('name', ''),
        "trigger": event.get('trigger', ''),
        "severity": event.get('severity', 'unknown'),
        "affected_settlements": event.get('affected_settlements', []),
        "duration_weeks": event.get('duration_weeks', 'unknown'),
        "economic_effects": event.get('economic_effects', []),
        "mercenary_opportunities": event.get('mercenary_opportunities', []),
    }


# ───────────────────────────────────────────────────────────────────────
# Tribute, occupation, in-kind, weekly summary (§11 economics)
# ───────────────────────────────────────────────────────────────────────

_TRIBUTE_RATE = {"hamlet": 0.12, "village": 0.10, "large_village": 0.08, "town": 0.06}
_FIGHTING_MEN_RATIO = {"hamlet": 0.12, "village": 0.15, "large_village": 0.12, "town": 0.10}
_SIZE_ORDER = ["hamlet", "village", "large_village", "town", "city"]
_DIFFICULTY_MODS = {"easy": 20, "standard": 0, "hard": -15, "risky": -30}


def _load_settlements_yaml() -> tuple[list[dict], str]:
    """Load settlements.yaml; return (settlements list, header comment string)."""
    path = _data_path('settlements.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    data = yaml.safe_load(raw)
    # Preserve comment lines at top
    header = "\n".join(ln for ln in raw.splitlines() if ln.startswith('#'))
    return data.get('settlements', []), header


def _save_settlements_yaml(settlements: list[dict], header: str = "") -> None:
    path = _data_path('settlements.yaml')
    with open(path, 'w', encoding='utf-8') as f:
        if header:
            f.write(header + "\n\n")
        yaml.dump({'settlements': settlements}, f, allow_unicode=True, sort_keys=False)


def _find_settlement_by_name(name: str) -> tuple[dict | None, int, list]:
    """Return (settlement, index, full_list) or (None, -1, list)."""
    settlements, _ = _load_settlements_yaml()
    needle = name.lower()
    for i, s in enumerate(settlements):
        if s.get('name', '').lower() == needle:
            return s, i, settlements
    return None, -1, settlements


def _load_band_yaml() -> dict:
    path = _data_path('band_state.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def _save_band_yaml(data: dict) -> None:
    path = _data_path('band_state.yaml')
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


def cmd_tribute(settlement_name: str, method: str) -> dict:
    """Levy tribute from a settlement by persuasion or intimidation."""
    import random as _r
    bd = _load_band_yaml()
    band = bd['band']
    members = bd.get('members', [])
    captain = next((m for m in members if m.get('rank') == 'captain'), None)

    settlement, s_idx, all_s = _find_settlement_by_name(settlement_name)
    if settlement is None:
        return {"error": f"Settlement '{settlement_name}' not found in settlements.yaml"}

    size = settlement.get('size', 'village')
    pop = settlement.get('population', 50)
    fighting_men = max(1, int(pop * _FIGHTING_MEN_RATIO.get(size, 0.12)))
    active = [m for m in members if not m.get('wounded', False)]
    band_strength = len(active)

    ratio = band_strength / fighting_men
    if ratio >= 2.0:
        difficulty = "easy"
    elif ratio >= 1.5:
        difficulty = "standard"
    elif ratio >= 1.0:
        difficulty = "hard"
    else:
        difficulty = "risky"

    wit = captain['wit'] if captain else 4
    skills = (captain or {}).get('skills', {})
    skill = skills.get('intimidate', 0) if method == 'intimidate' else skills.get('persuade', skills.get('manipulate', 0))

    base_chance = wit * 5 + skill * 10 + 15 + _DIFFICULTY_MODS[difficulty]
    base_chance = max(5, min(95, base_chance))
    roll = _r.randint(1, 100)
    success = roll <= base_chance

    silver_yield = 0
    feud_delta = 0

    if method == 'intimidate':
        feud_delta += 1  # always on use

    if success:
        silver_yield = max(1, int(pop * _TRIBUTE_RATE.get(size, 0.10)))
        band['treasury_silver'] = band.get('treasury_silver', 0) + silver_yield
    else:
        feud_delta += 1

    # Update feud_tracker in band
    feud_key = settlement_name.lower().replace(' ', '_')
    feud_tracker = band.setdefault('feud_tracker', {})
    feud_tracker[feud_key] = feud_tracker.get(feud_key, 0) + feud_delta

    # Update settlement
    if s_idx >= 0:
        all_s[s_idx]['feud_level'] = all_s[s_idx].get('feud_level', 0) + feud_delta
        if success:
            all_s[s_idx]['standing_with_band'] = all_s[s_idx].get('standing_with_band', 0) - 1
        _, hdr = _load_settlements_yaml()
        _save_settlements_yaml(all_s, hdr)

    _save_band_yaml(bd)
    return {
        "settlement": settlement_name,
        "method": method,
        "band_strength": band_strength,
        "fighting_men": fighting_men,
        "ratio": round(ratio, 2),
        "difficulty": difficulty,
        "check_chance": base_chance,
        "roll": roll,
        "success": success,
        "silver_yield": silver_yield,
        "feud_delta": feud_delta,
        "new_feud_level": all_s[s_idx].get('feud_level', 0) if s_idx >= 0 else None,
        "new_treasury": band.get('treasury_silver', 0),
    }


def cmd_occupation(settlement_name: str, weeks: int) -> dict:
    """Occupy a settlement for N weeks; collect 1d6 silver/week, track penalties."""
    import random as _r
    bd = _load_band_yaml()
    band = bd['band']

    settlement, s_idx, all_s = _find_settlement_by_name(settlement_name)
    if settlement is None:
        return {"error": f"Settlement '{settlement_name}' not found"}

    weekly_income = []
    total_income = 0
    feud_delta = 0
    standing_delta = 0

    for w in range(1, weeks + 1):
        income = _r.randint(1, 6)
        total_income += income
        weekly_income.append(income)
        standing_delta -= 1  # floor −5 overall
        if w == 1:
            feud_delta += 1  # +1 only on establishment

    # Apply treasury gain
    band['treasury_silver'] = band.get('treasury_silver', 0) + total_income

    # Post-occupation penalties on settlement
    times_occupied = all_s[s_idx].get('times_occupied', 0) + 1
    all_s[s_idx]['times_occupied'] = times_occupied
    all_s[s_idx]['feud_level'] = all_s[s_idx].get('feud_level', 0) + feud_delta
    standing_new = max(-5, all_s[s_idx].get('standing_with_band', 0) + standing_delta)
    all_s[s_idx]['standing_with_band'] = standing_new
    all_s[s_idx]['forage_penalty'] = -1         # one column lower, 1 season
    all_s[s_idx]['trade_multiplier'] = 0.5      # ×0.5, 1 season

    # Permanent size downgrade at 2+ occupations
    downgraded = False
    if times_occupied >= 2:
        size = all_s[s_idx].get('size', 'village')
        cur_idx = _SIZE_ORDER.index(size) if size in _SIZE_ORDER else 1
        if cur_idx > 0:
            all_s[s_idx]['size'] = _SIZE_ORDER[cur_idx - 1]
            downgraded = True

    # Update band feud tracker
    feud_key = settlement_name.lower().replace(' ', '_')
    feud_tracker = band.setdefault('feud_tracker', {})
    feud_tracker[feud_key] = feud_tracker.get(feud_key, 0) + feud_delta

    _, hdr = _load_settlements_yaml()
    _save_settlements_yaml(all_s, hdr)
    _save_band_yaml(bd)

    return {
        "settlement": settlement_name,
        "weeks": weeks,
        "weekly_income": weekly_income,
        "total_income": total_income,
        "feud_delta": feud_delta,
        "standing_delta": standing_delta,
        "standing_new": standing_new,
        "times_occupied": times_occupied,
        "permanent_size_downgrade": downgraded,
        "new_size": all_s[s_idx].get('size'),
        "new_treasury": band.get('treasury_silver', 0),
    }


def cmd_in_kind(week_number: int, quantity: int, good_type: str) -> dict:
    """Check morale consequences of paying in goods instead of silver."""
    import random as _r
    bd = _load_band_yaml()
    band = bd['band']
    captain = next((m for m in bd.get('members', []) if m.get('rank') == 'captain'), None)

    morale_delta = 0
    roll = None
    passed = None
    verdict = "acceptable"

    if week_number <= 3:
        verdict = "acceptable"
    elif week_number == 4:
        # Captain persuade check
        wit = captain['wit'] if captain else 4
        skills = (captain or {}).get('skills', {})
        skill = skills.get('persuade', skills.get('manipulate', 0))
        chance = max(5, min(95, wit * 5 + skill * 10))
        roll = _r.randint(1, 100)
        passed = roll <= chance
        if not passed:
            morale_delta = -1
            verdict = "grumbling (persuade failed)"
        else:
            verdict = "barely acceptable (persuade passed)"
    else:
        morale_delta = -1
        verdict = "morale penalty (automatic)"

    if morale_delta:
        band['morale'] = band.get('morale', 1) + morale_delta

    _save_band_yaml(bd)
    return {
        "week_number": week_number,
        "quantity": quantity,
        "good_type": good_type,
        "verdict": verdict,
        "morale_delta": morale_delta,
        "persuade_roll": roll,
        "persuade_passed": passed,
        "new_morale": band.get('morale', 1),
    }


def cmd_weekly_summary() -> dict:
    """Print current-week ledger summary from band_state.yaml."""
    bd = _load_band_yaml()
    band = bd['band']
    members = bd.get('members', [])
    day = band.get('day_of_year', 0)

    # Retainer estimate
    retainer_data = calculate_weekly_retainer(members)
    retainer_silver = retainer_data['total_copper'] // 100  # copper→silver (approx)
    if retainer_data.get('total_copper', 0) % 100:
        retainer_silver += 1

    # Contract advance (if any)
    contract = band.get('current_contract', {})
    contract_advance = contract.get('advance_received', 0) if contract.get('status') == 'in_progress' else 0
    contract_note = f"Contract ({contract.get('title', '?')}) advance already received" if contract_advance else ""

    # Treasury
    opening = band.get('treasury_silver', 0)  # current value (no persistent log yet)

    return {
        "day_start": day,
        "day_end": day + 7,
        "opening_silver": opening,
        "retainer_cost_silver": retainer_silver,
        "member_count": len(members),
        "contract_advance_pending": contract_advance,
        "contract_note": contract_note,
        "current_treasury": band.get('treasury_silver', 0),
        "morale": band.get('morale', 1),
    }


# ───────────────────────────────────────────────────────────────────────
# Tribute, occupation, in-kind, weekly summary (§11 economics)
# ───────────────────────────────────────────────────────────────────────

_TRIBUTE_RATE = {"hamlet": 0.12, "village": 0.10, "large_village": 0.08, "town": 0.06}
_FIGHTING_MEN_RATIO = {"hamlet": 0.12, "village": 0.15, "large_village": 0.12, "town": 0.10}
_SIZE_ORDER = ["hamlet", "village", "large_village", "town", "city"]
_DIFFICULTY_MODS = {"easy": 20, "standard": 0, "hard": -15, "risky": -30}


def _load_settlements_yaml() -> tuple[list[dict], str]:
    """Load settlements.yaml; return (settlements list, header comment string)."""
    path = _data_path('settlements.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    data = yaml.safe_load(raw)
    # Preserve comment lines at top
    header = "\n".join(ln for ln in raw.splitlines() if ln.startswith('#'))
    return data.get('settlements', []), header


def _save_settlements_yaml(settlements: list[dict], header: str = "") -> None:
    path = _data_path('settlements.yaml')
    with open(path, 'w', encoding='utf-8') as f:
        if header:
            f.write(header + "\n\n")
        yaml.dump({'settlements': settlements}, f, allow_unicode=True, sort_keys=False)


def _find_settlement_by_name(name: str) -> tuple[dict | None, int, list]:
    """Return (settlement, index, full_list) or (None, -1, list)."""
    settlements, _ = _load_settlements_yaml()
    needle = name.lower()
    for i, s in enumerate(settlements):
        if s.get('name', '').lower() == needle:
            return s, i, settlements
    return None, -1, settlements


def _load_band_yaml() -> dict:
    path = _data_path('band_state.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def _save_band_yaml(data: dict) -> None:
    path = _data_path('band_state.yaml')
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


def cmd_tribute(settlement_name: str, method: str) -> dict:
    """Levy tribute from a settlement by persuasion or intimidation."""
    import random as _r
    bd = _load_band_yaml()
    band = bd['band']
    members = bd.get('members', [])
    captain = next((m for m in members if m.get('rank') == 'captain'), None)

    settlement, s_idx, all_s = _find_settlement_by_name(settlement_name)
    if settlement is None:
        return {"error": f"Settlement '{settlement_name}' not found in settlements.yaml"}

    size = settlement.get('size', 'village')
    pop = settlement.get('population', 50)
    fighting_men = max(1, int(pop * _FIGHTING_MEN_RATIO.get(size, 0.12)))
    active = [m for m in members if not m.get('wounded', False)]
    band_strength = len(active)

    ratio = band_strength / fighting_men
    if ratio >= 2.0:
        difficulty = "easy"
    elif ratio >= 1.5:
        difficulty = "standard"
    elif ratio >= 1.0:
        difficulty = "hard"
    else:
        difficulty = "risky"

    wit = captain['wit'] if captain else 4
    skills = (captain or {}).get('skills', {})
    skill = skills.get('intimidate', 0) if method == 'intimidate' else skills.get('persuade', skills.get('manipulate', 0))

    base_chance = wit * 5 + skill * 10 + 15 + _DIFFICULTY_MODS[difficulty]
    base_chance = max(5, min(95, base_chance))
    roll = _r.randint(1, 100)
    success = roll <= base_chance

    silver_yield = 0
    feud_delta = 0

    if method == 'intimidate':
        feud_delta += 1  # always on use

    if success:
        silver_yield = max(1, int(pop * _TRIBUTE_RATE.get(size, 0.10)))
        band['treasury_silver'] = band.get('treasury_silver', 0) + silver_yield
    else:
        feud_delta += 1

    # Update feud_tracker in band
    feud_key = settlement_name.lower().replace(' ', '_')
    feud_tracker = band.setdefault('feud_tracker', {})
    feud_tracker[feud_key] = feud_tracker.get(feud_key, 0) + feud_delta

    # Update settlement
    if s_idx >= 0:
        all_s[s_idx]['feud_level'] = all_s[s_idx].get('feud_level', 0) + feud_delta
        if success:
            all_s[s_idx]['standing_with_band'] = all_s[s_idx].get('standing_with_band', 0) - 1
        _, hdr = _load_settlements_yaml()
        _save_settlements_yaml(all_s, hdr)

    _save_band_yaml(bd)
    return {
        "settlement": settlement_name,
        "method": method,
        "band_strength": band_strength,
        "fighting_men": fighting_men,
        "ratio": round(ratio, 2),
        "difficulty": difficulty,
        "check_chance": base_chance,
        "roll": roll,
        "success": success,
        "silver_yield": silver_yield,
        "feud_delta": feud_delta,
        "new_feud_level": all_s[s_idx].get('feud_level', 0) if s_idx >= 0 else None,
        "new_treasury": band.get('treasury_silver', 0),
    }


def cmd_occupation(settlement_name: str, weeks: int) -> dict:
    """Occupy a settlement for N weeks; collect 1d6 silver/week, track penalties."""
    import random as _r
    bd = _load_band_yaml()
    band = bd['band']

    settlement, s_idx, all_s = _find_settlement_by_name(settlement_name)
    if settlement is None:
        return {"error": f"Settlement '{settlement_name}' not found"}

    weekly_income = []
    total_income = 0
    feud_delta = 0
    standing_delta = 0

    for w in range(1, weeks + 1):
        income = _r.randint(1, 6)
        total_income += income
        weekly_income.append(income)
        standing_delta -= 1  # floor −5 overall
        if w == 1:
            feud_delta += 1  # +1 only on establishment

    # Apply treasury gain
    band['treasury_silver'] = band.get('treasury_silver', 0) + total_income

    # Post-occupation penalties on settlement
    times_occupied = all_s[s_idx].get('times_occupied', 0) + 1
    all_s[s_idx]['times_occupied'] = times_occupied
    all_s[s_idx]['feud_level'] = all_s[s_idx].get('feud_level', 0) + feud_delta
    standing_new = max(-5, all_s[s_idx].get('standing_with_band', 0) + standing_delta)
    all_s[s_idx]['standing_with_band'] = standing_new
    all_s[s_idx]['forage_penalty'] = -1         # one column lower, 1 season
    all_s[s_idx]['trade_multiplier'] = 0.5      # ×0.5, 1 season

    # Permanent size downgrade at 2+ occupations
    downgraded = False
    if times_occupied >= 2:
        size = all_s[s_idx].get('size', 'village')
        cur_idx = _SIZE_ORDER.index(size) if size in _SIZE_ORDER else 1
        if cur_idx > 0:
            all_s[s_idx]['size'] = _SIZE_ORDER[cur_idx - 1]
            downgraded = True

    # Update band feud tracker
    feud_key = settlement_name.lower().replace(' ', '_')
    feud_tracker = band.setdefault('feud_tracker', {})
    feud_tracker[feud_key] = feud_tracker.get(feud_key, 0) + feud_delta

    _, hdr = _load_settlements_yaml()
    _save_settlements_yaml(all_s, hdr)
    _save_band_yaml(bd)

    return {
        "settlement": settlement_name,
        "weeks": weeks,
        "weekly_income": weekly_income,
        "total_income": total_income,
        "feud_delta": feud_delta,
        "standing_delta": standing_delta,
        "standing_new": standing_new,
        "times_occupied": times_occupied,
        "permanent_size_downgrade": downgraded,
        "new_size": all_s[s_idx].get('size'),
        "new_treasury": band.get('treasury_silver', 0),
    }


def cmd_in_kind(week_number: int, quantity: int, good_type: str) -> dict:
    """Check morale consequences of paying in goods instead of silver."""
    import random as _r
    bd = _load_band_yaml()
    band = bd['band']
    captain = next((m for m in bd.get('members', []) if m.get('rank') == 'captain'), None)

    morale_delta = 0
    roll = None
    passed = None
    verdict = "acceptable"

    if week_number <= 3:
        verdict = "acceptable"
    elif week_number == 4:
        # Captain persuade check
        wit = captain['wit'] if captain else 4
        skills = (captain or {}).get('skills', {})
        skill = skills.get('persuade', skills.get('manipulate', 0))
        chance = max(5, min(95, wit * 5 + skill * 10))
        roll = _r.randint(1, 100)
        passed = roll <= chance
        if not passed:
            morale_delta = -1
            verdict = "grumbling (persuade failed)"
        else:
            verdict = "barely acceptable (persuade passed)"
    else:
        morale_delta = -1
        verdict = "morale penalty (automatic)"

    if morale_delta:
        band['morale'] = band.get('morale', 1) + morale_delta

    _save_band_yaml(bd)
    return {
        "week_number": week_number,
        "quantity": quantity,
        "good_type": good_type,
        "verdict": verdict,
        "morale_delta": morale_delta,
        "persuade_roll": roll,
        "persuade_passed": passed,
        "new_morale": band.get('morale', 1),
    }


def cmd_weekly_summary() -> dict:
    """Print current-week ledger summary from band_state.yaml."""
    bd = _load_band_yaml()
    band = bd['band']
    members = bd.get('members', [])
    day = band.get('day_of_year', 0)

    # Retainer estimate
    retainer_data = calculate_weekly_retainer(members)
    retainer_silver = retainer_data['total_copper'] // 100  # copper→silver (approx)
    if retainer_data.get('total_copper', 0) % 100:
        retainer_silver += 1

    # Contract advance (if any)
    contract = band.get('current_contract', {})
    contract_advance = contract.get('advance_received', 0) if contract.get('status') == 'in_progress' else 0
    contract_note = f"Contract ({contract.get('title', '?')}) advance already received" if contract_advance else ""

    # Treasury
    opening = band.get('treasury_silver', 0)  # current value (no persistent log yet)

    return {
        "day_start": day,
        "day_end": day + 7,
        "opening_silver": opening,
        "retainer_cost_silver": retainer_silver,
        "member_count": len(members),
        "contract_advance_pending": contract_advance,
        "contract_note": contract_note,
        "current_treasury": band.get('treasury_silver', 0),
        "morale": band.get('morale', 1),
    }


def main():
    parser = argparse.ArgumentParser(description="Iron Ledger Financial Ledger")
    subparsers = parser.add_subparsers(dest="command")

    # --- pay ---
    pay_p = subparsers.add_parser("pay", help="Calculate weekly retainer")
    pay_p.add_argument("--band-file", type=str, help="JSON with member list")
    pay_p.add_argument("--band", type=str, help="JSON string with member list")
    pay_p.add_argument("--json", action="store_true")

    # --- mission-pay ---
    mp_p = subparsers.add_parser("mission-pay", help="Calculate mission pay")
    mp_p.add_argument("--band-file", type=str, help="JSON with member list")
    mp_p.add_argument("--band", type=str, help="JSON string with member list")
    mp_p.add_argument("--days", type=int, required=True)
    mp_p.add_argument("--json", action="store_true")

    # --- loot ---
    loot_p = subparsers.add_parser("loot", help="Divide loot")
    loot_p.add_argument("--total", type=int, required=True, help="Total loot in silver")
    loot_p.add_argument("--archetype", type=str, default="standard",
                        choices=list(LOOT_SPLITS.keys()))
    loot_p.add_argument("--captain", type=int, default=1)
    loot_p.add_argument("--named", type=int, default=3)
    loot_p.add_argument("--veteran", type=int, default=4)
    loot_p.add_argument("--common", type=int, default=6)
    loot_p.add_argument("--json", action="store_true")

    # --- non-payment ---
    np_p = subparsers.add_parser("non-payment", help="Roll non-payment consequences")
    np_p.add_argument("--days-late", type=int, required=True)
    np_p.add_argument("--double", action="store_true", help="Roll twice (previous acceptance)")
    np_p.add_argument("--json", action="store_true")

    # --- status ---
    st_p = subparsers.add_parser("status", help="Treasury health check")
    st_p.add_argument("--treasury-file", type=str, help="JSON with treasury state")
    st_p.add_argument("--treasury", type=str, help="JSON string")
    st_p.add_argument("--json", action="store_true")

    # --- trade-price ---
    tp_p = subparsers.add_parser("trade-price", help="Look up trade good price with modifiers")
    tp_p.add_argument("--good", type=str, required=True, help="Trade good ID or partial name")
    tp_p.add_argument("--season", type=str, required=True,
                      choices=["thaw", "long_sun", "harvest", "long_dark"])
    tp_p.add_argument("--wartime", action="store_true", help="Apply wartime modifier")
    tp_p.add_argument("--settlement", type=str, default=None,
                      help="Settlement name for price modifier")
    tp_p.add_argument("--json", action="store_true")

    # --- upkeep ---
    uk_p = subparsers.add_parser("upkeep", help="Calculate weekly band upkeep")
    uk_p.add_argument("--band-size", type=int, required=True)
    uk_p.add_argument("--veterans", type=int, default=0)
    uk_p.add_argument("--named", type=int, default=0)
    uk_p.add_argument("--season", type=str, default="long_sun",
                      choices=["thaw", "long_sun", "harvest", "long_dark"])
    uk_p.add_argument("--json", action="store_true")

    # --- war-event ---
    we_p = subparsers.add_parser("war-event", help="Roll a random war economy event")
    we_p.add_argument("--season", type=str, required=True,
                      choices=["thaw", "long_sun", "harvest", "long_dark"])
    we_p.add_argument("--category", type=str, default=None,
                      choices=EVENT_CATEGORIES, help="Limit to a specific category")
    we_p.add_argument("--json", action="store_true")

    # ── Tribute / Occupation / In-Kind / Weekly Summary ──
    tr_p = subparsers.add_parser("tribute", help="Levy tribute from a settlement")
    tr_p.add_argument("--settlement", type=str, required=True)
    tr_p.add_argument("--method", type=str, default="persuade",
                      choices=["persuade", "intimidate"])
    tr_p.add_argument("--json", action="store_true")

    occ_p = subparsers.add_parser("occupation", help="Occupy a settlement for N weeks")
    occ_p.add_argument("--settlement", type=str, required=True)
    occ_p.add_argument("--weeks", type=int, required=True)
    occ_p.add_argument("--json", action="store_true")

    ik_p = subparsers.add_parser("in_kind", help="Check in-kind payment consequences")
    ik_p.add_argument("--week", type=int, required=True, help="How many consecutive weeks of in-kind pay")
    ik_p.add_argument("--quantity", type=int, default=1)
    ik_p.add_argument("--good", type=str, default="grain")
    ik_p.add_argument("--json", action="store_true")

    ws_p = subparsers.add_parser("weekly_summary", help="Print weekly ledger summary")
    ws_p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "pay":
        if args.band_file:
            with open(args.band_file, 'r', encoding='utf-8') as f:
                members = json.load(f)
        else:
            members = json.loads(args.band)
        result = calculate_weekly_retainer(members)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Weekly retainer: {result['total_display']}")
            for b in result["breakdown"]:
                note = b.get("note", copper_to_display(b["pay"]))
                print(f"  {b['name']} ({b['rank']}): {note}")

    elif args.command == "mission-pay":
        if args.band_file:
            with open(args.band_file, 'r', encoding='utf-8') as f:
                members = json.load(f)
        else:
            members = json.loads(args.band)
        result = calculate_mission_pay(members, args.days)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Mission pay ({args.days} days): {result['total_display']}")

    elif args.command == "loot":
        counts = {
            "captain": args.captain,
            "named": args.named,
            "veteran": args.veteran,
            "common": args.common,
        }
        result = divide_loot(args.total, args.archetype, counts)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Loot division ({args.archetype}): {args.total} silver")
            for rank, div in result["division"].items():
                print(f"  {rank}: {div['pool_display']} total, "
                      f"{div['per_person_display']} each ({div['count']} people)")

    elif args.command == "non-payment":
        results = roll_non_payment(args.days_late, args.double)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for r in results:
                print(f"Roll {r['roll']}: [{r['event_type']}] {r['description']}")

    elif args.command == "status":
        if args.treasury_file:
            with open(args.treasury_file, 'r', encoding='utf-8') as f:
                treasury = json.load(f)
        else:
            treasury = json.loads(args.treasury)
        result = treasury_status(treasury)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Treasury: {result['treasury_silver']} silver + {result['goods_value_silver']} goods")
            print(f"Net worth: {result['net_worth_silver']} silver")
            print(f"Runway: {result['weeks_runway']} weeks ({result['health']})")

    elif args.command == "trade-price":
        if yaml is None:
            print("Error: PyYAML is required for trade-price. Install with: pip install pyyaml")
            sys.exit(1)
        goods = load_trade_goods()
        good, category = find_trade_good(goods, args.good)
        if good is None:
            print(f"Error: Trade good '{args.good}' not found.")
            sys.exit(1)
        result = calculate_trade_price(good, args.season, args.wartime, args.settlement)
        result["category"] = category
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"{result['name']} [{result['id']}] ({category})")
            print(f"  Base price: {copper_to_display(result['base_price_copper'])}")
            for m in result["modifiers"]:
                print(f"  {m['type']}: ×{m['multiplier']}")
            print(f"  Final price: {result['final_price_display']} "
                  f"(×{result['combined_multiplier']} overall)")

    elif args.command == "upkeep":
        if yaml is None:
            print("Error: PyYAML is required for upkeep. Install with: pip install pyyaml")
            sys.exit(1)
        result = calculate_upkeep(args.band_size, args.veterans, args.named, args.season)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            bd = result["breakdown"]
            print(f"Weekly upkeep ({result['band_size']} fighters, {result['season']}):")
            print(f"  Pay:  {bd['pay_display']} ({result['commons']}c/{result['veterans']}v/{result['named']}n)")
            print(f"  Food: {bd['food_display']} (×{result['seasonal_modifiers']['food']})")
            print(f"  Camp: {bd['camp_display']} (×{result['seasonal_modifiers']['camp']})")
            print(f"  TOTAL: {result['total_display']}")
            if result['seasonal_note']:
                print(f"  Season note: {result['seasonal_note']}")

    elif args.command == "war-event":
        if yaml is None:
            print("Error: PyYAML is required for war-event. Install with: pip install pyyaml")
            sys.exit(1)
        result = roll_war_event(args.season, args.category)
        if "error" in result:
            print(result["error"])
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"[{result['category']}] {result['name']} ({result['severity']})")
            print(f"  Trigger: {result['trigger']}")
            print(f"  Duration: {result['duration_weeks']} weeks")
            if result['affected_settlements']:
                print(f"  Affected: {', '.join(result['affected_settlements'])}")
            if result['economic_effects']:
                print("  Economic effects:")
                for eff in result['economic_effects']:
                    print(f"    - {eff}")
            if result['mercenary_opportunities']:
                print("  Mercenary opportunities:")
                for opp in result['mercenary_opportunities']:
                    print(f"    - {opp}")

    elif args.command == "tribute":
        if yaml is None:
            print("Error: PyYAML required for tribute command.")
            sys.exit(1)
        result = cmd_tribute(args.settlement, args.method)
        if "error" in result:
            print(result["error"])
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            outcome = "SUCCESS" if result["success"] else "FAILURE"
            print(f"Tribute: {args.settlement} | {args.method} | {outcome}")
            print(f"  Band {result['band_strength']} vs {result['fighting_men']} fighting men "
                  f"(ratio {result['ratio']}) → {result['difficulty']}")
            print(f"  Check: {result['check_chance']}% | Roll: {result['roll']}")
            if result["success"]:
                print(f"  Collected: {result['silver_yield']} silver → treasury now {result['new_treasury']} s")
            else:
                print(f"  Nothing collected. Feud +{result['feud_delta']}")

    elif args.command == "occupation":
        if yaml is None:
            print("Error: PyYAML required for occupation command.")
            sys.exit(1)
        result = cmd_occupation(args.settlement, args.weeks)
        if "error" in result:
            print(result["error"])
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Occupation: {args.settlement} × {args.weeks} weeks")
            for i, inc in enumerate(result["weekly_income"], 1):
                print(f"  Week {i}: +{inc} silver")
            print(f"  Total income: {result['total_income']} silver")
            print(f"  Standing Δ: {result['standing_delta']} → {result['standing_new']}")
            print(f"  Feud Δ: +{result['feud_delta']}")
            print(f"  Penalties: forage −1 col, trade ×0.5 (1 season)")
            if result["permanent_size_downgrade"]:
                print(f"  ⚠ Permanent size downgrade → {result['new_size']}")
            print(f"  Treasury now: {result['new_treasury']} s")

    elif args.command == "in_kind":
        result = cmd_in_kind(args.week, args.quantity, args.good)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"In-kind payment (week {result['week_number']}): {result['quantity']}× {result['good_type']}")
            print(f"  Verdict: {result['verdict']}")
            if result["morale_delta"]:
                print(f"  Morale Δ: {result['morale_delta']} → {result['new_morale']}")
            if result["persuade_roll"] is not None:
                status = "passed" if result["persuade_passed"] else "failed"
                print(f"  Persuade roll: {result['persuade_roll']} ({status})")

    elif args.command == "weekly_summary":
        if yaml is None:
            print("Error: PyYAML required for weekly_summary.")
            sys.exit(1)
        result = cmd_weekly_summary()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"=== Weekly Ledger — Day {result['day_start']} → {result['day_end']} ===")
            print(f"  Treasury:       {result['current_treasury']} silver")
            print(f"  Est. retainer:  {result['member_count']} members × est. −{result['retainer_cost_silver']} s/week")
            if result['contract_note']:
                print(f"  Contract:       {result['contract_note']}")
            print(f"  Morale:         {result['morale']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
