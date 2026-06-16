from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ..state_paths import DATA_DIR


SETTLEMENTS_PATH = DATA_DIR / "settlements.yaml"
YEAR_LENGTH = 360


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


@lru_cache(maxsize=1)
def known_settlements() -> set[str]:
    payload = load_yaml(SETTLEMENTS_PATH)
    return {
        str(item.get("name"))
        for item in payload.get("settlements", [])
        if isinstance(item, dict) and item.get("name")
    }


def display_day(year: int, day: int) -> str:
    return f"D{day} Y{year}"


def ordinal_day(year: int, day: int) -> int:
    return (year * YEAR_LENGTH) + (day - 1)


def year_day_from_ordinal(value: int) -> tuple[int, int]:
    year = value // YEAR_LENGTH
    day = (value % YEAR_LENGTH) + 1
    return year, day


def span_overlaps_year(
    start_year: int,
    start_day: int,
    end_year: int,
    end_day: int,
    year: int,
) -> bool:
    span_start = ordinal_day(start_year, start_day)
    span_end = ordinal_day(end_year, end_day)
    year_start = ordinal_day(year, 1)
    year_end = ordinal_day(year, YEAR_LENGTH)
    return not (span_end < year_start or span_start > year_end)


def span_contains_day(
    start_year: int,
    start_day: int,
    end_year: int,
    end_day: int,
    year: int,
    day: int,
) -> bool:
    target = ordinal_day(year, day)
    span_start = ordinal_day(start_year, start_day)
    span_end = ordinal_day(end_year, end_day)
    return span_start <= target <= span_end


def iter_span_days(
    start_year: int,
    start_day: int,
    end_year: int,
    end_day: int,
) -> list[tuple[int, int]]:
    span_start = ordinal_day(start_year, start_day)
    span_end = ordinal_day(end_year, end_day)
    return [year_day_from_ordinal(value) for value in range(span_start, span_end + 1)]


def prettify_name(raw: Any) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    if text in known_settlements():
        return text
    lowered = text.lower()
    for prefix in ("settlement_", "band_", "union_", "location_", "route_"):
        if lowered.startswith(prefix):
            text = text[len(prefix) :]
            break
    text = text.replace("_", " ").replace("-", " ")
    return " ".join(part.capitalize() for part in text.split())


def is_secondary_tag(label: str) -> bool:
    if not label:
        return False
    if label in known_settlements():
        return True
    lowered = label.casefold()
    band_markers = ("band", "axes", "merc", "company", "wolves", "remnant")
    return any(marker in lowered for marker in band_markers)


def metric_line(name: str, value: Any) -> str:
    label = " ".join(part.capitalize() for part in str(name).split("_"))
    return f"{label}: {value}"
