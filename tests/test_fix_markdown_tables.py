from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from fix_markdown_tables import fix_markdown_tables_text


def test_merges_wrapped_table_rows_into_previous_row():
    source = """| Blight Total | Stage | Effect                                       |
| ------------ | ----- | -------------------------------------------- |
| 31-50        | 2     | Echo. Will check per carving or drift to     |
|              |       | náttmál. Dark-face whispers audible.         |
| 51-75        | 3     | Mark. Rune-lines visible on body. Env        |
|              |       | effects (blue fire, metal drift). -10 galdr. |
"""

    fixed, merge_count = fix_markdown_tables_text(source)

    assert merge_count == 2
    assert "Echo. Will check per carving or drift to náttmál. Dark-face whispers audible." in fixed
    assert "Mark. Rune-lines visible on body. Env effects (blue fire, metal drift). -10 galdr." in fixed
    assert "|              |       |" not in fixed


def test_merges_parenthetical_name_continuation_rows():
    source = """| Soulbane     | Soul Killed | Galdr Effect                     |
| ------------ | ----------- | -------------------------------- |
| Villimennska | Fylgja      | Galdr ceases to function. All    |
| (Wilding)    |             | runes do not glow. Permanent.    |
"""

    fixed, merge_count = fix_markdown_tables_text(source)

    assert merge_count == 1
    assert "Villimennska (Wilding)" in fixed
    assert "Galdr ceases to function. All runes do not glow. Permanent." in fixed
