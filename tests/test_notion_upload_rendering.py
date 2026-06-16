from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTION_DIR = PROJECT_ROOT / "notion"

if str(NOTION_DIR) not in sys.path:
    sys.path.insert(0, str(NOTION_DIR))

import notion_export as exporter
from notion_export import TOC_MARKER, markdown_to_notion_blocks


def test_sanitize_manifest_data_removes_transient_keys() -> None:
    manifest = {
        "_scratch": True,
        "chapters": [
            {
                "key": "01",
                "_pending_upload": True,
                "subpages": [{"key": "01A", "_trash_after_upload": "old-id"}],
            }
        ],
    }

    cleaned = exporter.sanitize_manifest_data(manifest)

    assert "_scratch" not in cleaned
    assert "_pending_upload" not in cleaned["chapters"][0]
    assert "_trash_after_upload" not in cleaned["chapters"][0]["subpages"][0]


def test_markdown_renderer_emits_toc_and_resolves_links() -> None:
    text = (
        "# Upload Sample\n\n"
        f"{TOC_MARKER}\n\n"
        "## Section\n\n"
        "See [rules](20_SIMULATION_RULES.md) and `08_MAGIC_OF_RIMEVEGR.md` for details.\n"
    )

    blocks = markdown_to_notion_blocks(
        text,
        {
            "20_SIMULATION_RULES.md": "https://example.com/rules",
            "08_MAGIC_OF_RIMEVEGR.md": "https://example.com/magic",
        },
    )

    assert blocks[0]["type"] == "table_of_contents"
    assert any(block["type"] == "heading_2" for block in blocks)

    paragraph = next(block for block in blocks if block["type"] == "paragraph")
    links = [
        item["text"]["link"]["url"]
        for item in paragraph["paragraph"]["rich_text"]
        if item.get("type") == "text" and item["text"].get("link")
    ]

    assert "https://example.com/rules" in links
    assert "https://example.com/magic" in links


def test_markdown_renderer_converts_bold_and_preserves_soft_line_breaks() -> None:
    text = (
        "# Sample\n\n"
        "**Name:** The Rimevegr\n"
        "**Era:** Frozen twilight\n"
    )

    blocks = markdown_to_notion_blocks(text)

    paragraph = next(block for block in blocks if block["type"] == "paragraph")
    rich_text = paragraph["paragraph"]["rich_text"]

    assert any(item.get("annotations", {}).get("bold") for item in rich_text)
    joined = "".join(item["text"]["content"] for item in rich_text)
    assert "\n" in joined
    assert "**Name:**" not in joined


def test_markdown_renderer_emits_real_notion_table_block() -> None:
    text = (
        "# Table Sample\n\n"
        "| Name | Role |\n"
        "| --- | --- |\n"
        "| Voss | Captain |\n"
        "| Yrsa | Scout |\n"
    )

    blocks = markdown_to_notion_blocks(text)

    table = next(block for block in blocks if block["type"] == "table")
    assert table["table"]["table_width"] == 2
    assert table["table"]["has_column_header"] is True
    assert len(table["table"]["children"]) == 3


def test_markdown_renderer_merges_multiline_blockquotes() -> None:
    text = (
        "# Quote Sample\n\n"
        "> First line of the same quote\n"
        "> second line should stay attached\n"
    )

    blocks = markdown_to_notion_blocks(text)

    quotes = [block for block in blocks if block["type"] == "quote"]
    assert len(quotes) == 1
    joined = "".join(item["text"]["content"] for item in quotes[0]["quote"]["rich_text"])
    assert "First line of the same quote\nsecond line should stay attached" in joined


def test_markdown_renderer_converts_underscore_italics() -> None:
    text = "# Italic Sample\n\n_Dýrríða_ — being ridden by beasts.\n"

    blocks = markdown_to_notion_blocks(text)

    paragraph = next(block for block in blocks if block["type"] == "paragraph")
    rich_text = paragraph["paragraph"]["rich_text"]

    assert any(item.get("annotations", {}).get("italic") for item in rich_text)
    joined = "".join(item["text"]["content"] for item in rich_text)
    assert "_Dýrríða_" not in joined
    assert "Dýrríða" in joined


def test_build_split_chapter_index_text_avoids_duplicate_bullets() -> None:
    text = exporter.build_split_chapter_index_text(
        "Iron Ledger — Simulation Rules",
        ["1 -- Core Loop", "2 -- Health and Wounds"],
    )

    assert "## Chapter navigation" in text
    assert "Open the numbered child pages below." in text
    assert "- [" not in text


def test_compute_render_hash_changes_when_rendered_blocks_change() -> None:
    text = "# Sample\n\nHello\n"
    hash_a = exporter.compute_render_hash(text, [exporter.paragraph_block("Hello")])
    hash_b = exporter.compute_render_hash(text, [exporter.paragraph_block("Hello again")])

    assert hash_a != hash_b


def test_patient_retry_policy_waits_longer_for_cloudflare() -> None:
    standard = exporter.build_retry_policy(patient=False, max_wait_minutes=15)
    patient = exporter.build_retry_policy(patient=True, max_wait_minutes=15)

    assert patient["patient"] is True
    assert patient["max_attempts"] > standard["max_attempts"]
    assert patient["max_total_wait_seconds"] > standard["max_total_wait_seconds"]
    assert exporter.compute_retry_delay(2, blocked_by_cloudflare=True, patient=True) > exporter.compute_retry_delay(
        2,
        blocked_by_cloudflare=True,
        patient=False,
    )


def test_trash_page_ignores_already_archived_pages(monkeypatch) -> None:
    def fake_notion_api_request(method: str, path: str, payload=None):
        raise RuntimeError(
            "Notion API request failed with HTTP 400: {\"message\":\"Can't edit block that is archived. You must unarchive the block before editing.\"}"
        )

    monkeypatch.setattr(exporter, "notion_api_request", fake_notion_api_request)

    exporter.trash_page("old-page-id")


def test_replace_page_content_updates_existing_page_in_place(monkeypatch) -> None:
    calls: list[tuple[str, str]] = []

    def fake_update_page_metadata(page_id: str, title: str, emoji: str | None = None) -> dict[str, str]:
        calls.append(("update", page_id))
        return {"id": page_id, "url": "https://example.com/existing"}

    def fake_clear_page_children(page_id: str, *, preserve_child_pages: bool = False) -> int:
        calls.append(("clear", page_id))
        return 3

    def fake_append_blocks_to_page(page_id: str, blocks: list[dict[str, object]]) -> int:
        calls.append(("append", page_id))
        return len(blocks)

    monkeypatch.setattr(exporter, "update_page_metadata", fake_update_page_metadata)
    monkeypatch.setattr(exporter, "clear_page_children", fake_clear_page_children)
    monkeypatch.setattr(exporter, "append_blocks_to_page", fake_append_blocks_to_page)

    result = exporter.replace_page_content(
        parent_page_id="parent-123",
        existing_page_id="old-page-id",
        title="Fresh Title",
        emoji="🪓",
        blocks=[exporter.paragraph_block("hello")],
    )

    assert result["id"] == "old-page-id"
    assert calls == [
        ("update", "old-page-id"),
        ("clear", "old-page-id"),
        ("append", "old-page-id"),
    ]
