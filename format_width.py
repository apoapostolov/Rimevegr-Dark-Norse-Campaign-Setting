#!/usr/bin/env python3
"""Project Markdown formatter for Norse Grit.

This formatter normalizes prose width to the chapter's native style, wraps long
list prose, preserves headings and code fences, and repairs phantom Markdown
table rows caused by prior hard-wrapping.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from textwrap import TextWrapper

try:
    from scripts.fix_markdown_tables import fix_markdown_tables_text
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
    from fix_markdown_tables import fix_markdown_tables_text

DEFAULT_WIDTH = 75
MIN_WIDTH = 73
MAX_WIDTH = 75


def is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.count("|") >= 2


def is_list_line(line: str) -> bool:
    return bool(re.match(r"^\s*(?:[-*+]\s+|\d+\.\s+)", line))


def is_special_line(line: str) -> bool:
    """Return True for lines that should never be reflowed as prose."""
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith("#"):
        return True
    if stripped.startswith("```"):
        return True
    if stripped.startswith("<!--"):
        return True
    if is_table_line(line):
        return True
    return False


def reflow_markdown_line(text: str, width: int = DEFAULT_WIDTH) -> str:
    """Reflow one Markdown prose or list line to the target width."""
    raw = text.rstrip("\n")
    if not raw.strip():
        return raw

    list_match = re.match(r"^(\s*(?:[-*+]\s+|\d+\.\s+))(.*)$", raw)
    quote_match = re.match(r"^(\s*>\s?)(.*)$", raw)

    if list_match:
        prefix = list_match.group(1)
        body = list_match.group(2).strip()
        initial_indent = prefix
        subsequent_indent = " " * len(prefix)
    elif quote_match:
        prefix = quote_match.group(1)
        body = quote_match.group(2).strip()
        initial_indent = prefix
        subsequent_indent = " " * len(prefix)
    else:
        leading_spaces = len(raw) - len(raw.lstrip(" "))
        indent = " " * leading_spaces
        body = raw.strip()
        initial_indent = indent
        subsequent_indent = indent

    wrapper = TextWrapper(
        width=width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
        break_long_words=False,
        break_on_hyphens=False,
        replace_whitespace=True,
        drop_whitespace=True,
    )
    return "\n".join(wrapper.wrap(body))


def detect_target_width(lines: list[str], default: int = DEFAULT_WIDTH) -> int:
    """Infer the document's prose width from existing non-table prose lines."""
    candidates: list[int] = []
    in_code_block = False
    in_spoiler_block = False

    for raw in lines:
        stripped = raw.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if "<!-- SPOILER_START -->" in stripped:
            in_spoiler_block = True
            continue
        if "<!-- SPOILER_END -->" in stripped:
            in_spoiler_block = False
            continue
        if in_code_block or in_spoiler_block:
            continue
        if is_special_line(raw) or is_list_line(raw):
            continue

        length = len(raw.rstrip())
        if 55 <= length <= 78:
            candidates.append(length)

    if not candidates:
        return default

    candidates.sort()
    median = candidates[len(candidates) // 2]
    return max(MIN_WIDTH, min(MAX_WIDTH, median))


def process_text(text: str, start_line: int = 0, width: int | None = None) -> str:
    """Process Markdown text from the given 0-based line index onward."""
    fixed_text, _merge_count = fix_markdown_tables_text(text)
    lines = fixed_text.splitlines(keepends=True)

    if width is None:
        width = detect_target_width(lines[: max(start_line, 1)] or lines)

    before = lines[:start_line]
    after = lines[start_line:]

    processed: list[str] = []
    in_code_block = False
    in_spoiler_block = False
    i = 0

    while i < len(after):
        line = after[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            processed.append(line)
            i += 1
            continue

        if "<!-- SPOILER_START -->" in stripped:
            in_spoiler_block = True
            processed.append(line)
            i += 1
            continue

        if "<!-- SPOILER_END -->" in stripped:
            in_spoiler_block = False
            processed.append(line)
            i += 1
            continue

        if in_code_block or in_spoiler_block:
            processed.append(line)
            i += 1
            continue

        if is_list_line(line):
            processed.append(
                reflow_markdown_line(line.rstrip("\n"), width=width) + "\n"
            )
            i += 1
            continue

        if is_special_line(line):
            processed.append(line)
            i += 1
            continue

        para_lines: list[str] = []
        while i < len(after):
            current = after[i]
            current_stripped = current.strip()
            if (
                current_stripped.startswith("```")
                or "<!-- SPOILER_START -->" in current_stripped
                or "<!-- SPOILER_END -->" in current_stripped
                or in_code_block
                or is_special_line(current)
                or is_list_line(current)
            ):
                break
            para_lines.append(current.rstrip("\n"))
            i += 1

        if para_lines:
            para_text = " ".join(part.strip() for part in para_lines if part.strip())
            if para_text:
                processed.append(reflow_markdown_line(para_text, width=width) + "\n")
        else:
            processed.append(line)
            i += 1

    return "".join(before + processed)


def process_file(input_path: str, start_line: int = 0, width: int | None = None) -> str:
    """Process a file from the given 0-based line index onward."""
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    return process_text(text, start_line=start_line, width=width)


def main() -> int:
    parser = argparse.ArgumentParser(description="Reflow prose and repair wrapped Markdown tables for this project.")
    parser.add_argument("file", help="Markdown file to process")
    parser.add_argument("--start-line", type=int, default=1, help="1-based line number to start reflowing from")
    parser.add_argument("--width", type=int, default=None, help="Override detected width")
    parser.add_argument("--write", action="store_true", help="Write changes back to the file")
    args = parser.parse_args()

    path = Path(args.file)
    zero_based_start = max(0, args.start_line - 1)
    result = process_file(str(path), start_line=zero_based_start, width=args.width)

    if args.write:
        path.write_text(result, encoding="utf-8")
    else:
        print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
