from __future__ import annotations

import json
from typing import Any

from ..models import FeedPost
from ..state_paths import TRANSACTIONS_DIR
from .common import (
    display_day,
    is_secondary_tag,
    metric_line,
    ordinal_day,
    prettify_name,
    year_day_from_ordinal,
)


def _transaction_span(transaction: dict[str, Any]) -> tuple[tuple[int, int], tuple[int, int], str]:
    from_cursor = transaction.get("from_cursor", {}) or {}
    to_cursor = transaction.get("to_cursor", {}) or {}
    unit = str(transaction.get("unit", "day") or "day")
    from_year = int(from_cursor.get("year", 0) or 0)
    from_day = int(from_cursor.get("day_of_year", 0) or 0)
    to_year = int(to_cursor.get("year", 0) or 0)
    to_day = int(to_cursor.get("day_of_year", 0) or 0)
    to_ordinal = ordinal_day(to_year, to_day)
    if unit == "day":
        start_ordinal = to_ordinal
    else:
        start_ordinal = ordinal_day(from_year, from_day) + 1
    start_year, start_day = year_day_from_ordinal(start_ordinal)
    end_year, end_day = year_day_from_ordinal(to_ordinal)
    cadence = unit if unit in {"day", "week", "month", "season"} else "day"
    return (start_year, start_day), (end_year, end_day), cadence


def _span_fields(transaction: dict[str, Any]) -> dict[str, int | str]:
    (start_year, start_day), (end_year, end_day), cadence = _transaction_span(transaction)
    return {
        "cadence": cadence,
        "span_start_year": start_year,
        "span_start_day": start_day,
        "span_end_year": end_year,
        "span_end_day": end_day,
    }


def _build_settlement_probe_post(transaction: dict[str, Any], probe: dict[str, Any]) -> FeedPost:
    payload = probe.get("payload", {}) or {}
    year = int(transaction.get("to_cursor", {}).get("year", 0) or 0)
    day = int(transaction.get("to_cursor", {}).get("day_of_year", 0) or 0)
    title = "Settlement Chronicle"
    summary = str(payload.get("summary", "")).strip() or "Settlement pressures shifted during the latest step."
    metrics = payload.get("metrics", {}) or {}
    affected = [
        prettify_name(item)
        for item in payload.get("affected_entities", []) or []
        if prettify_name(item) and is_secondary_tag(prettify_name(item))
    ]
    narrative = [summary]
    technical: list[str] = []
    if affected:
        narrative.append(f"Affected settlements and bands: {', '.join(affected)}.")
    if metrics:
        technical.append("Pressure ledger:")
        technical.extend(metric_line(name, value) for name, value in metrics.items())
    warnings = [str(item) for item in payload.get("warnings", []) or []]
    if warnings:
        technical.append("Warnings:")
        technical.extend(warnings)
    return FeedPost(
        id=f"{transaction['transaction_id']}::settlement_stack",
        source_type="settlement_stack",
        simulated_year=year,
        simulated_day=day,
        simulated_label=display_day(year, day),
        **_span_fields(transaction),
        title=title,
        category="Settlements",
        tags=["settlement_stack", str(transaction.get("unit", "step")), "generated"],
        entities=affected,
        summary=summary,
        narrative=narrative,
        technical=technical,
        provenance=str(transaction.get("transaction_id")),
    )


def _build_animal_probe_post(transaction: dict[str, Any], probe: dict[str, Any]) -> FeedPost:
    payload = probe.get("payload", {}) or {}
    year = int(transaction.get("to_cursor", {}).get("year", 0) or 0)
    day = int(transaction.get("to_cursor", {}).get("day_of_year", 0) or 0)
    summary = str(payload.get("summary", "")).strip() or "Herd and kennel seasonal changes were recorded."
    metrics = payload.get("metrics", {}) or {}
    draw_journal = payload.get("draw_journal", {}) or {}
    affected = [prettify_name(item) for item in payload.get("affected_entities", []) or [] if prettify_name(item)]
    narrative = [summary]
    technical: list[str] = []
    if affected:
        narrative.append(f"Herds and kennels touched: {', '.join(affected)}.")
    if metrics:
        technical.append("Season ledger:")
        technical.extend(metric_line(name, value) for name, value in metrics.items())
    if draw_journal:
        technical.append(
            f"Recorded draw journal with {draw_journal.get('total_draws', 0)} draw(s)."
        )
    return FeedPost(
        id=f"{transaction['transaction_id']}::animal_breeding",
        source_type="animal_breeding",
        simulated_year=year,
        simulated_day=day,
        simulated_label=display_day(year, day),
        **_span_fields(transaction),
        title="Herd And Kennel Chronicle",
        category="Animals",
        tags=["animal_breeding", str(transaction.get("unit", "step")), "generated"],
        entities=affected,
        summary=summary,
        narrative=narrative,
        technical=technical,
        provenance=str(transaction.get("transaction_id")),
    )


def _build_generic_probe_post(transaction: dict[str, Any], probe: dict[str, Any]) -> FeedPost:
    payload = probe.get("payload", {}) or {}
    key = str(payload.get("key", probe.get("key", "simulation")))
    year = int(transaction.get("to_cursor", {}).get("year", 0) or 0)
    day = int(transaction.get("to_cursor", {}).get("day_of_year", 0) or 0)
    summary = str(payload.get("summary", "")).strip() or "Simulation step recorded."
    metrics = payload.get("metrics", {}) or {}
    affected = [prettify_name(item) for item in payload.get("affected_entities", []) or [] if prettify_name(item)]
    narrative = [summary]
    technical: list[str] = []
    if affected:
        narrative.append(f"Touched places and groups: {', '.join(affected)}.")
    if metrics:
        technical.append("Ledger signals:")
        technical.extend(metric_line(name, value) for name, value in metrics.items())
    return FeedPost(
        id=f"{transaction['transaction_id']}::{key}",
        source_type=key,
        simulated_year=year,
        simulated_day=day,
        simulated_label=display_day(year, day),
        **_span_fields(transaction),
        title="Simulation Chronicle",
        category="Simulation",
        tags=[key, str(transaction.get("unit", "step")), "generated"],
        entities=affected,
        summary=summary,
        narrative=narrative,
        technical=technical,
        provenance=str(transaction.get("transaction_id")),
    )


def build_transaction_posts() -> list[FeedPost]:
    if not TRANSACTIONS_DIR.exists():
        return []

    posts: list[FeedPost] = []
    for path in sorted(TRANSACTIONS_DIR.glob("*.json"), reverse=True):
        transaction = json.loads(path.read_text(encoding="utf-8"))
        to_cursor = transaction.get("to_cursor", {}) or {}
        year = int(to_cursor.get("year", 0) or 0)
        day = int(to_cursor.get("day_of_year", 0) or 0)
        transaction_id = str(transaction.get("transaction_id", path.stem))
        unit = str(transaction.get("unit", "step"))
        amount = int(transaction.get("amount", 0) or 0)
        summary = (
            f"The world clock advanced by {amount} {unit}(s) and committed a "
            "new reversible transaction."
        )
        posts.append(
            FeedPost(
                id=f"{transaction_id}::clock",
                source_type="transaction",
                simulated_year=year,
                simulated_day=day,
                simulated_label=display_day(year, day),
                **_span_fields(transaction),
                title=f"World Clock Ledger — {amount} {unit}(s) committed",
                category="Timekeeping",
                tags=["transaction", unit],
                entities=[],
                summary=summary,
                narrative=[
                    summary,
                    (
                        f"Recorded move: Y{transaction.get('from_cursor', {}).get('year')} "
                        f"day {transaction.get('from_cursor', {}).get('day_of_year')} to "
                        f"Y{year} day {day}."
                    ),
                ],
                technical=[
                    (
                        f"Master seed {transaction.get('seed_journal', {}).get('master_seed')} "
                        "anchors replay for this movement."
                    )
                ],
                provenance=transaction_id,
            )
        )
        for probe in transaction.get("replay_probes", []) or []:
            payload = probe.get("payload", {}) or {}
            key = str(payload.get("key", probe.get("key", "simulation")))
            if key == "settlement_stack":
                posts.append(_build_settlement_probe_post(transaction, probe))
            elif key == "animal_breeding":
                posts.append(_build_animal_probe_post(transaction, probe))
            else:
                posts.append(_build_generic_probe_post(transaction, probe))
    return posts
