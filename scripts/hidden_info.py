#!/usr/bin/env python3
"""
Iron Ledger — Hidden Information Encoder/Decoder

Encodes English text into Chinese characters so that secret game information
(traitor plans, hidden events, NPC agendas) cannot be read by the player
when browsing data files. The AI uses this script to encode before writing
and decode before reading hidden information.

The cipher uses a deterministic character substitution mapping. Each ASCII
character maps to a unique Chinese character (common hanzi). The mapping is
consistent across encode/decode operations.

Usage:
    python hidden_info.py encode "Kell plans to desert on day 95"
    python hidden_info.py decode "科仁伦伦 普伦阿纳思 图欧 德仁思仁让图 欧纳 德阿要 九五"
    python hidden_info.py encode-file secrets.txt encoded.txt
    python hidden_info.py decode-file encoded.txt decoded.txt
"""

import argparse
import sys

# Deterministic substitution cipher: ASCII printable → Chinese hanzi
# Using common, visually distinct characters for readability
_ENCODE_MAP = {
    'a': '阿', 'b': '伯', 'c': '次', 'd': '德', 'e': '仁',
    'f': '弗', 'g': '格', 'h': '和', 'i': '义', 'j': '杰',
    'k': '科', 'l': '伦', 'm': '慕', 'n': '纳', 'o': '欧',
    'p': '普', 'q': '奇', 'r': '让', 's': '思', 't': '图',
    'u': '乌', 'v': '维', 'w': '瓦', 'x': '西', 'y': '要',
    'z': '泽',
    'A': '安', 'B': '白', 'C': '曹', 'D': '丁', 'E': '尔',
    'F': '凡', 'G': '高', 'H': '何', 'I': '英', 'J': '金',
    'K': '孔', 'L': '李', 'M': '明', 'N': '宁', 'O': '欧',
    'P': '潘', 'Q': '秦', 'R': '任', 'S': '沈', 'T': '唐',
    'U': '于', 'V': '万', 'W': '王', 'X': '夏', 'Y': '严',
    'Z': '赵',
    '0': '零', '1': '一', '2': '二', '3': '三', '4': '四',
    '5': '五', '6': '六', '7': '七', '8': '八', '9': '九',
    ' ': ' ',  # spaces preserved for readability
    '.': '点', ',': '逗', '!': '叹', '?': '问', ':': '冒',
    ';': '分', "'": '引', '"': '双', '-': '横', '_': '底',
    '(': '左', ')': '右', '/': '斜', '\\': '反', '+': '加',
    '=': '等', '@': '圈', '#': '井', '$': '元', '%': '百',
    '&': '与', '*': '星', '\n': '\n', '\t': '\t',
}

# Build reverse map for decoding
_DECODE_MAP = {}
for k, v in _ENCODE_MAP.items():
    if v not in _DECODE_MAP:
        _DECODE_MAP[v] = k
    elif k.islower():
        # Lowercase takes priority in ambiguous mappings
        _DECODE_MAP[v] = k

# Handle the A/a → 阿/安 etc. case: uppercase letters have unique mappings
# so we need separate entries. The issue is 'O' and 'o' both map to '欧'.
# Fix: give 'O' a distinct character.
_ENCODE_MAP['O'] = '偶'
_DECODE_MAP['偶'] = 'O'


def encode(text: str) -> str:
    """Encode English text to Chinese characters."""
    result = []
    for ch in text:
        if ch in _ENCODE_MAP:
            result.append(_ENCODE_MAP[ch])
        else:
            # Unknown characters pass through wrapped in brackets
            result.append(f'[{ch}]')
    return ''.join(result)


def decode(text: str) -> str:
    """Decode Chinese characters back to English text."""
    result = []
    i = 0
    while i < len(text):
        ch = text[i]

        # Check for bracket-wrapped passthrough characters
        if ch == '[' and i + 2 < len(text) and text[i + 2] == ']':
            result.append(text[i + 1])
            i += 3
            continue

        if ch in _DECODE_MAP:
            result.append(_DECODE_MAP[ch])
        elif ch in (' ', '\n', '\t'):
            result.append(ch)
        else:
            result.append(ch)  # Unknown Chinese chars pass through
        i += 1
    return ''.join(result)


def encode_file(input_path: str, output_path: str) -> None:
    """Encode an entire file."""
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    encoded = encode(text)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(encoded)


def decode_file(input_path: str, output_path: str) -> None:
    """Decode an entire file."""
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    decoded = decode(text)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(decoded)


def main():
    parser = argparse.ArgumentParser(
        description="Iron Ledger — Hidden Information Encoder/Decoder"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # encode
    enc_p = subparsers.add_parser("encode", help="Encode English text to Chinese")
    enc_p.add_argument("text", help="Text to encode")

    # decode
    dec_p = subparsers.add_parser("decode", help="Decode Chinese text to English")
    dec_p.add_argument("text", help="Text to decode")

    # encode-file
    encf_p = subparsers.add_parser("encode-file", help="Encode a file")
    encf_p.add_argument("input", help="Input file path")
    encf_p.add_argument("output", help="Output file path")

    # decode-file
    decf_p = subparsers.add_parser("decode-file", help="Decode a file")
    decf_p.add_argument("input", help="Input file path")
    decf_p.add_argument("output", help="Output file path")

    # test
    subparsers.add_parser("test", help="Run encode/decode round-trip test")

    args = parser.parse_args()

    if args.command == "encode":
        print(encode(args.text))

    elif args.command == "decode":
        print(decode(args.text))

    elif args.command == "encode-file":
        encode_file(args.input, args.output)
        print(f"Encoded: {args.input} → {args.output}")

    elif args.command == "decode-file":
        decode_file(args.input, args.output)
        print(f"Decoded: {args.input} → {args.output}")

    elif args.command == "test":
        test_strings = [
            "Kell plans to desert on day 95",
            "The Pale Widow has hired the Three Wolves to ambush Voss",
            "Thorne's loyalty drops to 1 on day 120 if blood-debt unresolved",
            "Barrow at Frostfjord contains a bound draugr lord",
            "Gest secretly hoards 15 silver in his boot",
        ]
        print("=== Round-trip Test ===")
        all_passed = True
        for s in test_strings:
            encoded = encode(s)
            decoded = decode(encoded)
            status = "PASS" if decoded == s else "FAIL"
            if status == "FAIL":
                all_passed = False
            print(f"  [{status}] '{s}'")
            print(f"         → '{encoded}'")
            if decoded != s:
                print(f"         ← '{decoded}' (MISMATCH)")
        print(f"\n{'All tests passed.' if all_passed else 'SOME TESTS FAILED.'}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
