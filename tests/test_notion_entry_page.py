from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTION_DIR = PROJECT_ROOT / "notion"

if str(NOTION_DIR) not in sys.path:
    sys.path.insert(0, str(NOTION_DIR))

import notion_export as exporter


def test_build_entry_page_payload_has_expected_shape() -> None:
    payload = exporter.build_entry_page_payload()

    assert payload["icon"]["emoji"] == "🪓"
    assert payload["properties"]["title"]["title"][0]["text"]["content"] == "Rimevegr"

    child_types = [child["type"] for child in payload["children"]]
    assert "table_of_contents" not in child_types
    assert child_types.count("column_list") >= 2


def test_build_entry_page_blocks_supports_in_place_fill() -> None:
    blocks = exporter.build_entry_page_blocks(use_columns=True)

    assert isinstance(blocks, list)
    assert blocks
    block_types = [block["type"] for block in blocks]
    assert "table_of_contents" not in block_types
    assert block_types.count("column_list") >= 2

    def collect_text(items: list[dict[str, object]]) -> list[str]:
        text_bits: list[str] = []
        for block in items:
            payload = block.get(block["type"], {})
            for item in payload.get("rich_text", []):
                text_bits.append(item.get("text", {}).get("content", ""))
            for child in payload.get("children", []):
                text_bits.extend(collect_text([child]))
        return text_bits

    flat_text = " ".join(collect_text(blocks))

    assert "Rimevegr" in flat_text
    assert "The Living World" in flat_text
    assert "Play or Write" in flat_text
    assert "01 Setting Bible" not in flat_text


def test_create_entry_page_preserves_existing_child_pages(monkeypatch) -> None:
    calls: list[tuple[str, bool]] = []

    monkeypatch.setattr(exporter, "build_link_map", lambda manifest: {})
    monkeypatch.setattr(exporter, "load_manifest_data", lambda: {"chapters": []})
    monkeypatch.setattr(exporter, "update_page_icon", lambda page_id: None)
    monkeypatch.setattr(exporter, "append_blocks_to_page", lambda page_id, blocks: len(blocks))
    monkeypatch.setattr(exporter, "build_entry_page_blocks", lambda **kwargs: [exporter.paragraph_block("hello")])
    monkeypatch.setattr(exporter, "notion_api_request", lambda method, path, payload=None: {"id": "root-id", "url": "https://example.com/root", "properties": {"title": {}}})
    monkeypatch.setattr(exporter, "save_entry_page_state", lambda result, layout_mode: None)
    monkeypatch.setattr(exporter, "update_manifest_root_page", lambda result: None)

    def fake_clear_page_children(page_id: str, *, preserve_child_pages: bool = False) -> int:
        calls.append((page_id, preserve_child_pages))
        return 2

    monkeypatch.setattr(exporter, "clear_page_children", fake_clear_page_children)

    result = exporter.command_create_entry_page("3450ea5c-af8e-80c1-ba7d-e9d059a8b8fd")

    assert result == 0
    assert calls == [("3450ea5c-af8e-80c1-ba7d-e9d059a8b8fd", True)]
