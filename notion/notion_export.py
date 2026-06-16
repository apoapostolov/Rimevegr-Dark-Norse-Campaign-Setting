from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import time
from pathlib import Path
from typing import Any
from urllib import error, request

from format_normalizer import FENCE_RE, NormalizationOptions, normalize_markdown
from models import (
    CHAPTER_EMOJIS,
    DiscoveryRules,
    EntryPageBlueprint,
    HouseSafetyBudget,
    NotionApiBudget,
    SyncManifest,
)


ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT.parent
RAW_DIR = ROOT / "raw"
CLEAN_DIR = ROOT / "clean"
SPLIT_DIR = ROOT / "split"
STATE_DIR = ROOT / "state"
REPO_ROOT = ROOT.parents[2]
NOTION_API_VERSION = "2026-03-11"
RENDERER_VERSION = "2026-04-17-notion-render-v3"
TOC_MARKER = "<!-- notion-export:toc -->"
CHAPTER_FILE_RE = re.compile(r"^(?P<key>\d{2}[A-Z]?)_.+\.md$", re.IGNORECASE)
LAST_NOTION_REQUEST_AT = 0.0
CURRENT_RETRY_POLICY: dict[str, Any] | None = None


def build_retry_policy(
    *,
    patient: bool = False,
    max_wait_minutes: int | None = None,
) -> dict[str, Any]:
    if patient:
        wait_minutes = max_wait_minutes or 180
        return {
            "patient": True,
            "max_attempts": 120,
            "max_total_wait_seconds": wait_minutes * 60,
            "default_base_delay_seconds": 15.0,
            "cloudflare_base_delay_seconds": 45.0,
            "max_delay_seconds": 900.0,
        }

    return {
        "patient": False,
        "max_attempts": 6,
        "max_total_wait_seconds": 10 * 60,
        "default_base_delay_seconds": 2.0,
        "cloudflare_base_delay_seconds": 5.0,
        "max_delay_seconds": 60.0,
    }


def configure_retry_policy(
    *,
    patient: bool = False,
    max_wait_minutes: int | None = None,
) -> dict[str, Any]:
    global CURRENT_RETRY_POLICY
    CURRENT_RETRY_POLICY = build_retry_policy(
        patient=patient,
        max_wait_minutes=max_wait_minutes,
    )
    return CURRENT_RETRY_POLICY


def get_retry_policy() -> dict[str, Any]:
    global CURRENT_RETRY_POLICY
    if CURRENT_RETRY_POLICY is None:
        CURRENT_RETRY_POLICY = build_retry_policy(patient=False)
    return CURRENT_RETRY_POLICY


def compute_retry_delay(
    attempt: int,
    *,
    blocked_by_cloudflare: bool = False,
    patient: bool = False,
) -> float:
    policy = build_retry_policy(patient=patient)
    base_delay = (
        policy["cloudflare_base_delay_seconds"]
        if blocked_by_cloudflare
        else policy["default_base_delay_seconds"]
    )
    growth = 1.8 if patient else 1.5
    return min(policy["max_delay_seconds"], base_delay * (growth**attempt))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare Norse Grit chapters for safe Notion sync."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("plan", help="Show the current pipeline plan.")
    subparsers.add_parser("status", help="Show the saved manifest status.")
    subparsers.add_parser("entry-page", help="Show the landing page blueprint metadata.")
    create_parser = subparsers.add_parser(
        "create-entry-page",
        help="Create the Notion landing page now as a live API test.",
    )
    create_parser.add_argument(
        "--parent-page-id",
        dest="parent_page_id",
        default=None,
        help="Optional Notion parent page URL or ID shared with the integration.",
    )
    create_parser.add_argument(
        "--patient",
        action="store_true",
        help="Retry patiently with long backoff if Notion or Cloudflare blocks the request.",
    )
    create_parser.add_argument(
        "--max-wait-minutes",
        type=int,
        default=180,
        help="Maximum total retry wait for patient mode.",
    )
    raw_copy_parser = subparsers.add_parser(
        "raw-copy",
        help="Copy the canonical core chapters into the raw export folder.",
    )
    raw_copy_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which chapters would be copied without writing files.",
    )
    normalize_parser = subparsers.add_parser(
        "normalize",
        help="Normalize the copied raw chapters into clean Notion-ready Markdown.",
    )
    normalize_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview which raw files would be normalized without writing clean output.",
    )
    split_parser = subparsers.add_parser(
        "split",
        help="Split oversized clean chapters into Notion-safe parts.",
    )
    split_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the split plan without writing files.",
    )
    split_parser.add_argument(
        "--max-bytes",
        type=int,
        default=HouseSafetyBudget().max_subpage_source_bytes,
        help="Override the conservative per-page byte budget.",
    )
    upload_parser = subparsers.add_parser(
        "upload",
        help="Create or update the chapter pages under the Notion project root.",
    )
    upload_parser.add_argument(
        "--root-page-id",
        dest="root_page_id",
        default=None,
        help="Optional override for the Notion root page ID or URL.",
    )
    upload_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the upload plan without making API changes.",
    )
    upload_parser.add_argument(
        "--patient",
        action="store_true",
        help="Retry patiently with long backoff if Notion or Cloudflare blocks the request.",
    )
    upload_parser.add_argument(
        "--max-wait-minutes",
        type=int,
        default=180,
        help="Maximum total retry wait for patient mode.",
    )
    sync_parser = subparsers.add_parser(
        "sync",
        help="Run raw copy, normalize, split, and upload in one pass.",
    )
    sync_parser.add_argument(
        "--root-page-id",
        dest="root_page_id",
        default=None,
        help="Optional override for the Notion root page ID or URL.",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the full sync without making API changes.",
    )
    sync_parser.add_argument(
        "--patient",
        action="store_true",
        help="Retry patiently with long backoff if Notion or Cloudflare blocks the request.",
    )
    sync_parser.add_argument(
        "--max-wait-minutes",
        type=int,
        default=180,
        help="Maximum total retry wait for patient mode.",
    )
    return parser


def read_simple_dotenv(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def get_notion_api_key() -> str:
    env_key = os.environ.get("NOTION_API_KEY")
    if env_key:
        return env_key

    dotenv_path = REPO_ROOT / ".env"
    dotenv_values = read_simple_dotenv(dotenv_path)
    notion_key = dotenv_values.get("NOTION_API_KEY")
    if notion_key:
        return notion_key

    raise RuntimeError("NOTION_API_KEY was not found in the environment or root .env file.")


def chapter_sort_key(chapter_key: str) -> tuple[int, int, str]:
    base = int(chapter_key[:2])
    suffix = chapter_key[2:] if len(chapter_key) > 2 else ""
    return (base, 0 if not suffix else 1, suffix)


def discover_chapter_inventory(source_root: Path | None = None) -> dict[str, list[dict[str, Any]]]:
    source_root = Path(source_root or SOURCE_ROOT)
    rules = DiscoveryRules()
    inventory: dict[str, list[dict[str, Any]]] = {
        "core": [],
        "supplements": [],
        "ignored_by_rule": [],
    }

    for path in sorted(source_root.glob("*.md")):
        match = CHAPTER_FILE_RE.match(path.name)
        if not match:
            continue

        chapter_key = match.group("key").upper()
        chapter_number = int(chapter_key[:2])
        if not rules.include_low <= chapter_number <= rules.include_high:
            continue

        item = {
            "key": chapter_key,
            "filename": path.name,
            "path": str(path),
            "root_key": chapter_key[:2],
        }

        if len(chapter_key) == 2:
            inventory["core"].append(item)
        elif rules.should_ignore(chapter_key):
            item["reason"] = "ignored_by_rule"
            inventory["ignored_by_rule"].append(item)
        else:
            item["reason"] = "supplemental_variant"
            inventory["supplements"].append(item)

    for group in inventory.values():
        group.sort(key=lambda item: chapter_sort_key(item["key"]))

    return inventory


def copy_core_chapters(
    source_root: Path | None = None,
    raw_dir: Path | None = None,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    source_root = Path(source_root or SOURCE_ROOT)
    raw_dir = Path(raw_dir or RAW_DIR)
    inventory = discover_chapter_inventory(source_root)
    core_files = inventory["core"]

    if not dry_run:
        raw_dir.mkdir(parents=True, exist_ok=True)
        for existing_file in raw_dir.glob("*.md"):
            existing_file.unlink()
        for item in core_files:
            shutil.copy2(source_root / item["filename"], raw_dir / item["filename"])

    report = {
        "source_root": str(source_root),
        "raw_dir": str(raw_dir),
        "dry_run": dry_run,
        "copied_count": 0 if dry_run else len(core_files),
        "core_count": len(core_files),
        "core": core_files,
        "supplements": inventory["supplements"],
        "ignored_by_rule": inventory["ignored_by_rule"],
    }

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "raw_copy_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return report


def split_text_for_notion(
    content: str,
    *,
    url: str | None = None,
    bold: bool = False,
    italic: bool = False,
    code: bool = False,
) -> list[dict[str, Any]]:
    limit = HouseSafetyBudget().max_rich_text_chars
    chunks = [content[i : i + limit] for i in range(0, len(content), limit)] or [""]
    return [
        {
            "type": "text",
            "text": {
                "content": chunk,
                "link": None if not url else {"url": url},
            },
            "annotations": {
                "bold": bold,
                "italic": italic,
                "strikethrough": False,
                "underline": False,
                "code": code,
                "color": "default",
            },
        }
        for chunk in chunks
    ]


def rich_text(content: str) -> dict[str, Any]:
    return split_text_for_notion(content)[0]


def ensure_rich_text_items(content: str | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(content, list):
        return content
    return split_text_for_notion(content)


def paragraph_block(content: str | list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": ensure_rich_text_items(content),
            "color": "default",
        },
    }


def heading_block(level: int, content: str | list[dict[str, Any]]) -> dict[str, Any]:
    safe_level = min(max(level, 1), 3)
    block_type = f"heading_{safe_level}"
    return {
        "object": "block",
        "type": block_type,
        block_type: {
            "rich_text": ensure_rich_text_items(content),
            "color": "default",
            "is_toggleable": False,
        },
    }


def bullet_block(content: str | list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": ensure_rich_text_items(content),
            "color": "default",
        },
    }


def numbered_block(content: str | list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {
            "rich_text": ensure_rich_text_items(content),
            "color": "default",
        },
    }


def quote_block(content: str | list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "quote",
        "quote": {
            "rich_text": ensure_rich_text_items(content),
            "color": "default",
        },
    }


def code_block(content: str, language: str = "plain text") -> dict[str, Any]:
    return {
        "object": "block",
        "type": "code",
        "code": {
            "rich_text": split_text_for_notion(content),
            "language": language,
        },
    }


def callout_block(content: str | list[dict[str, Any]], emoji: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": ensure_rich_text_items(content),
            "icon": {"type": "emoji", "emoji": emoji},
            "color": "gray_background",
        },
    }


def divider_block() -> dict[str, Any]:
    return {
        "object": "block",
        "type": "divider",
        "divider": {},
    }


def toc_block() -> dict[str, Any]:
    return {
        "object": "block",
        "type": "table_of_contents",
        "table_of_contents": {"color": "default"},
    }


def column_block(children: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "column",
        "column": {
            "children": children,
        },
    }


def column_list_block(columns: list[list[dict[str, Any]]]) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "column_list",
        "column_list": {
            "children": [column_block(children) for children in columns],
        },
    }


def normalize_notion_parent_id(value: str | None) -> str | None:
    if not value:
        return None

    raw = value.strip()
    if not raw:
        return None

    if raw.startswith("http"):
        match = re.search(r"([0-9a-fA-F]{32})", raw.replace("-", ""))
        if match:
            raw = match.group(1)

    compact = raw.replace("-", "")
    if len(compact) == 32:
        return (
            f"{compact[0:8]}-{compact[8:12]}-{compact[12:16]}-"
            f"{compact[16:20]}-{compact[20:32]}"
        )
    return raw


def compose_entry_rich_text(
    *parts: str | tuple[str, str] | tuple[str, str, bool],
    link_map: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    safe_map = link_map or {}

    for part in parts:
        if isinstance(part, tuple):
            if len(part) == 2:
                label, target = part
                bold = False
            else:
                label, target, bold = part
            lookup_key = normalize_link_target(target)
            url = safe_map.get(lookup_key) or safe_map.get(lookup_key.upper())
            items.extend(split_text_for_notion(label, url=url, bold=bold))
        else:
            items.extend(split_text_for_notion(part))

    return items


def build_entry_page_blocks(
    *,
    use_columns: bool = True,
    link_map: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    blueprint = EntryPageBlueprint()
    children: list[dict[str, Any]] = [
        callout_block(
            "Voss counted heads at the ford and came up one short. The river had not taken anyone. The arithmetic was the same as always: feed the ones who stayed, pay the ones who fought, bury the ones who fell, and forget the ones who walked off in the dark.",
            blueprint.hero_icon,
        ),
        paragraph_block(
            "Iron Ledger is a low-magic Norse frontier setting trapped in long cold twilight after the gods fell silent. Small hard settlements cling to trade, oath, and firelight while hired bands sell protection, violence, and endurance for silver."
        ),
        divider_block(),
    ]

    if use_columns:
        children.append(
            column_list_block(
                [
                    [
                        heading_block(2, "What this setting is"),
                        bullet_block(
                            compose_entry_rich_text(
                                ("Mercenary-survival Norse world.", "01_RIMEVEGR_SETTING_BIBLE.md", True),
                                " Contracts, food, weather, and kinship pressure drive nearly every choice, from where a band sleeps to which oath it can still afford to keep.",
                                link_map=link_map,
                            )
                        ),
                        bullet_block(
                            compose_entry_rich_text(
                                ("Low magic with high consequence.", "08_MAGIC_OF_RIMEVEGR.md", True),
                                " The supernatural exists, but every use leaves a social, bodily, or spiritual cost that lingers long after the moment of wonder.",
                                link_map=link_map,
                            )
                        ),
                        bullet_block(
                            compose_entry_rich_text(
                                ("Driven by hunger, weather, debt, and oath-keeping.", "05_ECONOMY_OF_RIMEVEGR.md", True),
                                " Survival depends as much on logistics and promises as on steel, because a missed payment can wreck a season as surely as defeat.",
                                link_map=link_map,
                            )
                        ),
                        bullet_block(
                            compose_entry_rich_text(
                                ("Grounded dread.", "24_VIGNETTES_AND_SCENES.md", True),
                                " Horror arrives through omen, silence, rumor, memory, and accumulating cost, building pressure slowly instead of exploding into spectacle.",
                                link_map=link_map,
                            )
                        ),
                    ],
                    [
                        heading_block(2, "What this setting is not"),
                        bullet_block(
                            compose_entry_rich_text(
                                ("Not heroic power fantasy.", "15_MERCENARY_LIFESTYLE.md", True),
                                " People endure, bargain, and survive; they do not stride above consequence or solve hardship through destiny.",
                                link_map=link_map,
                            )
                        ),
                        bullet_block(
                            compose_entry_rich_text(
                                ("Not a raid-glory Viking caricature.", "04_CULTURE_AND_CUSTOMS.md", True),
                                " Social reality, labor, trade, kin tension, and law matter more than spectacle plunder or costume mythology.",
                                link_map=link_map,
                            )
                        ),
                        bullet_block(
                            compose_entry_rich_text(
                                ("Not high fantasy with chosen ones or dark lords.", "07_RELIGION_OF_RIMEVEGR.md", True),
                                " The setting stays local, human, and uncertain rather than prophecy-driven, world-saving, or mythically ordained.",
                                link_map=link_map,
                            )
                        ),
                        bullet_block(
                            compose_entry_rich_text(
                                ("Not spectacle magic or cruelty for style alone.", "08_MAGIC_OF_RIMEVEGR.md", True),
                                " Wonder and violence are present only when they deepen tension, price, and tone instead of becoming decorative excess.",
                                link_map=link_map,
                            )
                        ),
                    ],
                ]
            )
        )
        children.append(divider_block())
        children.append(
            column_list_block(
                [
                    [
                        heading_block(2, "Rimevegr"),
                        bullet_block(compose_entry_rich_text("🧭 ", ("Setting Bible", "01_RIMEVEGR_SETTING_BIBLE.md"), " — the canon overview", link_map=link_map)),
                        bullet_block(compose_entry_rich_text("🗺️ ", ("Geography and Map", "03_GEOGRAPHY_AND_MAP.md"), " — land, travel, and regions", link_map=link_map)),
                        bullet_block(compose_entry_rich_text("🍞 ", ("Culture and Customs", "04_CULTURE_AND_CUSTOMS.md"), " — daily life and social norms", link_map=link_map)),
                        bullet_block(compose_entry_rich_text("🙏 ", ("Religion of the Rimevegr", "07_RELIGION_OF_RIMEVEGR.md"), " — the silent gods and their rites", link_map=link_map)),
                        bullet_block(compose_entry_rich_text("✨ ", ("Magic of Rimevegr", "08_MAGIC_OF_RIMEVEGR.md"), " — rune-work, seiðr, and dread", link_map=link_map)),
                    ],
                    [
                        heading_block(2, "The Living World"),
                        bullet_block(compose_entry_rich_text("🏘️ ", ("Villages and Settlements", "11_VILLAGES_AND_SETTLEMENTS.md"), " — the places people still endure", link_map=link_map)),
                        bullet_block(compose_entry_rich_text("👑 ", ("Political Villages and Unions", "12_POLITICAL_VILLAGES_AND_UNIONS.md"), " — power, law, and rivalry", link_map=link_map)),
                        bullet_block(compose_entry_rich_text("⚔️ ", ("Rival Bands and Factions", "13_RIVAL_BANDS_AND_FACTIONS.md"), " — organized pressure from outside", link_map=link_map)),
                        bullet_block(compose_entry_rich_text("🐺 ", ("Wolfsheads of Rimevegr", "14_WOLFSHEADS_OF_RIMEVEGR.md"), " — outlaw threat and fear", link_map=link_map)),
                        bullet_block(compose_entry_rich_text("🪙 ", ("Mercenary Lifestyle", "15_MERCENARY_LIFESTYLE.md"), " — the band-for-hire reality", link_map=link_map)),
                    ],
                    [
                        heading_block(2, "Play or Write"),
                        bullet_block(compose_entry_rich_text("🧾 ", ("Master Index", "02_MASTER_INDEX.md"), " — the full project map", link_map=link_map)),
                        bullet_block(compose_entry_rich_text("🎲 ", ("Game Content Bible", "19_GAME_CONTENT_BIBLE.md"), " — tools, tables, and support data", link_map=link_map)),
                        bullet_block(compose_entry_rich_text("⚙️ ", ("Simulation Rules", "20_SIMULATION_RULES.md"), " — the engine under the world", link_map=link_map)),
                        bullet_block(compose_entry_rich_text("🔥 ", ("Campaign Arcs and Plot Seeds", "23_CAMPAIGN_ARCS_AND_PLOT_SEEDS.md"), " — long-form story entry", link_map=link_map)),
                        bullet_block(compose_entry_rich_text("🖋️ ", ("Vignettes and Scenes", "24_VIGNETTES_AND_SCENES.md"), " — tone, voice, and openings", link_map=link_map)),
                    ],
                ]
            )
        )
    else:
        children.extend(
            [
                heading_block(2, "What this setting is"),
                bullet_block("A mercenary-survival Norse world."),
                bullet_block("Low magic with high consequence."),
                bullet_block("Driven by hunger, weather, debt, and oath-keeping."),
                bullet_block("Grounded dread through pressure and cost."),
                heading_block(2, "What this setting is not"),
                bullet_block("Not heroic power fantasy."),
                bullet_block("Not a raid-glory Viking caricature."),
                bullet_block("Not high fantasy with chosen ones or dark lords."),
                divider_block(),
                heading_block(2, "Entry points"),
                bullet_block("🧭 Start with 01 Setting Bible for canon and tone."),
                bullet_block("🏘️ Use 11 to 17 for people, places, and conflict."),
                bullet_block("⚙️ Use 19 to 24 for systems, arcs, and fiction voice."),
            ]
        )

    children.extend(
        [
            divider_block(),
            heading_block(2, "Start here if you want..."),
            bullet_block(
                compose_entry_rich_text(
                    "📖 To understand the world fast: ",
                    ("Setting Bible", "01_RIMEVEGR_SETTING_BIBLE.md"),
                    " → ",
                    ("Geography and Map", "03_GEOGRAPHY_AND_MAP.md"),
                    " → ",
                    ("Culture and Customs", "04_CULTURE_AND_CUSTOMS.md"),
                    " → ",
                    ("Mercenary Lifestyle", "15_MERCENARY_LIFESTYLE.md"),
                    link_map=link_map,
                )
            ),
            bullet_block(
                compose_entry_rich_text(
                    "🧭 To run a campaign: ",
                    ("Setting Bible", "01_RIMEVEGR_SETTING_BIBLE.md"),
                    " → ",
                    ("Villages and Settlements", "11_VILLAGES_AND_SETTLEMENTS.md"),
                    " → ",
                    ("Rival Bands and Factions", "13_RIVAL_BANDS_AND_FACTIONS.md"),
                    " → ",
                    ("Simulation Rules", "20_SIMULATION_RULES.md"),
                    " → ",
                    ("Campaign Arcs and Plot Seeds", "23_CAMPAIGN_ARCS_AND_PLOT_SEEDS.md"),
                    link_map=link_map,
                )
            ),
            bullet_block(
                compose_entry_rich_text(
                    "✍️ To write fiction: ",
                    ("Vignettes and Scenes", "24_VIGNETTES_AND_SCENES.md"),
                    " → ",
                    ("Character Bible", "17_CHARACTER_BIBLE.md"),
                    " → ",
                    ("Mercenary Lifestyle", "15_MERCENARY_LIFESTYLE.md"),
                    " → ",
                    ("Campaign Arcs and Plot Seeds", "23_CAMPAIGN_ARCS_AND_PLOT_SEEDS.md"),
                    link_map=link_map,
                )
            ),
            bullet_block(
                compose_entry_rich_text(
                    "👻 To lean into the dread: ",
                    ("Religion of the Rimevegr", "07_RELIGION_OF_RIMEVEGR.md"),
                    " → ",
                    ("Magic of Rimevegr", "08_MAGIC_OF_RIMEVEGR.md"),
                    " → ",
                    ("Barrows of Rimevegr", "18_BARROWS_OF_RIMEVEGR.md"),
                    " → ",
                    ("Weather, Seasons, and Hazards", "09_WEATHER_SEASONS_AND_HAZARDS.md"),
                    link_map=link_map,
                )
            ),
        ]
    )
    return children


def build_entry_page_payload(
    parent_page_id: str | None = None,
    *,
    use_columns: bool = True,
    link_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    blueprint = EntryPageBlueprint()
    parent_page_id = normalize_notion_parent_id(parent_page_id)
    parent: dict[str, Any]
    if parent_page_id:
        parent = {"type": "page_id", "page_id": parent_page_id}
    else:
        parent = {"type": "workspace", "workspace": True}

    return {
        "parent": parent,
        "icon": {"type": "emoji", "emoji": blueprint.icon},
        "properties": {
            "title": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": blueprint.title},
                    }
                ]
            }
        },
        "children": build_entry_page_blocks(use_columns=use_columns, link_map=link_map),
    }


def notion_api_request(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    global LAST_NOTION_REQUEST_AT

    api_key = get_notion_api_key()
    retry_policy = get_retry_policy()
    min_interval = 0.55
    elapsed = time.monotonic() - LAST_NOTION_REQUEST_AT
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)

    last_error: RuntimeError | None = None
    total_waited = 0.0

    for attempt in range(retry_policy["max_attempts"]):
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        req = request.Request(
            url=f"https://api.notion.com/v1{path}",
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Notion-Version": NOTION_API_VERSION,
                "User-Agent": "norse-grit-notion-export/0.1",
            },
        )
        try:
            with request.urlopen(req, timeout=90) as response:
                LAST_NOTION_REQUEST_AT = time.monotonic()
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            detail_lower = detail.lower()
            blocked_by_cloudflare = "cloudflare" in detail_lower or "enable cookies" in detail_lower
            is_retryable = exc.code in (403, 429, 502, 503, 504) or blocked_by_cloudflare
            last_error = RuntimeError(
                f"Notion API request failed with HTTP {exc.code}: {detail}"
            )
            if not is_retryable or attempt >= retry_policy["max_attempts"] - 1:
                raise last_error from exc

            wait_seconds = compute_retry_delay(
                attempt + 1,
                blocked_by_cloudflare=blocked_by_cloudflare,
                patient=retry_policy["patient"],
            )
            remaining_budget = retry_policy["max_total_wait_seconds"] - total_waited
            if remaining_budget <= 0:
                raise last_error from exc
            wait_seconds = min(wait_seconds, remaining_budget)
            print(
                f"Notion API retry {attempt + 1}/{retry_policy['max_attempts']} after HTTP {exc.code}. Waiting {wait_seconds:.0f}s before retrying {path}...",
                flush=True,
            )
            time.sleep(wait_seconds)
            total_waited += wait_seconds
            continue

    assert last_error is not None
    raise last_error


def list_block_children(block_id: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    next_cursor: str | None = None

    while True:
        path = f"/blocks/{block_id}/children?page_size=100"
        if next_cursor:
            path += f"&start_cursor={next_cursor}"
        payload = notion_api_request("GET", path, None)
        results.extend(payload.get("results", []))
        if not payload.get("has_more"):
            break
        next_cursor = payload.get("next_cursor")

    return results


def delete_block(block_id: str) -> None:
    try:
        notion_api_request("DELETE", f"/blocks/{block_id}", None)
    except RuntimeError as exc:
        message = str(exc).lower()
        if "archived ancestor" in message or "can't edit block that is archived" in message:
            return
        raise


def clear_page_children(page_id: str, *, preserve_child_pages: bool = False) -> int:
    children = list_block_children(page_id)
    deleted = 0
    for child in children:
        if preserve_child_pages and child.get("type") == "child_page":
            continue
        delete_block(child["id"])
        deleted += 1
    return deleted


def append_blocks_to_page(page_id: str, blocks: list[dict[str, Any]]) -> int:
    appended = 0
    batch_size = min(
        HouseSafetyBudget().max_append_batch_blocks,
        NotionApiBudget().max_blocks_per_append,
    )
    for start in range(0, len(blocks), batch_size):
        chunk = blocks[start : start + batch_size]
        notion_api_request(
            "PATCH",
            f"/blocks/{page_id}/children",
            {"children": chunk},
        )
        appended += len(chunk)
    return appended


def update_page_icon(page_id: str) -> None:
    blueprint = EntryPageBlueprint()
    notion_api_request(
        "PATCH",
        f"/pages/{page_id}",
        {"icon": {"type": "emoji", "emoji": blueprint.icon}},
    )


def trash_page(page_id: str) -> None:
    try:
        notion_api_request("PATCH", f"/pages/{page_id}", {"in_trash": True})
    except RuntimeError as exc:
        message = str(exc).lower()
        if "archived" in message or "already in trash" in message:
            return
        raise


def save_entry_page_state(result: dict[str, Any], layout_mode: str) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_path = STATE_DIR / "entry_page_test.json"
    state_payload = {
        "page_id": result.get("id"),
        "url": result.get("url"),
        "title": result.get("properties", {}).get("title", {}),
        "layout_mode": layout_mode,
        "created_time": result.get("created_time"),
        "last_edited_time": result.get("last_edited_time"),
    }
    state_path.write_text(
        json.dumps(state_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def update_manifest_root_page(result: dict[str, Any]) -> None:
    manifest_path = SyncManifest.default_path(ROOT)
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = SyncManifest().to_dict()
    manifest["project_root_page_id"] = result.get("id")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def normalize_raw_chapters(
    raw_dir: Path | None = None,
    clean_dir: Path | None = None,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    raw_dir = Path(raw_dir or RAW_DIR)
    clean_dir = Path(clean_dir or CLEAN_DIR)
    files = sorted(raw_dir.glob("*.md"))

    normalized_files: list[dict[str, Any]] = []
    if not dry_run:
        clean_dir.mkdir(parents=True, exist_ok=True)
        for existing_file in clean_dir.glob("*.md"):
            existing_file.unlink()

    for path in files:
        source_text = path.read_text(encoding="utf-8")
        normalized_text = normalize_markdown(
            source_text,
            NormalizationOptions(unwrap_paragraphs=True),
        )
        if not dry_run:
            (clean_dir / path.name).write_text(normalized_text, encoding="utf-8")
        normalized_files.append(
            {
                "filename": path.name,
                "source_bytes": len(source_text.encode("utf-8")),
                "clean_bytes": len(normalized_text.encode("utf-8")),
            }
        )

    report = {
        "raw_dir": str(raw_dir),
        "clean_dir": str(clean_dir),
        "dry_run": dry_run,
        "normalized_count": len(normalized_files),
        "files": normalized_files,
    }
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "normalize_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return report


def byte_count(text: str) -> int:
    return len(text.encode("utf-8"))


def estimate_block_count(text: str) -> int:
    count = 0
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if FENCE_RE.match(stripped):
            count += 1
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            continue
        count += 1
    return count


def extract_markdown_title(text: str, fallback_filename: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()

    fallback = Path(fallback_filename).stem
    fallback = re.sub(r"^\d{2}[A-Z]?_", "", fallback)
    return fallback.replace("_", " ").strip()


def inject_toc_marker(text: str) -> str:
    if TOC_MARKER in text:
        return text if text.endswith("\n") else f"{text}\n"

    lines = text.rstrip().splitlines()
    if lines and lines[0].startswith("# "):
        result = [lines[0], "", TOC_MARKER]
        if len(lines) > 1:
            result.extend(["", *lines[1:]])
        return "\n".join(result).rstrip() + "\n"

    return f"{TOC_MARKER}\n\n{text.rstrip()}\n"


def split_on_heading(text: str, prefix: str) -> list[str]:
    pattern = re.compile(rf"(?=^{re.escape(prefix)}\s+)", re.MULTILINE)
    parts = [part.strip() for part in pattern.split(text.strip()) if part.strip()]
    return [f"{part}\n" for part in parts]


def pack_chunks(chunks: list[str], max_bytes: int, *, prefix: str = "") -> list[str]:
    built: list[str] = []
    current = prefix.strip()

    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        candidate = chunk if not current else f"{current}\n\n{chunk}"
        if current and byte_count(candidate) > max_bytes:
            built.append(current.rstrip() + "\n")
            current = f"{prefix.strip()}\n\n{chunk}" if prefix.strip() else chunk
        else:
            current = candidate

    if current.strip():
        built.append(current.rstrip() + "\n")
    return built


def split_large_section(section_text: str, max_bytes: int) -> list[str]:
    if byte_count(section_text) <= max_bytes:
        return [section_text]

    lines = section_text.strip().splitlines()
    section_heading = lines[0] if lines else ""
    body = "\n".join(lines[1:]).strip()

    h3_chunks = split_on_heading(body, "###")
    if len(h3_chunks) > 1:
        return pack_chunks(h3_chunks, max_bytes, prefix=section_heading)

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
    if len(paragraphs) > 1:
        return pack_chunks(paragraphs, max_bytes, prefix=section_heading)

    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", body) if part.strip()]
    if len(sentences) > 1:
        return pack_chunks(sentences, max_bytes, prefix=section_heading)

    return [section_text]


def extract_preamble_and_h2_sections(text: str) -> tuple[str, list[str]]:
    lines = text.strip().splitlines()
    preamble: list[str] = []
    sections: list[str] = []
    current: list[str] = []
    in_section = False

    for line in lines:
        if line.startswith("## "):
            if current:
                sections.append("\n".join(current).rstrip() + "\n")
            current = [line]
            in_section = True
            continue

        if in_section:
            current.append(line)
        else:
            preamble.append(line)

    if current:
        sections.append("\n".join(current).rstrip() + "\n")

    return "\n".join(preamble).rstrip() + "\n", sections


def alpha_suffix(index: int) -> str:
    letters = ""
    current = index
    while current > 0:
        current -= 1
        letters = chr(ord("A") + (current % 26)) + letters
        current //= 26
    return letters


def first_subheading(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            return stripped[3:].strip()
    return None


def clean_section_name_for_page_title(section_name: str | None) -> str | None:
    if not section_name:
        return None

    cleaned = section_name.strip()
    cleaned = re.sub(r"^\d+\s*[.)\-:]\s*", "", cleaned)
    cleaned = re.sub(r"^\d+\s+", "", cleaned)
    return cleaned.strip() or None


def build_split_part_title(part_number: int, section_name: str | None, fallback_title: str) -> str:
    cleaned = clean_section_name_for_page_title(section_name) or fallback_title.strip()
    return f"{part_number} -- {cleaned}"


def build_split_chapter_index_text(title: str, part_titles: list[str]) -> str:
    lines = [
        f"# {title}",
        "",
        TOC_MARKER,
        "",
        "## Chapter navigation",
        "",
        "Open the numbered child pages below.",
    ]
    return "\n".join(lines) + "\n"


def split_clean_chapter_text(
    chapter_key: str,
    filename: str,
    text: str,
    *,
    max_bytes: int | None = None,
) -> dict[str, Any]:
    max_bytes = max_bytes or HouseSafetyBudget().max_subpage_source_bytes
    title = extract_markdown_title(text, filename)
    chapter_bytes = byte_count(text)
    estimated_blocks = estimate_block_count(text)

    if chapter_bytes <= max_bytes:
        return {
            "chapter_key": chapter_key,
            "title": title,
            "filename": filename,
            "is_split": False,
            "source_bytes": chapter_bytes,
            "estimated_blocks": estimated_blocks,
            "parts": [
                {
                    "key": chapter_key,
                    "title": title,
                    "content": inject_toc_marker(text),
                    "source_bytes": chapter_bytes,
                    "estimated_blocks": estimated_blocks,
                }
            ],
        }

    preamble, sections = extract_preamble_and_h2_sections(text)
    expanded_sections: list[str] = []
    for section in sections:
        expanded_sections.extend(split_large_section(section, max_bytes))

    if expanded_sections:
        raw_parts = pack_chunks(expanded_sections, max_bytes, prefix=preamble)
    else:
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
        raw_parts = pack_chunks(paragraphs, max_bytes, prefix=f"# {title}")

    parts: list[dict[str, Any]] = []
    for index, part_text in enumerate(raw_parts, start=1):
        part_key = f"{chapter_key}{alpha_suffix(index)}"
        section_name = first_subheading(part_text)
        part_title = build_split_part_title(index, section_name, title)
        prepared = inject_toc_marker(part_text)
        parts.append(
            {
                "key": part_key,
                "title": part_title,
                "content": prepared,
                "source_bytes": byte_count(prepared),
                "estimated_blocks": estimate_block_count(prepared),
            }
        )

    return {
        "chapter_key": chapter_key,
        "title": title,
        "filename": filename,
        "is_split": True,
        "source_bytes": chapter_bytes,
        "estimated_blocks": estimated_blocks,
        "parts": parts,
    }


def split_clean_chapters(
    clean_dir: Path | None = None,
    split_dir: Path | None = None,
    *,
    dry_run: bool = False,
    max_bytes: int | None = None,
) -> dict[str, Any]:
    clean_dir = Path(clean_dir or CLEAN_DIR)
    split_dir = Path(split_dir or SPLIT_DIR)
    max_bytes = max_bytes or HouseSafetyBudget().max_subpage_source_bytes
    files = sorted(clean_dir.glob("*.md"))

    chapters: list[dict[str, Any]] = []
    if not dry_run:
        split_dir.mkdir(parents=True, exist_ok=True)
        for existing in split_dir.glob("*.md"):
            existing.unlink()

    for path in files:
        match = CHAPTER_FILE_RE.match(path.name)
        if not match:
            continue
        chapter_key = match.group("key").upper()
        result = split_clean_chapter_text(
            chapter_key,
            path.name,
            path.read_text(encoding="utf-8"),
            max_bytes=max_bytes,
        )
        chapters.append(result)

        if dry_run:
            continue

        suffix = re.sub(r"^\d{2}[A-Z]?_", "", path.name)
        for part in result["parts"]:
            target_name = f"{part['key']}_{suffix}"
            (split_dir / target_name).write_text(part["content"], encoding="utf-8")

    report = {
        "clean_dir": str(clean_dir),
        "split_dir": str(split_dir),
        "dry_run": dry_run,
        "max_bytes": max_bytes,
        "chapter_count": len(chapters),
        "split_count": sum(1 for item in chapters if item["is_split"]),
        "chapters": [
            {
                "chapter_key": item["chapter_key"],
                "title": item["title"],
                "is_split": item["is_split"],
                "source_bytes": item["source_bytes"],
                "estimated_blocks": item["estimated_blocks"],
                "part_keys": [part["key"] for part in item["parts"]],
                "part_bytes": [part["source_bytes"] for part in item["parts"]],
            }
            for item in chapters
        ],
    }
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "split_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return report


def command_raw_copy(*, dry_run: bool = False) -> int:
    report = copy_core_chapters(SOURCE_ROOT, RAW_DIR, dry_run=dry_run)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


def command_normalize(*, dry_run: bool = False) -> int:
    report = normalize_raw_chapters(RAW_DIR, CLEAN_DIR, dry_run=dry_run)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


def command_split(*, dry_run: bool = False, max_bytes: int | None = None) -> int:
    report = split_clean_chapters(
        CLEAN_DIR,
        SPLIT_DIR,
        dry_run=dry_run,
        max_bytes=max_bytes,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_render_hash(text: str, blocks: list[dict[str, Any]]) -> str:
    payload = {
        "renderer_version": RENDERER_VERSION,
        "text": text,
        "blocks": blocks,
    }
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def sanitize_manifest_data(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            if isinstance(key, str) and key.startswith("_"):
                continue
            cleaned[key] = sanitize_manifest_data(item)
        if "chapters" in cleaned and not isinstance(cleaned["chapters"], list):
            cleaned["chapters"] = []
        return cleaned
    if isinstance(value, list):
        return [sanitize_manifest_data(item) for item in value]
    return value


def load_manifest_data() -> dict[str, Any]:
    manifest_path = SyncManifest.default_path(ROOT)
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        data = SyncManifest().to_dict()
    data = sanitize_manifest_data(data)
    data.setdefault("chapters", [])
    return data


def save_manifest_data(manifest: dict[str, Any]) -> None:
    manifest = sanitize_manifest_data(manifest)
    manifest_path = SyncManifest.default_path(ROOT)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def create_child_page(
    parent_page_id: str,
    title: str,
    emoji: str | None = None,
    children: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "properties": {
            "title": {
                "title": split_text_for_notion(title),
            }
        },
    }
    if emoji:
        payload["icon"] = {"type": "emoji", "emoji": emoji}
    if children:
        max_initial_children = min(
            HouseSafetyBudget().max_append_batch_blocks,
            NotionApiBudget().max_blocks_per_append,
        )
        payload["children"] = children[:max_initial_children]
    return notion_api_request("POST", "/pages", payload)


def update_page_metadata(page_id: str, title: str, emoji: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "properties": {
            "title": {
                "title": split_text_for_notion(title),
            }
        }
    }
    if emoji:
        payload["icon"] = {"type": "emoji", "emoji": emoji}
    return notion_api_request("PATCH", f"/pages/{page_id}", payload)


def ensure_page(
    parent_page_id: str,
    existing_page_id: str | None,
    *,
    title: str,
    emoji: str | None = None,
    replace_existing: bool = False,
    children: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if existing_page_id:
        try:
            return update_page_metadata(existing_page_id, title, emoji=emoji)
        except RuntimeError:
            pass
    return create_child_page(parent_page_id, title, emoji=emoji, children=children)


def replace_page_content(
    parent_page_id: str,
    existing_page_id: str | None,
    *,
    title: str,
    emoji: str | None = None,
    blocks: list[dict[str, Any]],
    preserve_child_pages: bool = False,
) -> dict[str, Any]:
    if existing_page_id:
        page_result = update_page_metadata(existing_page_id, title, emoji=emoji)
        clear_page_children(existing_page_id, preserve_child_pages=preserve_child_pages)
        if blocks:
            append_blocks_to_page(existing_page_id, blocks)
        return page_result

    max_initial_children = min(
        HouseSafetyBudget().max_append_batch_blocks,
        NotionApiBudget().max_blocks_per_append,
    )
    initial_children = blocks[:max_initial_children]
    remaining_blocks = blocks[max_initial_children:]
    page_result = create_child_page(
        parent_page_id,
        title,
        emoji=emoji,
        children=initial_children,
    )
    if remaining_blocks:
        append_blocks_to_page(page_result["id"], remaining_blocks)
    return page_result


def normalize_link_target(target: str) -> str:
    normalized = target.strip().strip("`")
    normalized = normalized.split("#", 1)[0]
    normalized = normalized.split("?", 1)[0]
    normalized = normalized.replace("\\", "/")
    normalized = normalized.rsplit("/", 1)[-1]
    return normalized


def build_link_map(manifest: dict[str, Any]) -> dict[str, str]:
    link_map: dict[str, str] = {}
    for chapter in manifest.get("chapters", []):
        chapter_url = chapter.get("url")
        source_file = chapter.get("source_file")
        if chapter_url and source_file:
            link_map[source_file] = chapter_url
            link_map[source_file.upper()] = chapter_url
        if chapter_url and chapter.get("key"):
            link_map[f"{chapter['key']}.md"] = chapter_url
            link_map[f"{chapter['key']}.MD"] = chapter_url
        for subpage in chapter.get("subpages", []):
            subpage_url = subpage.get("url")
            if not subpage_url:
                continue
            source_name = subpage.get("source_file")
            if source_name:
                link_map[source_name] = subpage_url
                link_map[source_name.upper()] = subpage_url
    return link_map


def inline_text_to_rich_text(text: str, link_map: dict[str, str] | None = None) -> list[dict[str, Any]]:
    if not text:
        return []

    link_map = link_map or {}
    pattern = re.compile(
        r"\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+?)\*\*|_([^_]+?)_|`([^`]+?)`|(?<![\w/])((?:\d{2}[A-Za-z]?_[A-Za-z0-9_\-]+\.md))"
    )
    items: list[dict[str, Any]] = []
    position = 0

    for match in pattern.finditer(text):
        if match.start() > position:
            items.extend(split_text_for_notion(text[position : match.start()]))

        if match.group(1) is not None:
            label = match.group(1)
            target = match.group(2)
            lookup_key = normalize_link_target(target)
            url = link_map.get(lookup_key) or link_map.get(lookup_key.upper())
            items.extend(split_text_for_notion(label, url=url))
        elif match.group(3) is not None:
            items.extend(split_text_for_notion(match.group(3), bold=True))
        elif match.group(4) is not None:
            items.extend(split_text_for_notion(match.group(4), italic=True))
        elif match.group(5) is not None:
            label = match.group(5)
            lookup_key = normalize_link_target(label)
            url = link_map.get(lookup_key) or link_map.get(lookup_key.upper())
            items.extend(split_text_for_notion(label, url=url, code=True))
        else:
            label = match.group(6) or ""
            lookup_key = normalize_link_target(label)
            url = link_map.get(lookup_key) or link_map.get(lookup_key.upper())
            items.extend(split_text_for_notion(label, url=url))
        position = match.end()

    if position < len(text):
        items.extend(split_text_for_notion(text[position:]))

    return items or split_text_for_notion(text)


def is_markdown_table_divider(line: str) -> bool:
    return bool(re.match(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$", line))


def split_markdown_table_row(line: str) -> list[str]:
    trimmed = line.strip().strip("|")
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", trimmed)]


def table_row_block(
    cells: list[str],
    table_width: int,
    link_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    padded_cells = cells + [""] * max(0, table_width - len(cells))
    return {
        "object": "block",
        "type": "table_row",
        "table_row": {
            "cells": [inline_text_to_rich_text(cell, link_map) for cell in padded_cells[:table_width]],
        },
    }


def notion_table_block_from_lines(
    table_lines: list[str],
    link_map: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    if not table_lines:
        return None

    rows = [split_markdown_table_row(line) for line in table_lines if line.strip()]
    if not rows:
        return None

    has_column_header = len(table_lines) > 1 and is_markdown_table_divider(table_lines[1])
    if has_column_header:
        rows = [rows[0], *rows[2:]]

    if not rows:
        return None

    table_width = max(len(row) for row in rows)
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": table_width,
            "has_column_header": has_column_header,
            "has_row_header": False,
            "children": [table_row_block(row, table_width, link_map) for row in rows],
        },
    }


def markdown_to_notion_blocks(text: str, link_map: dict[str, str] | None = None) -> list[dict[str, Any]]:
    link_map = link_map or {}
    blocks: list[dict[str, Any]] = []
    paragraph_lines: list[str] = []
    table_lines: list[str] = []
    quote_lines: list[str] = []
    code_lines: list[str] = []
    in_code = False

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        paragraph_text = "\n".join(line.rstrip() for line in paragraph_lines if line.strip())
        if paragraph_text:
            blocks.append(paragraph_block(inline_text_to_rich_text(paragraph_text, link_map)))
        paragraph_lines.clear()

    def flush_table() -> None:
        if not table_lines:
            return
        table = notion_table_block_from_lines(table_lines, link_map)
        if table is not None:
            blocks.append(table)
        else:
            blocks.append(code_block("\n".join(table_lines), language="markdown"))
        table_lines.clear()

    def flush_quotes() -> None:
        if not quote_lines:
            return
        quote_text = "\n".join(line.rstrip() for line in quote_lines if line.strip())
        if quote_text:
            blocks.append(quote_block(inline_text_to_rich_text(quote_text, link_map)))
        quote_lines.clear()

    for line in text.splitlines():
        stripped = line.rstrip()
        plain = stripped.strip()

        if plain == TOC_MARKER:
            flush_paragraph()
            flush_table()
            flush_quotes()
            blocks.append(toc_block())
            continue

        if FENCE_RE.match(plain):
            flush_paragraph()
            flush_table()
            flush_quotes()
            if in_code:
                blocks.append(code_block("\n".join(code_lines), language="markdown"))
                code_lines.clear()
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if plain.startswith("<!--") and plain.endswith("-->"):
            flush_paragraph()
            flush_table()
            flush_quotes()
            continue

        if line.lstrip().startswith("|") and line.rstrip().endswith("|"):
            flush_paragraph()
            flush_quotes()
            table_lines.append(line)
            continue

        if not plain:
            flush_paragraph()
            flush_table()
            flush_quotes()
            continue

        if plain.startswith("# "):
            flush_paragraph()
            flush_table()
            flush_quotes()
            continue

        if plain.startswith("## "):
            flush_paragraph()
            flush_table()
            flush_quotes()
            blocks.append(heading_block(2, inline_text_to_rich_text(plain[3:].strip(), link_map)))
            continue

        if plain.startswith("### "):
            flush_paragraph()
            flush_table()
            flush_quotes()
            blocks.append(heading_block(3, inline_text_to_rich_text(plain[4:].strip(), link_map)))
            continue

        if plain.startswith("#### "):
            flush_paragraph()
            flush_table()
            flush_quotes()
            blocks.append(heading_block(3, inline_text_to_rich_text(plain[5:].strip(), link_map)))
            continue

        if re.match(r"^\s*(?:---|\*\*\*|___)\s*$", plain):
            flush_paragraph()
            flush_table()
            flush_quotes()
            blocks.append(divider_block())
            continue

        bullet_match = re.match(r"^\s*[-*+]\s+(.*)$", line)
        if bullet_match:
            flush_paragraph()
            flush_table()
            flush_quotes()
            blocks.append(bullet_block(inline_text_to_rich_text(bullet_match.group(1).strip(), link_map)))
            continue

        numbered_match = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if numbered_match:
            flush_paragraph()
            flush_table()
            flush_quotes()
            blocks.append(numbered_block(inline_text_to_rich_text(numbered_match.group(1).strip(), link_map)))
            continue

        quote_match = re.match(r"^\s*>\s?(.*)$", line)
        if quote_match:
            flush_paragraph()
            flush_table()
            quote_lines.append(quote_match.group(1).rstrip())
            continue

        paragraph_lines.append(line)

    flush_paragraph()
    flush_table()
    flush_quotes()
    if code_lines:
        blocks.append(code_block("\n".join(code_lines), language="markdown"))

    return blocks


def upload_split_chapters(
    *,
    root_page_id: str | None = None,
    split_dir: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    split_dir = Path(split_dir or SPLIT_DIR)
    manifest = load_manifest_data()
    root_page_id = normalize_notion_parent_id(root_page_id) or manifest.get("project_root_page_id")
    if not root_page_id:
        raise RuntimeError(
            "No Notion root page ID is configured. Run create-entry-page with --parent-page-id first or pass --root-page-id."
        )

    split_report_path = STATE_DIR / "split_report.json"
    if not split_report_path.exists():
        raise RuntimeError("split_report.json is missing. Run the split command first.")

    split_report = json.loads(split_report_path.read_text(encoding="utf-8"))
    manifest["project_root_page_id"] = root_page_id
    chapters = manifest.setdefault("chapters", [])

    try:
        root_children = list_block_children(root_page_id)
        if chapters and not any(child.get("type") == "child_page" for child in root_children):
            chapters.clear()
    except RuntimeError:
        pass

    summary = {
        "root_page_id": root_page_id,
        "dry_run": dry_run,
        "chapter_pages_updated": 0,
        "subpages_updated": 0,
        "chapter_pages_replaced": 0,
        "subpages_replaced": 0,
        "skipped": 0,
        "chapters": [],
    }

    if dry_run:
        summary["chapters"] = [
            {
                "chapter_key": item["chapter_key"],
                "title": item["title"],
                "is_split": item["is_split"],
                "part_keys": item["part_keys"],
            }
            for item in split_report.get("chapters", [])
        ]
        return summary

    chapter_inputs: dict[str, dict[str, Any]] = {}
    preliminary_link_map = build_link_map(manifest)
    initial_batch_size = min(
        HouseSafetyBudget().max_append_batch_blocks,
        NotionApiBudget().max_blocks_per_append,
    )

    for item in split_report.get("chapters", []):
        chapter_key = item["chapter_key"]
        title = item["title"]
        emoji = CHAPTER_EMOJIS.get(chapter_key, "📄")
        part_keys = item.get("part_keys", [])

        part_files: list[Path] = []
        for part_key in part_keys:
            matches = sorted(split_dir.glob(f"{part_key}_*.md"))
            if matches:
                part_files.append(matches[0])

        if part_files:
            suffix = re.sub(r"^\d{2}[A-Z]?_", "", part_files[0].name)
        else:
            suffix = f"{title.upper().replace(' ', '_')}.md"
        source_file = f"{chapter_key}_{suffix}"

        chapter_record = next((entry for entry in chapters if entry.get("key") == chapter_key), None)
        if chapter_record is None:
            chapter_record = {
                "key": chapter_key,
                "title": title,
                "source_file": source_file,
                "chapter_page_id": None,
                "subpages": [],
            }
            chapters.append(chapter_record)

        chapter_record["title"] = title
        chapter_record["source_file"] = source_file
        part_title_map = {
            part["key"]: part.get("title", part["key"])
            for part in item.get("parts", [])
        }

        if item.get("is_split"):
            chapter_text = build_split_chapter_index_text(
                title,
                [part_title_map.get(part_key, part_key) for part_key in part_keys],
            )
        else:
            part_path = part_files[0] if part_files else None
            chapter_text = part_path.read_text(encoding="utf-8") if part_path else f"# {title}\n"

        chapter_blocks = markdown_to_notion_blocks(chapter_text, preliminary_link_map)
        chapter_hash = compute_render_hash(chapter_text, chapter_blocks)
        chapter_inputs[chapter_key] = {
            "chapter_text": chapter_text,
            "chapter_blocks": chapter_blocks,
            "part_files": part_files,
            "part_blocks": {},
        }

        page_title = title
        old_chapter_page_id = chapter_record.get("chapter_page_id")
        chapter_content_changed = not old_chapter_page_id or chapter_record.get("clean_hash") != chapter_hash
        chapter_metadata_changed = chapter_record.get("page_title") != page_title
        if chapter_content_changed or chapter_metadata_changed or not chapter_record.get("url"):
            page_result = ensure_page(
                root_page_id,
                old_chapter_page_id,
                title=page_title,
                emoji=emoji,
                replace_existing=chapter_content_changed,
                children=chapter_blocks if not old_chapter_page_id else None,
            )
            chapter_record["chapter_page_id"] = page_result.get("id")
            chapter_record["url"] = page_result.get("url")
        chapter_record["page_title"] = page_title
        chapter_record["_pending_upload"] = chapter_content_changed
        chapter_record["_pending_hash"] = chapter_hash
        chapter_record["_clear_before_upload"] = bool(chapter_content_changed and old_chapter_page_id)

        summary["chapters"].append(
            {
                "chapter_key": chapter_key,
                "title": title,
                "page_id": chapter_record.get("chapter_page_id"),
                "part_keys": part_keys,
            }
        )

        if item.get("is_split"):
            chapter_record.setdefault("subpages", [])
            for part_number, (part_key, part_path) in enumerate(
                zip(part_keys, part_files, strict=False),
                start=1,
            ):
                content = part_path.read_text(encoding="utf-8")
                section_name = first_subheading(content)
                part_title = part_title_map.get(part_key) or build_split_part_title(
                    part_number,
                    section_name,
                    title,
                )
                subpage_record = next(
                    (entry for entry in chapter_record["subpages"] if entry.get("key") == part_key),
                    None,
                )
                if subpage_record is None:
                    subpage_record = {"key": part_key, "title": part_title, "source_file": part_path.name}
                    chapter_record["subpages"].append(subpage_record)

                part_blocks = markdown_to_notion_blocks(content, preliminary_link_map)
                content_hash = compute_render_hash(content, part_blocks)
                chapter_inputs[chapter_key]["part_blocks"][part_key] = part_blocks
                old_subpage_id = subpage_record.get("notion_page_id")
                subpage_content_changed = (
                    chapter_content_changed
                    or not old_subpage_id
                    or subpage_record.get("clean_hash") != content_hash
                )
                subpage_metadata_changed = subpage_record.get("page_title") != part_title
                if subpage_content_changed or subpage_metadata_changed or not subpage_record.get("url"):
                    page_result = ensure_page(
                        chapter_record["chapter_page_id"],
                        old_subpage_id,
                        title=part_title,
                        emoji=emoji,
                        replace_existing=subpage_content_changed,
                        children=part_blocks if not old_subpage_id else None,
                    )
                    subpage_record["notion_page_id"] = page_result.get("id")
                    subpage_record["url"] = page_result.get("url")
                subpage_record["title"] = part_title
                subpage_record["page_title"] = part_title
                subpage_record["source_file"] = part_path.name
                subpage_record["_pending_upload"] = subpage_content_changed
                subpage_record["_pending_hash"] = content_hash
                subpage_record["_clear_before_upload"] = bool(subpage_content_changed and old_subpage_id)

    save_manifest_data(manifest)
    link_map = build_link_map(manifest)

    for item in split_report.get("chapters", []):
        chapter_key = item["chapter_key"]
        chapter_record = next(entry for entry in chapters if entry.get("key") == chapter_key)
        chapter_text = chapter_inputs[chapter_key]["chapter_text"]
        chapter_blocks = chapter_inputs[chapter_key]["chapter_blocks"]
        part_files = chapter_inputs[chapter_key]["part_files"]
        part_keys = item.get("part_keys", [])

        if chapter_record.pop("_pending_upload", False):
            if chapter_record.pop("_clear_before_upload", False):
                clear_page_children(
                    chapter_record["chapter_page_id"],
                    preserve_child_pages=item.get("is_split", False),
                )
                blocks_to_append = chapter_blocks
            else:
                blocks_to_append = chapter_blocks[initial_batch_size:]
            if blocks_to_append:
                append_blocks_to_page(chapter_record["chapter_page_id"], blocks_to_append)
            chapter_record["clean_hash"] = chapter_record.pop(
                "_pending_hash",
                compute_render_hash(chapter_text, chapter_blocks),
            )
            chapter_record["block_count"] = len(chapter_blocks)
            summary["chapter_pages_updated"] += 1
        else:
            chapter_record.pop("_pending_hash", None)
            chapter_record.pop("_clear_before_upload", None)
            summary["skipped"] += 1

        if not item.get("is_split"):
            continue

        for part_key, part_path in zip(part_keys, part_files, strict=False):
            subpage_record = next(
                entry for entry in chapter_record.get("subpages", []) if entry.get("key") == part_key
            )
            content = part_path.read_text(encoding="utf-8")
            if not subpage_record.pop("_pending_upload", False):
                subpage_record.pop("_pending_hash", None)
                subpage_record.pop("_clear_before_upload", None)
                summary["skipped"] += 1
                continue

            blocks = chapter_inputs[chapter_key]["part_blocks"].get(
                part_key,
                markdown_to_notion_blocks(content, link_map),
            )
            if subpage_record.pop("_clear_before_upload", False):
                clear_page_children(subpage_record["notion_page_id"])
                blocks_to_append = blocks
            else:
                blocks_to_append = blocks[initial_batch_size:]
            if blocks_to_append:
                append_blocks_to_page(subpage_record["notion_page_id"], blocks_to_append)
            subpage_record["clean_hash"] = subpage_record.pop(
                "_pending_hash",
                compute_render_hash(content, blocks),
            )
            subpage_record["block_count"] = len(blocks)
            summary["subpages_updated"] += 1

    save_manifest_data(manifest)
    return summary


def command_upload(root_page_id: str | None = None, *, dry_run: bool = False) -> int:
    report = upload_split_chapters(root_page_id=root_page_id, split_dir=SPLIT_DIR, dry_run=dry_run)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


def command_sync(root_page_id: str | None = None, *, dry_run: bool = False) -> int:
    copy_core_chapters(SOURCE_ROOT, RAW_DIR, dry_run=dry_run)
    normalize_raw_chapters(RAW_DIR, CLEAN_DIR, dry_run=dry_run)
    split_clean_chapters(CLEAN_DIR, SPLIT_DIR, dry_run=dry_run)
    report = upload_split_chapters(root_page_id=root_page_id, split_dir=SPLIT_DIR, dry_run=dry_run)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


def command_plan() -> int:
    api_budget = NotionApiBudget()
    house_budget = HouseSafetyBudget()
    rules = DiscoveryRules()

    payload = {
        "root": str(ROOT),
        "raw_dir": str(RAW_DIR),
        "clean_dir": str(CLEAN_DIR),
        "split_dir": str(SPLIT_DIR),
        "state_dir": str(STATE_DIR),
        "official_limits": api_budget.__dict__,
        "house_limits": house_budget.__dict__,
        "ignored_chapter_keys": list(rules.ignore_keys),
        "prefer_merged_keys": list(rules.prefer_merged_keys),
        "normalizer_defaults": NormalizationOptions().__dict__,
    }
    print(json.dumps(payload, indent=2))
    return 0


def command_status() -> int:
    manifest_path = SyncManifest.default_path(ROOT)
    if not manifest_path.exists():
        print("No manifest file exists yet.")
        return 0

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    print(json.dumps(data, indent=2))
    return 0


def command_entry_page() -> int:
    blueprint = EntryPageBlueprint()
    payload = {
        "title": blueprint.title,
        "icon": blueprint.icon,
        "hero_icon": blueprint.hero_icon,
        "promise_icon": blueprint.promise_icon,
        "blueprint_file": str(ROOT / blueprint.blueprint_file),
        "section_order": list(blueprint.section_order),
        "chapter_emojis": CHAPTER_EMOJIS,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def command_create_entry_page(parent_page_id: str | None = None) -> int:
    parent_page_id = normalize_notion_parent_id(parent_page_id)
    entry_link_map = build_link_map(load_manifest_data())

    if parent_page_id:
        previous_root_page_id: str | None = None
        manifest_path = SyncManifest.default_path(ROOT)
        if manifest_path.exists():
            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
            previous_root_page_id = manifest_data.get("project_root_page_id")

        cleared_blocks = clear_page_children(
            parent_page_id,
            preserve_child_pages=True,
        )
        update_page_icon(parent_page_id)

        try:
            appended_blocks = append_blocks_to_page(
                parent_page_id,
                build_entry_page_blocks(use_columns=True, link_map=entry_link_map),
            )
            layout_mode = "columns-parent-fill"
        except RuntimeError as exc:
            print(str(exc))
            print("Retrying with a simpler linear layout...")
            append_blocks_to_page(
                parent_page_id,
                build_entry_page_blocks(use_columns=False, link_map=entry_link_map),
            )
            appended_blocks = len(build_entry_page_blocks(use_columns=False))
            layout_mode = "linear-parent-fill"

        result = notion_api_request("GET", f"/pages/{parent_page_id}", None)
        if previous_root_page_id and previous_root_page_id != parent_page_id:
            try:
                trash_page(previous_root_page_id)
            except RuntimeError:
                pass

        save_entry_page_state(result, layout_mode=layout_mode)
        update_manifest_root_page(result)
        output = {
            "status": "filled_parent_page",
            "layout_mode": layout_mode,
            "page_id": result.get("id"),
            "url": result.get("url"),
            "cleared_blocks": cleared_blocks,
            "appended_blocks": appended_blocks,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 0

    try:
        result = notion_api_request(
            "POST",
            "/pages",
            build_entry_page_payload(parent_page_id=None, use_columns=True, link_map=entry_link_map),
        )
        layout_mode = "columns"
    except RuntimeError as exc:
        message = str(exc)
        if "parent.page_id" in message or "workspace-level private pages is not supported" in message:
            raise RuntimeError(
                "The Notion integration is internal and cannot create a workspace-root page by itself. Share any parent page with the integration and rerun create-entry-page with --parent-page-id set to that page URL or ID."
            ) from exc

        print(message)
        print("Retrying with a simpler linear layout...")
        result = notion_api_request(
            "POST",
            "/pages",
            build_entry_page_payload(parent_page_id=None, use_columns=False),
        )
        layout_mode = "linear-fallback"

    save_entry_page_state(result, layout_mode=layout_mode)
    update_manifest_root_page(result)
    output = {
        "status": "created",
        "layout_mode": layout_mode,
        "page_id": result.get("id"),
        "url": result.get("url"),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


def command_placeholder(name: str) -> int:
    print(f"Command '{name}' is scaffolded and will be implemented in later prompts.")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    configure_retry_policy(
        patient=getattr(args, "patient", False),
        max_wait_minutes=getattr(args, "max_wait_minutes", None),
    )

    if args.command == "plan":
        return command_plan()
    if args.command == "status":
        return command_status()
    if args.command == "entry-page":
        return command_entry_page()
    if args.command == "create-entry-page":
        return command_create_entry_page(args.parent_page_id)
    if args.command == "raw-copy":
        return command_raw_copy(dry_run=args.dry_run)
    if args.command == "normalize":
        return command_normalize(dry_run=args.dry_run)
    if args.command == "split":
        return command_split(dry_run=args.dry_run, max_bytes=args.max_bytes)
    if args.command == "upload":
        return command_upload(args.root_page_id, dry_run=args.dry_run)
    if args.command == "sync":
        return command_sync(args.root_page_id, dry_run=args.dry_run)
    return command_placeholder(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
