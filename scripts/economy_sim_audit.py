#!/usr/bin/env python3
"""Audit economy data and identify missing simulation targets.

The report compares detailed economic source data to the dimensions
currently modeled by village_politics.py and related state files.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _field_counter(records: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for record in records:
        for key in record.keys():
            counter[key] += 1
    return counter


def analyze_settlements() -> dict[str, Any]:
    detailed = _load_yaml(DATA_DIR / "economy" / "settlement_economies.yaml")["settlement_economies"]
    political = _load_yaml(DATA_DIR / "political_state.yaml")["economies"]

    simulated_fields = {
        "population",
        "crop_fields",
        "livestock",
        "food_stores_days",
        "food_stores_max",
        "silver_treasury",
        "weekly_trade_income",
        "weekly_expenses",
        "labor_allocation",
    }
    detailed_fields = set(_field_counter(detailed).keys())
    missing = sorted(detailed_fields - simulated_fields - {"settlement"})

    priorities = [
        (
            "import dependency and shortage propagation",
            "imports",
            "The detailed data tracks urgent imports, but the economy tick only uses flat income and food stores.",
        ),
        (
            "commodity production by good",
            "production",
            "Settlements list concrete goods and weekly quantities, but no simulation converts them into stocks, trade, or bargaining power.",
        ),
        (
            "export destination throughput",
            "exports",
            "Destination-specific exports exist, but route closures do not currently reduce settlement income by commodity or partner.",
        ),
        (
            "route-level trade flow and disruption",
            "trade_routes",
            "Routes include frequency and goods flow, but the simulation only applies feud penalties rather than route capacity or blockade state.",
        ),
        (
            "market liquidity and local price pressure",
            "market",
            "Market day, trader traffic, exotic goods, and price modifiers are defined but not fed into dynamic pricing.",
        ),
        (
            "strategic resource control",
            "strategic_resources",
            "Military-economic assets like harbours, tar-works, and smithies are present only as prose.",
        ),
        (
            "wartime endurance and essential imports",
            "wartime_impact",
            "Siege endurance and at-risk imports are authored per settlement but not simulated.",
        ),
        (
            "economic vulnerability triggers",
            "economic_vulnerabilities",
            "Arson, blockade chokepoints, and single-point failures are enumerated but do not drive state changes.",
        ),
    ]

    mapped_settlements = sorted(set(political.keys()))
    detailed_settlements = sorted({entry["settlement"] for entry in detailed})
    return {
        "source_count": len(detailed),
        "state_count": len(mapped_settlements),
        "detailed_only_fields": missing,
        "settlement_name_mismatches": sorted(set(detailed_settlements) ^ set(mapped_settlements)),
        "priority_gaps": priorities,
    }


def analyze_unions() -> dict[str, Any]:
    unions = _load_yaml(DATA_DIR / "political_state.yaml")["unions"]
    field_counts = _field_counter(unions)
    member_counter = Counter()
    for union in unions:
        for member in union.get("members", []):
            for key in member.keys():
                member_counter[key] += 1

    currently_simulated = {
        "cohesion",
        "war_readiness",
        "dark_arts_level",
        "members",
        "seat",
        "overjarl",
        "overjarl_stats",
        "type",
    }
    member_simulated = {
        "settlement",
        "loyalty",
        "tribute_silver_weekly",
        "role",
    }

    missing_union_fields = sorted(set(field_counts.keys()) - currently_simulated)
    missing_member_fields = sorted(set(member_counter.keys()) - member_simulated)

    priorities = [
        (
            "in-kind tribute and levy extraction",
            "tribute_livestock_monthly / levy_fighters",
            "Union member data already carries livestock tribute and levy fighters, but no weekly or monthly extraction logic applies them.",
        ),
        (
            "intra-union trade modifiers",
            "trade_bonus",
            "Economic unions encode trade bonuses on members, but treasury and supply never use them.",
        ),
        (
            "covert network maintenance economics",
            "whisper_agents",
            "Agents exist for intelligence, but they do not consume silver, generate smuggling leverage, or alter market confidence.",
        ),
        (
            "practitioner upkeep and dark-arts cost curves",
            "dark_arts_practitioners",
            "The script handles dark-arts failures, but not recurring upkeep, scarcity, or recruitment economics for practitioners.",
        ),
    ]

    return {
        "union_count": len(unions),
        "missing_union_fields": missing_union_fields,
        "missing_member_fields": missing_member_fields,
        "priority_gaps": priorities,
    }


def analyze_wolfsheads() -> dict[str, Any]:
    bands = _load_yaml(DATA_DIR / "wolfshead_bands.yaml")["wolfshead_bands"]
    field_counts = _field_counter(bands)

    simulated = {
        "id",
        "name",
        "size",
        "leader",
        "named_members",
    }
    missing = sorted(set(field_counts.keys()) - simulated)

    priorities = [
        (
            "outlaw revenue model",
            "survival_strategy",
            "Wolfshead bands explicitly earn by toll-taking, escort work, poaching, smuggling, or raiding, but none of it feeds a faction economy.",
        ),
        (
            "territory control and route predation",
            "territory / camp_defenses",
            "Their camp locations and chokepoints should affect route risk, toll pressure, and caravan losses.",
        ),
        (
            "winter survival and family burden",
            "winter_strategy / origin_story",
            "Some bands have children, dependents, and seasonal labor strategies that should alter desperation and raid frequency.",
        ),
        (
            "mercenary-market competition",
            "relationship_to_mercenaries / disposition",
            "These bands compete with legal mercenaries for escort, smuggling, and intimidation work, but there is no contract-market pressure model.",
        ),
    ]

    return {
        "band_count": len(bands),
        "missing_fields": missing,
        "priority_gaps": priorities,
    }


def analyze_contract_market() -> dict[str, Any]:
    contracts = _load_yaml(DATA_DIR / "contracts" / "faction_contracts.yaml")["contracts"]
    factions = Counter(contract["faction"] for contract in contracts)
    priorities = [
        (
            "faction hiring budget depletion",
            "payment_silver / advance_silver",
            "Contract values exist, but faction treasuries do not go down when these offers appear or pay out.",
        ),
        (
            "seasonal contract demand spikes",
            "season / year_range / region",
            "The contract market is rich enough to affect regional labor prices, but demand is not fed back into economy or manpower.",
        ),
        (
            "supply destruction consequences",
            "grain-store burning / siege support contracts",
            "Contracts that attack granaries or hold passes should mutate settlement economy state directly.",
        ),
    ]
    return {
        "contract_count": len(contracts),
        "contracts_by_faction": dict(factions),
        "priority_gaps": priorities,
    }


def build_report() -> dict[str, Any]:
    settlements = analyze_settlements()
    unions = analyze_unions()
    wolfsheads = analyze_wolfsheads()
    contracts = analyze_contract_market()
    return {
        "settlements": settlements,
        "unions": unions,
        "wolfsheads": wolfsheads,
        "contracts": contracts,
        "top_recommendations": [
            "Simulate imports, exports, and route throughput before adding more war-economy events.",
            "Apply union tribute, levy, and trade bonuses as real weekly treasury and supply flows.",
            "Give wolfshead bands recurring revenue, upkeep, and territorial pressure so they behave like economic actors instead of static lore.",
            "Bind faction contract payouts and sabotage outcomes to settlement and union state changes.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Economy Simulation Gap Report",
        "",
        "## Summary",
        "",
        f"- Settlement profiles analyzed: {report['settlements']['source_count']}",
        f"- Political-state economies mapped: {report['settlements']['state_count']}",
        f"- Unions analyzed: {report['unions']['union_count']}",
        f"- Wolfshead bands analyzed: {report['wolfsheads']['band_count']}",
        f"- Faction contracts analyzed: {report['contracts']['contract_count']}",
        "",
        "## Highest-Priority Missing Simulation",
        "",
    ]
    for item in report["top_recommendations"]:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Settlement Economy Gaps",
            "",
            f"- Detailed-only fields not currently represented in the weekly state model: {', '.join(report['settlements']['detailed_only_fields'])}",
            f"- Settlement name mismatches between detailed and political-state data: {', '.join(report['settlements']['settlement_name_mismatches']) or 'none'}",
            "",
        ]
    )
    for title, field_name, detail in report["settlements"]["priority_gaps"]:
        lines.append(f"- `{title}` via `{field_name}`: {detail}")

    lines.extend(
        [
            "",
            "## Union and Faction Gaps",
            "",
            f"- Union fields present but not economically simulated: {', '.join(report['unions']['missing_union_fields'])}",
            f"- Union member fields present but not economically simulated: {', '.join(report['unions']['missing_member_fields'])}",
            "",
        ]
    )
    for title, field_name, detail in report["unions"]["priority_gaps"]:
        lines.append(f"- `{title}` via `{field_name}`: {detail}")

    lines.extend(
        [
            "",
            "## Wolfshead Band Gaps",
            "",
            f"- Wolfshead fields present but not economically simulated: {', '.join(report['wolfsheads']['missing_fields'])}",
            "",
        ]
    )
    for title, field_name, detail in report["wolfsheads"]["priority_gaps"]:
        lines.append(f"- `{title}` via `{field_name}`: {detail}")

    lines.extend(
        [
            "",
            "## Contract-Market Gaps",
            "",
            f"- Contracts by faction: {json.dumps(report['contracts']['contracts_by_faction'], ensure_ascii=False, sort_keys=True)}",
            "",
        ]
    )
    for title, field_name, detail in report["contracts"]["priority_gaps"]:
        lines.append(f"- `{title}` via `{field_name}`: {detail}")

    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit economy datasets for missing simulation coverage")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    parser.add_argument("--output", help="Write output to a file instead of stdout")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    report = build_report()
    rendered = json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_markdown(report)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
        return

    print(rendered)


if __name__ == "__main__":
    main()
