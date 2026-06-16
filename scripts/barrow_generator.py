#!/usr/bin/env python3
"""
Iron Ledger — Barrow Generator

Procedural barrow/dungeon generator using the barrow atlas, room templates,
encounter tables, and loot tables from data/barrows/.

Usage:
    python barrow_generator.py list
    python barrow_generator.py show --name "Whispering Barrow"
    python barrow_generator.py show --id BAR_001
    python barrow_generator.py generate --size medium --age ancient --region frostfjord
    python barrow_generator.py generate --barrow BAR_001
    python barrow_generator.py stats
    python barrow_generator.py validate
"""

import argparse
import json
import os
import random
import sys
import textwrap

import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data", "barrows")

# --- Size and depth mapping ---
SIZE_ROOM_COUNTS = {
    "small": (3, 5),
    "medium": (5, 9),
    "large": (9, 14),
    "vast": (14, 22),
}

SIZE_ORDER = ["small", "medium", "large", "vast"]
AGE_ORDER = ["recent", "old", "ancient", "primordial"]

DEPTH_BY_SIZE = {
    "small": 2,
    "medium": 3,
    "large": 3,
    "vast": 4,
}


def load_yaml(filename):
    """Load a YAML file from the barrows data directory."""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"Error: {path} not found.", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_barrow_atlas():
    """Load the barrow atlas from data/barrows/barrows.yaml."""
    path = os.path.join(DATA_DIR, "barrows.yaml")
    if not os.path.exists(path):
        print(f"Error: {path} not found.", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("barrows", [])


def load_room_templates():
    """Load room templates."""
    data = load_yaml("room_templates.yaml")
    return data.get("room_templates", [])


def load_encounter_tables():
    """Load encounter tables."""
    data = load_yaml("encounter_tables.yaml")
    return data.get("encounter_tables", [])


def load_loot_tables():
    """Load loot tables."""
    data = load_yaml("loot_tables.yaml")
    return data.get("loot_tables", {})


# --- Filtering helpers ---

def size_gte(room_min, barrow_size):
    """Check if barrow_size >= room's minimum size requirement."""
    if room_min not in SIZE_ORDER:
        return True
    return SIZE_ORDER.index(barrow_size) >= SIZE_ORDER.index(room_min)


def age_matches(room_affinity, barrow_age):
    """Check if the barrow age matches room's age affinity list."""
    if not room_affinity:
        return True
    return barrow_age in room_affinity


def filter_rooms(templates, barrow_size, barrow_age, category=None):
    """Filter room templates by barrow size, age, and optional category."""
    results = []
    for room in templates:
        if category and room.get("category") != category:
            continue
        if not size_gte(room.get("barrow_size_min", "small"), barrow_size):
            continue
        if not age_matches(room.get("barrow_age_affinity"), barrow_age):
            continue
        results.append(room)
    return results


def filter_encounters(encounters, barrow_size, barrow_age, depth_level):
    """Filter encounters by barrow parameters and depth."""
    results = []
    for enc in encounters:
        enc_sizes = enc.get("barrow_size", [])
        enc_ages = enc.get("barrow_age", [])
        enc_depths = enc.get("depth_level", [])
        if barrow_size not in enc_sizes:
            continue
        if barrow_age not in enc_ages:
            continue
        if depth_level not in enc_depths:
            continue
        results.append(enc)
    return results


def pick_loot(loot_tables, tier, count=1):
    """Pick random loot items from a tier."""
    tier_key = f"tier_{tier}"
    tier_data = loot_tables.get(tier_key)
    if not tier_data:
        return []
    items = tier_data.get("items", [])
    if not items:
        return []
    return random.sample(items, min(count, len(items)))


# --- Generation ---

def generate_barrow(barrow_size, barrow_age, region, all_templates, all_encounters, loot_tables):
    """Generate a procedural barrow layout."""
    min_rooms, max_rooms = SIZE_ROOM_COUNTS.get(barrow_size, (5, 9))
    num_rooms = random.randint(min_rooms, max_rooms)
    max_depth = DEPTH_BY_SIZE.get(barrow_size, 3)

    # Pick entry room
    entry_rooms = filter_rooms(all_templates, barrow_size, barrow_age, category="entry")
    if not entry_rooms:
        entry_rooms = filter_rooms(all_templates, barrow_size, barrow_age)

    layout = []
    used_room_ids = set()

    # Room 1 is always an entry
    entry = random.choice(entry_rooms) if entry_rooms else all_templates[0]
    used_room_ids.add(entry["id"])

    current_depth = 1
    rooms_per_depth = max(1, num_rooms // max_depth)

    layout.append(_build_room_entry(entry, current_depth, barrow_size, barrow_age,
                                     all_encounters, loot_tables))

    # Generate remaining rooms
    room_count = 1
    for i in range(1, num_rooms):
        room_count += 1
        # Advance depth periodically
        if room_count > rooms_per_depth * current_depth and current_depth < max_depth:
            current_depth += 1

        # Determine category distribution
        roll = random.random()
        if current_depth == max_depth and i == num_rooms - 1:
            # Last room in deepest level — try special/boss
            cat = "special"
        elif roll < 0.30:
            cat = "corridor"
        elif roll < 0.55:
            cat = "chamber"
        elif roll < 0.70:
            cat = "hazard"
        elif roll < 0.85:
            cat = "discovery"
        else:
            cat = None  # any

        candidates = filter_rooms(all_templates, barrow_size, barrow_age, category=cat)
        # Avoid repeats where possible
        fresh = [r for r in candidates if r["id"] not in used_room_ids]
        if fresh:
            room = random.choice(fresh)
        elif candidates:
            room = random.choice(candidates)
        else:
            # Fallback: any room that fits
            fallback = filter_rooms(all_templates, barrow_size, barrow_age)
            room = random.choice(fallback) if fallback else all_templates[0]

        used_room_ids.add(room["id"])
        layout.append(_build_room_entry(room, current_depth, barrow_size, barrow_age,
                                         all_encounters, loot_tables))

    return {
        "barrow_size": barrow_size,
        "barrow_age": barrow_age,
        "region": region,
        "total_rooms": len(layout),
        "max_depth": max_depth,
        "rooms": layout,
    }


def _build_room_entry(room_template, depth, barrow_size, barrow_age,
                       all_encounters, loot_tables):
    """Build a single room entry with encounters and loot."""
    entry = {
        "room_id": room_template["id"],
        "name": room_template["name"],
        "category": room_template["category"],
        "depth_level": depth,
        "description": room_template.get("description", ""),
        "features": room_template.get("features", []),
        "traps": [],
        "hazards": room_template.get("hazards", []),
        "encounter": None,
        "loot": [],
    }

    # Roll for trap
    traps = room_template.get("traps", [])
    if traps and random.random() < 0.5:
        entry["traps"] = [random.choice(traps)]

    # Roll for encounter
    available_enc = filter_encounters(all_encounters, barrow_size, barrow_age, depth)
    if available_enc and random.random() < 0.6:
        enc = random.choice(available_enc)
        entry["encounter"] = {
            "id": enc["id"],
            "name": enc["name"],
            "category": enc["category"],
            "description": enc.get("description", ""),
            "difficulty": enc.get("difficulty", "moderate"),
        }

    # Roll for loot (based on depth → tier)
    loot_tier = min(depth, 4)
    if random.random() < 0.4:
        items = pick_loot(loot_tables, loot_tier, count=random.randint(1, 2))
        entry["loot"] = [{"id": it["id"], "name": it["name"],
                          "value_silver": it.get("value_silver", 0)}
                         for it in items]

    return entry


# --- Display ---

def display_barrow(barrow_data, verbose=False):
    """Print a generated barrow layout."""
    print(f"\n{'=' * 60}")
    print(f"  BARROW — Size: {barrow_data['barrow_size'].upper()}, "
          f"Age: {barrow_data['barrow_age'].upper()}, Region: {barrow_data['region']}")
    print(f"  Rooms: {barrow_data['total_rooms']}, Max Depth: {barrow_data['max_depth']}")
    print(f"{'=' * 60}")

    for i, room in enumerate(barrow_data["rooms"], 1):
        depth_marker = ">" * room["depth_level"]
        print(f"\n  [{i}] {depth_marker} {room['name']} (Depth {room['depth_level']})")
        print(f"      Category: {room['category']}")

        if verbose and room.get("description"):
            wrapped = textwrap.fill(room["description"], width=60,
                                    initial_indent="      ", subsequent_indent="      ")
            print(wrapped)

        if room.get("features"):
            print(f"      Features: {', '.join(room['features'][:3])}")

        if room.get("traps"):
            for trap in room["traps"]:
                print(f"      TRAP: {trap['name']} [{trap.get('damage', '?')}]")

        if room.get("hazards"):
            print(f"      Hazards: {', '.join(room['hazards'][:2])}")

        if room.get("encounter"):
            enc = room["encounter"]
            print(f"      ENCOUNTER: {enc['name']} ({enc['difficulty']})")
            if verbose:
                wrapped = textwrap.fill(enc["description"], width=60,
                                        initial_indent="        ", subsequent_indent="        ")
                print(wrapped)

        if room.get("loot"):
            loot_str = ", ".join(f"{it['name']} ({it['value_silver']}s)" for it in room["loot"])
            print(f"      LOOT: {loot_str}")

    print(f"\n{'=' * 60}\n")


def list_barrows(barrows):
    """List all canon barrows."""
    print(f"\n{'Barrow Atlas':^60}")
    print(f"{'=' * 60}")
    current_region = None
    for b in sorted(barrows, key=lambda x: x.get("region", "")):
        region = b.get("region", "unknown")
        if region != current_region:
            current_region = region
            print(f"\n  --- {region.upper()} ---")
        state_icon = {"sealed": "[S]", "breached": "[B]", "active": "[A]",
                      "collapsed": "[X]"}.get(b.get("current_state", ""), "[?]")
        print(f"  {b['id']:8} {state_icon} {b['name']:<30} "
              f"Size:{b.get('size','?'):8} Age:{b.get('age','?'):10} "
              f"Loot:{b.get('loot_grade','?')}")
    print(f"\n  Total: {len(barrows)} barrows")
    print(f"{'=' * 60}\n")


def show_barrow(barrows, identifier):
    """Show details of a specific barrow by name or ID."""
    target = None
    for b in barrows:
        if b["id"].lower() == identifier.lower() or b["name"].lower() == identifier.lower():
            target = b
            break

    if not target:
        print(f"Barrow not found: {identifier}")
        print(f"Available: {', '.join(b['id'] for b in barrows)}")
        return

    print(f"\n{'=' * 60}")
    print(f"  {target['name']} ({target['id']})")
    print(f"{'=' * 60}")
    print(f"  Region:     {target.get('region', '?')}")
    print(f"  Nearest:    {target.get('nearest_settlement', '?')} "
          f"({target.get('distance_hours', '?')}h travel)")
    print(f"  Terrain:    {target.get('terrain', '?')}")
    print(f"  Size:       {target.get('size', '?')}")
    print(f"  Age:        {target.get('age', '?')}")
    print(f"  State:      {target.get('current_state', '?')}")
    print(f"  Loot Grade: {target.get('loot_grade', '?')}")

    occ = target.get("occupants", {})
    if occ:
        print(f"\n  Occupants:")
        print(f"    Primary:   {occ.get('primary', 'none')}")
        secondary = occ.get("secondary", [])
        if secondary:
            print(f"    Secondary: {', '.join(secondary)}")
        if occ.get("boss"):
            print(f"    BOSS:      {occ['boss']}")
        print(f"    Est. count: {occ.get('estimated_count', '?')}")

    hooks = target.get("lore_hooks", [])
    if hooks:
        print(f"\n  Lore Hooks:")
        for h in hooks:
            print(f"    - {h}")

    dangers = target.get("known_dangers", [])
    if dangers:
        print(f"\n  Known Dangers:")
        for d in dangers:
            print(f"    - {d}")

    chains = target.get("event_chains", [])
    if chains:
        print(f"\n  Event Chains: {', '.join(chains)}")

    contracts = target.get("associated_contracts", [])
    if contracts:
        print(f"  Contracts:    {', '.join(contracts)}")

    if target.get("notes"):
        print(f"\n  Notes: {target['notes']}")

    print(f"{'=' * 60}\n")


def barrow_stats(barrows):
    """Print statistics about the barrow atlas."""
    print(f"\n{'Barrow Atlas Statistics':^60}")
    print(f"{'=' * 60}")
    print(f"  Total barrows: {len(barrows)}")

    # By region
    regions = {}
    for b in barrows:
        r = b.get("region", "unknown")
        regions[r] = regions.get(r, 0) + 1
    print(f"\n  By Region:")
    for r, c in sorted(regions.items()):
        print(f"    {r:15} {c}")

    # By size
    sizes = {}
    for b in barrows:
        s = b.get("size", "unknown")
        sizes[s] = sizes.get(s, 0) + 1
    print(f"\n  By Size:")
    for s in SIZE_ORDER:
        print(f"    {s:15} {sizes.get(s, 0)}")

    # By state
    states = {}
    for b in barrows:
        st = b.get("current_state", "unknown")
        states[st] = states.get(st, 0) + 1
    print(f"\n  By State:")
    for st, c in sorted(states.items()):
        print(f"    {st:15} {c}")

    # By age
    ages = {}
    for b in barrows:
        a = b.get("age", "unknown")
        ages[a] = ages.get(a, 0) + 1
    print(f"\n  By Age:")
    for a in AGE_ORDER:
        print(f"    {a:15} {ages.get(a, 0)}")

    # Boss barrows
    boss_barrows = [b for b in barrows if b.get("occupants", {}).get("boss")]
    print(f"\n  Boss barrows: {len(boss_barrows)}")
    for b in boss_barrows:
        print(f"    {b['id']} {b['name']} — {b['occupants']['boss']}")

    print(f"{'=' * 60}\n")


def validate_barrows(barrows, templates, encounters, loot_tables):
    """Validate data integrity across barrow files."""
    issues = []

    # Check barrow IDs are unique
    ids = [b["id"] for b in barrows]
    dupes = [x for x in ids if ids.count(x) > 1]
    if dupes:
        issues.append(f"Duplicate barrow IDs: {set(dupes)}")

    # Check required fields
    required = ["id", "name", "region", "nearest_settlement", "size", "age", "current_state"]
    for b in barrows:
        for field in required:
            if field not in b:
                issues.append(f"{b.get('id', '???')}: missing field '{field}'")

    # Check sizes and ages are valid
    for b in barrows:
        if b.get("size") not in SIZE_ORDER:
            issues.append(f"{b['id']}: invalid size '{b.get('size')}'")
        if b.get("age") not in AGE_ORDER + ["primordial"]:
            issues.append(f"{b['id']}: invalid age '{b.get('age')}'")

    # Check room template IDs are unique
    template_ids = [t["id"] for t in templates]
    t_dupes = [x for x in template_ids if template_ids.count(x) > 1]
    if t_dupes:
        issues.append(f"Duplicate room template IDs: {set(t_dupes)}")

    # Check encounter IDs are unique
    enc_ids = [e["id"] for e in encounters]
    e_dupes = [x for x in enc_ids if enc_ids.count(x) > 1]
    if e_dupes:
        issues.append(f"Duplicate encounter IDs: {set(e_dupes)}")

    # Report
    if issues:
        print(f"\nValidation found {len(issues)} issue(s):")
        for iss in issues:
            print(f"  - {iss}")
    else:
        print(f"\nValidation passed.")
        print(f"  Barrows:    {len(barrows)}")
        print(f"  Rooms:      {len(templates)}")
        print(f"  Encounters: {len(encounters)}")
        tier_counts = []
        for t in range(1, 5):
            key = f"tier_{t}"
            items = loot_tables.get(key, {}).get("items", [])
            tier_counts.append(f"T{t}:{len(items)}")
        print(f"  Loot items: {', '.join(tier_counts)}")

    return len(issues)


def main():
    parser = argparse.ArgumentParser(description="Iron Ledger Barrow Generator")
    subparsers = parser.add_subparsers(dest="command")

    # --- list ---
    subparsers.add_parser("list", help="List all canon barrows")

    # --- show ---
    show_p = subparsers.add_parser("show", help="Show barrow details")
    show_g = show_p.add_mutually_exclusive_group(required=True)
    show_g.add_argument("--name", type=str, help="Barrow name")
    show_g.add_argument("--id", type=str, help="Barrow ID (e.g. BAR_001)")

    # --- generate ---
    gen_p = subparsers.add_parser("generate", help="Generate a procedural barrow")
    gen_p.add_argument("--size", type=str, default="medium",
                       choices=SIZE_ORDER)
    gen_p.add_argument("--age", type=str, default="ancient",
                       choices=AGE_ORDER + ["primordial"])
    gen_p.add_argument("--region", type=str, default="unknown")
    gen_p.add_argument("--barrow", type=str, default=None,
                       help="Generate from a canon barrow ID (uses its size/age/region)")
    gen_p.add_argument("--seed", type=int, default=None,
                       help="Random seed for reproducible generation")
    gen_p.add_argument("--verbose", action="store_true",
                       help="Show full descriptions")
    gen_p.add_argument("--json", action="store_true",
                       help="Output JSON instead of formatted text")

    # --- stats ---
    subparsers.add_parser("stats", help="Barrow atlas statistics")

    # --- validate ---
    subparsers.add_parser("validate", help="Validate barrow data files")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Load data
    barrows = load_barrow_atlas()
    templates = load_room_templates()
    encounters = load_encounter_tables()
    loot_tables = load_loot_tables()

    if args.command == "list":
        list_barrows(barrows)

    elif args.command == "show":
        identifier = args.name or args.id
        show_barrow(barrows, identifier)

    elif args.command == "generate":
        size = args.size
        age = args.age
        region = args.region

        # If generating from a canon barrow, use its parameters
        if args.barrow:
            canon = None
            for b in barrows:
                if b["id"].lower() == args.barrow.lower():
                    canon = b
                    break
            if not canon:
                print(f"Barrow {args.barrow} not found in atlas.")
                sys.exit(1)
            size = canon["size"]
            age = canon["age"]
            region = canon["region"]

        if args.seed is not None:
            random.seed(args.seed)

        result = generate_barrow(size, age, region, templates, encounters, loot_tables)

        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            display_barrow(result, verbose=args.verbose)

    elif args.command == "stats":
        barrow_stats(barrows)

    elif args.command == "validate":
        issue_count = validate_barrows(barrows, templates, encounters, loot_tables)
        sys.exit(1 if issue_count > 0 else 0)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
