from __future__ import annotations

from collections import Counter

from .content_sources import (
    build_canon_event_posts,
    build_transaction_posts,
    build_settlement_posts,
    build_weather_posts,
)
from .content_sources.common import iter_span_days, is_secondary_tag, span_contains_day, span_overlaps_year
from .models import FeedDateFacet, FeedFacetItem, FeedFacetsResponse, FeedPost, FeedResponse


def _all_posts() -> list[FeedPost]:
    posts = [
        *build_transaction_posts(),
        *build_settlement_posts(),
        *build_weather_posts(),
        *build_canon_event_posts(),
    ]
    return sorted(
        posts,
        key=lambda item: (item.simulated_year, item.simulated_day, item.id),
        reverse=True,
    )


def _post_span(post: FeedPost) -> tuple[int, int, int, int]:
    start_year = post.span_start_year if post.span_start_year is not None else post.simulated_year
    start_day = post.span_start_day if post.span_start_day is not None else post.simulated_day
    end_year = post.span_end_year if post.span_end_year is not None else post.simulated_year
    end_day = post.span_end_day if post.span_end_day is not None else post.simulated_day
    return start_year, start_day, end_year, end_day


def _post_applies_to_year(post: FeedPost, year: int) -> bool:
    start_year, start_day, end_year, end_day = _post_span(post)
    return span_overlaps_year(start_year, start_day, end_year, end_day, year)


def _post_applies_to_day(post: FeedPost, year: int, day: int) -> bool:
    start_year, start_day, end_year, end_day = _post_span(post)
    return span_contains_day(start_year, start_day, end_year, end_day, year, day)


def get_feed(
    *,
    year: int | None = None,
    day: int | None = None,
    categories: list[str] | None = None,
    entities: list[str] | None = None,
    limit: int = 80,
) -> FeedResponse:
    category_set = {item.casefold() for item in categories or [] if item}
    entity_set = {item.casefold() for item in entities or [] if item}
    items: list[FeedPost] = []
    for post in _all_posts():
        if year is not None and not _post_applies_to_year(post, year):
            continue
        if day is not None and not _post_applies_to_day(post, year or post.simulated_year, day):
            continue
        if category_set and post.category.casefold() not in category_set:
            continue
        if entity_set and not any(entity.casefold() in entity_set for entity in post.entities):
            continue
        items.append(post)
        if len(items) >= limit:
            break
    return FeedResponse(items=items)


def get_feed_facets() -> FeedFacetsResponse:
    posts = _all_posts()
    date_counts = Counter(
        (year, day)
        for post in posts
        for year, day in iter_span_days(*_post_span(post))
    )
    category_counts = Counter(post.category for post in posts)
    entity_counts = Counter(entity for post in posts for entity in post.entities if is_secondary_tag(entity))
    return FeedFacetsResponse(
        dates=[
            FeedDateFacet(
                year=year,
                day=day,
                label=f"D{day} Y{year}",
                count=count,
            )
            for (year, day), count in sorted(date_counts.items(), reverse=True)
        ],
        categories=[
            FeedFacetItem(label=label, count=count)
            for label, count in category_counts.most_common()
        ],
        entities=[
            FeedFacetItem(label=label, count=count)
            for label, count in entity_counts.most_common(24)
        ],
    )
