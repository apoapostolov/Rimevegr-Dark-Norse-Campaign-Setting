from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTION_DIR = PROJECT_ROOT / "notion"

if str(NOTION_DIR) not in sys.path:
    sys.path.insert(0, str(NOTION_DIR))

from format_normalizer import NormalizationOptions, normalize_markdown


def test_unwraps_simple_paragraphs_into_single_lines() -> None:
    text = (
        "This is a wrapped paragraph that should become one line\n"
        "after normalization because it is ordinary prose.\n\n"
        "Another wrapped paragraph also needs\n"
        "to stay intact semantically.\n"
    )

    result = normalize_markdown(
        text,
        NormalizationOptions(unwrap_paragraphs=True),
    )

    assert "This is a wrapped paragraph that should become one line after normalization because it is ordinary prose." in result
    assert "Another wrapped paragraph also needs to stay intact semantically." in result


def test_preserves_bullets_and_wrapped_bullet_continuations() -> None:
    text = (
        "- First bullet starts here and continues\n"
        "  on the next wrapped line without becoming a new bullet.\n"
        "- Second bullet remains separate.\n"
    )

    result = normalize_markdown(
        text, NormalizationOptions(unwrap_paragraphs=True)
    )

    assert "- First bullet starts here and continues on the next wrapped line without becoming a new bullet." in result
    assert "- Second bullet remains separate." in result


def test_preserves_tables_headings_and_code_fences() -> None:
    text = (
        "## Heading\n\n"
        "| A | B |\n"
        "|---|---|\n"
        "| x | y |\n\n"
        "```text\n"
        "line one\nline two\n"
        "```\n"
    )

    result = normalize_markdown(
        text, NormalizationOptions(unwrap_paragraphs=True)
    )

    assert "## Heading" in result
    assert "| A | B |" in result
    assert "```text" in result
    assert "line one\nline two" in result


def test_preserves_bold_prefixed_statblock_lines_as_separate_lines() -> None:
    text = (
        "**Name:** The Rimevegr\n"
        "**Era:** Roughly equivalent to 850--1050 CE Norse world\n"
        "**Magic Level:** Extremely low and terrifying.\n"
    )

    result = normalize_markdown(
        text, NormalizationOptions(unwrap_paragraphs=True)
    )

    assert "**Name:** The Rimevegr\n**Era:** Roughly equivalent to 850--1050 CE Norse world" in result
    assert "**Magic Level:** Extremely low and terrifying." in result
    assert "**Name:** The Rimevegr **Era:**" not in result


def test_unwraps_wrapped_bold_prefixed_statblock_values_without_merging_fields() -> None:
    text = (
        "**Domain:** Grief that becomes endurance, bitter fertility, the\n"
        "seidr tradition (she taught women to speak with the dead).\n\n"
        "**Depiction:** A woman with a dry face (she wept until she could\n"
        "not weep).\n"
    )

    result = normalize_markdown(
        text, NormalizationOptions(unwrap_paragraphs=True)
    )

    assert "**Domain:** Grief that becomes endurance, bitter fertility, the seidr tradition" in result
    assert "**Depiction:** A woman with a dry face (she wept until she could not weep)." in result
    assert "the\nseidr tradition" not in result
    assert "could\nnot weep" not in result
