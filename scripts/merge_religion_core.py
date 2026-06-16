from __future__ import annotations

import argparse
from pathlib import Path

SOURCE_FILES = [
    "07_PANTHEON_AND_DIVINE_PRACTICES.md",
    "07B_RELIGIOUS_LIFE_AND_PRACTICES.md",
]

OUTPUT_FILE = "07_RELIGION_OF_RIMEVEGR.md"

HEADER = """# Religion of the Rimevegr

> Generated from the split source chapters 07 and 07B.
> Edit those source files, then rerun this script to rebuild this core document.

"""


def strip_top_h1(text: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    while lines and not lines[0].strip():
        lines = lines[1:]
    body = "\n".join(lines).strip()
    return body + "\n"


def dedupe_h2_sections(text: str) -> str:
    lines = text.splitlines()
    preamble: list[str] = []
    sections: list[list[str]] = []
    current: list[str] | None = None

    for line in lines:
        if line.startswith("## "):
            if current is not None:
                sections.append(current)
            current = [line]
        elif current is None:
            preamble.append(line)
        else:
            current.append(line)

    if current is not None:
        sections.append(current)

    seen: set[str] = set()
    kept_sections: list[str] = []

    for section in sections:
        block = "\n".join(section).strip()
        if block and block not in seen:
            seen.add(block)
            kept_sections.append(block)

    parts: list[str] = []
    preamble_text = "\n".join(preamble).strip()
    if preamble_text:
        parts.append(preamble_text)
    parts.extend(kept_sections)

    return "\n\n".join(parts).strip() + "\n"


def build_core_document(base_dir: Path) -> str:
    parts: list[str] = [HEADER.rstrip(), ""]

    for idx, filename in enumerate(SOURCE_FILES):
        source_path = base_dir / filename
        if not source_path.exists():
            raise FileNotFoundError(f"Missing source file: {source_path}")

        text = source_path.read_text(encoding="utf-8")
        cleaned = dedupe_h2_sections(strip_top_h1(text))
        parts.append(cleaned.rstrip())

        if idx < len(SOURCE_FILES) - 1:
            parts.append("\n---\n")

    return "\n".join(parts).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge 07 and 07B religion chapters into 07_RELIGION_OF_RIMEVEGR.md"
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Directory containing the 07*.md files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path; defaults to <base-dir>/07_RELIGION_OF_RIMEVEGR.md",
    )
    args = parser.parse_args()

    base_dir = args.base_dir.resolve()
    output_path = args.output.resolve() if args.output else (base_dir / OUTPUT_FILE)

    merged = build_core_document(base_dir)
    output_path.write_text(merged, encoding="utf-8")

    print(f"Merged {len(SOURCE_FILES)} files into {output_path}")
    for name in SOURCE_FILES:
        print(f" - {name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
