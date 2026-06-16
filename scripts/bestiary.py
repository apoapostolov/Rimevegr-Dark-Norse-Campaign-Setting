#!/usr/bin/env python3
"""
Iron Ledger — Bestiary Manager

CLI tool for querying, filtering, and generating random encounters
from the enemy/creature database.

Usage:
    python bestiary.py list
    python bestiary.py list --category human --tier 3
    python bestiary.py list --terrain forest --season winter
    python bestiary.py show HUM_BANDIT_02
    python bestiary.py encounter --terrain barrow --tier 3
    python bestiary.py encounter --terrain road --season summer
    python bestiary.py stats
    python bestiary.py validate
    python bestiary.py image-prompts

Schema: data/bestiary/BESTIARY_SCHEMA.md
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path
from typing import Any

import yaml

# --- Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
BESTIARY_DIR = DATA_DIR / "bestiary"

VALID_CATEGORIES = {"human", "undead", "supernatural", "animal", "boss", "world_boss"}
TIER_LABELS = {1: "Trivial", 2: "Common", 3: "Dangerous", 4: "Deadly", 5: "Legendary", 6: "World-Ending"}


# ============================================================
# Data Loading
# ============================================================

def load_all_enemies() -> list[dict]:
    """Load and merge enemies from all YAML files under data/bestiary/."""
    all_enemies: list[dict] = []
    if not BESTIARY_DIR.exists():
        return all_enemies
    for path in sorted(BESTIARY_DIR.glob("*.yaml")):
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data and "enemies" in data:
                for entry in data["enemies"]:
                    entry["_source"] = path.name
                    all_enemies.append(entry)
        except (yaml.YAMLError, OSError) as exc:
            print(f"Warning: failed to load {path.name}: {exc}", file=sys.stderr)
    return all_enemies


# ============================================================
# Filtering
# ============================================================

def filter_enemies(
    enemies: list[dict],
    category: str | None = None,
    subcategory: str | None = None,
    tier: int | None = None,
    tier_min: int | None = None,
    tier_max: int | None = None,
    terrain: str | None = None,
    season: str | None = None,
    named_only: bool = False,
    chain: str | None = None,
    location: str | None = None,
) -> list[dict]:
    """Filter enemies by multiple criteria."""
    result = enemies
    if category:
        result = [e for e in result if e.get("category") == category]
    if subcategory:
        result = [e for e in result if e.get("subcategory") == subcategory]
    if tier is not None:
        result = [e for e in result if e.get("tier") == tier]
    if tier_min is not None:
        result = [e for e in result if e.get("tier", 0) >= tier_min]
    if tier_max is not None:
        result = [e for e in result if e.get("tier", 99) <= tier_max]
    if terrain:
        result = [
            e for e in result
            if terrain in e.get("encounter_conditions", {}).get("terrain", [])
        ]
    if season:
        result = [
            e for e in result
            if season in e.get("encounter_conditions", {}).get("season", [])
               or not e.get("encounter_conditions", {}).get("season")
        ]
    if named_only:
        result = [e for e in result if e.get("named")]
    if chain:
        result = [e for e in result if chain in e.get("associated_chains", [])]
    if location:
        result = [e for e in result if location in e.get("associated_locations", [])]
    return result


# ============================================================
# Display
# ============================================================

def display_list(enemies: list[dict]) -> None:
    """Print a compact list of enemies."""
    if not enemies:
        print("No matching enemies found.")
        return
    print(f"{'ID':<22} {'Name':<30} {'Cat':<14} {'Tier':<6} {'Group'}")
    print("-" * 85)
    for e in sorted(enemies, key=lambda x: (x.get("tier", 0), x.get("id", ""))):
        print(
            f"{e.get('id', '???'):<22} "
            f"{e.get('name', '???'):<30} "
            f"{e.get('category', '???'):<14} "
            f"T{e.get('tier', '?'):<5} "
            f"{e.get('group_size', '?')}"
        )
    print(f"\n{len(enemies)} entries.")


def display_entry(entry: dict) -> None:
    """Print full details of a single enemy."""
    print(f"=== {entry.get('name', '???')} ({entry.get('id', '???')}) ===")
    print(f"Category: {entry.get('category')} / {entry.get('subcategory', '-')}")
    print(f"Tier: {entry.get('tier')} ({TIER_LABELS.get(entry.get('tier', 0), '?')})")
    if entry.get("named"):
        print("** NAMED / UNIQUE **")
    print(f"\n{entry.get('description', '')}")

    stats = entry.get("stats", {})
    print(f"\nStats: MIG {stats.get('MIG','-')} | NIM {stats.get('NIM','-')} | "
          f"TOU {stats.get('TOU','-')} | WIT {stats.get('WIT','-')} | "
          f"WIL {stats.get('WIL','-')} | WYR {stats.get('WYR','-')}")
    print(f"HP: {entry.get('hp', '-')}")

    skills = entry.get("skills", [])
    if skills:
        skill_str = ", ".join(f"{s['name']} {s['rank']}" for s in skills)
        print(f"Skills: {skill_str}")

    gear = entry.get("gear", {})
    weapons = gear.get("weapons", [])
    if weapons:
        for w in weapons:
            print(f"Weapon: {w.get('name', '?')} (type={w.get('type')}, "
                  f"spd={w.get('speed')}, dmg={w.get('base_damage')})")
    armor = gear.get("armor", {})
    if armor:
        armor_parts = [f"{k}: {v}" for k, v in armor.items() if v and v != "None"]
        if armor_parts:
            print(f"Armor: {', '.join(armor_parts)}")

    abilities = entry.get("abilities", [])
    if abilities:
        print("\nAbilities:")
        for a in abilities:
            print(f"  - {a}")

    combat_phases = entry.get("combat_phases", {})
    if combat_phases:
        phase_labels = {
            "pre_battle": "PRE-BATTLE",
            "maneuvers": "COMBAT MANEUVERS",
            "bloodied": "BLOODIED (<50% HP)",
            "on_death": "ON DEATH",
        }
        print("\nCombat Phases:")
        for phase_key in ("pre_battle", "maneuvers", "bloodied", "on_death"):
            phase_list = combat_phases.get(phase_key, [])
            if phase_list:
                print(f"  [{phase_labels.get(phase_key, phase_key)}]")
                for ability in phase_list:
                    name = ability.get("name", "???")
                    desc = ability.get("description", "")
                    extras = []
                    if ability.get("cost"):
                        extras.append(f"Cost: {ability['cost']}")
                    if ability.get("trigger"):
                        extras.append(f"Trigger: {ability['trigger']}")
                    suffix = f" ({', '.join(extras)})" if extras else ""
                    print(f"    * {name}: {desc}{suffix}")

    resistances = entry.get("resistances", [])
    if resistances:
        print(f"Resistances: {', '.join(resistances)}")
    weaknesses = entry.get("weaknesses", [])
    if weaknesses:
        print(f"Weaknesses: {', '.join(weaknesses)}")

    print(f"\nTactics: {entry.get('tactics', '-')}")
    print(f"Morale Break: {entry.get('morale_break', '-')}")
    print(f"Group Size: {entry.get('group_size', '-')}")

    ec = entry.get("encounter_conditions", {})
    if ec:
        print(f"Terrain: {', '.join(ec.get('terrain', []))}")
        if ec.get("season"):
            print(f"Season: {', '.join(ec.get('season', []))}")

    loot = entry.get("loot", {})
    if loot:
        sr = loot.get("silver_range", [0, 0])
        print(f"Loot: {sr[0]}-{sr[1]} silver, items: {loot.get('items', [])}")
        if loot.get("special"):
            print(f"  Special: {loot['special']}")

    achilles = entry.get("achilles_heel", {})
    if achilles:
        print(f"\n** ACHILLES HEEL: {achilles.get('name', '?')} **")
        print(f"  Discovery: {achilles.get('discovery', '-')}")
        print(f"  Location: {achilles.get('location', '-')}")
        print(f"  Exploit: {achilles.get('exploit', '-')}")
        print(f"  Difficulty: {achilles.get('difficulty', '-')}")

    if entry.get("lore"):
        print(f"\nLore: {entry['lore']}")
    if entry.get("associated_locations"):
        print(f"Locations: {', '.join(entry['associated_locations'])}")
    if entry.get("associated_chains"):
        print(f"Chains: {', '.join(entry['associated_chains'])}")

    print(f"\nSource: {entry.get('_source', '?')}")


# ============================================================
# Random Encounter
# ============================================================

def random_encounter(
    enemies: list[dict],
    terrain: str | None = None,
    season: str | None = None,
    tier: int | None = None,
    tier_max: int | None = None,
) -> dict | None:
    """Pick a random enemy matching conditions."""
    pool = filter_enemies(
        enemies, terrain=terrain, season=season, tier=tier, tier_max=tier_max
    )
    if not pool:
        return None
    return random.choice(pool)


# ============================================================
# Stats
# ============================================================

def show_stats(enemies: list[dict]) -> None:
    """Show database statistics."""
    print(f"Bestiary — {len(enemies)} total entries\n")

    # By category
    cats: dict[str, int] = {}
    for e in enemies:
        c = e.get("category", "unknown")
        cats[c] = cats.get(c, 0) + 1
    print("By Category:")
    for c in sorted(cats):
        print(f"  {c}: {cats[c]}")

    # By tier
    tiers: dict[int, int] = {}
    for e in enemies:
        t = e.get("tier", 0)
        tiers[t] = tiers.get(t, 0) + 1
    print("\nBy Tier:")
    for t in sorted(tiers):
        print(f"  T{t} ({TIER_LABELS.get(t, '?')}): {tiers[t]}")

    # By subcategory
    subs: dict[str, int] = {}
    for e in enemies:
        s = e.get("subcategory", "none")
        subs[s] = subs.get(s, 0) + 1
    print("\nBy Subcategory:")
    for s in sorted(subs):
        print(f"  {s}: {subs[s]}")

    # Named
    named = sum(1 for e in enemies if e.get("named"))
    print(f"\nNamed/Unique: {named}")

    # Sources
    sources: dict[str, int] = {}
    for e in enemies:
        src = e.get("_source", "?")
        sources[src] = sources.get(src, 0) + 1
    print("\nSources:")
    for s in sorted(sources):
        print(f"  {s}: {sources[s]}")


# ============================================================
# Validation
# ============================================================

REQUIRED_FIELDS = {"id", "name", "category", "tier", "description", "stats", "hp",
                   "tactics", "morale_break"}
REQUIRED_STATS = {"MIG", "NIM", "TOU", "WIT", "WIL", "WYR"}


def validate_enemies(enemies: list[dict]) -> list[str]:
    """Validate all entries. Returns list of issues."""
    issues: list[str] = []
    seen_ids: set[str] = set()

    for e in enemies:
        eid = e.get("id", "NO_ID")

        # Duplicate ID
        if eid in seen_ids:
            issues.append(f"Duplicate ID: {eid}")
        seen_ids.add(eid)

        # Required fields
        for field in REQUIRED_FIELDS:
            if field not in e:
                issues.append(f"{eid}: missing required field '{field}'")

        # Stats completeness
        stats = e.get("stats", {})
        for s in REQUIRED_STATS:
            if s not in stats:
                issues.append(f"{eid}: missing stat '{s}'")

        # Tier range
        tier = e.get("tier", 0)
        if tier < 1 or tier > 6:
            issues.append(f"{eid}: tier {tier} out of range 1-6")

        # HP positive (exempt hazards, phenomena, and special world bosses)
        hp = e.get("hp", 0)
        subcat = e.get("subcategory", "")
        cat = e.get("category", "")
        if hp <= 0 and subcat not in ("hazard", "veil_entity", "unique", "primordial", "cursed_warlord"):
            issues.append(f"{eid}: hp must be positive, got {hp}")

        # World bosses must have achilles_heel
        if cat == "world_boss" and "achilles_heel" not in e:
            issues.append(f"{eid}: world_boss must have 'achilles_heel' field")

        # Combat phases validation
        combat_phases = e.get("combat_phases", {})
        if combat_phases:
            valid_phases = {"pre_battle", "maneuvers", "bloodied", "on_death"}
            for phase_key, phase_list in combat_phases.items():
                if phase_key not in valid_phases:
                    issues.append(f"{eid}: unknown combat phase '{phase_key}'")
                if not isinstance(phase_list, list):
                    issues.append(f"{eid}: combat_phases.{phase_key} must be a list")
                    continue
                for idx, ability in enumerate(phase_list):
                    if not isinstance(ability, dict):
                        issues.append(f"{eid}: combat_phases.{phase_key}[{idx}] must be a dict")
                        continue
                    if "name" not in ability:
                        issues.append(f"{eid}: combat_phases.{phase_key}[{idx}] missing 'name'")
                    if "description" not in ability:
                        issues.append(f"{eid}: combat_phases.{phase_key}[{idx}] missing 'description'")

    return issues


# ============================================================
# Image Prompt Compiler
# ============================================================

def compile_image_prompts(enemies: list[dict]) -> str:
    """Compile all image prompts into a single document."""
    lines = ["# Bestiary Image Prompts\n"]
    by_cat: dict[str, list[dict]] = {}
    for e in enemies:
        c = e.get("category", "unknown")
        by_cat.setdefault(c, []).append(e)

    for cat in sorted(by_cat):
        lines.append(f"\n## {cat.title()}\n")
        for e in sorted(by_cat[cat], key=lambda x: x.get("id", "")):
            prompt = e.get("image_prompt", "No image prompt.")
            lines.append(f"### {e.get('name', '???')} ({e.get('id', '???')})\n")
            lines.append(f"Tier {e.get('tier', '?')} | {e.get('subcategory', '-')}\n")
            lines.append(f"{prompt.strip()}\n")

    return "\n".join(lines)


# ============================================================
# Encounter Table System
# ============================================================

ENCOUNTERS_FILE = BESTIARY_DIR / "encounters.yaml"


def load_encounters() -> list[dict]:
    """Load all encounter templates from encounters.yaml."""
    if not ENCOUNTERS_FILE.exists():
        return []
    try:
        with open(ENCOUNTERS_FILE, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("encounters", []) if data else []
    except (yaml.YAMLError, OSError) as exc:
        print(f"Warning: failed to load encounters: {exc}", file=sys.stderr)
        return []


def filter_encounters(
    encounters: list[dict],
    terrain: str | None = None,
    tier: int | None = None,
    tier_min: int | None = None,
    tier_max: int | None = None,
    season: str | None = None,
    time_of_day: str | None = None,
    difficulty: str | None = None,
) -> list[dict]:
    """Filter encounter templates by criteria."""
    result = encounters
    if terrain:
        result = [e for e in result if e.get("terrain") == terrain]
    if tier is not None:
        result = [e for e in result if e.get("tier") == tier]
    if tier_min is not None:
        result = [e for e in result if e.get("tier", 0) >= tier_min]
    if tier_max is not None:
        result = [e for e in result if e.get("tier", 99) <= tier_max]
    if season:
        result = [
            e for e in result
            if season in e.get("season", [])
               or "any" in e.get("season", [])
        ]
    if time_of_day:
        result = [
            e for e in result
            if e.get("time_of_day") == time_of_day
               or e.get("time_of_day") == "any"
        ]
    if difficulty:
        result = [e for e in result if e.get("difficulty") == difficulty]
    return result


def display_encounter_list(encounters: list[dict]) -> None:
    """Print a compact list of encounters."""
    if not encounters:
        print("No matching encounters found.")
        return
    print(f"{'ID':<20} {'Name':<35} {'Terrain':<12} {'Tier':<6} {'Diff'}")
    print("-" * 85)
    for e in sorted(encounters, key=lambda x: x.get("id", "")):
        print(
            f"{e.get('id', '???'):<20} "
            f"{e.get('name', '???'):<35} "
            f"{e.get('terrain', '???'):<12} "
            f"T{e.get('tier', '?'):<5} "
            f"{e.get('difficulty', '?')}"
        )
    print(f"\n{len(encounters)} encounters.")


def display_encounter(enc: dict, enemies_db: list[dict] | None = None) -> None:
    """Print full details of a single encounter."""
    print(f"{'=' * 70}")
    print(f"  {enc.get('name', '???')} ({enc.get('id', '???')})")
    print(f"{'=' * 70}")
    print(f"Terrain: {enc.get('terrain')}  |  Tier: {enc.get('tier')}  |  "
          f"Difficulty: {enc.get('difficulty')}")
    print(f"Season: {', '.join(enc.get('season', []))}  |  "
          f"Time: {enc.get('time_of_day', 'any')}")
    print(f"\n  \"{enc.get('description', '')}\"")

    print(f"\n--- ENEMIES ---")
    total_enemies = 0
    for egroup in enc.get("enemies", []):
        count = egroup.get("count", 1)
        total_enemies += count
        eid = egroup.get("enemy_id", "???")
        ename = egroup.get("name", "???")
        # Look up tier from bestiary if available
        tier_str = ""
        if enemies_db:
            match = [e for e in enemies_db if e.get("id") == eid]
            if match:
                tier_str = f" [T{match[0].get('tier', '?')}]"
        print(f"  {count}x {ename} ({eid}){tier_str}")
    print(f"  Total hostiles: {total_enemies}")

    conditions = enc.get("battlefield_conditions", [])
    if conditions:
        print(f"\n--- BATTLEFIELD CONDITIONS ---")
        for c in conditions:
            print(f"  * {c}")

    if enc.get("loot_bonus"):
        print(f"\nLoot: {enc['loot_bonus']}")
    if enc.get("notes"):
        print(f"Notes: {enc['notes']}")


def roll_encounter(
    encounters: list[dict],
    terrain: str | None = None,
    season: str | None = None,
    tier: int | None = None,
    tier_max: int | None = None,
    difficulty: str | None = None,
) -> dict | None:
    """Pick a random encounter from the table matching filters."""
    pool = filter_encounters(
        encounters, terrain=terrain, tier=tier, tier_max=tier_max,
        season=season, difficulty=difficulty,
    )
    if not pool:
        return None
    return random.choice(pool)


def encounter_stats(encounters: list[dict]) -> None:
    """Show encounter table statistics."""
    print(f"Encounter Table — {len(encounters)} total encounters\n")

    # By terrain
    terrains: dict[str, int] = {}
    for e in encounters:
        t = e.get("terrain", "unknown")
        terrains[t] = terrains.get(t, 0) + 1
    print("By Terrain:")
    for t in sorted(terrains):
        print(f"  {t}: {terrains[t]}")

    # By tier
    tiers: dict[int, int] = {}
    for e in encounters:
        t = e.get("tier", 0)
        tiers[t] = tiers.get(t, 0) + 1
    print("\nBy Tier:")
    for t in sorted(tiers):
        print(f"  T{t} ({TIER_LABELS.get(t, '?')}): {tiers[t]}")

    # By difficulty
    diffs: dict[str, int] = {}
    for e in encounters:
        d = e.get("difficulty", "unknown")
        diffs[d] = diffs.get(d, 0) + 1
    print("\nBy Difficulty:")
    for d in sorted(diffs):
        print(f"  {d}: {diffs[d]}")

    # Enemy count distribution
    counts = [sum(eg.get("count", 1) for eg in e.get("enemies", []))
              for e in encounters]
    if counts:
        print(f"\nEnemy Count: min={min(counts)}, max={max(counts)}, "
              f"avg={sum(counts)/len(counts):.1f}")

    # Unique enemy IDs used
    used_ids: set[str] = set()
    for e in encounters:
        for eg in e.get("enemies", []):
            used_ids.add(eg.get("enemy_id", ""))
    print(f"Unique enemy types used: {len(used_ids)}")


def validate_encounters(encounters: list[dict], enemies_db: list[dict]) -> list[str]:
    """Validate encounter templates. Returns issues."""
    issues: list[str] = []
    seen_ids: set[str] = set()
    enemy_ids = {e.get("id") for e in enemies_db}

    required = {"id", "name", "terrain", "tier", "description",
                "enemies", "battlefield_conditions", "difficulty"}

    for enc in encounters:
        eid = enc.get("id", "NO_ID")

        if eid in seen_ids:
            issues.append(f"Duplicate encounter ID: {eid}")
        seen_ids.add(eid)

        for field in required:
            if field not in enc:
                issues.append(f"{eid}: missing field '{field}'")

        # Validate enemy references
        for egroup in enc.get("enemies", []):
            ref = egroup.get("enemy_id", "")
            if ref and ref not in enemy_ids:
                issues.append(f"{eid}: references unknown enemy '{ref}'")
            if egroup.get("count", 0) < 1:
                issues.append(f"{eid}: enemy count < 1 for {ref}")

        # Tier range
        tier = enc.get("tier", 0)
        if tier < 1 or tier > 5:
            issues.append(f"{eid}: tier {tier} out of range")

        # Battlefield conditions present
        conditions = enc.get("battlefield_conditions", [])
        if len(conditions) < 2:
            issues.append(f"{eid}: fewer than 2 battlefield conditions")

    return issues


# ============================================================
# CLI
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="Iron Ledger Bestiary Manager")
    sub = parser.add_subparsers(dest="command")

    # list
    p_list = sub.add_parser("list", help="List enemies with optional filters")
    p_list.add_argument("--category", choices=sorted(VALID_CATEGORIES))
    p_list.add_argument("--subcategory")
    p_list.add_argument("--tier", type=int)
    p_list.add_argument("--tier-min", type=int)
    p_list.add_argument("--tier-max", type=int)
    p_list.add_argument("--terrain")
    p_list.add_argument("--season")
    p_list.add_argument("--named", action="store_true")
    p_list.add_argument("--chain")
    p_list.add_argument("--location")
    p_list.add_argument("--wolfshead", action="store_true",
                        help="Show only wolfshead (outlaw) enemies")

    # show
    p_show = sub.add_parser("show", help="Show full entry for an enemy ID")
    p_show.add_argument("id", help="Enemy ID")

    # encounter
    p_enc = sub.add_parser("encounter", help="Generate a random encounter")
    p_enc.add_argument("--terrain")
    p_enc.add_argument("--season")
    p_enc.add_argument("--tier", type=int)
    p_enc.add_argument("--tier-max", type=int)

    # stats
    sub.add_parser("stats", help="Show database statistics")

    # validate
    sub.add_parser("validate", help="Validate all entries")

    # image-prompts
    sub.add_parser("image-prompts", help="Compile all image prompts to stdout")

    # encounter-list
    p_encl = sub.add_parser("encounter-list", help="List encounter templates")
    p_encl.add_argument("--terrain")
    p_encl.add_argument("--tier", type=int)
    p_encl.add_argument("--tier-min", type=int)
    p_encl.add_argument("--tier-max", type=int)
    p_encl.add_argument("--season")
    p_encl.add_argument("--difficulty",
                        choices=["trivial", "easy", "moderate", "hard", "deadly"])
    p_encl.add_argument("--wolfshead", action="store_true",
                        help="Show only wolfshead encounters")

    # encounter-roll
    p_encr = sub.add_parser("encounter-roll", help="Roll a random encounter")
    p_encr.add_argument("--terrain")
    p_encr.add_argument("--season")
    p_encr.add_argument("--tier", type=int)
    p_encr.add_argument("--tier-max", type=int)
    p_encr.add_argument("--difficulty",
                        choices=["trivial", "easy", "moderate", "hard", "deadly"])
    p_encr.add_argument("--count", type=int, default=1,
                        help="Number of encounters to roll")
    p_encr.add_argument("--wolfshead", action="store_true",
                        help="Show only wolfshead encounters")

    # encounter-show
    p_encs = sub.add_parser("encounter-show", help="Show a specific encounter")
    p_encs.add_argument("id", help="Encounter ID")

    # encounter-stats
    sub.add_parser("encounter-stats", help="Encounter table statistics")

    # encounter-validate
    sub.add_parser("encounter-validate", help="Validate encounter templates")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    enemies = load_all_enemies()

    if args.command == "list":
        filtered = filter_enemies(
            enemies,
            category=args.category,
            subcategory=args.subcategory,
            tier=args.tier,
            tier_min=args.tier_min,
            tier_max=args.tier_max,
            terrain=args.terrain,
            season=args.season,
            named_only=args.named,
            chain=args.chain,
            location=args.location,
        )
        if args.wolfshead:
            filtered = [e for e in filtered if e.get("subcategory") == "wolfshead"]
        display_list(filtered)

    elif args.command == "show":
        match = [e for e in enemies if e.get("id") == args.id]
        if match:
            display_entry(match[0])
        else:
            print(f"No entry with ID '{args.id}'.")

    elif args.command == "encounter":
        result = random_encounter(
            enemies, terrain=args.terrain, season=args.season,
            tier=args.tier, tier_max=args.tier_max,
        )
        if result:
            display_entry(result)
        else:
            print("No matching enemies for those conditions.")

    elif args.command == "stats":
        show_stats(enemies)

    elif args.command == "validate":
        issues = validate_enemies(enemies)
        if issues:
            for i in issues:
                print(f"  ISSUE: {i}")
            print(f"\nValidation found {len(issues)} issue(s).")
        else:
            print(f"Validation passed — {len(enemies)} entries, 0 issues.")

    elif args.command == "image-prompts":
        print(compile_image_prompts(enemies))

    # --- Encounter table commands ---
    elif args.command == "encounter-list":
        enc_all = load_encounters()
        filtered = filter_encounters(
            enc_all, terrain=args.terrain, tier=args.tier,
            tier_min=args.tier_min, tier_max=args.tier_max,
            season=args.season, difficulty=args.difficulty,
        )
        if args.wolfshead:
            filtered = [e for e in filtered if e.get("id", "").startswith("ENC_WHEAD_")]
        display_encounter_list(filtered)

    elif args.command == "encounter-roll":
        enc_all = load_encounters()
        for i in range(args.count):
            if i > 0:
                print(f"\n{'#' * 70}\n")
            if args.wolfshead:
                pool = [e for e in enc_all if e.get("id", "").startswith("ENC_WHEAD_")]
            else:
                pool = enc_all
            result = roll_encounter(
                pool, terrain=args.terrain, season=args.season,
                tier=args.tier, tier_max=args.tier_max,
                difficulty=args.difficulty,
            )
            if result:
                display_encounter(result, enemies)
            else:
                print("No matching encounters for those conditions.")
                break

    elif args.command == "encounter-show":
        enc_all = load_encounters()
        match = [e for e in enc_all if e.get("id") == args.id]
        if match:
            display_encounter(match[0], enemies)
        else:
            print(f"No encounter with ID '{args.id}'.")

    elif args.command == "encounter-stats":
        enc_all = load_encounters()
        encounter_stats(enc_all)

    elif args.command == "encounter-validate":
        enc_all = load_encounters()
        issues = validate_encounters(enc_all, enemies)
        if issues:
            for i in issues:
                print(f"  ISSUE: {i}")
            print(f"\nEncounter validation found {len(issues)} issue(s).")
        else:
            print(f"Encounter validation passed — {len(enc_all)} encounters, 0 issues.")


if __name__ == "__main__":
    main()
