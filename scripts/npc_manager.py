#!/usr/bin/env python3
"""
Iron Ledger — NPC Database Manager

CLI tool for querying, filtering, and analysing the named NPC database
across all five category files.

Usage:
    python npc_manager.py list
    python npc_manager.py list --category settlement --settlement "Frostfjord Hollow"
    python npc_manager.py list --category band --band "Voss's Black Axes"
    python npc_manager.py list --category traveling --role merchant
    python npc_manager.py list --category antagonist --threat high
    python npc_manager.py list --category supernatural --type named_draugr
    python npc_manager.py show NPC_SET_001
    python npc_manager.py stats
    python npc_manager.py validate
    python npc_manager.py relationships NPC_SET_001
    python npc_manager.py web --settlement "Grimholt"
    python npc_manager.py image-prompts --category settlement

Schema: data/npcs/NPC_SCHEMA.md
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

# --- Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
NPC_DIR = DATA_DIR / "npcs"
REL_WEB = NPC_DIR / "relationship_web.yaml"

# --- Category mapping ---
CATEGORY_FILES = {
    "settlement": "settlement_npcs.yaml",
    "band": "rival_band_npcs.yaml",
    "traveling": "traveling_npcs.yaml",
    "antagonist": "antagonist_npcs.yaml",
    "supernatural": "supernatural_npcs.yaml",
}

VALID_STATS = {"MIG", "NIM", "TOU", "WIT", "WIL", "WYR"}

VALID_SKILLS = {
    "Axes", "Blades", "Spears", "Brawl", "Shields", "Bows",
    "Command", "Intimidate", "Persuade", "Bargain", "Deceive",
    "Track", "Navigate", "Forage", "Survival", "Shelter", "Heal",
    "Rune-lore", "Wyrd-reading", "Spirit-lore", "Smithing", "Sagas",
    "Weather-sense", "Stealth",
}


# ============================================================
# Data Loading
# ============================================================

def load_all_npcs() -> list[dict]:
    """Load and merge NPCs from all YAML files under data/npcs/."""
    all_npcs: list[dict] = []
    if not NPC_DIR.exists():
        return all_npcs
    for cat, filename in CATEGORY_FILES.items():
        path = NPC_DIR / filename
        if not path.exists():
            continue
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data and "npcs" in data:
                for entry in data["npcs"]:
                    entry["_source"] = filename
                    entry["_category"] = cat
                    all_npcs.append(entry)
        except (yaml.YAMLError, OSError) as exc:
            print(f"Warning: failed to load {filename}: {exc}", file=sys.stderr)
    return all_npcs


def load_relationship_web() -> dict:
    """Load the relationship web YAML."""
    if not REL_WEB.exists():
        return {}
    with open(REL_WEB, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# ============================================================
# Filtering
# ============================================================

def filter_npcs(
    npcs: list[dict],
    category: str | None = None,
    settlement: str | None = None,
    band: str | None = None,
    role: str | None = None,
    threat: str | None = None,
    npc_type: str | None = None,
    region: str | None = None,
    min_wyr: int | None = None,
) -> list[dict]:
    """Filter NPCs by multiple criteria."""
    result = npcs
    if category:
        result = [n for n in result if n.get("_category") == category]
    if settlement:
        low = settlement.lower()
        result = [n for n in result if low in n.get("settlement", "").lower()
                  or low in n.get("base", "").lower()
                  or low in n.get("bound_location", "").lower()]
    if band:
        low = band.lower()
        result = [n for n in result if low in n.get("band", "").lower()]
    if role:
        result = [n for n in result if n.get("role") == role]
    if threat:
        result = [n for n in result if n.get("threat_level") == threat]
    if npc_type:
        result = [n for n in result if n.get("type") == npc_type]
    if region:
        result = [n for n in result if n.get("travel_region") == region]
    if min_wyr is not None:
        result = [n for n in result if n.get("stats", {}).get("WYR", 0) >= min_wyr]
    return result


# ============================================================
# Display
# ============================================================

def display_list(npcs: list[dict]) -> None:
    """Print a compact list of NPCs."""
    if not npcs:
        print("No matching NPCs found.")
        return
    print(f"{'ID':<18} {'Name':<28} {'Call Name':<22} {'Category':<14} {'Role/Type'}")
    print("-" * 95)
    for n in sorted(npcs, key=lambda x: x.get("id", "")):
        role_or_type = n.get("role") or n.get("type") or "—"
        print(
            f"{n.get('id', '???'):<18} "
            f"{n.get('name', '???'):<28} "
            f"{n.get('call_name', '—'):<22} "
            f"{n.get('_category', '???'):<14} "
            f"{role_or_type}"
        )
    print(f"\n{len(npcs)} NPCs.")


def display_entry(entry: dict) -> None:
    """Print full details of a single NPC."""
    print(f"\n=== {entry.get('name', '???')} \"{entry.get('call_name', '')}\" ({entry.get('id', '???')}) ===")
    print(f"Category: {entry.get('_category', '?')} | Source: {entry.get('_source', '?')}")

    for loc_key in ("settlement", "band", "base", "bound_location", "travel_region"):
        val = entry.get(loc_key)
        if val:
            print(f"{loc_key.replace('_', ' ').title()}: {val}")

    role_or_type = entry.get("role") or entry.get("type")
    if role_or_type:
        print(f"Role/Type: {role_or_type}")

    if entry.get("threat_level"):
        print(f"Threat: {entry['threat_level']}")

    print(f"\n{entry.get('description', '')}")

    stats = entry.get("stats", {})
    print(f"\nStats: MIG {stats.get('MIG', '-')} | NIM {stats.get('NIM', '-')} | "
          f"TOU {stats.get('TOU', '-')} | WIT {stats.get('WIT', '-')} | "
          f"WIL {stats.get('WIL', '-')} | WYR {stats.get('WYR', '-')}")

    if entry.get("hp") is not None:
        print(f"HP: {entry['hp']}")

    skills = entry.get("skills", [])
    if skills:
        skill_str = ", ".join(f"{s['name']} {s['rank']}" for s in skills)
        print(f"Skills: {skill_str}")

    gear = entry.get("gear", {})
    weapons = gear.get("weapons", [])
    if weapons:
        for w in weapons:
            print(f"Weapon: {w.get('name', '?')} (type={w.get('type')}, dmg={w.get('base_damage')})")
    armor = gear.get("armor", {})
    if armor:
        parts = [f"{k}: {v}" for k, v in armor.items() if v and v != "None"]
        if parts:
            print(f"Armor: {', '.join(parts)}")

    abilities = entry.get("abilities", [])
    if abilities:
        print("\nAbilities:")
        for a in abilities:
            print(f"  - {a}")

    print(f"\nPersonality: {entry.get('personality', '—')}")
    print(f"Agenda: {entry.get('agenda', '—')}")

    if entry.get("scheme"):
        print(f"Scheme: {entry['scheme']}")
    if entry.get("resources"):
        print(f"Resources: {entry['resources']}")
    if entry.get("vulnerability"):
        print(f"Vulnerability: {entry['vulnerability']}")
    if entry.get("trigger"):
        print(f"Trigger: {entry['trigger']}")
    if entry.get("loyalty") is not None:
        print(f"Loyalty: {entry['loyalty']}/5")
    if entry.get("services"):
        print(f"Services: {entry['services']}")
    if entry.get("knowledge"):
        print(f"Knowledge: {entry['knowledge']}")
    if entry.get("can_communicate") is not None:
        print(f"Can Communicate: {entry['can_communicate']} ({entry.get('communication_method', '?')})")
    if entry.get("danger_level"):
        print(f"Danger: {entry['danger_level']}")

    print(f"\nSecret: {entry.get('secret', '—')}")

    rels = entry.get("relationships", [])
    if rels:
        print("\nRelationships:")
        for r in rels:
            print(f"  → {r.get('target', '?')} [{r.get('type', '?')}] — {r.get('note', '')}")

    chains = entry.get("associated_chains", [])
    if chains:
        print(f"Event Chains: {', '.join(chains)}")
    barrows = entry.get("associated_barrows", [])
    if barrows:
        print(f"Barrows: {', '.join(barrows)}")
    hooks = entry.get("interaction_hooks", [])
    if hooks:
        print("\nInteraction Hooks:")
        for h in hooks:
            print(f"  - {h}")

    if entry.get("image_prompt"):
        print(f"\nImage Prompt: {entry['image_prompt']}")


def display_relationships(npc_id: str, npcs: list[dict]) -> None:
    """Show all relationships involving a specific NPC."""
    npc = next((n for n in npcs if n.get("id") == npc_id), None)
    if not npc:
        print(f"NPC {npc_id} not found.")
        return

    print(f"\n=== Relationships for {npc.get('name', '?')} ({npc_id}) ===\n")

    # Outgoing
    rels = npc.get("relationships", [])
    if rels:
        print("Outgoing:")
        for r in rels:
            print(f"  → {r.get('target', '?')} [{r.get('type', '?')}] — {r.get('note', '')}")

    # Incoming: find all NPCs that reference this NPC
    name = npc.get("name", "")
    call = npc.get("call_name", "")
    incoming = []
    for other in npcs:
        if other.get("id") == npc_id:
            continue
        for r in other.get("relationships", []):
            target = r.get("target", "")
            if npc_id in target or name in target or (call and call in target):
                incoming.append((other, r))

    if incoming:
        print("\nIncoming:")
        for other, r in incoming:
            print(f"  ← {other.get('name', '?')} ({other.get('id', '?')}) "
                  f"[{r.get('type', '?')}] — {r.get('note', '')}")

    if not rels and not incoming:
        print("  No relationships found.")


def display_web(npcs: list[dict], settlement: str | None = None) -> None:
    """Display the relationship web as a text graph."""
    if settlement:
        low = settlement.lower()
        subset = [n for n in npcs
                  if low in n.get("settlement", "").lower()
                  or low in n.get("base", "").lower()
                  or low in n.get("bound_location", "").lower()]
    else:
        subset = npcs

    if not subset:
        print("No NPCs found for that filter.")
        return

    print(f"\n=== Relationship Web ({len(subset)} NPCs) ===\n")
    for n in sorted(subset, key=lambda x: x.get("id", "")):
        rels = n.get("relationships", [])
        if rels:
            for r in rels:
                print(f"  {n.get('call_name', n.get('name', '?')):<24} "
                      f"--[{r.get('type', '?'):<8}]--> "
                      f"{r.get('target', '?')}")


# ============================================================
# Statistics
# ============================================================

def display_stats(npcs: list[dict]) -> None:
    """Print summary statistics for the NPC database."""
    print(f"\n=== NPC Database Statistics ===\n")
    print(f"Total NPCs: {len(npcs)}\n")

    cat_counts = Counter(n.get("_category") for n in npcs)
    print("By Category:")
    for cat in sorted(CATEGORY_FILES.keys()):
        print(f"  {cat:<16} {cat_counts.get(cat, 0)}")

    role_counts = Counter(n.get("role") or n.get("type") for n in npcs)
    print("\nBy Role/Type:")
    for role, count in role_counts.most_common():
        print(f"  {role:<24} {count}")

    # Settlement distribution
    set_counts: Counter[str] = Counter()
    for n in npcs:
        for key in ("settlement", "base"):
            if n.get(key):
                set_counts[n[key]] += 1
    if set_counts:
        print("\nBy Settlement/Base:")
        for loc, count in set_counts.most_common(20):
            print(f"  {loc:<28} {count}")

    # Band distribution
    band_counts = Counter(n.get("band") for n in npcs if n.get("band"))
    if band_counts:
        print("\nBy Band:")
        for band, count in band_counts.most_common():
            print(f"  {band:<28} {count}")

    # WYR distribution
    wyr_counts = Counter(n.get("stats", {}).get("WYR", 0) for n in npcs)
    print("\nWYR Distribution:")
    for wyr in sorted(wyr_counts.keys()):
        bar = "█" * wyr_counts[wyr]
        print(f"  WYR {wyr}: {bar} ({wyr_counts[wyr]})")

    # Threat levels (antagonists)
    threats = Counter(n.get("threat_level") for n in npcs if n.get("threat_level"))
    if threats:
        print("\nThreat Levels (Antagonists):")
        for t in ("low", "medium", "high"):
            print(f"  {t:<10} {threats.get(t, 0)}")

    # Relationship count
    total_rels = sum(len(n.get("relationships", [])) for n in npcs)
    print(f"\nTotal Relationships: {total_rels}")


# ============================================================
# Validation
# ============================================================

def validate_npcs(npcs: list[dict]) -> int:
    """Validate NPC data. Returns number of issues found."""
    issues = 0
    seen_ids: set[str] = set()

    for n in npcs:
        npc_id = n.get("id", "NO_ID")
        prefix = f"[{npc_id}]"

        # Duplicate ID
        if npc_id in seen_ids:
            print(f"{prefix} DUPLICATE ID")
            issues += 1
        seen_ids.add(npc_id)

        # Required fields (supernatural NPCs use different schema)
        is_supernatural = n.get("_category") == "supernatural"
        base_required = ["name", "description", "stats", "personality", "agenda", "secret"]
        if is_supernatural:
            # Supernatural NPCs use true_name/name, abilities instead of skills
            base_required.extend(["type", "abilities"])
        else:
            base_required.extend(["call_name", "skills"])
        for field in base_required:
            if not n.get(field):
                print(f"{prefix} Missing required field: {field}")
                issues += 1

        # Stats validation
        stats = n.get("stats", {})
        for stat in VALID_STATS:
            val = stats.get(stat)
            if val is None:
                print(f"{prefix} Missing stat: {stat}")
                issues += 1
            elif not isinstance(val, int) or val < 1 or val > 10:
                print(f"{prefix} Invalid stat {stat}={val} (must be 1-10)")
                issues += 1

        # Skills validation (skip for supernatural — they use abilities)
        if not is_supernatural:
            for s in n.get("skills", []):
                name = s.get("name", "")
                if name not in VALID_SKILLS:
                    print(f"{prefix} Unknown skill: {name}")
                    issues += 1
                rank = s.get("rank", 0)
                if not isinstance(rank, int) or rank < 1 or rank > 5:
                    print(f"{prefix} Invalid skill rank for {name}: {rank}")
                    issues += 1

        # Relationships
        for r in n.get("relationships", []):
            if not r.get("target"):
                print(f"{prefix} Relationship missing target")
                issues += 1
            if not r.get("type"):
                print(f"{prefix} Relationship missing type")
                issues += 1

    if issues == 0:
        print(f"Validated {len(npcs)} NPCs — 0 issues.")
    else:
        print(f"\n{issues} issues found across {len(npcs)} NPCs.")
    return issues


# ============================================================
# Image Prompts
# ============================================================

def display_image_prompts(npcs: list[dict]) -> None:
    """Dump all image prompts for batch art generation."""
    for n in sorted(npcs, key=lambda x: x.get("id", "")):
        prompt = n.get("image_prompt")
        if prompt:
            print(f"[{n.get('id')}] {n.get('name', '?')}")
            print(f"  {prompt}\n")


# ============================================================
# CLI
# ============================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Iron Ledger — NPC Database Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    # list
    ls = sub.add_parser("list", help="List NPCs with optional filters")
    ls.add_argument("--category", choices=list(CATEGORY_FILES.keys()))
    ls.add_argument("--settlement")
    ls.add_argument("--band")
    ls.add_argument("--role")
    ls.add_argument("--threat", choices=["low", "medium", "high"])
    ls.add_argument("--type", dest="npc_type")
    ls.add_argument("--region")
    ls.add_argument("--min-wyr", type=int)

    # show
    sh = sub.add_parser("show", help="Show full details of an NPC")
    sh.add_argument("npc_id")

    # stats
    sub.add_parser("stats", help="Database statistics")

    # validate
    sub.add_parser("validate", help="Validate all NPC data")

    # relationships
    rel = sub.add_parser("relationships", help="Show relationships for an NPC")
    rel.add_argument("npc_id")

    # web
    web = sub.add_parser("web", help="Display relationship web")
    web.add_argument("--settlement")

    # image-prompts
    ip = sub.add_parser("image-prompts", help="Dump image prompts")
    ip.add_argument("--category", choices=list(CATEGORY_FILES.keys()))

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    npcs = load_all_npcs()
    if not npcs:
        print("No NPC data found. Check data/npcs/ directory.", file=sys.stderr)
        sys.exit(1)

    if args.command == "list":
        filtered = filter_npcs(
            npcs,
            category=args.category,
            settlement=args.settlement,
            band=args.band,
            role=args.role,
            threat=args.threat,
            npc_type=args.npc_type,
            region=args.region,
            min_wyr=args.min_wyr,
        )
        display_list(filtered)

    elif args.command == "show":
        entry = next((n for n in npcs if n.get("id") == args.npc_id), None)
        if not entry:
            print(f"NPC {args.npc_id} not found.")
            sys.exit(1)
        display_entry(entry)

    elif args.command == "stats":
        display_stats(npcs)

    elif args.command == "validate":
        issues = validate_npcs(npcs)
        sys.exit(1 if issues > 0 else 0)

    elif args.command == "relationships":
        display_relationships(args.npc_id, npcs)

    elif args.command == "web":
        display_web(npcs, settlement=args.settlement)

    elif args.command == "image-prompts":
        filtered = npcs
        if args.category:
            filtered = [n for n in npcs if n.get("_category") == args.category]
        display_image_prompts(filtered)


if __name__ == "__main__":
    main()
