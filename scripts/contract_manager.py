#!/usr/bin/env python3
"""
Iron Ledger — Contract Manager (Extended)

Loads contracts from multiple YAML files in data/contracts/ and the legacy
contracts_available.yaml. Supports filtering by season, settlement, faction,
risk, type, and year. Tracks contract chains and generates contract pools.

Usage:
    python contract_manager.py list
    python contract_manager.py list --settlement "Frostfjord Hollow" --season winter
    python contract_manager.py list --faction "The Iron Grip" --year 313
    python contract_manager.py list --type barrow_clear --risk high
    python contract_manager.py show CONT_SET_001
    python contract_manager.py pool --reputation 2 --settlement "Deepholm" --season summer --year 313
    python contract_manager.py chains
    python contract_manager.py chains --from CONT_SET_001
    python contract_manager.py stats
    python contract_manager.py validate
"""

import argparse
import glob
import json
import os
import sys
import textwrap

import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
CONTRACTS_DIR = os.path.join(DATA_DIR, "contracts")


def load_all_contracts():
    """Load contracts from all YAML files in data/contracts/ and legacy file."""
    all_contracts = []
    sources = {}

    # Load from data/contracts/*.yaml
    if os.path.isdir(CONTRACTS_DIR):
        for fpath in sorted(glob.glob(os.path.join(CONTRACTS_DIR, "*.yaml"))):
            fname = os.path.basename(fpath)
            with open(fpath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            contracts = data.get("contracts", [])
            for c in contracts:
                c["_source"] = fname
            all_contracts.extend(contracts)
            sources[fname] = len(contracts)

    # Load legacy contracts_available.yaml
    legacy_path = os.path.join(DATA_DIR, "contracts_available.yaml")
    if os.path.exists(legacy_path):
        with open(legacy_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        # Active contract
        active = data.get("active_contract")
        if active:
            active["_source"] = "contracts_available.yaml"
            active["_legacy"] = True
            all_contracts.append(active)
        # Available contracts
        available = data.get("available_contracts", [])
        for c in available:
            c["_source"] = "contracts_available.yaml"
            c["_legacy"] = True
        all_contracts.extend(available)
        sources["contracts_available.yaml"] = 1 + len(available)

    return all_contracts, sources


def filter_contracts(contracts, settlement=None, region=None, season=None,
                     year=None, faction=None, risk=None, contract_type=None,
                     min_reputation=None, max_reputation=None):
    """Filter contracts by multiple criteria."""

    def _norm(v):
        return (v or "").lower()

    results = []
    for c in contracts:
        if settlement and _norm(c.get("settlement")) != settlement.lower():
            continue
        if region and _norm(c.get("region")) != region.lower():
            continue
        if season and c.get("season", "any") not in (season, "any"):
            continue
        if year:
            yr = c.get("year_range")
            if yr and (year < yr[0] or year > yr[1]):
                continue
        if faction:
            c_faction = c.get("faction")
            if c_faction and _norm(c_faction) != faction.lower():
                continue
            # Also check employer-based faction inference for settlement contracts
            if not c_faction:
                continue
        if risk and _norm(c.get("risk")) != risk.lower():
            continue
        if contract_type and _norm(c.get("type")) != contract_type.lower():
            continue
        if min_reputation is not None:
            c_min = c.get("min_reputation", 0)
            if c_min > min_reputation:
                continue
        results.append(c)
    return results


def generate_pool(contracts, reputation, settlement=None, season=None, year=None,
                  max_pool=6):
    """Generate a contract pool based on conditions."""
    candidates = filter_contracts(
        contracts, settlement=settlement, season=season, year=year,
        min_reputation=reputation
    )

    # Exclude faction-locked contracts unless reputation is high enough
    pool = []
    for c in candidates:
        req_rep = c.get("min_reputation", 0)
        if req_rep <= reputation:
            pool.append(c)

    # Sort by payment (descending) and take top N
    pool.sort(key=lambda x: x.get("payment_silver", 0), reverse=True)
    return pool[:max_pool]


def find_chains(contracts):
    """Find all contract chains (contracts that unlock others)."""
    chains = {}
    id_map = {c["id"]: c for c in contracts if "id" in c}

    for c in contracts:
        cid = c.get("id")
        if not cid:
            continue
        unlocks = []
        cons = c.get("consequences", {})
        success = cons.get("success", {})
        unlock_ids = success.get("unlocks") or []
        if not isinstance(unlock_ids, list):
            unlock_ids = []
        for uid in unlock_ids:
            if uid in id_map:
                unlocks.append(uid)
        if unlocks:
            chains[cid] = unlocks

    return chains


def trace_chain(chains, start_id, visited=None):
    """Trace a chain from a starting contract ID."""
    if visited is None:
        visited = set()
    if start_id in visited:
        return []
    visited.add(start_id)
    result = [start_id]
    for next_id in chains.get(start_id, []):
        result.extend(trace_chain(chains, next_id, visited))
    return result


# --- Display ---

def display_list(contracts, verbose=False):
    """Display contract list."""
    if not contracts:
        print("  No contracts match the filter.")
        return

    for c in contracts:
        cid = c.get("id", "???")
        ctype = c.get("type", "?")
        title = c.get("title", "Untitled")
        pay = c.get("payment_silver", 0)
        risk = c.get("risk", "?")
        settlement = c.get("settlement", "?")
        source = c.get("_source", "?")

        print(f"  {cid:16} [{ctype:16}] {title}")
        print(f"    {settlement:20} {pay:>4}s  risk:{risk:8}  ({source})")

        if verbose:
            hook = c.get("narrative_hook", "")
            if hook:
                wrapped = textwrap.fill(hook, width=64,
                                        initial_indent="    ", subsequent_indent="    ")
                print(wrapped)
            print()

    print(f"\n  Total: {len(contracts)} contracts")


def display_contract(contracts, contract_id):
    """Show full details of a single contract."""
    target = None
    for c in contracts:
        if c.get("id", "").lower() == contract_id.lower():
            target = c
            break

    if not target:
        print(f"Contract not found: {contract_id}")
        return

    print(f"\n{'=' * 60}")
    print(f"  {target.get('title', 'Untitled')} ({target.get('id', '?')})")
    print(f"{'=' * 60}")
    print(f"  Type:       {target.get('type', '?')}")
    print(f"  Employer:   {target.get('employer', '?')}")
    print(f"  Settlement: {target.get('settlement', '?')}")
    print(f"  Region:     {target.get('region', '?')}")
    print(f"  Season:     {target.get('season', '?')}")
    print(f"  Years:      {target.get('year_range', '?')}")
    print(f"  Payment:    {target.get('payment_silver', 0)} silver")
    bonus = target.get("bonus")
    if bonus:
        print(f"  Bonus:      {bonus}")
    advance = target.get("advance_silver", 0)
    if advance:
        print(f"  Advance:    {advance} silver")
    print(f"  Duration:   {target.get('duration_days', '?')} days")
    print(f"  Risk:       {target.get('risk', '?')}")
    print(f"  Min Rep:    {target.get('min_reputation', 0)}")
    print(f"  Band Min:   {target.get('band_size_min', '?')}")
    print(f"  Skills:     {', '.join(target.get('skills_valued', []))}")

    # Faction info
    faction = target.get("faction")
    if faction:
        print(f"\n  Faction:    {faction}")
    if target.get("forces_choice"):
        print(f"  FORCES CHOICE — taking this locks faction alignment")

    # Political conditions
    pol = target.get("political_conditions", {})
    if pol:
        blocks = pol.get("blocks_factions", [])
        if blocks:
            print(f"  Blocks:     {', '.join(blocks)}")
        req_event = pol.get("requires_event")
        if req_event:
            print(f"  Requires:   {req_event}")

    # Moral cost (desperate contracts)
    moral = target.get("moral_cost", {})
    if moral:
        print(f"\n  MORAL COST:")
        print(f"    Type:     {moral.get('type', '?')}")
        print(f"    {moral.get('description', '')}")
        morale = moral.get("band_morale_effect")
        if morale:
            print(f"    Morale:   {morale:+d}")

    # Supernatural elements
    super_elem = target.get("supernatural_elements", {})
    if super_elem:
        print(f"\n  Supernatural:")
        print(f"    Veil:     {super_elem.get('veil_proximity', '?')}")
        print(f"    Curse:    {super_elem.get('curse_risk', '?')}")
        print(f"    Seidr:    {'useful' if super_elem.get('seidr_useful') else 'not needed'}")

    # Consequences
    cons = target.get("consequences", {})
    success = cons.get("success", {})
    failure = cons.get("failure", {})
    if success:
        print(f"\n  On Success:")
        if success.get("reputation_change"):
            print(f"    Reputation: {success['reputation_change']:+d}")
        standing = success.get("standing_change", {})
        for k, v in standing.items():
            print(f"    Standing ({k}): {v:+d}")
        unlocks = success.get("unlocks", [])
        if unlocks:
            print(f"    Unlocks: {', '.join(unlocks)}")
    if failure:
        print(f"\n  On Failure:")
        if failure.get("reputation_change"):
            print(f"    Reputation: {failure['reputation_change']:+d}")

    # Narrative hook
    hook = target.get("narrative_hook", "")
    if hook:
        print(f"\n  Narrative Hook:")
        wrapped = textwrap.fill(hook, width=60,
                                initial_indent="    ", subsequent_indent="    ")
        print(wrapped)

    print(f"\n  Source: {target.get('_source', '?')}")
    print(f"{'=' * 60}\n")


def display_chains(contracts, from_id=None):
    """Display contract chains."""
    chains = find_chains(contracts)

    if from_id:
        if from_id not in chains and from_id not in {c.get("id") for c in contracts}:
            print(f"Contract {from_id} not found.")
            return
        chain = trace_chain(chains, from_id)
        print(f"\n  Chain from {from_id}:")
        id_map = {c["id"]: c for c in contracts if "id" in c}
        for i, cid in enumerate(chain):
            c = id_map.get(cid, {})
            prefix = "  └─" if i == len(chain) - 1 else "  ├─"
            print(f"  {prefix} {cid}: {c.get('title', '?')} ({c.get('type', '?')})")
        return

    if not chains:
        print("  No contract chains found.")
        return

    # Find chain roots (contracts that aren't unlocked by anything else)
    all_unlocked = set()
    for unlocks in chains.values():
        all_unlocked.update(unlocks)
    roots = [cid for cid in chains if cid not in all_unlocked]

    id_map = {c["id"]: c for c in contracts if "id" in c}
    print(f"\n  Contract Chains ({len(roots)} chains found):")
    print(f"{'=' * 60}")
    for root in sorted(roots):
        chain = trace_chain(chains, root)
        print(f"\n  Chain: {root}")
        for i, cid in enumerate(chain):
            c = id_map.get(cid, {})
            indent = "    " * min(i, 3)
            print(f"  {indent}→ {cid}: {c.get('title', '?')}")
    print(f"{'=' * 60}\n")


def display_stats(contracts, sources):
    """Display contract database statistics."""
    print(f"\n{'Contract Database Statistics':^60}")
    print(f"{'=' * 60}")
    print(f"  Total contracts: {len(contracts)}")

    # By source file
    print(f"\n  By Source:")
    for src, count in sorted(sources.items()):
        print(f"    {src:40} {count}")

    # By type
    types = {}
    for c in contracts:
        t = c.get("type", "unknown")
        types[t] = types.get(t, 0) + 1
    print(f"\n  By Type:")
    for t, count in sorted(types.items(), key=lambda x: -x[1]):
        print(f"    {t:20} {count}")

    # By risk
    risks = {}
    for c in contracts:
        r = c.get("risk", "unknown")
        risks[r] = risks.get(r, 0) + 1
    print(f"\n  By Risk:")
    for r in ["low", "moderate", "high", "extreme"]:
        print(f"    {r:20} {risks.get(r, 0)}")

    # By settlement
    settlements = {}
    for c in contracts:
        s = c.get("settlement", "unknown")
        settlements[s] = settlements.get(s, 0) + 1
    print(f"\n  By Settlement (top 10):")
    for s, count in sorted(settlements.items(), key=lambda x: -x[1])[:10]:
        print(f"    {s:25} {count}")

    # Payment stats
    payments = [c.get("payment_silver", 0) for c in contracts if c.get("payment_silver")]
    if payments:
        print(f"\n  Payment Range: {min(payments)}-{max(payments)} silver")
        print(f"  Average Pay:   {sum(payments) // len(payments)} silver")

    # Chains
    chains = find_chains(contracts)
    print(f"\n  Contract chains: {len(chains)}")

    # Faction contracts
    faction_contracts = [c for c in contracts if c.get("faction")]
    print(f"  Faction contracts: {len(faction_contracts)}")

    # Desperate contracts
    desperate = [c for c in contracts if c.get("moral_cost")]
    print(f"  Desperate contracts: {len(desperate)}")

    # Supernatural
    supernatural = [c for c in contracts if c.get("supernatural_elements")]
    print(f"  Supernatural contracts: {len(supernatural)}")

    print(f"{'=' * 60}\n")


def validate_contracts(contracts):
    """Validate contract data integrity."""
    issues = []

    # Check IDs are unique
    ids = [c.get("id") for c in contracts if c.get("id")]
    dupes = set(x for x in ids if ids.count(x) > 1)
    if dupes:
        issues.append(f"Duplicate contract IDs: {dupes}")

    # Check required fields
    required = ["id", "type", "title"]
    for c in contracts:
        cid = c.get("id", "???")
        for field in required:
            if field not in c:
                issues.append(f"{cid}: missing field '{field}'")

    # Check chain references point to existing contracts
    id_set = set(ids)
    chains = find_chains(contracts)
    for cid, unlocks in chains.items():
        for uid in unlocks:
            if uid not in id_set:
                issues.append(f"{cid}: unlocks unknown contract '{uid}'")

    # Report
    if issues:
        print(f"\nValidation found {len(issues)} issue(s):")
        for iss in issues:
            print(f"  - {iss}")
    else:
        print(f"\nValidation passed.")
        print(f"  Contracts:  {len(contracts)}")
        print(f"  Unique IDs: {len(id_set)}")
        print(f"  Chains:     {len(chains)}")

    return len(issues)


def main():
    parser = argparse.ArgumentParser(description="Iron Ledger Contract Manager (Extended)")
    subparsers = parser.add_subparsers(dest="command")

    # --- list ---
    list_p = subparsers.add_parser("list", help="List contracts with optional filters")
    list_p.add_argument("--settlement", type=str, help="Filter by settlement name")
    list_p.add_argument("--region", type=str, help="Filter by region")
    list_p.add_argument("--season", type=str, choices=["spring", "summer", "autumn", "winter"])
    list_p.add_argument("--year", type=int, help="Filter by year (312-315)")
    list_p.add_argument("--faction", type=str, help="Filter by faction")
    list_p.add_argument("--risk", type=str, choices=["low", "moderate", "high", "extreme"])
    list_p.add_argument("--type", type=str, dest="contract_type", help="Filter by contract type")
    list_p.add_argument("--verbose", action="store_true", help="Show narrative hooks")
    list_p.add_argument("--json", action="store_true")

    # --- show ---
    show_p = subparsers.add_parser("show", help="Show contract details")
    show_p.add_argument("contract_id", type=str, help="Contract ID")
    show_p.add_argument("--json", action="store_true")

    # --- pool ---
    pool_p = subparsers.add_parser("pool", help="Generate a contract pool")
    pool_p.add_argument("--reputation", type=int, required=True)
    pool_p.add_argument("--settlement", type=str)
    pool_p.add_argument("--season", type=str)
    pool_p.add_argument("--year", type=int)
    pool_p.add_argument("--max", type=int, default=6, dest="max_pool")
    pool_p.add_argument("--json", action="store_true")

    # --- chains ---
    chains_p = subparsers.add_parser("chains", help="Show contract chains")
    chains_p.add_argument("--from", type=str, dest="from_id",
                          help="Trace chain from a specific contract")

    # --- stats ---
    subparsers.add_parser("stats", help="Contract database statistics")

    # --- validate ---
    subparsers.add_parser("validate", help="Validate contract data integrity")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    contracts, sources = load_all_contracts()

    if args.command == "list":
        filtered = filter_contracts(
            contracts,
            settlement=args.settlement,
            region=args.region,
            season=args.season,
            year=args.year,
            faction=args.faction,
            risk=args.risk,
            contract_type=args.contract_type,
        )
        if args.json:
            # Strip internal fields
            clean = [{k: v for k, v in c.items() if not k.startswith("_")}
                     for c in filtered]
            print(json.dumps(clean, indent=2, ensure_ascii=False))
        else:
            display_list(filtered, verbose=args.verbose)

    elif args.command == "show":
        if args.json:
            target = None
            for c in contracts:
                if c.get("id", "").lower() == args.contract_id.lower():
                    target = c
                    break
            if target:
                clean = {k: v for k, v in target.items() if not k.startswith("_")}
                print(json.dumps(clean, indent=2, ensure_ascii=False))
            else:
                print(json.dumps({"error": f"Not found: {args.contract_id}"}))
        else:
            display_contract(contracts, args.contract_id)

    elif args.command == "pool":
        pool = generate_pool(
            contracts,
            reputation=args.reputation,
            settlement=args.settlement,
            season=args.season,
            year=args.year,
            max_pool=args.max_pool,
        )
        if args.json:
            clean = [{k: v for k, v in c.items() if not k.startswith("_")}
                     for c in pool]
            print(json.dumps(clean, indent=2, ensure_ascii=False))
        else:
            print(f"\n  Contract Pool (Rep {args.reputation}, max {args.max_pool}):")
            display_list(pool)

    elif args.command == "chains":
        display_chains(contracts, from_id=args.from_id)

    elif args.command == "stats":
        display_stats(contracts, sources)

    elif args.command == "validate":
        issue_count = validate_contracts(contracts)
        sys.exit(1 if issue_count > 0 else 0)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
