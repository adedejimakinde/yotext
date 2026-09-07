"""Tests for yotext.validate."""

from yotext.validate import validate


def test_clean_canonical_text():
    r = validate("\u1eb9\u0300k\u1ecd\u0301")
    assert r.is_canonical is True
    assert r.misordered_marks == 0
    assert r.non_canonical_underdots == {}
    assert r.invisibles == {}


def test_underdot_0329_detected():
    r = validate("e\u0329")
    assert r.non_canonical_underdots == {"U+0329": 1}


def test_underdot_0331_detected():
    r = validate("e\u0331")
    assert r.non_canonical_underdots == {"U+0331": 1}


def test_underdot_032D_detected():
    r = validate("e\u032D")
    assert r.non_canonical_underdots == {"U+032D": 1}


def test_underdot_counted_correctly_across_multiple_occurrences():
    r = validate("e\u0329o\u0329")
    assert r.non_canonical_underdots == {"U+0329": 2}


def test_misordered_marks_with_canonical_underdot():
    r = validate("e\u0301\u0323")
    assert r.misordered_marks == 1


def test_misordered_marks_with_non_canonical_underdot():
    r = validate("e\u0301\u0329")
    assert r.misordered_marks == 1
    assert r.non_canonical_underdots == {"U+0329": 1}


def test_invisibles_counted():
    r = validate("a\u200bb\u00adc")
    assert r.invisibles == {"U+200B": 1, "U+00AD": 1}


def test_smart_punctuation_counted():
    r = validate("\u2018hi\u2019 \u2014 ok")
    assert r.smart_punctuation == 3


def test_empty_string():
    r = validate("")
    assert r.length == 0
    assert r.coverage == 0.0
    assert r.is_canonical is True
    assert r.non_canonical_underdots == {}
    assert r.misordered_marks == 0
    assert r.invisibles == {}
    assert r.smart_punctuation == 0


def test_summary_returns_non_empty_string():
    r = validate("e\u0301\u0323")
    summary = r.summary()
    assert isinstance(summary, str)
    assert len(summary) > 0


def test_validate_does_not_modify_input():
    original = "e\u0301\u0323"
    text = original
    validate(text)
    assert text == original
