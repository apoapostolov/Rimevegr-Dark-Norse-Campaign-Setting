from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTION_DIR = PROJECT_ROOT / "notion"

if str(NOTION_DIR) not in sys.path:
    sys.path.insert(0, str(NOTION_DIR))

import notion_export as exporter


def _write_markdown_files(root: Path, filenames: list[str]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for name in filenames:
        (root / name).write_text(f"# {name}\n\nBody\n", encoding="utf-8")


def test_discover_chapter_inventory_filters_and_orders_files(tmp_path: Path) -> None:
    _write_markdown_files(
        tmp_path,
        [
            "00_NOVEL.md",
            "01_SETTING.md",
            "02_INDEX.md",
            "07_PANTHEON.md",
            "07A_RELIGION.md",
            "07B_RELIGIOUS_LIFE.md",
            "08_MAGIC.md",
            "08A_MAGIC_CRACKING.md",
            "23_ARCS.md",
            "23A_FOUNDATIONS.md",
            "24_SCENES.md",
            "AGENTS.md",
            "TODO.md",
        ],
    )

    inventory = exporter.discover_chapter_inventory(tmp_path)

    assert [item["key"] for item in inventory["core"]] == [
        "01",
        "02",
        "07",
        "08",
        "23",
        "24",
    ]
    assert [item["key"] for item in inventory["ignored_by_rule"]] == [
        "07B",
        "08A",
    ]
    assert [item["key"] for item in inventory["supplements"]] == [
        "07A",
        "23A",
    ]


def test_copy_core_chapters_removes_stale_files_and_copies_only_core(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    raw_dir = tmp_path / "raw"

    _write_markdown_files(
        source_dir,
        [
            "01_SETTING.md",
            "08_MAGIC.md",
            "08B_MAGIC_TRADITIONS.md",
            "11_SETTLEMENTS.md",
            "23_ARCS.md",
        ],
    )
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "stale.md").write_text("old", encoding="utf-8")

    report = exporter.copy_core_chapters(source_dir, raw_dir, dry_run=False)

    copied_files = sorted(path.name for path in raw_dir.glob("*.md"))
    assert copied_files == [
        "01_SETTING.md",
        "08_MAGIC.md",
        "11_SETTLEMENTS.md",
        "23_ARCS.md",
    ]
    assert report["copied_count"] == 4
    assert report["dry_run"] is False
