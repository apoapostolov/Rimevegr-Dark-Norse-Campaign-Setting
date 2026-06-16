from __future__ import annotations

import json
from pathlib import Path

from .models import PeriodExportResponse, TransactionExportResponse
from .narrative_engine import build_transaction_narrative
from .state_paths import EXPORTS_DIR
from .time_engine import load_timeline_state


def _markdown_for_narrative(transaction_id: str) -> str:
    narrative = build_transaction_narrative(transaction_id)
    lines: list[str] = [
        f"# Transaction Export — {transaction_id}",
        "",
        "## Operator Summary",
        "",
    ]
    lines.extend(f"- {line}" for line in narrative.operator_summary)
    lines.extend(["", "## Writer Summary", ""])
    lines.extend(f"- {line}" for line in narrative.writer_summary)
    for block in narrative.blocks:
        lines.extend(["", f"## {block.title}", ""])
        lines.extend(f"- {line}" for line in block.lines)
    lines.append("")
    return "\n".join(lines)


def export_transaction_bundle(transaction_id: str) -> TransactionExportResponse:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    narrative = build_transaction_narrative(transaction_id)

    json_path = EXPORTS_DIR / f"{transaction_id}.json"
    markdown_path = EXPORTS_DIR / f"{transaction_id}.md"

    json_path.write_text(
        json.dumps(narrative.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    markdown_path.write_text(_markdown_for_narrative(transaction_id), encoding="utf-8")

    return TransactionExportResponse(
        transaction_id=transaction_id,
        json_path=str(json_path),
        markdown_path=str(markdown_path),
    )


def _period_markdown(transaction_ids: list[str]) -> str:
    lines = ["# Period Export", ""]
    for transaction_id in transaction_ids:
        narrative = build_transaction_narrative(transaction_id)
        lines.extend([f"## {transaction_id}", ""])
        lines.extend(f"- {line}" for line in narrative.writer_summary)
        lines.append("")
    return "\n".join(lines)


def export_period_bundle(count: int = 3) -> PeriodExportResponse:
    timeline = load_timeline_state()
    history = list(timeline.get("history", []))
    transaction_ids = history[-count:] if count > 0 else history
    narratives = [build_transaction_narrative(transaction_id) for transaction_id in transaction_ids]

    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"period_latest_{len(transaction_ids)}"
    json_path = EXPORTS_DIR / f"{stem}.json"
    markdown_path = EXPORTS_DIR / f"{stem}.md"

    json_payload = {
        "transaction_ids": transaction_ids,
        "operator_summaries": [
            {
                "transaction_id": narrative.transaction_id,
                "operator_summary": narrative.operator_summary,
                "writer_summary": narrative.writer_summary,
            }
            for narrative in narratives
        ],
    }
    json_path.write_text(
        json.dumps(json_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    markdown_path.write_text(_period_markdown(transaction_ids), encoding="utf-8")

    return PeriodExportResponse(
        transaction_ids=transaction_ids,
        json_path=str(json_path),
        markdown_path=str(markdown_path),
    )
