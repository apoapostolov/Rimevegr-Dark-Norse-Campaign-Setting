#!/usr/bin/env python3
"""
Iron Ledger — Spoiler Codec

Encodes and decodes spoiler text using CJK character substitution.
Spoiler content (trajectories, timelines, secret plans, betrayal info)
is stored in Chinese encoding so players/editors cannot accidentally
read it. Only the simulation system decodes on demand.

Encoding: each byte of UTF-8 text → CJK character at U+4E00 + byte_value.
Decoding: each CJK character → byte_value = ord(char) - U+4E00.

Marker format in Markdown:
    <!-- SPOILER_START -->
    一丂七丄丅...  (encoded Chinese)
    <!-- SPOILER_END -->

Marker format in YAML comments:
    # SPOILER: 一丂七丄丅...

Usage:
    python spoiler_codec.py encode "Ordovast marches in Year 313"
    python spoiler_codec.py decode "丯丶丨丯丷両丳..."
    python spoiler_codec.py decode-file ../11_VILLAGES_AND_SETTLEMENTS.md
    python spoiler_codec.py decode-file ../data/political_state.yaml
    python spoiler_codec.py encode-file <path> --dry-run
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# CJK Unified Ideographs block starts at U+4E00
CJK_BASE = 0x4E00

# Markers
MD_SPOILER_START = "<!-- SPOILER_START -->"
MD_SPOILER_END = "<!-- SPOILER_END -->"
YAML_SPOILER_PREFIX = "# SPOILER: "

# Regex patterns for decoding
MD_SPOILER_RE = re.compile(
    r"<!-- SPOILER_START -->\n(.*?)\n<!-- SPOILER_END -->",
    re.DOTALL,
)
YAML_SPOILER_RE = re.compile(r"# SPOILER: (.+)")
YAML_VALUE_SPOILER_RE = re.compile(r'"SPOILER:([^"]+)"')


def encode(text: str) -> str:
    """Encode plaintext to CJK character string."""
    encoded_bytes = text.encode("utf-8")
    return "".join(chr(CJK_BASE + b) for b in encoded_bytes)


def decode(encoded: str) -> str:
    """Decode CJK character string back to plaintext."""
    byte_values = []
    for ch in encoded:
        code = ord(ch) - CJK_BASE
        if 0 <= code <= 255:
            byte_values.append(code)
        # Skip non-CJK chars (whitespace, markers, etc.)
    return bytes(byte_values).decode("utf-8")


def decode_file(filepath: str | Path) -> list[dict]:
    """Find and decode all spoiler blocks in a file.

    Returns list of {line: int, encoded: str, decoded: str}.
    """
    filepath = Path(filepath)
    content = filepath.read_text(encoding="utf-8")
    results = []

    # Markdown spoiler blocks
    for match in MD_SPOILER_RE.finditer(content):
        encoded_text = match.group(1).strip()
        # Remove any line breaks within the encoded block
        clean = encoded_text.replace("\n", "")
        try:
            decoded = decode(clean)
            line_num = content[: match.start()].count("\n") + 1
            results.append({
                "line": line_num,
                "type": "markdown_block",
                "decoded": decoded,
            })
        except Exception as e:
            results.append({
                "line": content[: match.start()].count("\n") + 1,
                "type": "markdown_block",
                "error": str(e),
            })

    # YAML comment spoilers
    for match in YAML_SPOILER_RE.finditer(content):
        encoded_text = match.group(1).strip()
        try:
            decoded = decode(encoded_text)
            line_num = content[: match.start()].count("\n") + 1
            results.append({
                "line": line_num,
                "type": "yaml_comment",
                "decoded": decoded,
            })
        except Exception as e:
            results.append({
                "line": content[: match.start()].count("\n") + 1,
                "type": "yaml_comment",
                "error": str(e),
            })

    # YAML value spoilers
    for match in YAML_VALUE_SPOILER_RE.finditer(content):
        encoded_text = match.group(1).strip()
        try:
            decoded = decode(encoded_text)
            line_num = content[: match.start()].count("\n") + 1
            results.append({
                "line": line_num,
                "type": "yaml_value",
                "decoded": decoded,
            })
        except Exception as e:
            results.append({
                "line": content[: match.start()].count("\n") + 1,
                "type": "yaml_value",
                "error": str(e),
            })

    return results


def wrap_md_spoiler(plaintext: str) -> str:
    """Wrap plaintext as a Markdown spoiler block."""
    encoded = encode(plaintext)
    # Break into ~80-char lines for readability
    lines = [encoded[i : i + 80] for i in range(0, len(encoded), 80)]
    body = "\n".join(lines)
    return f"{MD_SPOILER_START}\n{body}\n{MD_SPOILER_END}"


def wrap_yaml_comment_spoiler(plaintext: str) -> str:
    """Wrap plaintext as a YAML comment spoiler."""
    encoded = encode(plaintext)
    return f"{YAML_SPOILER_PREFIX}{encoded}"


def wrap_yaml_value_spoiler(plaintext: str) -> str:
    """Wrap plaintext as a YAML value spoiler."""
    encoded = encode(plaintext)
    return f'"SPOILER:{encoded}"'


# ============================================================
# CLI
# ============================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spoiler_codec",
        description="Iron Ledger — Spoiler Encoder/Decoder (CJK substitution)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_enc = sub.add_parser("encode", help="Encode plaintext to CJK")
    p_enc.add_argument("text", help="Plaintext to encode")

    p_dec = sub.add_parser("decode", help="Decode CJK to plaintext")
    p_dec.add_argument("text", help="CJK-encoded text to decode")

    p_df = sub.add_parser("decode-file", help="Decode all spoilers in a file")
    p_df.add_argument("filepath", type=Path, help="Path to file")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "encode":
        print(encode(args.text))

    elif args.command == "decode":
        print(decode(args.text))

    elif args.command == "decode-file":
        if not args.filepath.exists():
            print(f"File not found: {args.filepath}", file=sys.stderr)
            sys.exit(1)
        results = decode_file(args.filepath)
        if not results:
            print("No spoiler blocks found.")
            return
        for r in results:
            print(f"\n--- Line {r['line']} ({r['type']}) ---")
            if "error" in r:
                print(f"  ERROR: {r['error']}")
            else:
                print(r["decoded"])


if __name__ == "__main__":
    main()
