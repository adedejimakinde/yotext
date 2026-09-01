"""Tests for yotext.restore."""

import unicodedata

from yotext import restore


def test_restore_empty_string():
    assert restore("") == ""


def test_diacritized_input_roundtrips():
    word = "b\u1eb9\u0300r\u1eb9\u0300"
    result = restore(word)
    assert unicodedata.normalize("NFC", result) == unicodedata.normalize("NFC", word)


def test_unknown_word_passes_through_unchanged():
    word = "qwxyzblorp"
    assert restore(word) == word


def test_capitalization_preserved():
    assert restore("Qwxyzblorp") == "Qwxyzblorp"


def test_allcaps_preserved():
    assert restore("QWXYZBLORP") == "QWXYZBLORP"


def test_context_influences_choice():
    assert restore("owo mi") != restore("owo pupo")


def test_token_count_preserved():
    text = "owo mi wa nile"
    assert len(restore(text).split()) == len(text.split())
