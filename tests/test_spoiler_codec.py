"""test_spoiler_codec.py — Tests for spoiler_codec.py encode/decode."""
import pytest

from spoiler_codec import encode, decode, MD_SPOILER_START, MD_SPOILER_END


class TestEncodeDecode:
    def test_roundtrip_simple_ascii(self):
        text = "Ordovast marches in Year 313"
        assert decode(encode(text)) == text

    def test_roundtrip_empty_string(self):
        assert decode(encode("")) == ""

    def test_roundtrip_unicode(self):
        text = "Þorvaldr segir: 'Ek em reiðr'"
        assert decode(encode(text)) == text

    def test_roundtrip_newlines(self):
        text = "Line one\nLine two\nLine three"
        assert decode(encode(text)) == text

    def test_roundtrip_numbers_and_symbols(self):
        text = "Treasury: 42 silver (3 gold) — paid in full."
        assert decode(encode(text)) == text

    def test_encoded_differs_from_plaintext(self):
        text = "Sigrid is the traitor"
        encoded = encode(text)
        assert encoded != text

    def test_encoded_is_cjk_only(self):
        """All encoded characters should be in the CJK block."""
        text = "betrayal at dawn"
        encoded = encode(text)
        for ch in encoded:
            code = ord(ch)
            assert 0x4E00 <= code <= 0x4E00 + 255, (
                f"char U+{code:04X} is not in CJK range"
            )

    def test_decode_ignores_non_cjk_chars(self):
        """Whitespace in encoded string is silently skipped."""
        text = "hello"
        encoded = encode(text)
        # Insert whitespace
        decoded = decode(encoded + " ")
        assert decoded == text


class TestMarkers:
    def test_md_start_marker_present(self):
        assert MD_SPOILER_START == "<!-- SPOILER_START -->"

    def test_md_end_marker_present(self):
        assert MD_SPOILER_END == "<!-- SPOILER_END -->"
