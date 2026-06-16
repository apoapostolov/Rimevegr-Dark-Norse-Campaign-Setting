from __future__ import annotations

from typing import Any

from ..models import FeedPost
from ..state_paths import DATA_DIR
from .common import display_day, load_yaml


WEATHER_EVENTS_PATH = DATA_DIR / "weather" / "named_events.yaml"


def build_weather_posts() -> list[FeedPost]:
    payload = load_yaml(WEATHER_EVENTS_PATH)
    posts: list[FeedPost] = []
    for event in payload.get("named_events", []) or []:
        year = int(event.get("year", 0) or 0)
        day = int(event.get("start_day", 0) or 0)
        settlements = [str(item) for item in event.get("affected_settlements", []) or []]
        narrative = [str(event.get("description", "")).strip()]
        consequences = [str(item) for item in event.get("narrative_consequences", []) or []]
        if consequences:
            narrative.append("What people remember:")
            narrative.extend(consequences)
        effects = event.get("mechanical_effects", {}) or {}
        technical = [
            f"{name.replace('_', ' ').capitalize()}: {value}"
            for name, value in effects.items()
            if name != "special"
        ]
        if technical:
            technical.insert(0, "Weather effects:")
        special = str(effects.get("special", "")).strip()
        if special:
            technical.append(f"Special note: {special}")
        folk_origin = str(event.get("folk_name_origin", "")).strip()
        if folk_origin:
            narrative.append(folk_origin)
        posts.append(
            FeedPost(
                id=str(event.get("id")),
                source_type="weather",
                simulated_year=year,
                simulated_day=day,
                simulated_label=display_day(year, day),
                cadence="day",
                span_start_year=year,
                span_start_day=day,
                span_end_year=year,
                span_end_day=day,
                title=str(event.get("name", "Weather Event")),
                category="Weather",
                tags=[
                    "weather",
                    str(event.get("severity", "")),
                    str(event.get("weather_type", "")),
                ],
                entities=settlements,
                summary=str(event.get("description", "")).strip(),
                narrative=narrative,
                technical=technical,
                provenance="data/weather/named_events.yaml",
            )
        )
    return posts
