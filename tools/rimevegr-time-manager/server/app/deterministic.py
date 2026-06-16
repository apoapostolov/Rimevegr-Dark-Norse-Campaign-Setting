from __future__ import annotations

import json
import hashlib

from .models import TimelineCursor


def _stable_seed(*parts: object) -> int:
    joined = "|".join(str(part) for part in parts)
    digest = hashlib.sha256(joined.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def build_seed_journal(
    cursor: TimelineCursor,
    *,
    unit: str,
    amount: int,
    transaction_id: str,
    adapter_keys: list[str],
) -> dict[str, object]:
    master_seed = _stable_seed(
        cursor.branch,
        cursor.year,
        cursor.day_of_year,
        unit,
        amount,
        transaction_id,
    )
    return {
        "master_seed": master_seed,
        "transaction_anchor": (
            f"{cursor.branch}:Y{cursor.year}:D{cursor.day_of_year}:{unit}:{amount}"
        ),
        "adapter_seeds": {
            key: _stable_seed(master_seed, key, index)
            for index, key in enumerate(adapter_keys)
        },
    }


def build_replay_signature(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
