from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from .adapter_registry import build_replay_probe_payloads, built_in_adapters
from .deterministic import build_replay_signature, build_seed_journal
from .models import (
    RecentTransactionItem,
    RecentTransactionsResponse,
    TimeTransactionResponse,
    TimelineCursor,
    UndoRedoResponse,
)
from .state_paths import SNAPSHOTS_DIR, STATE_DIR, TRANSACTIONS_DIR


TIMELINE_PATH = STATE_DIR / "timeline.json"
SEASON_RANGES = [
    (1, 60, "Long Summer"),
    (61, 150, "Early Dark"),
    (151, 300, "Deep Dark"),
    (301, 360, "Late Dark"),
]
UNIT_TO_DAYS = {"day": 1, "week": 7, "month": 30, "season": 90}


def _season_for_day(day_of_year: int) -> str:
    for start, end, label in SEASON_RANGES:
        if start <= day_of_year <= end:
            return label
    return "Late Dark"


def ensure_timeline_file() -> None:
    if TIMELINE_PATH.exists():
        return
    TIMELINE_PATH.write_text(
        json.dumps(
            {
                "cursor": {
                    "year": 312,
                    "day_of_year": 1,
                    "season": _season_for_day(1),
                    "branch": "mainline",
                    "transaction_index": 0,
                },
                "history": [],
                "redo_stack": [],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def load_timeline_state() -> dict[str, Any]:
    ensure_timeline_file()
    return json.loads(TIMELINE_PATH.read_text(encoding="utf-8"))


def save_timeline_state(data: dict[str, Any]) -> None:
    TIMELINE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def current_cursor() -> TimelineCursor:
    state = load_timeline_state()
    return TimelineCursor(**state["cursor"])


def _advance_cursor(cursor: TimelineCursor, unit: str, amount: int) -> TimelineCursor:
    days = UNIT_TO_DAYS[unit] * amount
    year = cursor.year
    day = cursor.day_of_year + days
    while day > 360:
        day -= 360
        year += 1
    while day < 1:
        day += 360
        year -= 1
    return TimelineCursor(
        year=year,
        day_of_year=day,
        season=_season_for_day(day),
        branch=cursor.branch,
        transaction_index=cursor.transaction_index + (1 if amount > 0 else -1),
    )


def _timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _write_snapshot(transaction_id: str, payload: dict[str, Any]) -> Path:
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOTS_DIR / f"{transaction_id}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _write_transaction(transaction_id: str, payload: dict[str, Any]) -> Path:
    TRANSACTIONS_DIR.mkdir(parents=True, exist_ok=True)
    path = TRANSACTIONS_DIR / f"{transaction_id}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _build_replay_probes(
    from_cursor: TimelineCursor,
    *,
    unit: str,
    amount: int,
    adapter_seeds: dict[str, int],
) -> list[dict[str, Any]]:
    payloads = build_replay_probe_payloads(
        from_cursor,
        unit,
        amount,
        adapter_seeds=adapter_seeds,
    )
    probes: list[dict[str, Any]] = []
    for probe_payload in payloads:
        probes.append(
            {
                "key": str(probe_payload["key"]),
                "signature": build_replay_signature(probe_payload),
                "payload": probe_payload,
            }
        )
    return probes


def _replay_probe_mismatch(transaction: dict[str, Any]) -> str | None:
    seed_journal = transaction.get("seed_journal") or {}
    adapter_seeds = {
        str(key): int(value)
        for key, value in dict(seed_journal.get("adapter_seeds") or {}).items()
    }
    expected_probes = transaction.get("replay_probes") or []
    if not expected_probes:
        return None

    from_cursor = TimelineCursor(**transaction["from_cursor"])
    fresh_probes = _build_replay_probes(
        from_cursor,
        unit=str(transaction["unit"]),
        amount=int(transaction["amount"]),
        adapter_seeds=adapter_seeds,
    )
    fresh_map = {probe["key"]: probe["signature"] for probe in fresh_probes}
    for probe in expected_probes:
        key = str(probe.get("key"))
        expected_signature = str(probe.get("signature"))
        if fresh_map.get(key) != expected_signature:
            return (
                f"Replay probe mismatch for adapter '{key}'. Current deterministic "
                "state no longer matches the recorded redo assumptions."
            )
    return None


def advance_time(unit: str, amount: int = 1, dry_run: bool = True) -> TimeTransactionResponse:
    if unit not in UNIT_TO_DAYS:
        raise ValueError(f"Unsupported unit: {unit}")

    timeline = load_timeline_state()
    from_cursor = TimelineCursor(**timeline["cursor"])
    to_cursor = _advance_cursor(from_cursor, unit, amount)
    transaction_id = f"txn_{_timestamp_slug()}_{unit}_{amount:+d}".replace("+", "p").replace("-", "m")

    adapter_keys = [adapter.key for adapter in built_in_adapters() if unit in adapter.granularities]
    seed_journal = build_seed_journal(
        from_cursor,
        unit=unit,
        amount=amount,
        transaction_id=transaction_id,
        adapter_keys=adapter_keys,
    )

    snapshot_payload = {
        "transaction_id": transaction_id,
        "cursor": from_cursor.model_dump(),
        "timeline_state": timeline,
    }
    transaction_payload = {
        "transaction_id": transaction_id,
        "branch": from_cursor.branch,
        "unit": unit,
        "amount": amount,
        "seed_journal": seed_journal,
        "replay_probes": _build_replay_probes(
            from_cursor,
            unit=unit,
            amount=amount,
            adapter_seeds={
                str(key): int(value)
                for key, value in dict(seed_journal["adapter_seeds"]).items()
            },
        ),
        "from_cursor": from_cursor.model_dump(),
        "to_cursor": to_cursor.model_dump(),
        "inverse": {"unit": unit, "amount": -amount},
        "patches": [],
        "notes": (
            "Cursor transaction with deterministic seed journal scaffolded "
            "for replay-safe adapter execution."
        ),
    }

    snapshot_path: str | None = None
    transaction_path: str | None = None
    if not dry_run:
        snapshot_path = str(_write_snapshot(transaction_id, snapshot_payload))
        transaction_path = str(_write_transaction(transaction_id, transaction_payload))
        timeline["cursor"] = to_cursor.model_dump()
        timeline.setdefault("history", []).append(transaction_id)
        timeline["redo_stack"] = []
        save_timeline_state(timeline)

    return TimeTransactionResponse(
        dry_run=dry_run,
        transaction_id=transaction_id,
        branch=from_cursor.branch,
        unit=unit,
        amount=amount,
        seed=int(seed_journal["master_seed"]),
        adapter_seeds={
            str(key): int(value)
            for key, value in dict(seed_journal["adapter_seeds"]).items()
        },
        from_cursor=from_cursor,
        to_cursor=to_cursor,
        inverse_unit=unit,
        inverse_amount=-amount,
        snapshot_path=snapshot_path,
        transaction_path=transaction_path,
    )


def _load_transaction(transaction_id: str) -> dict[str, Any]:
    path = TRANSACTIONS_DIR / f"{transaction_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def recent_transactions(count: int = 5) -> RecentTransactionsResponse:
    timeline = load_timeline_state()
    history = list(timeline.get("history", []))[-count:]
    items: list[RecentTransactionItem] = []
    for transaction_id in reversed(history):
        transaction = _load_transaction(transaction_id)
        from_cursor = transaction.get("from_cursor", {})
        to_cursor = transaction.get("to_cursor", {})
        items.append(
            RecentTransactionItem(
                transaction_id=transaction_id,
                unit=str(transaction.get("unit", "?")),
                amount=int(transaction.get("amount", 0)),
                from_label=f"Y{from_cursor.get('year')} D{from_cursor.get('day_of_year')}",
                to_label=f"Y{to_cursor.get('year')} D{to_cursor.get('day_of_year')}",
                note=str(transaction.get("notes", "")) or None,
            )
        )
    return RecentTransactionsResponse(items=items)


def undo_last(dry_run: bool = True) -> UndoRedoResponse:
    timeline = load_timeline_state()
    history = timeline.get("history", [])
    if not history:
        return UndoRedoResponse(action="undo", dry_run=dry_run, transaction_id=None, cursor=TimelineCursor(**timeline["cursor"]))

    transaction_id = history[-1]
    transaction = _load_transaction(transaction_id)
    cursor = TimelineCursor(**transaction["from_cursor"])
    if not dry_run:
        timeline["cursor"] = cursor.model_dump()
        timeline["history"] = history[:-1]
        timeline.setdefault("redo_stack", []).append(transaction_id)
        save_timeline_state(timeline)
    return UndoRedoResponse(action="undo", dry_run=dry_run, transaction_id=transaction_id, cursor=cursor)


def redo_last(dry_run: bool = True) -> UndoRedoResponse:
    timeline = load_timeline_state()
    redo_stack = timeline.get("redo_stack", [])
    if not redo_stack:
        return UndoRedoResponse(
            action="redo",
            dry_run=dry_run,
            transaction_id=None,
            cursor=TimelineCursor(**timeline["cursor"]),
        )

    transaction_id = redo_stack[-1]
    transaction = _load_transaction(transaction_id)
    blocked_reason = _replay_probe_mismatch(transaction)
    if blocked_reason is not None:
        return UndoRedoResponse(
            action="redo",
            dry_run=dry_run,
            transaction_id=transaction_id,
            cursor=TimelineCursor(**timeline["cursor"]),
            blocked_reason=blocked_reason,
        )
    cursor = TimelineCursor(**transaction["to_cursor"])
    if not dry_run:
        timeline["cursor"] = cursor.model_dump()
        timeline.setdefault("history", []).append(transaction_id)
        timeline["redo_stack"] = redo_stack[:-1]
        save_timeline_state(timeline)
    return UndoRedoResponse(
        action="redo",
        dry_run=dry_run,
        transaction_id=transaction_id,
        cursor=cursor,
    )
