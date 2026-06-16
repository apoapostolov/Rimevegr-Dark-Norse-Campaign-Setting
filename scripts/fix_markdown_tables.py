#!/usr/bin/env python3
"""Fix phantom continuation rows in Markdown tables.

This repairs tables where a formatter wrapped a long cell into extra physical
rows, leaving the other columns blank. It merges those continuation rows back
into the previous real row and rewrites the table so each row stays on a single
line.

Usage:
    python scripts/fix_markdown_tables.py path/to/file.md --write
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


def is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.count("|") >= 2


def split_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def is_separator_row(cells: Iterable[str]) -> bool:
    cells = list(cells)
    return bool(cells) and all(cell and set(cell) <= set("-: ") for cell in cells)


def merge_cells(base: str, extra: str) -> str:
    if not base:
        return extra.strip()
    if not extra:
        return base.strip()
    return f"{base.rstrip()} {extra.lstrip()}".strip()


def _fix_table_block(lines: list[str]) -> tuple[list[str], int]:
    if len(lines) < 2:
        return lines, 0

    parsed = [split_row(line) for line in lines]
    expected_cols = max(len(row) for row in parsed)

    normalized: list[tuple[str, list[str]]] = []
    merge_count = 0
    previous_data_index: int | None = None

    for row in parsed:
        padded = row + [""] * (expected_cols - len(row))

        if is_separator_row(padded):
            normalized.append(("separator", padded))
            continue

        nonempty = [i for i, cell in enumerate(padded) if cell.strip()]
        mostly_blank = len(nonempty) <= max(1, expected_cols // 2)
        has_empty = any(not cell.strip() for cell in padded)
        first_cell = padded[0].strip()
        continuation_style = (
            not first_cell
            or first_cell.startswith("(")
            or (len(nonempty) <= 2 and has_empty)
            or any(
                padded[idx].strip() and (
                    padded[idx].strip()[0].islower()
                    or padded[idx].strip()[0] in "(×-"
                )
                for idx in nonempty
            )
        )

        if previous_data_index is not None and has_empty and (mostly_blank or continuation_style):
            prev_kind, prev_cells = normalized[previous_data_index]
            if prev_kind == "row":
                for idx in nonempty:
                    prev_cells[idx] = merge_cells(prev_cells[idx], padded[idx])
                merge_count += 1
                continue

        normalized.append(("row", padded))
        previous_data_index = len(normalized) - 1

    widths = [0] * expected_cols
    for kind, row in normalized:
        if kind == "separator":
            continue
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))
    widths = [max(3, width) for width in widths]

    output: list[str] = []
    for kind, row in normalized:
        if kind == "separator":
            rendered = "| " + " | ".join("-" * width for width in widths) + " |"
        else:
            rendered = "| " + " | ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(row)) + " |"
        output.append(rendered + "\n")

    return output, merge_count


def fix_markdown_tables_text(text: str) -> tuple[str, int]:
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    merge_count = 0
    i = 0

    while i < len(lines):
        if is_table_line(lines[i]):
            block: list[str] = []
            while i < len(lines) and is_table_line(lines[i]):
                block.append(lines[i])
                i += 1
            fixed_block, block_merges = _fix_table_block(block)
            output.extend(fixed_block)
            merge_count += block_merges
        else:
            output.append(lines[i])
            i += 1

    return "".join(output), merge_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix wrapped Markdown table rows.")
    parser.add_argument("file", help="Markdown file to inspect or repair")
    parser.add_argument("--write", action="store_true", help="Write the fixed content back to the file")
    args = parser.parse_args()

    path = Path(args.file)
    original = path.read_text(encoding="utf-8")
    fixed, merge_count = fix_markdown_tables_text(original)

    if args.write:
        path.write_text(fixed, encoding="utf-8")
        print(f"Fixed {merge_count} wrapped table row(s) in {path}")
    else:
        print(fixed)
        print(f"\n[info] Wrapped rows merged: {merge_count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
