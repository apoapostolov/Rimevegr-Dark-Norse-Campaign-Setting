from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "rimevegr-time-manager"


class ManifestResponse(BaseModel):
    tool: str
    branch: str
    current_date: str
    preview_mode: bool
    tracked_domains: list[str] = Field(default_factory=list)


class AdapterDescriptor(BaseModel):
    key: str
    label: str
    domains: list[str] = Field(default_factory=list)
    granularities: list[str]
    write_targets: list[str]
    deterministic: bool
    implementation_status: str = "planned"
    notes: str | None = None


class DataDocumentSummary(BaseModel):
    path: str
    sha256: str
    top_level_keys: list[str] = Field(default_factory=list)
    settlement_refs: int = 0
    contract_refs: int = 0
    parse_mode: str


class ValidationIssue(BaseModel):
    severity: str
    code: str
    message: str
    path: str | None = None


class DataPreviewResponse(BaseModel):
    dry_run: bool = True
    document_count: int
    documents: list[DataDocumentSummary] = Field(default_factory=list)
    issues: list[ValidationIssue] = Field(default_factory=list)
    manifest_path: str


class TimelineCursor(BaseModel):
    year: int
    day_of_year: int
    season: str
    branch: str
    transaction_index: int = 0


class TimeAdvanceRequest(BaseModel):
    unit: str
    amount: int = 1
    dry_run: bool = True


class TimeTransactionResponse(BaseModel):
    dry_run: bool
    transaction_id: str
    branch: str
    unit: str
    amount: int
    seed: int
    adapter_seeds: dict[str, int] = Field(default_factory=dict)
    from_cursor: TimelineCursor
    to_cursor: TimelineCursor
    inverse_unit: str
    inverse_amount: int
    snapshot_path: str | None = None
    transaction_path: str | None = None


class UndoRedoResponse(BaseModel):
    action: str
    dry_run: bool
    transaction_id: str | None = None
    cursor: TimelineCursor
    blocked_reason: str | None = None


class AdapterPreviewRequest(BaseModel):
    unit: str
    amount: int = 1


class AdapterPreviewResult(BaseModel):
    key: str
    label: str
    domains: list[str] = Field(default_factory=list)
    status: str
    supported: bool
    write_targets: list[str] = Field(default_factory=list)
    summary: str
    metrics: dict[str, int | float | str] = Field(default_factory=dict)
    affected_entities: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class AdapterPreviewResponse(BaseModel):
    cursor: TimelineCursor
    unit: str
    amount: int
    adapters: list[AdapterPreviewResult] = Field(default_factory=list)


class NarrativeBlock(BaseModel):
    title: str
    lines: list[str] = Field(default_factory=list)


class TransactionNarrativeResponse(BaseModel):
    transaction_id: str
    operator_summary: list[str] = Field(default_factory=list)
    writer_summary: list[str] = Field(default_factory=list)
    blocks: list[NarrativeBlock] = Field(default_factory=list)


class TransactionExportResponse(BaseModel):
    transaction_id: str
    json_path: str
    markdown_path: str


class PeriodExportResponse(BaseModel):
    transaction_ids: list[str] = Field(default_factory=list)
    json_path: str
    markdown_path: str


class RecentTransactionItem(BaseModel):
    transaction_id: str
    unit: str
    amount: int
    from_label: str
    to_label: str
    note: str | None = None


class RecentTransactionsResponse(BaseModel):
    items: list[RecentTransactionItem] = Field(default_factory=list)


class FeedPost(BaseModel):
    id: str
    source_type: str
    simulated_year: int
    simulated_day: int
    simulated_label: str
    cadence: str = "day"
    span_start_year: int | None = None
    span_start_day: int | None = None
    span_end_year: int | None = None
    span_end_day: int | None = None
    title: str
    category: str
    tags: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    summary: str
    narrative: list[str] = Field(default_factory=list)
    technical: list[str] = Field(default_factory=list)
    provenance: str | None = None


class FeedResponse(BaseModel):
    items: list[FeedPost] = Field(default_factory=list)


class FeedFacetItem(BaseModel):
    label: str
    count: int


class FeedDateFacet(BaseModel):
    year: int
    day: int
    label: str
    count: int


class FeedFacetsResponse(BaseModel):
    dates: list[FeedDateFacet] = Field(default_factory=list)
    categories: list[FeedFacetItem] = Field(default_factory=list)
    entities: list[FeedFacetItem] = Field(default_factory=list)
