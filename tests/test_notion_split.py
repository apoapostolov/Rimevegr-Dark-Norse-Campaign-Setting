from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTION_DIR = PROJECT_ROOT / "notion"

if str(NOTION_DIR) not in sys.path:
    sys.path.insert(0, str(NOTION_DIR))

from notion_export import TOC_MARKER, split_clean_chapter_text


def test_split_prefers_h2_boundaries_for_large_chapter() -> None:
    text = (
        "# Big Chapter\n\n"
        "Intro text for the chapter.\n\n"
        "## First Section\n\n"
        + ("alpha line in the first section.\n" * 20)
        + "\n## Second Section\n\n"
        + ("beta line in the second section.\n" * 20)
        + "\n## Third Section\n\n"
        + ("gamma line in the third section.\n" * 20)
    )

    result = split_clean_chapter_text(
        "08",
        "08_BIG_CHAPTER.md",
        text,
        max_bytes=900,
    )

    assert result["is_split"] is True
    assert [part["key"] for part in result["parts"]] == ["08A", "08B", "08C"]
    assert all(TOC_MARKER in part["content"] for part in result["parts"])
    assert "## First Section" in result["parts"][0]["content"]
    assert "## Second Section" in result["parts"][1]["content"]
    assert "## Third Section" in result["parts"][2]["content"]


def test_split_falls_back_to_h3_when_one_h2_section_is_too_large() -> None:
    text = (
        "# Oversized Chapter\n\n"
        "## Giant Section\n\n"
        "### Alpha\n\n"
        + ("alpha paragraph.\n" * 25)
        + "\n### Beta\n\n"
        + ("beta paragraph.\n" * 25)
    )

    result = split_clean_chapter_text(
        "20",
        "20_OVERSIZED_CHAPTER.md",
        text,
        max_bytes=700,
    )

    assert result["is_split"] is True
    assert len(result["parts"]) >= 2
    assert any("### Alpha" in part["content"] for part in result["parts"])
    assert any("### Beta" in part["content"] for part in result["parts"])


def test_small_chapter_remains_single_part() -> None:
    text = "# Small Chapter\n\n## One\n\nShort body.\n"

    result = split_clean_chapter_text(
        "05",
        "05_SMALL_CHAPTER.md",
        text,
        max_bytes=5_000,
    )

    assert result["is_split"] is False
    assert len(result["parts"]) == 1
    assert result["parts"][0]["key"] == "05"
    assert TOC_MARKER in result["parts"][0]["content"]


def test_split_part_titles_use_numeric_prefixes_not_letters() -> None:
    text = (
        "# Simulation Rules\n\n"
        "## 1. Core Loop\n\n"
        + ("alpha line\n" * 25)
        + "\n## 5. Health and Wounds\n\n"
        + ("beta line\n" * 25)
        + "\n## 11. Norse Magic System\n\n"
        + ("gamma line\n" * 25)
    )

    result = split_clean_chapter_text(
        "20",
        "20_SIMULATION_RULES.md",
        text,
        max_bytes=700,
    )

    assert result["is_split"] is True
    titles = [part["title"] for part in result["parts"]]

    assert titles[0] == "1 -- Core Loop"
    assert titles[1].startswith("2 -- ")
    assert "5. " not in titles[1]
    assert all(title.split(" -- ", 1)[0].isdigit() for title in titles)
