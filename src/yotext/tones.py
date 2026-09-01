"""Tone mark and diacritic handling for Yorùbá text.

Underdots are SEGMENTAL: they distinguish separate phonemes (ẹ vs e, ọ vs o)
and are part of a letter's identity. Tone marks (acute, grave, and the
implicit mid tone) are SUPRASEGMENTAL: they indicate pitch on top of a
vowel/syllabic nasal, independent of which phoneme it is. Because of this,
stripping tone marks and stripping diacritics are genuinely different
operations: strip_tones removes only pitch information and must leave
underdots untouched, while strip_diacritics removes every combining mark,
underdots included, collapsing segmental distinctions along with tone.
"""

import unicodedata

from .constants import ACUTE, GRAVE, TONE_MARKS, VOWELS
from .standardize import standardize


def strip_tones(text: str) -> str:
    """Remove suprasegmental tone marks, preserving segmental underdots.

    Only characters in TONE_MARKS are removed; DOT_BELOW is not a tone mark
    and survives, since it marks a distinct phoneme (e.g. ẹ vs e) rather than
    pitch.

    Args:
        text: The input text.

    Returns:
        The text with tone marks removed, in NFC form.
    """
    decomposed = standardize(text, compose=False)
    filtered = "".join(c for c in decomposed if c not in TONE_MARKS)
    return unicodedata.normalize("NFC", filtered)


def strip_diacritics(text: str) -> str:
    """Remove every combining mark, including segmental underdots.

    Unlike strip_tones, this removes all combining characters (any character
    for which unicodedata.combining() is non-zero), which collapses
    segmental distinctions such as ẹ/e and ọ/o along with tone information.

    Args:
        text: The input text.

    Returns:
        The text with all combining marks removed.
    """
    decomposed = standardize(text, compose=False)
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def tone_pattern(text: str) -> str:
    """Derive the tone pattern of a text as a string of H/M/L markers.

    Walks the decomposed text; for each base character, the combining marks
    that immediately follow it are inspected. Non-vowel bases are skipped.
    For vowel bases, "H" is emitted if ACUTE is present among its marks, "L"
    if GRAVE is present, and "M" otherwise (mid tone, unmarked).

    Args:
        text: The input text.

    Returns:
        A string of "H", "M", and "L" characters, one per vowel.
    """
    decomposed = standardize(text, compose=False)
    pattern = []
    i = 0
    n = len(decomposed)
    while i < n:
        base = decomposed[i]
        i += 1
        marks = []
        while i < n and unicodedata.combining(decomposed[i]) != 0:
            marks.append(decomposed[i])
            i += 1
        if base in VOWELS:
            if ACUTE in marks:
                pattern.append("H")
            elif GRAVE in marks:
                pattern.append("L")
            else:
                pattern.append("M")
    return "".join(pattern)


def diacritic_coverage(text: str) -> float:
    """Compute the fraction of vowels that carry at least one combining mark.

    Walks the decomposed text; for each base character, the combining marks
    that immediately follow it are inspected. Non-vowel bases are skipped.
    A vowel counts as marked if it has one or more combining marks
    following it, tone marks and underdots alike.

    Args:
        text: The input text.

    Returns:
        The number of marked vowels divided by the total number of vowels,
        or 0.0 if the text has no vowels.
    """
    decomposed = standardize(text, compose=False)
    total = 0
    marked = 0
    i = 0
    n = len(decomposed)
    while i < n:
        base = decomposed[i]
        i += 1
        marks = []
        while i < n and unicodedata.combining(decomposed[i]) != 0:
            marks.append(decomposed[i])
            i += 1
        if base in VOWELS:
            total += 1
            if marks:
                marked += 1
    return marked / total if total else 0.0
