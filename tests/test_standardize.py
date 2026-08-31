"""Tests for yotext.standardize."""

from yotext.standardize import standardize


def test_mark_ordering_reorders_combining_classes():
    result = standardize("e\u0301\u0329", compose=False)
    assert result == "e\u0323\u0301"


def test_idempotence():
    for s in ["", "e\u0301\u0329", "plain text", "\u2018hi\u2019", "\u200bzero width"]:
        once = standardize(s)
        twice = standardize(once)
        assert once == twice


def test_invisibles_removed():
    assert standardize("a\u200bb") == "ab"
    assert standardize("a\u200cb") == "ab"
    assert standardize("a\u200db") == "ab"
    assert standardize("a\ufeffb") == "ab"
    assert standardize("a\u00adb") == "ab"


def test_punctuation_normalized():
    assert standardize("\u2018hi\u2019") == "'hi'"
    assert standardize("\u201chi\u201d") == '"hi"'
    assert standardize("a\u2013b") == "a-b"
    assert standardize("a\u2014b") == "a-b"


def test_underdot_variants_fold_to_canonical():
    for variant in ("\u0329", "\u0331", "\u032D"):
        result = standardize("e" + variant, compose=False)
        assert result == "e\u0323"


def test_compose_flag():
    nfd = standardize("e\u0323\u0301", compose=False)
    nfc = standardize("e\u0323\u0301", compose=True)
    assert nfd == "e\u0323\u0301"
    assert nfc == "\u1eb9\u0301"
