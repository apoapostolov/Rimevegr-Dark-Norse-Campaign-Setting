from __future__ import annotations

from typing import Any

from ..models import FeedPost
from ..state_paths import DATA_DIR
from ..time_engine import current_cursor
from .common import display_day, load_yaml


SETTLEMENTS_PATH = DATA_DIR / "settlements.yaml"


def _flatten_count_map(section: dict[str, Any] | None) -> list[str]:
    if not isinstance(section, dict):
        return []
    lines: list[str] = []
    for key, value in section.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                lines.append(f"{key.replace('_', ' ').title()} - {subkey.replace('_', ' ').title()}: {subvalue}")
        else:
            lines.append(f"{key.replace('_', ' ').title()}: {value}")
    return lines


def build_settlement_posts() -> list[FeedPost]:
    payload = load_yaml(SETTLEMENTS_PATH)
    cursor = current_cursor()
    simulated_year = cursor.year
    simulated_day = cursor.day_of_year
    posts: list[FeedPost] = []
    for settlement in payload.get("settlements", []) or []:
        if not isinstance(settlement, dict):
            continue
        name = str(settlement.get("name", "")).strip()
        if not name:
            continue
        structures = settlement.get("structures", {}) or {}
        services = [str(item) for item in settlement.get("services", []) or []]
        economy = settlement.get("economy", {}) or {}
        defenses = settlement.get("defenses", {}) or {}
        narrative = [f"Settlement profile for {name}."]
        technical = [
            f"Size: {settlement.get('size', 'unknown')}",
            f"Terrain: {settlement.get('terrain', 'unknown')}",
            f"Population: {settlement.get('population', 'unknown')}",
        ]
        leader = str(settlement.get("leader", "")).strip()
        if leader:
            narrative.append(f"Leader: {leader}")
        defense_line = str(settlement.get("defense", "")).strip()
        if defense_line:
            narrative.append(f"Headline defense: {defense_line}")
        if services:
            technical.append(f"Services: {', '.join(services)}")
        structure_lines = _flatten_count_map(structures)
        if structure_lines:
            technical.append("Structure ledger:")
            technical.extend(structure_lines)
        defense_lines = _flatten_count_map(defenses)
        if defense_lines:
            technical.append("Defensive works:")
            technical.extend(defense_lines)
        economy_line = str(economy.get("main_trade", "")).strip()
        if economy_line:
            narrative.append(f"Main trade: {economy_line}")
        income = str(economy.get("weekly_income_silver", "")).strip()
        if income:
            technical.append(f"Weekly income band: {income} silver")
        stores = str(economy.get("food_stores_days", "")).strip()
        if stores:
            technical.append(f"Food stores: {stores} days")
        damage = settlement.get("damage_state", {}) or {}
        if isinstance(damage, dict):
            overall = str(damage.get("overall", "")).strip()
            if overall:
                technical.append(f"Damage state: {overall}")
            damaged_elements = [str(item) for item in damage.get("damaged_elements", []) or [] if str(item).strip()]
            if damaged_elements:
                technical.append(f"Damaged elements: {', '.join(damaged_elements)}")
        notes = str(settlement.get("notes", "")).strip()
        if notes:
            narrative.append(notes)
        posts.append(
            FeedPost(
                id=f"settlement::{name}",
                source_type="settlement_profile",
                simulated_year=simulated_year,
                simulated_day=simulated_day,
                simulated_label=display_day(simulated_year, simulated_day),
                cadence="day",
                span_start_year=simulated_year,
                span_start_day=simulated_day,
                span_end_year=simulated_year,
                span_end_day=simulated_day,
                title=f"{name} Dossier",
                category="Settlements",
                tags=[
                    "settlement_profile",
                    str(settlement.get("size", "unknown")),
                    str(settlement.get("terrain", "unknown")),
                ],
                entities=[name],
                summary=(
                    f"{name} is a {settlement.get('size', 'unknown')} settlement on "
                    f"{settlement.get('terrain', 'unknown')} ground."
                ),
                narrative=narrative,
                technical=technical,
                provenance="data/settlements.yaml",
            )
        )
    return posts
