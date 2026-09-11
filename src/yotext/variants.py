"""Detect diacritic variant inconsistencies for word forms across texts."""

from collections import Counter, defaultdict
from typing import Iterable, Union

from .standardize import standardize
from .tones import strip_diacritics

PUNCTUATION = ".,!?;:\"'()[]"


def _iter_texts(texts: Union[str, Iterable[str]]):
    if isinstance(texts, str):
        return [texts]
    return texts


def _tokenize(text: str):
    tokens = []
    for raw in standardize(text).split():
        word = raw.strip(PUNCTUATION).lower()
        if word:
            tokens.append(word)
    return tokens


def variants(texts: Union[str, Iterable[str]], min_count: int = 1) -> dict[str, dict[str, int]]:
    """Map each bare word form to the diacritized surface forms observed.

    Accepts a single string or an iterable of strings. Each text is
    standardized, split on whitespace, stripped of surrounding punctuation,
    and lowercased before being keyed by its undiacritized (bare) form.
    Bare forms whose total observed count is below min_count are dropped.
    """
    counts = defaultdict(Counter)
    for text in _iter_texts(texts):
        for token in _tokenize(text):
            bare = strip_diacritics(token)
            counts[bare][token] += 1

    return {
        bare: dict(counter)
        for bare, counter in counts.items()
        if sum(counter.values()) >= min_count
    }


def inconsistent(texts: Union[str, Iterable[str]], min_count: int = 1) -> dict[str, dict[str, int]]:
    """Like variants(), but keeping only bare forms with more than one surface form.

    This is the diagnostic most users want: it flags words that appear
    diacritized inconsistently across the given texts.
    """
    return {
        bare: forms
        for bare, forms in variants(texts, min_count).items()
        if len(forms) > 1
    }
