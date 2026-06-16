from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizationOptions:
    """Safe defaults for Markdown cleanup before Notion conversion."""

    unwrap_paragraphs: bool = False
    preserve_tables: bool = True
    preserve_code_fences: bool = True
    preserve_lists: bool = True


LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
HEADING_RE = re.compile(r"^#{1,6}\s+")
FENCE_RE = re.compile(r"^```|^~~~")
BLOCKQUOTE_RE = re.compile(r"^\s*>")
HORIZONTAL_RULE_RE = re.compile(r"^\s*(?:---|\*\*\*|___)\s*$")
BOLD_PREFIX_RE = re.compile(r"^\s*\*\*[^*]+:\*\*")


def _is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def _is_special_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    return any(
        [
            HEADING_RE.match(stripped),
            LIST_ITEM_RE.match(line),
            BLOCKQUOTE_RE.match(line),
            HORIZONTAL_RULE_RE.match(stripped),
            BOLD_PREFIX_RE.match(line),
            _is_table_line(line),
        ]
    )


def _normalize_inline_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _join_statblock_lines(lines: list[str]) -> list[str]:
    joined: list[str] = []
    current = ""

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            continue

        if BOLD_PREFIX_RE.match(stripped):
            if current:
                joined.append(_normalize_inline_spaces(current))
            current = stripped
        else:
            current = f"{current} {stripped}".strip()

    if current:
        joined.append(_normalize_inline_spaces(current))

    return joined


def normalize_markdown(markdown: str, options: NormalizationOptions | None = None) -> str:
    """Normalize Markdown for safer Notion conversion.

    The main transformation is to unwrap hard-wrapped prose paragraphs and list
    continuations while preserving Markdown structures that depend on line shape.
    """

    options = options or NormalizationOptions()
    text = markdown.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]

    if not options.unwrap_paragraphs:
        return "\n".join(lines).strip() + "\n"

    output: list[str] = []
    paragraph_buffer: list[str] = []
    in_fence = False
    in_bold_prefixed_block = False

    def flush_paragraph_buffer() -> None:
        nonlocal paragraph_buffer, in_bold_prefixed_block
        if not paragraph_buffer:
            return
        if in_bold_prefixed_block:
            output.extend(_join_statblock_lines(paragraph_buffer))
        else:
            merged = _normalize_inline_spaces(" ".join(part.strip() for part in paragraph_buffer))
            if merged:
                output.append(merged)
        paragraph_buffer = []
        in_bold_prefixed_block = False

    for line in lines:
        stripped = line.strip()

        if options.preserve_code_fences and FENCE_RE.match(stripped):
            flush_paragraph_buffer()
            output.append(line)
            in_fence = not in_fence
            continue

        if in_fence:
            output.append(line)
            continue

        if not stripped:
            flush_paragraph_buffer()
            if output and output[-1] != "":
                output.append("")
            continue

        if options.preserve_tables and _is_table_line(line):
            flush_paragraph_buffer()
            output.append(line)
            continue

        if HEADING_RE.match(stripped) or BLOCKQUOTE_RE.match(line) or HORIZONTAL_RULE_RE.match(stripped):
            flush_paragraph_buffer()
            output.append(line)
            continue

        if BOLD_PREFIX_RE.match(line):
            if not in_bold_prefixed_block:
                flush_paragraph_buffer()
            paragraph_buffer.append(line)
            in_bold_prefixed_block = True
            continue

        if options.preserve_lists and LIST_ITEM_RE.match(line):
            flush_paragraph_buffer()
            output.append(_normalize_inline_spaces(line))
            continue

        if in_bold_prefixed_block:
            paragraph_buffer.append(stripped)
            continue

        if options.preserve_lists and output:
            previous = output[-1]
            if previous and LIST_ITEM_RE.match(previous):
                output[-1] = _normalize_inline_spaces(f"{previous} {stripped}")
                continue

        if _is_special_line(line):
            flush_paragraph_buffer()
            output.append(line)
            continue

        paragraph_buffer.append(stripped)

    flush_paragraph_buffer()

    while output and output[-1] == "":
        output.pop()

    return "\n".join(output) + "\n"
