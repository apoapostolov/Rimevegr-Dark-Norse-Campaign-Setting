from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .adapter_registry import built_in_adapters, preview_adapters
from .data_loader import build_preview
from .export_engine import export_transaction_bundle
from .feed_engine import get_feed, get_feed_facets
from .models import (
    AdapterPreviewRequest,
    AdapterPreviewResponse,
    DataPreviewResponse,
    FeedFacetsResponse,
    FeedResponse,
    HealthResponse,
    ManifestResponse,
    PeriodExportResponse,
    RecentTransactionsResponse,
    TransactionExportResponse,
    TransactionNarrativeResponse,
    TimeAdvanceRequest,
    TimeTransactionResponse,
    TimelineCursor,
    UndoRedoResponse,
)
from .export_engine import export_period_bundle
from .narrative_engine import build_transaction_narrative
from .time_engine import (
    advance_time,
    current_cursor,
    recent_transactions,
    redo_last,
    undo_last,
)

app = FastAPI(title="Rimevegr Time Manager", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.get("/api/manifest", response_model=ManifestResponse)
def manifest() -> ManifestResponse:
    cursor = current_cursor()
    return ManifestResponse(
        tool="rimevegr-time-manager",
        branch="mainline",
        current_date=f"Y{cursor.year} D{cursor.day_of_year}",
        preview_mode=True,
        tracked_domains=[adapter.key for adapter in built_in_adapters()],
    )


@app.get("/api/adapters")
def adapters():
    return built_in_adapters()


@app.post("/api/adapters/preview", response_model=AdapterPreviewResponse)
def adapter_preview(request: AdapterPreviewRequest) -> AdapterPreviewResponse:
    return preview_adapters(current_cursor(), request.unit, request.amount)


@app.get("/api/data/preview", response_model=DataPreviewResponse)
def data_preview() -> DataPreviewResponse:
    return build_preview()


@app.get("/api/feed", response_model=FeedResponse)
def feed(
    year: int | None = None,
    day: int | None = None,
    categories: str | None = None,
    entities: str | None = None,
    limit: int = 80,
) -> FeedResponse:
    category_items = [item.strip() for item in (categories or "").split(",") if item.strip()]
    entity_items = [item.strip() for item in (entities or "").split(",") if item.strip()]
    return get_feed(
        year=year,
        day=day,
        categories=category_items,
        entities=entity_items,
        limit=limit,
    )


@app.get("/api/feed/facets", response_model=FeedFacetsResponse)
def feed_facets() -> FeedFacetsResponse:
    return get_feed_facets()


@app.get("/api/time/cursor", response_model=TimelineCursor)
def time_cursor() -> TimelineCursor:
    return current_cursor()


@app.get("/api/transactions/recent", response_model=RecentTransactionsResponse)
def transactions_recent(count: int = 5) -> RecentTransactionsResponse:
    return recent_transactions(count=count)


@app.post("/api/time/advance", response_model=TimeTransactionResponse)
def time_advance(request: TimeAdvanceRequest) -> TimeTransactionResponse:
    return advance_time(unit=request.unit, amount=request.amount, dry_run=request.dry_run)


@app.post("/api/time/undo", response_model=UndoRedoResponse)
def time_undo(dry_run: bool = True) -> UndoRedoResponse:
    return undo_last(dry_run=dry_run)


@app.post("/api/time/redo", response_model=UndoRedoResponse)
def time_redo(dry_run: bool = True) -> UndoRedoResponse:
    return redo_last(dry_run=dry_run)


@app.get(
    "/api/transactions/{transaction_id}/narrative",
    response_model=TransactionNarrativeResponse,
)
def transaction_narrative(transaction_id: str) -> TransactionNarrativeResponse:
    return build_transaction_narrative(transaction_id)


@app.post(
    "/api/transactions/{transaction_id}/export",
    response_model=TransactionExportResponse,
)
def transaction_export(transaction_id: str) -> TransactionExportResponse:
    return export_transaction_bundle(transaction_id)


@app.post("/api/exports/period", response_model=PeriodExportResponse)
def period_export(count: int = 3) -> PeriodExportResponse:
    return export_period_bundle(count=count)
