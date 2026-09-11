"""Tests for yotext.variants."""

from yotext.variants import variants, inconsistent


def test_single_string_input():
    result = variants("\u1eb9 \u1eb9")
    assert result == {"e": {"\u1eb9": 2}}


def test_list_of_strings_input():
    result = variants(["\u1eb9", "e"])
    assert result == {"e": {"\u1eb9": 1, "e": 1}}


def test_single_variant_not_in_inconsistent():
    texts = ["ni ni", "\u1eb9 e"]
    v = variants(texts)
    inc = inconsistent(texts)
    assert "ni" in v
    assert "ni" not in inc


def test_two_variants_in_both():
    texts = ["ni ni", "\u1eb9 e"]
    v = variants(texts)
    inc = inconsistent(texts)
    assert "e" in v
    assert "e" in inc
    assert v["e"] == {"\u1eb9": 1, "e": 1}
    assert inc["e"] == {"\u1eb9": 1, "e": 1}


def test_min_count_filters():
    texts = ["ni", "\u1eb9 e"]
    assert "ni" in variants(texts, min_count=1)
    result = variants(texts, min_count=2)
    assert "ni" not in result
    assert "e" in result


def test_punctuation_stripped():
    result = variants("(\u1eb9),")
    assert result == {"e": {"\u1eb9": 1}}


def test_case_folded():
    result = variants("\u1eb8 \u1eb9")
    assert result == {"e": {"\u1eb9": 2}}


def test_empty_string_returns_empty_dict():
    assert variants("") == {}


def test_empty_list_returns_empty_dict():
    assert variants([]) == {}
