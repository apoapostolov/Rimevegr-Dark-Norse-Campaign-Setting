from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import format_width


def test_reflow_list_item_to_document_width():
    text = "- this is a very long bullet item that should wrap to the same approximate prose width used by the surrounding chapter text instead of leaking far past the normal visual margin for the document"
    result = format_width.reflow_markdown_line(text, width=75)
    lines = result.splitlines()

    assert len(lines) > 1
    assert all(len(line) <= 75 for line in lines)
    assert lines[0].startswith("- ")
    assert all(line.startswith("  ") for line in lines[1:])


def test_detect_target_width_prefers_existing_prose_band():
    sample_lines = [
        "This is a normal prose line sitting near the chapter's typical width.\n",
        "This is another line that is also in the expected seventy-something range.\n",
        "| table | rows | can stay long without affecting prose width detection |\n",
        "A third prose line keeps the same visual rhythm and should guide width choice.\n",
    ]

    detected = format_width.detect_target_width(sample_lines)

    assert 73 <= detected <= 75


def test_formatter_also_repairs_wrapped_table_rows():
    broken = """| Roll   | Consequence                                          |
| ------ | ---------------------------------------------------- |
| 96-100 | Catastrophic. Bind explodes. 4d6 damage radius 10ft. |
|        | All runes activate simultaneously, uncontrolled.     |
"""

    fixed = format_width.process_text(broken, width=75)

    assert "All runes activate simultaneously, uncontrolled." in fixed
    assert "|        |" not in fixed
