"""Tests for yotext.tones."""

from yotext.tones import strip_tones, strip_diacritics, tone_pattern


def test_strip_tones_removes_acute():
    result = strip_tones("e\u0301")
    assert result == "e"


def test_strip_tones_removes_grave():
    result = strip_tones("e\u0300")
    assert result == "e"


def test_strip_tones_removes_macron():
    result = strip_tones("e\u0304")
    assert result == "e"


def test_strip_tones_preserves_underdot():
    result = strip_tones("\u1eb9\u0301")
    assert result == "\u1eb9"


def test_strip_diacritics_removes_everything_combining():
    result = strip_diacritics("\u1eb9\u0301")
    assert result == "e"


def test_consistency_invariant():
    for s in [
        "\u1eb9\u0300k\u1ecd\u0301",
        "b\u00e0b\u00e1",
        "plain",
        "",
        "\u1ecd\u0300w\u1ecd\u0300",
        "e\u0301\u0329",
        "\u1e63\u00e9",
    ]:
        assert strip_diacritics(s) == strip_diacritics(strip_tones(s))


def test_tone_pattern_known_words():
    assert tone_pattern("\u1eb9\u0300k\u1ecd\u0301") == "LH"
    assert tone_pattern("b\u00e0b\u00e1") == "LH"
    assert tone_pattern("k\u00e1\u00e0r\u1ecd\u0300") == "HLL"


def test_tone_pattern_unmarked_vowels_yield_mid():
    assert tone_pattern("aeiou") == "MMMMM"


def test_empty_string():
    assert strip_tones("") == ""
    assert strip_diacritics("") == ""
    assert tone_pattern("") == ""
