from __future__ import annotations

import json

from .models import NarrativeBlock, TransactionNarrativeResponse
from .state_paths import TRANSACTIONS_DIR


def _load_transaction(transaction_id: str) -> dict:
    path = TRANSACTIONS_DIR / f"{transaction_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def build_transaction_narrative(transaction_id: str) -> TransactionNarrativeResponse:
    transaction = _load_transaction(transaction_id)
    unit = str(transaction.get("unit"))
    amount = int(transaction.get("amount", 0))
    from_cursor = transaction.get("from_cursor", {})
    to_cursor = transaction.get("to_cursor", {})
    replay_probes = transaction.get("replay_probes") or []

    operator_summary = [
        (
            f"Advanced {amount} {unit}(s) from "
            f"Y{from_cursor.get('year')} D{from_cursor.get('day_of_year')} to "
            f"Y{to_cursor.get('year')} D{to_cursor.get('day_of_year')}."
        ),
        (
            f"Deterministic master seed {transaction.get('seed_journal', {}).get('master_seed')} "
            f"anchored replay for {len(replay_probes)} deterministic adapter probe(s)."
        ),
    ]

    writer_summary = [
        (
            f"World time moved forward by {amount} {unit}(s), shifting pressures and "
            "seasonal processes across the Rimevegr."
        )
    ]

    blocks: list[NarrativeBlock] = [
        NarrativeBlock(title="Clock Move", lines=operator_summary),
    ]

    for probe in replay_probes:
        payload = probe.get("payload", {})
        key = str(payload.get("key", "unknown"))
        summary = str(payload.get("summary", ""))
        metrics = payload.get("metrics", {}) or {}
        affected = payload.get("affected_entities", []) or []
        metric_lines = [f"{name}: {value}" for name, value in metrics.items()]
        affected_line = (
            f"Affected entities: {', '.join(str(item) for item in affected)}"
            if affected
            else "Affected entities: none surfaced"
        )
        blocks.append(
            NarrativeBlock(
                title=f"Deterministic Probe — {key}",
                lines=[summary, affected_line, *metric_lines],
            )
        )
        writer_summary.append(summary)

    return TransactionNarrativeResponse(
        transaction_id=transaction_id,
        operator_summary=operator_summary,
        writer_summary=writer_summary,
        blocks=blocks,
    )
