#!/usr/bin/env python3
"""
Iron Ledger — YAML Data Validator

Comprehensive validation of all 54 YAML data files: schema checks,
cross-reference integrity, ID uniqueness, and format compliance.

Usage:
    python scripts/validate_data.py              # Run all checks
    python scripts/validate_data.py --verbose    # Show all individual checks
    python scripts/validate_data.py --fix        # Auto-fix where possible (future)
    python scripts/validate_data.py --check settlements  # Run only one check group
"""

import argparse
import collections
import glob
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"

# ANSI colours
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"

LEVEL_COLOR = {PASS: C_GREEN, WARN: C_YELLOW, FAIL: C_RED}

# ---------------------------------------------------------------------------
# File manifest — every YAML file and its expected top-level keys
# ---------------------------------------------------------------------------

FILE_MANIFEST = {
    # Root data
    "data/band_state.yaml": ["band", "members"],
    "data/contracts_available.yaml": ["active_contract", "available_contracts"],
    "data/political_state.yaml": [
        "current_date", "unions", "feuds", "independent",
        "demographics", "economies", "event_log",
    ],
    "data/settlements.yaml": [
        "settlements", "settlement_positions", "travel_routes",
        "bypass_routes", "faction_relations", "rival_bands",
    ],
    # barrows/
    "data/barrows/barrows.yaml": ["barrows"],
    "data/barrows/encounter_tables.yaml": ["encounter_tables"],
    "data/barrows/loot_tables.yaml": ["loot_tables"],
    "data/barrows/room_templates.yaml": ["room_templates"],
    # bestiary/
    "data/bestiary/animals.yaml": ["enemies"],
    "data/bestiary/encounters.yaml": ["encounters"],
    "data/bestiary/humans.yaml": ["enemies"],
    "data/bestiary/named_enemies.yaml": ["enemies"],
    "data/bestiary/supernatural.yaml": ["enemies"],
    "data/bestiary/undead.yaml": ["enemies"],
    "data/bestiary/world_bosses.yaml": ["enemies"],
    # contracts/
    "data/contracts/desperate_contracts.yaml": ["contracts"],
    "data/contracts/faction_contracts.yaml": ["contracts"],
    "data/contracts/settlement_contracts.yaml": ["contracts"],
    "data/contracts/supernatural_contracts.yaml": ["contracts"],
    # culture/
    "data/culture/colloquialisms.yaml": ["colloquialisms"],
    "data/culture/expressions.yaml": ["expressions"],
    "data/culture/insults_extended.yaml": ["insults_extended"],
    "data/culture/legal_customs.yaml": ["legal_customs"],
    "data/culture/material_culture.yaml": ["material_culture"],
    "data/culture/names_and_language.yaml": ["names_and_language"],
    "data/culture/proverbs_extended.yaml": ["proverbs_extended"],
    "data/culture/rituals.yaml": ["rituals"],
    # economy/
    "data/economy/mercenary_costs.yaml": ["mercenary_costs"],
    "data/economy/settlement_economies.yaml": ["settlement_economies"],
    "data/economy/trade_goods.yaml": ["trade_goods"],
    "data/economy/war_economy.yaml": [
        "war_economy_events", "cascade_rules", "seasonal_modifiers",
    ],
    # events/
    "data/events/personal_band_events.yaml": ["events"],
    "data/events/supernatural_chain_events.yaml": ["events"],
    "data/events/y312_events.yaml": ["events"],
    "data/events/y313_events.yaml": ["events"],
    "data/events/y314_y315_events.yaml": ["events"],
    # geography/
    "data/geography/atlas.yaml": ["locations"],
    "data/geography/routes.yaml": ["routes"],
    "data/geography/terrain_encounters.yaml": ["terrain_encounters"],
    # hidden/
    "data/hidden/manifest.yaml": [
        "calendar_events", "campaign_arcs", "npc_secrets", "campaign_chains",
    ],
    # npcs/
    "data/npcs/antagonist_npcs.yaml": ["npcs"],
    "data/npcs/relationship_web.yaml": ["metadata", "edges"],
    "data/npcs/rival_band_npcs.yaml": ["npcs"],
    "data/npcs/settlement_npcs.yaml": ["npcs"],
    "data/npcs/supernatural_npcs.yaml": ["npcs"],
    "data/npcs/traveling_npcs.yaml": ["npcs"],
    # volumes/
    "data/volumes/chapter_templates.yaml": ["chapter_templates"],
    "data/volumes/volume_arcs.yaml": ["volume_arcs"],
    "data/volumes/volumes_1_3.yaml": ["volumes_1_3"],
    "data/volumes/volumes_4_7.yaml": ["volumes_4_7"],
    "data/volumes/volumes_8_10.yaml": ["volumes_8_10"],
    # weather/
    "data/weather/hazards.yaml": ["hazards"],
    "data/weather/named_events.yaml": ["named_events"],
    "data/weather/seasonal_life.yaml": ["seasonal_life"],
    "data/weather/weather_history.yaml": ["weather_history"],
}

EVENT_ID_PATTERN = re.compile(
    r"^EVT_(\d{3,4})_S(\d{2})_(\d{3,4})$"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rel(path):
    """Return path relative to project root for display."""
    return os.path.relpath(path, PROJECT_ROOT)


def load_yaml(filepath):
    """Load a YAML file and return (data, error)."""
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data, None
    except yaml.YAMLError as exc:
        return None, str(exc)
    except FileNotFoundError:
        return None, "File not found"
    except Exception as exc:
        return None, str(exc)


def collect_list(data, key):
    """Safely get a list from data[key], returning [] on any issue."""
    if not isinstance(data, dict):
        return []
    val = data.get(key)
    if isinstance(val, list):
        return val
    return []


def extract_field(items, field):
    """Extract a set of field values from a list of dicts."""
    out = set()
    for item in items:
        if isinstance(item, dict) and field in item:
            out.add(str(item[field]))
    return out


def deep_extract_strings(obj, key):
    """Recursively extract all string values for a given key in nested data."""
    results = set()
    if isinstance(obj, dict):
        if key in obj and isinstance(obj[key], str):
            results.add(obj[key])
        for v in obj.values():
            results.update(deep_extract_strings(v, key))
    elif isinstance(obj, list):
        for item in obj:
            results.update(deep_extract_strings(item, key))
    return results


def deep_extract_list_strings(obj, key):
    """Recursively extract all string values from lists at a given key."""
    results = set()
    if isinstance(obj, dict):
        if key in obj:
            val = obj[key]
            if isinstance(val, str):
                results.add(val)
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, str):
                        results.add(item)
        for v in obj.values():
            results.update(deep_extract_list_strings(v, key))
    elif isinstance(obj, list):
        for item in obj:
            results.update(deep_extract_list_strings(item, key))
    return results

# ---------------------------------------------------------------------------
# Data cache — lazy-loaded shared state for cross-reference checks
# ---------------------------------------------------------------------------

class DataCache:
    """Loads all YAML once and caches parsed data."""

    def __init__(self):
        self._files = {}
        self._load_errors = {}
        self._loaded = False

    def load_all(self):
        if self._loaded:
            return
        for relpath in FILE_MANIFEST:
            abspath = os.path.join(PROJECT_ROOT, relpath)
            data, err = load_yaml(abspath)
            if err:
                self._load_errors[relpath] = err
            else:
                self._files[relpath] = data
        self._loaded = True

    def get(self, relpath):
        return self._files.get(relpath)

    def errors(self):
        return dict(self._load_errors)

    def settlement_names(self):
        data = self.get("data/settlements.yaml")
        if not data:
            return set()
        return extract_field(collect_list(data, "settlements"), "name")

    def all_npc_names(self):
        names = set()
        npc_files = [
            "data/npcs/antagonist_npcs.yaml",
            "data/npcs/rival_band_npcs.yaml",
            "data/npcs/settlement_npcs.yaml",
            "data/npcs/supernatural_npcs.yaml",
            "data/npcs/traveling_npcs.yaml",
        ]
        for f in npc_files:
            data = self.get(f)
            if data:
                for npc in collect_list(data, "npcs"):
                    if isinstance(npc, dict):
                        if "name" in npc:
                            names.add(npc["name"])
                        if "call_name" in npc:
                            names.add(npc["call_name"])
        return names

    def all_enemy_ids(self):
        ids = set()
        bestiary_files = [
            "data/bestiary/animals.yaml",
            "data/bestiary/humans.yaml",
            "data/bestiary/named_enemies.yaml",
            "data/bestiary/supernatural.yaml",
            "data/bestiary/undead.yaml",
            "data/bestiary/world_bosses.yaml",
        ]
        for f in bestiary_files:
            data = self.get(f)
            if data:
                ids.update(extract_field(collect_list(data, "enemies"), "id"))
        return ids

    def all_event_ids(self):
        ids = set()
        event_files = [
            "data/events/personal_band_events.yaml",
            "data/events/supernatural_chain_events.yaml",
            "data/events/y312_events.yaml",
            "data/events/y313_events.yaml",
            "data/events/y314_y315_events.yaml",
        ]
        for f in event_files:
            data = self.get(f)
            if data:
                ids.update(extract_field(collect_list(data, "events"), "id"))
        return ids

    def all_barrow_names(self):
        data = self.get("data/barrows/barrows.yaml")
        if not data:
            return set()
        return extract_field(collect_list(data, "barrows"), "name")

    def all_contract_ids(self):
        ids = set()
        contract_files = [
            "data/contracts/desperate_contracts.yaml",
            "data/contracts/faction_contracts.yaml",
            "data/contracts/settlement_contracts.yaml",
            "data/contracts/supernatural_contracts.yaml",
        ]
        for f in contract_files:
            data = self.get(f)
            if data:
                ids.update(extract_field(collect_list(data, "contracts"), "id"))
        return ids

    def all_events(self):
        events = []
        event_files = [
            "data/events/personal_band_events.yaml",
            "data/events/supernatural_chain_events.yaml",
            "data/events/y312_events.yaml",
            "data/events/y313_events.yaml",
            "data/events/y314_y315_events.yaml",
        ]
        for f in event_files:
            data = self.get(f)
            if data:
                for ev in collect_list(data, "events"):
                    if isinstance(ev, dict):
                        events.append((f, ev))
        return events


CACHE = DataCache()

# ---------------------------------------------------------------------------
# Validation checks — each returns list of (level, message) tuples
# ---------------------------------------------------------------------------

def check_load():
    """1. Load Test — every YAML file parses without error."""
    results = []
    CACHE.load_all()
    errors = CACHE.errors()
    total = len(FILE_MANIFEST)
    ok = total - len(errors)

    for relpath in sorted(FILE_MANIFEST):
        abspath = os.path.join(PROJECT_ROOT, relpath)
        if relpath in errors:
            results.append((FAIL, f"{relpath}: {errors[relpath]}"))
        elif not os.path.exists(abspath):
            results.append((FAIL, f"{relpath}: file missing"))
        else:
            results.append((PASS, f"{relpath}: loaded OK"))

    if errors:
        results.insert(0, (FAIL, f"{ok}/{total} YAML files load successfully"))
    else:
        results.insert(0, (PASS, f"{total}/{total} YAML files load successfully"))
    return results


def check_schema():
    """2. Schema Check — required top-level keys exist."""
    results = []
    all_ok = True
    for relpath, required_keys in FILE_MANIFEST.items():
        data = CACHE.get(relpath)
        if data is None:
            results.append((FAIL, f"{relpath}: could not check schema (load failed)"))
            all_ok = False
            continue
        if not isinstance(data, dict):
            results.append((FAIL, f"{relpath}: top-level is {type(data).__name__}, expected dict"))
            all_ok = False
            continue
        missing = [k for k in required_keys if k not in data]
        if missing:
            results.append((FAIL, f"{relpath}: missing keys: {', '.join(missing)}"))
            all_ok = False
        else:
            results.append((PASS, f"{relpath}: all {len(required_keys)} required keys present"))

    if all_ok:
        results.insert(0, (PASS, "Schema validation: all required keys present"))
    else:
        results.insert(0, (FAIL, "Schema validation: some files have missing keys"))
    return results


def check_id_uniqueness():
    """3. ID Uniqueness — no duplicate IDs within collections."""
    results = []
    dup_count = 0

    # Collection files where items have an "id" field
    id_collections = {
        "data/bestiary/animals.yaml": "enemies",
        "data/bestiary/humans.yaml": "enemies",
        "data/bestiary/named_enemies.yaml": "enemies",
        "data/bestiary/supernatural.yaml": "enemies",
        "data/bestiary/undead.yaml": "enemies",
        "data/bestiary/world_bosses.yaml": "enemies",
        "data/bestiary/encounters.yaml": "encounters",
        "data/contracts/desperate_contracts.yaml": "contracts",
        "data/contracts/faction_contracts.yaml": "contracts",
        "data/contracts/settlement_contracts.yaml": "contracts",
        "data/contracts/supernatural_contracts.yaml": "contracts",
        "data/npcs/antagonist_npcs.yaml": "npcs",
        "data/npcs/rival_band_npcs.yaml": "npcs",
        "data/npcs/settlement_npcs.yaml": "npcs",
        "data/npcs/supernatural_npcs.yaml": "npcs",
        "data/npcs/traveling_npcs.yaml": "npcs",
        "data/barrows/barrows.yaml": "barrows",
        "data/geography/routes.yaml": "routes",
        "data/events/personal_band_events.yaml": "events",
        "data/events/supernatural_chain_events.yaml": "events",
        "data/events/y312_events.yaml": "events",
        "data/events/y313_events.yaml": "events",
        "data/events/y314_y315_events.yaml": "events",
    }

    for relpath, key in id_collections.items():
        data = CACHE.get(relpath)
        if not data:
            continue
        items = collect_list(data, key)
        seen = collections.Counter()
        for item in items:
            if isinstance(item, dict) and "id" in item:
                seen[item["id"]] += 1
        dupes = {k: v for k, v in seen.items() if v > 1}
        if dupes:
            for dup_id, cnt in dupes.items():
                results.append((FAIL, f"{relpath}: \"{dup_id}\" appears {cnt} times"))
                dup_count += 1
        else:
            results.append((PASS, f"{relpath}: all IDs unique"))

    # Cross-file uniqueness for globally-scoped IDs
    global_pools = {
        "enemy_ids": {},
        "event_ids": {},
        "contract_ids": {},
        "npc_ids": {},
        "barrow_ids": {},
    }

    for relpath, key in id_collections.items():
        data = CACHE.get(relpath)
        if not data:
            continue
        items = collect_list(data, key)
        pool = None
        if key == "enemies":
            pool = "enemy_ids"
        elif key == "events":
            pool = "event_ids"
        elif key == "contracts":
            pool = "contract_ids"
        elif key == "npcs":
            pool = "npc_ids"
        elif key == "barrows":
            pool = "barrow_ids"

        if pool:
            for item in items:
                if isinstance(item, dict) and "id" in item:
                    item_id = item["id"]
                    if item_id in global_pools[pool]:
                        results.append((
                            WARN,
                            f"Cross-file duplicate {pool}: \"{item_id}\" in "
                            f"{relpath} and {global_pools[pool][item_id]}"
                        ))
                        dup_count += 1
                    else:
                        global_pools[pool][item_id] = relpath

    if dup_count == 0:
        results.insert(0, (PASS, "ID uniqueness: no duplicates found"))
    else:
        results.insert(0, (FAIL, f"ID uniqueness: {dup_count} duplicate(s) found"))
    return results


def check_settlement_references():
    """4. Settlement References — locations in events/contracts/NPCs exist."""
    results = []
    settlements = CACHE.settlement_names()
    if not settlements:
        return [(WARN, "Settlement references: settlements.yaml has no settlement names")]

    missing_refs = []

    # Check events
    for src_file, ev in CACHE.all_events():
        loc = ev.get("location")
        if loc and loc not in settlements:
            missing_refs.append((src_file, ev.get("id", "?"), loc))

    # Check contracts
    contract_files = [
        "data/contracts/desperate_contracts.yaml",
        "data/contracts/faction_contracts.yaml",
        "data/contracts/settlement_contracts.yaml",
        "data/contracts/supernatural_contracts.yaml",
    ]
    for f in contract_files:
        data = CACHE.get(f)
        if not data:
            continue
        for c in collect_list(data, "contracts"):
            if isinstance(c, dict):
                sett = c.get("settlement")
                if sett and sett not in settlements:
                    missing_refs.append((f, c.get("id", "?"), sett))

    # Check NPCs
    npc_files = [
        "data/npcs/antagonist_npcs.yaml",
        "data/npcs/rival_band_npcs.yaml",
        "data/npcs/settlement_npcs.yaml",
        "data/npcs/supernatural_npcs.yaml",
        "data/npcs/traveling_npcs.yaml",
    ]
    for f in npc_files:
        data = CACHE.get(f)
        if not data:
            continue
        for npc in collect_list(data, "npcs"):
            if isinstance(npc, dict):
                sett = npc.get("settlement")
                if sett and sett not in settlements:
                    missing_refs.append((f, npc.get("id", npc.get("name", "?")), sett))

    if missing_refs:
        results.append((WARN, f"{len(missing_refs)} settlement reference(s) not found in settlements.yaml:"))
        for src, item_id, sett_name in missing_refs:
            results.append((WARN, f"  {src}: {item_id} references \"{sett_name}\""))
    else:
        results.append((PASS, "Settlement references: all locations exist in settlements.yaml"))
    return results


def check_npc_references():
    """5. NPC References — actor names in events exist in NPC files."""
    results = []
    npc_names = CACHE.all_npc_names()
    if not npc_names:
        return [(WARN, "NPC references: no NPC names loaded")]

    missing = []
    for src_file, ev in CACHE.all_events():
        actors = ev.get("actors", [])
        if not isinstance(actors, list):
            continue
        for actor in actors:
            if isinstance(actor, str) and actor not in npc_names:
                missing.append((src_file, ev.get("id", "?"), actor))

    if missing:
        results.append((WARN, f"{len(missing)} NPC reference(s) in events not found in NPC files:"))
        for src, evt_id, name in missing:
            results.append((WARN, f"  {src}: {evt_id} references actor \"{name}\""))
    else:
        results.append((PASS, "NPC references: all event actors found in NPC files"))
    return results


def check_enemy_references():
    """6. Enemy References — enemy IDs in encounter tables exist in bestiary."""
    results = []
    enemy_ids = CACHE.all_enemy_ids()
    if not enemy_ids:
        return [(WARN, "Enemy references: no enemy IDs loaded")]

    missing = []

    # Check bestiary/encounters.yaml
    enc_data = CACHE.get("data/bestiary/encounters.yaml")
    if enc_data:
        for enc in collect_list(enc_data, "encounters"):
            if not isinstance(enc, dict):
                continue
            enc_id = enc.get("id", "?")
            for enemy_entry in enc.get("enemies", []):
                if isinstance(enemy_entry, dict):
                    eid = enemy_entry.get("enemy_id")
                    if eid and eid not in enemy_ids:
                        missing.append(("data/bestiary/encounters.yaml", enc_id, eid))

    # Check barrows/encounter_tables.yaml
    bar_enc = CACHE.get("data/barrows/encounter_tables.yaml")
    if bar_enc:
        tables = bar_enc.get("encounter_tables")
        if isinstance(tables, dict):
            for table_name, entries in tables.items():
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    if isinstance(entry, dict):
                        eid = entry.get("enemy_id")
                        if eid and eid not in enemy_ids:
                            missing.append(("data/barrows/encounter_tables.yaml", table_name, eid))
        elif isinstance(tables, list):
            for table in tables:
                if isinstance(table, dict):
                    table_id = table.get("id", "?")
                    for entry in table.get("entries", []):
                        if isinstance(entry, dict):
                            eid = entry.get("enemy_id")
                            if eid and eid not in enemy_ids:
                                missing.append(("data/barrows/encounter_tables.yaml", table_id, eid))

    if missing:
        results.append((WARN, f"{len(missing)} enemy reference(s) not found in bestiary:"))
        for src, parent_id, eid in missing:
            results.append((WARN, f"  {src}: {parent_id} references enemy \"{eid}\""))
    else:
        results.append((PASS, "Enemy references: all encounter enemies found in bestiary"))
    return results


def check_event_id_format():
    """7. Event ID Format — all event IDs follow EVT_{year}_S{season}_{number}."""
    results = []
    bad = []
    for src_file, ev in CACHE.all_events():
        eid = ev.get("id")
        if not eid:
            bad.append((src_file, "(missing id)", "no id field"))
            continue
        if not EVENT_ID_PATTERN.match(eid):
            bad.append((src_file, eid, "wrong format"))

    if bad:
        results.append((WARN, f"{len(bad)} event ID(s) do not match EVT_{{year}}_S{{season}}_{{number}} format:"))
        for src, eid, reason in bad:
            results.append((WARN, f"  {src}: \"{eid}\" — {reason}"))
    else:
        results.append((PASS, "Event ID format: all events match EVT_{{year}}_S{{season}}_{{number}}"))
    return results


def check_barrow_references():
    """8. Barrow References — barrow names in contracts exist in barrows.yaml."""
    results = []
    barrow_names = CACHE.all_barrow_names()
    if not barrow_names:
        return [(WARN, "Barrow references: no barrow names loaded")]

    missing = []
    contract_files = [
        "data/contracts/desperate_contracts.yaml",
        "data/contracts/faction_contracts.yaml",
        "data/contracts/settlement_contracts.yaml",
        "data/contracts/supernatural_contracts.yaml",
    ]
    for f in contract_files:
        data = CACHE.get(f)
        if not data:
            continue
        for c in collect_list(data, "contracts"):
            if not isinstance(c, dict):
                continue
            ctype = c.get("type", "")
            # Check barrow-related contracts
            if "barrow" in str(ctype).lower():
                barrow_ref = c.get("barrow") or c.get("target_barrow") or c.get("location")
                if barrow_ref and barrow_ref not in barrow_names:
                    missing.append((f, c.get("id", "?"), barrow_ref))

    if missing:
        results.append((WARN, f"{len(missing)} barrow reference(s) not found in barrows.yaml:"))
        for src, cid, bname in missing:
            results.append((WARN, f"  {src}: {cid} references barrow \"{bname}\""))
    else:
        results.append((PASS, "Barrow references: all contract barrows found in barrows.yaml"))
    return results


def check_route_validation():
    """9. Route Validation — travel route endpoints exist in settlements."""
    results = []
    settlements = CACHE.settlement_names()
    if not settlements:
        return [(WARN, "Route validation: no settlement names loaded")]

    missing = []
    routes_data = CACHE.get("data/geography/routes.yaml")
    if not routes_data:
        return [(WARN, "Route validation: routes.yaml not loaded")]

    for route in collect_list(routes_data, "routes"):
        if not isinstance(route, dict):
            continue
        rid = route.get("id", route.get("name", "?"))
        for endpoint_key in ("from_settlement", "to_settlement", "from", "to"):
            ep = route.get(endpoint_key)
            if ep and ep not in settlements:
                missing.append((rid, endpoint_key, ep))

    # Also check travel_routes in settlements.yaml
    sett_data = CACHE.get("data/settlements.yaml")
    if sett_data:
        travel_routes = sett_data.get("travel_routes")
        if isinstance(travel_routes, list):
            for tr in travel_routes:
                if isinstance(tr, dict):
                    tid = tr.get("id", tr.get("name", "?"))
                    for endpoint_key in ("from_settlement", "to_settlement", "from", "to"):
                        ep = tr.get(endpoint_key)
                        if ep and ep not in settlements:
                            missing.append((tid, endpoint_key, ep))

    if missing:
        results.append((WARN, f"{len(missing)} route endpoint(s) not found in settlements:"))
        for rid, key, ep in missing:
            results.append((WARN, f"  route {rid}: {key} \"{ep}\" not in settlements"))
    else:
        results.append((PASS, "Route validation: all route endpoints exist in settlements"))
    return results


def check_weather_weeks():
    """10. Weather Week References — weeks in volume outlines are valid (1-48)."""
    results = []
    bad = []
    volume_files = [
        "data/volumes/volumes_1_3.yaml",
        "data/volumes/volumes_4_7.yaml",
        "data/volumes/volumes_8_10.yaml",
    ]
    for f in volume_files:
        data = CACHE.get(f)
        if not data:
            continue
        # Recursively find any "week" or "weather_week" integers
        weeks = set()
        _extract_week_refs(data, weeks)
        for w in weeks:
            if not (1 <= w <= 48):
                bad.append((f, w))

    if bad:
        results.append((WARN, f"{len(bad)} invalid weather week reference(s):"))
        for src, w in bad:
            results.append((WARN, f"  {src}: week {w} outside valid range 1-48"))
    else:
        results.append((PASS, "Weather week references: all weeks within 1-48 range"))
    return results


def _extract_week_refs(obj, out):
    """Recursively extract integer values from 'week' or 'weather_week' keys."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("week", "weather_week") and isinstance(v, int):
                out.add(v)
            else:
                _extract_week_refs(v, out)
    elif isinstance(obj, list):
        for item in obj:
            _extract_week_refs(item, out)


def check_band_members():
    """11. Band Member Consistency — stats in valid 1-10 range."""
    results = []
    data = CACHE.get("data/band_state.yaml")
    if not data:
        return [(WARN, "Band member check: band_state.yaml not loaded")]

    members = collect_list(data, "members")
    if not members:
        return [(WARN, "Band member check: no members list found")]

    bad = []
    stat_keys = {"MIG", "NIM", "TOU", "WIT", "WIL", "WYR"}

    for member in members:
        if not isinstance(member, dict):
            continue
        name = member.get("name", "?")
        stats = member.get("stats", {})
        if not isinstance(stats, dict):
            bad.append((name, "stats is not a dict"))
            continue
        for sk in stat_keys:
            val = stats.get(sk)
            if val is None:
                continue
            if not isinstance(val, (int, float)):
                bad.append((name, f"{sk} is {type(val).__name__}, expected int"))
            elif not (1 <= val <= 10):
                bad.append((name, f"{sk}={val} outside 1-10 range"))

    if bad:
        results.append((WARN, f"{len(bad)} band member stat issue(s):"))
        for name, issue in bad:
            results.append((WARN, f"  {name}: {issue}"))
    else:
        results.append((PASS, "Band member stats: all values within 1-10 range"))
    return results

# ---------------------------------------------------------------------------
# Check registry
# ---------------------------------------------------------------------------

CHECK_REGISTRY = collections.OrderedDict([
    ("load", ("Load Test", check_load)),
    ("schema", ("Schema Check", check_schema)),
    ("ids", ("ID Uniqueness", check_id_uniqueness)),
    ("settlements", ("Settlement References", check_settlement_references)),
    ("npcs", ("NPC References", check_npc_references)),
    ("enemies", ("Enemy References", check_enemy_references)),
    ("event_format", ("Event ID Format", check_event_id_format)),
    ("barrows", ("Barrow References", check_barrow_references)),
    ("routes", ("Route Validation", check_route_validation)),
    ("weather", ("Weather Week References", check_weather_weeks)),
    ("band", ("Band Member Consistency", check_band_members)),
])

# ---------------------------------------------------------------------------
# CLI + runner
# ---------------------------------------------------------------------------

def format_result(level, message, verbose=False):
    """Format a single result line with colour."""
    color = LEVEL_COLOR.get(level, "")
    tag = f"{color}[{level}]{C_RESET}"
    return f"  {tag} {message}"


def run_checks(selected=None, verbose=False):
    """Run selected (or all) checks, print results, return exit code."""
    print(f"\n{C_BOLD}=== YAML Data Validation Report ==={C_RESET}\n")

    # Always load data first
    CACHE.load_all()

    total_pass = 0
    total_warn = 0
    total_fail = 0

    checks_to_run = CHECK_REGISTRY
    if selected:
        checks_to_run = collections.OrderedDict(
            (k, v) for k, v in CHECK_REGISTRY.items() if k in selected
        )
        if not checks_to_run:
            print(f"{C_RED}No matching check group. Available: {', '.join(CHECK_REGISTRY.keys())}{C_RESET}")
            return 1

    for key, (label, fn) in checks_to_run.items():
        print(f"{C_BOLD}--- {label} ---{C_RESET}")
        results = fn()

        for level, message in results:
            is_summary = results.index((level, message)) == 0
            if verbose or is_summary or level in (WARN, FAIL):
                print(format_result(level, message, verbose))

            if level == PASS:
                total_pass += 1
            elif level == WARN:
                total_warn += 1
            elif level == FAIL:
                total_fail += 1

        print()

    # Summary
    print(f"{C_BOLD}--- Summary ---{C_RESET}")
    parts = []
    parts.append(f"{C_GREEN}{total_pass} passed{C_RESET}")
    if total_warn:
        parts.append(f"{C_YELLOW}{total_warn} warnings{C_RESET}")
    if total_fail:
        parts.append(f"{C_RED}{total_fail} failures{C_RESET}")
    print(f"  {', '.join(parts)}")
    print()

    return 1 if total_fail > 0 else 0


def main():
    parser = argparse.ArgumentParser(
        description="Iron Ledger — YAML data validation"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show all individual check results"
    )
    parser.add_argument(
        "--fix", action="store_true",
        help="Auto-fix where possible (not yet implemented)"
    )
    parser.add_argument(
        "--check", "-c", nargs="+", metavar="GROUP",
        help=f"Run only specific check group(s). Available: {', '.join(CHECK_REGISTRY.keys())}"
    )
    args = parser.parse_args()

    if args.fix:
        print(f"{C_YELLOW}[NOTE] --fix is reserved for future auto-fix support.{C_RESET}")

    selected = set(args.check) if args.check else None
    exit_code = run_checks(selected=selected, verbose=args.verbose)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
