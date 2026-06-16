from __future__ import annotations

from ..models import FeedPost
from ..state_paths import DATA_DIR
from .common import display_day, load_yaml, prettify_name


CANON_EVENTS_PATH = DATA_DIR / "events" / "y314_y315_events.yaml"


def build_canon_event_posts() -> list[FeedPost]:
    payload = load_yaml(CANON_EVENTS_PATH)
    posts: list[FeedPost] = []
    for event in payload.get("events", []) or []:
        year = int(event.get("year", 0) or 0)
        day = int(event.get("day", 0) or 0)
        entities: list[str] = []
        if event.get("location"):
            entities.append(prettify_name(event.get("location")))
        entities.extend(prettify_name(item) for item in event.get("actors", []) or [])
        entities.extend(prettify_name(item) for item in event.get("factions", []) or [])
        entities = [item for item in entities if item]
        summary = str(event.get("summary", "")).strip()
        category = str(event.get("category", "Event") or "Event").replace("_", " ").title()
        narrative = [summary]
        technical: list[str] = []
        prerequisites = [str(item) for item in event.get("prerequisites", []) or []]
        if prerequisites:
            technical.append("Preconditions:")
            technical.extend(prerequisites)
        chain = str(event.get("chain", "")).strip()
        if chain:
            technical.append(f"Chain: {chain}")
        posts.append(
            FeedPost(
                id=str(event.get("id")),
                source_type="canon_event",
                simulated_year=year,
                simulated_day=day,
                simulated_label=display_day(year, day),
                cadence="day",
                span_start_year=year,
                span_start_day=day,
                span_end_year=year,
                span_end_day=day,
                title=str(event.get("title", "World Event")),
                category=category,
                tags=[
                    "canon",
                    str(event.get("category", "Event") or "Event"),
                    "band-relevant" if bool(event.get("band_relevant")) else "world",
                ],
                entities=entities,
                summary=summary,
                narrative=narrative,
                technical=technical,
                provenance="data/events/y314_y315_events.yaml",
            )
        )
    return posts
