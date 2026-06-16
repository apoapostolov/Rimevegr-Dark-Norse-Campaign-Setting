from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


CHAPTER_EMOJIS: dict[str, str] = {
    "01": "🧭",
    "02": "🧾",
    "03": "🗺️",
    "04": "🍞",
    "05": "💰",
    "06": "📚",
    "07": "🙏",
    "08": "✨",
    "09": "🌨️",
    "10": "📆",
    "11": "🏘️",
    "12": "👑",
    "13": "⚔️",
    "14": "🐺",
    "15": "🪙",
    "16": "👥",
    "17": "🧍",
    "18": "⚰️",
    "19": "🎲",
    "20": "⚙️",
    "21": "📊",
    "22": "🛡️",
    "23": "🔥",
    "24": "🖋️",
}


@dataclass(frozen=True)
class NotionApiBudget:
    """Official Notion API limits that matter for this pipeline."""

    max_rich_text_chars: int = 2000
    max_blocks_per_append: int = 100
    max_payload_block_elements: int = 1000
    max_payload_bytes: int = 500 * 1024
    max_append_nesting_levels: int = 2
    average_requests_per_second: int = 3


@dataclass(frozen=True)
class HouseSafetyBudget:
    """Conservative limits used by the exporter for stable uploads."""

    max_subpage_source_bytes: int = 90_000
    max_subpage_estimated_blocks: int = 700
    max_append_batch_blocks: int = 90
    max_append_payload_bytes: int = 450 * 1024
    max_rich_text_chars: int = 1800
    request_rate_target: int = 2


@dataclass(frozen=True)
class DiscoveryRules:
    """Chapter inclusion and exclusion rules for the canonical export set."""

    include_low: int = 1
    include_high: int = 24
    ignore_keys: tuple[str, ...] = (
        "07B",
        "08A",
        "08B",
        "08C",
        "08D",
        "08E",
        "08F",
        "08G",
        "08H",
    )
    prefer_merged_keys: tuple[str, ...] = ("07", "08")

    def should_ignore(self, chapter_key: str) -> bool:
        return chapter_key.upper() in self.ignore_keys


@dataclass
class SubpageManifest:
    key: str
    title: str
    notion_page_id: str | None = None
    source_hash: str | None = None
    clean_hash: str | None = None
    block_count: int | None = None
    byte_count: int | None = None
    is_index_only: bool = False


@dataclass
class ChapterManifest:
    key: str
    title: str
    source_file: str
    chapter_page_id: str | None = None
    source_hash: str | None = None
    clean_hash: str | None = None
    ignored: bool = False
    ignored_reason: str | None = None
    subpages: list[SubpageManifest] = field(default_factory=list)


@dataclass(frozen=True)
class EntryPageBlueprint:
    title: str = "Rimevegr"
    icon: str = "🪓"
    hero_icon: str = "🌫️"
    promise_icon: str = "📜"
    blueprint_file: str = "ENTRY_PAGE_BLUEPRINT.md"
    section_order: tuple[str, ...] = (
        "hero_vignette",
        "world_summary",
        "table_of_contents",
        "identity_two_columns",
        "entry_hub_three_columns",
        "guided_entry_paths",
    )


@dataclass
class SyncManifest:
    pipeline_version: str = "0.1.0"
    notion_api_version: str = "2026-03-11"
    project_root_page_id: str | None = None
    chapters: list[ChapterManifest] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def default_path(cls, root: Path) -> Path:
        return root / "state" / "manifest.json"
